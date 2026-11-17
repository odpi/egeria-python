"""
   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   Headless Recording Client for Egeria Coco Pharmaceuticals Business Value Series (Episodes 1-7).
   Drives the MyProfileApp headlessly across all 7 persona identities against the live Egeria
   Quickstart environment, executing specific scene workflows and capturing UI screens.

   Usage:
       uv run python my_egeria/my_egeria/recording/record_episode_screens.py --episode all
       uv run python my_egeria/my_egeria/recording/record_episode_screens.py --episode episode1
"""

import argparse
import asyncio
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List

from textual.app import App
from textual.pilot import Pilot
from textual.widgets import DataTable

try:
    import resvg_py
except ImportError:
    resvg_py = None

# Ensure paths are set
SCRIPT_DIR = Path(__file__).resolve().parent
MY_PROFILE_DIR = SCRIPT_DIR.parent
REPO_ROOT = MY_PROFILE_DIR.parents[1]

if str(MY_PROFILE_DIR) not in sys.path:
    sys.path.insert(0, str(MY_PROFILE_DIR))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from my_egeria.my_profile import MyProfileApp
from episode_specs import EPISODES, EpisodeSpec

DEFAULT_SIZE = (150, 42)
OUTPUT_BASE_DIR = SCRIPT_DIR / "output"


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


def save_screen_capture(app: App, filename: str, output_dir: Path) -> Path:
    """Save clean sanitized SVG screenshot and high-res PNG of current active screen."""
    output_dir.mkdir(parents=True, exist_ok=True)
    target_svg = output_dir / f"{filename}.svg"
    target_png = output_dir / f"{filename}.png"
    try:
        raw_svg = app.export_screenshot()
        clean_svg = sanitize_svg(raw_svg)
        target_svg.write_text(clean_svg, encoding="utf-8")
        if resvg_py:
            try:
                png_bytes = resvg_py.svg_to_bytes(svg_string=clean_svg, width=1800)
                target_png.write_bytes(png_bytes)
            except Exception as pe:
                print(f"      [WARN] PNG rasterization failed for {filename}: {pe}")
        print(f"      [CAPTURED SCREEN] {target_svg.name} (SVG + PNG)")
    except Exception as e:
        print(f"      [WARN] Screen export failed ({filename}): {e}")
    return target_svg


