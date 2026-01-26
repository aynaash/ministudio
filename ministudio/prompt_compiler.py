"""
Structured Prompt Compiler
==========================
Advanced prompt compilation system that generates provider-specific prompts
from structured shot plans and cinematography data.

Features:
- Provider-agnostic structured prompts
- Cinematography-aware prompt enhancement
- Character consistency injection
- Scene graph integration
- Multi-part prompt generation (main, negative, control)
"""

import json
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from .shot_plan import (
    Shot, ShotPlan, CameraSpec, LightingSpec, CharacterSpec,
    AudioSpec, ShotType, CameraMotion, Transition
)
from .cinematography import (
    CinematographyProfile, CompositionRule, LightingStyle,
    CINEMATOGRAPHY_PROFILES
)
from .scene_graph import SceneGraph, Entity, CharacterState, CameraState


class PromptFormat(Enum):
    """Output format for prompts."""
    TEXT = "text"  # Single text string
    STRUCTURED = "structured"  # Dict with parts
    JSON = "json"  # JSON string


class PromptStyle(Enum):
    """Prompt style/verbosity."""
    MINIMAL = "minimal"  # Essential only
    STANDARD = "standard"  # Balanced
    DETAILED = "detailed"  # Full description
    TECHNICAL = "technical"  # Technical terms
    ARTISTIC = "artistic"  # Evocative language


@dataclass
class PromptPart:
    """A component of a structured prompt."""
    name: str
    content: str
    priority: int = 1  # Higher = more important
    provider_tags: List[str] = field(default_factory=list)  # Which providers use this
    

@dataclass
class CompiledPrompt:
    """Complete compiled prompt with all parts."""
    # Main prompts
    main_prompt: str
    negative_prompt: Optional[str] = None
    
    # Structured parts (for providers that need them)
    parts: List[PromptPart] = field(default_factory=list)
    
    # Control signals
    control_signals: Dict[str, Any] = field(default_factory=dict)
    
    # Provider-specific overrides
    provider_prompts: Dict[str, str] = field(default_factory=dict)
    
    # Metadata
    shot_id: Optional[str] = None
    duration: Optional[float] = None
    seed: Optional[int] = None
    
    def get_for_provider(self, provider: str) -> str:
        """Get prompt optimized for specific provider."""
        if provider in self.provider_prompts:
            return self.provider_prompts[provider]
        return self.main_prompt
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "main_prompt": self.main_prompt,
            "negative_prompt": self.negative_prompt,
            "parts": [{"name": p.name, "content": p.content, "priority": p.priority} for p in self.parts],
            "control_signals": self.control_signals,
            "provider_prompts": self.provider_prompts,
            "shot_id": self.shot_id,
            "duration": self.duration,
            "seed": self.seed
        }


