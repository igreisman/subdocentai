from __future__ import annotations
import base64
from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import html
import io
import json
import math
import os
import re
import secrets
import smtplib
import threading
import shutil
import unicodedata
import uuid
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

# Render persistent disk.  Editable corpora live here so on-site edits survive a
# redeploy; see _editable_corpus_path below.  Pages that are deployed but not
# published to the repository live under <disk>/web for the same reason — a
# redeploy rebuilds the container from git, so anything absent from git and not
# on the disk is gone.
_RENDER_DATA_DIR = "/data"
_UNPUBLISHED_WEB_DIR = os.path.join(_RENDER_DATA_DIR, "web")


def _unpublished_page_path(filename: str) -> Optional[str]:
    """Locate a page that ships outside the repository.

    Checks the persistent disk first, so a deployment serves the uploaded copy,
    then the ordinary checkout, so local development works for anyone who holds
    the file. Returns None when neither exists, letting the caller answer with
    an explanation instead of a stack trace.
    """
    # Callers pass a literal today, but keep this a lookup of one file in one
    # of two directories rather than something a path could ever escape.
    filename = os.path.basename(filename)
    if not filename:
        return None
    for candidate in (os.path.join(_UNPUBLISHED_WEB_DIR, filename),
                      os.path.join(WEB_DIR, filename)):
        if os.path.isfile(candidate):
            return candidate
    return None


