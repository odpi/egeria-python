"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the Asset Maker OMVS module.
The Asset Maker OMVS provides APIs for supporting the creation and editing of assets.

"""

import asyncio

from pyegeria.core._server_client import ServerClient
from pyegeria.core._globals import max_paging_size
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
)
from pyegeria.core.utils import dynamic_catch

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
                filter_string, body, start_from, page_size, output_format, report_spec
            )
        )

    @dynamic_catch
    async def _async_find_assets(self, search_string: str = "*", starts_with: bool = False, ends_with: bool = False,
                                 ignore_case: bool = True, anchor_domain: str = None, metadata_element_type: str = None,
                                 metadata_element_subtypes: list[str] = None, skip_relationships: list[str] = None,
                                 include_only_relationships: list[str] = None,
                                 skip_classified_elements: list[str] = None,
                                 include_only_classified_elements: list[str] = None, graph_query_depth: int = 3,
                                 governance_zone_filter: list[str] = None, as_of_time: str = None,
                                 effective_time: str = None, relationship_page_size: int = 0,
                                 limit_results_by_status: list[str] = None, sequencing_order: str = None,
                                 sequencing_property: str = None, output_format: str = "DICT",
                                 report_spec: dict | str | None = None, start_from: int = 0,
                                 page_size: int = 0, property_names: list[str] = None,
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
                    ignore_case: bool = True, anchor_domain: str = None, metadata_element_type: str = None,
                    metadata_element_subtypes: list[str] = None, skip_relationships: list[str] = None,
                    include_only_relationships: list[str] = None, skip_classified_elements: list[str] = None,
                    include_only_classified_elements: list[str] = None, graph_query_depth: int = 3,
                    governance_zone_filter: list[str] = None, as_of_time: str = None, effective_time: str = None,
                    relationship_page_size: int = 0, limit_results_by_status: list[str] = None,
                    sequencing_order: str = None, sequencing_property: str = None, output_format: str = "DICT",
                    report_spec: dict | str | None = None, start_from: int = 0, page_size: int = 0,
                    property_names: list[str] = None, body: dict | SearchStringRequestBody | None = None) -> list | dict | str:
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
        body: dict | GetRequestBody | None = None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str:
        """Return the properties of a specific asset. Async version.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset.
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
            _type="Asset",
            _gen_output=self._generate_referenceable_output,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
        )

    @dynamic_catch
    def get_asset_by_guid(
        self,
        asset_guid: str,
        body: dict | GetRequestBody | None = None,
        output_format: str = "DICT",
        report_spec: dict | str | None = None,
    ) -> dict | str:
        """Return the properties of a specific asset.

        Parameters
        ----------
        asset_guid: str
            Unique identifier of the asset.
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
            self._async_get_asset_by_guid(asset_guid, body, output_format, report_spec)
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