"""PY-63 S2: `hey_egeria ... deployed-servers` defaults to a type Egeria accepts, not "*"."""
import inspect
from types import SimpleNamespace
from unittest.mock import patch

import click
from click.testing import CliRunner

import commands.cli.egeria as cli
from commands.cat.list_deployed_servers import display_servers_by_dep_imp


def _ctx_obj():
    return SimpleNamespace(view_server="v", view_server_url="https://x", userid="u", password="p",
                           jupyter=False, width=100)


def _invoke(*args):
    group = cli.deployed_data
    command = group.get_command(click.Context(group), "deployed-servers")
    with patch.object(cli, "display_servers_by_dep_imp") as shown:
        result = CliRunner().invoke(command, list(args), obj=_ctx_obj())
    assert result.exit_code == 0, result.output
    return shown.call_args.args[0]


def test_the_default_command_sends_view_server():
    assert _invoke() == "View Server"


def test_an_explicit_type_is_passed_through():
    assert _invoke("--search-string", "PostgreSQL Server") == "PostgreSQL Server"


def test_the_display_function_defaults_to_view_server_too():
    assert inspect.signature(display_servers_by_dep_imp).parameters["search_string"].default == "View Server"
