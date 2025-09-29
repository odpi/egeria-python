#!/usr/bin/env python3
"""
Validate a .env-style file for pyegeria configuration.

Usage:
  python scripts/validate_env.py                 # auto-detect: prefer ./config/env, else ./.env
  python scripts/validate_env.py --env path/to/file

This script does not contact any server. It only verifies that the .env can be
parsed by pyegeria and that key values have sensible types.
"""
import argparse
import os
import sys
from pprint import pprint

try:
    # Import lazily through the public API
    from pyegeria.load_config import PyegeriaSettings
except Exception as e:
    print(f"Error: could not import pyegeria: {e}")
    sys.exit(2)


def detect_env_file() -> str | None:
    candidates = [
        os.path.abspath(os.path.join(os.getcwd(), "config", "env")),
        os.path.abspath(os.path.join(os.getcwd(), ".env")),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def validate_settings(settings: "PyegeriaSettings") -> list[str]:
    errors: list[str] = []

    # Basic type validations
    if not isinstance(settings.pyegeria_console_width, int):
        errors.append("PYEGERIA_CONSOLE_WIDTH must parse as an integer")

    # If URLs are provided, ensure they are non-empty strings
    for name in [
        "pyegeria_root_path",
        "pyegeria_config_directory",
        "pyegeria_config_file",
        "egeria_user_name",
        "egeria_user_password",
    ]:
        val = getattr(settings, name, None)
        if val is not None and not isinstance(val, (str, int)):
            errors.append(f"{name} has unexpected type: {type(val).__name__}")

    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate a .env for pyegeria")
    parser.add_argument("--env", dest="env_file", help="Path to .env-like file (defaults to ./config/env or ./.env)")
    args = parser.parse_args(argv)

    env_file = args.env_file or detect_env_file()
    if not env_file:
        print("No env file provided and none detected in ./config/env or ./.env")
        return 1

    print(f"Using env file: {env_file}")

    try:
        settings = PyegeriaSettings.with_env_file(env_file)
    except Exception as e:
        print(f"Failed to load environment from {env_file}: {e}")
        return 2

    # Display a summary of key values actually loaded
    summary = {
        "pyegeria_root_path": settings.pyegeria_root_path,
        "pyegeria_config_directory": settings.pyegeria_config_directory,
        "pyegeria_config_file": settings.pyegeria_config_file,
        "pyegeria_console_width": settings.pyegeria_console_width,
        "egeria_user_name": settings.egeria_user_name,
        "egeria_user_password": "***" if settings.egeria_user_password else "",
    }

    print("Loaded settings summary (secrets masked):")
    pprint(summary)

    errors = validate_settings(settings)
    if errors:
        print("\nValidation errors:")
        for e in errors:
            print(f" - {e}")
        return 3

    print("\n.env validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
