"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the Time Keeper View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewElementRequestBody,
    DeleteElementRequestBody,
    UpdateElementRequestBody,
    TemplateRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    FilterRequestBody,
    SearchStringRequestBody,
    GetRequestBody,
    ReferenceableProperties,
    RelationshipBeanProperties,
)
from pyegeria.view.output_formatter import (
    generate_output,
    populate_common_columns,
    overlay_additional_values,
)
from pyegeria.core.utils import dynamic_catch


class ContextEventProperties(ReferenceableProperties):
    class_: Annotated[Literal["ContextEventProperties"], Field(alias="class")]
    url: Optional[str] = None
    event_effect: Optional[str] = None
    planned_start_date: Optional[str] = None
    actual_start_date: Optional[str] = None
    planned_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    repeat_interval: Optional[int] = None
    planned_completion_date: Optional[str] = None
    actual_completion_date: Optional[str] = None
    reference_effective_from: Optional[str] = None
    reference_effective_to: Optional[str] = None


class DependentContextEventProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["DependentContextEventProperties"], Field(alias="class")]
    label: Optional[str] = None
    description: Optional[str] = None


class RelatedContextEventProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["RelatedContextEventProperties"], Field(alias="class")]
    label: Optional[str] = None
    description: Optional[str] = None
    status_identifier: Optional[int] = None
    confidence: Optional[int] = None
    steward: Optional[str] = None
    steward_type_name: Optional[str] = None
    steward_property_name: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class ContextEventEvidenceProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["ContextEventEvidenceProperties"], Field(alias="class")]
    label: Optional[str] = None
    description: Optional[str] = None


class ContextEventImpactProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["ContextEventImpactProperties"], Field(alias="class")]
    label: Optional[str] = None
    description: Optional[str] = None
    status_identifier: Optional[int] = None


class ContextEventForTimelineEffectsProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["ContextEventForTimelineEffectsProperties"], Field(alias="class")]
    label: Optional[str] = None
    description: Optional[str] = None
    status_identifier: Optional[int] = None


