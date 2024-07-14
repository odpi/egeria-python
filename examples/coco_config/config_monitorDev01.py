"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



Egeria Coco Pharmaceutical demonstration labs.

This script creates and configures the monitorDev01 integration daemon.

The monitorDev01 is another integration daemon server supporting the development team.
It is cataloguing assets in preparation for deployment into production.
It has no integration services active initially since they are set up in the labs and demos that use it.

"""

from globals import (devPlatformURL, adminUserId, max_paging_size)
from pyegeria import (
    print_exception_response,

)
from pyegeria.full_omag_server_config import FullServerConfig

daemon_server_name        = "monitorDev01"
daemon_server_platform    = devPlatformURL
daemon_server_user_id     = "erinoverview"
daemon_server_password    = "erinoverviewpassw0rd"

mdr_server                = "cocoMDSx"
platform_url              = devPlatformURL

print("Configuring " + daemon_server_name + "...")

try:
    f_client = FullServerConfig(daemon_server_name, daemon_server_platform, adminUserId)

    f_client.set_basic_server_properties("Integration daemon supporting the development team",
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

    print(f"Initial configuration for {daemon_server_name} is complete - more configuration and activation "
          f"will be performed in the labs")

except Exception as e:
    print_exception_response(e)
