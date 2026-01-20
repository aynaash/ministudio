# Quick Start Guide

Get up and running with Ministudio in 10 minutes. This guide covers the essentials to generate your first AI video.

## Prerequisites

- Python 3.8+
- Internet connection (for API providers)

## 1. Installation

```bash
# Install Ministudio
pip install ministudio

# Verify installation
ministudio --help
```

## 2. Your First Video (Mock Provider)

No API keys needed for testing:

```bash
ministudio --provider mock --concept "Hello World" --action "orb waving"
```

You should see:
```
✓ Video generated successfully!
  Provider: mock
  Time: 1.0s
  Saved to: ./ministudio_output/Hello_World_123456789.mp4
```

## 3. Understanding the Output

Ministudio creates videos in `./ministudio_output/` by default. The mock provider generates a placeholder file for testing.

## 4. Real Providers

### Google Vertex AI

```bash
# Set your project ID
export GCP_PROJECT_ID="your-google-cloud-project"

# Install Vertex AI support
pip install ministudio[vertex-ai]

# Generate video
ministudio --provider vertex-ai --concept "Nature" --action "forest growing"
```

### OpenAI Sora

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# Install OpenAI support
pip install ministudio[openai]

# Generate video
ministudio --provider openai-sora --concept "Ocean" --action "waves crashing"
```

## 5. Python API Usage

```python
import asyncio
from ministudio import Ministudio

async def main():
    # Create provider
    provider = Ministudio.create_provider("mock")

    # Create studio
    studio = Ministudio(provider=provider)

    # Generate video
    result = await studio.generate_concept_video(
        concept="Programming",
        action="code appearing on screen"
    )

    if result.success:
        print(f"Video created: {result.video_path}")
    else:
        print(f"Error: {result.error}")

# Run the async function
asyncio.run(main())
```

## 6. Using Styles

Make your videos consistent:

```python
from ministudio import Ministudio, StyleConfig

# Define a style
style = StyleConfig(
    name="tutorial",
    characters={
        "teacher": {
            "appearance": "Friendly robot instructor",
            "motion": "Gesturing helpfully"
        }
    },
    environment={
        "lighting": "Bright classroom",
        "setting": "Clean educational space"
    }
)

# Use the style
studio = Ministudio(provider=provider, style_config=style)

result = await studio.generate_concept_video(
    concept="Math",
    action="teacher explaining algebra"
)
```

## 7. Templates

Use predefined templates for common scenarios:

```python
from ministudio.templates import explainer_template

result = await studio.generate_concept_video(
    concept="Photosynthesis",
    action="plant absorbing sunlight",
    template=explainer_template
)
```

## 8. API Server

Run your own video generation server:

```bash
# Install server dependencies
pip install ministudio[all]

# Start server
uvicorn ministudio.api:app --host 0.0.0.0 --port 8000
```

Test the API:

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"concept": "test", "action": "orb floating", "duration": 8}'
```

## 9. Docker Usage

```bash
# Build image
docker build -t ministudio .

# Run container
docker run -p 8000:8000 ministudio
```

## 10. Next Steps

- Explore [Styles and Templates](styles.md)
- Learn about [Providers](providers.md)
- Check out [Examples](examples.md)
- Read the [API Reference](api.md)

## Troubleshooting

### Common Issues

**"Module not found"**: Ensure Ministudio is installed: `pip install ministudio`

**"Provider not found"**: Check provider name and installation: `pip install ministudio[provider-name]`

**"API key error"**: Verify environment variables are set correctly

**"No video generated"**: Check provider status and quota/limits

### Getting Help

- [GitHub Issues](https://github.com/yourusername/ministudio/issues)
- [Documentation](https://yourusername.github.io/ministudio/)
- [Discord Community](https://discord.gg/ministudio)

## What's Next?

Now that you have Ministudio working:

1. Experiment with different concepts and actions
2. Try various styles for consistent branding
3. Set up multiple providers for comparison
4. Integrate into your applications
5. Contribute back to the community

Happy video generating! 🎬
