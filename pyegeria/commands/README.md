<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

The Commands in this directory provide a simple but useful command line interface for the Egeria environment. They 
are built with the **Rich** python package and demonstrate the use of **pyegeria** .

The commands can either be invoked from one of the command line interfaces or executed directly as python scripts.
To invoke the commands directly, install them with pipx by invoking:

`pipx install pyegeria`

Some of the widgets are "live" - that is running continuously until ctrl-c is issued to interrupt it. Other widgets are
**paged** to allow you to page through long lists of content. Paged interfaces have a similar behaviour to the unix
`more` command - so, for example you type `q` to quit.

As the number of widgets has grown, they have been organized by role into different sub-directories:

* cat (catalog_user) - for users of the Egeria environment
* cli - command line interfaces to simplify finding and using the commands
* my - for visualizing work and individual items
* ops - for configuring and operating Egeria
* tech - for technical users to configure and use Egeria

The command line interfaces (CLIs) can be invoked with:

hey_egeria - provides access to all commands
hey_egeria_cat - access for commands used by catalog users
hey_egeria_my - access to personal information commands for all users
hey_egeria_ops - access to operations commands
hey_egeria_tech - access to commands for technical users

Each of these CLIs have a textual user interface (TUI) that provides a forms based approach
to utilizing each command. You invoke the TUI by adding `tui` to the cli command. For instance:

`hey_egeria_cat tui`

To execute a command from the TUI type ctrl-R.


To upgrade the CLI commands you can type:

`pipx upgrade pyegeria`

----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.