"""
PDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module contains the People Organizer View Service client.
"""

import asyncio
from typing import Annotated, Literal, Optional

from pydantic import Field

from pyegeria.core._server_client import ServerClient
from pyegeria.models import (
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    RelationshipBeanProperties,
)
from pyegeria.core.utils import dynamic_catch


class TeamStructureProperties(RelationshipBeanProperties):
    class_: Annotated[Literal["TeamStructureProperties"], Field(alias="class")]
    delegation_escalation_authority: Optional[bool] = True


class PeopleOrganizer(ServerClient):
    """
    Client for the People Organizer View Service.

    The People Organizer View Service provides methods to manage person profiles and teams.

    Attributes
    ----------
    view_server : str
        The name of the View Server to use.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        The identity of the user calling the method.
    user_pwd : str
        The password associated with the user_id. Defaults to None.
    """

    def __init__(
        self,
        view_server: str,
        platform_url: str,
        user_id: str,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        super().__init__(view_server, platform_url, user_id, user_pwd, token)
        self.view_server = view_server
        self.platform_url = platform_url
        self.user_id = user_id
        self.user_pwd = user_pwd
        self.url_marker = "people-organizer"

    @dynamic_catch
    async def _async_link_peer_person(
        self,
        person_one_guid: str,
        person_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link a person profile to one of its peers. Async version.

        Parameters
        ----------
        person_one_guid : str
            The unique identifier of the first person profile.
        person_two_guid : str
            The unique identifier of the second person profile.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class": "NewRelationshipRequestBody",
          "properties": {
            "class": "PeerProperties",
            "effectiveFrom": "2024-01-01T00:00:00.000+00:00"
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/people-organizer/actor-profiles/{person_one_guid}/peer-persons/{person_two_guid}/attach"
        await self._async_new_relationship_request(url, ["PeerProperties"], body)

    def link_peer_person(
        self,
        person_one_guid: str,
        person_two_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link a person profile to one of its peers.

        Parameters
        ----------
        person_one_guid : str
            The unique identifier of the first person profile.
        person_two_guid : str
            The unique identifier of the second person profile.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "RelationshipProperties",
            "effectiveFrom": "2024-01-01T00:00:00.000+00:00"
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_peer_person(person_one_guid, person_two_guid, body)
        )

    @dynamic_catch
    async def _async_unlink_peer_person(
        self,
        person_one_guid: str,
        person_two_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach a person profile from one of its peers. Async version.

        Parameters
        ----------
        person_one_guid : str
            The unique identifier of the first person profile.
        person_two_guid : str
            The unique identifier of the second person profile.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/people-organizer/actor-profiles/{person_one_guid}/peer-persons/{person_two_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_peer_person(
        self,
        person_one_guid: str,
        person_two_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach a person profile from one of its peers.

        Parameters
        ----------
        person_one_guid : str
            The unique identifier of the first person profile.
        person_two_guid : str
            The unique identifier of the second person profile.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_unlink_peer_person(person_one_guid, person_two_guid, body)
        )

    @dynamic_catch
    async def _async_link_team_structure(
        self,
        super_team_guid: str,
        subteam_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link a super team to a subteam. Async version.

        Parameters
        ----------
        super_team_guid : str
            The unique identifier of the super team.
        subteam_guid : str
            The unique identifier of the subteam.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "TeamStructureProperties",
            "delegationEscalationAuthority": true
          }
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/people-organizer/actor-profiles/{super_team_guid}/team-structures/{subteam_guid}/attach"
        await self._async_new_relationship_request(url, ["TeamStructureProperties"], body)

    def link_team_structure(
        self,
        super_team_guid: str,
        subteam_guid: str,
        body: dict | NewRelationshipRequestBody,
    ) -> None:
        """Link a super team to a subteam.

        Parameters
        ----------
        super_team_guid : str
            The unique identifier of the super team.
        subteam_guid : str
            The unique identifier of the subteam.
        body : dict | NewRelationshipRequestBody
            The properties for the relationship.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "NewRelationshipRequestBody",
          "properties": {
            "class": "TeamStructureProperties",
            "delegationEscalationAuthority": true
          }
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_link_team_structure(super_team_guid, subteam_guid, body)
        )

    @dynamic_catch
    async def _async_detach_team_structure(
        self,
        super_team_guid: str,
        subteam_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach a super team from a subteam. Async version.

        Parameters
        ----------
        super_team_guid : str
            The unique identifier of the super team.
        subteam_guid : str
            The unique identifier of the subteam.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE"
        }
        ```
        """
        url = f"{self.platform_url}/servers/{self.view_server}/api/open-metadata/people-organizer/actor-profiles/{super_team_guid}/team-structures/{subteam_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    def detach_team_structure(
        self,
        super_team_guid: str,
        subteam_guid: str,
        body: dict | DeleteRelationshipRequestBody,
    ) -> None:
        """Detach a super team from a subteam.

        Parameters
        ----------
        super_team_guid : str
            The unique identifier of the super team.
        subteam_guid : str
            The unique identifier of the subteam.
        body : dict | DeleteRelationshipRequestBody
            The request body for the detach operation.

        Returns
        -------
        None

        Raises
        ------
        PyegeriaException
            If there are issues in communications, message format, or Egeria errors.

        Notes
        -----
        Sample JSON body:
        ```json
        {
          "class" : "DeleteRelationshipRequestBody",
          "deleteMethod": "LOOK_FOR_LINEAGE"
        }
        ```
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            self._async_detach_team_structure(super_team_guid, subteam_guid, body)
        )
