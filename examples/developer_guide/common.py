"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Shared helpers for the Developer Guide examples: connection settings and a glossary query.
"""

from dataclasses import dataclass

from pyegeria import EgeriaTech, load_app_config, settings


@dataclass
class Connection:
    view_server: str
    platform_url: str
    user_name: str
    user_password: str


def connection_settings() -> Connection:
    """Read connection details from pyegeria's configuration (.env, config.json or OS environment),
    falling back to the Egeria quick-start defaults for anything that isn't set."""
    load_app_config()
    env = settings.Environment
    user = settings.User_Profile
    return Connection(
        view_server=env.egeria_view_server or "qs-view-server",
        platform_url=env.egeria_platform_url or "https://localhost:9443",
        user_name=user.user_name or "garygeeke",
        user_password=user.user_pwd or "secret",
    )


def fetch_glossaries(conn: Connection, search_string: str = "*") -> list[dict]:
    """Return one dict per glossary with its display name, qualified name, description and GUID.

    find_glossaries(output_format="JSON") returns the raw Egeria elements: each has an
    "elementHeader" (holding the GUID) and a "properties" dict. A str is returned instead
    of a list when nothing matches.
    """
    client = EgeriaTech(conn.view_server, conn.platform_url, conn.user_name, conn.user_password)
    try:
        client.create_egeria_bearer_token(conn.user_name, conn.user_password)
        elements = client.find_glossaries(search_string, output_format="JSON", graph_query_depth=0)
    finally:
        client.close_session()

    if not isinstance(elements, list):
        return []
    return [
        {
            "Display Name": element["properties"].get("displayName", ""),
            "Qualified Name": element["properties"].get("qualifiedName", ""),
            "Description": element["properties"].get("description", ""),
            "GUID": element["elementHeader"]["guid"],
        }
        for element in elements
    ]