class EpisodeHeadlessRecorder:
    """Headless driver executing scene workflows for each business value episode."""

    def __init__(self, output_base: Path = OUTPUT_BASE_DIR):
        self.output_base = output_base

    async def _dismiss_splash_if_active(self, pilot: Pilot, app: MyProfileApp):
        """Wait for profile to load and dismiss splash screen."""
        await pilot.pause(2.0)
        if app.screen.__class__.__name__ == "SplashScreen":
            try:
                continue_btn = app.screen.query_one("#continue")
                if continue_btn:
                    await pilot.click("#continue")
            except Exception:
                await pilot.press("enter")
            await pilot.pause(2.0)

    # --------------------------------------------------------------------------
    # Episode 1: Faith Broker (Data Privacy & GDPR)
    # --------------------------------------------------------------------------
    async def record_episode1(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP1] Faith Broker - Data Privacy & GDPR Workflows...")
        await self._dismiss_splash_if_active(pilot, app)
        
        # Scene 2: Main Dashboard & Privacy Roles / Team Drill-down
        save_screen_capture(app, "ep1_scene2_01_dashboard", out_dir)
        try:
            main_screen = app.get_screen("main")
            roles_table = main_screen.query_one("#roles_table", DataTable)
            if roles_table:
                roles_table.focus()
                await pilot.pause(1.0)
                save_screen_capture(app, "ep1_scene2_02_privacy_roles", out_dir)
                # Drill down into My Team via enter on focused roles table
                await pilot.press("enter")
                await pilot.pause(2.0)
                save_screen_capture(app, "ep1_scene2_03_privacy_team", out_dir)
                await pilot.press("escape")
                await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep1 Scene 2 error: {e}")

        # Scene 3: SAR Lineage & Shop for Data / My Network
        try:
            await app.handle_shop_for_data_option()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep1_scene3_01_shop_for_data_pii", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)

            app.show_my_network()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep1_scene3_02_my_network_lineage", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep1 Scene 3 error: {e}")

        # Scene 4: Real-time Privacy Stewardship & Feedback
        try:
            app.show_my_bookmarks()
            await pilot.pause(1.5)
            save_screen_capture(app, "ep1_scene4_01_privacy_bookmarks", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)

            await app.action_feedback()
            await pilot.pause(1.5)
            save_screen_capture(app, "ep1_scene4_02_privacy_feedback", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep1 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Episode 2: Peter Profile (Zero-Touch Stewardship)
    # --------------------------------------------------------------------------
    async def record_episode2(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP2] Peter Profile - Zero-Touch Stewardship Workflows...")
        await self._dismiss_splash_if_active(pilot, app)

        # Scene 2: Interactive Stewardship & Table Editing
        save_screen_capture(app, "ep2_scene2_01_stewardship_dashboard", out_dir)
        try:
            main_screen = app.get_screen("main")
            roles_table = main_screen.query_one("#roles_table", DataTable)
            if roles_table:
                roles_table.focus()
                await pilot.pause(1.0)
                await pilot.press("ctrl+t")
                await pilot.pause(1.5)
                save_screen_capture(app, "ep2_scene2_02_edit_table_dialog", out_dir)
                await pilot.press("escape")
                await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep2 Scene 2 error: {e}")

        # Scene 3: Threaded Discussions & Asset Bookmarking
        try:
            roles_table = app.screen.query_one("#roles_table", DataTable)
            if roles_table:
                roles_table.focus()
                await pilot.press("ctrl+o")
                await pilot.pause(1.5)
                save_screen_capture(app, "ep2_scene3_01_view_comments", out_dir)
                await pilot.press("escape")
                await pilot.pause(1.0)

            app.show_my_bookmarks()
            await pilot.pause(1.5)
            save_screen_capture(app, "ep2_scene3_02_stewardship_bookmarks", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep2 Scene 3 error: {e}")

        # Scene 4: Automated Housekeeping & Karma Recognition
        try:
            app.show_communities()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep2_scene4_01_communities_karma", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep2 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Episode 3: Dr. Tessa Tube (Clinical Data Provenance & Subscriptions)
    # --------------------------------------------------------------------------
    async def record_episode3(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP3] Dr. Tessa Tube - Clinical Data Provenance Workflows...")
        await self._dismiss_splash_if_active(pilot, app)

        # Scene 2: Clinical Data Product Exploration
        save_screen_capture(app, "ep3_scene2_01_clinical_dashboard", out_dir)
        try:
            await app.handle_shop_for_data_option()
            await pilot.pause(2.5)
            save_screen_capture(app, "ep3_scene2_02_data_products_catalog", out_dir)

            # Scene 3: Sample Data (Ctrl+L) & Create Subscription (Ctrl+U)
            try:
                glossary_table = app.screen.query_one("#glossary_table", DataTable)
                if glossary_table:
                    glossary_table.focus()
                    await pilot.press("ctrl+l")
                    await pilot.pause(1.5)
                    save_screen_capture(app, "ep3_scene3_01_sample_data_preview", out_dir)
                    await pilot.press("escape")
                    await pilot.pause(1.0)

                    await pilot.press("ctrl+u")
                    await pilot.pause(1.5)
                    save_screen_capture(app, "ep3_scene3_02_subscription_contract", out_dir)
                    await pilot.press("escape")
                    await pilot.pause(1.0)
            except Exception:
                pass

            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep3 Scene 2/3 error: {e}")

        # Scene 4: Verifying Data Lineage & Active Subscriptions
        try:
            await app.push_screen("view_subscriptions")
            await pilot.pause(2.0)
            save_screen_capture(app, "ep3_scene4_01_active_subscriptions", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)

            app.show_my_network()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep3_scene4_02_clinical_lineage_graph", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep3 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Episode 4: Stew Faster (Supply Chain & ESG Sustainability)
    # --------------------------------------------------------------------------
    async def record_episode4(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP4] Stew Faster - Supply Chain & ESG Sustainability Workflows...")
        await self._dismiss_splash_if_active(pilot, app)

        # Scene 2: Technology Types & Operational Catalogs
        save_screen_capture(app, "ep4_scene2_01_manufacturing_dashboard", out_dir)
        try:
            await app.push_screen("tech_types")
            await pilot.pause(2.0)
            save_screen_capture(app, "ep4_scene2_02_technology_types", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep4 Scene 2 error: {e}")

        # Scene 3: Supply Chain Data Products & Carbon Footprint
        try:
            await app.handle_shop_for_data_option()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep4_scene3_01_supply_chain_catalog", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep4 Scene 3 error: {e}")

        # Scene 4: Collaborative Quality Management & Sustainability Circles
        try:
            app.show_communities()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep4_scene4_01_sustainability_community", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)

            await app.action_feedback()
            await pilot.pause(1.5)
            save_screen_capture(app, "ep4_scene4_02_operational_feedback", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep4 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Episode 5: Erin Overview (Glossaries & Architecture)
    # --------------------------------------------------------------------------
    async def record_episode5(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP5] Erin Overview - Information Architecture & Glossaries...")
        await self._dismiss_splash_if_active(pilot, app)

        # Scene 2: Exploring Business Domains & Glossaries
        save_screen_capture(app, "ep5_scene2_01_architecture_dashboard", out_dir)
        try:
            await app.handle_shop_for_data_option()
            await pilot.pause(2.5)
            save_screen_capture(app, "ep5_scene2_02_business_glossaries", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep5 Scene 2 error: {e}")

        # Scene 3: Search for Term & Schema Mappings
        try:
            await app.push_screen("search_for_term")
            await pilot.pause(2.0)
            save_screen_capture(app, "ep5_scene3_01_search_for_term_mapping", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep5 Scene 3 error: {e}")

        # Scene 4: Visualizing Cross-Domain Network Graphs
        try:
            app.show_my_network()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep5_scene4_01_cross_domain_knowledge_graph", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep5 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Episode 6: Sidney Seeker (Forensic Auditing & Fraud)
    # --------------------------------------------------------------------------
    async def record_episode6(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP6] Sidney Seeker - Forensic Data Auditing & Lineage...")
        await self._dismiss_splash_if_active(pilot, app)

        # Scene 2: Inspecting Audit Trails & Activity Journals
        save_screen_capture(app, "ep6_scene2_01_forensic_dashboard", out_dir)

        # Scene 3: Tracing Financial Lineage in My Network
        try:
            app.show_my_network()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep6_scene3_01_forensic_lineage_graph", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep6 Scene 3 error: {e}")

        # Scene 4: Incident Remediation & Cross-Functional Feedback
        try:
            await app.action_feedback()
            await pilot.pause(1.5)
            save_screen_capture(app, "ep6_scene4_01_incident_audit_feedback", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep6 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Episode 7: Jules Keeper (Executive Cockpit & Governance ROI)
    # --------------------------------------------------------------------------
    async def record_episode7(self, pilot: Pilot, app: MyProfileApp, out_dir: Path):
        print("    [EP7] Jules Keeper - Executive Cockpit & Governance ROI...")
        await self._dismiss_splash_if_active(pilot, app)

        # Scene 2: Executive Dashboard & Leadership Alignment
        save_screen_capture(app, "ep7_scene2_01_executive_dashboard", out_dir)
        try:
            main_screen = app.get_screen("main")
            roles_table = main_screen.query_one("#roles_table", DataTable)
            if roles_table:
                roles_table.focus()
                await pilot.pause(1.0)
                await pilot.press("enter")
                await pilot.pause(2.0)
                save_screen_capture(app, "ep7_scene2_02_executive_leadership_team", out_dir)
                await pilot.press("escape")
                await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep7 Scene 2 error: {e}")

        # Scene 3: Measuring Catalog Adoption & Stewardship ROI
        try:
            app.show_communities()
            await pilot.pause(2.0)
            save_screen_capture(app, "ep7_scene3_01_enterprise_karma_leaderboard", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep7 Scene 3 error: {e}")

        # Scene 4: Governance Action Engine Telemetry
        try:
            await app.push_screen("tech_types")
            await pilot.pause(2.0)
            save_screen_capture(app, "ep7_scene4_01_governance_engine_telemetry", out_dir)
            await pilot.press("escape")
            await pilot.pause(1.0)
        except Exception as e:
            print(f"      [WARN] Ep7 Scene 4 error: {e}")

    # --------------------------------------------------------------------------
    # Master Dispatcher
    # --------------------------------------------------------------------------
    async def record_episode_by_id(self, episode_id: str) -> None:
        if episode_id not in EPISODES:
            print(f"[ERROR] Unknown episode: {episode_id}")
            return
        ep = EPISODES[episode_id]
        ep_dir = self.output_base / episode_id / "captures"
        global_captures = self.output_base / "captures"
        ep_dir.mkdir(parents=True, exist_ok=True)
        global_captures.mkdir(parents=True, exist_ok=True)

        print(f"\n================================================================================")
        print(f"HEADLESS CLIENT RECORDING: EPISODE {ep.episode_number} ({ep.lead_persona} - {ep.persona_username})")
        print(f"================================================================================")

        app = MyProfileApp()
        app.user_name = ep.persona_username
        
        handler_name = f"record_{episode_id}"
        handler = getattr(self, handler_name, None)

        if not handler:
            print(f"[ERROR] No handler found for {episode_id}")
            return

        async with app.run_test(size=DEFAULT_SIZE) as pilot:
            await handler(pilot, app, ep_dir)

        print(f"✓ Completed headless captures for Episode {ep.episode_number} in {ep_dir}")

    async def record_all(self) -> None:
        for ep_id in ["episode1", "episode2", "episode3", "episode4", "episode5", "episode6", "episode7"]:
            await self.record_episode_by_id(ep_id)


def parse_args():
    parser = argparse.ArgumentParser(description="Record Headless Episode Terminal Screens for Egeria Video Series")
    parser.add_argument(
        "--episode",
        choices=["all", "episode1", "episode2", "episode3", "episode4", "episode5", "episode6", "episode7"],
        default="all",
        help="Specify which episode to record (default: all)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    recorder = EpisodeHeadlessRecorder()
    if args.episode == "all":
        asyncio.run(recorder.record_all())
    else:
        asyncio.run(recorder.record_episode_by_id(args.episode))


if __name__ == "__main__":
    main()
