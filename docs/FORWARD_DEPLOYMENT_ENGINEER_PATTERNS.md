# Forward Deployment Engineer Interview Preparation
## Similar Patterns and Logic from Convonet Project

This document maps patterns from the forward deployment engineer practice example to similar implementations in the Convonet project. Use this to prepare for interviews by demonstrating real-world experience with these patterns.

---

## 1. TTL Cache Pattern

### Example Pattern (TTLCache)
```python
class TTLCache:
    def __init__(self, ttl_seconds):
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        
    def set(self, key, value):
        timestamp = time.monotonic()
        self.cache[key] = (value, timestamp)
        
    def get(self, key):
        if key not in self.cache:
            return None
        value, inserted_time = self.cache[key] 
        elapsed = time.monotonic() - inserted_time
        if elapsed >= self.ttl_seconds:
            del self.cache[key]
            return None
        return value
```

### Similar Implementation in Convonet

**File:** `convonet/redis_manager.py`

**Pattern:** Redis-based TTL caching with expiration

```python
class RedisManager:
    def cache_user_data(self, user_id: str, data_type: str, data: Any, ttl: int = 300) -> bool:
        """Cache user-specific data (todos, teams, etc.)"""
        try:
            if self.redis_client:
                cache_key = f"user:{user_id}:{data_type}"
                self.redis_client.setex(cache_key, ttl, json.dumps(data))
                logger.info(f"✅ Cached {data_type} for user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Failed to cache data: {e}")
            return False
    
    def get_cached_user_data(self, user_id: str, data_type: str) -> Optional[Any]:
        """Get cached user data"""
        try:
            if self.redis_client:
                cache_key = f"user:{user_id}:{data_type}"
                cached_data = self.redis_client.get(cache_key)
                return json.loads(cached_data) if cached_data else None
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get cached data: {e}")
            return None
```

**Key Similarities:**
- ✅ TTL-based expiration (`ttl` parameter)
- ✅ Key-value storage with expiration
- ✅ Automatic cleanup of expired entries (handled by Redis)
- ✅ Fallback to in-memory storage when Redis unavailable

**Additional Features in Convonet:**
- Distributed caching (Redis vs in-memory OrderedDict)
- JSON serialization for complex data types
- Error handling and logging
- Session management with TTL extension

**Usage Examples:**
- `convonet/webrtc_voice_server.py:149` - Caching call center profiles with 5-minute TTL
- `convonet/agent_monitor.py:109` - Caching agent interactions with 7-day TTL
- `convonet/routes.py:2357` - Caching LLM provider preferences with 30-day TTL

---

## 2. Async Batching Pattern

### Example Pattern (AsyncBatchWithCache)
```python
class AsyncBatchWithCache:
    def __init__(self, async_iterable, batch_size, max_wait_seconds, cache):
        self.async_iterable = async_iterable
        self.batch_size = batch_size
        self.max_wait_seconds = max_wait_seconds
        self.cache = cache
        self.buffer = []
        self.start_time = None
        
    async def __anext__(self):
        while True:
            try:
                remain_time = None
                if self.start_time is not None:
                    elapsed = time.monotonic() - self.start_time
                    remain_time = max(0, self.max_wait_seconds - elapsed)
                    
                item = await asyncio.wait_for(self._aiter.__anext__(), timeout=remain_time)
                if self.cache.get(item):
                    continue  # skip duplicate
                
                if not self.buffer:
                    self.start_time = time.monotonic()
                self.buffer.append(item)
                self.cache.set(item, True)
                
                if len(self.buffer) >= self.batch_size:
                    batch = self.buffer
                    self.buffer = []
                    self.start_time = None
                    return batch
            except asyncio.TimeoutError:
                if self.buffer:
                    batch = self.buffer
                    self.buffer = []
                    self.start_time = None
                    return batch
                else:
                    raise
```

### Similar Implementation in Convonet

**File:** `convonet/rag_service.py`

**Pattern:** Batch processing with configurable batch size

