"""
MiniStudio Audio Agent
======================
A small agent that takes audio descriptions from users and compiles them
into prompts for MiniStudio video generation.

Features:
- Audio transcription (via Whisper or cloud APIs)
- Natural language understanding
- Prompt compilation for video generation
- Interactive voice-driven video creation

Usage:
    from ministudio.audio_agent import AudioAgent
    
    agent = AudioAgent()
    
    # From audio file
    result = agent.process_audio("describe_video.wav")
    
    # From microphone (interactive)
    result = agent.listen_and_generate()
    
    # Generate video from result
    video = await agent.generate_video(result)
"""

import os
import re
import json
import asyncio
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
from enum import Enum

# Import MiniStudio components
try:
    from .simple_builder import SimpleBuilder, generate_video, TEMPLATES
    from .config import VideoConfig, ShotConfig
    from .orchestrator import VideoOrchestrator
except ImportError:
    from simple_builder import SimpleBuilder, generate_video, TEMPLATES
    from config import VideoConfig, ShotConfig
    from orchestrator import VideoOrchestrator


class TranscriptionProvider(Enum):
    """Supported transcription providers."""
    WHISPER_LOCAL = "whisper_local"
    WHISPER_API = "whisper_api"
    GOOGLE_SPEECH = "google_speech"
    AZURE_SPEECH = "azure_speech"
    DEEPGRAM = "deepgram"


@dataclass
class AudioInput:
    """Represents audio input from user."""
    source: str  # file path or "microphone"
    duration: Optional[float] = None
    sample_rate: int = 16000
    channels: int = 1
    format: str = "wav"


@dataclass
class TranscriptionResult:
    """Result from audio transcription."""
    text: str
    confidence: float = 1.0
    language: str = "en"
    segments: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: Optional[Dict] = None


@dataclass
class VideoPrompt:
    """Compiled video prompt ready for MiniStudio."""
    description: str
    style: str = "cinematic"
    duration: int = 8
    shots: List[Dict[str, Any]] = field(default_factory=list)
    characters: List[Dict[str, Any]] = field(default_factory=list)
    mood: str = "neutral"
    camera_movements: List[str] = field(default_factory=list)
    audio_requirements: Optional[Dict[str, Any]] = None
    template: Optional[str] = None
    confidence: float = 1.0
    original_transcript: str = ""


