"""
Standard Glossary and Term Processors for Dr.Egeria v2.
"""
from typing import Dict, Any, Optional, List
from loguru import logger

from pyegeria import EgeriaTech, PyegeriaException
from md_processing.v2.processors import AsyncBaseCommandProcessor
from md_processing.md_processing_utils.md_processing_constants import (
    get_command_spec, APPLY_CLASSIFICATION_VERBS, REMOVE_CLASSIFICATION_VERBS,
    UPDATE_CLASSIFICATION_VERBS,
)
from md_processing.md_processing_utils.common_md_utils import (
    set_element_prop_body, set_create_body, set_update_body,
    set_object_classifications, update_element_dictionary,
    async_add_note_in_dr_e
)

class GlossaryProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Glossary collections (Glossary, Taxonomy, CanonicalVocabulary).
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_glossary_by_guid(guid)
        except PyegeriaException:
            return None


    async def apply_changes(self) -> str:
        verb = self.command.verb
        object_type = getattr(self, 'canonical_object_type', self.command.object_type)
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        
        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # 1. Prepare properties
        prop_body = set_element_prop_body(om_type or "Glossary", qualified_name, attributes)
        prop_body["language"] = attributes.get('Language', {}).get('value', None)
        prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
        
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        if verb == "Update":
            guid = self.parsed_output.get("guid")
            if not guid and self.as_is_element:
                guid = self.as_is_element['elementHeader']['guid']
                
            if not guid:
                logger.error(f"Cannot update {display_name}: GUID not found")
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "Glossary", attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            await self.client._async_update_collection(guid, body)
            self.parsed_output["guid"] = guid

            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))
                
            logger.success(f"Updated {object_type} '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = set_create_body(om_type or object_type, attributes)
            body["initialClassifications"] = set_object_classifications(
                object_type, attributes, ["Taxonomy", "CanonicalVocabulary"]
            )
            
            # Type-specific classification logic
            if object_type == "Taxonomy":
                if 'Taxonomy' in body["initialClassifications"]:
                    body["initialClassifications"]['Taxonomy']['organizingPrinciple'] = attributes.get('Organizing Principle', {}).get('value', None)
            elif object_type == "CanonicalVocabulary":
                if 'CanonicalVocabulary' in body["initialClassifications"]:
                    body["initialClassifications"]['CanonicalVocabulary']['usage'] = attributes.get('Usage', {}).get('value', None)

            body["properties"] = prop_body
            
            raw_guid = await self.client._async_create_collection(body=body)
            guid = self.extract_guid_or_raise(raw_guid, f"Create {object_type}")
            if guid:
                self.parsed_output["guid"] = guid

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created {object_type} '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)
            
        return self.command.raw_block

class TermProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Glossary Terms.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_term_by_guid(guid)
        except PyegeriaException:
            return None


    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get('Display Name', {}).get('value', qualified_name)
        status = attributes.get('Status', {}).get('value', None)
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        journal_entry = attributes.get('Journal Entry', {}).get('value')

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE")

        # 1. Properties
        prop_body = set_element_prop_body(om_type or "GlossaryTerm", qualified_name, attributes)
        prop_body["aliases"] = attributes.get('Aliases', {}).get('value', None)
        prop_body["summary"] = attributes.get('Summary', {}).get('value', None)
        prop_body["examples"] = attributes.get('Examples', {}).get('value', None)
        prop_body["abbreviation"] = attributes.get('Abbreviation', {}).get('value', None)
        prop_body["usage"] = attributes.get('Usage', {}).get('value', None)
        prop_body["user_defined_status"] = attributes.get('UserDefinedStatus', {}).get('value', None)
        prop_body["contextDescription"] = attributes.get('Context Description', {}).get('value', None)
        prop_body["contextScope"] = attributes.get('Context Scope', {}).get('value', None)
        prop_body["isAbstractConcept"] = attributes.get('Is Abstract Concept', {}).get('value', False)
        prop_body["isActivityDescription"] = attributes.get('Is Activity Description', {}).get('value', False)
        prop_body["isContext"] = attributes.get('Is Context', {}).get('value', False)
        prop_body["isDataValue"] = attributes.get('Is Data Value', {}).get('value', False)
        prop_body["termActivityType"] = attributes.get('Term Activity Type', {}).get('value', None)
        
        # 2. Extract collection GUIDs
        # We may have one or more collections listed (Glossary Name, Folders)
        glossary_guids = attributes.get("Glossary Name", {}).get("guid_list", [])
        if not glossary_guids and attributes.get("Glossary Name", {}).get("guid"):
            glossary_guids = [attributes["Glossary Name"]["guid"]]
            
        folder_guids = attributes.get("Folders", {}).get("guid_list", [])
        if not folder_guids and attributes.get("Folders", {}).get("guid"):
            folder_guids = [attributes["Folders"]["guid"]]
            
        to_be_collection_guids = list(set(glossary_guids) | set(folder_guids))
        to_be_collection_guids = [g for g in to_be_collection_guids if g]

        if verb == "Update":
            guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if self.as_is_element else None)
            if not guid:
                return self.command.raw_block

            self.last_body = body = set_update_body(om_type or "GlossaryTerm", attributes)
            body['properties'] = self.filter_update_properties(prop_body, body.get('mergeUpdate', True))
            
            await self.client._async_update_glossary_term(guid, body)
            self.parsed_output["guid"] = guid
            if status:
                await self.client._async_update_glossary_term_status(guid, status)

            # Sync memberships: if merge_update is True, we only add (replace_all=False)
            # If merge_update is False, we synchronize (replace_all=True)
            await self._sync_term_memberships(guid, to_be_collection_guids, not merge_update)
            await self._sync_term_naming_classifications(guid, attributes)
            
            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))
            
            logger.success(f"Updated Term '{display_name}' with GUID {guid}")
            update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
            return await self.render_result_markdown(guid)

        elif verb == "Create":
            self.last_body = body = set_create_body(om_type or "GlossaryTerm", attributes)
            body["properties"] = prop_body
            
            # Anchor Scope check
            anchor_scope_guid = attributes.get("Anchor Scope", {}).get('guid', None)
            if anchor_scope_guid is None and glossary_guids:
                body["anchorScopeGUID"] = glossary_guids[0] # Use first glossary as anchor if not specified

            raw_guid = await self.client._async_create_glossary_term(body=body)
            guid = self.extract_guid_or_raise(raw_guid, "Create Glossary Term")
            if guid:
                self.parsed_output["guid"] = guid
                # For Create, we always want to ensure it's in all listed collections.
                # known_new=True: this GUID was just created, so it cannot have any
                # existing CollectionMembership relationships -- skip the as-is fetch.
                await self._sync_term_memberships(guid, to_be_collection_guids, replace_all=True, known_new=True)
                await self._sync_term_naming_classifications(guid, attributes)

                if journal_entry:
                    try:
                        j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                        if j_guid:
                            self.add_related_result("Journal Entry", j_guid)
                    except Exception as e:
                        self.add_related_result("Journal Entry", status="failure", message=str(e))

                update_element_dictionary(qualified_name, {'guid': guid, 'display_name': display_name})
                logger.success(f"Created Term '{display_name}' with GUID {guid}")
                return await self.render_result_markdown(guid)

        return self.command.raw_block

    async def _sync_term_memberships(self, term_guid: str, to_be_guids: List[str], replace_all: bool,
                                      known_new: bool = False):
        """
        Standardized helper for term collection sync.

        known_new=True (pass this for a just-created term) skips the
        "what does this element currently have" relationship fetch entirely
        -- a brand-new term cannot have any existing CollectionMembership
        relationships, so there is nothing to fetch. Otherwise the fetch is
        made lazily (only actually issued if sync_members determines it's
        needed -- e.g. not when replace_all=False with an empty to_be_guids)
        via _async_get_related_elements against the classification-explorer
        by-relationship/CollectionMembership endpoint, which is the single
        most expensive call in this whole sync path on a loaded server.
        """
        guid_to_name: Dict[str, str] = {}

        if known_new:
            as_is_source: set = set()
        else:
            async def fetch_as_is() -> set:
                current_collections = await self.client._async_get_related_elements(
                    term_guid, relationship_type="CollectionMembership", start_at_end=2
                )
                if not current_collections or isinstance(current_collections, str):
                    return set()
                for c in current_collections:
                    g = c['elementHeader']['guid']
                    name = c.get('properties', {}).get('displayName') or c.get('properties', {}).get('qualifiedName') or g
                    guid_to_name[g] = name
                return {c['elementHeader']['guid'] for c in current_collections}

            as_is_source = fetch_as_is

        to_be_set = set(to_be_guids)

        async def add_fn(collection_guid):
            await self.client._async_add_to_collection(collection_guid, term_guid)

        async def remove_fn(collection_guid):
            body = {
                "class": "DeleteRelationshipRequestBody",
                "forLineage": False,
                "forDuplicateProcessing": False
            }
            await self.client._async_remove_from_collection(collection_guid, term_guid, body=body)

        sync_res = await self.sync_members(as_is_source, to_be_set, add_fn, remove_fn, replace_all)
        
        if sync_res.get("added") or sync_res.get("removed"):
            added_names = []
            for g in sync_res["added"]:
                # Try to find name in input attributes if it matched a guid
                added_names.append(g) # For now just GUID
                
            removed_names = [guid_to_name.get(g, g) for g in sync_res["removed"]]
            
            msg = f"Sync: Added {len(sync_res['added'])} collection(s), Removed {len(sync_res['removed'])} collection(s)."
            if sync_res["added"]:
                msg += f" Added: {', '.join(sync_res['added'])}"
            if sync_res["removed"]:
                msg += f" Removed: {', '.join(removed_names)}"
                
            self.add_related_result("Collection Memberships Sync", message=msg)
            
        if sync_res.get("errors"):
            self.add_related_result("Collection Memberships Sync", status="failure", message="; ".join(sync_res["errors"]))

    async def analyze_relationships(self) -> List[Dict[str, Any]]:
        results = []
        if self.command.verb not in ["Create", "Update"]:
            return results
            
        attributes = self.parsed_output.get("attributes", {})
        
        glossary_guids = attributes.get("Glossary Name", {}).get("guid_list", [])
        if not glossary_guids and attributes.get("Glossary Name", {}).get("guid"):
            glossary_guids = [attributes["Glossary Name"]["guid"]]
            
        folder_guids = attributes.get("Folders", {}).get("guid_list", [])
        if not folder_guids and attributes.get("Folders", {}).get("guid"):
            folder_guids = [attributes["Folders"]["guid"]]
            
        to_be_guids = list(set(glossary_guids) | set(folder_guids))
        to_be_guids = [g for g in to_be_guids if g]
        
        merge_update = attributes.get('Merge Update', {}).get('value', True)
        if self.command.verb == "Create":
            merge_update = False
            
        guid = self.parsed_output.get("guid") or (self.as_is_element['elementHeader']['guid'] if getattr(self, 'as_is_element', None) else None)

        as_is_guids = set()
        guid_to_name = {}
        to_be_set = set(to_be_guids)
        replace_all = not merge_update

        # Same expensive CollectionMembership relationship query as
        # _sync_term_memberships -- this is the dry-run preview path, so
        # skip it under the identical condition: add-only (replace_all=False)
        # with nothing to add means the result can't change regardless of
        # current state.
        if guid and not guid.startswith("(Planned:") and (replace_all or to_be_set):
            try:
                current_collections = await self.client._async_get_related_elements(
                    guid, relationship_type="CollectionMembership", start_at_end=2
                )
                if current_collections and not isinstance(current_collections, str):
                    for c in current_collections:
                        c_guid = c['elementHeader']['guid']
                        as_is_guids.add(c_guid)
                        name = c.get('properties', {}).get('displayName') or c.get('properties', {}).get('qualifiedName') or c_guid
                        guid_to_name[c_guid] = name
            except Exception:
                pass

        to_add_guids = to_be_set - as_is_guids
        to_remove_guids = (as_is_guids - to_be_set) if replace_all else set()
        unchanged_guids = as_is_guids.intersection(to_be_set)
        
        if to_be_set or as_is_guids:
            results.append({
                "type": "Collection Folder & Glossary Memberships",
                "added": list(to_add_guids),
                "removed": [guid_to_name.get(g, g) for g in to_remove_guids],
                "unchanged": [guid_to_name.get(g, g) for g in unchanged_guids]
            })
            
        return results

