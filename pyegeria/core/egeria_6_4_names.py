# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the ODPi Egeria project.
"""Every name the Egeria 6.4 additions (odpi/egeria#9463, configuration values and decisions) introduce.

The names were reviewed as the PR went in, so they are kept here and only here. Wrappers, Dr.Egeria
commands and the Egeria Explorer cards import them instead of typing them, which makes a rename one edit
here plus a regeneration of the generated tables.

Source: odpi/egeria#9463, head 0dbf468774c7f3dc102dd677b720b670ed6a8e09 (branch oak2026), merged to
odpi/egeria main as 90232870b2 with the same tree. The source sha below is now odpi/egeria main at 2e22b1e85b
(the #9465 merge, which adds SolutionBoundary and DesignModelBoundary); the five `.http` sample collections are
byte-identical there and at the #9463 head. They are in tests/fixtures/egeria-6.4/ (see its SOURCE file); tests/micro-tests/test_egeria_6_4_names.py checks this
module against them and against the generated tables.

URL paths are relative to ``/servers/{server}/api/open-metadata/`` and use the `.http` placeholder names in
single braces. Every request is a POST.
"""

EGERIA_6_4_SOURCE_SHA = "2e22b1e85b952bbe490ff19b8dcdc9f28ec260ed"

# --- Type names (11) ---------------------------------------------------------------------------------------
DECISION = "Decision"                                # entity, 0018 (AuthoredReferenceable)
OUTCOME = "Outcome"                                  # relationship, uni-link: Decision -> Referenceable
ASSESSMENT = "Assessment"                            # relationship, MULTI-link: Referenceable -> Decision
PROJECT_TARGET = "ProjectTarget"                     # relationship, uni-link: Project -> Referenceable (0130)
DATA_VALUE = "DataValue"                             # entity, 0208 (Referenceable)
LITERAL_DATA_VALUE = "LiteralDataValue"              # entity, 0208 (DataValue)
DATA_VALUE_SOURCE = "DataValueSource"                # relationship, uni-link: DataValue -> Asset
PROCESSING_VARIABLE = "ProcessingVariable"           # relationship, uni-link: Referenceable -> DataValue
EMBEDDED_DATA_VALUE = "EmbeddedDataValue"            # relationship, uni-link: DataValue -> DataValue
BRANCH = "Branch"                                    # classification, 0280, any Referenceable
SUPPORTED_VARIABLE_TYPE = "SupportedVariableType"    # relationship, uni-link: Referenceable -> SchemaType (0520)

TYPE_NAMES = (DECISION, OUTCOME, ASSESSMENT, PROJECT_TARGET, DATA_VALUE, LITERAL_DATA_VALUE, DATA_VALUE_SOURCE,
              PROCESSING_VARIABLE, EMBEDDED_DATA_VALUE, BRANCH, SUPPORTED_VARIABLE_TYPE)

# --- Relationship lists on OpenMetadataRootElement (14) -> the relationship type each reads ----------------
# Assessment lists can name the same element more than once: once per assessment.
ROOT_ELEMENT_LISTS = {
    "decisionOutcomes": OUTCOME,
    "associatedDecisions": OUTCOME,
    "inputsToDecision": ASSESSMENT,
    "assessmentDecisions": ASSESSMENT,
    "projectTargets": PROJECT_TARGET,
    "workedOnByProjects": PROJECT_TARGET,
    "processingVariables": PROCESSING_VARIABLE,
    "dataValueUses": PROCESSING_VARIABLE,
    "embeddedDataValues": EMBEDDED_DATA_VALUE,
    "parentDataValues": EMBEDDED_DATA_VALUE,
    "dataValueSources": DATA_VALUE_SOURCE,
    "providesDataValues": DATA_VALUE_SOURCE,
    "processVariableTypes": SUPPORTED_VARIABLE_TYPE,
    "processVariableTypeUses": SUPPORTED_VARIABLE_TYPE,
}

# --- Properties classes -> kind and the keys the spec names for each (some inherited) ----------------------
# The spec summary says 12 classes; #9463 adds these 11 (LiteralDataValue is sent through the data-value
# requests with class LiteralDataValueProperties).
DECISION_PROPERTIES = "DecisionProperties"
OUTCOME_PROPERTIES = "OutcomeProperties"
ASSESSMENT_PROPERTIES = "AssessmentProperties"
DATA_VALUE_PROPERTIES = "DataValueProperties"
LITERAL_DATA_VALUE_PROPERTIES = "LiteralDataValueProperties"
DATA_VALUE_SOURCE_PROPERTIES = "DataValueSourceProperties"
PROCESSING_VARIABLE_PROPERTIES = "ProcessingVariableProperties"
EMBEDDED_DATA_VALUE_PROPERTIES = "EmbeddedDataValueProperties"
PROJECT_TARGET_PROPERTIES = "ProjectTargetProperties"
SUPPORTED_VARIABLE_TYPE_PROPERTIES = "SupportedVariableTypeProperties"
BRANCH_PROPERTIES = "BranchProperties"

