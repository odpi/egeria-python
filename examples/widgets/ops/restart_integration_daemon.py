"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This script restarts an integration daemon.

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



def restart_connector(connector: str, server:str, url:str, userid:str, password:str):
    try:

        s_client = ServerOps(server, url, userid)
        if connector == 'all':
            connector = None
            statement = "ALL connectors"
        else:
            statement = f"the {connector} "

        s_client.restart_integration_connector(connector, server, time_out = 60)

        print(f"\n===> Integration Daemon \'{server}\' restarted {statement}.")


    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", help="Name of the integration daemon to refresh")
    parser.add_argument("--url", help="URL Platform to connect to")
    parser.add_argument("--userid", help="User Id")
    parser.add_argument("--password", help="User Password")
    parser.add_argument("--connector", default='all', help="Name of the connector to refresh")
    args = parser.parse_args()

    server = args.server if args.server is not None else EGERIA_INTEGRATION_DAEMON
    url = args.url if args.url is not None else EGERIA_INTEGRATION_DAEMON_URL
    userid = args.userid if args.userid is not None else EGERIA_ADMIN_USER
    user_pass = args.password if args.password is not None else EGERIA_USER_PASSWORD
    restart_connector(args.connector, server, url, userid, user_pass)

if __name__ == "__main__":
    main()