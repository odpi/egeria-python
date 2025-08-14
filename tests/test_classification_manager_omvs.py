"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the classification manager view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import asyncio
import json
import time
from contextlib import nullcontext as does_not_raise

import pytest
from rich import print, print_json
from rich.console import Console

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.classification_manager_omvs import ClassificationManager
from pyegeria.core_omag_server_config import CoreServerConfig
from pyegeria.output_formatter import make_preamble, make_md_attribute

disable_ssl_warnings = True

platform_url = "https://localhost:9443"
view_server = "qs-view-server"

# c_client = ClassificationManager(view_server, platform_url)

user = "erinoverview"
password = "secret"

# element_guid = '4fe24e34-490a-43f0-a0d4-fe45ac45c663'
# element_guid = "a2915132-9d9a-4449-846f-43a871b5a6a0"
# element_guid = "b359e297-a565-414a-8213-fa423312ab36" # clinical trials management
# element_guid = "25b1791f-c2fb-4b93-b236-cad53739a9a2"  # Approved Hospital
element_guid = "58933d73-7f04-4899-99ce-bbd25826041a"  # a glossary term
relationship_type = "GovernedBy"

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
    # open_metadata_type_name = 'CertificationType'
    #
    # open_metadata_type_name = "DeployedDatabaseSchema"
    open_metadata_type_name = "DataField"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_elements(open_metadata_type_name)

    if type(response) is list:
        print(f"\n\tElement count is: {len(response)}")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True


def test_get_elements_by_property_value():
    # open_metadata_type_name = 'Project'
    # property_value = "Campaign:Clinical Trials Management"
    # open_metadata_type_name = "ValidValueDefinition"
    open_metadata_type_name = "InformationSupplyChainSegment"
    # property_value = "Unity Catalog Catalog"
    # property_names = ["name", "qualifiedName"]
    # open_metadata_type_name = "Asset"
    # property_value = "ClinicalTrials@CocoPharmaceuticals:set-up-clinical-trial"
    # property_value = "default"
    # property_names = ["name", "qualifiedName"]
    property_names = ["name","displayName",'qualifiedName']
    property_value = "first segment"
    # property_names = ["anchorGUID"]
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.get_elements_by_property_value(
            property_value, property_names, open_metadata_type_name
        )
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if type(result) is list:
            print(f"\n\tElement count is: {len(result)}")
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_elements_by_property_value():
    # open_metadata_type_name = 'Project'
    # property_value = "Campaign:Clinical Trials Management"
    # open_metadata_type_name = "ValidValueDefinition"
    # open_metadata_type_name = None
    # open_metadata_type_name = "ArchiveFile"
    open_metadata_type_name = "SolutionBlueprint"
    # open_metadata_type_name = None
    # property_names = ["name"]
    # property_value = "Set up new clinical trial"
    property_names = ["displayName"]
    property_value = "my_first_blueprint"

    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.find_elements_by_property_value(
            property_value, property_names, open_metadata_type_name
        )
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if type(result) is list:
            print(f"\n\tElement count is: {len(result)}")
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_element_by_guid():
    element_guid = '28ca67d8-9cb4-4bb9-9af8-9dce83ce3e17'
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.get_element_by_guid(element_guid)
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if type(result) is dict:
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_actor_for_guid():
    element_guid = "dcfd7e32-8074-4cdf-bdc5-9a6f28818a9d"
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.get_actor_for_guid(element_guid)
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if type(result) is dict:
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_guid_for_name():
    open_metadata_type_name = None
    # property_value = "Person:UK:324713"
    # property_value = "simple-metadata-store"
    # property_value = "Sustainability Glossary"
    property_value = "qs-view-server"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    start_time = time.perf_counter()
    result = c_client.get_guid_for_name(property_value)
    duration = time.perf_counter() - start_time
    print(f"\n\tDuration was {duration} seconds")
    if type(result) is list:
        print(f"\n\tElement count is: {len(result)}")
        print_json(data=result)
    elif type(result) is str:
        console.print("\n\n\t Response is " + result)

    assert True


def test_get_element_guid_by_unique_name():
    open_metadata_type_name = None
    # property_value = "Person:UK:324713"
    # property_value = "simple-metadata-store"
    property_value = "qs-view-server"

    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    start_time = time.perf_counter()
    result = c_client.get_element_guid_by_unique_name(property_value, "displayName")
    duration = time.perf_counter() - start_time
    print(f"\n\tDuration was {duration} seconds")
    if type(result) is list:
        print(f"\n\tElement count is: {len(result)}")
        print_json(data=result)
    elif type(result) is str:
        console.print("\n\n\t Response is " + result)

    assert True


def test_get_element_by_unique_name():
    open_metadata_type_name = None
    # property_value = "Person:UK:324713"
    property_value = "SupplyChainSegment::first segment"

    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    start_time = time.perf_counter()
    result = c_client.get_element_by_unique_name(property_value, "qualifiedName")
    duration = time.perf_counter() - start_time
    print(f"\n\tDuration was {duration} seconds")
    if type(result) is dict:
        print(f"\n\tElement count is: {len(result)}")
        print_json(data=result)
    elif type(result) is str:
        console.print("\n\n\t Response is " + result)

    assert True


