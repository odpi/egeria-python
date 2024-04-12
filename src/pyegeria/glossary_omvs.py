"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains an initial version of the glossary_omvs module. There are additional methods that will be
added in subsequent versions of the glossary_omvs module.

"""
import json
from datetime import datetime
import asyncio

# import json
from pyegeria._client import Client, max_paging_size
from pyegeria._globals import enable_ssl_check
from pyegeria._validators import (
    validate_name,
    validate_guid,
    validate_url, validate_search_string,
)
from pyegeria.utils import body_slimmer


class GlossaryBrowser(Client):
    """
    GlossaryBrowser is a class that extends the Client class. It provides methods to search and retrieve glossaries,
    terms and categories.

    Attributes:

        server_name: str
            The name of the View Server to connect to.
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
            token: str = None,
            user_id: str = None,
            user_pwd: str = None,
            verify_flag: bool = enable_ssl_check,
            sync_mode: bool = True
    ):
        self.admin_command_root: str
        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token, async_mode=sync_mode)

    #
    #       Glossaries
    #
    async def _async_find_glossaries(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                     ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                                     for_duplicate_processing: bool = False, type_name: str = None,
                                     server_name: str = None,
                                     start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary metadata elements that contain the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional
        type_name: str, [default=None], optional
            An optional parameter indicating the subtype of the glossary to filter by.
            Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        Returns
        -------
        List | str

        A list of glossary definitions active in the server.

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
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        validate_search_string(search_string)

        if search_string == '*':
            search_string = None

        body = {
            "class": "SearchStringRequestBody",
            "searchString": search_string,
            "effectiveTime": effective_time,
            "typeName": type_name
        }
        body = body_slimmer(body)
        # print(f"\n\nBody is: \n{body}")

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        response = await self._async_make_request("POST", url, body)
        return response

    def find_glossaries(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                        ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                        for_duplicate_processing: bool = False, type_name: str = None, server_name: str = None,
                        start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary metadata elements that contain the search string.
                   The search string is located in the request body and is interpreted as a plain string.
                   The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

           Parameters
           ----------
           search_string: str,
               Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.

           effective_time: str, [default=None], optional
               Effective time of the query. If not specified will default to any time.
           server_name : str, optional
               The name of the server to  configure.
               If not provided, the server name associated with the instance is used.
           starts_with : bool, [default=False], optional
               Starts with the supplied string.
           ends_with : bool, [default=False], optional
               Ends with the supplied string
           ignore_case : bool, [default=False], optional
               Ignore case when searching
           for_lineage : bool, [default=False], optional
                Indicates the search is for lineage.
           for_duplicate_processing : bool, [default=False], optional
           type_name: str, [default=None], optional
               An optional parameter indicating the subtype of the glossary to filter by.
               Values include 'ControlledGlossary', 'EditingGlossary', and 'StagingGlossary'
            start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
           Returns
           -------
           List | str

           A list of glossary definitions active in the server.

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
        response = loop.run_until_complete(self._async_find_glossaries(search_string, effective_time, starts_with,
                                        ends_with, ignore_case, for_lineage,
                                        for_duplicate_processing,type_name,
                                        server_name,start_from, page_size))

        return response.json().get("elementList", "No Glossaries found")

    async def _async_get_glossary_by_guid(self, glossary_guid: str, server_name: str = None,
                                          effective_time: str = None) -> dict:
        """ Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
            effective_time: str, optional
                Effective time of the query. If not specified will default to any time.
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_guid)

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time
        }

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/retrieve")
        print(url)
        response = await self._async_make_request("POST", url, payload=body)
        return response

    def get_glossary_by_guid(self, glossary_guid: str, server_name: str = None) -> dict:
        """ Retrieves information about a glossary
        Parameters
        ----------
            glossary_guid : str
                Unique idetifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_by_guid(glossary_guid, server_name))
        return response

    async def _async_get_glossaries_by_name(self, glossary_name: str, effective_time: datetime = None,
                                            server_name: str = None,
                                            start_from: int = 0, page_size: int = None) -> dict | str:
        """ Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
             When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        validate_name(glossary_name)

        if effective_time is None:
            body = {"name": glossary_name}
        else:
            body = {"name": glossary_name, "effectiveTime": effective_time}

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        response = await self._async_make_request("POST", url, body)
        return response.json()

    def get_glossaries_by_name(self, glossary_name: str, effective_time: datetime = None, server_name: str = None,
                               start_from: int = 0, page_size: int = None) -> dict | str:
        """ Retrieve the list of glossary metadata elements with an exactly matching qualified or display name.
            There are no wildcards supported on this request.

        Parameters
        ----------
        glossary_name: str,
            Name of the glossary to be retrieved
        effective_time: datetime, [default=None], optional
            Effective time of the query. If not specified will default to any effective time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            he class instance.

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
        ConfigurationErrorException
          Raised when configuration parameters passed on earlier calls turn out to be
          invalid or make the new call invalid.
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossaries_by_name(glossary_name, effective_time,
                                                                  server_name, start_from, page_size))
        return response

    async def _async_get_terms_for_glossary(self, glossary_guid: str, server_name: str = None,
                                            effective_time: datetime = None,
                                            start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary terms associated with a glossary.
            The request body also supports the specification of an effective time for the query.
        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
            effective_time : str, optional
                If specified, the query is performed as of the `effective_time`
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """

        if server_name is None:
            server_name = self.server_name
        validate_guid(glossary_guid)

        if page_size is None:
            page_size = self.page_size

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"{glossary_guid}/terms/retrieve?startFrom={start_from}&pageSize={page_size}")

        if effective_time is not None:
            body = {
                "effectiveTime": str(effective_time)
            }
            response = await self._async_make_request("POST", url, body)
        else:
            response = await self._async_make_request("POST", url)

        return response.json().get("elementList", "No terms found")

    def get_terms_for_glossary(self, glossary_guid: str, server_name: str = None, effective_time: datetime = None,
                               start_from: int = 0, page_size: int = None) -> list | str:
        """ Retrieve the list of glossary terms associated with a glossary.
            The request body also supports the specification of an effective time for the query.
        Parameters
        ----------
            glossary_guid : str
                Unique identifier for the glossary
            server_name : str, optional
               The name of the server to get the configured access services for.
               If not provided, the server name associated with the instance is used.
            effective_time : str, optional
                If specified, the query is performed as of the `effective_time`
            start_from: int, optional defaults to 0
                The page number to start retrieving elements from
            page_size : int, optional defaults to None
                The number of elements to retrieve
        Returns
        -------
        dict
            The glossary definition associated with the glossary_guid

        Raises
        ------
         InvalidParameterException
             If the client passes incorrect parameters on the request - such as bad URLs or invalid values.
         PropertyServerException
             Raised by the server when an issue arises in processing a valid request.
         NotAuthorizedException
             The principle specified by the user_id does not have authorization for the requested action.
        Notes
        -----
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_terms_for_glossary(glossary_guid, server_name,
                                                                  effective_time, start_from,
                                                                  page_size))

        return response

    async def _async_get_glossary_for_term(self, term_guid: str, server_name: str = None,
                                           effective_time: datetime = None,
                                           for_lineage: bool = False, for_duplicate_processing: bool = False) -> dict:
        if server_name is None:
            server_name = self.server_name
        validate_guid(term_guid)
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "EffectiveTimeQueryRequestBody",
            "effectiveTime": effective_time
        }
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"for-term/{term_guid}/retrieve?forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}"

               )

        response = await self._async_make_request("POST", url, body)
        return json.loads(response.text)

    def get_glossary_for_term(self, term_guid: str, server_name: str = None, effective_time: datetime = None,
                              for_lineage: bool = False, for_duplicate_processing: bool = False) -> dict:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_glossary_for_term(term_guid, server_name,
                                                                       effective_time, for_lineage,
                                                                       for_duplicate_processing))
        return response

    async def _async_get_terms_by_name(self, term: str, glossary_guid: str = None, status_filter: list = [],
                                       server_name: str = None,
                                       effective_time: datetime = None, for_lineage: bool = False,
                                       for_duplicate_processing: bool = False,
                                       start_from: int = 0, page_size: int = None) -> list:
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size

        validate_name(term)

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "GlossaryNameRequestBody",
            "glossaryGUID": glossary_guid,
            "name": term,
            "effectiveTime": effective_time,
            "limitResultsByStatus": status_filter
        }
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-name?startFrom={start_from}&pageSize={page_size}&"
               f"&forLineage={for_lineage_s}&forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")

    def get_terms_by_name(self, term: str, glossary_guid: str = None, status_filter: list = [], server_name: str = None,
                          effective_time: datetime = None, for_lineage: bool = False,
                          for_duplicate_processing: bool = False,
                          start_from: int = 0, page_size: int = None) -> list:
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_get_terms_by_name(term, glossary_guid, status_filter,
                                                             server_name, effective_time, for_lineage,
                                                             for_duplicate_processing, start_from, page_size))
        return response

    async def _async_find_glossary_terms(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                                         effective_time: str = None, starts_with: bool = False,
                                         ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                                         for_duplicate_processing: bool = False, server_name: str = None,
                                         start_from: int = 0, page_size: int = None) -> list | str:

        """ Retrieve the list of glossary term metadata elements that contain the search string.

        Parameters
        ----------
        search_string: str
            Search string to use to find matching glossaries. If the search string is '*' then all glossaries returned.
        glossary_guid str
            Identifier of the glossary to search within. If None, then all glossaries are searched.
        status_filter: list, default = [], optional
            Filters the results by the included Term statuses (such as 'ACTIVE', 'DRAFT'). If not specified,
            the results will not be filtered.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
            If the effective time is not in the right format then it will be considered any.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
        starts_with : bool, [default=False], optional
            Starts with the supplied string.
        ends_with : bool, [default=False], optional
            Ends with the supplied string
        ignore_case : bool, [default=False], optional
            Ignore case when searching
        for_lineage : bool, [default=False], optional

        for_duplicate_processing : bool, [default=False], optional

        start_from: str, [default=0], optional
            Page of results to start from
        page_size : int, optional
            Number of elements to return per page - if None, then default for class will be used.

        Returns
        -------
        List | str

        A list of term definitions

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
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.
        The request body also supports the specification of a glossaryGUID to restrict the search to within a single glossary.
        """
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == '*':
            search_string = None

        # validate_search_string(search_string)

        body = {
            "class": "GlossarySearchStringRequestBody",
            "glossaryGUID": glossary_guid,
            "searchString": search_string,
            "effectiveTime": effective_time,
            "limitResultsByStatus": status_filter
        }
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")
        # return response.text

    def find_glossary_terms(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                            effective_time: str = None, starts_with: bool = False,
                            ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                            for_duplicate_processing: bool = False, server_name: str = None,
                            start_from: int = 0, page_size: int = None) -> list | str:

        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._async_find_glossary_terms(search_string, glossary_guid, status_filter,
                                                               effective_time, starts_with,
                                                               ends_with, ignore_case, for_lineage,
                                                               for_duplicate_processing, server_name,
                                                               start_from, page_size))

        return response

