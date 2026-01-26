"""
MiniStudio Providers
====================
Unified provider system for video generation.

Quick Start:
    # Auto-detect best provider
    from ministudio.providers import create_provider
    provider = create_provider()
    
    # Specific provider with factory
    from ministudio.providers import VertexAIProvider
    provider = VertexAIProvider.create(project_id="my-project")
    
    # List available providers
    from ministudio.providers import list_providers
    print(list_providers())
"""

import os
from typing import Optional, Dict, Any, List

from .base import BaseVideoProvider
from .vertex_ai import VertexAIProvider
from .local import LocalVideoProvider
from .mock import MockVideoProvider

# Try to import optional providers
try:
    from .openai_sora import OpenAISoraProvider
    HAS_SORA = True
except ImportError:
    HAS_SORA = False

# Veo provider (Google's video generation model)
try:
    from .veo import VeoProvider, VeoConfig, VeoModel, VeoGenerationResult, create_veo_provider
    HAS_VEO = True
except ImportError:
    HAS_VEO = False

# HuggingFace open-source video models
try:
    from .huggingface import (
        HuggingFaceProvider, HFVideoConfig, HFVideoModel, HFGenerationResult,
        create_huggingface_provider
    )
    HAS_HUGGINGFACE = True
except ImportError:
    HAS_HUGGINGFACE = False


# Provider registry
PROVIDERS: Dict[str, type] = {
    "vertex-ai": VertexAIProvider,
    "google": VertexAIProvider,
    "local": LocalVideoProvider,
    "mock": MockVideoProvider,
}

if HAS_SORA:
    PROVIDERS["sora"] = OpenAISoraProvider
    PROVIDERS["openai"] = OpenAISoraProvider

if HAS_VEO:
    PROVIDERS["veo"] = VeoProvider

if HAS_HUGGINGFACE:
    PROVIDERS["huggingface"] = HuggingFaceProvider
    PROVIDERS["hf"] = HuggingFaceProvider


