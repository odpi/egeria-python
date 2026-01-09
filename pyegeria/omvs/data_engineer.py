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
    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None, token: str = None):
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
    async def _async_find_tabular_data_sets(self, search_string: str | None,
                                            body: dict | SearchStringRequestBody = None,
                                            start_from: int = 0, page_size: int = 0,
                                            output_format: str = "JSON", report_spec: str = None) -> dict:
        """ Retrieve the list of asset metadata elements of type tabular data set optionally filtered by search_string.
         Async version.

        Parameters
        ----------
        search_string: str | None, optional
            Search string to filter by - if `*` or `None` then all tabular data sets are returned.
        body: dict | SearchStringRequestBody, optional
            If provided, details of the search that allow more specific criteria. Overrides search_string..
        Returns
        -------
        dict - the list of tabular data sets

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        sample:
        {
          "class": "SearchStringRequestBody",
          "searchString": "{{$searchString}}",
          "metadataElementTypeName": "TabularDataSet",
          "skipClassifiedElements": ["Template"]
        }

    """
        url = str(HttpUrl(f"{self.command_root}/assets/by-search-string"))
        if body is None:
            body = SearchStringRequestBody(class_="SearchStringRequestBody",search_string=search_string, metadata_element_type_name="TabularDataSet",
                                          skip_classified_elements=["Template"])
        response = await self._async_find_request(url, _type="TabularDataSet",
                                                  _gen_output=_generate_default_output,
                                                  search_string=search_string, output_format=output_format,
                                                  report_spec = report_spec,start_from = start_from, page_size=page_size,
                                                  body=body)

        return response

    @dynamic_catch
    def find_tabular_data_sets(self, search_string: str | None, body: dict | SearchStringRequestBody = None,
                               start_from: int = 0, page_size: int = 0,
                               output_format: str = "JSON", report_spec: str = None
                               ) -> dict:
        """ Retrieve the list of asset metadata elements of type tabular data set optionally filtered by search_string.

        Parameters
        ----------
        search_string: str | None, optional
            Search string to filter by - if `*` or `None` then all tabular data sets are returned.
        body: dict | SearchStringRequestBody, optional
            If provided, details of the search that allow more specific criteria. Overrides search_string..
        Returns
        -------
        dict - the list of tabular data sets

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        sample:
        {
          "class": "SearchStringRequestBody",
          "searchString": "{{$searchString}}",
          "metadataElementTypeName": "TabularDataSet",
          "skipClassifiedElements": ["Template"]
        }

    """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_tabular_data_sets(search_string, body,
                                             start_from, page_size, output_format, report_spec)
        )
        return response

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