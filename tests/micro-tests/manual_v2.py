import asyncio
from md_processing.dr_egeria import process_md_file_v2
import traceback

async def run():
    try:
        await process_md_file_v2('../../sample-data/egeria-inbox/dr-egeria-inbox/Flex.md', 'process', '')
        print("Success")
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(run())