PROPERTIES_CLASSES = {
    # class: (kind, keys the spec names; the generated table must contain every one)
    DECISION_PROPERTIES: ("entity", ("summary", "scope", "usage", "importance", "disposition", "implications",
                                     "notes", "startTime", "lastReviewTime", "nextReviewTime", "expiryTime",
                                     "authors", "contentStatus", "userDefinedContentStatus")),
    OUTCOME_PROPERTIES: ("relationship", ("label", "description", "importance", "disposition")),
    ASSESSMENT_PROPERTIES: ("relationship", ("label", "description", "assessor", "assessorTypeName",
                                             "assessorPropertyName", "assessmentTime", "expiryTime", "notes",
                                             "additionalProperties")),
    DATA_VALUE_PROPERTIES: ("entity", ("dataFormat", "length", "dataType", "usage", "fingerprint",
                                       "fingerprintAlgorithm", "hash", "hashAlgorithm")),
    LITERAL_DATA_VALUE_PROPERTIES: ("entity", ("dataFormat", "length", "dataType", "dataValue", "dataValueList",
                                               "dataValueMap")),
    DATA_VALUE_SOURCE_PROPERTIES: ("relationship", ("label", "description")),
    PROCESSING_VARIABLE_PROPERTIES: ("relationship", ("label", "description", "position")),
    EMBEDDED_DATA_VALUE_PROPERTIES: ("relationship", ("label", "description", "position")),
    PROJECT_TARGET_PROPERTIES: ("relationship", ("label", "description")),
    SUPPORTED_VARIABLE_TYPE_PROPERTIES: ("relationship", ("label", "description", "position", "minCardinality",
                                                          "maxCardinality")),
    BRANCH_PROPERTIES: ("classification", ("displayName", "scope", "purpose", "url")),
}

# --- REST requests (31), relative to /servers/{server}/api/open-metadata/ ---------------------------------
GOVERNANCE_OFFICER = "governance-officer"
DATA_ENGINEER = "data-engineer"
PROJECT_MANAGER = "project-manager"
DEVOPS_PIPELINE = "devops-pipeline"
SCHEMA_MAKER = "schema-maker"

# Governance Officer (12; the build plan's "13" is a miscount: 12 + 13 + 2 + 2 + 2 = 31)
DECISIONS_CREATE = f"{GOVERNANCE_OFFICER}/decisions"
DECISIONS_FROM_TEMPLATE = f"{GOVERNANCE_OFFICER}/decisions/from-template"
DECISIONS_UPDATE = f"{GOVERNANCE_OFFICER}/decisions/{{decisionGUID}}/update"
DECISIONS_DELETE = f"{GOVERNANCE_OFFICER}/decisions/{{decisionGUID}}/delete"
DECISIONS_BY_NAME = f"{GOVERNANCE_OFFICER}/decisions/by-name"
DECISIONS_RETRIEVE = f"{GOVERNANCE_OFFICER}/decisions/{{decisionGUID}}/retrieve"
DECISIONS_BY_SEARCH_STRING = f"{GOVERNANCE_OFFICER}/decisions/by-search-string"
OUTCOMES_ATTACH = f"{GOVERNANCE_OFFICER}/decisions/{{decisionGUID}}/outcomes/{{outcomeGUID}}/attach"
OUTCOMES_DETACH = f"{GOVERNANCE_OFFICER}/decisions/{{decisionGUID}}/outcomes/{{outcomeGUID}}/detach"
ASSESSMENTS_ATTACH = f"{GOVERNANCE_OFFICER}/elements/{{elementGUID}}/assessments/{{decisionGUID}}/attach"
ASSESSMENTS_UPDATE = f"{GOVERNANCE_OFFICER}/assessments/{{assessmentGUID}}/update"
ASSESSMENTS_DETACH = f"{GOVERNANCE_OFFICER}/assessments/{{assessmentGUID}}/detach"

