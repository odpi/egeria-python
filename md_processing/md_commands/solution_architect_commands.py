"""
This file contains blueprint/solution-related object_action functions for processing Egeria Markdown
"""

import json
import sys
from datetime import datetime
from typing import Optional

from loguru import logger
from pygments.lexers import blueprint
from rich import print
from rich.console import Console
from rich.markdown import Markdown

from md_processing.md_processing_utils.common_md_proc_utils import (parse_upsert_command, parse_view_command)
from md_processing.md_processing_utils.common_md_utils import update_element_dictionary, set_element_prop_body, \
    set_update_body, set_create_body, add_search_keywords, add_note_in_dr_e
from md_processing.md_processing_utils.extraction_utils import (extract_command_plus, update_a_command)
from md_processing.md_processing_utils.md_processing_constants import (load_commands)
from pyegeria import body_slimmer, EgeriaTech, PyegeriaException, print_basic_exception

load_commands('commands.json')

console = Console(width=int(200))


@logger.catch
def sync_chain_related_elements(egeria_client: EgeriaTech, guid:str, in_supply_chain_guids:list, display_name:str,
                                merge_update:bool):
    if not merge_update:
        rel_el_list = egeria_client._get_supply_chain_rel_elements(guid)
        if rel_el_list is None:
            logger.warning("Unexpected -> the list was None - assigning empty list")
            rel_el_list = {}

        as_is_parent_guids = set(rel_el_list.get("parent_guids", []))

        to_be_parent_guids = set(in_supply_chain_guids) if in_supply_chain_guids is not None else set()

        logger.trace(
            f"as_is_parent supply chains: {list(as_is_parent_guids)} to_be_parent supply chains: {list(to_be_parent_guids)}")


        parent_guids_to_remove =  as_is_parent_guids - to_be_parent_guids
        logger.trace(f"parent_guids_to_remove: {list(parent_guids_to_remove)}")
        if len(parent_guids_to_remove) > 0:
            for parent_guid in parent_guids_to_remove:
                egeria_client.decompose_info_supply_chains(parent_guid, guid,  None)
                msg = f"Removed `{display_name}` from supply chain parent `{parent_guid}`"
                logger.trace(msg)

        parent_guids_to_add = to_be_parent_guids - as_is_parent_guids
        logger.trace(f"parent supply chains_to_add: {list(parent_guids_to_add)}")
        if len(parent_guids_to_add) > 0:
            for parent_guid in parent_guids_to_add:
                egeria_client.compose_info_supply_chains(parent_guid, guid, None)
                msg = f"Added `{display_name}` to supply chain parent `{parent_guid}`"
                logger.trace(msg)

    else:  # merge - add supply chain to parents
        if in_supply_chain_guids:
            for parent_guid in in_supply_chain_guids:
                egeria_client.compose_info_supply_chains(parent_guid, guid, None)
                msg = f"Added `{display_name}` to supply chain `{parent_guid}`"
                logger.trace(msg)



