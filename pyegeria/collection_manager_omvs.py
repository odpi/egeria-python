"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""
import asyncio
import time

# import json
from pyegeria._client import Client
from pyegeria._exceptions import (InvalidParameterException, )
from pyegeria._validators import (validate_guid, validate_search_string, )
from pyegeria.utils import body_slimmer


class CollectionManager(Client):
    """
    Maintain and explore the contents of nested collections. These collections can be used to represent digital
    products, or collections of resources for a particular project or team. They can be used to organize assets and
    other resources into logical groups.

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

     """

    def __init__(self, server_name: str, platform_url: str, token: str = None, user_id: str = None,
                 user_pwd: str = None, sync_mode: bool = True):
        self.command_base: str = f"/api/open-metadata/collection-manager/collections"
        Client.__init__(self, server_name, platform_url, user_id=user_id, token=token, async_mode=sync_mode)

    #
    #       Retrieving Collections - https://egeria-project.org/concepts/collection
    #
    async def _async_get_linked_collections(self, parent_guid: str, server_name: str = None, start_from: int = 0,
                                            page_size: int = None) -> list:
        """  Returns the list of collections that are linked off of the supplied element. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked collections from.
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
        List

        A list of collections linked off of the supplied element.

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

        body = {

        }

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/collection-manager/"
               f"metadata-elements/{parent_guid}/collections?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body)
        return resp.json()

    def get_linked_collections(self, parent_guid: str, server_name: str = None, start_from: int = 0,
                               page_size: int = None) -> list:
        """  Returns the list of collections that are linked off of the supplied element.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked collections from.
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
        List

        A list of collections linked off of the supplied element.

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
        resp = loop.run_until_complete(
            self._async_get_linked_collections(parent_guid, server_name, start_from, page_size))
        return resp

    async def _async_get_classified_collections(self, classification: str, server_name: str = None, start_from: int = 0,
                                                page_size: int = None) -> list | str:
        """ Returns the list of collections with a particular classification.  These classifications
            are typically "RootCollection", "Folder" or "DigitalProduct". Async version.

        Parameters
        ----------
        classification: str
            The classification of the collection to inspect.
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
        list | str
            The list of collections (if found) with the specified classification. Returns a string if none found.

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
        if page_size is None:
            page_size = self.page_size

        body = {"filter": classification}

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/by-classifications?"
               f"startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body)
        # result = resp.json().get("elements","No elements found")
        result = resp.json().get("elements", "No Elements to return")
        return result

    def get_classified_collections(self, classification: str, server_name: str = None, start_from: int = 0,
                                   page_size: int = None) -> list | str:
        """  Returns the list of collections with a particular classification.  These classifications
             are typically "RootCollection", "Folder" or "DigitalProduct".

        Parameters
        ----------
        classification: str
            The classification of the collection to inspect.
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
        List | str

        A list of collections linked off of the supplied element.

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
        resp = loop.run_until_complete(
            self._async_get_classified_collections(classification, server_name, start_from, page_size))
        return resp

    async def _async_find_collections(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                                      ends_with: bool = False, ignore_case: bool = False, server_name: str = None,
                                      start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching collections. If the search string is '*' then all glossaries returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. ISO8601 format is assumed.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        List | str

        A list of collections match matching the search string. Returns a string if none found.

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

        validate_search_string(search_string)

        if search_string == '*':
            search_string = None

        body = {"filter": search_string, "effective_time": effective_time}

        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/"
               f"by-search-string?startFrom={start_from}&pageSize={page_size}&startsWith={starts_with_s}&"
               f"endsWith={ends_with_s}&ignoreCase={ignore_case_s}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("elements", "No elements found")

    def find_collections(self, search_string: str, effective_time: str = None, starts_with: bool = False,
                         ends_with: bool = False, ignore_case: bool = False, server_name: str = None,
                         start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        search_string: str,
            Search string to use to find matching collections. If the search string is '*' then all glossaries returned.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.
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
        List | str

        A list of collections match matching the search string. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_find_collections(search_string, effective_time, starts_with, ends_with, ignore_case,
                                         server_name, start_from, page_size))

        return resp

    async def _async_get_collections_by_name(self, name: str, effective_time: str = None, server_name: str = None,
                                             start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections with a particular name.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
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
        List | str

        A list of collections match matching the name. Returns a string if none found.

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

        validate_search_string(name)

        body = {"filter": name, effective_time: effective_time, }
        body_s = body_slimmer(body)
        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/"
               f"by-name?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("elements", "No elements found")

    def get_collections_by_name(self, name: str, effective_time: str = None, server_name: str = None,
                                start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
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
        List | str

        A list of collections match matching the search string. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_get_collections_by_name(name, effective_time, server_name, start_from, page_size))

        return resp

    async def _async_get_collections_by_type(self, collection_type: str, effective_time: str = None,
                                             server_name: str = None, start_from: int = 0,
                                             page_size: int = None) -> list | str:
        """ Returns the list of collections with a particular collectionType. This is an optional text field in the
            collection element.

        Parameters
        ----------
        collection_type: str,
            collection_type to use to find matching collections.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
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
        List | str

        A list of collections match matching the name. Returns a string if none found.

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

        validate_search_string(collection_type)

        body = {"filter": collection_type, effective_time: effective_time, }
        body_s = body_slimmer(body)

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/"
               f"by-collection-type?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("POST", url, body_s)
        return resp.json().get("elements", "No elements found")

    def get_collections_by_type(self, collection_type: str, effective_time: str = None, server_name: str = None,
                                start_from: int = 0, page_size: int = None) -> list | str:
        """ Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        collection_type: str,
            collection type to find.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
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
        List | str

        A list of collections match matching the search string. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_get_collections_by_type(collection_type, effective_time, server_name, start_from, page_size))

        return resp

    async def _async_get_collection(self, collection_guid: str, effective_time: str = None,
                                    server_name: str = None) -> dict | str:
        """ Return the properties of a specific collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            unique identifier of the collection.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time. Time in ISO8601 format is assumed.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

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

        validate_guid(collection_guid)

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}"
        body = {"effective_time": effective_time, }
        resp = await self._async_make_request("GET", url, body)
        return resp.json()

    def get_collection(self, collection_guid: str, effective_time: str = None, server_name: str = None) -> dict | str:
        """ Return the properties of a specific collection.

        Parameters
        ----------
        collection_guid: str,
            unique identifier of the collection.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
        server_name : str, optional
            The name of the server to  configure.
            If not provided, the server name associated with the instance is used.

        Returns
        -------
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(self._async_get_collection(collection_guid, effective_time, server_name))

        return resp

    #
    #   Create collection methods
    #
    async def _async_create_collection_w_body(self, classification_name: str, body: dict,
                                              server_name: str = None) -> str:
        """  Create Collections: https://egeria-project.org/concepts/collection Async version.

            Parameters
            ----------
            classification_name: str
                Type of collection to create; e.g RootCollection, Folder, Set, DigitalProduct, etc.
            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the
                instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}?"
               f"classificationName={classification_name}")

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID returned")

    def create_collection_w_body(self, classification_name: str, body: dict, server_name: str = None) -> str:
        """ Create Collections: https://egeria-project.org/concepts/collection

            Parameters
            ----------
            classification_name: str
                Type of collection to create; e.g RootCollection, Folder, Set, DigitalProduct, etc.
            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(self._async_create_collection_w_body(classification_name, body, server_name))
        return resp

    async def _async_create_collection(self, classification_name: str, anchor_guid: str, parent_guid: str,
                                       parent_relationship_type_name: str, parent_at_end1: bool, display_name: str,
                                       description: str, collection_type: str, is_own_anchor: bool = False,
                                       collection_ordering: str = None, order_property_name: str = None,
                                       server_name: str = None) -> str:
        """ Create Collections: https://egeria-project.org/concepts/collection Async version.

            Parameters
            ----------
            classification_name: str
                Type of collection to create; e.g RootCollection, Folder, Set, DigitalProduct, etc.
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element. Set to null if no
                anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            collection_ordering: str, optional, defaults to "OTHER"
                Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER", "DATE_CREATED",
                 "OTHER"
            order_property_name: str, optional, defaults to "Something"
                Property to use for sequencing if collection_ordering is "OTHER"
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the instance is
                 used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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

        if parent_guid is None:
            is_own_anchor = False
        is_own_anchor_s = str(is_own_anchor).lower()

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}?"
               f"classificationName={classification_name}")

        body = {"anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor_s, "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                "collectionProperties": {"class": "CollectionProperties",
                                         "qualifiedName": f"{classification_name}-{display_name}-{time.asctime()}",
                                         "name": display_name,
                                         "description": description, "collectionType": collection_type,
                                         "collectionOrdering": collection_ordering,
                                         "orderPropertyName": order_property_name}}

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID returned")

    def create_collection(self, classification_name: str, anchor_guid: str, parent_guid: str,
                          parent_relationship_type_name: str, parent_at_end1: bool, display_name: str, description: str,
                          collection_type: str, is_own_anchor: bool = False, collection_ordering: str = "OTHER",
                          order_property_name: str = "Something", server_name: str = None) -> str:
        """  Create Collections: https://egeria-project.org/concepts/collection

            Parameters
            ----------
            classification_name: str
                Type of collection to create; e.g RootCollection, Folder, Set, DigitalProduct, etc.
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element.
                Set to null if no anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            collection_ordering: str, optional, defaults to "OTHER"
                Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER",
                "DATE_CREATED", "OTHER"
            order_property_name: str, optional, defaults to "Something"
                Property to use for sequencing if collection_ordering is "OTHER"
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the
                instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_create_collection(classification_name, anchor_guid, parent_guid, parent_relationship_type_name,
                                          parent_at_end1, display_name, description, collection_type, is_own_anchor,
                                          collection_ordering, order_property_name, server_name))
        return resp

    async def _async_create_root_collection(self, anchor_guid: str, parent_guid: str,
                                            parent_relationship_type_name: str, parent_at_end1: bool, display_name: str,
                                            description: str, collection_type: str, is_own_anchor: bool = False,
                                            server_name: str = None) -> str:
        """ Create a new collection with the RootCollection classification.  Used to identify the top of a
            collection hierarchy. Async version.

            Parameters
            ----------
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element.
                Set to null if no anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If none, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        is_own_anchor_s = str(is_own_anchor).lower()
        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/root-collection"

        body = {"anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor_s, "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                "collectionProperties": {"class": "CollectionProperties",
                                         "qualifiedName": f"root-collection-{display_name}-{time.asctime()}",
                                         "name": display_name,
                                         "description": description, "collectionType": collection_type,

                                         }}

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID Returned")

    def create_root_collection(self, anchor_guid: str, parent_guid: str, parent_relationship_type_name: str,
                               parent_at_end1: bool, display_name: str, description: str, collection_type: str,
                               is_own_anchor: bool = False, server_name: str = None) -> str:
        """  Create a new collection with the RootCollection classification.  Used to identify the top of a
             collection hierarchy.

            Parameters
            ----------
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element.
                Set to null if no anchor,
                or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If None, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_create_root_collection(anchor_guid, parent_guid, parent_relationship_type_name, parent_at_end1,
                                               display_name, description, collection_type, is_own_anchor, server_name))
        return resp

    async def _async_create_data_spec_collection(self, anchor_guid: str, parent_guid: str,
                                                 parent_relationship_type_name: str, parent_at_end1: bool,
                                                 display_name: str, description: str, collection_type: str,
                                                 is_own_anchor: bool = True, collection_ordering: str = "OTHER",
                                                 order_property_name: str = "Something",
                                                 server_name: str = None) -> str:
        """  Create a new collection with the DataSpec classification.  Used to identify a collection of data fields
             and schema types. Async version.

            Parameters
            ----------
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element.
                Set to null if no anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            collection_ordering: str, optional, defaults to "OTHER"
                Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER",
                "DATE_CREATED", "OTHER"
            order_property_name: str, optional, defaults to "Something"
                Property to use for sequencing if collection_ordering is "OTHER"
            server_name: str, optional, defaults to None
                The name of the server to  configure. If None, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        is_own_anchor_s = str(is_own_anchor).lower()
        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/data-spec-collection"

        body = {"anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor_s, "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                "collectionProperties": {"class": "CollectionProperties",
                                         "qualifiedName": f"data-spec-collection-{display_name}-{time.asctime()}",
                                         "name": display_name,
                                         "description": description, "collectionType": collection_type,
                                         "collectionOrdering": collection_ordering,
                                         "orderPropertyName": order_property_name}}

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID Returned")

    def create_data_spec_collection(self, anchor_guid: str, parent_guid: str, parent_relationship_type_name: str,
                                    parent_at_end1: bool, display_name: str, description: str, collection_type: str,
                                    is_own_anchor: bool, collection_ordering: str = "OTHER",
                                    order_property_name: str = "Something", server_name: str = None) -> str:
        """  Create a new collection with the DataSpec classification.  Used to identify a collection of data fields
         and schema types.

        Parameters
        ----------
        anchor_guid: str
            The unique identifier of the element that should be the anchor for the new element.
            Set to null if no anchor, or if this collection is to be its own anchor.
        parent_guid: str
           The optional unique identifier for an element that should be connected to the newly created element.
           If this property is specified, parentRelationshipTypeName must also be specified
        parent_relationship_type_name: str
            The name of the relationship, if any, that should be established between the new element and the parent
            element. Examples could be "ResourceList" or "DigitalServiceProduct".
        parent_at_end1: bool
            Identifies which end any parent entity sits on the relationship.
        display_name: str
            The display name of the element. Will also be used as the basis of the qualified_name.
        description: str
            A description of the collection.
        collection_type: str
            Add appropriate valid value for the collection type.
        is_own_anchor: bool, optional, defaults to False
            Indicates if the collection should classified as its own anchor or not.
        collection_ordering: str, optional, defaults to "OTHER"
            Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER", "DATE_CREATED", "OTHER"
        order_property_name: str, optional, defaults to "Something"
            Property to use for sequencing if collection_ordering is "OTHER"
        server_name: str, optional, defaults to None
            The name of the server to  configure. If not provided, the server name associated with the instance is used.

        Returns
        -------
        str - the guid of the created collection

        A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_create_data_spec_collection(anchor_guid, parent_guid, parent_relationship_type_name,
                                                    parent_at_end1, display_name, description, collection_type,
                                                    is_own_anchor, collection_ordering, order_property_name,
                                                    server_name))
        return resp

    async def _async_create_folder_collection(self, anchor_guid: str, parent_guid: str,
                                              parent_relationship_type_name: str, parent_at_end1: bool,
                                              display_name: str, description: str, collection_type: str,
                                              is_own_anchor: bool = True, collection_ordering: str = "OTHER",
                                              order_property_name: str = "Something", server_name: str = None) -> str:
        """ Create a new collection with the Folder classification.  This is used to identify the organizing
            collections in a collection hierarchy. Async version.

            Parameters
            ----------
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element.
                Set to null if no anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            collection_ordering: str, optional, defaults to "OTHER"
                Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER",
                "DATE_CREATED", "OTHER"
            order_property_name: str, optional, defaults to "Something"
                Property to use for sequencing if collection_ordering is "OTHER"
            server_name: str, optional, defaults to None
                The name of the server to  configure. If None, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        is_own_anchor_s = str(is_own_anchor).lower()

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/folder"

        body = {"anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor_s, "parentGUID": parent_guid,
                "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                "collectionProperties": {"class": "CollectionProperties",
                                         "qualifiedName": f"folder-collection-{display_name}-{time.asctime()}",
                                         "name": display_name,
                                         "description": description, "collectionType": collection_type,
                                         "collectionOrdering": collection_ordering,
                                         "orderPropertyName": order_property_name}}

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID returned")

    def create_folder_collection(self, anchor_guid: str, parent_guid: str, parent_relationship_type_name: str,
                                 parent_at_end1: bool, display_name: str, description: str, collection_type: str,
                                 is_own_anchor: bool, collection_ordering: str = "OTHER",
                                 order_property_name: str = "Something", server_name: str = None) -> str:
        """ Create a new collection with the Folder classification.  This is used to identify the organizing
            collections in a collection hierarchy.

            Parameters
            ----------
            anchor_guid: str
                The unique identifier of the element that should be the anchor for the new element.
                Set to null if no anchor, or if this collection is to be its own anchor.
            parent_guid: str
               The optional unique identifier for an element that should be connected to the newly created element.
               If this property is specified, parentRelationshipTypeName must also be specified
            parent_relationship_type_name: str
                The name of the relationship, if any, that should be established between the new element and the parent
                element. Examples could be "ResourceList" or "DigitalServiceProduct".
            parent_at_end1: bool
                Identifies which end any parent entity sits on the relationship.
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            collection_type: str
                Add appropriate valid value for the collection type.
            is_own_anchor: bool, optional, defaults to False
                Indicates if the collection should classified as its own anchor or not.
            collection_ordering: str, optional, defaults to "OTHER"
                Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER", "DATE_CREATED",
                "OTHER"
            order_property_name: str, optional, defaults to "Something"
                Property to use for sequencing if collection_ordering is "OTHER"
            server_name: str, optional, defaults to None
                The name of the server to  configure. If None, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

            A JSON dict representing the specified collection. Returns a string if none found.

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
        resp = loop.run_until_complete(
            self._async_create_folder_collection(anchor_guid, parent_guid, parent_relationship_type_name,
                                                 parent_at_end1, display_name, description, collection_type,
                                                 is_own_anchor, collection_ordering, order_property_name, server_name))
        return resp

    async def _async_create_collection_from_template(self, body: dict, server_name: str = None) -> str:
        """ Create a new metadata element to represent a collection using an existing metadata element as a template.
            The template defines additional classifications and relationships that are added to the new collection.
            Async version.

            Parameters
            ----------

            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If None, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

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
            JSON Structure looks like:

            {
              "class": "TemplateRequestBody",
              "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor": false,
              "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName": "open metadata type name",
              "parentAtEnd1": true,
              "templateGUID": "template GUID",
              "replacementProperties": {
                "class": "ElementProperties",
                "propertyValueMap" : {
                  "propertyName" : {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveTypeCategory" : "OM_PRIMITIVE_TYPE_STRING",
                    "primitiveValue" : "value of property"
                  }
                }
              },
              "placeholderPropertyValues" : {
                "placeholderProperty1Name" : "property1Value",
                "placeholderProperty2Name" : "property2Value"
              }
            }

    """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/from-template"

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID Returned")

    def create_collection_from_template(self, body: dict, server_name: str = None) -> str:
        """ Create a new metadata element to represent a collection using an existing metadata element as a template.
            The template defines additional classifications and relationships that are added to the new collection.

            Parameters
            ----------
            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If None, the server name associated with the instance is used.

            Returns
            -------
            str - the guid of the created collection

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
            JSON Structure looks like:

            {
              "class": "TemplateRequestBody",
              "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor": false,
              "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName": "open metadata type name",
              "parentAtEnd1": true,
              "templateGUID": "template GUID",
              "replacementProperties": {
                "class": "ElementProperties",
                "propertyValueMap" : {
                  "propertyName" : {
                    "class": "PrimitiveTypePropertyValue",
                    "typeName": "string",
                    "primitiveTypeCategory" : "OM_PRIMITIVE_TYPE_STRING",
                    "primitiveValue" : "value of property"
                  }
                }
              },
              "placeholderPropertyValues" : {
                "placeholderProperty1Name" : "property1Value",
                "placeholderProperty2Name" : "property2Value"
              }
            }
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_collection_from_template(body, server_name))
        return resp

    async def _async_create_digital_product(self, body: dict, server_name: str = None) -> str:
        """ Create a new collection that represents a digital product. Async version.

            Parameters
            ----------
            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            str - the guid of the created collection

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
            JSON Structure looks like:
            {
              "class" : "NewDigitalProductRequestBody",
              "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor" : false,
              "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName" : "open metadata type name",
              "parentAtEnd1": true,
              "collectionProperties": {
                "class" : "CollectionProperties",
                "qualifiedName": "Must provide a unique name here",
                "name" : "Add display name here",
                "description" : "Add description of the collection here",
                "collectionType": "Add appropriate valid value for type",
                "collectionOrdering" : "OTHER",
                "orderPropertyName" : "Add property name if 'collectionOrdering' is OTHER"
              },
              "digitalProductProperties" : {
                "class" : "DigitalProductProperties",
                "productStatus" : "ACTIVE",
                "productName" : "Add name here",
                "productType" : "Add valid value here",
                "description" : "Add description here",
                "introductionDate" : "date",
                "maturity" : "Add valid value here",
                "serviceLife" : "Add the estimated lifetime of the product",
                "currentVersion": "V1.0",
                "nextVersion": "V1.1",
                "withdrawDate": "date",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              }
            }
    """
        if server_name is None:
            server_name = self.server_name

        url = f"{self.platform_url}/servers/{server_name}/api/open-metadata/collection-manager/digital-products"

        resp = await self._async_make_request("POST", url, body)
        return resp.json().get("guid", "No GUID returned")

    def create_digital_product(self, body: dict, server_name: str = None) -> str:
        """ Create a new collection that represents a digital product. Async version.

            Parameters
            ----------
            body: dict
                A dict representing the details of the collection to create.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            str - the guid of the created collection

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
            JSON Structure looks like:
            {
              "class" : "NewDigitalProductRequestBody",
              "anchorGUID" : "anchor GUID, if set then isOwnAnchor=false",
              "isOwnAnchor" : false,
              "parentGUID" : "parent GUID, if set, set all parameters beginning 'parent'",
              "parentRelationshipTypeName" : "open metadata type name",
              "parentAtEnd1": true,
              "collectionProperties": {
                "class" : "CollectionProperties",
                "qualifiedName": "Must provide a unique name here",
                "name" : "Add display name here",
                "description" : "Add description of the collection here",
                "collectionType": "Add appropriate valid value for type",
                "collectionOrdering" : "OTHER",
                "orderPropertyName" : "Add property name if 'collectionOrdering' is OTHER"
              },
              "digitalProductProperties" : {
                "class" : "DigitalProductProperties",
                "productStatus" : "ACTIVE",
                "productName" : "Add name here",
                "productType" : "Add valid value here",
                "description" : "Add description here",
                "introductionDate" : "date",
                "maturity" : "Add valid value here",
                "serviceLife" : "Add the estimated lifetime of the product",
                "currentVersion": "V1.0",
                "nextVersion": "V1.1",
                "withdrawDate": "date",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              }
            }
    """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_digital_product(body, server_name))
        return resp

    #
    # Manage collections
    #
    async def _async_update_collection(self, collection_guid: str, qualified_name: str = None, display_name: str = None,
                                       description: str = None, collection_type: str = None,
                                       collection_ordering: str = None, order_property_name: str = None,
                                       replace_all_props: bool = False, server_name: str = None) -> None:
        """ Update the properties of a collection.  Async version.

            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            qualified_name: str, optional, defaults to None
                The qualified name of the collection to update.
            display_name: str, optional, defaults to None
               The display name of the element. Will also be used as the basis of the qualified_name.
            description: str, optional, defaults to None
               A description of the collection.
            collection_type: str, optional, defaults to None
               Add appropriate valid value for the collection type.
            collection_ordering: str, optional, defaults to None
               Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER",
               "DATE_CREATED", "OTHER"
            order_property_name: str, optional, defaults to None
               Property to use for sequencing if collection_ordering is "OTHER"
            replace_all_props: bool, optional, defaults to False
                Whether to replace all properties in the collection.
            server_name: str, optional, defaults to None
               The name of the server to  configure. If not provided, the server name associated
               with the instance is used.

            Returns
            -------
            Nothing

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
        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}/update?"
               f"replaceAllProperties={replace_all_props_s}")

        body = {"class": "CollectionProperties", "qualifiedName": qualified_name, "name": display_name,
                "description": description, "collectionType": collection_type,
                "collectionOrdering": collection_ordering,
                "orderPropertyName": order_property_name}
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        return

    def update_collection(self, collection_guid, qualified_name: str = None, display_name: str = None,
                          description: str = None, collection_type: str = None, collection_ordering: str = None,
                          order_property_name: str = None, replace_all_props: bool = False,
                          server_name: str = None) -> None:
        """ Update the properties of a collection.

            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            qualified_name: str
                The qualified name of the collection to update.
            display_name: str
               The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
               A description of the collection.
            collection_type: str
               Add appropriate valid value for the collection type.
            collection_ordering: str, optional, defaults to "OTHER"
               Specifies the sequencing to use in a collection. Examples include "NAME", "OWNER",
               "DATE_CREATED", "OTHER"
            order_property_name: str, optional, defaults to "Something"
               Property to use for sequencing if collection_ordering is "OTHER"
            replace_all_props: bool, optional, defaults to False
                Whether to replace all properties in the collection.
            server_name: str, optional, defaults to None
               The name of the server to  configure. If not provided, the server name associated
               with the instance is used.

            Returns
            -------
            Nothing

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
        loop.run_until_complete(
            self._async_update_collection(collection_guid, qualified_name, display_name, description, collection_type,
                                          collection_ordering, order_property_name, replace_all_props, server_name))
        return

    async def _async_update_digital_product(self, collection_guid: str, body: dict, replace_all_props: bool = False,
                                            server_name: str = None):
        """ Update the properties of the DigitalProduct classification attached to a collection. Async version.

            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            body: dict
                A dict representing the details of the collection to create.
            replace_all_props: bool, optional, defaults to False
                Whether to replace all properties in the collection.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the
                instance is used.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
            {
              "class" : "DigitalProductProperties",
              "productStatus" : "ACTIVE",
              "productName" : "Add name here",
              "productType" : "Add valid value here",
              "description" : "Add description here",
              "introductionDate" : "date",
              "maturity" : "Add valid value here",
              "serviceLife" : "Add the estimated lifetime of the product",
              "currentVersion": "V1.0",
              "nextVersion": "V1.1",
              "withdrawDate": "date",
              "additionalProperties": {
                "property1Name" : "property1Value",
                "property2Name" : "property2Value"
              }
            }
        """
        if server_name is None:
            server_name = self.server_name

        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/collection-manager/digital-products/"
               f"{collection_guid}/update?replaceAllProperties={replace_all_props_s}")

        await self._async_make_request("POST", url, body)
        return

    def update_digital_product(self, collection_guid: str, body: dict, replace_all_props: bool = False,
                               server_name: str = None):
        """ Update the properties of the DigitalProduct classification attached to a collection.

            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            body: dict
                A dict representing the details of the collection to create.
            replace_all_props: bool, optional, defaults to False
                Whether to replace all properties in the collection.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the
                instance is used.

            Returns
            -------
            Nothing

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
            JSON Structure looks like:
            {
              "class" : "DigitalProductProperties",
              "productStatus" : "ACTIVE",
              "productName" : "Add name here",
              "productType" : "Add valid value here",
              "description" : "Add description here",
              "introductionDate" : "date",
              "maturity" : "Add valid value here",
              "serviceLife" : "Add the estimated lifetime of the product",
              "currentVersion": "V1.0",
              "nextVersion": "V1.1",
              "withdrawDate": "date",
              "additionalProperties": {
                "property1Name" : "property1Value",
                "property2Name" : "property2Value"
              }
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_digital_product(collection_guid, body, replace_all_props, server_name))
        return

    async def _async_attach_collection(self, collection_guid: str, element_guid: str, resource_use: str,
                                       resource_use_description: str = None, resource_use_props: dict = None,
                                       watch_resources: bool = False, make_anchor: bool = False,
                                       server_name: str = None) -> None:
        """ Connect an existing collection to an element using the ResourceList relationship (0019). Async version.
            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            element_guid: str
                The guid of the element to attach.
            resource_use: str,
                How the resource is being used.
            resource_use_description: str
                Describe how the resource is being used.
            resource_use_props: dict, optional, defaults to None
                The properties of the resource to be used.
            watch_resources, bool, optional, defaults to False
                Whether to watch for the resources to be updated.
            make_anchor, bool, optional, defaults to False
                Whether to make the this an anchor.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated with the
                instance is used.

            Returns
            -------
            Nothing

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
        watch_resources_s = str(watch_resources).lower()
        make_anchor_s = str(make_anchor).lower()

        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/collection-manager/metadata-elements/"
               f"{element_guid}/collections/{collection_guid}/attach?makeAnchor={make_anchor_s}")

        body = {"class": "ResourceListProperties", "resourceUse": resource_use,
                "resourceUseDescription": resource_use_description, "watchResource": watch_resources_s,
                "resourceUseProperties": resource_use_props}
        await self._async_make_request("POST", url, body)
        return

    def attach_collection(self, collection_guid: str, element_guid: str, resource_use: str,
                          resource_use_description: str, resource_use_props: dict = None, watch_resources: bool = False,
                          make_anchor: bool = False, server_name: str = None) -> None:
        """ Connect an existing collection to an element using the ResourceList relationship (0019).
            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            element_guid: str
                The guid of the element to attach.
            resource_use: str,
                How the resource is being used.
            resource_use_description: str
                Describe how the resource is being used.
            resource_use_props: dict, optional, defaults to None
                The properties of the resource to be used.
            watch_resources: bool, optional, defaults to False
                Whether to watch for the resources to be updated.
            make_anchor: bool, optional, defaults to False
                Whether to make the this an anchor.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            Nothing

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
        loop.run_until_complete(
            self._async_attach_collection(collection_guid, element_guid, resource_use, resource_use_description,
                                          resource_use_props, watch_resources, make_anchor, server_name))
        return

    async def _async_detach_collection(self, collection_guid: str, element_guid: str, server_name: str = None) -> None:
        """ Detach an existing collection from an element.  If the collection is anchored to the element, it is deleted.
            Async version.

            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            element_guid: str
                The guid of the element to attach.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            Nothing

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
        url = (f"{self.platform_url}/servers/{server_name}/api/open-metadata/collection-manager/metadata-elements/"
               f"{element_guid}/collections/{collection_guid}/detach")

        body = {"class": "NullRequestBody"}

        await self._async_make_request("POST", url, body)
        return

    def detach_collection(self, collection_guid: str, element_guid: str, server_name: str = None) -> None:
        """ Connect an existing collection to an element using the ResourceList relationship (0019).
            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            element_guid: str
                The guid of the element to attach.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            Nothing

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
        loop.run_until_complete(self._async_detach_collection(collection_guid, element_guid, server_name))
        return

    async def _async_delete_collection(self, collection_guid: str, server_name: str = None) -> None:
        """ Delete a collection.  It is detected from all parent elements.  If members are anchored to the collection
            then they are also deleted. Async version


            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            Nothing

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
        url = f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}/delete"
        body = {"class": "NullRequestBody"}

        await self._async_make_request("POST", url, body)
        return

    def delete_collection(self, collection_guid: str, server_name: str = None) -> None:
        """ Delete a collection.  It is detected from all parent elements.  If members are anchored to the collection
            then they are also deleted.

            Parameters
            ----------
            collection_guid: str
                The guid of the collection to update.
            server_name: str, optional, defaults to None
                The name of the server to  configure. If not provided, the server name associated
                with the instance is used.

            Returns
            -------
            Nothing

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
        loop.run_until_complete(self._async_delete_collection(collection_guid, server_name))
        return

    async def _async_get_collection_members(self, collection_guid: str, effective_time: str = None,
                                            server_name: str = None, start_from: int = 0,
                                            page_size: int = None) -> list | str:
        """ Return a list of elements that are a member of a collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for.
        effective_time: str, [default=None], optional
            Effective time of the query. If not specified will default to any time.
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
        List | str

        A list of collection members in the collection.

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

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}/"
               f"members?startFrom={start_from}&pageSize={page_size}")

        resp = await self._async_make_request("GET", url)
        return resp.json().get("elements", "No elements found")

    def get_collection_members(self, collection_guid: str, effective_time: str = None, server_name: str = None,
                               start_from: int = 0, page_size: int = None) -> list | str:
        """ Return a list of elements that are a member of a collection.

            Parameters
            ----------
            collection_guid: str,
                identity of the collection to return members for.
            effective_time: str, [default=None], optional
                Effective time of the query. If not specified will default to any time.
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
            List | str

            A list of collection members in the collection.

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
        resp = loop.run_until_complete(
            self._async_get_collection_members(collection_guid, effective_time, server_name, start_from, page_size))

        return resp

    async def _async_add_to_collection(self, collection_guid: str, element_guid: str, body: dict = None,
                                       server_name: str = None) -> None:
        """ Add an element to a collection.  The request body is optional. Async version.

            Parameters
            ----------
            collection_guid: str
                identity of the collection to return members for.
            element_guid: str
                Effective time of the query. If not specified will default to any time.
            body: dict, optional, defaults to None
                The body of the request to add to the collection. See notes.
            server_name : str, optional
                The name of the server to use.
                If not provided, the server name associated with the instance is used.

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

            Notes
            -----
            Example body:
            {
              "class" : "CollectionMembershipProperties",
              "membershipRationale": "xxx",
              "createdBy": "user id here",
              "expression": "expression that described why the element is a part of this collection",
              "confidence": 100,
              "status": "PROPOSED",
              "userDefinedStatus": "Add valid value here",
              "steward": "identifier of steward that validated this member",
              "stewardTypeName": "type name of element identifying the steward",
              "stewardPropertyName": "property name if the steward's identifier",
              "source": "source of the member",
              "notes": "Add notes here"
            }

        """
        if server_name is None:
            server_name = self.server_name

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}/members/"
               f"{element_guid}/attach")
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        return

    def add_to_collection(self, collection_guid: str, element_guid: str, body: dict = None,
                          server_name: str = None) -> None:
        """ Add an element to a collection.  The request body is optional.

            Parameters
            ----------
            collection_guid: str
                identity of the collection to return members for.
            element_guid: str
                Effective time of the query. If not specified will default to any time.
            body: dict, optional, defaults to None
                The body of the request to add to the collection. See notes.
            server_name : str, optional
                The name of the server to use.
                If not provided, the server name associated with the instance is used.

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

            Notes
            -----
            Example body:
            {
              "class" : "CollectionMembershipProperties",
              "membershipRationale": "xxx",
              "createdBy": "user id here",
              "expression": "expression that described why the element is a part of this collection",
              "confidence": 100,
              "status": "PROPOSED",
              "userDefinedStatus": "Add valid value here",
              "steward": "identifier of steward that validated this member",
              "stewardTypeName": "type name of element identifying the steward",
              "stewardPropertyName": "property name if the steward's identifier",
              "source": "source of the member",
              "notes": "Add notes here"
            }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_to_collection(collection_guid, element_guid, body, server_name))
        return

    async def _async_update_collection_membership(self, collection_guid: str, element_guid: str, body: dict = None,
                                                  replace_all_props: bool = False, server_name: str = None) -> None:
        """ Update an element's membership to a collection. Async version.

            Parameters
            ----------
            collection_guid: str
                identity of the collection to return members for.
            element_guid: str
                Effective time of the query. If not specified will default to any time.
            body: dict, optional, defaults to None
                The body of the request to add to the collection. See notes.
            replace_all_props: bool, optional, defaults to False
                Replace all properties or just update ones specified in body.
            server_name : str, optional
                The name of the server to use.
                If not provided, the server name associated with the instance is used.

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

            Notes
            -----
            Example body:
            {
              "class" : "CollectionMembershipProperties",
              "membershipRationale": "xxx",
              "createdBy": "user id here",
              "expression": "expression that described why the element is a part of this collection",
              "confidence": 100,
              "status": "PROPOSED",
              "userDefinedStatus": "Add valid value here",
              "steward": "identifier of steward that validated this member",
              "stewardTypeName": "type name of element identifying the steward",
              "stewardPropertyName": "property name if the steward's identifier",
              "source": "source of the member",
              "notes": "Add notes here"
            }

        """
        if server_name is None:
            server_name = self.server_name
        replace_all_props_s = str(replace_all_props).lower()
        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}/members/"
               f"{element_guid}/update?replaceAllProperties={replace_all_props_s}")
        body_s = body_slimmer(body)
        await self._async_make_request("POST", url, body_s)
        return

    def update_collection_membership(self, collection_guid: str, element_guid: str, body: dict = None,
                                     replace_all_props: bool = False, server_name: str = None) -> None:
        """ Update an element's membership to a collection.

            Parameters
            ----------
            collection_guid: str
                identity of the collection to update members for.
            element_guid: str
                Effective time of the query. If not specified will default to any time.
            body: dict, optional, defaults to None
                The body of the request to add to the collection. See notes.
            replace_all_props: bool, optional, defaults to False
                Replace all properties or just update ones specified in body.
            server_name : str, optional
                The name of the server to use.
                If not provided, the server name associated with the instance is used.

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

            Notes
            -----
            Example body:
            {
              "class" : "CollectionMembershipProperties",
              "membershipRationale": "xxx",
              "createdBy": "user id here",
              "expression": "expression that described why the element is a part of this collection",
              "confidence": 100,
              "status": "PROPOSED",
              "userDefinedStatus": "Add valid value here",
              "steward": "identifier of steward that validated this member",
              "stewardTypeName": "type name of element identifying the steward",
              "stewardPropertyName": "property name if the steward's identifier",
              "source": "source of the member",
              "notes": "Add notes here"
            }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_collection_membership(collection_guid, element_guid, body, replace_all_props,
                                                     server_name))
        return

    async def _async_remove_from_collection(self, collection_guid: str, element_guid: str,
                                            server_name: str = None) -> None:
        """ Remove an element from a collection. Async version.

            Parameters
            ----------
            collection_guid: str
                identity of the collection to return members for.
            element_guid: str
                Effective time of the query. If not specified will default to any time.
            server_name : str, optional
                The name of the server to use.
                If not provided, the server name associated with the instance is used.

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

        url = (f"{self.platform_url}/servers/{server_name}{self.command_base}/{collection_guid}/members/"
               f"{element_guid}/detach")
        body = {"class": "NullRequestBody"}
        await self._async_make_request("POST", url, body)
        return

    def remove_from_collection(self, collection_guid: str, element_guid: str, server_name: str = None) -> None:
        """ Remove an element from a collection.

            Parameters
            ----------
            collection_guid: str
                identity of the collection to return members for.
            element_guid: str
                Effective time of the query. If not specified will default to any time.
            server_name : str, optional
                The name of the server to use.
                If not provided, the server name associated with the instance is used.

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
        loop.run_until_complete(self._async_remove_from_collection(collection_guid, element_guid, server_name))
        return

    async def _async_get_member_list(self, root_collection_name: str, server_name: str = None) -> list | bool:
        """ Get the member list for the collection - async version.
        Parameters
        ----------
        root_collection_name : str
            The name of the root collection.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        list | bool
            The list of member information if successful, otherwise False.

        Raises
        ------
        InvalidParameterException
            If the root_collection_name does not have exactly one root collection.

        """
        if server_name is None:
            server_name = self.server_name
        # first find the guid for the collection we are using as root
        root_guids = await self._async_get_collections_by_name(root_collection_name)
        if type(root_guids) is str:
            return False
        if len(root_guids) != 1:
            raise InvalidParameterException(
                "root_collection_name must have exactly one root collection for this method")
        root = root_guids[0]['elementHeader']['guid']

        # now find the members of the collection
        member_list = []
        members = await self._async_get_collection_members(root)
        if type(members) is str:
            return False
        # finally, construct a list of  member information
        for member_rel in members:
            member_guid = member_rel['member']['guid']
            member_resp = await self._async_get_collection(member_guid)
            member = member_resp['element']
            # print(json.dumps(member, indent = 4))
            member_instance = {"name": member['properties']['name'],
                               "qualifiedName": member['properties']['qualifiedName'],
                               "guid": member['elementHeader']['guid'],
                               "description": member['properties']['description'],
                               "collectionType": member['properties']['collectionType'], }
            member_list.append(member_instance)

        return member_list

    def get_member_list(self, root_collection_name: str, server_name: str = None) -> list | bool:
        """ Get the member list for the collection.
        Parameters
        ----------
        root_collection_name : str
            The name of the root collection.

        server_name : str, optional
            The name of the server. If not provided, the default server name will be used.

        Returns
        -------
        list | bool
            The list of member information if successful, otherwise False.

        Raises
        ------
        InvalidParameterException
            If the root_collection_name does not have exactly one root collection.

        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_get_member_list(root_collection_name, server_name))
        return resp
