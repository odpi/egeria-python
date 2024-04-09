"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Egeria Coco Pharmaceutical demonstration labs.

Configuring cocoMDS1 - Data Lake Operations metadata server

"""


import json

from globals import (adminUserId, cocoMDS1Name, dataLakePlatformURL, cocoCohort)
from pyegeria import CoreServerConfig, Platform
from pyegeria import (
    print_exception_response,
)

mdr_server = cocoMDS1Name
platform_url = dataLakePlatformURL
admin_user = adminUserId
mdr_server_user_id = "cocoMDS1npa"
mdr_server_password = "cocoMDS1passw0rd"
metadataCollectionId = f"{mdr_server}-e915f2fa-aa3g-4396-8bde-bcd65e642b1d"
metadataCollectionName = "Data Lake Catalog"

max_page_size = 600

print("Configuring " + mdr_server + "..." + " @ " + platform_url)

try:
    o_client = CoreServerConfig(mdr_server, platform_url, admin_user)

    o_client.set_basic_server_properties(metadataCollectionName,
                                         "Coco Pharmaceuticals",
                                         platform_url,
                                         mdr_server_user_id, mdr_server_password,
                                         max_page_size)

    # Can also inherit event bus config from application properties

    event_bus_config = {
        "producer": {
            "bootstrap.servers": "localhost:9092"
        },
        "consumer": {
            "bootstrap.servers": "localhost:9092"
        }
    }

    o_client.set_event_bus(event_bus_config)

    security_connection_body = {
        "class": "Connection",
        "connectorType": {
            "class": "ConnectorType",
            "connectorProviderClassName":
                "org.odpi.openmetadata.metadatasecurity.samples.CocoPharmaServerSecurityProvider"
        }
    }
    o_client.set_xtdb_local_kv_repository()
    # o_client.set_in_mem_local_repository()
    o_client.add_default_log_destinations()
    o_client.set_server_security_connection(security_connection_body)
    o_client.set_local_metadata_collection_name(metadataCollectionName)
    o_client.set_local_metadata_collection_id(metadataCollectionId)

    o_client.add_cohort_registration(cocoCohort)

    print(f"Configuring {mdr_server}  Access Services (OMAS)....")

    # o_client.configure_all_access_services()
    access_service_options = {
        "SupportedZones": ["quarantine", "clinical-trials", "research", "data-lake", "trash-can"]
    }

    o_client.configure_access_service("asset-catalog", access_service_options)
    o_client.configure_access_service("asset-consumer", access_service_options)

    access_service_options["DefaultZones"] = ["quarantine"]
    access_service_options["PublishZones"] = ["data-lake"]

    # print(f"Access Service Options: {access_service_options}")

    o_client.configure_access_service("asset-manager", access_service_options)
    o_client.configure_access_service("asset-owner", access_service_options)
    o_client.configure_access_service("community-profile",
                                      {"KarmaPointPlateau": "500"})
    o_client.configure_access_service("glossary-view", {})
    o_client.configure_access_service("asset-owner", access_service_options)
    o_client.configure_access_service("data-engine", access_service_options)
    o_client.configure_access_service("data-manager", access_service_options)
    o_client.configure_access_service("digital-architecture", access_service_options)
    o_client.configure_access_service("governance-engine", access_service_options)
    o_client.configure_access_service("governance-server", access_service_options)
    o_client.configure_access_service("asset-lineage", access_service_options)

    print(f"Activating {mdr_server}")
    p_client = Platform(mdr_server, platform_url, admin_user)
    p_client.activate_server_stored_config()

    config = o_client.get_stored_configuration()
    print(f"\n\n\tConfiguration of {mdr_server} is complete.")
    print(f"\nThe server stored configuration is:\n {json.dumps(config, indent=4)}")

except Exception as e:
    print_exception_response(e)
