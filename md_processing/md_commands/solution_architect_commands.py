"""
This file contains blueprint/solution-related object_action functions for processing Egeria Markdown
"""
import json
import sys
from typing import Optional

from loguru import logger
from pygments.lexers import blueprint
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands)
from pyegeria import body_slimmer, EgeriaTech

load_commands('commands.json')

console = Console(width=int(200))

log_format = "D {time} | {level} | {function} | {line} | {message} | {extra}"
logger.remove()
logger.add(sys.stderr, level="INFO", format=log_format, colorize=True)
logger.add("solution_architect_log.log", rotation="1 day", retention="1 week", compression="zip", level="TRACE",
           format=log_format, colorize=True)


@logger.catch
def sync_component_related_elements(egeria_client: EgeriaTech, object_type: str, sub_component_guids: list,
                                    actor_guids: list, in_blueprint_guids: list, guid: str, qualified_name: str,
                                    display_name: str, replace_all_props: bool = True) -> None:
    """Sync a components related elements.

    """
    if replace_all_props:
        rel_el_list = egeria_client.get_component_related_elements(guid)
        # should I throw an exception if empty?
        as_is_sub_components = set(rel_el_list.get("sub_component_guids", []))
        as_is_actors = set(rel_el_list.get("actor_guids", []))
        as_is_blueprints = set(rel_el_list.get("blueprint_guids", []))

        to_be_sub_components = set(sub_component_guids) if sub_component_guids is not None else set()
        to_be_actors = set(actor_guids) if actor_guids is not None else set()
        to_be_blueprints = set(in_blueprint_guids) if in_blueprint_guids is not None else set()

        logger.trace(
            f"as_is_sub_components: {list(as_is_sub_components)} to_be_sub_components: {list(to_be_sub_components)}")
        logger.trace(f"as_is_actors: {list(as_is_actors)} to_be_actors: {list(to_be_actors)}")
        logger.trace(f"as_is_blueprints: {list(as_is_blueprints)} to_be_blueprints: {list(to_be_blueprints)}")

        sub_components_to_remove = as_is_sub_components - to_be_sub_components
        logger.trace(f"sub_components_to_remove: {list(sub_components_to_remove)}")
        if len(sub_components_to_remove) > 0:
            for ds in sub_components_to_remove:
                egeria_client.detach_sub_component(guid, ds, None)
                msg = f"Removed `{ds}` from component `{display_name}`"
                logger.trace(msg)
        sub_components_to_add = to_be_sub_components - as_is_sub_components
        logger.trace(f"sub_components_to_add: {list(sub_components_to_add)}")
        if len(sub_components_to_add) > 0:
            for ds in sub_components_to_add:
                egeria_client.link_subcomponent(guid, ds, None)
                msg = f"Added `{ds}` to component `{display_name}`"
                logger.trace(msg)

        actors_to_remove = to_be_actors - as_is_actors
        logger.trace(f"actors_to_remove: {list(actors_to_remove)}")
        if len(actors_to_remove) > 0:
            for actor in actors_to_remove:
                egeria_client.detach_component_from_role(actor, guid, None)
                msg = f"Removed actor `{actor}` from component `{display_name}`"
                logger.trace(msg)
        actors_to_add = to_be_actors - as_is_actors
        logger.trace(f"actors_to_add: {list(actors_to_add)}")
        if len(actors_to_add) > 0:
            for actor in actors_to_add:
                egeria_client.link_component_to_role(actor, guid, None)
                msg = f"Added `{display_name}` to role `{actor}`"
                logger.trace(msg)

        blueprints_to_remove = as_is_blueprints - to_be_blueprints
        logger.trace(f"blueprints_to_remove: {list(blueprints_to_remove)}")
        if len(blueprints_to_remove) > 0:
            for bp in blueprints_to_remove:
                egeria_client.detach_solution_component_from_blueprint(bp, guid)
                msg = f"Removed `{bp}` from `{display_name}`"
                logger.trace(msg)
        blueprints_to_add = to_be_blueprints - as_is_blueprints
        logger.trace(f"blueprints_to_add: {list(blueprints_to_add)}")
        if len(blueprints_to_add) > 0:
            for bp in blueprints_to_add:
                egeria_client.link_solution_component_to_blueprint(bp, guid)
                msg = f"Added `{bp}` to`{display_name}`"
                logger.trace(msg)
        logger.info(f"Replaced the related elements in `{display_name}`")

    else:  # merge - add field to related elements
        if sub_component_guids:
            for comp in sub_component_guids:
                egeria_client.link_subcomponent(guid, comp, None)
            msg = f"Added `{sub_component_guids}` to `{display_name}`"
            logger.trace(msg)

        if actor_guids:
            for actor in actor_guids:
                egeria_client.link_component_to_role(actor, guid, None)
            msg = f"Added `{actor_guids}` to `{display_name}`"
            logger.trace(msg)

        if in_blueprint_guids:
            for bp in in_blueprint_guids:
                egeria_client.link_solution_component_to_blueprint(bp, guid, None)
            msg = f"Added `{in_blueprint_guids}` to `{display_name}`"
            logger.trace(msg)
        logger.info(f"Merged related elements in `{display_name}`")


