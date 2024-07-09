<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

The example applications in this directory provide some simple but useful visualization of the Egeria environment. They 
are built with the **Rich** python package and demonstrate the use of **pyegeria** .

The applications are invoked using the python3 command - for instance:
`python3 server_status_widget -h` would display the help information for the server_status_widget.
Running them requires that you have pyegeria installed. pyegeria can be installed using:
'pip install pyegeria'

Once pyegeria is installed, the scripts may also be run as commands from any directory without having to specify python3 in front such as:
`view_platform_status.py

Some of the widgets are "live" - that is running continuously until ctrl-c is issued to interrupt it.

As the number of widgets has grown, they have been organized by role into different sub-directories:

* catalog_user - for users of the Egeria environment
* developer - for those building with, or working on Egeria
* operational - for visualizing the current state of Egeria - typically for administrators
* personal_organizer - for visualizing work and individual items

The naming convention for the widgets helps to understand their behaviour:
Here is a list - if the widget starts with:

* get - it will return details about a single item
* list - lists elements through a paging interface like "more" - use q to quit.
* view - provides a live view - typically of a status - use control-c to quit


----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.