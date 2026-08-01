# Adding A Video

How to put a video on the Videos page at [/web/videos.html](../web/videos.html), and how that
differs from attaching one to a single question.

## Before Anything Else: Do We Have The Right To Show It?

The Videos page exists to show video we are permitted to show. That is the whole
premise, so this step is not a formality.

- **We made it, or the museum did.** Fine to show. Note that in `rights_note`.
- **A U.S. government work** (Navy, National Archives). Generally public domain,
  but confirm the specific item rather than assuming it from the agency.
- **Someone else's, with written permission.** Fine to show. Record who granted
  it and when, in `rights_note`.
- **Someone else's, without permission.** Do not add it. "It's on YouTube" and
  "it's embeddable" are not permission. YouTube leaving embedding enabled is the
  uploader's setting, not a licence for a museum exhibit.
- **Library of Congress / Veterans History Project oral histories.** These are
  *not* free to use. Veterans retain copyright and LoC states it "cannot give or
  deny permission" to republish. Link to the item page instead — see
  [Linking Instead Of Embedding](#linking-instead-of-embedding).

When in doubt, ask before adding. A takedown from an annoyed rights holder costs
far more than a wait.

## Adding The Video: Use The Editor

The normal way is the admin screen. Open [Admin](../web/edit.html) → **Videos**,
or go straight to `/web/edit_videos.html`. Fill in the form, press **Add video**,
and it appears on the public page immediately — no deploy, no restart.

Only **Video URL** is required. Paste the ordinary `watch?v=…` link; it is
rewritten to `youtube-nocookie.com` automatically so visitors don't pick up
YouTube's tracking cookie just by reading the page. Fill in **Rights note**
anyway: it is displayed publicly and it is how anyone later can tell permission
was obtained without digging through email.

The editor refuses a URL that isn't `http://` or `https://`, and a start time
that isn't a whole number of seconds. It shows every stored record, including
ones the public page would drop, so a broken entry can be seen and repaired
rather than silently vanishing.

**Where this data lives.** Videos are stored on the Render persistent disk
(`/data`), like the FAQ corpus and the glossary, so an edit made on the live site
survives the next redeploy. The consequence is the one that catches everyone:

> Editing the committed `corpora/videos.jsonl` **does not change production.**
> That file seeds `/data` once, on first boot, and is ignored from then on.

So use the editor for anything that should appear on the live site. The file
below is the local-development and first-boot-seed copy only.

## Editing The File Directly (local work and seeding)

### 1. Edit `corpora/videos.jsonl`

One JSON object per line, no blank lines, no comments. JSONL is strict: a single
malformed line stops the loader at that point and **silently truncates the rest
of the file**, so every video after the bad line disappears.

```json
{"id": "vid_001", "display_order": 1, "title": "Clay Decker: Escaping The Tang", "video_url": "https://www.youtube.com/watch?v=Ns3AJhNlEzs", "video_start": 166, "description": "Clay Decker, one of nine men who survived the loss of USS Tang, describes escaping the sunken submarine.", "video_credit": "Omni Media Services", "video_credit_url": "https://www.youtube.com/@omnimediaservices", "rights_note": "Embedded with the uploader's written permission, 4 August 2026."}
```

| Field | Required | What it does |
| --- | --- | --- |
| `video_url` | **Yes** | The video. A record without one is dropped rather than shown as a description under an empty frame. |
| `id` | No | Internal identifier. Also the tiebreaker when two records share a `display_order`. |
| `display_order` | No | Position on the page, low to high. Records without one sort last. |
| `title` | No | Heading above the description. |
| `description` | No | The text under the player. Line breaks are preserved. |
| `video_start` | No | Start the video at this many seconds in. Omit to start at the beginning. |
| `video_credit` | No | Rendered as "Courtesy of …". |
| `video_credit_url` | No | Makes the credit a link. |
| `rights_note` | No | **Why we may show this.** Displayed on the page. Fill it in — it is how anyone later can tell permission was obtained without digging through email. |

Only `video_url` is strictly required, but a video with no description is a poor
exhibit. Write the description for a visitor standing on the boat.

### 2. Check the JSON before you push

A typo here breaks the page quietly. From the repo root:

```bash
python3 -c "
import json
ok = True
for i, line in enumerate(open('corpora/videos.jsonl', encoding='utf-8-sig'), 1):
    line = line.strip()
    if not line:
        continue
    try:
        r = json.loads(line)
    except Exception as e:
        print(f'LINE {i}: {e}'); ok = False; continue
    if not r.get('video_url'):
        print(f'LINE {i}: no video_url — this record will not appear')
print('OK' if ok else 'FIX THE LINES ABOVE')
"
```

This reports the **file** line number to fix. Do not trust the line number in a
raw `json` traceback — it counts characters within the single line being parsed,
so it always says "line 1."

### 3. Look at it locally

```bash
CONTENT_ROOT=corpora_local python3 -m uvicorn api.main:app --port 8000
```

Then open <http://127.0.0.1:8000/web/videos.html>. Note that this reads
`corpora_local/videos.jsonl`, so copy your edit there to preview it, or drop
`CONTENT_ROOT` to read `corpora/` directly.

The page reads the file per request — edit, save, refresh. No restart needed.

### 4. Commit it

```bash
git add corpora/videos.jsonl
git commit -m "Add <video title> to the Videos page"
git push
```

Worth doing so the committed copy stays a sensible seed and baseline — but
remember it **will not change the live site** if `/data` has already been
seeded. Production content comes from the editor. Pushing also restarts the live
site for two to three minutes; give Dwight a heads-up, since a content save he
attempts during the restart can fail.

### 5. Verify what is actually live

```bash
curl -s https://submarinedocent.org/api/videos | python3 -m json.tool
```

This is the truth for the public page, whatever the committed file says. If your
video isn't there, add it through the editor.

## Linking Instead Of Embedding

When we may point at a video but not show it, attach a link to the relevant
question instead. This is the right move for Veterans History Project oral
histories and anything else whose rights we do not hold.

Links live on a FAQ record as `related_links`, and unlike the Videos page they
**cannot be deployed by pushing** — the FAQ corpus lives on the Render
persistent disk. Write them through the admin API:

```bash
curl -X PUT https://submarinedocent.org/admin/faq/faq_777 \
  -u "$ADMIN_USERNAME:$ADMIN_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{"related_links":[
        {"url":"https://www.loc.gov/item/afc2001001.111768/",
         "label":"Lawrence E. Noker, Fireman First Class — video interview",
         "citation":"Lawrence E. Noker (AFC 2001/001/111768), Veterans History Project Collection, American Folklife Center, Library of Congress."}
      ]}'
```

Two cautions:

- `{"status":"saved"}` does **not** mean the field was understood. An older build
  accepts the request and ignores fields it does not know. Always read back with
  `curl -s https://submarinedocent.org/api/faqs` and confirm the links appear.
- `GET /admin/faqs` returns only `chunk_id`, `title`, `text`, `category`, and
  `display_order`. It does **not** show `related_links` or the `video_*` fields,
  so their absence there is not evidence they are missing. It also means
  [bin/sync-local-from-prod](../bin/sync-local-from-prod) will not bring them
  down, and running it can silently strip them from your local copy.

## Attaching A Video To One Question

Separate from the Videos page, a single FAQ answer can carry its own video. It
renders under the answer as a button the visitor presses, rather than
autoplaying, so it cannot talk over the tour narration.

Use the same `video_url`, `video_start`, `video_caption`, `video_credit`, and
`video_credit_url` fields, set on the FAQ record rather than in `videos.jsonl`.
Like `related_links`, these live on the persistent disk and are not deployed by
pushing.

Choose the question the video actually answers. A clip of a Tang survivor
belongs on "Has anyone escaped from a sunken WWII submarine," not on a general
question about submarines.

## Things That Will Trip You Up

- **A malformed JSONL line truncates the file** from that point on, without an
  error to the visitor. Validate before pushing.
- **URLs must be `http://` or `https://`.** Anything else is rejected and the
  record is dropped. This is a deliberate guard, not a bug.
- **YouTube links are rewritten** to `youtube-nocookie.com` so a visitor reading
  the page does not get YouTube's tracking cookie. Paste the ordinary
  `watch?v=…` URL; the rewrite is automatic.
- **Editing a committed corpus file does nothing in production.** True for
  `videos.jsonl`, the FAQ corpus, and the glossary alike — all are served from
  `/data`. Use the admin screens for anything that should appear on the live
  site.
- **`corpora/` and `corpora_local/` drift apart.** `corpora_local/` mirrors live
  content; `corpora/` is the shipped seed. They are not expected to match.

## Related

- [MediaRightsReview.md](MediaRightsReview.md) — why `web/videos/` and
  `web/images/` are held back from public release, and the standing caution
  about media of unclear provenance.
