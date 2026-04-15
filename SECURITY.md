# Security Policy

## Supported Development Line

Security fixes should target the current main branch and the currently deployed configuration.

## Reporting A Vulnerability

Do not open a public issue for a suspected security problem.

Preferred reporting path after publication:

1. Use the repository hosting platform's private security advisory feature, if available.
2. If a private advisory flow is not available, contact the maintainer through a private channel already used for project operations.

Please include:

- a description of the issue
- affected routes, pages, or files
- reproduction steps
- impact assessment
- any suggested mitigation, if known

## Sensitive Areas In This Project

Changes in these areas should be reviewed carefully:

- `/admin/*` routes
- `/feedback/list`
- admin-facing web pages in `web/`
- auth and redirect middleware in `api/main.py`
- startup scripts and environment-variable handling

## Current Security Expectations

- admin routes must remain protected server-side
- secrets must be supplied via environment variables, not committed files
- local certificates and feedback exports must stay out of version control
- preview-only gating must not rely on client-side hardcoded passwords
