"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json

from pyegeria.core_omag_server_config import CoreServerConfig
from pyegeria.exceptions import (
    print_exception_response,
)
from pyegeria.platform_services import Platform

disable_ssl_warnings = True
mdr = "fluffy_kv"
plat = "https://127.0.0.1:9443"
metadataCollectionId = "e915f2fa-aaag-4396-8bde-bcd65e642b1d-kv"
metadataCollectionName = "collection-" + mdr

try:
    o_client = CoreServerConfig(mdr, plat, "garygeeke")
    o_client.set_basic_server_properties("fluffy description", "pdr",
                                         "https://127.0.0.1:9443",
                                         "cocoMDS1npa", "generalnpapwd", 0)


    o_client.set_xtdb_local_kv_repository()


    o_client.set_local_metadata_collection_id(metadataCollectionId)
    o_client.set_local_metadata_collection_name(metadataCollectionName)


    o_client.configure_access_service_no_topics("asset-manager")

    con_archive = "./content-packs/OpenConnectorsArchive.omarchive"
    o_client.add_startup_open_metadata_archive_file(con_archive)

    # glossary_archive = "./content-packs/BigGlossaryA.omarchive"
    # o_client.add_startup_open_metadata_archive_file(glossary_archive)
    p_client = Platform(mdr, plat, "garygeeke")
    p_client.activate_server_stored_config(timeout=90)

    config = o_client.get_stored_configuration()
    print(f"The server stored configuration is {json.dumps(config, indent=4)}")


except Exception as e:
    print_exception_response(e)
