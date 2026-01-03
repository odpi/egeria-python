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
from rich.markdown import Markdown
from rich.table import Table

from pyegeria._exceptions import (
    PyegeriaInvalidParameterException as InvalidParameterException,
    PyegeriaAPIException as PropertyServerException,
    PyegeriaUnauthorizedException as UserNotAuthorizedException,
    print_basic_exception as print_exception_response,
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
    good_server_2 = "qs-view-server"
    good_server_3 = "qs-metadata-store"
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
            ("integration-services"),
            # (
            #         "view-services"
            # ),
        ],
    )
    def test_list_registered_svcs(self, service_kind):
        try:
            r_client = RegisteredInfo(
                self.good_server_1, self.good_platform1_url, self.good_user_1
            )
            service_kind = "all"
            response = r_client.list_registered_svcs(service_kind, output_format="LIST", report_spec = "Registered-Services")

            assert (type(response) is list) or (
                type(response) is str
            ), "No services found"
            if type(response) is list:
                print(f"\n\nView services configuration for {service_kind}: \n\n")
                # print(json.dumps(response, indent=4))
                rprint(response)
            else:
                print(f"\n\n{response}: \n\n")

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_list_severity_definitions(self):
        try:
            r_client = RegisteredInfo(
                self.good_server_3, self.good_platform1_url, user_id=self.good_user_1
            )
            output_format = "LIST"
            response = r_client.list_severity_definitions(output_format=output_format, report_spec = "Severity-Definitions")
            console = Console(width = 130)

            if isinstance(response, list | dict):
                console.print(json.dumps(response, indent=4))
            elif output_format in ["REPORT","LIST","FORM","MD"]:
                console.print(Markdown(response))
            else:
                console.print(f"\n\n{response}: \n\n")
            assert True

        except (
            InvalidParameterException,
            PropertyServerException,
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_list_asset_types(self):
        user = self.good_user_2
        try:
            r_client = RegisteredInfo(
                self.good_server_2, self.good_platform1_url, user, "secret"
            )
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
            UserNotAuthorizedException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