def sync_blueprint_related_elements(egeria_client: EgeriaTech, object_type: str, component_guids: list, guid: str,
                                    qualified_name: str, display_name: str, replace_all_props: bool = True) -> None:
    """Sync a blueprints related elements.

    """
    if replace_all_props:
        bp_element = egeria_client.get_solution_blueprint_by_guid(guid)
        solution_components = bp_element['solutionComponents']
        as_is_components = {}
        if len(solution_components) > 0:
            for component in solution_components:
                as_is_components.append(component['elementHeader']['guid'])

        # should I throw an exception if empty?

        to_be_components = set(component_guids) if component_guids is not None else set()

        logger.trace(f"as_is_components: {list(as_is_components)} to_be_sub_components: {list(to_be_components)}")

        components_to_remove = as_is_components - to_be_components
        logger.trace(f"components_to_remove: {list(components_to_remove)}")
        if len(components_to_remove) > 0:
            for ds in components_to_remove:
                egeria_client.detach_solution_component_from_blueprint(guid, ds, None)
                msg = f"Removed `{ds}` from component `{display_name}`"
                logger.trace(msg)
        components_to_add = to_be_components - as_is_components
        logger.trace(f"sub_components_to_add: {list(components_to_add)}")
        if len(components_to_add) > 0:
            for ds in components_to_add:
                egeria_client.link_solution_component_to_blueprint(guid, ds, None)
                msg = f"Added `{ds}` to component `{display_name}`"
                logger.trace(msg)

        logger.info(f"Replaced the related elements in `{display_name}`")

    else:  # merge - add field to related elements
        if component_guids:
            for comp in component_guids:
                egeria_client.link_solution_component_to_blueprint(guid, comp, None)
            msg = f"Added `{component_guids}` to `{display_name}`"
            logger.trace(msg)

        logger.info(f"Merged related elements in `{display_name}`")


@logger.catch
def process_blueprint_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a solution blueprint create or update object_action by extracting key attributes such as
    blueprint name, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes.get('Description', {}).get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    version_identifier = attributes.get('Version Identifier', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)
    external_source_guid = attributes.get('External Source GUID', {}).get('value', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True

    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None
    component_guids = attributes.get('Solution Components', {}).get('guid_list', None)

    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"object_action\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    body = body_slimmer({
                        "class": "UpdateSolutionBlueprintRequestBody", "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name, "effectiveTime": effective_time,
                        "forLineage": False, "forDuplicateProcessing": False, "properties": {
                            "class": "SolutionBlueprintProperties", "qualifiedName": qualified_name,
                            "displayName": display_name, "description": description, "version": version_identifier,
                            "additionalProperties": additional_properties, "extendedProperties": extended_properties,
                            "effectiveFrom": effective_from, "effectiveTo": effective_to
                            }
                        })

                egeria_client.update_solution_blueprint(guid, body, replace_all_props)
                logger.success(f"==> Updated  {object_type} `{display_name}` with GUID {guid}\n\n")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                sync_blueprint_related_elements(egeria_client, object_type, component_guids, guid, qualified_name,
                                                display_name, replace_all_props)
                logger.success(f"===> Updated {object_type} `{display_name}` related elements\n\n")
                return egeria_client.find_solution_blueprints(qualified_name, output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                elif not valid:
                    msg = (f"==>{object_type} `{display_name}` is not valid and can't be created")
                    logger.error(msg)
                    return
            else:
                body = {
                    "class": "NewSolutionBlueprintRequestBody", "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name, "forLineage": False, "forDuplicateProcessing": False,
                    "effectiveTime": effective_time, "anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor,
                    "anchorScopeGUID": anchor_scope_guid, "parentGUID": parent_guid,
                    "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                    "properties": {
                        "class": "SolutionBlueprintProperties", "effectiveFrom": effective_from,
                        "effectiveTo": effective_to,  # "typeName": type_name,
                        "extendedProperties": extended_properties, "qualifiedName": qualified_name,
                        "additionalProperties": additional_properties, "displayName": display_name,
                        "description": description, "version": version_identifier
                        }
                    }

                guid = egeria_client.create_solution_blueprint(body)
                if guid:
                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                        })
                    msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                    logger.success(msg)
                    return egeria_client.find_solution_blueprints(qualified_name, output_format='MD')
                else:
                    msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                    logger.error(msg)
                    return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


