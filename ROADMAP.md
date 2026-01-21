# Ministudio Roadmap

Our goal is to reach v1.0 as the definitive orchestration layer for AI video.

## Phase 1: Foundation (Current - ✅ Complete)
- [x] Basic provider architecture (Mock, Vertex AI)
- [x] "Kubernetes for Video" Orchestration Engine
- [x] State Machine for world state persistence
- [x] Programmatic Prompt Compiler (Character, Environment, Lighting DNA)
- [x] Model-agnostic configuration (`VideoConfig`)pulish to ppypi too

## Phase 2: Performance & Precision (In Progress)
- [ ] **Visual DNA Extraction**: Analyze generated videos to update State Machine automatically.
- [ ] **Precision Lighting**: Better mapping of `LightSource` objects to provider-specific prompts.
- [ ] **Camera Pathing**: Programmatic camera movements (pan, tilt, dolly) via `Cinematography`.
- [ ] **Parallel Generation**: Parallelize independent scenes in a sequence.

## Phase 3: Provider Ecosystem
- [ ] **OpenAI Sora Integration**: Support for Sora API once broadly available.
- [ ] **Local Model Support**: Integration with local generation models (Stable Video Diffusion, etc.).
- [ ] **Model Router**: Automatically select the best provider based on scene requirements.

## Phase 4: Creative Tools
- [ ] **Storyboard-as-Code**: YAML/JSON schema for defining entire movies.
- [ ] **Gradio Dashboard**: Full-featured visual engine for managing state and segments.
- [ ] **Plugin System**: Allow custom "Visual Modifiers" to be injected into the compiler.

## v1.0: Production Ready
- [ ] Enterprise-grade security and secret management.
- [ ] Fine-tuned prompt templates for maximum consistency.
- [ ] Real-time state visualization.

---

*Found a feature you want to build? Check [CONTRIBUTING.md](CONTRIBUTING.md) and open a PR!*
