"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    The Metadata Expert OMVS provides APIs for supporting the search, query and retrieval of open metadata.
    It is an advanced API for users that understand the Open Metadata Types.

"""

import asyncio
from loguru import logger

from pyegeria.models import (NewOpenMetadataElementRequestBody, TemplateRequestBody,
                             UpdatePropertiesRequestBody, MetadataSourceRequestBody,
                             UpdateEffectivityDatesRequestBody, OpenMetadataDeleteRequestBody,
                             ArchiveRequestBody, NewClassificationRequestBody,
                             NewRelatedElementsRequestBody)
from pyegeria.core.utils import dynamic_catch
from pyegeria.core._server_client import ServerClient
from typing import Any, Optional

class MetadataExpert(ServerClient):
    """
    Metadata Expert OMVS client.

    Attributes:
        server_name: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str
            An optional bearer token
    """

    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: Optional[str] = None, token: str = None):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        logger.debug(f"{self.__class__.__name__} initialized")
        self.command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/metadata-expert")

    @dynamic_catch
    async def _async_create_metadata_element(self, body: Optional[dict | NewOpenMetadataElementRequestBody] = None) -> str:
        """
        Create a new metadata element in the metadata store. Async version.
        The type name comes from the open metadata types.
        The selected type also controls the names and types of the properties that are allowed.
        This version of the method allows access to advanced features such as multiple states and
        effectivity dates.

        Parameters
        ----------
        body : dict | NewOpenMetadataElementRequestBody, optional
            The details of the metadata element to create.

        Returns
        -------
        str
            The unique identifier (GUID) of the newly created metadata element.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "NewOpenMetadataElementRequestBody",
          "externalSourceGUID" : "",
          "externalSourceName" : "",
          "typeName" : "",
          "initialClassifications" : {},
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTo": "2024-12-31T23:59:59.000+00:00",
          "properties" : {},
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements"
        return await self._async_create_open_metadata_element_body_request(url, body)

    @dynamic_catch
    def create_metadata_element(self, body: Optional[dict | NewOpenMetadataElementRequestBody] = None) -> str:
        """
        Create a new metadata element in the metadata store.
        """
        return asyncio.run(self._async_create_metadata_element(body))

    @dynamic_catch
    async def _async_create_metadata_element_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """
        Create a new metadata element in the metadata store using a template. Async version.

        Parameters
        ----------
        body : dict | TemplateRequestBody, optional
            The details for creating the element from a template.

        Returns
        -------
        str
            The unique identifier (GUID) of the newly created metadata element.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "TemplateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "typeName" : "",
          "templateGUID" : "",
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTo": "2024-12-31T23:59:59.000+00:00",
          "replacementProperties" : {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "propertyName" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "value of property"
              }
            }
          },
          "placeholderPropertyValues" : {
             "placeholderName1" : "placeholderValue1",
             "placeholderName2" : "placeholderValue2"
          },
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/from-template"
        return await self._async_create_element_from_template(url, body)

    @dynamic_catch
    def create_metadata_element_from_template(self, body: Optional[dict | TemplateRequestBody] = None) -> str:
        """
        Create a new metadata element in the metadata store using a template.
        """
        return asyncio.run(self._async_create_metadata_element_from_template(body))

    @dynamic_catch
    async def _async_update_metadata_element_properties(self, metadata_element_guid: str, body: Optional[dict | UpdatePropertiesRequestBody] = None) -> None:
        """
        Update the properties of a specific metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element to update.
        body : dict | UpdatePropertiesRequestBody, optional
            The updated properties.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "properties" : {
            "class": "ElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "replaceProperties" : false
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/update-properties"
        await self._async_update_properties_body_request(url, body)

    @dynamic_catch
    def update_metadata_element_properties(self, metadata_element_guid: str, body: Optional[dict | UpdatePropertiesRequestBody] = None) -> None:
        """
        Update the properties of a specific metadata element.
        """
        return asyncio.run(self._async_update_metadata_element_properties(metadata_element_guid, body))

    @dynamic_catch
    async def _async_publish_metadata_element(self, metadata_element_guid: str, body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """
        Update the zone membership to increase its visibility. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element to publish.
        body : dict | MetadataSourceRequestBody, optional
            Publication details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/publish"
        await self._async_metadata_source_body_request(url, body)

    @dynamic_catch
    def publish_metadata_element(self, metadata_element_guid: str, body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """
        Update the zone membership to increase its visibility.
        """
        return asyncio.run(self._async_publish_metadata_element(metadata_element_guid, body))

    @dynamic_catch
    async def _async_withdraw_metadata_element(self, metadata_element_guid: str, body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """
        Update the zone membership to decrease its visibility. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element to withdraw.
        body : dict | MetadataSourceRequestBody, optional
            Withdrawal details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/withdraw"
        await self._async_metadata_source_body_request(url, body)

    @dynamic_catch
    def withdraw_metadata_element(self, metadata_element_guid: str, body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """
        Update the zone membership to decrease its visibility.
        """
        return asyncio.run(self._async_withdraw_metadata_element(metadata_element_guid, body))

    @dynamic_catch
    async def _async_update_metadata_element_effectivity(self, metadata_element_guid: str, body: Optional[dict | UpdateEffectivityDatesRequestBody] = None) -> None:
        """
        Update the effectivity dates for a specific metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element.
        body : dict | UpdateEffectivityDatesRequestBody, optional
            The new effectivity dates.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTo": "2024-12-31T23:59:59.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/update-effectivity"
        await self._async_update_effectivity_dates_body_request(url, body)

    @dynamic_catch
    def update_metadata_element_effectivity(self, metadata_element_guid: str, body: Optional[dict | UpdateEffectivityDatesRequestBody] = None) -> None:
        """
        Update the effectivity dates for a specific metadata element.
        """
        return asyncio.run(self._async_update_metadata_element_effectivity(metadata_element_guid, body))

    @dynamic_catch
    async def _async_delete_metadata_element(self, metadata_element_guid: str, body: Optional[dict | OpenMetadataDeleteRequestBody] = None) -> None:
        """
        Delete a specific metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element to delete.
        body : dict | OpenMetadataDeleteRequestBody, optional
            Deletion details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "OpenMetadataDeleteRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/delete"
        await self._async_open_metadata_delete_body_request(url, body)

    @dynamic_catch
    def delete_metadata_element(self, metadata_element_guid: str, body: Optional[dict | OpenMetadataDeleteRequestBody] = None) -> None:
        """
        Delete a specific metadata element.
        """
        return asyncio.run(self._async_delete_metadata_element(metadata_element_guid, body))

    @dynamic_catch
    async def _async_archive_metadata_element(self, metadata_element_guid: str, body: Optional[dict | ArchiveRequestBody] = None) -> None:
        """
        Archive a specific metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element to archive.
        body : dict | ArchiveRequestBody, optional
            Archiving details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "ArchiveRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "archiveProperties" : {
            "archiveDate" : "2024-01-01T00:00:00.000+00:00",
            "archiveProcess" : "",
            "archiveProperties": {
               "propertyName1" : "propertyValue1",
               "propertyName2" : "propertyValue2"
            }
          },
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/archive"
        await self._async_archive_body_request(url, body)

    @dynamic_catch
    def archive_metadata_element(self, metadata_element_guid: str, body: Optional[dict | ArchiveRequestBody] = None) -> None:
        """
        Archive a specific metadata element.
        """
        return asyncio.run(self._async_archive_metadata_element(metadata_element_guid, body))

    @dynamic_catch
    async def _async_classify_metadata_element(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """
        Add a new classification to the metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element.
        classification_name : str
            Name of the classification to add.
        body : dict | NewClassificationRequestBody, optional
            Classification details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "NewClassificationRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/classifications/{classification_name}"
        await self._async_new_classification_request(url, body=body)

    @dynamic_catch
    def classify_metadata_element(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """
        Add a new classification to the metadata element.
        """
        return asyncio.run(self._async_classify_metadata_element(metadata_element_guid, classification_name, body))

    @dynamic_catch
    async def _async_reclassify_metadata_element(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | UpdatePropertiesRequestBody] = None) -> None:
        """
        Update the properties of a classification that is currently attached to a specific metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element.
        classification_name : str
            Name of the classification to update.
        body : dict | UpdatePropertiesRequestBody, optional
            Updated classification properties.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/classifications/{classification_name}/update-properties"
        await self._async_update_properties_body_request(url, body)

    @dynamic_catch
    def reclassify_metadata_element(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | UpdatePropertiesRequestBody] = None) -> None:
        """
        Update the properties of a classification that is currently attached to a specific metadata element.
        """
        return asyncio.run(self._async_reclassify_metadata_element(metadata_element_guid, classification_name, body))

    @dynamic_catch
    async def _async_update_classification_effectivity(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | UpdateEffectivityDatesRequestBody] = None) -> None:
        """
        Update the effectivity dates of a specific classification attached to a metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element.
        classification_name : str
            Name of the classification.
        body : dict | UpdateEffectivityDatesRequestBody, optional
            New effectivity dates.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTo": "2024-12-31T23:59:59.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/classifications/{classification_name}/update-effectivity"
        await self._async_update_effectivity_dates_body_request(url, body)

    @dynamic_catch
    def update_classification_effectivity(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | UpdateEffectivityDatesRequestBody] = None) -> None:
        """
        Update the effectivity dates of a specific classification attached to a metadata element.
        """
        return asyncio.run(self._async_update_classification_effectivity(metadata_element_guid, classification_name, body))

    @dynamic_catch
    async def _async_declassify_metadata_element(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """
        Remove the named classification from a specific metadata element. Async version.

        Parameters
        ----------
        metadata_element_guid : str
            Unique identifier of the metadata element.
        classification_name : str
            Name of the classification to remove.
        body : dict | MetadataSourceRequestBody, optional
            Declassification details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/metadata-elements/{metadata_element_guid}/classifications/{classification_name}/delete"
        await self._async_metadata_source_body_request(url, body)

    @dynamic_catch
    def declassify_metadata_element(self, metadata_element_guid: str, classification_name: str, body: Optional[dict | MetadataSourceRequestBody] = None) -> None:
        """
        Remove the named classification from a specific metadata element.
        """
        return asyncio.run(self._async_declassify_metadata_element(metadata_element_guid, classification_name, body))

    @dynamic_catch
    async def _async_create_related_elements(self, body: Optional[dict | NewRelatedElementsRequestBody] = None) -> str:
        """
        Create a relationship between two metadata elements. Async version.

        Parameters
        ----------
        body : dict | NewRelatedElementsRequestBody, optional
            The details of the relationship to create.

        Returns
        -------
        str
            The unique identifier (GUID) of the newly created relationship.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "NewRelatedElementsRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/related-elements"
        return await self._async_create_related_elements_body_request(url, body)

    @dynamic_catch
    def create_related_elements(self, body: Optional[dict | NewRelatedElementsRequestBody] = None) -> str:
        """
        Create a relationship between two metadata elements.
        """
        return asyncio.run(self._async_create_related_elements(body))

    @dynamic_catch
    async def _async_update_related_elements_properties(self, relationship_guid: str, body: Optional[dict | UpdatePropertiesRequestBody] = None) -> None:
        """
        Update the properties associated with a relationship. Async version.

        Parameters
        ----------
        relationship_guid : str
            Unique identifier of the relationship.
        body : dict | UpdatePropertiesRequestBody, optional
            The updated properties.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/related-elements/{relationship_guid}/update-properties"
        await self._async_update_properties_body_request(url, body)

    @dynamic_catch
    def update_related_elements_properties(self, relationship_guid: str, body: Optional[dict | UpdatePropertiesRequestBody] = None) -> None:
        """
        Update the properties associated with a relationship.
        """
        return asyncio.run(self._async_update_related_elements_properties(relationship_guid, body))

    @dynamic_catch
    async def _async_update_related_elements_effectivity(self, relationship_guid: str, body: Optional[dict | UpdateEffectivityDatesRequestBody] = None) -> None:
        """
        Update the effectivity dates of a specific relationship between metadata elements. Async version.

        Parameters
        ----------
        relationship_guid : str
            Unique identifier of the relationship.
        body : dict | UpdateEffectivityDatesRequestBody, optional
            The new effectivity dates.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTo": "2024-12-31T23:59:59.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/related-elements/{relationship_guid}/update-effectivity"
        await self._async_update_effectivity_dates_body_request(url, body)

    @dynamic_catch
    def update_related_elements_effectivity(self, relationship_guid: str, body: Optional[dict | UpdateEffectivityDatesRequestBody] = None) -> None:
        """
        Update the effectivity dates of a specific relationship between metadata elements.
        """
        return asyncio.run(self._async_update_related_elements_effectivity(relationship_guid, body))

    @dynamic_catch
    async def _async_delete_related_elements(self, relationship_guid: str, body: Optional[dict | OpenMetadataDeleteRequestBody] = None) -> None:
        """
        Delete a relationship between two metadata elements. Async version.

        Parameters
        ----------
        relationship_guid : str
            Unique identifier of the relationship to delete.
        body : dict | OpenMetadataDeleteRequestBody, optional
            Deletion details.

        Notes
        -----
        Sample JSON body:
        {
          "class" : "OpenMetadataDeleteRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/related-elements/{relationship_guid}/delete"
        await self._async_open_metadata_delete_body_request(url, body)

    @dynamic_catch
    def delete_related_elements(self, relationship_guid: str, body: Optional[dict | OpenMetadataDeleteRequestBody] = None) -> None:
        """
        Delete a relationship between two metadata elements.
        """
        return asyncio.run(self._async_delete_related_elements(relationship_guid, body))
