from __future__ import annotations

import json
import mimetypes
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ric.config import Settings
from ric.core.events import EventBus
from ric.db.connection import Database
from ric.reminders.service import ReminderPermissionError, ReminderService
from ric.voice import VoiceService
from ric.web.ws import WsHub, accept_key, decode_frames, encode_text

STATIC_DIR = Path(__file__).resolve().parent / "static"


class RicApp:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = Database(settings.db_path)
        self.db.init_schema()
        self.reminders = ReminderService(self.db, settings)
        self.events = EventBus()
        self.ws = WsHub()
        self.events.subscribe(self.ws.broadcast_event)
        self.voice = VoiceService(
            piper_model=settings.piper_model,
            piper_bin=settings.piper_bin,
            cache_dir=settings.data_dir / "tts",
            length_scale=settings.piper_length_scale,
            on_speaking=self._on_speaking,
        )
        self._watchdog_stop = threading.Event()
        self._watchdog_thread: threading.Thread | None = None
        self._alert_lock = threading.Lock()
        self._last_alert_key: tuple[int, int] | None = None

    def _on_speaking(self, speaking: bool) -> None:
        # Nesta fatia o TTS só corre em alertas — voltar a "alert" para o painel Já fiz.
        if speaking:
            self.events.set_state("speaking")
        else:
            self.events.set_state("alert")

    def start_watchdog(self, interval: float = 3.0) -> None:
        if self._watchdog_thread and self._watchdog_thread.is_alive():
            return
        self._watchdog_stop.clear()
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            args=(interval,),
            name="ric-reminder-watchdog",
            daemon=True,
        )
        self._watchdog_thread.start()

    def stop_watchdog(self) -> None:
        self._watchdog_stop.set()

    def _watchdog_loop(self, interval: float) -> None:
        while not self._watchdog_stop.wait(interval):
            try:
                if not self._alert_lock.acquire(blocking=False):
                    continue
                try:
                    due = self.reminders.due_now()
                    if not due:
                        continue
                    # Um alerta de cada vez — vários em paralelo = eco no browser
                    item = due[0]
                    if item.estado != "disparado":
                        self.reminders.mark_fired(item.id)
                    updated = self.reminders.register_alert(item.id)
                    key = (updated.id, updated.avisos_feitos)
                    if key == self._last_alert_key:
                        continue
                    self._last_alert_key = key
                    frase = f"Atenção, é a hora de {updated.titulo}."
                    wav = self.voice.synthesize_alert(
                        frase, stem=f"alert-{updated.id}-{updated.avisos_feitos}"
                    )
                    audio_url = None
                    if wav is not None:
                        audio_url = f"/api/v1/tts/{wav.name}"
                    self.events.set_state("alert")
                    payload = {
                        "type": "alert",
                        "reminder": updated.to_dict(),
                        "phrase": frase,
                        "audio_url": audio_url,
                        "play_id": f"{updated.id}-{updated.avisos_feitos}",
                    }
                    if wav is None:
                        self.voice.speak(frase, async_=True, with_beep=False)
                    self.events.publish(payload)
                    print(
                        f"[RIC] Alerta lembrete #{updated.id}: {updated.titulo}",
                        flush=True,
                    )
                finally:
                    self._alert_lock.release()
            except Exception as exc:  # noqa: BLE001
                print(f"[RIC] watchdog erro: {exc}", flush=True)


