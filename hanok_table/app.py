"""FastAPI entrypoint: health, telemetry, Hanok Table dynamic webhooks, and static site."""

import logging
import os
from contextlib import asynccontextmanager
from html import escape
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from hanok_table.config import (
    admin_dashboard_token,
    convonet_voice_assistant_url,
    hanok_mcp_http_mount_enabled,
    hanok_mcp_http_mount_path,
    hanok_public_base_url,
    hanok_reservation_lab_enabled,
    hanok_table_voice_api_key,
    hanok_table_voice_connection_id,
)
from hanok_table.routers import admin, reservations, webhook

logger = logging.getLogger(__name__)

_STATIC = Path(__file__).resolve().parent / "static"
_INDEX = _STATIC / "index.html"
_RESERVE_ONLINE = _STATIC / "reserve_online.html"
_RESERVATION_STATUS = _STATIC / "reservation_status.html"
_RESERVATION_LAB = _STATIC / "reservation_lab.html"
_APP_REV = os.environ.get("RENDER_GIT_COMMIT", os.environ.get("APP_GIT_REVISION", "local"))


def _lifespan_startup(log: logging.Logger) -> None:
    """DB seed and boot warnings; runs inside root lifespan."""
    log.warning(
        "Hanok Table: rev=%s index_exists=%s app_py=%s",
        _APP_REV[:12] if _APP_REV else "?",
        _INDEX.is_file(),
        Path(__file__).resolve(),
    )
    if hanok_table_voice_api_key() and hanok_table_voice_connection_id() and not hanok_public_base_url():
        log.warning(
            "Set HANOK_PUBLIC_BASE_URL (https://your-host) so reminder dials send Call Control webhooks "
            "to /webhooks/hanok_table/call-control; otherwise answered calls may stay silent."
        )
    try:
        from hanok_table.db import SessionLocal, init_db
        from hanok_table.seed import seed_demo_reservations

        if init_db() and SessionLocal is not None:
            db = SessionLocal()
            try:
                n = seed_demo_reservations(db)
                if n:
                    log.warning("Seeded %s demo reservations (empty table)", n)
            except Exception:
                log.exception("Demo seed failed — check DB_URI and DB permissions")
            finally:
                db.close()
    except Exception:
        log.exception("Database startup skipped — app will run without Postgres until DB is reachable")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Log deploy fingerprint; DB seed; Streamable HTTP MCP task group when mounted."""
    log = logging.getLogger("uvicorn.error")
    _lifespan_startup(log)

    if hanok_mcp_http_mount_enabled():
        from hanok_table.mcp_server.server import mcp as _hanok_mcp

        # FastAPI does not run mounted Starlette sub-app lifespans; MCP requires session_manager.run().
        async with _hanok_mcp.session_manager.run():
            yield
    else:
        yield


app = FastAPI(
    title="Hanok Table Reservation API",
    description="REST API, dynamic webhooks, and MCP-backed tools for Hanok Table reservations.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(webhook.router, prefix="/webhooks/hanok_table", tags=["hanok_table"])
app.include_router(reservations.router)
app.include_router(admin.router)

if hanok_mcp_http_mount_enabled():
    from hanok_table.mcp_server.server import mcp as _hanok_mcp

    _hanok_mcp.settings.streamable_http_path = "/"
    app.mount(hanok_mcp_http_mount_path(), _hanok_mcp.streamable_http_app())

if _STATIC.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=_STATIC),
        name="assets",
    )


@app.get("/health")
@app.post("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _voice_cta_attributes() -> str:
    """Attributes for the Convonet WebRTC CTA: real link when env is set, else disabled stub."""
    url = convonet_voice_assistant_url()
    if url:
        safe = escape(url, quote=True)
        return f'href="{safe}" target="_blank" rel="noopener noreferrer"'
    return (
        'href="#" onclick="return false;" aria-disabled="true" '
        'style="opacity:0.72;cursor:not-allowed" '
        'title="Set CONVONET_VOICE_ASSISTANT_URL on this service (your call-center /voice_assistant URL)."'
    )


def _home_page_html() -> str:
    if not _INDEX.is_file():
        logger.error("Missing Hanok landing page: %s (static dir: %s)", _INDEX, _STATIC)
        return (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Setup</title></head>"
            "<body><h1>index.html not found</h1>"
            f"<p>Expected file at: <code>{_INDEX}</code></p>"
            "<p>Redeploy from GitHub so <code>hanok_table/static/index.html</code> is on the server.</p>"
            "</body></html>"
        )
    raw = _INDEX.read_text(encoding="utf-8")
    return raw.replace("__HANOK_VOICE_CTA_ATTRS__", _voice_cta_attributes())


@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
def serve_home() -> HTMLResponse:
    """Hanok Table landing page (EN/KO)."""
    return HTMLResponse(content=_home_page_html())


def _read_static_html(path: Path, label: str) -> HTMLResponse:
    if not path.is_file():
        logger.error("Missing static HTML: %s (%s)", path, label)
        return HTMLResponse(
            f"<!DOCTYPE html><html><body><h1>Missing {label}</h1><p>Expected <code>{path}</code></p></body></html>",
            status_code=404,
        )
    return HTMLResponse(content=path.read_text(encoding="utf-8"))


@app.get("/reserve-online", response_class=HTMLResponse)
@app.get("/reserve-online.html", response_class=HTMLResponse)
def serve_reserve_online() -> HTMLResponse:
    """Pre-order form, 7% food discount, posts to REST API."""
    return _read_static_html(_RESERVE_ONLINE, "reserve_online.html")


@app.get("/reservation/status", response_class=HTMLResponse)
@app.get("/reservation-status.html", response_class=HTMLResponse)
def serve_reservation_status() -> HTMLResponse:
    """Guest-facing status & food totals (confirmation code)."""
    return _read_static_html(_RESERVATION_STATUS, "reservation_status.html")


@app.get("/reservation-lab", response_class=HTMLResponse)
@app.get("/reservation-lab.html", response_class=HTMLResponse)
def serve_reservation_lab(
    token: str | None = Query(None, description="Must match ADMIN_DASHBOARD_TOKEN when that env is set."),
) -> HTMLResponse:
    """Optional browser UI: create / lookup / amend / canned scenarios (dev & demos). Off unless HANOK_RESERVATION_LAB=1."""
    if not hanok_reservation_lab_enabled():
        return HTMLResponse("Not found.", status_code=404)
    expected = admin_dashboard_token()
    if expected and token != expected:
        return HTMLResponse(
            (
                "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Lab</title></head><body>"
                "<p>Unauthorized. Open <code>/reservation-lab?token=…</code> with "
                "<code>ADMIN_DASHBOARD_TOKEN</code>.</p><p><a href='/'>Home</a></p></body></html>"
            ),
            status_code=401,
        )
    return _read_static_html(_RESERVATION_LAB, "reservation_lab.html")
