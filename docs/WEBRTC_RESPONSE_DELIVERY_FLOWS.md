# WebRTC Response Delivery Flows: Socket.IO vs HTTP + Streaming Audio

This document explains the delivery mechanisms for agent responses in the WebRTC voice assistant.

## Overview

The system uses multiple strategies to optimize response delivery:

1. **Response Size-Based Routing**: 
   - **Small responses (<500KB)**: Socket.IO (real-time, low latency)
   - **Large responses (>500KB)**: HTTP (reliable, avoids WebSocket corruption)

2. **Streaming Audio for Long Responses**:
   - **Long text responses (>1 chunk)**: Text is split into sentence-based chunks
   - **Audio chunks are generated and sent sequentially** to minimize waiting time
   - **Client plays chunks as they arrive** instead of waiting for complete audio

---

## Flow 1: Socket.IO Delivery (Small Responses <500KB)

### When Used
- Calendar events (typically short responses)
- Todo operations (short confirmations)
- Small mortgage responses
- Any response with audio <500KB base64

### Call Flow

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. User speaks: "Create calendar event"
       │
       ▼
┌─────────────────────────────────────┐
│  WebRTC Voice Server               │
│  - Records audio                    │
│  - Transcribes with Deepgram        │
│  - Processes with LangGraph agent    │
│  - Generates TTS audio              │
└──────┬──────────────────────────────┘
       │
       │ 2. Check audio size
       │    audio_size = 200KB (<500KB threshold)
       │
       ▼
┌─────────────────────────────────────┐
│  Size Check: PASS                   │
│  ✅ Small enough for Socket.IO      │
└──────┬──────────────────────────────┘
       │
       │ 3. Emit via Socket.IO
       │    socketio.emit('agent_response', {
       │      text: "...",
       │      audio: "base64..."  // 200KB
       │    })
       │
       ▼
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 4. Receive event
       │    socket.on('agent_response', ...)
       │
       │ 5. Play audio immediately
       │    playAudioResponse(audio)
       │
       ▼
   ✅ Success
```

### Characteristics
- **Latency**: Low (~100-200ms after TTS completes)
- **Reliability**: Good for small payloads
- **Connection**: Requires active WebSocket connection
- **Use Case**: Real-time, small responses

---

## Flow 2: HTTP Delivery (Large Responses >500KB)

### When Used
- Mortgage responses (long explanations, ~1.4MB)
- Long agent responses
- Any response with audio >500KB base64

### Call Flow

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. User speaks: "I want to apply for mortgage"
       │
       ▼
┌─────────────────────────────────────┐
│  WebRTC Voice Server               │
│  - Records audio                    │
│  - Transcribes with Deepgram        │
│  - Processes with LangGraph agent    │
│  - Generates TTS audio              │
└──────┬──────────────────────────────┘
       │
       │ 2. Check audio size
       │    audio_size = 1.4MB (>500KB threshold)
       │
       ▼
┌─────────────────────────────────────┐
│  Size Check: FAIL                   │
│  ⚠️ Too large for Socket.IO         │
└──────┬──────────────────────────────┘
       │
       │ 3. Store in Redis
       │    redis.setex(
       │      "pending_response:{user_id}",
       │      {text, audio}, 300s
       │    )
       │
       ▼
┌─────────────────────────────────────┐
│  Send Small Notification            │
│  socketio.emit('pending_response_   │
│    available', {user_id})            │
│  // Small payload, safe for WebSocket│
└──────┬──────────────────────────────┘
       │
       │ 4. Notification received
       │    (Client may disconnect during TTS)
       │
       ▼
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 5a. HTTP Polling (every 1s for 15s)
       │     GET /webrtc/pending-response?user_id=...
       │
       │ 5b. OR receives notification
       │     socket.on('pending_response_available')
       │     → triggers immediate HTTP fetch
       │
       ▼
┌─────────────────────────────────────┐
│  HTTP Endpoint                      │
│  /webrtc/pending-response           │
│  - Fetches from Redis               │
│  - Returns {text, audio}            │
│  - Deletes from Redis (one-time)    │
└──────┬──────────────────────────────┘
       │
       │ 6. Client receives response
       │    {success: true, text: "...", audio: "..."}
       │
       │ 7. Play audio
       │    playAudioResponse(audio)
       │
       ▼
   ✅ Success
```

### Characteristics
- **Latency**: Slightly higher (~500ms-2s due to polling)
- **Reliability**: Excellent (works even if client disconnects)
- **Connection**: Works with HTTP (no WebSocket required)
- **Use Case**: Large responses, unreliable connections

---

## Decision Point: Size Check

The system automatically routes responses based on size:

```python
AUDIO_SIZE_THRESHOLD = 500000  # 500KB base64 (~375KB binary)

if audio_size > AUDIO_SIZE_THRESHOLD:
    # HTTP delivery
    - Store in Redis
    - Send small notification via Socket.IO
    - Client polls HTTP endpoint
else:
    # Socket.IO delivery
    - Send directly via Socket.IO
    - Client receives immediately
```

---

## Comparison Table

| Aspect | Socket.IO | HTTP |
|--------|----------|------|
| **Payload Size** | <500KB | >500KB |
| **Latency** | Low (~100-200ms) | Medium (~500ms-2s) |
| **Reliability** | Good (requires active connection) | Excellent (works after disconnect) |
| **WebSocket Impact** | Safe for small payloads | Avoids corruption |
| **Use Cases** | Calendar, todos, short responses | Mortgage, long explanations |
| **Client Polling** | Not needed | Polls every 1s for 15s |
| **Delivery Confirmation** | Socket.IO callback | HTTP response |

---

## Why This Matters

