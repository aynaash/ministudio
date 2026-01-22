# Ministudio Documentation

**Model-Agnostic AI Video Framework**

*"The Model-Agnostic AI Video Framework - Make AI video generation as consistent as CSS makes web styling"*

[![PyPI version](https://badge.fury.io/py/ministudio.svg)](https://pypi.org/project/ministudio/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Welcome to Ministudio, the open-source framework that makes AI video generation consistent and programmable. Define your character once, use it everywhere - across different AI models, providers, and projects.

## Table of Contents

- [What is Ministudio?](#what-is-ministudio)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Providers](#providers)
- [Styles and Templates](#styles-and-templates)
- [Docker and Self-Hosting](#docker-and-self-hosting)
- [Examples](#examples)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [FAQ](#faq)

## What is Ministudio?

Ministudio is an open-source framework that abstracts AI video generation across multiple providers (Google Vertex AI, OpenAI Sora, local models, etc.). Its core innovation is **stateful prompt programming** - maintain visual consistency across generations.

### Key Features

- **Model-Agnostic**: Swap providers without changing code
- **Character Consistency**: Define once, use everywhere
- **State Management**: Remember what happened in previous scenes
- **Extensible**: Plugin architecture for new providers
- **Self-Hostable**: Run your own API server
- **Docker Ready**: Containerized deployment

### The Problem It Solves

Traditional AI video generation suffers from inconsistency:

```python
# Traditional approach - characters change between videos
video1 = generate("golden orb teaching math")
video2 = generate("golden orb teaching physics")
# Orb looks completely different in each video!
```

```python
# Ministudio approach - consistent characters
studio = Ministudio(provider=provider, style=style)
studio.define_character("orb", orb_description)

video1 = studio.generate("orb teaching math")  # Same orb
video2 = studio.generate("orb teaching physics")  # Same orb
```

## Quick Start

### 1. Install

```bash
pip install ministudio
```

### 2. Generate Your First Video

```bash
# Mock provider (no API keys needed)
ministudio --provider mock --concept "Neural Networks" --action "orb visualizing particle connections"
```

### 3. Use Real Providers

```bash
# Google Vertex AI
export GCP_PROJECT_ID="your-project-id"
ministudio --provider vertex-ai --concept "Quantum Physics" --action "orb demonstrating wave functions"

# OpenAI Sora
export OPENAI_API_KEY="your-api-key"
ministudio --provider openai-sora --concept "Evolution" --action "orb showing species adaptation"
```

### 4. Programmatic Usage

```python
from ministudio import Ministudio

# Create studio
studio = Ministudio.create_provider("mock")
studio = Ministudio(provider=studio)

# Generate video
result = await studio.generate_concept_video(
    concept="Machine Learning",
    action="orb sorting data points"
)

print(f"Video saved: {result.video_path}")
```

## Installation

### Basic Installation

```bash
pip install ministudio
```

### With Provider Support

```bash
# Google Vertex AI
pip install ministudio[vertex-ai]

# OpenAI Sora
pip install ministudio[openai]

# All providers
pip install ministudio[all]
```

### From Source

```bash
git clone https://github.com/yourusername/ministudio.git
cd ministudio
pip install -e .
```

### Requirements

- Python 3.8+
- Provider-specific API keys (optional)

## Core Concepts

### State Management

Ministudio maintains consistency through stateful prompt engineering:

```python
style_config = StyleConfig(
    characters={
        "orb": {
            "appearance": "Golden glowing orb",
            "motion": "Floating drift",
            "glow": "Warm teal accents"
        }
    },
    environment={
        "lighting": "Golden hour",
        "setting": "Twilight sky"
    }
)

studio = Ministudio(provider=provider, style_config=style_config)
```

### Provider Abstraction

All providers implement the same interface:

```python
class VideoProvider(Protocol):
    @property
    def name(self) -> str: ...
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult: ...
```

Add new providers by extending `BaseVideoProvider`.

### Prompt Engine

The prompt engine enhances raw prompts with consistency rules:

```python
prompt_engine = PromptEngine(style_config)
enhanced_prompt = prompt_engine.create_prompt(
    concept="AI Learning",
    action="orb discovering patterns",
    mood="magical"
)
```

## Usage

### Command Line Interface

```bash
ministudio --help
ministudio --provider mock --concept "topic" --action "description" [--duration 8]
```

### Python API

```python
import asyncio
from ministudio import Ministudio

async def main():
    provider = Ministudio.create_provider("mock")
    studio = Ministudio(provider=provider)

    result = await studio.generate_concept_video(
        concept="Mathematics",
        action="orb solving equations"
    )

asyncio.run(main())
```

### API Server

Run the self-hosted API:

```bash
# Install with API dependencies
pip install ministudio[all]

# Run server
uvicorn ministudio.api:app --host 0.0.0.0 --port 8000
```

API endpoints:

- `POST /generate` - Generate video
- `GET /health` - Health check
- `GET /` - API info

## API Reference

### Ministudio Class

```python
class Ministudio:
    def __init__(self, provider: VideoProvider, style_config: Optional[StyleConfig] = None, output_dir: str = "./ministudio_output")

    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> BaseVideoProvider:
        """Factory method for providers"""

    async def generate_concept_video(self, concept: str, action: str, duration: int = 8, mood: str = "magical", filename: Optional[str] = None) -> VideoGenerationResult:
        """Generate a video for a concept"""

    async def generate_template_series(self, template_name: str, concepts: List[str]) -> List[VideoGenerationResult]:
        """Generate series using templates"""
```

### VideoGenerationRequest

```python
@dataclass
class VideoGenerationRequest:
    prompt: str
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    style_guidance: Optional[Dict[str, Any]] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None
```

### VideoGenerationResult

```python
@dataclass
class VideoGenerationResult:
    success: bool
    video_path: Optional[Path] = None
    video_bytes: Optional[bytes] = None
    provider: str = "unknown"
    generation_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_video(self) -> bool:
        return bool(self.video_path or self.video_bytes)
```

### StyleConfig

Configuration for visual consistency:

```python
@dataclass
class StyleConfig:
    name: str = "ghibli"
    characters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    technical: Dict[str, Any] = field(default_factory=dict)
```

## Providers

### Available Providers

| Provider | Status | Setup |
|----------|--------|-------|
| Mock |  Ready | No setup required |
| Google Vertex AI |  Ready | `GCP_PROJECT_ID` env var |
| OpenAI Sora |  Ready | `OPENAI_API_KEY` env var |
| Local (SVD) |  Ready | Model path configuration |

### Adding New Providers

```python
from ministudio.providers.base import BaseVideoProvider

class NewProvider(BaseVideoProvider):
    @property
    def name(self) -> str:
        return "new-provider"

    async def generate_video(self, request):
        # Implementation
        pass
```

## Styles and Templates

### Built-in Styles

```python
from ministudio.styles import ghibli_style, cyberpunk_style, realistic_style, cinematic_style

# Use predefined styles
studio = Ministudio(provider=provider, style_config=ghibli_style)
```

### Custom Styles

```python
custom_style = StyleConfig(
    name="my_style",
    characters={"hero": {"appearance": "Brave warrior", ...}},
    environment={"lighting": "Epic fantasy", ...}
)
```

### Templates

```python
from ministudio.templates import explainer_template, marketing_template, cinematic_template

# Use templates for specific use cases
result = await studio.generate_concept_video(
    concept="Product Demo",
    action="hero showcasing features",
    template=marketing_template
)
```

## Docker and Self-Hosting

### Docker Image

Build and run with Docker:

```bash
# Build image
docker build -t ministudio .

# Run container
docker run -p 8000:8000 ministudio
```

### Self-Hosting

The API server allows self-hosting:

```bash
# Run locally
uvicorn ministudio.api:app --reload

# Access at http://localhost:8000
```

## Examples

### Basic Usage

```python
import asyncio
from ministudio import Ministudio

async def example():
    provider = Ministudio.create_provider("mock")
    studio = Ministudio(provider=provider)

    result = await studio.generate_concept_video(
        concept="Climate Change",
        action="orb showing rising temperatures"
    )

    if result.success:
        print(f"Generated: {result.video_path}")

asyncio.run(example())
```

### Character Consistency

```python
style = StyleConfig(characters={
    "orb": {
        "appearance": "Golden orb with circuits",
        "motion": "Gentle floating"
    }
})

studio = Ministudio(provider=provider, style_config=style)

# Same orb in both videos
video1 = await studio.generate_concept_video("Math", "orb calculating")
video2 = await studio.generate_concept_video("Physics", "orb experimenting")
```

### Template Usage

```python
from ministudio.templates import cinematic_template

result = await studio.generate_concept_video(
    concept="Battle Scene",
    action="warrior fighting dragon",
    template=cinematic_template
)
```

## Contributing

We welcome contributions! See our [Contributing Guide](contributing.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/ministudio.git
cd ministudio
pip install -e .[all]
```

### Adding Providers

1. Create `providers/new_provider.py`
2. Extend `BaseVideoProvider`
3. Add to factory method
4. Update docs

### Code Style

- Black for formatting
- Ruff for linting
- Type hints required

## Roadmap

### Phase 1: Developer Adoption (Current)

-  MVP with core providers
-  CLI and Python API
-  Self-hostable API server
-  Docker containerization
-  MCP server integration
-  Cinematic filmmaking templates

### Phase 2: Production Ready

- Advanced video editing
- Cost optimization
- Batch processing
- Performance benchmarks
- Rust extensions for speed

### Phase 3: Ecosystem

- Plugin marketplace
- Integration with LangChain, AutoGPT
- Enterprise features
- Community templates

### Phase 4: Industry Standard

- Open API specification
- Benchmark suite
- Research partnerships

## FAQ

### Q: How does Ministudio ensure consistency?

A: Through stateful prompt engineering - the framework remembers character appearances, environment settings, and scene history, injecting consistency rules into every prompt.

### Q: Can I use multiple providers?

A: Yes! Switch providers without changing your code. Each provider implements the same interface.

### Q: Is it free?

A: The framework is free and open-source. Provider APIs may have costs (Google Vertex AI, OpenAI, etc.).

### Q: Can I run locally?

A: Yes! Use local providers or self-host the API server. Docker support included.

### Q: How do I add new providers?

A: Extend `BaseVideoProvider` and implement the required methods. See the provider documentation.

### Q: What's the difference from other AI video tools?

A: Ministudio focuses on consistency and abstraction, not just raw generation. It's the "framework" that makes other tools production-ready.

## Support

- **Documentation**: You're reading it!
- **Issues**: [GitHub Issues](https://github.com/yourusername/ministudio/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ministudio/discussions)
- **Discord**: [Join our community](https://discord.gg/ministudio)

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Built with  for the AI video generation community**

*Consistent AI video generation, made simple.*
