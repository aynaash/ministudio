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
    
    # Priority order: Vertex AI > Sora > Local > Mock
    
    # Check Vertex AI
    if (os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or 
        os.getenv("VERTEX_AI_API_KEY") or 
        os.getenv("GCP_PROJECT_ID")):
        return "vertex-ai"
    
    # Check Sora
    if HAS_SORA and os.getenv("OPENAI_API_KEY"):
        return "sora"
    
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
    "list_providers",
    
    # Registry
    "PROVIDERS",
]

# Add Sora if available
if HAS_SORA:
    __all__.append("OpenAISoraProvider")
