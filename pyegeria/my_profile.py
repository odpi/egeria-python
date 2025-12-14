"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the MyProfile class and its methods.

"""

import asyncio

from pyegeria._server_client import ServerClient
from pyegeria.models import NewElementRequestBody
from pyegeria.utils import dynamic_catch


class MyProfile(ServerClient):
    """A class representing the profile of a user.

    This class provides methods for retrieving the profile details
    of a user associated with a token.

    Parameters
    ----------
    view_server : str
        The name of the view server to configure.
    platform_url : str
        The URL of the platform.
    token : str, optional
        The token associated with the user. Default is None.
    user_id : str, optional
        The user ID. Default is None.
    user_pwd : str, optional
        The user password. Default is None.

    """

    def __init__(
                self,
                view_server: str,
                platform_url: str,
                user_id: str = None,
                user_pwd: str = None,
                token: str = None,
                ):
        ServerClient.__init__(
            self,
            view_server,
            platform_url,
            user_id=user_id,
            user_pwd=user_pwd,
            token=token,
        )
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd

        self.my_profile_command_root: str = f"{platform_url}/servers"

    #
    #       MyProfile
    #

    @dynamic_catch
    async def _async_create_action(self, body: dict | NewElementRequestBody = None) -> str:
        """ Create a new $el_name$. Async version.

        Parameters
        ----------

        body: dict | NewElementRequestBody, optional
            A dict or NewElementRequestBody representing the details of the $el_name$ to create.
        Returns
        -------
        str - the guid of the created $el_name$

        Raises
        ------
        PyegeriaException
            One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
            Egeria errors.
        ValidationError
            Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
        PyegeriaNotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action

        Notes:
        -----
        simple:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "effectiveFrom": "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "properties": {
            "class" : "ActorProfileProperties",
            "typeName" : "enter the type of the element",
            "qualifiedName": "add unique name here",
            "displayName": "add short name here",
            "description": "add description here",
            "additionalProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
            "extendedProperties": {
              "property1" : "propertyValue1",
              "property2" : "propertyValue2"
            },
        }

        """

        url = f"{self.command_root}/actor-profiles"
        return await self._async_create_element_body_request(url, ["ActorProfileProperties"], body)

    @dynamic_catch
    def create_action(self, body: dict | NewElementRequestBody = None) -> str:

        """ Create a new $el_name$.

               Parameters
               ----------
               body: dict | NewElementRequestBody, optional
                   A dict or NewElementRequestBody representing the details of the $el_name$ to create.
               Returns
               -------
               str - the guid of the created $el_name$

               Raises
               ------
               PyegeriaException
                   One of the pyegeria exceptions will be raised if there are issues in communications, message format, or
                   Egeria errors.
               ValidationError
                   Pydantic validation errors are raised if the body does not conform to the NewElementRequestBody.
               PyegeriaUnAuthorizedException
                 The principle specified by the user_id does not have authorization for the requested action

               Notes:
               -----
               example:
               {
                 "class": "NewElementRequestBody",
                 "isOwnAnchor": true,
                 "effectiveFrom": "{{$isoTimestamp}}",
                 "effectiveTo": "{{$isoTimestamp}}",
                 "properties": {
                   "class" : "ActorProfileProperties",
                   "typeName" : "enter the type of the element",
                   "qualifiedName": "add unique name here",
                   "displayName": "add short name here",
                   "description": "add description here",
                   "additionalProperties": {
                     "property1" : "propertyValue1",
                     "property2" : "propertyValue2"
                   },
                   "extendedProperties": {
                     "property1" : "propertyValue1",
                     "property2" : "propertyValue2"
                   },
               }

           """

    return asyncio.get_event_loop().run_until_complete(self._async_create_action(body))


#######

@dynamic_catch
async def create_async_$


el_type$_profile_from_template(self, body: TemplateRequestBody | dict) -> str:
""" Create a new metadata element to represent a $el_name$ using an existing metadata element as a template.
    The template defines additional classifications and relationships that should be added to the new element.
    Async version.

Parameters
----------
body: dict
    A dict representing the details of the $el_name$ to create.

Returns
-------
str - the guid of the created $el_name$

Raises
------
PyegeriaInvalidParameterException
  If the client passes incorrect parameters on the request - such as bad URLs or invalid values
PyegeriaAPIException
  Raised by the server when an issue arises in processing a valid request
PyegeriaUnAuthorizedException
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
url = f"{self.command_root}/actor-profiles/from-template"

return await self._async_create_element_from_template("POST", url, body)


@dynamic_catch
def create_$


el_type$_profile_from_template(self, body: dict) -> str:
""" Create a new metadata element to represent a $el_name$ using an existing metadata element as a template.
    The template defines additional classifications and relationships that should be added to the new element.
    Async version.

Parameters
----------
body: dict
    A dict representing the details of the $el_name$ to create.

Returns
-------
str - the guid of the created $el_name$

Raises
------
PyegeriaInvalidParameterException
  If the client passes incorrect parameters on the request - such as bad URLs or invalid values
PyegeriaAPIException
  Raised by the server when an issue arises in processing a valid request
PyegeriaUnAuthorizedException
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
resp = loop.run_until_complete(self._async_Action_from_template(body))
return resp


@dynamic_catch
async def _async_update_actor_profile(self, actor_profile_guid: str,
                                      body: dict | UpdateElementRequestBody) -> None:
    """ Update the properties of an $el_name$.
        Collections: https://egeria-project.org/concepts/actor_profile

        Async version.
    Parameters
    ----------
    actor_profile_guid: str
        The guid of the $el_name$ to update.

    body: dict | UpdateElementRequestBody, optional
        A dict or NewElementRequestBody representing the details of the $el_name$ to create.

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
    PyegeriaUnAuthorizedException
      The principle specified by the user_id does not have authorization for the requested action

    Notes:
    -----
    example:
    {
      "class" : "UpdateElementRequestBody",
      "properties": {
        "class" : "CollectionProperties",
        "qualifiedName": "Must provide a unique name here",
        "name" : "Add display name here",
        "description" : "Add description of the $el_name$ here",
        "category": "Add appropriate valid value for type"
      },
      "externalSourceGUID": "add guid here",
      "externalSourceName": "add qualified name here",
      "effectiveTime" : "{{$isoTimestamp}}",
      "forLineage" : false,
      "forDuplicateProcessing" : false
    }
    """

    url = (f"{self.command_root}/actor-profiles/{actor_profile_guid}/update")
    await self._async_update_element_body_request(url, ["ActorProfileProperties"], body)


@dynamic_catch
def update_actor_profile(self, actor_profile_guid: str, body: dict | UpdateElementRequestBody) -> None:
    """ Update the properties of an $el_name$.
        Collections: https://egeria-project.org/concepts/actor_profile

    Parameters
    ----------
    actor_profile_guid: str
        The guid of the $el_name$ to update.

    body: dict | UpdateElementRequestBody, optional
        A dict or NewElementRequestBody representing the details of the $el_name$ to create.

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
    PyegeriaUnAuthorizedException
      The principle specified by the user_id does not have authorization for the requested action

    Notes:
    -----
    example:
    {
      "class" : "UpdateElementRequestBody",
      "properties": {
        "class" : "CollectionProperties",
        "qualifiedName": "Must provide a unique name here",
        "name" : "Add display name here",
        "description" : "Add description of the $el_name$ here",
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
        self._async_update_actor_profile(actor_profile_guid, body))


@dynamic_catch
async def _async_link_actor_profile(self, asset_guid: str, profile_guid: str,
                                    body: dict | NewRelationshipRequestBody = None) -> None:
    """ Attach an asset to an IT .
        Async version.

    Parameters
    ----------
    element_guid: str
        The unique identifier of the element.
    ext_ref_guid: str
        The identifier of the external reference.
    body: dict | NewRelationshipRequestBody, optional, default = None
        A structure representing the details of the relationship.

    Returns
    -------
    Nothing

    Raises
    ------
    PyegeriaInvalidParameterException
      If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    PyegeriaAPIException
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
        "class": "ExternalReferenceLinkProperties",",
        "label": "add label here",
        "description": "add description here",
        "effectiveFrom": "{{$isoTimestamp}}",
        "effectiveTo": "{{$isoTimestamp}}"
      }
    }

    """

    url = url = (f"{self.command_root}/elements/{element_guid}/external-references/{ext_ref_guid}/attach")
    await self._async_new_relationship_request(url, "ExternalReferenceLinkProperties", body)
    logger.info(f"Linking element {element_guid} to ext. ref.  {ext_ref_guid}")


@dynamic_catch
def link_actor_profile(self, element_guid: str, ext_ref_guid: str,
                       body: dict | NewRelationshipRequestBody = None):
    """ Attach an element to an external reference.

        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        ext_ref_guid: str
            The identifier of the external reference.
        body: dict | NewRelationshipRequestBody, optional, default = None
            A structure representing the details of the relationship.

        Returns
        -------
        Nothing

        Raises
        ------
        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
            "class": "ExternalReferenceLinkProperties",",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self._async_link_actor_profile(element_guid, ext_ref_guid, body))


@dynamic_catch
async def _async_detach_actor_profile(self, element_guid: str, ext_ref_guid: str,
                                      body: dict | DeleteRelationshipRequestBody = None) -> None:
    """ Detach an element from an external reference; body is optional. Async version.

    Parameters
    ----------
    element_guid: str
        The unique identifier of the subscriber.
    ext_ref_guid: str
        The unique identifier of the subscription.
    body: dict | DeleteRelationshipRequestBody, optional, default = None
        A structure representing the details of the relationship.

    Returns
    -------
    Nothing

    Raises
    ------
    PyegeriaInvalidParameterException
      If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    PyegeriaAPIException
      Raised by the server when an issue arises in processing a valid request
    NotAuthorizedException
      The principle specified by the user_id does not have authorization for the requested action

    Notes
    -----
    JSON Structure looks like:
    {
      "class": "DeleteRelationshipRequestBody",
      "externalSourceGUID": "add guid here",
      "externalSourceName": "add qualified name here",
      "effectiveTime": "{{$isoTimestamp}}",
      "forLineage": false,
      "forDuplicateProcessing": false
    }
    """
    url = (f"{self.command_root}/elements/{element_guid}/actor_profiles/{ext_ref_guid}/detach")

    await self._async_delete_element_request(url, body)
    logger.info(f"Detached element {element_guid} from external reference {ext_ref_guid}")


def detach_actor_profile(self, element_guid: str, ext_ref_guid: str, body: dict | DeleteRelationshipRequestBody = None):
    """ Detach an element from an external reference. Request body is optional.

    Parameters
    ----------
    element_guid: str
        The unique identifier of the subscriber.
    ext_ref_guid: str
        The unique identifier of the subscription.
    body: dict, optional, default = None
        A dict representing the details of the relationship.

    Returns
    -------
    Nothing

    Raises
    ------
    PyegeriaInvalidParameterException
      If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    PyegeriaAPIException
      Raised by the server when an issue arises in processing a valid request
    NotAuthorizedException
      The principle specified by the user_id does not have authorization for the requested action

    Notes
    -----
    JSON Structure looks like:
    {
      "class": "DeleteRelationshipRequestBody",
      "externalSourceGUID": "add guid here",
      "externalSourceName": "add qualified name here",
      "effectiveTime": "{{$isoTimestamp}}",
      "forLineage": false,
      "forDuplicateProcessing": false
    }
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self._async_detach_actor_profile(element_guid, ext_ref_guid, body))


@dynamic_catch
async def _async_delete_actor_profile(self, ext_ref_guid: str,
                                      body: dict | DeleteRelationshipRequestBody = None,
                                      cascade: bool = False) -> None:
    """ Delete an external reference. Async Version.

    Parameters
    ----------
    ext_ref_guid: str
        The guid of the governance definition to delete.

    cascade: bool, optional, defaults to True
        If true, a cascade delete is performed.

    body: dict DeleteRelationshipRequestBodyt, optional, default = None
        A dict representing the details of the relationship.

    Returns
    -------
    Nothing

    Raises
    ------
    PyegeriaInvalidParameterException
      If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    ValidationException
      Raised by pydantic when the request body is invalid.
    NotAuthorizedException
      The principle specified by the user_id does not have authorization for the requested action

    Notes
    _____
    JSON Structure looks like:
    {
      "class" : "DeleteRelationshipRequestBody",
      "externalSourceGUID": "add guid here",
      "externalSourceName": "add qualified name here",
      "effectiveTime" : "{{$isoTimestamp}}",
      "forLineage" : false,
      "forDuplicateProcessing" : false
    }
    """
    url = f"{self.command_root}/external-references/{ext_ref_guid}/delete"

    await self._async_delete_element_request(url, body, cascade)
    logger.info(f"Deleted collection {ext_ref_guid} with cascade {cascade}")


@dynamic_catch
def delete_actor_profile(self, ext_ref_guid: str, body: dict | DeleteElementRequestBody = None,
                         cascade: bool = False) -> None:
    """Delete an external reference..

    Parameters
    ----------
    ext_ref_guid: str
        The guid of the external reference to delete.

    cascade: bool, optional, defaults to True
        If true, a cascade delete is performed.

    body: dict DeleteElementRequestBody, optional, default = None
        A dict representing the details of the relationship.

    Returns
    -------
    Nothing

    Raises
    ------
    PyegeriaInvalidParameterException
      If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    ValidationException
      Raised by pydantic when the request body is invalid.
    NotAuthorizedException
      The principle specified by the user_id does not have authorization for the requested action

    Notes
    _____
    JSON Structure looks like:
    {
      "class" : "DeleteElementRequestBody",
      "externalSourceGUID": "add guid here",
      "externalSourceName": "add qualified name here",
      "effectiveTime" : "{{$isoTimestamp}}",
      "forLineage" : false,
      "forDuplicateProcessing" : false
    }
    """
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self._async_delete_actor_profile(ext_ref_guid, body, cascade))


