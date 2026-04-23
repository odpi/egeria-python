"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage platform security and governance zones in Egeria.

"""

import asyncio
import json
from typing import Optional, Union, Any

from pyegeria.core._server_client import ServerClient
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core._exceptions import PyegeriaNotFoundException
from pyegeria.models import (
    UserAccountRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
)
from pyegeria.core.utils import dynamic_catch


class SecurityOfficer(ServerClient):
    """
    Manage Security Officer operations in Egeria.

    This client provides methods to manage user accounts on Egeria platforms
    and define governance zone hierarchies.

    Parameters
    -----------
    view_server : str
        The name of the View Server to connect to.
    platform_url : str
        URL of the server platform to connect to.
    user_id : str
        Default user identity for calls (can be overridden per call).
    user_pwd : str, optional
        Password for the user_id. If a token is supplied, this may be None.
    token : str, optional
        Supply a token instead of using userId/password discovery.
    """

    def __init__(
        self,
        view_server: str = None,
        platform_url: str = None,
        user_id: str = None,
        user_pwd: Optional[str] = None,
        token: Optional[str] = None,
    ):
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token)
        self.security_officer_base_url = (
            f"{self.platform_url}/servers/{self.server_name}/api/open-metadata/security-officer"
        )

    async def __get_platform_guid__(self, platform_name: str) -> str:
        """Helper to look up platform GUID by name using inherited method."""
        platform_guid = await self._async_get_guid_for_name(
            platform_name,
            property_name=["displayName", "qualifiedName", "resourceName"],
        )
        if platform_guid == NO_ELEMENTS_FOUND:
            raise PyegeriaNotFoundException(f"Platform '{platform_name}' not found")
        return platform_guid

    @dynamic_catch
    async def _async_set_user_account(
        self, platform_name: str, body: Union[dict, Any], platform_guid: str = None
    ) -> None:
        """Create or update a user account in the platform metadata security connector. Async version.
        {
            "class": "UserAccountRequestBody",
            "userAccount": {
                "class": "OpenMetadataUserAccount",
                "userId": "{{accountUserId}}",
                "userName": "Freddie Mercury",
                "userAccountType": "EXTERNAL",
                "employeeNumber": "",
                "employeeType": "",
                "givenName": "Freddie",
                "surname": "Mercury",
                "email": "freddiemercury@queen.com",
                "securityRoles": ["serverOperator", "serverInvestigator"],
                "userAccountStatus": "CREDENTIALS_EXPIRED",
                "secrets": {
                    "clearPassword": "itsakindofmagic"
                }
            }
        """
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = f"{self.security_officer_base_url}/platforms/{platform_guid}/user-accounts"

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def set_user_account(
        self, platform_name: str, body: Union[dict, UserAccountRequestBody], platform_guid: str = None
    ) -> None:
        """Create or update a user account in the platform metadata security connector."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_set_user_account(platform_name, body, platform_guid))

    @dynamic_catch
    async def _async_get_user_account(self, platform_name: str, user_id: str, platform_guid: str = None) -> dict:
        """Return the user account object for the requested user. Async version."""
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = f"{self.security_officer_base_url}/platforms/{platform_guid}/user-accounts/{user_id}"
        response = await self._async_make_request("GET", url)
        if response:
            return response.json().get("userAccount")
        return None

    def get_user_account(self, platform_name: str, user_id: str, platform_guid: str = None) -> dict:
        """Return the user account object for the requested user."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_get_user_account(platform_name, user_id, platform_guid))

    @dynamic_catch
    async def _async_delete_user_account(self, platform_name: str, user_id: str, platform_guid: str = None) -> None:
        """Clear the account for a user with the platform security connector. Async version."""
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = f"{self.security_officer_base_url}/platforms/{platform_guid}/user-accounts/{user_id}"
        await self._async_make_request("DELETE", url)

    def delete_user_account(self, platform_name: str, user_id: str, platform_guid: str = None) -> None:
        """Clear the account for a user with the platform security connector."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_delete_user_account(platform_name, user_id, platform_guid))

    @dynamic_catch
    async def _async_link_governance_zones(
        self,
        governance_zone_guid: str,
        nested_governance_zone_guid: str,
        body: Union[dict, Any],
    ) -> None:
        """Attach a nested governance zone to a broader governance zone definition. Async version."""
        url = f"{self.security_officer_base_url}/governance-zones/{governance_zone_guid}/governance-zone-hierarchies/{nested_governance_zone_guid}/attach"

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def link_governance_zones(
        self,
        governance_zone_guid: str,
        nested_governance_zone_guid: str,
        body: Union[dict, NewRelationshipRequestBody],
    ) -> None:
        """Attach a nested governance zone to a broader governance zone definition."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_link_governance_zones(
                governance_zone_guid, nested_governance_zone_guid, body
            )
        )

    @dynamic_catch
    async def _async_detach_governance_zones(
        self,
        governance_zone_guid: str,
        nested_governance_zone_guid: str,
        body: Union[dict, Any],
    ) -> None:
        """Detach a governance zone definition from a hierarchical relationship. Async version."""
        url = f"{self.security_officer_base_url}/governance-zones/{governance_zone_guid}/governance-zone-hierarchies/{nested_governance_zone_guid}/detach"

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    def detach_governance_zones(
        self,
        governance_zone_guid: str,
        nested_governance_zone_guid: str,
        body: Union[dict, DeleteRelationshipRequestBody],
    ) -> None:
        """Detach a governance zone definition from a hierarchical relationship."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_detach_governance_zones(
                governance_zone_guid, nested_governance_zone_guid, body
            )
        )

    # =====================================================================
    # Security Access Controls
    # =====================================================================

    @dynamic_catch
    async def _async_set_security_access_control(
        self,
        platform_name: str,
        body: Union[dict, Any],
        platform_guid: str = None,
    ) -> None:
        """Set up or update a security access control in the platform metadata security connector.
        Async version.

        Parameters
        ----------
        platform_name : str
            Name of the platform to update (used to look up its GUID unless ``platform_guid``
            is provided directly).
        body : dict or SecurityAccessControlRequestBody
            Request body.  Expected shape::

                {
                    "class": "SecurityAccessControlRequestBody",
                    "securityAccessControl": {
                        "controlName": "<name>",
                        "displayName": "",
                        "description": "",
                        "controlTypeName": "",
                        "associatedSecurityList": {
                            "operationName": ["user1", "user2"]
                        },
                        "mappingProperties": {"property1": "value1"},
                        "securityLabels": [],
                        "securityProperties": {"property1": "value1"},
                        "otherProperties": {"property1": "value1"}
                    }
                }

        platform_guid : str, optional
            Pre-resolved GUID of the platform, bypassing the name lookup.
        """
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = f"{self.security_officer_base_url}/platforms/{platform_guid}/security-access-control"

        if hasattr(body, "model_dump_json"):
            payload = body.model_dump_json(exclude_none=True, by_alias=True)
        else:
            payload = json.dumps(body)

        await self._async_make_request("POST", url, payload)

    @dynamic_catch
    def set_security_access_control(
        self,
        platform_name: str,
        body: Union[dict, Any],
        platform_guid: str = None,
    ) -> None:
        """Set up or update a security access control in the platform metadata security connector.

        Parameters
        ----------
        platform_name : str
            Name of the platform to update.
        body : dict
            Request body.  See :meth:`_async_set_security_access_control` for the expected shape.
        platform_guid : str, optional
            Pre-resolved GUID of the platform, bypassing the name lookup.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_set_security_access_control(platform_name, body, platform_guid)
        )

    @dynamic_catch
    async def _async_get_security_access_control(
        self,
        platform_name: str,
        control_name: str,
        platform_guid: str = None,
    ) -> Optional[dict]:
        """Return the named security access control object from the platform metadata security
        connector.  Returns ``None`` if no matching control has been set up.  Async version.

        Parameters
        ----------
        platform_name : str
            Name of the platform to query.
        control_name : str
            Name of the security access control to retrieve.
        platform_guid : str, optional
            Pre-resolved GUID of the platform, bypassing the name lookup.
        """
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = (
            f"{self.security_officer_base_url}/platforms/{platform_guid}"
            f"/security-access-control/{control_name}"
        )
        response = await self._async_make_request("GET", url)
        if response:
            return response.json().get("securityAccessControl")
        return None

    @dynamic_catch
    def get_security_access_control(
        self,
        platform_name: str,
        control_name: str,
        platform_guid: str = None,
    ) -> Optional[dict]:
        """Return the named security access control object from the platform metadata security
        connector.  Returns ``None`` if no matching control has been set up.

        Parameters
        ----------
        platform_name : str
            Name of the platform to query.
        control_name : str
            Name of the security access control to retrieve.
        platform_guid : str, optional
            Pre-resolved GUID of the platform, bypassing the name lookup.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_get_security_access_control(platform_name, control_name, platform_guid)
        )

    @dynamic_catch
    async def _async_delete_security_access_control(
        self,
        platform_name: str,
        control_name: str,
        platform_guid: str = None,
    ) -> None:
        """Clear the named security access control from the platform security connector.
        Async version.

        Parameters
        ----------
        platform_name : str
            Name of the platform to update.
        control_name : str
            Name of the security access control to remove.
        platform_guid : str, optional
            Pre-resolved GUID of the platform, bypassing the name lookup.
        """
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = (
            f"{self.security_officer_base_url}/platforms/{platform_guid}"
            f"/security-access-control/{control_name}"
        )
        await self._async_make_request("DELETE", url)

    @dynamic_catch
    def delete_security_access_control(
        self,
        platform_name: str,
        control_name: str,
        platform_guid: str = None,
    ) -> None:
        """Clear the named security access control from the platform security connector.

        Parameters
        ----------
        platform_name : str
            Name of the platform to update.
        control_name : str
            Name of the security access control to remove.
        platform_guid : str, optional
            Pre-resolved GUID of the platform, bypassing the name lookup.
        """
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            self._async_delete_security_access_control(platform_name, control_name, platform_guid)
        )
