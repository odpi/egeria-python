"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This is a simple script to secure a fresh-start environment with an admin user.

"""
import os
from pyegeria import (Egeria, settings,
                      PyegeriaAPIException, PyegeriaConnectionException, PyegeriaInvalidParameterException,
                      PyegeriaUnknownException, PyegeriaClientException, PyegeriaTimeoutException)


app_config = settings.Environment
EGERIA_PLATFORM_URL = app_config.egeria_platform_url
EGERIA_VIEW_SERVER_URL = app_config.egeria_view_server_url
EGERIA_VIEW_SERVER = app_config.egeria_view_server
EGERIA_USER = os.environ.get('EGERIA_USER','freddie')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD')


client = Egeria(
    platform_url=EGERIA_PLATFORM_URL,
    view_server_url=EGERIA_VIEW_SERVER_URL,
    view_server=EGERIA_VIEW_SERVER,
    user="bootstrap",
    password="secret",
)

client.create_egeria_bearer_token()

body = {
    "class": "UserAccountRequestBody",
    "userAccount": {
        "class": "OpenMetadataUserAccount",
        "userId": EGERIA_USER,
        "userName": "First",
        "userAccountStatus": "AVAILABLE",
        "secrets": {"clearPassword": "testpassword"}
    }