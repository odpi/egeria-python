import sys
import os
sys.path.append(os.path.abspath('../..'))

from md_processing.v2.parsing import AttributeFirstParser
from md_processing.v2.extraction import UniversalExtractor

with open('../../sample-data/egeria-inbox/dr-egeria-inbox/dr_egeria_intro_part2.md', 'r') as f:
    text = f.read()

extractor = UniversalExtractor(text)
commands = sorted(extractor.extract_commands(), key=lambda x: x.line_number)

for cmd in commands:
    if cmd.verb == "Update" and cmd.object_type == "Term":
        print("Raw Attributes:")
        for k, v in cmd.attributes.items():
            print(f"  {k}: {v}")
        
        parser = AttributeFirstParser(cmd)
        result = parser.parse()
        print("\nParsed Attributes:")
        for k, v in result.get("attributes", {}).items():
            print(f"  {k}: {v}")
        
        print("\nErrors:", result.get("errors"))
        print("Warnings:", result.get("warnings"))
        break
