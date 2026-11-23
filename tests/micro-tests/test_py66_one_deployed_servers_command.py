"""PY-66: `hey_egeria show deployed-data deployed-servers` is registered once. click keeps the last registration of a
name, so a second copy silently replaced the first; commands/cli/egeria.py has more such copies (listed below) that
are not part of this item."""
import ast
import collections
import os

import click

import commands.cli.egeria as cli

SOURCE = os.path.join(os.path.dirname(cli.__file__), "egeria.py")

# (group variable, command name) registered more than once in commands/cli/egeria.py, other than deployed-servers.
# This list can only shrink: a new duplicate, or one fixed and left here, fails the test.
KNOWN_OTHER_DUPLICATES = {
    ("show_cat_info", "tech-types"), ("asset_group", "asset-graph"), ("show_project_group", "projects"),
    ("show_cat_info", "certification-types"), ("show_project_group", "project-structure"),
    ("show_project_group", "project-dependencies"), ("show_cat_info", "user-ids"),
    ("deployed_data", "deployed-schemas"), ("deployed_data", "catalogs"), ("deployed_data", "databases"),
}


def _registrations():
    tree = ast.parse(open(SOURCE).read())
    seen = collections.defaultdict(list)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            for d in node.decorator_list:
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "command":
                    name = d.args[0].value if d.args and isinstance(d.args[0], ast.Constant) else node.name
                    seen[(ast.unparse(d.func.value), name)].append(node.lineno)
    return seen


def test_deployed_servers_is_registered_once():
    assert len(_registrations()[("deployed_data", "deployed-servers")]) == 1


def test_no_new_duplicate_command_names():
    dups = {k for k, v in _registrations().items() if len(v) > 1}
    assert dups == KNOWN_OTHER_DUPLICATES, (sorted(dups - KNOWN_OTHER_DUPLICATES), sorted(KNOWN_OTHER_DUPLICATES - dups))


def test_the_one_command_keeps_the_view_server_default():
    group = cli.deployed_data
    command = group.get_command(click.Context(group), "deployed-servers")
    option = next(p for p in command.params if p.name == "search_string")
    assert option.default == "View Server"
