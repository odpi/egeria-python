"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module tests the NotificationManager class and methods

A running Egeria environment is needed to run these tests.
"""
import time
from datetime import datetime

from rich import print
from rich.console import Console
from pyegeria.omvs.notification_manager import NotificationManager
from pyegeria.omvs.actor_manager import ActorManager
from pyegeria.omvs.collection_manager import CollectionManager
from pyegeria.core.logging_configuration import config_logging, init_logging
from pyegeria.core._exceptions import (
    PyegeriaInvalidParameterException,
    PyegeriaConnectionException,
    PyegeriaClientException,
    PyegeriaAPIException,
    PyegeriaUnknownException,
    print_basic_exception,
    print_validation_error,
)
from pydantic import ValidationError
from pyegeria.models import (
    NewElementRequestBody,
    NewRelationshipRequestBody,
)

disable_ssl_warnings = True
console = Console(width=250)

config_logging()
init_logging(True)

VIEW_SERVER = "view-server"
PLATFORM_URL = "https://localhost:9443"
USER_ID = "peterprofile"
USER_PWD = "secret"


class TestNotificationManager:
    good_platform1_url = PLATFORM_URL
    good_user_1 = USER_ID
    good_user_2 = "peterprofile"
    good_server_1 = VIEW_SERVER
    good_view_server_1 = VIEW_SERVER

    def _unique_qname(self, prefix: str = "NotificationTest") -> str:
        ts = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"{prefix}::{ts}"

    def test_link_monitored_resource(self):
        """Test linking a monitored resource to a notification type"""
        try:
            nm_client = NotificationManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            nm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create collections to act as notification type and monitored resource
            coll_client = CollectionManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            coll_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create notification type collection
            qname1 = self._unique_qname("NotificationType")
            notification_type_guid = coll_client.create_collection(
                display_name="Test Notification Type",
                description="Test notification type collection",
                collection_type="NotificationType",
                is_own_anchor=True,
            )
            print(f"Created notification type: {notification_type_guid}")

            # Create monitored resource collection
            qname2 = self._unique_qname("MonitoredResource")
            monitored_resource_guid = coll_client.create_collection(
                display_name="Test Monitored Resource",
                description="Test monitored resource collection",
                collection_type="MonitoredResource",
                is_own_anchor=True,
            )
            print(f"Created monitored resource: {monitored_resource_guid}")

            # Link monitored resource
            link_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "MonitoredResourceProperties",
                    "label": "Test Monitored Resource",
                    "description": "Test monitored resource relationship",
                },
            )
            start_time = time.perf_counter()
            nm_client.link_monitored_resource(
                notification_type_guid, monitored_resource_guid, body=link_body
            )
            duration = time.perf_counter() - start_time
            print(f"Linked monitored resource in {duration} seconds")

            # Detach monitored resource
            start_time = time.perf_counter()
            nm_client.detach_monitored_resource(
                notification_type_guid, monitored_resource_guid
            )
            duration = time.perf_counter() - start_time
            print(f"Detached monitored resource in {duration} seconds")

            # Cleanup
            coll_client.delete_collection(notification_type_guid)
            coll_client.delete_collection(monitored_resource_guid)
            coll_client.close_session()

            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            nm_client.close_session()

    def test_link_notification_subscriber(self):
        """Test linking a notification subscriber to a notification type"""
        try:
            nm_client = NotificationManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            nm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create collection for notification type
            coll_client = CollectionManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            coll_client.create_egeria_bearer_token(self.good_user_1, "secret")

            qname1 = self._unique_qname("NotificationTypeSubscriber")
            notification_type_guid = coll_client.create_collection(
                display_name="Test Notification Type for Subscriber",
                description="Test notification type for subscriber testing",
                collection_type="NotificationType",
                is_own_anchor=True,
            )
            print(f"Created notification type: {notification_type_guid}")

            # Create actor profile for subscriber
            actor_client = ActorManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            actor_client.create_egeria_bearer_token(self.good_user_1, "secret")

            qname2 = self._unique_qname("Subscriber")
            subscriber_guid = actor_client.create_actor_profile(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname2,
                        "name": "Test Subscriber",
                        "description": "Test subscriber actor profile",
                    },
                )
            )
            print(f"Created subscriber: {subscriber_guid}")

            # Link subscriber
            link_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "MonitoredResourceProperties",
                    "label": "Test Subscriber",
                    "description": "Test subscriber relationship",
                },
            )
            start_time = time.perf_counter()
            nm_client.link_notification_subscriber(
                notification_type_guid, subscriber_guid, body=link_body
            )
            duration = time.perf_counter() - start_time
            print(f"Linked notification subscriber in {duration} seconds")

            # Detach subscriber
            start_time = time.perf_counter()
            nm_client.detach_notification_subscriber(notification_type_guid, subscriber_guid)
            duration = time.perf_counter() - start_time
            print(f"Detached notification subscriber in {duration} seconds")

            # Cleanup
            coll_client.delete_collection(notification_type_guid)
            actor_client.delete_actor_profile(subscriber_guid)
            coll_client.close_session()
            actor_client.close_session()

            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            nm_client.close_session()

    def test_complete_notification_setup(self):
        """Test complete notification setup with resource and subscriber"""
        try:
            nm_client = NotificationManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            nm_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create collections
            coll_client = CollectionManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            coll_client.create_egeria_bearer_token(self.good_user_1, "secret")

            # Create notification type
            notification_type_guid = coll_client.create_collection(
                display_name="Complete Notification Type",
                description="Complete notification type for testing",
                collection_type="NotificationType",
                is_own_anchor=True,
            )
            print(f"Created notification type: {notification_type_guid}")

            # Create monitored resource
            monitored_resource_guid = coll_client.create_collection(
                display_name="Complete Monitored Resource",
                description="Complete monitored resource for testing",
                collection_type="MonitoredResource",
                is_own_anchor=True,
            )
            print(f"Created monitored resource: {monitored_resource_guid}")

            # Create subscriber
            actor_client = ActorManager(
                self.good_view_server_1,
                self.good_platform1_url,
                user_id=self.good_user_1,
                user_pwd="secret",
            )
            actor_client.create_egeria_bearer_token(self.good_user_1, "secret")

            qname = self._unique_qname("CompleteSubscriber")
            subscriber_guid = actor_client.create_actor_profile(
                body=NewElementRequestBody(
                    class_="NewElementRequestBody",
                    properties={
                        "qualifiedName": qname,
                        "name": "Complete Subscriber",
                        "description": "Complete subscriber for testing",
                    },
                )
            )
            print(f"Created subscriber: {subscriber_guid}")

            # Link monitored resource
            resource_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "MonitoredResourceProperties",
                    "label": "Complete Test Resource",
                    "description": "Complete test monitored resource",
                },
            )
            nm_client.link_monitored_resource(
                notification_type_guid, monitored_resource_guid, body=resource_body
            )
            print("Linked monitored resource")

            # Link subscriber
            subscriber_body = NewRelationshipRequestBody(
                class_="NewRelationshipRequestBody",
                properties={
                    "class": "MonitoredResourceProperties",
                    "label": "Complete Test Subscriber",
                    "description": "Complete test subscriber",
                },
            )
            nm_client.link_notification_subscriber(
                notification_type_guid, subscriber_guid, body=subscriber_body
            )
            print("Linked notification subscriber")

            # Detach both
            nm_client.detach_monitored_resource(notification_type_guid, monitored_resource_guid)
            print("Detached monitored resource")

            nm_client.detach_notification_subscriber(notification_type_guid, subscriber_guid)
            print("Detached notification subscriber")

            # Cleanup
            coll_client.delete_collection(notification_type_guid)
            coll_client.delete_collection(monitored_resource_guid)
            actor_client.delete_actor_profile(subscriber_guid)
            coll_client.close_session()
            actor_client.close_session()

            assert True

        except (
            PyegeriaInvalidParameterException,
            PyegeriaConnectionException,
            PyegeriaClientException,
            PyegeriaAPIException,
            PyegeriaUnknownException,
        ) as e:
            print_basic_exception(e)
            assert False, "Invalid request"
        except ValidationError as e:
            print_validation_error(e)
            assert False, "Validation error"
        finally:
            nm_client.close_session()


if __name__ == "__main__":
    print("Manual test run")