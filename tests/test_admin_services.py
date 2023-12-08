"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the platform_services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests. To run these tests you need to use the
Egeria lab environment and run the automate-curation lab to just before the initiateGovernanceAction

"""

import pytest
import requests
from datetime import datetime
import json

from contextlib import nullcontext as does_not_raise

disable_ssl_warnings = True

from pyegeria.util_exp import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
    print_rest_response,
)

from pyegeria.admin_services import OMAGServerConfigClient
class TestAdminServices:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://127.0.0.1:9444"
    bad_platform1_url = "https://localhost:9443"

    # good_platform1_url = "https://127.0.0.1:30080"
    # good_platform2_url = "https://127.0.0.1:30081"
    # bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "cocoMDS1"
    good_server_2 = "cocoMDS2"
    good_server_3 = "meow"
    bad_server_1 = "coco"
    bad_server_2 = ""

    def test_get_audit_log_destinations(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            destinations = o_client.get_audit_log_destinations()

            print("\n\n" + json.dumps(destinations, indent=4))
            assert destinations is not None, "Failed to get audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_audit_log_destinations(self):
        audit_log_dest = [
            {
                "class": "Connection",
                "qualifiedName": "Console- default",
                "displayName": "Console",
                "connectorType": {
                    "class": "ConnectorType",
                    "type": {
                        "typeId": "954421eb-33a6-462d-a8ca-b5709a1bd0d4",
                        "typeName": "ConnectorType",
                        "typeVersion": 1,
                        "typeDescription": "A set of properties describing a type of connector."
                    },
                    "guid": "4afac741-3dcc-4c60-a4ca-a6dede994e3f",
                    "qualifiedName": "Egeria:AuditLogDestinationConnector:Console",
                    "displayName": "Console Audit Log Destination Connector",
                    "description": "Connector supports logging of audit log messages to stdout.",
                    "connectorProviderClassName": "org.odpi.openmetadata.adapters.repositoryservices.auditlogstore.console.ConsoleAuditLogStoreProvider",
                    "connectorFrameworkName": "Open Connector Framework (OCF)",
                    "connectorInterfaceLanguage": "Java",
                    "connectorInterfaces": [
                        "org.odpi.openmetadata.repositoryservices.connectors.stores.auditlogstore.OMRSAuditLogStore"
                    ],
                    "recognizedConfigurationProperties": [
                        "supportedSeverities"
                    ]
                },
                "configurationProperties": {
                    "supportedSeverities": [
                        "<Unknown>",
                        "Action",
                        "Error",
                        "Exception",
                        "Security",
                        "Startup",
                        "Shutdown",
                    ]
                }
            },
            {
                "class": "Connection",
                "connectorType": {
                    "class": "ConnectorType",
                    "connectorProviderClassName": "org.odpi.openmetadata.adapters.repositoryservices.auditlogstore.file.FileBasedAuditLogStoreProvider"
                },
                "endpoint": {
                    "class": "Endpoint",
                    "address": "data/servers/auditlog"
                },
                "configurationProperties": {
                    "supportedSeverities": [
                        "Error",
                        "Exception",
                        "Security"
                    ]
                }
            }
        ]

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.set_audit_log_destinations(audit_log_dest)

            print("\n\n" + json.dumps(response, indent=4))
            assert response is not None, "Failed to set audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_audit_log_destinations(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.clear_audit_log_destinations()

            print("\n\n\t\tResponse is: " + json.dumps(response, indent=4))
            assert response is None, "Failed to clear audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_console_log_destinations(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.add_console_log_destinations([])

            print("\n\n\t\tResponse is: " + str(response))
            assert response, "Failed to clear audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_default_log_destinations(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.add_default_log_destinations()

            print("\n\n\t\tResponse is: " + str(response))
            assert response, "Failed to clear audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_topic_log_destinations(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.add_topic_log_destinations([])

            print("\n\n\t\tResponse is: " + str(response))
            assert response, "Failed to add topic log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_file_log_destinations(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.add_file_log_destinations("./logs", [])

            print("\n\n\t\tResponse is: " + str(response))
            assert response, "Failed to add file log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_SLF4J_log_destination(self):

        try:
            o_client = OMAGServerConfigClient(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.add_SLF4J_log_destination()

            print("\n\n\t\tResponse is: " + str(response))
            assert response, "Failed to add SLF4J log destination"

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    # def test_clear_a_log_destination(self):
    #
    #     try:
    #         o_client = OMAGServerConfigClient(
    #             self.good_server_2, self.good_platform1_url,
    #             self.good_user_1)
    #         qname = "Files in ./logs"
    #         response = o_client.clear_a_log_destination(qname)
    #
    #         print("\n\n\t\tResponse is: " + str(response))
    #         assert response, "Failed to clear the log destination"
    #
    #     except (
    #             InvalidParameterException,
    #             PropertyServerException,
    #     ) as e:
    #         print_exception_response(e)
    #         assert False, "Invalid request"
