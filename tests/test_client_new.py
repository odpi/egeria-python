import types
import pytest
import os
from pyegeria._client_new import Client2
from pyegeria.config import settings
from pyegeria.external_links import ExternalReferences
from pyegeria.logging_configuration import config_logging

from pyegeria._exceptions_new import PyegeriaException, print_exception_response, print_basic_exception



EGERIA_USER = os.environ.get("EGERIA_USER", "peterprofile")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")


app_config = settings.Environment
config_logging()
view_server: str = app_config.egeria_view_server
view_url: str = app_config.egeria_view_server_url
user: str = EGERIA_USER
user_pass: str = EGERIA_USER_PASSWORD

def test_add_archive_file():
    server_display_name = "qs-metadata-server"

    try:
        client = Client2(view_server, view_url, user, user_pass)
        client.create_egeria_bearer_token()
        archive_file = "content-packs/CocoComboArchive.omarchive"
        response = client.add_archive_file(archive_file, display_name = "qs-metadata-store")
        print(response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False