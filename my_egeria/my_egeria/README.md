<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# my_egeria/my_egeria

The `my-egeria` Textual TUI application's package root — see the parent
`my_egeria/README.md` for install/run/configuration instructions.

| Folder/file | Role |
|---|---|
| `my_profile.py` | Production My Profile & Catalog TUI Application (`MyProfileApp` / `MyEgeriaApp`, entry point `uv run my_profile` / `python -m my_egeria.my_profile`). |
| `main.py` | Entry point for MyEgeria app (`uv run my-egeria` / `python -m my_egeria.main`). |
| `my_egeria_app.py` | The MyEgeria browser/navigation Textual `App` class. |
| `*Screen.py` / `*Screens.py` | Production Textual screens (Main, Splash, Profile Creation/Edit, Data Shopping, Bookmarks, Network, Teams, Communities, Feedback, Tech Types, Subscriptions). |
| `*_handler.py` | Domain mixins for bookmarks, communities, CRUD operations, feedback, networks, shopping, team roles, and tech types. |
| `profile_utils.py` | Profile formatting, Mermaid graph sanitization, data structures, and connection utilities. |
| `screens/` | Feature screens (`GovernanceOfficer`, `ProductManager`, `ProjectManager`, `collections`, `glossary`, `platform`). |
| `widgets/` | Reusable Textual widgets shared across screens. |
| `services/`, `con_services/` | Backend service layer wrapping pyegeria SDK calls for screens/widgets. |
| `utils/` | Shared helpers and configuration. |
| `styles/` | Textual CSS styles. |
| `tests/` | Tests for the app components. |
| `error_popup_app.py`, `startup_check.py` | Startup/error-handling helpers. |
| `serve.py` | Browser-mode serving via `textual-serve` — provides `serve_my_profile` and `serve_my_egeria`. |
| `RETURN_CODES.md` | Screen callback return code contract reference. |
| `catalog_api_calls.md` | API mapping reference for Egeria catalog calls. |
| `DemoCode/` | Standalone demo scripts and experimental/deprecated code (`Data_Products_Demo`, `Deprecated/`, `Experimental Code/`). |

`DemoCode/` is a scratch/demo area for experimental prototypes — production code lives in `my_egeria/my_egeria/`.
