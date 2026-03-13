# USS Pampanito — AI Docent

**Application Overview & Technical Summary**

---

## 1. What Is This?

SubmarineDocent is a voice- and text-enabled Q&A assistant that answers visitor questions about the USS Pampanito (SS-383) and WWII submarine history. It runs as a local HTTPS server on a Mac or small Linux machine, serving a mobile web app to any visitor's phone or a shared kiosk tablet over the local network.

Visitors speak or type a question and receive a spoken, historically accurate answer in seconds, drawn exclusively from verified museum-grade sources. No app download is required. No internet connection is needed during operation.

---

## 2. The Problem It Solves

Museum visitors are curious. They stand inside a torpedo room and want to know whether sailors actually slept next to live torpedoes, or how many men were on the boat, or what a depth charge felt like from inside. Fixed audio narration cannot answer these questions; human docents cannot be everywhere at once.

- Curiosity goes unrewarded — visitors leave with unanswered questions.
- Non-English-speaking visitors receive no additional context.
- Staff cannot scale to provide personalised responses to hundreds of visitors daily.

SubmarineDocent provides an always-available, on-premises AI guide that responds to natural spoken questions in real time.

---

## 3. Visitor Experience — How It Works

| Step | What Happens |
|------|-------------|
| **1. Arrive at a compartment** | The visitor enters a compartment (e.g., Control Room, Forward Torpedo Room) and taps to hear the narrated audio for that space. |
| **2. Listen to narration** | Pre-recorded audio plays — the same narration currently offered by the Pampanito tour. |
| **3. Ask a question** | At any point, the visitor taps a microphone (or record) button and speaks naturally: "How did the torpedo work?" or "Where did the crew sleep?" |
| **4. AI retrieves an answer** | The transcript is sent to the on-premises retrieval engine, which searches curated historical sources and assembles a direct spoken answer in under two seconds. |
| **5. Answer plays aloud** | The answer is read aloud through the visitor's phone speaker or headphones, with a spoken location prefix when relevant (e.g., "In the Control Room…"). |
| **6. Follow-ups offered** | The guide suggests related questions to keep exploration going. |
| **7. Unanswered questions** | If the system cannot find a reliable answer, it says so honestly rather than guessing. |

---

## 4. Knowledge Sources

The AI guide answers exclusively from three curated, authoritative corpora. It does not search the internet and cannot fabricate information.

| Source | Size | Description |
|--------|------|-------------|
| **Pampanito Tour Script** | 213 chunks | The official compartment-by-compartment narration for all 11 interior compartments plus forward and after decks. Each chunk is tagged with a compartment ID, location context, and display citation. |
| **Submarine FAQ Corpus** | 458 entries | Custom-authored Q&A pairs covering crew life, weapons, engineering, tactics, escape, medical, communications, and Pampanito-specific history. 226 entries (pam_001–pam_226) are Pampanito-focused; 232 entries cover WWII diesel-electric submarines broadly. |
| **DieselSubs Shorts** | 31 chunks | Concise background explanations on submarine systems, operations, and history, used to supplement answers when the other sources are insufficient. |

**Total corpus:** 702 chunks. Every answer includes a citation identifying which source and chunk the information came from.

---

## 5. Key Features

| Feature | Detail |
|---------|--------|
| **Voice input — iOS/desktop** | Browser Web Speech API (`webkitSpeechRecognition`) captures the question locally — no audio upload required. |
| **Voice input — Android** | Audio is recorded via MediaRecorder and POSTed to the `/transcribe` endpoint; Groq Whisper (`whisper-large-v3-turbo`) transcribes it server-side (~0.3 s latency). Falls back to a text input row on browsers without microphone support. |
| **Spoken answers** | Text-to-speech delivers answers aloud — eyes-free while exploring the boat. |
| **Multilingual audio** | Answers available in English, Spanish, French, German, Japanese, and Chinese. |
| **Location-aware retrieval** | The AI knows which compartment the visitor is standing in and weights results accordingly. |
| **No internet required** | Fully self-contained — runs on a Mac or small server on or near the vessel. (Groq Whisper requires internet only if Android transcription is enabled.) |
| **No app download** | Progressive Web App served over HTTPS — works in any modern smartphone browser. |
| **Honest fallback** | If no reliable answer is found, the system says so rather than guessing. `partial_match` flag signals relevant-but-indirect answers. |

---

## 6. Technical Architecture

The application is built on three layers: a browser-based frontend, an on-premises Python API server, and a local retrieval engine backed by curated JSONL corpora.

### 6.1 Frontend (`web/pampanito.html`)

A single-page application served directly by the backend. Designed for iOS Safari on iPhone as the primary visitor device, with full Android support.

- **Compartment-aware navigation** — 11 compartments + fore/aft deck, each with a unique ID passed to the API.
- **AudioContext playback** — GainNode normalises volume across narration, TTS answers, and pre-recorded fallback audio.
- **Voice input (dual path)** — On startup, the client calls `/health`; if `transcribe_available` is true, it routes all voice input through Groq Whisper (record → upload path). Otherwise it uses the browser's native Web Speech API. Browsers without any microphone support show a text input row.
- **Answer pipeline** — transcript POSTed to `/ask`; answer text POSTed to `/tts` for speech synthesis; audio streamed and played immediately.
- **No-cache headers** — visitors always load the latest tour version without a hard refresh.

### 6.2 API Server (`api/main.py`)

