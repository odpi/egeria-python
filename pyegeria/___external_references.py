"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage external references to a variety of artifacts.

"""

import asyncio
from typing import Optional

from loguru import logger
from pydantic import HttpUrl

from pyegeria._globals import NO_GUID_RETURNED
from pyegeria._output_formats import select_output_format_set, get_output_format_type_match
from pyegeria.config import settings
from pyegeria.models import (SearchStringRequestBody, FilterRequestBody, GetRequestBody, NewElementRequestBody,
                             TemplateRequestBody,
                             UpdateElementRequestBody, UpdateStatusRequestBody, NewRelationshipRequestBody,
                             DeleteRequestBody, UpdateRelationshipRequestBody, get_defined_field_values)
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties, populate_columns_from_properties,
                                       get_required_relationships)
from pyegeria.utils import dynamic_catch

app_settings = settings
EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier

from pyegeria._client_new import Client2


class ExternalReferences(Client2):
    """
    Establish linkage to external references which can be a variety of artifacts. Including media,
    documents, data, and more.

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
        logger.info(f"ExternalReferences initialized, platform origin is: {result}")
        self.command_root: str = (
            f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external-references")

    @dynamic_catch
    async def _async_create_external_reference(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic external_reference. If the body is not present, the display_name, description, category,
            and classification will be used to create a simple, self-anchored external_reference.
            Collections: https://egeria-project.org/concepts/external_reference
            Async version.

        Parameters
        ----------


        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the external_reference to create. If supplied, this
            information will be used to create the external_reference and the other attributes will be ignored. The body is
            validated before being used.

        Returns
        -------
        str - the guid of the created external_reference

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
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
            "class": "ExternalReferenceProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the external_reference here",
            "category": "Add appropriate valid value for type",
            "referenceTitle: "Add reference title here",
            "referenceAbstract": "Add reference abstract here",
            "authors": ["Add author names here"],
            "url": "Add url here",
            "datePublished": "2023-01-01",
            "dateConnected": "2023-01-01",
            "dateCreated": "2023-01-01",
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
             "class": "ExternalReferenceProperties",
            "qualifiedName": "Must provide a unique name here",
            "name": "Add display name here",
            "description": "Add description of the external_reference here",
            "category": "Add appropriate valid value for type",
            "referenceTitle: "Add reference title here",
            "referenceAbstract": "Add reference abstract here",
            "authors": ["Add author names here"],
            "url": "Add url here",
            "datePublished": "2023-01-01",
            "dateConnected": "2023-01-01",
            "dateCreated": "2023-01-01",
          },
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }

    """

        url = f"{self.external_reference_command_root}/external-references"
        response = await self._async_create_collection(body=body)
        return response

    def create_external_reference(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new generic external_reference. If the body is not present, the display_name, description, category,
             and classification will be used to create a simple, self-anchored external_reference.
             Collections: https://egeria-project.org/concepts/external_reference
             Async version.

             Parameters
             ----------


             body: dict | NewElementRequestBody, optional
                 A dict or NewElementRequestBody representing the details of the external_reference to create. If supplied, this
                 information will be used to create the external_reference and the other attributes will be ignored. The body is
                 validated before being used.

             Returns
             -------
             str - the guid of the created external_reference

             Raises
             ------
             PyegeriaException
                 One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
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
                 "class": "ExternalReferenceProperties",
                 "qualifiedName": "Must provide a unique name here",
                 "name": "Add display name here",
                 "description": "Add description of the external_reference here",
                 "category": "Add appropriate valid value for type",
                 "referenceTitle: "Add reference title here",
                 "referenceAbstract": "Add reference abstract here",
                 "authors": ["Add author names here"],
                 "url": "Add url here",
                 "datePublished": "2023-01-01",
                 "dateConnected": "2023-01-01",
                 "dateCreated": "2023-01-01",
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
                  "class": "ExternalReferenceProperties",
                 "qualifiedName": "Must provide a unique name here",
                 "name": "Add display name here",
                 "description": "Add description of the external_reference here",
                 "category": "Add appropriate valid value for type",
                 "referenceTitle: "Add reference title here",
                 "referenceAbstract": "Add reference abstract here",
                 "authors": ["Add author names here"],
                 "url": "Add url here",
                 "datePublished": "2023-01-01",
                 "dateConnected": "2023-01-01",
                 "dateCreated": "2023-01-01",
               },
               "externalSourceGUID": "add guid here",
               "externalSourceName": "add qualified name here",
               "effectiveTime": "{{$isoTimestamp}}",
               "forLineage": false,
               "forDuplicateProcessing": false
             }


      """

        return asyncio.get_event_loop().run_until_complete(self._async_create_external_reference(body))


