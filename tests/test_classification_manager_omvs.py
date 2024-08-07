"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the classification manager view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import time

import pytest
import asyncio
import json
from rich import print, print_json
from rich.console import Console

from contextlib import nullcontext as does_not_raise

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.core_omag_server_config import CoreServerConfig

from pyegeria.classification_manager_omvs import ClassificationManager

disable_ssl_warnings = True

platform_url = "https://localhost:9443"
view_server = "view-server"

# c_client = ClassificationManager(view_server, platform_url)

user = "erinoverview"
password = "secret"

# element_guid = '4fe24e34-490a-43f0-a0d4-fe45ac45c663'
# element_guid = "a2915132-9d9a-4449-846f-43a871b5a6a0"
# element_guid = "b359e297-a565-414a-8213-fa423312ab36" # clinical trials management
element_guid = "25b1791f-c2fb-4b93-b236-cad53739a9a2" # Approved Hospital
relationship_type= "GovernedBy"

# bearer_token = c_client.create_egeria_bearer_token(user, password)
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


#
##
#
def test_get_elements():
    open_metadata_type_name = 'CertificationType'
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_elements(
        open_metadata_type_name
    )

    if type(response) is list:
        print(f"\n\tElement count is: {len(response)}")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True


def test_get_elements_by_property_value():
    open_metadata_type_name = 'Project'
    property_value = "Campaign:Clinical Trials Management"
    property_names = ["name", "qualifiedName"]
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_elements_by_property_value(
            property_value,
            property_names,
            open_metadata_type_name
        )

        if type(result) is list:
            print(f"\n\tElement count is: {len(result)}")

            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_elements_by_property_value():
    open_metadata_type_name = 'CertificationType'
    property_value = 'Approved Hospital'
    property_names = ["name", "qualifiedName", "title"]
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    result = c_client.find_elements_by_property_value(
        property_value,
        property_names,
        open_metadata_type_name
    )

    if type(result) is list:
        print(f"\n\tElement count is: {len(result)}")
        print_json(data=result)
    elif type(result) is str:
        console.print("\n\n\t Response is" + result)

    assert True


def test_get_elements_by_classification():
    open_metadata_type_name = 'Project'
    classification = "GovernanceProject"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_elements_by_classification(classification,
        open_metadata_type_name
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True


def test_get_elements_by_classification_with_property_value():
    open_metadata_type_name = 'Project'
    classification = "GovernanceProject"
    property_value = "Clinical Trials"
    property_names = ["name", "qualifiedName"]
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_elements_by_classification_with_property_value(
            classification,
            property_value,
            property_names,
            open_metadata_type_name
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_elements_by_classification_with_property_value():
    classification = "GovernanceProject"
    open_metadata_type_name = 'Project'
    property_value = 'Clinical Trials'
    property_names = ["name", "qualifiedName"]
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.find_elements_by_classification_with_property_value(
        classification,
        property_value,
        property_names,
        open_metadata_type_name
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True

def test_get_all_related_elements():
    # open_metadata_type_name = 'Project'
    open_metadata_type_name = None
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_all_related_elements(element_guid,open_metadata_type_name)

    if type(response) is list:
        print(f"\n\tElement count is: {len(response)}")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True

def test_get_related_elements():
    # open_metadata_type_name = 'CertificationType'

    # open_metadata_type_name = "Organization"
    open_metadata_type_name = None
    relationship_type = "Certification"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_related_elements(element_guid,relationship_type,open_metadata_type_name)

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is: " + response)

    assert True

def test_get_related_elements_with_property_value():
    # open_metadata_type_name = 'Project'
    open_metadata_type_name = None
    relationship_type = "Certification"
    property_value = "Partner"
    property_names = ["teamType", ]

    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_related_elements_with_property_value(
            element_guid,relationship_type,
            property_value,
            property_names,
            open_metadata_type_name
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            print("\n\n\t Response is: " + result)
        else:
            print(f"type is: {type(result)}")

        assert True

    except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_related_elements_with_property_value():
    # open_metadata_type_name = 'Project'
    open_metadata_type_name = None
    # property_value = 'Clinical Trials Management'
    # property_names = ["name", "qualifiedName"]
    property_value = "Partner"
    property_names = ["teamType" ]

    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.find_related_elements_with_property_value(
        element_guid,
        relationship_type,
        property_value,
        property_names,
        open_metadata_type_name
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True


def test_get_relationships():
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_relationships(relationship_type)

    if type(response) is list:
        print(f"\n\tElement count is: {len(response)}")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is: " + response)

    assert True

def test_get_relationships_with_property_value():
    property_value = "Organization:Hampton Hospital"
    property_names = ["name", "qualifiedName"]
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_relationships_with_property_value(
            relationship_type,
            property_value,
            property_names
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            print("\n\n\t Response is: " + result)
        else:
            print(f"type is: {type(result)}")

        assert True

    except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_relationships_with_property_value():
    property_value = 'Clinical Trials'
    property_names = ["name", "qualifiedName"]
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.find_relationships_with_property_value(
        relationship_type,
        property_value,
        property_names
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True

def test_retrieve_instance_for_guid():
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    element_guid = "456cacde-a891-4e5a-bd3f-9fa0eeaa792c"
    response = c_client.retrieve_instance_for_guid(
        element_guid
    )

    if type(response) is dict:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True
