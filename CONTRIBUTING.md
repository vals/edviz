# Contributing to edviz

Thank you for your interest in contributing to edviz! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/vals/edviz.git
cd edviz
```

2. Create a virtual environment and install development dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

3. Run tests to ensure everything is working:
```bash
pytest
```

## Development Workflow

1. Create a new branch for your feature or bugfix:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes following the code style guidelines below

3. Add or update tests as needed

4. Run the test suite:
```bash
pytest
```

5. Check code formatting and linting:
```bash
black edviz tests
flake8 edviz tests --max-line-length=100 --extend-ignore=E203,W503
mypy edviz --ignore-missing-imports
```

6. Commit your changes with a descriptive commit message:
```bash
git commit -m "Add feature: description of what you added"
```

7. Push to your fork and create a pull request

## Code Style

- Follow PEP 8 style guidelines
- Use `black` for code formatting (line length: 88)
- Use type hints for function signatures
- Write docstrings for public APIs using Google style
- Keep functions focused and modular

## Testing

- Write tests for all new features and bug fixes
- Aim for high test coverage (current: >95%)
- Use pytest for testing
- Place tests in the `tests/` directory mirroring the source structure

Example test structure:
```python
def test_feature_name():
    """Test description."""
    # Arrange
    design = ExperimentalDesign()

    # Act
    result = design.some_method()

    # Assert
    assert result == expected_value
```

## Documentation

- Update README.md if adding user-facing features
- Update GRAMMAR.md if modifying grammar syntax
- Update KNOWN_ISSUES.md if discovering or fixing limitations
- Add docstrings to new functions and classes
- Include examples in docstrings where helpful

## Pull Request Guidelines

- Provide a clear description of the changes
- Reference any related issues
- Include test coverage for new code
- Ensure all CI checks pass
- Update documentation as needed
- Keep pull requests focused (one feature/fix per PR)

## Reporting Issues

When reporting bugs, please include:
- Python version
- edviz version
- Minimal reproducible example
- Expected vs. actual behavior
- Full error traceback if applicable

## Areas for Contribution

We welcome contributions in these areas:
- Bug fixes
- Performance improvements
- Documentation improvements
- Additional export formats
- Grammar enhancements
- Visualization improvements
- Test coverage improvements

## Parser and Grammar

If contributing to the parser or grammar:
- Read GRAMMAR.md for formal specification
- Understand the precedence rules
- Add worked examples to documentation
- Update EBNF grammar if changing syntax
- Consider backward compatibility

## Visualizer

If contributing to the ASCII visualizer:
- Test with multiple design patterns
- Ensure alignment is correct
- Verify layer ordering
- Check edge cases (very wide/narrow designs)
- Document new visual features

## Questions?

Feel free to open an issue for questions about contributing. We're happy to help!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
