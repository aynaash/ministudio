# MiniStudio: Secrets, Config & Multi-Model Integration Guide

**Programmable, Secure, Provider-Agnostic Video Generation**

---

## Table of Contents
1. [Principles](#principles)
2. [Secrets Management](#secrets-management)
3. [Multi-Model Integration Guide](#multi-model-integration-guide)
4. [Config & Prompt Compilation](#config--prompt-compilation)
5. [Developer & Contributor Tips](#developer--contributor-tips)
6. [Pre-Configured Adapters](#pre-configured-adapters)

---

## Principles

Before implementation, understand MiniStudio's design philosophy:

1. **Provider-Agnostic**: MiniStudio works with any model—Hugging Face, open-source, cloud-hosted, or local.
2. **Secure Secrets**: API keys, tokens, and credentials must never be hard-coded. Use secret managers.
3. **Flexible Configs**: Users can define provider settings via `.env`, config files, environment variables, or secret managers.
4. **Runtime Hot-Swapping**: Users can switch models at runtime without code changes.
5. **Fallback Chains**: Local models → Cloud APIs → Fallbacks ensure the framework doesn't break.

---

## Secrets Management

### 2.1 Recommended: Doppler

[Doppler](https://www.doppler.com/) is a multi-platform secret manager that keeps credentials out of code and version control.

**Example `.env` style config in Doppler**:

```env
VERTEX_AI_API_KEY=xxxx
GOOGLE_TTS_KEY=xxxx
HF_API_TOKEN=xxxx
AWS_ACCESS_KEY_ID=xxxx
AWS_SECRET_ACCESS_KEY=xxxx
OPENAI_API_KEY=xxxx
SORA_API_KEY=xxxx
```

**Usage in MiniStudio**:

```bash
# Install Doppler CLI: https://www.doppler.com/docs/cli
doppler run -- python examples/contextbytes_brand_story.py
```

**Benefits**:
- Works across dev, staging, and production environments
- Integrates with CI/CD pipelines (GitHub Actions, GitLab CI, etc.)
- Audit trails for who accessed what credentials
- Zero risk of accidental commits

---

### 2.2 Fallback: Environment Variables & `.env`

Create a `.env` file in your project root (add to `.gitignore`):

```env
# Video Generation Providers
VERTEX_AI_API_KEY=your-vertex-ai-key
HF_API_TOKEN=your-huggingface-token
LOCAL_MODEL_PATH=/models/stable-diffusion
SORA_API_KEY=your-sora-key

# Cloud Services
AWS_ACCESS_KEY_ID=xxxx
AWS_SECRET_ACCESS_KEY=xxxx
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Optional: Custom Endpoints
CUSTOM_PROVIDER_URL=http://localhost:8000
```

**Load in Python**:

```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access variables
hf_token = os.getenv("HF_API_TOKEN")
local_model_path = os.getenv("LOCAL_MODEL_PATH")
vertex_key = os.getenv("VERTEX_AI_API_KEY")
```

**Installation**:

```bash
pip install python-dotenv
```

**Security**: Always add `.env` to `.gitignore`:

```gitignore
.env
.env.local
.env.*.local
*.pem
service-account.json
```

---

### 2.3 Cloud Secret Managers

For production deployments, use dedicated secret managers:

#### **GCP Secret Manager**

```python
from google.cloud import secretmanager

class GCPSecretProvider:
    """Access secrets from GCP Secret Manager"""
    
    def __init__(self, project_id: str):
        self.client = secretmanager.SecretManagerServiceClient()
        self.project_id = project_id

    def get_secret(self, secret_name: str) -> str:
        """Fetch a secret by name"""
        secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
        response = self.client.access_secret_version(request={"name": secret_path})
        return response.payload.data.decode("UTF-8")

# Usage
gcp_provider = GCPSecretProvider("my-project-id")
vertex_key = gcp_provider.get_secret("VERTEX_AI_API_KEY")
```

#### **AWS Secrets Manager**

```python
import boto3
import json

class AWSSecretProvider:
    """Access secrets from AWS Secrets Manager"""
    
    def __init__(self, region: str = "us-east-1"):
        self.client = boto3.client("secretsmanager", region_name=region)

    def get_secret(self, secret_name: str) -> dict:
        """Fetch a secret (usually JSON)"""
        response = self.client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])

# Usage
aws_provider = AWSSecretProvider()
secrets = aws_provider.get_secret("ministudio/prod")
hf_token = secrets["HF_API_TOKEN"]
```

#### **Azure Key Vault**

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

class AzureSecretProvider:
    """Access secrets from Azure Key Vault"""
    
    def __init__(self, vault_url: str):
        self.client = SecretClient(vault_url=vault_url, credential=DefaultAzureCredential())

    def get_secret(self, secret_name: str) -> str:
        """Fetch a secret"""
        return self.client.get_secret(secret_name).value

# Usage
azure_provider = AzureSecretProvider("https://my-vault.vault.azure.net/")
vertex_key = azure_provider.get_secret("VERTEX-AI-API-KEY")
```

---

## Multi-Model Integration Guide

MiniStudio's `BaseVideoProvider` architecture allows seamless integration with any video generation model. Follow these patterns for common model types.

### 3.1 Hugging Face Models

**Models to Consider**:
- `damo-vilab/text-to-video-ms-1.7b` (Open-source)
- `modelscope/text-to-video-ms-1.7b` (Alternative)
- Community LoRAs for style/character control

**Implementation**:

```python
from ministudio.providers.base import BaseVideoProvider
from ministudio.interfaces import VideoGenerationRequest, VideoGenerationResult
from diffusers import DiffusionPipeline
import torch

class HuggingFaceVideoProvider(BaseVideoProvider):
    """Generate videos using Hugging Face models"""
    
    def __init__(self, model_name: str, token: str):
        super().__init__(api_key=token)
        self.model_name = model_name
        self.token = token
        # Load model once to avoid repeated downloads
        self.pipeline = DiffusionPipeline.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            use_auth_token=token
        ).to("cuda")

    @property
    def name(self) -> str:
        return f"huggingface_{self.model_name.split('/')[-1]}"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video from text prompt"""
        try:
            video = self.pipeline(
                prompt=request.prompt,
                height=512,
                width=512,
                num_frames=int(request.duration_seconds * 8),  # ~8fps
                num_inference_steps=30
            )
            # Convert to bytes
            video_bytes = self._export_to_bytes(video.frames)
            return VideoGenerationResult(
                video_bytes=video_bytes,
                format="mp4",
                duration_seconds=request.duration_seconds
            )
        except Exception as e:
            raise RuntimeError(f"HF generation failed: {str(e)}")

    def _export_to_bytes(self, frames):
        """Helper: Convert frame list to video bytes"""
        # Implementation depends on video format
        pass
```

**Usage**:

```python
from ministudio import VideoOrchestrator

provider = HuggingFaceVideoProvider(
    model_name="damo-vilab/text-to-video-ms-1.7b",
    token=os.getenv("HF_API_TOKEN")
)
orchestrator = VideoOrchestrator(provider)
```

---

### 3.2 Local Models

**Advantages**:
- Zero API costs
- Full control over inference
- Privacy (no data leaves your machine)

**Models**:
- CogVideo (local inference)
- Stable Video Diffusion (SVD)
- AnimateAnything

**Implementation**:

```python
from ministudio.providers.base import BaseVideoProvider
import torch
from pathlib import Path

class LocalVideoProvider(BaseVideoProvider):
    """Generate videos using locally-hosted models"""
    
    def __init__(self, model_path: str, device: str = "cuda"):
        super().__init__()
        self.model_path = Path(model_path)
        self.device = device
        # Load model once to avoid reload overhead
        self.model = self._load_model()

    def _load_model(self):
        """Load model from disk (implementation-specific)"""
        # Example: Load from checkpoint
        from diffusers import DiffusionPipeline
        return DiffusionPipeline.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16
        ).to(self.device)

    @property
    def name(self) -> str:
        return f"local_{self.model_path.name}"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video from prompt"""
        with torch.no_grad():
            output = self.model(
                prompt=request.prompt,
                height=512,
                width=512,
                num_frames=int(request.duration_seconds * 8)
            )
        video_bytes = self._export_to_bytes(output.frames)
        return VideoGenerationResult(
            video_bytes=video_bytes,
            format="mp4",
            duration_seconds=request.duration_seconds
        )

    def estimate_cost(self, duration_seconds: int) -> float:
        """Local inference is free"""
        return 0.0
```

**Usage**:

```python
provider = LocalVideoProvider(
    model_path="/models/stable-video-diffusion",
    device="cuda"
)
orchestrator = VideoOrchestrator(provider)
```

**Tip**: Use shared memory or model caching to avoid repeated loads in batch processing:

```python
import gc

class CachedLocalVideoProvider(LocalVideoProvider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generation_cache = {}

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        # Cache based on prompt hash
        prompt_hash = hash(request.prompt)
        if prompt_hash in self._generation_cache:
            return self._generation_cache[prompt_hash]
        
        result = await super().generate_video(request)
        self._generation_cache[prompt_hash] = result
        
        # Clean cache if too large
        if len(self._generation_cache) > 10:
            self._generation_cache.clear()
            gc.collect()
        
        return result
```

---

### 3.3 Cloud-Hosted Models (GCP Vertex AI / AWS SageMaker / Azure OpenAI)

**Advantages**:
- Managed infrastructure
- Auto-scaling
- No local compute required

#### **GCP Vertex AI (Veo 3.1)**

```python
from ministudio.providers.base import BaseVideoProvider
from google.cloud import aiplatform
import asyncio

class VertexAIVideoProvider(BaseVideoProvider):
    """Generate videos using Google Cloud Vertex AI"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        super().__init__()
        self.project_id = project_id
        self.location = location
        aiplatform.init(project=project_id, location=location)

    @property
    def name(self) -> str:
        return "vertex_ai_veo"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Generate video via Vertex AI"""
        # This is a simplified example; actual Vertex AI API may differ
        loop = asyncio.get_event_loop()
        job = await loop.run_in_executor(
            None,
            self._submit_generation_job,
            request.prompt,
            request.duration_seconds
        )
        
        # Poll for completion
        result = await self._poll_job(job)
        return result

    def _submit_generation_job(self, prompt: str, duration: int):
        """Submit generation job to Vertex AI"""
        # Implementation details depend on Vertex AI SDK
        pass

    async def _poll_job(self, job):
        """Poll job until completion"""
        while True:
            status = job.check_status()
            if status == "COMPLETED":
                return VideoGenerationResult(
                    video_bytes=job.get_output(),
                    format="mp4",
                    duration_seconds=job.duration
                )
            elif status == "FAILED":
                raise RuntimeError(f"Job failed: {job.error}")
            await asyncio.sleep(5)  # Poll every 5 seconds

    def estimate_cost(self, duration_seconds: int) -> float:
        """Estimate cost for Vertex AI"""
        # Pricing: $0.10 per video (example)
        return 0.10
```

#### **AWS SageMaker**

```python
import boto3
import json
import time

class SageMakerVideoProvider(BaseVideoProvider):
    """Generate videos using AWS SageMaker"""
    
    def __init__(self, region: str = "us-east-1", endpoint_name: str = "video-generator"):
        super().__init__()
        self.sagemaker_client = boto3.client("sagemaker-runtime", region_name=region)
        self.endpoint_name = endpoint_name

    @property
    def name(self) -> str:
        return "sagemaker_video"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Invoke SageMaker endpoint"""
        payload = {
            "prompt": request.prompt,
            "duration_seconds": request.duration_seconds,
            "width": 512,
            "height": 512
        }
        
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload)
        )
        
        video_bytes = response["Body"].read()
        return VideoGenerationResult(
            video_bytes=video_bytes,
            format="mp4",
            duration_seconds=request.duration_seconds
        )
```

#### **Azure OpenAI / Custom Endpoint**

```python
import httpx

class CustomEndpointProvider(BaseVideoProvider):
    """Generate videos via custom HTTP endpoint"""
    
    def __init__(self, endpoint_url: str, api_key: str):
        super().__init__(api_key=api_key)
        self.endpoint_url = endpoint_url

    @property
    def name(self) -> str:
        return "custom_endpoint"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        """Call custom endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint_url}/generate",
                json={
                    "prompt": request.prompt,
                    "duration": request.duration_seconds
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            return VideoGenerationResult(
                video_bytes=response.content,
                format="mp4",
                duration_seconds=request.duration_seconds
            )
```

---

## Config & Prompt Compilation

### 4.1 Central Config Strategy

Keep all provider configuration in one place:

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class ProviderConfig:
    """Configuration for a specific provider"""
    name: str  # "vertex_ai", "huggingface", "local", etc.
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    model_name: Optional[str] = None
    model_path: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VideoConfig:
    """Master configuration for video generation"""
    provider: ProviderConfig
    tts_provider: ProviderConfig
    
    # Visual anchors
    character_visual_anchors: Dict[str, str] = field(default_factory=dict)
    environment_visual_anchor: Optional[str] = None
    
    # Generation settings
    width: int = 512
    height: int = 512
    fps: int = 8
    
    # Style & creativity
    style: str = "cinematic"  # "cinematic", "cyberpunk", "ghibli", "realistic"
    temperature: float = 0.7
    
    # Advanced
    continuity_enabled: bool = True
    quality_preset: str = "high"  # "fast", "balanced", "high"
```

### 4.2 Provider Factory Pattern

Dynamically instantiate providers from config:

```python
from ministudio.providers import (
    VertexAIProvider, 
    HuggingFaceVideoProvider,
    LocalVideoProvider,
    CustomEndpointProvider
)

class ProviderFactory:
    """Factory for creating providers from config"""
    
    PROVIDERS = {
        "vertex_ai": VertexAIProvider,
        "huggingface": HuggingFaceVideoProvider,
        "local": LocalVideoProvider,
        "custom": CustomEndpointProvider,
    }

    @staticmethod
    def create_provider(config: ProviderConfig) -> BaseVideoProvider:
        """Create provider instance from config"""
        provider_class = ProviderFactory.PROVIDERS.get(config.name)
        
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.name}")
        
        # Build kwargs from config
        kwargs = {
            "api_key": config.api_key,
            **config.options
        }
        
        if config.model_name:
            kwargs["model_name"] = config.model_name
        if config.model_path:
            kwargs["model_path"] = config.model_path
        if config.api_endpoint:
            kwargs["endpoint_url"] = config.api_endpoint
        
        return provider_class(**kwargs)
```

### 4.3 Prompt Compilation

Compile MiniStudio configs into provider-specific prompts:

```python
class PromptCompiler:
    """Compile MiniStudio shot configs into model-specific prompts"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
    
    def compile(self, shot_config, video_config: VideoConfig) -> str:
        """Generate final prompt for model"""
        # Base prompt from shot action
        prompt_parts = [shot_config.action_description]
        
        # Add style information
        if video_config.style:
            prompt_parts.append(f"Style: {video_config.style}")
        
        # Include character visual anchors
        for char_name, anchor_path in video_config.character_visual_anchors.items():
            prompt_parts.append(f"Character '{char_name}' inspired by: {anchor_path}")
        
        # Include environment context
        if video_config.environment_visual_anchor:
            prompt_parts.append(f"Background inspired by: {video_config.environment_visual_anchor}")
        
        # Camera direction
        if hasattr(shot_config, "camera_movement"):
            prompt_parts.append(f"Camera: {shot_config.camera_movement}")
        
        # Lighting
        if hasattr(shot_config, "lighting"):
            prompt_parts.append(f"Lighting: {shot_config.lighting}")
        
        # Model-specific optimizations
        if self.provider_name == "vertex_ai":
            return self._optimize_for_vertex(", ".join(prompt_parts))
        elif self.provider_name == "huggingface":
            return self._optimize_for_huggingface(", ".join(prompt_parts))
        elif self.provider_name == "local":
            return self._optimize_for_local(", ".join(prompt_parts))
        
        return ", ".join(prompt_parts)
    
    def _optimize_for_vertex(self, prompt: str) -> str:
        """Optimize prompt for Vertex AI Veo"""
        # Vertex AI prefers detailed, structured prompts
        return f"{prompt}. High quality cinematic render."
    
    def _optimize_for_huggingface(self, prompt: str) -> str:
        """Optimize prompt for HF models"""
        # HF models work better with simpler, shorter prompts
        return prompt[:150]  # Truncate to 150 chars
    
    def _optimize_for_local(self, prompt: str) -> str:
        """Optimize prompt for local models"""
        # Local models often need explicit quality directives
        return f"{prompt}. Best quality, 4k resolution."
```

**Usage**:

```python
config = VideoConfig(
    provider=ProviderConfig(name="vertex_ai", api_key=os.getenv("VERTEX_AI_API_KEY")),
    character_visual_anchors={"Emma": "emma_reference.jpg"},
    style="cinematic"
)

compiler = PromptCompiler("vertex_ai")
shot_prompt = compiler.compile(shot_config, config)
```

---

## Developer & Contributor Tips

### Best Practices for Adding Providers

1. **Always inherit from `BaseVideoProvider`**
   ```python
   class MyNewProvider(BaseVideoProvider):
       @property
       def name(self) -> str:
           return "my_provider"
   ```

2. **Implement `generate_video()`**
   - Handle API authentication
   - Implement error handling and retries
   - Return `VideoGenerationResult` with proper metadata

3. **Support cost estimation**
   ```python
   def estimate_cost(self, duration_seconds: int) -> float:
       # Return estimated cost in USD
       return duration_seconds * 0.01  # Example: $0.01/sec
   ```

4. **Add logging for debugging**
   ```python
   import logging
   logger = logging.getLogger(__name__)
   
   logger.info(f"Generating video: {request.prompt[:50]}...")
   logger.debug(f"Using model: {self.model_name}")
   ```

5. **Implement graceful fallbacks**
   ```python
   async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
       try:
           # Try primary approach
           return await self._generate_with_advanced_features(request)
       except Exception as e:
           logger.warning(f"Advanced generation failed, falling back: {e}")
           # Fall back to simpler approach
           return await self._generate_basic(request)
   ```

### Hot-Swapping Providers at Runtime

```python
async def generate_scene_with_fallback(orchestrator, scene_config):
    """Try primary provider, fall back to secondary"""
    providers = [
        VertexAIProvider(os.getenv("VERTEX_AI_API_KEY")),
        HuggingFaceVideoProvider("model-name", os.getenv("HF_API_TOKEN")),
    ]
    
    for provider in providers:
        try:
            orchestrator.provider = provider
            logger.info(f"Attempting with {provider.name}...")
            return await orchestrator.generate_scene(scene_config)
        except Exception as e:
            logger.warning(f"{provider.name} failed: {e}. Trying next...")
    
    raise RuntimeError("All providers failed")
```

### Testing Providers

```python
# In tests/test_providers.py
from ministudio.providers import LocalVideoProvider
from ministudio.interfaces import VideoGenerationRequest

@pytest.mark.asyncio
async def test_local_provider_generation():
    provider = LocalVideoProvider("/path/to/model")
    request = VideoGenerationRequest(
        prompt="A scientist in a lab",
        duration_seconds=5
    )
    result = await provider.generate_video(request)
    assert result.video_bytes is not None
    assert len(result.video_bytes) > 0
```

---

## Pre-Configured Adapters

MiniStudio provides a folder of pre-built adapters for common models. Just add credentials and go.

### Structure

```
ministudio/adapters/
├── __init__.py
├── huggingface_adapter.py      # HF models (SD, CogVideo, etc.)
├── vertex_ai_adapter.py        # GCP Vertex AI Veo
├── aws_sagemaker_adapter.py    # AWS SageMaker endpoints
├── azure_openai_adapter.py     # Azure OpenAI + custom
├── local_model_adapter.py      # Local inference (SDXL, SVD, etc.)
└── README.md                   # Setup instructions
```

### Example: Hugging Face Adapter

```python
# ministudio/adapters/huggingface_adapter.py
"""Pre-configured Hugging Face video generation adapter"""

from ministudio.providers import HuggingFaceVideoProvider
import os

class HFAdapter:
    """Simplified setup for Hugging Face models"""
    
    RECOMMENDED_MODELS = {
        "text-to-video": "damo-vilab/text-to-video-ms-1.7b",
        "fast": "modelscope/text-to-video-ms-1.7b",
        "quality": "damo-vilab/text-to-video-ms-1.7b",
    }
    
    @staticmethod
    def create(model_type: str = "text-to-video") -> HuggingFaceVideoProvider:
        """Create provider with minimal config"""
        model_name = HFAdapter.RECOMMENDED_MODELS.get(
            model_type,
            HFAdapter.RECOMMENDED_MODELS["text-to-video"]
        )
        return HuggingFaceVideoProvider(
            model_name=model_name,
            token=os.getenv("HF_API_TOKEN")
        )

# Usage
from ministudio.adapters.huggingface_adapter import HFAdapter

provider = HFAdapter.create("quality")
```

### Getting Started with Adapters

1. **Copy the adapter file** for your provider
2. **Add your credentials** to `.env`
3. **Import and instantiate**:

```python
from ministudio.adapters.vertex_ai_adapter import VertexAIAdapter

provider = VertexAIAdapter.create()
orchestrator = VideoOrchestrator(provider)
```

---

## Summary & Next Steps

| Task | Recommendation |
|------|---|
| **Secrets Management** | Use Doppler for production, `.env` for local dev |
| **Provider Selection** | Start with Vertex AI (cloud) or HF (local) |
| **Config Management** | Use `ProviderConfig` + `ProviderFactory` |
| **Prompt Optimization** | Use `PromptCompiler` for model-specific tweaks |
| **Contributing** | Follow the provider template and add tests |

For questions, see [CONTRIBUTING.md](../CONTRIBUTING.md) and [ROADMAP.md](../ROADMAP.md).

