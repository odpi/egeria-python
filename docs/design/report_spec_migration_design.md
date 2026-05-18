# Design: Migrating Report Specs to Egeria

**Status:** Design decisions captured — ready for Phase 1 planning  
**Date:** 2026-05-17  
**Context:** `pyegeria/view/base_report_formats.py` currently holds all report specs (FormatSet objects)
as Python/JSON. Goal is to make Egeria the source of truth for the metadata portions — starting with
`question_spec` — while keeping file-based specs for formats and action wiring.

---

## 1. Current Architecture Summary

A `FormatSet` has five logical parts:

| Part | Description | Migration destination |
|------|-------------|----------------------|
| `target_type` | Egeria open metadata type being reported on (e.g. "Glossary") | `additional_properties` on ReportType (Phase 1) |
| `family` | Product area grouping (e.g. "Actor Manager") | CollectionFolder hierarchy, tags, or classification — flexible |
| `formats` | Column lists per view type (LIST / ALL / TABLE) | **File — deferred to Phase 2** |
| `action` | Which API function to call + params | **File — deferred to Phase 2** |
| `question_spec` | Perspective → question mappings | **Egeria — Phase 1 target** |

The registry is currently assembled from four layers at startup:
`base_report_specs` (hand-authored) → `generated_format_sets` (refresh_specs) → `_CONFIG_REPORT_FORMATS` (env var JSON) → `_RUNTIME_REPORT_FORMATS`

---

## 2. Egeria Mapping — Decided

### Core entity mapping

```
FormatSet           →  ReportType         (Collection subtype)
question_spec entry →  QuestionSpec       (new Collection subtype — see §2.1)
perspective string  →  Perspective        (Actor Manager entity)
question string     →  GlossaryTerm       (with IsQuestion classification)
```

### 2.1  QuestionSpec — CollectionFolder with reserved qualified name prefix

A single entry in the current `question_spec` list maps to a **CollectionFolder** whose
`qualified_name` starts with `QuestionSpec::`. No new OM type is introduced in Phase 1.
This lets us experiment with the structure and add a proper subtype in Phase 2 once the
shape is confirmed.

```
ReportType
  └─ CollectionMembership → CollectionFolder  (QN: QuestionSpec::Glossary-DrE-Basic::1)
       └─ CollectionMembership → Question 1
       └─ CollectionMembership → Question 2
  └─ CollectionMembership → CollectionFolder  (QN: QuestionSpec::Glossary-DrE-Basic::2)
       └─ CollectionMembership → Question 3
```

Perspectives are linked to Questions directly (many-to-many), not to the QuestionSpec folder.
The `membershipType` on CollectionMembership provides additional semantics on each link.

### Relationship mapping

```
ReportType → QuestionSpec          CollectionMembership
QuestionSpec → Question            CollectionMembership (membershipType carries semantics)
Question ↔ Perspective             ScopedBy  (both ends are Referenceable — confirmed valid)
ReportType grouped by family       CollectionFolder hierarchy, tags, or other — flexible
```

**On ScopedBy:** `ScopedBy` is Referenceable-to-Referenceable and is confirmed valid for
Question ↔ Perspective. Whether a more semantically precise relationship is warranted (given
that a Perspective is a viewpoint of an Actor, not a generic scope) is left as a future
consideration. For Phase 1, `ScopedBy` is used.

### Qualified name convention

```
ReportType         ::  ReportSpec::<label>          e.g.  ReportSpec::Glossary-DrE-Basic
QuestionSpec folder::  QuestionSpec::<report>::<n>  e.g.  QuestionSpec::Glossary-DrE-Basic::1
Perspective        ::  Perspective::<name>          e.g.  Perspective::Business Analyst
Question           ::  Question::<text-slug>        e.g.  Question::What-is-the-purpose
```

---

## 3. Resolved Questions

### 3.1  ScopedBy for Question ↔ Perspective — ✅ Use ScopedBy

