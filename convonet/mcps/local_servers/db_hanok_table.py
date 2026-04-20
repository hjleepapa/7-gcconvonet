"""
MCP stdio entry for Hanok Table (kfood) reservation tools.

Requires HANOK_MCP_API_BASE_URL (or HANOK_PUBLIC_BASE_URL) on **agent-llm-service** pointing at the
deployed Hanok FastAPI base URL (e.g. https://hanok.convonetai.com) that serves /api/reservations.
The Hanok app is deployed from its **own repository / CI**, not from 7-gcconvonet. This stdio
entry still needs the ``hanok_table`` Python package importable in the agent-llm environment.
"""
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_KFOOD = os.path.join(_ROOT, "kfood")
if _KFOOD not in sys.path:
    sys.path.insert(0, _KFOOD)

os.chdir(_ROOT)
os.environ.setdefault("HANOK_MCP_TRANSPORT", "stdio")


if __name__ == "__main__":
    from hanok_table.mcp_server.server import main

    main()
