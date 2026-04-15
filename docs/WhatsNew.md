# What's New — SubmarineDocent

Changes are listed newest-first. Dates are commit dates.

---

## 2026-03-25 — Open Source Hardening And Config Cleanup

- Replaced the hardcoded client-side `1941` PIN gates with server-side Basic Auth for admin and feedback routes.
- Added optional preview auth for the tour page via `PREVIEW_USERNAME` and `PREVIEW_PASSWORD`.
- Added `.env.example`, top-level repository docs, and an MIT-style software license with explicit content-rights caveat.
- Moved host-based routing and local HTTPS display settings into environment variables.
- Added a bundled sample-content mode for redistribution-safe demos.

---

## 2026-03-17 — Visitor Share Links and Editor Hub

The public-facing pages now include direct `Copy Link` actions, and the site has a new central admin landing page for editing workflows.

- **Visitor copy links added across public pages** — `Copy Link` buttons now appear on the FAQ dashboard/views, Eternal Patrol, Pampanito, and Feedback pages.
- **Stateful FAQ view sharing** — copied FAQ links now reopen the correct in-page public view, including category/search state, Medal of Honor, Lost Submarines, Incidents, and Operations.
- **Lost-submarine sharing preserved** — the Lost Submarines modal keeps its boat-specific share link support, while page-level share buttons were added for the surrounding views.
- **Editor Hub added** — new `/edit.html` convenience route redirects to `/web/edit.html`, a central launcher for FAQ, category, lost-boat, glossary, incidents, operations, and memorial workflows.
- **Stable edit landing pages added** — dedicated hub destinations were created for categories, lost boats, glossary, incidents, operations, and memorial content, even where a full CRUD editor does not yet exist.

---

## 2026-03-17 — FAQ Dashboard and Editor Refinements

Several FAQ-site and editor usability improvements shipped together during the March 17 updates.

- **Category navigation simplified** — the public FAQ page now uses a `Categories` dropdown instead of category buttons/tabs.
- **Category display cleaned up** — redundant single-category headings were removed and category order is respected consistently.
- **FAQ editor layout improved** — the answer editor toolbar now stays fixed while the answer body scrolls.
- **Internal history linking expanded** — FAQ answers can now link directly into Lost Submarines content using `?lost_sub=...` URLs.
- **Lost Submarines modal upgraded** — direct-link opening and a modal-level `Copy Link` control were added for specific boats.
- **Public page copy and layout polish** — small copy and UI refinements were applied to both the FAQ page and FAQ editor.

---

## 2026-03-16 — FAQ Categories and HTML Rendering

The FAQ system moved further away from hardcoded frontend state and toward data-backed content configuration.

- **FAQ HTML normalization shipped** — imported/stored FAQ answer HTML is now normalized so rich-text content renders correctly in both the editor and public site.
- **FAQ categories moved into JSONL** — category definitions are now stored in `corpora/dieselsubs_faq_categories.jsonl` instead of existing only as frontend constants.
- **`/api/faq-categories` added** — the backend now exposes category records, including their configured sort order.
- **FAQ editor category list is API-backed** — the editor fetches categories from the backend and can persist newly introduced category names into the categories corpus.
- **Public FAQ ordering improved** — `/api/faqs` and the public FAQ page now respect category sort order from the categories dataset.
- **FAQ item ordering prepared for `display_order`** — the API and public FAQ renderer now preserve and sort by `display_order` when that field is present on FAQ entries.

## 2026-03-10 — FAQ Corpus: pam_001–pam_226 (226 entries)

The custom Pampanito FAQ corpus grew from 7 seed entries to 226 in a series of batches, each tested with a regression suite before committing.

| Batch | Range | Count | Topics added |
| ----- | ----- | ----- | ------------ |
| Seed | pam_001–007 | 7 | Maneuvering room, bunks in torpedo rooms, engines, food storage, smarts, torpedo reloads, running submerged |
| 1–2 | pam_008–034 | 27 | Navigation, sonar, radio, Pampanito history, crew life basics, weapons, attack procedure, visiting |
| 3 | pam_035–066 | 32 | Crew size, recreation, toilets, surfacing, periscopes, conning tower, depth control, losses, torpedoes, captain, Silent Service, crew demographics, resupply, smell, mail, return to port, wolf pack, POW rescue, KIA, Japanese subs, US vs U-boats |
| 4 | pam_067–087 | 21 | Torpedo count, temperature, noise, patrol length, enemy sighting, sub-vs-sub combat, bottoming, largest sub, war patrol, special forces, laundry, shore leave, ports, Mark 14, crew tracking, battery room, crew after war, medals, fuel, diving alarm |
| 5 | pam_088–112 | 25 | Food, submarine tender, SS designation, POW identification, doctors, submarine school, SJ radar, war strategy, patrol assignments, damage, end-of-war, commissioning/decommissioning, museum preservation, longest submerged |
| 6 | pam_113–132 | 20 | Lifeguard mission, mine laying, depth charge sensation, hot bunking, deck gun operation, Pampanito name, fire fighting, snorkel, Battle of Midway, radio direction finding, claustrophobia, galley, fresh water, close calls, convoy attack, seasickness, warship sinkings, aircraft threat, wolfpack tactics, spies/special forces |
| 7–10 | pam_133–197 | 65 | Battle stations, pharmacist's mate, ballast tanks, enemy minefields, fleet boats, battery recharging, Gato vs Balao, captain's duties, destroyer evasion, torpedo sounds, commissioning day, Japanese sub fate, crew death, patrol orders, control room, forward torpedo room, garbage disposal, enemy survivors, flooding/fire, periscope feather, boredom, TDC operator, grounding, Japanese convoys, battle stars, flying bridge, Pampanito dive depth, magnetic exploder, top commander, celebration, return to port, Silent Service origin, construction changes, snorkel, periscope depth, OOD duties, conning tower, crew training, sound-powered phones, night identification, after torpedo room, Navy selection, crew of sunken sub, night surface attacks, lookouts, Pacific refueling, angle on bow, Pearl Harbor comms, forward engine room, navigation to patrol area, surfacing decision |
| 11 | pam_198–210 | 13 | Escape trunk, sonar tracking, chief of the boat, torpedo spreads, collision avoidance, periscope attack procedure, after engine room, diving planes, WWII radar use, tropical heat, commander qualities, depth charge interior, destroyer evasion tactics |
| 12 | pam_211–226 | 16 | Submarine tender services, Mark 14 depth failure, ULTRA codebreaking, down-the-throat shot, mine threats, sinking accuracy, strategic impact, torpedo tube mechanics, forward battery/officers' quarters, Medal of Honor, crew mail, deck gun vs torpedoes, conning tower vs control room, Presidential Unit Citation, two-periscope design, Pampanito war record |

