from ..config import Character, Environment, VideoConfig, Color

# --- Ghibli Character Bible ---

EMMA = Character(
    name="Emma",
    genetics={
        "description": "Young woman, short brown hair that flutters in the wind, expressive large eyes, Ghibli heroine aesthetic, wearing a blue sweater with soft wool texture",
        "animation": "Fluid, expressive facial movements, gentle blinking, hair swaying organically, painterly hand-drawn feel"
    },
    voice_id="en-US-Studio-O"
)

DAVID = Character(
    name="David",
    genetics={
        "description": "Earnest young professional, glasses that catch the light, green scarf, Ghibli student style, warm skin tones",
        "animation": "Thoughtful micro-expressions, adjusting glasses, smooth posture shifts, expressive hand gestures"
    },
    voice_id="en-US-Studio-O"
)

ORB = Character(
    name="ContextKeeper Orb",
    genetics={
        "appearance": "Golden glowing orb with warm inner light, size of a tennis ball",
        "surface": "Translucent with gentle data-circuit patterns flowing inside like koi fish",
        "glow": "Soft golden (#D4AF37) with ethereal teal (#008080) accents",
        "animation": "Pulsing rhythmic light, trailing soft particles, organic floating motion like a dandelion"
    }
)

GHIBLI_ENVIRONMENT = Environment(
    location="Studio Ghibli painterly aesthetic",
    generation_rules={
        "style": "Hand-drawn textures, Makoto Shinkai cinematic lighting",
        "lighting": "Golden hour, warm rays, long shadows, lens flares",
        "atmosphere": "Magical realism, floating bioluminescent particles, soft depth of field"
    }
)

GHIBLI_CONFIG = VideoConfig(
    style_name="ghibli",
    duration_seconds=10,
    aspect_ratio="16:9",
    characters={
        "Emma": EMMA,
        "David": DAVID,
        "Orb": ORB
    },
    environment=GHIBLI_ENVIRONMENT,
    custom_metadata={
        "technical": "cinematic framing, detailed painterly textures, hand-drawn animation feel, NO CGI LOOK"
    }
)
