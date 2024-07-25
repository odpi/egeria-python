"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This script refreshed an integration daemon.

"""

import os
import argparse
import time

from pyegeria import ServerOps, AutomatedCuration
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
EGERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
EGERIA_KAFKA_ENDPOINT = os.environ.get('KAFKA_ENDPOINT', 'localhost:9092')
EGERIA_PLATFORM_URL = os.environ.get('EGERIA_PLATFORM_URL', 'https://localhost:9443')
EGERIA_VIEW_SERVER = os.environ.get('VIEW_SERVER', 'view-server')
EGERIA_VIEW_SERVER_URL = os.environ.get('EGERIA_VIEW_SERVER_URL', 'https://localhost:9443')
EGERIA_INTEGRATION_DAEMON = os.environ.get('INTEGRATION_DAEMON', 'integration-daemon')
EGERIA_INTEGRATION_DAEMON_URL = os.environ.get('EGERIA_INTEGRATION_DAEMON_URL', 'https://localhost:9443')
EGERIA_ADMIN_USER = os.environ.get('ADMIN_USER', 'garygeeke')
EGERIA_ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'secret')
EGERIA_USER = os.environ.get('EGERIA_USER', 'erinoverview')
EGERIA_USER_PASSWORD = os.environ.get('EGERIA_USER_PASSWORD', 'secret')




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the integration daemon to refresh")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_INTEGRATION_DAEMON
    url = args.url if args.url is not None else EGERIA_INTEGRATION_DAEMON_URL
    userid = args.userid if args.userid is not None else EGERIA_ADMIN_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD

    try:

        s_client = ServerOps(server, url, userid)

        s_client.refresh_integration_connectors(None, server, time_out = 60)

        print(f"\n===> Integration Daemon: \'{server}\' was refreshed.")


    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


if __name__ == "__main__":
    main()