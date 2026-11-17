"""Pager step 3, ruling (A): every find run carries result["end"]; a first page that shows nothing is paged on
for list formats; text formats say "nothing in the first N positions; can't rule out more"; preview pages fully.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core._server_client import LIST_REQUEST_RECORD
from pyegeria.view import format_set_executor as fse

pytestmark = pytest.mark.unit

ROW = lambda n: {"GUID": f"g{n}", "Display Name": f"Risk {n}"}  # noqa: E731 -- a DICT-formatted row


class FakeClient:
    """A find method the executor resolves to. `pages` maps startFrom to what Egeria sent: a list of rows,
    [] (a filtered page, which the method collapses to "No elements found", as the real ones do) or absent
    (null). It records "page" as pyegeria's list helpers do."""
    pages: dict = {}
    calls: list = []

    def __init__(self, *a, **kw):
        pass

    def set_bearer_token(self, token):
        pass

    def create_egeria_bearer_token(self):
        pass

    def close_session(self):
        pass

    def _answer(self, start_from, page_size):
        FakeClient.calls.append((start_from, page_size))
        sent = FakeClient.pages.get(start_from)
        record = LIST_REQUEST_RECORD.get()
        if record is not None:
            record["page"] = "null" if sent is None else "empty" if not sent else "rows"
        return sent if sent else NO_ELEMENTS_FOUND

    def find_things(self, search_string="*", start_from=0, page_size=100, output_format="JSON",
                    report_spec=None, **kwargs):
        return self._answer(start_from, page_size)

    # a trusted path, by name (TRUSTED_END_METHODS)
    def find_authored_elements(self, search_string="*", start_from=0, page_size=100, output_format="JSON",
                               report_spec=None, **kwargs):
        return self._answer(start_from, page_size)


@pytest.fixture
def server(monkeypatch):
    def use(method, pages):
        FakeClient.pages, FakeClient.calls = pages, []
        monkeypatch.setattr(fse, "_resolve_client_and_method", lambda decl: (FakeClient, method))
        return FakeClient
    return use


def run(fmt="DICT", **kw):
    return fse.exec_report_spec("Risk-DrE-Basic", output_format=fmt, params={"search_string": "Risk::"},
                                view_server="vs", view_url="https://localhost:1", user="u", user_pass="", token="t",
                                **kw)


# ── list formats: a first page that shows nothing is paged on ──

def test_filtered_first_page_is_paged_on_suspect(server):
    srv = server("find_things", {0: [], 100: [ROW(1), ROW(2)]})
    r = run("DICT")
    assert r["kind"] == "json" and [x["GUID"] for x in r["data"]] == ["g1", "g2"]
    assert r["end"] == "not_confirmed"                       # suspect: the nulls after g2 aren't proof
    assert r["notes"][0].startswith("Showing at least 2 rows")
    assert [s for s, _ in srv.calls] == [0, 100, 200, 300, 400, 500]


def test_filtered_first_page_is_paged_on_trusted(server):
    srv = server("find_authored_elements", {0: [], 100: [], 200: [ROW(1)]})
    r = run("DICT")
    assert [x["GUID"] for x in r["data"]] == ["g1"] and r["end"] == "confirmed" and "notes" not in r
    assert [s for s, _ in srv.calls] == [0, 100, 200, 300]


def test_trusted_null_first_page_is_a_confirmed_empty(server):
    srv = server("find_authored_elements", {})
    r = run("DICT")
    assert r["kind"] == "empty" and r["end"] == "confirmed" and "notes" not in r
    assert srv.calls == [(0, 100)]


def test_suspect_null_first_page_probes_and_never_says_found_nothing(server):
    srv = server("find_things", {})
    r = run("DICT")
    assert r["kind"] == "empty" and r["end"] == "not_confirmed"
    assert r["notes"] == ["nothing in the first 500 positions; can't rule out more"]
    assert [s for s, _ in srv.calls] == [0, 100, 200, 300, 400]


def test_suspect_null_then_a_probe_finds_rows(server):
    # B5's shape: null for the filtered page at 0, the live element on the next page.
    server("find_things", {100: [ROW(7)]})
    r = run("TABLE", table_shape="structured")
    assert r["kind"] == "table" and r["end"] == "not_confirmed"


def test_rows_on_the_first_page_are_not_paged_and_end_first_page(server):
    srv = server("find_things", {0: [ROW(1)], 100: [ROW(2)]})
    r = run("DICT")
    assert [x["GUID"] for x in r["data"]] == ["g1"]
    assert r["end"] == "first_page" and "notes" not in r      # structured only: no words added
    assert srv.calls == [(0, 100)]


# ── the cost of paging on (step-3 read-back, REQUIRED 1) ──

def run25(fmt="DICT"):
    return fse.exec_report_spec("Risk-DrE-Basic", output_format=fmt,
                                params={"search_string": "Risk::", "page_size": 25}, view_server="vs",
                                view_url="https://localhost:1", user="u", user_pass="", token="t")


def test_all_filtered_at_size_25_costs_at_most_eleven_requests(server):
    srv = server("find_things", {n: [] for n in range(0, 5000, 25)})
    r = run25()
    assert r["kind"] == "empty" and r["end"] == "capped"
    assert r["notes"] == ["nothing in the first 1025 positions; can't rule out more"]
    assert srv.calls == [(0, 25)] + [(25 + 100 * i, 100) for i in range(fse.AFTER_EMPTY_MAX_PAGES)]
    assert len(srv.calls) == 11


