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
                             UpdateElementRequestBody, NewRelationshipRequestBody,
                             DeleteRequestBody)
from pyegeria.output_formatter import (generate_output,
                                       _extract_referenceable_properties, populate_columns_from_properties,
                                       get_required_relationships)
from pyegeria.utils import dynamic_catch

app_settings = settings
EGERIA_LOCAL_QUALIFIER = app_settings.User_Profile.egeria_local_qualifier
EXTERNAL_REFERENCE_PROPS = ["ExternalReferenceProperties", "ExternalDataSourceProperties",
                            "ExternalModelSourceProperties",
                            "RelatedMediaProperties", "CitedDocumentProperties"]

EXTERNAL_REFERENCE_TYPES = ["ExternalReference", "ExternalDataSource", "ExternalModelSource",
                            "RelatedMedia", "CitedDocument"]
from pyegeria._client_new import Client2


class ExternalReferences(Client2):
    """
    Establish linkage to external references which can be a variety of artifacts. Including media,
    documents, data, and more. Keep in mind that there are several sub-types of external references, each
    with their own property body. This includes:
    
    * ExternalReferenceProperties
    * ExternalDataSourceProperties
    * ExternalModelSourceProperties
    * RelatedMediaProperties
    * CitedDocumentProperties

    Review the documentation on the website for more details.
    
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

    For related media use this properties body:
        {
          "class": "NewElementRequestBody",
          "isOwnAnchor": true,
          "properties": {
            "class": "RelatedMediaProperties",
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
            "mediaType": "Add media type here",
            "mediaTypeOtherId": "Add media type other id here",
            "defaultMediaUsage": "Add default media usage here",
            "defaultMediaUsageOtherId": "Add default media usage other id here",
          }
        }

        See https://egeria-project.org/types/0/0015-Linked-Media-Types/ for more information on media types and 
        valid values.

    """

        url = f"{self.command_root}/external-references"
        return await self._async_create_element_body_request(url, EXTERNAL_REFERENCE_PROPS, body)

    @dynamic_catch
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
                 "referenceTitle": "Add reference title here",
                 "referenceAbstract": "Add reference abstract here",
                 "authors": ["Add author names here"],
                 "url": "Add url here",
                 "sources": "Add sources here",
                 "license": "Add license here",
                 "copyright": "Add copyright here",
                 "attribution": "Add attribution here"
               }
             }

              For related media use this properties body:
            {
              "class": "NewElementRequestBody",
              "isOwnAnchor": true,
              "properties": {
                "class": "RelatedMediaProperties",
                "qualifiedName": "Must provide a unique name here",
                "name": "Add display name here",
                "description": "Add description of the external_reference here",
                "category": "Add appropriate valid value for type",
                "referenceTitle": "Add reference title here",
                "referenceAbstract": "Add reference abstract here",
                "authors": ["Add author names here"],
                "url": "Add url here",
                "sources": "Add sources here",
                 "license": "Add license here",
                 "copyright": "Add copyright here",
                 "attribution": "Add attribution here",
                "datePublished": "2023-01-01",
                "dateConnected": "2023-01-01",
                "dateCreated": "2023-01-01",
                "mediaType": "Add media type here",
                "mediaTypeOtherId": "Add media type other id here",
                "defaultMediaUsage": "Add default media usage here",
                "defaultMediaUsageOtherId": "Add default media usage other id here",
              }
            }

            For CitedDocument use this properties body:
            {
              "class": "NewElementRequestBody",
              "isOwnAnchor": true,
              "properties": {
                "class": "CitedDocumentProperties",
                "qualifiedName": "Must provide a unique name here",
                "name": "Add display name here",
                "description": "Add description of the external_reference here",
                "category": "Add appropriate valid value for type",
                "numberOfPates": int,
                "pageRange": "Add page range here",
                "publicationSeries": "Add publication series here",
                "publicationSeriesVolume": "Add publication series volume here",
                "publisher": "Add publisher here",
                "edition": "Add edition here",
                "firstPublicationDate": "2023-01-01",
                "publicationDate": "2023-01-01",
                "publicationCity": "Add publication city here",
                "publicationYear": "publication year",
                "publicationNumbers": ["string"],
                "defaultMediaUsage": "Add default media usage here",
                "defaultMediaUsageOtherId": "Add default media usage other id here",
                "referenceTitle": "Add reference title here",
                "referenceAbstract": "Add reference abstract here",
                "authors": ["Add author names here"],
                "url": "Add url here",
                "sources": "Add sources here",
                 "license": "Add license here",
                 "copyright": "Add copyright here",
                 "attribution": "Add attribution here"
              }
            }

        See https://egeria-project.org/types/0/0015-Linked-Media-Types/ for more information on media types and 
        valid values.


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

        url = f"{self.command_root}/external-references/from-template"
        json_body = validated_body.model_dump_json(indent=2, exclude_none=True)
        logger.info(json_body)
        resp = await self._async_make_request("POST", url, json_body, is_json=True)
        logger.info(f"Create external_reference from template with GUID: {resp.json().get('guid')}")
        return resp.json().get("guid", NO_GUID_RETURNED)

    @dynamic_catch
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

        url = (f"{self.command_root}/external-references/{external_reference_guid}/update")
        await self._async_update_element_body_request(url, EXTERNAL_REFERENCE_PROPS, body)

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

    @dynamic_catch
    async def _async_link_external_reference(self, element_guid: str, ext_ref_guid: str,
                                             body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach an element to an external reference.
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
            "class": "ExternalReferenceLinkProperties",",
            "label": "add label here",
            "description": "add description here",
            "effectiveFrom": "{{$isoTimestamp}}",
            "effectiveTo": "{{$isoTimestamp}}"
          }
        }
        {{baseURL}}/servers/{{viewServer}}/api/open-metadata/external-references/elements/660bfc21-12b5-4de1-a8f3-63239fbb58a0/external-references/850ffe6c-c551-497b-9b7a-6efcadcf2c88/attach
        `https://localhost:9443/servers/qs-view-server/api/open-metadata/external-references/elements/660bfc21-12b5-4de1-a8f3-63239fbb58a0/external_references/850ffe6c-c551-497b-9b7a-6efcadcf2c88/attach
        """

        url = url = (f"{self.command_root}/elements/{element_guid}/external-references/{ext_ref_guid}/attach")
        await self._async_new_relationship_request(url, "ExternalReferenceLinkProperties", body)
        logger.info(f"Linking element {element_guid} to ext. ref.  {ext_ref_guid}")

    @dynamic_catch
    def link_external_reference(self, element_guid: str, ext_ref_guid: str,
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
                "class": "ExternalReferenceLinkProperties",",
                "label": "add label here",
                "description": "add description here",
                "effectiveFrom": "{{$isoTimestamp}}",
                "effectiveTo": "{{$isoTimestamp}}"
              }
            }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_external_reference(element_guid, ext_ref_guid, body))

    @dynamic_catch
    async def _async_detach_external_reference(self, element_guid: str, ext_ref_guid: str,
                                               body: dict | DeleteRequestBody = None) -> None:
        """ Detach an element from an external reference; body is optional. Async version.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the subscriber.
        ext_ref_guid: str
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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (f"{self.command_root}/elements/{element_guid}/external_references/{ext_ref_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(f"Detached element {element_guid} from external reference {ext_ref_guid}")

    def detach_external_reference(self, element_guid: str, ext_ref_guid: str, body: dict | DeleteRequestBody = None):
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
        loop.run_until_complete(self._async_detach_external_reference(element_guid, ext_ref_guid, body))

    @dynamic_catch
    async def _async_link_media_reference(self, element_guid: str, media_ref_guid: str,
                                          body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach an element to a related media reference.
            Async version.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        media_ref_guid: str
            The identifier of the external media reference.
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
                    "class": "CitedDocumentProperties",
                    "qualifiedName": "Must provide a unique name here",
                    "name": "Add display name here",
                    "description": "Add description of the external_reference here",
                    "category": "Add appropriate valid value for type",
                    "numberOfPates": int,
                    "pageRange": "Add page range here",
                    "publicationSeries": "Add publication series here",
                    "publicationSeriesVolume": "Add publication series volume here",
                    "publisher": "Add publisher here",
                    "edition": "Add edition here",
                    "firstPublicationDate": "2023-01-01",
                    "publicationDate": "2023-01-01",
                    "publicationCity": "Add publication city here",
                    "publicationYear": "publication year",
                    "publicationNumbers": ["string"],
                    "defaultMediaUsage": "Add default media usage here",
                    "defaultMediaUsageOtherId": "Add default media usage other id here",
                    "referenceTitle": "Add reference title here",
                    "referenceAbstract": "Add reference abstract here",
                    "authors": ["Add author names here"],
                    "url": "Add url here",
                    "sources": "Add sources here",
                     "license": "Add license here",
                     "copyright": "Add copyright here",
                     "attribution": "Add attribution here"
                  }
        }
        """
        url = f"{self.command_root}/elements/{element_guid}/media-references/{media_ref_guid}/attach"
        await self._async_new_relationship_request(url, "MediaReferenceProperties", body)
        logger.info(f"Linking element {element_guid} to media reference  {media_ref_guid}")

    @dynamic_catch
    def link_media_reference(self, element_guid: str, media_ref_guid: str,
                             body: dict | NewRelationshipRequestBody = None):
        """ Attach an element to an external media reference.
    
            Parameters
            ----------
            element_guid: str
                The unique identifier of the element.
            media_ref_guid: str
                The identifier of the external reference.
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
                    "class": "CitedDocumentProperties",
                    "qualifiedName": "Must provide a unique name here",
                    "name": "Add display name here",
                    "description": "Add description of the external_reference here",
                    "category": "Add appropriate valid value for type",
                    "numberOfPates": int,
                    "pageRange": "Add page range here",
                    "publicationSeries": "Add publication series here",
                    "publicationSeriesVolume": "Add publication series volume here",
                    "publisher": "Add publisher here",
                    "edition": "Add edition here",
                    "firstPublicationDate": "2023-01-01",
                    "publicationDate": "2023-01-01",
                    "publicationCity": "Add publication city here",
                    "publicationYear": "publication year",
                    "publicationNumbers": ["string"],
                    "defaultMediaUsage": "Add default media usage here",
                    "defaultMediaUsageOtherId": "Add default media usage other id here",
                    "referenceTitle": "Add reference title here",
                    "referenceAbstract": "Add reference abstract here",
                    "authors": ["Add author names here"],
                    "url": "Add url here",
                    "sources": "Add sources here",
                     "license": "Add license here",
                     "copyright": "Add copyright here",
                     "attribution": "Add attribution here"
                  }
             }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_media_reference(element_guid, media_ref_guid, body))

    @dynamic_catch
    async def _async_detach_media_reference(self, element_guid: str, media_ref_guid: str,
                                            body: dict | DeleteRequestBody = None) -> None:
        """ Detach an element from an external media reference; body is optional. Async version.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the subscriber.
        media_ref_guid: str
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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = (
            f"{self.command_root}/elements/{element_guid}/media-references/{media_ref_guid}/detach")

        await self._async_delete_request(url, body)
        logger.info(f"Detached element {element_guid} from external media reference {media_ref_guid}")

    @dynamic_catch
    def detach_media_reference(self, element_guid: str, media_ref_guid: str, body: dict | DeleteRequestBody = None):
        """ Detach an element from an external media reference. Request body is optional.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the subscriber.
        media_ref_guid: str
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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_media_reference(element_guid, media_ref_guid, body))

    @dynamic_catch
    async def _async_link_cited_document(self, element_guid: str, cited_doc_guid: str,
                                         body: dict | NewRelationshipRequestBody = None) -> None:
        """ Attach an element to a cited document reference.
            Async version.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the element.
        cited_doc_guid: str
            The identifier of the external cited document reference.
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
                    "class": "CitedDocumentLinkProperties",
                    "referenceId": "add reference id here",
                    "description": "Add description of the external_reference here",
                    "pages": "Add pages here"
                  }
        }
        """
        url = f"{self.command_root}/elements/{element_guid}/cited-document-references/{cited_doc_guid}/attach"
        await self._async_new_relationship_request(url, "CitedDocumentLinkProperties", body)
        logger.info(f"Linking element {element_guid} to cited document  {cited_doc_guid}")

    @dynamic_catch
    def link_cited_document(self, element_guid: str, cited_doc_guid: str,
                            body: dict | NewRelationshipRequestBody = None):
        """ Attach an element to an external media reference.
    
            Parameters
            ----------
            element_guid: str
                The unique identifier of the element.
            cited_doc_guid: str
                The identifier of the external reference.
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
                    "class": "CitedDocumentLinkProperties",
                    "referenceId": "add reference id here",
                    "description": "Add description of the external_reference here",
                    "pages": "Add pages here"
                  }
             }
            """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_link_cited_document(element_guid, cited_doc_guid, body))

    @dynamic_catch
    async def _async_detach_cited_document(self, element_guid: str, cited_doc_guid: str,
                                           body: dict | DeleteRequestBody = None) -> None:
        """ Detach an element from an cited document reference; body is optional. Async version.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the subscriber.
        cited_doc_guid: str
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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        url = f"{self.command_root}/elements/{element_guid}/cited-document-references/{cited_doc_guid}/detach"

        await self._async_delete_request(url, body)
        logger.info(f"Detached element {element_guid} from cited document reference {cited_doc_guid}")

    @dynamic_catch
    def detach_cited_document(self, element_guid: str, cited_doc_guid: str, body: dict | DeleteRequestBody = None):
        """ Detach an element from acited document reference. Request body is optional.
    
        Parameters
        ----------
        element_guid: str
            The unique identifier of the subscriber.
        cited_doc_guid: str
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
          "class": "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime": "{{$isoTimestamp}}",
          "forLineage": false,
          "forDuplicateProcessing": false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_detach_cited_document(element_guid, cited_doc_guid, body))

    #
    # do deletes etc
    #
    @dynamic_catch
    async def _async_delete_external_reference(self, ext_ref_guid: str,
                                               body: dict | DeleteRequestBody = None,
                                               cascade: bool = False) -> None:
        """ Delete an external reference. Async Version.
    
        Parameters
        ----------
        ext_ref_guid: str
            The guid of the governance definition to delete.
    
        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.
    
        body: dict DeleteRequestBodyt, optional, default = None
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
          "class" : "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        url = f"{self.command_root}/external-references/{ext_ref_guid}/delete"

        await self._async_delete_request(url, body, cascade)
        logger.info(f"Deleted collection {ext_ref_guid} with cascade {cascade}")

    @dynamic_catch
    def delete_external_reference(self, ext_ref_guid: str, body: dict | DeleteRequestBody = None,
                                  cascade: bool = False) -> None:
        """Delete an external reference..
    
        Parameters
        ----------
        ext_ref_guid: str
            The guid of the external reference to delete.
    
        cascade: bool, optional, defaults to True
            If true, a cascade delete is performed.
    
        body: dict DeleteRequestBody, optional, default = None
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
          "class" : "DeleteRequestBody",
          "externalSourceGUID": "add guid here",
          "externalSourceName": "add qualified name here",
          "effectiveTime" : "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_delete_external_reference(ext_ref_guid, body, cascade))

    @dynamic_catch
    async def _async_find_external_references(self, search_string: str = "*", classification_names: list[str] = None,
                                              metadata_element_types: list[str] = EXTERNAL_REFERENCE_TYPES,
                                              starts_with: bool = True, ends_with: bool = False,
                                              ignore_case: bool = False,
                                              start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                              output_format_set: str | dict = "ExternalReference",
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
        url = str(HttpUrl(f"{self.command_root}/external-references/by-search-string"))
        response = await self._async_find_request(url, _type="ExternalReference", search_string=search_string,
                                                  _gen_output=self._generate_external_reference_output,
                                                  classification_names=classification_names,
                                                  metadata_element_types=metadata_element_types,
                                                  starts_with=starts_with, ends_with=ends_with, ignore_case=ignore_case,
                                                  start_from=start_from, page_size=page_size,
                                                  output_format=output_format, output_format_set=output_format_set,
                                                  body=body)

        return response

    @dynamic_catch
    def find_external_references(self, search_string: str = '*', classification_names: str = None,
                                 metadata_element_types: list[str] = EXTERNAL_REFERENCE_TYPES, starts_with: bool = True,
                                 ends_with: bool = False, ignore_case: bool = False,
                                 start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                 output_format_set: str | dict = "ExternalReference",
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
                                                     output_format_set: str | dict = "ExternalReference") -> list | str:
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
        url = str(HttpUrl(f"{self.command_root}/external-references/by-name"))
        response = await self._async_get_name_request(url, _type="Collection",
                                                      _gen_output=self._generate_external_reference_output,
                                                      filter_string=filter_string,
                                                      classification_names=classification_names,
                                                      start_from=start_from, page_size=page_size,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    def get_external_references_by_name(self, filter_string: str = None, classification_names: list[str] = None,
                                        body: dict | FilterRequestBody = None,
                                        start_from: int = 0, page_size: int = 0, output_format: str = 'JSON',
                                        output_format_set: str | dict = "ExternalReference") -> list | str:
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
            self._async_get_external_references_by_name(filter_string, classification_names, body, start_from,
                                                        page_size,
                                                        output_format, output_format_set))

    @dynamic_catch
    async def _async_get_external_reference_by_guid(self, ext_ref_guid: str, element_type: str = None,
                                                    body: dict | GetRequestBody = None,
                                                    output_format: str = 'JSON',
                                                    output_format_set: str | dict = "ExternalReference") -> dict | str:
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

        url = str(HttpUrl(f"{self.command_root}/external-references/{ext_ref_guid}/retrieve"))
        type = element_type if element_type else "ExternalReference"

        response = await self._async_get_guid_request(url, _type=type,
                                                      _gen_output=self._generate_external_reference_output,
                                                      output_format=output_format, output_format_set=output_format_set,
                                                      body=body)

        return response

    @dynamic_catch
    def get_external_reference_by_guid(self, ext_ref_guid: str, element_type: str = None,
                                       body: dict | GetRequestBody = None,
                                       output_format: str = 'JSON',
                                       output_format_set: str | dict = "ExternalReference") -> dict | str:
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
            self._async_get_external_reference_by_guid(ext_ref_guid, element_type, body,
                                                       output_format, output_format_set))

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
            entity_type = "ExternalReference"
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
