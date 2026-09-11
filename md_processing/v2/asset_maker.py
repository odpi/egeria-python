"""
Asset Maker Processor for Dr.Egeria v2.

Wraps `pyegeria/omvs/automated_curation.py`'s catalog-template-based element
creation surface: the generic `_async_create_elem_from_template` (the
`Create Element` command -- Advanced-only, low-level) plus its twelve
type-specific convenience wrappers (`Create Secrets Store Element`,
`Create Kafka Server Element`, ... -- Basic). Every one of these instantiates
an Open Metadata catalog template rather than posting a Referenceable
properties body, so there's no update counterpart to any of them (matching
the underlying OMVS surface: create-from-template only) and no
`fetch_as_is`/upsert transition applies -- each command is a pure Create.
"""
from typing import Any, Dict, Optional

from loguru import logger

from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary


def _v(attributes: dict, name: str, default=None):
    return attributes.get(name, {}).get("value", default)


def _guid(attributes: dict, name: str):
    return attributes.get(name, {}).get("guid")


class AssetMakerProcessor(AsyncBaseCommandProcessor):
    """Processor for every 'Create <Type> Element' / 'Create Element' command
    in the Asset Maker family. Dispatches on OM_TYPE (specific commands) or
    the bare command key (the generic 'Create Element') to the matching
    automated_curation.py method."""

    def supports_target_element_lookup(self) -> bool:
        # Pure create-from-template, no update path -- see module docstring.
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output.get("attributes", {})
        client = self.client.automated_curation
        om_type = self.get_command_spec().get("OM_TYPE")
        command_key = self.command.object_type

        if command_key == "Element" and not om_type:
            # Generic 'Create Element' -- the raw TemplateRequestBody surface.
            body = {
                "class": "TemplateRequestBody",
                "typeName": _v(attributes, "Element Type Name"),
                "templateGUID": _v(attributes, "Template GUID"),
                "placeholderPropertyValues": _v(attributes, "Placeholder Property Values") or {},
                "replacementProperties": _v(attributes, "Template Properties"),
                "initialStatus": _v(attributes, "Initial Status"),
                "initialClassifications": _v(attributes, "Generic Initial Classifications"),
                "anchorGUID": _guid(attributes, "Anchor ID"),
                "isOwnAnchor": _v(attributes, "Is Own Anchor", True),
                "anchorScopeGUIDs": _v(attributes, "Anchor Scope IDs"),
                "effectiveFrom": _v(attributes, "Effective From"),
                "effectiveTo": _v(attributes, "Effective To"),
                "parentGUID": _guid(attributes, "Parent ID"),
                "parentRelationshipTypeName": _v(attributes, "Parent Relationship Type Name"),
                "parentRelationshipProperties": _v(attributes, "Parent Relationship Attributes"),
                "parentAtEnd1": _v(attributes, "Parent at End1", True),
            }
            guid = await client._async_create_elem_from_template(body)
            display_name = f"{_v(attributes, 'Element Type Name')} element"

        elif om_type == "SecretsCollection":
            guid = await client._async_create_secrets_store_element_from_template(
                file_path_name=_v(attributes, "File Path Name"),
                file_name=_v(attributes, "File Name"),
                description=_v(attributes, "Description"),
                version_identifier=_v(attributes, "Version Identifier"),
                file_system_name=_v(attributes, "File System Name", ""),
                file_type=_v(attributes, "File Type", "Open Metadata Secrets Store File"),
                file_extension=_v(attributes, "File Extension", "omsecrets"),
                file_encoding=_v(attributes, "File Encoding", "YAML"),
            )
            display_name = _v(attributes, "File Name")

        elif command_key == "Kafka Server Element":
            guid = await client._async_create_kafka_server_element_from_template(
                kafka_server=_v(attributes, "Kafka Server Name"),
                host_name=_v(attributes, "Host Name"),
                port=_v(attributes, "Port"),
                description=_v(attributes, "Description"),
            )
            display_name = _v(attributes, "Kafka Server Name")

        elif om_type == "CSVFile":
            guid = await client._async_create_csv_data_file_element_from_template(
                file_name=_v(attributes, "File Name"),
                file_type=_v(attributes, "File Type", "CSV Data File"),
                file_path_name=_v(attributes, "File Path Name"),
                version_identifier=_v(attributes, "Version Identifier"),
                file_encoding=_v(attributes, "File Encoding", "UTF-8"),
                file_extension=_v(attributes, "File Extension", "csv"),
                file_system_name=_v(attributes, "File System Name"),
                description=_v(attributes, "Description"),
            )
            display_name = _v(attributes, "File Name")

        elif command_key == "Postgres Server Element":
            guid = await client._async_create_postgres_server_element_from_template(
                postgres_server=_v(attributes, "Postgres Server Name"),
                host_name=_v(attributes, "Host Name"),
                port=_v(attributes, "Port"),
                db_user=_v(attributes, "Database User Id"),
                db_pwd=_v(attributes, "Database Password"),
                description=_v(attributes, "Description"),
            )
            display_name = _v(attributes, "Postgres Server Name")

        elif command_key == "Postgres Database Element":
            guid = await client._async_create_postgres_database_element_from_template(
                postgres_database=_v(attributes, "Postgres Database Name"),
                server_name=_v(attributes, "Postgres Server Name"),
                host_identifier=_v(attributes, "Host Name"),
                port=_v(attributes, "Port"),
                db_user=_v(attributes, "Database User Id"),
                db_pwd=_v(attributes, "Database Password"),
                description=_v(attributes, "Description"),
            )
            display_name = _v(attributes, "Postgres Database Name")

        elif om_type == "DataFolder" and command_key == "Folder Element":
            guid = await client._async_create_folder_element_from_template(
                path_name=_v(attributes, "Directory Path Name"),
                folder_name=_v(attributes, "Folder Name"),
                file_system=_v(attributes, "File System Name"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "Folder Name")

        elif command_key == "Unity Catalog Server Element":
            guid = await client._async_create_uc_server_element_from_template(
                server_name=_v(attributes, "UC Server Name"),
                host_url=_v(attributes, "Host URL"),
                port=_v(attributes, "Port"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "UC Server Name")

        elif om_type == "SoftwareCapability":
            guid = await client._async_create_uc_catalog_element_from_template(
                uc_catalog=_v(attributes, "UC Catalog Name"),
                network_address=_v(attributes, "Network Address"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "UC Catalog Name")

        elif command_key == "Unity Catalog Schema Element":
            guid = await client._async_create_uc_schema_element_from_template(
                uc_catalog=_v(attributes, "UC Catalog Name"),
                uc_schema=_v(attributes, "UC Schema Name"),
                network_address=_v(attributes, "Network Address"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "UC Schema Name")

        elif command_key == "Unity Catalog Table Element":
            guid = await client._async_create_uc_table_element_from_template(
                uc_catalog=_v(attributes, "UC Catalog Name"),
                uc_schema=_v(attributes, "UC Schema Name"),
                uc_table=_v(attributes, "UC Table Name"),
                uc_table_type=_v(attributes, "UC Table Type", "Managed"),
                uc_storage_loc=_v(attributes, "UC Storage Location"),
                uc_data_source_format=_v(attributes, "UC Data Source Format", "DELTA"),
                network_address=_v(attributes, "Network Address"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "UC Table Name")

        elif om_type == "DeployedAPI":
            guid = await client._async_create_uc_function_element_from_template(
                uc_catalog=_v(attributes, "UC Catalog Name"),
                uc_schema=_v(attributes, "UC Schema Name"),
                uc_function=_v(attributes, "UC Function Name"),
                network_address=_v(attributes, "Network Address"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "UC Function Name")

        elif om_type == "StorageVolume":
            guid = await client._async_create_uc_volume_element_from_template(
                uc_catalog=_v(attributes, "UC Catalog Name"),
                uc_schema=_v(attributes, "UC Schema Name"),
                uc_volume=_v(attributes, "UC Volume Name"),
                uc_vol_type=_v(attributes, "UC Volume Type", "Managed"),
                uc_storage_loc=_v(attributes, "UC Storage Location"),
                network_address=_v(attributes, "Network Address"),
                description=_v(attributes, "Description"),
                version=_v(attributes, "Version Identifier"),
            )
            display_name = _v(attributes, "UC Volume Name")

        else:
            raise ValueError(f"AssetMakerProcessor: unrecognized command "
                              f"(object_type={command_key!r}, OM_TYPE={om_type!r})")

        guid = self.extract_guid_or_raise(guid, f"Create {command_key}")
        self.parsed_output["guid"] = guid
        if display_name:
            update_element_dictionary(display_name, {"guid": guid, "display_name": display_name})

        logger.success(f"Created {command_key} '{display_name}' with GUID {guid}")
        return await self.render_result_markdown(guid)
