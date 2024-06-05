"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the platform_services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework. These tests are not idempotent - much
more work would be needed to ensure that they work correctly in any order. That said, running the last test,
`test_platform_services` does a fairly good job of exercising the test cases in the right sequence - and so is a
good way to start.

A running Egeria environment is needed to run these tests. A set of platform, server and user variables are
created local to the TestPlatform class to hold the set of values to be used for testing. The default values have
been configured based on pre-built startup Egeria configurations and the local testing environment. The pre-built
configurations are documented at
`https://github.com/odpi/egeria/blob/main/open-metadata-resources/open-metadata-deployment/sample-configs/README.md`.

However, the tests are not dependent on this configuration. It should, however, be noted that the tests are currently
order sensitive - in other words if you delete all the servers the subsequent tests that expect the servers to be
available may fail..

"""

import time
import pytest
import json
from time import sleep

from contextlib import nullcontext as does_not_raise

disable_ssl_warnings = True

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import inspect

from pyegeria.platform_services import Platform
from pyegeria.server_operations import ServerOps


class TestPlatform:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://egeria.pdr-associates.com:7443"
    good_platform3_url = "https://egeria.pdr-associates.com:9443"
    bad_platform1_url = "https://localhost:9443"

    # good_platform1_url = "https://127.0.0.1:30080"
    # good_platform2_url = "https://127.0.0.1:30081"
    # bad_platform1_url = "https://localhost:9443"

    good_user_1 = "garygeeke"
    good_user_2 = "erinoverview"
    bad_user_1 = "eviledna"
    bad_user_2 = ""

    good_server_1 = "active-metadata-store"
    good_server_2 = "simple-metadata-store"
    good_server_3 = "view-server"
    good_server_4 = "engine-host"
    bad_server_1 = "coco"
    bad_server_2 = ""

    @pytest.mark.parametrize(
        "server, url, user_id, exc_type, expectation",
        [
            # (
            #         "meow",
            #         "https://google.com",
            #         "garygeeke",
            #         "InvalidParameterException",
            #         pytest.raises(InvalidParameterException),
            # ),
            (
                    "active-metadata-server",
                    "https://localhost:9443",
                    "garygeeke",
                    "nothing",
                    does_not_raise(),
            ),
            # (
            #         "cocoMDS1",
            #         good_platform3_url,
            #         "garygeeke",
            #         "",
            #         does_not_raise(),
            # ),
            # (
            #         "cocoMDS2",
            #         "https://127.0.0.1:9443",
            #         None,
            #         "InvalidParameterException",
            #         pytest.raises(InvalidParameterException),
            # ),
            # (
            #         "cocoMDS2",
            #         "https://127.0.0.1:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
            #         "meow",
            #         "InvalidParameterException",
            #         pytest.raises(InvalidParameterException),
            # ),
            # ("", "", "", "InvalidParameterException", pytest.raises(InvalidParameterException)),
        ],
    )
    def test_get_platform_origin(self, server, url, user_id, exc_type, expectation):
        with expectation as excinfo:
            p_client = Platform(server, url, user_id)
            response_text = p_client.get_platform_origin()
            if response_text is not None:
                print("\n\n" + response_text)
                assert True
        if excinfo:
            print_exception_response(excinfo.value)
            assert excinfo.typename is exc_type, "Unexpected exception"

    def test_shutdown_platform(self, server: str = good_server_1):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.shutdown_platform()
            print(f"\n\n\t Platform shutdown")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code is not "200", "Invalid parameters"
        finally:
            p_client.close_session()

    def test_activate_server_stored_config(self, server: str = "active-metadata-store"):
        """
        Need to decide if its worth it to broaden out the test cases..for instance
        in this method if there is an exception - such as invalid server name
        then the test case fails because the response is used before set..

        """
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.activate_server_stored_config(server)
            print(f"\n\n\t server {server} configured and activated successfully")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_shutdown_server(self, server: str = 'cocoMDS1'):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.shutdown_server(server)
            print(f"\n\n\t server {server} was shut down successfully")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code == 404, "Invalid parameters"
        finally:
            p_client.close_session()

    def test_get_known_servers(self, server: str = good_server_2):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_known_servers()
            print(f"\n\n\t response = {response}")
            assert len(response) > 0, "Empty server list"

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"
        finally:
            p_client.close_session()

    def test_shutdown_unregister_servers(self, server: str = good_server_2):
        try:
            p_client = Platform(
                server, self.good_platform1_url, self.good_user_1
            )
            p_client.shutdown_unregister_servers()
            print(f"\n\n\t Servers on platform {p_client.platform_url} shutdown and unregistered")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"
        finally:
            p_client.close_session()

    @pytest.mark.parametrize(
        "server, url, user_id, ex_type, expectation",
        [
            (
                "meow",
                "https://google.com",
                "garygeeke",
                "InvalidParameterException",
                pytest.raises(InvalidParameterException),
            ),
            (
                "cocoMDS2",
                "https://localhost:9448",
                "garygeeke",
                "InvalidParameterException",
                pytest.raises(InvalidParameterException),
            ),
            (
                "cocoMDS1",
                "https://127.0.0.1:30081",
                "garygeeke",
                "InvalidParameterException",
                pytest.raises(InvalidParameterException),
            ),
            (
                "cocoMDS9",
                "https://127.0.0.1:9443",
                "garygeeke",
                "InvalidParameterException",
                does_not_raise(),
            ),
            (
                    good_server_2,
                    "https://127.0.0.1:9443",
                    "garygeeke",
                    None,
                    does_not_raise(),
            ),
            (
                    "cocoMDS2",
                    "https://127.0.0.1:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
                    "meow",
                    "UserNotAuthorizedException",
                    pytest.raises(UserNotAuthorizedException)
            )
        ],
    )
    def test_get_active_configuration(
            self, server, url, user_id, ex_type, expectation
    ):
        with Platform(server, url, user_id) as p_client:
            with expectation as excinfo:
                response = p_client.get_active_configuration(server)
                print(f"\n\n\tThe active configuration of {server} is \n{json.dumps(response, indent=4)}")
                assert True

            if excinfo:
                print_exception_response(excinfo.value)
                assert excinfo.typename is ex_type

    def test_activate_server_supplied_config(self, server: str = good_server_3):
        server_name = server
        config_body = {
            "class": "OMAGServerConfig",
            "versionId": "V2.0",
            "localServerId": "f81bbe7a-2592-4afe-bd851-64dfb3bd7920",
            "localServerName": "test-store",
            "localServerURL": "https://localhost:9443",
            "localServerUserId": "activemdsnpa",
            "maxPageSize": 1000,
            "eventBusConfig": {
                "class": "EventBusConfig",
                "topicURLRoot": "egeria.omag",
                "configurationProperties": {
                    "producer": {
                        "bootstrap.servers": "localhost:9092"
                    },
                    "consumer": {
                        "bootstrap.servers": "localhost:9092"
                    }
                }
            },
            "accessServicesConfig": [
                {
                    "class": "AccessServiceConfig",
                    "accessServiceId": 210,
                    "accessServiceDevelopmentStatus": "STABLE",
                    "accessServiceAdminClass": "org.odpi.openmetadata.accessservices.datamanager.admin.DataManagerAdmin",
                    "accessServiceName": "Data Manager",
                    "accessServiceFullName": "Data Manager OMAS",
                    "accessServiceURLMarker": "data-manager",
                    "accessServiceDescription": "Capture changes to the data stores and data set managed by a data manager such as a database server, content manager or file system.",
                    "accessServiceWiki": "https://egeria-project.org/services/omas/data-manager/overview/",
                    "accessServiceOperationalStatus": "ENABLED",
                    "accessServiceOutTopic": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Kafka Event Bus Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.kafka.KafkaOpenMetadataTopicProvider"
                        },
                        "endpoint": {
                            "class": "Endpoint",
                            "headerVersion": 0,
                            "address": "egeria.omag.server.test-store.omas.datamanager.outTopic"
                        },
                        "configurationProperties": {
                            "producer": {
                                "bootstrap.servers": "localhost:9092"
                            },
                            "local.server.id": "f81bbe7a-2592-4afe-bd81-64dfb3bd7920",
                            "consumer": {
                                "bootstrap.servers": "localhost:9092"
                            }
                        }
                    }
                },
                {
                    "class": "AccessServiceConfig",
                    "accessServiceId": 204,
                    "accessServiceDevelopmentStatus": "STABLE",
                    "accessServiceAdminClass": "org.odpi.openmetadata.accessservices.assetmanager.admin.AssetManagerAdmin",
                    "accessServiceName": "Asset Manager",
                    "accessServiceFullName": "Asset Manager OMAS",
                    "accessServiceURLMarker": "asset-manager",
                    "accessServiceDescription": "Manage metadata from a third party asset manager",
                    "accessServiceWiki": "https://egeria-project.org/services/omas/asset-manager/overview/",
                    "accessServiceOperationalStatus": "ENABLED",
                    "accessServiceOutTopic": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Kafka Event Bus Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.kafka.KafkaOpenMetadataTopicProvider"
                        },
                        "endpoint": {
                            "class": "Endpoint",
                            "headerVersion": 0,
                            "address": "egeria.omag.server.test-store.omas.assetmanager.outTopic"
                        },
                        "configurationProperties": {
                            "producer": {
                                "bootstrap.servers": "localhost:9092"
                            },
                            "local.server.id": "f81bbe7a-2592-4afe-bd81-64dfb3bd7920",
                            "consumer": {
                                "bootstrap.servers": "localhost:9092"
                            }
                        }
                    }
                },
                {
                    "class": "AccessServiceConfig",
                    "accessServiceId": 207,
                    "accessServiceDevelopmentStatus": "STABLE",
                    "accessServiceAdminClass": "org.odpi.openmetadata.accessservices.communityprofile.admin.CommunityProfileAdmin",
                    "accessServiceName": "Community Profile",
                    "accessServiceFullName": "Community Profile OMAS",
                    "accessServiceURLMarker": "community-profile",
                    "accessServiceDescription": "Define personal profile and collaborate.",
                    "accessServiceWiki": "https://egeria-project.org/services/omas/community-profile/overview/",
                    "accessServiceOperationalStatus": "ENABLED",
                    "accessServiceOutTopic": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Kafka Event Bus Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.kafka.KafkaOpenMetadataTopicProvider"
                        },
                        "endpoint": {
                            "class": "Endpoint",
                            "headerVersion": 0,
                            "address": "egeria.omag.server.test-store.omas.communityprofile.outTopic"
                        },
                        "configurationProperties": {
                            "producer": {
                                "bootstrap.servers": "localhost:9092"
                            },
                            "local.server.id": "f81bbe7a-2592-4afe-bd81-64dfb3bd7920",
                            "consumer": {
                                "bootstrap.servers": "localhost:9092"
                            }
                        }
                    }
                },
                {
                    "class": "AccessServiceConfig",
                    "accessServiceId": 227,
                    "accessServiceDevelopmentStatus": "STABLE",
                    "accessServiceAdminClass": "org.odpi.openmetadata.accessservices.governanceserver.admin.GovernanceServerAdmin",
                    "accessServiceName": "Governance Server",
                    "accessServiceFullName": "Governance Server OMAS",
                    "accessServiceURLMarker": "governance-server",
                    "accessServiceDescription": "Supply the governance engine definitions to the engine hosts and the and integration group definitions to the integration daemons.",
                    "accessServiceWiki": "https://egeria-project.org/services/omas/governance-server/overview/",
                    "accessServiceOperationalStatus": "ENABLED",
                    "accessServiceOutTopic": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Kafka Event Bus Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.kafka.KafkaOpenMetadataTopicProvider"
                        },
                        "endpoint": {
                            "class": "Endpoint",
                            "headerVersion": 0,
                            "address": "egeria.omag.server.test-store.omas.governanceserver.outTopic"
                        },
                        "configurationProperties": {
                            "producer": {
                                "bootstrap.servers": "localhost:9092"
                            },
                            "local.server.id": "f81bbe7a-2592-4afe-bd81-64dfb3bd7920",
                            "consumer": {
                                "bootstrap.servers": "localhost:9092"
                            }
                        }
                    }
                },
                {
                    "class": "AccessServiceConfig",
                    "accessServiceId": 219,
                    "accessServiceDevelopmentStatus": "STABLE",
                    "accessServiceAdminClass": "org.odpi.openmetadata.accessservices.governanceengine.admin.GovernanceEngineAdmin",
                    "accessServiceName": "Governance Engine",
                    "accessServiceFullName": "Governance Engine OMAS",
                    "accessServiceURLMarker": "governance-engine",
                    "accessServiceDescription": "Provide metadata services and watch dog notification to the governance action services.",
                    "accessServiceWiki": "https://egeria-project.org/services/omas/governance-engine/overview/",
                    "accessServiceOperationalStatus": "ENABLED",
                    "accessServiceOutTopic": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Kafka Event Bus Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.kafka.KafkaOpenMetadataTopicProvider"
                        },
                        "endpoint": {
                            "class": "Endpoint",
                            "headerVersion": 0,
                            "address": "egeria.omag.server.test-store.omas.governanceengine.outTopic"
                        },
                        "configurationProperties": {
                            "producer": {
                                "bootstrap.servers": "localhost:9092"
                            },
                            "local.server.id": "f81bbe7a-2592-4afe-bd81-64dfb3bd7920",
                            "consumer": {
                                "bootstrap.servers": "localhost:9092"
                            }
                        }
                    }
                }
            ],
            "repositoryServicesConfig": {
                "class": "RepositoryServicesConfig",
                "auditLogConnections": [
                    {
                        "class": "Connection",
                        "headerVersion": 0,
                        "qualifiedName": "Console- default",
                        "displayName": "Console",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.repositoryservices.auditlogstore.console.ConsoleAuditLogStoreProvider"
                        },
                        "configurationProperties": {
                            "supportedSeverities": [
                                "Unknown",
                                "Information",
                                "Decision",
                                "Action",
                                "Error",
                                "Exception",
                                "Security",
                                "Startup",
                                "Shutdown",
                                "Asset",
                                "Cohort"
                            ]
                        }
                    }
                ],
                "localRepositoryConfig": {
                    "class": "LocalRepositoryConfig",
                    "metadataCollectionId": "be62f138-62fb-4ecf-85a6-ee497d8a4a90",
                    "localRepositoryMode": "OPEN_METADATA_NATIVE",
                    "localRepositoryLocalConnection": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Local KV XTDB Repository",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.repositoryservices.xtdb.repositoryconnector.XTDBOMRSRepositoryConnectorProvider"
                        },
                        "configurationProperties": {
                            "xtdbConfig": {
                                "xtdb.lucene/lucene-store": {
                                    "db-dir": "data/servers/test-store/repository/xtdb-kv/lucene"
                                },
                                "xtdb/tx-log": {
                                    "kv-store": {
                                        "db-dir": "data/servers/test-store/repository/xtdb-kv/rdb-tx",
                                        "xtdb/module": "xtdb.rocksdb/-\u003ekv-store"
                                    }
                                },
                                "xtdb/index-store": {
                                    "kv-store": {
                                        "db-dir": "data/servers/test-store/repository/xtdb-kv/rdb-index",
                                        "xtdb/module": "xtdb.rocksdb/-\u003ekv-store"
                                    }
                                },
                                "xtdb/document-store": {
                                    "kv-store": {
                                        "db-dir": "data/servers/test-store/repository/xtdb-kv/rdb-docs",
                                        "xtdb/module": "xtdb.rocksdb/-\u003ekv-store"
                                    }
                                }
                            }
                        }
                    },
                    "localRepositoryRemoteConnection": {
                        "class": "Connection",
                        "headerVersion": 0,
                        "displayName": "Local Repository Remote Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.adapters.repositoryservices.rest.repositoryconnector.OMRSRESTRepositoryConnectorProvider"
                        },
                        "endpoint": {
                            "class": "Endpoint",
                            "headerVersion": 0,
                            "address": "https://localhost:9443/servers/test-store"
                        }
                    },
                    "eventsToSaveRule": "ALL",
                    "eventsToSendRule": "ALL"
                },
                "enterpriseAccessConfig": {
                    "class": "EnterpriseAccessConfig",
                    "enterpriseMetadataCollectionName": "test-store Enterprise Metadata Collection",
                    "enterpriseMetadataCollectionId": "3d6db963-2c87-455d-b4de-d7862ba5fc9b",
                    "enterpriseOMRSTopicConnection": {
                        "class": "VirtualConnection",
                        "headerVersion": 0,
                        "displayName": "Enterprise OMRS Topic Connection",
                        "connectorType": {
                            "class": "ConnectorType",
                            "headerVersion": 0,
                            "connectorProviderClassName": "org.odpi.openmetadata.repositoryservices.connectors.omrstopic.OMRSTopicProvider"
                        },
                        "embeddedConnections": [
                            {
                                "class": "EmbeddedConnection",
                                "headerVersion": 0,
                                "position": 0,
                                "displayName": "Enterprise OMRS Events",
                                "embeddedConnection": {
                                    "class": "Connection",
                                    "headerVersion": 0,
                                    "displayName": "Kafka Event Bus Connection",
                                    "connectorType": {
                                        "class": "ConnectorType",
                                        "headerVersion": 0,
                                        "connectorProviderClassName": "org.odpi.openmetadata.adapters.eventbus.topic.inmemory.InMemoryOpenMetadataTopicProvider"
                                    },
                                    "endpoint": {
                                        "class": "Endpoint",
                                        "headerVersion": 0,
                                        "address": "test-store.openmetadata.repositoryservices.enterprise.test-store.OMRSTopic"
                                    },
                                    "configurationProperties": {
                                        "local.server.id": "f81bbe7a-2592-4afe-bd81-64dfb3bd7920",
                                        "eventDirection": "inOut"
                                    }
                                }
                            }
                        ]
                    },
                    "enterpriseOMRSTopicProtocolVersion": "V1"
                }
            }
        }

        try:
            p_client = Platform(server_name, self.good_platform1_url, self.good_user_1)
            p_client.activate_server_supplied_config(config_body, server)
            print(f"\n\n\tServer {server_name} now configured and activated")
            assert True
        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_get_active_server_instance_status(self, server: str = good_server_1):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_instance_status()
            if type(response) is str:
                print("Server instance status indicates: " + response)
            else:
                print (f"\n\n\tActive server status: {json.dumps(response, indent=4)}")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_is_server_known(self, server:str = good_server_2):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.is_server_known(server)
            print(f"\n\n\tis_server_known() for server {server} reports {response}")
            assert (response is True) or (response is False), "Exception happened?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_is_server_configured(self, server:str= good_server_3):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.is_server_configured(server)
            print(f"\n\n\tis_server_configured() for server {server} reports {response}")
            assert (response is True) or (response is False), "Exception happened?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"
        finally:
            p_client.close_session()

    # todo: does this exist?
    # def test_get_active_service_list_for_server(self, server: str = good_server_2):
    #     try:
    #         p_client = Platform(server, self.good_platform1_url, self.good_user_1, )
    #
    #         response = p_client.get_active_service_list_for_server(server)
    #         print(f"\n\n\tActive Service list for server {server} is {json.dumps(response, indent=4)}")
    #         assert len(response) >= 0, "Exception?"
    #
    #     except (InvalidParameterException, PropertyServerException) as e:
    #         print_exception_response(e)
    #         assert e.related_http_code != "200", "Invalid parameters"

    def test_get_active_server_list(self, server: str = good_server_2):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_list()
            print(f"\n\n\tThe active servers are: {response}")
            assert len(response) > 0, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_shutdown_all_servers(self):
        try:
            server = self.good_server_1
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.shutdown_all_servers()
            print(f"\n\n\tAll servers have been shutdown")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_check_server_active(self, server: str = good_server_3):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.check_server_active(server)
            print(f"\n\nserver {server} active state is {str(response)}")
            assert response in (True, False), "Bad Response"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_activate_server_if_down(self):
        try:
            server = self.good_server_3
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)

            response = p_client.activate_server_if_down(server, verbose=True)
            print(f"\n\n\t  activation success was {response}")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"


    def test_activate_servers_on_platform(self, server: str = good_server_2):
        server_name = server
        with Platform(server_name, self.good_platform1_url, self.good_user_1) as p_client:
            server_list = p_client.get_known_servers()
            print(f"\n\n\tKnown servers on the platform are: {server_list}")

            print(f"\n\tTrying to activate {server_list}")
            response = p_client.activate_servers_on_platform(server_list, verbose=True)
            print(f"\n\n\t\tactivate_servers_on_platform: success = {response}")
            if response is False:
                print("\n\t\tCheck that all servers are configured")
            known_servers = p_client.get_known_servers()
            print(f"\n\n\tKnown servers on the platform are: {known_servers}")
            assert True, "Issues encountered "

        if p_client.exc_type:
            print_exception_response(p_client.exc_val)
            assert False

    def test_activate_platform(self, server:str = good_server_3):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.activate_platform("laz", ["active-metadata-store","simple-metadata-store"])
            print(f"\n\n\tPlatform laz activated")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

        finally:
            p_client.close_session()

    def test_display_status(self, server:str = good_server_1):
        server_name = server

        table = Table(
            title=f"Server Status for Platform - {time.asctime()}",
            style = "black on grey66",
            header_style = "white on dark_blue",
            show_lines=True,
            expand=True
        )
        table.add_column("Known Server", width=20)
        table.add_column( "Status", width=10)
        table.add_column( "Service Name", width=20, no_wrap=True)
        table.add_column( "Service Status", width=10)
        try:
            with  ServerOps(server_name, self.good_platform1_url, self.good_user_1) as p_client:
                server_list = p_client.get_known_servers()
                live = Live(table, refresh_per_second=1)
                with live:
                    for server in server_list:
                        status = "Unknown"
                        if p_client.check_server_active(server):
                            status = "Active"
                        else:
                            status = "Inactive"
                        services = p_client.get_server_status(server)['serverStatus']['services']
                        for service in services:
                            service_name = service['serviceName']
                            service_status = service['serviceStatus']
                            table.add_row(server, status, service_name, service_status),

                    sleep(2)

        except(InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

        finally:
            p_client.close_session()



    def test_platform_services(self):
        server = self.good_server_2
        url = "https://127.0.0.1:9443"
        user_id = "garygeeke"

        # tp = TestPlatform()
        print("Running through a test scenario for the platform services module.")

        print("\n\n==========================================>Check what servers are active")
        self.test_get_active_server_list(server)

        print("\n\n==========================================>First we will shutdown and unregister all servers")
        self.test_shutdown_unregister_servers(server)

        print("\n\n==========================================>Check what servers are active")
        self.test_get_active_server_list(server)

        print("\n\n==========================================>Now we will look to see what servers are known")
        self.test_get_known_servers()

        print("\n\n==========================================>Start `simple-metadata-store`")
        self.test_activate_server_stored_config(server)

        print("\n\n==========================================>Check that simple-metadata-store is active")
        self.test_check_server_active()

        print("\n\n==========================================>Retrieve the server status for simple-metadata-store")
        self.test_get_active_server_instance_status()

        print("\n\n==========================================>Retrieve the active_server_instance_status for simple-metadata-store")
        self.test_get_active_server_instance_status()

        print("\n\n==========================================>Retrieve the active service list for simple-metadata-store")
        self.test_get_active_server_instance_status()

        print("\n\n==========================================>Start the 'active-metadata-store'")
        self.test_activate_server_stored_config("active-metadata-store")

        print("\n\n==========================================>Get the list of all active servers")
        self.test_get_active_server_list(server)

        print("\n\n==========================================>Stop the simple-metadata-store server")
        self.test_shutdown_server("simple-metadata-store")

        print("\n\n==========================================>Get the list of all active servers")
        self.test_get_active_server_list(server)

        print(f"\n\n==========================================>Activate {self.good_server_2} if down")
        self.test_activate_server_if_down()

        print("\n\n==========================================>Get the list of all active servers")
        self.test_get_active_server_list(server)

        print("\n\n==========================================>Activate known servers")
        self.test_activate_servers_on_platform()

        print("\n\n==========================================>All Tests Complete<======================================")


if __name__ == "__main__":
    pass