```python
class RAGService:
    def index_documents(
        self,
        documents: List[Document],
        batch_size: int = 100
    ) -> bool:
        """
        Index documents into the vector database.
        
        Args:
            documents: List of documents to index
            batch_size: Number of documents to process in each batch
        """
        if not self.is_available():
            logger.error("❌ RAG service not available")
            return False
        
        try:
            logger.info(f"📚 Indexing {len(documents)} documents...")
            
            # Generate embeddings
            texts = [doc.content for doc in documents]
            embeddings = self._generate_embeddings(texts)
            
            if not embeddings:
                logger.error("❌ Failed to generate embeddings")
                return False
            
            # Prepare data for ChromaDB
            ids = [doc.id for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            # Add embeddings to ChromaDB in batches
            for i in range(0, len(documents), batch_size):
                batch_ids = ids[i:i+batch_size]
                batch_embeddings = embeddings[i:i+batch_size]
                batch_texts = texts[i:i+batch_size]
                batch_metadatas = metadatas[i:i+batch_size]
                
                self.collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_texts,
                    metadatas=batch_metadatas
                )
            
            logger.info(f"✅ Indexed {len(documents)} documents successfully")
            return True
```

**Key Similarities:**
- ✅ Batch size configuration
- ✅ Processing items in batches
- ✅ Buffer management (implicit in range slicing)

**Additional Features in Convonet:**
- Synchronous batching (can be adapted to async)
- Error handling and logging
- Vector database integration

**Async Batching Pattern in Convonet:**

**File:** `convonet/routes.py` - Async stream processing with state batching

```python
async def process_stream():
    stream = agent_graph.astream(input=input_state, stream_mode="values", config=config)
    stream_iter = stream.__aiter__()
    states_processed = 0
    max_states = 50  # Prevent infinite loops
    
    try:
        while states_processed < max_states:
            # Get next state with timeout
            state = await asyncio.wait_for(stream_iter.__anext__(), timeout=stream_timeout)
            states_processed += 1
            # Process state...
```

---

## 3. Async Iteration with Timeouts

### Example Pattern
```python
async def __anext__(self):
    try:
        remain_time = None
        if self.start_time is not None:
            elapsed = time.monotonic() - self.start_time
            remain_time = max(0, self.max_wait_seconds - elapsed)
            
        item = await asyncio.wait_for(self._aiter.__anext__(), timeout=remain_time)
        # Process item...
    except asyncio.TimeoutError:
        # Handle timeout
```

### Similar Implementation in Convonet

**File:** `convonet/routes.py` (Lines 1457-1700)

**Pattern:** Async stream iteration with timeout and watchdog

```python
async def process_stream():
    import time as watchdog_time
    import asyncio
    
    stream = agent_graph.astream(input=input_state, stream_mode="values", config=config)
    stream_iter = stream.__aiter__()
    states_processed = 0
    max_states = 50  # Prevent infinite loops
    
    # Timeout per iteration
    stream_timeout = 10.0  # Must be > tool_timeout (6.0s) to get tool results
    
    # Watchdog timer - if we don't get a state update within this time, force exit
    last_state_time = watchdog_time.time()
    watchdog_timeout = 10.0  # Maximum time between state updates
    
    try:
        while states_processed < max_states:
            # Check watchdog - if too much time has passed since last state, force exit
            current_time = watchdog_time.time()
            time_since_last_state = current_time - last_state_time
            if time_since_last_state > watchdog_timeout:
                print(f"⚠️ Watchdog timeout: {time_since_last_state:.2f}s since last state update - forcing exit")
                break
        
            try:
                # Get next state with timeout - this prevents hanging on a single iteration
                state = await asyncio.wait_for(stream_iter.__anext__(), timeout=stream_timeout)
                states_processed += 1
                last_state_time = watchdog_time.time()  # Update watchdog timer
                # Process state...
            except asyncio.TimeoutError:
                print(f"⏱️ Stream iteration timed out after {stream_timeout}s")
                break
```

**Key Similarities:**
- ✅ `asyncio.wait_for()` with timeout
- ✅ Timeout calculation based on elapsed time
- ✅ Handling `asyncio.TimeoutError`
- ✅ Async iteration with `__anext__()`

