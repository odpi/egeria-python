<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# scripts

Standalone maintenance/audit scripts that aren't part of the installed
package or the pytest suite.

- `omvs_audit.py` — cross-checks every `_async_*` method in
  `pyegeria/omvs/*.py` against its reference `pyegeria/http-clients/*.http`
  file (URL, HTTP verb, request-body class) and reports MISSING/VERB
  MISMATCH/PATH MISMATCH/BODY MISMATCH/ELSEWHERE/LINT findings (see
  `omvs_audit_report.md` at the repo root for the latest run's output).
  When an Egeria Java checkout is present (`--java-dir`, `$EGERIA_JAVA_DIR`,
  default `~/localGit/egeria-v6/egeria`) it also checks against the Spring
  `@RequestBody` types: JAVA-BODY REJECTED / CLASS-IGNORED, UNKNOWN-CLASS,
  JAVA-MISSING and HTTP-vs-JAVA, plus field-level FIELD-DROP / CLIENT-DROP /
  MODEL-FIELD gaps (ISSUE-163/164). `--no-java` skips them.
  `python scripts/omvs_audit.py [--report PATH] [--service NAME] [--quiet]`;
  exits 1 on any confirmed defect, so it can gate CI.
- `safe_git_sync.sh` — stashes all local changes (including untracked),
  fetches and rebases onto a remote branch, then restores the stash — aborts
  and restores on failure so local work is never lost.
  `safe_git_sync.sh PROJECT_DIR [REMOTE] [BRANCH]`.
