"""
Audio Transcription System
==========================
Automatic speech recognition and transcription with subtitle generation.

Features:
- Speech-to-text using Whisper models
- Word-level timestamps for karaoke-style subtitles
- Multiple language support
- Speaker diarization (TODO)
- Subtitle file generation (SRT, VTT)

Dependencies:
    pip install openai-whisper
    
Or for faster inference:
    pip install faster-whisper

Optional (for speaker diarization):
    pip install pyannote.audio
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============ Transcription Data Structures ============

@dataclass
class Word:
    """A single transcribed word with timing."""
    
    text: str
    start: float  # seconds
    end: float  # seconds
    confidence: float = 1.0
    speaker: Optional[str] = None
    
    @property
    def duration(self) -> float:
        return self.end - self.start
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "confidence": self.confidence,
            "speaker": self.speaker
        }


@dataclass
class Segment:
    """A transcription segment (typically a sentence or phrase)."""
    
    text: str
    start: float
    end: float
    words: List[Word] = field(default_factory=list)
    confidence: float = 1.0
    speaker: Optional[str] = None
    language: Optional[str] = None
    
    @property
    def duration(self) -> float:
        return self.end - self.start
    
    @property
    def word_count(self) -> int:
        return len(self.words) if self.words else len(self.text.split())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "start": self.start,
            "end": self.end,
            "words": [w.to_dict() for w in self.words],
            "confidence": self.confidence,
            "speaker": self.speaker,
            "language": self.language
        }


@dataclass
class Transcription:
    """Complete transcription result."""
    
    text: str  # Full text
    segments: List[Segment] = field(default_factory=list)
    language: str = "en"
    duration: float = 0.0
    
    # Source info
    source_file: Optional[str] = None
    model_name: Optional[str] = None
    
    # Processing metadata
    word_count: int = 0
    processing_time: float = 0.0
    
    def get_words(self) -> List[Word]:
        """Get all words across all segments."""
        words = []
        for segment in self.segments:
            words.extend(segment.words)
        return words
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "segments": [s.to_dict() for s in self.segments],
            "language": self.language,
            "duration": self.duration,
            "source_file": self.source_file,
            "model_name": self.model_name
        }
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
    
    def save_json(self, path: str) -> str:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        return path


# ============ Transcription Engine ============

class TranscriptionModel(Enum):
    """Available transcription models."""
    
    # OpenAI Whisper models
    WHISPER_TINY = "tiny"
    WHISPER_BASE = "base"
    WHISPER_SMALL = "small"
    WHISPER_MEDIUM = "medium"
    WHISPER_LARGE = "large"
    WHISPER_LARGE_V2 = "large-v2"
    WHISPER_LARGE_V3 = "large-v3"
    
    # Faster Whisper variants
    FASTER_WHISPER_TINY = "faster-tiny"
    FASTER_WHISPER_BASE = "faster-base"
    FASTER_WHISPER_SMALL = "faster-small"
    FASTER_WHISPER_MEDIUM = "faster-medium"
    FASTER_WHISPER_LARGE = "faster-large-v2"


@dataclass
class TranscriptionConfig:
    """Transcription configuration."""
    
    model: str = "base"
    language: Optional[str] = None  # Auto-detect if None
    task: str = "transcribe"  # or "translate"
    
    # Word-level timestamps
    word_timestamps: bool = True
    
    # VAD (Voice Activity Detection)
    vad_filter: bool = True
    
    # Quality settings
    beam_size: int = 5
    temperature: float = 0.0
    compression_ratio_threshold: float = 2.4
    
    # Performance
    device: str = "auto"  # "cpu", "cuda", or "auto"
    compute_type: str = "auto"  # "int8", "float16", "float32"


class Transcriber:
    """
    Audio/video transcription using Whisper.
    
    Supports both openai-whisper and faster-whisper backends.
    """
    
    def __init__(self, config: Optional[TranscriptionConfig] = None):
        self.config = config or TranscriptionConfig()
        self._model = None
        self._backend = self._detect_backend()
    
    def _detect_backend(self) -> str:
        """Detect available transcription backend."""
        try:
            from faster_whisper import WhisperModel
            return "faster-whisper"
        except ImportError:
            pass
        
        try:
            import whisper
            return "openai-whisper"
        except ImportError:
            pass
        
        return "none"
    
    def is_available(self) -> bool:
        """Check if transcription is available."""
        return self._backend != "none"
    
    def _load_model(self):
        """Load the transcription model."""
        if self._model is not None:
            return
        
        model_name = self.config.model
        
        # Remove "faster-" prefix if using faster-whisper
        if model_name.startswith("faster-"):
            model_name = model_name[7:]
        
        if self._backend == "faster-whisper":
            from faster_whisper import WhisperModel
            
            device = self.config.device
            if device == "auto":
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            compute_type = self.config.compute_type
            if compute_type == "auto":
                compute_type = "float16" if device == "cuda" else "int8"
            
            self._model = WhisperModel(
                model_name,
                device=device,
                compute_type=compute_type
            )
            
        elif self._backend == "openai-whisper":
            import whisper
            self._model = whisper.load_model(model_name)
    
    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        **kwargs
    ) -> Transcription:
        """
        Transcribe audio/video file.
        
        Args:
            audio_path: Path to audio or video file
            language: Language code (None for auto-detect)
            **kwargs: Additional options passed to model
        
        Returns:
            Transcription result
        """
        if not self.is_available():
            raise ImportError(
                "No transcription backend available. Install with:\n"
                "  pip install openai-whisper\n"
                "or:\n"
                "  pip install faster-whisper"
            )
        
        import time
        start_time = time.time()
        
        self._load_model()
        
        lang = language or self.config.language
        
        if self._backend == "faster-whisper":
            result = self._transcribe_faster_whisper(audio_path, lang, **kwargs)
        else:
            result = self._transcribe_openai_whisper(audio_path, lang, **kwargs)
        
        result.processing_time = time.time() - start_time
        result.source_file = audio_path
        result.model_name = self.config.model
        
        return result
    
    def _transcribe_faster_whisper(
        self,
        audio_path: str,
        language: Optional[str],
        **kwargs
    ) -> Transcription:
        """Transcribe using faster-whisper."""
        segments_gen, info = self._model.transcribe(
            audio_path,
            language=language,
            task=self.config.task,
            beam_size=self.config.beam_size,
            word_timestamps=self.config.word_timestamps,
            vad_filter=self.config.vad_filter,
            **kwargs
        )
        
        segments = []
        full_text = []
        
        for seg in segments_gen:
            words = []
            
            if self.config.word_timestamps and seg.words:
                for w in seg.words:
                    words.append(Word(
                        text=w.word.strip(),
                        start=w.start,
                        end=w.end,
                        confidence=w.probability if hasattr(w, 'probability') else 1.0
                    ))
            
            segment = Segment(
                text=seg.text.strip(),
                start=seg.start,
                end=seg.end,
                words=words,
                confidence=seg.avg_logprob if hasattr(seg, 'avg_logprob') else 1.0,
                language=info.language
            )
            
            segments.append(segment)
            full_text.append(seg.text.strip())
        
        return Transcription(
            text=" ".join(full_text),
            segments=segments,
            language=info.language,
            duration=info.duration,
            word_count=sum(len(s.text.split()) for s in segments)
        )
    
    def _transcribe_openai_whisper(
        self,
        audio_path: str,
        language: Optional[str],
        **kwargs
    ) -> Transcription:
        """Transcribe using openai-whisper."""
        result = self._model.transcribe(
            audio_path,
            language=language,
            task=self.config.task,
            word_timestamps=self.config.word_timestamps,
            **kwargs
        )
        
        segments = []
        
        for seg in result.get("segments", []):
            words = []
            
            if self.config.word_timestamps and "words" in seg:
                for w in seg["words"]:
                    words.append(Word(
                        text=w.get("word", "").strip(),
                        start=w.get("start", 0),
                        end=w.get("end", 0),
                        confidence=w.get("probability", 1.0)
                    ))
            
            segment = Segment(
                text=seg.get("text", "").strip(),
                start=seg.get("start", 0),
                end=seg.get("end", 0),
                words=words,
                confidence=seg.get("avg_logprob", 0),
                language=result.get("language")
            )
            
            segments.append(segment)
        
        return Transcription(
            text=result.get("text", "").strip(),
            segments=segments,
            language=result.get("language", "en"),
            duration=segments[-1].end if segments else 0,
            word_count=len(result.get("text", "").split())
        )


# ============ Subtitle Generation ============

class SubtitleGenerator:
    """
    Generate subtitle files from transcription.
    
    Supports SRT and VTT formats with various styling options.
    """
    
    @staticmethod
    def to_srt(
        transcription: Transcription,
        max_chars_per_line: int = 42,
        max_lines: int = 2,
        use_words: bool = False
    ) -> str:
        """
        Generate SRT subtitle content.
        
        Args:
            transcription: Transcription to convert
            max_chars_per_line: Maximum characters per line
            max_lines: Maximum lines per subtitle
            use_words: Use word-level timing for karaoke style
        
        Returns:
            SRT content as string
        """
        lines = []
        index = 1
        
        if use_words:
            # Word-level subtitles (karaoke style)
            words = transcription.get_words()
            word_groups = SubtitleGenerator._group_words(
                words, max_chars_per_line, max_lines
            )
            
            for group in word_groups:
                if not group:
                    continue
                
                start = group[0].start
                end = group[-1].end
                text = " ".join(w.text for w in group)
                
                lines.append(str(index))
                lines.append(f"{SubtitleGenerator._format_time_srt(start)} --> {SubtitleGenerator._format_time_srt(end)}")
                lines.append(text)
                lines.append("")
                index += 1
        else:
            # Segment-level subtitles
            for segment in transcription.segments:
                text = SubtitleGenerator._wrap_text(
                    segment.text, max_chars_per_line, max_lines
                )
                
                lines.append(str(index))
                lines.append(f"{SubtitleGenerator._format_time_srt(segment.start)} --> {SubtitleGenerator._format_time_srt(segment.end)}")
                lines.append(text)
                lines.append("")
                index += 1
        
        return "\n".join(lines)
    
    @staticmethod
    def to_vtt(
        transcription: Transcription,
        max_chars_per_line: int = 42,
        max_lines: int = 2,
        include_styles: bool = False
    ) -> str:
        """
        Generate WebVTT subtitle content.
        
        Args:
            transcription: Transcription to convert
            max_chars_per_line: Maximum characters per line
            max_lines: Maximum lines per subtitle
            include_styles: Include VTT styling header
        
        Returns:
            VTT content as string
        """
        lines = ["WEBVTT", ""]
        
        if include_styles:
            lines.extend([
                "STYLE",
                "::cue {",
                "  background-color: rgba(0, 0, 0, 0.8);",
                "  color: white;",
                "  font-family: Arial, sans-serif;",
                "}",
                ""
            ])
        
        for i, segment in enumerate(transcription.segments, 1):
            text = SubtitleGenerator._wrap_text(
                segment.text, max_chars_per_line, max_lines
            )
            
            start = SubtitleGenerator._format_time_vtt(segment.start)
            end = SubtitleGenerator._format_time_vtt(segment.end)
            
            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def save_srt(transcription: Transcription, path: str, **kwargs) -> str:
        """Save transcription as SRT file."""
        content = SubtitleGenerator.to_srt(transcription, **kwargs)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    @staticmethod
    def save_vtt(transcription: Transcription, path: str, **kwargs) -> str:
        """Save transcription as VTT file."""
        content = SubtitleGenerator.to_vtt(transcription, **kwargs)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return path
    
    @staticmethod
    def _format_time_srt(seconds: float) -> str:
        """Format time for SRT (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    @staticmethod
    def _format_time_vtt(seconds: float) -> str:
        """Format time for VTT (HH:MM:SS.mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
    
    @staticmethod
    def _wrap_text(text: str, max_chars: int, max_lines: int) -> str:
        """Wrap text to fit within constraints."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
                
                if len(lines) >= max_lines:
                    break
        
        if current_line and len(lines) < max_lines:
            lines.append(" ".join(current_line))
        
        return "\n".join(lines[:max_lines])
    
    @staticmethod
    def _group_words(
        words: List[Word],
        max_chars: int,
        max_lines: int
    ) -> List[List[Word]]:
        """Group words into subtitle groups."""
        groups = []
        current_group = []
        current_length = 0
        
        for word in words:
            word_len = len(word.text) + 1
            
            if current_length + word_len <= max_chars * max_lines:
                current_group.append(word)
                current_length += word_len
            else:
                if current_group:
                    groups.append(current_group)
                current_group = [word]
                current_length = word_len
        
        if current_group:
            groups.append(current_group)
        
        return groups


# ============ Speaker Diarization ============

class SpeakerDiarizer:
    """
    Speaker diarization - identify different speakers.
    
    TODO: Implement with pyannote.audio
    """
    
    def __init__(self):
        self._pipeline = None
        self._available = self._check_available()
    
    def _check_available(self) -> bool:
        """Check if diarization is available."""
        try:
            from pyannote.audio import Pipeline
            return True
        except ImportError:
            return False
    
    def is_available(self) -> bool:
        return self._available
    
    def diarize(
        self,
        audio_path: str,
        num_speakers: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Identify speakers in audio.
        
        TODO: Implement actual diarization
        
        Args:
            audio_path: Path to audio file
            num_speakers: Expected number of speakers (optional)
        
        Returns:
            List of speaker segments with timing
        """
        if not self._available:
            logger.warning("Speaker diarization not available. Install: pip install pyannote.audio")
            return []
        
        # TODO: Implement with pyannote.audio
        # Requires HuggingFace token and model download
        
        return []
    
    def assign_speakers_to_transcription(
        self,
        transcription: Transcription,
        diarization: List[Dict[str, Any]]
    ) -> Transcription:
        """
        Assign speaker labels to transcription segments.
        
        TODO: Implement speaker assignment
        """
        # TODO: Match diarization to transcription segments
        return transcription


# ============ Convenience Functions ============

def transcribe(
    audio_path: str,
    model: str = "base",
    language: Optional[str] = None,
    word_timestamps: bool = True
) -> Transcription:
    """
    Transcribe audio/video file.
    
    Args:
        audio_path: Path to audio or video file
        model: Whisper model name
        language: Language code (None for auto)
        word_timestamps: Include word-level timestamps
    
    Returns:
        Transcription result
    """
    config = TranscriptionConfig(
        model=model,
        language=language,
        word_timestamps=word_timestamps
    )
    
    transcriber = Transcriber(config)
    return transcriber.transcribe(audio_path)


def transcribe_to_srt(
    audio_path: str,
    output_path: str,
    model: str = "base",
    **kwargs
) -> str:
    """Transcribe and save as SRT."""
    result = transcribe(audio_path, model=model, **kwargs)
    return SubtitleGenerator.save_srt(result, output_path)


def transcribe_to_vtt(
    audio_path: str,
    output_path: str,
    model: str = "base",
    **kwargs
) -> str:
    """Transcribe and save as VTT."""
    result = transcribe(audio_path, model=model, **kwargs)
    return SubtitleGenerator.save_vtt(result, output_path)


def is_transcription_available() -> bool:
    """Check if transcription is available."""
    return Transcriber().is_available()
