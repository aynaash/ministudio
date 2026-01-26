# Migration Guide: New Configuration & Multi-Provider System

**For existing users and contributors migrating to the new secrets, config, and adapter system.**

---

## What Changed?

### ✅ NEW: Adapters System
The easiest way to get started with any provider:

```python
# OLD: Required manual provider setup
from ministudio.providers.vertex_ai import VertexAIProvider
provider = VertexAIProvider(project_id="...", ...)

# NEW: Just one import and one line
from ministudio.adapters import VertexAIAdapter
provider = VertexAIAdapter.create(project_id="my-project")
```

### ✅ NEW: Comprehensive Configuration Guide
See [docs/configuration_and_secrets.md](docs/configuration_and_secrets.md) for:
- All 7 secrets management options
- Provider integration patterns
- Multi-provider fallbacks
- Cost estimation
- Production deployment

### ✅ NEW: `.env.example` Template
50+ environment variables pre-documented:
```bash
cp .env.example .env
# Edit with your credentials
```

### ✅ NEW: Quick Reference Card
See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for one-page cheat sheet.

### ✅ UPDATED: README & ROADMAP
- README now links to configuration guide
- Provider support table
- ROADMAP includes "Phase 0: Configuration & Secrets"

---

## Migration Path

### If You're a User

**Step 1: Update to Latest Code**
```bash
git pull origin main
pip install -e .
```

**Step 2: Create `.env` from Template**
```bash
cp .env.example .env
# Edit .env with your existing credentials
```

**Step 3: Update Your Scripts**

OLD:
```python
from ministudio.providers.vertex_ai import VertexAIProvider
from ministudio import VideoOrchestrator

provider = VertexAIProvider(
    api_key=os.getenv("VERTEX_AI_API_KEY"),
    project_id=os.getenv("VERTEX_AI_PROJECT_ID")
)
orchestrator = VideoOrchestrator(provider)
```

NEW:
```python
from ministudio.adapters import VertexAIAdapter
from ministudio import VideoOrchestrator

provider = VertexAIAdapter.create(project_id="my-project")
orchestrator = VideoOrchestrator(provider)
```

**That's it!** Your scripts now support:
- Automatic credential loading from `.env` or Doppler
- Better error messages
- Setup instructions built-in
- Fallback to other providers if needed

---

### If You're a Contributor

#### If You Added a Custom Provider

**Good news:** Your provider still works! But you can now:

1. **Create an adapter** for easier user onboarding:

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
        return """Setup instructions here..."""
```

2. **Update `__init__.py`**:
```python
# ministudio/adapters/__init__.py
from .my_provider_adapter import MyProviderAdapter
__all__ = [..., "MyProviderAdapter"]
```

3. **Users can now use it easily:**
```python
from ministudio.adapters import MyProviderAdapter
provider = MyProviderAdapter.create()
```

#### If You Were Working on Secrets Management

**Check the new system!** We now support:
- ✅ `.env` files
- ✅ Environment variables
- ✅ Doppler
- ✅ GCP Secret Manager
- ✅ AWS Secrets Manager
- ✅ Azure Key Vault

All documented with code examples in [Configuration & Secrets Guide](docs/configuration_and_secrets.md).

---

## Breaking Changes

⚠️ **This is NOT a breaking change for most users.**

The old API still works:
```python
from ministudio.providers.vertex_ai import VertexAIProvider
provider = VertexAIProvider(api_key="...", project_id="...")
```

However, we recommend migrating to adapters for:
- Automatic credential loading
- Better error messages
- Setup instructions
- Consistency across providers

---

## FAQ

### Q: Do I need to change my existing code?
**A:** No, but we recommend it. The new adapter system is:
- Simpler (fewer lines of code)
- More robust (automatic credential loading)
- More discoverable (adapters have help text)

### Q: What if I use a custom credential system?
**A:** Still works! You can:
1. Keep using `BaseVideoProvider` directly
2. Or create a custom adapter that loads from your system

### Q: Can I use both old and new APIs?
**A:** Yes! They coexist. Mix and match as needed:
```python
from ministudio.adapters import VertexAIAdapter
from ministudio.providers.local import LocalVideoProvider

