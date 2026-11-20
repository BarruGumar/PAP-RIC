# Roteiro — treinar wake-word «ei RIC» (do zero)

**Data:** 2026-11-19  
**Onde:** Google Colab (GPU) + notebook comunidade 2026  
**Resultado:** `ei_ric.onnx` → `py -m ric wake-install …` → `ric-data/wake/ric.onnx`  
**Pasta do projecto:** `C:\Users\pedro\Desktop\PAP`

Enquanto não houver `ric.onnx`, o RIC usa o temporário **hey jarvis**.

---

## 0. Fecha sessões antigas

1. Fecha separadores Colab antigos do treino.
2. Se ainda estiveres ligado: **Ambiente de execução → Terminar sessão**.

Não uses o notebook oficial `automatic_model_training.ipynb` (está partido).

---

## 1. Abre o notebook certo

https://colab.research.google.com/github/alfiedennen/openwakeword-colab-2026/blob/main/train_wakeword.ipynb

1. **Copiar para o Drive** (recomendado).
2. **Ambiente de execução → Alterar tipo de ambiente de execução**
   - Acelerador: **T4 GPU**
   - **Versão do tempo de execução: 2026.07 ou 2026.04** (Python **3.12**)  
     **Não** deixes «Mais recente» (isso é 3.13 e parte o `piper-phonemize`).
3. **Guardar** → **Ligar**.
4. Confirma numa célula:

```python
!python --version
```

Tem de dizer **3.12.x**.

---

## 2. Edita só estas duas linhas

Procura a célula com `TARGET_PHRASE` / `MODEL_NAME` e deixa **exactamente**:

```python
TARGET_PHRASE = ["ei ric"]
MODEL_NAME = "ei_ric"
```

- Frase com espaço: `"ei ric"`
- Nome do modelo **sem** espaços: `ei_ric` (snake_case)

---

## 3. Célula extra (obrigatória) — logo a seguir às instalações

O notebook esquece o `deep-phonemizer` e o S3 do modelo muitas vezes dá 403.  
**Depois** da célula de install que imprime `All openwakeword deps … import cleanly`, cria uma célula nova e corre:

```python
!pip install -q deep-phonemizer==0.0.19

!sed -i 's|checkpoint = torch.load(checkpoint_path, map_location=device)|checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=False)|' \
  /usr/local/lib/python3.12/dist-packages/dp/model/model.py

import os, hashlib, urllib.request
dst = "/content/openwakeword/openwakeword/resources/en_us_cmudict_forward.pt"
os.makedirs(os.path.dirname(dst), exist_ok=True)
url = "https://huggingface.co/TaterTotterson/DeepPhonemizer/resolve/main/en_us_cmudict_forward.pt"
if not os.path.isfile(dst) or os.path.getsize(dst) < 60_000_000:
    print("A descarregar DeepPhonemizer…")
    urllib.request.urlretrieve(url, dst)
h = hashlib.sha256(open(dst, "rb").read()).hexdigest()
assert h == "c2e1fb223d7e027bf7b33052540c6f71d19db6d7fd87ab8671152b8b114501c2", h
print("OK deep-phonemizer + checkpoint")
```

Se o `openwakeword` ainda não estiver clonado nessa altura, corre esta célula **depois** da célula que faz `git clone` do openwakeword (antes de generate_clips).

---

## 4. Correr o resto

**Ambiente de execução → Executar tudo**  
(ou corre célula a célula **por ordem**, sem saltar).

Ordem importante:

1. Install + verify  
2. Clone / patches / pre-flight  
3. Downloads (mel, IR, FMA, ACAV) — demora  
4. Config (`TARGET_PHRASE` / `MODEL_NAME`)  
5. Célula do `deep-phonemizer` (secção 3)  
6. Generate clips → Resample → Augment → Treino → ONNX  

Tempo típico: **~1,5–2,5 h** no Colab grátis. Não feches o separador.

Ignora avisos de:

- `libhwloc` / `ldconfig`
- `protobuf` conflicts
- `CUDAExecutionProvider` / `FutureWarning` do audiomentations  

Só paramos em **traceback vermelho** / `AssertionError`.

---

## 5. Checklist a meio do caminho

| Momento | O que deve aparecer |
|---|---|
| Após install | `Python: 3.12…` + `import cleanly` |
| Após config | `model_name: ei_ric` (sem espaços no caminho) |
| Após generate_clips | 4 pastas com muitos `.wav` (positivos **e** negativos > 0) |
| Após augment | 4 ficheiros `*_features_*.npy` + `PASS` |
| Após treino | download / ficheiro `ei_ric.onnx` |

---

## 6. Descarregar

1. Ícone **pasta** à esquerda  
2. Procura `ei_ric.onnx`  
3. ⋮ → **Download** → `C:\Users\pedro\Downloads\ei_ric.onnx`

---

## 7. Instalar no RIC (PC)

```powershell
cd C:\Users\pedro\Desktop\PAP
py -m ric wake-install C:\Users\pedro\Downloads\ei_ric.onnx
py -m ric ui
```

Diz **«ei RIC»**. No terminal deve aparecer algo como `wake=openwakeword phrase=ei RIC`.

Se disparar pouco: `$env:RIC_WAKE_THRESHOLD="0.4"` e volta a `py -m ric ui`.  
O botão **Falar** continua sempre a funcionar.

---

## Problemas comuns

| Sintoma | Fix |
|---|---|
| `piper-phonemize` / Python 3.13 | Runtime version **2026.07** (3.12) |
| `No module named 'dp'` / `negative_train: 0` | Célula da secção 3 + voltar a generate_clips |
| Caminho `/content/ei ric_output/` | `MODEL_NAME = "ei_ric"` sem espaços; recomeçar config |
| Treino pede `.npy` em falta | Correr **Augment** antes do trainer |
| Colab desliga | Religa com a **mesma** versão 2026.07 + GPU; células idempotentes saltam o que já está em cache |
