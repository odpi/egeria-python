"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This script refreshed an integration daemon.

"""

import os
import argparse
import time
import click
from trogon import tui
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

@tui()
@click.command()
@click.option('--file', prompt= "Path to the archive file to load", help='Full path to the archive file to load')
@click.option('--server', default = EGERIA_METADATA_STORE, help='Egeria metadata store to load')
@click.option('--url', default = EGERIA_PLATFORM_URL, help='URL of Egeria platform to connect to')
@click.option('--userid', default = EGERIA_ADMIN_USER, help='Egeria admin user')
@click.option('--password', default = EGERIA_ADMIN_PASSWORD, help='Egeria admin password')
@click.option('--timeout', default = 60, help = 'Number of seconds to wait')

def load_archive(file, server, url, userid, password, timeout):

    try:

        s_client = ServerOps(server, url, userid, password)

        s_client.add_archive_file(file, server, timeout = timeout)

        click.echo(f"Loaded archive: {file}")


    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)


if __name__ == "__main__":
    load_archive()