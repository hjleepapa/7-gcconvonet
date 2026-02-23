# Hybrid Streaming Implementation

## Overview

This document describes the hybrid streaming implementation that combines native SDK streaming for Gemini with optimized LangGraph streaming for Claude/OpenAI, along with latency optimizations.

## Key Features

### 1. **Gemini Native SDK Streaming**
- Uses `google-genai` native SDK instead of LangChain wrapper
- Real-time WebSocket streaming via `generate_content_stream`
- Eliminates blocking HTTP calls that caused timeouts
- Streams text chunks and tool calls incrementally

### 2. **Claude/OpenAI Optimized Streaming**
- Reduced timeouts: 8s → 5s per iteration
- Reduced watchdog: 6s → 4s
- Reduced execution timeout: 15s → 12s
- Incremental text emission via WebSocket (`agent_stream_chunk` events)

### 3. **Parallel Tool Execution**
- Multiple tools execute in parallel using `asyncio.gather()`
- Reduced tool timeout: 8s → 6s
- Faster failure detection

### 4. **WebSocket Streaming**
- Real-time text chunks via `agent_stream_chunk` events
- Tool call notifications in real-time
- Lower perceived latency

## Architecture

```
Browser → WebSocket → Flask → LangGraph/Streaming Handler → LLM API
         (Audio)      (Stream)  (State updates)              (Stream)
```

### For Gemini:
```
Browser → WebSocket → Flask → Gemini Native SDK → Gemini API
         (Audio)      (Stream)  (WebSocket)        (Stream)
```

### For Claude/OpenAI:
```
Browser → WebSocket → Flask → LangGraph → Claude/OpenAI API
         (Audio)      (Stream)  (astream)   (Stream)
```

## Implementation Details

### Files Modified

1. **`convonet/gemini_streaming.py`** (NEW)
   - Native Gemini SDK streaming handler
   - Converts LangChain tools to Gemini format
   - Streams responses via WebSocket

2. **`convonet/routes.py`**
   - Added `socketio` and `session_id` parameters to `_run_agent_async()`
   - Hybrid streaming logic for Gemini (native SDK) vs others (LangGraph)
   - Incremental text emission for Claude/OpenAI
   - Reduced timeouts

3. **`convonet/assistant_graph_todo.py`**
   - Parallel tool execution for multiple tools
   - Reduced tool timeouts
   - Better error handling

4. **`convonet/webrtc_voice_server.py`**
   - Passes `socketio` and `session_id` to agent processing
   - Supports streaming responses

### WebSocket Events

#### `agent_stream_chunk`
Emitted incrementally as text arrives:
```json
{
  "text": "chunk of text",
  "type": "text"
}
```

Or for tool calls:
```json
{
  "tool_call": {
    "name": "create_calendar_event",
    "id": "tool_123",
    "args": {...}
  },
  "type": "tool"
}
```

#### `agent_response`
Emitted when complete response is ready (existing):
```json
{
  "success": true,
  "text": "full response",
  "audio": "base64_encoded_audio"
}
```

## Latency Optimizations

1. **Reduced Timeouts**
   - Stream iteration: 8s → 5s
   - Watchdog: 6s → 4s
   - Execution: 15s → 12s
   - Tool execution: 8s → 6s

2. **Parallel Tool Execution**
   - Multiple tools execute concurrently
   - Reduces total tool execution time

3. **Incremental Streaming**
   - Text chunks sent as they arrive
   - Lower perceived latency
   - Better user experience

4. **Native SDK for Gemini**
   - Eliminates LangChain wrapper overhead
   - Direct WebSocket streaming
   - No blocking HTTP calls

## Benefits

1. **Lower Latency**
   - Reduced timeouts = faster failure detection
   - Parallel tools = faster execution
   - Incremental streaming = lower perceived latency

2. **Better Reliability**
   - Native SDK eliminates blocking issues
   - Proper async streaming
   - Better error handling

3. **Improved UX**
   - Real-time text updates
   - Tool call notifications
   - Faster response times

## Testing

To test the implementation:

1. **Gemini Streaming**
   - Set provider to `gemini`
   - Check logs for "📡 Streaming Gemini response with native SDK..."
   - Verify `agent_stream_chunk` events are received

2. **Claude/OpenAI Streaming**
   - Set provider to `claude` or `openai`
   - Check logs for incremental text emission
   - Verify reduced timeouts are working

3. **Parallel Tools**
   - Request multiple tool calls
   - Check logs for "🚀 Executing N tools in parallel..."
   - Verify faster execution

## Future Improvements

1. **Frontend Support**
   - Add `agent_stream_chunk` event handler
   - Display incremental text updates
   - Show tool call progress

2. **Audio Streaming**
   - Stream TTS audio chunks
   - Lower audio latency

3. **Caching**
   - Cache common responses
   - Reduce API calls

4. **Connection Pooling**
   - Reuse connections
   - Lower connection overhead

