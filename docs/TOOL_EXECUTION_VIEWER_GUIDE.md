# Tool Execution Viewer Guide

## 🎯 Overview

The Tool Execution Viewer is a specialized logging system that tracks and displays tool call execution status in a beautiful, easy-to-read format. It's the **most important checkpoint** for troubleshooting agent behavior.

---

## 🚀 Quick Start

### 1. Import the Viewer

```python
from convonet.tool_execution_viewer import (
    create_tracker,
    ToolExecutionViewer,
    ToolStatus
)
from convonet.logger import get_logger

logger = get_logger(__name__, component="tool")
```

### 2. Create a Tracker for Each Request

```python
# At the start of agent processing
tracker = create_tracker(request_id="req_123", user_id="user_456")
```

### 3. Track Tool Executions

```python
# When a tool is about to execute
execution = tracker.start_tool(
    tool_name="create_todo",
    tool_id="tool_call_abc123",
    arguments={"title": "Buy groceries", "priority": "high"}
)

try:
    # Execute the tool
    result = await execute_tool(arguments)
    
    # Mark as successful
    tracker.complete_tool("tool_call_abc123", result=result)
    execution.complete(result)
    
except Exception as e:
    # Mark as failed
    import traceback
    tracker.fail_tool(
        "tool_call_abc123",
        error=str(e),
        error_type=type(e).__name__,
        stack_trace=traceback.format_exc()
    )
    execution.fail(str(e), type(e).__name__, traceback.format_exc())
```

### 4. Display the Summary

```python
# At the end of agent processing
tracker.finish()
ToolExecutionViewer.display_summary(tracker)
```

---

## 📊 Example Output

### Console Display

```
================================================================================
TOOL EXECUTION SUMMARY
================================================================================

✅ ALL TOOLS EXECUTED SUCCESSFULLY

Request ID: req_123
User ID: user_456
Total Tools: 2
✅ Successful: 2
❌ Failed: 0
⏱️  Timeout: 0

Total Duration: 1245.67ms

Tool Execution Details:

================================================================================
✅ Tool #1: create_todo
================================================================================
Status: SUCCESS
Tool ID: tool_call_abc123
Duration: 245.23ms

Arguments:
{
  "title": "Buy groceries",
  "priority": "high",
  "due_date": "2025-01-20"
}

Result:
Todo created successfully with ID: todo_789

================================================================================
✅ Tool #2: get_todos
================================================================================
Status: SUCCESS
Tool ID: tool_call_def456
Duration: 156.44ms

Arguments:
{
  "completed": false
}

Result:
Found 5 todos: [todo_1, todo_2, ...]

================================================================================
```

### Failed Tool Example

```
================================================================================
❌ Tool #1: create_todo
================================================================================
Status: FAILED
Tool ID: tool_call_abc123
Duration: 1234.56ms

Arguments:
{
  "title": "Buy groceries",
  "priority": "high"
}

Error:
Type: ValidationError
Database constraint violation: title cannot be empty

Stack Trace:
  File "tool.py", line 45, in create_todo
    validate_title(title)
  File "validator.py", line 12, in validate_title
    raise ValidationError("title cannot be empty")
```

---

## 🔧 Integration with Agent Graph

### Update `assistant_graph_todo.py`

Add tracking to the `tools_node` function:

```python
from convonet.tool_execution_viewer import create_tracker, ToolExecutionViewer
from convonet.logger import get_logger

logger = get_logger(__name__, component="tool")

# In your agent processing function, create tracker
tracker = create_tracker(user_id=user_id)

async def tools_node(state: AgentState):
    """Execute async MCP tools and return results."""
    try:
        # Get the last message which should contain tool calls
        last_message = state.messages[-1]
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return state
        
        tool_messages = []
        tool_call_ids = set()
        
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get('name', 'unknown')
            tool_args = tool_call.get('args', {})
            tool_id = tool_call.get('id', f'tool_{len(tool_messages)}')
            tool_call_ids.add(tool_id)
            
            # Start tracking
            execution = tracker.start_tool(tool_name, tool_id, tool_args)
            logger.tool_execution(
                tool_name=tool_name,
                tool_id=tool_id,
                status="executing",
                arguments=tool_args
            )
            
            try:
                # Find and execute tool
                tool = None
                for t in self.tools:
                    if t.name == tool_name:
                        tool = t
                        break
                
                if tool:
                    import time
                    start_time = time.time()
                    
                    try:
                        if hasattr(tool, 'ainvoke'):
                            result = await asyncio.wait_for(tool.ainvoke(tool_args), timeout=8.0)
                        else:
                            result = await asyncio.wait_for(
                                asyncio.to_thread(tool.invoke, tool_args), 
                                timeout=8.0
                            )
                        
                        duration = time.time() - start_time
                        
                        # Mark as successful
                        tracker.complete_tool(tool_id, result)
                        execution.complete(result)
                        logger.tool_execution(
                            tool_name=tool_name,
                            tool_id=tool_id,
                            status="success",
                            duration_ms=duration * 1000,
                            result=result
                        )
                        
                    except asyncio.TimeoutError:
                        duration = time.time() - start_time
                        tracker.timeout_tool(tool_id)
                        execution.timeout()
                        logger.tool_execution(
                            tool_name=tool_name,
                            tool_id=tool_id,
                            status="timeout",
                            duration_ms=duration * 1000,
                            error="Tool execution timed out after 8 seconds"
                        )
                        result = "I'm sorry, the database operation timed out. Please try again."
                        
                    except Exception as tool_error:
                        duration = time.time() - start_time
                        import traceback
                        error_str = str(tool_error)
                        error_type = type(tool_error).__name__
                        stack = traceback.format_exc()
                        
                        tracker.fail_tool(tool_id, error_str, error_type, stack)
                        execution.fail(error_str, error_type, stack)
                        logger.tool_execution(
                            tool_name=tool_name,
                            tool_id=tool_id,
                            status="failed",
                            duration_ms=duration * 1000,
                            error=error_str,
                            arguments=tool_args
                        )
                        
                        # Handle error and create result message
                        result = handle_tool_error(tool_error)
                    
                    # Create tool message
                    from langchain_core.messages import ToolMessage
                    tool_message = ToolMessage(
                        content=str(result),
                        name=tool_name,
                        tool_call_id=tool_id
                    )
                    tool_messages.append(tool_message)
                    
            except Exception as e:
                import traceback
                tracker.fail_tool(tool_id, str(e), type(e).__name__, traceback.format_exc())
                logger.tool_execution(
                    tool_name=tool_name,
                    tool_id=tool_id,
                    status="failed",
                    error=str(e)
                )
                # Create error message
                tool_message = ToolMessage(
                    content=f"Error: {str(e)}",
                    name=tool_name,
                    tool_call_id=tool_id
                )
                tool_messages.append(tool_message)
        
        # Add tool messages to state
        state.messages.extend(tool_messages)
        
        # Display summary
        tracker.finish()
        ToolExecutionViewer.display_summary(tracker)
        
        return state
        
    except Exception as e:
        logger.error("Critical error in tools_node", context={"error": str(e)}, exc_info=True)
        raise
```

