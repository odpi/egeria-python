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
    good_platform3_url = "https://127.0.0.1:9445"
    bad_platform1_url = "https://localhost"


    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""
    good_integ_1 = "integration-daemon"
    good_server_1 = "simple-metadata-store"
    good_server_2 = "cocoMDS1"
    good_server_3 = "active-metadata-store"
    good_server_4 = "integration-daemon"
    good_server_5 = "engine-host"
    good_server_6 = "cocoView1"
    good_engine_host_1 = "engine-host"
    good_view_server_1 = "view-server"
    good_view_server_2 = "cocoView1"
    bad_server_1 = "coc"
    bad_server_2 = ""

    @pytest.mark.parametrize("server, url, user, expectation",
                             # [
                             [(good_server_4, good_platform1_url, "garygeeke", does_not_raise()),
                              (bad_server_1, bad_platform1_url, "garygeeke",
                               pytest.raises(InvalidParameterException)),
                              (good_server_3, good_platform1_url, "garygeeke", does_not_raise()),
                              (good_server_1, good_platform1_url, "garygeeke", does_not_raise())
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

    def test_is_server_configured(self, server:str = good_server_4):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            configured = o_client.is_server_configured()
            assert True
            print(f"\n\n\t Server {server} configured status is {configured}")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"


    #
    #   Configure Access Services
    #
    def test_get_configured_access_services(self,server:str = good_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_configured_access_services()
            assert type(response) is list, "Failed to get access services"
            if type(response) is list:
                print(f"\n\n\t Response for server {server} is: {json.dumps(response, indent=4)}")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_configure_all_access_services_good(self, server:str = good_server_3):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.configure_all_access_services()
            print(f"\n\n\t Server {server} has all access services configured")
            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request or improper server configuration"

    def test_configure_all_access_services_bad(self, server:str = bad_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.bad_platform1_url,
                self.good_user_1)
            o_client.configure_all_access_services()
            print(f"\n\n Expected this to fail for {server} - why didn't it?")
            assert False
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print("Expected this to fail")
            print_exception_response(e)
            assert True, "Invalid request or improper server configuration"

    def test_configure_all_access_services_no_topics(self, server:str = good_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.configure_all_access_services_no_topics()
            print(f"\n\n\t Server {server} has all access services configured")
            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_all_access_services(self, server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.clear_all_access_services()
            assert True, "Failed to delete access services"
            print(f"\n\n\tServer {server} has all access services cleared")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request - clear access services failed"

    def test_get_access_service_config(self, server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_access_service_config("subject-area")
            print(f"\n\n\t Config for server {server} is:")
            if type(response) is dict:
                print(json.dumps(response, indent=4))
            elif type(response) is str:
                print(f"response was: {response}")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_configure_access_service(self, server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            access_service_options = {
                "SupportedZones": ["quarantine", "clinical-trials", "research", "data-lake", "trash-can"]
            }
            o_client.configure_access_service("subject-area", access_service_options)
            print(f"\n\n\t Server {server} configured an access service")
            assert True
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_configure_access_service_no_topics(self, server:str = good_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            access_service_options = {
                "SupportedZones": ["quarantine", "clinical-trials", "research", "data-lake", "trash-can"]
            }
            o_client.configure_access_service("discovery-engine", access_service_options)
            assert True
            print(f"\n\n\t Server {server} configured an access service")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_access_service(self,server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.clear_access_service("subject-area", )
            assert True, "Failed to delete access services"
            print(f"\n\n\tserver {server} has all access services cleared")
        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request - clear access services failed"

    def test_get_access_services_config(self,server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_access_services_configuration()
            assert type(response) is list, "Failed to get access services"
            if type(response) is list:
                print(f"\n\n\t Server {server} access services: \njson.dumps(response, indent=4)")

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
    def test_get_event_bus(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_event_bus()
            print(f"\n\n\t Server {server} event bus: \n")
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

    def test_set_event_bus(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
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
            print(f"\n\n\t\tServer {server} -Set event bus configuration")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_event_bus(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_event_bus()
            assert True, "Failed to clear event bus"
            print(f"\n\n\tServer {server}: Event bus configuration cleared")

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
    def test_get_audit_log_destinations(self, server:str = good_server_3):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            destinations = o_client.get_audit_log_destinations()

            print(f"\n\n\tServer {server}:\n {json.dumps(destinations, indent=4)}")
            assert destinations is not None, "Failed to get audit log destinations"

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_audit_log_destinations(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_audit_log_destinations()
            assert True, "Failed to delete audit logs"
            print(f"\n\n\tServer {server}: All audit log destinations cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_a_log_destination(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_a_log_destination("Console- default")
            assert True, "Failed to delete audit logs"
            print(f"\n\n\tServer {server}: Audit log destinations cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_console_log_destinations(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_console_log_destinations([])
            assert True
            print(f"\n\n\tServer {server}: Console log destination added")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_default_log_destinations(self, server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_default_log_destinations()

            print(f"\n\n\t\tServer {server}:Added default log destinations")
            assert True

        except(
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_topic_log_destinations(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_event_topic_log_destinations("meow", [])

            print(f"\n\n\t\tServer {server}: Added topic log destinations")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_file_log_destinations(self, server: str = good_server_2):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_file_log_destinations("./logs", ["Error","Exception"])

            print(f"\n\n\t\tServer {server}: Added file log destinations")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_slf4j_log_destination(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_slf4j_log_destination()
            assert True
            print(f"\n\n\t\tServer {server}: Added slf4j log destination")

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
    def test_set_no_repository_mode(self, server: str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.set_no_repository_mode()
            print(f"\n\n\t\tServer {server}: Set no_repository_mode")
            assert True

            print("\n\n\t\tNo repository mode set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_local_repository_config(self, server: str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            config = o_client.get_local_repository_config()
            assert config is not None, "Failed to get repository config"
            print(f"\n\n\tServer {server}: json.dumps(config, indent=4)")


        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_local_repository_config(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.clear_local_repository_config()
            assert True

            print(f"\n\n\t\tServer {server}: Local repository config cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_local_metadata_collection_id(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_local_metadata_collection_id()
            assert response is not None and type(response) is str, "no collection id returned"

            print(f"\n\n\tServer {server}: Metadata collection ID GUID is: " + response)

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_local_metadata_collection_id(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.set_local_metadata_collection_id("aCollectionid")
            assert True

            print(f"\n\n\t\tServer {server}: Metadata collection id set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_local_metadata_collection_name(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_local_metadata_collection_name()
            assert response is not None and type(response) is str, "no collection id returned"

            print(f"\n\n\t\tServer {server}: The metadata collection name is: " + response)

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_local_metadata_collection_name(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.set_local_metadata_collection_name("aCollectionName")
            assert True

            print(f"\n\n\t\tServer {server}: Metadata collection id set")

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
    def test_set_in_mem_local_repository(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.set_in_mem_local_repository()
            assert True

            print(f"\n\n\t\tServer {server}: In memory repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_graph_local_repository(self,server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            o_client.set_graph_local_repository()
            assert True

            print(f"\n\n\t\tServer {server}: Local graph repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_read_only_local_repository(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_read_only_local_repository()
            assert True

            print(f"\n\n\t\tServer {server}: Read-only repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_plug_in_repository(self, server:str = good_server_2):
        server_name = server
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            full_config_body = {
                "class": "Connection",
                "connectorType": {
                    "class": "ConnectorType",
                    "connectorProviderClassName": "org.odpi.egeria.connectors.juxt.xtdb.repositoryconnector.XtdbOMRSRepositoryConnectorProvider"
                },
                "configurationProperties": {
                    "xtdbConfig": {
                        "xtdb.lucene/lucene-store": {
                            "db-dir": "data/servers/" + server_name + "/xtdb/lucene"
                        },
                        "xtdb/index-store": {
                            "kv-store": {
                                "xtdb/module": "xtdb.rocksdb/->kv-store",
                                "db-dir": "data/servers/" + server_name + "/xtdb/rdb-index"
                            }
                        },
                        "xtdb/document-store": {
                            "kv-store": {
                                "xtdb/module": "xtdb.rocksdb/->kv-store",
                                "db-dir": "data/servers/" + server_name + "/xtdb/rdb-docs"
                            }
                        },
                        "xtdb/tx-log": {
                            "kv-store": {
                                "xtdb/module": "xtdb.rocksdb/->kv-store",
                                "db-dir": "data/servers/" + server_name + "/xtdb/rdb-tx"
                            }
                        }
                    }
                }
            }
            o_client.set_plug_in_repository(full_config_body)
            assert True

            print(f"\n\n\t\tServer {server}: Plug-in repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"


    def test_set_xtdb_in_mem_repository(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_xtdb_in_mem_repository()
            assert True

            print(f"\n\n\t\tServer {server}: XTDB in-memory repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_xtdb_local_kv_repository(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_xtdb_local_kv_repository()
            assert True

            print(f"\n\n\t\tServer {server}: XTDB local kv repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_xtdb_local_repository(self, server:str = good_server_1):

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

            print(f"\n\n\t\tServer {server}: XTDB in-memory repository type set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_open_metadata_archives(self, server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)
            response = o_client.get_open_metadata_archives()
            if response is not None:
                print(f"\n\n\tServer {server}: \njson.dumps(response, indent=4)")
                assert True
            else:
                print(f"\n\n\t Server {server}: No archives found")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_startup_open_metadata_archive(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_startup_open_metadata_archive_file("./content-packs/OpenConnectorsArchive.omarchive")
            assert True

            print(f"\n\n\t\tServer {server}: Archives added")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_open_metadata_archives(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_open_metadata_archives()
            assert True

            print(f"\n\n\t\tServer {server}: Archives cleared")

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
    def test_get_basic_server_properties(self, server:str = good_server_1):

        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_basic_server_properties()
            assert (type(response) is dict) or (type(response) is str), "No server properties returned"
            print(f"\n\nServer {server}: Response is- \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_basic_server_properties(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)
            o_client.set_basic_server_properties("view service description", "pdr", "http://laz.local:9443",
                                                 "garygeeke", "admin", 0, "fluffy_view")
            assert True

            print(f"\n\n\t\tServer {server}: Basic server properties set")

        except (
                InvalidParameterException,
                PropertyServerException,
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_server_security_connection(self, server:str = good_server_1):

        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_server_security_connection()
            print(f"Server {server}:\n")
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

    def test_clear_server_security_connection(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_server_security_connection()
            assert True

            print(f"\n\n\t\tServer {server}: Server security cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_security_connection(self, server:str = good_server_1):

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

            print(f"\n\n\t\tServer {server}: Security connection set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_server_classification(self, server:str = good_server_1):
        try:
            o_client = CoreServerConfig(
                self.good_server_2, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_server_classification()
            print(f"Server {server}:\n")
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

    def test_get_configured_view_svcs(self, server:str = good_view_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_configured_view_svcs()
            assert (type(response) is str) or (type(response) is list), "No view services"
            print(f"\n\n\tServer {server}: View services configuration- \n{json.dumps(response, indent=4)}")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_all_view_services(self, server:str = good_view_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.config_all_view_services(self.good_server_3, self.good_platform1_url, )
            assert True

            print(f"\n\n\t\tServer {server}: View service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_all_view_services_w_body(self, server:str = good_view_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,self.good_user_1)

            body = {
                "class": "ViewServiceRequestBody",
                "omagserverPlatformRootURL": self.good_platform1_url,
                "omagserverName": self.good_server_3,
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

            print(f"\n\n\t\tServer {server}: View service set using body")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_all_view_svcs(self, server:str = good_view_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_all_view_services()
            assert True

            print(f"\n\n\t\tServer {server}: View services cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_view_svc_config(self, server:str = good_view_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_view_svc_config("glossary-author")
            assert (type(response) is dict) or (type(response) is str), "No view services"
            print(f"\n\nServer {server} view services configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_view_service(self, server:str = good_view_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.config_view_service("glossary-browser", self.good_server_3,
                                         self.good_platform1_url)
            assert True

            print(f"\n\n\t\tServer {server}: view service set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_view_svc(self, server:str = good_view_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_view_service("server-author")
            assert True

            print(f"\n\n\t\tServer {server}: view service cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_view_svcs_config(self, server:str = "cocoView1"):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_view_svcs_config()
            assert (type(response) is list) or (type(response) is str), "No view services"
            print(f"\n\nServer {server}: view services configuration: \n" + json.dumps(response, indent=4))

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



    def test_get_server_type(self, server:str = good_view_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_server_type_classification()
            assert (type(response) is dict) or (type(response) is str), "No view services"
            print(f"\n\nServer {server}: type is: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_add_cohort_registration(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.add_cohort_registration("pdr-cohort")
            assert True

            print(f"\n\n\t\tServer {server}: added to cohort")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_cohort_config(self, server:str = good_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_cohort_config("pdr-cohort")
            assert (type(response) is dict) or (type(response) is str), "No view services"
            print(f"\n\nServer {server}: cohort configuration: \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_deploy_server_config(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            target_platform_body = {
                "urlRoot": "https://cray.local:9443"
            }

            o_client.deploy_server_config(target_platform_body)
            assert True

            print(f"\n\n\t\tServer {server}: Deployed to target")

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
    def test_clear_all_integration_groups(self, server:str = good_integ_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_all_integration_groups()
            assert True

            print(f"\n\n\t\tServer {server}: all integration groups cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_an_integration_group(self, server:str = good_integ_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_an_integration_group("Egeria:IntegrationGroup:DefaultIntegrationGroup")
            assert True

            print(f"\n\n\t\tServer {server}: An integration group cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_integration_groups_config(self, server:str = good_integ_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_integration_groups_config()
            assert (type(response) is list) or (type(response) is str), "No integration groups found"
            print(f"\n\nServer {server}: Integration Groups configuration- \n" + json.dumps(response, indent=4))

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_config_integration_group(self, server:str = good_integ_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.config_integration_group(self.good_server_3, self.good_platform1_url,
                                              "Egeria:IntegrationGroup:DefaultIntegrationGroup")
            assert True

            print(f"\n\n\t\tServer {server}: configured Integration Group")

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
    def test_clear_engine_definitions_client_configs(self, server:str = good_engine_host_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_engine_definitions_client_config()
            assert True

            print(f"\n\n\t\tServer {server}: engine definition client configuration cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_engine_definitions_client_config(self, server:str = good_engine_host_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.set_engine_definitions_client_config(self.good_server_3,
                                                          self.good_platform1_url)
            assert True

            print(f"\n\n\t\tServer {server}: client config for engine definition set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_engine_list(self, server:str = good_engine_host_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_engine_list()
            assert True

            print(f"\n\n\t\tServer {server}: Engine list cleared")

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

    def test_get_engine_host_services_config(self, server:str = good_engine_host_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            response = o_client.get_engine_host_services_config()
            assert (type(response) is dict) or (type(response) is str), "No Engine List found"
            print(f"\n\n\tServer {server} Engine List: {json.dumps(response, indent=4)}")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_engine_list(self, server:str = good_engine_host_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
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

            print(f"\n\n\t\tServer {server}: Engine list set")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_get_placeholder_variables(self, server:str = good_server_1):
        try:
            o_client = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_2)

            response = o_client.get_placeholder_variables()
            if type(response) is dict:
                print(f"\n\n\tPlaceholder variables are: \n{json.dumps(response, indent=4)}")
            else:
                print("\n\n\tNo placeholders found")
            assert True

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_clear_placeholder_variables(self, server:str = good_server_1):
        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            o_client.clear_placeholder_variables()
            assert True

            print(f"\n\n\t\tPlaceholder variables have been cleared")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

    def test_set_placeholder_variables(self, server:str = good_server_1):

        try:
            o_client: CoreServerConfig = CoreServerConfig(
                server, self.good_platform1_url,
                self.good_user_1)

            placeholder_variables = {
                "freddie_endpoint": "http://localhost:9092",
                "ingres-endpoint": "http://localhost:4321"
            }
            o_client.set_placeholder_variables(placeholder_variables)
            assert True

            print(f"\n\n\t\tSet placeholder variables: \n {placeholder_variables}")

        except (
                InvalidParameterException,
                PropertyServerException,
                UserNotAuthorizedException
        ) as e:
            print_exception_response(e)
            assert False, "Invalid request"

# todo: test case for set repository proxy details