def test_get_elements_by_classification():
    # open_metadata_type_name = "Project"
    # open_metadata_type_name = "DeployedDatabaseSchema"
    open_metadata_type_name = "DataStructure"
    # classification = "GovernanceProject"
    classification = "DataSpec"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_elements_by_classification(
        classification, open_metadata_type_name
    )

    if type(response) is list:
        print("Result = \n")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is: " + response)

    assert True


def test_get_elements_by_classification_with_property_value():
    # open_metadata_type_name = "Project"
    open_metadata_type_name = None
    classification = "DataSpec"
    # property_value = "Collection"
    # property_names = ["anchorTypeName"]
    property_value = ""
    property_names = [""]
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_elements_by_classification_with_property_value(
            classification, property_value, property_names, open_metadata_type_name
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_elements_by_classification_with_property_value():
    # classification = "GovernanceProject"
    # open_metadata_type_name = "Project"
    # property_value = "Clinical Trials"
    # property_names = ["name", "qualifiedName"]
    #
    classification = "DataSpec"
    # open_metadata_type_name = "DeployedDatabaseSchema"
    open_metadata_type_name = None
    property_value = ""
    property_names = ["displayName"]
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)

    start_time = time.perf_counter()
    response = c_client.find_elements_by_classification_with_property_value(
        classification, property_value, property_names, open_metadata_type_name
    )
    duration = time.perf_counter() - start_time
    print(
        f"\n\tDuration was {duration:.2f} seconds, Type: {type(response)}, Element count is {len(response)}"
    )
    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is: " + response)

    assert True


def test_find_anchored_elements_with_property_value():
    classification = "Anchors"
    open_metadata_type_name = None
    property_value = "PostgreSQL Server"
    # property_names = ["ServerCapability", "anchorTypeName"]
    property_names = ["name"]
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.find_elements_by_classification_with_property_value(
        classification, property_value, property_names, open_metadata_type_name
    )

    if type(response) is list:
        print("Response payload is: \n")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True


def test_get_all_related_elements():
    # open_metadata_type_name = 'Project'
    open_metadata_type_name = None
    c_client = ClassificationManager(view_server, platform_url)
    # element_guid = "d156faa6-90cf-4be8-b3c1-c002f3e9a0e5" # branch database
    element_guid = "da0442bf-818f-406b-99dc-83b72605cc98"
    # element_guid = "8b9cce34-ff42-4f9d-b4b3-6317c8a767c3"  # Retail schema
    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_related_elements(
        element_guid, None, open_metadata_type_name
    )

    if type(response) is list:
        print(f"\n\tElement count is: {len(response)}")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True


def test_get_related_elements():
    # open_metadata_type_name = 'CertificationType'
    element_guid = "d71c7ee2-b414-4c8f-bf9b-b16bd3601855"
    # open_metadata_type_name = "Organization"
    # open_metadata_type_name = "CSVFile"
    # open_metadata_type_name = "InformationSupplyChain"
    open_metadata_type_name = None
    # element_guid = "8dca6e76-d454-4344-9c93-faa837a1a898"
    # relationship_type = "DataContentForDataSet"
    relationship_type = "CollectionMembership"
    # relationship_type = "InformationSupplyChainComposition"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_related_elements(
        element_guid, relationship_type, open_metadata_type_name
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is:\n " + response)

    assert True


def test_get_related_elements_with_property_value():
    # open_metadata_type_name = 'Project'
    open_metadata_type_name = None
    relationship_type = "Certification"
    property_value = "Partner"
    property_names = [
        "teamType",
    ]

    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_related_elements_with_property_value(
            element_guid,
            relationship_type,
            property_value,
            property_names,
            open_metadata_type_name,
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
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_related_elements_with_property_value():
    # open_metadata_type_name = 'Project'
    open_metadata_type_name = None
    property_value = "Clinical Trials Management"
    property_names = ["name", "qualifiedName"]
    # property_value = "Partner"
    # property_names = ["teamType"]

    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.find_related_elements_with_property_value(
        element_guid,
        relationship_type,
        property_value,
        property_names,
        open_metadata_type_name,
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True


def test_get_relationships():
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    relationship_type = "Certification"
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
            relationship_type, property_value, property_names
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
        UserNotAuthorizedException,
    ) as e:
        print_exception_response(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_relationships_with_property_value():
    property_value = "Clinical Trials"
    property_names = ["name", "qualifiedName"]
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.find_relationships_with_property_value(
        relationship_type, property_value, property_names
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True


def test_retrieve_instance_for_guid():
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    element_guid = "bda24e8a-4798-4cc0-b693-b09c688d5a6f"
    response = c_client.retrieve_instance_for_guid(element_guid)

    if type(response) is dict:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True
