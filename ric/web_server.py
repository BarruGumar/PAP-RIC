from __future__ import annotations

import json
import mimetypes
import re
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ric import db
from ric import llm

WEB_DIR = Path(__file__).resolve().parent / "web"
HOST = "127.0.0.1"
PORT = 8787


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


class RicHandler(BaseHTTPRequestHandler):
    server_version = "RIC/0.1"

    def log_message(self, fmt: str, *args) -> None:
        # Menos ruído na consola; erros importantes ainda aparecem via print manual.
        if self.command != "GET" or not str(args[0]).startswith("/api/"):
            super().log_message(fmt, *args)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
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
            _json_response(self, 200, llm.estado())
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/chat":
                data = _read_json(self)
                historico = data.get("historico") or []
                if not isinstance(historico, list):
                    raise ValueError("historico inválido.")
                resultado = llm.conversar(str(data.get("mensagem", "")), historico)
                _json_response(self, 200, resultado)
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
        # Impede path traversal
        rel = path.lstrip("/").replace("\\", "/")
        if ".." in rel.split("/"):
            self.send_error(400, "Pedido inválido")
            return
        file_path = (WEB_DIR / rel).resolve()
        if not str(file_path).startswith(str(WEB_DIR.resolve())):
            self.send_error(400, "Pedido inválido")
            return
        if not file_path.is_file():
            self.send_error(404, "Ficheiro não encontrado")
            return
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)


def servir(host: str = HOST, port: int = PORT, abrir_browser: bool = True) -> None:
    db.init_db()
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer((host, port), RicHandler)
    url = f"http://{host}:{port}/"
    print(f"RIC interface: {url}", flush=True)
    print("Ctrl+C para parar.", flush=True)
    if abrir_browser:
        webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nInterface RIC parada.", flush=True)
    finally:
        httpd.server_close()
