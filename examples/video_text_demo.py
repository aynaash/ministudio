"""
Video Text Demo
===============
Demonstrates the video text overlay system with test videos.

This example shows how to:
1. Add subtitles from SRT/VTT files
2. Auto-transcribe and add subtitles
3. Add custom text overlays (titles, lower thirds, watermarks)
4. Use different text styles
5. Work with test videos

Setup:
    pip install moviepy pillow
    
Optional (for transcription):
    pip install faster-whisper
"""

import os
from pathlib import Path

# Import ministudio text tools
from ministudio import (
    # Video Text Pipeline
    VideoTextPipeline,
    TextPipelineConfig,
    
    # Text Overlays
    TextOverlay,
    TextTrack,
    TextPosition,
    TextAnimation,
    TextOverlayStyle,
    TEXT_STYLES,
    get_text_style,
    
    # Video Tools
    get_video_info,
    
    # Convenience functions
    add_subtitles,
    auto_subtitle,
    add_title,
    add_watermark,
)


# ============ Basic Examples ============

def example_add_subtitles():
    """
    Add subtitles from an SRT file to a video.
    
    TODO: Provide your own video and subtitle files
    """
    print("\n=== Add Subtitles from File ===")
    
    # TODO: Replace with your test video path
    video_path = "test_videos/sample.mp4"
    subtitle_path = "test_videos/sample.srt"
    output_path = "output/video_with_subs.mp4"
    
    if not os.path.exists(video_path):
        print(f"TODO: Add test video at {video_path}")
        return
    
    if not os.path.exists(subtitle_path):
        print(f"TODO: Add subtitle file at {subtitle_path}")
        return
    
    # Simple one-liner
    result = add_subtitles(
        video_path,
        subtitle_path,
        output_path,
        style="youtube_subtitle"  # or "netflix_subtitle", "subtitle_box"
    )
    
    print(f"Created: {result}")


def example_auto_transcribe():
    """
    Automatically transcribe video and add subtitles.
    
    Requires: pip install faster-whisper (or openai-whisper)
    TODO: Provide your own video file
    """
    print("\n=== Auto Transcription ===")
    
    # TODO: Replace with your test video path
    video_path = "test_videos/speech_sample.mp4"
    output_path = "output/auto_subtitled.mp4"
    srt_path = "output/transcription.srt"
    
    if not os.path.exists(video_path):
        print(f"TODO: Add test video at {video_path}")
        return
    
    # Check if transcription is available
    from ministudio import is_transcription_available
    
    if not is_transcription_available():
        print("Transcription not available. Install with:")
        print("  pip install faster-whisper")
        return
    
    # Create pipeline with custom config
    config = TextPipelineConfig(
        transcription_model="base",  # tiny, base, small, medium, large
        transcription_language=None,  # Auto-detect
        default_style="youtube_subtitle"
    )
    
    pipeline = VideoTextPipeline(config)
    
    # Transcribe and add subtitles
    result = pipeline.auto_subtitle(
        video_path,
        output_path,
        save_srt=srt_path  # Also save SRT file
    )
    
    print(f"Created: {result}")
    print(f"Subtitles saved: {srt_path}")


def example_add_title():
    """
    Add a title card to the beginning of a video.
    
    TODO: Provide your own video file
    """
    print("\n=== Add Title ===")
    
    # TODO: Replace with your test video path
    video_path = "test_videos/sample.mp4"
    output_path = "output/with_title.mp4"
    
    if not os.path.exists(video_path):
        print(f"TODO: Add test video at {video_path}")
        return
    
    result = add_title(
        video_path,
        "Welcome to MiniStudio",
        output_path,
        duration=3.0  # Show for 3 seconds
    )
    
    print(f"Created: {result}")


def example_add_watermark():
    """
    Add a watermark to the entire video.
    
    TODO: Provide your own video file
    """
    print("\n=== Add Watermark ===")
    
    # TODO: Replace with your test video path
    video_path = "test_videos/sample.mp4"
    output_path = "output/watermarked.mp4"
    
    if not os.path.exists(video_path):
        print(f"TODO: Add test video at {video_path}")
        return
    
    result = add_watermark(
        video_path,
        "© MiniStudio 2026",
        output_path
    )
    
    print(f"Created: {result}")


# ============ Advanced Examples ============

