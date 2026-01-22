"""
Video Orchestrator.
The "Kubernetes like Controller" that coordinates State, Compilation, and Execution.
"""

import copy
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import VideoConfig, DEFAULT_CONFIG, SceneConfig, ShotConfig, ShotType
from .state import VideoStateMachine
from .compiler import ProgrammaticPromptCompiler
from .interfaces import VideoProvider, VideoGenerationResult, VideoGenerationRequest
from .utils import extract_last_frames, merge_production
from .audio import AudioRequest, AudioProvider, MockAudioProvider, GoogleTTSProvider
from .s3_utils import S3Uploader

logger = logging.getLogger(__name__)


class VideoOrchestrator:
    def __init__(self, provider: VideoProvider, audio_provider: Optional[AudioProvider] = None):
        self.provider = provider
        # Each orchestrator manages a specific state machine (like a specific deployment)
        self.state_machine = VideoStateMachine()
        self.compiler = ProgrammaticPromptCompiler()

        # Try to shared credentials from provider if it's a VertexAIProvider
        credentials = getattr(provider, "credentials", None)

        self.audio_provider = audio_provider or GoogleTTSProvider(
            credentials=credentials)
        self.s3_uploader = S3Uploader()

    async def schedule_generation(self,
                                  concept: str,
                                  action: str,
                                  config: Optional[VideoConfig] = None) -> VideoGenerationResult:
        """
        Execute a single video generation job.
        1. Update State
        2. Compile Prompt
        3. Execute Provider
        """
        if config is None:
            config = DEFAULT_CONFIG

        # 0. Ensure config has the action
        config.action_description = action

        # 1. Update State Machine with new config intent
        self.state_machine.update_from_config(config)

        # 2. Advance State (Commit)
        world_state = self.state_machine.next_scene()

        # 3. Compile Prompt using the FULL config (merged with state)
        # We need to construct a "Resolution" config that combines:
        # - The transient config (action, specific lighting)
        # - The persistent state (characters, environment)

        # Start with the persistent state as a base config
        resolution_config = self.state_machine.get_current_state_as_config()

        # Merge in the specific request's config (which overrides persistent state if specified)
        # Note: In a real logic we might be recursive, but simple merge for now
        # We manually copy over the non-state things from the request config
        resolution_config.action_description = action
        if config.cinematography:
            resolution_config.cinematography = config.cinematography
        if config.lighting:
            resolution_config.lighting = config.lighting
        if config.continuity:
            resolution_config.continuity = config.continuity
        resolution_config.duration_seconds = config.duration_seconds

        # Compile
        compiled_prompt = self.compiler.compile(resolution_config)
        # Fallback if compile returns empty (e.g. no fancy config)
        final_prompt = compiled_prompt if compiled_prompt.strip(
        ) else f"{concept}: {action}"

        logger.info(f"Compiled Prompt Length: {len(final_prompt)}")
        logger.debug(f"Compiled Prompt: {final_prompt}")

        # 4. execute
        request = VideoGenerationRequest(
            prompt=final_prompt,
            duration_seconds=config.duration_seconds,
            aspect_ratio=config.aspect_ratio,
            negative_prompt=config.negative_prompt,
            seed=config.seed
        )

        result = await self.provider.generate_video(request)

        # 5. Future: Capture result into state (feedback loop)

        return result

    async def generate_sequence(self,
                                segments: List[Dict[str, Any]],
                                base_config: Optional[VideoConfig] = None) -> List[VideoGenerationResult]:
        """
        Orchestrate a sequence of scenes.
        """
        if base_config:
            self.state_machine.update_from_config(base_config)

        results = []
        for segment in segments:
            # Create a transient config choice for this segment
            # This is where we would interpret "storyboard-as-code"
            seg_config = base_config or VideoConfig()  # fallback

            # Simple override if segment has specific state updates (legacy support)
            # In the new system, we'd look for specific `Character` objects in the segment dict

            concept = segment.get("concept", "")
            action = segment.get("action", "")

            result = await self.schedule_generation(concept, action, seg_config)
            results.append(result)

        return results

    async def generate_scene(self, scene: SceneConfig, base_config: Optional[VideoConfig] = None) -> List[VideoGenerationResult]:
        """
        Generate a full cinematic scene with multiple shots and continuity.
        """
        if base_config is None:
            base_config = DEFAULT_CONFIG

        # Update state machine with scene-level characters and environment
        scene_base_config = copy.deepcopy(base_config)

        # Merge scene characters: preserve identity, update transient state
        for name, char in scene.characters.items():
            if name in scene_base_config.characters:
                existing = scene_base_config.characters[name]
                if hasattr(char, 'identity') and char.identity:
                    existing.identity.update(char.identity)
                if hasattr(char, 'current_state') and char.current_state:
                    existing.current_state.update(char.current_state)
            else:
                scene_base_config.characters[name] = char

        if scene.environment:
            if scene_base_config.environment and scene_base_config.environment.location == scene.environment.location:
                if hasattr(scene.environment, 'identity') and scene.environment.identity:
                    scene_base_config.environment.identity.update(
                        scene.environment.identity)
                if hasattr(scene.environment, 'current_context') and scene.environment.current_context:
                    scene_base_config.environment.current_context.update(
                        scene.environment.current_context)
            else:
                scene_base_config.environment = scene.environment

        self.state_machine.update_from_config(scene_base_config)

        # Define output directory from config
        output_dir = Path(scene_base_config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        last_frames = []

        for i, shot in enumerate(scene.shots):
            logger.info(
                f"Generating shot {i+1}/{len(scene.shots)}: {shot.shot_type}")

            # Smart Cut Detection: If environment changes, reset continuity frames
            if shot.environment and self.state_machine.environment:
                if shot.environment.location != self.state_machine.environment.location:
                    logger.info(
                        "Environment change detected. Resetting continuity frames.")
                    last_frames = []

            # Apply programmable cuts (shot-level overrides)
            if shot.characters or shot.environment:
                override_config = VideoConfig()
                if shot.characters:
                    override_config.characters = shot.characters
                if shot.environment:
                    override_config.environment = shot.environment
                self.state_machine.update_from_config(override_config)

            # Prepare shot-specific config
            shot_config = self.state_machine.get_current_state_as_config()
            shot_config.action_description = shot.action
            shot_config.duration_seconds = shot.duration_seconds
            shot_config.custom_metadata["shot_type"] = shot.shot_type

            # Continuity logic: last 3 frames from previous shot if required
            continuity_frames = None
            if shot.continuity_required and last_frames:
                continuity_frames = last_frames

            # Character and Background samples
            char_samples = {}
            for name, char in shot_config.characters.items():
                samples = []
                # Prioritize visual anchor as the first and most important sample
                if hasattr(char, 'visual_anchor_path') and char.visual_anchor_path:
                    samples.append(char.visual_anchor_path)

                # Add remainder of reference images
                if char.reference_images:
                    samples.extend(char.reference_images)

                if samples:
                    char_samples[name] = samples

            bg_samples = shot_config.environment.reference_images if shot_config.environment else []
            if hasattr(shot_config.environment, 'visual_anchor_path') and shot_config.environment.visual_anchor_path:
                bg_samples = [
                    shot_config.environment.visual_anchor_path] + bg_samples

            # Compile prompt
            final_prompt = self.compiler.compile(shot_config)

            # Build request
            request = VideoGenerationRequest(
                prompt=final_prompt,
                duration_seconds=shot.duration_seconds,
                aspect_ratio=shot_config.aspect_ratio,
                negative_prompt=shot_config.negative_prompt,
                seed=shot_config.seed,
                starting_frames=continuity_frames,
                character_samples=char_samples,
                background_samples=bg_samples,
                previous_narration=shot_config.custom_metadata.get(
                    "last_narration")
            )

            # Execute Audio Generation first if duration is None (auto)
            audio_text = shot.narration or shot.dialogue
            audio_path = None
            speaker_name = None

            if audio_text:
                # Find the character's voice_id and profile
                voice_id = "default"
                voice_profile = None

                if shot.narration:
                    speaker_name = "Narrator"
                    voice_id = "en-US-Studio-O"
                elif shot.dialogue and ":" in shot.dialogue:
                    speaker_name, dialogue_text = shot.dialogue.split(":", 1)
                    speaker_name = speaker_name.strip()
                    audio_text = dialogue_text.strip()
                    char = shot_config.characters.get(speaker_name)
                    if char:
                        voice_id = char.voice_id or voice_id
                        voice_profile = char.voice_profile

                audio_path = await self.audio_provider.generate_audio(
                    AudioRequest(
                        text=audio_text,
                        voice_id=voice_id,
                        voice_profile=voice_profile
                    )
                )

                # Dynamic Duration Logic: Calculate duration from audio if requested
                if shot.duration_seconds is None:
                    from moviepy import AudioFileClip
                    try:
                        audio_clip = AudioFileClip(str(audio_path))
                        shot_config.duration_seconds = int(
                            audio_clip.duration) + 1  # Add small buffer
                        audio_clip.close()
                        logger.info(
                            f"Auto-calculated duration for shot {i+1}: {shot_config.duration_seconds}s")
                    except Exception as e:
                        logger.warning(
                            f"Failed to calculate audio duration: {e}. Defaulting to 5s")
                        shot_config.duration_seconds = 5

            # Execute Video Generation (with Recursive Splitting for long shots)
            target_duration = shot_config.duration_seconds or 8
            max_dur = getattr(self.provider, 'max_duration', 8)

            if target_duration > max_dur:
                logger.info(
                    f"Shot {i+1} duration ({target_duration}s) exceeds provider limit ({max_dur}s). Splitting into segments...")

                segment_results = []
                remaining_duration = target_duration
                current_continuity = continuity_frames

                while remaining_duration > 0:
                    chunk_dur = min(remaining_duration, max_dur)
                    # If remaining is too small (e.g. 1s), just add it to the last chunk if possible,
                    # but Veo has strict 4-8 range. For now we'll just clamp.
                    if chunk_dur < 4 and remaining_duration == chunk_dur:
                        chunk_dur = 4  # Minimum duration

                    logger.info(
                        f"Generating segment chunk: {chunk_dur}s (Remaining: {remaining_duration}s)")

                    chunk_request = VideoGenerationRequest(
                        prompt=final_prompt,
                        duration_seconds=int(chunk_dur),
                        aspect_ratio=shot_config.aspect_ratio,
                        negative_prompt=shot_config.negative_prompt,
                        seed=shot_config.seed,
                        starting_frames=current_continuity,
                        character_samples=char_samples,
                        background_samples=bg_samples,
                        previous_narration=shot_config.custom_metadata.get(
                            "last_narration")
                    )

                    chunk_result = await self.provider.generate_video(chunk_request)
                    if not chunk_result.success:
                        logger.error(
                            f"Chunk generation failed: {chunk_result.error}")
                        result = chunk_result
                        break

                    # SAVE CHUNK IMMEDIATELY for frame extraction
                    chunk_filename = f"shot_{i+1}_segment_{len(segment_results)}_{int(time.time())}.mp4"
                    chunk_path = Path(shot_config.output_dir) / chunk_filename
                    if chunk_result.video_bytes:
                        chunk_path.write_bytes(chunk_result.video_bytes)
                        chunk_result.video_path = chunk_path

                    segment_results.append(chunk_result)
                    remaining_duration -= chunk_dur

                    if remaining_duration > 0 and chunk_result.video_path:
                        # Extract last frame for the next chunk's starting_frames
                        frame_dir = Path(
                            shot_config.output_dir) / "temp_frames"
                        from .utils import extract_last_frames
                        current_continuity = extract_last_frames(
                            chunk_result.video_path, frame_dir, num_frames=1)

                # Merge all segments into one final result for this shot
                if len(segment_results) > 1:
                    from .utils import merge_videos
                    shot_video_path = Path(
                        shot_config.output_dir) / f"shot_{i+1}_full.mp4"
                    success = merge_videos(
                        [r.video_path for r in segment_results], shot_video_path)

                    if success:
                        result = VideoGenerationResult(
                            success=True,
                            video_path=shot_video_path,
                            provider=self.provider.name,
                            metadata={"segments": len(segment_results)}
                        )
                    else:
                        result = segment_results[0]  # Fallback
                elif segment_results:
                    result = segment_results[0]
                # else result is already the failure from the loop
            else:
                # Standard single-shot generation
                request = VideoGenerationRequest(
                    prompt=final_prompt,
                    duration_seconds=target_duration,
                    aspect_ratio=shot_config.aspect_ratio,
                    negative_prompt=shot_config.negative_prompt,
                    seed=shot_config.seed,
                    starting_frames=continuity_frames,
                    character_samples=char_samples,
                    background_samples=bg_samples,
                    previous_narration=shot_config.custom_metadata.get(
                        "last_narration")
                )
                result = await self.provider.generate_video(request)

            # Link audio and metadata to result
            if audio_path:
                result.audio_path = audio_path
                result.metadata["speaker"] = speaker_name

            # Save the video shot immediately so we have a path for continuity extraction
            if result.success and result.video_bytes and output_dir:
                # Use a more sequential naming pattern: shot_001, shot_002, etc.
                shot_idx_str = str(len(results)).zfill(3)
                filename = f"shot_{shot_idx_str}_{int(time.time())}.mp4"
                video_path = output_dir / filename
                video_path.write_bytes(result.video_bytes)
                result.video_path = video_path
                logger.debug(f"Shot saved to {video_path}")

            results.append(result)

            # Advance state and extract frames for next shot
            if result.success and result.video_path:
                # Use utils to extract frames
                shot_output_dir = result.video_path.parent / \
                    f"frames_{result.video_path.stem}"
                last_frames = extract_last_frames(
                    result.video_path, shot_output_dir)

                # Commit to state machine
                self.state_machine.next_scene(
                    video_path=result.video_path,
                    frames=last_frames,
                    speaker=result.metadata.get("speaker"),
                    narration=audio_text if audio_text else None
                )
            else:
                self.state_machine.next_scene()

        return results

    async def generate_production(self,
                                  scene: SceneConfig,
                                  base_config: Optional[VideoConfig] = None,
                                  output_filename: Optional[str] = None,
                                  upload_to_s3: bool = False) -> Dict[str, Any]:
        """
        Generate a full production: multiple shots merged with audio and subtitles.
        """
        if base_config is None:
            base_config = VideoConfig()

        output_dir = Path(base_config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generate all shots
        results = await self.generate_scene(scene, base_config)

        # 2. Extract scripts for overlays
        scripts = [shot.narration or shot.dialogue for shot in scene.shots]

        # 3. Merge into final production
        timestamp = int(time.time())
        final_filename = output_filename or f"production_{scene.concept.replace(' ', '_')}_{timestamp}.mp4"
        final_path = output_dir / final_filename

        success = merge_production(results, final_path, scripts)

        response = {
            "success": success,
            "local_path": str(final_path) if success else None,
            "results": results
        }

        # 4. Upload to S3 if requested
        if success and upload_to_s3:
            s3_url = self.s3_uploader.upload_file(final_path)
            response["s3_url"] = s3_url

        return response