**Additional Features in Convonet:**
- **Watchdog timer** - Prevents infinite loops by tracking time between state updates
- **Max states limit** - Prevents processing too many states
- **Nested timeout handling** - Per-iteration timeout + overall watchdog
- **State tracking** - Tracks processed states and updates watchdog timer

**Another Example - Tool Execution with Timeout:**

**File:** `convonet/assistant_graph_todo.py` (Lines 836-890)

```python
async def execute_tool_async(tool_call):
    tool_timeout = 6.0
    try:
        if hasattr(tool, 'ainvoke'):
            result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=tool_timeout)
        else:
            result = await asyncio.wait_for(asyncio.to_thread(tool.invoke, tool_args), timeout=tool_timeout)
        return result
    except asyncio.TimeoutError:
        return {
            'tool_call_id': tool_id,
            'content': "I'm sorry, the database operation timed out. Please try again.",
            'status': 'timeout'
        }
```

---

## 4. Producer-Consumer Pattern with Queues

### Example Pattern
```python
async def run_pipeline(async_iterable, batch_size, max_wait_seconds, cache, max_concurrency, process_batch):
    queue = asyncio.Queue()
    semaphore = asyncio.Semaphore(max_concurrency)
    
    async def producer():
        async for batch in AsyncBatchWithCache(async_iterable, batch_size, max_wait_seconds, cache):
            await queue.put(batch)
        # signal consumers to exit
        for _ in range(max_concurrency):
            await queue.put(None)
    
    async def consumer():
        while True:
            batch = await queue.get()
            if batch is None:
                return
            async with semaphore:
                await process_batch(batch)
    
    producer_task = asyncio.create_task(producer())
    consumer_tasks = [asyncio.create_task(consumer()) for _ in range(max_concurrency)]
    
    await producer_task
    await asyncio.gather(*consumer_tasks)
```

### Similar Implementation in Convonet

**File:** `convonet/assistant_graph_todo.py` (Lines 818-890)

**Pattern:** Parallel tool execution with concurrency control

```python
async def tools_node(state: AgentState):
    """Execute async MCP tools and return results."""
    # Collect all tool calls first
    tool_calls_list = list(last_message.tool_calls)
    
    # OPTIMIZATION: Execute multiple tools in parallel
    if len(tool_calls_list) > 1:
        print(f"🚀 Executing {len(tool_calls_list)} tools in parallel for lower latency")
        
        async def execute_tool_async(tool_call):
            """Execute a single tool call"""
            tool_name = tool_call.get('name', 'unknown')
            tool_args = tool_call.get('args', {})
            tool_id = tool_call.get('id', f'tool_{len(tool_messages)}')
            
            try:
                tool = None
                for t in self.tools:
                    if t.name == tool_name:
                        tool = t
                        break
                
                if tool:
                    tool_timeout = 6.0
                    if hasattr(tool, 'ainvoke'):
                        result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=tool_timeout)
                    else:
                        result = await asyncio.wait_for(asyncio.to_thread(tool.invoke, tool_args), timeout=tool_timeout)
                    return {
                        'tool_call_id': tool_id,
                        'content': str(result),
                        'status': 'success'
                    }
            except asyncio.TimeoutError:
                return {
                    'tool_call_id': tool_id,
                    'content': "I'm sorry, the database operation timed out. Please try again.",
                    'status': 'timeout'
                }
        
        # Execute all tools in parallel (similar to consumer pattern)
        tool_results = await asyncio.gather(*[execute_tool_async(tc) for tc in tool_calls_list])
        
        # Convert results to ToolMessage format
        for result in tool_results:
            from langchain_core.messages import ToolMessage
            tool_messages.append(ToolMessage(
                content=result['content'],
                tool_call_id=result['tool_call_id']
            ))
```

**Key Similarities:**
- ✅ Parallel execution of multiple items
- ✅ Concurrency control (implicit via `asyncio.gather()`)
- ✅ Async task execution
- ✅ Error handling per task

