from __future__ import annotations
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import io
import json
import os
import re
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Tuple, Any, Optional

app = FastAPI(title="SubmarineDocent")

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
def root_redirect(request: Request):
    from fastapi.responses import RedirectResponse
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    if host.startswith("pampanito."):
        return RedirectResponse(url="/web/pampanito.html")
    return RedirectResponse(url="/web/faqs.html")

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

    # Convenience redirect: /review.html → /web/review.html
    @app.get("/review.html", include_in_schema=False)
    def redirect_review_html():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/review.html")

    # Convenience redirect: /faq_editor.html → /web/faq_editor.html
    @app.get("/faq_editor.html", include_in_schema=False)
    def redirect_faq_editor_html():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/faq_editor.html")

    # Public FAQ page shortcuts
    @app.get("/faqs", include_in_schema=False)
    @app.get("/faqs.html", include_in_schema=False)
    @app.get("/faq", include_in_schema=False)
    def redirect_faqs_html():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/faqs.html")

    @app.get("/index.html", include_in_schema=False)
    @app.get("/web/index.html", include_in_schema=False)
    def redirect_index_html():
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/web/faqs.html")

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
SHORTS_PATH = os.path.join(CORPORA_DIR, "dieselsubs_shorts_corpus.jsonl")

# FAQ corpus — use Render persistent disk (/data) if mounted, else local corpora/
_BUNDLED_FAQ_PATH = os.path.join(CORPORA_DIR, "dieselsubs_faq_corpus.jsonl")
_RENDER_DATA_DIR = "/data"
if os.path.isdir(_RENDER_DATA_DIR):
    FAQ_PATH = os.path.join(_RENDER_DATA_DIR, "dieselsubs_faq_corpus.jsonl")
    if not os.path.exists(FAQ_PATH) and os.path.exists(_BUNDLED_FAQ_PATH):
        import shutil
        shutil.copy2(_BUNDLED_FAQ_PATH, FAQ_PATH)
        print(f"✅ Seeded persistent disk FAQ corpus from bundled copy")
else:
    FAQ_PATH = _BUNDLED_FAQ_PATH


# Path for incidents corpus
INCIDENTS_PATH = os.path.join(CORPORA_DIR, "incidents.jsonl")

# Feature flag: keep demo fully local today; later, flip to true with funding.
USE_LLM = os.getenv("USE_LLM", "false").lower() in ("1", "true", "yes")
def load_incidents():
    """Load incidents corpus from JSONL file."""
    if not os.path.exists(INCIDENTS_PATH):
        print(f"❌ File not found: {INCIDENTS_PATH}")
        return []
    data = []
    with open(INCIDENTS_PATH, "r", encoding="utf-8-sig") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except Exception as e:
                print(f"⚠️ JSON parse error on line {i} in {INCIDENTS_PATH}: {e}")
                break
    print(f"✅ Loaded {len(data)} records from {os.path.basename(INCIDENTS_PATH)}")
    return data

# Load incidents corpus at startup
INCIDENTS = load_incidents()
# ------------------------------------------------------------
# Incidents API endpoint
# ------------------------------------------------------------

@app.get("/api/incidents")
def get_incidents():
    """Return all submarine incidents."""
    return {"incidents": INCIDENTS}

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
    # common filler words that appear everywhere and create false score matches
    "any", "there", "than", "other",
    # question / wh- words that carry no domain meaning on their own
    # NOTE: "why" is intentionally NOT here — it drives is_why_question intent detection
    "where", "how", "when", "who", "which", "whose", "whom",
    # directional/location words too common on a submarine to be useful signals
    "after", "forward",
    # context-universal words: every chunk is about a submarine/boat
    "submarine", "boat", "sub",
    # ultra-generic verbs / pronouns with no domain signal
    "got", "get", "gets", "gotten",
    # prepositions with no domain meaning
    "into", "onto", "upon", "within", "without", "through", "throughout",
    # NOTE: "happened" / "happen" intentionally NOT here — they disambiguate
    # "what happened to X?" questions from generic "where is X?" questions.
    "someone", "something", "somebody", "anyone", "anything",
    "people", "person", "things", "thing",
    # generic auxiliary / modal verbs with no domain signal
    "could", "would", "should", "had", "have", "has", "if", "its", "been",
    # all content is WWII-era so these words match everything equally
    "world", "war", "ii",
}


