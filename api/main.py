# api/main.py
from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import io
import json
import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Tuple, Any, Optional

app = FastAPI(title="Pampanito Local RAG Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve web/ as static files at /
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WEB_DIR = os.path.join(BASE_DIR, "web")

@app.get("/", include_in_schema=False)
def root_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/web/index.html")

if os.path.isdir(WEB_DIR):
    # Convenience redirect: /pampanito.html → /web/pampanito.html
    @app.get("/pampanito.html", include_in_schema=False)
    def redirect_tour_html():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/pampanito.html")

    # Convenience redirect: /feedback.html → /web/feedback.html
    @app.get("/feedback.html", include_in_schema=False)
    def redirect_feedback_html():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/feedback.html")

    # Serve pampanito.html with no-cache so Safari always loads the latest version
    @app.get("/web/pampanito.html", include_in_schema=False)
    def serve_tour_html():
        return FileResponse(
            os.path.join(WEB_DIR, "pampanito.html"),
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    app.mount("/web", StaticFiles(directory=WEB_DIR, html=True), name="web")
CORPORA_DIR = os.path.join(BASE_DIR, "corpora")

TOUR_PATH = os.path.join(CORPORA_DIR, "pampanito_tour_corpus.jsonl")
FAQ_PATH = os.path.join(CORPORA_DIR, "dieselsubs_faq_corpus.jsonl")
SHORTS_PATH = os.path.join(CORPORA_DIR, "dieselsubs_shorts_corpus.jsonl")

# Feature flag: keep demo fully local today; later, flip to true with funding.
USE_LLM = os.getenv("USE_LLM", "false").lower() in ("1", "true", "yes")

# Groq key — used for Whisper transcription (whisper-large-v3-turbo, ~0.3s latency)
_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ── Historian contact email ────────────────────────────────────────────────
HISTORIAN_EMAIL = os.getenv("HISTORIAN_EMAIL", "irving.greisman@gmail.com")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")   # set in start_https.sh
SMTP_PASS = os.getenv("SMTP_PASS", "")   # Gmail App Password


def load_jsonl(path: str) -> List[Dict[str, Any]]:
    data: List[Dict[str, Any]] = []
    print(f"Loading file: {path}")

    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return data

    # utf-8-sig handles BOM if present
    with open(path, "r", encoding="utf-8-sig") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except Exception as e:
                print(f"⚠️ JSON parse error on line {i} in {path}: {e}")
                break

    print(f"✅ Loaded {len(data)} records from {os.path.basename(path)}")
    return data


print("Loading corpora...")
TOUR = load_jsonl(TOUR_PATH)
FAQ = load_jsonl(FAQ_PATH)
SHORTS = load_jsonl(SHORTS_PATH)
print(f"Loaded: {len(TOUR)} tour, {len(FAQ)} faq, {len(SHORTS)} shorts chunks")



@app.post("/contact")
async def contact(
    question_text: str = Form(""),
    visitor_response: str = Form(""),
    lang: str = Form("en"),
    audio: Optional[UploadFile] = File(None),
):
    """Receive a visitor question + contact response and email the historian."""
    question = question_text.strip()
    visitor_response = visitor_response.strip()

    lang_label = {
        "en": "English", "fr": "French", "de": "German",
        "es": "Spanish", "zh": "Chinese", "ja": "Japanese",
    }.get(lang, lang)

    body = (
        f"Tour language: {lang_label}\n\n"
        f"Visitor question (as heard in {lang_label}):\n{question}\n\n"
        f"Visitor contact info:\n{visitor_response}"
    )
    print(f"[CONTACT] {body}")

    if not SMTP_USER or not SMTP_PASS:
        return {"status": "logged", "note": "Set SMTP_USER and SMTP_PASS env vars to enable email."}

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = HISTORIAN_EMAIL
        msg["Subject"] = "Pampanito Visitor Question"
        msg.attach(MIMEText(body, "plain"))

        # Attach audio recording if provided
        if audio:
            audio_bytes = await audio.read()
            if audio_bytes:
                ct = (audio.content_type or "audio/webm")
                ext = "mp4" if "mp4" in ct else "webm"
                part = MIMEBase("audio", ext)
                part.set_payload(audio_bytes)
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment", filename=f"question.{ext}")
                msg.attach(part)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        return {"status": "sent"}
    except Exception as e:
        print(f"[CONTACT] Email send failed: {e}")
        return {"status": "error", "detail": str(e)}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "use_llm": USE_LLM,
        "transcribe_available": bool(_GROQ_API_KEY),
        "tour_chunks": len(TOUR),
        "faq_chunks": len(FAQ),
        "shorts_chunks": len(SHORTS),
        "corpora_dir": CORPORA_DIR,
    }


@app.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    lang: str = Form("en"),
):
    """Transcribe visitor speech using Groq Whisper (whisper-large-v3-turbo).
    Accepts any audio format MediaRecorder can produce (webm, mp4, ogg).
    Returns {transcript: str}.
    """
    if not _GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="Transcription not available: GROQ_API_KEY not set")

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio")

    ct = (audio.content_type or "").lower()
    if "mp4" in ct or "mpeg" in ct:
        ext = "mp4"
    elif "ogg" in ct:
        ext = "ogg"
    elif "wav" in ct:
        ext = "wav"
    else:
        ext = "webm"

    buf = io.BytesIO(audio_bytes)
    buf.name = f"audio.{ext}"  # openai client uses the name for format detection

    lang_map = {"en": "en", "fr": "fr", "de": "de", "es": "es", "zh": "zh", "ja": "ja"}
    whisper_lang = lang_map.get(lang, "en")

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(
            api_key=_GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        result = await client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=buf,
            language=whisper_lang,
        )
        transcript = (result.text or "").strip()
        print(f"[TRANSCRIBE] '{transcript[:80]}'")
        return {"transcript": transcript}
    except Exception as e:
        print(f"[TRANSCRIBE] Groq Whisper error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------------
# Retrieval: robust token overlap + intent gating
# ------------------------------------------------------------

STOPWORDS = {
    "the", "a", "an", "what", "were", "was", "is", "are", "of", "on", "in",
    "to", "and", "for", "some", "between", "did", "do", "does", "you",
    "it", "that", "this", "with", "as", "at", "by", "from", "about",
    "whats", "what's", "difference", "please", "tell", "me",
    # question / wh- words that carry no domain meaning on their own
    # NOTE: "why" is intentionally NOT here — it drives is_why_question intent detection
    "where", "how", "when", "who", "which", "whose", "whom",
    # directional/location words too common on a submarine to be useful signals
    "after", "forward",
    # context-universal words: every chunk is about a submarine/boat
    "submarine", "boat", "sub",
    # ultra-generic verbs / pronouns with no domain signal
    "got", "get", "gets", "gotten", "happened", "happen",
    "someone", "something", "somebody", "anyone", "anything",
    "people", "person", "things", "thing",
}


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    # keep numbers (Mark 14 / Mark 18), strip punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # keep tokens longer than 2 chars, OR 2-char pure numbers (e.g. "14", "18")
    toks = [t for t in text.split() if t not in STOPWORDS and (len(t) > 2 or (len(t) == 2 and t.isdigit()))]
    return toks


# Compartment phrases where a word that is normally meaningful (e.g. "battery",
# "room") is being used purely as a location name.  When the raw query contains
# one of these phrases we drop the ambiguous word from the query tokens so it
# doesn't match unrelated corpus content (e.g. "battery" → electrical cells).
_COMPARTMENT_AMBIGUOUS_TOKENS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\bafter\s+battery\b", re.I), "battery"),
    (re.compile(r"\bforward\s+battery\b", re.I), "battery"),
]


