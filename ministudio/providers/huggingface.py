"""
HuggingFace Video Generation Provider
=====================================
Video generation using open-source models from HuggingFace.

Supported Models:
- Stable Video Diffusion (SVD)
- AnimateDiff
- CogVideo / CogVideoX
- Open-Sora
- ModelScope Text-to-Video

Setup:
    pip install diffusers transformers torch accelerate
    
For GPU acceleration:
    pip install torch --index-url https://download.pytorch.org/whl/cu118

Environment Variables:
    HF_TOKEN - HuggingFace access token (for gated models)
    HF_HOME - HuggingFace cache directory
"""

import os
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import tempfile

from .base import BaseVideoProvider

logger = logging.getLogger(__name__)


class HFVideoModel(Enum):
    """Available HuggingFace video models."""
    
    # Stable Video Diffusion
    SVD = "stabilityai/stable-video-diffusion-img2vid"
    SVD_XT = "stabilityai/stable-video-diffusion-img2vid-xt"
    
    # AnimateDiff
    ANIMATEDIFF = "guoyww/animatediff-motion-adapter-v1-5-2"
    ANIMATEDIFF_LIGHTNING = "ByteDance/AnimateDiff-Lightning"
    
    # CogVideo
    COGVIDEO = "THUDM/CogVideoX-2b"
    COGVIDEO_5B = "THUDM/CogVideoX-5b"
    
    # Open-Sora
    OPEN_SORA = "hpcai-tech/Open-Sora"
    
    # ModelScope
    MODELSCOPE_T2V = "damo-vilab/text-to-video-ms-1.7b"
    
    # Zeroscope (lightweight)
    ZEROSCOPE = "cerspense/zeroscope_v2_576w"
    ZEROSCOPE_XL = "cerspense/zeroscope_v2_XL"


@dataclass
class HFVideoConfig:
    """Configuration for HuggingFace video provider."""
    
    model: Union[HFVideoModel, str] = HFVideoModel.ZEROSCOPE
    
    # Generation settings
    num_frames: int = 24
    width: int = 576
    height: int = 320
    fps: int = 8
    num_inference_steps: int = 25
    guidance_scale: float = 7.5
    
    # Performance settings
    device: str = "auto"  # "cpu", "cuda", "mps", "auto"
    dtype: str = "float16"  # "float16", "float32", "bfloat16"
    enable_model_cpu_offload: bool = True
    enable_vae_slicing: bool = True
    
    # Output
    output_dir: str = "output/huggingface"
    output_format: str = "mp4"  # mp4, gif
    
    # HuggingFace settings
    hf_token: Optional[str] = None
    cache_dir: Optional[str] = None
    
    def get_model_id(self) -> str:
        """Get model ID string."""
        if isinstance(self.model, HFVideoModel):
            return self.model.value
        return self.model