class TimeKeeper(ServerClient):
    """
    Client for the Time Keeper View Service.

    The Time Keeper View Service provides methods to manage context events.

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
        self.url_marker = "time-keeper"

    def _extract_context_event_properties(self, element: dict, columns_struct: dict) -> dict:
        col_data = populate_common_columns(element, columns_struct)
        props = element.get("properties", {})
        overlay_additional_values(col_data, props)
        return col_data

    def _generate_context_event_output(
        self,
        elements: dict | list[dict],
        filter: Optional[str],
        element_type_name: Optional[str],
        output_format: str = "DICT",
        report_spec: dict | str = None,
    ) -> str | list[dict]:
        return generate_output(
            elements,
            filter,
            element_type_name,
            output_format,
            self._extract_context_event_properties,
            None,
            report_spec,
        )

    @dynamic_catch
    async def _async_create_context_event(self, body: dict | NewElementRequestBody) -> str:
        """Create a context event. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The properties for the context event.

        Returns
        -------
        str
            The unique identifier of the newly created context event.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "properties": {
            "class" : "ContextEventProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "plannedStartDate" : "2024-01-01T00:00:00.000+00:00"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events"
        return await self._async_create_element_body_request(url, "ContextEventProperties", body)

    def create_context_event(self, body: dict | NewElementRequestBody) -> str:
        """Create a context event.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            The properties for the context event.

        Returns
        -------
        str
            The unique identifier of the newly created context event.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewElementRequestBody",
          "properties": {
            "class" : "ContextEventProperties",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "plannedStartDate" : "2024-01-01T00:00:00.000+00:00"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_context_event(body))

    @dynamic_catch
    async def _async_create_context_event_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a context event from a template. Async version.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            The properties for the new context event, including the template GUID.

        Returns
        -------
        str
            The unique identifier of the newly created context event.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "TemplateRequestBody",
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/from-template"
        return await self._async_create_element_body_request(url, "ContextEventProperties", body)

    def create_context_event_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a context event from a template.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            The properties for the new context event, including the template GUID.

        Returns
        -------
        str
            The unique identifier of the newly created context event.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "TemplateRequestBody",
          "templateGUID": "add guid here",
          "replacementProperties": {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_context_event_from_template(body))

    @dynamic_catch
    async def _async_update_context_event(
        self, context_event_guid: str, body: dict | UpdateElementRequestBody
    ) -> None:
        """Update a context event. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | UpdateElementRequestBody
            The properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ContextEventProperties",
            "displayName": "Updated Name"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/update"
        await self._async_update_element_body_request(url, body)

    def update_context_event(self, context_event_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """Update a context event.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | UpdateElementRequestBody
            The properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "UpdateElementRequestBody",
          "mergeUpdate": true,
          "properties": {
            "class" : "ContextEventProperties",
            "displayName": "Updated Name"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_context_event(context_event_guid, body))

    @dynamic_catch
    async def _async_delete_context_event(
        self, context_event_guid: str, body: dict | DeleteElementRequestBody
    ) -> None:
        """Delete a context event. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | DeleteElementRequestBody
            The request body for the delete operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteElementRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/delete"
        await self._async_delete_element_body_request(url, body)

    def delete_context_event(self, context_event_guid: str, body: dict | DeleteElementRequestBody) -> None:
        """Delete a context event.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | DeleteElementRequestBody
            The request body for the delete operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteElementRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_context_event(context_event_guid, body))

    @dynamic_catch
    async def _async_link_dependent_context_events(
        self,
        parent_context_event_guid: str,
        child_context_event_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link dependent context events. Async version.

        Parameters
        ----------
        parent_context_event_guid : str
            The unique identifier of the parent context event.
        child_context_event_guid : str
            The unique identifier of the child context event.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "DependentContextEventProperties",
            "label" : "Dependency",
            "description" : "Child event depends on parent event"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{parent_context_event_guid}/dependent-context-events/{child_context_event_guid}/attach"
        await self._async_create_related_elements_body_request(url, body)

    def link_dependent_context_events(
        self,
        parent_context_event_guid: str,
        child_context_event_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link dependent context events.

        Parameters
        ----------
        parent_context_event_guid : str
            The unique identifier of the parent context event.
        child_context_event_guid : str
            The unique identifier of the child context event.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "DependentContextEventProperties",
            "label" : "Dependency",
            "description" : "Child event depends on parent event"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_dependent_context_events(
                parent_context_event_guid, child_context_event_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_dependent_context_events(
        self,
        parent_context_event_guid: str,
        child_context_event_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach dependent context events. Async version.

        Parameters
        ----------
        parent_context_event_guid : str
            The unique identifier of the parent context event.
        child_context_event_guid : str
            The unique identifier of the child context event.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{parent_context_event_guid}/dependent-context-events/{child_context_event_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_dependent_context_events(
        self,
        parent_context_event_guid: str,
        child_context_event_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach dependent context events.

        Parameters
        ----------
        parent_context_event_guid : str
            The unique identifier of the parent context event.
        child_context_event_guid : str
            The unique identifier of the child context event.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_dependent_context_events(
                parent_context_event_guid, child_context_event_guid, body
            )
        )

    @dynamic_catch
    async def _async_link_related_context_events(
        self,
        context_event_one_guid: str,
        context_event_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link related context events. Async version.

        Parameters
        ----------
        context_event_one_guid : str
            The unique identifier of the first context event.
        context_event_two_guid : str
            The unique identifier of the second context event.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "RelatedContextEventProperties",
            "label" : "Related",
            "description" : "These events are related"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_one_guid}/related-context-events/{context_event_two_guid}/attach"
        await self._async_new_relationship_request(url, ['ContextEventEvidence'],body)

    def link_related_context_events(
        self,
        context_event_one_guid: str,
        context_event_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link related context events.

        Parameters
        ----------
        context_event_one_guid : str
            The unique identifier of the first context event.
        context_event_two_guid : str
            The unique identifier of the second context event.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "RelatedContextEventProperties",
            "label" : "Related",
            "description" : "These events are related"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_related_context_events(context_event_one_guid, context_event_two_guid, body)
        )

    @dynamic_catch
    async def _async_detach_related_context_events(
        self,
        context_event_one_guid: str,
        context_event_two_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach related context events. Async version.

        Parameters
        ----------
        context_event_one_guid : str
            The unique identifier of the first context event.
        context_event_two_guid : str
            The unique identifier of the second context event.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_one_guid}/related-context-events/{context_event_two_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_related_context_events(
        self,
        context_event_one_guid: str,
        context_event_two_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach related context events.

        Parameters
        ----------
        context_event_one_guid : str
            The unique identifier of the first context event.
        context_event_two_guid : str
            The unique identifier of the second context event.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_related_context_events(context_event_one_guid, context_event_two_guid, body)
        )

    @dynamic_catch
    async def _async_link_context_event_evidence(
        self, context_event_guid: str, evidence_guid: str, body: dict | NewRelationshipRequestBody
    ) -> None:
        """Link context event evidence. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        evidence_guid : str
            The unique identifier of the element providing evidence.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "ContextEventEvidenceProperties",
            "label" : "Evidence",
            "description" : "Evidence for context event"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/evidence/{evidence_guid}/attach"
        await self._async_new_relationship_request(url, body)

    def link_context_event_evidence(
        self, context_event_guid: str, evidence_guid: str, body: dict | NewRelationshipRequestBody
    ) -> None:
        """Link context event evidence.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        evidence_guid : str
            The unique identifier of the element providing evidence.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "ContextEventEvidenceProperties",
            "label" : "Evidence",
            "description" : "Evidence for context event"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_context_event_evidence(context_event_guid, evidence_guid, body)
        )

    @dynamic_catch
    async def _async_detach_context_event_evidence(
        self, context_event_guid: str, evidence_guid: str, body: dict | DeleteRelationshipRequestBody
    ) -> None:
        """Detach context event evidence. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        evidence_guid : str
            The unique identifier of the element providing evidence.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/evidence/{evidence_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_context_event_evidence(
        self, context_event_guid: str, evidence_guid: str, body: dict | DeleteRelationshipRequestBody
    ) -> None:
        """Detach context event evidence.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        evidence_guid : str
            The unique identifier of the element providing evidence.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_context_event_evidence(context_event_guid, evidence_guid, body)
        )

    @dynamic_catch
    async def _async_link_context_event_impact(
        self, context_event_guid: str, impacted_element_guid: str, body: dict | NewRelationshipRequestBody
    ) -> None:
        """Link context event impact. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        impacted_element_guid : str
            The unique identifier of the impacted element.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "ContextEventImpactProperties",
            "label" : "Impact",
            "description" : "Element impacted by context event"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/impacts/{impacted_element_guid}/attach"
        await self._async_new_relationship_request(url, ['ContextEventImpact'],body)

    def link_context_event_impact(
        self, context_event_guid: str, impacted_element_guid: str, body: dict | NewRelationshipRequestBody
    ) -> None:
        """Link context event impact.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        impacted_element_guid : str
            The unique identifier of the impacted element.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "ContextEventImpactProperties",
            "label" : "Impact",
            "description" : "Element impacted by context event"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_context_event_impact(context_event_guid, impacted_element_guid, body)
        )

    @dynamic_catch
    async def _async_detach_context_event_impact(
        self, context_event_guid: str, impacted_element_guid: str, body: dict | DeleteRelationshipRequestBody
    ) -> None:
        """Detach context event impact. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        impacted_element_guid : str
            The unique identifier of the impacted element.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/impacts/{impacted_element_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_context_event_impact(
        self, context_event_guid: str, impacted_element_guid: str, body: dict | DeleteRelationshipRequestBody
    ) -> None:
        """Detach context event impact.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        impacted_element_guid : str
            The unique identifier of the impacted element.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_context_event_impact(context_event_guid, impacted_element_guid, body)
        )

    @dynamic_catch
    async def _async_link_context_event_timeline_effect(
        self,
        timeline_affected_element_guid: str,
        context_event_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link context event timeline effect. Async version.

        Parameters
        ----------
        timeline_affected_element_guid : str
            The unique identifier of the element affected by the timeline.
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "ContextEventForTimelineEffectsProperties",
            "label" : "Timeline Effect",
            "description" : "Element data affected by context event"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/elements/{timeline_affected_element_guid}/context-events-describing-timeline-effects/{context_event_guid}/attach"
        await self._async_new_relationship_request(url, ['ContextEventTimelineEffect'],body)

    def link_context_event_timeline_effect(
        self,
        timeline_affected_element_guid: str,
        context_event_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link context event timeline effect.

        Parameters
        ----------
        timeline_affected_element_guid : str
            The unique identifier of the element affected by the timeline.
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

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
            "class": "ContextEventForTimelineEffectsProperties",
            "label" : "Timeline Effect",
            "description" : "Element data affected by context event"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_context_event_timeline_effect(
                timeline_affected_element_guid, context_event_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_context_event_timeline_effect(
        self,
        timeline_affected_element_guid: str,
        context_event_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach context event timeline effect. Async version.

        Parameters
        ----------
        timeline_affected_element_guid : str
            The unique identifier of the element affected by the timeline.
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/elements/{timeline_affected_element_guid}/context-events-describing-timeline-effect/{context_event_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_context_event_timeline_effect(
        self,
        timeline_affected_element_guid: str,
        context_event_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach context event timeline effect.

        Parameters
        ----------
        timeline_affected_element_guid : str
            The unique identifier of the element affected by the timeline.
        context_event_guid : str
            The unique identifier of the context event.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "cascadedDelete" : false,
          "deleteMethod" : "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_context_event_timeline_effect(
                timeline_affected_element_guid, context_event_guid, body
            )
        )

    @dynamic_catch
    async def _async_get_context_events_by_name(
        self,
        filter_string: str = None,
        classification_names: list[str] = None,
        body: dict | FilterRequestBody = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "ContextEvents",
    ) -> list | str:
        """Get context events by name. Async version.

        Parameters
        ----------
        filter_string : str, optional
            The string to find in the properties.
        classification_names : list[str], optional
            The list of classification names to filter by.
        body : dict | FilterRequestBody, optional
            The request body for the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        list | str
            The list of matching context events or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "FilterRequestBody",
          "filter" : "EventName",
          "startFrom": 0,
          "pageSize": 10
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/by-name"
        return await self._async_get_name_request(
            url,
            _type="ContextEvent",
            _gen_output=self._generate_context_event_output,
            filter_string=filter_string,
            classification_names=classification_names,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_context_events_by_name(
        self,
        filter_string: str = None,
        classification_names: list[str] = None,
        body: dict | FilterRequestBody = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "ContextEvents",
    ) -> list | str:
        """Get context events by name.

        Parameters
        ----------
        filter_string : str, optional
            The string to find in the properties.
        classification_names : list[str], optional
            The list of classification names to filter by.
        body : dict | FilterRequestBody, optional
            The request body for the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        list | str
            The list of matching context events or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "FilterRequestBody",
          "filter" : "EventName",
          "startFrom": 0,
          "pageSize": 10
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_context_events_by_name(
                filter_string,
                classification_names,
                body,
                start_from,
                page_size,
                output_format,
                report_spec,
            )
        )

    @dynamic_catch
    async def _async_find_context_events(
        self,
        search_string: str = "*",
        skip_classification_names: list[str] = None,
        metadata_element_subtypes: list[str] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        body: dict | SearchStringRequestBody = None,
    ) -> list | str:
        """Find context events. Async version.

        Parameters
        ----------
        search_string : str, optional
            The string to search for.
        skip_classification_names : list[str], optional
            The list of classification names to skip.
        metadata_element_subtypes : list[str], optional
            The list of metadata element subtypes to filter by.
        starts_with : bool, optional
            Whether the search string must be at the start.
        ends_with : bool, optional
            Whether the search string must be at the end.
        ignore_case : bool, optional
            Whether to ignore case in the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | SearchStringRequestBody, optional
            The request body for the search.

        Returns
        -------
        list | str
            The list of matching context events or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "SearchStringRequestBody",
          "searchString": "Event",
          "startsWith" : true,
          "ignoreCase" : true
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/by-search-string"
        return await self._async_find_request(
            url,
            _type="ContextEvent",
            _gen_output=self._generate_context_event_output,
            search_string=search_string,
            skip_classified_elements=skip_classification_names,
            metadata_element_subtypes=metadata_element_subtypes,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def find_context_events(
        self,
        search_string: str = "*",
        classification_names: list[str] = None,
        metadata_element_subtypes: list[str] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        body: dict | SearchStringRequestBody = None,
    ) -> list | str:
        """Find context events.

        Parameters
        ----------
        search_string : str, optional
            The string to search for.
        classification_names : list[str], optional
            The list of classification names to filter by.
        metadata_element_subtypes : list[str], optional
            The list of metadata element subtypes to filter by.
        starts_with : bool, optional
            Whether the search string must be at the start.
        ends_with : bool, optional
            Whether the search string must be at the end.
        ignore_case : bool, optional
            Whether to ignore case in the search.
        start_from : int, optional
            The starting index for paged results.
        page_size : int, optional
            The maximum number of results to return.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.
        body : dict | SearchStringRequestBody, optional
            The request body for the search.

        Returns
        -------
        list | str
            The list of matching context events or a message if none found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "SearchStringRequestBody",
          "searchString": "Event",
          "startsWith" : true,
          "ignoreCase" : true
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_context_events(
                search_string,
                classification_names,
                metadata_element_subtypes,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                output_format,
                report_spec,
                body,
            )
        )

    @dynamic_catch
    async def _async_get_context_event_by_guid(
        self,
        context_event_guid: str,
        element_type: str = "ContextEvent",
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict = "ContextEvents",
    ) -> dict | str:
        """Get context event by GUID. Async version.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        element_type : str, optional
            The type of metadata element.
        body : dict | GetRequestBody, optional
            The request body for the retrieval.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        dict | str
            The properties of the context event or a message if not found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "forLineage" : false
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/time-keeper/context-events/{context_event_guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            _type=element_type,
            _gen_output=self._generate_context_event_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    def get_context_event_by_guid(
        self,
        context_event_guid: str,
        element_type: str = "ContextEvent",
        body: dict | GetRequestBody = None,
        output_format: str = "JSON",
        report_spec: str | dict = "ContextEvents",
    ) -> dict | str:
        """Get context event by GUID.

        Parameters
        ----------
        context_event_guid : str
            The unique identifier of the context event.
        element_type : str, optional
            The type of metadata element.
        body : dict | GetRequestBody, optional
            The request body for the retrieval.
        output_format : str, optional
            The desired output format.
        report_spec : str | dict, optional
            The desired output columns/fields to include.

        Returns
        -------
        dict | str
            The properties of the context event or a message if not found.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "GetRequestBody",
          "forLineage" : false
        }
        ```
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_context_event_by_guid(
                context_event_guid, element_type, body, output_format, report_spec
            )
        )
