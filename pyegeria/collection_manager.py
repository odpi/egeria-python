"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Maintain and explore the contents of nested collections.

"""

import asyncio
import inspect
from datetime import datetime
from typing import Optional, Annotated, Literal, Union

from loguru import logger
from pydantic import ValidationError, Field, HttpUrl

from pyegeria._exceptions_new import PyegeriaInvalidParameterException
from pyegeria._globals import NO_ELEMENTS_FOUND, NO_GUID_RETURNED, NO_MEMBERS_FOUND
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria.config import settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             ReferenceableProperties, InitialClassifications, TemplateRequestBody,
                             UpdateElementRequestBody, UpdateStatusRequestBody, NewRelationshipRequestBody,
                             DeleteRequestBody, UpdateRelationshipRequestBody, ResultsRequestBody,
                             get_defined_field_values, PyegeriaModel)
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties, populate_columns_from_properties,
                                       get_required_relationships)
from pyegeria.utils import body_slimmer, dynamic_catch


app_settings = settings
EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier

COLLECTION_PROPERTIES_LIST = ["CollectionProperties", "DataDictionaryProperties",
                              "DataSpecProperties", "DigitalProductProperties",
                              "AgreementProperties"]

AGREEMENT_PROPERTIES_LIST = ["AgreementProperties", "DigitalSubscriptionProperties",]


def query_seperator(current_string):
    if current_string == "":
        return "?"
    else:
        return "&"


# ("params are in the form of [(paramName, value), (param2Name, value)] if the value is not None, it will be added to "
# "the query string")


def query_string(params):
    result = ""
    for i in range(len(params)):
        if params[i][1] is not None:
            result = f"{result}{query_seperator(result)}{params[i][0]}={params[i][1]}"
    return result

from pyegeria._client_new import Client2

class CollectionProperties(ReferenceableProperties):
    class_: Annotated[Literal["CollectionProperties"], Field(alias="class")]


class DataSpecProperties(CollectionProperties):
    class_: Annotated[Literal["DataSpecProperties"], Field(alias="class")]


class DataDictionaryProperties(CollectionProperties):
    class_: Annotated[Literal["DataDictionaryProperties"], Field(alias="class")]


class AgreementProperties(CollectionProperties):
    class_: Annotated[Literal["AgreementProperties"], Field(alias="class")]
    identifier: str | None = None
    user_defined_status: str | None = None

class DigitalSubscriptionProperties(AgreementProperties):
    class_: Annotated[Literal["DigitalSubscriptionProperties"], Field(alias="class")]
    support_level: str | None = None
    service_levels: dict | None = None


class DigitalProductProperties(CollectionProperties):
    class_: Annotated[Literal["DigitalProductProperties"], Field(alias="class")]
    user_defined_status: str | None = None
    product_name: str | None = None
    identifier: str | None = None
    introduction_date: datetime | None = None
    maturity: str | None = None
    service_life: str | None = None
    next_version_date: datetime | None = None
    withdrawal_date: datetime | None = None

class Collections(PyegeriaModel):
    collection: Union[CollectionProperties, DigitalSubscriptionProperties, DigitalProductProperties, AgreementProperties,
                      DataSpecProperties, DataDictionaryProperties] = Field(desciminator="class_")


class CollectionManager(Client2):
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
        token: str
            An optional bearer token

    """


    def __init__(self, view_server: str, platform_url: str, user_id: str, user_pwd: str = None, token: str = None, ):
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd


        Client2.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        result = self.get_platform_origin()
        logger.info(f"CollectionManager initialized, platform origin is: {result}")
        self.collection_command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections")
        #
        #       Retrieving Collections - https://egeria-project.org/concepts/collection
        #


    @dynamic_catch
    async def _async_get_attached_collections(self, parent_guid: str, start_from: int = 0, page_size: int = 0,
                                              category: str = None, classification_names: list[str]= None,
                                              body: dict | FilterRequestBody = None, output_format: str = "JSON",
                                              output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections that are linked off of the supplied element using the ResourceList
           relationship. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked collections from.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            If supplied, adds addition request details - for instance, to filter the results on collectionType
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict = None), optional, default = None
            The desired output columns/fields to include.

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

        Notes
        -----
        Sample body:
        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add collectionType value here"
        }

        """

        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/"
               f"metadata-elements/{parent_guid}/collections")
        return await self._async_get_name_request(url, body, output_format, output_format_set)
        response = await self._async_make_request("POST", url, body_slimmer(body))
        elements = response.json().get("elements", NO_ELEMENTS_FOUND)
        if type(elements) is str:
            logger.info(NO_ELEMENTS_FOUND)
            return NO_ELEMENTS_FOUND

        if output_format != 'JSON':  # return a simplified markdown representation
            logger.info(f"Found elements, output format: {output_format}, output_format_set: {output_format_set}")
            return self._generate_collection_output(elements, None, None, output_format,
                                                    output_format_set=output_format_set)
        return elements


    def get_attached_collections(self, parent_guid: str, start_from: int = 0, page_size: int = 0, body: dict = None,
                                 output_format: str = "JSON", output_format_set: str | dict = None) -> list:
        """Returns the list of collections that are linked off of the supplied element using the ResourceList
           relationship. Async version.

        Parameters
        ----------
        parent_guid: str
            The identity of the parent to find linked collections from.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        body: dict, optional, default = None
            If supplied, adds addition request details - for instance, to filter the results on collectionType
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict = None), optional, default = None
                The desired output columns/fields to include.


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

        Notes
        -----
        Sample body:
        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add collectionType value here"
        }

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_attached_collections(parent_guid, start_from, page_size,
                                                 body, output_format, output_format_set))


    @dynamic_catch
    async def _async_find_collections(self, search_string: str = "*", classification_names: list[str] = None,
                                      metadata_element_types: list[str] = None,
                                      starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                      start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                      output_format_set: str | dict = None,
                                      body: dict | SearchStringRequestBody = None) -> list | str:
        """ Returns the list of collections matching the search string filtered by the optional classification.
            This method can either be used with a body, allowing full control, or with the individual parameters.
            If the body is provided it will be used and the search_string will be ignored.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all collections (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_types: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
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
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        output_format_set: str | dict , optional, default = None
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        """
        url = str(HttpUrl(f"{self.collection_command_root}/by-search-string"))
        response = await self._async_find_request(url, _type="Collection",
                                                  _gen_output=self._generate_collection_output,
                                                  search_string = search_string, classification_names = classification_names,
                                                  metadata_element_types = metadata_element_types,
                                                  starts_with = starts_with, ends_with = ends_with, ignore_case = ignore_case,
                                                  start_from = start_from, page_size = page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response

    @dynamic_catch
    def find_collections(self, search_string: str = '*', classification_names: str = None,
                         metadata_element_types: list[str] = None, starts_with: bool = True,
                         ends_with: bool = False, ignore_case: bool = False,
                         start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                         output_format_set: str | dict = None,
                         body: dict | SearchStringRequestBody = None) -> list | str:
        """ Returns the list of collections matching the search string filtered by the optional classification.
            This method can either be used with a body, allowing full control, or with the individual parameters.
            If the body is provided it will be used and the search_string will be ignored.

        Parameters
        ----------
        search_string: str
            Search string to match against - None or '*' indicate match against all collections (may be filtered by
            classification).
        classification_names: list[str], optional, default=None
            A list of classification names to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all classifications are returned.
        metadata_element_types: list[str], optional, default=None
            A list of metadata element types to filter on - for example, ["DataSpec"], for data specifications. If none,
            then all metadata element types are returned.
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
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
        output_format_set: str | dict , optional, default = None
            - The desired output columns/fields to include.
        body: dict | SearchStringRequestBody, optional, default = None
            - if provided, the search parameters in the body will supercede other attributes, such as "search_string"

        Returns
        -------
        List | str

        Output depends on the output format specified.

        Raises
        ------

        ValidationError
          If the client passes incorrect parameters on the request that don't conform to the data model.
        PyegeriaException
          Issues raised in communicating or server side processing.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Args:
            classification_names ():
            metadata_element_types ():

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_find_collections(search_string, classification_names, metadata_element_types,
                                         starts_with, ends_with, ignore_case,
                                         start_from, page_size, output_format,
                                         output_format_set, body))


    @dynamic_catch
    async def _async_get_collections_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None,
                                             start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list | str:
        """ Returns the list of collections with a particular name.

            Parameters
            ----------
            name: str,
                name to use to find matching collections.
            classification_names: list[str], optional, default = None
                type of collection to filter by - e.g., DataDict, Folder, Root
            body: dict, optional, default = None
                Provides, a full request body. If specified, the body supercedes the name parameter.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            output_format_set: dict , optional, default = None
                The desired output columns/fields to include.

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
        url = str(HttpUrl(f"{self.collection_command_root}/by-name"))
        response = await self._async_get_name_request(url, _type="Collection",
                                                  _gen_output=self._generate_collection_output,
                                                  filter_string = filter_string, classification_names = classification_names,
                                                  start_from = start_from, page_size = page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response


    def get_collections_by_name(self, name: str = None, classification_names: list[str] = None,
                                body: dict | FilterRequestBody = None,
                                start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections matching the search string. Async version.
            The search string is located in the request body and is interpreted as a plain string.
            The request parameters, startsWith, endsWith and ignoreCase can be used to allow a fuzzy search.

        Parameters
        ----------
        name: str,
            name to use to find matching collections.
        classification_names: list[str], optional, default = None
            type of collection to filter by - e.g., DataDict, Folder, Root
        body: dict, optional, default = None
            Provides, a full request body. If specified, the body supercedes the name parameter.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict, optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collections match matching the search string. Returns a string if none found.

        Raises
        ------
        PyegeriaException

        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collections_by_name(name, classification_names, body, start_from, page_size,
                                                output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collections_by_category(self, category: str, classification_names: list[str] = None,
                                             body: dict | FilterRequestBody = None, start_from: int = 0, page_size: int = 0,
                                             output_format: str = 'JSON',
                                             output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections with a particular category. This is an optional text field in the
            collection element.

        Parameters
        ----------
        category: str
            category to use to find matching collections.
        classification_names: str, optional
            An optional filter on the search, e.g., DataSpec
        body: dict, optional, default = None
            Provides, a full request body. If specified, the body filter parameter supercedes the collection_type
            parameter.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collections matching the collection type. Returns a string if none found.

        Raises
        ------
        PyegeriaException

        Notes
        -----
        Body sample:

        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add category here"
        }

        """
        url = str(HttpUrl(f"{self.collection_command_root}/by-collection-category"))
        response = await self._async_get_name_request(url, _type="Collection",
                                                  _gen_output=self._generate_collection_output,
                                                  filter_string = category, classification_names = classification_names,
                                                  start_from = start_from, page_size = page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response



    def get_collections_by_category(self, category: str, classification_names: list[str] = None,
                                body: dict | FilterRequestBody = None,
                                start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                output_format_set: str | dict = None) -> list | str:
        """Returns the list of collections with a particular collectionType. This is an optional text field in the
            collection element.

        Parameters
        ----------
        category: str
            category to use to find matching collections.
        classification_names: list[str], optional
            An optional filter on the search, e.g., DataSpec
        body: dict, optional, default = None
            Provides, a full request body. If specified, the body filter parameter supersedes the category
            parameter.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        output_format_set: str | dict, optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collections filtered by the specified category. Output based on specified output format.

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
        Body sample:

        {
          "class": "FilterRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false,
          "limitResultsByStatus": ["ACTIVE"],
          "sequencingOrder": "PROPERTY_ASCENDING",
          "sequencingProperty": "qualifiedName",
          "filter": "Add category here"
        }

        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collections_by_category(category, classification_names, body, start_from, page_size,
                                                output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collection_by_guid(self, collection_guid: str, element_type: str = None,
                                            body: dict | GetRequestBody = None,
                                            output_format: str = 'JSON',
                                            output_format_set: str | dict = None) -> dict | str:
        """Return the properties of a specific collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            unique identifier of the collection.
        element_type: str, default = None, optional
            type of collection - Collection, DataSpec, Agreement, etc.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict, optional, default = None
                The desired output columns/fields to include.

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

        Notes
        ----
        Body sample:
        {
          "class": "GetRequestBody",
          "asOfTime": "{{$isoTimestamp}}",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = str(HttpUrl(f"{self.collection_command_root}/{collection_guid}/retrieve"))
        type = element_type if element_type else "Collection"

        response = await self._async_get_guid_request(url, _type=type,
                                                  _gen_output=self._generate_collection_output,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response




    def get_collection_by_guid(self, collection_guid: str, element_type: str = None, body: dict | GetRequestBody= None,
                               output_format: str = 'JSON', output_format_set: str | dict = None) -> dict | str:
        """ Return the properties of a specific collection. Async version.

            Parameters
            ----------
            collection_guid: str,
                unique identifier of the collection.
            element_type: str, default = None, optional
                type of element - Collection, DataSpec, Agreement, etc.
            body: dict | GetRequestBody, optional, default = None
                full request body.
            output_format: str, default = "JSON"
                - one of "DICT", "MERMAID" or "JSON"
            output_format_set: dict , optional, default = None
                The desired output columns/fields to include.


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

            Notes
            ----
            Body sample:
            {
              "class": "AnyTimeRequestBody",
              "asOfTime": "{{$isoTimestamp}}",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collection_by_guid(collection_guid, element_type, body,
                                               output_format, output_format_set))


    @dynamic_catch
    async def _async_get_collection_members(self, collection_guid: str = None, collection_name: str = None,
                                            collection_qname: str = None, body: dict | ResultsRequestBody = None, start_from: int = 0,
                                            page_size: int = 0, output_format: str = "JSON",
                                            output_format_set: str | dict = None) -> list | str:
        """Return a list of elements that are a member of a collection. Async version.

        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for. If none, collection_name or
            collection_qname are used.
        collection_name: str,
            display the name of the collection to return members for. If none, collection_guid
            or collection_qname are used.
        collection_qname: str,
            qualified name of the collection to return members for. If none, collection_guid
            or collection_name are used.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

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

        Notes:
        -----
        Body sample:
        {
          "class": "ResultsRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "limitResultsByStatus": ["ACTIVE"],
          "asOfTime": "{{$isoTimestamp}}",
          "sequencingOrder": "CREATION_DATE_RECENT",
          "sequencingProperty": ""
        }

        """

        if collection_guid is None:
            collection_guid = self.__get_guid__(collection_guid, collection_name, "displayName",
                                                collection_qname, None, )

        url = str(HttpUrl(f"{self.collection_command_root}/{collection_guid}/members"))


        response = await self._async_get_results_body_request(url, _type="Collection",
                                                  _gen_output=self._generate_collection_output,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response


    def get_collection_members(self, collection_guid: str = None, collection_name: str = None,
                               collection_qname: str = None, body: dict = None, start_from: int = 0,
                               page_size: int = 0,
                               output_format: str = "JSON", output_format_set: str | dict = None) -> list | str:
        """Return a list of elements that are a member of a collection.
        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for. If none, collection_name or
            collection_qname are used.
        collection_name: str,
            display the name of the collection to return members for. If none, collection_guid
            or collection_qname are used.
        collection_qname: str,
            qualified name of the collection to return members for. If none, collection_guid
            or collection_name are used.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
            When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

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

        Notes:
        -----
        Body sample:
        {
          "class": "ResultsRequestBody",
          "effectiveTime": "{{$isoTimestamp}}",
          "limitResultsByStatus": ["ACTIVE"],
          "asOfTime": "{{$isoTimestamp}}",
          "sequencingOrder": "CREATION_DATE_RECENT",
          "sequencingProperty": ""
        }

    """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._async_get_collection_members(collection_guid, collection_name, collection_qname, body, start_from,
                                               page_size, output_format, output_format_set))

        return resp


    @dynamic_catch
    async def _async_get_collection_hierarchy(self, collection_guid: str, body: dict | ResultsRequestBody = None, start_from: int = 0,
                                          page_size: int = 0, output_format: str = "JSON",
                                          output_format_set: str | dict = None) -> list | str:
        """ Return a hierarchy of nested collections. Request body is optional Async version.

            Parameters
            ----------
            collection_guid: str,
                identity of the collection to return members for. If none, collection_name or
                collection_qname are used.
            body: dict | ResultsRequestBody, optional, default = None
                Providing the body allows full control of the request and replaces filter parameters.
            start_from: int, [default=0], optional
                        When multiple pages of results are available, the page number to start from.
            page_size: int, [default=None]
                The number of items to return in a single page. If not specified, the default will be taken from
                the class instance.
            output_format: str, default = "JSON"
                - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
             output_format_set: dict , optional, default = None
                The desired output columns/fields to include.

            Returns
            -------
            List | str

           Results based on the output format.

            Raises
            ------

            InvalidParameterException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            PropertyServerException
              Raised by the server when an issue arises in processing a valid request
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes:
            -----
                Body sample:
            {
              "class": "ResultsRequestBody",
              "startFrom": 0,
              "pageSize": 0,
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }
            """

        url = str(HttpUrl(f"{self.collection_command_root}/{collection_guid}/hierarchy"))
        response = await self._async_get_results_body_request(url, _type="Collection",
                                                              _gen_output=self._generate_collection_output,
                                                              start_from=start_from, page_size=page_size,
                                                              output_format=output_format,
                                                              output_format_set=output_format_set,
                                                              body=body)

        return response

    def get_collection_hierarchy(self, collection_guid: str = None, body: dict| ResultsRequestBody = None, start_from: int = 0,
                             page_size: int = 0, output_format: str = "JSON",
                             output_format_set: str | dict = None) -> list | str:
        """ Return a graph of elements that are the nested members of a collection along
            with elements immediately connected to the starting collection.  The result
            includes a mermaid graph of the returned elements.

        Parameters
        ----------
        collection_guid: str,
            identity of the collection to return members for. If none, collection_name or
            collection_qname are used.
        body: dict, optional, default = None
            Providing the body allows full control of the request and replaces filter parameters.
        start_from: int, [default=0], optional
                    When multiple pages of results are available, the page number to start from.
        page_size: int, [default=None]
            The number of items to return in a single page. If not specified, the default will be taken from
            the class instance.
        output_format: str, default = "JSON"
            - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
         output_format_set: str | dict , optional, default = None
                The desired output columns/fields to include.

        Returns
        -------
        List | str

        A graph anchored in the collection.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
            Body sample:
            {
              "class": "ResultsRequestBody",
              "effectiveTime": "{{$isoTimestamp}}",
              "limitResultsByStatus": ["ACTIVE"],
              "asOfTime": "{{$isoTimestamp}}",
              "sequencingOrder": "CREATION_DATE_RECENT",
              "sequencingProperty": ""
            }
        """
        return asyncio.get_event_loop().run_until_complete(
            self._async_get_collection_hierarchy(collection_guid, body, start_from, page_size,
                                             output_format, output_format_set))


    @dynamic_catch
    async def _async_create_collection(self, display_name: str = None, description: str = None,
                                       category: str = None, initial_classifications: list[str] = None,
                                       body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic collection. If the body is not present, the display_name, description, category
            and classification will be used to create a simple, self-anchored collection.
            Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        display_name: str, optional
            The display name of the collection. The display name will be used to manufacture a qualified name. An
            exception will be raised if a unique qualified name can't be manufactured.
        description: str, optional
            The description of the collection.
        category: str, optional
            An optional user-assigned category for the collection.
        initial_classifications: list[str], optional
            An initial list of classifications for the collection. This can be used to distinguish, for instance, Folders
            from Root Collections.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          }
        }

        anchored:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        a root collection:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "initialClassifications": {
            "RootCollection": {}
          },
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        if body:
            validated_body = self.validate_new_element_request(body,"CollectionProperties")
        elif (body is None) and (display_name is not None):
            pre = initial_classifications[0] if initial_classifications is not None else "Collection"
            qualified_name = self.__create_qualified_name__(pre, display_name, EGERIA_LOCAL_QUALIFIER)
            if initial_classifications:
                initial_classifications_dict = {}
                for c in initial_classifications:
                    initial_classifications_dict = initial_classifications_dict | {c : {"class": f"{c}Properties"}}

            else:
                initial_classifications_dict = None

            collection_properties = CollectionProperties( class_ = "CollectionProperties",
                                                             qualified_name = qualified_name,
                                                             display_name = display_name,
                                                             description = description,
                                                             category = category
                                                             )
            body = {
                "class" :"NewElementRequestBody",
                "isOwnAnchor": True,
                "initialClassifications": initial_classifications_dict,
                "properties": collection_properties.model_dump()
                }
            validated_body = NewElementRequestBody.model_validate(body)
        else:
            raise PyegeriaInvalidParameterException(additional_info={"reason": "Invalid input parameters"})

        url = f"{self.collection_command_root}"
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create collection with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)


    def create_collection(self, display_name: str = None, description: str = None,
                                category: str = None, initial_classifications: list[str] = None,
                                body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic collection. If the body is not present, the display_name, description, category
            and classification will be used to create a simple, self-anchored collection.
            Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        display_name: str, optional
            The display name of the collection. The display name will be used to manufacture a qualified name. An
            exception will be raised if a unique qualified name can't be manufactured.
        description: str, optional
            The description of the collection.
        category: str, optional
            An optional user-assigned category for the collection.
        initial_classifications: str, optional
            An initial classification for the collection. This can be used to distinguish, for instance, Folders
            from Root Collections.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          }
        }

        anchored:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        a root collection:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "initialClassifications": {
            "RootCollection": {}
          },
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


             """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection(display_name, description,category,
                                                 initial_classifications,    body))


    @dynamic_catch
    def create_root_collection(self, display_name: str = None, description: str = None,
                                      category: str = None,  body: dict | NewElementRequestBody = None) -> str:
        """ Create a new collection with the RootCollection classification.  Used to identify the top of a
            collection hierarchy.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

            Parameters
            ----------
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            category: str
                Adds an user supplied valid value for the collection type.
            body: dict | NewElementRequestBody, Optional = None
                The body of the collection request. Supersedes other parameters.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            PyegeriaException
              Error in the request or response
            ValueError
              Pydantic validation error
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection(display_name=display_name, description=description, category=category,
                                         initial_classifications = ["RootCollection"], body=body))


    @dynamic_catch
    def create_folder_collection(self, display_name: str = None, description: str = None,
                                      category: str = None, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new collection with the RootCollection classification.  Used to identify the top of a
            collection hierarchy.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

            Parameters
            ----------
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            category: str
                Adds an user supplied valid value for the collection type.
            body: dict | NewElementRequestBody, Optional = None
                The body of the collection request. Supersedes other parameters.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            PyegeriaException
              Error in the request or response
            ValueError
              Pydantic validation error
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection(display_name, description, category,
                                          ["Folder"], body))



        return resp
    @dynamic_catch
    def create_reference_list_collection(self, display_name: str = None, description: str = None,
                                      category: str = None, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new collection with the RootCollection classification.  Used to identify the top of a
            collection hierarchy.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

            Parameters
            ----------
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            category: str
                Adds an user supplied valid value for the collection type.
            body: dict | NewElementRequestBody, Optional = None
                The body of the collection request. Supersedes other parameters.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            PyegeriaException
              Error in the request or response
            ValueError
              Pydantic validation error
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection(display_name, description, category,
                                          ["ReferenceList"], body))

    @dynamic_catch
    def create_context_event_collection(self, display_name: str = None, description: str = None,
                                      category: str = None, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new collection with the RootCollection classification.  Used to identify the top of a
            collection hierarchy.
            Create Collections: https://egeria-project.org/concepts/collection
            Async version.

            Parameters
            ----------
            display_name: str
                The display name of the element. Will also be used as the basis of the qualified_name.
            description: str
                A description of the collection.
            category: str
                Adds an user supplied valid value for the collection type.
            body: dict | NewElementRequestBody, Optional = None
                The body of the collection request. Supersedes other parameters.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            PyegeriaException
              Error in the request or response
            ValueError
              Pydantic validation error
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_collection(display_name, description, category,
                                          ["ContextEvent"], body))

    # @dynamic_catch
    # def create_glossary(self, display_name: str, description: str = None, language: str = "English", usage: str = None,
    #                     category: str = None, body: dict | NewElementRequestBody = None) -> str:
    #     """Create a new glossary with optional classification. """
    #     if body is None:
    #
    #         qualified_name = self.__create_qualified_name__("Glossary", display_name, EGERIA_LOCAL_QUALIFIER)
    #         body = {
    #             "class": "NewElementRequestBody",
    #             "is_own_anchor": True,
    #             "properties": {
    #                 "class": "GlossaryProperties",
    #                 "displayName": display_name,
    #                 "qualifiedName": qualified_name,
    #                 "description": description,
    #                 "language": language,
    #                 "usage": usage,
    #                 "category": category
    #                 },
    #             }
    #     response = self.create_collection(body=body)
    #     return response

    @dynamic_catch
    async def _async_create_data_spec_collection(self, display_name: str = None, description: str = None,
                                                category: str = None, classification_name: str = None,
                                                 body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic collection. If the body is not present, the display_name, description, category
            and classification will be used to create a simple, self-anchored collection.
            Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        display_name: str, optional
            The display name of the collection. The display name will be used to manufacture a qualified name. An
            exception will be raised if a unique qualified name can't be manufactured.
        description: str, optional
            The description of the collection.
        category: str, optional
            An optional user-assigned category for the collection.
        classification: str, optional
            An initial classification for the collection. This can be used to distinguish, for instance, Folders
            from Root Collections.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          }
        }

        anchored:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        a root collection:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "initialClassifications": {
            "RootCollection": {}
          },
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        if body:
            validated_body = self.validate_new_element_request(body,"DataSpecProperties")
        elif display_name is not None:
            qualified_name = self.__create_qualified_name__("DataSpec", display_name, EGERIA_LOCAL_QUALIFIER)
            logger.info(f"\n\tDisplayName was {display_name}, classification {classification_name}\n")
            if classification_name:
                initial_classification_data = {
                    classification_name: {
                    "class" : "ClassificationProperties"
                    }
                }
            else:
                initial_classification_dict = None
            collection_properties = DataSpecProperties( class_ = "DataSpecProperties",
                                                             qualified_name = qualified_name,
                                                             display_name = display_name,
                                                             description = description,
                                                             category = category
                                                             )
            body = {
                "class" :"NewElementRequestBody",
                "isOwnAnchor": True,
                "initialClassifications": initial_classification_dict,
                "properties": collection_properties.model_dump()
                }
            validated_body = NewElementRequestBody.model_validate(body)
        else:
            raise PyegeriaInvalidParameterException(additional_info={"reason": "Invalid input parameters"})




        url = f"{self.collection_command_root}"
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create collection with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_data_spec_collection(self, display_name: str = None, description: str = None,
                                category: str = None, classification_name: str = None,
                                body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic collection. If the body is not present, the display_name, description, category
            and classification will be used to create a simple, self-anchored collection.
            Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        display_name: str, optional
            The display name of the collection. The display name will be used to manufacture a qualified name. An
            exception will be raised if a unique qualified name can't be manufactured.
        description: str, optional
            The description of the collection.
        category: str, optional
            An optional user-assigned category for the collection.
        classification_name: str, optional
            An initial classification for the collection. This can be used to distinguish, for instance, Folders
            from Root Collections.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          }
        }

        anchored:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        a root collection:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "initialClassifications": {
            "RootCollection": {}
          },
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


             """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_data_spec_collection(display_name, description,category,
                                                 classification_name, body))


    @dynamic_catch
    async def _async_create_data_dictionary_collection(self, display_name: str = None, description: str = None,
                                                category: str = None, classification_name: str = None,
                                                 body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic collection. If the body is not present, the display_name, description, category
            and classification will be used to create a simple, self-anchored collection.
            Collections: https://egeria-project.org/concepts/collection
            Async version.

        Parameters
        ----------
        display_name: str, optional
            The display name of the collection. The display name will be used to manufacture a qualified name. An
            exception will be raised if a unique qualified name can't be manufactured.
        description: str, optional
            The description of the collection.
        category: str, optional
            An optional user-assigned category for the collection.
        classification: str, optional
            An initial classification for the collection. This can be used to distinguish, for instance, Folders
            from Root Collections.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          }
        }

        anchored:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        a root collection:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "initialClassifications": {
            "RootCollection": {}
          },
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        validated_body = self.validate_new_element_request(body,"DataDictionaryProperties")

        if validated_body is None and display_name is not None:
            qualified_name = self.__create_qualified_name__("DataDictionary", display_name, EGERIA_LOCAL_QUALIFIER)
            initial_classifications_data = {"class" : "ClassificationProperties"}
            if classification_name:
                initial_classification_dict = {
                    classification_name: InitialClassifications.model_validate(initial_classifications_data)
                }
            else:
                initial_classification_dict = None
            collection_properties = DataDictionaryProperties( class_ = "DataDictionaryProperties",
                                                             qualified_name = qualified_name,
                                                             display_name = display_name,
                                                             description = description,
                                                             category = category
                                                             )
            body = {
                "class" :"NewElementRequestBody",
                "isOwnAnchor": True,
                "initialClassifications": initial_classification_dict,
                "properties": collection_properties.model_dump()
                }
            validated_body = NewElementRequestBody.model_validate(body)

        if validated_body is None:
            raise PyegeriaInvalidParameterException(additional_info={"reason": "Invalid input parameters"})


        url = f"{self.collection_command_root}"
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create collection with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
    def create_data_dictionary_collection(self, display_name: str = None, description: str = None,
                                category: str = None, classification_name: str = None,
                                body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic collection. If the body is not present, the display_name, description, category
            and classification will be used to create a simple, self-anchored collection.
            Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        display_name: str, optional
            The display name of the collection. The display name will be used to manufacture a qualified name. An
            exception will be raised if a unique qualified name can't be manufactured.
        description: str, optional
            The description of the collection.
        category: str, optional
            An optional user-assigned category for the collection.
        classification: str, optional
            An initial classification for the collection. This can be used to distinguish, for instance, Folders
            from Root Collections.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          }
        }

        anchored:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        a root collection:
        {
          "class": "NewElementRequestBody",
          "anchorGUID": "anchor GUID, if set then isOwnAnchor=false",
          "isOwnAnchor": false,
          "anchorScopeGUID": "optional GUID of search scope",
          "initialClassifications": {
            "RootCollection": {}
          },
          "parentGUID": "parent GUID, if set, set all parameters beginning 'parent'",
          "parentRelationshipTypeName": "open metadata type name",
          "parentAtEnd1": true,
          "properties": {
            "class": "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


             """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_data_dictionary_collection(display_name, description,category,
                                                 classification_name, body))






