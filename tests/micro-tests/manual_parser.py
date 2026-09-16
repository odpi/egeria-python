import asyncio
import sys
import os
sys.path.append(os.path.abspath('../..'))

from md_processing.v2.parsing import AttributeFirstParser
from md_processing.v2.extraction import UniversalExtractor

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INTRO_FILE = os.path.join(BASE_DIR, 'sample-data/egeria-inbox/dr-egeria-inbox/dr_egeria_intro_part2.md')

async def main():
    with open(INTRO_FILE, 'r') as f:
        text = f.read()

    extractor = UniversalExtractor(text)
    commands = sorted(extractor.extract_commands(), key=lambda x: x.start_line)

    for cmd in commands:
        if cmd.verb == "Update" and cmd.object_type == "Term":
            print("Raw Attributes:")
            for k, v in cmd.attributes.items():
                print(f"  {k}: {v}")
            
            parser = AttributeFirstParser(cmd)
            result = await parser.parse()
            print("\nParsed Attributes:")
            for k, v in result.get("attributes", {}).items():
                print(f"  {k}: {v}")
            
            print("\nErrors:", result.get("errors"))
            print("Warnings:", result.get("warnings"))
            break

if __name__ == "__main__":
    asyncio.run(main())
