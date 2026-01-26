# MiniStudio for Non-Technical Users

**No coding experience needed! Just describe what you want and MiniStudio handles the rest.**

---

## 🎬 The Easiest Way to Start

### Option 1: Interactive Mode (Recommended for Beginners)

```bash
cd ministudio
python ministudio/simple_builder.py
```

Then follow the prompts:
1. Describe what you want to generate
2. Choose a provider (or let us pick)
3. Watch your video get created!

### Option 2: Just Write a Script

```python
from ministudio.simple_builder import generate_video

description = """
A scientist discovers a glowing orb in the lab.
She looks amazed and reaches towards it.
Duration: 10 seconds
Style: cinematic
"""

result = generate_video(description)
print(f"Video saved to: {result.video_path}")
```

### Option 3: Run Pre-Made Examples

```bash
python examples/simple_examples.py
```

Choose from:
- 1️⃣ Simplest way
- 2️⃣ Using templates
- 5️⃣ Interactive mode
- And more!

---

## 📝 How to Describe Your Video

Just write naturally! MiniStudio understands:

### Basic Description
```
A lone warrior stands at the edge of a cliff.
She watches the sunset.
```

### With Duration
```
A wizard casts a spell.
Magical lights appear around them.
Duration: 10 seconds
```

### With Style
```
A futuristic robot walks through a neon city.
Flying cars zoom past overhead.
Duration: 8 seconds
Style: cyberpunk
```

### Full Example
```
A chef prepares a gourmet meal in a professional kitchen.
They carefully plate each element with precision.
The camera zooms in to show the final creation.
Duration: 12 seconds
Style: realistic
```

---

## 🎨 Supported Styles

| Style | Best For | Example |
|-------|----------|---------|
| **cinematic** | Movies, drama | A tense confrontation scene |
| **cyberpunk** | Sci-fi, tech | Neon-lit futuristic city |
| **ghibli** | Animation, whimsy | Magical forest adventure |
| **realistic** | Documentary, natural | Nature scenes, everyday life |
| **fantasy** | Epic, magical | Dragon encounters, wizards |
| **horror** | Scary, suspenseful | Dark, atmospheric scenes |
| **comedy** | Funny, lighthearted | Silly, exaggerated moments |

### How to Use Styles

Just mention the style in your description:

```
A warrior battles a dragon in a magical land.
Duration: 15 seconds
Style: fantasy
```

---

## 🚀 Quick Start Templates

We have pre-made scenarios you can use:

```python
from ministudio.simple_builder import generate_from_template

# Generate from template
result = await generate_from_template("sci-fi-lab")
```

### Available Templates

**sci-fi-lab** - Scientist discovers a glowing orb
```
A scientist in a futuristic lab discovers a mysterious glowing orb.
She looks amazed and reaches towards it.
The camera slowly zooms in.
Duration: 10 seconds
Style: cinematic
```

**fantasy-quest** - Warrior at the forest edge
```
A brave warrior stands at the edge of a magical forest.
She draws her sword as mysterious lights appear.
The camera pans to reveal an ancient castle.
Duration: 12 seconds
Style: fantasy
```

**cyberpunk-city** - Hacker in neon room
```
A hacker in a neon-lit room stares at holographic screens.
Futuristic code and data streams surround them.
The camera zooms through the digital landscape.
Duration: 8 seconds
Style: cyberpunk
```

**nature-journey** - Peaceful waterfall
```
A peaceful waterfall in a lush forest.
Birds fly through the canopy as sunlight filters through.
The camera reveals a hidden cave behind the water.
Duration: 10 seconds
Style: realistic
```

**comedy-moment** - Slapstick humor
```
A character slips on a banana peel and tumbles hilariously.
Friends laugh in the background.
Everything is silly and exaggerated.
Duration: 6 seconds
Style: comedy
```

---

## 💻 Installation (One-Time Setup)

### Step 1: Install Python
Download Python from https://www.python.org/downloads/ (any recent version)

### Step 2: Install MiniStudio
```bash
# In your terminal/command prompt, run:
git clone https://github.com/hersi/ministudio.git
cd ministudio
pip install -e .
```

### Step 3: Setup Credentials
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your API keys
# See "Getting API Keys" below
```

---

## 🔑 Getting API Keys (Choose One Provider)

### Option A: Vertex AI (Best Quality)

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "Vertex AI API"
4. Create a service account and download the JSON key
5. Add to `.env`:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
VERTEX_AI_PROJECT_ID=your-project-id
```

**Cost:** ~$0.10 per video | **Quality:** Highest | **Setup Time:** 10 minutes

### Option B: Hugging Face (Flexible)

1. Sign up at https://huggingface.co/join
2. Go to https://huggingface.co/settings/tokens
3. Create a new "read" token
4. Add to `.env`:
```env
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxx
```

**Cost:** Free (local) or $ (cloud) | **Quality:** High | **Setup Time:** 5 minutes