#######


    @dynamic_catch
    async def _async_create_collection_from_template(self, body: TemplateRequestBody | dict) -> str:
        """Create a new metadata element to represent a collection using an existing metadata element as a template.
        The template defines additional classifications and relationships that are added to the new collection.
        Async version.

        Parameters
        ----------

        body: dict
            A dict representing the details of the collection to create.

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


        if isinstance(body, TemplateRequestBody):
            validated_body = body

        elif isinstance(body, dict):
            validated_body = self._template_request_adapter.validate_python(body)




        url = f"{self.collection_command_root}/from-template"
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create collection from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)


    def create_collection_from_template(self, body: dict) -> str:
        """Create a new metadata element to represent a collection using an existing metadata element as a template.
        The template defines additional classifications and relationships that are added to the new collection.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

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
        resp = loop.run_until_complete(self._async_create_collection_from_template(body))
        return resp

        #
        # Manage collections
        #



    @dynamic_catch
    async def _async_update_collection(self, collection_guid: str,  body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of a collection. Use the correct properties object (CollectionProperties,
            DigitalProductProperties, AgreementProperties, etc), that is appropriate for your element.
            Collections: https://egeria-project.org/concepts/collection

            Async version.
        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.

        body: dict | UpdateElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.
        merge_update: bool, optional, default = True
            If true then property changes will be overlaid on top of existing properties. If false, existing
            properties will all be replaced by the set provided in the update request.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple example:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        # try:

        url = (f"{self.collection_command_root}/{collection_guid}/update")
        await self._async_update_element_body_request(url, COLLECTION_PROPERTIES_LIST,body)






    @dynamic_catch
    def update_collection(self, collection_guid: str,  body: dict | NewElementRequestBody) -> None:
        """ Update the properties of a collection. Use the correct properties object (CollectionProperties,
            DigitalProductProperties, AgreementProperties, etc), that is appropriate for your element.
            Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.
        merge_update: bool, optional, default = True
            If true then property changes will be overlaid on top of existing properties. If false, existing
            properties will all be replaced by the set provided in the update request.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple example:
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "CollectionProperties",
            "qualifiedName": "Must provide a unique name here",
            "name" : "Add display name here",
            "description" : "Add description of the collection here",
            "category": "Add appropriate valid value for type"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_collection(collection_guid, body))


    @dynamic_catch
    async def _async_create_digital_product(self, body: dict | NewElementRequestBody) -> str:
        """ Create a new collection that represents a digital product.
            Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A structure representing the details of the digital product to create.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        ValidationError
          Raised by the pydantic validator if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct::Add product name here",
            "name" : "Product contents",
            "description" : "Add description of product and its expected usage here",
            "identifier" : "Add product identifier here",
            "productName" : "Add product name here",
            "category" : "Periodic Delta",
            "maturity" : "Add valid value here",
            "serviceLife" : "Add the estimated lifetime of the product",
            "introductionDate" : "date",
            "nextVersionDate": "date",
            "withdrawDate": "date",
            "currentVersion": "V0.1",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "initialStatus" : "ACTIVE"
        }

        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
        UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
        OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
        default to ACTIVE.
        """
        url = f"{self.collection_command_root}"
        return await self._async_create_element_body_request(url, "DigitalProductProperties", body)


    @dynamic_catch
    def create_digital_product(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new collection that represents a digital product.

            Parameters
            ----------
            body: dict | NewElementRequestBody
                A structure representing the details of the digital product to create.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            PyegeriaException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            ValidationError
              Raised by the pydantic validator if the body does not conform to the NewElementRequestBody.
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
            be valid dates if specified, otherwise you will get a 400 error response.

            JSON Structure looks like:
            {
              "class" : "NewElementRequestBody",
              "isOwnAnchor" : true,
              "anchorScopeGUID" : "optional GUID of search scope",
              "parentGUID" : "xxx",
              "parentRelationshipTypeName" : "CollectionMembership",
              "parentAtEnd1": true,
              "properties": {
                "class" : "DigitalProductProperties",
                "qualifiedName": "DigitalProduct::Add product name here",
                "name" : "Product contents",
                "description" : "Add description of product and its expected usage here",
                "identifier" : "Add product identifier here",
                "productName" : "Add product name here",
                "category" : "Periodic Delta",
                "maturity" : "Add valid value here",
                "serviceLife" : "Add the estimated lifetime of the product",
                "introductionDate" : "date",
                "nextVersionDate": "date",
                "withdrawDate": "date",
                "currentVersion": "V0.1",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "initialStatus" : "ACTIVE"
            }

            The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
            UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
            OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
            default to ACTIVE.
            """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_digital_product(body))


    @dynamic_catch
    async def _async_update_digital_product(self, collection_guid: str,  body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of a digital product.
            Collections: https://egeria-project.org/concepts/collection

            Async version.
        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.
        merge_update: bool, optional, default = True
            If true then property changes will be overlaid on top of existing properties. If false, existing
            properties will all be replaced by the set provided in the update request.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct::Add product name here",
            "name" : "Product contents",
            "description" : "Add description of product and its expected usage here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add product identifier here",
            "productName" : "Add product name here",
            "category" : "Periodic Delta",
            "maturity" : "Add valid value here",
            "serviceLife" : "Add the estimated lifetime of the product",
            "introductionDate" : "date",
            "nextVersionDate": "date",
            "withdrawDate": "date",
            "currentVersion": "V0.1",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        url = (f"{self.collection_command_root}/{collection_guid}/update")
        await self._async_update_element_body_request(url, "DigitalProductProperties", body )


    @dynamic_catch
    def update_digital_product(self, collection_guid: str,  body: dict | UpdateElementRequestBody,) -> None:
        """ Update the properties of a digital product..
            Collections: https://egeria-project.org/concepts/collection

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the collection to create. If supplied, this
            information will be used to create the collection and the other attributes will be ignored. The body is
            validated before being used.
        merge_update: bool, optional, default = True
            If true then property changes will be overlaid on top of existing properties. If false, existing
            properties will all be replaced by the set provided in the update request.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "DigitalProductProperties",
            "qualifiedName": "DigitalProduct::Add product name here",
            "name" : "Product contents",
            "description" : "Add description of product and its expected usage here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add product identifier here",
            "productName" : "Add product name here",
            "category" : "Periodic Delta",
            "maturity" : "Add valid value here",
            "serviceLife" : "Add the estimated lifetime of the product",
            "introductionDate" : "date",
            "nextVersionDate": "date",
            "withdrawDate": "date",
            "currentVersion": "V0.1",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_digital_product(collection_guid, body))


    @dynamic_catch
    async def _async_update_collection_status(self, collection_guid: str, status: str = None,
                                              body: dict | UpdateStatusRequestBody = None):
        """Update the status of a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        status: str, optional
            The new lifecycle status for the collection. Ignored, if the body is provided.
        body: dict | UpdateStatusRequestBody, optional
            A structure representing the details of the collection to create. If supplied, these details
            supersede the status parameter provided.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """

        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/metadata-elements/{collection_guid}/update-status"
        await self._async_update_status_request(url, status, body)

    @dynamic_catch
    def update_collection_status(self, collection_guid: str, status: str = None,
                                 body: dict | UpdateStatusRequestBody = None):
        """Update the status of a DigitalProduct collection.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to update.
        status: str, optional
            The new lifecycle status for the digital product. Ignored, if the body is provided.
        body: dict | UpdateStatusRequestBody, optional
            A structure representing the details of the collection to create. If supplied, these details
            supersede the status parameter provided.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_collection_status(collection_guid, status, body))


    @dynamic_catch
    def update_digital_product_status(self, digital_product_guid: str, status: str = None,
                                      body: dict | UpdateStatusRequestBody = None):
        """Update the status of a DigitalProduct collection.

        Parameters
        ----------
        digital_product_guid: str
            The guid of the collection to update.
        status: str, optional
            The new lifecycle status for the digital product. Ignored, if the body is provided.
        body: dict | UpdateStatusRequestBody, optional
            A structure representing the details of the collection to create. If supplied, these details
            supersede the status parameter provided.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_collection_status(digital_product_guid, status, body))


    @dynamic_catch
    async def _async_link_digital_product_dependency(self, upstream_digital_prod_guid: str,
                                                     downstream_digital_prod_guid: str,
                                                     body: dict | NewRelationshipRequestBody = None):
        """ Link two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional. Async version.

        Parameters
        ----------
        upstream_digital_prod_guid: str
            The guid of the first digital product
        downstream_digital_prod_guid: str
            The guid of the downstream digital product
        body: dict | NewRelationshipRequestBody, optional, default = None
            A dict representing the details of the relationship.

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
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "InformationSupplyChainLinkProperties",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital-products/"
            f"{upstream_digital_prod_guid}/product-dependencies/{downstream_digital_prod_guid}/attach")
        await self._async_new_relationship_request(url, "InformationSupplyChainLinkProperties", body)
        logger.info(f"Linked {upstream_digital_prod_guid} -> {downstream_digital_prod_guid}")


    def link_digital_product_dependency(self, upstream_digital_prod_guid: str, downstream_digital_prod_guid: str,
                                        body: dict | NewRelationshipRequestBody= None):
        """ Link two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional.

            Parameters
            ----------
            upstream_digital_prod_guid: str
                The guid of the first digital product
            downstream_digital_prod_guid: str
                The guid of the downstream digital product
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

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
            JSON Structure looks like:
            {
              "class" : "NewRelationshipRequestBody",
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "properties": {
                "class": "InformationSupplyChainLinkProperties",
                "label": "add label here",
                "description": "add description here",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_digital_product_dependency(upstream_digital_prod_guid, downstream_digital_prod_guid,
                                                        body))


    @dynamic_catch
    async def _async_detach_digital_product_dependency(self, upstream_digital_prod_guid: str,
                                                       downstream_digital_prod_guid: str,
                                                       body: dict | DeleteRequestBody = None)-> None:
        """ Unlink two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional. Async version.

        Parameters
        ----------
        upstream_digital_prod_guid: str
            The guid of the first digital product
        downstream_digital_prod_guid: str
            The guid of the downstream digital product
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital-products/"
            f"{upstream_digital_prod_guid}/product-dependencies/{downstream_digital_prod_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached digital product dependency {upstream_digital_prod_guid} -> {downstream_digital_prod_guid}")


    def detach_digital_product_dependency(self, upstream_digital_prod_guid: str, downstream_digital_prod_guid: str,
                                        body: dict | DeleteRequestBody= None):
        """ Unlink two dependent digital products.  The linked elements are of type DigitalProduct.
            Request body is optional.

        Parameters
        ----------
        upstream_digital_prod_guid: str
            The guid of the first digital product
        downstream_digital_prod_guid: str
            The guid of the downstream digital product
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_digital_product_dependency(upstream_digital_prod_guid, downstream_digital_prod_guid,
                                                        body))





    @dynamic_catch
    async def _async_link_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str,
                                          body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach a product manager to a digital product. Request body is optional.
            Request body is optional. Async version.

        Parameters
        ----------
        digital_prod_guid: str
            The guid of the digital product
        digital_prod_manager_guid: str
            The guid of the digital_product_manager
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "NewRelationshipRequestBody",
          "properties": {
              "assignmentType": "Add type here",
              "description": "Add assignment description here"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital"
            f"-products/"
            f"{digital_prod_guid}/product-managers/{digital_prod_manager_guid}/attach")
        await self._async_new_relationship_request(url, "AssignmentScopeProperties",body)
        logger.info(f"Attached digital product manager {digital_prod_guid} -> {digital_prod_manager_guid}")


    def link_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str, body: dict | NewRelationshipRequestBody = None):
        """ Attach a product manager to a digital product. Request body is optional.
                Request body is optional.

            Parameters
            ----------
            digital_prod_guid: str
                The guid of the digital product
            digital_prod_manager_guid: str
                The guid of the digital_product_manager
            body: dict | NewRelationshipRequestBody, optional, default = None
                A structure representing the details of the relationship.

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
              "class": "NewRelationshipRequestBody",
              "properties": {
                  "assignmentType": "Add type here",
                  "description": "Add assignment description here"
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime": "{{$isoTimestamp}}",
              "forLineage": false,
              "forDuplicateProcessing": false
            }

            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_product_manager(digital_prod_guid, digital_prod_manager_guid, body))


    @dynamic_catch
    async def _async_detach_product_manager(self, digital_prod_guid: str,
                                             digital_prod_manager_guid: str,
                                             body: dict | DeleteRequestBody = None)-> None:
        """ Detach a digital product manager from a digital product.
            Request body is optional. Async version.

        Parameters
        ----------
        digital_prod_guid: str
            The guid of the digital product.
        prod_manager: str
            The guid of the digital product manager.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/digital-products/"
            f"{digital_prod_guid}/product-dependencies/{digital_prod_manager_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached digital product manager {digital_prod_guid} -> {digital_prod_manager_guid}")

    @dynamic_catch
    def detach_product_manager(self, digital_prod_guid: str, digital_prod_manager_guid: str,
                                body: dict | DeleteRequestBody= None):
        """ Detach a digital product manager from a digital product.
            Request body is optional. Async version.

        Parameters
        ----------
        digital_prod_guid: str
            The guid of the digital product.
        digital_prod_manager_guid: str
            The guid of the digital product manager.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_product_manager(digital_prod_guid, digital_prod_manager_guid,
                                                        body))


