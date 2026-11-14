"""Dr.Egeria resolve_element_guid never folds a lookup error into "absent" (pager step 5, the exists-lookups
ruling, 6): a transport, auth or timeout error could make Create-or-Update create a duplicate."""
import asyncio
from typing import List

import pytest

from pyegeria.core._exceptions import PyegeriaException, PyegeriaNotFoundException

pytestmark = pytest.mark.unit


# ── Dr.Egeria: resolve_element_guid never folds an error into "absent" ──

class _ErrClient:
    def __init__(self, exc):
        self.exc = exc

    async def __async_get_guid__(self, *a, **kw):
        assert kw.get("strict_errors") is True   # the core read must raise real errors, not swallow them
        raise self.exc


def _processor(client):
    from md_processing.v2.processors import AsyncBaseCommandProcessor

    class P(AsyncBaseCommandProcessor):
        created: List[str] = []

        async def apply_changes(self) -> str:
            P.created.append(self.parsed_output["qualified_name"])
            return "created"
    return P


def _run(client):
    from md_processing.md_processing_utils.md_processing_constants import load_commands
    from md_processing.v2.dispatcher import V2Dispatcher
    from md_processing.v2.extraction import DrECommand
    load_commands()
    P = _processor(client)
    P.created = []
    d = V2Dispatcher(client)
    d.register("Create Project", P)
    cmd = DrECommand(verb="Create", object_type="Project", attributes={"Display Name": "Lookup Probe"},
                     raw_block="## Create Project\n### Display Name\nLookup Probe\n")
    [result] = asyncio.run(d.dispatch_batch([cmd], {"directive": "process"}))
    return result, P.created


@pytest.mark.parametrize("exc", [TimeoutError("slow"), ConnectionError("down"), PyegeriaException("401")])
def test_a_lookup_error_blocks_the_create(exc):
    result, created = _run(_ErrClient(exc))
    assert created == [] and result["status"] == "failure"
    assert "couldn't tell whether" in result["message"] and "nothing was created" in result["message"]


def test_egerias_not_found_still_creates():
    import httpx
    response = httpx.Response(404, json={"relatedHTTPCode": 404},
                              request=httpx.Request("POST", "https://localhost:9443/guid-by-unique-name"))
    nf = PyegeriaNotFoundException(response, {"caller method": "test"}, additional_info={})
    result, created = _run(_ErrClient(nf))
    assert result["status"] == "success" and len(created) == 1
