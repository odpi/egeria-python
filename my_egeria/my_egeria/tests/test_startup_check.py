""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file is a unit test for my_egeria.


"""

import os
import pytest
from ..startup_check import validate_envs, check_connection


def test_validate_envs_missing(monkeypatch):
    monkeypatch.setenv("EGERIA_SERVER", "")
    monkeypatch.setenv("EGERIA_BASE_URL", "")
    ok, msg = validate_envs()
    assert not ok
    assert "Missing environment variables" in msg


def test_check_connection_no_pyegeria(monkeypatch):
    # Simulate import error by inserting dummy module
    monkeypatch.setitem(__import__("sys").modules, "pyegeria", None)
    ok, msg = check_connection()
    assert not ok
    assert "pyegeria import failed" in msg
