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
from ric.llm import LlmService
from ric.voice import VoiceService
from ric.voice.session import VoiceSession
from ric.voice.stt import SpeechToText, SttUnavailableError
from ric.voice.tts import format_alert_phrase
from ric.voice.wake import WakeWordService
from ric.web.ws import WsHub, accept_key, decode_frames, encode_text

STATIC_DIR = Path(__file__).resolve().parent / "static"
MAX_BODY_BYTES = 10 * 1024 * 1024


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
            engine=settings.tts_engine,
            on_speaking=self._on_speaking,
        )
        self.stt = SpeechToText(
            cache_dir=settings.data_dir / "stt",
            model_size=settings.whisper_model,
            language=settings.stt_language,
        )
        self.llm = LlmService(
            reminders=self.reminders,
            base_url=settings.ollama_url,
            model=settings.llm_model,
            timeout=settings.llm_timeout,
            on_reminders_changed=self._on_reminder_from_llm,
        )
        self.session = VoiceSession(
            events=self.events,
            stt=self.stt,
            llm=self.llm,
            tts=self.voice,
        )
        self.wake = WakeWordService(on_detect=self.session.on_wake)
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

    def _on_reminder_from_llm(self, reminder: dict) -> None:
        """Actualiza a UI quando o LLM cria um lembrete por voz."""
        self.events.publish({"type": "reminders_changed", "reminder": reminder})
        nxt = self.reminders.next_pending()
        self.events.publish(
            {
                "type": "next_reminder",
                "reminder": nxt.to_dict() if nxt is not None else None,
            }
        )

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
                    frase = format_alert_phrase(updated.titulo)
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
            if length > MAX_BODY_BYTES:
                raise ValueError("Pedido demasiado grande")
            self.connection.settimeout(15.0)
            try:
                raw = self.rfile.read(length)
            finally:
                try:
                    self.connection.settimeout(None)
                except Exception:  # noqa: BLE001
                    pass
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
                                "voice": {
                                    **app.voice.status(),
                                    "wake": app.wake.status(),
                                    "stt": app.stt.status(),
                                    "llm": app.llm.status(),
                                    "last_transcript": app.session.last_transcript,
                                    "last_reply": app.session.last_reply,
                                },
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
                if path == "/api/v1/voice/preview":
                    # Ouvir TTS (afinar voz) — não é STT
                    texto = str(
                        body.get("text")
                        or format_alert_phrase("beber água")
                    ).strip()
                    if app.events.state == "alert":
                        raise ValueError("Alerta activo — termina o lembrete primeiro.")
                    wav = app.voice.synthesize_alert(texto, stem="preview")
                    if wav is None:
                        app.voice.speak(texto, async_=True, with_beep=False)
                        self._json(
                            200,
                            {
                                "ok": True,
                                "error": None,
                                "data": {
                                    "text": texto,
                                    "audio_url": None,
                                    "length_scale": app.voice.length_scale,
                                },
                            },
                        )
                        return
                    prev = app.events.state
                    app.events.set_state("speaking")
                    audio_url = f"/api/v1/tts/{wav.name}"
                    app.events.publish(
                        {
                            "type": "tts_preview",
                            "text": texto,
                            "audio_url": audio_url,
                            "play_id": f"preview-{wav.stem}",
                        }
                    )

                    def _back_idle() -> None:
                        import time as _t

                        _t.sleep(0.4)
                        if app.events.state == "speaking":
                            app.events.set_state(
                                "idle" if prev in ("idle", "speaking") else prev
                            )

                    threading.Thread(
                        target=_back_idle, name="ric-preview-idle", daemon=True
                    ).start()
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": {
                                "text": texto,
                                "audio_url": audio_url,
                                "length_scale": app.voice.length_scale,
                            },
                        },
                    )
                    return
                if path == "/api/v1/voice/wake":
                    app.wake.trigger_manual()
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": {"state": app.events.state},
                        },
                    )
                    return
                if path == "/api/v1/voice/cancel":
                    app.session.cancel()
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": {"state": app.events.state},
                        },
                    )
                    return
                if path == "/api/v1/voice/utterance":
                    if app.events.state not in ("listening", "thinking"):
                        raise ValueError(
                            "Sessão de voz não activa. Carrega em Falar primeiro."
                        )
                    audio_b64 = str(body.get("audio_base64", "")).strip()
                    if not audio_b64:
                        raise ValueError("audio_base64 é obrigatório")
                    content_type = str(body.get("content_type", "audio/wav"))
                    text = app.session.process_base64(
                        audio_b64, content_type=content_type
                    )
                    self._json(
                        200,
                        {
                            "ok": True,
                            "error": None,
                            "data": {
                                "text": text,
                                "reply": app.session.last_reply,
                                "audio_url": app.session.last_audio_url,
                                "state": app.events.state,
                            },
                        },
                    )
                    return
                self._json(404, {"ok": False, "error": "Não encontrado", "data": None})
            except ReminderPermissionError as exc:
                self._json(403, {"ok": False, "error": str(exc), "data": None})
            except SttUnavailableError as exc:
                self._json(503, {"ok": False, "error": str(exc), "data": None})
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
    app.wake.start()
    handler = make_handler(app)
    server = ThreadingHTTPServer((settings.host, settings.port), handler)
    print(
        f"RIC em http://{settings.host}:{settings.port}/  (WS /ws)",
        flush=True,
    )
    print(
        f"[RIC] wake={app.wake.status()['mode']} "
        f"stt={app.stt.status()['engine']} "
        f"llm={'ok' if app.llm.available else 'off'} ({app.llm.model}) "
        f"timeout={app.llm.timeout:.0f}s",
        flush=True,
    )
    def _warm_voice_stack() -> None:
        # Em paralelo no arranque: evita 1.º «Falar» a pagar carga a frio.
        app.voice.warm_up()
        app.stt.warm_up()
        if app.llm.available:
            app.llm.warm_up()

    threading.Thread(
        target=_warm_voice_stack,
        name="ric-voice-warmup",
        daemon=True,
    ).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nA parar RIC…", flush=True)
    finally:
        app.wake.stop()
        app.stop_watchdog()
        server.server_close()