def tokenize(text: str) -> List[str]:
    text = (text or "").lower()
    # Preserve known hyphenated terms before stripping punctuation
    text = re.sub(r"\bv-mail\b", "vmail", text)
    text = re.sub(r"\bjn-25\b", "jn25", text)
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
    """Return the corpus compartment_id named in the query, or None.
    If multiple compartments are mentioned (comparison query), return None
    so the boost isn't applied unfairly to one side."""
    matches = [cid for pattern, cid in _COMPARTMENT_QUERY_MAP if pattern.search(raw_query)]
    if len(matches) == 1:
        return matches[0]
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
    "gun":    ["guns", "deck gun", "cannon", "weapon", "weapons", "armament", "5 inch", "4 inch", "gun action"],
    "shoot":  ["fire", "fired", "firing", "launch", "launched", "torpedo", "attack"],
    "dive":   ["dived", "diving", "submerge", "submerged", "submerging", "crash dive"],
    "speed":  ["knots", "fast", "faster", "slow", "slower", "velocity"],
    "fast":   ["speed", "knots", "faster", "velocity", "slow", "slower"],
    "faster": ["fast", "speed", "knots", "velocity"],
    "engine": ["engines", "motor", "motors", "diesel", "electric", "power", "drive"],
    # crew-size questions: "men" and "served" should find crew/complement content
    "men":    ["crew", "sailors", "crewmen", "enlisted", "personnel", "complement"],
    "served": ["crew", "crewmen", "complement", "enlisted", "assigned"],
    "crew":   ["men", "sailors", "crewmen", "complement", "personnel", "enlisted"],
    "crews":  ["crew", "men", "sailors", "crewmen", "complement", "personnel", "enlisted"],
    # medical
    "doctors": ["doctor", "medical", "pharmacist", "corpsman", "medic", "physician"],
    "doctor":  ["doctors", "medical", "pharmacist", "corpsman", "medic", "physician", "health", "sick", "ill", "medicine"],
    "medical": ["doctor", "doctors", "pharmacist", "corpsman", "medic", "hospital", "health", "sick", "ill", "medicine", "injury"],
    # supply / resupply
    "resupplied": ["resupply", "supply", "supplies", "fuel", "reloaded", "restock", "tender", "tenders"],
    "resupply":   ["resupplied", "supply", "supplies", "fuel", "restock", "tender", "tenders"],
    "tender":     ["tenders", "support ship", "resupply", "supply", "base", "flotilla", "fulton", "sperry", "depot"],
    "tenders":    ["tender", "support ship", "resupply", "supply", "base", "fulton", "sperry"],
    # radar (distinct from sonar — different technology)
    "radar":  ["sj", "sd", "surface search", "air search", "detection", "sensors", "electronic", "radio", "contact", "pip", "scan"],
    # decommission
    "decommissioned":   ["decommissioning", "decommission", "retired", "mothballed", "inactive"],
    "decommissioning":  ["decommissioned", "decommission", "retired", "mothballed"],
    # museum / preservation
    "preserved":  ["preservation", "restore", "restored", "maintain", "museum"],
    "museum":     ["preserved", "preservation", "historic", "landmark", "exhibit"],
    # war contribution / strategy
    "strategy":   ["strategic", "campaign", "plan", "mission", "objective", "tactics"],
    "contribute": ["contributed", "contribution", "role", "impact", "win", "winning"],
    "won":    ["win", "winning", "victory", "defeat", "outcome"],
    # illness / medical questions
    "sick":    ["ill", "illness", "health", "doctor", "pharmacist", "medical", "medicine", "injury", "injured", "wound", "wounded", "hurt"],
    "ill":     ["sick", "illness", "health", "doctor", "pharmacist", "medical"],
    "hurt":    ["injured", "injury", "wound", "wounded", "sick", "ill", "medical"],
    # computer / fire control questions → TDC in conning tower
    "computer":  ["torpedo data computer", "tdc", "fire control", "targeting", "conning tower", "periscope", "attack"],
    "computers": ["torpedo data computer", "tdc", "fire control", "targeting", "conning tower"],
    "tdc":       ["torpedo data computer", "computer", "fire control", "targeting", "attack"],
    # plural/singular bridging
    "rooms":  ["room"],
    "room":   ["rooms"],
    # sleeping / berthing — physical berthing terms only; do NOT include sleep/slept
    # which over-matches tour chunks about the sleeping *experience* (e.g. "I slept
    # in the aft torpedo room") when the visitor is asking about the physical bunks.
    "bunks":  ["bunk", "bed", "beds", "rack", "racks", "berthing"],
    "bunk":   ["bunks", "bed", "beds", "rack", "racks", "berthing"],
    # "banks" is a common STT mishearing of "bunks" (also handled client-side)
    "banks":  ["bunks", "bunk", "bed", "beds", "rack", "racks", "berthing"],
    # crew quality / selection questions
    "smarter":  ["intelligent", "qualified", "trained", "selected", "better", "volunteers"],
    "sailors":  ["submariners", "crewmen", "crew", "enlisted", "men", "personnel"],
    "submariners": ["sailors", "crewmen", "crew", "enlisted", "men", "personnel"],
    # submerged / underwater propulsion vocabulary
    "underwater": ["submerged", "submerge", "dived", "diving", "dive", "battery", "batteries"],
    "submerged":  ["underwater", "dived", "diving", "dive", "battery", "batteries"],
    "needed":     ["need", "needs", "require", "required", "requires", "uses", "use"],
    "need":       ["needed", "needs", "require", "required", "requires"],
    # torpedo reload vocabulary
    "reloads":   ["reload", "reloading", "reloaded", "loading", "loaded", "skid", "skids"],
    "reload":    ["reloads", "reloading", "reloaded", "loading", "loaded", "skid", "skids", "tube", "tubes", "torpedo"],
    "reloading": ["reload", "reloads", "reloaded", "loading", "loaded", "skid", "skids"],
    "handled":   ["loaded", "done", "managed", "moved", "operated", "worked"],
    # food storage vocabulary
    "stored":    ["stowed", "stow", "storage", "kept", "loaded", "provisions", "provisioned"],
    "stowed":    ["stored", "storage", "stow", "kept", "provisions"],
    "kept":      ["stored", "stowed", "storage", "stow", "provisions"],
    "provisions":["food", "stores", "stored", "stowed", "supply", "supplies"],
    # torpedo singular/plural pairing
    "torpedo":   ["torpedoes", "fired", "launched", "shot", "warhead"],
    "torpedoes": ["torpedo", "fired", "launched", "shot", "warhead"],
    # underwater communication vocabulary — merged entry (see also batch-10 radio/telephone synonyms)
    "communication": ["communicate", "radio", "transmit", "message", "signal", "contact"],
    # Speech-to-text substitutions: common mis-transcriptions mapped to intended words
    # "controls" → "patrols" is a very common STT error (same syllable pattern)
    "controls":  ["patrols", "patrol", "war patrol", "missions", "mission", "voyages"],
    # "complete" / "completed" used when asking about patrols Pampanito finished
    "complete":  ["completed", "conducted", "finished", "ran", "made", "patrols"],
    # "afterdeck" (one word) ↔ "after deck" (two words) — both forms used by visitors
    "afterdeck": ["after deck", "deck", "gun", "deck gun", "aft", "after"],
    "foredeck":  ["forward deck", "deck", "gun", "deck gun", "forward"],
    # lifeguard mission / downed pilots rescue
    "lifeguard": ["rescue", "downed", "pilots", "airmen", "aviators"],
    "airmen":    ["lifeguard", "pilots", "aviators", "downed", "rescue"],
    "pilots":    ["airmen", "lifeguard", "aviators", "downed", "rescue", "aircraft"],
    "downed":    ["lifeguard", "airmen", "pilots", "aviators", "rescue"],
    # mine-laying
    "mines":       ["mine", "minelaying", "lay", "laying"],
    "mine":        ["mines", "minelaying", "lay", "laying"],
    "minelaying":  ["mines", "mine", "lay", "laying"],
    # wolfpack / coordinated attack
    "wolfpack":  ["wolf", "pack", "coordinated", "tactics", "packs"],
    "wolfpacks": ["wolfpack", "wolf", "pack", "coordinated", "tactics"],
    "wolf":      ["wolfpack", "wolfpacks", "pack", "coordinated"],
    # convoy / merchant shipping
    "convoy":   ["convoys", "merchant", "shipping", "transports", "fleet"],
    "convoys":  ["convoy", "merchant", "shipping", "transports", "fleet"],
    # aircraft threat
    "aircraft":  ["plane", "planes", "airplane", "airplanes", "patrol"],
    "airplane":  ["aircraft", "plane", "planes", "airplanes"],
    "planes":    ["aircraft", "airplane", "airplanes", "plane"],
    "plane":     ["aircraft", "airplane", "airplanes", "planes"],
    # seasickness
    "seasick":    ["seasickness", "sick", "nauseous", "motion", "vomit"],
    "seasickness":["seasick", "sick", "nauseous", "motion"],
    "nauseous":   ["seasick", "seasickness", "sick", "motion"],
    # claustrophobia
    "claustrophobia":  ["confined", "enclosed", "tight", "crowded", "phobia"],
    "claustrophobic":  ["claustrophobia", "confined", "enclosed", "tight"],
    "confined":        ["claustrophobia", "claustrophobic", "enclosed", "tight"],
    # warship / naval vessel types
    "warship":   ["warships", "destroyer", "cruiser", "naval", "vessel"],
    "warships":  ["warship", "destroyer", "cruiser", "naval", "vessels"],
    "destroyer": ["warship", "warships", "escort", "destroyer escort"],
    # galley / kitchen
    "galley":  ["kitchen", "cook", "cooks", "cooking", "chow", "mess"],
    "kitchen": ["galley", "cook", "cooks", "cooking", "chow", "food"],
    # snorkel (pam_175)
    "snorkel":  ["breathe", "air", "diesel", "mast", "snorkeling", "snort"],
    "snorkeling": ["snorkel", "snort", "diesel", "surface", "recharge"],
    "snort":    ["snorkel", "snorkeling", "diesel", "recharge"],
    # control room (pam_156)
    "christmas":  ["tree", "green board", "board", "dials", "diving", "control"],
    "green":      ["board", "christmas", "tree", "light", "dive", "safe"],
    # garbage / trash disposal (pam_158)
    "garbage":   ["trash", "waste", "disposal", "dispose", "gdu", "discard"],
    "trash":     ["garbage", "waste", "disposal", "dispose", "gdu"],
    "disposal":  ["garbage", "trash", "waste", "dispose", "gdu"],
    "dispose":   ["garbage", "trash", "waste", "disposal", "gdu"],
    # enemy survivors (pam_159)
    "survivors": ["survivor", "rescued", "rescue", "enemy", "prisoner"],
    "survivor":  ["survivors", "rescued", "rescue", "enemy", "prisoner"],
    # fires / flooding (pam_160)
    "fire":      ["fires", "flooding", "flood", "emergency", "emergency procedures", "danger"],
    "fires":     ["fire", "flooding", "flood", "emergency"],
    "flooding":  ["flood", "fire", "fires", "emergency", "leak", "leaking", "tube", "tubes", "outer", "door", "breech", "torpedo", "launch"],
    "flood":     ["flooding", "fire", "fires", "emergency", "leak", "ballast", "tank", "tanks", "dive", "submerge"],
    "emergency": ["fire", "fires", "flooding", "flood", "aground", "danger", "crash"],
    "leak":      ["flooding", "flood", "fire", "damage", "hull"],
    # periscope feather (pam_161)
    "feather":   ["periscope", "wake", "spray", "surface", "visible", "scope"],
    "wake":      ["feather", "periscope", "surface", "visible", "wave"],
    # boredom / morale (pam_162)
    "boredom":   ["boring", "morale", "entertainment", "recreation", "pass time"],
    "boring":    ["boredom", "morale", "entertainment", "recreation"],
    "morale":    ["boredom", "boring", "entertainment", "recreation", "crew"],
    "entertainment": ["boredom", "boring", "morale", "recreation", "games"],
    "recreation":    ["boredom", "boring", "morale", "entertainment", "games"],
    # grounded / aground (pam_164)
    "aground":   ["grounded", "ground", "shoal", "shallow", "stuck"],
    "grounded":  ["aground", "ground", "shoal", "shallow", "stuck"],
    # battle stars (pam_166)
    "stars":     ["battle", "star", "award", "awarded", "recognition", "credit"],
    "star":      ["battle", "stars", "award", "awarded"],
    # flying bridge (pam_167)
    "bridge":    ["flying", "conn", "surface", "watch", "lookout", "top"],
    "flying":    ["bridge", "conn", "top", "platform"],
    # deep / dive depth (pam_168)
    "deep":      ["depth", "feet", "test", "dive", "diving", "crush", "hull"],
    "depth":     ["deep", "feet", "test", "dive", "underwater", "running", "problem", "failure"],
    "feet":      ["deep", "depth", "test", "400", "300"],
    # magnetic exploder / dud torpedoes (pam_169)
    "magnetic":  ["exploder", "exploders", "dud", "duds", "torpedo", "fail"],
    "exploder":  ["magnetic", "exploders", "dud", "duds", "torpedo", "fail"],
    "exploders": ["magnetic", "exploder", "dud", "duds", "torpedo"],
    "dud":       ["duds", "magnetic", "exploder", "torpedo", "malfunction", "failed"],
    "duds":      ["dud", "magnetic", "exploder", "torpedo", "malfunction"],
    # celebrate / victory (pam_171)
    "celebrate": ["celebration", "celebrating", "victory", "attack", "successful", "after"],
    "celebration": ["celebrate", "celebrating", "victory", "attack"],
    "victory":   ["celebrate", "celebration", "successful", "won", "win", "vmail", "microfilm", "mail"],
    # return to port / liberty (pam_172)
    "liberty":   ["port", "leave", "rest", "r&r", "shore", "hawaii", "pearl"],
    "leave":     ["liberty", "port", "rest", "r&r", "shore"],
    "r&r":       ["liberty", "leave", "rest", "port"],
    "returned":  ["return", "port", "liberty", "leave", "patrol"],
    "return":    ["returned", "port", "liberty", "leave", "patrol"],
    # Silent Service / nickname (pam_173)
    "silent":    ["service", "nickname", "secretive", "secret", "quiet"],
    "nickname":  ["silent", "service", "called", "known as", "name"],
    # ace / best commander (pam_170)
    "ace":       ["best", "top", "successful", "commander", "captain", "score"],
    "best":      ["top", "ace", "successful", "most", "commander", "captain"],
    "top":       ["best", "ace", "successful", "most", "commander"],
    # periscope depth (pam_176)
    "periscope": ["scope", "lens", "look", "observation", "conning", "tower"],
    # construction / building (pam_174)
    "construction": ["build", "built", "building", "shipyard", "keel", "launch"],
    "shipyard":     ["build", "built", "construction", "built", "keel"],
    "keel":         ["shipyard", "construction", "built", "build", "launch"],
    # qualification / dolphins / insignia (pam_136, pam_137)
    "qualified":   ["qualification", "qualify", "dolphins", "pin", "insignia", "certified", "certification"],
    "qualify":     ["qualified", "qualification", "dolphins", "pin", "insignia"],
    "dolphins":    ["qualified", "qualification", "insignia", "pin", "badge", "warfare"],
    "insignia":    ["dolphins", "qualified", "pin", "badge", "warfare", "qualification"],
    "badge":       ["insignia", "dolphins", "pin", "qualified"],
    "certification": ["qualified", "qualify", "qualification", "insignia"],
    # executive officer / XO (pam_139)
    "executive":   ["xo", "exec", "officer", "second", "command"],
    "xo":          ["executive", "exec", "officer", "second", "command"],
    "exec":        ["executive", "xo", "officer", "second"],
    # battle stations / general quarters (pam_140)
    "battle":      ["stations", "general quarters", "gq", "combat", "quarters", "manned"],
    "stations":    ["battle", "station", "general quarters", "gq", "quarters"],
    "quarters":    ["battle stations", "general quarters", "station", "gq"],
    # pharmacist / corpsman — extend existing entries
    "pharmacist":  ["corpsman", "medic", "medical", "doctor", "mate", "surgeon"],
    "corpsman":    ["pharmacist", "medic", "medical", "doctor", "mate"],
    "mate":        ["pharmacist", "corpsman", "medic"],
    # ballast / buoyancy / diving (pam_143)
    "ballast":     ["tank", "tanks", "dive", "diving", "submerge", "flood", "blow", "buoyancy"],
    "buoyancy":    ["ballast", "tank", "tanks", "float", "dive", "submerge"],
    "blow":        ["ballast", "tank", "tanks", "surface", "surfaced"],
    # fleet boat / fleet submarine (pam_146)
    "fleet":       ["boat", "submarine", "class", "type", "design"],
    # patrol report / after-action (pam_144)
    "report":      ["reports", "patrol report", "log", "logs", "record", "records", "documented"],
    "reports":     ["report", "patrol report", "log", "logs", "record"],
    # Gato / Balao / class differences (pam_148)
    "gato":        ["balao", "class", "submarine", "design", "type"],
    "balao":       ["gato", "class", "submarine", "design", "type", "depth"],
    "class":       ["gato", "balao", "tench", "type", "design", "difference"],
    "difference":  ["class", "compare", "compared", "versus", "vs", "unlike", "control room", "conning", "tower"],
    "versus":      ["difference", "vs", "compare", "compared", "unlike", "control room", "conning", "tower"],
    "vs":          ["versus", "difference", "compare", "compared"],
    # died / killed (pam_154 / pam_056)
    "died":        ["killed", "death", "dead", "die", "lost", "casualties"],
    "die":         ["died", "killed", "death", "dead", "casualties"],
    "killed":      ["died", "death", "dead", "die", "lost", "casualties"],
    "death":       ["died", "killed", "dead", "die", "casualties"],
    # orders / patrol assignments (pam_155 / pam_096)
    # One-directional: "orders" finds pam_096 ("assignments"); but "assignments"
    # already finds pam_096 directly — don't let it also expand to "orders" (pam_155)
    "orders":      ["assignments", "assigned", "mission", "directed", "patrol"],
    "assigned":    ["orders", "mission", "directed"],
    # recharge / battery (pam_147)
    "recharge":    ["recharging", "recharged", "charge", "charging", "battery", "batteries"],
    "recharging":  ["recharge", "recharged", "charge", "charging", "battery", "batteries"],
    "batteries":   ["battery", "recharge", "recharging", "charge", "power", "electric"],
    "battery":     ["batteries", "recharge", "recharging", "charge", "power", "electric", "forward battery", "cells", "lead-acid"],
    # destroyer / tin can threat (pam_150)
    "destroyers":  ["destroyer", "escort", "escorts", "tin", "threat", "anti-submarine", "asw"],
    "tin":         ["destroyer", "destroyers", "can", "escort", "asw"],
    "escort":      ["destroyer", "destroyers", "escorts", "anti-submarine", "asw"],
    "escorts":     ["destroyer", "destroyers", "escort", "anti-submarine", "asw"],
    # daily / duties (pam_149)
    "daily":       ["duties", "day", "routine", "typical", "schedule", "work"],
    "duties":      ["daily", "job", "tasks", "role", "responsibility", "routine"],
    "routine":     ["daily", "duties", "day", "schedule", "typical"],
    # commissioning (pam_152)
    "commissioning": ["commissioned", "ceremony", "day", "placed", "service"],
    "commissioned":  ["commissioning", "ceremony", "day", "placed", "service"],
    # sound / noise (pam_151)
    "sound":   ["sounds", "hear", "heard", "noise", "loud", "bang", "explosion"],
    "sounds":  ["sound", "hear", "heard", "noise", "loud", "bang"],
    "hear":    ["sound", "sounds", "heard", "noise", "loud"],
    "heard":   ["sound", "sounds", "hear", "noise", "bang"],
    "noise":   ["sound", "sounds", "hear", "heard", "loud", "bang", "explosion"],
    "loud":    ["sound", "noise", "hear", "heard", "bang", "explosion"],
    "bang":    ["sound", "noise", "explosion", "heard", "loud"],
    # POW rescue vocabulary (pam_138)
    "rescue":  ["rescued", "rescuing", "save", "saved", "survivor", "survivors", "pow", "prisoner"],
    "rescued": ["rescue", "rescuing", "save", "saved", "survivor", "survivors", "pow"],
    "prisoner":["prisoners", "pow", "pows", "captive", "captives", "rescued", "rescue"],
    "prisoners":["prisoner", "pow", "pows", "captive", "captives", "rescued"],
    "pow":     ["prisoner", "prisoners", "captive", "captives", "rescued", "rescue"],
    "pows":    ["prisoner", "prisoners", "pow", "captive", "captives", "rescued"],
    # wear / clothing (pam_135)
    "wore":    ["wear", "wearing", "worn", "clothes", "clothing", "uniform", "uniforms"],
    "wear":    ["wore", "wearing", "worn", "clothes", "clothing", "uniform", "uniforms"],
    "wearing": ["wear", "wore", "worn", "clothes", "clothing", "uniform"],
    "clothes": ["clothing", "uniform", "uniforms", "wore", "wear", "wearing"],
    "clothing":["clothes", "uniform", "uniforms", "wore", "wear", "wearing", "dress"],
    "uniform": ["uniforms", "clothes", "clothing", "wore", "wear", "dress"],
    "uniforms":["uniform", "clothes", "clothing", "wore", "wear", "dress"],
    # OOD / officer of the deck (pam_177)
    "ood":       ["deck", "deck watch", "officer", "watch", "conn", "conning", "underway"],
    "conn":      ["ood", "deck", "officer", "watch", "conning", "bridge"],
    # conning tower (pam_178)
    "conning":   ["tower", "conn", "periscope", "helm", "tdc", "fairwater", "attack"],
    "tower":     ["conning", "conn", "fairwater", "periscope", "tdc", "helm"],
    "fairwater": ["conning", "tower", "sail", "conn"],
    # training / qualification (pam_179)
    "training":  ["trained", "train", "school", "submarine school", "new london", "qualification", "qualify"],
    "trained":   ["training", "train", "school", "submarine school", "new london"],
    "school":    ["submarine school", "qualify", "qualification"],
    # sound-powered telephone (pam_180)
    "telephone": ["phone", "phones", "sound-powered", "spt", "circuit", "intercom"],
    "phone":     ["telephone", "phones", "sound-powered", "spt", "circuit", "intercom"],
    "intercom":  ["telephone", "phone", "sound-powered", "spt", "circuit"],
    # communicate / recognize (pam_180, pam_181)
    "recognize":  ["recognition", "silhouette", "night", "identification", "identify", "dark"],
    # night identification / silhouette recognition (pam_181)
    "identify":  ["recognition", "silhouette", "night", "identify", "identification", "oni", "dark"],
    "silhouette":["identify", "recognition", "night", "identification", "oni", "dark"],
    "recognition":["identify", "identification", "silhouette", "night", "dark"],
    # after torpedo room / aft (pam_182)
    "stern":     ["aft", "after", "rear", "torpedo room", "tubes"],
    # volunteer / selection (pam_183)
    "volunteer": ["volunteers", "volunteered", "selected", "selection", "screened", "choose"],
    "volunteers":["volunteer", "volunteered", "selected", "selection", "screened"],
    "screened":  ["volunteer", "selected", "selection", "screen", "testing", "physical"],
    "selection": ["volunteer", "volunteers", "selected", "screened", "choose", "pick"],
    # sunk / survive (pam_184)
    "sunk":      ["sink", "sinking", "lost", "survival", "survive", "casualty", "casualties"],
    "sink":      ["sunk", "sinking", "lost", "survival", "survive", "casualty"],
    "sinking":   ["sunk", "sink", "lost", "survival", "survive", "casualty"],
    "survival":  ["sunk", "sink", "survive", "casualty", "casualties", "escape"],
    "survive":   ["sunk", "sink", "sinking", "survival", "casualty", "casualties"],
    # night surface attack / deck gun (pam_185, pam_222)
    "surface":   ["surfaced", "surfacing", "awash", "deck", "gun", "guns", "deck gun", "attack", "target"],
    "surfaced":  ["surface", "surfacing", "awash"],
    "surfacing": ["surface", "surfaced", "blow", "awash"],
    # lookout / binoculars / aircraft (pam_186)
    "lookout":   ["lookouts", "watch", "binoculars", "bridge watch", "aircraft", "sector"],
    "lookouts":  ["lookout", "watch", "binoculars", "bridge watch", "aircraft"],
    "binoculars":["lookout", "lookouts", "watch", "glasses", "optics"],
    # refueled / fuel (pam_187)
    "refueled":  ["fuel", "fueled", "refuel", "refueling", "tender", "base", "guam", "midway"],
    "refuel":    ["refueled", "fuel", "fueled", "refueling", "tender", "base"],
    "refueling": ["refueled", "fuel", "fueled", "refuel", "tender", "base"],
    # angle on the bow / AOB (pam_188)
    "aob":       ["angle", "bow", "target angle", "approach angle", "track"],
    "approach":  ["aob", "angle", "bow", "attack", "intercept", "course"],
    # radio / Pearl Harbor (pam_189)
    "radio":     ["communicate", "communication", "broadcast", "transmit", "ultra", "pearl harbor"],
    "communicate":["telephone", "phone", "sound-powered", "radio", "broadcast", "transmit", "communication", "transmission", "message", "signal", "contact", "talk"],
    "broadcast": ["radio", "communicate", "communication", "transmit", "pearl harbor"],
    "transmit":  ["radio", "broadcast", "communicate", "transmission", "signal"],
    "ultra":     ["radio", "intelligence", "decrypt", "signal", "code", "codebreaking", "jn25", "convoy", "route"],
    "contact":   ["radio", "communicate", "broadcast", "transmit", "pearl harbor", "signal", "magnetic", "exploder", "mark 6", "fuze", "fuse", "dud", "detonate"],
    # forward engine room (pam_190)
    "forward":   ["engine room", "fairbanks", "diesel", "forward engine", "engines"],
    "fairbanks": ["engine", "engines", "diesel", "forward engine room", "forward"],
    # celestial navigation / dead reckoning (pam_191)
    "celestial": ["sextant", "stars", "star sights", "navigation", "navigate", "dead reckoning"],
    "sextant":   ["celestial", "stars", "star sights", "navigation", "navigate"],
    "reckoning": ["dead reckoning", "celestial", "navigation", "navigate", "position"],
    "position":  ["celestial", "sextant", "navigate", "navigation", "fix", "dead reckoning"],
    # when to surface / surfacing timing (pam_192)
    "dusk":      ["surface", "surfaced", "surfacing", "sunset", "dark", "timing"],
    "timing":    ["surface", "surfaced", "when", "decision", "dusk", "sunset"],
    # escape trunk / Momsen lung (pam_193)
    "escape":    ["trunk", "hatch", "momsen", "lung", "abandon", "emergency"],
    "trunk":     ["escape", "hatch", "momsen", "lung", "abandon", "emergency"],
    "hatch":     ["escape", "trunk", "momsen", "lung", "abandon"],
    "momsen":    ["escape", "trunk", "hatch", "lung", "rescue"],
    # sonar / passive listening (pam_194)
    "sonar":     ["hydrophone", "passive", "listening", "doppler", "sound", "propeller", "screw"],
    "hydrophone":["sonar", "passive", "listening", "sound", "propeller"],
    "passive":   ["sonar", "hydrophone", "listening", "doppler", "active"],
    "doppler":   ["sonar", "hydrophone", "passive", "listening", "speed", "frequency"],
    # chief of the boat / COB (pam_195)
    "cob":       ["chief", "boat", "senior enlisted", "chief of the boat", "master chief"],
    # torpedo spread / fan shot (pam_196)
    "spread":    ["fan", "fan shot", "torpedo spread", "gyro", "salvo", "pattern", "spreads"],
    "spreads":   ["fan", "fan shot", "torpedo spread", "gyro", "salvo", "spread"],
    "fan":       ["spread", "spreads", "fan shot", "torpedo spread", "gyro", "salvo"],
    "salvo":     ["spread", "spreads", "fan", "torpedo", "multiple", "volley"],
    # collision / fratricide / deconflict (pam_197)
    "collision": ["collide", "colliding", "friendly fire", "fratricide", "deconflict", "sector"],
    "collide":   ["collision", "colliding", "friendly fire", "fratricide"],
    "colliding": ["collision", "collide", "friendly fire", "fratricide"],
    "fratricide":["collision", "collide", "friendly fire", "deconflict", "wolfpack"],
    "deconflict":["collision", "collide", "fratricide", "sector", "zone"],
    "friendly":  ["fratricide", "deconflict", "collision", "wolfpack", "zone", "sector"],
    "attacking": ["collision", "fratricide", "friendly fire", "collide"],
    # sonar / listen / operators (pam_194)
    "listen":    ["sonar", "hydrophone", "passive", "listening", "sound operators", "operators"],
    "listening": ["listen", "sonar", "hydrophone", "passive", "sound operators"],
    "operators": ["sonar", "hydrophone", "listen", "listening", "passive", "sound operators"],
    # targeting / fire control / AOB (pam_188)
    "targeting": ["aob", "angle", "bow", "fire control", "solution", "target"],
    "target":    ["targets", "targeting", "aob", "angle", "bow", "fire control", "solution"],
    "angle":     ["aob", "bow", "approach", "bearing", "target angle"],
    # periscope attack procedure (pam_198)
    "procedure": ["periscope", "attack", "approach", "step", "steps", "solution", "fire"],
    "step":      ["procedure", "steps", "periscope", "attack", "approach"],
    "steps":     ["procedure", "step", "periscope", "attack", "approach"],
    "firing":    ["fire", "fire solution", "tdc", "shoot", "attack", "torpedo"],
    "solution":  ["fire", "tdc", "firing", "bearing", "attack", "approach"],
    # after engine room (pam_199) — extends existing "forward" / "fairbanks" entries
    "aft":       ["after", "stern", "rear", "engine room", "maneuvering"],
    "rear":      ["aft", "after", "stern", "engine room"],
    # diving planes (pam_200)
    "planesman": ["planes", "bow planes", "stern planes", "depth", "hydroplane", "control"],
    "hydroplane":["planes", "bow planes", "planesman", "depth", "diving"],
    "bow":       ["planes", "planesman", "hydroplane", "bow planes", "forward"],
    "rudder":    ["planes", "planesman", "hydroplane", "stern planes", "yaw", "heading"],
    # radar (pam_201) — extends existing "aircraft" entries
    "sj":        ["radar", "surface search", "contact", "range", "bearing"],
    "sd":        ["radar", "air search", "aircraft", "plane", "warning"],
    # tropical heat / temperature (pam_202)
    "heat":      ["hot", "temperature", "tropical", "tropics", "sweat", "humid"],
    "hot":       ["heat", "temperature", "tropical", "tropics", "sweat", "humid"],
    "temperature":["heat", "hot", "tropical", "tropics", "celsius", "degrees"],
    "tropical":  ["heat", "hot", "temperature", "tropics", "pacific", "equator"],
    "tropics":   ["tropical", "heat", "hot", "temperature", "pacific", "equator"],
    "humid":     ["heat", "hot", "tropical", "sweat", "temperature"],
    # submarine captain qualities (pam_203) — extends existing "ace/best" entries
    "captain":   ["commander", "co", "qualities", "leadership", "commanding", "officer"],
    "commander": ["captain", "co", "qualities", "leadership", "commanding", "officer"],
    "commanding":["captain", "commander", "co", "officer", "leadership"],
    "qualities": ["captain", "commander", "co", "leadership", "good", "best", "ace"],
    "leadership":["qualities", "captain", "commander", "co", "best", "ace"],
    # depth charge attack experience (pam_204) — extends existing "sonar/sound" entries
    "pinging":   ["sonar", "asdic", "hydrophone", "depth charge", "ping", "hunter"],
    "ping":      ["pinging", "sonar", "asdic", "hydrophone", "depth charge"],
    "asdic":     ["sonar", "pinging", "ping", "hydrophone", "depth charge", "jap"],
    "concussion":["depth charge", "explosion", "bang", "blast", "charge", "attack"],
    "scared":    ["depth charge", "fear", "terrifying", "terrified", "attack", "morale"],
    "fear":      ["depth charge", "scared", "terrifying", "morale", "attack"],
    "terrifying":["depth charge", "scared", "fear", "concussion", "attack"],
    # evading destroyers (pam_205) — extends existing "destroyer/silent" entries
    "evade":     ["evading", "evasion", "escape", "hide", "silent", "deep", "quiet"],
    "evading":   ["evade", "evasion", "escape", "hide", "silent", "deep", "quiet"],
    "evasion":   ["evade", "evading", "escape", "hide", "silent", "deep", "quiet"],
    "quiet":     ["silent", "silent running", "evade", "evasion", "noise"],
    "hide":      ["evade", "evading", "evasion", "silent", "deep", "quiet"],
    # aircraft threat (pam_206) — strengthens existing "aircraft/planes" entries
    "air":       ["aircraft", "airplane", "planes", "threat", "patrol", "bomb"],
    "bomb":      ["aircraft", "airplane", "depth charge", "attack", "threat"],
    "threat":    ["aircraft", "airplane", "destroyer", "destroyers", "danger"],
    # US Navy wolfpack tactics (pam_207) — strengthens existing "wolfpack" entries
    "coordinated":["wolfpack", "wolfpacks", "tactics", "pack", "group", "coordinate"],
    "coordinate": ["wolfpack", "wolfpacks", "tactics", "pack", "group", "coordinated"],
    "group":      ["wolfpack", "coordinated", "tactics", "pack", "coordinate"],
    # US subs vs enemy submarines (pam_208)
    "enemy":      ["japanese", "submarine", "enemy submarine", "batfish", "sank"],
    "batfish":    ["enemy submarine", "japanese submarine", "sank", "killed", "sink"],
    "engagements":["enemy submarine", "submarine", "batfish", "sank", "fight"],
    "engagement": ["enemy submarine", "submarine", "batfish", "sank", "fight"],
    "sank":       ["sunk", "sink", "sinking", "enemy", "batfish", "submarine", "pampanito", "ships", "merchant"],
    # magnetic vs contact exploder distinction (pam_209) — extends existing "magnetic/exploder" entries
    "mark":       ["mark 6", "magnetic", "exploder", "torpedo", "mark 14", "mark 18"],
    "detonate":   ["magnetic", "exploder", "contact", "dud", "fuze", "fuse", "fire"],
    "fuse":       ["magnetic", "exploder", "contact", "detonate", "fuze", "mark 6"],
    "fuze":       ["fuse", "magnetic", "exploder", "contact", "detonate", "mark 6"],
    # Japanese anti-submarine warfare (pam_210)
    "japanese":   ["asw", "anti-submarine", "japanese asw", "destroyer", "convoy", "depth charge"],
    "asw":        ["japanese", "anti-submarine", "destroyer", "destroyers", "depth charge"],
    "anti-submarine": ["asw", "japanese", "depth charge", "convoy", "destroyer"],
    "effectiveness":  ["japanese", "asw", "anti-submarine", "losses", "successful", "effective"],
    "effective":      ["effectiveness", "japanese", "asw", "anti-submarine", "losses"],
    "hunter":     ["asw", "anti-submarine", "japanese", "destroyer", "depth charge"],
    # submarine tender (pam_211)
    "fulton":     ["tender", "tenders", "support ship", "depot"],
    "depot":      ["tender", "tenders", "base", "support", "supply"],
    # Mark 14 depth-running problem (pam_212) — extends existing "torpedo/mark" entries
    "deeper":     ["depth", "running depth", "running", "mark 14", "dud", "exploder", "set", "failure", "torpedo"],
    "running":    ["run", "depth", "deeper", "failure", "torpedo", "problem", "running depth", "mark 14", "dud", "running deeper"],
    "buford":     ["mark 14", "torpedo", "depth", "running"],  # Lockwood slang
    "lockwood":   ["mark 14", "depth", "torpedo", "admiral"],
    # ULTRA intelligence (pam_213)
    "codebreaking":["ultra", "intelligence", "decrypt", "jn25", "convoy"],
    "decrypt":    ["ultra", "codebreaking", "intelligence", "code", "cipher"],
    "cipher":     ["ultra", "codebreaking", "decrypt", "code", "intelligence", "jn25"],
    "intelligence":["ultra", "codebreaking", "decrypt", "convoy", "route", "intercept"],
    "intercept":  ["ultra", "intelligence", "route", "convoy", "decrypt"],
    "frupac":     ["ultra", "intelligence", "codebreaking", "pearl harbor"],
    # down-the-throat shots (pam_214)
    "throat":     ["down-the-throat", "shot", "destroyer", "attack", "dealey", "bow-on"],
    "bow-on":     ["throat", "down-the-throat", "destroyer", "attack"],
    "desperate":  ["throat", "last resort", "attack", "destroyer", "counterattack"],
    "dealey":     ["harder", "destroyer", "throat", "medal", "honor", "attack"],
    "harder":     ["dealey", "destroyer", "throat", "medal", "honor"],
    # mine threat / avoidance (pam_215) — extends existing "mines" entries
    "minefields": ["mines", "mine", "threat", "avoid", "sweep", "shallow"],
    "minefield":  ["mines", "mine", "threat", "avoid", "sweep", "shallow"],
    "avoid":      ["mine", "mines", "minefields", "minefield", "evade", "evasion", "sweep", "threat", "cope"],
    "swept":      ["mines", "minefields", "minefield", "channel", "safe"],
    "shallow":    ["mines", "minefields", "minefield", "water", "reef"],
    # JANAC / tonnage accuracy (pam_216)
    "janac":      ["tonnage", "sinking", "claims", "accuracy", "accurate", "overclaim"],
    "tonnage":    ["janac", "sinking", "claims", "tons", "shipped", "merchant"],
    "overclaim":  ["janac", "tonnage", "claims", "accuracy", "overstated"],
    "overstated": ["janac", "tonnage", "claims", "accuracy", "overclaim"],
    "accurate":   ["janac", "tonnage", "claims", "accuracy", "overclaim", "confirmed"],
    "claims":     ["janac", "tonnage", "accurate", "accuracy", "sinking"],
    # strategic results / campaign impact (pam_217)
    "strategic":  ["campaign", "results", "impact", "oil", "shipping", "japan", "merchant"],
    "campaign":   ["strategic", "results", "impact", "war", "shipping", "pacific", "submarine", "tender", "supply", "base"],
    "impact":     ["strategic", "campaign", "results", "war", "shipping", "japan"],
    "decisive":   ["strategic", "campaign", "impact", "results", "merchant", "oil"],
    "merchant":   ["convoy", "convoys", "shipping", "tonnage", "tanker", "freighter"],
    "maritime":   ["merchant", "shipping", "tonnage", "convoy", "tanker"],
    "oil":        ["tanker", "fuel", "petroleum", "strategic", "crude", "dutch"],
    "tanker":     ["oil", "fuel", "petroleum", "merchant", "convoy", "tonnage"],
    # torpedo tube mechanics (pam_218)
    "tube":       ["torpedo tube", "breech", "outer door", "impulse", "flood", "fire"],
    "tubes":      ["torpedo tubes", "breech", "outer door", "impulse", "flood", "fire"],
    "breech":     ["tube", "tubes", "door", "torpedo", "loading", "seal"],
    "impulse":    ["tube", "tubes", "air", "launch", "fire", "torpedo"],
    "launch":     ["fire", "launch", "torpedo", "tube", "impulse", "eject"],
    "eject":      ["launch", "fire", "impulse", "torpedo", "tube"],
    "fired":      ["launch", "launched", "fire", "shoot", "shot", "torpedo", "tube"],
    # forward battery compartment / officers country (pam_219)
    "wardroom":   ["officers", "forward battery", "compartment", "meals", "captain", "xo"],
    "country":    ["officers", "wardroom", "forward battery", "quarters", "cabin"],
    "cabin":      ["wardroom", "officers", "captain", "co", "forward battery"],
    "stateroom":  ["cabin", "wardroom", "officers", "quarters", "forward battery"],
    "cells":      ["battery", "forward battery", "lead-acid", "power", "electric"],
    # Medal of Honor (pam_220)
    "medal":      ["honor", "moh", "gilmore", "cromwell", "fluckey", "o'kane", "award"],
    "honor":      ["medal", "moh", "award", "gilmore", "cromwell", "fluckey"],
    "moh":        ["medal", "honor", "award", "gilmore", "cromwell", "o'kane"],
    "gilmore":    ["medal", "honor", "growler", "take her down", "bridge"],
    "cromwell":   ["medal", "honor", "sculpin", "ultra", "sacrifice", "down"],
    "fluckey":    ["medal", "honor", "barb", "captain", "ace"],
    "gilmour":    ["gilmore", "medal", "honor"],  # STT misspelling
    # submarine mail (pam_221)
    "mail":       ["letters", "post", "postal", "vmail", "home", "family"],
    "letters":    ["mail", "post", "postal", "vmail", "home", "family", "write"],
    "vmail":      ["mail", "letters", "postal", "microfilm", "victory", "censored", "microfilmed", "fpo", "censor", "blacked", "fremantle"],
    "postal":     ["mail", "letters", "vmail", "fpo", "post office"],
    "censor":     ["mail", "letters", "censored", "post", "patrol"],
    "microfilm":  ["vmail", "victory", "mail", "letters", "censored"],
    # deck guns vs torpedoes (pam_222) — extends existing "gun" entries
    "guns":       ["gun", "deck gun", "5 inch", "4 inch", "surface", "gun action"],
    "gun action": ["guns", "gun", "deck gun", "surface attack", "5 inch", "gun fight"],
    "conserve":   ["torpedoes", "torpedo", "guns", "gun", "save", "deck gun", "instead", "rather"],
    "sampan":     ["guns", "gun", "deck gun", "small", "vessel", "target"],
    # conning tower vs control room (pam_223)
    "compared":   ["versus", "difference", "control room", "conning", "tower"],
    # Presidential Unit Citation (pam_224)
    "presidential":["citation", "puc", "unit", "award", "honor", "pampanito"],
    "citation":    ["presidential", "puc", "unit", "award", "honor"],
    "puc":         ["presidential", "citation", "unit", "award", "honor"],
    "unit":        ["presidential", "citation", "puc", "award"],
    # two periscopes (pam_225)
    "periscopes":  ["periscope", "attack scope", "search scope", "two", "scopes"],
    "scopes":      ["periscope", "periscopes", "attack scope", "search scope", "two"],
    "scope":       ["periscope", "periscopes", "attack scope", "search scope"],
    "attack scope":["periscope", "periscopes", "search scope", "thin", "feather"],
    "search scope":["periscope", "periscopes", "attack scope", "large", "magnification"],
    # Pampanito's war record / ships sunk (pam_226)
    "pampanito":   ["sank", "sunk", "ships", "patrols", "war record", "citation", "pow"],
    "record":      ["pampanito", "sank", "sunk", "ships", "patrols", "war record"],
    "patrols":     ["war patrol", "patrol", "pampanito", "record", "six", "missions"],
    # ----------  batch 12 follow-up synonym fixes  ----------
    # depth-running problem (pam_212)
    "problem":    ["failure", "torpedo", "malfunction", "dud", "depth", "running"],
    # mine threat / avoidance (pam_215)
    "avoiding":   ["mine", "mines", "minefield", "evasion", "evade", "avoid"],
    "avoidance":  ["mine", "mines", "minefield", "evasion", "evade", "avoid"],
    # Medal of Honor (pam_220)
    "decorated":  ["medal", "honor", "moh", "award", "gilmore", "fluckey", "citation"],
    # submarine mail (pam_221)
    "families":   ["family", "mail", "letters", "home", "loved"],
    "family":     ["families", "mail", "letters", "home", "loved"],
    "delivered":  ["mail", "letters", "post", "postal", "deliver"],
    "deliver":    ["mail", "letters", "post", "postal", "delivered"],
    # deck guns vs torpedoes (pam_222)
    "rather":     ["instead", "versus", "gun", "guns", "deck gun", "conserve"],
    "instead":    ["rather", "versus", "gun", "guns", "deck gun", "conserve"],
    # attack/search periscope (pam_225)
    "two":        ["periscopes", "attack scope", "search scope", "scopes"],
    # Mark 14 depth running failure (pam_212)
    "failure":    ["failed", "depth", "running", "problem", "mark 14", "dud", "torpedo"],
    "failed":     ["failure", "depth", "running", "problem", "dud", "torpedo"],
    # ULTRA / convoy routes (pam_213)
    "decoded":    ["ultra", "codebreaking", "cipher", "jn25", "decrypt"],
    "jn25":       ["ultra", "cipher", "codebreaking", "decrypt", "code", "intelligence"],
    # loading into tube (pam_218)
    "loaded":     ["load", "torpedo", "tube", "tubes", "breech", "skid", "reload"],
    "loading":    ["load", "torpedo", "tube", "tubes", "breech", "skid", "reload"],
    "sequence":   ["tube", "tubes", "torpedo", "firing", "flood", "breech", "outer", "launch", "steps"],
    # V-mail (pam_221) — note: "v-mail" tokenizes to "vmail"; key handles both
    "write":      ["mail", "letters", "vmail", "family", "home"],
    "wrote":      ["mail", "letters", "vmail", "family", "home"],
    # submarine tender services (pam_211)
    "services":   ["tender", "tenders", "support", "supply", "repair", "resupply"],
    "provided":   ["tender", "tenders", "supply", "support", "repair", "resupply"],
    "provides":   ["tender", "tenders", "supply", "support", "repair", "resupply"],
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
    raw_lower = raw_question.lower()
    # True only when the query explicitly asks about BOTH Mark 14 and Mark 18,
    # or uses comparison language alongside a specific Mark reference.
    # Earlier broad condition ("torpedo" + "mark") triggered for any single-Mark
    # torpedo question (e.g. "why did the Mark 14 fail?") which boosted the
    # encyclopedia faq_982 entry far above the specific repair/failure FAQs.
    _compare_words = {"vs", "versus", "difference", "differences", "compare",
                      "comparison", "better", "worse", "prefer", "preferred",
                      "advantage", "advantages", "disadvantage", "disadvantages"}
    wants_mark_compare = bool(
        ("14" in tset and "18" in tset) or
        (("14" in tset or "18" in tset) and ("mark" in tset) and (tset & _compare_words)) or
        re.search(r"mark\s*14.{0,20}mark\s*18|mark\s*18.{0,20}mark\s*14", raw_lower)
    )

    # Quantity question: "how many", "how much", "what number", etc.
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
            # Guard: only apply the boost when the chunk also matches a query
            # token *beyond* the compartment-name tokens themselves.  Without
            # this, "were there bunks in the after torpedo room" inflates tour
            # chunks that only share "torpedo"+"room" with the query and score
            # 2×9=18, burying FAQ entries that explicitly list the bunks.
            if named_compartment and source_id == "pampanito_tour":
                if ch.get("compartment_id") == named_compartment:
                    comp_toks = set(tokenize(named_compartment.replace("_", " ")))
                    content_q_tokens = [t for t in q_tokens if t not in comp_toks]
                    # Boost when: no content tokens (pure compartment query) OR
                    # at least one content token matches something in the chunk
                    if not content_q_tokens or overlap_score(content_q_tokens, text) > 0:
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
                        # Clamp to at least weight so long titles are not penalized
                        effective_weight = max(weight, weight * 4.0 * coverage)
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
# Admin: generated FAQ review / edit / accept
# ------------------------------------------------------------

