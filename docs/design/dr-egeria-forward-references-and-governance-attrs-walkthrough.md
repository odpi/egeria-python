# Walkthrough — Forward References, Parent Relationships, and Governance Classifications on Update

Three related gaps closed in the same pass, all following the same shape: an attribute was resolved/parsed correctly but the effect was never actually applied. See `BACKLOG.md` for the full investigation history (including two pyegeria bugs found only by live-verifying these fixes, and one apparent Egeria server-side gap that remains open for `Retention Classification`).

## 1. Forward references now resolve

Dr.Egeria previously only supported **backward** references — an element could only be referenced by a command that came *after* it in the file. `context["planned_elements"]` is populated incrementally, in file order, as each command is dispatched, so a reference to a name belonging to a *later* command was never recognized — it just failed.

`V2Dispatcher.dispatch_batch()` now runs in rounds. A pre-scan (`prescan_batch_target_qns()`) walks the whole batch once before anything executes and records every command's own target name (qualified name and display name) into `context["batch_target_qns"]`. A reference that resolves to a name in that set — but isn't creatable yet — is deferred and retried on a later round, instead of failing immediately.

### Before

```markdown
## Create Project
### Display Name
Sales Forecast Program
### Sub-Projects
Q1 Delivery

___

## Create Project
### Display Name
Q1 Delivery
```

```text
ERROR | Referenced element(s) ['Q1 Delivery'] for attribute 'Sub-Projects' not found.
```

### After — live-verified against `qs-view-server`

```text
│ Update Project   │ Update Project    │ SUCCESS │ Yes   │ FwdRefTest Parent    │ FwdRefTest Parent::1.0 │ Executed Update Project (GUID: 84b4279f-...) | Related: Sub-Projects Sync │
│ Create Project   │ Create Project    │ SUCCESS │ No    │ FwdRefTest Child     │ FwdRefTest Child::1.0  │ Executed Create Project (GUID: 44675913-...)                        │
```

Direct element fetch confirmed the real relationship:

```text
>>> await client._async_get_project_by_guid('84b4279f-...')
managedProjects: [{ relationshipHeader.type.typeName: 'ProjectHierarchy', relatedElement.properties.displayName: 'FwdRefTest Child' }]
```

`--validate` mode's message for a still-unresolved forward reference now says so plainly (`| Note: forward reference(s) not yet creatable in this preview - will resolve during --process`) instead of reporting an unqualified success, since validate mode never actually creates anything for the reference to resolve against.

A multi-level chain (grandparent → parent → child, each forward-referencing the next) required one further fix: a `context["final_round"]` guard on the existing "resolve Planned GUIDs before applying changes" gate, so a reference doesn't get declared a permanent failure one round too early while its own target is still waiting on *its* forward reference to resolve.

## 2. `Parent ID` / `Parent Relationship Type Name` now work on `Update`

