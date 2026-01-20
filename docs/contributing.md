# Contributing to Ministudio

We welcome contributions from the community! This guide explains how to get started with development, submit changes, and follow our processes.

## Ways to Contribute

- **Code**: Fix bugs, add features, improve performance
- **Documentation**: Improve docs, add examples, translate
- **Testing**: Write tests, report bugs, verify fixes
- **Design**: UI/UX improvements, logo, branding
- **Community**: Answer questions, moderate discussions

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment tool (venv, conda, etc.)

### Clone and Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/ministudio.git
cd ministudio

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[all]
pip install -r requirements-dev.txt  # If exists

# Verify setup
python -c "import ministudio; print('Setup successful')"
```

### Code Quality Tools

We use several tools to maintain code quality:

```bash
# Format code
black ministudio/

# Lint code
ruff check ministudio/

# Type check
mypy ministudio/

# Run tests
pytest

# Run with coverage
pytest --cov=ministudio --cov-report=html
```

## Development Workflow

### 1. Choose an Issue

- Check [GitHub Issues](https://github.com/yourusername/ministudio/issues) for open tasks
- Look for "good first issue" or "help wanted" labels
- Comment on the issue to indicate you're working on it

### 2. Create a Branch

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-number-description
```

### 3. Make Changes

- Write clear, focused commits
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run tests
pytest

# Test specific functionality
pytest tests/test_providers.py -v

# Test CLI
ministudio --provider mock --concept "test" --action "orb moving"
```

### 5. Submit a Pull Request

```bash
# Push your branch
git push origin feature/your-feature-name

# Create PR on GitHub
# Fill out the PR template
# Link to related issues
```

## Adding a New Provider

Ministudio supports multiple AI video providers through a plugin architecture.

### 1. Create Provider File

Create `ministudio/providers/your_provider.py`:

```python
from ..providers.base import BaseVideoProvider
from ..core import VideoGenerationRequest, VideoGenerationResult

class YourProvider(BaseVideoProvider):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key=api_key, **kwargs)

    @property
    def name(self) -> str:
        return "your-provider"

    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResult:
        # Implementation here
        # Call your API
        # Return VideoGenerationResult
        pass
```

### 2. Update Factory Method

Add to `ministudio/core.py` in the `create_provider` method:

```python
elif provider_type == "your-provider":
    from .providers.your_provider import YourProvider
    return YourProvider(**provider_kwargs)
```

### 3. Update Documentation

- Add to `docs/providers.md`
- Update installation instructions
- Add to README badges/examples

### 4. Add Tests

Create `tests/test_your_provider.py`:

```python
import pytest
from ministudio import Ministudio

class TestYourProvider:
    def test_generate_video(self):
        # Test implementation
        pass
```

## Writing Documentation

### Documentation Structure

```
docs/
├── index.md           # Main documentation
├── installation.md    # Installation guide
├── quickstart.md      # Getting started
├── api.md            # API reference
├── providers.md      # Provider documentation
├── styles.md         # Styles and templates
├── examples.md       # Usage examples
├── contributing.md   # This file
├── roadmap.md        # Future plans
└── troubleshooting.md # Common issues
```

### Writing Guidelines

- Use Markdown format
- Include code examples
- Keep it concise but comprehensive
- Use relative links between docs
- Test all code examples

### Building Docs Locally

```bash
# Install Jekyll (for local testing)
gem install jekyll bundler

# Serve docs locally
cd docs
jekyll serve

# View at http://localhost:4000
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_core.py

# With verbose output
pytest -v

# With coverage
pytest --cov=ministudio
```

### Writing Tests

- Use `pytest` framework
- Place tests in `tests/` directory
- Name files `test_*.py`
- Use descriptive test names
- Test both success and failure cases

Example test:

```python
import pytest
from ministudio import Ministudio

@pytest.mark.asyncio
async def test_generate_concept_video():
    provider = Ministudio.create_provider("mock")
    studio = Ministudio(provider=provider)

    result = await studio.generate_concept_video(
        concept="test",
        action="orb moving"
    )

    assert result.success is True
    assert result.video_path is not None
```

## Code Style

### Python Style

- Follow PEP 8
- Use type hints
- Write descriptive variable names
- Keep functions focused and small
- Use async/await for I/O operations

### Commit Messages

- Use conventional commits format
- Start with type: feat, fix, docs, style, refactor, test, chore
- Keep first line under 50 characters
- Add detailed description if needed

Examples:
```
feat: add support for OpenAI Sora provider
fix: handle API timeout errors gracefully
docs: update installation guide for Windows
```

### Pull Request Guidelines

- Reference related issues
- Provide clear description of changes
- Include screenshots for UI changes
- Ensure CI passes
- Request review from maintainers

## Community Guidelines

### Communication

- Be respectful and inclusive
- Use clear, concise language
- Provide context for questions
- Help others when possible

### Issue Reporting

When reporting bugs:

1. Use a clear, descriptive title
2. Provide steps to reproduce
3. Include expected vs actual behavior
4. Add system information (OS, Python version)
5. Attach logs or screenshots if relevant

### Feature Requests

For new features:

1. Check if it already exists or is planned
2. Describe the use case clearly
3. Explain why it's valuable
4. Consider implementation complexity

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: For real-time community support
- **Documentation**: Comprehensive guides and API reference

## Recognition

Contributors are recognized in:

- GitHub repository contributors list
- CHANGELOG.md for significant contributions
- Release notes
- Community shoutouts

## License

By contributing to Ministudio, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Ministudio! 🚀
