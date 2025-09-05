"""
Compatibility shim for legacy imports.
Re-exports configuration loading utilities from pyegeria.config.
"""
# Import config lazily inside functions to avoid import-time side effects in tests
from importlib import import_module

def load_app_config(env_file: str | None = None):
    return import_module('pyegeria.config').load_app_config(env_file)

def get_app_config(env_file: str | None = None):
    return import_module('pyegeria.config').get_app_config(env_file)

class PyegeriaSettings:
    def __new__(cls, *args, **kwargs):
        # Construct a real settings instance from pyegeria.config
        return import_module('pyegeria.config').PyegeriaSettings(*args, **kwargs)

    @classmethod
    def with_env_file(cls, env_file: str):
        return import_module('pyegeria.config').PyegeriaSettings.with_env_file(env_file)

# expose the cached instance for tests that reset it directly
from . import config as _config

def __getattr__(name):
    if name == "_app_config":
        return _config._app_config
    raise AttributeError(name)


def __setattr__(name, value):
    if name == "_app_config":
        _config._app_config = value
    else:
        globals()[name] = value