provider1 = VertexAIAdapter.create()  # New style
provider2 = LocalVideoProvider(model_path="/models/...")  # Old style
```

### Q: How do I add a new provider?
**A:** Two options:

**Option 1: Simple (Recommended)**
- Inherit from `BaseVideoProvider`
- Create an adapter (2-3 min)
- Users can use it immediately

**Option 2: Advanced**
- Implement full integration with all bells & whistles
- See [Configuration & Secrets Guide](docs/configuration_and_secrets.md#developer--contributor-tips)

### Q: What about my existing Doppler setup?
**A:** Still works perfectly! Run as before:
```bash
doppler run -- python examples/contextbytes_brand_story.py
```

Adapters automatically read from environment variables set by Doppler.

### Q: Do I need to update my CI/CD?
**A:** No changes needed! If you:
- **Use `.env`**: Just copy `[name].env` to `.env` in your CI runner
- **Use Doppler**: No changes—same command
- **Use secrets**: Adapters read environment variables automatically

---

## Common Migration Scenarios

### Scenario 1: User with `.env` File

**Before:**
```python
import os
os.getenv("VERTEX_AI_API_KEY")  # Manual
```

**After:**
```python
provider = VertexAIAdapter.create()  # Automatic
```

### Scenario 2: User with Doppler

**Before:**
```bash
doppler run -- python script.py
```

**After:**
```bash
# Same! Adapters work with Doppler automatically
doppler run -- python script.py
```

### Scenario 3: Contributor Adding Sora Support

**New approach** (recommended):
```python
# ministudio/adapters/sora_adapter.py
class SoraAdapter:
    @staticmethod
    def create(api_key=None, **kwargs):
        if not api_key:
            api_key = os.getenv("SORA_API_KEY")
        return SoraProvider(api_key=api_key, **kwargs)
    
    @staticmethod
    def get_setup_instructions():
        return "Follow steps at https://..."

# ministudio/adapters/__init__.py
from .sora_adapter import SoraAdapter
__all__ = [..., "SoraAdapter"]

# Users now use it:
from ministudio.adapters import SoraAdapter
provider = SoraAdapter.create()
```

### Scenario 4: Adding to Existing Project

**Before (complex):**
```python
import os
from ministudio.providers.huggingface import HuggingFaceVideoProvider

hf_token = os.getenv("HF_API_TOKEN")
if not hf_token:
    raise ValueError("HF_API_TOKEN not set")

provider = HuggingFaceVideoProvider(
    model_name="damo-vilab/text-to-video-ms-1.7b",
    token=hf_token
)
```

**After (simple):**
```python
from ministudio.adapters import HuggingFaceAdapter

provider = HuggingFaceAdapter.create("text-to-video")
```

---

## Backwards Compatibility

✅ **100% backwards compatible!**

All existing code continues to work:
```python
# Still works
from ministudio.providers.vertex_ai import VertexAIProvider
from ministudio.providers.local import LocalVideoProvider
from ministudio.providers.mock import MockVideoProvider

provider = VertexAIProvider(project_id="...", ...)
orchestrator = VideoOrchestrator(provider)
```

New adapter system is **optional** but **recommended**.

---

## Update Checklist

- [ ] Pull latest code: `git pull origin main`
- [ ] Install dependencies: `pip install -e .`
- [ ] Copy config: `cp .env.example .env`
- [ ] Update credentials in `.env` (if using local dev)
- [ ] Update your scripts to use adapters (optional, but recommended)
- [ ] Run tests: `pytest tests/`
- [ ] Update documentation/README in your project (if applicable)

---

## Getting Help

If you run into issues during migration:

1. **Check [docs/configuration_and_secrets.md](docs/configuration_and_secrets.md)** for detailed setup
2. **Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md)** for common patterns
3. **Check [ministudio/adapters/README.md](ministudio/adapters/README.md)** for adapter details
4. **Open an issue** on GitHub with error message + your setup

---

## Summary

| Aspect | Old | New |
|--------|-----|-----|
| **Setup Complexity** | Medium | Simple (adapters) |
| **Credential Loading** | Manual | Automatic |
| **Provider Support** | 2-3 built-in | 4+ built-in + extensible |
| **Documentation** | Basic | Comprehensive |
| **Contributor Onboarding** | Moderate | Easy (templates) |
| **Backwards Compatible** | N/A | ✅ 100% |

---

**Ready to upgrade? Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md)** 🚀

