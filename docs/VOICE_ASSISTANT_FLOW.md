# Voice Assistant Flow Documentation

## Overview
This document describes the complete flow of how the WebRTC voice assistant processes user audio and generates responses.

## Architecture Components

### 1. **Frontend (Browser)**
- **File**: `templates/webrtc_voice_assistant.html` (or similar)
- **Technology**: WebRTC, Socket.IO client
- **Responsibilities**:
  - Captures audio from user's microphone
  - Sends audio chunks to server via Socket.IO
  - Receives and plays TTS audio responses
  - Handles UI state (recording, authentication, etc.)

### 2. **WebRTC Voice Server**
- **File**: `convonet/webrtc_voice_server.py`
- **Technology**: Flask-SocketIO, Deepgram SDK
- **Responsibilities**:
  - WebSocket connection management
  - Audio buffer management (Redis or in-memory)
  - Deepgram STT (Speech-to-Text) transcription
  - Deepgram TTS (Text-to-Speech) generation
  - Session management
  - Authentication handling

### 3. **Agent Processing**
- **File**: `convonet/routes.py`
- **Technology**: LangGraph, LangChain, Anthropic Claude
- **Responsibilities**:
  - Agent graph initialization
  - MCP tools loading
  - Processing user prompts
  - Generating AI responses

### 4. **Agent Graph**
- **File**: `convonet/assistant_graph_todo.py`
- **Technology**: LangGraph, LangChain Anthropic
- **Responsibilities**:
  - LLM integration (Anthropic Claude)
  - Tool execution orchestration
  - State management
  - Response generation

## Complete Flow

### Step 1: User Authentication
**File**: `convonet/webrtc_voice_server.py` - `handle_authenticate()`

1. User enters PIN in frontend
2. Frontend sends `authenticate` event with PIN via Socket.IO
3. Server receives PIN and calls `_run_agent_for_pin_verification(pin)`
4. Agent verifies PIN using `verify_user_pin` tool
5. If valid, session is marked as authenticated in Redis/memory
6. Welcome greeting is sent with TTS audio

**Key Methods**:
- `handle_authenticate()` - Socket.IO handler
- `_run_agent_for_pin_verification()` - Agent PIN verification
- `send_welcome_greeting()` - TTS welcome message

### Step 2: Audio Recording
**File**: `convonet/webrtc_voice_server.py` - `handle_start_recording()`, `handle_audio_data()`

1. User clicks "Start Recording" button
2. Frontend sends `start_recording` event
3. Server clears audio buffer and sets `is_recording=True`
4. Frontend captures audio chunks from microphone
5. Each audio chunk is base64-encoded and sent via `audio_data` event
6. Server appends chunks to session's audio buffer (Redis or memory)

**Key Methods**:
- `handle_start_recording()` - Initialize recording
- `handle_audio_data()` - Receive and buffer audio chunks

### Step 3: Stop Recording & Transcription
**File**: `convonet/webrtc_voice_server.py` - `handle_stop_recording()`

1. User clicks "Stop Recording" button
2. Frontend sends `stop_recording` event with complete base64-encoded audio blob
3. Server receives complete audio blob
4. Audio is decoded from base64 to binary
5. Audio is sent to Deepgram STT API for transcription
6. Deepgram returns transcribed text

**Key Methods**:
- `handle_stop_recording()` - Process complete audio
- `transcribe_audio_with_deepgram_webrtc()` - Deepgram STT call

### Step 4: Agent Processing
**File**: `convonet/webrtc_voice_server.py` - `process_with_agent()`
**File**: `convonet/routes.py` - `_run_agent_async()`, `_get_agent_graph()`

1. Transcribed text is passed to `process_with_agent()`
2. `process_with_agent()` calls `_run_agent_async()` from `routes.py`
3. `_run_agent_async()` calls `_get_agent_graph()` to get or initialize agent graph
4. `_get_agent_graph()`:
   - Checks if graph is cached (returns if yes)
   - Initializes MCP client to load tools
   - Handles `UnboundLocalError` from library bug gracefully
   - Builds agent graph with available tools (or empty list if MCP fails)
   - Caches graph for future use
5. Agent graph processes the user's prompt:
   - Creates `AgentState` with user message
   - Streams through graph nodes (assistant → tools → assistant)
   - LLM generates response and tool calls
   - Tools are executed (database queries, calendar operations, etc.)
   - Final response is generated
6. Response text is returned

**Key Methods**:
- `process_with_agent()` - Entry point for agent processing
- `_run_agent_async()` - Main agent execution
- `_get_agent_graph()` - Agent graph initialization with error handling
- `TodoAgent.build_graph()` - Graph construction
- `TodoAgent.assistant()` - LLM node
- `TodoAgent.tools_node()` - Tool execution node

### Step 5: Text-to-Speech Generation
**File**: `convonet/webrtc_voice_server.py` - `handle_stop_recording()`
**File**: `deepgram_service.py` - `synthesize_speech()`

1. Agent response text is passed to Deepgram TTS API
2. Deepgram generates audio (MP3 format)
3. Audio is base64-encoded
4. Response is sent to frontend via Socket.IO `agent_response` event