def test_suspect_null_at_size_25_costs_five_requests(server):
    srv = server("find_things", {})
    r = run25()
    assert r["kind"] == "empty" and r["end"] == "not_confirmed"
    assert srv.calls == [(0, 25), (25, 100), (125, 100), (225, 100), (325, 100)]


def test_paging_on_at_size_25_still_returns_at_most_the_tile_size(server):
    srv = server("find_things", {0: [], 25: [ROW(n) for n in range(100)]})
    r = run25()
    assert len(r["data"]) == 25 and r["end"] == "capped"
    assert srv.calls == [(0, 25), (25, 100)]


# ── text formats: first page only, and the exact words ──

@pytest.mark.parametrize("fmt", ["REPORT", "MD", "LIST", "FORM", "HTML", "MERMAID"])
def test_text_format_nothing_says_the_positions_read(server, fmt):
    srv = server("find_things", {0: [], 100: [ROW(1)]})
    r = run(fmt)
    assert r["kind"] == "empty" and r["end"] == "not_confirmed"
    assert r["notes"] == ["nothing in the first 100 positions; can't rule out more"]
    assert srv.calls == [(0, 100)]


def test_text_format_trusted_null_is_confirmed(server):
    server("find_authored_elements", {})
    r = run("REPORT")
    assert r == {**r, "kind": "empty", "end": "confirmed"} and "notes" not in r


# ── page_to: preview pages fully ──

def test_page_to_pages_fully_up_to_the_rows_asked_for(server):
    srv = server("find_authored_elements", {0: [], 100: [ROW(1)], 200: [ROW(2), ROW(3)]})
    r = run("DICT", page_to=2)
    assert [x["GUID"] for x in r["data"]] == ["g1", "g2"] and r["end"] == "capped"
    assert {size for _, size in srv.calls} == {100}


def test_page_to_with_fewer_rows_ends_confirmed_on_a_trusted_path(server):
    server("find_authored_elements", {0: [ROW(1)]})
    r = run("DICT", page_to=25)
    assert [x["GUID"] for x in r["data"]] == ["g1"] and r["end"] == "confirmed"


def test_page_to_is_refused_unless_a_whole_number(server):
    server("find_things", {})
    with pytest.raises(ValueError):
        run("DICT", page_to=0)


# ── preview reads end ──

def test_preview_cap_never_says_found_nothing_unless_confirmed():
    _cap = __import__("importlib").import_module("pyegeria.authoring.preview")._cap
    notes = []
    out = _cap({"kind": "empty", "end": "not_confirmed",
                "notes": ["nothing in the first 500 positions; can't rule out more"]}, 25, notes)
    assert out["end"] == "not_confirmed" and "ran, and found nothing" not in notes
    assert notes == ["nothing in the first 500 positions; can't rule out more"]
    notes = []
    _cap({"kind": "empty", "end": "confirmed"}, 25, notes)
    assert notes == ["ran, and found nothing"]


def test_preview_cap_says_may_be_more_when_the_end_is_not_reached():
    _cap = __import__("importlib").import_module("pyegeria.authoring.preview")._cap
    notes = []
    out = _cap({"kind": "json", "data": [ROW(1)], "end": "first_page"}, 25, notes)
    assert out["capped"] is True and out["shown"] == 1
    assert notes == ["1 rows shown; Egeria didn't confirm there are no more"]
    notes = []
    out = _cap({"kind": "json", "data": [ROW(1)], "end": "confirmed"}, 25, notes)
    assert out["capped"] is False and notes == []


def test_preview_run_asks_the_executor_to_page_fully(monkeypatch):
    import asyncio
    from types import SimpleNamespace

    import importlib
    preview = importlib.import_module("pyegeria.authoring.preview")   # the package exports a preview() too
    seen = {}

    def fake_exec(spec, **kw):
        seen.update(kw)
        return {"kind": "json", "data": [ROW(1)], "end": "confirmed"}

    monkeypatch.setattr(fse, "exec_report_spec", fake_exec)
    monkeypatch.setattr(preview, "run_dict", lambda label, fs, out: {"name": label})
    client = SimpleNamespace(server_name="vs", platform_url="https://localhost:1", user_id="u", user_pwd="",
                             token="t")
    out = asyncio.run(preview._run("Draft", object(), client, "TABLE", {}, 25, []))
    assert seen["page_to"] == 25 and seen["params"]["page_size"] == 25
    assert out["end"] == "confirmed" and out["capped"] is False


# ── the golden tiles: every run carries end, and it is first_page (rows, not paged) ──

_spec = importlib.util.spec_from_file_location("report_fixture_replay",
                                               Path(__file__).parent / "report_fixture_replay.py")
replay_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(replay_mod)


GOLDEN_CASES = sorted(json.loads((Path(__file__).parent / "data" / "report_specs" /
                                  "golden_default_outputs.json").read_text()))


#: The one golden that is an error, not a run: Digital-Products offers no MD format.
GOLDEN_ERRORS = {"digital_products/MD"}


@pytest.mark.parametrize("case", [c for c in GOLDEN_CASES if c not in GOLDEN_ERRORS])
def test_golden_tiles_end_is_pinned(monkeypatch, case):
    # Ruling (A), condition 3: every golden run is a first page WITH rows, read once: first_page.
    tile, fmt = case.split("/")
    replay = replay_mod.ReportReplay(monkeypatch, tile)
    r = replay.run(fmt)
    assert r["end"] == "first_page", (case, r.get("end"))
    assert len(replay.requests) == 1   # the one recorded find: no extra request for any golden tile