class GlossaryClassifyProcessor(AsyncBaseCommandProcessor):
    """
    Processor for classification commands on glossary entities (Glossary, GlossaryTerm).

    Handles the Classify / Set, Declassify / Unset, and Reclassify verb families.
    Classifications always act on an already-existing entity — no fetch/upsert logic.

    Supported commands (extend by adding entries to the dispatch table below):
      - Classify Term as Question  /  Declassify Term as Question
      - Classify Term as Element Supplement  /  Declassify Term as Element Supplement
    """

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        command_name = f"{verb} {self.command.object_type}"
        attributes = self.parsed_output.get("attributes", {})

        # --- dispatch table: command noun → (apply_coro, remove_coro, properties "class" name) ---
        # Each coro accepts (guid, body). Add new classification commands here.
        dispatch = {
            "Term as Question": (
                self.client._async_set_term_as_question,
                self.client._async_clear_term_as_question,
                "QuestionProperties",
            ),
            "Term as Element Supplement": (
                self.client._async_set_term_as_element_supplement,
                self.client._async_clear_term_as_element_supplement,
                "ElementSupplementProperties",
            ),
        }

        # Identify which classification this command targets
        noun = self.command.object_type  # e.g. "Term as Question"
        if noun not in dispatch:
            raise PyegeriaException(f"GlossaryClassifyProcessor: unsupported command '{command_name}'")

        apply_coro, remove_coro, props_class = dispatch[noun]

        # Resolve entity GUID — "Term Name" for term classifications
        term_name_attr = attributes.get("Term Name", {})
        entity_guid = term_name_attr.get("guid")
        entity_label = term_name_attr.get("qualified_name") or term_name_attr.get("value") or noun

        if not entity_guid:
            logger.error(f"GlossaryClassifyProcessor: no GUID resolved for '{entity_label}' in '{command_name}'")
            return self.command.raw_block

        # NOTE: "class" must match what each pyegeria method's own request-body
        # validator expects -- NewClassificationRequestBody for set, DeleteClassificationRequestBody
        # for clear. A single shared "ClassificationRequestBody" body (the previous
        # bug here) matches neither: pydantic's Literal check on "class" rejects it
        # before any HTTP call is made, surfacing as "Request body failed validation".
        apply_body = {
            "class": "NewClassificationRequestBody",
            "properties": {"class": props_class},
            "forLineage": False,
            "forDuplicateProcessing": False,
        }
        remove_body = {
            "class": "DeleteClassificationRequestBody",
            "forLineage": False,
            "forDuplicateProcessing": False,
        }

        if verb in APPLY_CLASSIFICATION_VERBS:
            await apply_coro(entity_guid, apply_body)
            logger.success(f"Classified '{entity_label}' via '{command_name}'")
        elif verb in REMOVE_CLASSIFICATION_VERBS:
            await remove_coro(entity_guid, remove_body)
            logger.success(f"Removed classification '{noun}' from '{entity_label}'")
        elif verb in UPDATE_CLASSIFICATION_VERBS:
            # Reclassify: remove then re-apply (default; override per noun if needed)
            await remove_coro(entity_guid, remove_body)
            await apply_coro(entity_guid, apply_body)
            logger.success(f"Reclassified '{entity_label}' via '{command_name}'")
        else:
            raise PyegeriaException(f"GlossaryClassifyProcessor: unrecognised verb '{verb}'")

        return await self.render_result_markdown(entity_guid)