**Key Methods**:
- `deepgram_service.synthesize_speech()` - Deepgram TTS call
- Socket.IO `emit('agent_response', ...)` - Send to frontend

### Step 6: Frontend Playback
**File**: Frontend template (e.g., `templates/webrtc_voice_assistant.html`)

1. Frontend receives `agent_response` event with text and audio
2. Audio is decoded from base64
3. Audio is played using HTML5 Audio API
4. Text is displayed in conversation UI
5. User can start next recording

## Error Handling

### MCP Tools Initialization Error
**Problem**: `UnboundLocalError` from `langchain_mcp_adapters` library bug

**Solution** (in `_get_agent_graph()`):
1. Initialize `tools = []` before try block
2. Wrap `client.get_tools()` in `safe_get_tools()` wrapper
3. Catch `UnboundLocalError` at multiple levels:
   - Inner try-except around `asyncio.wait_for()`
   - Outer exception handlers
   - Check error messages for "UnboundLocalError" or "cannot access local variable 'tools'"
4. Always set `tools = []` if MCP fails
5. Build graph with empty tools list as fallback
6. Return graph even if tools failed to load

**Key Code Locations**:
- `convonet/routes.py` lines 770-864
- Wrapper function: `safe_get_tools()` (lines 778-790)
- Exception handlers: lines 781-797, 833-851
- Fallback graph building: lines 855-864

### Anthropic Model Error
**Problem**: Model name not found (404 error)

**Solution** (in `TodoAgent.__init__()`):
1. Try multiple model names as fallback:
   - User-specified or `ANTHROPIC_MODEL` env var
   - `claude-3-5-sonnet-20240620` (June 2024)
   - `claude-3-5-sonnet` (without date)
   - `claude-3-sonnet-20240229` (older version)
2. Validate model name length to detect truncation
3. Log which model is being used

**Key Code Locations**:
- `convonet/assistant_graph_todo.py` lines 256-285

## Data Flow Diagram

```
User → Frontend → Socket.IO → webrtc_voice_server.py
                                    ↓
                            handle_stop_recording()
                                    ↓
                        transcribe_audio_with_deepgram_webrtc()
                                    ↓
                            Deepgram STT API
                                    ↓
                        process_with_agent(transcribed_text)
                                    ↓
                            _run_agent_async()
                                    ↓
                            _get_agent_graph()
                                    ↓
                    [MCP Tools Loading - with error handling]
                                    ↓
                            TodoAgent.build_graph()
                                    ↓
                    [LangGraph Execution: assistant → tools → assistant]
                                    ↓
                            Anthropic Claude API
                                    ↓
                            Tool Execution (if needed)
                                    ↓
                            Final Response Text
                                    ↓
                        deepgram_service.synthesize_speech()
                                    ↓
                            Deepgram TTS API
                                    ↓
                        Socket.IO emit('agent_response')
                                    ↓
                            Frontend → Audio Playback
```

## Key Configuration

### Environment Variables
- `ANTHROPIC_API_KEY` - Anthropic Claude API key
- `ANTHROPIC_MODEL` - Model name (optional, defaults to `claude-3-5-sonnet-20240620`)
- `DEEPGRAM_API_KEY` - Deepgram API key for STT and TTS
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` - Redis configuration
- `DB_URI` - PostgreSQL database connection string

### MCP Configuration
- **File**: `convonet/mcps/mcp_config.json`
- Contains MCP server configurations for database tools
- Environment variable substitution for `DB_URI`

## Session Management

### Storage Options
1. **Redis** (preferred): Persistent, shared across workers
2. **In-memory** (fallback): Local to worker process

### Session Data
- `authenticated` - Boolean authentication status
- `user_id` - Authenticated user ID
- `user_name` - User's display name
- `audio_buffer` - Base64-encoded audio chunks
- `is_recording` - Recording state flag

## Performance Considerations

1. **Agent Graph Caching**: Graph is cached after first initialization
2. **Async Processing**: All I/O operations are async
3. **Timeout Handling**: 10-second timeout for MCP tools, 20-second for agent processing
4. **Error Recovery**: Graceful degradation if MCP tools fail (continues with empty tools)

## Debugging

### Key Log Messages
- `🔧 Initializing agent graph (first time only)...` - Graph initialization start
- `🔧 Creating MCP client...` - MCP client creation
- `🔧 Getting tools from MCP client...` - Tools loading
- `⚠️ MCP library error (UnboundLocalError): ...` - MCP error caught
- `🔧 Building agent graph with X tools...` - Graph building
- `✅ Agent graph cached for future requests` - Success
- `🤖 Using Anthropic model: ...` - Model selection
- `🎧 Deepgram: Processing audio buffer: ...` - Audio processing
- `🤖 Agent response: ...` - Final response

### Common Issues
1. **UnboundLocalError**: Handled gracefully, agent continues with empty tools
2. **Model 404**: Falls back to alternative model names
3. **MCP Timeout**: Continues with empty tools list
4. **Redis Unavailable**: Falls back to in-memory storage

