# Audio Agent Guide

> **Speak your video into existence!** 🎤 → 🎬

The Audio Agent lets you describe videos with your voice and automatically compiles them into MiniStudio prompts.

---

## Quick Start

### Option 1: Interactive Mode (Easiest)
```bash
python -m ministudio.audio_agent
```
This launches a guided session where you can:
- Speak into your microphone
- Use an audio file
- Type a description

### Option 2: One-liner
```python
from ministudio.audio_agent import audio_to_prompt

prompt = audio_to_prompt("my_description.wav")
print(prompt.description)  # Your compiled prompt!
```

### Option 3: Text Input (Testing)
```python
from ministudio.audio_agent import text_to_prompt

prompt = text_to_prompt("A cinematic sunset over mountains, 10 seconds")
```

---

## How It Works

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐    ┌─────────────┐
│ Your Voice  │ →  │ Transcription │ →  │   Compile   │ →  │ Video Prompt│
│  (Audio)    │    │  (Whisper)    │    │  (Parser)   │    │  (Ready!)   │
└─────────────┘    └──────────────┘    └─────────────┘    └─────────────┘
```

1. **You speak** - Describe what you want naturally
2. **We transcribe** - Using Whisper or cloud APIs
3. **We compile** - Extract style, duration, mood, shots
4. **Ready to generate** - Clean prompt for MiniStudio

---

## What Gets Extracted

When you speak, the agent understands:

| Component | Example Phrases |
|-----------|-----------------|
| **Style** | "cinematic", "anime", "cyberpunk", "realistic" |
| **Duration** | "10 seconds", "30 sec", "short clip", "long video" |
| **Mood** | "happy", "tense", "mysterious", "peaceful" |
| **Camera** | "slow motion", "zoom in", "pan across", "aerial shot" |
| **Shots** | "then cut to", "next show", "followed by" |
| **Characters** | "a person named Sarah", "character called Max" |

### Example

**You say:**
> "Make me a 20 second cyberpunk video of a hacker in a neon room, 
> then cut to the city streets with rain, use slow motion"

**Agent extracts:**
- Style: `cyberpunk`
- Duration: `20` seconds
- Shots: 2 (room → streets)
- Camera: `slow motion`
- Mood: inferred from style

---

## Installation

### Basic (Local Whisper)
```bash
pip install openai-whisper
```

### With Microphone Support
```bash
pip install sounddevice soundfile openai-whisper
```

### With Cloud Transcription
```bash
# OpenAI Whisper API
pip install openai

# Google Cloud Speech
pip install google-cloud-speech

# Deepgram
pip install deepgram-sdk
```

---

## Usage Examples

### From Audio File
```python
from ministudio.audio_agent import AudioAgent

agent = AudioAgent()
prompt = agent.process_audio("describe_video.wav")

print(f"Style: {prompt.style}")
print(f"Duration: {prompt.duration}s")
print(f"Description: {prompt.description}")
```

### From Microphone
```python
from ministudio.audio_agent import AudioAgent

agent = AudioAgent()
prompt = agent.listen_and_generate(duration=10)  # Records for 10 seconds
```

### Generate Video
```python
import asyncio
from ministudio.audio_agent import AudioAgent

agent = AudioAgent()
prompt = agent.process_audio("my_video.wav")

# Generate the video
video_path = asyncio.run(agent.generate_video(prompt))
print(f"Video saved: {video_path}")
```

### Save/Load Prompts
```python
from ministudio.audio_agent import AudioAgent

agent = AudioAgent()
prompt = agent.process_audio("my_video.wav")

# Save for later
agent.save_prompt(prompt, "video_prompt.json")

