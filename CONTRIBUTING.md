# Contributing to Home Data Lab

Thank you for your interest in contributing to the Home Data Lab project! This document provides guidelines for contributing.

## Code of Conduct

Be respectful and inclusive. We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (Raspberry Pi model, OS version, k3s version)
- Logs if available

### Suggesting Enhancements

We welcome suggestions for new features or improvements:
- Open an issue with the "enhancement" label
- Describe the enhancement and its use case
- Explain how it would benefit users

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Submit a pull request** with a clear description

## Development Setup

### Prerequisites

- Raspberry Pi 4B (for testing k3s setup)
- Python 3.9+
- Docker (for building container images)
- kubectl
- Ansible

### Local Development

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/home-data-lab.git
cd home-data-lab

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd data-scrapers
pip install -r requirements.txt

# Run tests
python -m pytest
```

## Coding Standards

### Python Code

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular
- Handle errors gracefully with try-except blocks
- Add logging for debugging

Example:
```python
def scrape_data(country_code: str, start: pd.Timestamp, end: pd.Timestamp) -> Optional[pd.DataFrame]:
    """
    Scrape electricity data for a given country and time period.
    
    Args:
        country_code: Two-letter country code (e.g., 'DE', 'FR')
        start: Start timestamp
        end: End timestamp
        
    Returns:
        DataFrame with scraped data or None if error
    """
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"Error scraping data: {e}")
        return None
```

### Shell Scripts

- Use `set -e` to exit on error
- Add comments for complex operations
- Provide informative output messages
- Use color coding for better UX

### YAML Files

- Use 2 spaces for indentation
- Add comments to explain non-obvious configurations
- Validate YAML syntax before committing

### Documentation

- Keep documentation up to date with code changes
- Use clear, concise language
- Include examples where helpful
- Add troubleshooting sections for common issues

## Testing

### Before Submitting

1. **Test Python code**:
   ```bash
   python -m py_compile *.py
   ```

2. **Test Ansible playbooks**:
   ```bash
   ansible-playbook --syntax-check playbook-k3s-setup.yml
   ```

3. **Validate Kubernetes manifests**:
   ```bash
   kubectl apply --dry-run=client -f your-manifest.yaml
   ```

4. **Check for security vulnerabilities**:
   ```bash
   pip install safety
   safety check -r requirements.txt
   ```

### Testing on Raspberry Pi

If you're modifying k3s setup:
- Test on actual Raspberry Pi hardware
- Test both fresh installation and upgrades
- Verify all nodes join the cluster correctly
- Test with different Raspberry Pi OS versions

## Project Structure

```
home-data-lab/
├── ansible/              # Ansible automation
├── data-scrapers/        # Data collection scripts
├── k3s-setup/           # Kubernetes manifests
├── notebooks/           # Jupyter notebooks
└── docs/                # Documentation
```

## Areas for Contribution

We especially welcome contributions in:

### Data Scrapers
- Support for additional data sources
- More sophisticated error handling
- Data validation and quality checks
- Performance optimizations
- Database storage backend

### Analysis Notebooks
- Advanced statistical analysis
- Machine learning models
- Predictive analytics
- Additional visualizations
- Time series forecasting

### Infrastructure
- Monitoring and alerting setup
- Backup and recovery procedures
- High availability configurations
- Security hardening
- Cost optimization

### Documentation
- Video tutorials
- More examples and use cases
- Translations
- Architecture diagrams

## Commit Messages

Use clear and descriptive commit messages:

```
Add support for Italian electricity market data

- Implement IT market scraper
- Add tests for IT data validation
- Update documentation with IT examples
```

Format:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- First line should be 50 characters or less
- Reference issues and pull requests when relevant

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update documentation in the `docs/` folder
3. Add or update tests for your changes
4. Ensure all tests pass
5. The PR will be merged once you have approval from a maintainer

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Home Data Lab! 🎉
