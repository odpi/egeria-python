# My Profile — Automated Terminal Recording Suite

**Series:** *Coco Pharmaceuticals Data Governance Journey*  
**Presenter Persona:** Callie Quartile (Data Scientist)  
**Companion Script:** [`../VIDEO_SCRIPT_DRAFT.md`](../VIDEO_SCRIPT_DRAFT.md)  

This directory contains production-ready automated recording scripts that capture high-definition terminal screencasts and vector SVG frames of `my_profile.py` for video blogs, tutorials, presentations, and documentation.

---

## 📁 Directory Structure

```text
recording/
├── my_profile_full_walkthrough.tape  # Full continuous end-to-end VHS recording (Scenes 2-6)
├── scenes/
│   ├── scene2_launch_and_startup.tape            # Scene 2: Splash screen, async loading, continue
│   ├── scene3_main_dashboard.tape                # Scene 3: Dashboard grid, roles & team drill-down
│   ├── scene4_curation_todos_comments.tape       # Scene 4: To-Dos (Ctrl+T), Comments (Ctrl+O/N), Bookmarks (Ctrl+K/B)
│   ├── scene5_shop_for_data.tape                 # Scene 5: Catalogs, sample data (Ctrl+L), subscribe (Ctrl+U)
│   └── scene6_network_communities_feedback.tape # Scene 6: My Network, communities, feedback (Ctrl+F), tech types
├── generate_voiceover.py               # AI Text-to-Speech voiceover generator & video assembly pipeline
├── record_demo.py                      # Python Textual Pilot automated driver (generates vector SVG captures)
├── run_recordings.sh                   # Master runner script for VHS, Pilot captures, and narration
├── output/                             # Generated recording artifacts (ignored by git)
│   ├── audio/                          # Synthesized MP3 narration audio tracks per scene & full episode
│   ├── videos/                         # Rendered raw 1080p MP4 videos
│   ├── videos_narrated/                # 1080p MP4 videos with synchronized voiceover narration
│   ├── gifs/                           # Animated GIF screencasts
│   ├── slides/                         # 1080p PNG slide title cards
│   └── captures/                       # Timestamped SVG/PNG screenshots per scene
└── README.md                           # This documentation guide
```

---

## 🛠️ Prerequisites & Installation

### Option A: VHS Recording (Recommended for MP4/GIF Video Capture)
Charm's [VHS](https://github.com/charmbracelet/vhs) runs headless terminal scripts with exact millisecond timings and renders 1080p, 60fps MP4 and GIF videos.

- **macOS (Homebrew):**
  ```bash
  brew install vhs ffmpeg ttyd
  ```
- **Linux (Debian / Ubuntu):**
  ```bash
  sudo apt-get install ffmpeg ttyd
  go install github.com/charmbracelet/vhs@latest
  ```

### Option B: Textual Pilot Recorder (Python Native, No External Binary Needed)
Built on Textual's async `Pilot` framework, included out of the box with the project dependencies (`uv sync`).

---

## 🚀 Running Recordings

### 1. Master Runner Script (`run_recordings.sh`)

```bash
# Make sure the script is executable
chmod +x my_egeria/my_egeria/recording/run_recordings.sh

# Record the full continuous walkthrough (Scenes 2 to 6)
./my_egeria/my_egeria/recording/run_recordings.sh --walkthrough

# Record all individual scene clips
./my_egeria/my_egeria/recording/run_recordings.sh --scenes

# Record a specific scene clip (e.g. Scene 5: Shop for Data)
./my_egeria/my_egeria/recording/run_recordings.sh --scene 5

# Generate all vector SVG screenshots via Textual Pilot
./my_egeria/my_egeria/recording/run_recordings.sh --pilot

# Generate AI Voiceover narration (Callie Quartile) and merge with recorded video clips
./my_egeria/my_egeria/recording/run_recordings.sh --narrate

# Assemble the complete 5-minute master video blog episode (Scenes 0-7)
./my_egeria/my_egeria/recording/run_recordings.sh --assemble

# Run everything (walkthrough + all individual scenes + SVG captures + narration + master episode)
./my_egeria/my_egeria/recording/run_recordings.sh --all
```

### 2. Running Voiceover Generator Directly (`generate_voiceover.py`)

```bash
# Generate narration and merge videos using Edge Neural TTS (default: en-GB-SoniaNeural)
uv run python my_egeria/my_egeria/recording/generate_voiceover.py --assemble

# Use native macOS speech synthesizer (offline fallback)
uv run python my_egeria/my_egeria/recording/generate_voiceover.py --tts say --voice "Flo (English (UK))" --assemble

# Generate narration audio files only
uv run python my_egeria/my_egeria/recording/generate_voiceover.py --audio-only

# Target a specific scene (e.g. Scene 5)
uv run python my_egeria/my_egeria/recording/generate_voiceover.py --scene 5
```

### 3. Running Individual VHS Tapes Directly

```bash
cd my_egeria/my_egeria/recording

# Run full walkthrough tape
vhs my_profile_full_walkthrough.tape

# Run a specific scene tape
vhs scenes/scene5_shop_for_data.tape
```

### 4. Running the Python Pilot Driver Directly

```bash
# Record all scenes headlessly to SVG
uv run python my_egeria/my_egeria/recording/record_demo.py

# Record a specific scene
uv run python my_egeria/my_egeria/recording/record_demo.py --scene 4

# Specify custom output directory
uv run python my_egeria/my_egeria/recording/record_demo.py --output-dir ./my_captures
```

---

## ⚙️ Environment Configuration

You can customize the target persona and Egeria platform environment variables before executing recordings:

```bash
# Set persona to Callie Quartile (default)
export EGERIA_USER_NAME="calliequartile"

# Set custom view server or platform URL if recording against live or demo servers
export EGERIA_VIEW_SERVER="qs-view-server"
export EGERIA_PLATFORM_URL="https://127.0.0.1:9443"
```

---

## 🎬 Video Production Workflow

1. **Audio Narration:** Record spoken voiceover according to [`VIDEO_SCRIPT_DRAFT.md`](../VIDEO_SCRIPT_DRAFT.md).
2. **Video Capture:** Execute `./run_recordings.sh --walkthrough` to generate `output/videos/my_profile_full_walkthrough.mp4` (or use individual scene `.mp4` files from `output/videos/`).
3. **Assembly & Editing:** In your video editor (e.g. DaVinci Resolve, Premiere Pro, Camtasia, CapCut, or via `ffmpeg`):
   - Place the presenter intro / title card (Scene 0 & Scene 1).
   - Sync the recorded `.mp4` terminal clips with Callie's narration for Scenes 2 through 6.
   - Insert lower-thirds, hotkey overlays (`Ctrl+T`, `Ctrl+O`, `Ctrl+L`, `Ctrl+U`), and zoom spotlights onto active dialogs.
   - Attach the closing call to action and link end cards (Scene 7).
