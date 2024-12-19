<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->
# **hey_egeria:** A Visual Reference Summary

This summary has embeds links and commentary for the Egeria CLI (**hey_egeria**).
It is organized in the same manner as the CLI itself to simplify learning how to navigate the CLI.

The commands and the structure of **hey_egeria** continue to evolve and expand based on the needs of the community.
For this reason, each screenshot is time-stamped. A visual time-line of each command will be kept in the directories below
but this document will continue to refer to only the current version.

You will note that in most screenshots, the command used to generate the screenshot is displayed (usually in purple) with
a purple arrow pointing to it.

As always, we welcome your feedback and contributions to this work.

 ---

<!-- TOC -->
* [**hey_egeria:** A Visual Reference Summary](#hey_egeria-a-visual-reference-summary)
  * [1. Top level](#1-top-level)
  * [2. cat: Commands for the catalog user](#2-cat-commands-for-the-catalog-user)
    * [2.1 assets: display information about assets](#21-assets-display-information-about-assets)
      * [2.1.1 asset-graph - displays information about the asset and the elements related to it](#211-asset-graph---displays-information-about-the-asset-and-the-elements-related-to-it)
      * [2.1.2 assets-in-domain - search for occurrences of search-string in the asset domain](#212-assets-in-domain---search-for-occurrences-of-search-string-in-the-asset-domain)
      * [2.1.3 elements-of-type - display elements for a specified technology type](#213-elements-of-type---display-elements-for-a-specified-technology-type)
      * [2.1.4 tech-type-elements - list the elements of the specified technology type](#214-tech-type-elements---list-the-elements-of-the-specified-technology-type)
    * [2.2 deployed-data: display information about deployed data resources Egeria has been told about](#22-deployed-data-display-information-about-deployed-data-resources-egeria-has-been-told-about)
      * [2.2.1 deployed-data-catalogs - lists the known deployed catalogs](#221-deployed-data-catalogs---lists-the-known-deployed-catalogs)
      * [2.2.2 deployed-schemas: lists information about schemas, optionally filtered by catalog name](#222-deployed-schemas-lists-information-about-schemas-optionally-filtered-by-catalog-name)
      * [2.2.3 deployed-servers: lists the deployed software servers](#223-deployed-servers-lists-the-deployed-software-servers)
      * [2.2.4 deployed-databases: lists the known, deployed databases](#224-deployed-databases-lists-the-known-deployed-databases)
    * [2.3 glossary: display information about glossaries and glossary terms](#23-glossary-display-information-about-glossaries-and-glossary-terms)
      * [2.3.1 list-glossaries: lists the known glossaries](#231-list-glossaries-lists-the-known-glossaries)
      * [2.3.2 list-glossary-terms: lists glossary terms, optionally filtered by glossary](#232-list-glossary-terms-lists-glossary-terms-optionally-filtered-by-glossary)
    * [2,4 info: a mix of other information and Egeria structures](#24-info-a-mix-of-other-information-and-egeria-structures)
      * [2.4.1 asset-types: list the types of assets Egeria knows about](#241-asset-types-list-the-types-of-assets-egeria-knows-about)
      * [2.4.2 certification-types: list the types of certifications that have been defined](#242-certification-types-list-the-types-of-certifications-that-have-been-defined)
      * [2.4.3 collection-graph: display a graph of collection from a specified root collection](#243-collection-graph-display-a-graph-of-collection-from-a-specified-root-collection)
      * [2.4.4 collections: lists collections filtered by the optional search string](#244-collections-lists-collections-filtered-by-the-optional-search-string)
      * [2.4.5 to-dos: list to-do items optionally filtered by a search string](#245-to-dos-list-to-do-items-optionally-filtered-by-a-search-string)
      * [2.4.6 user-ids: list all known user ids](#246-user-ids-list-all-known-user-ids)
      * [2.4.7 tech-types: list technology types optionally filtered by a search-string](#247-tech-types-list-technology-types-optionally-filtered-by-a-search-string)
    * [2.5 projects: information about projects that Egeria represents](#25-projects-information-about-projects-that-egeria-represents)
      * [2.5.1 project-dependencies: display a dependency graph of projects starting from the specified project](#251-project-dependencies-display-a-dependency-graph-of-projects-starting-from-the-specified-project)
      * [2.5.2 project-structure: display the structure of the project specified, including sub-projects and relationships](#252-project-structure-display-the-structure-of-the-project-specified-including-sub-projects-and-relationships)
      * [2.5.3 projects: display a list of projects optionally filtered by a search string](#253-projects-display-a-list-of-projects-optionally-filtered-by-a-search-string)
  * [3.0 my: a personal view](#30-my-a-personal-view)
      * [3.0.1 my-profile: displays the profile of the user identity the command runs under](#301-my-profile-displays-the-profile-of-the-user-identity-the-command-runs-under)
      * [3.0.2 my-roles: displays the roles of the user identity the command runs under](#302-my-roles-displays-the-roles-of-the-user-identity-the-command-runs-under)
      * [3.03 my-to-dos: displays to-do items that have been assigned to the current user identity](#303-my-to-dos-displays-to-do-items-that-have-been-assigned-to-the-current-user-identity)
      * [3.04 open-to-dos: displays a list of all open to-do items](#304-open-to-dos-displays-a-list-of-all-open-to-do-items)
  * [4.0 ops - information about Egeria operations and configurations](#40-ops---information-about-egeria-operations-and-configurations)
    * [4.1 engines](#41-engines)
      * [4.1.1 activity: display the current engine activity as a static, paged list in a compressed view](#411-activity-display-the-current-engine-activity-as-a-static-paged-list-in-a-compressed-view)
      * [4.1.2 activity: display the current engine activity as a live monitor in a compressed view](#412-activity-display-the-current-engine-activity-as-a-live-monitor-in-a-compressed-view)
      * [4.1.3 activity: display the current engine activity as a live monitor](#413-activity-display-the-current-engine-activity-as-a-live-monitor-)
      * [4.1.4 status: display the current status of governance engines either as a live monitor or as a static, paged list](#414-status-display-the-current-status-of-governance-engines-either-as-a-live-monitor-or-as-a-static-paged-list)
    * [4.2 integrations](#42-integrations)
      * [4.2.1 status: display the integration daemon status either as a live monitor or as a static, paged list](#421-status-display-the-integration-daemon-status-either-as-a-live-monitor-or-as-a-static-paged-list)
      * [4.2.2 targets: display a list of catalog targets and their details](#422-targets-display-a-list-of-catalog-targets-and-their-details)
    * [4.3 platforms](#43-platforms)
      * [4.3.1 status: display the platform status as a live monitor](#431-status-display-the-platform-status-as-a-live-monitor)
    * [4.4 servers](#44-servers)
      * [4.4.1 status: show the status of servers running on the default platform with full details](#441-status-show-the-status-of-servers-running-on-the-default-platform-with-full-details)
      * [4.4.2 status: show the status of servers running on the default platform with only status](#442-status-show-the-status-of-servers-running-on-the-default-platform-with-only-status)
      * [4.4.3 startup: display a summary server status view using direct platform information.](#443-startup-display-a-summary-server-status-view-using-direct-platform-information)
  * [5.0 tech: information for technologists](#50-tech-information-for-technologists)
    * [5.1 elements: different ways to explore and display metadata elements managed by Egeria](#51-elements-different-ways-to-explore-and-display-metadata-elements-managed-by-egeria)
      * [5.1.1 anchored_elements: List anchored elements that match a specified value for a property.](#511-anchored_elements-list-anchored-elements-that-match-a-specified-value-for-a-property)
      * [5.1.2 elements: List of elements of the specified Egeria Open Metadata type](#512-elements-list-of-elements-of-the-specified-egeria-open-metadata-type)
      * [5.1.3 elements - extended: List of elements of the specified Egeria Open Metadata type with the extended columns](#513-elements---extended-list-of-elements-of-the-specified-egeria-open-metadata-type-with-the-extended-columns)
      * [5.1.4 elements of om_type by classification](#514-elements-of-om_type-by-classification)
      * [5.1.5 get_elements: a list of elements of the specified om_type](#515-get_elements-a-list-of-elements-of-the-specified-om_type)
      * [5.1.6 guid-info: information about the element identified by the supplied GUID](#516-guid-info-information-about-the-element-identified-by-the-supplied-guid)
      * [5.1.7 related-elements: lists elements related to specified element](#517-related-elements-lists-elements-related-to-specified-element)
      * [5.1.8 related-specifications: display template specification parameters](#518-related-specifications-display-template-specification-parameters)
    * [5.2 tech-info](#52-tech-info)
      * [5.2.1 asset-types: List defined asset types](#521-asset-types-list-defined-asset-types)
      * [5.2.2 gov-action-processes: displays details about identified governance action processes](#522-gov-action-processes-displays-details-about-identified-governance-action-processes)
      * [5.2.3 processes: lists all governance action processes](#523-processes-lists-all-governance-action-processes)
      * [5.2.4 registered-services: lists the services registered with the Egeria OMAG Platform](#524-registered-services-lists-the-services-registered-with-the-egeria-omag-platform)
      * [5.2.5 relationship-types: lists the relationship types from the specified Egeria Open Metadata type](#525-relationship-types-lists-the-relationship-types-from-the-specified-egeria-open-metadata-type)
      * [5.2.6 relationships <placeholder>](#526-relationships-placeholder)
      * [5.2.7 valid-metadata-values: display valid metadata value for the specified property of a type](#527-valid-metadata-values-display-valid-metadata-value-for-the-specified-property-of-a-type)
    * [5.3 tech-types](#53-tech-types)
      * [5.3.1 details - Display details for the specified technology type.](#531-details---display-details-for-the-specified-technology-type)
      * [5.3.2 list - list the deployed technology types specified by the search string](#532-list---list-the-deployed-technology-types-specified-by-the-search-string)
      * [5.3.3 template-spec - list the template specification details for the specified technology type](#533-template-spec---list-the-template-specification-details-for-the-specified-technology-type)
      * [5.3.4 templates - display details of technology type templates for the specified technology type](#534-templates---display-details-of-technology-type-templates-for-the-specified-technology-type)
<!-- TOC -->

 ---

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

Note:
Set the EGERIA_USER and EGERIA_USER_PASSWORD environment variables for your desired default user.

![my_profile  2024-12-14 at 16.29.27@2x.png](my/show/my_profile%20%202024-12-14%20at%2016.29.27%402x.png)

#### 3.0.2 my-roles: displays the roles of the user identity the command runs under
Input:
 userid (required) - default is "erinoverview", one of the fictitious Coco Pharmaceuticals employees.

Note:
Set the EGERIA_USER and EGERIA_USER_PASSWORD environment variables for your desired default user.

![my_roles 2024-12-14 at 16.32.10@2x.png](my/show/my_roles%202024-12-14%20at%2016.32.10%402x.png)

#### 3.03 my-to-dos: displays to-do items that have been assigned to the current user identity

Input:
 userid (required) - default is "erinoverview", one of the fictitious Coco Pharmaceuticals employees.

Note:
Set the EGERIA_USER and EGERIA_USER_PASSWORD environment variables for your desired default user.

![my_todos  2024-12-15 at 16.24.13@2x.png](my/show/my_todos%20%202024-12-15%20at%2016.24.13%402x.png)

#### 3.04 open-to-dos: displays a list of all open to-do items

![open_todos 2024-12-14 at 16.36.12@2x.png](my/show/open_todos%202024-12-14%20at%2016.36.12%402x.png)




## 4.0 ops - information about Egeria operations and configurations

### 4.1 engines

#### 4.1.1 activity: display the current engine activity as a static, paged list in a compressed view
Input:
* rowlimit - limits the number of rows to display, default is 0, which means return all rows.
* list (checkbox) - if checked, a paging version of the display is provided, if unchecked this will be a live, continuously updated version; default is not checked.
* compressed (checkbox) - if checked, a compressed version of the display is provided, default is not checked.

Note:
To exit a live monitor you type "ctrl-c"; to exit a paged list you type "q"

![list_engine_activity compressed 2024-12-15 at 16.48.48@2x.png](ops/show/engines/list_engine_activity%20compressed%202024-12-15%20at%2016.48.48%402x.png)

#### 4.1.2 activity: display the current engine activity as a live monitor in a compressed view
Input:
* rowlimit - limits the number of rows to display, default is 0, which means return all rows.
* list (checkbox) - if checked, a paging version of the display is provided, if unchecked this will be a live, continuously updated version; default is not checked.
* compressed (checkbox) - if checked, a compressed version of the display is provided, default is not checked.

Note:
To exit a live monitor you type "ctrl-c"; to exit a paged list you type "q"



![monitor_engine_activity compressed  2024-12-15 at 16.38.29@2x.png](ops/show/engines/monitor_engine_activity%20compressed%20%202024-12-15%20at%2016.38.29%402x.png)
#### 4.1.3 activity: display the current engine activity as a live monitor 
Input:
* rowlimit - limits the number of rows to display, default is 0, which means return all rows.
* list (checkbox) - if checked, a paging version of the display is provided, if unchecked this will be a live, continuously updated version; default is not checked.
* compressed (checkbox) - if checked, a compressed version of the display is provided, default is not checked.

Note:
To exit a live monitor you type "ctrl-c"; to exit a paged list you type "q"
![monitor_engine_activity  2024-12-15 at 16.32.55@2x.png](ops/show/engines/monitor_engine_activity%20%202024-12-15%20at%2016.32.55%402x.png)

#### 4.1.4 status: display the current status of governance engines either as a live monitor or as a static, paged list
Input:
* engine-list - list of engines to include in the display, default is "*" (all)
* list (checkbox) - if checked, a paging version of the display is provided, if unchecked this will be a live, continuously updated version; default is not checked.


Note:
To exit a live monitor you type "ctrl-c"; to exit a paged list you type "q"
![monitor_engine_status 2024-12-15 at 16.51.26.jpeg](ops/show/engines/monitor_engine_status%202024-12-15%20at%2016.51.26.jpeg)



### 4.2 integrations

#### 4.2.1 status: display the integration daemon status either as a live monitor or as a static, paged list
Input:
* connector-list - list of connectors to include in the display, default is "*" (all)
* list (checkbox) - if checked, a paging version of the display is provided, if unchecked this will be a live, continuously updated version; default is not checked.
* sorted (checkbox) - if checked, the list of connectors will be sorted; default is checked.

![monitor_integration_daemon_status  2024-12-15 at 16.57.12@2x.png](ops/show/integrations/monitor_integration_daemon_status%20%202024-12-15%20at%2016.57.12%402x.png)


#### 4.2.2 targets: display a list of catalog targets and their details
Input:
* connector (required) - a valid connector name must be provided - typically selected using the previous 'integration daemon status' command.


![monitor_integration_targets  2024-12-15 at 17.02.19@2x.png](ops/show/integrations/monitor_integration_targets%20%202024-12-15%20at%2017.02.19%402x.png)

### 4.3 platforms
#### 4.3.1 status: display the platform status as a live monitor

![monitor_platform_status  2024-12-15 at 19.53.18@2x.png](ops/show/platforms/monitor_platform_status%20%202024-12-15%20at%2019.53.18%402x.png)



### 4.4 servers

#### 4.4.1 status: show the status of servers running on the default platform with full details
Input:
* full (checkbox) - if check shows a full description of the servers, otherwise just the status is displayed; default is unchecked.
* url - the url of the Egeria OMAG Server Platform to get the server status for; default is derived from the EGERIA_PLATFORM_URL environment variable.

![monitor_server_status full 2024-12-15 at 20.01.57@2x.png](ops/show/servers/monitor_server_status%20full%202024-12-15%20at%2020.01.57%402x.png)

#### 4.4.2 status: show the status of servers running on the default platform with only status
Input:
* full (checkbox) - if check shows a full description of the servers, otherwise just the status is displayed; default is unchecked.
* url - the url of the Egeria OMAG Server Platform to get the server status for; default is derived from the EGERIA_PLATFORM_URL environment variable.

![monitor_server_status  2024-12-15 at 19.59.39@2x.png](ops/show/servers/monitor_server_status%20%202024-12-15%20at%2019.59.39%402x.png)

#### 4.4.3 startup: display a summary server status view using direct platform information.
Input:
* url - the url of the Egeria OMAG Server Platform to get the server status for; default is derived from the EGERIA_PLATFORM_URL environment variable.


![monitor_startup_servers 2024-12-15 at 19.56.07@2x.png](ops/show/servers/monitor_startup_servers%202024-12-15%20at%2019.56.07%402x.png)




## 5.0 tech: information for technologists

### 5.1 elements: different ways to explore and display metadata elements managed by Egeria

#### 5.1.1 anchored_elements: List anchored elements that match a specified value for a property.
Input:
* search-string (required) - value to search for, default is "DeployedDatabaseSchema"
* prop-list (required) - properties to search for the the above search-string. This is a list of strings separated by comma. Default is "anchorTypeName".

![get_anchored_elements 2024-12-15 at 21.25.41@2x.png](tech/show/elements/get_anchored_elements%202024-12-15%20at%2021.25.41%402x.png)


#### 5.1.2 elements: List of elements of the specified Egeria Open Metadata type
Input:
* extended (checkbox) - if checked additional feedback columns are displayed; default is unchecked.
* om_type (required) - the Egeria Open Metadata type to return elements for; default is "Organization"

![list_elements_by_om-type  2024-12-16 at 14.24.18@2x.png](tech/show/elements/list_elements_by_om-type%20%202024-12-16%20at%2014.24.18%402x.png)

#### 5.1.3 elements - extended: List of elements of the specified Egeria Open Metadata type with the extended columns
Input:
* extended (checkbox) - if checked additional feedback columns are displayed; default is unchecked.
* om_type (required) - the Egeria Open Metadata type to return elements for; default is "Organization"

![list_elements_by_om-type extended  2024-12-16 at 14.28.46@2x.png](tech/show/elements/list_elements_by_om-type%20extended%20%202024-12-16%20at%2014.28.46%402x.png)

#### 5.1.4 elements of om_type by classification
Input:
* om_type (required) - Egeria Open Metadata type to search for; default is "Project".
* classification - Egeria classification to search within; default is "GovernanceProject".

![list_elements_of_om_type_by_classification  2024-12-16 at 14.35.26@2x.png](tech/show/elements/list_elements_of_om_type_by_classification%20%202024-12-16%20at%2014.35.26%402x.png)

#### 5.1.5 get_elements: a list of elements of the specified om_type
Input: 
* om_type (required) - Egeria Open Metadata type to search for; default is "Project".
![get_elements_of_om_type  2024-12-16 at 14.39.59@2x.png](tech/show/elements/get_elements_of_om_type%20%202024-12-16%20at%2014.39.59%402x.png)


#### 5.1.6 guid-info: information about the element identified by the supplied GUID
Input:
* guid (required) - the unique identifier of the element to return information about.

![info_for_guid  2024-12-16 at 11.35.29@2x.png](tech/show/elements/info_for_guid%20%202024-12-16%20at%2011.35.29%402x.png)

#### 5.1.7 related-elements: lists elements related to specified element
Input:
* guid (required) - the unique identifier of the element to return information about.
* om_type (required) - Egeria Open Metadata type to search for; default is "Project".
* rel_type (requited) - Egeria relationship type to filter by; default is "Certification".
![related_elements 2024-12-16 at 14.55.01@2x.png](tech/show/elements/related_elements%202024-12-16%20at%2014.55.01%402x.png)


#### 5.1.8 related-specifications: display template specification parameters
Input:
* guid (required) - the unique identifier of the element to return information about.

![show_related_specifications 2024-12-16 at 15.04.55@2x.png](tech/show/elements/show_related_specifications%202024-12-16%20at%2015.04.55%402x.png)

### 5.2 tech-info
#### 5.2.1 asset-types: List defined asset types

![asset_types 2024-12-16 at 15.10.16@2x.png](tech/show/tech-info/asset_types%202024-12-16%20at%2015.10.16%402x.png)

#### 5.2.2 gov-action-processes: displays details about identified governance action processes
Input:
* search-string (required) - value to search for, default is "*" (all)

![detailed_governance_action_processes  2024-12-16 at 15.16.26@2x.png](tech/show/tech-info/detailed_governance_action_processes%20%202024-12-16%20at%2015.16.26%402x.png)

#### 5.2.3 processes: lists all governance action processes
![governance_action_processes 2024-12-16 at 15.13.01@2x.png](tech/show/tech-info/governance_action_processes%202024-12-16%20at%2015.13.01%402x.png)

#### 5.2.4 registered-services: lists the services registered with the Egeria OMAG Platform
Input:
* services: one of all, access-services, common-services, engine-services, governance-services, integration-services, view-services; default is "all".
![registered_services 2024-12-16 at 16.44.54@2x.png](tech/show/tech-info/registered_services%202024-12-16%20at%2016.44.54%402x.png)

#### 5.2.5 relationship-types: lists the relationship types from the specified Egeria Open Metadata type
Input:

* om_type (required) - Egeria Open Metadata type to search for; default is "AssetOwner".

![relationship_types 2024-12-19 at 10.51.54@2x.png](tech/show/tech-info/relationship_types%202024-12-19%20at%2010.51.54%402x.png)

#### 5.2.6 relationships <placeholder>
Input:

* relationships (reqired) - relationship to search for; default is "Certification".


#### 5.2.7 valid-metadata-values: display valid metadata value for the specified property of a type
Input:

* property (required) - valid value property to return the value for; default is "projectHealth".
* type-name (required) - metadata type to search the valid values for; default is "Project"

![valid_metadata_values 2024-12-16 at 15.31.56@2x.png](tech/show/tech-info/valid_metadata_values%202024-12-16%20at%2015.31.56%402x.png)



### 5.3 tech-types

#### 5.3.1 details - Display details for the specified technology type.
Input:

* tech_name (required) - technology name to get details for.

![tech_type_details 2024-12-16 at 15.37.21@2x.png](tech/show/tech-types/tech_type_details%202024-12-16%20at%2015.37.21%402x.png)


#### 5.3.2 list - list the deployed technology types specified by the search string
Input:
* search-string - search for technology types containing the search-string; default is "*" (all).

[list_technology_types 2024-12-16 at 15.39.20@2x.png](tech/show/tech-types/list_technology_types%202024-12-16%20at%2015.39.20%402x.png)

#### 5.3.3 template-spec - list the template specification details for the specified technology type

Input:
* search-string - search for templates associated with technology types containing the search-string; default is "*" (all).

![list_tech_type_template_specs  2024-12-16 at 16.03.22@2x.png](tech/show/tech-types/list_tech_type_template_specs%20%202024-12-16%20at%2016.03.22%402x.png)

#### 5.3.4 templates - display details of technology type templates for the specified technology type
Input:
* tech-type - name of the technology type to display templates for; default is "PostgreSQL Server"

![tech_type_templates 2024-12-16 at 16.11.48@2x.png](tech/show/tech-types/tech_type_templates%202024-12-16%20at%2016.11.48%402x.png)



----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the Egeria project.