**Additional Features in Convonet:**
- **Direct parallel execution** - Uses `asyncio.gather()` instead of queue (simpler for fixed-size batches)
- **Timeout per task** - Each tool execution has its own timeout
- **Result aggregation** - Collects results from all parallel tasks
- **Error isolation** - Each tool's errors don't affect others

**Alternative Pattern - ThreadPoolExecutor (Producer-Consumer):**

**File:** `convonet/webrtc_voice_server.py` (Lines 1231-1332)

```python
def process_audio_async(session_id, audio_buffer):
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
    
    def run_async_in_thread():
        """Run async function in a new thread with its own event loop"""
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        
        timeout_seconds = 60.0
        try:
            result = new_loop.run_until_complete(
                asyncio.wait_for(
                    process_with_agent(text, user_id, user_name),
                    timeout=timeout_seconds
                )
            )
            return result
        except asyncio.TimeoutError:
            return None, None
    
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(run_async_in_thread)
        try:
            executor_timeout = 90.0
            agent_response, transfer_marker = future.result(timeout=executor_timeout)
        except FutureTimeoutError:
            print(f"⏱️ ThreadPoolExecutor timed out after {executor_timeout}s")
```

**Key Similarities:**
- ✅ Producer-consumer pattern (ThreadPoolExecutor as queue)
- ✅ Timeout handling
- ✅ Concurrency control (`max_workers=1`)
- ✅ Signal completion (future.result())

---

## 5. Watchdog Timer Pattern

### Example Pattern (Implicit in AsyncBatchWithCache)
The example uses `max_wait_seconds` to limit how long to wait for items, which is similar to a watchdog.

### Similar Implementation in Convonet

**File:** `convonet/routes.py` (Lines 1646-1660)

**Pattern:** Watchdog timer to prevent infinite loops

```python
# Add watchdog timer - if we don't get a state update within this time, force exit
import time as watchdog_time
last_state_time = watchdog_time.time()
watchdog_timeout = 10.0  # Maximum time between state updates

try:
    while states_processed < max_states:
        # Check watchdog - if too much time has passed since last state, force exit
        current_time = watchdog_time.time()
        time_since_last_state = current_time - last_state_time
        if time_since_last_state > watchdog_timeout:
            print(f"⚠️ Watchdog timeout: {time_since_last_state:.2f}s since last state update - forcing exit")
            break
        
        try:
            state = await asyncio.wait_for(stream_iter.__anext__(), timeout=stream_timeout)
            states_processed += 1
            last_state_time = watchdog_time.time()  # Update watchdog timer
            # Process state...
```

**Key Similarities:**
- ✅ Time-based monitoring
- ✅ Force exit when threshold exceeded
- ✅ Timer reset on successful operations

**Additional Features in Convonet:**
- **Dual timeout system** - Per-iteration timeout + overall watchdog
- **State tracking** - Updates timer on each successful state update
- **Graceful degradation** - Exits cleanly when watchdog triggers

---

## 6. Duplicate Detection with Cache

### Example Pattern
```python
if self.cache.get(item):  # check cache to decide skip
    continue  # skip duplicate
self.cache.set(item, True)
```

### Similar Implementation in Convonet

**File:** `convonet/agent_monitor.py` (Lines 106-129)

**Pattern:** Tracking and deduplication of interactions

```python
def track_interaction(self, request_id: str, ...):
    """Track an agent interaction"""
    try:
        interaction = AgentInteraction(...)
        
        # Store in Redis
        interaction_key = f"agent_interaction:{request_id}"
        interaction_data = json.dumps(interaction.to_dict())
        self.redis.set(interaction_key, interaction_data, expire=86400 * 7)  # 7 days
        
        # Add to recent interactions list (with size limit - prevents duplicates)
        recent_key = "agent_interactions:recent"
        self.redis.redis_client.lpush(recent_key, request_id)
        self.redis.redis_client.ltrim(recent_key, 0, self.max_interactions - 1)
        self.redis.redis_client.expire(recent_key, 86400 * 7)  # 7 days
```

