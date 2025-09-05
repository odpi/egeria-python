<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

![Egeria Logo](https://egeria-project.org/assets/images/egeria-header.png)

[![GitHub](https://img.shields.io/github/license/odpi/egeria)](LICENSE)


# pyegeria: a python client for Egeria

This is a package for easily using the Egeria
open metadata environment from python. Details about the
open source Egeria project can be found at [Egeria Project](https://egeria-project.org).

This package is in active development. There is initial
support for many of Egeria's services including configuration and operation.  This client depends on 
This release supports Egeria 5.1 - although most of the functions may work on earlier versions of Egeria as well. 

The code is organized to mimic the existing Egeria Java Client structure.

The commands folder holds the Egeria Command Line Interface and corresponding commands
to visualize and use Egeria. The commands also serve as useful examples.

An examples folder holds some useful examples showing different facets of using pyegeria.

WARNING: files that start with "X" are in-progress placeholders that are not meant to be used..they will mature and 
evolve.

All feedback is welcome. Please engage via our [community](http://egeria-project.org/guides/community/), 
team calls, or via github issues in this repo. If interested in contributing,
you can engage via the community or directly reach out to
[dan.wolfson\@pdr-associates.com](mailto:dan.wolfson@pdr-associates.com?subject=pyegeria).

This is a learning experience.

## Configuration

pyegeria uses a simple, predictable precedence for configuration:

1. Built-in defaults (Pydantic models in pyegeria.config)
2. Config file (JSON) if found
3. Environment variables (OS env and optional .env)
4. Explicit env file passed to get_app_config/load_app_config

Environment always overrides config file, which overrides defaults.

### Where to put your configuration

- Config file: A JSON file named config.json. The loader looks in this order:
  - If PYEGERIA_CONFIG_DIRECTORY is set: $PYEGERIA_CONFIG_DIRECTORY/$PYEGERIA_CONFIG_FILE
  - Else if PYEGERIA_ROOT_PATH is set: $PYEGERIA_ROOT_PATH/$PYEGERIA_CONFIG_FILE
  - Else: ./config.json (the current working directory)

- .env file: Optional. If present in the current working directory (.env), variables from it will be loaded. You can also pass a specific env file path to get_app_config(env_file=...) or load_app_config(env_file=...). For sample variables, see config/env in this repo.

### Common environment variables

- PYEGERIA_CONFIG_DIRECTORY: directory containing your config.json
- PYEGERIA_ROOT_PATH: root folder used to resolve config.json when CONFIG_DIRECTORY is not set
- PYEGERIA_CONFIG_FILE: filename of the configuration JSON (default: config.json)
- PYEGERIA_CONSOLE_WIDTH: integer console width (e.g., 200 or 280)
- EGERIA_PLATFORM_URL, EGERIA_VIEW_SERVER_URL, EGERIA_ENGINE_HOST_URL: URLs for your Egeria servers
- EGERIA_USER, EGERIA_USER_PASSWORD: credentials used by some clients
- Logging related: PYEGERIA_ENABLE_LOGGING, PYEGERIA_LOG_DIRECTORY, PYEGERIA_CONSOLE_LOG_LVL, PYEGERIA_FILE_LOG_LVL, etc.

See config/env for more variables and defaults.

### Example .env

# PYEGERIA_CONFIG_DIRECTORY=/path/to/configs
# PYEGERIA_ROOT_PATH=/path/to/project
# PYEGERIA_CONFIG_FILE=config.json
# EGERIA_PLATFORM_URL=https://localhost:9443
# EGERIA_VIEW_SERVER=qs-view-server
# EGERIA_VIEW_SERVER_URL=https://localhost:9443
# EGERIA_USER=myuser
# EGERIA_USER_PASSWORD=mypassword
# PYEGERIA_CONSOLE_WIDTH=280

Lines starting with # are comments. Quotes are optional; python-dotenv/pydantic-settings handle both.

### Example config.json (minimal)

{
  "Environment": {
    "Pyegeria Root": ".",
    "Egeria Platform URL": "https://localhost:9443"
  },
  "User Profile": {
    "Egeria Home Collection": "MyHome"
  }
}

### Programmatic usage

from pyegeria import get_app_config
cfg = get_app_config()  # uses OS env and ./.env
# or with explicit env file
cfg = get_app_config(env_file="/path/to/dev.env")

# Access values via Pydantic models
print(cfg.Environment.egeria_platform_url)
print(cfg.Logging.enable_logging)

### CLI quick checks

- Validate your env file:
  python scripts/validate_env.py --env config/env
  python scripts/validate_env.py               # auto-detects ./config/env or ./.env

- Run tests (requires Poetry):
  poetry install
  poetry run pytest -v

### Troubleshooting

- If your env doesn’t seem to apply, confirm which config.json is used (the loader checks PYEGERIA_CONFIG_DIRECTORY first, then PYEGERIA_ROOT_PATH, then ./config.json).
- .env files are optional. Missing .env is not an error.
- You can always override values with OS environment variables (they take precedence over config.json).



----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.