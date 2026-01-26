"""
Intelligent Shot Splitting
==========================
Advanced shot splitting based on visual cues, action changes, and audio timing.

Features:
- Audio-driven duration calculation
- Visual action change detection
- Intelligent retry with fallback strategies
- Sub-segment generation for long shots
- Beat-aligned cuts
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum

from .shot_plan import Shot, ShotPlan, CameraSpec, AudioSpec, ShotType, CameraMotion
from .audio_system import estimate_narration_duration, estimate_dialogue_duration


class SplitStrategy(Enum):
    """Strategies for splitting long shots."""
    AUDIO_BEATS = "audio_beats"  # Split on audio beats/pauses
    VISUAL_ACTIONS = "visual_actions"  # Split on action changes
    FIXED_DURATION = "fixed_duration"  # Fixed segment length
    SENTENCE_BREAKS = "sentence_breaks"  # Split on sentence boundaries
    ADAPTIVE = "adaptive"  # Combine strategies


class RetryStrategy(Enum):
    """Strategies for handling generation failures."""
    DIRECT_RETRY = "direct_retry"  # Retry same prompt
    SIMPLIFIED_PROMPT = "simplified_prompt"  # Simplify and retry
    SPLIT_SEGMENT = "split_segment"  # Split into smaller parts
    FALLBACK_PROVIDER = "fallback_provider"  # Try different provider
    SKIP_SEGMENT = "skip_segment"  # Skip problematic segment


@dataclass
class SplitConfig:
    """Configuration for shot splitting."""
    # Duration limits (provider-specific)
    max_segment_duration: float = 8.0  # Maximum single generation
    min_segment_duration: float = 2.0  # Minimum viable segment
    ideal_segment_duration: float = 5.0  # Target duration
    
    # Strategy
    primary_strategy: SplitStrategy = SplitStrategy.ADAPTIVE
    
    # Audio settings
    words_per_minute: float = 150.0
    pause_between_sentences: float = 0.3
    
    # Overlap for continuity
    overlap_frames: int = 2  # Frames to overlap between segments
    
    # Retry settings
    max_retries: int = 3
    retry_strategies: List[RetryStrategy] = field(
        default_factory=lambda: [
            RetryStrategy.DIRECT_RETRY,
            RetryStrategy.SIMPLIFIED_PROMPT,
            RetryStrategy.SPLIT_SEGMENT
        ]
    )


@dataclass
class SplitPoint:
    """A point where a shot should be split."""
    time: float
    reason: str  # Why we split here
    priority: int = 1  # Higher = more important
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Segment:
    """A segment of a shot ready for generation."""
    segment_id: str
    parent_shot_id: str
    index: int  # Order in parent shot
    
    # Timing
    start_time: float
    end_time: float
    duration: float
    
    # Content
    action: str
    narration: Optional[str] = None
    
    # Continuity
    requires_starting_frame: bool = False
    starting_frame_source: Optional[str] = None  # Path or segment ID
    
    # Generation metadata
    prompt: Optional[str] = None
    provider: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "segment_id": self.segment_id,
            "parent_shot_id": self.parent_shot_id,
            "index": self.index,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "action": self.action,
            "narration": self.narration,
            "requires_starting_frame": self.requires_starting_frame,
            "starting_frame_source": self.starting_frame_source
        }


class ShotSplitter:
    """
    Intelligently splits shots into segments based on various strategies.
    
    Features:
    - Audio-sync aware splitting
    - Visual action detection
    - Sentence boundary detection
    - Provider-specific duration limits
    """
    
    def __init__(self, config: Optional[SplitConfig] = None):
        self.config = config or SplitConfig()
    
    def split_shot(
        self,
        shot: Shot,
        provider_max_duration: Optional[float] = None
    ) -> List[Segment]:
        """
        Split a shot into generation-ready segments.
        
        Args:
            shot: The shot to split
            provider_max_duration: Override max duration for specific provider
        
        Returns:
            List of Segments ready for generation
        """
        max_duration = provider_max_duration or self.config.max_segment_duration
        
        # Calculate total duration needed
        total_duration = self._calculate_shot_duration(shot)
        
        # If short enough, return as single segment
        if total_duration <= max_duration:
            return [self._create_segment(shot, 0, 0, total_duration)]
        
        # Find split points based on strategy
        split_points = self._find_split_points(shot, total_duration, max_duration)
        
        # Create segments from split points
        segments = self._create_segments_from_splits(shot, split_points, total_duration)
        
        return segments
    
    def split_plan(
        self,
        plan: ShotPlan,
        provider_max_duration: Optional[float] = None
    ) -> List[Segment]:
        """Split all shots in a plan."""
        all_segments = []
        
        for shot in plan.get_all_shots():
            segments = self.split_shot(shot, provider_max_duration)
            all_segments.extend(segments)
        
        return all_segments
    
    def _calculate_shot_duration(self, shot: Shot) -> float:
        """Calculate the required duration for a shot."""
        # If duration is explicitly set, use it
        if shot.duration:
            return shot.duration
        
        # Calculate from audio
        audio_duration = self._estimate_audio_duration(shot.audio)
        
        # Apply min/max bounds
        duration = max(shot.min_duration, min(shot.max_duration, audio_duration))
        
        return duration
    
    def _estimate_audio_duration(self, audio: AudioSpec) -> float:
        """Estimate duration needed for audio content."""
        total = 0.0
        
        # Narration
        if audio.narration:
            total += estimate_narration_duration(
                audio.narration,
                self.config.words_per_minute
            )
        
        # Dialogue
        if audio.dialogue:
            # Extract just the dialogue text (remove "Character: " prefix)
            dialogue_text = audio.dialogue
            if ":" in dialogue_text:
                dialogue_text = dialogue_text.split(":", 1)[1].strip()
            
            total += estimate_dialogue_duration(
                dialogue_text,
                audio.dialogue_emotion,
                self.config.words_per_minute * 1.1  # Dialogue slightly faster
            )
        
        # Add buffer
        total += audio.audio_delay
        total *= 1.1  # 10% buffer
        
        return max(total, 3.0)  # Minimum 3 seconds
    
    def _find_split_points(
        self,
        shot: Shot,
        total_duration: float,
        max_duration: float
    ) -> List[SplitPoint]:
        """Find optimal split points based on strategy."""
        strategy = self.config.primary_strategy
        
        if strategy == SplitStrategy.AUDIO_BEATS:
            return self._find_audio_beats(shot, total_duration, max_duration)
        elif strategy == SplitStrategy.VISUAL_ACTIONS:
            return self._find_visual_action_splits(shot, total_duration, max_duration)
        elif strategy == SplitStrategy.SENTENCE_BREAKS:
            return self._find_sentence_breaks(shot, total_duration, max_duration)
        elif strategy == SplitStrategy.FIXED_DURATION:
            return self._find_fixed_splits(total_duration, max_duration)
        elif strategy == SplitStrategy.ADAPTIVE:
            return self._find_adaptive_splits(shot, total_duration, max_duration)
        
        return self._find_fixed_splits(total_duration, max_duration)
    
    def _find_audio_beats(
        self,
        shot: Shot,
        total_duration: float,
        max_duration: float
    ) -> List[SplitPoint]:
        """Find split points based on audio pauses and beats."""
        points = []
        
        text = shot.audio.narration or shot.audio.dialogue or ""
        if not text:
            return self._find_fixed_splits(total_duration, max_duration)
        
        # Find natural pauses in text
        sentences = self._split_into_sentences(text)
        
        current_time = 0.0
        current_segment_start = 0.0
        
        for i, sentence in enumerate(sentences):
            sentence_duration = estimate_narration_duration(
                sentence, self.config.words_per_minute
            )
            
            # Check if adding this sentence would exceed max
            segment_duration = (current_time + sentence_duration) - current_segment_start
            
            if segment_duration > max_duration and current_time > current_segment_start:
                # Add split point at current position
                points.append(SplitPoint(
                    time=current_time,
                    reason="audio_beat",
                    priority=2,
                    metadata={"sentence_index": i}
                ))
                current_segment_start = current_time
            
            current_time += sentence_duration + self.config.pause_between_sentences
        
        return points
    
    def _find_visual_action_splits(
        self,
        shot: Shot,
        total_duration: float,
        max_duration: float
    ) -> List[SplitPoint]:
        """Find split points based on visual action changes."""
        points = []
        
        # Parse action description for visual cues
        action = shot.action
        
        # Look for action change indicators
        action_markers = [
            (r'\bthen\b', 0.5),
            (r'\bafter\b', 0.5),
            (r'\bnext\b', 0.5),
            (r'\bsuddenly\b', 0.3),
            (r'\bmoving\b', 0.4),
            (r'\bturning\b', 0.4),
            (r'\bwalking\b', 0.6),
            (r'\brunning\b', 0.4),
        ]
        
        # Simple heuristic: estimate action time based on text position
        action_words = action.split()
        total_words = len(action_words)
        
        for pattern, weight in action_markers:
            for match in re.finditer(pattern, action.lower()):
                # Estimate time based on position in text
                word_index = len(action[:match.start()].split())
                estimated_time = (word_index / max(1, total_words)) * total_duration
                
                if estimated_time > self.config.min_segment_duration:
                    points.append(SplitPoint(
                        time=estimated_time,
                        reason=f"visual_action: {pattern}",
                        priority=1,
                        metadata={"pattern": pattern}
                    ))
        
        # Ensure we have enough split points
        if not points or (total_duration / max_duration) > len(points) + 1:
            # Add fixed splits where needed
            fixed_points = self._find_fixed_splits(total_duration, max_duration)
            points = self._merge_split_points(points, fixed_points, max_duration)
        
        return points
    
    def _find_sentence_breaks(
        self,
        shot: Shot,
        total_duration: float,
        max_duration: float
    ) -> List[SplitPoint]:
        """Find split points at sentence boundaries."""
        text = shot.audio.narration or shot.audio.dialogue or shot.action
        sentences = self._split_into_sentences(text)
        
        if len(sentences) <= 1:
            return self._find_fixed_splits(total_duration, max_duration)
        
        points = []
        time_per_sentence = total_duration / len(sentences)
        current_time = 0.0
        segment_start = 0.0
        
        for i, sentence in enumerate(sentences[:-1]):  # Skip last
            current_time += time_per_sentence
            segment_duration = current_time - segment_start
            
            if segment_duration >= self.config.min_segment_duration:
                if segment_duration >= max_duration or i == len(sentences) - 2:
                    points.append(SplitPoint(
                        time=current_time,
                        reason="sentence_break",
                        priority=2,
                        metadata={"sentence_index": i}
                    ))
                    segment_start = current_time
        
        return points
    
    def _find_fixed_splits(
        self,
        total_duration: float,
        max_duration: float
    ) -> List[SplitPoint]:
        """Find fixed-interval split points."""
        points = []
        
        num_segments = math.ceil(total_duration / max_duration)
        segment_duration = total_duration / num_segments
        
        for i in range(1, num_segments):
            points.append(SplitPoint(
                time=i * segment_duration,
                reason="fixed_split",
                priority=0
            ))
        
        return points
    
    def _find_adaptive_splits(
        self,
        shot: Shot,
        total_duration: float,
        max_duration: float
    ) -> List[SplitPoint]:
        """Combine multiple strategies for optimal splits."""
        all_points = []
        
        # Gather points from all strategies
        audio_points = self._find_audio_beats(shot, total_duration, max_duration)
        visual_points = self._find_visual_action_splits(shot, total_duration, max_duration)
        sentence_points = self._find_sentence_breaks(shot, total_duration, max_duration)
        
        # Combine with priority weighting
        for p in audio_points:
            p.priority = 3
        for p in sentence_points:
            p.priority = 2
        for p in visual_points:
            p.priority = 1
        
        all_points = audio_points + visual_points + sentence_points
        
        # Merge close points
        merged = self._merge_close_points(all_points, min_gap=1.0)
        
        # Ensure we have enough split points
        min_splits = math.ceil(total_duration / max_duration) - 1
        
        if len(merged) < min_splits:
            fixed = self._find_fixed_splits(total_duration, max_duration)
            merged = self._merge_split_points(merged, fixed, max_duration)
        
        return merged
    
    def _merge_close_points(
        self,
        points: List[SplitPoint],
        min_gap: float
    ) -> List[SplitPoint]:
        """Merge split points that are too close together."""
        if not points:
            return []
        
        # Sort by time
        sorted_points = sorted(points, key=lambda p: p.time)
        merged = [sorted_points[0]]
        
        for point in sorted_points[1:]:
            if point.time - merged[-1].time < min_gap:
                # Keep the higher priority one
                if point.priority > merged[-1].priority:
                    merged[-1] = point
            else:
                merged.append(point)
        
        return merged
    
    def _merge_split_points(
        self,
        primary: List[SplitPoint],
        secondary: List[SplitPoint],
        max_duration: float
    ) -> List[SplitPoint]:
        """Merge primary and secondary split points."""
        all_points = primary + secondary
        merged = self._merge_close_points(all_points, min_gap=1.0)
        
        # Verify segments don't exceed max duration
        merged.sort(key=lambda p: p.time)
        
        return merged
    
    def _create_segments_from_splits(
        self,
        shot: Shot,
        split_points: List[SplitPoint],
        total_duration: float
    ) -> List[Segment]:
        """Create segments from split points."""
        segments = []
        split_points.sort(key=lambda p: p.time)
        
        # Add start and end points
        times = [0.0] + [p.time for p in split_points] + [total_duration]
        
        # Get narration/action parts for each segment
        text_parts = self._split_text_for_segments(shot, times)
        
        for i in range(len(times) - 1):
            start_time = times[i]
            end_time = times[i + 1]
            duration = end_time - start_time
            
            segment = Segment(
                segment_id=f"{shot.shot_id}_seg{i:02d}",
                parent_shot_id=shot.shot_id,
                index=i,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                action=text_parts[i]["action"],
                narration=text_parts[i].get("narration"),
                requires_starting_frame=i > 0,
                starting_frame_source=f"{shot.shot_id}_seg{i-1:02d}" if i > 0 else None
            )
            segments.append(segment)
        
        return segments
    
    def _create_segment(
        self,
        shot: Shot,
        index: int,
        start_time: float,
        duration: float
    ) -> Segment:
        """Create a single segment from a shot."""
        return Segment(
            segment_id=f"{shot.shot_id}_seg{index:02d}",
            parent_shot_id=shot.shot_id,
            index=index,
            start_time=start_time,
            end_time=start_time + duration,
            duration=duration,
            action=shot.action,
            narration=shot.audio.narration,
            requires_starting_frame=False
        )
    
    def _split_text_for_segments(
        self,
        shot: Shot,
        times: List[float]
    ) -> List[Dict[str, str]]:
        """Split narration/action text to match segments."""
        parts = []
        
        narration = shot.audio.narration or ""
        action = shot.action or ""
        
        narration_sentences = self._split_into_sentences(narration)
        action_sentences = self._split_into_sentences(action)
        
        num_segments = len(times) - 1
        
        # Distribute sentences across segments
        narration_per_segment = self._distribute_items(narration_sentences, num_segments)
        action_per_segment = self._distribute_items(action_sentences, num_segments)
        
        for i in range(num_segments):
            parts.append({
                "narration": " ".join(narration_per_segment[i]) if narration_per_segment[i] else None,
                "action": " ".join(action_per_segment[i]) if action_per_segment[i] else action
            })
        
        return parts
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        if not text:
            return []
        
        # Simple sentence splitting
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def _distribute_items(
        self,
        items: List[str],
        num_buckets: int
    ) -> List[List[str]]:
        """Distribute items evenly across buckets."""
        if not items:
            return [[] for _ in range(num_buckets)]
        
        buckets = [[] for _ in range(num_buckets)]
        items_per_bucket = max(1, len(items) // num_buckets)
        
        item_idx = 0
        for bucket_idx in range(num_buckets):
            if bucket_idx == num_buckets - 1:
                # Last bucket gets remaining items
                buckets[bucket_idx] = items[item_idx:]
            else:
                end_idx = min(item_idx + items_per_bucket, len(items))
                buckets[bucket_idx] = items[item_idx:end_idx]
                item_idx = end_idx
        
        return buckets


# ============ Retry Handler ============

@dataclass
class RetryResult:
    """Result of a retry attempt."""
    success: bool
    segment: Optional[Segment]
    strategy_used: RetryStrategy
    error: Optional[str] = None
    output_path: Optional[str] = None


class RetryHandler:
    """
    Handles intelligent retry logic for failed generations.
    """
    
    def __init__(self, config: Optional[SplitConfig] = None):
        self.config = config or SplitConfig()
        self.splitter = ShotSplitter(config)
    
    async def handle_failure(
        self,
        segment: Segment,
        error: str,
        attempt: int,
        generate_fn: Callable
    ) -> RetryResult:
        """
        Handle a generation failure with intelligent retry.
        
        Args:
            segment: The failed segment
            error: Error message
            attempt: Current attempt number
            generate_fn: Function to call for generation
        
        Returns:
            RetryResult with outcome
        """
        if attempt >= self.config.max_retries:
            return RetryResult(
                success=False,
                segment=segment,
                strategy_used=RetryStrategy.SKIP_SEGMENT,
                error=f"Max retries ({self.config.max_retries}) exceeded"
            )
        
        # Select strategy based on attempt
        strategy_index = min(attempt, len(self.config.retry_strategies) - 1)
        strategy = self.config.retry_strategies[strategy_index]
        
        if strategy == RetryStrategy.DIRECT_RETRY:
            return await self._direct_retry(segment, generate_fn)
        
        elif strategy == RetryStrategy.SIMPLIFIED_PROMPT:
            return await self._simplified_retry(segment, generate_fn)
        
        elif strategy == RetryStrategy.SPLIT_SEGMENT:
            return await self._split_and_retry(segment, generate_fn)
        
        elif strategy == RetryStrategy.FALLBACK_PROVIDER:
            return await self._fallback_retry(segment, generate_fn)
        
        return RetryResult(
            success=False,
            segment=segment,
            strategy_used=strategy,
            error="Unknown retry strategy"
        )
    
    async def _direct_retry(
        self,
        segment: Segment,
        generate_fn: Callable
    ) -> RetryResult:
        """Simple direct retry."""
        try:
            result = await generate_fn(segment)
            return RetryResult(
                success=True,
                segment=segment,
                strategy_used=RetryStrategy.DIRECT_RETRY,
                output_path=result
            )
        except Exception as e:
            return RetryResult(
                success=False,
                segment=segment,
                strategy_used=RetryStrategy.DIRECT_RETRY,
                error=str(e)
            )
    
    async def _simplified_retry(
        self,
        segment: Segment,
        generate_fn: Callable
    ) -> RetryResult:
        """Retry with simplified prompt."""
        # Create simplified segment
        simplified = Segment(
            segment_id=segment.segment_id + "_simple",
            parent_shot_id=segment.parent_shot_id,
            index=segment.index,
            start_time=segment.start_time,
            end_time=segment.end_time,
            duration=segment.duration,
            action=self._simplify_action(segment.action),
            narration=None,  # Remove narration for simplicity
            requires_starting_frame=segment.requires_starting_frame,
            starting_frame_source=segment.starting_frame_source
        )
        
        try:
            result = await generate_fn(simplified)
            return RetryResult(
                success=True,
                segment=simplified,
                strategy_used=RetryStrategy.SIMPLIFIED_PROMPT,
                output_path=result
            )
        except Exception as e:
            return RetryResult(
                success=False,
                segment=simplified,
                strategy_used=RetryStrategy.SIMPLIFIED_PROMPT,
                error=str(e)
            )
    
    async def _split_and_retry(
        self,
        segment: Segment,
        generate_fn: Callable
    ) -> RetryResult:
        """Split segment and retry smaller parts."""
        # Create a shot from the segment for splitting
        shot = Shot(
            shot_id=segment.segment_id,
            action=segment.action,
            duration=segment.duration,
            audio=AudioSpec(narration=segment.narration)
        )
        
        # Split with smaller max duration
        sub_splitter = ShotSplitter(SplitConfig(
            max_segment_duration=segment.duration / 2,
            min_segment_duration=1.5
        ))
        
        sub_segments = sub_splitter.split_shot(shot)
        
        # Try generating each sub-segment
        success_count = 0
        output_paths = []
        
        for sub_seg in sub_segments:
            try:
                result = await generate_fn(sub_seg)
                output_paths.append(result)
                success_count += 1
            except Exception:
                pass
        
        if success_count == len(sub_segments):
            return RetryResult(
                success=True,
                segment=segment,
                strategy_used=RetryStrategy.SPLIT_SEGMENT,
                output_path=",".join(output_paths)  # Multiple paths
            )
        
        return RetryResult(
            success=False,
            segment=segment,
            strategy_used=RetryStrategy.SPLIT_SEGMENT,
            error=f"Only {success_count}/{len(sub_segments)} sub-segments succeeded"
        )
    
    async def _fallback_retry(
        self,
        segment: Segment,
        generate_fn: Callable
    ) -> RetryResult:
        """Retry with fallback provider (handled by caller)."""
        # This signals to the caller to try a different provider
        return RetryResult(
            success=False,
            segment=segment,
            strategy_used=RetryStrategy.FALLBACK_PROVIDER,
            error="Fallback provider requested"
        )
    
    def _simplify_action(self, action: str) -> str:
        """Simplify an action description."""
        # Remove complex phrases
        simplified = action
        
        # Remove parenthetical notes
        simplified = re.sub(r'\([^)]*\)', '', simplified)
        
        # Remove complex adjectives
        complex_words = [
            "simultaneously", "meanwhile", "subsequently",
            "cinematically", "dramatically", "elegantly"
        ]
        for word in complex_words:
            simplified = simplified.replace(word, "")
        
        # Clean up whitespace
        simplified = " ".join(simplified.split())
        
        # Truncate if too long
        max_words = 30
        words = simplified.split()
        if len(words) > max_words:
            simplified = " ".join(words[:max_words])
        
        return simplified


# ============ Convenience Functions ============

def split_shot(
    shot: Shot,
    max_duration: float = 8.0
) -> List[Segment]:
    """Split a shot into segments."""
    splitter = ShotSplitter(SplitConfig(max_segment_duration=max_duration))
    return splitter.split_shot(shot)


def split_plan(
    plan: ShotPlan,
    max_duration: float = 8.0
) -> List[Segment]:
    """Split all shots in a plan."""
    splitter = ShotSplitter(SplitConfig(max_segment_duration=max_duration))
    return splitter.split_plan(plan)


def calculate_shot_duration(
    narration: Optional[str] = None,
    dialogue: Optional[str] = None,
    min_duration: float = 3.0,
    max_duration: float = 30.0
) -> float:
    """Calculate duration for a shot based on audio."""
    duration = min_duration
    
    if narration:
        duration = max(duration, estimate_narration_duration(narration))
    
    if dialogue:
        duration = max(duration, estimate_dialogue_duration(dialogue))
    
    return min(duration, max_duration)
