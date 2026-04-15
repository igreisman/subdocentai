# Media Rights Review

Last updated: March 25, 2026

This review records the current publication risk for media under `web/videos/` and `web/images/`.

## Decision For Public Release

Until provenance and redistribution rights are confirmed, exclude both of these directories from the public `public-release` branch:

- `web/videos/`
- `web/images/`

This is the conservative default consistent with [NOTICE](../NOTICE) and the platform-only release strategy.

## Findings

### `web/videos/`

- Approximate total size: `3986999461` bytes, about `3.71 GiB`
- File types present:
  - `127` `.png`
  - `113` `.pxd`
  - `13` `.mp4`
  - `11` `.jpg`
  - `7` `.numbers`
  - `4` `.xlsx`
  - `2` `.tif`
  - `2` `.jpeg`
  - `1` `.txt`
  - `5` extensionless files
- The directory contains scene-build source material, not just web-ready assets.
- Representative risk indicators:
  - editable project files such as `.pxd`
  - production planning files such as `.numbers` and `.xlsx`
  - raw or export media such as `.mp4`, `.tif`, `.png`, `.jpg`
  - narration/transcript text such as `after_torpedo_room_eng.txt`
- Scene directories such as `after_torpedo_room`, `control room`, `radio room`, and `forward_engine` look like museum-specific production packages rather than generic application assets.

### `web/images/`

- Approximate total size: `96319684` bytes, about `91.86 MiB`
- File types present:
  - `424` `.jpg`
  - `15` `.jpeg`
  - `15` `.png`
  - `10` `.webp`
  - `5` `.xcf`
  - `2` `.gif`
  - `1` `.svg`
  - additional malformed or extensionless entries also exist
- The directory includes large volumes of historical boat and captain imagery with filenames tied to specific vessels, officers, and museum artifacts.
- Representative risk indicators:
  - historical photo assets such as `USS Wahoo (SS-238).jpg`
  - person-specific portraits such as `LCDR Hugh Rimmer.jpg`
  - editable source files such as `USS_Pampanito 2560x1440.xcf`
  - mixed generated/exported derivatives such as `boat-*.jpg`, `captain-*.jpg`, and `extra-*.jpg`

## Publication Guidance

For a public software branch, keep:

- code
- docs
- sample corpora in `sample_data/corpora/`
- minimal clearly owned UI assets only after provenance is verified

Do not keep `web/videos/` or `web/images/` in the public branch until each asset class has an explicit provenance decision.

## Follow-Up Review Needed

Before any later reintroduction of media into a public branch, verify at least these questions:

- Was the asset created by the project team, the museum, or a third party?
- Is there written permission to redistribute it in a public code repository?
- Is the file a source/editable working file that should never ship publicly?
- Is the asset tied to museum branding, narration, or other non-code rights that should remain private?
