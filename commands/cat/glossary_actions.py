"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute Glossary actions.

"""

import json
import os
import sys

import click

from pyegeria import EgeriaTech, body_slimmer, settings, NO_ELEMENTS_FOUND, TERM_STATUS
from pyegeria._exceptions import (
    PyegeriaException, print_basic_exception
)

app_config = settings.Environment

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")



@click.command("create-glossary")
@click.option("--name", help="Name of Glossary", required=True)
@click.option("--language", help="Language of Glossary", default="English")
@click.option("--description", help="Description of Glossary", default="A description goes here")
@click.option("--usage", help="Purpose of glossary", default="Definitions")
@click.option("--category", help="Category of glossary")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use.")
@click.option("--url", default=app_config.egeria_view_server_url, help="URL of view server to connect to")
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
        category: str,
) -> None:
    """Create a new Glossary """

    try:
        m_client = EgeriaTech(server, url, userid, password)
        token = m_client.create_egeria_bearer_token()

        glossary_guid = m_client.create_glossary(name, description, language, usage, category)
        print(f"New glossary `{name}` created with id of `{glossary_guid}`")

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("delete-glossary")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
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
        m_client.delete_glossary(glossary_guid, cascade=False)

        click.echo(f"Deleted glossary: `{glossary_guid}`")

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("create-term")
@click.option("--glossary-name", help="Name of Glossary", required=True)
@click.option("--term-name", help="Name of Term", required=True)
@click.option("--qualified-name", help="Qualified name of Term", default=None)
@click.option("--summary", help="Summary definition", default="Summary goes here")
@click.option("--description", help="Full description", default="Description goes here")
@click.option("--abbrev", help="Abbreviation", default=None)
@click.option("--examples", help="Example usage", default=None)
@click.option("--usage", help="Usage notes", default=None)
@click.option("--version", help="Version", default="1.0")
@click.option("--status", help="Status",
              type=click.Choice(TERM_STATUS, case_sensitive=False
            ), default="DRAFT")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use.")
@click.option("--url", default=app_config.egeria_view_server_url,
              help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def create_term(server, url, userid, password, glossary_name, term_name, summary, description, abbrev, examples, usage,
                version, status, timeout: int = 120, qualified_name=None) -> str:
    """Create a new term """
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    if qualified_name is None:
        qualified_name = m_client.__create_qualified_name__('Term', term_name,
                                                            settings.User_Profile.egeria_local_qualifier)
    try:
        glossary_guid = m_client.__get_guid__(display_name = glossary_name, property_name = "displayName")
        if glossary_guid == NO_ELEMENTS_FOUND:
            click.echo(f"The glossary name {glossary_name} was not found..exiting\n")
            sys.exit(0)

        body = {
            "class": "NewElementRequestBody",
            "parentGUID" : glossary_guid,
            "parentRelationshipTypeName" : "CollectionMembership",
            "anchorScopeGUID" : glossary_guid,
            "isOwnAnchor": True,
            "parentAtEnd1": True,
            "elementProperties": {
                "class": "GlossaryTermProperties",
                "qualifiedName": qualified_name,
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

        term_guid = m_client.create_glossary_term(body_slimmer(body)
        )

        click.echo(
            f"Successfully created term `{term_name}` with GUID `{term_guid}`, in glossary `{glossary_name}`.\n"
        )
        return term_guid
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("update-term")
@click.option("--term-guid", help="GUID of the Term", required=True)
@click.option("--summary", help="Summary definition", default="Summary goes here")
@click.option("--description", help="Full description", default="Description goes here")
@click.option("--abbrev", help="Abbreviation", default=None)
@click.option("--examples", help="Example usage", default=None)
@click.option("--usage", help="Usage notes", default=None)
@click.option("--version", help="Version", default="1.0")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use.")
@click.option("--url", default=app_config.egeria_view_server_url,
              help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def update_term(server, url, userid, password, term_name, summary, description, abbrev, examples, usage,
                version, timeout: int = 120) -> None:
    """Update a term """
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()

    try:
        body = {
            "class": "UpdateElementRequestBody",
            "mergeUpdate": True,
            "elementProperties": {
                "class": "GlossaryTermProperties",
                "displayName": term_name,
                "summary": summary,
                "description": description,
                "abbreviation": abbrev,
                "examples": examples,
                "usage": usage,
                "publishVersionIdentifier": version,
            },
        }

        term_guid = m_client.update_glossary_term(body_slimmer(body)
        )

        click.echo(
            f"Successfully updated term `{term_name}` with GUID `{term_guid}`.\n"
        )

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("update-term-status")
@click.option("--term-guid", help="GUID of the Term", required=True)
@click.option("--status", help="Status",
              type=click.Choice(TERM_STATUS, case_sensitive=False), default="DRAFT")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use.")
@click.option("--url", default=app_config.egeria_view_server_url,
              help="URL of Egeria platform to connect to")
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def update_term_status(server, url, userid, password, term_guid, status, timeout: int = 120) -> None:
    """Update a term """
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()

    try:

        term_guid = m_client.update_glossary_term_status(term_guid, status)

        click.echo(
            f"Successfully updated term {term_guid} with status `{status}`.\n"
        )

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("delete-term")
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria View Server to connect to"
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

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()

@click.command("import-terms-from-csv")
@click.option("--glossary_name", help="Name of Glossary", required=True)
@click.option("--file_name", help="Name of CSV file", required=True)
@click.option(
    "--input_file", help="Path of CSV file", default=app_config.egeria_glossary_path, required=False
)
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
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def import_terms_csv(
        glossary_name: str,
        file_path: str,
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
        result = m_client.load_terms_from_csv_file(
            glossary_name,
            file_name,
            file_path=file_path,
            upsert=upsert,
            verbose=verbose,
        )

        click.echo(
            f"Loaded terms from  into glossary: {glossary_name} from {file_name}"
        )
        if verbose:
            print(f"\n Verbose output:\n{json.dumps(result, indent=2)}")

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()


@click.command("export-terms-csv")
@click.option(
    "--glossary_guid",
    help="GUID of Glossary to export",
    required=True,
)
@click.option("--file_name", help="Name of CSV file", required=True)
@click.option(
    "--input_file", help="Path of CSV file", default=app_config.egeria_glossary_path, required=False
)
@click.option("--server", default=app_config.egeria_view_server, help="Egeria view server to use")
@click.option(
    "--url", default=app_config.egeria_view_server_url, help="URL of Egeria platform to connect to"
)
@click.option("--userid", default=EGERIA_USER, help="Egeria user")
@click.option("--password", default=EGERIA_USER_PASSWORD, help="Egeria user password")
@click.option("--timeout", default=60, help="Number of seconds to wait")
def export_terms_csv(
        glossary_guid: str, file_name, file_path, server, url, userid, password, timeout
):
    """Export the glossary specified"""
    m_client = EgeriaTech(server, url, user_id=userid, user_pwd=password)
    token = m_client.create_egeria_bearer_token()
    try:
        result = m_client.export_glossary_to_csv(glossary_guid, file_name, file_path)

        click.echo(
            f"Exported {result} terms  from glossary: {glossary_guid} into {file_name}"
        )

    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        m_client.close_session()

