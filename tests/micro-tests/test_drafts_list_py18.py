"""PY-18 (found by the D16 run on laz, 2026-11-15): EgeriaDraftStore.async_list listed an author's drafts with a
property search for ".*", which Egeria matches LITERALLY, so on a live server it listed no drafts (and prune, built
on it, removed none). It now lists by type with the author's zone as the filter.

Lesson the fakes here follow: an Egeria fake must copy Egeria's matching rules. A property value is matched as
text, never as a regular expression."""
import ast
import asyncio
from pathlib import Path

import pytest

from pyegeria.authoring.drafts import EgeriaDraftStore
from pyegeria.core import paging
from test_authoring_api import _DraftEgeria   # its property search matches literally, like Egeria

pytestmark = pytest.mark.unit

ERIN = "erinoverview"
REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh_gate(monkeypatch):
    paging._GATE_CACHE.clear()
    monkeypatch.delenv(paging.GATE_OVERRIDE_ENV, raising=False)
    yield
    paging._GATE_CACHE.clear()


def _list(eg, kind="report"):
    notes = []
    out = asyncio.run(EgeriaDraftStore(eg, eg.run).async_list(ERIN, kind, notes=notes))
    return out, notes


def test_the_old_dot_star_property_search_finds_nothing_on_a_literal_egeria():
    eg = _DraftEgeria()
    eg.hold("R::mine", "Mine", "Report", [ERIN], "2026-11-15T19:49:47Z")
    old = asyncio.run(eg.classification_manager._async_find_elements_by_property_value(
        ".*", ["qualifiedName"], metadata_element_type="Report", starts_with=False, governance_zone_filter=[ERIN],
        graph_query_depth=0, start_from=0, page_size=50))
    assert old == "No elements found"          # what laz answered the old async_list
    out, _ = _list(eg)
    assert [d["name"] for d in out] == ["Mine"]   # the by-type read lists it


def test_drafts_are_read_by_type_with_the_authors_zone():
    eg = _DraftEgeria()
    seen = []
    real = eg.classification_manager._async_get_elements

    async def spy(**kw):
        seen.append(kw)
        return await real(**kw)
    eg.classification_manager._async_get_elements = spy
    eg.hold("R::mine", "Mine", "Report", [ERIN], "2026-11-15T19:49:47Z")
    _list(eg)
    assert seen and all(k["metadata_element_type"] == "Report" and k["governance_zone_filter"] == [ERIN]
                        and k["page_size"] >= 25 for k in seen)


def test_only_an_exact_zone_is_a_private_draft_a_superset_is_noted():
    eg = _DraftEgeria()
    eg.hold("R::mine", "Mine", "Report", [ERIN], "2026-11-15T10:00:00Z")
    eg.hold("R::shared", "Shared", "Report", [ERIN, "peterprofile"], "2026-11-15T10:00:00Z")
    eg.hold("R::peter", "Peter's", "Report", ["peterprofile"], "2026-11-15T10:00:00Z")
    out, notes = _list(eg)
    assert [d["name"] for d in out] == ["Mine"] and out[0]["zones"] == [ERIN]
    assert any("zoned to you and others" in n and "R::shared" in n for n in notes)


def test_the_list_is_confirmed_on_a_gated_platform_and_at_least_otherwise():
    eg = _DraftEgeria(gated=True)          # 5deda38d: #9453, so the by-type read is trusted
    eg.hold("R::mine", "Mine", "Report", [ERIN], "2026-11-15T10:00:00Z")
    out, notes = _list(eg)
    assert len(out) == 1 and not any(n.startswith("Showing at least") for n in notes)
    old = _DraftEgeria(gated=False)        # before #9453: by-type is NULL_NOT_END, never a confirmed end
    old.hold("R::mine", "Mine", "Report", [ERIN], "2026-11-15T10:00:00Z")
    out, notes = _list(old)
    assert len(out) == 1 and any(n.startswith("Showing at least 1 report drafts") for n in notes)


def test_prune_sees_the_drafts_the_list_finds():
    eg = _DraftEgeria()
    eg.hold("R::old", "Old draft", "Report", [ERIN], "2026-09-01T10:00:00Z")
    out = EgeriaDraftStore(eg, eg.run).prune_drafts(ERIN)
    assert out["removed"] == ["report:Old draft"] and eg.deleted == ["g-Old draft"]


# ── the guard: no ".*" (or any regex) may reach a by-property-value call ──

def _regex_like(value: str) -> bool:
    return any(token in value for token in (".*", ".+", "^", "$", "[", "\\"))


def test_no_regex_reaches_a_by_property_value_call():
    """A by-property-value value is matched literally by Egeria, so a regex there matches nothing. (A
    search-string endpoint, e.g. asset_catalog's ".*", takes a regex and is not caught here.)"""
    offenders = []
    for root in ("pyegeria", "md_processing", "commands", "my_egeria"):
        for path in (REPO / root).rglob("*.py"):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError):
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "attr", None) or getattr(node.func, "id", None) or ""
                if not name.endswith("by_property_value"):
                    continue
                values = [node.args[0]] if node.args else []
                values += [k.value for k in node.keywords if k.arg == "property_value"]
                for v in values:
                    if isinstance(v, ast.Constant) and isinstance(v.value, str) and _regex_like(v.value):
                        offenders.append(f"{path.relative_to(REPO)}:{node.lineno} {name}({v.value!r})")
    assert offenders == [], offenders
