"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the cocoView1 server.

"""


import json

from globals import (cocoMDS2Name, corePlatformURL, dataLakePlatformURL, devPlatformURL)
from pyegeria import (
    print_exception_response,
)
from pyegeria.full_omag_server_config import FullServerConfig
from pyegeria.platform_services import Platform

disable_ssl_warnings = True

view_server = "cocoView1"
# platform_url = dataLakePlatformURL
platform_url = corePlatformURL
admin_user = "garygeeke"
view_server_user_id = "cocoView1npa"
view_server_password = "cocoView1passw0rd"
view_server_type = "View Server"
remote_platform_url = corePlatformURL
remote_server_name = cocoMDS2Name


print("Configuring " + view_server + "...")
try:
    f_client = FullServerConfig(view_server, platform_url, admin_user)

    f_client.set_server_user_id(view_server_user_id)
    f_client.set_server_user_password(view_server_password)
    f_client.set_organization_name("Coco Pharmaceuticals")

    f_client.set_server_description("Coco View Server")
    f_client.set_server_url_root(platform_url)

    # Can inherit event bus config

    event_bus_config = {
        "producer": {
            "bootstrap.servers": "localhost:9092"
        },
        "consumer": {
            "bootstrap.servers": "localhost:9092"
        }
    }

    f_client.set_event_bus(event_bus_config)

    security_connection_body = {
        "class": "Connection",
        "connectorType": {
            "class": "ConnectorType",
            "connectorProviderClassName":
                "org.odpi.openmetadata.metadatasecurity.samples.CocoPharmaServerSecurityProvider"
        }
    }
    f_client.set_server_security_connection(security_connection_body)

    f_client.add_default_log_destinations()

    view_server_config = {
        "class": "ViewServiceRequestBody",
        "omagserverPlatformRootURL": remote_platform_url,
        "omagserverName": remote_server_name,
        "resourceEndpoints": [
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Platform",
                "description": "Core Platform",
                "platformName": "Core",
                "platformRootURL": corePlatformURL
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Platform",
                "description": "DataLake Platform",
                "platformName": "DataLake",
                "platformRootURL": dataLakePlatformURL
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Platform",
                "description": "Development Platform",
                "platformName": "Development",
                "platformRootURL": devPlatformURL
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Server",
                "serverInstanceName": "cocoMDS1",
                "description": "Data Lake Operations",
                "platformName": "DataLake",
                "serverName": "cocoMDS1"
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Server",
                "serverInstanceName": "cocoMDS2",
                "description": "Governance",
                "platformName": "Core",
                "serverName": "cocoMDS2"
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Server",
                "serverInstanceName": "cocoMDS3",
                "description": "Research",
                "platformName": "Core",
                "serverName": "cocoMDS3"
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Server",
                "serverInstanceName": "cocoMDS5",
                "description": "Business Systems",
                "platformName": "Core",
                "serverName": "cocoMDS5"
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Server",
                "serverInstanceName": "cocoMDS6",
                "description": "Manufacturing",
                "platformName": "Core",
                "serverName": "cocoMDS6"
            },
            {
                "class": "ResourceEndpointConfig",
                "resourceCategory": "Server",
                "serverInstanceName": "cocoMDSx",
                "description": "Development",
                "platformName": "Development",
                "serverName": "cocoMDSx"
            },
        ]
    }

    f_client.config_all_view_services_w_body(view_server_config)

    p_client = Platform(view_server, platform_url, admin_user)
    p_client.activate_server_stored_config()

    config = f_client.get_stored_configuration()
    print(f"The server stored configuration is {json.dumps(config, indent=4)}")
    view_config = f_client.get_view_svcs_config()
    print(f"The view config is {json.dumps(view_config, indent=4)}")

except Exception as e:
    print_exception_response(e)
