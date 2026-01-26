# MiniStudio Provider Adapters

Quick-start adapters for common video generation providers. Just add credentials and go.

## Overview

These adapters provide sensible defaults and simplified setup for popular video generation services:

| Provider | Use Case | Requirements | Setup Time |
|----------|----------|--------------|-----------|
| **Vertex AI** | Cloud, production | GCP account + API key | 5 min |
| **Hugging Face** | Cloud or local, flexible | HF token | 5 min |
| **Local Models** | Free, private, full control | GPU + disk space | 10 min |
| **Custom Endpoint** | Self-hosted or third-party | Endpoint URL + API key | 5 min |

---

## Quick Start

### 1. Vertex AI (Recommended for Production)

```python
from ministudio.adapters import VertexAIAdapter

# Create provider (requires VERTEX_AI_PROJECT_ID)
provider = VertexAIAdapter.create(project_id="my-gcp-project")
```

**Setup:** [See VertexAIAdapter.get_setup_instructions()](vertex_ai_adapter.py#L47)

### 2. Hugging Face (Recommended for Development)

```python
from ministudio.adapters import HuggingFaceAdapter

# Create provider with recommended model
provider = HuggingFaceAdapter.create()

# Or choose a specific model
provider = HuggingFaceAdapter.create("text-to-video-fast")
provider = HuggingFaceAdapter.create("stable-video")
provider = HuggingFaceAdapter.create("cogvideo-quality")
```

**Setup:** [See HuggingFaceAdapter.get_setup_instructions()](huggingface_adapter.py#L73)

### 3. Local Models (Free & Private)

```python
from ministudio.adapters import LocalModelAdapter

# Create provider (requires LOCAL_MODEL_PATH)
provider = LocalModelAdapter.create()

# Or use explicit path
provider = LocalModelAdapter.create(model_path="/models/text-to-video-ms-1.7b")
```

**Setup:** [See LocalModelAdapter.get_setup_instructions()](local_model_adapter.py#L54)

---

## Full Usage Example

```python
import asyncio
from ministudio import VideoOrchestrator
from ministudio.adapters import VertexAIAdapter
from ministudio.config import ShotConfig

async def generate_cinematic_shot():
    # Create provider
    provider = VertexAIAdapter.create(project_id="my-project")
    
    # Create orchestrator
    orchestrator = VideoOrchestrator(provider)
    
    # Define a shot
    shot = ShotConfig(
        action_description="A lone researcher discovers a glowing orb.",
        characters={"Emma": "emma_reference.jpg"},
        duration_seconds=8,
        style="cinematic"
    )
    
    # Generate
    result = await orchestrator.generate_shot(shot)
    print(f"Generated video: {result.video_path}")

# Run
asyncio.run(generate_cinematic_shot())
```

---

## Adapter API Reference

### VertexAIAdapter

```python
from ministudio.adapters import VertexAIAdapter

# Create with defaults
provider = VertexAIAdapter.create(project_id="my-project")

# Get setup instructions
print(VertexAIAdapter.get_setup_instructions())
```

### HuggingFaceAdapter

```python
from ministudio.adapters import HuggingFaceAdapter

# List available models
models = HuggingFaceAdapter.list_available_models()
print(models)

# Create with model type
provider = HuggingFaceAdapter.create(model_type="text-to-video-fast")

# Get setup instructions
print(HuggingFaceAdapter.get_setup_instructions())
```

### LocalModelAdapter

```python
from ministudio.adapters import LocalModelAdapter

# Create with environment variable
provider = LocalModelAdapter.create()

# Or with explicit path
provider = LocalModelAdapter.create(
    model_path="/models/stable-video-diffusion",
    device="cuda"
)

# Get setup instructions
print(LocalModelAdapter.get_setup_instructions())
```

---

## Advanced: Custom Adapters

Want to add support for another provider? Follow this pattern:

```python
from ministudio.providers.base import BaseVideoProvider

class MyCustomAdapter:
    """Adapter for MyCustomProvider"""
    
    @staticmethod
    def create(api_key=None, endpoint=None, **kwargs):
        if not api_key:
            api_key = os.getenv("MY_CUSTOM_API_KEY")
        
        return MyCustomProvider(
            api_key=api_key,
            endpoint=endpoint,
            **kwargs
        )
```

Then submit a PR to add it to MiniStudio!

---

## Environment Variables

See [.env.example](../../.env.example) for a complete list of supported environment variables.

Key variables for adapters:
- `VERTEX_AI_PROJECT_ID` / `GCP_PROJECT_ID`
- `HF_API_TOKEN`
- `LOCAL_MODEL_PATH`
- `GOOGLE_APPLICATION_CREDENTIALS`

---

## Troubleshooting

### "API key not found"
- Check that your `.env` file exists in the project root
- Verify the environment variable name matches
- For Doppler: `doppler run -- python your_script.py`

### "Model not found"
- For HF models: Verify you've accepted the license at the model page
- For local models: Ensure the directory path is correct and contains model files
- Use `LocalModelAdapter.get_setup_instructions()` for download help

### "Out of memory"
- Use smaller models (`-2B` instead of `-5B`)
- Reduce resolution or duration
- Use CPU-based inference (slower but uses less VRAM)

---

## Contributing

Found a great provider? Want to add an adapter?

1. Create a new `your_provider_adapter.py` in this directory
2. Inherit from `BaseVideoProvider`
3. Implement the adapter following the pattern above
4. Add setup instructions and tests
5. Submit a PR!

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.
