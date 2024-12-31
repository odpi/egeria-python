"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

Template manager is a view service that supports managing metadata elements using templates.

"""
import asyncio

from requests import Response

from pyegeria import (
    Client,
    max_paging_size,
    body_slimmer,
    InvalidParameterException,
    default_time_out,
)


class TemplateManager(Client):
    """Client to issue Template Manager requests.

    Attributes:

        view_server : str
                Name of the server to use.
        platform_url : str
            URL of the server platform to connect to
        user_id : str
            The identity of the user calling the method - this sets a default optionally used by the methods
            when the user doesn't pass the user_id on a method call.
        user_pwd: str
            The password associated with the user_id. Defaults to None
        token: str, optional
            Bearer token

    Methods:

    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: str = None,
        token: str = None,
        time_out: int = default_time_out,
    ):
        self.view_server = view_server
        self.time_out = time_out
        Client.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)
        self.command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/template-manager"

    #
    #   Maintain the metadata elements that makes up the template
    #
    async def _async_create_metadata_element_in_store(self, body: dict) -> str:
        """Create a new metadata element in the metadata store.  The type name comes from the open metadata types.
        The selected type also controls the names and types of the properties that are allowed.
        This version of the method allows access to advanced features such as multiple states and
        effectivity dates. Async version.

        Parameters
        ----------
        body : dict
            The definition of the element to create. A sample is below.

        Returns
        -------
           str: If successful, the GUID of the element created; otherwise None is returned.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        =====

        Example of the body:

        {
          "class" : "NewOpenMetadataElementRequestBody",
          "externalSourceGUID" : "666",
          "externalSourceName" : "radio1",
          "typeName" : "",
          "initialStatus" : "ACTIVE",
          "initialClassifications" : {},
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "properties" : {},
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """

        url = f"{self.command_root}/metadata-elements"
        response = await self._async_make_request("POST", url, body_slimmer(body))
        guid = response.json().get("guid", None)
        return guid

    def create_metadata_element_in_store(self, body: dict) -> str:
        """Create a new metadata element in the metadata store.  The type name comes from the open metadata types.
        The selected type also controls the names and types of the properties that are allowed.
        This version of the method allows access to advanced features such as multiple states and
        effectivity dates.

        Parameters
        ----------
        body : dict
            The definition of the element to create. A sample is below.

        Returns
        -------
           str: If successful, the GUID of the element created; otherwise None is returned.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        =====

        Example of the body:

        {
          "class" : "NewOpenMetadataElementRequestBody",
          "externalSourceGUID" : "666",
          "externalSourceName" : "radio1",
          "typeName" : "",
          "initialStatus" : "ACTIVE",
          "initialClassifications" : {},
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "properties" : {},
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_metadata_element_in_store(body)
        )
        return response

    async def _async_create_metadata_element_from_template(self, body: dict) -> str:
        """Create a new metadata element in the metadata store using a template.  The type name comes from the
        open metadata types. The selected type also controls the names and types of the properties that are allowed.
        Async version.

        Parameters
        ----------
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "TemplateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "typeName" : "",
          "templateGUID" : "",
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "replacementProperties" : { },
          "placeholderProperties" : {
             "placeholderName1" : "placeholderValue1",
             "placeholderName2" : "placeholderValue2"
          },
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/from-templates"

        response = await self._async_make_request("POST", url, body_slimmer(body))
        guid = response.json().get("guid", None)
        return guid

    def create_metadata_element_from_template(self, body: dict) -> str:
        """Create a new metadata element in the metadata store using a template.  The type name comes from the
        open metadata types. The selected type also controls the names and types of the properties that are allowed.

        Parameters
        ----------
        body : dict
            dict containing the definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_metadata_element_from_template(body)
        )
        return response

    async def _async_update_metadata_element_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Update the properties of a specific metadata element.  The properties must match the type definition
        associated with the metadata element when it was created.  However, it is possible to update a few
        properties, or replace all them by the value used in the replaceProperties flag.
        Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "TemplateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "typeName" : "",
          "templateGUID" : "",
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "replacementProperties" : { },
          "placeholderProperties" : {
             "placeholderName1" : "placeholderValue1",
             "placeholderName2" : "placeholderValue2"
          },
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/update-properties"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_metadata_element_in_store(self, element_guid: str, body: dict) -> None:
        """Update the properties of a specific metadata element.  The properties must match the type definition
        associated with the metadata element when it was created.  However, it is possible to update a few
        properties, or replace all them by the value used in the replaceProperties flag.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "TemplateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "typeName" : "",
          "templateGUID" : "",
          "anchorGUID" : "",
          "isOwnAnchor" : false,
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "replacementProperties" : { },
          "placeholderProperties" : {
             "placeholderName1" : "placeholderValue1",
             "placeholderName2" : "placeholderValue2"
          },
          "parentGUID" : "",
          "parentRelationshipTypeName" : "",
          "parentRelationshipProperties" : {},
          "parentAtEnd1" : true,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_metadata_element_in_store(element_guid, body)
        )
        return

    async def _async_update_metadata_element_status_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Update the status of a specific metadata element. The new status must match a status value that is defined
        for the element's type assigned when it was created. Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateStatusRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/update-status"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_metadata_element_status_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Update the status of a specific metadata element. The new status must match a status value that is defined
        for the element's type assigned when it was created.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateStatusRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_metadata_element_status_in_store(element_guid, body)
        )
        return

    async def _async_update_metadata_element_effectivity_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Update the effectivity dates control the visibility of the element through specific APIs.
            Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/update-effectivity"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_metadata_element_effectivity_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Update the effectivity dates control the visibility of the element through specific APIs.
            Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_metadata_element_effectivity_in_store(element_guid, body)
        )
        return

    async def _async_delete_metadata_element_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Delete a metadata element.
            Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/delete"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def delete_metadata_element_in_store(self, element_guid: str, body: dict) -> None:
        """Delete a metadata element.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_metadata_element_in_store(element_guid, body)
        )
        return

    async def _async_archive_metadata_element_in_store(
        self, element_guid: str, body: dict
    ) -> None:
        """Archive a specific metadata element.
            Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "ArchiveRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "archiveProperties" : {
            "archiveDate" : "{{$isoTimestamp}}",
            "archiveProcess" : "",
            "archiveProperties": {
               "propertyName1" : "propertyValue1",
               "propertyName2" : "propertyValue2"
            }
          },
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/archive"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def archive_metadata_element_in_store(self, element_guid: str, body: dict) -> None:
        """Archive a specific metadata element.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

          "class" : "ArchiveRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "archiveProperties" : {
            "archiveDate" : "{{$isoTimestamp}}",
            "archiveProcess" : "",
            "archiveProperties": {
               "propertyName1" : "propertyValue1",
               "propertyName2" : "propertyValue2"
            }
          },
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_archive_metadata_element_in_store(element_guid, body)
        )
        return

    async def _async_classify_metadata_element_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Add a new classification to the metadata element.  Note that only one classification with the same name can
            be attached to a metadata element. Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification : str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "NewClassificationRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/classifications/{classification}"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def classify_metadata_element_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Add a new classification to the metadata element.  Note that only one classification with the same name can
            be attached to a metadata element.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification : str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "NewClassificationRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_classify_metadata_element_in_store(
                element_guid, classification, body
            )
        )
        return

    async def _async_reclassify_metadata_element_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Update the properties of a classification that is currently attached to a specific metadata element.
            Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification: str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/classifications/{classification}/update-properties"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def reclassify_metadata_element_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Update the properties of a classification that is currently attached to a specific metadata element.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification: str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }

        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_reclassify_metadata_element_in_store(
                element_guid, classification, body
            )
        )
        return

    async def _async_update_classification_effectivity_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Update the effectivity dates of a specific classification attached to a metadata element.
            The effectivity dates control the visibility of the classification through specific APIs.
            Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification: str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/classifications/{classification}/update-effectivity"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_classification_effectivity_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Update the effectivity dates of a specific classification attached to a metadata element.
            The effectivity dates control the visibility of the classification through specific APIs.


        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification: str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_classification_effectivity_in_store(
                element_guid, classification, body
            )
        )
        return

    async def _async_declassify_metadata_element_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Remove the named classification from a specific metadata element. Async version.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification: str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        url = f"{self.command_root}/metadata-elements/{element_guid}/classifications/{classification}/delete"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def declassify_metadata_element_in_store(
        self, element_guid: str, classification: str, body: dict
    ) -> None:
        """Remove the named classification from a specific metadata element.

        Parameters
        ----------
        element_guid : str
            The identity of the metadata element to update.
        classification: str
            The classification name to apply.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_declassify_metadata_element_in_store(
                element_guid, classification, body
            )
        )
        return

    async def _async_create_related_elements_in_store(self, body: dict) -> str:
        """Create a relationship between two metadata elements.  It is important to put the right element at each end
            of the relationship according to the type definition since this will affect how the relationship is
            interpreted. Async version.

        Parameters
        ----------
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           str containing the relationship GUID.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "NewRelatedElementsRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
          "typeName": "string",
          "metadataElement1GUID": "string",
          "metadataElement2GUID": "string",
        }
        """
        url = f"{self.command_root}/related-elements"
        response = await self._async_make_request("POST", url, body_slimmer(body))
        guid = response.json().get("guid", None)
        return guid

    def create_related_elements_in_store(self, body: dict) -> str:
        """Create a relationship between two metadata elements.  It is important to put the right element at each end
            of the relationship according to the type definition since this will affect how the relationship is
            interpreted.

        Parameters
        ----------
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           str containing the relationship GUID.

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "NewRelatedElementsRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
          "typeName": "string",
          "metadataElement1GUID": "string",
          "metadataElement2GUID": "string",
        }
        """
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(
            self._async_create_related_elements_in_store(body)
        )
        return response

    async def _async_update_related_elements_in_store(
        self, relationship_guid: str, body: dict
    ) -> None:
        """Update the properties associated with a relationship. Async version.

        Parameters
        ----------
        relationship_guid : str
            The identity of the relationship to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "typeName": "string",
          "metadataElement1GUID": "string",
          "metadataElement2GUID": "string",
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        url = f"{self.command_root}/related-elements/{relationship_guid}/update-properties"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_related_elements_in_store(
        self, relationship_guid: str, body: dict
    ) -> None:
        """Update the properties associated with a relationship. Async version.

        Parameters
        ----------
        relationship_guid : str
            The identity of the relationship to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdatePropertiesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "typeName": "string",
          "metadataElement1GUID": "string",
          "metadataElement2GUID": "string",
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_related_elements_in_store(relationship_guid, body)
        )
        return

    async def _async_update_related_elements_effectivity_in_store(
        self, relationship_guid: str, body: dict
    ) -> None:
        """Update the effectivity dates of a specific relationship between metadata elements.
            The effectivity dates control the visibility of the classification through specific APIs.
            Async version.

        Parameters
        ----------
        relationship_guid : str
            The identity of the relationship to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        url = f"{self.command_root}/metadata-elements/related-elements/{relationship_guid}/update-effectivity"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def update_related_elements_effectivity_in_store(
        self, relationship_guid: str, body: dict
    ) -> None:
        """Update the effectivity dates of a specific relationship between metadata elements.
            The effectivity dates control the visibility of the classification through specific APIs.

        Parameters
        ----------
        relationship_guid : str
            The identity of the relationship to update.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateEffectivityDatesRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "effectiveFrom" : "{{$isoTimestamp}}",
          "effectiveTo": "{{$isoTimestamp}}",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_update_related_elements_effectivity_in_store(
                relationship_guid, body
            )
        )
        return

    async def _async_delete_related_elements_in_store(
        self, relationship_guid: str, body: dict
    ) -> None:
        """Delete a relationship between two metadata elements. Async version.

        Parameters
        ----------
        relationship_guid : str
            The identity of the relationship to delete.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        url = f"{self.command_root}/metadata-elements/related-elements/{relationship_guid}/delete"
        await self._async_make_request("POST", url, body_slimmer(body))
        return

    def delete_related_elements_in_store(
        self, relationship_guid: str, body: dict
    ) -> None:
        """Delete a relationship between two metadata elements.

        Parameters
        ----------
        relationship_guid : str
            The identity of the relationship to delete.
        body : dict
            The definition of the element to create. A sample is the notes below.

        Returns
        -------
           None

        Raises
        ------
        InvalidParameterException
        PropertyServerException
        UserNotAuthorizedException

        Notes
        -----
        Example of the body:

        {
          "class" : "UpdateRequestBody",
          "externalSourceGUID" :  "",
          "externalSourceName" : "",
          "forLineage" : false,
          "forDuplicateProcessing" : false,
          "effectiveTime" : "{{$isoTimestamp}}"
        }
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_delete_related_elements_in_store(relationship_guid, body)
        )
        return


if __name__ == "__main__":
    print("Main-Template Manager")
