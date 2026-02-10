"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module creates sample data for the COCO Sales Regions example.
"""
import os
from rich.console import Console
from rich.markdown import Markdown

from pyegeria.core.utils import dynamic_catch
from pyegeria import (
    settings, EgeriaTech,
    config_logging, print_basic_exception, PyegeriaAPIException, PyegeriaClientException
)

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_config = settings.Environment
config_logging()
console = Console(width=app_config.console_width)

client = EgeriaTech(app_config.egeria_view_server,
                      app_config.egeria_view_server_url,
                      EGERIA_USER, EGERIA_USER_PASSWORD)
token = client.create_egeria_bearer_token(client.user_id, client.user_pwd)
if token is None:
    console.print(f"Failed to create token for user {client.user_id}", style="bold red")
    exit(1)

try:

# First, create the reference data set
    ref_data_body = {
    "class" : "NewElementRequestBody",
      "isOwnAnchor": True,
      "parentAtEnd1": False,
      "properties": {
        "class" : "ReferenceDataSetProperties",
        "qualifiedName": "ReferenceDataSet::CocoPharmaceuticals::SalesTerritories",
        "identifier": "SALES-TERRITORIES-2026",
        "displayName": "Coco Pharmaceuticals Sales Territories",
        "description": "Geographical organization of sales territories for reporting.",
        "category": "Reference Data",
        "contentStatus" : "ACTIVE",
        "usage": "Used to consistently report on sales forecasts and actual sales.",
        "dataType" : "string",
        "scope" : "Global",
        "preferredValue" : "SALES-TERRITORIES-2026"
      }
    }
    # ref_data_guid = client.create_valid_value_definition(ref_data_body)
    # if ref_data_guid is None:
    #     console.print(f"Failed to create reference data set", style="bold red")
    #     exit(1)

    # Create a reference data value for Europe
    europe_body = {
              "class" : "NewElementRequestBody",
              "anchorGUID" : ref_data_guid,
              "isOwnAnchor": False,
              "parentGUID": ref_data_guid,
              "parentRelationshipTypeName": "ValidValueMember",
              "parentRelationshipProperties": {
                "class": "ValidValueMemberProperties",
                "isDefaultValue" : False
              },
              "parentAtEnd1": True,
              "properties": {
                "class" : "ReferenceDataValueProperties",
                "qualifiedName": "ReferenceDataSet::CocoPharmaceuticals::SalesTerritories::Europe",
                "displayName": "Europe",
                "description": "European sales territory encompassing EU counties and the United Kingdom.",
                "category": "Reference Data",
                "contentStatus" : "ACTIVE",
                "usage": "Used to consistently report on sales forecasts and actual sales.",
                "dataType" : "string",
                "scope" : "Global",
                "preferredValue" : "Europe"
              }
        }
    # europe_data_guid = client.create_valid_value_definition(europe_body)
    # if europe_data_guid is None:
    #     console.print(f"Failed to create reference data value for Europe", style="bold red")
    #     exit(1)

    # Create a reference data value for Eu
    eu_body = {
        "class": "NewElementRequestBody",
        "anchorGUID": "{{salesTerritoriesGUID}}",
        "isOwnAnchor": True,
        "parentGUID": "{{europeSalesTerritoriesGUID}}",
        "parentRelationshipTypeName": "ValidValueMember",
        "parentRelationshipProperties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": False
        },
        "parentAtEnd1": True,
        "properties": {
            "class": "ReferenceDataValueProperties",
            "qualifiedName": "ReferenceDataSet::CocoPharmaceuticals::SalesTerritories::EU",
            "displayName": "European Union (EU)",
            "description": "Sales territory encompassing European Union (EU) counties.",
            "category": "Reference Data",
            "contentStatus": "ACTIVE",
            "usage": "Used to consistently report on sales forecasts and actual sales.",
            "dataType": "string",
            "scope": "Global",
            "preferredValue": "European Union"
        }
    }
    eu_data_guid = client.create_valid_value_definition(eu_body)
    if eu_data_guid is None:
        console.print(f"Failed to create reference data value for the EU", style="bold red")
        exit(1)

    # Create a reference data value for the United Kingdom
    uk_body = {
        "class": "NewElementRequestBody",
        "anchorGUID": "{{salesTerritoriesGUID}}",
        "isOwnAnchor": False,
        "parentGUID": "{{europeSalesTerritoriesGUID}}",
        "parentRelationshipTypeName": "ValidValueMember",
        "parentRelationshipProperties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": False
        },
        "parentAtEnd1": True,
        "properties": {
            "class": "ReferenceDataValueProperties",
            "qualifiedName": "ReferenceDataSet::CocoPharmaceuticals::SalesTerritories::UK",
            "displayName": "United Kingdom (UK)",
            "description": "Sales territory encompassing Great Britain and Northern Ireland.",
            "category": "Reference Data",
            "contentStatus": "ACTIVE",
            "usage": "Used to consistently report on sales forecasts and actual sales.",
            "dataType": "string",
            "scope": "Global",
            "preferredValue": "United Kingdom"
        }
    }
    uk_data_guid = client.create_valid_value_definition(uk_body)
    if uk_data_guid is None:
        console.print(f"Failed to create reference data value for the UK", style="bold red")
        exit(1)

    # Create a reference data value for North America
    na_body = {
        "class": "NewElementRequestBody",
        "anchorGUID": "{{salesTerritoriesGUID}}",
        "isOwnAnchor": False,
        "parentGUID": "{{salesTerritoriesGUID}}",
        "parentRelationshipTypeName": "ValidValueMember",
        "parentRelationshipProperties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": False
        },
        "parentAtEnd1": True,
        "properties": {
            "class": "ReferenceDataValueProperties",
            "qualifiedName": "ReferenceDataSet::CocoPharmaceuticals::SalesTerritories::NA",
            "displayName": "North America (NA)",
            "description": "North American sales territory encompassing the United States (US) and Canada.",
            "category": "Reference Data",
            "contentStatus": "ACTIVE",
            "usage": "Used to consistently report on sales forecasts and actual sales.",
            "dataType": "string",
            "scope": "Global",
            "preferredValue": "North America"
        }
        }
    na_data_guid = client.create_valid_value_definition(na_body)
    if na_data_guid is None:
        console.print(f"Failed to create reference data value for North America", style="bold red")
        exit(1)

    # Create a reference data value for USA
    usa_body = {
        "class": "NewElementRequestBody",
        "anchorGUID": "{{salesTerritoriesGUID}}",
        "isOwnAnchor": False,
        "parentGUID": "{{naSalesTerritoriesGUID}}",
        "parentRelationshipTypeName": "ValidValueMember",
        "parentRelationshipProperties": {
            "class": "ValidValueMemberProperties",
            "isDefaultValue": False
        },
        "parentAtEnd1": True,
        "properties": {
            "class": "ReferenceDataValueProperties",
            "qualifiedName": "ReferenceDataSet::CocoPharmaceuticals::SalesTerritories::US",
            "displayName": "United States of America (USA)",
            "description": "Sales territory encompassing the United States of America.",
            "category": "Reference Data",
            "contentStatus": "ACTIVE",
            "usage": "Used to consistently report on sales forecasts and actual sales.",
            "dataType": "string",
            "scope": "Global",
            "preferredValue": "United States of America"
        }
        }
    usa_data_guid = client.create_valid_value_definition(usa_body)
    if usa_data_guid is None:
        console.print(f"Failed to create reference data value for USA", style="bold red")
        exit(1)

    output = (
              # f"* SALES-TERRITORIES-2026: {ref_data_guid}\n"
              # f"* Europe:\t\t\t{europe_data_guid}\n"
              f"* EU:\t\t\t\t{eu_data_guid}\n"
              f"* UK:\t\t\t\t{uk_data_guid}\n"
              f"* NA:\t\t\t\t{na_data_guid}\n"
              f"* USA:\t\t\t\t{usa_data_guid}\n"
              )
    console.print(Markdown(output))

except (PyegeriaAPIException, PyegeriaClientException) as e:
    print_basic_exception(e)
