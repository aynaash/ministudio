"""
Tests for Ministudio core functionality.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from ministudio import (
    VideoGenerationRequest,
    VideoGenerationResult,
    StyleConfig,
    Ministudio,
    VideoProvider,
    VideoConfig
)


class TestVideoGenerationRequest:
    """Test VideoGenerationRequest class."""

    def test_creation(self):
        """Test basic creation."""
        request = VideoGenerationRequest(
            prompt="Test prompt",
            duration_seconds=10,
            aspect_ratio="16:9"
        )
        assert request.prompt == "Test prompt"
        assert request.duration_seconds == 10
        assert request.aspect_ratio == "16:9"

    def test_to_dict(self):
        """Test to_dict conversion."""
        request = VideoGenerationRequest(
            prompt="Test",
            duration_seconds=8,
            negative_prompt="no humans"
        )
        data = request.to_dict()
        assert data["prompt"] == "Test"
        assert data["negative_prompt"] == "no humans"


class TestVideoGenerationResult:
    """Test VideoGenerationResult class."""

    def test_success_result(self):
        """Test successful result."""
        result = VideoGenerationResult(
            success=True,
            video_bytes=b"test video",
            provider="mock",
            generation_time=2.5
        )
        assert result.success is True
        assert result.video_bytes == b"test video"
        assert result.generation_time == 2.5


class TestStyleConfig:
    """Test StyleConfig class."""

    def test_creation(self):
        """Test basic creation."""
        config = StyleConfig(
            name="cyberpunk",
            description="Neon cyberpunk style"
        )
        assert config.name == "cyberpunk"
        assert config.description == "Neon cyberpunk style"


class TestMinistudio:
    """Test Ministudio class."""

    @pytest.mark.asyncio
    async def test_generate_concept_video(self):
        """Test concept video generation."""
        # Mock provider
        mock_provider = Mock(spec=VideoProvider)
        mock_provider.name = "mock"
        mock_result = VideoGenerationResult(
            success=True,
            video_bytes=b"test video",
            provider="mock",
            generation_time=2.0
        )
        mock_provider.generate_video = AsyncMock(return_value=mock_result)

        # Create studio
        studio = Ministudio(provider=mock_provider)

        # Generate video
        result = await studio.generate_concept_video(
            concept="Test",
            action="orb testing"
        )

        assert result.success is True
        assert result.video_bytes == b"test video"
        assert result.provider == "mock"
        mock_provider.generate_video.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_segmented_video(self):
        """Test segmented video generation."""
        # Mock provider
        mock_provider = Mock(spec=VideoProvider)
        mock_provider.name = "mock"
        mock_result = VideoGenerationResult(
            success=True,
            video_bytes=b"segment video",
            provider="mock",
            generation_time=1.0
        )
        mock_provider.generate_video = AsyncMock(return_value=mock_result)

        # Create studio
        studio = Ministudio(provider=mock_provider)

        # Define segments
        segments = [
            {"concept": "Intro", "action": "character enters"},
            {"concept": "Action", "action": "character moves"}
        ]

        # Generate segmented video
        results = await studio.generate_segmented_video(segments)

        assert len(results) == 2
        assert all(r.success for r in results)
        assert mock_provider.generate_video.call_count == 2

    def test_output_directory_creation(self):
        """Test output directory creation."""
        import tempfile
        import shutil

        with tempfile.TemporaryDirectory() as temp_dir:
            custom_dir = Path(temp_dir) / "custom_output"
            studio = Ministudio(
                provider=Mock(spec=VideoProvider),
                output_dir=str(custom_dir)
            )

            assert custom_dir.exists()
            assert custom_dir.is_dir()
