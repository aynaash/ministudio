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

        # 0. GLOBAL IDENTITY & CONSISTENCY (Authoritative anchors)
        global_identity = ["CRITICAL: MAINTAIN ABSOLUTE VISUAL CONSISTENCY"]
        if config.characters:
            char_names = ", ".join(config.characters.keys())
            global_identity.append(
                f"- Characters {char_names} MUST look identical to previous shots.")
        if config.environment:
            global_identity.append(
                f"- Background ({config.environment.location}) MUST remain stationary and unchanged.")
        sections.append("\n".join(global_identity))

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
            # Check for shot type in custom_metadata if not explicitly provided
            shot_info = ""
            if config.custom_metadata.get("shot_type"):
                shot_info = f"SHOT TYPE: {config.custom_metadata['shot_type']}\n"
            sections.append(f"{shot_info}ACTION:\n{config.action_description}")

        # 7. CONTINUITY
        if config.continuity:
            sections.append(self._compile_continuity(config.continuity))

        # Join with double newlines for clear separation
        return "\n\n".join(sections)

    def _compile_characters(self, characters: dict) -> str:
        lines = ["GLOBAL CHARACTER IDENTITY (PERSISTENT ANCHORS):"]
        lines.append(
            "CRITICAL: THE FOLLOWING FEATURES ARE STATIC AND MUST NOT CHANGE ACROSS SHOTS.")

        for name, char in characters.items():
            desc = f"- {name}:"

            # Grounding Instructions
            grounding = []
            if hasattr(char, 'identity') and any(char.identity.values()):
                id_stats = char.identity
                if id_stats.get("hair_style") or id_stats.get("hair_color"):
                    grounding.append(
                        f"HAIR: {id_stats.get('hair_style')} ({id_stats.get('hair_color')})")
                if id_stats.get("eye_color"):
                    grounding.append(f"EYES: {id_stats.get('eye_color')}")
                if id_stats.get("face_shape") or id_stats.get("skin_tone"):
                    grounding.append(
                        f"FACE: {id_stats.get('face_shape')} skin, {id_stats.get('skin_tone')} tone")

                # Add remainder of identity
                other_identity = {k: v for k, v in id_stats.items() if k not in [
                    "hair_style", "hair_color", "eye_color", "face_shape", "skin_tone"] and v}
                if other_identity:
                    grounding.append(
                        f"FEATURES: {self._dict_to_readable(other_identity)}")

            if grounding:
                desc += f" [STRICT ANCHORS: {', '.join(grounding)}]"
            elif char.genetics:
                desc += f" {self._dict_to_readable(char.genetics)}"

            if hasattr(char, 'visual_anchor_path') and char.visual_anchor_path:
                desc += f" (CRITICAL: REPLICATE THE FACE IN THE PROVIDED PORTRAIT ANCHOR EXACTLY)"
            elif char.reference_images:
                desc += f" (Referencing visual samples of {name})"

            lines.append(desc)

            # Local state for characters
            if hasattr(char, 'current_state') and any(char.current_state.values()):
                lines.append(
                    f"  CURRENT STATE (SHOT-SPECIFIC): {self._dict_to_readable(char.current_state)}")

            if char.motion_library:
                lines.append(
                    f"  Motion: {self._dict_to_readable(char.motion_library)}")

        return "\n".join(lines)

    def _compile_environment(self, env: Environment) -> str:
        lines = ["ENVIRONMENT IDENTITY (PERSISTENT BACKGROUND):"]
        lines.append(f"- Location: {env.location}")

        # Identity (Fixed architecture/base)
        if hasattr(env, 'identity') and any(env.identity.values()):
            lines.append(
                f"- Visual Base: {self._dict_to_readable(env.identity)}")

        # Local Context (Lighting, dynamic props)
        if hasattr(env, 'current_context') and any(env.current_context.values()):
            lines.append(
                f"- Current Scene Context: {self._dict_to_readable(env.current_context)}")

        if env.reference_images:
            lines.append(
                f"- Visual Identity: Matching provided background samples")
        if env.composition:
            lines.append(
                f"- Composition: {self._dict_to_readable(env.composition)}")
        return "\n".join(lines)

    def _compile_cinematography(self, cine: Cinematography) -> str:
        lines = ["CINEMATOGRAPHY & LIP SYNC:"]
        active = cine.camera_behaviors.get(cine.active_camera)
        if active:
            lines.append(
                f"- Camera: {active.lens}, {active.aperture}, movement: {active.movement_style}")

        # Add Lip Sync instruction if dialogue is expected
        lines.append(
            "- CRITICAL: If a character is speaking, ensure their lips sync perfectly with the dialogue.")

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