class AudioTranscriber:
    """Handles audio transcription from multiple providers."""
    
    def __init__(self, provider: TranscriptionProvider = TranscriptionProvider.WHISPER_LOCAL):
        self.provider = provider
        self._whisper_model = None
    
    def transcribe(self, audio: Union[str, AudioInput]) -> TranscriptionResult:
        """Transcribe audio to text."""
        if isinstance(audio, str):
            audio = AudioInput(source=audio)
        
        if self.provider == TranscriptionProvider.WHISPER_LOCAL:
            return self._transcribe_whisper_local(audio)
        elif self.provider == TranscriptionProvider.WHISPER_API:
            return self._transcribe_whisper_api(audio)
        elif self.provider == TranscriptionProvider.GOOGLE_SPEECH:
            return self._transcribe_google(audio)
        elif self.provider == TranscriptionProvider.DEEPGRAM:
            return self._transcribe_deepgram(audio)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _transcribe_whisper_local(self, audio: AudioInput) -> TranscriptionResult:
        """Transcribe using local Whisper model."""
        try:
            import whisper
        except ImportError:
            raise ImportError(
                "Whisper not installed. Run: pip install openai-whisper\n"
                "Or use a cloud provider instead."
            )
        
        if self._whisper_model is None:
            model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
            print(f"Loading Whisper model ({model_size})...")
            self._whisper_model = whisper.load_model(model_size)
        
        result = self._whisper_model.transcribe(audio.source)
        
        return TranscriptionResult(
            text=result["text"].strip(),
            language=result.get("language", "en"),
            segments=[
                {"start": s["start"], "end": s["end"], "text": s["text"]}
                for s in result.get("segments", [])
            ],
            raw_response=result
        )
    
    def _transcribe_whisper_api(self, audio: AudioInput) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("OpenAI not installed. Run: pip install openai")
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        with open(audio.source, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json"
            )
        
        return TranscriptionResult(
            text=response.text,
            language=response.language or "en",
            segments=[
                {"start": s.start, "end": s.end, "text": s.text}
                for s in (response.segments or [])
            ],
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
        )
    
    def _transcribe_google(self, audio: AudioInput) -> TranscriptionResult:
        """Transcribe using Google Cloud Speech-to-Text."""
        try:
            from google.cloud import speech
        except ImportError:
            raise ImportError(
                "Google Cloud Speech not installed. Run: pip install google-cloud-speech"
            )
        
        client = speech.SpeechClient()
        
        with open(audio.source, "rb") as audio_file:
            content = audio_file.read()
        
        audio_config = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=audio.sample_rate,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )
        
        response = client.recognize(config=config, audio=audio_config)
        
        text = " ".join(
            result.alternatives[0].transcript
            for result in response.results
        )
        
        confidence = sum(
            result.alternatives[0].confidence
            for result in response.results
        ) / len(response.results) if response.results else 1.0
        
        return TranscriptionResult(
            text=text,
            confidence=confidence,
            language="en"
        )
    
    def _transcribe_deepgram(self, audio: AudioInput) -> TranscriptionResult:
        """Transcribe using Deepgram API."""
        try:
            from deepgram import Deepgram
        except ImportError:
            raise ImportError("Deepgram not installed. Run: pip install deepgram-sdk")
        
        dg_client = Deepgram(os.getenv("DEEPGRAM_API_KEY"))
        
        with open(audio.source, "rb") as audio_file:
            source = {"buffer": audio_file.read(), "mimetype": f"audio/{audio.format}"}
        
        response = asyncio.run(
            dg_client.transcription.prerecorded(
                source,
                {"punctuate": True, "model": "nova-2"}
            )
        )
        
        transcript = response["results"]["channels"][0]["alternatives"][0]
        
        return TranscriptionResult(
            text=transcript["transcript"],
            confidence=transcript.get("confidence", 1.0),
            raw_response=response
        )


