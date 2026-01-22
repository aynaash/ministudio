
import pytest
from ministudio import VideoConfig, Persona, DEFAULT_PERSONA, ProgrammaticPromptCompiler


def test_persona_in_config():
    """Test that persona can be added to VideoConfig."""
    persona = Persona(name="test", description="desc", expertise=["exp"])
    config = VideoConfig(persona=persona)
    assert config.persona.name == "test"
    assert config.persona.description == "desc"
    assert "exp" in config.persona.expertise


def test_persona_serialization():
    """Test that persona survives serialization."""
    persona = Persona(name="test", description="desc")
    config = VideoConfig(persona=persona)
    data = config.to_dict()
    assert data["persona"]["name"] == "test"

    new_config = VideoConfig.from_dict(data)
    assert isinstance(new_config.persona, Persona)
    assert new_config.persona.name == "test"


def test_compiler_includes_persona():
    """Test that the compiler includes persona in the generated prompt."""
    persona = Persona(
        name="Director",
        description="A strict director.",
        expertise=["shouting", "pacing"]
    )
    config = VideoConfig(persona=persona, action_description="Scene start")
    compiler = ProgrammaticPromptCompiler()
    prompt = compiler.compile(config)

    assert "ROLE: Director" in prompt
    assert "A strict director." in prompt
    assert "TECHNICAL EXPERTISE: shouting, pacing" in prompt
    assert "ACTION:\nScene start" in prompt


def test_default_persona_injection():
    """Test using the DEFAULT_PERSONA."""
    config = VideoConfig(persona=DEFAULT_PERSONA,
                         action_description="A wide shot of a valley")
    compiler = ProgrammaticPromptCompiler()
    prompt = compiler.compile(config)

    assert "ROLE: Master Filmmaker" in prompt
    assert "You are a master filmmaker" in prompt
    assert "TECHNICAL EXPERTISE: wide angle shots" in prompt
