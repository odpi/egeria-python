""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file is a unit test for my_egeria.


"""

import os
import sys
from pathlib import Path

# Ensure `src` is on sys.path so imports like `services.*` and `my_egeria.*` work in tests
# tests/ is at: <project-root>/src/my_egeria/tests
SRC_DIR = Path(__file__).resolve().parents[2]  # -> <project-root>/src
if SRC_DIR.is_dir():
    sys.path.insert(0, str(SRC_DIR))

def pytest_configure():
    # Ensure pyegeria-required env vars are set and non-empty for import-time validation
    os.environ.setdefault("EGERIA_USER", "erinoverview")
    os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
    os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")
    os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")


# @pytest.fixture(scope="session", autouse=True)
# def _pytest_asyncio_auto():
#     """Ensure pytest-asyncio auto mode is used for async TUI tests."""
#     pytest.register_assert_rewrite("textual")
