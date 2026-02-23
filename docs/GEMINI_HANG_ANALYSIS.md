# Gemini Hang Analysis & Function Flow Explanation

## 🔴 **ROOT CAUSE IDENTIFIED**

The hang occurs in this exact sequence:
1. `process_audio_async()` → ThreadPoolExecutor
2. `run_async_in_thread()` → Creates new event loop
3. `process_with_agent()` → Calls `_run_agent_async()`
4. `_run_agent_async()` → Calls `_get_agent_graph()` with 8s timeout
5. `_get_agent_graph()` → Creates `TodoAgent(tools=tools, provider="gemini", model="gemini-3-pro-preview")`
6. **`TodoAgent.__init__()` → Calls `provider_manager.create_llm(provider="gemini", tools=tools)`**
7. **`create_llm()` → Calls `llm.bind_tools(tools)` for Gemini**
8. **`bind_tools()` HANGS HERE** ⚠️

## ❌ **MCP Tools Are NOT The Problem**

**Evidence:**
- ✅ MCP tools are pre-loaded at startup: "✅ MCP tools pre-loaded and cached: 36 tools"
- ✅ Tools are already in memory when `_get_agent_graph()` is called
- ✅ The hang happens AFTER tools are loaded, during `bind_tools()` call

**The Real Problem:**
- `llm.bind_tools(tools)` for Gemini can hang indefinitely
- This is a known issue with Gemini's tool binding implementation
- Even with pre-loaded tools, binding them to the Gemini model hangs

---

## 📋 **Detailed Function Flow**

### **webrtc_voice_server.py Functions**

#### 1. `init_socketio(socketio_instance, app)`
**Purpose:** Initialize WebSocket handlers for voice assistant
**Key Functions:**
- `handle_connect()`: Creates session in Redis when client connects
- `handle_disconnect()`: Cleans up session when client disconnects
- `handle_authenticate()`: Validates PIN and stores user info
- `handle_start_recording()`: Starts audio recording session
- `handle_audio_data()`: Receives audio chunks from client
- `handle_stop_recording()`: Stops recording and triggers processing

#### 2. `process_audio_async(session_id, audio_buffer)`
**Purpose:** Main audio processing pipeline (runs in background task)
**Flow:**
1. Gets session data from Redis
2. Transcribes audio with Deepgram
3. Checks for transfer intent
4. **Calls `process_with_agent()` in ThreadPoolExecutor** ← HANGS HERE
5. Generates TTS response
6. Sends response to client

**Critical Section (Lines 1229-1332):**
```python
def run_async_in_thread():
    # Creates new event loop in separate thread
    new_loop = asyncio.new_event_loop()
    # Calls process_with_agent with 10s timeout
    result = new_loop.run_until_complete(
        asyncio.wait_for(
            process_with_agent(...),
            timeout=10.0
        )
    )
```

#### 3. `process_with_agent(text, user_id, user_name)`
**Purpose:** Wrapper that calls `_run_agent_async()` from routes.py
**Location:** Line 1399
**What it does:**
- Sets up Sentry context
- Calls `_run_agent_async()` from `routes.py`
- Returns response and transfer marker

---

### **routes.py Functions**

#### 1. `_get_agent_graph(provider, user_id)`
**Purpose:** Initialize and cache the agent graph
**Location:** Line 889
**Flow:**
1. Gets provider preference from Redis (user-specific → global → env)
2. Checks if cached graph exists (provider + model match)
3. If not cached:
   - Loads MCP config
   - **Uses pre-loaded MCP tools from `_mcp_tools_cache`** ✅
   - Adds transfer tools
   - **Creates `TodoAgent(tools=tools, provider=provider, model=model)`** ← HANGS HERE
4. Caches graph for future requests

**Critical Section (Lines 1114-1125):**
```python
# MCP tools are already cached, no loading needed
if _mcp_tools_cache is not None:
    tools = _mcp_tools_cache.copy()

# This is where it hangs - TodoAgent.__init__ calls bind_tools()
todo_agent = TodoAgent(tools=tools, provider=provider, model=current_model)
```

#### 2. `_run_agent_async(prompt, user_id, user_name, reset_thread, include_metadata)`
**Purpose:** Execute the agent with a prompt
**Location:** Line 1195
**Flow:**
1. Gets agent graph (calls `_get_agent_graph()` with 8s timeout for Gemini)
2. Creates input state with user message
3. Streams through graph to execute agent
4. Returns response with metadata

