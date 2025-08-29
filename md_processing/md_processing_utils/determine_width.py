"""
Determines the width of a markdown table
"""

import re
import html
from wcwidth import wcswidth

def split_row(line: str) -> list[str]:
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]

    parts = []
    cur = []
    escape = False
    for ch in s:
        if escape:
            cur.append(ch)
            escape = False
        elif ch == "\\":
            escape = True
        elif ch == "|":
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts

IMG_RE = re.compile(r'!\[([^\]]*)\]\([^)]+\)')
LINK_RE = re.compile(r'\[([^\]]*)\]\([^)]+\)')
CODE_TICKS_RE = re.compile(r'`([^`]*)`')
EMPH_RE = re.compile(r'(\*\*|\*|__|_)')

def visible_text(md: str) -> str:
    s = md
    s = IMG_RE.sub(lambda m: m.group(1), s)    # images → alt
    s = LINK_RE.sub(lambda m: m.group(1), s)   # links → text
    s = CODE_TICKS_RE.sub(lambda m: m.group(1), s)  # remove backticks
    s = EMPH_RE.sub("", s)                    # remove emphasis markers

    # unescape common backslash-escapes
    s = (s
         .replace("\\|", "|")
         .replace("\\*", "*")
         .replace("\\_", "_")
         .replace("\\`", "`")
         .replace("\\\\", "\\"))

    s = html.unescape(s)  # &amp; → &
    return s.strip()

def is_alignment_row(line: str) -> bool:
    parts = split_row(line)
    if not parts:
        return False
    def is_align_cell(c: str) -> bool:
        c = c.strip()
        return c != "" and all(ch in ":-" for ch in c)
    return all(is_align_cell(p) for p in parts)

def column_widths(md_table: str) -> list[int]:
    lines = [ln for ln in md_table.splitlines() if ln.strip()]
    if not lines:
        return []

    lines_wo_align = [ln for ln in lines if not is_alignment_row(ln)]

    rows = [split_row(ln) for ln in lines_wo_align]
    if not rows:
        return []

    max_cols = max(len(r) for r in rows)
    for r in rows:
        if len(r) < max_cols:
            r.extend([""] * (max_cols - len(r)))

    widths = [0] * max_cols
    for r in rows:
        for i, cell in enumerate(r):
            text = visible_text(cell)
            w = wcswidth(text)
            if w < 0:  # non-printables fallback
                w = len(text)
            widths[i] = max(widths[i], w)
    print(widths)
    return widths

# Example usage
if __name__ == "__main__":
    table = """
| Attribute Name      | Input Required | Read Only | Generated | Default Value | Notes                                                                                                       | Unique Values | Valid Values                                                              |
| ------------------- | -------------- | --------- | --------- | ------------- | ----------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------- |
| Display Name        | True           | True      | False     | None          | Name of the  definition.                                                                                    | False         |                                                                           |
| Summary             | False          | True      | False     | None          | Summary of the definition.                                                                                  | False         |                                                                           |
| Description         | False          | True      | False     | None          | Description of the contents of the definition.                                                              | False         |                                                                           |
| Category            | False          | True      | False     | None          | A user specified category name that can be used for example, to define product types or agreement types.    | False         |                                                                           |
"""

print(column_widths(table))  # e.g., [9, 28, 36] depending on characters