`ScopedBy` is Referenceable-to-Referenceable, so it can link a Question to a Perspective.
This is confirmed valid for Phase 1. Whether a purpose-built relationship type is cleaner
semantically can be revisited in Phase 2.

### 3.2  Question ordering — ✅ Not required

`CollectionMembership` has no position attribute. Question ordering within a spec is not
considered important for the AI/report-discovery use case. `membershipType` on the
CollectionMembership relationship will be used to carry additional semantics instead.

### 3.3  Many-to-many perspectives on one question — ✅ Supported naturally

A question with multiple ScopedBy relationships to different Perspectives is straightforward.
Discovery in the reverse direction (given a Perspective, find Questions) is supported by
Egeria's graph traversal with configurable depth, relationship type filters, and related-element
expansion on the Perspective find methods.

### 3.4  Which glossary holds Questions — ✅ Glossary not required

GlossaryTerms with IsQuestion do not need to live in a specific glossary. They can be queried
directly by classification. No glossary constraint is imposed.

`Create Question` will be a **combined command** that creates the GlossaryTerm and applies
IsQuestion in a single API call using the initial-classifications parameter of
`newElementRequestBody`. No two-step create-then-classify needed.

### 3.5  Label collision during transition — ✅ File wins; Egeria provides question_spec only

Collision between an Egeria-sourced spec and a file-based spec generates a **warning** but
does not error. Priority (highest to lowest):

```
user files  →  generated  →  built-ins  →  Egeria
```

This works because Phase 1 removes `question_spec` from file-based FormatSets entirely.
The file provides `formats` and `action`; Egeria provides `question_spec`. The loader
merges them at startup by label — no collision, no duplication.

### 3.6  `target_type` storage on ReportType — ✅ `additional_properties`

Store `target_type` in `additional_properties` on the ReportType for Phase 1.
A formal custom attribute can be introduced later if needed.

---

## 4. Design Decisions

### 4.1  Clean join: file holds formats/action, Egeria holds question_spec

`question_spec` will be **removed from file-based FormatSets** as those FormatSets are
migrated. The startup loader (`load_egeria_report_specs`) pulls question_specs from Egeria
and merges them into the corresponding file-based FormatSet by label. The file-based spec
without question_spec is complete — it just has no questions until Egeria provides them.

This eliminates the risk of out-of-sync specs and makes the ownership boundary unambiguous.

### 4.2  Bootstrap strategy

`refresh_specs` does **not** currently generate question_specs. It generates DrE-Basic format
entries from compact command JSONs. The question_spec content will be authored separately:

- **Initially:** ReportTypes and their QuestionSpecs/Questions/Perspectives are created manually
  in Egeria via Dr.Egeria markdown commands.
- **Later:** A `refresh_specs --push` mode (or equivalent CLI command) auto-generates
  ReportType entities in Egeria from the file-based specs, bootstrapping the catalog.
- **Eventually:** A `Create Report Type` Dr.Egeria command makes the process fully declarative.

### 4.3  Offline resilience — N/A

If Egeria is unreachable, the report cannot be executed regardless. A graceful fallback to
file-based question_specs is not required. The loader simply skips the Egeria merge step
and the FormatSet is loaded without a question_spec.

### 4.4  Caching and Discovery

Egeria specs are loaded once at startup via `load_egeria_report_specs(client)`. This function
queries all ReportTypes, reconstructs the `question_spec` portion of each FormatSet, and merges
into the registry. No per-request Egeria queries.

**Discovering QuestionSpec folders:** Use `find_collections` with:
```python
metadata_element_type = "CollectionFolder"
starts_with = True
search_string = "QuestionSpec"
```
This finds all CollectionFolders whose qualified name starts with `QuestionSpec::` without
needing a new OM type. The loader traverses each folder's members to reconstruct the
perspective-question grouping.

### 4.5  Question reuse — ✅ Shared, not owned

