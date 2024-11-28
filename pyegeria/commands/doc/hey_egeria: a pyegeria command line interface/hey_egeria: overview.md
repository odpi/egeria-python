<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

# Introduction to Hey_Egeria

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

`hey_egeria ops show servers status`

Which should produce an output similar to:
![out-server-status  2024-11-10 at 18.15.42@2x.png](images/out-server-status%20%202024-11-10%20at%2018.15.42%402x.png)
**N.B. if you are trying this out in your terminal, you may need to type either `ctrl-c` or `q` to quit the display.

We can also execute a variation of this command to display an extended version of this status.

`hey_egeria ops show servers status --full` 
which will return much more descriptive information about the servers and their status:

![out-server-status-full 2024-11-10 at 18.25.14@2x.png](images/out-server-status-full%202024-11-10%20at%2018.25.14%402x.png)

The general structure of the command is:

`hey_egeria` [area] [show/tell] [object] [command] [required parameters] [--optional parameters]

* `hey_egeria` - this is the shell level command
* [area] - there are currently four areas of commands that roughly correspond to user roles. They are:
	* cat - for catalog users - this is for general usage of Egeria as a governance catalog.
	* my - for individual information - these commands are relevant to an individual such as my_todos.
	* ops - for Egeria operations - these commands are for working with the Egeria environment itself.
	* tech - for technical users - these commands provide technical details and management.
* [show/tell] - **show** commands display something and **tell** commands instruct Egeria to do something. 
For example, above we requested to be shown the status of Egeria servers on a platform. We could use a tell command to, create or delete a glossary term.
* [required parameters] - parameters are sometimes required by a command. 
* [optional parameters] - most parameters are optional and have sensible defaults so that you don't have to type them in.

A more visual representation of **hey_egeria** is shown in the following two diagrams. The first shows the structure 
and the second shows the structure and all the commands. **PLEASE NOTE** - **hey_egeria** continues to evolve; view all 
images as representing a point-in-time representation. The principles will hold true but details may vary.

![Xmind 1731421782704.png](images/Xmind%201731421782704.png)

![Xmind 1731422134920.png](images/Xmind%201731422134920.png)

There is a lot of detail here that can seem a bit daunting to learn - so to make things easier, we have a TUI 
(Textual User Interface) that allows us to browse through the commands with documentation and guidance about how to fill out each command - and then to execute the command. Here is what it looks like:

![tui-hey-egeria.png](images/tui-hey-egeria.png)

Lets review the numbered annotations in the screenshot above:

1) The left hand side is a scrollable list of commands organized as discussed above. Clicking on a command
will cause details to be displayed on the right hand pane.
2) At the top of the right hand pane is a brief command description.
3) Below this description is a search bar that allows you to search for parameters to fill out and review. You will notice
that the list of parameters is scrollable - often more than will fit in the space allocated - so search can be handy.
4) The bottom command bar shows the equivalent shell command that is being built through your parameter selections in the TUI.
If you are going to use this command often, you could copy this command and create a shell alias for it - or just execute 
it in the terminal window.
5) Pressing this button or typing `ctrl-R` will execute the command that you are building and return you to the terminal window
to view the results.

## Working with the TUI

We can return to the example above, this time using the TUI to help us fill out the parameters. Here is what the TUI 
looks like to execute the same command:

![tui-show-server-status 2024-11-10 at 18.52.01@2x.png](images/tui-show-server-status%202024-11-10%20at%2018.52.01%402x.png)
To show the full version of the server status we would select the check-box for --full as shown here:

![tui-show-server-status-full 2024-11-10.png](images/tui-show-server-status-full%202024-11-10.png)
As you can see, the TUI provides visibility into the available command options as well as descriptive text explaining
what they are.

In addition to getting a quick overview of all of the servers, we often
want to see more details about a specific kind of server. For instance,  to view a status of an Egeria integration server
we would use `hey_egeria ops show integrations status` which we could either type at the terminal or enter via the TUI.
The output of this command looks like:

![out-integ-status-live 2024-11-12 at 16.44.12@2x.png](images/out-integ-status-live%202024-11-12%20at%2016.44.12%402x.png)

