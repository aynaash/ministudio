# MiniStudio: The Cinematic AI Engine 🎬✨

**Programmable, Stateful, and Model-Agnostic Orchestration for High-Fidelity Video Production.**

MiniStudio transforms the chaotic world of generative AI into a structured filmmaking pipeline. It solves the "Consistency Problem" by treating video like code—enforcing character identity, environment stability, and temporal continuity through a state-machine driven architecture.

---

## 🎬 See it in Action

The "Why" behind this project and the high-fidelity results (Ghibli 2.0, The Last Algorithm) are documented in detail on my personal site:

### **👉 [Read the Full Article: Programmable Cinematography](https://www.hersi.dev/blog/ministudio)**

---

## 🛠️ The Architecture: How it Works

MiniStudio uses a three-layer stack to ensure your characters don't "drift" between shots.

1.  **Identity Grounding 2.0**: We use "Master Reference" portraits (Visual Anchors) that are injected into every injection step, ensuring **Emma** looks like **Emma** in Shot 1 and Shot 60.
2.  **The Invisible Weave**: A state-machine that "remembers" the environment geometry. If you move the camera 45 degrees, the engine knows what *should* be there.
3.  **Sequential Memory**: Each generation is grounded by the final frames of the previous shot, creating a perfect temporal link.

---

## 🚀 Quick Start

### 1. Installation
```bash
pip install -e .
```

### 2. Configure Credentials
MiniStudio supports **Vertex AI (Veo 3.1)** and **Google TTS**. 

#### Using Doppler (Recommended)
[Doppler](https://www.doppler.com/) is a multi-platform secret manager. If you use it, you can run:
```bash
doppler run -- python examples/contextbytes_brand_story.py
```

#### Using .env or Environment Variables
If you don't use Doppler, simply create a `.env` file or export your variables directly:
```bash
export GOOGLE_API_KEY="your-key-here"
# or
export GOOGLE_APPLICATION_CREDENTIALS="path/to/key.json"
```

### 3. Your First Shot
```python
from ministudio import VideoOrchestrator, VertexAIProvider

# Initialize the Director
orchestrator = VideoOrchestrator(VertexAIProvider())

# Define a Shot
shot = ShotConfig(
    action="A lone researcher discovers a glowing orb.",
    characters={"Emma": EMMA_STRICT_ID},
    duration_seconds=8
)

# Produce
await orchestrator.generate_shot(shot)
```

---

## ⚠️ Challenges & Roadmap (AI Filmmaking 2.0)

We are currently pushing the boundaries of what is possible. Current research areas included in our **[Production Journal](PRODUCTION_JOURNAL.md)**:
- **Audio-Sync Lag**: Refining the waveform orchestrator to eliminate the 0.5s voice/video drift.
- **Environment Shimmer**: Implementing 2-pass background locking.
- **Character Masks**: Forcing the AI to paint "over" a locked environment plate.

---

## 🤝 Contributing & Community
MiniStudio is built by the community for the community. See **[ROADMAP.md](ROADMAP.md)** for our upcoming features.

**Made with ❤️ for the future of cinema.**
