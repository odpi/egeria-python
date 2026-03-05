import json
from collections import Counter

with open("../md_processing/data/commands/commands_governance.json") as f:
    data = json.load(f)

specs = data["Command Specifications"]
attr_sets = {}
all_attrs = Counter()

for name, spec in specs.items():
    if spec.get("verb") == "Create":
        attrs = [list(a.keys())[0] for a in spec.get("Attributes", [])]
        for a in attrs:
            all_attrs[a] += 1
        attr_sets[name] = attrs

print("### Attribute Frequency (Governance Create Commands)")
for attr, count in all_attrs.most_common():
    print(f"- {attr}: {count}")

print("\n### Common Attribute Sets")
sets = {}
for name, attrs in attr_sets.items():
    s = tuple(sorted(attrs))
    sets.setdefault(s, []).append(name)

for s, names in sets.items():
    print(f"\nSet: {s}")
    print(f"Commands: {', '.join(names)}")