There are a few different styles of output. Some of the tables are **live monitors**. That is, the commands run until interrupted by either a failure or the user typing `ctrl-c`. They reflect the status of 
the object they are monitoring. Quite useful for operational monitoring - but the number of rows displayed is limited by
your current screen size. There are different techniques we use to work around this limitation but the simplest is to
enable a **list** (also sometimes called **paging**) version of the command that allows you to page through all the results using a syntax similar to
the Unix style **more** or **less** commands. To enable this version of the command we can look for
the `list` flag in the parameter list of the TUI like this:

![tui-integration-status-paging.png](images/tui-integration-status-paging.png)

The list view looks a bit different, but contains the same information. 

![out-integ-status-list 2024-11-12 at 16.45.26.png](images/out-integ-status-list%202024-11-12%20at%2016.45.26.png)

Pressing the `space-bar` will advance the page. You can exit the display by pressing `q`. There are other options
that generally follow the syntax of the `more` command.

## Taking action

So far we have demonstrated how to display information with hey_egeria - but we can also tell it to perform a variety of actions.
These actions could be very simple (start a server) or more complex, requiring multiple fields of information such as 
create a glossary term. If the user specified in the command has permissions then the action will be performed.

As an example, lets look at the command to load a content pack (or archive) into a repository. The 
TUI page looks like this:
![tui-load-archive 2024-11-10 at 19.19.09@2x.png](images/tui-load-archive%202024-11-10%20at%2019.19.09%402x.png)

Creating a glossary term looks like:
![tui-create-term 2024-11-06 at 20.46.35.png](../glossary/images/tui-create-term%202024-11-06%20at%2020.46.35.png)

Building and managing glossaries is explained in more detail in a separate tutorial.

## Working in a specific role

The number and variety of commands continues to expand. To make it a bit easier to find the right function
we also have subsets of **hey_egeria** available for the major roles/perspectives. There are:

* hey_egeria_cat - for catalog users
* hey_egeria_my - for personal tasks
* hey_egeria_ops - for operations
* hey_egeria_tech - for technical use

The structure and use of these is quite similar to **hey_egeria** - however, these commands can be a bit
simpler if you focus on one of the above areas.

## When to upgrade - and how

**pyegeria** is in active development. New methods are added in conjunction with new capabilities in Egeria, methods
are updated to reflect Egeria's evolution and commands are added or updated to support the community. To support this 
active lifecycle, are *moving* to a naming convention where the version of pyegeria is aligned with the version of 
Egeria. Thus version 5.2 of Egeria will be aligned with version 5.2.x.x.x of pyegeria. The 3rd digit of the version will
be a 0 for SNAPSHOT (in-progress) releases of Egeria and non-zero for production releases.

# Adapting to your environment

