"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Lineage Linker View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewRelationshipRequestBody,
    RelationshipBeanProperties,
)
from pyegeria.core.utils import dynamic_catch


class DataFlowProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["DataFlowProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    formula: Optional[str] = None
    formula_type: Optional[str] = None


class ControlFlowProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["ControlFlowProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    guard: Optional[str] = None
    mandatory_guard: Optional[bool] = None


class ProcessCallProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["ProcessCallProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    formula: Optional[str] = None
    formula_type: Optional[str] = None


class LineageMappingProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["LineageMappingProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None


class DataMappingProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["DataMappingProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    formula: Optional[str] = None
    formula_type: Optional[str] = None
    query_id: Optional[str] = None
    query: Optional[str] = None
    query_type: Optional[str] = None


class UltimateSourceProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["UltimateSourceProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None


class UltimateDestinationProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["UltimateDestinationProperties"], Field(alias="class")]
    isc_qualified_name: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None


class LineageLinker(ServerClient):
    """
    Client for the Lineage Linker View Service.

    The Lineage Linker View Service provides methods to manage lineage relationships.

    Attributes
    ----------
    view_server : str
        The name of the View Server to use.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method.
    user_pwd : str
        The password associated with the user_id. Defaults to None.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.url_marker = "lineage-linker"

    @dynamic_catch
    async def _async_link_lineage(
        self,
        element_one_guid: str,
        relationship_type_name: str,
        element_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> str:
        """Create a lineage relationship between two elements. Async version.

        Parameters
        ----------
        element_one_guid : str
            The unique identifier of the element at end one.
        relationship_type_name : str
            The name of the lineage relationship type (e.g., ControlFlow, ProcessCall, LineageMapping, etc.).
        element_two_guid : str
            The unique identifier of the element at end two.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        str
            The unique identifier of the newly created relationship.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body (for LineageMapping):
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class" : "LineageMappingProperties",
            "iscQualifiedName": "add qualifiedName of information supply chain here",
            "label": "add label here",
            "description": "add description here"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/lineage-linker/elements/{element_one_guid}/{relationship_type_name}/{element_two_guid}/attach"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid")

    def link_lineage(
        self,
        element_one_guid: str,
        relationship_type_name: str,
        element_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> str:
        """Create a lineage relationship between two elements.

        Parameters
        ----------
        element_one_guid : str
            The unique identifier of the element at end one.
        relationship_type_name : str
            The name of the lineage relationship type (e.g., ControlFlow, ProcessCall, LineageMapping, etc.).
        element_two_guid : str
            The unique identifier of the element at end two.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        str
            The unique identifier of the newly created relationship.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body (for LineageMapping):
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class" : "LineageMappingProperties",
            "iscQualifiedName": "add qualifiedName of information supply chain here",
            "label": "add label here",
            "description": "add description here"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_link_lineage(element_one_guid, relationship_type_name, element_two_guid, body)
        )

    @dynamic_catch
    async def _async_link_data_flow(
        self,
        element_one_guid: str,
        relationship_type_name: str,
        element_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> str:
        """Create a data flow relationship between two elements. Async version.

        Parameters
        ----------
        element_one_guid : str
            The unique identifier of the element at end one.
        relationship_type_name : str
            The name of the data flow relationship type.
        element_two_guid : str
            The unique identifier of the element at end two.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        str
            The unique identifier of the newly created relationship.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class" : "DataFlowProperties",
            "iscQualifiedName": "add qualifiedName of information supply chain here",
            "label": "add label here",
            "description": "add description here",
            "formula": "add formula here"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/lineage-linker/from-elements/{element_one_guid}/via/{relationship_type_name}/to-elements/{element_two_guid}/attach"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid")

    def link_data_flow(
        self,
        element_one_guid: str,
        relationship_type_name: str,
        element_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> str:
        """Create a data flow relationship between two elements.

        Parameters
        ----------
        element_one_guid : str
            The unique identifier of the element at end one.
        relationship_type_name : str
            The name of the data flow relationship type.
        element_two_guid : str
            The unique identifier of the element at end two.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        str
            The unique identifier of the newly created relationship.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class" : "DataFlowProperties",
            "iscQualifiedName": "add qualifiedName of information supply chain here",
            "label": "add label here",
            "description": "add description here",
            "formula": "add formula here"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_link_data_flow(element_one_guid, relationship_type_name, element_two_guid, body)
        )