**All 226 entries pass regression tests across all 12 batches.**

---

## 2026-03-10 — Scoring Engine Fixes

Several retrieval engine bugs were fixed during batch 12 development:

- **`wants_mark_compare` over-trigger fixed** — previously fired for any torpedo query containing "mark", inflating `faq_982` (encyclopedic torpedo comparison FAQ) to score 36.0 on unrelated queries. Narrowed to require both Mark 14 and Mark 18 in query, or explicit comparison vocabulary (versus, difference, compare, etc.).
- **`raw_lower` variable order bug fixed** — `raw_lower` was referenced before assignment in `detect_intent()`; moved definition before the `wants_mark_compare` block.
- **Prepositions added to STOPWORDS** — "into", "onto", "upon", "within", "without", "through", "throughout" now filtered from query tokens, preventing them from blocking `all_q_covered` title-match checks.
- **`fired` synonym entry added** — expands to launch, launched, fire, shoot, shot, torpedo, tube; allows "how was a torpedo fired" to match FAQ titles using "launch".
- **`target` synonym expanded** — added "targets" so updated FAQ titles containing the plural form score correctly.
- **Title-bonus formula corrected** — `effective_weight = max(weight, weight * 4.0 * coverage)` ensures a perfect-coverage title always beats a partial one regardless of base weight.

---

## 2026-03-04–05 — Android Speech Recognition

Full voice input support added for Android browsers, which cannot use the browser's native Web Speech API against a local HTTPS server.

- **`/transcribe` POST endpoint** — accepts an audio file (WebM/OGG from MediaRecorder), sends to Groq `whisper-large-v3-turbo`, returns transcribed text (~0.3 s latency).
- **`/health` response extended** — now includes `transcribe_available: true/false` so the client can decide which speech path to use on startup.
- **Client dual-path routing** — on load, client calls `/health`; if `transcribe_available`, all voice input routes through the record → Groq path (bypassing native SpeechRecognition even on Android Chrome, which has `webkitSpeechRecognition` but fails with "No speech detected" on local servers).
- **Text input fallback** — on browsers with no microphone support at all (Android Firefox, Samsung Internet), the mic button converts to a keyboard icon and a text input row appears immediately.
- **Groq replaces OpenAI Whisper** — same `openai` Python client, different `base_url` and `GROQ_API_KEY`; faster and cheaper.

---

## 2026-03-04 — UX Improvements

- Password gate auto-submits on entering the 4th digit (no Enter button needed).
- FAQ source ID displayed below answer text when answer comes from the FAQ corpus.
- Race condition eliminated in speech initialisation — `enableRecordMode()` called synchronously.
- Default `transcribeAvailable=true` so TLS cert failures on first load don't silently break speech.

---

## 2026-03-02–03 — Retrieval Quality & Compartment Awareness

- **Compartment-aware retrieval** — query is matched against the visitor's current tour stop; tour chunks in that compartment score higher than off-compartment chunks.
- **Tour stop attribution** — answers from the audio tour corpus are prefixed with "From the audio tour in [location]."
- **Intent detection** — WHERE questions prepend "In the [location]." to the answer; HOW MANY questions activate a quantity-word score multiplier.
- **STT corrections** — phonetic substitutions added for common misrecognitions (e.g., "banks" → "bunks", torpedo-room homophones).
- **Synonym expansion** — domain synonyms added in batches alongside each new FAQ group (e.g., communicate, torpedo, fast/faster, crew, radar, medical, museum, storage, snorkel, wolfpack, convoy).
- **STOPWORDS tuning** — removed "happened/happen" (too domain-specific to suppress); added directional and universal submarine terms.

---

## 2026-03-02 — Feedback System

- Thumbs up / thumbs down widget on each answer.
- Optional free-text comment field.
- Responses logged to `feedback.jsonl`.
- `GET /feedback/list` endpoint returns recent entries.
- Password-gated feedback viewer page (`feedback.html`).

---

## 2026-03-01–02 — Infrastructure & Launch

- Deployed to Render.com (`submarinedocent.org`) with `render.yaml`.
- Added `GROQ_API_KEY` to Render environment for production Whisper transcription.
- Renamed `tour.html` → `pampanito.html`; added `/pampanito.html` redirect and root redirect to index.
- Password gate added to protect pre-launch preview.
- "Coming soon" index page for public-facing URL.
- Self-signed TLS certificates for local HTTPS (required for microphone access).
- `start_https.sh` — single-command server start/restart.
