"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the cocoMDS6 - Manufacturing

"""


import json

from globals import (
    cocoMDS6Name,
    corePlatformURL,
    cocoCohort,
    iotCohort,
    max_paging_size,
)
from pyegeria import CoreServerConfig, Platform
from pyegeria import (
    print_exception_response,
)

disable_ssl_warnings = True

mdr_server = cocoMDS6Name
platform_url = corePlatformURL
admin_user = "garygeeke"
mdr_server_user_id = "cocoMDS6npa"
mdr_server_password = "cocoMDS6passw0rd"
metadataCollectionId = f"{mdr_server}-e915f2fa-aa3g-4396-8bde-bcd65e642b1d"
metadataCollectionName = "Manufacturing Catalog"

print("Configuring " + mdr_server + "...")

try:
    o_client = CoreServerConfig(mdr_server, platform_url, admin_user)

    o_client.set_basic_server_properties(
        "Manufacturing",
        "Coco Pharmaceuticals",
        platform_url,
        mdr_server_user_id,
        mdr_server_password,
        max_paging_size,
    )

    # Can inherit event bus config

    # event_bus_config = {
    #     "producer": {
    #         "bootstrap.servers": "localhost:9092"
    #     },
    #     "consumer": {
    #         "bootstrap.servers": "localhost:9092"
    #     }
    # }
    #
    # o_client.set_event_bus(event_bus_config)

    security_connection_body = {
        "class": "Connection",
        "connectorType": {
            "class": "ConnectorType",
            "connectorProviderClassName": "org.odpi.openmetadata.metadatasecurity.samples.CocoPharmaServerSecurityProvider",
        },
    }

    o_client.set_server_security_connection(security_connection_body)
    o_client.add_default_log_destinations()

    # o_client.set_in_mem_local_repository()
    o_client.set_xtdb_local_kv_repository()

    o_client.set_local_metadata_collection_id(metadataCollectionId)
    o_client.set_local_metadata_collection_name(metadataCollectionName)

    o_client.add_cohort_registration(cocoCohort)
    o_client.add_cohort_registration(iotCohort)

    print(f"Configuring {mdr_server}  Access Services (OMAS)....")

    access_service_options = {
        "SupportedZones": ["manufacturing"],
        "DefaultZones": ["manufacturing"],
    }

    # o_client.configure_access_service("asset-catalog", access_service_options)
    o_client.configure_access_service("asset-consumer", access_service_options)
    o_client.configure_access_service("asset-owner", access_service_options)
    o_client.configure_access_service("community-profile", {"KarmaPointPlateau": "500"})
    # o_client.configure_access_service("glossary-view", {})
    o_client.configure_access_service("data-science", access_service_options)
    # o_client.configure_access_service("subject-area", {})
    o_client.configure_access_service("asset-manager", access_service_options)
    o_client.configure_access_service("governance-engine", access_service_options)
    o_client.configure_access_service("governance-server", access_service_options)
    o_client.configure_access_service("asset-owner", access_service_options)
    # o_client.configure_access_service("data-engine", access_service_options)
    o_client.configure_access_service("data-manager", access_service_options)
    o_client.configure_access_service("it-infrastructure", access_service_options)
    o_client.configure_access_service("project-management", access_service_options)

    p_client = Platform(mdr_server, platform_url, admin_user)
    p_client.activate_server_stored_config()

    print(f"\n\n\tConfiguration of {mdr_server} is complete.")

    config = o_client.get_stored_configuration()
    print(f"The server stored configuration is \n{json.dumps(config, indent=4)}")

except Exception as e:
    print_exception_response(e)
