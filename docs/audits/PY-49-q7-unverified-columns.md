# PY-49 Q7: the 30 columns that cannot be checked against the 6.4 type system

These columns of hand-written specs name keys that no Egeria *type* defines: the values come straight from a runtime,
registry or type-definition response, or from a related-element summary, so the Properties-class table cannot confirm
them and this machine (Egeria 6.3, no 6.4 platform) cannot run them. For each, **laz is asked to read the live 6.4
response of the call in the third column and say keep or drop for each column** (keep = the key is in the response and
is non-empty for at least one row; drop = absent in every row, so the column is dead on 6.4).

Nothing changes until that answer arrives. The find is the method the spec runs (`action.function`), or, for a spec with
no find of its own, the call that supplies its rows (the spec is a detail sub-table or is read by that client method).

| # | Spec | Column | Find / producer to run on 6.4 | Why it is unverified |
|---|---|---|---|---|
| 1 | Asset-Types | super_type | `RegisteredInfo.list_asset_types` (`pyegeria/omvs/registered_info.py:203`, report_spec "Asset-Types") | asset-type definition payload, no element type |
| 2 | My-User | teams | `MyProfile.get_my_profile` | client-built list of the profile's teams (`my_profile.py`) |
| 3 | My-User | communities | `MyProfile.get_my_profile` | client-built list of communities |
| 4 | My-User-MD | teams | `MyProfile.get_my_profile` | same as My-User |
| 5 | My-User-MD | communities | `MyProfile.get_my_profile` | same as My-User |
| 6 | My-User-Note-Logs-Detail | title | `MyProfile.get_my_profile` (note-log detail rows: `my_profile.py:176 _extract_note_log_entries`) | keys of a note-log entry summary; the spec's target `Action` does not describe it |
| 7 | My-User-Note-Logs-Detail | text | same | same |
| 8 | My-User-Note-Logs-Detail | time | same | same |
| 9 | Platforms | omag_servers | `RuntimeManager.get_platforms_by_name` (`runtime_manager.py:2047`, report_spec "Platforms"); the list of servers the platform reports (`omagservers` / `omagServers`) | runtime platform response |
| 10 | Registered-Services | service_name | `RegisteredInfo.list_registered_svcs` (`registered_info.py:75`, `/server-platform/registered-services`) | registered-services response |
| 11 | Registered-Services | service_description | same | same |
| 12 | Registered-Services | service_url_marker | same | same |
| 13 | Registered-Services | service_type | same | same |
| 14 | Registered-Services | service_wiki | same | same |
| 15 | Registered-Services | conformance_profile | same | same |
| 16 | Severity-Definitions | ordinal | `RegisteredInfo.list_severity_definitions` (`registered_info.py:148`, `/audit-log/severity-definitions`) | audit-log severity definitions |
| 17 | Severity-Definitions | severity_code | same | no producer line found; may be absent |
| 18 | Severity-Definitions | system_action | same | same |
| 19 | Severity-Definitions | user_action | same | same |
| 20 | Statement-of-Applicability-Controls | label | `SecurityOfficer.get_statement_of_applicability_controls` (target ControlApplicability, a relationship) | ControlApplicability relationship property |
| 21 | Statement-of-Applicability-Controls | implementation_status | same | same (`ControlApplicabilityProperties.implementationStatus` is in the 6.4 table; the response shape is what is unchecked) |
| 22 | Statement-of-Applicability-Controls | justification | same | same (`justification` is in the table) |
| 23 | Statement-of-Applicability-Controls | inclusion_reasons | same | same (`inclusionReasons` is in the table) |
| 24 | Statement-of-Applicability-Controls | review_date | same | same (`reviewDate` is in the table) |
| 25 | Statement-of-Applicability-Controls | implementation_description | same | same (`implementationDescription` is in the table) |
| 26 | Statement-of-Applicability-Controls | notes | same | NOT in `ControlApplicabilityProperties` (`notes` belongs to Decision): probably dead |
| 27 | Tech-Type-Elements | deployedImplementationType | `EgeriaTech.get_technology_type_elements` | technology-type element summary |
| 28 | TypeDef | beanClassName | `ValidMetadataManager.get_all_entity_defs` / `get_typedef_by_name` (`valid_metadata.py:1820`, `:2427`, entity "TypeDef") | type-definition payload; no producer line found |
| 29 | TypeDef | initialStatus | same | type-definition payload |
| 30 | TypeDef | descriptionWiki | same | type-definition payload; no producer line found |