---

## 📈 Features

### 1. **Automatic Status Tracking**
- Tracks: PENDING → EXECUTING → SUCCESS/FAILED/TIMEOUT
- Records timing for each tool
- Captures arguments and results

### 2. **Beautiful Console Output**
- Color-coded by status (green=success, red=failed, yellow=timeout)
- Icons for quick visual scanning
- Formatted JSON for arguments/results
- Stack traces for errors

### 3. **Sentry Integration**
- Automatically sends summary to Sentry
- Includes all context (arguments, results, errors)
- Tags requests for easy filtering

### 4. **Performance Metrics**
- Duration for each tool
- Total request duration
- Color-coded by performance (green < 1s, yellow < 3s, red > 3s)

### 5. **Error Details**
- Error type and message
- Full stack traces
- Arguments that caused the error

---

## 🔍 Troubleshooting with Tool Viewer

### Check if Tools Executed

```python
# After agent processing
tracker.finish()
summary = tracker.get_summary()

if summary['all_successful']:
    print("✅ All tools executed successfully")
else:
    print(f"❌ {summary['failed']} tools failed, {summary['timeout']} timed out")
    # Display full details
    ToolExecutionViewer.display_summary(tracker)
```

### Find Slow Tools

```python
# Check which tools took too long
for tool_id, execution in tracker.tools.items():
    if execution.duration_ms and execution.duration_ms > 1000:
        print(f"⚠️ {execution.tool_name} took {execution.duration_ms:.2f}ms")
```

### Debug Failed Tools

```python
# Get details of failed tools
failed_tools = [t for t in tracker.tools.values() if t.status == ToolStatus.FAILED]

for tool in failed_tools:
    print(f"Tool: {tool.tool_name}")
    print(f"Error: {tool.error}")
    print(f"Arguments: {tool.arguments}")
    if tool.stack_trace:
        print(f"Stack: {tool.stack_trace}")
```

---

## 🎯 Best Practices

1. **Always create a tracker** at the start of agent processing
2. **Track every tool call** - don't skip any
3. **Display summary** at the end of processing
4. **Use in production** - it helps debug issues quickly
5. **Check Sentry** for tool execution failures

---

## 📝 Example: Complete Integration

```python
from convonet.tool_execution_viewer import create_tracker, ToolExecutionViewer
from convonet.logger import get_logger

logger = get_logger(__name__, component="agent")

async def process_with_agent(text: str, user_id: str):
    # Create tracker
    tracker = create_tracker(user_id=user_id)
    
    try:
        # Process with agent (this will call tools_node which tracks tools)
        result = await agent.process(text)
        
        # Finish tracking
        tracker.finish()
        
        # Display summary
        ToolExecutionViewer.display_summary(tracker)
        
        return result
        
    except Exception as e:
        tracker.finish()
        ToolExecutionViewer.display_summary(tracker)
        logger.error("Agent processing failed", exc_info=True)
        raise
```

---

## 🚀 Quick Reference

### Status Values
- `PENDING` - Tool call received but not started
- `EXECUTING` - Tool is currently running
- `SUCCESS` - Tool completed successfully
- `FAILED` - Tool execution failed
- `TIMEOUT` - Tool execution timed out
- `SKIPPED` - Tool was skipped

### Key Methods
- `tracker.start_tool(name, id, args)` - Start tracking
- `tracker.complete_tool(id, result)` - Mark successful
- `tracker.fail_tool(id, error, type, trace)` - Mark failed
- `tracker.timeout_tool(id)` - Mark timeout
- `tracker.finish()` - Complete tracking
- `ToolExecutionViewer.display_summary(tracker)` - Show summary

---

**Now you can easily validate that tool calls executed properly! 🎉**

