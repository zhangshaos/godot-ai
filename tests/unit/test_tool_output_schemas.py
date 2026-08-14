"""Contract tests for informative MCP output schemas on host-mirrored tools."""

from __future__ import annotations

import asyncio

from godot_ai.server import create_server

_HOST_MIRRORED_TOOLS = {
    "session_manage",
    "editor_state",
    "scene_get_hierarchy",
    "node_get_properties",
    "scene_open",
    "scene_save",
    "scene_manage",
    "node_create",
    "node_set_property",
    "node_manage",
    "resource_manage",
    "script_attach",
    "script_manage",
}


def test_host_mirrored_tools_expose_informative_output_schemas():
    tools = {tool.name: tool for tool in asyncio.run(create_server().list_tools())}

    for name in sorted(_HOST_MIRRORED_TOOLS):
        schema = tools[name].output_schema
        assert schema is not None, f"{name} is missing outputSchema"
        assert schema.get("type") == "object", name
        assert schema.get("description"), f"{name} outputSchema needs a description"
        assert schema.get("properties"), f"{name} outputSchema is still generic"


def test_unoverridden_manage_tools_keep_fastmcp_inferred_output_schema():
    tools = {tool.name: tool for tool in asyncio.run(create_server().list_tools())}

    schema = tools["test_manage"].output_schema
    assert schema == {"type": "object", "additionalProperties": True}


def test_high_frequency_write_output_schemas_document_follow_up_fields():
    tools = {tool.name: tool for tool in asyncio.run(create_server().list_tools())}

    node_create = tools["node_create"].output_schema
    assert node_create is not None
    assert {"name", "type", "path", "parent_path", "undoable"} <= set(
        node_create["properties"]
    )

    node_set_property = tools["node_set_property"].output_schema
    assert node_set_property is not None
    assert {"path", "property", "value", "old_value", "undoable"} <= set(
        node_set_property["properties"]
    )

    script_attach = tools["script_attach"].output_schema
    assert script_attach is not None
    assert {"path", "script_path", "had_previous_script", "undoable"} <= set(
        script_attach["properties"]
    )
