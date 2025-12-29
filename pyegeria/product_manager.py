"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Product Manager OMVS module.

The Product Manager OMVS provides APIs for managing digital products and their
relationships, including product dependencies and product managers.
"""

import asyncio
from typing import Optional

from pyegeria._server_client import ServerClient
from pyegeria._exceptions import PyegeriaInvalidParameterException
from pyegeria._globals import NO_GUID_RETURNED
from pyegeria.config import settings as app_settings
from pyegeria.models import (
    NewElementRequestBody,
    UpdateElementRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from pyegeria.utils import dynamic_catch, body_slimmer
from loguru import logger

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier


class ProductManager(ServerClient):
    """
    Manage digital products and their relationships.

    This client provides methods to create, update, and manage digital products,
    including linking product dependencies and product manager roles.

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
    create_digital_product(body)
        Create a new digital product collection.
    update_digital_product(digital_product_guid, body)
        Update the properties of a digital product.
    link_digital_product_dependency(consumer_product_guid, consumed_product_guid, body)
        Link two dependent digital products.
    detach_digital_product_dependency(consumer_product_guid, consumed_product_guid, body)
        Unlink dependent digital products.
    link_product_manager(digital_product_guid, product_manager_role_guid, body)
        Attach a product manager role to a digital product.
    detach_product_manager(digital_product_guid, product_manager_role_guid, body)
        Detach a product manager from a digital product.
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
        self.product_manager_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager"
        )
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)

    def _prepare_body(self, body: Optional[dict | NewElementRequestBody | UpdateElementRequestBody | 
                                           NewRelationshipRequestBody | DeleteRelationshipRequestBody]) -> dict:
        """Convert Pydantic models to dict and slim the body."""
        if body is None:
            return {}
        if isinstance(body, dict):
            return body_slimmer(body)
        # It's a Pydantic model
        return body_slimmer(body.model_dump(mode='json', by_alias=True, exclude_none=True))

    #
    # Digital Product Management
    #

    @dynamic_catch
    async def _async_create_digital_product(
        self,
        body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create a new digital product collection. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody, optional
            Request body containing digital product properties.

        Returns
        -------
        str
            The GUID of the created digital product.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        ValidationError
            If the body does not conform to NewElementRequestBody.
        PyegeriaNotAuthorizedException
            If the user is not authorized for the requested action.

        Notes
        -----
            Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
            be valid dates if specified, otherwise you will get a 400 error response.

            JSON Structure looks like:
            {
              "class" : "NewElementRequestBody",
              "isOwnAnchor" : true,
              "anchorScopeGUID" : "optional GUID of search scope",
              "parentGUID" : "xxx",
              "parentRelationshipTypeName" : "CollectionMembership",
              "parentAtEnd1": true,
              "properties": {
                "class" : "DigitalProductProperties",
                "qualifiedName": "DigitalProduct::Add product name here",
                "name" : "Product contents",
                "description" : "Add description of product and its expected usage here",
                "identifier" : "Add product identifier here",
                "productName" : "Add product name here",
                "category" : "Periodic Delta",
                "maturity" : "Add valid value here",
                "serviceLife" : "Add the estimated lifetime of the product",
                "introductionDate" : "date",
                "nextVersionDate": "date",
                "withdrawDate": "date",
                "currentVersion": "V0.1",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
            }

            The valid values for Status are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
            UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
            OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
            default to ACTIVE.
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/product-manager/collections"
        return await self._async_create_element_body_request(url, ["DigitalProductProperties"], body)

        # response = await self._async_make_request("POST", url, self._prepare_body(body))
        # return response.json().get("guid", NO_GUID_RETURNED) if response else NO_GUID_RETURNED

    def create_digital_product(
        self,
        body: Optional[dict | NewElementRequestBody] = None,
    ) -> str:
        """Create a new digital product collection. Sync version.

        Parameters
        ----------
        body : dict | NewElementRequestBody, optional
            Request body containing digital product properties.

        Returns
        -------
        str
            The GUID of the created digital product.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_digital_product(body))

    @dynamic_catch
    async def _async_update_digital_product(
        self,
        digital_product_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product to update.
        body : dict | UpdateElementRequestBody, optional
            Request body containing updated properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes:
        -----
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct::Add product name here",
            "name" : "Product contents",
            "description" : "Add description of product and its expected usage here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add product identifier here",
            "productName" : "Add product name here",
            "category" : "Periodic Delta",
            "maturity" : "Add valid value here",
            "serviceLife" : "Add the estimated lifetime of the product",
            "introductionDate" : "date",
            "nextVersionDate": "date",
            "withdrawDate": "date",
            "currentVersion": "V0.1",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.product_manager_command_root}/collections/{digital_product_guid}/update"
        # await self._async_make_request("POST", url, self._prepare_body(body))
        await self._async_update_element_body_request(url, ["DigitalProductProperties"], body)

    def update_digital_product(
        self,
        digital_product_guid: str,
        body: Optional[dict | UpdateElementRequestBody] = None,
    ) -> None:
        """Update the properties of a digital product. Sync version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product to update.
        body : dict | UpdateElementRequestBody, optional
            Request body containing updated properties.

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
            self._async_update_digital_product(digital_product_guid, body)
        )

    #
    # Digital Product Dependency Management
    #

    @dynamic_catch
    async def _async_link_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link two dependent digital products. Async version.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the digital product that consumes another.
        consumed_product_guid : str
            The GUID of the digital product being consumed.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        JSON Structure looks like:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "DigitalProductDependencyProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{consumer_product_guid}/product-dependencies/{consumed_product_guid}/attach"
        )
        # await self._async_make_request("POST", url, self._prepare_body(body))
        await self._async_new_relationship_request(url, ["DigitalProductDependencyProperties"], body)
        logger.info(f"Linked {consumed_product_guid} -> {consumer_product_guid}")

    def link_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Link two dependent digital products. Sync version.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the digital product that consumes another.
        consumed_product_guid : str
            The GUID of the digital product being consumed.
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
            self._async_link_digital_product_dependency(
                consumer_product_guid, consumed_product_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Unlink dependent digital products. Async version.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the consumer digital product.
        consumed_product_guid : str
            The GUID of the consumed digital product to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{consumer_product_guid}/product-dependencies/{consumed_product_guid}/detach"
        )
        # await self._async_make_request("POST", url, self._prepare_body(body))
        await self._async_delete_relationship_request(url, body)
        logger.info(f"Detached digital product dependency {consumer_product_guid} -> {consumed_product_guid}")

    def detach_digital_product_dependency(
        self,
        consumer_product_guid: str,
        consumed_product_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Unlink dependent digital products. Sync version.

        Parameters
        ----------
        consumer_product_guid : str
            The GUID of the consumer digital product.
        consumed_product_guid : str
            The GUID of the consumed digital product to detach.
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
            self._async_detach_digital_product_dependency(
                consumer_product_guid, consumed_product_guid, body
            )
        )

    #
    # Product Manager Role Management
    #

    @dynamic_catch
    async def _async_link_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a product manager role to a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role.
        body : dict | NewRelationshipRequestBody, optional
            Request body containing relationship properties.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "NewRelationshipRequestBody",
          "properties": {
              "assignmentType": "Add type here",
              "description": "Add assignment description here"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{digital_product_guid}/product-managers/{product_manager_role_guid}/attach"
        )
        # await self._async_make_request("POST", url, self._prepare_body(body))
        await self._async_new_relationship_request(url, ["AssignmentScopeProperties"], body)
        logger.info(f"Attached digital product manager {digital_product_guid} -> {product_manager_role_guid}")

    def link_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """Attach a product manager role to a digital product. Sync version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role.
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
            self._async_link_product_manager(
                digital_product_guid, product_manager_role_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a product manager from a digital product. Async version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role to detach.
        body : dict | DeleteRelationshipRequestBody, optional
            Request body for deletion.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        JSON Structure looks like:
        {
          "class": "DeleteRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.product_manager_command_root}/digital-products/"
            f"{digital_product_guid}/product-managers/{product_manager_role_guid}/detach"
        )
        # await self._async_make_request("POST", url, self._prepare_body(body))
        await self._async_delete_relationship_request(url, body)
        logger.info(f"Detached digital product manager {digital_product_guid} -> {product_manager_role_guid}")

    def detach_product_manager(
        self,
        digital_product_guid: str,
        product_manager_role_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """Detach a product manager from a digital product. Sync version.

        Parameters
        ----------
        digital_product_guid : str
            The GUID of the digital product.
        product_manager_role_guid : str
            The GUID of the product manager role to detach.
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
            self._async_detach_product_manager(
                digital_product_guid, product_manager_role_guid, body
            )
        )