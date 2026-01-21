# MiniStudio: Engineer's Guide & Documentation

Welcome to the MiniStudio development repository. This guide explains how to use the library to create high-consistency AI videos and how to extend it for your own use cases.

## 🛠️ Installation & Setup

```bash
# Clone the repository
git clone https://github.com/aynaash/ministudio.git

# Install dependencies
pip install -r requirements.txt

# Set up authentication (choose one)
# 1. API Key (Recommended for simplicity)
export VERTEX_AI_API_KEY="your-api-key"

# 2. Service Account JSON
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

## 🏗️ Core Architecture: The "Stateful" Workflow

MiniStudio is built on the principle that **Video is Code**. Unlike simple prompt-based generators, MiniStudio tracks visual state across multiple API calls.

### 1. Define Visual Identity (Global State)
Characters and environments have a "Global Identity" that acts as a visual anchor.

```python
from ministudio.config import Character, Environment

# Character "Grounding"
MAYA = Character(
    name="Maya",
    identity={
        "hair_style": "long dark braid",
        "eye_color": "bright amber"
    }
)

# Environment "Grounding"
LAB = Environment(
    location="High-tech Lab",
    identity={"architecture_style": "Minimalist white and glass"}
)
```

### 2. Orchestrate the Scene
Use the `VideoOrchestrator` to coordinate the generation of multiple shots.

```python
from ministudio.orchestrator import VideoOrchestrator
from ministudio.providers.vertex_ai import VertexAIProvider

orchestrator = VideoOrchestrator(VertexAIProvider())

# Define shots with "continuity_required=True"
scene = SceneConfig(
    characters={"Maya": MAYA},
    environment=LAB,
    shots=[
        ShotConfig(action="Maya typing", continuity_required=True),
        ShotConfig(action="Maya looking up in surprise", continuity_required=True)
    ]
)

# Generate a unified MP4
result = await orchestrator.generate_production(scene)
```

## 🧠 Advanced Grounding Mechanism

MiniStudio solves the "drift" problem in 3 ways:
1.  **Prompt Anchoring**: The `identity` fields are injected at the top of every AI prompt as "CRITICAL" instructions.
2.  **Frame Continuity**: The orchestrator extracts the last 3 frames of `Shot N` and passes them as the "starting_frames" for `Shot N+1`.
3.  **Sequential Locking**: Videos are generated and merged in strict sequential order based on the `shot_idx`.

## 🛠️ Extending MiniStudio

### Adding a New Video Provider
1.  Create `ministudio/providers/your_provider.py`.
2.  Inherit from `BaseVideoProvider`.
3.  Implement `generate_video(request)`.
4.  Optionally support an `api_key` in the constructor.

### Custom Prompt Compilation
If you want to change how the objects are turned into text, modify `ministudio/compiler.py`.

## 📜 Available Examples
- `examples/ghibli_studio_demo.py`: Studio Ghibli artistic style.
- `examples/quantum_tiktok_demo.py`: Educational TikTok content (9:16).
- `examples/consistent_story_demo.py`: Demonstrates maximum character persistence.
- `examples/complex_story_demo.py`: Shows emotional evolution and background transitions.
