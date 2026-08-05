# SubmarineDocent

SubmarineDocent is a FastAPI-backed historical docent application with a static web frontend. In its current form, it powers four main experiences:

- a mobile-first USS Pampanito audio and video tour, where a visitor can ask a question about the compartment they are standing in
- a standalone "Ask the Docent" page for asking a question without taking the tour, by voice or by typing
- a public FAQ and history dashboard for WWII diesel-electric submarines, including war patrols, lost boats, Medal of Honor recipients, incidents, a glossary, museums, and video
- curator/admin tools for managing FAQs, glossary entries, incidents, videos, and visitor feedback

Questions are answered by local retrieval over JSONL corpora — BM25 with IDF, weighted so museum-authored material outranks reference sources — not by a language model. Voice input uses the browser's own speech recognition where it works and falls back to server-side Whisper transcription where it does not.

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

- `api/` — FastAPI application; `api/main.py` holds the routes, retrieval, and auth middleware
- `web/` — public and admin frontend pages, each a self-contained HTML file
- `corpora/` — JSONL corpora and retrieval configuration
- `sample_data/corpora/` — redistribution-safe sample dataset used by sample mode
- `docs/` — project documentation and planning notes
- `scripts/` — public-release staging and verification
- `bin/` — one-off import and sync utilities, not part of the running app
- `_test/` — retrieval evaluation and corpus-migration scripts (see Tests below)
- `.github/workflows/` — CI

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

## Content Rights

The goal is to host tours and video from several submarine museums. That material is licensed to this project by the institution holding it, not owned outright: permission can be given for one use, limited in time, or withdrawn on a phone call, and it differs per asset — one family may object to a relative's oral history while the others stand.

With one museum that is a conversation you keep in your head. Across twenty it has to be data, so every third-party asset carries:

| field | meaning |
| --- | --- |
| `museum_id` | joins `corpora/museums.jsonl` |
| `rights_status` | `granted`, `pending`, or `withheld` |
| `rights_note` | the basis in words — who agreed, when, on what terms |
| `rights_expires` | ISO date after which permission lapses (optional) |

These live on video records, on the `video_*` fields of a Q&A record, and on each entry in `related_links` individually.

One gate, `_rights_cleared()`, decides whether an asset may be served, applied where media becomes something a visitor can play. Anything not cleared is simply absent — the surrounding answer renders unchanged, because answer text is written to stand on its own. Admin endpoints deliberately read raw records instead, so a curator can still see and fix an asset the public pages are withholding.

`GET /admin/rights` lists every third-party asset with its owner, status, and reason, including ones being withheld and therefore invisible everywhere else. It answers the question a curator actually has: what are we publishing that we have not cleared, and whose is it.

### `RIGHTS_STRICT`

Records predating these fields carry no status, so by default an unrecorded asset is still served and shipping this changes nothing. Once every asset has been reviewed, set `RIGHTS_STRICT=true`: unrecorded then means not cleared, and the deployment fails closed. Check `GET /admin/rights` before turning it on — anything still `unrecorded` disappears from the public site the moment you do.

## Unpublished Pages

Some pages are deployed but deliberately not distributed with the source, because the content rights are still being settled. They are not in the repository and are ignored by git.

Currently: `web/pampanito.html`, the USS Pampanito tour, pending permission from the Maritime Association.

The server looks for such a page in two places, in order:

1. `/data/web/<name>` — the Render persistent disk, which survives redeploys
2. `web/<name>` — the ordinary checkout, for local development by anyone who holds the file

If neither exists the route returns a `404` explaining what is missing. The rest of the site is unaffected.

To deploy or update one, upload it to the disk from the Render Shell — a redeploy rebuilds the container from git, so a copy placed anywhere else is lost:

```bash
mkdir -p /data/web
# paste or transfer the file to /data/web/pampanito.html
```

Because the disk copy takes precedence, uploading a new build replaces what visitors see without a deploy. Remove the file from `/data/web/` to take the page down again.

## Tests And CI

There is no unit test suite. Two kinds of checking exist instead.

**CI** ([.github/workflows/sample-content-smoke.yml](.github/workflows/sample-content-smoke.yml)) runs on every push and pull request. It boots the app in sample mode and asserts `/health`, `/api/faqs`, `/api/incidents`, and `/api/eternal-patrol` respond, and that `/admin/faqs` and `/feedback/list` return `503` while credentials are unset. It does not run anything in `_test/`.

**Retrieval evaluation** lives in `_test/`. These are scripts, not tests: they POST questions to a *running* server at `https://localhost:8443` and report whether the expected corpus entry came back. They need the full corpora, so they are meaningful only against a real local instance, not in sample mode or CI.

```bash
./start_https.sh                      # in one shell
.venv/bin/python _test/spot_check.py  # in another
```

`spot_check.py` prints a per-question PASS/FAIL and a total; `test_batch*.py` and their `*_eval.py` counterparts run larger question sets. Treat the totals as a regression signal when changing retrieval — the constants under Retrieval tuning below were set against them.

