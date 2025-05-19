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

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    )
from pyegeria.data_designer_omvs import DataDesigner

disable_ssl_warnings = True


console = Console(width=250)


def jprint(info, comment=None):
    if comment:
        print(comment)
    print(json.dumps(info, indent=2))


def valid_guid(guid):
    if (guid is None) or (type(guid) is not str):
        return False
    else:
        return True


class TestDataDesigner:
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

    def test_delete_data_structure(self):
        guid = '1a6ef664-a107-4d6a-ade2-e6906cc38c08'
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            m_client.delete_data_structure(guid, cascade=True)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
            )

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

    def test_link_member_data_field(self):
        struct_guid = "e441f9f1-4dd0-4960-b11d-08a1b8c717f6"
        member_guid = "ca085aa8-c5bb-4a15-ab2b-73be43166f3c"

        body = {
          "class" : "MemberDataFieldRequestBody",
          "properties": {
            "class": "MemberDataFieldProperties",
            "dataFieldPosition": 0,
            "minCardinality": 0,
            "maxCardinality": -1,

          }
        }

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            m_client.link_member_data_field(struct_guid,member_guid, body)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
            )

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

    def test_delete_data_field(self):
        guid = 'c14ab70e-d3f5-440c-a389-50837cdc012b'
        # guid = 'b18df5d5-23c6-4c85-a06d-e1da6088901c'

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            m_client.delete_data_field(guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds"
            )

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
            response = m_client.find_all_data_structures(output_format="DICT")
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

    def test_find_data_structures(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            search_string = "TBDF-Incoming Weekly Measurement Data"
            response = m_client.find_data_structures(search_string, output_format="DICT")
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
        name = "solar"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_structures_by_name(name)
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

    def test_get_data_structures_by_guid(self):
        guid = "d3c0eb7f-476f-4649-a09c-f8ee39c0dfb9"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_structures_by_guid(guid, output_format="JSON")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if isinstance(response, list | dict):
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\tResponse is: \n" + response)

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


    def test_create_data_field(self):
        name = "Test Data Structure"
        description = "Test Data Structure Description"

        body =  {
          "properties": {
            "class": "DataFieldProperties",
            "qualifiedName": "dataField::radio_name",
            "displayName": "radio_name",
            "namespace": "",
            "description": "What is the name of the radio",
            "versionIdentifier": ".1",
            "aliases": [
              "transmitter"
            ],
            "namePatterns": [],
            "isDeprecated": False,
            "isNullable": False,
            "dataType": "String",
            "minimumLength": 3,
            "length": 20,
            "precision": 0,
            "orderedValues": False,
            "sortOrder": "UNSORTED",

            }
          }



        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.create_data_field(body)
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

    def test_find_all_data_fields(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_all_data_fields(output_format="DICT")
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

    def test_get_data_field_by_name(self):
        name = "radio_name"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_fields_by_name(name)
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

    def test_get_data_field_by_guid(self):
        guid = "d58698e3-0e9c-4237-9855-3c5949e5e64a"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_field_by_guid(guid, output_format="DICT")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if isinstance(response, list | dict):
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

    def test_create_data_class(self):
        name = "Purchase Date"
        description = "Date of purchase in YYYY-MM-DD format"

        body =  {
          "properties": {
            "class": "DataClassProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "namespace": "add scope of this data class's applicability.",
            "matchPropertyNames": [
              "name1",
              "name2"
            ],
            "matchThreshold": 0,
            "specification": "",
            "specificationDetails": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            },
            "dataType": "",
            "allowsDuplicateValues": True,
            "isNullable": False,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns": [],
            "additionalProperties": {
              "property1": "propertyValue1",
              "property2": "propertyValue2"
            }
          }
        }



        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.create_data_class(body)
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

    def test_find_data_fields(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            search_string = "PatientId"
            response = m_client.find_data_fields(search_string,output_format="DICT")
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

    def test_get_data_field_by_name(self):
        name = "radio_name"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_fields_by_name(name)
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

    def test_get_data_field_by_guid(self):
        guid = "5eeaab97-b6de-4788-b901-5c46845572f3"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_field_by_guid(guid, output_format="JSON")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if isinstance(response, list | dict):
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

    def test_find_all_data_classes(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_all_data_classes(output_format="JSON")
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

    def test_find_data_classes(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_data_classes(output_format="JSON")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            search_string = "date"
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