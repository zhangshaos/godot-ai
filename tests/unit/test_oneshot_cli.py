"""One-shot CLI dispatch, JSON I/O, and backend lifecycle contracts."""

from __future__ import annotations

import json
import os
from types import SimpleNamespace
from typing import Any

import httpx
import pytest

import godot_ai
from godot_ai import oneshot
from godot_ai.attach.ensure import AttachStartupError, BackendStatus


def _backend_status() -> BackendStatus:
    return BackendStatus(
        instance_id="instance-a",
        server_version=godot_ai.__version__,
        attach_protocol_version=1,
        ws_port=9500,
        exclude_domains=(),
        owner_type="attach",
        tool_catalog_hash="catalog-a",
        package_path="/tmp/godot-ai/src",
    )


@pytest.mark.parametrize("command", ["call", "status", "tools"])
def test_root_main_dispatches_oneshot_commands_before_server_parser(
    monkeypatch,
    command: str,
) -> None:
    received: list[list[str]] = []
    monkeypatch.setattr(oneshot, "main", lambda argv: received.append(list(argv)))

    argv = [command]
    if command == "call":
        argv.append("editor_state")
    godot_ai.main(argv)

    assert received == [argv]


def test_root_help_discovers_oneshot_commands(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        godot_ai.main(["--help"])

    assert exc_info.value.code == 0
    output = " ".join(capsys.readouterr().out.split())
    assert "godot-ai status --json" in output
    assert "godot-ai tools --json" in output
    assert "godot-ai call <tool>" in output


def test_status_emits_json_only(monkeypatch, capsys) -> None:
    async def fake_status(port: int) -> dict[str, Any]:
        assert port == 8123
        return {"http_port": port, "running": False}

    monkeypatch.setattr(oneshot, "run_status", fake_status)

    oneshot.main(["status", "--json", "--port", "8123"])

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"http_port": 8123, "running": False}
    assert captured.err == ""


def test_call_accepts_json_alias_for_arguments(monkeypatch, capsys) -> None:
    received: list[object] = []

    async def fake_call(
        tool_name: str,
        arguments: dict[str, Any],
        port: int,
        ws_port: int,
        exclude_domains: tuple[str, ...],
    ) -> dict[str, Any]:
        received.extend([tool_name, arguments, port, ws_port, exclude_domains])
        return {"scene": "res://main.tscn"}

    monkeypatch.setattr(oneshot, "run_call", fake_call)

    oneshot.main(
        [
            "call",
            "scene_get_hierarchy",
            "--json",
            '{"depth": 4}',
            "--port",
            "8123",
            "--ws-port",
            "9567",
            "--exclude-domains",
            "audio,theme",
        ]
    )

    captured = capsys.readouterr()
    assert received == [
        "scene_get_hierarchy",
        {"depth": 4},
        8123,
        9567,
        ("audio", "theme"),
    ]
    assert json.loads(captured.out) == {"scene": "res://main.tscn"}
    assert captured.err == ""


def test_call_accepts_args_and_output_json(monkeypatch, capsys) -> None:
    async def fake_call(*_args) -> dict[str, Any]:
        return {"ok": True}

    monkeypatch.setattr(oneshot, "run_call", fake_call)

    oneshot.main(["call", "editor_state", "--args", "{}", "--output", "json"])

    captured = capsys.readouterr()
    assert json.loads(captured.out) == {"ok": True}
    assert captured.err == ""


