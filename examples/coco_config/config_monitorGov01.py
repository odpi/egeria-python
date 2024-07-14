"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the monitorGov01 server.

The **monitorGov01** is another integration daemon server supporting the governance team.
It is managing the capture of lineage for the governance actions and external processing in the data lake.

"""

import json

from globals import (dataLakePlatformURL, fileSystemRoot)
from pyegeria import FullServerConfig
from pyegeria import Platform
from pyegeria import (
    print_exception_response,
)

daemon_server_name = "monitorGov01"
daemon_server_platform = dataLakePlatformURL
daemon_server_user_id = "exchangeDL01npa"
daemon_server_password = "exchangeDL01passw0rd"

mdr_server = "cocoMDS1"
mdr_platform_url = dataLakePlatformURL
admin_user = "garygeeke"

KafkaReceiverConnectorName = "KafkaOpenLineageEventReceiver"
KafkaReceiverConnectorUserId = "onboardDL01npa"
KafkaReceiverConnectorSourceName = "Apache Kafka"
KafkaReceiverConnectorConnection = {
    "class": "VirtualConnection",
    "connectorType":
        {
            "class": "ConnectorType",
            "connectorProviderClassName": "org.odpi.openmetadata.adapters.connectors.integration.openlineage.OpenLineageEventReceiverIntegrationProvider"
        },
    "embeddedConnections":
        [
            {
                "class": "EmbeddedConnection",
                "embeddedConnection":
                    {
                        "class": "Connection",
                        "connectorType":
                            {
                                "class": "ConnectorType",
                                "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.kafka.KafkaOpenMetadataTopicProvider",
                            },
                        "endpoint":
                            {
                                "class": "Endpoint",
                                "address": "openlineage.topic"
                            },
                        "configurationProperties":
                            {
                                "producer":
                                    {
                                        "bootstrap.servers": "localhost:9092"
                                    },
                                "local.server.id": "f234e808-2d0c-4d88-83df-275eee20c1b7",
                                "consumer":
                                    {
                                        "bootstrap.servers": "localhost:9092"
                                    }
                            }
                    }
            }
        ]
}

GovernanceActionConnectorName = "GovernanceActionOpenLineageCreator"
GovernanceActionConnectorUserId = "onboardDL01npa"
GovernanceActionConnectorSourceName = "Egeria"
GovernanceActionConnectorConnection = {
    "class": "Connection",
    "connectorType":
        {
            "class": "ConnectorType",
            "connectorProviderClassName": "org.odpi.openmetadata.adapters.connectors.integration.openlineage.GovernanceActionOpenLineageIntegrationProvider"
        },
}

APILoggerConnectorName = "APIBasedOpenLineageLogStore"
APILoggerConnectorUserId = "onboardDL01npa"
APILoggerConnectorSourceName = "Egeria"
APILoggerConnectorConnection = {
    "class": "Connection",
    "connectorType":
        {
            "class": "ConnectorType",
            "connectorProviderClassName": "org.odpi.openmetadata.adapters.connectors.integration.openlineage.APIBasedOpenLineageLogStoreProvider"
        },
    "endpoint":
        {
            "class": "Endpoint",
            "address": "http://localhost:5000/api/v1/lineage"
        }
}

FileLoggerConnectorName = "FileBasedOpenLineageLogStore"
FileLoggerConnectorUserId = "onboardDL01npa"
FileLoggerConnectorSourceName = "Egeria"
FileLoggerConnectorConnection = {
    "class": "Connection",
    "connectorType":
        {
            "class": "ConnectorType",
            "connectorProviderClassName": "org.odpi.openmetadata.adapters.connectors.integration.openlineage.FileBasedOpenLineageLogStoreProvider"
        },
    "endpoint":
        {
            "class": "Endpoint",
            "address": fileSystemRoot + '/openlineage.log'
        }
}

CataloguerConnectorName = "OpenLineageCataloguer"
CataloguerConnectorUserId = "onboardDL01npa"
CataloguerConnectorSourceName = "OpenLineageSources"
CataloguerConnectorConnection = {
    "class": "Connection",
    "connectorType":
        {
            "class": "ConnectorType",
            "connectorProviderClassName": "org.odpi.openmetadata.adapters.connectors.integration.openlineage.OpenLineageCataloguerIntegrationProvider"
        }
}

print("Configuring " + daemon_server_name + "...")

print("\nConfiguring " + daemon_server_name + " integration connectors ...")

connectorConfigs = [
    {
        "class": "IntegrationConnectorConfig",
        "connectorName": KafkaReceiverConnectorName,
        "connectorUserId": KafkaReceiverConnectorUserId,
        "connection": KafkaReceiverConnectorConnection,
        "metadataSourceQualifiedName": KafkaReceiverConnectorSourceName,
        "refreshTimeInterval": 10,
        "usesBlockingCalls": "false"
    },
    {
        "class": "IntegrationConnectorConfig",
        "connectorName": GovernanceActionConnectorName,
        "connectorUserId": GovernanceActionConnectorUserId,
        "connection": GovernanceActionConnectorConnection,
        "metadataSourceQualifiedName": GovernanceActionConnectorSourceName,
        "refreshTimeInterval": 10,
        "usesBlockingCalls": "false"
    },
    {
        "class": "IntegrationConnectorConfig",
        "connectorName": APILoggerConnectorName,
        "connectorUserId": APILoggerConnectorUserId,
        "connection": APILoggerConnectorConnection,
        "metadataSourceQualifiedName": APILoggerConnectorSourceName,
        "refreshTimeInterval": 10,
        "usesBlockingCalls": "false"
    },
    {
        "class": "IntegrationConnectorConfig",
        "connectorName": FileLoggerConnectorName,
        "connectorUserId": FileLoggerConnectorUserId,
        "connection": FileLoggerConnectorConnection,
        "metadataSourceQualifiedName": FileLoggerConnectorSourceName,
        "refreshTimeInterval": 10,
        "usesBlockingCalls": "false"
    },
    {
        "class": "IntegrationConnectorConfig",
        "connectorName": CataloguerConnectorName,
        "connectorUserId": CataloguerConnectorUserId,
        "connection": CataloguerConnectorConnection,
        "metadataSourceQualifiedName": CataloguerConnectorSourceName,
        "refreshTimeInterval": 10,
        "usesBlockingCalls": "false"
    }]

print("\nDone.")

try:
    f_client = FullServerConfig(daemon_server_name, daemon_server_platform, admin_user)

    f_client.set_basic_server_properties("An Engine Host to run governance actions for Coco Pharmaceuticals",
                                         "Coco Pharmaceuticals",
                                         daemon_server_platform,
                                         daemon_server_user_id, daemon_server_password,
                                         600)

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

    f_client.config_integration_service(mdr_server, mdr_platform_url,
                                        "lineage-integrator", {}, connectorConfigs)

    p_client = Platform(daemon_server_name, daemon_server_platform, admin_user)
    p_client.activate_server_stored_config()

    config = p_client.get_active_configuration()
    print(f"The server stored configuration is {json.dumps(config, indent=4)}")

except Exception as e:
    print_exception_response(e)
