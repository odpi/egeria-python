# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Every single unpaged get_collections_by_name read gets a disposition (MyEgeria read-back point (b)).

- An exact qualified name is answered by Egeria's unique-name read (pyegeria.core.unique_name): found / absent
  (only NO_ELEMENTS_FOUND or PyegeriaNotFoundException, or another type holds the name) / unknown (anything
  else). Readers say "couldn't tell" on unknown, never "not found": egeria_folders.find_folder,
  egeria_folders.read_consumer_tree's root, export_dcat._read_scope.
- A label (not an exact qualified name) is paged with paging_for, and "not found" only on a confirmed end:
  egeria_spec_cache._find_specs_by_label and its async twin.
"""
import asyncio
from unittest.mock import MagicMock

import pytest

from pyegeria.core import paging
from pyegeria.core import unique_name as un
from pyegeria.core._exceptions import PyegeriaException, PyegeriaNotFoundException
from pyegeria.view import egeria_folders as folders
from pyegeria.view import egeria_spec_cache as esc

pytestmark = pytest.mark.unit

NULL = "No elements found"


def _el(guid, qn, type_name="CollectionFolder", supers=()):
    return {"elementHeader": {"guid": guid, "type": {"typeName": type_name, "superTypeNames": list(supers)}},
            "properties": {"qualifiedName": qn, "displayName": qn.rsplit("::", 1)[-1]}}


def _not_found():
    return PyegeriaNotFoundException.__new__(PyegeriaNotFoundException)


def _failed():
    return PyegeriaException("boom")


class Unique:
    """A client whose only read is the unique-name read; any by-name search fails the test."""

    def __init__(self, answer=None, error=None):
        self.answer, self.error, self.asked = answer, error, []
        self.user_id = "erinoverview"

    def get_element_by_unique_name(self, qn, *_, **__):
        self.asked.append(qn)
        if self.error is not None:
            raise self.error
        return NULL if self.answer is None else self.answer

    def get_collections_by_name(self, *a, **k):
        raise AssertionError("a by-name search decided an exact qualified name")


# ── pyegeria.core.unique_name ────────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("client, type_name, answer", [
    (Unique(_el("g", "Q")), "CollectionFolder", "found"),
    (Unique(_el("g", "Q", "DigitalProductCatalog", ["Collection"])), "Collection", "found"),   # a subtype
    (Unique(), "CollectionFolder", "absent"),                                  # NO_ELEMENTS_FOUND
    (Unique(error=_not_found()), "CollectionFolder", "absent"),                # Egeria's specific not-found
    (Unique(_el("g", "Q", "Asset")), "CollectionFolder", "absent"),            # another type holds the name
    (Unique(error=_failed()), "CollectionFolder", "unknown"),
    (Unique(error=TimeoutError("slow")), "CollectionFolder", "unknown"),
    (Unique("garbage"), "CollectionFolder", "unknown"),
], ids=["found", "subtype", "no-elements", "not-found", "wrong-type", "pyegeria-error", "timeout", "not-an-element"])
def test_unique_name_answers(client, type_name, answer):
    found = un.by_unique_name(client, "Q", type_name)
    assert found.answer == answer
    if answer == "absent" and client.answer and isinstance(client.answer, dict):
        assert found.wrong_type == "Asset"
    if answer == "unknown":
        assert "Couldn't tell whether Egeria holds" in found.words("the folder")


def test_unique_name_async():
    class A:
        async def _async_get_element_by_unique_name(self, qn, *_, **__):
            return _el("g", qn)
    assert asyncio.run(un.async_by_unique_name(A(), "Q", "CollectionFolder")).guid == "g"


def test_reader_falls_back_to_classification_manager_then_a_new_explorer(monkeypatch):
    sub = Unique(_el("g", "Q"))
    via_sub = MagicMock(spec=["classification_manager"], classification_manager=sub)
    assert un.by_unique_name(via_sub, "Q").guid == "g"

    made = []

    class Explorer:
        def __init__(self, view_server, platform_url, user_id=None, user_pwd=None):
            made.append((view_server, platform_url, user_id))
            self.token = None

        def set_bearer_token(self, token):
            self.token = token

        def get_element_by_unique_name(self, qn, *_, **__):
            return _el("e", qn)

    import pyegeria.omvs.classification_explorer as ce
    monkeypatch.setattr(ce, "ClassificationExplorer", Explorer)
    cm = MagicMock(spec=["view_server", "platform_url", "user_id", "user_pwd", "get_token"],
                   view_server="qs", platform_url="https://p", user_id="erin", user_pwd=None)
    cm.get_token.return_value = "tok"
    assert un.by_unique_name(cm, "Q").guid == "e" and made == [("qs", "https://p", "erin")]


# ── egeria_folders.find_folder (dashboards, the spec-cache sync, restricted specs) ───────────────────────────

def test_find_folder_found_absent_unknown():
    assert folders.find_folder(Unique(_el("f", "F::A")), "F::A")["elementHeader"]["guid"] == "f"
    assert folders.find_folder(Unique(), "F::A") is None
    assert folders.find_folder(Unique(error=_not_found()), "F::A") is None
    assert folders.find_folder(Unique(_el("x", "F::A", "Asset")), "F::A") is None   # not a folder
    with pytest.raises(un.UniqueNameUnknown, match="Couldn't tell whether Egeria holds the folder F::A"):
        folders.find_folder(Unique(error=_failed()), "F::A")


def test_an_unknown_folder_keeps_its_cached_specs_never_prunes(tmp_path, monkeypatch):
    # sync_report_specs: a folder Egeria can't answer for is "could not be read" (kept), never "not found" (pruned)
    monkeypatch.setattr(esc, "_find_folder", lambda c, qn: folders.find_folder(Unique(error=_failed()), qn))
    report = esc.sync_report_specs(MagicMock(user_id="erin"), folders=["F::A"], cache_dir=str(tmp_path),
                                   index_consumers=False)
    assert report.skipped and "could not be read, so its specs are kept as cached" in report.skipped[0][1]
    assert not report.pruned


# ── egeria_folders.read_consumer_tree: the root ──────────────────────────────────────────────────────────────

def _tree(client):
    return folders.read_consumer_tree(client, root_qn="RootCollection::R", consumer_prefix="F::", key=lambda *a: None,
                                      fmt="t")


def test_root_unknown_is_not_read_with_the_reason():
    out = _tree(Unique(error=_failed()))
    assert out["status"] == "not read" and "could not be read: the unique-name read failed" in out["reason"]


def test_root_not_found_is_said():
    out = _tree(Unique())
    assert out["status"] == "not read" and "was not found, or is not visible to" in out["reason"]


# ── export_dcat._read_scope ──────────────────────────────────────────────────────────────────────────────────

def test_export_scope_by_qualified_name():
    try:
        from pyegeria.view import export_dcat as ed
    except ImportError:   # rdflib is an optional extra
        pytest.skip("rdflib not installed")
    coll = _el("c", "Coll::A", "Collection")
    assert ed._read_scope(Unique(coll), "Coll::A") is coll
    with pytest.raises(ValueError, match="no collection with qualifiedName 'Coll::A' is visible"):
        ed._read_scope(Unique(), "Coll::A")
    with pytest.raises(ValueError, match=r"'Coll::A' is a Asset"):
        ed._read_scope(Unique(_el("x", "Coll::A", "Asset")), "Coll::A")
    with pytest.raises(ValueError, match="couldn't tell whether a collection with qualifiedName 'Coll::A'"):
        ed._read_scope(Unique(error=_failed()), "Coll::A")


# ── egeria_spec_cache._find_specs_by_label: a label, paged ───────────────────────────────────────────────────

def _spec(guid, label):
    return {"elementHeader": {"guid": guid, "type": {"typeName": "ReportSpec"}},
            "properties": {"qualifiedName": f"Coco::ReportSpec::{label}", "displayName": label}}


class ByName:
    """A by-name search that pages like Egeria: `pages` per name, null after the last."""

    def __init__(self, pages_by_name=None, error_on=()):
        self.pages_by_name, self.error_on, self.calls = pages_by_name or {}, set(error_on), []
        self.user_id = "erin"

    def get_collections_by_name(self, name, metadata_element_type=None, output_format="JSON", start_from=0,
                                page_size=100, **_):
        self.calls.append((name, start_from, page_size))
        if name in self.error_on:
            raise RuntimeError("HTTP 503")
        pages = self.pages_by_name.get(name, [])
        i = start_from // page_size
        return pages[i] if i < len(pages) else NULL

    async def _async_get_collections_by_name(self, name, **kw):
        return self.get_collections_by_name(name, **kw)


def test_a_spec_after_a_filtered_page_is_found():
    client = ByName({"Trend": [[], [_spec("s1", "Trend")]]})
    assert [e["elementHeader"]["guid"] for e in esc._find_specs_by_label(client, "Trend")] == ["s1"]
    assert all(size == esc.SPEC_LOOKUP_PAGE for _, _, size in client.calls)


def test_none_found_without_a_confirmed_end_is_unconfirmed_not_not_found():
    with pytest.raises(esc.SpecLookupUnconfirmed, match="couldn't tell whether Egeria holds report spec 'Trend'"):
        esc._find_specs_by_label(ByName(), "Trend")   # NULL_NOT_END before #9453: a null isn't the end


def test_none_found_on_a_gated_platform_is_not_found(monkeypatch):
    monkeypatch.setattr(paging, "platform_fixes", lambda client: frozenset({paging.FIX_9453}))
    assert esc._find_specs_by_label(ByName(), "Trend") == []


def test_a_failed_name_never_reads_as_none():
    with pytest.raises(esc.SpecLookupUnconfirmed, match="the read failed"):
        esc._find_specs_by_label(ByName(error_on={"Trend", "ReportSpec::Trend", "ReportType::Trend"}), "Trend")
    # one failing name doesn't hide a match under another
    found = esc._find_specs_by_label(ByName({"ReportSpec::Trend": [[_spec("s2", "Trend")]]}, error_on={"Trend"}),
                                     "Trend")
    assert [e["elementHeader"]["guid"] for e in found] == ["s2"]


def test_async_twin():
    client = ByName({"Trend": [[], [_spec("s1", "Trend")]]})
    assert [e["elementHeader"]["guid"] for e in asyncio.run(esc._async_find_specs_by_label(client, "Trend"))] == ["s1"]
    with pytest.raises(esc.SpecLookupUnconfirmed):
        asyncio.run(esc._async_find_specs_by_label(ByName(), "Trend"))


def test_a_pinned_spec_lookup_that_cant_tell_is_skipped_with_words(tmp_path):
    report = esc.sync_report_specs(ByName(), specs=["Trend"], cache_dir=str(tmp_path), index_consumers=False)
    reasons = dict(report.skipped)
    assert "could not be looked up: couldn't tell" in reasons["Trend"]
    assert "not found in Egeria" not in reasons["Trend"]
