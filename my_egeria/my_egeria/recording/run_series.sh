#!/usr/bin/env bash
# ==============================================================================
# Egeria Coco Pharmaceuticals Business Value Video Series Orchestrator
#
# Generates 1080p slide cards, synthesized neural voiceovers, and assembled
# narrated MP4 videos for Episodes 1 through 7 of the Business Value Series.
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
cd "${PROJECT_ROOT}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================================================${NC}"
    echo -e "${BLUE}  Coco Pharmaceuticals Business Value Video Series Orchestrator${NC}"
    echo -e "${BLUE}========================================================================${NC}"
}

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --all                 Generate all 7 episodes (default)"
    echo "  --episode <1-7>       Generate a specific episode (e.g. --episode 1)"
    echo "  --record              Run headless client screen captures before video build"
    echo "  --record-only         Run headless client screen captures only without video build"
    echo "  --audio-only          Generate speech audio tracks only"
    echo "  --slides-only         Generate 1080p slide PNGs only"
    echo "  --export-vault [PATH] Automatically sync generated videos to pdr-vault"
    echo "  --all-assets          Include audio tracks and slide graphics in vault export"
    echo "  --list                List all available episodes and persona profiles"
    echo "  --help                Show this help message"
    echo ""
    exit 0
}

EPISODE_ARG="all"
EXTRA_FLAGS=""
DO_RECORD=false
RECORD_ONLY=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --all)
            EPISODE_ARG="all"
            shift
            ;;
        --episode)
            EPISODE_ARG="episode$2"
            shift 2
            ;;
        --record)
            DO_RECORD=true
            shift
            ;;
        --record-only)
            RECORD_ONLY=true
            DO_RECORD=true
            shift
            ;;
        --audio-only)
            EXTRA_FLAGS="${EXTRA_FLAGS} --audio-only"
            shift
            ;;
        --slides-only)
            EXTRA_FLAGS="${EXTRA_FLAGS} --slides-only"
            shift
            ;;
        --export-vault)
            if [[ $# -gt 1 && ! "$2" =~ ^-- ]]; then
                EXTRA_FLAGS="${EXTRA_FLAGS} --export-vault $2"
                shift 2
            else
                EXTRA_FLAGS="${EXTRA_FLAGS} --export-vault"
                shift
            fi
            ;;
        --all-assets)
            EXTRA_FLAGS="${EXTRA_FLAGS} --all-assets"
            shift
            ;;
        --list)
            EXTRA_FLAGS="${EXTRA_FLAGS} --list-episodes"
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo -e "${YELLOW}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

print_header

# Verify Python environment
if command -v uv &> /dev/null; then
    PY_CMD="uv run python"
else
    PY_CMD="python3"
fi

# Run headless client screen captures if requested
if [[ "${DO_RECORD}" = true ]]; then
    echo -e "\n${BLUE}▶ Running Headless Screen Captures for ${EPISODE_ARG}...${NC}"
    ${PY_CMD} "${SCRIPT_DIR}/record_episode_screens.py" --episode "${EPISODE_ARG}"
fi

if [[ "${RECORD_ONLY}" = true ]]; then
    echo -e "\n${GREEN}✓ Headless screen captures complete!${NC}"
    echo -e "Screen captures available in: ${SCRIPT_DIR}/output/\n"
    exit 0
fi

${PY_CMD} "${SCRIPT_DIR}/generate_series_videos.py" --episode "${EPISODE_ARG}" ${EXTRA_FLAGS}

echo -e "\n${GREEN}✓ Video series orchestration complete!${NC}"
echo -e "Outputs available in: ${SCRIPT_DIR}/output/\n"