@dynamic_catch
async def _async_find_actor_profiles(self, search_string: str = "*", classification_names: list[str] = None,
                                     metadata_element_subtypes: list[str] = actor_profile_TYPES,
                                     starts_with: bool = True, ends_with: bool = False,
                                     ignore_case: bool = False,
                                     start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                     report_spec: str | dict = "ExternalReference",
                                     body: dict | SearchStringRequestBody = None) -> list | str:
    """ Returns the list of external references matching the search string filtered by the optional classification.
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
    metadata_element_subtypes: list[str], optional, default=None
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
    report_spec: str | dict , optional, default = None
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
    url = str(HttpUrl(f"{self.command_root}/external-references/by-search-string"))
    response = await self._async_find_request(url, _type="ExternalReference",
                                              _gen_output=self._generate_actor_profile_output,
                                              search_string=search_string,
                                              include_only_classification_names=classification_names,
                                              metadata_element_subtypes=metadata_element_subtypes,
                                              starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                              start_from=start_from, page_size=page_size, output_format=output_format,
                                              report_spec=report_spec, body=body)

    return response


@dynamic_catch
def find_actor_profiles(self, search_string: str = '*', classification_names: str = None,
                        metadata_element_subtypes: list[str] = actor_profile_TYPES, starts_with: bool = True,
                        ends_with: bool = False, ignore_case: bool = False,
                        start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                        report_spec: str | dict = "ExternalReference",
                        body: dict | SearchStringRequestBody = None) -> list | str:
    """ Returns the list of external references matching the search string filtered by the optional classification.
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
    metadata_element_subtypes: list[str], optional, default=None
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
    report_spec: str | dict , optional, default = None
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
        metadata_element_subtypes ():

    """
    return asyncio.get_event_loop().run_until_complete(
        self._async_find_actor_profiles(search_string, classification_names, metadata_element_subtypes, starts_with,
                                        ends_with, ignore_case, start_from, page_size, output_format, report_spec,
                                        body))


@dynamic_catch
async def _async_get_actor_profiles_by_name(self, filter_string: str = None,
                                            classification_names: list[str] = None,
                                            body: dict | FilterRequestBody = None,
                                            start_from: int = 0, page_size: int = 0,
                                            output_format: str = 'JSON',
                                            report_spec: str | dict = "ExternalReference") -> list | str:
    """ Returns the list of external references with a particular name.

        Parameters
        ----------
        filter_string: str,
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
        report_spec: dict , optional, default = None
            The desired output columns/fields to include.

        Returns
        -------
        List | str

        A list of collections match matching the name. Returns a string if none found.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
          Raised by the server when an issue arises in processing a valid request
        NotAuthorizedException
          The principle specified by the user_id does not have authorization for the requested action
    """
    url = str(HttpUrl(f"{self.command_root}/external-references/by-name"))
    response = await self._async_get_name_request(url, _type="ExternalReference",
                                                  _gen_output=self._generate_actor_profile_output,
                                                  filter_string=filter_string,
                                                  classification_names=classification_names,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, report_spec=report_spec,
                                                  body=body)

    return response


def get_actor_profiles_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                               body: dict | FilterRequestBody = None,
                               start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                               report_spec: str | dict = "ExternalReference") -> list | str:
    """Returns the list of external references matching the filter string. Async version.
        The search string is located in the request body and is interpreted as a plain string.
        The request parameters, startsWith, endsWith, and ignoreCase can be used to allow a fuzzy search.

    Parameters
    ----------
    filter_string: str,
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
     report_spec: str | dict, optional, default = None
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
        self._async_get_actor_profiles_by_name(filter_string, classification_names, body, start_from,
                                               page_size,
                                               output_format, report_spec))