def remove_compartment_noise(tokens: List[str], raw_query: str) -> List[str]:
    """Drop tokens that are ambiguous location words in this raw query context."""
    drop: set = set()
    for pattern, ambiguous_tok in _COMPARTMENT_AMBIGUOUS_TOKENS:
        if pattern.search(raw_query):
            drop.add(ambiguous_tok)
    if not drop:
        return tokens
    return [t for t in tokens if t not in drop]


# Maps query-phrase patterns to corpus compartment_id values.
# When the visitor names a compartment in their question, tour chunks from
# that compartment get a strong scoring boost so we don't accidentally
# answer about the wrong location.
_COMPARTMENT_QUERY_MAP: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\bafter\s+battery\b", re.I),          "after_battery"),
    (re.compile(r"\bforward\s+battery\b", re.I),         "forward_battery"),
    (re.compile(r"\bafter\s+torpedo\b", re.I),           "after_torpedo_room"),
    (re.compile(r"\bforward\s+torpedo\b", re.I),         "forward_torpedo_room"),
    (re.compile(r"\bconning\s+tower\b", re.I),           "conning_tower"),
    (re.compile(r"\bcontrol\s+room\b", re.I),            "control_room"),
    (re.compile(r"\bengine\s+room\b", re.I),             "engine_room"),
    (re.compile(r"\bafter\s+deck\b|\bafterdeck\b", re.I), "after_deck"),
    (re.compile(r"\bforward\s+deck\b|fore\s+deck\b|\bforedeck\b", re.I), "forward_deck"),
    (re.compile(r"\bforward\s+engine\b", re.I),          "forward_engine_room"),
    (re.compile(r"\bafter\s+engine\b", re.I),            "after_engine_room"),
    (re.compile(r"\bward\s*room\b", re.I),               "wardroom"),
    (re.compile(r"\bgalley\b", re.I),                    "galley"),
    (re.compile(r"\bknife\s+&\s+fork\b|\bdining\b", re.I), "wardroom"),
]


def detect_compartment_in_query(raw_query: str) -> Optional[str]:
    """Return the corpus compartment_id named in the query, or None."""
    for pattern, cid in _COMPARTMENT_QUERY_MAP:
        if pattern.search(raw_query):
            return cid
    return None


