import os
import uuid
import asyncio
from md_processing.dr_egeria import process_md_file_v2
from rich.console import Console

console = Console()
async def run():
    await process_md_file_v2("../../sample-data/egeria-inbox/dr-egeria-inbox/Flex.md", "process")

if __name__ == "__main__":
    asyncio.run(run())
