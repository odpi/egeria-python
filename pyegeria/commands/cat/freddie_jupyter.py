"""
This is an ongoing experiment in parsing and playing with Freddie docs
"""
import json

from jupyter_notebook_parser import JupyterNotebookParser
import nbformat
import os
import re
from pyegeria import EgeriaTech
from rich import box, print
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from freddie_utils import (extract_command, process_glossary_upsert_command, process_term_upsert_command,
                        get_current_datetime_string, process_per_proj_upsert_command, commands)
import click
from pyegeria import EgeriaTech, body_slimmer, NO_GLOSSARIES_FOUND, NO_TERMS_FOUND, NO_ELEMENTS_FOUND, NO_PROJECTS_FOUND
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
)
from datetime import datetime

EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("EGERIA_VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("EGERIA_INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = os.environ.get("EGERIA_WIDTH", 220)
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", False)
EGERIA_HOME_GLOSSARY_GUID = os.environ.get("EGERIA_HOME_GLOSSARY_GUID", None)
EGERIA_GLOSSARY_PATH = os.environ.get("EGERIA_GLOSSARY_PATH", None)
EGERIA_ROOT_PATH = os.environ.get("EGERIA_ROOT_PATH", "/Users/dwolfson/localGit/egeria-v5-3/egeria-python")
EGERIA_INBOX_PATH = os.environ.get("EGERIA_INBOX_PATH", "pyegeria/commands/cat/freddies-inbox")
EGERIA_OUTBOX_PATH = os.environ.get("EGERIA_OUTBOX_PATH", "pyegeria/commands/cat/freddies-outbox")

console = Console(width=int(EGERIA_WIDTH))



@click.command("process-jupyter")
@click.option("--file-path", help="File path to notebook",
              default="glossary_creation_experiment.ipynb")
@click.option("--directive", default="display-only", help="How to process the file")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--user_pass", default=EGERIA_USER_PASSWORD, help="Egeria user password")
def process_jupyter_notebook(
        file_path: str,
        directive: str,
        server: str,
        url: str,
        userid: str,
        user_pass: str,
        ):
    client = EgeriaTech(server, url, user_id=userid)
    token = client.create_egeria_bearer_token(userid, user_pass)

    element_dictionary = {}

    try:
        updated = False
        full_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_INBOX_PATH, file_path)
        click.echo(f"Processing notebook: {full_file_path}")
        with open(full_file_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
            for cell in nb.cells:
                if cell.cell_type == 'markdown':
                    if cell.source.strip().startswith('#'):
                        potential_command = extract_command(cell.source)
                        if potential_command in commands:
                            if potential_command in ["Create Glossary", "Update Glossary"]:
                                result = process_glossary_upsert_command(client, element_dictionary,
                                                                         cell.source, directive)

                            elif potential_command in ["Create Term", "Update Term"]:
                                result = process_term_upsert_command(client, element_dictionary,
                                                                     cell.source, directive)
                            elif potential_command in ["Create Personal Project", "Update Personal Project"]:
                                result = process_per_proj_upsert_command(client, element_dictionary, cell.source, directive)
                            else:
                                # If command is not recognized, copy the block as-is
                                result = None

                            if result:
                                if directive == "process":
                                    updated = True
                                    cell.source = result
                                    # print(json.dumps(element_dictionary, indent=4))
                            elif directive == "process":
                                # Handle case with errors (skip this block but notify the user)
                                print(f"\n==>\tErrors found while processing command: \'{potential_command}\'\n"
                                      f"\tPlease correct and try again. \n")


        if updated:
            path, filename = os.path.split(file_path)  # Get both parts
            new_filename = f"processed-{get_current_datetime_string()}-{filename}"  # Create the new filename
            new_file_path = os.path.join(EGERIA_ROOT_PATH, EGERIA_OUTBOX_PATH, new_filename)  # Construct the new path
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)


            with open(new_file_path, 'w') as f2:
                nbformat.write(nb, f2)
            click.echo(f"\n==>Notebook written to {new_file_path}")
        else:
            click.echo("\nNo updates detected. New file not created.")

    except Exception as e:
        print_exception_response(e)
        return


if __name__ == "__main__":
    process_jupyter_notebook()
