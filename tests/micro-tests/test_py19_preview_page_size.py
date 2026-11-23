"""PY-19: a preview (page_to=N) asks Egeria only for the rows it shows: the first request is min(N, the default
fetch size), not always the default (100). Paging contract unchanged: a short page is not the last page, only a
null is, and the read stops once N rows are in. A full read (no page_to) is untouched."""
import asyncio

import pytest

from pyegeria.core.paging import DEFAULT_FETCH_PAGE_SIZE, async_page_all, page_all, paging_for
from pyegeria.view import format_set_executor as fse


def _plan(page_to, listed=True):
    return {"page_to": page_to, "list": listed, "start": 0, "size": 25, "policy": "suspect",
            "paging": paging_for(None, None)}


@pytest.mark.parametrize("page_to,size", [(1, 1), (25, 25), (99, 99), (100, 100), (101, 100), (250, 100), (5000, 100)])
def test_the_first_request_is_the_smaller_of_the_preview_and_the_default(page_to, size):
    full = fse._full_read(_plan(page_to))
    assert full["fetch_page_size"] == size and full["want"] == page_to


def test_a_full_read_and_a_non_list_are_untouched():
    assert fse._full_read(_plan(None)) is None
    assert fse._full_read(_plan(25, listed=False)) is None


class _Rows:
    """A fake Egeria: `rows` rows in all; `short` makes the first page return fewer than asked (filtered)."""
    def __init__(self, rows, short=None):
        self.rows, self.short, self.calls = rows, short, []

    def __call__(self, start, size):
        self.calls.append((start, size))
        page = [f"r{i}" for i in range(start, min(start + size, self.rows))]
        if self.short is not None and len(self.calls) == 1:
            page = page[: self.short]
        return page or None


def test_a_25_row_preview_sends_one_request_of_25():
    fake = _Rows(1000)
    got = page_all(fake, **fse._full_read(_plan(25)))
    assert fake.calls == [(0, 25)] and len(got.items) == 25


def test_a_preview_larger_than_the_default_pages_at_100_up_to_max_rows():
    fake = _Rows(1000)
    got = page_all(fake, **fse._full_read(_plan(250)))
    assert fake.calls == [(0, 100), (100, 100), (200, 100)] and len(got.items) == 250   # one page past, at most


def test_a_short_first_page_still_pages_on_and_stops_at_max_rows():
    fake = _Rows(1000, short=10)
    got = page_all(fake, **fse._full_read(_plan(25)))
    assert fake.calls[:2] == [(0, 25), (25, 25)]                      # a short page is not the last page
    assert len(got.items) == 25 and got.end == "capped"               # and it stops at the rows asked for


def test_a_null_is_the_only_end_and_a_short_dataset_does_not_over_ask():
    fake = _Rows(12)
    got = page_all(fake, **fse._full_read(_plan(25)))
    assert fake.calls[0] == (0, 25) and len(got.items) == 12


def test_the_async_driver_takes_the_same_arguments():
    fake = _Rows(1000)

    async def fetch(start, size):
        return fake(start, size)
    got = asyncio.run(async_page_all(fetch, **fse._full_read(_plan(25))))
    assert fake.calls == [(0, 25)] and len(got.items) == 25


def test_the_default_is_still_100():
    assert DEFAULT_FETCH_PAGE_SIZE == 100


def test_an_empty_filtered_page_does_not_end_the_preview():
    rows = {0: [], 25: ["a", "b"], 50: None}
    calls = []

    def fetch(start, size):
        calls.append((start, size))
        return rows.get(start)
    got = page_all(fetch, **fse._full_read(_plan(25)))
    assert calls[:2] == [(0, 25), (25, 25)] and got.items == ["a", "b"]


def test_a_preview_reads_at_most_one_page_past_max_rows():
    fake = _Rows(1000)
    page_all(fake, **fse._full_read(_plan(130)))
    assert fake.calls == [(0, 100), (100, 100)]          # 200 positions for 130 rows: under one page over


class _Filtered:
    """24 visible rows, then `filtered` positions Egeria returns as empty (zone-filtered) pages, then the end."""
    def __init__(self, filtered):
        self.filtered, self.calls = filtered, []

    def __call__(self, start, size):
        self.calls.append((start, size))
        visible = [f"r{i}" for i in range(start, min(start + size, 24))]
        if visible:
            return visible
        return [] if start < 24 + self.filtered else None


def test_filtered_positions_after_the_rows_cost_a_bounded_number_of_requests():
    fake = _Filtered(500)
    got = page_all(fake, **fse._full_read(_plan(25)))
    assert len(fake.calls) <= 30 and {size for _, size in fake.calls} == {25}   # not hundreds of one-row requests
    assert len(got.items) == 24


def test_a_long_filtered_run_ends_at_the_empty_run_cap_in_bounded_requests():
    fake = _Filtered(3000)
    got = page_all(fake, **fse._full_read(_plan(25)))
    assert got.end_reason == "empty_run_cap" and not got.complete
    assert len(fake.calls) <= 90 and {size for _, size in fake.calls} == {25}


def test_the_result_tells_stopped_at_max_rows_from_everything():
    stopped = page_all(_Rows(1000), **fse._full_read(_plan(25)))
    assert stopped.end == "capped" and stopped.end_reason == "want" and not stopped.complete
    assert "25 rows asked for" in stopped.note
    everything = page_all(_Rows(12), **fse._full_read(_plan(25)))
    assert len(everything.items) == 12 and everything.end_reason in ("trusted_null", "null_then_empty_probes")
