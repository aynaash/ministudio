"""
Utility functions for Ministudio.
Includes video merging and post-processing tools.
"""

from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def merge_videos(video_paths: List[Path], output_path: Path) -> bool:
    """
    Merge multiple video files into one using MoviePy.
    """
    if not video_paths:
        logger.error("No video paths provided for merging.")
        return False

    if len(video_paths) == 1:
        try:
            import shutil
            shutil.copy2(video_paths[0], output_path)
            return True
        except Exception as e:
            logger.error(f"Error copying single video: {e}")
            return False

    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips

        logger.info(
            f"Merging {len(video_paths)} videos into {output_path} via MoviePy...")

        clips = [VideoFileClip(str(p)) for p in video_paths]
        final_clip = concatenate_videoclips(clips, method="compose")

        # Write the result
        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        # Close clips to release resources
        for clip in clips:
            clip.close()
        final_clip.close()

        logger.info(f"Successfully merged video saved to: {output_path}")
        return True

    except ImportError:
        logger.error("MoviePy not installed. Please run 'pip install moviepy'")
        return False
    except Exception as e:
        logger.error(f"Error during video merging: {e}")
        return False


def merge_videos_with_audio(video_results: List['VideoGenerationResult'], output_path: Path) -> bool:
    """
    Merge multiple video files and their corresponding audio tracks using MoviePy.
    """
    if not video_results:
        logger.error("No video results provided for merging.")
        return False

    try:
        from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

        clips = []
        for result in video_results:
            if not result.video_path:
                continue

            video_clip = VideoFileClip(str(result.video_path))

            # If there's a dialogue audio file, overlay it
            if result.audio_path and result.audio_path.exists():
                audio_clip = AudioFileClip(str(result.audio_path))
                # Ensure audio isn't longer than video (or vice versa, handle as needed)
                video_clip = video_clip.set_audio(audio_clip)

            clips.append(video_clip)

        if not clips:
            return False

        final_clip = concatenate_videoclips(clips, method="compose")

        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        for clip in clips:
            clip.close()
        final_clip.close()

        return True

    except Exception as e:
        logger.error(f"Error during AV merge: {e}")
        return False


def apply_frame_manipulation(frame_paths: List[str], manipulation_func):
    """
    Apply a frame-by-frame manipulation function using OpenCV/PIL.
    """
    try:
        import cv2
        import numpy as np

        for path in frame_paths:
            img = cv2.imread(path)
            if img is not None:
                new_img = manipulation_func(img)
                cv2.imwrite(path, new_img)
        return True
    except Exception as e:
        logger.error(f"Error during frame manipulation: {e}")
        return False


def extract_last_frames(video_path: Path, output_dir: Path, num_frames: int = 3) -> List[str]:
    """
    Extract the last N frames from a video file.
    Returns a list of paths to the extracted image files.
    """
    if not video_path.exists():
        logger.error(f"Video file not found: {video_path}")
        return []

    try:
        from moviepy.editor import VideoFileClip
        import os

        # Ensure output dir exists
        output_dir.mkdir(parents=True, exist_ok=True)

        clip = VideoFileClip(str(video_path))
        duration = clip.duration

        # Calculate timestamps for the last N frames (assuming 24fps)
        fps = clip.fps or 24
        frame_interval = 1.0 / fps

        frame_paths = []
        for i in range(num_frames):
            t = max(0, duration - (num_frames - 1 - i) * frame_interval)
            frame_filename = f"frame_{int(t*1000)}.jpg"
            frame_path = output_dir / frame_filename

            # Save frame as image
            clip.save_frame(str(frame_path), t=t)
            frame_paths.append(str(frame_path))

        clip.close()
        return frame_paths

    except ImportError:
        logger.error("MoviePy not installed.")
        return []
    except Exception as e:
        logger.error(f"Error extracting frames: {e}")
        return []
