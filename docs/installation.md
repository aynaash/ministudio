# Installation Guide

This guide covers all ways to install and set up Ministudio for development and production use.

## Prerequisites

- Python 3.8 or higher
- Git (for source installation)
- Docker (optional, for containerized deployment)

## Basic Installation

### From PyPI (Recommended)

```bash
# Install core package
pip install ministudio

# Install with specific provider support
pip install ministudio[vertex-ai]    # Google Vertex AI
pip install ministudio[openai]       # OpenAI Sora
pip install ministudio[all]          # All providers
```

### From Source

```bash
# Clone repository
git clone https://github.com/yourusername/ministudio.git
cd ministudio

# Install in development mode
pip install -e .

# Or install with all dependencies
pip install -e .[all]
```

## Provider Setup

### Google Vertex AI

1. Create a Google Cloud Project
2. Enable Vertex AI API
3. Create a service account or use Application Default Credentials
4. Set environment variable:

```bash
export GCP_PROJECT_ID="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### OpenAI Sora

1. Get API key from OpenAI
2. Set environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

### Local Models

For local Stable Video Diffusion or other models:

```python
provider = Ministudio.create_provider(
    "local",
    model_path="/path/to/model",
    device="cuda"  # or "cpu"
)
```

## Development Setup

### Clone and Setup

```bash
git clone https://github.com/yourusername/ministudio.git
cd ministudio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[all]
pip install -r requirements-dev.txt  # If exists
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ministudio

# Run specific test
pytest tests/test_providers.py
```

### Code Quality

```bash
# Format code
black ministudio/

# Lint code
ruff check ministudio/

# Type check
mypy ministudio/
```

## Docker Installation

### Build from Source

```bash
# Clone repository
git clone https://github.com/yourusername/ministudio.git
cd ministudio

# Build Docker image
docker build -t ministudio .

# Run container
docker run -p 8000:8000 ministudio
```

### Using Pre-built Image

```bash
# Pull from registry (when available)
docker pull yourusername/ministudio:latest

# Run with environment variables
docker run -p 8000:8000 \
  -e GCP_PROJECT_ID="your-project" \
  -e OPENAI_API_KEY="your-key" \
  yourusername/ministudio:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  ministudio:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./output:/app/ministudio_output
```

Run with:

```bash
docker-compose up
```

## API Server Setup

### Local Development

```bash
# Run with auto-reload
uvicorn ministudio.api:app --reload

# Run on specific host/port
uvicorn ministudio.api:app --host 0.0.0.0 --port 8000
```

### Production Deployment

Use a production ASGI server:

```bash
# With Gunicorn
gunicorn ministudio.api:app -w 4 -k uvicorn.workers.UvicornWorker

# With Hypercorn
hypercorn ministudio.api:app --bind 0.0.0.0:8000
```

### Systemd Service

Create `/etc/systemd/system/ministudio.service`:

```ini
[Unit]
Description=Ministudio API Server
After=network.target

[Service]
User=ministudio
Group=ministudio
WorkingDirectory=/path/to/ministudio
ExecStart=/path/to/venv/bin/uvicorn ministudio.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable ministudio
sudo systemctl start ministudio
```

## Verification

### CLI Test

```bash
# Test installation
ministudio --help

# Test with mock provider
ministudio --provider mock --concept "test" --action "orb moving"
```

### API Test

```bash
# Start server
uvicorn ministudio.api:app &

# Test endpoint
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"concept": "test", "action": "orb floating"}'
```

### Import Test

```python
# Test Python import
python -c "from ministudio import Ministudio; print('Import successful')"
```

## Troubleshooting

### Common Issues

**Import Error**: Ensure you're in the correct virtual environment and have installed the package.

**Provider Errors**: Check API keys and network connectivity.

**CUDA Errors**: For local models, ensure CUDA is properly installed.

**Port Conflicts**: Change the port if 8000 is in use.

### Environment Variables

Create a `.env` file:

```bash
GCP_PROJECT_ID=your-project
OPENAI_API_KEY=your-key
MINISTUDIO_OUTPUT_DIR=./output
```

Load with:

```bash
pip install python-dotenv
# Then in code: from dotenv import load_dotenv; load_dotenv()
```

## Next Steps

After installation:

1. Read the [Quick Start Guide](quickstart.md)
2. Check out [Examples](examples.md)
3. Learn about [Styles and Templates](styles.md)
4. Set up your preferred [Providers](providers.md)
