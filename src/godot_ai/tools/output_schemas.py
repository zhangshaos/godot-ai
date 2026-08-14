"""Authoritative MCP output schemas for high-value Godot tools.

Keep these schemas permissive about additive fields so diagnostics such as
``new_errors_since_last_call`` can be appended without invalidating successful
tool results. The named fields document the stable result contract exposed to
MCP hosts; operation-rollup schemas list the common fields a caller may receive.
"""

from typing import Any

_JSON_VALUE: dict[str, Any] = {}
_NODE_SUMMARY: dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "path": {"type": "string"},
        "children_count": {"type": "integer"},
    },
    "additionalProperties": True,
}

SESSION_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Connected Godot editor sessions and server-global domain exclusions.",
    "properties": {
        "sessions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string"},
                    "name": {"type": "string"},
                    "godot_version": {"type": "string"},
                    "project_path": {"type": "string"},
                    "plugin_version": {"type": "string"},
                    "server_version": {"type": "string"},
                    "protocol_version": {"type": "integer"},
                    "current_scene": {"type": "string"},
                    "play_state": {"type": "string"},
                    "readiness": {"type": "string"},
                    "editor_pid": {"type": "integer"},
                    "server_launch_mode": {"type": "string"},
                    "connected_at": {"type": "string"},
                    "last_seen": {"type": "string"},
                    "is_active": {"type": "boolean"},
                },
                "additionalProperties": True,
            },
        },
        "count": {"type": "integer"},
        "exclude_domains": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

EDITOR_STATE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Current Godot editor, scene, readiness, and running-game state.",
    "properties": {
        "current_scene": {"type": "string"},
        "godot_version": {"type": "string"},
        "project_name": {"type": "string"},
        "readiness": {"type": "string"},
        "is_playing": {"type": "boolean"},
        "game_capture_ready": {"type": "boolean"},
        "helper_live": {"type": "boolean"},
        "session_active": {"type": "boolean"},
        "game_status": {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "active": {"type": "boolean"},
                "ready": {"type": "boolean"},
                "helper_live": {"type": "boolean"},
                "session_active": {"type": "boolean"},
            },
            "additionalProperties": True,
        },
    },
    "additionalProperties": True,
}

SCENE_HIERARCHY_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Paginated flat scene-tree nodes for the edited scene.",
    "properties": {
        "nodes": {"type": "array", "items": _NODE_SUMMARY},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "total_count": {"type": "integer"},
        "has_more": {"type": "boolean"},
    },
    "additionalProperties": True,
}

NODE_PROPERTIES_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Editor-visible properties for one scene node.",
    "properties": {
        "path": {"type": "string"},
        "node_type": {"type": "string"},
        "properties": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string"},
                    "value": _JSON_VALUE,
                    "class_name": {"type": "string"},
                    "hint": {"type": "integer"},
                    "hint_string": {"type": "string"},
                },
                "additionalProperties": True,
            },
        },
        "count": {"type": "integer"},
        "total_count": {"type": "integer"},
        "unknown_fields": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

