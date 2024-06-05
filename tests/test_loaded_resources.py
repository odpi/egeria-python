"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the Automated Curation View Service module.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import json
import time

from rich import print
from rich.console import Console

from pyegeria import LoadedResources
from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

console = Console()


class TestLoadedResources:
    good_platform1_url = "https://localhost:9443"
    good_platform2_url = "https://oak.local:9443"
    bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    good_user_3 = "peterprofile"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_integ_1 = "fluffy_integration"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "laz_kv"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoVIew1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "view-server"
    good_view_server_2 = "fluffy_view"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_get_all_templates(self):
        try:
            l_client = LoadedResources(self.good_server_3, self.good_platform1_url,
                                         user_id=self.good_user_2, user_pwd="secret")

            start_time = time.perf_counter()
            response = l_client.get_all_templates()
            duration = time.perf_counter() - start_time
            print(f"\n\tDuration was {duration} seconds")
            response_t = type(response)
            print("Type of response is: " + response_t)
            if response is list:
                print(f"\n\nTemplates found are:\n {json.dumps(response, indent=4)}")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

        finally:
            l_client.close_session()

