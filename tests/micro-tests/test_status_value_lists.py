"""PY-21: pyegeria's fallback status lists match Egeria's valid metadata values.

The seed report specs' activity_status columns still lack FOR_INFO: they are generated from the Dr.Egeria
command specs, so that part of PY-21 is fixed there and regenerated (follow-up), not here.

Read from laz's Egeria (get_valid_metadata_values, 2026-11-16):
  deploymentStatus: ACTIVE, APPROVED_FOR_DEPLOYMENT, DEVELOPMENT_COMPLETE, DISABLED, FAILED, OTHER,
                    PROPOSED, REJECTED, STANDBY, UNDER_DEVELOPMENT
  activityStatus:   ABANDONED, ACTIVATING, APPROVED, CANCELLED, COMPLETED, FAILED, FOR_INFO, IGNORED,
                    INVALID, IN_PROGRESS, OTHER, PAUSED, REQUESTED, WAITING
"""
import json
from pathlib import Path

import pyegeria
from pyegeria.core import _globals

EGERIA_DEPLOYMENT_STATUS = {"ACTIVE", "APPROVED_FOR_DEPLOYMENT", "DEVELOPMENT_COMPLETE", "DISABLED", "FAILED",
                            "OTHER", "PROPOSED", "REJECTED", "STANDBY", "UNDER_DEVELOPMENT"}
EGERIA_ACTIVITY_STATUS = {"ABANDONED", "ACTIVATING", "APPROVED", "CANCELLED", "COMPLETED", "FAILED", "FOR_INFO",
                          "IGNORED", "INVALID", "IN_PROGRESS", "OTHER", "PAUSED", "REQUESTED", "WAITING"}

SEED_DIR = Path(pyegeria.__file__).parent / "view" / "seed"


def test_deployment_status_fallback_matches_egeria():
    assert set(_globals.DEPLOYMENT_STATUS) == EGERIA_DEPLOYMENT_STATUS
    assert "REJECTED_FOR_DEPLOYMENT" not in _globals.DEPLOYMENT_STATUS


def test_activity_status_fallback_matches_egeria():
    assert set(_globals.ACTIVITY_STATUS) == EGERIA_ACTIVITY_STATUS


def _columns(obj):
    if isinstance(obj, dict):
        if "field" in obj and "valid_values" in obj:
            yield obj
        for v in obj.values():
            yield from _columns(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _columns(v)


def test_seed_deployment_status_columns_use_egeria_values():
    for path in sorted(SEED_DIR.glob("*.json")):
        for col in _columns(json.loads(path.read_text())):
            if col["field"] == "deployment_status":
                assert set(col["valid_values"]) <= EGERIA_DEPLOYMENT_STATUS, f"{path.name}: {col['valid_values']}"
