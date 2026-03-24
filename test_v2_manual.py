import sys
import os

print("Starting test_v2_manual.py", flush=True)

try:
    from pyegeria import EgeriaTech
    import asyncio
    from md_processing.dr_egeria import process_md_file_v2
    print("Imports successful", flush=True)

    client = EgeriaTech('cocoMDS2', 'https://192.168.0.222:39443', 'erinoverview', 'secret')
    print("Client created", flush=True)

    async def main():
        print("Inside main async run", flush=True)
        try:
            input_file = 'sample-data/egeria-inbox/dr-egeria-inbox/Flex.md'
            await process_md_file_v2(input_file, '', 'process', client)
            print("process_md_file_v2 returned", flush=True)
        except Exception as e:
            print(f"Exception inside main: {e}", flush=True)
            import traceback
            traceback.print_exc()

    print("Running asyncio", flush=True)
    asyncio.run(main())
    print("Asyncio finished", flush=True)
except Exception as e:
    print(f"Global exception: {e}", flush=True)
    import traceback
    traceback.print_exc()

print("Finished test_v2_manual.py", flush=True)