class PromptCompiler:
    """Compiles transcribed text into video prompts."""
    
    # Keywords for different aspects
    STYLE_KEYWORDS = {
        "cinematic": ["cinematic", "movie", "film", "hollywood", "dramatic", "epic"],
        "anime": ["anime", "animated", "cartoon", "ghibli", "japanese"],
        "realistic": ["realistic", "real", "photorealistic", "natural", "documentary"],
        "cyberpunk": ["cyberpunk", "neon", "futuristic", "sci-fi", "tech", "digital"],
        "fantasy": ["fantasy", "magical", "mystical", "fairy tale", "enchanted"],
        "horror": ["horror", "scary", "creepy", "dark", "spooky", "terrifying"],
        "comedy": ["comedy", "funny", "humorous", "silly", "lighthearted"],
        "noir": ["noir", "black and white", "detective", "moody", "shadowy"],
    }
    
    MOOD_KEYWORDS = {
        "happy": ["happy", "joyful", "cheerful", "bright", "uplifting"],
        "sad": ["sad", "melancholy", "somber", "emotional", "touching"],
        "tense": ["tense", "suspenseful", "thrilling", "exciting", "intense"],
        "peaceful": ["peaceful", "calm", "serene", "tranquil", "relaxing"],
        "mysterious": ["mysterious", "enigmatic", "intriguing", "curious"],
        "romantic": ["romantic", "love", "passionate", "intimate"],
        "action": ["action", "dynamic", "fast", "energetic", "explosive"],
    }
    
    CAMERA_KEYWORDS = {
        "pan": ["pan", "panning", "sweep"],
        "zoom": ["zoom", "zooming", "close up", "closeup"],
        "dolly": ["dolly", "tracking", "follow"],
        "crane": ["crane", "aerial", "overhead", "bird's eye"],
        "handheld": ["handheld", "shaky", "documentary style"],
        "static": ["static", "still", "fixed", "locked"],
        "slow motion": ["slow motion", "slow mo", "slowmo", "slowed down"],
        "time lapse": ["time lapse", "timelapse", "sped up"],
    }
    
    DURATION_PATTERNS = [
        (r"(\d+)\s*(?:second|sec|s)\b", 1),
        (r"(\d+)\s*(?:minute|min|m)\b", 60),
        (r"short\s*(?:video|clip)?", 5),
        (r"medium\s*(?:length)?(?:video|clip)?", 15),
        (r"long\s*(?:video|clip)?", 30),
        (r"quick\s*(?:video|clip)?", 3),
        (r"brief\s*(?:video|clip)?", 5),
    ]
    
    def __init__(self):
        self.simple_builder = SimpleBuilder()
    
    def compile(self, transcript: TranscriptionResult) -> VideoPrompt:
        """Compile transcript into video prompt."""
        text = transcript.text.lower()
        original = transcript.text
        
        # Extract components
        style = self._extract_style(text)
        mood = self._extract_mood(text)
        duration = self._extract_duration(text)
        camera_movements = self._extract_camera_movements(text)
        characters = self._extract_characters(original)
        template = self._match_template(text)
        shots = self._extract_shots(original, duration)
        
        # Clean and enhance description
        description = self._clean_description(original)
        description = self._enhance_description(description, style, mood)
        
        return VideoPrompt(
            description=description,
            style=style,
            duration=duration,
            shots=shots,
            characters=characters,
            mood=mood,
            camera_movements=camera_movements,
            template=template,
            confidence=transcript.confidence,
            original_transcript=original
        )
    
    def _extract_style(self, text: str) -> str:
        """Extract visual style from text."""
        for style, keywords in self.STYLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return style
        return "cinematic"  # default
    
    def _extract_mood(self, text: str) -> str:
        """Extract mood from text."""
        for mood, keywords in self.MOOD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    return mood
        return "neutral"
    
    def _extract_duration(self, text: str) -> int:
        """Extract duration from text."""
        for pattern, multiplier in self.DURATION_PATTERNS:
            match = re.search(pattern, text)
            if match:
                if match.groups():
                    return int(match.group(1)) * multiplier
                elif multiplier > 1:  # word-based duration
                    return multiplier
        return 8  # default 8 seconds
    
    def _extract_camera_movements(self, text: str) -> List[str]:
        """Extract camera movements from text."""
        movements = []
        for movement, keywords in self.CAMERA_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    movements.append(movement)
                    break
        return movements
    
    def _extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """Extract character descriptions from text."""
        characters = []
        
        # Pattern for "a/an [adjectives] person/man/woman/character named X"
        name_patterns = [
            r"(?:a|an)\s+([^,]+?)\s+(?:person|man|woman|character|guy|girl)\s+(?:named|called)\s+(\w+)",
            r"(\w+)\s+(?:is|who is)\s+(?:a|an)\s+([^,\.]+)",
            r"character\s+(?:named|called)\s+(\w+)",
        ]
        
        for pattern in name_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    characters.append({
                        "name": match.group(2) if "named" in pattern else match.group(1),
                        "description": match.group(1) if "named" in pattern else match.group(2)
                    })
                else:
                    characters.append({
                        "name": match.group(1),
                        "description": ""
                    })
        
        return characters
    
    def _match_template(self, text: str) -> Optional[str]:
        """Match text to a pre-built template if applicable."""
        template_keywords = {
            "sci-fi-lab": ["lab", "laboratory", "scientist", "experiment", "research"],
            "fantasy-quest": ["quest", "adventure", "hero", "journey", "magical"],
            "cyberpunk-city": ["cyberpunk", "neon city", "futuristic city", "tech noir"],
            "nature-journey": ["nature", "forest", "mountain", "ocean", "wildlife"],
            "comedy-moment": ["comedy", "funny", "humor", "joke", "laugh"],
        }
        
        for template, keywords in template_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return template
        
        return None
    
    def _extract_shots(self, text: str, total_duration: int) -> List[Dict[str, Any]]:
        """Extract individual shots from description."""
        shots = []
        
        # Split by common shot separators
        separators = [
            r"then\s+",
            r"next\s+",
            r"after that\s+",
            r"followed by\s+",
            r"cut to\s+",
            r"transition to\s+",
            r"\.\s+(?=[A-Z])",
        ]
        
        pattern = "|".join(separators)
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        
        if len(parts) <= 1:
            # Single shot
            shots.append({
                "description": text,
                "duration": total_duration
            })
        else:
            # Multiple shots - distribute duration
            shot_duration = max(3, total_duration // len(parts))
            for i, part in enumerate(parts):
                shots.append({
                    "description": part,
                    "duration": shot_duration,
                    "order": i + 1
                })
        
        return shots
    
    def _clean_description(self, text: str) -> str:
        """Clean up the description for video generation."""
        # Remove filler words and phrases
        fillers = [
            r"\b(?:um|uh|like|you know|basically|actually|literally)\b",
            r"\b(?:i want|i need|i'd like|can you|please|make me)\b",
            r"\b(?:a video of|a clip of|a scene of|generate|create)\b",
        ]
        
        cleaned = text
        for filler in fillers:
            cleaned = re.sub(filler, "", cleaned, flags=re.IGNORECASE)
        
        # Clean up whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        
        return cleaned
    
    def _enhance_description(self, description: str, style: str, mood: str) -> str:
        """Enhance description with style and mood context."""
        style_enhancements = {
            "cinematic": "cinematic shot, film quality, dramatic lighting",
            "anime": "anime style, vibrant colors, expressive characters",
            "realistic": "photorealistic, natural lighting, documentary style",
            "cyberpunk": "neon lights, rain-soaked streets, high tech low life",
            "fantasy": "magical atmosphere, ethereal lighting, otherworldly",
            "horror": "dark shadows, unsettling atmosphere, tension",
            "comedy": "bright lighting, dynamic expressions, comedic timing",
            "noir": "high contrast, dramatic shadows, moody atmosphere",
        }
        
        mood_enhancements = {
            "happy": "joyful energy, warm tones",
            "sad": "melancholic atmosphere, muted colors",
            "tense": "building suspense, tight framing",
            "peaceful": "serene mood, soft focus",
            "mysterious": "enigmatic atmosphere, selective focus",
            "romantic": "soft lighting, intimate framing",
            "action": "dynamic movement, energetic pacing",
        }
        
        enhanced = description
        
        if style in style_enhancements:
            enhanced = f"{enhanced}, {style_enhancements[style]}"
        
        if mood in mood_enhancements and mood != "neutral":
            enhanced = f"{enhanced}, {mood_enhancements[mood]}"
        
        return enhanced


class AudioAgent:
    """
    Main agent for audio-to-video generation.
    
    Takes audio descriptions and compiles them into MiniStudio prompts.
    """
    
    def __init__(
        self,
        transcription_provider: TranscriptionProvider = TranscriptionProvider.WHISPER_LOCAL,
        auto_generate: bool = False
    ):
        """
        Initialize the audio agent.
        
        Args:
            transcription_provider: Which transcription service to use
            auto_generate: If True, automatically generate video after processing
        """
        self.transcriber = AudioTranscriber(transcription_provider)
        self.compiler = PromptCompiler()
        self.simple_builder = SimpleBuilder()
        self.auto_generate = auto_generate
    
    def process_audio(self, audio_path: str) -> VideoPrompt:
        """
        Process an audio file and return a compiled video prompt.
        
        Args:
            audio_path: Path to audio file (.wav, .mp3, .m4a, etc.)
            
        Returns:
            VideoPrompt ready for video generation
        """
        print(f"🎤 Processing audio: {audio_path}")
        
        # Transcribe
        transcript = self.transcriber.transcribe(audio_path)
        print(f"📝 Transcribed: {transcript.text[:100]}...")
        
        # Compile to prompt
        prompt = self.compiler.compile(transcript)
        print(f"🎬 Compiled prompt:")
        print(f"   Style: {prompt.style}")
        print(f"   Duration: {prompt.duration}s")
        print(f"   Mood: {prompt.mood}")
        print(f"   Shots: {len(prompt.shots)}")
        
        return prompt
    
    def process_text(self, text: str) -> VideoPrompt:
        """
        Process text description directly (skip transcription).
        
        Useful for testing or when you have text input.
        """
        transcript = TranscriptionResult(text=text)
        return self.compiler.compile(transcript)
    
    def listen_and_generate(self, duration: float = 10.0) -> VideoPrompt:
        """
        Listen from microphone and generate prompt.
        
        Args:
            duration: How long to listen in seconds
            
        Returns:
            VideoPrompt from spoken description
        """
        print(f"🎤 Listening for {duration} seconds... Describe your video!")
        
        audio_path = self._record_audio(duration)
        prompt = self.process_audio(audio_path)
        
        # Clean up temp file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return prompt
    
    def _record_audio(self, duration: float) -> str:
        """Record audio from microphone."""
        try:
            import sounddevice as sd
            import soundfile as sf
        except ImportError:
            raise ImportError(
                "Audio recording requires sounddevice and soundfile.\n"
                "Run: pip install sounddevice soundfile"
            )
        
        sample_rate = 16000
        channels = 1
        
        print("🔴 Recording...")
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=channels,
            dtype='float32'
        )
        sd.wait()
        print("✅ Recording complete!")
        
        # Save to temp file
        temp_path = "temp_recording.wav"
        sf.write(temp_path, audio_data, sample_rate)
        
        return temp_path
    
    async def generate_video(self, prompt: VideoPrompt) -> str:
        """
        Generate video from compiled prompt.
        
        Args:
            prompt: VideoPrompt from process_audio or process_text
            
        Returns:
            Path to generated video file
        """
        print(f"🎬 Generating video...")
        print(f"   Description: {prompt.description[:80]}...")
        
        # Use template if matched
        if prompt.template and prompt.template in TEMPLATES:
            print(f"   Using template: {prompt.template}")
            from .simple_builder import generate_from_template
            return await generate_from_template(
                prompt.template,
                style=prompt.style,
                duration=prompt.duration
            )
        
        # Otherwise use description
        return await generate_video(
            description=prompt.description,
            style=prompt.style,
            duration=prompt.duration
        )
    
    def to_shot_config(self, prompt: VideoPrompt) -> ShotConfig:
        """Convert VideoPrompt to MiniStudio ShotConfig."""
        return self.simple_builder.create_shot_config(
            description=prompt.description,
            style=prompt.style,
            duration=prompt.duration
        )
    
    def to_dict(self, prompt: VideoPrompt) -> Dict[str, Any]:
        """Convert VideoPrompt to dictionary for JSON export."""
        return {
            "description": prompt.description,
            "style": prompt.style,
            "duration": prompt.duration,
            "shots": prompt.shots,
            "characters": prompt.characters,
            "mood": prompt.mood,
            "camera_movements": prompt.camera_movements,
            "template": prompt.template,
            "confidence": prompt.confidence,
            "original_transcript": prompt.original_transcript
        }
    
    def save_prompt(self, prompt: VideoPrompt, path: str):
        """Save prompt to JSON file."""
        with open(path, 'w') as f:
            json.dump(self.to_dict(prompt), f, indent=2)
        print(f"💾 Saved prompt to {path}")
    
    def load_prompt(self, path: str) -> VideoPrompt:
        """Load prompt from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return VideoPrompt(**data)


def interactive_audio_session():
    """
    Run an interactive audio-to-video session.
    
    Guides non-technical users through describing and generating videos.
    """
    print("""
