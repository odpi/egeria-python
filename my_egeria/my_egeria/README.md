<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# my_egeria/my_egeria

The `my-egeria` Textual TUI application's package root — see the parent
`my_egeria/README.md` for install/run/configuration instructions.

| Folder/file | Role |
|---|---|
| `main.py` | Entry point (`uv run my-egeria` / `python -m my_egeria.main`). |
| `my_egeria_app.py` | The main Textual `App` class. |
| `screens/` | Textual screens, one per feature area (`GovernanceOfficer`, `ProductManager`, `ProjectManager`, `collections`, `glossary`, `platform`). |
| `widgets/` | Reusable Textual widgets shared across screens. |
| `services/`, `con_services/` | Backend service layer wrapping pyegeria SDK calls for the screens/widgets to use. |
| `utils/` | Shared helpers. |
| `styles/` | Textual CSS. |
| `tests/` | Tests for this app. |
| `error_popup_app.py`, `startup_check.py` | Startup/error-handling helpers. |
| `serve.py` | Browser-mode serving (`textual serve`) — see `serve_my_egeria`/`serve_my_profile` entry points in the root `pyproject.toml`. |
| `DemoCode/` | Standalone demo scripts and experimental/deprecated code, not part of the main app (own subfolders per demo topic — Data Products, Journals, My Profile, Report Specs, Technology Type, plus `Deprecated/` and `Experimental Code/`). |

`DemoCode/` is a scratch/demo area, not maintained to the same standard as
the rest of the app — treat anything there as illustrative, not
production code.
