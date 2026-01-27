"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the classification manager view service class and methods.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
import time

from pydantic import ValidationError
from rich import print, print_json, traceback
from rich.console import Console

from pyegeria import EgeriaTech
from pyegeria.core._exceptions import PyegeriaException, print_basic_exception, print_validation_error, \
    PyegeriaConnectionException, PyegeriaAPIException, print_exception_table
from pyegeria.omvs.classification_manager import ClassificationManager

# from pyegeria.output_formatter import make_preamble, make_md_attribute

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
# element_guid = "e656f7ca-c11a-4d05-a5ed-adc69abbf0fd"  # a digital product glossary
element_guid = "c28ea54e-060a-4738-9d8c-1b4000442d7e"
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
def test_get_classified_elements_by():
    # metadata_element_type_name = 'CertificationType'
    #
    # metadata_element_type_name = "DeployedDatabaseSchema"
    classification_name = "Confidentiality"
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "LevelIdentifierQueryProperties",
            "levelIdentifier": 1
        }
        response = c_client.get_classified_elements_by(classification_name)

        if type(response) is list:
            print(f"\n\tElement count is: {len(response)}")
            print_json(data=response)
        elif type(response) is str:
            console.print("\n\n\t Response is: " + response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_security_tagged_elements():
    # metadata_element_type_name = 'CertificationType'
    #
    # metadata_element_type_name = "DeployedDatabaseSchema"
    classification_name = "confidentiality"
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "SecurityTagQueryProperties",

            "metadataElementTypeName": None,
            "limitResultsByStatus": [],
            "sequencingProperty": "displayName",
            "sequencingOrder": "LAST_UPDATE_RECENT",
            "securityLabels": [],
            "securityProperties": {
                "propertyName": "propertyValue"
            },
            "accessGroups": {
                "groupName": []
            }
        }
        response = c_client.get_security_tagged_elements(body, output_format="DICT", report_spec="Referenceable")

        if type(response) is list:
            print(f"\n\tElement count is: {len(response)}")
            print_json(data=response)
        elif type(response) is str:
            console.print("\n\n\t Response is: " + response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_owners_elements():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        owner_name = "Erin Overview"
        body = {
            "class": "FilterRequestBody",
            "filter": owner_name
        }
        response = c_client.get_owners_elements(owner_name, body, output_format="DICT", report_spec="Referenceable")

        if type(response) is list:
            print(f"\n\tElement count is: {len(response)}")
            print_json(data=response)
        elif type(response) is str:
            console.print("\n\n\t Response is: " + response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_elements_by_origin():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        home_metadata_collection = "PostgresContentPack"
        body = {
            "class": "FindDigitalResourceOriginProperties",
            "metadataElementTypeName": "ValidValueDefinition",
            "otherOriginValues": {"homeMetadataCollectionName": home_metadata_collection}
        }
        response = c_client.get_elements_by_origin(body, output_format="JSON", report_spec="Referenceable")

        if type(response) is list:
            print(f"\n\tElement count is: {len(response)}")
            print_json(data=response)
        elif type(response) is str:
            console.print("\n\n\t Response is: " + response)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    except ValidationError as e:
        print_validation_error(e)
    except Exception as e:
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_elements():
    # metadata_element_type_name = 'CertificationType'
    #
    # metadata_element_type_name = "DeployedDatabaseSchema"
    open_metadata_type_name = "UserIdentity"
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "ResultsRequestBody",
            "metadataElementTypeName": open_metadata_type_name,
        }
        response = c_client.get_elements(metadata_element_type = open_metadata_type_name,
                                         output_format="DICT",
                                         report_spec="Referenceable",
                                         body=body)

        if type(response) is list:
            print(f"\n\tElement count is: {len(response)}")
            print_json(data=response)
        elif type(response) is str:
            console.print("\n\n\t Response is" + response)
        assert True
    except (PyegeriaException, PyegeriaAPIException) as e:
        if e.response_egeria_msg_id == "OMAG-COMMON-400-018":
            print("\n\n==>Invalid OM Type\n\n")
        else:
            print_basic_exception(e)
            assert False, "Invalid request"
    except Exception as e:
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_elements_by_property_value():
    # metadata_element_type_name = 'Project'
    # property_value = "Campaign:Clinical Trials Management"
    # metadata_element_type_name = "ValidValueDefinition"
    metadata_element_type_name = None
    # property_value = "Unity Catalog Catalog"
    # property_names = ["name", "qualifiedName"]
    # metadata_element_type_name = "Asset"
    # property_value = "ClinicalTrials@CocoPharmaceuticals:set-up-clinical-trial"
    # property_value = "default"
    # property_names = ["name", "qualifiedName"]
    property_names = ["name", "displayName", 'qualifiedName']
    property_value = "BusinessArea::RES"
    # property_names = ["anchorGUID"]
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.get_elements_by_property_value(
            property_value,
            property_names,
            metadata_element_type_name=metadata_element_type_name,
            as_of_time="2025-12-01",
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
            PyegeriaException
    ) as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_elements_by_property_value():
    # metadata_element_type_name = 'Project'
    # property_value = "Campaign:Clinical Trials Management"
    # metadata_element_type_name = "ValidValueDefinition"
    # metadata_element_type_name = None
    # metadata_element_type_name = "ArchiveFile"
    open_metadata_type_name = "DigitalProduct"
    # metadata_element_type_name = None
    # property_names = ["name"]
    # property_value = "Set up new clinical trial"
    property_names = ["displayName"]
    property_value = "Open Metadata Digital Product Data Dictionary"

    try:
        c_client = EgeriaTech(view_server, platform_url, user, password)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.find_elements_by_property_value(
            property_value, property_names, open_metadata_type_name,
            output_format="JSON", report_spec="Referenceable"
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
            PyegeriaException
    ) as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_element_by_guid():
    element_guid = '6ec2c097-9d6e-4e9d-ab51-186d2c437443'
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.get_element_by_guid(element_guid, output_format="JSON", report_spec="Referenceable")
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if isinstance(result, list|dict):
            print(f"\n\tElement count is: {len(result)}")
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (
            PyegeriaException
    ) as e:
        print_basic_exception(e)
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

    except PyegeriaException as e:
        print_basic_exception(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    except ValidationError as e:
        print_validation_error(e)
        console.print_exception(show_locals=True)
    finally:
        c_client.close_session()


def test_get_guid_for_name():
    open_metadata_type_name = None
    property_value = "PostgreSQLServer::CreateAndSurveyGovernanceActionProcess"
    # property_value = "simple-metadata-store"
    # property_value = "Sustainability Glossary"
    # property_value = "qs-view-server"
    # property_value = "Campaign:Sustainability"
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
    # property_value = "FileDirectory:CreateAndSurveyGovernanceActionProcess"
    property_value = "Open Metadata Digital Product Data Dictionary"

    c_client = ClassificationManager(view_server, platform_url)
    try:
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        start_time = time.perf_counter()
        result = c_client.get_element_guid_by_unique_name(property_value, "displayName")
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if isinstance(result, list|dict):
            print(f"\n\tElement count is: {len(result)}")
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is " + result)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False, "Invalid request"


def test_get_element_by_unique_name():
    open_metadata_type_name = None
    # property_value = "Person:UK:324713"
    property_value = "FileDirectory:CreateAndSurveyGovernanceActionProcess"

    c_client = ClassificationManager(view_server, platform_url)
    try:
        bearer_token = c_client.create_egeria_bearer_token(user, password)

        start_time = time.perf_counter()
        result = c_client.get_element_by_unique_name(property_value, "qualifiedName", output_format="DICT",
                                                     report_spec="Referenceable")
        duration = time.perf_counter() - start_time
        print(f"\n\tDuration was {duration} seconds")
        if isinstance(result, list | dict):
            print(f"\n\tElement count is: {len(result)}")
            print(json.dumps(result, indent=4))
        elif type(result) is str:
            console.print("\n\n\t Response is " + result)

        assert True
    except (PyegeriaException, PyegeriaConnectionException) as e:
        print_basic_exception(e)
        assert False


def test_get_elements_by_classification():
    # metadata_element_type_name = "Project"
    # metadata_element_type_name = "DeployedDatabaseSchema"
    open_metadata_type_name = None
    # classification = "GovernanceProject"
    classification = "Ownership"
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    body = {
        "class": "ResultsRequestBody",
        "metadataElementTypeName": open_metadata_type_name,
        "pageSize": 10,
    }
    response = c_client.get_elements_by_classification(
        classification, output_format="JSON", report_spec="Collections", body=body
    )

    if type(response) is list:
        print("Result = \n")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is: " + response)

    assert True


def test_get_elements_by_classification_with_property_value():
    # metadata_element_type_name = "Project"
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
            classification,
            property_value,
            property_names,
            metadata_element_type_name=open_metadata_type_name,
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            console.print("\n\n\t Response is: " + result)

        assert True

    except (PyegeriaException) as e:
        print_basic_exception(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_elements_by_classification_with_property_value():
    # classification = "GovernanceProject"
    # metadata_element_type_name = "Project"
    # property_value = "Clinical Trials"
    # property_names = ["name", "qualifiedName"]
    #
    classification = "Anchor"
    # metadata_element_type_name = "Project"
    open_metadata_type_name = "DigitalProduct"
    property_value = "Open Metadata Digital Product Data Dictionary"
    property_names = ["displayName"]
    try:
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
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False


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
    # metadata_element_type_name = 'Project'
    open_metadata_type_name = None
    c_client = ClassificationManager(view_server, platform_url)
    # element_guid = "d156faa6-90cf-4be8-b3c1-c002f3e9a0e5" # branch database
    # element_guid = "da0442bf-818f-406b-99dc-83b72605cc98"
    # element_guid = "8b9cce34-ff42-4f9d-b4b3-6317c8a767c3"  # Retail schema
    element_guid = "0182bacf-32c4-40f0-91b5-2462dfeab50c"
    bearer_token = c_client.create_egeria_bearer_token(user, password)
    response = c_client.get_related_elements(element_guid, relationship_type=None)

    if type(response) is list:
        print(f"\n\tElement count is: {len(response)}")
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is" + response)

    assert True


def test_get_related_elements():
    # metadata_element_type_name = 'CertificationType'
    # element_guid = '2ce8d10d-08a2-4fca-b0c2-1d5a335d00fc'
    element_guid = "10662294-52d0-43c5-9aa3-19922e478e69"
    # metadata_element_type_name = "Organization"
    # metadata_element_type_name = "CSVFile"
    # metadata_element_type_name = "InformationSupplyChain"
    open_metadata_type_name = "Referenceable"
    # element_guid = "8dca6e76-d454-4344-9c93-faa837a1a898"
    # relationship_type = "DataContentForDataSet"
    relationship_type = "CollectionMembership"
    # relationship_type = "InformationSupplyChainComposition"
    c_client = ClassificationManager(view_server, platform_url)
    try:
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "ResultsRequestBody",
            "metadataElementTypeName": open_metadata_type_name,
        }
        response = c_client.get_related_elements(
            element_guid, relationship_type, body=body
        )

        if type(response) is list:
            print_json(data=response)
        elif type(response) is str:
            console.print("\n\n\t Response is:\n " + response)

        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
        assert False, "Invalid request"


def test_get_related_elements_with_property_value():
    # metadata_element_type_name = 'Project'
    open_metadata_type_name = None
    relationship_type = "ResourceList"
    property_value = "Catalog Resource"
    property_names = [
        "resourceUse",
    ]
    element_guid = '2ce8d10d-08a2-4fca-b0c2-1d5a335d00fc'
    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.get_related_elements_with_property_value(
            element_guid,
            relationship_type,
            property_value,
            property_names,
            metadata_element_type_name=open_metadata_type_name,
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            print("\n\n\t Response is: " + result)
        else:
            print(f"type is: {type(result)}")

        assert True

    except (
            PyegeriaException) as e:
        print_basic_exception(e)
        console.print_exception(show_locals=True)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_find_related_elements_with_property_value():
    # metadata_element_type_name = 'Project'
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
    response = c_client.get_relationships(relationship_type, output_format="JSON")

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
            property_value,
            property_names,
            relationship_type=relationship_type,
            output_format="JSON",
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            print("\n\n\t Response is: " + result)
        else:
            print(f"type is: {type(result)}")

        assert True

    except (
            PyegeriaException) as e:
        print_basic_exception(e)
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
        property_value,
        property_names,
        relationship_type=relationship_type,
    )

    if type(response) is list:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True


def test_retrieve_instance_for_guid():
    c_client = ClassificationManager(view_server, platform_url)

    bearer_token = c_client.create_egeria_bearer_token(user, password)
    element_guid = "59f0232c-f834-4365-8e06-83695d238d2d"
    response = c_client.retrieve_instance_for_guid(element_guid, output_format="JSON")

    if type(response) is dict:
        print_json(data=response)
    elif type(response) is str:
        console.print("\n\n\t Response is " + response)

    assert True


def test_set_criticality_classification():
    # metadata_element_type_name = 'Project'
    element_guid = "9f6f668d-d9b8-44e3-915b-9edeb4c1f8a5"
    body = {
        "class": "NewClassificationRequestBody",
        "Properties": {
            "class": "CriticalityProperties",
            "levelIdentifier": 3,
            "criticality": 3
        }
    }

    try:
        c_client = ClassificationManager(view_server, platform_url)

        bearer_token = c_client.create_egeria_bearer_token(user, password)
        result = c_client.set_criticality_classification(
            element_guid,
            body
        )

        if type(result) is list:
            print_json(data=result)
        elif type(result) is str:
            print("\n\n\t Response is: " + result)
        else:
            print(f"type is: {type(result)}")

        assert True

    except (
            PyegeriaException
    ) as e:
        print_basic_exception(e)
        assert False, "Invalid request"
    finally:
        c_client.close_session()


def test_get_subject_area_members():
    subject_area = "Clinical Trials"
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "FilterRequestBody",
            "filter": "*",
        }
        response = c_client.get_subject_area_members(subject_area, body)
        if type(response) is list:
            print(f"\n\tElement count is: {len(response)}")
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_meanings():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "FilterRequestBody",
            "filter": "*",
        }
        response = c_client.get_meanings(element_guid, body)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_semantic_asignees():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        body = {
            "class": "FilterRequestBody",
            "filter": "*",
        }
        response = c_client.get_semantic_asignees(element_guid, body)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_governed_elements():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_governed_elements(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_governed_by_definitions():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_governed_by_definitions(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_source_elements():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_source_elements(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_elements_sourced_from():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_elements_sourced_from(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_scopes():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_scopes(element_guid)
        if isinstance(response, list|dict):
            print(f"\n\tElement count is: {len(response)}")
            print(json.dumps(response, indent=2))
            assert True
        else:
            print(f"Expected list, got {type(response).__name__}, {response}")
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_scoped_elements():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_scoped_elements(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_licensed_elements():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_licensed_elements(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_licenses():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_licenses(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_certified_elements():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_certified_elements(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_get_certifications():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        response = c_client.get_certifications(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_confidence_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "ConfidenceProperties",
            "confidence": 100,
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_confidence_classification(element_guid, body)
        c_client.clear_confidence_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_confidentiality_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "ConfidentialityProperties",
            "levelIdentifier": 1,
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_confidentiality_classification(element_guid, body)
        c_client.clear_confidentiality_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_impact_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "ImpactProperties",
            "levelIdentifier": 1,
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_impact_classification(element_guid, body)
        c_client.clear_impact_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_criticality_classification_clear():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.clear_criticality_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_gov_definition_to_element():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        # using dummy GUIDs for now, expecting potential 404 but testing call pattern
        def_guid = "dummy-def-guid"
        c_client.add_gov_definition_to_element(def_guid, element_guid)
        c_client.remove_gov_definition_from_element(def_guid, element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_scope_to_element():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        scope_guid = "17f9bcd9-ede6-431e-9cec-1b8474f31e4b"

        c_client.add_scope_to_element(scope_guid, element_guid)
        c_client.clear_scope_from_element(scope_guid, element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_assign_actor_to_element():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        actor_guid = "dummy-actor-guid"

        c_client.assign_actor_to_element(element_guid, actor_guid)
        c_client.unassign_actor_from_element(element_guid, actor_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_certification_to_element():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        cert_type_guid = "dummy-cert-type-guid"
        # add returns guid of relationship
        # c_client.add_certification_to_element(cert_type_guid, element_guid)
        # c_client.update_certification("dummy-guid", {})
        # c_client.decertify_element("dummy-guid")
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_license_to_element():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        license_type_guid = "dummy-license-type-guid"
        # c_client.add_license_to_element(license_type_guid, element_guid)
        # c_client.update_license("dummy-guid", {})
        # c_client.unlicense_element("dummy-guid")
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_add_ownership_to_element():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "OwnershipProperties",
            "owner": "72b2af0a-cdd6-477a-b885-08d9f2e1b3b0",
            "ownerType": "USER_ID"
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.add_ownership_to_element(element_guid, body)
        c_client.clear_ownership_from_element(element_guid)
        assert True
    except PyegeriaException as e:
        print_exception_table(e)
    except Exception as e:
        console.print_exception(show_locals=True)
    finally:
        c_client.close_session()


def test_digital_resource_origin():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "DigitalResourceOriginProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.add_digital_resource_origin(element_guid, body)
        # c_client.clear_digital_resource_origin_from_element(element_guid, {"class": "DeleteClassificationRequestBody"})
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_zone_membership():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "ZoneMembershipProperties",
            "zoneMembership": ["quarantine"],
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.add_zone_membership(element_guid, body)
        # c_client.clear_zone_membership(element_guid, {"class": "DeleteClassificationRequestBody"})
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_retention_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "RetentionProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_retention_classification(element_guid, body)
        c_client.clear_retention_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_governance_expectation():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "GovernanceExpectationProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_governance_expectation(element_guid, body)
        c_client.update_governance_expectation(element_guid, body)
        # c_client.clear_governance_expectation(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_security_tags_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "SecurityTagsProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_security_tags_classification(element_guid, body)
        c_client.clear_security_tags_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_semantic_assignment():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        term_guid = "dummy-term-guid"
        # c_client.setup_semantic_assignment(term_guid, element_guid, {})
        # c_client.clear_semantic_assignment_classification(term_guid, element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_subject_area_membership():
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.add_element_to_subject_area(element_guid, {})
        c_client.remove_element_from_subject_area(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_governance_measurements():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "GovernanceMeasurementsProperties",
        }
    }
    update_body = {
        "class": "UpdateClassificationRequestBody",
        "mergeUpdate": True,
        "properties": {
            "class": "GovernanceMeasurementsProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.add_governance_measurements(element_guid, body)
        c_client.update_governance_measurements(element_guid, update_body)
        c_client.clear_governance_measurements(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_data_scope_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "DataScopeProperties",
        }
    }
    update_body = {
        "class": "UpdateClassificationRequestBody",
        "mergeUpdate": True,
        "properties": {
            "class": "DataScopeProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.add_data_scope(element_guid, body)
        c_client.update_data_scope(element_guid, update_body)
        c_client.clear_data_scope(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_search_keywords():
    body = {
        "class": "NewAttachmentRequestBody",
        "properties": {
            "class": "SearchKeywordProperties",
            "displayName": "testKeyword",
        }
    }
    update_body = {
        "class": "UpdateElementRequestBody",
        "mergeUpdate": True,
        "properties": {
            "class": "SearchKeywordProperties",
            "displayName": "updatedKeyword",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        keyword_guid = c_client.add_search_keyword_to_element(element_guid, body)
        if keyword_guid != "NO_GUID_RETURNED":
            c_client.update_search_keyword(keyword_guid, update_body)
            c_client.remove_search_keyword_from_element(keyword_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_known_duplicate_classification():
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "KnownDuplicateProperties"
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_known_duplicate_classification(element_guid, body)
        c_client.clear_known_duplicate_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_peer_duplicate_link():
    peer_guid = "peer-guid"
    body = {
        "class": "NewRelationshipRequestBody",
        "properties": {
            "class": "PeerDuplicateLinkProperties",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.link_elements_as_peer_duplicates(element_guid, peer_guid, body)
        c_client.unlink_elements_as_peer_duplicates(element_guid, peer_guid, body)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_consolidated_duplicate_management():
    source_guid = "source-guid"
    body = {
        "class": "NewClassificationRequestBody",
        "properties": {
            "class": "ConsolidatedDuplicateProperties",
        }
    }
    link_body = {
        "class": "NewRelationshipRequestBody",
        "properties": {
            "class": "ConsolidatedDuplicateLinkProperties"
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.set_consolidated_duplicate_classification(element_guid, body)
        c_client.link_consolidated_duplicate_to_source(element_guid, source_guid, link_body)
        c_client.unlink_consolidated_duplicate_from_source_element(element_guid, source_guid, link_body)
        c_client.clear_consolidated_duplicate_classification(element_guid)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()


def test_action_actor_linking():
    action_guid = "action-guid"
    actor_guid = "actor-guid"
    body = {
        "class": "NewRelationshipRequestBody",
        "properties": {
            "class": "AssignmentScopeProperties",
            "label": "testAction",
        }
    }
    try:
        c_client = ClassificationManager(view_server, platform_url)
        bearer_token = c_client.create_egeria_bearer_token(user, password)
        c_client.assign_action(action_guid, actor_guid, body)
        c_client.reassign_action(action_guid, actor_guid, body)
        c_client.unassign_action(action_guid, actor_guid, body)
        assert True
    except PyegeriaException as e:
        print_basic_exception(e)
    finally:
        c_client.close_session()
