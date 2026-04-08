"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys
import click
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from pyegeria.core._exceptions import PyegeriaException, print_basic_exception
from pyegeria.core.config import settings
from md_processing.dr_egeria import process_md_file_v2
import asyncio

# Configure logging
log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="WARNING", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="WARNING", format=log_format,
           colorize=True)

# Load configuration from config/config.json with environment variable overrides
app_config = settings.Environment

# Get configuration values with environment variable fallbacks
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", app_config.egeria_view_server)
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", app_config.egeria_view_server_url)
# User credentials are only from environment variables or command line (not stored in config for security)
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", app_config.console_width or 190))
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", str(app_config.egeria_jupyter)).lower() in ("true", "1", "yes")

console = Console(width=EGERIA_WIDTH)

@click.command("process_markdown_file", help="Process a markdown file and return the output as a string.")
@click.option("--input-file", help="Markdown file to process.", default="dr_egeria_intro_part1.md",
              prompt="Markdown file to process")
@click.option("--output-folder", help="Output folder.", default="", required=False)
@click.option("--directive", default="validate", help="How to process the file (display/validate/process). "
              "Overridden by --validate or --process flags.",
              type=click.Choice(["display", "validate", "process"], case_sensitive=False), prompt=False)
@click.option("--validate", "do_validate", is_flag=True, default=False,
              help="Shortcut: validate the file against Egeria without making changes (overrides --directive)")
@click.option("--process", "do_process", is_flag=True, default=False,
              help="Shortcut: execute all commands and make permanent changes in Egeria (overrides --directive)")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option("--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--parse-summary", default="none", help="When to show parse summaries",
              type=click.Choice(["all", "errors", "none"], case_sensitive=False))
@click.option("--attribute-logs", default="info", help="Per-attribute log verbosity",
              type=click.Choice(["debug", "info", "none"], case_sensitive=False))
@click.option("--advanced", is_flag=True, default=False,
              help="Use Advanced usage level — shows additional attributes (default: Basic)")
@click.option("--summary-only", is_flag=True, default=False, help="Only display the summary table and errors/warnings")
@click.option("--debug", is_flag=True, default=False, help="Print each Egeria API request URL and body to the console")
@logger.catch
def process_markdown_file(input_file: str, output_folder: str, directive: str,
                          do_validate: bool, do_process: bool,
                          server: str, url: str, userid: str,
                          user_pass: str, parse_summary: str, attribute_logs: str, advanced: bool,
                          summary_only: bool, debug: bool) -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.

    Directive resolution order (highest priority first):
      1. --process flag  → process
      2. --validate flag → validate
      3. --directive     → value provided (default: validate)
    """
    # Resolve directive: explicit shortcut flags take priority
    if do_process:
        directive = "process"
    elif do_validate:
        directive = "validate"
    # else: use --directive as-is (default "validate")

    usage_level = "Advanced" if advanced else "Basic"
    try:
        # Instantiate the client
        from pyegeria import EgeriaTech
        client = EgeriaTech(server, url, userid, user_pass)
        client.create_egeria_bearer_token()
        asyncio.run(process_md_file_v2(
            input_file=input_file,
            output_folder=output_folder,
            directive=directive,
            client=client,
            parse_summary=parse_summary,
            attribute_logs=attribute_logs,
            usage_level=usage_level,
            summary_only=summary_only,
            debug=debug,
        ))
        logger.info(f"Called process_markdown_file with input file {input_file}")
    except PyegeriaException as e:
        console.print_exception()
        print_basic_exception(e)
        logger.error(f"Error processing markdown file {input_file}: {e}")
    except Exception as e:
        console.print_exception()
        logger.error(f"Unexpected error processing markdown file {input_file}: {e}")


def _running_in_pycharm_debugger() -> bool:
    return sys.gettrace() is not None or os.environ.get("PYCHARM_HOSTED") is not None

if __name__ == "__main__":
    # if _running_in_pycharm_debugger():
    input_file = Prompt.ask("Markdown File name to process:", default="dr_egeria_intro_part1.md")
    directive = Prompt.ask("Directive (display/validate/process):", default="validate")
    advanced = Prompt.ask("Use advanced usage level? [y/N]:", default="N").strip().lower() in ("y", "yes")
    process_markdown_file.callback(input_file, "", directive,
                            do_validate=False, do_process=False,
                            server=EGERIA_VIEW_SERVER, url=EGERIA_VIEW_SERVER_URL, userid=EGERIA_USER,
                            user_pass=EGERIA_USER_PASSWORD, parse_summary="all", attribute_logs="debug",
                            advanced=advanced, summary_only=False, debug=False)
    # else:
    #     process_markdown_file()
