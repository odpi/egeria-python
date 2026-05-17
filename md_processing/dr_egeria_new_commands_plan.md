# Implementation Plan: New Dr. Egeria Commands

## What's new (from compact JSON updates)

| Command | Service | Type |
|---|---|---|
| Create Perspective | Actor Manager | Create |
| Create Skill | Actor Manager | Create |
| Link Associated Skill Set | Actor Manager → CollectionManager | Link |
| Create Skill Set | Collection Manager | Create (already wired, needs verification) |
| Classify Term as Question | Glossary | Classify (new verb) |

<!-- COMMENTS: -->

---

## Step 1 — `md_processing_constants.py`

Add `"Classify"` to `ALL_VERBS`. Without this, the parser won't recognise `Classify Term as Question` as a valid command verb. No other constants need changing — `Create Skill Set` is already in `COLLECTION_SUBTYPES` from the previous session.

<!-- COMMENTS: -->
This is a bit of a new pattern for classification commands. There are three verbs for classifications - Classify, Reclassify and Declassify.
Classify has synonyms of Set, DeClassify has synonyms of Unset, and Reclassify has no synonyms. 
The verb is used to determine the action to take on the classification, and the command name is used to determine which classification to apply. T
This means that we can have multiple classify commands for different classifications, and the verb will determine whether we are setting, unsetting or changing the classification.
Not all classifications will have all three verbs. Reclassify only makes sense when there are Classification properties that might need to be changed. This is often not the case.

Classifications are applied to existing entities, so there is no need for fetch or upsert logic in the processor. The processor can assume that the referenced entity already exists and focus solely on applying the classification.
---

## Step 2 — `md_processing/v2/actor_manager.py` (two sub-tasks)

### A: `ActorManagerProcessor.apply_changes()`

The current routing heuristic (`"Role" in object_type → actor_role; else → actor_profile`) doesn't handle Perspective or Skill. Add explicit cases before the existing `"Role"` check:

- `object_type == "Perspective"` → Create: `_async_create_perspective(body)` / Update: `_async_update_perspective(guid, body)`
- `object_type == "Skill"` → Create: `_async_create_skill(body)` / Update: `_async_update_skill(guid, body)`

Both methods already exist on `self.client.actor_manager`.

<!-- COMMENTS: -->

### B: `ActorManagerLinkProcessor.apply_changes()`

Add a new `elif object_type == "Associated Skill Set":` branch before the final `else: raise`. Attribute keys come from the compact bundle `"Associated Skill Set Link Base"`:

- `actor_guid` ← `attributes["Actor Name"]["guid"]`
- `skill_set_guid` ← `attributes["SkillSet Name"]["guid"]`

Dispatch to `self.client.collection_manager._async_link_associated_skill_set / _async_detach_associated_skill_set`. The `collection_manager` attribute is lazy-loaded on `EgeriaTech` — no import changes needed.

<!-- COMMENTS: -->
Right - just to be clear, the Dr.Egeria attribute would be "Actor Name" and "SkillSet Name", but the underlying method expects an actor_guid and skill_set_guid. So the processor needs to resolve the guids from the attributes before calling the method.
---

## Step 3 — `md_processing/v2/glossary.py`

Add a new `GlossaryClassifyProcessor` class. The command has `bundle: "Request Base"` and `custom_attributes: ["Term Name"]`, so the parsed attributes will contain `"Term Name"` with a resolved GUID.

Logic:
1. Fetch `term_guid` from `attributes["Term Name"]["guid"]`
2. Build a minimal `ClassificationRequestBody` dict
3. `await self.client._async_set_term_as_question(term_guid, body)`

No `fetch_element` / upsert logic needed — this is a pure classification action on an existing term.

<!-- COMMENTS: -->
we may add more commands to classify both glossaries and terms in the future, so it makes sense to have a dedicated processor for glossary classifications. This keeps the logic separate and allows us to easily add more classification commands later without cluttering the existing processors.
---

## Step 4 — `md_processing/v2/__init__.py`

Export `GlossaryClassifyProcessor` from the glossary module.

<!-- COMMENTS: -->

---

## Step 5 — `md_processing/dr_egeria.py`

Two small edits:

1. Add `GlossaryClassifyProcessor` to the import from `md_processing.v2`
2. In `setup_dispatcher()`, inside the Glossary section, add:
   ```python
   reg("Classify Term as Question", GlossaryClassifyProcessor)
   ```

No changes to `register_actor_manager_processors` — it already picks up all Actor Manager commands (including the three new ones) because the compact loader inherits `"family": "Actor Manager"` from the file-level field when individual commands have `family: ""`.

<!-- COMMENTS: -->

---

## What does NOT need changing

- `collection_manager_processor.py` — `Create Skill Set` is already wired to `_async_create_skill_set_collection` from the previous session
- `register_actor_manager_processors` in `dr_egeria.py` — spec-driven loop already covers all Actor Manager commands

<!-- COMMENTS: -->

---

## Risk / Open Question

`Link Associated Skill Set` calls `collection_manager._async_link_associated_skill_set` which takes an `actor_guid` at end 1. We just changed the test to use `ActorRole` for this — but in Dr. Egeria, the user will reference whatever actor they already created. The command will work as long as the referenced actor's Egeria entity type is acceptable to the `AssociatedSkillSet` relationship (the same type-mismatch concern from the bug fix above). Worth noting in the implementation as a caveat in the docstring.

<!-- COMMENTS: -->
