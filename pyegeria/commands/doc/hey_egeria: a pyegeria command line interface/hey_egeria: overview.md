<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

# Introduction
# Hey_Egeria

Hey_Egeria is a friendly, easy to use command line interface (CLI) to make using Egeria easier and more transparent. 
It is implemented as a set of pyegeria commands that allows users to manage and inspect Egeria artifacts through a simple terminal interface.
There are currently about 70 commands available, but the functions continue to grow and evolve with the needs of the Egeria community.

Getting started is easy. The CLI runs in a standard terminal window operating in Mac, PC and Linux environments. 
You will need to know some basic information about your Egeria environment, but if you are operating within a typical 
Egeria development environment or Egeria Workspaces the pre-configured environment variables and defaults should just work without additional setup. 

In this guide, we'll first review how to install hey_egeria, then go through how to use it from both the 
TUI (Textual User Interface) as well as the command line. After walking through a number of basic examples, 
we'll discuss how the CLI is organized, how to configure it and some advanced features. Let's get started!

# Installation & Upgrade

`hey_egeria` is written in python and is part of the the **__pyegeria package__** that can be found on [pypi](https://pypi.org). 
To install and run the CLI  we use the **pipx** utility [Installation - pipx](https://pipx.pypa.io/latest/installation/). 
This utility creates operating system level commands from suitably configured python packages. 
It installs the package in a private environment so that the python packages are isolated from the rest of your environment. 
So the first step is to install pipx from a terminal window by following the directions in the link above.


Once **pipx** is installed, install **pyegeria** using pipx, this will create and configure all of the pyegeria commands. 
Install pyegeria commands by entering into the terminal window:

`pipx install pyegeria`

This will result in a an output similar to:



```➜  / pipx install pyegeria
  installed package pyegeria 1.5.1.1.49, installed using Python 3.12.7
  These apps are now globally available
    - change_todo_status
    - create_glossary
    - create_term
    - create_todo
    - delete_glossary
    - delete_todo
    - export_terms_to_file
    - get_asset_graph
    - get_collection
    - get_element_info
    - get_guid_info
    - get_project_dependencies
    - get_project_structure
    - get_tech_details
    - get_tech_type_elements
    - get_tech_type_template
    - hey_egeria
    - hey_egeria_cat
    - hey_egeria_my
    - hey_egeria_ops
    - hey_egeria_per
    - hey_egeria_tech
    - list_archives
    - list_asset_types
    - list_assets
    - list_catalog_targets
    - list_cert_types
    - list_deployed_catalogs
    - list_deployed_databases
    - list_deployed_schemas
    - list_deployed_servers
    - list_element_graph
    - list_elements
    - list_elements_for_classification
    - list_engine_activity
    - list_engine_activity_compressed
    - list_glossaries
    - list_glossary
    - list_gov_action_processes
    - list_gov_eng_status
    - list_integ_daemon_status
    - list_my_profile
    - list_my_roles
    - list_projects
    - list_registered_services
    - list_related_elements
    - list_related_specification
    - list_relationship_types
    - list_relationships
    - list_tech_templates
    - list_tech_types
    - list_terms
    - list_todos
    - list_user_ids
    - list_valid_metadata_values
    - load_archive
    - load_archive_tui
    - load_terms_from_file
    - mark_todo_complete
    - monitor_asset_events
    - monitor_coco_status
    - monitor_engine_activity
    - monitor_engine_activity_compressed
    - monitor_gov_eng_status
    - monitor_integ_daemon_status
    - monitor_my_todos
    - monitor_open_todos
    - monitor_platform_status
    - monitor_server_list
    - monitor_server_startup
    - monitor_server_status
    - reassign_todo
    - refresh_gov_eng_config
    - refresh_integration_daemon
    - restart_integration_daemon
    - start_daemon
    - stop_daemon
done! ✨ 🌟 ✨
```

There are a couple of interesting things to note in the output. The first is the version of pyegeria which can be helpful in determining if and when to upgrade. The second is the long list of pyegeria commands that are installed. Executing these commands directly can be a useful shortcut - especially within shell scripts - but for getting started and everyday use many people find that using the **hey_egeria** CLI is simpler. Hence, this document will focus more on using the CLI. 

Uninstalling and upgrading pyegeria can also easily be done with pipx commands. Issuing:

`pipx -h`

Will provide a good overview.

## First Use

A good first use is to validate that we are able to communicate with an Egeria platform and check the status of the running servers. We can do this by typing:

`hey_egeria ops show servers`

Which should produce an output similar to:

The structure of the command is:

`hey_egeria` [area] [show/tell] [object] [required parameters] [--optional parameters]

* hey_egeria` - this is the shell level command
* [area] - there are currently four areas of commands that roughly correspond to user roles. They are:
	* cat - for catalog users - this is for general usage of Egeria as a governance catalog.
	* my - for individual information - these commands are relevant to an individual such as my_todos.
	* ops - for Egeria operations - these commands are for working with the Egeria environment itself.
	* tech - for technical users - these commands provide technical details and management.
* [show/tell] - **show** commands display something and **tell** commands instruct Egeria to do something. 
For example, above we requested to be shown the status of Egeria servers on a platform. We could use a tell command to, create or delete a glossary term.
* [required parameters] - parameters are sometimes required by a command. 
* [optional parameters] - most parameters are optional and have sensible defaults so that you don't have to type them in.

There is a lot of detail here that can seem a bit daunting to learn - so to make things easier, we have a TUI 
(Textual User Interface) that allows us to browse through the commands with documentation and guidance about how to fill out each command - and then to execute the command. Here is what it looks like:

![tui-hey-egeria 2024-11-10 at 18.31.01@2x.png](images/tui-hey-egeria%202024-11-10%20at%2018.31.01%402x.png)
Lets review the numbered annotations in the screenshot above:

1) The left hand side is a scrollable list of commands organized by area, show/tell and then 
## Working with the TUI



----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.