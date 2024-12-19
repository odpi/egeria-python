<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

# Overview

**hey_egeria** is a friendly, easy to use, command line interface (CLI) for Egeria with both a scriptable component and a textual user
interface to guide
users through the different commands and options. This interface is being actively maintained and enhanced. There are
currently about 70 commands in the interface and new ones are added based on perceived need and community feedback.

The CLI is written in python using the [click](https://click.palletsprojects.com/en/stable/) package
with [trogon](https://github.com/Textualize/trogon)
providing the textual user interface. The commands are written using [pyegeria](https://github.com/odpi/egeria-python)
or
https://pypi.org/project/pyegeria/. Commands are also available standalone. Simple standalone installation instructions
are
documented at [pyegeria](https://egeria-project.org/concepts/pyegeria). pyegeria and hey_egeria are pre-installed within
the **Egeria Workspaces** environment - [Egeria Workspaces](https://github.com/odpi/egeria-workspaces).

# Command Line Interfaces
## Commands
A command line interface provides a simple language for users to invoke commands. In the case of **hey_egeria**, once it
is installed, you can
start simply by typing `hey_egeria` on the command line and it will provide a list of options and commands that you can
use to interact with it. Commands are often arranged hierarchically - so, for instance if we type just `hey_egeria`, the
command options presented to us are:

```aiignore
Commands:
  cat   Commands for all users
  my    Work with my information
  ops   Commands to understand and manage operations
  tech  Commands for tech Users
  tui   Open Textual TUI
```

"cat", "my", "ops", and "tech" represent groups of commands oriented towards particular roles. If a user wants to only
use commands from a single role they can use a variant of hey_egeria that follows the pattern `hey_egeria_xxx`. So,
for example, `hey_egeria_cat` is the entry point for general catalog users.

Within each of these categories, commands are further split between **show** and **tell**. **Show** commands display
information to the user on the terminal and **tell** commands instruct Egeria to take some action. Commands may be further
sub-divided into topics.

So for example the command to display the status of the Egeria Platform is:

`hey_egeria ops show platforms status` 

And the command to list all glossaries is:

`hey_egeria cat show glossary glossaries`

## Options & Parameters

Each command has a number of optional, and often some mandatory parameters. There are really two groups of options.
* General options - that are present for every command. Sensible defaults based on environment variables are set for each.
* Command specific optons & parameters

# Command Reference

| Command                            | Purpose                                                      | Cat | My | Ops | Tech | python |
|------------------------------------|--------------------------------------------------------------|-----|----|-----|------|--------|
| change_todo_status                 | Update a ToDo item status                                    |     | ✓  |     |      |        |
| create_glossary                    | Create a new glossary                                        | ✓   |    |     |      |        |
| create_term                        | Create a new term                                            | ✓   |    |     |      |        |
| create_todo                        | Create a new ToDo item                                       |     | ✓  |     |      |        |
| delete_glossary                    | Delete the specified glossary                                | ✓   |    |     |      |        |
| delete_term                        | Delete the specified term                                    | ✓   |    |     |      |        |
| export_terms_to_file               | Export the specified glossary                                | ✓   |    |     |      |        |
| get_asset_graph                    | Display a tree graph of information about an asset           | ✓   |    |     |      |        |
| get_collection                     | Display a information about a collection                     | ✓   |    |     |      |        |
| get_element_graph                  | Return a table of elements and matching elements             |     |    |     | ✓    |        |
| get_element_info                   | Display elements of a specific Open Metadata Type            |     |    |     | ✓    |        |
| get_guid_info                      | Display information about GUID specified object              |     |    |     | ✓    |        |
| get_project_dependencies           | Show the dependencies of a project from a root               | ✓   |    |     |      |        |
| get_project_structure              | Show the organization structure of a project                 | ✓   |    |     |      |        |
| get_tech_details                   | Show details about a particular technology type              |     |    |     | ✓    |        |
| get_tech_type_elements             | Display elements of a specific technology type               | ✓   |    |     |      |        |
| get_tech_type_template             | Display the templates defined for a technology type          | ✓   |    |     |      |        |
| hey_egeria                         | Textual User Interface for the pyegeria commands             |     |    |     |      |        |
| hey_egeria_cat                     | Textual User Interface for catalog use                       |     |    |     |      |        |
| hey_egeria_my                      | Textual User Interface for personal use                      |     |    |     |      |        |
| hey_egeria_ops                     | Textual User Interface for operations use                    |     |    |     |      |        |
| hey_egeria_tech                    | Textual User Interface for technical use                     |     |    |     |      |        |
| list_archives                      | Display the available archives known to Egeria               | ✓   |    |     |      |        |
| list_asset_types                   | List the types of assets known to Egeria                     |     |    |     | ✓    |        |
| list_assets                        | Find and display assets in a domain                          | ✓   |    |     |      |        |
| list_catalog_targets               | List the catalog target details for a connection             |     |    | ✓   |      | ✓      |
| list_cert_types                    | List certification types                                     | ✓   |    |     |      |        |
| list_collections                   | List collections                                             | ✓   |    |     |      |        |
| list_deployed_catalogs             | List deployed catalogs                                       | ✓   |    |     |      | ✓      |
| list_deployed_databases            | List deployed databases                                      | ✓   |    |     |      | ✓      |
| list_deployed_schemas              | List deployed schemas                                        | ✓   |    |     |      | ✓      |
| list_deployed_servers              | List deployed servers                                        | ✓   |    |     |      |        |
| list_elements                      | Display table of Elements of an Open Metadata type           |     |    |     | ✓    |        |
| list_elements_for_classification   | List the elements of a classification                        |     |    |     | ✓    |        |
| list_engine_activity               | List engine activity                                         |     |    | ✓   |      |        |
| list_engine_activity_compressed    | Compressed view of engine activity                           |     |    | ✓   |      | ✓      |
| list_glossaries                    | List glossaries                                              | ✓   |    |     |      | ✓      |
| list_gov_action_processes          | List governance action processes                             |     |    |     | ✓    |        |
| list_gov_eng_status                | List the status of the governance engines                    |     |    | ✓   |      | ✓      |
| list_integ_daemon_status           | List status of an integration daemon server                  |     |    | ✓   |      | ✓      |
| list_my_profile                    | List the details of the current user profile                 |     | ✓  |     |      |        |
| list_my_roles                      | List the roles of the current user                           |     | ✓  |     |      |        |
| list_projects                      | List projects filtered by search string                      | ✓   |    |     |      |        |
| list_registered_services           | List all registered Egeria services                          |     |    |     | ✓    |        |
| list_related_elements              | List elements related to a specific element                  |     |    |     | ✓    |        |
| list_related_specification         | List details of related elements                             |     |    |     | ✓    |        |
| list_relationship_types            | List types of relationships and their attributes             |     |    |     | ✓    |        |
| list_relationships                 | List relationships for elements of a given type              | ✓   |    |     |      |        |
| list_tech_templates                | List templates for technology types                          |     |    |     | ✓    |        |
| list_tech_types                    | List technology types                                        | ✓   |    |     |      |        |
| list_terms                         | List glossary terms                                          | ✓   |    |     |      | ✓      |
| list_todos                         | List to-do actions                                           | ✓   |    |     |      |        |
| list_user_ids                      | Display table of known user ids                              | ✓   |    |     |      |        |
| list_valid_metadata_values         | List valid metadata (reference) values                       |     |    |     | ✓    |        |
| load_archive                       | Load an archive/content-pack into Egeria                     |     |    | ✓   |      |        |
| load_archive_tui                   | Load an archive/content-pack into Egeria                     |     |    | ✓   |      |        |
| load_terms_from_file               | Import glossary terms from a CSV file                        | ✓   |    |     |      |        |
| mark_todo_complete                 | Mark a to-do item as complete                                |     | ✓  |     |      |        |
| monitor_asset_events               | Monitor asset events                                         |     |    | ✓   |      |        |
| monitor_coco_status                | Monitor status of Coco Sample servers                        |     |    | ✓   |      |        |
| monitor_engine_activity            | Monitor engine activity                                      |     |    | ✓   |      |        |
| monitor_engine_activity_compressed | Monitor engine activity                                      |     |    | ✓   |      |        |
| monitor_gov_eng_status             | Monitor status of an engine-host OMAG server                 |     |    | ✓   |      |        |
| monitor_integ_daemon_status        | Monitor status of an integration daemon OMAG server          |     |    | ✓   |      |        |
| monitor_my_todos                   | Monitor to-do items assigned to me                           |     | ✓  |     |      |        |
| monitor_open_todos                 | Monitor open to-do items                                     |     | ✓  |     |      |        |
| monitor_platform_status            | Monitor the status of all platforms                          |     |    | ✓   |      |        |
| monitor_server_list                | List status of all servers using the RuntimeManager          |     |    | ✓   |      |        |
| monitor_server_startup             | Monitor the status of all servers using access services      |     |    | ✓   |      |        |
| monitor_server_status              | Monitor the status of all servers using the RuntimeManager   |     |    | ✓   |      |        |
| reassign_todo                      | Reassign a todo item to a new actor                          |     | ✓  |     |      |        |
| refresh_gov_eng_config             | Refresh the governance engines on an engine host             |     |    | ✓   |      |        |
| refresh_integration_daemon         | Refresh one or all integration connectors                    |     |    | ✓   |      |        |
| restart_integration_daemon         | Restart and integration daemon                               |     |    | ✓   |      |        |
| start_daemon                       | Start or restart an OMAG server from its known configuration |     |    | ✓   |      |        |
| stop_daemon                        | Stop an OMAG server daemon                                   |     |    | ✓   |      |        |


# Visual Command Reference
A visual command reference of all the `hey_egeria` **show** commands can be found [Visual Command Reference](https://github.com/odpi/egeria-python/tree/main/pyegeria/commands/doc/Visual%20Command%20Reference)
----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.