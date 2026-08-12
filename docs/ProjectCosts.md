# Project Costs

As of August 12, 2026, this project has a relatively low fixed software cost in its current form. Most of the application is a FastAPI server plus static HTML, JavaScript, corpus files, images, and video. The main cost drivers are hosting, domain ownership, optional voice/transcription services, email delivery, and any museum hardware used for on-site deployment.

This document separates:

- Confirmed recurring costs based on the current repo and deployment model
- Variable or usage-based costs that depend on visitor traffic and enabled features
- One-time launch costs for a Pampanito deployment
- Future costs that would only appear if roadmap items are implemented

## 1. Current Architecture Cost Profile

The current repo indicates:

- A Python/FastAPI web app deployed on Render via `render.yaml`
- Static frontend assets served from the same app
- No database service configured in `render.yaml`
- No Redis, queue, cron, or separate worker configured
- Groq used only for transcription if `GROQ_API_KEY` is set
- OpenAI used for server-side spoken answers if `OPENAI_API_KEY` is set
- SMTP email used only if `SMTP_USER` and `SMTP_PASS` are set
- A server-side `/tts` endpoint now exists for built-in spoken answers
- ElevenLabs remains optional as a higher-quality alternative if the project chooses to fund it
- The current answer path is mainly extractive and does not require paid LLM generation for every question

That means the present system can still run with a low baseline cost, but spoken answers are now an actual usage-based operating cost when enabled.

## 2. Fixed Recurring Costs

### Hosting

Current hosting is Render.

Known public pricing observed on March 24, 2026:

- Render Hobby workspace: `$0/user/month` plus compute usage
- Render web service free instance: `$0/month`
- Render Starter web service: `$7/month`
- Render Standard web service: `$25/month`
- Render persistent disk: `$0.25/GB/month`

What this project likely needs:

- For a low-traffic public site or demo: `0` to `7` dollars per month is plausible if the app fits on a free or Starter instance
- For a more reliable public production site: budget `7` to `25` dollars per month for the web service
- Persistent disk cost is only needed if you decide to rely on Render disk storage rather than keeping corpora inside the deploy image

Practical planning number:

- Recommended budget for cloud hosting: `7` to `25` dollars per month

### Domain Names

The repo references both:

- `submarinedocent.org`
- legacy redirect from `submarinedocent.com`

The actual registrar is not documented in the repo, so the exact renewal price is unknown here. For planning purposes:

- One domain typically costs roughly `12` to `25` dollars per year
- Two domains typically cost roughly `24` to `50` dollars per year

Practical planning number:

- Domain budget: `25` to `50` dollars per year if both domains are retained

### TLS / HTTPS

For public Render hosting, managed TLS is included as part of the platform.

For local Pampanito deployment:

- Self-generated local certificates can be created at no direct software cost
- The real cost is operational time spent installing and trusting certificates on devices

Practical planning number:

- Public TLS software cost: `0` incremental dollars
- Local TLS operational cost: staff time, not a software subscription

## 3. Variable Operating Costs

### Groq Speech Transcription

The repo uses Groq for `POST /transcribe` when `GROQ_API_KEY` is configured.

Cost characteristics:

- This is usage-based, not a fixed monthly charge in the repo
- If transcription is disabled, project cost is `0`
- If transcription is enabled only on-site for moderate visitor use, cost should remain materially lower than a full LLM-per-question architecture

Important note:

- I could confirm from the repo that Groq is a real dependency, but I could not reliably pull a current public pricing page during this session, so the exact per-minute or per-token price should be verified directly before budgeting

Practical planning approach:

- Budget line item: `Groq transcription, usage-based, verify current pricing before launch`
- If voice input is optional or rarely used, keep this as a small contingency rather than a large fixed cost

### Email Delivery

The app sends contact/feedback email only if SMTP credentials are configured.

Current implementation suggests:

- Gmail SMTP is the default host
- If an existing account is used, incremental software cost may be `0`
- If a dedicated mailbox or Workspace account is preferred, cost depends on the chosen provider

Practical planning number:

- Existing email account: `0` incremental dollars
- Dedicated mailbox: provider-dependent, typically a small monthly admin cost

### Bandwidth / Media Delivery

This project includes:

- Static HTML/CSS/JS
- Local images
- Pampanito video files
- Audio files

The main bandwidth cost appears only if the public site gets meaningful traffic or if many users stream videos from the hosted app rather than from a local network.

Practical planning number:

- For modest traffic: covered by the selected hosting tier
- For heavy public media traffic: expect hosting tier pressure before code changes become the problem

