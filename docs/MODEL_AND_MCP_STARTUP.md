# Model and MCP Server Startup Behavior

## Overview

This document explains when and how `mortgage_models.py` and `db_mortgage.py` are executed/loaded when the service starts.

## 1. `mortgage_models.py` (SQLAlchemy Models)

### Current Status: **Lazy Imported** (Not automatically loaded at startup)

**Location:** `convonet/models/mortgage_models.py`

**How it's imported:**
- Listed in `convonet/models/__init__.py` (lines 5-13)
- But `convonet/models/__init__.py` is only imported when something explicitly imports from `convonet.models`
- Currently imported lazily in:
  - `convonet/routes.py` (lines 789, 860) - only when mortgage routes are accessed
  - `convonet/mcps/local_servers/db_mortgage.py` (line 52) - only when MCP tools are called

**For Flask-Migrate:**
- Flask-Migrate needs models to be imported at startup to detect schema changes
- Currently, mortgage models are **NOT** automatically imported at startup
- This means `flask db migrate` might not detect mortgage model changes unless models are imported first

**Recommendation:**
To ensure models are loaded at startup for Flask-Migrate, add this to `app.py` in `create_app()`:

```python
# Import all models at startup for Flask-Migrate autogenerate
try:
    from convonet.models import (
        User, Team, TeamMembership,
        MortgageApplication, MortgageDocument, MortgageDebt, MortgageApplicationNote
    )
    print("✅ All models imported for Flask-Migrate")
except ImportError as e:
    print(f"⚠️  Could not import models: {e}")
```

## 2. `db_mortgage.py` (MCP Server)

### Current Status: **Started on-demand** (Not executed at startup)

**Location:** `convonet/mcps/local_servers/db_mortgage.py`

**How it's started:**
1. Listed in `convonet/mcps/mcp_config.json` (lines 14-24)
2. Started as a **separate Python subprocess** when MCP tools are requested
3. Pre-loaded at startup via `preload_mcp_tools_sync()` in `app.py` (line 149)
   - This starts the MCP server process to cache tools
   - But the actual Python file execution happens in the subprocess, not in the main Flask app

**Startup Flow:**
```
app.py (create_app)
  → preload_mcp_tools_sync()
    → _preload_mcp_tools()
      → MultiServerMCPClient(connections=mcp_config)
        → Starts subprocess: python convonet/mcps/local_servers/db_mortgage.py
          → db_mortgage.py executes (separate process)
            → Lazy imports mortgage_models.py when tools are called
```

**Key Points:**
- `db_mortgage.py` runs in a **separate process**, not in the main Flask app
- It uses **lazy imports** for models (line 46: `_lazy_import_mortgage_models()`)
- The MCP server process stays alive to handle tool requests
- Tools are cached after first load for performance

## Summary

| File | Executed at Startup? | How |
|------|---------------------|-----|
| `mortgage_models.py` | ❌ **No** | Lazy imported when needed |
| `db_mortgage.py` | ⚠️ **Partially** | Started as subprocess during MCP pre-load, but models are lazy imported |

## Recommendations

### For Models (`mortgage_models.py`):
**Add explicit model import in `app.py`** to ensure Flask-Migrate can detect schema changes:

```python
# In app.py, create_app() function, after db.init_app(app)
try:
    from convonet.models import (
        User, Team, TeamMembership,
        MortgageApplication, MortgageDocument, MortgageDebt, MortgageApplicationNote
    )
    print("✅ All models imported for Flask-Migrate")
except ImportError as e:
    print(f"⚠️  Could not import models: {e}")
```

### For MCP Server (`db_mortgage.py`):
**Current behavior is correct** - it's started on-demand and models are lazy imported when tools are called. No changes needed.

## Testing

To verify models are loaded:
```python
# In Python shell or test script
from app import create_app
app = create_app()
from convonet.models import MortgageApplication
print(MortgageApplication.__table__)  # Should print table definition
```

To verify MCP server is running:
- Check startup logs for: `✅ MCP tools pre-loaded and cached: X tools`
- Check that mortgage tools are in the list: `create_mortgage_application`, `get_mortgage_application_status`, etc.