**Critical Section (Lines 1220-1229):**
```python
# This timeout should catch the hang, but it doesn't work
agent_graph = await asyncio.wait_for(
    _get_agent_graph(user_id=user_id),
    timeout=8.0  # 8s for Gemini
)
```

#### 3. `_preload_mcp_tools()` / `preload_mcp_tools_sync()`
**Purpose:** Pre-load MCP tools at startup to avoid loading during requests
**Location:** Line 778
**What it does:**
- Creates MCP client
- Calls `client.get_tools()` with 10s timeout
- Caches tools in `_mcp_tools_cache`
- **This works fine** ✅

---

### **assistant_graph_todo.py Functions**

#### 1. `TodoAgent.__init__(name, model, provider, tools, system_prompt)`
**Purpose:** Initialize the agent with LLM and tools
**Location:** Line 39
**Flow:**
1. Stores tools and provider
2. **Calls `provider_manager.create_llm(provider, model, tools=tools)`** ← HANGS HERE
3. Builds LangGraph state graph
4. Caches graph

**Critical Section (Lines 286-293):**
```python
# This calls create_llm which calls bind_tools() for Gemini
self.llm = provider_manager.create_llm(
    provider=self.provider,
    model=self.model,
    temperature=0.0,
    tools=self.tools,  # Pre-loaded MCP tools
)
```

#### 2. `TodoAgent.build_graph()`
**Purpose:** Build the LangGraph state graph
**Location:** Line 330
**What it does:**
- Creates StateGraph with AgentState
- Adds "assistant" node (LLM)
- Adds "tools" node (tool execution)
- Adds conditional edges
- Compiles graph

---

### **llm_provider_manager.py Functions**

#### 1. `create_llm(provider, model, temperature, tools)`
**Purpose:** Create LLM instance and bind tools
**Location:** Line ~80-150 (approximate)
**Flow:**
1. Gets provider-specific LLM class
2. Creates LLM instance
3. **Calls `llm.bind_tools(tools)`** ← HANGS HERE FOR GEMINI
4. Returns bound LLM

**The Problem:**
- For Gemini: `ChatGoogleGenerativeAI(...).bind_tools(tools)` can hang
- This is a known issue with Gemini's tool binding
- Even with pre-loaded tools, the binding operation itself hangs

---

## 🎯 **Why Timeouts Don't Work**

1. **`asyncio.wait_for()` timeout (8s)**: Should catch the hang, but `bind_tools()` is **synchronous** and blocks the event loop
2. **ThreadPoolExecutor timeout (15s)**: Should catch it, but the thread is blocked in synchronous `bind_tools()` call
3. **Worker timeout (30s)**: Gunicorn kills the worker because it's completely blocked

**The Issue:**
- `bind_tools()` is a **synchronous blocking call** inside an async function
- It blocks the event loop, preventing `asyncio.wait_for()` from timing out
- The thread is blocked, so `future.result(timeout=15.0)` can't interrupt it

---

## ✅ **Solution: Skip Tool Binding for Gemini**

Since MCP tools are NOT the problem, but `bind_tools()` IS, we should:

1. **Skip tool binding for Gemini** if it takes too long
2. **Use tools without binding** (manual tool calling)
3. **Or use a different approach** for Gemini tool calling

**Recommended Fix:**
- Add a timeout wrapper around `bind_tools()` using threading
- If it times out, skip binding and use manual tool calling
- This allows Gemini to work without hanging

---

## 📚 **Complete Function Reference**

### **webrtc_voice_server.py - Complete Function List**

#### **1. `init_socketio(socketio_instance, app)` (Line 421)**
**Purpose:** Main initialization function for WebSocket handlers
**What it does:**
- Stores global `socketio` and `flask_app` references
- Registers all Socket.IO event handlers
- Sets up session management

**Registered Handlers:**
- `handle_connect()`: Client connects → Create session
- `handle_disconnect()`: Client disconnects → Cleanup session
- `handle_authenticate()`: PIN validation → Store user info
- `handle_start_recording()`: Start audio capture
- `handle_audio_data()`: Receive audio chunks
- `handle_stop_recording()`: Stop recording → Trigger processing

#### **2. `process_audio_async(session_id, audio_buffer)` (Line 1022)**
**Purpose:** Main audio processing pipeline
**Execution:** Runs in background task via `socketio.start_background_task()`
**Flow:**
1. **Session Retrieval** (Lines 1034-1057)
   - Gets session from Redis or memory
   - Extracts user_id and user_name
   
2. **Transcription** (Lines 1059-1095)
   - Calls `transcribe_audio_with_deepgram_webrtc()`
   - Validates transcription result
   - Sends transcription to client
   
