# Legacy monolith (Flask / Render)

**Primary deployment is GCP** (Cloud Run). See `cloudbuild.yaml`, `docker/`, and `docs/CLOUD_RUN_ENV.md`.

The repo still contains a **legacy Flask + Socket.IO monolith** for local or historical use. It is not required for GCP.

## What was removed (cleanup)

- **Render configs:** `render.yaml`, `render_memory_optimized.yaml`, `render-hybrid.yaml`, `convonet/render.yaml`, `convonet/render_memory_optimized.yaml`
- **WSGI variants:** `passenger_wsgi_memory_optimized.py`, `convonet/passenger_wsgi.py`, `convonet/passenger_wsgi_memory_optimized.py`, `convonet/app_memory_optimized.py`
- **Old FastAPI voice:** `convonet/fastapi_voice_gateway.py` (replaced by `convonet/voice_gateway_service.py` on GCP)
- **Scripts/examples:** `debug_livekit.py`, `LOGGING_EXAMPLE.py`, `TOOL_EXECUTION_EXAMPLE.py`, `convonet/elevenlabs/WEBSOCKET_EXAMPLES.py`
- **Deploy scripts:** `deploy_memory_optimized.sh`, `convonet/deploy_memory_optimized.sh` (relied on removed Render/memory-optimized files)
- **Memory-optimized deps:** `requirements_memory_optimized.txt`, `convonet/requirements_memory_optimized.txt`

## What remains for the monolith

| File / folder | Purpose |
|---------------|--------|
| `app.py` | Flask `create_app()`, registers blueprints |
| `passenger_wsgi.py` | Gunicorn entry (e.g. `gunicorn passenger_wsgi:application`) |
| `asgi_main.py` | Optional FastAPI wrapper mounting Flask (no longer mounts old voice gateway) |
| `extensions.py` | Flask extensions (db, ckeditor, bootstrap, migrate) |
| `convonet/app.py` | Alternate Flask app (convonet-only) |
| `convonet/webrtc_voice_server_socketio.py` | Socket.IO WebRTC voice server |
| `convonet/livekit_audio_bridge.py` | Optional LiveKit bridge (used by Socket.IO server) |
| `call_center/` | Flask blueprint + templates/static (templates/static also used by GCP call-center-service) |

To run the monolith locally you can use `flask run` (with `app:app` or `convonet.app:app`) or `gunicorn passenger_wsgi:application`. For production use **GCP Cloud Run** and the services in `docker/`.
