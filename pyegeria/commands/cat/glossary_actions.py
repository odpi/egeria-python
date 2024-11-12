"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute Glossary actions.

"""
import csv
import json
import os
import sys
import time
from datetime import datetime
from rich import box
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

import click


from pyegeria import EgeriaTech, body_slimmer
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
)


EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get("KAFKA_ENDPOINT", "localhost:9092")
EGERIA_PLATFORM_URL = os.environ.get("EGERIA_PLATFORM_URL", "https://localhost:9443")
EGERIA_VIEW_SERVER = os.environ.get("VIEW_SERVER", "view-server")
EGERIA_VIEW_SERVER_URL = os.environ.get(
    "EGERIA_VIEW_SERVER_URL", "https://localhost:9443"
)
EGERIA_INTEGRATION_DAEMON = os.environ.get("INTEGRATION_DAEMON", "integration-daemon")
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get(
    "EGERIA_INTEGRATION_DAEMON_URL", "https://localhost:9443"
)
EGERIA_ADMIN_USER = os.environ.get("ADMIN_USER", "garygeeke")
EGERIA_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "secret")
EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")
EGERIA_WIDTH = os.environ.get("EGERIA_WIDTH", 200)
EGERIA_JUPYTER = os.environ.get("EGERIA_JUPYTER", False)


@click.command("create-glossary")
@click.option("--name", help="Name of Glossary", required=True)
@click.option("--language", help="Language of Glossary", default="English")
@click.option(
    "--description",
    help="Description of Glossary",
    default="A description goes here",
)
@click.option(
    "--usage",
    help="Purpose of glossary",
    default="Definitions",
)
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def create_glossary(
    server: str,
    url: str,
    userid: str,
    password: str,
    timeout: int,
    name: str,
    language: str,
    description: str,
    usage: str,
) -> None:
    """Create a new Glossary"""

    try:
        m_client = EgeriaTech(server, url, userid, password)
        token = m_client.create_egeria_bearer_token()

        existing_glossary = m_client.find_glossaries(name)
        if type(existing_glossary) is list:
            click.echo(
                f"\nFound {len(existing_glossary)} existing Glossaries with a similar name!\n"
            )
            for glossary in existing_glossary:
                if (
                    glossary["glossaryProperties"]["qualifiedName"]
                    == "Glossary:" + name
                ):
                    click.echo(
                        (
                            f"\tFound existing glossary: {glossary['glossaryProperties']['qualifiedName']} with id of {glossary['elementHeader']['guid']}\n"
                            "Exiting\n"
                        )
                    )
                    sys.exit(0)
                else:
                    click.echo(
                        "Found glossaries with similar names but different qualifiedNames...proceeding\n"
                    )

        glossary_guid = m_client.create_glossary(name, description, language, usage)
        print(f"New glossary {name} created with id of {glossary_guid}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("delete-glossary")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.argument("glossary-guid")
def delete_glossary(server, url, userid, password, timeout, glossary_guid):
    """Delete the glossary specified"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        m_client.delete_glossary(glossary_guid)

        click.echo(f"Deleted glossary: {glossary_guid}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("create-term")
@click.option("--glossary-name", help="Name of Glossary", required=True)
@click.option("--term-name", help="Name of Term", required=True)
@click.option(
    "--summary",
    help="Summary definition",
    default="Summary goes here",
)
@click.option(
    "--description",
    help="Full description",
    default="Description goes here",
)
@click.option("--abbrev", help="Abbreviation", default=None)
@click.option("--examples", help="Example usage", default=None)
@click.option("--usage", help="Usage notes", default=None)
@click.option("--version", help="Version", default="1.0")
@click.option(
    "--status",
    help="Status",
    type=click.Choice(
        ["DRAFT", "ACTIVE", "DEPRACATED", "OBSOLETE", "OTHER"], case_sensitive=False
    ),
    default="DRAFT",
)
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use.")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def create_term(
    server,
    url,
    userid,
    password,
    glossary_name,
    term_name,
    summary,
    description,
    abbrev,
    examples,
    usage,
    version,
    status,
    timeout: int = 120,
) -> str:
    """Create a new term"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        body = {
            "class": "ReferenceableRequestBody",
            "elementProperties": {
                "class": "GlossaryTermProperties",
                "qualifiedName": f"GlossaryTerm: {term_name} - {datetime.now().isoformat()}",
                "displayName": term_name,
                "summary": summary,
                "description": description,
                "abbreviation": abbrev,
                "examples": examples,
                "usage": usage,
                "publishVersionIdentifier": version,
            },
            "initialStatus": status,
        }
        exists = False
        glossary_info = m_client.find_glossaries(glossary_name)
        if type(glossary_info) is list:
            for glossary in glossary_info:
                if glossary["glossaryProperties"]["displayName"] == glossary_name:
                    exists = True
                    glossary_guid = glossary["elementHeader"]["guid"]

        if not exists:
            click.echo(f"The glossary name {glossary_name} was not found..exiting\n")
            sys.exit(0)

        term_guid = m_client.create_controlled_glossary_term(
            glossary_guid, body_slimmer(body)
        )

        click.echo(
            f"Successfully created term {term_name} with GUID {term_guid}, in glossary {glossary_name}.\n"
        )
        return term_guid
    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("delete-term")
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
@click.argument("term-guid")
def delete_term(server, url, userid, password, timeout, term_guid):
    """Delete a glossary term"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        term_guid = term_guid.strip()
        term_info = m_client.get_terms_by_guid(term_guid)

        m_client.delete_term(term_guid)

        click.echo(
            f"Deleted term with GUID: {term_guid} and Display Name: {term_info['glossaryTermProperties']['displayName']}"
        )

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("import-terms")
@click.option("--glossary-name", help="Name of Glossary", required=True)
@click.option("--file-name", help="Path of CSV file", required=True)
@click.option(
    "--verbose",
    is_flag=True,
    default=True,
    help="If set, result descriptions are provided",
)
@click.option(
    "--upsert",
    is_flag=True,
    default=True,
    help="If set, terms will be updated if they exist; otherwise they would be appended",
)
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def import_terms(
    glossary_name: str,
    file_name: str,
    verbose: bool,
    upsert: bool,
    server: str,
    url: str,
    userid: str,
    password: str,
    timeout: int,
):
    """Load terms from file into the glossary specified"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        result = m_client.load_terms_from_file(
            glossary_name, file_name, upsert=upsert, verbose=verbose
        )

        click.echo(
            f"Loaded terms from  into glossary: {glossary_name} from {file_name}"
        )
        if verbose:
            print(f"\n Verbose output:\n{json.dumps(result, indent = 2)}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()


@click.command("export-terms")
@click.option("--glossary-guid", help="GUID of Glossary to export", required=True)
@click.option("--file-name", help="Path of CSV file", required=True)
@click.option("--server", default=EGERIA_VIEW_SERVER, help="Egeria view server to use")
@click.option(
    "--url", default=EGERIA_VIEW_SERVER_URL, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def export_terms(glossary_guid: str, file_name, server, url, userid, password, timeout):
    """Export the glossary specified"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        result = m_client.export_glossary_to_csv(glossary_guid, file_name)

        click.echo(
            f"Exported {result} terms  from glossary: {glossary_guid} into {file_name}"
        )

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        m_client.close_session()
