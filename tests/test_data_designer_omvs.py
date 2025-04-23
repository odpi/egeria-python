"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the data designer view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from rich import print, print_json
from rich.console import Console

from pyegeria import MetadataExplorer
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.data_designer_omvs import DataDesigner

disable_ssl_warnings = True


console = Console()


def jprint(info, comment=None):
    if comment:
        print(comment)
    print(json.dumps(info, indent=2))


def valid_guid(guid):
    if (guid is None) or (type(guid) is not str):
        return False
    else:
        return True


class TestMetadataExplorer:
    good_view_server_1 = "qs-view-server"
    platform_url = "https://localhost:9443"
    view_server = "qs-view-server"
    user = "erinoverview"
    password = "secret"

    #
    ##
    #
    def test_create_data_structure(self):
        name = "Test Data Structure"
        description = "Test Data Structure Description"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.create_data_structure(name, description)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
            )
            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()

    def test_create_data_structure_w_body(self):
        display_name = "solar_power"
        namespace = "solar"
        body = {
              "properties": {
                "class" : "DataStructureProperties",
                "displayName": display_name,
                "qualifiedName": f"{namespace}::data-structure::{display_name}",
                "description": "a solar power data structure",
                "namespace": namespace,
                "versionIdentifier": "0.1"
              }
            }

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.create_data_structure_w_body(body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
            )
            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()



    def test_find_all_data_structures(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_all_data_structures()
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()


    def test_get_data_structures_by_name(self):
        name = "Test Data Structure"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_structures_by_name(name, add_implementation=False)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: " + response)

            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException,
                ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            m_client.close_session()