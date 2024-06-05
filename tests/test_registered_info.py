"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""
import json
import pytest
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.registered_info import RegisteredInfo

disable_ssl_warnings = True


class TestRegisteredInfoServices:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://cray.local:9443"
    bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "simple-metadata-store"
    good_server_2 = "view-server"
    good_server_3 = "active-metadata-store"
    bad_server_1 = "coco"
    bad_server_2 = ""

    @pytest.mark.parametrize(
        "service_kind",
        [
            # (
            #     None
            # ),
            # (
            #     "all"
            # ),
            # (
            #     "access-services"
            # ),
            # (
            #     "common-services"
            # ),
            # (
            #     "engine-services"
            #
            # ),
            # (
            #     "governance-services"
            # ),
            (
                 "integration-services"
            ),
            # (
            #         "view-services"
            # ),
        ],
    )
    def test_list_registered_svcs(self, service_kind):

        try:
            r_client = RegisteredInfo(self.good_server_1,self.good_platform1_url, self.good_user_1)
            service_kind = 'all'
            response = r_client.list_registered_svcs(service_kind)

            assert (type(response) is list) or (type(response) is str), "No services found"
            if type(response) is list:
                print(f"\n\nView services configuration for {service_kind}: \n\n")
                # print(json.dumps(response, indent=4))
                rprint(response)
            else:
                print(f"\n\n{response}: \n\n")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_list_severity_definitions(self):
        try:
            r_client = RegisteredInfo(self.good_server_3,self.good_platform1_url,
                                       user_id=self.good_user_1)

            response = r_client.list_severity_definitions()
            console = Console()

            table = Table(
                title="Severity Codes",
                style = "black on grey66",
                header_style= "white on dark_blue"
            )
            table.add_column("Number")
            table.add_column("Name", width = 30)
            table.add_column("Description")

            for code in response:
                ordinal, name, description = (str(code['ordinal']), code['name'], code['description'])
                table.add_row(ordinal, name, description)
            console.print(table)
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_list_asset_types(self):
        user = self.good_user_2
        try:
            r_client = RegisteredInfo(self.good_server_2,self.good_platform1_url, user,
                                      "secret")
            token = r_client.create_egeria_bearer_token(user, "secret")
            response = r_client.list_asset_types()

            assert type(response) is list, "No services found"
            if type(response) is list:
                print(f"\n\nAsset types are: \n\n")
                print(json.dumps(response, indent=4))
            else:
                print(f"\n\n{response}: \n\n")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
