"""
PY-35: pyegeria has no built-in admin credentials either (PY-33 removed the mermaid_utilities pair; these were
the last two). md_processing.dr_egeria and md_processing_utils.common_md_utils read ADMIN_USER / ADMIN_PASSWORD
with no literal default: unset means None. No live server.
"""
import importlib
import sys

import pytest

MODULES = ["md_processing.dr_egeria", "md_processing.md_processing_utils.common_md_utils"]


def _fresh(name):
    sys.modules.pop(name, None)
    return importlib.import_module(name)


@pytest.mark.parametrize("name", MODULES)
def test_admin_credentials_have_no_default(monkeypatch, name):
    monkeypatch.delenv("ADMIN_USER", raising=False)
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    mod = _fresh(name)
    assert mod.EGERIA_ADMIN_USER is None
    assert mod.EGERIA_ADMIN_PASSWORD is None


@pytest.mark.parametrize("name", MODULES)
def test_admin_credentials_come_from_the_environment(monkeypatch, name):
    monkeypatch.setenv("ADMIN_USER", "an-admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "its-password")
    mod = _fresh(name)
    assert mod.EGERIA_ADMIN_USER == "an-admin"
    assert mod.EGERIA_ADMIN_PASSWORD == "its-password"


def test_no_literal_admin_default_left_in_pyegeria_sources():
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parents[2]
    pat = re.compile(r'os\.environ\.get\(\s*["\']ADMIN_(USER|PASSWORD)["\']\s*,')
    hits = [f"{p.relative_to(root)}:{i}" for d in ("pyegeria", "md_processing", "commands")
            for p in (root / d).rglob("*.py")
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1)
            if pat.search(line)]
    assert not hits, hits
