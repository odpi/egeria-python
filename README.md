<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

![Egeria Logo](https://egeria-project.org/assets/images/egeria-header.png)

[![GitHub](https://img.shields.io/github/license/odpi/egeria)](LICENSE)


# pyegeria: a python client for Egeria

A lightweight Python 3.12+ client and CLI for the Egeria open metadata and governance platform. It helps you configure and operate Egeria services and work with metadata (assets, glossaries, lineage, etc.) from Python, with examples, tests, and documented report formats.

This is a package for easily using the Egeria
open metadata environment from python. Details about the
open source Egeria project can be found at [Egeria Project](https://egeria-project.org).

This package is in active development. There is initial
support for many of Egeria's services including configuration and operation.  This client depends on 
This release supports Egeria 6.0 - although most of the functions may work on earlier versions of Egeria as well. 

The code is organized to mimic the existing Egeria Java Client structure.

The commands folder holds the Egeria Command Line Interface and corresponding commands
to visualize and use Egeria. The commands also serve as useful examples.

An examples folder holds some useful examples showing different facets of using pyegeria.

## Documentation

For detailed information on using pyegeria, see:
- [docs/user_programming.md](docs/user_programming.md): A comprehensive guide to the programming model, configuration, and client usage.
- [docs/output-formats-and-report-specs.md](docs/output-formats-and-report-specs.md): Guidance on output formats and report specs (including nested/master–detail).

### Report specs: families and filtering

Report specs (aka format sets) can be tagged with an optional `family` string to help organize and discover related specs.

- Show names with family and sort by family, then name:

```python
from pyegeria.view.base_report_formats import report_spec_list

names = report_spec_list(show_family=True, sort_by_family=True)
for n in names:
  print(n)
```

- Filter specs by family programmatically:

```python
from pyegeria.view.base_report_formats import report_specs

# Exact family match (case-insensitive)
security_specs = report_specs.filter_by_family("Security")
# Specs with no family assigned
no_family_specs = report_specs.filter_by_family("")
```

WARNING: files that start with "X" are in-progress placeholders that are not meant to be used..they will mature and 
evolve.

All feedback is welcome. Please engage via our [community](http://egeria-project.org/guides/community/), 
team calls, or via github issues in this repo. If interested in contributing,
you can engage via the community or directly reach out to
[dan.wolfson\@pdr-associates.com](mailto:dan.wolfson@pdr-associates.com?subject=pyegeria).

This is a learning experience.

## Configuration

pyegeria uses a centralized configuration system powered by Pydantic. Clients (like `EgeriaTech` or `EgeriaCat`) automatically pick up these settings if parameters are omitted during initialization.

Precedence for configuration:
1. Explicitly passed parameters to client constructors
2. Environment variables (OS env and optional .env)
3. Config file (JSON) if found
4. Built-in defaults

For more details on setting up your configuration and available variables, see [docs/user_programming.md](docs/user_programming.md).

**For detailed instructions on setting up authentication credentials on Linux, see [SETUP_LINUX_CREDENTIALS.md](SETUP_LINUX_CREDENTIALS.md)**

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

### Testing

By default, running pytest executes unit tests that use monkeypatching/fakes and do not contact a live Egeria.

- Run unit tests (recommended default):
  poetry install
  poetry run pytest -v

You can also run tests live against a local Egeria instance. Enable live mode with either a CLI flag or an environment variable. In live mode, tests marked as `unit` are skipped and live tests run using a real Client2 connection.

- Enable live mode via CLI:
  poetry run pytest -q --live-egeria

- Or enable via environment variable:
  PYEG_LIVE_EGERIA=1 poetry run pytest -q

Default live connection parameters (can be overridden via env):
- server_name = "qs-view-server"           (override with PYEG_SERVER_NAME)
- platform_url = "https://localhost:9443" (override with PYEG_PLATFORM_URL)
- user_id = "peterprofile"                (override with PYEG_USER_ID)
- user_pwd = "secret"                      (override with PYEG_USER_PWD)

Notes:
- SSL verification is controlled by pyegeria._globals.enable_ssl_check, which defaults to False in this repo to support localhost/self-signed certs.
- See tests/conftest.py for the live test fixtures and switches.

### Troubleshooting

- If your env doesn’t seem to apply, confirm which config.json is used (the loader checks PYEGERIA_CONFIG_DIRECTORY first, then PYEGERIA_ROOT_PATH, then ./config.json).
- .env files are optional. Missing .env is not an error.
- You can always override values with OS environment variables (they take precedence over config.json).



----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.