#######

@dynamic_catch
async def _async_create_external_reference_from_template(self, body: TemplateRequestBody | dict) -> str:
    """Create a new metadata element to represent a external_reference using an existing metadata element as a template.
    The template defines additional classifications and relationships that are added to the new external_reference.
    Async version.

    Parameters
    ----------

    body: dict
        A dict representing the details of the external_reference to create.

    Returns
    -------
    str - the guid of the created external_reference

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

    url = f"{self.external_reference_command_root}/from-template"
    json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
    logger.info(json_body)
    resp = await self._async_make_request("POST", url, json_body, is_json=True)
    logger.info(f"Create external_reference from template with GUID: {resp.json().get('guid')}")
    return resp.json().get("guid", NO_GUID_RETURNED)


def create_external_reference_from_template(self, body: dict) -> str:
    """Create a new metadata element to represent a external_reference using an existing metadata element as a template.
    The template defines additional classifications and relationships that are added to the new external_reference.

    Parameters
    ----------
    body: dict
        A dict representing the details of the external_reference to create.

    Returns
    -------
    str - the guid of the created external_reference

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
    resp = loop.run_until_complete(self._async_create_external_reference_from_template(body))
    return resp

    #
    # Manage external_references
    #


@dynamic_catch
async def _async_update_external_reference(self, external_reference_guid: str,
                                           body: dict | UpdateElementRequestBody) -> None:
    """ Update the properties of a external_reference. Use the correct properties object (CollectionProperties,
        DigitalProductProperties, AgreementProperties, etc), that is appropriate for your element.
        Collections: https://egeria-project.org/concepts/external_reference

        Async version.
    Parameters
    ----------
    external_reference_guid: str
        The guid of the external_reference to update.

    body: dict | UpdateElementRequestBody, optional
        A dict or NewElementRequestBody representing the details of the external_reference to create. If supplied, this
        information will be used to create the external_reference and the other attributes will be ignored. The body is
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
        One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
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
        "description" : "Add description of the external_reference here",
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

    url = (f"{self.external_reference_command_root}/{external_reference_guid}/update")
    await self._async_update_element_body_request(url, [""], body)


@dynamic_catch
def update_external_reference(self, external_reference_guid: str, body: dict | NewElementRequestBody) -> None:
    """ Update the properties of a external_reference. Use the correct properties object (CollectionProperties,
        DigitalProductProperties, AgreementProperties, etc), that is appropriate for your element.
        Collections: https://egeria-project.org/concepts/external_reference

    Parameters
    ----------
    external_reference_guid: str
        The guid of the external_reference to update.

    body: dict | NewElementRequestBody, optional
        A dict or NewElementRequestBody representing the details of the external_reference to create. If supplied, this
        information will be used to create the external_reference and the other attributes will be ignored. The body is
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
        One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
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
        "description" : "Add description of the external_reference here",
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
        self._async_update_external_reference(external_reference_guid, body))


def get_attached_external_references(self, parent_guid: str, start_from: int = 0, page_size: int = 0, body: dict = None,
                                     output_format: str = "JSON", output_format_set: str | dict = None) -> list:
    """Returns the list of external_references that are linked off of the supplied element using the ResourceList
       relationship. Async version.

    Parameters
    ----------
    parent_guid: str
        The identity of the parent to find linked external_references from.
    start_from: int, [default=0], optional
                When multiple pages of results are available, the page number to start from.
    page_size: int, [default=None]
        The number of items to return in a single page. If not specified, the default will be taken from
        the class instance.
    body: dict, optional, default = None
        If supplied, adds addition request details - for instance, to filter the results on external_referenceType
    output_format: str, default = "JSON"
        - one of "MD", "LIST", "FORM", "REPORT", "DICT", "MERMAID" or "JSON"
     output_format_set: str | dict = None), optional, default = None
            The desired output columns/fields to include.


    Returns
    -------
    List

    A list of external_references linked off of the supplied element.

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
      "filter": "Add external_referenceType value here"
    }

    """
    return asyncio.get_event_loop().run_until_complete(
        self._async_get_attached_external_references(parent_guid, start_from, page_size,
                                                     body, output_format, output_format_set))