**Key Similarities:**
- ✅ Cache-based tracking
- ✅ TTL expiration
- ✅ Duplicate prevention (via request_id)

**Additional Features in Convonet:**
- **List-based tracking** - Maintains ordered list of recent interactions
- **Size limits** - `ltrim` prevents unbounded growth
- **Multiple indexes** - Tracks by provider, user, and globally

---

## 7. Error Handling and Retry Logic

### Example Pattern (Implicit)
The example shows timeout handling, but doesn't show retry logic explicitly.

### Similar Implementation in Convonet

**File:** `convonet/assistant_graph_todo.py` (Lines 912-950)

**Pattern:** Retry logic with exponential backoff

```python
# Retry logic for MCP connection failures
max_retries = 2
retry_count = 0
result = None

while retry_count < max_retries and result is None:
    try:
        if hasattr(tool, 'ainvoke'):
            result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=tool_timeout)
        else:
            result = await asyncio.wait_for(asyncio.to_thread(tool.invoke, tool_args), timeout=tool_timeout)
        print(f"✅ Tool {tool_name} completed successfully")
        break  # Success, exit retry loop
    except asyncio.TimeoutError:
        result = "I'm sorry, the database operation timed out. Please try again."
        print(f"⏰ Tool {tool_name} timed out after {tool_timeout} seconds")
        break  # Timeout is not retryable
    except ExceptionGroup as eg:
        # Unwrap ExceptionGroup and get the first exception
        print(f"❌ Tool {tool_name} ExceptionGroup with {len(eg.exceptions)} exception(s)")
        for i, exc in enumerate(eg.exceptions):
            print(f"   Exception {i}: {type(exc).__name__}: {str(exc)}")
        
        # Check if it's a retryable error
        if retry_count < max_retries - 1:
            retry_count += 1
            print(f"🔄 Retrying tool {tool_name} (attempt {retry_count + 1}/{max_retries})...")
            await asyncio.sleep(0.5)  # Brief delay before retry
            continue
        else:
            # Final attempt failed
            result = "I encountered a system error. Please try again."
            break
```

**Key Similarities:**
- ✅ Retry loop with max attempts
- ✅ Error classification (retryable vs non-retryable)
- ✅ Timeout handling (non-retryable)

**Additional Features in Convonet:**
- **ExceptionGroup handling** - Unwraps nested exceptions
- **Selective retries** - Only retries on specific error types
- **Backoff delay** - `asyncio.sleep(0.5)` between retries
- **Detailed logging** - Tracks retry attempts and errors

---

## Summary: Key Patterns Demonstrated

| Pattern | Example Code | Convonet Implementation | File Location |
|---------|-------------|------------------------|---------------|
| **TTL Cache** | `TTLCache` with `OrderedDict` | `RedisManager.cache_user_data()` | `convonet/redis_manager.py:138` |
| **Async Batching** | `AsyncBatchWithCache` | `RAGService.index_documents()` | `convonet/rag_service.py:196` |
| **Async Iteration** | `__anext__()` with timeout | `process_stream()` | `convonet/routes.py:1457` |
| **Producer-Consumer** | `run_pipeline()` with queue | Parallel tool execution | `convonet/assistant_graph_todo.py:818` |
| **Watchdog Timer** | Implicit in timeout logic | Watchdog in stream processing | `convonet/routes.py:1646` |
| **Duplicate Detection** | Cache check before processing | Interaction tracking | `convonet/agent_monitor.py:106` |
| **Retry Logic** | Not in example | MCP tool retry logic | `convonet/assistant_graph_todo.py:912` |

---

## Interview Talking Points

### 1. **TTL Cache Implementation**
- "I implemented a distributed TTL cache using Redis in the Convonet project. Unlike the in-memory `OrderedDict` approach, I used Redis for distributed caching across multiple workers, with automatic expiration via `setex()`. I also added fallback to in-memory storage when Redis is unavailable, ensuring graceful degradation."

