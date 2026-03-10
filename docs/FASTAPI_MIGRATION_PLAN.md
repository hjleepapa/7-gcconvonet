# Migration Plan: Flask + Flask-SocketIO → FastAPI on Render

This document answers: (1) **Can FastAPI run on Render?** (2) **Migration plan** from the current Flask + Flask-SocketIO app to a FastAPI-first stack. (3) **Rough timeline** for the migration.

---

## 1. Does FastAPI work on Render.com?

**Yes.** Render Web Services run whatever process you specify. You can run an ASGI app (FastAPI) with **Uvicorn** instead of a WSGI app (Flask) with Gunicorn.

Your repo already has a **hybrid** setup that does this:

- **`render.yaml`** (current production):  
  `gunicorn --worker-class eventlet -w 1 ... passenger_wsgi:application`  
  → Flask + eventlet (for Socket.IO).

- **`render-hybrid.yaml`**:  
  `uvicorn asgi_main:api --host 0.0.0.0 --port $PORT --workers 1 --loop asyncio`  
  → FastAPI app (`asgi_main:api`) with Flask mounted via `WSGIMiddleware`.

So **FastAPI already runs on Render** in the hybrid config. A **full FastAPI migration** would mean the main app is FastAPI and you no longer depend on Flask for the voice path (or at all, if you migrate everything).

**Render details:**

- **Start command:** Use `uvicorn` (or `gunicorn` with `uvicorn.workers.UvicornWorker`) for a FastAPI/ASGI app.
- **Health check:** Point `healthCheckPath` to a FastAPI route (e.g. `/` or `/health`).
- **Env vars:** Same as today (no Render-specific changes for FastAPI).
- **Build:** Same `pip install -r requirements-render.txt` (add `uvicorn` if not already there).

---

## 2. Migration strategy (two options)

| Option | Description | Effort | Risk |
|--------|-------------|--------|------|
| **A. Incremental (recommended)** | Keep Flask mounted under FastAPI; move voice routes and real-time layer to FastAPI first; migrate rest of routes over time. | Medium | Low |
| **B. Full rewrite** | New FastAPI app; migrate all routes and replace Socket.IO with native WebSockets in one go. | High | Higher |

**Recommendation:** Option A. Use the existing **asgi_main.py** (FastAPI + Flask mount) as the single Render service, then move voice-related routes and WebSocket handling into FastAPI step by step. When nothing critical remains on Flask, you can remove the mount.

---

## 3. Migration phases and tasks

### Phase 1: FastAPI as primary entrypoint on Render (no behavior change)

**Goal:** Run the same app via Uvicorn (FastAPI + mounted Flask) on Render so production uses ASGI.

| Task | Description | Est. |
|------|-------------|------|
| 1.1 | Switch Render service to `render-hybrid.yaml` (or change `render.yaml` startCommand to `uvicorn asgi_main:api --host 0.0.0.0 --port $PORT --workers 1`). | 0.5 day |
| 1.2 | Confirm `healthCheckPath` works (e.g. `/fastapi/health` or `/`). | 0.5 day |
| 1.3 | Smoke-test: site loads, login, voice assistant connects (Socket.IO over WSGIMiddleware / long-polling). | 0.5 day |

**Deliverable:** Production on Render using Uvicorn + FastAPI with Flask mounted. No change to app logic.

**Risks:** Flask-SocketIO under WSGIMiddleware may use long-polling instead of WebSocket (Render and many proxies support WebSocket for the same process; document that if you see fallback). If everything works as today, no further change needed in this phase.

---

### Phase 2: Move REST and static routes to FastAPI

**Goal:** Expose main HTTP routes from FastAPI; keep Flask only for Socket.IO (or remove later).

| Task | Description | Est. |
|------|-------------|------|
| 2.1 | Add FastAPI routes for: health, `/convonet_todo/` index, Twilio webhooks (`/twilio/call`, `/twilio/verify_pin`, `/twilio/process_audio`, `/twilio/voice_assistant/transfer_bridge`). Implement by calling existing Python logic (from `routes.py` / `webrtc_voice_server_socketio.py`) or copy handlers. | 2–3 days |
| 2.2 | Add FastAPI routes for Convonet Todo API: run_agent, LLM/STT/TTS provider get/set, pending-response, mortgage, SuiteCRM debug, etc. Reuse existing service layer. | 2–3 days |
| 2.3 | Serve static/templates from FastAPI (e.g. `StaticFiles`, Jinja2 with `Request` + `HTMLResponse`) or keep redirecting to Flask for now. | 0.5–1 day |
| 2.4 | Point Render `healthCheckPath` to FastAPI health route. | 0.5 day |

**Deliverable:** All critical HTTP traffic can be served by FastAPI; Flask mount can be limited to Socket.IO or removed if you move to Phase 3.

---

### Phase 3: Replace Flask-SocketIO with FastAPI WebSockets (or python-socketio ASGI)

**Goal:** Voice assistant real-time path runs on FastAPI (native WebSocket or Socket.IO on ASGI).

