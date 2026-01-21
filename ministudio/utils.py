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