FastAPI application hosted with Uvicorn behind a self-signed TLS certificate (required for microphone access on mobile browsers).

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `POST /ask` | JSON: `question_text`, `compartment_id`, `playhead_time_ms` | Main Q&A endpoint. Runs retrieval + extractive synthesis; returns a structured answer with citations and `partial_match` flag. |
| `POST /tts` | JSON: `text`, `language` | Converts answer text to speech; returns an MP3 audio stream. |
| `POST /transcribe` | Multipart: audio file | Android speech path — sends audio to Groq Whisper; returns transcribed text. |
| `POST /contact` | Multipart form | Captures visitor contact info and unanswered question for historian review. |
| `GET /health` | — | Returns server status including `transcribe_available` flag (whether a Groq API key is configured). |
| `GET /pampanito.html` | — | Serves the tour frontend. |

### 6.3 Retrieval Engine

A custom token-overlap retrieval system with vocabulary expansion — no vector database or LLM required at query time. Designed for high accuracy on a closed, domain-specific corpus.

- **Tokenisation & stopword filtering** — query and corpus text are lowercased, punctuation-stripped, and filtered against a domain-tuned stopword list (including universal noise words like "submarine" that appear in every chunk, and prepositions such as "into", "upon", "through").
- **Synonym expansion (`QUERY_SYNONYMS`)** — query tokens are expanded with domain synonyms before scoring. For example, "eat" expands to *ate, galley, mess, food, meal*; "fired" expands to *launch, launched, tube*; "depth" expands to *deep, feet, dive, running, failure*. This bridges the vocabulary gap between visitor phrasing and corpus language.
- **Weighted corpus scoring** — Tour = 3.0×, FAQ = 1.2×, Shorts = 0.8×. Tour chunks in the visitor's current compartment score highest.
- **FAQ title-match bonus** — FAQ chunks whose question title covers all synonym-expanded query tokens receive up to a 4× coverage bonus (`max(weight, weight × 4.0 × coverage)`), ensuring the most precisely targeted FAQ answer wins over tangentially related tour passages.
- **Quantity boost** — for "how many" questions, chunks containing number words receive a 1.5× score multiplier.
- **Intent detection** — detects WHERE questions (prepends "In the [location]." to the answer), HOW MANY questions (activates quantity checking), and Mark 14/18 comparison questions (activates comparison-language boost only when both marks or explicit comparison vocabulary are present).

### 6.4 Extractive Answer Synthesis

Answers are assembled by extracting the most relevant sentences from the top-ranked corpus chunk — no LLM generation in the default deployment. This guarantees factual fidelity and eliminates hallucination risk.

- Sentences are filtered and ranked by synonym-expanded term overlap with the query.
- A second chunk is consulted if the first does not yield a complete answer.
- Speech filler words ("uh", "um", "er") are automatically stripped from oral-history transcript chunks before the answer is read aloud.
- A `partial_match` flag is returned when the answer is topically relevant but does not directly answer the question. The frontend plays a recorded "I don't have a direct answer, but here's what I know" prefix before reading the answer.

---

## 7. Answer Quality & Partial Match Logic

A key reliability feature is the system's ability to distinguish between a direct answer and a relevant-but-indirect answer.

| Condition | Example |
|-----------|---------|
| None of the core query terms appear in the assembled answer | Question about "escape hatches" but answer discusses hull construction |
| "How many X" question but no sentence contains both X and a number | "How many torpedoes" but answer only says they were stored forward |
| Question contains a superlative (worst, best, hardest…) but the answer does not address the judgment | "What was the worst bunk to sleep in" — answer describes bunks but cannot rank them |

When `partial_match` is `true`, the frontend plays a soft spoken prefix before reading the answer, setting visitor expectations correctly. If no relevant content is found at all, a separate "nothing found" audio clip plays.

---

## 8. Deployment

| Component | Detail |
|-----------|--------|
| **Hardware** | Mac (MacBook Pro, Mac Mini, or equivalent). No GPU required. |
| **Network** | Local Wi-Fi access point. Visitors connect via QR code or direct URL. Internet not required except for optional Groq Whisper transcription. |
| **TLS** | Self-signed certificate on port 8443 — required by browsers for microphone access (HTTPS). |
| **Python stack** | Python 3.10+, FastAPI, Uvicorn, OpenAI SDK (TTS), Groq API (Whisper transcription). All dependencies in a local virtual environment. |
| **Server startup** | Single command: `bash start_https.sh` — kills any prior instance, sources environment variables, starts Uvicorn. |
| **Environment** | `.env.local` — `GROQ_API_KEY` for Android transcription, other service keys as needed. |
| **LLM flag** | `USE_LLM=false` (default) — fully local, no LLM calls for Q&A. API stub present for future GPT-based synthesis. |

---

## 9. Current Status

**The application is a fully functional prototype.** It covers all 11 interior compartments plus the fore and aft decks of the Pampanito, and the AI guide can answer 226 custom-authored questions about the ship and her crew, plus hundreds more from the broader WWII submarine corpus.

| Capability | Status |
|------------|--------|
| Voice Q&A — iOS / desktop | ✓ Web Speech API |
| Voice Q&A — Android | ✓ Groq Whisper record mode |
| Text input fallback | ✓ All browsers |
| Multilingual TTS (6 languages) | ✓ |
| Compartment-aware retrieval | ✓ |
| Sub-2-second response time | ✓ |
| Honest partial-answer signalling | ✓ |
| 226 custom Pampanito FAQs | ✓ pam_001–pam_226 |
| LLM-backed synthesis | Stubbed — not enabled |

**Near-term roadmap:**

- Expand FAQ corpus to ~300 entries (batch 13+)
- Pre-cached TTS audio for the most common questions — instant playback without API latency
- Expanded corpus coverage: crew oral histories, patrol logs, post-war interviews
- QR code self-check-in for analytics (compartment traffic, popular questions)

---

*USS Pampanito — SS-383 | Fisherman's Wharf, San Francisco | AI Docent Prototype | 2026*
