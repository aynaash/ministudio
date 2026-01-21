# MiniStudio: The Cinematic AI Engine 🎬✨

**Programmable, Stateful, and Model-Agnostic Orchestration for High-Fidelity Video Production.**

MiniStudio transforms the chaotic world of generative AI into a structured filmmaking pipeline. It solves the "Consistency Problem" by treating video like code—enforcing character identity, environment stability, and temporal continuity through a state-machine driven architecture.

---

## 📽️ Visual Showcase (Stateful Productions)

MiniStudio isn't just a wrapper; it's a director. Below are complete productions generated entirely by the engine.

### 🌟 The "Ghibli 2.0" Brand Story
*Theme: Intellectual Empowerment & Awe. Style: Studio Ghibli x Makoto Shinkai.*

| 📜 The Script | 🎬 The Production (S3 Hosted) |
| :--- | :--- |
| **Emma** (Heroine) looks overwhelmed at a desk. Thousands of data screens reflect in her eyes. The room is cold blue. Suddenly, a **Golden Orb** pulses, weaving teal threads between a physical book and a tablet. | <video src="https://ministudio-public.s3.amazonaws.com/contextbytes_brand_story.mp4" controls width="480"></video> |

> [!TIP]
> **View the Code**: [contextbytes_brand_story.py](examples/contextbytes_brand_story.py)

---

### 🧬 The "Last Algorithm" Narrative
*Theme: Sci-Fi Mystery. Style: Cinematic Cyberpunk Night.*

| 📜 The Script | 🎬 The Production (S3 Hosted) |
| :--- | :--- |
| **Sarah** transitions from scholarly focus to visceral fear as her AI hologram (**Aria**) begins to glitch. Dramatic lighting shifts from Lab-Blue to Alarm-Red. | <video src="https://ministudio-public.s3.amazonaws.com/the_last_algorithm.mp4" controls width="480"></video> |

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
MiniStudio supports **Vertex AI (Veo 3.1)** and **Google TTS**. Use Doppler for secure secret management:
```bash
doppler run -- python examples/contextbytes_brand_story.py
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