@dynamic_catch
async def _async_get_actor_profile_by_guid(self, ext_ref_guid: str, element_type: str = None,
                                           body: dict | GetRequestBody = None,
                                           output_format: str = 'JSON',
                                           report_spec: str | dict = "ExternalReference") -> dict | str:
    """Return the properties of a specific external reference. Async version.

    Parameters
    ----------
    ext_ref_guid: str,
        unique identifier of the external reference to retrieve.
    element_type: str, default = None, optional
         type of externak reference ExternalReference, RelatedMedia, etc.
    body: dict | GetRequestBody, optional, default = None
        full request body.
    output_format: str, default = "JSON"
        - one of "DICT", "MERMAID" or "JSON"
     report_spec: str | dict, optional, default = None
            The desired output columns/fields to include.

    Returns
    -------
    dict | str

    A JSON dict representing the specified collection. Returns a string if none found.

    Raises
    ------

    PyegeriaInvalidParameterException
      If the client passes incorrect parameters on the request - such as bad URLs or invalid values
    PyegeriaAPIException
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

    url = str(HttpUrl(f"{self.command_root}/external-references/{ext_ref_guid}/retrieve"))
    type = element_type if element_type else "ExternalReference"

    response = await self._async_get_guid_request(url, _type=type,
                                                  _gen_output=self._generate_actor_profile_output,
                                                  output_format=output_format, report_spec=report_spec,
                                                  body=body)

    return response


@dynamic_catch
def get_actor_profile_by_guid(self, ext_ref_guid: str, element_type: str = None,
                              body: dict | GetRequestBody = None,
                              output_format: str = 'JSON',
                              report_spec: str | dict = "ExternalReference") -> dict | str:
    """ Return the properties of a specific external reference. Async version.

        Parameters
        ----------
        ext_ref_guid: str,
            unique identifier of the external reference to retrieve.
        element_type: str, default = None, optional
            type of element - ExternalReference, RelatedMedia, etc.
        body: dict | GetRequestBody, optional, default = None
            full request body.
        output_format: str, default = "JSON"
            - one of "DICT", "MERMAID" or "JSON"
        report_spec: dict , optional, default = None
            The desired output columns/fields to include.


        Returns
        -------
        dict | str

        A JSON dict representing the specified collection. Returns a string if none found.

        Raises
        ------

        PyegeriaInvalidParameterException
          If the client passes incorrect parameters on the request - such as bad URLs or invalid values
        PyegeriaAPIException
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
        self._async_get_actor_profile_by_guid(ext_ref_guid, element_type, body,
                                              output_format, report_spec))


