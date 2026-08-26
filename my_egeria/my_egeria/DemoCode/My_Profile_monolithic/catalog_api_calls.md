# Catalog (Shop for Data) — pyegeria API Call Reference

This document maps each UI function in the **Catalogs / Shop for Data** flow of `my_profile_app.py`
to the underlying pyegeria API calls it makes.

---

## Left Navigation Pane — Catalog Chooser (`ShopForDataScreen`)

Populated when the user selects **"Catalogs/Shop for Data"** from the main menu option list.
All five tables are loaded before the screen is pushed.

| Table | pyegeria Call | Report Spec / Method | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|---|
| Glossaries | `exec_report_spec()` | `format_set_name="Glossaries"` | `search_string="*"` | | |
| Digital Product Catalog | `exec_report_spec()` | `format_set_name="Digital-Product-Catalog"` | `search_string="*"`, `metadata_element_subtypes=["DigitalProduct","DigitalProductFamily"]` | | |
| Data Dictionaries | `exec_report_spec()` | `format_set_name="Data-Dictionaries"` | `search_string="*"` | | |
| Business Domains | `exec_report_spec()` | `format_set_name="BusinessCapabilities"` | `search_string="*"` | | |
| Root Collections | `exec_report_spec()` | `format_set_name="BasicCollections"` | `search_string="RootCollection"` | | |

All five calls use `output_format="DICT"` and share the same `view_server`, `view_url`, `user`, and `user_pass` from app config.

---

## Right-Hand Pane — Detail View (`SelectionOverviewScreen`)

Populated via the `shop_for_data_callback()` after the user selects a row in the left nav.
The `selection_type` string returned by `ShopForDataScreen` determines which builder runs.

### Glossary selected → `build_glossary_details()`

| Action | pyegeria Call | Notes | Suggested Call | Comments |
|---|---|---|---|---|
| Build folder/term tree | _(none — reuses pre-fetched data)_ | Parses `self.glossary_data_extract` loaded during left-nav population; no additional API call | | |

### Digital Product Catalog selected → `build_catalog_details()`

| Action | pyegeria Call | Report Spec / Method | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|---|
| Load catalog items | `exec_report_spec()` | `format_set_name="Digital-Product-Catalog"` | `search_string=<qname>`, `filter_string=<qname>` | | |
| Retrieve sample data for DigitalProduct members | `DataEngineer.find_tabular_data_sets()` | _(direct method)_ | `search_string=<membership_qname>`, `start_from=0`, `page_size=10`, `output_format="MD"` | | |

### Data Dictionary selected → `build_dictionary_details()`

| Action | pyegeria Call | Report Spec / Method | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|---|
| Load dictionary terms | `exec_report_spec()` | `format_set_name="Data-Dictionaries"` | `search_string=<qname>`, `filter_string=<qname>` | | |

### Business Domain selected → `build_domain_details()`

| Action | pyegeria Call | Report Spec / Method | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|---|
| Load domain structure | `exec_report_spec()` | `format_set_name="BusinessCapabilities"` | `search_string=<qname>`, `filter_string=<qname>` | | |

### Root Collection selected → `build_root_collection_details()`

| Action | pyegeria Call | Notes | Suggested Call | Comments |
|---|---|---|---|---|
| Build member tree | _(none — reuses pre-fetched data)_ | Parses `self.collections` loaded during left-nav population; no additional API call | | |

---

## Subscribe Action (`overview_callback` → r_code 211)

Triggered when the user clicks **Subscribe** in `SelectionOverviewScreen`.

| Action | pyegeria Call | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|
| Create digital subscription | `ProductManager.create_digital_subscription()` | `selected_item` (qualified name of selected element) | | |

---

## Supporting Flows (Main Screen / App Startup)

These run on app mount, before the catalog screen is reached.

| Function | pyegeria Call | Report Spec / Method | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|---|
| Load user profile | `MyProfile._async_get_my_profile()` | `report_spec="My-User-MD"` | `output_format="DICT"` | | |
| Load user identities | `MyProfile.get_my_profile()` | `report_spec="User-Identities"` | `output_format="DICT"` | | |
| Load team members (on role row select) | `exec_report_spec()` | `format_set_name="Team-Members"` | `search_string=<role_search_key>` | | |

---

## Technology Types Flow (separate from catalog)

| Function | pyegeria Call | Key Parameters | Suggested Call | Comments |
|---|---|---|---|---|
| Populate tech-type tree (left nav) | `AutomatedCuration._async_get_tech_type_hierarchy()` | `filter_string="*"` | | |
| Load tech-type detail (right pane) | `AutomatedCuration.get_tech_type_detail()` | `filter_string=<selected_t_node>`, `output_format="JSON"` | | |
| Create element from template | `AutomatedCuration.initiate_gov_action_process()` | `body=<request_body>` (includes `templateGUID`, `placeholderPropertyValues`) | | |

---

## Client Classes Used

| Client Class | Used For |
|---|---|
| `MyProfile` | User profile and identity retrieval |
| `AutomatedCuration` | Technology type hierarchy, detail, and template/process instantiation |
| `DataEngineer` | Tabular data set retrieval for catalog sample data |
| `ProductManager` | Creating digital subscriptions |
| `exec_report_spec()` | All report-spec-driven lookups (glossaries, catalogs, dictionaries, domains, collections, team members) |
