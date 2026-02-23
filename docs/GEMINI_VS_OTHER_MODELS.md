# Gemini vs Other Models: Key Differences in Tool Calling

## 🔴 Main Differences

### 1. **Execution Method**

#### Gemini
- **Uses `ainvoke()`** (non-streaming, blocking)
- Waits for **ENTIRE** graph execution to complete before returning
- This includes: LLM call → tool execution → LLM call → tool execution → ... until done
- **Problem**: If any tool takes time, the entire `ainvoke()` blocks for that duration
- **Why**: Gemini's `astream()` uses blocking HTTP that can't be interrupted

#### Claude/OpenAI
- **Uses `astream()`** (streaming, non-blocking)
- Processes state updates incrementally
- Can handle timeouts per iteration
- **Advantage**: Can detect hangs early and timeout individual iterations

### 2. **Tool Calling Format**

#### Gemini
- Uses `functionCall` format in `additional_kwargs`
- Tool calls are embedded in response content as `functionCall` objects
- Requires special parsing: `response.additional_kwargs['candidates'][0]['content']['parts']`
- Tool binding uses `bind_tools()` which can hang

#### Claude
- Uses `tool_use` / `tool_result` format
- Standard LangChain `tool_calls` attribute
- Requires strict pairing: every `tool_use` must be immediately followed by `tool_result`
- Tool binding is straightforward

#### OpenAI
- Uses standard `tool_calls` attribute
- Tool calls are in `response.tool_calls` list
- Tool binding is straightforward

### 3. **Tool Binding**

#### Gemini
- **Problem**: `bind_tools()` can hang indefinitely
- Even with timeout wrappers, the blocking call prevents interruption
- This is a known issue with Gemini's LangChain implementation
- **Workaround**: Skip binding with `SKIP_GEMINI_TOOL_BINDING=true`

#### Claude/OpenAI
- Tool binding works reliably
- No known hanging issues

### 4. **Timeout Behavior**

#### Gemini
- `ainvoke()` timeout (20s) must account for:
  - Initial LLM call
  - Tool execution (can be slow for MCP calls, API calls)
  - Subsequent LLM calls
  - All iterations combined
- **Problem**: 20s isn't enough if tools take time
- **Worker timeout**: 120s (from render.yaml) - but worker is killed if `ainvoke()` blocks too long

#### Claude/OpenAI
- Per-iteration timeout (8s) catches hangs early
- Watchdog timeout (6s) detects stalls between iterations
- Execution timeout (15s) for overall execution
- **Advantage**: Can timeout individual slow iterations without killing entire request

## 🎯 Why Google AI Studio Works

1. **Native SDK**: Uses `@google/genai` SDK directly, not LangChain wrapper
2. **Streaming WebSocket**: Uses `ai.live.connect()` for real-time streaming
3. **Longer Timeouts**: No aggressive timeout limits
4. **Different Architecture**: Direct API calls, not through LangGraph

## 🔧 Current Implementation Issues

### Problem 1: `ainvoke()` Blocks Entire Execution
- Gemini's `ainvoke()` waits for complete graph execution
- If tools take 10s, LLM takes 5s, and there are 2 iterations:
  - Total time: (5s + 10s) × 2 = 30s
  - This exceeds the 20s timeout
  - Worker timeout (120s) is hit before `ainvoke()` completes

### Problem 2: No Incremental Processing
- Can't detect which part is slow (LLM vs tool execution)
- Can't timeout individual iterations
- All-or-nothing timeout

### Problem 3: Tool Binding Can Hang
- `bind_tools()` for Gemini can hang during initialization
- Even with pre-loaded tools, binding operation itself hangs
- Timeout wrappers don't work because call blocks thread

## ✅ Recommended Solutions

### Option 1: Increase Timeout Significantly
- Increase `ainvoke_timeout` to 60s or more
- Increase Gunicorn worker timeout to 180s
- **Risk**: Still might timeout on complex tool chains

### Option 2: Use Streaming for Gemini (If Possible)
- Try using `astream()` with proper timeout handling
- Process state updates incrementally
- **Risk**: Comment says `astream()` blocks - needs testing

### Option 3: Skip Tool Binding
- Use `SKIP_GEMINI_TOOL_BINDING=true`
- Manually handle tool calling
- **Risk**: More complex implementation

### Option 4: Use Native Gemini SDK
- Replace LangChain wrapper with native `@google/genai` SDK
- Match Google AI Studio's approach
- **Risk**: Major refactoring required

## 📊 Comparison Table

| Feature | Gemini | Claude | OpenAI |
|---------|--------|-------|--------|
| Execution Method | `ainvoke()` (blocking) | `astream()` (streaming) | `astream()` (streaming) |
| Tool Format | `functionCall` in `additional_kwargs` | `tool_use` / `tool_result` | `tool_calls` attribute |
| Tool Binding | Can hang | Reliable | Reliable |
| Timeout Strategy | Single timeout for entire execution | Per-iteration + watchdog | Per-iteration + watchdog |
| Incremental Processing | ❌ No | ✅ Yes | ✅ Yes |
| Early Hang Detection | ❌ No | ✅ Yes | ✅ Yes |

