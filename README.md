# MiniStudio: The Cinematic AI Engine

**Programmable, Stateful, and Model-Agnostic Orchestration for High-Fidelity Video Production.**

MiniStudio transforms the chaotic world of generative AI into a structured filmmaking pipeline. It solves the "Consistency Problem" by treating video like code—enforcing character identity, environment stability, and temporal continuity through a state-machine driven architecture.

---

## See it in Action

The "Why" behind this project and the high-fidelity results (Ghibli 2.0, The Last Algorithm) are documented in detail on my personal site:

### **[Read the Full Article: Programmable Cinematography](https://www.hersi.dev/blog/ministudio)**

---

## The Architecture: How it Works

MiniStudio uses a three-layer stack to ensure your characters don't "drift" between shots.

1.  **Identity Grounding 2.0**: We use "Master Reference" portraits (Visual Anchors) that are injected into every injection step, ensuring **Emma** looks like **Emma** in Shot 1 and Shot 60.
2.  **The Invisible Weave**: A state-machine that "remembers" the environment geometry. If you move the camera 45 degrees, the engine knows what *should* be there.
3.  **Sequential Memory**: Each generation is grounded by the final frames of the previous shot, creating a perfect temporal link.

---

## Quick Start

### 1. Installation
```bash
pip install -e .
```

### 2. Configure Credentials
MiniStudio supports **Vertex AI (Veo 3.1)**, **Google TTS**, and is extensible to any generative model. 

**See the [Configuration & Secrets Guide](docs/configuration_and_secrets.md)** for comprehensive setup instructions covering:
- Doppler (recommended for production)
- `.env` files for local development
- Cloud secret managers (GCP, AWS, Azure)
- Multi-provider integration (Hugging Face, local models, custom endpoints)

#### Quick Setup (Local Dev)
1. Copy `.env.example` to `.env`
2. Add your credentials:
```bash
cp .env.example .env
# Edit .env with your API keys
```

#### Quick Setup (Production with Doppler)
```bash
# Install Doppler: https://www.doppler.com/docs/cli
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

Or use **interactive mode** (no code needed!):
```bash
python ministudio/simple_builder.py
```

👉 **[See "For Non-Technical Users" Guide](docs/for_non_technical_users.md)**

**For Developers (With Adapters)**
```python
from ministudio import VideoOrchestrator
from ministudio.adapters import VertexAIAdapter

# Initialize with your provider
provider = VertexAIAdapter.create(project_id="my-gcp-project")
orchestrator = VideoOrchestrator(provider)

# Define a Shot
shot = ShotConfig(
    action="A lone researcher discovers a glowing orb.",
    characters={"Emma": EMMA_STRICT_ID},
    duration_seconds=8
)

# Produce
await orchestrator.generate_shot(shot)
```

👉 **[See Provider Adapters](ministudio/adapters/README.md)**

---

## Provider Support

MiniStudio supports multiple video generation providers out of the box:

| Provider | Status | Setup Difficulty | Cost | Best For |
|----------|--------|------------------|------|----------|
| **Vertex AI (Veo 3.1)** | ✅ Built-in | Easy | $$ | Production, quality |
| **Hugging Face** | ✅ Built-in | Easy | Free (local) / $ (cloud) | Development, flexibility |
| **Local Models** | ✅ Built-in | Medium | Free | Privacy, offline, experimentation |
| **OpenAI Sora** | 🚧 Coming Soon | TBD | TBD | Ultra-high quality |
| **Kling AI** | 🚧 Roadmap | TBD | TBD | Alternative provider |
| **Luma AI** | 🚧 Roadmap | TBD | TBD | Alternative provider |

See [Configuration & Secrets Guide](docs/configuration_and_secrets.md) for detailed integration instructions.

---

## Challenges & Roadmap (AI Filmmaking 2.0)

We are currently pushing the boundaries of what is possible. Current research areas included in our **[Production Journal](PRODUCTION_JOURNAL.md)**:
- **Audio-Sync Lag**: Refining the waveform orchestrator to eliminate the 0.5s voice/video drift.
- **Environment Shimmer**: Implementing 2-pass background locking.
- **Character Masks**: Forcing the AI to paint "over" a locked environment plate.

---

## Contributing & Community
MiniStudio is built by the community for the community. See **[ROADMAP.md](ROADMAP.md)** for our upcoming features.

**Made with love for the future of cinema.**
