# Contributing to Daniel LightRAG MCP Server

Thank you for your interest in contributing to the Daniel LightRAG MCP Server! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/daniel-lightrag-mcp.git
   cd daniel-lightrag-mcp
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Making Changes

1. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. **Make your changes** following the coding standards below

3. **Write or update tests** for your changes

4. **Run the test suite** to ensure everything works:
   ```bash
   pytest
   ```

5. **Run code formatting**:
   ```bash
   black src/ tests/
   isort src/ tests/
   ```

6. **Run type checking**:
   ```bash
   mypy src/
   ```

### Coding Standards

- **Code Style**: We use Black for code formatting and isort for import sorting
- **Type Hints**: All public functions should have type hints
- **Documentation**: All public functions and classes should have docstrings
- **Testing**: New features should include comprehensive tests
- **Error Handling**: Use the existing error hierarchy and provide meaningful error messages

### Testing

- **Unit Tests**: Test individual functions and methods in isolation
- **Integration Tests**: Test complete workflows and tool interactions
- **Model Tests**: Test Pydantic model validation and serialization
- **Coverage**: Aim for >95% test coverage for new code

Run tests with:
```bash
# All tests
pytest

# Specific test file
pytest tests/test_server.py

# With coverage
pytest --cov=src/daniel_lightrag_mcp --cov-report=html
```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:
- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Error messages** and stack traces if applicable

### Feature Requests

For new features, please:
- **Describe the use case** and why it's needed
- **Provide examples** of how it would be used
- **Consider backwards compatibility**
- **Discuss implementation approach** if you have ideas

### Code Contributions

#### Adding New Tools

If you want to add a new MCP tool:

1. **Add the tool definition** in `server.py`:
   - Add to the `handle_list_tools()` function
   - Add handling in `handle_call_tool()`
   - Include proper input schema validation

2. **Add client method** in `client.py`:
   - Implement the API call method
   - Add proper error handling
   - Include type hints and docstring

3. **Add models** in `models.py` if needed:
   - Request and response models
   - Proper validation rules

4. **Write comprehensive tests**:
   - Unit tests for the tool
   - Client method tests
   - Model validation tests
   - Integration tests

5. **Update documentation**:
   - Add tool to README.md
   - Add usage examples
   - Update CONFIGURATION_GUIDE.md

#### Improving Existing Features

- **Maintain backwards compatibility** unless it's a breaking change
- **Update tests** to cover your changes
- **Update documentation** if behavior changes
- **Consider performance implications**

## Pull Request Process

1. **Ensure your branch is up to date** with main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch
   git rebase main
   ```

2. **Run the full test suite** and ensure it passes

3. **Update documentation** if needed

4. **Create a pull request** with:
   - **Clear title** describing the change
   - **Detailed description** of what was changed and why
   - **Reference any related issues**
   - **Include testing information**

5. **Respond to review feedback** promptly

### Pull Request Guidelines

- **One feature per PR**: Keep pull requests focused on a single feature or fix
- **Clear commit messages**: Use descriptive commit messages
- **Small, focused commits**: Break large changes into logical commits
- **Update CHANGELOG.md**: Add your changes to the unreleased section

## Code Review Process

- All pull requests require review before merging
- Reviews focus on:
  - Code quality and style
  - Test coverage
  - Documentation completeness
  - Backwards compatibility
  - Performance implications

## Release Process

Releases follow semantic versioning:
- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features, backwards compatible
- **Patch** (0.0.X): Bug fixes, backwards compatible

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Ask questions in pull request comments

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- CHANGELOG.md for significant contributions
- README.md acknowledgments section (if added)

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Daniel LightRAG MCP Server!