3. **Transfer Intent Check** (Lines 1116-1120)
   - Calls `has_transfer_intent()` to detect transfer requests
   - If transfer requested, initiates transfer flow
   
4. **Agent Processing** (Lines 1200-1342) ⚠️ **HANGS HERE**
   - Emits status message
   - **Creates ThreadPoolExecutor**
   - **Calls `run_async_in_thread()` which calls `process_with_agent()`**
   - Waits for result with 15s timeout
   
5. **TTS Generation** (Lines 1359-1383)
   - Generates speech using Deepgram TTS
   - Sends audio response to client

#### **3. `run_async_in_thread()` (Line 1229) - NESTED FUNCTION**
**Purpose:** Run async code in separate thread with its own event loop
**Why:** Isolates async execution from eventlet worker
**Flow:**
1. Creates new event loop for thread
2. Calls `process_with_agent()` with 10s timeout
3. Returns result or raises timeout

**Critical Issue:**
- `process_with_agent()` → `_run_agent_async()` → `_get_agent_graph()` → `TodoAgent.__init__()` → `bind_tools()`
- `bind_tools()` is **synchronous** and blocks the thread
- Timeout can't interrupt blocking call

#### **4. `process_with_agent(text, user_id, user_name)` (Line 1399)**
**Purpose:** Wrapper function that calls `_run_agent_async()` from routes.py
**What it does:**
- Sets up Sentry context
- Imports `_run_agent_async` from `routes.py`
- Calls it with proper parameters
- Returns (response, transfer_marker) tuple

#### **5. `send_welcome_greeting(session_id, user_name)` (Line 991)**
**Purpose:** Generate and send welcome message after authentication
**What it does:**
- Generates welcome text
- Creates TTS audio with Deepgram
- Sends to client via Socket.IO

#### **6. Helper Functions:**
- `build_customer_profile_from_session()`: Build customer profile for call center
- `cache_call_center_profile()`: Cache profile in Redis
- `is_transfer_in_progress()`: Check transfer flag
- `set_transfer_flag()`: Set transfer flag
- `initiate_agent_transfer()`: Create Twilio call for transfer
- `sentry_capture_voice_event()`: Log events to Sentry
- `sentry_capture_redis_operation()`: Log Redis operations

---

### **routes.py - Complete Function List**

#### **1. `_get_agent_graph(provider, user_id)` (Line 889)**
**Purpose:** Initialize and cache the LangGraph agent graph
**Returns:** `CompiledStateGraph` instance
**Caching Strategy:**
- Checks if cached graph exists (provider + model match)
- If match → returns cached graph
- If no match → creates new graph and caches it

**Flow:**
1. **Provider Selection** (Lines 899-937)
   - Checks user-specific preference: `user:{user_id}:llm_provider`
   - Falls back to global: `user:default:llm_provider`
   - Falls back to env: `LLM_PROVIDER` or "claude"
   
2. **Model Selection** (Lines 939-945)
   - Gemini → `GOOGLE_MODEL` or "gemini-3-pro-preview"
   - OpenAI → `OPENAI_MODEL` or "gpt-4o"
   - Claude → `ANTHROPIC_MODEL` or "claude-sonnet-4-20250514"
   
3. **Cache Check** (Lines 949-954)
   - Returns cached graph if provider + model match
   
4. **Tool Loading** (Lines 1014-1081)
   - **Uses pre-loaded `_mcp_tools_cache`** ✅ (MCP tools already loaded)
   - Adds transfer tools
   - Adds Composio tools (if available)
   
5. **Agent Creation** (Lines 1114-1125) ⚠️ **HANGS HERE**
   - Creates `TodoAgent(tools=tools, provider=provider, model=model)`
   - This calls `TodoAgent.__init__()` which calls `bind_tools()`
   - **`bind_tools()` hangs for Gemini**
   
6. **Caching** (Lines 1129-1132)
   - Caches graph, model, and provider for future requests

#### **2. `_run_agent_async(prompt, user_id, user_name, reset_thread, include_metadata)` (Line 1195)**
**Purpose:** Execute the agent with a user prompt
**Returns:** Response string or dict with metadata
**Flow:**
1. **Agent Graph Initialization** (Lines 1220-1248)
   - Calls `_get_agent_graph()` with timeout
   - **8s timeout for Gemini, 12s for others**
   - If timeout → returns error message
   
2. **State Creation** (Lines 1269-1286)
   - Creates `AgentState` with user message
   - Sets up thread_id for conversation continuity
   
