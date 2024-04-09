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
