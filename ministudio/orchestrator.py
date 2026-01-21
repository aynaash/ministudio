"""
Video Orchestrator.
The "Kubernetes like Controller" that coordinates State, Compilation, and Execution.
"""

import copy
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import VideoConfig, DEFAULT_CONFIG, SceneConfig, ShotConfig, ShotType
from .state import VideoStateMachine
from .compiler import ProgrammaticPromptCompiler
from .interfaces import VideoProvider, VideoGenerationResult, VideoGenerationRequest
from .utils import extract_last_frames
from .audio import AudioRequest, AudioProvider, MockAudioProvider

logger = logging.getLogger(__name__)


class VideoOrchestrator:
    def __init__(self, provider: VideoProvider):
        self.provider = provider
        # Each orchestrator manages a specific state machine (like a specific deployment)
        self.state_machine = VideoStateMachine()
        self.compiler = ProgrammaticPromptCompiler()
        self.audio_provider = MockAudioProvider()  # Default audio provider

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
        scene_base_config.characters.update(scene.characters)
        if scene.environment:
            scene_base_config.environment = scene.environment

        self.state_machine.update_from_config(scene_base_config)

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
            char_samples = {
                name: char.reference_images
                for name, char in shot_config.characters.items()
                if char.reference_images
            }
            bg_samples = shot_config.environment.reference_images if shot_config.environment else []

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
                background_samples=bg_samples
            )

            # Execute Video Generation
            result = await self.provider.generate_video(request)

            # Execute Dialogue or Narration Generation if present
            audio_text = shot.narration or shot.dialogue
            if audio_text:
                # Find the character's voice_id and profile
                speaker_name = None
                voice_id = "default"
                voice_profile = None

                if shot.narration:
                    speaker_name = "Narrator"
                    voice_id = "narrator_id"
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
                result.audio_path = audio_path
                result.metadata["speaker"] = speaker_name

            # Save the video shot immediately so we have a path for continuity extraction
            if result.success and result.video_bytes and output_dir:
                filename = f"scene_{scene.concept.replace(' ', '_')}_shot_{len(results)}_{int(time.time())}.mp4"
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
                    speaker=result.metadata.get("speaker")
                )
            else:
                self.state_machine.next_scene()

        return results