| Task | Description | Est. |
|------|-------------|------|
| 3.1 | **Option A – Native WebSocket:** Design a simple protocol (e.g. JSON messages: `auth`, `audio_chunk`, `start_recording`, `stop_recording`, server: `transcription`, `agent_response`, `audio_chunk`). Implement FastAPI WebSocket endpoint(s) that replace the `/voice` namespace. | 2–3 days |
| 3.2 | **Option B – Socket.IO on ASGI:** Use `python-socketio` in ASGI mode; mount the Socket.IO app on FastAPI. Refactor current Socket.IO handlers from `webrtc_voice_server_socketio.py` into a shared module callable from both Flask-SocketIO and ASGI (or only ASGI). | 2–4 days |
| 3.3 | Reuse existing logic: auth (PIN/session), Redis session, STT (Deepgram streaming), `process_audio_async` → `process_with_agent` → `_run_agent_async`, TTS, LiveKit token/send, transfer. No rewrite of STT/LLM/TTS. | 2–3 days |
| 3.4 | Update frontend: point Socket.IO client to same URL (if Option B) or replace with a single WebSocket (if Option A). Test: connect, auth, record, get transcription and TTS, transfer. | 1–2 days |

**Deliverable:** Voice assistant works end-to-end on FastAPI (WebSocket or Socket.IO ASGI); Flask no longer required for the voice path.

---

### Phase 4: Retire Flask (optional)

**Goal:** Remove Flask and WSGIMiddleware; single FastAPI app.

| Task | Description | Est. |
|------|-------------|------|
| 4.1 | Move any remaining Flask routes (call center, auth, team, audio player, tool GUI) to FastAPI. | 2–4 days |
| 4.2 | Remove Flask app creation and `api.mount("/", WSGIMiddleware(flask_app))` from `asgi_main.py`. | 0.5 day |
| 4.3 | Run full regression (web, voice, call center, Twilio, transfer). | 1–2 days |

**Deliverable:** One FastAPI app on Render; no Flask dependency.

---

## 4. Timeline summary

| Phase | Scope | Estimated duration (one developer) |
|-------|--------|-----------------------------------|
| **1** | FastAPI as entrypoint (Uvicorn), Flask mounted | **1–2 days** |
| **2** | Move REST + Twilio to FastAPI | **5–8 days** |
| **3** | Replace Flask-SocketIO with WebSocket or Socket.IO ASGI | **5–10 days** |
| **4** | Remove Flask entirely | **3–6 days** (optional) |

- **Minimal (Phase 1 only):** ~1–2 days — production runs on FastAPI + Uvicorn, behavior unchanged.
- **Voice on FastAPI (Phases 1 + 2 + 3):** ~3–4 weeks (about 11–20 working days).
- **Full migration including Phase 4:** ~4–5 weeks (about 15–26 working days).

Durations assume one developer familiar with the codebase; add buffer for testing, fixes, and deployment.

---

## 5. Render configuration (FastAPI-only)

After migration, a single Render Web Service can look like this (no Flask):

```yaml
# render.yaml (FastAPI-only example)
services:
  - type: web
    name: convonet-todo-app
    env: python
    region: oregon
    buildCommand: pip install -r requirements-render.txt
    startCommand: uvicorn asgi_main:api --host 0.0.0.0 --port $PORT --workers 1 --loop asyncio
    envVars:
      - key: PYTHON_VERSION
        value: 3.12.0
      # ... same env vars as current render.yaml ...
    healthCheckPath: /
    autoDeploy: true
```

- **startCommand:** `uvicorn asgi_main:api` (or your main FastAPI app module).
- **workers:** Keep `1` if you use in-process state (e.g. Redis-backed sessions); increase only if you move to stateless workers and external session/store.
- **healthCheckPath:** `/` or `/health` or `/fastapi/health` — any route that returns 200 when the app is up.

---

## 6. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Socket.IO vs WebSocket protocol change | Option B (Socket.IO on ASGI) keeps the same client; Option A requires a small client change and a clear message schema. |
| Eventlet vs asyncio | Current code mixes eventlet and asyncio (e.g. `AgentProcessor`). Move voice path to `async def` and `await` only; use `run_in_executor` or async HTTP/DB where needed. |
| Session/Redis | Keep using Redis for session and cache; no change required for Render. |
| Twilio webhooks | Same URLs; only the process handling them changes (FastAPI instead of Flask). |
| LiveKit | Unchanged; keep using existing LiveKit token and send logic from the new FastAPI routes. |

---

## 7. Quick answers

1. **Can FastAPI be used without Flask + Flask-SocketIO?**  
   Yes. You migrate routes and real-time handling to FastAPI; the same STT/LLM/TTS and transfer logic can stay.

2. **Does FastAPI work on Render.com?**  
   Yes. Use `uvicorn asgi_main:api --host 0.0.0.0 --port $PORT` (or your FastAPI app). You already have this in `render-hybrid.yaml`.

3. **How long does migration take?**  
   - **Minimal (only switch to Uvicorn + FastAPI entrypoint):** 1–2 days.  
   - **Voice pipeline on FastAPI (Phases 1–3):** about 3–4 weeks.  
   - **Full removal of Flask (Phase 4):** about 4–5 weeks total.

4. **Recommended path?**  
   Use **Option A (incremental):** switch Render to `uvicorn asgi_main:api` (Phase 1), then move Twilio and voice-related HTTP to FastAPI (Phase 2), then replace Flask-SocketIO with FastAPI WebSocket or Socket.IO ASGI (Phase 3). Phase 4 (remove Flask) is optional.
