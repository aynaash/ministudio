"""
Video Text Integration
======================
Complete system for adding text, subtitles, and captions to videos
with automatic color analysis and contrast optimization.

This module integrates:
- text_overlay.py: Text styling and positioning
- video_tools.py: Video reading/writing
- transcription.py: Speech-to-text
- image_tools.py: Image/text rendering

Usage:
    from ministudio.video_text import VideoTextPipeline
    
    pipeline = VideoTextPipeline()
    
    # Add subtitles from file
    pipeline.add_subtitles("video.mp4", "subtitles.srt", "output.mp4")
    
    # Auto-transcribe and add
    pipeline.auto_subtitle("video.mp4", "output.mp4")
    
    # Add custom text overlays
    pipeline.add_text_overlays("video.mp4", overlays, "output.mp4")

Dependencies:
    pip install moviepy pillow numpy
    
Optional:
    pip install opencv-python faster-whisper
"""

import os
import json
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

# Import from our modules
from .text_overlay import (
    TextOverlay, TextTrack, TextPosition, TextAnimation,
    TextOverlayStyle, TEXT_STYLES, get_text_style,
    Color, COLORS, get_contrasting_color,
    VideoColorAnalyzer, SubtitleParser
)
from .video_tools import (
    VideoReader, VideoWriter, VideoWriterConfig, VideoOperations,
    VideoInfo, get_video_info
)

logger = logging.getLogger(__name__)


# ============ Video Text Pipeline ============

@dataclass
class TextPipelineConfig:
    """Configuration for video text pipeline."""
    
    # Default style
    default_style: str = "youtube_subtitle"
    
    # Auto-contrast settings
    auto_contrast: bool = True
    contrast_sample_frames: int = 5
    
    # Transcription settings
    transcription_model: str = "base"
    transcription_language: Optional[str] = None
    
    # Output settings
    output_codec: str = "libx264"
    output_quality: int = 23
    
    # Performance
    use_gpu: bool = True
    temp_dir: Optional[str] = None


