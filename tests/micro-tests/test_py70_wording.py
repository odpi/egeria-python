"""PY-70: N1 the spec-cache reason does not say the element is gone or invisible when Egeria only says it is
not effective for this read (OMAG-REPOSITORY-HANDLER-400-010); N2 karma_leaderboard declares it may return None."""
from types import SimpleNamespace

import httpx

from pyegeria import PyegeriaBadRequestException
from pyegeria.view import egeria_spec_cache as cache

BODY_400_010 = {
    "class": "VoidResponse", "relatedHTTPCode": 400,
    "exceptionErrorMessageId": "OMAG-REPOSITORY-HANDLER-400-010",
    "exceptionErrorMessage": "OMAG-REPOSITORY-HANDLER-400-010 The element with guid 1234 is not visible to the "
                             "caller because it is anchored to or classified with [Anchors, Promise]",
}


def test_not_visible_reason_says_not_effective_and_never_deleted(monkeypatch):
    resp = httpx.Response(200, json=BODY_400_010, request=httpx.Request("POST", "https://egeria/x"))
    exc = PyegeriaBadRequestException(resp, {"caller": "t"}, additional_info=BODY_400_010)

    def boom(client, guid):
        raise exc
    monkeypatch.setattr(cache, "_get_full", boom)
    state, why = cache._pinned_element_state(SimpleNamespace(user_id="erin"), "1234")
    assert state == "gone"
    assert "not effective for this read" in why
    assert "no longer visible" not in why and "deleted" not in why.lower()


def test_karma_leaderboard_returns_declares_none():
    from pyegeria.view.analytic_registry import _BUILTINS as F
    assert F["karma_leaderboard"].returns.startswith("list[dict] | None")