╔══════════════════════════════════════════════════════════════════╗
║           🎤 MiniStudio Audio Agent 🎬                           ║
║                                                                  ║
║   Describe your video with your voice!                           ║
║   Just speak naturally about what you want to see.               ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Choose input method
    print("\nHow would you like to describe your video?")
    print("1. 🎤 Speak into microphone")
    print("2. 📁 Use an audio file")
    print("3. ⌨️  Type description (for testing)")
    print("4. ❌ Exit")
    
    choice = input("\nChoice (1-4): ").strip()
    
    # Determine transcription provider
    provider = TranscriptionProvider.WHISPER_LOCAL
    if os.getenv("OPENAI_API_KEY"):
        print("\n💡 OpenAI API key found - using Whisper API for better accuracy")
        provider = TranscriptionProvider.WHISPER_API
    
    agent = AudioAgent(transcription_provider=provider)
    
    if choice == "1":
        # Microphone input
        duration = input("How long to record? (default: 10 seconds): ").strip()
        duration = float(duration) if duration else 10.0
        prompt = agent.listen_and_generate(duration)
        
    elif choice == "2":
        # File input
        file_path = input("Path to audio file: ").strip()
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        prompt = agent.process_audio(file_path)
        
    elif choice == "3":
        # Text input
        print("\nDescribe your video (speak as if you were talking):")
        text = input("> ").strip()
        prompt = agent.process_text(text)
        
    elif choice == "4":
        print("👋 Goodbye!")
        return
        
    else:
        print("❌ Invalid choice")
        return
    
    # Display compiled prompt
    print("\n" + "="*60)
    print("📋 COMPILED VIDEO PROMPT")
    print("="*60)
    print(f"\n🎬 Description: {prompt.description}")
    print(f"🎨 Style: {prompt.style}")
    print(f"⏱️  Duration: {prompt.duration} seconds")
    print(f"😊 Mood: {prompt.mood}")
    
    if prompt.camera_movements:
        print(f"📷 Camera: {', '.join(prompt.camera_movements)}")
    
    if prompt.template:
        print(f"📦 Matched Template: {prompt.template}")
    
    if prompt.shots:
        print(f"\n📍 Shots ({len(prompt.shots)}):")
        for i, shot in enumerate(prompt.shots, 1):
            print(f"   {i}. {shot['description'][:50]}... ({shot['duration']}s)")
    
    print("\n" + "="*60)
    
    # Ask to generate
    generate = input("\n🎬 Generate this video? (y/n): ").strip().lower()
    
    if generate == 'y':
        print("\n⏳ Generating video...")
        try:
            video_path = asyncio.run(agent.generate_video(prompt))
            print(f"\n✅ Video generated: {video_path}")
        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            print("💡 Tip: Make sure you have a provider configured (see .env.example)")
    
    # Offer to save prompt
    save = input("\n💾 Save prompt to file? (y/n): ").strip().lower()
    if save == 'y':
        path = input("Save path (default: video_prompt.json): ").strip()
        path = path or "video_prompt.json"
        agent.save_prompt(prompt, path)


# Quick functions for simple usage
def audio_to_prompt(audio_path: str) -> VideoPrompt:
    """
    Quick function: Convert audio file to video prompt.
    
    Example:
        prompt = audio_to_prompt("describe_my_video.wav")
        print(prompt.description)
    """
    agent = AudioAgent()
    return agent.process_audio(audio_path)


def text_to_prompt(text: str) -> VideoPrompt:
    """
    Quick function: Convert text to video prompt.
    
    Example:
        prompt = text_to_prompt("A cinematic shot of a sunset over mountains")
        print(prompt.style)  # "cinematic"
    """
    agent = AudioAgent()
    return agent.process_text(text)


async def audio_to_video(audio_path: str) -> str:
    """
    Quick function: Audio file directly to video.
    
    Example:
        video = await audio_to_video("describe_my_video.wav")
    """
    agent = AudioAgent()
    prompt = agent.process_audio(audio_path)
    return await agent.generate_video(prompt)


if __name__ == "__main__":
    interactive_audio_session()
