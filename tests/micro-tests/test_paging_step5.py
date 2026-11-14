"""Pager step 5: every page_all call takes its paging from paging_for(method), so a NULL_NOT_END method can't
be paged with the plain suspect policy by accident (the Architect's step-4 read-back advisory)."""
import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
SOURCES = [p for d in ("pyegeria", "md_processing", "commands") for p in (ROOT / d).rglob("*.py")
           if p.name != "paging.py" and "deprecated" not in p.parts]   # commands/deprecated doesn't parse


def _pager_calls():
    for path in SOURCES:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", None)) in (
                    "page_all", "async_page_all"):
                yield path.relative_to(ROOT), node


def test_every_pager_call_takes_its_paging_from_paging_for():
    calls = list(_pager_calls())
    assert len(calls) >= 15   # the step 3/4 call sites
    for path, call in calls:
        assert not any(k.arg in ("end_policy", "probe_pages", "null_not_end") for k in call.keywords), (
            f"{path}:{call.lineno} sets its own paging; use **paging_for(method)")
        assert any(k.arg is None for k in call.keywords), (
            f"{path}:{call.lineno} takes no **paging_for(...) / **plan arguments")
