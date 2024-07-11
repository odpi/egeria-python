"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This sample creates a collection structure for a sustainability reporting project. It is
simplistic but shows how we can set up a collection hierarchy that can hold different kinds of
assets.

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

    # Create a root collection for the sustainability project
    parent_guid = None
    parent_relationship_type_name = None
    display_name = "Root Sustainability Collection"
    description = "The root collection for our sustainability reporting project."
    collection_type = "Sustainability Collection"

    root = c_client.create_root_collection(None, parent_guid,
                                           parent_relationship_type_name,
                                           False, display_name, description,
                                           collection_type, True)
    print(f"\n\n created a root with guid {root}")
    # create a folder for Scope 1 Emissions
    anchor_guid = root
    parent_guid = root
    parent_relationship_type_name = "CollectionMembership"
    display_name = "Scope 1 Emissions"
    description = "A folder for information about scope 1 emissions."
    collection_type = "Sustainability Collection"

    scope1_folder = c_client.create_folder_collection(anchor_guid, parent_guid,
                                                      parent_relationship_type_name,
                                                      True, display_name, description,
                                                      collection_type, False, "DATE_CREATED",
                                                      None
                                                      )
    print(f"\n\n created scope1_folder with guid {scope1_folder}")

    # create a folder for Scope 2 Emissions.
    anchor_guid = root
    parent_guid = root
    parent_relationship_type_name = "CollectionMembership"
    display_name = "Scope 2 Emissions"
    description = "A folder for information about scope 2 emissions."
    collection_type = "Sustainability Collection"

    scope2_folder = c_client.create_folder_collection(anchor_guid, parent_guid,
                                                      parent_relationship_type_name,
                                                      True, display_name, description,
                                                      collection_type, False, "DATE_CREATED",
                                                      None
                                                      )
    print(f"\n\n created scope2_folder with guid {scope2_folder}")

    # create a folder for Scope 3 Emissions.
    anchor_guid = root
    parent_guid = root
    parent_relationship_type_name = "CollectionMembership"
    display_name = "Scope 3 Emissions"
    description = "A folder for information about scope 3 emissions."
    collection_type = "Sustainability Collection"

    scope3_folder = c_client.create_folder_collection(anchor_guid, parent_guid,
                                                      parent_relationship_type_name,
                                                      True, display_name, description,
                                                      collection_type, False, "DATE_CREATED",
                                                      None
                                                      )
    print(f"\n\n created scope3_folder with guid {scope3_folder}")

    # create a folder for Business Travel Emissions.
    anchor_guid = root
    parent_guid = scope3_folder
    parent_relationship_type_name = "CollectionMembership"
    display_name = "Business Travel Emissions"
    description = "A folder for information about scope 3 business travel emissions."
    collection_type = "Sustainability Collection"

    travel_folder = c_client.create_folder_collection(anchor_guid, parent_guid,
                                                      parent_relationship_type_name,
                                                      True, display_name, description,
                                                      collection_type, False, "DATE_CREATED",
                                                      None
                                                      )
    print(f"\n\n created travel_folder with guid {travel_folder}")


except (
        InvalidParameterException,
        PropertyServerException,
        UserNotAuthorizedException
) as e:
    console.print_exception(show_locals=True)

finally:
    c_client.close_session()
