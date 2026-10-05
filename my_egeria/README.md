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

## Running the apps
This package contains two Textual apps:

- **My Profile** (`DemoCode/My_Profile/`) — the actively developed app, and the one
  the Egeria-Workspaces portal serves:
  ```bash
  uv run my_profile            # or: python -m my_egeria.DemoCode.My_Profile.my_profile_app
  ```
- **MyEgeria** — the original glossary/collection browser (not under active
  development; several of its secondary screens are incomplete):
  ```bash
  uv run my-egeria             # or: python -m my_egeria.main
  ```

Both run in a terminal with the defaults below; set `EGERIA_USER` /
`EGERIA_USER_PASSWORD` to sign in as someone else (e.g. `peterprofile`, who has a
populated profile on the quickstart). For browser mode, see
`serve_my_profile` / `serve_my_egeria` in `EGERIA_WORKSPACES_INTEGRATION.md`.
Use Python 3.13 — Textual fails on Python 3.14.

## Configuration
The app uses the following environment variables (with defaults):
- `EGERIA_PLATFORM_URL`: URL of the Egeria platform (default: `https://localhost:9443`)
- `EGERIA_VIEW_SERVER`: Name of the view server (default: `qs-view-server`)
- `EGERIA_USER`: Egeria user (default: `erinoverview`)
- `EGERIA_USER_PASSWORD`: Egeria password (default: `secret`)
