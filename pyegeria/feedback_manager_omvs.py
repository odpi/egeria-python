"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the feedback_manager_omvs
module.

"""

import asyncio
import json

# import json
from pyegeria._client import Client, max_paging_size


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
    elif not "elementList" in response:
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
    elif not element_type in response:
        return response
    else:
        return element_properties_plus(response[element_type])


def elements_response(response: dict, element_type: str, detailed_response: bool):
    # print(response)
    if detailed_response:
        return response
    elif not element_type in response:
        return response
    else:
        return element_property_plus_list(response[element_type])


class FeedbackManager(Client):
    """FeedbackManager is a class that extends the Client class. It
    provides methods to CRUD tags, comments and likes for managed
    elements.

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

         token: str, optional
            bearer token

    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
    ):
        self.admin_command_root: str
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        Client.__init__(
            self,
            view_server,
            platform_url,
            user_id,
            user_pwd,
            token=token,
        )

    async def _async_add_comment_reply(
        self,
        element_guid: str,
        comment_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a reply to a comment.

        Parameters
        ----------
        element_guid
            - String - unique id for the anchor element.
        comment_guid
            - String - unique id for an existing comment. Used to add a reply to a comment.

        is_public
            - is this visible to other people
        body
            - containing type of comment enum and the text of the comment.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/comments/{comment_guid}/replies{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_comment_reply(
        self,
        element_guid: str,
        comment_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a reply to a comment.

        Parameters
        ----------
        element_guid
            - String - unique id for the anchor element.
        comment_guid
            - String - unique id for an existing comment. Used to add a reply to a comment.

        is_public
            - is this visible to other people
        body
            - containing type of comment enum and the text of the comment.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
                is_public,
                body,
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response

    #
    ## add_comment_to_element implementation
    #

    async def _async_add_comment_to_element(
        self,
        element_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        is_public
            - is this visible to other people
        body
            - containing type of comment enum and the text of the comment.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/comments{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_comment_to_element(
        self,
        element_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a comment and attaches it to an element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a "like" object and attaches it to an element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )

        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/likes{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_like_to_element(
        self,
        element_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a "like" object and attaches it to an element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a star rating and optional review text to the element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/ratings{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_rating_to_element(
        self,
        element_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds a star rating and optional review text to the element.

        Parameters
        ----------

        element_guid
            - String - unique id for the element.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_public: bool = False,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds an informal tag (either private of public) to an element.

        Parameters
        ----------

        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/tags/{tag_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def add_tag_to_element(
        self,
        element_guid: str,
        tag_guid: str,
        is_public: bool = False,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Adds an informal tag (either private of public) to an element.

        Parameters
        ----------
        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.

        is_public
            - is this visible to other people
        body
            - optional effective time
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Unlink a comment that contains an answer to a question posed in another comment.

        Parameters
        ----------
        server_name
            - name of the server to route the request to
        question_comment_guid
            - unique identifier of the comment containing the question
        answer_comment_guid
            - unique identifier of the comment containing the accepted answer
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/comments/questions/{question_comment_guid}/answers/{answer_comment_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def clear_accepted_answer(
        self,
        question_comment_guid: str,
        answer_comment_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Unlink a comment that contains an answer to a question posed in another comment.

        Parameters
        ----------
        server_name
            - name of the server to route the request to
        question_comment_guid
            - unique identifier of the comment containing the question
        answer_comment_guid
            - unique identifier of the comment containing the accepted answer
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new informal tag and returns the unique identifier for it.

        Parameters
        ----------

        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        new element_guid

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
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/tags{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def create_informal_tag(
        self,
        body: dict,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new informal tag and returns the unique identifier for it.

        Parameters
        ----------

        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        new element_guid

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
            self._async_create_informal_tag(body, self.view_server)
        )
        return response

    #
    ## create_note implementation
    #

    async def _async_create_note(
        self,
        note_log_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new note for a note log and returns the unique identifier for it.

        Parameters
        ----------
        note_log_guid
            - unique identifier of the note log
        server_name
            - name of the server instances for this request
        body
            - contains the name of the tag and (optional) description of the tag
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )

        url = f"{base_path(self, self.view_server)}/note-logs/{note_log_guid}/notes{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def create_note(
        self,
        note_log_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new note for a note log and returns the unique identifier for it.

        Parameters
        ----------
        note_log_guid
            - unique identifier of the note log
        server_name
            - name of the server instances for this request
        body
            - contains the name of the tag and (optional) description of the tag
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new noteLog and returns the unique identifier for it.

        Parameters
        ----------
        element_guid
            - unique identifier of the element where the note log is located
        server_name
            - name of the server instances for this request
        is_public
            - is this element visible to other people.
        body
            - contains the name of the tag and (optional) description of the tag
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/note-logs{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def create_note_log(
        self,
        element_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Creates a new noteLog and returns the unique identifier for it.

        Parameters
        ----------
        element_guid
            - unique identifier of the element where the note log is located
        server_name
            - name of the server instances for this request
        is_public
            - is this element visible to other people.
        body
            - contains the name of the tag and (optional) description of the tag
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        server_name
            - name of the server instances for this request
        tag_guid
            - String - unique id for the tag.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/feedback-manager/tags/{tag_guid}/remove{possible_query_params}"

        response = await self._async_make_request("POST", url, {})
        return response.json()

    def delete_tag(
        self,
        tag_guid: str,
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
        server_name
            - name of the server instances for this request
        tag_guid
            - String - unique id for the tag.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        url = f"{base_path(self, self.view_server)}/tags/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "tags", detailed_response)

    def find_my_tags(
        self,
        body: str,
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

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        body
            - search string and effective time.

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        url = f"{base_path(self, self.view_server)}/note-logs/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def find_note_logs(
        self,
        body: dict,
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
        body
            - search string and effective time.

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body
            - search string and effective time.

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        url = f"{base_path(self, self.view_server)}/note-logs/notes/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def find_notes(
        self,
        body: dict,
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
        body
            - search string and effective time.

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        url = f"{base_path(self, self.view_server)}/tags/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "tags", detailed_response)

    def find_tags(
        self,
        body: str,
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

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        url = f"{base_path(self, self.view_server)}/comments/by-search-string{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def find_comments(
        self,
        body: str,
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

        starts_with
            - does the value start with the supplied string?
        ends_with
            - does the value end with the supplied string?
        ignore_case
            - should the search ignore case?
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        element_guid
            - unique identifier for the element that the comments are connected to (maybe a comment too).
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/comments/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_attached_comments(
        self,
        element_guid: str,
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
        element_guid
            - unique identifier for the element that the comments are connected to (maybe a comment too).
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        comment_guid
            - unique identifier for the comment object.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/comments/{comment_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return element_response(response.json(), "element", detailed_response)

    def get_comment(
        self,
        comment_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the requested comment.

        Parameters
        ----------
        comment_guid
            - unique identifier for the comment object.
        server_name
            - name of the server instances for this request
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        element_guid
            - unique identifier for the element that the likes are connected to
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/likes/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)
        # return response.json().get("ratings", "---")

    def get_attached_likes(
        self,
        element_guid: str,
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
        element_guid
            - unique identifier for the element that the likes are connected to
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        element_guid
            - unique identifier for the element that the ratings are connected to
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/ratings/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_attached_ratings(
        self,
        element_guid: str,
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
        element_guid
            - unique identifier for the element that the ratings are connected to
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        element_guid
            - unique identifier for the element that the ratings are connected to
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/tags/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        # return response.json().get("tags", "---")
        return elements_response(response.json(), "tags", detailed_response)

    def get_attached_tags(
        self,
        element_guid: str,
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
        element_guid
            - unique identifier for the element that the ratings are connected to
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        tag_guid
            - unique identifier of tag.
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/by-tag/{tag_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return related_elements_response(response.json(), detailed_response)

    def get_elements_by_tag(
        self,
        tag_guid: str,
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
        tag_guid
            - unique identifier of tag.
        server_name
            - name of the server instances for this request
        body
            - optional effective time
        start_from
            - index of the list to start from (0 for start)
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: str = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note metadata element with the supplied unique identifier.

        Parameters
        ----------
        note_guid
             - unique identifier of the requested metadata element
        server_name
             - name of the server instances for this request
        view_service_url_marker
             - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/note-logs/notes/{note_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return element_response(response.json(), "element", detailed_response)

    def get_note_by_guid(
        self,
        note_guid: str,
        body: str = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note metadata element with the supplied unique identifier.

        Parameters
        ----------
        note_guid
             - unique identifier of the requested metadata element
        server_name
             - name of the server instances for this request
        view_service_url_marker
             - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: str = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note log metadata element with the supplied unique identifier.

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        note_log_guid
            - unique identifier of the requested metadata element
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/note-logs/{note_log_guid}/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return element_response(response.json(), "element", detailed_response)

    def get_note_log_by_guid(
        self,
        note_log_guid: str,
        body: str = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Retrieve the note log metadata element with the supplied unique identifier.

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        note_log_guid
            - unique identifier of the requested metadata element
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        server_name
            - name of the server instances for this request
        start_from
            - paging start point
        page_size
            - maximum results that can be returned
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/note-logs/by-name{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_note_logs_by_name(
        self,
        body: dict,
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
        server_name
            - name of the server instances for this request
        start_from
            - paging start point
        page_size
            - maximum results that can be returned
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        element_guid
            - element to start from
        body
            - optional effective time
        server_name
            - name of the server instances for this request
        start_from
            - paging start point
        page_size
            - maximum results that can be returned
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/note-logs/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_note_logs_for_element(
        self,
        element_guid: str,
        body: dict = {},
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
        element_guid
            - element to start from
        body
            - optional effective time
        server_name
            - name of the server instances for this request
        start_from
            - paging start point
        page_size
            - maximum results that can be returned
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        note_log_guid
            - unique identifier of the note log of interest
        body
            - optional effective time
        server_name
            - name of the server instances for this request
        start_from
            - paging start point
        page_size
            - maximum results that can be returned
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/note-logs/{note_log_guid}/notes/retrieve{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "elementList", detailed_response)

    def get_notes_for_note_log(
        self,
        note_log_guid: str,
        body: dict = {},
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
        note_log_guid
            - unique identifier of the note log of interest
        body
            - optional effective time
        server_name
            - name of the server instances for this request
        start_from
            - paging start point
        page_size
            - maximum results that can be returned
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the informal tag for the supplied unique identifier (tag_guid).

        Parameters
        ----------

        tag_guid
            - unique identifier of the meaning.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/tags/{tag_guid}/retrieve{possible_query_params}"

        response = await self._async_make_request("POST", url, {})
        return element_response(response.json(), "tag", detailed_response)

    def get_tag(
        self,
        tag_guid: str,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
        detailed_response: bool = False,
    ) -> dict | str:
        """
        Return the informal tag for the supplied unique identifier (tag_guid).

        Parameters
        ----------

        tag_guid
            - unique identifier of the meaning.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        body
            - name of tag.
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("startFrom", start_from),
                ("pageSize", page_size),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/tags/by-name{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return elements_response(response.json(), "tags", detailed_response)

    def get_tags_by_name(
        self,
        body: str,
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

        body
            - name of tag.
        start_from
            - index of the list to start from (0 for start).
        page_size
            - maximum number of elements to return.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a comment added to the element by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        comment_guid
            - String - unique id for the comment object
        server_name
            - name of the server instances for this request
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/comments/{comment_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_comment_from_element(
        self,
        comment_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a comment added to the element by this user.

        This deletes the link to the comment, the comment itself and any comment replies attached to it.

        Parameters
        ----------
        comment_guid
            - String - unique id for the comment object
        server_name
            - name of the server instances for this request
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a "Like" added to the element by this user.

        Parameters
        ----------

        element_guid
            - unique identifier for the element where the like is attached.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/likes/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_like_from_element(
        self,
        element_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a "Like" added to the element by this user.

        Parameters
        ----------

        element_guid
            - unique identifier for the element where the like is attached.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        note_guid
            - unique id for the note .
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/notes/{note_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_note(
        self,
        note_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        note_guid
            - unique id for the note .
        server_name
            - name of the server instances for this request
        body
            - null request body.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note log from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        note_log_guid
            - unique id for the note log.
        server_name
            - name of the server instances for this request
        body
            - null request body.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/note-logs/{note_log_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_note_log(
        self,
        note_log_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a note log from the repository.

        All the relationships to referenceables are lost.

        Parameters
        ----------
        note_log_guid
            - unique id for the note log.
        server_name
            - name of the server instances for this request
        body
            - null request body.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes of a star rating/review that was added to the element by this user.

        Parameters
        ----------

        element_guid
            - unique identifier for the element where the rating is attached.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/ratings/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_rating_from_element(
        self,
        element_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes of a star rating/review that was added to the element by this user.

        Parameters
        ----------

        element_guid
            - unique identifier for the element where the rating is attached.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a link between a tag and an element that was added by this user.


        Parameters
        ----------

        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/elements/{element_guid}/tags/{tag_guid}/remove{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def remove_tag_from_element(
        self,
        element_guid: str,
        tag_guid: str,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Removes a link between a tag and an element that was added by this user.


        Parameters
        ----------
        element_guid
            - unique id for the element.
        tag_guid
            - unique id of the tag.

        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Link a comment that contains the best answer to a question posed in another comment.

        Parameters
        ----------
        server_name
            - name of the server to route the request to
        question_comment_guid
            - unique identifier of the comment containing the question
        answer_comment_guid
            - unique identifier of the comment containing the accepted answer
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/comments/questions/{question_comment_guid}/answers/{answer_comment_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def setup_accepted_answer(
        self,
        question_comment_guid: str,
        answer_comment_guid: str,
        is_public: bool = True,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Link a comment that contains the best answer to a question posed in another comment.

        Parameters
        ----------
        server_name
            - name of the server to route the request to
        question_comment_guid
            - unique identifier of the comment containing the question
        answer_comment_guid
            - unique identifier of the comment containing the accepted answer
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_merge_update: bool = None,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment.

        Parameters
        ----------
        comment_guid
            - unique identifier for the comment to change.
        body
            - containing type of comment enum and the text of the comment.

        is_merge_update
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("isMergeUpdate", is_merge_update),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/comments/{comment_guid}/update{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_comment(
        self,
        comment_guid: str,
        body: dict,
        is_merge_update: bool = None,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment.

        Parameters
        ----------
        comment_guid
            - unique identifier for the comment to change.
        body
            - containing type of comment enum and the text of the comment.

        is_merge_update
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment's visibility.

        Parameters
        ----------

        comment_guid
            - unique identifier for the comment to change.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("isPublic", is_public),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/parents/{parent_guid}/comments/{comment_guid}/update-visibility{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_comment_visibility(
        self,
        parent_guid: str,
        comment_guid: str,
        is_public: bool,
        body: dict = {},
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing comment's visibility.

        Parameters
        ----------

        comment_guid
            - unique identifier for the comment to change.
        is_public
            - is this visible to other people
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_merge_update: bool = None,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note.

        Parameters
        ----------

        note_guid
            - unique identifier for the note to change.
        is_merge_update
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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

        possible_query_params = query_string(
            [
                ("isMergeUpdate", is_merge_update),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/notes/{note_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_note(
        self,
        note_guid: str,
        body: dict,
        is_merge_update: bool = None,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note.

        Parameters
        ----------

        note_guid
            - unique identifier for the note to change.
        is_merge_update
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body
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
        is_merge_update: bool = None,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note log.

        Parameters
        ----------
        note_log_guid
            - unique identifier for the note log to change.
        body
            - containing type of comment enum and the text of the comment.

        is_merge_update
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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

        possible_query_params = query_string(
            [
                ("isMergeUpdate", is_merge_update),
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/note-logs/{note_log_guid}{possible_query_params}"
        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_note_log(
        self,
        note_log_guid: str,
        body: dict,
        is_merge_update: bool = None,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Update an existing note log.

        Parameters
        ----------
        note_log_guid
            - unique identifier for the note log to change.
        body
            - containing type of comment enum and the text of the comment.

        is_merge_update
            - should the new properties be merged with existing properties (true) or completely replace them (false)?
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
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
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Updates the description of an existing tag (either private or public).

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        tag_guid
            - unique id for the tag
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body - contains the name of the tag and (optional) description of the tag.

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

        possible_query_params = query_string(
            [
                ("viewServiceUrlMarker", view_service_url_marker),
                ("accessServiceUrlMarker", access_service_url_marker),
            ]
        )
        url = f"{base_path(self, self.view_server)}/tags/{tag_guid}/update{possible_query_params}"

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def update_tag_description(
        self,
        tag_guid: str,
        body: str,
        view_service_url_marker: str = None,
        access_service_url_marker: str = None,
    ) -> dict | str:
        """
        Updates the description of an existing tag (either private or public).

        Parameters
        ----------
        server_name
            - name of the server instances for this request
        tag_guid
            - unique id for the tag
        view_service_url_marker
            - optional view service URL marker (overrides access_service_url_marker)
        access_service_url_marker
            - optional access service URL marker used to identify which back end service to call
        body - contains the name of the tag and (optional) description of the tag.

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
                view_service_url_marker,
                access_service_url_marker,
            )
        )
        return response


if __name__ == "__main__":
    print("Main-Feedback Manager")
