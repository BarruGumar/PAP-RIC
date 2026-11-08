# `ric/cli.py` / `__main__.py`

```text
py -m ric ui          # servidor + UI
py -m ric add "Água" 18:00
py -m ric soon "Teste" 1
py -m ric list
py -m ric voices      # default + extras
py -m ric say "Olá"   # testa TTS (default)
py -m ric say "Olá" --model extras/OUTRA.onnx
py -m ric say "Olá" --speed 1.45 --loop 3
py -m ric tune        # ouvir TTS e afinar ritmo (+/- / s 1.35)
```

`ui` é o caminho principal da demo. `say` / `tune` / `voices` permitem experimentar vozes **sem** apagar o tugão medium. Na UI, botão **Ouvir voz** = amostras Piper.