### Problem Before Fix
- Large responses (>1MB) sent via Socket.IO
- WebSocket encoding errors: `Could not decode a text frame as UTF-8`
- Continuous disconnect/reconnect cycles
- Responses lost

### Solution
- Size-based routing
- Large responses use HTTP (reliable)
- Small responses use Socket.IO (fast)
- Best of both worlds

---

## Code Locations

### Size Check
- **File**: `convonet/webrtc_voice_server.py`
- **Line**: ~2059-2108
- **Function**: `process_audio_async()` → response emission

### HTTP Endpoint
- **File**: `convonet/routes.py`
- **Route**: `/webrtc/pending-response`
- **Method**: GET
- **Returns**: `{success, pending, text, audio}`

### Client Polling
- **File**: `templates/webrtc_voice_assistant.html`
- **Function**: `pollForPendingResponse()`
- **Interval**: Every 1 second for 15 seconds
- **Trigger**: After authentication

### Notification Handler
- **File**: `templates/webrtc_voice_assistant.html`
- **Event**: `socket.on('pending_response_available')`
- **Action**: Triggers immediate HTTP fetch

---

## Example Scenarios

### Scenario 1: Calendar Event (Small Response)
```
User: "Create calendar event for tomorrow at 2pm"
→ Agent: "I've created a calendar event..."
→ TTS Audio: 150KB
→ Size Check: 150KB < 500KB ✅
→ Delivery: Socket.IO (immediate)
→ Result: Fast, reliable delivery
```

### Scenario 2: Mortgage Application (Large Response)
```
User: "I want to apply for mortgage"
→ Agent: "Great! I can see you already have a mortgage application..."
→ TTS Audio: 1.4MB
→ Size Check: 1.4MB > 500KB ⚠️
→ Delivery: HTTP (via polling)
→ Result: Reliable delivery, avoids WebSocket corruption
```

---

## Benefits

1. **Prevents WebSocket Corruption**: Large payloads no longer break connections
2. **Automatic Routing**: System chooses best method automatically
3. **Backward Compatible**: Small responses still use Socket.IO (fast)
4. **Reliable**: Large responses always delivered via HTTP
5. **No Code Changes Needed**: Works transparently for all agent types

---

## Flow 3: Streaming Audio Delivery (Long Responses)

### When Used
- Responses split into multiple sentence-based chunks (typically >400 characters)
- Automatically enabled for long responses to minimize waiting time
- Works with both Socket.IO and HTTP delivery methods

### Call Flow

```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 1. User speaks: "Tell me about mortgage application process"
       │
       ▼
┌─────────────────────────────────────┐
│  WebRTC Voice Server               │
│  - Records audio                    │
│  - Transcribes with Deepgram        │
│  - Processes with LangGraph agent   │
│  - Gets long text response          │
└──────┬──────────────────────────────┘
       │
       │ 2. Split text into chunks
       │    chunks = ["First sentence...", "Second sentence...", ...]
       │
       ▼
┌─────────────────────────────────────┐
│  For each chunk:                    │
│  1. Generate TTS audio              │
│  2. Emit 'audio_chunk' event        │
│  3. Client receives and queues      │
│  4. Client plays sequentially       │
└──────┬──────────────────────────────┘
       │
       │ 3. Send text immediately
       │    socketio.emit('agent_response', {text: "..."})
       │
       │ 4. Send audio chunks as ready
       │    socketio.emit('audio_chunk', {
       │      chunk_index: 0,
       │      audio: "base64...",
       │      is_final: false
       │    })
       │    ... (more chunks)
       │
       │ 5. Send completion
       │    socketio.emit('audio_stream_complete')
       │
       ▼
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │
       │ 6. Display text immediately
       │    addTranscript('agent', text)
       │
       │ 7. Queue and play chunks
       │    audioChunkQueue.push(chunk)
       │    playAudioChunksSequentially()
       │    → Play chunk 0, wait for end
       │    → Play chunk 1, wait for end
       │    → ... (sequential playback)
       │
       ▼
   ✅ Success (audio starts playing quickly)
```

### Characteristics
- **Latency**: Much lower - audio starts playing as soon as first chunk is ready
- **Perceived Wait Time**: Reduced from "full TTS time" to "first chunk TTS time"
- **User Experience**: More responsive, natural conversation flow
- **Compatibility**: Works with both Socket.IO and HTTP delivery
- **Chunking Strategy**: Sentence-based splitting (preserves natural pauses)

### Benefits
1. **Faster Response**: User hears audio starting while later chunks are still being generated
2. **Better UX**: No long silence while waiting for complete audio generation
3. **Scalable**: Works for responses of any length
4. **Backward Compatible**: Short responses (<1 chunk) use original non-streaming approach

### Implementation Details

**Server Side** (`convonet/webrtc_voice_server.py`):
- `chunk_text_by_sentences()`: Splits text into sentence-based chunks (100-400 chars)
- For each chunk: Generate TTS → Emit `audio_chunk` event immediately
- Emit `audio_stream_complete` when all chunks sent

**Client Side** (`templates/webrtc_voice_assistant.html`):
- `audio_chunk` event handler: Queues chunks in `audioChunkQueue`
- `playAudioChunksSequentially()`: Plays chunks one after another
- Uses HTML5 Audio API with `onended` callback for sequential playback

### Example Timeline

**Without Streaming**:
```
User asks question
  ↓ (5s) Agent processing
  ↓ (8s) Full TTS generation (all text at once)
  ↓ Audio playback starts (13s total wait)
```

**With Streaming**:
```
User asks question
  ↓ (5s) Agent processing  
  ↓ (2s) First chunk TTS → Audio starts playing! 🎵
  ↓ (continues) Remaining chunks generated & played sequentially
  ↓ (7s total, but user hears response starting at 7s instead of 13s)
```

**Result**: User hears response starting 6 seconds earlier!
