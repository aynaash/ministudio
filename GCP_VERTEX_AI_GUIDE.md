# Using Ministudio with Google Cloud Vertex AI

A comprehensive guide to using Ministudio for AI video generation with Google Cloud Vertex AI (Veo).

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setting up Google Cloud Project](#setting-up-google-cloud-project)
- [Enabling Vertex AI API](#enabling-vertex-ai-api)
- [Service Account Setup](#service-account-setup)
- [Authentication](#authentication)
- [Installing Ministudio](#installing-ministudio)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

## Overview

Ministudio integrates with Google Cloud Vertex AI to generate videos using the Veo model. This guide shows you how to set up authentication and use Ministudio with GCP resources.

### Key Features
- **State Persistence**: Maintain visual consistency across video segments
- **Model-Agnostic**: Easy provider switching
- **Production Ready**: Robust authentication and error handling
- **Scalable**: Works with GCP's enterprise-grade infrastructure

## Prerequisites

- Google Cloud account with billing enabled
- Python 3.8+
- Basic familiarity with command line and environment variables

## Setting up Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your Project ID (you'll need this later)

## Enabling Vertex AI API

1. In the Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Vertex AI API"
3. Click on it and enable the API

Alternatively, use the command line:
```bash
gcloud services enable aiplatform.googleapis.com
```

## Service Account Setup

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Give it a name like "ministudio-vertex-ai"
4. Grant the following roles:
   - `Vertex AI User`
   - `Storage Object Admin` (if you want to save videos to GCS)
5. Create the service account
6. Click on the service account email
7. Go to "Keys" tab
8. Click "Add Key" > "Create new key"
9. Choose JSON format
10. Download the JSON key file

## Authentication

Ministudio supports multiple authentication methods for GCP:

### Method 1: Service Account JSON (Recommended)

Set the path to your JSON key file:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
```

### Method 2: JSON Content as Environment Variable

Copy the entire JSON content and set as environment variable:
```bash
export GCP_SERVICE_ACCOUNT_JSON='{"type": "service_account", "project_id": "...", ...}'
```

### Method 3: Individual Environment Variables

Set each component separately:
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_CLIENT_EMAIL="your-service-account@project.iam.gserviceaccount.com"
export GCP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
```

### Method 4: GCP CLI Authentication

If you have `gcloud` installed and authenticated:
```bash
gcloud auth application-default login
```

Ministudio will automatically try all methods in order until one succeeds.

## Installing Ministudio

Install from PyPI with GCP support:
```bash
pip install ministudio[vertex-ai]
```

Or install all providers:
```bash
pip install ministudio[all]
```

## Basic Usage

### Python Code Example

```python
import asyncio
from ministudio import Ministudio

async def main():
    # Create Vertex AI provider (credentials loaded automatically)
    provider = Ministudio.create_provider("vertex-ai", project_id="your-project-id")

    # Create Ministudio instance
    studio = Ministudio(provider=provider)

    # Generate a basic video
    result = await studio.generate_concept_video(
        concept="Nature",
        action="forest growing in time lapse"
    )

    if result.success:
        print(f"Video generated: {result.video_path}")
        print(f"Generation time: {result.generation_time:.1f}s")
    else:
        print(f"Error: {result.error}")

# Run the example
asyncio.run(main())
```

### Command Line Usage

```bash
# Set your GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Generate video
ministudio --provider vertex-ai --concept "Ocean" --action "waves crashing"
```

## Advanced Usage

### Segmented Video Generation with State Persistence

```python
import asyncio
from ministudio import Ministudio, VideoConfig

async def generate_story_video():
    # Setup provider
    provider = Ministudio.create_provider("vertex-ai", project_id="your-project-id")
    studio = Ministudio(provider=provider)

    # Define video segments with state updates
    segments = [
        {
            "concept": "Introduction",
            "action": "hero enters mystical forest"
        },
        {
            "concept": "Discovery",
            "action": "hero finds glowing artifact",
            "state_updates": {
                "character": {"inventory": ["artifact"]},
                "environment": {"lighting": "mystical"}
            }
        },
        {
            "concept": "Challenge",
            "action": "hero battles guardian with artifact power",
            "state_updates": {
                "character": {"power": "enhanced"}
            }
        },
        {
            "concept": "Triumph",
            "action": "hero emerges victorious"
        }
    ]

    # Generate segmented video
    results = await studio.generate_segmented_video(segments)

    # Check results
    for i, result in enumerate(results, 1):
        if result.success:
            print(f"Segment {i}: Generated successfully")
        else:
            print(f"Segment {i}: Failed - {result.error}")

asyncio.run(generate_story_video())
```

### Custom Configuration

```python
from ministudio import VideoConfig

# Create custom config
config = VideoConfig(
    duration_seconds=15,
    aspect_ratio="16:9",
    style_name="cinematic"
)

# Use with generation
result = await studio.generate_concept_video(
    concept="Space Exploration",
    action="astronaut discovers alien planet",
    config=config
)
```

### Using with Gradio Web UI

```python
from ministudio.gradio_app import demo

# Launch web interface
demo.launch()
```

## Troubleshooting

### Authentication Issues

**Error: "Failed to load GCP credentials"**
- Check that you've set one of the authentication methods above
- Verify your service account has the correct permissions
- Ensure the JSON key file is readable and not corrupted

**Error: "Permission denied"**
- Make sure your service account has "Vertex AI User" role
- Check that the Vertex AI API is enabled in your project

### API Errors

**Error: "Quota exceeded"**
- Check your GCP billing and quotas in the Cloud Console
- Vertex AI has usage limits that can be increased

**Error: "Model not available"**
- Ensure you're using a supported region (us-central1 recommended)
- Check Vertex AI service status

### Video Generation Issues

**Error: "No video generated"**
- Try simplifying your prompt
- Check that aspect_ratio and duration_seconds are supported values
- Verify your project has sufficient quota

**Slow generation times**
- Video generation can take several minutes
- Consider using shorter durations for testing

### Environment Variables

**Windows PowerShell escaping issues**
- Use single quotes around JSON content
- Or save JSON to file and use file path

**Docker container issues**
- Mount credentials file as volume
- Use environment variables for JSON content

## Resources

### Documentation
- [Ministudio Documentation](https://aynaash.github.io/ministudio/)
- [Google Cloud Vertex AI](https://cloud.google.com/vertex-ai)
- [Veo Model Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo)

### GCP Console Links
- [Vertex AI Studio](https://console.cloud.google.com/vertex-ai/studio)
- [API Dashboard](https://console.cloud.google.com/apis/dashboard)
- [IAM Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)

### Community
- [Ministudio GitHub](https://github.com/aynaash/ministudio)
- [Google Cloud Community](https://cloud.google.com/community)

### Pricing
- [Vertex AI Pricing](https://cloud.google.com/vertex-ai/pricing)
- [Free Tier Limits](https://cloud.google.com/free/docs/free-tier-limits)

## Best Practices

1. **Security**: Never commit service account keys to version control
2. **Cost Control**: Monitor usage in GCP Console and set budgets
3. **Testing**: Use short videos and simple prompts for development
4. **Regions**: Start with us-central1 for lowest latency
5. **Monitoring**: Check Cloud Logging for detailed error information

## Support

- **Ministudio Issues**: [GitHub Issues](https://github.com/aynaash/ministudio/issues)
- **GCP Support**: [Cloud Support](https://cloud.google.com/support)
- **Vertex AI Forums**: [AI/ML Forums](https://cloud.google.com/vertex-ai/docs/support/forum)

---

This guide covers everything you need to start using Ministudio with GCP Vertex AI. For the latest updates, check the official documentation. 🚀
