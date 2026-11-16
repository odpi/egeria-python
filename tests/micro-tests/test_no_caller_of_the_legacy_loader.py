"""The owner's direction (2026-11-14): pyegeria's own code is off the deprecated legacy ReportType:: loader
(load_egeria_report_specs, removed in the next release). Only its own module defines it; nothing in pyegeria,
md_processing or commands calls it. The load-report-specs command runs the spec cache's sync instead."""
import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]


def test_nothing_of_ours_calls_the_legacy_loader():
    callers = []
    for d in ("pyegeria", "md_processing", "commands"):
        for path in (ROOT / d).rglob("*.py"):
            if "deprecated" in path.parts or path.name == "base_report_formats.py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                name = getattr(node.func, "id", getattr(node.func, "attr", None)) if isinstance(node, ast.Call) \
                    else None
                if name == "load_egeria_report_specs":
                    callers.append(f"{path.relative_to(ROOT)}:{node.lineno}")
                if isinstance(node, ast.ImportFrom) and any(a.name == "load_egeria_report_specs" for a in node.names):
                    callers.append(f"{path.relative_to(ROOT)}:{node.lineno} (import)")
    assert callers == []


def test_the_command_runs_the_spec_cache_sync(monkeypatch):
    from commands.cat import load_report_specs as cli
    from pyegeria.view import egeria_spec_cache

    calls = []

    class Report:
        def render(self):
            return "synced"

    class Client:
        def __init__(self, *a, **kw):
            pass

        def create_egeria_bearer_token(self, *a):
            pass

        def close_session(self):
            calls.append("closed")

    monkeypatch.setattr(cli, "EgeriaTech", Client)
    monkeypatch.setattr(egeria_spec_cache, "sync_report_specs", lambda client, **kw: calls.append("sync") or Report())
    printed = []
    monkeypatch.setattr(cli.Console, "print", lambda self, *a, **kw: printed.append(" ".join(map(str, a))))
    cli._run(view_server="vs", view_url="https://x", user="u", user_pass="p", force=True)
    assert calls == ["sync", "closed"]
    assert printed[0] == cli.DEPRECATION_WORDS and "removed in the next release" in printed[0]
    assert any("ignored" in p for p in printed) and "synced" in printed
