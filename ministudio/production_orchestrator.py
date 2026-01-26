"""
Enhanced Video Production Orchestrator
======================================
Production-grade orchestrator that integrates all cinematic pipeline components.

Features:
- Multi-provider support with registry
- Scene graph for continuity
- Shot plan execution
- Intelligent splitting and retry
- Post-processing pipeline
- Full production manifest
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from .registry import ProviderRegistry, get_registry, ProviderStatus
from .scene_graph import SceneGraph, Entity, EntityType, CharacterState, EmotionalState
from .shot_plan import ShotPlan, Shot, Scene, CharacterDefinition
from .prompt_compiler import StructuredPromptCompiler, CompiledPrompt, PromptStyle
from .shot_splitter import ShotSplitter, Segment, SplitConfig, RetryHandler, RetryStrategy
from .audio_system import AudioTimeline, AudioGenerator
from .post_processor import PostProcessor, ColorGradeSettings, ProductionManifest, get_color_grade
from .cinematography import CinematographyProfile


logger = logging.getLogger(__name__)


@dataclass
class ProductionConfig:
    """Configuration for a video production."""
    # Output settings
    output_dir: str = "./output"
    resolution: str = "1920x1080"
    frame_rate: int = 24
    aspect_ratio: str = "16:9"
    
    # Provider settings
    default_provider: Optional[str] = None
    fallback_providers: List[str] = field(default_factory=list)
    
    # Generation settings
    max_segment_duration: float = 8.0
    min_segment_duration: float = 2.0
    max_retries: int = 3
    
    # Post-processing
    color_preset: str = "cinematic"
    enable_transitions: bool = True
    
    # Continuity
    maintain_character_consistency: bool = True
    save_keyframes: bool = True
    
    # Debug
    save_prompts: bool = True
    verbose: bool = False


@dataclass
class ProductionProgress:
    """Track production progress."""
    total_shots: int = 0
    completed_shots: int = 0
    total_segments: int = 0
    completed_segments: int = 0
    current_stage: str = "initializing"
    errors: List[str] = field(default_factory=list)
    
    @property
    def progress(self) -> float:
        if self.total_segments == 0:
            return 0.0
        return self.completed_segments / self.total_segments
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_shots": self.total_shots,
            "completed_shots": self.completed_shots,
            "total_segments": self.total_segments,
            "completed_segments": self.completed_segments,
            "current_stage": self.current_stage,
            "progress": self.progress,
            "errors": self.errors
        }


class ProductionOrchestrator:
    """
    Enhanced orchestrator for professional video production.
    
    Integrates:
    - ProviderRegistry for multi-model generation
    - SceneGraph for continuity tracking
    - ShotPlan for structured production
    - PromptCompiler for provider-optimized prompts
    - ShotSplitter for intelligent segmentation
    - PostProcessor for final assembly
    """
    
    def __init__(
        self,
        config: Optional[ProductionConfig] = None,
        registry: Optional[ProviderRegistry] = None
    ):
        self.config = config or ProductionConfig()
        self.registry = registry or get_registry()
        
        # Initialize components
        self.scene_graph = SceneGraph()
        self.prompt_compiler = StructuredPromptCompiler(style=PromptStyle.STANDARD)
        self.shot_splitter = ShotSplitter(SplitConfig(
            max_segment_duration=self.config.max_segment_duration,
            min_segment_duration=self.config.min_segment_duration,
            max_retries=self.config.max_retries
        ))
        self.retry_handler = RetryHandler()
        self.audio_generator: Optional[AudioGenerator] = None
        
        # Production state
        self.current_plan: Optional[ShotPlan] = None
        self.audio_timeline: Optional[AudioTimeline] = None
        self.progress = ProductionProgress()
        self.generated_clips: List[Dict[str, Any]] = []
        
        # Output paths
        self.output_dir = Path(self.config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Callbacks
        self._on_progress: Optional[Callable[[ProductionProgress], None]] = None
        self._on_shot_complete: Optional[Callable[[Shot, str], None]] = None
    
    def set_progress_callback(self, callback: Callable[[ProductionProgress], None]):
        """Set callback for progress updates."""
        self._on_progress = callback
    
    def set_shot_complete_callback(self, callback: Callable[[Shot, str], None]):
        """Set callback when a shot completes."""
        self._on_shot_complete = callback
    
    async def produce(
        self,
        plan: ShotPlan,
        audio_timeline: Optional[AudioTimeline] = None
    ) -> str:
        """
        Execute a complete production from a shot plan.
        
        Args:
            plan: The shot plan to produce
            audio_timeline: Optional audio timeline
        
        Returns:
            Path to final assembled video
        """
        self.current_plan = plan
        self.audio_timeline = audio_timeline
        self.generated_clips = []
        
        try:
            # Initialize scene graph with characters
            self._init_scene_graph(plan)
            
            # Stage 1: Prepare segments
            self._update_progress("preparing")
            all_segments = self._prepare_segments(plan)
            self.progress.total_segments = len(all_segments)
            self.progress.total_shots = len(plan.get_all_shots())
            
            # Stage 2: Generate audio (if provided)
            if audio_timeline:
                self._update_progress("generating_audio")
                await self._generate_audio(audio_timeline)
            
            # Stage 3: Generate video segments
            self._update_progress("generating_video")
            await self._generate_segments(all_segments, plan)
            
            # Stage 4: Post-processing
            self._update_progress("post_processing")
            output_path = await self._post_process(plan.title)
            
            # Stage 5: Generate manifest
            self._update_progress("finalizing")
            self._generate_manifest(plan, output_path)
            
            self._update_progress("complete")
            return output_path
            
        except Exception as e:
            self.progress.errors.append(str(e))
            logger.error(f"Production failed: {e}")
            raise
    
    def _init_scene_graph(self, plan: ShotPlan):
        """Initialize scene graph with plan data."""
        self.scene_graph = SceneGraph()
        
        # Add characters from plan
        for char_id, char_def in plan.characters.items():
            entity = Entity(
                entity_id=char_id,
                name=char_def.name,
                entity_type=EntityType.CHARACTER,
                visual_anchor=char_def.visual_anchor
            )
            
            # Set initial state
            entity.character_state = CharacterState(
                emotion=EmotionalState.NEUTRAL,
                emotion_intensity=0.5
            )
            
            self.scene_graph.add_entity(entity)
    
    def _prepare_segments(self, plan: ShotPlan) -> List[Segment]:
        """Prepare all segments for generation."""
        # Get provider max duration
        provider = self._get_provider(plan.default_provider)
        max_duration = self.config.max_segment_duration
        
        if provider:
            # Check provider capabilities
            capabilities = getattr(provider, 'capabilities', {})
            max_duration = capabilities.get('max_duration', max_duration)
        
        # Split all shots
        return self.shot_splitter.split_plan(plan, max_duration)
    
    async def _generate_audio(self, timeline: AudioTimeline):
        """Generate all audio from timeline."""
        if not self.audio_generator:
            logger.warning("No audio generator configured, skipping audio")
            return
        
        audio_dir = self.output_dir / "audio"
        audio_dir.mkdir(exist_ok=True)
        
        await self.audio_generator.generate_timeline_audio(timeline, audio_dir)
    
    async def _generate_segments(
        self,
        segments: List[Segment],
        plan: ShotPlan
    ):
        """Generate all video segments."""
        for i, segment in enumerate(segments):
            try:
                # Find the parent shot
                shot = self._find_shot(segment.parent_shot_id, plan)
                if not shot:
                    logger.warning(f"Shot not found for segment {segment.segment_id}")
                    continue
                
                # Compile prompt
                compiled = self.prompt_compiler.compile(
                    shot, 
                    self.scene_graph, 
                    plan
                )
                
                # Get starting frame if needed
                starting_frame = None
                if segment.requires_starting_frame:
                    starting_frame = self._get_starting_frame(segment)
                
                # Generate video
                output_path = await self._generate_segment(
                    segment, 
                    compiled, 
                    starting_frame
                )
                
                # Update scene graph
                self._update_scene_graph(shot)
                
                # Store result
                self.generated_clips.append({
                    "clip_id": segment.segment_id,
                    "path": output_path,
                    "segment": segment,
                    "shot_id": shot.shot_id,
                    "scene_number": self._get_scene_number(shot, plan),
                    "shot_number": shot.order,
                    "duration": segment.duration,
                    "start_time": segment.start_time,
                    "end_time": segment.end_time
                })
                
                self.progress.completed_segments += 1
                self._notify_progress()
                
                # Callback
                if self._on_shot_complete and segment.index == 0:
                    self._on_shot_complete(shot, output_path)
                
            except Exception as e:
                logger.error(f"Failed to generate segment {segment.segment_id}: {e}")
                self.progress.errors.append(f"Segment {segment.segment_id}: {e}")
                
                # Attempt retry
                await self._handle_retry(segment, str(e), plan)
    
    async def _generate_segment(
        self,
        segment: Segment,
        compiled: CompiledPrompt,
        starting_frame: Optional[str] = None
    ) -> str:
        """Generate a single video segment."""
        # Get provider
        provider_name = segment.provider or self.config.default_provider
        provider = self._get_provider(provider_name)
        
        if not provider:
            raise ValueError(f"No provider available: {provider_name}")
        
        # Get provider-optimized prompt
        prompt = compiled.get_for_provider(provider_name) if provider_name else compiled.main_prompt
        
        # Output path
        output_path = self.output_dir / "segments" / f"{segment.segment_id}.mp4"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save prompt for debugging
        if self.config.save_prompts:
            prompt_path = self.output_dir / "prompts" / f"{segment.segment_id}.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt)
        
        # Generate
        try:
            # Most providers have an async generate method
            if hasattr(provider, 'generate_async'):
                result = await provider.generate_async(
                    prompt=prompt,
                    duration=segment.duration,
                    starting_frame=starting_frame,
                    negative_prompt=compiled.negative_prompt
                )
            else:
                # Fallback to sync
                result = provider.generate(
                    prompt=prompt,
                    duration=segment.duration,
                    starting_frame=starting_frame
                )
            
            # Handle result (might be path or bytes)
            if isinstance(result, (str, Path)):
                return str(result)
            elif isinstance(result, bytes):
                output_path.write_bytes(result)
                return str(output_path)
            else:
                # Assume it's a result object with a path
                return getattr(result, 'video_path', str(output_path))
                
        except Exception as e:
            # Record failure in registry
            self.registry.record_result(provider_name, False, 0)
            raise
    
    async def _handle_retry(
        self,
        segment: Segment,
        error: str,
        plan: ShotPlan
    ):
        """Handle segment generation failure with retry."""
        for attempt in range(self.config.max_retries):
            try:
                shot = self._find_shot(segment.parent_shot_id, plan)
                compiled = self.prompt_compiler.compile(shot, self.scene_graph, plan)
                
                # Try with fallback provider
                if self.config.fallback_providers:
                    fallback = self.config.fallback_providers[
                        attempt % len(self.config.fallback_providers)
                    ]
                    segment.provider = fallback
                    logger.info(f"Retrying with fallback provider: {fallback}")
                
                output_path = await self._generate_segment(segment, compiled)
                
                # Success
                self.generated_clips.append({
                    "clip_id": segment.segment_id,
                    "path": output_path,
                    "segment": segment,
                    "retry_attempt": attempt + 1
                })
                return
                
            except Exception as retry_error:
                logger.warning(f"Retry {attempt + 1} failed: {retry_error}")
        
        logger.error(f"All retries failed for segment {segment.segment_id}")
    
    async def _post_process(self, title: str) -> str:
        """Run post-processing pipeline."""
        processor = PostProcessor(
            output_dir=self.output_dir,
            temp_dir=self.output_dir / "temp"
        )
        
        # Get color grade
        color_grade = get_color_grade(self.config.color_preset)
        
        # Prepare clip data
        clips = []
        for clip_data in self.generated_clips:
            clips.append({
                "clip_id": clip_data["clip_id"],
                "path": clip_data["path"],
                "scene_number": clip_data.get("scene_number", 1),
                "shot_number": clip_data.get("shot_number", 0),
                "duration": clip_data.get("duration", 0),
                "start_time": clip_data.get("start_time", 0),
                "end_time": clip_data.get("end_time", 0)
            })
        
        # Run post-processing
        return await processor.process(
            clips=clips,
            title=title,
            color_grade=color_grade,
            on_progress=lambda stage, prog: self._update_progress(f"post_{stage}")
        )
    
    def _generate_manifest(self, plan: ShotPlan, output_path: str):
        """Generate production manifest."""
        manifest = ProductionManifest(
            production_id=f"prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=plan.title,
            created_at=datetime.now().isoformat(),
            resolution=self.config.resolution,
            frame_rate=self.config.frame_rate,
            aspect_ratio=self.config.aspect_ratio,
            output_path=output_path,
            total_duration=sum(c.get("duration", 0) for c in self.generated_clips)
        )
        
        # Add generation info
        for clip in self.generated_clips:
            manifest.clips.append({
                "clip_id": clip["clip_id"],
                "path": clip["path"],
                "duration": clip.get("duration", 0)
            })
        
        # Save
        manifest_path = self.output_dir / f"{plan.title}_manifest.json"
        manifest.save(manifest_path)
    
    def _find_shot(self, shot_id: str, plan: ShotPlan) -> Optional[Shot]:
        """Find a shot by ID in the plan."""
        for shot in plan.get_all_shots():
            if shot.shot_id == shot_id:
                return shot
        return None
    
    def _get_scene_number(self, shot: Shot, plan: ShotPlan) -> int:
        """Get the scene number for a shot."""
        for i, scene in enumerate(plan.scenes):
            if shot.scene_id == scene.scene_id:
                return i + 1
        return 1
    
    def _get_provider(self, name: Optional[str]):
        """Get a provider by name from registry."""
        if name:
            return self.registry.get(name)
        
        # Get any healthy provider
        return self.registry.get_with_fallback(
            self.config.fallback_providers or []
        )
    
    def _get_starting_frame(self, segment: Segment) -> Optional[str]:
        """Get the starting frame for continuity."""
        if not segment.starting_frame_source:
            return None
        
        # Find the previous clip
        for clip in self.generated_clips:
            if clip["clip_id"] == segment.starting_frame_source:
                # Extract last frame (in real implementation)
                return clip["path"]
        
        return None
    
    def _update_scene_graph(self, shot: Shot):
        """Update scene graph after shot generation."""
        # Update character states
        for char_id, char_spec in shot.characters.items():
            entity = self.scene_graph.get_entity(char_id)
            if entity and entity.character_state:
                # Parse emotion
                try:
                    emotion = EmotionalState(char_spec.emotion)
                except ValueError:
                    emotion = EmotionalState.NEUTRAL
                
                self.scene_graph.update_character_emotion(
                    char_id, emotion, char_spec.emotion_intensity
                )
        
        # Take snapshot for continuity
        if self.config.save_keyframes:
            self.scene_graph.take_snapshot(f"shot_{shot.shot_id}")
    
    def _update_progress(self, stage: str):
        """Update progress state."""
        self.progress.current_stage = stage
        self._notify_progress()
    
    def _notify_progress(self):
        """Notify progress callback."""
        if self._on_progress:
            self._on_progress(self.progress)


# ============ Convenience Functions ============

async def produce_from_plan(
    plan: ShotPlan,
    output_dir: str = "./output",
    provider: Optional[str] = None,
    color_preset: str = "cinematic"
) -> str:
    """
    Quick production from a shot plan.
    
    Args:
        plan: The shot plan to produce
        output_dir: Output directory
        provider: Provider name to use
        color_preset: Color grading preset
    
    Returns:
        Path to final video
    """
    config = ProductionConfig(
        output_dir=output_dir,
        default_provider=provider,
        color_preset=color_preset
    )
    
    orchestrator = ProductionOrchestrator(config)
    return await orchestrator.produce(plan)


async def quick_produce(
    shots: List[Dict[str, Any]],
    title: str = "production",
    output_dir: str = "./output"
) -> str:
    """
    Quick production from simple shot definitions.
    
    Args:
        shots: List of shot definitions with 'action' key
        title: Production title
        output_dir: Output directory
    
    Returns:
        Path to final video
    """
    # Create plan from shots
    plan = ShotPlan.create(title)
    scene = plan.create_scene("Main Scene")
    
    for shot_def in shots:
        shot = Shot(
            action=shot_def.get("action", ""),
            duration=shot_def.get("duration"),
        )
        scene.add_shot(shot)
    
    return await produce_from_plan(plan, output_dir)
