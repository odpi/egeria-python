#!/usr/bin/env python3
"""Automated Voiceover & Video Assembly Pipeline for My Profile Video Blog.

Series: Coco Pharmaceuticals Data Governance Journey
Persona: Callie Quartile (Data Scientist)
Companion Script: VIDEO_SCRIPT_DRAFT.md

Features:
- Extracts scene narration dialogue from VIDEO_SCRIPT_DRAFT.md
- Generates high-quality TTS audio tracks using edge-tts (Azure Neural) or macOS say
- Automatically matches audio and terminal video durations (with smart frame freezing/padding)
- Merges voiceover tracks with VHS terminal recordings into 1080p narrated MP4s
- Generates visual title cards and intro/outro slides for full episode assembly
- Assembles complete multi-scene video episodes with seamless transitions
"""

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]
DOCS_SCRIPT = SCRIPT_DIR.parent / "VIDEO_SCRIPT_DRAFT.md"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "output"

DEFAULT_EDGE_VOICE = "en-GB-SoniaNeural"
DEFAULT_SAY_VOICE = "Flo (English (UK))"


def slugify(text: str) -> str:
    """Convert a title to a clean filename slug."""
    text = text.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


@dataclass
class SceneSpec:
    number: int
    title: str
    dialogue: str
    scene_type: str  # "camera", "slide", or "terminal"
    video_file: Optional[str] = None
    slide_title: Optional[str] = None
    slide_subtitle: Optional[str] = None
    callouts: Optional[List[str]] = None


