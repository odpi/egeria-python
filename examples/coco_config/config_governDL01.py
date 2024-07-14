"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the governDL01 engine host.


"""


import json

from globals import (dataLakePlatformURL, max_paging_size)
from pyegeria import CoreServerConfig
from pyegeria import (
    print_exception_response,
)
from pyegeria.platform_services import Platform

engine_server = "governDL01"
engine_server_platform = dataLakePlatformURL
admin_user = "garygeeke"

engine_server_user_id = "governDL01npa"
engine_server_password = "governDL01passw0rd"
mdr_server = "cocoMDS1"
mdr_engine_server_platform = dataLakePlatformURL

print("Configuring " + engine_server + "...")

try:
    o_client = CoreServerConfig(engine_server, engine_server_platform, admin_user)

    o_client.set_basic_server_properties("An Engine Host to run governance actions for Coco Pharmaceuticals",
                                         "Coco Pharmaceuticals",
                                         engine_server_platform,
                                         engine_server_user_id, engine_server_password,
                                         max_paging_size)

    security_connection_body = {
        "class": "Connection",
        "connectorType": {
            "class": "ConnectorType",
            "connectorProviderClassName":
                "org.odpi.openmetadata.metadatasecurity.samples.CocoPharmaServerSecurityProvider"
        }
    }
    o_client.set_server_security_connection(security_connection_body)

    o_client.set_engine_definitions_client_config(mdr_server, mdr_engine_server_platform)

    engine_list_body = [
        {
            "class": "EngineConfig",
            "engineQualifiedName": "AssetDiscovery",
            "engineUserId": "findItDL01npa"
        },
        {
            "class": "EngineConfig",
            "engineQualifiedName": "AssetQuality",
            "engineUserId": "findItDL01npa"
        }
    ]

    o_client.set_engine_list(engine_list_body)

    config = o_client.get_stored_configuration()
    print(f"The server stored configuration is {json.dumps(config, indent=4)}")

    p_client = Platform(engine_server, engine_server_platform, admin_user)
    p_client.activate_server_stored_config()

    config = p_client.get_active_configuration()
    print(f"The server stored configuration is {json.dumps(config, indent=4)}")

except Exception as e:
    print_exception_response(e)
