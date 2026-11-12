# `ric/cli.py` / `__main__.py`

```text
py -m ric ui          # servidor + UI
py -m ric add "Água" 18:00
py -m ric soon "Teste" 1
py -m ric list
py -m ric voices      # modelos Piper
py -m ric say "Olá"   # Piper
py -m ric say "Olá" --model extras/OUTRA.onnx
py -m ric say "Olá" --speed 1.45 --loop 3
py -m ric tune        # ouvir Piper e afinar ritmo (+/- / s 1.35)
```

`ui` é o caminho principal da demo.  
`say` / `tune` / `voices` permitem experimentar vozes Piper **sem** apagar o tugão medium.
