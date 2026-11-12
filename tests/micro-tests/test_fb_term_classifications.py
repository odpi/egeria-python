# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""F-B group 1: the glossary-term flags are classifications in Egeria 6.

Sent as GlossaryTerm properties they were silently ignored (round-trip probe, PostgreSQL baseline: Is
Abstract Concept / Is Activity Description / Is Context / Is Data Value / Term Activity Type / Context Scope
DROPPED, Context Description CHANGED -- it read back the term's own description).
"""
from md_processing.v2.glossary import term_properties_and_classifications


def _attrs(**kv):
    return {k.replace("_", " "): {"value": v} for k, v in kv.items()}


def test_flags_become_typed_classifications():
    props = {"class": "GlossaryTermProperties"}
    classifications = term_properties_and_classifications(props, _attrs(
        Is_Abstract_Concept=True, Is_Activity_Description=True, Term_Activity_Type="ACTION", Is_Context=True,
        Context_Description="RTP ctx", Context_Scope="RTP scope", Is_Data_Value=True, Summary="RTP sum",
        Aliases=["a1"], Example="RTP ex", Abbreviation="RTP", Usage="RTP use"))
    assert classifications == {
        "AbstractConcept": {"class": "AbstractConceptProperties"},
        "ActivityDescription": {"class": "ActivityDescriptionProperties", "activityType": "ACTION"},
        "ContextDefinition": {"class": "ContextDefinitionProperties", "description": "RTP ctx", "scope": "RTP scope"},
        "DataValueMeaning": {"class": "DataValueMeaningProperties"}}
    assert props == {"class": "GlossaryTermProperties", "aliases": ["a1"], "summary": "RTP sum",
                     "examples": "RTP ex", "abbreviation": "RTP", "usage": "RTP use"}


def test_false_or_absent_flags_classify_nothing():
    assert term_properties_and_classifications({}, _attrs(Is_Abstract_Concept=False, Is_Context=False)) == {}


def test_context_description_alone_implies_context_definition():
    c = term_properties_and_classifications({}, _attrs(Context_Description="d"))
    assert c == {"ContextDefinition": {"class": "ContextDefinitionProperties", "description": "d"}}
