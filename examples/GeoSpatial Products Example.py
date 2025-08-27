"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides a simple example for building out some GeoSpatial Digital Products.


"""
import os
import time

from loguru import logger
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import pydevd_pycharm

from pyegeria import (
    EgeriaTech,
    CollectionManager,
    NO_ELEMENTS_FOUND,

)
from pyegeria.config import settings, get_app_config
from pyegeria.logging_configuration import config_logging
from pyegeria._output_formats import (select_output_format_set, get_output_format_set_heading, get_output_format_set_description)
from pyegeria._exceptions_new import (PyegeriaException, print_basic_exception, print_validation_error,
                                      PyegeriaInvalidParameterException, PyegeriaConnectionException,
                                      PyegeriaAPIException, PyegeriaUnknownException, print_exception_table
                                      )
from pydantic import ValidationError
from pyegeria import EgeriaTech

EGERIA_USER = os.environ.get("EGERIA_USER", "erinoverview")
EGERIA_USER_PASSWORD = os.environ.get("EGERIA_USER_PASSWORD", "secret")

app_settings = get_app_config()
app_config = app_settings.Environment
config_logging()
logger.enable("pyegeria")
logger.info(f"Console width is {app_config.console_width}")

view_server = app_config.egeria_view_server
view_url = app_config.egeria_view_server_url
user = app_settings.User_Profile.user_name
user_pass = app_settings.User_Profile.user_pwd


console = Console(
    style="bold bright_white on black",
    width=app_config.console_width,
    force_terminal=not app_config.egeria_jupyter,
    )




try:
    client = EgeriaTech(view_server, view_url, user, user_pass)

    token = client.create_egeria_bearer_token()
    start_time = time.perf_counter()
    logger.info("Starting to create GeoSpatial Products")
    display_name = "GeoSpatial Root"
    description = "This is the root of the GeoSpatial work"
    category = "GeoSpatial"


    print("First we'll set up a number of folders to support the work.")
    #
    # Root Folder
    #
    root = client.get_collections_by_name(display_name)
    if isinstance(root, dict | list):
        root_guid = root[0]['elementHeader']['guid']
        print(f"Found root guid of {root_guid}")
    else:
        root_guid = client.create_root_collection(
            display_name=display_name,
            description=description,
            category=category
            )
        logger.success(f"Created root collection {root_guid}")
    #
    # Digital Products Marketplace
    #
    display_name = "Digital Products MarketPlace"
    description = "This is the digital products marketplace"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {
        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {

        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": root_guid,
        "parentGUID": root_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    marketplace = client.get_collections_by_name(qualified_name)
    if isinstance(marketplace, dict | list):
        marketplace_guid = marketplace[0]['elementHeader']['guid']
        print(f"Found marketplace guid of {marketplace_guid}")
    else:
        marketplace_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder collection for marketplace: {marketplace_guid}")
    #
    # GeoSpatial Products folder
    #
    display_name = "GeoSpatial Products"
    description = "GeoSpatial product offerings"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {
        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": marketplace_guid,
        "parentGUID": marketplace_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    geo_prods = client.get_collections_by_name(qualified_name)
    if isinstance(geo_prods, dict | list):
        geo_prods_guid = geo_prods[0]['elementHeader']['guid']
        print(f"Found geo_prods guid of {geo_prods_guid}")
    else:
        geo_prods_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder collection for geoprods: {geo_prods_guid}")
    #
    #   Agricultural Products Folder
    #
    display_name = "Agricultural Products"
    description = "Agricultural product offerings"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {

        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {

        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": marketplace_guid,
        "parentGUID": marketplace_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    ag_prods = client.get_collections_by_name(qualified_name)
    if isinstance(ag_prods, dict | list):
        ag_prods_guid = ag_prods[0]['elementHeader']['guid']
        print(f"Found ag_prods guid of {ag_prods_guid}")
    else:
        ag_prods_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder collection for  ag products: {ag_prods_guid}")
    #
    #   Folder to hold Prepared Imagery Products
    #
    display_name = "Prepared Imagery Products"
    description = "Imagery products that are ready for consumption"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {
        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": root_guid,
        "parentGUID": root_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    prepared_imagery = client.get_collections_by_name(qualified_name)
    if isinstance(prepared_imagery, dict | list):
        prepared_imagery_guid = prepared_imagery[0]['elementHeader']['guid']
        print(f"Found prepared_imagery guid of {prepared_imagery_guid}")
    else:
        prepared_imagery_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder for prepared imagery products: {prepared_imagery_guid}")
    #
    #   A digital product covering NDVI - derived from Sentinel 2
    #
    display_name = "NDVI - Sentinel 2 derived"
    description = "NDVI vegetation index calculated from Sentinel 2 imagery"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("DigitalProduct", display_name)

    props_body = {
        "class": "DigitalProductProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category,
        "productType": "Periodic Extended",
        "identifier": "NDVI-S",
        "productName": "NDVI - Sentinel 2",
        "serviceLife": "Until interest and budget wane",
        "maturity": "Nascent"
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": prepared_imagery_guid,
        "parentGUID": prepared_imagery_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }

    ndvi = client.get_collections_by_name(qualified_name)
    if isinstance(ndvi, dict | list):
        ndvi_guid = ndvi[0]['elementHeader']['guid']
        print(f"Found ndvi guid of {ndvi_guid}")
    else:
        ndvi_guid = client.create_digital_product(body=request_body)
        logger.success(f"Created NDVI product: {ndvi_guid}")
    #
    #   A folder to hold Raw Satellite Imagery Products
    #
    display_name = "Raw Satellite Imagery Products"
    description = "Raw satellite imagery imported from or referenced from satellite data providers"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {
        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": root_guid,
        "parentGUID": root_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    raw_imagery = client.get_collections_by_name(qualified_name)
    if isinstance(raw_imagery, dict | list):
        raw_imagery_guid = raw_imagery[0]['elementHeader']['guid']
        print(f"Found raw_imagery guid of {raw_imagery_guid}")
    else:
        raw_imagery_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder for raw imagery products: {raw_imagery_guid}")
    #
    #   A digital product providing Sentinel-2a imagery
    #
    display_name = "Sentinel-2a"
    description = "Level 2a (surface level) imagery"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("DigitalProduct", display_name)

    props_body = {
        "class": "DigitalProductProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category,
        "productType": "Periodic Extended",
        "identifier": "sentinel-2a",
        "productName": "Sentinel Level 2A",
        "serviceLife": "Until interest and budget wane",
        "maturity": "Nascent"
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": raw_imagery_guid,
        "parentGUID": raw_imagery_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    sentinel2a = client.get_collections_by_name(qualified_name)
    if isinstance(sentinel2a, dict | list):
        sentinel2a_guid = sentinel2a[0]['elementHeader']['guid']
        print(f"Found sentinel2a guid of {sentinel2a_guid}")
    else:
        sentinel2a_guid = client.create_digital_product(body=request_body)
        logger.success(f"Created Sentinel-2a product: {sentinel2a_guid}")

    # NDVI uses Sentinel 2A data so Add a dependency between ndvi dependent on sentinel2a
    client.link_digital_product_dependency(sentinel2a_guid, ndvi_guid)

    #
    # Now lets create some standard subscriptions (a form of agreement)
    #
    # Create a folder for standard agreements
    display_name = "Standard Subscription Agreements Folder"
    description = "A folder collection for digital product subscriptions"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {
        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": root_guid,
        "parentGUID": root_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    subscriptions_folder = client.get_collections_by_name(qualified_name)
    if isinstance(subscriptions_folder, dict | list):
        subscriptions_folder_guid = subscriptions_folder[0]['elementHeader']['guid']
        print(f"Found Standard Subscription Agreements Folder {subscriptions_folder_guid}")
    else:
        subscriptions_folder_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder for standard subscriptions: {subscriptions_folder_guid}")
    #
    # Add a Digital Subscription to this folder
    #
    anchor_guid = subscriptions_folder_guid
    parent_guid = subscriptions_folder_guid
    parent_relationship_type_name = "CollectionMembership"
    parent_at_end1 = True
    display_name = "GeoSpatial Data Products Subscription"
    description = "A generic subscription agreement for GeoSpatial Data Products"
    identifier = "GeoSpatial-0"
    category = "GeoSpatial"
    is_own_anchor = False

    qualified_name = client.__create_qualified_name__("DigitalSubscription", display_name)

    body = {
        "class": "NewElementRequestBody",
        "anchorGUID": anchor_guid,
        "isOwnAnchor": is_own_anchor,
        "parentGUID": parent_guid,
        # "initialClassification": {classification: {"class": {}}},
        "parentRelationshipTypeName": parent_relationship_type_name,
        "parentAtEnd1": parent_at_end1,
        "properties": {
            "class": "DigitalSubscriptionProperties",
            "displayName": display_name,
            "qualifiedName": qualified_name,
            "description": description,
            "identifier": identifier,
            "category": category,
            "supportLevel": "Best Effort"
            },
        }
    geo_subscriptions = client.get_collections_by_name(qualified_name)
    if isinstance(geo_subscriptions, dict | list):
        geo_subscriptions_guid = geo_subscriptions[0]['elementHeader']['guid']
        print(f"Found GeoSpatial Subscriptions guid of {geo_subscriptions_guid}")
    else:
        geo_subscriptions_guid = client.create_digital_subscription(body)
        print(f"Created Digital Subscription, GeoSpatial Data Products Subscription: {geo_subscriptions_guid}")
        logger.success(f"Created subscription : {geo_subscriptions_guid}")
    #
    #  Add agreement items to the agreement - the sentinel data
    #
    body = {
        "class": "NewRelationshipRequestBody",
        "properties": {
            "class": "AgreementItemProperties",
            "agreementItemId": "Sentinel-2a-Subscription",
            "agreementStart": "2025-08-01",
            "agreementEnd": "2025-12-31",
            "entitlements": {"Data Download": "Allowed", "Data Sharing": "Allowed"}
            }
        }
    client.link_agreement_item(geo_subscriptions_guid, sentinel2a_guid, body)
    msg = f"Linked agreement item sentinel2a to geo_subscriptions"
    logger.success(msg)
    print(msg)

    #
    #   Licensing
    #
    #   First a folder to hold license types - we will anchor it to the GeoSpatial root
    #
    display_name = "GeoSpatial Data Products License Types"
    description = "A folder collection containing license types governing GeoSpatial Data Products"
    category = "GeoSpatial"
    qualified_name = client.__create_qualified_name__("Folder", display_name)

    props_body = {
        "class": "CollectionProperties",
        "qualifiedName": qualified_name,
        "displayName": display_name,
        "description": description,
        "category": category
        }

    request_body = {
        "class": "NewElementRequestBody",
        "isOwnAnchor": False,
        "anchorGUID": root_guid,
        "parentGUID": root_guid,
        "parentRelationshipTypeName": "CollectionMembership",
        "parentAtEnd1": True,
        "properties": props_body,
        "initialClassifications": {"Folder": {"class": "ClassificationProperties"}}
        }
    license_type_folder = client.get_collections_by_name(qualified_name)
    if not isinstance(license_type_folder, dict | list):
        license_type_folder_guid = client.create_folder_collection(body=request_body)
        logger.success(f"Created folder for GeoSpatial Data Products License Types: {license_type_folder_guid}")
    else:
        license_type_folder_guid = license_type_folder[0]['elementHeader']['guid']
        print(f"Found license_type_folder guid of {license_type_folder_guid}")

    #
    #   Now lets create a few license types:
    #   - one for importing sentinel 2 data from ESA
    #   - one for offering the sentinel 2 data as a digital product
    #   - one for offering our derived product (NDVI) as a digital product
    #
    display_name = "ESA License Type"
    description = "A folder collection containing license types governing GeoSpatial Data Products"
    summary = "Free and Open Data - Requires Attribution"
    category = "GeoSpatial"
    details = "https://www.copernicus.eu/en/access-data/copyright-and-licences"
    qualified_name = client.__create_qualified_name__("LicenseType", display_name)


    props_body = {
                "class": "LicenseTypeProperties",
                "typeName": "LicenseType",
                "domainIdentifier": 0,
                "qualifiedName": qualified_name,
                "display_name": display_name,
                "summary": summary,
                "description": description,
                "scope": "World-Wide",
                "importance": "Foundational",
                # "details": details,
                # "entitlements": {"Data Download": "True", "Data Sharing": "True", "Data Access": "True",
                #                  "Data Usage": "True", "Data Analysis": "True"},
                # "restrictions": {},
                # "obligations": {"Attribution Required": "True"},
                "implications": ["Open Use"],
                "outcomes": ["Data Available"]
                # "results": [],
                }


    request_body = {
            "class": "NewElementRequestBody",
            "anchorGUID": license_type_folder_guid,
            "isOwnAnchor": False,
            "parentGUID": license_type_folder_guid,
            "parentRelationshipTypeName": "CollectionMembership",
            "parentAtEnd1": True,
            "properties": {
                "class": "LicenseTypeProperties",
                "typeName": "LicenseType",
                "domainIdentifier": 0,
                "qualifiedName": qualified_name,
                "display_name": display_name,
                "summary": summary,
                "description": description,
                "scope": "World-Wide",
                "importance": "Foundational",
                # "details": details,
                "entitlements": {"Data Download": "True", "Data Sharing": "True", "Data Access": "True",
                                 "Data Usage": "True", "Data Analysis": "True"},
                "restrictions": {},
                "obligations": {"Attribution Required": "True"},
                "implications": ["Open Use"],
                "outcomes": ["Data Available"],
                "results": []
                },
            "initialStatus": "ACTIVE"
            }

    esa_license_type = client.get_governance_definitions_by_name(qualified_name)
    if not isinstance(esa_license_type, dict | list):
        esa_license_type_guid = client.create_governance_definition(body=request_body)
        logger.success(f"Created license type for ESA License Type: {esa_license_type_guid}")
    else:
        esa_license_type_guid = esa_license_type[0]['elementHeader']['guid']
        print(f"Found license_type_guid for esa license type {esa_license_type_guid}")



except (PyegeriaInvalidParameterException, PyegeriaConnectionException, PyegeriaAPIException,
        PyegeriaUnknownException, PyegeriaException) as e:
    print_exception_table(e)

except ValidationError as e:
    print_validation_error(e)

finally:
    client.close_session()