Likely drops, from what the code and the 6.4 table already say: **#26** (`notes`), **#28** and **#30** (no producer line
anywhere), **#17** (no producer line). Everything else probably stays, but is not provable here.

Rows 20 to 26 are columns of the ControlApplicability **relationship**; 21 to 25 are real fields of
`ControlApplicabilityProperties` in the 6.4 table, so the live check is only that the response carries them.


## Results (2026-11-23)

Live check on a 6.4 platform (laz, read-only SQL and the 6.4 source; LIVECHECK-PY49-Q7-2026-11-23.md):

| Rows | Answer | Applied |
|---|---|---|
| 20 to 25 | KEEP: label 15/15, implementationStatus 14/15, justification 15/15, inclusionReasons 14/15, reviewDate 15/15, implementationDescription 14/15 | none |
| 26 notes | DROP (0/15; not in ControlApplicabilityProperties) | column removed from Statement-of-Applicability-Controls |
| (new) | the spec lacked `description`; `isApplicable` was already there as `is_applicable` ("Applicable") | `description` added |
| 28 to 30 | KEEP, by source: OpenMetadataStoreRESTServices.java:5425-5446 fills beanClassName (name + "Properties"), initialStatus and descriptionWiki | none (the expected drops of 28 and 30 were wrong) |
| UC Catalog Element | a UC catalog is a Namespace with no deployedImplementationType; its qualifiedName starts "Unity Catalog Catalog::" | the spec finds Namespace elements by that qualified-name prefix (QUALIFIED_NAME_PREFIX_SPECS) and has no technology column |

**Rows 1 to 19 and 27, checked read-only on laz 6.4 (signed in as erinoverview; verdicts from the raw JSON keys; LIVECHECK-PY49-Q7-ROWS-1-19-27-2026-11-23.md):**

| Rows | Answer | Applied |
|---|---|---|
| 1 super_type | KEEP (superType 96/96) | none |
| 10, 11, 12, 14 service_name, service_description, service_url_marker, service_wiki | KEEP | the raw key is `serviceURLMarker` (capital URL), which the snake-to-camel mapping never reached, so the 6.2.39 "URL Marker" column was empty 0/55; `_extract_registered_service_properties` now copies it to `serviceUrlMarker` |
| 13 service_type, 15 conformance_profile | DROP (absent in all 55 services) | both columns removed from Registered-Services |
| 16 ordinal | KEEP (16/16) | none |
| 17 severity_code, 18 system_action, 19 user_action | DROP (absent 0/16; rows carry ordinal, name, description) | all three removed from Severity-Definitions |
| 27 deployedImplementationType | KEEP (File System Directory 6/6, PostgreSQL Relational Database, Unity Catalog Server) | none |
| 2 to 5 teams, communities (My-User, My-User-MD) | NO DATA: unverified, test persona has none (no team or community memberships; the raw profile has no such key, the client builds them) | unchanged |
| 6 to 8 note-log title, text, time | NO DATA: unverified, test persona has no note logs | unchanged |
| 9 omag_servers (Platforms) | DROP-CANDIDATE: `get_platforms_by_type` returns 1 platform with no omagServers key (only serverEndpoints, serverId, serverName) | unchanged, awaiting a decision |

Separate finding: `get_platforms_by_name("*")` returns SERVER_ERROR_500 on 6.4; not a spec problem, not addressed here.
