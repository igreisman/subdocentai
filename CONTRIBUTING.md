# Contributing

## Scope

This repository mixes application code with historical content and deployment-specific material. Keep changes narrowly scoped and call out whether your change affects:

- application code
- historical corpora or editorial content
- deployment configuration
- admin workflow pages

## Before You Start

1. Read [README.md](README.md)
2. Review [docs/OpenSourceReadinessChecklist.md](docs/OpenSourceReadinessChecklist.md)
3. Use `.env.local` for local configuration
4. Do not commit secrets, local certs, or feedback exports

## Development Setup

```bash
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

For local HTTPS testing, use:

```bash
./start_https.sh
```

## Contribution Guidelines

- Prefer minimal, focused changes
- Preserve existing public behavior unless the change intentionally updates it
- Add or update documentation when configuration or workflow changes
- Do not introduce hardcoded secrets, local IPs, or environment-specific assumptions
- Treat admin and feedback surfaces as sensitive features and keep server-side protection in place

## Content Changes

If you change corpora, text, or media references:

- identify the source of the material
- confirm that redistribution and modification are allowed
- note any provenance or licensing constraints in the pull request

## Testing

At minimum, contributors should:

- verify the app starts locally
- verify public pages still load
- verify protected admin routes remain protected
- run any targeted test scripts relevant to the changed area

## Pull Requests

Include:

- a short summary of what changed
- why the change was needed
- any environment variables or deployment settings affected
- any follow-up work that remains