Questions are shared GlossaryTerms. A single Question entity can be a member of many
QuestionSpecs across many ReportTypes. This is the desired behavior — editing a question
propagates everywhere. Where a variant question is needed, a Synonym relationship on the
GlossaryTerm can express the variation without creating a duplicate.

---

## 5. Patterns

### 5.1  Collection hierarchy for family grouping

```
Root Collection: "Report Specifications"
  └─ CollectionFolder: "Actor Manager"
       └─ ReportType: "Perspectives"
       └─ ReportType: "Skills"
  └─ CollectionFolder: "Glossary"
       └─ ReportType: "Glossary Terms"
```

Multiple grouping mechanisms are available (collection hierarchies, tags, search keywords).
The folder approach is the most browsable and aligns with the existing `family` concept.
May also want folder collections organized by Perspective to enable perspective-first browsing.

### 5.2  Shared question library with perspective folders

Questions live in a shared pool (no mandatory glossary). Optional organization:
- A `CollectionFolder` per Perspective groups the questions that belong to that perspective
- A `CollectionFolder` per domain groups questions by subject area

This enables both "find all questions for a perspective" and "find all report types that ask
about data quality" without changing the core relationship model.

### 5.3  Dr.Egeria commands for authoring

New commands to support Phase 1:

```markdown
## Create Question             # creates GlossaryTerm + IsQuestion in one call
## Create Report Type          # creates ReportType collection
## Create Question Spec        # creates CollectionFolder with QuestionSpec:: prefix, member of a ReportType
## Link Question to Spec       # CollectionMembership: QuestionSpec folder → Question
## Link Perspective to Question # ScopedBy: Question ↔ Perspective
```

A full report spec can then be expressed as a single Dr.Egeria markdown file:
declarative, version-controllable, and processable through the existing pipeline.

---

## 6. Phase 1 Scope

### What we build

1. **`Create Question` command** in Dr.Egeria — creates GlossaryTerm with IsQuestion in one call
2. **`Create Report Type` command** in Dr.Egeria — creates ReportType collection
3. **`Create Question Spec` command** in Dr.Egeria — creates a CollectionFolder (QN prefix `QuestionSpec::`) as a member of a ReportType
4. **`Link Question to Spec` command** in Dr.Egeria — CollectionMembership: QuestionSpec → Question
5. **`Link Perspective to Question` command** in Dr.Egeria — ScopedBy: Question ↔ Perspective
6. **`load_egeria_report_specs(client)`** — startup function that pulls ReportTypes + QuestionSpecs
   from Egeria and merges question_spec into the corresponding file-based FormatSets by label
7. **`QuestionSpec` loader recognition** — loader identifies QuestionSpec folders by `QuestionSpec::` qualified name prefix; no new subtype in Phase 1

### What we defer to Phase 2

- Migrating `formats` (column lists per view type) to Egeria
- Migrating `action` (API function wiring) to Egeria
- Migrating `target_type` and `family` beyond additional_properties
- `refresh_specs --push` bootstrap command
- Full deprecation of file-based generated specs

### Open item before Phase 1 starts

None — all blocking decisions are resolved. Phase 1 can begin.

---

## 7. Migration Plan — Moving question_specs from base_report_formats.py to Egeria

### 7.1  What needs to be migrated

Every `FormatSet` in `base_report_formats.py` that has a non-empty `question_spec` list.
Each `question_spec` entry is a dict `{'perspectives': [...], 'questions': [...]}`.

Approximate scale:
- ~30+ hand-authored FormatSets in `base_report_specs` with question_specs
- Most `generated_format_sets` (DrE-Basic entries) also have question_specs

### 7.2  Migration steps per FormatSet

For each FormatSet with a `question_spec`:

