# `ric/cli.py` / `__main__.py`

```text
py -m ric ui          # servidor + UI
py -m ric add "Água" 18:00
py -m ric soon "Teste" 1
py -m ric list
py -m ric voices      # default + extras + estado Chatterbox
py -m ric say "Olá"   # Piper (default)
py -m ric say "Olá" --model extras/OUTRA.onnx
py -m ric say "Olá" --speed 1.45 --loop 3
py -m ric say "Olá" --engine chatterbox
py -m ric say "Olá" --engine chatterbox --prompt extras/pt_pt_ref.wav
py -m ric tts-compare --play
py -m ric record-ref  # grava WAV >5 s para clonagem zero-shot
py -m ric tune        # ouvir Piper e afinar ritmo (+/- / s 1.35)
```

`ui` é o caminho principal da demo.  
`say` / `tune` / `voices` / `tts-compare` permitem experimentar vozes **sem** apagar o tugão medium.  
Chatterbox exige `requirements-chatterbox.txt` e usa referência pt-PT (oficial ou `--prompt`).
