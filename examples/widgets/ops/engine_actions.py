"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Execute engine actions.

"""
import os

import click

# from ops_config import Config, pass_config
from pyegeria import Platform
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    print_exception_response,
)

GERIA_METADATA_STORE = os.environ.get("EGERIA_METADATA_STORE", "active-metadata-store")
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


@click.command('stop')
@click.option('--server', default=EGERIA_VIEW_SERVER, help='Egeria metadata store to load')
@click.option('--url', default=EGERIA_VIEW_SERVER_URL, help='URL of Egeria platform to connect to')
@click.option('--userid', default=EGERIA_ADMIN_USER, help='Egeria admin user')
@click.option('--password', default=EGERIA_ADMIN_PASSWORD, help='Egeria admin password')
@click.option('--timeout', default=60, help='Number of seconds to wait')
def stop_daemon(file, server, url, userid, password, timeout):
    """Stop an engine-host daemon"""
    p_client = Platform(server, url, userid, password)
    try:
        p_client.shutdown_server()

        click.echo(f"Stopped server {server}")
    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()


@click.command('start')
@click.option('--server', default=EGERIA_VIEW_SERVER, help='Egeria metadata store to load')
@click.option('--url', default=EGERIA_VIEW_SERVER_URL, help='URL of Egeria platform to connect to')
@click.option('--userid', default=EGERIA_ADMIN_USER, help='Egeria admin user')
@click.option('--password', default=EGERIA_ADMIN_PASSWORD, help='Egeria admin password')
@click.option('--timeout', default=60, help='Number of seconds to wait')
def start_daemon(file, server, url, userid, password, timeout):
    """Start or restart an engine-host from its known configuration """
    p_client = Platform(server, url, userid, password)
    try:
        p_client.activate_server_stored_config()

        click.echo(f"Started server {server}")

    except (InvalidParameterException, PropertyServerException) as e:
        print_exception_response(e)
    finally:
        p_client.close_session()