@dynamic_catch
async def _async_find_external_references(self, search_string: str = "*", classification_names: list[str] = None,
                                          metadata_element_types: list[str] = None,
                                          starts_with: bool = True, ends_with: bool = False, ignore_case: bool = False,
                                          start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                          output_format_set: str | dict = None,
                                          body: dict | SearchStringRequestBody = None) -> list | str:
    """ Returns the list of external_references matching the search string filtered by the optional classification.
        This method can either be used with a body, allowing full control, or with the individual parameters.
        If the body is provided it will be used and the search_string will be ignored.

    Parameters
    ----------
    search_string: str
        Search string to match against - None or '*' indicate match against all external_references (may be filtered by
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
    url = str(HttpUrl(f"{self.external_reference_command_root}/by-search-string"))
    response = await self._async_find_request(url, _type="Collection",
                                              _gen_output=self._generate_external_reference_output,
                                              search_string=search_string, classification_names=classification_names,
                                              metadata_element_types=metadata_element_types,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size,
                                              output_format=output_format, output_format_set=output_format_set,
                                              body=body)

    return response


@dynamic_catch
def find_external_references(self, search_string: str = '*', classification_names: str = None,
                             metadata_element_types: list[str] = None, starts_with: bool = True,
                             ends_with: bool = False, ignore_case: bool = False,
                             start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                             output_format_set: str | dict = None,
                             body: dict | SearchStringRequestBody = None) -> list | str:
    """ Returns the list of external_references matching the search string filtered by the optional classification.
        This method can either be used with a body, allowing full control, or with the individual parameters.
        If the body is provided it will be used and the search_string will be ignored.

    Parameters
    ----------
    search_string: str
        Search string to match against - None or '*' indicate match against all external_references (may be filtered by
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
        self._async_find_external_references(search_string, classification_names, metadata_element_types,
                                             starts_with, ends_with, ignore_case,
                                             start_from, page_size, output_format,
                                             output_format_set, body))


@dynamic_catch
async def _async_get_external_references_by_name(self, filter_string: str = None,
                                                 classification_names: list[str] = None,
                                                 body: dict | FilterRequestBody = None,
                                                 start_from: int = 0, page_size: int = 0,
                                                 output_format: str = 'JSON',
                                                 output_format_set: str | dict = None) -> list | str:
    """ Returns the list of external_references with a particular name.

        Parameters
        ----------
        name: str,
            name to use to find matching external_references.
        classification_names: list[str], optional, default = None
            type of external_reference to filter by - e.g., DataDict, Folder, Root
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

        A list of external_references match matching the name. Returns a string if none found.

        Raises
        ------

        InvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PropertyServerException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
    """
    url = str(HttpUrl(f"{self.external_reference_command_root}/by-name"))
    response = await self._async_get_name_request(url, _type="Collection",
                                                  _gen_output=self._generate_external_reference_output,
                                                  filter_string=filter_string,
                                                  classification_names=classification_names,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

    return response


def get_external_references_by_name(self, name: str = None, classification_names: list[str] = None,
                                    body: dict | FilterRequestBody = None,
                                    start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                    output_format_set: str | dict = None) -> list | str:
    """Returns the list of external_references matching the search string. Async version.
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

    Parameters
    ----------
    name: str,
        name to use to find matching external_references.
    classification_names: list[str], optional, default = None
        type of external_reference to filter by - e.g., DataDict, Folder, Root
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

    A list of external_references match matching the search string. Returns a string if none found.

    Raises
    ------
    PyegeriaException

    """
    return asyncio.get_event_loop().run_until_complete(
        self._async_get_external_references_by_name(name, classification_names, body, start_from, page_size,
                                                    output_format, output_format_set))


@dynamic_catch
async def _async_get_external_references_by_category(self, category: str, classification_names: list[str] = None,
                                                     body: dict | FilterRequestBody = None, start_from: int = 0,
                                                     page_size: int = 0,
                                                     output_format: str = 'JSON',
                                                     output_format_set: str | dict = None) -> list | str:
    """Returns the list of external_references with a particular category. This is an optional text field in the
        external_reference element.

    Parameters
    ----------
    category: str
        category to use to find matching external_references.
    classification_names: str, optional
        An optional filter on the search, e.g., DataSpec
    body: dict, optional, default = None
        Provides, a full request body. If specified, the body filter parameter supercedes the external_reference_type
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

    A list of external_references matching the external_reference type. Returns a string if none found.

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
    url = str(HttpUrl(f"{self.external_reference_command_root}/by-external_reference-category"))
    response = await self._async_get_name_request(url, _type="Collection",
                                                  _gen_output=self._generate_external_reference_output,
                                                  filter_string=category, classification_names=classification_names,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

    return response


def get_external_references_by_category(self, category: str, classification_names: list[str] = None,
                                        body: dict | FilterRequestBody = None,
                                        start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                        output_format_set: str | dict = None) -> list | str:
    """Returns the list of external_references with a particular external_referenceType. This is an optional text field in the
        external_reference element.

    Parameters
    ----------
    category: str
        category to use to find matching external_references.
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

    A list of external_references filtered by the specified category. Output based on specified output format.

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
        self._async_get_external_references_by_category(category, classification_names, body, start_from, page_size,
                                                        output_format, output_format_set))


