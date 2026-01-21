# GitHub Showcase Guide: Code-as-Video 🎬

GitHub is perfect for showing off MiniStudio because you can present the **Script** and the **Result** side-by-side. Here is how to do it without making your repository too heavy.

## 📦 Keeping it Lightweight

Video files (MP4) can be large. To keep your repo lean and your README fast, follow these best practices:

### 1. The GIF Preview (Highly Recommended)
Convert your 10-second segments into high-quality GIFs. They auto-play on GitHub and are usually smaller.
- **Tip**: Use `ffmpeg` to compress.
- **Example**: `![Preview](outputs/previews/shot1.gif)`

### 2. GitHub Video Upload
GitHub now allows you to drag and drop MP4 files directly into issues, PRs, and READMEs. They host the video on their own CDN, so it doesn't bloat your `.git` folder.

### 3. Side-by-Side Comparison
Use a Markdown table to show the **Code** next to the **Video**. This proves that the video was generated from the script.

---

## 📝 Example README Structure

```markdown
### 🚀 Scene: The Quantum Mystery
This 8-second shot was generated using the **Identity Grounding 2.0** engine.

| The Python Script | The Generated Result |
| :--- | :--- |
| ```python
# Elias explains quantum waves
ShotConfig(
    action="Close-up of Elias's face...",
    dialogue="maya: Why does it choice?",
    continuity_required=True
)
``` | ![Elias Preview](path/to/shot_preview.gif) |

[View Full 4K Production](https://link-to-your-video.com)
```

---

## 🛠️ Performance Optimization for Previews

If you want to automate this, we can add a `utils.export_as_gif()` function to MiniStudio using `MoviePy`:

```python
def export_as_preview(mp4_path, gif_path):
    from moviepy import VideoFileClip
    clip = VideoFileClip(mp4_path).resized(width=480) # Shrink for web
    clip.write_gif(gif_path, fps=12) # Lower FPS for smaller size
```

## 🤖 AI Agent Ingestion
Don't forget to keep `llm.txt` in your root directory! When other developers or AI agents visit your repo, they can read `llm.txt` to instantly understand how to build videos with your library.

## 🌟 Best Repos to Reference
Check out projects like **Manim** (3Blue1Brown) for inspiration on how to document programmatic video generation.
