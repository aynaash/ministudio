"""
Local Model Adapter

Pre-configured adapter for locally-hosted models.

Setup:
    1. Download a model (e.g., from Hugging Face)
    2. Set LOCAL_MODEL_PATH environment variable
    3. Create provider:
        from ministudio.adapters import LocalModelAdapter
        provider = LocalModelAdapter.create()
    4. Use with orchestrator:
        orchestrator = VideoOrchestrator(provider)
"""

import os
from pathlib import Path
from typing import Optional
from ..providers.local import LocalVideoProvider


class LocalModelAdapter:
    """Simplified local model provider setup"""
    
    @staticmethod
    def create(
        model_path: Optional[str] = None,
        device: str = "cuda",
        **kwargs
    ) -> LocalVideoProvider:
        """
        Create local model provider with minimal configuration.
        
        Args:
            model_path: Path to local model (defaults to LOCAL_MODEL_PATH env var)
            device: Device to use ('cuda', 'cpu', 'mps')
            **kwargs: Additional options
        
        Returns:
            Configured LocalVideoProvider instance
        
        Example:
            # Use environment variable
            provider = LocalModelAdapter.create()
            
            # Use explicit path
            provider = LocalModelAdapter.create(
                model_path="/models/stable-diffusion-v1.5",
                device="cuda"
            )
        """
        if not model_path:
            model_path = os.getenv("LOCAL_MODEL_PATH")
            if not model_path:
                raise ValueError(
                    "model_path must be provided or set LOCAL_MODEL_PATH environment variable"
                )
        
        # Verify path exists
        model_dir = Path(model_path)
        if not model_dir.exists():
            raise FileNotFoundError(
                f"Model path does not exist: {model_path}\n"
                "Download a model from Hugging Face or update LOCAL_MODEL_PATH"
            )
        
        return LocalVideoProvider(
            model_path=str(model_path),
            device=device,
            **kwargs
        )
    
    @staticmethod
    def get_setup_instructions() -> str:
        """Return setup instructions for local models"""
        return """
=== Local Model Setup Instructions ===

1. Choose a model from Hugging Face:
   - Text-to-Video: damo-vilab/text-to-video-ms-1.7b
   - Stable Video: stabilityai/stable-video-diffusion-img2vid
   - CogVideo: THUDM/CogVideoX-2B (fast) or THUDM/CogVideoX-5B (quality)

2. Download the model:
   
   Option A: Using Hugging Face CLI
   huggingface-cli download damo-vilab/text-to-video-ms-1.7b --local-dir ./models/text-to-video
   
   Option B: Programmatically
   from diffusers import DiffusionPipeline
   pipe = DiffusionPipeline.from_pretrained("damo-vilab/text-to-video-ms-1.7b")
   pipe.save_pretrained("./models/text-to-video")
   
   Option C: Manual download
   Download from https://huggingface.co/damo-vilab/text-to-video-ms-1.7b
   and extract to your models directory

3. Set environment variable in .env:
   LOCAL_MODEL_PATH=/path/to/model
   
   Example:
   LOCAL_MODEL_PATH=/models/text-to-video-ms-1.7b

4. Usage:
   from ministudio.adapters import LocalModelAdapter
   provider = LocalModelAdapter.create()

5. System Requirements:
   - GPU with 10GB+ VRAM (for 512x512 videos)
   - 20GB+ VRAM recommended for quality models
   - NVIDIA GPU recommended (CUDA 11.8+)
   - AMD GPU supported (ROCm 5.4+)
   - Intel Arc supported (Intel oneAPI)
   - CPU mode available but very slow

6. Installation:
   pip install torch diffusers transformers
   
   For GPU acceleration:
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

7. Performance Tips:
   - Use device="cuda" for fastest inference
   - Reduce num_inference_steps for faster generation (trade quality for speed)
   - Cache model in memory to avoid reload overhead
   - Use smaller models (2B) for faster testing, larger (5B) for quality

8. Model Download Sizes:
   - damo-vilab/text-to-video-ms-1.7b: ~5GB
   - stabilityai/stable-video-diffusion-img2vid: ~5GB
   - THUDM/CogVideoX-2B: ~7GB
   - THUDM/CogVideoX-5B: ~14GB
"""


# Aliases for convenience
create_local_model = LocalModelAdapter.create
