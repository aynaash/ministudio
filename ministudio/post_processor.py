"""
Post-Processing Pipeline
========================
Automated post-production with transitions, color grading, and final assembly.

Features:
- Sequential file naming
- Transition generation
- Color grading
- Audio mixing
- Final assembly
- Production manifest generation
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime
import shutil


class PostProcessStep(Enum):
    """Post-processing pipeline steps."""
    RENAME_FILES = "rename_files"
    TRANSITIONS = "transitions"
    COLOR_GRADE = "color_grade"
    AUDIO_SYNC = "audio_sync"
    AUDIO_MIX = "audio_mix"
    ASSEMBLY = "assembly"
    MANIFEST = "manifest"
    CLEANUP = "cleanup"


@dataclass
class ProcessedClip:
    """A processed video clip ready for assembly."""
    clip_id: str
    original_path: str
    processed_path: str
    
    # Timing
    start_time: float
    end_time: float
    duration: float
    
    # Sequence
    sequence_number: int
    scene_number: int
    shot_number: int
    
    # Transitions
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    transition_duration: float = 0.5
    
    # Audio
    audio_path: Optional[str] = None
    audio_synced: bool = False
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_sequential_name(self) -> str:
        """Get sequential filename."""
        return f"scene{self.scene_number:02d}_shot{self.shot_number:02d}_{self.sequence_number:04d}.mp4"


@dataclass
class ColorGradeSettings:
    """Color grading settings."""
    # Basic adjustments
    brightness: float = 0.0  # -1.0 to 1.0
    contrast: float = 1.0  # 0.0 to 2.0
    saturation: float = 1.0  # 0.0 to 2.0
    gamma: float = 1.0
    
    # Color temperature
    temperature: float = 0.0  # -1.0 (cool) to 1.0 (warm)
    tint: float = 0.0  # -1.0 (green) to 1.0 (magenta)
    
    # Curves (simplified)
    shadows: float = 0.0  # Lift
    midtones: float = 0.0  # Gamma
    highlights: float = 0.0  # Gain
    
    # LUT
    lut_path: Optional[str] = None
    lut_intensity: float = 1.0
    
    # Film effects
    film_grain: float = 0.0  # 0.0 to 1.0
    vignette: float = 0.0  # 0.0 to 1.0
    
    def to_ffmpeg_filters(self) -> str:
        """Generate FFmpeg filter string."""
        filters = []
        
        # Brightness/Contrast
        if self.brightness != 0 or self.contrast != 1:
            filters.append(f"eq=brightness={self.brightness}:contrast={self.contrast}")
        
        # Saturation
        if self.saturation != 1:
            filters.append(f"eq=saturation={self.saturation}")
        
        # Gamma
        if self.gamma != 1:
            filters.append(f"eq=gamma={self.gamma}")
        
        # Color temperature (simplified using colorbalance)
        if self.temperature != 0:
            r_adj = self.temperature * 0.3
            b_adj = -self.temperature * 0.3
            filters.append(f"colorbalance=rs={r_adj}:bs={b_adj}")
        
        # Shadows/Midtones/Highlights
        if any([self.shadows, self.midtones, self.highlights]):
            filters.append(
                f"curves=m='0/0 0.5/{0.5+self.midtones*0.2} 1/1'"
            )
        
        # Vignette
        if self.vignette > 0:
            filters.append(f"vignette=angle={self.vignette}*PI/4")
        
        # Film grain (noise)
        if self.film_grain > 0:
            grain_amount = int(self.film_grain * 30)
            filters.append(f"noise=alls={grain_amount}:allf=t")
        
        # LUT
        if self.lut_path:
            filters.append(f"lut3d={self.lut_path}:interp=trilinear")
            if self.lut_intensity < 1:
                # Blend with original
                filters.append(f"blend=all_mode=normal:all_opacity={self.lut_intensity}")
        
        return ",".join(filters) if filters else "null"


@dataclass
class TransitionSpec:
    """Specification for a transition between clips."""
    type: str  # cut, fade, dissolve, wipe, etc.
    duration: float = 0.5
    
    # Type-specific parameters
    direction: str = "left"  # For wipes
    color: str = "#000000"  # For fade to color
    easing: str = "linear"  # linear, ease_in, ease_out, ease_in_out
    
    def to_ffmpeg_filter(self, clip1_end: float, clip2_start: float) -> str:
        """Generate FFmpeg xfade filter."""
        offset = clip1_end - self.duration
        
        transition_map = {
            "cut": "fade",  # Instant
            "fade": "fade",
            "dissolve": "dissolve",
            "wipe": "wipeleft" if self.direction == "left" else "wiperight",
            "slide": "slideleft" if self.direction == "left" else "slideright",
            "zoom": "zoomin",
            "circle": "circlecrop",
        }
        
        xfade_type = transition_map.get(self.type, "fade")
        
        return f"xfade=transition={xfade_type}:duration={self.duration}:offset={offset}"


@dataclass
class ProductionManifest:
    """Complete production manifest for reproducibility."""
    # Identity
    production_id: str
    title: str
    created_at: str
    
    # Settings
    resolution: str = "1920x1080"
    frame_rate: int = 24
    aspect_ratio: str = "16:9"
    codec: str = "h264"
    
    # Clips
    clips: List[Dict[str, Any]] = field(default_factory=list)
    
    # Audio
    audio_tracks: List[Dict[str, Any]] = field(default_factory=list)
    
    # Processing
    color_grade: Optional[Dict[str, Any]] = None
    transitions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Output
    output_path: Optional[str] = None
    total_duration: float = 0.0
    
    # Generation metadata
    providers_used: List[str] = field(default_factory=list)
    prompts: List[Dict[str, str]] = field(default_factory=list)
    generation_times: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "production_id": self.production_id,
            "title": self.title,
            "created_at": self.created_at,
            "settings": {
                "resolution": self.resolution,
                "frame_rate": self.frame_rate,
                "aspect_ratio": self.aspect_ratio,
                "codec": self.codec
            },
            "clips": self.clips,
            "audio_tracks": self.audio_tracks,
            "color_grade": self.color_grade,
            "transitions": self.transitions,
            "output": {
                "path": self.output_path,
                "total_duration": self.total_duration
            },
            "generation": {
                "providers_used": self.providers_used,
                "prompts": self.prompts,
                "generation_times": self.generation_times
            }
        }
    
    def save(self, path: Path):
        """Save manifest to JSON."""
        path.write_text(json.dumps(self.to_dict(), indent=2))
    
    @classmethod
    def load(cls, path: Path) -> "ProductionManifest":
        """Load manifest from JSON."""
        data = json.loads(path.read_text())
        return cls(
            production_id=data["production_id"],
            title=data["title"],
            created_at=data["created_at"],
            resolution=data["settings"]["resolution"],
            frame_rate=data["settings"]["frame_rate"],
            aspect_ratio=data["settings"]["aspect_ratio"],
            codec=data["settings"]["codec"],
            clips=data["clips"],
            audio_tracks=data["audio_tracks"],
            color_grade=data.get("color_grade"),
            transitions=data.get("transitions", []),
            output_path=data["output"]["path"],
            total_duration=data["output"]["total_duration"],
            providers_used=data["generation"]["providers_used"],
            prompts=data["generation"]["prompts"],
            generation_times=data["generation"]["generation_times"]
        )


class PostProcessor:
    """
    Handles post-production pipeline for generated videos.
    
    Pipeline:
    1. Rename files sequentially
    2. Apply color grading
    3. Generate transitions
    4. Sync and mix audio
    5. Assemble final video
    6. Generate production manifest
    """
    
    def __init__(
        self,
        output_dir: Path,
        temp_dir: Optional[Path] = None
    ):
        self.output_dir = Path(output_dir)
        self.temp_dir = temp_dir or self.output_dir / "temp"
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline state
        self.clips: List[ProcessedClip] = []
        self.manifest: Optional[ProductionManifest] = None
        
        # Settings
        self.color_grade: Optional[ColorGradeSettings] = None
        self.default_transition = TransitionSpec(type="cut", duration=0.0)
    
    async def process(
        self,
        clips: List[Dict[str, Any]],
        title: str = "production",
        color_grade: Optional[ColorGradeSettings] = None,
        on_progress: Optional[Callable[[str, float], None]] = None
    ) -> str:
        """
        Run complete post-processing pipeline.
        
        Args:
            clips: List of clip info dicts with paths, timing, etc.
            title: Production title
            color_grade: Optional color grading settings
            on_progress: Optional progress callback (step_name, progress)
        
        Returns:
            Path to final assembled video
        """
        self.color_grade = color_grade
        
        # Step 1: Organize and rename files
        if on_progress:
            on_progress("Organizing files", 0.1)
        self.clips = self._organize_clips(clips)
        
        # Step 2: Apply color grading
        if color_grade:
            if on_progress:
                on_progress("Color grading", 0.3)
            await self._apply_color_grade()
        
        # Step 3: Generate transitions
        if on_progress:
            on_progress("Creating transitions", 0.5)
        transition_clips = await self._create_transitions()
        
        # Step 4: Sync audio
        if on_progress:
            on_progress("Syncing audio", 0.7)
        await self._sync_audio()
        
        # Step 5: Assemble final video
        if on_progress:
            on_progress("Assembling video", 0.85)
        output_path = await self._assemble(title)
        
        # Step 6: Generate manifest
        if on_progress:
            on_progress("Generating manifest", 0.95)
        self._generate_manifest(title, output_path)
        
        # Cleanup
        if on_progress:
            on_progress("Complete", 1.0)
        
        return output_path
    
    def _organize_clips(
        self,
        clips: List[Dict[str, Any]]
    ) -> List[ProcessedClip]:
        """Organize and rename clips sequentially."""
        processed = []
        
        for i, clip_info in enumerate(clips):
            # Parse scene/shot numbers from IDs
            clip_id = clip_info.get("clip_id", f"clip_{i}")
            scene_num = clip_info.get("scene_number", 1)
            shot_num = clip_info.get("shot_number", i + 1)
            
            original_path = clip_info.get("path", "")
            
            # Create sequential filename
            new_name = f"scene{scene_num:02d}_shot{shot_num:02d}_{i:04d}.mp4"
            processed_path = self.temp_dir / new_name
            
            # Copy/move to temp directory with new name
            if Path(original_path).exists():
                shutil.copy(original_path, processed_path)
            
            processed_clip = ProcessedClip(
                clip_id=clip_id,
                original_path=original_path,
                processed_path=str(processed_path),
                start_time=clip_info.get("start_time", 0.0),
                end_time=clip_info.get("end_time", 0.0),
                duration=clip_info.get("duration", 0.0),
                sequence_number=i,
                scene_number=scene_num,
                shot_number=shot_num,
                transition_in=clip_info.get("transition_in"),
                transition_out=clip_info.get("transition_out"),
                audio_path=clip_info.get("audio_path"),
                metadata=clip_info.get("metadata", {})
            )
            processed.append(processed_clip)
        
        return processed
    
    async def _apply_color_grade(self):
        """Apply color grading to all clips."""
        if not self.color_grade:
            return
        
        filters = self.color_grade.to_ffmpeg_filters()
        
        for clip in self.clips:
            if not Path(clip.processed_path).exists():
                continue
            
            input_path = clip.processed_path
            output_path = str(Path(clip.processed_path).with_suffix(".graded.mp4"))
            
            # Build FFmpeg command
            cmd = [
                "ffmpeg", "-y",
                "-i", input_path,
                "-vf", filters,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
                output_path
            ]
            
            # Execute (in real implementation, use asyncio.subprocess)
            # For now, just update path
            clip.processed_path = output_path
    
    async def _create_transitions(self) -> List[str]:
        """Create transition effects between clips."""
        transition_paths = []
        
        for i in range(len(self.clips) - 1):
            current = self.clips[i]
            next_clip = self.clips[i + 1]
            
            # Determine transition type
            transition_type = current.transition_out or next_clip.transition_in or "cut"
            
            if transition_type == "cut":
                continue  # No transition needed
            
            transition = TransitionSpec(
                type=transition_type,
                duration=current.transition_duration
            )
            
            # Store transition info for assembly
            transition_paths.append({
                "from_clip": current.clip_id,
                "to_clip": next_clip.clip_id,
                "transition": transition
            })
        
        return transition_paths
    
    async def _sync_audio(self):
        """Sync audio tracks with video clips."""
        for clip in self.clips:
            if clip.audio_path and Path(clip.audio_path).exists():
                # Mark as having audio to sync
                clip.audio_synced = True
    
    async def _assemble(self, title: str) -> str:
        """Assemble all clips into final video."""
        output_path = self.output_dir / f"{title}_final.mp4"
        
        # Create concat file for FFmpeg
        concat_file = self.temp_dir / "concat.txt"
        
        with open(concat_file, "w") as f:
            for clip in self.clips:
                if Path(clip.processed_path).exists():
                    # Escape path for FFmpeg
                    escaped_path = clip.processed_path.replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
        
        # In real implementation, run FFmpeg concat
        # For now, create placeholder
        output_path.touch()
        
        return str(output_path)
    
    def _generate_manifest(self, title: str, output_path: str):
        """Generate production manifest."""
        self.manifest = ProductionManifest(
            production_id=f"prod_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=title,
            created_at=datetime.now().isoformat(),
            output_path=output_path,
            total_duration=sum(c.duration for c in self.clips)
        )
        
        # Add clip info
        for clip in self.clips:
            self.manifest.clips.append({
                "clip_id": clip.clip_id,
                "original_path": clip.original_path,
                "processed_path": clip.processed_path,
                "sequence_number": clip.sequence_number,
                "scene_number": clip.scene_number,
                "shot_number": clip.shot_number,
                "duration": clip.duration
            })
        
        # Add color grade if used
        if self.color_grade:
            self.manifest.color_grade = {
                "brightness": self.color_grade.brightness,
                "contrast": self.color_grade.contrast,
                "saturation": self.color_grade.saturation,
                "temperature": self.color_grade.temperature
            }
        
        # Save manifest
        manifest_path = self.output_dir / f"{title}_manifest.json"
        self.manifest.save(manifest_path)


# ============ Pre-built Color Grade Presets ============

COLOR_GRADE_PRESETS: Dict[str, ColorGradeSettings] = {
    "neutral": ColorGradeSettings(),
    
    "cinematic": ColorGradeSettings(
        contrast=1.1,
        saturation=0.9,
        temperature=0.1,
        shadows=-0.05,
        highlights=0.05,
        vignette=0.2
    ),
    
    "warm_film": ColorGradeSettings(
        contrast=1.05,
        saturation=1.1,
        temperature=0.3,
        film_grain=0.15,
        vignette=0.15
    ),
    
    "cool_modern": ColorGradeSettings(
        contrast=1.15,
        saturation=0.85,
        temperature=-0.2,
        highlights=0.1
    ),
    
    "vintage": ColorGradeSettings(
        contrast=0.95,
        saturation=0.7,
        temperature=0.2,
        shadows=0.1,
        film_grain=0.25,
        vignette=0.3
    ),
    
    "noir": ColorGradeSettings(
        contrast=1.3,
        saturation=0.0,  # Black and white
        shadows=-0.1,
        highlights=0.1,
        vignette=0.4
    ),
    
    "teal_orange": ColorGradeSettings(
        contrast=1.1,
        saturation=1.15,
        temperature=0.1,
        tint=-0.05
    ),
    
    "documentary": ColorGradeSettings(
        contrast=1.05,
        saturation=0.95,
        film_grain=0.1
    ),
    
    "dreamy": ColorGradeSettings(
        contrast=0.9,
        saturation=0.8,
        brightness=0.05,
        highlights=0.1,
        vignette=0.1
    ),
    
    "high_contrast": ColorGradeSettings(
        contrast=1.4,
        saturation=1.1,
        shadows=-0.1,
        highlights=0.15
    )
}


def get_color_grade(preset: str) -> ColorGradeSettings:
    """Get a color grade preset."""
    return COLOR_GRADE_PRESETS.get(preset, ColorGradeSettings())


# ============ EDL Export ============

def export_edl(
    clips: List[ProcessedClip],
    title: str = "production",
    frame_rate: int = 24
) -> str:
    """
    Export Edit Decision List (EDL) for use in professional editors.
    """
    lines = [
        "TITLE: " + title,
        f"FCM: NON-DROP FRAME",
        ""
    ]
    
    def frames_to_tc(frames: int) -> str:
        """Convert frame count to timecode."""
        h = frames // (frame_rate * 3600)
        m = (frames % (frame_rate * 3600)) // (frame_rate * 60)
        s = (frames % (frame_rate * 60)) // frame_rate
        f = frames % frame_rate
        return f"{h:02d}:{m:02d}:{s:02d}:{f:02d}"
    
    record_in = 0
    
    for i, clip in enumerate(clips, 1):
        duration_frames = int(clip.duration * frame_rate)
        record_out = record_in + duration_frames
        
        lines.append(
            f"{i:03d}  "
            f"AX       "
            f"V     "
            f"C        "
            f"{frames_to_tc(0)} "
            f"{frames_to_tc(duration_frames)} "
            f"{frames_to_tc(record_in)} "
            f"{frames_to_tc(record_out)}"
        )
        lines.append(f"* FROM CLIP NAME: {clip.get_sequential_name()}")
        lines.append("")
        
        record_in = record_out
    
    return "\n".join(lines)


# ============ FFmpeg Command Builder ============

class FFmpegCommandBuilder:
    """Builder for complex FFmpeg commands."""
    
    def __init__(self):
        self.inputs: List[str] = []
        self.filters: List[str] = []
        self.output_options: List[str] = []
    
    def add_input(self, path: str) -> "FFmpegCommandBuilder":
        self.inputs.append(f'-i "{path}"')
        return self
    
    def add_filter(self, filter_str: str) -> "FFmpegCommandBuilder":
        self.filters.append(filter_str)
        return self
    
    def set_codec(self, codec: str = "libx264") -> "FFmpegCommandBuilder":
        self.output_options.append(f"-c:v {codec}")
        return self
    
    def set_quality(self, crf: int = 18) -> "FFmpegCommandBuilder":
        self.output_options.append(f"-crf {crf}")
        return self
    
    def set_framerate(self, fps: int = 24) -> "FFmpegCommandBuilder":
        self.output_options.append(f"-r {fps}")
        return self
    
    def set_resolution(self, resolution: str = "1920x1080") -> "FFmpegCommandBuilder":
        self.output_options.append(f"-s {resolution}")
        return self
    
    def build(self, output_path: str) -> str:
        """Build the complete FFmpeg command."""
        cmd_parts = ["ffmpeg", "-y"]
        cmd_parts.extend(self.inputs)
        
        if self.filters:
            cmd_parts.append("-filter_complex")
            cmd_parts.append(f'"{";".join(self.filters)}"')
        
        cmd_parts.extend(self.output_options)
        cmd_parts.append(f'"{output_path}"')
        
        return " ".join(cmd_parts)


# ============ Convenience Functions ============

async def quick_post_process(
    clips: List[Dict[str, Any]],
    output_dir: str,
    title: str = "production",
    color_preset: str = "cinematic"
) -> str:
    """Quick post-processing with preset."""
    processor = PostProcessor(Path(output_dir))
    color_grade = get_color_grade(color_preset)
    
    return await processor.process(
        clips=clips,
        title=title,
        color_grade=color_grade
    )
