"""MCP server package loads (heavy deps: mcp, httpx)."""

from __future__ import annotations


def test_mcp_server_module_imports() -> None:
    from hanok_table.mcp_server.server import mcp

    assert mcp.name == "hanok-table-reservations"
