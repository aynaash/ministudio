# Contributing to Ministudio

Ministudio is an open-source framework designed to solve one of the hardest problems in AI video: **consistency across scenes.**

## The Vision: "Kubernetes for Video"

Just as Kubernetes manages the state of microservices, Ministudio manages the "world state" of an AI-generated video. It treats visual elements (characters, environments, lighting) as programmable state that persists across multiple generation jobs.

## Development Principles

1. **Model Agnosticism**: We don't build models; we build the orchestration layer for them.
2. **State over Prompts**: Natural language prompts are fragile. We favor structured configuration (Code-as-Video).
3. **Circular-Free Architecture**: Maintain strict separation between interfaces, core logic, and providers.
4. **Developer Experience**: "Make it as easy to generate a consistent video as it is to style a web page."

## Core Components

If you want to contribute, these are the areas to focus on:

- **State Machine (`ministudio/state.py`)**: Improving how world state is tracked and evolved.
- **Prompt Compiler (`ministudio/compiler.py`)**: Optimizing how visual configurations are translated for different models (Vertex, Sora, etc.).
- **Orchestrator (`ministudio/orchestrator.py`)**: Enhancing the "control plane" for complex multi-scene workflows.
- **Providers (`ministudio/providers/`)**: Adding support for new AI video models.

## How to Contribute

### 1. Set Up Environment

```bash
git clone https://github.com/aynaash/ministudio
cd ministudio
pip install -e .
```

### 2. Run Tests

```bash
python -m pytest
```

### 3. Adding a Provider

Implement the `VideoProvider` protocol in `ministudio/interfaces.py` and add your provider to `ministudio/providers/`.

### 4. Improving Compiled Prompts

The `ProgrammaticPromptCompiler` in `ministudio/compiler.py` is where the "magic" happens. Help us improve the templates for better visual results.

## Style Guide

- Follow PEP 8.
- Use type hints for all public methods.
- Document classes and major functions using Google-style docstrings.
- **No emojis** in logging messages (user preference).

## Join the Mission

We are building the standard framework for AI video generation. Whether you're an AI researcher, a systems engineer, or a creative coder, there's a place for you in Ministudio.

---

**Made by context-aware builders for the AI video era.**