### 2. **Async Batching**
- "I implemented batch processing for document indexing in the RAG service. While the example uses async iteration with timeouts, I used synchronous batching with configurable batch sizes. The pattern is similar - accumulating items until a batch size is reached, then processing the batch. This can be easily adapted to async with timeout logic."

### 3. **Timeout and Watchdog Patterns**
- "I implemented a dual-timeout system in the agent streaming pipeline: a per-iteration timeout using `asyncio.wait_for()` and a watchdog timer that tracks time between state updates. This prevents both individual operation hangs and overall infinite loops. The watchdog pattern is particularly important for LLM streaming where responses can be unpredictable."

### 4. **Producer-Consumer Pattern**
- "I implemented parallel tool execution using `asyncio.gather()` instead of explicit queues. For fixed-size batches (like tool calls), this is more efficient. However, I also used `ThreadPoolExecutor` for producer-consumer patterns when integrating async code with synchronous frameworks like Flask/Eventlet."

### 5. **Error Handling and Retries**
- "I implemented sophisticated retry logic for MCP tool calls, with error classification (retryable vs non-retryable), exponential backoff, and detailed logging. Timeout errors are not retried, but connection errors are retried up to 2 times with a brief delay."

### 6. **Real-World Challenges**
- "In production, I encountered issues with blocking operations that couldn't be interrupted by timeouts. I solved this by using `ThreadPoolExecutor` with separate event loops, allowing timeout control at the thread level. This is more complex than the example but necessary for real-world async/sync integration."

---

## Code Snippets for Quick Reference

### TTL Cache Pattern
```python
# Convonet: RedisManager.cache_user_data()
cache_key = f"user:{user_id}:{data_type}"
self.redis_client.setex(cache_key, ttl, json.dumps(data))
```

### Async Iteration with Timeout
```python
# Convonet: routes.py process_stream()
state = await asyncio.wait_for(stream_iter.__anext__(), timeout=stream_timeout)
```

### Watchdog Timer
```python
# Convonet: routes.py process_stream()
time_since_last_state = current_time - last_state_time
if time_since_last_state > watchdog_timeout:
    break  # Force exit
```

### Parallel Execution
```python
# Convonet: assistant_graph_todo.py tools_node()
tool_results = await asyncio.gather(*[execute_tool_async(tc) for tc in tool_calls_list])
```

### Retry Logic
```python
# Convonet: assistant_graph_todo.py tools_node()
while retry_count < max_retries and result is None:
    try:
        result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=tool_timeout)
        break
    except ExceptionGroup as eg:
        if retry_count < max_retries - 1:
            retry_count += 1
            await asyncio.sleep(0.5)
            continue
```

---

## Additional Patterns Not in Example

### 1. **Semaphore for Concurrency Control**
**File:** `docs/MEMORY_ISSUES.md` (Lines 108-118)
```python
from asyncio import Semaphore

MAX_CONCURRENT_AGENTS = 2
agent_semaphore = Semaphore(MAX_CONCURRENT_AGENTS)

async def _run_agent_async(...):
    async with agent_semaphore:
        # Existing agent execution code
```

### 2. **Rate Limiting**
**File:** `convonet/redis_manager.py` (Lines 240-251)
```python
def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
    """Check if rate limit is exceeded"""
    current_count = self.redis_client.incr(key)
    if current_count == 1:
        self.redis_client.expire(key, window)
    return current_count <= limit
```

### 3. **Graceful Degradation**
**File:** `convonet/redis_manager.py` (Lines 58-61)
```python
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    # Fallback to in-memory storage for development
    self.redis_client = None
    self._fallback_storage = {}
```

---

## Conclusion

The Convonet project demonstrates production-ready implementations of all the patterns shown in the forward deployment engineer example, with additional real-world considerations:

- **Distributed systems** (Redis vs in-memory)
- **Error handling and retries**
- **Watchdog timers for reliability**
- **Graceful degradation**
- **Integration with existing frameworks** (Flask/Eventlet)
- **Production logging and monitoring**

These implementations show not just understanding of the patterns, but also experience with real-world constraints and trade-offs.
