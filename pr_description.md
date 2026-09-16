### PR Description: Enhance FOSS Compliance and OSSF Scorecard Posture

This PR significantly enhances the repository's alignment with open-source best practices, specifically targeting a high **OSSF Scorecard** score and improved community health. It introduces automated security checks, supply-chain transparency (SBOMs), and formalized governance documentation.

#### Key Changes

**1. Security Automation & Supply Chain**
- **OSSF Scorecard Action**: Added `.github/workflows/scorecard.yml` (pinned to stable SHA) to automatically analyze the project's security posture.
- **SBOM Generation**: Integrated `cyclonedx-py` into the release workflow to generate CycloneDX SBOMs (JSON and XML) for every release.
- **Continuous Integration**: Added `python-tests.yml` to run unit tests on every Pull Request and push to `main`, ensuring baseline code quality.
- **Security Policy**: Completed the `SECURITY.md` file and documented the SBOM and vulnerability reporting process.
- **Dependency Management**: Restricted supported Python versions to `>=3.12, <3.14` in `pyproject.toml` to resolve resolution conflicts and refreshed `uv.lock`.

**2. Community Health & Governance**
- **Code of Conduct**: Added `CODE_OF_CONDUCT.md` aligned with ODPi Egeria, including modern sections on responsible AI usage.
- **Governance**: Added `GOVERNANCE.md` to clarify decision-making processes.
- **Contribution Guidelines**: Enhanced `CONTRIBUTING.md` with explicit **Developer Certificate of Origin (DCO)** instructions and `Signed-off-by` requirements.
- **Attribution**: Added `CITATION.cff` for academic and professional attribution.
- **Ownership**: Added `CODEOWNERS` to formalize review responsibilities.

**3. Test Isolation & CI Reliability**
- **Manual Script Isolation**: Renamed manual scripts in `tests/micro-tests/` to `manual_*.py` to prevent them from being picked up by `pytest` during automated runs, resolving "file not found" errors in CI.
- **Unit Test Marking**: Updated `tests/micro-tests/conftest.py` to automatically mark all tests in that directory as `unit`, ensuring correct test selection with `pytest -m unit`.

**4. Visibility**
- **README Badges**: Added a comprehensive suite of badges for OSSF Scorecard, Python Tests, CII Best Practices, Governance, and Code of Conduct.

---

#### Checklist
- [x] All commits are signed off (DCO compliant).
- [x] GitHub Actions workflows for testing and security analysis added.
- [x] Documentation for community health and security updated.
- [x] Dependencies for SBOM generation integrated into workflows.
- [x] Merged latest upstream changes and resolved conflicts in `uv.lock`.

#### Verification Results
- **Unit Tests**: `uv run pytest tests/micro-tests/ -m unit` passes locally.
- **Workflow Syntax**: Validated the YAML structure for all new GitHub Actions.
- **Dependency Resolution**: Confirmed that `uv lock` succeeds with the new version constraints.
