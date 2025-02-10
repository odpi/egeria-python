"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module provides access to the metadata-explorer OMVS module.

https://egeria-project.org/concepts/information-supply-chain

"""

import asyncio
import os
import sys

from httpx import Response

from pyegeria.utils import body_slimmer
from pyegeria._client import Client, max_paging_size
from pyegeria._globals import NO_ELEMENTS_FOUND
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))



DEFAULT_BODY_SKELETON = {
    "effective_time": None,
    "limitResultsByStatus": ["ACTIVE"],
    "asOfTime": None,
    "sequencingOrder": None,
    "sequencingProperty": None,
    "filter": None,
}


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
    return f"{client.platform_url}/servers/{view_server}/api/open-metadata/metadata-explorer"


class SolutionArchitect(Client):
    """SolutionArchitect is a class that extends the Client class. The Solution Architect OMVS provides APIs for
      searching for architectural elements such as information supply chains, solution blueprints, solution components
      and component implementations.

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
        user_id: str = None,
        user_pwd: str = None,
        token: str = None,
    ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.solution_architect_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}"
            f"/api/open-metadata/solution-architect"
        )
        Client.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )

    #
    #
    #

    async def _async_find_information_supply_chains(
        self,
        filter: str = "*",
        add_implementation: bool = True,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the list of information supply chain metadata elements that contain the search string.
           https://egeria-project.org/concepts/information-supply-chain
           Async version.

        Parameters
        ----------
        filter : str
            - search_filter string to search for.
        add_implementation : bool, [default=True], optional
            - add_implementation flag to include information supply chain implementations details..
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("addImplementation", add_implementation),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
            ]
        )

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

        if body is None:
            body = {
                "filter": search_filter,
            }
        else:
            body["filter"] = search_filter

        url = (
            f"{self.solution_architect_command_root}/information-supply-chains/by-search-string"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_information_supply_chains(
        self,
        filter: str = "*",
        add_implementation: bool = True,
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the list of information supply chain metadata elements that contain the search string.
          https://egeria-project.org/concepts/information-supply-chain

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        add_implementation : bool, [default=True], optional
            - add_implementation flag to include information supply chain implementations details..
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_information_supply_chains(
                filter,
                add_implementation,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                body,
            )
        )
        return response

    def find_all_information_supply_chains(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list[dict] | str:
        """Retrieve a list of all information supply chains
        https://egeria-project.org/concepts/information-supply-chain
        """

        return self.find_information_supply_chains(
            "*", start_from=start_from, page_size=page_size
        )

    async def _async_find_solution_blueprints(
        self,
        filter: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the solution blueprint elements that contain the search string.
           https://egeria-project.org/concepts/solution-blueprint
           Async version.

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of solution blueprint structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
            ]
        )

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

        if body is None:
            body = {
                "filter": search_filter,
            }
        else:
            body["filter"] = search_filter

        url = (
            f"{self.solution_architect_command_root}/solution-blueprints/by-search-string"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_solution_blueprints(
        self,
        filter: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the list of solution blueprint elements that contain the search string.
           https://egeria-project.org/concepts/solution-blueprint

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_blueprints(
                filter,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                body,
            )
        )
        return response

    def find_all_solution_blueprints(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/solution-blueprint
        """
        return self.find_solution_blueprints(
            "*", start_from=start_from, page_size=page_size
        )

    async def _async_find_solution_roles(
        self,
        filter: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the solutio nrole elements that contain the search string.
           https://egeria-project.org/concepts/actor
           Async version.

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of solution role structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
            ]
        )

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

        if body is None:
            body = {
                "filter": search_filter,
            }
        else:
            body["filter"] = search_filter

        url = (
            f"{self.solution_architect_command_root}/solution-roles/by-search-string"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_solution_roles(
        self,
        filter: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the list of solution role elements that contain the search string.
           https://egeria-project.org/concepts/actor

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_roles(
                filter,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                body,
            )
        )
        return response

    def find_all_solution_roles(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list[dict] | str:
        """Retrieve a list of all solution blueprint elements
        https://egeria-project.org/concepts/actor
        """
        return self.find_solution_roles("*", start_from=start_from, page_size=page_size)

    async def _async_find_solution_components(
        self,
        filter: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the solution component elements that contain the search string.
           https://egeria-project.org/concepts/solution-components
           Async version.

        Parameters
        ----------
        filter: str
            - search_filterstring to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of solution blueprint structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
            ]
        )

        if filter is None or filter == "*":
            search_filter = None
        else:
            search_filter = filter

        if body is None:
            body = {
                "filter": search_filter,
            }
        else:
            body["filter"] = search_filter

        url = (
            f"{self.solution_architect_command_root}/solution-components/by-search-string"
            f"{possible_query_params}"
        )
        response: Response = await self._async_make_request(
            "POST", url, body_slimmer(body)
        )
        return response.json().get("elements", NO_ELEMENTS_FOUND)

    def find_solution_components(
        self,
        filter: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = False,
        start_from: int = 0,
        page_size: int = max_paging_size,
        body: dict = None,
    ) -> list[dict] | str:
        """Retrieve the list of solution component elements that contain the search string.
           https://egeria-project.org/concepts/solution-components

        Parameters
        ----------
        filter : str
            - filter string to search for.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        body: dict, optional, default = None
            - additional optional specifications for the search.

        Returns
        -------
        list[dict] | str
            A list of information supply chain structures or a string if there are no elements found.

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_find_solution_components(
                filter,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                body,
            )
        )
        return response

    def find_all_solution_components(
        self, start_from: int = 0, page_size: int = max_paging_size
    ) -> list[dict] | str:
        """Retrieve a list of all solution component elements
        https://egeria-project.org/concepts/solution-components
        """
        return self.find_solution_components(
            "*", start_from=start_from, page_size=page_size
        )


if __name__ == "__main__":
    print("Main-Metadata Explorer")
