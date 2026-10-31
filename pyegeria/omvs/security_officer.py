"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

    Manage platform security and governance zones in Egeria.

"""

import asyncio
import json
import uuid
from typing import Optional, Union, Any

from pyegeria.core._server_client import ServerClient
from pyegeria.core._globals import NO_ELEMENTS_FOUND
from pyegeria.core._exceptions import PyegeriaNotFoundException
from pyegeria.models import (
    UserAccountRequestBody,
    NewElementRequestBody,
    TemplateRequestBody,
    UpdateElementRequestBody,
    DeleteElementRequestBody,
    FilterRequestBody,
    GetRequestBody,
    NewRelationshipRequestBody,
    DeleteRelationshipRequestBody,
    NewClassificationRequestBody,
    DeleteClassificationRequestBody,
    SearchStringRequestBody,
    ControlImplementationStatus,
)
from pyegeria.core.utils import dynamic_catch
from pyegeria.core.async_runner import run_sync


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
        timeout: int = None):
        ServerClient.__init__(self, view_server, platform_url, user_id, user_pwd, token, timeout=timeout)
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
        return run_sync(self._async_set_user_account(platform_name, body, platform_guid))

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
        return run_sync(self._async_get_user_account(platform_name, user_id, platform_guid))

    @dynamic_catch
    async def _async_delete_user_account(self, platform_name: str, user_id: str, platform_guid: str = None) -> None:
        """Clear the account for a user with the platform security connector. Async version."""
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = f"{self.security_officer_base_url}/platforms/{platform_guid}/user-accounts/{user_id}"
        await self._async_make_request("DELETE", url)

    def delete_user_account(self, platform_name: str, user_id: str, platform_guid: str = None) -> None:
        """Clear the account for a user with the platform security connector."""
        return run_sync(self._async_delete_user_account(platform_name, user_id, platform_guid))

    @dynamic_catch
    async def _async_get_user_list(
        self,
        platform_name: str,
        status: str = None,
        user_type: str = None,
        platform_guid: str = None,
    ) -> list[str]:
        """Return the list of users registered with the platform security connector. Async version.

        Parameters
        ----------
        platform_name : str
            Name of the platform to query.
        status : str, optional
            Status of the user - or null for any status.
        user_type : str, optional
            Type of user - or null for any type.
        platform_guid : str, optional
            Pre-resolved GUID of the platform.
        """
        if not platform_guid:
            platform_guid = await self.__get_platform_guid__(platform_name)
        url = f"{self.security_officer_base_url}/platforms/{platform_guid}/user-accounts"
        params = {}
        if status:
            params["status"] = status
        if user_type:
            params["type"] = user_type

        response = await self._async_make_request("GET", url, params=params)
        if response:
            return response.json().get("names", [])
        return []

    def get_user_list(
        self,
        platform_name: str,
        status: str = None,
        user_type: str = None,
        platform_guid: str = None,
    ) -> list[str]:
        """Return the list of users registered with the platform security connector."""
        return run_sync(
            self._async_get_user_list(platform_name, status, user_type, platform_guid)
        )

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
        return run_sync(
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
        return run_sync(
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
        return run_sync(
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
        return run_sync(
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
        return run_sync(
            self._async_delete_security_access_control(platform_name, control_name, platform_guid)
        )

    # =====================================================================
    # Security Roles and Groups
    # =====================================================================

    @dynamic_catch
    async def _async_find_security_roles(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "SecurityRole",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SecurityRole",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the list of security roles matching the search string. Async version."""
        url = f"{self.security_officer_base_url}/collections/by-search-string"
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        return await self._async_find_request(
            url,
            _type="SecurityRole",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    def find_security_roles(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "SecurityRole",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SecurityRole",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the list of security roles matching the search string."""
        return run_sync(
            self._async_find_security_roles(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_find_security_groups(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "SecurityGroup",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SecurityGroup",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the list of security groups matching the search string. Async version."""
        url = f"{self.security_officer_base_url}/collections/by-search-string"
        params = {
            "search_string": search_string,
            "starts_with": starts_with,
            "ends_with": ends_with,
            "ignore_case": ignore_case,
            "metadata_element_type": metadata_element_type_name,
            "metadata_element_subtypes": metadata_element_subtypes,
            "include_only_relationships": include_only_relationships,
            "skip_relationships": skip_relationships,
            "graph_query_depth": graph_query_depth,
            "as_of_time": as_of_time,
            "start_from": start_from,
            "page_size": page_size,
            "sequencing_order": sequencing_order,
            "sequencing_property": sequencing_property,
            "output_format": output_format,
            "report_spec": report_spec,
            "body": body,
        }
        params.update(kwargs)
        params = {k: v for k, v in params.items() if v is not None or k == "search_string"}

        return await self._async_find_request(
            url,
            _type="SecurityGroup",
            _gen_output=self._generate_referenceable_output,
            **params,
        )

    def find_security_groups(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = "SecurityGroup",
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = "SecurityGroup",
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the list of security groups matching the search string."""
        return run_sync(
            self._async_find_security_groups(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    #
    # Relationship and classification maintenance - added to close the gap
    # found by scripts/omvs_audit.py against the security-officer .http
    # ground truth (2026-08-21).
    #

    @dynamic_catch
    async def _async_link_resource_permissions(self, secrets_collection_guid: str, security_access_control_guid: str,
                                                body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a security access control to a secrets collection it grants permission for (ResourcePermissions relationship). Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/resource-permissions/{security_access_control_guid}/attach"
        await self._async_new_relationship_request(url, ["ResourcePermissionsProperties"], body)

    @dynamic_catch
    def link_resource_permissions(self, secrets_collection_guid: str, security_access_control_guid: str,
                                  body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a security access control to a secrets collection it grants permission for (ResourcePermissions relationship)."""
        run_sync(self._async_link_resource_permissions(secrets_collection_guid, security_access_control_guid, body))

    @dynamic_catch
    async def _async_detach_resource_permissions(self, secrets_collection_guid: str, security_access_control_guid: str,
                                                  body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a security access control from a secrets collection. Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/resource-permissions/{security_access_control_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def detach_resource_permissions(self, secrets_collection_guid: str, security_access_control_guid: str,
                                    body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a security access control from a secrets collection."""
        run_sync(self._async_detach_resource_permissions(secrets_collection_guid, security_access_control_guid, body))

    @dynamic_catch
    async def _async_link_secrets_collection_security_list(self, secrets_collection_guid: str, security_list_guid: str,
                                                            body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a security list to a secrets collection it governs (SecretsCollectionSecurityList relationship). Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/security-lists/{security_list_guid}/attach"
        await self._async_new_relationship_request(url, ["SecretsCollectionSecurityListProperties"], body)

    @dynamic_catch
    def link_secrets_collection_security_list(self, secrets_collection_guid: str, security_list_guid: str,
                                               body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a security list to a secrets collection it governs (SecretsCollectionSecurityList relationship)."""
        run_sync(self._async_link_secrets_collection_security_list(secrets_collection_guid, security_list_guid, body))

    @dynamic_catch
    async def _async_detach_secrets_collection_security_list(self, secrets_collection_guid: str, security_list_guid: str,
                                                              body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a security list from a secrets collection. Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/security-lists/{security_list_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def detach_secrets_collection_security_list(self, secrets_collection_guid: str, security_list_guid: str,
                                                 body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a security list from a secrets collection."""
        run_sync(self._async_detach_secrets_collection_security_list(secrets_collection_guid, security_list_guid, body))

    @dynamic_catch
    async def _async_link_user_account(self, secrets_collection_guid: str, user_identity_guid: str,
                                       body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a user identity to a secrets collection holding its account secrets (UserAccount relationship). Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/user-accounts/{user_identity_guid}/attach"
        await self._async_new_relationship_request(url, ["UserAccountProperties"], body)

    @dynamic_catch
    def link_user_account(self, secrets_collection_guid: str, user_identity_guid: str,
                          body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Attach a user identity to a secrets collection holding its account secrets (UserAccount relationship)."""
        run_sync(self._async_link_user_account(secrets_collection_guid, user_identity_guid, body))

    @dynamic_catch
    async def _async_detach_user_account(self, secrets_collection_guid: str, user_identity_guid: str,
                                         body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a user identity from a secrets collection. Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/user-accounts/{user_identity_guid}/detach"
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def detach_user_account(self, secrets_collection_guid: str, user_identity_guid: str,
                            body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Detach a user identity from a secrets collection."""
        run_sync(self._async_detach_user_account(secrets_collection_guid, user_identity_guid, body))

    @dynamic_catch
    async def _async_set_user_account_profile(self, secrets_collection_guid: str,
                                              body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a secrets collection with its user account profile statistics. Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/user-account-profile"
        if body is None:
            body = {"class": "NewClassificationRequestBody", "properties": {"class": "UserAccountProfileProperties"}}
        await self._async_new_classification_request(url, ["UserAccountProfileProperties"], body)

    @dynamic_catch
    def set_user_account_profile(self, secrets_collection_guid: str,
                                 body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a secrets collection with its user account profile statistics."""
        run_sync(self._async_set_user_account_profile(secrets_collection_guid, body))

    @dynamic_catch
    async def _async_clear_user_account_profile(self, secrets_collection_guid: str,
                                                body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the UserAccountProfile classification from a secrets collection. Async version."""
        url = f"{self.security_officer_base_url}/secrets-collections/{secrets_collection_guid}/user-account-profile/remove"
        await self._async_delete_classification_request(url, body)

    @dynamic_catch
    def clear_user_account_profile(self, secrets_collection_guid: str,
                                   body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the UserAccountProfile classification from a secrets collection."""
        run_sync(self._async_clear_user_account_profile(secrets_collection_guid, body))

    @dynamic_catch
    async def _async_set_zone_membership_profile(self, governance_zone_guid: str,
                                                  body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a governance zone with its zone membership profile (e.g. allowed security groups). Async version."""
        url = f"{self.security_officer_base_url}/governance-zones/{governance_zone_guid}/zone-membership-profile"
        if body is None:
            body = {"class": "NewClassificationRequestBody", "properties": {"class": "ZoneMembershipProfileProperties"}}
        await self._async_new_classification_request(url, ["ZoneMembershipProfileProperties"], body)

    @dynamic_catch
    def set_zone_membership_profile(self, governance_zone_guid: str,
                                    body: Optional[dict | NewClassificationRequestBody] = None) -> None:
        """Classify a governance zone with its zone membership profile (e.g. allowed security groups)."""
        run_sync(self._async_set_zone_membership_profile(governance_zone_guid, body))

    @dynamic_catch
    async def _async_clear_zone_membership_profile(self, governance_zone_guid: str,
                                                    body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the ZoneMembershipProfile classification from a governance zone. Async version."""
        url = f"{self.security_officer_base_url}/governance-zones/{governance_zone_guid}/zone-membership-profile/remove"
        await self._async_delete_classification_request(url, body)

    @dynamic_catch
    def clear_zone_membership_profile(self, governance_zone_guid: str,
                                      body: Optional[dict | DeleteClassificationRequestBody] = None) -> None:
        """Remove the ZoneMembershipProfile classification from a governance zone."""
        run_sync(self._async_clear_zone_membership_profile(governance_zone_guid, body))

    #
    # Statements of applicability - which controls from a standard (such as the
    # Annex A controls of ISO/IEC 27001) apply to the organization, why, and how
    # far each is implemented.  Added in Egeria 6.3.
    #

    @dynamic_catch
    async def _async_create_statement_of_applicability(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """Create a statement of applicability. Async version.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            Request body whose properties class is StatementOfApplicabilityProperties.

        Returns
        -------
        str
            The GUID of the new statement of applicability.
        """
        url = f"{self.security_officer_base_url}/statements-of-applicability"
        return await self._async_create_element_body_request(url, ["StatementOfApplicabilityProperties"], body)

    @dynamic_catch
    def create_statement_of_applicability(self, body: Optional[dict | NewElementRequestBody] = None) -> str:
        """Create a statement of applicability.

        Parameters
        ----------
        body : dict | NewElementRequestBody
            Request body whose properties class is StatementOfApplicabilityProperties.

        Returns
        -------
        str
            The GUID of the new statement of applicability.
        """
        return run_sync(self._async_create_statement_of_applicability(body))

    @dynamic_catch
    async def _async_create_statement_of_applicability_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a statement of applicability using an existing one as a template. Async version."""
        url = f"{self.security_officer_base_url}/statements-of-applicability/from-template"
        return await self._async_create_element_from_template(url, body)

    @dynamic_catch
    def create_statement_of_applicability_from_template(self, body: dict | TemplateRequestBody) -> str:
        """Create a statement of applicability using an existing one as a template."""
        return run_sync(self._async_create_statement_of_applicability_from_template(body))

    @dynamic_catch
    async def _async_update_statement_of_applicability(self, soa_guid: str,
                                                       body: dict | UpdateElementRequestBody) -> None:
        """Update the properties of a statement of applicability - for example, to approve it. Async version."""
        url = f"{self.security_officer_base_url}/statements-of-applicability/{soa_guid}/update"
        await self._async_update_element_body_request(url, ["StatementOfApplicabilityProperties"], body)

    @dynamic_catch
    def update_statement_of_applicability(self, soa_guid: str, body: dict | UpdateElementRequestBody) -> None:
        """Update the properties of a statement of applicability - for example, to approve it."""
        run_sync(self._async_update_statement_of_applicability(soa_guid, body))

    @dynamic_catch
    async def _async_delete_statement_of_applicability(self, soa_guid: str,
                                                       body: Optional[dict | DeleteElementRequestBody] = None,
                                                       cascade: bool = False) -> None:
        """Delete a statement of applicability. Async version."""
        url = f"{self.security_officer_base_url}/statements-of-applicability/{soa_guid}/delete"
        await self._async_delete_element_request(url, body, cascade)

    @dynamic_catch
    def delete_statement_of_applicability(self, soa_guid: str, body: Optional[dict | DeleteElementRequestBody] = None,
                                          cascade: bool = False) -> None:
        """Delete a statement of applicability."""
        run_sync(self._async_delete_statement_of_applicability(soa_guid, body, cascade))

    def _generate_statement_of_applicability_output(
        self,
        elements: dict | list[dict],
        search_string: Optional[str] = None,
        element_type_name: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: dict | str | None = None,
        **kwargs
    ) -> Any:
        return self._generate_formatted_output(
            elements=elements,
            query_string=search_string,
            entity_type=element_type_name or "StatementOfApplicability",
            output_format=output_format,
            extract_properties_func=self._extract_referenceable_properties,
            report_spec=report_spec,
            **kwargs
        )

    @dynamic_catch
    async def _async_get_statements_of_applicability_by_name(
        self,
        filter_string: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the statements of applicability with a particular name. Async version."""
        url = f"{self.security_officer_base_url}/statements-of-applicability/by-name"
        return await self._async_get_name_request(
            url,
            _type="StatementOfApplicability",
            _gen_output=self._generate_statement_of_applicability_output,
            filter_string=filter_string,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            start_from=start_from,
            page_size=page_size,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    @dynamic_catch
    def get_statements_of_applicability_by_name(
        self,
        filter_string: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        start_from: int = 0,
        page_size: int = 0,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
        body: Optional[dict | FilterRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the statements of applicability with a particular name."""
        return run_sync(
            self._async_get_statements_of_applicability_by_name(
                filter_string=filter_string,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                start_from=start_from,
                page_size=page_size,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_find_statements_of_applicability(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the statements of applicability that contain the search string. Async version."""
        url = f"{self.security_officer_base_url}/statements-of-applicability/by-search-string"
        return await self._async_find_request(
            url,
            _type="StatementOfApplicability",
            _gen_output=self._generate_statement_of_applicability_output,
            search_string=search_string,
            starts_with=starts_with,
            ends_with=ends_with,
            ignore_case=ignore_case,
            metadata_element_type=metadata_element_type_name,
            metadata_element_subtypes=metadata_element_subtypes,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            as_of_time=as_of_time,
            start_from=start_from,
            page_size=page_size,
            sequencing_order=sequencing_order,
            sequencing_property=sequencing_property,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    @dynamic_catch
    def find_statements_of_applicability(
        self,
        search_string: str = "*",
        starts_with: bool = True,
        ends_with: bool = False,
        ignore_case: bool = True,
        metadata_element_type_name: str | None = None,
        metadata_element_subtypes: list[str] | None = None,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        as_of_time: Optional[str] = None,
        start_from: int = 0,
        page_size: int = 100,
        sequencing_order: Optional[str] = None,
        sequencing_property: Optional[str] = None,
        output_format: str = "JSON",
        report_spec: Optional[str | dict] = None,
        body: Optional[dict | SearchStringRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the statements of applicability that contain the search string."""
        return run_sync(
            self._async_find_statements_of_applicability(
                search_string=search_string,
                starts_with=starts_with,
                ends_with=ends_with,
                ignore_case=ignore_case,
                metadata_element_type_name=metadata_element_type_name,
                metadata_element_subtypes=metadata_element_subtypes,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                as_of_time=as_of_time,
                start_from=start_from,
                page_size=page_size,
                sequencing_order=sequencing_order,
                sequencing_property=sequencing_property,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_get_statement_of_applicability_by_guid(
        self,
        soa_guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return a statement of applicability. Async version.

        Each linked control, with its ControlApplicability relationship properties, is returned in the
        element's otherRelatedElements list.
        """
        url = f"{self.security_officer_base_url}/statements-of-applicability/{soa_guid}/retrieve"
        return await self._async_get_guid_request(
            url,
            _type="StatementOfApplicability",
            _gen_output=self._generate_statement_of_applicability_output,
            include_only_relationships=include_only_relationships,
            skip_relationships=skip_relationships,
            graph_query_depth=graph_query_depth,
            output_format=output_format,
            report_spec=report_spec,
            body=body,
            **kwargs,
        )

    @dynamic_catch
    def get_statement_of_applicability_by_guid(
        self,
        soa_guid: str,
        include_only_relationships: list[str] | None = None,
        skip_relationships: list[str] | None = None,
        graph_query_depth: int = 3,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> dict | str:
        """Return a statement of applicability.

        Each linked control, with its ControlApplicability relationship properties, is returned in the
        element's otherRelatedElements list.
        """
        return run_sync(
            self._async_get_statement_of_applicability_by_guid(
                soa_guid=soa_guid,
                include_only_relationships=include_only_relationships,
                skip_relationships=skip_relationships,
                graph_query_depth=graph_query_depth,
                output_format=output_format,
                report_spec=report_spec,
                body=body,
                **kwargs,
            )
        )

    @dynamic_catch
    async def _async_link_control_applicability(self, soa_guid: str, control_guid: str,
                                                body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Link a control to a statement of applicability (ControlApplicability relationship). Async version.

        ControlApplicability is not multi-link: linking a control that is already linked updates the
        properties of the existing relationship, so this is also how a control's applicability is updated.

        Parameters
        ----------
        soa_guid : str
            The statement of applicability.
        control_guid : str
            The governance definition (typically a GovernanceControl) being assessed.
        body : dict | NewRelationshipRequestBody, optional
            Request body whose properties class is ControlApplicabilityProperties.
        """
        url = (f"{self.security_officer_base_url}/statements-of-applicability/{soa_guid}"
               f"/control-applicability/{control_guid}/attach")
        await self._async_new_relationship_request(url, ["ControlApplicabilityProperties"], body)

    @dynamic_catch
    def link_control_applicability(self, soa_guid: str, control_guid: str,
                                   body: Optional[dict | NewRelationshipRequestBody] = None) -> None:
        """Link a control to a statement of applicability (ControlApplicability relationship).

        ControlApplicability is not multi-link: linking a control that is already linked updates the
        properties of the existing relationship, so this is also how a control's applicability is updated.

        Parameters
        ----------
        soa_guid : str
            The statement of applicability.
        control_guid : str
            The governance definition (typically a GovernanceControl) being assessed.
        body : dict | NewRelationshipRequestBody, optional
            Request body whose properties class is ControlApplicabilityProperties.
        """
        run_sync(self._async_link_control_applicability(soa_guid, control_guid, body))

    @dynamic_catch
    async def _async_detach_control_applicability(self, soa_guid: str, control_guid: str,
                                                  body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Remove a control from a statement of applicability. Async version."""
        url = (f"{self.security_officer_base_url}/statements-of-applicability/{soa_guid}"
               f"/control-applicability/{control_guid}/detach")
        await self._async_delete_relationship_request(url, body)

    @dynamic_catch
    def detach_control_applicability(self, soa_guid: str, control_guid: str,
                                     body: Optional[dict | DeleteRelationshipRequestBody] = None) -> None:
        """Remove a control from a statement of applicability."""
        run_sync(self._async_detach_control_applicability(soa_guid, control_guid, body))

    @staticmethod
    def _control_applicability_rows(soa: dict) -> list[dict]:
        """Turn a statement of applicability's ControlApplicability relationships into one element per control.

        Each row carries the control's header and properties, with the relationship properties merged in.
        The relationship's description becomes `notes` so it does not hide the control's own description.
        """
        rows = []
        for rel in soa.get("otherRelatedElements") or []:
            rel_type = (rel.get("relationshipHeader") or {}).get("type", {}).get("typeName")
            if rel_type != "ControlApplicability":
                continue
            control = rel.get("relatedElement") or {}
            properties = dict(control.get("properties") or {})
            for key, value in (rel.get("relationshipProperties") or {}).items():
                if key in ("class", "typeName"):
                    continue
                properties["notes" if key == "description" else key] = value
            # Egeria treats a control as applicable unless isApplicable is false.
            properties.setdefault("isApplicable", True)
            rows.append({"elementHeader": control.get("elementHeader", {}), "properties": properties})
        rows.sort(key=lambda r: (str(r["properties"].get("label") or ""), str(r["properties"].get("displayName") or "")))
        return rows

    async def _async_resolve_statement_of_applicability(self, soa_guid: str,
                                                        body: Optional[dict | GetRequestBody] = None) -> dict | str:
        """Fetch a statement of applicability by GUID, or by qualified name when `soa_guid` is not a GUID."""
        try:
            uuid.UUID(str(soa_guid))
        except ValueError:
            matches = await self._async_get_statements_of_applicability_by_name(soa_guid)
            if not isinstance(matches, list) or not matches:
                return NO_ELEMENTS_FOUND
            soa_guid = matches[0]["elementHeader"]["guid"]
        return await self._async_get_statement_of_applicability_by_guid(soa_guid, body=body)

    @dynamic_catch
    async def _async_get_statement_of_applicability_controls(
        self,
        soa_guid: str,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the controls assessed in a statement of applicability, one row per control. Async version.

        Each row has the control's properties plus its ControlApplicability properties (label, isApplicable,
        justification, inclusionReasons, implementationStatus, implementationDescription, reviewDate, and the
        relationship description as notes). This is the table an auditor asks for.

        Parameters
        ----------
        soa_guid : str
            The statement of applicability's GUID, or its qualified name.
        output_format : str, default "JSON"
            JSON returns the rows as element dicts; any other format is rendered with the report spec.
        report_spec : str | dict, optional
            Defaults to "Statement-of-Applicability-Controls".
        body : dict | GetRequestBody, optional
            Passed to get_statement_of_applicability_by_guid.

        Returns
        -------
        list | str
            The rows, or NO_ELEMENTS_FOUND when no controls are linked.
        """
        soa = await self._async_resolve_statement_of_applicability(soa_guid, body)
        rows = self._control_applicability_rows(soa) if isinstance(soa, dict) else []
        if not rows:
            return NO_ELEMENTS_FOUND
        return self._generate_formatted_output(
            elements=rows,
            entity_type="Statement-of-Applicability-Controls",
            output_format=output_format,
            extract_properties_func=self._extract_referenceable_properties,
            report_spec=report_spec or "Statement-of-Applicability-Controls",
            **kwargs,
        )

    @dynamic_catch
    def get_statement_of_applicability_controls(
        self,
        soa_guid: str,
        output_format: str = "JSON",
        report_spec: str | dict | None = None,
        body: Optional[dict | GetRequestBody] = None,
        **kwargs,
    ) -> list | str:
        """Return the controls assessed in a statement of applicability, one row per control.

        See _async_get_statement_of_applicability_controls.
        """
        return run_sync(
            self._async_get_statement_of_applicability_controls(
                soa_guid, output_format=output_format, report_spec=report_spec, body=body, **kwargs
            )
        )

    @dynamic_catch
    async def _async_get_control_implementation_summary(self, soa_guid: str,
                                                        body: Optional[dict | GetRequestBody] = None) -> dict:
        """Count the applicable controls in a statement of applicability by implementation status. Async version.

        Every ControlImplementationStatus value is present, so a zero is a real count. A control with no
        implementation status counts as NOT_STARTED, the enum's default. Controls marked not applicable are
        left out of the status counts and reported separately.

        Returns
        -------
        dict
            {"byStatus": {status: count, ...}, "applicable": int, "notApplicable": int}
        """
        soa = await self._async_resolve_statement_of_applicability(soa_guid, body)
        rows = self._control_applicability_rows(soa) if isinstance(soa, dict) else []
        by_status = {status.value: 0 for status in ControlImplementationStatus}
        not_applicable = 0
        for row in rows:
            props = row["properties"]
            if props.get("isApplicable") is False:
                not_applicable += 1
                continue
            status = props.get("implementationStatus") or ControlImplementationStatus.NOT_STARTED.value
            by_status[status] = by_status.get(status, 0) + 1
        return {"byStatus": by_status, "applicable": len(rows) - not_applicable, "notApplicable": not_applicable}

    @dynamic_catch
    def get_control_implementation_summary(self, soa_guid: str,
                                           body: Optional[dict | GetRequestBody] = None) -> dict:
        """Count the applicable controls in a statement of applicability by implementation status.

        See _async_get_control_implementation_summary.
        """
        return run_sync(self._async_get_control_implementation_summary(soa_guid, body))
