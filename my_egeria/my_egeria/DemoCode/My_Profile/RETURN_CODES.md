# My Profile Application Return Codes Reference

This document provides a comprehensive catalog of all return codes and screen dismiss codes used across the `my_profile_app.py` application and its supporting handlers and screens in `my_egeria/my_egeria/DemoCode/My_Profile/`.

In accordance with application conventions:
- **200 Series**: Successful operations, normal navigation, user selections, and action triggers.
- **400 Series**: Failure, error, cancellation, or exception return codes.

---

## 200 Series: Success, Navigation, and Action Codes

| Return Code | Name / Type | Description | Source Components |
|---|---|---|---|
| **`200`** | `SUCCESS_OK` / `DEFAULT_EXIT` | Standard success code. Used for successful operations, standard modal dismissal, backing out of dialogs, cancelling inputs without error, or quitting cleanly. | `my_profile_app.py`, `MainScreen.py`, `StatusScreen.py`, `CreateProfileScreen.py`, `EditElementsScreens.py`, `AddToElementsScreens.py`, `TechnologyTypeScreens.py`, `tech_types_handler.py`, `shop_for_data_handler.py`, `team_roles_handler.py`, `SelectionOverviewScreen.py`, `GenericDataViewScreen.py`, `MyBookMarksScreen.py`, `MyTeamScreen.py`, `SearchForTermScreen.py`, `ShowCommentScreen.py` |
| **`201`** | `ALT_NAVIGATION` / `NO_MATCH` | Alternative navigation or fallback action code. In search/team screens, indicates no matching terms/roles found and triggers transition to data shopping or alternate view. In tech type selection, represents secondary navigation action. | `SearchForTermScreen.py`, `team_roles_handler.py`, `TechnologyTypeScreens.py`, `MyTeamScreen.py`, `ShopForDataScreen.py` |
| **`210`** | `QUIT_TO_MAIN` | Exit/Quit action code from data shopping / data viewing screens to dismiss the view and return directly to the main menu screen. | `ShopForDataScreen.py`, `GenericDataViewScreen.py`, `SelectionOverviewScreen.py`, `shop_for_data_handler.py` |
| **`211`** | `SUBSCRIBE_ACTION` | Action code indicating the user has requested to create a digital subscription for the selected data source, catalog product, or data element. | `ShopForDataScreen.py`, `GenericDataViewScreen.py`, `SelectionOverviewScreen.py`, `shop_for_data_handler.py` |
| **`212`** | `SAMPLE_DATA_ACTION` | Action code indicating the user has requested to view sample data for the selected data source in Shop for Data. | `ShopForDataScreen.py`, `shop_for_data_handler.py` |

---

## 400 Series: Failure, Exception, and Error Codes

