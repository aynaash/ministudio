"""
Hugging Face Adapter

Pre-configured adapter for Hugging Face models (text-to-video, diffusers, etc.).

Setup:
    1. Create a Hugging Face account: https://huggingface.co/join
    2. Get your API token: https://huggingface.co/settings/tokens
    3. Set HF_API_TOKEN environment variable
    4. Create provider:
        from ministudio.adapters import HuggingFaceAdapter
        provider = HuggingFaceAdapter.create("text-to-video")
    5. Use with orchestrator:
        orchestrator = VideoOrchestrator(provider)
"""

import os
from typing import Optional
from ..providers.local import HuggingFaceVideoProvider


class HuggingFaceAdapter:
    """Simplified Hugging Face provider setup"""
    
    # Recommended open-source models for different use cases
    RECOMMENDED_MODELS = {
        "text-to-video-fast": "modelscope/text-to-video-ms-1.7b",
        "text-to-video-quality": "damo-vilab/text-to-video-ms-1.7b",
        "text-to-video": "damo-vilab/text-to-video-ms-1.7b",  # Default
        "stable-video": "stabilityai/stable-video-diffusion-img2vid",
        "cogvideo-fast": "THUDM/CogVideoX-2B",
        "cogvideo-quality": "THUDM/CogVideoX-5B",
    }
    
    @staticmethod
    def create(
        model_type: str = "text-to-video",
        model_name: Optional[str] = None,
        token: Optional[str] = None,
        **kwargs
    ) -> HuggingFaceVideoProvider:
        """
        Create Hugging Face provider with minimal configuration.
        
        Args:
            model_type: Preset type ('text-to-video', 'text-to-video-fast', 'stable-video', etc.)
            model_name: Override with custom model ID (e.g., "stabilityai/stable-video-diffusion-img2vid")
            token: HF API token (defaults to HF_API_TOKEN env var)
            **kwargs: Additional options
        
        Returns:
            Configured HuggingFaceVideoProvider instance
        
        Example:
            # Use recommended model for text-to-video
            provider = HuggingFaceAdapter.create()
            
            # Use specific model
            provider = HuggingFaceAdapter.create("stable-video")
            
            # Use custom model
            provider = HuggingFaceAdapter.create(
                model_name="my-org/my-model"
            )
        """
        if not token:
            token = os.getenv("HF_API_TOKEN")
            if not token:
                raise ValueError(
                    "HF_API_TOKEN not found. Set it in .env or pass token parameter.\n"
                    "Get your token at: https://huggingface.co/settings/tokens"
                )
        
        # Resolve model name
        if not model_name:
            if model_type not in HuggingFaceAdapter.RECOMMENDED_MODELS:
                raise ValueError(
                    f"Unknown model type: {model_type}\n"
                    f"Available types: {list(HuggingFaceAdapter.RECOMMENDED_MODELS.keys())}"
                )
            model_name = HuggingFaceAdapter.RECOMMENDED_MODELS[model_type]
        
        return HuggingFaceVideoProvider(
            model_name=model_name,
            token=token,
            **kwargs
        )
    
    @staticmethod
    def list_available_models() -> dict:
        """Return available recommended models"""
        return HuggingFaceAdapter.RECOMMENDED_MODELS.copy()
    
    @staticmethod
    def get_setup_instructions() -> str:
        """Return setup instructions for Hugging Face"""
        return """
=== Hugging Face Setup Instructions ===

1. Create a Hugging Face account:
   https://huggingface.co/join

2. Get your API token:
   https://huggingface.co/settings/tokens
   (Click "New token" → Select "read" access)

3. Add to .env:
   HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

4. Accept model licenses:
   For text-to-video models, visit the model page and click "Accept"
   - https://huggingface.co/damo-vilab/text-to-video-ms-1.7b
   - https://huggingface.co/modelscope/text-to-video-ms-1.7b

5. Usage:
   from ministudio.adapters import HuggingFaceAdapter
   
   # Use default (recommended)
   provider = HuggingFaceAdapter.create()
   
   # Use specific model
   provider = HuggingFaceAdapter.create("stable-video")

6. Available Models:
   - text-to-video: High quality (default)
   - text-to-video-fast: Faster inference
   - stable-video: Stable Video Diffusion (img2vid)
   - cogvideo-fast: CogVideoX (2B, fast)
   - cogvideo-quality: CogVideoX (5B, high quality)

7. System Requirements:
   - GPU with at least 10GB VRAM (for 512x512 videos)
   - 20GB+ VRAM recommended for quality models
   - CUDA/ROCm for GPU acceleration

8. Installation:
   pip install diffusers transformers torch
"""


# Aliases for convenience
create_huggingface = HuggingFaceAdapter.create
list_hf_models = HuggingFaceAdapter.list_available_models
