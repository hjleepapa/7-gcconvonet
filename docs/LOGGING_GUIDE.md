# Beautiful Logging & Troubleshooting Guide

## 🎯 Overview

This guide shows you how to use the new structured logging system for beautiful, easy-to-read troubleshooting logs.

---

## 🚀 Quick Start

### 1. Import the Logger

```python
from convonet.logger import get_logger

# Create a logger for your component
logger = get_logger(__name__, component="agent")
```

### 2. Use It Instead of `print()`

**Before (ugly):**
```python
print(f"❌ Agent error: {e}")
print(f"🤖 Assistant response: {response.content}")
```

**After (beautiful):**
```python
logger.error("Agent processing failed", context={"error": str(e), "user_id": user_id}, exc_info=True)
logger.agent("Generated response", user_id=user_id, response=response.content)
```

---

## 📊 Log Output Examples

### Console Output (Beautiful Colors & Icons)

```
[2025-01-15 14:23:45] 🤖 INFO     agent Generated response
Context: {
  "user_id": "user-123",
  "prompt_preview": "Create a todo for...",
  "response_preview": "I've created the todo..."
}

[2025-01-15 14:23:46] 🔧 INFO     tool Tool create_todo: executed completed (245ms)
Context: {
  "tool_name": "create_todo",
  "action": "executed",
  "success": true,
  "duration_ms": 245.23
}

[2025-01-15 14:23:47] ⚠️  WARNING  agent Agent processing took 3200ms
Context: {
  "operation": "agent_processing",
  "duration_ms": 3200.45
}
```

### Sentry Integration (Rich Context)

All logs automatically send breadcrumbs to Sentry with:
- Component tags
- Full context data
- Performance metrics
- Error stack traces

---

## 🎨 Logger Methods

### Basic Logging

```python
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)
logger.critical("Critical failure", exc_info=True)
```

### Specialized Methods

#### Agent Logging
```python
logger.agent(
    "Processing user request",
    user_id="user-123",
    prompt="Create a todo",
    response="I've created the todo..."
)
```

#### Tool Execution Logging
```python
import time
start = time.time()
result = await execute_tool()
duration = time.time() - start

logger.tool(
    tool_name="create_todo",
    action="executed",
    success=True,
    duration=duration,
    todo_id=result.id
)
```

#### Performance Logging
```python
import time
start = time.time()
await process_request()
duration = time.time() - start

logger.performance("process_request", duration, user_id=user_id)
```

---

## 🔧 Integration Examples

### Replace Print Statements in `assistant_graph_todo.py`

**Before:**
```python
print(f"🤖 Assistant response: {response.content}")
print(f"🤖 Tool calls: {response.tool_calls}")
```

**After:**
```python
from convonet.logger import get_logger

logger = get_logger(__name__, component="agent")

logger.agent(
    "Generated response",
    response=response.content,
    tool_calls_count=len(response.tool_calls) if hasattr(response, 'tool_calls') else 0
)
```

### Replace Print Statements in `routes.py`

**Before:**
```python
print(f"❌ Failed to initialize agent: {e}")
print(f"🔄 Marked user {user_id} for thread reset")
```

**After:**
```python
from convonet.logger import get_logger

logger = get_logger(__name__, component="agent")

logger.error(
    "Failed to initialize agent",
    context={"error": str(e), "user_id": user_id},
    exc_info=True
)

logger.info(
    "Thread reset initiated",
    context={"user_id": user_id, "reason": "timeout"}
)
```

### Replace Print Statements in `webrtc_voice_server.py`

**Before:**
```python
print(f"🔊 TTS generated: {len(audio_bytes)} bytes")
print(f"❌ Error generating TTS: {e}")
```

**After:**
```python
from convonet.logger import get_logger

logger = get_logger(__name__, component="websocket")

logger.info(
    "TTS audio generated",
    context={
        "audio_size_bytes": len(audio_bytes),
        "session_id": session_id
    }
)

logger.error(
    "TTS generation failed",
    context={"session_id": session_id, "error": str(e)},
    exc_info=True
)
```

---

## 🎯 Function Decorator

Automatically log function calls with timing:

```python
from convonet.logger import get_logger, log_function

logger = get_logger(__name__, component="agent")

@log_function(logger)
async def process_with_agent(text: str, user_id: str):
    # Your function code
    return result
```

This automatically logs:
- Function call with arguments
- Execution duration
- Errors with stack traces

---

## 📈 Sentry Integration