Commands in the hey_egeria TUI have parameters to adapt to your environment. These parameters set 
the endpoints, server names and user information for the commands to use. There is a default set of values that 
matches the default environment for Egeria Workspaces [overview](https://egeria-project.org/try-egeria/overview/) as well 
as many of our samples, labs and demos. These defaults can be easily changed; both in a shell environment, by changing
the values of the corresponding environment variables or in the TUI by over-riding defaults using the optional parameters.
Here is a list of the variables and their defaults:

| Environment Variable          | Default                | Command Option           | Description                                                |
|-------------------------------|------------------------|--------------------------|------------------------------------------------------------|
| EGERIA_JUPYTER                | True                   | --jupyter                | Set to True for better display in Jupyter notebooks        |
| EGERIA_USER                   | erinoverview           | --userid                 | A typical Egeria user                                      |
| EGERIA_USER_PASSWORD          | secret                 | --password               | User password                                              |
| EGERIA_ADMIN_USE              | garygeeke              | --admin_user             | A user that configures and operates Egeria platform        |
| EGERIA_ADMIN_PASSWORD         | secret                 | --admin_user_password    | Admin password                                             |
| EGERIA_ENGINE_HOST            | engine-host            | --engine_host            | Egeria Engine host to use for governance actions/processes |
| EGERIA_ENGINE_HOST_URL        | https://localhost:9443 | --engine_host_url        | Platform URL where Engine host is running                  |
| EGERIA_INTEGRATION_DAEMON     | integration-daemon     | --integration-daemon     | Egeria integration daemon to use                           |
| EGERIA_INTEGRATION_DAEMON_URL | https://localhost:9443 | --integration_daemon_url | Platform URL where Integration daemon is running           |
| EGERIA_VIEW_SERVER            | view-server            | --view_server            | Egeria view server to use                                  |
| EGERIA_VIEW_SERVER_URL        | https://localhost:9443 | --view_server_url        | Platform URL where view server is running                  |
| EGERIA_PLATFORM_URL           | https://localhost:9443 | --url                    | Platform URL where chosen Egeria metadata store is running |
| EGERIA_METADATA_STORE         | active-metadata-store  | --server                 | Egeria metadata store to use                               |
| EGERIA_WIDTH                  | 200                    | --width                  | Width of the terminal screen to use for displaying results |
| EGERIA_TIMEOUT                | 60                     | --timeout                | Timeout for Egeria actions                                 |

Egeria workspaces changes some of these defaults for the Docker environment it sets up. A kubernetes deployment may similarly alter the defaults
to accommodate deployment. Note that this is a very simplistic use of user identity and password. This can be augmented by using the 
[Secrets Connector](https://egeria-project.org/concepts/secrets-store-connector). 

# Advanced Use
This section briefly discusses some more advanced topics on the use and extension of the pyegeria commands and CLI.
## Using the CLI from the command line
As we have shown, CLI commands can be used directly in a terminal window without using the TUI.
For frequently used commands this can be a bit quicker.

We start with a terminal window and type `hey_egeria` and we see that we get a lot of help information, the commands that
are available at this point and optional parameters that we can pass: 
![hey_egeria  2024-11-12 at 20.38.43.png](images/hey_egeria%20%202024-11-12%20at%2020.38.43.png)
We can add one of the commands to the end of the clause and see that the next set of commands to choose from. In the 
following screenshot below we show incrementally building up the final command clause by clause. Till we finally have the
`hey_egeria cat show glossary glossaries`. 
![hey_egeria cat 2024-11-12 at 21.41.43.png](images/hey_egeria%20cat%202024-11-12%20at%2021.41.43.png)

Of course, if we remember the command we can just type it in and execute it.

## Direct commands
Sometimes, especially when writing automation scripts, we may want to use a more terse set of commands.
Pyegeria has short-hand commands that are the rough equivalent of the CLI commands. For example,
the short-hand for:

`hey_egeria ops show servers status`

is

`monitor_server_status`

Each of these commands has a help option that lists the available parameters. For example:

![short-cut commands 2024-11-12 at 22.22.13.png](images/short-cut%20commands%202024-11-12%20at%2022.22.13.png)

The full list of available short-cut commands can be found by typing `pipx list`. It is also shown above in the 
installation section.

## How this is implemented

The pyegeria commands are built in python using the [**click**](https://click.palletsprojects.com/en/stable/) package 
for the CLI along with the [**Trogon**](https://github.com/Textualize/trogon) from Textualize to create the 
CLI TUI. Most of the display commands make use of the [**Rich**](https://rich.readthedocs.io/en/stable/introduction.html) 
library for visualization in a terminal environment. 

## Making changes
All of the code for the CLI and for the pyegeria library itself (along with this documentation) can be found
on Github in the **egeria-python** repo at [pyegeria](https://github.com/odpi/egeria-python). This code is 
Open Source with an Apache 2 license. You are free to use, copy and extend this code. However, if you are
interested, we would very much value your participation in the Egeria Community. We look forward to hearing from you!

# Feedback

The pyegeria CLI and Command set offer an evolving set of capabilities. We use these features daily - but perhaps
there are aspects that you either love or wish were different? We'd love to hear from you and learn from your use cases!
Feel free to raise an issue in Github - or better yet, join our slack channel and participate in the community.





----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.