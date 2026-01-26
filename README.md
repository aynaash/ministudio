# MiniStudio: The Cinematic AI Engine

[![Version](https://img.shields.io/badge/version-0.2.2-blue.svg)](https://github.com/ministudio/ministudio)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)

**Programmable, Stateful, and Model-Agnostic Orchestration for High-Fidelity Video Production.**

MiniStudio transforms the chaotic world of generative AI into a structured filmmaking pipeline. It solves the "Consistency Problem" by treating video like code—enforcing character identity, environment stability, and temporal continuity through a state-machine driven architecture.

---

## ✨ What's New in v0.2.2

- 🎬 **Google Veo Provider** - Native integration with Veo 1 & Veo 2
- 🤗 **HuggingFace Provider** - 10+ open-source models (Zeroscope, SVD, AnimateDiff, CogVideoX)
- 📝 **Text Overlay System** - Intelligent subtitles with auto color contrast
- 🎙️ **Transcription Pipeline** - Whisper-based speech-to-text with speaker diarization
- 🎥 **Video Processing Tools** - Concatenation, trimming, audio extraction
- 🖼️ **Image Tools** - Text rendering, compositing, frame extraction

---

## 🎯 See it in Action

The "Why" behind this project and the high-fidelity results (Ghibli 2.0, The Last Algorithm) are documented in detail on my personal site:

### **[Read the Full Article: Programmable Cinematography](https://www.hersi.dev/blog/ministudio)**

---

## 🏗️ The Architecture: How it Works

MiniStudio uses a three-layer stack to ensure your characters don't "drift" between shots.

```
┌─────────────────────────────────────────────────────────┐
│                    MiniStudio Pipeline                  │
├─────────────────────────────────────────────────────────┤
│  📋 Shot Plan (JSON/CineLang)                          │
│       ↓                                                 │
│  🎬 Cinematography Profile (lens, lighting, mood)      │
│       ↓                                                 │
│  📝 Prompt Compiler (structured → provider format)     │
│       ↓                                                 │
│  🎥 Provider (Veo / HuggingFace / Vertex AI / Local)   │
│       ↓                                                 │
│  🎞️ Post Processor (color grade, transitions, audio)   │
│       ↓                                                 │
│  📺 Final Video                                        │
└─────────────────────────────────────────────────────────┘
```

1.  **Identity Grounding 2.0**: We use "Master Reference" portraits (Visual Anchors) that are injected into every injection step, ensuring **Emma** looks like **Emma** in Shot 1 and Shot 60.
2.  **The Invisible Weave**: A state-machine that "remembers" the environment geometry. If you move the camera 45 degrees, the engine knows what *should* be there.
3.  **Sequential Memory**: Each generation is grounded by the final frames of the previous shot, creating a perfect temporal link.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Basic installation
pip install -e .

# With HuggingFace models (GPU recommended)
pip install -e ".[huggingface]"

# With all optional dependencies
pip install -e ".[all]"
```

### 2. Configure Credentials
MiniStudio supports **Google Veo**, **Vertex AI**, **HuggingFace**, and is extensible to any generative model. 

**See the [Configuration & Secrets Guide](docs/configuration_and_secrets.md)** for comprehensive setup instructions.

#### Quick Setup (Local Dev)
```bash
cp .env.example .env
# Edit .env with your API keys
```

#### Quick Setup (Production with Doppler)
```bash
doppler run -- python examples/contextbytes_brand_story.py
```

### 3. Your First Shot

**For Non-Technical Users (Simplest!)**
```python
from ministudio.simple_builder import generate_video

# Just describe what you want!
result = generate_video("""
A lone researcher discovers a glowing orb in the lab.
She looks amazed and reaches towards it.
Duration: 10 seconds
Style: cinematic
""")

print(f"Video created: {result.video_path}")
```

**For Developers (With Providers)**
```python
from ministudio import create_provider, VideoOrchestrator
from ministudio.config import ShotConfig

# Auto-detect best provider (Veo > HuggingFace > Mock)
provider = create_provider()

# Or specify one
from ministudio.providers import HuggingFaceProvider, HFVideoConfig
provider = HuggingFaceProvider(HFVideoConfig(model="cerspense/zeroscope_v2_576w"))

orchestrator = VideoOrchestrator(provider)

shot = ShotConfig(
    action="A lone researcher discovers a glowing orb.",
    duration_seconds=8
)

await orchestrator.generate_shot(shot)
```

**Interactive Mode** (no code needed!):
```bash
python ministudio/simple_builder.py
```

---

## 🎬 Provider Support

MiniStudio supports multiple video generation providers:

| Provider | Status | Models | Best For |
|----------|--------|--------|----------|
| **Google Veo** | ✅ Ready | Veo 1, Veo 2 | Production, highest quality |
| **HuggingFace** | ✅ Ready | Zeroscope, SVD, AnimateDiff, CogVideoX, Open-Sora | Local GPU, open-source |
| **Vertex AI** | ✅ Ready | Veo 3.1, Imagen | Cloud production |
| **Local Models** | ✅ Ready | Any diffusers model | Privacy, offline |
| **Mock** | ✅ Ready | Test patterns | Development, testing |
| **OpenAI Sora** | 🚧 Coming | Sora | Ultra-high quality |

### Using HuggingFace Models

```python
from ministudio.providers import HuggingFaceProvider, HFVideoConfig, HFVideoModel

# Lightweight model (6GB VRAM)
config = HFVideoConfig(model=HFVideoModel.ZEROSCOPE)

# High quality (16GB VRAM)
config = HFVideoConfig(model=HFVideoModel.COGVIDEO)

# Image-to-video (16GB VRAM)
config = HFVideoConfig(model=HFVideoModel.SVD_XT)

provider = HuggingFaceProvider(config)
result = await provider.generate("A cinematic sunset over mountains", duration=5)
```

### Using Google Veo

```python
from ministudio.providers import VeoProvider, VeoConfig, VeoModel

config = VeoConfig(
    project_id="your-gcp-project",
    model=VeoModel.VEO_2,
    resolution="1080p"
)

provider = VeoProvider(config)
result = await provider.generate("Cinematic drone shot of a city at night", duration=8)
```

---

## 📝 Text & Subtitle System

Add professional text overlays with intelligent color contrast:

```python
from ministudio import VideoTextPipeline, auto_subtitle, add_title

# Auto-generate subtitles from speech
auto_subtitle("input.mp4", "output_with_subs.mp4")

# Add custom title with auto-contrast colors
add_title("input.mp4", "My Epic Video", "output.mp4")

# Full pipeline
pipeline = VideoTextPipeline()
pipeline.add_subtitles("video.mp4", "subtitles.srt", "output.mp4",
    style="cinematic",  # Auto color contrast
    position="bottom"
)
```

---

## 🎙️ Audio & Transcription

```python
from ministudio import transcribe, transcribe_to_srt

# Transcribe audio/video
transcription = transcribe("video.mp4")
print(transcription.text)

# Generate SRT subtitles
transcribe_to_srt("video.mp4", "output.srt")

# With speaker diarization
transcription = transcribe("video.mp4", diarize=True)
for segment in transcription.segments:
    print(f"[{segment.speaker}] {segment.text}")
```

---

## 🎥 Demo Runner

Generate the 3-minute CineLang meta-demo:

```bash
# List all shots in the demo
python -m examples.demo_runner --list-shots

# List available HuggingFace models
python -m examples.demo_runner --list-models

# Generate with HuggingFace (local GPU)
python -m examples.demo_runner --provider huggingface

# Generate with Google Veo
python -m examples.demo_runner --provider veo --veo-project your-project

# Generate specific shot
python -m examples.demo_runner --shot shot_1_intro
```

---

## 📚 Documentation

- **[Configuration & Secrets Guide](docs/configuration_and_secrets.md)** - Setup providers and credentials
- **[For Non-Technical Users](docs/for_non_technical_users.md)** - Simple Builder guide
- **[API Reference](docs/api.md)** - Full API documentation
- **[Production Journal](PRODUCTION_JOURNAL.md)** - Research and learnings
- **[Roadmap](ROADMAP.md)** - Upcoming features

---

## 🔬 Challenges & Research

Current research areas in **[Production Journal](PRODUCTION_JOURNAL.md)**:
- **Audio-Sync Lag**: Refining the waveform orchestrator to eliminate the 0.5s voice/video drift.
- **Environment Shimmer**: Implementing 2-pass background locking.
- **Character Masks**: Forcing the AI to paint "over" a locked environment plate.

---

## 🤝 Contributing & Community

MiniStudio is built by the community for the community. 

- See **[CONTRIBUTING.md](CONTRIBUTING.md)** for contribution guidelines
- See **[ROADMAP.md](ROADMAP.md)** for upcoming features
- See **[ENGINEER_GUIDE.md](ENGINEER_GUIDE.md)** for architecture details

---

**Made with ❤️ for the future of cinema.**
