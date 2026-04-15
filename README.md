# SubmarineDocent

SubmarineDocent is a FastAPI-backed historical docent application with a static web frontend. In its current form, it powers three main experiences:

- a mobile-first USS Pampanito tour and question-answering app
- a public FAQ and history dashboard for WWII diesel-electric submarines
- curator/admin tools for managing FAQs, glossary entries, incidents, and visitor feedback

## Repository Scope

This repository contains both application code and project-specific content.

- Software source code is licensed under the terms in [LICENSE](LICENSE).
- Historical corpora, images, audio, video, trademarks, and other project-specific source materials may be subject to separate rights. Review [docs/OpenSourceReadinessChecklist.md](docs/OpenSourceReadinessChecklist.md) before redistributing this repository or using it as the basis for a public deployment.

## Stack

- Python 3.9+
- FastAPI + Uvicorn
- Static HTML, CSS, and JavaScript frontend
- JSONL corpora in `corpora/`
- Optional third-party services for transcription and email delivery

## Project Layout

- `api/` — FastAPI application
- `web/` — public and admin frontend pages
- `corpora/` — JSONL corpora and retrieval configuration
- `docs/` — project documentation and planning notes
- `render.yaml` — Render deployment definition

## Quick Start

1. Create and activate a virtual environment.
1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Create local configuration from the example file:

```bash
cp .env.example .env.local
```

1. Start the app over HTTP:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

1. Or start the local HTTPS flow used by the museum/local device deployment:

```bash
./start_https.sh
```

## Sample Content Mode

For redistribution-safe demos, the app can run against the bundled sample dataset instead of the full museum corpus.

```bash
SAMPLE_CONTENT_MODE=true uvicorn api.main:app --host 0.0.0.0 --port 8000
```

You can also point the app at a different content directory by setting `CONTENT_ROOT`.

If `CONTENT_ROOT` is unset and the full corpus bundle is missing, the app will automatically fall back to `sample_data/corpora/` when that sample bundle is present.

## Public Release Prep

The repository now includes a non-destructive public-release staging flow.

```bash
make public-release-stage
make public-release-check
```

`make public-release-stage` builds a stripped tree in `build/public-release/` with the known private corpora and internal planning files removed.

`make public-release-check` stages that tree, boots it with no production corpora present, verifies automatic fallback to `sample_data/corpora/`, checks public APIs, and confirms admin routes stay disabled by default when credentials are unset.

## Environment Variables

The project supports these groups of environment variables.

### Service credentials

- `GROQ_API_KEY` — enables server-side transcription
- `OPENAI_API_KEY` — reserved for future model-backed features
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` — enable email delivery

### Route protection

- `ADMIN_USERNAME`, `ADMIN_PASSWORD` — required to enable `/admin/*`, `/feedback/list`, and admin-facing pages
- `PREVIEW_USERNAME`, `PREVIEW_PASSWORD` — optional Basic Auth for preview/tour routes

If `ADMIN_USERNAME` or `ADMIN_PASSWORD` is not set, admin routes are disabled by default.

### Host and redirect config

- `LEGACY_DOMAIN_HOSTS` — comma-separated legacy hostnames to redirect
- `LEGACY_DOMAIN_TARGET` — redirect target for legacy domains
- `TOUR_HOST_PREFIXES` — comma-separated host prefixes that should land on the tour page
- `DEFAULT_ROOT_REDIRECT` — first-visit landing page
- `RETURNING_VISITOR_REDIRECT` — landing page when the `visited` cookie is present

### Content source

- `SAMPLE_CONTENT_MODE` — uses the bundled sample corpus in `sample_data/corpora/`
- `CONTENT_ROOT` — overrides the corpus directory entirely

The `/health` response reports whether sample mode is active and whether it was enabled by automatic fallback.

### Local HTTPS helper config

- `LOCAL_HTTPS_HOST`
- `LOCAL_HTTPS_PORT`
- `LOCAL_STATIC_PORT`
- `LOCAL_TOUR_PATH`
- `LOCAL_STATIC_TOUR_PATH`
- `SSL_KEYFILE`
- `SSL_CERTFILE`

See [.env.example](.env.example) for defaults.

## Admin Access

Admin pages and endpoints now use server-side Basic Auth.

Protected surfaces include:

- `/admin/*`
- `/feedback/list`
- `/feedback.html`
- `/review.html`
- `/faq_editor.html`
- `/edit.html`
- `/web/edit_*.html`

This is a deliberate hardening change so the repository can be prepared for open-source publication without exposing curator tools by default.

## Deployment Notes

The app is currently configured for Render via [render.yaml](render.yaml).

For local museum-style HTTPS startup, [start_https.sh](start_https.sh) and [serve_https.py](serve_https.py) now read host and port display values from environment variables rather than assuming one fixed local IP.

## Documentation

- Overview: [docs/Overview.md](docs/Overview.md)
- Open-source release checklist: [docs/OpenSourceReadinessChecklist.md](docs/OpenSourceReadinessChecklist.md)
- Media rights review: [docs/MediaRightsReview.md](docs/MediaRightsReview.md)
- Cost summary: [docs/ProjectCostsNonTechnical.md](docs/ProjectCostsNonTechnical.md)

## Contributing And Security

- Contribution process: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: [SECURITY.md](SECURITY.md)
- Community expectations: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