# Load and use
loaded = agent.load_prompt("video_prompt.json")
```

---

## Transcription Providers

| Provider | Setup | Best For |
|----------|-------|----------|
| **Whisper Local** | `pip install openai-whisper` | Free, offline, good accuracy |
| **Whisper API** | Set `OPENAI_API_KEY` | Best accuracy, fast |
| **Google Speech** | Set up GCP credentials | Noisy audio, long files |
| **Deepgram** | Set `DEEPGRAM_API_KEY` | Real-time, fast |

### Choosing a Provider
```python
from ministudio.audio_agent import AudioAgent, TranscriptionProvider

# Local (default, free)
agent = AudioAgent(transcription_provider=TranscriptionProvider.WHISPER_LOCAL)

# OpenAI API (best accuracy)
agent = AudioAgent(transcription_provider=TranscriptionProvider.WHISPER_API)

# Google Cloud
agent = AudioAgent(transcription_provider=TranscriptionProvider.GOOGLE_SPEECH)
```

---

## Tips for Best Results

### ✅ Do
- Speak clearly and naturally
- Mention style explicitly: "cinematic", "anime", etc.
- Say duration: "10 seconds", "30 sec"
- Describe shots: "start with X, then Y"
- Name characters: "a woman named Sarah"

### ❌ Don't
- Rush through description
- Use very technical camera terms
- Speak in incomplete sentences
- Mumble or whisper

### Example Good Description
> "I want a 15 second cinematic video. Start with a close-up of a coffee cup, 
> then slowly zoom out to reveal a cozy cafe. The mood should be peaceful 
> and warm. Use soft morning light."

**Extracted:**
- Style: cinematic
- Duration: 15s
- Shots: 2 (coffee cup → cafe)
- Camera: zoom out
- Mood: peaceful

---

## API Reference

### AudioAgent
```python
class AudioAgent:
    def __init__(
        self,
        transcription_provider: TranscriptionProvider = WHISPER_LOCAL,
        auto_generate: bool = False
    )
    
    def process_audio(self, audio_path: str) -> VideoPrompt
    def process_text(self, text: str) -> VideoPrompt
    def listen_and_generate(self, duration: float = 10.0) -> VideoPrompt
    async def generate_video(self, prompt: VideoPrompt) -> str
    def save_prompt(self, prompt: VideoPrompt, path: str)
    def load_prompt(self, path: str) -> VideoPrompt
```

### VideoPrompt
```python
@dataclass
class VideoPrompt:
    description: str
    style: str = "cinematic"
    duration: int = 8
    shots: List[Dict]
    characters: List[Dict]
    mood: str
    camera_movements: List[str]
    template: Optional[str]
    confidence: float
    original_transcript: str
```

### Quick Functions
```python
# Audio file to prompt
prompt = audio_to_prompt("file.wav")

# Text to prompt
prompt = text_to_prompt("description here")

# Audio directly to video
video = await audio_to_video("file.wav")
```

---

## Troubleshooting

### "Whisper not installed"
```bash
pip install openai-whisper
```

### "No audio device found"
```bash
pip install sounddevice soundfile
```
Also check your microphone is connected and enabled.

### Poor transcription accuracy
- Try Whisper API: Set `OPENAI_API_KEY`
- Use larger model: `WHISPER_MODEL_SIZE=medium`
- Ensure clear audio without background noise

### Prompt doesn't match what I said
- Speak more slowly
- Use explicit keywords (style, duration)
- Check the `original_transcript` field

---

## Environment Variables

```bash
# Whisper model size (tiny, base, small, medium, large)
WHISPER_MODEL_SIZE=base

# OpenAI API (for Whisper API)
OPENAI_API_KEY=sk-...

# Google Cloud (for Google Speech)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Deepgram
DEEPGRAM_API_KEY=...
```

---

## Next Steps

1. **Try it out**: `python -m ministudio.audio_agent`
2. **See examples**: `examples/audio_agent_examples.py`
3. **Generate videos**: Connect to your provider
4. **Save prompts**: Build a library of voice-created prompts

---

**Questions?** Check [configuration guide](configuration_and_secrets.md) for provider setup.