| Return Code | Name / Type | Description | Source Components |
|---|---|---|---|
| **`400`** | `GENERIC_ERROR` / `BAD_RESULT` | General error code or user cancellation with bad result. Used in StatusScreen when copying GUID fails or user indicates bad status, and in edit elements when invalid operations occur. | `StatusScreen.py`, `EditElementsScreens.py`, `ShowCommentsScreen.py` |
| **`401`** | `PROFILE_ACTION_FAILED` | Profile creation or profile element editing cancelled, rejected, or failed. | `CreateProfileScreen.py`, `EditElementsScreens.py` |
| **`404`** | `TECH_TYPE_NO_PROCESS_FALLBACK_FAIL` | Failed to mount empty processes option list when fallback handler encountered an unexpected error. | `TechnologyTypeScreens.py` |
| **`405`** | `TECH_TYPE_NO_PROCESS_CREATE_FAIL` | Failed to create empty processes option list during initial widget mount. | `TechnologyTypeScreens.py` |
| **`406`** | `TECH_TYPE_PROCESS_CREATE_FAIL` | Error creating technology type governance action processes option list widget. | `TechnologyTypeScreens.py` |
| **`407`** | `TECH_TYPE_PROCESS_FALLBACK_FAIL` | Error creating technology type governance action processes option list widget during NoMatches fallback recovery. | `TechnologyTypeScreens.py` |
| **`408`** | `TECH_TYPE_NO_TEMPLATE_FALLBACK_FAIL` | Failed to mount empty templates option list when fallback handler encountered an unexpected error. | `TechnologyTypeScreens.py` |
| **`409`** | `TECH_TYPE_NO_TEMPLATE_CREATE_FAIL` | Failed to create empty templates option list during initial widget mount. | `TechnologyTypeScreens.py` |
| **`410`** | `TECH_TYPE_TEMPLATE_FALLBACK_FAIL` / `COLLECTION_CATEGORY_ERROR` | Error mounting template option list during NoMatches fallback recovery in technology type screens; or unknown collection category returned in selection overview processing. | `TechnologyTypeScreens.py`, `shop_for_data_handler.py` |
| **`411`** | `TECH_TYPE_TEMPLATE_CREATE_FAIL` / `GLOSSARY_TREE_MISSING` | Error creating template option list widget in technology type screens; or query_one found no matches for glossary tree in overview processing. | `TechnologyTypeScreens.py`, `shop_for_data_handler.py` |
| **`412`** | `CATALOG_TREE_MISSING` | Query_one found no matches for digital product catalog tree in selection overview processing. | `shop_for_data_handler.py` |
| **`413`** | `DATA_DICTIONARY_TREE_MISSING` | Query_one found no matches for data dictionary tree in selection overview processing. | `shop_for_data_handler.py` |
| **`414`** | `BUSINESS_DOMAIN_TREE_MISSING` | Query_one found no matches for business domain tree in selection overview processing. | `shop_for_data_handler.py` |
| **`415`** | `ROOT_COLLECTION_TREE_MISSING` / `TECH_TYPE_OPTION_INVALID_RC` | Query_one found no matches for root collections tree in selection overview processing; or technology type options screen returned non-200 error code. | `shop_for_data_handler.py`, `tech_types_handler.py` |
| **`416`** | `TECH_TYPE_FETCH_FAIL` | Failed to retrieve technology type hierarchy or details from Egeria Automated Curation service, or invalid option type passed. | `TechnologyTypeScreens.py`, `tech_types_handler.py` |
| **`417`** | `TECH_TYPE_UNPACK_DATA_ERROR` | Unexpected or unparseable data structure received from Egeria when unpacking technology type data. | `tech_types_handler.py` |
| **`418`** | `TECH_TYPE_TEMPLATE_CALLBACK_INVALID` / `SHOP_DATA_PAYLOAD_INVALID` | Invalid payload or missing required arguments received in technology type templates/processes callback; or invalid data payload returned from Shop for Data screen. | `tech_types_handler.py`, `shop_for_data_handler.py` |
| **`419`** | `TECH_TYPE_PLACEHOLDER_NOT_DICT` | Technology type placeholder input data is not a dictionary structure as expected. | `tech_types_handler.py` |
| **`420`** | `TECH_TYPE_CREATE_ELEMENT_FAIL` / `SHOP_DATA_RETRIEVAL_ERROR` | Exception raised during creation of metadata element from template via Automated Curation; or error retrieving details for glossary, catalog, or dictionary data elements. | `tech_types_handler.py`, `shop_for_data_handler.py` |
| **`421`** | `APP_INITIALIZATION_FAIL` / `DOMAIN_DATA_RETRIEVAL_ERROR` | Failure to initialize main profile app / retrieve current user profile details; or error retrieving business domain details in Shop for Data. | `my_profile_app.py`, `shop_for_data_handler.py` |
| **`422`** | `DATA_SPECIFICATION_RETRIEVAL_ERROR` | Error retrieving data specification details from Egeria in Shop for Data handler. | `shop_for_data_handler.py` |
| **`423`** | `BUSINESS_DOMAIN_SPEC_ERROR` | Error executing BusinessCapabilities report specification in Shop for Data handler. | `shop_for_data_handler.py` |
| **`429`** | `SAMPLE_DATA_RETRIEVAL_ERROR` | Failed to retrieve or parse sample data from Egeria Asset Catalog / Data Engine in Shop for Data handler. | `shop_for_data_handler.py` |
| **`440`** | `TEAM_ROLES_OR_GLOSSARY_ERROR` | Error communicating with Egeria or retrieving team members, user roles, or glossary term details. | `team_roles_handler.py` |

---

## Return Code Ranges Summary

- **200–219**: Normal flow, successful callbacks, dismiss codes, and user navigation/interaction actions.
- **400–409**: Screen UI widget creation, mount, and fallback recovery errors.
- **410–419**: Tree resolution errors in selection overview, and technology type data extraction / callback payload errors.
- **420–429**: Data retrieval exceptions, report specification execution failures, and template instantiation failures across Shop for Data and Technology Types.
- **440**: Team roles and glossary term query communication errors.
