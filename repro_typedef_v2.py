from typing import Any

def _extract_typedef_list(payload: Any) -> list[dict]:
    """Normalize valid-metadata typedef payload variants to a list of typedef dicts."""
    entries: list[dict] = []
    seen_guids = set()

    def _collect(node: Any):
        if isinstance(node, list):
            for item in node:
                _collect(item)
        elif isinstance(node, dict):
            if "name" in node and isinstance(node.get("name"), str) and ("category" in node or "guid" in node):
                guid = node.get("guid", node.get("name"))
                if guid not in seen_guids:
                    entries.append(node)
                    seen_guids.add(guid)
            else:
                # Look for known containers
                found_container = False
                for key in ("typeDefList", "typeDefs", "elements", "typeDef"):
                    if key in node:
                        _collect(node[key])
                        found_container = True
                
                # If no known containers, maybe it's a map or a generic wrapper
                if not found_container:
                    for v in node.values():
                        if isinstance(v, (list, dict)):
                            _collect(v)

    _collect(payload)
    return entries

# Test cases
test_cases = [
    # Case 1: Direct list
    [{"name": "Entity1", "category": "C"}],
    # Case 2: Wrapped in list with keys
    {"typeDefs": [{"name": "Entity2", "category": "C"}]},
    # Case 3: Wrapped in typeDefList
    {"typeDefList": [{"name": "Entity3", "category": "C"}]},
    # Case 4: Wrapped in elements
    {"elements": [{"name": "Entity4", "category": "C"}]},
    # Case 5: Wrapped in dict but value is a dict (Map of Typedefs?)
    {"typeDefs": {"Entity5": {"name": "Entity5", "category": "C"}}},
    # Case 6: Empty payload
    {},
    # Case 7: Non-dict elements in list
    {"typeDefs": ["not-a-dict"]},
    # Case 8: Single Typedef
    {"name": "Entity8", "category": "ENTITY_DEF"},
    # Case 9: Single Typedef under key
    {"typeDef": {"name": "Entity9", "category": "ENTITY_DEF"}},
    # Case 10: Nested wrapper (The one we just found)
    {"typeDefList": {"typeDefs": [{"name": "Entity10", "category": "C"}]}},
]

for i, tc in enumerate(test_cases, 1):
    result = _extract_typedef_list(tc)
    print(f"Test {i}: Found {len(result)} items.")
    if result:
        print(f"  First: {result[0]['name']}")
