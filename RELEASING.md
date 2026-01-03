# Release Process for pyegeria

We follow Semantic Versioning (SemVer). Releases are automated via GitHub Actions when a tag is pushed.

## Steps to Release

1.  **Update Version**: Update the version in `pyproject.toml`.
    ```bash
    # Example: bump to 1.1.0
    sed -i 's/version = ".*"/version = "1.1.0"/' pyproject.toml
    ```
2.  **Commit and Push**:
    ```bash
    git add pyproject.toml
    git commit -m "chore: release v1.1.0"
    git push origin main
    ```
3.  **Create and Push Tag**:
    ```bash
    git tag v1.1.0
    git push origin v1.1.0
    ```
4.  **Verify**:
    *   Monitor the "Actions" tab in GitHub.
    *   Once complete, the package will appear on [PyPI](https://pypi.org/project/pyegeria/) and a new Release will be visible on GitHub.

## Best Practices
- **PR Labels**: Use labels like `bug`, `enhancement`, and `documentation` on Pull Requests. The release notes generator uses these to categorize changes automatically.
- **Trusted Publishing**: This repo uses OIDC. Ensure the GitHub environment `release` is configured in PyPI settings to allow publishing from this specific workflow.