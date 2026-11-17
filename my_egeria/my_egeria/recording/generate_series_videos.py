#!/usr/bin/env python3
"""
Egeria Coco Pharmaceuticals Business Value Video Series Generator.

Generates 1080p slide cards, synthesized neural voiceovers with distinct persona
accents and voices, VHS terminal interaction tapes, and assembled narrated MP4 videos
for Episodes 1 through 7 of the Coco Pharmaceuticals Business Value Series.

Prerequisites:
    - uv pip install edge-tts Pillow textual
    - brew install vhs ffmpeg ttyd (optional for VHS raster captures)
"""

import argparse
import asyncio
import io
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict

import edge_tts
from PIL import Image, ImageDraw, ImageFont

try:
    import resvg_py
except ImportError:
    resvg_py = None

from episode_specs import EPISODES, EpisodeSpec, SceneSpec
from export_vault import export_to_vault

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"
SLIDES_DIR = OUTPUT_DIR / "slides"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEOS_DIR = OUTPUT_DIR / "videos"
NARRATED_DIR = OUTPUT_DIR / "videos_narrated"
CAPTURES_DIR = OUTPUT_DIR / "captures"
TAPES_DIR = SCRIPT_DIR / "tapes"


def slugify(text: str) -> str:
    """Convert text into a filesystem-safe lowercase slug."""
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "_", text)


class AudioSynthesizer:
    """Generates speech audio using Microsoft Azure Neural TTS (via edge-tts) or macOS say."""

    def __init__(self, audio_dir: Path):
        self.audio_dir = audio_dir
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    async def _synth_edge_tts(self, text: str, voice: str, output_path: Path):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(output_path))

    def synthesize_scene(self, scene: SceneSpec, episode: EpisodeSpec, output_path: Path):
        """Synthesize dialogue for a single scene with the specified persona voice."""
        voice = scene.voice or episode.voice_name
        print(f"    [TTS] {scene.speaker} ({episode.voice_accent}) -> {output_path.name}")
        try:
            asyncio.run(self._synth_edge_tts(scene.dialogue, voice, output_path))
        except Exception as e:
            print(f"    [WARN] Edge-TTS error ({e}), falling back to macOS 'say'...")
            self._synth_macos_say(scene.dialogue, episode.offline_say_voice, output_path)

    def _synth_macos_say(self, text: str, voice: str, output_path: Path):
        aiff_path = output_path.with_suffix(".aiff")
        subprocess.run(["say", "-v", voice, "-o", str(aiff_path), text], check=True)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(aiff_path),
                "-codec:a",
                "libmp3lame",
                "-qscale:a",
                "2",
                str(output_path),
            ],
            capture_output=True,
            check=True,
        )
        if aiff_path.exists():
            aiff_path.unlink()

    def stitch_full_audio(self, scene_mp3s: List[Path], output_path: Path):
        """Stitch individual scene MP3 files into a continuous episode audio track."""
        filter_inputs = "".join(f"[{i}:0]" for i in range(len(scene_mp3s)))
        filter_complex = f"{filter_inputs}concat=n={len(scene_mp3s)}:v=0:a=1[a]"
        cmd = ["ffmpeg", "-y"]
        for p in scene_mp3s:
            cmd.extend(["-i", str(p)])
        cmd.extend(
            [
                "-filter_complex",
                filter_complex,
                "-map",
                "[a]",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(output_path),
            ]
        )
        subprocess.run(cmd, capture_output=True, check=True)


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


