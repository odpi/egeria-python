### Configuration and Logging Guide for pyegeria Applications

This short tutorial explains how to configure applications that use pyegeria. It covers:

- How configuration is discovered and loaded
- How to initialize logging
- Two practical setups:
  1) Local development in your PyCharm egeria-python project, using `config/config.json`
  2) Egeria Workspaces Jupyter environment, using `config/config_workspaces.json`

#### How configuration is resolved

pyegeria provides helpers in `pyegeria.config` (re-exported in `pyegeria.__init__`) to load settings:

- `load_app_config(env_file: str | None = None)`: loads and caches configuration
- `get_app_config(env_file: str | None = None)`: returns the loaded configuration model
- `settings`: a lazy accessor exposing the grouped sections as attributes (e.g., `settings.Environment`)
- `config_logging(verbose: bool = False)`: initializes logging from the loaded configuration

Load order and precedence (last-wins):
1. Built-in defaults (Pydantic models in `pyegeria/config.py`)
2. JSON config file (pointed to by environment variables)
3. Environment variables (process env and optional `.env` file)

Key environment variables influencing file discovery:

- `PYEGERIA_ROOT_PATH`: base path used by various folders; may also be set inside the JSON under "Pyegeria Root"
- `PYEGERIA_CONFIG_DIRECTORY`: directory that contains your configuration JSON files
- `PYEGERIA_CONFIG_FILE`: the name of the JSON to use (e.g., `config.json` or `config_workspaces.json`)

Tip: You can put these into a `.env` file or export them in your shell. See sample variables in `config/env`.

Once loaded, key values live under sections like `Environment`, `Logging`, `Debug`, and `User Profile`. For example:

- `settings.Environment.egeria_platform_url`
- `settings.Environment.egeria_view_server`
- `settings.Environment.egeria_jupyter`
- `settings.Logging.enable_logging`

#### Initializing configuration and logging (common to both use cases)

```python
from pyegeria import load_app_config, get_app_config, settings, config_logging

# Load the configuration (reads env vars and JSON); do this once near program start
load_app_config()

# Access structured config models
app_config = settings.Environment  # or get_app_config().Environment

# Initialize logging based on config.Logging
config_logging()

print("Platform:", app_config.egeria_platform_url)
print("View Server:", app_config.egeria_view_server)
```

If you need to choose a specific `.env` file at runtime:

```python
from pyegeria import load_app_config

load_app_config(env_file="/path/to/.env")
```

---

### Use case 1: Local development in PyCharm (egeria-python project)

Typical setup uses `config/config.json` under this repository's `config` folder. That file contains environment and logging defaults suited to local development.

Steps:
1. Ensure `PYEGERIA_CONFIG_DIRECTORY` points to this repo's `config` folder, and `PYEGERIA_CONFIG_FILE` is `config.json`.
   - You can export these in your shell, add them to `.env`, or configure them in your PyCharm Run/Debug configuration.
2. Optionally set `PYEGERIA_ROOT_PATH` to the root folder for your in/out boxes (many examples use `sample-data`).
3. Start your application; call `load_app_config()` early; then call `config_logging()`.

Example shell exports for macOS/Linux:

```bash
export PYEGERIA_CONFIG_DIRECTORY="/Users/<you>/localGit/egeria-python/config"
export PYEGERIA_CONFIG_FILE="config.json"
export PYEGERIA_ROOT_PATH="/Users/<you>/localGit/egeria-python/sample-data"
```

Or create a `.env` file in your project root with the same variables.

Minimal application snippet:

```python
from pyegeria import load_app_config, settings, config_logging, SolutionArchitect

def main():
    load_app_config()      # reads config/config.json via the env variables
    config_logging()       # enable file/console logging per Logging section

    env = settings.Environment
    client = SolutionArchitect(
        server_name=env.egeria_view_server,
        platform_url=env.egeria_platform_url,
        user="erinoverview",            # or from env vars
        user_password="secret",         # or from env vars / secrets
    )
    # Use the client…

if __name__ == "__main__":
    main()
```

