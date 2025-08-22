"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_browser omvs module. There are additional methods that will be
added in subsequent versions of the glossary_omvs module.

"""

import asyncio
from datetime import datetime

from pyegeria import NO_GLOSSARIES_FOUND, max_paging_size
from pyegeria._client_new import Client2
from pyegeria._exceptions import InvalidParameterException, PropertyServerException, UserNotAuthorizedException
from pyegeria._globals import NO_CATEGORIES_FOUND, NO_TERMS_FOUND
from pyegeria._validators import validate_guid, validate_name, validate_search_string
from pyegeria.models import GetRequestBody
from pyegeria.utils import body_slimmer
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from loguru import logger
from pydantic import ValidationError, Field, HttpUrl

from pyegeria._exceptions_new import PyegeriaInvalidParameterException
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_GUID_RETURNED, NO_MEMBERS_FOUND
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria.load_config import get_app_config
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             ReferenceableProperties, InitialClassifications, TemplateRequestBody,
                             UpdateElementRequestBody, UpdateStatusRequestBody, NewRelationshipRequestBody,
                             DeleteRequestBody, UpdateRelationshipRequestBody, ResultsRequestBody,
                             get_defined_field_values, PyegeriaModel)
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties, populate_columns_from_properties,
                                       get_required_relationships)
from pyegeria.utils import body_slimmer, dynamic_catch


class GlossaryBrowser(Client2):
    """
    GlossaryBrowser is a class that extends the Client class. It provides methods to search and retrieve glossaries,
    terms, and categories.

    Attributes:

        view_server: str
            The name of the View Server to connect to.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None

    """

    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None, token: str = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_pwd = user_pwd
        self.user_id = user_id
        self.g_browser_command_root: str

        Client2.__init__(self, view_server, platform_url, user_id, user_pwd, token)


    def _extract_glossary_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract and populate glossary properties into columns_struct following the unified output_formatter pattern.

        Args:
            element (dict): The glossary element returned by the OMVS (contains 'glossaryProperties').
            columns_struct (dict): The columns structure to populate.

        Returns:
            dict: columns_struct with populated 'value' fields
        """
        # Normalize properties for populate_columns_from_properties (expects element['properties'])
        props = element.get('properties', {}) or {}
        normalized = {
            'properties': props,
            'elementHeader': element.get('elementHeader', {}),
        }
        # Prime columns with direct properties
        col_data = populate_columns_from_properties(normalized, columns_struct)
        columns_list = col_data.get('formats', {}).get('columns', [])

        # Header-derived values (GUID, type_name, etc.)
        header_props = _extract_referenceable_properties(element)
        guid = header_props.get('GUID')
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = guid

        # Derived category fields if requested
        if guid:
            categories = None
            try:
                categories = self.get_categories_for_glossary(guid)
            except Exception:
                categories = None
            cat_display_list = []
            cat_qn_list = []
            if isinstance(categories, list):
                for category in categories:
                    gcp = category.get('glossaryCategoryProperties', {})
                    dn = gcp.get('displayName', '') or ''
                    qn = gcp.get('qualifiedName', '') or ''
                    if dn:
                        cat_display_list.append(dn)
                    if qn:
                        cat_qn_list.append(qn)
            cat_names_md = (", \n".join(cat_display_list)).rstrip(',') if cat_display_list else ''
            cat_qn_md = (", \n".join(cat_qn_list)).rstrip(',') if cat_qn_list else ''
            for column in columns_list:
                if column.get('key') == 'categories_names' and not column.get('value'):
                    column['value'] = cat_names_md
                if column.get('key') == 'categories_qualified_names' and not column.get('value'):
                    column['value'] = cat_qn_md

        # Mermaid graph if requested
        for column in columns_list:
            if column.get('key') == 'mermaid' and not column.get('value'):
                column['value'] = element.get('mermaidGraph', '') or ''
                break

        return col_data



    def _extract_term_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract and populate term properties into columns_struct following the unified output_formatter pattern.

        Args:
            element (dict): The term element returned by the OMVS (contains 'glossaryTermProperties' in properties or
                normalized 'properties').
            columns_struct (dict): The columns structure to populate (as returned by select_output_format_set).

        Returns:
            dict: columns_struct with populated 'value' fields for requested columns.
        """
        # First, populate from element.properties using the utility
        col_data = populate_columns_from_properties(element, columns_struct)

        columns_list = col_data.get("formats", {}).get("columns", [])

        # Populate header-derived values
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = header_props.get('GUID')

        # Derived/computed fields
        # collectionCategories are classifications
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("collectionCategories", [])
        for classification in classifications:
            classification_names += f"{classification['classificationName']}, "
        if classification_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = classification_names[:-2]
                    break

        # Populate requested relationship-based columns generically from top-level keys
        col_data = get_required_relationships(element, col_data)

        # Subject area classification
        subject_area = element.get('elementHeader', {}).get("subjectArea", "") or ""
        subj_val = ""
        if isinstance(subject_area, dict):
            subj_val = subject_area.get("classificationProperties", {}).get("subjectAreaName", "")
        for column in columns_list:
            if column.get('key') == 'subject_area':
                column['value'] = subj_val
                break

        # Mermaid graph
        mermaid_val = element.get('mermaidGraph', "") or ""
        for column in columns_list:
            if column.get('key') == 'mermaid':
                column['value'] = mermaid_val
                break

        logger.trace(f"Extracted/Populated columns: {col_data}")

        return col_data



    def _generate_glossary_output(self, elements: dict | list[dict], search_string: str,
                                  element_type_name: str | None,
                                  output_format: str = 'DICT',
                                  output_format_set: dict | str = None) -> str | list[dict]:
        """Generate output for glossaries using the unified output formatter.

        Args:
            elements: Dictionary or list of glossary elements
            search_string: The search string used
            element_type_name: Optional subtype name
            output_format: Desired output format
            output_format_set: Optional format set name or structure
        """
        entity_type = 'Glossary'
        # Resolve output formats
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set(entity_type, output_format)
        if output_formats is None:
            output_formats = select_output_format_set('Default', output_format)

        logger.trace(f"Executing generate_glossary_output: {output_formats}")
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_glossary_properties,
            get_additional_props_func=None,
            columns_struct=output_formats,
        )

    def _get_term_additional_properties(self, element: dict, term_guid: str, output_format: str = None) -> dict:
        """Safely compute additional properties for terms (glossary and categories) if available."""
        additional: dict = {}
        # Best effort: attempt to derive glossary name and categories if helper methods exist in this class
        try:
            # Extract glossary classification anchor if present
            classifications = element.get('elementHeader', {}).get('otherClassifications', [])
            glossary_name = ''
            if classifications:
                cls_props = classifications[0].get('classificationProperties', {}) or {}
                g_guid = cls_props.get('anchorScopeGUID')
                if g_guid and hasattr(self, 'get_glossary_by_guid'):
                    try:
                        gl = self.get_glossary_by_guid(g_guid)
                        if isinstance(gl, dict):
                            if output_format == 'REPORT':
                                glossary_name = gl.get('glossaryProperties', {}).get('displayName', '')
                            else:
                                glossary_name = gl.get('glossaryProperties', {}).get('qualifiedName', '')
                    except Exception:
                        pass
            if glossary_name:
                additional['in_glossary'] = glossary_name
        except Exception:
            pass
        try:
            if hasattr(self, 'get_categories_for_term') and term_guid:
                cats = self.get_categories_for_term(term_guid)
                names = []
                if isinstance(cats, list):
                    for c in cats:
                        gcp = c.get('glossaryCategoryProperties', {})
                        val = gcp.get('displayName') if output_format in ['REPORT', 'LIST'] else gcp.get('qualifiedName')
                        if val:
                            names.append(val)
                if names:
                    additional['categories'] = ", \n".join(names)
        except Exception:
            pass
        return additional

    def _generate_term_output(self, elements: dict | list[dict], search_string: str,
                               element_type_name: str | None,
                               output_format: str = 'DICT',
                               output_format_set: dict | str = None) -> str | list[dict]:
        """Generate output for glossary terms using the unified output formatter.

        Args:
            elements: Dictionary or list of term elements.
            search_string: The search string used.
            element_type_name: Optional subtype name; determines the entity type label when provided.
            output_format: Desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML).
            output_format_set: Optional format set name or structure controlling columns.

        Returns:
            Union[str, list[dict]]: Formatted output per requested format.
        """
        entity_type = 'GlossaryTerm'
        # Resolve output formats
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)
            else:
                output_formats = None
        else:
            output_formats = select_output_format_set(entity_type, output_format)
        if output_formats is None:
            output_formats = select_output_format_set('Default', output_format)

        logger.trace(f"Executing generate_term_output: {output_formats}")
        return generate_output(
            elements=elements,
            search_string=search_string,
            entity_type=entity_type,
            output_format=output_format,
            extract_properties_func=self._extract_term_properties,
            get_additional_props_func=self._get_term_additional_properties,
            columns_struct=output_formats,
        )

    #
    #       Get Valid Values for Enumerations
    #

    async def _async_get_glossary_term_statuses(self) -> [str]:
        """Return the list of glossary term status enum values. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term statuses retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-browser/glossaries/terms/status-list")

        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    def get_glossary_term_statuses(self) -> [str]:
        """Return the list of glossary term status enum values.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of glossary term statuses. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    async def _async_get_glossary_term_rel_statuses(self) -> [str]:
        """Return the list of glossary term relationship status enum values.  These values are stored in a
        term-to-term, or term-to-category, relationship and are used to indicate how much the relationship should be
        trusted. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term statuses retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-browser/glossaries/terms/relationships/status-list")

        response = await self._async_make_request("GET", url)
        return response.json().get("statuses", [])

    def get_glossary_term_rel_statuses(self) -> [str]:
        """Return the list of glossary term relationship status enum values.  These values are stored in a
        term-to-term, or term-to-category, relationship and are used to indicate how much the relationship should be
        trusted.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of glossary term statuses. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_rel_statuses())
        return response

    async def _async_get_glossary_term_activity_types(self) -> [str]:
        """Return the list of glossary term activity type enum values. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term statuses retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-browser/glossaries/terms/activity-types")

        response = await self._async_make_request("GET", url)
        return response.json().get("types", [])

    def get_glossary_term_activity_types(self) -> [str]:
        """Return the list of glossary term activity type enum values.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of glossary term statuses. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_term_statuses())
        return response

    async def _async_get_term_relationship_types(self) -> [str]:
        """Return the list of term relationship types enum values. Async version.

        Parameters
        ----------


        Returns
        -------
        List[str]
            A list of glossary term relationships retrieved from the server.

        """

        url = (f"{self.platform_url}/servers/{self.view_server}"
               f"/api/open-metadata/glossary-manager/glossaries/terms/relationships/type-names")

        response = await self._async_make_request("GET", url)
        return response.json().get("names", [])

    def get_term_relationship_types(self) -> [str]:
        """Return the list of term relationship type enum values.

        Parameters
        ----------


        Returns
        -------
        list of str
            A list of term relationship types. Each status is represented as a string.

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_relationship_types())
        return response


    #
    #       Glossaries
    #

    async def _async_find_glossaries(self, search_string: str, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, type_name: str = "Glossary",
                                     classification_names: list[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict = None, body: dict = None) -> list | str:
        """Retrieve the list of glossary metadata elements that contain the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        classification_names: list[str], [default=None], optional
            An optional parameter indicating the classification names to filter by.
        type_name: str, [default=None], optional
            An optional parameter indicating the subtype of the glossary to filter by.
            Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.
        body: dict, optional
            A dictionary containing the search string and other optional parameters. If specified, these values
            will override the search_string, starts_with, ends_with, and ignore_case parameters.

        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """

        if search_string == "*":
            search_string = None



        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"by-search-string")
        response = await self._async_find_request(url, _type= type_name,
                                                  _gen_output=self._generate_glossary_output,
                                                  search_string = search_string, classification_names = classification_names,
                                                  metadata_element_types = ["Glossary"],
                                                  starts_with = starts_with, ends_with = ends_with, ignore_case = ignore_case,
                                                  start_from = start_from, page_size = page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)
        return response


    def find_glossaries(self, search_string: str, starts_with: bool = False,
                        ends_with: bool = False, ignore_case: bool = False, type_name: str = None,
                                     classification_names: list[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict = None, body: dict = None) -> list | str:

        """ Retrieve the list of glossary metadata elements that contain the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

         Parameters
         ----------
         search_string: str,
             Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
         starts_with : bool, [default=False], optional
             Starts with the supplied string.
         ends_with : bool, [default=False], optional
             Ends with the supplied string
         ignore_case : bool, [default=False], optional
             Ignore case when searching
         classification_names: list[str], [default=None], optional
             An optional parameter indicating the classification names to filter by.
         type_name: str, [default=None], optional
             An optional parameter indicating the subtype of the glossary to filter by.
             Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
         start_from: int, [default=0], optional
                     When multiple pages of results are available, the page number to start from.
         page_size: int, [default=None]
             The number of items to return in a single page. If not specified, the default will be taken from
             the class instance.
         output_format: str, default = 'JSON'
             Type of output to produce:
                 JSON - output standard json
                 MD - output standard markdown with no preamble
                 FORM - output markdown with a preamble for a form
                 REPORT - output markdown with a preamble for a report
         output_format_set: str | dict, optional
             Output format set name or dictionary. Defaults to None.
         body: dict, optional
             A dictionary containing the search string and other optional parameters. If specified, these values
             will override the search_string, starts_with, ends_with, and ignore_case parameters.

         Returns
         -------
         List | str

         A list of glossary definitions active in the server.

         Raises
         ------

         InvalidParameterException
           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
         PropertyServerException
           Raised by the server when an issue arises in processing a valid request
         NotAuthorizedException
           The principle specified by the user_id does not have authorization for the requested action

         """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
                    self._async_find_glossaries(search_string,  starts_with, ends_with, ignore_case,
                                         type_name, classification_names, start_from, page_size,
                                                output_format, output_format_set, body))

        return response
    async def _async_get_glossaries_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> dict | str:
        """Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time. Time format is
            "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        None

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """


        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"by-name")
        response = await self._async_get_name_request(url, _type="Glossary",
                                                     _gen_output=self._generate_glossary_output,
                                                     filter_string=filter_string,
                                                     classification_names=classification_names,
                                                     start_from=start_from, page_size=page_size,
                                                     output_format=output_format, output_format_set=output_format_set,
                                                     body=body)

        return response

    def get_glossaries_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> dict | str:
        """Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time.

            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

        Returns
        -------
        None

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossaries_by_name(filter_string, classification_names, body,start_from, page_size,
                                               output_format, output_format_set))
        return response


    async def _async_get_glossary_by_guid(self, glossary_guid: str, element_type: str = "Glossary", body: dict | GetRequestBody = None,
                                          output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        """Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            effective_time: str, optional
                Effective time of the query. If not specified will default to any time. Time format is
                "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                LIST - output a markdown table with columns for Glossary Name, Qualified Name, Language, Description,
                Usage
                DICT - output a dictionary structure containing all attributes
            output_format_set: str | dict, optional
                Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict | str
            if output format is JSON: The glossary definition associated with the glossary_guid
            if output format is MD: A markdown string with the same information.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/retrieve")
        response = await self._async_get_guid_request(url, _type=element_type,
                                                  _gen_output=self._generate_glossary_output,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response


    def get_glossary_by_guid(self, glossary_guid: str, element_type: str = "Glossary", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", output_format_set: str | dict = None) -> dict:
        """Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            effective_time: str, optional
                Effective time of the query. If not specified will default to any time. Time format is
                "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
            output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
                LIST - output a markdown table with columns for Glossary Name, Qualified Name, Language, Description,
                Usage
                DICT - output a dictionary structure containing all attributes
            output_format_set: str | dict, optional
                Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_by_guid(glossary_guid, element_type, body,output_format, output_format_set))
        return response

    async def _async_get_glossary_for_term(self, term_guid: str, element_type: str = "GlossaryTerm",
                                           body: dict | GetRequestBody = None,
                                           output_format: str = "JSON",
                                           output_format_set: str | dict = None) -> dict | str:
        """Retrieve the glossary metadata element for the requested term.  The optional request body allows you to
            specify that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

        Returns
        -------
        dict
            The glossary information retrieved for the specified term.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"for-term/{term_guid}/retrieve")

        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_glossary_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)
        return response

    def get_glossary_for_term(self, term_guid: str, element_type: str = "GlossaryTerm",
                              body: dict | GetRequestBody = None,
                              output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        """Retrieve the glossary metadata element for the requested term.  The optional request body allows you to
            specify that the glossary element should only be returned if it was effective at a particular time.

            Async Version.

        Parameters
        ----------
        term_guid : str
            The unique identifier for the term.

        effective_time : datetime, optional
            TIf specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601).

        Returns
        -------
        dict
            The glossary information retrieved for the specified term.
        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_glossary_for_term(term_guid, element_type, body, output_format, output_format_set))
        return response




    async def _async_get_terms_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list:
        """Retrieve glossary terms by display name or qualified name. Async Version.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage : bool, optional
            Flag to indicate whether the search should include lineage information. Default is False.
        for_duplicate_processing : bool, optional
            Flag to indicate whether the search should include duplicate processing information. Default is False.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
        output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
            DICT - output a simplified DICT structure
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        list
            A list of terms matching the search criteria. If no terms are found, it returns the string "No terms found".

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        """



        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-name")

        response = await self._async_get_name_request(url, _type="Glossary",
                                                      _gen_output=self._generate_term_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response


    def get_terms_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list:
        """Retrieve glossary terms by display name or qualified name.

        Parameters
        ----------
        term : str
            The term to search for in the glossaries.
        glossary_guid : str, optional
            The GUID of the glossary to search in. If not provided, the search will be performed in all glossaries.
        status_filter : list, optional
            A list of status values to filter the search results. Default is an empty list, which means no filtering.

        effective_time : datetime, optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
             Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)
        for_lineage : bool, optional
            Flag to indicate whether the search should include lineage information. Default is False.
        for_duplicate_processing : bool, optional
            Flag to indicate whether the search should include duplicate processing information. Default is False.
        start_from : int, optional
            The index of the first term to retrieve. Default is 0.
        page_size : int, optional
            The number of terms to retrieve per page. If not provided, it will use the default page size.
         output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
            DICT - output a simplified DICT structure
         output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        list
            A list of terms matching the search criteria. If no terms are found,
            it returns the string "No terms found".

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_terms_by_name(filter_string, classification_names, body,start_from, page_size,
                                           output_format, output_format_set))
        return response

    async def _async_get_term_by_guid(self, term_guid: str, element_type: str = "GlossaryTerm", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        """Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        output_format: str, default = 'JSON'
            Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.

        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"{term_guid}/retrieve")
        response = await self._async_get_guid_request(url, _type=element_type,
                                                      _gen_output=self._generate_term_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)
        return response

    def get_term_by_guid(self, term_guid: str, element_type: str = "GlossaryTerm", body: dict| GetRequestBody=None,
                             output_format: str = "JSON", output_format_set: str | dict = None) -> dict | str:
        """Retrieve a term using its unique id. Async version.
        Parameters
        ----------
        term_guid : str
            The GUID of the glossary term to retrieve.
        output_format: str, default = 'JSON'
                Type of output to produce:
                JSON - output standard json
                MD - output standard markdown with no preamble
                FORM - output markdown with a preamble for a form
                REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.
        Returns
        -------
        dict | str
            A dict detailing the glossary term represented by the GUID. If no term is found, the string
            "No term found" will be returned.
        Raises
        ------
        InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
        PropertyServerException
            Raised by the server when an issue arises in processing a valid request.
        NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_term_by_guid(term_guid, element_type, body,  output_format, output_format_set))

        return response

    async def _async_find_glossary_terms(self, search_string: str, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, type_name: str = "GlossaryTerm",
                                     classification_names: list[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict = None, body: dict = None) -> list | str:
        """Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.
        output_format: str, default = 'JSON'
          Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report

        Returns
        -------
        List | str

        A list of term definitions

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a single
        glossary.
        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/glossary-browser/glossaries/terms/"
               f"by-search-string")
        response = await self._async_find_request(url, _type= type_name,
                                                  _gen_output=self._generate_term_output,
                                                  search_string = search_string, classification_names = classification_names,
                                                  metadata_element_types = ["GlossaryTerm"],
                                                  starts_with = starts_with, ends_with = ends_with, ignore_case = ignore_case,
                                                  start_from = start_from, page_size = page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)
        return response


    def find_glossary_terms(self, search_string: str, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, type_name: str = "GlossaryTerm",
                                     classification_names: list[str] = None, start_from: int = 0,
                                     page_size: int = 0, output_format: str = 'JSON',
                                     output_format_set: str | dict = None, body: dict = None) -> list | str:
        """Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries
            returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            If specified, the term information will be retrieved if it is active at the `effective_time`.
            Time format is "YYYY-MM-DDTHH:MM:SS" (ISO 8601)

            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.
        output_format: str, default = 'JSON'
            Type of output to produce:
            JSON - output standard json
            MD - output standard markdown with no preamble
            FORM - output markdown with a preamble for a form
            REPORT - output markdown with a preamble for a report
        output_format_set: str | dict, optional
            Output format set name or dictionary. Defaults to None.

        Returns
        -------
        List | str

        A list of term definitions

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a
        single glossary.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_glossary_terms(search_string, starts_with,
                                            ends_with, ignore_case, type_name,classification_names,
                                            start_from,
                                            page_size, output_format, output_format_set, body))

        return response






if __name__ == "__main__":
    print("Main-Glossary Browser")
