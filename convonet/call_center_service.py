import logging
import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("call-center-service")

from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Call Center Service")

# Mount static files from the project root
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
# Mount call_center static so url_for('call_center.static', filename='...') works
if os.path.exists("call_center/static"):
    app.mount("/call_center/static", StaticFiles(directory="call_center/static"), name="call_center_static")

# Setup templates - use absolute paths so they work from any cwd (e.g. Docker /app)
_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_template_dirs = [
    os.path.join(_root, "call_center", "templates"),
    os.path.join(_root, "templates"),
]
templates = Jinja2Templates(directory=[d for d in _template_dirs if os.path.isdir(d)] or ["templates"])


def _url_for(name: str, **kwargs) -> str:
    """Flask-style url_for for Jinja so index.html and base.html render without errors."""
    if name == "static" and "filename" in kwargs:
        return f"/static/{kwargs['filename'].lstrip('/')}"
    if name == "call_center.static" and "filename" in kwargs:
        return f"/call_center/static/{kwargs['filename'].lstrip('/')}"
    # Route names used by index.html / base.html (links can point to # or same-host paths)
    if name == "convonet_tech_spec":
        return "/convonet_tech_spec"
    if name == "convonet_system_architecture":
        return "/convonet_system_architecture"
    if name == "convonet_sequence_diagram":
        return "/convonet_sequence_diagram"
    return "#"


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "call-center-service"}


