# `ric/core/events.py`

Barramento in-process. O watchdog e a API publicam eventos (`state`, `alert`, …); o hub WebSocket subscreve e envia JSON aos browsers.

Estados de rosto previstos: `idle`, `listening`, `thinking`, `speaking`, `alert`, `music`, `story`. Nesta fatia usam-se sobretudo `idle` e `alert`.
