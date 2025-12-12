"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the classification_manager_omvs module.

"""

import asyncio
from datetime import datetime

from httpx import Response
from loguru import logger

from pyegeria._exceptions import PyegeriaException, PyegeriaInvalidParameterException
from pyegeria._server_client import ServerClient
from pyegeria._globals import default_time_out, NO_ELEMENTS_FOUND
from pyegeria.base_report_formats import select_report_spec, get_report_spec_match
from pyegeria.models import LevelIdentifierQueryBody, FilterRequestBody, GetRequestBody, NewClassificationRequestBody, \
    DeleteClassificationRequestBody, NewRelationshipRequestBody, DeleteRelationshipRequestBody, \
    UpdateRelationshipRequestBody
from pyegeria.output_formatter import (
    generate_output,
    _extract_referenceable_properties,
    populate_columns_from_properties,
    get_required_relationships,
)
from pyegeria.utils import body_slimmer, dynamic_catch


def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


"params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to the query string"


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result


def base_path(client, view_server: str):
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/classification-manager"


class ClassificationManager(ServerClient):
    """ClassificationManager is a class that extends the Client class. It
    provides methods to CRUD annotations and to query elements and relationships. Async version.

    Attributes:

        server_name: str
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
            user_id: str = None,
            user_pwd: str = None,
            token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.classification_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/classification-manager"
        )
        ServerClient.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )

        # Default entity label for formatter when not specified
        self.REFERENCEABLE_LABEL = "Referenceable"

    @dynamic_catch
    def _extract_referenceable_output_properties(self, element: dict, columns_struct: dict) -> dict:
        """Populate requested columns from a generic Referenceable element.
        Tolerant of missing values; fills from properties, header, relationships, and mermaid graph.
        """
        col_data = populate_columns_from_properties(element, columns_struct)
        columns_list = col_data.get("formats", {}).get("attributes", [])

        # Header-derived fields (GUID, qualifiedName, displayName, etc.)
        header_props = _extract_referenceable_properties(element)
        for col in columns_list:
            key = col.get("key")
            if key in header_props:
                col["value"] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == "guid":
                col["value"] = header_props.get("GUID")

        # Relationships (generic handler fills requested relationship-driven columns if present in format set)
        col_data = get_required_relationships(element, col_data)

        # Mermaid graph support if present
        mermaid_val = element.get("mermaidGraph", "") or ""
        for col in columns_list:
            if col.get("key") == "mermaid":
                col["value"] = mermaid_val
                break

        return col_data

    @dynamic_catch
    def _generate_referenceable_output(self,
                                       elements: dict | list[dict],
                                       filter: str | None,
                                       element_type_name: str | None,
                                       output_format: str = "DICT",
                                       report_spec: dict | str | None = None) -> str | list[dict]:
        """Resolve format set and generate output for Referenceable-derived elements."""
        entity_type = element_type_name or self.REFERENCEABLE_LABEL

        # Resolve output format set
        get_additional_props_func = None
        if report_spec:
            if isinstance(report_spec, str):
                output_formats = select_report_spec(report_spec, output_format)
            else:
                output_formats = get_report_spec_match(report_spec, output_format)
        elif element_type_name:
            output_formats = select_report_spec(element_type_name, output_format)
        else:
            output_formats = select_report_spec(entity_type, output_format)

        if output_formats is None:
            output_formats = select_report_spec("Default", output_format)

        # Optional hook: allow format set to specify an enrichment method on this class
        get_additional_props_name = (
            output_formats.get("get_additional_props", {}).get("function") if output_formats else None
        )
        if isinstance(get_additional_props_name, str):
            method_name = get_additional_props_name.split(".")[-1]
            if hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)

        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_referenceable_output_properties,
            get_additional_props_func,
            output_formats,
        )

    #
    #   Get elements
    #
    @dynamic_catch
    async def _async_get_classified_elements_by(
            self,
            classification_name: str,
            body: dict | LevelIdentifierQueryBody,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the specified classification. Async version.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        classification_name: str
            One of impact, confidence, criticality, confidentiality, retention
        body: dict | LevelIdentifierQueryBody
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "LevelIdentifierQueryProperties",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT",
            "returnSpecificLevel": true,
            "levelIdentifier": 3
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/by-{classification_name}")

        response = await self._async_get_level_identifier_query_body_request(
            url=url, _gen_output=self._generate_referenceable_output, output_format=output_format,
            report_spec=report_spec, body=body
        )
        return response

    @dynamic_catch
    def get_classified_elements_by(
            self,
            classification_name: str,
            body: dict | LevelIdentifierQueryBody,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the specified classification.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        classification_name: str
            One of impact, confidence, criticality, confidentiality, retention
        body: dict | LevelIdentifierQueryBody
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "LevelIdentifierQueryProperties",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT",
            "returnSpecificLevel": true,
            "levelIdentifier": 3
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_classified_elements_by(
                classification_name, body, output_format, report_spec
            )
        )
        return response

    @dynamic_catch
    async def _async_get_security_tagged_elements(
            self,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the security tags classification. Async version.
        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "SecurityTagQueryProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "securityLabels" : [ "???" ],
            "securityProperties" : {
               "propertyName" : "propertyValue"
            },
            "accessGroups" : {
                "groupName" : [ "???" ]
            }
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/by-security-tags")

        response = await self._async_make_request("POST", url, body_slimmer(body))
        elements = response.json().get("elements", None)
        if elements is None:
            elements = response.json().get("element", NO_ELEMENTS_FOUND)

        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "", "Referenceable",
                                                       output_format, report_spec)
        return elements

    @dynamic_catch
    def get_security_tagged_elements(
            self,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the specified classification.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        body: dict
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "SecurityTagQueryProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "securityLabels" : [ "???" ],
            "securityProperties" : {
               "propertyName" : "propertyValue"
            },
            "accessGroups" : {
                "groupName" : [ "???" ]
            }
        }
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_security_tagged_elements(
                body, output_format, report_spec
            )
        )
        return response

    @dynamic_catch
    async def _async_get_owners_elements(
            self,
            owner_name: str,
            body: dict | FilterRequestBody = None,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the ownership classification. Async version.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        owner_name: str
            Name of owner to retrieve elements for.
        body: dict | FilterRequestBody
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "FilterRequestBody",
            "filter": "????",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/by-ownership")

        response = await self._async_get_name_request(url, "Referenceable",
                                                      self._generate_referenceable_output, owner_name,
                                                      None, 0, 0,
                                                      output_format, report_spec, body)
        return response

    @dynamic_catch
    def get_owners_elements(
            self,
            owner_name: str,
body: dict | FilterRequestBody = None,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the ownership classification.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        owner_name: str
            Name of owner to retrieve elements for.
        body: dict | FilterRequestBody
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "FilterRequestBody",
            "filter": "????",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_owners_elements(owner_name, body, output_format, report_spec)
        )
        return response

    @dynamic_catch
    async def _async_get_subject_area_members(
            self,
            subject_area: str,
            body: dict | FilterRequestBody,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the subject area classification. Async version.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        subject_area: str
            Name of subject area to retrieve elements for.
        body: dict | FilterRequestBody
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "FilterRequestBody",
            "filter": "????",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }


        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/by-ownership")

        response = await self._async_get_name_request(url, "Referenceable",
                                                      self._generate_referenceable_output, subject_area,
                                                      None, 0, 0,
                                                      output_format, report_spec, body)
        return response

    @dynamic_catch
    def get_subject_area_members(
            self,
            subject_area: str,
            body: dict | FilterRequestBody,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the elements classified with the subject area classification.

        https://egeria-project.org/types/4/0422-Governed-Data-Classifications/

        Parameters
        ----------
        subject_area: str
            Name of subject area to retrieve elements for.
        body: dict | FilterRequestBody
            Details of the query. See LevelIdentifierQueryBody for details.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "FilterRequestBody",
            "filter": "????",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }



        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_subject_area_members(
                subject_area, body, output_format, report_spec
            )
        )
        return response

    @dynamic_catch
    async def _async_get_elements_by_origin(
            self,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the digital resources from a specific origin. Async version.

        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        ----------

        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "FindDigitalResourceOriginProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "organizationGUID" : "????",
            "businessCapabilityGUID" : "????",
            "otherOriginValues" : {
                 "propertyName" : "propertyValue"
            }
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/by-digital-resource-origin")

        response = await self._async_make_request("POST", url, body_slimmer(body), time_out=default_time_out)
        elements = response.json().get("elements", None)
        if elements is None:
            elements = response.json().get("element", NO_ELEMENTS_FOUND)

        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "", "Referenceable",
                                                       output_format, report_spec)
        return elements

    @dynamic_catch
    def get_elements_by_origin(
            self,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Return information about the digital resources from a specific origin.

        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        ----------

        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "FindDigitalResourceOriginProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "organizationGUID" : "????",
            "businessCapabilityGUID" : "????",
            "otherOriginValues" : {
                 "propertyName" : "propertyValue"
            }
        }


        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_origin(body, output_format, report_spec
                                              )
        )
        return response

    @dynamic_catch
    async def _async_get_meanings(
            self,
            element_guid: str,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Retrieve the glossary terms linked via a "SemanticAssignment" relationship to the requested element. Async version.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "SemanticAssignmentQueryProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "expression" : "????",
            "description" : "????",
            "status" : "VALIDATED",
            "returnSpecificConfidence" : true,
            "confidence" : 100,
            "createdBy" : "???",
            "steward" : "??",
            "source" : "???"

        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/terms/by-semantic-assignment/{element_guid}")

        response = await self._async_make_request("POST", url, body_slimmer(body), time_out=default_time_out)
        elements = response.json().get("elements", None)
        if elements is None:
            elements = response.json().get("element", NO_ELEMENTS_FOUND)

        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "", "Referenceable",
                                                       output_format, report_spec)
        return elements

    @dynamic_catch
    def get_meanings(
            self,
            element_guid: str,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Retrieve the glossary terms linked via a "SemanticAssignment" relationship to the requested element.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "SemanticAssignmentQueryProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "expression" : "????",
            "description" : "????",
            "status" : "VALIDATED",
            "returnSpecificConfidence" : true,
            "confidence" : 100,
            "createdBy" : "???",
            "steward" : "??",
            "source" : "???"

        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_meanings(element_guid, body, output_format, report_spec
                                    )
        )
        return response

    @dynamic_catch
    async def _async_get_semantic_asignees(
            self,
            term_guid: str,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Retrieve the elements linked via a "SemanticAssignment" relationship to the requested glossary term. Async version.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        term_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "SemanticAssignmentQueryProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "expression" : "????",
            "description" : "????",
            "status" : "VALIDATED",
            "returnSpecificConfidence" : true,
            "confidence" : 100,
            "createdBy" : "???",
            "steward" : "??",
            "source" : "???"

        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/by-semantic-assignment/{term_guid}")

        response = await self._async_make_request("POST", url, body_slimmer(body), time_out=default_time_out)
        elements = response.json().get("elements", None)
        if elements is None:
            elements = response.json().get("element", NO_ELEMENTS_FOUND)

        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "", "Referenceable",
                                                       output_format, report_spec)
        return elements

    @dynamic_catch
    def get_semantic_asignees(
            self,
            term_guid: str,
            body: dict,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Retrieve the elements linked via a "SemanticAssignment" relationship to the requested glossary term.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        term_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class" : "SemanticAssignmentQueryProperties",
            "effectiveTime" : "{{$isoTimestamp}}",
            "asOfTime" : "{{$isoTimestamp}}",
            "forLineage" : false,
            "forDuplicateProcessing" : false,
            "metadataElementTypeName" : "GlossaryTerm",
            "limitResultsByStatus" : [ "ACTIVE", "DRAFT"],
            "sequencingProperty" : "???",
            "sequencingOrder" : "LAST_UPDATE_RECENT",
            "expression" : "????",
            "description" : "????",
            "status" : "VALIDATED",
            "returnSpecificConfidence" : true,
            "confidence" : 100,
            "createdBy" : "???",
            "steward" : "??",
            "source" : "???"

        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_semantic_asignees(term_guid, body, output_format, report_spec
                                             )
        )
        return response

    @dynamic_catch
    async def _async_get_governed_elements(
            self,
            gov_def_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
        Retrieve the elements linked via a "governed-by" relationship to the requested governance definition. Async version.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        gov_def_guid: str
            Governance definition linked by governed-by relationship.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/governed-by/{gov_def_guid}")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_governed_elements(
            self,
            gov_def_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
        Retrieve the elements linked via a "governed-by" relationship to the requested governance definition.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        gov_def_guid: str
            Governance definition linked by governed-by relationship.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_governed_elements(gov_def_guid, body, output_format, report_spec,
                                             start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_governed_by_definitions(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
        Retrieve the governance definitions linked via a "governed-by" relationship to the specified element. Async version.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/{element_guid}/governed-by")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_governed_by_definitions(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
        Retrieve the governance definitions linked via a "governed-by" relationship to the specified element.
        https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        __________
        element_guid: str
            element to retrieve governed-by relationship for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_governed_by_definitions(element_guid, body, output_format, report_spec,
                                                   start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_source_elements(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via a SourceFrom relationship to the requested element.
            The elements returned were used to create the requested element.
            Typically only one element is returned.  Async version.

            https://egeria-project.org/types/0/0011-Managing-Referenceables/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/{element_guid}/source")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_source_elements(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via a SourceFrom relationship to the requested element.
            The elements returned were used to create the requested element.
            Typically only one element is returned.  Async version.

            https://egeria-project.org/types/0/0011-Managing-Referenceables/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_certified_elements(element_guid, body, output_format, report_spec, start_from,
                                              page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_elements_sourced_from(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via the SourcedFrom relationship to the requested element. The elements
            returned were created using the requested element as a template.  Async version.

            https://egeria-project.org/types/0/0011-Managing-Referenceables/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/{element_guid}/sourced-from")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_elements_sourced_from(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
          Retrieve the elements linked via the SourcedFrom relationship to the requested element. The elements
            returned were created using the requested element as a template.

            https://egeria-project.org/types/0/0011-Managing-Referenceables/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_sourced_from(element_guid, body, output_format, report_spec,
                                                 start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_scopes(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
        Retrieve the scopes linked via the ScopedBy relationship to the requested element. Async version.
        Scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/{element_guid}/scoped-by")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_scopes(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
        Retrieve the scopes linked via the ScopedBy relationship to the requested element.
        Scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_certified_elements(element_guid, body, output_format, report_spec, start_from,
                                              page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_scoped_elements(
            self,
            scope_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via the ScopedBy relationship to the scope. Async version.
            scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        __________
        scope_guid: str
             Scope to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/scoped-by/{scope_guid}")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_scoped_elements(
            self,
            scope_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
             Retrieve the elements linked via the ScopedBy relationship to the scope. Async version.
            scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        __________
        scope_guid: str
            Scope to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_scoped_elements(scope_guid,body, output_format, report_spec, start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_licensed_elements(
            self,
            license_type_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via a License relationship to the requested LicenseType. Async version.
            https://https://egeria-project.org/types/4/0481-Licenses/
        Parameters
        __________
        license_type_guid: str
            License type to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/licenses/{license_type_guid}")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_licensed_elements(
            self,
            license_type_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via a License relationship to the requested LicenseType.
            https://https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        license_type_guid: str
            License type to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_licensed_elements(license_type_guid, body, output_format, report_spec, start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_licenses(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the license types linked via a License relationship to the requested element. Async version.
            https://https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/{element_guid}/licenses")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_licenses(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the license types linked via a License relationship to the requested element.
            https://https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_licenses(element_guid, body, output_format, report_spec,
                                    start_from, page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_certified_elements(
            self,
            certification_type_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via a Certification relationship to the requested CertificationType. Async version.
            https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        certification_type_guid: str
            Certification type to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/glossaries/elements/certificactions/{certification_type_guid}")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_certified_elements(
            self,
            certification_type_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the elements linked via a Certification relationship to the requested CertificationType. Async version.
            https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        certification_type_guid: str
            Certification type to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_certified_elements(certification_type_guid, body, output_format, report_spec, start_from,
                                              page_size)
        )
        return response

    @dynamic_catch
    async def _async_get_certifications(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the certification types linked via a Certification relationship to the requested element. Async version.
            https://https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/{element_guid}/certifications")

        response = await self._async_get_results_body_request(url, "Referenceable", self._generate_referenceable_output,
                                                              start_from, page_size, output_format,
                                                              report_spec, body)
        return response

    @dynamic_catch
    def get_certifications(
            self,
            element_guid: str,
            body: dict = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            start_from: int = 0,
            page_size: int = 0
    ) -> list | str:
        """
            Retrieve the certification types linked via a Certification relationship to the requested element.
            https://https://egeria-project.org/types/4/0481-Licenses/

        Parameters
        __________
        element_guid: str
            Element to retrieve information for.
        body: dict
            Details of the query.
        output_format: str, default = "JSON"
            Type of output to return.
        report_spec: dict | str, default = None
            Output format set to use. If None, the default output format set is used.
        start_from: int, default = 0
            When multiple pages of results are available, the element number to start from.
        page_size: int, default = 0
            The number of elements returned per page.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:

        {
            "class": "ResultsRequestBody",
            "effectiveTime": "{{$isoTimestamp}}",
            "asOfTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "metadataElementTypeName": "GlossaryTerm",
            "limitResultsByStatus": [ "ACTIVE", "DRAFT"],
            "sequencingProperty": "???",
            "sequencingOrder": "LAST_UPDATE_RECENT"
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_certifications(element_guid, body, output_format, report_spec, start_from,
                                          page_size)
        )
        return response

    #
    #
    #
    async def _async_get_elements(
            self,
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements of the requested type name. If no type name is specified, then any type of element may
        be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = f"{base_path(self, self.view_server)}/elements/by-type"
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements = elements, filter = metadata_element_type_name,
                                                       element_type_name = "Referenceable", output_format=output_format,
                                                       report_spec=report_spec,
                                                       )
        return elements


    def get_elements(
            self,
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements of the requested type name. If no type name is specified, then any type of element may
        be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements(metadata_element_type_name, effective_time, for_lineage, for_duplicate_processing,
                                     start_from, page_size, time_out, output_format, report_spec)
        )

        return response

    async def _async_get_elements_by_property_value(self, property_value: str, property_names: list[str],
                                                    metadata_element_type_name: str = None, effective_time: str = None,
                                                    as_of_time: str = None, for_lineage: bool = None,
                                                     for_duplicate_processing: bool = None,
                                                    start_from: int = 0, page_size: int = 0,
                                                    time_out: int = default_time_out, output_format: str = "JSON",
                                                    report_spec: str | dict = None) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must match exactly.
        An open metadata type name may be supplied to restrict the results. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.


        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            report_spec ():
        """
        if property_value in ["","*"] or property_value is None:
            context: dict = {}
            context['method'] = "_async_get_elements_by_property_value"
            context['reason'] = "Invalid property value"
            raise PyegeriaInvalidParameterException(context=context)

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "asOfTime": as_of_time,
            "startFrom": start_from,
            "pageSize": page_size,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing
        }

        url = f"{base_path(self, self.view_server)}/elements/by-exact-property-value"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements = elements, filter=property_value,
                                                       element_type_name = "Referenceable",
                                                       output_format = output_format, report_spec = report_spec)
        return elements

    def get_elements_by_property_value(self, property_value: str, property_names: list[str],
                                       metadata_element_type_name: str = None, effective_time: str = None,
                                       as_of_time: str = None, for_lineage: bool = None, for_duplicate_processing: bool = None,
                                       start_from: int = 0, page_size: int = 0,
                                       time_out: int = default_time_out, output_format: str = "JSON",
                                       report_spec: str | dict = None) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must match exactly.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        as_of_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_property_value(property_value, property_names, metadata_element_type_name,
                                                       effective_time, as_of_time, for_lineage, for_duplicate_processing,
                                                       start_from, page_size, time_out, output_format, report_spec)
        )
        return response

    async def _async_find_elements_by_property_value(
            self,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            body: dict = None,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified. The value must only be contained in the
        properties rather than needing to be an exact match. An open metadata type name may be supplied to restrict the
        results. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str = None
            - Output format set to use. If None, the default output format set is used.
        body: dict = None
-           - Full request body - supercedes other parameters.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaExeception

        Notes
        -----

        Sample body:
        {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "startFrom": start_from,
            "pageSize": page_size,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing
        }
        """
        if body is None:
            body = {
                "class": "FindPropertyNamesProperties",
                "metadataElementTypeName": metadata_element_type_name,
                "propertyValue": property_value,
                "propertyNames": property_names,
                "startFrom": start_from,
                "pageSize": page_size,
                "forLineage": None,
                "forDuplicateProcessing": None
            }

        url = f"{base_path(self, self.view_server)}/elements/by-property-value-search"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0 or elements == NO_ELEMENTS_FOUND:
            return NO_ELEMENTS_FOUND
        if output_format == "JSON":
            return elements
        else:
            logger.info(f"Found element, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements,  property_value, metadata_element_type_name, output_format,
                                                       report_spec)


    def find_elements_by_property_value(
            self,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            body: dict = None,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified. The value must only be contained in the
        properties rather than needing to be an exact match. An open metadata type name may be supplied to restrict the
        results.

        https://egeria-project.org/types/

        Parameters
        ----------
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str = None
            - Output format set to use. If None, the default output format set is used.
        body: dict = None
-           - Full request body - supercedes other parameters.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaExeception

        Notes
        -----

        Sample body:
        {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "startFrom": start_from,
            "pageSize": page_size,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing
        }
"""

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_by_property_value(
                property_value,
                property_names,
                metadata_element_type_name,
                start_from,
                page_size,
                time_out,
                output_format,
                report_spec,
                body
            )
        )
        return response

    async def _async_get_element_by_guid(
            self,
            element_guid: str,
            element_type_name: str = None,
            output_format: str = "JSON",
            report_spec: dict | str = "Referenceable",
            body: dict | GetRequestBody = None,
    ) -> dict | str:
        """
        Retrieve element by its unique identifier.  Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - unique identifier for the element
        element_type_name : str, default = None
            - type of element to be returned
        output_format: str, default = "JSON"
            - output format to be used
        report_spec: dict | str, default = "Referenceable"
            - output format set to be used
        body: dict | GetRequestBody, default = None
            - full request specification - if provided, overrides other parameters.

        Returns
        -------
        dict | str
            Returns a string if no elements found; otherwise a dict of the element.

        Raises
        ------
        PyegeriaException
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/{element_guid}")

        response = await self._async_get_guid_request(url, element_type_name,
                                                      self._generate_referenceable_output, output_format,
                                                      report_spec, body)
        return response

    def get_element_by_guid(
            self,
            element_guid: str,
            element_type_name: str = None,
            output_format: str = "JSON",
            report_spec: dict | str = None,
            body: dict | GetRequestBody = None
    ) -> dict | str:
        """
        Retrieve element by its unique identifier.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - unique identifier for the element
        element_type_name : str, default = None
            - type of element to be returned
        output_format: str, default = "JSON"
            - output format to be used
        report_spec: dict | str, default = "Referenceable"
            - output format set to be used
        body: dict | GetRequestBody, default = None
            - full request specification - if provided, overrides other parameters.

        Returns
        -------
        dict | str
            Returns a string if no elements found; otherwise a dict of the element.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_element_by_guid(
                element_guid,
                element_type_name, output_format, report_spec, body
            )
        )
        return response

    def get_actor_for_guid(self, guid: str) -> str:
        """Get the name of the actor from the supplied guid."""
        details = self.get_element_by_guid(guid)
        if type(details) is str:
            return details
        if details["elementHeader"]["type"]["typeName"] != "UserIdentity":
            return "GUID does not represent a UserIdentity"
        return details["properties"]["userId"]

    async def _async_get_element_by_unique_name(
            self,
            name: str,
            property_name: str = None,
            output_format: str = "JSON",
            report_spec: dict | str = "Referenceable",
            body: dict = None
    ) -> list | str:
        """
        Retrieve the metadata element using the suppl
        ied unique element name (typically the qualifiedName,
        but it is possible to specify a different property name in the request body as long as its unique.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional
            - optional name of property to search. If not specified, defaults to qualifiedName
        output_format: str, default = "JSON"
            - output format to be used
        report_spec: dict | str, default = "Referenceable"
            - output format set to be used
        body: dict, default = None
            - full request specification - if provided, overrides other parameters.
        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaException
      """

        property_name = "qualifiedName" if property_name is None else property_name
        if body is None:
            body = {
                "class": "FindPropertyNameProperties",
                "propertyValue": name,
                "propertyName": property_name,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/by-unique-name")

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        elements = response.json().get("element", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found element, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "GUID", "Referenceable", output_format, report_spec)
        return elements

    def get_element_by_unique_name(
            self,
            name: str,
            property_name: str = None,
            output_format: str = "JSON",
            report_spec: dict | str = "Referenceable",
            body: dict = None
    ) -> list | str:
        """
        Retrieve the metadata element using the supplied unique element name (typically the qualifiedName,
        but it is possible to specify a different property name in the request body as long as its unique.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional
            - optional name of property to search. If not specified, defaults to qualifiedName
        output_format: str, default = "JSON"
            - output format to be used
        report_spec: dict | str, default = "Referenceable"
            - output format set to be used
        body: dict, default = None
            - full request specification - if provided, overrides other parameters.

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_element_by_unique_name(name, property_name, output_format, report_spec, body)
        )
        return response

    async def _async_get_element_guid_by_unique_name(
            self,
            name: str,
            property_name: str = None,
            body: dict = None) -> list | str:
        """
        Retrieve the guid associated with the supplied unique element name.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional, default = "qualifiedName"
            - optional name of property to search. If not specified, defaults to qualifiedName
        body: dict, default = None
            - full request specification - if provided, overrides other parameters.

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaException
        """

        property_name = "qualifiedName" if property_name is None else property_name
        if body is None:
            body = {
                "class": "FindPropertyNameProperties",
                "propertyValue": name,
                "propertyName": property_name,
            }

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/"
               f"classification-explorer/elements/guid-by-unique-name")

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )

        return response.json().get("guid", NO_ELEMENTS_FOUND)

    def get_element_guid_by_unique_name(
            self,
            name: str,
            property_name: str = None,
            body: dict = None) -> list | str:
        """
        Retrieve the guid associated with the supplied unique element name.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: str, optional, default = "qualifiedName"
            - optional name of property to search. If not specified, defaults to qualifiedName
        body: dict, default = None

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_element_guid_by_unique_name(
                name,
                property_name,
                body
            )
        )
        return response

    async def _async_get_guid_for_name(self, name: str, property_name: list[str] = ["qualifiedName", "displayName"],
                                       type_name: str = "ValidMetadataValue") -> str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown. Async version.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: list[str], default = ["qualifiedName","displayName"]
            - optional name of property to search. If not specified, defaults to qualifiedName and displayName.
        type_name: str, default = "ValidMetadataValue"
            - metadata element type name to be used to restrict the search

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaException
        """

        elements = await self._async_get_elements_by_property_value(name, property_name, type_name)

        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
            elif len(elements) > 1:
                raise PyegeriaException(context={"output": "Multiple elements found for supplied name!"})
            elif len(elements) == 1:
                return elements[0]["elementHeader"]["guid"]
        return elements

    def get_guid_for_name(
            self, name: str, property_name: list[str] = ["qualifiedName", "displayName"],
            type_name: str = "ValidMetadataValue"
    ) -> str:
        """
        Retrieve the guid associated with the supplied element name.
        If more than one element returned, an exception is thrown.

        Parameters
        ----------
        name: str
            - element name to be searched.
        property_name: list[str], default = ["qualifiedName","displayName"]
            - optional name of property to search. If not specified, defaults to qualifiedName and displayName.
        type_name: str, default = "ValidMetadataValue"
            - metadata element type name to be used to restrict the search

        Returns
        -------
        str
            Returns the guid of the element.

        Raises
        ------
        PyegeriaExeception
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_guid_for_name(name, property_name, type_name)
        )
        return response

    #
    # Elements by classification
    #
    async def _async_get_elements_by_classification(
            self,
            classification_name: str,
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: str | dict = None,
    ) -> list | str:
        """
         Retrieve elements with the requested classification name. It is also possible to limit the results
        by specifying a type name for the elements that should be returned. If no type name is specified then
        any type of element may be returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DD THH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = f"{base_path(self, self.view_server)}/elements/by-classification/{classification_name}"

        response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "", "Referenceable",
                                                       output_format, report_spec)
        return elements

    def get_elements_by_classification(
            self,
            classification_name: str,
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name. It is also possible to limit the results
        by specifying a type name for the elements that should be returned. If no type name is specified then
        any type of element may be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_classification(classification_name, metadata_element_type_name, effective_time,
                                                       for_lineage, for_duplicate_processing, start_from, page_size,
                                                       time_out, output_format, report_spec)
        )
        return response


    async def _async_get_elements_by_classification_with_property_value(
            self,
            classification_name: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name and with the requested a value found in one of the
        classification's properties specified.  The value must match exactly. An open metadata type name may be supplied
        to restrict the types of elements returned. Async version.

         https://egeria-project.org/types/

         Parameters
         ----------
         classification_name: str
             - the classification name to retrieve elements for.
         property_value: str
             - property value to be searched.
         property_names: list[str]
             - property names to search in.
         metadata_element_type_name : str, default = None
             - open metadata type to be used to restrict the search
         effective_time: str, default = None
             - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
         for_lineage: bool, default is set by server
             - determines if elements classified as Memento should be returned - normally false
         for_duplicate_processing: bool, default is set by server
             - Normally false. Set true when the caller is part of a deduplication function
         start_from: int, default = 0
             - index of the list to start from (0 for start).
         page_size
             - maximum number of elements to return.


         time_out: int, default = default_time_out
             - http request timeout for this request

         Returns
         -------
         [dict] | str
             Returns a string if no elements found and a list of dict of elements with the results.

         Raises
         ------
         PyegeriaInvalidParameterException
             one of the parameters is null or invalid or
         PyegeriaAPIException
             There is a problem adding the element properties to the metadata repository or
         PyegeriaUnauthorizedException
             the requesting user is not authorized to issue this request.

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/by-classification/{classification_name}/"
            f"with-exact-property-value"
        )
        response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements,  "Referenceable",
                                                       output_format, report_spec)
        return elements

    def get_elements_by_classification_with_property_value(
            self,
            classification_name: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements by a value found in one of the properties specified.  The value must match exactly.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_elements_by_classification_with_property_value(classification_name, property_value,
                                                                           property_names, metadata_element_type_name,
                                                                           effective_time, for_lineage,
                                                                           for_duplicate_processing, start_from,
                                                                           page_size, time_out, output_format, report_spec)
        )
        return response

    async def _async_find_elements_by_classification_with_property_value(
            self,
            classification_name: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name and with the requested value found in
        one of the classification's properties specified.  The value must only be contained in the
        properties rather than needing to be an exact match.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """
        if property_value == "*":
            property_value = None

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/by-classification/{classification_name}/"
            f"with-property-value-search"
        )
        response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if (type(elements) is list and len(elements) == 0 and property_value is not None) or type(elements) is str:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "Referenceable",
                                                       output_format, report_spec)
        return elements

    def find_elements_by_classification_with_property_value(
            self,
            classification_name: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements with the requested classification name and with the requested a value found in
        one of the classification's properties specified.  The value must only be contained in the
        properties rather than needing to be an exact match.
        An open metadata type name may be supplied to restrict the results.

        https://egeria-project.org/types/

        Parameters
        ----------
        classification_name: str
            - the classification name to retrieve elements for.
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.
        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_elements_by_classification_with_property_value(
                classification_name,
                property_value,
                property_names,
                metadata_element_type_name,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                start_from,
                page_size,
                time_out,
                output_format,
                report_spec
            )
        )
        return response

    #
    #   related elements
    #

    async def _async_get_related_elements(
            self,
            element_guid: str,
            relationship_type: str = None,
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Retrieve elements linked by relationship type name. If the relationship type is None, then all related elements
        will be returned. It is also possible to limit the results by specifying a type name for the elements that
        should be returned. If no type name is specified then any type of element may be returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str, optional, default = None
            - the type of relationship to navigate to related elements.
              If None, then all related elements will be returned.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        if relationship_type is None:
            url = (
                f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship?startAtEnd={start_at_end}"
            )
        else:
            url = (
                f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship/"
                f"{relationship_type}?startAtEnd={start_at_end}"
            )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "Referenceable",
                                                       output_format, report_spec)
        return elements

    def get_related_elements(
            self,
            element_guid: str,
            relationship_type: str = None,
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements linked by relationship type name. If the relationship type is None, then all related elements
        will be returned. It is also possible to limit the results by specifying a type name for the elements that
        should be returned. If no type name is specified then any type of element may be returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_related_elements(element_guid, relationship_type, metadata_element_type_name, start_at_end,
                                             effective_time, for_lineage, for_duplicate_processing, start_from,
                                             page_size, time_out, output_format, report_spec)
        )
        return response

    async def _async_get_related_elements_with_property_value(
            self,
            element_guid: str,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must match exactly. An open metadata type name may be
        supplied to restrict the types of elements returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - restrict search to elements of this open metadata type
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship/"
            f"{relationship_type}/with-exact-property-value"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list and len(elements) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "Referenceable",
                                                       output_format, report_spec)
        return elements

    def get_related_elements_with_property_value(
            self,
            element_guid: str,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must match exactly. An open metadata type name may be
        supplied to restrict the types of elements returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_related_elements_with_property_value(element_guid, relationship_type, property_value,
                                                                 property_names, metadata_element_type_name,
                                                                 start_at_end, effective_time, for_lineage,
                                                                 for_duplicate_processing, start_from, page_size,
                                                                 time_out, output_format, report_spec)
        )
        return response


    async def _async_find_related_elements_with_property_value(
            self,
            element_guid: str,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must only be contained in the properties rather than
        needing to be an exact match An open metadata type name may be supplied to restrict the types of elements
        returned. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - restrict search to elements of this open metadata type
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "metadataElementTypeName": metadata_element_type_name,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size,
        }

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/by-relationship/"
            f"{relationship_type}/with-property-value-search?startAtEnd={start_at_end}"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is list:
            if len(elements) == 0:
                return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(elements, "Referenceable",
                                                       output_format, report_spec)

        return elements

    def find_related_elements_with_property_value(
            self,
            element_guid: str,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
            metadata_element_type_name: str = None,
            start_at_end: int = 1,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve elements linked via the requested relationship type name and with the requested a value found in one of
        the classification's properties specified.  The value must only be contained in the properties rather than
        needing to be an exact match An open metadata type name may be supplied to restrict the types of elements
        returned.

        https://egeria-project.org/types/

        Parameters
        ----------
        element_guid: str
            - the base element to get related elements for
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        metadata_element_type_name : str, default = None
            - open metadata type to be used to restrict the search
        start_at_end: int, default = 1
            - The end of the relationship to start from - typically End1
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size: int, default = 0
            - maximum number of elements to return.
        time_out: int, default = default_time_out
            - http request timeout for this request
        output_format: str, default = "JSON"
            - Type of output to return.
        report_spec: dict | str, default = None
            - Output format set to use. If None, the default output format set is used.

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_related_elements_with_property_value(element_guid, relationship_type, property_value,
                                                                  property_names, metadata_element_type_name,
                                                                  start_at_end, effective_time, for_lineage,
                                                                  for_duplicate_processing, start_from, page_size,
                                                                  time_out, output_format, report_spec)
        )
        return response

    #
    #   relationships

    async def _async_get_relationships(
            self,
            relationship_type: str,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name. Async version.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindProperties",
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = f"{base_path(self, self.view_server)}/relationships/{relationship_type}"

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rels = response.json().get("relationships", "No relationships found")

        if type(rels) is list and len(rels) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(rels, "Referenceable",
                                                       output_format, report_spec)

        return rels

    def get_relationships(
            self,
            relationship_type: str,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_relationships(relationship_type, effective_time, for_lineage, for_duplicate_processing,
                                          start_from, page_size, time_out, output_format, report_spec)
        )
        return response

    async def _async_get_relationships_with_property_value(
            self,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON", report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name and with the requested a value found in
        one of the relationship's properties specified.  The value must match exactly. Async version.

        https://egeria-project.org/types/

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindPropertyNamesProperties",
            "openMetadataType": relationship_type,
            "propertyValue": property_value,
            "propertyNames": property_names,
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
            "startFrom": start_from,
            "pageSize": page_size
        }

        url = (
            f"{base_path(self, self.view_server)}/relationships/"
            f"with-exact-property-value"
        )

        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        rels = response.json().get("relationships", NO_ELEMENTS_FOUND)
        if type(rels) is list and len(rels) == 0:
            return NO_ELEMENTS_FOUND
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(rels, "Referenceable",
                                                       output_format, report_spec)

        return rels

    def get_relationships_with_property_value(
            self,
            relationship_type: str,
            property_value: str,
            property_names: list[str],
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            start_from: int = 0,
            page_size: int = 0,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None,
    ) -> list | str:
        """
        Retrieve relationships of the requested relationship type name and with the requested a value found in
        one of the relationship's properties specified.  The value must match exactly.

        Parameters
        ----------
        relationship_type: str
            - the type of relationship to navigate to related elements
        property_value: str
            - property value to be searched.
        property_names: list[str]
            - property names to search in.
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        start_from: int, default = 0
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_relationships_with_property_value(relationship_type, property_value, property_names,
                                                              effective_time, for_lineage, for_duplicate_processing,
                                                              start_from, page_size, time_out, output_format, report_spec)
        )
        return response

    #
    #  guid
    #

    async def _async_retrieve_instance_for_guid(
            self,
            guid: str,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None

    ) -> list | str:
        """
         Retrieve the header for the instance identified by the supplied unique identifier.
         It may be an element (entity) or a relationship between elements. Async version.

        Parameters
        ----------
        guid: str
            - the identity of the instance to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        body = {
            "class": "FindProperties",
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
        }

        url = f"{base_path(self, self.view_server)}/guids/{guid}"
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )
        element = response.json().get("element", NO_ELEMENTS_FOUND)
        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format} and report_spec: {report_spec}")
            return self._generate_referenceable_output(element, "Referenceable",
                                                       output_format, report_spec)

        return element

    def retrieve_instance_for_guid(
            self,
            guid: str,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            time_out: int = default_time_out,
            output_format: str = "JSON",
            report_spec: dict | str = None
    ) -> list | str:
        """
         Retrieve the header for the instance identified by the supplied unique identifier.
         It may be an element (entity) or a relationship between elements.

        Parameters
        ----------
        guid: str
            - the identity of the instance to retrieve
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Args:
            output_format ():
            report_spec ():
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_retrieve_instance_for_guid(guid, effective_time, for_lineage, for_duplicate_processing,
                                                   time_out, output_format, report_spec)
        )
        return response

    #
    #   Classification CRUD
    #

    async def _async_set_confidence_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate the level of confidence that the organization
        has that the data is complete, accurate and up-to-date.  The level of confidence is expressed by the
        levelIdentifier property. Async version.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an-isoTimestamp",
           "properties": {
               "class": "GovernanceClassificationProperties",
               "levelIdentifier": 0,
               "status": 0,
               "confidence": 0,
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidence"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_confidence_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate the level of confidence that the organization
        has that the data is complete, accurate and up-to-date.  The level of confidence is expressed by the
        levelIdentifier property.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an-isoTimestamp",
           "properties": {
               "class": "GovernanceClassificationProperties",
               "levelIdentifier": 0,
               "status": 0,
               "confidence": 0,
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_confidence_classification(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_confidence_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidence classification from the element.  This normally occurs when the organization has lost
        track of the level of confidence to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidence/remove"
            f""
        )
        body = {
            "class": "ClassificationRequestBody",
            "effectiveTime": effective_time,
            "forLineage": for_lineage,
            "forDuplicateProcessing": for_duplicate_processing,
        }

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_confidence_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidence classification from the element.  This normally occurs when the organization has lost
        track of the level of confidence to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_confidence_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_confidentiality_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically a data field, schema attribute or glossary term) to indicate the
        level of confidentiality that any data associated with the element should be given.  If the classification is
        attached to a glossary term, the level of confidentiality is a suggestion for any element linked to the
        glossary term via the SemanticAssignment classification. The level of confidence is expressed by the
        levelIdentifier property. Async version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an-isoTimestamp",
           "properties": {
               "class": "GovernanceClassificationProperties",
               "levelIdentifier": 0,
               "status": 0,
               "confidentiality": 0,
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidentiality"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_confidentiality_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically a data field, schema attribute or glossary term) to indicate the
        level of confidentiality that any data associated with the element should be given.  If the classification is
        attached to a glossary term, the level of confidentiality is a suggestion for any element linked to the
        glossary term via the SemanticAssignment classification. The level of confidence is expressed by the
        levelIdentifier property.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an-isoTimestamp",
           "properties": {
               "class": "GovernanceClassificationProperties",
               "levelIdentifier": 0,
               "status": 0,
               "confidentiality": 0,
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_confidentiality_classification(
                element_guid,
                body,
                time_out
            )
        )

    async def _async_clear_confidentiality_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidentiality classification from the element.  This normally occurs when the organization has lost
        track of the level of confidentiality to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/confidentiality/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time,
                "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_confidentiality_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the confidentiality classification from the element.  This normally occurs when the organization has lost
        track of the level of confidentiality to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_confidentiality_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_impact_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically a data field, schema attribute or glossary term) to indicate the
        level of confidentiality that any data associated with the element should be given.  If the classification is
        attached to a glossary term, the level of impact is a suggestion for any element linked to the
        glossary term via the SemanticAssignment classification. The level of confidence is expressed by the
        levelIdentifier property. Async version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:
        {
           "class" : "NewClassificationRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties" : {
               "class" : "ImpactProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "confidence" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/impact"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_impact_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically a data field, schema attribute or glossary term) to indicate the
        level of impact that any data associated with the element should be given.  If the classification is
        attached to a glossary term, the level of impact is a suggestion for any element linked to the
        glossary term via the SemanticAssignment classification. The level of confidence is expressed by the
        levelIdentifier property.

         Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class" : "NewClassificationRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties" : {
               "class" : "ImpactProperties",
               "levelIdentifier" : 0,
               "status" : 0,
               "confidence" : 0,
               "steward" : "Add value here",
               "stewardTypeName" : "Add value here",
               "stewardPropertyName" : "Add value here",
               "source" : "Add value here",
               "notes" : "Add value here"
           }
}

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_impact_classification(
                element_guid,
                body,
                time_out
            )
        )

    async def _async_clear_impact_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the impact classification from the element.  This normally occurs when the organization has lost
        track of the level of impact to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/impact/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time,
                "forLineage": for_lineage, "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_impact_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the impact classification from the element.  This normally occurs when the organization has lost
        track of the level of impact to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_impact_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_criticality_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how critical the element (or
        associated resource) is to the organization.  The level of criticality is expressed by the levelIdentifier
        property. Async version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below
        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an-isoTimestamp",
           "properties": {
               "class": "GovernanceClassificationProperties",
               "levelIdentifier": 0,
               "status": 0,
               "criticality": 0,
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/criticality"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_criticality_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how critical the element (or
        associated resource) is to the organization.  The level of criticality is expressed by the levelIdentifier
        property.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an-isoTimestamp",
           "properties": {
               "class": "GovernanceClassificationProperties",
               "levelIdentifier": 0,
               "status": 0,
               "criticality": 0,
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_criticality_classification(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_criticality_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the criticality classification from the element.  This normally occurs when the organization has lost
        track of the level of criticality to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/criticality/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_criticality_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the criticality classification from the element.  This normally occurs when the organization has lost
        track of the level of criticality to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_criticality_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_add_gov_definition_to_element(
            self,
            definition_guid: str,
            element_guid: str,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Link a governance definition to an element using the GovernedBy relationship. Async version.

        Governance Definitions: https://egeria-project.org/types/4/0401-Governance-Definitions/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        effective_time: str, default is None
            - None means ignore, otherwise the time that the element must be effective
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governed-by/definition/{definition_guid}/attach"
            f""
        )

        body = {"class": "RelationshipRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def add_gov_definition_to_element(
            self,
            definition_guid: str,
            element_guid: str,
            effective_time: str = None,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Link a governance definition to an element using the GovernedBy relationship.

        Governance Definition: https://egeria-project.org/types/4/0401-Governance-Definitions/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        effective_time: str, default is None
            - None means ignore, otherwise the time that the element must be effective
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_gov_definition_to_element(
                definition_guid,
                element_guid,
                effective_time,
                for_lineage,
                for_duplicate_processing,
                time_out,
            )
        )

    async def _async_clear_gov_definition_from_element(
            self,
            definition_guid,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,

    ) -> None:
        """
        Remove the GovernedBy relationship between a governance definition and an element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        definition_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governed-by/definition/"
            f"{definition_guid}/detach"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body)
        )

    def clear_gov_definition_from_element(
            self,
            scoped_by_guid,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
    ) -> None:
        """
        Remove the GovernedBy relationship between a governance definition and an element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        scoped_by_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_gov_definition_from_element(scoped_by_guid, element_guid, for_lineage,
                                                         for_duplicate_processing, effective_time)
        )

    async def _async_add_scope_to_element(
            self,
            scoped_by_guid: str,
            element_guid: str,
            body: dict | NewRelationshipRequestBody = None,
    ) -> None:
        """
        Link a scope to an element using the ScopedBy relationship. Async version.

        Scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        ----------
        scoped_by_guid: str
            - identity of the governance scope to add
        element_guid: str
            - the identity of the element to update
        body: dict | NewRelationshipRequestBody, optional
            - structure containing scope information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/scoped-by/{scoped_by_guid}/attach"

        await self._async_new_relationship_request(url, ['ScopedBy'], body)

    def add_scope_to_element(
            self,
            scoped_by_guid: str,
            element_guid: str,
            body: dict | NewRelationshipRequestBody = None,
    ) -> None:
        """
        Link a scope to an element using the ScopedBy relationship.

        Scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        ----------
        scoped_by_guid: str
            - identity of the governance scope to add
        element_guid: str
            - the identity of the element to update
        body: dict | NewRelationshipRequestBody, optional
            - structure containing scope information - see Notes

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_scope_to_element(
                scoped_by_guid,
                element_guid,
                body
            )
        )

    async def _async_remove_scope_from_element(
            self,
            scoped_by_guid,
            element_guid: str,
            body: dict | DeleteRelationshipRequestBody = None,
    ) -> None:
        """
        Remove the ScopedBy relationship between a scope and an element. Async Version.

        Scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        ----------
        scoped_by_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update
        body: dict | DeleteRelationshipRequestBody, optional
            - structure request information

        Returns
        -------

        Raises
        ------
        PyegeriaException


        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/scoped-by/{scoped_by_guid}/detach"


        await self._async_delete_relationship_request(url, body_slimmer(body))

    def remove_scope_from_element(
            self,
            scoped_by_guid,
            element_guid: str,
            body : dict | DeleteRelationshipRequestBody = None,
    ) -> None:
        """
        Remove the ScopeddBy relationship between a scope and an element.

        Scopes: https://egeria-project.org/types/1/0120-Assignment-Scopes/

        Parameters
        ----------
        scoped_by_guid: str
            - identity of the governance definition to add
        element_guid: str
            - the identity of the element to update

        body: dict | DeleteRelationshipRequestBody, optional
            - structure request information

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_scope_from_element(scoped_by_guid, element_guid, body)
        )


    async def _async_add_certification_to_element(
            self,
            certification_type_guid: str,
            element_guid: str,
            body: dict | NewRelationshipRequestBody = None,
    ) -> str:
        """
        Link an element to a certification type and include details of the certification in the relationship properties.
        The GUID returned is the identifier of the relationship. Async Version.

        Parameters
        ----------
        certification_type_guid: str
            - identity of the governance certification to add
        element_guid: str
            - the identity of the element to update
        body: dict | NewRelationshipRequestBody, optional
            - structure containing certification information - see Notes

        Returns
        -------
        GUID of the certification.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
           "class" : "NewRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties": {
              "class" : "LicenseProperties",
              "certificateId" : "",
              "startDate" : "{{$isoTimestamp}}",
              "endDate" : "{{$isoTimestamp}}",
              "conditions" : "",
              "certifiedBy" : "",
              "certifiedByTypeName" : "",
              "certifiedByPropertyName" : "",
              "custodian" : "",
              "custodianTypeName" : "",
              "custodianPropertyName" : "",
              "recipient" : "",
              "recipientTypeName" : "",
              "recipientPropertyName" : "",
              "notes" : ""
           }
        }

        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/certification-types/{certification_type_guid}/certify"

        response = await self._async_make_request("POST",url, body_slimmer(body))
        return response.json().get('guid','Relationship was not created')

    def add_certification_to_element(
            self,
            certification_type_guid: str,
            element_guid: str,
            body: dict | NewRelationshipRequestBody = None,
    ) -> str:
        """
        Link an element to a certification type and include details of the certification in the relationship properties.
        The GUID returned is the identifier of the relationship. Async Version.

        Parameters
        ----------
        certification_type_guid: str
            - identity of the governance certification to add
        element_guid: str
            - the identity of the element to update
        body: dict | NewRelationshipRequestBody, optional
            - structure containing certification information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
           "class" : "NewRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties": {
              "class" : "certificationProperties",
              "certificationId" : "",
              "startDate" : "{{$isoTimestamp}}",
              "endDate" : "{{$isoTimestamp}}",
              "conditions" : "",
              "certificationdBy" : "",
              "certificationdByTypeName" : "",
              "certificationdByPropertyName" : "",
              "custodian" : "",
              "custodianTypeName" : "",
              "custodianPropertyName" : "",
              "certificatione" : "",
              "certificationeTypeName" : "",
              "certificationePropertyName" : "",
              "entitlements" : "",
              "restrictions" : "",
              "obligations" : "",
              "notes" : ""
           }
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_certification_to_element(certification_type_guid, element_guid, body)
        )
        return response

    async def _async_update_certification(
            self,
            certification_guid: str,
            body: dict | UpdateRelationshipRequestBody = None,
    ) -> str:
        """
            Update the properties of a certification.  Remember to include the certificationId in the properties if the element has multiple
            certifications for the same certification type. Async version.

            Parameters
            ----------
            certification_guid: str
                - identity of the certification to update
            body: dict | UpdateRelationshipRequestBody, optional
                - structure containing certification information - see Notes

            Returns
            -------
            None

            Raises
            ------
            PyegeriaException

            Notes
            -----
            Sample body:
            {
               "class" : "UpdateRelationshipRequestBody",
               "externalSourceGUID": "Add guid here",
               "externalSourceName": "Add qualified name here",
               "forLineage": false,
               "forDuplicateProcessing": false,
               "effectiveTime" : "{{$isoTimestamp}}",
               "properties": {
                  "class" : "CertificationProperties",
                  "certificateId" : "",
                  "startDate" : "{{$isoTimestamp}}",
                  "endDate" : "{{$isoTimestamp}}",
                  "conditions" : "",
                  "certifiedBy" : "",
                  "certifiedByTypeName" : "",
                  "certifiedByPropertyName" : "",
                  "custodian" : "",
                  "custodianTypeName" : "",
                  "custodianPropertyName" : "",
                  "recipient" : "",
                  "recipientTypeName" : "",
                  "recipientPropertyName" : "",
                  "notes" : ""
               }
            }
            """

        url = f"{base_path(self, self.view_server)}/certifications/{certification_guid}/update"

        await self._async_update_relationship_request(url, None, body_slimmer(body))

    def update_certification(
            self,
            certification_guid: str,
            body: dict | UpdateRelationshipRequestBody = None,
    ) -> str:
        """
            Update the properties of a certification.  Remember to include the certificationId in the properties if the element has multiple
            certifications for the same certification type.

            Parameters
            ----------
            certification_guid: str
                - identity of the certification to update
            body: dict | UpdateRelationshipRequestBody, optional
                - structure containing certification information - see Notes

            Returns
            -------
            None

            Raises
            ------
            PyegeriaException

            Notes
            -----
            Sample body:
            {
               "class" : "UpdateRelationshipRequestBody",
               "externalSourceGUID": "Add guid here",
               "externalSourceName": "Add qualified name here",
               "forLineage": false,
               "forDuplicateProcessing": false,
               "effectiveTime" : "{{$isoTimestamp}}",
               "properties": {
                  "class" : "CertificationProperties",
                  "certificateId" : "",
                  "startDate" : "{{$isoTimestamp}}",
                  "endDate" : "{{$isoTimestamp}}",
                  "conditions" : "",
                  "certifiedBy" : "",
                  "certifiedByTypeName" : "",
                  "certifiedByPropertyName" : "",
                  "custodian" : "",
                  "custodianTypeName" : "",
                  "custodianPropertyName" : "",
                  "recipient" : "",
                  "recipientTypeName" : "",
                  "recipientPropertyName" : "",
                  "notes" : ""
               }
            }
            """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_certification(certification_guid, body)
        )


    async def _async_decertify_element(
            self,
            certification_guid,
            body: dict | DeleteRelationshipRequestBody = None,
    ) -> None:
        """
        Remove the certification for an element. Async Version.

        Parameters
        ----------
        certification_guid: str
            - identity of the certification to remove.
        body: dict | DeleteRelationshipRequestBody, optional
            - structure request information

        Returns
        -------

        Raises
        ------
        PyegeriaException

        """

        url = f"{base_path(self, self.view_server)}/certifications/{certification_guid}/delete"
        await self._async_delete_relationship_request(url, body_slimmer(body))

    def decertify_element(
            self,
            certification_guid,
            body : dict | DeleteRelationshipRequestBody = None,
    ) -> None:
        """
        Remove the certification for an element.

        Parameters
        ----------
        certification_guid: str
            - identity of the cerrification to remove
        body: dict | DeleteRelationshipRequestBody, optional
            - structure request information

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_decertify_element(certification_guid, body)
        )

    async def _async_add_license_to_element(
            self,
            license_type_guid: str,
            element_guid: str,
            body: dict | NewRelationshipRequestBody = None,
    ) -> str:
        """
        Link an element to a license type and include details of the license in the relationship properties.
        The GUID returned is the identifier of the relationship. Async Version.

        Parameters
        ----------
        license_type_guid: str
            - identity of the governance license to add
        element_guid: str
            - the identity of the element to update
        body: dict | NewRelationshipRequestBody, optional
            - structure containing license information - see Notes

        Returns
        -------
        Guid of the license.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
           "class" : "NewRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties": {
              "class" : "LicenseProperties",
              "licenseId" : "",
              "startDate" : "{{$isoTimestamp}}",
              "endDate" : "{{$isoTimestamp}}",
              "conditions" : "",
              "licensedBy" : "",
              "licensedByTypeName" : "",
              "licensedByPropertyName" : "",
              "custodian" : "",
              "custodianTypeName" : "",
              "custodianPropertyName" : "",
              "licensee" : "",
              "licenseeTypeName" : "",
              "licenseePropertyName" : "",
              "entitlements" : "",
              "restrictions" : "",
              "obligations" : "",
              "notes" : ""
           }
        }

        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/licensed-types/{license_type_guid}/license"

        response = await self._async_make_request("POST",url, body_slimmer(body))
        return response.json().get('guid','Relationship was not created')

    def add_license_to_element(
            self,
            license_type_guid: str,
            element_guid: str,
            body: dict | NewRelationshipRequestBody = None,
    ) -> str:
        """
        Link an element to a license type and include details of the license in the relationship properties.
        The GUID returned is the identifier of the relationship.

        Parameters
        ----------
        license_type_guid: str
            - identity of the governance license to add
        element_guid: str
            - the identity of the element to update
        body: dict | NewRelationshipRequestBody, optional
            - structure containing license information - see Notes

        Returns
        -------
        GUID of the license.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
           "class" : "NewRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties": {
              "class" : "LicenseProperties",
              "licenseId" : "",
              "startDate" : "{{$isoTimestamp}}",
              "endDate" : "{{$isoTimestamp}}",
              "conditions" : "",
              "licensedBy" : "",
              "licensedByTypeName" : "",
              "licensedByPropertyName" : "",
              "custodian" : "",
              "custodianTypeName" : "",
              "custodianPropertyName" : "",
              "licensee" : "",
              "licenseeTypeName" : "",
              "licenseePropertyName" : "",
              "entitlements" : "",
              "restrictions" : "",
              "obligations" : "",
              "notes" : ""
           }
        }

        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_license_to_element(license_type_guid, element_guid, body)
        )
        return response

    async def _async_update_license(
            self,
            license_guid: str,
            body: dict | UpdateRelationshipRequestBody = None,
    ) -> str:
        """
       Update the properties of a license.  Remember to include the licenseId in the properties if the element has multiple
       licenses for the same license type. Async Version.

        Parameters
        ----------
        license_guid: str
            - identity of the license to update
        body: dict | UpdateRelationshipRequestBody, optional
            - structure containing license information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
           "class" : "UpdateRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties": {
              "class" : "LicenseProperties",
              "licenseId" : "",
              "startDate" : "{{$isoTimestamp}}",
              "endDate" : "{{$isoTimestamp}}",
              "conditions" : "",
              "licensedBy" : "",
              "licensedByTypeName" : "",
              "licensedByPropertyName" : "",
              "custodian" : "",
              "custodianTypeName" : "",
              "custodianPropertyName" : "",
              "licensee" : "",
              "licenseeTypeName" : "",
              "licenseePropertyName" : "",
              "entitlements" : "",
              "restrictions" : "",
              "obligations" : "",
              "notes" : ""
           }
        }

        """

        url = f"{base_path(self, self.view_server)}/licenses/{license_guid}/update"

        await self._async_update_relationship_request(url, None, body_slimmer(body))

    def update_license(
            self,
            license_guid: str,
            body: dict | UpdateRelationshipRequestBody = None,
    ) -> str:
        """
       Update the properties of a license.  Remember to include the licenseId in the properties if the element has multiple
       licenses for the same license type.

        Parameters
        ----------
        license_guid: str
            - identity of the license to update
        body: dict | UpdateRelationshipRequestBody, optional
            - structure containing license information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Sample body:
        {
           "class" : "UpdateRelationshipRequestBody",
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}",
           "properties": {
              "class" : "LicenseProperties",
              "licenseId" : "",
              "startDate" : "{{$isoTimestamp}}",
              "endDate" : "{{$isoTimestamp}}",
              "conditions" : "",
              "licensedBy" : "",
              "licensedByTypeName" : "",
              "licensedByPropertyName" : "",
              "custodian" : "",
              "custodianTypeName" : "",
              "custodianPropertyName" : "",
              "licensee" : "",
              "licenseeTypeName" : "",
              "licenseePropertyName" : "",
              "entitlements" : "",
              "restrictions" : "",
              "obligations" : "",
              "notes" : ""
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_license(license_guid, body)
        )


    async def _async_unlicense_element(
            self,
            license_guid,
            body: dict | DeleteRelationshipRequestBody = None,
    ) -> None:
        """
        Remove the licensed for an element. Async Version.

        licenses: https://egeria-project.org/types/1/0120-Assignment-licenses/

        Parameters
        ----------
        license_guid: str
            - identity of the license to remove.
        body: dict | DeleteRelationshipRequestBody, optional
            - structure request information

        Returns
        -------

        Raises
        ------
        PyegeriaException


        """

        url = f"{base_path(self, self.view_server)}/licenses/{license_guid}/delete"
        await self._async_delete_relationship_request(url, body_slimmer(body))

    def unlicense_element(
            self,
            license_guid,
            body : dict | DeleteRelationshipRequestBody = None,
    ) -> None:
        """
        Remove the licensed for an element.

        licenses: https://egeria-project.org/types/1/0120-Assignment-licenses/

        Parameters
        ----------
        license_guid: str
            - identity of the license to remove
        body: dict | DeleteRelationshipRequestBody, optional
            - structure request information

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_unlicense_element(license_guid, body)
        )




    async def _async_add_ownership_to_element(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the ownership classification for an element. Async version.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - structure containing ownership information - see Notes


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forDuplicateProcessing": false,
           "forLineage": false,
           "properties": {
               "class": "OwnerProperties",
               "owner": "Add value here",
               "ownerTypeName": "Add value here",
               "ownerPropertyName": "Add value here"
           }
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/ownership"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def add_ownership_to_element(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the ownership classification for an element.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - structure containing ownership information - see Notes


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forDuplicateProcessing": false,
           "forLineage": false,
           "properties": {
               "class": "OwnerProperties",
               "owner": "Add value here",
               "ownerTypeName": "Add value here",
               "ownerPropertyName": "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_ownership_to_element(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_ownership_from_element(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the ownership classification from an element. Async version.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/ownership/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_ownership_from_element(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the ownership classification from an element.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_digital_resource_origin_from_element(element_guid, for_lineage, for_duplicate_processing,
                                                                  effective_time, time_out)
        )

    @dynamic_catch
    async def _async_add_digital_resource_origin(
            self,
            element_guid: str,
            body: dict | NewClassificationRequestBody
    ) -> None:
        """
        Add the digital resource origin classification for an element. Async Version.

        Origin: https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | NewClassificationRequestBody
            - structure containing origin information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----

        {
           "class": "NewClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forDuplicateProcessing": false,
           "forLineage": false,
           "properties": {
               "class": "DigitalResourceOriginProperties",
               "owner": "Add value here",
               "ownerTypeName": "Add value here",
               "ownerPropertyName": "Add value here"
           }
        }

        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/digital-resource-origin"
        await self._async_new_classification_request(url, ["DigitalResourceOriginProperties"], body)

    @dynamic_catch
    def add_digital_resource_origin(
            self,
            element_guid: str,
            body: dict | NewClassificationRequestBody
    ) -> None:
        """
        Add or replace the digital resource origin classification for an element.

        Origin: https://egeria-project.org/types/4/0440-Organizational-Controls/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | NewClassificationRequestBody
            - structure containing ownership information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forDuplicateProcessing": false,
           "forLineage": false,
           "properties": {
               "class": "DigitalResourceOriginProperties",
               "owner": "Add value here",
               "ownerTypeName": "Add value here",
               "ownerPropertyName": "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_digital_resource_origin(
                element_guid,
                body,
            )
        )

    @dynamic_catch
    async def _async_clear_digital_resource_origin_from_element(
            self,
            element_guid: str,
            body: dict | DeleteClassificationRequestBody
    ) -> None:
        """
        Remove the digital resource classification from an element. Async version.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | DeleteClassificationRequestBody
        - structure containing digital resource request - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException


        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/digital-resource-origin/remove"

        await self._async_delete_classification_request(
             url, body
        )

    @dynamic_catch
    def clear_digital_resource_origin_from_element(
            self,
            element_guid: str,
            body: dict | DeleteClassificationRequestBody
    ) -> None:
        """
        Remove the digital resource classification from an element.

        Ownership: https://egeria-project.org/types/4/0445-Governance-Roles/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | DeleteClassificationRequestBody
            - structure containing digital resource request - see Notes


        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_digital_resource_origin_from_element(element_guid, body)
        )

    @dynamic_catch
    async def _async_add_zone_membership(
            self,
            element_guid: str,
            body: dict | NewClassificationRequestBody
    ) -> None:
        """
        Add the zone membership classification for an element. Async Version.

        Origin: Governance Zones: https://egeria-project.org/types/4/0424-Governance-Zones/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | NewClassificationRequestBody
            - structure containing zone information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----

        {
           "class": "NewClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forDuplicateProcessing": false,
           "forLineage": false,
           "properties": {
               "class": "ZoneMembershipProperties",
               "owner": "Add value here",
               "ownerTypeName": "Add value here",
               "ownerPropertyName": "Add value here"
           }
        }

        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/zone-membership"
        await self._async_new_classification_request(url, ["ZoneMembershipProperties"], body)

    @dynamic_catch
    def add_zone_membership(
            self,
            element_guid: str,
            body: dict | NewClassificationRequestBody
    ) -> None:
        """
        Add the zone membership classification for an element.

        Origin: https://egeria-project.org/types/4/0424-Governance-Zones/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | NewClassificationRequestBody
            - structure containing zone information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Notes
        -----

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forDuplicateProcessing": false,
           "forLineage": false,
           "properties": {
               "class": "ZoneMembershipProperties",
               "owner": "Add value here",
               "ownerTypeName": "Add value here",
               "ownerPropertyName": "Add value here"
           }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_zone_membership(element_guid, body
            )
        )

    @dynamic_catch
    async def _async_clear_zone_membership(
            self,
            element_guid: str,
            body: dict | DeleteClassificationRequestBody
    ) -> None:
        """
        Remove the zone membership classification from an element. Async version.

        Ownership: https://egeria-project.org/types/4/0424-Governance-Zones/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | DeleteClassificationRequestBody
        - structure containing zone information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException


        """

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/zone-membership/remove"

        await self._async_delete_classification_request(
             url, body
        )

    @dynamic_catch
    def clear_zone_membership(
            self,
            element_guid: str,
            body: dict | DeleteClassificationRequestBody
    ) -> None:
        """
        Remove the zone membership classification from an element.

        Ownership: https://egeria-project.org/types/4/0424-Governance-Zones/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict | DeleteClassificationRequestBody
            - structure containing zone information - see Notes

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_zone_membership(element_guid, body)
        )


    async def _async_set_retention_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how long the element (or associated resource)
        is to be retained by the organization.  The policy to apply to the element/resource is captured by the retentionBasis
        property.  The dates after which the element/resource is archived and then deleted are specified in the archiveAfter and deleteAfter
        properties respectively. Async version

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below



        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "properties": {
               "class": "RetentionClassificationProperties",
               "retentionBasis": 0,
               "status": 0,
               "confidence": 0,
               "associatedGUID": "Add value here",
               "archiveAfter": "{{$isoTimestamp}}",
               "deleteAfter": "{{$isoTimestamp}}",
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/retention"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_retention_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to indicate how long the element (or associated resource)
        is to be retained by the organization.  The policy to apply to the element/resource is captured by the retentionBasis
        property.  The dates after which the element/resource is archived and then deleted are specified in the archiveAfter and deleteAfter
        properties respectively. Async version

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "properties": {
               "class": "RetentionClassificationProperties",
               "retentionBasis": 0,
               "status": 0,
               "confidence": 0,
               "associatedGUID": "Add value here",
               "archiveAfter": "{{$isoTimestamp}}",
               "deleteAfter": "{{$isoTimestamp}}",
               "steward": "Add value here",
               "stewardTypeName": "Add value here",
               "stewardPropertyName": "Add value here",
               "source": "Add value here",
               "notes": "Add value here"
           }
        }
        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_retention_classification(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_retention_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the retention classification from the element.  This normally occurs when the organization has lost
        track of the level of retention to assign to the element. Async Version.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/retention/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_retention_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the retention classification from the element.  This normally occurs when the organization has lost
        track of the level of retention to assign to the element.

        Governance Action Classifications: https://egeria-project.org/types/4/0422-Governance-Action-Classifications/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_retention_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_set_governance_expectation(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to Add the governance expectations classification to an element. Async version
        Governance Rollout: https://egeria-project.org/types/4/0450-Governance-Rollout/
        Async Version

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class" : "NewClassificationRequestBody",
           "properties" : {
               "class" : "GovernanceExpectationsProperties",
               "counts" : {
                 "countName1" : 23,
                 "countName2" : 42
               },
               "values" : {
                 "valueName1" : "Add string here",
                 "valueName2" : "Add string here"
               },
               "flags" : {
                 "flagName1" : true,
                 "flagName2" : false
               }
           },
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}"
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governance-expectations"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_governance_expectation(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
            Classify/reclassify the element (typically an asset) to Add the governance expectations classification to an element. Async version
            Governance Rollout: https://egeria-project.org/types/4/0450-Governance-Rollout/

            Parameters
            ----------
            element_guid: str
                - the identity of the element to update
            body: dict
                - a dictionary structure containing the properties to set - see note below

            time_out: int, default = default_time_out
                - http request timeout for this request

            Returns
            -------
            [dict] | str
                Returns a string if no elements found and a list of dict of elements with the results.

            Raises
            ------
            PyegeriaException

            Note:

            A sample dict structure is:

            {
               "class" : "NewClassificationRequestBody",
               "properties" : {
                   "class" : "GovernanceExpectationsProperties",
                   "counts" : {
                     "countName1" : 23,
                     "countName2" : 42
                   },
                   "values" : {
                     "valueName1" : "Add string here",
                     "valueName2" : "Add string here"
                   },
                   "flags" : {
                     "flagName1" : true,
                     "flagName2" : false
                   }
               },
               "externalSourceGUID": "Add guid here",
               "externalSourceName": "Add qualified name here",
               "forLineage": false,
               "forDuplicateProcessing": false,
               "effectiveTime" : "{{$isoTimestamp}}"
            }

            """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_governance_expectation(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_governance_expectation(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the governance expectations classification from an element. Async version

#       Governance Rollout: https://egeria-project.org/types/4/0450-Governance-Rollout/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governance-expectations/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    async def _async_update_governance_expectation(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify/reclassify the element (typically an asset) to Add the governance expectations classification to an element. Async version
        Governance Rollout: https://egeria-project.org/types/4/0450-Governance-Rollout/
        Async Version

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

    {
           "class" : "UpdateClassificationRequestBody",
           "mergeUpdate": true,
           "properties" : {
               "class" : "GovernanceExpectationsProperties",
               "counts" : {
                 "countName1" : 23,
                 "countName2" : 42
               },
               "values" : {
                 "valueName1" : "Add string here",
                 "valueName2" : "Add string here"
               },
               "flags" : {
                 "flagName1" : true,
                 "flagName2" : false
               }
           },
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "{{$isoTimestamp}}"
        }

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/governance-expectations/update"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def update_governance_expectation(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
         Classify/reclassify the element (typically an asset) to Add the governance expectations classification to an element. Async version
         Governance Rollout: https://egeria-project.org/types/4/0450-Governance-Rollout/
         Async Version

         Parameters
         ----------
         element_guid: str
             - the identity of the element to update
         body: dict
             - a dictionary structure containing the properties to set - see note below

         time_out: int, default = default_time_out
             - http request timeout for this request

         Returns
         -------
         [dict] | str
             Returns a string if no elements found and a list of dict of elements with the results.

         Raises
         ------
         PyegeriaException

         Note:

         A sample dict structure is:

        {
            "class" : "UpdateClassificationRequestBody",
            "mergeUpdate": true,
            "properties" : {
                "class" : "GovernanceExpectationsProperties",
                "counts" : {
                  "countName1" : 23,
                  "countName2" : 42
                },
                "values" : {
                  "valueName1" : "Add string here",
                  "valueName2" : "Add string here"
                },
                "flags" : {
                  "flagName1" : true,
                  "flagName2" : false
                }
            },
            "externalSourceGUID": "Add guid here",
            "externalSourceName": "Add qualified name here",
            "forLineage": false,
            "forDuplicateProcessing": false,
            "effectiveTime" : "{{$isoTimestamp}}"
        }

    """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_governance_expectation(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_set_security_tags_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the security tags for an element. Async version,

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below



        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "properties": {
               "class": "SecurityTagsProperties",
               "securityLabels": [ "Label1", "Label2" ],
               "securityProperties": {
                   "propertyName1": "add property value here",
                   "propertyName2": "add property value here"
               },
               "accessGroups": {
                   "groupName1": [ "operation1", "operation2" ],
                   "groupName2": [ "operation1", "operation3" ]
               }
           }
        }


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/security-tags"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def set_security_tags_classification(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Add or replace the security tags for an element. Async versuib,

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below



        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        [dict] | str
            Returns a string if no elements found and a list of dict of elements with the results.

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "properties": {
               "class": "SecurityTagsProperties",
               "securityLabels": [ "Label1", "Label2" ],
               "securityProperties": {
                   "propertyName1": "add property value here",
                   "propertyName2": "add property value here"
               },
               "accessGroups": {
                   "groupName1": [ "operation1", "operation2" ],
                   "groupName2": [ "operation1", "operation3" ]
               }
           }
        }


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_set_security_tags_classification(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_security_tags_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the security-tags classification from the element.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        time_out: int, default = default_time_out
            - http request timeout for this request
        effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        Returns
        -------
           None

        Raises
        ------
        PyegeriaException


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/security-tags/remove"
            f""
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_security_tags_classification(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the security-tags classification from the element.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_security_tags_classification(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_setup_semantic_assignment(
            self,
            glossary_term_guid: str,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Create a semantic assignment relationship between a glossary term and an element (normally a schema attribute,
        data field or asset). This relationship indicates that the data associated with the element meaning matches
        the description in the glossary term. Async version

        Semantic Assignments: https://egeria-project.org/types/3/0370-Semantic-Assignment/

        Parameters
        ----------
        glossary_term_guid: str
            - identity of glossary to assign
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below



        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
          "class": "RelationshipRequestBody",
          "effectiveTime": "an isoTimestamp",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "relationshipProperties": {
            "class": "SemanticAssignmentProperties",
            "expression": "add value here",
            "description": "add value here",
            "status": "VALIDATED",
            "confidence": 100,
            "createdBy": "add value here",
            "steward": "add value here",
            "source": "add value here"
          }
        }


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/semantic-assignment/terms/attach"
            f"/{glossary_term_guid}"
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def setup_semantic_assignment(
            self,
            glossary_term_guid: str,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Create a semantic assignment relationship between a glossary term and an element (normally a schema attribute,
        data field or asset). This relationship indicates that the data associated with the element meaning matches
        the description in the glossary term.

        Semantic Assignments: https://egeria-project.org/types/3/0370-Semantic-Assignment/

        Parameters
        ----------
        glossary_term_guid: str
            - identity of glossary to assign
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below



        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
          "class": "RelationshipRequestBody",
          "effectiveTime": "an isoTimestamp",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "relationshipProperties": {
            "class": "SemanticAssignmentProperties",
            "expression": "add value here",
            "description": "add value here",
            "status": "VALIDATED",
            "confidence": 100,
            "createdBy": "add value here",
            "steward": "add value here",
            "source": "add value here"
          }
        }

        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_setup_semantic_assignment(
                glossary_term_guid,
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_clear_semantic_assignment_classification(
            self,
            glossary_term_guid: str,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the semantic_assignment classification from the element. Async version.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        glossary_term_guid: str
           - identity of glossary to remove
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

        Raises
        ------
        PyegeriaException

        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/semantic-assignment/terms/"
            f"{glossary_term_guid}/detach"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def clear_semantic_assignment_classification(
            self,
            glossary_term_guid: str,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the semantic_assignment classification from the element.

        Security Tags: https://egeria-project.org/types/4/0423-Security-Definitions/

        Parameters
        ----------
        glossary_term_guid: str
           - identity of glossary to remove
        element_guid: str
            - the identity of the element to update
        for_lineage: bool, default is set by server
            - determines if elements classified as Memento should be returned - normally false
        for_duplicate_processing: bool, default is set by server
            - Normally false. Set true when the caller is part of a deduplication function
        effective_time: str, default = None
           - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
           None

        Raises
        ------
        PyegeriaException


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_clear_semantic_assignment_classification(
                glossary_term_guid,
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )

    async def _async_add_element_to_subject_area(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify the element to assert that the definitions it represents are part of a subject area definition. Async

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below


        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "properties": {
               "class": "SubjectAreaMemberProperties",
               "subjectAreaName": "Add value here"
           }
        }


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/subject-area-member"
            f""
        )

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def add_element_to_subject_area(
            self,
            element_guid: str,
            body: dict,
            time_out: int = default_time_out,
    ) -> None:
        """
        Classify the element to assert that the definitions it represents are part of a subject area definition. Async

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

        Parameters
        ----------
        element_guid: str
            - the identity of the element to update
        body: dict
            - a dictionary structure containing the properties to set - see note below

        time_out: int, default = default_time_out
            - http request timeout for this request

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException

        Note:

        A sample dict structure is:

        {
           "class": "ClassificationRequestBody",
           "effectiveTime": "an isoTimestamp",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "properties": {
               "class": "SubjectAreaMemberProperties",
               "subjectAreaName": "Add value here"
           }
        }


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_add_element_to_subject_area(
                element_guid,
                body,
                time_out,
            )
        )

    async def _async_remove_element_from_subject_area(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the subject area designation from the identified element. Async version.

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

         Parameters
         ----------
         element_guid: str
             - the identity of the element to update
         for_lineage: bool, default is set by server
             - determines if elements classified as Memento should be returned - normally false
         for_duplicate_processing: bool, default is set by server
             - Normally false. Set true when the caller is part of a deduplication function
         effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
         time_out: int, default = default_time_out
             - http request timeout for this request

         Returns
         -------
            None

         Raises
         ------
         PyegeriaInvalidParameterException
             one of the parameters is null or invalid or
         PyegeriaAPIException
             There is a problem adding the element properties to the metadata repository or
         PyegeriaUnauthorizedException
             the requesting user is not authorized to issue this request.


        """

        url = (
            f"{base_path(self, self.view_server)}/elements/{element_guid}/subject-area-member"
            f"/remove"
        )

        body = {"class": "ClassificationRequestBody", "effectiveTime": effective_time, "forLineage": for_lineage,
                "forDuplicateProcessing": for_duplicate_processing}

        await self._async_make_request(
            "POST", url, body_slimmer(body), time_out=time_out
        )

    def remove_element_from_subject_area(
            self,
            element_guid: str,
            for_lineage: bool = None,
            for_duplicate_processing: bool = None,
            effective_time: str = None,
            time_out: int = default_time_out,
    ) -> None:
        """
        Remove the subject area designation from the identified element.

        Subject Areas: https://egeria-project.org/types/4/0425-Subject-Areas/

         Parameters
         ----------
         element_guid: str
             - the identity of the element to update
         for_lineage: bool, default is set by server
             - determines if elements classified as Memento should be returned - normally false
         for_duplicate_processing: bool, default is set by server
             - Normally false. Set true when the caller is part of a deduplication function
         effective_time: str, default = None
            - Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)


         time_out: int, default = default_time_out
             - http request timeout for this request

         Returns
         -------
            None

         Raises
         ------
         PyegeriaInvalidParameterException
             one of the parameters is null or invalid or
         PyegeriaAPIException
             There is a problem adding the element properties to the metadata repository or
         PyegeriaUnauthorizedException
             the requesting user is not authorized to issue this request.


        """

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_remove_element_from_subject_area(
                element_guid,
                for_lineage,
                for_duplicate_processing,
                effective_time,
                time_out,
            )
        )


if __name__ == "__main__":
    print("Main-Classification Manager")