Relevant fields in `config/config.json` (examples):
- Environment
  - "Egeria Platform URL": `https://localhost:9443`
  - "Egeria View Server": `qs-view-server2`
  - "Egeria Jupyter": `true` or `false` depending on terminal rendering
  - "Pyegeria Root": base path used for inbox/outbox/mermaid graphs
- Logging
  - `enable_logging`: turn logging on/off
  - `console_logging_level`, `file_logging_level`, `log_directory`, `logging_*_format`

Note on precedence: any exported env var (e.g., `EGERIA_PLATFORM_URL`) will override the value from `config.json`.

---

### Use case 2: Egeria Workspaces Jupyter environment

For applications running inside the Egeria Workspaces JupyterLab, use the `config/config_workspaces.json` profile. It pre-sets URLs to reach the host from within the container and configures paths under `/home/jovyan`.

Steps:
1. Set `PYEGERIA_CONFIG_DIRECTORY` to the repo `config` folder accessible in the workspace and `PYEGERIA_CONFIG_FILE` to `config_workspaces.json`.
2. Ensure `Pyegeria Root` and paths like `Egeria Glossary Path` and `Egeria Mermaid Folder` match your workspace layout (defaults target `/home/jovyan`).
3. In notebooks or scripts, call `load_app_config()` in the first cell, then `config_logging()`.

Example in a notebook cell:

```python
from pyegeria import load_app_config, settings, config_logging

# If needed, set env vars programmatically before loading
import os
os.environ["PYEGERIA_CONFIG_DIRECTORY"] = "/home/jovyan/work/egeria-python/config"
os.environ["PYEGERIA_CONFIG_FILE"] = "config_workspaces.json"

load_app_config()
config_logging()

env = settings.Environment
print(env.egeria_platform_url)  # expected: https://host.docker.internal:9443
```

Config highlights from `config_workspaces.json`:
- Environment
  - "Egeria Platform URL": `https://host.docker.internal:9443`
  - "Egeria View Server": `qs-view-server`
  - "Egeria Jupyter": `true` (improves console rendering in notebooks)
  - Paths under `/home/jovyan`, e.g., `Egeria Mermaid Folder`: `/home/jovyan/work/mermaid_graphs`
- Logging
  - `enable_logging`: `true`
  - `log_directory`: `./logs` (relative to notebook working directory)
  - Console/file formats tuned for Jupyter readability

---

### Environment variables reference (selected)

You can override many values via environment variables; `config/env` contains commented examples. Common ones:

- Config discovery
  - `PYEGERIA_CONFIG_DIRECTORY`
  - `PYEGERIA_CONFIG_FILE`
  - `PYEGERIA_ROOT_PATH`
- Egeria endpoints
  - `EGERIA_PLATFORM_URL`, `EGERIA_VIEW_SERVER`, `EGERIA_INTEGRATION_DAEMON_URL`, etc.
- Jupyter rendering toggle
  - `EGERIA_JUPYTER` (`True`/`False`)
- Logging
  - `PYEGERIA_ENABLE_LOGGING`, `PYEGERIA_LOG_DIRECTORY`, `PYEGERIA_CONSOLE_LOG_LVL`, `PYEGERIA_FILE_LOG_LVL`, `PYEGERIA_CONSOLE_FILTER_LEVELS`

Values provided via environment variables take precedence over JSON and defaults.

---

### Troubleshooting tips

- Call `from pyegeria.config import pretty_print_config; pretty_print_config(safe=True)` to print the effective configuration (safely masks secrets) to the console.
- If logging isn’t writing files, verify `Logging.enable_logging` is `true` and `Logging.log_directory` exists and is writable in your environment.
- In Jupyter, ensure `Egeria Jupyter` is `true` to improve table/pager rendering in rich outputs.

---

### Quick checklist

- Set `PYEGERIA_CONFIG_DIRECTORY` and `PYEGERIA_CONFIG_FILE` to select the right JSON profile
- Call `load_app_config()` once at startup
- Initialize logging with `config_logging()`
- Use `settings.Environment.*` in your code for URLs, folders, and flags
