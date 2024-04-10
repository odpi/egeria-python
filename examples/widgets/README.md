The example applications in this directory provide some simple but useful visualization of the Egeria environment. They 
are built with the **Rich** python package and demonstrate the use of **pyegeria** .

The applications are invoked using the python3 command - for instance:
`python3 server_status_widget -h` would display the help information for the server_status_widget.
Running them may require that you have pyegeria installed. pyegeria can be installed using:
'pip install pyegeria'

The functions are:

* server_status_widget: provide a live view of servers running on a platform.
* gov_engine_status:    provides a live view of the specified governance engine host.
* engine_action_status: provides a live view of the engine actions - both running and completed.
* glossary_view: a paged list of terms as specified by the search string
* find_todos: find and display outstanding todos
* gov_engine_status: provide a live status view of a governance engine
* integration_daemon_status: provide a live status view of an integration daemon
* my_todos: provide a live view of my todos
* view_my_profile: view an Egeria profile
* list_asset_types: list the types of assets that have been configured in Egeria
* multi-server_status: show the status from two platforms concurrently
* 
