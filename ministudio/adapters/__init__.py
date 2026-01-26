"""
MiniStudio Provider Adapters

Pre-configured adapters for common video generation providers.
These adapters simplify setup and provide best-practice defaults.

Usage:
    from ministudio.adapters import VertexAIAdapter
    
    provider = VertexAIAdapter.create()
    orchestrator = VideoOrchestrator(provider)
"""

from .huggingface_adapter import HuggingFaceAdapter
from .vertex_ai_adapter import VertexAIAdapter
from .local_model_adapter import LocalModelAdapter

__all__ = [
    "HuggingFaceAdapter",
    "VertexAIAdapter",
    "LocalModelAdapter",
]
