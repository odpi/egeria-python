"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 This module is incomplete.
 The methods to author governance processes are transitioning to this module.

"""

from requests import Response

from pyegeria._exceptions import (
    InvalidParameterException,
)
from pyegeria import Platform, AutomatedCuration
import asyncio


class GovernanceAuthor(AutomatedCuration):
    """
    Client to issue Curation requests.

    Attributes:

        server_name: str
                Name of the server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        verify_flag: bool
            Flag to indicate if SSL Certificates should be verified in the HTTP requests.
            Defaults to False.

    Methods:

    """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
        ):
        AutomatedCuration.__init__(self, server_name, platform_url, user_id,
                          user_pwd, verify_flag)
        self.cur_command_root = f"{platform_url}/servers/"

    async def _async_create_element_from_template(self, body:str, server:str = None)-> str:
        """ Create a metadata element from a template.  Async version.
            Parameters
            ----------
            body : str
                The json body used to instantiate the template.
            server : str, optional
               The name of the server to get governance engine summaries from. If not provided, the default server name will be used.

            Returns
            -------
            Response
               The guid of the resulting element

        """
        if server is None:
           server = self.server_name

        url = f"{self.platform_url}/servers/{server}/open-metadata/automate-curation/catalog-templates/new-element"

        response = await self._async_make_request("POST", url, body)
        return response.json().get("guid")


    async def _async_find_gov_action_types(self, search_string: str='*', server_name:str=None)-> dict | str:
        pass

    async def _async_get_gov_action_types_by_name(self, server_name:str=None) -> dict | str:
        pass

    async def _async_find_gov_action_types_by_guid(self, guid: str, server_name:str=None) -> dict | str:
        pass

    # Governance Action Processes

    # async def _async_create_gov_action_process(self, body: dict, server_name:str=None) -> None:
    #     pass
    #
    # async def _async_update_gov_action_process(self, process_id: str, body: dict, server_name:str=None) -> None:
    #     pass
    #
    # async def _async_publish_gov_action_process(self, process_id:str, server_name:str=None) -> None:
    #     pass
    #
    # async def _async_withdraw_gov_action_process(self, process_id:str, server_name:str=None) -> None:
    #     pass
    #
    # async def _async_remove_gov_action_process(self, process_id: str, server_name: str = None) -> None:
    #     pass

    async def _async_find_gov_action_processes(self, search_string:str, server_name:str=None) -> dict | str:
        pass

    async def _async_get_gov_action_processes_by_name(self, name:str, server_name:str=None) -> dict | str:
        pass

    async def _async_get_gov_action_processes_by_guid(self, guid:str, server_name:str=None) -> dict | str:
        pass

    async def _async_get_gov_action_process_graph(self, guid:str, server_name:str=None) -> dict | str:
        pass

# Process Steps
#     async def _async_create_gov_action_process_step(self, body: dict, server_name:str=None) -> None:
#         pass
#
#     async def _async_update_gov_action_process_step(self, guid: str, body: dict, server_name:str=None) -> None:
#         pass
#
#     async def _async_remove_gov_action_process_step(self, guid: str, server_name:str=None) -> None:
#         pass
#
#
#     async def _async_find_gov_action_process_step(self, search_string: str, server_name: str = None) -> dict | str:
#         pass
#
#
#     async def _async_get_gov_action_process_step_by_name(self, name: str, server_name: str = None) -> dict | str:
#         pass
#
#
#     async def _async_get_gov_action_process_step_by_guid(self, guid: str, server_name: str = None) -> dict | str:
#         pass
#
#
#     async def _async_setup_first_action_process_step(self, process_guid: str, process_step_guid:str,
#                                                      server_name: str = None) -> dict | str:
#         pass
#
#     async def _async_get_first_action_process_step(self, process_guid: str, server_name: str = None) -> dict | str:
#         pass
#
#     async def _async_remove_first_action_process_step(self, process_guid: str, server_name: str = None) -> None:
#         pass
#
#     async def _async_setup_next_action_process_step(self, process_guid: str, process_step_guid:str,
#                                                      next_process_step_guid:str, server_name: str = None) -> None:
#         pass
#
#
#     async def _async_update_next_action_process_step(self, guid: str, body: dict, server_name: str = None) -> None:
#         pass
#
#
#     async def _async_remove_next_action_process_step(self, guid: str, server_name: str = None) -> None:
#         pass
#
#
#     async def _async_get_next_action_process_step(self, guid: str, server_name: str = None) -> dict | str:
#         pass

    # Engine Actions

    async def _async_initiate_Engine_action(self, gov_eng_name: str, body: dict, server_name: str = None) -> None:
        pass


    async def _async_initiate_gov_action_type(self, body: dict, server_name: str = None) -> None:
        pass
    #implement

    async def _async_initiate_gov_action_processes(self):
        pass





if __name__ == "__main__":
    p = AutomatedCuration("meow", "https://127.0.0.1:9443", "garygeeke", verify_flag=False)
    response = p.get_active_service_list_for_server()
    out = response.json()["result"]
    print(out)
