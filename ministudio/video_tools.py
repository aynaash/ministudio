"""
Video Processing Tools
======================
Comprehensive video manipulation using best-in-class Python libraries.

Features:
- Video reading/writing with codec support
- Frame extraction and manipulation
- Audio extraction and merging
- Video concatenation and trimming
- Format conversion
- Thumbnail generation

Dependencies:
    pip install moviepy opencv-python numpy

Optional:
    pip install ffmpeg-python imageio[ffmpeg]
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, List, Any, Optional, Tuple, Union, Generator
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============ Video Information ============

@dataclass
class VideoInfo:
    """Video file metadata."""
    
    path: str
    width: int = 0
    height: int = 0
    fps: float = 30.0
    duration: float = 0.0
    frame_count: int = 0
    codec: str = ""
    audio_codec: str = ""
    has_audio: bool = False
    bitrate: int = 0
    file_size: int = 0
    format: str = ""
    
    @property
    def resolution(self) -> str:
        return f"{self.width}x{self.height}"
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 16/9
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "duration": self.duration,
            "frame_count": self.frame_count,
            "codec": self.codec,
            "has_audio": self.has_audio,
            "resolution": self.resolution
        }


class VideoReader:
    """
    Read video files and extract frames.
    
    Supports multiple backends: OpenCV, MoviePy, FFmpeg.
    """
    
    def __init__(self, video_path: str):
        self.video_path = video_path
        self._info: Optional[VideoInfo] = None
        self._cap = None  # OpenCV capture
        self._backend = self._detect_backend()
    
    def _detect_backend(self) -> str:
        """Detect available video backend."""
        try:
            import cv2
            return "opencv"
        except ImportError:
            pass
        
        try:
            from moviepy.editor import VideoFileClip
            return "moviepy"
        except ImportError:
            pass
        
        # Check for FFmpeg
        try:
            result = subprocess.run(['ffprobe', '-version'], 
                                    capture_output=True, check=True)
            return "ffmpeg"
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        raise ImportError(
            "No video backend available. Install one of: "
            "opencv-python, moviepy, or ffmpeg"
        )
    
    def get_info(self) -> VideoInfo:
        """Get video information."""
        if self._info:
            return self._info
        
        if self._backend == "opencv":
            self._info = self._get_info_opencv()
        elif self._backend == "moviepy":
            self._info = self._get_info_moviepy()
        else:
            self._info = self._get_info_ffprobe()
        
        return self._info
    
    def _get_info_opencv(self) -> VideoInfo:
        """Get info using OpenCV."""
        import cv2
        
        cap = cv2.VideoCapture(self.video_path)
        
        info = VideoInfo(
            path=self.video_path,
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            fps=cap.get(cv2.CAP_PROP_FPS),
            frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            codec=int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, 'little').decode('utf-8', errors='ignore'),
            file_size=os.path.getsize(self.video_path)
        )
        
        if info.fps > 0 and info.frame_count > 0:
            info.duration = info.frame_count / info.fps
        
        cap.release()
        return info
    
    def _get_info_moviepy(self) -> VideoInfo:
        """Get info using MoviePy."""
        from moviepy.editor import VideoFileClip
        
        clip = VideoFileClip(self.video_path)
        
        info = VideoInfo(
            path=self.video_path,
            width=clip.w,
            height=clip.h,
            fps=clip.fps,
            duration=clip.duration,
            frame_count=int(clip.fps * clip.duration) if clip.fps else 0,
            has_audio=clip.audio is not None,
            file_size=os.path.getsize(self.video_path)
        )
        
        clip.close()
        return info
    
    def _get_info_ffprobe(self) -> VideoInfo:
        """Get info using FFprobe."""
        cmd = [
            'ffprobe', '-v', 'quiet',
            '-print_format', 'json',
            '-show_format', '-show_streams',
            self.video_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        video_stream = None
        audio_stream = None
        
        for stream in data.get('streams', []):
            if stream['codec_type'] == 'video' and not video_stream:
                video_stream = stream
            elif stream['codec_type'] == 'audio' and not audio_stream:
                audio_stream = stream
        
        format_info = data.get('format', {})
        
        info = VideoInfo(
            path=self.video_path,
            width=video_stream.get('width', 0) if video_stream else 0,
            height=video_stream.get('height', 0) if video_stream else 0,
            fps=eval(video_stream.get('r_frame_rate', '30/1')) if video_stream else 30,
            duration=float(format_info.get('duration', 0)),
            codec=video_stream.get('codec_name', '') if video_stream else '',
            audio_codec=audio_stream.get('codec_name', '') if audio_stream else '',
            has_audio=audio_stream is not None,
            bitrate=int(format_info.get('bit_rate', 0)),
            file_size=int(format_info.get('size', 0)),
            format=format_info.get('format_name', '')
        )
        
        if info.fps and info.duration:
            info.frame_count = int(info.fps * info.duration)
        
        return info
    
    def read_frame(self, frame_number: int) -> Optional[Any]:
        """
        Read a specific frame.
        
        Returns:
            numpy array (BGR format for OpenCV)
        """
        if self._backend == "opencv":
            return self._read_frame_opencv(frame_number)
        elif self._backend == "moviepy":
            return self._read_frame_moviepy(frame_number)
        else:
            return self._read_frame_ffmpeg(frame_number)
    
    def _read_frame_opencv(self, frame_number: int) -> Optional[Any]:
        """Read frame using OpenCV."""
        import cv2
        
        if self._cap is None:
            self._cap = cv2.VideoCapture(self.video_path)
        
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self._cap.read()
        
        return frame if ret else None
    
    def _read_frame_moviepy(self, frame_number: int) -> Optional[Any]:
        """Read frame using MoviePy."""
        from moviepy.editor import VideoFileClip
        
        info = self.get_info()
        time = frame_number / info.fps if info.fps > 0 else 0
        
        clip = VideoFileClip(self.video_path)
        frame = clip.get_frame(time)
        clip.close()
        
        return frame
    
    def _read_frame_ffmpeg(self, frame_number: int) -> Optional[Any]:
        """Read frame using FFmpeg."""
        import numpy as np
        
        info = self.get_info()
        time = frame_number / info.fps if info.fps > 0 else 0
        
        cmd = [
            'ffmpeg', '-ss', str(time),
            '-i', self.video_path,
            '-vframes', '1',
            '-f', 'rawvideo',
            '-pix_fmt', 'rgb24',
            '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        
        if result.returncode != 0:
            return None
        
        frame = np.frombuffer(result.stdout, dtype=np.uint8)
        frame = frame.reshape((info.height, info.width, 3))
        
        return frame
    
    def read_frames(
        self,
        start: int = 0,
        end: Optional[int] = None,
        step: int = 1
    ) -> Generator[Tuple[int, Any], None, None]:
        """
        Read multiple frames.
        
        Yields:
            (frame_number, frame_data) tuples
        """
        info = self.get_info()
        end = end or info.frame_count
        
        for i in range(start, end, step):
            frame = self.read_frame(i)
            if frame is not None:
                yield (i, frame)
    
    def extract_frame_to_file(
        self,
        frame_number: int,
        output_path: str
    ) -> str:
        """Extract a frame and save to file."""
        frame = self.read_frame(frame_number)
        
        if frame is None:
            raise ValueError(f"Could not read frame {frame_number}")
        
        if self._backend == "opencv":
            import cv2
            cv2.imwrite(output_path, frame)
        else:
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(output_path)
        
        return output_path
    
    def close(self):
        """Release resources."""
        if self._cap is not None:
            self._cap.release()
            self._cap = None


# ============ Video Writer ============

@dataclass
class VideoWriterConfig:
    """Video writer configuration."""
    
    width: int = 1920
    height: int = 1080
    fps: float = 30.0
    codec: str = "libx264"  # h264
    pixel_format: str = "yuv420p"
    bitrate: str = "8M"
    quality: int = 23  # CRF for x264 (0-51, lower = better)
    preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"


class VideoWriter:
    """
    Write video files.
    
    Supports multiple backends for flexibility.
    """
    
    def __init__(
        self,
        output_path: str,
        config: Optional[VideoWriterConfig] = None
    ):
        self.output_path = output_path
        self.config = config or VideoWriterConfig()
        self._writer = None
        self._backend = self._detect_backend()
        self._frame_count = 0
    
    def _detect_backend(self) -> str:
        """Detect available backend."""
        try:
            import cv2
            return "opencv"
        except ImportError:
            pass
        
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return "ffmpeg"
        except:
            pass
        
        raise ImportError("No video writer backend available")
    
    def open(self):
        """Open writer for writing."""
        if self._backend == "opencv":
            self._open_opencv()
        else:
            self._open_ffmpeg()
    
    def _open_opencv(self):
        """Open OpenCV writer."""
        import cv2
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self._writer = cv2.VideoWriter(
            self.output_path,
            fourcc,
            self.config.fps,
            (self.config.width, self.config.height)
        )
    
    def _open_ffmpeg(self):
        """Open FFmpeg pipe writer."""
        cmd = [
            'ffmpeg', '-y',
            '-f', 'rawvideo',
            '-vcodec', 'rawvideo',
            '-s', f'{self.config.width}x{self.config.height}',
            '-pix_fmt', 'rgb24',
            '-r', str(self.config.fps),
            '-i', '-',
            '-c:v', self.config.codec,
            '-pix_fmt', self.config.pixel_format,
            '-crf', str(self.config.quality),
            '-preset', self.config.preset,
            self.output_path
        ]
        
        self._writer = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    
    def write_frame(self, frame: Any):
        """Write a single frame."""
        if self._writer is None:
            self.open()
        
        if self._backend == "opencv":
            self._writer.write(frame)
        else:
            self._writer.stdin.write(frame.tobytes())
        
        self._frame_count += 1
    
    def close(self):
        """Close and finalize video."""
        if self._writer is None:
            return
        
        if self._backend == "opencv":
            self._writer.release()
        else:
            self._writer.stdin.close()
            self._writer.wait()
        
        self._writer = None
    
    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ============ Video Operations ============

class VideoOperations:
    """
    Common video operations.
    
    TODO: Implement remaining operations with actual video processing
    """
    
    @staticmethod
    def get_info(video_path: str) -> VideoInfo:
        """Get video information."""
        reader = VideoReader(video_path)
        return reader.get_info()
    
    @staticmethod
    def extract_audio(
        video_path: str,
        output_path: str,
        format: str = "wav"
    ) -> str:
        """
        Extract audio from video.
        
        Args:
            video_path: Input video
            output_path: Output audio file
            format: Audio format (wav, mp3, aac)
        
        Returns:
            Path to extracted audio
        """
        try:
            from moviepy.editor import VideoFileClip
            
            video = VideoFileClip(video_path)
            if video.audio:
                video.audio.write_audiofile(output_path)
            video.close()
            
        except ImportError:
            # Fallback to FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le' if format == 'wav' else 'libmp3lame',
                output_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)
        
        return output_path
    
    @staticmethod
    def trim(
        video_path: str,
        output_path: str,
        start_time: float,
        end_time: Optional[float] = None,
        duration: Optional[float] = None
    ) -> str:
        """
        Trim video to specified range.
        
        Args:
            video_path: Input video
            output_path: Output video
            start_time: Start time in seconds
            end_time: End time in seconds (optional)
            duration: Duration in seconds (optional, alternative to end_time)
        
        Returns:
            Path to trimmed video
        """
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-ss', str(start_time),
        ]
        
        if duration is not None:
            cmd.extend(['-t', str(duration)])
        elif end_time is not None:
            cmd.extend(['-to', str(end_time)])
        
        cmd.extend([
            '-c', 'copy',  # Stream copy for speed
            output_path
        ])
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    @staticmethod
    def concatenate(
        video_paths: List[str],
        output_path: str,
        transition: Optional[str] = None,
        transition_duration: float = 0.5
    ) -> str:
        """
        Concatenate multiple videos.
        
        Args:
            video_paths: List of input video paths
            output_path: Output video path
            transition: Transition type (None, 'fade', 'dissolve')
            transition_duration: Transition duration in seconds
        
        Returns:
            Path to concatenated video
        """
        if not video_paths:
            raise ValueError("No videos to concatenate")
        
        if len(video_paths) == 1:
            import shutil
            shutil.copy(video_paths[0], output_path)
            return output_path
        
        # Create concat file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            for path in video_paths:
                # Escape special characters
                escaped = path.replace("'", "'\\''")
                f.write(f"file '{escaped}'\n")
            concat_file = f.name
        
        try:
            if transition == 'fade':
                # TODO: Implement fade transitions
                # Requires complex filtergraph
                pass
            
            # Simple concatenation
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-c', 'copy',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            
        finally:
            os.unlink(concat_file)
        
        return output_path
    
    @staticmethod
    def resize(
        video_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect: bool = True
    ) -> str:
        """
        Resize video.
        
        Args:
            video_path: Input video
            output_path: Output video
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio
        
        Returns:
            Path to resized video
        """
        if width is None and height is None:
            raise ValueError("Must specify width or height")
        
        # Build scale filter
        if maintain_aspect:
            if width and height:
                scale = f"scale={width}:{height}:force_original_aspect_ratio=decrease"
            elif width:
                scale = f"scale={width}:-2"
            else:
                scale = f"scale=-2:{height}"
        else:
            scale = f"scale={width or -2}:{height or -2}"
        
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-vf', scale,
            '-c:a', 'copy',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    @staticmethod
    def add_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
        replace: bool = True,
        mix: bool = False,
        audio_volume: float = 1.0
    ) -> str:
        """
        Add or replace audio in video.
        
        Args:
            video_path: Input video
            audio_path: Audio file to add
            output_path: Output video
            replace: Replace existing audio
            mix: Mix with existing audio
            audio_volume: Volume multiplier for new audio
        
        Returns:
            Path to output video
        """
        if replace:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-map', '0:v:0',
                '-map', '1:a:0',
                '-shortest',
                output_path
            ]
        elif mix:
            # TODO: Implement audio mixing
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-filter_complex',
                f'[0:a][1:a]amix=inputs=2:duration=first[aout]',
                '-map', '0:v',
                '-map', '[aout]',
                output_path
            ]
        else:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                output_path
            ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    @staticmethod
    def change_fps(
        video_path: str,
        output_path: str,
        target_fps: float
    ) -> str:
        """
        Change video frame rate.
        
        Args:
            video_path: Input video
            output_path: Output video
            target_fps: Target frame rate
        
        Returns:
            Path to output video
        """
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-filter:v', f'fps={target_fps}',
            '-c:a', 'copy',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    @staticmethod
    def extract_thumbnail(
        video_path: str,
        output_path: str,
        time: float = 0,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> str:
        """
        Extract thumbnail from video.
        
        Args:
            video_path: Input video
            output_path: Output image path
            time: Time to extract from (seconds)
            width: Thumbnail width
            height: Thumbnail height
        
        Returns:
            Path to thumbnail
        """
        cmd = [
            'ffmpeg', '-y',
            '-ss', str(time),
            '-i', video_path,
            '-vframes', '1',
        ]
        
        if width or height:
            scale = f"scale={width or -1}:{height or -1}"
            cmd.extend(['-vf', scale])
        
        cmd.append(output_path)
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    
    @staticmethod
    def convert_format(
        video_path: str,
        output_path: str,
        codec: str = "libx264",
        quality: int = 23
    ) -> str:
        """
        Convert video to different format/codec.
        
        Args:
            video_path: Input video
            output_path: Output video
            codec: Video codec
            quality: Quality (CRF for x264)
        
        Returns:
            Path to converted video
        """
        cmd = [
            'ffmpeg', '-y',
            '-i', video_path,
            '-c:v', codec,
            '-crf', str(quality),
            '-c:a', 'aac',
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path


# ============ Batch Processing ============

@dataclass
class BatchJob:
    """A batch processing job."""
    
    input_path: str
    output_path: str
    operation: str  # 'trim', 'resize', 'convert', etc.
    params: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    error: Optional[str] = None


class BatchProcessor:
    """
    Process multiple videos in batch.
    
    TODO: Add parallel processing support
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.jobs: List[BatchJob] = []
    
    def add_job(
        self,
        input_path: str,
        output_path: str,
        operation: str,
        **params
    ) -> BatchJob:
        """Add a job to the batch."""
        job = BatchJob(
            input_path=input_path,
            output_path=output_path,
            operation=operation,
            params=params
        )
        self.jobs.append(job)
        return job
    
    def process(self, progress_callback=None) -> List[BatchJob]:
        """
        Process all jobs.
        
        TODO: Implement parallel processing
        
        Args:
            progress_callback: Called with (completed, total) after each job
        
        Returns:
            List of completed jobs
        """
        operations = VideoOperations()
        
        for i, job in enumerate(self.jobs):
            try:
                job.status = "processing"
                
                # Get operation function
                op_func = getattr(operations, job.operation, None)
                if op_func is None:
                    raise ValueError(f"Unknown operation: {job.operation}")
                
                # Execute
                op_func(
                    job.input_path,
                    job.output_path,
                    **job.params
                )
                
                job.status = "completed"
                
            except Exception as e:
                job.status = "failed"
                job.error = str(e)
                logger.error(f"Batch job failed: {e}")
            
            if progress_callback:
                progress_callback(i + 1, len(self.jobs))
        
        return self.jobs


# ============ Convenience Functions ============

def get_video_info(video_path: str) -> VideoInfo:
    """Get video information."""
    return VideoOperations.get_info(video_path)


def trim_video(
    video_path: str,
    output_path: str,
    start: float,
    end: Optional[float] = None,
    duration: Optional[float] = None
) -> str:
    """Trim a video."""
    return VideoOperations.trim(video_path, output_path, start, end, duration)


def concatenate_videos(
    video_paths: List[str],
    output_path: str
) -> str:
    """Concatenate videos."""
    return VideoOperations.concatenate(video_paths, output_path)


def extract_audio(video_path: str, output_path: str) -> str:
    """Extract audio from video."""
    return VideoOperations.extract_audio(video_path, output_path)


def add_audio_to_video(
    video_path: str,
    audio_path: str,
    output_path: str
) -> str:
    """Add audio to video."""
    return VideoOperations.add_audio(video_path, audio_path, output_path)
