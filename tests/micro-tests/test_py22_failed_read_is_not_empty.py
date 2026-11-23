"""PY-22: a failed read is not "none". Two reads that turned any error into [] now say they could not read."""
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from pyegeria import PyegeriaInvalidParameterException
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.view import overview_metrics as om


class _Stub(AutomatedCuration):
    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return "http://x"


def _curation():
    c = _Stub.__new__(_Stub)
    return c


# ── item 2: the survey type's action targets ──
def test_a_failed_read_of_the_action_targets_is_none_not_empty():
    c = _curation()
    c.__async_get_guid__ = AsyncMock(return_value="g-1")
    c._async_make_request = AsyncMock(side_effect=TimeoutError("slow"))
    assert asyncio.run(AutomatedCuration._async_get_supported_action_target_names(c, "S::1")) is None


def test_an_unresolvable_survey_type_is_none_not_empty():
    c = _curation()
    c.__async_get_guid__ = AsyncMock(return_value=None)
    assert asyncio.run(AutomatedCuration._async_get_supported_action_target_names(c, "S::1")) is None


def test_a_read_survey_type_with_no_targets_is_still_empty():
    c = _curation()
    c.__async_get_guid__ = AsyncMock(return_value="g-1")
    resp = MagicMock(); resp.json.return_value = {"element": {"specification": {}}}
    c._async_make_request = AsyncMock(return_value=resp)
    assert asyncio.run(AutomatedCuration._async_get_supported_action_target_names(c, "S::1")) == []


def test_initiate_survey_says_the_targets_could_not_be_read_and_sends_nothing():
    c = _curation()
    c._async_get_supported_action_target_names = AsyncMock(return_value=None)
    c._async_make_request = AsyncMock()
    with pytest.raises(PyegeriaInvalidParameterException) as info:
        asyncio.run(AutomatedCuration._async_initiate_survey(c, "PostgreSQLSurvey::survey-postgres-database",
                                                              "6b0b3c8e-1c36-4f0e-8a4e-111111111111"))
    assert "could not be read" in str(info.value) and "action_target_name" in str(info.value)
    c._async_make_request.assert_not_called()


def test_initiate_survey_with_an_explicit_target_never_reads_the_targets():
    c = _curation()
    c._async_get_supported_action_target_names = AsyncMock(side_effect=AssertionError("must not be read"))
    resp = MagicMock(); resp.json.return_value = {"guid": "a-1"}
    c._async_make_request = AsyncMock(return_value=resp)
    out = asyncio.run(AutomatedCuration._async_initiate_survey(
        c, "S::1", "6b0b3c8e-1c36-4f0e-8a4e-111111111111", action_target_name="t"))
    assert out == "a-1"


# ── item 3: karma_leaderboard ──
def test_karma_leaderboard_is_none_when_the_find_raises():
    mgr = MagicMock()
    mgr.find_metadata_elements.side_effect = TimeoutError("slow")
    assert om.karma_leaderboard(mgr) is None


def test_karma_leaderboard_is_none_when_the_scan_is_unknown(monkeypatch):
    monkeypatch.setattr(om, "_all_elements", lambda mgr, body: None)
    assert om.karma_leaderboard(MagicMock()) is None


def test_karma_leaderboard_is_empty_when_read_in_full_and_nobody_qualifies(monkeypatch):
    monkeypatch.setattr(om, "_all_elements", lambda mgr, body: [])
    assert om.karma_leaderboard(MagicMock()) == []
