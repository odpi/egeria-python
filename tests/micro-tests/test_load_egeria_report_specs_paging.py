"""Pager step 6 (the load_egeria_report_specs ruling, 2026-11-14): the ReportType read pages past a filtered
(empty) page, and only a confirmed end marks the load done; an unconfirmed read keeps what it read and retries
after ~5 minutes, and "no ReportType found" is said only on a confirmed end."""
import pytest

from pyegeria.core import paging
from pyegeria.view import base_report_formats as brf

pytestmark = pytest.mark.unit

NULL = "No elements found"


@pytest.fixture(autouse=True)
def _fresh(monkeypatch):
    monkeypatch.setattr(brf, "_EGERIA_SPECS_LOADED_AT", None)
    monkeypatch.setattr(brf, "_EGERIA_SPECS_RETRY_AT", None)


def _rt(label):
    return {"elementHeader": {"guid": f"g-{label}"},
            "properties": {"qualifiedName": f"ReportType::{label}", "displayName": label}}


class _Client:
    def __init__(self, pages, error=None):
        self.pages, self.error, self.starts = pages, error, []

    def find_collections(self, search_string="*", _type=None, start_from=0, page_size=0, **kw):
        self.starts.append(start_from)
        if self.error:
            raise self.error
        return self.pages.get(start_from, NULL)

    def get_collection_members(self, guid, **kw):
        return []   # no QuestionSpec folders: nothing to merge, the read itself is what's tested


def _trusted(monkeypatch):
    monkeypatch.setattr(paging, "paging_for", lambda method, client=None: {"end_policy": "trusted"})


def test_a_filtered_empty_page_is_read_past(monkeypatch):
    _trusted(monkeypatch)
    client = _Client({0: [], 1000: [_rt("A"), _rt("B")]})   # [] (filtered), then the specs, then null
    assert brf.load_egeria_report_specs(client) is True
    assert client.starts == [0, 1000, 2000]                 # it used to stop at the first, empty page
    assert brf._EGERIA_SPECS_LOADED_AT is not None


def test_an_unconfirmed_read_is_not_marked_loaded_and_retries_later():
    client = _Client({0: [_rt("A")]})   # find_collections is a suspect path: the null isn't proof
    brf.load_egeria_report_specs(client)
    assert brf._EGERIA_SPECS_LOADED_AT is None and brf._EGERIA_SPECS_RETRY_AT is not None
    before = len(client.starts)
    assert brf.load_egeria_report_specs(client) is False    # within the retry window: no re-read
    assert len(client.starts) == before
    brf.load_egeria_report_specs(client, force=True)        # force reads again
    assert len(client.starts) > before


def test_an_unconfirmed_empty_read_is_never_cached_as_none():
    # not "no ReportType found": nothing is marked loaded, and the next load (after the retry window) reads again
    client = _Client({})
    assert brf.load_egeria_report_specs(client) is False
    assert brf._EGERIA_SPECS_LOADED_AT is None and brf._EGERIA_SPECS_RETRY_AT is not None


def test_a_confirmed_empty_read_is_loaded(monkeypatch):
    _trusted(monkeypatch)
    client = _Client({})
    assert brf.load_egeria_report_specs(client) is True     # "no ReportType found" is the answer
    assert brf._EGERIA_SPECS_LOADED_AT is not None and brf._EGERIA_SPECS_RETRY_AT is None


def test_an_exception_is_not_loaded():
    client = _Client({}, error=ConnectionError("down"))
    assert brf.load_egeria_report_specs(client) is False
    assert brf._EGERIA_SPECS_LOADED_AT is None and brf._EGERIA_SPECS_RETRY_AT is None
