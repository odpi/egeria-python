"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

 Feedback Manager View Service Methods - Add comments, reviews, tags and notes to elements of interest.

 This work is being actively developed..

"""
import asyncio
from datetime import datetime

from httpx import Response

from pyegeria import Client, max_paging_size, body_slimmer
from pyegeria._exceptions import (
    InvalidParameterException,
)
from ._validators import validate_name, validate_guid, validate_search_string


class FeedbackManager(Client):
    """ Set up and maintain automation services in Egeria.

    Attributes:
        server_name : str
            The name of the View Server to use.
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

    """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            user_id: str,
            user_pwd: str = None,
            verify_flag: bool = False,
    ):
        Client.__init__(self, server_name, platform_url, user_id, user_pwd, verify_flag)
        self.cur_command_root = f"{platform_url}/servers/"


    async def _async_get_comment_by_guid(self, comment_guid: str, view_server: str, server: str = None,
                                         access_service: str = 'asset-manager',for_lineage: bool = False,
                                         for_duplicate_processing: bool = False, effective_time: str = None) -> dict:
        """ Create a new metadata element from a template.  Async version.
             Parameters
             ----------
             body : str
                 The json body used to instantiate the template.
             server : str, optional
                The name of the view server to use. If not provided, the default server name will be used.

             Returns
             -------
             Response
                The guid of the resulting element

             Raises
             ------
             InvalidParameterException
             PropertyServerException
             UserNotAuthorizedException

             Notes
             -----

                """

        server = self.server_name if server is None else server

        url = f"{self.platform_url}/servers/{server}/api/open-metadata/automated-curation/catalog-templates/new-element"
        response = await self._async_make_request("POST", url)
        return response.json().get("guid", "GUID failed to be returned")

    def get_comment_by_guid(self, comment_guid: str, view_server: str, server: str = None,
                                         access_service: str = 'asset-manager',for_lineage: bool = False,
                                         for_duplicate_processing: bool = False, effective_time: str = None) -> dict:
        """ Create a new metadata element from a template.  Async version.
           Parameters
           ----------
           body : str
                The json body used to instantiate the template.
           server : str, optional
               The name of the view server to use. If not provided, the default server name will be used.

           Returns
           -------
           Response
               The guid of the resulting element

            Raises
            ------
            InvalidParameterException
            PropertyServerException
            UserNotAuthorizedException

            Notes
            -----
            See also: https://egeria-project.org/features/templated-cataloguing/overview/
            The full description of the body is shown below:
                {
                  "typeName" : "",
                  "initialStatus" : "",
                  "initialClassifications" : "",
                  "anchorGUID" : "",
                  "isOwnAnchor" : "",
                  "effectiveFrom" : "",
                  "effectiveTo" : "",
                  "templateGUID" : "",
                  "templateProperties" : {},
                  "placeholderPropertyValues" : {
                    "placeholderPropertyName1" : "placeholderPropertyValue1",
                    "placeholderPropertyName2" : "placeholderPropertyValue2"
                  },
                  "parentGUID" : "",
                  "parentRelationshipTypeName" : "",
                  "parentRelationshipProperties" : "",
                  "parentAtEnd1" : "",
                  "effectiveTime" : ""
                }
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_get_comment_by_guid(comment_guid, view_server,server,access_service,
                                            for_lineage,for_duplicate_processing,effective_time)
        )
        return response

    async def _async_add_comment_to_reply(self, comment_guid: str, view_server: str, comment: str, server: str = None,
                                          access_service: str = 'asset-manager', is_public: bool = False,
                                          for_lineage: bool = False, for_duplicate_processing: bool = False,
                                          effective_time: str = None) -> str:
        """ Add a reply to a comment.  Async version.
            See also: https://egeria-project.org/patterns/metadata-manager/overview/#asset-feedback

        Parameters
        ----------
        comment_guid : str
            The GUID of the comment.
        view_server : str
            The server where the view is hosted.
        comment : str
            The text to add as the reply.
        server : str, optional
            The server to connect to. Default is None.
        access_service : str, optional
            The access service to use. Default is 'asset-manager'.
        is_public : bool, optional
            Determines if the comment is public. Default is False.
        for_lineage : bool, optional
            Determines if the comment is for lineage. Default is False.
        for_duplicate_processing : bool, optional
            Determines if the comment is for duplicate processing. Default is False.
        effective_time : str, optional
            The effective time for the comment. Default is None.

        Returns
        -------
        str
            The unique identifier (guid) of the new comment.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """

        url = f"{self.cur_command_root}api/open-metadata/feedback-manager/comments/{comment_guid}/replies"
        body = {
            'parentGUID': comment_guid,
            'effectiveTime': effective_time,
            'updateDescription': comment
            }

        response = await self._async_make_request("POST",url,body)
        return response

    def add_comment_to_reply(self, comment_guid: str, view_server: str, comment: str, server: str = None,
                                          access_service: str = 'asset-manager', is_public: bool = False,
                                          for_lineage: bool = False, for_duplicate_processing: bool = False,
                                          effective_time: str = None) -> str:
        """ Add a reply to a comment.  Async version.
            See also: https://egeria-project.org/patterns/metadata-manager/overview/#asset-feedback

        Parameters
        ----------
        comment_guid : str
            The GUID of the comment.
        view_server : str
            The server where the view is hosted.
        comment : str
            The text to add as the reply.
        server : str, optional
            The server to connect to. Default is None.
        access_service : str, optional
            The access service to use. Default is 'asset-manager'.
        is_public : bool, optional
            Determines if the comment is public. Default is False.
        for_lineage : bool, optional
            Determines if the comment is for lineage. Default is False.
        for_duplicate_processing : bool, optional
            Determines if the comment is for duplicate processing. Default is False.
        effective_time : str, optional
            The effective time for the comment. Default is None.

        Returns
        -------
        str
            The unique identifier (guid) of the new comment.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_comment_to_reply(comment_guid, view_server, comment,
                                             server, access_service, is_public,)
        )
        return response


