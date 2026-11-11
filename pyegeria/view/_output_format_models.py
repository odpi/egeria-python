"""
SPDX-License-Identifier: Apache-2.0
Copyright Contributors to the ODPi Egeria project.

This module defines Pydantic models for output format sets used in pyegeria.

These models provide a structured way to define and validate output formats
for different types of data, supporting composition and reuse of formats.

The module defines the following models:
- Column: Represents a column in an output format with name, key, and format attributes.
- Format: Represents a format configuration with types and columns.
- ActionParameter: Represents a parameter for an action with function, required_params, optional_params, and spec_params.
- FormatSet: Represents a complete format set with heading, description, aliases, annotations, formats, and actions.
- FormatSetDict: A dictionary of format sets with methods for backward compatibility.

These models are used in the `_output_formats.py` module to replace the dictionary-based
implementation of output format sets. The models provide several advantages:
- Type validation: The models ensure that the data has the correct types and structure.
- Composition: The models support composition of formats, allowing formats to be reused and combined.
- Documentation: The models provide clear documentation of the data structure.
- IDE support: The models provide better IDE support, including autocompletion and type hints.

Example usage:
```python
from pyegeria._output_format_models import Column, Format, FormatSet

# Create columns
columns = [
    Column(name="Display Name", key="display_name"),
    Column(name="Description", key="description", format=True),
]

# Create a format
format = Format(
    types=["TABLE", "DICT"],
    columns=columns,
)

# Create a format set
format_set = FormatSet(
    heading="Example Format Set",
    description="An example format set",
    formats=[format],
)

# Convert to dictionary for backward compatibility
format_set_dict = format_set.dict()
```

The models are designed to be backward compatible with the existing dictionary-based
implementation. The `FormatSet` class has a `get` method that mimics the behavior of a
dictionary, and the `FormatSetDict` class provides dictionary-like access to the format sets.

Exceptions
----------
The following exceptions may be raised by functions and classes in this module:
- FileNotFoundError: When attempting to load format sets from a non-existent JSON file.
- json.JSONDecodeError: When a JSON file cannot be parsed.
- pydantic.ValidationError: When provided data does not conform to the expected model schema
  for `Column`/`Attribute`, `Format`, `ActionParameter`, `QuestionSpec`, or `FormatSet`.
- KeyError: Accessing a missing format set label via `FormatSetDict.__getitem__` or
  `FormatSet.get` when a default is not supplied.
- ValueError: From internal validators if an attribute/format contains invalid values.
"""

import json
import os
import warnings
from pathlib import Path
from typing import Dict, List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator
from loguru import logger
__all__ = [
    'Column',
    'Attribute',
    'Format',
    'ActionParameter',
    'FormatSet',
    'FormatSetDict',
    'save_format_sets_to_json',
    'load_format_sets_from_json',
]

def save_format_sets_to_json(format_sets: Dict[str, 'FormatSet'], file_path: str) -> None:
    """
    Save format sets to a JSON file.
    
    Args:
        format_sets: The format sets to save
        file_path: The path to save the file to
    """
    # Convert FormatSet objects to dictionaries
    serializable_dict = {key: value.dict() for key, value in format_sets.items()}
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    # Write to file
    try:
        with open(file_path, 'w') as f:
            json.dump(serializable_dict, f, indent=2)
        logger.info(f"Format sets saved to {file_path}")
    except Exception as e:
        logger.error(f"Error saving format sets to {file_path}: {e}")
        raise

