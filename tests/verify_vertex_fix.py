import asyncio
import os
import unittest
from unittest.mock import MagicMock, patch
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Mocking the interfaces and request to avoid complex imports if needed
# but since we are in the repo, we can try to import them
from ministudio.interfaces import VideoGenerationRequest
from ministudio.providers.vertex_ai import VertexAIProvider


class TestVertexAIFix(unittest.TestCase):
    def setUp(self):
        # Create a dummy image file for testing
        self.test_image = "test_anchor.png"
        with open(self.test_image, "wb") as f:
            f.write(b"fake image data")

    def tearDown(self):
        if os.path.exists(self.test_image):
            os.remove(self.test_image)

    @patch('google.genai.Client')
    @patch('ministudio.providers.vertex_ai.load_gcp_credentials')
    def test_image_anchor_fix(self, mock_load_creds, mock_client_class):
        # Setup mocks
        mock_load_creds.return_value = (MagicMock(), "test-project")
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        provider = VertexAIProvider(project_id="test-project")

        # Mock the operation
        mock_operation = MagicMock()
        mock_operation.done = True
        mock_client.models.generate_videos.return_value = mock_operation

        # Mock operation result
        mock_result = MagicMock()
        mock_result.generated_videos = [MagicMock()]
        mock_operation.result = mock_result

        # Request with character samples (should trigger reference_images)
        request = VideoGenerationRequest(
            prompt="Test prompt",
            duration_seconds=4,
            character_samples={"emma": [self.test_image]}
        )

        # Run generate_video
        async def run():
            return await provider.generate_video(request)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())

        # Verify generate_videos was called with correct types
        args, kwargs = mock_client.models.generate_videos.call_args

        # Check that 'image' is passed correctly if starting_frames were used
        # (In our case, starting_frames is None, so image should be None)
        self.assertIsNone(kwargs.get('image'))

        # Check config
        config = kwargs.get('config')
        self.assertIsNotNone(config)

        # Check reference_images
        self.assertIsNotNone(config.reference_images)
        self.assertEqual(len(config.reference_images), 1)

        # Check that it's using types.Image (mocked/real)
        self.assertEqual(
            config.reference_images[0].image.image_bytes, b"fake image data")
        self.assertEqual(
            config.reference_images[0].image.mime_type, "image/png")

        # Check duration was clamped correctly (or set to 8 for refs)
        self.assertEqual(config.duration_seconds, 8)

    @patch('google.genai.Client')
    @patch('ministudio.providers.vertex_ai.load_gcp_credentials')
    def test_starting_frames_to_image(self, mock_load_creds, mock_client_class):
        mock_load_creds.return_value = (MagicMock(), "test-project")
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        provider = VertexAIProvider(project_id="test-project")

        mock_operation = MagicMock()
        mock_operation.done = True
        mock_client.models.generate_videos.return_value = mock_operation
        mock_operation.result = MagicMock()

        # Request with starting frames
        request = VideoGenerationRequest(
            prompt="Test prompt",
            duration_seconds=4,
            starting_frames=[self.test_image]
        )

        async def run():
            return await provider.generate_video(request)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(run())

        kwargs = mock_client.models.generate_videos.call_args[1]

        # Check that 'image' is now populated from starting_frames
        self.assertIsNotNone(kwargs.get('image'))
        # It's a types.Image object, let's check its content
        self.assertEqual(kwargs.get('image').image_bytes, b"fake image data")
        self.assertEqual(kwargs.get('image').mime_type, "image/png")


if __name__ == "__main__":
    unittest.main()