# Synonym expansion applied to query tokens before scoring.
# Maps a query word to extra tokens that count as a match in the corpus.
QUERY_SYNONYMS: Dict[str, List[str]] = {
    "eat":    ["ate", "eaten", "eating", "food", "meal", "meals", "galley", "mess", "chow", "cook", "cooks", "cooked", "dining", "breakfast", "lunch", "dinner"],
    "ate":    ["eat", "eaten", "food", "meal", "meals", "galley", "mess", "chow"],
    "food":   ["eat", "ate", "meal", "meals", "galley", "mess", "chow", "cook", "cooked"],
    "sleep":  ["slept", "sleeping", "bunk", "bunks", "bed", "beds", "rack", "racks", "berthing"],
    "slept":  ["sleep", "bunk", "bunks", "bed", "beds", "rack", "racks"],
    "work":   ["worked", "working", "duty", "watch", "operate", "operated", "station"],
    "live":   ["lived", "living", "berthing", "bunk", "quarters", "crew"],
    "shower": ["showers", "bath", "wash", "washing", "hygiene", "head"],
    "toilet": ["head", "restroom", "bathroom", "latrine"],
    "gun":    ["guns", "deck gun", "cannon", "weapon", "weapons", "armament"],
    "shoot":  ["fire", "fired", "firing", "launch", "launched", "torpedo", "attack"],
    "dive":   ["dived", "diving", "submerge", "submerged", "submerging", "crash dive"],
    "speed":  ["knots", "fast", "faster", "slow", "slower", "velocity"],
    "engine": ["engines", "motor", "motors", "diesel", "electric", "power", "drive"],
    # crew-size questions: "men" and "served" should find crew/complement content
    "men":    ["crew", "sailors", "crewmen", "enlisted", "personnel", "complement"],
    "served": ["crew", "crewmen", "complement", "enlisted", "assigned"],
    "crew":   ["men", "sailors", "crewmen", "complement", "personnel", "enlisted"],
    # illness / medical questions
    "sick":    ["ill", "illness", "health", "doctor", "pharmacist", "medical", "medicine", "injury", "injured", "wound", "wounded", "hurt"],
    "ill":     ["sick", "illness", "health", "doctor", "pharmacist", "medical"],
    "doctor":  ["pharmacist", "medical", "health", "sick", "ill", "medicine"],
    "medical": ["doctor", "pharmacist", "health", "sick", "ill", "medicine", "injury"],
    "hurt":    ["injured", "injury", "wound", "wounded", "sick", "ill", "medical"],
    # computer / fire control questions → TDC in conning tower
    "computer":  ["torpedo data computer", "tdc", "fire control", "targeting", "conning tower", "periscope", "attack"],
    "computers": ["torpedo data computer", "tdc", "fire control", "targeting", "conning tower"],
    "tdc":       ["torpedo data computer", "computer", "fire control", "targeting", "attack"],
    # Speech-to-text substitutions: common mis-transcriptions mapped to intended words
    # "controls" → "patrols" is a very common STT error (same syllable pattern)
    "controls":  ["patrols", "patrol", "war patrol", "missions", "mission", "voyages"],
    # "complete" / "completed" used when asking about patrols Pampanito finished
    "complete":  ["completed", "conducted", "finished", "ran", "made", "patrols"],
    # "afterdeck" (one word) ↔ "after deck" (two words) — both forms used by visitors
    "afterdeck": ["after deck", "deck", "gun", "deck gun", "aft", "after"],
    "foredeck":  ["forward deck", "deck", "gun", "deck gun", "forward"],
}


def expand_query_tokens(tokens: List[str]) -> List[str]:
    """Return query tokens plus corpus-side synonyms for better vocabulary coverage."""
    expanded = list(tokens)
    seen = set(tokens)
    for t in tokens:
        for syn in QUERY_SYNONYMS.get(t, []):
            if syn not in seen:
                expanded.append(syn)
                seen.add(syn)
    return expanded


def overlap_score(query_tokens: List[str], text: str) -> int:
    """Count token overlap using synonym-expanded query against text.
    Multiple matches from the same synonym group each count separately,
    so a food-rich chunk (breakfast + meal + galley) outranks one with a
    single synonym hit.  We avoid synonym inflation by not mapping generic
    terms (like 'officers') into the synonym table."""
    expanded = expand_query_tokens(query_tokens)
    text_tokens = set(tokenize(text))
    return len(set(expanded) & text_tokens)


def detect_intent(query_tokens: List[str], raw_question: str = "") -> Dict[str, Any]:
    """
    Very lightweight intent detection used only to gate obviously-wrong hits.
    """
    tset = set(query_tokens)
    wants_mark_compare = (
        ("mark" in tset and ("14" in tset or "18" in tset)) or
        ("torpedo" in tset and "mark" in tset)
    )

    # Quantity question: "how many", "how much", "what number", etc.
    raw_lower = raw_question.lower()
    wants_quantity = bool(
        re.search(r"how many|how much|how\s+\w+\s+(are|were|is|was)\b", raw_lower) or
        "many" in tset or "count" in tset or "number of" in raw_lower
    )

    # Location question: starts with "where" or contains key where-phrases
    is_where_question = bool(
        re.match(r"\s*where\b", raw_lower) or
        re.search(r"\bwhere (did|do|does|is|are|was|were|can)\b", raw_lower)
    )

    # Causal/reason question: starts with "why" or asks for a reason/cause
    is_why_question = bool(
        re.match(r"\s*why\b", raw_lower) or
        re.search(r"\b(reason|reasons|cause|causes|caused|motive|motives|motivation)\b", raw_lower)
    )

    return {
        "wants_mark_compare": wants_mark_compare,
        "wants_quantity": wants_quantity,
        "is_where_question": is_where_question,
        "is_why_question": is_why_question,
    }


MARK_COMPARE_SIGNAL_TERMS = [
    "mark 14", "mk 14", "mark 18", "mk 18",
    "steam", "wet heater", "wet-heater",
    "electric", "battery",
    "torpex", "warhead", "range", "speed"
]

