# Egeria Video Production & Automated Recording Suite

Automated video generation, slide rendering, terminal interaction recording, neural speech synthesis, and video assembly framework for the **Coco Pharmaceuticals Video Series** in `pyegeria` / `my_profile`.

---

## Series Architecture

The repository contains two complementary video suites:
1. **Practitioner Walkthrough (Callie Quartile - Episode 0)**: In-depth interactive walkthrough of the `my_profile.py` textual cockpit (launch, dashboard, to-dos/curation, shop for data, subscriptions, and networks).
2. **Business Value Series (Episodes 1 through 7)**: 7 modular video blog episodes covering enterprise ROI and governance value propositions presented by authentic Coco Pharmaceuticals personas with unique regional accents and voices.

---

## Business Value Episodes & Persona Voice Roster

| Ep # | Title & Value Driver | Lead Persona & Role | Assigned Voice | Accent & Character |
|:---:|:---|:---|:---|:---|
| **0** | **Shop for Data & Governed Research** | Callie Quartile (Data Scientist) | `en-GB-SoniaNeural` | British English (Engaging & Clear) |
| **1** | **Automating Data Privacy & GDPR** | Faith Broker (Privacy Officer & HR) | `en-GB-LibbyNeural` | British English (Authoritative & Rigorous) |
| **2** | **Zero-Touch Data Stewardship** | Peter Profile (Lead Data Steward) | `en-GB-RyanNeural` | British English (Methodical & Enthusiastic) |
| **3** | **Clinical Data Provenance & Integrity** | Dr. Tessa Tube (Lead Clinical Researcher) | `en-US-AriaNeural` | American English (Academic & Authoritative) |
| **4** | **Supply Chain & ESG Sustainability** | Stew Faster (Manufacturing GM) | `en-AU-WilliamMultilingualNeural` | Australian English (Direct & Pragmatic) |
| **5** | **Business Glossaries & Architecture** | Erin Overview (Information Architect) | `en-US-JennyNeural` | American English (Strategic & Visionary) |
| **6** | **Forensic Auditing & Fraud Investigation** | Sidney Seeker (Lead Fraud Auditor) | `en-IE-ConnorNeural` | Irish English (Inquisitive & Sharp) |
| **7** | **The Executive Cockpit & Measuring ROI** | Jules Keeper (CDO) & Reggie Mint (CFO) | `en-GB-ThomasNeural` & `en-US-GuyNeural` | British Executive & American CFO |

---

## Directory Layout

```
recording/
├── episode_specs.py              # Narrative scripts, scene breakdowns & persona voice metadata
├── generate_series_videos.py     # Multi-episode video & slide generator (Episodes 1 to 7)
├── generate_voiceover.py         # Callie Quartile foundational walkthrough generator (Episode 0)
├── run_series.sh                 # Master CLI runner for the Business Value Video Series
├── run_recordings.sh             # Terminal recording runner (VHS tapes + headless pilot)
├── my_profile_full_walkthrough.tape  # Full 1080p VHS terminal recording script
├── record_demo.py                # Headless Textual Pilot automated SVG/PNG frame capture
├── README.md                     # This documentation guide
└── output/
    ├── episode1/ ... episode7/   # Per-episode audio, 1080p slide PNGs, scene clips & master MP4s
    │   ├── audio/                # Scene MP3 voiceovers & full stitched episode audio
    │   ├── slides/               # 1080p Catppuccin Mocha slide cards
    │   └── videos_narrated/      # Assembled master MP4 episodes
    ├── audio/                    # Callie Quartile voiceover tracks
    ├── slides/                   # Callie Quartile intro/outro slides
    ├── videos/                   # Raw raster terminal recordings from VHS
    └── videos_narrated/          # Callie Quartile assembled video blog master
```

---

## Generating & Rebuilding Video Episodes

### 1. Generate the Entire Business Value Series (Episodes 1–7)
```bash
./my_egeria/my_egeria/recording/run_series.sh --all
```

### 2. Generate and Automatically Export to `pdr-vault`
```bash
# Generate all episodes and auto-sync master videos to the shared vault
./my_egeria/my_egeria/recording/run_series.sh --all --export-vault

# Generate a single episode and auto-sync with all audio/slide assets
./my_egeria/my_egeria/recording/run_series.sh --episode 1 --export-vault --all-assets
```