@dynamic_catch
async def _async_get_external_reference_by_guid(self, external_reference_guid: str, element_type: str = None,
                                                body: dict | GetRequestBody = None,
                                                output_format: str = 'JSON',
                                                output_format_set: str | dict = None) -> dict | str:
    """Return the properties of a specific external_reference. Async version.

    Parameters
    ----------
    external_reference_guid: str,
        unique identifier of the external_reference.
    element_type: str, default = None, optional
        type of external_reference - Collection, DataSpec, Agreement, etc.
    body: dict | GetRequestBody, optional, default = None
        full request body.
    output_format: str, default = "JSON"
        - one of "DICT", "MERMAID" or "JSON"
     output_format_set: str | dict, optional, default = None
            The desired output columns/fields to include.

    Returns
    -------
    dict | str

    A JSON dict representing the specified external_reference. Returns a string if none found.

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

    url = str(HttpUrl(f"{self.external_reference_command_root}/{external_reference_guid}/retrieve"))
    type = element_type if element_type else "Collection"

    response = await self._async_get_guid_request(url, _type=type,
                                                  _gen_output=self._generate_external_reference_output,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

    return response


def get_external_reference_by_guid(self, external_reference_guid: str, element_type: str = None,
                                   body: dict | GetRequestBody = None,
                                   output_format: str = 'JSON', output_format_set: str | dict = None) -> dict | str:
    """ Return the properties of a specific external_reference. Async version.

        Parameters
        ----------
        external_reference_guid: str,
            unique identifier of the external_reference.
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

        A JSON dict representing the specified external_reference. Returns a string if none found.

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
        self._async_get_external_reference_by_guid(external_reference_guid, element_type, body,
                                                   output_format, output_format_set))


@dynamic_catch
async def _async_update_external_reference_status(self, external_reference_guid: str, status: str = None,
                                                  body: dict | UpdateStatusRequestBody = None):
    """Update the status of a external_reference. Async version.

    Parameters
    ----------
    external_reference_guid: str
        The guid of the external_reference to update.
    status: str, optional
        The new lifecycle status for the external_reference. Ignored, if the body is provided.
    body: dict | UpdateStatusRequestBody, optional
        A structure representing the details of the external_reference to create. If supplied, these details
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

    url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/metadata-elements/{external_reference_guid}/update-status"
    await self._async_update_status_request(url, status, body)


@dynamic_catch
def update_external_reference_status(self, external_reference_guid: str, status: str = None,
                                     body: dict | UpdateStatusRequestBody = None):
    """Update the status of a DigitalProduct external_reference.

    Parameters
    ----------
    external_reference_guid: str
        The guid of the external_reference to update.
    status: str, optional
        The new lifecycle status for the digital product. Ignored, if the body is provided.
    body: dict | UpdateStatusRequestBody, optional
        A structure representing the details of the external_reference to create. If supplied, these details
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
    loop.run_until_complete(self._async_update_external_reference_status(external_reference_guid, status, body))


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
        f"{self.view_server}/api/open-metadata/external_reference-manager/external_references/digital-products/"
        f"{upstream_digital_prod_guid}/product-dependencies/{downstream_digital_prod_guid}/attach")
    await self._async_new_relationship_request(url, "InformationSupplyChainLinkProperties", body)
    logger.info(f"Linked {upstream_digital_prod_guid} -> {downstream_digital_prod_guid}")


