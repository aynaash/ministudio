# MiniStudio Simple Builder - Non-Technical User Features

**Summary of easy-to-use features for non-technical users who just want to describe and generate videos.**

---

## 🎯 Overview

The **Simple Builder** module (`ministudio.simple_builder`) is designed for non-technical users. It:

✅ Takes natural language descriptions  
✅ Automatically creates configs (no code needed)  
✅ Handles provider selection automatically  
✅ Includes templates for common scenarios  
✅ Provides interactive setup mode  

---

## 📁 What Was Added

### 1. Core Module: `simple_builder.py`
- `generate_video()` - Synchronous function (simplest)
- `generate_video_from_description()` - Async version
- `SimpleBuilder` class - Configuration helpers
- `generate_from_template()` - Use pre-made templates
- `interactive_setup()` - Step-by-step setup
- Pre-built templates (sci-fi, fantasy, cyberpunk, etc.)

### 2. Examples: `examples/simple_examples.py`
8 runnable examples showing:
- Simplest way (just describe)
- Templates
- Synchronous usage
- Provider selection
- Interactive mode
- Multiple videos
- With characters
- Template gallery

### 3. Documentation: `docs/for_non_technical_users.md`
Complete guide including:
- Installation (one-time setup)
- Getting API keys
- Usage examples
- Q&A
- Troubleshooting
- Workflow recommendations

---

## 🚀 Quick Start

### Option 1: Interactive (No Code!)
```bash
python ministudio/simple_builder.py
```

### Option 2: Simple Python
```python
from ministudio.simple_builder import generate_video

result = generate_video("""
A scientist discovers a glowing orb.
Duration: 10 seconds
Style: cinematic
""")
```

### Option 3: Run Examples
```bash
python examples/simple_examples.py
```

---

## 📝 How Users Describe Videos

### Basic
```
A warrior walks through a forest
```

### With Duration
```
A wizard casts a spell
Duration: 8 seconds
```

### With Style
```
A robot dances in a futuristic city
Style: cyberpunk
```

### Complete
```
A scientist carefully examines a crystal in the lab.
The crystal begins to glow brightly.
She looks amazed and reaches towards it.
Duration: 12 seconds
Style: cinematic
```

---

## 🎨 Supported Styles

| Style | Purpose |
|-------|---------|
| **cinematic** | Movies, drama |
| **cyberpunk** | Sci-fi, tech |
| **ghibli** | Whimsical, magical |
| **realistic** | Natural, documentary |
| **fantasy** | Epic, magical |
| **horror** | Scary, dark |
| **comedy** | Funny, lighthearted |

---

## 📦 Pre-Built Templates

Users can generate videos instantly from templates:

```python
from ministudio.simple_builder import generate_from_template

await generate_from_template("sci-fi-lab")
await generate_from_template("fantasy-quest")
await generate_from_template("cyberpunk-city")
```

Available: `sci-fi-lab`, `fantasy-quest`, `cyberpunk-city`, `nature-journey`, `comedy-moment`

---

## 🔄 Automatic Provider Selection

The system automatically picks the best provider:

```python
# "auto" tries: Vertex AI → Hugging Face → Local
result = generate_video(description, provider="auto")

# Or specify:
result = generate_video(description, provider="vertex_ai")
result = generate_video(description, provider="huggingface")
result = generate_video(description, provider="local")
```

---

## 🧩 Architecture

```python
User Input (Description)
    ↓
SimpleBuilder.parse_description()  ← Extracts action, duration, style
    ↓
SimpleBuilder.create_shot_config()  ← Creates ShotConfig
    ↓
SimpleBuilder.get_provider()  ← Gets video provider (auto or specified)
    ↓
VideoOrchestrator  ← Generates the video
    ↓
VideoGenerationResult  ← Returns path to video
```

---

## 💻 Synchronous API (For Non-Programmers)

Non-technical users don't need to understand async/await:

```python
# SIMPLE - Just works
from ministudio.simple_builder import generate_video
result = generate_video("A wizard casts a spell")

# NOT NEEDED - (But available if you know async)
# import asyncio
# from ministudio.simple_builder import generate_video_from_description
# result = asyncio.run(generate_video_from_description("..."))
```

---

## 🎬 Example Flows

### Flow 1: Complete Beginner
```
1. Run: python ministudio/simple_builder.py
2. Answer questions
3. Watch video generate
4. Done!
```

### Flow 2: Non-Technical User
```
from ministudio.simple_builder import generate_video

result = generate_video("Describe your video here")
print(f"Video at: {result.video_path}")
```

### Flow 3: Using Templates
```
from ministudio.simple_builder import generate_from_template

result = await generate_from_template("sci-fi-lab")
```

### Flow 4: Multiple Videos
```
from ministudio.simple_builder import generate_video

scenes = [
    "Scene 1: The beginning",
    "Scene 2: The middle",
    "Scene 3: The end",
]

for scene in scenes:
    generate_video(scene)
```

---

## 🔑 Key Features

### 1. Natural Language Parsing
Extracts from descriptions:
- **Action**: What happens (required)
- **Duration**: How long (default: 8 seconds)
- **Style**: Visual style (default: cinematic)

