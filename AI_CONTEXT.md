Project: USS Pampanito Interactive AI Docent (Local RAG Demo)

Stack:

- FastAPI backend (api/main.py)
- Local JSONL corpora:
  - pampanito_tour_corpus.jsonl (timestamped tour narration)
  - dieselsubs_faq_corpus.jsonl (technical reference)
  - dieselsubs_shorts_corpus.jsonl (supporting content)
- Frontend: static web/index.html audio player + /ask API

Critical Design Rules:

1. Tour corpus has highest authority (location-aware)
2. Retrieval must NOT use naive substring matching
3. Must filter stopwords to avoid FAQ hijacking
4. Must prefer technical term overlap (torpedo, mark 14, battery, etc.)
5. Answers must be extractive from retrieved chunks (not random)
6. Must preserve citation format:
   - source_id
   - display_citation
   - chunk_id

Goal:
Museum-grade interactive audio tour where visitors ask contextual questions while listening.