# Phrases that indicate a chunk is *comparing* rather than just enumerating.
COMPARISON_LANGUAGE = [
    "advantage", "advantages", "on the other hand", "better",
    "however", "compare", "comparison", "differ", "whereas",
    "versus", "vs.", "trade-off", "tradeoff",
]


def intent_gate(text: str, intent: Dict[str, Any]) -> bool:
    """
    If the question is clearly about Mk14 vs Mk18, require signal terms.
    Otherwise allow.
    """
    if not intent.get("wants_mark_compare"):
        return True

    tl = (text or "").lower()
    return any(k in tl for k in MARK_COMPARE_SIGNAL_TERMS)


# (score, chunk, source_id)
Hit = Tuple[float, Dict[str, Any], str]


def retrieve(
    question_text: str,
    compartment_id: str,
    playhead_time_ms: Optional[int] = None,
    top_k: int = 8
) -> List[Hit]:
    """
    Local demo retriever:
    - Tour in current compartment gets highest weight.
    - FAQ is global reference, lower weight.
    - Shorts is lowest authority.
    - Stopword-safe overlap scoring.
    - Intent gating to prevent obviously wrong matches.
    """
    q_tokens = tokenize(question_text)
    q_tokens = remove_compartment_noise(q_tokens, question_text)
    intent = detect_intent(q_tokens, question_text)
    named_compartment = detect_compartment_in_query(question_text)

    hits: List[Hit] = []

    # Terms for comparison-boost: chunk must contain both sides
    _BOTH_MARKS_RE = [
        (re.compile(r"mark\s*14|mk\s*14", re.I), re.compile(r"mark\s*18|mk\s*18", re.I))
    ]

    def _has_both_marks(text: str) -> bool:
        return bool(_BOTH_MARKS_RE[0][0].search(text) and _BOTH_MARKS_RE[0][1].search(text))

    # helper
    def add_hits(chunks: List[Dict[str, Any]], source_id: str, weight: float, compartment_filter: bool):
        for ch in chunks:
            if compartment_filter and ch.get("compartment_id") != compartment_id:
                continue

            text = ch.get("text", "") or ""
            s = overlap_score(q_tokens, text)
            if s <= 0:
                continue

            if not intent_gate(text, intent):
                continue

            effective_weight = weight

            # If the query explicitly names a compartment, strongly boost tour
            # chunks from that compartment so they outrank equally-relevant
            # chunks from other locations (e.g. "bunks in after battery" should
            # not be answered with After Torpedo Room bunk content).
            if named_compartment and source_id == "pampanito_tour":
                if ch.get("compartment_id") == named_compartment:
                    effective_weight *= 3.0

            # FAQ question-title match bonus: reward titles whose vocabulary
            # closely matches the query. Scale by title coverage so a short,
            # specific title like "What is a torpedo?" (coverage=1.0) beats
            # "What is in the after torpedo room?" (coverage=0.33) even when
            # both contain the only query token "torpedo".
            raw_paras = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
            if raw_paras and raw_paras[0].rstrip().endswith("?"):
                title_toks = set(tokenize(raw_paras[0]))
                q_set = set(q_tokens)
                if q_set and title_toks:
                    # Use synonym-expanded query tokens so e.g. "served"→"assigned"
                    # still matches a FAQ title like "How many men were assigned?"
                    q_expanded_set = set(expand_query_tokens(q_tokens))
                    matched = len(q_expanded_set & title_toks)
                    coverage = matched / len(title_toks)  # fraction of title covered by query
                    # "All covered" = every original query token appears directly
                    # or via synonym expansion in the title
                    all_q_covered = all(
                        t in title_toks or
                        any(syn in title_toks for syn in QUERY_SYNONYMS.get(t, []))
                        for t in q_set
                    )
                    if all_q_covered:
                        # All query intent represented in title: scale 4x by coverage
                        effective_weight = weight * 4.0 * coverage
                    elif matched >= max(1, len(q_set) - 1):
                        # Near-exact (all but one): scale 2x by coverage
                        effective_weight = weight * 2.0 * coverage

            # For comparison queries, strongly boost chunks that discuss both sides
            if intent.get("wants_mark_compare") and _has_both_marks(text):
                effective_weight = max(effective_weight, weight * 2.5)
                # Extra bonus for chunks that use comparison language (analysis vs enumeration)
                comp_bonus = sum(1 for phrase in COMPARISON_LANGUAGE if phrase in text.lower())
                hits.append((s * effective_weight + comp_bonus, ch, source_id))
                continue

            # For quantity questions, boost chunks that actually contain a number —
            # they are far more likely to directly answer "how many" questions.
            if intent.get("wants_quantity") and re.search(
                r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten"
                r"|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen"
                r"|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy"
                r"|eighty|ninety|hundred|thousand|dozen)\b",
                text, re.I
            ):
                effective_weight *= 1.5

            hits.append((s * effective_weight, ch, source_id))

    # Tour – search all compartments; current compartment chunks naturally
    # score highest because they share the most vocabulary with a question
    # asked while standing there.  Restricting to the current compartment
    # caused cross-compartment "where is X?" questions to miss the right chunk.
    add_hits(TOUR, "pampanito_tour", weight=3.0, compartment_filter=False)

    # FAQ (global)
    add_hits(FAQ, "dieselsubs_faq", weight=1.2, compartment_filter=False)

    # Shorts (global)
    add_hits(SHORTS, "dieselsubs_shorts", weight=0.8, compartment_filter=False)

    hits.sort(key=lambda x: x[0], reverse=True)
    return hits[:top_k]


