# API Reference

Complete reference for Ministudio's Python API.

## Ministudio Class

The main orchestrator for video generation.

### Constructor

```python
Ministudio(provider: VideoProvider, style_config: Optional[StyleConfig] = None, output_dir: str = "./ministudio_output")
```

**Parameters:**
- `provider`: Video generation provider instance
- `style_config`: Optional style configuration for consistency
- `output_dir`: Directory to save generated videos

### Methods

#### create_provider

```python
@classmethod
def create_provider(cls, provider_type: str, **provider_kwargs) -> BaseVideoProvider
```

Factory method to create provider instances.

**Parameters:**
- `provider_type`: One of "mock", "vertex-ai", "openai-sora", "local"
- `**provider_kwargs`: Provider-specific configuration

**Returns:** Configured provider instance

**Example:**
```python
provider = Ministudio.create_provider("vertex-ai", project_id="my-project")
```

#### generate_concept_video

```python
async def generate_concept_video(self, concept: str, action: str, duration: int = 8, mood: str = "magical", filename: Optional[str] = None) -> VideoGenerationResult
```

Generate a video for a specific concept and action.

**Parameters:**
- `concept`: The main topic or theme
- `action`: Description of what's happening in the video
- `duration`: Video length in seconds (default: 8)
- `mood`: Emotional tone (default: "magical")
- `filename`: Optional output filename

**Returns:** VideoGenerationResult with success status and metadata

**Example:**
```python
result = await studio.generate_concept_video(
    concept="Mathematics",
    action="orb solving equations",
    duration=10
)
```

#### generate_template_series

```python
async def generate_template_series(self, template_name: str, concepts: List[str]) -> List[VideoGenerationResult]
```

Generate a series of videos using a predefined template.

**Parameters:**
- `template_name`: Name of template ("explainer", "marketing", "cinematic")
- `concepts`: List of concepts to generate videos for

**Returns:** List of VideoGenerationResult objects

## VideoGenerationRequest

Request object for video generation.

```python
@dataclass
class VideoGenerationRequest:
    prompt: str
    duration_seconds: int = 8
    aspect_ratio: str = "16:9"
    style_guidance: Optional[Dict[str, Any]] = None
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]: ...
```

## VideoGenerationResult

Result object from video generation.

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
    def has_video(self) -> bool: ...
```

**Properties:**
- `success`: Whether generation succeeded
- `video_path`: Path to saved video file
- `video_bytes`: Raw video bytes (for API responses)
- `provider`: Name of provider used
- `generation_time`: Time taken in seconds
- `error`: Error message if failed
- `metadata`: Additional provider-specific data
- `has_video`: Whether video data is available

## StyleConfig

Configuration for visual style consistency.

```python
@dataclass
class StyleConfig:
    name: str = "ghibli"
    description: str = "Studio Ghibli aesthetic"

    characters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    environment: Dict[str, Any] = field(default_factory=dict)
    technical: Dict[str, Any] = field(default_factory=dict)
```

**Fields:**
- `characters`: Dictionary of character definitions
- `environment`: Environment and setting descriptions
- `technical`: Technical specifications (fps, motion, etc.)

**Example:**
```python
style = StyleConfig(
    name="cyberpunk",
    characters={
        "hacker": {
            "appearance": "Young hacker with neon tattoos",
            "motion": "Quick, nervous movements"
        }
    },
    environment={
        "lighting": "Neon city lights",
        "setting": "Dark alley in futuristic city"
    },
    technical={
        "motion_style": "Jittery, digital effects"
    }
)
```

## VideoProvider Protocol

Interface that all video providers must implement.

```python
@runtime_checkable
class VideoProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def supported_aspect_ratios(self) -> List[str]: ...

    @property
    def max_duration(self) -> int: ...

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult: ...

    def estimate_cost(self, duration_seconds: int) -> float: ...
```

## PromptEngine

Handles prompt enhancement for consistency.

```python
class PromptEngine:
    def __init__(self, style_config: StyleConfig): ...

    def create_prompt(self, concept: str, action: str, mood: str = "magical", include_style: bool = True) -> str: ...

    def create_negative_prompt(self) -> str: ...
```

## VideoTemplate

Reusable template for video generation.

```python
@dataclass
class VideoTemplate:
    name: str
    description: str
    duration: int = 8
    mood: str = "magical"
    style: str = "ghibli"
    prompt_template: str = "A scene showing {action}. {style_description}"
    variables: Dict[str, Any] = field(default_factory=dict)

    def render_prompt(self, **kwargs) -> str: ...
```

## BaseVideoProvider

Base class for implementing new providers.

```python
class BaseVideoProvider(ABC):
    def __init__(self, api_key: Optional[str] = None, **kwargs): ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def supported_aspect_ratios(self) -> List[str]: ...

    @property
    def max_duration(self) -> int: ...

    @abstractmethod
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult: ...

    def estimate_cost(self, duration_seconds: int) -> float: ...
```

## Exception Types

Ministudio uses standard Python exceptions. Provider-specific errors are included in `VideoGenerationResult.error`.

## Constants

- `DEFAULT_OUTPUT_DIR = "./ministudio_output"`
- `DEFAULT_DURATION = 8`
- `DEFAULT_ASPECT_RATIO = "16:9"`

## Examples

### Basic Generation

```python
import asyncio
from ministudio import Ministudio

async def generate():
    provider = Ministudio.create_provider("mock")
    studio = Ministudio(provider=provider)

    result = await studio.generate_concept_video(
        concept="Space",
        action="rocket launching into stars"
    )

    print(f"Success: {result.success}")
    print(f"Path: {result.video_path}")
    print(f"Time: {result.generation_time}s")

asyncio.run(generate())
```

### With Style

```python
from ministudio.styles import cinematic_style

studio = Ministudio(
    provider=provider,
    style_config=cinematic_style
)

result = await studio.generate_concept_video(
    concept="Battle",
    action="warrior charging into combat"
)
```

### Template Usage

```python
from ministudio.templates import explainer_template

result = await studio.generate_concept_video(
    concept="Quantum Physics",
    action="particles interacting",
    template=explainer_template
)
```

## See Also

- [Installation Guide](installation.md)
- [Quick Start](quickstart.md)
- [Provider Documentation](providers.md)
- [Examples](examples.md)