class QuestionProcessor(AsyncBaseCommandProcessor):
    """
    Processor for the 'Create Question' command.

    Creates a GlossaryTerm classified with Question in a single API call,
    using initialClassifications in the request body — no separate classify step.
    """

    async def fetch_element(self, guid: str) -> Optional[Dict[str, Any]]:
        try:
            return await self.client._async_get_term_by_guid(guid)
        except PyegeriaException:
            return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        if verb != "Create":
            return self.command.raw_block

        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output["qualified_name"]
        display_name = attributes.get("Display Name", {}).get("value", qualified_name)
        description = attributes.get("Description", {}).get("value")
        journal_entry = attributes.get("Journal Entry", {}).get("value")

        spec = self.get_command_spec()
        om_type = spec.get("OM_TYPE", "GlossaryTerm")

        prop_body = set_element_prop_body(om_type, qualified_name, attributes)
        body = set_create_body(om_type, attributes)
        body["properties"] = prop_body
        body["initialClassifications"] = {"Question": {"class": "QuestionProperties"}}

        raw_guid = await self.client._async_create_question(body=body)
        guid = self.extract_guid_or_raise(raw_guid, "Create Question")

        if guid:
            self.parsed_output["guid"] = guid
            await self._sync_term_naming_classifications(guid, attributes)

            if journal_entry:
                try:
                    j_guid = await async_add_note_in_dr_e(self.client, qualified_name, display_name, journal_entry)
                    if j_guid:
                        self.add_related_result("Journal Entry", j_guid)
                except Exception as e:
                    self.add_related_result("Journal Entry", status="failure", message=str(e))

            update_element_dictionary(qualified_name, {"guid": guid, "display_name": display_name})
            logger.success(f"Created Question '{display_name}' with GUID {guid}")
            return await self.render_result_markdown(guid)

        return self.command.raw_block


class TermRelationshipProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Term-to-Term relationships (Link, Attach, Add).
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec("Link Term-Term Relationship")

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        # Relationship lookup is more complex; for now we return None to force creation
        return None

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        term1_guid = attributes.get('Term 1', {}).get('guid', None)
        term1_qname = attributes.get('Term 1', {}).get('qualified_name', None)
        term2_guid = attributes.get('Term 2', {}).get('guid', None)
        term2_qname = attributes.get('Term 2', {}).get('qualified_name', None)
        
        relationship = attributes.get('Relationship Type', {}).get('value', None)
        if not relationship:
            # Fallback for old templates
            relationship = attributes.get('Relationship', {}).get('value', None)

        # Standardize common relationship names
        rel_mapping = {
            "ISA": "ISARelationship",
            "IS A": "ISARelationship",
            "HASA": "TermHASARelationship",
            "HAS A": "TermHASARelationship",
            "TYPED BY": "TermTYPEDBYRelationship",
            "TYPE OF": "TermISATYPEOFRelationship",
        }
        if relationship and relationship.upper() in rel_mapping:
            relationship = rel_mapping[relationship.upper()]
        
        if not (term1_guid and term2_guid and relationship):
            msg = f"TermRelationshipProcessor: Missing required identifiers (Term 1 GUID: {bool(term1_guid)}, Term 2 GUID: {bool(term2_guid)}, Relationship: {bool(relationship)})"
            logger.error(msg)
            self.parsed_output['valid'] = False
            self.parsed_output['reason'] = msg
            return self.command.raw_block
            
        logger.info(f"TermRelationshipProcessor: Linking '{term1_qname}' to '{term2_qname}' via '{relationship}'")
        
        try:
            if self.command.verb in ["Unlink", "Detach", "Remove"]:
                await self.client._async_remove_relationship_between_terms(term1_guid, term2_guid, relationship)
                logger.success(f"Unlinked terms via {relationship}")
            else:
                await self.client._async_add_relationship_between_terms(term1_guid, term2_guid, relationship)
                logger.success(f"Linked terms via {relationship}")
            
            # Standard v2 relationship output
            return (f"\n\n## {self.command.verb} Term-Term Relationship\n\n"
                    f"### Term 1 Name:\n\n{term1_qname}\n\n"
                    f"### Term 2 Name:\n\n{term2_qname}\n\n"
                    f"### Term Relationship:\n\n{relationship}")
        except PyegeriaException as e:
            logger.error(f"Failed to link terms: {e}")
            self.parsed_output['valid'] = False
            self.parsed_output['reason'] = str(e)
            return self.command.raw_block


