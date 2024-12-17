<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->
<!-- TOC -->
* [**hey_egeria:** A Visual Reference Summary](#hey_egeria-a-visual-reference-summary)
  * [Top level](#top-level)
  * [cat: Commands for the catalog user](#cat-commands-for-the-catalog-user)
    * [assets: display information about assets](#assets-display-information-about-assets)
    * [deployed-data: display information about deployed data resources Egeria has been told about](#deployed-data-display-information-about-deployed-data-resources-egeria-has-been-told-about)
    * [glossary: display information about glossaries and glossary terms](#glossary-display-information-about-glossaries-and-glossary-terms)
    * [info: a mix of other information and Egeria structures](#info-a-mix-of-other-information-and-egeria-structures)
    * [projects: information about projects that Egeria represents](#projects-information-about-projects-that-egeria-represents)
  * [my - a personal view](#my---a-personal-view)
  * [ops - information about Egeria operations and configurations](#ops---information-about-egeria-operations-and-configurations)
    * [engines](#engines)
    * [integrations](#integrations)
    * [platforms](#platforms)
    * [servers](#servers)
  * [tech - more technical information of use to technologists](#tech---more-technical-information-of-use-to-technologists)
    * [elements - different ways to explore and display metadata elements managed by Egeria](#elements---different-ways-to-explore-and-display-metadata-elements-managed-by-egeria)
    * [tech-info](#tech-info)
    * [tech-types](#tech-types)
<!-- TOC -->

# **hey_egeria:** A Visual Reference Summary

This summary has embeds links and commentary for the Egeria CLI (**hey_egeria**).
It is organized in the same manner as the CLI itself to simplify learning how to navigate the CLI.

The commands and the structure of **hey_egeria** continue to evolve and expand based on the needs of the community.
For this reason, each screenshot is time-stamped. A visual time-line of each command will be kept in the directories below
but this document will continue to refer to only the current version.

You will note that in most screenshots, the command used to generate the screenshot is displayed (usually in purple) with
a purple arrow pointing to it.

As always, we welcome your feedback and contributions to this work.

## 1. Top level
This image is a composite of screenshots showing the full list and organization of **hey_egeria** commands.

![hey_egeria tui 2024-12-16 at 16.58.22@2x.png](hey_egeria%20tui%202024-12-16%20at%2016.58.22%402x.png)


## 2. cat: Commands for the catalog user

### 2.1 assets: display information about assets
#### 2.1.1 asset-graph - displays information about the asset and the elements related to it
Input:
* asset-guid (required): the unique identity (GUID) of the asset to start from.
![asset-graph 2024-11-20 at 15.56.42.png](cat/show/assets/Asset-graph%202024-11-20%20at%2015.56.42.png)

#### 2.1.2 assets-in-domain - search for occurrences of search-string in the asset domain
Input:
* search_string (required): the string to search for; matches will be displayed.

![assets-in-domain 2024-11-20 at 15.49.55@2x.png](cat/show/assets/Assets-in-domain%202024-11-20%20at%2015.49.55%402x.png)

#### 2.1.3 elements-of-type - display elements for a specified technology type
Input:
* tech_type (required) - technology type to search elements for; default is 'PostgreSQL Server'.

Note: Technology type artifacts are generally loaded from open-metadata archives. You may need to load the right
archive file, if it hasn't already been loaded,  before finding a specific technology type.

![elements-of-type 2024-11-20 at 16.01.35.png](cat/show/assets/elements-of-type%202024-11-20%20at%2016.01.35.png)

#### 2.1.4 tech-type-elements - list the elements of the specified technology type
Input: 
* tech_type (required) - technology type to search elements for; default is 'PostgreSQL Server'

![tech-type-elements 2024-11-20 at 16.05.05.png](cat/show/assets/tech-type-elements%202024-11-20%20at%2016.05.05.png)

### 2.2 deployed-data: display information about deployed data resources Egeria has been told about

#### 2.2.1 deployed-data-catalogs - lists the known deployed catalogs
Input:
* search_server - optionally filter results by this server name, default is '*' (all)
Notes: This shows the properties for each server found as well as the catalog schemas it contains.

![deployed-data-catalogs 2024-12-17 at 15.43.27@2x.png](cat/show/deployed-data/deployed-data-catalogs%202024-12-17%20at%2015.43.27%402x.png)

#### 2.2.2 deployed-schemas: lists information about schemas, optionally filtered by catalog name
Input:
* search_catalog - optionally filter results by this catalog name, default is '*' (all)
Notes: This shows the schemas for catalogs as well as data resources within the schema.

![deployed-schemas 2024-12-17 at 15.48.38@2x.png](cat/show/deployed-data/deployed-schemas%202024-12-17%20at%2015.48.38%402x.png) 

#### 2.2.3 deployed-servers: lists the deployed software servers
Input: 
* search_string - optionally filters by the search string, default is '*' (all).

![deployed-servers 2024-12-17 at 15.52.16@2x.png](cat/show/deployed-data/deployed-servers%202024-12-17%20at%2015.52.16%402x.png)

#### 2.2.4 deployed-databases: lists the known, deployed databases
Input:
* server - optionally filter the databases by the name of the database servers.  

![deployed_databases 2024-12-16 at 16.40.31@2x.png](cat/show/deployed-data/deployed_databases%202024-12-16%20at%2016.40.31%402x.png)


### 2.3 glossary: display information about glossaries and glossary terms

#### 2.3.1 list-glossaries: lists the known glossaries
Input:
* search_string - optionally filters by the search string, default is '*' (all).

* ![list-glossaries 2024-11-25 at 20.30.02.png](cat/show/glossary/list-glossaries%202024-11-25%20at%2020.30.02.png)

#### 2.3.2 list-glossary-terms: lists glossary terms, optionally filtered by glossary
Input:
* search-string - optionally filters terms by the search string, default is '*' (all).
* glossary-guid - optionally restricts the search to just the glossary specified by the GUID, default is EGERIA_HOME_GLOSSARY_GUID.
* glossary-name - optionally restricts the search to just the glossary specified by the name, default is '*' (all).

Note:
If both glossary-guid and glossary-name have values, glossary-guid will take precedence.

![list-terms 2024-11-25 at 20.32.11.png](cat/show/glossary/list-terms%202024-11-25%20at%2020.32.11.png)

### 2,4 info: a mix of other information and Egeria structures

As we get more commands in particular topic areas, we will sub-divide this further.

#### 2.4.1 asset-types: list the types of assets Egeria knows about

![asset-types 2024-11-25 at 20.34.19@2x.png](cat/show/info/asset-types%202024-11-25%20at%2020.34.19%402x.png)

#### 2.4.2 certification-types: list the types of certifications that have been defined
Input:
* search-string - optionally filters certifications by the search string, default is '*' (all).

![certification-types 2024-11-25 at 20.37.07.png](cat/show/info/certification-types%202024-11-25%20at%2020.37.07.png)

#### 2.4.3 collection-graph: display a graph of collection from a specified root collection
Input:
* root_collection (required) - collection to use as the root of the graph; nested collections will be displayed, default root collection is 'Coco Pharmaceuticals Governance Domains'.
![collection-graph 2024-12-12 at 11.33.18@2x.png](cat/show/info/collection-graph%202024-12-12%20at%2011.33.18%402x.png)

#### 2.4.4 collections: lists collections filtered by the optional search string
Input:
* collection - optionally filter collections by the string specified, default is "*" (all).

![list-collections 2024-12-10 at 14.25.51@2x.png](cat/show/info/list-collections%202024-12-10%20at%2014.25.51%402x.png)

#### 2.4.5 to-dos: list to-do items optionally filtered by a search string
Input:
* search-string - optionally filters todo items by the search string, default is '*' (all).

![list-todos 2024-12-12 at 11.46.30@2x.png](cat/show/info/list-todos%202024-12-12%20at%2011.46.30%402x.png)

#### 2.4.6 user-ids: list all known user ids

![list-user-ids 2024-12-12 at 11.51.09@2x.png](cat/show/info/list-user-ids%202024-12-12%20at%2011.51.09%402x.png)

#### 2.4.7 tech-types: list technology types optionally filtered by a search-string
Input:
* tech_type: optionally filters list by the search string, default is '*' (all).
![tech-types 2024-12-12 at 11.37.20@2x.png](cat/show/info/tech-types%202024-12-12%20at%2011.37.20%402x.png)


### 2.5 projects: information about projects that Egeria represents

#### 2.5.1 project-dependencies: display a dependency graph of projects starting from the specified project
Input:
* project (required) - base project to show dependencies from, default is "Clinical Trials Management"

![project_dependencies 2024-12-14 at 16.24.39@2x.png](cat/show/projects/project_dependencies%202024-12-14%20at%2016.24.39%402x.png)

#### 2.5.2 project-structure: display the structure of the project specified, including sub-projects and relationships
Input:
* project (required) - base project to show dependencies from, default is "Clinical Trials Management"

![project_structure 2024-12-14 at 16.21.35@2x.png](cat/show/projects/project_structure%202024-12-14%20at%2016.21.35%402x.png)

#### 2.5.3 projects: display a list of projects optionally filtered by a search string
Input:
* search-string - optionally filters projects by the search string, default is '*' (all).

![projects 2024-12-14 at 16.18.10@2x.png](cat/show/projects/projects%202024-12-14%20at%2016.18.10%402x.png)



## 3.0 my: a personal view
#### 3.0.1 my-profile: displays the profile of the user identity the command runs under
Input:
* userid (required) - default is "erinoverview", one of the fictitious Coco Pharmaceuticals employees.

![my_profile  2024-12-14 at 16.29.27@2x.png](my/show/my_profile%20%202024-12-14%20at%2016.29.27%402x.png)


![my_roles 2024-12-14 at 16.32.10@2x.png](my/show/my_roles%202024-12-14%20at%2016.32.10%402x.png)


![my_todos  2024-12-15 at 16.24.13@2x.png](my/show/my_todos%20%202024-12-15%20at%2016.24.13%402x.png)


![open_todos 2024-12-14 at 16.36.12@2x.png](my/show/open_todos%202024-12-14%20at%2016.36.12%402x.png)




## ops - information about Egeria operations and configurations

### engines

![list_engine_activity compressed 2024-12-15 at 16.48.48@2x.png](ops/show/engines/list_engine_activity%20compressed%202024-12-15%20at%2016.48.48%402x.png)

![monitor_engine_activity compressed  2024-12-15 at 16.38.29@2x.png](ops/show/engines/monitor_engine_activity%20compressed%20%202024-12-15%20at%2016.38.29%402x.png)

![monitor_engine_activity  2024-12-15 at 16.32.55@2x.png](ops/show/engines/monitor_engine_activity%20%202024-12-15%20at%2016.32.55%402x.png)

![monitor_engine_status 2024-12-15 at 16.51.26.jpeg](ops/show/engines/monitor_engine_status%202024-12-15%20at%2016.51.26.jpeg)



### integrations

![monitor_integration_daemon_status  2024-12-15 at 16.57.12@2x.png](ops/show/integrations/monitor_integration_daemon_status%20%202024-12-15%20at%2016.57.12%402x.png)

![monitor_integration_targets  2024-12-15 at 17.02.19@2x.png](ops/show/integrations/monitor_integration_targets%20%202024-12-15%20at%2017.02.19%402x.png)

### platforms

![monitor_platform_status  2024-12-15 at 19.53.18@2x.png](ops/show/platforms/monitor_platform_status%20%202024-12-15%20at%2019.53.18%402x.png)



### servers

![monitor_server_status full 2024-12-15 at 20.01.57@2x.png](ops/show/servers/monitor_server_status%20full%202024-12-15%20at%2020.01.57%402x.png)

![monitor_server_status  2024-12-15 at 19.59.39@2x.png](ops/show/servers/monitor_server_status%20%202024-12-15%20at%2019.59.39%402x.png)

![monitor_startup_servers 2024-12-15 at 19.56.07@2x.png](ops/show/servers/monitor_startup_servers%202024-12-15%20at%2019.56.07%402x.png)




## tech - more technical information of use to technologists

### elements - different ways to explore and display metadata elements managed by Egeria

![get_anchored_elements 2024-12-15 at 21.25.41@2x.png](tech/show/elements/get_anchored_elements%202024-12-15%20at%2021.25.41%402x.png)

![get_elements_of_om_type  2024-12-16 at 14.39.59@2x.png](tech/show/elements/get_elements_of_om_type%20%202024-12-16%20at%2014.39.59%402x.png)

![info_for_guid  2024-12-16 at 11.35.29@2x.png](tech/show/elements/info_for_guid%20%202024-12-16%20at%2011.35.29%402x.png)

![list_elements_by_om-type extended  2024-12-16 at 14.28.46@2x.png](tech/show/elements/list_elements_by_om-type%20extended%20%202024-12-16%20at%2014.28.46%402x.png)

![list_elements_by_om-type  2024-12-16 at 14.24.18@2x.png](tech/show/elements/list_elements_by_om-type%20%202024-12-16%20at%2014.24.18%402x.png)

![list_elements_of_om_type_by_classification  2024-12-16 at 14.35.26@2x.png](tech/show/elements/list_elements_of_om_type_by_classification%20%202024-12-16%20at%2014.35.26%402x.png)

![related_elements 2024-12-16 at 14.55.01@2x.png](tech/show/elements/related_elements%202024-12-16%20at%2014.55.01%402x.png)

![show_related_specifications 2024-12-16 at 15.04.55@2x.png](tech/show/elements/show_related_specifications%202024-12-16%20at%2015.04.55%402x.png)

### tech-info

![asset_types 2024-12-16 at 15.10.16@2x.png](tech/show/tech-info/asset_types%202024-12-16%20at%2015.10.16%402x.png)

![detailed_governance_action_processes  2024-12-16 at 15.16.26@2x.png](tech/show/tech-info/detailed_governance_action_processes%20%202024-12-16%20at%2015.16.26%402x.png)

![governance_action_processes 2024-12-16 at 15.13.01@2x.png](tech/show/tech-info/governance_action_processes%202024-12-16%20at%2015.13.01%402x.png)

![list_relationship_types 2024-12-16 at 16.20.34@2x.png](tech/show/tech-info/list_relationship_types%202024-12-16%20at%2016.20.34%402x.png)

![registered_services 2024-12-16 at 16.44.54@2x.png](tech/show/tech-info/registered_services%202024-12-16%20at%2016.44.54%402x.png)

![valid_metadata_values 2024-12-16 at 15.31.56@2x.png](tech/show/tech-info/valid_metadata_values%202024-12-16%20at%2015.31.56%402x.png)



### tech-types

![list_tech_type_template_specs  2024-12-16 at 16.03.22@2x.png](tech/show/tech-types/list_tech_type_template_specs%20%202024-12-16%20at%2016.03.22%402x.png)

![list_technology_types 2024-12-16 at 15.39.20@2x.png](tech/show/tech-types/list_technology_types%202024-12-16%20at%2015.39.20%402x.png)

![tech_type_details 2024-12-16 at 15.37.21@2x.png](tech/show/tech-types/tech_type_details%202024-12-16%20at%2015.37.21%402x.png)

![tech_type_templates 2024-12-16 at 16.11.48@2x.png](tech/show/tech-types/tech_type_templates%202024-12-16%20at%2016.11.48%402x.png)



----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.