# MyEgeria

A Textual-based TUI application for Egeria, integrated into the `egeria-python` repository as a `uv` workspace member.

## Features
- Glossary browser and search
- Collection management (view, add, delete)
- Governance officer utilities
- Product manager browser

## Installation
If you have `uv` installed, you can sync the workspace from the root:
```bash
uv sync
```

## Running the app
You can run the app using:
```bash
uv run my-egeria
```
or
```bash
python -m my_egeria.main
```

## Configuration
The app uses the following environment variables (with defaults):
- `EGERIA_PLATFORM_URL`: URL of the Egeria platform (default: `https://localhost:9443`)
- `EGERIA_VIEW_SERVER`: Name of the view server (default: `qs-view-server`)
- `EGERIA_USER`: Egeria user (default: `erinoverview`)
- `EGERIA_USER_PASSWORD`: Egeria password (default: `secret`)
