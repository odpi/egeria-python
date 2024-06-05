"""

This module contains the MyProfile class and its methods.

"""
import asyncio
import json

from pyegeria._client import Client
from pyegeria._validators import validate_name, validate_search_string


class MyProfile(Client):
    """A class representing the profile of a user.

    This class provides methods for retrieving the profile details
    of a user associated with a token.

    Parameters
    ----------
    server_name : str
        The name of the view server to configure.
    platform_url : str
        The URL of the platform.
    token : str, optional
        The token associated with the user. Default is None.
    user_id : str, optional
        The user ID. Default is None.
    user_pwd : str, optional
        The user password. Default is None.
    sync_mode : bool, optional
        The flag indicating whether to use synchronous mode. Default
        is True.
    """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            token: str = None,
            user_id: str = None,
            user_pwd: str = None,
            sync_mode: bool = True
    ):

        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token, async_mode=sync_mode)
        self.my_profile_command_root: str = f"{platform_url}/servers"

    #
    #       MyProfile
    #

    async def _async_get_my_profile(self, server_name: str = None) -> dict | str:
        """ Get the profile of the user associated with the token used.

        Parameters
        ----------
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        List | str

        Profile details as a dict.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name
        url = f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile"

        response = await self._async_make_request("GET", url)
        return response

    def get_my_profile(self, server_name: str = None) -> dict | str:
        """ Get the profile of the user associated with the token used.

                Parameters
                ----------
                server_name : str, optional
                    The name of the server to  configure.
                    If not provided, the server name associated with the instance is used.

                Returns
                -------
                List | str

                Profile details as a dict.

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
        response = loop.run_until_complete(self._async_get_my_profile(server_name))

        return response.json().get("personalProfile", "No one found")

    async def _async_get_assigned_actions(self, actor_guid: str, status: str = "OPEN", server_name: str = None,
                                          start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get assigned actions for the actor. Async version.

        Parameters
        ----------
        actor_guid: str
            The GUID of the actor whose assigned actions are to be retrieved.
        status: str
            The status of teh action to filter on. Default value is "OPEN".
        server_name: str, optional
            The name of the server. If not provided, the value of self.server_name will be used.
        start_from: int, optional
            The index from which to start retrieving the assigned actions. Default is 0.
        page_size: int, optional
            The number of assigned actions to retrieve per page. Default is 100.

        Returns
        -------
        list or str
            A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name

        if page_size is None:
            page_size = self.page_size

        body = {"status": status}

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/actors/{actor_guid}"
               f"/assigned/to-dos?startFrom={start_from}&pageSize={page_size}&")

        response = await self._async_make_request("POST", url, body)

        return response.json().get("toDoElements", "No entries found")

    def get_assigned_actions(self, actor_guid: str, status: str = "OPEN", server_name: str = None, start_from: int = 0,
                             page_size: int = 100) -> list | str:
        """ Get assigned actions for the actor.
        Parameters
        ----------
        actor_guid: str
            The GUID of the actor whose assigned actions are to be retrieved.
        status: str
            The status of teh action to filter on. Default value is "OPEN".
        server_name: str, optional
            The name of the server. If not provided, the value of self.server_name will be used.
        start_from: int, optional
            The index from which to start retrieving the assigned actions. Default is 0.
        page_size: int, optional
            The number of assigned actions to retrieve per page. Default is 100.

        Returns
        -------
        list or str
            A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

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
            self._async_get_assigned_actions(actor_guid, status, server_name,
                                             start_from, page_size)
        )

        return response

    async def _async_get_actions_for_action_target(self, element_guid: str, status: str = "OPEN",
                                                   server_name: str = None,
                                                   start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get actions assigned to the action target. Async version.

            Parameters
            ----------
            element_guid: str
                The GUID of the target whose assigned actions are to be retrieved.
            status: str
                The status of teh action to filter on. Default value is "OPEN".
            server_name: str, optional
                The name of the server. If not provided, the value of self.server_name will be used.
            start_from: int, optional
                The index from which to start retrieving the assigned actions. Default is 0.
            page_size: int, optional
                The number of assigned actions to retrieve per page. Default is 100.

            Returns
            -------
            list or str
                A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
            """
        if server_name is None:
            server_name = self.server_name

        validate_name(element_guid)

        body = {"status": status}

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/elements/{element_guid}"
               f"/action-targets/to-dos?start-from={start_from}&page-size={page_size}")

        response = await self._async_make_request("POST", url, body)
        return response.json() if response is not None else "No Results"

    def get_actions_for_action_target(self, element_guid: str, status: str = "OPEN", server_name: str = None,
                                      start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get actions assigned to the action target.

            Parameters
            ----------
            element_guid: str
                The GUID of the target whose assigned actions are to be retrieved.
            status: str
                The status of teh action to filter on. Default value is "OPEN"
            server_name: str, optional
                The name of the server. If not provided, the value of self.server_name will be used.
            start_from: int, optional
                The index from which to start retrieving the assigned actions. Default is 0.
            page_size: int, optional
                The number of assigned actions to retrieve per page. Default is 100.

            Returns
            -------
            list or str
                A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

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
            self._async_get_actions_for_action_target(element_guid, status, server_name,
                                                      start_from, page_size)
        )

        return response

    async def _async_get_actions_for_sponsor(self, element_guid: str, status: str = "", server_name: str = None,
                                             start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get actions assigned to an owner. Async version.

            Parameters
            ----------
            element_guid: str
                The GUID of the target whose assigned actions are to be retrieved.
            status: str
                The status of the action to filter on. Default value is "OPEN".
            server_name: str, optional
                The name of the server. If not provided, the value of self.server_name will be used.
            start_from: int, optional
                The index from which to start retrieving the assigned actions. Default is 0.
            page_size: int, optional
                The number of assigned actions to retrieve per page. Default is 100.

            Returns
            -------
            list or str
                A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

            Raises
            ------
            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
            """
        if server_name is None:
            server_name = self.server_name

        validate_name(element_guid)

        body = {"status": status}

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/elements/{element_guid}"
               f"/sponsored/to-dos?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url, body)
        return response.json() if response is not None else "No Results"

    def get_actions_for_sponsor(self, element_guid: str, status: str = "OPEN", server_name: str = None,
                                start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get actions assigned to an owner.
            Parameters
            ----------
            element_guid: str
                The GUID of the target whose assigned actions are to be retrieved.
            status: str
                The status of teh action to filter on. Default value is "OPEN".
            server_name: str, optional
                The name of the server. If not provided, the value of self.server_name will be used.
            start_from: int, optional
                The index from which to start retrieving the assigned actions. Default is 0.
            page_size: int, optional
                The number of assigned actions to retrieve per page. Default is 100.

            Returns
            -------
            list or str
                A list of assigned actions is returned. If there aren't any, a string is returned indicating that.

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
        response = loop.run_until_complete(self._async_get_actions_for_sponsor(
            element_guid, status, server_name, start_from, page_size)
        )
        return response

    async def _async_create_to_do(self, body: dict, server_name: str = None) -> str:
        """ Create a To-Do item. Async version.
        Parameters
        ----------
        body : dict
                    The dictionary containing the details of the to-do item.
        server_name : str, optional
            The name of the server where the to-do item will be created. If not provided,
            the default server name associated with the instance of the class will be used.

        Returns
        -------
        None
            This method does not return any value.

        Raises
        ------
        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
        """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos"
        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid", "No guid returned")

    def create_to_do(self, body: dict, server_name: str = None) -> None:
        """ Create a To-Do item.
            Parameters
            ----------
            body : dict
                The dictionary containing the details of the to-do item.
            server_name : str, optional
                The name of the server where the to-do item will be created. If not provided,
                the default server name associated with the instance of the class will be used.

            Returns
            -------
            None
                This method does not return any value.

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

            Here is a typical body:
            body = {
                    "properties": {
                        "class" : "ToDoProperties",
                        "qualifiedName": f"Test-To-Do-{time.asctime()}",
                        "name": to_do,
                        "description": to_do_desc,
                        "toDoType": to_do_type,
                        "priority": 0,
                        "dueTime": "2024-03-11T15:42:11.307Z",
                        "status": "OPEN"
                    },
                "assignToActorGUID": erins_guid
        }
            """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_to_do(body, server_name)
        )
        return response

    async def _async_get_to_do(self, todo_guid: str, server_name: str = None) -> dict | str:
        """ Get a To-Do item. Async version.
           Parameters
           ----------
           todo_guid: str
                Identifier of the To-Do item.
           server_name : str, optional
               The name of the server where the to-do item will be created. If not provided,
               the default server name associated with the instance of the class will be used.

           Returns
           -------
           None
               This method does not return any value.

           Raises
           ------
           InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values
           PropertyServerException
             Raised by the server when an issue arises in processing a valid request
           NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action
           """
        if server_name is None:
            server_name = self.server_name

        validate_name(todo_guid)

        url = f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/{todo_guid}"

        response = await self._async_make_request("GET", url)
        # return response.text if response is not None else "No Results"
        return json.loads(response.text).get("toDoElement", "No TODO returned")

    def get_to_do(self, todo_guid: str, server_name: str = None) -> dict | str:
        """ Get a To-Do item. Async version.
           Parameters
           ----------
           todo_guid: str
                Identifier of the To-Do item.
           server_name : str, optional
               The name of the server where the to-do item will be created. If not provided,
               the default server name associated with the instance of the class will be used.

           Returns
           -------
           None
               This method does not return any value.

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
        response = loop.run_until_complete(self._async_get_to_do(todo_guid, server_name))

        return response

    async def _async_update_to_do(self, todo_guid: str, body: dict, is_merge_update: bool = True,
                                  server_name: str = None) -> None:
        """ Update a To-Do item. Async version.
            Parameters
            ----------
            todo_guid: str
              Identifier of the To-Do item.
            body: str
                The details to update the to-do item with.
            server_name : str, optional
             The name of the server where the to-do item will be created. If not provided,
             the default server name associated with the instance of the class will be used.

            Returns
            -------
            None
             This method does not return any value.

            Raises
            ------
            InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
            Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
            """
        if server_name is None:
            server_name = self.server_name

        validate_name(todo_guid)

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/"
               f"{todo_guid}?merge-update={is_merge_update}")

        await self._async_make_request("POST", url, body)
        return

    def update_to_do(self, todo_guid: str, body: dict, is_merge_update: bool = True,
                     server_name: str = None) -> None:
        """ Update a To-Do item.
            Parameters
            ----------
            todo_guid: str
              Identifier of the To-Do item.
            body: str
                The details to update the to-do item with.
            is_merge_update: bool [default: True]
                If true then merges the updated information, otherwise replace the existing information.
            server_name : str, optional
             The name of the server where the to-do item will be created. If not provided,
             the default server name associated with the instance of the class will be used.

            Returns
            -------
            None
             This method does not return any value.

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
        loop.run_until_complete(self._async_update_to_do(todo_guid, body, is_merge_update, server_name))
        return

    async def _async_delete_to_do(self, todo_guid: str, status: str = "OPEN", server_name: str = None) -> None:
        """ Delete a To-Do item. Async version.
            Parameters
            ----------
            todo_guid: str
              Identifier of the To-Do item.
            status: str
                Filter items to match this status. Defaults to "OPEN"
            server_name : str, optional
             The name of the server where the to-do item will be created. If not provided,
             the default server name associated with the instance of the class will be used.

            Returns
            -------
            None
             This method does not return any value.

            Raises
            ------
            InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
            Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
            """
        if server_name is None:
            server_name = self.server_name

        validate_name(todo_guid)
        body = {"status": status}

        url = f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/{todo_guid}"

        await self._async_make_request("POST", url, body)
        return

    def delete_to_do(self, todo_guid: str, status: str = "OPEN", server_name: str = None) -> None:
        """ Delete a To-Do item.
            Parameters
            ----------
            todo_guid: str
              Identifier of the To-Do item.
            status: str
                Filter items to match this status. Defaults to "OPEN"
            server_name : str, optional
             The name of the server where the to-do item will be created. If not provided,
             the default server name associated with the instance of the class will be used.

            Returns
            -------
            None
             This method does not return any value.

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
        loop.run_until_complete(self._async_delete_to_do(todo_guid, status, server_name))
        return

    async def _async_reassign_to_do(self, todo_guid: str, actor_guid: str, status: str = "OPEN",
                                    server_name: str = None) -> None:
        """ Reassign a To-Do item. Async version.
           Parameters
           ----------
            todo_guid: str
                Identifier of the To-Do item.
            actor_guid: str
                The actor to receive the reassigned to-do item.
            status: str [default = "OPEN"]
                Filter items to match this status.
            server_name : str, optional
                The name of the server where the to-do item will be created. If not provided,
                the default server name associated with the instance of the class will be used.

           Returns
           -------
           None
            This method does not return any value.

           Raises
           ------
           InvalidParameterException
           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
           PropertyServerException
           Raised by the server when an issue arises in processing a valid request
           NotAuthorizedException
           The principle specified by the user_id does not have authorization for the requested action
           """
        if server_name is None:
            server_name = self.server_name

        validate_name(todo_guid)
        validate_name(actor_guid)
        body = {"status": status}

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/"
               f"{todo_guid}/reassign/{actor_guid}")

        await self._async_make_request("POST", url, body)
        return

    def reassign_to_do(self, todo_guid: str, actor_guid: str, status: str = "OPEN", server_name: str = None) -> None:
        """ Reassign a To-Do item.
           Parameters
           ----------
            todo_guid: str
                Identifier of the To-Do item.
            actor_guid: str
                The actor to receive the reassigned to-do item.
            status: str [default = "OPEN"]
                Filter items to match this status.
            server_name : str, optional
                The name of the server where the to-do item will be created. If not provided,
                the default server name associated with the instance of the class will be used.

           Returns
           -------
           None
            This method does not return any value.

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
        loop.run_until_complete(self._async_reassign_to_do(todo_guid, actor_guid, status, server_name))
        return

    async def _async_find_to_do(self, search_string: str = "*", server_name: str = "None", status: str = "OPEN",
                                starts_with: bool = False, ends_with: bool = False, ignore_case: bool = True,
                                start_from: int = 0, page_size: int = 100) -> list | str:
        """ find To-Do items. Async version.
              Parameters
              ----------
                search_string: str
                   String to search against. If '*' then all to-do items will match.
                server_name : str, optional
                   The name of the server where the to-do item will be created. If not provided,
                   the default server name associated with the instance of the class will be used.
                status: str
                   Filter items to match this status. Defaults to "OPEN"
                starts_with : bool, [default=False], optional
                   Starts with the supplied string.
                ends_with : bool, [default=False], optional
                       Ends with the supplied string
                ignore_case : bool, [default=False], optional
                       Ignore case when searching
              Returns
              -------
              None
               List of To-Do items that match the criteria

              Raises
              ------
              InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
              PropertyServerException
              Raised by the server when an issue arises in processing a valid request
              NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action
              """
        if server_name is None:
            server_name = self.server_name

        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()

        if search_string == '*':
            search_string = " "

        body = {
            "class": "ToDoStatusSearchString",
            "toDoStatus": status,
            "searchString": search_string
        }

        validate_search_string(search_string)

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/"
               f"find-by-search-string?startFrom={start_from}&pageSize={page_size}&"
               f"startsWith={starts_with_s}&endsWith={ends_with_s}&ignoreCase={ignore_case_s}")

        response = await self._async_make_request("POST", url, body)
        # return response.text
        return response.json().get("toDoElements", "No ToDos found")

    def find_to_do(self, search_string: str, server_name: str = None, status: str = "OPEN",
                   starts_with: bool = False, ends_with: bool = False, ignore_case: bool = True,
                   start_from: int = 0, page_size: int = 100) -> list | str:
        """ find To-Do items.
            Parameters
            ----------
           search_string: str
              String to search against. If '*' then all to-do items will match.
           server_name : str, optional
              The name of the server where the to-do item will be created. If not provided,
              the default server name associated with the instance of the class will be used.
           status: str
              Filter items to match this status. Defaults to "OPEN"
           starts_with : bool, [default=False], optional
              Starts with the supplied string.
           ends_with : bool, [default=False], optional
                  Ends with the supplied string
           ignore_case : bool, [default=False], optional
                  Ignore case when searching
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
         Returns
         -------
         None
          List of To-Do items that match the criteria

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
        response = loop.run_until_complete(self._async_find_to_do(search_string, server_name, status, starts_with,
                                                                  ends_with, ignore_case, start_from, page_size))
        return response

    async def _async_get_to_dos_by_type(self, todo_type: str,  server_name: str = None, status: str = "OPEN",
                                        start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get To-Do items by type. Async version
            Parameters
            ----------
            todo_type: str
              Type of to-do to find
            server_name : str, optional
              The name of the server where the to-do item will be created. If not provided,
              the default server name associated with the instance of the class will be used.
            status: str
              Filter items to match this status. Defaults to "OPEN"
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            Returns
            -------
            List of To-Do items that match the criteria

            Raises
            ------
            InvalidParameterException
            If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
            Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
            The principle specified by the user_id does not have authorization for the requested action
            """
        if server_name is None:
            server_name = self.server_name

        validate_name(todo_type)
        body = {
            "status": status,

        }

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/types/"
               f"{todo_type}?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("toDoElements","No ToDos found")

    def get_to_dos_by_type(self, todo_type: str,  server_name: str = None, status: str = "OPEN",
                           start_from: int = 0, page_size: int = 100) -> list | str:
        """ Get To-Do items by type.
            Parameters
            ----------
            todo_type: str
              Type of to-do to find
            server_name : str, optional
              The name of the server where the to-do item will be created. If not provided,
              the default server name associated with the instance of the class will be used.
            status: str
              Filter items to match this status. Defaults to "OPEN"
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            Returns
            -------
            List of To-Do items that match the criteria

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
        response = loop.run_until_complete(self._async_get_to_dos_by_type(todo_type,  server_name, status,
                                                                          start_from, page_size))
        return response

    async def _async_update_action_target_properties(self, action_target_guid: str, body: dict,
                                                     is_merge_update: bool = True, server_name: str = None) -> None:
        """ Get To-Do items by type. Async version
           Parameters
           ----------
            action_target_guid: str
                Identity of the action target to update.
            body: dict
                Details of the updates to make.
            is_merge_update : bool, [default=True], optional
                indicates if the update should be a merge or replacement.
            server_name : str, optional
              The name of the server where the to-do item will be created. If not provided,
              the default server name associated with the instance of the class will be used.
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
           """
        if server_name is None:
            server_name = self.server_name

        is_merge_update_t = str(is_merge_update).lower()

        validate_name(action_target_guid)

        url = (f"{self.my_profile_command_root}/{server_name}/api/open-metadata/my-profile/to-dos/"
               f"action-targets/{action_target_guid}?is_merge_update={is_merge_update_t}")

        await self._async_make_request("POST", url, body)
        return

    def update_action_target_properties(self, action_target_guid: str, body: dict,
                                        is_merge_update: bool = True, server_name: str = None) -> None:
        """ Get To-Do items by type.
           Parameters
           ----------
            action_target_guid: str
                Identity of the action target to update.
            body: dict
                Details of the updates to make.
            is_merge_update : bool, [default=True], optional
                indicates if the update should be a merge or replacement.
            server_name : str, optional
              The name of the server where the to-do item will be created. If not provided,
              the default server name associated with the instance of the class will be used.
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
           """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_action_target_properties(action_target_guid,
                                                                            body, is_merge_update,
                                                                            server_name))
        return
