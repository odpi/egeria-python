"""
Standardized extraction logic for Dr.Egeria v2.
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from loguru import logger

# Standard Dr.Egeria / OMAG verbs
STANDARD_VERBS = {
    "Create", "Update", "Delete", "Link", "Attach", "Add",
    "Unlink", "Detach", "Remove", "Display", "Run", "View",
    "Search", "Find", "Provenance", "Validate", "Process",
    "Classify", "Reclassify", "Declassify",
    # "Cancel Engine Action" -- stops an in-progress engine action request;
    # matches the concept name used everywhere else in the codebase (the
    # Egeria REST endpoint, pyegeria's cancel_engine_action, the Operations
    # UI's Cancel button), so it earns its own verb rather than overloading
    # Delete/Remove (which would misleadingly imply erasing the audit record).
    "Cancel",
    # "Initiate Engine Action" -- ad-hoc triggers a governance engine request;
    # matches pyegeria's initiate_engine_action / Egeria's own
    # InitiateEngineActionRequestBody naming. Deliberately not "Create Engine
    # Action": unlike every other Create command in this codebase, this is
    # never an idempotent upsert-by-qualified-name -- each call mints a new
    # runtime request even if a prior one shares the same display name.
    "Initiate",
    # Reference Data family: valid metadata values, map names, map values
    # ("Setup Valid Metadata Value", "Clear Valid Metadata Map Name", "Set
    # Consistent Metadata Values", etc.). Without these, the whole family's
    # `## Setup ...`/`## Clear ...`/`## Set ...` headings never match
    # cmd_header_rx, so extract_commands() silently falls through to its
    # "preserve as prose" branch (is_command=False) -- no error, no summary
    # row, and every downstream definition/link claiming the never-created
    # valid value fails with an unrelated-looking message instead.
    "Setup", "Clear", "Set",
    # Digital Products family: "Import Data Contract" / "Import Data Product" (catalog an
    # ODCS / ODPS document) and "Publish Data Contract" / "Publish Data Product" (send one to an
    # integration daemon). Without these the `## Import ...` / `## Publish ...` headings never match
    # cmd_header_rx and silently fall through as prose -- no error, no summary row.
    "Import", "Publish",
    # MetadataExpert family: "Count Metadata Elements".
    "Count",
}

# Commands that appear as a single word (no separate verb) and map to canonical verb+object
VERBLESS_COMMAND_ALIASES = {
    "report": ("View", "Report"),
}

@dataclass
class DrECommand:
    verb: str
    object_type: str
    source_verb: str = ""
    source_object_type: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)
    raw_block: str = ""
    start_line: int = 0
    end_line: int = 0
    is_command: bool = True

class UniversalExtractor:
    """
    Extracts Dr.Egeria commands from various text formats:
    - Standard Markdown (## Verb Object)
    - Jupyter Notebooks (Markdown cells)
    - LLM prompts (Headless or Markdown)
    """
    def __init__(self, text: str):
        self.text = text
        # Regex for a command header line: ## <Verb> <Object> or headless <Verb> <Object>
        verbs_pattern = "|".join(STANDARD_VERBS)
        self.cmd_header_rx = re.compile(
            rf"^\s*(?P<header>##\s+)?(?P<verb>{verbs_pattern})\s+(?P<object>[^#\n_]+)\s*$",
            re.IGNORECASE,
        )

    def _match_command_header(self, block_text: str) -> Optional[re.Match[str]]:
        """Return a command match only when the first meaningful line is a command header."""
        for line in block_text.splitlines():
            if not line.strip():
                continue
            if re.match(r'^\s*___+\s*$', line) or re.match(r'^\s*---+\s*$', line):
                continue
            return self.cmd_header_rx.match(line)
        return None

    def extract_commands(self) -> List[DrECommand]:
        blocks = self._split_into_blocks()
        commands = []
        
        for block_text, start_line in blocks:
            match = self._match_command_header(block_text)
            if match:
                verb = match.group("verb").strip().capitalize()
                obj = match.group("object").strip()
                
                # Cleanup object name from trailing markdown artifacts
                obj = re.sub(r'[\s_*-]+$', '', obj)
                
                attributes = self._extract_attributes_from_block(block_text)
                
                commands.append(DrECommand(
                    verb=verb,
                    object_type=obj,
                    source_verb=verb,
                    source_object_type=obj,
                    attributes=attributes,
                    raw_block=block_text,
                    start_line=start_line,
                    end_line=start_line + block_text.count('\n'),
                    is_command=True
                ))
            else:
                # Check for known verbless aliases (e.g. "## Report" → View Report)
                verbless_verb, verbless_obj = "", ""
                for line in block_text.splitlines():
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if re.match(r'^\s*[_-]{3,}\s*$', line):
                        continue
                    word = re.sub(r'^##?\s*', '', stripped).strip().lower()
                    if word in VERBLESS_COMMAND_ALIASES:
                        verbless_verb, verbless_obj = VERBLESS_COMMAND_ALIASES[word]
                    break

                if verbless_verb:
                    attributes = self._extract_attributes_from_block(block_text)
                    commands.append(DrECommand(
                        verb=verbless_verb,
                        object_type=verbless_obj,
                        source_verb=word.capitalize(),
                        source_object_type="",
                        attributes=attributes,
                        raw_block=block_text,
                        start_line=start_line,
                        end_line=start_line + block_text.count('\n'),
                        is_command=True
                    ))
                else:
                    # Preservation: include non-command blocks as-is
                    commands.append(DrECommand(
                        verb="",
                        object_type="",
                        source_verb="",
                        source_object_type="",
                        attributes={},
                        raw_block=block_text,
                        start_line=start_line,
                        end_line=start_line + block_text.count('\n'),
                        is_command=False
                    ))
        return commands

    def diagnose(self, command_attributes: Optional[Dict[str, List[str]]] = None) -> List[str]:
        """Explain, in words, heading mistakes that make a document run less than its author meant (PY-30).

        A Dr.Egeria command is an H2 heading ``## <Verb> <Object>`` with its attributes as H3 ``### <Label>``.
        Two mistakes otherwise pass silently:

        - an H1 command heading (``# Delete Instance``) is kept as prose, so the document runs nothing;
        - an attribute written as H2 (``## Delete Method``) can match the command pattern and be taken as a
          command of its own.

        ``command_attributes`` maps a command name ("Delete Instance") to its attribute labels. When it is None,
        the compact command specs are loaded if available; without them the second check is skipped.
        Returns hint strings (empty when nothing looks wrong).
        """
        hints: List[str] = []
        if command_attributes is None:
            command_attributes = _load_command_attributes()
        known = {name.lower(): {a.lower() for a in attrs} for name, attrs in (command_attributes or {}).items()}
        # A Create command is also written as Update (the dispatcher upserts), so "# Update Data Class" is a known name.
        for name, attrs in list((command_attributes or {}).items()):
            if name.startswith("Create "):
                known.setdefault("update " + name[len("Create "):].lower(), {a.lower() for a in attrs})

        in_fence = False
        for number, line in enumerate(self.text.splitlines(), 1):
            # Lines inside ``` or ~~~ code fences are code (e.g. a shell comment "# Create a venv"), never headings.
            if re.match(r"^\s*(```|~~~)", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            h1 = re.match(r"^#\s+(?P<rest>[^#].*?)\s*$", line)
            if not h1:
                continue
            m = self.cmd_header_rx.match(h1.group("rest"))
            if not m:
                continue
            rest = h1.group("rest")
            name = f"{m.group('verb').strip().capitalize()} {re.sub(r'[\s_*-]+$', '', m.group('object').strip())}"
            # With the specs at hand, only a real command name earns the hint ("# Create Fantasy Thing" doesn't).
            if known and name.lower() not in known:
                continue
            hints.append(
                f"line {number}: '# {rest}' is an H1 heading, so it is read as a title, not a command. "
                f"Write the command as '## {rest}' and its attributes as '### <Attribute>'."
            )

        commands = [c for c in self.extract_commands() if c.is_command]
        if known:
            previous: Optional[str] = None
            for cmd in commands:
                name = f"{cmd.verb} {cmd.object_type}".strip()
                if name.lower() in known:
                    previous = name
                    continue
                if previous and name.lower() in known.get(previous.lower(), set()):
                    hints.append(
                        f"line {cmd.start_line}: '## {name}' is an attribute of '{previous}' written as a command "
                        f"heading. Write it as '### {name}'."
                    )

        if not commands:
            hints.append(
                "No Dr.Egeria command was found. A command is an H2 heading '## <Verb> <Object>' "
                "followed by '### <Attribute>' lines."
            )
        return hints

    def _split_into_blocks(self) -> List[tuple[str, int]]:
        """Split text into potential command blocks based on H1/H2 headers or horizontal rules."""
        # Using a lookahead to split by '#' or '##' at start of line OR horizontal rules
        # Also handles headless blocks by checking if the start is a command
        lines = self.text.splitlines()
        blocks = []
        current_block = []
        start_line = 1
        
        for i, line in enumerate(lines):
            # Check for block boundaries: H1/H2 header or horizontal rule
            if (line.startswith("# ") or line.startswith("## ") or re.match(r'^\s*___+\s*$', line) or re.match(r'^\s*---+\s*$', line)):
                if current_block:
                    blocks.append(("\n".join(current_block), start_line))
                current_block = [line]
                start_line = i + 1
            else:
                current_block.append(line)
        
        if current_block:
            blocks.append(("\n".join(current_block), start_line))
            
        return blocks

    def _extract_attributes_from_block(self, block: str) -> Dict[str, str]:
        """Extracts ### attributes from a block of text."""
        attributes = {}
        # Match ### Header until next ### or end of block
        attr_rx = re.compile(r"^###\s+(?P<label>[^#\n]+)\n(?P<value>(?:(?!^###).)*)", re.MULTILINE | re.DOTALL)
        
        for match in attr_rx.finditer(block):
            label = match.group("label").strip()
            value = match.group("value").strip()
            
            # Clean up the value (remove provenance lines, excessive newlines)
            filtered_lines = [
                line for line in value.splitlines() 
                if not line.lstrip().startswith(">") and not re.match(r'^\s*_+\s*$', line)
            ]
            attributes[label] = "\n".join(filtered_lines).strip()
            
        return attributes


def _load_command_attributes() -> Dict[str, List[str]]:
    """Command name -> attribute labels, from the compact command specs; {} if they can't be loaded."""
    try:
        from md_processing.md_processing_utils import md_processing_constants as mpc

        if not mpc.COMMAND_DEFINITIONS.get("Command Specifications"):
            mpc.load_commands()
        specs = mpc.COMMAND_DEFINITIONS.get("Command Specifications", {})
    except Exception as exc:  # the hints are advisory; never fail extraction over them
        logger.debug(f"diagnose: command specs not available ({exc})")
        return {}
    out: Dict[str, List[str]] = {}
    for name, spec in specs.items():
        if not isinstance(spec, dict):
            continue
        labels = list(spec.get("custom_attributes") or [])
        for attr in spec.get("Attributes") or []:
            if isinstance(attr, dict):
                if attr.get("name"):
                    labels.append(str(attr["name"]))
                alt = attr.get("attr_labels")
                if isinstance(alt, str):
                    labels.extend(a.strip() for a in alt.split(";") if a.strip())
                elif isinstance(alt, list):
                    labels.extend(str(a) for a in alt if a)
            elif isinstance(attr, str):
                labels.append(attr)
        out[name] = labels
    return out