@logger.catch
def sync_component_related_elements(egeria_client: EgeriaTech, object_type: str,
                                    supply_chain_guids: list, parent_component_guids: list,
                                    actor_guids: list, in_blueprint_guids: list, keywords: list[str], guid: str, qualified_name: str,
                                    display_name: str, merge_update: bool = True) -> None:
    """Sync a components related elements.

    """
    if not merge_update:
        rel_el_list = egeria_client.get_component_related_elements(guid)
        # should I throw an exception if empty?

        as_is_actors = set(rel_el_list.get("actor_guids", []))
        as_is_blueprints = set(rel_el_list.get("blueprint_guids", []))
        as_is_parent_components = set(rel_el_list.get("parent_component_guids", []))
        as_is_supply_chains = set(rel_el_list.get("supply_chain_guids", []))
        as_is_keywords_list = set(rel_el_list.get("keywords_list", {}))
        as_is_keywords = set(rel_el_list.get("keywords_list", {}).keys())


        to_be_actors = set(actor_guids) if actor_guids is not None else set()
        to_be_blueprints = set(in_blueprint_guids) if in_blueprint_guids is not None else set()
        to_be_parent_components = set(parent_component_guids) if parent_component_guids is not None else set()
        to_be_supply_chains = set(supply_chain_guids) if supply_chain_guids is not None else set()
        to_be_keywords_list = set(keywords) if keywords is not None else set()


        logger.trace(
            f"as_is_sub_components: {list(as_is_parent_components)} to_be_sub_components: {list(to_be_parent_components)}")
        logger.trace(f"as_is_actors: {list(as_is_actors)} to_be_actors: {list(to_be_actors)}")
        logger.trace(f"as_is_blueprints: {list(as_is_blueprints)} to_be_blueprints: {list(to_be_blueprints)}")

        keywords_to_add = to_be_keywords_list - as_is_keywords
        logger.trace(f"keywords_to_add: {list(keywords_to_add)}")
        if len(keywords_to_add) > 0:
            for ds in keywords_to_add:
                egeria_client.add_search_keyword_to_element(guid, ds)
                msg = f"Added `{ds}` to component `{guid}`"
                logger.trace(msg)

        keywords_to_remove = as_is_keywords_list - to_be_keywords_list
        logger.trace(f"keyword_to_remove: {list(keywords_to_remove)}")
        if len(keywords_to_remove) > 0:
            for ds in keywords_to_remove: ## change structure of get related elements to return pairs of keywords and guids
                egeria_client.remove_search_keyword(rel_el_list['keywords_list'][ds])
                msg = f"Removed `{ds}` from component `{guid}`"
                logger.trace(msg)

        parent_components_to_remove = as_is_parent_components - to_be_parent_components
        logger.trace(f"sub_components_to_remove: {list(parent_components_to_remove)}")
        if len(parent_components_to_remove) > 0:
            for ds in parent_components_to_remove:
                egeria_client.detach_sub_component(ds, guid, None)
                msg = f"Removed `{display_name}` from component `{ds}`"
                logger.trace(msg)



        parent_components_to_add = to_be_parent_components - as_is_parent_components
        logger.trace(f"parent_components_to_add: {list(parent_components_to_add)}")
        if len(parent_components_to_add) > 0:
            for ds in parent_components_to_add:
                egeria_client.link_subcomponent(ds, guid, None)
                msg = f"Added `{display_name}` to component `{ds}`"
                logger.trace(msg)

        blueprints_to_remove = as_is_blueprints - to_be_blueprints
        logger.trace(f"blueprints_to_remove: {list(blueprints_to_remove)}")
        if len(blueprints_to_remove) > 0:
            for bp in blueprints_to_remove:
                egeria_client.detach_solution_component_from_blueprint(bp, guid, None)
                msg = f"Removed `{display_name}` from blueprintt `{bp}`"
                logger.trace(msg)

        blueprints_to_add = to_be_blueprints - as_is_blueprints
        logger.trace(f"blueprints_to_add: {list(blueprints_to_add)}")
        if len(blueprints_to_add) > 0:
            for bp in blueprints_to_add:
                egeria_client.link_solution_component_to_blueprint(bp, guid, None)
                msg = f"Added `{display_name}` to component `{bp}`"
                logger.trace(msg)



        actors_to_remove = to_be_actors - as_is_actors
        logger.trace(f"actors_to_remove: {list(actors_to_remove)}")
        if len(actors_to_remove) > 0:
            for actor in actors_to_remove:
                egeria_client.detach_component_actore(actor, guid, None)
                msg = f"Removed actor `{actor}` from component `{display_name}`"
                logger.trace(msg)

        actors_to_add = to_be_actors - as_is_actors
        logger.trace(f"actors_to_add: {list(actors_to_add)}")
        if len(actors_to_add) > 0:
            for actor in actors_to_add:
                egeria_client.link_component_to_actor(actor, guid, None)
                msg = f"Added `{display_name}` to role `{actor}`"
                logger.trace(msg)

        supply_chains_to_remove = as_is_supply_chains - to_be_supply_chains
        logger.trace(f"supply_chains_to_remove: {list(supply_chains_to_remove)}")
        if len(supply_chains_to_remove) > 0:
            for isc in supply_chains_to_remove:
                egeria_client.detach_design_from_implementation(isc, guid)
                msg = f"Removed `{isc}` from `{display_name}`"
                logger.trace(msg)
        supply_chains_to_add = to_be_supply_chains - as_is_supply_chains
        logger.trace(f"supply_chains_to_add: {list(supply_chains_to_add)}")
        if len(supply_chains_to_add) > 0:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ImplementedByProperties",
                    "description": "a blank description to satisfy the Egeria gods"
                    }
                }
            for isc in supply_chains_to_add:
                egeria_client.link_design_to_implementation(isc, guid, body)
                msg = f"Added `{isc}` to`{display_name}`"
                logger.trace(msg)
            logger.info(f"Replaced the related elements in `{display_name}`")

    else:  # merge - add field to related elements
        if parent_component_guids:
            for comp in parent_component_guids:
                egeria_client.link_subcomponent(guid, comp, None)
                msg = f"Added `{parent_component_guids}` to `{display_name}`"
                logger.trace(msg)

        if actor_guids:
            for actor in actor_guids:
                egeria_client.link_component_to_actor(actor, guid, None)
                msg = f"Added `{actor_guids}` to `{display_name}`"
                logger.trace(msg)

        if in_blueprint_guids:
            for bp in in_blueprint_guids:
                egeria_client.link_solution_component_to_blueprint(bp, guid, None)
                msg = f"Added `{in_blueprint_guids}` to `{display_name}`"
                logger.trace(msg)

        if keywords:
            add_search_keywords(egeria_client, guid, keywords)

        if supply_chain_guids:
            body = {
                "class": "NewRelationshipRequestBody",
                "properties": {
                    "class": "ImplementedByProperties",
                    "description": "a blank description to satisfy the Egeria gods"
                }
            }
            for isc in supply_chain_guids:
                egeria_client.link_design_to_implementation(isc, guid, body)
                msg = f"Added `{display_name}` to `{isc}`"
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
    print(Markdown(f"# {command}\n"))
    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)
    journal_entry = parsed_output.get('Journey Entry', {}.get('value', None))
    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes.get('Description', {}).get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    search_keywords = attributes['Search Keywords'].get('value', None)



    component_guids = attributes.get('Solution Components', {}).get('guid_list', None)

    status = attributes.get('Status', {}).get('value', None)
    if status is None:
        status = "ACTIVE"

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
        prop_body = set_element_prop_body(object_type, qualified_name, attributes)

        try:
            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"object_action\n")
                    logger.error(msg)
                    print(Markdown(msg))
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    body = set_update_body(object_type, attributes)
                    body['properties'] = prop_body
                    egeria_client.update_solution_blueprint(guid, body)
                    if status:
                        egeria_client.update_solution_element_status(guid, status)

                    msg = f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___"
                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                    })
                    logger.success(msg)
                    sync_blueprint_related_elements(egeria_client, object_type, component_guids, guid, qualified_name,
                                                    display_name, replace_all_props)

                    journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name, journal_entry)
                    logger.success(f"===> Updated {object_type} `{display_name}` related elements\n\n")
                    return egeria_client.get_solution_blueprints_by_name(qualified_name, output_format='MD', report_spec = "Solution-Blueprint-DrE")


            elif object_action == "Create":
                print(f"valid: {valid}, type: {type(valid)}")
                try:
                    if valid is False and exists:
                        msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                               f"`Create` to `Update` in processed output\n\n___")
                        logger.error(msg)
                        print(Markdown(msg))
                        return update_a_command(txt, object_action, object_type, qualified_name, guid)

                    elif not valid:
                        msg = (f"==>{object_type} `{display_name}` is not valid and can't be created")
                        print(Markdown(msg))
                        logger.error(msg)
                        return

                    else:
                        body = set_create_body(object_type,attributes)
                        body['properties'] = prop_body
                        guid = egeria_client.create_solution_blueprint(body)
                except Exception as e:
                    print(f"Unexpected error: {e}, {type(valid)}, {valid}")


                if guid:
                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                        })
                    journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name, journal_entry)
                    msg = f"\n\nCreated Element `{display_name}` with GUID {guid}\n\n___"
                    print(Markdown(msg))
                    logger.success(msg)
                    return egeria_client.get_solution_blueprint_by_guid(guid, output_format='MD', report_spec = "Solution-Blueprint-DrE")
                else:
                    msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                    print(Markdown(msg))
                    logger.error(msg)
                    return None

        except PyegeriaException as e:
            print_basic_exception(e)
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None


