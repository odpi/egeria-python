"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys

import click
from loguru import logger
from rich.console import Console
from rich.prompt import Prompt

from pyegeria.core._exceptions import PyegeriaException
from pyegeria.core.config import settings
from md_processing.dr_egeria import process_md_file

# Configure logging
log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)

# Load configuration from config/config.json with environment variable overrides
app_config = settings.Environment

# Get configuration values with environment variable fallbacks
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", app_config.egeria_view_server)
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", app_config.egeria_view_server_url)
# User credentials are only from environment variables or command line (not stored in config for security)
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = int(os.environ.get("EGERIA_WIDTH", app_config.console_width or 220))
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", str(app_config.egeria_jupyter)).lower() in ("true", "1", "yes")

console = Console(width=EGERIA_WIDTH)

@click.command("process_markdown_file", help="Process a markdown file and return the output as a string.")
@click.option("--input-file", help="Markdown file to process.", default="dr_egeria_intro_part1.md", required=True,
              prompt=False)
@click.option("--output-folder", help="Output folder.", default="", required=False)
@click.option("--directive", default="process", help="How to process the file",
              type = click.Choice(["display", "validate", "process"], case_sensitive=False), prompt=False, )
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option("--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--parse-summary", default="none", help="When to show parse summaries",
              type=click.Choice(["all", "errors", "none"], case_sensitive=False))
@click.option("--attribute-logs", default="debug", help="Per-attribute log verbosity",
              type=click.Choice(["debug", "info", "none"], case_sensitive=False))
@logger.catch
def process_markdown_file(input_file: str, output_folder:str, directive: str, server: str, url: str, userid: str,
                          user_pass: str, parse_summary: str, attribute_logs: str) -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.
    """
    try:
        process_md_file(input_file, output_folder, directive, server, url, userid, user_pass,
                        parse_summary=parse_summary, attribute_logs=attribute_logs)
        logger.info(f"Called process_markdown_file with input file {input_file}")
    except PyegeriaException as e:
        logger.error(f"Error processing markdown file {input_file}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing markdown file {input_file}: {e}")


def _running_in_pycharm_debugger() -> bool:
    return sys.gettrace() is not None or os.environ.get("PYCHARM_HOSTED") is not None

if __name__ == "__main__":
    if _running_in_pycharm_debugger():
        input_file = Prompt.ask("Markdown File name to process:", default="dr_egeria_intro_part1.md")
        process_md_file(input_file, "", "process", EGERIA_VIEW_SERVER, EGERIA_VIEW_SERVER_URL, EGERIA_USER,
                        EGERIA_USER_PASSWORD, parse_summary="all", attribute_logs="debug")
    else:
        process_markdown_file()
