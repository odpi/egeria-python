"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Access tabular data sets

"""
import asyncio

from pydantic import HttpUrl

from pyegeria.core._exceptions import PyegeriaException
from pyegeria.core.utils import dynamic_catch, transform_json_to_tabular
from pyegeria.core._server_client import ServerClient
from pyegeria.models import SearchStringRequestBody
from pyegeria.view.output_formatter import _generate_default_output
from typing import Any, Optional

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
    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: Optional[str] = None, token: str = None):
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
        """
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        self.command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/data-engineer")

    @dynamic_catch
    async def _async_find_tabular_data_sets(self, search_string: str = "*",
                                            starts_with: bool = True, ends_with: bool = False,
                                            ignore_case: bool = False,
                                            anchor_domain: Optional[str] = None,
                                            metadata_element_type: str = "TabularDataSet",
                                            metadata_element_subtypes: Optional[list[str]] = None,
                                            skip_relationships: Optional[list[str]] = None,
                                            include_only_relationships: Optional[list[str]] = None,
                                            skip_classified_elements: list[str] = ["Template"],
                                            include_only_classified_elements: Optional[list[str]] = None,
                                            graph_query_depth: int = 3,
                                            governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                                            effective_time: Optional[str] = None, relationship_page_size: int = 0,
                                            limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                                            sequencing_property: Optional[str] = None,
                                            output_format: str = "JSON",
                                            report_spec: str | dict = "Referenceable",
                                            start_from: int = 0, page_size: int = 100,
                                            property_names: Optional[list[str]] = None,
                                            body: Optional[dict | SearchStringRequestBody] = None) -> list | str:
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
        response = await self._async_find_request(url, _type="TabularDataSet", _gen_output=self._generate_referenceable_output,
                                                  search_string=search_string, starts_with=starts_with,
                                                  ends_with=ends_with, ignore_case=ignore_case,
                                                  anchor_domain=anchor_domain,
                                                  metadata_element_type=metadata_element_type,
                                                  metadata_element_subtypes=metadata_element_subtypes,
                                                  skip_relationships=skip_relationships,
                                                  include_only_relationships=include_only_relationships,
                                                  skip_classified_elements=skip_classified_elements,
                                                  include_only_classified_elements=include_only_classified_elements,
                                                  graph_query_depth=graph_query_depth,
                                                  governance_zone_filter=governance_zone_filter,
                                                  as_of_time=as_of_time, effective_time=effective_time,
                                                  relationship_page_size=relationship_page_size,
                                                  limit_results_by_status=limit_results_by_status,
                                                  sequencing_order=sequencing_order,
                                                  sequencing_property=sequencing_property,
                                                  output_format=output_format, report_spec=report_spec,
                                                  start_from=start_from, page_size=page_size,
                                                  property_names=property_names, body=body)

        return response

    @dynamic_catch
    def find_tabular_data_sets(self, search_string: str = "*",
                               starts_with: bool = True, ends_with: bool = False,
                               ignore_case: bool = False,
                               anchor_domain: Optional[str] = None,
                               metadata_element_type: str = "TabularDataSet",
                               metadata_element_subtypes: Optional[list[str]] = None,
                               skip_relationships: Optional[list[str]] = None,
                               include_only_relationships: Optional[list[str]] = None,
                               skip_classified_elements: list[str] = ["Template"],
                               include_only_classified_elements: Optional[list[str]] = None,
                               graph_query_depth: int = 3,
                               governance_zone_filter: Optional[list[str]] = None, as_of_time: Optional[str] = None,
                               effective_time: Optional[str] = None, relationship_page_size: int = 0,
                               limit_results_by_status: Optional[list[str]] = None, sequencing_order: Optional[str] = None,
                               sequencing_property: Optional[str] = None,
                               output_format: str = "JSON",
                               report_spec: str | dict = "Referenceable",
                               start_from: int = 0, page_size: int = 100,
                               property_names: Optional[list[str]] = None,
                               body: Optional[dict | SearchStringRequestBody] = None) -> list | str:
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
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_find_tabular_data_sets(search_string=search_string,
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
                                                                         property_names=property_names,
                                                                         body=body))

    @dynamic_catch
    def get_tabular_data_set(self, tabular_data_set_guid: str, start_from_row: int = 0, max_row_count: int = 5000,
                             output_format: str = "JSON") -> dict:
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
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_tabular_data_set(tabular_data_set_guid, start_from_row, max_row_count, output_format)
        )
        return response

    @dynamic_catch
    async def _async_get_tabular_data_set(self, tabular_data_set_guid:str, start_from_row:int = 0, max_row_count: int = 5000,
                                          output_format: str = "JSON") -> dict:
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
        url = str(HttpUrl(f"{self.command_root}/tabular-data-sets/{tabular_data_set_guid}/report?"
                          f"startFromRow={start_from_row}&MaxRowCount={max_row_count}"))
        response = await self._async_make_request("GET", url)
        el_list = response.json().get('tabularDataSetReport',"No Dataset Found")
        if isinstance(el_list, dict):
            if output_format == "JSON":
                return el_list
            elif output_format == "CSV":
                return transform_json_to_tabular(response, output_format="CSV")
            elif output_format == "RICH-TABLE":
                return transform_json_to_tabular(response, output_format="RICH-TABLE")
            else:
                raise PyegeriaException(f"Unsupported output format: {output_format}")
        else:
            raise PyegeriaException(f"Unsupported output format: {output_format}")