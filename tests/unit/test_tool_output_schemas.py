"""Contract tests for informative MCP output schemas on host-mirrored tools."""

from __future__ import annotations

import asyncio

from godot_ai.server import create_server

_HOST_MIRRORED_TOOLS = {
    "session_activate",
    "session_manage",
    "editor_state",
    "logs_read",
    "editor_manage",
    "editor_reload_plugin",
    "scene_get_hierarchy",
    "node_get_properties",
    "node_find",
    "scene_open",
    "scene_save",
    "scene_manage",
    "node_create",
    "node_set_property",
    "node_manage",
    "project_run",
    "project_manage",
    "script_create",
    "script_patch",
    "script_attach",
    "script_manage",
    "resource_manage",
    "api_manage",
    "filesystem_manage",
    "signal_manage",
    "autoload_manage",
    "input_map_manage",
    "game_manage",
    "test_run",
    "test_manage",
    "batch_execute",
    "client_manage",
    "ui_manage",
    "theme_manage",
    "animation_create",
    "animation_manage",
    "material_manage",
    "particle_manage",
    "camera_manage",
    "audio_manage",
    "tilemap_manage",
    "tileset_manage",
    "gridmap_manage",
    "csg_manage",
}


def test_host_mirrored_tools_expose_informative_output_schemas():
    tools = {tool.name: tool for tool in asyncio.run(create_server().list_tools())}

    for name in sorted(_HOST_MIRRORED_TOOLS):
        schema = tools[name].output_schema
        assert schema is not None, f"{name} is missing outputSchema"
        assert schema.get("type") == "object", name
        assert schema.get("description"), f"{name} outputSchema needs a description"
        assert schema.get("properties"), f"{name} outputSchema is still generic"


def test_editor_screenshot_keeps_multimodal_output_unconstrained():
    tools = {tool.name: tool for tool in asyncio.run(create_server().list_tools())}

    # editor_screenshot may return MCP ImageContent/list blocks when include_image=True.
    # An object output schema would falsely constrain that multimodal return contract.
    assert tools["editor_screenshot"].output_schema is None


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

    batch_execute = tools["batch_execute"].output_schema
    assert batch_execute is not None
    assert {"succeeded", "stopped_at", "results", "rolled_back", "undoable"} <= set(
        batch_execute["properties"]
    )
