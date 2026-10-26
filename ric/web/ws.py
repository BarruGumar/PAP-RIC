"""Minimal WebSocket (text frames) for localhost RIC UI."""

from __future__ import annotations

import base64
import hashlib
import struct
import threading
from collections.abc import Callable
from typing import Any


GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def accept_key(sec_websocket_key: str) -> str:
    digest = hashlib.sha1((sec_websocket_key + GUID).encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def encode_text(message: str) -> bytes:
    raw = message.encode("utf-8")
    length = len(raw)
    if length < 126:
        header = struct.pack("!BB", 0x81, length)
    elif length < 65536:
        header = struct.pack("!BBH", 0x81, 126, length)
    else:
        header = struct.pack("!BBQ", 0x81, 127, length)
    return header + raw


def decode_frames(buffer: bytes) -> tuple[list[str], bytes]:
    """Decode complete text frames; return messages and leftover buffer."""
    messages: list[str] = []
    i = 0
    while True:
        if len(buffer) - i < 2:
            break
        b1, b2 = buffer[i], buffer[i + 1]
        opcode = b1 & 0x0F
        masked = (b2 & 0x80) != 0
        length = b2 & 0x7F
        header_len = 2
        if length == 126:
            if len(buffer) - i < 4:
                break
            length = struct.unpack("!H", buffer[i + 2 : i + 4])[0]
            header_len = 4
        elif length == 127:
            if len(buffer) - i < 10:
                break
            length = struct.unpack("!Q", buffer[i + 2 : i + 10])[0]
            header_len = 10
        mask_len = 4 if masked else 0
        total = header_len + mask_len + length
        if len(buffer) - i < total:
            break
        start = i + header_len
        if masked:
            mask = buffer[start : start + 4]
            payload = bytearray(buffer[start + 4 : start + 4 + length])
            for idx in range(len(payload)):
                payload[idx] ^= mask[idx % 4]
            data = bytes(payload)
        else:
            data = buffer[start : start + length]
        i += total
        if opcode == 0x8:  # close
            break
        if opcode == 0x1:
            messages.append(data.decode("utf-8"))
        elif opcode == 0x9:  # ping — ignore; client handles
            pass
    return messages, buffer[i:]


class WsHub:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._clients: list[Callable[[str], None]] = []

    def add(self, send: Callable[[str], None]) -> Callable[[], None]:
        with self._lock:
            self._clients.append(send)

        def remove() -> None:
            with self._lock:
                if send in self._clients:
                    self._clients.remove(send)

        return remove

    def broadcast(self, message: str) -> None:
        with self._lock:
            clients = list(self._clients)
        dead: list[Callable[[str], None]] = []
        for send in clients:
            try:
                send(message)
            except Exception:  # noqa: BLE001
                dead.append(send)
        if dead:
            with self._lock:
                for send in dead:
                    if send in self._clients:
                        self._clients.remove(send)

    def broadcast_event(self, event: dict[str, Any]) -> None:
        import json

        self.broadcast(json.dumps(event, ensure_ascii=False))
