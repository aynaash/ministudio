"""
Audio Generation for Ministudio.
Handles voice synthesis for character dialogue.


"""


# TODO: add more providers like Amazon Polly, Azure TTS, or opensource models tts
import logging
from typing import Dict, List, Optional, Any, Protocol, runtime_checkable
from pathlib import Path
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class AudioRequest:
    text: str
    voice_id: str
    voice_profile: Optional['VoiceProfile'] = None
    settings: Dict[str, Any] = None


@runtime_checkable
class AudioProvider(Protocol):
    """Protocol for audio generation providers"""
    @property
    def name(self) -> str: ...
    async def generate_audio(self, request: AudioRequest) -> Path: ...


class MockAudioProvider:
    """Mock audio provider for testing"""

    def __init__(self, output_dir: str = "./ministudio_audio"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "mock"

    async def generate_audio(self, request: AudioRequest) -> Path:
        """Simulate audio generation"""
        await asyncio.sleep(0.5)

        filename = f"dialogue_{str(abs(hash(request.text)))[:8]}.mp3"
        output_path = self.output_dir / filename

        # Create a dummy file
        output_path.write_bytes(b"mock_audio_data")

        logger.info(f"Mock audio generated: {output_path}")
        return output_path


class ElevenLabsProvider:
    """Placeholder for ElevenLabs integration"""

    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    def name(self) -> str:
        return "elevenlabs"

    async def generate_audio(self, request: AudioRequest) -> Path:
        # TODO: Implement real ElevenLabs call
        raise NotImplementedError("ElevenLabs provider not yet implemented")


class GoogleTTSProvider:
    """Google Cloud Text-to-Speech provider"""

    def __init__(self, output_dir: str = "./ministudio_audio", credentials=None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Lazy import to avoid circular dependency if utils imports from audio (not likely but safe)
        from .utils import load_gcp_credentials

        # Load credentials if not provided
        if not credentials:
            credentials, _ = load_gcp_credentials()

        try:
            from google.cloud import texttospeech
            if credentials:
                self._client = texttospeech.TextToSpeechClient(
                    credentials=credentials)
            else:
                self._client = texttospeech.TextToSpeechClient()
        except ImportError:
            logger.error(
                "google-cloud-texttospeech not installed. Run 'pip install google-cloud-texttospeech'")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize Google TTS client: {e}")
            self._client = None

    @property
    def name(self) -> str:
        return "google-tts"

    async def generate_audio(self, request: AudioRequest) -> Path:
        """Generate speech using Google Cloud TTS"""
        if not self._client:
            raise ImportError(
                "Google Cloud Text-to-Speech client is not initialized.")

        from google.cloud import texttospeech

        logger.info(f"Generating Google TTS: '{request.text[:30]}...'")

        synthesis_input = texttospeech.SynthesisInput(text=request.text)

        # Use Studio-O by default if not specified, or fallback to request.voice_id
        voice_name = request.voice_id if request.voice_id and "-" in request.voice_id else "en-US-Studio-O"

        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name
        )

        # Default configuration optimized for emotional storytelling
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.settings.get(
                "speaking_rate", 0.92) if request.settings else 0.92,
            pitch=request.settings.get(
                "pitch", 0.0) if request.settings else 0.0
        )

        try:
            # Run in executor to avoid blocking async loop if client is synchronous
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
            )

            filename = f"voice_{voice_name}_{str(abs(hash(request.text)))[:8]}.mp3"
            output_path = self.output_dir / filename

            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            logger.info(f"Google TTS generated: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"GCP TTS Error: {e}")
            raise
