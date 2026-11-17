"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Automated Textual Pilot Demo Recorder for My Profile (Callie Quartile Video Script).
   Drives the application headlessly through all 6 video scenes and generates
   timestamped, high-resolution SVG screenshots for video assets, slides, and documentation.

   Usage:
       python my_egeria/my_egeria/recording/record_demo.py
       python my_egeria/my_egeria/recording/record_demo.py --scene 5
       python my_egeria/my_egeria/recording/record_demo.py --output-dir ./custom_captures
"""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path

from textual.app import App
from textual.pilot import Pilot
from textual.widgets import DataTable, Input, OptionList

# Ensure my_profile package path is available
RECORDING_DIR = Path(__file__).resolve().parent
MY_PROFILE_DIR = RECORDING_DIR.parent
REPO_ROOT = MY_PROFILE_DIR.parents[1]

if str(MY_PROFILE_DIR) not in sys.path:
    sys.path.insert(0, str(MY_PROFILE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from my_egeria.my_profile import MyProfileApp

DEFAULT_SIZE = (150, 42)
DEFAULT_OUTPUT_DIR = RECORDING_DIR / "output" / "captures"


async def wait_for_table(pilot: Pilot, table: DataTable, timeout: float = 30.0) -> bool:
    """Wait until a DataTable has finished loading and populated rows (or timed out)."""
    for _ in range(int(timeout / 0.5)):
        await pilot.pause(0.5)
        if not table.loading:
            return True
    return False


BOX_CHARS = set("╭╮╯╰│─┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬━┃┏┓┗┛┣┫┳┻╋")

EXTRA_SVG_STYLES = """
    .term-border { fill: #89b4fa !important; font-weight: normal; }
    .term-header-title { fill: #89b4fa !important; font-weight: bold; }
    .term-section-title { fill: #cba6f7 !important; font-weight: bold; }
    .term-table-header { fill: #74c7ec !important; font-weight: bold; }
    .term-gold { fill: #f9e2af !important; font-weight: bold; }
    .term-green { fill: #a6e3a1 !important; font-weight: bold; }
    .term-peach { fill: #fab387 !important; font-weight: bold; }
    .term-red { fill: #f38ba8 !important; font-weight: bold; }
    .term-sky { fill: #74c7ec !important; font-weight: bold; }
    .term-white { fill: #cdd6f4 !important; }
"""

CATPPUCCIN_MOCHA_MAP = {
    r"#0178d4\b": "#89b4fa",  # Sapphire / Blue
    r"#004578\b": "#74c7ec",  # Sky
    r"#004854\b": "#cba6f7",  # Mauve
    r"#00008b\b": "#89b4fa",  # Dark Blue -> Blue
    r"#28c840\b": "#a6e3a1",  # Green
    r"#febc2e\b": "#f9e2af",  # Yellow
    r"#ff5f57\b": "#f38ba8",  # Red
}

KNOWN_SECTIONS = [
    "User Associations", "My Collections", "Other Functions", "Roles", "Teams",
    "Blogs", "Journal", "To-Dos", "User Identity", "Projects", "Select a function",
    "Shop for Data", "My Network", "Work with Communities", "User Bookmarks",
    "Leave Feedback", "Feedback Log", "Subscriptions", "Catalogs/Shop for Data",
    "Technology Types", "Edit Profile", "Change User", "Peer Details", "People Search",
    "Community Details", "Active Communities", "Joined Communities", "Available Roles",
    "Catalog Search", "Digital Data Products", "Data Dictionaries", "Business Domains"
]


def sanitize_svg(svg_content: str) -> str:
    """Sanitize Textual/Rich SVG export to fix typography, character spacing, and full TrueColor colors."""
    # 1. Remove font-variant-east-asian: full-width (which forces double spacing)
    svg = re.sub(r"font-variant-east-asian:\s*full-width;?", "", svg_content)

    # 2. Embed JetBrains Mono webfont & vibrant TrueColor styling
    jb_font = f"""
    @font-face {{
        font-family: "JetBrains Mono";
        src: local("JetBrainsMono-Regular"), local("JetBrains Mono"),
             url("https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono/web/woff2/JetBrainsMono-Regular.woff2") format("woff2");
        font-style: normal;
        font-weight: 400;
    }}
    @font-face {{
        font-family: "JetBrains Mono";
        src: local("JetBrainsMono-Bold"), local("JetBrains Mono-Bold"),
             url("https://cdn.jsdelivr.net/gh/JetBrains/JetBrainsMono/web/woff2/JetBrainsMono-Bold.woff2") format("woff2");
        font-style: bold;
        font-weight: 700;
    }}
{EXTRA_SVG_STYLES}
"""
    if "<style>" in svg and "JetBrains Mono" not in svg:
        svg = svg.replace("<style>", f"<style>{jb_font}")

    # 3. Update font-family rule in matrix classes
    svg = re.sub(
        r"font-family:\s*Fira Code,\s*monospace;",
        'font-family: "JetBrains Mono", "Fira Code", Menlo, Monaco, "Courier New", monospace; letter-spacing: normal;',
        svg,
    )

    # 4. Standardize dark panel & container background fills
    svg = re.sub(r'fill="#121212"', 'fill="#181825"', svg)
    svg = re.sub(r'fill="#191919"', 'fill="#1e1e2e"', svg)
    svg = re.sub(r'fill="#000000"', 'fill="#11111b"', svg)
    svg = re.sub(r'fill="#282828"', 'fill="#313244"', svg)

    # 5. Semantic text colorization for rich visual elements
    def colorize_text_element(match):
        full_tag = match.group(0)
        attrs = match.group(1)
        content = match.group(2)

        def replace_class(target_class):
            if 'class="' in attrs:
                new_attrs = re.sub(r'class="[^"]*"', f'class="{target_class}"', attrs)
            else:
                new_attrs = f'class="{target_class}" {attrs}'
            return f'<text {new_attrs}>{content}</text>'

        clean_content = content.replace("&#160;", " ").strip()

        # Check box drawing border
        if clean_content and all(c in BOX_CHARS or c == " " for c in clean_content):
            return replace_class("term-border")

        # Check Header / Egeria title
        if clean_content == "Egeria":
            return replace_class("term-header-title")

        # Check section headings
        if any(sec in clean_content for sec in KNOWN_SECTIONS):
            return replace_class("term-section-title")

        # Check Karma points, clocks, numbers
        if "Karma Points" in clean_content or re.search(r"\b\d{2}:\d{2}:\d{2}\b", clean_content):
            return replace_class("term-gold")

        # Check badges / status indicators
        if "●" in clean_content or clean_content in ["Active", "Done", "Approved", "Valid"]:
            return replace_class("term-green")
        if "⭘" in clean_content or clean_content in ["Pending", "In Progress", "Draft"]:
            return replace_class("term-gold")
        if clean_content in ["Restricted", "Confidential", "High", "Critical", "Error"]:
            return replace_class("term-red")

        # Check hotkeys
        if re.search(r"\[(Ctrl\+[A-Z]|Enter|Esc|Space)\]", clean_content):
            return replace_class("term-peach")

        # Check buttons
        if clean_content in ["Continue", "Change User", "Close", "Cancel", "Submit", "Edit"]:
            return replace_class("term-green")

        # Check table headers
        if clean_content in ["Role Name", "Team Name", "Project Name", "Association", "Collection", "User Name", "Action", "Target", "Status", "Date", "Type", "Scope", "Access"]:
            return replace_class("term-table-header")

        return full_tag

    svg = re.sub(r"<text([^>]*)>(.*?)</text>", colorize_text_element, svg)

    # 6. Apply fallback palette translations
    for pattern, replacement in CATPPUCCIN_MOCHA_MAP.items():
        svg = re.sub(pattern, replacement, svg, flags=re.IGNORECASE)

    return svg


def save_screenshot(app: App, filename: str, output_dir: Path) -> Path:
    """Save a clean, sanitized SVG screenshot of the current active screen."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{filename}.svg"
    raw_svg = app.export_screenshot()
    clean_svg = sanitize_svg(raw_svg)
    target.write_text(clean_svg, encoding="utf-8")
    print(f"  [SAVED SVG] {target}")
    return target


async def record_scene_2_launch(pilot: Pilot, app: MyProfileApp, output_dir: Path) -> None:
    """Scene 2: Splash screen, async loading, and navigation into main."""
    print("\n--- Recording Scene 2: Launch & Background Startup ---")
    await pilot.pause(1.5)
    save_screenshot(app, "scene2_01_splash_screen", output_dir)

    # Click continue button to enter main dashboard
    continue_btn = app.screen.query_one("#continue")
    if continue_btn:
        await pilot.click("#continue")
    await pilot.pause(2.0)
    save_screenshot(app, "scene2_02_main_dashboard_loaded", output_dir)


async def record_scene_3_dashboard(pilot: Pilot, app: MyProfileApp, output_dir: Path) -> None:
    """Scene 3: Main dashboard tour, roles & team drill-down."""
    print("\n--- Recording Scene 3: Main Dashboard Tour ---")
    await pilot.pause(1.0)
    save_screenshot(app, "scene3_01_dashboard_overview", output_dir)

    # Focus and inspect Roles table
    main_screen = app.get_screen("main")
    roles_table = main_screen.query_one("#roles_table", DataTable)
    if roles_table:
        roles_table.focus()
        await pilot.pause(1.0)
        save_screenshot(app, "scene3_02_roles_and_teams", output_dir)

        # Drill down into My Team if team role is available
        try:
            await app.handle_roles_table_selection(None)
            await pilot.pause(2.0)
            save_screenshot(app, "scene3_03_my_team_screen", output_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception:
            pass


async def record_scene_4_curation(pilot: Pilot, app: MyProfileApp, output_dir: Path) -> None:
    """Scene 4: Real-time curation - To-Dos editing, comments, and bookmarks."""
    print("\n--- Recording Scene 4: Real-Time Curation ---")
    main_screen = app.get_screen("main")

    # 1. Edit To-Dos Table (Ctrl+T)
    todos_table = main_screen.query_one("#todos_table", DataTable)
    if todos_table:
        todos_table.focus()
        await pilot.pause(0.5)
        await pilot.press("ctrl+t")
        await pilot.pause(1.5)
        save_screenshot(app, "scene4_01_edit_todos_dialog", output_dir)
        await pilot.press("escape")
        await pilot.pause(1.0)

    # 2. View Comments (Ctrl+O)
    roles_table = main_screen.query_one("#roles_table", DataTable)
    if roles_table:
        roles_table.focus()
        await pilot.press("ctrl+o")
        await pilot.pause(1.5)
        save_screenshot(app, "scene4_02_view_comments_screen", output_dir)
        await pilot.press("escape")
        await pilot.pause(1.0)

    # 3. Add Comment (Ctrl+N)
    if roles_table:
        roles_table.focus()
        await pilot.press("ctrl+n")
        await pilot.pause(1.5)
        save_screenshot(app, "scene4_03_add_comment_modal", output_dir)
        await pilot.press("escape")
        await pilot.pause(1.0)

    # 4. View Bookmarks Screen (Ctrl+B)
    await pilot.press("ctrl+b")
    await pilot.pause(1.5)
    save_screenshot(app, "scene4_04_my_bookmarks_screen", output_dir)
    await pilot.press("escape")
    await pilot.pause(1.0)


async def record_scene_5_shop_for_data(pilot: Pilot, app: MyProfileApp, output_dir: Path) -> None:
    """Scene 5: Hero Workflow - Catalogs/Shop for Data, sample data, and subscribe."""
    print("\n--- Recording Scene 5: Shop for Governed Data Products ---")
    await app.handle_shop_for_data_option()
    await pilot.pause(2.5)
    save_screenshot(app, "scene5_01_shop_for_data_overview", output_dir)

    # Focus glossary table
    try:
        glossary_table = app.screen.query_one("#glossary_table", DataTable)
        if glossary_table:
            glossary_table.focus()
            await pilot.pause(1.0)
            save_screenshot(app, "scene5_02_catalog_selection", output_dir)

            # Sample Data dialog (Ctrl+L)
            await pilot.press("ctrl+l")
            await pilot.pause(2.0)
            save_screenshot(app, "scene5_03_sample_data_modal", output_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)

            # Create Subscription Request modal (Ctrl+U)
            await pilot.press("ctrl+u")
            await pilot.pause(1.5)
            save_screenshot(app, "scene5_04_create_subscription_modal", output_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
    except Exception as e:
        print(f"  [NOTE] Shop for data sub-screens: {e}")

    await pilot.press("escape")
    await pilot.pause(1.0)


async def record_scene_6_collaboration(pilot: Pilot, app: MyProfileApp, output_dir: Path) -> None:
    """Scene 6: My Network graph, communities, feedback, and technology types."""
    print("\n--- Recording Scene 6: Collaboration, Networks & Feedback ---")

    # 1. My Network Graph
    try:
        if hasattr(app, "show_my_network"):
            app.show_my_network()
            await pilot.pause(2.5)
            save_screenshot(app, "scene6_01_my_network_graph", output_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
    except Exception as e:
        print(f"  [NOTE] My Network: {e}")

    # 2. Work with Communities
    try:
        if hasattr(app, "show_communities"):
            app.show_communities()
            await pilot.pause(2.0)
            save_screenshot(app, "scene6_02_communities_screen", output_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
    except Exception as e:
        print(f"  [NOTE] Communities: {e}")

    # 3. In-App Feedback Dialog (Ctrl+F)
    await pilot.press("ctrl+f")
    await pilot.pause(1.5)
    save_screenshot(app, "scene6_03_leave_feedback_modal", output_dir)
    await pilot.press("escape")
    await pilot.pause(1.0)

    # 4. Technology Types Screen
    try:
        if hasattr(app, "handle_technology_types_option"):
            await app.handle_technology_types_option()
            await pilot.pause(2.0)
            save_screenshot(app, "scene6_04_technology_types_screen", output_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
    except Exception as e:
        print(f"  [NOTE] Technology Types: {e}")


async def run_full_recording(target_scene: int | None, output_dir: Path) -> None:
    """Execute the full demo recording session using Textual pilot."""
    os.environ.pop("NO_COLOR", None)
    os.environ["FORCE_COLOR"] = "1"
    os.environ["COLORTERM"] = "truecolor"
    os.environ["TERM"] = "xterm-256color"
    os.environ.setdefault("EGERIA_USER_NAME", "calliequartile")
    app = MyProfileApp()

    async with app.run_test(size=DEFAULT_SIZE) as pilot:
        # Scene 2 is always run first to advance past the splash screen
        await record_scene_2_launch(pilot, app, output_dir)

        if target_scene in (None, 3):
            await record_scene_3_dashboard(pilot, app, output_dir)

        if target_scene in (None, 4):
            await record_scene_4_curation(pilot, app, output_dir)

        if target_scene in (None, 5):
            await record_scene_5_shop_for_data(pilot, app, output_dir)

        if target_scene in (None, 6):
            await record_scene_6_collaboration(pilot, app, output_dir)

    print(f"\n[COMPLETE] All captures generated in: {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated Video Demo Pilot Recorder for My Profile")
    parser.add_argument("--scene", type=int, choices=[2, 3, 4, 5, 6], default=None,
                        help="Record a specific scene (default: all scenes)")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help="Directory to save output SVG screenshots")
    args = parser.parse_args()

    asyncio.run(run_full_recording(args.scene, args.output_dir))


if __name__ == "__main__":
    main()
