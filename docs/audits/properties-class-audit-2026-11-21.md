# Properties-class audit of built request bodies (2026-11-21)

Egeria 6.4 build plan, branch A5. Run 2 was against Egeria `90232870b2` and A0's tables; see "Runs" (§3 of `DESIGN-EGERIA-6.4-ADDITIONS-BUILD-PLAN-2026-11-21.md`). **This is a report only: nothing in this branch fixes anything.** Each fix below becomes its own small item.

## Why

Egeria deserialises its Properties beans with `@JsonIgnoreProperties(ignoreUnknown=true)`. If a body's `properties.class` names a class that doesn't read a key we send, **Egeria drops that key and reports no error.** That is how TR-89 lost `libraryType`: it was sent under `SoftwareCapabilityProperties`, and only `SourceControlLibraryProperties` reads it.

A wrong, unrelated class is a different case. laz's Egeria already rejects it loudly (`handleInvalidPropertiesObject`, 386 sites), so this audit only hunts the quiet cases.

## What was scanned

| repo | ref | what |
|---|---|---|
| egeria-python | upstream/main `6232bcfa` | `pyegeria/`, `md_processing/` |
| egeria-workspaces | upstream/main `61251c77` | whole tree, read-only via `git archive` into a scratch dir |
| trellis | origin/main `b3d9c69d` | whole tree, read-only via `git archive` into a scratch dir |
| Egeria | `90232870b2` (odpi/egeria main, the #9463 merge) | class hierarchy and Jackson setters, read with `git cat-file` (no checkout) |
| properties table | egeria-python `claude/e64-a0-generated-tables` `83e4fb22` (A0's regeneration, from #9463's head `0dbf468774`, the same tree as `90232870b2`) | `PROPERTIES_CLASS_FIELDS`, passed with `--table` |

Two kinds of file are skipped by default: tests and fakes (`tests/` dirs, `test_*.py`, `fake_*.py`, `conftest.py`), because they don't send to a real Egeria. Use `--include-tests` to scan them too. No Egeria server was called.

To reproduce it:

```bash
python scripts/audit_properties_class_bodies.py pyegeria md_processing <ws-archive> <trellis-archive> \
  --label egeria-python --label egeria-python --label egeria-workspaces --label trellis \
  --base . --base . --base <ws-archive> --base <trellis-archive> \
  --table <A0's properties_class_fields.py> --ref 90232870b2 --report report.md
```

## How "built" was told apart from pass-through

The scan is AST-based and works on Python only.

**Built (checked):**
- a dict literal in our code whose `"class"` is a Properties class;
- plus keys added to it later in the same function: `x["k"] = …`, `x.update({...})` / `x.update(k=…)`, `x.setdefault("k", …)`, `x |= {...}`;
- plus `**` spreads that resolve to another literal in the same function.

A name resolves to its **nearest preceding assignment**, so one `props` reused across `if/elif` branches keeps each branch's keys apart. A string class bound to a name in the same function (`cls = "XProperties"`) is resolved too.

**Built by a table-filtering helper (counted, not checked):** Dr.Egeria's `typed_properties` family in `md_processing/md_processing_utils/typed_properties.py`. These helpers keep only the keys the class reads and note the rest, so they are correct by construction.

**Pass-through (counted, skipped):** a `properties` / `parentRelationshipProperties` / `replacementProperties` slot whose value is a parameter of the enclosing function, meaning the caller supplied the properties. A pyegeria method that takes a whole `body` from its caller isn't counted here. It has no literal to check, so it never appears at all.

**Unclassified (listed, never guessed):**
- a class that is an expression we can't resolve (`f"{t}Properties"`, a parameter, a lookup table);
- a `*Properties` class missing from the table;
- a slot filled by a call or another non-literal;
- a `**` spread or computed key we can't resolve (the static keys are still checked);
- a slot assigned on a parameter (`body["properties"] = {}`);
- a query class whose inherited fields the table lacks.

**What counts as "read":** the table's keys, plus, when an Egeria clone is present, every public setter in the class's superclass chain. Jackson binds through setters (`setterVisibility=PUBLIC_ONLY, fieldVisibility=NONE`), so the setters are the ground truth. This matters because the table has gaps (see "Table gaps seen in use" at the end):
- `gen_properties_class_fields.py`'s field regex misses package-private fields, such as `ResourceListProperties.resourceUse`;
- it also misses superclasses outside the `properties` packages, such as `GetOptions`, `SearchOptions` and `QueryOptions`.

Checked against the table alone, that would give 9 false findings.

**How a parent class is detected (`PARENT_CLASS`):** the named class is an ancestor, in Egeria's hierarchy, of a more specific Properties class that the call is evidently about. The evidence is any of:
- the body's own literal `"typeName"`. When this is present, it is the only evidence used;
- the enclosing function's name, e.g. `create_source_control_library`;
- a URL path segment in the same function, e.g. `/source-control-libraries`.

Without an Egeria clone, "ancestor" is *inferred* as "same kind and a strict superset of fields", and the report says so.

## How this differs from the attribute-consumption audit

`scripts/dr_egeria_attribute_consumption_audit.py` (dr-egeria-command-sync, Step 3) checks the layer above this one:
- **That audit** asks whether a Dr.Egeria processor reads every attribute its compact spec declares. It works spec → processor, by display-name string search.
- **This audit** asks whether the body the code then sends names a class that Egeria will actually read those keys from. It works code → wire, by AST and Egeria's Java.

An attribute can pass the sibling audit and still be lost here, because it was read and sent but under the wrong class. That was TR-89's shape. No parsing was shared: the sibling works on compact-spec JSON and string search, and this one needs Python ASTs.

## Triage and suggested fix items

Each row is a separate fix item. The ones marked *read* were confirmed by reading the code, not only by the script.

| # | where | what is lost | suggested fix | confidence |
|---|---|---|---|---|
| F1 | `pyegeria/core/_server_client.py:5571` `_async_add_search_keyword_to_element` | `keyword` is the **only** key sent; `SearchKeywordProperties` reads `displayName`/`description`, so the keyword entity is created empty | send `displayName` (Dr.Egeria's curation.py already does) | read |
| F2 | `pyegeria/omvs/project_manager.py:1350, 1654, 2387` (create / update project, create task) | `startDate`, `plannedEndDate` | `plannedStartDate`, `plannedCompletionDate` (also `actualStartDate`/`actualCompletionDate` exist) | read |
| F3 | `md_processing/v2/governance.py:374, 530` (Certification) and `:395, 563` (License) | `startDate`, `endDate`; for Certification also `entitlements`, `obligations`, `restrictions` | `coverageStart`, `coverageEnd`. Certification has no entitlements/obligations/restrictions in Egeria: drop them or ask Mandy (License does have them) | read |
| F4 | `pyegeria/core/_server_client.py:532` `FindPropertyNamesProperties` | `openMetadataType`, so the relationship-type filter is silently ignored | `metadataElementTypeName` (from `SearchOptions`) | read |
| F5 | `pyegeria/omvs/glossary_manager.py:1001, 1032` (CSV import); `pyegeria/view/md_processing_utils.py:1490, 1530` (legacy term upsert) | `publishVersionIdentifier`; also `status` at 1490 | `versionIdentifier`; `contentStatus` | read |
| F6 | `md_processing/v2/collection_manager_processor.py:408` AgreementActor | `actorRole`, `agreementStart/End`, `entitlements`, `obligations`, `restrictions`, `usageMeasurements` (only `agreementPartyName` is read) | send `agreementPartyName`; the rest belong to AgreementItem, so check the compact spec | read |
| F7 | `md_processing/v2/collection_manager_processor.py:373` AgreementItem | `agreementItemTypeName` | no Properties class reads it: drop it, or ask whether it should be `typeName` | read |
| F8 | `pyegeria/core/_server_client.py:3951` InformalTag | `name` (low impact: `displayName` is sent too) | drop `name` | read |
| F9 | trellis `resource_explorer/open_data/publish.py:92` `origin_body` | `owner`, `ownerTypeName`, `ownerPropertyName` on `DigitalResourceOriginProperties` | these belong to the `Ownership` classification (`OwnershipProperties`) | script |
| F10 | trellis `surveyors/egeria_investigation_publisher.py:208` | `ClassificationProperties` + `typeName` for the Investigation marker. Also PARENT_CLASS: `InvestigationProperties` exists | send `InvestigationProperties` | read |
| F11 | trellis `scripts/create_measure_definitions.py:200` | `description`, `label` on `ValidValueMemberProperties` (it reads `isDefaultValue`, `ordinal`) | drop them, or put them on the member entity | script |
| F12 | `md_processing/v2/schema_maker.py:300` SchemaLinkProcessor | `properties` with `label`/`description` and **no class** under NewRelationshipRequestBody. pyegeria's `validate_new_relationship_request` doesn't fill the class in | add `f"{om_type}Properties"`, after checking that the relationship class reads label/description | read; 400 not proven live |
| F13 | egeria-workspaces `PyegeriaWebHandler/resource_browser_handler.py` `_create_list` (quickstart :2298, freshstart :2093) | PARENT_CLASS: `CollectionProperties` with `typeName "WorkingSet"`. Nothing is dropped today (`disposition` isn't sent) | send `WorkingSetProperties` | script |
| F14 | trellis, 7 SurveyReport creates (`egeria_publisher.py:1426`, `database/egeria_database_surveyor.py:845, 1386`, `filesystem/egeria_filesystem_surveyor.py:366, 600, 768, 844, 910`) | PARENT_CLASS: `AssetProperties` with `typeName "SurveyReport"`. Nothing is dropped today, but any future `analysisStep`/`completionTime`/… would be | send `SurveyReportProperties` (one trellis item covering all 7) | script |
| F15 | the generator `scripts/gen_properties_class_fields.py` | table gaps: package-private fields and superclasses outside `properties/`. Dr.Egeria's `typed_properties` would **refuse** valid keys, e.g. ResourceList `resourceUse`/`label`/`description`, AssignmentScope `assignmentType`/`description`, SupportingDefinition `rationale`, AssociatedSecurityList `operationName` | derive keys from public setters, as this audit does, or widen the field regex and the scanned paths. **Land it before or with A0's regeneration from `oak2026`** | read (Java checked) |

`exchange-quickstart/project_manager.py` in egeria-workspaces had F2's sibling (`AssignmentScopeProperties`), which turned out to be a table gap, not a finding. That file is a vendored copy of pyegeria, so fixing F2 in pyegeria won't reach it.

## Runs

Each re-run adds a row here, so the drop in unclassified sites shows over time. The code refs were the same in runs 1–3: egeria-python `6232bcfa`, egeria-workspaces `61251c77`, trellis `b3d9c69d` (each read with `git archive`).

| run | date | Egeria ref (hierarchy, setters) | tables ref | findings (UNREAD / PARENT / NO_CLASS) | unclassified (python / workspaces / trellis) |
|---|---|---|---|---|---|
| 1 | 2026-11-21 | `c61bad6514` | egeria-python upstream/main `6232bcfa` (generated from `c61bad6514`) | 19 / 11 / 1 | **127** (94 / 12 / 21) |
| 2 | 2026-11-21 | `90232870b2` (#9463 merged) | A0 `83e4fb22` (generated from `0dbf468774`, the same tree) | 19 / 11 / 1 | **127** (94 / 12 / 21) |
| 3 | 2026-11-21 | `90232870b2`; **setter keys by Jackson's naming** (A6) | PY-45 `a0f914e4` (setters through the whole chain) | 19 / 11 / 1 | **127** (94 / 12 / 21) |
| 4 | 2026-11-21 | as run 3; egeria-python code = A6 `claude/e64-a6-consolidation` instead of `6232bcfa` | as run 3 | 19 / 11 / 1 | **129** (96 / 12 / 21) |

Run 2 gave the same findings as run 1, row for row. #9463 adds new types and endpoints, but none of the bodies we build today use them. A0's table still has every F15 gap, so the generator fix is still needed.

Run 3 changes only how the script names Egeria's setters, and the table. The script now uses gen_properties_class_fields' own parser (PY-45's rule): Jackson's legacy naming (`setURL` → `url`, `setGUID` → `guid`, not java.beans' `URL`), `@JsonProperty` names honoured, and `@JsonIgnore`'d, multi-argument and nested-class setters not counted. That changes the setter keys of 70 Egeria classes at `90232870b2`, but no finding: the 19 / 11 / 1 are the same rows as runs 1 and 2. PY-45's table already has every F15 key, so the "table gaps" section is empty.

Run 4 scans the A6 code. Its 2 extra unclassified sites are the shared 6.4 checker itself (`pyegeria/core/egeria_6_4_bodies.py` `checked_body`, whose class is a parameter) and DevopsPipeline's Branch keywords body (`e64.BRANCH_PROPERTIES`, a names-module constant). Both are checked at run time by `checked_body` (rules 3 and 4), so neither is a gap. The A1–A3 6.4 wrappers add no finding.

## Unclassified, in short

There are 127 unclassified sites in run 2, all listed below.

**Largest bucket, the inter-procedural follow-up:** 57 sites.
- 52 have a class built from a type name, such as `f"{type}Properties"` or `prop_name + "Properties"`, that the script can't resolve to a string: egeria-python 32, egeria-workspaces 7, trellis 13.
- 5 have a slot filled by `md_processing_utils/common_md_utils.py` `set_element_prop_body`.

These helpers build keys for whatever type their caller hands them, so they can only be checked per call site: resolve the type argument at each caller, then check the helper's keys against that class. That is the next item to shrink this count.

**The rest (70):**

| reason | sites |
|---|---|
| slot filled by another non-literal (calls such as `element_properties(...)`, `_build_relationship_properties(...)`) | 39 |
| unresolved `**` spread or `update(...)`, or a class that may come from a spread | 19 |
| name not bound in scope | 7 |
| computed key (`x[prop_name] = …`) | 2 |
| class missing from the table | 2 |
| slot set on a parameter | 1 |

## Re-run on 6.4

Done: that is run 2 in the table above. Before the 6.4 upgrade on laz, re-run the audit with the tables on egeria-python main once A0 merges, and add a row.

# Generated report (run 2)

- properties table: A0 83e4fb22 md_processing/md_processing_utils/properties_class_fields.py (generated from Egeria 0dbf468774)
- class hierarchy: Egeria 90232870b2 (git cat-file, read-only): superclasses, and keys read = table ∪ public setters in the class chain
- tests and fakes: skipped

### Totals

| repo | files | bodies checked | UNREAD_KEYS | PARENT_CLASS | NO_CLASS | unclassified | pass-through | table-filtering helper |
|---|---|---|---|---|---|---|---|---|
| egeria-python | 177 | 185 | 16 | 0 | 1 | 94 | 4 | 4 |
| egeria-workspaces | 204 | 55 | 0 | 2 | 0 | 12 | 0 | 0 |
| trellis | 819 | 75 | 3 | 9 | 0 | 21 | 2 | 0 |

### UNREAD_KEYS

| repo | file:line | function | class | keys | detail | suggested fix |
|---|---|---|---|---|---|---|
| egeria-python | `pyegeria/core/_server_client.py:532` | `ServerClient._async_get_relationships_with_property_value` | FindPropertyNamesProperties | openMetadataType | FindPropertyNamesProperties doesn't read openMetadataType (added at line 534) | no single class reads them all (openMetadataType: no class) — drop them, split them into the right body, or move them to additionalProperties |
| egeria-python | `pyegeria/core/_server_client.py:3951` | `ServerClient._async_create_informal_tag` | InformalTagProperties | name | InformalTagProperties doesn't read name (added at line 3953) | no subclass of InformalTagProperties reads them; classes that do: FindPropertyNameProperties — use the right one, or drop/move the keys |
| egeria-python | `pyegeria/core/_server_client.py:5571` | `ServerClient._async_add_search_keyword_to_element` | SearchKeywordProperties | keyword | SearchKeywordProperties doesn't read keyword (added at line 5573) | no single class reads them all (keyword: no class) — drop them, split them into the right body, or move them to additionalProperties |
| egeria-python | `pyegeria/omvs/glossary_manager.py:1032` | `GlossaryManager._async_import_glossary_terms_from_csv` | GlossaryTermProperties | publishVersionIdentifier | GlossaryTermProperties doesn't read publishVersionIdentifier (added at line 1041) | no single class reads them all (publishVersionIdentifier: no class) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: publishVersionIdentifier → versionIdentifier |
| egeria-python | `pyegeria/omvs/glossary_manager.py:1001` | `GlossaryManager._async_import_glossary_terms_from_csv` | GlossaryTermProperties | publishVersionIdentifier | GlossaryTermProperties doesn't read publishVersionIdentifier (added at line 1010) | no single class reads them all (publishVersionIdentifier: no class) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: publishVersionIdentifier → versionIdentifier |
| egeria-python | `pyegeria/omvs/project_manager.py:1350` | `ProjectManager._async_create_project` | ProjectProperties | plannedEndDate, startDate | ProjectProperties doesn't read plannedEndDate, startDate (added at line 1359, 1360) | no single class reads them all (plannedEndDate: no class; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: plannedEndDate → plannedStartDate / plannedCompletionDate; startDate → actualStartDate / plannedStartDate |
| egeria-python | `pyegeria/omvs/project_manager.py:1654` | `ProjectManager._async_update_project` | ProjectProperties | plannedEndDate, startDate | ProjectProperties doesn't read plannedEndDate, startDate (added at line 1663, 1664) | no single class reads them all (plannedEndDate: no class; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: plannedEndDate → plannedStartDate / plannedCompletionDate; startDate → actualStartDate / plannedStartDate |
| egeria-python | `pyegeria/omvs/project_manager.py:2387` | `ProjectManager._async_create_project_task` | ProjectProperties | plannedEndDate, startDate | ProjectProperties doesn't read plannedEndDate, startDate (added at line 2396, 2397) | no single class reads them all (plannedEndDate: no class; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: plannedEndDate → plannedStartDate / plannedCompletionDate; startDate → actualStartDate / plannedStartDate |
| egeria-python | `pyegeria/view/md_processing_utils.py:1530` | `process_term_upsert_command` | GlossaryTermProperties | publishVersionIdentifier | GlossaryTermProperties doesn't read publishVersionIdentifier (added at line 1533) | no single class reads them all (publishVersionIdentifier: no class) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: publishVersionIdentifier → versionIdentifier |
| egeria-python | `pyegeria/view/md_processing_utils.py:1490` | `process_term_upsert_command` | GlossaryTermProperties | publishVersionIdentifier, status | GlossaryTermProperties doesn't read publishVersionIdentifier, status (added at line 1493) | no single class reads them all (publishVersionIdentifier: no class; status: SemanticAssignmentQueryProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: publishVersionIdentifier → versionIdentifier |
| egeria-python | `md_processing/v2/collection_manager_processor.py:408` | `CollectionLinkProcessor.apply_changes` | AgreementActorProperties | actorRole, agreementEnd, agreementStart, entitlements, obligations, restrictions, usageMeasurements | AgreementActorProperties doesn't read actorRole, agreementEnd, agreementStart, entitlements, obligations, restrictions, usageMeasurements (added at line 411, 412, 413, 414, 415, 416, 417) | no single class reads them all (actorRole: no class; agreementEnd: AgreementItemProperties; agreementStart: AgreementItemProperties; entitlements: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; obligations: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; restrictions: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; usageMeasurements: AgreementItemProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: agreementEnd → agreementPartyName; agreementStart → agreementPartyName |
| egeria-python | `md_processing/v2/collection_manager_processor.py:373` | `CollectionLinkProcessor.apply_changes` | AgreementItemProperties | agreementItemTypeName | AgreementItemProperties doesn't read agreementItemTypeName (added at line 377) | no single class reads them all (agreementItemTypeName: no class) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: agreementItemTypeName → agreementItemId / agreementStart |
| egeria-python | `md_processing/v2/governance.py:563` | `GovernanceLinkProcessor.apply_changes` | LicenseProperties | endDate, startDate | LicenseProperties doesn't read endDate, startDate (added at line 566, 567) | no single class reads them all (endDate: no class; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties |
| egeria-python | `md_processing/v2/governance.py:530` | `GovernanceLinkProcessor.apply_changes` | CertificationProperties | endDate, entitlements, obligations, restrictions, startDate | CertificationProperties doesn't read endDate, entitlements, obligations, restrictions, startDate (added at line 533, 534, 545, 546, 547) | no single class reads them all (endDate: no class; entitlements: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; obligations: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; restrictions: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: obligations → conditions |
| egeria-python | `md_processing/v2/governance.py:395` | `GovernanceLinkProcessor.apply_changes` | LicenseProperties | endDate, startDate | LicenseProperties doesn't read endDate, startDate (added at line 397, 398) | no single class reads them all (endDate: no class; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties |
| egeria-python | `md_processing/v2/governance.py:374` | `GovernanceLinkProcessor.apply_changes` | CertificationProperties | endDate, entitlements, obligations, restrictions, startDate | CertificationProperties doesn't read endDate, entitlements, obligations, restrictions, startDate (added at line 376, 377, 388, 389, 390) | no single class reads them all (endDate: no class; entitlements: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; obligations: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; restrictions: AgreementItemProperties, CertificationTypeProperties, LicenseProperties …; startDate: RegisteredIntegrationConnectorProperties) — drop them, split them into the right body, or move them to additionalProperties; closest names this class reads: obligations → conditions |
| trellis | `packages/resource-explorer/resource_explorer/open_data/publish.py:92` | `origin_body` | DigitalResourceOriginProperties | owner, ownerPropertyName, ownerTypeName | DigitalResourceOriginProperties doesn't read owner, ownerPropertyName, ownerTypeName (added at line 92, 93) | no subclass of DigitalResourceOriginProperties reads them; classes that do: OwnershipProperties — use the right one, or drop/move the keys; closest names this class reads: ownerPropertyName → organizationPropertyName; ownerTypeName → typeName |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/egeria_investigation_publisher.py:208` | `_apply_investigation_marker` | ClassificationProperties | typeName | ClassificationProperties doesn't read typeName (added at line 209) | name the subclass that reads them: AbstractConceptProperties, AccountingCodesProperties, ActivityDescriptionProperties, AnchorsProperties |
| trellis | `packages/resource-explorer/scripts/create_measure_definitions.py:200` | `_link_member` | ValidValueMemberProperties | description, label | ValidValueMemberProperties doesn't read description, label (added at line 203, 204) | no subclass of ValidValueMemberProperties reads them; classes that do: ActionRequesterProperties, ActionsProperties, AdjacentLocationProperties, AnnotationExtensionProperties … — use the right one, or drop/move the keys |

### PARENT_CLASS

| repo | file:line | function | class | keys | detail | suggested fix |
|---|---|---|---|---|---|---|
| egeria-workspaces | `compose-configs/egeria-freshstart/PyegeriaWebHandler/resource_browser_handler.py:2093` | `_create_list` | CollectionProperties | — | CollectionProperties is a parent of WorkingSetProperties (typeName "WorkingSet") [Egeria hierarchy]; subclass-only fields: disposition | send WorkingSetProperties (check the endpoint's element type first) |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/resource_browser_handler.py:2298` | `_create_list` | CollectionProperties | — | CollectionProperties is a parent of WorkingSetProperties (typeName "WorkingSet") [Egeria hierarchy]; subclass-only fields: disposition | send WorkingSetProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/egeria_investigation_publisher.py:208` | `_apply_investigation_marker` | ClassificationProperties | typeName | ClassificationProperties is a parent of InvestigationProperties (function _apply_investigation_marker) [Egeria hierarchy]; subclass-only fields: extendedProperties, typeName | send InvestigationProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/egeria_publisher.py:1426` | `EgeriaPublisher._create_survey_report` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/database/egeria_database_surveyor.py:845` | `EgeriaDatabaseSurveyor.publish_step_annotations` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/database/egeria_database_surveyor.py:1386` | `EgeriaDatabaseSurveyor.publish_local_survey` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/filesystem/egeria_filesystem_surveyor.py:366` | `EgeriaFileSystemSurveyor.catalog_and_survey` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/filesystem/egeria_filesystem_surveyor.py:600` | `EgeriaFileSystemSurveyor._publish_step_annotations` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/filesystem/egeria_filesystem_surveyor.py:768` | `EgeriaFileSystemSurveyor.publish_file_profiles` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/filesystem/egeria_filesystem_surveyor.py:844` | `EgeriaFileSystemSurveyor.publish_confirmed_data_classes` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/filesystem/egeria_filesystem_surveyor.py:910` | `EgeriaFileSystemSurveyor.request_action_for_finding` | AssetProperties | — | AssetProperties is a parent of SurveyReportProperties (typeName "SurveyReport") [Egeria hierarchy]; subclass-only fields: analysisParameters, analysisStep, authors, completionMessage, completionTime, contentStatus, createdTime, formula … | send SurveyReportProperties (check the endpoint's element type first) |

### NO_CLASS

| repo | file:line | function | class | keys | detail | suggested fix |
|---|---|---|---|---|---|---|
| egeria-python | `md_processing/v2/schema_maker.py:300` | `SchemaLinkProcessor.apply_changes` | — | description, label | `properties` under NewRelationshipRequestBody has no class | add the Properties class of the element/relationship/classification type |

### Unclassified

| repo | file:line | function | why not classified |
|---|---|---|---|
| egeria-python | `pyegeria/core/_server_client.py:685` | `ServerClient._async_get_elements_by_property_value` | FindPropertyNamesProperties: spread **kwargs: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/core/_server_client.py:1339` | `ServerClient._async_update_comment` | `body['properties']` set on a parameter: the caller's body, class not known here |
| egeria-python | `pyegeria/core/_server_client.py:6645` | `ServerClient._async_find_request` | FindPropertyNamesProperties: spread **_filters: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/core/_server_client.py:6817` | `ServerClient._async_get_guid_request` | class is `body_model.__name__`: not resolvable to a string |
| egeria-python | `pyegeria/core/_server_client.py:7515` | `ServerClient._async_new_relationship_request` | class is `prop_class`: not resolvable to a string |
| egeria-python | `pyegeria/omvs/automated_curation.py:4247` | `AutomatedCuration._async_add_catalog_target` | `properties` is `self._catalog_target_properties(catalog_target_name, connection_name, metadata_src_qual_name, config`: not a literal |
| egeria-python | `pyegeria/omvs/automated_curation.py:4374` | `AutomatedCuration._async_update_catalog_target` | `properties` is `self._catalog_target_properties(catalog_target_name, connection_name, metadata_src_qual_name, config`: not a literal |
| egeria-python | `pyegeria/omvs/classification_explorer.py:5608` | `ClassificationExplorer._async_retrieve_instance_for_guid` | class FindProperties is not in PROPERTIES_CLASS_FIELDS |
| egeria-python | `pyegeria/omvs/collection_manager.py:1645` | `CollectionManager._async_create_collection` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:1629` | `CollectionManager._async_create_collection` | class is `f'{c}Properties'`: not resolvable to a string |
| egeria-python | `pyegeria/omvs/collection_manager.py:2150` | `CollectionManager._async_create_data_spec_collection` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:2359` | `CollectionManager._async_create_report_type_collection` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:2541` | `CollectionManager._async_create_report_spec` | `properties` is `spec_properties.model_dump(exclude_none=True)`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:2613` | `CollectionManager._async_create_question_spec_folder` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:2726` | `CollectionManager._async_create_security_list` | class is `prop + 'Properties'`: not resolvable to a string |
| egeria-python | `pyegeria/omvs/collection_manager.py:3064` | `CollectionManager._async_create_data_dictionary_collection` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:3270` | `CollectionManager._async_create_skill_set_collection` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/collection_manager.py:3424` | `CollectionManager._async_create_reference_list_collection` | `properties` is `collection_properties.model_dump()`: not a literal |
| egeria-python | `pyegeria/omvs/data_designer.py:3399` | `DataDesigner._as_data_class` | DataClassProperties: spread **body['properties']: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/omvs/data_designer.py:3406` | `DataDesigner._as_value_assignment` | DataValueAssignmentProperties: spread **body['properties']: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/omvs/data_discovery.py:1994` | `DataDiscovery._as_survey_report` | SurveyReportProperties: spread **body['properties']: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/omvs/my_profile.py:1378` | `MyProfile._async_create_my_todo` | ToDoProperties: update({k: v for k, v in extra_properties.items() if v is not None}) at line 1400: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/omvs/my_profile.py:1496` | `MyProfile._async_create_meeting` | MeetingProperties: update({k: v for k, v in extra_properties.items() if v is not None}) at line 1513: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/omvs/my_profile.py:1589` | `MyProfile._async_create_review` | ReviewProperties: update({k: v for k, v in extra_properties.items() if v is not None}) at line 1605: keys not known (the static keys were checked) |
| egeria-python | `pyegeria/omvs/project_manager.py:1346` | `ProjectManager._async_create_project` | class is `f'{classification_name}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:404` | `set_create_body` | `parentRelationshipProperties` is `parent_props` = unbound here: not a literal |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:409` | `set_create_body` | `properties` is `''`: not a literal |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:433` | `set_update_body` | `properties` is `''`: not a literal |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:439` | `set_rel_prop_body` | class is `prop_name + 'Properties'`: not resolvable to a string |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:500` | `set_element_prop_body` | class is `prop_name + 'Properties'`: not resolvable to a string |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:1016` | `set_rel_request_body` | `properties` is `''`: not a literal |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:1039` | `set_rel_request_body_for_type` | class is `class_prop`: not resolvable to a string |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:1084` | `set_element_status_request_body` | class is `f'{camel_to_title_case(object_type)}StatusRequestBody'`: not resolvable to a string |
| egeria-python | `md_processing/md_processing_utils/common_md_utils.py:1115` | `set_object_classifications` | class is `f'{classification}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/v2/asset_maker.py:80` | `AssetMakerProcessor.apply_changes` | `replacementProperties` is `replacement` = unbound here: not a literal |
| egeria-python | `md_processing/v2/asset_maker.py:89` | `AssetMakerProcessor.apply_changes` | `parentRelationshipProperties` is `parent_props` = unbound here: not a literal |
| egeria-python | `md_processing/v2/curation.py:301` | `_build_classification_properties` | class is `spec.props_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/curation.py:373` | `CurationClassifyProcessor.apply_changes` | class is `'UpdateClassificationRequestBody' if use_update else 'NewClassificationRequestBody'`: not resolvable to a string |
| egeria-python | `md_processing/v2/data_designer.py:169` | `DataValueSpecificationProcessor.apply_changes` | `properties` is `props` = _with_create_defaults(props): not a literal |
| egeria-python | `md_processing/v2/data_designer.py:97` | `DataValueSpecificationProcessor.apply_changes` | class is `f"{om_type or 'DataValueSpecification'}Properties"`: not resolvable to a string |
| egeria-python | `md_processing/v2/data_designer.py:513` | `DataFieldProcessor._sync_all_rels` | NestedDataFieldProperties: spread **_part_of_props(attributes): keys not known (the static keys were checked) |
| egeria-python | `md_processing/v2/data_designer.py:509` | `DataFieldProcessor._sync_all_rels` | MemberDataFieldProperties: spread **_part_of_props(attributes): keys not known (the static keys were checked) |
| egeria-python | `md_processing/v2/data_designer.py:675` | `DataClassProcessor.apply_changes` | `properties` is `props` = _with_create_defaults(props): not a literal |
| egeria-python | `md_processing/v2/data_designer.py:604` | `DataClassProcessor.apply_changes` | class is `f"{om_type or 'DataClass'}Properties"`: not resolvable to a string |
| egeria-python | `md_processing/v2/data_designer.py:999` | `DataDesignerLinkProcessor.apply_changes` | class is `f'{om_type}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/v2/embedded_process.py:77` | `EmbeddedProcessProcessor.apply_changes` | `properties` is `props` = set_element_prop_body('Embedded Process', qualified_name, attributes): not a literal |
| egeria-python | `md_processing/v2/feedback.py:102` | `FeedbackProcessor.apply_changes` | `properties` is `{k: v for k, v in entry_props.items() if v not in (None, '', [], {})}`: not a literal |
| egeria-python | `md_processing/v2/feedback.py:93` | `FeedbackProcessor.apply_changes` | class is `f'{entry_type}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/v2/glossary.py:166` | `TermProcessor._classify_term` | `properties` is `props` = unbound here: not a literal |
| egeria-python | `md_processing/v2/glossary.py:455` | `GlossaryClassifyProcessor.apply_changes` | class is `props_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/glossary.py:667` | `TermAsContextProcessor.apply_changes` | UsedInContextProperties: key prop_name added at line 674: keys not known (the static keys were checked) |
| egeria-python | `md_processing/v2/governance.py:109` | `GovernanceProcessor._to_base_governance_definition_properties` | GovernanceDefinitionProperties: key key added at line 130: keys not known (the static keys were checked) |
| egeria-python | `md_processing/v2/governance.py:180` | `GovernanceProcessor.apply_changes` | `properties` is `self.filter_update_properties(prop_body, attributes.get('Merge Update', {}).get('value', True))`: not a literal |
| egeria-python | `md_processing/v2/governance.py:688` | `GovernanceLinkProcessor.apply_changes` | `properties` is `set_rel_prop_body(object_type, attributes)`: not a literal |
| egeria-python | `md_processing/v2/governance.py:658` | `GovernanceLinkProcessor.apply_changes` | `properties` is `set_rel_prop_body(object_type, attributes)`: not a literal |
| egeria-python | `md_processing/v2/governance.py:523` | `GovernanceLinkProcessor.apply_changes` | `properties` is `set_rel_prop_body(object_type, attributes)`: not a literal |
| egeria-python | `md_processing/v2/governance.py:516` | `GovernanceLinkProcessor.apply_changes` | `properties` is `set_rel_prop_body(object_type, attributes)`: not a literal |
| egeria-python | `md_processing/v2/governance.py:509` | `GovernanceLinkProcessor.apply_changes` | `properties` is `set_rel_prop_body(object_type, attributes)`: not a literal |
| egeria-python | `md_processing/v2/lineage_linker.py:121` | `_build_relationship_properties` | class is `_RELATIONSHIP_PROPERTIES_CLASS[relationship_type]`: not resolvable to a string |
| egeria-python | `md_processing/v2/lineage_linker.py:175` | `LineageLinkProcessor.apply_changes` | `properties` is `properties` = _build_relationship_properties(relationship_type, attributes): not a literal |
| egeria-python | `md_processing/v2/lineage_linker.py:244` | `UpdateLineageRelationshipProcessor.apply_changes` | `properties` is `properties` = _build_relationship_properties(relationship_type, attributes): not a literal |
| egeria-python | `md_processing/v2/metadata_expert.py:84` | `_attribute_type` | class is `cls`: not resolvable to a string |
| egeria-python | `md_processing/v2/metadata_expert.py:97` | `type_def_body` | class is `_CATEGORY_CLASS[category]`: not resolvable to a string |
| egeria-python | `md_processing/v2/metadata_expert.py:415` | `element_properties` | class is `class_name`: not resolvable to a string |
| egeria-python | `md_processing/v2/metadata_expert.py:448` | `new_instance_body` | `properties` is `props` = element_properties(_v(attributes, 'Instance Properties'), 'EntityElementProperti: not a literal |
| egeria-python | `md_processing/v2/metadata_expert.py:469` | `update_properties_body` | `properties` is `props` = element_properties(properties, class_name, declared, type_name): not a literal |
| egeria-python | `md_processing/v2/metadata_expert.py:482` | `related_elements_body` | `properties` is `props` = element_properties(_v(attributes, 'Relationship Properties'), 'RelationshipEleme: not a literal |
| egeria-python | `md_processing/v2/metadata_expert.py:559` | `InstanceClassificationProcessor.apply_changes` | `properties` is `cls_props` = element_properties(props, 'ClassificationElementProperties', declared, name): not a literal |
| egeria-python | `md_processing/v2/processors.py:360` | `AsyncBaseCommandProcessor._sync_governance_classifications` | class is `prop_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/processors.py:481` | `AsyncBaseCommandProcessor._sync_referenceable_extras` | `properties` is `typed` = unbound here: not a literal |
| egeria-python | `md_processing/v2/processors.py:466` | `AsyncBaseCommandProcessor._sync_referenceable_extras` | `properties` is `props` = unbound here: not a literal |
| egeria-python | `md_processing/v2/processors.py:547` | `AsyncBaseCommandProcessor._sync_referenceable_classifications` | class is `spec.props_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/processors.py:536` | `AsyncBaseCommandProcessor._sync_referenceable_classifications` | class is `spec.props_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/processors.py:598` | `AsyncBaseCommandProcessor._sync_term_naming_classifications` | class is `spec.props_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/project.py:163` | `ProjectProcessor.apply_changes` | class is `type_classification`: not resolvable to a string |
| egeria-python | `md_processing/v2/project.py:160` | `ProjectProcessor.apply_changes` | ProjectClassificationProperties: spread **project_classification: keys not known (the static keys were checked) |
| egeria-python | `md_processing/v2/project.py:210` | `ProjectProcessor._apply_project_classifications` | class is `type_classification`: not resolvable to a string |
| egeria-python | `md_processing/v2/project.py:201` | `ProjectProcessor._apply_project_classifications` | ProjectClassificationProperties: spread **project_classification: keys not known (the static keys were checked) |
| egeria-python | `md_processing/v2/reference_data.py:536` | `ValidValueLinkProcessor.apply_changes` | class is `f'{om_type}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/v2/report.py:323` | `upsert_dashboard_asset` | `properties` has no literal class; it may come from **update_props |
| egeria-python | `md_processing/v2/report.py:398` | `ReportProcessor.apply_changes` | `properties` is `props` = set_element_prop_body('Report', qualified_name, attributes): not a literal |
| egeria-python | `md_processing/v2/saved_query.py:67` | `SavedQueryProcessor.apply_changes` | `properties` is `props` = set_element_prop_body('SavedQuery', qualified_name, attributes): not a literal |
| egeria-python | `md_processing/v2/schema_maker.py:66` | `_outer_body` | `parentRelationshipProperties` has no literal class; it may come from **parent_props or {'class': f'{rel_type}Properties'} |
| egeria-python | `md_processing/v2/schema_maker.py:66` | `_outer_body` | class is `f'{rel_type}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/v2/schema_maker.py:178` | `SchemaElementProcessor.apply_changes` | `properties` is `self.filter_update_properties(props, _v(attributes, 'Merge Update', True))`: not a literal |
| egeria-python | `md_processing/v2/schema_maker.py:106` | `SchemaElementProcessor.apply_changes` | class is `props_class`: not resolvable to a string |
| egeria-python | `md_processing/v2/schema_maker.py:226` | `SchemaTemplateProcessor.apply_changes` | `replacementProperties` is `replacement` = unbound here: not a literal |
| egeria-python | `md_processing/v2/schema_maker.py:358` | `SchemaClassificationProcessor.apply_changes` | class is `f'{om_type}Properties'`: not resolvable to a string |
| egeria-python | `md_processing/v2/security_officer.py:116` | `StatementOfApplicabilityProcessor.apply_changes` | `properties` is `self.filter_update_properties(props, merge_update)`: not a literal |
| egeria-python | `md_processing/v2/security_officer.py:353` | `SurveyReportProcessor.apply_changes` | `properties` is `self.filter_update_properties(props, merge_update)`: not a literal |
| egeria-python | `md_processing/v2/security_officer.py:404` | `SecurityFindingProcessor.apply_changes` | `properties` is `self.filter_update_properties(props, merge_update)`: not a literal |
| egeria-python | `md_processing/v2/solution_architect.py:253` | `ComponentProcessor.apply_changes` | `properties` is `prop_body` = set_element_prop_body(om_type or 'SolutionComponent', qualified_name, attributes: not a literal |
| egeria-python | `md_processing/v2/solution_architect.py:227` | `ComponentProcessor.apply_changes` | `properties` is `prop_body` = set_element_prop_body(om_type or 'SolutionComponent', qualified_name, attributes: not a literal |
| egeria-python | `md_processing/v2/solution_architect.py:799` | `SolutionLinkProcessor.apply_changes` | class is `f'{om_type}Properties'`: not resolvable to a string |
| egeria-workspaces | `compose-configs/egeria-freshstart/PyegeriaWebHandler/resource_browser_handler.py:1997` | `_membership_body` | `properties` is `dict(props, **{'class': 'CollectionMembershipProperties'})`: not a literal |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/data_scope_handler.py:250` | `_write_body` | class is `body_class`: not resolvable to a string |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/data_scope_handler.py:247` | `_write_body` | class is `props_class`: not resolvable to a string |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/governance_classifications_handler.py:387` | `set_classification_members` | class is `cfg['properties_class']`: not resolvable to a string |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/resource_browser_handler.py:2199` | `_membership_body` | `properties` is `dict(props, **{'class': 'CollectionMembershipProperties'})`: not a literal |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/resource_locator_lens_handler.py:179` | `_lens_properties` | DataLensProperties: spread **dims: keys not known (the static keys were checked) |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/resource_locator_lens_handler.py:314` | `create_lens` | `properties` is `_lens_properties(name, body.description or '', dims, qn)`: not a literal |
| egeria-workspaces | `compose-configs/egeria-quickstart/PyegeriaWebHandler/resource_locator_lens_handler.py:342` | `edit_lens` | `properties` has no literal class; it may come from **kept |
| egeria-workspaces | `exchange-quickstart/coco-dags/coco_egeria_client.py:69` | `Egeria.create` | class is `properties_class`: not resolvable to a string |
| egeria-workspaces | `exchange-quickstart/coco-dags/coco_egeria_client.py:78` | `Egeria.update` | class is `properties_class`: not resolvable to a string |
| egeria-workspaces | `exchange-quickstart/coco-dags/coco_egeria_client.py:84` | `Egeria.attach` | class is `properties_class`: not resolvable to a string |
| egeria-workspaces | `exchange-quickstart/coco-dags/coco_egeria_client.py:91` | `Egeria.classify` | class is `properties_class`: not resolvable to a string |
| trellis | `packages/egeria-advisor/advisor/analytics.py:62` | `AnalyticsManager._load_statistics` | class is `data.get('total_classes', 0)`: not resolvable to a string |
| trellis | `packages/egeria-advisor/advisor/enhanced_relationships.py:74` | `EnhancedRelationshipQueryHandler.find_class` | class is `cls`: not resolvable to a string |
| trellis | `packages/egeria-advisor/advisor/enhanced_relationships.py:100` | `EnhancedRelationshipQueryHandler.find_function` | class is `cls['name']`: not resolvable to a string |
| trellis | `packages/egeria-advisor/advisor/enhanced_relationships.py:151` | `EnhancedRelationshipQueryHandler.get_class_hierarchy` | class is `cls['name']`: not resolvable to a string |
| trellis | `packages/egeria-advisor/advisor/agents/pyegeria_agent.py:67` | `PyEgeriaAgent.__init__` | class is `['class', 'what is', 'tell me about', 'explain', 'manager', 'client', 'handler', 'widget']`: not resolvable to a string |
| trellis | `packages/egeria-advisor/advisor/agents/pyegeria_agent.py:498` | `PyEgeriaAgent.generate_response` | class is `QueryType.CONCEPT`: not resolvable to a string |
| trellis | `packages/resource-explorer/resource_explorer/curate_plan.py:217` | `_classification_write` | class RetentionClassificationProperties is not in PROPERTIES_CLASS_FIELDS |
| trellis | `packages/resource-explorer/resource_explorer/curate_plan.py:205` | `_classification_write` | CriticalityProperties: spread **common(): keys not known (the static keys were checked) |
| trellis | `packages/resource-explorer/resource_explorer/curate_plan.py:199` | `_classification_write` | ConfidentialityProperties: spread **common(): keys not known (the static keys were checked) |
| trellis | `packages/resource-explorer/resource_explorer/dr_egeria_runner.py:538` | `_Steps._element` | class is `properties_class`: not resolvable to a string |
| trellis | `packages/resource-explorer/resource_explorer/egeria_outbox.py:522` | `_refresh_adopted_annotation` | `properties` is `props` = dict((payload or {}).get('properties') or {}): not a literal |
| trellis | `packages/resource-explorer/resource_explorer/egeria_outbox.py:556` | `_create_collection_membership` | `properties` is `dict(props, **{'class': 'CollectionMembershipProperties'})`: not a literal |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/annotation_props.py:191` | `build_annotation_props` | class is `egeria_class`: not resolvable to a string |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/annotation_props.py:411` | `build_annotation_body` | `properties` is `build_annotation_props(ann, qualified_name)`: not a literal |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/egeria_investigation_publisher.py:94` | `_initial_classifications` | class is `f'{classification}Properties'`: not resolvable to a string |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/investigation_reclassifier.py:329` | `InvestigationReclassifier._move_kind_classification` | `properties` is `props` = _initial_classifications(to_kind, hypothesis)[to_kind]: not a literal |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/database/bootstrap_data_classes.py:273` | `_vvd_body` | ValidValueDefinitionProperties: spread **props: keys not known (the static keys were checked) |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/database/egeria_database_surveyor.py:1756` | `EgeriaDatabaseSurveyor._retire_superseded_verdicts` | class is `f'{type_name}Properties' if type_name else 'AnnotationProperties'`: not resolvable to a string |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/database/quality/egeria_rules.py:143` | `rule_properties` | class is `PROPERTIES_CLASS`: not resolvable to a string |
| trellis | `packages/resource-explorer/resource_explorer/surveyors/database/quality/egeria_rules.py:394` | `_retire` | class is `PROPERTIES_CLASS`: not resolvable to a string |
| trellis | `packages/resource-explorer/scripts/backfill_classification_annotations.py:188` | `update_body` | class is `PROPERTIES_CLASS`: not resolvable to a string |

### Table gaps seen in use

Keys our code sends that Egeria does read (a public setter in the class chain) but
PROPERTIES_CLASS_FIELDS lacks. Not findings; they are gen_properties_class_fields misses
(package-private fields, or superclasses outside the scanned packages), and Dr.Egeria's
typed_properties would wrongly refuse to send them.

| class | keys the table lacks |
|---|---|
| AssignmentScopeProperties | assignmentType, description |
| AssociatedSecurityListProperties | operationName |
| FindProjectClassificationProperties | pageSize, startFrom |
| FindPropertyNameProperties | asOfTime, effectiveTime, forDuplicateProcessing, forLineage, metadataElementTypeName |
| FindPropertyNamesProperties | anchorDomainName, anchorGUID, anchorScopeGUID, asOfTime, effectiveTime, forDuplicateProcessing, forLineage, governanceZoneFilter, graphQueryDepth, includeOnlyClassifiedElements, includeOnlyRelationships, limitResultsByStatus, maxMermaidNodeCount, metadataElementSubtypeNames, metadataElementTypeName, pageSize, relationshipsPageSize, sequencingOrder, sequencingProperty, skipClassifiedElements, skipRelationships, startFrom |
| ResourceListProperties | additionalProperties, description, label, resourceUse |
| SupportingDefinitionProperties | rationale |
