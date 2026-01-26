# MiniStudio Quick Reference: Secrets, Config & Providers

**One-page cheat sheet for developers and contributors.**

---

## 🚀 Get Started in 5 Minutes

### Step 1: Clone & Install
```bash
git clone https://github.com/hersi/ministudio.git
cd ministudio
pip install -e .
```

### Step 2: Choose Your Provider

| Provider | Command | Best For |
|----------|---------|----------|
| **Cloud (Vertex AI)** | `cp .env.example .env && edit` | Production, high quality |
| **Local (Free)** | `pip install diffusers torch` | Development, privacy |
| **Hugging Face** | `pip install diffusers` | Flexibility, variety |

### Step 3: Configure & Run
```bash
# Local dev with .env
python examples/contextbytes_brand_story.py

# Production with Doppler
doppler run -- python examples/contextbytes_brand_story.py
```

---

## 📝 Configuration Hierarchy

MiniStudio looks for config in this order (first match wins):

```
1. Doppler (doppler run -- ...)
2. Environment variables (set before running)
3. .env file (in project root)
4. Defaults in code
```

---

## 🔑 Essential Environment Variables

```env
# Required: Choose one video provider
VERTEX_AI_PROJECT_ID=my-gcp-project           # For Vertex AI
HF_API_TOKEN=hf_xxxxx                          # For Hugging Face
LOCAL_MODEL_PATH=/models/text-to-video-ms     # For local inference

# Optional: Other services
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
GOOGLE_TTS_KEY=xxxx
```

**See [.env.example](.env.example) for all 50+ variables.**

---

## 🏗️ Provider Quick Start

### Vertex AI (Recommended for Production)
```python
from ministudio.adapters import VertexAIAdapter

provider = VertexAIAdapter.create(project_id="my-project")
# Cost: ~$0.10 per video
# Setup: 5 min (GCP account + credentials)
```

### Hugging Face (Recommended for Development)
```python
from ministudio.adapters import HuggingFaceAdapter

provider = HuggingFaceAdapter.create()  # Uses default "text-to-video"
# Cost: Free (local) or $ (API)
# Setup: 5 min (HF token)
```

### Local (Free, Private)
```python
from ministudio.adapters import LocalModelAdapter

provider = LocalModelAdapter.create()
# Cost: Free (no API calls)
# Setup: 10 min (download model + GPU setup)
```

---

## 🔄 Hot-Swap Providers at Runtime

```python
from ministudio import VideoOrchestrator
from ministudio.adapters import *

# Try providers in order
providers = [
    VertexAIAdapter.create(),
    HuggingFaceAdapter.create(),
    LocalModelAdapter.create(),
]

for provider in providers:
    try:
        orchestrator.provider = provider
        result = await orchestrator.generate_shot(shot_config)
        break
    except Exception as e:
        logger.warning(f"Provider failed: {e}. Trying next...")
```

---

## 📦 Pre-Configured Adapters

Location: `ministudio/adapters/`

| File | Class | Purpose |
|------|-------|---------|
| `vertex_ai_adapter.py` | `VertexAIAdapter` | GCP Vertex AI Veo 3.1 |
| `huggingface_adapter.py` | `HuggingFaceAdapter` | Open-source HF models |
| `local_model_adapter.py` | `LocalModelAdapter` | Local model inference |

Each has:
- `create()` → Instantiate provider
- `get_setup_instructions()` → Print setup guide
- `list_available_models()` → Show available models (HF)

---

## 🔐 Secrets Management

### Local Development
```bash
# 1. Copy template
cp .env.example .env

# 2. Edit with your credentials
nano .env

# 3. Add to .gitignore (already done)
cat .gitignore | grep "^\.env"

# 4. Load automatically
python your_script.py  # Loads .env automatically
```

### Production (Doppler)
```bash
# 1. Install Doppler CLI
curl -Ls https://cli.doppler.com/install.sh | sh

# 2. Setup secrets
doppler setup
doppler secrets set VERTEX_AI_PROJECT_ID my-project

# 3. Run your app
doppler run -- python examples/contextbytes_brand_story.py
```

### Cloud Secret Managers

**GCP Secret Manager**
```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
secret = client.access_secret_version(
    request={"name": f"projects/PROJECT_ID/secrets/NAME/versions/latest"}
)
api_key = secret.payload.data.decode('UTF-8')
```

**AWS Secrets Manager**
```python
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='ministudio/prod')
api_key = json.loads(secret['SecretString'])['VERTEX_AI_API_KEY']
```

