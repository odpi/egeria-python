"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import os
import sys
from datetime import datetime

from loguru import logger
from pydantic import ValidationError

log_format = "{time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
logger.add("debug_log.log", rotation="1 day", retention="1 week", compression="zip", level="TRACE", format=log_format,
           colorize=True)
import click
from rich import print
from rich.console import Console


from pyegeria._exceptions_new import PyegeriaException
from md_processing.dr_egeria import process_md_file

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get("EGERIA_VIEW_SERVER_URL", "https://localhost:9443")
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get("EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443")
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = os.environ.get("EGERIA_WIDTH", 220)
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", False)
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "../../")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "md_processing/dr_egeria_inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "md_processing/dr_egeria_outbox")

@click.command("process_markdown_file", help="Process a markdown file and return the output as a string.")
@click.option("--input-file", help="Markdown file to process.", default="dr_egeria_intro_part1.md", required=True,
              prompt=False)
@click.option("--output-folder", help="Output folder.", default="", required=False)
@click.option("--directive", default="process", help="How to process the file",
              type=click.Choice(["display", "validate", "process"], case_sensitive=False), prompt=False, )
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option("--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@logger.catch
def process_markdown_file(input_file: str, output_folder:str, directive: str, server: str, url: str, userid: str,
                          user_pass: str ) -> None:
    """
    Process a markdown file by parsing and executing Dr. Egeria md_commands. Write output to a new file.
    """
    try:
        process_md_file(input_file, output_folder, directive, server, url, userid, user_pass)
        logger.info(f"Called process_markdown_file with input file {input_file}")
    except PyegeriaException as e:
        logger.error(f"Error processing markdown file {input_file}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error processing markdown file {input_file}: {e}")


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--server", help="Name of the server to display status for")
#     parser.add_argument("--url", help="URL Platform to connect to")
#     parser.add_argument("--userid", help="User Id")
#     parser.add_argument("--password", help="User Password")
#     parser.add_argument("--time_out", help="Time Out")
#
#     args = parser.parse_args()
#
#     server = args.server if args.server is not None else EGERIA_VIEW_SERVER
#     url = args.url if args.url is not None else EGERIA_PLATFORM_URL
#     userid = args.userid if args.userid is not None else EGERIA_USER
#     user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
#     time_out = args.time_out if args.time_out is not None else 60
#     try:
#         input_file = Prompt.ask("Markdown File name to process:", default="")
#         directive = Prompt.ask("Processing Directive:", choices=[ "display", "validate", "process"],
#         default="validate")
#
#         process_markdown_file(input_file, directive, server, url, userid, user_pass)
#     except KeyboardInterrupt:
#         pass
#
#
# if __name__ == "__main__":
#     main()

if __name__ == "__main__":
    process_markdown_file()