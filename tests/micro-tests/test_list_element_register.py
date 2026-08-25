# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
Unit tests for commands/tech/list_element_register.py -- the hey_egeria
"register" view: any Open Metadata Type, grouped by each element's own
real subtype, with classification badges and a simple search/classification
filter. General-purpose by design (not tied to governance definitions or
any particular data set).

No live server needed: EgeriaTech is monkeypatched with a fake exposing
just the methods this command calls.
"""
from rich.text import Text

from commands.tech import list_element_register as reg


class _FakeTypedClient:
    def __init__(self, *args, **kwargs):
        pass

    def create_egeria_bearer_token(self, *args, **kwargs):
        return "fake-token"

    def get_typedef_by_name(self, om_type):
        return {"name": om_type}

    def close_session(self):
        pass


def _element(display_name, qualified_name, type_name, classifications=None):
    return {
        "elementHeader": {
            "guid": f"guid-{qualified_name}",
            "type": {"typeName": type_name},
            "otherClassifications": [
                {"classificationName": c} for c in (classifications or [])
            ],
        },
        "properties": {
            "displayName": display_name,
            "qualifiedName": qualified_name,
        },
    }


ELEMENTS = [
    _element("A Trustworthy Third-Party Network", "GovDef::1", "BusinessImperative", ["CORPORATE"]),
    _element("Financial Reporting Integrity", "GovDef::2", "BusinessImperative", ["CORPORATE"]),
    _element("Cyber Resilience", "GovDef::3", "Threat", ["SECURITY"]),
]


def _make_fake_client(pages):
    """pages: list of pages (lists) to return in order, then empty.

    `instances`: every constructed fake client, in creation order, so a
    caller can inspect calls made on the one `element_register` built.
    """

    class _FakeClient(_FakeTypedClient):
        instances: list = []

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._pages = list(pages)
            self.calls = []
            _FakeClient.instances.append(self)

        def get_elements(self, om_type, start_from=0, page_size=100, output_format="JSON"):
            self.calls.append((om_type, start_from, page_size))
            if self._pages:
                return self._pages.pop(0)
            return []

    return _FakeClient


def test_groups_by_real_subtype_not_the_queried_base_type(monkeypatch, capsys):
    monkeypatch.setattr(reg, "EgeriaTech", _make_fake_client([ELEMENTS]))

    reg.element_register("GovernanceDefinition", "vs", "https://localhost:9443", "u", "p", width=200)

    out = capsys.readouterr().out
    assert "BusinessImperative" in out
    assert "Threat" in out
    assert "(2)" in out  # BusinessImperative group size
    assert "(1)" in out  # Threat group size


def test_search_filters_by_display_name(monkeypatch, capsys):
    monkeypatch.setattr(reg, "EgeriaTech", _make_fake_client([ELEMENTS]))

    reg.element_register("GovernanceDefinition", "vs", "https://localhost:9443", "u", "p",
                          search="Cyber", width=200)

    out = capsys.readouterr().out
    assert "Cyber Resilience" in out
    assert "Financial Reporting Integrity" not in out


def test_classification_filter(monkeypatch, capsys):
    monkeypatch.setattr(reg, "EgeriaTech", _make_fake_client([ELEMENTS]))

    reg.element_register("GovernanceDefinition", "vs", "https://localhost:9443", "u", "p",
                          classification="SECURITY", width=200)

    out = capsys.readouterr().out
    assert "Cyber Resilience" in out
    assert "Financial Reporting Integrity" not in out


def test_pages_until_empty_result_not_until_short_page(monkeypatch):
    # Egeria's paging contract: a short page doesn't mean "last page", only
    # an empty one does. Simulate a full first page (== page_size) followed
    # by a short-but-nonempty second page, then empty.
    full_page = [_element(f"Item {i}", f"qn::{i}", "Thing") for i in range(3)]
    short_page = [_element("Last Item", "qn::last", "Thing")]
    FakeClient = _make_fake_client([full_page, short_page])
    monkeypatch.setattr(reg, "EgeriaTech", FakeClient)

    reg.element_register("Thing", "vs", "https://localhost:9443", "u", "p", page_size=3, width=200)

    # Keeps asking past the short-but-nonempty second page -- correctly
    # treating "short" as not proof of "last" -- and only stops once a
    # third, genuinely empty page confirms it.
    assert FakeClient.instances[-1].calls == [("Thing", 0, 3), ("Thing", 3, 3), ("Thing", 6, 3)]


def test_display_name_falls_back_to_qualified_name():
    assert reg._display_name({}, "Fallback::QN") == "Fallback::QN"
    assert reg._display_name({"name": "Named"}, "Fallback::QN") == "Named"


def test_badge_style_is_deterministic():
    assert reg._badge_style("DATA") == reg._badge_style("DATA")


def test_badges_renders_all_labels():
    text = reg._badges(["DATA", "SECURITY"])
    assert isinstance(text, Text)
    assert "DATA" in text.plain
    assert "SECURITY" in text.plain
