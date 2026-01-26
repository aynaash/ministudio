"""
Provider Registry
=================
Multi-model orchestration system for MiniStudio.

Manages multiple AI providers (Vertex AI, Hugging Face, Local, etc.) with:
- Dynamic provider selection per shot
- Fallback chains for resilience
- Cost tracking and optimization
- Provider health monitoring

Example:
    from ministudio.registry import ProviderRegistry
    
    registry = ProviderRegistry()
    registry.register("vertex-ai", VertexAIProvider.create())
    registry.register("local", LocalVideoProvider.create())
    
    # Per-shot provider selection
    provider = registry.get("vertex-ai")
    
    # Auto-fallback
    provider = registry.get_with_fallback(["vertex-ai", "local"])
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from .providers import BaseVideoProvider, create_provider, list_providers

logger = logging.getLogger(__name__)


class ProviderStatus(Enum):
    """Health status of a provider."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ProviderMetrics:
    """Tracks provider performance metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_generation_time: float = 0.0
    total_cost: float = 0.0
    last_success: Optional[float] = None
    last_failure: Optional[float] = None
    consecutive_failures: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    @property
    def average_generation_time(self) -> float:
        if self.successful_requests == 0:
            return 0.0
        return self.total_generation_time / self.successful_requests
    
    def record_success(self, generation_time: float, cost: float = 0.0):
        self.total_requests += 1
        self.successful_requests += 1
        self.total_generation_time += generation_time
        self.total_cost += cost
        self.last_success = time.time()
        self.consecutive_failures = 0
    
    def record_failure(self):
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = time.time()
        self.consecutive_failures += 1


@dataclass
class RegisteredProvider:
    """A provider registered in the registry."""
    name: str
    provider: BaseVideoProvider
    priority: int = 0  # Higher = preferred
    tags: List[str] = field(default_factory=list)  # e.g., ["cloud", "fast", "cheap"]
    metrics: ProviderMetrics = field(default_factory=ProviderMetrics)
    enabled: bool = True
    
    # Provider capabilities
    max_duration: int = 8
    supported_styles: List[str] = field(default_factory=list)
    supports_image_input: bool = False
    supports_character_grounding: bool = False
    
    @property
    def status(self) -> ProviderStatus:
        """Determine health status based on metrics."""
        if not self.enabled:
            return ProviderStatus.UNHEALTHY
        if self.metrics.consecutive_failures >= 3:
            return ProviderStatus.UNHEALTHY
        if self.metrics.consecutive_failures >= 1:
            return ProviderStatus.DEGRADED
        if self.metrics.total_requests == 0:
            return ProviderStatus.UNKNOWN
        if self.metrics.success_rate < 0.5:
            return ProviderStatus.DEGRADED
        return ProviderStatus.HEALTHY


class ProviderRegistry:
    """
    Central registry for managing multiple video generation providers.
    
    Features:
    - Register/unregister providers dynamically
    - Get providers by name, tags, or capabilities
    - Automatic fallback chains
    - Health monitoring and circuit breaking
    - Cost tracking and optimization
    """
    
    def __init__(self, auto_discover: bool = True):
        """
        Initialize the registry.
        
        Args:
            auto_discover: If True, automatically discover and register
                          configured providers from environment
        """
        self._providers: Dict[str, RegisteredProvider] = {}
        self._fallback_chain: List[str] = []
        self._default_provider: Optional[str] = None
        
        if auto_discover:
            self._auto_discover()
    
    def _auto_discover(self):
        """Auto-discover providers from environment configuration."""
        available = list_providers()
        
        for name, info in available.items():
            if info.get("configured") and info.get("available"):
                try:
                    provider = create_provider(name)
                    self.register(
                        name=name,
                        provider=provider,
                        tags=self._get_tags_for_provider(name),
                        priority=self._get_priority_for_provider(name)
                    )
                    logger.info(f"Auto-registered provider: {name}")
                except Exception as e:
                    logger.debug(f"Could not auto-register {name}: {e}")
    
    def _get_tags_for_provider(self, name: str) -> List[str]:
        """Get default tags for known providers."""
        tag_map = {
            "vertex-ai": ["cloud", "high-quality", "grounding"],
            "google": ["cloud", "high-quality", "grounding"],
            "sora": ["cloud", "high-quality", "long-form"],
            "local": ["local", "free", "customizable"],
            "mock": ["test", "free", "fast"],
        }
        return tag_map.get(name, [])
    
    def _get_priority_for_provider(self, name: str) -> int:
        """Get default priority for known providers."""
        priority_map = {
            "vertex-ai": 100,
            "google": 100,
            "sora": 90,
            "local": 50,
            "mock": 10,
        }
        return priority_map.get(name, 50)
    
    def register(
        self,
        name: str,
        provider: BaseVideoProvider,
        priority: int = 50,
        tags: Optional[List[str]] = None,
        set_default: bool = False
    ) -> "ProviderRegistry":
        """
        Register a provider.
        
        Args:
            name: Unique identifier for the provider
            provider: The provider instance
            priority: Priority for fallback selection (higher = preferred)
            tags: Tags for filtering (e.g., ["cloud", "fast"])
            set_default: If True, set as the default provider
            
        Returns:
            Self for chaining
        """
        registered = RegisteredProvider(
            name=name,
            provider=provider,
            priority=priority,
            tags=tags or [],
            max_duration=getattr(provider, 'max_duration', 8),
            supports_image_input=hasattr(provider, 'supports_image_input'),
            supports_character_grounding=hasattr(provider, 'supports_character_grounding'),
        )
        
        self._providers[name] = registered
        
        # Update fallback chain based on priority
        self._update_fallback_chain()
        
        if set_default or self._default_provider is None:
            self._default_provider = name
        
        logger.info(f"Registered provider: {name} (priority={priority})")
        return self
    
    def unregister(self, name: str) -> bool:
        """Remove a provider from the registry."""
        if name in self._providers:
            del self._providers[name]
            self._update_fallback_chain()
            if self._default_provider == name:
                self._default_provider = self._fallback_chain[0] if self._fallback_chain else None
            return True
        return False
    
    def _update_fallback_chain(self):
        """Update fallback chain based on provider priorities."""
        sorted_providers = sorted(
            self._providers.values(),
            key=lambda p: (-p.priority, p.name)
        )
        self._fallback_chain = [p.name for p in sorted_providers if p.enabled]
    
    def get(self, name: Optional[str] = None) -> Optional[BaseVideoProvider]:
        """
        Get a provider by name.
        
        Args:
            name: Provider name. If None, returns default provider.
            
        Returns:
            The provider instance, or None if not found
        """
        if name is None:
            name = self._default_provider
        
        if name and name in self._providers:
            return self._providers[name].provider
        
        return None
    
    def get_with_fallback(
        self,
        preferred: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        min_duration: Optional[int] = None,
        exclude_unhealthy: bool = True
    ) -> Optional[BaseVideoProvider]:
        """
        Get a provider with automatic fallback.
        
        Args:
            preferred: Ordered list of preferred providers
            tags: Required tags (provider must have ALL tags)
            min_duration: Minimum duration support required
            exclude_unhealthy: Skip unhealthy providers
            
        Returns:
            First available provider matching criteria
        """
        # Build candidate list
        if preferred:
            candidates = preferred
        else:
            candidates = self._fallback_chain
        
        for name in candidates:
            if name not in self._providers:
                continue
            
            registered = self._providers[name]
            
            # Check health
            if exclude_unhealthy and registered.status == ProviderStatus.UNHEALTHY:
                logger.debug(f"Skipping unhealthy provider: {name}")
                continue
            
            # Check tags
            if tags and not all(tag in registered.tags for tag in tags):
                continue
            
            # Check duration
            if min_duration and registered.max_duration < min_duration:
                continue
            
            return registered.provider
        
        logger.warning("No suitable provider found in fallback chain")
        return None
    
    def get_for_shot(
        self,
        shot_config: Dict[str, Any],
        default_provider: Optional[str] = None
    ) -> BaseVideoProvider:
        """
        Get the best provider for a specific shot.
        
        Considers shot requirements (duration, style, grounding needs)
        and provider capabilities.
        
        Args:
            shot_config: Shot configuration dict
            default_provider: Fallback provider name
            
        Returns:
            Best matching provider
        """
        # Check if shot specifies a provider
        if "provider" in shot_config:
            requested = shot_config["provider"]
            if requested in self._providers:
                return self._providers[requested].provider
            # Try to parse provider reference (e.g., "huggingface/model-name")
            if "/" in requested:
                base_provider = requested.split("/")[0]
                if base_provider in self._providers:
                    return self._providers[base_provider].provider
        
        # Determine requirements from shot
        duration = shot_config.get("duration_seconds", 8)
        needs_grounding = bool(
            shot_config.get("character_samples") or 
            shot_config.get("background_samples") or
            shot_config.get("starting_frames")
        )
        
        # Find best match
        for name in self._fallback_chain:
            registered = self._providers[name]
            
            if registered.status == ProviderStatus.UNHEALTHY:
                continue
            
            if duration > registered.max_duration:
                continue
            
            if needs_grounding and not registered.supports_character_grounding:
                # Prefer providers with grounding, but don't exclude others
                pass
            
            return registered.provider
        
        # Fallback to default
        if default_provider and default_provider in self._providers:
            return self._providers[default_provider].provider
        
        raise RuntimeError("No suitable provider available for shot")
    
    def record_result(
        self,
        provider_name: str,
        success: bool,
        generation_time: float = 0.0,
        cost: float = 0.0
    ):
        """Record a generation result for metrics tracking."""
        if provider_name not in self._providers:
            return
        
        metrics = self._providers[provider_name].metrics
        if success:
            metrics.record_success(generation_time, cost)
        else:
            metrics.record_failure()
    
    def get_metrics(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for one or all providers."""
        if provider_name:
            if provider_name not in self._providers:
                return {}
            p = self._providers[provider_name]
            return {
                "name": p.name,
                "status": p.status.value,
                "total_requests": p.metrics.total_requests,
                "success_rate": p.metrics.success_rate,
                "avg_generation_time": p.metrics.average_generation_time,
                "total_cost": p.metrics.total_cost,
            }
        
        return {
            name: self.get_metrics(name)
            for name in self._providers
        }
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all registered providers with their status."""
        return {
            name: {
                "status": p.status.value,
                "priority": p.priority,
                "tags": p.tags,
                "max_duration": p.max_duration,
                "enabled": p.enabled,
                "metrics": {
                    "requests": p.metrics.total_requests,
                    "success_rate": p.metrics.success_rate,
                }
            }
            for name, p in self._providers.items()
        }
    
    def enable(self, name: str) -> bool:
        """Enable a provider."""
        if name in self._providers:
            self._providers[name].enabled = True
            self._update_fallback_chain()
            return True
        return False
    
    def disable(self, name: str) -> bool:
        """Disable a provider (excludes from selection)."""
        if name in self._providers:
            self._providers[name].enabled = False
            self._update_fallback_chain()
            return True
        return False
    
    @property
    def default_provider(self) -> Optional[str]:
        """Get the default provider name."""
        return self._default_provider
    
    @default_provider.setter
    def default_provider(self, name: str):
        """Set the default provider."""
        if name in self._providers:
            self._default_provider = name
        else:
            raise ValueError(f"Provider not found: {name}")
    
    @property
    def fallback_chain(self) -> List[str]:
        """Get the current fallback chain."""
        return self._fallback_chain.copy()
    
    def __contains__(self, name: str) -> bool:
        return name in self._providers
    
    def __len__(self) -> int:
        return len(self._providers)
    
    def __iter__(self):
        return iter(self._providers.values())


# Global registry instance
_global_registry: Optional[ProviderRegistry] = None


def get_registry(auto_create: bool = True) -> ProviderRegistry:
    """Get the global provider registry."""
    global _global_registry
    if _global_registry is None and auto_create:
        _global_registry = ProviderRegistry()
    return _global_registry


def set_registry(registry: ProviderRegistry):
    """Set the global provider registry."""
    global _global_registry
    _global_registry = registry