# TODO - I think this comes after (or part of) doing the Actors
@logger.catch
def process_solution_roles_upsert_command(egeria_client: EgeriaTech, txt: str, directive: str = "display") -> Optional[str]:
    """
    Processes a solution role create or update object_action by extracting key attributes such as from the given text.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))
    parsed_output = parse_upsert_command(egeria_client, object_type, object_action, txt, directive)

    valid = parsed_output['valid']
    exists = parsed_output['exists']

    qualified_name = parsed_output.get('qualified_name', None)
    guid = parsed_output.get('guid', None)
    journal_entry = parsed_output.get('Journey Entry', {}.get('value', None))
    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']
    description = attributes.get('Description', {}).get('value', None)
    display_name = attributes['Display Name'].get('value', None)
    search_keywords = attributes['Search Keywords'].get('value', None)



    component_guids = attributes.get('Solution Components', {}).get('guid_list', None)

    status = attributes.get('Status', {}).get('value', None)
    if status is None:
        status = "ACTIVE"

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
        prop_body = set_element_prop_body(object_type, qualified_name, attributes)

        try:
            if object_action == "Update":
                if not exists:
                    msg = (f" Element `{display_name}` does not exist! Updating result document with Create "
                           f"object_action\n")
                    logger.error(msg)
                    print(Markdown(msg))
                    return update_a_command(txt, object_action, object_type, qualified_name, guid)
                elif not valid:
                    return None
                else:
                    print(Markdown(
                        f"==> Validation of {command} completed successfully! Proceeding to apply the changes.\n"))

                    body = set_update_body(object_type, attributes)
                    body['properties'] = prop_body
                    egeria_client.update_solution_blueprint(guid, body)
                    if status:
                        egeria_client.update_solution_element_status(guid, status)

                    msg = f"Updated  {object_type} `{display_name}` with GUID {guid}\n\n___"
                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                    })
                    logger.success(msg)
                    sync_blueprint_related_elements(egeria_client, object_type, component_guids, guid, qualified_name,
                                                    display_name, replace_all_props)

                    journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name, journal_entry)
                    logger.success(f"===> Updated {object_type} `{display_name}` related elements\n\n")
                    return egeria_client.get_solution_blueprints_by_name(qualified_name, output_format='MD', report_spec = "Solution-Blueprint-DrE")


            elif object_action == "Create":
                print(f"valid: {valid}, type: {type(valid)}")
                try:
                    if valid is False and exists:
                        msg = (f"  Data Specification `{display_name}` already exists and result document updated changing "
                               f"`Create` to `Update` in processed output\n\n___")
                        logger.error(msg)
                        print(Markdown(msg))
                        return update_a_command(txt, object_action, object_type, qualified_name, guid)

                    elif not valid:
                        msg = (f"==>{object_type} `{display_name}` is not valid and can't be created")
                        print(Markdown(msg))
                        logger.error(msg)
                        return

                    else:
                        body = set_create_body(object_type,attributes)
                        body['properties'] = prop_body
                        guid = egeria_client.create_solution_blueprint(body)
                except Exception as e:
                    print(f"Unexpected error: {e}, {type(valid)}, {valid}")


                if guid:
                    update_element_dictionary(qualified_name, {
                        'guid': guid, 'display_name': display_name
                        })
                    journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name, journal_entry)
                    msg = f"\n\nCreated Element `{display_name}` with GUID {guid}\n\n___"
                    print(Markdown(msg))
                    logger.success(msg)
                    return egeria_client.get_solution_blueprint_by_guid(guid, output_format='MD', report_spec = "Solution-Blueprint-DrE")
                else:
                    msg = f"Failed to create element `{display_name}` with GUID {guid}\n\n___"
                    print(Markdown(msg))
                    logger.error(msg)
                    return None

        except PyegeriaException as e:
            print_basic_exception(e)
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
    print(Markdown(f"# {command}\n"))

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
    solution_component_type = attributes.get('Solution Component Type', {}).get('value', None)
    planned_deployed_impl_type = attributes.get('Planned Deployed Implementation Type', {}).get('value', None)
    initial_status = attributes.get('Status', {}).get('value', None)
    url = attributes.get('URL', {}).get('value', None)
    search_keywords = attributes.get('Search Keywords', {}).get('value', None)
    journal_entry = attributes.get('Journal Entry', {}).get('value', None)
    user_defined_status = attributes.get('User Defined Status', {}).get('value', None)
    if initial_status != "OTHER":
        user_defined_status = None

    # sub_component_names = attributes.get('Solution SubComponents', {}).get('name_list', None)
    # sub_component_guids = attributes.get('Solution SubComponents', {}).get('guid_list', None)
    actor_names = attributes.get('Actors', {}).get('name_list', None)
    actor_guids = attributes.get('Actors', {}).get('guid_list', None)
    in_blueprint_names = attributes.get('In Solution Blueprints', {}).get('name_list', None)
    in_blueprint_guids = attributes.get('In Solution Blueprints', {}).get('guid_list', None)
    in_supply_chain_names = attributes.get('In Information Supply Chains', {}).get('name_list', None)
    in_supply_chain_guids = attributes.get('In Information Supply Chains', {}).get('guid_list', None)
    in_component_names = attributes.get('In Solution Components', {}).get('name_list', None)
    in_component_guids = attributes.get('In Solution Components', {}).get('guid_list', None)
    parent_component_guids = attributes.get('Parent Components', {}).get('guid_list', None)
    parent_component_names = attributes.get('Parent Components', {}).get('name_list', None)

    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)
    external_source_guid = attributes.get('External Source GUID', {}).get('value', None)
    external_source_name = attributes.get('External Source Name', {}).get('value', None)

    anchor_guid = attributes.get('Anchor ID', {}).get('guid', None)
    parent_guid = attributes.get('Parent ID', {}).get('guid', None)
    parent_relationship_type_name = attributes.get('Parent Relationship Type Name', {}).get('value', None)
    parent_relationship_properties = attributes.get('Parent Relationship Properties', {}).get('value', None)
    parent_at_end1 = attributes.get('Parent at End1', {}).get('value', True)

    anchor_scope_guid = attributes.get('Anchor Scope GUID', {}).get('value', None)
    is_own_anchor = attributes.get('Is Own Anchor', {}).get('value', True)
    if parent_guid is None:
        is_own_anchor = True

    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None

    merge_update = attributes.get('Merge Update', {}).get('value', True)



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
                    "class": "UpdateElementRequestBody",
                    "externalSourceGUID": external_source_guid,
                    "externalSourceName": external_source_name,
                    "effectiveTime": effective_time,
                    "mergeUpdate": merge_update,
                    "forLineage": False,
                    "forDuplicateProcessing": False,
                    "properties": {
                        "class": "SolutionComponentProperties",
                        "qualifiedName": qualified_name,
                        "displayName": display_name,
                        "description": description,
                        "solutionComponentType": solution_component_type,
                        "plannedDeployedImplementationType": planned_deployed_impl_type,
                        "additionalProperties": additional_properties,
                        "extendedProperties": extended_properties,
                        "effectiveFrom": effective_from,
                        "effectiveTo": effective_to,
                        "URL": url
                        }
                    })

                egeria_client.update_solution_component(guid, body)
                msg = f"\n==>Updated  {object_type} `{display_name}` with GUID {guid}\n"
                logger.success(msg)
                print(Markdown(msg))
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                # Sync Parent Components and Blueprints
                sync_component_related_elements(egeria_client, object_type ,
                                                in_supply_chain_guids,parent_component_guids,actor_guids,
                                                in_blueprint_guids, search_keywords, guid, qualified_name,
                                                display_name,
                                                merge_update)

                if journal_entry:
                    journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name, journal_entry)
                return egeria_client.get_solution_component_by_guid(guid, output_format='MD', report_spec = "Solution-Component-DrE")


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
                        "class": "NewElementRequestBody",
                        "anchorGUID": anchor_guid,
                        "isOwnAnchor": is_own_anchor,
                        "parentGUID": parent_guid,
                        "parentRelationshipTypeName": parent_relationship_type_name,
                        "parentRelationshipProperties": parent_relationship_properties,
                        "parentAtEnd1": parent_at_end1,
                        "properties": {
                            "class": "SolutionComponentProperties",
                            "qualifiedName": qualified_name,
                            "displayName": display_name,
                            "description": description,
                            "solutionComponentType": solution_component_type,
                            "versionIdentifier" : version_identifier,
                            "plannedDeployedImplementationType": planned_deployed_impl_type,
                            "userDefinedStatus" : user_defined_status,
                            "additionalProperties": additional_properties,
                            "extendedProperties": extended_properties,
                            "effectiveFrom": effective_from,
                            "effectiveTo": effective_to,
                            "URL": url
                        },
                        "initialStatus": initial_status,
                        "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name,
                        "effectiveTime": effective_time,
                        "forLineage": False,
                        "forDuplicateProcessing": False
                    })

                    guid = egeria_client.create_solution_component(body)
                    if guid:
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        msg = f"\n\n==> Created Element `{display_name}` with GUID {guid}\n\n___"
                        logger.success(msg)
                        print(Markdown(msg))

                        if search_keywords:
                            add_search_keywords(egeria_client, guid, search_keywords)

                        if in_component_guids:
                            for comp in in_component_guids:
                                egeria_client.link_subcomponent(comp, guid, None)
                            msg = f"Added to parent components `{in_component_names}` "
                            logger.trace(msg)

                        if actor_guids:
                            for actor in actor_guids:
                                egeria_client.link_component_to_actor(actor, guid, None)
                            msg = f"Added `{actor_guids}` to `{display_name}`"
                            logger.trace(msg)

                        if in_blueprint_guids:
                            for bp in in_blueprint_guids:
                                egeria_client.link_solution_component_to_blueprint(bp, guid, None)
                            msg = f"Added  `{display_name}`to blueprints `{in_blueprint_names}`"
                            logger.trace(msg)

                        if in_supply_chain_guids:
                            for isc in in_supply_chain_guids:
                                egeria_client.link_design_to_implementation(isc, guid, None)
                            msg = f"Added  `{display_name}`to supply chain `{in_supply_chain_names}`"
                            logger.trace(msg)
                        journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name,
                                                              journal_entry)

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
def process_component_link_unlink_command(egeria_client: EgeriaTech, txt: str,
                                                         directive: str = "display") -> Optional[str]:
    """
    Processes a link or unlink command to wire solution components.

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    component1 = attributes.get('Component1', {}).get('guid', None)
    component2 = attributes.get('Component2', {}).get('guid', None)
    label = attributes.get('Wire Label', {}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)

    valid = parsed_output['valid']
    exists = component1 is not None and  component2 is not None


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
            if object_action == "Unlink":
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
                        "class": "MetadataSourceRequestBody",
                        "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name,
                        "effectiveTime": effective_time,
                        "forLineage": False,
                        "forDuplicateProcessing": False
                        })

                egeria_client.detach_solution_linking_wire(component1, component2, body)

                logger.success(f"===> Detached segment with {label} from `{component1}`to {component2}\n")
                out = parsed_output['display'].replace('Unlink', 'Link', 1)

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
                        "class": "NewRelationshipRequestBody",
                        "effectiveTime": effective_time,
                        "forLineage": False,
                        "forDuplicateProcessing": False,
                        "properties": {
                            "class": "SolutionLinkingWireProperties",
                            "label": label,
                            "description": description,
                            "effectiveFrom": effective_from,
                            "effectiveTo": effective_to
                            }
                        }

                    egeria_client.link_solution_linking_wire(component1, component2, body)
                    msg = f"==>Created {object_type} link named `{label}`\n"
                    logger.success(msg)
                    print(Markdown(msg))
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out

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
    print(Markdown(f"# {command}\n"))

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
    journal_entry = attributes.get('Journal Entry', {}).get('value', None)
    effective_time = attributes.get('Effective Time', {}).get('value', None)
    effective_from = attributes.get('Effective From', {}).get('value', None)
    effective_to = attributes.get('Effective To', {}).get('value', None)

    nested_supply_chain_guids = attributes.get('Nested Information Supply Chains', {}).get('guid_list', None)
    additional_prop = attributes.get('Additional Properties', {}).get('value', None)
    additional_properties = json.loads(additional_prop) if additional_prop is not None else None
    extended_prop = attributes.get('Extended Properties', {}).get('value', None)
    extended_properties = json.loads(extended_prop) if extended_prop is not None else None

    scope = attributes.get('Scope', {}).get('value', None)
    purposes = attributes.get('Purposes', {}).get('value', None)
    in_supply_chain_guids = attributes.get('In Information Supply Chain', {}).get('guid_list', None)
    merge_update = attributes.get('Merge Update', {}).get('value', True),


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
            prop_body = {
                "class": "InformationSupplyChainProperties", "effectiveFrom": effective_from,
                "effectiveTo": effective_to, "extendedProperties": extended_properties,
                "qualifiedName": qualified_name, "additionalProperties": additional_properties,
                "displayName": display_name, "description": description, "scope": scope,
                "purposes": purposes, "version": version_identifier
            }

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


                body = set_update_body("InformationSupplyChain", attributes)
                body['properties'] = prop_body
                egeria_client.update_info_supply_chain(guid, body)

                sync_chain_related_elements(egeria_client, guid, in_supply_chain_guids, display_name, merge_update)
                logger.success(f"==> Updated  {object_type} `{display_name}` with GUID {guid}\n\n")
                update_element_dictionary(qualified_name, {
                    'guid': guid, 'display_name': display_name
                    })
                journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name, journal_entry)

                logger.success(f"===> Updated {object_type} `{display_name}` related elements\n\n")
                return egeria_client.get_info_supply_chain_by_guid(guid, output_format='MD', report_spec = "Information-Supply-Chain-DrE")


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
                    body = set_create_body("InformationSupplyChain", attributes)
                    body['properties'] = prop_body

                    guid = egeria_client.create_info_supply_chain(body)
                    if guid:
                        msg = f"==>Created Element `{display_name}` with GUID {guid}\n"
                        logger.success(msg)
                        print(Markdown(msg))
                        update_element_dictionary(qualified_name, {
                            'guid': guid, 'display_name': display_name
                            })
                        if in_supply_chain_guids:
                            for nested_chain in in_supply_chain_guids:
                                egeria_client.compose_info_supply_chains(nested_chain, guid)

                        if journal_entry:
                            journal_entry_guid = add_note_in_dr_e(egeria_client, qualified_name, display_name,
                                                              journal_entry)
                        if nested_supply_chain_guids:
                            for nested_supply_chain in nested_supply_chain_guids:
                                egeria_client.compose_info_supply_chains(guid, nested_supply_chain)

                        msg = f"==>Created Element `{display_name}` Relationships\n"
                        logger.success(msg)
                        print(Markdown(msg))
                        return egeria_client.get_info_supply_chain_by_guid(guid, output_format='MD', report_spec="Information-Supply-Chain-DrE")
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
    Processes a link or unlink command to associate or break up peer supply chains..

    :param txt: A string representing the input cell to be processed for
        extracting blueprint-related attributes.
    :param directive: an optional string indicating the directive to be used - display, validate or execute
    :return: A string summarizing the outcome of the processing.
    """
    command, object_type, object_action = extract_command_plus(txt)
    print(Markdown(f"# {command}\n"))

    parsed_output = parse_view_command(egeria_client, object_type, object_action, txt, directive)

    print(Markdown(parsed_output['display']))

    logger.debug(json.dumps(parsed_output, indent=4))

    attributes = parsed_output['attributes']

    segment1 = attributes.get('Segment1', {}).get('guid', None)
    segment2 = attributes.get('Segment2', {}).get('guid', None)
    label = attributes.get('Link Label', {}).get('value', None)
    description = attributes.get('Description', {}).get('value', None)

    valid = parsed_output['valid']
    exists = segment1 is not None and  segment2 is not None


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
            if object_action == "Unlink":
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
                        "class": "DeleteRelationshipRequestBody",
                        "externalSourceGUID": external_source_guid,
                        "externalSourceName": external_source_name,
                        "effectiveTime": effective_time,
                        "forLineage": False,
                        "forDuplicateProcessing": False
                        })

                egeria_client.unlink_peer_info_supply_chains(segment1, segment2, body)

                logger.success(f"===> Detached segment with {label} from `{segment1}`to {segment2}\n")
                out = parsed_output['display'].replace('Unlink', 'Link', 1)

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
                        "class": "NewRelationshipRequestBody",
                        "effectiveTime": effective_time,
                        "forLineage": False,
                        "forDuplicateProcessing": False,
                        "properties": {
                            "class": "InformationSupplyChainLinkProperties",
                            "label": label,
                            "description": description,
                            "effectiveFrom": effective_from,
                            "effectiveTo": effective_to
                            }
                        }

                    egeria_client.link_peer_info_supply_chains(segment1, segment2, body)
                    msg = f"==>Created {object_type} link named `{label}`\n"
                    logger.success(msg)
                    out = parsed_output['display'].replace('Link', 'Detach', 1)
                    return out


        except Exception as e:
            logger.error(f"Error performing {command}: {e}")
            return None
    else:
        return None

