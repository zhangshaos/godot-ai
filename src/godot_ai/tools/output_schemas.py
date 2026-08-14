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