class VideoTextPipeline:
    """
    Complete pipeline for adding text to videos.
    
    Supports:
    - Manual subtitle files (SRT, VTT)
    - Auto-transcription
    - Custom text overlays
    - Adaptive color contrast
    - Multiple text tracks
    """
    
    def __init__(self, config: Optional[TextPipelineConfig] = None):
        self.config = config or TextPipelineConfig()
        self.color_analyzer = VideoColorAnalyzer()
        self._transcriber = None
    
    # ========== Subtitle Methods ==========
    
    def add_subtitles(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str,
        style: Optional[str] = None,
        auto_contrast: Optional[bool] = None
    ) -> str:
        """
        Add subtitles from file to video.
        
        Args:
            video_path: Input video
            subtitle_path: SRT or VTT file
            output_path: Output video
            style: Style preset name
            auto_contrast: Override auto-contrast setting
        
        Returns:
            Path to output video
        """
        # Load subtitles
        entries = SubtitleParser.load(subtitle_path)
        
        # Convert to overlays
        style_obj = get_text_style(style or self.config.default_style)
        overlays = [entry.to_overlay(style_obj) for entry in entries]
        
        # Create track
        track = TextTrack(name="Subtitles", overlays=overlays)
        
        return self._render_text_to_video(
            video_path, [track], output_path,
            auto_contrast if auto_contrast is not None else self.config.auto_contrast
        )
    
    def auto_subtitle(
        self,
        video_path: str,
        output_path: str,
        style: Optional[str] = None,
        language: Optional[str] = None,
        save_srt: Optional[str] = None
    ) -> str:
        """
        Auto-transcribe video and add subtitles.
        
        Args:
            video_path: Input video
            output_path: Output video
            style: Style preset
            language: Language code (auto-detect if None)
            save_srt: Optional path to save SRT file
        
        Returns:
            Path to output video
        """
        try:
            from .transcription import Transcriber, TranscriptionConfig, SubtitleGenerator
        except ImportError:
            raise ImportError(
                "Transcription requires whisper. Install with:\n"
                "  pip install openai-whisper\n"
                "or:\n"
                "  pip install faster-whisper"
            )
        
        # Transcribe
        config = TranscriptionConfig(
            model=self.config.transcription_model,
            language=language or self.config.transcription_language,
            word_timestamps=True
        )
        
        transcriber = Transcriber(config)
        
        logger.info(f"Transcribing {video_path}...")
        transcription = transcriber.transcribe(video_path)
        logger.info(f"Transcribed {len(transcription.segments)} segments")
        
        # Save SRT if requested
        if save_srt:
            SubtitleGenerator.save_srt(transcription, save_srt)
            logger.info(f"Saved subtitles to {save_srt}")
        
        # Convert to overlays
        style_obj = get_text_style(style or self.config.default_style)
        overlays = []
        
        for segment in transcription.segments:
            overlays.append(TextOverlay(
                text=segment.text,
                start_time=segment.start,
                end_time=segment.end,
                style=style_obj
            ))
        
        # Create track and render
        track = TextTrack(name="Auto Subtitles", overlays=overlays)
        
        return self._render_text_to_video(
            video_path, [track], output_path,
            self.config.auto_contrast
        )
    
    # ========== Custom Text Methods ==========
    
    def add_text_overlays(
        self,
        video_path: str,
        overlays: List[TextOverlay],
        output_path: str,
        auto_contrast: bool = True
    ) -> str:
        """
        Add custom text overlays to video.
        
        Args:
            video_path: Input video
            overlays: List of TextOverlay objects
            output_path: Output video
            auto_contrast: Adjust colors for contrast
        
        Returns:
            Path to output video
        """
        track = TextTrack(name="Custom", overlays=overlays)
        return self._render_text_to_video(video_path, [track], output_path, auto_contrast)
    
    def add_title(
        self,
        video_path: str,
        title: str,
        output_path: str,
        duration: float = 3.0,
        start_time: float = 0,
        style: str = "title"
    ) -> str:
        """
        Add a title card to video.
        
        Args:
            video_path: Input video
            title: Title text
            output_path: Output video
            duration: How long to show title
            start_time: When to show title
            style: Style preset
        
        Returns:
            Path to output video
        """
        overlay = TextOverlay(
            text=title,
            start_time=start_time,
            end_time=start_time + duration,
            position=TextPosition.CENTER,
            style=get_text_style(style),
            animation_in=TextAnimation.FADE_IN,
            animation_out=TextAnimation.FADE_OUT
        )
        
        return self.add_text_overlays(video_path, [overlay], output_path)
    
    def add_lower_third(
        self,
        video_path: str,
        name: str,
        title: str,
        output_path: str,
        start_time: float = 0,
        duration: float = 5.0
    ) -> str:
        """
        Add lower third (name card) to video.
        
        Args:
            video_path: Input video
            name: Person's name
            title: Person's title/role
            output_path: Output video
            start_time: When to show
            duration: How long to show
        
        Returns:
            Path to output video
        """
        from .text_overlay import LowerThird
        
        lower_third = LowerThird(
            name=name,
            title=title,
            start_time=start_time,
            end_time=start_time + duration
        )
        
        return self.add_text_overlays(
            video_path,
            lower_third.to_overlays(),
            output_path
        )
    
    def add_watermark(
        self,
        video_path: str,
        text: str,
        output_path: str,
        position: TextPosition = TextPosition.BOTTOM_RIGHT
    ) -> str:
        """
        Add watermark to entire video.
        
        Args:
            video_path: Input video
            text: Watermark text
            output_path: Output video
            position: Watermark position
        
        Returns:
            Path to output video
        """
        info = get_video_info(video_path)
        
        overlay = TextOverlay(
            text=text,
            start_time=0,
            end_time=info.duration,
            position=position,
            style=get_text_style("watermark")
        )
        
        return self.add_text_overlays(video_path, [overlay], output_path, auto_contrast=False)
    
    # ========== Multi-Track Methods ==========
    
    def add_tracks(
        self,
        video_path: str,
        tracks: List[TextTrack],
        output_path: str,
        auto_contrast: bool = True
    ) -> str:
        """
        Add multiple text tracks to video.
        
        Args:
            video_path: Input video
            tracks: List of TextTrack objects
            output_path: Output video
            auto_contrast: Adjust colors for contrast
        
        Returns:
            Path to output video
        """
        return self._render_text_to_video(video_path, tracks, output_path, auto_contrast)
    
    # ========== Rendering ==========
    
    def _render_text_to_video(
        self,
        video_path: str,
        tracks: List[TextTrack],
        output_path: str,
        auto_contrast: bool = True
    ) -> str:
        """
        Core rendering method.
        
        TODO: Implement full rendering with MoviePy/OpenCV
        Currently generates FFmpeg command.
        """
        # Collect all overlays
        all_overlays = []
        for track in tracks:
            if track.enabled:
                all_overlays.extend(track.overlays)
        
        if not all_overlays:
            # No text - just copy
            import shutil
            shutil.copy(video_path, output_path)
            return output_path
        
        # Try MoviePy first
        try:
            return self._render_with_moviepy(video_path, all_overlays, output_path, auto_contrast)
        except ImportError:
            logger.warning("MoviePy not available, falling back to FFmpeg")
        
        # Fallback to FFmpeg
        return self._render_with_ffmpeg(video_path, all_overlays, output_path)
    
    def _render_with_moviepy(
        self,
        video_path: str,
        overlays: List[TextOverlay],
        output_path: str,
        auto_contrast: bool
    ) -> str:
        """Render using MoviePy."""
        from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
        
        video = VideoFileClip(video_path)
        
        text_clips = []
        
        for overlay in overlays:
            # Get style
            style = overlay.style
            
            # TODO: Implement auto_contrast color adjustment
            
            # Create TextClip
            try:
                txt = TextClip(
                    overlay.text,
                    fontsize=style.font_size,
                    color='white',
                    stroke_color='black' if style.outline_color else None,
                    stroke_width=style.outline_width,
                    font=style.font_family,
                    method='caption',
                    size=(int(video.w * 0.9), None)
                )
            except Exception as e:
                logger.warning(f"TextClip creation failed: {e}, using label method")
                txt = TextClip(
                    overlay.text,
                    fontsize=style.font_size,
                    color='white',
                    method='label'
                )
            
            # Set timing
            txt = txt.set_start(overlay.start_time)
            txt = txt.set_duration(overlay.duration)
            
            # Set position
            pos = self._get_moviepy_position(overlay, video.w, video.h)
            txt = txt.set_position(pos)
            
            text_clips.append(txt)
        
        # Composite
        final = CompositeVideoClip([video] + text_clips)
        
        # Write
        final.write_videofile(
            output_path,
            codec=self.config.output_codec,
            audio_codec='aac',
            temp_audiofile=os.path.join(
                self.config.temp_dir or tempfile.gettempdir(),
                'temp_audio.m4a'
            ),
            remove_temp=True
        )
        
        video.close()
        final.close()
        
        return output_path
    
    def _get_moviepy_position(
        self,
        overlay: TextOverlay,
        width: int,
        height: int
    ) -> Union[str, Tuple]:
        """Get MoviePy position from TextPosition."""
        pos_map = {
            TextPosition.TOP_LEFT: ('left', 'top'),
            TextPosition.TOP_CENTER: ('center', 'top'),
            TextPosition.TOP_RIGHT: ('right', 'top'),
            TextPosition.CENTER_LEFT: ('left', 'center'),
            TextPosition.CENTER: ('center', 'center'),
            TextPosition.CENTER_RIGHT: ('right', 'center'),
            TextPosition.BOTTOM_LEFT: ('left', 'bottom'),
            TextPosition.BOTTOM_CENTER: ('center', 'bottom'),
            TextPosition.BOTTOM_RIGHT: ('right', 'bottom'),
            TextPosition.LOWER_THIRD: (50, height - 150),
        }
        
        if overlay.position == TextPosition.CUSTOM and overlay.x is not None:
            return (overlay.x, overlay.y or 0)
        
        return pos_map.get(overlay.position, ('center', 'bottom'))
    
    def _render_with_ffmpeg(
        self,
        video_path: str,
        overlays: List[TextOverlay],
        output_path: str
    ) -> str:
        """Render using FFmpeg drawtext filter."""
        import subprocess
        
        # Build filter chain
        filters = []
        
        for overlay in overlays:
            # Escape text
            text = overlay.text.replace("'", "'\\''").replace(":", "\\:")
            
            # Position
            x, y = self._get_ffmpeg_position(overlay)
            
            # Build filter
            parts = [
                f"text='{text}'",
                f"fontsize={overlay.style.font_size}",
                "fontcolor=white",
                f"x={x}",
                f"y={y}",
                f"enable='between(t,{overlay.start_time},{overlay.end_time})'"
            ]
            
            if overlay.style.outline_width > 0:
                parts.append(f"borderw={overlay.style.outline_width}")
                parts.append("bordercolor=black")
            
            if overlay.style.shadow:
                parts.append("shadowcolor=black@0.5")
                parts.append("shadowx=2")
                parts.append("shadowy=2")
            
            filters.append(f"drawtext={':'.join(parts)}")
        
        filter_chain = ','.join(filters)
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', filter_chain,
            '-c:a', 'copy',
            output_path
        ]
        
        logger.info(f"Running FFmpeg: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        return output_path
    
    def _get_ffmpeg_position(self, overlay: TextOverlay) -> Tuple[str, str]:
        """Get FFmpeg position expressions."""
        pos_map = {
            TextPosition.TOP_LEFT: ("10", "10"),
            TextPosition.TOP_CENTER: ("(w-text_w)/2", "10"),
            TextPosition.TOP_RIGHT: ("w-text_w-10", "10"),
            TextPosition.CENTER_LEFT: ("10", "(h-text_h)/2"),
            TextPosition.CENTER: ("(w-text_w)/2", "(h-text_h)/2"),
            TextPosition.CENTER_RIGHT: ("w-text_w-10", "(h-text_h)/2"),
            TextPosition.BOTTOM_LEFT: ("10", "h-text_h-50"),
            TextPosition.BOTTOM_CENTER: ("(w-text_w)/2", "h-text_h-50"),
            TextPosition.BOTTOM_RIGHT: ("w-text_w-10", "h-text_h-50"),
            TextPosition.LOWER_THIRD: ("50", "h-150"),
        }
        
        if overlay.position == TextPosition.CUSTOM and overlay.x is not None:
            return (str(overlay.x), str(overlay.y or 0))
        
        return pos_map.get(overlay.position, ("(w-text_w)/2", "h-text_h-50"))
    
    # ========== Utility Methods ==========
    
    def generate_ffmpeg_command(
        self,
        video_path: str,
        overlays: List[TextOverlay],
        output_path: str
    ) -> str:
        """
        Generate FFmpeg command for text overlay.
        
        Useful for debugging or manual execution.
        """
        filters = []
        
        for overlay in overlays:
            text = overlay.text.replace("'", "'\\''").replace(":", "\\:")
            x, y = self._get_ffmpeg_position(overlay)
            
            parts = [
                f"text='{text}'",
                f"fontsize={overlay.style.font_size}",
                "fontcolor=white",
                f"x={x}",
                f"y={y}",
                f"enable='between(t,{overlay.start_time},{overlay.end_time})'"
            ]
            
            filters.append(f"drawtext={':'.join(parts)}")
        
        filter_chain = ','.join(filters) if filters else 'null'
        
        return f'ffmpeg -i "{video_path}" -vf "{filter_chain}" -c:a copy "{output_path}"'
    
    def analyze_video_for_text(
        self,
        video_path: str,
        position: TextPosition = TextPosition.BOTTOM_CENTER
    ) -> Dict[str, Any]:
        """
        Analyze video to determine optimal text colors.
        
        Args:
            video_path: Video to analyze
            position: Text position to analyze
        
        Returns:
            Analysis results with suggested colors
        """
        return self.color_analyzer.analyze_video_region(
            video_path, position, 0, None, self.config.contrast_sample_frames
        )


# ============ Convenience Functions ============

def add_subtitles(
    video_path: str,
    subtitle_path: str,
    output_path: str,
    style: str = "youtube_subtitle"
) -> str:
    """Add subtitles to video."""
    pipeline = VideoTextPipeline()
    return pipeline.add_subtitles(video_path, subtitle_path, output_path, style)


def auto_subtitle(
    video_path: str,
    output_path: str,
    language: Optional[str] = None
) -> str:
    """Auto-transcribe and add subtitles."""
    pipeline = VideoTextPipeline()
    return pipeline.auto_subtitle(video_path, output_path, language=language)


def add_title(
    video_path: str,
    title: str,
    output_path: str,
    duration: float = 3.0
) -> str:
    """Add title to video."""
    pipeline = VideoTextPipeline()
    return pipeline.add_title(video_path, title, output_path, duration)


def add_watermark(
    video_path: str,
    text: str,
    output_path: str
) -> str:
    """Add watermark to video."""
    pipeline = VideoTextPipeline()
    return pipeline.add_watermark(video_path, text, output_path)


# ============ Test Video Support ============

class TestVideoManager:
    """
    Manage test videos for pipeline development.
    
    TODO: User will provide test videos
    """
    
    def __init__(self, test_dir: str = "test_videos"):
        self.test_dir = Path(test_dir)
        self.test_dir.mkdir(exist_ok=True)
    
    def list_videos(self) -> List[str]:
        """List available test videos."""
        extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
        videos = []
        
        for ext in extensions:
            videos.extend(self.test_dir.glob(f"*{ext}"))
        
        return [str(v) for v in videos]
    
    def get_video(self, name: str) -> Optional[str]:
        """Get path to test video by name."""
        for video in self.list_videos():
            if name in video:
                return video
        return None
    
    def video_info(self, name: str) -> Optional[VideoInfo]:
        """Get info for test video."""
        path = self.get_video(name)
        if path:
            return get_video_info(path)
        return None