class StructuredPromptCompiler:
    """
    Compiles shots into provider-ready prompts with full cinematography.
    
    Pipeline:
    1. Extract shot metadata (action, characters, environment)
    2. Apply cinematography enhancements
    3. Inject continuity context
    4. Generate provider-specific variations
    5. Build negative prompts
    6. Output structured or text format
    """
    
    def __init__(
        self,
        style: PromptStyle = PromptStyle.STANDARD,
        default_negative: Optional[str] = None
    ):
        self.style = style
        self.default_negative = default_negative or self._get_default_negative()
        
        # Provider-specific prompt templates
        self.provider_templates = {
            "vertex_ai": self._template_vertex_ai,
            "openai_sora": self._template_sora,
            "runway": self._template_runway,
            "pika": self._template_pika,
            "stable_video": self._template_stable_video,
            "kling": self._template_kling,
        }
    
    def compile(
        self,
        shot: Shot,
        scene_graph: Optional[SceneGraph] = None,
        plan: Optional[ShotPlan] = None,
        format: PromptFormat = PromptFormat.TEXT
    ) -> CompiledPrompt:
        """
        Compile a shot into a prompt.
        
        Args:
            shot: The shot to compile
            scene_graph: Optional scene graph for continuity
            plan: Optional shot plan for global context
            format: Output format
        
        Returns:
            CompiledPrompt with main prompt and parts
        """
        parts = []
        
        # 1. Action/Scene Description (highest priority)
        action_part = self._compile_action(shot)
        parts.append(action_part)
        
        # 2. Characters
        if shot.characters:
            char_parts = self._compile_characters(shot, plan)
            parts.extend(char_parts)
        
        # 3. Environment
        if shot.environment:
            env_part = self._compile_environment(shot)
            parts.append(env_part)
        
        # 4. Cinematography
        cinema_part = self._compile_cinematography(shot)
        parts.append(cinema_part)
        
        # 5. Lighting
        light_part = self._compile_lighting(shot)
        parts.append(light_part)
        
        # 6. Continuity context
        if scene_graph:
            continuity_part = self._compile_continuity(scene_graph)
            if continuity_part:
                parts.append(continuity_part)
        
        # 7. Style
        if plan and plan.global_style:
            style_part = self._compile_style(plan)
            parts.append(style_part)
        
        # Sort by priority
        parts.sort(key=lambda p: p.priority, reverse=True)
        
        # Build main prompt
        main_prompt = self._assemble_prompt(parts)
        
        # Build negative prompt
        negative_prompt = self._build_negative_prompt(shot, plan)
        
        # Generate provider-specific prompts
        provider_prompts = self._generate_provider_prompts(shot, parts, plan)
        
        # Control signals
        control_signals = self._extract_control_signals(shot)
        
        return CompiledPrompt(
            main_prompt=main_prompt,
            negative_prompt=negative_prompt,
            parts=parts,
            control_signals=control_signals,
            provider_prompts=provider_prompts,
            shot_id=shot.shot_id,
            duration=shot.duration,
            seed=shot.seed
        )
    
    def compile_batch(
        self,
        plan: ShotPlan,
        scene_graph: Optional[SceneGraph] = None
    ) -> List[CompiledPrompt]:
        """Compile all shots in a plan."""
        compiled = []
        for shot in plan.get_all_shots():
            prompt = self.compile(shot, scene_graph, plan)
            compiled.append(prompt)
        return compiled
    
    # ============ Part Compilation ============
    
    def _compile_action(self, shot: Shot) -> PromptPart:
        """Compile the action description."""
        action_text = shot.action
        
        # Add description if present
        if shot.description:
            action_text = f"{action_text}. {shot.description}"
        
        # Style-based enhancement
        if self.style == PromptStyle.DETAILED:
            action_text = f"Cinematic shot: {action_text}"
        elif self.style == PromptStyle.ARTISTIC:
            action_text = f"Visually striking moment: {action_text}"
        
        return PromptPart(
            name="action",
            content=action_text,
            priority=10,
            provider_tags=["all"]
        )
    
    def _compile_characters(
        self,
        shot: Shot,
        plan: Optional[ShotPlan]
    ) -> List[PromptPart]:
        """Compile character descriptions."""
        parts = []
        
        for char_id, char_spec in shot.characters.items():
            # Get character definition from plan
            char_def = None
            if plan and char_id in plan.characters:
                char_def = plan.characters[char_id]
            
            char_text = []
            
            # Name and identity
            if char_def:
                char_text.append(f"{char_def.name}")
                if char_def.description:
                    char_text.append(char_def.description)
                
                # Identity traits
                if char_def.identity:
                    identity_parts = []
                    for k, v in char_def.identity.items():
                        if v:
                            identity_parts.append(f"{k}: {v}")
                    if identity_parts:
                        char_text.append(f"({', '.join(identity_parts)})")
            else:
                char_text.append(char_id)
            
            # Current state
            state_parts = []
            if char_spec.emotion != "neutral":
                state_parts.append(f"{char_spec.emotion} expression")
            if char_spec.action != "standing":
                state_parts.append(char_spec.action)
            if char_spec.posture != "relaxed":
                state_parts.append(f"{char_spec.posture} posture")
            if char_spec.speaking:
                state_parts.append("speaking")
            
            if state_parts:
                char_text.append(f"- {', '.join(state_parts)}")
            
            # Visual anchor
            if char_spec.visual_anchor or (char_def and char_def.visual_anchor):
                char_text.append("(maintain exact appearance from reference)")
            
            parts.append(PromptPart(
                name=f"character_{char_id}",
                content=" ".join(char_text),
                priority=8,
                provider_tags=["all"]
            ))
        
        return parts
    
    def _compile_environment(self, shot: Shot) -> PromptPart:
        """Compile environment description."""
        env = shot.environment
        env_parts = []
        
        env_parts.append(f"Location: {env.location}")
        
        if env.time_of_day != "day":
            env_parts.append(f"Time: {env.time_of_day}")
        
        if env.weather != "clear":
            env_parts.append(f"Weather: {env.weather}")
        
        if env.dynamic_elements:
            env_parts.append(f"Elements: {', '.join(env.dynamic_elements)}")
        
        return PromptPart(
            name="environment",
            content=", ".join(env_parts),
            priority=6,
            provider_tags=["all"]
        )
    
    def _compile_cinematography(self, shot: Shot) -> PromptPart:
        """Compile cinematography description."""
        camera = shot.camera
        cinema_parts = []
        
        # Shot type
        shot_type = camera.shot_type
        if isinstance(shot_type, ShotType):
            shot_type = shot_type.value
        
        shot_type_desc = {
            "extreme_wide": "extreme wide shot",
            "wide": "wide shot",
            "full": "full shot",
            "medium_wide": "medium wide shot",
            "medium": "medium shot",
            "medium_close": "medium close-up",
            "close_up": "close-up",
            "extreme_close_up": "extreme close-up",
            "pov": "POV shot",
            "over_shoulder": "over-the-shoulder shot",
            "two_shot": "two-shot"
        }
        cinema_parts.append(shot_type_desc.get(shot_type, shot_type))
        
        # Lens
        cinema_parts.append(f"shot on {camera.lens} lens")
        
        # DOF
        if camera.depth_of_field == "shallow":
            cinema_parts.append("shallow depth of field with bokeh")
        elif camera.depth_of_field == "deep":
            cinema_parts.append("deep focus")
        
        # Motion
        motion = camera.motion
        if isinstance(motion, CameraMotion):
            motion = motion.value
        
        if motion != "static":
            motion_desc = {
                "dolly_in": "dolly in",
                "dolly_out": "dolly out",
                "pan_left": "pan left",
                "pan_right": "pan right",
                "tilt_up": "tilt up",
                "tilt_down": "tilt down",
                "tracking": "tracking shot",
                "handheld": "handheld camera",
                "steadicam": "steadicam movement",
                "crane_up": "crane shot rising",
                "crane_down": "crane shot descending"
            }
            cinema_parts.append(motion_desc.get(motion, motion))
        
        # Framing
        if camera.framing != "rule_of_thirds":
            framing_desc = {
                "center": "centered framing",
                "golden_ratio": "golden ratio composition",
                "leading_space": "leading space for movement"
            }
            if camera.framing in framing_desc:
                cinema_parts.append(framing_desc[camera.framing])
        
        return PromptPart(
            name="cinematography",
            content=", ".join(cinema_parts),
            priority=7,
            provider_tags=["all"]
        )
    
    def _compile_lighting(self, shot: Shot) -> PromptPart:
        """Compile lighting description."""
        light = shot.lighting
        light_parts = []
        
        # Time of day
        time_desc = {
            "dawn": "soft dawn light",
            "morning": "morning light",
            "day": "daylight",
            "afternoon": "afternoon light",
            "golden_hour": "golden hour lighting",
            "dusk": "dusk light",
            "night": "night scene"
        }
        light_parts.append(time_desc.get(light.time_of_day, light.time_of_day))
        
        # Mood
        if light.mood != "neutral":
            mood_desc = {
                "dramatic": "dramatic lighting",
                "soft": "soft diffused light",
                "harsh": "harsh directional light",
                "mysterious": "mysterious shadows",
                "romantic": "romantic soft glow"
            }
            if light.mood in mood_desc:
                light_parts.append(mood_desc[light.mood])
        
        # Color temperature
        if light.key_color_temp < 4000:
            light_parts.append("warm tungsten tones")
        elif light.key_color_temp > 6000:
            light_parts.append("cool blue tones")
        
        # Atmosphere
        if light.fog:
            light_parts.append(f"atmospheric fog")
        if light.particles and light.particle_type:
            light_parts.append(f"{light.particle_type} in the air")
        
        # Color grade
        if light.color_grade != "neutral":
            grade_desc = {
                "warm": "warm color grading",
                "cool": "cool color grading",
                "teal_orange": "teal and orange color grade",
                "vintage": "vintage film look",
                "cinematic": "cinematic color grading"
            }
            if light.color_grade in grade_desc:
                light_parts.append(grade_desc[light.color_grade])
        
        return PromptPart(
            name="lighting",
            content=", ".join(light_parts),
            priority=5,
            provider_tags=["all"]
        )
    
    def _compile_continuity(self, scene_graph: SceneGraph) -> Optional[PromptPart]:
        """Compile continuity context from scene graph."""
        context = scene_graph.get_continuity_context()
        
        if not context.get("characters") and not context.get("camera"):
            return None
        
        continuity_parts = []
        
        # Character continuity
        for char_id, char_data in context.get("characters", {}).items():
            if char_data.get("visual_anchor"):
                continuity_parts.append(
                    f"maintain {char_id}'s exact appearance"
                )
            if char_data.get("emotion"):
                continuity_parts.append(
                    f"{char_id} emotion: {char_data['emotion']}"
                )
        
        # Camera continuity
        cam = context.get("camera", {})
        if cam.get("shot_type"):
            continuity_parts.append(f"transitioning from {cam['shot_type']}")
        
        if not continuity_parts:
            return None
        
        return PromptPart(
            name="continuity",
            content="[CONTINUITY: " + ", ".join(continuity_parts) + "]",
            priority=9,
            provider_tags=["all"]
        )
    
    def _compile_style(self, plan: ShotPlan) -> PromptPart:
        """Compile global style."""
        style_parts = [plan.global_style]
        
        if plan.style_references:
            refs = ", ".join(plan.style_references[:3])  # Limit references
            style_parts.append(f"inspired by {refs}")
        
        return PromptPart(
            name="style",
            content=", ".join(style_parts),
            priority=4,
            provider_tags=["all"]
        )
    
    # ============ Prompt Assembly ============
    
    def _assemble_prompt(self, parts: List[PromptPart]) -> str:
        """Assemble parts into final prompt."""
        # Group by priority tiers
        high_priority = [p for p in parts if p.priority >= 8]
        medium_priority = [p for p in parts if 4 <= p.priority < 8]
        low_priority = [p for p in parts if p.priority < 4]
        
        sections = []
        
        # High priority first
        if high_priority:
            sections.append(". ".join(p.content for p in high_priority))
        
        # Medium priority
        if medium_priority:
            sections.append(", ".join(p.content for p in medium_priority))
        
        # Low priority
        if low_priority:
            sections.append(", ".join(p.content for p in low_priority))
        
        return ". ".join(sections)
    
    def _build_negative_prompt(
        self,
        shot: Shot,
        plan: Optional[ShotPlan]
    ) -> str:
        """Build negative prompt."""
        negatives = [self.default_negative]
        
        # Shot-specific negatives
        if shot.negative_prompt:
            negatives.append(shot.negative_prompt)
        
        # Plan-level negatives
        if plan and plan.negative_prompt:
            negatives.append(plan.negative_prompt)
        
        return ", ".join(n for n in negatives if n)
    
    def _get_default_negative(self) -> str:
        """Get default negative prompt."""
        return (
            "blurry, low quality, distorted, deformed, disfigured, "
            "bad anatomy, wrong proportions, extra limbs, missing limbs, "
            "floating limbs, disconnected limbs, mutation, mutated, "
            "ugly, disgusting, bad art, amateur, poorly drawn, "
            "jpeg artifacts, watermark, text, signature, "
            "inconsistent lighting, flickering, temporal inconsistency"
        )
    
    # ============ Provider-Specific Generation ============
    
    def _generate_provider_prompts(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> Dict[str, str]:
        """Generate provider-specific prompt variations."""
        prompts = {}
        
        for provider, template_fn in self.provider_templates.items():
            prompts[provider] = template_fn(shot, parts, plan)
        
        return prompts
    
    def _template_vertex_ai(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> str:
        """Generate Vertex AI (Veo) optimized prompt."""
        # Vertex AI prefers structured, clear prompts
        sections = []
        
        # Action first
        action = next((p for p in parts if p.name == "action"), None)
        if action:
            sections.append(action.content)
        
        # Style reference
        sections.append("cinematic 4K video")
        
        # Camera
        cinema = next((p for p in parts if p.name == "cinematography"), None)
        if cinema:
            sections.append(cinema.content)
        
        # Lighting
        lighting = next((p for p in parts if p.name == "lighting"), None)
        if lighting:
            sections.append(lighting.content)
        
        # Characters
        char_parts = [p for p in parts if p.name.startswith("character_")]
        for cp in char_parts:
            sections.append(cp.content)
        
        return ". ".join(sections)
    
    def _template_sora(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> str:
        """Generate OpenAI Sora optimized prompt."""
        # Sora likes natural, narrative descriptions
        sections = []
        
        # Start with scene/action
        action = next((p for p in parts if p.name == "action"), None)
        if action:
            sections.append(action.content)
        
        # Add cinematography naturally
        cinema = next((p for p in parts if p.name == "cinematography"), None)
        if cinema:
            sections.append(f"The camera captures this in a {cinema.content}")
        
        # Lighting as atmosphere
        lighting = next((p for p in parts if p.name == "lighting"), None)
        if lighting:
            sections.append(f"The scene is bathed in {lighting.content}")
        
        return " ".join(sections)
    
    def _template_runway(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> str:
        """Generate Runway Gen-3 optimized prompt."""
        # Runway likes concise, tag-style prompts
        tags = []
        
        # Action
        action = next((p for p in parts if p.name == "action"), None)
        if action:
            tags.append(action.content)
        
        # Style tags
        tags.append("cinematic")
        tags.append("high quality")
        tags.append("4K")
        
        # Camera
        camera = shot.camera
        shot_type = camera.shot_type
        if isinstance(shot_type, ShotType):
            shot_type = shot_type.value
        tags.append(shot_type.replace("_", " "))
        
        return ", ".join(tags)
    
    def _template_pika(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> str:
        """Generate Pika Labs optimized prompt."""
        # Pika prefers shorter, focused prompts
        action = next((p for p in parts if p.name == "action"), None)
        cinema = next((p for p in parts if p.name == "cinematography"), None)
        
        prompt_parts = []
        if action:
            prompt_parts.append(action.content)
        if cinema:
            prompt_parts.append(cinema.content)
        
        prompt_parts.append("cinematic quality")
        
        return ", ".join(prompt_parts)
    
    def _template_stable_video(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> str:
        """Generate Stable Video Diffusion optimized prompt."""
        # SVD works best with img2vid, but for text prompts:
        sections = []
        
        action = next((p for p in parts if p.name == "action"), None)
        if action:
            sections.append(action.content)
        
        # Motion emphasis
        motion = shot.camera.motion
        if isinstance(motion, CameraMotion):
            motion = motion.value
        if motion != "static":
            sections.append(f"smooth {motion} camera movement")
        
        sections.append("photorealistic, high detail")
        
        return ", ".join(sections)
    
    def _template_kling(
        self,
        shot: Shot,
        parts: List[PromptPart],
        plan: Optional[ShotPlan]
    ) -> str:
        """Generate Kling AI optimized prompt."""
        # Kling prefers detailed scene descriptions
        sections = []
        
        # Full action description
        action = next((p for p in parts if p.name == "action"), None)
        if action:
            sections.append(action.content)
        
        # Characters with detail
        char_parts = [p for p in parts if p.name.startswith("character_")]
        for cp in char_parts:
            sections.append(cp.content)
        
        # Environment
        env = next((p for p in parts if p.name == "environment"), None)
        if env:
            sections.append(env.content)
        
        # Technical quality
        sections.append("professional cinematography, 4K resolution")
        
        return ". ".join(sections)
    
    # ============ Control Signals ============
    
    def _extract_control_signals(self, shot: Shot) -> Dict[str, Any]:
        """Extract control signals for generation."""
        signals = {}
        
        # Camera controls
        signals["camera"] = {
            "motion": shot.camera.motion.value if isinstance(shot.camera.motion, CameraMotion) else shot.camera.motion,
            "motion_speed": shot.camera.motion_speed
        }
        
        # Duration
        if shot.duration:
            signals["duration"] = shot.duration
        else:
            signals["duration_range"] = {
                "min": shot.min_duration,
                "max": shot.max_duration
            }
        
        # Effects
        effects = shot.effects
        if effects.slow_motion:
            signals["slow_motion"] = effects.slow_motion_factor
        if effects.time_lapse:
            signals["time_lapse"] = effects.time_lapse_factor
        
        # Seed
        if shot.seed:
            signals["seed"] = shot.seed
        
        # Transition hints
        signals["transition_in"] = shot.transition_in.value if isinstance(shot.transition_in, Transition) else shot.transition_in
        signals["transition_out"] = shot.transition_out.value if isinstance(shot.transition_out, Transition) else shot.transition_out
        
        return signals


# ============ Convenience Functions ============

def compile_shot(
    shot: Shot,
    scene_graph: Optional[SceneGraph] = None,
    plan: Optional[ShotPlan] = None,
    style: PromptStyle = PromptStyle.STANDARD
) -> CompiledPrompt:
    """Compile a single shot to prompt."""
    compiler = StructuredPromptCompiler(style=style)
    return compiler.compile(shot, scene_graph, plan)


def compile_plan(
    plan: ShotPlan,
    scene_graph: Optional[SceneGraph] = None,
    style: PromptStyle = PromptStyle.STANDARD
) -> List[CompiledPrompt]:
    """Compile all shots in a plan."""
    compiler = StructuredPromptCompiler(style=style)
    return compiler.compile_batch(plan, scene_graph)


def quick_prompt(
    action: str,
    shot_type: str = "medium",
    mood: str = "cinematic"
) -> str:
    """Generate a quick prompt from minimal input."""
    shot = Shot(
        action=action,
        camera=CameraSpec(shot_type=ShotType(shot_type) if shot_type in [e.value for e in ShotType] else ShotType.MEDIUM)
    )
    
    compiler = StructuredPromptCompiler(style=PromptStyle.STANDARD)
    compiled = compiler.compile(shot)
    return compiled.main_prompt