@logger.catch
def process_solution_component_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> \
        Optional[str]:
    """
    Processes a solution component create or update object_action by extracting key attributes such as
    component name, description, and parent components from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting component-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes.get('Description', {}).get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    version_identifier = attributes.get('Version Identifier', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)
    external_source_guid = attributes.get('External Source GUID', {}).get('value', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True

    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None

    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

    solution_component_type = attributes.get('Solution Component Type', {}).get('value', None)
    planned_deployed_impl_type = attributes.get('Planned Deployed Implementation Type', {}).get('value', None)
    sub_component_names = attributes.get('Solution SubComponents', {}).get('name_list', None)
    sub_component_guids = attributes.get('Solution SubComponents', {}).get('guid_list', None)
    actor_names = attributes.get('Actors', {}).get('name_list', None)
    actor_guids = attributes.get('Actors', {}).get('guid_list', None)
    in_blueprint_names = attributes.get('Solution Blueprints', {}).get('name_list', None)
    in_blueprint_guids = attributes.get('Solution Blueprints', {}).get('guid_list', None)

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            if object_action == "Update":
                if not exists:
                    msg = (f"==> Element `{display_name}` does not exist! Updating result document with Create."
                           f"object_action\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    logger.error(f"==> Element `{display_name}` entry is not valid. Please refer to the errors above.")
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                body = body_slimmer({
                    "class": "UpdateSolutionComponentRequestBody", "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name, "effectiveTime": effective_time, "forLineage": False,
                    "forDuplicateProcessing": False, "parentAtEnd1": parent_at_end1, "properties": {
                        "class": "SolutionComponentProperties", "qualifiedName": qualified_name,
                        "displayName": display_name, "description": description,
                        "solutionComponentType": solution_component_type,
                        "plannedDeployedImplementationType": planned_deployed_impl_type,
                        "additionalProperties": additional_properties, "extendedProperties": extended_properties,
                        "effectiveFrom": effective_from, "effectiveTo": effective_to
                        }
                    })

                egeria_client.update_solution_component(guid, body, replace_all_props)
                logger.success(f"==>Updated  {object_type} `{display_name}` with GUID {guid}\n")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                # Sync Parent Components and Blueprints
                sync_component_related_elements(egeria_client, object_type, sub_component_guids, actor_guids,
                                                in_blueprint_guids, guid, qualified_name, display_name,
                                                replace_all_props)
                logger.success(f"==>Updated  {object_type} `{display_name}` with related elements")
                return egeria_client.get_solution_component_by_guid(guid, output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (f"  {object_type} `{display_name}` already exists and result document updated changing "
                           f"`Create` to `Update` in processed output\n\n___")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                elif not valid:
                    msg = (f"==>{object_type} `{display_name}` is not valid and can't be created")
                    logger.error(msg)
                    return

                else:
                    body = body_slimmer({
                        "class": "NewSolutionComponentRequestBody", "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name, "forLineage": False,
                        "forDuplicateProcessing": False, "effectiveTime": effective_time, "anchorGUID": anchor_guid,
                        "isOwnAnchor": True, "anchorScopeGUID": anchor_scope_guid, "parentGUID": parent_guid,
                        "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                        "properties": {
                            "class": "SolutionComponentProperties", "effectiveFrom": effective_from,
                            "effectiveTo": effective_to, "extendedProperties": extended_properties,
                            "qualifiedName": qualified_name, "additionalProperties": additional_properties,
                            "displayName": display_name, "description": description,
                            "solutionComponentType": solution_component_type,
                            "plannedDeployedImplementationType": planned_deployed_impl_type

                            }
                        })

                    guid = egeria_client.create_solution_component(body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        if sub_component_guids:
                            for comp in sub_component_guids:
                                egeria_client.link_subcomponent(guid, comp, None)
                            msg = f"Added `{sub_component_guids}` to `{display_name}`"
                            logger.trace(msg)

                        if actor_guids:
                            for actor in actor_guids:
                                egeria_client.link_component_to_role(actor, guid, None)
                            msg = f"Added `{actor_guids}` to `{display_name}`"
                            logger.trace(msg)

                        if in_blueprint_guids:
                            for bp in in_blueprint_guids:
                                egeria_client.link_solution_component_to_blueprint(bp, guid, None)
                            msg = f"Added `{in_blueprint_guids}` to `{display_name}`"
                            logger.trace(msg)

                        return egeria_client.get_solution_component_by_guid(guid, output_format='MD')
                    else:
                        msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


@logger.catch
def process_information_supply_chain_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") \
        -> \
        Optional[str]:
    """
    Processes a solution blueprint create or update object_action by extracting key attributes such as
    blueprint name, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes.get('Description', {}).get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    version_identifier = attributes.get('Version Identifier', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)
    external_source_guid = attributes.get('External Source GUID', {}).get('value', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True

    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None

    scope = attributes.get('Scope', {}).get('value', None)
    purposes = attributes.get('Purposes', {}).get('value', None)
    segment_guids = attributes.get('Information Supply Chain Segments', {}).get('guid_list', None)

    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"object_action\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    body = body_slimmer({
                        "class": "UpdateInformationSupplyChainRequestBody", "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name, "effectiveTime": effective_time,
                        "forLineage": False, "forDuplicateProcessing": False, "properties": {
                            "class": "InformationSupplyChainProperties", "effectiveFrom": effective_from,
                            "effectiveTo": effective_to, "extendedProperties": extended_properties,
                            "qualifiedName": qualified_name, "additionalProperties": additional_properties,
                            "displayName": display_name, "description": description, "scope": scope,
                            "purposes": purposes, "version": version_identifier
                            }
                        })

                egeria_client.update_info_supply_chain(guid, body, replace_all_props)
                logger.success(f"==> Updated  {object_type} `{display_name}` with GUID {guid}\n\n")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                # sync_blueprint_related_elements(egeria_client,object_type, segment_guids, guid, qualified_name,
                # display_name, replace_all_props)
                # logger.success(f"===> Updated {object_type} `{display_name}` related elements\n\n")
                return egeria_client.get_info_supply_chain_by_guid(guid, output_format='MD')


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (
                        f"-->  Data Specification `{display_name}` already exists and result document updated changing "
                        f"`Create` to `Update` in processed output\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                elif valid is False:
                    msg = f"==>{object_type} `{display_name}` is not valid and can't be created"
                    logger.error(msg)
                    return
                else:
                    body = {
                        "class": "NewInformationSupplyChainRequestBody", "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name, "forLineage": False,
                        "forDuplicateProcessing": False, "effectiveTime": effective_time, "anchorGUID": anchor_guid,
                        "isOwnAnchor": is_own_anchor, "anchorScopeGUID": anchor_scope_guid, "parentGUID": parent_guid,
                        "parentRelationshipTypeName": parent_relationship_type_name, "parentAtEnd1": parent_at_end1,
                        "properties": {
                            "class": "InformationSupplyChainProperties", "effectiveFrom": effective_from,
                            "effectiveTo": effective_to, "extendedProperties": extended_properties,
                            "qualifiedName": qualified_name, "additionalProperties": additional_properties,
                            "displayName": display_name, "description": description, "scope": scope,
                            "purposes": purposes, "version": version_identifier
                            }
                        }

                    guid = egeria_client.create_info_supply_chain(body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"==>Created Element `{display_name}` with GUID {guid}\n"
                        logger.success(msg)
                        return egeria_client.get_info_supply_chain_by_guid(guid, output_format='MD')
                    else:
                        msg = f"==>Failed to create element `{display_name}` with GUID {guid}\n"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


@logger.catch
def process_information_supply_chain_segment_upsert_command(egeria_client: EgeriaTech, txt: str,
                                                            directive: str = "display") -> Optional[str]:
    """
    Processes a solution blueprint create or update object_action by extracting key attributes such as
    blueprint name, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes.get('Description', {}).get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    version_identifier = attributes.get('Version Identifier', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)
    external_source_guid = attributes.get('External Source GUID', {}).get('value', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True

    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None

    scope = attributes.get('Scope', {}).get('value', None)
    integration_style = attributes.get('Integration Style', {}).get('value', None)
    volumetrics = attributes.get('Estimated Volumetrics', {}).get('value', None)
    info_supply_chain = attributes.get('Information Supply Chain', {}).get('value', None)
    info_supply_chain_guid = attributes.get('Information Supply Chain', {}).get('guid', None)
    replace_all_props = not attributes.get('Merge Update', {}).get('value', True)

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"object_action\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    body = body_slimmer({
                        "class": "UpdateInformationSupplyChainSegmentRequestBody",
                        "externalSourceGUID": external_source_guid, "externalSourceName": external_source_name,
                        "effectiveTime": effective_time, "forLineage": False, "forDuplicateProcessing": False,
                        "properties": {
                            "class": "InformationSupplyChainSegmentProperties", "effectiveFrom": effective_from,
                            "effectiveTo": effective_to, "extendedProperties": extended_properties,
                            "qualifiedName": qualified_name, "additionalProperties": additional_properties,
                            "displayName": display_name, "description": description, "scope": scope,
                            "integrationStyle": integration_style, "estimatedVolumetrics": volumetrics,
                            "version": version_identifier
                            }
                        })

                egeria_client.update_info_supply_chain_segment(info_supply_chain_guid, body, replace_all_props)
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                logger.success(f"===> Updated {object_type} `{display_name}` with GUID {guid}\n")
                # sync_blueprint_related_elements(egeria_client,object_type, segment_guids, guid, qualified_name,
                # display_name, replace_all_props)
                # logger.success(f"===> Updated {object_type} `{display_name}` related elements\n\n")
                return egeria_client.get_info_supply_chain_segment_by_guid(guid, info_supply_chain_guid)


            elif object_action == "Create":
                if valid is False and exists:
                    msg = (
                        f"-->  Data Specification `{display_name}` already exists and result document updated changing "
                        f"`Create` to `Update` in processed output\n")
                    logger.error(msg)
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)

                elif valid is False:
                    msg = f"==>{object_type} `{display_name}` is not valid and can't be created"
                    logger.error(msg)
                    return
                else:
                    body = {
                        "class": "NewInformationSupplyChainSegmentRequestBody",
                        "externalSourceGUID": external_source_guid, "externalSourceName": external_source_name,
                        "forLineage": False, "forDuplicateProcessing": False, "effectiveTime": effective_time,
                        "anchorGUID": anchor_guid, "isOwnAnchor": is_own_anchor, "anchorScopeGUID": anchor_scope_guid,
                        "parentGUID": parent_guid, "parentRelationshipTypeName": parent_relationship_type_name,
                        "parentAtEnd1": parent_at_end1, "properties": {
                            "class": "InformationSupplyChainSegmentProperties", "effectiveFrom": effective_from,
                            "effectiveTo": effective_to, "extendedProperties": extended_properties,
                            "qualifiedName": qualified_name, "additionalProperties": additional_properties,
                            "displayName": display_name, "description": description, "scope": scope,
                            "integrationStyle": integration_style, "estimatedVolumetrics": volumetrics,
                            "version": version_identifier
                            }
                        }

                    guid = egeria_client.create_info_supply_chain_segment(info_supply_chain_guid, body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"==>Created Element `{display_name}` with GUID {guid}\n"
                        logger.success(msg)
                        return egeria_client.get_info_supply_chain_segment_by_guid(guid, info_supply_chain_guid)
                    else:
                        msg = f"==>Failed to create element `{display_name}` with GUID {guid}\n"
                        logger.error(msg)
                        return None

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


@logger.catch
def process_information_supply_chain_link_unlink_command(egeria_client: EgeriaTech, txt: str,
                                                         directive: str = "display") -> Optional[str]:
    """
    Processes a solution blueprint create or update object_action by extracting key attributes such as
    blueprint name, description, and usage from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    segment1 = attributes.get('Segment1', {}).get('guid', None)
    segment2 = attributes.get('Segment1', {}).get('guid', None)
    label = attributes.get('Link Label', {}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    external_source_guid = attributes.get('External Source GUID', {}).get('value', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)

    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)

    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None

    if directive == "display":

        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
        return valid

    elif directive == "process":
        try:
            if object_action == "Detach":
                if not exists:
                    msg = (f" Link `{label}` does not exist! Updating result document with Link "
                           f"object_action\n")
                    logger.error(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    body = body_slimmer({
                        "class": "MetadataSourceRequestBody", "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name, "effectiveTime": effective_time,
                        "forLineage": False, "forDuplicateProcessing": False

                        })

                egeria_client.detach_info_supply_chain_segments(segment1, segment2, body)

                logger.success(f"===> Detached segment with {label} from `{segment1}`to {segment2}\n")
                out = parsed_output['display'].replace('Detach', 'Link', 1)

                return (out)


            elif object_action == "Link":
                if valid is False and exists:
                    msg = (f"-->  Link called `{label}` already exists and result document updated changing "
                           f"`Link` to `Detach` in processed output\n")
                    logger.error(msg)

                elif valid is False:
                    msg = f"==>{object_type} Link with label `{label}` is not valid and can't be created"
                    logger.error(msg)
                    return
                else:
                    body = {
                        "class": "InformationSupplyChainLinkRequestBody", "effectiveTime": effective_time,
                        "forLineage": False, "forDuplicateProcessing": False, "properties": {
                            "class": "InformationSupplyChainLinkProperties", "label": label, "description": description,
                            "effectiveFrom": effective_from, "effectiveTo": effective_to
                            }
                        }

                    egeria_client.link_info_supply_chain_segments(segment1, segment2, body)
                    msg = f"==>Created {object_type} link named `{label}`\n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

@logger.catch
def process_sol_arch_list_command(egeria_client: EgeriaTech, txt: str, kind:str, directive: str = "display" ) -> Optional[str]:
    """
    Processes Solution Blueprint list object_action by extracting key attributes such as
     search string from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting term-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    attributes = parsed_output['attributes']

    valid = parsed_output['valid']

    print(Markdown(parsed_output['display']))

    if directive == "display":
        return None
    elif directive == "validate":
        if valid:
            print(Markdown(f"==> Validation of {command} completed successfully!\n"))
        else:
            msg = f"Validation failed for object_action `{command}`\n"
            logger.error(msg)
        return valid

    elif directive == "process":
        attributes = parsed_output['attributes']
        search_string = attributes.get('Search String', {}).get('value', '*')
        output_format = attributes.get('Output Format', {}).get('value', 'LIST')
        detailed = attributes.get('Detailed', {}).get('value', False)

        match kind:
            case "Solution Blueprints":
                find_proc = egeria_client.find_solution_blueprints
            case "Information Supply Chains":
                find_proc = egeria_client.find_information_supply_chains
            case "Solution Components":
                find_proc = egeria_client.find_solution_components
            case "Solution Roles":
                find_proc = egeria_client.find_solution_roles

        try:
            if not valid:  # First validate the command before we process it
                msg = f"Validation failed for {object_action} `{object_type}`\n"
                logger.error(msg)
                return None

            list_md = f"\n# {kind} with filter: `{search_string}`\n\n"
            if output_format == "DICT":
                struct = find_proc(search_string, output_format=output_format)
                list_md += f"```{json.dumps(struct, indent=4)}```\n"
            else:
                list_md += find_proc(search_string, output_format=output_format)
            logger.info(f"Wrote Output for search string: `{search_string}`")

            return list_md

        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            console.print_exception(show_locals=True)
            return None
    else:
        return None
