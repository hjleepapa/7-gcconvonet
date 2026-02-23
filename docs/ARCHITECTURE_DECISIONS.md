# Architecture Decisions: Streaming, LangGraph, and Direct API Calls

## 1. Why Gemini Uses Blocking (`ainvoke`) While Others Use Streaming (`astream`)

### The Problem

**Gemini's LangChain Implementation Limitation:**
- Gemini's `astream()` in LangChain uses **blocking HTTP calls** that can't be interrupted
- This is a limitation of the `langchain-google-genai` wrapper, not Gemini itself
- The native Google GenAI SDK (used in `index.ts`) supports streaming via WebSocket

**Why It's Blocking:**
```python
# In routes.py line 1456
# Gemini's astream() uses blocking HTTP that can't be interrupted
# ainvoke() is async but still needs a timeout wrapper
```

**The Real Issue:**
- LangChain's Gemini wrapper doesn't properly implement async streaming
- It uses synchronous HTTP requests under the hood
- This blocks the event loop, preventing proper timeout handling
- `asyncio.wait_for()` can't interrupt blocking calls

### Why Claude/OpenAI Work

**Claude/OpenAI LangChain Implementation:**
- Properly implements async streaming with `astream()`
- Uses non-blocking HTTP/WebSocket connections
- Can be interrupted by `asyncio.wait_for()` timeouts
- Processes state updates incrementally

### Solution: Use Native SDK (Like in `index.ts`)

**Current Frontend Implementation (`index.ts`):**
```typescript
// Uses native Google GenAI SDK with WebSocket streaming
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
const session = ai.live.connect({
  model: 'gemini-2.5-flash-native-audio-preview-09-2025',
  callbacks: {
    onmessage: async (msg) => {
      // Streams audio and text in real-time
    }
  }
});
```

**This works because:**
- Native SDK uses WebSocket (`ai.live.connect()`)
- Real-time bidirectional streaming
- No blocking HTTP calls
- Proper async/await support

---

## 2. Can We Switch to Streaming Audio Directly?

### Current Architecture

**Backend (REST API Approach):**
```
Browser → WebSocket (Socket.IO) → Flask → Deepgram STT → LangGraph → Deepgram TTS → Browser
         (Audio chunks)           (REST)   (REST)         (REST)      (REST)        (Audio)
```

**Problems:**
- Multiple REST API calls (Deepgram STT, LangGraph, Deepgram TTS)
- Latency accumulates: STT (1-2s) + LLM (2-5s) + TTS (1-2s) = 4-9s total
- No real-time streaming
- Audio must be complete before processing

### Proposed: Direct Streaming Architecture

**Option A: Browser → LLM Direct (Like `index.ts`)**
```
Browser → Native LLM SDK (WebSocket) → LLM API
         (Audio stream)                (Audio/text stream)
```

**Benefits:**
- ✅ Real-time bidirectional streaming
- ✅ Lower latency (no intermediate server)
- ✅ Native audio streaming (Gemini Live API)
- ✅ Works in `index.ts` already

**Limitations:**
- ❌ No server-side tool execution (MCP tools, database)
- ❌ No conversation persistence (Redis checkpoints)
- ❌ No authentication/authorization
- ❌ API keys exposed to browser (security risk)

**Option B: Hybrid Approach (Recommended)**
```
Browser → WebSocket → Flask → LangGraph (Streaming) → LLM API
         (Audio)      (Stream)  (State updates)        (Stream)
```

**Benefits:**
- ✅ Server-side tool execution (MCP, database)
- ✅ Conversation persistence (Redis)
- ✅ Security (API keys on server)
- ✅ Streaming responses (lower latency)
- ✅ Can use native SDK for Gemini

**Implementation:**
1. Use native Gemini SDK on backend (not LangChain wrapper)
2. Stream audio/text via WebSocket
3. Execute tools server-side
4. Stream results back to browser

---

## 3. Benefits of LangGraph vs Direct API Calls

### What LangGraph Provides

#### 1. **State Management**
```python
# LangGraph maintains conversation state
AgentState(
    messages=[...],  # Full conversation history
    authenticated_user_id="...",
    authenticated_user_name="...",
    is_authenticated=True
)
```

**Benefits:**
- Persistent conversation context
- Multi-turn conversations
- User authentication state
- Tool execution history

**Direct API Calls:**
- ❌ No built-in state management
- ❌ Must manually track conversation history
- ❌ No authentication context
- ❌ Stateless (lose context on refresh)