def _env_flag(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


def _resolve_path_setting(raw_value: str, default_path: str) -> str:
    value = (raw_value or "").strip()
    if not value:
        return default_path
    if os.path.isabs(value):
        return value
    return os.path.abspath(os.path.join(BASE_DIR, value))


DEFAULT_CORPORA_DIR = os.path.join(BASE_DIR, "corpora")
SAMPLE_CORPORA_DIR = os.path.join(BASE_DIR, "sample_data", "corpora")
REQUIRED_CORPORA_FILES = (
    "pampanito_tour_corpus.jsonl",
    "dieselsubs_faq_corpus.jsonl",
    "dieselsubs_faq_categories.jsonl",
    "dieselsubs_shorts_corpus.jsonl",
    "dieselsubs_glossary.jsonl",
    "dieselsubs_operations_guide.jsonl",
    "dieselsubs_operations_guide_faq_schema.jsonl",
    "dieselsubs_operations_guide_single_record_html.jsonl",
    "incidents.jsonl",
    "eternal_patrol.jsonl",
)


def _corpora_has_required_files(directory: str) -> bool:
    return all(os.path.exists(os.path.join(directory, filename)) for filename in REQUIRED_CORPORA_FILES)


def _determine_corpora_dir(
    requested_root: str,
    explicit_sample_mode: bool,
    default_dir: str,
    sample_dir: str,
) -> Tuple[str, bool, bool]:
    if requested_root:
        resolved_dir = _resolve_path_setting(requested_root, default_dir)
        return resolved_dir, os.path.abspath(resolved_dir) == os.path.abspath(sample_dir), False

    if explicit_sample_mode:
        return sample_dir, True, False

    if _corpora_has_required_files(default_dir):
        return default_dir, False, False

    if _corpora_has_required_files(sample_dir):
        print("⚠️ Default corpora missing; falling back to bundled sample corpus")
        return sample_dir, True, True

    return default_dir, False, False


REQUESTED_CONTENT_ROOT = os.getenv("CONTENT_ROOT", "").strip()
CORPORA_DIR, SAMPLE_CONTENT_MODE, AUTO_SAMPLE_FALLBACK = _determine_corpora_dir(
    REQUESTED_CONTENT_ROOT,
    _env_flag("SAMPLE_CONTENT_MODE"),
    DEFAULT_CORPORA_DIR,
    SAMPLE_CORPORA_DIR,
)


def _csv_env(name: str, default: str) -> Tuple[str, ...]:
    raw_value = os.getenv(name, default)
    return tuple(part.strip() for part in raw_value.split(",") if part.strip())


LEGACY_DOMAIN_HOSTS = set(_csv_env("LEGACY_DOMAIN_HOSTS", "submarinedocent.com,www.submarinedocent.com"))
LEGACY_DOMAIN_TARGET = os.getenv("LEGACY_DOMAIN_TARGET", "https://submarinedocent.org").strip()
TOUR_HOST_PREFIXES = _csv_env("TOUR_HOST_PREFIXES", "pampanito.")
DEFAULT_ROOT_REDIRECT = os.getenv("DEFAULT_ROOT_REDIRECT", "/web/welcome.html").strip() or "/web/welcome.html"
RETURNING_VISITOR_REDIRECT = os.getenv("RETURNING_VISITOR_REDIRECT", "/web/faqs.html").strip() or "/web/faqs.html"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
MUSEUM_ADMIN_USERNAME = os.getenv("MUSEUM_ADMIN_USERNAME", "").strip()
MUSEUM_ADMIN_PASSWORD = os.getenv("MUSEUM_ADMIN_PASSWORD", "").strip()
PREVIEW_USERNAME = os.getenv("PREVIEW_USERNAME", "").strip()
PREVIEW_PASSWORD = os.getenv("PREVIEW_PASSWORD", "").strip()
ADMIN_PAGE_PATHS = {
    "/feedback.html",
    "/web/feedback.html",
    "/review.html",
    "/web/review.html",
    "/faq_editor.html",
    "/web/faq_editor.html",
    "/edit.html",
    "/web/edit.html",
}
PREVIEW_PAGE_PATHS = {
    "/pampanito.html",
    "/web/pampanito.html",
    "/web/pampanito-tour-cues.js",
}


def _request_host(request: Request) -> str:
    host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    return host.split(",", 1)[0].strip().split(":", 1)[0].lower()


def _is_tour_host(host: str) -> bool:
    return any(host.startswith(prefix) for prefix in TOUR_HOST_PREFIXES)


def _is_admin_path(path: str) -> bool:
    return (
        path.startswith("/admin/")
        or path == "/feedback/list"
        or path in ADMIN_PAGE_PATHS
        or (path.startswith("/web/edit_") and path.endswith(".html"))
    )


def _is_museum_admin_path(path: str) -> bool:
    return (
        path.startswith("/admin/museum_pages")
        or path == "/web/edit_museum_pages.html"
        or path == "/edit_museum_pages.html"
    )


def _is_preview_path(path: str) -> bool:
    return path in PREVIEW_PAGE_PATHS


def _check_basic_auth(request: Request, username: str, password: str) -> bool:
    header = request.headers.get("authorization", "")
    if not header.startswith("Basic "):
        return False
    try:
        raw_value = header.split(" ", 1)[1]
        decoded = base64.b64decode(raw_value).decode("utf-8")
        provided_user, provided_password = decoded.split(":", 1)
    except Exception:
        return False
    return secrets.compare_digest(provided_user, username) and secrets.compare_digest(provided_password, password)


def _basic_auth_challenge(realm: str, detail: str, status_code: int = 401) -> PlainTextResponse:
    return PlainTextResponse(
        detail,
        status_code=status_code,
        headers={"WWW-Authenticate": f'Basic realm="{realm}"'},
    )


@app.middleware("http")
async def redirect_legacy_domain(request: Request, call_next):
    host = _request_host(request)
    if host in LEGACY_DOMAIN_HOSTS:
        target = f"{LEGACY_DOMAIN_TARGET}{request.url.path}"
        if request.url.query:
            target = f"{target}?{request.url.query}"
        return RedirectResponse(url=target, status_code=308)
    return await call_next(request)


@app.middleware("http")
async def protect_sensitive_routes(request: Request, call_next):
    path = request.url.path
    if _is_museum_admin_path(path):
        super_ok = (
            ADMIN_USERNAME and ADMIN_PASSWORD
            and _check_basic_auth(request, ADMIN_USERNAME, ADMIN_PASSWORD)
        )
        museum_ok = (
            MUSEUM_ADMIN_USERNAME and MUSEUM_ADMIN_PASSWORD
            and _check_basic_auth(request, MUSEUM_ADMIN_USERNAME, MUSEUM_ADMIN_PASSWORD)
        )
        if not super_ok and not museum_ok:
            if not (ADMIN_USERNAME and ADMIN_PASSWORD) and not (MUSEUM_ADMIN_USERNAME and MUSEUM_ADMIN_PASSWORD):
                return _basic_auth_challenge(
                    "SubmarineDocent Museum Admin",
                    "Museum admin access is disabled. Set MUSEUM_ADMIN_USERNAME and MUSEUM_ADMIN_PASSWORD to enable it.",
                    status_code=503,
                )
            return _basic_auth_challenge("SubmarineDocent Museum Admin", "Authentication required.")
    elif _is_admin_path(path):
        if not ADMIN_USERNAME or not ADMIN_PASSWORD:
            return _basic_auth_challenge(
                "SubmarineDocent Admin",
                "Admin access is disabled. Set ADMIN_USERNAME and ADMIN_PASSWORD to enable it.",
                status_code=503,
            )
        if not _check_basic_auth(request, ADMIN_USERNAME, ADMIN_PASSWORD):
            return _basic_auth_challenge("SubmarineDocent Admin", "Authentication required.")
    elif _is_preview_path(path) and PREVIEW_USERNAME and PREVIEW_PASSWORD:
        if not _check_basic_auth(request, PREVIEW_USERNAME, PREVIEW_PASSWORD):
            return _basic_auth_challenge("SubmarineDocent Preview", "Authentication required.")
    return await call_next(request)

@app.get("/", include_in_schema=False)
def root_redirect(request: Request):
    host = _request_host(request)
    if host and _is_tour_host(host):
        return RedirectResponse(url="/web/pampanito.html")
    if request.cookies.get("visited") == "1":
        return RedirectResponse(url=RETURNING_VISITOR_REDIRECT)
    return RedirectResponse(url=DEFAULT_ROOT_REDIRECT)

if os.path.isdir(WEB_DIR):
    # Convenience redirect: /pampanito.html → /web/pampanito.html
    @app.get("/pampanito.html", include_in_schema=False)
    def redirect_tour_html():
        return RedirectResponse(url="/web/pampanito.html")

    # Convenience redirect: /feedback.html → /web/feedback.html
    @app.get("/feedback.html", include_in_schema=False)
    def redirect_feedback_html():
        return RedirectResponse(url="/web/feedback.html")

    # Convenience redirect: /welcome.html → /web/welcome.html
    @app.get("/welcome.html", include_in_schema=False)
    def redirect_welcome_html(request: Request):
        target = "/web/welcome.html"
        if request.url.query:
            target = f"{target}?{request.url.query}"
        return RedirectResponse(url=target)

    # Convenience redirect: /review.html → /web/review.html
    @app.get("/review.html", include_in_schema=False)
    def redirect_review_html():
        return RedirectResponse(url="/web/review.html")

    # Convenience redirect: /faq_editor.html → /web/faq_editor.html
    @app.get("/faq_editor.html", include_in_schema=False)
    def redirect_faq_editor_html():
        return RedirectResponse(url="/web/faq_editor.html")

    # Convenience redirect: /edit_glossary.html → /web/edit_glossary.html
    @app.get("/edit_glossary.html", include_in_schema=False)
    def redirect_edit_glossary_html():
        return RedirectResponse(url="/web/edit_glossary.html")

    # Convenience redirect: /edit_operations.html → /web/edit_operations.html
    @app.get("/edit_operations.html", include_in_schema=False)
    def redirect_edit_operations_html():
        return RedirectResponse(url="/web/edit_operations.html")

    # Convenience redirect: /edit_incidents.html → /web/edit_incidents.html
    @app.get("/edit_incidents.html", include_in_schema=False)
    def redirect_edit_incidents_html():
        return RedirectResponse(url="/web/edit_incidents.html")

    # Convenience redirect: /edit.html → /web/edit.html
    @app.get("/edit.html", include_in_schema=False)
    def redirect_edit_html():
        return RedirectResponse(url="/web/edit.html")

    # Public FAQ page shortcuts
    @app.get("/faqs", include_in_schema=False)
    @app.get("/faqs.html", include_in_schema=False)
    @app.get("/faq", include_in_schema=False)
    def redirect_faqs_html():
        return RedirectResponse(url="/web/faqs.html")

    @app.get("/glossary", include_in_schema=False)
    @app.get("/glossary.html", include_in_schema=False)
    def redirect_glossary_html():
        return RedirectResponse(url="/web/glossary.html")

    @app.get("/videos", include_in_schema=False)
    @app.get("/videos.html", include_in_schema=False)
    def redirect_videos_html():
        return RedirectResponse(url="/web/videos.html")

    @app.get("/index.html", include_in_schema=False)
    @app.get("/web/index.html", include_in_schema=False)
    def redirect_index_html():
        return RedirectResponse(url="/web/faqs.html")

    # Serve pampanito.html with no-cache so Safari always loads the latest version.
    #
    # The tour page is deliberately not in the repository: it is shown to the
    # Maritime Association as a proof of concept, and stays unpublished until
    # they grant permission.  So it is deployed by placing it on the Render
    # persistent disk at /data/web/pampanito.html, which survives redeploys the
    # same way editable corpora do, and a checkout copy is used when present for
    # local development.  Absent both, say so plainly rather than 500 on a
    # missing file.
    @app.get("/web/pampanito.html", include_in_schema=False)
    def serve_tour_html():
        path = _unpublished_page_path("pampanito.html")
        if path is None:
            return PlainTextResponse(
                "The Pampanito tour page is not installed on this server.\n\n"
                "It is not distributed with the source. To run it, place "
                "pampanito.html in web/ locally, or upload it to "
                f"{os.path.join(_RENDER_DATA_DIR, 'web')}/ on a deployment with a "
                "persistent disk.",
                status_code=404,
            )
        return FileResponse(
            path,
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @app.get("/web/pampanito-tour-cues.js", include_in_schema=False)
    def serve_pampanito_tour_cues_js():
        return FileResponse(
            os.path.join(WEB_DIR, "pampanito-tour-cues.js"),
            media_type="application/javascript",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    @app.get("/web/edit_operations.html", include_in_schema=False)
    def serve_edit_operations_html():
        return FileResponse(
            os.path.join(WEB_DIR, "edit_operations.html"),
            media_type="text/html",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    app.mount("/web", StaticFiles(directory=WEB_DIR, html=True), name="web")
ETERNAL_PATROL_IMAGE_DIR = os.path.join(WEB_DIR, "images", "extracted")

TOUR_PATH = os.path.join(CORPORA_DIR, "pampanito_tour_corpus.jsonl")
SHORTS_PATH = os.path.join(CORPORA_DIR, "dieselsubs_shorts_corpus.jsonl")
# Fleet Type Submarine manual series (NAVPERS 16160-16169) — reference text,
# not museum-authored content, so it is read-only and deliberately absent from
# REQUIRED_CORPORA_FILES: the app runs normally without it.
FLEETSUB_MANUAL_PATH = os.path.join(CORPORA_DIR, "dieselsubs_fleetsub_manual.jsonl")
# Editable corpora — on Render these live on the persistent disk (/data) so
# that edits made on the live site survive redeploys. The bundled copy under
# corpora/ seeds the disk on first boot and is the fallback for local/dev runs
# (or when CORPORA_DIR is overridden, e.g. sample-content mode).
_using_nondefault_corpora = os.path.abspath(CORPORA_DIR) != os.path.abspath(DEFAULT_CORPORA_DIR)
_persistent_disk_available = (not _using_nondefault_corpora) and os.path.isdir(_RENDER_DATA_DIR)


def _editable_corpus_path(filename: str) -> str:
    """Return the read/write path for an editable corpus file.

    Prefers the Render persistent disk when available, seeding it from the
    bundled corpora copy the first time. Falls back to the bundled path for
    local development or sample-content mode, so on-site edits are never lost
    to a redeploy in production.
    """
    bundled = os.path.join(CORPORA_DIR, filename)
    if not _persistent_disk_available:
        return bundled
    disk_path = os.path.join(_RENDER_DATA_DIR, filename)
    if not os.path.exists(disk_path) and os.path.exists(bundled):
        import shutil
        shutil.copy2(bundled, disk_path)
        print(f"✅ Seeded persistent disk copy of {filename} from bundled corpora")
    return disk_path


def _editable_corpus_dir(dirname: str) -> str:
    """Return the directory for editable user uploads (images/docs).

    Like _editable_corpus_path, but for a directory of uploads rather than a
    single seeded file: on Render it lives on the persistent disk so uploaded
    files survive redeploys. The caller creates it via os.makedirs.
    """
    base = _RENDER_DATA_DIR if _persistent_disk_available else CORPORA_DIR
    return os.path.join(base, dirname)


# Videos page.  Editable through the admin screens, so it lives on the persistent
# disk like every other corpus a human maintains: a video added on the live site
# has to survive the next redeploy.  The consequence is the usual one -- the
# bundled corpora/videos.jsonl seeds /data once and is ignored thereafter, so
# editing the committed file no longer changes production.  See
# docs/AddingVideos.md.
VIDEOS_PATH = _editable_corpus_path("videos.jsonl")
GLOSSARY_PATH = _editable_corpus_path("dieselsubs_glossary.jsonl")
OPERATIONS_GUIDE_PATH = _editable_corpus_path("dieselsubs_operations_guide.jsonl")
OPERATIONS_GUIDE_FAQ_SCHEMA_PATH = _editable_corpus_path("dieselsubs_operations_guide_faq_schema.jsonl")
OPERATIONS_GUIDE_SINGLE_HTML_PATH = _editable_corpus_path("dieselsubs_operations_guide_single_record_html.jsonl")
FAQ_PATH = _editable_corpus_path("dieselsubs_faq_corpus.jsonl")
CATEGORIES_PATH = _editable_corpus_path("dieselsubs_faq_categories.jsonl")


# Path for incidents corpus
INCIDENTS_PATH = _editable_corpus_path("incidents.jsonl")

# Whisper domain vocabulary prompt — persisted to a text file so it can be
# edited via the admin UI without touching source code.
_WHISPER_PROMPT_PATH = _editable_corpus_path("whisper_prompt.txt")
_WHISPER_PROMPT_DEFAULT = (
    "USS Pampanito, submarine, torpedo, periscope, conning tower, "
    "hot bunk, hot bunking, hot racking, watertight door, ballast tank, "
    "diesel engine, electric motor, sonar, hydrophone, deck gun, "
    "wardroom, galley, maneuvering room, engine room, forward torpedo room, "
    "after torpedo room, crew's mess, radio room, control room, "
    "snorkel, trim tank, bow plane, stern plane, "
    "Gato class, fleet submarine, war patrol, depth charge, "
    "skipper, officer of the deck, chief of the watch, "
    "WWII, World War Two, Pacific, Japanese, Navy"
)

def _load_whisper_prompt() -> str:
    try:
        text = open(_WHISPER_PROMPT_PATH, encoding="utf-8").read().strip()
        return text if text else _WHISPER_PROMPT_DEFAULT
    except FileNotFoundError:
        return _WHISPER_PROMPT_DEFAULT

_whisper_prompt_lock = threading.Lock()
_WHISPER_PROMPT: str = _load_whisper_prompt()

_incidents_cache: list[dict[str, Any]] | None = None

# Feature flag: keep demo fully local today; later, flip to true with funding.
USE_LLM = os.getenv("USE_LLM", "false").lower() in ("1", "true", "yes")


def _incident_sort_key(entry: dict[str, Any]) -> tuple[str, str, int]:
    date_value = str(entry.get("date_sort") or entry.get("date") or "").strip()
    name = str(entry.get("submarine_name") or "").strip().casefold()
    try:
        incident_id = int(entry.get("id") or 0)
    except (TypeError, ValueError):
        incident_id = 0
    return (date_value, name, incident_id)


def _normalize_incident_text(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").strip()


def _normalize_incident_date_sort(date_value: str) -> str:
    value = _normalize_incident_text(date_value)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    return ""


def _load_incidents() -> list[dict[str, Any]]:
    """Load incidents corpus from JSONL file."""
    global _incidents_cache
    if _incidents_cache is not None:
        return _incidents_cache

    if not os.path.exists(INCIDENTS_PATH):
        print(f"❌ File not found: {INCIDENTS_PATH}")
        _incidents_cache = []
        return _incidents_cache

    data: list[dict[str, Any]] = []
    with open(INCIDENTS_PATH, "r", encoding="utf-8-sig") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                raw_entry = json.loads(line)
            except Exception as e:
                print(f"⚠️ JSON parse error on line {i} in {INCIDENTS_PATH}: {e}")
                break
            if not isinstance(raw_entry, dict):
                continue
            entry = {
                "id": int(raw_entry.get("id") or 0),
                "date": _normalize_incident_text(raw_entry.get("date")),
                "date_sort": _normalize_incident_text(raw_entry.get("date_sort")),
                "submarine_name": _normalize_incident_text(raw_entry.get("submarine_name")),
                "hull_number": _normalize_incident_text(raw_entry.get("hull_number")),
                "incident_type": _normalize_incident_text(raw_entry.get("incident_type")),
                "description": _normalize_incident_text(raw_entry.get("description")),
                "casualties": _normalize_incident_text(raw_entry.get("casualties")),
                "status": _normalize_incident_text(raw_entry.get("status")),
                "era": _normalize_incident_text(raw_entry.get("era")),
                "notes": _normalize_incident_text(raw_entry.get("notes")),
            }
            entry["date_sort"] = entry["date_sort"] or _normalize_incident_date_sort(entry["date"])
            data.append(entry)
    print(f"✅ Loaded {len(data)} records from {os.path.basename(INCIDENTS_PATH)}")
    data.sort(key=_incident_sort_key)
    _incidents_cache = data
    return data


def _save_incidents() -> None:
    incidents = _load_incidents()
    tmp_path = INCIDENTS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        for entry in incidents:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp_path, INCIDENTS_PATH)


def _next_incident_id(incidents: list[dict[str, Any]]) -> int:
    max_id = 0
    for entry in incidents:
        try:
            max_id = max(max_id, int(entry.get("id") or 0))
        except (TypeError, ValueError):
            continue
    return max_id + 1


def _apply_incident_payload(target: dict[str, Any], payload: dict[str, Any]) -> None:
    submarine_name = _normalize_incident_text(payload.get("submarine_name"))
    if not submarine_name:
        raise HTTPException(status_code=400, detail="submarine_name is required")

    target["submarine_name"] = submarine_name
    target["date"] = _normalize_incident_text(payload.get("date"))
    target["date_sort"] = _normalize_incident_date_sort(target["date"])
    target["hull_number"] = _normalize_incident_text(payload.get("hull_number"))
    target["incident_type"] = _normalize_incident_text(payload.get("incident_type"))
    target["description"] = _normalize_incident_text(payload.get("description"))
    target["casualties"] = _normalize_incident_text(payload.get("casualties"))
    target["status"] = _normalize_incident_text(payload.get("status"))
    target["era"] = _normalize_incident_text(payload.get("era"))
    target["notes"] = _normalize_incident_text(payload.get("notes"))


# ------------------------------------------------------------
# Incidents API endpoint
# ------------------------------------------------------------

@app.get("/api/incidents")
def get_incidents():
    """Return all submarine incidents."""
    return {"incidents": list(_load_incidents())}

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
CATEGORIES = load_jsonl(CATEGORIES_PATH)
OPERATIONS_GUIDE = load_jsonl(OPERATIONS_GUIDE_PATH)
FLEETSUB_MANUAL = load_jsonl(FLEETSUB_MANUAL_PATH)

# Retrieval weight for the operations guide reference corpus.  Sits below FAQ
# (1.2) and just above shorts (0.8): reference material should supplement the
# museum's own narration and FAQ answers, never displace them.
OPERATIONS_GUIDE_WEIGHT = float(os.getenv("OPERATIONS_GUIDE_WEIGHT", "0.9"))

# The manual corpus is an order of magnitude larger than everything else the
# app holds (roughly 2,200 chunks against ~760 of tour and FAQ combined), and
# it is 1946 Navy engineering prose rather than docent narration.  It is
# weighted well below every museum-authored source so it answers only what
# nothing else can.
FLEETSUB_MANUAL_WEIGHT = float(os.getenv("FLEETSUB_MANUAL_WEIGHT", "0.5"))
print(f"Loaded: {len(TOUR)} tour, {len(FAQ)} faq, {len(SHORTS)} shorts chunks, {len(CATEGORIES)} categories, {len(OPERATIONS_GUIDE)} operations guide records")



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
        "sample_content_mode": SAMPLE_CONTENT_MODE,
        "auto_sample_fallback": AUTO_SAMPLE_FALLBACK,
        "transcribe_available": bool(_GROQ_API_KEY),
        "tour_chunks": len(TOUR),
        "faq_chunks": len(FAQ),
        "shorts_chunks": len(SHORTS),
        "operations_guide_chunks": len(OPERATIONS_GUIDE),
        "fleetsub_manual_chunks": len(FLEETSUB_MANUAL),
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
        # Domain prompt biases Whisper toward submarine/Pampanito vocabulary,
        # reducing mishearings of specialist terms (e.g. "bunk" → "punk").
        result = await client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=buf,
            language=whisper_lang,
            prompt=_WHISPER_PROMPT,
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
    # "hot" in "hot bunk/bunking" means the practice, not temperature
    (re.compile(r"\bhot[\s-]bunk", re.I), "hot"),
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
    "bunk":   ["bunks", "bunking", "bed", "beds", "rack", "racks", "berthing"],
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
    # NOTE: "pampanito" itself is deliberately NOT expanded.  Nearly every
    # visitor question names the boat they are standing on, so mapping it to
    # war-record vocabulary injected "sank / patrols / war record" into
    # unrelated questions — "when was the Pampanito built" retrieved the
    # ships-sunk narration instead of the build date.  The reverse mappings
    # below still route genuine war-record questions to the right chunks.
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


# Compound terms whose meaning is unrelated to the words they are built from.
# When the query contains one, the listed constituent is kept but NOT expanded:
# "depth" normally maps to deep/feet/dive/underwater, which turns "what is a
# depth charge" into a query about diving depth and buries the depth-charge
# entry entirely.  Tokenisation is word-at-a-time, so these are matched as
# adjacent token pairs rather than as multi-word synonym keys (which can never
# fire — see the dead "war record" / "attack scope" keys in QUERY_SYNONYMS).
COMPOUND_GUARDS: Dict[tuple[str, str], set[str]] = {
    ("depth", "charge"): {"depth"},
    ("depth", "charges"): {"depth"},
    ("depth", "charging"): {"depth"},
}


def expand_query_tokens(tokens: List[str]) -> List[str]:
    """Return query tokens plus corpus-side synonyms for better vocabulary coverage."""
    suppress: set[str] = set()
    for first, second in zip(tokens, tokens[1:]):
        guarded = COMPOUND_GUARDS.get((first, second))
        if guarded:
            suppress |= guarded

    expanded = list(tokens)
    seen = set(tokens)
    for t in tokens:
        if t in suppress:
            continue
        for syn in QUERY_SYNONYMS.get(t, []):
            if syn not in seen:
                expanded.append(syn)
                seen.add(syn)
    return expanded


# Multiplier applied when a question matches a FAQ title verbatim.  Raised from
# a hardcoded 8.0 when scoring moved to BM25: the score scale changed, and at
# 8.0 an exact title match no longer outranked chunks that merely shared more
# synonym-expanded tokens ("Where is the Pampanito?" returned her war record).
EXACT_TITLE_BOOST = float(os.getenv("EXACT_TITLE_BOOST", "20.0"))

# BM25 length-normalisation parameters.  k1 controls how quickly additional
# term matches stop adding score; b controls how strongly length is penalised
# (0 = ignore length, 1 = fully normalise).
#
# b is well below the usual 0.75 default because chunk length here reflects
# *kind*, not verbosity: a 12-token line of tour narration and an 89-token FAQ
# answer are different sorts of content, not a terse and a padded version of
# the same thing.  Penalising length hard let short narration fragments outrank
# the FAQ entry that directly answered the question — "what is a depth charge"
# returned a remark about atheists in foxholes ahead of the depth-charge entry.
BM25_K1 = 1.5
BM25_B = float(os.getenv("BM25_B", "0.3"))

_avg_chunk_tokens: Optional[float] = None
_doc_freq: Optional[Dict[str, int]] = None
_doc_count: int = 0


def _corpus_stats() -> tuple[float, Dict[str, int], int]:
    """Mean chunk length and per-token document frequency, computed once.

    Both are needed for BM25 and both depend on every corpus being loaded, so
    they are built lazily on first retrieval rather than at import time.
    """
    global _avg_chunk_tokens, _doc_freq, _doc_count
    if _avg_chunk_tokens is None:
        counts: List[int] = []
        freq: Dict[str, int] = {}
        # FLEETSUB_MANUAL is deliberately excluded.  It is ~2,200 long chunks
        # of 1946 engineering prose against ~760 of museum narration, so
        # folding it in shifts both the average chunk length and the document
        # frequency of common terms enough to change answers that have nothing
        # to do with it — measured, it cost a point of self-retrieval and one
        # of three off-script questions even with the manual's own retrieval
        # weight set to zero.  Statistics stay anchored to the museum corpora;
        # the manual is scored against them as a supplementary index.
        for corpus in (TOUR, FAQ, SHORTS, OPERATIONS_GUIDE):
            for ch in corpus:
                toks = set(tokenize(ch.get("text", "") or ""))
                if not toks:
                    continue
                counts.append(len(toks))
                for tok in toks:
                    freq[tok] = freq.get(tok, 0) + 1
        _avg_chunk_tokens = (sum(counts) / len(counts)) if counts else 1.0
        _doc_freq = freq
        _doc_count = len(counts)
    return _avg_chunk_tokens, _doc_freq or {}, _doc_count


def _idf(token: str) -> float:
    """Inverse document frequency: rare terms discriminate, common ones don't.

    Without this every matched term counts the same, so "how did the
    ventilation work" scores a chunk containing only the synonym-expanded
    "watch" as highly as one that actually discusses ventilation.
    """
    _, freq, total = _corpus_stats()
    n = freq.get(token, 0)
    return math.log(1 + (total - n + 0.5) / (n + 0.5))


def overlap_score(query_tokens: List[str], text: str) -> float:
    """Length-normalised token overlap between a synonym-expanded query and text.

    A raw match count rewards long chunks purely for having a large vocabulary:
    a 24,000-character FAQ entry intersects almost any query and so won every
    question that didn't match a FAQ title outright, answering "how did the air
    system work" from an entry about depth-charge attacks.

    BM25 saturation fixes that.  Additional matched terms give diminishing
    returns (k1), and the score is divided by chunk length relative to the
    corpus average (b), so a long chunk must match proportionally more of the
    query to outrank a short, precise one.
    """
    expanded = expand_query_tokens(query_tokens)
    text_tokens = set(tokenize(text))
    matched = set(expanded) & text_tokens
    if not matched:
        return 0.0
    avg_len, _, _ = _corpus_stats()
    length_ratio = len(text_tokens) / avg_len
    # Binary term frequency (presence, not count), so the saturation term is
    # the same for every matched token and only the IDF weighting varies.
    saturation = (BM25_K1 + 1) / (1 + BM25_K1 * (1 - BM25_B + BM25_B * length_ratio))
    return sum(_idf(tok) for tok in matched) * saturation


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

    def _get_chunk_title(ch: Dict[str, Any], text: str) -> str:
        explicit_title = (ch.get("title") or "").strip()
        if explicit_title:
            return explicit_title
        raw_paras = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
        if raw_paras and raw_paras[0].rstrip().endswith("?"):
            return raw_paras[0]
        return ""

    normalized_question = re.sub(r"[^a-z0-9\s]", " ", (question_text or "").lower()).split()
    normalized_question_text = " ".join(normalized_question)

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
            title_text = _get_chunk_title(ch, text)
            if title_text:
                title_toks = set(tokenize(title_text))
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
                        # Every query token appears in the title, so the entry
                        # answers the whole question: apply the full boost and
                        # do NOT scale by coverage.  Scaling diluted the match
                        # for titles carrying extra words — "what is a depth
                        # charge" against "What is a depth charge and how did
                        # it work?" lost two thirds of the boost and ranked
                        # below a passing mention in tour narration.
                        effective_weight = max(weight, weight * 4.0)
                    elif matched >= max(1, len(q_set) - 1):
                        # Near-exact (all but one): scale 2x by coverage
                        effective_weight = weight * 2.0 * coverage

                    normalized_title_text = " ".join(
                        re.sub(r"[^a-z0-9\s]", " ", title_text.lower()).split()
                    )
                    if normalized_question_text and normalized_question_text == normalized_title_text:
                        # Exact FAQ wording should outrank broader topical chunks.
                        effective_weight = max(effective_weight, weight * EXACT_TITLE_BOOST)

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

    # Operations guide (global) – maritime.org reference material.  Weighted
    # below FAQ so it supplements the museum's own answers rather than
    # displacing them; a visitor standing in a compartment should still hear
    # the tour narration first.  Tunable without a code edit so the weight can
    # be re-checked against real questions after the corpus grows.
    add_hits(OPERATIONS_GUIDE, "dieselsubs_operations_guide",
             weight=OPERATIONS_GUIDE_WEIGHT, compartment_filter=False)

    # Fleet Type Submarine manual series (global) – the primary sources behind
    # the operations guide's descriptions.  Lowest weight of any corpus.
    add_hits(FLEETSUB_MANUAL, "fleetsub_manual",
             weight=FLEETSUB_MANUAL_WEIGHT, compartment_filter=False)

    hits.sort(key=lambda x: x[0], reverse=True)
    return hits[:top_k]


# ------------------------------------------------------------
# Synthesis: Extractive now, OpenAI later (stubbed)
# ------------------------------------------------------------

def html_to_speakable(value: str) -> str:
    """Convert rich-text FAQ HTML into plain prose with paragraph breaks.

    FAQ entries are authored in the admin rich-text editor and stored as HTML;
    that stored markup is the source of truth for editing and must not be
    rewritten on disk.  Answers, however, are spoken aloud and rendered as
    plain text, so tags have to come out at synthesis time.

    Block-level closers become blank lines.  This matters beyond cosmetics:
    much of the FAQ corpus is stored as a single line with no newlines at all,
    which defeats every downstream routine that works paragraph- or
    line-at-a-time (see clean_for_audio) and could blank an entire answer.
    """
    if not value:
        return ""
    if not re.search(r"</?[a-z][^>]*>|&(?:nbsp|amp|lt|gt|quot|#39);", value, re.I):
        return value
    v = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", " ", value, flags=re.I | re.S)
    # Newlines inside HTML source are insignificant whitespace — Word and Quill
    # both hard-wrap their markup mid-sentence.  Collapse them before inserting
    # our own breaks, or the wrapping leaks into the spoken answer.
    v = re.sub(r"\s+", " ", v)
    v = re.sub(r"<br\s*/?>", "\n", v, flags=re.I)
    v = re.sub(r"</(p|div|li|h[1-6]|tr|blockquote)\s*>", "\n\n", v, flags=re.I)
    v = re.sub(r"<li\b[^>]*>", "• ", v, flags=re.I)
    v = re.sub(r"<[^>]+>", "", v)
    v = html.unescape(v).replace("\xa0", " ")
    v = re.sub(r"[ \t]+", " ", v)
    v = re.sub(r" *\n *", "\n", v)
    v = re.sub(r"\n{3,}", "\n\n", v)
    return v.strip()


def chunk_display_text(ch: Dict[str, Any]) -> str:
    """Speakable text for a retrieved chunk, with any stored HTML removed."""
    return html_to_speakable(ch.get("text", "") or "")


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


# ── Supplementary video attachments ──────────────────────────────────────────
# A record may carry a video that illustrates its answer — oral-history
# testimony, museum footage.  Third-party clips are embedded from the host
# rather than copied into web/videos/, so the file, the rights, and any takedown
# stay with the uploader; see docs/MediaRightsReview.md.  The answer text has to
# stand on its own: an uploader can pull a video at any time, and when that
# happens the embed goes dark while the answer still reads.
# Shared by every field that ends up in an href or an iframe src.  Anything that
# isn't plainly http(s) is rejected: these records are editable through the admin
# screens and by hand, so a "javascript:" URL would be a script-injection path
# into visitors' pages rather than a merely broken link.
_SAFE_LINK_SCHEME_RE = re.compile(r"^https?://", re.I)

_YT_ID_RE = re.compile(
    r"(?:youtube\.com/(?:watch\?(?:.*&)?v=|embed/|shorts/)|youtu\.be/)([A-Za-z0-9_-]{11})"
)

# A URL ending in a media extension is a file we serve, not a page to frame.
_MEDIA_FILE_RE = re.compile(r"\.(mp4|m4v|mov|webm|ogv)$", re.I)


def _video_payload(entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Normalize a record's video_* fields into an embeddable payload, or None.

    YouTube links are rewritten to the youtube-nocookie host: a standard embed
    sets YouTube's tracking cookie on a museum page for visitors who never
    opted into it.  A non-YouTube URL is passed through untouched so this isn't
    locked to one host.
    """
    raw_url = (entry.get("video_url") or "").strip()
    # Only http(s) may reach an iframe src.  Records are editable through the
    # admin screens and hand-maintained in videos.jsonl, so a "javascript:" URL
    # is a live script-injection path into every visitor's page, not a typo that
    # merely renders a broken embed.  Reject rather than pass through.
    if not raw_url or not _SAFE_LINK_SCHEME_RE.match(raw_url):
        return None
    try:
        start = int(entry.get("video_start") or 0)
    except (TypeError, ValueError):
        start = 0
    match = _YT_ID_RE.search(raw_url)
    if match:
        embed_url = f"https://www.youtube-nocookie.com/embed/{match.group(1)}?rel=0"
        if start > 0:
            embed_url += f"&start={start}"
        kind = "embed"
    else:
        embed_url = raw_url
        # A media file we host ourselves plays in a <video> element, not an
        # iframe: real controls, no third party, and it keeps working where a
        # phone can't reach the open internet -- which inside a steel hull is
        # most places.  #t= is the direct-file equivalent of YouTube's start.
        kind = "file" if _MEDIA_FILE_RE.search(raw_url.split("?", 1)[0]) else "embed"
        if kind == "file" and start > 0:
            embed_url += f"#t={start}"
    return {
        "kind": kind,
        "embed_url": embed_url,
        "watch_url": raw_url,
        "caption": (entry.get("video_caption") or "").strip(),
        "credit": (entry.get("video_credit") or "").strip(),
        "credit_url": (entry.get("video_credit_url") or "").strip(),
        "start": start,
    }


# ── Related outside sources ──────────────────────────────────────────────────
# A referral, not a reproduction.  Some material we'd like visitors to hear can't
# be hosted or embedded: Veterans History Project oral histories, for instance,
# are held by the Library of Congress but the veterans retain copyright, and LoC
# states it "cannot give or deny permission" to republish them.  A hyperlink to
# the holding institution's own page carries none of that exposure, so a record
# can point at such material without our copying a byte of it.


def _related_links_payload(entry: Dict[str, Any]) -> List[Dict[str, str]]:
    """Normalize a record's related_links into a safe, renderable list.

    Records are editable through the admin screens, so the URL scheme is
    checked here rather than trusted: only http(s) survives, which keeps a
    pasted ``javascript:`` URL from reaching an href.  Entries without a usable
    URL are dropped rather than rendered as dead links.
    """
    raw = entry.get("related_links")
    if not isinstance(raw, list):
        return []
    out: List[Dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        url = (item.get("url") or "").strip()
        if not url or not _SAFE_LINK_SCHEME_RE.match(url):
            continue
        out.append({
            "url": url,
            "label": (item.get("label") or "").strip() or url,
            # Holding institutions often prescribe an exact citation format;
            # VHP does, down to the collection ID.  Carry it verbatim.
            "citation": (item.get("citation") or "").strip(),
        })
    return out


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
        text = chunk_display_text(ch)
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
            raw_text = chunk_display_text(ch)
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
                "source_url": ch.get("source_url"),
            })

    # Secondary chunk: supplement if primary is thin.
    # Do not append a second chunk onto a FAQ answer body — for exact FAQ-style
    # questions that produces mixed answers like the right FAQ followed by an
    # unrelated generic explanation from another chunk.
    # Also skip if this is a quantity question and the primary already contains
    # a number — the answer is complete and supplementing adds off-topic content.
    _primary_has_number = bool(re.search(
        r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten"
        r"|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen"
        r"|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy"
        r"|eighty|ninety|hundred|thousand|dozen|thirty-six|twenty-four)\b",
        " ".join(used_sentences), re.I
    ))
    if faq_body is None and len(used_sentences) < 3 and len(hits) > 1 and not (intent.get("wants_quantity") and _primary_has_number):
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
                    "source_url": ch2.get("source_url"),
                })
                break

    if not used_sentences:
        # fallback: try any hit that has sentences containing query terms,
        # preferring FAQ/shorts over tour for this last-resort path
        for _, ch_fb, src_fb in sorted(hits, key=lambda h: 0 if h[2] != "pampanito_tour" else 1):
            sents_fb = split_sentences(chunk_display_text(ch_fb))
            rel = [s for s in sents_fb if any(w in s.lower() for w in want_terms_l)] if want_terms_l else sents_fb[:2]
            if rel:
                used_sentences = rel[:3]
                citations = [{
                    "source_id": src_fb,
                    "display_citation": ch_fb.get("display_citation"),
                    "chunk_id": ch_fb.get("chunk_id"),
                    "source_url": ch_fb.get("source_url"),
                }]
                break
        # absolute last resort: first two sentences of the top chunk
        if not used_sentences:
            _, ch, source_id = hits[0]
            sents = split_sentences(chunk_display_text(ch))
            used_sentences = sents[:2] if sents else ["(No text available in retrieved chunk.)"]
            citations = [{
                "source_id": source_id,
                "display_citation": ch.get("display_citation"),
                "chunk_id": ch.get("chunk_id"),
                "source_url": ch.get("source_url"),
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
    # Answers drawn from the Fleet Type Submarine manuals are 1946 Navy
    # engineering prose, not museum-authored narration, and without a lead-in
    # they reach the visitor in the docent's own voice with nothing marking the
    # difference.  Name the manual the text actually came from.
    elif citations and answer_short and citations[0].get("source_id") == "fleetsub_manual":
        used_chunk_id = citations[0].get("chunk_id")
        man_ch = next((c for c in FLEETSUB_MANUAL if c.get("chunk_id") == used_chunk_id), None)
        manual_name = (man_ch or {}).get("manual", "").strip()
        if manual_name:
            answer_short = f"From the Navy's 1946 manual {manual_name}\n\n{answer_short}"
        else:
            answer_short = f"From the Navy's 1946 fleet submarine manuals\n\n{answer_short}"
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
        r"==>|-->"                          # arrow diagrams
        r"|\[[A-Z][\w\s]{0,20}\].{0,40}\["  # [Foo] ... [Bar] bracket chains
        r"|^\s*[|+][-+|]+[|+]\s*$"          # box-drawing lines
        r"|^Note\s*:",                      # "NOTE :" headers from FAQ
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
        "since", "so that", "designed to", "meant to", "required to",
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
                    raw_text = chunk_display_text(ch_why)
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

    # Any video belongs to the chunk that actually supplied the answer text, not
    # to hits[0] — the "why"-question rebuild above can cite a different chunk.
    video = None
    related_links: List[Dict[str, str]] = []
    if citations:
        cited_id = citations[0].get("chunk_id")
        for _, ch_video, _src_video in hits:
            if ch_video.get("chunk_id") == cited_id:
                video = _video_payload(ch_video)
                related_links = _related_links_payload(ch_video)
                break

    return {
        "answer_mode": "standard",
        "answer_short": answer_short,
        "partial_match": partial_match,
        "faq_id": faq_chunk_id,
        "video": video,
        "related_links": related_links,
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
_category_write_lock = threading.Lock()
_videos_write_lock = threading.Lock()
_glossary_write_lock = threading.Lock()
_incidents_write_lock = threading.Lock()
_operations_guide_write_lock = threading.Lock()
_eternal_patrol_write_lock = threading.Lock()


def _normalize_faq_html(text: str) -> str:
    value = (text or "").replace("\r\n", "\n").strip()
    if not value:
        return ""
    if not re.search(r"</?[a-z][\s\S]*>|&(?:nbsp|amp|lt|gt|quot|#39);", value, re.I):
        return value

    value = re.sub(r'<span class="ql-ui"[^>]*></span>', "", value, flags=re.I)
    # Unwrap Word bookmark anchors like <a name="_Hlk...">text</a> (no href).
    # They carry no behavior but inherit the blue link color on the public page,
    # showing up as an "unfixable" blue paragraph. Keep the inner text, drop the tag.
    value = re.sub(r'<a\b(?![^>]*\bhref=)[^>]*>(.*?)</a>', r"\1", value, flags=re.I | re.S)
    value = re.sub(r'\sdata-row="\d+"', "", value, flags=re.I)
    value = re.sub(r'\sstyle="color:\s*black;?"', "", value, flags=re.I)
    value = re.sub(r'\sclass="ql-align-right"', ' style="text-align: right;"', value, flags=re.I)
    value = re.sub(r'\sclass="ql-align-center"', ' style="text-align: center;"', value, flags=re.I)
    value = re.sub(r'\sclass="ql-align-justify"', ' style="text-align: justify;"', value, flags=re.I)
    value = re.sub(
        r'\sclass="ql-indent-(\d+)"',
        lambda m: f' style="margin-left: {int(m.group(1)) * 3}em;"',
        value,
        flags=re.I,
    )

    def _normalize_list(match: re.Match[str]) -> str:
        body = match.group(1)
        list_tag = "ol"
        if re.search(r'<li\b[^>]*data-list="bullet"', body, re.I) and not re.search(r'<li\b[^>]*data-list="ordered"', body, re.I):
            list_tag = "ul"
        normalized_body = re.sub(r'\sdata-list="(?:bullet|ordered)"', "", body, flags=re.I)
        return f"<{list_tag}>{normalized_body}</{list_tag}>"

    def _normalize_unordered_list(match: re.Match[str]) -> str:
        normalized_body = re.sub(r'\sdata-list="(?:bullet|ordered)"', "", match.group(1), flags=re.I)
        return f"<ul>{normalized_body}</ul>"

    value = re.sub(r'<ol\b[^>]*>(.*?)</ol>', _normalize_list, value, flags=re.I | re.S)
    value = re.sub(r'<ul\b[^>]*>(.*?)</ul>', _normalize_unordered_list, value, flags=re.I | re.S)

    while re.match(r'^\s*<p><br></p>', value, flags=re.I):
        value = re.sub(r'^\s*<p><br></p>', "", value, count=1, flags=re.I)
    while re.search(r'<p><br></p>\s*$', value, flags=re.I):
        value = re.sub(r'<p><br></p>\s*$', "", value, count=1, flags=re.I)
    return value.strip()


def _save_faq_corpus() -> None:
    """Atomically rewrite the FAQ JSONL file from the in-memory FAQ list."""
    tmp = FAQ_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for entry in FAQ:
            entry["text"] = _normalize_faq_html(entry.get("text", ""))
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, FAQ_PATH)


def _make_slug(title: str) -> str:
    s = title.lower()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s[:120]


def _save_categories_corpus() -> None:
    """Atomically rewrite the FAQ categories JSONL file from the in-memory category list."""
    tmp = CATEGORIES_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for entry in sorted(CATEGORIES, key=lambda e: (int(e.get("sort_order") or 0), (e.get("title") or "").lower())):
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, CATEGORIES_PATH)


_glossary_cache: list[dict[str, Any]] | None = None


def _glossary_sort_key(term: str) -> tuple[str, str]:
    normalized = unicodedata.normalize("NFKD", term or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return (ascii_value.casefold(), (term or "").casefold())


def _load_glossary() -> list[dict[str, Any]]:
    global _glossary_cache
    if _glossary_cache is not None:
        return _glossary_cache

    entries: list[dict[str, Any]] = []
    if os.path.exists(GLOSSARY_PATH):
        with open(GLOSSARY_PATH, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                entries.append({
                    "id": int(entry.get("id") or 0),
                    "term": str(entry.get("term") or "").strip(),
                    "definition": str(entry.get("definition") or "").strip(),
                })

    entries.sort(key=lambda entry: _glossary_sort_key(entry.get("term", "")))
    _glossary_cache = entries
    return entries


def _save_glossary() -> None:
    entries = _load_glossary()
    tmp_path = GLOSSARY_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp_path, GLOSSARY_PATH)


def _next_glossary_id(entries: list[dict[str, Any]]) -> int:
    max_id = 0
    for entry in entries:
        try:
            max_id = max(max_id, int(entry.get("id") or 0))
        except (TypeError, ValueError):
            continue
    return max_id + 1


def _assert_unique_glossary_term(entries: list[dict[str, Any]], term: str, ignore_id: int | None = None) -> None:
    normalized = term.casefold()
    for entry in entries:
        try:
            entry_id = int(entry.get("id") or 0)
        except (TypeError, ValueError):
            entry_id = 0
        if ignore_id is not None and entry_id == ignore_id:
            continue
        if str(entry.get("term") or "").strip().casefold() == normalized:
            raise HTTPException(status_code=409, detail="A glossary term with that name already exists")


def _apply_glossary_payload(target: dict[str, Any], payload: dict[str, Any]) -> None:
    term = (payload.get("term") or "").strip()
    if not term:
        raise HTTPException(status_code=400, detail="term is required")
    target["term"] = term
    target["definition"] = _normalize_faq_html(payload.get("definition") or "")


def _operations_guide_sort_key(entry: dict[str, Any]) -> tuple[int, str]:
    chunk_id = str(entry.get("chunk_id") or "")
    match = re.search(r"(\d+)$", chunk_id)
    order = int(match.group(1)) if match else 0
    return (order, chunk_id)


def _operations_text_blocks(text: str) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    current_paragraph: list[str] = []
    current_list: list[str] = []

    def flush_paragraph() -> None:
        nonlocal current_paragraph
        if current_paragraph:
            blocks.append({"type": "paragraph", "text": " ".join(line.strip() for line in current_paragraph if line.strip())})
            current_paragraph = []

    def flush_list() -> None:
        nonlocal current_list
        if current_list:
            blocks.append({"type": "list", "items": current_list[:]})
            current_list = []

    for raw_line in str(text or "").replace("\r\n", "\n").split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            flush_paragraph()
            flush_list()
            continue
        if stripped.startswith("- "):
            flush_paragraph()
            current_list.append(stripped[2:].strip())
            continue
        flush_list()
        current_paragraph.append(stripped)

    flush_paragraph()
    flush_list()
    return blocks


def _operations_text_to_html(text: str) -> str:
    parts: list[str] = []
    for block in _operations_text_blocks(text):
        if block["type"] == "paragraph":
            parts.append(f"<p>{html.escape(block['text'])}</p>")
        elif block["type"] == "list":
            items = "".join(f"<li>{html.escape(item)}</li>" for item in block["items"])
            parts.append(f"<ul>{items}</ul>")
    return "".join(parts)


def _operations_topic_tags(entry: dict[str, Any]) -> list[str]:
    seed_text = " ".join([
        str(entry.get("section") or "").replace("_", " "),
        str(entry.get("title") or ""),
    ])
    tags: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[a-z0-9]+", seed_text.lower()):
        if len(token) < 3 or token in seen:
            continue
        seen.add(token)
        tags.append(token)
        if len(tags) >= 6:
            break
    if "ww2" not in seen:
        tags.append("ww2")
    return tags[:7]


def _build_operations_guide_faq_schema_entries() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for entry in sorted(OPERATIONS_GUIDE, key=_operations_guide_sort_key):
        chunk_id = str(entry.get("chunk_id") or "ops_000")
        title = str(entry.get("title") or "Operations Guide Entry").strip()
        records.append({
            "chunk_id": f"faq_{chunk_id}",
            "doc_type": "dieselsubs_faq",
            "source": "Submarine Operations Guide",
            "title": title,
            "slug": _make_slug(title),
            "category": "Operations Guide",
            "text": _operations_text_to_html(str(entry.get("text") or "")),
            "topic_tags": _operations_topic_tags(entry),
            "authority_level": "reference_faq",
            "era": "ww2",
            "platform": ["us_diesel_electric_submarines"],
            "pampanito_specific": False,
            "display_citation": str(entry.get("display_citation") or f"Operations Guide — {title}"),
        })
    return records


def _build_operations_guide_single_html_record() -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for entry in sorted(OPERATIONS_GUIDE, key=_operations_guide_sort_key):
        groups.setdefault(str(entry.get("section") or "custom"), []).append(entry)

    html_parts = [
        '<div id="operations-view">',
        '<h1>Submarine Operations</h1>',
        '<p>Explore the fascinating world of submarine operations, tactics, and missions throughout history.</p>',
    ]

    for section_name, heading in [
        ("overview", "About Submarine Operations"),
        ("types_of_operations", "Types of Operations"),
        ("tactical_approaches", "Tactical Approaches"),
        ("related_faqs", "Related FAQs"),
        ("statistics", "WWII Pacific Theater Statistics"),
        ("additional_resources", "Additional Resources"),
    ]:
        entries = groups.pop(section_name, [])
        if not entries:
            continue
        html_parts.append(f"<section><h2>{html.escape(heading)}</h2>")
        for entry in entries:
            title = str(entry.get("title") or "").strip()
            if section_name != "overview" and title and title.lower() != heading.lower():
                html_parts.append(f"<article><h3>{html.escape(title)}</h3>{_operations_text_to_html(str(entry.get('text') or ''))}</article>")
            else:
                html_parts.append(_operations_text_to_html(str(entry.get("text") or "")))
        html_parts.append("</section>")

    for section_name, entries in groups.items():
        if not entries:
            continue
        html_parts.append(f"<section><h2>{html.escape(section_name.replace('_', ' ').title())}</h2>")
        for entry in entries:
            title = str(entry.get("title") or "").strip()
            html_parts.append(f"<article><h3>{html.escape(title)}</h3>{_operations_text_to_html(str(entry.get('text') or ''))}</article>")
        html_parts.append("</section>")

    html_parts.append("</div>")
    return {
        "chunk_id": "ops_html_001",
        "doc_type": "dieselsubs_operations_guide_html",
        "source": "Submarine Operations Guide",
        "title": "Submarine Operations",
        "slug": "submarine-operations",
        "category": "Operations Guide",
        "text": "".join(html_parts),
        "display_citation": "Operations Guide — Submarine Operations",
        "source_url": "/web/faqs.html?view=operations",
    }


def _save_operations_derived_exports() -> None:
    faq_schema_records = _build_operations_guide_faq_schema_entries()
    faq_schema_tmp_path = OPERATIONS_GUIDE_FAQ_SCHEMA_PATH + ".tmp"
    with open(faq_schema_tmp_path, "w", encoding="utf-8") as handle:
        for entry in faq_schema_records:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(faq_schema_tmp_path, OPERATIONS_GUIDE_FAQ_SCHEMA_PATH)

    html_record = _build_operations_guide_single_html_record()
    html_tmp_path = OPERATIONS_GUIDE_SINGLE_HTML_PATH + ".tmp"
    with open(html_tmp_path, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(html_record, ensure_ascii=False) + "\n")
    os.replace(html_tmp_path, OPERATIONS_GUIDE_SINGLE_HTML_PATH)


def _save_operations_guide() -> None:
    tmp_path = OPERATIONS_GUIDE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        for entry in sorted(OPERATIONS_GUIDE, key=_operations_guide_sort_key):
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp_path, OPERATIONS_GUIDE_PATH)
    _save_operations_derived_exports()


def _next_operations_guide_chunk_id(entries: list[dict[str, Any]]) -> str:
    max_value = 0
    for entry in entries:
        match = re.search(r"(\d+)$", str(entry.get("chunk_id") or ""))
        if match:
            max_value = max(max_value, int(match.group(1)))
    return f"ops_{max_value + 1:03d}"


def _apply_operations_guide_payload(target: dict[str, Any], payload: dict[str, Any]) -> None:
    title = str(payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")

    target["doc_type"] = "dieselsubs_operations_guide"
    target["section"] = str(payload.get("section") or "").strip() or "custom"
    target["title"] = title
    target["text"] = str(payload.get("text") or "").replace("\r\n", "\n").strip()
    target["display_citation"] = str(payload.get("display_citation") or "").strip() or f"Submarine Operations Guide — {title}"
    target["source_url"] = str(payload.get("source_url") or "").strip() or "/web/faqs.html?view=operations"


def _category_text(title: str, description: str) -> str:
    description = (description or "").strip()
    return f"{title}\n\n{description}" if description else title


def _find_category_entry(title: str) -> Optional[dict[str, Any]]:
    title = (title or "").strip()
    for entry in CATEGORIES:
        entry_title = (entry.get("title") or entry.get("name") or "").strip()
        if entry_title == title:
            return entry
    return None


def _next_category_id() -> int:
    existing_ids = [int(entry.get("category_id")) for entry in CATEGORIES if str(entry.get("category_id", "")).isdigit()]
    return max(existing_ids) + 1 if existing_ids else 1


def _materialize_category_record(record: dict[str, Any], sort_order: int) -> dict[str, Any]:
    title = (record.get("title") or "").strip()
    if not title:
        raise ValueError("Category title is required")

    description = (record.get("description") or "").strip()
    slug = record.get("slug") or _make_slug(title)
    entry = _find_category_entry(title)
    if entry is None:
        category_id = record.get("category_id")
        if not str(category_id or "").isdigit():
            category_id = _next_category_id()
        entry = {
            "chunk_id": record.get("chunk_id") or f"faq_category_{category_id}",
            "doc_type": "dieselsubs_faq_category",
            "source": record.get("source") or "manual_editor",
            "category_id": category_id,
            "title": title,
            "slug": slug,
            "description": description,
            "text": _category_text(title, description),
            "sort_order": sort_order,
            "era": record.get("era") or "ww2",
            "platform": record.get("platform") or ["us_diesel_electric_submarines"],
            "display_citation": record.get("display_citation") or f"SubmarineDocent FAQ Category — {title}",
        }
        CATEGORIES.append(entry)
        return entry

    entry["title"] = title
    entry["slug"] = slug
    entry["description"] = description
    entry["text"] = _category_text(title, description)
    entry["sort_order"] = sort_order
    entry["display_citation"] = f"SubmarineDocent FAQ Category — {title}"
    entry.setdefault("doc_type", "dieselsubs_faq_category")
    entry.setdefault("source", "manual_editor")
    entry.setdefault("era", "ww2")
    entry.setdefault("platform", ["us_diesel_electric_submarines"])
    if not str(entry.get("category_id", "")).isdigit():
        entry["category_id"] = _next_category_id()
    if not entry.get("chunk_id"):
        entry["chunk_id"] = f"faq_category_{entry['category_id']}"
    return entry


def _normalize_category_sort_orders() -> None:
    records = _get_category_records()
    for index, record in enumerate(records):
        _materialize_category_record(record, index * 10)
    _save_categories_corpus()


def _get_category_records() -> list[dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    max_sort_order = 0

    for entry in CATEGORIES:
        title = (entry.get("title") or entry.get("name") or "").strip()
        if not title:
            continue
        sort_order = int(entry.get("sort_order") or 0)
        max_sort_order = max(max_sort_order, sort_order)
        records[title] = {
            "chunk_id": entry.get("chunk_id") or f"faq_category_{entry.get('category_id', _make_slug(title))}",
            "category_id": entry.get("category_id"),
            "title": title,
            "slug": entry.get("slug") or _make_slug(title),
            "description": entry.get("description") or "",
            "sort_order": sort_order,
        }

    extra_sort_order = max_sort_order + 10
    for entry in FAQ:
        title = (entry.get("category") or "").strip()
        if not title or title in records:
            continue
        records[title] = {
            "chunk_id": f"faq_category_{_make_slug(title)}",
            "category_id": None,
            "title": title,
            "slug": _make_slug(title),
            "description": "",
            "sort_order": extra_sort_order,
        }
        extra_sort_order += 10

    return sorted(records.values(), key=lambda e: (int(e.get("sort_order") or 0), e.get("title", "").lower()))


def _ensure_category_exists(category: str) -> None:
    title = (category or "").strip()
    if not title:
        return
    if any((entry.get("title") or entry.get("name") or "").strip() == title for entry in CATEGORIES):
        return

    existing_ids = [int(entry.get("category_id")) for entry in CATEGORIES if str(entry.get("category_id", "")).isdigit()]
    existing_orders = [int(entry.get("sort_order") or 0) for entry in CATEGORIES]
    next_id = max(existing_ids) + 1 if existing_ids else 1
    next_order = max(existing_orders) + 10 if existing_orders else 0
    CATEGORIES.append({
        "chunk_id": f"faq_category_{next_id}",
        "doc_type": "dieselsubs_faq_category",
        "source": "manual_editor",
        "category_id": next_id,
        "title": title,
        "slug": _make_slug(title),
        "description": "",
        "text": title,
        "sort_order": next_order,
        "era": "ww2",
        "platform": ["us_diesel_electric_submarines"],
        "display_citation": f"SubmarineDocent FAQ Category — {title}",
    })
    _save_categories_corpus()


@app.get("/admin/generated-faqs")
def get_generated_faqs():
    """Return all der_, pam_, fix_ entries for the review tool."""
    return [e for e in FAQ if e.get("chunk_id", "").split("_")[0] in _GENERATED_PREFIXES]


@app.get("/admin/faqs")
def get_all_faqs():
    """Return all FAQ entries for the editor tool."""
    # video_* and related_links are included so an editor can show what a record
    # actually carries.  Without them a curator has no way to see -- let alone
    # remove -- a video attached to an answer, which is the one thing a rights
    # holder may ask for at any time.
    return [
        {
            "chunk_id": e.get("chunk_id", ""),
            "title": e.get("title", ""),
            "text": e.get("text", ""),
            "category": e.get("category", ""),
            "display_order": e.get("display_order"),
            "video_url": e.get("video_url", ""),
            "video_start": e.get("video_start"),
            "video_caption": e.get("video_caption", ""),
            "video_credit": e.get("video_credit", ""),
            "video_credit_url": e.get("video_credit_url", ""),
            "related_links": e.get("related_links") or [],
        }
        for e in FAQ
    ]


@app.get("/api/faq-categories")
def get_faq_categories():
    """Return FAQ categories in configured display order."""
    return _get_category_records()


@app.post("/admin/faq-categories")
async def create_faq_category(request: Request):
    payload = await request.json()
    title = (payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Category title is required")

    if any(record.get("title", "").strip().lower() == title.lower() for record in _get_category_records()):
        raise HTTPException(status_code=409, detail="A category with that title already exists")

    existing_orders = [int(entry.get("sort_order") or 0) for entry in CATEGORIES]
    next_order = max(existing_orders) + 10 if existing_orders else len(_get_category_records()) * 10
    _materialize_category_record({"title": title, "description": payload.get("description") or ""}, next_order)
    _normalize_category_sort_orders()
    return _get_category_records()


@app.post("/admin/faq-categories/reorder")
async def reorder_faq_category(request: Request):
    payload = await request.json()
    records = _get_category_records()
    ordered_titles = payload.get("ordered_titles")

    if isinstance(ordered_titles, list):
        normalized_titles = [(title or "").strip() for title in ordered_titles]
        existing_titles = [record.get("title") for record in records]
        if sorted(normalized_titles) != sorted(existing_titles):
            raise HTTPException(status_code=400, detail="ordered_titles must contain every category exactly once")
        records_by_title = {record.get("title"): record for record in records}
        records = [records_by_title[title] for title in normalized_titles]
    else:
        title = (payload.get("title") or "").strip()
        direction = (payload.get("direction") or "").strip().lower()
        if not title or direction not in {"up", "down"}:
            raise HTTPException(status_code=400, detail="Provide ordered_titles or title and direction")

        index = next((i for i, record in enumerate(records) if record.get("title") == title), None)
        if index is None:
            raise HTTPException(status_code=404, detail="Category not found")

        target_index = index - 1 if direction == "up" else index + 1
        if target_index < 0 or target_index >= len(records):
            return records

        records[index], records[target_index] = records[target_index], records[index]

    for order, record in enumerate(records):
        _materialize_category_record(record, order * 10)
    _save_categories_corpus()
    return _get_category_records()


@app.put("/admin/faq-categories/rename")
async def rename_faq_category(request: Request):
    payload = await request.json()
    old_title = (payload.get("old_title") or "").strip()
    new_title = (payload.get("new_title") or "").strip()
    if not old_title or not new_title:
        raise HTTPException(status_code=400, detail="old_title and new_title are required")

    if old_title == new_title:
        return _get_category_records()

    records = _get_category_records()
    existing = next((record for record in records if record.get("title") == old_title), None)
    if existing is None:
        raise HTTPException(status_code=404, detail="Category not found")

    if any(record.get("title", "").strip().lower() == new_title.lower() and record.get("title") != old_title for record in records):
        raise HTTPException(status_code=409, detail="A category with that title already exists")

    updated_any_faq = False
    for entry in FAQ:
        if (entry.get("category") or "").strip() == old_title:
            entry["category"] = new_title
            updated_any_faq = True

    entry = _find_category_entry(old_title)
    if entry is None:
        entry = _materialize_category_record(existing, int(existing.get("sort_order") or 0))

    entry["title"] = new_title
    entry["slug"] = _make_slug(new_title)
    entry["description"] = existing.get("description") or entry.get("description") or ""
    entry["text"] = _category_text(new_title, entry.get("description") or "")
    entry["display_citation"] = f"SubmarineDocent FAQ Category — {new_title}"

    if updated_any_faq:
        _save_faq_corpus()
    _normalize_category_sort_orders()
    return _get_category_records()


@app.delete("/admin/faq-categories")
async def delete_faq_category(request: Request):
    payload = await request.json()
    title = (payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Category title is required")

    original_len = len(CATEGORIES)
    CATEGORIES[:] = [entry for entry in CATEGORIES if (entry.get("title") or entry.get("name") or "").strip() != title]
    found = len(CATEGORIES) < original_len

    updated_any_faq = False
    for entry in FAQ:
        if (entry.get("category") or "").strip() == title:
            entry["category"] = ""
            updated_any_faq = True

    if not found and not updated_any_faq:
        raise HTTPException(status_code=404, detail="Category not found")

    if updated_any_faq:
        _save_faq_corpus()
    _normalize_category_sort_orders()
    return _get_category_records()


@app.get("/api/glossary")
def get_public_glossary():
    entries = list(_load_glossary())
    entries.sort(key=lambda entry: _glossary_sort_key(entry.get("term", "")))
    return entries


@app.get("/admin/glossary")
def get_admin_glossary():
    entries = list(_load_glossary())
    entries.sort(key=lambda entry: _glossary_sort_key(entry.get("term", "")))
    return entries


@app.post("/admin/glossary")
async def create_admin_glossary(request: Request):
    payload = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    if not isinstance(payload, dict):
        payload = {}

    entries = _load_glossary()
    new_entry = {
        "id": _next_glossary_id(entries),
        "term": "",
        "definition": "",
    }
    _apply_glossary_payload(new_entry, payload)

    with _glossary_write_lock:
        _assert_unique_glossary_term(entries, new_entry["term"])
        entries.append(new_entry)
        entries.sort(key=lambda entry: _glossary_sort_key(entry.get("term", "")))
        _save_glossary()

    return {"status": "created", "entry": new_entry}


@app.put("/admin/glossary/{entry_id}")
async def update_admin_glossary(entry_id: int, request: Request):
    payload = await request.json()
    entries = _load_glossary()
    target = next((entry for entry in entries if int(entry.get("id") or 0) == entry_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Glossary entry not found")

    with _glossary_write_lock:
        _apply_glossary_payload(target, payload)
        _assert_unique_glossary_term(entries, target["term"], ignore_id=entry_id)
        entries.sort(key=lambda entry: _glossary_sort_key(entry.get("term", "")))
        _save_glossary()

    return {"status": "updated", "entry": target}


@app.delete("/admin/glossary/{entry_id}")
def delete_admin_glossary(entry_id: int):
    entries = _load_glossary()
    target = next((entry for entry in entries if int(entry.get("id") or 0) == entry_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Glossary entry not found")

    with _glossary_write_lock:
        entries[:] = [entry for entry in entries if int(entry.get("id") or 0) != entry_id]
        _save_glossary()

    return {"status": "deleted", "entry_id": entry_id}


@app.get("/admin/incidents")
def get_admin_incidents():
    incidents = list(_load_incidents())
    incidents.sort(key=_incident_sort_key)
    return incidents


@app.post("/admin/incidents")
async def create_admin_incident(request: Request):
    payload = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    if not isinstance(payload, dict):
        payload = {}

    incidents = _load_incidents()
    new_incident = {
        "id": _next_incident_id(incidents),
        "date": "",
        "date_sort": "",
        "submarine_name": "",
        "hull_number": "",
        "incident_type": "",
        "description": "",
        "casualties": "",
        "status": "",
        "era": "",
        "notes": "",
    }
    _apply_incident_payload(new_incident, payload)

    with _incidents_write_lock:
        incidents.append(new_incident)
        incidents.sort(key=_incident_sort_key)
        _save_incidents()

    return {"status": "created", "incident": new_incident}


@app.put("/admin/incidents/{incident_id}")
async def update_admin_incident(incident_id: int, request: Request):
    payload = await request.json()
    incidents = _load_incidents()
    target = next((incident for incident in incidents if int(incident.get("id") or 0) == incident_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    with _incidents_write_lock:
        _apply_incident_payload(target, payload)
        incidents.sort(key=_incident_sort_key)
        _save_incidents()

    return {"status": "updated", "incident": target}


@app.delete("/admin/incidents/{incident_id}")
def delete_admin_incident(incident_id: int):
    incidents = _load_incidents()
    target = next((incident for incident in incidents if int(incident.get("id") or 0) == incident_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    with _incidents_write_lock:
        incidents[:] = [incident for incident in incidents if int(incident.get("id") or 0) != incident_id]
        _save_incidents()

    return {"status": "deleted", "incident_id": incident_id}


@app.get("/admin/operations-guide")
def get_admin_operations_guide():
    entries = list(OPERATIONS_GUIDE)
    entries.sort(key=_operations_guide_sort_key)
    return entries


@app.post("/admin/operations-guide")
async def create_admin_operations_guide_entry(request: Request):
    payload = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    if not isinstance(payload, dict):
        payload = {}

    new_entry = {
        "chunk_id": _next_operations_guide_chunk_id(OPERATIONS_GUIDE),
        "doc_type": "dieselsubs_operations_guide",
        "section": "custom",
        "title": "",
        "text": "",
        "display_citation": "",
        "source_url": "/web/faqs.html?view=operations",
    }
    _apply_operations_guide_payload(new_entry, payload)

    with _operations_guide_write_lock:
        OPERATIONS_GUIDE.append(new_entry)
        OPERATIONS_GUIDE.sort(key=_operations_guide_sort_key)
        _save_operations_guide()

    return {"status": "created", "entry": new_entry}


@app.put("/admin/operations-guide/{chunk_id}")
async def update_admin_operations_guide_entry(chunk_id: str, request: Request):
    payload = await request.json()
    target = next((entry for entry in OPERATIONS_GUIDE if str(entry.get("chunk_id") or "") == chunk_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Operations guide entry not found")

    with _operations_guide_write_lock:
        _apply_operations_guide_payload(target, payload)
        OPERATIONS_GUIDE.sort(key=_operations_guide_sort_key)
        _save_operations_guide()

    return {"status": "updated", "entry": target}


@app.delete("/admin/operations-guide/{chunk_id}")
def delete_admin_operations_guide_entry(chunk_id: str):
    target = next((entry for entry in OPERATIONS_GUIDE if str(entry.get("chunk_id") or "") == chunk_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Operations guide entry not found")

    with _operations_guide_write_lock:
        OPERATIONS_GUIDE[:] = [entry for entry in OPERATIONS_GUIDE if str(entry.get("chunk_id") or "") != chunk_id]
        _save_operations_guide()

    return {"status": "deleted", "chunk_id": chunk_id}


# ── Eternal Patrol ────────────────────────────────────────────────────────────

_ETERNAL_PATROL_PATH = os.path.join(CORPORA_DIR, "eternal_patrol.jsonl")
_eternal_patrol_cache: list | None = None


def _boat_number_sort_key(value: str) -> tuple[int, str]:
    raw = (value or "").strip().upper()
    match = re.search(r"(\d+)", raw)
    if match:
        return (int(match.group(1)), raw)
    return (10**9, raw)


def _slugify_filename_part(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", ascii_value).strip("_")
    return slug or "boat"


def _safe_image_extension(filename: str, content_type: str | None) -> str:
    extension = os.path.splitext(filename or "")[1].lower()
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    if extension in allowed:
        return ".jpg" if extension == ".jpeg" else extension
    by_content_type = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    guessed = by_content_type.get((content_type or "").lower())
    if guessed:
        return guessed
    raise HTTPException(status_code=400, detail="Unsupported image type")


def _build_eternal_patrol_image_name(boat: dict[str, Any], field_name: str, extension: str) -> str:
    designation = _slugify_filename_part(boat.get("designation") or boat.get("boat_number") or boat.get("name") or "boat")
    suffix_map = {
        "photo_boat": "boat",
        "photo_captain": "captain",
        "image1": "extra1",
        "image2": "extra2",
        "image3": "extra3",
        "image4": "extra4",
    }
    suffix = suffix_map.get(field_name)
    if not suffix:
        raise HTTPException(status_code=400, detail="Unsupported image field")
    return f"{designation}_{suffix}{extension}"


def _next_eternal_patrol_id(boats: list[dict[str, Any]]) -> int:
    max_id = 0
    for boat in boats:
        try:
            max_id = max(max_id, int(boat.get("id") or 0))
        except (TypeError, ValueError):
            continue
    return max_id + 1


def _derive_eternal_patrol_era(boat: dict[str, Any]) -> str:
    raw_sort = str(boat.get("date_lost_sort") or "").strip()
    raw_date = str(boat.get("date_lost") or "").strip()
    year_match = re.search(r"(\d{4})", raw_sort) or re.search(r"(\d{4})", raw_date)
    if not year_match:
        return str(boat.get("era") or "unknown").strip() or "unknown"

    year = int(year_match.group(1))
    if year < 1941:
        return "pre-wwii"
    if year <= 1945:
        return "wwii"
    return "post-wwii"


def _apply_eternal_patrol_payload(target: dict[str, Any], payload: dict[str, Any]) -> None:
    allowed_fields = {
        "boat_number",
        "name",
        "designation",
        "date_lost",
        "date_lost_sort",
        "fatalities_num",
        "fatalities_text",
        "last_captain",
        "location",
        "cause",
        "construction",
        "loss_narrative",
        "photo_boat",
        "photo_captain",
        "image1",
        "image1_subtitle",
        "image2",
        "image2_subtitle",
        "image3",
        "image3_subtitle",
        "image4",
        "image4_subtitle",
    }

    for field in allowed_fields:
        if field not in payload:
            continue
        value = payload.get(field)
        if field == "fatalities_num":
            if value in (None, ""):
                target[field] = None
            else:
                try:
                    target[field] = int(value)
                except (TypeError, ValueError):
                    raise HTTPException(status_code=400, detail="fatalities_num must be an integer")
        else:
            target[field] = (value or "").strip() if isinstance(value, str) else value

    target["era"] = _derive_eternal_patrol_era(target)


def _save_eternal_patrol() -> None:
    boats = _load_eternal_patrol()
    tmp = _ETERNAL_PATROL_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for entry in boats:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, _ETERNAL_PATROL_PATH)

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
                        boat = json.loads(line)
                        boat["era"] = _derive_eternal_patrol_era(boat)
                        boats.append(boat)
                    except json.JSONDecodeError:
                        pass
    boats.sort(key=lambda b: b.get("date_lost", ""))
    _eternal_patrol_cache = boats
    return boats


@app.get("/api/eternal-patrol")
def eternal_patrol():
    """Return all submarines on eternal patrol."""
    return _load_eternal_patrol()


@app.get("/admin/eternal-patrol")
def get_admin_eternal_patrol():
    boats = list(_load_eternal_patrol())
    boats.sort(key=lambda boat: _boat_number_sort_key(boat.get("boat_number", "")))
    return boats


@app.post("/admin/eternal-patrol")
async def create_admin_eternal_patrol(request: Request):
    payload = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    if not isinstance(payload, dict):
        payload = {}
    boats = _load_eternal_patrol()
    new_boat = {
        "id": _next_eternal_patrol_id(boats),
        "boat_number": "",
        "name": "",
        "designation": "",
        "date_lost": "",
        "date_lost_sort": "",
        "fatalities_num": None,
        "fatalities_text": "",
        "last_captain": "",
        "location": "",
        "cause": "",
        "construction": "",
        "loss_narrative": "",
        "photo_boat": None,
        "photo_captain": None,
        "era": "unknown",
        "image1": None,
        "image1_subtitle": None,
        "image2": None,
        "image2_subtitle": None,
        "image3": None,
        "image3_subtitle": None,
        "image4": None,
        "image4_subtitle": None,
    }
    _apply_eternal_patrol_payload(new_boat, payload)

    with _eternal_patrol_write_lock:
        boats.append(new_boat)
        _save_eternal_patrol()

    return {"status": "created", "boat": new_boat}


@app.put("/admin/eternal-patrol/{boat_id}")
async def update_admin_eternal_patrol(boat_id: int, request: Request):
    payload = await request.json()
    boats = _load_eternal_patrol()
    target = next((boat for boat in boats if int(boat.get("id") or 0) == boat_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Boat not found")

    with _eternal_patrol_write_lock:
        _apply_eternal_patrol_payload(target, payload)
        _save_eternal_patrol()

    return {"status": "updated", "boat": target}


@app.delete("/admin/eternal-patrol/{boat_id}")
def delete_admin_eternal_patrol(boat_id: int):
    boats = _load_eternal_patrol()
    target = next((boat for boat in boats if int(boat.get("id") or 0) == boat_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Boat not found")

    with _eternal_patrol_write_lock:
        boats[:] = [boat for boat in boats if int(boat.get("id") or 0) != boat_id]
        _save_eternal_patrol()

    return {"status": "deleted", "boat_id": boat_id}


@app.post("/admin/eternal-patrol/{boat_id}/upload-image")
async def upload_admin_eternal_patrol_image(
    boat_id: int,
    field_name: str = Form(...),
    image: UploadFile = File(...),
):
    allowed_fields = {"photo_boat", "photo_captain", "image1", "image2", "image3", "image4"}
    if field_name not in allowed_fields:
        raise HTTPException(status_code=400, detail="Unsupported image field")
    if not image.filename:
        raise HTTPException(status_code=400, detail="Image filename is required")

    boats = _load_eternal_patrol()
    target = next((boat for boat in boats if int(boat.get("id") or 0) == boat_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Boat not found")

    extension = _safe_image_extension(image.filename, image.content_type)
    os.makedirs(ETERNAL_PATROL_IMAGE_DIR, exist_ok=True)
    filename = _build_eternal_patrol_image_name(target, field_name, extension)
    destination = os.path.join(ETERNAL_PATROL_IMAGE_DIR, filename)

    try:
        with open(destination, "wb") as output_file:
            shutil.copyfileobj(image.file, output_file)
    finally:
        await image.close()

    relative_path = f"images/extracted/{filename}"
    with _eternal_patrol_write_lock:
        target[field_name] = relative_path
        _save_eternal_patrol()

    return {"status": "uploaded", "field_name": field_name, "path": relative_path, "boat": target}


@app.get("/api/faqs")
def public_faqs():
    """Return all published faq_ entries grouped by category, for the public FAQ page."""
    from collections import defaultdict

    def _display_order_key(entry: dict[str, Any]) -> tuple[int, int | str]:
        raw_order = entry.get("display_order")
        try:
            return (0, int(raw_order))
        except (TypeError, ValueError):
            return (1, entry.get("id", ""))

    groups: dict[str, list] = defaultdict(list)
    for e in FAQ:
        if not e.get("chunk_id", "").startswith("faq_"):
            continue
        title = e.get("title", "")
        # The stored ``text`` field holds the answer HTML only; the question is
        # kept separately in ``title``. Earlier code split ``text`` on the first
        # blank line and served only the part after it, on the assumption that
        # ``text`` was formatted "question\n\nanswer". Rich-editor / Word-pasted
        # answers legitimately contain blank lines, so that split silently
        # discarded the beginning of those answers for visitors (while the editor,
        # which reads the raw field, still showed them in full). Serve the whole
        # normalized answer.
        answer = _normalize_faq_html(e.get("text", ""))
        cat = e.get("category") or "General"
        groups[cat].append(
            {
                "id": e["chunk_id"],
                "title": title,
                "answer": answer,
                "video": _video_payload(e),
                "related_links": _related_links_payload(e),
                "display_order": e.get("display_order"),
            }
        )
    for cat, faqs in groups.items():
        groups[cat] = sorted(faqs, key=_display_order_key)
    ordered_categories = [entry["title"] for entry in _get_category_records() if entry.get("title") in groups]
    unordered_categories = sorted(cat for cat in groups.keys() if cat not in set(ordered_categories))
    return [{"category": cat, "faqs": groups[cat]} for cat in [*ordered_categories, *unordered_categories]]


# ── Videos storage ───────────────────────────────────────────────────────────
# Deliberately uncached: the file is small, and reading it per request means an
# edit through the admin screens shows on the public page immediately without a
# restart, which is how a curator expects a save to behave.
VIDEO_EDITABLE_FIELDS = (
    "title", "video_url", "video_start", "description",
    "video_credit", "video_credit_url", "rights_note", "category",
)
# Bucket for records with no category, matching what the FAQ grouping uses.
VIDEO_DEFAULT_CATEGORY = "General"


def _load_videos_raw() -> List[Dict[str, Any]]:
    return load_jsonl(VIDEOS_PATH)


def _save_videos(entries: List[Dict[str, Any]]) -> None:
    """Write the whole file atomically so a crash mid-write can't truncate it.

    load_jsonl stops at the first unparseable line, so a half-written file would
    silently drop every video after the break rather than erroring.
    """
    tmp_path = VIDEOS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp_path, VIDEOS_PATH)


def _next_video_id(entries: List[Dict[str, Any]]) -> str:
    max_n = 0
    for entry in entries:
        match = re.search(r"(\d+)$", str(entry.get("id") or ""))
        if match:
            max_n = max(max_n, int(match.group(1)))
    return f"vid_{max_n + 1:03d}"


def _apply_video_payload(target: Dict[str, Any], payload: Dict[str, Any]) -> None:
    """Copy the editable fields off a request body onto a record.

    video_url is validated here rather than only on read: an unusable URL should
    be refused at the point the curator can still fix it, not silently swallowed
    and then filtered out of the page with no explanation.
    """
    url = (payload.get("video_url") or "").strip()
    if not url:
        raise HTTPException(status_code=400, detail="video_url is required")
    if not _SAFE_LINK_SCHEME_RE.match(url):
        raise HTTPException(
            status_code=400,
            detail="video_url must start with http:// or https://",
        )
    target["video_url"] = url

    for field in ("title", "description", "video_credit", "video_credit_url",
                  "rights_note", "category"):
        if field in payload:
            target[field] = (payload.get(field) or "").strip()

    if "video_start" in payload:
        raw_start = payload.get("video_start")
        if raw_start in (None, ""):
            target.pop("video_start", None)
        else:
            try:
                target["video_start"] = max(0, int(raw_start))
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="video_start must be a whole number of seconds")

    if "display_order" in payload:
        raw_order = payload.get("display_order")
        if raw_order in (None, ""):
            target.pop("display_order", None)
        else:
            try:
                target["display_order"] = int(raw_order)
            except (TypeError, ValueError):
                raise HTTPException(status_code=400, detail="display_order must be a number")


@app.get("/admin/videos")
def get_admin_videos():
    """Return raw video records for the editor, unfiltered.

    Unlike /api/videos this keeps records the public page would drop, so a
    curator can see and repair a broken entry instead of wondering where it went.
    """
    return _load_videos_raw()


@app.post("/admin/videos")
async def create_admin_video(request: Request):
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    with _videos_write_lock:
        entries = _load_videos_raw()
        entry: Dict[str, Any] = {"id": _next_video_id(entries)}
        _apply_video_payload(entry, payload)
        entry.setdefault("display_order", len(entries) + 1)
        entries.append(entry)
        _save_videos(entries)
    return {"status": "created", "entry": entry}


@app.put("/admin/videos/{video_id}")
async def update_admin_video(video_id: str, request: Request):
    payload = await request.json()
    with _videos_write_lock:
        entries = _load_videos_raw()
        target = next((e for e in entries if str(e.get("id")) == video_id), None)
        if target is None:
            raise HTTPException(status_code=404, detail=f"{video_id} not found")
        _apply_video_payload(target, payload)
        _save_videos(entries)
    return {"status": "updated", "entry": target}


@app.delete("/admin/videos/{video_id}")
def delete_admin_video(video_id: str):
    with _videos_write_lock:
        entries = _load_videos_raw()
        remaining = [e for e in entries if str(e.get("id")) != video_id]
        if len(remaining) == len(entries):
            raise HTTPException(status_code=404, detail=f"{video_id} not found")
        _save_videos(remaining)
    return {"status": "deleted", "id": video_id}


@app.get("/api/videos")
def public_videos():
    """Return the curated videos, in display order, for the Videos page.

    Read per request rather than cached at import so editing videos.jsonl takes
    effect on refresh without a restart.  Only entries with a usable video_url
    are returned: this page exists to show video, and a record without one would
    render as a description with an empty frame above it.
    """
    def _order_key(entry: Dict[str, Any]) -> tuple[int, Any]:
        try:
            return (0, int(entry.get("display_order")))
        except (TypeError, ValueError):
            return (1, entry.get("id") or "")

    out: List[Dict[str, Any]] = []
    for entry in _load_videos_raw():
        video = _video_payload(entry)
        if not video:
            continue
        out.append({
            "id": entry.get("id") or "",
            "title": (entry.get("title") or "").strip(),
            "description": (entry.get("description") or "").strip(),
            # Why we are permitted to show this one — shown on the page so the
            # basis is visible rather than buried in a commit message.
            "rights_note": (entry.get("rights_note") or "").strip(),
            "category": (entry.get("category") or "").strip() or VIDEO_DEFAULT_CATEGORY,
            "video": video,
            "display_order": entry.get("display_order"),
        })
    out.sort(key=_order_key)

    # Grouped by category, mirroring the shape /api/faqs returns. There is no
    # separate category corpus for videos, so a category's position follows the
    # lowest display_order among its videos: ordering one video ahead of another
    # moves its section too, rather than needing a second thing to maintain.
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for item in out:
        groups.setdefault(item["category"], []).append(item)
    return [{"category": name, "videos": videos} for name, videos in groups.items()]


@app.get("/api/operations-guide")
def public_operations_guide():
    """Return the structured operations guide corpus used to build exports and derived experiences."""
    return list(OPERATIONS_GUIDE)


@app.get("/admin/operations-guide-html")
def get_operations_guide_html():
    """Return the current rendered HTML for the operations guide."""
    if not os.path.exists(OPERATIONS_GUIDE_SINGLE_HTML_PATH):
        return {"html": ""}
    with open(OPERATIONS_GUIDE_SINGLE_HTML_PATH, "r", encoding="utf-8") as f:
        line = f.read().strip()
    if not line:
        return {"html": ""}
    try:
        record = json.loads(line)
        raw = record.get("text", "")
        # Strip the outer wrapper div added by the builder
        raw = re.sub(r'^<div[^>]*id=["\']operations-view["\'][^>]*>', '', raw).rstrip()
        if raw.endswith("</div>"):
            raw = raw[:-6]
        return {"html": raw.strip()}
    except Exception:
        return {"html": ""}


@app.put("/admin/operations-guide-html")
async def update_operations_guide_html(request: Request):
    """Save edited HTML directly to the single-record file."""
    body = await request.json()
    body_html = (body.get("html") or "").strip()
    record = {
        "chunk_id": "ops_html_001",
        "doc_type": "dieselsubs_operations_guide_html",
        "source": "Submarine Operations Guide",
        "title": "Submarine Operations",
        "slug": "submarine-operations",
        "category": "Operations Guide",
        "text": f'<div id="operations-view">{body_html}</div>',
        "display_citation": "Operations Guide — Submarine Operations",
        "source_url": "/web/faqs.html?view=operations",
    }
    tmp = OPERATIONS_GUIDE_SINGLE_HTML_PATH + ".tmp"
    with _operations_guide_write_lock:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        os.replace(tmp, OPERATIONS_GUIDE_SINGLE_HTML_PATH)
    return {"status": "saved"}


@app.post("/admin/faq")
async def create_faq(request: Request):
    """Create a new faq_NNN entry from a simple title + text payload."""
    body = await request.json()
    title = (body.get("title") or "").strip()
    text = _normalize_faq_html((body.get("text") or "").strip())
    category = (body.get("category") or "").strip()
    if not title or not text:
        raise HTTPException(status_code=400, detail="title and text are required")
    with _faq_write_lock:
        with _category_write_lock:
            _ensure_category_exists(category)
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
    text = _normalize_faq_html((body.get("text") or "").strip())
    entry = next((e for e in FAQ if e.get("chunk_id") == chunk_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail=f"{chunk_id} not found")
    with _faq_write_lock:
        with _category_write_lock:
            if "category" in body:
                _ensure_category_exists(body.get("category") or "")
        if title:
            entry["title"] = title
        if text:
            entry["text"] = text
        if "category" in body:
            entry["category"] = (body.get("category") or "").strip()
        # Only touched when the caller sends the key, so an ordinary title/text
        # save from the editor can't silently drop a record's links.  Stored
        # through the same validator that serves them, so an unsafe URL is
        # rejected at write time rather than persisting and being filtered on
        # every later read.  An empty list clears them.
        if "related_links" in body:
            entry["related_links"] = _related_links_payload(
                {"related_links": body.get("related_links")}
            )
        # Same contract as related_links: only touched when the key is sent, so
        # an ordinary text save can't strip a record's video.  Sending an empty
        # video_url clears the whole attachment rather than leaving orphaned
        # caption and credit fields behind.
        if "video_url" in body:
            video_url = (body.get("video_url") or "").strip()
            if not video_url:
                for field in ("video_url", "video_start", "video_caption",
                              "video_credit", "video_credit_url"):
                    entry.pop(field, None)
            elif not _SAFE_LINK_SCHEME_RE.match(video_url):
                raise HTTPException(
                    status_code=400,
                    detail="video_url must start with http:// or https://",
                )
            else:
                entry["video_url"] = video_url
                for field in ("video_caption", "video_credit", "video_credit_url"):
                    if field in body:
                        entry[field] = (body.get(field) or "").strip()
                if "video_start" in body:
                    raw_start = body.get("video_start")
                    if raw_start in (None, ""):
                        entry.pop("video_start", None)
                    else:
                        try:
                            entry["video_start"] = max(0, int(raw_start))
                        except (TypeError, ValueError):
                            raise HTTPException(
                                status_code=400,
                                detail="video_start must be a whole number of seconds",
                            )
        _save_faq_corpus()
    return {"status": "saved", "chunk_id": chunk_id}


@app.post("/admin/faqs/reorder")
async def reorder_faqs(request: Request):
    """Persist the display order of FAQs within a category.

    Body: {"category": str, "ordered_ids": [chunk_id, ...]}. Assigns
    display_order in steps of 10 following the given order; FAQs not listed
    are left untouched.
    """
    payload = await request.json()
    ordered_ids = payload.get("ordered_ids")
    if not isinstance(ordered_ids, list):
        raise HTTPException(status_code=400, detail="ordered_ids must be a list")
    with _faq_write_lock:
        entries_by_id = {e.get("chunk_id"): e for e in FAQ}
        order = 0
        for chunk_id in ordered_ids:
            entry = entries_by_id.get(chunk_id)
            if entry is None:
                continue
            entry["display_order"] = order
            order += 10
        _save_faq_corpus()
    return {"status": "saved"}


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
    """Permanently remove a FAQ entry from the corpus.

    Allows deleting both generated (der_/pam_/fix_) entries and the curated
    faq_ entries shown in the per-category editor, whose "Delete entry" button
    targets this endpoint.
    """
    if chunk_id.split("_")[0] not in (_GENERATED_PREFIXES | {"faq"}):
        raise HTTPException(status_code=400, detail="Only der_, pam_, fix_, faq_ entries can be deleted")
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
# Medal of Honor recipients
# ------------------------------------------------------------

_MOH_PATH = os.path.join(CORPORA_DIR, "moh_recipients.jsonl")
_moh_cache: list | None = None
_moh_write_lock = threading.Lock()


def _load_moh() -> list:
    global _moh_cache
    if _moh_cache is not None:
        return _moh_cache
    entries = []
    if os.path.exists(_MOH_PATH):
        with open(_MOH_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except Exception:
                        pass
    _moh_cache = entries
    return entries


def _save_moh() -> None:
    entries = _load_moh()
    tmp = _MOH_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, _MOH_PATH)


def _next_moh_id(entries: list) -> int:
    existing = [int(e.get("id") or 0) for e in entries]
    return max(existing) + 1 if existing else 1


@app.get("/api/moh-recipients")
def get_moh_recipients():
    return _load_moh()


@app.post("/admin/moh-recipients")
async def create_moh_recipient(request: Request):
    body = await request.json()
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    entries = _load_moh()
    new_entry = {
        "id": _next_moh_id(entries),
        "name": name,
        "rank_unit": (body.get("rank_unit") or "").strip(),
        "date_awarded": (body.get("date_awarded") or "").strip(),
        "posthumous": bool(body.get("posthumous")),
        "citation_summary": (body.get("citation_summary") or "").strip(),
    }
    with _moh_write_lock:
        entries.append(new_entry)
        _save_moh()
    return {"status": "created", "entry": new_entry}


@app.put("/admin/moh-recipients/{entry_id}")
async def update_moh_recipient(entry_id: int, request: Request):
    entries = _load_moh()
    target = next((e for e in entries if int(e.get("id") or 0) == entry_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Recipient not found")
    body = await request.json()
    with _moh_write_lock:
        for field in ("name", "rank_unit", "date_awarded", "citation_summary"):
            if field in body:
                target[field] = (body[field] or "").strip()
        if "posthumous" in body:
            target["posthumous"] = bool(body["posthumous"])
        _save_moh()
    return {"status": "updated", "entry": target}


@app.delete("/admin/moh-recipients/{entry_id}")
def delete_moh_recipient(entry_id: int):
    entries = _load_moh()
    original_len = len(entries)
    entries[:] = [e for e in entries if int(e.get("id") or 0) != entry_id]
    if len(entries) == original_len:
        raise HTTPException(status_code=404, detail="Recipient not found")
    with _moh_write_lock:
        _save_moh()
    return {"status": "deleted", "entry_id": entry_id}


# ------------------------------------------------------------
# Museums
# ------------------------------------------------------------

_MUSEUMS_PATH = _editable_corpus_path("museums.jsonl")
_museums_cache: list | None = None
_museums_write_lock = threading.Lock()


def _load_museums() -> list:
    global _museums_cache
    if _museums_cache is not None:
        return _museums_cache
    museums = []
    if os.path.exists(_MUSEUMS_PATH):
        with open(_MUSEUMS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        museums.append(json.loads(line))
                    except Exception:
                        pass
    _museums_cache = museums
    return museums


def _save_museums() -> None:
    museums = _load_museums()
    tmp = _MUSEUMS_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for entry in museums:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    os.replace(tmp, _MUSEUMS_PATH)


def _next_museum_id(museums: list) -> int:
    existing = [int(m.get("id") or 0) for m in museums]
    return max(existing) + 1 if existing else 1


@app.get("/api/museums")
def get_museums():
    return _load_museums()


@app.post("/admin/museums")
async def create_museum(request: Request):
    body = await request.json()
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    museums = _load_museums()
    new_entry = {
        "id": _next_museum_id(museums),
        "name": name,
        "designation": (body.get("designation") or "").strip(),
        "location": (body.get("location") or "").strip(),
        "url": (body.get("url") or "").strip(),
        "description": (body.get("description") or "").strip(),
    }
    with _museums_write_lock:
        museums.append(new_entry)
        _save_museums()
    return {"status": "created", "museum": new_entry}


@app.put("/admin/museums/{museum_id}")
async def update_museum(museum_id: int, request: Request):
    museums = _load_museums()
    target = next((m for m in museums if int(m.get("id") or 0) == museum_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Museum not found")
    body = await request.json()
    with _museums_write_lock:
        for field in ("name", "designation", "location", "url", "description"):
            if field in body:
                target[field] = (body[field] or "").strip()
        _save_museums()
    return {"status": "updated", "museum": target}


@app.delete("/admin/museums/{museum_id}")
def delete_museum(museum_id: int):
    museums = _load_museums()
    original_len = len(museums)
    museums[:] = [m for m in museums if int(m.get("id") or 0) != museum_id]
    if len(museums) == original_len:
        raise HTTPException(status_code=404, detail="Museum not found")
    with _museums_write_lock:
        _save_museums()
    return {"status": "deleted", "museum_id": museum_id}


# ------------------------------------------------------------
# Museum sub-pages (managed by museum admin)
# ------------------------------------------------------------

_MUSEUM_PAGES_PATH = _editable_corpus_path("museum_pages.jsonl")
_MUSEUM_UPLOADS_DIR = _editable_corpus_dir("museum_uploads")
_MUSEUM_UPLOAD_ALLOWED_EXTS = {
    ".html", ".htm",
    ".doc", ".docx",
    ".xls", ".xlsx",
    ".ppt", ".pptx",
    ".pdf", ".txt", ".md", ".rtf", ".odt",
}
_MUSEUM_UPLOAD_MAX_BYTES = 25 * 1024 * 1024  # 25 MB per file
_museum_pages_cache: list | None = None
_museum_pages_write_lock = threading.Lock()

os.makedirs(_MUSEUM_UPLOADS_DIR, exist_ok=True)
app.mount(
    "/museum_uploads",
    StaticFiles(directory=_MUSEUM_UPLOADS_DIR),
    name="museum_uploads",
)

# ── FAQ answer attachments (images + documents embedded in FAQ answers) ──────
_FAQ_UPLOADS_DIR = _editable_corpus_dir("faq_uploads")
_FAQ_UPLOAD_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
_FAQ_UPLOAD_ALLOWED_EXTS = _FAQ_UPLOAD_IMAGE_EXTS | {
    ".pdf", ".txt", ".md", ".rtf",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt",
}
_FAQ_UPLOAD_MAX_BYTES = 25 * 1024 * 1024  # 25 MB per file

os.makedirs(_FAQ_UPLOADS_DIR, exist_ok=True)
app.mount(
    "/faq_uploads",
    StaticFiles(directory=_FAQ_UPLOADS_DIR),
    name="faq_uploads",
)


@app.post("/admin/faq-uploads")
async def upload_faq_attachment(file: UploadFile = File(...)):
    """Store a file referenced from a FAQ answer and return its public URL."""
    orig_name = _sanitize_upload_name(file.filename or "")
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in _FAQ_UPLOAD_ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"File type {ext or '(none)'} is not allowed")

    stored_name = f"{uuid.uuid4().hex[:8]}_{orig_name}"
    dest_path = os.path.join(_FAQ_UPLOADS_DIR, stored_name)

    total = 0
    try:
        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > _FAQ_UPLOAD_MAX_BYTES:
                    out.close()
                    os.remove(dest_path)
                    raise HTTPException(status_code=413, detail="File exceeds 25 MB limit")
                out.write(chunk)
    finally:
        await file.close()

    result = {
        "status": "uploaded",
        "filename": orig_name,
        "url": f"/faq_uploads/{stored_name}",
        "content_type": file.content_type or "application/octet-stream",
        "size": total,
        "is_image": ext in _FAQ_UPLOAD_IMAGE_EXTS,
    }

    # Word documents: convert to inline HTML so the content lands in the answer
    # body. Falls back to a download link if conversion fails or mammoth is absent.
    if ext == ".docx":
        try:
            import mammoth
            with open(dest_path, "rb") as docx_in:
                conversion = mammoth.convert_to_html(docx_in)
            html_out = (conversion.value or "").strip()
            if html_out:
                result["is_docx"] = True
                result["html"] = html_out
        except Exception as e:
            print(f"[faq-upload] docx conversion failed for {orig_name}: {e}")

    return result


def _load_museum_pages() -> list:
    global _museum_pages_cache
    if _museum_pages_cache is not None:
        return _museum_pages_cache
    pages = []
    if os.path.exists(_MUSEUM_PAGES_PATH):
        with open(_MUSEUM_PAGES_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        pages.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    _museum_pages_cache = pages
    return pages


def _save_museum_pages() -> None:
    pages = _load_museum_pages()
    os.makedirs(os.path.dirname(_MUSEUM_PAGES_PATH), exist_ok=True)
    with open(_MUSEUM_PAGES_PATH, "w", encoding="utf-8") as f:
        for entry in pages:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _next_museum_page_id(pages: list) -> int:
    existing = [int(p.get("id") or 0) for p in pages]
    return (max(existing) + 1) if existing else 1


def _museum_exists(museum_id: int) -> bool:
    return any(int(m.get("id") or 0) == museum_id for m in _load_museums())


@app.get("/api/museums/{museum_id}/pages")
def get_museum_pages(museum_id: int):
    if not _museum_exists(museum_id):
        raise HTTPException(status_code=404, detail="Museum not found")
    return [p for p in _load_museum_pages() if int(p.get("museum_id") or 0) == museum_id]


def _coerce_parent_id(value, museum_id: int, pages: list, self_id: int | None = None) -> int | None:
    if value in (None, "", 0, "0"):
        return None
    try:
        parent_id = int(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="parent_page_id must be an integer or null")
    parent = next((p for p in pages if int(p.get("id") or 0) == parent_id), None)
    if parent is None:
        raise HTTPException(status_code=404, detail="Parent page not found")
    if int(parent.get("museum_id") or 0) != museum_id:
        raise HTTPException(status_code=400, detail="Parent page belongs to a different museum")
    if self_id is not None:
        ancestor = parent
        while ancestor is not None:
            if int(ancestor.get("id") or 0) == self_id:
                raise HTTPException(status_code=400, detail="Cannot set parent to self or a descendant")
            pid = ancestor.get("parent_page_id")
            ancestor = next((p for p in pages if int(p.get("id") or 0) == (pid or 0)), None) if pid else None
    return parent_id


@app.post("/admin/museum_pages")
async def create_museum_page(request: Request):
    body = await request.json()
    try:
        museum_id = int(body.get("museum_id"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="museum_id is required")
    if not _museum_exists(museum_id):
        raise HTTPException(status_code=404, detail="Museum not found")
    title = (body.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="title is required")
    pages = _load_museum_pages()
    parent_page_id = _coerce_parent_id(body.get("parent_page_id"), museum_id, pages)
    new_entry = {
        "id": _next_museum_page_id(pages),
        "museum_id": museum_id,
        "parent_page_id": parent_page_id,
        "title": title,
        "description": (body.get("description") or "").strip(),
        "is_faq": bool(body.get("is_faq")),
        "content": (body.get("content") or "").strip(),
        "attachments": [],
    }
    with _museum_pages_write_lock:
        pages.append(new_entry)
        _save_museum_pages()
    return {"status": "created", "page": new_entry}


@app.put("/admin/museum_pages/{page_id}")
async def update_museum_page(page_id: int, request: Request):
    pages = _load_museum_pages()
    target = next((p for p in pages if int(p.get("id") or 0) == page_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Page not found")
    body = await request.json()
    with _museum_pages_write_lock:
        if "title" in body:
            target["title"] = (body["title"] or "").strip()
        if "description" in body:
            target["description"] = (body["description"] or "").strip()
        if "is_faq" in body:
            target["is_faq"] = bool(body["is_faq"])
        if "content" in body:
            target["content"] = (body["content"] or "").strip()
        if "parent_page_id" in body:
            target["parent_page_id"] = _coerce_parent_id(
                body["parent_page_id"], int(target["museum_id"]), pages, self_id=page_id
            )
        _save_museum_pages()
    return {"status": "updated", "page": target}


@app.delete("/admin/museum_pages/{page_id}")
def delete_museum_page(page_id: int):
    pages = _load_museum_pages()
    to_delete = {page_id}
    changed = True
    while changed:
        changed = False
        for p in pages:
            pid = int(p.get("id") or 0)
            parent = p.get("parent_page_id")
            if parent and int(parent) in to_delete and pid not in to_delete:
                to_delete.add(pid)
                changed = True
    original_len = len(pages)
    pages[:] = [p for p in pages if int(p.get("id") or 0) not in to_delete]
    if len(pages) == original_len:
        raise HTTPException(status_code=404, detail="Page not found")
    with _museum_pages_write_lock:
        _save_museum_pages()
    for pid in to_delete:
        shutil.rmtree(os.path.join(_MUSEUM_UPLOADS_DIR, str(pid)), ignore_errors=True)
    return {"status": "deleted", "page_ids": sorted(to_delete)}


def _sanitize_upload_name(name: str) -> str:
    stem, ext = os.path.splitext(os.path.basename(name or ""))
    stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._") or "file"
    return (stem + ext.lower())[:120]


def _next_attachment_id(attachments: list) -> int:
    existing = [int(a.get("id") or 0) for a in attachments]
    return (max(existing) + 1) if existing else 1


@app.post("/admin/museum_pages/{page_id}/uploads")
async def upload_museum_page_attachment(page_id: int, file: UploadFile = File(...)):
    pages = _load_museum_pages()
    target = next((p for p in pages if int(p.get("id") or 0) == page_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Page not found")

    orig_name = _sanitize_upload_name(file.filename or "")
    ext = os.path.splitext(orig_name)[1].lower()
    if ext not in _MUSEUM_UPLOAD_ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail=f"File type {ext or '(none)'} is not allowed")

    page_dir = os.path.join(_MUSEUM_UPLOADS_DIR, str(page_id))
    os.makedirs(page_dir, exist_ok=True)

    attachments = list(target.get("attachments") or [])
    attachment_id = _next_attachment_id(attachments)
    stored_name = f"{attachment_id}_{orig_name}"
    dest_path = os.path.join(page_dir, stored_name)

    total = 0
    try:
        with open(dest_path, "wb") as out:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > _MUSEUM_UPLOAD_MAX_BYTES:
                    out.close()
                    os.remove(dest_path)
                    raise HTTPException(status_code=413, detail="File exceeds 25 MB limit")
                out.write(chunk)
    finally:
        await file.close()

    entry = {
        "id": attachment_id,
        "filename": orig_name,
        "stored_name": stored_name,
        "content_type": file.content_type or "application/octet-stream",
        "size": total,
        "url": f"/museum_uploads/{page_id}/{stored_name}",
    }
    with _museum_pages_write_lock:
        attachments.append(entry)
        target["attachments"] = attachments
        _save_museum_pages()
    return {"status": "uploaded", "attachment": entry}


@app.delete("/admin/museum_pages/{page_id}/uploads/{attachment_id}")
def delete_museum_page_attachment(page_id: int, attachment_id: int):
    pages = _load_museum_pages()
    target = next((p for p in pages if int(p.get("id") or 0) == page_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Page not found")
    attachments = list(target.get("attachments") or [])
    match = next((a for a in attachments if int(a.get("id") or 0) == attachment_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail="Attachment not found")
    stored = match.get("stored_name")
    if stored:
        try:
            os.remove(os.path.join(_MUSEUM_UPLOADS_DIR, str(page_id), stored))
        except FileNotFoundError:
            pass
    with _museum_pages_write_lock:
        target["attachments"] = [a for a in attachments if int(a.get("id") or 0) != attachment_id]
        _save_museum_pages()
    return {"status": "deleted", "attachment_id": attachment_id}


# ------------------------------------------------------------
# Feedback endpoint
# ------------------------------------------------------------

FEEDBACK_PATH = os.path.join(BASE_DIR, "feedback.jsonl")

@app.post("/feedback")
def receive_feedback(payload: dict):
    import datetime
    source = (payload.get("source") or "tour").strip()
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "source": source,                         # "tour" | "contact"
        "question": (payload.get("question") or "").strip(),
        "answer": (payload.get("answer") or "").strip(),
        "rating": payload.get("rating"),          # "up" | "down" | null
        "comment": (payload.get("comment") or "").strip(),
    }
    if source == "contact":
        # Free-form visitor message from the public contact form.
        entry["name"] = (payload.get("name") or "").strip()
        entry["email"] = (payload.get("email") or "").strip()
        entry["message"] = (payload.get("message") or "").strip()
    try:
        with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[feedback] write error: {e}")
    if source == "contact":
        print(f"[feedback] contact from {entry.get('email') or 'anon'} — {entry['message'][:80]}")
    else:
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
# Admin: Whisper domain vocabulary prompt
# ------------------------------------------------------------

@app.get("/admin/whisper-prompt")
def get_whisper_prompt():
    return {"prompt": _WHISPER_PROMPT}


@app.put("/admin/whisper-prompt")
async def update_whisper_prompt(request: Request):
    global _WHISPER_PROMPT
    payload = await request.json()
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt must not be empty")
    with _whisper_prompt_lock:
        with open(_WHISPER_PROMPT_PATH, "w", encoding="utf-8") as f:
            f.write(prompt)
        _WHISPER_PROMPT = prompt
    return {"status": "updated"}


# ------------------------------------------------------------
# Admin: War Patrol HTML pages
# ------------------------------------------------------------

_PATROL_ORDINALS = ["First", "Second", "Third", "Fourth", "Fifth"]
_patrol_write_lock = threading.Lock()
_PATROL_BODY_START = "<!-- PATROL-BODY-START -->"
_PATROL_BODY_END = "<!-- PATROL-BODY-END -->"


def _patrol_page_path(n: int) -> str:
    return os.path.join(WEB_DIR, f"pampanito-patrol-{n}.html")


def _patrol_page_html(n: int, body_html: str) -> str:
    ordinal = _PATROL_ORDINALS[n - 1]
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>USS Pampanito \u2014 {ordinal} Patrol</title>
  <link rel="stylesheet" href="/web/site-header.css">
  <style>
    body {{
      margin: 0;
      font-family: ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0d1117;
      color: #e6edf3;
    }}
    .patrol-content {{
      max-width: 860px;
      margin: 0 auto;
      padding: 40px 24px 56px;
      line-height: 1.7;
    }}
    .patrol-content h1, .patrol-content h2, .patrol-content h3 {{
      font-weight: 700;
      line-height: 1.25;
    }}
    .patrol-content h1 {{ font-size: 28px; margin: 1.5em 0 0.5em; }}
    .patrol-content h2 {{ font-size: 22px; margin: 1.4em 0 0.4em; }}
    .patrol-content h3 {{ font-size: 18px; margin: 1.2em 0 0.4em; }}
    .patrol-content p {{ margin: 0 0 1em; }}
    .patrol-content ul, .patrol-content ol {{ padding-left: 1.5em; margin: 0 0 1em; }}
    .patrol-content blockquote {{
      border-left: 3px solid #30363d;
      margin: 0 0 1em;
      padding-left: 1em;
      color: #8b949e;
    }}
    .patrol-content table {{
      border-collapse: collapse;
      width: 100%;
      margin: 1em 0;
      font-size: 14px;
    }}
    .patrol-content th, .patrol-content td {{
      border: 1px solid #30363d;
      padding: 8px 12px;
      text-align: left;
    }}
    .patrol-content th {{ background: #161b22; font-weight: 600; }}
    .patrol-content a {{ color: #58a6ff; }}
  </style>
</head>
<body>
  <article class="patrol-content">
{_PATROL_BODY_START}
{body_html}
{_PATROL_BODY_END}
  </article>
  <script src="/web/site-footer.js"></script>
  <script src="/web/site-header.js"></script>
  <script>
    SiteFooter.render();
    SiteHeader.render({{
      title: '{ordinal} Patrol',
    }});
  </script>
</body>
</html>
"""


@app.get("/admin/patrol/{n}")
def get_patrol_content(n: int):
    if not 1 <= n <= 5:
        raise HTTPException(status_code=404, detail="Patrol number must be 1-5")
    path = _patrol_page_path(n)
    if not os.path.exists(path):
        return {"exists": False, "html": ""}
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    start = content.find(_PATROL_BODY_START)
    end = content.find(_PATROL_BODY_END)
    if start == -1 or end == -1:
        return {"exists": True, "html": content}
    body = content[start + len(_PATROL_BODY_START):end].strip()
    return {"exists": True, "html": body}


@app.put("/admin/patrol/{n}")
async def save_patrol_content(n: int, request: Request):
    if not 1 <= n <= 5:
        raise HTTPException(status_code=404, detail="Patrol number must be 1-5")
    body = await request.json()
    body_html = (body.get("html") or "").strip()
    page = _patrol_page_html(n, body_html)
    path = _patrol_page_path(n)
    tmp = path + ".tmp"
    with _patrol_write_lock:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(page)
        os.replace(tmp, path)
    return {"status": "saved", "patrol": n}


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