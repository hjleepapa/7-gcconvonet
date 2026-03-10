import asyncio
import base64
import json
import os
import uuid
import logging
from typing import Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from convonet.schemas import (
    ClientMessageType,
    AuthMessage,
    StartRecordingMessage,
    AudioChunkMessage,
    AuthOkMessage,
    TranscriptPartialMessage,
    TranscriptFinalMessage,
    ErrorMessage,
    ServerMessageType
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-gateway")

app = FastAPI(title="Voice Gateway Service")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections: session_id -> WebSocket
active_connections: Dict[str, WebSocket] = {}

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "voice-gateway"}

@app.websocket("/webrtc/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    logger.info(f"New WebSocket connection: {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if "type" not in message:
                await websocket.send_json(ErrorMessage(message="Missing message type").model_dump())
                continue
                
            msg_type = message["type"]
            
            try:
                if msg_type == ClientMessageType.AUTHENTICATE:
                    auth = AuthMessage(**message)
                    # Logic for authentication (PIN/Token)
                    session_id = auth.session_id or session_id
                    active_connections[session_id] = websocket
                    await websocket.send_json(AuthOkMessage(session_id=session_id).model_dump())
                    logger.info(f"Session {session_id} authenticated")
                    
                elif msg_type == ClientMessageType.START_RECORDING:
                    start = StartRecordingMessage(**message)
                    logger.info(f"Starting recording for session {start.session_id}")
                    # Initialize STT resources here
                    
                elif msg_type == ClientMessageType.AUDIO_CHUNK:
                    chunk = AudioChunkMessage(**message)
                    # Process audio chunk (send to STT)
                    # For now, just logging sequence
                    if chunk.sequence % 50 == 0:
                        logger.info(f"Received audio chunk {chunk.sequence} for {chunk.session_id}")
                        
                elif msg_type == ClientMessageType.STOP_RECORDING:
                    logger.info(f"Stopping recording for session {session_id}")
                    # Finalize STT and trigger LLM
                    
                elif msg_type == ClientMessageType.HEARTBEAT:
                    pass # Keep-alive
                    
            except ValidationError as e:
                await websocket.send_json(ErrorMessage(session_id=session_id, message=str(e)).model_dump())
                
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
        if session_id in active_connections:
            del active_connections[session_id]
    except Exception as e:
        logger.error(f"Error in WebSocket handler: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