### 3. Generate an Individual Episode
```bash
# Generate Episode 1 (Faith Broker - Data Privacy)
./my_egeria/my_egeria/recording/run_series.sh --episode 1

# Generate Episode 2 (Peter Profile - Stewardship)
./my_egeria/my_egeria/recording/run_series.sh --episode 2

# Generate Episode 4 (Stew Faster - Supply Chain)
./my_egeria/my_egeria/recording/run_series.sh --episode 4
```

### 4. Generate Audio Tracks or Slide Cards Only
```bash
# Audio tracks only
./my_egeria/my_egeria/recording/run_series.sh --all --audio-only

# Slide cards only
./my_egeria/my_egeria/recording/run_series.sh --all --slides-only
```

---

## Centralized Video Vault Synchronization (`pdr-vault`)

To prevent repository bloat while providing a certified, single source of truth for distribution, master video exports and media assets are synchronized to the shared `pdr-vault` repository.

### 1. On-Demand Vault Synchronization
Run the standalone vault exporter anytime to sync master videos to the vault:
```bash
# Default destination ($PDR_VAULT_PATH or /Users/Shared/pdr-vault)
uv run python my_egeria/my_egeria/recording/export_vault.py

# Custom vault location
uv run python my_egeria/my_egeria/recording/export_vault.py --vault-path /Volumes/pdr-vault

# Export all media assets (master MP4s, per-scene audio MP3s, slide PNGs)
uv run python my_egeria/my_egeria/recording/export_vault.py --all-assets

# Dry-run preview
uv run python my_egeria/my_egeria/recording/export_vault.py --dry-run
```

### 2. Destination Resolution Hierarchy
The exporter automatically resolves the vault target in the following order:
1. Explicit `--vault-path` or `--export-vault <path>` CLI argument
2. `PDR_VAULT_PATH` or `EGERIA_VAULT_PATH` environment variable
3. `/Volumes/pdr-vault` (if mounted)
4. `/Users/Shared/pdr-vault` (default local shared directory)
5. `~/pdr-vault`

### 3. Vault Structure & Metadata Index
Upon synchronization, `export_vault.py` writes a `README.md` and `vault_manifest.json` inside the vault directory with file checksums, sizes, durations, and episode personas:
```
pdr-vault/
├── README.md               # Vault index catalog and playback guidance
├── vault_manifest.json     # Machine-readable sync manifest with checksums
├── videos/                 # 1080p Master MP4 video episodes
├── audio/                  # (Optional) Synthesized neural voiceover MP3 tracks
└── slides/                 # (Optional) 1080p Catppuccin Mocha slide PNGs
```

---

## How to Play and View the Rendered Videos

On macOS, you can launch the completed MP4 video files directly in QuickTime Player or open their folders in Finder:

```bash
# Episode 1: Faith Broker (Data Privacy & GDPR)
open my_egeria/my_egeria/recording/output/episode1/videos_narrated/coco_pharma_episode_1_faith_broker.mp4

# Episode 2: Peter Profile (Zero-Touch Stewardship)
open my_egeria/my_egeria/recording/output/episode2/videos_narrated/coco_pharma_episode_2_peter_profile.mp4

# Episode 3: Dr. Tessa Tube (Clinical Data Provenance)
open my_egeria/my_egeria/recording/output/episode3/videos_narrated/coco_pharma_episode_3_dr_tessa_tube.mp4

# Episode 4: Stew Faster (Supply Chain & ESG Sustainability)
open my_egeria/my_egeria/recording/output/episode4/videos_narrated/coco_pharma_episode_4_stew_faster.mp4

# Episode 5: Erin Overview (Business Glossaries & Architecture)
open my_egeria/my_egeria/recording/output/episode5/videos_narrated/coco_pharma_episode_5_erin_overview.mp4

# Episode 6: Sidney Seeker (Forensic Auditing & Fraud Investigation)
open my_egeria/my_egeria/recording/output/episode6/videos_narrated/coco_pharma_episode_6_sidney_seeker.mp4

# Episode 7: Jules Keeper & Reggie Mint (The Executive Cockpit & ROI)
open my_egeria/my_egeria/recording/output/episode7/videos_narrated/coco_pharma_episode_7_jules_keeper_reggie_mint.mp4

# Open the Master Episodes Folder in macOS Finder
open my_egeria/my_egeria/recording/output
```

---

## Required Toolchain & Dependencies

- **Python Environment**: `uv pip install edge-tts Pillow textual rich`
- **System CLI Utilities (Homebrew)**: `brew install vhs ffmpeg ttyd`
- **Container / Video Standards**: 1080p H.264 video (`yuv420p`), 48kHz stereo AAC audio, QuickTime `-bf 0` stream safety, and `faststart` metadata for instant seeking.