@dynamic_catch
def _extract_actor_profile_properties(self, element: dict, columns_struct: dict) -> dict:
    """
    Extract common properties from a actor_profile element and populate into the provided columns_struct.

    Args:
        element (dict): The actor_profile element
        columns_struct (dict): The columns structure to populate

    Returns:
        dict: columns_struct with column 'value' fields populated
    """
    # First, populate from element.properties using the utility
    col_data = populate_columns_from_properties(element, columns_struct)

    columns_list = col_data.get("formats", {}).get("attributes", [])

    # Populate header-derived values
    header_props = _extract_referenceable_properties(element)
    for column in columns_list:
        key = column.get('key')
        if key in header_props:
            column['value'] = header_props.get(key)
        elif isinstance(key, str) and key.lower() == 'guid':
            column['value'] = header_props.get('GUID')

    # Derived/computed fields
    # actor_profileCategories are classifications
    classification_names = ""
    classifications = element.get('elementHeader', {}).get("actor_profileCategories", [])
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


@dynamic_catch
def _generate_actor_profile_output(self, elements: dict | list[dict], filter: Optional[str],
                                   element_type_name: Optional[str], output_format: str = "DICT",
                                   report_spec: dict | str = None) -> str | list[dict]:
    """ Generate output for actor_profiles in the specified format.

        Args:
            elements (Union[Dict, List[Dict]]): Dictionary or list of dictionaries containing data field elements
            filter (Optional[str]): The search string used to find the elements
            element_type_name (Optional[str]): The type of actor_profile
            output_format (str): The desired output format (MD, FORM, REPORT, LIST, DICT, MERMAID, HTML)
            report_spec (Optional[dict], optional): List of dictionaries containing column data. Defaults
            to None.

        Returns:
            Union[str, List[Dict]]: Formatted output as a string or list of dictionaries
    """
    if element_type_name is None:
        entity_type = "ExternalReference"
    else:
        entity_type = element_type_name
    # First see if the user has specified an report_spec - either a label or a dict
    get_additional_props_func = None
    if report_spec:
        if isinstance(report_spec, str):
            output_formats = select_report_spec(report_spec, output_format)
        elif isinstance(report_spec, dict):
            output_formats = get_report_spec_match(report_spec, output_format)

    # If no output_format was set, then use the element_type_name to lookup the output format
    elif element_type_name:
        output_formats = select_report_spec(element_type_name, output_format)
    else:
        # fallback to actor_profiles or entity type
        output_formats = select_report_spec(entity_type, output_format)
    if output_formats is None:
        output_formats = select_report_spec("Default", output_format)

    if output_formats:
        get_additional_props_name = output_formats.get("get_additional_props", {}).get("function", None)
        if isinstance(get_additional_props_name, str):
            class_name, method_name = get_additional_props_name.split(".")
            if hasattr(self, method_name):
                get_additional_props_func = getattr(self, method_name)

    logger.trace(f"Executing generate_actor_profile_output for {entity_type}: {output_formats}")
    return generate_output(
        elements,
        filter,
        entity_type,
        output_format,
        self._extract_actor_profile_properties,
        get_additional_props_func,
        output_formats,
    )


if __name__ == "__main__":
    print("Main-My Profile")