# Data Engineer (13)
DATA_VALUES_CREATE = f"{DATA_ENGINEER}/data-values"
DATA_VALUES_FROM_TEMPLATE = f"{DATA_ENGINEER}/data-values/from-template"
DATA_VALUES_UPDATE = f"{DATA_ENGINEER}/data-values/{{dataValueGUID}}/update"
DATA_VALUES_DELETE = f"{DATA_ENGINEER}/data-values/{{dataValueGUID}}/delete"
DATA_VALUES_BY_NAME = f"{DATA_ENGINEER}/data-values/by-name"
DATA_VALUES_RETRIEVE = f"{DATA_ENGINEER}/data-values/{{dataValueGUID}}/retrieve"
DATA_VALUES_BY_SEARCH_STRING = f"{DATA_ENGINEER}/data-values/by-search-string"
DATA_VALUE_SOURCES_ATTACH = f"{DATA_ENGINEER}/data-values/{{dataValueGUID}}/data-value-sources/{{assetGUID}}/attach"
DATA_VALUE_SOURCES_DETACH = f"{DATA_ENGINEER}/data-values/{{dataValueGUID}}/data-value-sources/{{assetGUID}}/detach"
PROCESSING_VARIABLES_ATTACH = f"{DATA_ENGINEER}/elements/{{elementGUID}}/processing-variables/{{dataValueGUID}}/attach"
PROCESSING_VARIABLES_DETACH = f"{DATA_ENGINEER}/elements/{{elementGUID}}/processing-variables/{{dataValueGUID}}/detach"
EMBEDDED_DATA_VALUES_ATTACH = (f"{DATA_ENGINEER}/data-values/{{parentDataValueGUID}}/embedded-data-values/"
                               f"{{embeddedDataValueGUID}}/attach")
EMBEDDED_DATA_VALUES_DETACH = (f"{DATA_ENGINEER}/data-values/{{parentDataValueGUID}}/embedded-data-values/"
                               f"{{embeddedDataValueGUID}}/detach")

# Project Manager (2)
PROJECT_TARGETS_ATTACH = f"{PROJECT_MANAGER}/projects/{{projectGUID}}/project-targets/{{targetGUID}}/attach"
PROJECT_TARGETS_DETACH = f"{PROJECT_MANAGER}/projects/{{projectGUID}}/project-targets/{{targetGUID}}/detach"

# Devops Pipeline (2): set takes a NewClassificationRequestBody (BranchProperties); remove a
# MetadataSourceRequestBody.
BRANCH_SET = f"{DEVOPS_PIPELINE}/elements/{{elementGUID}}/branch"
BRANCH_REMOVE = f"{DEVOPS_PIPELINE}/elements/{{elementGUID}}/branch/remove"

# Schema Maker (2)
SUPPORTED_VARIABLE_TYPES_ATTACH = (f"{SCHEMA_MAKER}/elements/{{elementGUID}}/supported-variable-types/"
                                   f"{{schemaTypeGUID}}/attach")
SUPPORTED_VARIABLE_TYPES_DETACH = (f"{SCHEMA_MAKER}/elements/{{elementGUID}}/supported-variable-types/"
                                   f"{{schemaTypeGUID}}/detach")

URL_PATHS = (
    DECISIONS_CREATE, DECISIONS_FROM_TEMPLATE, DECISIONS_UPDATE, DECISIONS_DELETE, DECISIONS_BY_NAME,
    DECISIONS_RETRIEVE, DECISIONS_BY_SEARCH_STRING, OUTCOMES_ATTACH, OUTCOMES_DETACH, ASSESSMENTS_ATTACH,
    ASSESSMENTS_UPDATE, ASSESSMENTS_DETACH,
    DATA_VALUES_CREATE, DATA_VALUES_FROM_TEMPLATE, DATA_VALUES_UPDATE, DATA_VALUES_DELETE, DATA_VALUES_BY_NAME,
    DATA_VALUES_RETRIEVE, DATA_VALUES_BY_SEARCH_STRING, DATA_VALUE_SOURCES_ATTACH, DATA_VALUE_SOURCES_DETACH,
    PROCESSING_VARIABLES_ATTACH, PROCESSING_VARIABLES_DETACH, EMBEDDED_DATA_VALUES_ATTACH,
    EMBEDDED_DATA_VALUES_DETACH,
    PROJECT_TARGETS_ATTACH, PROJECT_TARGETS_DETACH,
    BRANCH_SET, BRANCH_REMOVE,
    SUPPORTED_VARIABLE_TYPES_ATTACH, SUPPORTED_VARIABLE_TYPES_DETACH,
)
