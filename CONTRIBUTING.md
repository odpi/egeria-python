<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->


# Contributing to pyegeria

First off, thank you for considering contributing to pyegeria! It's people like you that make Egeria a great tool for the metadata community.

## Development Setup

We use `uv` for dependency management. To set up your environment:

1. Clone the repository.
2. Install dependencies: `uv sync`.
3. Activate the environment: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).

## Project Structure

- `pyegeria/core`: Foundation clients and base classes.
- `pyegeria/omvs`: Individual View Service implementations.
- `pyegeria/models`: Pydantic models for Egeria API requests/responses.
- `pyegeria/view`: Formatting logic (Markdown, Rich, Mermaid).
- `commands/`: CLI tools and scripts.

## Coding Standards

### Sync and Async
Every new OMVS method should provide both an `async` version (prefixed with `_async_`) and a synchronous wrapper. This ensures compatibility with both high-performance applications and interactive Jupyter notebooks.

### Docstrings
We use the NumPy/SciPy docstring format. Ensure every public method has clear parameter descriptions and a "Notes" section with a sample JSON body where applicable.

## Testing

We use `pytest`. We prioritize **Scenario Tests** that demonstrate full lifecycles (Create -> Link -> Detach -> Delete).

To run tests:
`pytest tests/`

To run against a live Egeria instance:
`pytest --live-egeria` (Requires environment variables for credentials).

## Pull Request Process

1. Create a feature branch.
2. Ensure scenario tests pass for your new module.
3. Update the `EgeriaTech` client if adding a new OMVS.
4. Submit your PR for review.