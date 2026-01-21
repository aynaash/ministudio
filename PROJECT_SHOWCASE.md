# MiniStudio Project Showcase 🎬

Welcome to the future of **Stateful Video Generation**. MiniStudio allows developers to treat video production like code—structured, repeatable, and identity-grounded.

---

## 📽️ The Productions

### 🌟 1. ContextBytes Brand Story (Ghibli 2.0)
**Script Path**: `examples/contextbytes_brand_story.py`  
**Vision**: A cinematic 1-minute journey from data chaos to cloud wisdom using Studio Ghibli aesthetics.

| The Production Script | The Cinematic Player |
| :--- | :--- |
| **[Brand Story 2.0](examples/contextbytes_brand_story.py)** | <video src="contextbytes_production/contextbytes_brand_story.mp4" controls width="400"></video> |
| **[The Last Algorithm](examples/complex_story_demo.py)** | <video src="the_last_algorithm/the_last_algorithm.mp4" controls width="400"></video> |
| **[Quantum TikTok](examples/quantum_tiktok_demo.py)** | <video src="quantum_tiktok/quantum_mechanics_explained.mp4" controls width="400"></video> |

---

## ⚠️ Challenges & Technical Ceiling

Generative video is evolving rapidly. Here are the current challenges we've logged and our roadmap to solve them:

### 1. Visual Drift (Character & Environment)
- **Challenge**: Character clothing or environment layout can shift slightly between shots.
- **Solution**: Implementing **Global Seed Locking** and **Semantic Identity Masks** in the next update.

### 2. Audio-Visual Synchronization
- **Challenge**: Variable TTS lengths can sometimes lead or lag the generated video frames.
- **Solution**: Moving to a **Waveform-Controlled Orchestrator** that dynamically pad/clips video to match audio beats.

### 3. Background Stability
- **Challenge**: Complex hand-drawn backgrounds can "shimmer" or change proportions.
- **Solution**: Working on a **2-Pass Generation** technique where the background is locked in pass 1.

---

## 🛠️ How to View
To reproduce these results, ensure your `DOPPLER_TOKEN` is set and run:
```bash
doppler run -- python examples/contextbytes_brand_story.py
```

Check out [GITHUB_SHOWCASE.md](GITHUB_SHOWCASE.md) for tips on presenting these videos in your own repository!
