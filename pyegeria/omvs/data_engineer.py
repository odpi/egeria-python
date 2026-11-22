"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Access tabular data sets

"""
from pyegeria.core._no_password import NO_PASSWORD, carried_password, password_as_given, resolve_password
import asyncio

from pydantic import HttpUrl

from typing import Unpack
from pyegeria.core.request_filters import GetFilters, ListFilters, SearchFilters
from pyegeria.core._exceptions import PyegeriaException
from pyegeria.core.utils import dynamic_catch, transform_json_to_tabular
from pyegeria.core._server_client import ServerClient
from pyegeria.models import SearchStringRequestBody
from pyegeria.models import (NewElementRequestBody, TemplateRequestBody, UpdateElementRequestBody,
                             DeleteElementRequestBody, FilterRequestBody, GetRequestBody,
                             NewRelationshipRequestBody, DeleteRelationshipRequestBody)
from pyegeria.core._globals import NO_GUID_RETURNED
from pyegeria.core.egeria_6_4_bodies import checked_body, e64_url
from pyegeria.core.egeria_6_4_names import (
    DATA_VALUE, DATA_VALUE_PROPERTIES, LITERAL_DATA_VALUE_PROPERTIES,
    DATA_VALUES_CREATE, DATA_VALUES_FROM_TEMPLATE, DATA_VALUES_UPDATE, DATA_VALUES_DELETE, DATA_VALUES_BY_NAME,
    DATA_VALUES_RETRIEVE, DATA_VALUES_BY_SEARCH_STRING,
    DATA_VALUE_SOURCE_PROPERTIES, PROCESSING_VARIABLE_PROPERTIES, EMBEDDED_DATA_VALUE_PROPERTIES,
    DATA_VALUE_SOURCES_ATTACH, DATA_VALUE_SOURCES_DETACH, PROCESSING_VARIABLES_ATTACH,
    PROCESSING_VARIABLES_DETACH, EMBEDDED_DATA_VALUES_ATTACH, EMBEDDED_DATA_VALUES_DETACH,
)
from pyegeria.view.output_formatter import _generate_default_output
from typing import Any, Optional
from pyegeria.core.async_runner import run_sync

# The properties classes a data-value request accepts (Egeria 6.4): a DataValue or its LiteralDataValue subtype.
DATA_VALUE_PROPERTIES_CLASSES = (DATA_VALUE_PROPERTIES, LITERAL_DATA_VALUE_PROPERTIES)

class DataEngineer(ServerClient):
    """
    Client for the Data Engineer View Service.

    The Data Engineer View Service provides methods to access tabular data sets.

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
    @dynamic_catch
    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: str = None,
        timeout: int = None,
    ):
        """
        Initialize the DataEngineer client.

        Parameters
        ----------
        view_server : str
            The name of the View Server to use.
        platform_url : str
            URL of the server platform to connect to.
        user_id : str
            The identity of the user calling the method.
        user_pwd : str, optional
            The password associated with the user_id. Defaults to None.
        token : str, optional
            An optional bearer token for authentication.
        timeout : int, optional
            An optional timeout for requests.
        """
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = password_as_given(user_pwd)

        ServerClient.__init__(
            self, view_server, platform_url, user_id, user_pwd, token, timeout=timeout
        )
        self.command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-engineer")

    @dynamic_catch
    async def _async_find_tabular_data_sets(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        **kwargs: Unpack[SearchFilters]
    ) -> list | str:
        """ Retrieve the list of tabular data set metadata elements that contain the search string. Async Version.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all data sets.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_classified_elements: list[str], optional
            The types of classified elements to skip.
        include_only_classified_elements: list[str], optional
            The types of classified elements to include.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        governance_zone_filter: list[str], optional
            The governance zones to search in.
        as_of_time: str, optional
            The time to search as of.
        effective_time: str, optional
            The effective time to search at.
        relationship_page_size: int, [default=0], optional
            The page size for relationships.
        limit_results_by_status: list[str], optional
            The statuses to limit results by.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = "Referenceable"
            - The desired output columns/fields to include.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        property_names: list[str], optional
            The names of properties to search for.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Accepts the standard search filters as keyword arguments (see ``SearchFilters``
        in ``pyegeria.core.request_filters``), e.g. ``metadata_element_subtypes=[...]``.

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = f"{self.command_root}/assets/by-search-string"
        
        # Merge explicit parameters with kwargs
        params = {
            'graph_query_depth': graph_query_depth,
            'search_string': search_string,
            'body': body,
            'starts_with': starts_with,
            'ends_with': ends_with,
            'ignore_case': ignore_case,
            'start_from': start_from,
            'page_size': page_size,
            'output_format': output_format,
            'report_spec': report_spec
        }
        params.update(kwargs)
        
        # Filter out None values, but keep search_string even if None (it's required)
        params = {k: v for k, v in params.items() if v is not None or k == 'search_string'}
        
        response = await self._async_find_request(url, _type="TabularDataSet",
                                                  _gen_output=self._generate_referenceable_output, **params)
        return response

    @dynamic_catch
    def find_tabular_data_sets(
        self,
        search_string: str = "*",
        body: Optional[dict | SearchStringRequestBody] = None,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = 100,
        graph_query_depth: int = 3, output_format: str = "JSON",
        report_spec: str | dict = "Referenceable",
        **kwargs: Unpack[SearchFilters]
    ) -> list | str:
        """ Retrieve the list of tabular data set metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all data sets.
        starts_with : bool, [default=True], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        anchor_domain: str, optional
            The anchor domain to search in.
        metadata_element_type: str, optional
            The type of metadata element to search for.
        metadata_element_subtypes: list[str], optional
            The subtypes of metadata element to search for.
        skip_relationships: list[str], optional
            The types of relationships to skip.
        include_only_relationships: list[str], optional
            The types of relationships to include.
        skip_classified_elements: list[str], optional
            The types of classified elements to skip.
        include_only_classified_elements: list[str], optional
            The types of classified elements to include.
        graph_query_depth: int, [default=3], optional
            The depth of the graph query.
        governance_zone_filter: list[str], optional
            The governance zones to search in.
        as_of_time: str, optional
            The time to search as of.
        effective_time: str, optional
            The effective time to search at.
        relationship_page_size: int, [default=0], optional
            The page size for relationships.
        limit_results_by_status: list[str], optional
            The statuses to limit results by.
        sequencing_order: str, optional
            The order to sequence results by.
        sequencing_property: str, optional
            The property to sequence results by.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        report_spec: str | dict , optional, default = "Referenceable"
            - The desired output columns/fields to include.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=100]
            The number of items to return in a single page.
        property_names: list[str], optional
            The names of properties to search for.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Accepts the standard search filters as keyword arguments (see ``SearchFilters``
        in ``pyegeria.core.request_filters``), e.g. ``metadata_element_subtypes=[...]``.

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
-------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        return run_sync(
            self._async_find_tabular_data_sets(
                search_string=search_string,
                graph_query_depth=graph_query_depth,
                body=body,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                **kwargs
            )
        )

    @dynamic_catch
    def get_tabular_data_set(self, guid: str = None, start_from_row: int = 0, max_row_count: int = 5000,
                             output_format: str = "JSON", **kwargs) -> dict:
        """ Retrieve a tabular data set report.

        Parameters
        ----------
        tabular_data_set_guid: str
            The unique identifier of the tabular data set.
        start_from_row: int, optional
            The starting row number for the report.
        max_row_count: int, optional
            The maximum number of rows to return.
        output_format: str, optional
            The format of the output (JSON, CSV, RICH-TABLE).

        Returns
        -------
        dict - the tabular data set report

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        """
        response = run_sync(
            self._async_get_tabular_data_set(guid=guid, start_from_row=start_from_row, max_row_count=max_row_count, output_format=output_format, **kwargs)
        )
        return response

    @dynamic_catch
    async def _async_get_tabular_data_set(self, guid: str = None, start_from_row: int = 0, max_row_count: int = 5000,
                                          output_format: str = "JSON", **kwargs) -> dict:
        """Retrieve a tabular data set report. Async version.

        Parameters
        ----------
        tabular_data_set_guid: str
            The unique identifier of the tabular data set.
        start_from_row: int, optional
            The starting row number for the report.
        max_row_count: int, optional
            The maximum number of rows to return.
        output_format: str, optional
            The format of the output (JSON, CSV, RICH-TABLE).

        Returns
        -------
        dict
            The tabular data set report.

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.
        """
        if guid is None and "tabular_data_set_guid" in kwargs:
            guid = kwargs.pop("tabular_data_set_guid")

        url = str(HttpUrl(f"{self.command_root}/tabular-data-sets/{guid}/report?"
                          f"startFromRow={start_from_row}&maxRowCount={max_row_count}"))
        response = await self._async_make_request("GET", url)
        el_list = response.json().get('tabularDataSetReport',"No Dataset Found")
        if isinstance(el_list, dict):
            return el_list
        else:
            raise PyegeriaException(f"Unsupported output format: {output_format}")

    # =========================================================================================================
    # Data values (Egeria 6.4, odpi/egeria#9463; type 0208 Data Values)
    #
    # Every request below needs Egeria 6.4 or later: on an earlier Egeria the endpoints do not exist (404).
    # The paths come from pyegeria.core.egeria_6_4_names, the one place the 6.4 names are kept.
    #
    # The write requests send the caller's body as given, after pyegeria.core.egeria_6_4_bodies.checked_body's
    # checks (a dict is sent unchanged; a model is sent as its JSON dump), so a body copied from Egeria's `.http`
    # samples reaches Egeria exactly. A DataValue's properties may be DataValueProperties or its subtype
    # LiteralDataValueProperties (dataValue, dataValueList, dataValueMap); any other properties class, and any
    # property key the class does not read, is refused here, before Egeria refuses or silently drops it.
    # =========================================================================================================

    @dynamic_catch
    async def _async_create_data_value(self, body: dict | NewElementRequestBody) -> str:
        """Create a data value (a DataValue, or a LiteralDataValue that holds the value itself). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        body : dict | NewElementRequestBody
            A NewElementRequestBody whose properties are DataValueProperties or LiteralDataValueProperties.
            Required. For a literal value, `dataValue` holds one value, `dataValueList` a list of values and
            `dataValueMap` a map of names to values; all three are sent unchanged.

        Returns
        -------
        str
            The GUID of the new data value.

        Raises
        ------
        PyegeriaInvalidParameterException
            No body, or a properties class other than DataValueProperties or LiteralDataValueProperties
            (refused locally, before the request is sent).
        PyegeriaException
            Issues raised in communicating or server-side processing.

        Notes
        -----
        Sample body (Egeria's data-engineer `.http`, createDataValue)::

            {
              "class" : "NewElementRequestBody",
              "anchorGUID" : "add guid here",
              "isOwnAnchor": false,
              "parentGUID": "add guid here",
              "parentRelationshipTypeName": "add type name here",
              "parentAtEnd1": false,
              "properties": {
                "class" : "DataValueProperties",
                "qualifiedName": "add unique name here",
                "displayName": "add short name here",
                "description": "add description here",
                "dataFormat": "add data format here",
                "length": 0,
                "dataType": "add data type here",
                "usage": "add usage here"
              }
            }

        For a LiteralDataValue, use "class": "LiteralDataValueProperties" and add any of
        "dataValue": "42", "dataValueList": ["a", "b"], "dataValueMap": {"low": "1", "high": "9"}.
        """
        json_body = checked_body(body, "create_data_value", request_class="NewElementRequestBody",
                                 properties_classes=DATA_VALUE_PROPERTIES_CLASSES, required=True)
        response = await self._async_make_request("POST", e64_url(self.platform_url, self.view_server, DATA_VALUES_CREATE), json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_data_value(self, body: dict | NewElementRequestBody) -> str:
        """Create a data value (a DataValue, or a LiteralDataValue that holds the value itself).

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_create_data_value` for the body.

        Returns
        -------
        str
            The GUID of the new data value.
        """
        return run_sync(self._async_create_data_value(body))

    @dynamic_catch
    async def _async_create_data_value_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a data value from an existing element used as a template. Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        The template defines additional classifications and relationships to add to the new element.

        Parameters
        ----------
        body : dict | TemplateRequestBody
            A TemplateRequestBody naming the `templateGUID`, with optional `replacementProperties` and
            `placeholderPropertyValues`. Required.

        Returns
        -------
        str
            The GUID of the new data value.

        Raises
        ------
        PyegeriaInvalidParameterException
            No body (refused locally).
        PyegeriaException
            Issues raised in communicating or server-side processing.

        Notes
        -----
        Sample body (createDataValueFromTemplate)::

            {
              "class" : "TemplateRequestBody",
              "anchorGUID" : "add guid here",
              "isOwnAnchor": false,
              "templateGUID": "add guid here",
              "replacementProperties": {
                "class": "EntityElementProperties",
                "propertyValueMap" : {
                  "description" : {"class": "PrimitiveTypePropertyValue", "typeName": "string",
                                    "primitiveValue" : "New description"}
                }
              },
              "placeholderPropertyValues": {"placeholder1" : "propertyValue1"}
            }
        """
        json_body = checked_body(body, "create_data_value_from_template", request_class="TemplateRequestBody",
                                 required=True)
        response = await self._async_make_request("POST", e64_url(self.platform_url, self.view_server, DATA_VALUES_FROM_TEMPLATE), json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_data_value_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a data value from an existing element used as a template.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_create_data_value_from_template`.

        Returns
        -------
        str
            The GUID of the new data value.
        """
        return run_sync(self._async_create_data_value_from_template(body))

    @dynamic_catch
    async def _async_update_data_value(self, data_value_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """Update the properties of a data value. Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        data_value_guid : str
            The GUID of the data value to update.
        body : dict | UpdateElementRequestBody
            Required. Its properties are DataValueProperties or LiteralDataValueProperties. `mergeUpdate` is
            sent as given: true changes only the properties sent; false replaces them all.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaInvalidParameterException
            No body, or a properties class other than DataValueProperties or LiteralDataValueProperties
            (refused locally).
        PyegeriaException
            Issues raised in communicating or server-side processing.

        Notes
        -----
        Sample body (updateDataValue)::

            {
              "class" : "UpdateElementRequestBody",
              "mergeUpdate": true,
              "properties": {
                "class" : "DataValueProperties",
                "qualifiedName": "add unique name here",
                "description": "add description here",
                "dataFormat": "add data format here",
                "dataType": "add data type here"
              }
            }
        """
        json_body = checked_body(body, "update_data_value", request_class="UpdateElementRequestBody",
                                 properties_classes=DATA_VALUE_PROPERTIES_CLASSES, required=True)
        await self._async_make_request("POST", e64_url(self.platform_url, self.view_server, DATA_VALUES_UPDATE, dataValueGUID=data_value_guid),
                                       json_body)

    @dynamic_catch
    def update_data_value(self, data_value_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """Update the properties of a data value.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_update_data_value` for the body.
        """
        return run_sync(self._async_update_data_value(data_value_guid, body))

    @dynamic_catch
    async def _async_delete_data_value(self, data_value_guid: str,
                                       body: Optional[dict | DeleteElementRequestBody] = None,
                                       cascade: bool = False) -> None:
        """Delete a data value. Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        data_value_guid : str
            The GUID of the data value to delete.
        body : dict | DeleteElementRequestBody, optional
            Sent as given. With no body, a DeleteElementRequestBody with `cascadedDelete` = `cascade` is sent.
        cascade : bool, default False
            Used only when no body is given: also delete the elements anchored to this one.

        Returns
        -------
        None

        Notes
        -----
        Sample body (deleteDataValue)::

            {
              "class" : "DeleteElementRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
        """
        if body is None:
            body = {"class": "DeleteElementRequestBody", "cascadedDelete": cascade}
        json_body = checked_body(body, "delete_data_value", request_class="DeleteElementRequestBody")
        await self._async_make_request("POST", e64_url(self.platform_url, self.view_server, DATA_VALUES_DELETE, dataValueGUID=data_value_guid),
                                       json_body)

    @dynamic_catch
    def delete_data_value(self, data_value_guid: str, body: Optional[dict | DeleteElementRequestBody] = None,
                          cascade: bool = False) -> None:
        """Delete a data value.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_delete_data_value`.
        """
        return run_sync(self._async_delete_data_value(data_value_guid, body, cascade))

    @dynamic_catch
    async def _async_get_data_values_by_name(self, filter_string: Optional[str] = None,
                                             body: Optional[dict | FilterRequestBody] = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = "JSON",
                                             report_spec: str | dict = "Referenceable",
                                             **kwargs: Unpack[ListFilters]) -> list | str:
        """Return the data values (and literal data values) with a particular name. Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        filter_string : str, optional
            The name to match. Ignored when `body` is given.
        body : dict | FilterRequestBody, optional
            A FilterRequestBody; it takes precedence over the other arguments.
        start_from : int, default 0
            The first result to return, when paging.
        page_size : int, default 0
            The most results to return (0 means the server's maximum).
        output_format : str, default "JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", "LIST", "MERMAID".
        report_spec : str | dict, default "Referenceable"
            The report spec that chooses the columns, for formats other than JSON.

        Returns
        -------
        list | str
            The matching elements, or NO_ELEMENTS_FOUND.

        Notes
        -----
        Sample body (getDataValuesByName)::

            {"class" : "FilterRequestBody", "filter" : "Add name here", "startFrom": 0, "pageSize": 10}
        """
        return await self._async_get_name_request(e64_url(self.platform_url, self.view_server, DATA_VALUES_BY_NAME), _type=DATA_VALUE,
                                                  _gen_output=self._generate_referenceable_output,
                                                  filter_string=filter_string, body=body, start_from=start_from,
                                                  page_size=page_size, output_format=output_format,
                                                  report_spec=report_spec, **kwargs)

    @dynamic_catch
    def get_data_values_by_name(self, filter_string: Optional[str] = None,
                                body: Optional[dict | FilterRequestBody] = None, start_from: int = 0,
                                page_size: int = 0, output_format: str = "JSON",
                                report_spec: str | dict = "Referenceable", **kwargs: Unpack[ListFilters]) -> list | str:
        """Return the data values (and literal data values) with a particular name.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_get_data_values_by_name`.
        """
        return run_sync(self._async_get_data_values_by_name(filter_string, body, start_from, page_size,
                                                            output_format, report_spec, **kwargs))

    @dynamic_catch
    async def _async_get_data_value_by_guid(self, data_value_guid: str,
                                            body: Optional[dict | GetRequestBody] = None,
                                            output_format: str = "JSON",
                                            report_spec: str | dict = "Referenceable",
                                            **kwargs: Unpack[GetFilters]) -> dict | str:
        """Return the properties of a data value (or literal data value). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        data_value_guid : str
            The GUID of the data value.
        body : dict | GetRequestBody, optional
            A GetRequestBody (asOfTime, effectiveTime, ...); it takes precedence over the other arguments.
        output_format : str, default "JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", "LIST", "MERMAID".
        report_spec : str | dict, default "Referenceable"
            The report spec that chooses the columns, for formats other than JSON.

        Returns
        -------
        dict | str
            The element, or NO_ELEMENTS_FOUND.

        Notes
        -----
        Sample body (getDataValueByGUID)::

            {"class" : "GetRequestBody", "asOfTime" : "2026-11-21T10:00:00Z",
             "effectiveTime" : "2026-11-21T10:00:00Z", "forLineage" : false, "forDuplicateProcessing" : false}
        """
        return await self._async_get_guid_request(
            e64_url(self.platform_url, self.view_server, DATA_VALUES_RETRIEVE, dataValueGUID=data_value_guid), _type=DATA_VALUE,
            _gen_output=self._generate_referenceable_output, body=body, output_format=output_format,
            report_spec=report_spec, **kwargs)

    @dynamic_catch
    def get_data_value_by_guid(self, data_value_guid: str, body: Optional[dict | GetRequestBody] = None,
                               output_format: str = "JSON", report_spec: str | dict = "Referenceable",
                               **kwargs: Unpack[GetFilters]) -> dict | str:
        """Return the properties of a data value (or literal data value).

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_get_data_value_by_guid`.
        """
        return run_sync(self._async_get_data_value_by_guid(data_value_guid, body, output_format, report_spec,
                                                           **kwargs))

    @dynamic_catch
    async def _async_find_data_values(self, search_string: str = "*",
                                      body: Optional[dict | SearchStringRequestBody] = None,
                                      starts_with: bool = True, ends_with: bool = False,
                                      ignore_case: bool = False, start_from: int = 0, page_size: int = 0,
                                      output_format: str = "JSON", report_spec: str | dict = "Referenceable",
                                      **kwargs: Unpack[SearchFilters]) -> list | str:
        """Return the data values (and literal data values) that contain the search string. Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        search_string : str, default "*"
            The string to search for; "*" matches every data value. Ignored when `body` is given.
        body : dict | SearchStringRequestBody, optional
            A SearchStringRequestBody; it takes precedence over the other arguments.
        starts_with, ends_with, ignore_case : bool
            How the search string matches.
        start_from : int, default 0
            The first result to return, when paging.
        page_size : int, default 0
            The most results to return (0 means the server's maximum).
        output_format : str, default "JSON"
            One of "JSON", "DICT", "MD", "FORM", "REPORT", "LIST", "MERMAID".
        report_spec : str | dict, default "Referenceable"
            The report spec that chooses the columns, for formats other than JSON.

        Accepts the standard search filters as keyword arguments (see ``SearchFilters``).

        Returns
        -------
        list | str
            The matching elements, or NO_ELEMENTS_FOUND.

        Notes
        -----
        Sample body (findDataValues)::

            {"class" : "SearchStringRequestBody", "searchString" : "Add value here", "startsWith" : false,
             "endsWith" : false, "ignoreCase" : true, "startFrom" : 0, "pageSize": 10}
        """
        return await self._async_find_request(e64_url(self.platform_url, self.view_server, DATA_VALUES_BY_SEARCH_STRING), _type=DATA_VALUE,
                                              _gen_output=self._generate_referenceable_output,
                                              search_string=search_string, body=body, starts_with=starts_with,
                                              ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, report_spec=report_spec, **kwargs)

    @dynamic_catch
    def find_data_values(self, search_string: str = "*", body: Optional[dict | SearchStringRequestBody] = None,
                         starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                         start_from: int = 0, page_size: int = 0, output_format: str = "JSON",
                         report_spec: str | dict = "Referenceable", **kwargs: Unpack[SearchFilters]) -> list | str:
        """Return the data values (and literal data values) that contain the search string.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_find_data_values`.
        """
        return run_sync(self._async_find_data_values(search_string, body, starts_with, ends_with, ignore_case,
                                                     start_from, page_size, output_format, report_spec,
                                                     **kwargs))

    # =========================================================================================================
    # Data-value links (Egeria 6.4, odpi/egeria#9463): DataValueSource, ProcessingVariable, EmbeddedDataValue
    #
    # Attach and detach take an optional body. With no body, no body is sent (Egeria accepts an attach with
    # no body or no properties). A body is sent as given; its properties class, when it has properties, must
    # be the relationship's own class, and `position` (ProcessingVariable, EmbeddedDataValue) must be an int:
    # 0 means unset, and it is passed through unchanged.
    # =========================================================================================================

    @dynamic_catch
    async def _async_link_data_value_source(self, data_value_guid: str, asset_guid: str,
                                            body: Optional[dict | NewRelationshipRequestBody] = None) -> str:
        """Attach a data value to the asset that describes the digital resource where its data is stored
        (a DataValueSource relationship). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        data_value_guid : str
            The GUID of the data value.
        asset_guid : str
            The GUID of the asset where the data is stored.
        body : dict | NewRelationshipRequestBody, optional
            Sent as given; with no body, no body is sent. Its properties, if any, are
            DataValueSourceProperties (label, description, effectiveFrom, effectiveTo).

        Returns
        -------
        str
            The GUID of the new relationship, or NO_GUID_RETURNED.

        Raises
        ------
        PyegeriaInvalidParameterException
            A properties class other than DataValueSourceProperties (refused locally).
        PyegeriaException
            Issues raised in communicating or server-side processing.

        Notes
        -----
        Sample body (linkDataValueSource)::

            {
              "class" : "NewRelationshipRequestBody",
              "properties": {
                "class" : "DataValueSourceProperties",
                "label": "add label here",
                "description": "add description here"
              }
            }
        """
        json_body = checked_body(body, "link_data_value_source", request_class="NewRelationshipRequestBody",
                                 properties_classes={DATA_VALUE_SOURCE_PROPERTIES})
        url = e64_url(self.platform_url, self.view_server, DATA_VALUE_SOURCES_ATTACH, dataValueGUID=data_value_guid, assetGUID=asset_guid)
        response = await self._async_make_request("POST", url, json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def link_data_value_source(self, data_value_guid: str, asset_guid: str,
                               body: Optional[dict | NewRelationshipRequestBody] = None) -> str:
        """Attach a data value to the asset where its data is stored (DataValueSource).

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_link_data_value_source`.

        Returns
        -------
        str
            The GUID of the new relationship, or NO_GUID_RETURNED.
        """
        return run_sync(self._async_link_data_value_source(data_value_guid, asset_guid, body))

    @dynamic_catch
    async def _async_detach_data_value_source(self, data_value_guid: str, asset_guid: str,
                                              body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a data value from the asset where its data is stored (DataValueSource). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        data_value_guid : str
            The GUID of the data value.
        asset_guid : str
            The GUID of the asset.
        body : dict | DeleteRelationshipRequestBody, optional
            Sent as given; with no body, no body is sent.

        Returns
        -------
        None
        """
        url = e64_url(self.platform_url, self.view_server, DATA_VALUE_SOURCES_DETACH, dataValueGUID=data_value_guid, assetGUID=asset_guid)
        await self._async_make_request("POST", url, checked_body(body, "detach_data_value_source", request_class="DeleteRelationshipRequestBody"))

    @dynamic_catch
    def detach_data_value_source(self, data_value_guid: str, asset_guid: str,
                                 body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a data value from the asset where its data is stored (DataValueSource).

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_detach_data_value_source`.
        """
        return run_sync(self._async_detach_data_value_source(data_value_guid, asset_guid, body))

    @dynamic_catch
    async def _async_link_processing_variable(self, element_guid: str, data_value_guid: str,
                                              body: Optional[dict | NewRelationshipRequestBody] = None) -> str:
        """Attach an element (such as a process) to a data value used to configure its processing
        (a ProcessingVariable relationship). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        element_guid : str
            The GUID of the element (for example a process) that uses the data value.
        data_value_guid : str
            The GUID of the data value.
        body : dict | NewRelationshipRequestBody, optional
            Sent as given; with no body, no body is sent. Its properties, if any, are
            ProcessingVariableProperties (label, description, position). `position` is an int and 0 means
            unset; it is passed through unchanged.

        Returns
        -------
        str
            The GUID of the new relationship, or NO_GUID_RETURNED.

        Raises
        ------
        PyegeriaInvalidParameterException
            A properties class other than ProcessingVariableProperties, or a position that is not an int
            (refused locally).
        PyegeriaException
            Issues raised in communicating or server-side processing.

        Notes
        -----
        Sample body (linkProcessingVariable)::

            {
              "class" : "NewRelationshipRequestBody",
              "properties": {
                "class" : "ProcessingVariableProperties",
                "label": "add label here",
                "description": "add description here",
                "position": 0
              }
            }
        """
        json_body = checked_body(body, "link_processing_variable", request_class="NewRelationshipRequestBody",
                                 properties_classes={PROCESSING_VARIABLE_PROPERTIES}, int_keys=("position",))
        url = e64_url(self.platform_url, self.view_server, PROCESSING_VARIABLES_ATTACH, elementGUID=element_guid, dataValueGUID=data_value_guid)
        response = await self._async_make_request("POST", url, json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def link_processing_variable(self, element_guid: str, data_value_guid: str,
                                 body: Optional[dict | NewRelationshipRequestBody] = None) -> str:
        """Attach an element (such as a process) to a data value that configures its processing.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_link_processing_variable`.

        Returns
        -------
        str
            The GUID of the new relationship, or NO_GUID_RETURNED.
        """
        return run_sync(self._async_link_processing_variable(element_guid, data_value_guid, body))

    @dynamic_catch
    async def _async_detach_processing_variable(self, element_guid: str, data_value_guid: str,
                                                body: Optional[dict | DeleteRelationshipRequestBody] = None
                                                ) -> None:
        """Detach an element (such as a process) from a data value that configures its processing
        (ProcessingVariable). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        element_guid : str
            The GUID of the element that uses the data value.
        data_value_guid : str
            The GUID of the data value.
        body : dict | DeleteRelationshipRequestBody, optional
            Sent as given; with no body, no body is sent.

        Returns
        -------
        None
        """
        url = e64_url(self.platform_url, self.view_server, PROCESSING_VARIABLES_DETACH, elementGUID=element_guid, dataValueGUID=data_value_guid)
        await self._async_make_request("POST", url, checked_body(body, "detach_processing_variable", request_class="DeleteRelationshipRequestBody"))

    @dynamic_catch
    def detach_processing_variable(self, element_guid: str, data_value_guid: str,
                                   body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach an element (such as a process) from a data value that configures its processing.

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_detach_processing_variable`.
        """
        return run_sync(self._async_detach_processing_variable(element_guid, data_value_guid, body))

    @dynamic_catch
    async def _async_link_embedded_data_value(self, parent_data_value_guid: str, embedded_data_value_guid: str,
                                              body: Optional[dict | NewRelationshipRequestBody] = None) -> str:
        """Embed a data value in another data value (an EmbeddedDataValue relationship). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        parent_data_value_guid : str
            The GUID of the data value that holds the embedded one.
        embedded_data_value_guid : str
            The GUID of the data value to embed.
        body : dict | NewRelationshipRequestBody, optional
            Sent as given; with no body, no body is sent. Its properties, if any, are
            EmbeddedDataValueProperties (label, description, position). `position` orders the embedded
            values: an int, 0 meaning unset, passed through unchanged.

        Returns
        -------
        str
            The GUID of the new relationship, or NO_GUID_RETURNED.

        Raises
        ------
        PyegeriaInvalidParameterException
            A properties class other than EmbeddedDataValueProperties, or a position that is not an int
            (refused locally).
        PyegeriaException
            Issues raised in communicating or server-side processing.

        Notes
        -----
        Sample body (linkEmbeddedDataValue)::

            {
              "class" : "NewRelationshipRequestBody",
              "properties": {
                "class" : "EmbeddedDataValueProperties",
                "label": "add label here",
                "description": "add description here",
                "position": 0
              }
            }
        """
        json_body = checked_body(body, "link_embedded_data_value", request_class="NewRelationshipRequestBody",
                                 properties_classes={EMBEDDED_DATA_VALUE_PROPERTIES}, int_keys=("position",))
        url = e64_url(self.platform_url, self.view_server, EMBEDDED_DATA_VALUES_ATTACH, parentDataValueGUID=parent_data_value_guid,
                            embeddedDataValueGUID=embedded_data_value_guid)
        response = await self._async_make_request("POST", url, json_body)
        return response.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def link_embedded_data_value(self, parent_data_value_guid: str, embedded_data_value_guid: str,
                                 body: Optional[dict | NewRelationshipRequestBody] = None) -> str:
        """Embed a data value in another data value (EmbeddedDataValue).

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_link_embedded_data_value`.

        Returns
        -------
        str
            The GUID of the new relationship, or NO_GUID_RETURNED.
        """
        return run_sync(self._async_link_embedded_data_value(parent_data_value_guid, embedded_data_value_guid,
                                                             body))

    @dynamic_catch
    async def _async_detach_embedded_data_value(self, parent_data_value_guid: str, embedded_data_value_guid: str,
                                                body: Optional[dict | DeleteRelationshipRequestBody] = None
                                                ) -> None:
        """Remove an embedded data value from its parent data value (EmbeddedDataValue). Async version.

        Needs Egeria 6.4 or later (odpi/egeria#9463).

        Parameters
        ----------
        parent_data_value_guid : str
            The GUID of the parent data value.
        embedded_data_value_guid : str
            The GUID of the embedded data value.
        body : dict | DeleteRelationshipRequestBody, optional
            Sent as given; with no body, no body is sent.

        Returns
        -------
        None
        """
        url = e64_url(self.platform_url, self.view_server, EMBEDDED_DATA_VALUES_DETACH, parentDataValueGUID=parent_data_value_guid,
                            embeddedDataValueGUID=embedded_data_value_guid)
        await self._async_make_request("POST", url, checked_body(body, "detach_embedded_data_value", request_class="DeleteRelationshipRequestBody"))

    @dynamic_catch
    def detach_embedded_data_value(self, parent_data_value_guid: str, embedded_data_value_guid: str,
                                   body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Remove an embedded data value from its parent data value (EmbeddedDataValue).

        Needs Egeria 6.4 or later (odpi/egeria#9463). See `_async_detach_embedded_data_value`.
        """
        return run_sync(self._async_detach_embedded_data_value(parent_data_value_guid, embedded_data_value_guid,
                                                               body))
