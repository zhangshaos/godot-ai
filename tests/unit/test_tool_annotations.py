"""Contract tests for MCP tool annotations exposed by the Godot AI catalog."""

from __future__ import annotations

import asyncio

from godot_ai.server import create_server

_ADDITIVE_TOOLS = {"node_create"}

_READ_ONLY_TOOLS = {
    "api_manage",
    "editor_state",
    "logs_read",
    "node_find",
    "node_get_properties",
    "scene_get_hierarchy",
    "session_manage",
    "test_manage",
    "tileset_manage",
}


def test_every_tool_exposes_conservative_mcp_annotations():
    tools = asyncio.run(create_server().list_tools())

    for tool in tools:
        annotations = tool.annotations
        assert annotations is not None, f"{tool.name} is missing MCP annotations"
        assert annotations.openWorldHint is False, tool.name

        if tool.name in _READ_ONLY_TOOLS:
            assert annotations.readOnlyHint is True, tool.name
            assert annotations.destructiveHint is False, tool.name
            assert annotations.idempotentHint is True, tool.name
        elif tool.name in _ADDITIVE_TOOLS:
            assert annotations.readOnlyHint is False, tool.name
            assert annotations.destructiveHint is False, tool.name
            assert annotations.idempotentHint is False, tool.name
        else:
            assert annotations.readOnlyHint is False, tool.name
            assert annotations.destructiveHint is True, tool.name
            assert annotations.idempotentHint is False, tool.name


def test_expected_read_only_tools_are_registered():
    names = {tool.name for tool in asyncio.run(create_server().list_tools())}
    assert _READ_ONLY_TOOLS <= names
