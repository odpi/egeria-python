"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the cocoMDS4 - Data Lake Users

"""


import json

from globals import (cocoMDS4Name, corePlatformURL, cocoCohort, max_paging_size)
from pyegeria import CoreServerConfig, Platform
from pyegeria import (
    print_exception_response,
)

disable_ssl_warnings = True

mdr_server = cocoMDS4Name
platform_url = corePlatformURL
admin_user = "garygeeke"
mdr_server_user_id = "cocoMDS4npa"
mdr_server_password = "cocoMDS4passw0rd"
metadataCollectionId = f"{mdr_server}-e915f2fa-aa3g-4396-8bde-bcd65e642b1d"
metadataCollectionName = "Data Lake Users"

print("Configuring " + mdr_server + "...")

try:
    o_client = CoreServerConfig(mdr_server, platform_url, admin_user)

    o_client.set_basic_server_properties(metadataCollectionName,
                                         "Coco Pharmaceuticals",
                                         platform_url,
                                         mdr_server_user_id, mdr_server_password,
                                         max_paging_size)

    # Inherit event bus config

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

    o_client.set_server_security_connection(security_connection_body)
    o_client.add_default_log_destinations()

    # Note: no metadata repository or collection configuration in this server.

    o_client.add_cohort_registration(cocoCohort)

    print(f"Configuring {mdr_server}  Access Services (OMAS)....")

    accessServiceOptions = {
        "SupportedZones": ["data-lake"]
    }

    o_client.configure_access_service("asset-catalog", accessServiceOptions)
    o_client.configure_access_service("asset-consumer", accessServiceOptions)
    o_client.configure_access_service("asset-owner", {})
    o_client.configure_access_service("community-profile",
                                      {"KarmaPointPlateau": "500"})
    o_client.configure_access_service("glossary-view", {})
    o_client.configure_access_service("data-science", accessServiceOptions)

    p_client = Platform(mdr_server, platform_url, admin_user)
    p_client.activate_server_stored_config()

    print(f"\n\n\tConfiguration of {mdr_server} is complete.")

    config = o_client.get_stored_configuration()
    print(f"The server stored configuration is \n{json.dumps(config, indent=4)}")

except Exception as e:
    print_exception_response(e)