@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Serves the main landing page for FastAPI/GCP microservices."""
    # Optional: set CONVONET_API_BASE to agent-llm-service URL if provider APIs are on another origin (e.g. https://agent-llm-xxx.run.app)
    convonet_api_base = os.getenv("CONVONET_API_BASE", "").rstrip("/")
    voice_assistant_url = os.getenv("VOICE_ASSISTANT_URL", "").strip() or None
    mortgage_dashboard_url = os.getenv("MORTGAGE_DASHBOARD_URL", "").strip() or None
    context = {
        "request": request,
        "url_for": _url_for,
        "convonet_api_base": convonet_api_base,
        "voice_assistant_url": voice_assistant_url,
        "mortgage_dashboard_url": mortgage_dashboard_url,
        "llm_providers": ["Gemini", "GPT-4", "Claude"],
        "stt_providers": ["Google", "Deepgram", "OpenAI"],
        "tts_providers": ["Google", "ElevenLabs", "Cartesia"],
    }
    return templates.TemplateResponse("index.html", context)


def _get_sip_config() -> dict:
    """SIP config for call center UI (domain, wss_port). Uses env or defaults."""
    domain = os.getenv("SIP_DOMAIN", "sip.example.com").strip()
    try:
        wss_port = int(os.getenv("SIP_WSS_PORT", "7443"))
    except ValueError:
        wss_port = 7443
    return {"domain": domain, "wss_port": wss_port}


@app.get("/call-center", response_class=HTMLResponse)
async def call_center_ui(request: Request):
    """Serves the Unified Agent Desktop UI"""
    return templates.TemplateResponse(
        "call_center.html",
        {
            "request": request,
            "url_for": _url_for,
            "sip_config": _get_sip_config(),
        },
    )


@app.get("/voice_assistant", response_class=HTMLResponse)
@app.get("/voice-assistant", response_class=HTMLResponse)
async def voice_assistant_ui(request: Request):
    """Voice assistant UI: connects to FastAPI WebSocket at /webrtc/ws (voice-gateway-service). No LiveKit."""
    return templates.TemplateResponse(
        "voice_assistant.html",
        {"request": request, "url_for": _url_for, "websocket_path": "/webrtc/ws"},
    )


@app.get("/mortgage_dashboard", response_class=HTMLResponse)
async def mortgage_dashboard_ui(request: Request):
    """Mortgage dashboard UI."""
    return templates.TemplateResponse(
        "mortgage_dashboard.html",
        {"request": request, "url_for": _url_for},
    )


@app.get("/agent-monitor", response_class=HTMLResponse)
async def agent_monitor_ui(request: Request):
    """Agent monitor dashboard UI."""
    return templates.TemplateResponse(
        "agent_monitor_dashboard.html",
        {"request": request, "url_for": _url_for},
    )


@app.get("/tool-execution", response_class=HTMLResponse)
async def tool_execution_ui(request: Request):
    """Tool execution dashboard UI."""
    return templates.TemplateResponse(
        "templates/tool_execution_dashboard.html",
        {"request": request, "url_for": _url_for},
    )


@app.get("/convonet_tech_spec", response_class=HTMLResponse)
async def convonet_tech_spec(request: Request):
    """Technical specification page."""
    return templates.TemplateResponse(
        "convonet_tech_spec.html",
        {"request": request, "url_for": _url_for},
    )


@app.get("/convonet_system_architecture", response_class=HTMLResponse)
async def convonet_system_architecture(request: Request):
    """System architecture diagram page."""
    return templates.TemplateResponse(
        "templates/convonet_system_architecture.html",
        {"request": request, "url_for": _url_for},
    )


@app.get("/convonet_sequence_diagram", response_class=HTMLResponse)
async def convonet_sequence_diagram(request: Request):
    """Sequence diagram page."""
    return templates.TemplateResponse(
        "convonet_sequence_diagram.html",
        {"request": request, "url_for": _url_for},
    )


# Agent-monitor dashboard APIs: read from Redis (same store agent-llm-service writes to via AgentMonitor)
def _get_agent_monitor_safe():
    """Return AgentMonitor instance or None if Redis/agent_monitor unavailable."""
    try:
        from convonet.agent_monitor import get_agent_monitor
        return get_agent_monitor()
    except Exception as e:
        logger.warning("Agent monitor unavailable (Redis may be unset on call-center): %s", e)
        return None


@app.get("/agent-monitor/api/stats")
async def agent_monitor_api_stats():
    """Return agent interaction stats from Redis (written by agent-llm-service)."""
    monitor = _get_agent_monitor_safe()
    if not monitor:
        return {
            "success": True,
            "stats": {
                "total_interactions": 0,
                "by_provider": {"claude": 0, "gemini": 0, "openai": 0},
                "total_tool_calls": 0,
                "avg_duration_ms": 0,
            },
        }
    try:
        stats = monitor.get_stats()
        by_provider = stats.get("by_provider") or {}
        # Ensure keys expected by dashboard exist
        by_provider = {
            "claude": by_provider.get("claude", 0),
            "gemini": by_provider.get("gemini", 0),
            "openai": by_provider.get("openai", 0),
            **{k: v for k, v in by_provider.items() if k not in ("claude", "gemini", "openai")},
        }
        return {
            "success": True,
            "stats": {
                "total_interactions": stats.get("total_interactions", 0),
                "by_provider": by_provider,
                "total_tool_calls": stats.get("total_tool_calls", 0),
                "avg_duration_ms": stats.get("avg_duration_ms", 0),
            },
        }
    except Exception as e:
        logger.exception("Error fetching agent-monitor stats")
        return {
            "success": True,
            "stats": {
                "total_interactions": 0,
                "by_provider": {"claude": 0, "gemini": 0, "openai": 0},
                "total_tool_calls": 0,
                "avg_duration_ms": 0,
            },
        }


@app.get("/agent-monitor/api/interactions")
async def agent_monitor_api_interactions(limit: int = 50, provider: Optional[str] = None, agent_type: Optional[str] = None):
    """Return recent agent interactions from Redis (written by agent-llm-service)."""
    monitor = _get_agent_monitor_safe()
    if not monitor:
        return {"success": True, "interactions": []}
    try:
        if provider and provider != "all":
            interactions = monitor.get_interactions_by_provider(provider, limit=limit)
        else:
            interactions = monitor.get_recent_interactions(limit=limit)
        interactions_data = [i.to_dict() for i in interactions]
        if agent_type and agent_type != "all":
            interactions_data = [
                i for i in interactions_data
                if (i.get("metadata") or {}).get("agent_type") == agent_type
            ]
        return {"success": True, "interactions": interactions_data}
    except Exception as e:
        logger.exception("Error fetching agent-monitor interactions")
        return {"success": True, "interactions": []}


# Stub APIs for tool-execution dashboard
@app.get("/tool-execution/api/stats")
async def tool_execution_api_stats():
    """Stub: return empty stats so the dashboard renders until real backend is wired."""
    return {
        "success": True,
        "stats": {
            "total_successful": 0,
            "total_failed": 0,
            "total_timeout": 0,
            "success_rate": 0.0,
            "total_requests": 0,
        },
    }


@app.get("/tool-execution/api/trackers")
async def tool_execution_api_trackers():
    """Stub: return empty list until real backend is wired."""
    return {"success": True, "trackers": []}


@app.get("/tool-execution/api/tracker/{request_id}")
async def tool_execution_api_tracker(request_id: str):
    """Stub: return empty tools until real backend is wired."""
    return {"success": True, "tools": []}


class AgentStatusUpdate(BaseModel):
    agent_id: str
    status: str # e.g., "Available", "Busy", "Offline"

@app.post("/api/agent/status")
async def update_agent_status(data: AgentStatusUpdate):
    logger.info(f"Updating agent {data.agent_id} status to {data.status}")
    # In a real implementation, this would update SQLAlchemy models In DB
    return {"success": True, "agent_id": data.agent_id, "new_status": data.status}

class CallInfo(BaseModel):
    call_sid: str
    direction: str
    from_number: str
    to_number: str
    status: str

@app.post("/api/call/event")
async def handle_call_event(call: CallInfo):
    logger.info(f"Call event received: {call.call_sid} - {call.status}")
    # Log call activity to DB
    return {"success": True}

@app.get("/api/customer/profile")
async def get_customer_profile(phone: str):
    """Fetches customer profile, enriched by CRM microservice if needed"""
    logger.info(f"Fetching profile for {phone}")
    # Real implementation would call CRM microservice
    return {
        "phone": phone,
        "name": "Jane Doe",
        "last_interaction": str(datetime.datetime.now()),
        "summary": "Potential mortgage lead."
    }

if __name__ == "__main__":
    import uvicorn
    # Default port 8002 for Call Center Service
    uvicorn.run(app, host="0.0.0.0", port=8002)