#

    @dynamic_catch
    async def _async_create_agreement(self, body: dict | NewElementRequestBody) -> str:
        """ Create a new collection that represents an agreement.
            Async version.

        Parameters
        ----------
        body: dict | NewElementRequestBody
            A structure representing the details of the agreement to create.

        Returns
        -------
        str - the guid of the created collection

        Raises
        ------
        PyegeriaException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        ValidationError
          Raised by the pydantic validator if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes
        -----
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "initialStatus" : "ACTIVE"
        }

        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
        UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
        OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
        default to ACTIVE.
        """
        url = f"{self.collection_command_root}"
        return await self._async_create_element_body_request(url, "AgreementProperties", body)

    @dynamic_catch
    def create_agreement(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new collection that represents an agreement..

            Parameters
            ----------
            body: dict | NewElementRequestBody
                A structure representing the details of the agreement to create.

            Returns
            -------
            str - the guid of the created collection

            Raises
            ------
            PyegeriaException
              If the client passes incorrect parameters on the request - such as bad URLs or invalid values
            ValidationError
              Raised by the pydantic validator if the body does not conform to the NewElementRequestBody.
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes
            -----
            Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
            be valid dates if specified, otherwise you will get a 400 error response.

            JSON Structure looks like:
            {
              "class" : "NewElementRequestBody",
              "isOwnAnchor" : true,
              "anchorScopeGUID" : "optional GUID of search scope",
              "parentGUID" : "xxx",
              "parentRelationshipTypeName" : "CollectionMembership",
              "parentAtEnd1": true,
              "properties": {
                "class" : "AgreementProperties",
                "qualifiedName": "Agreement::Add agreement name here",
                "name" : "display name",
                "description" : "Add description of the agreement here",
                "identifier" : "Add agreement identifier here",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false,
              "initialStatus" : "ACTIVE"
            }

            The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
            UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
            OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
            default to ACTIVE.
            """

        return asyncio.get_event_loop().run_until_complete(
            self._async_create_agreement(body))

    #
    # @dynamic_catch
    # async def _async_create_data_sharing_agreement(self, body: dict | NewElementRequestBody) -> str:
    #     """ Create a new collection that represents a data sharing agreement.
    #         Async version.
    #
    #     Parameters
    #     ----------
    #     body: dict | NewElementRequestBody
    #         A structure representing the details of the data sharing agreement to create.
    #
    #     Returns
    #     -------
    #     str - the guid of the created collection
    #
    #     Raises
    #     ------
    #     PyegeriaException
    #       If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #     ValidationError
    #       Raised by the pydantic validator if the body does not conform to the NewElementRequestBody.
    #     NotAuthorizedException
    #       The principle specified by the user_id does not have authorization for the requested action
    #
    #     Notes
    #     -----
    #     Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
    #     be valid dates if specified, otherwise you will get a 400 error response.
    #
    #     JSON Structure looks like:
    #     {
    #       "class" : "NewElementRequestBody",
    #       "isOwnAnchor" : true,
    #       "anchorScopeGUID" : "optional GUID of search scope",
    #       "parentGUID" : "xxx",
    #       "parentRelationshipTypeName" : "CollectionMembership",
    #       "parentAtEnd1": true,
    #       "properties": {
    #         "class" : "AgreementProperties",
    #         "qualifiedName": "Agreement::Add agreement name here",
    #         "name" : "display name",
    #         "description" : "Add description of the agreement here",
    #         "userDefinedStatus" : "NEW",
    #         "identifier" : "Add agreement identifier here",
    #         "additionalProperties": {
    #           "property1Name" : "property1Value",
    #           "property2Name" : "property2Value"
    #         }
    #       },
    #       "initialStatus" : "ACTIVE",
    #       "externalSourceGUID": "add guid here",
    #       "externalSourceName": "add qualified name here",
    #       "effectiveTime" : "{{$isoTimestamp}}",
    #       "forLineage" : false,
    #       "forDuplicateProcessing" : false
    #     }
    #
    #     The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
    #     UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
    #     OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
    #     default to ACTIVE.
    #     """
    #
    #     url = f"{self.collection_command_root}/data-sharing-agreement"
    #     return await self._async_create_element_body_request(url, "AgreementProperties", body)
    #
    # @dynamic_catch
    # def create_data_sharing_agreement(self, body: dict | NewElementRequestBody = None) -> str:
    #     """ Create a new collection that represents a digital product.
    #
    #         Parameters
    #         ----------
    #         body: dict | NewElementRequestBody
    #             A structure representing the details of the digital product to create.
    #
    #         Returns
    #         -------
    #         str - the guid of the created collection
    #
    #         Raises
    #         ------
    #         PyegeriaException
    #           If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    #         ValidationError
    #           Raised by the pydantic validator if the body does not conform to the NewElementRequestBody.
    #         NotAuthorizedException
    #           The principle specified by the user_id does not have authorization for the requested action
    #
    #         Notes
    #         -----
    #         Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
    #         be valid dates if specified, otherwise you will get a 400 error response.
    #
    #         JSON Structure looks like:
    #         {
    #           "class" : "NewElementRequestBody",
    #           "isOwnAnchor" : true,
    #           "anchorScopeGUID" : "optional GUID of search scope",
    #           "parentGUID" : "xxx",
    #           "parentRelationshipTypeName" : "CollectionMembership",
    #           "parentAtEnd1": true,
    #           "properties": {
    #             "class" : "DigitalProductProperties",
    #             "qualifiedName": "DigitalProduct::Add product name here",
    #             "name" : "Product contents",
    #             "description" : "Add description of product and its expected usage here",
    #             "identifier" : "Add product identifier here",
    #             "productName" : "Add product name here",
    #             "category" : "Periodic Delta",
    #             "maturity" : "Add valid value here",
    #             "serviceLife" : "Add the estimated lifetime of the product",
    #             "introductionDate" : "date",
    #             "nextVersionDate": "date",
    #             "withdrawDate": "date",
    #             "currentVersion": "V0.1",
    #             "additionalProperties": {
    #               "property1Name" : "property1Value",
    #               "property2Name" : "property2Value"
    #             }
    #           },
    #           "externalSourceGUID": "add guid here",
    #           "externalSourceName": "add qualified name here",
    #           "effectiveTime" : "{{$isoTimestamp}}",
    #           "forLineage" : false,
    #           "forDuplicateProcessing" : false,
    #           "initialStatus" : "ACTIVE"
    #         }
    #
    #         The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED, APPROVED_CONCEPT,
    #         UNDER_DEVELOPMENT, DEVELOPMENT_COMPLETE, APPROVED_FOR_DEPLOYMENT, ACTIVE, DISABLED, DEPRECATED,
    #         OTHER.  If using OTHER, set the userDefinedStatus with the status value you want. If not specified, will
    #         default to ACTIVE.
    #         """
    #
    #     return asyncio.get_event_loop().run_until_complete(
    #         self._async_create_data_sharing_agreement(body))
    #

    @dynamic_catch
    async def _async_update_agreement(self, agreement_guid: str,  body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an agreement.
            Collections: https://egeria-project.org/concepts/collection

            Async version.
        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the agreement to create.
        merge_update: bool, optional, default = True
            If true then property changes will be overlaid on top of existing properties. If false, existing
            properties will all be replaced by the set provided in the update request.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        {
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add agreement name here",
            "name" : "display name",
            "description" : "Add description of the agreement here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add agreement identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = (f"{self.collection_command_root}/{agreement_guid}/update")
        await self._async_update_element_body_request(url, AGREEMENT_PROPERTIES_LIST,body)

    @dynamic_catch
    def update_agreement(self, agreement_guid: str,  body: dict | UpdateElementRequestBody) -> None:
        """ Update the properties of an agreement.
                Collections: https://egeria-project.org/concepts/collection

            Parameters
            ----------
            agreement_guid: str
                The guid of the agreement to update.

            body: dict | NewElementRequestBody, optional
                A dict or NewElementRequestBody representing the details of the agreement to create.
            merge_update: bool, optional, default = True
                If true then property changes will be overlaid on top of existing properties. If false, existing
                properties will all be replaced by the set provided in the update request.

            Returns
            -------
            None

            Raises
            ------
            PyegeriaException
                One of the pyegeria exceptions will be raised if there are issues in communications, message format or
                Egeria errors.
            ValidationError
                Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
            NotAuthorizedException
              The principle specified by the user_id does not have authorization for the requested action

            Notes:
            -----
            {
              "class" : "UpdateElementRequestBody",
              "properties": {
                "class" : "AgreementProperties",
                "qualifiedName": "Agreement::Add agreement name here",
                "name" : "display name",
                "description" : "Add description of the agreement here",
                "userDefinedStatus" : "OBSOLETE",
                "identifier" : "Add agreement identifier here",
                "additionalProperties": {
                  "property1Name" : "property1Value",
                  "property2Name" : "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
            """

        return asyncio.get_event_loop().run_until_complete(
            self._async_update_agreement(agreement_guid, body))



    @dynamic_catch
    def update_agreement_status(self, agreement_guid: str, status: str = None,
                                body: dict | UpdateStatusRequestBody = None):
        """Update the status of an agreement.
        Parameters
        ----------
        agreement_guid: str
            The guid of the collection to update.
        status: str, optional
            The new lifecycle status for the collection. Ignored, if the body is provided.
        body: dict | UpdateStatusRequestBody
            A structure representing the details of the collection to create.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_collection_status(agreement_guid, status,body))



    @dynamic_catch
    async def _async_link_agreement_actor(self, agreement_guid: str, actor_guid: str,
                                          body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach an actor to an agreement.  The actor element may be an actor profile (person, team or IT profile);
            actor role (person role, team role or IT profile role); or user identity. Request body is optional.
            Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement
        actor_guid: str
            The guid of the actor
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "NewRelationshipRequestBody",
          "properties": {
         "properties": {
            "class": "AgreementActorProperties",
            "actorName": "add name of actor used in agreement text",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/agreements/"
            f"{agreement_guid}/agreement-actors/{actor_guid}/attach")
        await self._async_new_relationship_request(url, "AgreementActorProperties",body)
        logger.info(f"Attached digital product manager {agreement_guid} -> {actor_guid}")


    def link_agreement_actor(self, agreement_guid: str, actor_guid: str, body: dict | NewRelationshipRequestBody = None):
        """ Attach an actor to an agreement.  The actor element may be an actor profile (person, team or IT profile);
            actor role (person role, team role or IT profile role); or user identity. Request body is optional.
            Async version.

          Parameters
          ----------
          agreement_guid: str
              The guid of the agreement
          actor_guid: str
              The guid of the actor
          body: dict | NewRelationshipRequestBody, optional, default = None
              A structure representing the details of the relationship.

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
            "class": "NewRelationshipRequestBody",
            "properties": {
           "properties": {
              "class": "AgreementActorProperties",
              "actorName": "add name of actor used in agreement text",
              "effectiveFrom": "{{$isoTimestamp}}",
              "effectiveTo": "{{$isoTimestamp}}"
            },
            "externalSourceGUID": "add guid here",
            "externalSourceName": "add qualified name here",
            "effectiveTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false
          }

          """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_agreement_actor(agreement_guid, actor_guid, body))


    @dynamic_catch
    async def _async_detach_agreement_actor(self, agreement_guid: str,
                                             actor_guid: str,
                                             body: dict | DeleteRequestBody = None)-> None:
        """ Detach an actor from an agreement.
            Request body is optional. Async Version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement.
        actor_guid: str
            The guid of the actor.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/collections/agreements/"
            f"{agreement_guid}/agreement-actors/{actor_guid}/detach")
        self._async_delete_request(url, body)
        logger.info(f"Detached digital product manager {agreement_guid} -> {actor_guid}")


    def detach_agreement_actor(self, agreement_guid: str, actor_guid: str,
                                body: dict | DeleteRequestBody= None):
        """ Detach an actor from an agreement.
            Request body is optional.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement.
        actor_guid: str
            The guid of the actor.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_agreement_actor(agreement_guid, actor_guid,
                                                        body))



###

    @dynamic_catch
    async def _async_link_agreement_item(self, agreement_guid: str, agreement_item_guid: str,
                                         body: dict| NewRelationshipRequestBody = None) -> None:
        """ Attach an agreement to an element referenced in its definition. The agreement item element is of type
           'Referenceable' to allow the agreement to refer to many things. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        agreement_item_guid: str
            The guid of the element to attach.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A dict representing the details of the relationship.

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
        _____
        {
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "AgreementItemProperties",
            "agreementItemId": "add label here",
            "agreementStart": "{{$isoTimestamp}}",
            "agreementEnd": "{{$isoTimestamp}}",
            "restrictions": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "obligations" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "entitlements" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "usageMeasurements" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

            """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"agreements/{agreement_guid}/agreement-items/{agreement_item_guid}/attach")

        await self._async_new_relationship_request(url, "AgreementItemProperties", body)
        logger.info(f"Attached agreement item {agreement_item_guid} to {agreement_guid}")


    def link_agreement_item(self, agreement_guid: str, agreement_item_guid: str, body: dict = None) -> None:
        """ Attach an agreement to an element referenced in its definition. The agreement item element is of type
                  'Referenceable' to allow the agreement to refer to many things. Request body is optional.

               Parameters
               ----------
               agreement_guid: str
                   The guid of the agreement to update.
               agreement_item_guid: str
                   The guid of the element to attach.
               body: dict, optional, default = None
                   A dict representing the details of the relationship.

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
               _____

               {
                 "class" : "RelationshipRequestBody",
                 "externalSourceGUID": "add guid here",
                 "externalSourceName": "add qualified name here",
                 "effectiveTime" : "{{$isoTimestamp}}",
                 "forLineage" : false,
                 "forDuplicateProcessing" : false,
                 "properties": {
                   "class": "AgreementItemProperties",
                   "agreementItemId": "add label here",
                   "agreementStart": "{{$isoTimestamp}}",
                   "agreementEnd": "{{$isoTimestamp}}",
                   "restrictions": {
                     "property1Name" : "property1Value",
                     "property2Name" : "property2Value"
                   },
                   "obligations" : {
                     "property1Name" : "property1Value",
                     "property2Name" : "property2Value"
                   },
                   "usageMeasurements" : {
                     "property1Name" : "property1Value",
                     "property2Name" : "property2Value"
                   },
                   "effectiveFrom": "{{$isoTimestamp}}",
                   "effectiveTo": "{{$isoTimestamp}}"
                 }
               }

               """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_agreement_item(agreement_guid, agreement_item_guid, body))


    @dynamic_catch
    async def _async_detach_agreement_item(self, agreement_guid: str, agreement_item_guid: str,
                                           body: dict | DeleteRequestBody = None) -> None:
        """Detach an agreement item from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        agreement_item_guid: str
            The guid of the element to attach.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
        _____
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements"
            f"{agreement_guid}/agreement-items/{agreement_item_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached agreement item {agreement_item_guid} from {agreement_guid}")


    def detach_agreement_item(self, agreement_guid: str, agreement_item_guid: str, body: dict = None) -> None:
        """Detach an agreement item from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        agreement_item_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

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
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_agreement_item(agreement_guid, agreement_item_guid, body))


    @dynamic_catch
    async def _async_link_contract(self, agreement_guid: str, external_ref_guid: str, 
                                   body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach an agreement to an external reference element that describes the location of the contract
        documents.
            Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        external_ref_guid: str
            The guid of the external reference to attach.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
        _____

        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ContractLinkProperties",
            "contractId": "add id here",
            "contractLiaison": "add identifier of actor here",
            "contractLiaisonTypeName": "add type of actor here",
            "contractLiaisonPropertyName": "add property of actor's identifier here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"agreements/{agreement_guid}/contract-links/{external_ref_guid}/attach")
        await self._async_new_relationship_request(url, "ContractLinkProperties", body)
        logger.info(f"Attached agreement {agreement_guid} to contract {external_ref_guid}")

    @dynamic_catch
    def link_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """ Attach an agreement to an external reference element that describes the location of the contract
        documents.
            Request body is optional.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to update.
        external_ref_guid: str
            The guid of the external reference to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

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
        _____

        {
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "ContractLinkProperties",
            "contractId": "add id here",
            "contractLiaison": "add identifier of actor here",
            "contractLiaisonTypeName": "add type of actor here",
            "contractLiaisonPropertyName": "add property of actor's identifier here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_contract(agreement_guid, external_ref_guid, body))


    @dynamic_catch
    async def _async_detach_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """Detach an external reference to a contract, from an agreement. Request body is optional. Async version.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        external_ref_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

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
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/{agreement_guid}/contract-links/{external_ref_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached contract: {external_ref_guid} from {agreement_guid}")

    @dynamic_catch
    def detach_contract(self, agreement_guid: str, external_ref_guid: str, body: dict = None) -> None:
        """Detach an external reference to a contract, from an agreement. Request body is optional.

        Parameters
        ----------
        agreement_guid: str
            The guid of the agreement to link.
        external_ref_guid: str
            The guid of the element to attach.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

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
        _____
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_contract(agreement_guid, external_ref_guid, body))

        #
        # Digital Subscriptions
        #


    @dynamic_catch
    async def _async_create_digital_subscription(self, body: dict | NewElementRequestBody) -> str:
        """Create a new collection that represents a type of agreement called a digital_subscription. Async version.

        Parameters
        ----------
        body | NewElementRequewstBody: dict
            A structure representing the details of the collection to create.

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        {
          "class" : "NewElementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
             }
           },
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime" : "{{$isoTimestamp}}",
           "forLineage" : false,
           "forDuplicateProcessing" : false
        }

        With a lifecycle, the body is:

        The DigitalSubscription is a type of Agreement and so can have lifecycle states.
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must be valid dates if specified,
        otherwise you will get a 400 error response.
        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED
        ACTIVE, DEPRECATED, OTHER.  If using OTHER, set the userDefinedStatus with the statu value you want.

        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
             }
           },
           "initialStatus" : "OTHER",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime" : "{{$isoTimestamp}}",
           "forLineage" : false,
           "forDuplicateProcessing" : false
        }
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
        return await self._async_create_element_body_request(url, "DigitalSubscriptionProperties", body)


    def create_digital_subscription(self, body: dict) -> str:
        """Create a new collection that represents a type of agreement called a digital_subscription.

        Parameters
        ----------
        body: dict
            A dict representing the details of the collection to create.

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
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must
        be valid dates if specified, otherwise you will get a 400 error response.

        JSON Structure looks like:
        With a lifecycle, the body is:

        The DigitalSubscription is a type of Agreement and so can have lifecycle states.
        Note: the three dates: introductionDate, nextVersionDate and withdrawDate must be valid dates if specified,
        otherwise you will get a 400 error response.
        The valid values for initialStatus are: DRAFT, PREPARED, PROPOSED, APPROVED, REJECTED
        ACTIVE, DEPRECATED, OTHER.  If using OTHER, set the userDefinedStatus with the statu value you want.

        {
          "class" : "NewAgreementRequestBody",
          "isOwnAnchor" : true,
          "anchorScopeGUID" : "optional GUID of search scope",
          "parentGUID" : "xxx",
          "parentRelationshipTypeName" : "CollectionMembership",
          "parentAtEnd1": true,
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
             }
           },
           "initialStatus" : "OTHER",
           "externalSourceGUID": "add guid here",
           "externalSourceName": "add qualified name here",
           "effectiveTime" : "{{$isoTimestamp}}",
           "forLineage" : false,
           "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(self._async_create_digital_subscription(body))
        return resp


    @dynamic_catch
    async def _async_update_digital_subscription(self, digital_subscription_guid: str,
                                                 body: dict | UpdateElementRequestBody) -> None:
        """Update the properties of the digital_subscription collection. Async version.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital_subscription to update.
        body: dict | UpdateElementRequestBody
            A structure representing the details of the collection to create.

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
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "DigitalSubscriptionProperties",
            "qualifiedName": "DigitalSubscription::Add subscription name here",
            "name" : "display name",
            "description" : "Add description of the subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add subscription identifier here",
            "supportLevel" : "Add the level of support agreed/requested",
            "serviceLevels" : {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            },
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = (f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections/"
               f"{digital_subscription_guid}/update")
        await self._async_update_element_body_request(url,["DigitalSubscriptionProperties"], body )
        logger.info(f"Updated digital subscription {digital_subscription_guid}")

    @dynamic_catch
    def update_digital_subscription(self, digital_subscription_guid: str, body: dict,):
        """Update the properties of the DigitalProduct classification attached to a collection.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital_subscription to update.
        body: dict
            A dict representing the details of the collection to create.
        replace_all_props: bool, optional, defaults to False
            Whether to replace all properties in the collection.


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
          "class" : "UpdateElementRequestBody",
          "properties": {
            "class" : "AgreementProperties",
            "qualifiedName": "Agreement::Add digital_subscription name here",
            "name" : "display name",
            "description" : "Add description of the digital_subscription here",
            "userDefinedStatus" : "OBSOLETE",
            "identifier" : "Add digital_subscription identifier here",
            "additionalProperties": {
              "property1Name" : "property1Value",
              "property2Name" : "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_digital_subscription(digital_subscription_guid, body))


    @dynamic_catch
    async def _async_update_digital_subscription_status(self, digital_subscription_guid: str, status: str = None,
                                                        body: dict | UpdateStatusRequestBody = None)-> None:
        """Update the status of a digital_subscription collection. Async version.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital product collection to update.
        status: str, optional
            The new status of the digital_subscription collection. Will be used only if body is not provided.
        body: dict | UpdateStatusRequestBody, optional, defaults to None
            A structure representing the details of the collection to create.

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
          "class": "UpdateStatusRequestBody",
          "status": "APPROVED",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{digital_subscription_guid}/update-status")
        await self._async_update_status_request(url, status, body)
        logger.info(f"Updated status for DigitalProduct {digital_subscription_guid}")

    @dynamic_catch
    def update_digital_subscription_status(self, digital_subscription_guid: str,
                                           body: dict | UpdateStatusRequestBody = None,):
        """Update the status of an digital_subscription collection. Async version.

            Parameters
            ----------
            digital_subscription_guid: str
                The guid of the digital product collection to update.
            body: dict
                A dict representing the details of the collection to create.

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
                  "class": "AgreementStatusRequestBody",
                  "status": "APPROVED",
                  "externalSourceGUID": "add guid here",
                  "externalSourceName": "add qualified name here",
                  "effectiveTime": "{{$isoTimestamp}}",
                  "forLineage": false,
                  "forDuplicateProcessing": false
                }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_update_digital_subscription_status(digital_subscription_guid, body))


    @dynamic_catch
    async def _async_link_subscriber(self, subscriber_guid: str, subscription_guid: str,
                                     body: dict | NewRelationshipRequestBody = None)-> None:
        """ Attach a subscriber to a subscription.  The subscriber is of type 'Referenceable' to allow digital
            products, team or business capabilities to be the subscriber. The subscription is an element of type
            DigitalSubscription.
            Async version.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The identifier of the subscription.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class" : "NewRelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "DigitalSubscriberProperties",
            "subscriberId": "add id here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/subscribers/"
            f"{subscriber_guid}/subscriptions/{subscription_guid}/attach")
        await self._async_new_relationship_request(url, "DigitalSubscriberProperties", body)
        logger.info(f"Linking subscriber {subscriber_guid} to subscription {subscription_guid}")

    @dynamic_catch
    def link_subscriber(self, subscriber_guid: str, subscription_guid: str,
                        body: dict | NewRelationshipRequestBody = None):
        """ Attach a subscriber to a subscription.  The subscriber is of type 'Referenceable' to allow digital
            products, team or business capabilities to be the subscriber. The subscription is an element of type
            DigitalSubscription.
            Async version.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The identifier of the subscription.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

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
          "class" : "RelationshipRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "properties": {
            "class": "DigitalSubscriberProperties",
            "subscriberId": "add id here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_subscriber(subscriber_guid, subscription_guid, body))


    @dynamic_catch
    async def _async_detach_subscriber(self, subscriber_guid: str, subscription_guid: str,
                                       body: dict | DeleteRequestBody = None) -> None:
        """ Detach a subscriber from a subscription Request body is optional. Async version.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The unique identifier of the subscription.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/collection-manager/collections"
            f"/agreements/"
            f"{subscriber_guid}/agreement-actors/{subscription_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached subscriber {subscriber_guid} from subscription {subscription_guid}")


    def detach_subscriber(self, subscriber_guid: str, subscription_guid: str, body: dict | DeleteRequestBody= None):
        """ Detach a subscriber from a subscription. Request body is optional.

        Parameters
        ----------
        subscriber_guid: str
            The unique identifier of the subscriber.
        subscription_guid: str
            The unique identifier of the subscription.
        body: dict, optional, default = None
            A dict representing the details of the relationship.

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
          "class": "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_subscriber(subscriber_guid, subscription_guid, body))

        #
        #
        #


    @dynamic_catch
    async def _async_attach_collection(self, parent_guid: str, collection_guid: str,
                                       body: dict | NewRelationshipRequestBody= None):
        """ Connect an existing collection to an element using the ResourceList relationship (0019).
            Async version.

        Parameters
        ----------
        parent_guid: str
            The unique identifier of the parent to attach to.
        collection_guid: str
            The identifier of the collection being attached.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "ResourceListProperties",
            "resourceUse": "Add valid value here",
            "resourceUseDescription": "Add description here",
            "watchResource": false,
            "resourceUseProperties": {
              "property1Name": "property1Value",
              "property2Name": "property2Value"
            }
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/metadata-elements/"
            f"{parent_guid}/collections/{collection_guid}/attach")
        await self._async_new_relationship_request(url, "ResourceListProperties", body)
        logger.info(f"Attached {collection_guid} to {parent_guid}")

    @dynamic_catch
    def attach_collection(self, parent_guid: str, collection_guid: str,
                          body: dict | NewRelationshipRequestBody = None):
        """ Connect an existing collection to an element using the ResourceList relationship (0019).

            Parameters
            ----------
            parent_guid: str
                The unique identifier of the parent to attach to.
            collection_guid: str
                The identifier of the collection being attached.
            body: dict, optional, default = None
                A dict representing the details of the relationship.
            make_anchor: bool, optional, default = False
                Indicates if the collection should be anchored to the element.

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
              "class" : "RelationshipRequestBody",
              "properties": {
                "class": "ResourceListProperties",
                "resourceUse": "Add valid value here",
                "resourceUseDescription": "Add description here",
                "watchResource": false,
                "resourceUseProperties": {
                  "property1Name": "property1Value",
                  "property2Name": "property2Value"
                }
              },
              "externalSourceGUID": "add guid here",
              "externalSourceName": "add qualified name here",
              "effectiveTime" : "{{$isoTimestamp}}",
              "forLineage" : false,
              "forDuplicateProcessing" : false
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_attach_collection(parent_guid, collection_guid, body))


    @dynamic_catch
    async def _async_detach_collection(self, parent_guid: str, collection_guid: str,
                                       body: dict | DeleteRequestBody = None):
        """ Detach an existing collection from an element. If the collection is anchored to the element,
        it is delete.
            Async version.

        Parameters
        ----------
        parent_guid: str
                The unique identifier of the parent to detach from.
        collection_guid: str
                The identifier of the collection being detached.
        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.


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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

        """
        url = (
            f"{self.platform_url}/servers/"
            f"{self.view_server}/api/open-metadata/collection-manager/metadata-elements/"
            f"{parent_guid}/collections/{collection_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Detached collection {collection_guid} from {parent_guid}")


    def detach_collection(self, parent_guid: str, collection_guid: str,
                          body: dict | DeleteRequestBody = None):
        """ Detach an existing collection from an element. If the collection is anchored to the element,
        it is delete.

          Parameters
          ----------
          parent_guid: str
                  The unique identifier of the parent to detach from.
          collection_guid: str
                 The identifier of the collection being detached.
          body: dict, optional, default = None
              A dict representing the details of the relationship.

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
            "class": "MetadataSourceRequestBody",
            "externalSourceGUID": "add guid here",
            "externalSourceName": "add qualified name here",
            "effectiveTime": "{{$isoTimestamp}}",
            "forLineage": false,
            "forDuplicateProcessing": false
          }
          """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_collection(parent_guid, collection_guid, body))


    @dynamic_catch
    async def _async_delete_collection(self, collection_guid: str, body: dict | DeleteRequestBody= None,
                                       cascade: bool = False) -> None:
        """Delete a collection.  It is detected from all parent elements.  If members are anchored to the collection
        then they are also deleted. Async version


        Parameters
        ----------
        collection_guid: str
            The guid of the collection to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict | DeleteRequestBody, optional, default = None
            A structure representing the details of the relationship.

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
        _____
        JSON Structure looks like:
        {
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }


        """
        url = f"{self.collection_command_root}/{collection_guid}/delete"
        await self._async_delete_request(url, body, cascade)
        logger.info(f"Deleted collection {collection_guid} with cascade {cascade}")


    def delete_collection(self, collection_guid: str, body: dict | DeleteRequestBody = None,
                          cascade: bool = False) -> None:
        """Delete a collection.  It is deleted from all parent elements.  If members are anchored to the collection
        then they are also deleted.

        Parameters
        ----------
        collection_guid: str
            The guid of the collection to delete.

        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.

        body: dict DeleteRequestBodyt, optional, default = None
            A dict representing the details of the relationship.

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
        _____
        JSON Structure looks like:



        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_collection(collection_guid, body, cascade))


    @dynamic_catch
    async def _async_add_to_collection(self, collection_guid: str, element_guid: str,
                                       body: dict | NewRelationshipRequestBody = None, ) -> None:
        """Add an element to a collection.  The request body is optional. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict NewRelationshipRequestBody, optional, defaults to None
            The body of the request to add to the collection. See notes.

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
        { "class": "NewRelationshipRequestBody",
           "properties" : {
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
              },
              },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.collection_command_root}/{collection_guid}/members/"
               f"{element_guid}/attach")
        await self._async_new_relationship_request(url, "CollectionMembershipProperties", body)
        logger.info(f"Added {element_guid} to {collection_guid}")


    def add_to_collection(self, collection_guid: str, element_guid: str,
                          body: dict | NewRelationshipRequestBody= None, ) -> None:
        """Add an element to a collection.  The request body is optional.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

            The name of the server to use.


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
         { "class": "RelationshipRequestBody",
           "properties" : {
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
              },
              },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_to_collection(collection_guid, element_guid, body))

    def add_term_to_folder(self, folder_guid: str, term_guid: str,
                             body: dict | NewRelationshipRequestBody = None) -> None:
        """Add a term to a category.  The request body is optional."""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_add_to_collection(folder_guid, term_guid, body))


    @dynamic_catch
    async def _async_update_collection_membership_prop(self, collection_guid: str, element_guid: str, body: dict = None,
                                                   ) -> None:
        """Update an element's membership to a collection. Async version.

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

            The name of the server to use.


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
          "class" : "RelationshipRequestBody",
          "properties" : {
            "class": "CollectionMembershipProperties",
            "membershipRationale": "xxx",
            "createdBy": "user id here",
            "expression": "expression that described why the element is a part of this collection",
            "confidence": 100,
            "membershipStatus": "PROPOSED",
            "userDefinedStatus": "Add valid value here",
            "steward": "identifier of steward that validated this member",
            "stewardTypeName": "type name of element identifying the steward",
            "stewardPropertyName": "property name if the steward's identifier",
            "source": "source of the member",
            "notes": "Add notes here"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """

        url = (f"{self.collection_command_root}/{collection_guid}/members/"
               f"{element_guid}/update")
        await self._async_update_relationship_request(url, "CollectionMembershipProperties", body )
        logger.info(f"Updated membership for collection {collection_guid}")


    def update_collection_membership_prop(self, collection_guid: str, element_guid: str,
                                     body: dict | UpdateRelationshipRequestBody= None,
                                      ) -> None:
        """Update an element's membership to a collection.

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

            The name of the server to use.


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
          "class" : "RelationshipRequestBody",
          "properties" : {
            "class": "CollectionMembershipProperties",
            "membershipRationale": "xxx",
            "createdBy": "user id here",
            "expression": "expression that described why the element is a part of this collection",
            "confidence": 100,
            "membershipStatus": "PROPOSED",
            "userDefinedStatus": "Add valid value here",
            "steward": "identifier of steward that validated this member",
            "stewardTypeName": "type name of element identifying the steward",
            "stewardPropertyName": "property name if the steward's identifier",
            "source": "source of the member",
            "notes": "Add notes here"
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_collection_membership(collection_guid, element_guid, body))


    @dynamic_catch
    async def _async_remove_from_collection(self, collection_guid: str, element_guid: str,
                                            body: dict | DeleteRequestBody = None) -> None:
        """Remove an element from a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict | DeleteRequestBody, optional, defaults to None
            The body of the request to add to the collection. See notes.

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
        {
          "class" : "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """

        url = (f"{self.collection_command_root}/{collection_guid}/members/"
               f"{element_guid}/detach")
        await self._async_delete_request(url, body)
        logger.info(f"Removed member {element_guid} from collection {collection_guid}")


    def remove_from_collection(self, collection_guid: str, element_guid: str,
                               body: dict | DeleteRequestBody= None) -> None:
        """Remove an element from a collection. Async version.

        Parameters
        ----------
        collection_guid: str
            identity of the collection to return members for.
        element_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

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
        {
          "class" : "MetadataSourceRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_from_collection(collection_guid, element_guid, body))

        #
        #
        #


    def remove_term_from_category(self, folder_guid: str, term_guid: str,
                               body: dict | DeleteRequestBody= None) -> None:
        """Remove a term from a category.

        Parameters
        ----------
        category_guid: str
            identity of the collection to return members for.
        term_guid: str
            Effective time of the query. If not specified will default to any time.
        body: dict, optional, defaults to None
            The body of the request to add to the collection. See notes.

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

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_remove_from_collection(folder_guid, term_guid, body))

        #
        #
        #


    @dynamic_catch
    async def _async_get_member_list(self, collection_guid: str = None, collection_name: str = None,
                                     collection_qname: str = None, ) -> list | str:
        """Get the member list for the collection - async version.
        Parameters
        ----------
        collection_guid: str,
           identity of the collection to return members for. If none, collection_name or
           collection_qname are used.
        collection_name: str,
           display name of the collection to return members for. If none, collection_guid
           or collection_qname are used.
        collection_qname: str,
           qualified name of the collection to return members for. If none, collection_guid
           or collection_name are used.

        Returns
        -------
        list | str
            The list of member information if successful, otherwise the string "No members found"

        Raises
        ------
        InvalidParameterException
            If the root_collection_name does not have exactly one root collection.

        """

        # first find the guid for the collection we are using as root

        # now find the members of the collection
        member_list = []
        members = await self._async_get_collection_members(collection_guid, collection_name, collection_qname)
        if (type(members) is str) or (len(members) == 0):
            logger.trace(f"No members found for collection {collection_guid}")
            return "No members found"
        # finally, construct a list of  member information
        for member_rel in members:
            member_guid = member_rel["elementHeader"]["guid"]
            member = await self._async_get_element_by_guid_(member_guid)
            if isinstance(member, dict):
                member_instance = {
                    "name": member["properties"].get('displayName', ''),
                    "qualifiedName": member["properties"]["qualifiedName"], "guid": member["elementHeader"]["guid"],
                    "description": member["properties"].get("description", ''),
                    "type": member["elementHeader"]["type"]['typeName'],
                    }
                member_list.append(member_instance)
        logger.debug(f"Member list for collection {collection_guid}: {member_list}")
        return member_list if len(member_list) > 0 else "No members found"


    def get_member_list(self, collection_guid: str = None, collection_name: str = None,
                        collection_qname: str = None, ) -> list | bool:
        """Get the member list for a collection - async version.
        Parameters
        ----------
        collection_guid: str,
           identity of the collection to return members for. If none, collection_name or
           collection_qname are used.
        collection_name: str,
           display name of the collection to return members for. If none, collection_guid
           or collection_qname are used.
        collection_qname: str,
           qualified name of the collection to return members for. If none, collection_guid
           or collection_name are used.
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
        resp = loop.run_until_complete(
            self._async_get_member_list(collection_guid, collection_name, collection_qname))
        return resp

    def _extract_digital_product_properties(self, element: dict, guid: str, output_format: str) -> dict:
        props = element["properties"]
        digital_prod = DigitalProductProperties.model_validate(props)
        added_props = get_defined_field_values(digital_prod)

        used_by_digital_products = element.get("usedByDigitalProducts", "")
        if isinstance(used_by_digital_products, (list | dict)):
            used_by_digital_products_list = ""
            for prod in used_by_digital_products:
                used_by_digital_products_list += f"{prod["relatedElement"]["properties"]["qualifiedName"]}, "
            added_props["used_by_digital_products"] = used_by_digital_products_list[:-2]

        uses_digital_products = element.get("usesDigitalProducts", "")
        if isinstance(uses_digital_products, (list | dict)):
            uses_digital_products_list = ""
            for prod in uses_digital_products:
                uses_digital_products_list += f"{prod["relatedElement"]["properties"]["qualifiedName"]}, "
            added_props["uses_digital_products"] = uses_digital_products_list[:-2]

        return added_props

    def _extract_agreement_properties(self, element: dict, guid: str, output_format: str) -> dict:
        props = element["properties"]
        # agreement = Collections.model_validate(props)
        # added_props = get_defined_field_values(agreement)

        added_props = {}
        agreement_items = element.get("agreementItems", "")
        if isinstance(agreement_items, (list | dict)):
            agreement_items_list = ""
            for item in agreement_items:
                agreement_items_list += f"{item["relatedElement"]["properties"]["qualifiedName"]}, "
            added_props["agreementItems"] = agreement_items_list[:-2]

        return added_props

    def _extract_collection_properties(self, element: dict, columns_struct: dict) -> dict:
        """
        Extract common properties from a collection element and populate into the provided columns_struct.

        Args:
            element (dict): The collection element
            columns_struct (dict): The columns structure to populate

        Returns:
            dict: columns_struct with column 'value' fields populated
        """
        # First, populate from element.properties using the utility
        col_data = populate_columns_from_properties(element, columns_struct)

        columns_list = col_data.get("formats", {}).get("columns", [])

        # Populate header-derived values
        header_props = _extract_referenceable_properties(element)
        for column in columns_list:
            key = column.get('key')
            if key in header_props:
                column['value'] = header_props.get(key)
            elif isinstance(key, str) and key.lower() == 'guid':
                column['value'] = header_props.get('GUID')

        # Derived/computed fields
        # collectionCategories are classifications
        classification_names = ""
        classifications = element.get('elementHeader', {}).get("collectionCategories", [])
        for classification in classifications:
            classification_names += f"{classification['classificationName']}, "
        if classification_names:
            for column in columns_list:
                if column.get('key') == 'classifications':
                    column['value'] = classification_names[:-2]
                    break

        # Populate requested relationship-based columns generically from top-level keys
        col_data = get_required_relationships(element, col_data)

        # Subject area classification
        subject_area = element.get('elementHeader', {}).get("subjectArea", "") or ""
        subj_val = ""
        if isinstance(subject_area, dict):
            subj_val = subject_area.get("classificationProperties", {}).get("subjectAreaName", "")
        for column in columns_list:
            if column.get('key') == 'subject_area':
                column['value'] = subj_val
                break

        # Mermaid graph
        mermaid_val = element.get('mermaidGraph', "") or ""
        for column in columns_list:
            if column.get('key') == 'mermaid':
                column['value'] = mermaid_val
                break

        logger.trace(f"Extracted/Populated columns: {col_data}")

        return col_data


    def _generate_collection_output(self, elements: dict|list[dict], filter: Optional[str],
                                    element_type_name: Optional[str], output_format: str = "DICT",
                                    output_format_set: dict | str = None) -> str| list[dict]:
        """ Generate output for collections in the specified format.

            Args:
                elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
                filter (Optional[str]): The search string used to find the elements
                element_type_name (Optional[str]): The type of collection
                output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
                output_format_set (Optional[dict], optional): List of dictionaries containing column data. Defaults
                to None.

            Returns:
                Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
        """
        if element_type_name is None:
            entity_type = "Collections"
        else:
            entity_type = element_type_name
        # First see if the user has specified an output_format_set - either a label or a dict
        get_additional_props_func  = None
        if output_format_set:
            if isinstance(output_format_set, str):
                output_formats = select_output_format_set(output_format_set, output_format)
            elif isinstance(output_format_set, dict):
                output_formats = get_output_format_type_match(output_format_set, output_format)

        # If no output_format was set, then use the element_type_name to lookup the output format
        elif element_type_name:
            output_formats = select_output_format_set(element_type_name, output_format)
        else:
            # fallback to collections or entity type
            output_formats = select_output_format_set(entity_type,output_format)
        if output_formats is None:
            output_formats = select_output_format_set("Default", output_format)

        if output_formats:
            get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
            if isinstance(get_additional_props_name, str):
                class_name, method_name = get_additional_props_name.split(".")
                if hasattr(self, method_name):
                    get_additional_props_func = getattr(self, method_name)

        logger.trace(f"Executing generate_collection_output for {entity_type}: {output_formats}")
        return generate_output(
            elements,
            filter,
            entity_type,
            output_format,
            self._extract_collection_properties,
            get_additional_props_func,
            output_formats,
            )


from typing import Union, Dict, List, Optional

if __name__ == "__main__":
    print("Main-Collection Manager")
