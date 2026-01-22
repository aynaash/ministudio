# MiniStudio Project Showcase 🎬

Welcome to the future of **Stateful Video Generation**. MiniStudio allows developers to treat video production like code—structured, repeatable, and identity-grounded.

---

## 📽️ The Productions

### 🌟 1. ContextBytes Brand Story (Ghibli 2.0)
**Script Path**: `examples/contextbytes_brand_story.py`  
**Vision**: A cinematic 1-minute journey from data chaos to cloud wisdom using Studio Ghibli aesthetics.

| The Production Script | The Result |
| :--- | :--- |
| **[Brand Story 2.0](examples/contextbytes_brand_story.py)** | [See High-Quality Result on hersi.dev](https://www.hersi.dev/blog/ministudio) |
| **[The Last Algorithm](examples/complex_story_demo.py)** | [See High-Quality Result on hersi.dev](https://www.hersi.dev/blog/ministudio) |
| **[Quantum TikTok](examples/quantum_tiktok_demo.py)** | [See High-Quality Result on hersi.dev](https://www.hersi.dev/blog/ministudio) |

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
To reproduce these results, ensure your credentials are set. We use **Doppler** (a secret manager) for security, but you can also use a standard `.env` file or environment variables.

### Running with Doppler:
```bash
doppler run -- python examples/contextbytes_brand_story.py
```

### Running with .env / Shell:
```bash
python examples/contextbytes_brand_story.py
```
*(Ensure `GOOGLE_API_KEY` or `GOOGLE_APPLICATION_CREDENTIALS` are exported in your shell.)*