def link_digital_product_dependency(self, upstream_digital_prod_guid: str, downstream_digital_prod_guid: str,
                                    body: dict | NewRelationshipRequestBody = None):
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
                                                   body: dict | DeleteRequestBody = None) -> None:
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
        f"{self.view_server}/api/open-metadata/external_reference-manager/external_references/digital-products/"
        f"{upstream_digital_prod_guid}/product-dependencies/{downstream_digital_prod_guid}/detach")
    await self._async_delete_request(url, body)
    logger.info(f"Detached digital product dependency {upstream_digital_prod_guid} -> {downstream_digital_prod_guid}")


def detach_digital_product_dependency(self, upstream_digital_prod_guid: str, downstream_digital_prod_guid: str,
                                      body: dict | DeleteRequestBody = None):
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


#

###

@dynamic_catch
async def _async_link_agreement_item(self, agreement_guid: str, agreement_item_guid: str,
                                     body: dict | NewRelationshipRequestBody = None) -> None:
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
    url = (
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references/"
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
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references"
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
    url = (
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references/"
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
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references"
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
    """Create a new external_reference that represents a type of agreement called a digital_subscription. Async version.

    Parameters
    ----------
    body | NewElementRequewstBody: dict
        A structure representing the details of the external_reference to create.

    Returns
    -------
    str - the guid of the created external_reference

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
    Note: the three dates: introductionDate, nextVersionDate, and withdrawDate must
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
    Note: the three dates: introductionDate, nextVersionDate, and withdrawDate must be valid dates if specified,
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
    url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references"
    return await self._async_create_element_body_request(url, "DigitalSubscriptionProperties", body)


def create_digital_subscription(self, body: dict) -> str:
    """Create a new external_reference that represents a type of agreement called a digital_subscription.

    Parameters
    ----------
    body: dict
        A dict representing the details of the external_reference to create.

    Returns
    -------
    str - the guid of the created external_reference

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
    Note: the three dates: introductionDate, nextVersionDate, and withdrawDate must
    be valid dates if specified, otherwise you will get a 400 error response.

    JSON Structure looks like:
    With a lifecycle, the body is:

    The DigitalSubscription is a type of Agreement and so can have lifecycle states.
    Note: the three dates: introductionDate, nextVersionDate, and withdrawDate must be valid dates if specified,
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
    """Update the properties of the digital_subscription external_reference. Async version.

    Parameters
    ----------
    digital_subscription_guid: str
        The guid of the digital_subscription to update.
    body: dict | UpdateElementRequestBody
        A structure representing the details of the external_reference to create.

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
    url = (
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references/"
        f"{digital_subscription_guid}/update")
    await self._async_update_element_body_request(url, ["DigitalSubscriptionProperties"], body)
    logger.info(f"Updated digital subscription {digital_subscription_guid}")


@dynamic_catch
def update_digital_subscription(self, digital_subscription_guid: str, body: dict, ):
    """Update the properties of the DigitalProduct classification attached to a external_reference.

    Parameters
    ----------
    digital_subscription_guid: str
        The guid of the digital_subscription to update.
    body: dict
        A dict representing the details of the external_reference to create.
    replace_all_props: bool, optional, defaults to False
        Whether to replace all properties in the external_reference.


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
                                                    body: dict | UpdateStatusRequestBody = None) -> None:
    """Update the status of a digital_subscription external_reference. Async version.

    Parameters
    ----------
    digital_subscription_guid: str
        The guid of the digital product external_reference to update.
    status: str, optional
        The new status of the digital_subscription external_reference. Will be used only if body is not provided.
    body: dict | UpdateStatusRequestBody, optional, defaults to None
        A structure representing the details of the external_reference to create.

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
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references"
        f"/agreements/"
        f"{digital_subscription_guid}/update-status")
    await self._async_update_status_request(url, status, body)
    logger.info(f"Updated status for DigitalProduct {digital_subscription_guid}")


@dynamic_catch
def update_digital_subscription_status(self, digital_subscription_guid: str,
                                       body: dict | UpdateStatusRequestBody = None, ):
    """Update the status of an digital_subscription external_reference. Async version.

        Parameters
        ----------
        digital_subscription_guid: str
            The guid of the digital product external_reference to update.
        body: dict
            A dict representing the details of the external_reference to create.

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
                                 body: dict | NewRelationshipRequestBody = None) -> None:
    """ Attach a subscriber to a subscription.  The subscriber is of type 'Referenceable' to allow digital
        products, team, or business capabilities to be the subscriber. The subscription is an element of type
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
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references"
        f"/subscribers/"
        f"{subscriber_guid}/subscriptions/{subscription_guid}/attach")
    await self._async_new_relationship_request(url, "DigitalSubscriberProperties", body)
    logger.info(f"Linking subscriber {subscriber_guid} to subscription {subscription_guid}")


@dynamic_catch
def link_subscriber(self, subscriber_guid: str, subscription_guid: str,
                    body: dict | NewRelationshipRequestBody = None):
    """ Attach a subscriber to a subscription.  The subscriber is of type 'Referenceable' to allow digital
        products, team, or business capabilities to be the subscriber. The subscription is an element of type
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
        f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/external_reference-manager/external_references"
        f"/agreements/"
        f"{subscriber_guid}/agreement-actors/{subscription_guid}/detach")
    await self._async_delete_request(url, body)
    logger.info(f"Detached subscriber {subscriber_guid} from subscription {subscription_guid}")


