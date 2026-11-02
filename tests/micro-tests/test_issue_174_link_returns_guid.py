# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""
ISSUE-174: link_*/attach_*/setup_* methods must return the new relationship's
GUID.

``ServerClient._async_new_relationship_request`` returns the GUID from the
server's ``GUIDResponse``, but 142 of its callers in ``pyegeria/omvs`` used to
call it as a bare ``await`` and return None, and so did their sync wrappers.
Resource Explorer had to re-read each schema after
``AssetMaker.link_data_set_content`` to learn the DataSetContent relationship's
GUID. That matters most for multi-link types, where update and detach need
the GUID of the specific instance.

Two checks:
  - an AST guard: no method in ``pyegeria/omvs`` drops the result of the
    helper, or of any method that (transitively) returns it, and no sync
    wrapper drops the result of such an async method;
  - a sample of real methods, async and sync, across several clients, return
    the GUID the stubbed server sends back.

No live server needed: ``_async_make_request`` is stubbed.
"""
import ast
import pathlib

import pytest

from pyegeria.omvs.asset_maker import AssetMaker
from pyegeria.omvs.classification_explorer import ClassificationExplorer
from pyegeria.omvs.connection_maker import ConnectionMaker
from pyegeria.omvs.data_designer import DataDesigner
from pyegeria.omvs.governance_officer import GovernanceOfficer
from pyegeria.omvs.schema_maker import SchemaMaker
from pyegeria.omvs.solution_architect import SolutionArchitect

HELPER = "_async_new_relationship_request"
OMVS_DIR = pathlib.Path(__file__).resolve().parents[2] / "pyegeria" / "omvs"
REL_GUID = "new-relationship-guid-0174"


# ---------------------------------------------------------------- AST guard

def _self_call_name(node):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
        return node.func.attr
    return None


def _returning_methods(funcs):
    """Names of async methods that return the helper's result, transitively."""
    returning = {HELPER}
    changed = True
    while changed:
        changed = False
        for fn in funcs:
            if not isinstance(fn, ast.AsyncFunctionDef) or fn.name in returning:
                continue
            for node in ast.walk(fn):
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Await) \
                        and _self_call_name(node.value.value) in returning:
                    returning.add(fn.name)
                    changed = True
                    break
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Await) \
                        and _self_call_name(node.value.value) in returning:
                    # e.g. relationship_guid = await self._async_new_relationship_request(...)
                    returning.add(fn.name)
                    changed = True
                    break
    return returning


def _discards(path):
    tree = ast.parse(path.read_text())
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    returning = _returning_methods(funcs)
    found = []
    for fn in funcs:
        for node in ast.walk(fn):
            if not isinstance(node, ast.Expr):
                continue
            value = node.value
            if isinstance(value, ast.Await) and _self_call_name(value.value) in returning:
                found.append(f"{path.name}:{node.lineno} {fn.name} awaits "
                             f"{_self_call_name(value.value)} and drops the GUID")
            elif isinstance(value, ast.Call) and not isinstance(fn, ast.AsyncFunctionDef):
                for arg in value.args:
                    if _self_call_name(arg) in returning:
                        found.append(f"{path.name}:{node.lineno} {fn.name} runs "
                                     f"{_self_call_name(arg)} and drops the GUID")
    return found


def test_no_omvs_method_discards_the_relationship_guid():
    found = []
    for path in sorted(OMVS_DIR.glob("*.py")):
        found.extend(_discards(path))
    assert not found, "Methods that drop the new relationship GUID:\n" + "\n".join(found)


def test_guard_catches_a_discarding_method(tmp_path):
    bad = tmp_path / "bad.py"
    bad.write_text(
        "class C:\n"
        "    async def _async_link_x(self, url):\n"
        f"        await self.{HELPER}(url)\n"
        "    async def _async_link_y(self, url):\n"
        f"        return await self.{HELPER}(url)\n"
        "    def link_y(self, url):\n"
        "        run_sync(self._async_link_y(url))\n"
    )
    found = _discards(bad)
    assert len(found) == 2
    assert "_async_link_x" in found[0] and "link_y" in found[1]


# ---------------------------------------------------------- live-shaped sample

class _Response:
    def json(self):
        return {"class": "GUIDResponse", "relatedHTTPCode": 200, "guid": REL_GUID}


def _client(cls, monkeypatch):
    monkeypatch.setattr(cls, "check_connection", lambda self: "test")
    client = cls("view-server", "https://localhost:1", "user", "pwd")
    calls = []

    async def fake_make_request(method, url, body=None, *args, **kwargs):
        calls.append((method, url))
        return _Response()

    client._async_make_request = fake_make_request
    client._calls = calls
    return client


SYNC_CASES = [
    (AssetMaker, "link_data_set_content", ("data-set-guid", "content-guid")),
    (SchemaMaker, "link_nested_schema_attribute", ("parent-guid", "child-guid")),
    (SchemaMaker, "link_attribute_for_schema", ("schema-type-guid", "attribute-guid")),
    (DataDesigner, "link_member_data_field", ("struct-guid", "field-guid")),
    (GovernanceOfficer, "link_peer_definitions", ("def-guid-1", "GovernanceDriverLink", "def-guid-2")),
    (ClassificationExplorer, "add_scope_to_element", ("scope-guid", "element-guid")),
    (SolutionArchitect, "link_subcomponent", ("component-guid", "sub-guid", None)),
    (ConnectionMaker, "link_connection_endpoint", ("connection-guid", "endpoint-guid")),
]


@pytest.mark.parametrize("cls,method,args", SYNC_CASES, ids=[c[1] for c in SYNC_CASES])
def test_sync_link_methods_return_the_relationship_guid(cls, method, args, monkeypatch):
    client = _client(cls, monkeypatch)
    assert getattr(client, method)(*args) == REL_GUID
    assert client._calls and client._calls[0][0] == "POST"


@pytest.mark.parametrize("cls,method,args", SYNC_CASES, ids=[c[1] for c in SYNC_CASES])
async def test_async_link_methods_return_the_relationship_guid(cls, method, args, monkeypatch):
    client = _client(cls, monkeypatch)
    assert await getattr(client, f"_async_{method}")(*args) == REL_GUID
