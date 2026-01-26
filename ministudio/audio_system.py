"""
Multi-Track Audio System
========================
Professional audio management with separate tracks for narration, dialogue, music, and SFX.

Features:
- Multi-track audio timeline
- Voice generation integration
- Music cue management
- Audio mixing and sync
- Lip sync preparation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from datetime import datetime
import uuid


class AudioTrackType(Enum):
    """Types of audio tracks."""
    NARRATION = "narration"
    DIALOGUE = "dialogue"
    MUSIC = "music"
    SFX = "sfx"
    AMBIENT = "ambient"
    FOLEY = "foley"


class VoiceStyle(Enum):
    """Voice styles for narration/dialogue."""
    NARRATIVE = "narrative"
    CONVERSATIONAL = "conversational"
    DRAMATIC = "dramatic"
    WHISPER = "whisper"
    SHOUT = "shout"
    EMOTIONAL = "emotional"
    NEWSCAST = "newscast"
    STORYTELLING = "storytelling"


class MusicAction(Enum):
    """Music cue actions."""
    START = "start"
    CONTINUE = "continue"
    STOP = "stop"
    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    CROSSFADE = "crossfade"
    DUCK = "duck"  # Lower volume for dialogue
    UNDUCK = "unduck"
    SWELL = "swell"  # Dramatic increase


@dataclass
class VoiceSettings:
    """Voice generation settings."""
    voice_id: Optional[str] = None
    voice_name: Optional[str] = None
    
    # Characteristics
    pitch: float = 1.0  # 0.5 - 2.0
    speed: float = 1.0  # 0.5 - 2.0
    
    # Style
    style: VoiceStyle = VoiceStyle.NARRATIVE
    emotion: str = "neutral"
    emotion_intensity: float = 0.5
    
    # Quality
    stability: float = 0.5
    similarity_boost: float = 0.75
    
    # Provider-specific
    provider: Optional[str] = None  # elevenlabs, google, azure, etc.
    provider_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "voice_id": self.voice_id,
            "voice_name": self.voice_name,
            "pitch": self.pitch,
            "speed": self.speed,
            "style": self.style.value,
            "emotion": self.emotion,
            "emotion_intensity": self.emotion_intensity,
            "stability": self.stability,
            "similarity_boost": self.similarity_boost,
            "provider": self.provider,
            "provider_config": self.provider_config
        }


@dataclass
class AudioClip:
    """A single audio clip."""
    clip_id: str = field(default_factory=lambda: f"clip_{uuid.uuid4().hex[:8]}")
    track_type: AudioTrackType = AudioTrackType.NARRATION
    
    # Content
    content: str = ""  # Text for TTS or path to audio file
    is_file: bool = False  # If True, content is a file path
    
    # Timing (in seconds)
    start_time: float = 0.0
    duration: Optional[float] = None  # None = auto from TTS
    end_time: Optional[float] = None
    
    # Volume and mixing
    volume: float = 1.0  # 0.0 - 2.0
    pan: float = 0.0  # -1.0 (left) to 1.0 (right)
    
    # Fade
    fade_in: float = 0.0
    fade_out: float = 0.0
    
    # Voice settings (for TTS)
    voice_settings: Optional[VoiceSettings] = None
    
    # Character association
    character_id: Optional[str] = None
    
    # Generated file
    output_path: Optional[str] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "track_type": self.track_type.value,
            "content": self.content,
            "is_file": self.is_file,
            "start_time": self.start_time,
            "duration": self.duration,
            "end_time": self.end_time,
            "volume": self.volume,
            "pan": self.pan,
            "fade_in": self.fade_in,
            "fade_out": self.fade_out,
            "voice_settings": self.voice_settings.to_dict() if self.voice_settings else None,
            "character_id": self.character_id,
            "output_path": self.output_path,
            "metadata": self.metadata
        }


@dataclass
class MusicCue:
    """A music cue for scoring."""
    cue_id: str = field(default_factory=lambda: f"cue_{uuid.uuid4().hex[:8]}")
    
    # Track reference
    track_id: Optional[str] = None  # Reference to music track
    track_path: Optional[str] = None  # Path to music file
    track_description: str = ""  # For AI music generation
    
    # Timing
    start_time: float = 0.0
    action: MusicAction = MusicAction.START
    
    # Volume
    volume: float = 0.5
    target_volume: Optional[float] = None  # For fades
    
    # Transition
    transition_duration: float = 1.0  # For fades
    
    # Mood/style hints
    mood: str = "neutral"
    intensity: float = 0.5
    tempo: Optional[str] = None  # slow, medium, fast
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cue_id": self.cue_id,
            "track_id": self.track_id,
            "track_path": self.track_path,
            "track_description": self.track_description,
            "start_time": self.start_time,
            "action": self.action.value,
            "volume": self.volume,
            "target_volume": self.target_volume,
            "transition_duration": self.transition_duration,
            "mood": self.mood,
            "intensity": self.intensity,
            "tempo": self.tempo
        }


@dataclass
class SFXEvent:
    """A sound effect event."""
    event_id: str = field(default_factory=lambda: f"sfx_{uuid.uuid4().hex[:8]}")
    
    # Content
    sfx_name: str = ""  # Name or description
    sfx_path: Optional[str] = None  # Path to file
    
    # Timing
    start_time: float = 0.0
    duration: Optional[float] = None
    
    # Mixing
    volume: float = 1.0
    pan: float = 0.0
    
    # Spatial audio hints
    distance: float = 1.0  # 0.0 (close) to 1.0 (far)
    reverb: float = 0.0  # Amount of reverb
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "sfx_name": self.sfx_name,
            "sfx_path": self.sfx_path,
            "start_time": self.start_time,
            "duration": self.duration,
            "volume": self.volume,
            "pan": self.pan,
            "distance": self.distance,
            "reverb": self.reverb
        }


@dataclass
class AudioTrack:
    """A complete audio track."""
    track_id: str = field(default_factory=lambda: f"track_{uuid.uuid4().hex[:8]}")
    track_type: AudioTrackType = AudioTrackType.NARRATION
    name: str = ""
    
    # Track settings
    volume: float = 1.0
    pan: float = 0.0
    muted: bool = False
    solo: bool = False
    
    # Clips on this track
    clips: List[AudioClip] = field(default_factory=list)
    
    # For music tracks
    music_cues: List[MusicCue] = field(default_factory=list)
    
    # For SFX tracks
    sfx_events: List[SFXEvent] = field(default_factory=list)
    
    def add_clip(self, clip: AudioClip) -> AudioClip:
        """Add a clip to this track."""
        clip.track_type = self.track_type
        self.clips.append(clip)
        return clip
    
    def add_music_cue(self, cue: MusicCue) -> MusicCue:
        """Add a music cue."""
        self.music_cues.append(cue)
        return cue
    
    def add_sfx(self, sfx: SFXEvent) -> SFXEvent:
        """Add an SFX event."""
        self.sfx_events.append(sfx)
        return sfx
    
    def get_duration(self) -> float:
        """Get the total duration of this track."""
        max_time = 0.0
        
        for clip in self.clips:
            end_time = clip.end_time
            if end_time is None and clip.duration:
                end_time = clip.start_time + clip.duration
            if end_time and end_time > max_time:
                max_time = end_time
        
        for sfx in self.sfx_events:
            end_time = sfx.start_time + (sfx.duration or 0)
            if end_time > max_time:
                max_time = end_time
        
        return max_time
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "track_type": self.track_type.value,
            "name": self.name,
            "volume": self.volume,
            "pan": self.pan,
            "muted": self.muted,
            "solo": self.solo,
            "clips": [c.to_dict() for c in self.clips],
            "music_cues": [m.to_dict() for m in self.music_cues],
            "sfx_events": [s.to_dict() for s in self.sfx_events]
        }


@dataclass
class AudioTimeline:
    """Complete audio timeline for a video."""
    timeline_id: str = field(default_factory=lambda: f"timeline_{uuid.uuid4().hex[:8]}")
    
    # Tracks
    tracks: Dict[str, AudioTrack] = field(default_factory=dict)
    
    # Master settings
    master_volume: float = 1.0
    
    # Output settings
    sample_rate: int = 44100
    channels: int = 2
    bit_depth: int = 16
    
    # Character voices (shared across tracks)
    character_voices: Dict[str, VoiceSettings] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize default tracks."""
        if not self.tracks:
            self._create_default_tracks()
    
    def _create_default_tracks(self):
        """Create standard audio tracks."""
        default_tracks = [
            (AudioTrackType.NARRATION, "Narration", 1.0),
            (AudioTrackType.DIALOGUE, "Dialogue", 1.0),
            (AudioTrackType.MUSIC, "Music", 0.5),
            (AudioTrackType.SFX, "Sound Effects", 0.8),
            (AudioTrackType.AMBIENT, "Ambient", 0.3)
        ]
        
        for track_type, name, volume in default_tracks:
            track = AudioTrack(
                track_type=track_type,
                name=name,
                volume=volume
            )
            self.tracks[track.track_id] = track
    
    def get_track(self, track_type: AudioTrackType) -> Optional[AudioTrack]:
        """Get track by type."""
        for track in self.tracks.values():
            if track.track_type == track_type:
                return track
        return None
    
    def add_narration(
        self,
        text: str,
        start_time: float = 0.0,
        voice_settings: Optional[VoiceSettings] = None
    ) -> AudioClip:
        """Add narration clip."""
        track = self.get_track(AudioTrackType.NARRATION)
        if not track:
            track = AudioTrack(
                track_type=AudioTrackType.NARRATION,
                name="Narration"
            )
            self.tracks[track.track_id] = track
        
        clip = AudioClip(
            track_type=AudioTrackType.NARRATION,
            content=text,
            start_time=start_time,
            voice_settings=voice_settings
        )
        track.add_clip(clip)
        return clip
    
    def add_dialogue(
        self,
        character_id: str,
        text: str,
        start_time: float = 0.0,
        emotion: str = "neutral"
    ) -> AudioClip:
        """Add character dialogue."""
        track = self.get_track(AudioTrackType.DIALOGUE)
        if not track:
            track = AudioTrack(
                track_type=AudioTrackType.DIALOGUE,
                name="Dialogue"
            )
            self.tracks[track.track_id] = track
        
        # Get character voice
        voice = self.character_voices.get(character_id)
        if voice:
            voice = VoiceSettings(**{**voice.__dict__})
            voice.emotion = emotion
        
        clip = AudioClip(
            track_type=AudioTrackType.DIALOGUE,
            content=text,
            start_time=start_time,
            character_id=character_id,
            voice_settings=voice
        )
        track.add_clip(clip)
        return clip
    
    def add_music(
        self,
        track_path_or_description: str,
        start_time: float = 0.0,
        action: MusicAction = MusicAction.START,
        volume: float = 0.5
    ) -> MusicCue:
        """Add music cue."""
        track = self.get_track(AudioTrackType.MUSIC)
        if not track:
            track = AudioTrack(
                track_type=AudioTrackType.MUSIC,
                name="Music"
            )
            self.tracks[track.track_id] = track
        
        # Determine if it's a file path or description
        is_file = Path(track_path_or_description).exists()
        
        cue = MusicCue(
            track_path=track_path_or_description if is_file else None,
            track_description=track_path_or_description if not is_file else "",
            start_time=start_time,
            action=action,
            volume=volume
        )
        track.add_music_cue(cue)
        return cue
    
    def add_sfx(
        self,
        sfx_name: str,
        start_time: float = 0.0,
        volume: float = 1.0,
        sfx_path: Optional[str] = None
    ) -> SFXEvent:
        """Add sound effect."""
        track = self.get_track(AudioTrackType.SFX)
        if not track:
            track = AudioTrack(
                track_type=AudioTrackType.SFX,
                name="Sound Effects"
            )
            self.tracks[track.track_id] = track
        
        sfx = SFXEvent(
            sfx_name=sfx_name,
            sfx_path=sfx_path,
            start_time=start_time,
            volume=volume
        )
        track.add_sfx(sfx)
        return sfx
    
    def set_character_voice(
        self,
        character_id: str,
        voice_settings: VoiceSettings
    ):
        """Set voice for a character."""
        self.character_voices[character_id] = voice_settings
    
    def get_duration(self) -> float:
        """Get total timeline duration."""
        max_duration = 0.0
        for track in self.tracks.values():
            track_duration = track.get_duration()
            if track_duration > max_duration:
                max_duration = track_duration
        return max_duration
    
    def get_clips_at_time(self, time: float) -> List[AudioClip]:
        """Get all clips active at a given time."""
        active = []
        for track in self.tracks.values():
            for clip in track.clips:
                start = clip.start_time
                end = clip.end_time or (start + (clip.duration or 0))
                if start <= time <= end:
                    active.append(clip)
        return active
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeline_id": self.timeline_id,
            "tracks": {k: v.to_dict() for k, v in self.tracks.items()},
            "master_volume": self.master_volume,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "bit_depth": self.bit_depth,
            "character_voices": {k: v.to_dict() for k, v in self.character_voices.items()}
        }
    
    def to_json(self, pretty: bool = True) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2 if pretty else None)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AudioTimeline":
        """Create from dictionary."""
        timeline = cls(
            timeline_id=data.get("timeline_id"),
            master_volume=data.get("master_volume", 1.0),
            sample_rate=data.get("sample_rate", 44100),
            channels=data.get("channels", 2),
            bit_depth=data.get("bit_depth", 16)
        )
        
        # Parse character voices
        if "character_voices" in data:
            for char_id, voice_data in data["character_voices"].items():
                timeline.character_voices[char_id] = VoiceSettings(
                    voice_id=voice_data.get("voice_id"),
                    voice_name=voice_data.get("voice_name"),
                    pitch=voice_data.get("pitch", 1.0),
                    speed=voice_data.get("speed", 1.0),
                    style=VoiceStyle(voice_data.get("style", "narrative")),
                    emotion=voice_data.get("emotion", "neutral"),
                    provider=voice_data.get("provider"),
                    provider_config=voice_data.get("provider_config", {})
                )
        
        return timeline


