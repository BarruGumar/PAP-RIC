from __future__ import annotations

import json
import mimetypes
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from ric import db
from ric import llm
from ric import music
from ric import voice

WEB_DIR = Path(__file__).resolve().parent / "web"
HOST = "127.0.0.1"
PORT = 8787

_watchdog_stop = threading.Event()
_watchdog_thread: threading.Thread | None = None


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: object) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length)
    if not raw:
        return {}
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("JSON inválido.")
    return data


def _lembrete_dict(item: db.Lembrete) -> dict:
    return {
        "id": item.id,
        "titulo": item.titulo,
        "hora": item.hora,
        "tipo": item.tipo,
        "estado": item.estado,
        "proximo_em": item.proximo_em,
        "criado_em": item.criado_em,
    }


def _watchdog_loop(intervalo: float = 5.0) -> None:
    """Rede de segurança: alerta no servidor mesmo se o JS falhar."""
    alertados: set[int] = set()
    print("[RIC watchdog] ativo (lembretes independentes da UI).", flush=True)
    while not _watchdog_stop.wait(intervalo):
        try:
            devidos = db.devidos()
            ids_atuais = {i.id for i in devidos}
            alertados &= ids_atuais
            for item in devidos:
                if item.id in alertados:
                    continue
                alertados.add(item.id)
                if item.estado != "disparado":
                    db.marcar_disparado(item.id)
                frase = f"É a hora: {item.titulo}"
                print(
                    f"[RIC watchdog] Lembrete #{item.id}: {item.titulo} "
                    f"({item.tipo}, {item.hora})",
                    flush=True,
                )
                voice.beep()
                voice.falar(frase, async_=True)
        except Exception as exc:  # noqa: BLE001
            print(f"[RIC watchdog] erro: {exc}", flush=True)


def iniciar_watchdog(intervalo: float = 5.0) -> None:
    global _watchdog_thread
    if _watchdog_thread and _watchdog_thread.is_alive():
        return
    _watchdog_stop.clear()
    _watchdog_thread = threading.Thread(
        target=_watchdog_loop,
        args=(intervalo,),
        name="ric-reminder-watchdog",
        daemon=True,
    )
    _watchdog_thread.start()


def parar_watchdog() -> None:
    global _watchdog_thread
    _watchdog_stop.set()
    thread = _watchdog_thread
    if thread and thread.is_alive() and thread is not threading.current_thread():
        thread.join(timeout=2.0)
    _watchdog_thread = None


def _serve_file(handler: BaseHTTPRequestHandler, file_path: Path) -> None:
    if not file_path.is_file():
        handler.send_error(404, "Ficheiro não encontrado")
        return
    content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    data = file_path.read_bytes()
    size = len(data)
    range_header = handler.headers.get("Range")
    if range_header and range_header.startswith("bytes="):
        try:
            start_s, end_s = range_header.replace("bytes=", "", 1).split("-", 1)
            start = int(start_s) if start_s else 0
            end = int(end_s) if end_s else size - 1
            end = min(end, size - 1)
            if start < 0 or start > end:
                raise ValueError("range inválido")
            chunk = data[start : end + 1]
            handler.send_response(206)
            handler.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            handler.send_header("Accept-Ranges", "bytes")
            handler.send_header("Content-Type", content_type)
            handler.send_header("Content-Length", str(len(chunk)))
            handler.end_headers()
            handler.wfile.write(chunk)
            return
        except ValueError:
            pass
    handler.send_response(200)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(size))
    handler.send_header("Accept-Ranges", "bytes")
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(data)


