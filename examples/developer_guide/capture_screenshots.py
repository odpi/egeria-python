"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Regenerates the Developer Guide screenshots (docs/images/developer-guide/*.svg) by driving
   the example apps and the My Profile app headlessly with Textual's test Pilot.
   Needs a running Egeria (e.g. the egeria-workspaces quick start). Nothing is written to
   Egeria: the comment and bookmark dialogs are captured before they are submitted.

   Run:  python examples/developer_guide/capture_screenshots.py
"""

import asyncio
import sys
from pathlib import Path

from textual.app import App
from textual.pilot import Pilot
from textual.widgets import DataTable, Input

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]
IMAGES = REPO_ROOT / "docs" / "images" / "developer-guide"
MY_PROFILE_DIR = REPO_ROOT / "my_egeria" / "my_egeria" / "DemoCode" / "My_Profile"
SIZE = (150, 42)

sys.path.append(str(MY_PROFILE_DIR))


async def wait_for_table(pilot: Pilot, table: DataTable, timeout: float = 60.0) -> None:
    """Wait until a DataTable has finished loading and has rows."""
    for _ in range(int(timeout / 0.5)):
        await pilot.pause(0.5)
        if not table.loading and table.row_count:
            return


def save(app: App, name: str) -> None:
    app.save_screenshot(f"{name}.svg", path=str(IMAGES))
    print(f"saved {IMAGES / name}.svg")


async def capture_examples() -> None:
    from step2_glossary_browser import GlossaryBrowserApp
    from step3_glossary_comments import GlossaryCommentsApp

    app = GlossaryBrowserApp()
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_table(pilot, app.query_one(DataTable))
        await pilot.pause(4)  # let the "Loaded n glossaries" toast clear
        save(app, "step2_glossary_browser")

    app = GlossaryCommentsApp()
    async with app.run_test(size=SIZE) as pilot:
        await wait_for_table(pilot, app.query_one(DataTable))
        await pilot.pause(4)
        await pilot.press("down", "down", "ctrl+a")
        await pilot.pause()
        app.screen.query_one("#comment", Input).value = "Is this glossary still maintained?"
        await pilot.pause()
        save(app, "step3_add_comment")


async def capture_my_profile() -> None:
    from my_profile_app import MyProfileApp

    app = MyProfileApp()
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause(1)
        save(app, "my_profile_splash")

        await pilot.click("#continue")
        await wait_for_table(pilot, app.get_screen("main").query_one("#roles_table", DataTable))
        await pilot.pause(1)
        save(app, "my_profile_main")

        await app.handle_shop_for_data_option()
        await pilot.pause()
        for table_id in ("#glossary_table", "#data_dictionary_table"):
            await wait_for_table(pilot, app.screen.query_one(table_id, DataTable))
        await pilot.pause(1)
        save(app, "my_profile_shop_for_data")

        # Bookmark the highlighted glossary: Ctrl+B opens bookmarks, Ctrl+N shows the pre-filled GUID
        app.screen.query_one("#glossary_table", DataTable).focus()
        await pilot.press("down", "ctrl+b")
        await pilot.pause(2)
        await pilot.press("ctrl+n")
        await pilot.pause()
        save(app, "my_profile_bookmark_prefilled")


async def main() -> None:
    IMAGES.mkdir(parents=True, exist_ok=True)
    await capture_examples()
    await capture_my_profile()


if __name__ == "__main__":
    asyncio.run(main())
