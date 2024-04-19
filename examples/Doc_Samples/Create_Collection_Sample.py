"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This sample creates the collection structure show in https://egeria-project.org/types/0/0021-Collections

"""

import time

from rich import print
from rich.console import Console

from pyegeria import CollectionManager, InvalidParameterException, PropertyServerException, UserNotAuthorizedException

view_server = 'view-server'
platform_url = 'https://localhost:9443'
user = 'erinoverview'
console = Console()

try:
    c_client = CollectionManager(view_server, platform_url,
                                 user_id=user)

    token = c_client.create_egeria_bearer_token(user, "secret")
    start_time = time.perf_counter()

    # Create a Data Products Root collection
    anchor_guid = None
    parent_guid = None
    parent_relationship_type_name = None
    parent_at_end1 = False
    display_name = "Digital Products Root"
    description = "This is the root catalog for digital products"
    collection_type = "Digital Products Root"
    is_own_anchor = True

    response = c_client.create_root_collection(anchor_guid, parent_guid,
                                               parent_relationship_type_name, parent_at_end1,
                                               display_name, description, collection_type,
                                               is_own_anchor)
    # Create first folder for Agriculture Insights
    parent_guid = "97bbfe07-6696-4550-bf8b-6b577d25bef0"
    parent_relationship_type_name = "CollectionMembership"
    display_name = "Agriculture Insights Collection"
    description = "A folder for agricultural insights data product collections"
    collection_type = "Digital Product Marketplace"

    folder1 = c_client.create_folder_collection(None, parent_guid,
                                                parent_relationship_type_name,
                                                True, display_name, description,
                                                collection_type, True, "DATE_CREATED",
                                                None
                                                )
    print(f"\n\n created a folder with guid {folder1}")
    # create second folder for Earth Observations
    display_name = "Earth Observation Data Collection"
    description = "A folder for Earth Observation data product collections"

    folder2 = c_client.create_folder_collection(None, parent_guid,
                                                parent_relationship_type_name,
                                                True, display_name, description,
                                                collection_type, True, "DATE_CREATED",
                                                None
                                                )
    print(f"\n\n created a folder with guid {folder2}")

    # create a digital product, child of folder 1, for Land Use products
    parent_guid = folder1
    parent_relationship_type_name = "CollectionMembership"
    display_name = "Land Use Classification"
    description = "Land use classification assets"
    collection_type = "Digital Product"
    classification_name = "Digital Product"
    body_3 = {
            "class": "NewDigitalProductRequestBody",
            "isOwnAnchor": True,
            "parentGUID": parent_guid,
            "parentRelationshipTypeName": parent_relationship_type_name,
            "parentAtEnd1": True,
            "collectionProperties": {
                "class": "CollectionProperties",
                "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                "name": display_name,
                "description": description,
                "collectionType": collection_type,
                "collectionOrdering": "DATE_CREATED",
            },
            "digitalProductProperties": {
                "class": "DigitalProductProperties",
                "productStatus": "ACTIVE",
                "productName": "Land Use Classifications",
                "productType": "Geospatial Data Assets",
                "description": "Land use classification assets",
                "introductionDate": "2023-12-01",
                "maturity": "Nacent",
                "serviceLife": "3 years",
                "currentVersion": "V.5",
                "nextVersionDate": "2024-12-01",
                "withdrawDate": "2030-01-01",
                "additionalProperties": {
                    "thought_id": "a guid",
                    "license": "cc-by-sa",
                }
            }
    }
    folder3 = c_client.create_digital_product(body_3)
    print(f"\n\n created a collection with guid {folder3}")

    # create a fourth collection, a digital product, child of folder 2, for Landsat 8
    parent_guid = folder2
    display_name = "Landsat 8"
    description = "Landsat 8 data products"

    body_4 = {
            "class": "NewDigitalProductRequestBody",
            "isOwnAnchor": True,
            "parentGUID": parent_guid,
            "parentRelationshipTypeName": parent_relationship_type_name,
            "parentAtEnd1": True,
            "collectionProperties": {
                "class": "CollectionProperties",
                "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                "name": display_name,
                "description": description,
                "collectionType": collection_type,
                "collectionOrdering": "DATE_CREATED",
            },
            "digitalProductProperties": {
                "class": "DigitalProductProperties",
                "productStatus": "ACTIVE",
                "productName": "Landsat 8 Imagery",
                "productType": "Geospatial Data Assets",
                "description": description,
                "introductionDate": "2024-01-01",
                "maturity": "Mature",
                "serviceLife": "3 years",
                "currentVersion": "V1.5",
                "nextVersion": "2024-06-01",
                "withdrawDate": "2030-01-01",
                "additionalProperties": {
                    "thought_id": "a guid",
                    "license": "cc-by-sa",
                }
            }
    }
    folder4 = c_client.create_digital_product(body_4)
    print(f"\n\n created a collection with guid {folder4}")

    # Now create a 5th collection for sentinel 2 data
    parent_guid = folder2
    display_name = "Sentinel 2"
    description = "Sentinel 2 products"
    parent_relationship_type_name = "CollectionMembership"
    collection_type = "Digital Product Marketplace"

    folder5 = c_client.create_folder_collection(None, parent_guid,
                                                parent_relationship_type_name,
                                                True, display_name, description,
                                                collection_type, True, "DATE_CREATED",
                                                None
                                                )
    # Create a DigitalProduct for Level-1B
    parent_guid = folder5
    display_name = "Sentinel 2 - Level 1B"
    description = "Level 1B of Sentinel 2"

    body_6 = {
        "class": "NewDigitalProductRequestBody",
        "anchor_guid": parent_guid,
        "isOwnAnchor": False,
        "parentGUID": parent_guid,
        "parentRelationshipTypeName": parent_relationship_type_name,
        "parentAtEnd1": True,
        "collectionProperties": {
            "class": "CollectionProperties",
            "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
            "name": display_name,
            "description": description,
            "collectionType": collection_type,
            "collectionOrdering": "DATE_CREATED",
        },
        "digitalProductProperties": {
            "class": "DigitalProductProperties",
            "productStatus": "ACTIVE",
            "productName": "Sentinel 2 - Level 1B",
            "productType": "Geospatial Data Assets",
            "description": description,
            "introductionDate": "2024-01-01",
            "maturity": "Mature",
            "serviceLife": "3 years",
            "currentVersion": "V1.5",
            "nextVersion": "2024-06-01",
            "withdrawDate": "2030-01-01",
            "additionalProperties": {
                "thought_id": "a guid",
                "license": "cc-by-sa",
            }
        }
    }
    folder6 = c_client.create_digital_product(body_6)
    print(f"\n\n created a collection with guid {folder6}")

    # now lets create a digital product for - Level - 1c
    parent_guid = folder5
    display_name = "Sentinel 2 - Level 1C"
    description = "Level 1C of Sentinel 2"
    body_7 = {
        "class": "NewDigitalProductRequestBody",
        "anchor_guid": parent_guid,
        "isOwnAnchor": False,
        "parentGUID": parent_guid,
        "parentRelationshipTypeName": parent_relationship_type_name,
        "parentAtEnd1": True,
        "collectionProperties": {
            "class": "CollectionProperties",
            "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
            "name": display_name,
            "description": description,
            "collectionType": collection_type,
            "collectionOrdering": "DATE_CREATED",
        },
        "digitalProductProperties": {
            "class": "DigitalProductProperties",
            "productStatus": "ACTIVE",
            "productName": "Sentinel 2 - Level 1B",
            "productType": "Geospatial Data Assets",
            "description": description,
            "introductionDate": "2024-01-01",
            "maturity": "Mature",
            "serviceLife": "3 years",
            "currentVersion": "V1.5",
            "nextVersion": "2024-06-01",
            "withdrawDate": "2030-01-01",
            "additionalProperties": {
                "thought_id": "a guid",
                "license": "cc-by-sa",
            }
        }
    }
    folder7 = c_client.create_digital_product(body_7)
    print(f"\n\n created a collection with guid {folder7}")

    # now let's create a digital product for - Level - 2A
    parent_guid = folder5
    display_name = "Sentinel 2 - Level 2A"
    description = "Level 2A of Sentinel 2"
    body_8 = {
        "class": "NewDigitalProductRequestBody",
        "anchor_guid": parent_guid,
        "isOwnAnchor": False,
        "parentGUID": parent_guid,
        "parentRelationshipTypeName": parent_relationship_type_name,
        "parentAtEnd1": True,
        "collectionProperties": {
            "class": "CollectionProperties",
            "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
            "name": display_name,
            "description": description,
            "collectionType": collection_type,
            "collectionOrdering": "DATE_CREATED",
        },
        "digitalProductProperties": {
            "class": "DigitalProductProperties",
            "productStatus": "ACTIVE",
            "productName": "Sentinel 2 - Level 1B",
            "productType": "Geospatial Data Assets",
            "description": description,
            "introductionDate": "2024-01-01",
            "maturity": "Mature",
            "serviceLife": "3 years",
            "currentVersion": "V1.5",
            "nextVersion": "2024-06-01",
            "withdrawDate": "2030-01-01",
            "additionalProperties": {
                "thought_id": "a guid",
                "license": "cc-by-sa",
            }
        }
    }
    folder8 = c_client.create_digital_product(body_8)
    print(f"\n\n created a collection with guid {folder8}")

except (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException
) as e:
    console.print_exception(show_locals=True)

finally:
    c_client.close_session()