def load_format_sets_from_json(file_path: str) -> Dict[str, 'FormatSet']:
    """
    Load format sets from a JSON file.
    
    Args:
        file_path: The path to load the file from
        
    Returns:
        Dict[str, FormatSet]: The loaded format sets
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Convert dictionaries to FormatSet objects
        format_sets = {}
        for key, value in data.items():
            format_sets[key] = FormatSet(**value)
        
        logger.info(f"Format sets loaded from {file_path}")
        return format_sets
    except Exception as e:
        logger.error(f"Error loading format sets from {file_path}: {e}")
        raise

COLUMN_RENDERS = ("text", "join", "bullets", "kv", "subtable", "count", "link")
COLUMN_LABELS = ("qualified_name", "display_name")


class Column(BaseModel):
    """
    Represents an attribute (formerly called a column) in an output format.
    
    Fields:
        name: The display name of the attribute
        key: The key used to access the attribute's value in the data
        format: Whether the attribute's value should be formatted
        detail_spec: Optional report spec to use for detailed rendering of this column
        valid_values: Optional list or dict of valid values for Enum mapping
        render: How a renderer draws the value (R2): text, join, bullets, kv, subtable, count or link.
            Unset, it follows the value's type (scalar/text -> text, list -> bullets, map -> kv,
            related elements -> join, sub-rows -> subtable). `subtable` without detail_spec uses the
            objects' own scalar keys.
        max_items: Items a list cell shows before "+N more" (effective default 10).
        max_lines: Lines a long text cell shows in web-oriented outputs (effective default 3).
        label: Which name a related element shows in text outputs: "qualified_name" (the default,
            today's text) or "display_name". Set per column, never globally (the F7 read-back).
    """
    name: str
    key: str
    value: Any = None
    format: Union[bool, str] = False
    detail_spec: Optional[str] = None
    valid_values: Optional[Union[List[str], Dict[str, str]]] = None
    render: Optional[Literal["text", "join", "bullets", "kv", "subtable", "count", "link"]] = None
    max_items: Optional[int] = Field(default=None, ge=1)
    max_lines: Optional[int] = Field(default=None, ge=1)
    label: Optional[Literal["qualified_name", "display_name"]] = None

# New preferred alias for Column
Attribute = Column

DOCUMENT_OUTPUT_TYPE = "DOCUMENT"


def check_document_file_name(file_name: str) -> Optional[str]:
    """Why a document file name (or its template) is refused, or None when it is safe: a file
    name is one name in the output directory, never a path. No separators, no `..`, not empty,
    not hidden."""
    if not isinstance(file_name, str) or not file_name.strip():
        return "the file name is empty"
    if "/" in file_name or "\\" in file_name:
        return f"the file name '{file_name}' contains a path separator; it must be a single file name"
    if ".." in file_name:
        return f"the file name '{file_name}' contains '..'; it must be a single file name"
    if file_name.startswith(".") or file_name.startswith("~"):
        return f"the file name '{file_name}' starts with '{file_name[0]}'; it must be a plain file name"
    if "\x00" in file_name:
        return "the file name contains a NUL character"
    return None


class DocumentSpec(BaseModel):
    """What a DOCUMENT format produces (SD-1): one document in a published standard.

    Fields:
        standard: the standard the document conforms to, e.g. "dcat-ap-3".
        media_type: its media type, e.g. "application/ld+json".
        file_name: a template filled from the run's parameters, e.g. "{scope}-dcat.jsonld".
            A single file name: path separators and ".." are refused here and again after the
            parameters are filled in.
        validator: an optional registered document-validator name
            (`pyegeria.view.document_validators`). With none, every result says
            `not_validated` and why.
        validator_options: options passed to the validator, e.g. {"shapes": "package:<pkg>/<path>"}
            for the built-in `shacl`, {"schema": "package:<pkg>/<path>"} for `json-schema`. A
            file reference here must be a `package:` reference: a spec may be held in Egeria and
            written by any user, so it may not name a local file or URL.
    """
    standard: str
    media_type: str
    file_name: str
    validator: Optional[str] = None
    validator_options: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("validator_options")
    @classmethod
    def _package_references_only(cls, v):
        """A spec may be held in Egeria and written by any user, so it may not make the Portal or
        EA read a local file: `schema`/`shapes` must be `package:` references (SD-1 read-back C2)."""
        from pyegeria.view.document_validators import spec_option_refusal
        reason = spec_option_refusal(v)
        if reason:
            raise ValueError(f"DOCUMENT {reason}")
        return v

    @field_validator("file_name")
    @classmethod
    def _safe_file_name(cls, v):
        reason = check_document_file_name(v)
        if reason:
            raise ValueError(f"DOCUMENT file_name refused: {reason}")
        return v


class Format(BaseModel):
    """
    Represents a format configuration with types and attributes.
    
    Fields:
        types: The output types this format supports (e.g., "DICT", "TABLE", "ALL", "DOCUMENT")
        attributes: The attributes (formerly columns) to include in the output. A DOCUMENT
            format has none: its exporter builds the whole document.
        document: For a DOCUMENT format only (and required there): the standard, media type,
            file name template and optional validator. See `DocumentSpec`.
    """
    types: List[str]
    attributes: List[Union[Column, Dict[str, Any]]] = Field(default_factory=list)
    document: Optional[DocumentSpec] = None

    @model_validator(mode="after")
    def _document_block_matches_type(self):
        """A DOCUMENT format stands alone in its row and carries a `document` block; no other
        format carries one."""
        types = [str(t).upper() for t in self.types]
        if DOCUMENT_OUTPUT_TYPE in types:
            if len(types) > 1:
                raise ValueError(
                    f"A DOCUMENT format cannot share its row with other output types ({', '.join(self.types)}): "
                    f"a document is not a rendering of attributes")
            if self.document is None:
                raise ValueError("A DOCUMENT format needs a 'document' block (standard, media_type, file_name)")
        elif self.document is not None:
            raise ValueError(f"Only a DOCUMENT format carries a 'document' block, not {', '.join(self.types)}")
        return self
    
    @model_validator(mode="before")
    @classmethod
    def _migrate_columns_to_attributes(cls, values):
        """Support legacy 'columns' by migrating to 'attributes' when loading."""
        if isinstance(values, dict):
            if 'attributes' not in values and 'columns' in values:
                values['attributes'] = values.pop('columns')
        return values

    @field_validator('attributes', mode='before')
    @classmethod
    def validate_attributes(cls, v):
        """Convert dictionary attributes to Attribute/Column objects."""
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(Column(**item))
            else:
                result.append(item)
        return result
    
    def dict(self, *args, **kwargs):
        """Override dict method to convert Attribute objects back to dictionaries.
        Emits both 'attributes' (preferred) and 'columns' (deprecated) for backward compatibility.
        """
        result = self.model_dump(*args, **kwargs)
        result['attributes'] = [
            attr if isinstance(attr, dict) else attr.model_dump()
            for attr in self.attributes
        ]
        # Backward-compat alias
        result['columns'] = list(result['attributes'])
        return result

    # Backward-compat property to expose 'columns'
    @property
    def columns(self):
        return self.attributes

    @columns.setter
    def columns(self, value):
        # Allow setting via legacy field
        self.attributes = self.validate_attributes(value)

class ActionParameter(BaseModel):
    """
    Represents a parameter for an action.

    A FormatSet's action has up to two independent execution paths, mirroring
    the two function slots Dr.Egeria commands have always carried
    (`find_method`/`find_constraints` and `extra_find`/`extra_constraints` --
    present in the compact command schema since its inception, but `extra_find`
    was inert until this field was added: gen_report_specs.py only ever read
    `find_method`). Both draw their parameter *values* from the same command
    attributes at runtime -- they differ in which Python function gets called
    and what shape of result it returns:

    - `function` (from `find_method`): an element-query call, typically a
      `pyegeria.omvs.*` method (e.g. `MetadataExpert.find_metadata_elements_with_string`)
      -- returns a list of Egeria elements, formatted per-column by the
      FormatSet's `Format.attributes` (the TABLE/DICT/REPORT/MERMAID path).
    - `analytic_function` (from `extra_find`): a generic counting/aggregation
      call, typically a `pyegeria.view.overview_metrics` (or similar) function
      -- returns already-aggregated {label, value[, series]}-shaped dicts
      ready for a Vega chart generator, not raw elements. Optional: only set
      when the same report spec should also support a chart-shaped
      representation of the same underlying data (e.g. a growth-over-time
      line chart alongside a plain element list).

    Unlike `function`, `analytic_function` has no fixed required/optional
    param-name list: each analytic function takes whatever arbitrary
    parameters it needs (window/points for growth_series, something else for
    the next one), supplied via a Report's free-form "Analytic Parameters"
    dict (a `Create Report` attribute) and forwarded to the analytic function
    as-is at execution time -- no per-function param registry to maintain
    here as more analytic functions are added.

    Attributes:
        function: The (find) function to call. Optional when analytic_function is set.
        required_params: Parameters that are required from the user, for `function`
        optional_params: Parameters that are optional from the user, for `function`
        spec_params: Parameters that are fixed for this action, for `function`
        analytic_function: The (extra_find) analytic/aggregation function to call, if any
        analytic_spec_params: Parameters fixed for this action, for `analytic_function`
            (from `extra_constraints`) -- layered under whatever arbitrary
            parameters the caller supplies at execution time.

    RS-W2-3 PR-B: the former `analytic_binders` field is gone. A routine's non-JSON
    arguments (clients, readers, viewer, subject) are its declared `inputs`, which the
    executor's role supply provides. For one release a spec that still carries the key is
    accepted and the key ignored, with a DeprecationWarning when it is non-empty
    (`_drop_deprecated_binders`).
    """
    function: Optional[str] = None
    required_params: List[str] = Field(default_factory=list)
    optional_params: Optional[List[str]] = Field(default_factory=list)
    spec_params: Dict[str, Any] = Field(default_factory=dict)
    analytic_function: Optional[str] = None
    analytic_spec_params: Dict[str, Any] = Field(default_factory=dict)

    _dropped_binders: List[str] = PrivateAttr(default_factory=list)

    @model_validator(mode="wrap")
    @classmethod
    def _drop_deprecated_binders(cls, values, handler):
        """Accept and ignore the removed `analytic_binders` key for one release (RS-W2-3 PR-B).

        An empty mapping (what older generated specs serialise) is dropped silently. A non-empty
        one is dropped with a DeprecationWarning and a log warning naming the parameters: the
        routine must declare them as `inputs` instead, or its call will lack them. The names are
        kept on the model (`_dropped_binders`) so the spec resolver can report them as a warning.

        The marker is a private attribute: it survives `model_copy`, but NOT `model_dump` and a
        reload (`model_validate_json(fs.model_dump_json())` has no marker and so no warning), since
        the dump no longer holds the key. Resolve the loaded spec, not a serialised copy of it. The
        EGERIA tier rebuilds its specs from the cached micro-flow text, which keeps the key, so
        its marker is set afresh on every load.
        """
        names: List[str] = []
        if isinstance(values, dict) and "analytic_binders" in values:
            values = dict(values)
            binders = values.pop("analytic_binders")
            if binders:
                names = sorted(binders) if isinstance(binders, dict) else [repr(binders)]
                message = (
                    f"analytic_binders is no longer supported and is ignored (binders for: {', '.join(names)}). "
                    f"Declare these arguments as the routine's inputs (reader:<name>, viewer, subject, "
                    f"egeria_client:<Class>); the environment's role supply provides them. "
                    f"The key will be refused in a later release.")
                warnings.warn(message, DeprecationWarning, stacklevel=2)
                logger.warning(message)
        model = handler(values)
        if names:
            model._dropped_binders = names
        return model

    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_user_params(cls, values):
        """Migrate legacy 'user_params' into 'required_params' when loading from older dict/json."""
        if isinstance(values, dict):
            if 'required_params' not in values and 'user_params' in values:
                values['required_params'] = values.pop('user_params')
        return values

    @model_validator(mode="after")
    def _needs_a_function(self):
        """`function` may be omitted only when `analytic_function` is set (ISSUE-141).

        An explicit empty string is still accepted, as it was when `function` was required.
        """
        if self.function is None and not self.analytic_function:
            raise ValueError("ActionParameter needs a function or an analytic_function")
        return self


class QuestionSpec(BaseModel):
    """
    An example-question specification for a report spec.

    Attributes:
        perspectives: A list of perspective names for whom these questions are relevant
        questions: Example natural-language questions this report spec can answer
    """
    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_roles(cls, values):
        """Migrate legacy 'roles' field to 'perspectives' when loading from older dict/json."""
        if isinstance(values, dict) and 'perspectives' not in values and 'roles' in values:
            values = dict(values)
            values['perspectives'] = values.pop('roles')
        return values
    perspectives: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)

class FormatSet(BaseModel):
    """
    Represents a complete format set with target_type, heading, description, aliases, annotations, formats, and actions.
    
    Attributes:
        target_type: The related Open Metadata entity type this format set targets (e.g., Glossary, Term). Optional.
        heading: A title for the format set
        description: A description of what the format set is for
        aliases: Alternative names that can be used to reference this format set
        annotations: Additional metadata, like wiki links
        family: Optional tag to group related format sets for organization/searching
        formats: A list of format configurations
        action: Optional action associated with the format set
        get_additional_props: Optional action used to retrieve additional properties for a format set
    """
    target_type: Optional[str] = None
    heading: str
    description: str
    aliases: List[str] = Field(default_factory=list)
    annotations: Dict[str, List[str]] = Field(default_factory=dict)
    family: Optional[str] = None
    formats: List[Union[Format, Dict[str, Any]]]
    action: Optional[Union[ActionParameter, Dict[str, Any]]] = None
    get_additional_props: Optional[Union[ActionParameter, Dict[str, Any]]] = None
    # Optional: example questions and perspectives this report spec can address
    question_spec: Optional[List[Union[QuestionSpec, Dict[str, Any]]]] = None
    
    @model_validator(mode="before")
    @classmethod
    def _migrate_legacy_fields(cls, values):
        """Migrate legacy fields from older saved JSON (entity_type -> target_type)."""
        if isinstance(values, dict):
            if 'entity_type' in values and 'target_type' not in values:
                values['target_type'] = values.pop('entity_type')
            # Egeria's ReportSpec property, and the canonical JSON key (ws #794, RS-W2-2 PR-B).
            # `target_type` stays this model's field name until the generator moves (§9.6).
            if 'target_type_name' in values:
                values = dict(values)
                canonical = values.pop('target_type_name')
                if values.get('target_type') not in (None, canonical):
                    raise ValueError(f"target_type_name '{canonical}' and target_type '{values['target_type']}' "
                                     "disagree: they are one value (target_type is its old key)")
                values['target_type'] = canonical
        return values

    @property
    def target_type_name(self) -> Optional[str]:
        """Egeria's name for `target_type` (the ReportSpec property targetTypeName)."""
        return self.target_type

    @field_validator('formats', mode='before')
    @classmethod
    def validate_formats(cls, v):
        """Convert dictionary formats to Format objects."""
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(Format(**item))
            else:
                result.append(item)
        return result

    @model_validator(mode="after")
    def _document_spec_rules(self):
        """A report spec with a DOCUMENT format (SD-1) is a document spec:

        - its document is built by an exporter, so its action needs an `analytic_function`;
        - a `function` (find) with no analytic function is refused, since a find returns
          elements to render column by column, not a document;
        - it has no other formats, since every other output type is refused for it at run time.
        """
        doc_formats = [f for f in self.formats if isinstance(f, Format) and f.document is not None]
        if not doc_formats:
            return self
        others = [t for f in self.formats if isinstance(f, Format) and f.document is None for t in f.types]
        if len(doc_formats) > 1:
            raise ValueError(f"Report spec '{self.heading}' has {len(doc_formats)} DOCUMENT formats; "
                             f"a document spec produces exactly one document")
        if others:
            raise ValueError(f"Report spec '{self.heading}' is a DOCUMENT spec and cannot also offer "
                             f"{', '.join(others)}: a DOCUMENT spec produces only its document")
        action = self.action
        if action is None or isinstance(action, dict):
            fn = (action or {}).get("function") if isinstance(action, dict) else None
            analytic = (action or {}).get("analytic_function") if isinstance(action, dict) else None
        else:
            fn, analytic = action.function, action.analytic_function
        if not analytic:
            if fn:
                raise ValueError(
                    f"Report spec '{self.heading}' has a DOCUMENT format and a find function ({fn}) but no "
                    f"analytic_function: a find returns elements, not a document. Name an exporter as the "
                    f"action's analytic_function")
            raise ValueError(f"Report spec '{self.heading}' has a DOCUMENT format but no action.analytic_function; "
                             f"a document is built by an exporter registered as an analytic function")
        return self

    def document_format(self) -> Optional["Format"]:
        """This spec's DOCUMENT format, or None when it is not a document spec."""
        for f in self.formats:
            if isinstance(f, Format) and f.document is not None:
                return f
        return None

    @field_validator('question_spec', mode='before')
    @classmethod
    def validate_question_spec(cls, v):
        """Convert dictionary items to QuestionSpec objects when provided."""
        if v is None:
            return None
        out: List[QuestionSpec] = []
        for item in v:
            if isinstance(item, dict):
                out.append(QuestionSpec(**item))
            else:
                out.append(item)
        return out
    
    @field_validator('action', 'get_additional_props', mode='before')
    @classmethod
    def validate_action_like(cls, v):
        """Convert dictionary action-like fields to ActionParameter objects. Accepts legacy list shape."""
        if v is None:
            return None
        # Backward compatibility: if a list is provided, use the first element
        if isinstance(v, list):
            if not v:
                return None
            logger.warning("FormatSet.action/get_additional_props provided as a list; coercing first element to dict. This shape is deprecated.")
            v = v[0]
        if isinstance(v, dict):
            return ActionParameter(**v)
        return v
    
    def dict(self, *args, **kwargs):
        """Override dict method to convert nested objects back to dictionaries."""
        result = self.model_dump(*args, **kwargs)
        result['formats'] = [
            format if isinstance(format, dict) else format.dict()
            for format in self.formats
        ]
        if self.action is not None:
            result['action'] = self.action if isinstance(self.action, dict) else self.action.model_dump()
        if self.get_additional_props is not None:
            result['get_additional_props'] = (
                self.get_additional_props if isinstance(self.get_additional_props, dict) else self.get_additional_props.model_dump()
            )
        if self.question_spec is not None:
            result['question_spec'] = [
                item if isinstance(item, dict) else item.model_dump() for item in self.question_spec
            ]
        return result
    
    def get(self, key, default=None):
        """
        Dictionary-like get method for backward compatibility.
        
        Args:
            key: The key to look up
            default: The default value to return if the key is not found
            
        Returns:
            The value for the key if found, otherwise the default value
        """
        if hasattr(self, key):
            return getattr(self, key)
        return default

    def merge_with(self, other: "FormatSet") -> "FormatSet":
        """Deep merge another FormatSet into this one.

        Updates simple fields (heading, description, target_type, family, action)
        if the other one has non-empty values.

        The formats list is merged based on the 'types' of each format. If a format
        with the same set of types exists, it is replaced. Otherwise, it is appended.
        """
        if other.heading:
            self.heading = other.heading
        if other.description:
            self.description = other.description
        if other.target_type:
            self.target_type = other.target_type
        if other.family:
            self.family = other.family
        if other.action:
            self.action = other.action
        if other.get_additional_props:
            self.get_additional_props = other.get_additional_props
        if other.question_spec:
            self.question_spec = other.question_spec

        # Merge aliases
        if other.aliases:
            existing_aliases = set(self.aliases or [])
            existing_aliases.update(other.aliases)
            self.aliases = sorted(list(existing_aliases))

        # Merge formats
        # Since formats is a list of Format objects, we merge based on the types they support.
        for other_fmt in other.formats:
            # Ensure other_fmt is a Format object
            if isinstance(other_fmt, dict):
                other_fmt = Format(**other_fmt)

            other_types = set(other_fmt.types)
            found = False
            for i, existing_fmt in enumerate(self.formats):
                if isinstance(existing_fmt, dict):
                    existing_fmt = Format(**existing_fmt)
                    self.formats[i] = existing_fmt

                if set(existing_fmt.types) == other_types:
                    self.formats[i] = other_fmt
                    found = True
                    break
            if not found:
                self.formats.append(other_fmt)

        return self

class FormatSetDict(Dict[str, FormatSet]):
    """
    A dictionary of format sets, with methods for backward compatibility.
    
    This class allows the format sets to be accessed like a dictionary,
    while providing the validation and structure of Pydantic models.
    
    It also provides the ability to find format sets by either name or alias,
    making it easier to work with format sets without knowing their exact name.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def find_by_name_or_alias(self, key, default=None):
        """
        Find a format set by either name or alias.
        
        This method first checks if the key exists directly in the dictionary.
        It also tries to normalize spaces to dashes as a robustness measure.
        If not found, it searches through all format sets to find one with a matching alias.
        
        Args:
            key: The name or alias to look up
            default: The default value to return if the key is not found
        
        Returns:
            FormatSet: The format set if found, otherwise the default value
        """
        # First try to find by name (key)
        format_set = super().get(key, None)
        
        # Second try: normalize spaces to dashes (e.g., 'Business Imperative-DrE' -> 'Business-Imperative-DrE')
        if format_set is None and isinstance(key, str) and " " in key:
            format_set = super().get(key.replace(" ", "-"), None)
        
        # If not found by name/normalized name, try to find by alias
        if format_set is None:
            for value in self.values():
                if key in value.aliases:
                    format_set = value
                    break
        
        # Return the format set if found, otherwise the default value
        return format_set if format_set is not None else default
    
    def get(self, key, default=None):
        """
        Get a format set by name or alias.
        
        This method first checks if the key exists directly in the dictionary.
        If not found, it searches through all format sets to find one with a matching alias.
        
        Args:
            key: The name or alias to look up
            default: The default value to return if the key is not found
        
        Returns:
            FormatSet: The format set if found, otherwise the default value
        """
        return self.find_by_name_or_alias(key, default)
    
    def filter_by_family(self, family: str) -> Dict[str, FormatSet]:
        """
        Return a plain dict of format sets whose `family` matches the given value.
        
        Matching rules
        - Case-insensitive comparison
        - Leading/trailing whitespace in the input and stored family are ignored
        - Pass an empty string ("") to match entries with no family assigned
        
        Args:
            family: Family name to match (case-insensitive). Use "" to select entries with no family.
        
        Returns:
            dict[str, FormatSet]: Mapping of spec name -> FormatSet for matching entries.
        """
        # Normalize the requested family
        fam_norm = (family or "").strip().lower()
        result: Dict[str, FormatSet] = {}
        for name, fs in self.items():
            fs_family_raw = getattr(fs, "family", None)
            fs_family_norm = (fs_family_raw or "").strip().lower()
            if fam_norm == "":
                # Select items with no family set
                if fs_family_norm == "":
                    result[name] = fs
            else:
                if fs_family_norm == fam_norm:
                    result[name] = fs
        return result
    
    def values(self):
        """Get all format sets."""
        return super().values()
    
    def keys(self):
        """Get all format set names."""
        return super().keys()
    
    def items(self):
        """Get all format set items."""
        return super().items()
    
    def __getitem__(self, key):
        """
        Get a format set by name or alias.
        
        This method first checks if the key exists directly in the dictionary.
        If not found, it searches through all format sets to find one with a matching alias.
        If still not found, it raises a KeyError.
        
        Args:
            key: The name or alias to look up
            
        Returns:
            FormatSet: The format set if found
            
        Raises:
            KeyError: If the format set is not found by name or alias
        """
        format_set = self.find_by_name_or_alias(key, None)
        if format_set is None:
            raise KeyError(key)
        return format_set
    
    def __setitem__(self, key, value):
        """Set a format set by name."""
        if isinstance(value, dict):
            value = FormatSet(**value)
        super().__setitem__(key, value)
    
    def __contains__(self, key):
        """
        Check if a format set exists by name or alias.
        
        Args:
            key: The name or alias to check
        
        Returns:
            bool: True if the format set exists, False otherwise
        """
        return self.find_by_name_or_alias(key, None) is not None

    def upsert(self, key: str, value: Union[FormatSet, Dict[str, Any]]) -> None:
        """
        Add a format set if it doesn't exist, or deep merge it if it does.
        
        Args:
            key: The name of the format set
            value: The FormatSet object or dictionary to upsert
        """
        if isinstance(value, dict):
            value = FormatSet(**value)
            
        existing = self.find_by_name_or_alias(key, None)
        if existing:
            existing.merge_with(value)
        else:
            self[key] = value

    def to_dict(self):
        """Convert all format sets to dictionaries."""
        return {key: value.dict() for key, value in self.items()}
        
    def save_to_json(self, file_path: str) -> None:
        """
        Save format sets to a JSON file.
        
        Args:
            file_path: The path to save the file to
        """
        save_format_sets_to_json(self, file_path)
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'FormatSetDict':
        """
        Load format sets from a JSON file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            FormatSetDict: A new FormatSetDict instance with the loaded format sets
        """
        format_sets = load_format_sets_from_json(file_path)
        return cls(format_sets)