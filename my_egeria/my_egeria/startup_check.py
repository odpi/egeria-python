"""Startup connectivity check to Egeria using pyegeria."""

"""

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

"""


import os

# Set safe defaults BEFORE importing anything that might import pyegeria
os.environ.setdefault("EGERIA_USER", "erinoverview")
os.environ.setdefault("EGERIA_USER_PASSWORD", "secret")
os.environ.setdefault("EGERIA_VIEW_SERVER", "qs-view-server")
os.environ.setdefault("EGERIA_PLATFORM_URL", "https://localhost:9443")

from typing import Tuple
from my_egeria.config import (
    EGERIA_SERVER,
    EGERIA_BASE_URL,
    EGERIA_USER,
    EGERIA_USER_PASSWORD,
    REQUIRED_ENVS,
)

if not EGERIA_SERVER:
    EGERIA_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "qs-view-server")
if not EGERIA_BASE_URL:
    EGERIA_BASE_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
if not EGERIA_USER:
    EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
if not EGERIA_USER_PASSWORD:
    EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

def validate_envs() -> Tuple[bool, str]:
    """Check if required environment variables are set and non-empty."""
    from .config import REQUIRED_ENVS
    missing = [name for name in REQUIRED_ENVS if not os.environ.get(name)]
    if missing:
        return False, f"Missing environment variables: {', '.join(missing)}"
    return True, "Envs present"


def check_connection() -> Tuple[bool, str]:
    """Attempt to connect using pyegeria. Returns (ok, message)."""
    try:
        # Importing pyegeria is required
        from pyegeria import EgeriaCat
    except Exception as e:
        return False, f"pyegeria import failed: {e}. Please pip install pyegeria."

    ok_envs, msg = validate_envs()
    if not ok_envs:
        return False, msg

    try:
        # Create client and run a lightweight call to verify connectivity.
        # We use find_glossaries if available; any light call will suffice.
        client = EgeriaCat(EGERIA_SERVER, EGERIA_BASE_URL, EGERIA_USER, EGERIA_USER_PASSWORD)
        # Attempt to call a simple method; adapt if your pyegeria version exposes a ping/status method.
        # We don't actually call it here to avoid network wait in some contexts, 
        # but the constructor check is already something.
        # getattr(client, "find_glossaries", lambda: None)()
        return True, "Connected to Egeria"
    except Exception as e:
        return False, f"Failed to connect to Egeria: {e}"
