"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.



This module allows users to query the available (registered) capabilities of Egeria. Detailed information is returned
to provide both insight and understanding in how to use these capabilities. For example, when configuring an Egeria
integration service, it is importregistered_info.pyant to know what companion service it depends on so that you can make sure the
companion service is also configured and running.

"""

from pyegeria import (
    Client, max_paging_size, InvalidParameterException, PropertyServerException, UserNotAuthorizedException,
    print_exception_response
)



class LoadedResources(Client):
    """ Client to search and retrieve currently loaded information about connectors, templates, governance actions,
        etc.

    Attributes:
    ----------
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
    -------

    """

    admin_command_root: str

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
    ):
        if server_name is None:
            server_name = "NA"
        Client.__init__(self, server_name, platform_url,
                        user_id, user_pwd, verify_flag)

    def get_all_templates(self, server: str = None, start_from: int = 0, page_size: int = max_paging_size) -> list | str:
        """ Get Loaded templates for the Server.

           Parameters
           ----------

           Returns
           -------
           dict | str
              A dictionary containing a simplified list of key template attributes.

           Raises
           ------
           InvalidParameterException
               If the response code is not 200.
           PropertyServerException:
               Raised by the server when an issue arises in processing a valid request
           NotAuthorizedException:
               The principle specified by the user_id does not have authorization for the requested action

           """
        server = self.server_name if server is None else server
        url = (f"{self.platform_url}/servers/{server}/open-metadata/framework-services/asset-owner/open-metadata-store/"
               f"users/{self.user_id}/metadata-elements/by-search-string?startFrom=start_from&pageSize=page_size")
        body = {
                  "class" : "SearchStringRequestBody",
                  "searchString" : ".*Template.*"
                }
        response = self.make_request("POST", url, body)
        return response.json().get("elementList", "No elements")

    # def get_all_assets_in_archives(self, asset_type: str = None, archive_id: str = None, server: str= None, page_start:int = 0, page_size = max_paging_size):

