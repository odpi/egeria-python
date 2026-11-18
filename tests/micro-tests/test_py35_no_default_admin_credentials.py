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


def test_no_built_in_password_default_in_pyegeria_or_md_processing():
    """PY-35 W2: no literal password default, in any form, in pyegeria/ or md_processing/: a class field or
    parameter default (`user_pwd: ... = "secret"`) or an env read with a literal fallback for a *PASSWORD* or
    *_PWD name. commands/ (the CLIs' own EGERIA_USER_PASSWORD defaults, 79 live ones) is a separate decision."""
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parents[2]
    default = re.compile(r'\b(user_pwd|password|pwd|user_pass|admin_password)\b\s*(:[^=,]+)?=\s*["\'][^"\']+["\']')
    env = re.compile(r'(environ\.get|getenv)\(\s*["\'][A-Z_]*(PASSWORD|PWD)[A-Z_]*["\']\s*,\s*["\'][^"\']+["\']')
    hits = []
    for d in ("pyegeria", "md_processing"):
        for p in (root / d).rglob("*.py"):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                code = line.split("#", 1)[0]
                if default.search(code) or env.search(code):
                    hits.append(f"{p.relative_to(root)}:{i}: {line.strip()[:80]}")
    assert not hits, hits


def test_the_scan_catches_a_class_default_and_skips_the_next_parameter():
    import re
    default = re.compile(r'\b(user_pwd|password|pwd|user_pass|admin_password)\b\s*(:[^=,]+)?=\s*["\'][^"\']+["\']')
    assert default.search('    user_pwd: Optional[str] = "secret"')
    assert default.search('def f(user_pwd: str = "secret"):')
    assert not default.search('def f(user_pass: str, parse_summary: str = "none"):')


def test_the_user_profile_model_has_no_default_password():
    from pyegeria.core.config import UserProfileConfig
    assert UserProfileConfig().user_pwd is None
