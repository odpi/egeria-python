# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Build hook: ship the rendered Dr.Egeria templates inside the wheel.

All project metadata lives in pyproject.toml; this file only adds one build
step. ``sample-data/templates/{basic,advanced}`` is the single source of
truth (``gen_md_cmd_templates`` / ``refresh_specs`` write there). At build
time it is copied into ``md_processing/data/templates/`` in the build tree,
so the wheel carries the same files without a second tree in git.
``md_processing.templates`` reads them through ``importlib.resources`` and,
in a source checkout or editable install, falls back to ``sample-data``.
"""
import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

TEMPLATE_LEVELS = ("basic", "advanced")


class BuildPyWithTemplates(build_py):
    def run(self):
        super().run()
        src_root = Path(__file__).resolve().parent / "sample-data" / "templates"
        dest_root = Path(self.build_lib) / "md_processing" / "data" / "templates"
        for level in TEMPLATE_LEVELS:
            src = src_root / level
            if not src.is_dir():
                # Fail the build rather than ship a wheel without templates:
                # a missing tree would only show up later as an empty list.
                raise FileNotFoundError(
                    f"Dr.Egeria templates not found at {src}; "
                    "sample-data/templates must be in the sdist (MANIFEST.in)."
                )
            dest = dest_root / level
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("*.pyc", ".DS_Store"))


setup(cmdclass={"build_py": BuildPyWithTemplates})