def detach_subscriber(self, subscriber_guid: str, subscription_guid: str, body: dict | DeleteRequestBody = None):
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
async def _async_attach_external_reference(self, parent_guid: str, external_reference_guid: str,
                                           body: dict | NewRelationshipRequestBody = None):
    """ Connect an existing external_reference to an element using the ResourceList relationship (0019).
        Async version.

    Parameters
    ----------
    parent_guid: str
        The unique identifier of the parent to attach to.
    external_reference_guid: str
        The identifier of the external_reference being attached.
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
        f"{self.view_server}/api/open-metadata/external_reference-manager/metadata-elements/"
        f"{parent_guid}/external_references/{external_reference_guid}/attach")
    await self._async_new_relationship_request(url, "ResourceListProperties", body)
    logger.info(f"Attached {external_reference_guid} to {parent_guid}")


@dynamic_catch
def attach_external_reference(self, parent_guid: str, external_reference_guid: str,
                              body: dict | NewRelationshipRequestBody = None):
    """ Connect an existing external_reference to an element using the ResourceList relationship (0019).

        Parameters
        ----------
        parent_guid: str
            The unique identifier of the parent to attach to.
        external_reference_guid: str
            The identifier of the external_reference being attached.
        body: dict, optional, default = None
            A dict representing the details of the relationship.
        make_anchor: bool, optional, default = False
            Indicates if the external_reference should be anchored to the element.

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
    loop.run_until_complete(self._async_attach_external_reference(parent_guid, external_reference_guid, body))


@dynamic_catch
async def _async_detach_external_reference(self, parent_guid: str, external_reference_guid: str,
                                           body: dict | DeleteRequestBody = None):
    """ Detach an existing external_reference from an element. If the external_reference is anchored to the element,
    it is delete.
        Async version.

    Parameters
    ----------
    parent_guid: str
            The unique identifier of the parent to detach from.
    external_reference_guid: str
            The identifier of the external_reference being detached.
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
        f"{self.view_server}/api/open-metadata/external_reference-manager/metadata-elements/"
        f"{parent_guid}/external_references/{external_reference_guid}/detach")
    await self._async_delete_request(url, body)
    logger.info(f"Detached external_reference {external_reference_guid} from {parent_guid}")


def detach_external_reference(self, parent_guid: str, external_reference_guid: str,
                              body: dict | DeleteRequestBody = None):
    """ Detach an existing external_reference from an element. If the external_reference is anchored to the element,
    it is delete.

      Parameters
      ----------
      parent_guid: str
              The unique identifier of the parent to detach from.
      external_reference_guid: str
             The identifier of the external_reference being detached.
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
    loop.run_until_complete(self._async_detach_external_reference(parent_guid, external_reference_guid, body))


@dynamic_catch
async def _async_delete_external_reference(self, external_reference_guid: str, body: dict | DeleteRequestBody = None,
                                           cascade: bool = False) -> None:
    """Delete a external_reference.  It is detected from all parent elements.  If members are anchored to the external_reference
    then they are also deleted. Async version


    Parameters
    ----------
    external_reference_guid: str
        The guid of the external_reference to delete.

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
    url = f"{self.external_reference_command_root}/{external_reference_guid}/delete"
    await self._async_delete_request(url, body, cascade)
    logger.info(f"Deleted external_reference {external_reference_guid} with cascade {cascade}")


def delete_external_reference(self, external_reference_guid: str, body: dict | DeleteRequestBody = None,
                              cascade: bool = False) -> None:
    """Delete a external_reference.  It is deleted from all parent elements.  If members are anchored to the external_reference
    then they are also deleted.

    Parameters
    ----------
    external_reference_guid: str
        The guid of the external_reference to delete.

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
    loop.run_until_complete(self._async_delete_external_reference(external_reference_guid, body, cascade))


