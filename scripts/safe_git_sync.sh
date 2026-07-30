#!/bin/bash
# safe_git_sync.sh — Safely sync a git repo from a remote, preserving local work.
#
# Usage: safe_git_sync.sh PROJECT_DIR [REMOTE] [BRANCH]
#
#   PROJECT_DIR  Path to the git repository (required)
#   REMOTE       Remote to sync from (optional; auto-detects 'upstream' or 'origin')
#   BRANCH       Branch to sync (optional; defaults to 'main')
#
# Behaviour:
#   1. Stashes ALL local changes (including untracked files) before syncing.
#   2. Fetches from the remote and rebases the local branch on top.
#   3. On failure, aborts the rebase and restores the stash so no work is lost.
#   4. Logs each step with a timestamp.

set -euo pipefail

# ── Arguments ─────────────────────────────────────────────────────────────────
PROJECT_DIR="${1:-}"
if [[ -z "$PROJECT_DIR" ]]; then
    echo "ERROR: PROJECT_DIR is required." >&2
    echo "Usage: $0 PROJECT_DIR [REMOTE] [BRANCH]" >&2
    exit 1
fi

REQUESTED_REMOTE="${2:-}"
BRANCH="${3:-main}"

# ── Helpers ───────────────────────────────────────────────────────────────────
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
fail() { log "ERROR: $*" >&2; exit 1; }

# ── Enter repository ──────────────────────────────────────────────────────────
cd "$PROJECT_DIR" || fail "Cannot cd into '$PROJECT_DIR'."
log "=== Starting safe_git_sync for '$PROJECT_DIR' ==="

# Verify this is a git repo
git rev-parse --git-dir > /dev/null 2>&1 || fail "'$PROJECT_DIR' is not a git repository."

# ── Detect remote ─────────────────────────────────────────────────────────────
if [[ -n "$REQUESTED_REMOTE" ]]; then
    REMOTE="$REQUESTED_REMOTE"
else
    # Prefer 'upstream'; fall back to 'origin'
    if git remote get-url upstream > /dev/null 2>&1; then
        REMOTE="upstream"
    elif git remote get-url origin > /dev/null 2>&1; then
        REMOTE="origin"
    else
        fail "No usable remote found (tried 'upstream' and 'origin')."
    fi
fi
log "Using remote: $REMOTE  branch: $BRANCH"

# ── Check for local changes (modified, staged, AND untracked) ─────────────────
HAS_STASH=false
if [[ -n "$(git status --porcelain)" ]]; then
    log "Local changes detected — stashing (including untracked files)..."
    STASH_MSG="safe_git_sync auto-stash $(date '+%Y-%m-%d %H:%M:%S')"
    git stash push --include-untracked -m "$STASH_MSG" \
        || fail "git stash failed. Aborting to protect local work."
    HAS_STASH=true
    log "Stash created: '$STASH_MSG'"
else
    log "Working tree is clean — no stash needed."
fi

# ── Fetch ─────────────────────────────────────────────────────────────────────
log "Fetching from $REMOTE..."
git fetch "$REMOTE" "$BRANCH" || fail "git fetch $REMOTE $BRANCH failed."

# ── Up-to-date check ──────────────────────────────────────────────────────────
REMOTE_HASH=$(git rev-parse "$REMOTE/$BRANCH" 2>/dev/null) \
    || fail "Cannot resolve $REMOTE/$BRANCH after fetch."
LOCAL_HASH=$(git rev-parse HEAD)

if [[ "$REMOTE_HASH" == "$LOCAL_HASH" ]]; then
    log "Already up to date with $REMOTE/$BRANCH."
else
    log "Remote is ahead — rebasing local $BRANCH onto $REMOTE/$BRANCH..."

    if git rebase "$REMOTE/$BRANCH"; then
        log "Rebase succeeded."
    else
        log "Rebase failed — aborting to restore clean state."
        git rebase --abort 2>/dev/null || true

        if [[ "$HAS_STASH" == true ]]; then
            log "Restoring stash after failed rebase..."
            git stash pop || log "WARNING: stash pop failed — run 'git stash list' to recover."
        fi

        fail "Rebase failed. Conflicts must be resolved manually. Repo left at pre-fetch state."
    fi
fi

# ── Restore stash ─────────────────────────────────────────────────────────────
if [[ "$HAS_STASH" == true ]]; then
    log "Restoring stashed changes..."
    if git stash pop; then
        log "Stash restored successfully."
    else
        log "WARNING: stash pop produced conflicts — run 'git stash list' and resolve manually."
    fi
fi

log "=== Sync complete for '$PROJECT_DIR' ==="
