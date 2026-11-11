#!/usr/bin/env bash
# ==============================================================================
# Automated Terminal Recording Runner for My Profile Video
# Series: Coco Pharmaceuticals Data Governance Journey (Callie Quartile)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
VIDEOS_DIR="${OUTPUT_DIR}/videos"
GIFS_DIR="${OUTPUT_DIR}/gifs"
CAPTURES_DIR="${OUTPUT_DIR}/captures"

mkdir -p "${VIDEOS_DIR}" "${GIFS_DIR}" "${CAPTURES_DIR}"

export EGERIA_USER_NAME="${EGERIA_USER_NAME:-calliequartile}"
unset NO_COLOR || true
export FORCE_COLOR=1
export COLORTERM=truecolor
export TERM=xterm-256color

print_header() {
    echo "========================================================================"
    echo " My Profile — Automated Terminal Recording Suite"
    echo " Persona: Callie Quartile (Data Scientist, Coco Pharmaceuticals)"
    echo "========================================================================"
    echo " Output directory: ${OUTPUT_DIR}"
    echo " Egeria User:      ${EGERIA_USER_NAME}"
    echo "========================================================================"
}

check_vhs() {
    if ! command -v vhs &>/dev/null; then
        echo ""
        echo "[WARNING] Charm's 'vhs' CLI is not found on your PATH."
        echo "To record high-resolution .mp4 / .gif terminal videos:"
        echo "  • macOS:       brew install vhs ffmpeg ttyd"
        echo "  • Debian/Ubuntu: sudo apt-get install ffmpeg ttyd && go install github.com/charmbracelet/vhs@latest"
        echo ""
        echo "Falling back to Textual Pilot SVG screenshot recorder..."
        run_pilot_all
        exit 0
    fi
}

run_tape() {
    local tape_file="$1"
    local base_name
    base_name="$(basename "${tape_file}" .tape)"

    echo ""
    echo ">>> Running VHS recording for: ${base_name} ..."
    cd "${SCRIPT_DIR}"
    vhs "${tape_file}"

    # Move output files if generated in current dir
    if [[ -f "${SCRIPT_DIR}/${base_name}.mp4" ]]; then
        mv "${SCRIPT_DIR}/${base_name}.mp4" "${VIDEOS_DIR}/"
        echo "  [OUTPUT MP4] ${VIDEOS_DIR}/${base_name}.mp4"
    fi
    if [[ -f "${SCRIPT_DIR}/${base_name}.gif" ]]; then
        mv "${SCRIPT_DIR}/${base_name}.gif" "${GIFS_DIR}/"
        echo "  [OUTPUT GIF] ${GIFS_DIR}/${base_name}.gif"
    fi
    # Move any captured PNGs to captures directory
    find "${SCRIPT_DIR}" -maxdepth 1 -name "*.png" -exec mv {} "${CAPTURES_DIR}/" \;
}

run_walkthrough() {
    check_vhs
    run_tape "${SCRIPT_DIR}/my_profile_full_walkthrough.tape"
}

run_scenes_all() {
    check_vhs
    echo "Recording all individual scene tapes (Scenes 2 to 6)..."
    for scene_tape in "${SCRIPT_DIR}/scenes"/scene*.tape; do
        if [[ -f "${scene_tape}" ]]; then
            run_tape "${scene_tape}"
        fi
    done
}

run_scene() {
    local num="$1"
    check_vhs
    local files=("${SCRIPT_DIR}/scenes/scene${num}_"*.tape)
    if [[ -f "${files[0]}" ]]; then
        run_tape "${files[0]}"
    else
        echo "[ERROR] No tape found for scene number: ${num}"
        exit 1
    fi
}

run_pilot_all() {
    echo ""
    echo ">>> Running Textual Pilot Headless Demo Recorder..."
    local repo_root
    repo_root="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
    if command -v uv &>/dev/null; then
        uv run python "${SCRIPT_DIR}/record_demo.py" --output-dir "${CAPTURES_DIR}"
    else
        PYTHONPATH="${repo_root}:${PYTHONPATH:-}" python3 "${SCRIPT_DIR}/record_demo.py" --output-dir "${CAPTURES_DIR}"
    fi
}

run_voiceover() {
    local assemble_flag="${1:-}"
    echo ""
    echo ">>> Running Automated Voiceover & Video Assembly Pipeline..."
    local repo_root
    repo_root="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
    local extra_args=()
    if [[ "${assemble_flag}" == "--assemble" ]]; then
        extra_args+=("--assemble")
    elif [[ "${assemble_flag}" == "--audio-only" ]]; then
        extra_args+=("--audio-only")
    fi

    if command -v uv &>/dev/null; then
        uv run python "${SCRIPT_DIR}/generate_voiceover.py" --output-dir "${OUTPUT_DIR}" "${extra_args[@]}"
    else
        PYTHONPATH="${repo_root}:${PYTHONPATH:-}" python3 "${SCRIPT_DIR}/generate_voiceover.py" --output-dir "${OUTPUT_DIR}" "${extra_args[@]}"
    fi
}

usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Recording Options:"
    echo "  --walkthrough   Record the continuous full walkthrough video tape (Scenes 2-6)"
    echo "  --scenes        Record all individual scene video tapes (Scenes 2, 3, 4, 5, 6)"
    echo "  --scene <2-6>   Record a specific scene tape (e.g. $0 --scene 5)"
    echo "  --pilot         Run Python Textual Pilot SVG screenshot capture"
    echo ""
    echo "Voiceover & Assembly Options:"
    echo "  --narrate       Generate Callie Quartile's voiceover & merge with video clips"
    echo "  --assemble      Generate narration and assemble complete master video episode (Scenes 0-7)"
    echo "  --audio-only    Generate spoken audio MP3 tracks without video merging"
    echo ""
    echo "Master Workflow:"
    echo "  --all           Record walkthrough, scenes, pilot SVGs, voiceover, and master episode"
    echo "  --help          Display this help message"
    echo ""
}

print_header

if [[ $# -eq 0 ]]; then
    run_walkthrough
    exit 0
fi

case "$1" in
    --walkthrough)
        run_walkthrough
        ;;
    --scenes)
        run_scenes_all
        ;;
    --scene)
        if [[ -z "${2:-}" ]]; then
            echo "[ERROR] --scene requires a scene number (2, 3, 4, 5, or 6)"
            exit 1
        fi
        run_scene "$2"
        ;;
    --pilot)
        run_pilot_all
        ;;
    --narrate)
        run_voiceover ""
        ;;
    --assemble)
        run_voiceover "--assemble"
        ;;
    --audio-only)
        run_voiceover "--audio-only"
        ;;
    --all)
        run_walkthrough
        run_scenes_all
        run_pilot_all
        run_voiceover "--assemble"
        ;;
    --help|-h)
        usage
        ;;
    *)
        echo "[ERROR] Unknown option: $1"
        usage
        exit 1
        ;;
esac

echo ""
echo "========================================================================"
echo " Recording session completed successfully!"
echo " Check artifacts in: ${OUTPUT_DIR}"
echo "========================================================================"
