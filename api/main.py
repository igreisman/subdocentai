from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import re

app = FastAPI(title="Pampanito Local RAG Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IMPORTANT: Your corpora are in /corpora at project root (not inside api/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA_DIR = os.path.join(BASE_DIR, "corpora")

TOUR_PATH = os.path.join(CORPORA_DIR, "pampanito_tour_corpus.jsonl")
FAQ_PATH = os.path.join(CORPORA_DIR, "dieselsubs_faq_corpus.jsonl")
SHORTS_PATH = os.path.join(CORPORA_DIR, "dieselsubs_shorts_corpus.jsonl")


def load_jsonl(path):
    data = []
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


@app.get("/health")
def health():
    return {
        "status": "ok",
        "tour_chunks": len(TOUR),
        "faq_chunks": len(FAQ),
        "shorts_chunks": len(SHORTS),
        "corpora_dir": CORPORA_DIR,
    }


# --------------------------
# Tokenization / scoring
# --------------------------

STOPWORDS = {
    "the", "a", "an", "what", "were", "was", "is", "are", "of", "on", "in",
    "to", "and", "for", "some", "between", "did", "do", "does", "you",
    "it", "that", "this", "with", "as", "at", "by", "from", "about",
    "whats", "what’s", "difference"
}


def tokenize(text: str):
    text = (text or "").lower()
    # keep numbers (Mark 14 / Mark 18), strip punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    toks = [t for t in text.split() if len(t) > 2 and t not in STOPWORDS]
    return toks


def overlap_score(query_tokens, text: str) -> int:
    """
    Count unique token overlap to avoid stopword hijacking.
    """
    text_tokens = set(tokenize(text))
    return len(set(query_tokens) & text_tokens)


def best_sentences(text: str, want_terms):
    """
    Extract up to 2 sentences that contain the most want_terms.
    """
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    scored = []
    for p in parts:
        pl = p.lower()
        sc = sum(1 for t in want_terms if t in pl)
        if sc > 0:
            scored.append((sc, p.strip()))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:2]]


@app.post("/ask")
def ask(payload: dict):
    question = (payload.get("question_text") or "").strip()
    compartment = (payload.get("compartment_id") or "").strip()

    q_tokens = tokenize(question)

    # detect Mark 14/18 torpedo comparison intent
    wants_mark_compare = (
        "mark" in q_tokens and ("14" in q_tokens or "18" in q_tokens)
    ) or ("torpedo" in q_tokens and "mark" in q_tokens)

    scored_hits = []

    def add_hits(chunks, source_id, weight, compartment_filter=False):
        for chunk in chunks:
            if compartment_filter and chunk.get("compartment_id") != compartment:
                continue

            text = chunk.get("text", "") or ""
            s = overlap_score(q_tokens, text)
            if s <= 0:
                continue

            # If question is about Mark 14/18, require torpedo-tech signal in the chunk
            if wants_mark_compare:
                text_l = text.lower()
                has_signal = any(k in text_l for k in [
                    "mark 14", "mk 14", "mark 18", "mk 18",
                    "steam", "wet heater", "wet-heater",
                    "electric", "battery",
                    "torpex", "warhead", "range", "speed"
                ])
                if not has_signal:
                    continue

            scored_hits.append((s * weight, chunk, source_id))

    # 1) Tour corpus (location-aware)
    add_hits(TOUR, "pampanito_tour", 3.0, compartment_filter=True)

    # 2) FAQ corpus (global reference) — lower weight so it doesn’t hijack
    add_hits(FAQ, "dieselsubs_faq", 1.2, compartment_filter=False)

    # 3) Shorts corpus (supporting)
    add_hits(SHORTS, "dieselsubs_shorts", 0.8, compartment_filter=False)

    scored_hits.sort(key=lambda x: x[0], reverse=True)

    if not scored_hits:
        return {
            "answer_mode": "standard",
            "answer_short": "I don’t have that detail in the Pampanito audio tour or the DieselSubs reference material I’m using.",
            "citations": [],
            "followups": [
                "Are you asking about the Mark 14 steam torpedo, the Mark 18 electric torpedo, or both?",
                "Do you want the quick version or the deeper docent version?"
            ],
            "refusal": {"is_refusal": True, "reason": "no_source"}
        }

    # Extractive answer: pick sentences from top hits that mention key terms
    want_terms = [
        "mark 14", "mk 14", "mark 18", "mk 18",
        "steam", "wet-heater", "wet heater",
        "electric", "battery",
        "warhead", "torpex", "range", "speed"
    ]

    used_sentences = []
    citations = []

    for score, chunk, source in scored_hits[:4]:
        text = chunk.get("text", "") or ""

        if wants_mark_compare:
            picks = best_sentences(text, want_terms)
        else:
            # for general questions, pull sentences that match query tokens
            picks = best_sentences(text, [t for t in q_tokens if len(t) > 2])

        if picks:
            used_sentences.extend(picks)
            citations.append({
                "source_id": source,
                "display_citation": chunk.get("display_citation"),
                "chunk_id": chunk.get("chunk_id")
            })

        if len(used_sentences) >= 2:
            break

    if not used_sentences:
        # fallback: first two sentences of top chunk
        top_score, top_chunk, source = scored_hits[0]
        text = (top_chunk.get("text", "") or "").strip()
        parts = re.split(r"(?<=[.!?])\s+", text)
        used_sentences = [" ".join(parts[:2]).strip()]
        citations = [{
            "source_id": source,
            "display_citation": top_chunk.get("display_citation"),
            "chunk_id": top_chunk.get("chunk_id")
        }]

    answer_short = " ".join(used_sentences).strip()
    if len(answer_short) > 700:
        answer_short = answer_short[:700].rstrip() + "…"

    return {
        "answer_mode": "standard",
        "answer_short": answer_short,
        "what_you_are_seeing": None,
        "citations": citations[:2],
        "followups": [
            "Want the quick comparison in one sentence?",
            "Want the deeper explanation of how each was powered and why it mattered?"
        ],
        "refusal": {"is_refusal": False, "reason": None}
    }