### Spoken Answer Audio

The app now has a server-side `POST /tts` endpoint.  That means spoken answers can generate real API spend even when visitors do not provide their own voice-provider key.

OpenAI is now the selected built-in provider.  ElevenLabs remains the main higher-quality alternative to compare against.

For ElevenLabs, the clearest budgeting split is:

- `Flash / Turbo` for the lower-cost, English-oriented path
- `Multilingual v2 / v3` for higher-quality multilingual speech

Published ElevenLabs API rates observed on August 12, 2026:

- `Flash / Turbo`: `0.05` dollars per `1,000` characters
- `Multilingual v2 / v3`: `0.10` dollars per `1,000` characters

Practical monthly examples for `2,000` visitors, assuming each visitor plays one spoken answer:

- At `300` characters per spoken answer: about `30` dollars per month on ElevenLabs Flash / Turbo, or about `60` dollars per month on ElevenLabs Multilingual
- At `600` characters per spoken answer: about `60` dollars per month on ElevenLabs Flash / Turbo, or about `120` dollars per month on ElevenLabs Multilingual
- At `1,200` characters per spoken answer: about `120` dollars per month on ElevenLabs Flash / Turbo, or about `240` dollars per month on ElevenLabs Multilingual

If only half of visitors tap `Listen to answer`, those totals are cut roughly in half.

Practical planning number for ElevenLabs at `2,000` visitors per month:

- Lower-cost English-oriented voice: budget roughly `30` to `60` dollars per month
- Higher-quality multilingual voice: budget roughly `60` to `120` dollars per month

The actual bill depends most on three product choices:

- how many visitors tap the listen button
- how aggressively spoken answers are trimmed
- whether the project chooses the lower-cost English-oriented model or the multilingual-quality model

## 4. Current Costs That Are Effectively Zero

These features do not currently create a direct project bill in the present repo configuration:

- Server-side LLM answer synthesis: not implemented as an active paid path
- Database hosting: none configured
- Redis / cache hosting: none configured
- Queue workers / cron jobs: none configured
- Analytics platform: none configured

This is why the current app can remain inexpensive unless voice usage becomes heavy or future AI features expand.

## 5. One-Time Pampanito Deployment Costs

If the goal is to deploy this project physically on the Pampanito rather than only as a public site, the main one-time costs are operational and hardware-related.

### Local Server Hardware

If you reuse an existing machine:

- Cost can be `0`

If you buy a dedicated machine:

- Small-form desktop or laptop for local hosting: roughly `500` to `1,500` dollars depending on the device standard the museum wants

Recommended planning number:

- Dedicated local server hardware budget: `800` to `1,200` dollars

### Visitor Devices

If visitors use their own phones:

- Device cost is `0` for the project

If the museum supplies devices:

- Phones or tablets become a major capital cost
- Headphones, charging stations, and theft-resistant mounts also matter

Recommended planning note:

- This can exceed software costs very quickly and should be budgeted separately from app development

### Network Setup

Potential one-time costs:

- RF site survey and compartment-by-compartment connectivity testing
- One or more local access points, or a wired backhaul plus compartment-local access points
- Cabling, power cleanup, and mounting hardware
- Device testing and signal validation in the submarine environment

Important operational constraint:

- The steel hull, bulkheads, narrow compartments, and visitor layout make whole-submarine Wi-Fi coverage an unsafe planning assumption
- Full-vessel BYOD coverage is a project requirement, so the cost model must assume network engineering beyond a single access point
- A practical deployment will likely require multiple access points, wired segments, careful channel planning, and repeated on-site RF testing until visitor phones stay connected across the full tour path

Expected budget:

- Could be `0` if existing infrastructure is reused
- Could be a few hundred dollars for a simple segmented network
- Could be materially more if the solution requires multiple access points, cabling runs, ruggedized mounting, and repeated on-site RF testing
- Because full-vessel BYOD coverage is mandatory, network costs should be treated as required launch costs rather than optional improvements

### Content Production

Current repo state shows that audio and multilingual polish are incomplete.

Likely one-time content costs if quality is upgraded:

- Recording or generating fallback audio in multiple languages
- Producing pre-cached audio for top FAQ questions
- Video editing or compression for Pampanito media assets
- Translation review if multilingual text output is added later

This is mostly labor cost, not infrastructure cost.

## 6. Scenario Budgets

### Scenario A: Lowest-Cost Public Site

Assumptions:

- Render free or low-cost instance
- No Groq transcription in production
- No dedicated email account
- No museum-provided devices

