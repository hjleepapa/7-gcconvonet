from enum import Enum
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

# --- Client to Server Messages ---

class ClientMessageType(str, Enum):
    AUTHENTICATE = "authenticate"
    START_RECORDING = "start_recording"
    AUDIO_CHUNK = "audio_chunk"
    STOP_RECORDING = "stop_recording"
    # Streaming STT protocol (Phase 1+)
    AUDIO_FRAME = "audio_frame"
    END_UTTERANCE = "end_utterance"
    STREAM_RESET = "stream_reset"
    # Barge-in / cancel current turn
    CANCEL = "cancel"
    VOICE_PROVIDERS = "voice_providers"
    TRANSFER_REQUEST = "transfer_request"
    HEARTBEAT = "heartbeat"

class AuthMessage(BaseModel):
    type: ClientMessageType = Field(ClientMessageType.AUTHENTICATE, Literal=True)
    session_id: Optional[str] = None
    pin: Optional[str] = None
    user_token: Optional[str] = None
    stt_provider: Optional[str] = None
    tts_provider: Optional[str] = None

class StartRecordingMessage(BaseModel):
    type: ClientMessageType = Field(ClientMessageType.START_RECORDING, Literal=True)
    session_id: str
    stt_mode: str = "batch"  # "batch" = audio_chunk + stop_recording; "streaming" = audio_frame + end_utterance
    language: str = "en-US"
    stt_provider: Optional[str] = None
    tts_provider: Optional[str] = None

class AudioChunkMessage(BaseModel):
    type: ClientMessageType = Field(ClientMessageType.AUDIO_CHUNK, Literal=True)
    session_id: str
    sequence: int
    timestamp_ms: int
    data_b64: str

class StopRecordingMessage(BaseModel):
    type: ClientMessageType = Field(ClientMessageType.STOP_RECORDING, Literal=True)
    session_id: str


class AudioFrameMessage(BaseModel):
    """Streaming: small audio chunk (e.g. 20–50 ms). Server buffers until end_utterance."""
    type: ClientMessageType = Field(ClientMessageType.AUDIO_FRAME, Literal=True)
    session_id: str
    sequence: int = 0
    data_b64: str


class EndUtteranceMessage(BaseModel):
    """Streaming: client signals end of current utterance; server runs STT on buffered frames then LLM+TTS."""
    type: ClientMessageType = Field(ClientMessageType.END_UTTERANCE, Literal=True)
    session_id: str


class StreamResetMessage(BaseModel):
    """Streaming: discard buffered frames and reset for next utterance."""
    type: ClientMessageType = Field(ClientMessageType.STREAM_RESET, Literal=True)
    session_id: str


class CancelMessage(BaseModel):
    """Barge-in: client requests that the server skip sending transcript/agent/tts for the in-flight turn."""
    type: ClientMessageType = Field(ClientMessageType.CANCEL, Literal=True)
    session_id: str


class VoiceProvidersMessage(BaseModel):
    """Update per-session STT/TTS provider without re-running full start_recording."""
    type: ClientMessageType = Field(ClientMessageType.VOICE_PROVIDERS, Literal=True)
    session_id: str
    stt_provider: Optional[str] = None
    tts_provider: Optional[str] = None


class TransferRequestMessage(BaseModel):
    type: ClientMessageType = Field(ClientMessageType.TRANSFER_REQUEST, Literal=True)
    session_id: str
    extension: str = "2001"
    department: str = "support"
    reason: Optional[str] = "User requested human agent"

class HeartbeatMessage(BaseModel):
    type: ClientMessageType = Field(ClientMessageType.HEARTBEAT, Literal=True)
    session_id: str
    ts_ms: int

# --- Server to Client Messages ---

class ServerMessageType(str, Enum):
    AUTH_OK = "auth_ok"
    AUTH_FAILED = "auth_failed"
    GREETING = "greeting"
    STATUS = "status"
    PROCESSING_START = "processing_start"
    TRANSCRIPT_PARTIAL = "transcript_partial"
    TRANSCRIPT_FINAL = "transcript_final"
    AGENT_STREAM_CHUNK = "agent_stream_chunk"
    AGENT_FINAL = "agent_final"
    AUDIO_CHUNK = "audio_chunk"
    TRANSFER_INITIATED = "transfer_initiated"
    TRANSFER_STATUS = "transfer_status"
    ERROR = "error"

class AuthOkMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.AUTH_OK, Literal=True)
    session_id: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None

class GreetingMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.GREETING, Literal=True)
    session_id: str
    text: str
    data_b64: str  # TTS audio (e.g. audio/mpeg or audio/wav)
    mime_type: str = "audio/mpeg"  # audio/wav for Cartesia REST (PCM wrapped as WAV)

class ProcessingStartMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.PROCESSING_START, Literal=True)
    session_id: str
    started_at_ts: float  # Unix timestamp so client can show elapsed seconds

class StatusMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.STATUS, Literal=True)
    session_id: str
    message: str

class TranscriptPartialMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.TRANSCRIPT_PARTIAL, Literal=True)
    session_id: str
    text: str
    is_final: bool = False

class TranscriptFinalMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.TRANSCRIPT_FINAL, Literal=True)
    session_id: str
    text: str
    sequence: Optional[int] = None

class AgentStreamChunkMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.AGENT_STREAM_CHUNK, Literal=True)
    session_id: str
    text_chunk: str
    is_final: bool = False

class AgentFinalMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.AGENT_FINAL, Literal=True)
    session_id: str
    text: str
    transfer_marker: Optional[str] = None

class AudioChunkOutMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.AUDIO_CHUNK, Literal=True)
    session_id: str
    chunk_index: int
    total_chunks: Optional[int] = None
    data_b64: str
    is_final: bool = False
    is_early: bool = False
    mime_type: str = "audio/mpeg"

class TransferInitiatedMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.TRANSFER_INITIATED, Literal=True)
    session_id: str
    extension: str
    department: str
    reason: str

class TransferStatusMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.TRANSFER_STATUS, Literal=True)
    session_id: str
    success: bool
    details: Dict[str, Any]

class ErrorMessage(BaseModel):
    type: ServerMessageType = Field(ServerMessageType.ERROR, Literal=True)
    session_id: Optional[str] = None
    message: str
    code: Optional[str] = None