# ============ Audio Generation Interface ============

class AudioGenerator:
    """Interface for generating audio from timeline."""
    
    def __init__(
        self,
        tts_provider: Optional[Callable] = None,
        music_provider: Optional[Callable] = None,
        sfx_provider: Optional[Callable] = None
    ):
        self.tts_provider = tts_provider
        self.music_provider = music_provider
        self.sfx_provider = sfx_provider
        self._cache: Dict[str, str] = {}
    
    async def generate_clip_audio(
        self,
        clip: AudioClip,
        output_dir: Path
    ) -> str:
        """Generate audio for a clip."""
        if clip.is_file and clip.content:
            return clip.content
        
        if not self.tts_provider:
            raise ValueError("No TTS provider configured")
        
        # Create cache key
        cache_key = f"{clip.content}_{clip.voice_settings}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Generate audio
        output_path = output_dir / f"{clip.clip_id}.wav"
        
        if asyncio.iscoroutinefunction(self.tts_provider):
            await self.tts_provider(
                text=clip.content,
                voice_settings=clip.voice_settings,
                output_path=str(output_path)
            )
        else:
            self.tts_provider(
                text=clip.content,
                voice_settings=clip.voice_settings,
                output_path=str(output_path)
            )
        
        clip.output_path = str(output_path)
        self._cache[cache_key] = str(output_path)
        
        return str(output_path)
    
    async def generate_timeline_audio(
        self,
        timeline: AudioTimeline,
        output_dir: Path
    ) -> Dict[str, List[str]]:
        """Generate all audio for a timeline."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {
            "narration": [],
            "dialogue": [],
            "music": [],
            "sfx": []
        }
        
        for track in timeline.tracks.values():
            for clip in track.clips:
                if not clip.is_file and clip.content:
                    path = await self.generate_clip_audio(clip, output_dir)
                    results[track.track_type.value.lower()].append(path)
        
        return results


# ============ Lip Sync Data Generation ============

@dataclass
class LipSyncFrame:
    """A single frame of lip sync data."""
    time: float
    viseme: str  # Viseme code (mouth shape)
    intensity: float = 1.0


@dataclass
class LipSyncData:
    """Complete lip sync data for an audio clip."""
    clip_id: str
    character_id: Optional[str]
    duration: float
    frames: List[LipSyncFrame] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "character_id": self.character_id,
            "duration": self.duration,
            "frames": [
                {"time": f.time, "viseme": f.viseme, "intensity": f.intensity}
                for f in self.frames
            ]
        }


# Standard viseme set (compatible with most TTS systems)
VISEMES = {
    "SILENCE": "sil",  # Closed mouth
    "AA": "aa",  # Open mouth (ah)
    "AE": "ae",  # Slightly open (cat)
    "AH": "ah",  # Open (about)
    "AO": "ao",  # Round (dog)
    "AW": "aw",  # Round to open (cow)
    "AY": "ay",  # Open to spread (my)
    "B": "bp",  # Closed lips (b, m, p)
    "CH": "ch",  # Rounded, narrow (ch, j, sh)
    "D": "dt",  # Tongue behind teeth (d, t, n)
    "EH": "eh",  # Slight smile (bed)
    "ER": "er",  # Rounded, r-colored
    "EY": "ey",  # Spread (say)
    "F": "fv",  # Lower lip under teeth (f, v)
    "G": "kg",  # Back of tongue (g, k)
    "IH": "ih",  # Slight spread (bit)
    "IY": "iy",  # Spread smile (see)
    "K": "kg",  # Back of tongue
    "L": "l",   # Tongue up
    "OW": "ow",  # Round (go)
    "OY": "oy",  # Round to spread (boy)
    "R": "r",   # Rounded
    "S": "s",   # Teeth together (s, z)
    "TH": "th",  # Tongue between teeth
    "UH": "uh",  # Rounded (book)
    "UW": "uw",  # Tight round (too)
    "W": "w",   # Rounded, narrow
    "Y": "y",   # Spread, narrow
}


def estimate_lip_sync(
    text: str,
    duration: float,
    words_per_minute: float = 150
) -> List[LipSyncFrame]:
    """
    Estimate basic lip sync frames from text.
    This is a simple approximation - real systems use audio analysis.
    """
    frames = []
    
    # Calculate time per word
    words = text.split()
    if not words:
        return [LipSyncFrame(0.0, "sil")]
    
    time_per_word = duration / len(words)
    
    current_time = 0.0
    for word in words:
        # Simple vowel/consonant detection for visemes
        for i, char in enumerate(word.lower()):
            progress = i / max(1, len(word))
            char_time = current_time + (progress * time_per_word)
            
            if char in 'aeiou':
                # Vowel visemes
                viseme_map = {'a': 'aa', 'e': 'eh', 'i': 'iy', 'o': 'ow', 'u': 'uw'}
                frames.append(LipSyncFrame(char_time, viseme_map.get(char, 'aa'), 0.8))
            elif char in 'bmp':
                frames.append(LipSyncFrame(char_time, 'bp', 1.0))
            elif char in 'fv':
                frames.append(LipSyncFrame(char_time, 'fv', 0.9))
            elif char in 'dtnl':
                frames.append(LipSyncFrame(char_time, 'dt', 0.7))
            elif char in 'szc':
                frames.append(LipSyncFrame(char_time, 's', 0.6))
            elif char in 'kg':
                frames.append(LipSyncFrame(char_time, 'kg', 0.5))
            elif char in 'wr':
                frames.append(LipSyncFrame(char_time, 'w', 0.7))
        
        current_time += time_per_word
    
    # Add closing frame
    frames.append(LipSyncFrame(duration, 'sil', 0.0))
    
    return frames


# ============ Audio Mixing Utilities ============

@dataclass
class MixSettings:
    """Settings for audio mixing."""
    
    # Track volumes (relative)
    narration_volume: float = 1.0
    dialogue_volume: float = 1.0
    music_volume: float = 0.5
    sfx_volume: float = 0.8
    ambient_volume: float = 0.3
    
    # Ducking (lower music during speech)
    duck_music_during_speech: bool = True
    duck_amount: float = 0.3  # How much to reduce
    duck_attack: float = 0.1  # Seconds to duck
    duck_release: float = 0.5  # Seconds to return
    
    # Compression
    compress_output: bool = True
    compression_ratio: float = 4.0
    compression_threshold: float = -12.0  # dB
    
    # Normalization
    normalize_output: bool = True
    target_loudness: float = -14.0  # LUFS
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_volumes": {
                "narration": self.narration_volume,
                "dialogue": self.dialogue_volume,
                "music": self.music_volume,
                "sfx": self.sfx_volume,
                "ambient": self.ambient_volume
            },
            "ducking": {
                "enabled": self.duck_music_during_speech,
                "amount": self.duck_amount,
                "attack": self.duck_attack,
                "release": self.duck_release
            },
            "compression": {
                "enabled": self.compress_output,
                "ratio": self.compression_ratio,
                "threshold": self.compression_threshold
            },
            "normalization": {
                "enabled": self.normalize_output,
                "target_loudness": self.target_loudness
            }
        }


def create_mix_timeline(
    timeline: AudioTimeline,
    mix_settings: MixSettings = None
) -> Dict[str, Any]:
    """
    Create a mix timeline that can be used by audio processing tools.
    Returns EDL-like structure for mixing.
    """
    if mix_settings is None:
        mix_settings = MixSettings()
    
    events = []
    
    for track in timeline.tracks.values():
        volume_multiplier = {
            AudioTrackType.NARRATION: mix_settings.narration_volume,
            AudioTrackType.DIALOGUE: mix_settings.dialogue_volume,
            AudioTrackType.MUSIC: mix_settings.music_volume,
            AudioTrackType.SFX: mix_settings.sfx_volume,
            AudioTrackType.AMBIENT: mix_settings.ambient_volume
        }.get(track.track_type, 1.0)
        
        # Add clip events
        for clip in track.clips:
            events.append({
                "type": "clip",
                "track": track.track_type.value,
                "clip_id": clip.clip_id,
                "source": clip.output_path or clip.content,
                "start_time": clip.start_time,
                "duration": clip.duration,
                "volume": clip.volume * volume_multiplier * track.volume,
                "pan": clip.pan,
                "fade_in": clip.fade_in,
                "fade_out": clip.fade_out
            })
        
        # Add music cues
        for cue in track.music_cues:
            events.append({
                "type": "music_cue",
                "cue_id": cue.cue_id,
                "track": cue.track_path,
                "description": cue.track_description,
                "start_time": cue.start_time,
                "action": cue.action.value,
                "volume": cue.volume * volume_multiplier,
                "transition_duration": cue.transition_duration
            })
        
        # Add SFX events
        for sfx in track.sfx_events:
            events.append({
                "type": "sfx",
                "event_id": sfx.event_id,
                "name": sfx.sfx_name,
                "source": sfx.sfx_path,
                "start_time": sfx.start_time,
                "duration": sfx.duration,
                "volume": sfx.volume * volume_multiplier,
                "pan": sfx.pan
            })
    
    # Sort by start time
    events.sort(key=lambda x: x.get("start_time", 0))
    
    return {
        "version": "1.0",
        "duration": timeline.get_duration(),
        "sample_rate": timeline.sample_rate,
        "channels": timeline.channels,
        "events": events,
        "mix_settings": mix_settings.to_dict()
    }


# ============ Duration Estimation ============

def estimate_narration_duration(
    text: str,
    words_per_minute: float = 150,
    min_duration: float = 1.0
) -> float:
    """Estimate narration duration from text."""
    word_count = len(text.split())
    duration = (word_count / words_per_minute) * 60
    return max(duration, min_duration)


def estimate_dialogue_duration(
    text: str,
    emotion: str = "neutral",
    words_per_minute: float = 160
) -> float:
    """Estimate dialogue duration, accounting for emotion."""
    # Emotional adjustments
    speed_modifiers = {
        "excited": 1.2,
        "angry": 1.1,
        "sad": 0.8,
        "thoughtful": 0.85,
        "nervous": 1.15,
        "calm": 0.9,
        "neutral": 1.0
    }
    
    modifier = speed_modifiers.get(emotion.lower(), 1.0)
    adjusted_wpm = words_per_minute * modifier
    
    word_count = len(text.split())
    return (word_count / adjusted_wpm) * 60
