# Tool Execution GUI Guide

## 🎯 Overview

The Tool Execution GUI is a beautiful web-based dashboard for monitoring and troubleshooting tool call executions in real-time. It provides visual insights into tool execution status, performance, and errors.

---

## 🚀 Quick Start

### 1. Access the Dashboard

Once your Flask app is running, navigate to:

```
http://localhost:10000/anthropic/tool-execution/
```

Or in production:

```
https://hjlees.com/anthropic/tool-execution/
```

### 2. View Tool Executions

The dashboard automatically displays:
- **Overall Statistics**: Success rate, failed tools, timeouts
- **Visual Charts**: Tool execution distribution
- **Recent Requests**: List of all agent requests with tool executions
- **Detailed Views**: Click any request to see detailed tool execution information

---

## 📊 Dashboard Features

### Statistics Cards

The top of the dashboard shows:
- ✅ **Successful Tools**: Total number of successfully executed tools
- ❌ **Failed Tools**: Total number of failed tool executions
- ⏱️ **Timeout Tools**: Total number of timed-out tools
- 📊 **Success Rate**: Percentage of successful tool executions

### Visual Chart

A doughnut chart shows the distribution of:
- Successful (green)
- Failed (red)
- Timeout (yellow)

### Recent Requests List

Shows all recent agent requests with:
- Request ID
- Overall status (All Success / Some Failed)
- Tool execution counts
- Total duration

### Detailed Tool View

Click any request to see:
- **Tool Name** and **Status**
- **Execution Duration**
- **Arguments** passed to the tool
- **Results** returned (if successful)
- **Error Details** with stack traces (if failed)

---

## 🔧 Integration

### The GUI automatically works with:

1. **Tool Execution Tracker** - Tracks tool executions in `assistant_graph_todo.py`
2. **Tool Execution Viewer** - Provides the data structure
3. **Structured Logger** - Logs tool execution events

### To enable tracking in your agent:

```python
from convonet.tool_execution_viewer import create_tracker, ToolExecutionViewer
from convonet.logger import get_logger

logger = get_logger(__name__, component="tool")

# In your agent processing function
tracker = create_tracker(user_id=user_id)

# In tools_node, track each tool execution
execution = tracker.start_tool(tool_name, tool_id, arguments)
try:
    result = await execute_tool()
    tracker.complete_tool(tool_id, result)
except Exception as e:
    tracker.fail_tool(tool_id, str(e), type(e).__name__, traceback.format_exc())

# At the end
tracker.finish()
```

---

## 📡 API Endpoints

The GUI uses these API endpoints (you can also use them programmatically):

### Get All Trackers
```
GET /anthropic/tool-execution/api/trackers
```

Returns list of all trackers with summaries.

### Get Tracker Details
```
GET /anthropic/tool-execution/api/tracker/<request_id>
```

Returns detailed information about a specific tracker including all tool executions.

### Get Overall Statistics
```
GET /anthropic/tool-execution/api/stats
```

Returns aggregated statistics across all trackers.

---

## 🎨 Features

### Real-Time Updates
- Dashboard auto-refreshes every 5 seconds
- Click "🔄 Refresh" button for manual refresh
- Statistics update automatically

### Interactive Views
- Click any request to see detailed tool executions
- Expand/collapse error stack traces
- View formatted JSON for arguments and results

### Visual Indicators
- Color-coded status badges
- Icons for quick visual scanning
- Performance indicators (duration in milliseconds)

### Error Details
- Full error messages
- Error types
- Complete stack traces (expandable)
- Arguments that caused the error

---

## 🔍 Troubleshooting

### No Trackers Showing

If you don't see any trackers:
1. Make sure tool execution tracking is enabled in your agent
2. Execute a request that triggers tool calls
3. Check browser console for errors
4. Verify the blueprint is registered (check Flask logs)

### Dashboard Not Loading

1. Check Flask logs for blueprint registration
2. Verify the route: `/anthropic/tool-execution/`
3. Check browser console for JavaScript errors
4. Ensure Chart.js CDN is accessible

### Data Not Updating

1. Check if trackers are being created in your code
2. Verify the `_trackers` dictionary is being populated
3. Check browser network tab for API calls
4. Verify auto-refresh is working (check browser console)

---

## 📝 Example: Complete Integration

```python
# In assistant_graph_todo.py
from convonet.tool_execution_viewer import create_tracker, ToolExecutionViewer
from convonet.logger import get_logger

logger = get_logger(__name__, component="tool")

# Store tracker in state or context
# (You'll need to pass it through your agent processing)

async def tools_node(state: AgentState):
    """Execute async MCP tools and return results."""
    # Get tracker from state or create new one
    tracker = getattr(state, '_tracker', None)
    if not tracker:
        tracker = create_tracker(user_id=state.authenticated_user_id)
        state._tracker = tracker
    
    # ... existing tool execution code ...
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.get('name', 'unknown')
        tool_id = tool_call.get('id', f'tool_{len(tool_messages)}')
        tool_args = tool_call.get('args', {})
        
        # Start tracking
        execution = tracker.start_tool(tool_name, tool_id, tool_args)
        
        try:
            # Execute tool
            result = await execute_tool(tool_name, tool_args)
            tracker.complete_tool(tool_id, result)
        except Exception as e:
            import traceback
            tracker.fail_tool(tool_id, str(e), type(e).__name__, traceback.format_exc())
    
    # Finish tracking
    tracker.finish()
    
    # Display in console (optional)
    ToolExecutionViewer.display_summary(tracker)
    
    return state
```

---

## 🎯 Use Cases

### 1. **Production Monitoring**
- Monitor tool execution success rates
- Identify failing tools quickly
- Track performance over time

### 2. **Debugging**
- See exactly which tools failed
- View error details and stack traces
- Check arguments that caused failures

### 3. **Performance Analysis**
- Identify slow tools
- Compare execution times
- Optimize tool performance

### 4. **Development**
- Validate tool integrations
- Test tool execution flows
- Verify error handling

---

## 🚀 Next Stepsou

1. **Integrate tracking** in your `tools_node` function
2. **Access the dashboard** at `/anthropic/tool-execution/`
3. **Monitor tool executions** in real-time
4. **Debug issues** using the detailed views

---

**Now you have a beautiful GUI to monitor tool executions! 🎉**

