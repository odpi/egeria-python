# pyegeria Developer Guidelines

## Project Overview
pyegeria is a Python client for Egeria, an open metadata and governance platform. It provides a comprehensive set of tools for interacting with Egeria services, including configuration, operation, and metadata management.

## Project Structure
- **pyegeria/**: Main package
  - **_client.py**: Base client implementation
  - **egeria_*.py**: Client interfaces for different services
  - ***_omvs.py**: Open Metadata View Services clients
  - **commands/**: CLI commands organized by category
    - **cat/**: Catalog-related commands
    - **cli/**: CLI interface commands
    - **my/**: User-specific commands
    - **ops/**: Operations-related commands
    - **tech/**: Technical commands
- **tests/**: Test files mirroring the main package structure
- **examples/**: Example usage and configurations
  - **Jupyter Notebooks/**: Interactive examples
  - **Coco_config/**: Configuration examples
  - **doc_samples/**: Documentation samples

## Tech Stack
- **Python**: 3.12+
- **Dependency Management**: Poetry
- **HTTP Clients**: httpx, requests
- **CLI Tools**: click, trogon, textual
- **Testing**: pytest
- **Documentation**: Jupyter notebooks, Markdown

## Running Tests
Tests are implemented using pytest and follow the same structure as the main package:

```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_specific_module.py

# Run tests with verbose output
poetry run pytest -v
```

## Executing Scripts
The project provides numerous CLI commands for interacting with Egeria:

```bash
# Install the package
poetry install

# Run a command (examples)
poetry run list_assets
poetry run list_terms
poetry run hey_egeria  # Main CLI entry point
```

You can also use the library programmatically:

```python
from pyegeria.egeria_client import EgeriaClient

# Create a client
client = EgeriaClient(platform_url="https://your-egeria-platform:9443")

# Use the client to interact with Egeria
assets = client.catalog.list_assets()
```

## Best Practices
1. **Code Organization**: 
   - Follow the existing structure when adding new modules
   - Place service-specific code in appropriate *_omvs.py files
   - Add CLI commands to the relevant category in commands/

2. **Testing**:
   - Write tests for all new functionality
   - Follow the existing test patterns
   - Ensure tests are independent and don't rely on specific Egeria instances

3. **Documentation**:
   - Document all public APIs with docstrings
   - Include examples in docstrings
   - Add Jupyter notebooks for complex workflows

4. **Development Workflow**:
   - Use Poetry for dependency management
   - Format code with black and isort
   - Validate code with flake8
   - Files prefixed with "X" are in-progress and not ready for use

5. **CLI Commands**:
   - Register new commands in pyproject.toml
   - Follow the existing command structure and naming conventions
   - Provide helpful error messages and documentation