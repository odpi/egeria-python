"""
exec_report_spec only copies a report spec's declared required/optional params into
the call, so a caller's graph_query_depth used to be silently dropped and every call
ran at the SDK default depth of 3 (live: the "Glossaries" list timed out at 90s at
depth 3 vs 0.3s at depth 0). It is now forwarded when the target method accepts it.
"""
import pytest

import pyegeria.view.format_set_executor as fse


class _FakeClient:
    calls: list = []

    def __init__(self, *args, **kwargs):
        pass

    def create_egeria_bearer_token(self, *args, **kwargs):
        return "token"

    def set_bearer_token(self, token):
        pass

    def close_session(self):
        pass

    def find_glossaries(self, search_string="*", graph_query_depth: int = 3, **kwargs):
        _FakeClient.calls.append({"search_string": search_string, "graph_query_depth": graph_query_depth, **kwargs})
        return [{"guid": "g1"}]

    def no_depth_method(self, search_string="*", output_format="DICT", report_spec=None):
        _FakeClient.calls.append({"search_string": search_string})
        return [{"guid": "g1"}]


@pytest.fixture(autouse=True)
def _fake_client(monkeypatch):
    _FakeClient.calls = []
    monkeypatch.setattr(fse, "_resolve_client_and_method",
                        lambda func_decl: (_FakeClient, func_decl.split(".")[-1]))


def _run(params):
    # "Glossaries" is a real registered spec (GlossaryManager.find_glossaries) that does
    # not list graph_query_depth in its required/optional params.
    return fse.exec_report_spec("Glossaries", output_format="DICT", params=params,
                                view_server="v", view_url="https://x", user="u", user_pass="p")


@pytest.mark.parametrize("depth", [0, 1])
def test_graph_query_depth_reaches_the_method(depth):
    result = _run({"search_string": "*", "graph_query_depth": depth})
    assert result["kind"] == "json"
    assert _FakeClient.calls[0]["graph_query_depth"] == depth


def test_default_depth_unchanged_when_not_given():
    _run({"search_string": "*"})
    assert _FakeClient.calls[0]["graph_query_depth"] == 3


def test_other_undeclared_params_still_not_forwarded():
    _run({"search_string": "*", "graph_query_depth": 0, "not_a_spec_param": "x"})
    assert "not_a_spec_param" not in _FakeClient.calls[0]


def test_not_forwarded_to_a_method_that_cannot_take_it():
    params = {"search_string": "*", "graph_query_depth": 0}
    merged = fse._add_request_options(_FakeClient().no_depth_method, params, {"search_string": "*"})
    assert "graph_query_depth" not in merged
