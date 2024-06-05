"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the platform_services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.
"""

import json

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.full_omag_server_config import FullServerConfig

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestAdminServices:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://127.0.0.1:9444"
    bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "active-metadata-store"
    good_server_2 = "cocoMDS2"
    good_server_3 = "cocoMDS1"
    bad_server_1 = "coco"
    bad_server_2 = ""

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
            o_client = FullServerConfig(
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

    def test_get_access_services_topic_names(self):
        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_access_services_topic_names("Asset Owner OMAS")

            assert (response is not None and type(response) is dict), "No topic names"

            print("\n\n\t\tResponse is: " + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"


    def test_all_get_access_services_topic_names(self):
        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_all_access_services_topic_names()

            assert (response is not None and type(response) is dict), "No topic names"

            print("\n\n\t\tResponse is: " + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_event_bus(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_event_bus()

            assert (response is not None and type(response) is dict), "No event bus returned"

            print("\n\n\t\tResponse is: " + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_event_bus(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.set_event_bus("EventBusConfig", "egeria.omag")
            assert True
            print("\n\n\t\tSet event bus configuration")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_startup_open_metadata_archive(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            archive_config_body = {
                "class": "Connection",
                "headerVersion": 0,
                "displayName": "Open Metadata Archive File content-packs/OpenConnectorsArchive.omarchive Connection",
                "connectorType": {
                    "class": "ConnectorType",
                    "headerVersion": 0,
                    "type": {
                        "typeId": "954421eb-33a6-462d-a8ca-b5709a1bd0d4",
                        "typeName": "ConnectorType",
                        "typeVersion": 1,
                        "typeDescription": "A set of properties describing a type of connector."
                    },
                    "guid": "f4b49aa8-4f8f-4e0d-a725-fef8fa6ae722",
                    "qualifiedName": "Egeria:OpenMetadataArchiveStoreConnector:File",
                    "displayName": "File-based Open Metadata Archive Store Connector",
                    "description": "Connector supports storing of an open metadata archive as a single file stored using JSON format.",
                    "connectorProviderClassName": "org.odpi.openmetadata.adapters.repositoryservices.archiveconnector.file.FileBasedOpenMetadataArchiveStoreProvider",
                    "connectorFrameworkName": "Open Connector Framework (OCF)",
                    "connectorInterfaceLanguage": "Java",
                    "connectorInterfaces": [
                        "org.odpi.openmetadata.frameworks.connectors.SecureConnectorExtension",
                        "org.odpi.openmetadata.frameworks.auditlog.AuditLoggingComponent",
                        "org.odpi.openmetadata.repositoryservices.connectors.stores.archivestore.OpenMetadataArchiveStore"
                    ]
                },
                "endpoint": {
                    "class": "Endpoint",
                    "headerVersion": 0,
                    "address": "content-packs/OpenConnectorsArchive.omarchive"
                }
            }
            o_client.add_startup_open_metadata_archive_file(archive_config_body)
            assert True

            print("\n\n\t\tArchives added")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_view_service(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            view_config_body = iew_svc_body = {
                "class": "SolutionViewServiceConfig",
                "omagserverName": "fluffy",
                "omagserverPlatformRootURL": "https://lex.local:9443"
            }

            o_client.config_view_service("glossary-author", view_config_body)
            assert True

            print("\n\n\t\tView service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_view_service_config(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_view_server_2, self.good_platform1_url,
                self.good_user_1)
            view_svc_body = {
                "class": "SolutionViewServiceConfig",
                "omagserverName": "fluffy",
                "omagserverPlatformRootURL": "https://lex.local:9443"
            }

            o_client.config_view_service("glossary-author", view_svc_body)
            assert True

            print("\n\n\t\tView service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_server_type(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_server_type()
            assert True

            print("\n\n\t\tService type cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_max_paging_size(self):

        try:
            o_client: FullServerConfig = FullServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.set_max_page_size(5000)
            assert True

            print("\n\n\t\tService type cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"