### 2. Automatic Config Generation
Creates `ShotConfig` automatically with:
- Enhanced prompts (action + style)
- Proper duration
- Style specifications

### 3. Provider Auto-Selection
Tries providers in order until one works:
1. Vertex AI (best quality)
2. Hugging Face (flexible)
3. Local Model (free)

### 4. Template System
Pre-made scenarios for quick generation:
```python
TEMPLATES = {
    "sci-fi-lab": "...",
    "fantasy-quest": "...",
    "cyberpunk-city": "...",
    "nature-journey": "...",
    "comedy-moment": "...",
}
```

### 5. Interactive Setup
Walks users through:
- Writing description
- Choosing provider
- Confirming settings
- Generating video

---

## 📊 Comparison: Simple vs Advanced

| Feature | Simple Builder | Advanced |
|---------|---|---|
| **Learning Curve** | 5 minutes | 30 minutes+ |
| **Code Required** | 1-3 lines | 10+ lines |
| **For Non-Techs** | ✅ Perfect | ⚠️ Possible |
| **Customization** | Moderate | Extensive |
| **Character Consistency** | Built-in | Built-in |
| **Multi-Provider** | Automatic | Manual |
| **Templates** | 5 pre-built | Build your own |

---

## 🎯 Use Cases

### Use Case 1: Content Creator (Non-Technical)
```python
# Create a video for social media
from ministudio.simple_builder import generate_video

video = generate_video("""
A person opens a mysterious box.
The inside glows with magical light.
Duration: 6 seconds
Style: cinematic
""")
```

### Use Case 2: Marketer
```python
# Generate promotional content
from ministudio.simple_builder import generate_from_template

video = await generate_from_template("sci-fi-lab")
```

### Use Case 3: Student Project
```python
# Tell a story with AI
from ministudio.simple_builder import generate_video

scenes = [
    "The hero arrives at the castle",
    "She discovers the secret",
    "The kingdom is saved",
]

for scene in scenes:
    generate_video(scene)
```

### Use Case 4: Workshop/Training
```
1. Run interactive mode
2. Follow prompts
3. Generate video
4. Learn about AI video generation
```

---

## 🛠️ Technical Details

### SimpleBuilder Class

```python
class SimpleBuilder:
    # Parse natural language
    @staticmethod
    def parse_description(description: str) -> Dict[str, Any]
    
    # Create ShotConfig from request
    @staticmethod
    def create_shot_config(request: SimpleVideoRequest) -> ShotConfig
    
    # Get provider automatically or by name
    @staticmethod
    async def get_provider(provider_name: str = "auto") -> BaseVideoProvider
```

### SimpleVideoRequest Dataclass

```python
@dataclass
class SimpleVideoRequest:
    description: str  # What to generate
    duration_seconds: int = 8  # Length (auto-parsed)
    style: str = "cinematic"  # Visual style (auto-parsed)
    character_names: Optional[Dict[str, str]] = None  # {"Name": "image.jpg"}
    provider: str = "auto"  # Which provider
```

---

## 📈 Benefits Over Raw API

### Without Simple Builder
```python
# Lots of code
from ministudio.config import ShotConfig, VideoConfig, ProviderConfig
from ministudio.adapters import VertexAIAdapter
from ministudio import VideoOrchestrator

provider_config = ProviderConfig(name="vertex_ai", ...)
video_config = VideoConfig(provider=provider_config, ...)
shot_config = ShotConfig(...)
provider = VertexAIAdapter.create(...)
orchestrator = VideoOrchestrator(provider)
result = await orchestrator.generate_shot(shot_config)
```

### With Simple Builder
```python
# One line!
result = generate_video("A wizard casts a spell")
```

---

## 🚀 Future Enhancements

Potential improvements:
- [ ] LLM-powered description enhancement
- [ ] Auto-character detection from images
- [ ] Web UI for interactive generation
- [ ] Voice input support
- [ ] Mobile app
- [ ] More templates (100+)
- [ ] Style recommendations
- [ ] Cost estimation UI

---

## 📝 Files & Structure

```
ministudio/
├── simple_builder.py                     # Core module
│   ├── SimpleBuilder class
│   ├── generate_video() function
│   ├── generate_from_template() function
│   ├── interactive_setup() function
│   └── TEMPLATES dictionary
│
examples/
├── simple_examples.py                    # 8 runnable examples
│
docs/
├── for_non_technical_users.md           # Comprehensive guide
│   ├── Quick start
│   ├── Installation
│   ├── API key setup
│   ├── Usage examples
│   ├── Q&A
│   └── Troubleshooting
│
README.md (UPDATED)
│   ├── Features "For Non-Technical Users"
│   ├── Interactive mode command
│   └── Link to simple guide
```

---

## ✅ Success Criteria

✅ Non-technical users can generate videos in < 5 minutes  
✅ No code knowledge required  
✅ Works with interactive mode or simple Python  
✅ Automatic provider selection  
✅ Pre-built templates for quick start  
✅ Clear error messages  
✅ Comprehensive documentation  

---

## 🎉 Impact

This feature makes MiniStudio accessible to:
- ✅ Content creators
- ✅ Marketers
- ✅ Students
- ✅ Teachers
- ✅ Non-programmers
- ✅ Anyone wanting to try AI video generation

Without requiring any coding knowledge!