#
#   Catagories
#

#
#   Feedback
#
    async def _async_get_comment(self, commemtGUID: str, effective_time: datetime, server_name: str=None,
                                 for_lineage: bool = False, for_duplicate_processing: bool = False) -> dict | list:
        """ Retrieve the comment specified by the comment GUID """
        if server_name is None:
            server_name = self.server_name

        validate_guid(commemtGUID)

        if effective_time is None:
            effective_time = datetime.now().isoformat()

        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "effective_time": effective_time
        }

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/comments/"
               f"{commemtGUID}?forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json()


    async def _async_add_comment_reply(self, commentGUID: str, is_public: bool, comment_type: str, comment_text: str,
                                       server_name: str=None, for_lineage: bool = False,
                                       for_duplicate_processing: bool = False ) -> str:
        """ Reply to a comment """

        if server_name is None:
            server_name = self.server_name

        validate_guid(commentGUID)
        validate_name(comment_type)

        is_public_s = str(is_public).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "CommentRequestBody",
            "commentType": comment_type,
            "commentText": comment_text,
            "isPublic": is_public
        }

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/comments/"
               f"{commentGUID}/replies?isPublic={is_public_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response


    async def _async_update_comment(self, commentGUID: str, is_public: bool, comment_type: str, comment_text: str,
                                    server_name: str=None, is_merge_update: bool = False, for_lineage: bool = False,
                                    for_duplicate_processing: bool = False) -> str:
        """ Update the specified comment"""
        if server_name is None:
            server_name = self.server_name

        validate_guid(commentGUID)
        validate_name(comment_type)

        is_public_s = str(is_public).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()

        body = {
            "class": "CommentRequestBody",
            "commentType": comment_type,
            "commentText": comment_text,
            "isPublic": is_public
        }

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/comments/"
               f"{commentGUID}/replies?isPublic={is_public_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response

    async def _async_find_comment(self, search_string: str, glossary_guid: str = None, status_filter: list = [],
                                         effective_time: str = None, starts_with: bool = False,
                                         ends_with: bool = False, ignore_case: bool = False, for_lineage: bool = False,
                                         for_duplicate_processing: bool = False, server_name: str = None,
                                         start_from: int = 0, page_size: int = None):
        """Find comments by search string"""
        if server_name is None:
            server_name = self.server_name
        if page_size is None:
            page_size = self.page_size
        if effective_time is None:
            effective_time = datetime.now().isoformat()
        starts_with_s = str(starts_with).lower()
        ends_with_s = str(ends_with).lower()
        ignore_case_s = str(ignore_case).lower()
        for_lineage_s = str(for_lineage).lower()
        for_duplicate_processing_s = str(for_duplicate_processing).lower()
        if search_string == '*':
            search_string = None

        # validate_search_string(search_string)

        body = {
            "class": "GlossarySearchStringRequestBody",
            "glossaryGUID": glossary_guid,
            "searchString": search_string,
            "effectiveTime": effective_time,
            "limitResultsByStatus": status_filter
        }
        # body = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/glossary-browser/glossaries/"
               f"terms/by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}&forLineage={for_lineage_s}&"
               f"forDuplicateProcessing={for_duplicate_processing_s}")

        # print(f"\n\nURL is: \n {url}\n\nBody is: \n{body}")

        response = await self._async_make_request("POST", url, body)
        return response.json().get("elementList", "No terms found")