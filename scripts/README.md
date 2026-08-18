<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# scripts

Standalone maintenance/audit scripts that aren't part of the installed
package or the pytest suite.

- `omvs_audit.py` — cross-checks every `_async_*` method in
  `pyegeria/omvs/*.py` against its ground-truth `pyegeria/http clients/*.http`
  file (URL, HTTP verb, request-body class) and reports MISSING/VERB
  MISMATCH/PATH MISMATCH/BODY MISMATCH/ELSEWHERE/LINT findings (see
  `omvs_audit_report.md` at the repo root for the latest run's output).
  `python scripts/omvs_audit.py [--report PATH] [--service NAME] [--quiet]`;
  exits 1 on any confirmed defect, so it can gate CI.
- `safe_git_sync.sh` — stashes all local changes (including untracked),
  fetches and rebases onto a remote branch, then restores the stash — aborts
  and restores on failure so local work is never lost.
  `safe_git_sync.sh PROJECT_DIR [REMOTE] [BRANCH]`.
