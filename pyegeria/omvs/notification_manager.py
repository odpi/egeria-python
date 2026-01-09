"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Notification Manager OMVS module.

The Notification Manager OMVS provides APIs for managing notification types and their
relationships to monitored resources and subscribers.
"""

import asyncio
from typing import Optional

from pyegeria.core._server_client import ServerClient
from pyegeria.core.config import settings as app_settings
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from pyegeria.core.utils import dynamic_catch, body_slimmer

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier


class NotificationManager(ServerClient):
    """
    Manage notification types and their relationships to monitored resources and subscribers.

    This client provides methods to link notification types with monitored resources
    and notification subscribers.

    Attributes
    ----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method - this sets a default optionally
        used by the methods when the user doesn't pass the user_id on a method call.
    user_pwd : str, optional
        The password associated with the user_id. Defaults to None.
    token : str, optional
        An optional bearer token for authentication.

    Methods
    -------
    link_monitored_resource(notification_type_guid, monitored_resource_guid, body)
        Attach a monitored resource to a notification type.
    detach_monitored_resource(notification_type_guid, monitored_resource_guid, body)
        Detach a monitored resource from a notification type.
    link_notification_subscriber(notification_type_guid, subscriber_guid, body)
        Attach a subscriber to a notification type.
    detach_notification_subscriber(notification_type_guid, subscriber_guid, body)
        Detach a subscriber from a notification type.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.notification_manager_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/notification-manager"
        )
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    def _prepare_body(self, body: Optional[dict | NewRelationshipRequestBody | DeleteRelationshipRequestBody]) -> dict:
        """Convert Pydantic models to dict and slim the body."""
        if body is None:
            return {}
        if isinstance(body, dict):
            return body_slimmer(body)
        # It's a Pydantic model
        return body_slimmer(body.model_dump(mode='json', by_alias=True, exclude_none=True))

    #
    # Monitored Resource Management
    #

    @dynamic_catch
    async def _async_link_monitored_resource(
        self,
        notification_type_guid: str,
        monitored_resource_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a monitored resource to a notification type. Async version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        monitored_resource_guid : str
            The GUID of the monitored resource.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        ValidationError
            If the body does not conform to NewRelationshipRequestBody.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.
        """
        url = (
            f"{self.notification_manager_command_root}/notification-types/"
            f"{notification_type_guid}/monitored-resources/{monitored_resource_guid}/attach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def link_monitored_resource(
        self,
        notification_type_guid: str,
        monitored_resource_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a monitored resource to a notification type. Sync version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        monitored_resource_guid : str
            The GUID of the monitored resource.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_monitored_resource(
                notification_type_guid, monitored_resource_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_monitored_resource(
        self,
        notification_type_guid: str,
        monitored_resource_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a monitored resource from a notification type. Async version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        monitored_resource_guid : str
            The GUID of the monitored resource to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = (
            f"{self.notification_manager_command_root}/notification-types/"
            f"{notification_type_guid}/monitored-resources/{monitored_resource_guid}/detach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def detach_monitored_resource(
        self,
        notification_type_guid: str,
        monitored_resource_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a monitored resource from a notification type. Sync version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        monitored_resource_guid : str
            The GUID of the monitored resource to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_monitored_resource(
                notification_type_guid, monitored_resource_guid, body
            )
        )

    #
    # Notification Subscriber Management
    #

    @dynamic_catch
    async def _async_link_notification_subscriber(
        self,
        notification_type_guid: str,
        subscriber_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a subscriber to a notification type. Async version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        subscriber_guid : str
            The GUID of the subscriber.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = (
            f"{self.notification_manager_command_root}/notification-types/"
            f"{notification_type_guid}/notification-subscribers/{subscriber_guid}/attach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def link_notification_subscriber(
        self,
        notification_type_guid: str,
        subscriber_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a subscriber to a notification type. Sync version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        subscriber_guid : str
            The GUID of the subscriber.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_notification_subscriber(
                notification_type_guid, subscriber_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_notification_subscriber(
        self,
        notification_type_guid: str,
        subscriber_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a subscriber from a notification type. Async version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        subscriber_guid : str
            The GUID of the subscriber to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = (
            f"{self.notification_manager_command_root}/notification-types/"
            f"{notification_type_guid}/notification-subscribers/{subscriber_guid}/detach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def detach_notification_subscriber(
        self,
        notification_type_guid: str,
        subscriber_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a subscriber from a notification type. Sync version.

        Parameters
        ----------
        notification_type_guid : str
            The GUID of the notification type.
        subscriber_guid : str
            The GUID of the subscriber to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_notification_subscriber(
                notification_type_guid, subscriber_guid, body
            )
        )