_GENERATED_PREFIXES = {"der", "pam", "fix"}
_faq_write_lock = threading.Lock()


def _save_faq_corpus() -> None:
    """Atomically rewrite the FAQ JSONL file from the in-memory FAQ list."""
    tmp = FAQ_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for entry in FAQ:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, FAQ_PATH)


def _make_slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:120]


@app.get("/admin/generated-faqs")
def get_generated_faqs():
    """Return all der_, pam_, fix_ entries for the review tool."""
    return [e for e in FAQ if e.get("chunk_id", "").split("_")[0] in _GENERATED_PREFIXES]


@app.get("/admin/faqs")
def get_all_faqs():
    """Return all FAQ entries for the editor tool."""
    return [{"chunk_id": e.get("chunk_id", ""), "title": e.get("title", ""), "text": e.get("text", ""), "category": e.get("category", "")} for e in FAQ]


# ── Eternal Patrol ────────────────────────────────────────────────────────────

_ETERNAL_PATROL_PATH = os.path.join(CORPORA_DIR, "eternal_patrol.jsonl")
_eternal_patrol_cache: list | None = None

def _load_eternal_patrol() -> list:
    global _eternal_patrol_cache
    if _eternal_patrol_cache is not None:
        return _eternal_patrol_cache
    boats = []
    if os.path.exists(_ETERNAL_PATROL_PATH):
        with open(_ETERNAL_PATROL_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        boats.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    boats.sort(key=lambda b: b.get("date_lost", ""))
    _eternal_patrol_cache = boats
    return boats


@app.get("/api/eternal-patrol")
def eternal_patrol():
    """Return all submarines on eternal patrol."""
    return _load_eternal_patrol()


@app.get("/api/faqs")
def public_faqs():
    """Return all published faq_ entries grouped by category, for the public FAQ page."""
    from collections import defaultdict
    groups: dict[str, list] = defaultdict(list)
    for e in FAQ:
        if not e.get("chunk_id", "").startswith("faq_"):
            continue
        title = e.get("title", "")
        text = e.get("text", "")
        parts = text.split("\n\n", 1)
        answer = parts[1].strip() if len(parts) > 1 else text
        cat = e.get("category") or "General"
        groups[cat].append({"id": e["chunk_id"], "title": title, "answer": answer})
    return [{"category": cat, "faqs": groups[cat]} for cat in sorted(groups.keys())]


@app.post("/admin/faq")
async def create_faq(request: Request):
    """Create a new faq_NNN entry from a simple title + text payload."""
    body = await request.json()
    title = (body.get("title") or "").strip()
    text = (body.get("text") or "").strip()
    category = (body.get("category") or "").strip()
    if not title or not text:
        raise HTTPException(status_code=400, detail="title and text are required")
    with _faq_write_lock:
        faq_nums = [
            int(e["chunk_id"].split("_")[1])
            for e in FAQ
            if e.get("chunk_id", "").startswith("faq_") and e["chunk_id"].split("_")[1].isdigit()
        ]
        new_num = max(faq_nums) + 1 if faq_nums else 1
        new_id = f"faq_{new_num}"
        new_entry: Dict[str, Any] = {
            "chunk_id": new_id,
            "doc_type": "dieselsubs_faq",
            "source": "manual_editor",
            "display_citation": f"SubmarineDocent FAQ — {title}",
            "title": title,
            "text": text,
            "category": category,
            "slug": _make_slug(title),
            "topic_tags": [],
            "authority_level": "reference_faq",
            "era": "ww2",
            "platform": ["us_diesel_electric_submarines"],
        }
        FAQ.append(new_entry)
        _save_faq_corpus()
    return {"status": "created", "chunk_id": new_id}


@app.put("/admin/faq/{chunk_id}")
async def update_faq(chunk_id: str, request: Request):
    """Update title and/or text of any FAQ entry."""
    body = await request.json()
    title = (body.get("title") or "").strip()
    text = (body.get("text") or "").strip()
    entry = next((e for e in FAQ if e.get("chunk_id") == chunk_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail=f"{chunk_id} not found")
    with _faq_write_lock:
        if title:
            entry["title"] = title
        if text:
            entry["text"] = text
        if "category" in body:
            entry["category"] = (body.get("category") or "").strip()
        _save_faq_corpus()
    return {"status": "saved", "chunk_id": chunk_id}


@app.post("/admin/faq/{chunk_id}/accept")
def accept_faq(chunk_id: str):
    """Promote a generated FAQ entry to an accepted faq_NNN entry."""
    if chunk_id.split("_")[0] not in _GENERATED_PREFIXES:
        raise HTTPException(status_code=400, detail="Only der_, pam_, fix_ entries can be accepted")
    entry = next((e for e in FAQ if e.get("chunk_id") == chunk_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail=f"{chunk_id} not found")
    with _faq_write_lock:
        faq_nums = [
            int(e["chunk_id"].split("_")[1])
            for e in FAQ
            if e.get("chunk_id", "").startswith("faq_") and e["chunk_id"].split("_")[1].isdigit()
        ]
        new_num = max(faq_nums) + 1 if faq_nums else 1
        new_id = f"faq_{new_num}"
        old_id = entry["chunk_id"]
        entry["chunk_id"] = new_id
        # Normalise fields so the accepted entry matches the standard faq_ schema
        entry.setdefault("slug", _make_slug(entry.get("title", "")))
        entry.setdefault("topic_tags", [])
        entry.setdefault("authority_level", "reference_faq")
        entry.setdefault("era", "ww2")
        entry.setdefault("platform", ["us_diesel_electric_submarines"])
        entry.setdefault("pampanito_specific", True)
        entry["source"] = f"accepted_from_{old_id}"
        entry["display_citation"] = f"SubmarineDocent FAQ — {entry.get('title', new_id)}"
        entry.pop("type", None)  # pam_ entries carry a spurious "type" key
        _save_faq_corpus()
    return {"status": "accepted", "old_id": old_id, "new_id": new_id}


@app.delete("/admin/faq/{chunk_id}")
def delete_faq(chunk_id: str):
    """Permanently remove a generated FAQ entry from the corpus."""
    if chunk_id.split("_")[0] not in _GENERATED_PREFIXES:
        raise HTTPException(status_code=400, detail="Only der_, pam_, fix_ entries can be deleted")
    with _faq_write_lock:
        idx = next((i for i, e in enumerate(FAQ) if e.get("chunk_id") == chunk_id), None)
        if idx is None:
            raise HTTPException(status_code=404, detail=f"{chunk_id} not found")
        FAQ.pop(idx)
        _save_faq_corpus()
    return {"status": "deleted", "chunk_id": chunk_id}


@app.post("/admin/import-sql")
async def import_sql(sql_file: UploadFile = File(...)):
    """
    Import FAQ corpus from an uploaded phpMyAdmin SQL dump.

    Staff workflow (no technical help needed):
      1. phpMyAdmin → Export → download .sql file
      2. Open /faq_editor.html → click "Import from dieselsubs.com" → pick the file
      3. Done — corpus updated immediately, no server restart required.
    """
    import sys
    sys.path.insert(0, BASE_DIR)
    try:
        from sync_from_sql import sync_from_string
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"sync_from_sql not found: {e}")

    content = await sql_file.read()
    sql_text = content.decode("utf-8", errors="replace")

    try:
        with _faq_write_lock:
            stats = sync_from_string(sql_text, FAQ, _save_faq_corpus)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse SQL: {e}")

    return {"status": "ok", **stats}


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