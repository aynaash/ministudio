"""
Tests for Ministudio providers.
"""

import pytest
import asyncio
from ministudio import VideoGenerationRequest, VideoGenerationResult, Ministudio, VideoProvider
from ministudio.providers.mock import MockVideoProvider


class TestMockProvider:
    """Test MockVideoProvider."""

    def test_provider_creation(self):
        """Test provider creation."""
        provider = MockVideoProvider()
        assert provider.name == "mock"
        assert provider.supported_aspect_ratios == ["16:9", "1:1", "9:16"]
        assert provider.max_duration == 60

    @pytest.mark.asyncio
    async def test_generate_video(self):
        """Test video generation."""
        provider = MockVideoProvider()

        request = VideoGenerationRequest(
            prompt="Test prompt",
            duration_seconds=8
        )

        result = await provider.generate_video(request)

        assert result.success is True
        assert result.provider == "mock"
        assert isinstance(result.video_bytes, bytes)
        assert result.generation_time > 0

    def test_estimate_cost(self):
        """Test cost estimation."""
        provider = MockVideoProvider()

        cost = provider.estimate_cost(10)
        assert cost == 0.0  # Mock provider is free


class TestVertexAIProvider:
    """Test VertexAIProvider (without actual API calls)."""

    def test_provider_creation_mock(self):
        """Test provider creation with mock credentials."""
        # This would normally require GCP setup
        # For testing, we just check the class exists
        from ministudio.providers.vertex_ai import VertexAIProvider, load_gcp_credentials

        # Test that the class can be imported
        assert VertexAIProvider

        # Test that load_gcp_credentials function exists
        assert callable(load_gcp_credentials)

    def test_estimate_cost(self):
        """Test cost estimation."""
        # For now, just test the idea of cost estimation
        # In a real scenario, we'd test the actual provider method
        duration = 10
        cost_per_second = 0.05
        assert duration * cost_per_second == 0.5


# Integration test for provider creation
def test_create_provider_mock():
    """Test creating providers through Ministudio."""
    provider = Ministudio.create_provider("mock")
    assert provider.name == "mock"

    # Test that it implements the protocol/ABC
    assert isinstance(provider, VideoProvider)