1. **Create or find the ReportType** in Egeria (QN: `ReportSpec::<label>`)
2. For each entry `{'perspectives': [...], 'questions': [...]}` in the `question_spec` list:
   - **Create a QuestionSpec folder** (CollectionFolder, QN: `QuestionSpec::<label>::<n>`)
   - **Link the folder to the ReportType** via CollectionMembership
   - For each question string:
     - **Find or create a GlossaryTerm** with the question text as display name, with IsQuestion classification; QN: `Question::<slug>`
     - **Link the Question to the QuestionSpec folder** via CollectionMembership
   - For each perspective name:
     - **Find or create a Perspective** entity (QN: `Perspective::<name>`)
     - For each Question in this entry:
       - **Link Question to Perspective** via ScopedBy
3. **Remove `question_spec`** from the file-based FormatSet entry
4. **Verify** by calling `load_egeria_report_specs` and checking the merged FormatSet

### 7.3  Migration approach — decided

**Initial bulk load — migration script**

A Python script reads `base_report_specs` and `generated_format_sets` from
`base_report_formats.py`, iterates each FormatSet, and pushes the question_spec structure
to Egeria using pyegeria API calls. Questions and Perspectives are deduplicated by
qualified name (find-or-create pattern). Run once against each environment.

```
python tools/migrate_question_specs.py --server <url> --user <user>
```

**Ongoing updates — Dr.Egeria commands**

After the initial migration, all additions and edits to report specs, question specs,
questions, and perspective links are authored as Dr.Egeria markdown files using the
commands defined in §5.3. The migration script is a one-time bootstrap; Dr.Egeria is
the ongoing authoring surface.

`refresh_specs --push` (Phase 2) may later automate generation of ReportType/QuestionSpec
entries from compact command JSONs, complementing Dr.Egeria for the generated_format_sets family.

### 7.4  Deduplication rules

- **Questions:** matched by qualified name `Question::<slug>` where slug is the question text
  lowercased, spaces replaced with `-`, punctuation stripped. If found, the existing entity is
  reused; the ScopedBy relationship is added if not already present.
- **Perspectives:** matched by `Perspective::<name>`. If found, reused; not duplicated.
- **ReportType:** matched by `ReportSpec::<label>`. If found, additional QuestionSpec folders
  are added as members (upsert behavior).

### 7.5  Rollback / validation

- Run migration in a test/sandbox Egeria first
- After migration: `load_egeria_report_specs(client)` should produce identical question_spec
  structure to the original file-based FormatSet
- Add a `validate_question_spec_migration(label)` utility that diffs the Egeria-loaded
  question_spec against the file-based one before deletion
- Remove question_spec from files only after validation passes

### 7.6  Migration order

1. Migrate the small hand-authored `base_report_specs` first (fewer, easier to verify)
2. Migrate `generated_format_sets` (more numerous but uniform structure)
3. Remove question_specs from files as each batch is validated

---

## 8. Decisions Log

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Use CollectionFolder with `QuestionSpec::` qualified name prefix instead of a new subtype | Allows experimentation in Phase 1; proper subtype can be introduced in Phase 2 once shape is confirmed |
| D2 | Use ScopedBy for Question ↔ Perspective | Valid Referenceable-to-Referenceable relationship; revisit semantics in Phase 2 |
| D3 | Remove question_spec from file-based FormatSets as they migrate | Avoids out-of-sync risk; clear ownership boundary |
| D4 | File wins over Egeria in collision; Egeria provides question_spec only | Allows incremental migration without breaking existing file-based specs |
| D5 | Questions are shared (not owned by ReportType) | Reuse is desirable; synonyms handle variations |
| D6 | target_type in additional_properties | Pragmatic for Phase 1; formalize later |
| D7 | No glossary required for Questions | IsQuestion classification is queryable directly |
| D8 | Create Question is a combined create-and-classify call | newElementRequestBody supports initial classifications |
| D9 | No offline fallback needed | Egeria must be up to execute reports anyway |
| D10 | Migration script for initial bulk load; Dr.Egeria commands for ongoing updates | Script is a one-time bootstrap; Dr.Egeria is the authoring surface going forward |
