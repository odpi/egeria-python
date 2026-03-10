---
apply: always
---

Pyegeria is an Open Source python library supporting Egeria. There are 3 sub-projects.

1. Pyegeria - base python client library to Egeria's REST APIs that adds a bit of business semantics and also include flexible reporting through the report_specs.
2. Hey_Egeria - Command line scripts to interact with Egeria accessible either standalone, and through a Click CLI.
3. Dr.Egeria - A markdown processor that allows Egeria commands to be written in markdown documents and then interpreted and executed by Dr.Egeria.

Raw sample HTTP requests can be seen in pyegeria/http clients - this is useful to see example payloads and URLs

There are common patterns we try to follow across the different element types. location_arena.py is one good example but there are many others.
Most of the common patterns use common helper functions in _server_client.py. 

Do not make changes to _server_client.py, or other core files without permission.

Do not make changes without permission to files other than the specific ones being requested.

Put documents intended for the developer (as opposed to use) and test code meant for your understanding (as opposed to 
standard pyegeria tests) in the folder egeria-python/.ai/.ai-sandbox

Review your plan of execution with me before proceeding. Get confirmation before significant changes.
Discuss bugs you've found and improvements you'd like to make before doing so - unless I give you the go-ahead for this request.
