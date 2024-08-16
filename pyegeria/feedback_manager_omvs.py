"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the feedback_manager_omvs
module.

"""

import asyncio
import json

# import json
from pyegeria._client import Client, max_paging_size
from pyegeria._globals import enable_ssl_check


def jprint(info, comment=None):
    if comment:
        print(comment)
    print(json.dumps(info, indent=2))


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


def base_path(fm_client, view_server: str):
    return f"{fm_client.platform_url}/servers/{view_server}/api/open-metadata/feedback-manager"


def extract_relationships_plus(element):
    type_name = element["relatedElement"]["type"]["typeName"]
    guid = element["relationshipHeader"]["guid"]
    properties = element["relationshipProperties"]["propertiesAsStrings"]
    name = element["relatedElement"]["uniqueName"]
    return {"name": name, "typeName": type_name, "guid": guid, "properties": properties}


def extract_related_elements_list(element_list):
    return [extract_relationships_plus(element) for element in element_list]


def related_elements_response(response: dict, detailed_response: bool):
    if detailed_response:
        return response
    else:
        return extract_related_elements_list(response["elementList"])


def element_properties_plus(element):
    props_plus = element["properties"]
    props_plus.update({"guid": element["elementHeader"]["guid"]})
    props_plus.update({"versions": element["elementHeader"]["versions"]})
    return props_plus


def element_property_plus_list(element_list):
    return [element_properties_plus(element) for element in element_list]


def element_response(response: dict, element_type: str, detailed_response: bool):
    if detailed_response:
        return response
    else:
        return element_properties_plus(response[element_type])


def elements_response(response: dict, element_type: str, detailed_response: bool):
    if type(response) != dict:
        return('---')
    if detailed_response:
        return response
    else:
        return element_property_plus_list(response.get(element_type,'---'))
# Todo - review with Kevin...

class FeedbackManager(Client):
    """FeedbackManager is a class that extends the Client class. It
    provides methods to CRUD tags, comments and likes for managed
    elements.

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
        verify_flag: bool
            Flag to indicate if SSL Certificates should be verified in the HTTP
            requests.
            Defaults to False.

    """

    def __init__(
            self,
            server_name: str,
            platform_url: str,
            token: str = None,
            user_id: str = None,
            user_pwd: str = None,
            verify_flag: bool = enable_ssl_check,
            sync_mode: bool = True,
    ):
        self.admin_command_root: str
        Client.__init__(
            self,
            server_name,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
            async_mode=sync_mode,
        )

    async def _async_add_comment_reply(
            self,
            element_guid: str,
            comment_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a reply to a comment.

        Parameters
        ----------
        elementGUID
            - String - unique id for the anchor element.
        commentGUID
            - String - unique id for an existing comment. Used to add a reply to a comment.
        serverName
            - name of the server instances for this request.
        isPublic
            - is this visible to other people
        requestBody
            - containing type of comment enum and the text of the comment.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        ElementGUID

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/comments/{comment_guid}/replies{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_comment_reply(
            self,
            element_guid: str,
            comment_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a reply to a comment.

        Parameters
        ----------
        elementGUID
            - String - unique id for the anchor element.
        commentGUID
            - String - unique id for an existing comment. Used to add a reply to a comment.
        serverName
            - name of the server instances for this request.
        isPublic
            - is this visible to other people
        requestBody
            - containing type of comment enum and the text of the comment.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        ElementGUID

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
            self._async_add_comment_reply(
                element_guid,
                comment_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_add_comment_reply(server_name, body)
        )
        return response

    #
    ## add_comment_to_element implementation
    #

    async def _async_add_comment_to_element(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - String - unique id for the element.
        isPublic
            - is this visible to other people
        requestBody
            - containing type of comment enum and the text of the comment.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        ElementGUID

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/comments{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_comment_to_element(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - String - unique id for the element.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        ElementGUID

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
            self._async_add_comment_to_element(
                element_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## add_like_to_element implementation
    #

    async def _async_add_like_to_element(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a "like" object and attaches it to an element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - String - unique id for the element.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )

        url = f"{base_path(self, server_name)}/elements/{element_guid}/likes{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_like_to_element(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a "like" object and attaches it to an element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - String - unique id for the element.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        Void

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
            self._async_add_like_to_element(
                element_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## add_rating_to_element implementation
    #

    async def _async_add_rating_to_element(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a star rating and optional review text to the element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - String - unique id for the element.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing the StarRating and user review of element.

        Returns
        -------
        ElementGUID

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/ratings{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_rating_to_element(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a star rating and optional review text to the element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - String - unique id for the element.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing the StarRating and user review of element.

        Returns
        -------
        ElementGUID

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
            self._async_add_rating_to_element(
                element_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## add_tag_to_element implementation
    #

    async def _async_add_tag_to_element(
            self,
            element_guid: str,
            tag_guid: str,
            server_name: str = None,
            is_public: bool = False,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds an informal tag (either private of public) to an element.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - unique id for the element.
        tagGUID
            - unique id of the tag.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/tags/{tag_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_tag_to_element(
            self,
            element_guid: str,
            tag_guid: str,
            server_name: str = None,
            is_public: bool = False,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds an informal tag (either private of public) to an element.

        Parameters
        ----------
        elementGUID
            - unique id for the element.
        tagGUID
            - unique id of the tag.
        serverName
            - name of the server instances for this request.
        isPublic
            - is this visible to other people
        requestBody
            - optional effective time
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Void

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
            self._async_add_tag_to_element(
                element_guid,
                tag_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## clear_accepted_answer implementation
    #

    async def _async_clear_accepted_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Unlink a comment that contains an answer to a question posed in another comment.

        Parameters
        ----------
        serverName
            - name of the server to route the request to
        questionCommentGUID
            - unique identifier of the comment containing the question
        answerCommentGUID
            - unique identifier of the comment containing the accepted answer
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - properties to help with the mapping of the elements in the external asset manager and open metadata

        Returns
        -------
        VoidResponse

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/comments/questions/{question_comment_guid}/answers/{answer_comment_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def clear_accepted_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Unlink a comment that contains an answer to a question posed in another comment.

        Parameters
        ----------
        serverName
            - name of the server to route the request to
        questionCommentGUID
            - unique identifier of the comment containing the question
        answerCommentGUID
            - unique identifier of the comment containing the accepted answer
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - properties to help with the mapping of the elements in the external asset manager and open metadata

        Returns
        -------
        VoidResponse

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
            self._async_clear_accepted_answer(
                question_comment_guid,
                answer_comment_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## create_informal_tag implementation
    #

    async def _async_create_informal_tag(
            self,
            body: dict,
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new informal tag and returns the unique identifier for it.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - public/private flag, name of the tag and (optional) description of the tag.

        Example
        -------
        my_new_tag_body = {
            "isPrivateTag": False,
            "name": "new-tag-from-python",
            "description": "this tag was created using the python API"
        }
        response = fm_client.create_informal_tag(my_new_tag_body)
        print(response)
        {'class': 'GUIDResponse', 'relatedHTTPCode': 200,
         'guid': '27bb889d-f646-45e4-b032-e9cd7b2a614f'}

        Returns
        -------
        new elementGUID

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/tags{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def create_informal_tag(
            self,
            body: dict,
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new informal tag and returns the unique identifier for it.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - public/private flag, name of the tag and (optional) description of the tag.

        Example
        -------
        my_new_tag_body = {
            "isPrivateTag": False,
            "name": "new-tag-from-python",
            "description": "this tag was created using the python API"
        }
        response = fm_client.create_informal_tag(my_new_tag_body)
        print(response)
        {'class': 'GUIDResponse', 'relatedHTTPCode': 200,
         'guid': '27bb889d-f646-45e4-b032-e9cd7b2a614f'}

        Returns
        -------
        new elementGUID

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
            self._async_create_informal_tag(body, server_name)
        )
        return response

    #
    ## create_note implementation
    #

    async def _async_create_note(
            self,
            note_log_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new note for a note log and returns the unique identifier for it.

        Parameters
        ----------
        noteLogGUID
            - unique identifier of the note log
        serverName
            - name of the server instances for this request
        requestBody
            - contains the name of the tag and (optional) description of the tag
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Guid for the note

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )

        url = f"{base_path(self, server_name)}/note-logs/{note_log_guid}/notes{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def create_note(
            self,
            note_log_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new note for a note log and returns the unique identifier for it.

        Parameters
        ----------
        noteLogGUID
            - unique identifier of the note log
        serverName
            - name of the server instances for this request
        requestBody
            - contains the name of the tag and (optional) description of the tag
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Guid for the note

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
            self._async_create_note(
                note_log_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## create_note_log implementation
    #

    async def _async_create_note_log(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new noteLog and returns the unique identifier for it.

        Parameters
        ----------
        elementGUID
            - unique identifier of the element where the note log is located
        serverName
            - name of the server instances for this request
        isPublic
            - is this element visible to other people.
        requestBody
            - contains the name of the tag and (optional) description of the tag
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        ElementGUID

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/note-logs{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def create_note_log(
            self,
            element_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new noteLog and returns the unique identifier for it.

        Parameters
        ----------
        elementGUID
            - unique identifier of the element where the note log is located
        serverName
            - name of the server instances for this request
        isPublic
            - is this element visible to other people.
        requestBody
            - contains the name of the tag and (optional) description of the tag
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        ElementGUID

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
            self._async_create_note_log(
                element_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## delete_tag implementation
    #

    async def _async_delete_tag(
            self,
            tag_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes an informal tag from the repository.

        All the tagging relationships to this informal tag are lost. A
        private tag can be deleted by its creator and all the
        references are lost; a public tag can be deleted by anyone,
        but only if it is not attached to any referenceable.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        tagGUID
            - String - unique id for the tag.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - null request body.

        Returns
        -------
        VOIDResponse

        Example
        -------
        my_new_tag_tag_guid = {
            "isPrivateTag": False,
            "name": "new-tag-from-python",
            "description": "this tag was created using the python API"
        }
        create_response = fm_client.delete_tag(my_new_tag_tag_guid)
        print(create_response)
        {'class': 'GUIDResponse', 'relatedHTTPCode': 200,
         'guid': '27bb889d-f646-45e4-b032-e9cd7b2a614f'}
        delete_response = fm_client.delete_tag("view-server", create_response["guid"])
        print(delete_response)
        {'class': 'VoidResponse', 'relatedHTTPCode': 200}

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/feedback-manager/tags/{tag_guid}/remove{possible_query_params}"

        response = await self._async_make_request("POST", url, {})
        return response.json()

    def delete_tag(
            self,
            tag_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes an informal tag from the repository.

        All the tagging relationships to this informal tag are lost. A
        private tag can be deleted by its creator and all the
        references are lost; a public tag can be deleted by anyone,
        but only if it is not attached to any referenceable.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        tagGUID
            - String - unique id for the tag.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - null request body.

        Returns
        -------
        VOIDResponse

        Example
        -------
        my_new_tag_tag_guid = {
            "isPrivateTag": False,
            "name": "new-tag-from-python",
            "description": "this tag was created using the python API"
        }
        create_response = fm_client.delete_tag(my_new_tag_tag_guid)
        print(create_response)
        {'class': 'GUIDResponse', 'relatedHTTPCode': 200,
         'guid': '27bb889d-f646-45e4-b032-e9cd7b2a614f'}
        delete_response = fm_client.delete_tag("view-server", create_response["guid"])
        print(delete_response)
        {'class': 'VoidResponse', 'relatedHTTPCode': 200}

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
            self._async_delete_tag(
                tag_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## find_my_tags implementation
    #

    async def _async_find_my_tags(
            self,
            body: str,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of the calling user's private tags containing the supplied string in either the name or description. The search string is a regular expression (RegEx).


        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - search string and effective time.

        Returns
        -------
        list of tag objects

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/tags/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "tags", detailed_response)

    def find_my_tags(
            self,
            body: str,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of the calling user's private tags containing the supplied string in either the name or description. The search string is a regular expression (RegEx).


        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - search string and effective time.

        Returns
        -------
        list of tag objects

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
            self._async_find_my_tags(
                body,
                server_name=server_name,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                start_from=start_from,
                page_size=page_size,
                view_service_url_marker=view_service_url_marker,
                access_service_url_marker=access_service_url_marker,
                detailed_response=detailed_response,
            )
        )
        return response

    #
    ## find_note_logs implementation
    #

    async def _async_find_note_logs(
            self,
            body: dict,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements that contain the search string.

        Parameters
        ----------
        requestBody
            - search string and effective time.
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of matching metadata elements

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def find_note_logs(
            self,
            body: dict,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements that contain the search string.

        Parameters
        ----------
        requestBody
            - search string and effective time.
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of matching metadata elements

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
            self._async_find_note_logs(
                body,
                server_name,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## find_notes implementation
    #

    async def _async_find_notes(
            self,
            body: dict,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note metadata elements that contain the search string.

        Parameters
        ----------
        requestBody
            - search string and effective time.
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of matching metadata elements

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/notes/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def find_notes(
            self,
            body: dict,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note metadata elements that contain the search string.

        Parameters
        ----------
        requestBody
            - search string and effective time.
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of matching metadata elements

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
            self._async_find_notes(
                body,
                server_name,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## find_tags implementation
    #

    async def _async_find_tags(
            self,
            body: str,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            detailed_response: bool = False,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Return the list of tags containing the supplied string in the text. The search string is a regular expression (RegEx).

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - search string and effective time.

        Returns
        -------
        list of tag objects

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/tags/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "tags", detailed_response)

    def find_tags(
            self,
            body: str,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of tags containing the supplied string in the text. The search string is a regular expression (RegEx).

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - search string and effective time.

        Returns
        -------
        list of tag objects

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
            self._async_find_tags(
                body,
                server_name=server_name,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                start_from=start_from,
                page_size=page_size,
                view_service_url_marker=view_service_url_marker,
                access_service_url_marker=access_service_url_marker,
                detailed_response=detailed_response,
            )
        )
        return response

    #
    ## find_comments implementation
    #

    async def _async_find_comments(
            self,
            body: str,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of comments containing the supplied string.

        Parameters
        ----------
        body
            - search string and effective time.
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of comment objects

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startsWith", starts_with),
                ("endsWith", ends_with),
                ("ignoreCase", ignore_case),
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/comments/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def find_comments(
            self,
            body: str,
            server_name: str = None,
            starts_with: bool = None,
            ends_with: bool = None,
            ignore_case: bool = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of comments containing the supplied string.

        Parameters
        ----------
        requestBody
            - search string and effective time.
        serverName
            - name of the server instances for this request.
        startsWith
            - does the value start with the supplied string?
        endsWith
            - does the value end with the supplied string?
        ignoreCase
            - should the search ignore case?
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of comment objects

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
            self._async_find_comments(
                body,
                server_name,
                starts_with,
                ends_with,
                ignore_case,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_attached_comments implementation
    #

    async def _async_get_attached_comments(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the comments attached to an element.

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the comments are connected to (maybe a comment too).
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of comments

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/comments/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_attached_comments(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the comments attached to an element.

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the comments are connected to (maybe a comment too).
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of comments

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
            self._async_get_attached_comments(
                element_guid,
                server_name,
                body,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_comment implementation
    #

    async def _async_get_comment(
            self,
            comment_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        commentGUID
            - unique identifier for the comment object.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        comment properties

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/comments/{comment_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return element_response(response.json(), "element", detailed_response)

    def get_comment(
            self,
            comment_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        commentGUID
            - unique identifier for the comment object.
        serverName
            - name of the server instances for this request
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        comment properties

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
            self._async_get_comment(
                comment_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_attached_likes implementation
    #
    async def _async_get_attached_likes(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the likes attached to an element

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the likes are connected to
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call


        Returns
        -------
        List of Likes (LikeElementsResponse)

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/likes/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        # return elements_response(response.json(), "elementList", detailed_response)
        return response.json().get('ratings','---')

    def get_attached_likes(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the likes attached to an element


        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the likes are connected to
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call


        Returns
        -------
        List of Likes (LikeElementsResponse)

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
            self._async_get_attached_likes(
                element_guid,
                server_name,
                body,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_attached_ratings implementation
    #
    async def _async_get_attached_ratings(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the ratings attached to an element.

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the ratings are connected to
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        List of ratings (RatingElementsResponse)

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/ratings/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_attached_ratings(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the ratings attached to an element.

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the ratings are connected to
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        List of ratings (RatingElementsResponse)

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
            self._async_get_attached_ratings(
                element_guid,
                server_name,
                body,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_attached_tags implementation
    #
    async def _async_get_attached_tags(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the informal tags attached to an element.

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the ratings are connected to
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        List of InformalTags (InformalTagsResponse)

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/tags/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json().get('tags', '---')
        # return elements_response(response.json(), "tags", detailed_response)

    def get_attached_tags(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the informal tags attached to an element.

        Parameters
        ----------
        elementGUID
            - unique identifier for the element that the ratings are connected to
        serverName
            - name of the server instances for this request
        body
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        List of InformalTags (InformalTagsResponse)

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
            self._async_get_attached_tags(
                element_guid,
                server_name,
                body,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_elements_by_tag implementation
    #

    async def _async_get_elements_by_tag(
            self,
            tag_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of unique identifiers for elements that are linked to a specific tag either directly, or via one of its schema elements.

        Parameters
        ----------
        tagGUID
            - unique identifier of tag.
        serverName
            - name of the server instances for this request
        requestBody
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        element stubs list

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/by-tag/{tag_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return related_elements_response(response.json(), detailed_response)

    def get_elements_by_tag(
            self,
            tag_guid: str,
            server_name: str = None,
            body: dict = {},
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the list of unique identifiers for elements that are linked to a specific tag either directly, or via one of its schema elements.

        Parameters
        ----------
        tagGUID
            - unique identifier of tag.
        serverName
            - name of the server instances for this request
        requestBody
            - optional effective time
        startFrom
            - index of the list to start from (0 for start)
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        element stubs list

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
            self._async_get_elements_by_tag(
                tag_guid,
                server_name,
                body,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_note_by_guid implementation
    #

    async def _async_get_note_by_guid(
            self,
            note_guid: str,
            server_name: str = None,
            body: str = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note metadata element with the supplied unique identifier.

        Parameters
        ----------
        noteGUID
             - unique identifier of the requested metadata element
        serverName
             - name of the server instances for this request
        viewServiceURLMarker
             - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
             - optional access service URL marker used to identify which back end service to call

         Returns
         -------
         matching metadata element

         Raises
         ------
         InvalidParameterException
             one of the parameters is null or invalid or
         PropertyServerException
             There is a problem adding the element properties to the metadata repository or
         UserNotAuthorizedException
             the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/notes/{note_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return element_response(response.json(), "element", detailed_response)

    def get_note_by_guid(
            self,
            note_guid: str,
            server_name: str = None,
            body: str = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note metadata element with the supplied unique identifier.

        Parameters
        ----------
        noteGUID
             - unique identifier of the requested metadata element
        serverName
             - name of the server instances for this request
        viewServiceURLMarker
             - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
             - optional access service URL marker used to identify which back end service to call

         Returns
         -------
         matching metadata element

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
            self._async_get_note_by_guid(
                note_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_note_log_by_guid implementation
    #

    async def _async_get_note_log_by_guid(
            self,
            note_log_guid: str,
            server_name: str = None,
            body: str = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note log metadata element with the supplied unique identifier.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        noteLogGUID
            - unique identifier of the requested metadata element
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        Note details

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/{note_log_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return element_response(response.json(), "element", detailed_response)

    def get_note_log_by_guid(
            self,
            note_log_guid: str,
            server_name: str = None,
            body: str = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note log metadata element with the supplied unique identifier.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        noteLogGUID
            - unique identifier of the requested metadata element
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        Note details

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
            self._async_get_note_log_by_guid(
                note_log_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_note_logs_by_name implementation
    #

    async def _async_get_note_logs_by_name(
            self,
            body: dict,
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements with a matching qualified or display name.

        There are no wildcards supported on this request.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        startFrom
            - paging start point
        pageSize
            - maximum results that can be returned
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - name to search for and correlators

        Returns
        -------
        list of matching note logs

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/by-name{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_note_logs_by_name(
            self,
            body: dict,
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements with a matching qualified or display name.

        There are no wildcards supported on this request.

        Parameters
        ----------
        body
            - name to search for and correlators
        serverName
            - name of the server instances for this request
        startFrom
            - paging start point
        pageSize
            - maximum results that can be returned
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of matching note logs

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
            self._async_get_note_logs_by_name(
                body,
                server_name,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_note_logs_for_element implementation
    #

    async def _async_get_note_logs_for_element(
            self,
            element_guid: str,
            body: dict = {},
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements attached to the element.

        Parameters
        ----------
        elementGUID
            - element to start from
        body
            - optional effective time
        serverName
            - name of the server instances for this request
        startFrom
            - paging start point
        pageSize
            - maximum results that can be returned
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of note logs

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/note-logs/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_note_logs_for_element(
            self,
            element_guid: str,
            body: dict = {},
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of note log metadata elements attached to the element.

        Parameters
        ----------
        elementGUID
            - element to start from
        body
            - optional effective time
        serverName
            - name of the server instances for this request
        startFrom
            - paging start point
        pageSize
            - maximum results that can be returned
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of note logs

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
            self._async_get_note_logs_for_element(
                element_guid,
                body,
                server_name,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_notes_for_note_log implementation
    #

    async def _async_get_notes_for_note_log(
            self,
            note_log_guid: str,
            body: dict = {},
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of notes associated with a note log.

        Parameters
        ----------
        noteLogGUID
            - unique identifier of the note log of interest
        body
            - optional effective time
        serverName
            - name of the server instances for this request
        startFrom
            - paging start point
        pageSize
            - maximum results that can be returned
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of notes

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/{note_log_guid}/notes/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_notes_for_note_log(
            self,
            note_log_guid: str,
            body: dict = {},
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the list of notes associated with a note log.

        Parameters
        ----------
        noteLogGUID
            - unique identifier of the note log of interest
        body
            - optional effective time
        serverName
            - name of the server instances for this request
        startFrom
            - paging start point
        pageSize
            - maximum results that can be returned
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of notes

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
            self._async_get_notes_for_note_log(
                note_log_guid,
                body,
                server_name,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_tag implementation
    #

    async def _async_get_tag(
            self,
            tag_guid: str,
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the informal tag for the supplied unique identifier (tagGUID).

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        tagGUID
            - unique identifier of the meaning.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        list of tag objects

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """

        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/tags/{tag_guid}/retrieve{possible_query_params}"

        response = await self._async_make_request("POST", url, {})
        return element_response(response.json(), "tag", detailed_response)

    def get_tag(
            self,
            tag_guid: str,
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the informal tag for the supplied unique identifier (tagGUID).

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        tagGUID
            - unique identifier of the meaning.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - optional effective time

        Returns
        -------
        tag object

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
            self._async_get_tag(
                tag_guid,
                server_name,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## get_tags_by_name implementation
    #

    async def _async_get_tags_by_name(
            self,
            body: str,
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the tags exactly matching the supplied name.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        requestBody
            - name of tag.
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of tag objects

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/tags/by-name{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "tags", detailed_response)

    def get_tags_by_name(
            self,
            body: str,
            server_name: str = None,
            start_from: int = 0,
            page_size: int = max_paging_size,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
            detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the tags exactly matching the supplied name.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        requestBody
            - name of tag.
        startFrom
            - index of the list to start from (0 for start).
        pageSize
            - maximum number of elements to return.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        list of tag objects

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
            self._async_get_tags_by_name(
                body,
                server_name,
                start_from,
                page_size,
                view_service_url_marker,
                access_service_url_marker,
                detailed_response,
            )
        )
        return response

    #
    ## remove_comment_from_element implementation
    #

    async def _async_remove_comment_from_element(
            self,
            comment_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a comment added to the element by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        commentGUID
            - String - unique id for the comment object
        serverName
            - name of the server instances for this request
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        VoidResponse

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/comments/{comment_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_comment_from_element(
            self,
            comment_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a comment added to the element by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        commentGUID
            - String - unique id for the comment object
        serverName
            - name of the server instances for this request
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        VoidResponse

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
            self._async_remove_comment_from_element(
                comment_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## remove_like_from_element implementation
    #

    async def _async_remove_like_from_element(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a "Like" added to the element by this user.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - unique identifier for the element where the like is attached.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        VoidResponse

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/likes/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_like_from_element(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a "Like" added to the element by this user.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - unique identifier for the element where the like is attached.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        VoidResponse

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
            self._async_remove_like_from_element(
                element_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## remove_note implementation
    #

    async def _async_remove_note(
            self,
            note_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        noteGUID
            - unique id for the note .
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - null request body.


        Returns
        -------
        VoidResponse

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/notes/{note_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_note(
            self,
            note_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        noteGUID
            - unique id for the note .
        serverName
            - name of the server instances for this request
        requestBody
            - null request body.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call


        Returns
        -------
        VoidResponse

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
            self._async_remove_note(
                note_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## remove_note_log implementation
    #

    async def _async_remove_note_log(
            self,
            note_log_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note log from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        noteLogGUID
            - unique id for the note log.
        serverName
            - name of the server instances for this request
        requestBody
            - null request body.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        VoidResponse

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/{note_log_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_note_log(
            self,
            note_log_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note log from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        noteLogGUID
            - unique id for the note log.
        serverName
            - name of the server instances for this request
        requestBody
            - null request body.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        VoidResponse

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
            self._async_remove_note_log(
                note_log_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## remove_rating_from_element implementation
    #

    async def _async_remove_rating_from_element(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes of a star rating/review that was added to the element by this user.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - unique identifier for the element where the rating is attached.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/ratings/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_rating_from_element(
            self,
            element_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes of a star rating/review that was added to the element by this user.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - unique identifier for the element where the rating is attached.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        Void

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
            self._async_remove_rating_from_element(
                element_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## remove_tag_from_element implementation
    #

    async def _async_remove_tag_from_element(
            self,
            element_guid: str,
            tag_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a link between a tag and an element that was added by this user.


        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        elementGUID
            - unique id for the element.
        tagGUID
            - unique id of the tag.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - null request body needed for correct protocol exchange.

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/elements/{element_guid}/tags/{tag_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_tag_from_element(
            self,
            element_guid: str,
            tag_guid: str,
            server_name: str = None,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a link between a tag and an element that was added by this user.


        Parameters
        ----------
        elementGUID
            - unique id for the element.
        tagGUID
            - unique id of the tag.
        serverName
            - name of the server instances for this request.
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - null request body needed for correct protocol exchange.

        Returns
        -------
        Void

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
            self._async_remove_tag_from_element(
                element_guid,
                tag_guid,
                server_name,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## setup_accepted_answer implementation
    #

    async def _async_setup_accepted_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Link a comment that contains the best answer to a question posed in another comment.

        Parameters
        ----------
        serverName
            - name of the server to route the request to
        questionCommentGUID
            - unique identifier of the comment containing the question
        answerCommentGUID
            - unique identifier of the comment containing the accepted answer
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - properties to help with the mapping of the elements in the external asset manager and open metadata

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/comments/questions/{question_comment_guid}/answers/{answer_comment_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def setup_accepted_answer(
            self,
            question_comment_guid: str,
            answer_comment_guid: str,
            server_name: str = None,
            is_public: bool = True,
            body: dict = {},
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Link a comment that contains the best answer to a question posed in another comment.

        Parameters
        ----------
        serverName
            - name of the server to route the request to
        questionCommentGUID
            - unique identifier of the comment containing the question
        answerCommentGUID
            - unique identifier of the comment containing the accepted answer
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - properties to help with the mapping of the elements in the external asset manager and open metadata

        Returns
        -------
        Void

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
            self._async_setup_accepted_answer(
                question_comment_guid,
                answer_comment_guid,
                server_name,
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## update_comment implementation
    #

    async def _async_update_comment(
            self,
            comment_guid: str,
            body: dict,
            server_name: str = None,
            is_merge_update: bool = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment.

        Parameters
        ----------
        commentGUID
            - unique identifier for the comment to change.
        body
            - containing type of comment enum and the text of the comment.
        serverName
            - name of the server instances for this request.
        isMergeUpdate
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isMergeUpdate", is_merge_update),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/comments/{comment_guid}/update{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_comment(
            self,
            comment_guid: str,
            body: dict,
            server_name: str = None,
            is_merge_update: bool = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment.

        Parameters
        ----------
        commentGUID
            - unique identifier for the comment to change.
        body
            - containing type of comment enum and the text of the comment.
        serverName
            - name of the server instances for this request.
        isMergeUpdate
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Void

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
            self._async_update_comment(
                comment_guid,
                body,
                server_name,
                is_merge_update,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## update_comment_visibility implementation
    #

    async def _async_update_comment_visibility(
            self,
            parent_guid: str,
            comment_guid: str,
            is_public: bool,
            body: dict = {},
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment's visibility.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        commentGUID
            - unique identifier for the comment to change.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/parents/{parent_guid}/comments/{comment_guid}/update-visibility{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_comment_visibility(
            self,
            parent_guid: str,
            comment_guid: str,
            is_public: bool,
            body: dict = {},
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment's visibility.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        commentGUID
            - unique identifier for the comment to change.
        isPublic
            - is this visible to other people
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        Void

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
            self._async_update_comment_visibility(
                parent_guid,
                comment_guid,
                is_public,
                body,
                server_name,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## update_note implementation
    #

    async def _async_update_note(
            self,
            note_guid: str,
            body: dict,
            server_name: str = None,
            is_merge_update: bool = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        noteGUID
            - unique identifier for the note to change.
        isMergeUpdate
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isMergeUpdate", is_merge_update),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/notes/{note_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_note(
            self,
            note_guid: str,
            body: dict,
            server_name: str = None,
            is_merge_update: bool = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note.

        Parameters
        ----------
        serverName
            - name of the server instances for this request.
        noteGUID
            - unique identifier for the note to change.
        isMergeUpdate
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody
            - containing type of comment enum and the text of the comment.

        Returns
        -------
        Void

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
            self._async_update_note(
                note_guid,
                body,
                server_name,
                is_merge_update,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## update_note_log implementation
    #

    async def _async_update_note_log(
            self,
            note_log_guid: str,
            body: dict,
            server_name: str = None,
            is_merge_update: bool = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note log.

        Parameters
        ----------
        noteLogGUID
            - unique identifier for the note log to change.
        body
            - containing type of comment enum and the text of the comment.
        serverName
            - name of the server instances for this request.
        isMergeUpdate
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Void

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("isMergeUpdate", is_merge_update),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/note-logs/{note_log_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_note_log(
            self,
            note_log_guid: str,
            body: dict,
            server_name: str = None,
            is_merge_update: bool = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note log.

        Parameters
        ----------
        noteLogGUID
            - unique identifier for the note log to change.
        body
            - containing type of comment enum and the text of the comment.
        serverName
            - name of the server instances for this request.
        isMergeUpdate
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call

        Returns
        -------
        Void

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
            self._async_update_note_log(
                note_log_guid,
                body,
                server_name,
                is_merge_update,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## update_tag_description implementation
    #

    async def _async_update_tag_description(
            self,
            tag_guid: str,
            body: str,
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Updates the description of an existing tag (either private or public).

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        tagGUID
            - unique id for the tag
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody - contains the name of the tag and (optional) description of the tag.

        Returns
        -------
        VoidResponse :
        {'class': 'VoidResponse', 'relatedHTTPCode': 200}

        Raises
        ------
        InvalidParameterException
            one of the parameters is null or invalid or
        PropertyServerException
            There is a problem adding the element properties to the metadata repository or
        UserNotAuthorizedException
            the requesting user is not authorized to issue this request.
        """
        if server_name is None:
            server_name = self.server_name

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, server_name)}/tags/{tag_guid}/update{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_tag_description(
            self,
            tag_guid: str,
            body: str,
            server_name: str = None,
            view_service_url_marker: str = None,
            access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Updates the description of an existing tag (either private or public).

        Parameters
        ----------
        serverName
            - name of the server instances for this request
        tagGUID
            - unique id for the tag
        viewServiceURLMarker
            - optional view service URL marker (overrides accessServiceURLMarker)
        accessServiceURLMarker
            - optional access service URL marker used to identify which back end service to call
        requestBody - contains the name of the tag and (optional) description of the tag.

        Returns
        -------
        VoidResponse :
        {'class': 'VoidResponse', 'relatedHTTPCode': 200}

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
            self._async_update_tag_description(
                tag_guid,
                body,
                server_name,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response
