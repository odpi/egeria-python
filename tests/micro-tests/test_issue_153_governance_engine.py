# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-153: Egeria #9371 moved engine-action claim/status/completion operations from the automated-curation
view service to a new governance-engine one. No live server: `_async_make_request` is replaced with a recorder.
"""
import warnings
from unittest.mock import MagicMock, patch

import pytest

from pyegeria.core._exceptions import PyegeriaClientException, PyegeriaNotFoundException
from pyegeria.omvs.automated_curation import AutomatedCuration
from pyegeria.omvs.governance_engine import GovernanceEngine

ROOT = "https://localhost:9443/servers/vs/api/open-metadata"
NEW = f"{ROOT}/governance-engine"
OLD = f"{ROOT}/automated-curation"
G = "11111111-1111-1111-1111-111111111111"
G2 = "22222222-2222-2222-2222-222222222222"


def _client(cls, **kw):
    with patch("pyegeria.core._base_server_client.BaseServerClient.check_connection", return_value=""):
        return cls(view_server="vs", platform_url="https://localhost:9443", user_id="u", user_pwd="p", **kw)


def _err(code):
    resp = MagicMock()
    resp.status_code = code
    resp.text = ""
    resp.json = MagicMock(return_value={})
    return PyegeriaClientException(resp, {}, {"userid": "u"}, Exception("boom"))


def _install(client, outcomes=None, elements=None):
    """Record calls; `outcomes` is a list of exceptions/None consumed per call."""
    calls = []
    outcomes = list(outcomes or [])

    async def fake(method, url, body=None, **kwargs):
        calls.append({"method": method, "url": url, "body": body, "params": kwargs.get("params")})
        out = outcomes.pop(0) if outcomes else None
        if isinstance(out, Exception):
            raise out
        resp = MagicMock()
        resp.json = MagicMock(return_value={"elements": elements} if elements is not None else {})
        return resp

    client._async_make_request = fake
    return calls


def _all_ge_calls(ge):
    return [
        (lambda: ge.claim_engine_action(G), "POST", f"/engine-actions/{G}/claim", None, None),
        (lambda: ge.update_engine_action_status(G, "IN_PROGRESS"), "POST", f"/engine-actions/{G}/status/update",
         {"class": "EngineActionStatusRequestBody", "status": "IN_PROGRESS"}, None),
        (lambda: ge.update_action_target_status(G2, "COMPLETED", completion_message="ok"), "POST",
         "/engine-actions/action-targets/update",
         {"class": "ActionTargetStatusRequestBody", "actionTargetGUID": G2, "status": "COMPLETED",
          "completionMessage": "ok"}, None),
        (lambda: ge.record_completion_status(G, "ACTIONED", output_guards=["g1"]), "POST",
         f"/engine-actions/{G}/completion-status",
         {"class": "CompletionStatusRequestBody", "status": "ACTIONED", "outputGuards": ["g1"]}, None),
        (lambda: ge.get_active_claimed_engine_actions(G, 2, 5), "GET",
         f"/governance-engines/{G}/engine-actions/active-claimed", None, {"startFrom": 2, "pageSize": 5}),
    ]


@pytest.mark.parametrize("i", range(5))
def test_governance_engine_urls(i):
    ge = _client(GovernanceEngine)
    calls = _install(ge, elements=[])
    fn, method, suffix, body, params = _all_ge_calls(ge)[i]
    fn()
    assert len(calls) == 1
    c = calls[0]
    assert (c["method"], c["url"], c["params"]) == (method, NEW + suffix, params)
    if body is not None:
        assert {k: v for k, v in c["body"].items() if v is not None} == body


def test_get_approved():
    ge = _client(GovernanceEngine)
    calls = _install(ge, elements=[{"x": 1}])
    assert ge.get_approved_engine_actions(G) == [{"x": 1}]
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == f"{NEW}/governance-engines/{G}/engine-actions/approved"
    assert calls[0]["params"] == {"startFrom": 0, "pageSize": 0}
    calls2 = _install(ge)
    assert ge.get_approved_engine_actions(G, 1, 3) == "No elements found"
    assert calls2[0]["params"] == {"startFrom": 1, "pageSize": 3}


def test_cancel_governance_action_process():
    ac = _client(AutomatedCuration)
    calls = _install(ac)
    ac.cancel_governance_action_process(G)
    assert calls == [{"method": "POST", "url": f"{OLD}/governance-action-process-instances/{G}/cancel",
                      "body": None, "params": None}]


@pytest.mark.parametrize("i", range(5))
def test_automated_curation_wrappers_use_new_url_and_warn(i):
    ac = _client(AutomatedCuration)
    ge = ac._governance_engine_client()
    calls = _install(ge, elements=[])
    fn, method, suffix, body, params = _all_ge_calls(ac)[i]
    with pytest.warns(DeprecationWarning):
        fn()
    assert calls[0]["url"] == NEW + suffix and calls[0]["method"] == method


def test_404_falls_back_once_and_caches():
    ac = _client(AutomatedCuration)
    ge = ac._governance_engine_client()
    calls = _install(ge, outcomes=[_err(404)])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ac.claim_engine_action(G)
        assert [c["url"] for c in calls] == [f"{NEW}/engine-actions/{G}/claim", f"{OLD}/engine-actions/{G}/claim"]
        ac.update_engine_action_status(G, "COMPLETED")
    # cached: the next call goes straight to the old path, no new-path probe
    assert calls[2]["url"] == f"{OLD}/engine-actions/{G}/status/update"
    assert len(calls) == 3
    assert calls[2]["body"]["status"] == "COMPLETED"


def test_new_path_success_is_cached_and_never_probes_old():
    ac = _client(AutomatedCuration)
    ge = ac._governance_engine_client()
    calls = _install(ge, outcomes=[None, _err(404)])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        ac.claim_engine_action(G)
        with pytest.raises(PyegeriaClientException):
            ac.claim_engine_action(G)  # once the new URL has worked a 404 is raised, not retried
    assert len(calls) == 2 and all(c["url"].startswith(NEW) for c in calls)


@pytest.mark.parametrize("exc", [lambda: _err(500), lambda: _err(403), lambda: _err(401)])
def test_non_404_error_does_not_fall_back(exc):
    ac = _client(AutomatedCuration)
    ge = ac._governance_engine_client()
    calls = _install(ge, outcomes=[exc()])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(PyegeriaClientException):
            ac.claim_engine_action(G)
    assert len(calls) == 1 and calls[0]["url"].startswith(NEW)


def test_egeria_reported_not_found_does_not_fall_back():
    ac = _client(AutomatedCuration)
    ge = ac._governance_engine_client()
    resp = MagicMock()
    resp.status_code = 200
    resp.json = MagicMock(return_value={"relatedHTTPCode": 404})
    nf = PyegeriaNotFoundException(resp, {}, additional_info={"relatedHTTPCode": 404})
    calls = _install(ge, outcomes=[nf])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with pytest.raises(PyegeriaNotFoundException):
            ac.claim_engine_action(G)
    assert len(calls) == 1


def test_direct_governance_engine_never_falls_back():
    ge = _client(GovernanceEngine)
    calls = _install(ge, outcomes=[_err(404)])
    with pytest.raises(PyegeriaClientException):
        ge.claim_engine_action(G)
    assert len(calls) == 1


def test_egeria_client_proxy_exposes_gov_engine():
    from pyegeria.egeria_tech_client import EgeriaTech
    assert EgeriaTech.__init__  # import works
    import pyegeria
    assert pyegeria.GovernanceEngine is GovernanceEngine
