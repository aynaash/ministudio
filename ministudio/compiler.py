"""
Programmatic Prompt Compiler.
Compiles high-level "Visual Code" (Objects) into AI-readable text prompts.
"""

from typing import List, Optional
from .config import (
    VideoConfig, Character, Environment, Cinematography,
    LightingDirector, StyleDNA, ContinuityEngine
)


class ProgrammaticPromptCompiler:
    """
    Turns hyper-detailed config objects into engineered text prompts.
    Follows the structure:
    1. Character DNA
    2. Environment Blueprint
    3. Cinematography
    4. Lighting
    5. Style
    6. Action
    7. Continuity
    """

    def compile(self, config: VideoConfig) -> str:
        sections: List[str] = []

        # 1. CHARACTER DNA
        if config.characters:
            sections.append(self._compile_characters(config.characters))

        # 2. ENVIRONMENT
        if config.environment:
            sections.append(self._compile_environment(config.environment))

        # 3. CINEMATOGRAPHY
        if config.cinematography:
            sections.append(self._compile_cinematography(
                config.cinematography))

        # 4. LIGHTING
        if config.lighting:
            sections.append(self._compile_lighting(config.lighting))

        # 5. STYLE
        if config.style_dna:
            sections.append(self._compile_style(config.style_dna))

        # 6. ACTION (The specific scene)
        if config.action_description:
            # Action is the most important, often put first or prominently
            # For this structured format, we append it as a clear instruction
            sections.append(f"ACTION:\n{config.action_description}")

        # 7. CONTINUITY
        if config.continuity:
            sections.append(self._compile_continuity(config.continuity))

        # Join with double newlines for clear separation
        return "\n\n".join(sections)

    def _compile_characters(self, characters: dict) -> str:
        lines = ["CHARACTER SPECIFICATION:"]
        for name, char in characters.items():
            desc = f"- {name}:"
            if char.genetics:
                desc += f" {self._dict_to_readable(char.genetics)}"
            if char.motion_library:
                desc += f" Motion: {self._dict_to_readable(char.motion_library)}"
            lines.append(desc)
        return "\n".join(lines)

    def _compile_environment(self, env: Environment) -> str:
        lines = ["ENVIRONMENT:"]
        lines.append(f"- Location: {env.location}")
        if env.physics:
            lines.append(f"- Physics: {self._dict_to_readable(env.physics)}")
        if env.composition:
            lines.append(
                f"- Composition: {self._dict_to_readable(env.composition)}")
        return "\n".join(lines)

    def _compile_cinematography(self, cine: Cinematography) -> str:
        lines = ["CINEMATOGRAPHY:"]
        active = cine.camera_behaviors.get(cine.active_camera)
        if active:
            lines.append(
                f"- Camera: {active.lens}, {active.aperture}, movement: {active.movement_style}")
        if cine.shot_composition_rules:
            lines.append(
                f"- Rules: {self._dict_to_readable(cine.shot_composition_rules)}")
        return "\n".join(lines)

    def _compile_lighting(self, light: LightingDirector) -> str:
        lines = ["LIGHTING:"]
        for i, k in enumerate(light.key_lights):
            lines.append(
                f"- Key Light {i+1}: {k.type} {k.color} intensity={k.intensity}")
        for i, f in enumerate(light.fill_lights):
            lines.append(f"- Fill Light {i+1}: {f.type} {f.color}")
        return "\n".join(lines)

    def _compile_style(self, style: StyleDNA) -> str:
        lines = ["VISUAL STYLE:"]
        if style.traits:
            lines.append(f"- Traits: {self._dict_to_readable(style.traits)}")
        if style.references:
            lines.append(f"- References: {', '.join(style.references)}")
        return "\n".join(lines)

    def _compile_continuity(self, cont: ContinuityEngine) -> str:
        lines = ["CONTINUITY REQUIREMENTS:"]
        if cont.rules:
            lines.append(f"- Rules: {self._dict_to_readable(cont.rules)}")
        return "\n".join(lines)

    def _dict_to_readable(self, d: dict) -> str:
        """Helper to flatten dicts into readable strings"""
        parts = []
        for k, v in d.items():
            if isinstance(v, dict):
                parts.append(f"{k} ({self._dict_to_readable(v)})")
            elif hasattr(v, 'to_dict'):  # Handle nested objects like Color
                parts.append(f"{k}: {v}")
            else:
                parts.append(f"{k}: {v}")
        return ", ".join(parts)