@dataclass
class HFGenerationResult:
    """Result from HuggingFace generation."""
    
    success: bool
    video_path: Optional[str] = None
    frames_path: Optional[str] = None  # Directory with frames
    duration: float = 0.0
    prompt: str = ""
    model: str = ""
    generation_time: float = 0.0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class HuggingFaceProvider(BaseVideoProvider):
    """
    HuggingFace video generation provider.
    
    Supports multiple open-source video generation models.
    """
    
    provider_name = "huggingface"
    
    def __init__(self, config: Optional[HFVideoConfig] = None):
        self.config = config or HFVideoConfig()
        self._pipeline = None
        self._current_model = None
        
        # Get HF token from config or environment
        self.hf_token = self.config.hf_token or os.environ.get("HF_TOKEN")
        
        # Ensure output directory exists
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        
        # Detect device
        self.device = self._detect_device()
    
    def _detect_device(self) -> str:
        """Detect best available device."""
        if self.config.device != "auto":
            return self.config.device
        
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        
        return "cpu"
    
    def _load_pipeline(self, model_id: Optional[str] = None):
        """Load the video generation pipeline."""
        model_id = model_id or self.config.get_model_id()
        
        if self._pipeline is not None and self._current_model == model_id:
            return
        
        try:
            import torch
            from diffusers import DiffusionPipeline
            
            logger.info(f"Loading model: {model_id}")
            
            # Determine dtype
            if self.config.dtype == "float16":
                dtype = torch.float16
            elif self.config.dtype == "bfloat16":
                dtype = torch.bfloat16
            else:
                dtype = torch.float32
            
            # Load based on model type
            if "stable-video-diffusion" in model_id:
                self._load_svd_pipeline(model_id, dtype)
            elif "animatediff" in model_id.lower():
                self._load_animatediff_pipeline(model_id, dtype)
            elif "cogvideo" in model_id.lower():
                self._load_cogvideo_pipeline(model_id, dtype)
            elif "zeroscope" in model_id or "text-to-video" in model_id:
                self._load_text2video_pipeline(model_id, dtype)
            else:
                # Generic pipeline loading
                self._pipeline = DiffusionPipeline.from_pretrained(
                    model_id,
                    torch_dtype=dtype,
                    token=self.hf_token,
                    cache_dir=self.config.cache_dir
                )
            
            # Move to device
            if self.config.enable_model_cpu_offload and self.device == "cuda":
                self._pipeline.enable_model_cpu_offload()
            else:
                self._pipeline = self._pipeline.to(self.device)
            
            # Enable memory optimizations
            if self.config.enable_vae_slicing and hasattr(self._pipeline, 'enable_vae_slicing'):
                self._pipeline.enable_vae_slicing()
            
            self._current_model = model_id
            logger.info(f"Model loaded successfully on {self.device}")
            
        except ImportError as e:
            raise ImportError(
                f"Required packages not installed: {e}\n"
                "Install with: pip install diffusers transformers torch accelerate"
            )
        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise
    
    def _load_svd_pipeline(self, model_id: str, dtype):
        """Load Stable Video Diffusion pipeline."""
        from diffusers import StableVideoDiffusionPipeline
        
        self._pipeline = StableVideoDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            variant="fp16" if dtype != "float32" else None,
            token=self.hf_token,
            cache_dir=self.config.cache_dir
        )
    
    def _load_animatediff_pipeline(self, model_id: str, dtype):
        """Load AnimateDiff pipeline."""
        from diffusers import AnimateDiffPipeline, MotionAdapter, DDIMScheduler
        
        # Load motion adapter
        adapter = MotionAdapter.from_pretrained(
            model_id,
            torch_dtype=dtype,
            token=self.hf_token
        )
        
        # Create pipeline with SD base model
        self._pipeline = AnimateDiffPipeline.from_pretrained(
            "emilianJR/epiCRealism",  # Base SD model
            motion_adapter=adapter,
            torch_dtype=dtype,
            token=self.hf_token
        )
        
        self._pipeline.scheduler = DDIMScheduler.from_config(
            self._pipeline.scheduler.config,
            beta_schedule="linear"
        )
    
    def _load_cogvideo_pipeline(self, model_id: str, dtype):
        """Load CogVideoX pipeline."""
        from diffusers import CogVideoXPipeline
        
        self._pipeline = CogVideoXPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            token=self.hf_token,
            cache_dir=self.config.cache_dir
        )
    
    def _load_text2video_pipeline(self, model_id: str, dtype):
        """Load text-to-video pipeline (Zeroscope, ModelScope)."""
        from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
        
        self._pipeline = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=dtype,
            token=self.hf_token,
            cache_dir=self.config.cache_dir
        )
        
        # Use faster scheduler
        self._pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
            self._pipeline.scheduler.config
        )
    
    def is_available(self) -> bool:
        """Check if HuggingFace provider is available."""
        try:
            import torch
            import diffusers
            return True
        except ImportError:
            return False
    
    async def generate(
        self,
        prompt: str,
        duration: float = 3.0,
        **kwargs
    ) -> HFGenerationResult:
        """
        Generate video from text prompt.
        
        Args:
            prompt: Text description of the video
            duration: Target duration in seconds
            **kwargs: Additional parameters
        
        Returns:
            HFGenerationResult
        """
        start_time = time.time()
        
        try:
            # Load pipeline
            model_id = kwargs.get("model", self.config.get_model_id())
            self._load_pipeline(model_id)
            
            # Calculate frames from duration
            num_frames = kwargs.get("num_frames", int(duration * self.config.fps))
            num_frames = max(8, min(num_frames, 64))  # Clamp to reasonable range
            
            logger.info(f"Generating {num_frames} frames for: {prompt[:50]}...")
            
            # Generate based on model type
            if "stable-video-diffusion" in model_id:
                result = await self._generate_svd(prompt, num_frames, **kwargs)
            elif "animatediff" in model_id.lower():
                result = await self._generate_animatediff(prompt, num_frames, **kwargs)
            elif "cogvideo" in model_id.lower():
                result = await self._generate_cogvideo(prompt, num_frames, **kwargs)
            else:
                result = await self._generate_text2video(prompt, num_frames, **kwargs)
            
            generation_time = time.time() - start_time
            
            if result.get("success"):
                return HFGenerationResult(
                    success=True,
                    video_path=result.get("video_path"),
                    frames_path=result.get("frames_path"),
                    duration=num_frames / self.config.fps,
                    prompt=prompt,
                    model=model_id,
                    generation_time=generation_time,
                    metadata=result.get("metadata", {})
                )
            else:
                return HFGenerationResult(
                    success=False,
                    error=result.get("error", "Generation failed"),
                    prompt=prompt,
                    model=model_id,
                    generation_time=generation_time
                )
                
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {e}")
            return HFGenerationResult(
                success=False,
                error=str(e),
                prompt=prompt,
                model=self.config.get_model_id(),
                generation_time=time.time() - start_time
            )
    
    async def _generate_text2video(
        self,
        prompt: str,
        num_frames: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with text-to-video models (Zeroscope, ModelScope)."""
        import torch
        
        # Run in thread pool to avoid blocking
        def _generate():
            with torch.no_grad():
                output = self._pipeline(
                    prompt=prompt,
                    num_frames=num_frames,
                    width=kwargs.get("width", self.config.width),
                    height=kwargs.get("height", self.config.height),
                    num_inference_steps=kwargs.get("num_inference_steps", self.config.num_inference_steps),
                    guidance_scale=kwargs.get("guidance_scale", self.config.guidance_scale),
                    negative_prompt=kwargs.get("negative_prompt", ""),
                    generator=torch.Generator(device=self.device).manual_seed(
                        kwargs.get("seed", int(time.time()))
                    )
                )
            return output
        
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, _generate)
        
        # Save video
        video_path = self._save_video(output.frames[0], prompt)
        
        return {
            "success": True,
            "video_path": video_path,
            "metadata": {
                "num_frames": num_frames,
                "prompt": prompt
            }
        }
    
    async def _generate_svd(
        self,
        prompt: str,
        num_frames: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with Stable Video Diffusion (image-to-video)."""
        # SVD requires an input image
        image_path = kwargs.get("image_path")
        
        if not image_path:
            return {
                "success": False,
                "error": "SVD requires an input image. Provide image_path parameter."
            }
        
        from PIL import Image
        import torch
        
        # Load and resize image
        image = Image.open(image_path).convert("RGB")
        image = image.resize((self.config.width, self.config.height))
        
        def _generate():
            with torch.no_grad():
                output = self._pipeline(
                    image,
                    num_frames=num_frames,
                    num_inference_steps=kwargs.get("num_inference_steps", self.config.num_inference_steps),
                    decode_chunk_size=8,
                    generator=torch.Generator(device=self.device).manual_seed(
                        kwargs.get("seed", int(time.time()))
                    )
                )
            return output
        
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, _generate)
        
        video_path = self._save_video(output.frames[0], prompt)
        
        return {
            "success": True,
            "video_path": video_path,
            "metadata": {
                "num_frames": num_frames,
                "source_image": image_path
            }
        }
    
    async def _generate_animatediff(
        self,
        prompt: str,
        num_frames: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with AnimateDiff."""
        import torch
        
        def _generate():
            with torch.no_grad():
                output = self._pipeline(
                    prompt=prompt,
                    num_frames=num_frames,
                    width=kwargs.get("width", self.config.width),
                    height=kwargs.get("height", self.config.height),
                    num_inference_steps=kwargs.get("num_inference_steps", self.config.num_inference_steps),
                    guidance_scale=kwargs.get("guidance_scale", self.config.guidance_scale),
                    negative_prompt=kwargs.get("negative_prompt", ""),
                    generator=torch.Generator(device=self.device).manual_seed(
                        kwargs.get("seed", int(time.time()))
                    )
                )
            return output
        
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, _generate)
        
        video_path = self._save_video(output.frames[0], prompt)
        
        return {
            "success": True,
            "video_path": video_path,
            "metadata": {
                "num_frames": num_frames,
                "prompt": prompt
            }
        }
    
    async def _generate_cogvideo(
        self,
        prompt: str,
        num_frames: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with CogVideoX."""
        import torch
        
        def _generate():
            with torch.no_grad():
                output = self._pipeline(
                    prompt=prompt,
                    num_frames=num_frames,
                    num_inference_steps=kwargs.get("num_inference_steps", 50),
                    guidance_scale=kwargs.get("guidance_scale", 6.0),
                    generator=torch.Generator(device=self.device).manual_seed(
                        kwargs.get("seed", int(time.time()))
                    )
                )
            return output
        
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(None, _generate)
        
        video_path = self._save_video(output.frames[0], prompt)
        
        return {
            "success": True,
            "video_path": video_path,
            "metadata": {
                "num_frames": num_frames,
                "prompt": prompt
            }
        }
    
    def _save_video(
        self,
        frames,
        prompt: str,
        output_path: Optional[str] = None
    ) -> str:
        """Save frames as video file."""
        from diffusers.utils import export_to_video
        
        if output_path is None:
            timestamp = int(time.time())
            filename = f"hf_{timestamp}.{self.config.output_format}"
            output_path = os.path.join(self.config.output_dir, filename)
        
        if self.config.output_format == "gif":
            # Save as GIF
            from diffusers.utils import export_to_gif
            export_to_gif(frames, output_path)
        else:
            # Save as video
            export_to_video(frames, output_path, fps=self.config.fps)
        
        logger.info(f"Saved video to: {output_path}")
        return output_path
    
    async def generate_from_image(
        self,
        image_path: str,
        prompt: str = "",
        duration: float = 3.0,
        **kwargs
    ) -> HFGenerationResult:
        """
        Generate video from an input image.
        
        Uses SVD or other image-to-video models.
        """
        # Force SVD model for image-to-video
        kwargs["model"] = kwargs.get("model", HFVideoModel.SVD_XT.value)
        kwargs["image_path"] = image_path
        
        return await self.generate(prompt or "video animation", duration, **kwargs)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            "provider": "huggingface",
            "models": [m.value for m in HFVideoModel],
            "device": self.device,
            "features": [
                "text_to_video",
                "image_to_video",
                "open_source",
                "local_generation"
            ],
            "max_frames": 64,
            "resolutions": {
                "zeroscope": "576x320",
                "svd": "1024x576",
                "animatediff": "512x512",
                "cogvideo": "720x480"
            }
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models with info."""
        return [
            {
                "id": HFVideoModel.ZEROSCOPE.value,
                "name": "Zeroscope v2",
                "type": "text-to-video",
                "quality": "medium",
                "speed": "fast",
                "vram": "6GB"
            },
            {
                "id": HFVideoModel.ZEROSCOPE_XL.value,
                "name": "Zeroscope v2 XL",
                "type": "text-to-video",
                "quality": "high",
                "speed": "medium",
                "vram": "12GB"
            },
            {
                "id": HFVideoModel.SVD_XT.value,
                "name": "Stable Video Diffusion XT",
                "type": "image-to-video",
                "quality": "high",
                "speed": "medium",
                "vram": "16GB"
            },
            {
                "id": HFVideoModel.ANIMATEDIFF.value,
                "name": "AnimateDiff",
                "type": "text-to-video",
                "quality": "high",
                "speed": "medium",
                "vram": "8GB"
            },
            {
                "id": HFVideoModel.COGVIDEO.value,
                "name": "CogVideoX 2B",
                "type": "text-to-video",
                "quality": "high",
                "speed": "slow",
                "vram": "16GB"
            },
            {
                "id": HFVideoModel.MODELSCOPE_T2V.value,
                "name": "ModelScope Text-to-Video",
                "type": "text-to-video",
                "quality": "medium",
                "speed": "fast",
                "vram": "8GB"
            }
        ]


# ============ Convenience Functions ============

def create_huggingface_provider(
    model: Union[HFVideoModel, str] = HFVideoModel.ZEROSCOPE,
    **kwargs
) -> HuggingFaceProvider:
    """Create a HuggingFace provider instance."""
    config = HFVideoConfig(model=model, **kwargs)
    return HuggingFaceProvider(config)


async def generate_hf_video(
    prompt: str,
    duration: float = 3.0,
    model: Union[HFVideoModel, str] = HFVideoModel.ZEROSCOPE,
    **kwargs
) -> HFGenerationResult:
    """
    Quick function to generate video with HuggingFace models.
    
    Args:
        prompt: Video description
        duration: Target duration
        model: Model to use
        **kwargs: Additional parameters
    
    Returns:
        HFGenerationResult
    """
    provider = create_huggingface_provider(model=model)
    return await provider.generate(prompt, duration, **kwargs)
