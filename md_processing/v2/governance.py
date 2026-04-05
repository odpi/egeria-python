"""
Governance Officer Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional
import uuid
from loguru import logger
import json

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import get_command_spec
from md_processing.md_processing_utils.common_md_utils import (
    set_gov_prop_body, set_create_body, set_update_body, 
    update_element_dictionary, set_delete_request_body,
    set_delete_rel_request_body,
    set_peer_gov_def_request_body, set_rel_prop_body,
    ALL_GOVERNANCE_DEFINITIONS
)
from pyegeria.core.utils import body_slimmer

class GovernanceProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Governance Definitions.
    """

    @staticmethod
    def _is_security_group_type_name(type_name: str) -> bool:
        normalized = "".join(ch for ch in (type_name or "") if ch.isalnum()).lower()
        return normalized == "securitygroup"

    @staticmethod
    def _prune_security_group_properties(properties: Dict[str, Any], egeria_type_name: str) -> Dict[str, Any]:
        if not GovernanceProcessor._is_security_group_type_name(egeria_type_name):
            return properties
        # SecurityGroup is modeled with a narrower property set on some server versions.
        for field in ("domainIdentifier", "summary", "scope", "importance", "implications", "outcomes", "results", "usage"):
            properties.pop(field, None)
        return properties

    @staticmethod
    def _strip_keys_recursive(
        payload: Any,
        disallowed_keys: set[str],
        *,
        preserve_under: Optional[set[str]] = None,
        context_label: str = "payload",
    ) -> Any:
        preserve_under = preserve_under or set()
        dropped: list[str] = []

        def _walk(node: Any, path: tuple[str, ...], in_preserved_branch: bool) -> Any:
            if isinstance(node, dict):
                cleaned: Dict[str, Any] = {}
                for key, value in node.items():
                    key_str = str(key)
                    current_path = ".".join((*path, key_str))
                    next_preserved = in_preserved_branch or (key_str in preserve_under)
                    if not in_preserved_branch and key_str in disallowed_keys:
                        dropped.append(current_path)
                        continue
                    cleaned[key] = _walk(value, (*path, key_str), next_preserved)
                return cleaned
            if isinstance(node, list):
                return [_walk(v, (*path, "[]"), in_preserved_branch) for v in node]
            return node

        cleaned_payload = _walk(payload, tuple(), False)
        if dropped:
            unique_dropped = sorted(set(dropped))
            logger.warning(
                f"Dropped unsupported keys while sanitizing {context_label}: {', '.join(unique_dropped)}"
            )
        return cleaned_payload

    @staticmethod
    def _is_security_group_property_rejection(exc: Exception) -> bool:
        msg = str(exc)
        msg_lower = msg.lower()
        return (
            "securitygroup" in msg_lower
            and "domainidentifier" in msg_lower
            and ("unsupported property named newproperties" in msg_lower or "not supported for this type" in msg_lower)
        )

    @staticmethod
    def _requires_base_governance_definition_properties(exc: Exception) -> bool:
        msg = str(exc).lower()
        return (
            "omag-common-400-029" in msg
            and "creategovernancedefinition" in msg
            and "governancedefinitionproperties" in msg
        )

    @staticmethod
    def _to_base_governance_definition_properties(properties: Dict[str, Any], object_type: str) -> Dict[str, Any]:
        source = dict(properties)
        fallback: Dict[str, Any] = {
            "class": "GovernanceDefinitionProperties",
            "typeName": source.get("typeName"),
        }

        # Keep only cross-type governance definition keys in base-class fallback payloads.
        for key in (
            "qualifiedName",
            "displayName",
            "description",
            "category",
            "identifier",
            "contentStatus",
            "userDefinedContentStatus",
            "versionIdentifier",
            "effectiveFrom",
            "effectiveTo",
            "additionalProperties",
            "extendedProperties",
        ):
            if key in source:
                fallback[key] = source.get(key)

        # SecurityGroup server-compat fallback: carry distinguishedName via additionalProperties only.
        if GovernanceProcessor._is_security_group_type_name(object_type) or GovernanceProcessor._is_security_group_type_name(
            str(source.get("typeName"))
        ):
            distinguished_name = source.get("distinguishedName")
            if distinguished_name:
                additional = fallback.get("additionalProperties")
                if not isinstance(additional, dict):
                    additional = {}
                additional.setdefault("distinguishedName", distinguished_name)
                fallback["additionalProperties"] = additional

        return fallback

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_governance_definition_by_guid(guid)
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        object_aliases = {
            "governance_drivers": "Governance Drivers",
            "governance_policies": "Governance Policies",
            "governance_controls": "Governance Controls",
        }
        object_type = object_aliases.get(object_type, object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")
        
        # 1. Properties
        prop_body = set_gov_prop_body(om_type or object_type, qualified_name, attributes)
        prop_body = self._prune_security_group_properties(prop_body, self.egeria_type_name)

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block
            self.parsed_output["guid"] = guid

            self.last_body = body = {
                "class": "UpdateElementRequestBody",
                "properties": self.filter_update_properties(prop_body, attributes.get('Merge Update', {}).get('value', True)),
                "mergeUpdate": attributes.get('Merge Update', {}).get('value', True)
            }
            await self.client._async_update_governance_definition(guid, body)
            
            # Relationships
            await self._sync_rels(guid, attributes)
            
            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = set_create_body(om_type or object_type, attributes)
            create_props = dict(prop_body)
            # Always use the most specific subtype properties class for create payloads.
            # set_gov_prop_body()/update_gov_body_for_type already choose the correct class.
            outgoing_type_name = str(create_props.get("typeName") or self.egeria_type_name or om_type or object_type)

            # Defensive: always prune SecurityGroup governance-only fields based on the outgoing type,
            # even if spec/type derivation drifts.
            if self._is_security_group_type_name(outgoing_type_name) or self._is_security_group_type_name(object_type):
                create_props = self._prune_security_group_properties(create_props, "SecurityGroup")
                create_props = self._strip_keys_recursive(
                    create_props,
                    {"domainIdentifier", "summary", "scope", "importance", "implications", "outcomes", "results", "usage"},
                    preserve_under={"extendedProperties", "additionalProperties"},
                    context_label=f"Create {object_type} initial payload",
                )

            body['properties'] = create_props
            if self._is_security_group_type_name(outgoing_type_name) or self._is_security_group_type_name(object_type):
                logger.debug(f"Create SecurityGroup payload properties: {json.dumps(body.get('properties', {}), sort_keys=True)}")

            try:
                raw_guid = await self.client._async_create_governance_definition(body_slimmer(body))
            except Exception as exc:
                # Some servers reject SecurityGroup payloads when governance-only fields leak into create properties.
                retry_type_name = str(create_props.get("typeName") or self.egeria_type_name or object_type)
                if (
                    not self._is_security_group_type_name(retry_type_name)
                    and not self._is_security_group_type_name(object_type)
                ) or not self._is_security_group_property_rejection(exc):
                    if not self._requires_base_governance_definition_properties(exc):
                        raise
                    retry_body = dict(body)
                    retry_body["properties"] = self._to_base_governance_definition_properties(dict(create_props), object_type)
                    logger.debug(
                        f"Create SecurityGroup fallback payload properties: {json.dumps(retry_body.get('properties', {}), sort_keys=True)}"
                    )
                    logger.warning(
                        "Retrying create with GovernanceDefinitionProperties for server compatibility"
                    )
                    raw_guid = await self.client._async_create_governance_definition(body_slimmer(retry_body))
                else:
                    retry_body = dict(body)
                    retry_props = self._prune_security_group_properties(dict(create_props), "SecurityGroup")
                    retry_props = self._strip_keys_recursive(
                        retry_props,
                        {"domainIdentifier", "summary", "scope", "importance", "implications", "outcomes", "results", "usage"},
                        preserve_under={"extendedProperties", "additionalProperties"},
                        context_label=f"Create {object_type} retry payload",
                    )
                    retry_body["properties"] = retry_props
                    logger.warning("Retrying Create Security Group with narrowed property set after server rejected governance-only fields")
                    raw_guid = await self.client._async_create_governance_definition(body_slimmer(retry_body))

            guid = self.extract_guid_or_raise(raw_guid, f"Create {object_type}")
            if guid:
                self.parsed_output["guid"] = guid
                await self._sync_rels(guid, attributes)
                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_rels(self, guid: str, attributes: Dict[str, Any]):
        to_be_supports = attributes.get("Supports Policies", {}).get("guid_list", [])
        to_be_drivers = attributes.get("Governance Drivers", {}).get("guid_list", [])
        
        for policy in to_be_supports:
            try:
                await self.client._async_attach_supporting_definitions(policy, "GovernanceImplementation", guid)
                self.add_related_result("Supports Policy", policy)
            except Exception as e:
                self.add_related_result("Supports Policy", policy, status="failure", message=str(e))

        for driver in to_be_drivers:
            try:
                await self.client._async_attach_supporting_definitions(driver, "GovernanceResponse", guid)
                self.add_related_result("Governance Driver", driver)
            except Exception as e:
                self.add_related_result("Governance Driver", driver, status="failure", message=str(e))

class GovernanceLinkProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Governance Peer/Supporting/Governed-By links.
    """



    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    @staticmethod
    def _normalize_guid(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None
        candidate = value.strip()
        if not candidate:
            return None
        try:
            uuid.UUID(candidate)
            return candidate
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _resolve_endpoint_guid(attributes: Dict[str, Any], keys: Any) -> Optional[str]:
        key_list = (keys,) if isinstance(keys, str) else tuple(keys)
        for key in key_list:
            guid = (attributes.get(key) or {}).get("guid")
            if guid:
                return guid
        return None

    def _resolve_relationship_guid(self, object_type: str, attributes: Dict[str, Any]) -> Optional[str]:
        guid_sources = [
            self.parsed_output.get("guid") if self.parsed_output else None,
            (attributes.get("GUID") or {}).get("guid"),
            (attributes.get("GUID") or {}).get("value"),
        ]

        # Backward compatibility: some markdown templates use these labels for relationship ids.
        if object_type == "Certification":
            guid_sources.append((attributes.get("Certificate GUID") or {}).get("value"))
        elif object_type == "License":
            guid_sources.append((attributes.get("License GUID") or {}).get("value"))

        for raw in guid_sources:
            guid = self._normalize_guid(raw)
            if guid:
                return guid
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        object_aliases = {
            "T&C": "Agreement T&C",
            "Agreement Terms and Conditions": "Agreement T&C",
        }
        object_type = object_aliases.get(object_type, object_type)
        attributes = self.parsed_output["attributes"]
        established_verbs = {"Link", "Attach", "Add"}
        remove_verbs = {"Detach", "Unlink", "Remove"}

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        endpoint_map = {
            "Governance Response": ("Driver", "Policy"),
            "Governance Mechanism": ("Policy", "Mechanism"),
            "Governed By": ("Referenceable", "Governance Definition"),
            "Governance Drivers": ("Governance Driver 1", "Governance Driver 2"),
            "Governance Policies": ("Governance Policy 1", "Governance Policy 2"),
            "Governance Controls": ("Governance Control 1", "Governance Control 2"),
            "Notification Subscriber": ("Notification Type", "Subscriber"),
            "Zone Hierarchy": ("Parent Zone", "Child Zone"),
            "Certification": ("Certification Type", "Referenceable"),
            "License": ("License Type", "Referenceable"),
            "Agreement T&C": ("Agreement Name", ("Terms & Conditions Id", "Referenceable")),
            "Associated Group": ("Access Control", "Security Group"),
            "Monitored Resource": (("Notification Type", "Monitoring Control"), "Monitored Resource"),
            "Regulation Certification Type": ("Regulation", "Certification Type"),
        }

        endpoint_keys = endpoint_map.get(object_type)
        if not endpoint_keys:
            raise NotImplementedError(
                f"Governance link type '{object_type}' is not yet supported by GovernanceLinkProcessor."
            )

        left_key, right_key = endpoint_keys
        left_guid = self._resolve_endpoint_guid(attributes, left_key)
        right_guid = self._resolve_endpoint_guid(attributes, right_key)

        left_label = left_key if isinstance(left_key, str) else " / ".join(left_key)
        right_label = right_key if isinstance(right_key, str) else " / ".join(right_key)

        missing = []
        if not left_guid:
            missing.append(left_label)
        if not right_guid:
            missing.append(right_label)
        if missing:
            raise ValueError(
                f"Missing unresolved reference GUID(s) for {', '.join(missing)} in '{verb} {object_type}'."
            )

        if verb in established_verbs:
            if object_type in {"Governance Drivers", "Governance Policies", "Governance Controls"}:
                rel_type = om_type or {
                    "Governance Drivers": "GovernanceDriverLink",
                    "Governance Policies": "GovernancePolicyLink",
                    "Governance Controls": "GovernanceControlLink",
                }.get(object_type)
                body = set_peer_gov_def_request_body(om_type or object_type, attributes)
                await self.client._async_link_peer_definitions(left_guid, rel_type, right_guid, body)

            elif object_type in {"Governance Response", "Governance Mechanism"}:
                rel_type = om_type or {
                    "Governance Response": "GovernanceResponse",
                    "Governance Mechanism": "GovernanceMechanism",
                }.get(object_type)
                body = set_peer_gov_def_request_body(om_type or object_type, attributes)
                body["properties"] = {
                    "class": "SupportingDefinitionProperties",
                    "typeName": rel_type,
                    "rationale": attributes.get("Rationale", {}).get("value"),
                    "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                    "effectiveTo": attributes.get("Effective To", {}).get("value"),
                }
                await self.client._async_attach_supporting_definitions(left_guid, rel_type, right_guid, body)

            elif object_type == "Governed By":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": set_rel_prop_body(object_type, attributes)
                })
                await self.client._async_attach_governed_by_definition(left_guid, right_guid, body)

            elif object_type == "Notification Subscriber":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": set_rel_prop_body(object_type, attributes)
                })
                await self.client._async_link_notification_subscriber(left_guid, right_guid, body)

            elif object_type == "Zone Hierarchy":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": set_rel_prop_body(object_type, attributes)
                })
                await self.client._async_link_governance_zones(left_guid, right_guid, body)

            elif object_type == "Certification":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": {
                        "class": "CertificationProperties",
                        "certificateId": attributes.get("Certificate GUID", {}).get("value"),
                        "startDate": attributes.get("Start Date", {}).get("value"),
                        "endDate": attributes.get("End Date", {}).get("value"),
                        "conditions": attributes.get("Conditions", {}).get("value"),
                        "certifiedBy": attributes.get("Certified By", {}).get("value"),
                        "certifiedByTypeName": attributes.get("Certified By Type Name", {}).get("value"),
                        "certifiedByPropertyName": attributes.get("Certified By Property Name", {}).get("value"),
                        "custodian": attributes.get("Custodian", {}).get("value"),
                        "custodianTypeName": attributes.get("Custodian Type Name", {}).get("value"),
                        "custodianPropertyName": attributes.get("Custodian Property Name", {}).get("value"),
                        "recipient": attributes.get("Recipient", {}).get("value"),
                        "recipientTypeName": attributes.get("Recipient Type Name", {}).get("value"),
                        "recipientPropertyName": attributes.get("Recipient Property Name", {}).get("value"),
                        "entitlements": attributes.get("Entitlements", {}).get("value"),
                        "obligations": attributes.get("Obligations", {}).get("value"),
                        "restrictions": attributes.get("Restrictions", {}).get("value"),
                        "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                        "effectiveTo": attributes.get("Effective To", {}).get("value"),
                    },
                })
                await self.client._async_add_certification_to_element(left_guid, right_guid, body)

            elif object_type == "License":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": {
                        "class": "LicenseProperties",
                        "licenseId": attributes.get("License GUID", {}).get("value"),
                        "startDate": attributes.get("Start Date", {}).get("value"),
                        "endDate": attributes.get("End Date", {}).get("value"),
                        "conditions": attributes.get("Conditions", {}).get("value"),
                        "licensedBy": attributes.get("Licensed By", {}).get("value"),
                        "licensedByTypeName": attributes.get("Licensed By Type Name", {}).get("value"),
                        "licensedByPropertyName": attributes.get("Licensed By Property Name", {}).get("value"),
                        "custodian": attributes.get("Custodian", {}).get("value"),
                        "custodianTypeName": attributes.get("Custodian Type Name", {}).get("value"),
                        "custodianPropertyName": attributes.get("Custodian Property Name", {}).get("value"),
                        "licensee": attributes.get("Licensee", {}).get("value"),
                        "licenseeTypeName": attributes.get("Licensee Type Name", {}).get("value"),
                        "licenseePropertyName": attributes.get("Licensee Property Name", {}).get("value"),
                        "entitlements": attributes.get("Entitlements", {}).get("value"),
                        "obligations": attributes.get("Obligations", {}).get("value"),
                        "restrictions": attributes.get("Restrictions", {}).get("value"),
                        "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                        "effectiveTo": attributes.get("Effective To", {}).get("value"),
                    },
                })
                await self.client._async_add_license_to_element(left_guid, right_guid, body)

            elif object_type == "Agreement T&C":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": {
                        "class": "AgreementItemProperties",
                        "agreementItemId": attributes.get("Agreement Item Id", {}).get("value"),
                        "agreementStart": attributes.get("Start Date", {}).get("value"),
                        "agreementEnd": attributes.get("End Date", {}).get("value"),
                        "entitlements": attributes.get("Entitlements", {}).get("value"),
                        "obligations": attributes.get("Obligations", {}).get("value"),
                        "restrictions": attributes.get("Restrictions", {}).get("value"),
                        "usageMeasurements": attributes.get("Usage Measurements", {}).get("value"),
                        "effectiveFrom": attributes.get("Effective From", {}).get("value"),
                        "effectiveTo": attributes.get("Effective To", {}).get("value"),
                    },
                })
                await self.client._async_link_agreement_item(left_guid, right_guid, body)

            elif object_type in {"Associated Group", "Regulation Certification Type"}:
                rel_map = {
                    "Associated Group": "AssociatedSecurityGroup",
                    "Regulation Certification Type": "RegulationCertificationType",
                }
                rel_type = rel_map[object_type]
                self.last_body = body = set_peer_gov_def_request_body(object_type, attributes)
                await self.client._async_link_peer_definitions(left_guid, rel_type, right_guid, body)

            elif object_type == "Monitored Resource":
                body = body_slimmer({
                    "class": "NewRelationshipRequestBody",
                    "properties": set_rel_prop_body(object_type, attributes)
                })
                await self.client._async_link_monitored_resource(left_guid, right_guid, body)

            logger.success(f"Linked Governance {object_type}")
            return f"\n\n# {verb} {object_type}\n\nOperation completed."

        elif verb in remove_verbs:
            self.last_body = body = set_delete_rel_request_body(object_type, attributes)
            if object_type in {"Governance Drivers", "Governance Policies", "Governance Controls"}:
                rel_map = {
                    "Governance Drivers": "GovernanceDriverLink",
                    "Governance Policies": "GovernancePolicyLink",
                    "Governance Controls": "GovernanceControlLink",
                }
                rel_type = rel_map[object_type]
                await self.client._async_detach_peer_definitions(left_guid, rel_type, right_guid, body)

            elif object_type in {"Governance Response", "Governance Mechanism"}:
                rel_map = {
                    "Governance Response": "GovernanceResponse",
                    "Governance Mechanism": "GovernanceMechanism",
                }
                rel_type = rel_map[object_type]
                await self.client._async_detach_supporting_definitions(left_guid, rel_type, right_guid, body)

            elif object_type == "Governed By":
                await self.client._async_detach_governed_by_definition(left_guid, right_guid, body)

            elif object_type == "Notification Subscriber":
                await self.client._async_detach_notification_subscriber(left_guid, right_guid, body)

            elif object_type == "Zone Hierarchy":
                await self.client._async_detach_governance_zones(left_guid, right_guid, body)

            elif object_type == "Agreement T&C":
                await self.client._async_detach_agreement_item(left_guid, right_guid, body)

            elif object_type in {"Associated Group", "Regulation Certification Type"}:
                rel_map = {
                    "Associated Group": "AssociatedSecurityGroup",
                    "Regulation Certification Type": "RegulationCertificationType",
                }
                rel_type = rel_map[object_type]
                await self.client._async_detach_peer_definitions(left_guid, rel_type, right_guid, body)

            elif object_type == "Monitored Resource":
                await self.client._async_detach_monitored_resource(left_guid, right_guid, body)

            elif object_type in {"Certification", "License"}:
                rel_guid = self._resolve_relationship_guid(object_type, attributes)
                if not rel_guid:
                    raise ValueError(
                        f"{verb} {object_type} requires the relationship GUID. Provide it in `GUID` (or the legacy id field)."
                    )
                if object_type == "Certification":
                    await self.client._async_decertify_element(rel_guid, body)
                else:
                    await self.client._async_unlicense_element(rel_guid, body)

            logger.success(f"Detached Governance {object_type}")
            return f"\n\n# {verb} {object_type}\n\nOperation completed."

        return self.command.raw_block

class GovernanceContextProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Governance Definition Context retrieval.
    """



    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        guid = self.parsed_output.get("guid")
        output_format = attributes.get('Output Format', {}).get('value', 'LIST')
        
        if not guid:
            return self.command.raw_block
            
        body = set_update_body(self.command.object_type, attributes)
        struct = await self.client._async_get_gov_def_in_context(guid, body=body, output_format=output_format)
        
        if output_format.upper() == "DICT":
            return f"\n# Context Graph for {guid}\n\n```json\n{json.dumps(struct, indent=4)}\n```"
        return f"\n# Context Graph for {guid}\n\n{struct}"
