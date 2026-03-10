import logging
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("call-center-service")

app = FastAPI(title="Call Center Service")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "call-center-service"}

@app.get("/call-center", response_class=HTMLResponse)
async def call_center_ui():
    # In a real implementation, this would serve the Jinja2 templates for the JsSIP UI
    # Reusing current templates/call_center.html
    return """
    <html>
        <head><title>JsSIP Call Center</title></head>
        <body>
            <h1>JsSIP Call Center (Placeholder)</h1>
            <p>This is the JsSIP-based call center UI.</p>
        </body>
    </html>
    """

class AgentLoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/agent/login")
async def agent_login(request: AgentLoginRequest):
    logger.info(f"Agent login attempt: {request.username}")
    # Integration with SQLAlchemy and Security helpers
    return {"success": True, "token": "mock-token-123"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
