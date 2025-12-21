"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Digital Business OMVS module.

The Digital Business OMVS provides APIs for managing business capabilities and their
relationships to digital resources.
"""

import asyncio
from typing import Optional

from pyegeria._server_client import ServerClient
from pyegeria._exceptions import PyegeriaInvalidParameterException
from pyegeria._globals import NO_GUID_RETURNED
from pyegeria.config import settings as app_settings
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    NewClassificationRequestBody,
    DeleteClassificationRequestBody
)
from pyegeria.utils import dynamic_catch, body_slimmer
from loguru import logger

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier


class DigitalBusiness(ServerClient):
    """
    Manage business capabilities and their digital support relationships.

    This client provides methods to link business capabilities with their dependencies
    and digital support elements, as well as manage business significance classifications.

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
    link_business_capability_dependency(business_capability_guid, supporting_capability_guid, body)
        Link dependent business capabilities.
    detach_business_capability_dependency(business_capability_guid, supporting_capability_guid, body)
        Detach dependent business capabilities.
    link_digital_support(business_capability_guid, element_guid, body)
        Attach a business capability to an element that provides digital support.
    detach_digital_support(business_capability_guid, element_guid, body)
        Detach a business capability from digital support.
    set_business_significant(element_guid, body)
        Classify an element as business significant.
    clear_business_significance(element_guid, body)
        Remove the business significant classification.
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
        self.digital_business_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/digital-business"
        )
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    def _prepare_body(self, body: Optional[dict | NewRelationshipRequestBody | DeleteRelationshipRequestBody |
                                           NewClassificationRequestBody | DeleteClassificationRequestBody]) -> dict:
        """Convert Pydantic models to dict and slim the body."""
        if body is None:
            return {}
        if isinstance(body, dict):
            return body_slimmer(body)
        # It's a Pydantic model
        return body_slimmer(body.model_dump(mode='json', by_alias=True, exclude_none=True))

    #
    # Business Capability Dependency Management
    #

    @dynamic_catch
    async def _async_link_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link dependent business capabilities. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability that depends on another.
        supporting_capability_guid : str
            The GUID of the supporting business capability.
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
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/dependencies/{supporting_capability_guid}/attach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def link_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link dependent business capabilities. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability that depends on another.
        supporting_capability_guid : str
            The GUID of the supporting business capability.
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
            self._async_link_business_capability_dependency(
                business_capability_guid, supporting_capability_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach dependent business capabilities. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        supporting_capability_guid : str
            The GUID of the supporting business capability to detach.
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
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/dependencies/{supporting_capability_guid}/detach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def detach_business_capability_dependency(
        self,
        business_capability_guid: str,
        supporting_capability_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach dependent business capabilities. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        supporting_capability_guid : str
            The GUID of the supporting business capability to detach.
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
            self._async_detach_business_capability_dependency(
                business_capability_guid, supporting_capability_guid, body
            )
        )

    #
    # Digital Support Management
    #

    @dynamic_catch
    async def _async_link_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a business capability to an element that provides digital support. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the element providing digital support.
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
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/digital-support/{element_guid}/attach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def link_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a business capability to an element that provides digital support. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the element providing digital support.
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
            self._async_link_digital_support(business_capability_guid, element_guid, body)
        )

    @dynamic_catch
    async def _async_detach_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a business capability from digital support. Async version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the digital support element to detach.
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
            f"{self.digital_business_command_root}/business-capabilities/"
            f"{business_capability_guid}/digital-support/{element_guid}/detach"
        )
        await self._async_make_request("POST", url, self._prepare_body(body))

    def detach_digital_support(
        self,
        business_capability_guid: str,
        element_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a business capability from digital support. Sync version.

        Parameters
        ----------
        business_capability_guid : str
            The GUID of the business capability.
        element_guid : str
            The GUID of the digital support element to detach.
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
            self._async_detach_digital_support(business_capability_guid, element_guid, body)
        )

    #
    # Business Significance Classification
    #

    @dynamic_catch
    async def _async_set_business_significant(
        self,
        element_guid: str,
        body: Optional[dict | NewClassificationRequestBody] = None,
    ) -> None:
        """Classify an element as business significant. Async version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to classify.
        body : dict | NewClassificationRequestBody, optional
            Request body containing classification properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.digital_business_command_root}/elements/{element_guid}/business-significant"
        await self._async_make_request("POST", url, self._prepare_body(body))

    def set_business_significant(
        self,
        element_guid: str,
        body: Optional[dict | NewClassificationRequestBody] = None,
    ) -> None:
        """Classify an element as business significant. Sync version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to classify.
        body : dict | NewClassificationRequestBody, optional
            Request body containing classification properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_set_business_significant(element_guid, body))

    @dynamic_catch
    async def _async_clear_business_significance(
        self,
        element_guid: str,
        body: Optional[dict | DeleteClassificationRequestBody] = None,
    ) -> None:
        """Remove the business significant classification. Async version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to declassify.
        body : dict | DeleteClassificationRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        url = f"{self.digital_business_command_root}/elements/{element_guid}/business-significant/remove"
        await self._async_make_request("POST", url, self._prepare_body(body))

    def clear_business_significance(
        self,
        element_guid: str,
        body: Optional[dict | DeleteClassificationRequestBody] = None,
    ) -> None:
        """Remove the business significant classification. Sync version.

        Parameters
        ----------
        element_guid : str
            The GUID of the element to declassify.
        body : dict | DeleteClassificationRequestBody, optional
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
        loop.run_until_complete(self._async_clear_business_significance(element_guid, body))