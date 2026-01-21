# Ministudio

**The Kubernetes for AI Video Generation**

*Model-agnostic orchestration layer for sequential, consistent AI video generation*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is Ministudio?

Ministudio is a **state machine orchestration framework** for AI video generation. Think of it as Kubernetes for video pipelines - it manages state, consistency, and sequencing across multiple AI model providers while handling context window limitations automatically.

### The Problem We Solve

```yaml
Current AI Video Pain Points:
1. Context Window Limits: Models can't remember characters across scenes
2. Model Switching Pain: Changing providers breaks consistency  
3. No State Management: Every prompt starts from scratch
4. Sequential Generation Hell: Manual stitching of multi-part videos
5. Style Drift: Characters/environments change unpredictably
```

### The Solution

```
Ministudio = State Machine + Prompt Compiler + Model Router
```

## Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

```python
from ministudio import Ministudio, VideoConfig

# Create provider (mock for testing, vertex-ai for production)
provider = Ministudio.create_provider("mock")
studio = Ministudio(provider=provider)

# Generate a video
result = await studio.generate_concept_video(
    concept="Introduction",
    action="A golden orb floating in a magical library"
)
```

### With Vertex AI

```bash
# Set up credentials in Doppler or environment
export GCP_PROJECT_ID="your-project"
export GCP_SERVICE_ACCOUNT_JSON='{"type": "service_account", ...}'

# Or use Doppler
doppler run -- python your_script.py
```

```python
from ministudio import Ministudio, VideoConfig

# Vertex AI provider
provider = Ministudio.create_provider("vertex-ai")
studio = Ministudio(provider=provider)

config = VideoConfig(duration_seconds=5, mood="magical")
result = await studio.generate_concept_video(
    concept="Test",
    action="A glowing orb in space",
    config=config
)
```

## Core Architecture

### 1. State Machine (`ministudio/state.py`)
Manages persistent world state across scenes:
- **VideoStateMachine**: Tracks characters, environment, style
- **StatePersistenceEngine**: Maintains history and continuity
- **WorldState**: Immutable snapshots at each scene

### 2. Prompt Compiler (`ministudio/compiler.py`)
Converts rich configurations into AI-readable prompts:
- Character DNA → Detailed specifications
- Environment → Physics and composition rules
- Lighting → Precise light source definitions
- Cinematography → Camera behaviors and shot composition

### 3. Orchestrator (`ministudio/orchestrator.py`)
The "Kubernetes Controller" that coordinates everything:
- `schedule_generation()`: Execute single video jobs
- `generate_sequence()`: Multi-scene with state persistence
- Model routing (future): Select best provider per scene

## Programmable Visuals (Code-as-Video)

Define every visual detail programmatically:

```python
from ministudio import VideoConfig
from ministudio.config import Character, Environment, LightingDirector, LightSource, Color

# Define character DNA
hero = Character(
    name="Hero Orb",
    genetics={
        "core": "golden energy",
        "surface": "circuit patterns",
        "glow": "warm ethereal"
    },
    motion_library={"idle": "gentle pulsing"},
    emotional_palette={
        "joy": {"glow_intensity": 1.2},
        "curious": {"pulse_pattern": "irregular"}
    }
)

# Define environment
library = Environment(
    location="Ancient magical library",
    physics={"gravity": 0.8, "light_scattering": "volumetric"},
    composition={
        "foreground": "aged wood desk",
        "background": "stained glass windows"
    }
)

# Define lighting
lighting = LightingDirector(
    key_lights=[
        LightSource(
            type="directional",
            color=Color(hex="#FFD700"),
            intensity=0.9,
            direction=(45, 30)
        )
    ]
)

# Create config
config = VideoConfig(
    characters={"orb": hero},
    environment=library,
    lighting=lighting,
    duration_seconds=5
)

# Generate with full control
result = await studio.generate_concept_video(
    concept="Discovery",
    action="The orb discovers the library",
    config=config
)
```

## Multi-Scene Sequences with State Persistence

```python
# Define base world
config = VideoConfig(
    characters={"orb": hero},
    environment=library
)

# Generate sequence - state persists automatically
segments = [
    {"concept": "Intro", "action": "Orb enters library"},
    {"concept": "Discovery", "action": "Orb finds ancient book"},
    {"concept": "Revelation", "action": "Book glows with knowledge"}
]

results = await studio.generate_segmented_video(segments, config)
# Same orb, same library, automatic continuity!
```

## Supported Providers

| Provider | Status | Setup |
|----------|--------|-------|
| Mock | ✅ Ready | None (for testing) |
| Google Vertex AI (Veo) | ✅ Ready | `GCP_PROJECT_ID` + credentials |
| OpenAI Sora | 🚧 Planned | `OPENAI_API_KEY` |
| Local Models | 🚧 Planned | Model path |

## Testing

```bash
# Run tests
python -m pytest

# Test with mock provider
python test_vertex_simple.py

# Test with Vertex AI (if you are using doppler to manage yuor secrets)
doppler run -- python test_vertex_ai.py

# Test sequence generation
doppler run -- python test_vertex_ai.py --sequence
```

## Project Structure

```
ministudio/
├── ministudio/
│   ├── __init__.py          # Public API
│   ├── interfaces.py        # Core protocols
│   ├── core.py              # Main Ministudio class
│   ├── config.py            # Rich configuration objects
│   ├── state.py             # State machine
│   ├── compiler.py          # Prompt compiler
│   ├── orchestrator.py      # Generation orchestrator
│   └── providers/
│       ├── base.py
│       ├── mock.py          # Testing provider
│       └── vertex_ai.py     # Google Vertex AI
├── tests/
├── CONTRIBUTING.md
├── ROADMAP.md
└── README.md
```

## Philosophy

Ministudio exists because:
- **AI video generation is powerful but inconsistent**
- **Developers need programmatic control over visuals**
- **State management enables multi-scene consistency**
- **Open ecosystems beat walled gardens**

We're building the standard framework for AI video generation - model-agnostic, stateful, and extensible.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the vision and how to help.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features.

## License

MIT License - see LICENSE file

## Acknowledgments

Inspired by the open-source AI community's work on making AI accessible and consistent.

---

**Made by the AI video generation community**

*Ready to make AI video generation consistent? Let's build the future together.*
