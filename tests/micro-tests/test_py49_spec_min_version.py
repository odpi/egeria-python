# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""PY-49: a report spec can say it needs a later Egeria, and the report runner refuses it before the find.

A FormatSet carries `min_egeria_version` (stored under the annotation of that name, so the seed and the Egeria-held
envelope round-trip unchanged). The runner asks `pyegeria.core.egeria_6_4_gate` whether the platform carries the 6.4
additions and, when it does not, refuses with the same "needs Egeria 6.4" words the Dr.Egeria commands use (PY-48) and
sends nothing. An unreadable version is unknown, never "no": the find is sent. The three 6.4-only types, Decision,
DataValue and LiteralDataValue, carry the field.

No Egeria: a fake client answers /api/about and records the find.
"""
import json

import pytest

from pyegeria.core import egeria_6_4_gate as gate
from pyegeria.view._output_format_models import FormatSet
from pyegeria.view import format_set_executor as fse
from pyegeria.view.base_report_formats import get_report_registry

pytestmark = pytest.mark.unit

ABOUT_6_3 = json.dumps({"class": "AboutPlatform", "version": "6.3", "time": "2026-11-20T10:00:00Z"})
ABOUT_6_4 = json.dumps({"class": "AboutPlatform", "version": "6.4", "time": "2026-11-22T10:00:00Z"})


class FakeClient:
    about = ABOUT_6_3
    calls: list = []

    def __init__(self, view_server, view_url, user_id=None, user_pwd=None):
        self.platform_url = view_url
        type(self).calls = []

    def set_bearer_token(self, token):
        pass

    def create_egeria_bearer_token(self):
        pass

    async def async_get_platform_origin(self):
        return type(self).about

    def find_things(self, search_string="*", **kw):
        type(self).calls.append(search_string)
        return []


@pytest.fixture(autouse=True)
def _fresh_gate():
    gate.clear_cache()
    yield
    gate.clear_cache()


def _spec(min_version=None):
    return {
        "target_type": "Decision", "heading": "Gated", "description": "d",
        "annotations": {"min_egeria_version": [min_version]} if min_version else {},
        "action": {"function": "FakeManager.find_things", "required_params": ["search_string"]},
        "formats": [{"types": ["DICT"], "attributes": [{"name": "Display Name", "key": "display_name"}]}],
    }


def _run(spec, about, platform_url="https://p63:9443"):
    FakeClient.about = about
    return fse.exec_report_spec(spec, output_format="DICT", params={"search_string": "x"}, view_server="v",
                                view_url=platform_url, user="u", user_pass="p", token="t")


@pytest.fixture(autouse=True)
def _fake_manager(monkeypatch):
    monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (FakeClient, "find_things"))


def test_the_model_exposes_the_minimum_version():
    fs = FormatSet(**_spec("6.4"))
    assert fs.min_egeria_version == "6.4"
    assert FormatSet(**_spec()).min_egeria_version is None


def test_only_a_checkable_version_is_accepted():
    with pytest.raises(ValueError, match="min_egeria_version"):
        FormatSet(**_spec("7.0"))


def test_before_6_4_the_runner_refuses_in_words_and_sends_nothing():
    with pytest.raises(fse.SpecNeedsNewerEgeria) as err:
        _run(_spec("6.4"), ABOUT_6_3)
    message = str(err.value)
    assert "needs Egeria 6.4" in message and "runs Egeria 6.3" in message and "Nothing was sent" in message
    assert "https://p63:9443" in message
    assert FakeClient.calls == []


def test_on_6_4_the_find_runs():
    out = _run(_spec("6.4"), ABOUT_6_4)
    assert out["kind"] in ("json", "empty") and FakeClient.calls == ["x"]


def test_an_unreadable_version_is_unknown_not_no_so_the_find_is_sent():
    _run(_spec("6.4"), "not json")
    assert FakeClient.calls == ["x"]


def test_a_spec_without_the_field_is_never_gated():
    _run(_spec(), ABOUT_6_3)
    assert FakeClient.calls == ["x"]


@pytest.mark.parametrize("label", ["Decision", "Data-Value", "Literal-Data-Value", "Decision-DrE-Basic",
                                   "Decision-DrE-Advanced", "Data-Value-DrE-Basic", "Data-Value-DrE-Advanced"])
def test_the_6_4_only_specs_carry_the_field(label):
    assert get_report_registry()[label].min_egeria_version == "6.4"


def test_other_specs_do_not_carry_it():
    carrying = sorted(k for k, v in get_report_registry().items() if v.min_egeria_version)
    assert carrying == ["Data-Value", "Data-Value-DrE-Advanced", "Data-Value-DrE-Basic", "Decision",
                        "Decision-DrE-Advanced", "Decision-DrE-Basic", "Literal-Data-Value"]