SCENE_OPEN_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Scene navigation result and switch-settle status.",
    "properties": {
        "path": {"type": "string"},
        "force_reload": {"type": "boolean"},
        "reloaded_from_disk": {"type": "boolean"},
        "previous_scene_path": {"type": "string"},
        "switched": {"type": "boolean"},
        "settle": {
            "type": "string",
            "enum": ["already_current", "settled", "not_waited", "timeout"],
        },
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

SCENE_SAVE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Saved scene path plus undoability metadata.",
    "properties": {
        "path": {"type": "string"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

SCENE_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific scene result for create, save_as, or get_roots.",
    "properties": {
        "path": {"type": "string"},
        "root_type": {"type": "string"},
        "root_name": {"type": "string"},
        "scenes": {"type": "array", "items": {"type": "string"}},
        "current_scene": {"type": "string"},
        "count": {"type": "integer"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

NODE_CREATE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Created node identity and path for follow-up node operations.",
    "properties": {
        "name": {"type": "string"},
        "type": {"type": "string"},
        "path": {"type": "string"},
        "parent_path": {"type": "string"},
        "scene_path": {"type": "string"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

NODE_SET_PROPERTY_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Applied node property value and previous serialized value.",
    "properties": {
        "path": {"type": "string"},
        "property": {"type": "string"},
        "value": _JSON_VALUE,
        "old_value": _JSON_VALUE,
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

NODE_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific node result; may describe children/groups or a completed mutation."
    ),
    "properties": {
        "path": {"type": "string"},
        "old_path": {"type": "string"},
        "new_path": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "children": {"type": "array", "items": _NODE_SUMMARY},
        "groups": {"type": "array", "items": {"type": "string"}},
        "count": {"type": "integer"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

RESOURCE_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific resource search, inspection, assignment, or creation result."
    ),
    "properties": {
        "path": {"type": "string"},
        "resource_path": {"type": "string"},
        "property": {"type": "string"},
        "type": {"type": "string"},
        "properties": {"type": ["object", "array"]},
        "resources": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "total_count": {"type": "integer"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "has_more": {"type": "boolean"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

SCRIPT_ATTACH_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Script attachment result for one node.",
    "properties": {
        "path": {"type": "string"},
        "script_path": {"type": "string"},
        "had_previous_script": {"type": "boolean"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

SCRIPT_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific script source, symbol outline, or detach result.",
    "properties": {
        "path": {"type": "string"},
        "content": {"type": "string"},
        "line_count": {"type": "integer"},
        "size": {"type": "integer"},
        "class_name": {"type": "string"},
        "extends": {"type": "string"},
        "functions": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "signals": {"type": "array", "items": {"type": "string"}},
        "exports": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "function_count": {"type": "integer"},
        "signal_count": {"type": "integer"},
        "export_count": {"type": "integer"},
        "had_script": {"type": "boolean"},
        "removed_script": {"type": "string"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

NODE_FIND_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Paginated scene nodes matching the requested name, type, and/or group filters.",
    "properties": {
        "nodes": {"type": "array", "items": _NODE_SUMMARY},
        "total_count": {"type": "integer"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "has_more": {"type": "boolean"},
    },
    "additionalProperties": True,
}

_LOG_ENTRY: dict[str, Any] = {
    "type": "object",
    "properties": {
        "source": {"type": "string"},
        "level": {"type": "string"},
        "text": {"type": "string"},
        "run_id": {"type": "string"},
        "path": {"type": "string"},
        "line": {"type": "integer"},
        "function": {"type": "string"},
    },
    "additionalProperties": True,
}

LOGS_READ_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Recent plugin, editor, or game log entries plus pagination and run metadata.",
    "properties": {
        "lines": {
            "type": "array",
            "items": {
                "anyOf": [
                    {"type": "string"},
                    _LOG_ENTRY,
                ]
            },
        },
        "entries": {"type": "array", "items": _LOG_ENTRY},
        "total_count": {"type": "integer"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "has_more": {"type": "boolean"},
        "run_id": {"type": "string"},
        "current_run_id": {"type": "string"},
        "current_run": {"type": "boolean"},
        "stale_run_id": {"type": "boolean"},
        "dropped_count": {"type": "integer"},
        "next_cursor": {"type": "integer"},
        "helper_live": {"type": "boolean"},
        "session_active": {"type": "boolean"},
        "game_status": {"type": "object", "additionalProperties": True},
    },
    "additionalProperties": True,
}

_API_MEMBER: dict[str, Any] = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
    },
    "additionalProperties": True,
}

API_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Version-correct Godot ClassDB metadata for the requested class and sections.",
    "properties": {
        "class_name": {"type": "string"},
        "engine_version": {"type": "string"},
        "parent_class": {"type": "string"},
        "inheritance_chain": {"type": "array", "items": {"type": "string"}},
        "can_instantiate": {"type": "boolean"},
        "is_singleton": {"type": "boolean"},
        "include_inherited": {"type": "boolean"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "properties": {"type": "array", "items": _API_MEMBER},
        "methods": {"type": "array", "items": _API_MEMBER},
        "signals": {"type": "array", "items": _API_MEMBER},
        "enums": {"type": "array", "items": _API_MEMBER},
        "constants": {"type": "array", "items": _API_MEMBER},
        "inheritors": {"type": "array", "items": {"type": "string"}},
        "concrete_inheritors": {"type": "array", "items": {"type": "string"}},
        "property_count": {"type": "integer"},
        "property_returned_count": {"type": "integer"},
        "method_count": {"type": "integer"},
        "method_returned_count": {"type": "integer"},
        "signal_count": {"type": "integer"},
        "signal_returned_count": {"type": "integer"},
        "enum_count": {"type": "integer"},
        "enum_returned_count": {"type": "integer"},
        "constant_count": {"type": "integer"},
        "constant_returned_count": {"type": "integer"},
        "inheritor_count": {"type": "integer"},
        "inheritor_returned_count": {"type": "integer"},
        "concrete_inheritor_count": {"type": "integer"},
        "concrete_inheritor_returned_count": {"type": "integer"},
    },
    "additionalProperties": True,
}

SESSION_ACTIVATE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Active-session selection result, including ambiguity candidates when a hint is not unique."
    ),
    "properties": {
        "status": {"type": "string"},
        "active_session_id": {"type": "string"},
        "matched": {"type": "string"},
        "matched_name": {"type": "string"},
        "message": {"type": "string"},
        "candidates": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "available": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
    },
    "additionalProperties": True,
}

EDITOR_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific editor health/state, selection, monitor, log-clear, quit, "
        "or game-eval result."
    ),
    "properties": {
        "backend_running": {"type": "boolean"},
        "editor_connected": {"type": "boolean"},
        "session_id": {"type": ["string", "null"]},
        "current_scene": {"type": ["string", "null"]},
        "project_name": {"type": ["string", "null"]},
        "godot_version": {"type": "string"},
        "readiness": {"type": ["string", "null"]},
        "is_playing": {"type": "boolean"},
        "game_status": {"type": "object", "additionalProperties": True},
        "selected_paths": {"type": "array", "items": {"type": "string"}},
        "count": {"type": "integer"},
        "monitors": {"type": "object", "additionalProperties": True},
        "cleared_count": {"type": "integer"},
        "debugger_errors_cleared": {"type": "integer"},
        "status": {"type": "string"},
        "message": {"type": "string"},
        "result": _JSON_VALUE,
    },
    "additionalProperties": True,
}

PROJECT_RUN_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Project play result with launch mode, liveness state, and recent editor diagnostics."
    ),
    "properties": {
        "mode": {"type": "string"},
        "scene": {"type": "string"},
        "autosave": {"type": "boolean"},
        "was_already_running": {"type": "boolean"},
        "game_status": {"type": "object", "additionalProperties": True},
        "helper_live": {"type": "boolean"},
        "session_active": {"type": "boolean"},
        "recent_errors": {
            "type": "array",
            "items": {"type": "object", "additionalProperties": True},
        },
        "recent_errors_scope": {"type": "string"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

PROJECT_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific project stop or ProjectSettings read/write result.",
    "properties": {
        "key": {"type": "string"},
        "value": _JSON_VALUE,
        "old_value": _JSON_VALUE,
        "type": {"type": "string"},
        "stopped": {"type": "boolean"},
        "was_running": {"type": "boolean"},
        "readiness_after": {"type": "string"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

SCRIPT_CREATE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Created or overwritten GDScript file metadata, import settlement, cleanup hints, "
        "and parse diagnostics."
    ),
    "properties": {
        "path": {"type": "string"},
        "size": {"type": "integer"},
        "committed": {"type": "boolean"},
        "import_settled": {"type": "boolean"},
        "import_settle": {"type": "string"},
        "class_name": {"type": "string"},
        "class_registration": {"type": "string"},
        "diagnostics": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "diagnostics_scope": {"type": "string"},
        "diagnostics_status": {"type": "string"},
        "cleanup": {"type": "object", "additionalProperties": True},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

SCRIPT_PATCH_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Anchor-based GDScript patch result with replacement count and parse diagnostics."
    ),
    "properties": {
        "path": {"type": "string"},
        "replacements": {"type": "integer"},
        "size": {"type": "integer"},
        "committed": {"type": "boolean"},
        "diagnostics": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "diagnostics_scope": {"type": "string"},
        "diagnostics_status": {"type": "string"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

FILESYSTEM_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific project filesystem read/write, reimport, scan, or search result."
    ),
    "properties": {
        "path": {"type": "string"},
        "content": {"type": "string"},
        "size": {"type": "integer"},
        "line_count": {"type": "integer"},
        "files": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "total_count": {"type": "integer"},
        "offset": {"type": "integer"},
        "limit": {"type": "integer"},
        "has_more": {"type": "boolean"},
        "reimported": {"type": "array", "items": {"type": "string"}},
        "skipped_non_imported": {"type": "array", "items": {"type": "string"}},
        "not_found": {"type": "array", "items": {"type": "string"}},
        "scan_completed": {"type": "boolean"},
        "global_classes_registered_delta": {"type": "integer"},
        "diagnostics": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "cleanup": {"type": "object", "additionalProperties": True},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

SIGNAL_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific node signal listing or connection mutation result.",
    "properties": {
        "path": {"type": "string"},
        "signal": {"type": "string"},
        "target": {"type": "string"},
        "method": {"type": "string"},
        "signals": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "connections": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "signal_count": {"type": "integer"},
        "connection_count": {"type": "integer"},
        "editor_connection_count": {"type": "integer"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

AUTOLOAD_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific autoload singleton listing, addition, or removal result.",
    "properties": {
        "autoloads": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "name": {"type": "string"},
        "path": {"type": "string"},
        "singleton": {"type": "boolean"},
        "removed": {"type": "boolean"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

INPUT_MAP_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific InputMap action listing, creation, removal, or binding result."
    ),
    "properties": {
        "actions": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "action": {"type": "string"},
        "deadzone": {"type": "number"},
        "event": {"type": "object", "additionalProperties": True},
        "created": {"type": "boolean"},
        "removed": {"type": "boolean"},
        "binding_added": {"type": "boolean"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

GAME_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific running-game scene inspection, UI inspection, input injection, "
        "or input-state result."
    ),
    "properties": {
        "nodes": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "elements": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "path": {"type": "string"},
        "type": {"type": "string"},
        "properties": {"type": "object", "additionalProperties": True},
        "actions": {"type": "object", "additionalProperties": True},
        "count": {"type": "integer"},
        "frames_elapsed": {"type": "integer"},
        "status": {"type": "string"},
    },
    "additionalProperties": True,
}

TEST_RUN_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "GDScript test-run summary with failures, optional verbose results, duration, "
        "and edited-scene context."
    ),
    "properties": {
        "passed": {"type": "integer"},
        "failed": {"type": "integer"},
        "skipped": {"type": "integer"},
        "total": {"type": "integer"},
        "duration_ms": {"type": "number"},
        "suites": {"type": "array", "items": _JSON_VALUE},
        "failures": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "results": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "edited_scene": {"type": "string"},
        "scene_warning": {"type": "string"},
    },
    "additionalProperties": True,
}

TEST_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Most recent GDScript test-run result, matching test_run without re-execution.",
    "properties": TEST_RUN_OUTPUT_SCHEMA["properties"],
    "additionalProperties": True,
}

BATCH_EXECUTE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Batch editor-command execution result with per-command outcomes and rollback state."
    ),
    "properties": {
        "succeeded": {"type": "integer"},
        "stopped_at": {"type": ["integer", "null"]},
        "results": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "rolled_back": {"type": "boolean"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

EDITOR_RELOAD_PLUGIN_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Plugin reload acknowledgement or completed reconnect result.",
    "properties": {
        "status": {"type": "string"},
        "transport_will_drop": {"type": "boolean"},
        "old_session_id": {"type": "string"},
        "new_session_id": {"type": "string"},
        "guidance": {"type": "string"},
    },
    "additionalProperties": True,
}

ANIMATION_CREATE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Created Animation clip metadata for follow-up track authoring.",
    "properties": {
        "player_path": {"type": "string"},
        "animation_name": {"type": "string"},
        "name": {"type": "string"},
        "length": {"type": "number"},
        "loop_mode": {"type": "string"},
        "overwritten": {"type": "boolean"},
        "player_created": {"type": "boolean"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

ANIMATION_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific AnimationPlayer authoring, playback, validation, or inspection result."
    ),
    "properties": {
        "player_path": {"type": "string"},
        "animation_name": {"type": "string"},
        "name": {"type": "string"},
        "length": {"type": "number"},
        "loop_mode": {"type": "string"},
        "track_count": {"type": "integer"},
        "tracks": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "animations": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "broken_count": {"type": "integer"},
        "issues": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "autoplay": {"type": "string"},
        "playing": {"type": "boolean"},
        "stopped": {"type": "boolean"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

CLIENT_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific supported-client status, configuration, or removal result.",
    "properties": {
        "clients": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "client": {"type": "string"},
        "display_name": {"type": "string"},
        "status": {"type": "string"},
        "installed": {"type": "boolean"},
        "config_path": {"type": "string"},
        "configured": {"type": "boolean"},
        "removed": {"type": "boolean"},
    },
    "additionalProperties": True,
}

UI_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific Control layout, text, subtree-build, or draw-recipe result.",
    "properties": {
        "path": {"type": "string"},
        "text": {"type": "string"},
        "preset": {"type": "string"},
        "root_path": {"type": "string"},
        "nodes_created": {"type": "integer"},
        "paths": {"type": "array", "items": {"type": "string"}},
        "op_count": {"type": "integer"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

THEME_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific Theme creation, slot update, stylebox authoring, or assignment result."
    ),
    "properties": {
        "path": {"type": "string"},
        "theme_path": {"type": "string"},
        "node_path": {"type": "string"},
        "class_name": {"type": "string"},
        "name": {"type": "string"},
        "value": _JSON_VALUE,
        "applied": {"type": "boolean"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

MATERIAL_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific material creation, inspection, parameter update, listing, "
        "or assignment result."
    ),
    "properties": {
        "path": {"type": "string"},
        "resource_path": {"type": "string"},
        "node_path": {"type": "string"},
        "type": {"type": "string"},
        "params": {"type": "object", "additionalProperties": True},
        "uniforms": {"type": "object", "additionalProperties": True},
        "materials": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "slot": {"type": "string"},
        "preset": {"type": "string"},
        "undoable": {"type": "boolean"},
        "reason": {"type": "string"},
    },
    "additionalProperties": True,
}

PARTICLE_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific particle emitter creation, configuration, restart, inspection, "
        "or preset result."
    ),
    "properties": {
        "path": {"type": "string"},
        "node_path": {"type": "string"},
        "type": {"type": "string"},
        "properties": {"type": "object", "additionalProperties": True},
        "process_material": {"type": "object", "additionalProperties": True},
        "draw_passes": {"type": "array", "items": _JSON_VALUE},
        "preset": {"type": "string"},
        "applied_main": {"type": "array", "items": {"type": "string"}},
        "applied_process": {"type": "array", "items": {"type": "string"}},
        "applied_draw": {"type": "array", "items": {"type": "string"}},
        "restarted": {"type": "boolean"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

CAMERA_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific Camera2D/Camera3D creation, configuration, follow, inspection, "
        "or preset result."
    ),
    "properties": {
        "path": {"type": "string"},
        "camera_path": {"type": "string"},
        "type": {"type": "string"},
        "current": {"type": "boolean"},
        "properties": {"type": "object", "additionalProperties": True},
        "cameras": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "preset": {"type": "string"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

AUDIO_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific audio-player creation, stream/playback update, preview, "
        "or resource-list result."
    ),
    "properties": {
        "path": {"type": "string"},
        "player_path": {"type": "string"},
        "type": {"type": "string"},
        "stream_path": {"type": "string"},
        "duration_seconds": {"type": "number"},
        "volume_db": {"type": "number"},
        "pitch_scale": {"type": "number"},
        "autoplay": {"type": "boolean"},
        "bus": {"type": "string"},
        "playing": {"type": "boolean"},
        "stopped": {"type": "boolean"},
        "audio": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

TILEMAP_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific TileMapLayer cell write, rectangular fill, clear, "
        "or used-cell read result."
    ),
    "properties": {
        "path": {"type": "string"},
        "map_x": {"type": "integer"},
        "map_y": {"type": "integer"},
        "source_id": {"type": "integer"},
        "atlas_col": {"type": "integer"},
        "atlas_row": {"type": "integer"},
        "cells_filled": {"type": "integer"},
        "rect": {"type": "object", "additionalProperties": True},
        "cleared": {"type": "boolean"},
        "cells": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

TILESET_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Read-only TileSet atlas tile coordinates or atlas-image metadata and payload.",
    "properties": {
        "tiles": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "image_base64": {"type": "string"},
        "width": {"type": "integer"},
        "height": {"type": "integer"},
        "original_width": {"type": "integer"},
        "original_height": {"type": "integer"},
        "format": {"type": "string"},
    },
    "additionalProperties": True,
}

GRIDMAP_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": (
        "Operation-specific GridMap item write, 3D fill, clear, used-cell read, "
        "or MeshLibrary listing result."
    ),
    "properties": {
        "path": {"type": "string"},
        "map_x": {"type": "integer"},
        "map_y": {"type": "integer"},
        "map_z": {"type": "integer"},
        "item": {"type": "integer"},
        "orientation": {"type": "integer"},
        "cells_filled": {"type": "integer"},
        "rect": {"type": "object", "additionalProperties": True},
        "cleared": {"type": "boolean"},
        "cells": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "library": {"type": "string"},
        "items": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "count": {"type": "integer"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}

CSG_MANAGE_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "description": "Operation-specific CSG shape creation or boolean-operation update result.",
    "properties": {
        "path": {"type": "string"},
        "name": {"type": "string"},
        "shape": {"type": "string"},
        "operation": {"type": "string"},
        "undoable": {"type": "boolean"},
    },
    "additionalProperties": True,
}
