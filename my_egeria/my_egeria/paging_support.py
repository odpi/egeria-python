"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Egeria's paging contract, as My Profile's handlers use it.

   A list from Egeria is one page of matches; an empty list means that page was filtered empty (keep
   paging); only null means there are no more, and on some paths not even that. So a handler never treats
   one page as the whole set, and never says "none" or a total unless the read reached a confirmed end.

   - ``read_all`` pages a list call through pyegeria's pager and returns ``PagedRows``: a plain list (so
     callers and screens are unchanged) that also says whether the read was complete, and the
     "at least N" words to show when it wasn't.
   - ``lookup`` / ``async_lookup`` answer "does Egeria already hold X?" three ways (found / absent /
     unknown) for a write guard: create only on absent; on unknown, refuse (``refusal``) and write nothing.
   - ``none_words`` is the empty-state text: "No X" only after a confirmed end.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Iterable

from pyegeria.core.paging import (PageResult, Exists, async_exists, async_page_all, async_paging_for, at_least_note,
                                  exists, page_all, paging_for)

#: Requests per read for a display list: 20 pages of 100 rows. Past it the list says "at least".
DISPLAY_MAX_PAGES = 20
NOT_CONFIRMED = "Egeria didn't confirm there are no more"


class LookupUnconfirmed(ValueError):
    """A write guard couldn't tell whether the thing it would create already exists; nothing was written.
    The message is the ``refusal`` words."""


class PagedRows(list):
    """The rows a handler shows, plus how the read that produced them ended. Two levels, as pyegeria's
    PageResult has them:

    - ``reached_end``: the read got to Egeria's end (a trusted null, or a null then empty probes), so the
      rows may be shown as the list, with no "at least". Otherwise ``note`` holds the "Showing at least N
      ..." words to show beside them.
    - ``complete``: Egeria *confirmed* there are no more (a trusted path). Only then may an empty list say
      "none" (``none_words``); a reached-but-unconfirmed empty read says "none found in what Egeria
      returned"."""

    def __init__(self, rows: Iterable[Any] = (), *, complete: bool = True, reached_end: bool | None = None,
                 note: str | None = None):
        super().__init__(rows)
        self.complete = complete
        self.reached_end = complete if reached_end is None else (reached_end or complete)
        self.note = note


def paged_rows(rows: Iterable[Any], read: PageResult | None, what: str) -> PagedRows:
    """``rows`` (built from ``read.items``) as PagedRows: the "at least" note when the read didn't reach
    Egeria's end. ``read`` None means the rows needed no read (complete)."""
    rows = list(rows)
    if read is None or read.complete:
        return PagedRows(rows, complete=True)
    if read.reached_end:
        return PagedRows(rows, complete=False, reached_end=True)
    return PagedRows(rows, complete=False, reached_end=False, note=at_least_note(read, what, count=len(rows)))


def is_complete(rows: Any) -> bool:
    """Whether Egeria confirmed a handler's rows are the whole set, so an empty one may say "none" (a plain
    list from an unpaged source counts as confirmed)."""
    return getattr(rows, "complete", True)


def reached_end(rows: Any) -> bool:
    """Whether a handler's rows may be shown as the list (no "at least")."""
    return getattr(rows, "reached_end", True)


def combine(*reads: Any) -> bool:
    """True only when every read (PageResult or PagedRows) reached Egeria's end."""
    return all(getattr(r, "reached_end", True) for r in reads)


def count_text(rows: Any) -> str:
    """The count of a handler's rows as it may be shown: "N", or "at least N" short of Egeria's end."""
    return str(len(rows)) if reached_end(rows) else f"at least {len(rows)}"


def none_words(what: str, complete: bool, matching: str | None = None) -> str:
    """The empty-state text: "No <what>" only after a confirmed end, else "none found in what Egeria
    returned"."""
    suffix = f" matching {matching}" if matching else ""
    if complete:
        return f"No {what} found{suffix}"
    return f"No {what} found{suffix} in what Egeria returned; {NOT_CONFIRMED}"


def report_end_complete(result: Any) -> bool:
    """Whether an ``exec_report_spec`` result reached a confirmed end. Its ``end`` is "confirmed" only then;
    an older executor (no ``end``) counts as unconfirmed for an empty result."""
    return isinstance(result, dict) and result.get("end") == "confirmed"


def report_empty_words(what: str, result: Any, matching: str | None = None) -> str:
    """Empty-state text for an ``exec_report_spec`` result that has no rows."""
    return none_words(what, report_end_complete(result), matching)


def report_empty_cells(what: str, result: Any) -> tuple[str, str]:
    """(headline, detail) for the placeholder row of a table whose ``exec_report_spec`` read showed no rows.

    Three different things, said differently: the read failed (``result`` isn't the executor's dict: the
    handlers store a sentinel list or an error string then), Egeria confirmed there are none, or the read
    stopped without that confirmation."""
    if not isinstance(result, dict):
        detail = result if isinstance(result, str) and result else "the read failed; see the log"
        return f"Couldn't retrieve {what} from Egeria", detail
    if report_end_complete(result):
        return f"No {what} found", "Egeria confirmed there are none"
    notes = result.get("notes") or []
    detail = "; ".join(str(n) for n in notes) if notes else NOT_CONFIRMED
    return f"No {what} found in what Egeria returned", detail


def read_all(fetch: Callable[[int, int], Any], *, method: str, client: Any = None,
             max_pages: int = DISPLAY_MAX_PAGES, **kwargs) -> PageResult:
    """Every row ``fetch(start, size)`` returns, paged per Egeria's contract for ``method``."""
    return page_all(fetch, max_pages=max_pages, **kwargs, **paging_for(method, client))


async def async_read_all(fetch: Callable[[int, int], Awaitable[Any]], *, method: str, client: Any = None,
                         max_pages: int = DISPLAY_MAX_PAGES, **kwargs) -> PageResult:
    """``read_all`` for an async ``fetch``."""
    return await async_page_all(fetch, max_pages=max_pages, **kwargs, **(await async_paging_for(method, client)))


def lookup(fetch: Callable[[int, int], Any], match: Callable[[Any], bool], *, method: str,
           client: Any = None, **kwargs) -> Exists:
    """found / absent / unknown: whether a row satisfying ``match`` (exact, client-side) is in what
    ``fetch`` pages to. Use only where one match decides the outcome."""
    return exists(fetch, match, method=method, client=client, **kwargs)


async def async_lookup(fetch: Callable[[int, int], Awaitable[Any]], match: Callable[[Any], bool], *, method: str,
                       client: Any = None, **kwargs) -> Exists:
    """``lookup`` for an async ``fetch``."""
    return await async_exists(fetch, match, method=method, client=client, **kwargs)


def refusal(what: str, found: Exists, action: str = "Nothing was created") -> str:
    """The words a write guard shows when it can't tell whether ``what`` already exists."""
    read = found.read
    return (f"Couldn't confirm whether Egeria already holds {what}: it didn't confirm there are no more "
            f"({read.positions_read} positions read, {read.end_reason or read.end}). {action}; try again later.")


def element_qn(element: Any) -> str:
    """An Egeria 6 element's qualifiedName ('' when it has none)."""
    if not isinstance(element, dict):
        return ""
    return str((element.get("properties") or {}).get("qualifiedName") or "")


def element_guid(element: Any) -> str:
    """An Egeria 6 element's GUID ('' when it has none)."""
    if not isinstance(element, dict):
        return ""
    return str((element.get("elementHeader") or {}).get("guid") or "")
