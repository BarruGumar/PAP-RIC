"""Integration — REST envelope + regra 2A via HTTP."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from ric.config import Settings
from ric.web.server import RicApp, make_handler


@pytest.fixture()
def http_server(tmp_path: Path):
    settings = Settings(data_dir=tmp_path, host="127.0.0.1", port=0)
    app = RicApp(settings)
    handler = make_handler(app)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{port}"
    yield base, app
    server.shutdown()
    server.server_close()


def _request(base: str, path: str, data: dict | None = None, method: str = "GET"):
    body = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        base + path,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"} if body else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        payload = json.loads(exc.read().decode("utf-8"))
        return exc.code, payload


def test_health_and_create_list(http_server) -> None:
    base, _app = http_server
    status, payload = _request(base, "/api/v1/health")
    assert status == 200
    assert payload["ok"] is True

    status, payload = _request(
        base,
        "/api/v1/reminders",
        {"titulo": "Água", "hora": "15:00", "tipo": "tarefa"},
        method="POST",
    )
    assert status == 201
    assert payload["data"]["titulo"] == "Água"

    status, payload = _request(base, "/api/v1/reminders")
    assert status == 200
    assert len(payload["data"]) == 1


def test_medicamento_forbidden_without_caregiver(http_server) -> None:
    base, _app = http_server
    status, payload = _request(
        base,
        "/api/v1/reminders",
        {"titulo": "Med", "hora": "09:00", "tipo": "medicamento", "critico": True},
        method="POST",
    )
    assert status == 403
    assert payload["ok"] is False