#### 2. **Tool Orchestration**
```python
# LangGraph automatically:
# 1. Detects when tools are needed
# 2. Executes tools
# 3. Passes results back to LLM
# 4. Continues conversation

builder.add_conditional_edges(
    "assistant",
    should_continue,  # Decides: use tools or respond
)
builder.add_edge("tools", "assistant")  # Loop back after tool execution
```

**Benefits:**
- ✅ Automatic tool selection
- ✅ Multi-step tool chains
- ✅ Error handling
- ✅ Tool result integration

**Direct API Calls:**
- ❌ Manual tool detection
- ❌ Manual tool execution
- ❌ Manual error handling
- ❌ Manual result integration

#### 3. **Checkpointing & Recovery**
```python
# LangGraph checkpoints state to Redis
checkpointer = RedisSaver(redis_client)
graph = builder.compile(checkpointer=checkpointer)

# Can recover from crashes
state = graph.get_state(config={"thread_id": "user-123"})
```

**Benefits:**
- ✅ Conversation recovery after crashes
- ✅ Multi-user support (thread_id)
- ✅ State persistence
- ✅ Resume interrupted conversations

**Direct API Calls:**
- ❌ No checkpointing
- ❌ Lose state on crash
- ❌ Must rebuild context manually

#### 4. **Conditional Routing**
```python
def should_continue(state: AgentState):
    """Decide: use tools or respond to user"""
    messages = state.messages
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "tools"  # Execute tools
    return "end"  # Respond to user
```

**Benefits:**
- ✅ Intelligent routing (tools vs response)
- ✅ Multi-step reasoning
- ✅ Complex workflows
- ✅ Transfer intent detection

**Direct API Calls:**
- ❌ Manual routing logic
- ❌ Must implement in application code
- ❌ More complex error handling

#### 5. **Multi-Provider Support**
```python
# LangGraph abstracts provider differences
provider_manager = LLMProviderManager()
llm = provider_manager.create_llm(provider="gemini", tools=tools)

# Same graph works with any provider
graph = builder.compile()
```

**Benefits:**
- ✅ Unified interface (Gemini, Claude, OpenAI)
- ✅ Easy provider switching
- ✅ Consistent tool execution
- ✅ Provider-agnostic code

**Direct API Calls:**
- ❌ Different APIs for each provider
- ❌ Must implement provider-specific logic
- ❌ More code to maintain

### When to Use Direct API Calls

**Use Direct API Calls When:**
- ✅ Simple single-turn conversations
- ✅ No tool execution needed
- ✅ No state persistence needed
- ✅ Client-side only (like `index.ts` demo)
- ✅ Maximum performance (lowest latency)

**Use LangGraph When:**
- ✅ Complex multi-turn conversations
- ✅ Tool execution required (MCP, database)
- ✅ State persistence needed
- ✅ Server-side processing
- ✅ Multi-user support
- ✅ Authentication/authorization

---

## Recommended Architecture

### Current: REST API with LangGraph
```
Browser → WebSocket → Flask → LangGraph → LLM (REST)
         (Audio)      (REST)   (State)      (Blocking)
```

**Pros:**
- ✅ Server-side tools (MCP, database)
- ✅ State persistence
- ✅ Security

**Cons:**
- ❌ High latency (4-9s)
- ❌ No real-time streaming
- ❌ Gemini blocking issue

### Recommended: Hybrid Streaming
```
Browser → WebSocket → Flask → LangGraph → Native SDK → LLM (WebSocket)
         (Audio)      (Stream)  (State)    (Stream)     (Stream)
```

**Implementation:**
1. **For Gemini**: Use native `@google/genai` SDK on backend (not LangChain)
2. **For Claude/OpenAI**: Keep LangChain (works fine)
3. **Stream responses**: Use WebSocket for real-time updates
4. **Tool execution**: Server-side via LangGraph
5. **State management**: Keep Redis checkpoints

**Benefits:**
- ✅ Real-time streaming (lower latency)
- ✅ Server-side tools
- ✅ State persistence
- ✅ Security
- ✅ Fixes Gemini blocking issue

---

## Summary

1. **Why Gemini Blocks**: LangChain wrapper limitation, not Gemini itself
2. **Streaming Audio**: Yes, use native SDK for Gemini, WebSocket for others
3. **LangGraph Benefits**: State management, tool orchestration, checkpointing, routing, multi-provider support

**Best Approach**: Hybrid - Use native SDK for Gemini streaming, keep LangGraph for orchestration, stream via WebSocket.