Estimated recurring cost:

- Monthly: `0` to `7` dollars
- Annual domains: `25` to `50` dollars

Best use:

- Public informational site
- Internal demo
- Small pilot

### Scenario B: Practical Public Production Site

Assumptions:

- Render Starter or Standard instance
- Domains retained
- SMTP enabled
- Some Groq voice transcription usage

Estimated recurring cost:

- Hosting: `7` to `25` dollars per month
- Domain renewals: `25` to `50` dollars per year
- Groq: small variable usage line item
- Email: `0` to low monthly admin cost

Recommended planning total:

- Rough baseline: `10` to `40` dollars per month, plus annual domain renewal

### Scenario C: On-Prem Pampanito Deployment

Assumptions:

- App runs on a local machine on the ship or in museum infrastructure
- Public cloud hosting may still exist for the website, but the tour itself can run locally
- Full-vessel BYOD coverage is required for launch
- The network design must support visitor phones across the entire required tour path, not only in selected compartments

Estimated recurring cost:

- Software hosting: potentially `0` to very low if local-only
- Groq transcription: variable, only if internet-backed transcription is enabled
- Domain cost: only needed if public access remains important

Estimated one-time cost:

- Local host machine: `0` to `1,500` dollars
- Network hardware/setup: `200` dollars to low thousands, depending on whether the final design is one access point, multiple wired access points, and how much cable/power work is required
- Device trust/certificate setup: staff labor

This scenario often has lower software cost than expected; the real work is hardware reliability, full-path BYOD connectivity, local HTTPS, and museum operations.

## 7. Future Costs If Roadmap Items Are Implemented

The repo roadmap implies these possible future cost increases.

### Server-Side TTS

The project now has a `/tts` endpoint using OpenAI.  If the project instead switches that path to ElevenLabs, or adds ElevenLabs as the primary spoken-answer provider:

- Every spoken answer can become a billable API event
- This is likely the single clearest new recurring cost after hosting

ElevenLabs planning range at `2,000` visitors per month:

- `Flash / Turbo` without multilingual-quality voice: roughly `30` to `60` dollars per month at typical short-answer lengths
- `Multilingual v2 / v3` with higher multilingual quality: roughly `60` to `120` dollars per month at typical short-answer lengths
- If answers regularly reach the app's `1,200` character cap, those figures can roughly double

### LLM Answer Synthesis

If the `USE_LLM` path is fully implemented:

- Each question may incur LLM inference cost
- This can move the project from a low-cost retrieval app to an ongoing AI operating expense

### Multilingual Translation

If answers are translated dynamically:

- Translation API usage becomes a recurring cost per answer

### Pre-Generated Audio Library

If you pre-generate top-question audio in six languages:

- There may be a one-time generation cost
- Storage and bandwidth costs may increase modestly

## 8. Recommended Budget Framing

For planning and approval purposes, the project is best described like this:

- Current software baseline: low-cost
- Main fixed recurring cost: hosting plus domain renewal
- Main variable recurring cost: Groq transcription, only if voice input is enabled
- Main new variable recurring cost when spoken answers are enabled: server-side TTS
- Main one-time Pampanito cost: hardware, submarine-specific full-vessel BYOD network design, and deployment labor
- Main future budget risk: adding server-side TTS or full LLM generation

A reasonable budgeting summary for the project in its current state is:

- Public/cloud deployment only: about `10` to `40` dollars per month plus domains
- Local Pampanito deployment with reused hardware: near-zero software cost, mostly labor
- Local Pampanito deployment with dedicated hardware: roughly `800` to `1,500` dollars one-time plus any optional cloud/API spend

## 9. Deployment Recommendation

For Pampanito deployment planning, the network should be treated as the primary technical risk.

- Full-vessel BYOD coverage is a hard requirement, not a nice-to-have
- The project should not assume a normal building-style Wi-Fi rollout will work inside the submarine
- The network design should be budgeted as required launch infrastructure, alongside the host machine itself
- The launch decision should depend on real end-to-end phone testing across the full visitor path, not only spot checks near an access point

In practical terms, this means the highest-uncertainty budget line is not the app server or the AI API usage. It is the submarine-specific network engineering needed to keep visitor phones connected everywhere the experience is supposed to work.

## 10. Recommended Next Step

Before using this document as a final approval budget, verify these three items with current vendor accounts:

- Actual Render service tier in production
- Current Groq pricing for the transcription model you intend to use
- Whether both domains still need to be renewed

Once those three are confirmed, this document can be converted into a final budget sheet with exact monthly and annual totals.
