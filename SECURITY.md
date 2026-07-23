# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project (the OWASP AIMA Healthcare
app or its source content), please report it privately rather than opening a public
GitHub issue:

- Open a [GitHub security advisory](../../security/advisories/new) for this repository, or
- Contact the project maintainer listed on the repository's GitHub profile.

Please include steps to reproduce, the potential impact, and any relevant logs or
screenshots. We aim to acknowledge reports within 5 business days.

## Scope

This app is a stateless assessment tool: all answers, organization details, and
exports live only in the visitor's browser session (`st.session_state`) for the
duration of their visit. Nothing is written to a database or persisted server-side.
Reports of concern in this area (e.g. data retention, cross-session leakage) are
in scope and taken seriously given the healthcare context.

## Supported Versions

Only the `main` branch / the app currently deployed at the public URL in
[README.md](README.md) is supported with security fixes.