All logs automatically create Sentry breadcrumbs with:
- **Tags**: Component name, log level
- **Context**: All context data
- **Breadcrumbs**: Chronological event trail
- **Performance**: Duration metrics

### View in Sentry

1. Go to your Sentry project
2. Click on an error
3. See the "Breadcrumbs" tab with all logged events
4. See the "Context" tab with all context data

---

## 🎨 Color Coding

Logs are color-coded for easy scanning:

- **Cyan** (🔍): Debug messages
- **Green** (✅): Info/Success messages
- **Yellow** (⚠️): Warnings
- **Red** (❌): Errors
- **Magenta**: Critical errors

---

## 🔍 Troubleshooting Tips

### 1. Filter Logs by Component

```bash
# In your terminal or log viewer
grep "agent" logs.txt
grep "tool" logs.txt
grep "database" logs.txt
```

### 2. Search for Errors Only

```bash
grep "ERROR" logs.txt
grep "❌" logs.txt
```

### 3. Find Performance Issues

```bash
grep "took" logs.txt | grep -E "[0-9]{4,}ms"
```

### 4. View Context Data

All context is included in the log output as JSON, making it easy to:
- Copy/paste into debugging tools
- Search for specific values
- Parse programmatically

---

## 🔧 Tool Execution Viewer

**The most important checkpoint for troubleshooting!**

The Tool Execution Viewer tracks and displays tool call execution status in a beautiful format. See `TOOL_EXECUTION_VIEWER_GUIDE.md` for complete documentation.

### Quick Example

```python
from convonet.tool_execution_viewer import create_tracker, ToolExecutionViewer

# Create tracker
tracker = create_tracker(user_id=user_id)

# Track tool execution
execution = tracker.start_tool("create_todo", "tool_123", {"title": "Task"})
try:
    result = await execute_tool()
    tracker.complete_tool("tool_123", result)
except Exception as e:
    tracker.fail_tool("tool_123", str(e))

# Display beautiful summary
tracker.finish()
ToolExecutionViewer.display_summary(tracker)
```

This shows:
- ✅ Which tools executed successfully
- ❌ Which tools failed and why
- ⏱️  Which tools timed out
- 📊 Performance metrics for each tool
- 🔍 Full error details with stack traces

---

## 🚀 Additional Tools

### 1. **Logtail** (Recommended)
- Beautiful log viewer with search
- Real-time log streaming
- Free tier available
- https://logtail.com

### 2. **Datadog**
- Full observability platform
- Log aggregation + APM
- Paid but powerful
- https://datadoghq.com

### 3. **Better Sentry Features**
- Use Sentry's "Issues" view
- Set up alerts for errors
- Use Sentry's performance monitoring
- Create custom dashboards

### 4. **Render.com Logs**
- Built-in log viewer
- Real-time streaming
- Search and filter
- Free with Render

---

## 📝 Migration Checklist

- [ ] Replace `print()` statements with `logger.info()`
- [ ] Replace error prints with `logger.error(..., exc_info=True)`
- [ ] Add context to all log calls
- [ ] Use specialized methods (`logger.agent()`, `logger.tool()`)
- [ ] Add performance logging for slow operations
- [ ] Test Sentry breadcrumbs appear correctly

---

## 🎯 Best Practices

1. **Always include context**: User IDs, session IDs, request IDs
2. **Use appropriate log levels**: Don't log everything as ERROR
3. **Include timing**: Use `logger.performance()` for slow operations
4. **Log before and after**: Log function entry and exit
5. **Use structured data**: Pass dicts to `context`, not strings

---

## 📚 Example: Complete Migration

**Before:**
```python
def process_request(user_id, text):
    print(f"Processing request for user {user_id}")
    try:
        result = agent.process(text)
        print(f"✅ Success: {result}")
        return result
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
```

**After:**
```python
from convonet.logger import get_logger

logger = get_logger(__name__, component="agent")

def process_request(user_id, text):
    logger.info(
        "Processing user request",
        context={"user_id": user_id, "text_preview": text[:50]}
    )
    
    try:
        import time
        start = time.time()
        result = agent.process(text)
        duration = time.time() - start
        
        logger.agent(
            "Request processed successfully",
            user_id=user_id,
            response=result
        )
        logger.performance("process_request", duration, user_id=user_id)
        
        return result
    except Exception as e:
        logger.error(
            "Request processing failed",
            context={"user_id": user_id, "text": text},
            exc_info=True
        )
        raise
```

---

**Now your logs are beautiful, structured, and easy to troubleshoot! 🎉**

