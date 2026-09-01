<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the ODPi Egeria project. -->

# Security Policy

pyegeria is part of the [ODPi Egeria](https://github.com/odpi/egeria) project family and follows Egeria's own
[code quality and security practices](https://github.com/odpi/egeria/blob/main/SECURITY.md), including:

- [GitHub Dependabot](https://dependabot.com/) to automatically update dependencies (`.github/dependabot.yml`).
- [GitHub CodeQL](https://github.com/features/security) to automatically scan for security vulnerabilities
  (`.github/workflows/codeql.yml`).
- PyPI [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC) for releases — no long-lived API
  token is stored in this repository.
- GitHub Actions steps pinned to a specific commit SHA rather than a mutable tag, so a workflow can't be
  silently altered by a tag being moved upstream.

## Reporting a Vulnerability

If you believe you've found a security vulnerability in pyegeria, please report it privately rather than
opening a public issue:

- Use GitHub's [private vulnerability reporting](https://github.com/odpi/egeria-python/security/advisories/new)
  for this repository, or
- Email [egeria-security@lists.lfaidata.foundation](mailto:egeria-security@lists.lfaidata.foundation).

For general questions about this policy, reach out to the
[Egeria development team](mailto:egeria-technical-discuss@lists.lfaidata.foundation).

----
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
Copyright Contributors to the ODPi Egeria project.