def list_providers() -> Dict[str, Dict[str, Any]]:
    """
    List all available providers with their status.
    
    Returns:
        Dict with provider info and configuration status
    """
    status = {}
    
    # Vertex AI / Google
    status["vertex-ai"] = {
        "available": True,
        "configured": bool(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or
            os.getenv("VERTEX_AI_API_KEY") or
            os.getenv("GOOGLE_API_KEY") or
            os.getenv("GCP_PROJECT_ID")
        ),
        "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS", "GCP_PROJECT_ID", "VERTEX_AI_API_KEY"],
        "description": "Google Cloud Vertex AI (Veo 3.1)"
    }
    
    # Veo (Google's dedicated video model)
    status["veo"] = {
        "available": HAS_VEO,
        "configured": bool(os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
        "env_vars": ["GCP_PROJECT_ID", "GOOGLE_APPLICATION_CREDENTIALS"],
        "description": "Google Veo video generation (Veo 1 / Veo 2)"
    }
    
    # HuggingFace open-source models
    status["huggingface"] = {
        "available": HAS_HUGGINGFACE,
        "configured": True,  # No API key needed for local inference
        "env_vars": ["HF_TOKEN"],  # Optional for private models
        "description": "HuggingFace open-source models (Zeroscope, SVD, AnimateDiff, CogVideo)"
    }
    
    # Local
    status["local"] = {
        "available": True,
        "configured": True,  # Always available
        "env_vars": ["LOCAL_MODEL_PATH"],
        "description": "Local model inference (Stable Video Diffusion, etc.)"
    }
    
    # Mock
    status["mock"] = {
        "available": True,
        "configured": True,
        "env_vars": [],
        "description": "Mock provider for testing"
    }
    
    # Sora
    status["sora"] = {
        "available": HAS_SORA,
        "configured": bool(os.getenv("OPENAI_API_KEY")),
        "env_vars": ["OPENAI_API_KEY"],
        "description": "OpenAI Sora (requires API access)"
    }
    
    return status


def create_provider(
    provider_name: Optional[str] = None,
    **kwargs
) -> BaseVideoProvider:
    """
    Create a provider instance with automatic configuration.
    
    Args:
        provider_name: Provider to use. If None, auto-detects best available.
        **kwargs: Provider-specific configuration
    
    Returns:
        Configured provider instance
    
    Examples:
        # Auto-detect
        provider = create_provider()
        
        # Specific provider
        provider = create_provider("vertex-ai", project_id="my-project")
        
        # From environment
        provider = create_provider()  # Uses MINISTUDIO_PROVIDER env var
    """
    # Check environment for provider preference
    if not provider_name:
        provider_name = os.getenv("MINISTUDIO_PROVIDER")
    
    # Auto-detect if still not specified
    if not provider_name:
        provider_name = _auto_detect_provider()
    
    provider_name = provider_name.lower()
    
    if provider_name not in PROVIDERS:
        available = list(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")
    
    provider_class = PROVIDERS[provider_name]
    
    # Use factory method if available
    if hasattr(provider_class, 'create'):
        return provider_class.create(**kwargs)
    
    return provider_class(**kwargs)


def _auto_detect_provider() -> str:
    """Auto-detect best available provider based on environment."""
    
    # Priority order: Veo > Vertex AI > Sora > HuggingFace > Local > Mock
    
    # Check Veo
    if HAS_VEO and (os.getenv("GCP_PROJECT_ID") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
        return "veo"
    
    # Check Vertex AI
    if (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or 
        os.getenv("VERTEX_AI_API_KEY") or 
        os.getenv("GCP_PROJECT_ID")):
        return "vertex-ai"
    
    # Check Sora
    if HAS_SORA and os.getenv("OPENAI_API_KEY"):
        return "sora"
    
    # Check HuggingFace (GPU available)
    if HAS_HUGGINGFACE:
        try:
            import torch
            if torch.cuda.is_available() or torch.backends.mps.is_available():
                return "huggingface"
        except ImportError:
            pass
    
    # Check for local model path
    if os.getenv("LOCAL_MODEL_PATH"):
        return "local"
    
    # Default to mock for development
    return "mock"


# Convenience functions
def create_vertex_ai(project_id: Optional[str] = None, **kwargs) -> VertexAIProvider:
    """Create Vertex AI provider."""
    return VertexAIProvider.create(project_id=project_id, **kwargs) if hasattr(VertexAIProvider, 'create') else VertexAIProvider(project_id=project_id, **kwargs)


def create_local(model_path: Optional[str] = None, **kwargs) -> LocalVideoProvider:
    """Create local provider."""
    return LocalVideoProvider.create(model_path=model_path, **kwargs) if hasattr(LocalVideoProvider, 'create') else LocalVideoProvider(model_path=model_path, **kwargs)


def create_mock(**kwargs) -> MockVideoProvider:
    """Create mock provider for testing."""
    return MockVideoProvider(**kwargs)


def create_veo(project_id: Optional[str] = None, **kwargs):
    """Create Veo provider."""
    if HAS_VEO:
        return create_veo_provider(project_id=project_id, **kwargs)
    raise ImportError("Veo provider not available. Install google-cloud-aiplatform.")


def create_huggingface(model: Optional[str] = None, **kwargs):
    """Create HuggingFace provider."""
    if HAS_HUGGINGFACE:
        return create_huggingface_provider(model=model, **kwargs)
    raise ImportError("HuggingFace provider not available. Install diffusers, transformers, torch.")


# Export all
__all__ = [
    # Base
    "BaseVideoProvider",
    
    # Providers
    "VertexAIProvider",
    "LocalVideoProvider", 
    "MockVideoProvider",
    
    # Factory functions
    "create_provider",
    "create_vertex_ai",
    "create_local",
    "create_mock",
    "create_veo",
    "create_huggingface",
    "list_providers",
    
    # Registry
    "PROVIDERS",
    
    # Feature flags
    "HAS_SORA",
    "HAS_VEO",
    "HAS_HUGGINGFACE",
]

# Add Sora if available
if HAS_SORA:
    __all__.append("OpenAISoraProvider")

# Add Veo exports if available
if HAS_VEO:
    __all__.extend([
        "VeoProvider",
        "VeoConfig",
        "VeoModel",
        "VeoGenerationResult",
        "create_veo_provider"
    ])

# Add HuggingFace exports if available
if HAS_HUGGINGFACE:
    __all__.extend([
        "HuggingFaceProvider",
        "HFVideoConfig",
        "HFVideoModel",
        "HFGenerationResult",
        "create_huggingface_provider"
    ])