## Environment Variables

The project supports these groups of environment variables.

### Service credentials

- `GROQ_API_KEY` — enables server-side Whisper transcription at `/transcribe`. Without it, `/health` reports `transcribe_available: false` and voice input falls back to the browser's own speech recognition or to typing.
- `OPENAI_API_KEY` — reserved for future model-backed features; nothing reads it today
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS` — enable email delivery
- `HISTORIAN_EMAIL` — where visitor questions from the "no answer found" flow are sent. **Set this.** The compiled-in default is a personal address.

### Route protection

- `ADMIN_USERNAME`, `ADMIN_PASSWORD` — required to enable `/admin/*`, `/feedback/list`, and admin-facing pages. These also open the museum-admin paths below.
- `MUSEUM_ADMIN_USERNAME`, `MUSEUM_ADMIN_PASSWORD` — a second, narrower credential pair that opens only `/admin/museum_pages*` and `/web/edit_museum_pages.html`, for a curator who should not hold the full admin password
- `PREVIEW_USERNAME`, `PREVIEW_PASSWORD` — optional Basic Auth for preview/tour routes

If neither pair is set, the routes each protects return `503` rather than a login prompt: access is disabled by default, not merely locked. Credentials are compared with `secrets.compare_digest`.

### Answer behaviour

- `USE_LLM` — when true, answers are synthesized rather than extracted. Off by default; the deployed configuration answers extractively.
- `RIGHTS_STRICT` — when true, an asset with no recorded rights is treated as not cleared and is not served. Off by default so existing content is unaffected. See Content Rights.

### Retrieval tuning

Scoring constants, overridable without a code change. Defaults are in parentheses and were chosen against the evaluation scripts in `_test/`; changing them shifts which source answers a question.

- `BM25_B` (0.3) — length normalisation. Low on purpose: chunk length here reflects the kind of content, not verbosity.
- `EXACT_TITLE_BOOST` (20.0) — multiplier when a query matches an FAQ title outright
- `OPERATIONS_GUIDE_WEIGHT` (0.9) — weight of the operations guide, below the FAQ corpus
- `FLEETSUB_MANUAL_WEIGHT` (0.5) — weight of the Fleet Type Submarine manuals, below every museum-authored source

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

Read by [start_https.sh](start_https.sh) only.

- `LOCAL_HTTPS_HOST`, `LOCAL_HTTPS_PORT` — host and port shown in the startup banner, and the port uvicorn binds
- `LOCAL_TOUR_PATH` — tour path shown in the banner
- `LOCAL_STATIC_PORT` — legacy separate static server; the script only kills anything still listening there
- `SSL_KEYFILE`, `SSL_CERTFILE` — TLS material, defaulting to `certs/key.pem` and `certs/cert.pem`

`LOCAL_STATIC_TOUR_PATH` appears in `.env.example` but is no longer read by anything; it belonged to a helper script that has been removed.

See [.env.example](.env.example) for defaults.

## Admin Access

Admin pages and endpoints use server-side Basic Auth, applied in middleware rather than per-route, so a new `/admin/` route or `web/edit_*.html` page is covered the moment it exists.

Requires `ADMIN_USERNAME` and `ADMIN_PASSWORD`:

- `/admin/*`
- `/feedback/list`
- `/feedback.html`
- `/review.html`
- `/faq_editor.html`
- `/edit.html`
- `/web/edit_*.html`

Requires either the admin pair above or `MUSEUM_ADMIN_USERNAME` and `MUSEUM_ADMIN_PASSWORD`:

- `/admin/museum_pages*`
- `/web/edit_museum_pages.html`

With no credentials configured these return `503`, not `401` — the surface is off, not merely locked, so an unconfigured deployment cannot be brute-forced. CI asserts this on every push.

This is a deliberate hardening change so the repository can be prepared for open-source publication without exposing curator tools by default.

## Deployment Notes

The app is currently deployed on Render, configured in the Render dashboard rather than by a blueprint in this repository. The `render.yaml` blueprint was removed in July 2026 because it recreated a duplicate service on sync; service settings, environment variables, and the persistent disk are managed in the dashboard.

For local museum-style HTTPS startup, [start_https.sh](start_https.sh) reads host and port display values from environment variables rather than assuming one fixed local IP. It expects a TLS key and certificate at `certs/key.pem` and `certs/cert.pem`; `certs/` is not tracked, so generate your own for local use.

## Documentation

- Overview: [docs/overview.md](docs/overview.md)
- Open-source release checklist: [docs/OpenSourceReadinessChecklist.md](docs/OpenSourceReadinessChecklist.md)
- Media rights review: [docs/MediaRightsReview.md](docs/MediaRightsReview.md)
- Cost summary: [docs/ProjectCostsNonTechnical.md](docs/ProjectCostsNonTechnical.md)

## Contributing And Security

- Contribution process: [CONTRIBUTING.md](CONTRIBUTING.md)
- Security reporting: [SECURITY.md](SECURITY.md)
- Community expectations: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
