"""PY-36: every Python file under commands/ must parse.

Two scripts in commands/deprecated had syntax errors for a long time because nothing imports or runs them,
so nothing noticed. Parsing (not importing) keeps this free of side effects and of the scripts' dependencies.
"""
import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

COMMANDS = Path(__file__).resolve().parents[2] / "commands"


def test_every_python_file_under_commands_parses():
    broken = []
    for path in sorted(COMMANDS.rglob("*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            broken.append(f"{path.relative_to(COMMANDS.parent)}:{exc.lineno}: {exc.msg}")
    assert broken == []


def test_the_scan_sees_the_commands_tree():
    assert len(list(COMMANDS.rglob("*.py"))) > 50