@pytest.mark.parametrize("raw", ["{", "[]", "null", "3"])
def test_call_rejects_invalid_or_non_object_arguments(raw: str, capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        oneshot.main(["call", "editor_state", "--args", raw])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert captured.out == ""
    assert "tool arguments" in captured.err


def test_tool_failure_uses_stderr_json_and_nonzero_exit(monkeypatch, capsys) -> None:
    async def fail(*_args) -> Any:
        raise oneshot.ToolCallFailed(
            {"error": {"code": "PLUGIN_DISCONNECTED", "message": "No editor"}}
        )

    monkeypatch.setattr(oneshot, "run_call", fail)

    with pytest.raises(SystemExit) as exc_info:
        oneshot.main(["call", "editor_state"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "error": {"code": "PLUGIN_DISCONNECTED", "message": "No editor"}
    }


def test_attach_startup_failure_preserves_exit_code_and_stdout_contract(
    monkeypatch,
    capsys,
) -> None:
    async def fail(*_args) -> Any:
        raise AttachStartupError(
            "PORT_OCCUPIED",
            "occupied",
            hint="choose another port",
            exit_code=98,
        )

    monkeypatch.setattr(oneshot, "run_tools", fail)

    with pytest.raises(SystemExit) as exc_info:
        oneshot.main(["tools"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 98
    assert captured.out == ""
    assert "PORT_OCCUPIED" in captured.err
    assert "choose another port" in captured.err


def test_http_failure_uses_stderr_json_and_nonzero_exit(monkeypatch, capsys) -> None:
    async def fail(*_args) -> Any:
        raise httpx.ConnectError("backend refused")

    monkeypatch.setattr(oneshot, "run_tools", fail)

    with pytest.raises(SystemExit) as exc_info:
        oneshot.main(["tools"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == "MCP_BACKEND_HTTP_ERROR"
    assert "backend refused" in captured.err


def test_unexpected_failure_uses_stderr_json_and_nonzero_exit(monkeypatch, capsys) -> None:
    async def fail(*_args) -> Any:
        raise RuntimeError("client exploded")

    monkeypatch.setattr(oneshot, "run_tools", fail)

    with pytest.raises(SystemExit) as exc_info:
        oneshot.main(["tools"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 1
    assert captured.out == ""
    assert json.loads(captured.err)["error"]["code"] == "MCP_CLIENT_ERROR"
    assert "client exploded" in captured.err


def test_disable_telemetry_sets_env_before_operation(monkeypatch) -> None:
    seen: list[str | None] = []

    async def fake_status(_port: int) -> dict[str, Any]:
        seen.append(os.environ.get("GODOT_AI_DISABLE_TELEMETRY"))
        return {"running": False}

    monkeypatch.setattr(oneshot, "run_status", fake_status)
    monkeypatch.delenv("GODOT_AI_DISABLE_TELEMETRY", raising=False)

    oneshot.main(["status", "--disable-telemetry"])

    assert seen == ["true"]


async def test_run_status_does_not_start_backend(monkeypatch) -> None:
    calls: list[object] = []

    async def fake_probe(port: int, **_kwargs) -> BackendStatus | None:
        calls.append(port)
        return None

    monkeypatch.setattr(oneshot, "probe_backend", fake_probe)

    result = await oneshot.run_status(8123)

    assert calls == [8123]
    assert result == {"http_port": 8123, "running": False}


async def test_run_status_serializes_backend_status(monkeypatch) -> None:
    status = _backend_status()

    async def fake_probe(_port: int, **_kwargs) -> BackendStatus:
        return status

    monkeypatch.setattr(oneshot, "probe_backend", fake_probe)

    result = await oneshot.run_status(8123)

    assert result["running"] is True
    assert result["http_port"] == 8123
    assert result["instance_id"] == "instance-a"
    assert result["exclude_domains"] == ()


async def test_backend_operation_reuses_ensure_lease_proxy_and_client(monkeypatch) -> None:
    events: list[object] = []
    status = _backend_status()

    class FakeEnsurer:
        def __init__(self, port: int, ws_port: int, domains: tuple[str, ...]) -> None:
            events.append(("ensurer", port, ws_port, domains))
            self.base_url = f"http://127.0.0.1:{port}"
            self.mcp_url = f"{self.base_url}/mcp"

        async def ensure(self) -> BackendStatus:
            events.append("ensure")
            return status

    class FakeLease:
        def __init__(self, base_url: str, ensure_backend) -> None:
            events.append(("lease", base_url))
            self.ensure_backend = ensure_backend

        async def start(self, initial_status: BackendStatus) -> None:
            events.append(("start", initial_status.instance_id))

        async def sync(self, current_status: BackendStatus) -> None:
            events.append(("sync", current_status.instance_id))

        async def close(self) -> None:
            events.append("close")

    class FakeProxy:
        def __init__(self, ensure_ready, observe_backend) -> None:
            self.ensure_ready = ensure_ready
            self.observe_backend = observe_backend

    class FakeClient:
        def __init__(self, proxy: FakeProxy, *, timeout: Any, init_timeout: float) -> None:
            events.append(("client", timeout, init_timeout))
            self.proxy = proxy

        async def __aenter__(self):
            events.append("client_enter")
            await self.proxy.ensure_ready()
            observed = await self.proxy.observe_backend()
            assert observed is status
            return self

        async def __aexit__(self, *_args) -> None:
            events.append("client_exit")

    async def fake_probe(port: int, *, timeout: float) -> BackendStatus:
        events.append(("observe", port, timeout))
        return status

    def fake_proxy(mcp_url: str, ensure_ready, observe_backend) -> FakeProxy:
        events.append(("proxy", mcp_url))
        return FakeProxy(ensure_ready, observe_backend)

    async def operation(client: Any) -> dict[str, Any]:
        assert isinstance(client, FakeClient)
        events.append("operation")
        return {"ok": True}

    monkeypatch.setattr(oneshot, "BackendEnsurer", FakeEnsurer)
    monkeypatch.setattr(oneshot, "LeaseClient", FakeLease)
    monkeypatch.setattr(oneshot, "Client", FakeClient)
    monkeypatch.setattr(oneshot, "probe_backend", fake_probe)
    monkeypatch.setattr(oneshot, "create_attach_proxy", fake_proxy)

    result = await oneshot._run_backend_operation(8123, 9567, ("audio",), operation)

    assert result == {"ok": True}
    assert ("ensurer", 8123, 9567, ("audio",)) in events
    assert ("proxy", "http://127.0.0.1:8123/mcp") in events
    assert ("sync", "instance-a") in events
    assert "operation" in events
    assert events[-1] == "close"


async def test_backend_operation_closes_lease_when_operation_fails(monkeypatch) -> None:
    events: list[str] = []
    status = _backend_status()

    class FakeEnsurer:
        base_url = "http://127.0.0.1:8000"
        mcp_url = "http://127.0.0.1:8000/mcp"

        def __init__(self, *_args) -> None:
            pass

        async def ensure(self) -> BackendStatus:
            return status

    class FakeLease:
        def __init__(self, *_args) -> None:
            pass

        async def start(self, _status: BackendStatus) -> None:
            pass

        async def sync(self, _status: BackendStatus) -> None:
            pass

        async def close(self) -> None:
            events.append("close")

    class FakeClient:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args) -> None:
            pass

    monkeypatch.setattr(oneshot, "BackendEnsurer", FakeEnsurer)
    monkeypatch.setattr(oneshot, "LeaseClient", FakeLease)
    monkeypatch.setattr(oneshot, "Client", FakeClient)
    monkeypatch.setattr(oneshot, "create_attach_proxy", lambda *_args: object())

    async def operation(_client: Any) -> Any:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        await oneshot._run_backend_operation(8000, 9500, (), operation)

    assert events == ["close"]


async def test_run_tools_serializes_tool_catalog(monkeypatch) -> None:
    received: list[object] = []

    class FakeTool:
        def __init__(self, name: str) -> None:
            self.name = name

        def model_dump(self, **kwargs) -> dict[str, Any]:
            received.append(kwargs)
            return {"name": self.name}

    class FakeClient:
        async def list_tools(self):
            return [FakeTool("editor_state"), FakeTool("scene_get_hierarchy")]

    async def fake_run(
        port: int,
        ws_port: int,
        exclude_domains: tuple[str, ...],
        operation,
    ) -> Any:
        received.append((port, ws_port, exclude_domains))
        return await operation(FakeClient())

    monkeypatch.setattr(oneshot, "_run_backend_operation", fake_run)

    result = await oneshot.run_tools(8123, 9567, ("audio",))

    assert result == {
        "count": 2,
        "tools": [{"name": "editor_state"}, {"name": "scene_get_hierarchy"}],
    }
    assert (8123, 9567, ("audio",)) in received
    assert {"mode": "json", "by_alias": True, "exclude_none": True} in received


async def test_run_call_returns_tool_data(monkeypatch) -> None:
    class FakeClient:
        async def call_tool(self, name: str, arguments: dict[str, Any], *, raise_on_error: bool):
            assert name == "editor_state"
            assert arguments == {"session_id": "demo@1234"}
            assert raise_on_error is False
            return SimpleNamespace(
                is_error=False,
                data={"is_playing": False},
                structured_content={"is_playing": False},
            )

    async def fake_run(_port, _ws_port, _domains, operation):
        return await operation(FakeClient())

    monkeypatch.setattr(oneshot, "_run_backend_operation", fake_run)

    result = await oneshot.run_call(
        "editor_state",
        {"session_id": "demo@1234"},
        8000,
        9500,
        (),
    )

    assert result == {"is_playing": False}


async def test_run_call_preserves_structured_tool_error(monkeypatch) -> None:
    error = {"error": {"code": "PLUGIN_DISCONNECTED", "message": "No editor"}}

    class FakeClient:
        async def call_tool(self, *_args, **_kwargs):
            return SimpleNamespace(is_error=True, data=None, structured_content=error)

    async def fake_run(_port, _ws_port, _domains, operation):
        return await operation(FakeClient())

    monkeypatch.setattr(oneshot, "_run_backend_operation", fake_run)

    with pytest.raises(oneshot.ToolCallFailed) as exc_info:
        await oneshot.run_call("editor_state", {}, 8000, 9500, ())

    assert exc_info.value.payload == error


async def test_run_call_wraps_unstructured_tool_error(monkeypatch) -> None:
    class FakeClient:
        async def call_tool(self, *_args, **_kwargs):
            return SimpleNamespace(is_error=True, data=None, structured_content=None)

    async def fake_run(_port, _ws_port, _domains, operation):
        return await operation(FakeClient())

    monkeypatch.setattr(oneshot, "_run_backend_operation", fake_run)

    with pytest.raises(oneshot.ToolCallFailed) as exc_info:
        await oneshot.run_call("editor_state", {}, 8000, 9500, ())

    assert exc_info.value.payload["error"]["code"] == "MCP_TOOL_ERROR"


async def test_run_call_falls_back_to_structured_content(monkeypatch) -> None:
    class FakeClient:
        async def call_tool(self, *_args, **_kwargs):
            return SimpleNamespace(
                is_error=False,
                data=None,
                structured_content={"value": 7},
            )

    async def fake_run(_port, _ws_port, _domains, operation):
        return await operation(FakeClient())

    monkeypatch.setattr(oneshot, "_run_backend_operation", fake_run)

    result = await oneshot.run_call("custom", {}, 8000, 9500, ())

    assert result == {"value": 7}