`Create`'s `NewElementRequestBody` bundles "create the element" and "link it to this one named parent relationship" in a single call. There's no `Update`-time equivalent (Egeria's real `UpdateElementRequestBody` has only a `properties` field — confirmed against the Java class directly) — so these attributes were being resolved to a real GUID on `Update` and then silently discarded.

`AsyncBaseCommandProcessor._sync_parent_relationship()` closes this using `MetadataExpert`'s generic relationship calls (works for any Egeria relationship type by name, not just ones with a dedicated OMVS wrapper).

### Live verification

```markdown
## Update Project
### Display Name
ParentRelTest Child
### Qualified Name
ParentRelTest Child::1.0
### Parent ID
ParentRelTest Parent
### Parent Relationship Type Name
ProjectHierarchy
```

```text
Executed Update Project (GUID: 8a8a9e1d-...) | Related: Parent Relationship (GUID: 7f7fba22-...)
```

Direct fetch confirmed the relationship. Re-running the identical command a second time produced **no** `Related:` line at all (idempotent no-op — the sync method found the relationship already correct and returned early). Changing `Parent ID` to a different project correctly removed the old relationship and created the new one (re-parenting), confirmed via direct fetch both times.

Fixing this surfaced three pyegeria bugs along the way (all fixed, see `BACKLOG.md` for detail): a validator using the wrong `TypeAdapter`, `NewRelatedElementsRequestBody`'s field names not matching the real Java DTO, and `_async_get_all_related_elements()` returning a differently-shaped dict rather than the list the original code assumed.

### `Anchor ID` / `Anchor Scope ID` — investigated, confirmed NOT the same kind of fix

Anchoring is a **classification**, not a relationship. The obvious equivalent (`_async_reclassify_metadata_element` with an updated `anchorGUID`) succeeds at the API level but does **not** establish real anchor semantics:

```text
>>> reclassify target's Anchors -> owner_guid   # no error
>>> delete owner (cascade=True)
>>> target STILL EXISTS after owner cascade-delete: True
```

Traced into `OpenMetadataAPIAnchorHandler.java`: anchor maintenance is wired into specific entity-*creation* flows, not any generic post-creation path. Reads as intentional (anchoring governs lifecycle/security scope — reasonable to keep immutable). No code change; documented in `BACKLOG.md` as a confirmed constraint.

## 3. Governance classifications were completely unwired (Confidentiality/Confidence/Criticality/Impact fixed; Retention blocked separately)

Unlike Anchor, these classifications genuinely need to change over an element's lifetime. Found they weren't applied on **either** verb — parsed and validated by `AttributeFirstParser`, then never read by any processor.

`AsyncBaseCommandProcessor._sync_governance_classifications()` closes this for four of the five, using `ClassificationExplorer`'s dedicated `_async_set_X_classification` methods.

**A systemic pyegeria documentation bug found along the way:** both the method docstrings and the compact spec attribute descriptions document the "level" property uniformly as `levelIdentifier`. Live-confirmed this is wrong for every one of the five — using it returns **no error** but silently fails to attach the classification at all:

```text
>>> set_confidentiality_classification(guid, {properties: {class: 'ConfidentialityProperties', levelIdentifier: 2}})
no error
>>> fetch element -> Confidentiality classification present: False
```

The real field names, cross-checked against each `*Properties.java` class and confirmed live:

| Attribute | Real field |
|---|---|
| Confidentiality Classification | `confidentialityLevel` |
| Confidence Classification | `confidenceLevel` |
| Criticality Classification | `criticalityLevel` |
| Impact Classification | `severityLevel` |
| Retention Classification | `retentionBasis` |

### Live verification (Create, then change on Update)

```markdown
## Create Project
### Display Name
GovClassifTest Proj
### Confidentiality Classification
CONFIDENTIAL
### Criticality Classification
IMPORTANT
### Impact Classification
MEDIUM
```

```markdown
## Update Project
### Display Name
GovClassifTest Proj
### Qualified Name
GovClassifTest Proj::1.0
### Confidentiality Classification
RESTRICTED
### Confidence Classification
AUTHORITATIVE
### Criticality Classification
CRITICAL
### Impact Classification
HIGH
```

Direct fetch after the Update confirmed all four values changed correctly:

```text
confidentiality -> confidentialityLevel: 4   (RESTRICTED)
confidence      -> confidenceLevel: 3        (AUTHORITATIVE)
criticality     -> criticalityLevel: 3       (CRITICAL)
impact          -> severityLevel: 3          (HIGH)
```

### `Retention Classification` — separate, unresolved, apparent server-side gap

Even after fixing pyegeria's own client-side class-name mismatch (`_async_set_retention_classification`'s hardcoded allowlist expects `"RetentionClassificationProperties"`, not the real Java class's own simple name `"RetentionProperties"`), every attempt is rejected by the server:

```text
OMRS-REPOSITORY-400-028 A property called statusIdentifier has been proposed for a metadata
instance of category ClassificationDef and type Retention; it is not supported for this type
```

A wire-level body dump confirmed the actual outgoing request contains no such field — only `class` and `retentionBasis`. This looks like Egeria's own `Retention` `ClassificationDef` registration not including a property (`statusIdentifier`) that the server auto-populates for it regardless, on this server version — not fixable from pyegeria or Dr.Egeria. Left wired in since it fails as a clean, isolated per-item error (reported via `add_related_result(..., status="failure", ...)`) without blocking the command or the other four classifications.

## Verification summary

- New unit tests: `tests/micro-tests/test_dispatcher_forward_references.py` (3 tests).
- Zero regression: all 12 `dr_test_*.md` regression fixtures produce byte-for-byte identical SCORE lines before/after.
- Live-verified end-to-end against `qs-view-server` for all three fixes, with throwaway elements created and deleted for each.
