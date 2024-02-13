"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module is for testing the core OMAG config class and methods
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests.

"""

import json
from contextlib import nullcontext as does_not_raise

import pytest

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from pyegeria.core_omag_server_config import CoreServerConfig

# from pyegeria.admin_services import FullServerConfig

disable_ssl_warnings = True


class TestCoreAdminServices:
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
    good_integ_1 = "fluffy_integration"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "lazView1"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "fluffy_kv"
    good_server_6 = "cocoView1"
    good_engine_host_1 = "governDL01"
    good_view_server_1 = "cocoView1"
    good_view_server_2 = "fluffy_view"
    bad_server_1 = "coco"
    bad_server_2 = ""

    @pytest.mark.parametrize("server, url, user, expectation",
                             [("fluffy", "https://laz.local:9443", "garygeeke", does_not_raise()),
                              ("fluffy", "https://localhost:9443", "garygeeke",
                               pytest.raises(InvalidParameterException)),
                              ("simple-metadata-store", "https://laz.local:9443", "garygeeke", does_not_raise()),
                              (good_server_3, "https://laz.local:9443", "garygeeke", does_not_raise())
                              ])
    def test_get_stored_configuration(self, server, url, user, expectation):
        with expectation as excinfo:
            client = CoreServerConfig(server, url, user)
            config = client.get_stored_configuration()
            assert (type(config) == dict), "There was only an exception response"
            if type(config) is dict:
                print("\n\n" + json.dumps(config, indent=4))

        if excinfo:
            print_exception_response(excinfo.value)

    #
    #   Configure Access Services
    #
    def test_get_configured_access_services(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_configured_access_services()
            assert type(response) is list, "Failed to get access services"
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_configure_all_access_services_good(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_5, self.good_platform1_url,
                self.good_user_1)
            o_client.configure_all_access_services()

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request or improper server configuration"

    def test_configure_all_access_services_bad(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.configure_all_access_services()

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert True, "Invalid request or improper server configuration"

    def test_configure_all_access_services_no_topics(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_5, self.good_platform1_url,
                self.good_user_1)
            o_client.configure_all_access_services_no_topics()

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_all_access_services(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            o_client.clear_all_access_services()
            assert True, "Failed to delete access services"
            print("\n\n\tAll access services cleared")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request - clear access services failed"

    def test_get_access_service_config(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_access_service_config("subject-area")
            assert type(response) is dict, "Failed to get access services"
            if type(response) is dict:
                print("\n\n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_configure_access_service(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            access_service_options = {
                "SupportedZones": ["quarantine", "clinical-trials", "research", "data-lake", "trash-can"]
            }
            o_client.configure_access_service("subject-area", access_service_options)
            print("\n\n\t Configured an access service")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_configure_access_service_no_topics(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            access_service_options = {
                "SupportedZones": ["quarantine", "clinical-trials", "research", "data-lake", "trash-can"]
            }
            o_client.configure_access_service("discovery-engine")

            print("\n\n\t Configured an access service")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_access_service(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            o_client.clear_access_service("subject-area", )
            assert True, "Failed to delete access services"
            print("\n\n\tAll access services cleared")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request - clear access services failed"

    def test_get_access_services_config(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_access_services_configuration()
            assert type(response) is list, "Failed to get access services"
            if type(response) is list:
                print("\n\n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    #   Event Bus Methods
    #
    def test_get_event_bus(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_event_bus()
            if response is None:
                print("\n\n\n\t No event bus configured")
            else:
                assert (response is not None and
                        (type(response) is dict) or (type(response) is str)), "No event bus returned"
                print("\n\n\t\tResponse is: " + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_event_bus(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            event_bus_config = {
                "producer": {
                    "bootstrap.servers": "egeria.pdr-associates.com:7092"
                },
                "consumer": {
                    "bootstrap.servers": "egeria.pdr-associates.com:7092"
                }
            }

            o_client.set_event_bus(event_bus_config)
            assert True
            print("\n\n\t\tSet event bus configuration")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_event_bus(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_event_bus()
            assert True, "Failed to clear event bus"
            print("\n\n\tEvent bus configuration cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    #   Audit Methods
    #
    def test_get_audit_log_destinations(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            destinations = o_client.get_audit_log_destinations()

            print("\n\n" + json.dumps(destinations, indent=4))
            assert destinations is not None, "Failed to get audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_audit_log_destinations(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_audit_log_destinations()
            assert True, "Failed to delete audit logs"
            print("\n\n\tAll audit log destinations cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_a_log_destination(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_a_log_destination("Console- default")
            assert True, "Failed to delete audit logs"
            print("\n\n\tAudit log destinations cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_console_log_destinations(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_console_log_destinations([])
            assert True
            print("\n\n\tConsole log destination added")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_default_log_destinations(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_default_log_destinations()

            print("\n\n\t\tAdded default log destinations")
            assert True

        except(
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_topic_log_destinations(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_event_topic_log_destinations("meow", [])

            print("\n\n\t\tAdded topic log destinations")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_file_log_destinations(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_file_log_destinations("./logs", [])

            print("\n\n\t\tAdded file log destinations")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_slf4j_log_destination(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_slf4j_log_destination()
            assert True
            print("\n\n\t\tAdded slf4j log destination")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    # Basic Repository Config
    #
    def test_set_no_repository_mode(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.set_no_repository_mode()

            assert True

            print("\n\n\t\tNo repository mode set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_local_repository_config(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            config = o_client.get_local_repository_config()
            assert config is not None, "Failed to get repository config"
            print("\n\n" + json.dumps(config, indent=4))


        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_local_repository_config(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            o_client.clear_local_repository_config()
            assert True

            print("\n\n\t\tLocal repository config cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_local_metadata_collection_id(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_local_metadata_collection_id()
            assert response is not None and type(response) is str, "no collection id returned"

            print("\n\nMetadata collection ID GUID is: " + response)

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_local_metadata_collection_id(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            o_client.set_local_metadata_collection_id("aCollectionid")
            assert True

            print("\n\n\t\tMetadata collection id set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_local_metadata_collection_name(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_local_metadata_collection_name()
            assert response is not None and type(response) is str, "no collection id returned"

            print("\n\n\t\tThe metadata collection name is: " + response)

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_local_metadata_collection_name(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            o_client.set_local_metadata_collection_name("aCollectionName")
            assert True

            print("\n\n\t\tMetadata collection id set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    #   Local Repository Config
    #
    def test_set_in_mem_local_repository(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_in_mem_local_repository()
            assert True

            print("\n\n\t\tIn memory repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_graph_local_repository(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_graph_local_repository()
            assert True

            print("\n\n\t\tLocal graph repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_read_only_local_repository(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_read_only_local_repository()
            assert True

            print("\n\n\t\tRead-only repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_xtdb_in_mem_repository(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_xtdb_in_mem_repository()
            assert True

            print("\n\n\t\tXTDB in-memory repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_xtdb_local_kv_repository(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_xtdb_local_kv_repository()
            assert True

            print("\n\n\t\tXTDB local kv repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_xtdb_local_repository(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            body = {
                "class": "Connection",
                "connectorType": {
                    "class": "ConnectorType",
                    "connectorProviderClassName": "org.odpi.egeria.connectors.juxt.xtdb.repositoryconnector.XtdbOMRSRepositoryConnectorProvider"
                },
                "configurationProperties": {
                    "xtdbConfigEDN": """{:xtdb/index-store {:kv-store {:xtdb/module xtdb.rocksdb/->kv-store :db-dir "data/servers/xtdb/rdb-index"}}
                                            :xtdb.lucene/lucene-store {:db-dir "data/servers/xtdb/lucene"
                                                                         :indexer {:xtdb/module xtdb.lucene.egeria/->egeria-indexer}
                                                                         :analyzer {:xtdb/module xtdb.lucene.egeria/->ci-analyzer}}
                                              :xtdb.jdbc/connection-pool {:dialect {:xtdb/module xtdb.jdbc.psql/->dialect}
                                                                          :db-spec {:jdbcUrl "jdbc:postgresql://localhost:5432/xtdb?user=postgres&password=notingres"}}
                                              :xtdb/tx-log {:xtdb/module xtdb.jdbc/->tx-log
                                                            :connection-pool :xtdb.jdbc/connection-pool
                                                            :poll-sleep-duration "PT1S"}
                                              :xtdb/document-store {:xtdb/module xtdb.jdbc/->document-store
                                                                    :connection-pool :xtdb.jdbc/connection-pool}}""",
                    "syncIndex": True
                }
            }
            o_client.set_xtdb_local_repository(body)
            assert True

            print("\n\n\t\tXTDB in-memory repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_open_metadata_archives(self):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_open_metadata_archives()
            if response is not None:
                print("\n\n" + json.dumps(response, indent=4))
                assert True
            else:
                print("\n\n\t No archives found")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_startup_open_metadata_archive(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_startup_open_metadata_archive_file("./content-packs/OpenConnectorsArchive.omarchive")
            assert True

            print("\n\n\t\tArchives added")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_open_metadata_archives(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_open_metadata_archives()
            assert True

            print("\n\n\t\tArchives cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    #   Basic settings and security
    #
    def test_get_basic_server_properties(self):

        try:
            o_client = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_basic_server_properties()
            assert (type(response) is dict) or (type(response) is str), "No server properties returned"
            print("\n\nResponse is: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_basic_server_properties(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_basic_server_properties("view service description", "pdr", "http://laz.local:9443",
                                                 "garygeeke", "admin", 0, "fluffy_view")
            assert True

            print("\n\n\t\tBasic server properties set")

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_server_security_connection(self):

        try:
            o_client = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_server_security_connection()
            if response is None:
                print("No security has been configured")
            else:
                assert (type(response) is dict) or (type(response) is str), "No security connection returned"
                print("\n\n\t\tResponse is: " + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_server_security_connection(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_server_security_connection()
            assert True

            print("\n\n\t\tServer security cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_security_connection(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            body = {
                "class": "Connection",
                "connectorType": {
                    "class": "ConnectorType",
                    "connectorProviderClassName":
                        "org.odpi.openmetadata.metadatasecurity.samples.CocoPharmaServerSecurityProvider"
                }
            }
            o_client.set_server_security_connection(body)
            assert True

            print("\n\n\t\tSecurity connection set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_server_classification(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_server_classification()
            if response is None:
                print("No server properties set")
            else:
                assert type(response) is dict, "No server properties returned"
                print(f"\n\nServer classification is:\n {json.dumps(response, indent=4)}")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    #   Config view services
    #

    def test_get_configured_view_svcs(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_6, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_configured_view_svcs()
            assert (type(response) is str) or (type(response) is list), "No view services"
            print("\n\nView services configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_all_view_services(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_view_server_2, self.good_platform1_url,
                self.good_user_1)

            o_client.config_all_view_services("fluffy", self.good_platform1_url, )
            assert True

            print("\n\n\t\tView service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_all_view_services_w_body(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_view_server_2, self.good_platform1_url,
                self.good_user_1)

            body = {
                "class": "ViewServiceRequestBody",
                "omagserverPlatformRootURL": self.good_platform1_url,
                "omagserverName": self.good_server_5,
                "resourceEndpoints": [
                    {
                        "class": "ResourceEndpointConfig",
                        "resourceCategory": "Platform",
                        "description": "Core Platform",
                        "platformName": "Core",
                        "platformRootURL": self.good_platform1_url
                    },
                    {
                        "class": "ResourceEndpointConfig",
                        "resourceCategory": "Platform",
                        "description": "DataLake Platform",
                        "platformName": "DataLake",
                        "platformRootURL": self.good_platform1_url
                    },
                    {
                        "class": "ResourceEndpointConfig",
                        "resourceCategory": "Platform",
                        "description": "Development Platform",
                        "platformName": "Development",
                        "platformRootURL": self.good_platform1_url
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

            o_client.config_all_view_services_w_body(body)
            assert True

            print("\n\n\t\tView service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_all_view_svcs(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_6, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_all_view_services()
            assert True

            print("\n\n\t\tView services cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_view_svc_config(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_6, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_view_svc_config("glossary-author")
            assert (type(response) is dict) or (type(response) is str), "No view services"
            print("\n\nView services configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_view_service(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_view_server_2, self.good_platform1_url,
                self.good_user_1)

            o_client.config_view_service("glossary-author", "cocoMDS1",
                                         self.good_platform1_url)
            assert True

            print("\n\n\t\tView service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_view_svcs(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_server_security_connection("rex")
            assert True

            print("\n\n\t\tView service cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_view_svcs_config(self):
        try:
            o_client = CoreServerConfig(
                self.good_view_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_view_svcs_config()
            assert (type(response) is list) or (type(response) is str), "No view services"
            print("\n\nView services configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

#
#     Cohort Configuration, etc
#



    def test_get_server_type(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_server_type_classification()
            assert (type(response) is dict) or (type(response) is str), "No view services"
            print("\n\nServer Types: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_cohort_registration(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.add_cohort_registration("pdr-cohort")
            assert True

            print("\n\n\t\tAdded to cohort")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_cohort_config(self):
        try:
            o_client = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_cohort_config("pdr-cohort")
            assert (type(response) is dict) or (type(response) is str), "No view services"
            print("\n\nView services configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_deploy_server_config(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            target_platform_body = {
                "urlRoot": "https://hades.local:9443"
            }

            o_client.deploy_server_config(target_platform_body)
            assert True

            print("\n\n\t\tDeployed to target")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    #   Integration Groups
    #
    def test_clear_all_integration_groups(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_all_integration_groups()
            assert True

            print("\n\n\t\tAll integration groups cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_an_integration_groups(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_an_integration_groups("newton")
            assert True

            print("\n\n\t\tAn integration group cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_integration_groups_config(self):
        try:
            o_client = CoreServerConfig(
                self.good_integ_1, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_integration_groups_config()
            assert (type(response) is list) or (type(response) is str), "No integration groups found"
            print("\n\nIntegration Groups configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_integration_group(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_4, self.good_platform1_url,
                self.good_user_1)

            o_client.config_integration_group("fluffy", self.good_platform1_url,
                                              "Egeria:IntegrationGroup:DefaultIntegrationGroup")
            assert True

            print("\n\n\t\tConfigured Integration Group")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    #
    # Engine Configurations
    #
    def test_clear_engine_definitions_client_configs(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_engine_host_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_engine_definitions_client_config()
            assert True

            print("\n\n\t\tEngine definition client configuration cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_engine_definitions_client_config(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_engine_host_1, self.good_platform1_url,
                self.good_user_1)

            o_client.set_engine_definitions_client_config(self.good_server_5,
                                                          self.good_platform1_url)
            assert True

            print("\n\n\t\tClient config for engine definition set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_an_engine_list(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_engine_host_1, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_an_engine_list()
            assert True

            print("\n\n\t\tEngine list cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    # def test_get_engine_list(self):
    #     try:
    #         o_client = CoreServerConfig(
    #             self.good_engine_host_1, self.good_platform1_url,
    #             self.good_user_1)
    #
    #         response = o_client.get_engine_list()
    #         assert (type(response) is list) or (type(response) is str), "No Engine List found"
    #         print("\n\nEngine List: \n" + json.dumps(response, indent=4))
    #
    #     except (
    #             InvalidParameterException,
    #             PropertyServerException,
    #             UserNotAuthorizedException
    #     ) as e:
    #         print_exception_response(e)
    #         assert False, "Invalid request"

    def test_get_engine_host_services_config(self):
        try:
            o_client = CoreServerConfig(
                self.good_engine_host_1, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_engine_host_services_config()
            assert (type(response) is dict) or (type(response) is str), "No Engine List found"
            print("\n\nEngine List: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_engine_list(self):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_engine_host_1, self.good_platform1_url,
                self.good_user_1)

            engine_list_body = [
                {
                    "class": "EngineConfig",
                    "engineQualifiedName": "AssetDiscovery",
                    "engineUserId": "findItDL01npa"
                },
                {
                    "class": "EngineConfig",
                    "engineQualifiedName": "AssetQuality",
                    "engineUserId": "findItDL01npa"
                }
            ]

            o_client.set_engine_list(engine_list_body)
            assert True

            print("\n\n\t\tEngine list set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"
