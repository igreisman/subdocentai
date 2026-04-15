# Public Release Branch Plan

This document defines the practical branch-cut plan for publishing a stripped public version of this repository.

## Goal

Create a `public-release` branch that keeps:

- the application code
- the static frontend
- the sample dataset in `sample_data/corpora/`
- the setup, contribution, and security documentation

And removes or privatizes assets that are environment-specific, proprietary, operational, or not clearly redistributable.

## Keep In Public Branch

- `api/`
- `web/`
- `sample_data/`
- `requirements.txt`
- `render.yaml`
- `README.md`
- `LICENSE`
- `NOTICE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- public-facing docs that describe architecture, setup, and release constraints

## Remove Or Move Out Of Public Branch

### Production or proprietary content

- `corpora/`
- `corpora copy/`
- top-level `eternal_patrol.jsonl` if it remains a production-side export
- `web/videos/` pending provenance review
- `web/images/` pending provenance review
- any other non-sample images, audio, or video whose redistribution rights are unclear

### Internal or operational data

- `lost_submarines-3.sql`
- any local exports derived from third-party systems
- any feedback exports if they appear in tracked history

### Internal planning or private business materials

- `docs/ProjectCosts.md`
- `docs/ProjectCostsApprovalMemo.md`
- `docs/todo.md`
- any other approval, budgeting, or internal rollout docs not intended for public readers

### Review Before Keeping

- `add_faqs*.py`
- `fix_*.py`
- `debug_*.py`
- `score_debug.py`
- `spot_check*.py`
- `test_batch*.py`

Current review outcome:

- remove these from the public branch for now
- they are tied to internal content generation, local HTTPS regression checks, or batch corpus evaluation against private historical content
- if any of them later become useful public tooling, reintroduce them intentionally with cleaned inputs and documentation

## Branch Procedure

1. Branch from current main into `public-release`.
1. Run `make public-release-stage` to build a first-pass stripped tree in `build/public-release/`.
1. Remove the full production corpora and any duplicate content folders from the actual `public-release` branch, using the staged tree as the baseline.
1. Remove `web/videos/` and `web/images/` from the actual public branch unless and until the review in `docs/MediaRightsReview.md` has been resolved in favor of publication.
1. Keep `sample_data/corpora/` as the default public demo dataset.
1. Re-read `NOTICE` and verify it still matches what remains in the branch.
1. Re-run `make public-release-check` before publishing.
1. Review all remaining docs for references to private infrastructure, internal approvals, or private content provenance.
1. Publish only after the sample-mode path is the documented default for external users.

## First-Pass Pruning

`make public-release-stage` removes the known private paths below from a staged copy of the repo:

- `corpora/`
- `corpora copy/`
- `eternal_patrol.jsonl`
- `lost_submarines-3.sql`
- `docs/ProjectCosts.md`
- `docs/ProjectCostsApprovalMemo.md`
- `docs/todo.md`
- `AI_CONTEXT.md`

It intentionally does not auto-delete `web/videos/`, `web/images/`, or the internal helper scripts and batch tests. Those still need a rights and usefulness review before a real public branch is cut.

Current review outcome:

- `web/videos/` should be excluded from the public branch for now
- `web/images/` should be excluded from the public branch for now
- internal helper and batch evaluation scripts should also be excluded from the public branch for now
- see `docs/MediaRightsReview.md`

## Release Gate

Do not publish the `public-release` branch until these are true:

- the branch boots successfully with sample content only
- no production corpora remain in the branch
- no unresolved media directories such as `web/videos/` or `web/images/` remain in the branch
- no internal business or deployment-sensitive documents remain unintentionally
- licensing and notice text still match the files that are actually present

## Recommended Verification Commands

```bash
make public-release-check
```

Then verify:

- `GET /health`
- `GET /api/faqs`
- `GET /api/incidents`
- `GET /api/eternal-patrol`
- `/admin/faqs` returns `503` without admin credentials
- `/feedback/list` returns `503` without admin credentials

This should be treated as the minimum publishability check for the public branch.
