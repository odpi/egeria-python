"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.


This file contains a set of test routines to test the platform_services of the Egeria python client.
The routines assume that pytest is being used as the test tool and framework.

A running Egeria environment is needed to run these tests. A set of platform, server and user variables are
created local to the TestPlatform class to hold the set of values to be used for testing. The default values have
been configured based on running the Egeria Lab Helm chart on a local kubernetes cluster and setting the portmap.
However, the tests are not dependent on this configuration. It should, however, be noted that the tests are currently
order sensitive - in other words if you delete all the servers the subsequent tests that expect the servers to be
available may fail..

"""

import pytest
import json

from contextlib import nullcontext as does_not_raise
disable_ssl_warnings = True

from pyegeria._exceptions import (
    InvalidParameterException,
    PropertyServerException,
    UserNotAuthorizedException,
    print_exception_response,
)

from pyegeria.platform_services import Platform

class TestPlatform:
    good_platform1_url = "https://127.0.0.1:9443"
    good_platform2_url = "https://egeria.pdr-associates.com:7443"
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
    good_server_3 = "fluffy"
    good_server_4 = "fluffy_kv"
    bad_server_1 = "coco"
    bad_server_2 = ""

    @pytest.mark.parametrize(
        "server, url, user_id, exc_type, expectation",
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
                    "https://localhost:9443",
                    "garygeeke",
                    "InvalidParameterException",
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS1",
                    "https://127.0.0.1:9443",
                    "garygeeke",
                    None,
                    does_not_raise(),
            ),
            (
                    "cocoMDS2",
                    "https://127.0.0.1:9443",
                    "",
                    "InvalidParameterException",
                    pytest.raises(InvalidParameterException),
            ),
            (
                    "cocoMDS2",
                    "https://127.0.0.1:9443/open-metadata/admin-services/users/garygeeke/servers/active-metadata-store",
                    "meow",
                    "InvalidParameterException",
                    pytest.raises(InvalidParameterException),
            ),
            ("", "", "", "InvalidParameterException", pytest.raises(InvalidParameterException)),
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

    def test_shutdown_platform(self, server: str = good_server_2):
        try:
            p_client = Platform(server,self.good_platform1_url, self.good_user_1)
            p_client.shutdown_platform()
            print(f"\n\n\t Platform shutdown")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code is not "200", "Invalid parameters"

    def test_activate_server_stored_config(self, server: str = good_server_2):
        """
        Need to decide if its worth it to broaden out the test cases..for instance
        in this method if there is an exception - such as invalid server name
        then the test case fails because the response is used before set..

        """
        try:
            p_client = Platform(server,self.good_platform1_url, self.good_user_1)
            p_client.activate_server_stored_config(server)
            print(f"\n\n\t server {server} configured and activated successfully")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    def test_shutdown_server(self, server: str = good_server_2):
        try:
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.shutdown_server(server)
            print(f"\n\n\t server {server} was shut down successfully")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code == 404, "Invalid parameters"

    def test_get_known_servers(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_known_servers()
            print(f"\n\n\t response = {response}")
            assert len(response) > 0, "Empty server list"

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    def test_shutdown_unregister_servers(self):
        try:
            p_client = Platform(
                self.good_server_4, self.good_platform1_url, self.good_user_1
            )
            p_client.shutdown_unregister_servers()
            print(f"\n\n\t Servers on platform {p_client.platform_url} shutdown and unregistered")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    @pytest.mark.parametrize(
        "server, url, user_id, ex_type, expectation",
        [
            # (
            #     "meow",
            #     "https://google.com",
            #     "garygeeke",
            #     "InvalidParameterException",
            #     pytest.raises(InvalidParameterException),
            # ),
            # (
            #     "cocoMDS2",
            #     "https://localhost:9443",
            #     "garygeeke",
            #     "InvalidParameterException",
            #     pytest.raises(InvalidParameterException),
            # ),
            # (
            #     "cocoMDS1",
            #     "https://127.0.0.1:30081",
            #     "garygeeke",
            #     "InvalidParameterException",
            #     pytest.raises(InvalidParameterException),
            # ),
            # (
            #     "cocoMDS9",
            #     "https://127.0.0.1:9443",
            #     "garygeeke",
            #     "InvalidParameterException",
            #     pytest.raises(InvalidParameterException),
            # ),
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
        with expectation as excinfo:
            p_client = Platform(server, url, user_id)
            response = p_client.get_active_configuration(server)
            print(f"\n\n\tThe active configuration of {server} is \n{json.dumps(response, indent=4)}")
            assert True

        if excinfo:
            print_exception_response(excinfo.value)
            assert excinfo.typename is ex_type


    def test_activate_server_supplied_config(self):
        server = "test-store"
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
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            p_client.activate_server_supplied_config(config_body, server)
            print(f"\n\n\tServer {server} now configured and activated")
            assert True
        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    # def test_add_archive_files(self):
    #     # Todo - the base function doesn't seem to validate the file or to actually load? Check
    #     try:
    #         server = self.good_server_1
    #         p_client = Platform(server, self.good_platform2_url, self.good_user_1)
    #         response = p_client.add_archive_file("/Users/dwolfson/localGit/pdr/pyegeria/CocoGovernanceEngineDefinitionsArchive.json", server)
    #         print_rest_response(response)
    #         assert response.get("relatedHTTPCode") == 200, "Invalid URL or server"
    #
    #     except (InvalidParameterException, PropertyServerException) as e:
    #         print_exception_response(e)
    #         assert e.related_http_code != "404", "Invalid parameters"

    def test_load_archive_file(self):
        try:
            server = self.good_server_4
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            file_name = "content-packs/CocoSustainabilityArchive.omarchive"
            p_client.add_archive_file(file_name, server)
            print(f"Archive file: {file_name} was loaded successfully")
            assert True

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert False, "Invalid parameters"

    def test_get_active_server_instance_status(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_instance_status()
            print(f"\n\n\tActive server status: {json.dumps(response, indent =4)}")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "404", "Invalid parameters"

    def test_is_server_known(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.is_server_known(server)
            print(f"\n\n\tis_known() for server {server} reports {response}")
            assert (response is True) or (response is False), "Exception happened?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code == "200", "Invalid parameters"

    def test_get_active_service_list_for_server(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_service_list_for_server(server)
            print(f"\n\n\tActive Service list for server {server} is {json.dumps(response, indent=4)}")
            assert len(response) >= 0, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_server_status(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_server_status(server)
            print(f"\n\n\tStatus for server {server} is {response}")
            assert True

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_get_active_server_list(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.get_active_server_list()
            print(f"\n\n\tThe active servers are: {response}")
            assert len(response) > 0, "Exception?"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

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

    def test_check_server_active(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.check_server_active(server)
            print(f"\n\nserver {server} active state is {str(response)}")
            assert response in (True, False), "Bad Response"

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_activate_server_if_down_forced_dn(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            response = p_client.shutdown_server(server)
            print(f"\n\n\t The server was forced down with a response of: {response}")
            response = p_client.activate_server_if_down(server)
            print(f"\n\n\t  activation success was {response}")
            assert response, "Server not configured"

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_activate_server_if_down_forced_up(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            a_response = p_client.activate_server_stored_config(server)
            response = p_client.activate_server_if_down(server)
            print(f"\n\n\t  activation success was {response}")
            assert response, "Server not configured "

        except (InvalidParameterException, PropertyServerException, UserNotAuthorizedException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"

    def test_activate_servers_on_platform(self):
        try:
            server = self.good_server_2
            p_client = Platform(server, self.good_platform1_url, self.good_user_1)
            server_list = p_client.get_known_servers()
            print(f"\n\n\tServers on the platform are: {server_list}")
            assert server_list is not None, "No servers found?"

            response = p_client.activate_servers_on_platform(server_list)
            print(f"\n\n\t activate_servers_on_platform: success = {response}")
            assert response, "Issues encountered "

        except (InvalidParameterException, PropertyServerException) as e:
            print_exception_response(e)
            assert e.related_http_code != "200", "Invalid parameters"


