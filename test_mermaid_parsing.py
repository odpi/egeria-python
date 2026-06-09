
from pyegeria.view.mermaid_utilities import parse_mermaid_code

mermaid_input = """--- title: Test Graph [12345] ---
```mermaid
flowchart TD
    A --> B
```
"""

title, guid, code = parse_mermaid_code(mermaid_input)
print(f"Title: {title}")
print(f"GUID: {guid}")
print(f"Code:\n{code}")
