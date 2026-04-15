# SubmarineDocent

Current site overview and technical summary.

## What This Site Is

SubmarineDocent is no longer just a single Pampanito tour prototype. It is now a small FastAPI-backed historical site with several connected experiences:

- A public USS Pampanito audio tour and question-answering app.
- A public diesel-electric submarine FAQ dashboard.
- Special-history sections embedded in the FAQ site for Medal of Honor recipients, Eternal Patrol / lost submarines, incidents, and operations content.
- Curator/admin tools for FAQ review, FAQ editing, and feedback review.

The application is served from one Python backend in [api/main.py](/Users/irving/Documents/submarinedocent/api/main.py) and static frontend pages in [web](/Users/irving/Documents/submarinedocent/web).

## Current Public Pages

### 1. Pampanito tour app

Primary visitor experience: [web/pampanito.html](/Users/irving/Documents/submarinedocent/web/pampanito.html)

- Mobile-first tour interface for USS Pampanito.
- Supports narrated compartment audio plus visitor Q&A.
- Uses `/ask`, `/tts`, `/transcribe`, `/health`, and `/contact`.
- Intended to work as the on-ship or museum-floor docent experience.

### 2. FAQ dashboard

Primary historical reference hub: [web/faqs.html](/Users/irving/Documents/submarinedocent/web/faqs.html)

- Dashboard of WWII diesel-electric submarine FAQ categories.
- Public FAQ browser backed by `/api/faqs`.
- Includes four special cards and dedicated in-page views for:
  - U.S. Submarine Medal of Honor recipients.
  - Lost submarines / Eternal Patrol.
  - Submarine incidents database.
  - Operations guide.

This page is currently the most developed general-purpose historical interface in the site.

### 3. Eternal Patrol page

Standalone lost-submarines page: [web/eternal-patrol.html](/Users/irving/Documents/submarinedocent/web/eternal-patrol.html)

- Fetches data from `/api/eternal-patrol` with JSONL fallback.
- Shows aggregate statistics, searchable/filterable list, and modal details.
- Modal now includes Construction before Loss Narrative.

### 4. Feedback and curator tools

- Auth-protected feedback viewer: [web/feedback.html](/Users/irving/Documents/submarinedocent/web/feedback.html)
- FAQ review tool: [web/review.html](/Users/irving/Documents/submarinedocent/web/review.html)
- FAQ editor and SQL import tool: [web/faq_editor.html](/Users/irving/Documents/submarinedocent/web/faq_editor.html)

### 5. Site entry behavior

- The backend now redirects `/` to [web/faqs.html](/Users/irving/Documents/submarinedocent/web/faqs.html) for returning visitors and [web/welcome.html](/Users/irving/Documents/submarinedocent/web/welcome.html) by default.
- Tour-host routing is now configuration-driven through `TOUR_HOST_PREFIXES` rather than hardcoded to one hostname pattern.
- Legacy `/index.html` requests are redirected to the FAQ dashboard.

## Current Backend Surface

Main application file: [api/main.py](/Users/irving/Documents/submarinedocent/api/main.py)

### Public routes

- `/` -> redirects according to host configuration and first-visit/returning-visitor settings.
- `/index.html`, `/web/index.html` -> redirect to the FAQ dashboard.
- `/pampanito.html` -> redirects to the Pampanito app.
- `/faqs`, `/faqs.html`, `/faq` -> redirect to the FAQ dashboard.
- `/feedback.html`, `/review.html`, `/faq_editor.html` -> redirect to their matching web pages and require admin auth.
- `/web/*` -> static file hosting for the frontend.

### Public API routes

- `GET /health`
  - Returns service status, transcription availability, and corpus counts for tour, FAQ, and shorts corpora.
- `POST /ask`
  - Main question-answering endpoint used by the Pampanito app.
- `POST /tts`
  - Text-to-speech endpoint.
- `POST /transcribe`
  - Audio transcription endpoint.
- `POST /contact`
  - Visitor contact / unanswered-question handoff.
- `GET /api/faqs`
  - Returns published `faq_` entries grouped by category for the public FAQ page.
- `GET /api/eternal-patrol`
  - Returns the Eternal Patrol / lost submarines dataset.
- `GET /api/incidents`
  - Returns the submarine incidents dataset.
- `POST /feedback`
  - Accepts simple user feedback submissions.
- `GET /feedback/list`
  - Returns stored feedback entries and now requires admin auth.

### Admin / curator API routes

- `GET /admin/generated-faqs`
  - Returns generated FAQ candidates (`der_`, `pam_`, `fix_`).
