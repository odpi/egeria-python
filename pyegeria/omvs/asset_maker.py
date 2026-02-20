"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Asset Maker OMVS module.
The Asset Maker OMVS provides APIs for supporting the creation and editing of assets.

"""

import asyncio
from typing import Any, Optional
from pyegeria.core._server_client import ServerClient
from pyegeria.core._globals import max_paging_size, NO_ELEMENTS_FOUND, NO_GUID_RETURNED
from pyegeria.core.config import settings as app_settings
from pyegeria.models import (
    GetRequestBody,
    SearchStringRequestBody,
    FilterRequestBody,
    NewElementRequestBody,
    ReferenceableProperties,
    TemplateRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    NewRelationshipRequestBody,
    UpdateRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    ContentStatusSearchString,
    ContentStatusFilterRequestBody,
    ActivityStatusSearchString,
    ActivityStatusFilterRequestBody,
    ActivityStatusRequestBody,
    ActionRequestBody,
    DeploymentStatusSearchString,
    DeploymentStatusFilterRequestBody,
)
from pyegeria.core.utils import dynamic_catch
from pyegeria.view.base_report_formats import select_report_spec, get_report_spec_match

EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier


class AssetProperties(ReferenceableProperties):
    """Properties for Asset elements"""
    pass


class CatalogTargetProperties(ReferenceableProperties):
    """Properties for Catalog Target relationships"""
    catalogTargetName: str | None = None
    metadataSourceQualifiedName: str | None = None
    templates: dict | None = None
    configurationProperties: dict | None = None


class AssetMaker(ServerClient):
    """AssetMaker is a class that extends the ServerClient class. The Asset Maker OMVS provides APIs for
    supporting the creation and editing of assets.

    Attributes:

        view_server: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a
            default optionally used by the methods when the user
            doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None

    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str | None = None,
        user_pwd: str | None = None,
        token: str | None = None,
    ):
        """Initialize an AssetMaker client."""
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        ServerClient.__init__(
            self, view_server, platform_url, user_id=user_id, user_pwd=user_pwd, token=token
        )
        self.asset_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/asset-maker"
        self.curation_command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/automated-curation"

    #
    # Asset Management Methods
    #

    @dynamic_catch
    async def _async_create_asset(self, asset_type: list[str]=None, body: dict | NewElementRequestBody | None = None) -> str:
        """Create an asset. Async version.

        Parameters
        ----------
        asset_type: [str], optional
            The type of asset to create. If not provided, a generic asset type will be used.
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the asset to create.

        Returns
        -------
        str - the guid of the created asset

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.

        Notes
        -----
        See: https://egeria-project.org/concepts/asset

        Sample body:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class" : "AssetProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "2024-01-01T00:00:00.000+00:00",
            "effectiveTo": "2024-12-31T23:59:59.999+00:00"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return await super()._async_create_asset(asset_type, body)

    @dynamic_catch
    def create_asset(self, asset_type:list[str]=None, body: dict | NewElementRequestBody | None = None) -> str:
        """Create an asset.

        Parameters
        ----------
        asset_type: [str], optional
            The type of asset to create. If not provided, a generic asset type will be used.
        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the asset to create.

        Returns
        -------
        str - the guid of the created asset

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.

        Notes
        -----
        See: https://egeria-project.org/concepts/asset

        Sample body:
        {
          "class" : "NewElementRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
          "properties": {
            "class" : "AssetProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "effectiveFrom": "2024-01-01T00:00:00.000+00:00",
            "effectiveTo": "2024-12-31T23:59:59.999+00:00"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return super().create_asset(asset_type, body)

    @dynamic_catch
    async def _async_create_asset_from_template(
        self, body: dict | TemplateRequestBody | None = None
    ) -> str:
        """Create a new metadata element to represent an asset using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.
        Async version.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dict or TemplateRequestBody representing the template details.

        Returns
        -------
        str - the guid of the created asset

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.

        Notes
        -----
        Sample body:
        {
          "class" : "TemplateRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
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
          },
          "placeholderPropertyValues":  {
            "placeholder1" : "propertyValue1",
            "placeholder2" : "propertyValue2"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return await super()._async_create_asset_from_template(body)

    @dynamic_catch
    def create_asset_from_template(self, body: dict | TemplateRequestBody | None = None) -> str:
        """Create a new metadata element to represent an asset using an existing metadata element as a template.
        The template defines additional classifications and relationships that should be added to the new element.

        Parameters
        ----------
        body: dict | TemplateRequestBody
            A dict or TemplateRequestBody representing the template details.

        Returns
        -------
        str - the guid of the created asset

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the TemplateRequestBody.

        Notes
        -----
        Sample body:
        {
          "class" : "TemplateRequestBody",
          "anchorGUID" : "add guid here",
          "isOwnAnchor": false,
          "parentGUID": "add guid here",
          "parentRelationshipTypeName": "add type name here",
          "parentRelationshipProperties": {
            "class": "RelationshipElementProperties",
            "propertyValueMap" : {
              "description" : {
                "class": "PrimitiveTypePropertyValue",
                "typeName": "string",
                "primitiveValue" : "New description"
              }
            }
          },
          "parentAtEnd1": false,
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
          },
          "placeholderPropertyValues":  {
            "placeholder1" : "propertyValue1",
            "placeholder2" : "propertyValue2"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        return super().create_asset_from_template(body)

    @dynamic_catch
    async def _async_update_asset(
        self, asset_guid: str, body: dict | UpdateElementRequestBody | None = None
    ) -> None:
        """Update the properties of an asset. Async version.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset to update.
        body: dict | UpdateElementRequestBody
            A dict or UpdateElementRequestBody with the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.

        Notes
        -----
        Sample body:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AssetProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        await super()._async_update_asset(asset_guid, body)

    @dynamic_catch
    def update_asset(
        self, asset_guid: str, body: dict | UpdateElementRequestBody | None = None
    ) -> None:
        """Update the properties of an asset.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset to update.
        body: dict | UpdateElementRequestBody
            A dict or UpdateElementRequestBody with the properties to update.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the UpdateElementRequestBody.

        Notes
        -----
        Sample body:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AssetProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        super().update_asset(asset_guid, body)

    @dynamic_catch
    async def _async_delete_asset(
        self, asset_guid: str, body: dict | DeleteElementRequestBody | None = None
    ) -> None:
        """Delete an asset. Async version.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset to delete.
        body: dict | DeleteElementRequestBody, optional
            Additional parameters for the delete operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "DeleteElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        await super()._async_delete_asset(asset_guid, body)

    @dynamic_catch
    def delete_asset(
        self, asset_guid: str, body: dict | DeleteElementRequestBody | None = None
    ) -> None:
        """Delete an asset.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset to delete.
        body: dict | DeleteElementRequestBody, optional
            Additional parameters for the delete operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "DeleteElementRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        super().delete_asset(asset_guid, body)

    @dynamic_catch
    async def _async_get_assets_by_name(
        self,
        filter_string: str,
        classification_names: Optional[list[str]] = None,
        body: dict | FilterRequestBody | None = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> list | dict | str:
        """Returns the list of assets with a particular name. Async version.

        Parameters
        ----------
        filter_string: str
            String to find in the asset properties.
        classification_names: list[str], optional
            Classification/type filters to include in the request body.
        body: dict | FilterRequestBody, optional
            Additional filter parameters.
        start_from: int, optional
            Index of the first result to return. Default is 0.
        page_size: int, optional
            Maximum number of results to return. Default is None (server default).
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        list | dict | str
            List of matching assets in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "FilterRequestBody",
          "filter" : "Add name here",
          "startFrom" : 0,
          "pageSize": 10,
          "metadataElementTypeName": "GovernanceActionType",
          "metadataElementSubtypeNames": [],
          "skipRelationships": [],
          "includeOnlyRelationships": [],
          "relationshipsPageSize": 100,
          "skipClassifiedElements": [],
          "includeOnlyClassifiedElements": [],
          "graphQueryDepth" : 10,
          "asOfTime" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """
        url = f"{self.asset_command_root}/assets/by-name"
        return await self._async_get_name_request(
            url,
            _type="Asset",
            _gen_output=self._generate_referenceable_output,
            filter_string=filter_string,
            classification_names=classification_names,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_assets_by_name(
        self,
        filter_string: str,
        classification_names: Optional[list[str]] = None,
        body: dict | FilterRequestBody | None = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> list | dict | str:
        """Returns the list of assets with a particular name.

        Parameters
        ----------
        filter_string: str
            String to find in the asset properties.
        classification_names: list[str], optional
            Classification/type filters to include in the request body.
        body: dict | FilterRequestBody, optional
            Additional filter parameters.
        start_from: int, optional
            Index of the first result to return. Default is 0.
        page_size: int, optional
            Maximum number of results to return. Default is None (server default).
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        list | dict | str
            List of matching assets in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "FilterRequestBody",
          "filter" : "Add name here",
          "startFrom" : 0,
          "pageSize": 10,
          "metadataElementTypeName": "GovernanceActionType",
          "metadataElementSubtypeNames": [],
          "skipRelationships": [],
          "includeOnlyRelationships": [],
          "relationshipsPageSize": 100,
          "skipClassifiedElements": [],
          "includeOnlyClassifiedElements": [],
          "graphQueryDepth" : 10,
          "asOfTime" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_assets_by_name(
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
    async def _async_find_assets(self, search_string: str = "*", starts_with: bool = False, ends_with: bool = False,
                                 ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None,
                                 metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None,
                                 include_only_relationships: Optional[list[str]] = None,
                                 skip_classified_elements: Optional[list[str]] = None,
                                 include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3,
                                 governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                                 effective_time: Optional[str] = None, relationship_page_size: int = 0,
                                 limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                                 sequencing_property: Optional[str] = None, output_format: str = "DICT",
                                 report_spec: dict | str | None = None, start_from: int = 0,
                                 page_size: int = 0, property_names: Optional[list[str]] = None,
                                 body: dict | SearchStringRequestBody | None = None) -> list | dict | str:
        """Retrieve the list of asset metadata elements that contain the search string. Async version.

        Parameters
        ----------
        search_string: str, optional
            String to search for in asset properties. Default is "*".
        starts_with: bool, optional
            Whether to match only at the start. Default is False.
        ends_with: bool, optional
            Whether to match only at the end. Default is False.
        ignore_case: bool, optional
            Whether to ignore case in matching. Default is True.
        start_from: int, optional
            Index of the first result to return. Default is 0.
        page_size: int, optional
            Maximum number of results to return. Default is None (server default).
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.
        body: dict | SearchStringRequestBody, optional
            Additional search parameters.

        Returns
        -------
        list | dict | str
            List of matching assets in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "SearchStringRequestBody",
          "searchString": "xxx",
          "metadataElementTypeName": "GovernanceActionType",
          "metadataElementSubtypeNames": [],
          "skipRelationships": [],
          "includeOnlyRelationships": [],
          "relationshipsPageSize": 100,
          "skipClassifiedElements": [],
          "includeOnlyClassifiedElements": [],
          "graphQueryDepth" : 10,
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0,
          "asOfTime" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """
        return await super()._async_find_assets(search_string=search_string, starts_with=starts_with,
                                                ends_with=ends_with, ignore_case=ignore_case,
                                                anchor_domain=anchor_domain,
                                                metadata_element_type=metadata_element_type,
                                                metadata_element_subtypes=metadata_element_subtypes,
                                                skip_relationships=skip_relationships,
                                                include_only_relationships=include_only_relationships,
                                                skip_classified_elements=skip_classified_elements,
                                                include_only_classified_elements=include_only_classified_elements,
                                                graph_query_depth=graph_query_depth,
                                                governance_zone_filter=governance_zone_filter, as_of_time=as_of_time,
                                                effective_time=effective_time,
                                                relationship_page_size=relationship_page_size,
                                                limit_results_by_status=limit_results_by_status,
                                                sequencing_order=sequencing_order,
                                                sequencing_property=sequencing_property, output_format=output_format,
                                                report_spec=report_spec, start_from=start_from, page_size=page_size,
                                                body=body)

    @dynamic_catch
    def find_assets(self, search_string: str = "*", starts_with: bool = False, ends_with: bool = False,
                    ignore_case: bool = True, anchor_domain: Optional[str] = None, metadata_element_type: Optional[str] = None,
                    metadata_element_subtypes: Optional[list[str]] = None, skip_relationships: Optional[list[str]] = None,
                    include_only_relationships: Optional[list[str]] = None, skip_classified_elements: Optional[list[str]] = None,
                    include_only_classified_elements: Optional[list[str]] = None, graph_query_depth: int = 3,
                    governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None, effective_time: Optional[str] = None,
                    relationship_page_size: int = 0, limit_results_by_status: Optional[list[str]] = None,
                    sequencing_order: Optional[str] = None, sequencing_property: Optional[str] = None, output_format: str = "DICT",
                    report_spec: dict | str | None = None, start_from: int = 0, page_size: int = 0,
                    property_names: Optional[list[str]] = None, body: dict | SearchStringRequestBody | None = None) -> list | dict | str:
        """Retrieve the list of asset metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str, optional
            String to search for in asset properties. Default is "*".
        starts_with: bool, optional
            Whether to match only at the start. Default is False.
        ends_with: bool, optional
            Whether to match only at the end. Default is False.
        ignore_case: bool, optional
            Whether to ignore case in matching. Default is True.
        start_from: int, optional
            Index of the first result to return. Default is 0.
        page_size: int, optional
            Maximum number of results to return. Default is None (server default).
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.
        body: dict | SearchStringRequestBody, optional
            Additional search parameters.

        Returns
        -------
        list | dict | str
            List of matching assets in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "SearchStringRequestBody",
          "searchString": "xxx",
          "metadataElementTypeName": "GovernanceActionType",
          "metadataElementSubtypeNames": [],
          "skipRelationships": [],
          "includeOnlyRelationships": [],
          "relationshipsPageSize": 100,
          "skipClassifiedElements": [],
          "includeOnlyClassifiedElements": [],
          "graphQueryDepth" : 10,
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0,
          "asOfTime" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "limitResultsByStatus" : ["ACTIVE"],
          "sequencingOrder" : "PROPERTY_ASCENDING",
          "sequencingProperty" : "qualifiedName"
        }
        """
        return super().find_assets(search_string=search_string, starts_with=starts_with, ends_with=ends_with,
                                   ignore_case=ignore_case, anchor_domain=anchor_domain,
                                   metadata_element_type=metadata_element_type,
                                   metadata_element_subtypes=metadata_element_subtypes,
                                   skip_relationships=skip_relationships,
                                   include_only_relationships=include_only_relationships,
                                   skip_classified_elements=skip_classified_elements,
                                   include_only_classified_elements=include_only_classified_elements,
                                   graph_query_depth=graph_query_depth, governance_zone_filter=governance_zone_filter,
                                   as_of_time=as_of_time, effective_time=effective_time,
                                   relationship_page_size=relationship_page_size,
                                   limit_results_by_status=limit_results_by_status, sequencing_order=sequencing_order,
                                   sequencing_property=sequencing_property, output_format=output_format,
                                   report_spec=report_spec, start_from=start_from, page_size=page_size, body=body)

    @dynamic_catch
    async def _async_get_asset_by_guid(
        self,
        asset_guid: str,
        element_type: Optional[str] = None,
        body: dict | GetRequestBody | None = None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str:
        """Return the properties of a specific asset. Async version.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset.
        element_type: str, optional
            Metadata element type name to include in the request body.
        body: dict | GetRequestBody, optional
            Additional parameters for the request.
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        dict | str
            Properties of the asset in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "GetRequestBody",
          "metadataElementTypeName": "",
          "metadataElementSubtypeNames": [],
          "skipRelationships": [],
          "includeOnlyRelationships": [],
          "relationshipsPageSize": 100,
          "skipClassifiedElements": [],
          "includeOnlyClassifiedElements": [],
          "graphQueryDepth" : 10,
          "asOfTime" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.asset_command_root}/assets/{asset_guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            _type=element_type or "Asset",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_asset_by_guid(
        self,
        asset_guid: str,
        element_type: Optional[str] = None,
        body: dict | GetRequestBody | None = None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str:
        """Return the properties of a specific asset.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset.
        element_type: str, optional
            Metadata element type name to include in the request body.
        body: dict | GetRequestBody, optional
            Additional parameters for the request.
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        dict | str
            Properties of the asset in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        Sample body:
        {
          "class" : "GetRequestBody",
          "metadataElementTypeName": "",
          "metadataElementSubtypeNames": [],
          "skipRelationships": [],
          "includeOnlyRelationships": [],
          "relationshipsPageSize": 100,
          "skipClassifiedElements": [],
          "includeOnlyClassifiedElements": [],
          "graphQueryDepth" : 10,
          "asOfTime" : "2024-01-01T00:00:00.000+00:00",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_asset_by_guid(asset_guid, element_type, body, output_format, report_spec)
        )

    #
    # Catalog Target Management Methods
    #

    @dynamic_catch
    async def _async_add_catalog_target(
        self,
        integration_connector_guid: str,
        metadata_element_guid: str,
        body: dict | NewRelationshipRequestBody | None = None,
    ) -> str:
        """Add a catalog target to an integration connector. Async version.

        Parameters
        ----------
        integration_connector_guid: str
            Unique identifier of the integration connector.
        metadata_element_guid: str
            Unique identifier of the metadata element to be cataloged.
        body: dict | NewRelationshipRequestBody, optional
            Properties for the catalog target relationship.

        Returns
        -------
        str
            GUID of the created catalog target relationship.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/

        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "CatalogTargetProperties",
            "catalogTargetName" : "Freddy",
            "metadataSourceQualifiedName" : "",
            "templates" : {
               "templateName1" : "template1GUID",
               "templateName2" : "template2GUID"
            },
            "configurationProperties" : {
              "propertyName1" : "propertyValue1",
              "propertyName2" : "propertyValue2"
            },
            "effectiveFrom": "2024-01-01T00:00:00.000+00:00",
            "effectiveTo": "2024-12-31T23:59:59.999+00:00"
          }
        }
        """
        url = f"{self.curation_command_root}/integration-connectors/{integration_connector_guid}/catalog-targets/{metadata_element_guid}"
        await self._async_new_relationship_request(url, ["CatalogTargetProperties"], body)
        return "Relationship created"  # The base method doesn't return a GUID for relationships

    @dynamic_catch
    def add_catalog_target(
        self,
        integration_connector_guid: str,
        metadata_element_guid: str,
        body: dict | NewRelationshipRequestBody | None = None,
    ) -> str:
        """Add a catalog target to an integration connector.

        Parameters
        ----------
        integration_connector_guid: str
            Unique identifier of the integration connector.
        metadata_element_guid: str
            Unique identifier of the metadata element to be cataloged.
        body: dict | NewRelationshipRequestBody, optional
            Properties for the catalog target relationship.

        Returns
        -------
        str
            GUID of the created catalog target relationship.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/

        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "CatalogTargetProperties",
            "catalogTargetName" : "Freddy",
            "metadataSourceQualifiedName" : "",
            "templates" : {
               "templateName1" : "template1GUID",
               "templateName2" : "template2GUID"
            },
            "configurationProperties" : {
              "propertyName1" : "propertyValue1",
              "propertyName2" : "propertyValue2"
            },
            "effectiveFrom": "2024-01-01T00:00:00.000+00:00",
            "effectiveTo": "2024-12-31T23:59:59.999+00:00"
          }
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_add_catalog_target(
                integration_connector_guid, metadata_element_guid, body
            )
        )

    @dynamic_catch
    async def _async_update_catalog_target(
        self,
        relationship_guid: str,
        body: dict | UpdateRelationshipRequestBody | None = None,
    ) -> None:
        """Update a catalog target for an integration connector. Async version.

        Parameters
        ----------
        relationship_guid: str
            Unique identifier of the catalog target relationship.
        body: dict | UpdateRelationshipRequestBody
            Updated properties for the catalog target.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/

        Sample body:
        {
          "class" : "UpdateRelationshipRequestBody",
          "properties" : {
            "class": "CatalogTargetProperties",
            "catalogTargetName" : "Freddy",
            "metadataSourceQualifiedName" : "",
            "templates" : {
               "templateName1" : "template1GUID",
               "templateName2" : "template2GUID"
            },
            "configurationProperties" : {
              "propertyName1" : "propertyValue1",
              "propertyName2" : "propertyValue2"
            }
          },
          "mergeUpdate": true,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.curation_command_root}/catalog-targets/{relationship_guid}/update"
        await self._async_update_relationship_request(url, ["CatalogTargetProperties"], body)

    @dynamic_catch
    def update_catalog_target(
        self,
        relationship_guid: str,
        body: dict | UpdateRelationshipRequestBody | None = None,
    ) -> None:
        """Update a catalog target for an integration connector.

        Parameters
        ----------
        relationship_guid: str
            Unique identifier of the catalog target relationship.
        body: dict | UpdateRelationshipRequestBody
            Updated properties for the catalog target.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/

        Sample body:
        {
          "class" : "UpdateRelationshipRequestBody",
          "properties" : {
            "class": "CatalogTargetProperties",
            "catalogTargetName" : "Freddy",
            "metadataSourceQualifiedName" : "",
            "templates" : {
               "templateName1" : "template1GUID",
               "templateName2" : "template2GUID"
            },
            "configurationProperties" : {
              "propertyName1" : "propertyValue1",
              "propertyName2" : "propertyValue2"
            }
          },
          "mergeUpdate": true,
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "2024-01-01T00:00:00.000+00:00",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_catalog_target(relationship_guid, body)
        )

    @dynamic_catch
    async def _async_get_catalog_target(
        self,
        relationship_guid: str,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str:
        """Retrieve a specific catalog target associated with an integration connector. Async version.

        Parameters
        ----------
        relationship_guid: str
            Unique identifier of the catalog target relationship.
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        dict | str
            Properties of the catalog target in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/
        """
        url = f"{self.curation_command_root}/catalog-targets/{relationship_guid}"
        return await self._async_get_guid_request(
            url,
            _type="CatalogTarget",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
        )

    @dynamic_catch
    def get_catalog_target(
        self,
        relationship_guid: str,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str:
        """Retrieve a specific catalog target associated with an integration connector.

        Parameters
        ----------
        relationship_guid: str
            Unique identifier of the catalog target relationship.
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        dict | str
            Properties of the catalog target in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_catalog_target(relationship_guid, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_catalog_targets(
        self,
        integration_connector_guid: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> list | dict | str:
        """Retrieve the details of the metadata elements identified as catalog targets with an integration connector.
        Async version.

        Parameters
        ----------
        integration_connector_guid: str
            Unique identifier of the integration connector.
        start_from: int, optional
            Index of the first result to return. Default is 0.
        page_size: int, optional
            Maximum number of results to return. Default is None (server default).
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        list | dict | str
            List of catalog targets in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/
        """
        url = (
            f"{self.curation_command_root}/integration-connectors/{integration_connector_guid}/"
            f"catalog-targets"
        )
        return await self._async_get_results_body_request(
            url,
            _type="CatalogTarget",
            _gen_output=self._generate_referenceable_output,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
        )

    @dynamic_catch
    def get_catalog_targets(
        self,
        integration_connector_guid: str,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> list | dict | str:
        """Retrieve the details of the metadata elements identified as catalog targets with an integration connector.

        Parameters
        ----------
        integration_connector_guid: str
            Unique identifier of the integration connector.
        start_from: int, optional
            Index of the first result to return. Default is 0.
        page_size: int, optional
            Maximum number of results to return. Default is None (server default).
        output_format: str, optional
            Format of the output. Default is "DICT".
        report_spec: dict | str, optional
            Specification for report formatting.

        Returns
        -------
        list | dict | str
            List of catalog targets in the specified format.

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_catalog_targets(
                integration_connector_guid, start_from, page_size, output_format, report_spec
            )
        )

    @dynamic_catch
    async def _async_remove_catalog_target(
        self,
        relationship_guid: str,
        body: dict | DeleteRelationshipRequestBody | None = None,
    ) -> None:
        """Unregister a catalog target from the integration connector. Async version.

        Parameters
        ----------
        relationship_guid: str
            Unique identifier of the catalog target relationship to remove.
        body: dict | DeleteRelationshipRequestBody, optional
            Additional parameters for the delete operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/
        """
        url = f"{self.curation_command_root}/catalog-targets/{relationship_guid}/remove"
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def remove_catalog_target(
        self,
        relationship_guid: str,
        body: dict | DeleteRelationshipRequestBody | None = None,
    ) -> None:
        """Unregister a catalog target from the integration connector.

        Parameters
        ----------
        relationship_guid: str
            Unique identifier of the catalog target relationship to remove.
        body: dict | DeleteRelationshipRequestBody, optional
            Additional parameters for the delete operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.

        Notes
        -----
        See: https://egeria-project.org/concepts/integration-connector/
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_catalog_target(relationship_guid, body)
        )

    #
    # Data Asset Methods
    #

    @dynamic_catch
    async def _async_find_data_assets(
        self,
        search_string: str = "*",
        content_status_list: list[str] = ["ACTIVE"],
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtypes: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ContentStatusSearchString] = None,
    ) -> list | str:
        """
        Returns the list of data assets matching the search string and optional content status. Async version.

        Parameters
        ----------
        search_string: str, default = "*"
            - the search string to use to find matching data assets
        content_status_list: list[str], default = ["ACTIVE"]
            - optional content status list to filter by
        starts_with: bool, default = False
            - if True, the search string must match the start of the property value
        ends_with: bool, default = False
            - if True, the search string must match the end of the property value
        ignore_case: bool, default = True
            - if True, the search is case-insensitive
        anchor_domain: str, optional
            - optional anchor domain filter
        metadata_element_type: str, optional
            - optional metadata element type filter
        metadata_element_subtypes: list[str], optional
            - optional metadata element subtypes filter
        skip_relationships: list[str], optional
            - relationships to skip
        include_only_relationships: list[str], optional
            - relationships to include
        skip_classified_elements: list[str], optional
            - classifications to skip
        include_only_classified_elements: list[str], optional
            - classifications to include
        graph_query_depth: int, default = 3
            - depth for relationship traversal
        governance_zone_filter: list[str], optional
            - governance zone filter
        as_of_time: str, optional
            - as-of time filter
        effective_time: str, optional
            - effective time filter
        relationship_page_size: int, default = 0
            - page size for relationships
        limit_results_by_status: list[str], optional
            - status filter for results
        sequencing_order: str, optional
            - sequencing order for results
        sequencing_property: str, optional
            - sequencing property for results
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | ContentStatusSearchString, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - a list of data assets or a string message if no assets are found

        Note:
        -----
        Sample body:
        {
          "class" : "ContentStatusSearchString",
          "searchString" : "xxx",
          "contentStatusList" : ["ACTIVE"],
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        url = f"{self.asset_command_root}/data-assets/by-search-string"
        return await self._async_content_status_search_request(
            url,
            _type="DataAsset",
            _gen_output=self._generate_referenceable_output,
            search_string=search_string,
            content_status_list=content_status_list,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            anchor_domain=anchor_domain,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtypes,
            skip_relationships=skip_relationships,
            include_only_relationships=include_only_relationships,
            skip_classified_elements=skip_classified_elements,
            include_only_classified_elements=include_only_classified_elements,
            graph_query_depth=graph_query_depth,
            governance_zone_filter=governance_zone_filter,
            as_of_time=as_of_time,
            effective_time=effective_time,
            relationship_page_size=relationship_page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            start_from=start_from,
            page_size=page_size,
            body=body,
        )

    @dynamic_catch
    def find_data_assets(
        self,
        search_string: str = "*",
        content_status_list: list[str] = ["ACTIVE"],
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtypes: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ContentStatusSearchString] = None,
    ) -> list | str:
        """
        Returns the list of data assets matching the search string and optional content status. Sync version.

        Parameters
        ----------
        search_string: str, default = "*"
            - the search string to use to find matching data assets
        content_status_list: list[str], default = ["ACTIVE"]
            - optional content status list to filter by
        starts_with: bool, default = False
            - if True, the search string must match the start of the property value
        ends_with: bool, default = False
            - if True, the search string must match the end of the property value
        ignore_case: bool, default = True
            - if True, the search is case-insensitive
        anchor_domain: str, optional
            - optional anchor domain filter
        metadata_element_type: str, optional
            - optional metadata element type filter
        metadata_element_subtypes: list[str], optional
            - optional metadata element subtypes filter
        skip_relationships: list[str], optional
            - relationships to skip
        include_only_relationships: list[str], optional
            - relationships to include
        skip_classified_elements: list[str], optional
            - classifications to skip
        include_only_classified_elements: list[str], optional
            - classifications to include
        graph_query_depth: int, default = 3
            - depth for relationship traversal
        governance_zone_filter: list[str], optional
            - governance zone filter
        as_of_time: str, optional
            - as-of time filter
        effective_time: str, optional
            - effective time filter
        relationship_page_size: int, default = 0
            - page size for relationships
        limit_results_by_status: list[str], optional
            - status filter for results
        sequencing_order: str, optional
            - sequencing order for results
        sequencing_property: str, optional
            - sequencing property for results
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | ContentStatusSearchString, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - a list of data assets or a string message if no assets are found

        Note:
        -----
        Sample body:
        {
          "class" : "ContentStatusSearchString",
          "searchString" : "xxx",
          "contentStatusList" : ["ACTIVE"],
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_data_assets(
                search_string,
                content_status_list,
                starts_with,
                ends_with,
                ignore_case,
                anchor_domain,
                metadata_element_type,
                metadata_element_subtypes,
                skip_relationships,
                include_only_relationships,
                skip_classified_elements,
                include_only_classified_elements,
                graph_query_depth,
                governance_zone_filter,
                as_of_time,
                effective_time,
                relationship_page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                start_from,
                page_size,
                output_format,
                report_spec,
                body,
            )
        )

    @dynamic_catch
    async def _async_get_data_assets_by_category(
        self,
        category: str,
        content_status_list: list[str] = ["ACTIVE"],
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ContentStatusFilterRequestBody] = None,
    ) -> list | str:
        """
        Returns the list of data assets matching the category and optional content status. Async version.

        Parameters
        ----------
        category: str
            - the category to filter by
        content_status_list: list[str], default = ["ACTIVE"]
            - optional content status list to filter by
        start_from: int, default = 0
            - starting point in the results
        page_size: int, default = 0
            - maximum results per page
        output_format: str, default = "JSON"
            - format of the output
        report_spec: str | dict, optional
            - report specification
        body: dict | ContentStatusFilterRequestBody, optional
            - the request body

        Returns
        -------
        list | str
            - a list of data assets

        Note:
        -----
        Sample body:
        {
          "class" : "ContentStatusFilterRequestBody",
          "filter" : "xxx",
          "contentStatusList" : ["ACTIVE"],
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        url = f"{self.asset_command_root}/data-assets/by-category"
        return await self._async_content_status_filter_request(
            url,
            _type="DataAsset",
            _gen_output=self._generate_referenceable_output,
            filter_string=category,
            content_status_list=content_status_list,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_data_assets_by_category(
        self,
        category: str,
        content_status_list: list[str] = ["ACTIVE"],
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ContentStatusFilterRequestBody] = None,
    ) -> list | str:
        """
        Returns the list of data assets matching the category and optional content status. Sync version.

        Parameters
        ----------
        category: str
            - category name to filter by
        content_status_list: list[str], default = ["ACTIVE"]
            - optional content status list to filter by
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | ContentStatusFilterRequestBody, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - a list of data assets or a string message if no assets are found

        Note:
        -----
        Sample body:
        {
          "class" : "ContentStatusFilterRequestBody",
          "filter" : "xxx",
          "contentStatusList" : ["ACTIVE"],
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_data_assets_by_category(
                category, content_status_list, start_from, page_size, output_format, report_spec, body
            )
        )

    #
    # Infrastructure Methods
    #

    @dynamic_catch
    async def _async_find_infrastructure(
        self,
        search_string: str = "*",
        deployment_status_list: list[str] = ["ACTIVE"],
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtypes: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | DeploymentStatusSearchString] = None,
    ) -> list | str:
        """
        Returns the list of infrastructure assets matching the search string and optional deployment status. Async version.

        Parameters
        ----------
        search_string: str, default = "*"
            - the search string to use to find matching infrastructure assets
        deployment_status_list: list[str], default = ["ACTIVE"]
            - optional deployment status list to filter by
        starts_with: bool, default = False
            - if True, the search string must match the start of the property value
        ends_with: bool, default = False
            - if True, the search string must match the end of the property value
        ignore_case: bool, default = True
            - if True, the search is case-insensitive
        anchor_domain: str, optional
            - optional anchor domain filter
        metadata_element_type: str, optional
            - optional metadata element type filter
        metadata_element_subtypes: list[str], optional
            - optional metadata element subtypes filter
        skip_relationships: list[str], optional
            - relationships to skip
        include_only_relationships: list[str], optional
            - relationships to include
        skip_classified_elements: list[str], optional
            - classifications to skip
        include_only_classified_elements: list[str], optional
            - classifications to include
        graph_query_depth: int, default = 3
            - depth for relationship traversal
        governance_zone_filter: list[str], optional
            - governance zone filter
        as_of_time: str, optional
            - as-of time filter
        effective_time: str, optional
            - effective time filter
        relationship_page_size: int, default = 0
            - page size for relationships
        limit_results_by_status: list[str], optional
            - status filter for results
        sequencing_order: str, optional
            - sequencing order for results
        sequencing_property: str, optional
            - sequencing property for results
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output
        report_spec: str | dict, optional
            - the report specification
        body: dict | DeploymentStatusSearchString, optional
            - the request body

        Returns
        -------
        list | str
            - a list of infrastructure assets

        Note:
        -----
        Sample body:
        {
          "class" : "DeploymentStatusSearchString",
          "searchString" : "xxx",
          "deploymentStatusList" : ["ACTIVE"],
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        url = f"{self.asset_command_root}/infrastructure-assets/by-search-string"
        return await self._async_deployment_status_search_request(
            url,
            _type="Infrastructure",
            _gen_output=self._generate_referenceable_output,
            search_string=search_string,
            deployment_status_list=deployment_status_list,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            anchor_domain=anchor_domain,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtypes,
            skip_relationships=skip_relationships,
            include_only_relationships=include_only_relationships,
            skip_classified_elements=skip_classified_elements,
            include_only_classified_elements=include_only_classified_elements,
            graph_query_depth=graph_query_depth,
            governance_zone_filter=governance_zone_filter,
            as_of_time=as_of_time,
            effective_time=effective_time,
            relationship_page_size=relationship_page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            start_from=start_from,
            page_size=page_size,
            body=body,
        )

    @dynamic_catch
    def find_infrastructure(
        self,
        search_string: str = "*",
        deployment_status_list: list[str] = ["ACTIVE"],
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtypes: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | DeploymentStatusSearchString] = None,
    ) -> list | str:
        """
        Returns the list of infrastructure assets matching the search string and optional deployment status. Sync version.

        Parameters
        ----------
        search_string: str, default = "*"
            - the search string to use to find matching infrastructure assets
        deployment_status_list: list[str], default = ["ACTIVE"]
            - optional deployment status list to filter by
        starts_with: bool, default = False
            - if True, the search string must match the start of the property value
        ends_with: bool, default = False
            - if True, the search string must match the end of the property value
        ignore_case: bool, default = True
            - if True, the search is case-insensitive
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | DeploymentStatusSearchString, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - a list of infrastructure assets or a string message if no assets are found

        Note:
        -----
        Sample body:
        {
          "class" : "DeploymentStatusSearchString",
          "searchString" : "xxx",
          "deploymentStatusList" : ["ACTIVE"],
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_infrastructure(
                search_string,
                deployment_status_list,
                starts_with,
                ends_with,
                ignore_case,
                anchor_domain,
                metadata_element_type,
                metadata_element_subtypes,
                skip_relationships,
                include_only_relationships,
                skip_classified_elements,
                include_only_classified_elements,
                graph_query_depth,
                governance_zone_filter,
                as_of_time,
                effective_time,
                relationship_page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                start_from,
                page_size,
                output_format,
                report_spec,
                body,
            )
        )

    @dynamic_catch
    async def _async_get_infrastructure_by_category(
        self,
        category: str,
        deployment_status_list: list[str] = ["ACTIVE"],
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | DeploymentStatusFilterRequestBody] = None,
    ) -> list | str:
        """
        Returns the list of infrastructure assets matching the category and optional deployment status. Async version.

        Parameters
        ----------
        category: str
            - the category to filter by
        deployment_status_list: list[str], default = ["ACTIVE"]
            - optional deployment status list to filter by
        start_from: int, default = 0
            - starting point in the results
        page_size: int, default = 0
            - maximum results per page
        output_format: str, default = "JSON"
            - format of the output
        report_spec: str | dict, optional
            - report specification
        body: dict | DeploymentStatusFilterRequestBody, optional
            - the request body

        Returns
        -------
        list | str
            - a list of infrastructure assets

        Note:
        -----
        Sample body:
        {
          "class" : "DeploymentStatusFilterRequestBody",
          "filter" : "xxx",
          "deploymentStatusList" : ["ACTIVE"],
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        url = f"{self.asset_command_root}/infrastructure-assets/by-category"
        return await self._async_deployment_status_filter_request(
            url,
            _type="Infrastructure",
            _gen_output=self._generate_referenceable_output,
            filter_string=category,
            deployment_status_list=deployment_status_list,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_infrastructure_by_category(
        self,
        category: str,
        deployment_status_list: list[str] = ["ACTIVE"],
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | DeploymentStatusFilterRequestBody] = None,
    ) -> list | str:
        """
        Returns the list of infrastructure assets matching the category and optional deployment status. Sync version.

        Parameters
        ----------
        category: str
            - category name to filter by
        deployment_status_list: list[str], default = ["ACTIVE"]
            - optional deployment status list to filter by
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | DeploymentStatusFilterRequestBody, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - a list of infrastructure assets or a string message if no assets are found

        Note:
        -----
        Sample body:
        {
          "class" : "DeploymentStatusFilterRequestBody",
          "filter" : "xxx",
          "deploymentStatusList" : ["ACTIVE"],
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_infrastructure_by_category(
                category, deployment_status_list, start_from, page_size, output_format, report_spec, body
            )
        )

    #
    # Process Methods
    #

    @dynamic_catch
    async def _async_find_processes(
        self,
        search_string: str = "*",
        activity_status_list: list[str] = [],
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtypes: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ActivityStatusSearchString] = None,
    ) -> list | str:
        """
        Retrieve the processes that match the search string and activity status. Async version.

        Parameters
        ----------
        search_string: str, default = "*"
            - search string for process properties
        activity_status_list: list[str], default = ["IN_PROGRESS"]
            - optional activity status list to filter by
        starts_with: bool, default = False
        ends_with: bool, default = False
        ignore_case: bool, default = True
        start_from: int, default = 0
        page_size: int, default = 0
        output_format: str, default = "JSON"
        report_spec: str | dict, optional
        body: dict | ActivityStatusSearchString, optional

        Returns
        -------
        list | str
            - list of processes

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusSearchString",
          "searchString" : "xxx",
          "activityStatusList" : ["IN_PROGRESS"],
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        url = f"{self.asset_command_root}/processes/find-by-search-string"
        return await self._async_activity_status_search_request(
            url,
            _type="Process",
            _gen_output=self._generate_referenceable_output,
            search_string=search_string,
            activity_status_list=activity_status_list,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            anchor_domain=anchor_domain,
            metadata_element_type=metadata_element_type,
            metadata_element_subtypes=metadata_element_subtypes,
            skip_relationships=skip_relationships,
            include_only_relationships=include_only_relationships,
            skip_classified_elements=skip_classified_elements,
            include_only_classified_elements=include_only_classified_elements,
            graph_query_depth=graph_query_depth,
            governance_zone_filter=governance_zone_filter,
            as_of_time=as_of_time,
            effective_time=effective_time,
            relationship_page_size=relationship_page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            start_from=start_from,
            page_size=page_size,
            body=body,
        )

    @dynamic_catch
    def find_processes(
        self,
        search_string: str = "*",
        activity_status_list: list[str] = ["IN_PROGRESS"],
        starts_with: bool = False,
        ends_with: bool = False,
        ignore_case: bool = True,
        anchor_domain: Optional[str] = None,
        metadata_element_type: Optional[str] = None,
        metadata_element_subtypes: Optional[list[str]] = None,
        skip_relationships: Optional[list[str]] = None,
        include_only_relationships: Optional[list[str]] = None,
        skip_classified_elements: Optional[list[str]] = None,
        include_only_classified_elements: Optional[list[str]] = None,
        graph_query_depth: int = 3,
        governance_zone_filter: Optional[list[str]] = None,
        as_of_time: Optional[str] = None,
        effective_time: Optional[str] = None,
        relationship_page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ActivityStatusSearchString] = None,
    ) -> list | str:
        """
        Retrieve the processes that match the search string and activity status. Sync version.

        Parameters
        ----------
        search_string: str, default = "*"
            - the search string to use to find matching processes
        activity_status_list: list[str], default = ["IN_PROGRESS"]
            - optional activity status list to filter by
        starts_with: bool, default = False
            - if True, the search string must match the start of the property value
        ends_with: bool, default = False
            - if True, the search string must match the end of the property value
        ignore_case: bool, default = True
            - if True, the search is case-insensitive
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | ActivityStatusSearchString, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - a list of processes or a string message if no processes are found

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusSearchString",
          "searchString" : "xxx",
          "activityStatusList" : ["IN_PROGRESS"],
          "startsWith" : false,
          "endsWith" : false,
          "ignoreCase" : true,
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_find_processes(
                search_string,
                activity_status_list,
                starts_with,
                ends_with,
                ignore_case,
                anchor_domain,
                metadata_element_type,
                metadata_element_subtypes,
                skip_relationships,
                include_only_relationships,
                skip_classified_elements,
                include_only_classified_elements,
                graph_query_depth,
                governance_zone_filter,
                as_of_time,
                effective_time,
                relationship_page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                start_from,
                page_size,
                output_format,
                report_spec,
                body,
            )
        )

    @dynamic_catch
    async def _async_get_processes_by_category(
        self,
        category: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ActivityStatusFilterRequestBody] = None,
    ) -> list | str:
        """
        Retrieve the processes that match the category name and status. Async version.

        Parameters
        ----------
        category: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        start_from: int, default = 0
        page_size: int, default = 0
        output_format: str, default = "JSON"
        report_spec: str | dict, optional
        body: dict | ActivityStatusFilterRequestBody, optional

        Returns
        -------
        list | str
            - list of processes

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusFilterRequestBody",
          "filter" : "xxx",
          "activityStatusList" : ["IN_PROGRESS"],
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        url = f"{self.asset_command_root}/processes/by-category"
        return await self._async_activity_status_filter_request(
            url,
            _type="Process",
            _gen_output=self._generate_referenceable_output,
            filter_string=category,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_processes_by_category(
        self,
        category: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict = None,
        body: Optional[dict | ActivityStatusFilterRequestBody] = None,
    ) -> list | str:
        """
        Retrieve the processes that match the category name and status. Sync version.

        Parameters
        ----------
        category: str
            - category name to filter by
        activity_status_list: list[str], default = ["IN_PROGRESS"]
            - optional activity status list to filter by
        start_from: int, default = 0
            - the starting point in the results list
        page_size: int, default = 0
            - the maximum number of results to return
        output_format: str, default = "JSON"
            - the format of the output (JSON, DICT, etc.)
        report_spec: str | dict, optional
            - the report specification to use for the output
        body: dict | ActivityStatusFilterRequestBody, optional
            - the request body to use for the request. If specified, this takes precedence over other parameters.

        Returns
        -------
        list | str
            - list of processes

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusFilterRequestBody",
          "filter" : "xxx",
          "activityStatusList" : ["IN_PROGRESS"],
          "startFrom" : 0,
          "pageSize": 0
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_processes_by_category(
                category, activity_status_list, start_from, page_size, output_format, report_spec, body
            )
        )

    #
    # Action Methods
    #

    @dynamic_catch
    async def _async_create_action(
        self, body: dict | ActionRequestBody
    ) -> str:
        """
        Create a new action and link it to the supplied actor and targets (if applicable). Async version.

        Parameters
        ----------
        body: dict | ActionRequestBody
            - properties of the action

        Returns
        -------
        str
            - unique identifier of the action

        Note:
        -----
        Sample body:
        {
          "class" : "ActionRequestBody",
          "initialClassifications" : {
            "ZoneMembership" : {
              "class" : "ZoneMembershipProperties",
              "zoneMembership" : "governance"
            }
          },
          "newActionTargets" : [
            {
              "actionTargetGUID" : "add guid here",
              "actionTargetName": "add name here"
            }
          ],
          "properties" : {
            "class" : "ToDoProperties",
            "qualifiedName": "",
            "identifier": "",
            "displayName": "",
            "description": "",
            "versionIdentifier": "",
            "category": "",
            "url": "",
            "resourceName": "",
            "namespace": "",
            "deployedImplementationType": "",
            "source": "",
            "expectedBehaviour": "",
            "requestedTime": "{{$isoTimestamp}}",
            "requestedStartTime": "{{$isoTimestamp}}",
            "startTime": "{{$isoTimestamp}}",
            "dueTime": "{{$isoTimestamp}}",
            "lastReviewTime": "{{$isoTimestamp}}",
            "lastPauseTime": "{{$isoTimestamp}}",
            "lastResumeTime": "{{$isoTimestamp}}",
            "completionTime": "{{$isoTimestamp}}",
            "priority": 0,
            "formula": "",
            "formulaType": "",
            "activityStatus": "REQUESTED",
            "userDefinedActivityStatus": "",
            "situation": "",
            "additionalProperties" : {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "originatorGUID" : "add guid of requester (ActionRequester relationship)",
          "actionSponsorGUID" : "add guid of sponsor (Actions relationship)",
          "assignToActorGUID" : "add guid of actor that will be assigned this action (AssignmentScope relationship)"
        }
        """
        url = f"{self.asset_command_root}/actions"

        if isinstance(body, ActionRequestBody):
            validated_body = body
        else:
            validated_body = self._action_request_adapter.validate_python(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True, by_alias=True)
        response = await self._async_make_request("POST", url, json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_action(self, body: dict | ActionRequestBody) -> str:
        """
        Create a new action and link it to the supplied actor and targets (if applicable). Sync version.

        Parameters
        ----------
        body: dict | ActionRequestBody
            - properties of the action

        Returns
        -------
        str
            - unique identifier of the action

        Note:
        -----
        Sample body:
        {
          "class" : "ActionRequestBody",
          "initialClassifications" : {
            "ZoneMembership" : {
              "class" : "ZoneMembershipProperties",
              "zoneMembership" : "governance"
            }
          },
          "newActionTargets" : [
            {
              "actionTargetGUID" : "add guid here",
              "actionTargetName": "add name here"
            }
          ],
          "properties" : {
            "class" : "ToDoProperties",
            "qualifiedName": "",
            "identifier": "",
            "displayName": "",
            "description": "",
            "versionIdentifier": "",
            "category": "",
            "url": "",
            "resourceName": "",
            "namespace": "",
            "deployedImplementationType": "",
            "source": "",
            "expectedBehaviour": "",
            "requestedTime": "{{$isoTimestamp}}",
            "requestedStartTime": "{{$isoTimestamp}}",
            "startTime": "{{$isoTimestamp}}",
            "dueTime": "{{$isoTimestamp}}",
            "lastReviewTime": "{{$isoTimestamp}}",
            "lastPauseTime": "{{$isoTimestamp}}",
            "lastResumeTime": "{{$isoTimestamp}}",
            "completionTime": "{{$isoTimestamp}}",
            "priority": 0,
            "formula": "",
            "formulaType": "",
            "activityStatus": "REQUESTED",
            "userDefinedActivityStatus": "",
            "situation": "",
            "additionalProperties" : {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            }
          },
          "originatorGUID" : "add guid of requester (ActionRequester relationship)",
          "actionSponsorGUID" : "add guid of sponsor (Actions relationship)",
          "assignToActorGUID" : "add guid of actor that will be assigned this action (AssignmentScope relationship)"
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_create_action(body))

    @dynamic_catch
    async def _async_add_action_target(
        self,
        action_guid: str,
        metadata_element_guid: str,
        body: dict | NewRelationshipRequestBody | None = None,
    ) -> str:
        """
        Add an element to an action's workload. Async version.

        Parameters
        ----------
        action_guid: str
            - unique identifier of the action
        metadata_element_guid: str
            - unique identifier of the metadata element that is a target
        body: dict | NewRelationshipRequestBody, optional

        Returns
        -------
        str
            - unique identifier of the relationship

        Note:
        -----
        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
          "properties" : {
             "class": "ActionTargetProperties",
             "activityStatus" : "IN_PROGRESS",
             "actionTargetName" : "add label here"
          }
        }
        """
        url = f"{self.asset_command_root}/actions/{action_guid}/action-targets/{metadata_element_guid}/attach"

        if isinstance(body, NewRelationshipRequestBody):
            validated_body = body
        elif isinstance(body, dict):
            validated_body = self._new_relationship_request_adapter.validate_python(body)
        else:
            validated_body = NewRelationshipRequestBody(class_="NewRelationshipRequestBody")

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True, by_alias=True)
        response = await self._async_make_request("POST", url, json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def add_action_target(
        self,
        action_guid: str,
        metadata_element_guid: str,
        body: dict | NewRelationshipRequestBody | None = None,
    ) -> str:
        """
        Add an element to an action's workload. Sync version.

        Parameters
        ----------
        action_guid: str
            - unique identifier of the action
        metadata_element_guid: str
            - unique identifier of the metadata element that is a target
        body: dict | NewRelationshipRequestBody, optional

        Returns
        -------
        str
            - unique identifier of the relationship

        Note:
        -----
        Sample body:
        {
          "class" : "NewRelationshipRequestBody",
           "properties" : {
             "class": "ActionTargetProperties",
             "activityStatus" : "IN_PROGRESS",
             "actionTargetName" : "add label here",
             "startTime" : "{{$isoTimestamp}}",
             "completionTime" : "{{$isoTimestamp}}",
             "completionMessage" : "Add message here"
          },
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_add_action_target(action_guid, metadata_element_guid, body)
        )

    @dynamic_catch
    async def _async_update_action_target_properties(
        self,
        action_target_guid: str,
        body: dict | UpdateRelationshipRequestBody,
    ) -> None:
        """
        Update the properties associated with an Action Target for an action. Async version.

        Parameters
        ----------
        action_target_guid: str
            - unique identifier of the action target relationship
        body: dict | UpdateRelationshipRequestBody

        Returns
        -------
        None
        """
        url = f"{self.asset_command_root}/actions/action-targets/{action_target_guid}/update"

        if isinstance(body, UpdateRelationshipRequestBody):
            validated_body = body
        else:
            validated_body = self._update_relationship_request_adapter.validate_python(body)

        json_body = validated_body.model_dump_json(indent=2, exclude_none=True, by_alias=True)
        await self._async_make_request("POST", url, json_body)

    @dynamic_catch
    def update_action_target_properties(
        self,
        action_target_guid: str,
        body: dict | UpdateRelationshipRequestBody,
    ) -> None:
        """
        Update the properties associated with an Action Target for an action. Sync version.

        Parameters
        ----------
        action_target_guid: str
            - unique identifier of the action target relationship
        body: dict | UpdateRelationshipRequestBody

        Returns
        -------
        None

        Note:
        -----
        Sample body:
        {
          "class" : "UpdateRelationshipRequestBody",
          "properties": {
            "class": "ActionTargetProperties",
             "activityStatus" : "IN_PROGRESS",
             "actionTargetName" : "add label here",
             "startTime" : "{{$isoTimestamp}}",
             "completionTime" : "{{$isoTimestamp}}",
             "completionMessage" : "Add message here"
          },
          "mergeUpdate": true,
          "externalSourceGUID": "",
          "externalSourceName": "",
          "forLineage": false,
          "forDuplicateProcessing": true,
          "effectiveTime": "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_action_target_properties(action_target_guid, body)
        )

    @dynamic_catch
    async def _async_get_action_target(
        self,
        action_target_guid: str,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve a specific action target associated with an action. Async version.

        Parameters
        ----------
        action_target_guid: str
        body: dict | GetRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str
        """
        url = f"{self.asset_command_root}/actions/action-targets/{action_target_guid}/retrieve"

        return await self._async_get_guid_request(
            url,
            _type="ActionTarget",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_action_target(
        self,
        action_target_guid: str,
        body: dict | GetRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve a specific action target associated with an action. Sync version.

        Parameters
        ----------
        action_target_guid: str
        body: dict | GetRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str

        Note:
        -----
        Sample body:
        {
          "class" : "GetRequestBody",
          "asOfTime" : "{{$isoTimestamp}}",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_action_target(action_target_guid, body, output_format, report_spec)
        )

    @dynamic_catch
    async def _async_get_action_targets(
        self,
        action_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Return a list of elements that are target elements for an action. Async version.

        Parameters
        ----------
        action_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str
        """
        url = f"{self.asset_command_root}/actions/{action_guid}/action-targets"
        return await self._async_activity_status_request(
            url,
            _type="ActionTarget",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_action_targets(
        self,
        action_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Return a list of elements that are target elements for an action. Sync version.

        Parameters
        ----------
        action_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        start_from: int, default = 0
        page_size: int, default = 0
        limit_results_by_status: list[str], optional
        sequencing_order: str, optional
        sequencing_property: str, optional
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusRequestBody",
          "activityStatusList": ["IN_PROGRESS"]
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_action_targets(
                action_guid,
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
            )
        )

    @dynamic_catch
    async def _async_get_actions_for_action_target(
        self,
        metadata_element_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the "Actions" that are chained off of an action target element. Async version.

        Parameters
        ----------
        metadata_element_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str
        """
        url = f"{self.asset_command_root}/elements/{metadata_element_guid}/action-targets/actions"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_actions_for_action_target(
        self,
        metadata_element_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the "Actions" that are chained off of an action target element. Sync version.

        Parameters
        ----------
        metadata_element_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        start_from: int, default = 0
        page_size: int, default = 0
        limit_results_by_status: list[str], optional
        sequencing_order: str, optional
        sequencing_property: str, optional
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusRequestBody",
          "activityStatusList": ["IN_PROGRESS"]
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actions_for_action_target(
                metadata_element_guid,
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
            )
        )

    @dynamic_catch
    async def _async_assign_action(
        self,
        action_guid: str,
        actor_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """
        Assign an action to an actor. Request body is optional. Async version.

        Parameters
        ----------
        action_guid: str
            - unique identifier of the action
        actor_guid: str
            - actor to assign the action to
        body: dict | NewRelationshipRequestBody, optional
            - request body
        """
        url = f"{self.asset_command_root}/actions/{action_guid}/assign/{actor_guid}"

        await self._async_new_relationship_request(url, prop=["AssignmentScopeProperties"], body=body)

    @dynamic_catch
    def assign_action(
        self,
        action_guid: str,
        actor_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """
        Assign an action to an actor. Sync version.

        Parameters
        ----------
        action_guid: str
            - unique identifier of the action
        actor_guid: str
            - actor to assign the action to
        body: dict | NewRelationshipRequestBody, optional
            - request body

        Note:
        -----
        Sample body:
        {
           "class" : "NewRelationshipRequestBody",
           "properties" : {
             "class": "AssignmentScopeProperties",
             "label" : "add label here",
             "description" : "Add description here"
          },
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_assign_action(action_guid, actor_guid, body))

    @dynamic_catch
    async def _async_reassign_action(
        self,
        action_guid: str,
        actor_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """
        Assign an action to a new actor. This will unassign all other actors previously assigned to the action. Async version.

        Parameters
        ----------
        action_guid: str
        actor_guid: str
        body: dict | NewRelationshipRequestBody, optional
        """
        url = f"{self.asset_command_root}/actions/{action_guid}/reassign/{actor_guid}"

        await self._async_new_relationship_request(url, prop=["AssignmentScopeProperties"], body=body)

    @dynamic_catch
    def reassign_action(
        self,
        action_guid: str,
        actor_guid: str,
        body: Optional[dict | NewRelationshipRequestBody] = None,
    ) -> None:
        """
        Assign an action to a new actor. Sync version.

        Parameters
        ----------
        action_guid: str
        actor_guid: str
        body: dict | NewRelationshipRequestBody, optional

        Note:
        -----
        Sample body:
        {
           "class" : "NewRelationshipRequestBody",
           "properties" : {
             "class": "AssignmentScopeProperties",
             "label" : "add label here",
             "description" : "Add description here"
          },
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_reassign_action(action_guid, actor_guid, body))

    @dynamic_catch
    async def _async_unassign_action(
        self,
        action_guid: str,
        actor_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """
        Remove an action from an actor. Async version.

        Parameters
        ----------
        action_guid: str
        actor_guid: str
        body: dict | DeleteRelationshipRequestBody, optional
        """
        url = f"{self.asset_command_root}/actions/{action_guid}/reassign/{actor_guid}"

        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def unassign_action(
        self,
        action_guid: str,
        actor_guid: str,
        body: Optional[dict | DeleteRelationshipRequestBody] = None,
    ) -> None:
        """
        Remove an action from an actor. Sync version.

        Parameters
        ----------
        action_guid: str
        actor_guid: str
        body: dict | DeleteRelationshipRequestBody, optional

        Note:
        -----
        Sample body:
        {
           "class" : "DeleteRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_unassign_action(action_guid, actor_guid, body))

    @dynamic_catch
    async def _async_get_assigned_actions(
        self,
        actor_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the actions for a particular actor. Async version.

        Parameters
        ----------
        actor_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str
        """
        url = f"{self.asset_command_root}/actors/{actor_guid}/assigned/actions"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_assigned_actions(
        self,
        actor_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the actions for a particular actor. Sync version.

        Parameters
        ----------
        actor_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        start_from: int, default = 0
        page_size: int, default = 0
        limit_results_by_status: list[str], optional
        sequencing_order: str, optional
        sequencing_property: str, optional
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusRequestBody",
          "activityStatusList": ["IN_PROGRESS"]
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_assigned_actions(
                actor_guid,
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
            )
        )

    @dynamic_catch
    async def _async_get_actions_for_sponsor(
        self,
        metadata_element_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the "Actions" that are chained off of a sponsor's element. Async version.

        Parameters
        ----------
        metadata_element_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str
        """
        url = f"{self.asset_command_root}/elements/{metadata_element_guid}/sponsored/actions"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_actions_for_sponsor(
        self,
        metadata_element_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the "Actions" that are chained off of a sponsor's element. Sync version.

        Parameters
        ----------
        metadata_element_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        start_from: int, default = 0
        page_size: int, default = 0
        limit_results_by_status: list[str], optional
        sequencing_order: str, optional
        sequencing_property: str, optional
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusRequestBody",
          "activityStatusList": ["IN_PROGRESS"]
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actions_for_sponsor(
                metadata_element_guid,
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
            )
        )

    @dynamic_catch
    async def _async_get_actions_for_requestor(
        self,
        metadata_element_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the "Actions" that are chained off of a requestor's element. Async version.

        Parameters
        ----------
        metadata_element_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str
        """
        url = f"{self.asset_command_root}/elements/{metadata_element_guid}/requested/actions"
        return await self._async_activity_status_request(
            url,
            _type="Action",
            _gen_output=self._generate_referenceable_output,
            activity_status_list=activity_status_list,
            start_from=start_from,
            page_size=page_size,
            limit_results_by_status=limit_results_by_status,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_actions_for_requestor(
        self,
        metadata_element_guid: str,
        activity_status_list: list[str] = ["IN_PROGRESS"],
        start_from: int = 0,
        page_size: int = 0,
        limit_results_by_status: Optional[list[str]] = None,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        body: dict | ActivityStatusRequestBody | None = None,
        output_format: str = "JSON",
        report_spec: str | dict = None,
    ) -> list | dict | str:
        """
        Retrieve the "Actions" that are chained off of a requestor's element. Sync version.

        Parameters
        ----------
        metadata_element_guid: str
        activity_status_list: list[str], default = ["IN_PROGRESS"]
        start_from: int, default = 0
        page_size: int, default = 0
        limit_results_by_status: list[str], optional
        sequencing_order: str, optional
        sequencing_property: str, optional
        body: dict | ActivityStatusRequestBody, optional
        output_format: str, default = "JSON"
        report_spec: str | dict, optional

        Returns
        -------
        list | dict | str

        Note:
        -----
        Sample body:
        {
          "class" : "ActivityStatusRequestBody",
          "activityStatusList": ["IN_PROGRESS"]
        }
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_actions_for_requester(
                metadata_element_guid,
                activity_status_list,
                start_from,
                page_size,
                limit_results_by_status,
                sequencing_order,
                sequencing_property,
                body,
                output_format,
                report_spec,
            )
        )


    def _generate_referenceable_output(
        self,
        elements: list | dict,
        search_string: Optional[str] = None,
        element_type_name: Optional[str] = None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
        **kwargs
    ):
        """Helper to generate output for referenceable elements."""
        return self._generate_formatted_output(
            elements=elements,
            query_string=search_string,
            entity_type=element_type_name or "Asset",
            output_format=output_format,
            extract_properties_func=self._extract_referenceable_properties,
            report_spec=report_spec,
            **kwargs
        )
