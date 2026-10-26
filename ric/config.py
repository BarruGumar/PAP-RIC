from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    host: str = "127.0.0.1"
    port: int = 8787
    data_dir: Path = Path("./ric-data")
    debug: bool = False
    reminder_max_alerts: int = 3
    reminder_retry_minutes: int = 2
    piper_model: Path | None = None
    piper_bin: str | None = None
    piper_length_scale: float = 1.35

    @property
    def db_path(self) -> Path:
        return self.data_dir / "ric.db"

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> Settings:
        root = Path(__file__).resolve().parent.parent
        _load_dotenv(env_file or (root / ".env"))
        data = Path(os.environ.get("RIC_DATA_DIR", "./ric-data"))
        if not data.is_absolute():
            data = (root / data).resolve()

        model_raw = os.environ.get("RIC_PIPER_MODEL", "").strip()
        if model_raw:
            model = Path(model_raw)
            if not model.is_absolute():
                model = (root / model).resolve()
        else:
            candidates = [
                data / "vozes" / "pt_PT-tugao-medium.onnx",
                root / "voz-teste" / "vozes" / "pt_PT-tugao-medium.onnx",
            ]
            model = next((p for p in candidates if p.is_file()), None)

        piper_bin = os.environ.get("RIC_PIPER_BIN", "").strip() or None
        length_scale = float(os.environ.get("RIC_PIPER_LENGTH_SCALE", "1.35"))
        return cls(
            host=os.environ.get("RIC_HOST", "127.0.0.1"),
            port=int(os.environ.get("RIC_PORT", "8787")),
            data_dir=data,
            debug=os.environ.get("RIC_DEBUG", "0") in ("1", "true", "True"),
            reminder_max_alerts=int(os.environ.get("RIC_REMINDER_MAX_ALERTS", "3")),
            reminder_retry_minutes=int(os.environ.get("RIC_REMINDER_RETRY_MINUTES", "2")),
            piper_model=model,
            piper_bin=piper_bin,
            piper_length_scale=length_scale,
        )