- `GET /admin/faqs`
  - Returns full editable FAQ records.
- `POST /admin/faq`
  - Creates a new published FAQ.
- `PUT /admin/faq/{chunk_id}`
  - Updates an FAQ.
- `POST /admin/faq/{chunk_id}/accept`
  - Promotes a generated FAQ entry into a published `faq_` entry.
- `DELETE /admin/faq/{chunk_id}`
  - Removes generated FAQ entries.
- `POST /admin/import-sql`
  - Imports FAQ content from a phpMyAdmin SQL export.

## Data Sources in the Repo

Primary corpora live in [corpora](/Users/irving/Documents/submarinedocent/corpora). A redistribution-safe sample dataset also exists under [sample_data/corpora](/Users/irving/Documents/submarinedocent/sample_data/corpora) for open-source demos.

Current line counts:

| Corpus | File | Count | Purpose |
| --- | --- | ---: | --- |
| Pampanito tour corpus | [corpora/pampanito_tour_corpus.jsonl](/Users/irving/Documents/submarinedocent/corpora/pampanito_tour_corpus.jsonl) | 213 | Tour narration / compartment knowledge |
| Diesel submarine FAQ corpus | [corpora/dieselsubs_faq_corpus.jsonl](/Users/irving/Documents/submarinedocent/corpora/dieselsubs_faq_corpus.jsonl) | 455 | Master FAQ corpus including published and generated entries |
| Published FAQ entries | [corpora/dieselsubs_faq_corpus.jsonl](/Users/irving/Documents/submarinedocent/corpora/dieselsubs_faq_corpus.jsonl) | 229 | Public `faq_` entries exposed through `/api/faqs` |
| DieselSubs shorts | [corpora/dieselsubs_shorts_corpus.jsonl](/Users/irving/Documents/submarinedocent/corpora/dieselsubs_shorts_corpus.jsonl) | 31 | Supplementary historical snippets |
| Eternal Patrol | [corpora/eternal_patrol.jsonl](/Users/irving/Documents/submarinedocent/corpora/eternal_patrol.jsonl) | 65 | Lost submarines data |
| Incidents | [corpora/incidents.jsonl](/Users/irving/Documents/submarinedocent/corpora/incidents.jsonl) | 16 | Incidents database records |

Other notable data/config files:

- [corpora/retrieval_config.yaml](/Users/irving/Documents/submarinedocent/corpora/retrieval_config.yaml)
- [corpora/system_prompt_ai_docent.md](/Users/irving/Documents/submarinedocent/corpora/system_prompt_ai_docent.md)
- [feedback.jsonl](/Users/irving/Documents/submarinedocent/feedback.jsonl)
- [corpora/api_contract.json](/Users/irving/Documents/submarinedocent/corpora/api_contract.json)

## How the Site Behaves Today

### Pampanito experience

The Pampanito app remains the AI-docent portion of the project:

- compartment-aware visitor Q&A
- text-to-speech answers
- optional server-side transcription
- visitor contact escalation when no good answer is available

### FAQ and history experience

The FAQ site has grown into a broader historical reference portal:

- category browsing across published diesel-electric submarine FAQs
- embedded special sections for awardees, losses, incidents, and operations
- dashboard-style navigation rather than a single search page

### Curator workflow

Curators can now:

- review generated FAQ candidates
- edit or create FAQ entries directly
- import FAQ material from SQL exports
- review accumulated visitor feedback

## Deployment and Hosting Model

Repository memory and config indicate the current deployment model is:

- FastAPI backend with static frontend assets
- Render deployment via [render.yaml](/Users/irving/Documents/submarinedocent/render.yaml)
- workspace rooted at `/Users/irving/Documents/submarinedocent`

The repo still contains local HTTPS startup helpers used during local/dev or on-prem usage:

- [serve_https.py](/Users/irving/Documents/submarinedocent/serve_https.py)
- [start_https.sh](/Users/irving/Documents/submarinedocent/start_https.sh)

## Current State Summary

As of March 2026, the site is best understood as a multi-surface historical web application with one backend and several distinct user experiences:

- The Pampanito tour app is functional and still central.
- The FAQ site is the main public historical dashboard.
- Eternal Patrol and Incidents are now real data-backed features, not placeholders.
- Admin tooling for FAQ curation is present and working.
- The FAQ dashboard is now the default entry point for the general site.

## Recommended Next Documentation Updates

- Add a dedicated architecture doc for the FAQ dashboard and history datasets.
- Add a curator workflow doc covering review, edit, import, and feedback moderation.
- Add a route map doc separating public, admin, and data endpoints.