class SlideRenderer:
    """Renders 1080p high-resolution slide cards with Catppuccin Mocha aesthetic."""

    def __init__(self, slides_dir: Path):
        self.slides_dir = slides_dir
        self.slides_dir.mkdir(parents=True, exist_ok=True)

    def _get_font(self, size: int, bold: bool = False):
        font_names = (
            [
                "/System/Library/Fonts/SFPro-Bold.ttf",
                "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                "/System/Library/Fonts/HelveticaNeue.ttc",
            ]
            if bold
            else [
                "/System/Library/Fonts/SFPro-Regular.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
            ]
        )
        for font_path in font_names:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except Exception:
                    continue
        return ImageFont.load_default()

    def render_slide(self, scene: SceneSpec, episode: EpisodeSpec, output_path: Path):
        """Render a single 1080p slide card for presentation scenes."""
        width, height = 1920, 1080
        img = Image.new("RGB", (width, height), color=(30, 30, 46))  # Base Dark
        draw = ImageDraw.Draw(img)

        # Subtle Grid / Background Accents
        draw.rectangle([(0, 0), (1920, 12)], fill=(203, 166, 247))  # Mauve top accent
        draw.rounded_rectangle([(80, 60), (1840, 1020)], radius=24, fill=(24, 24, 37), outline=(49, 50, 68), width=2)

        # Brand Bar & Persona Badge
        draw.rectangle([(140, 95), (148, 140)], fill=(137, 180, 250))  # Blue Tag
        font_brand = self._get_font(24, bold=True)
        draw.text((165, 102), f"COCO PHARMACEUTICALS • BUSINESS VALUE SERIES • EPISODE {episode.episode_number}", fill=(186, 194, 222), font=font_brand)

        # Persona Badge Top Right
        badge_text = f"Persona: {episode.lead_persona} ({episode.persona_role})"
        font_badge = self._get_font(18, bold=True)
        draw.text((1200, 104), badge_text, fill=(166, 227, 161), font=font_badge)

        # Slide Title & Subtitle
        title = scene.slide_title or f"EPISODE {episode.episode_number}: {scene.title.upper()}"
        subtitle = scene.slide_subtitle or episode.subtitle
        font_title = self._get_font(48, bold=True)
        font_sub = self._get_font(24)
        font_body = self._get_font(22)
        font_box_header = self._get_font(22, bold=True)
        font_box_content = self._get_font(21)
        font_footer = self._get_font(16)

        draw.text((140, 170), title, fill=(205, 214, 244), font=font_title)
        draw.text((140, 235), subtitle, fill=(137, 180, 250), font=font_sub)

        # Spoken Dialogue Overview Box
        dialogue_preview = scene.dialogue
        if len(dialogue_preview) > 340:
            dialogue_preview = dialogue_preview[:337] + "..."

        curr_y = 290
        # Wrap dialogue preview text
        words = dialogue_preview.split(" ")
        line = ""
        for word in words:
            test_line = line + (" " if line else "") + word
            bbox = font_body.getbbox(test_line)
            if bbox[2] > 1600:
                draw.text((140, curr_y), line, fill=(186, 194, 222), font=font_body)
                curr_y += 34
                line = word
            else:
                line = test_line
        if line:
            draw.text((140, curr_y), line, fill=(186, 194, 222), font=font_body)
            curr_y += 34

        # Key Highlights Box (Dynamic Height for multi-line bullets)
        if scene.callouts:
            line_height = 40
            num_callouts = len(scene.callouts)
            box_content_height = 40 + (num_callouts * line_height)
            box_height = max(box_content_height + 40, 180)
            box_y1 = min(max(curr_y + 35, 520), 920 - box_height)
            box_y2 = box_y1 + box_height

            draw.rounded_rectangle([(140, box_y1), (1780, box_y2)], radius=16, fill=(17, 17, 27), outline=(69, 71, 90), width=2)
            draw.text((180, box_y1 + 22), "STRATEGIC HIGHLIGHTS & GOVERNANCE VALUE:", fill=(166, 227, 161), font=font_box_header)

            callout_y = box_y1 + 68
            for item in scene.callouts:
                draw.text((180, callout_y), f"•  {item}", fill=(249, 226, 175), font=font_box_content)
                callout_y += line_height

        # Footer
        footer_text = f"Egeria Open Metadata Governance • {episode.business_driver} • Voice: {episode.voice_name} ({episode.voice_accent})"
        draw.text((140, 960), footer_text, fill=(108, 112, 134), font=font_footer)

        img.save(str(output_path), "PNG", quality=95)

    def render_terminal_screenshot_frame(
        self,
        capture_path: Path,
        scene: SceneSpec,
        episode: EpisodeSpec,
        output_path: Path,
        frame_idx: int = 0,
        total_frames: int = 1,
    ):
        """Render a 1080p frame featuring a live Textual UI screenshot with Catppuccin theme."""
        term_img: Optional[Image.Image] = None
        # Prefer companion SVG if available to ensure full Catppuccin Mocha TrueColor sanitization
        svg_file = capture_path if capture_path.suffix.lower() == ".svg" else capture_path.with_suffix(".svg")
        if svg_file.exists():
            clean_svg = sanitize_svg(svg_file.read_text(encoding="utf-8"))
            if resvg_py:
                try:
                    png_bytes = resvg_py.svg_to_bytes(svg_string=clean_svg, width=1800)
                    term_img = Image.open(io.BytesIO(png_bytes))
                except Exception as e:
                    print(f"      [WARN] resvg conversion failed for {svg_file.name}: {e}")
            if term_img is None:
                tmp_svg = output_path.with_suffix(".tmp.svg")
                tmp_png = output_path.with_suffix(".tmp.png")
                try:
                    tmp_svg.write_text(clean_svg, encoding="utf-8")
                    subprocess.run(
                        ["qlmanage", "-t", "-s", "1800", "-o", str(tmp_png.parent), str(tmp_svg)],
                        capture_output=True,
                        check=True,
                    )
                    gen_png = tmp_png.parent / f"{tmp_svg.name}.png"
                    if gen_png.exists():
                        term_img = Image.open(gen_png)
                        gen_png.unlink(missing_ok=True)
                    tmp_svg.unlink(missing_ok=True)
                except Exception:
                    pass
        elif capture_path.suffix.lower() == ".png":
            try:
                term_img = Image.open(capture_path)
            except Exception as e:
                print(f"      [WARN] Failed to open PNG {capture_path.name}: {e}")

        # If loading screenshot failed, fallback to render_terminal_card
        if term_img is None:
            return self.render_terminal_card(scene, episode, output_path)

        width, height = 1920, 1080
        img = Image.new("RGB", (width, height), color=(24, 24, 37))  # Catppuccin Base Dark
        draw = ImageDraw.Draw(img)

        # Top Accent Line (Sapphire)
        draw.rectangle([(0, 0), (1920, 10)], fill=(137, 180, 250))

        # Outer Terminal Window Frame
        draw.rounded_rectangle([(40, 30), (1880, 1050)], radius=18, fill=(30, 30, 46), outline=(69, 71, 90), width=2)

        # Title Bar
        draw.rounded_rectangle([(40, 30), (1880, 85)], radius=18, fill=(17, 17, 27))
        draw.rectangle([(40, 65), (1880, 85)], fill=(17, 17, 27))

        # macOS Terminal Control Buttons
        draw.ellipse([(65, 48), (85, 68)], fill=(243, 139, 168))  # Red
        draw.ellipse([(95, 48), (115, 68)], fill=(249, 226, 175))  # Yellow
        draw.ellipse([(125, 48), (145, 68)], fill=(166, 227, 161))  # Green

        font_win_title = self._get_font(20, bold=True)
        font_pill = self._get_font(16, bold=True)
        font_kb = self._get_font(15, bold=True)

        # Title text
        win_title = f"Egeria Workspace — {episode.lead_persona} ({episode.persona_username}) — Scene {scene.number}: {scene.title}"
        if len(win_title) > 85:
            win_title = win_title[:82] + "..."
        draw.text((165, 48), win_title, fill=(205, 214, 244), font=font_win_title)

        # Live Status Badges Top Right
        badge_text = f"● LIVE WORKSPACE: {episode.persona_username}"
        if total_frames > 1:
            badge_text += f" [{frame_idx + 1}/{total_frames}]"
        badge_width = font_pill.getbbox(badge_text)[2] + 30
        badge_x1 = 1860 - badge_width
        draw.rounded_rectangle([(badge_x1, 42), (1860, 74)], radius=8, fill=(49, 50, 68))
        draw.text((badge_x1 + 15, 49), badge_text, fill=(166, 227, 161), font=font_pill)

        # Scale and center the terminal screenshot inside the content area: (40, 95) to (1880, 1030)
        avail_w = 1840
        avail_h = 935
        term_copy = term_img.copy()
        term_copy.thumbnail((avail_w, avail_h), Image.Resampling.LANCZOS)

        paste_x = 40 + (avail_w - term_copy.width) // 2
        paste_y = 95 + (avail_h - term_copy.height) // 2
        img.paste(term_copy, (paste_x, paste_y))

        # Bottom Keybindings / Cue strip
        cue_text = scene.terminal_cue or "[Ctrl+T] Edit  •  [Ctrl+O] Comments  •  [Ctrl+N] Add  •  [Ctrl+L] Sample  •  [Ctrl+U] Subscribe  •  [Ctrl+F] Feedback  •  [Esc] Back"
        if len(cue_text) > 130:
            cue_text = cue_text[:127] + "..."
        draw.text((60, 1025), f"▶ {cue_text}", fill=(147, 154, 183), font=font_kb)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "PNG", quality=95)

    def render_terminal_card(self, scene: SceneSpec, episode: EpisodeSpec, output_path: Path):
        """Render a fallback 1080p Terminal Workspace Card when captures are unavailable."""
        width, height = 1920, 1080
        img = Image.new("RGB", (width, height), color=(24, 24, 37))  # Catppuccin Crust/Mantle
        draw = ImageDraw.Draw(img)

        # Top Accent Line (Sapphire / Green)
        draw.rectangle([(0, 0), (1920, 12)], fill=(137, 180, 250))

        # Main Terminal Window Container
        draw.rounded_rectangle([(70, 45), (1850, 1035)], radius=20, fill=(30, 30, 46), outline=(69, 71, 90), width=2)

        # Terminal Title Bar
        draw.rounded_rectangle([(70, 45), (1850, 105)], radius=20, fill=(17, 17, 27))
        draw.rectangle([(70, 85), (1850, 105)], fill=(17, 17, 27))  # Flat bottom for title bar

        # macOS Terminal Control Buttons
        draw.ellipse([(100, 68), (120, 88)], fill=(243, 139, 168))  # Red
        draw.ellipse([(135, 68), (155, 88)], fill=(249, 226, 175))  # Yellow
        draw.ellipse([(170, 68), (190, 88)], fill=(166, 227, 161))  # Green

        font_win_title = self._get_font(20, bold=True)
        draw.text((215, 68), f"Egeria Terminal — My Profile ({episode.persona_username}) — Scene {scene.number}", fill=(186, 194, 222), font=font_win_title)

        # Live Status Badges Top Right
        font_pill = self._get_font(16, bold=True)
        draw.rounded_rectangle([(1360, 60), (1820, 92)], radius=10, fill=(49, 50, 68))
        draw.text((1380, 67), "● LIVE EGERIA: https://127.0.0.1:9443", fill=(166, 227, 161), font=font_pill)

        # Terminal Prompt & Command Bar
        draw.rounded_rectangle([(100, 125), (1820, 180)], radius=12, fill=(17, 17, 27), outline=(49, 50, 68), width=1)
        font_cmd = self._get_font(22, bold=True)
        draw.text((120, 138), f"coco@pharma:~$ uv run my_profile --user {episode.persona_username}", fill=(137, 220, 235), font=font_cmd)

        # Live Screen Header & Workflow Badge
        font_screen_hdr = self._get_font(36, bold=True)
        font_screen_sub = self._get_font(22)
        draw.text((100, 205), f"WORKFLOW: {scene.title.upper()}", fill=(205, 214, 244), font=font_screen_hdr)
        draw.text((100, 255), f"Active Persona: {episode.lead_persona} • Role: {episode.persona_role} • Team: {episode.persona_team}", fill=(137, 180, 250), font=font_screen_sub)

        # Terminal Cue Box (Active UI Action)
        draw.rounded_rectangle([(100, 300), (1820, 375)], radius=14, fill=(17, 17, 27), outline=(137, 180, 250), width=2)
        font_cue_lbl = self._get_font(18, bold=True)
        font_cue_val = self._get_font(22, bold=True)
        draw.text((130, 312), "CURRENT TERMINAL ACTION & LIVE INTERACTION:", fill=(137, 180, 250), font=font_cue_lbl)
        cue_text = scene.terminal_cue or scene.title
        draw.text((130, 338), f"▶  {cue_text}", fill=(166, 227, 161), font=font_cue_val)

        # Spoken Narration Box
        draw.rounded_rectangle([(100, 395), (1820, 690)], radius=16, fill=(24, 24, 37), outline=(49, 50, 68), width=2)
        font_narr_hdr = self._get_font(20, bold=True)
        font_body = self._get_font(22)
        draw.text((130, 415), f"CALLIE / {episode.lead_persona.upper()} WALKTHROUGH COMMENTARY:", fill=(249, 226, 175), font=font_narr_hdr)

        curr_y = 455
        words = scene.dialogue.split(" ")
        line = ""
        for word in words:
            test_line = line + (" " if line else "") + word
            bbox = font_body.getbbox(test_line)
            if bbox[2] > 1620:
                draw.text((130, curr_y), line, fill=(205, 214, 244), font=font_body)
                curr_y += 34
                line = word
            else:
                line = test_line
        if line:
            draw.text((130, curr_y), line, fill=(205, 214, 244), font=font_body)
            curr_y += 34

        # Keybindings & Strategic Highlights Bar
        if scene.callouts:
            draw.rounded_rectangle([(100, 710), (1820, 940)], radius=14, fill=(17, 17, 27), outline=(69, 71, 90), width=1)
            draw.text((130, 725), "OPERATIONAL HIGHLIGHTS & KEYBINDINGS:", fill=(203, 166, 247), font=font_narr_hdr)
            callout_y = 760
            for item in scene.callouts:
                draw.text((130, callout_y), f"•  {item}", fill=(186, 194, 222), font=self._get_font(20))
                callout_y += 34

        # Bottom Keybindings Strip
        font_kb = self._get_font(16, bold=True)
        kb_text = "[Ctrl+T] Edit Table  •  [Ctrl+O] Comments  •  [Ctrl+N] Add  •  [Ctrl+L] Sample Data  •  [Ctrl+U] Subscribe  •  [Ctrl+F] Feedback  •  [Esc] Back"
        draw.text((100, 975), kb_text, fill=(147, 154, 183), font=font_kb)

        img.save(str(output_path), "PNG", quality=95)