### Option C: Local (Free & Private)

1. Download a model (no sign-up needed!)
2. Add to `.env`:
```env
LOCAL_MODEL_PATH=/path/to/model
```

**Cost:** Free | **Quality:** Good | **Setup Time:** 15 minutes (download)

---

## 📖 Usage Examples

### Example 1: Simple Description
```python
from ministudio.simple_builder import generate_video

result = generate_video("A cat plays with a ball of yarn")
print(f"Done! Video at: {result.video_path}")
```

### Example 2: Choose a Provider
```python
from ministudio.simple_builder import generate_video

# "auto" picks the best available
# Or use "vertex_ai", "huggingface", "local"
result = generate_video(
    "A wizard casts a spell",
    provider="auto"
)
```

### Example 3: Multiple Videos
```python
from ministudio.simple_builder import generate_video_from_description
import asyncio

async def make_videos():
    scenes = [
        "A warrior draws a sword",
        "The battle begins",
        "Victory is achieved",
    ]
    
    for scene in scenes:
        await generate_video_from_description(scene)
        print(f"✅ Created: {scene}")

asyncio.run(make_videos())
```

### Example 4: With Characters
```python
from ministudio.simple_builder import generate_video

result = generate_video(
    "Emma the scientist discovers a crystal",
    character_names={"Emma": "emma_photo.jpg"}
)
```

---

## ❓ Common Questions

### Q: Do I need to know Python?
**A:** No! You can use interactive mode:
```bash
python ministudio/simple_builder.py
```
Just answer the questions!

### Q: Which provider should I use?
**A:** Start with "auto" - it picks the best available:
```python
generate_video("Your description", provider="auto")
```

### Q: How long does generation take?
**A:** 2-5 minutes typically. Depends on:
- Duration (longer = slower)
- Provider (cloud is usually faster)
- Your computer (for local models)

### Q: Can I use my own characters?
**A:** Yes! Add their images:
```python
generate_video(
    "Emma walks through a forest",
    character_names={"Emma": "emma_reference.jpg"}
)
```

### Q: What if I don't have an API key?
**A:** Use the Local Model provider (free, no keys needed)

### Q: Can I make a full movie?
**A:** Yes! Generate multiple shots and stitch them together:
```python
scenes = [
    "Scene 1: The beginning",
    "Scene 2: The conflict",
    "Scene 3: The resolution",
]

for scene in scenes:
    generate_video(scene)
```

### Q: What's the cost?
**A:** Depends on provider:
- **Local:** Free
- **Hugging Face:** Free (local) or ~$1-5 per video
- **Vertex AI:** ~$0.10 per video

### Q: Can I use it offline?
**A:** Yes! Use the Local Model provider (requires GPU)

---

## 🎯 Recommended Workflow

### 1. Try Interactive Mode First
```bash
python ministudio/simple_builder.py
```
Answer the questions and generate your first video!

### 2. Use a Template
```python
from ministudio.simple_builder import generate_from_template
result = await generate_from_template("sci-fi-lab")
```

### 3. Write Your Own Description
```python
from ministudio.simple_builder import generate_video

result = generate_video("""
A mysterious figure enters a dark room.
They look around carefully.
Suddenly, a light appears.
Duration: 8 seconds
Style: mystery
""")
```

### 4. Customize with Providers
```python
result = generate_video(description, provider="vertex_ai")
```

### 5. Create a Series
```python
for scene in your_scenes:
    generate_video(scene)
```

---

## 🆘 Troubleshooting

### "API key not found"
```
✅ Solution: Check that .env file exists in the project root
            with your API key set
```

### "Model not found"
```
✅ Solution: If using Hugging Face:
            - Accept the license on the model page
            - Make sure HF_API_TOKEN is set
```

### "Out of memory"
```
✅ Solution: Use a smaller model or shorter duration
            python -c "from ministudio.simple_builder import generate_video
            generate_video('description', provider='vertex_ai')"
```

### Still stuck?
See [docs/configuration_and_secrets.md](../docs/configuration_and_secrets.md) or ask on GitHub!

---

## 📚 Next Steps

- ✅ **Got your first video?** Great! Try the templates
- ✅ **Want to use specific providers?** See the provider guides
- ✅ **Need advanced features?** Check [docs/configuration_and_secrets.md](../docs/configuration_and_secrets.md)
- ✅ **Want to contribute?** See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 🎉 You're Ready!

You now know how to:
- ✅ Describe videos in natural language
- ✅ Generate them with one line of code
- ✅ Use templates for quick starts
- ✅ Choose providers
- ✅ Add custom characters

**Start with:**
```bash
python ministudio/simple_builder.py
```

Or:
```python
from ministudio.simple_builder import generate_video
generate_video("A wizard casts a spell. Duration: 10 seconds")
```

**Happy creating!** 🎬✨