# Structured Scene Dialogue based on VIDEO_SCRIPT_DRAFT.md
SCENES: Dict[int, SceneSpec] = {
    0: SceneSpec(
        number=0,
        title="Cold Open & Introduction",
        dialogue=(
            "Hi, I'm Callie Quartile. I'm a data scientist here at Coco Pharmaceuticals, "
            "working across our Clinical Trials research and AI Pilot teams. "
            "If you've been following Jules Keeper's video blogs, you've heard our Chief Data Officer "
            "talk about his mission to establish business-led data governance without creating bureaucratic roadblocks. "
            "But as someone building cancer research models on patient cohorts, my immediate question was: "
            "how does Jules's 'better data for everyone' initiative help me get my daily work done? Where do I actually start? "
            "It turns out, I start with me."
        ),
        scene_type="camera",
        slide_title="Coco Pharmaceuticals",
        slide_subtitle="Better Data for Everyone — Powered by Egeria\nMeeting Egeria Through My Profile: The Practitioner's Cockpit",
        callouts=["Callie Quartile — Data Scientist", "Clinical Trials & AI Pilot Teams"],
    ),
    1: SceneSpec(
        number=1,
        title="The Context: Operationalizing Governance Roles",
        dialogue=(
            "In his recent video on Establishing Data Governance, Jules pointed out that governance policies on paper "
            "remain passive until you attach responsibilities to named roles with real people appointed to them. "
            "Egeria already knows the appointed roles I hold, the clinical trial teams I collaborate with under Dr. Tessa Tube, "
            "the data definitions curated by Peter Profile, and the privacy classifications set by Faith Broker. "
            "But having that information fragmented across multiple tools slows us down. "
            "We needed one fast, interactive, keyboard-driven cockpit where any team member can see their governance ecosystem, "
            "keep it up to date, and take immediate action. "
            "That workspace is My Profile."
        ),
        scene_type="slide",
        slide_title="Operationalizing Data Governance",
        slide_subtitle="Attaching Governance Principles to Named Roles & Active Teams",
        callouts=[
            "Jules Keeper — CDO (Governance Principles)",
            "Faith Broker — Privacy Officer (Classifications)",
            "Peter Profile — Information Analyst (Curated Catalogs)",
            "Dr. Tessa Tube — Lead Researcher (Clinical Trials)",
        ],
    ),
    2: SceneSpec(
        number=2,
        title="Launch & Parallel Background Startup",
        dialogue=(
            "My Profile is a terminal application built with Textual and pyegeria. When you launch it, there's no waiting around. "
            "While this welcome screen greets you, the application is already querying the Egeria metadata highway asynchronously in the background. "
            "By the time you hit Continue, your full profile, role appointments, and collections are already loaded in memory. "
            "And if I'm pairing with Peter Profile or auditing permissions with Faith Broker, Change User lets us switch identities "
            "right from the start with live credential validation."
        ),
        scene_type="terminal",
        video_file="scene2_launch_and_startup.mp4",
        slide_title="Launch & Background Startup",
        callouts=["Async background profile loading", "Live credential validation", "Instant keyboard response"],
    ),
    3: SceneSpec(
        number=3,
        title="The Main Dashboard Tour",
        dialogue=(
            "Here is my daily home base. Every single panel is synchronized live with Egeria. "
            "At the top, my User Associations and Collections organize the clinical datasets and glossaries I care about. "
            "In the middle, you see my appointed Roles and Teams. Notice how governance comes alive here: "
            "pressing Enter on my Clinical Trials team role instantly opens My Team, showing colleagues like Tessa Tube and Tanya Tidie "
            "along with their active responsibilities. "
            "Down here is my daily activity stream: team Blogs, my personal Journal, and my To-Dos. "
            "And at the top right, Egeria tracks my Karma Points, recognizing active curation and collaboration across Coco Pharmaceuticals!"
        ),
        scene_type="terminal",
        video_file="scene3_main_dashboard.mp4",
        slide_title="Main Dashboard & Roles",
        callouts=["Live metadata synchronization", "Role & Team drill-down", "Automated Karma recognition"],
    ),
    4: SceneSpec(
        number=4,
        title="Real-Time Curation: To-Dos, Comments & Bookmarks",
        dialogue=(
            "Data governance only works if metadata is maintained as part of our normal flow of work, not as an afterthought. "
            "Pressing Control plus T lets me edit any highlighted table in place, adding action items from morning stand-ups or updating project milestones. "
            "With Control plus O and Control plus N, threaded discussions attach directly to the metadata asset or task itself. "
            "Instead of losing critical context in email threads, Dr. Tube and I keep our clinical trial discussions permanently linked to the data. "
            "And with Control plus K and Control plus B, I can bookmark key assets and retrieve them instantly with a single keystroke."
        ),
        scene_type="terminal",
        video_file="scene4_curation_todos_comments.mp4",
        slide_title="Real-Time Metadata Curation",
        callouts=[
            "Ctrl+T Edit Table",
            "Ctrl+O View Comments / Ctrl+N Add Comment",
            "Ctrl+K Bookmark Row / Ctrl+B View Bookmarks",
        ],
    ),
    5: SceneSpec(
        number=5,
        title="The Hero Workflow: Shopping for Governed Data Products",
        dialogue=(
            "Now for the most powerful feature in my workflow: Shop for Data. "
            "Before Jules Keeper established our open metadata catalog, finding trusted clinical data meant weeks of meetings and manual approvals. "
            "Here, Egeria brings together Business Domains, Glossaries, Data Dictionaries, and Digital Product Catalogs into a unified data marketplace. "
            "I can explore standardized terminology, verify classifications, and hit Control plus L to sample the dataset right in my terminal "
            "to ensure it fits my AI model requirements. "
            "When it's right, Control plus U lets me submit a formal Subscription Request. "
            "Egeria ensures Faith Broker's privacy rules and compliance policies are satisfied, giving data owners full visibility into who is using their data and why. "
            "In less than sixty seconds, governed access is requested, validated, and tracked in Subscriptions."
        ),
        scene_type="terminal",
        video_file="scene5_shop_for_data.mp4",
        slide_title="Governed Data Marketplace",
        callouts=[
            "Unified Data Marketplace",
            "Instant Data Sampling (Ctrl+L)",
            "Governed Subscriptions (Ctrl+U)",
        ],
    ),
    6: SceneSpec(
        number=6,
        title="Collaboration, Networks & Technology Curation",
        dialogue=(
            "My Profile also strengthens our human network across Coco Pharmaceuticals. "
            "My Network visualizes collaboration graphs and reporting relationships across departments. "
            "Work with Communities connects us to cross-functional working groups, like our Oncology Research and Sustainability circles. "
            "If I notice something that needs improvement, pressing Control plus F lets me log feedback directly into Egeria from anywhere in the app. "
            "And for our integration architects like Bob Nitter, the Technology Types screen displays the automated governance action templates "
            "Egeria executes behind the scenes."
        ),
        scene_type="terminal",
        video_file="scene6_network_communities_feedback.mp4",
        slide_title="Collaboration & Networks",
        callouts=[
            "Interactive Network Graph",
            "Community Workspaces",
            "In-App Feedback (Ctrl+F)",
            "Technology Curation Types",
        ],
    ),
    7: SceneSpec(
        number=7,
        title="Wrap-Up & Call to Action",
        dialogue=(
            "That is My Profile: a fast, intuitive, and governed personal cockpit that turns enterprise metadata into everyday productivity. "
            "When Jules Keeper says 'better data for everyone', this is what it looks like in practice: "
            "researchers and data scientists spending less time searching for data and more time discovering breakthroughs. "
            "My Profile is fully open source as part of the egeria-python project. "
            "Try it out in your own terminal, connect it to the Coco Pharmaceuticals demo environment, "
            "and experience how open metadata can transform your working day. "
            "Thanks for watching, and see you next time!"
        ),
        scene_type="camera",
        slide_title="Better Data for Everyone",
        slide_subtitle="Open Metadata & Governed Productivity with Egeria\nhttps://egeria-project.org\nhttps://github.com/odpi/egeria-python",
        callouts=["Launch: uv run my_profile", "Web: uv run serve_my_profile"],
    ),
}


