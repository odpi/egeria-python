import os
from pyegeria.config import PyegeriaSettings, EnvironmentConfig, AppConfig


def test_pyegeria_settings_instantiation():
    # Basic instantiation should work without env
    settings = PyegeriaSettings()
    assert hasattr(settings, 'pyegeria_root_path')


def test_environment_config_defaults():
    env = EnvironmentConfig()
    assert isinstance(env.console_width, int)
    assert env.console_width > 0


def test_app_config_basic_structure():
    # Minimal viable AppConfig composed of defaulted sub-sections
    env = EnvironmentConfig()
    from pyegeria.config import DebugConfig, LoggingConfig, UserProfileConfig
    app = AppConfig(Environment=env, Debug=DebugConfig(), Logging=LoggingConfig(), **{"User Profile": UserProfileConfig()})
    assert app.Environment.console_width == env.console_width