class RicHandler(BaseHTTPRequestHandler):
    server_version = "RIC/0.3"

    def log_message(self, fmt: str, *args) -> None:
        if self.command != "GET" or not str(args[0]).startswith("/api/"):
            super().log_message(fmt, *args)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/lembretes":
                itens = [_lembrete_dict(x) for x in db.listar()]
                _json_response(self, 200, {"lembretes": itens})
                return
            if path == "/api/devidos":
                itens = [_lembrete_dict(x) for x in db.devidos()]
                _json_response(self, 200, {"devidos": itens})
                return
            if path == "/api/tipos":
                _json_response(self, 200, {"tipos": list(db.TIPOS_VALIDOS)})
                return
            if path == "/api/llm":
                st = llm.estado()
                st["voz"] = voice.estado()
                _json_response(self, 200, st)
                return
            if path == "/api/perfil":
                _json_response(self, 200, {"perfil": db.obter_perfil()})
                return
            if path == "/api/conversas":
                qs = parse_qs(urlparse(self.path).query)
                limite = int((qs.get("limite") or ["40"])[0])
                msgs = [
                    {
                        "id": m.id,
                        "role": m.role,
                        "conteudo": m.conteudo,
                        "criado_em": m.criado_em,
                    }
                    for m in db.listar_mensagens(limite)
                    if m.role in ("user", "assistant")
                ]
                _json_response(self, 200, {"mensagens": msgs})
                return
            if path == "/api/musica":
                qs = parse_qs(urlparse(self.path).query)
                genero = (qs.get("genero") or [None])[0]
                faixas = music.listar_por_genero(genero)
                _json_response(
                    self,
                    200,
                    {
                        "generos": music.listar_generos(),
                        "musicas": [f.to_dict() for f in faixas],
                    },
                )
                return
            m_stream = re.fullmatch(r"/api/musica/([^/]+)/stream", path)
            if m_stream:
                faixa = music.obter(m_stream.group(1))
                _serve_file(self, faixa.caminho)
                return
        except LookupError as exc:
            _json_response(self, 404, {"erro": str(exc)})
            return
        except ValueError as exc:
            _json_response(self, 400, {"erro": str(exc)})
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/chat":
                data = _read_json(self)
                historico = data.get("historico")
                if historico is not None and not isinstance(historico, list):
                    raise ValueError("historico inválido.")
                resultado = llm.conversar(str(data.get("mensagem", "")), historico)
                _json_response(self, 200, resultado)
                return

            if path == "/api/perfil":
                data = _read_json(self)
                pref = db.guardar_preferencia(
                    str(data.get("chave", "")),
                    str(data.get("valor", "")),
                )
                _json_response(self, 200, {"preferencia": pref, "perfil": db.obter_perfil()})
                return

            if path == "/api/conversas/limpar":
                db.limpar_conversas()
                _json_response(self, 200, {"ok": True})
                return

            if path == "/api/voz/falar":
                data = _read_json(self)
                texto = str(data.get("texto", "")).strip()
                if not texto:
                    raise ValueError("Texto vazio.")
                voice.beep()
                voice.falar(texto, async_=True)
                _json_response(self, 200, {"ok": True, "tts": voice.estado()})
                return

            if path == "/api/lembretes":
                data = _read_json(self)
                item = db.adicionar(
                    str(data.get("titulo", "")),
                    str(data.get("hora", "")),
                    str(data.get("tipo", "tarefa")),
                )
                _json_response(self, 201, {"lembrete": _lembrete_dict(item)})
                return

            m_ok = re.fullmatch(r"/api/lembretes/(\d+)/ok", path)
            if m_ok:
                item = db.confirmar(int(m_ok.group(1)))
                _json_response(self, 200, {"lembrete": _lembrete_dict(item)})
                return

            m_adiar = re.fullmatch(r"/api/lembretes/(\d+)/adiar", path)
            if m_adiar:
                data = _read_json(self)
                minutos = int(data.get("minutos", 10))
                item = db.adiar(int(m_adiar.group(1)), minutos)
                _json_response(self, 200, {"lembrete": _lembrete_dict(item)})
                return

            m_disp = re.fullmatch(r"/api/lembretes/(\d+)/disparar", path)
            if m_disp:
                lembrete_id = int(m_disp.group(1))
                db.obter(lembrete_id)
                db.marcar_disparado(lembrete_id)
                item = db.obter(lembrete_id)
                _json_response(self, 200, {"lembrete": _lembrete_dict(item)})
                return

            m_frase = re.fullmatch(r"/api/lembretes/(\d+)/frase", path)
            if m_frase:
                item = db.obter(int(m_frase.group(1)))
                frase = llm.frase_aviso(item.titulo, item.tipo, item.hora)
                _json_response(
                    self,
                    200,
                    {"id": item.id, "frase": frase, "titulo": item.titulo},
                )
                return

            if path == "/api/musica/tocar":
                data = _read_json(self)
                faixa = music.escolher_para_tocar(
                    str(data["titulo"]) if data.get("titulo") else None,
                    str(data["genero"]) if data.get("genero") else None,
                )
                _json_response(self, 200, {"musica": faixa.to_dict()})
                return
        except llm.LlmError as exc:
            _json_response(self, 503, {"erro": str(exc)})
            return
        except ValueError as exc:
            _json_response(self, 400, {"erro": str(exc)})
            return
        except LookupError as exc:
            _json_response(self, 404, {"erro": str(exc)})
            return
        except json.JSONDecodeError:
            _json_response(self, 400, {"erro": "JSON inválido."})
            return

        _json_response(self, 404, {"erro": "Rota não encontrada."})

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            path = "/index.html"
        rel = path.lstrip("/").replace("\\", "/")
        if ".." in rel.split("/"):
            self.send_error(400, "Pedido inválido")
            return
        file_path = (WEB_DIR / rel).resolve()
        if not str(file_path).startswith(str(WEB_DIR.resolve())):
            self.send_error(400, "Pedido inválido")
            return
        _serve_file(self, file_path)


def servir(host: str = HOST, port: int = PORT, abrir_browser: bool = True) -> None:
    db.init_db()
    music.garantir_pastas()
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    iniciar_watchdog(5.0)
    httpd = ThreadingHTTPServer((host, port), RicHandler)
    url = f"http://{host}:{port}/"
    print(f"RIC interface: {url}", flush=True)
    print(f"Músicas locais: {music.MUSIC_DIR}", flush=True)
    print("Lembretes: watchdog ativo no servidor (beep/TTS se disponível).", flush=True)
    print("Ctrl+C para parar.", flush=True)
    if abrir_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nInterface RIC parada.", flush=True)
    finally:
        parar_watchdog()
        httpd.server_close()