class VoiceoverSynthesizer:
    """Handles text-to-speech synthesis using edge-tts or macOS say."""

    def __init__(self, backend: str = "auto", voice: Optional[str] = None, rate: str = "+0%"):
        self.backend = self._resolve_backend(backend)
        self.voice = voice or (DEFAULT_EDGE_VOICE if self.backend == "edge" else DEFAULT_SAY_VOICE)
        self.rate = rate

    def _resolve_backend(self, backend: str) -> str:
        if backend in ("edge", "edge-tts"):
            return "edge"
        if backend in ("say", "macos"):
            return "say"
        # Auto-detect
        try:
            import edge_tts  # noqa: F401

            return "edge"
        except ImportError:
            if shutil.which("say"):
                return "say"
            return "edge"

    async def synthesize(self, text: str, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if self.backend == "edge":
            await self._synthesize_edge(text, output_path)
        else:
            self._synthesize_say(text, output_path)
        return output_path

    async def _synthesize_edge(self, text: str, output_path: Path) -> None:
        try:
            import edge_tts

            communicate = edge_tts.Communicate(text=text, voice=self.voice, rate=self.rate)
            await communicate.save(str(output_path))
        except ImportError:
            # Fallback to CLI
            cmd = [
                "edge-tts",
                "--voice",
                self.voice,
                "--text",
                text,
                "--write-media",
                str(output_path),
            ]
            if self.rate and self.rate != "+0%":
                cmd.extend(["--rate", self.rate])
            subprocess.run(cmd, check=True, capture_output=True)

    def _synthesize_say(self, text: str, output_path: Path) -> None:
        aiff_path = output_path.with_suffix(".aiff")
        cmd_say = ["say", "-v", self.voice, "-o", str(aiff_path), text]
        subprocess.run(cmd_say, check=True)

        # Convert AIFF to MP3 with ffmpeg
        cmd_ffmpeg = [
            "ffmpeg",
            "-y",
            "-i",
            str(aiff_path),
            "-codec:a",
            "libmp3lame",
            "-qscale:a",
            "2",
            str(output_path),
        ]
        subprocess.run(cmd_ffmpeg, check=True, capture_output=True)
        if aiff_path.exists():
            aiff_path.unlink()


def render_slide_image(scene: SceneSpec, output_png: Path) -> Path:
    """Render a high-resolution 1080p slide PNG image using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        # Fallback if Pillow is not available
        return output_png

    width, height = 1920, 1080
    img = Image.new("RGB", (width, height), color=(17, 17, 27))  # #11111b
    draw = ImageDraw.Draw(img)

    # Outer card
    draw.rounded_rectangle([(80, 80), (1840, 1000)], radius=24, fill=(24, 24, 37), outline=(49, 50, 68), width=4)

    # Accent pill
    draw.rounded_rectangle([(140, 140), (152, 250)], radius=6, fill=(137, 180, 250))

    # Helper to load system fonts
    def get_font(size: int, mono: bool = False, bold: bool = False):
        font_candidates = []
        if mono:
            font_candidates = [
                "/System/Library/Fonts/Menlo.ttc",
                "/System/Library/Fonts/SFCompactMono.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            ]
        elif bold:
            font_candidates = [
                "/System/Library/Fonts/HelveticaNeue-Bold.otf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            ]
        else:
            font_candidates = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            ]
        for fpath in font_candidates:
            if os.path.exists(fpath):
                try:
                    return ImageFont.truetype(fpath, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_brand = get_font(52, bold=True)
    font_series = get_font(26)
    font_scene = get_font(40, bold=True)
    font_body = get_font(28)
    font_box_header = get_font(22, mono=True, bold=True)
    font_box_content = get_font(22, mono=True)
    font_footer = get_font(20)

    title = scene.slide_title or scene.title
    subtitle = scene.slide_subtitle or ""

    # Brand Title
    draw.text((180, 150), title, fill=(205, 214, 244), font=font_brand)
    draw.text((180, 215), "Coco Pharmaceuticals Data Governance Journey • Video Blog", fill=(166, 173, 200), font=font_series)

    # Separator line
    draw.line([(140, 280), (1780, 280)], fill=(49, 50, 68), width=3)

    # Scene Title & Subtitle
    draw.text((140, 320), f"Scene {scene.number}: {scene.title}", fill=(137, 180, 250), font=font_scene)

    # Multiline Subtitle
    curr_y = 390
    for line in subtitle.split("\n"):
        if line.strip():
            draw.text((140, curr_y), line.strip(), fill=(186, 194, 222), font=font_body)
            curr_y += 45

    # Key Focus Box
    if scene.callouts:
        line_height = 42
        num_callouts = len(scene.callouts)
        box_content_height = 40 + (num_callouts * line_height)
        box_height = max(box_content_height + 50, 180)
        box_y1 = min(max(curr_y + 40, 540), 900 - box_height)
        box_y2 = box_y1 + box_height
        draw.rounded_rectangle([(140, box_y1), (1780, box_y2)], radius=16, fill=(17, 17, 27), outline=(69, 71, 90), width=2)
        draw.text((180, box_y1 + 25), "KEY HIGHLIGHTS & WORKFLOW FOCUS:", fill=(166, 227, 161), font=font_box_header)
        callout_y = box_y1 + 75
        for item in scene.callouts:
            draw.text((180, callout_y), f"•  {item}", fill=(249, 226, 175), font=font_box_content)
            callout_y += line_height

    # Footer
    draw.text((140, 940), "Egeria Project • Open Metadata & Governed Productivity • My Profile Cockpit", fill=(108, 112, 134), font=font_footer)

    output_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_png), "PNG")
    return output_png


class MediaProcessor:
    """Handles audio/video alignment, padding, title card creation, and multi-scene assembly."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.audio_dir = output_dir / "audio"
        self.videos_dir = output_dir / "videos"
        self.narrated_dir = output_dir / "videos_narrated"
        self.slides_dir = output_dir / "slides"

        for d in (self.audio_dir, self.videos_dir, self.narrated_dir, self.slides_dir):
            d.mkdir(parents=True, exist_ok=True)

    def get_duration(self, file_path: Path) -> float:
        """Get duration of audio or video file in seconds via ffprobe."""
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(file_path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        return float(data["format"]["duration"])

    def create_title_slide_video(self, scene: SceneSpec, audio_path: Path, output_mp4: Path) -> Path:
        """Create a 1080p slide video clip with audio narration for camera/slide scenes."""
        audio_duration = self.get_duration(audio_path)
        total_duration = audio_duration + 1.0  # Add 1.0s grace pad

        png_path = self.slides_dir / f"slide_scene_{scene.number}.png"
        render_slide_image(scene, png_path)

        # Convert PNG + Audio to MP4 with consistent framerate, 48kHz stereo audio, no B-frames (QuickTime safety), and faststart
        cmd = [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-framerate",
            "25",
            "-i",
            str(png_path),
            "-i",
            str(audio_path),
            "-c:v",
            "libx264",
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
            "-t",
            f"{total_duration:.2f}",
            "-shortest",
            "-movflags",
            "+faststart",
            str(output_mp4),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_mp4

    def merge_audio_video(
        self,
        video_path: Path,
        audio_path: Path,
        output_path: Path,
        lead_in_seconds: float = 0.5,
        lead_out_seconds: float = 1.0,
    ) -> Path:
        """Merge audio with a terminal video recording, dynamically matching duration with video freeze."""
        video_dur = self.get_duration(video_path)
        audio_dur = self.get_duration(audio_path)

        target_audio_dur = audio_dur + lead_in_seconds + lead_out_seconds

        print(f"  Merging: video={video_dur:.2f}s, audio={audio_dur:.2f}s -> target={target_audio_dur:.2f}s")

        # Audio filter: delay audio by lead_in, resample to 48kHz stereo, reset audio PTS
        adelay_ms = int(lead_in_seconds * 1000)
        audio_filter = f"[1:a]adelay={adelay_ms}|{adelay_ms},apad,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]"

        if target_audio_dur > video_dur:
            # Need to freeze last frame of video for (target_audio_dur - video_dur)
            diff = target_audio_dur - video_dur
            video_filter = (
                f"[0:v]fps=25,scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration={diff:.2f},"
                f"setpts=PTS-STARTPTS[v]"
            )
            filter_complex = f"{video_filter};{audio_filter}"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-filter_complex",
                filter_complex,
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
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
                "-t",
                f"{target_audio_dur:.2f}",
                "-movflags",
                "+faststart",
                str(output_path),
            ]
        else:
            # Video is longer than audio; audio will finish and padded silence will play until video end
            total_dur = video_dur
            video_filter = (
                f"[0:v]fps=25,scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setpts=PTS-STARTPTS[v]"
            )
            filter_complex = f"{video_filter};{audio_filter}"
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-filter_complex",
                filter_complex,
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
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
                "-t",
                f"{total_dur:.2f}",
                "-movflags",
                "+faststart",
                str(output_path),
            ]

        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def concatenate_audio_files(self, audio_paths: List[Path], output_path: Path, gap_seconds: float = 0.8) -> Path:
        """Concatenate multiple audio files with a brief silence gap between each."""
        filter_inputs = []
        filter_parts = []
        for i, ap in enumerate(audio_paths):
            filter_inputs.extend(["-i", str(ap)])
            # Pad each audio except the last with silence
            if i < len(audio_paths) - 1:
                filter_parts.append(f"[{i}:a]apad=pad_dur={gap_seconds:.2f}[a{i}];")
            else:
                filter_parts.append(f"[{i}:a]anull[a{i}];")

        concat_str = "".join(f"[a{i}]" for i in range(len(audio_paths)))
        filter_parts.append(f"{concat_str}concat=n={len(audio_paths)}:v=0:a=1[outa]")

        filter_complex = "".join(filter_parts)
        cmd = [
            "ffmpeg",
            "-y",
            *filter_inputs,
            "-filter_complex",
            filter_complex,
            "-map",
            "[outa]",
            "-c:a",
            "libmp3lame",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-qscale:a",
            "2",
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path

    def concatenate_videos(self, video_paths: List[Path], output_path: Path) -> Path:
        """Concatenate a sequence of MP4 video files into a single master video."""
        filter_inputs = []
        filter_streams = []
        for i, vp in enumerate(video_paths):
            filter_inputs.extend(["-i", str(vp.resolve())])
            filter_streams.append(f"[{i}:v][{i}:a]")

        concat_spec = "".join(filter_streams) + f"concat=n={len(video_paths)}:v=1:a=1[outv][outa]"

        cmd = [
            "ffmpeg",
            "-y",
            *filter_inputs,
            "-filter_complex",
            concat_spec,
            "-map",
            "[outv]",
            "-map",
            "[outa]",
            "-c:v",
            "libx264",
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
            str(output_path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path


async def generate_all_audio(
    synthesizer: VoiceoverSynthesizer,
    processor: MediaProcessor,
    target_scenes: Optional[List[int]] = None,
) -> Dict[int, Path]:
    """Generate audio MP3 files for all or selected scenes concurrently."""
    scenes_to_run = target_scenes if target_scenes is not None else list(SCENES.keys())
    audio_map: Dict[int, Path] = {}

    print(f"\n>>> Generating Voiceover Audio using [{synthesizer.backend.upper()}] voice: '{synthesizer.voice}'...", flush=True)

    async def synth_scene(num: int) -> tuple[int, Path]:
        scene = SCENES[num]
        audio_file = processor.audio_dir / f"scene{num}_{slugify(scene.title)}.mp3"
        print(f"  [Synthesizing Scene {num}] {scene.title} ...", flush=True)
        await synthesizer.synthesize(scene.dialogue, audio_file)
        print(f"    ✓ Generated: {audio_file.name}", flush=True)
        return num, audio_file

    results = await asyncio.gather(*(synth_scene(num) for num in scenes_to_run))
    for num, audio_file in results:
        audio_map[num] = audio_file

    # Generate combined walkthrough audio (terminal scenes 2-6) via fast audio concatenation
    if all(k in audio_map for k in (2, 3, 4, 5, 6)):
        wt_audio = processor.audio_dir / "my_profile_full_walkthrough_narration.mp3"
        print("  [Assembling Walkthrough Audio] Scenes 2 to 6 combined ...", flush=True)
        processor.concatenate_audio_files([audio_map[i] for i in (2, 3, 4, 5, 6)], wt_audio, gap_seconds=1.0)
        print(f"    ✓ Generated: {wt_audio.name}", flush=True)

    # Generate full episode audio (Scenes 0 to 7) via fast audio concatenation
    if all(k in audio_map for k in range(8)):
        full_audio = processor.audio_dir / "coco_pharma_my_profile_full_episode_audio.mp3"
        print("  [Assembling Full Episode Audio] Scenes 0 to 7 combined ...", flush=True)
        processor.concatenate_audio_files([audio_map[i] for i in range(8)], full_audio, gap_seconds=1.2)
        print(f"    ✓ Generated: {full_audio.name}", flush=True)

    return audio_map


def build_narrated_videos(
    processor: MediaProcessor,
    audio_map: Dict[int, Path],
    target_scenes: Optional[List[int]] = None,
) -> List[Path]:
    """Assemble individual narrated scene videos and master walkthrough."""
    scenes_to_run = target_scenes if target_scenes is not None else list(SCENES.keys())
    narrated_clips: List[Path] = []

    print("\n>>> Merging Video Captures & Audio Narration with FFmpeg...", flush=True)

    for num in sorted(scenes_to_run):
        scene = SCENES[num]
        audio_path = audio_map.get(num)
        if not audio_path or not audio_path.exists():
            print(f"  [SKIP Scene {num}] Audio file missing.", flush=True)
            continue

        output_clip = processor.narrated_dir / f"scene{num}_{slugify(scene.title)}_narrated.mp4"

        if scene.scene_type in ("camera", "slide"):
            print(f"  [Building Slide Scene {num}] {scene.title} ...", flush=True)
            processor.create_title_slide_video(scene, audio_path, output_clip)
            narrated_clips.append(output_clip)
            print(f"    ✓ Rendered: {output_clip.name}", flush=True)
        else:
            # Terminal scene
            video_input = processor.videos_dir / (scene.video_file or f"scene{num}.mp4")
            if not video_input.exists():
                print(f"  [WARNING] Video recording missing for Scene {num}: {video_input.name}", flush=True)
                print("            Generating slide fallback for scene preview...", flush=True)
                processor.create_title_slide_video(scene, audio_path, output_clip)
            else:
                print(f"  [Merging Scene {num}] {scene.title} ...", flush=True)
                processor.merge_audio_video(video_input, audio_path, output_clip)
            narrated_clips.append(output_clip)
            print(f"    ✓ Rendered: {output_clip.name}", flush=True)

    # Process full continuous walkthrough if present
    full_wt_video = processor.videos_dir / "my_profile_full_walkthrough.mp4"
    full_wt_audio = processor.audio_dir / "my_profile_full_walkthrough_narration.mp3"
    if full_wt_video.exists() and full_wt_audio.exists():
        wt_out = processor.narrated_dir / "my_profile_full_walkthrough_narrated.mp4"
        print("\n  [Merging Full Walkthrough Video] Scenes 2 to 6 continuous ...", flush=True)
        processor.merge_audio_video(full_wt_video, full_wt_audio, wt_out, lead_in_seconds=0.0, lead_out_seconds=0.5)
        print(f"    ✓ Rendered: {wt_out.name}", flush=True)

    return narrated_clips


def assemble_full_episode(processor: MediaProcessor, narrated_clips: List[Path]) -> Optional[Path]:
    """Concatenate scenes into a complete seamless 5-minute video blog."""
    print("\n>>> Assembling Master Complete Video Blog...")

    scene0 = processor.narrated_dir / f"scene0_{slugify(SCENES[0].title)}_narrated.mp4"
    scene1 = processor.narrated_dir / f"scene1_{slugify(SCENES[1].title)}_narrated.mp4"
    walkthrough = processor.narrated_dir / "my_profile_full_walkthrough_narrated.mp4"
    scene7 = processor.narrated_dir / f"scene7_{slugify(SCENES[7].title)}_narrated.mp4"

    if scene0.exists() and scene1.exists() and walkthrough.exists() and scene7.exists():
        sequence = [scene0, scene1, walkthrough, scene7]
        print("  Using seamless continuous terminal walkthrough (Scenes 2-6) without redundant terminal re-launches.")
    else:
        sequence = narrated_clips

    master_output = processor.narrated_dir / "coco_pharma_my_profile_complete_video_blog.mp4"
    processor.concatenate_videos(sequence, master_output)
    print(f"  ✓ MASTER VIDEO CREATED: {master_output}")
    print(f"    Duration: {processor.get_duration(master_output):.1f} seconds")
    return master_output


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Generate voiceover audio and assemble narrated videos for My Profile.")
    parser.add_argument(
        "--tts",
        choices=["auto", "edge", "say"],
        default="auto",
        help="TTS engine: 'edge' (Azure Neural) or 'say' (macOS native)",
    )
    parser.add_argument(
        "--voice",
        default=None,
        help=f"Voice name (default: {DEFAULT_EDGE_VOICE} for edge, {DEFAULT_SAY_VOICE} for say)",
    )
    parser.add_argument("--rate", default="+0%", help="Speech rate adjustment (e.g. '+5%%', '-5%%')")
    parser.add_argument(
        "--scene",
        default="all",
        help="Target scene number (0-7), 'walkthrough' (2-6), or 'all' (default: all)",
    )
    parser.add_argument("--audio-only", action="store_true", help="Generate audio tracks without merging video")
    parser.add_argument("--merge-only", action="store_true", help="Merge existing audio without re-synthesizing")
    parser.add_argument("--assemble", action="store_true", help="Assemble complete master multi-scene video episode")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory path")

    args = parser.parse_args()

    processor = MediaProcessor(args.output_dir)
    synthesizer = VoiceoverSynthesizer(backend=args.tts, voice=args.voice, rate=args.rate)

    target_scenes: Optional[List[int]] = None
    if args.scene.isdigit():
        target_scenes = [int(args.scene)]
    elif args.scene.lower() == "walkthrough":
        target_scenes = [2, 3, 4, 5, 6]
    elif args.scene.lower() == "all":
        target_scenes = list(SCENES.keys())

    print("========================================================================")
    print(" My Profile — Video Blog Voiceover & Video Assembly")
    print(" Series:  Coco Pharmaceuticals Data Governance Journey")
    print(" Persona: Callie Quartile (Data Scientist)")
    print(f" TTS:     {synthesizer.backend.upper()} (Voice: {synthesizer.voice})")
    print(f" Output:  {args.output_dir}")
    print("========================================================================")

    # 1. Generate Audio
    audio_map: Dict[int, Path] = {}
    if not args.merge_only:
        audio_map = await generate_all_audio(synthesizer, processor, target_scenes)
    else:
        # Load existing audio
        for num in (target_scenes or SCENES.keys()):
            scene = SCENES[num]
            f = processor.audio_dir / f"scene{num}_{scene.title.lower().replace(' ', '_').replace(':', '')}.mp3"
            if f.exists():
                audio_map[num] = f

    if args.audio_only:
        print("\n>>> Audio generation complete (--audio-only specified).")
        return

    # 2. Build Narrated Videos
    narrated_clips = build_narrated_videos(processor, audio_map, target_scenes)

    # 3. Assemble Full Episode if requested or if all scenes were built
    if args.assemble or (target_scenes is not None and len(target_scenes) == len(SCENES)):
        assemble_full_episode(processor, narrated_clips)

    print("\n========================================================================")
    print(" Pipeline completed successfully!")
    print(f" Narrated Videos: {processor.narrated_dir}")
    print(f" Audio Tracks:    {processor.audio_dir}")
    print("========================================================================")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
