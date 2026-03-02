# USS Pampanito AI Docent — TODO / Not Yet Implemented

Items described in [overview.md](overview.md) that are partially or fully unimplemented.
Organised by priority.

---

## 🔴 High Priority

### 1. Multilingual Tour Narration Audio
**What the doc says:** Narration plays for each compartment.
**Reality:** The 13 compartment audio files (`01_after_deck.mp3` → `13_forward_deck.mp3`) are English only. No Spanish, French, German, Japanese, or Chinese narration has been recorded or imported.

**To do:**
- Record or generate narration audio for each of the 6 supported languages
- Name files using the existing convention: `01_after_deck_es.mp3`, `01_after_deck_fr.mp3`, etc.
- The frontend already requests language-suffixed filenames — the files just don't exist yet

---

### 2. Built-in Text-to-Speech for AI Answers
**What the doc says:** "Text-to-speech delivers answers aloud."
**Reality:** There is no server-side `/tts` endpoint. The TTS chain is:
1. Pre-recorded FAQ audio (only 1 question has been recorded — see item 3)
2. ElevenLabs API — requires the visitor to manually enter a personal API key in the Settings panel
3. Browser `SpeechSynthesis` fallback — robotic quality; language support depends on device

In practice, most visitors hear browser SpeechSynthesis — robotic and English-accented regardless of language setting.

**To do:**
- Add a server-side `/tts` endpoint (OpenAI TTS or ElevenLabs) that takes `text` + `language` and returns MP3 audio
- Remove the requirement for visitors to supply their own API key
- This is the single highest-impact quality improvement available

---

### 3. Pre-Cached FAQ Audio at Scale
**What the doc says:** "Pre-recorded TTS answers that play instantly without any wait."
**Reality:** Only **one** FAQ question (`faq_594`) has pre-recorded audio, in all 6 languages. The remaining ~228 FAQ answers have no audio files — they fall through to ElevenLabs/browser TTS.

**To do:**
- Identify the top 50–100 most likely questions
- Generate TTS audio for each in all 6 languages using the established naming convention (`faq_{id}_{lang}.mp3`)
- Add audio files to `web/audio/`

---

## 🟡 Medium Priority

### 4. Follow-up Question Suggestions
**What the doc says:** "The guide proposes related questions to deepen visitor engagement."
**Reality:** The `/ask` API does return a `followups` array in every response, but the frontend completely ignores it — nothing is displayed or spoken.

**To do:**
- After an answer plays, display 2–3 follow-up question buttons in the UI
- Tapping a follow-up should submit it as a new question
- Optionally speak the follow-up options aloud too

---

### 5. Multilingual AI Answer Text
**What the doc says:** "Answers available in English, Spanish, French, German, Japanese, and Chinese."
**Reality:** The extractive synthesis in `api/main.py` always returns English text, because the corpora are in English. Even if TTS could speak other languages, the answer text itself would be English.

**To do:**
- Either: run answer text through a translation step before returning it (e.g. OpenAI `gpt-4o` translate)
- Or: source/create translated corpora for the target languages
- Neither option is currently implemented

---

### 6. Fallback Audio Files in Multiple Languages
**What the doc says:** Graceful fallback audio plays when the system can't answer.
**Reality:** `nodirectanswer.mp3`, `nothits.mp3`, `emailaddressorphonenumber.mp3`, and `wewillgetbacktoyou.mp3` are English only.

**To do:**
- Record/generate the four fallback audio clips in each supported language
- Update the frontend to select the language-appropriate fallback file

---

## 🟢 Roadmap (Acknowledged in doc as future work)

### 7. LLM-Backed Answer Synthesis
**Status:** Code stub exists (`USE_LLM` flag in `api/main.py`) but the GPT-4o synthesis path has not been implemented or tested.
**Blocks on:** OpenAI API budget/funding.

---

### 8. Pre-Cached TTS for Top 50 Questions
**Status:** Listed as near-term roadmap. Depends on item 2 (server-side TTS) being completed first so audio can be generated at scale.

---

### 9. Expanded Corpus Coverage
**Status:** Not started.
- Crew oral history transcripts
- WW2 patrol log excerpts
- Post-war interviews
- USS Pampanito-specific technical documents

---

### 10. QR Code Self-Check-In / Analytics
**Status:** Not started. No analytics instrumentation exists.
- Track which compartments get the most questions
- Track which questions are most frequently asked
- Track language distribution

---

## 📋 Documentation Corrections Needed

The overview in `overview.md` contains some inaccuracies introduced before the current architecture was confirmed:

| Section | What doc says | Reality |
|---------|--------------|---------|
| Section 6.2, API table | `POST /tts` endpoint exists | No `/tts` endpoint — TTS is entirely client-side |
| Section 6.2, Python stack | "OpenAI SDK (TTS only)" | OpenAI SDK is not used at all currently (Whisper removed; no TTS endpoint). ElevenLabs is used client-side if the user provides a key. |
| Section 5, Features | "Spoken answers" implies reliable TTS | In practice: robotic browser SpeechSynthesis unless visitor enters ElevenLabs key |
| Section 5, Features | "Multilingual audio" | Tour narration is English only; subtitles/translated answers not implemented |

---

*Last updated: March 2026*
