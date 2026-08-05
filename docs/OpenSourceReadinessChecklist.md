# Open Source Readiness Checklist

Last updated: August 5, 2026

This checklist tracks what must be completed before this repository should be published as open source.

## Current Standing Risk

The repository is already public, and Content Rights Review below is still open on all four items. The gate at the bottom of this document says not to publish until that section is complete, and it was crossed. `docs/MediaRightsReview.md` separately recommends excluding `web/videos/` and `web/images/` from any public branch until provenance is confirmed; both are on public `main` today, at roughly 807 MB and 82 MB.

The staging flow exists and works (`make public-release-stage`, `make public-release-check`). What has not happened is cutting the stripped `public-release` branch and deciding what `main` itself should hold.

## Completed In This Pass

- [x] Added server-side protection for sensitive routes
- [x] Disabled admin access by default unless `ADMIN_USERNAME` and `ADMIN_PASSWORD` are configured
- [x] Protected `GET /feedback/list` with the same server-side admin gate
- [x] Removed the hardcoded browser PIN gate from the tour page
- [x] Removed the hardcoded browser PIN gate from the feedback page
- [x] Added optional server-side preview auth using `PREVIEW_USERNAME` and `PREVIEW_PASSWORD`

## Still Required Before Public Release

### 1. Licensing

- [x] Add a `LICENSE` file
- [x] Decide whether the code license also applies to the bundled content and media — it does not; `LICENSE` scopes MIT to source code only
- [x] If content and code have different rights, document that explicitly — `LICENSE` states the split and `NOTICE` lists the asset classes needing provenance review

### 2. Repository Entry Docs

- [x] Add a top-level `README.md`
- [x] Add `CONTRIBUTING.md`
- [x] Add `SECURITY.md`
- [x] Add `CODE_OF_CONDUCT.md`

### 3. Secrets And Configuration Hygiene

- [x] Add a `.env.example` that lists all required and optional environment variables
- [x] Document `ADMIN_USERNAME` and `ADMIN_PASSWORD`
- [x] Document `PREVIEW_USERNAME` and `PREVIEW_PASSWORD`
- [x] Document `GROQ_API_KEY`, `SMTP_USER`, and `SMTP_PASS`
- [x] Move any remaining host-specific settings into environment variables or config files — `start_https.sh` reads host and port from the environment; no private-network IP remains hardcoded in the startup scripts or `api/`

### 4. Content Rights Review

- [ ] Confirm redistribution rights for all files in `corpora/`
- [ ] Confirm redistribution rights for images, videos, and extracted media in `web/`
- [ ] Confirm whether DieselSubs-derived material can be published in this repo
- [ ] Confirm whether Pampanito-specific narration and museum content can be published under an open-source repo model

If any of the above rights are unclear, publish the code separately from the content.

### 5. Public/Private Boundary

- [ ] Decide whether this repo is the full museum deployment or the reusable software platform
- [ ] If needed, split proprietary content into a private companion repo or private content bundle
- [x] Replace real corpora with a small sample dataset if the production content cannot be redistributed
- [x] Add a first-pass public-release staging flow that removes known private files from a staged tree

Current status:

- A redistribution-safe sample dataset is now available in `sample_data/corpora/`
- The app can run in sample mode via `SAMPLE_CONTENT_MODE=true`
- `make public-release-stage` now builds a stripped tree in `build/public-release/`
- A media review now recommends excluding `web/videos/` and `web/images/` from the public branch until provenance is verified
- Internal corpus migration, debug, and batch evaluation scripts are now also treated as non-public by default
- The remaining step is to cut an actual `public-release` branch and finish the media and helper-script review

### 6. Branding And Deployment Defaults

- [ ] Move domain-specific redirect settings into configuration
- [ ] Remove or generalize museum-specific local IP assumptions in startup scripts
- [ ] Review all museum- or deployment-specific wording for whether it belongs in the public repo

### 7. Test And Automation Baseline

- [ ] Add CI for startup and test execution
- [x] Add a smoke test for protected routes
- [x] Add a smoke test for public route availability
- [ ] Document how to run the existing test files

Current status:

- CI now boots the app in sample mode and verifies `/health`, `/api/faqs`, `/api/incidents`, and `/api/eternal-patrol`
- CI now also verifies `/admin/faqs` and `/feedback/list` stay disabled by default when admin credentials are unset

## Recommended Release Strategy

### Option A: Open-Source The Whole Repo

Use this only if:

- content rights are confirmed
- museum stakeholders approve public distribution
- branding and deployment assumptions are acceptable as public defaults

### Option B: Open-Source The Platform Only

Preferred if content rights are uncertain.

Steps:

- publish the FastAPI app, frontend, and sample data
- keep real corpora, media, and museum-specific deployment files private
- document how a private content pack plugs into the public codebase

## Release Gate

Do not publish the repository publicly until all items in these sections are complete:

- Licensing
- Repository Entry Docs
- Secrets And Configuration Hygiene
- Content Rights Review

The auth hardening completed in this pass removes the most immediate code-exposure issue, but it does not resolve licensing or content-ownership risk.
