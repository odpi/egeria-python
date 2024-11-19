<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->
# Overview

# Command Line Interfaces

## hey_egeria

## hey_egeria_cat

## hey_egeria_my

## hey_egeria_ops

## hey_egeria_tech

# Command Reference

| Command                            | Purpose                                             | Cat | My | Ops | Tech | python |
|------------------------------------|-----------------------------------------------------|-----|----|-----|------|--------|
| change_todo_status                 | Update a ToDo item status                           |     | ✓  |     |      |        |
| create_glossary                    | Create a new glossary                               | ✓   |    |     |      |        |
| create_term                        | Create a new term                                   | ✓   |    |     |      |        |
| create_todo                        | Create a new ToDo item                              |     | ✓  |     |      |        |
| delete_glossary                    | Delete the specified glossary                       | ✓   |    |     |      |        |
| delete_term                        | Delete the specified term                           | ✓   |    |     |      |        |
| export_terms_to_file               | Export the specified glossary                       | ✓   |    |     |      |        |
| get_asset_graph                    | Display a tree graph of information about an asset  | ✓   |    |     |      |        |
| get_collection                     | Display a information about a collection            | ✓   |    |     |      |        |
| get_element_graph                  | Return a table of elements and matching elements    |     |    |     | ✓    |        |
| get_element_info                   | Display elements of a specific Open Metadata Type   |     |    |     | ✓    |        |
| get_guid_info                      | Display information about GUID specified object     |     |    |     | ✓    |        |
| get_project_dependencies           | Show the dependencies of a project from a root      | ✓   |    |     |      |        |
| get_project_structure              | Show the organization structure of a project        | ✓   |    |     |      |        |
| get_tech_details                   | Show details about a particular technology type     |     |    |     | ✓    |        |
| get_tech_type_elements             | Display elements of a specific technology type      | ✓   |    |     |      |        |
| get_tech_type_template             | Display the templates defined for a technology type | ✓   |    |     |      |        |
| hey_egeria                         | Textual User Interface for the pyegeria commands    |     |    |     |      |        |
| hey_egeria_cat                     | Textual User Interface for catalog use              |     |    |     |      |        |
| hey_egeria_my                      | Textual User Interface for personal use             |     |    |     |      |        |
| hey_egeria_ops                     | Textual User Interface for operations use           |     |    |     |      |        |
| hey_egeria_tech                    | Textual User Interface for technical use            |     |    |     |      |        |
| list_archives                      | Display the available archives known to Egeria      | ✓   |    |     |      |        |
| list_asset_types                   | List the types of assets known to Egeria            |     |    |     | ✓    |        |
| list_assets                        | Find and display assets in a domain                 | ✓   |    |     |      |        |
| list_catalog_targets               | List the catalog target details for a connection    |     |    | ✓   |      | ✓      |
| list_cert_types                    | List certification types                            | ✓   |    |     |      |        |
| list_deployed_catalogs             | List deployed catalogs                              | ✓   |    |     |      | ✓      |
| list_deployed_databases            | List deployed databases                             | ✓   |    |     |      | ✓      |
| list_deployed_schemas              | List deployed schemas                               | ✓   |    |     |      | ✓      |
| list_deployed_servers              | List deployed servers                               | ✓   |    |     |      |        |
| list_elements                      | Display table of Elements of an Open Metadata type  |     |    |     | ✓    |        |
| list_elements_for_classification   | List the elements of a classification               |     |    |     | ✓    |        |
| list_engine_activity               | List engine activity                                |     |    | ✓   |      |        |
| list_engine_activity_compressed    | Compressed view of engine activity                  |     |    | ✓   |      | ✓      |
| list_glossaries                    | List glossaries                                     | ✓   |    |     |      | ✓      |
| list_gov_action_processes          | List governance action processes                    |     |    |     | ✓    |        |
| list_gov_eng_status                | List the status of the governance engines           |     |    | ✓   |      | ✓      |
| list_integ_daemon_status           | List status of an integration daemon server         |     |    | ✓   |      | ✓      |
| list_my_profile                    | List the details of the current user profile        |     | ✓  |     |      |        |
| list_my_roles                      | List the roles of the current user                  |     | ✓  |     |      |        |
| list_projects                      | List projects filtered by search string             | ✓   |    |     |      |        |
| list_registered_services           | List all registered Egeria services                 |     |    |     | ✓    |        |
| list_related_elements              | List elements related to a specific element         |     |    |     | ✓    |        |
| list_related_specification         | List details of related elements                    |     |    |     | ✓    |        |
| list_relationship_types            | List types of relationships and their attributes    |     |    |     | ✓    |        |
| list_relationships                 | List relationships for elements of a given type     | ✓   |    |     |      |        |
| list_tech_templates                |                                                     |     |    |     | ✓    |        |
| list_tech_types                    |                                                     | ✓   |    |     |      |        |
| list_terms                         |                                                     | ✓   |    |     |      | ✓      |
| list_todos                         |                                                     | ✓   |    |     |      |        |
| list_user_ids                      | Display table of known user ids                     | ✓   |    |     |      |        |
| list_valid_metadata_values         |                                                     |     |    |     | ✓    |        |
| load_archive                       |                                                     |     |    | ✓   |      |        |
| load_archive_tui                   |                                                     |     |    | ✓   |      |        |
| load_terms_from_file               |                                                     | ✓   |    |     |      |        |
| mark_todo_complete                 |                                                     |     | ✓  |     |      |        |
| monitor_asset_events               |                                                     |     |    | ✓   |      |        |
| monitor_coco_status                |                                                     |     |    | ✓   |      |        |
| monitor_engine_activity            |                                                     |     |    | ✓   |      |        |
| monitor_engine_activity_compressed |                                                     |     |    | ✓   |      |        |
| monitor_gov_eng_status             |                                                     |     |    | ✓   |      |        |
| monitor_integ_daemon_status        |                                                     |     |    | ✓   |      |        |
| monitor_my_todos                   |                                                     |     | ✓  |     |      |        |
| monitor_open_todos                 |                                                     |     | ✓  |     |      |        |
| monitor_platform_status            |                                                     |     |    | ✓   |      |        |
| monitor_server_list                |                                                     |     |    | ✓   |      |        |
| monitor_server_startup             |                                                     |     |    | ✓   |      |        |
| monitor_server_status              |                                                     |     |    | ✓   |      |        |
| reassign_todo                      |                                                     |     | ✓  |     |      |        |
| refresh_gov_eng_config             |                                                     |     |    | ✓   |      |        |
| refresh_integration_daemon         |                                                     |     |    | ✓   |      |        |
| restart_integration_daemon         |                                                     |     |    | ✓   |      |        |
| start_daemon                       |                                                     |     |    | ✓   |      |        |
| stop_daemon                        |                                                     |     |    | ✓   |      |        |

----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.