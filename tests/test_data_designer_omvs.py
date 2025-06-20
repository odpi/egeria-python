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
        guid = 'ff806689-e88a-425f-91de-7fe896f0f7aa'
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

    def test_link_data_class_definition(self):
        data_field_guid = "2ca5f6c9-1c9e-40b7-bffd-0ec440c1673d"
        data_class_guid = "7f2d5160-0133-4f23-b3fe-3c3d6f5a2be6"

        body = {
            "class": "MetadataSourceRequestBody",
            "forLineage": False,
            "forDuplicateProcessing": False
            }

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            m_client.link_data_class_definition(data_field_guid,data_class_guid, body)
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
            response = m_client.find_data_structures(search_string, output_format="REPORT")
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

    def test_get_data_struct_coll(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            guid = "feb88a1f-2e5d-4cdd-ae1d-36613d311ea8"
            response = m_client.get_data_memberships(m_client.get_data_structure_by_guid, guid)
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if type(response) is dict:
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
        guid = "f0618139-40d0-47b3-8dac-1053bf938ab4"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_structure_by_guid(guid, output_format="JSON")
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
            response = m_client.find_all_data_fields(output_format="LIST")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if type(response) is list:
                print_json(data=response)
            elif type(response) is str:
                console.print("\n\n\t Response is: \n\n" + response)

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
        name = "DataField::Date"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_fields_by_name(name, output_format="REPORT")
            duration = time.perf_counter() - start_time
            print(
                f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}"
                )
            if isinstance (response, list | dict):
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
        guid = 'cebe4255-e2bb-44f0-947e-8b7f3f731791'
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

    def test_delete_data_field(self):
        guid = 'cebe4255-e2bb-44f0-947e-8b7f3f731791'
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

    def test_get_data_field_rel_elements(self):
        guid = "407e0012-8a13-444a-8f96-e74ad77ed55c"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_field_rel_elements(guid)
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

    def test_link_nested_data_field(self):
        parent_guid = "a16cb2dd-22cd-4ffe-bca0-b48ac1b1762d"
        child_guid = "407e0012-8a13-444a-8f96-e74ad77ed55c"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.link_nested_data_field(parent_guid, child_guid)
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



    def test_find_data_fields(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            search_string = 'DataField::PatientId'
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




#
# Data Classes
#
    def test_create_data_class(self):
        name = "Purchase Date"
        description = "Date of purchase in YYYY-MM-DD format"

        body = {
          "class" : "NewDataClassRequestBody",

          "effectiveTime" : None,
          "forLineage" : False,
          "forDuplicateProcessing" : False,
          # "anchorGUID" : "add guid here",
          "isOwnAnchor": True,
          # "parentGUID": "add guid here",
          # "parentRelationshipTypeName": "add type name here",
          # "parentRelationshipProperties": {
          #   "class": "ElementProperties",
          #   "propertyValueMap" : {
          #     "description" : {
          #       "class": "PrimitiveTypePropertyValue",
          #       "typeName": "string",
          #       "primitiveValue" : "New description"
          #     }
          #   }
          # },
          "parentAtEnd1": True,
          "properties": {
            "class" : "DataClassProperties",
            "qualifiedName": "dataClass::moo",
            "displayName": "Moo",
            "description": "add description here",
            # "namespace": "add scope of this data class's applicability.",
            # "matchPropertyNames": ["name1", "name2"],
            "matchThreshold": 0,
            # "specification": "",
            # "specificationDetails": {
            #   "property1" : "propertyValue1",
            #   "property2" : "propertyValue2"
            # },
            "dataType": "String",
            "allowsDuplicateValues": True,
            "isNullable": False,
            "defaultValue": "",
            "averageValue": "",
            "valueList": [],
            "valueRangeFrom": "",
            "valueRangeTo": "",
            "sampleValues": [],
            "dataPatterns" : [],
            "namePatterns": [],
            # "additionalProperties": {
            #   "property1" : "propertyValue1",
            #   "property2" : "propertyValue2"
            # },
            # "effectiveFrom": "{{$isoTimestamp}}",
            # "effectiveTo": "{{$isoTimestamp}}"
          }
        }

            # {
            # "properties": {
            #     "class": "DataClassProperties",
            #     "qualifiedName": "DataClass::Purchase Date",
            #     "displayName": name,
            #     "description": description,
            #     "namespace": None,
            #     "matchPropertyNames": [],
            #     "matchThreshold": 0,
            #     "specification": None,
            #     "specificationDetails": {},
            #     "dataType": "Date",
            #     "allowsDuplicateValues": True,
            #     "isNullable": False,
            #     "defaultValue": None,
            #     "averageValue": None,
            #     "valueList": [],
            #     "valueRangeFrom": "",
            #     "valueRangeTo": "",
            #     "sampleValues": [],
            #     "dataPatterns": [],
            #     "additionalProperties": { }
            #     }
            # }

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

    def test_find_all_data_classes(self):

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.find_all_data_classes(output_format="DICT")
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
            search_string = "DataClass::ISO-Date"
            start_time = time.perf_counter()
            response = m_client.find_data_classes(search_string,output_format="FORM")
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

    def test_get_data_class_by_name(self):
        name = "DataClass::ISO-Date"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_classes_by_name(name)
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

    def test_get_data_class_by_guid(self):
        guid = "67e8744f-447d-4d79-8272-a811a3048326"
        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            response = m_client.get_data_class_by_guid(guid, output_format="DICT")
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

    def test_link_nested_data_class(self):
        containing_guid = "e441f9f1-4dd0-4960-b11d-08a1b8c717f6"
        member_guid = "ca085aa8-c5bb-4a15-ab2b-73be43166f3c"

        try:
            m_client = DataDesigner(self.view_server, self.platform_url)

            m_client.create_egeria_bearer_token(self.user, self.password)
            start_time = time.perf_counter()
            m_client.link_nested_data_class(containing_guid, member_guid)
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
