"""
Deprecated module shim.
This module has been renamed to pyegeria.base_report_formats.
It re-exports all public APIs and raises DeprecationWarning on import.
"""
import warnings

warnings.warn(
    "pyegeria._output_formats is deprecated; use pyegeria.base_report_formats instead",
    DeprecationWarning,
    stacklevel=2,
)

from .base_report_formats import *  # noqa: F401,F403
