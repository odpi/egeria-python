"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    The Template Manager OMVS provides APIs for managing metadata templates.
    Metadata templates are used to simplify the cataloguing of new metadata elements.

"""

import asyncio
from typing import Any, Optional
from pyegeria.core._server_client import ServerClient
from pyegeria.core._globals import default_time_out
from pyegeria.core.utils import dynamic_catch
from pyegeria.models import (NewRelationshipRequestBody, DeleteRelationshipRequestBody,
                             NewClassificationRequestBody, DeleteClassificationRequestBody)


class TemplateManager(ServerClient):
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
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
        time_out: int = default_time_out,
    ):
        self.view_server = view_server
        self.time_out = time_out
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token=token)
        self.command_root = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/template-manager"

    @dynamic_catch
    async def _async_link_sourced_from(self, element_guid: str, template_guid: str, body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a template to an element that was created from it.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the element created from the template.
        template_guid : str
            Unique identifier of the source template.
        body : dict | NewRelationshipRequestBody, optional
            Relationship details.

        Notes
        -----
        Sample JSON body:
        {
           "class" : "NewRelationshipRequestBody",
           "relationshipProperties" : {
             "class": "SourceFromProperties",
             "sourceVersionNumber" : 0
          },
           "externalSourceGUID": "Add guid here",
           "externalSourceName": "Add qualified name here",
           "forLineage": false,
           "forDuplicateProcessing": false,
           "effectiveTime" : "2024-01-01T00:00:00.000+00:00"
        }
        """
        url = f"{self.command_root}/elements/{element_guid}/sourced-from/{template_guid}/attach"
        await self._async_new_relationship_request(url, body=body)

    @dynamic_catch
    def link_sourced_from(self, element_guid: str, template_guid: str, body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a template to an element that was created from it."""
        return asyncio.get_event_loop().run_until_complete(self._async_link_sourced_from(element_guid, template_guid, body))

    @dynamic_catch
    async def _async_detach_sourced_from(self, element_guid: str, template_guid: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach the source template for an element.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the element.
        template_guid : str
            Unique identifier of the source template.
        body : dict | DeleteRelationshipRequestBody, optional
            Detachment details.
        """
        url = f"{self.command_root}/elements/{element_guid}/sourced-from/{template_guid}/detach"
        await self._async_delete_relationship_request(url, body=body)

    @dynamic_catch
    def detach_sourced_from(self, element_guid: str, template_guid: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach the source template for an element."""
        return asyncio.get_event_loop().run_until_complete(self._async_detach_sourced_from(element_guid, template_guid, body))

    @dynamic_catch
    async def _async_link_catalog_template(self, element_guid: str, template_guid: str, body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a template to an element that was created from it.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the parent element.
        template_guid : str
            Unique identifier of the catalog template.
        body : dict | NewRelationshipRequestBody, optional
            Relationship details.
        """
        url = f"{self.command_root}/elements/{element_guid}/catalog-template/{template_guid}/attach"
        await self._async_new_relationship_request(url, body=body)

    @dynamic_catch
    def link_catalog_template(self, element_guid: str, template_guid: str, body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a template to an element that was created from it."""
        return asyncio.get_event_loop().run_until_complete(self._async_link_catalog_template(element_guid, template_guid, body))

    @dynamic_catch
    async def _async_detach_catalog_template(self, element_guid: str, template_guid: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a template for an element that this template is relevant to.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the parent element.
        template_guid : str
            Unique identifier of the template.
        body : dict | DeleteRelationshipRequestBody, optional
            Detachment details.
        """
        url = f"{self.command_root}/elements/{element_guid}/catalog-template/{template_guid}/detach"
        await self._async_delete_relationship_request(url, body=body)

    @dynamic_catch
    def detach_catalog_template(self, element_guid: str, template_guid: str, body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a template for an element that this template is relevant to."""
        return asyncio.get_event_loop().run_until_complete(self._async_detach_catalog_template(element_guid, template_guid, body))

    @dynamic_catch
    async def _async_add_template_classification(self, element_guid: str, body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify an element as suitable to be used as a template for cataloguing elements of similar types.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the element to classify.
        body : dict | NewClassificationRequestBody, optional
            Classification details.
        """
        url = f"{self.command_root}/elements/{element_guid}/template"
        await self._async_new_classification_request(url, body=body)

    @dynamic_catch
    def add_template_classification(self, element_guid: str, body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify an element as suitable to be used as a template for cataloguing elements of similar types."""
        return asyncio.get_event_loop().run_until_complete(self._async_add_template_classification(element_guid, body))

    @dynamic_catch
    async def _async_remove_template_classification(self, element_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the Template classification from the element.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the element.
        body : dict | DeleteClassificationRequestBody, optional
            Declassification details.
        """
        url = f"{self.command_root}/elements/{element_guid}/template/remove"
        await self._async_delete_classification_request(url, body=body)

    @dynamic_catch
    def remove_template_classification(self, element_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the Template classification from the element."""
        return asyncio.get_event_loop().run_until_complete(self._async_remove_template_classification(element_guid, body))

    @dynamic_catch
    async def _async_add_template_substitute_classification(self, element_guid: str, body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify an element as suitable to be used as a template substitute for cataloguing elements of similar types.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the element to classify.
        body : dict | NewClassificationRequestBody, optional
            Classification details.
        """
        url = f"{self.command_root}/elements/{element_guid}/template-substitute"
        await self._async_new_classification_request(url, body=body)

    @dynamic_catch
    def add_template_substitute_classification(self, element_guid: str, body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify an element as suitable to be used as a template substitute for cataloguing elements of similar types."""
        return asyncio.get_event_loop().run_until_complete(self._async_add_template_substitute_classification(element_guid, body))

    @dynamic_catch
    async def _async_remove_template_substitute_classification(self, element_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the TemplateSubstitute classification from the element.
        Async version.

        Parameters
        ----------
        element_guid : str
            Unique identifier of the element.
        body : dict | DeleteClassificationRequestBody, optional
            Declassification details.
        """
        url = f"{self.command_root}/elements/{element_guid}/template-substitute/remove"
        await self._async_delete_classification_request(url, body=body)

    @dynamic_catch
    def remove_template_substitute_classification(self, element_guid: str, body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the TemplateSubstitute classification from the element."""
        return asyncio.get_event_loop().run_until_complete(self._async_remove_template_substitute_classification(element_guid, body))
