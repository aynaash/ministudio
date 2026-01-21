"""
Utility functions for Ministudio.
Includes video merging and post-processing tools.
"""

from pathlib import Path
from typing import List, Optional
import logging

import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np

import logging
import json
import os
import re
import asyncio
from typing import List, Optional, Any, Dict, Tuple
from pathlib import Path
from google.oauth2 import service_account

logger = logging.getLogger(__name__)


def load_gcp_credentials() -> Tuple[Optional[service_account.Credentials], Optional[str]]:
    """
    Load GCP credentials from environment variables with high resilience to escaping issues.
    """
    sa_key = (
        os.getenv("GCP_SERVICE_ACCOUNT_JSON")
        or os.getenv("GCP_SA_KEY")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )

    if not sa_key:
        logger.warning(
            "No GCP credential source found in environment variables")
        return None, None

    sa_info: Optional[Dict[str, Any]] = None

    # Strategy 1: Standard JSON parsing
    if not sa_info:
        try:
            sa_info = json.loads(sa_key)
            logger.info(
                "Successfully parsed GCP key using standard JSON parsing")
        except json.JSONDecodeError as e:
            logger.debug(f"Standard JSON parsing failed: {e}")

    # Strategy 2: ast.literal_eval fallback
    if not sa_info:
        try:
            import ast
            sa_info = ast.literal_eval(sa_key)
            if isinstance(sa_info, dict):
                logger.info(
                    "Successfully parsed GCP key using ast.literal_eval")
        except Exception as e:
            logger.debug(f"ast.literal_eval strategy failed: {e}")

    # Strategy 3: Handle escaped quotes
    if not sa_info:
        try:
            fixed = sa_key.strip()
            if (fixed.startswith('"') and fixed.endswith('"')) or \
               (fixed.startswith("'") and fixed.endswith("'")):
                fixed = fixed[1:-1]
            fixed = fixed.replace('\\"', '"').replace("\\'", "'")
            try:
                sa_info = json.loads(fixed)
            except json.JSONDecodeError:
                import ast
                sa_info = ast.literal_eval(fixed)
        except Exception as e:
            logger.debug(f"Escape/quote fixing strategy failed: {e}")

    # Strategy 4: Regex extraction
    if not sa_info:
        try:
            project_id_match = re.search(
                r'["\']project_id["\']:\s*["\']([^"\']+)["\']', sa_key)
            private_key_match = re.search(
                r'["\']private_key["\']:\s*["\'](-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----\\n?)["\']', sa_key, re.DOTALL)
            client_email_match = re.search(
                r'["\']client_email["\']:\s*["\']([^"\']+)["\']', sa_key)
            if project_id_match and private_key_match and client_email_match:
                private_key = private_key_match.group(1).replace("\\n", "\n")
                sa_info = {
                    "type": "service_account",
                    "project_id": project_id_match.group(1),
                    "private_key": private_key,
                    "client_email": client_email_match.group(1),
                }
        except Exception as e:
            logger.debug(f"Regex extraction failed: {e}")

    # Final check and credential creation
    if sa_info and isinstance(sa_info, dict):
        try:
            credentials = service_account.Credentials.from_service_account_info(
                sa_info, scopes=[
                    "https://www.googleapis.com/auth/cloud-platform"]
            )
            project_id = sa_info.get(
                "project_id") or sa_info.get("quota_project_id")
            return credentials, project_id
        except Exception as e:
            logger.error(
                f"Failed to create credentials from service account info: {e}")

    # Strategy 5: Application Default Credentials
    try:
        import google.auth
        # Check if GOOGLE_APPLICATION_CREDENTIALS is JSON content
        adc_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if adc_path and adc_path.strip().startswith("{"):
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as f:
                f.write(adc_path)
                temp_creds_path = f.name
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_path
            logger.info(
                f"Wrote JSON credentials to temp file: {temp_creds_path}")

        credentials, project_id = google.auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return credentials, project_id
    except Exception as e:
        logger.debug(f"ADC fallback failed: {e}")

    return None, None


def create_text_overlay(text: str, width: int, height: int, fontsize: int = 24) -> np.ndarray:
    """
    Creates an overlay image with text using Pillow (no ImageMagick required).
    Returns a numpy array suitable for MoviePy.
    """
    # Create a transparent RGBA image
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a semi-transparent black background box at the bottom
    padding = 10
    box_height = 80
    box_y = height - box_height - padding
    draw.rectangle([padding, box_y, width - padding,
                   height - padding], fill=(0, 0, 0, 180))

    # Try to load a clean font
    try:
        # Common Windows font paths
        font_path = "C:\\Windows\\Fonts\\arial.ttf"
        font = ImageFont.truetype(font_path, fontsize)
    except:
        try:
            # Fallback for other systems
            font = ImageFont.truetype("DejaVuSans", fontsize)
        except:
            font = ImageFont.load_default()

    # Word wrap logic
    words = text.split()
    lines = []
    current_line = []
    max_w = width - (padding * 4)

    for word in words:
        current_line.append(word)
        test_line = " ".join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        w = bbox[2] - bbox[0]
        if w > max_w:
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
    lines.append(" ".join(current_line))

    # Draw lines centered in the box
    total_text_height = sum(
        [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines])
    line_spacing = 5
    curr_y = box_y + (box_height - total_text_height) / 2

    for line in lines:
        lb = draw.textbbox((0, 0), line, font=font)
        lw = lb[2] - lb[0]
        draw.text(((width - lw) / 2, curr_y), line,
                  font=font, fill=(255, 255, 255, 255))
        curr_y += (lb[3] - lb[1]) + line_spacing

    # Return as numpy array for MoviePy (RGBA)
    return np.array(img)


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
        from moviepy import VideoFileClip, concatenate_videoclips

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


def merge_production(video_results: List['VideoGenerationResult'], output_path: Path, scripts: Optional[List[str]] = None) -> bool:
    """
    Merge multiple video files with audio tracks and optional text overlays.
    """
    if not video_results:
        logger.error("No video results provided for merging.")
        return False

    try:
        from moviepy import VideoFileClip, AudioFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip

        processed_clips = []
        for i, result in enumerate(video_results):
            if not result.video_path or not result.video_path.exists():
                logger.warning(
                    f"Video path missing for segment {i}: {result.video_path}")
                continue

            clip = VideoFileClip(str(result.video_path))

            # Sync duration with audio if available
            audio_duration = clip.duration
            if result.audio_path and result.audio_path.exists():
                audio = AudioFileClip(str(result.audio_path))
                audio_duration = min(audio.duration, clip.duration)
                clip = clip.with_audio(audio.subclipped(0, audio_duration))

            # Add Text Overlay (Pillow-based)
            if scripts and i < len(scripts) and scripts[i]:
                try:
                    overlay_img = create_text_overlay(
                        scripts[i], clip.w, clip.h)
                    txt_clip = ImageClip(overlay_img).with_duration(
                        audio_duration).with_position('center')
                    clip = CompositeVideoClip([clip, txt_clip])
                except Exception as txt_err:
                    logger.warning(
                        f"Could not add text overlay for segment {i}: {txt_err}")

            processed_clips.append(clip)

        if not processed_clips:
            return False

        final_clip = concatenate_videoclips(processed_clips, method="compose")

        final_clip.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )

        for clip in processed_clips:
            clip.close()
        final_clip.close()

        logger.info(f"Production merge complete: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error during production merge: {e}")
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
        from moviepy import VideoFileClip
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
