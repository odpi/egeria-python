"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the exchangeDL01 integration daemon.

"""


import json

from globals import (corePlatformURL, max_paging_size,
                     fileSystemRoot, adminUserId)
from pyegeria import (
    print_exception_response,

)
from pyegeria.full_omag_server_config import FullServerConfig
from pyegeria.platform_services import Platform

daemon_server_name        = "exchangeDL01"
#
daemon_server_platform    = corePlatformURL
daemon_server_user_id     = "exchangeDL01npa"
daemon_server_password    = "exchangeDL01passw0rd"

mdr_server                = "cocoMDS1"

platform_url = corePlatformURL
folder_connector_name       = "DropFootClinicalTrialResultsFolderMonitor"
folder_connector_user_id     = "monitorDL01npa"
folder_connector_source_name = "DropFootClinicalTrialResults"
folder_connector_folder     = fileSystemRoot + '/data-lake/research/clinical-trials/drop-foot/weekly-measurements'
folder_connector_connection =  { 
      "class": "Connection",
      "connectorType":
      {
           "class": "ConnectorType",
           "connectorProviderClassName":
               "org.odpi.openmetadata.adapters.connectors.integration.basicfiles.DataFolderMonitorIntegrationProvider"
      },
      "endpoint":
      {
           "class": "Endpoint",
           "address": folder_connector_folder
      }
  }

integration_group_name = "Onboarding"

print("Configuring " + daemon_server_name + "...")

try:
    f_client = FullServerConfig(daemon_server_name, daemon_server_platform, adminUserId)

    f_client.set_basic_server_properties("Supports exchange of metadata with third party technologies",
                                         "Coco Pharmaceuticals",
                                         daemon_server_platform,
                                         daemon_server_user_id, daemon_server_password,
                                         max_paging_size)

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

    print("\nConfiguring " + daemon_server_name + " integration connectors ...")

    connector_configs = [
        {
            "class": "IntegrationConnectorConfig",
            "connectorName": folder_connector_name,
            "connectorUserId": folder_connector_user_id,
            "connection": folder_connector_connection,
            "metadataSourceQualifiedName": folder_connector_source_name,
            "refreshTimeInterval": 10,
            "usesBlockingCalls": "false"
        }
    ]

    f_client.config_integration_service(mdr_server, platform_url, "files-integrator",
                                        {}, connector_configs)

    f_client.config_integration_group(daemon_server_name, daemon_server_platform,
                                      integration_group_name)

    p_client = Platform(daemon_server_name, daemon_server_platform, adminUserId)
    p_client.activate_server_stored_config()

    config = p_client.get_active_configuration()
    print(f"The server stored configuration is {json.dumps(config, indent=4)}")

except Exception as e:
    print_exception_response(e)
