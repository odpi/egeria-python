#!/usr/bin/env python3
"""
Egeria Coco Pharmaceuticals Video Vault Exporter.

Automates the synchronization and export of rendered master videos, audio tracks,
slide graphics, and manifests from the recording output directory into the shared
pdr-vault archival and distribution repository.

Usage:
    uv run python export_vault.py
    uv run python export_vault.py --vault-path /Volumes/pdr-vault
    uv run python export_vault.py --all-assets
    uv run python export_vault.py --dry-run
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR / "output"

DEFAULT_VAULT_ENV_VARS = ["PDR_VAULT_PATH", "EGERIA_VAULT_PATH", "EGERIA_RECORDING_VAULT"]
DEFAULT_CANDIDATE_PATHS = [
    Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/PDR 2/pdr-vault/Peter Videos",
    Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/PDR 2/pdr-vault",
    Path("/Volumes/pdr-vault"),
    Path("/Users/Shared/pdr-vault"),
    Path.home() / "pdr-vault",
    Path("/Volumes/Shared/pdr-vault"),
]


def resolve_vault_path(custom_path: Optional[str] = None) -> Path:
    """Resolve the destination vault path from args, environment variables, or standard candidate locations."""
    if custom_path:
        return Path(custom_path).expanduser().resolve()

    for env_var in DEFAULT_VAULT_ENV_VARS:
        val = os.getenv(env_var)
        if val:
            return Path(val).expanduser().resolve()

    for cand in DEFAULT_CANDIDATE_PATHS:
        if cand.exists() and cand.is_dir():
            return cand.resolve()

    # Default fallback: /Users/Shared/pdr-vault
    return Path("/Users/Shared/pdr-vault").resolve()


def file_checksum(path: Path) -> str:
    """Compute sha256 checksum of a file."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