class TermAsContextProcessor(AsyncBaseCommandProcessor):
    """
    Processor for Link/Detach Term as Context commands (UsedInContext
    relationship between a GlossaryTerm and the Referenceable it provides
    usage context for). Was defined in the compact spec but had no
    processor at all -- registered here now that GlossaryManager has
    _async_link_used_in_context/_async_detach_used_in_context
    (added 2026-08-21, verified against a live 6.2-SNAPSHOT server).
    """

    def get_command_spec(self) -> Dict[str, Any]:
        return get_command_spec(f"{self.command.verb} Term as Context")

    def supports_target_element_lookup(self) -> bool:
        # Relationship-only processor -- see GovernanceLinkProcessor's
        # identical override (md_processing/v2/governance.py) for why this
        # matters: without it, AsyncBaseCommandProcessor.execute()'s
        # Create<->Update upsert-transition logic can silently rewrite the
        # verb (ISSUE-68 follow-up).
        return False

    async def fetch_as_is(self) -> Optional[Dict[str, Any]]:
        return None

    async def apply_changes(self) -> str:
        verb = self.command.verb
        attributes = self.parsed_output["attributes"]
        term_guid = attributes.get('Term 1', {}).get('guid')
        element_guid = attributes.get('Element Id', {}).get('guid')
        if not (term_guid and element_guid):
            missing = []
            if not term_guid: missing.append("'Term 1'")
            if not element_guid: missing.append("'Element Id'")
            raise ValueError(f"Cannot {verb.lower()} Term as Context: resolution failed for {', '.join(missing)}")

        if verb in ["Link", "Attach", "Add"]:
            props = {"class": "UsedInContextProperties"}
            for attr_name, prop_name in {
                "Description": "description", "Expression": "expression", "Confidence": "confidence",
                "Steward": "steward", "Source": "source", "Term Relationship Status": "termRelationshipStatus",
            }.items():
                val = attributes.get(attr_name, {}).get('value')
                if val is not None:
                    props[prop_name] = val
            body = {"class": "NewRelationshipRequestBody", "properties": props}
            await self.client.glossary_manager._async_link_used_in_context(term_guid, element_guid, body)
            logger.success(f"Linked Term {term_guid} as context for {element_guid}")
            return f"\n\n## {verb} Term as Context\n\nLinked term {term_guid} as context for {element_guid}"

        elif verb in ["Detach", "Unlink", "Remove"]:
            await self.client.glossary_manager._async_detach_used_in_context(term_guid, element_guid)
            logger.success(f"Detached UsedInContext between {term_guid} and {element_guid}")
            return f"\n\n## {verb} Term as Context\n\nDetached the UsedInContext relationship between {term_guid} and {element_guid}"

        return self.command.raw_block
