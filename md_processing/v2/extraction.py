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
    "Search", "Find", "Provenance", "Validate", "Process"
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
    - Standard Markdown (# Verb Object)
    - Jupyter Notebooks (Markdown cells)
    - LLM prompts (Headless or Markdown)
    """
    def __init__(self, text: str):
        self.text = text
        # Regex for a command header line: # <Verb> <Object> or headless <Verb> <Object>
        verbs_pattern = "|".join(STANDARD_VERBS)
        self.cmd_header_rx = re.compile(
            rf"^\s*(?:#\s+)?(?P<verb>{verbs_pattern})\s+(?P<object>[^#\n_]+)\s*$",
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

    def _split_into_blocks(self) -> List[tuple[str, int]]:
        """Split text into potential command blocks based on H1 headers or horizontal rules."""
        # Using a lookahead to split by '#' at start of line OR horizontal rules
        # Also handles headless blocks by checking if the start is a command
        lines = self.text.splitlines()
        blocks = []
        current_block = []
        start_line = 1
        
        for i, line in enumerate(lines):
            # Check for block boundaries: H1 header or horizontal rule
            if (line.startswith("# ") or re.match(r'^\s*___+\s*$', line) or re.match(r'^\s*---+\s*$', line)):
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
        """Extracts ## attributes from a block of text."""
        attributes = {}
        # Match ## Header until next ## or end of block
        attr_rx = re.compile(r"^##\s+(?P<label>[^#\n]+)\n(?P<value>(?:(?!^##).)*)", re.MULTILINE | re.DOTALL)
        
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
