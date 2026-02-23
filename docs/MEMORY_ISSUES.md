# Memory Issues and Solutions

## Problem: 512MB RAM is Too Small

### Current Memory Usage Breakdown

Your application stack requires significant memory:

1. **Python Runtime**: ~50-100MB
2. **Flask/Gunicorn Worker**: ~100-150MB
3. **MCP Server Subprocess**: ~100-150MB (separate Python process)
4. **Database Connections** (SQLAlchemy): ~20-50MB
5. **Redis Client**: ~10-20MB
6. **LangChain/LangGraph**: ~50-100MB
7. **LLM SDKs** (Anthropic, Google, OpenAI): ~30-50MB each
8. **WebRTC Audio Processing**: ~20-50MB
9. **Agent Monitor Data** (Redis): Variable
10. **Operating System**: ~50-100MB

**Total Estimated**: **500-800MB** under normal load, **800MB-1.2GB** under heavy load

### Why 512MB Fails

The `BrokenPipeError` in MCP servers indicates:

1. **Out of Memory (OOM)**: OS kills processes when memory is exhausted
2. **Process Death**: MCP server subprocess dies, parent tries to write to closed pipe
3. **Intermittent Failures**: Works when memory is available, fails when memory is tight

### Error Pattern

```
BrokenPipeError: [Errno 32] Broken pipe
  File ".../mcp/server/stdio.py", line 81, in stdout_writer
    await stdout.flush()
```

This happens when:
- MCP server process is killed by OS (OOM killer)
- Parent process closes pipe before child finishes
- Memory pressure causes process crashes

## Solutions

### Option 1: Increase RAM (Recommended) ⭐

**Minimum**: 1GB RAM
**Recommended**: 2GB RAM for production

Update `render.yaml`:
```yaml
services:
  - type: web
    name: convonet-todo-app
    # Add plan specification (if Render supports it)
    # Or upgrade via Render dashboard
```

**Render Pricing**:
- Free tier: 512MB (current - insufficient)
- Starter: 1GB (~$7/month) - **Minimum recommended**
- Standard: 2GB (~$25/month) - **Recommended for production**

### Option 2: Optimize Memory Usage (Short-term)

#### A. Reduce Database Connection Pool
Already optimized: `pool_size=1, max_overflow=0`

#### B. Limit MCP Server Processes
Currently only 1 MCP server (`db_todo.py`), which is good.

#### C. Add MCP Server Restart Logic
Handle `BrokenPipeError` gracefully:

```python
# In routes.py or assistant_graph_todo.py
async def safe_mcp_tool_call(tool_name, args, max_retries=2):
    """Call MCP tool with automatic retry on BrokenPipeError"""
    for attempt in range(max_retries):
        try:
            result = await tool.call(args)
            return result
        except BrokenPipeError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ MCP server crashed, restarting... (attempt {attempt + 1}/{max_retries})")
                # Clear cache to force MCP server restart
                global _mcp_tools_cache
                _mcp_tools_cache = None
                await asyncio.sleep(1)  # Wait for restart
                continue
            else:
                return "I encountered a system error. Please try again."
```

#### D. Reduce Agent Monitor Data Retention
Currently 7 days, reduce to 1-2 days:

```python
# In agent_monitor.py
self.redis.set(interaction_key, interaction_data, expire=86400 * 1)  # 1 day instead of 7
```

#### E. Limit Concurrent Requests
Add request queuing to prevent memory spikes:

```python
# In routes.py
from asyncio import Semaphore

# Limit concurrent agent executions
MAX_CONCURRENT_AGENTS = 2  # Adjust based on memory
agent_semaphore = Semaphore(MAX_CONCURRENT_AGENTS)

async def _run_agent_async(...):
    async with agent_semaphore:
        # Existing agent execution code
        ...
```

### Option 3: Use External MCP Server (Advanced)

Run MCP server as separate service (not subprocess):

1. Deploy MCP server as separate Render service
2. Use HTTP transport instead of stdio
3. Reduces memory pressure on main service

**Trade-off**: More complex deployment, but better isolation

## Immediate Actions

### 1. Upgrade RAM (Best Solution)
- Go to Render Dashboard
- Select your service
- Upgrade to at least 1GB RAM (Starter plan)

### 2. Add Error Handling (Quick Fix)
Add `BrokenPipeError` handling in `assistant_graph_todo.py`:

```python
# In tools_node function
except BrokenPipeError as e:
    print(f"⚠️ MCP server pipe broken: {e}", flush=True)
    # Clear cache to force restart
    from convonet.routes import _mcp_tools_cache
    import convonet.routes as routes_module
    routes_module._mcp_tools_cache = None
    result = "I encountered a connection issue. Please try again."
```

### 3. Monitor Memory Usage
Add memory monitoring:

```python
import psutil
import os

def log_memory_usage():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"📊 Memory usage: {memory_mb:.1f}MB", flush=True)
```

## Testing After Upgrade

1. **Monitor logs** for `BrokenPipeError` - should disappear
2. **Check response times** - should be more consistent
3. **Test concurrent requests** - should handle multiple users
4. **Monitor memory** - should stay under 80% of allocated RAM

## Expected Results

### With 512MB (Current)
- ❌ Intermittent `BrokenPipeError`
- ❌ MCP server crashes
- ❌ Timeouts under load
- ❌ Unreliable tool execution

### With 1GB RAM
- ✅ Stable MCP server connections
- ✅ Consistent tool execution
- ✅ Better handling of concurrent requests
- ⚠️ May still struggle under heavy load

### With 2GB RAM
- ✅ Excellent stability
- ✅ Handles concurrent requests well
- ✅ Room for growth
- ✅ Production-ready

## Conclusion

**512MB RAM is insufficient** for your application stack. The intermittent failures are directly related to memory pressure causing process crashes.

**Recommended Action**: Upgrade to at least 1GB RAM (Starter plan) immediately. For production use, 2GB RAM is recommended.