# ------------------------------------------------------------
# Synthesis: Extractive now, OpenAI later (stubbed)
# ------------------------------------------------------------

def split_sentences(text: str) -> List[str]:
    # Normalize non-breaking spaces; split on whitespace after .!?
    # OR on a period immediately followed by a capital letter (no space in corpus text)
    text = (text or "").replace("\xa0", " ").strip()
    parts = re.split(r"(?<=[.!?])\s+|(?<=[.!?])(?=[A-Z])", text)
    return [p.strip() for p in parts if p.strip()]


def best_sentences(text: str, want_terms: List[str], max_sentences: int = 2) -> List[str]:
    """
    Extract up to max_sentences sentences that contain the most want_terms.
    """
    want_terms_l = [w.lower() for w in want_terms]
    sents = split_sentences(text)
    scored: List[Tuple[int, str]] = []
    for s in sents:
        sl = s.lower()
        sc = sum(1 for w in want_terms_l if w in sl)
        if sc > 0:
            scored.append((sc, s))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [s for _, s in scored[:max_sentences]]


def synthesize_extractive(
    question_text: str,
    hits: List[Hit]
) -> Dict[str, Any]:
    """
    Demo-friendly "docent-ish" answer without an LLM:
    - From the top-ranked chunk, extract sentences in their original order,
      preserving narrative flow and context-setting sentences.
    - Skips any leading title/question line (ends with '?').
    - Supplements with 1-2 sentences from a second chunk if needed.
    """
    q_tokens = tokenize(question_text)
    q_tokens = remove_compartment_noise(q_tokens, question_text)
    intent = detect_intent(q_tokens, question_text)

    if intent.get("wants_mark_compare"):
        want_terms = MARK_COMPARE_SIGNAL_TERMS
    else:
        # Expand query terms with synonyms so sentence filtering can match
        # corpus vocabulary that differs from the user's phrasing
        # (e.g. "eat" matches "ate", "galley", "food" etc.)
        want_terms = expand_query_tokens([t for t in q_tokens if len(t) > 2])
    want_terms_l = [w.lower() for w in want_terms]

    def chunk_sentences(ch: Dict[str, Any]) -> List[str]:
        """Sentences in original order; leading FAQ question paragraph dropped.

        FAQ entries have the question as the first paragraph, separated by a
        blank line from the answer body.  Split on double-newlines first so
        abbreviations like 'U. S.' don't leave stray fragments behind.
        """
        text = (ch.get("text", "") or "").replace("\xa0", " ")
        # Drop the leading question / title paragraph (ends with '?')
        paragraphs = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        if paragraphs and paragraphs[0].rstrip().endswith("?"):
            text = "\n\n".join(paragraphs[1:])
        sents = split_sentences(text)
        return [s for s in sents if len(s.strip()) >= 3]

    used_sentences: List[str] = []
    citations: List[Dict[str, Any]] = []
    faq_question: Optional[str] = None
    faq_body: Optional[str] = None  # paragraph-structured body, set for FAQ chunks
    faq_chunk_id: Optional[str] = None  # e.g. "faq_591", returned to client for display

    # Primary chunk: sentences in original order, but for tour chunks
    # restrict to sentences containing at least one query term so a chunk
    # that only mentions "periscopes" in passing doesn't flood the answer
    # with unrelated content.  FAQ/shorts keep their full paragraph body.
    if hits:
        _, ch, source_id = hits[0]
        # For FAQ chunks: capture the question and build a paragraph-structured body
        if ch.get("doc_type") in ("dieselsubs_faq", "dieselsubs_shorts"):
            faq_chunk_id = ch.get("chunk_id") or None
            raw_text = (ch.get("text", "") or "").replace("\xa0", " ")
            raw_paragraphs = [p.strip() for p in re.split(r"\n\n+", raw_text) if p.strip()]
            if raw_paragraphs and raw_paragraphs[0].rstrip().endswith("?"):
                faq_question = raw_paragraphs[0].strip()
                answer_paragraphs = raw_paragraphs[1:]
            else:
                answer_paragraphs = raw_paragraphs
            # Build body: sentences within each paragraph joined by space,
            # paragraphs separated by \n\n
            # List paragraphs (numbered/bulleted) are preserved verbatim.
            def is_list_para(p: str) -> bool:
                lines = [l for l in p.splitlines() if l.strip()]
                if len(lines) < 2:
                    return False
                return (all(re.match(r"^\d+\.\s", l) for l in lines) or
                        all(l.startswith("•") for l in lines))

            # Detect ASCII-art / diagram paragraphs that are visual-only and
            # unreadable as audio.  Examples:
            #   [Engine] [Generator] ==> [Cubicle] ==> [Main Motors]
            #   A --> B --> C
            _DIAGRAM_RE = re.compile(
                r"(\[\w[\w\s]*\].*==>)"   # [Foo] ==> style
                r"|(==>|-->|\|\s*\||\+-+\+)"  # arrows / box-drawing
                r"|(^\s*\[[\w\s]+\](\s*\[[\w\s]+\])+\s*$)",  # only [Brack] tokens
                re.MULTILINE,
            )

            def is_diagram_para(p: str) -> bool:
                """True if the paragraph is an ASCII diagram, not speakable prose."""
                return bool(_DIAGRAM_RE.search(p))

            result_paras: List[str] = []
            for para in answer_paragraphs:
                # Skip un-speakable ASCII diagrams entirely
                if is_diagram_para(para):
                    continue
                if is_list_para(para):
                    result_paras.append(para.strip())
                    continue
                sents = [s for s in split_sentences(para) if len(s.strip()) >= 3]
                if not sents:
                    continue
                # Drop dangling header sentences (end with ':' and are the only
                # sentence in the paragraph — the body they introduced was removed)
                if len(sents) == 1 and sents[0].rstrip().endswith(":"):
                    continue
                result_paras.append(" ".join(sents))
            faq_body = "\n\n".join(result_paras).strip()
            sents = chunk_sentences(ch)
            used_sentences = sents
        else:
            # Tour / shorts chunk: only keep sentences that contain a query term.
            # This prevents a chunk that mentions a term in passing from flooding
            # the answer with off-topic content.
            sents = chunk_sentences(ch)
            if want_terms_l:
                filtered = [s for s in sents if any(w in s.lower() for w in want_terms_l)]
            else:
                filtered = sents
            used_sentences = filtered  # may be empty; secondary loop will supplement
        if used_sentences:
            citations.append({
                "source_id": source_id,
                "display_citation": ch.get("display_citation"),
                "chunk_id": ch.get("chunk_id"),
            })

    # Secondary chunk: supplement if primary is thin
    if len(used_sentences) < 3 and len(hits) > 1:
        seen_norm = {re.sub(r"\s+", " ", s.strip().lower()) for s in used_sentences}
        for _, ch2, src2 in hits[1:]:
            sents2 = chunk_sentences(ch2)
            new = [
                s for s in sents2
                if re.sub(r"\s+", " ", s.strip().lower()) not in seen_norm
                and any(w in s.lower() for w in want_terms_l)
            ]
            if new:
                used_sentences.extend(new)
                citations.append({
                    "source_id": src2,
                    "display_citation": ch2.get("display_citation"),
                    "chunk_id": ch2.get("chunk_id"),
                })
                break

    if not used_sentences:
        # fallback: try any hit that has sentences containing query terms,
        # preferring FAQ/shorts over tour for this last-resort path
        for _, ch_fb, src_fb in sorted(hits, key=lambda h: 0 if h[2] != "pampanito_tour" else 1):
            sents_fb = split_sentences(ch_fb.get("text", "") or "")
            rel = [s for s in sents_fb if any(w in s.lower() for w in want_terms_l)] if want_terms_l else sents_fb[:2]
            if rel:
                used_sentences = rel[:3]
                citations = [{
                    "source_id": src_fb,
                    "display_citation": ch_fb.get("display_citation"),
                    "chunk_id": ch_fb.get("chunk_id"),
                }]
                break
        # absolute last resort: first two sentences of the top chunk
        if not used_sentences:
            _, ch, source_id = hits[0]
            sents = split_sentences(ch.get("text", "") or "")
            used_sentences = sents[:2] if sents else ["(No text available in retrieved chunk.)"]
            citations = [{
                "source_id": source_id,
                "display_citation": ch.get("display_citation"),
                "chunk_id": ch.get("chunk_id"),
            }]

    if faq_question and faq_body is not None:
        answer_short = faq_question + "\n\n" + faq_body
    else:
        answer_short = " ".join(used_sentences).strip()

    # For answers sourced from the audio tour, prepend a human-readable source line.
    # Deck stops (fore/aft): "From the audio in the After Deck"
    # Interior compartments : "From the audio in the Conning Tower compartment"
    # Use citations[0] (the chunk whose text was actually used), not hits[0].
    if citations and answer_short and citations[0].get("source_id") == "pampanito_tour":
        # Find the matching chunk to get location_context
        used_chunk_id = citations[0].get("chunk_id")
        tour_ch = next((c for c in TOUR if c.get("chunk_id") == used_chunk_id), None)
        if tour_ch:
            stop_loc = (tour_ch.get("location_context") or "").strip()
            if stop_loc:

                    answer_short = f"From the audio tour in {stop_loc}\n\n{answer_short}"
    if intent.get("is_where_question") and hits and answer_short:
        top_ch = hits[0][1]
        loc = (top_ch.get("location_context") or "").strip()
        # Only prepend if the answer actually came from a tour chunk and the location
        # name isn't already present near the top of the answer (e.g. from the audio prefix).
        if loc and citations and citations[0].get("source_id") == "pampanito_tour" and loc.lower() not in answer_short[:120].lower():
            answer_short = f"In the {loc}. " + answer_short

    # ── Audio-safety pass ────────────────────────────────────────────────────
    # Strip any diagram lines, ASCII-art, and orphaned colon-headers that
    # may have leaked through from long FAQ chunks.  Applied per-line so we
    # don't accidentally drop valid prose containing an arrow in a sentence.
    _DIAGRAM_LINE_RE = re.compile(
        r"==>|-->"                        # arrow diagrams
        r"|\[[A-Z][\w\s]{0,20}\].*\["    # [Foo] ... [Bar] bracket chains
        r"|^\s*[|+][-+|]+[|+]\s*$"       # box-drawing lines
        r"|^Note\s*:",                    # "NOTE :" headers from FAQ
        re.IGNORECASE,
    )

    def clean_for_audio(text: str) -> str:
        """Remove lines that are diagrams, ASCII art, or dangling colon-headers."""
        out_paras: List[str] = []
        for para in re.split(r"\n\n+", text):
            out_lines: List[str] = []
            for line in para.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                # Drop diagram / ASCII-art lines
                if _DIAGRAM_LINE_RE.search(stripped):
                    continue
                # Drop orphaned paragraph-header lines (end with ':',
                # contain no full sentence, and are the only line)
                out_lines.append(line)
            # After filtering, drop the paragraph if its only remaining content
            # is a dangling header (single short line ending with ':')
            if len(out_lines) == 1 and out_lines[0].rstrip().endswith(":"):
                continue
            joined = "\n".join(out_lines).strip()
            if joined:
                out_paras.append(joined)
        return "\n\n".join(out_paras)

    answer_short = clean_for_audio(answer_short)

    # Remove spoken filler words that appear in oral-history transcripts.
    # Patterns handled:
    #   "uh,"  "uh."  "uh "      → dropped with surrounding punctuation/space
    #   ", uh,"  ", uh "         → comma cleaned up
    #   "I, uh, said"            → "I said"
    def clean_speech_fillers(text: str) -> str:
        # Fillers surrounded by commas:  ", uh,"  → ","
        text = re.sub(r",\s*\b(uh|um|er|ah|uhh|umm)\b\s*,", ",", text, flags=re.I)
        # Filler at start of sentence or after comma with trailing comma/space
        text = re.sub(r"(?<![a-z])\b(uh|um|er|ah|uhh|umm)\b[,\s]+", " ", text, flags=re.I)
        # Filler at end before punctuation
        text = re.sub(r",?\s*\b(uh|um|er|ah|uhh|umm)\b\s*(?=[.!?])", "", text, flags=re.I)
        # Dangling leading comma after removal:  ", said" → " said"
        text = re.sub(r"\s*,\s*,", ",", text)
        # Clean up extra spaces
        text = re.sub(r"  +", " ", text)
        return text.strip()

    answer_short = clean_speech_fillers(answer_short)

    # For "why" questions: if the answer contains none of the causal markers
    # that would indicate an actual explanation, the retrieved content is off-topic.
    # Return a refusal rather than a misleading answer.
    CAUSAL_MARKERS = [
        "because", "reason", "reasons", "in order to", "caused", "cause",
        "due to", "led to", "motivated", "motive", "objective", "strategy",
        "provoked", "prompted", "intent", "intended", "wanted to", "sought",
        "goal", "aim", "embargo", "retaliation", "threat", "feared",
    ]
    if intent.get("is_why_question"):
        answer_lower = answer_short.lower()
        has_causal = any(m in answer_lower for m in CAUSAL_MARKERS)
        if not has_causal:
            # The top-ranked chunk doesn't answer the "why". Scan remaining
            # hits for any chunk whose text contains causal language and
            # rebuild the answer from that instead of returning a refusal.
            rebuilt = False
            for _, ch_why, src_why in hits:
                text_why = (ch_why.get("text", "") or "").lower()
                if any(m in text_why for m in CAUSAL_MARKERS):
                    # Found a causal chunk — synthesise from it directly.
                    raw_text = (ch_why.get("text", "") or "").replace("\xa0", " ")
                    raw_paras = [p.strip() for p in re.split(r"\n\n+", raw_text) if p.strip()]
                    if raw_paras and raw_paras[0].rstrip().endswith("?"):
                        faq_question = raw_paras[0].strip()
                        body_paras = raw_paras[1:]
                    else:
                        faq_question = None
                        body_paras = raw_paras
                    body = "\n\n".join(p.strip() for p in body_paras if p.strip())
                    if faq_question:
                        answer_short = faq_question + "\n\n" + body
                    else:
                        answer_short = body
                    citations = [{
                        "source_id": src_why,
                        "display_citation": ch_why.get("display_citation"),
                        "chunk_id": ch_why.get("chunk_id"),
                    }]
                    rebuilt = True
                    break
            if not rebuilt:
                return {
                    "answer_mode": "standard",
                    "answer_short": "I don't have that detail in the Pampanito audio tour or the DieselSubs reference material I'm using.",
                    "partial_match": False,
                    "answer_deep": None,
                    "what_you_are_seeing": None,
                    "citations": [],
                    "followups": [
                        "Are you asking about something specific to Pampanito or the Pacific submarine war?",
                        "Want to know what role Pampanito played after Pearl Harbor?",
                    ],
                    "refusal": {"is_refusal": True, "reason": "no_source"},
                }

    # Detect partial match:
    # 1. None of the subject query terms appear in the final answer, OR
    # 2. It was a quantity question ("how many X") but no sentence that
    #    contains the *counted noun* also contains a number/quantity word.
    NUMBER_WORDS = re.compile(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten"
        r"|eleven|twelve|dozen|several|numerous|multiple)\b", re.I
    )

    def answer_has_quantity_for_subject(text: str, count_subject: List[str]) -> bool:
        """True if any sentence contains both a count-subject term and a number."""
        if not count_subject:
            return bool(NUMBER_WORDS.search(text))
        for sent in split_sentences(text):
            sl = sent.lower()
            if any(w in sl for w in count_subject) and NUMBER_WORDS.search(sl):
                return True
        return False

    # Extract the noun being counted from the raw question:
    # e.g. "how many bunks are there" → ["bunks"]
    # Only grab the first 1-2 words after "how many" to avoid absorbing
    # location phrases like "in after torpedo room" as the subject.
    count_subject: List[str] = []
    qty_match = re.search(r"how\s+many\s+(\w+(?:\s+\w+)?)", question_text.lower())
    if qty_match:
        candidate_toks = [t for t in tokenize(qty_match.group(1)) if len(t) > 2]
        # Drop location/directional words that would pollute quantity checking
        LOCATION_WORDS = {"after", "forward", "room", "compartment", "area", "section"}
        count_subject = [t for t in candidate_toks if t not in LOCATION_WORDS]

    # Detect evaluative/superlative questions: "worst X", "best X", "hardest X", etc.
    # If the question asks for a judgment but the answer doesn't address it, flag partial.
    SUPERLATIVE_RE = re.compile(
        r"\b(worst|best|hardest|easiest|longest|shortest|hottest|coldest"
        r"|most\s+\w+|least\s+\w+|most|least|farthest|nearest|highest|lowest"
        r"|biggest|smallest|largest|toughest|roughest|worst.case)\b",
        re.I
    )
    superlatives_in_q = SUPERLATIVE_RE.findall(question_text.lower())
    answer_missing_superlative = bool(superlatives_in_q) and not any(
        s.strip() in answer_short.lower() for s in superlatives_in_q
    )

    partial_match = (
        (bool(want_terms_l) and not any(w in answer_short.lower() for w in want_terms_l))
        or (
            intent.get("wants_quantity")
            and not answer_has_quantity_for_subject(answer_short, count_subject or [w for w in want_terms_l if w not in {"many", "much", "count"}])
        )
        or answer_missing_superlative
    )

    return {
        "answer_mode": "standard",
        "answer_short": answer_short,
        "partial_match": partial_match,
        "faq_id": faq_chunk_id,
        "answer_deep": None,
        "what_you_are_seeing": None,
        "citations": citations[:2],
        "followups": [
            "Want the quick version or the deeper docent version?",
            "Want me to point out what to look for in this compartment?"
        ],
        "refusal": {"is_refusal": False, "reason": None},
    }

