# Releasing pyegeria

The release checklist, in order. The release itself (PyPI, GitHub release) is run by
`.github/workflows/release.yml` when a `v<version>` tag is pushed.

1. **Feature PRs merged** to `main` (squash-merge).
2. **Version bump PR**: `pyproject.toml` and `uv.lock` only (`uv lock`), CI green, squash-merged.
3. **3.13 micro-tests** pass on the bump commit (`uv run -p 3.13 pytest tests/micro-tests/`).
4. **Dr.Egeria round-trip probe gate green, or its failure explained in the PR.** Run the
   "Dr.Egeria round-trip probe gate" workflow (`workflow_dispatch`, or label the PR `release`), or locally
   `uv run -p 3.13 python scripts/dr_egeria_roundtrip_probe/gate.py` on a host with Docker (attach
   `RESULTS-<UTC>.md` and the gate output to the PR). Improvements mean the PR updates
   `scripts/dr_egeria_roundtrip_probe/baseline/<digest>.json` (`--rebaseline`, one-line reason per changed
   row). A new Egeria digest means a new baseline file. See `scripts/dr_egeria_roundtrip_probe/README.md`;
   the probe only ever runs against its own scratch Egeria.
5. **Check PyPI first:** `https://pypi.org/pypi/pyegeria/<version>/json` must return 404 (a local upload
   would make the tag-triggered publish fail).
6. **Tag** the merge commit with a lightweight `v<version>` tag and push it to `upstream`; approve the
   `release` environment deployment when asked.
7. **Verify** the version on PyPI and the GitHub release; prepend any behaviour change hidden in a PR
   title to the release notes.