class VaultExporter:
    """Manages synchronization of recording artifacts to the pdr-vault repository."""

    def __init__(self, vault_path: Path, dry_run: bool = False, all_assets: bool = False):
        self.vault_path = vault_path
        self.dry_run = dry_run
        self.all_assets = all_assets
        self.vault_videos_dir = self.vault_path / "videos"
        self.vault_audio_dir = self.vault_path / "audio"
        self.vault_slides_dir = self.vault_path / "slides"
        self.vault_episodes_dir = self.vault_path / "episodes"

    def ensure_directories(self):
        """Create target vault directories if they do not exist."""
        if not self.dry_run:
            self.vault_path.mkdir(parents=True, exist_ok=True)
            self.vault_videos_dir.mkdir(parents=True, exist_ok=True)
            if self.all_assets:
                self.vault_audio_dir.mkdir(parents=True, exist_ok=True)
                self.vault_slides_dir.mkdir(parents=True, exist_ok=True)
                self.vault_episodes_dir.mkdir(parents=True, exist_ok=True)

    def collect_master_videos(self) -> List[Path]:
        """Collect all master narrated MP4 videos across series and walkthrough outputs."""
        videos = []
        if not OUTPUT_DIR.exists():
            return videos

        # 1. Walkthrough master videos
        walkthrough_narrated = OUTPUT_DIR / "videos_narrated"
        if walkthrough_narrated.exists():
            for mp4 in walkthrough_narrated.glob("*.mp4"):
                if mp4.is_file():
                    videos.append(mp4)

        # 2. Business Value Series episode master videos
        for ep_dir in OUTPUT_DIR.glob("episode*"):
            if ep_dir.is_dir():
                ep_narrated = ep_dir / "videos_narrated"
                if ep_narrated.exists():
                    for mp4 in ep_narrated.glob("*.mp4"):
                        if mp4.is_file() and not mp4.name.startswith("scene_"):
                            videos.append(mp4)

        return sorted(list(set(videos)), key=lambda p: p.name)

    def collect_scene_clips(self) -> List[Path]:
        """Collect individual scene video clips."""
        clips = []
        for ep_dir in OUTPUT_DIR.glob("episode*"):
            if ep_dir.is_dir():
                ep_narrated = ep_dir / "videos_narrated"
                if ep_narrated.exists():
                    for mp4 in ep_narrated.glob("scene_*_narrated.mp4"):
                        clips.append(mp4)
        return sorted(clips, key=lambda p: p.name)

    def collect_audio_tracks(self) -> List[Path]:
        """Collect all MP3 audio tracks."""
        audios = []
        # Walkthrough audio
        walkthrough_audio = OUTPUT_DIR / "audio"
        if walkthrough_audio.exists():
            for mp3 in walkthrough_audio.glob("*.mp3"):
                audios.append(mp3)

        # Series episode audio
        for ep_dir in OUTPUT_DIR.glob("episode*"):
            if ep_dir.is_dir():
                ep_audio = ep_dir / "audio"
                if ep_audio.exists():
                    for mp3 in ep_audio.glob("*.mp3"):
                        audios.append(mp3)
        return sorted(audios, key=lambda p: p.name)

    def collect_slides(self) -> List[Path]:
        """Collect all 1080p slide PNGs."""
        slides = []
        walkthrough_slides = OUTPUT_DIR / "slides"
        if walkthrough_slides.exists():
            for png in walkthrough_slides.glob("*.png"):
                slides.append(png)

        for ep_dir in OUTPUT_DIR.glob("episode*"):
            if ep_dir.is_dir():
                ep_slides = ep_dir / "slides"
                if ep_slides.exists():
                    for png in ep_slides.glob("*.png"):
                        slides.append(png)
        return sorted(slides, key=lambda p: p.name)

    def copy_file(self, src: Path, dest: Path) -> Tuple[bool, str]:
        """Copy file if destination doesn't exist or content differs. Returns (copied, reason)."""
        if not src.exists():
            return False, "source missing"

        if dest.exists():
            if src.stat().st_size == dest.stat().st_size:
                # Fast check passed, verify checksum
                if file_checksum(src) == file_checksum(dest):
                    return False, "up to date"

        if not self.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        return True, "copied"

    def sync(self) -> Dict[str, any]:
        """Execute full vault synchronization."""
        self.ensure_directories()
        master_videos = self.collect_master_videos()
        audio_tracks = self.collect_audio_tracks() if self.all_assets else []
        slides = self.collect_slides() if self.all_assets else []

        print("\n" + "=" * 80)
        print("EGERIA VIDEO RECORDING VAULT SYNCHRONIZATION (pdr-vault)")
        print("=" * 80)
        print(f"Source Directory: {OUTPUT_DIR}")
        print(f"Vault Location:   {self.vault_path}")
        print(f"Mode:             {'DRY-RUN' if self.dry_run else 'ACTIVE SYNC'}")
        print(f"Asset Scope:      {'ALL ASSETS (Videos, Audio, Slides)' if self.all_assets else 'MASTER VIDEOS ONLY'}")
        print("-" * 80)

        results = {
            "timestamp": datetime.now().isoformat(),
            "vault_path": str(self.vault_path),
            "master_videos": [],
            "audio_tracks": [],
            "slides": [],
            "copied_count": 0,
            "skipped_count": 0,
        }

        # Sync master videos
        print(f"\n[1/3] Syncing Master Episode & Walkthrough Videos ({len(master_videos)} files)...")
        has_episode_folders = any(self.vault_path.glob("Episode *")) or self.vault_path.name == "Peter Videos"

        for video_src in master_videos:
            dest = self.vault_videos_dir / video_src.name
            copied, status = self.copy_file(video_src, dest)
            size_mb = video_src.stat().st_size / (1024 * 1024)
            icon = "✓ [COPY]" if copied else "• [SKIP]"
            print(f"  {icon} {video_src.name} ({size_mb:.1f} MB) -> {status}")
            if copied:
                results["copied_count"] += 1
            else:
                results["skipped_count"] += 1
            results["master_videos"].append({
                "filename": video_src.name,
                "size_bytes": video_src.stat().st_size,
                "size_mb": round(size_mb, 2),
                "status": status,
            })

            # Also sync into specific episode folder if present (e.g. Peter Videos / Episode 1 - ...)
            if has_episode_folders:
                m = re.search(r"episode_(\d+)", video_src.name)
                if m:
                    ep_num = m.group(1)
                    matching_folders = list(self.vault_path.glob(f"Episode {ep_num}*"))
                    for ep_folder in matching_folders:
                        ep_dest = ep_folder / video_src.name
                        ep_copied, ep_status = self.copy_file(video_src, ep_dest)
                        if ep_copied:
                            print(f"    ✓ [VAULT FOLDER SYNC] -> {ep_folder.name}/{video_src.name}")

                        if self.all_assets:
                            local_ep_dir = OUTPUT_DIR / f"episode{ep_num}"
                            if local_ep_dir.exists():
                                for sub in ["audio", "captures", "slides", "videos_narrated"]:
                                    src_sub = local_ep_dir / sub
                                    if src_sub.exists():
                                        dest_sub = ep_folder / "output" / sub
                                        dest_sub.mkdir(parents=True, exist_ok=True)
                                        for f in src_sub.glob("*"):
                                            if f.is_file():
                                                self.copy_file(f, dest_sub / f.name)

        # Sync audio tracks if requested
        if self.all_assets and audio_tracks:
            print(f"\n[2/3] Syncing Audio Narration Tracks ({len(audio_tracks)} files)...")
            for audio_src in audio_tracks:
                dest = self.vault_audio_dir / audio_src.name
                copied, status = self.copy_file(audio_src, dest)
                if copied:
                    results["copied_count"] += 1
                else:
                    results["skipped_count"] += 1
                results["audio_tracks"].append({
                    "filename": audio_src.name,
                    "size_bytes": audio_src.stat().st_size,
                    "status": status,
                })
            print(f"  ✓ Processed {len(audio_tracks)} audio files.")
        else:
            print("\n[2/3] Audio Narration Tracks: Skipped (pass --all-assets to include)")

        # Sync slide graphics if requested
        if self.all_assets and slides:
            print(f"\n[3/3] Syncing 1080p Slide Graphics ({len(slides)} files)...")
            for slide_src in slides:
                dest = self.vault_slides_dir / slide_src.name
                copied, status = self.copy_file(slide_src, dest)
                if copied:
                    results["copied_count"] += 1
                else:
                    results["skipped_count"] += 1
                results["slides"].append({
                    "filename": slide_src.name,
                    "size_bytes": slide_src.stat().st_size,
                    "status": status,
                })
            print(f"  ✓ Processed {len(slides)} slide images.")
        else:
            print("\n[3/3] Slide Graphics: Skipped (pass --all-assets to include)")

        # Generate Index Manifest in Vault
        self.generate_manifest(results)

        print("\n" + "=" * 80)
        print("VAULT SYNCHRONIZATION COMPLETE!")
        print(f"  • Files Copied / Updated: {results['copied_count']}")
        print(f"  • Files Up-to-Date:       {results['skipped_count']}")
        print(f"  • Vault Directory:        {self.vault_path}")
        print("=" * 80 + "\n")
        return results

    def generate_manifest(self, sync_results: Dict[str, any]):
        """Generate manifest JSON and Markdown index inside the vault directory."""
        if self.dry_run:
            return

        manifest_path = self.vault_path / "vault_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(sync_results, f, indent=2)

        # Markdown Index
        index_path = self.vault_path / "README.md"
        content = [
            "# Coco Pharmaceuticals Video Vault (`pdr-vault`)",
            "",
            "Central repository and distribution archive for certified master video blog episodes,",
            "practitioner walkthroughs, neural voiceover tracks, and slide decks.",
            "",
            f"**Last Synchronized:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Total Master Videos:** {len(sync_results['master_videos'])}",
            "",
            "---",
            "",
            "## Master Video Episodes (`videos/`)",
            "",
            "| Video File | Size | Description | Lead Persona / Topic | Technical Blog Reference |",
            "|:---|:---:|:---|:---|:---|",
            "| `coco_pharma_my_profile_complete_video_blog.mp4` | Master | Full Episode 0 Video Blog | Callie Quartile (Data Scientist) | [Blog 6](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-6-egeria-6-3-release), [Blog 8](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-8-building-the-data-mesh), [Blog 10](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-10-exchanging-dcat-documents) |",
            "| `my_profile_full_walkthrough_narrated.mp4` | Master | Continuous Terminal Walkthrough | Callie Quartile (Data Scientist) | [Blog 6](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-6-egeria-6-3-release) (Autonomous Housekeeping) |",
            "| `coco_pharma_episode_1_faith_broker.mp4` | Master | Episode 1: Data Privacy & GDPR | Faith Broker (Privacy Officer) | [Blog 7](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-7-supporting-security-professionals) (NIST CSF 2.0 & ISO 27001) |",
            "| `coco_pharma_episode_2_peter_profile.mp4` | Master | Episode 2: Zero-Touch Stewardship | Peter Profile (Lead Steward) | [Blog 6](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-6-egeria-6-3-release) (Connectors: Simon, Pasteur, Mendel) |",
            "| `coco_pharma_episode_3_dr_tessa_tube.mp4` | Master | Episode 3: Clinical Data Provenance | Dr. Tessa Tube (Lead Researcher) | [Blog 8](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-8-building-the-data-mesh) (Bitol ODCS) & [Blog 9](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-9-business-flows-from-lineage) (5 Lineage Layers) |",
            "| `coco_pharma_episode_4_stew_faster.mp4` | Master | Episode 4: Supply Chain & ESG | Stew Faster (Manufacturing GM) | [Blog 10](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-10-exchanging-dcat-documents) (W3C DCAT v3 JSON-LD) |",
            "| `coco_pharma_episode_5_erin_overview.mp4` | Master | Episode 5: Business Glossaries | Erin Overview (Info Architect) | [Blog 9](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-9-business-flows-from-lineage) (OpenLineage in PostgreSQL) |",
            "| `coco_pharma_episode_6_sidney_seeker.mp4` | Master | Episode 6: Fraud & Audit Lineage | Sidney Seeker (Fraud Auditor) | [Blog 6](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-6-egeria-6-3-release) & [Blog 7](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-7-supporting-security-professionals) (STRIDE & Reversibility) |",
            "| `coco_pharma_episode_7_jules_keeper_reggie_mint.mp4` | Master | Episode 7: Executive Cockpit & ROI | Jules Keeper (CDO) & Reggie Mint (CFO) | [Blog 6](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-6-egeria-6-3-release), [Blog 7](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-7-supporting-security-professionals), [Blog 8](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-8-building-the-data-mesh) |",
            "",
            "---",
            "",
            "## Technical Reference Links (Mandy Chessell Blog Series)",
            "",
            "- **Blog 6 (Release 6.3):** [Egeria 6.3: A Metadata Platform Built for the Long Run](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-6-egeria-6-3-release) — Housekeeping connectors (`Simon`, `Pasteur`, `Mendel`, `Baudot`, `Wedgwood`), native `Undo`/`Restore`, and fail-closed zones.",
            "- **Blog 7 (Security):** [Supporting Security Professionals: Frameworks, Threat Models & Findings](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-7-supporting-security-professionals) — NIST CSF 2.0, NIST SP 800-53 OSCAL catalogs, ISO 27001 Statement of Applicability, and STRIDE threat modeling.",
            "- **Blog 8 (Data Mesh):** [Building the Data Mesh: Products, Subscriptions, Contracts & Dependencies](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-8-building-the-data-mesh) — Bitol Open Data Contract Standard (ODCS), Open Data Product Standard (ODPS), and `Darwin` runtime dependency validation.",
            "- **Blog 9 (Lineage):** [From Pipeline Runs to Business Flows: Extracting Lineage Layers](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-9-business-flows-from-lineage) — PostgreSQL OpenLineage analysis (800k+ events in ~3s), five supply chain views, and bounded exploration.",
            "- **Blog 10 (DCAT):** [Speaking the Language of Open Data: Exchanging DCAT Documents](https://github.com/odpi/egeria-docs/tree/main/blogs/blog-10-exchanging-dcat-documents) — W3C DCAT v3 JSON-LD exchange, DCAT Files/Event receivers, and DCAT Publishers.",
            "",
            "---",
            "",
            "## Storage & Playback Notes",
            "",
            "- **Video Format:** 1080p Full HD H.264 (`yuv420p`), 25 fps, `-bf 0` QuickTime compatible.",
            "- **Audio Format:** 48kHz Stereo AAC (192 kbps).",
            "- **Metadata:** Faststart `moov` container atom enabled for instant streaming and playback.",
            "",
        ]
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))


def export_to_vault(vault_path: Optional[str] = None, all_assets: bool = False, dry_run: bool = False) -> Dict[str, any]:
    """Helper function to run export directly from other Python scripts."""
    target_path = resolve_vault_path(vault_path)
    exporter = VaultExporter(target_path, dry_run=dry_run, all_assets=all_assets)
    return exporter.sync()


def parse_args():
    parser = argparse.ArgumentParser(description="Export Egeria Coco Pharmaceuticals video media to pdr-vault")
    parser.add_argument(
        "--vault-path",
        "-p",
        type=str,
        default=None,
        help="Custom destination path for pdr-vault (default: $PDR_VAULT_PATH or /Users/Shared/pdr-vault)",
    )
    parser.add_argument(
        "--all-assets",
        "-a",
        action="store_true",
        help="Export all media assets including per-scene MP3s, slide PNGs, and captures (default: master MP4s only)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Preview files that would be synchronized without copying",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    export_to_vault(vault_path=args.vault_path, all_assets=args.all_assets, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
