"""PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the feedback_manager_omvs
module.

"""

import asyncio
import json
import time

# import json
from pyegeria._server_client import ServerClient, max_paging_size
from pyegeria._globals import NO_ELEMENTS_FOUND

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




class FeedbackManager(ServerClient):
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
        self.admin_command_root: str = f"{platform_url}/servers/{view_server}api/open-metadata/feedback-manager/"
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        ServerClient.__init__(
            self,
            view_server,
            platform_url,
            user_id,
            user_pwd,
            token=token,
        )

    def make_feedback_qn(self, feedback_type, src_guid) -> str:
        timestamp = int(time.time())
        return f"{feedback_type}::{src_guid}::{self.user_id}::{timestamp}"



    #
    ## add_comment_to_element implementation
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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



    #
    ## find_comments implementation
    #


    #
    ## get_attached_comments implementation
    #



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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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

    #
    ## remove_comment_from_element implementation
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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



    #
    ## remove_note_log implementation
    #


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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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
        PyegeriaInvalidParameterException
            one of the parameters is null or invalid or
        PyegeriaAPIException
            There is a problem adding the element properties to the metadata repository or
        PyegeriaUnauthorizedException
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



if __name__ == "__main__":
    print("Main-Feedback Manager")