def make_handler(app: RicApp) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            if app.settings.debug:
                super().log_message(fmt, *args)

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/ws":
                self._handle_ws()
                return
            if path.startswith("/api/v1/"):
                self._handle_api_get(path)
                return
            self._serve_static(path)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = parsed.path
            if not path.startswith("/api/v1/"):
                self._json(404, {"ok": False, "error": "Não encontrado", "data": None})
                return
            self._handle_api_post(path)

        def _json(self, status: int, payload: dict) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _read_json(self) -> dict:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return {}
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("JSON inválido")
            return data

        def _handle_api_get(self, path: str) -> None:
            try:
                if path == "/api/v1/health":
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": {
                                "state": app.events.state,
                                "voice": app.voice.status(),
                            },
                        },
                    )
                    return
                if path == "/api/v1/reminders":
                    items = [r.to_dict() for r in app.reminders.list_all()]
                    self._json(200, {"ok": True, "error": None, "data": items})
                    return
                if path == "/api/v1/reminders/next":
                    nxt = app.reminders.next_pending()
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": nxt.to_dict() if nxt else None,
                        },
                    )
                    return
                if path == "/api/v1/state":
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": {"state": app.events.state},
                        },
                    )
                    return
                if path.startswith("/api/v1/tts/") and path.endswith(".wav"):
                    name = path.rsplit("/", 1)[-1]
                    if ".." in name or "/" in name or "\\" in name:
                        self.send_error(400)
                        return
                    tts_dir = (app.settings.data_dir / "tts").resolve()
                    wav = (tts_dir / name).resolve()
                    if not str(wav).startswith(str(tts_dir)) or not wav.is_file():
                        self.send_error(404)
                        return
                    data = wav.read_bytes()
                    self.send_response(200)
                    self.send_header("Content-Type", "audio/wav")
                    self.send_header("Content-Length", str(len(data)))
                    self.send_header("Cache-Control", "no-store")
                    self.end_headers()
                    self.wfile.write(data)
                    return
                self._json(404, {"ok": False, "error": "Não encontrado", "data": None})
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"ok": False, "error": str(exc), "data": None})

        def _handle_api_post(self, path: str) -> None:
            try:
                body = self._read_json()
            except Exception as exc:  # noqa: BLE001
                self._json(400, {"ok": False, "error": str(exc), "data": None})
                return
            try:
                if path == "/api/v1/reminders":
                    item = app.reminders.create(
                        titulo=str(body.get("titulo", "")),
                        hora=str(body.get("hora", "")),
                        tipo=str(body.get("tipo", "tarefa")),
                        critico=bool(body.get("critico", False)),
                        caregiver_authenticated=bool(
                            body.get("caregiver_authenticated", False)
                        ),
                    )
                    app.events.publish(
                        {"type": "reminders_changed", "reminder": item.to_dict()}
                    )
                    self._json(201, {"ok": True, "error": None, "data": item.to_dict()})
                    return
                if path.startswith("/api/v1/reminders/") and path.endswith("/confirm"):
                    rid = int(path.split("/")[4])
                    item = app.reminders.confirm(rid)
                    app.events.set_state("idle")
                    app.events.publish(
                        {"type": "reminder_confirmed", "reminder": item.to_dict()}
                    )
                    self._json(200, {"ok": True, "error": None, "data": item.to_dict()})
                    return
                if path.startswith("/api/v1/reminders/") and path.endswith("/snooze"):
                    rid = int(path.split("/")[4])
                    minutes = int(body.get("minutes", 10))
                    item = app.reminders.snooze(rid, minutes=minutes)
                    app.events.set_state("idle")
                    app.events.publish(
                        {"type": "reminder_snoozed", "reminder": item.to_dict()}
                    )
                    self._json(200, {"ok": True, "error": None, "data": item.to_dict()})
                    return
                self._json(404, {"ok": False, "error": "Não encontrado", "data": None})
            except ReminderPermissionError as exc:
                self._json(403, {"ok": False, "error": str(exc), "data": None})
            except (ValueError, LookupError) as exc:
                self._json(400, {"ok": False, "error": str(exc), "data": None})
            except Exception as exc:  # noqa: BLE001
                self._json(500, {"ok": False, "error": str(exc), "data": None})

        def _serve_static(self, path: str) -> None:
            rel = "index.html" if path in ("", "/") else path.lstrip("/")
            file_path = (STATIC_DIR / rel).resolve()
            if not str(file_path).startswith(str(STATIC_DIR.resolve())):
                self.send_error(403)
                return
            if not file_path.is_file():
                self.send_error(404)
                return
            ctype, _ = mimetypes.guess_type(str(file_path))
            data = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle_ws(self) -> None:
            key = self.headers.get("Sec-WebSocket-Key")
            if not key:
                self.send_error(400, "Missing Sec-WebSocket-Key")
                return
            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept_key(key))
            self.end_headers()

            sock = self.connection
            lock = threading.Lock()

            def send(message: str) -> None:
                with lock:
                    sock.sendall(encode_text(message))

            unsub = app.ws.add(send)
            send(app.events.encode({"type": "state", "state": app.events.state}))
            nxt = app.reminders.next_pending()
            send(
                app.events.encode(
                    {
                        "type": "next_reminder",
                        "reminder": nxt.to_dict() if nxt else None,
                    }
                )
            )

            buffer = b""
            try:
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk
                    messages, buffer = decode_frames(buffer)
                    for msg in messages:
                        if msg == "ping":
                            send(app.events.encode({"type": "pong"}))
            finally:
                unsub()

    return Handler


def run_server(settings: Settings | None = None) -> None:
    settings = settings or Settings.from_env()
    app = RicApp(settings)
    app.events.set_state("idle")
    app.start_watchdog()
    handler = make_handler(app)
    server = ThreadingHTTPServer((settings.host, settings.port), handler)
    print(
        f"RIC em http://{settings.host}:{settings.port}/  (WS /ws)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nA parar RIC…", flush=True)
    finally:
        app.stop_watchdog()
        server.server_close()