def synthesize_openai_stub(
    question_text: str,
    hits: List[Hit],
    compartment_id: str,
    playhead_time_ms: int
) -> Dict[str, Any]:
    """
    Stub for later OpenAI API integration.
    Keeping this function in place now means you can “drop in” funding later
    without restructuring your app.

    For now, this clearly reports that LLM is disabled and falls back to extractive.
    """
    # If someone accidentally turned USE_LLM on without wiring credentials/code:
    # fall back safely.
    base = synthesize_extractive(question_text, hits)
    base["followups"] = [
        "LLM synthesis is not enabled in this demo build.",
        "Want the extractive answer (from sources) or a deeper docent version later?"
    ]
    return base


# ------------------------------------------------------------
# Feedback endpoint
# ------------------------------------------------------------

FEEDBACK_PATH = os.path.join(BASE_DIR, "feedback.jsonl")

@app.post("/feedback")
def receive_feedback(payload: dict):
    import datetime
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "question": (payload.get("question") or "").strip(),
        "answer": (payload.get("answer") or "").strip(),
        "rating": payload.get("rating"),          # "up" | "down" | null
        "comment": (payload.get("comment") or "").strip(),
    }
    try:
        with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[feedback] write error: {e}")
    print(f"[feedback] {entry['rating']} — {entry['question'][:80]}")
    return {"status": "ok"}