3. **Graph Execution** (Lines 1288-1400+)
   - Streams through graph with `agent_graph.astream()`
   - Processes each state update
   - Extracts tool calls and results
   - Returns final response

#### **3. `_preload_mcp_tools()` (Line 778) - ASYNC**
**Purpose:** Pre-load MCP tools at startup
**What it does:**
- Creates MCP client
- Calls `client.get_tools()` with 10s timeout
- Caches tools in `_mcp_tools_cache`
- **This works fine** ✅

#### **4. `preload_mcp_tools_sync()` (Line 820) - SYNC WRAPPER**
**Purpose:** Synchronous wrapper for `_preload_mcp_tools()`
**What it does:**
- Creates new event loop
- Runs `_preload_mcp_tools()` in that loop
- Called at app startup in `app.py`

---

### **assistant_graph_todo.py - Complete Function List**

#### **1. `TodoAgent.__init__(name, model, provider, tools, system_prompt)` (Line 39)**
**Purpose:** Initialize the agent with LLM and build graph
**Flow:**
1. **Store Parameters** (Lines 256-280)
   - Stores name, system_prompt, tools, provider, model
   
2. **Provider Validation** (Lines 256-283)
   - Gets `LLMProviderManager` instance
   - Validates provider is available
   
3. **LLM Creation** (Lines 286-326) ⚠️ **HANGS HERE**
   - Calls `provider_manager.create_llm(provider, model, tools=tools)`
   - This calls `create_llm()` in `llm_provider_manager.py`
   - Which calls `llm.bind_tools(tools)` for Gemini
   - **`bind_tools()` hangs**
   
4. **Graph Building** (Line 328)
   - Calls `self.build_graph()` to create LangGraph

#### **2. `TodoAgent.build_graph()` (Line 330)**
**Purpose:** Build the LangGraph state graph
**Returns:** `CompiledStateGraph`
**What it does:**
- Creates `StateGraph(AgentState)`
- Adds "assistant" node (LLM invocation)
- Adds "tools" node (tool execution)
- Adds conditional edges (tool calling logic)
- Compiles graph with checkpointer

---

### **llm_provider_manager.py - Complete Function List**

#### **1. `LLMProviderManager.__init__()` (Line 17)**
**Purpose:** Initialize provider registry
**What it does:**
- Calls `_initialize_providers()`
- Registers Claude, Gemini, OpenAI providers

#### **2. `_initialize_providers()` (Line 21)**
**Purpose:** Detect and register available LLM providers
**What it does:**
- Checks for API keys
- Imports provider classes
- Registers provider info (class, name, models, etc.)

#### **3. `create_llm(provider, model, temperature, tools)` (Line 84)** ⚠️ **HANGS HERE**
**Purpose:** Create LLM instance and bind tools
**Flow:**
1. **Validation** (Lines 106-123)
   - Validates provider exists
   - Checks provider is available
   - Gets API key
   
2. **LLM Creation** (Lines 134-184)
   - Creates provider-specific LLM instance
   - For Gemini: Uses `ChatGoogleGenerativeAI`
   
3. **Tool Binding** (Lines 186-220) ⚠️ **HANGS HERE**
   - If tools provided:
     - For Gemini: Calls `llm.bind_tools(tools)` with 5s timeout
     - **This is where it hangs** - timeout doesn't work
   - For Claude/OpenAI: Normal binding (works fine)

**The Problem:**
- `bind_tools()` for Gemini is **synchronous blocking call**
- Timeout wrapper (5s) doesn't work because call blocks thread
- Event loop can't interrupt blocking call

---

## 🎯 **Answer: MCP Tools Are NOT The Problem**

**Evidence:**
1. ✅ MCP tools are pre-loaded at startup: "✅ MCP tools pre-loaded and cached: 36 tools"
2. ✅ Tools are already in memory when `_get_agent_graph()` is called
3. ✅ The hang happens AFTER tools are loaded, during `bind_tools()` call
4. ✅ Logs show: "✅ Using cached MCP tools (36 tools)" before the hang

**The Real Problem:**
- `llm.bind_tools(tools)` for Gemini hangs
- This is a **synchronous blocking call** that can't be interrupted
- Even with pre-loaded tools, binding them to Gemini model hangs
- The timeout wrapper in `llm_provider_manager.py` (5s) doesn't work because the call blocks the thread

**Solution:**
- Skip `bind_tools()` for Gemini entirely
- Use manual tool calling instead
- Or use a different Gemini model that doesn't hang