def example_custom_overlays():
    """
    Add multiple custom text overlays with different styles.
    
    TODO: Provide your own video file
    """
    print("\n=== Custom Text Overlays ===")
    
    # TODO: Replace with your test video path
    video_path = "test_videos/sample.mp4"
    output_path = "output/custom_overlays.mp4"
    
    if not os.path.exists(video_path):
        print(f"TODO: Add test video at {video_path}")
        
        # Show example of how to create overlays
        print("\nExample overlay configuration:")
        
        overlays = [
            # Opening title (0-3 seconds)
            TextOverlay(
                text="Chapter 1: Introduction",
                start_time=0,
                end_time=3,
                position=TextPosition.CENTER,
                style=get_text_style("title"),
                animation_in=TextAnimation.FADE_IN,
                animation_out=TextAnimation.FADE_OUT
            ),
            
            # Lower third (5-10 seconds)
            TextOverlay(
                text="John Smith\nCEO, Tech Company",
                start_time=5,
                end_time=10,
                position=TextPosition.LOWER_THIRD,
                style=get_text_style("lower_third")
            ),
            
            # Subtitle (15-18 seconds)
            TextOverlay(
                text="This is a sample subtitle",
                start_time=15,
                end_time=18,
                position=TextPosition.BOTTOM_CENTER,
                style=get_text_style("youtube_subtitle")
            ),
        ]
        
        print("Overlays defined but video not found.")
        return
    
    # Create overlays
    overlays = [
        TextOverlay(
            text="Chapter 1",
            start_time=0,
            end_time=3,
            position=TextPosition.CENTER,
            style=get_text_style("title")
        ),
    ]
    
    pipeline = VideoTextPipeline()
    result = pipeline.add_text_overlays(video_path, overlays, output_path)
    
    print(f"Created: {result}")


def example_multiple_tracks():
    """
    Use multiple text tracks for complex overlays.
    
    TODO: Provide your own video file
    """
    print("\n=== Multiple Text Tracks ===")
    
    # TODO: Replace with your test video path
    video_path = "test_videos/sample.mp4"
    output_path = "output/multi_track.mp4"
    
    if not os.path.exists(video_path):
        print(f"TODO: Add test video at {video_path}")
        
        # Show example structure
        print("\nExample track structure:")
        
        # Track 1: Subtitles
        subtitle_track = TextTrack(name="Subtitles")
        subtitle_track.add_text("Hello world", 1.0, 3.0)
        subtitle_track.add_text("Welcome to the demo", 4.0, 6.0)
        
        # Track 2: Lower thirds
        lower_third_track = TextTrack(
            name="Lower Thirds",
            default_style=get_text_style("lower_third")
        )
        lower_third_track.add_text(
            "Speaker Name", 0, 5,
            position=TextPosition.LOWER_THIRD
        )
        
        # Track 3: Watermark (entire video)
        watermark_track = TextTrack(
            name="Watermark",
            default_style=get_text_style("watermark")
        )
        
        print("Tracks defined but video not found.")
        return
    
    pipeline = VideoTextPipeline()
    
    # Create tracks
    tracks = [
        TextTrack(name="Subtitles"),
        TextTrack(name="Lower Thirds"),
    ]
    
    tracks[0].add_text("First subtitle", 1.0, 4.0)
    tracks[1].add_text("Speaker Name", 0, 5, position=TextPosition.LOWER_THIRD)
    
    result = pipeline.add_tracks(video_path, tracks, output_path)
    print(f"Created: {result}")


def example_custom_style():
    """
    Create and use a custom text style.
    """
    print("\n=== Custom Text Style ===")
    
    from ministudio.text_overlay import TextOverlayStyle, Color
    
    # Create custom style
    custom_style = TextOverlayStyle(
        font_family="Arial",
        font_size=56,
        font_weight="bold",
        text_color=Color(255, 255, 0, 255),  # Yellow
        outline_color=Color(0, 0, 0, 255),  # Black outline
        outline_width=3,
        shadow=True,
        shadow_color=Color(0, 0, 0, 180),
        shadow_offset=(3, 3),
        shadow_blur=5,
        box_opacity=0.0,  # No background box
        text_align="center"
    )
    
    print("Custom style created:")
    print(f"  Font: {custom_style.font_family} {custom_style.font_size}px")
    print(f"  Color: {custom_style.text_color.to_hex()}")
    print(f"  Outline: {custom_style.outline_width}px")
    
    # Use it in an overlay
    overlay = TextOverlay(
        text="Custom Styled Text",
        start_time=0,
        end_time=5,
        style=custom_style
    )
    
    print(f"\nOverlay: '{overlay.text}' @ {overlay.start_time}-{overlay.end_time}s")