@dynamic_catch
async def _async_add_to_external_reference(self, external_reference_guid: str, element_guid: str,
                                           body: dict | NewRelationshipRequestBody = None, ) -> None:
    """Add an element to a external_reference.  The request body is optional. Async version.

    Parameters
    ----------
    external_reference_guid: str
        identity of the external_reference to return members for.
    element_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict NewRelationshipRequestBody, optional, defaults to None
        The body of the request to add to the external_reference. See notes.

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
          "expression": "expression that described why the element is a part of this external_reference",
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

    url = (f"{self.external_reference_command_root}/{external_reference_guid}/members/"
           f"{element_guid}/attach")
    await self._async_new_relationship_request(url, "CollectionMembershipProperties", body)
    logger.info(f"Added {element_guid} to {external_reference_guid}")


def add_to_external_reference(self, external_reference_guid: str, element_guid: str,
                              body: dict | NewRelationshipRequestBody = None, ) -> None:
    """Add an element to a external_reference.  The request body is optional.

    Parameters
    ----------
    external_reference_guid: str
        identity of the external_reference to return members for.
    element_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict, optional, defaults to None
        The body of the request to add to the external_reference. See notes.

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
          "expression": "expression that described why the element is a part of this external_reference",
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
    loop.run_until_complete(self._async_add_to_external_reference(external_reference_guid, element_guid, body))


def add_term_to_folder(self, folder_guid: str, term_guid: str,
                       body: dict | NewRelationshipRequestBody = None) -> None:
    """Add a term to a category.  The request body is optional."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self._async_add_to_external_reference(folder_guid, term_guid, body))


@dynamic_catch
async def _async_update_external_reference_membership_prop(self, external_reference_guid: str, element_guid: str,
                                                           body: dict = None,
                                                           ) -> None:
    """Update an element's membership to a external_reference. Async version.

    Parameters
    ----------
    external_reference_guid: str
        identity of the external_reference to return members for.
    element_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict, optional, defaults to None
        The body of the request to add to the external_reference. See notes.
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
        "expression": "expression that described why the element is a part of this external_reference",
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

    url = (f"{self.external_reference_command_root}/{external_reference_guid}/members/"
           f"{element_guid}/update")
    await self._async_update_relationship_request(url, "CollectionMembershipProperties", body)
    logger.info(f"Updated membership for external_reference {external_reference_guid}")


def update_external_reference_membership_prop(self, external_reference_guid: str, element_guid: str,
                                              body: dict | UpdateRelationshipRequestBody = None,
                                              ) -> None:
    """Update an element's membership to a external_reference.

    Parameters
    ----------
    external_reference_guid: str
        identity of the external_reference to return members for.
    element_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict, optional, defaults to None
        The body of the request to add to the external_reference. See notes.
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
        "expression": "expression that described why the element is a part of this external_reference",
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
        self._async_update_external_reference_membership(external_reference_guid, element_guid, body))


@dynamic_catch
async def _async_remove_from_external_reference(self, external_reference_guid: str, element_guid: str,
                                                body: dict | DeleteRequestBody = None) -> None:
    """Remove an element from a external_reference. Async version.

    Parameters
    ----------
    external_reference_guid: str
        identity of the external_reference to return members for.
    element_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict | DeleteRequestBody, optional, defaults to None
        The body of the request to add to the external_reference. See notes.

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

    url = (f"{self.external_reference_command_root}/{external_reference_guid}/members/"
           f"{element_guid}/detach")
    await self._async_delete_request(url, body)
    logger.info(f"Removed member {element_guid} from external_reference {external_reference_guid}")


def remove_from_external_reference(self, external_reference_guid: str, element_guid: str,
                                   body: dict | DeleteRequestBody = None) -> None:
    """Remove an element from a external_reference. Async version.

    Parameters
    ----------
    external_reference_guid: str
        identity of the external_reference to return members for.
    element_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict, optional, defaults to None
        The body of the request to add to the external_reference. See notes.

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
    loop.run_until_complete(self._async_remove_from_external_reference(external_reference_guid, element_guid, body))

    #
    #
    #


def remove_term_from_category(self, folder_guid: str, term_guid: str,
                              body: dict | DeleteRequestBody = None) -> None:
    """Remove a term from a category.

    Parameters
    ----------
    category_guid: str
        identity of the external_reference to return members for.
    term_guid: str
        Effective time of the query. If not specified will default to any time.
    body: dict, optional, defaults to None
        The body of the request to add to the external_reference. See notes.

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
    loop.run_until_complete(self._async_remove_from_external_reference(folder_guid, term_guid, body))

    #
    #
    #