class MediaProcessor:
    """FFmpeg wrapper for duration alignment, video-audio merging, and episode assembly."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def get_duration(self, file_path: Path) -> float:
        """Return media duration in seconds via ffprobe."""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(file_path),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(res.stdout.strip())
        except Exception:
            return 0.0

    def create_slide_video(self, png_path: Path, audio_path: Path, output_mp4: Path, lead_out: float = 0.5):
        """Create a 1080p MP4 clip from a static PNG slide and speech MP3."""
        audio_dur = self.get_duration(audio_path)
        total_dur = max(audio_dur + lead_out, 3.0)

        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(png_path),
            "-i",
            str(audio_path),
            "-t",
            f"{total_dur:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-tune",
            "stillimage",
            "-r",
            "25",
            "-g",
            "50",
            "-keyint_min",
            "25",
            "-bf",
            "0",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-af",
            "apad,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_mp4),
        ]
        subprocess.run(cmd, capture_output=True, check=True)

    def create_multi_image_video(
        self,
        png_paths: List[Path],
        audio_path: Path,
        output_mp4: Path,
        lead_out: float = 0.5,
    ):
        """Create a 1080p MP4 clip cycling through multiple screenshot frames across audio duration."""
        if len(png_paths) == 1:
            return self.create_slide_video(png_paths[0], audio_path, output_mp4, lead_out=lead_out)

        audio_dur = self.get_duration(audio_path)
        total_dur = max(audio_dur + lead_out, 3.0)
        dur_per_img = total_dur / len(png_paths)

        sub_clips = []
        tmp_dir = output_mp4.parent / f"_tmp_{output_mp4.stem}"
        tmp_dir.mkdir(parents=True, exist_ok=True)

        try:
            for i, png in enumerate(png_paths):
                sub_clip = tmp_dir / f"sub_{i}.mp4"
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-loop",
                    "1",
                    "-i",
                    str(png),
                    "-t",
                    f"{dur_per_img:.3f}",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-tune",
                    "stillimage",
                    "-r",
                    "25",
                    "-g",
                    "50",
                    "-keyint_min",
                    "25",
                    "-bf",
                    "0",
                    "-pix_fmt",
                    "yuv420p",
                    str(sub_clip),
                ]
                subprocess.run(cmd, capture_output=True, check=True)
                sub_clips.append(sub_clip)

            inputs = []
            for c in sub_clips:
                inputs.extend(["-i", str(c)])
            inputs.extend(["-i", str(audio_path)])

            filter_v = "".join(f"[{i}:v]" for i in range(len(sub_clips))) + f"concat=n={len(sub_clips)}:v=1:a=0[v]"
            audio_idx = len(sub_clips)
            audio_filter = f"[{audio_idx}:a]apad,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]"

            cmd = [
                "ffmpeg",
                "-y",
                *inputs,
                "-filter_complex",
                f"{filter_v};{audio_filter}",
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-t",
                f"{total_dur:.3f}",
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-r",
                "25",
                "-g",
                "50",
                "-keyint_min",
                "25",
                "-bf",
                "0",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-shortest",
                "-movflags",
                "+faststart",
                str(output_mp4),
            ]
            subprocess.run(cmd, capture_output=True, check=True)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def merge_audio_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_mp4: Path,
        lead_in_seconds: float = 0.5,
        lead_out_seconds: float = 0.5,
    ):
        """Merge terminal video recording with narration audio, applying frame freeze if needed."""
        video_dur = self.get_duration(video_path)
        audio_dur = self.get_duration(audio_path)
        target_audio_dur = audio_dur + lead_in_seconds + lead_out_seconds

        adelay_ms = int(lead_in_seconds * 1000)
        audio_filter = f"[1:a]adelay={adelay_ms}|{adelay_ms},apad,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]"

        if target_audio_dur > video_dur:
            freeze_dur = target_audio_dur - video_dur
            vf = f"[0:v]tpad=stop_mode=clone:stop_duration={freeze_dur:.3f},fps=25,setpts=PTS-STARTPTS[v]"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-filter_complex",
                f"{vf};{audio_filter}",
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-t",
                f"{target_audio_dur:.3f}",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-r",
                "25",
                "-g",
                "50",
                "-keyint_min",
                "25",
                "-bf",
                "0",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                str(output_mp4),
            ]
        else:
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-filter_complex",
                audio_filter,
                "-map",
                "0:v",
                "-map",
                "[a]",
                "-t",
                f"{video_dur:.3f}",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-crf",
                "18",
                "-r",
                "25",
                "-g",
                "50",
                "-keyint_min",
                "25",
                "-bf",
                "0",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-movflags",
                "+faststart",
                str(output_mp4),
            ]

        subprocess.run(cmd, capture_output=True, check=True)

    def concatenate_videos(self, video_paths: List[Path], output_mp4: Path):
        """Concatenate video clips using filter_complex concat for flawless QuickTime playback."""
        inputs = []
        filter_parts = []
        for i, p in enumerate(video_paths):
            inputs.extend(["-i", str(p)])
            filter_parts.append(f"[{i}:v][{i}:a]")

        concat_filter = f"{''.join(filter_parts)}concat=n={len(video_paths)}:v=1:a=1[v][a]"
        cmd = [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            concat_filter,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast",
            "-crf",
            "18",
            "-r",
            "25",
            "-g",
            "50",
            "-keyint_min",
            "25",
            "-bf",
            "0",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(output_mp4),
        ]
        subprocess.run(cmd, capture_output=True, check=True)


class EpisodeBuilder:
    """Coordinates generation of audio, slides, recordings, and assembled video for an episode."""

    def __init__(self, episode: EpisodeSpec):
        self.episode = episode
        self.ep_dir = OUTPUT_DIR / episode.id
        self.slides_dir = self.ep_dir / "slides"
        self.audio_dir = self.ep_dir / "audio"
        self.videos_dir = self.ep_dir / "videos"
        self.narrated_dir = self.ep_dir / "videos_narrated"

        for d in [self.slides_dir, self.audio_dir, self.videos_dir, self.narrated_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.synth = AudioSynthesizer(self.audio_dir)
        self.renderer = SlideRenderer(self.slides_dir)
        self.processor = MediaProcessor(self.ep_dir)

    def generate_audio(self) -> List[Path]:
        """Generate audio files for all scenes."""
        print(f"\n[1/4] Generating Voiceovers for Episode {self.episode.episode_number}: {self.episode.title}")
        print(f"      Persona: {self.episode.lead_persona} | Voice: {self.episode.voice_name} ({self.episode.voice_accent})")
        scene_audios = []
        for scene in self.episode.scenes:
            audio_path = self.audio_dir / f"scene_{scene.number}_{slugify(scene.title)}.mp3"
            self.synth.synthesize_scene(scene, self.episode, audio_path)
            scene_audios.append(audio_path)

        # Full stitched audio
        full_audio_path = self.audio_dir / f"episode_{self.episode.episode_number}_full_audio.mp3"
        self.synth.stitch_full_audio(scene_audios, full_audio_path)
        print(f"      ✓ Full Audio Track: {full_audio_path.name}")
        return scene_audios

    def find_scene_captures(self, scene_number: int) -> List[Path]:
        """Find all captured UI screenshots for a specific scene."""
        candidate_dirs = [
            self.ep_dir / "captures",
            OUTPUT_DIR / "captures",
            CAPTURES_DIR / self.episode.id,
            CAPTURES_DIR,
            Path("/Users/Shared/pdr-vault") / "captures",
        ]
        # Also check Peter Videos in iCloud vault
        vault_peter_videos = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/PDR 2/pdr-vault/Peter Videos"
        if vault_peter_videos.exists():
            for ep_folder in vault_peter_videos.glob(f"Episode {self.episode.episode_number}*"):
                candidate_dirs.append(ep_folder / "output/captures")
                candidate_dirs.append(ep_folder / "captures")

        patterns = [
            f"ep{self.episode.episode_number}_scene{scene_number}_*.svg",
            f"ep{self.episode.episode_number}_scene{scene_number}_*.png",
            f"scene_{scene_number}_*.svg",
            f"scene_{scene_number}_*.png",
            f"scene{scene_number}_*.svg",
            f"scene{scene_number}_*.png",
        ]

        found: Dict[str, Path] = {}
        for cdir in candidate_dirs:
            if not cdir.exists():
                continue
            for pat in patterns:
                for file_path in cdir.glob(pat):
                    if file_path.is_file() and file_path.stem not in found:
                        found[file_path.stem] = file_path

        return [found[k] for k in sorted(found.keys())]

    def generate_slides(self) -> List[Path]:
        """Generate 1080p slide PNGs for all scenes."""
        print(f"\n[2/4] Generating Slide Graphics for Episode {self.episode.episode_number}")
        slide_paths = []
        for scene in self.episode.scenes:
            slide_path = self.slides_dir / f"slide_scene_{scene.number}.png"
            self.renderer.render_slide(scene, self.episode, slide_path)
            slide_paths.append(slide_path)
            print(f"      ✓ Rendered Slide {scene.number}: {slide_path.name}")
        return slide_paths

    def generate_scene_clips(self, slide_paths: List[Path], audio_paths: List[Path]) -> List[Path]:
        """Generate MP4 video clips for each scene, embedding live terminal captures where available."""
        print(f"\n[3/4] Rendering Scene Video Clips for Episode {self.episode.episode_number}")
        clips = []
        for scene, slide_path, audio_path in zip(self.episode.scenes, slide_paths, audio_paths):
            clip_path = self.narrated_dir / f"scene_{scene.number}_{slugify(scene.title)}_narrated.mp4"

            # Scenes 0, 1, and 5 are slide cards
            if scene.number in (0, 1, 5):
                self.processor.create_slide_video(slide_path, audio_path, clip_path)
                dur = self.processor.get_duration(clip_path)
                print(f"      ✓ Rendered Scene {scene.number} Slide Clip ({dur:.1f}s)")
            else:
                captures = self.find_scene_captures(scene.number)
                if captures:
                    framed_pngs = []
                    for idx, cap in enumerate(captures):
                        frame_png = self.slides_dir / f"frame_scene_{scene.number}_{idx + 1}.png"
                        self.renderer.render_terminal_screenshot_frame(
                            cap,
                            scene,
                            self.episode,
                            frame_png,
                            frame_idx=idx,
                            total_frames=len(captures),
                        )
                        framed_pngs.append(frame_png)

                    self.processor.create_multi_image_video(framed_pngs, audio_path, clip_path)
                    dur = self.processor.get_duration(clip_path)
                    print(
                        f"      ✓ Rendered Scene {scene.number} Live Screen Clip ({dur:.1f}s) "
                        f"with {len(captures)} live Egeria UI capture(s)"
                    )
                else:
                    self.processor.create_slide_video(slide_path, audio_path, clip_path)
                    dur = self.processor.get_duration(clip_path)
                    print(f"      ✓ Rendered Scene {scene.number} Slide Clip ({dur:.1f}s)")

            clips.append(clip_path)
        return clips

    def assemble_episode(self, clips: List[Path], audio_paths: Optional[List[Path]] = None) -> Path:
        """Assemble all scene clips into the master episode MP4."""
        print(f"\n[4/4] Assembling Master Episode {self.episode.episode_number} Video...")
        master_output = self.narrated_dir / f"coco_pharma_episode_{self.episode.episode_number}_{slugify(self.episode.lead_persona)}.mp4"

        # Check for continuous VHS walkthrough recording (Scenes 2 to 4)
        walkthrough_video = self.videos_dir / f"episode_{self.episode.episode_number}_walkthrough.mp4"
        scene0_clip = self.narrated_dir / f"scene_0_{slugify(self.episode.scenes[0].title)}_narrated.mp4"
        scene1_clip = self.narrated_dir / f"scene_1_{slugify(self.episode.scenes[1].title)}_narrated.mp4"
        scene5_clip = self.narrated_dir / f"scene_5_{slugify(self.episode.scenes[5].title)}_narrated.mp4"

        if walkthrough_video.exists() and scene0_clip.exists() and scene1_clip.exists() and scene5_clip.exists() and audio_paths and len(audio_paths) >= 5:
            # Stitch audio for Scenes 2, 3, and 4
            ui_audios = audio_paths[2:5]
            wt_audio = self.audio_dir / f"episode_{self.episode.episode_number}_walkthrough_audio.mp3"
            self.synth.stitch_full_audio(ui_audios, wt_audio)

            wt_narrated = self.narrated_dir / f"episode_{self.episode.episode_number}_walkthrough_narrated.mp4"
            print(f"      Merging Full VHS Terminal Walkthrough (Scenes 2 to 4) ...")
            self.processor.merge_audio_video(
                walkthrough_video, wt_audio, wt_narrated, lead_in_seconds=0.0, lead_out_seconds=0.5
            )
            print(f"      ✓ Rendered VHS Walkthrough Clip: {wt_narrated.name}")

            sequence = [scene0_clip, scene1_clip, wt_narrated, scene5_clip]
            print("      Using seamless continuous terminal walkthrough (Scenes 2-4) without redundant terminal re-launches.")
        else:
            sequence = clips

        self.processor.concatenate_videos(sequence, master_output)
        dur = self.processor.get_duration(master_output)
        print(f"      ✓ MASTER EPISODE CREATED: {master_output}")
        print(f"        Total Duration: {dur:.1f} seconds ({dur/60:.1f} minutes)")
        return master_output

    def build_full(self) -> Path:
        """Run complete generation pipeline for this episode."""
        audios = self.generate_audio()
        slides = self.generate_slides()
        clips = self.generate_scene_clips(slides, audios)
        return self.assemble_episode(clips, audios)


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Coco Pharmaceuticals Business Value Video Series")
    parser.add_argument(
        "--episode",
        choices=["all", "episode1", "episode2", "episode3", "episode4", "episode5", "episode6", "episode7"],
        default="all",
        help="Specify which episode to generate (default: all)",
    )
    parser.add_argument("--audio-only", action="store_true", help="Generate speech audio tracks only")
    parser.add_argument("--slides-only", action="store_true", help="Generate 1080p slide PNGs only")
    parser.add_argument("--list-episodes", action="store_true", help="List all available episodes and persona profiles")
    parser.add_argument(
        "--export-vault",
        nargs="?",
        const="DEFAULT",
        default=None,
        help="Automatically sync generated videos to pdr-vault (optional custom vault path)",
    )
    parser.add_argument(
        "--all-assets",
        action="store_true",
        help="When exporting to vault, include all audio and slide assets alongside master videos",
    )
    return parser.parse_args()


def print_episode_roster():
    print("\n" + "=" * 80)
    print("COCO PHARMACEUTICALS BUSINESS VALUE VIDEO SERIES - EPISODE ROSTER")
    print("=" * 80)
    for ep_id, ep in EPISODES.items():
        print(f"\n[EPISODE {ep.episode_number}] {ep.title}")
        print(f"  • Subtitle: {ep.subtitle}")
        print(f"  • Lead Persona: {ep.lead_persona} ({ep.persona_role})")
        print(f"  • Team: {ep.persona_team}")
        print(f"  • Business Driver: {ep.business_driver}")
        print(f"  • Assigned Voice: {ep.voice_name} ({ep.voice_gender}, {ep.voice_accent})")
        print(f"  • Scenes: {len(ep.scenes)} scenes")
    print("\n" + "=" * 80 + "\n")


def main():
    args = parse_args()

    if args.list_episodes:
        print_episode_roster()
        return

    selected_keys = list(EPISODES.keys()) if args.episode == "all" else [args.episode]

    print("\n" + "=" * 80)
    print(f"GENERATING COCO PHARMA BUSINESS VALUE SERIES ({len(selected_keys)} Episodes)")
    print("=" * 80)

    for ep_key in selected_keys:
        episode = EPISODES[ep_key]
        builder = EpisodeBuilder(episode)

        if args.audio_only:
            builder.generate_audio()
        elif args.slides_only:
            builder.generate_slides()
        else:
            builder.build_full()

    print("\n" + "=" * 80)
    print("ALL REQUESTED VIDEO EPISODES GENERATED SUCCESSFULLY!")
    print(f"Media Output Directory: {OUTPUT_DIR}")
    print("=" * 80 + "\n")

    # Automated Vault Export Trigger
    should_export = args.export_vault is not None or os.getenv("PDR_VAULT_PATH") is not None
    if should_export and not (args.audio_only or args.slides_only):
        vault_custom = None if args.export_vault in (None, "DEFAULT") else args.export_vault
        print("[AUTO-EXPORT] Initiating automated synchronization to pdr-vault...")
        export_to_vault(vault_path=vault_custom, all_assets=args.all_assets)


if __name__ == "__main__":
    main()