def example_ffmpeg_command():
    """
    Generate FFmpeg command for text overlay.
    
    Useful for debugging or running outside Python.
    """
    print("\n=== FFmpeg Command Generation ===")
    
    pipeline = VideoTextPipeline()
    
    overlays = [
        TextOverlay(
            text="Sample Text",
            start_time=0,
            end_time=5,
            position=TextPosition.BOTTOM_CENTER
        ),
        TextOverlay(
            text="Another Text",
            start_time=5,
            end_time=10,
            position=TextPosition.TOP_CENTER
        )
    ]
    
    cmd = pipeline.generate_ffmpeg_command(
        "input.mp4",
        overlays,
        "output.mp4"
    )
    
    print("Generated FFmpeg command:")
    print(cmd)


def example_list_styles():
    """
    List all available text styles.
    """
    print("\n=== Available Text Styles ===")
    
    for name, style in TEXT_STYLES.items():
        print(f"\n{name}:")
        print(f"  Font: {style.font_family} {style.font_size}px")
        print(f"  Outline: {style.outline_width}px")
        print(f"  Shadow: {style.shadow}")
        print(f"  Box opacity: {style.box_opacity}")


# ============ Test Video Management ============

def setup_test_directory():
    """
    Setup test directories and show expected structure.
    """
    print("\n=== Test Directory Setup ===")
    
    # Create directories
    Path("test_videos").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)
    
    print("Created directories:")
    print("  test_videos/  - Place your test videos here")
    print("  output/       - Output files will be saved here")
    
    print("\nExpected test files:")
    print("  test_videos/sample.mp4       - General purpose test video")
    print("  test_videos/speech_sample.mp4 - Video with speech for transcription")
    print("  test_videos/sample.srt       - Example subtitle file")
    
    # Create example SRT file
    example_srt = """1
00:00:01,000 --> 00:00:04,000
Hello and welcome to this demo.

2
00:00:05,000 --> 00:00:08,000
This is an example subtitle file.

3
00:00:09,000 --> 00:00:12,000
You can edit this to match your video.
"""
    
    srt_path = "test_videos/sample.srt"
    if not os.path.exists(srt_path):
        with open(srt_path, 'w') as f:
            f.write(example_srt)
        print(f"\nCreated example subtitle file: {srt_path}")


def list_test_videos():
    """
    List available test videos.
    """
    print("\n=== Test Videos ===")
    
    test_dir = Path("test_videos")
    if not test_dir.exists():
        print("Test directory not found. Run setup_test_directory() first.")
        return
    
    video_extensions = ['.mp4', '.mov', '.avi', '.webm', '.mkv']
    videos = []
    
    for ext in video_extensions:
        videos.extend(test_dir.glob(f"*{ext}"))
    
    if not videos:
        print("No test videos found. Add videos to test_videos/ folder.")
        return
    
    for video in videos:
        info = get_video_info(str(video))
        print(f"\n{video.name}:")
        print(f"  Resolution: {info.resolution}")
        print(f"  Duration: {info.duration:.1f}s")
        print(f"  FPS: {info.fps}")


# ============ Main Demo ============

def main():
    """
    Run all examples.
    """
    print("=" * 60)
    print("MiniStudio Video Text Demo")
    print("=" * 60)
    
    # Setup
    setup_test_directory()
    
    # List available videos
    list_test_videos()
    
    # List styles
    example_list_styles()
    
    # Custom style example
    example_custom_style()
    
    # FFmpeg command example
    example_ffmpeg_command()
    
    # These require actual video files:
    # example_add_subtitles()
    # example_auto_transcribe()
    # example_add_title()
    # example_add_watermark()
    # example_custom_overlays()
    # example_multiple_tracks()
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("\nTo test with real videos:")
    print("1. Add your video files to test_videos/")
    print("2. Uncomment the example functions in main()")
    print("3. Run this script again")
    print("=" * 60)


if __name__ == "__main__":
    main()