@dynamic_catch
async def _async_get_member_list(self, external_reference_guid: str = None, external_reference_name: str = None,
                                 external_reference_qname: str = None, ) -> list | str:
    """Get the member list for the external_reference - async version.
    Parameters
    ----------
    external_reference_guid: str,
       identity of the external_reference to return members for. If none, external_reference_name or
       external_reference_qname are used.
    external_reference_name: str,
       display name of the external_reference to return members for. If none, external_reference_guid
       or external_reference_qname are used.
    external_reference_qname: str,
       qualified name of the external_reference to return members for. If none, external_reference_guid
       or external_reference_name are used.

    Returns
    -------
    list | str
        The list of member information if successful, otherwise the string "No members found"

    Raises
    ------
    InvalidParameterException
        If the root_external_reference_name does not have exactly one root external_reference.

    """

    # first find the guid for the external_reference we are using as root

    # now find the members of the external_reference
    member_list = []
    members = await self._async_get_external_reference_members(external_reference_guid, external_reference_name,
                                                               external_reference_qname)
    if (type(members) is str) or (len(members) == 0):
        logger.trace(f"No members found for external_reference {external_reference_guid}")
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
    logger.debug(f"Member list for external_reference {external_reference_guid}: {member_list}")
    return member_list if len(member_list) > 0 else "No members found"


def get_member_list(self, external_reference_guid: str = None, external_reference_name: str = None,
                    external_reference_qname: str = None, ) -> list | bool:
    """Get the member list for a external_reference - async version.
    Parameters
    ----------
    external_reference_guid: str,
       identity of the external_reference to return members for. If none, external_reference_name or
       external_reference_qname are used.
    external_reference_name: str,
       display name of the external_reference to return members for. If none, external_reference_guid
       or external_reference_qname are used.
    external_reference_qname: str,
       qualified name of the external_reference to return members for. If none, external_reference_guid
       or external_reference_name are used.
    Returns
    -------
    list | bool
        The list of member information if successful, otherwise False.

    Raises
    ------
    InvalidParameterException
        If the root_external_reference_name does not have exactly one root external_reference.

    """
    loop = asyncio.get_event_loop()
    resp = loop.run_until_complete(
        self._async_get_member_list(external_reference_guid, external_reference_name, external_reference_qname))
    return resp





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


def _extract_external_reference_properties(self, element: dict, columns_struct: dict) -> dict:
    """
    Extract common properties from a external_reference element and populate into the provided columns_struct.

    Args:
        element (dict): The external_reference element
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
    # external_referenceCategories are classifications
    classification_names = ""
    classifications = element.get('elementHeader', {}).get("external_referenceCategories", [])
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


def _generate_external_reference_output(self, elements: dict | list[dict], filter: Optional[str],
                                        element_type_name: Optional[str], output_format: str = "DICT",
                                        output_format_set: dict | str = None) -> str | list[dict]:
    """ Generate output for external_references in the specified format.

        Args:
            elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
            filter (Optional[str]): The search string used to find the elements
            element_type_name (Optional[str]): The type of external_reference
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
    get_additional_props_func = None
    if output_format_set:
        if isinstance(output_format_set, str):
            output_formats = select_output_format_set(output_format_set, output_format)
        elif isinstance(output_format_set, dict):
            output_formats = get_output_format_type_match(output_format_set, output_format)

    # If no output_format was set, then use the element_type_name to lookup the output format
    elif element_type_name:
        output_formats = select_output_format_set(element_type_name, output_format)
    else:
        # fallback to external_references or entity type
        output_formats = select_output_format_set(entity_type, output_format)
    if output_formats is None:
        output_formats = select_output_format_set("Default", output_format)

    if output_formats:
        get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
        if isinstance(get_additional_props_name, str):
            class_name, method_name = get_additional_props_name.split(".")
            if hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)

    logger.trace(f"Executing generate_external_reference_output for {entity_type}: {output_formats}")
    return generate_output(
        elements,
        filter,
        entity_type,
        output_format,
        self._extract_external_reference_properties,
        get_additional_props_func,
        output_formats,
    )


from typing import Union, Dict, List, Optional

if __name__ == "__main__":
    print("Main-Collection Manager")
