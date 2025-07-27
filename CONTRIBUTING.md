# Contributing to Paper Search Interface

Thank you for your interest in contributing to the Paper Search Interface! This document provides guidelines and information for contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Development Setup

1. **Install development dependencies** (if any are added in the future)
2. **Run the application** to ensure everything works:
   ```bash
   python run.py
   ```
3. **Run the demo** to test functionality:
   ```bash
   python demo.py
   ```

## Making Changes

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Testing
- Test your changes thoroughly
- Ensure the web interface works correctly
- Test with different search combinations
- Verify that the demo script runs without errors

### Adding New Features

#### Adding New Conferences
1. Place JSON files in the appropriate conference folder
2. Update the `get_subfield()` function in `tools/combine_papers.py` if needed
3. Regenerate the CSV: `python tools/combine_papers.py`
4. Test the new data appears correctly

#### Adding New Search Features
1. Update the `filter_papers()` function in `tools/web_interface.py`
2. Add corresponding UI elements in `tools/templates/index.html`
3. Update the JavaScript functions as needed
4. Test the new functionality

#### Adding New Subfields
1. Update the `get_subfield()` function in `tools/combine_papers.py`
2. Regenerate the CSV data
3. Test that venues are correctly categorized

### File Structure
```
paper-search-interface/
├── tools/
│   ├── web_interface.py          # Main Flask application
│   ├── combine_papers.py         # Data processing
│   ├── templates/
│   │   └── index.html           # Web interface
│   └── requirements.txt         # Dependencies
├── run.py                       # Quick start script
├── demo.py                      # Demo script
├── setup.py                     # Package setup
├── requirements.txt             # Root dependencies
├── README.md                    # Main documentation
└── CONTRIBUTING.md              # This file
```

## Submitting Changes

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a pull request** on GitHub

### Pull Request Guidelines

- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Screenshots** for UI changes (if applicable)
- **Test results** showing the changes work correctly
- **Reference any issues** that the PR addresses

## Issue Reporting

When reporting issues, please include:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **System information** (OS, Python version, etc.)
- **Error messages** (if any)

## Code of Conduct

- Be respectful and inclusive
- Help others learn and contribute
- Provide constructive feedback
- Focus on the code and its functionality

## Questions?

If you have questions about contributing, feel free to:
- Open an issue on GitHub
- Ask in the discussions section
- Contact the maintainers directly

Thank you for contributing to making this tool better for the research community! 