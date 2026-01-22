# MiniStudio: Product & Engineering Roadmap

##  Vision
To become the industry standard for **Stateful AI Filmmaking**, where production-quality videos are generated through code with 100% visual and narrative continuity.

##  Phase 1: Performance & Speed Optimization (Current Priority)

###  Generation Speed
- [ ] **Parallel Shot Processing**: Implement asynchronous multi-shot generation. Currently, we generate shots 1-by-1. By parallelizing API calls, we can reduce a 1-minute video's generation time from 10+ minutes to ~3 minutes.
- [ ] **Adaptive Polling**: Implement exponential backoff or websocket-based status checks (where supported) to reduce latency between "operation complete" and "download start".
- [ ] **Asset Caching**: Cache character samples and environment background images to skip redundant uploads in multi-scene productions.

###  Production Efficiency
- [ ] **Incremental Rendering**: Only re-render the shots that changed during an edit, instead of the entire scene.
- [ ] **Streaming Merges**: Start the video merging process while the final shots are still downloading.

##  Phase 2: Model & Provider Expansion

###  Multi-Model Support
- [ ] **OpenAI Sora Integration**: Add support for Sora as a high-fidelity provider once available.
- [ ] **Kling & Luma AI**: Integrate third-party video providers via API keys to allow users to "hot-swap" engines based on price/quality.
- [ ] **Hybrid Pipeline**: Use one model for backgrounds (e.g., Luma) and another for character performance (e.g., Veo).

###  Advanced Visual Control
- [ ] **ControlNet Integration**: Support Pose, Depth, and Canny maps for frame-by-frame character control.
- [ ] **LoRA Grounding**: Automatically train and apply a "mini-LoRA" of character identity dynamically during production.

##  Phase 3: AI-Driven Directing

- [ ] **Auto-Storyboarding**: Use LLMs (Gemini Pro) to transform a simple script into the `SceneConfig` and `ShotConfig` objects automatically.
- [ ] **Vocal Emotion Tuning**: Feed the video frames back to the TTS engine to match voice inflection with visual emotion.
- [ ] **Automated QC**: An AI-based "Quality Control" agent that detects continuity errors or "hallucinations" and auto-retries the shot.

##  Engineering Guide: How to Add New Models

1.  **Inherit from `BaseVideoProvider`**: Create a new class in `ministudio/providers/`.
2.  **Implement `generate_video`**:
    - Handle prompt mapping (map MiniStudio DNA to the model's specific prompt format).
    - Manage long-running operations (polling/webhooks).
    - Extract and return `VideoGenerationResult`.
3.  **Register as a "Component"**: Update `VideoConfig` and `VideoOrchestrator` to support the new provider string.

##  Resource & API Access
- **API Keys**: MiniStudio now supports `VERTEX_AI_API_KEY` for easy integration without Service Account complexity.
- **Compute**: Future versions will support distributed rendering across multiple machines/worker-nodes.
