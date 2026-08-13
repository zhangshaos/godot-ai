"""One-shot JSON CLI client for shell and automation access to the MCP backend."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import asdict
from typing import Any

import httpx
from fastmcp import Client

from godot_ai import __version__
from godot_ai.attach.ensure import AttachStartupError, BackendEnsurer, BackendStatus, probe_backend
from godot_ai.attach.lease import LeaseClient
from godot_ai.attach.proxy import (
    DEFAULT_INIT_TIMEOUT_SECONDS,
    DEFAULT_MONITOR_PROBE_TIMEOUT_SECONDS,
    create_attach_proxy,
)
from godot_ai.tools.domains import parse_exclude_list


class ToolCallFailed(RuntimeError):
    """Carry one structured MCP tool failure to the CLI boundary."""

    def __init__(self, payload: dict[str, Any]) -> None:
        super().__init__("MCP tool call failed")
        self.payload = payload


BackendOperation = Callable[[Client[Any]], Awaitable[Any]]


def _add_backend_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--port", type=int, default=8000, help="Shared backend HTTP port")
    parser.add_argument("--ws-port", type=int, default=9500, help="Godot editor WebSocket port")
    parser.add_argument(
        "--exclude-domains",
        default="",
        help="Comma-separated backend tool domains to exclude",
    )
    parser.add_argument(
        "--disable-telemetry",
        action="store_true",
        help="Disable anonymous telemetry in this command and any backend it spawns",
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="godot-ai",
        description="One-shot JSON access to the Godot AI MCP backend",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"godot-ai {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Probe the shared backend without starting it")
    _add_backend_options(status)
    status.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON (accepted for explicit automation; JSON is the default)",
    )

    tools = subparsers.add_parser("tools", help="List tools from the shared MCP backend")
    _add_backend_options(tools)
    tools.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON (accepted for explicit automation; JSON is the default)",
    )

    call = subparsers.add_parser("call", help="Call one MCP tool and emit its JSON result")
    call.add_argument("tool_name", help="MCP tool name")
    _add_backend_options(call)
    call.add_argument(
        "--args",
        "--json",
        dest="arguments_json",
        default="{}",
        metavar="JSON",
        help="Tool arguments as one JSON object (default: {})",
    )
    call.add_argument(
        "--output",
        choices=["json"],
        default="json",
        help="Output format (currently only json)",
    )
    return parser


def _json_object(parser: argparse.ArgumentParser, raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        parser.error(f"tool arguments must be valid JSON: {exc.msg}")
    if not isinstance(value, dict):
        parser.error("tool arguments must decode to a JSON object")
    return value


def _write_json(value: Any, *, stream: Any) -> None:
    json.dump(value, stream, ensure_ascii=False, sort_keys=True)
    stream.write("\n")


def _status_payload(port: int, status: BackendStatus | None) -> dict[str, Any]:
    if status is None:
        return {
            "http_port": port,
            "running": False,
        }
    payload = asdict(status)
    payload["http_port"] = port
    payload["running"] = True
    return payload


async def run_status(port: int) -> dict[str, Any]:
    """Probe backend state without changing backend lifecycle."""

    return _status_payload(port, await probe_backend(port))


async def _run_backend_operation(
    port: int,
    ws_port: int,
    exclude_domains: tuple[str, ...],
    operation: BackendOperation,
) -> Any:
    """Run one MCP operation while reusing attach start/adopt and lease semantics."""

    ensurer = BackendEnsurer(port, ws_port, exclude_domains)
    lease: LeaseClient

    async def ensure_ready() -> BackendStatus:
        status = await ensurer.ensure()
        await lease.sync(status)
        return status

    async def observe_backend() -> BackendStatus | None:
        return await probe_backend(port, timeout=DEFAULT_MONITOR_PROBE_TIMEOUT_SECONDS)

    lease = LeaseClient(ensurer.base_url, ensurer.ensure)
    initial_status = await ensurer.ensure()
    await lease.start(initial_status)
    proxy = create_attach_proxy(ensurer.mcp_url, ensure_ready, observe_backend)
    try:
        async with Client(
            proxy,
            timeout=None,
            init_timeout=DEFAULT_INIT_TIMEOUT_SECONDS,
        ) as client:
            return await operation(client)
    finally:
        await lease.close()


async def run_tools(
    port: int,
    ws_port: int,
    exclude_domains: tuple[str, ...],
) -> dict[str, Any]:
    """List the backend MCP tool catalog in JSON-serializable form."""

    async def operation(client: Client[Any]) -> dict[str, Any]:
        tools = await client.list_tools()
        serialized = [
            tool.model_dump(mode="json", by_alias=True, exclude_none=True)
            for tool in tools
        ]
        return {
            "count": len(serialized),
            "tools": serialized,
        }

    return await _run_backend_operation(port, ws_port, exclude_domains, operation)


async def run_call(
    tool_name: str,
    arguments: dict[str, Any],
    port: int,
    ws_port: int,
    exclude_domains: tuple[str, ...],
) -> Any:
    """Call one backend MCP tool and return only its structured tool payload."""

    async def operation(client: Client[Any]) -> Any:
        result = await client.call_tool(tool_name, arguments, raise_on_error=False)
        if result.is_error:
            structured = result.structured_content
            if isinstance(structured, dict):
                raise ToolCallFailed(structured)
            raise ToolCallFailed(
                {
                    "error": {
                        "code": "MCP_TOOL_ERROR",
                        "message": f"Tool {tool_name!r} returned an unstructured MCP error.",
                    }
                }
            )
        if result.data is not None:
            return result.data
        if result.structured_content is not None:
            return result.structured_content
        return {}

    return await _run_backend_operation(port, ws_port, exclude_domains, operation)


def _parse_excludes(parser: argparse.ArgumentParser, raw: str) -> tuple[str, ...]:
    try:
        return tuple(sorted(parse_exclude_list(raw)))
    except ValueError as exc:
        parser.error(str(exc))


def main(argv: Sequence[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    exclude_domains = _parse_excludes(parser, args.exclude_domains)
    if args.disable_telemetry:
        os.environ["GODOT_AI_DISABLE_TELEMETRY"] = "true"

    try:
        if args.command == "status":
            result = asyncio.run(run_status(args.port))
        elif args.command == "tools":
            result = asyncio.run(run_tools(args.port, args.ws_port, exclude_domains))
        else:
            arguments = _json_object(parser, args.arguments_json)
            result = asyncio.run(
                run_call(
                    args.tool_name,
                    arguments,
                    args.port,
                    args.ws_port,
                    exclude_domains,
                )
            )
    except ToolCallFailed as exc:
        _write_json(exc.payload, stream=sys.stderr)
        raise SystemExit(1) from exc
    except AttachStartupError as exc:
        print(exc.stderr_text(), file=sys.stderr)
        raise SystemExit(exc.exit_code) from exc
    except httpx.HTTPError as exc:
        _write_json(
            {
                "error": {
                    "code": "MCP_BACKEND_HTTP_ERROR",
                    "message": str(exc),
                }
            },
            stream=sys.stderr,
        )
        raise SystemExit(1) from exc
    except Exception as exc:
        _write_json(
            {
                "error": {
                    "code": "MCP_CLIENT_ERROR",
                    "message": str(exc),
                }
            },
            stream=sys.stderr,
        )
        raise SystemExit(1) from exc

    _write_json(result, stream=sys.stdout)
