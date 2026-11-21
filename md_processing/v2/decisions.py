# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Dr.Egeria commands for Egeria 6.4 Decisions (odpi/egeria#9463, model 0018): Governance Officer family.

- Create/Update Decision -> GovernanceOfficer.create_decision / update_decision (DecisionProperties).
- Link/Detach Decision Outcome -> link_decision_outcome / detach_decision_outcome (Outcome: Decision -> element).
- Link/Update/Detach Assessment -> link_assessment / update_assessment / detach_assessment (Assessment: element ->
  Decision, MULTI-link).

**How one assessment is picked** (the Architect's ruling, DESIGN-EGERIA-6.4-ADDITIONS-BUILD-PLAN §2):
- The Assessment relationship's own GUID is the identifier, as with License and Certification. Link Assessment
  writes ``Assessment GUID`` into the processed document, so the author has it for later.
- Update and Detach take ``Assessment GUID``. Without it they take Element + Decision + Label (+ Assessment Time
  when more than one matches), read from the Decision's ``inputsToDecision`` list.
- Exactly one match proceeds. Zero, or more than one, is refused, listing each candidate's GUID, label and
  assessmentTime, so the author can paste the right GUID. Nothing is guessed.
- Times compare as UTC instants; a time with no zone is refused with words.
- Link Assessment given an Assessment GUID (a processed document run again) updates that assessment instead of
  adding another: Egeria never merges a second Assessment between the same two elements.

Every command is gated on Egeria 6.4 (md_processing.v2.egeria_6_4).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from loguru import logger

from pyegeria.core import egeria_6_4_names as e64
from pyegeria.core._globals import NO_GUID_RETURNED
from pyegeria.core.utils import body_slimmer
from md_processing.md_processing_utils.common_md_utils import (
    set_create_body, set_element_prop_body, set_update_body, update_element_dictionary)
from md_processing.v2.egeria_6_4 import (
    EMPTY, Egeria64LinkProcessor, Egeria64Processor, delete_relationship_body, guid, new_relationship_body,
    read_keys_only, stored_instant, update_relationship_body, utc_instant, value)

#: Decision-specific attributes and the DecisionProperties key each fills.
DECISION_FIELDS = {
    "Summary": "summary", "Scope": "scope", "Usage": "usage", "Importance": "importance",
    "Disposition": "disposition", "Implications": "implications", "Notes": "notes", "Start Time": "startTime",
    "Last Review Time": "lastReviewTime", "Next Review Time": "nextReviewTime", "Expiry Time": "expiryTime",
}

#: The Referenceable/Authored bundle keys set_element_prop_body fills, and their attributes (for "not applied").
ELEMENT_ATTRIBUTE_OF = {
    "displayName": "Display Name", "description": "Description", "category": "Category", "identifier": "Identifier",
    "url": "URL", "authors": "Authors", "userDefinedContentStatus": "User Defined Content Status",
    "versionIdentifier": "Version Identifier", "effectiveFrom": "Effective From", "effectiveTo": "Effective To",
    "additionalProperties": "Additional Properties", "extendedProperties": "Extended Properties",
    "supportLevel": "Support Level", "serviceLevels": "Service Levels", "legal": "Legal",
    "contentStatus": "Content Status",
}

#: Outcome-specific attributes and the OutcomeProperties key each fills.
OUTCOME_FIELDS = {"Importance": "importance", "Disposition": "disposition"}

#: Assessment-specific attributes and the AssessmentProperties key each fills.
ASSESSMENT_FIELDS = {
    "Assessor": "assessor", "Assessor Type Name": "assessorTypeName", "Assessor Property Name": "assessorPropertyName",
    "Assessment Time": "assessmentTime", "Expiry Time": "expiryTime", "Notes": "notes",
    "Additional Properties": "additionalProperties",
}


def _fields(attributes: Dict[str, Any], mapping: Dict[str, str]) -> dict:
    return {key: value(attributes, name) for name, key in mapping.items()}


class DecisionProcessor(Egeria64Processor):
    """Create Decision / Update Decision."""

    async def fetch_element(self, guid_: str, _max_timeout_retries: int = 2):
        element = await self.e64(self.client.governance_officer._async_get_decision_by_guid(guid_))
        return element if isinstance(element, dict) else None

    def decision_properties(self, qualified_name: str) -> dict:
        attributes = self.parsed_output["attributes"]
        props = set_element_prop_body(e64.DECISION, qualified_name, attributes)
        props.update({k: v for k, v in _fields(attributes, DECISION_FIELDS).items() if v not in EMPTY})
        props["class"] = e64.DECISION_PROPERTIES
        # Empty values are not sent: on a merge update an empty list (set_element_prop_body's default authors)
        # would clear what Egeria holds.
        props = {k: v for k, v in body_slimmer(props).items() if v not in EMPTY}
        return read_keys_only(props, attributes, {**ELEMENT_ATTRIBUTE_OF,
                                                  **{k: n for n, k in DECISION_FIELDS.items()}})

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        qualified_name = self.parsed_output.get("qualified_name")
        display_name = value(attributes, "Display Name")
        go = self.client.governance_officer

        if self.command.verb == "Update":
            guid_ = self.parsed_output.get("guid")
            body = set_update_body(e64.DECISION, attributes)
            body["properties"] = self.decision_properties(qualified_name)
            body = body_slimmer(body)
            self.last_body = body
            await self.e64(go._async_update_decision(guid_, body))
            logger.success(f"Updated Decision '{display_name}' ({guid_})")
            update_element_dictionary(qualified_name, {"guid": guid_, "display_name": display_name})
            return await self.render_result_markdown(guid_)

        body = set_create_body(e64.DECISION, attributes)
        body["properties"] = self.decision_properties(qualified_name)
        body.pop("initialClassifications", None)
        body = body_slimmer(body)
        self.last_body = body
        guid_ = self.extract_guid_or_raise(await self.e64(go._async_create_decision(body)), "Create Decision")
        self.parsed_output["guid"] = guid_
        update_element_dictionary(qualified_name, {"guid": guid_, "display_name": display_name})
        logger.success(f"Created Decision '{display_name}' with GUID {guid_}")
        return await self.render_result_markdown(guid_)


class DecisionOutcomeProcessor(Egeria64LinkProcessor):
    """Link Decision Outcome / Detach Decision Outcome (uni-link: attach by the two end GUIDs)."""

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        decision, outcome = self.ends(attributes, "Decision", "Outcome")
        go = self.client.governance_officer
        if self.command.verb in self.DETACH_VERBS:
            body = delete_relationship_body(attributes)
            self.last_body = body
            await self.e64(go._async_detach_decision_outcome(decision, outcome, body))
            return f"\n\n# {self.command.verb} {self.command.object_type}\n\nDetached outcome {outcome} from decision {decision}.\n"
        body = new_relationship_body(e64.OUTCOME, attributes, _fields(attributes, OUTCOME_FIELDS),
                                     {k: n for n, k in OUTCOME_FIELDS.items()})
        self.last_body = body
        await self.e64(go._async_link_decision_outcome(decision, outcome, body))
        return f"\n\n# {self.command.verb} {self.command.object_type}\n\nLinked outcome {outcome} to decision {decision}.\n"


def _candidate_line(c: Dict[str, Any]) -> str:
    rel = c.get("relationshipHeader") or {}
    props = c.get("relationshipProperties") or {}
    return (f"Assessment GUID {rel.get('guid') or '(no GUID returned)'}, label "
            f"{props.get('label')!r}, assessmentTime {props.get('assessmentTime') or '(none)'}")


class AssessmentProcessor(Egeria64LinkProcessor):
    """Link / Update / Detach Assessment (multi-link: the relationship's own GUID identifies one)."""

    def _assessment_properties(self, attributes: Dict[str, Any]) -> dict:
        fields = _fields(attributes, ASSESSMENT_FIELDS)
        if fields.get("assessmentTime") not in EMPTY:
            utc_instant(fields["assessmentTime"], "Assessment Time")   # refused with words when it has no zone
        return fields

    async def _resolve_assessment_guid(self, attributes: Dict[str, Any]) -> str:
        """The one assessment this Update/Detach means: by Assessment GUID, else Element + Decision + Label
        (+ Assessment Time), read from the Decision's inputsToDecision. Zero or several matches are refused."""
        explicit = value(attributes, "Assessment GUID")
        if explicit not in EMPTY:
            return str(explicit).strip()
        what = f"{self.command.verb} {self.command.object_type}"
        element, decision, label = guid(attributes, "Element"), guid(attributes, "Decision"), value(attributes, "Label")
        missing = [n for n, v in (("Element", element), ("Decision", decision), ("Label", label)) if v in EMPTY]
        if missing:
            raise ValueError(f"{what} needs the Assessment GUID (as Link Assessment wrote it into the processed "
                             f"document), or else Element, Decision and Label to find it; "
                             f"{', '.join(missing)} {'is' if len(missing) == 1 else 'are'} missing.")
        wanted_time = value(attributes, "Assessment Time")
        wanted = utc_instant(wanted_time, "Assessment Time") if wanted_time not in EMPTY else None

        found = await self.e64(self.client.governance_officer._async_get_decision_by_guid(decision))
        if not isinstance(found, dict):
            raise ValueError(f"{what}: decision {decision} could not be read, so no assessment can be picked. "
                             f"Give the Assessment GUID instead.")
        inputs = found.get("inputsToDecision") or []
        same = [c for c in inputs
                if ((c.get("relatedElement") or {}).get("elementHeader") or {}).get("guid") == element
                and (c.get("relationshipProperties") or {}).get("label") == label]
        matches = same
        if wanted is not None:
            matches = [c for c in same
                       if stored_instant((c.get("relationshipProperties") or {}).get("assessmentTime")) == wanted]
        if len(matches) == 1:
            rel_guid = (matches[0].get("relationshipHeader") or {}).get("guid")
            if rel_guid:
                return rel_guid
        criteria = f"element {element}, label {label!r}" + (f", assessment time {wanted_time}" if wanted else "")
        if not matches:
            if not inputs:
                listed = (f"decision {decision} lists no assessed inputs (its inputsToDecision is empty), so there "
                          f"is nothing to {self.command.verb.lower()}.")
            elif same:
                listed = ("these assessments match the element and label but not the time: "
                          + "; ".join(_candidate_line(c) for c in same) + ".")
            else:
                listed = (f"decision {decision} has {len(inputs)} assessed input(s), none for that element and label: "
                          + "; ".join(_candidate_line(c) for c in inputs) + ".")
            raise ValueError(f"{what}: no assessment matches {criteria}; {listed} Nothing was changed.")
        hint = "Add Assessment Time, or give" if wanted is None else "Give"
        raise ValueError(f"{what}: {len(matches)} assessments match {criteria}, so none was picked: "
                         + "; ".join(_candidate_line(c) for c in matches)
                         + f". {hint} the Assessment GUID of the one you mean. Nothing was changed.")

    @staticmethod
    def _with_guid_section(raw_block: str, rel_guid: str) -> str:
        """The command block with its ``Assessment GUID`` section set to `rel_guid` (added after the header when
        absent), so the processed document identifies this assessment for later Update/Detach commands."""
        lines = raw_block.rstrip("\n").split("\n")
        for i, line in enumerate(lines):
            if re.match(r"^\s*#{3,}\s*Assessment GUID\s*$", line, re.IGNORECASE):
                j = i + 1
                while j < len(lines) and not re.match(r"^\s*#{2,}\s", lines[j]) and not lines[j].strip().startswith("___"):
                    j += 1
                return "\n".join(lines[:i + 1] + [rel_guid, ""] + lines[j:]) + "\n"
        header = next((i for i, line in enumerate(lines) if re.match(r"^\s*#{1,2}\s*\S", line)), 0)
        return "\n".join(lines[:header + 1] + ["", "### Assessment GUID", rel_guid] + lines[header + 1:]) + "\n"

    async def apply_changes(self) -> str:
        attributes = self.parsed_output["attributes"]
        verb = self.command.verb
        go = self.client.governance_officer
        attribute_of = {k: n for n, k in ASSESSMENT_FIELDS.items()}

        if verb in self.DETACH_VERBS:
            rel_guid = await self._resolve_assessment_guid(attributes)
            body = delete_relationship_body(attributes)
            self.last_body = body
            await self.e64(go._async_detach_assessment(rel_guid, body))
            return f"\n\n# {verb} {self.command.object_type}\n\nDetached assessment {rel_guid}.\n"

        if verb == "Update":
            rel_guid = await self._resolve_assessment_guid(attributes)
            body = update_relationship_body(e64.ASSESSMENT, attributes, self._assessment_properties(attributes),
                                            attribute_of)
            self.last_body = body
            await self.e64(go._async_update_assessment(rel_guid, body))
            self.parsed_output["guid"] = rel_guid
            return f"\n\n# {verb} {self.command.object_type}\n\nUpdated assessment {rel_guid}.\n"

        # Link: a new assessment, unless the document already names one (re-run of a processed document).
        properties = self._assessment_properties(attributes)
        explicit = value(attributes, "Assessment GUID")
        if explicit not in EMPTY:
            rel_guid = str(explicit).strip()
            body = update_relationship_body(e64.ASSESSMENT, attributes, properties, attribute_of)
            self.last_body = body
            await self.e64(go._async_update_assessment(rel_guid, body))
            self.parsed_output["guid"] = rel_guid
            logger.info(f"Link Assessment names Assessment GUID {rel_guid}: updated it rather than adding another")
            return (self._with_guid_section(self.command.raw_block, rel_guid)
                    + f"\n> Updated existing assessment {rel_guid} (the document names its Assessment GUID).\n")
        element, decision = self.ends(attributes, "Element", "Decision")
        body = new_relationship_body(e64.ASSESSMENT, attributes, properties, attribute_of)
        self.last_body = body
        rel_guid = await self.e64(go._async_link_assessment(element, decision, body))
        if not isinstance(rel_guid, str) or not rel_guid or rel_guid == NO_GUID_RETURNED:
            raise ValueError(f"Link Assessment: Egeria returned no relationship GUID ({rel_guid!r}), so the "
                             f"processed document can't name this assessment.")
        self.parsed_output["guid"] = rel_guid
        return (self._with_guid_section(self.command.raw_block, rel_guid)
                + f"\n> Linked assessment {rel_guid}: element {element} assessed for decision {decision}.\n")


def register_decision_processors(reg) -> List[str]:
    """Register the B1 commands; returns their names."""
    names = {
        "Create Decision": DecisionProcessor, "Update Decision": DecisionProcessor,
        "Link Decision Outcome": DecisionOutcomeProcessor, "Detach Decision Outcome": DecisionOutcomeProcessor,
        "Link Assessment": AssessmentProcessor, "Update Assessment": AssessmentProcessor,
        "Detach Assessment": AssessmentProcessor,
    }
    for name, cls in names.items():
        reg(name, cls)
    return list(names)
