"""PY-17 (with PY-16's MCP part): a find run's count is "N" only on a confirmed end, else "at least N" with the
reason; the MCP report runs page a list format to their max rows (as preview does) and carry that count."""
import asyncio

import pytest

from pyegeria.core import mcp_adapter
from pyegeria.view.format_set_executor import END_REASONS_WORDS, result_count

pytestmark = pytest.mark.unit


# ── result_count: the helper the Portal and EA can reuse ──

def test_a_confirmed_end_is_a_total():
    assert result_count({"kind": "json", "data": [1, 2, 3], "end": "confirmed"}) == {
        "count": 3, "count_text": "3", "complete": True, "end": "confirmed", "reason": None}


@pytest.mark.parametrize("end", ["first_page", "not_confirmed", "capped", "stalled"])
def test_any_other_end_is_at_least_with_its_reason(end):
    c = result_count({"kind": "json", "data": [1, 2], "end": end})
    assert c["count_text"] == "at least 2" and c["complete"] is False and c["reason"] == END_REASONS_WORDS[end]


def test_the_results_own_notes_are_the_reason_when_it_has_them():
    c = result_count({"kind": "table", "rows": [{"a": 1}], "end": "not_confirmed",
                      "notes": ["Showing at least 1 rows: Egeria reported no more at position 25."]})
    assert c["count_text"] == "at least 1" and "position 25" in c["reason"]


def test_nothing_found_is_zero_only_on_a_confirmed_end():
    assert result_count({"kind": "empty", "end": "confirmed"})["count_text"] == "0"
    c = result_count({"kind": "empty", "end": "capped", "notes": ["nothing in the first 1000 positions; can't rule out more"]})
    assert c["count_text"] == "at least 0" and "can't rule out more" in c["reason"]


@pytest.mark.parametrize("result", [
    {"kind": "json", "data": [1]},                       # no end: not a paged find, no count claimed
    {"kind": "text", "mime": "text/markdown", "content": "x", "end": "first_page"},
    {"kind": "absent", "content": "not established"},
    {"kind": "json", "data": {"a": 1}, "end": "confirmed"},   # not rows
    "No elements found", None,
])
def test_no_count_is_claimed_for_what_isnt_a_counted_find(result):
    assert result_count(result) is None


# ── the MCP report runs ──

def test_the_mcp_tool_pages_to_its_max_rows_and_says_at_least(monkeypatch):
    seen = {}

    async def fake(report, client, output_format="DICT", params=None, page_to=None, **kw):
        seen.update(page_to=page_to, params=params)
        return {"kind": "json", "data": [{"g": 1}, {"g": 2}], "end": "first_page"}
    monkeypatch.setattr(mcp_adapter, "_async_run_report", fake)
    out = asyncio.run(mcp_adapter._async_run_report_tool(report="R", egeria_client=object(),
                                                         params={"search_string": "*", "page_size": 0}))
    assert seen["page_to"] == mcp_adapter.MCP_MAX_ROWS
    assert out["count"]["count_text"] == "at least 2" and out["count"]["reason"] == END_REASONS_WORDS["first_page"]
    assert out["data"] == [{"g": 1}, {"g": 2}] and out["end"] == "first_page"   # the result itself is unchanged


def test_the_mcp_tool_takes_page_size_as_its_max_rows_and_a_confirmed_total(monkeypatch):
    seen = {}

    async def fake(report, client, output_format="DICT", params=None, page_to=None, **kw):
        seen["page_to"] = page_to
        return {"kind": "json", "data": [{"g": 1}], "end": "confirmed"}
    monkeypatch.setattr(mcp_adapter, "_async_run_report", fake)
    out = asyncio.run(mcp_adapter._async_run_report_tool(report="R", egeria_client=object(), params={"page_size": 25}))
    assert seen["page_to"] == 25 and out["count"]["count_text"] == "1" and out["count"]["complete"] is True


def test_a_text_result_carries_no_count(monkeypatch):
    async def fake(report, client, output_format="DICT", params=None, page_to=None, **kw):
        return {"kind": "text", "mime": "text/markdown", "content": "# R"}
    monkeypatch.setattr(mcp_adapter, "_async_run_report", fake)
    out = asyncio.run(mcp_adapter._async_run_report_tool(report="R", egeria_client=object(), output_format="REPORT"))
    assert "count" not in out


@pytest.mark.parametrize("entry", ["run_report", "_execute_egeria_call_blocking"])
def test_the_sync_mcp_entry_points_page_and_count_too(monkeypatch, entry):
    seen = {}

    def fake(**kw):
        seen.update(kw)
        return {"kind": "json", "data": [1, 2, 3], "end": "capped"}
    monkeypatch.setattr(mcp_adapter, "exec_report_spec", fake)
    out = getattr(mcp_adapter, entry)(report="R", params={"page_size": 3}, view_server="v", view_url="u",
                                      user="erinoverview", user_pass="x")
    assert seen["page_to"] == 3 and out["count"]["count_text"] == "at least 3"