@app.get("/feedback/list")
def list_feedback():
    """Return all feedback entries, newest first. Admin use only."""
    if not os.path.exists(FEEDBACK_PATH):
        return []
    entries = []
    with open(FEEDBACK_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except Exception:
                    pass
    entries.reverse()
    return entries


# ------------------------------------------------------------
# API endpoint
# ------------------------------------------------------------

@app.post("/ask")
def ask(payload: dict):
    question = (payload.get("question_text") or "").strip()
    compartment = (payload.get("compartment_id") or "").strip()
    playhead_time_ms = int(payload.get("playhead_time_ms") or 0)

    hits = retrieve(
        question_text=question,
        compartment_id=compartment,
        playhead_time_ms=playhead_time_ms,
        top_k=8
    )

    if not hits:
        return {
            "answer_mode": payload.get("answer_mode", "standard") or "standard",
            "answer_short": "I don’t have that detail in the Pampanito audio tour or the DieselSubs reference material I’m using.",
            "answer_deep": None,
            "what_you_are_seeing": None,
            "citations": [],
            "followups": [
                "Which compartment are you in (or which tour section are you listening to)?",
                "Are you asking about Pampanito specifically, or WWII fleet submarines in general?"
            ],
            "refusal": {"is_refusal": True, "reason": "no_source"},
        }

    if USE_LLM:
        # Later: replace synthesize_openai_stub with a real OpenAI call.
        return synthesize_openai_stub(
            question_text=question,
            hits=hits,
            compartment_id=compartment,
            playhead_time_ms=playhead_time_ms
        )

    return synthesize_extractive(question_text=question, hits=hits)