---

## 🧩 Add a New Provider (5 Steps)

### 1. Inherit from BaseVideoProvider
```python
from ministudio.providers.base import BaseVideoProvider

class MyProvider(BaseVideoProvider):
    @property
    def name(self) -> str:
        return "my_provider"
    
    async def generate_video(self, request) -> VideoGenerationResult:
        # Your implementation here
        pass
```

### 2. Create an Adapter
```python
# ministudio/adapters/my_provider_adapter.py
class MyProviderAdapter:
    @staticmethod
    def create(api_key=None, **kwargs):
        if not api_key:
            api_key = os.getenv("MY_PROVIDER_API_KEY")
        return MyProvider(api_key=api_key, **kwargs)
    
    @staticmethod
    def get_setup_instructions():
        return "..."
```

### 3. Update __init__.py
```python
# ministudio/adapters/__init__.py
from .my_provider_adapter import MyProviderAdapter

__all__ = [..., "MyProviderAdapter"]
```

### 4. Add Tests
```python
# tests/test_providers.py
@pytest.mark.asyncio
async def test_my_provider():
    provider = MyProviderAdapter.create()
    result = await provider.generate_video(request)
    assert result is not None
```

### 5. Submit PR
Push to GitHub and create a pull request!

---

## 🛠️ Useful Commands

```bash
# List available HF models
python -c "from ministudio.adapters import HuggingFaceAdapter; print(HuggingFaceAdapter.list_available_models())"

# Get setup instructions
python -c "from ministudio.adapters import VertexAIAdapter; print(VertexAIAdapter.get_setup_instructions())"

# Test provider connection
python -c "
from ministudio.adapters import LocalModelAdapter
provider = LocalModelAdapter.create()
print(f'✅ Provider ready: {provider.name}')
"

# Check environment variables
env | grep -E "VERTEX_AI|HF_API|LOCAL_MODEL"
```

---

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| `ValueError: API key not found` | Verify `.env` exists and is in project root |
| `Model not found (HF)` | Visit model page and accept license |
| `CUDA out of memory` | Use smaller model (`-2B`) or reduce resolution |
| `Connection timeout` | Check API key validity and network connection |
| `Module not found: diffusers` | `pip install diffusers transformers` |

**More help:**
- [Configuration & Secrets Guide](docs/configuration_and_secrets.md)
- [Adapters README](ministudio/adapters/README.md)
- [ROADMAP](ROADMAP.md)
- [CONTRIBUTING](CONTRIBUTING.md)

---

## 📚 Documentation Map

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Overview & quick start |
| [docs/configuration_and_secrets.md](docs/configuration_and_secrets.md) | Deep dive: config, secrets, providers |
| [ministudio/adapters/README.md](ministudio/adapters/README.md) | Adapter usage guide |
| [.env.example](.env.example) | All environment variables |
| [ROADMAP.md](ROADMAP.md) | Future features & phases |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

---

## 🚦 Decision Tree: Which Provider?

```
Start: Need to generate videos?

┌─ Local dev & experimentation?
│  └─ ✅ LocalModelAdapter (free, private)
│
├─ Need fast setup?
│  └─ ✅ HuggingFaceAdapter (5 min)
│
├─ Production & high quality?
│  └─ ✅ VertexAIAdapter (Veo 3.1, high-fidelity)
│
└─ Custom endpoint or provider?
   └─ ✅ Implement BaseVideoProvider + create adapter
```

---

## 💡 Pro Tips

### 1. Use Model Aliases
```python
# Instead of full HF name
provider = HuggingFaceAdapter.create("text-to-video-fast")

# Or with default
provider = HuggingFaceAdapter.create()
```

### 2. Cost Estimation
```python
provider = VertexAIAdapter.create()
cost = provider.estimate_cost(duration_seconds=10)
print(f"Estimated cost: ${cost}")  # $0.10 for 10 seconds
```

### 3. Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now see detailed provider info
provider = VertexAIAdapter.create()
```

### 4. Fallback Chain
```python
# Automatic fallback to local if cloud fails
providers = [
    VertexAIAdapter.create(),
    LocalModelAdapter.create(),
]
```

---

## 📞 Getting Help

1. **GitHub Issues**: Report bugs at `github.com/hersi/ministudio/issues`
2. **Discussions**: Ask questions at `github.com/hersi/ministudio/discussions`
3. **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Happy generating! 🎬**
