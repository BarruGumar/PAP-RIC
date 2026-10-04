# Explicação: `ric/music.py` + `ric/musica/`

## Para que serve

Biblioteca de músicas **100% offline**:

- lê ficheiros já guardados em `ric/musica/`
- organiza por **género** (nome da pasta)
- permite listar e tocar via API / conversa com a LLM

Não precisa de internet. Não descarrega músicas da cloud.

## Estrutura

```text
ric/musica/
  pop/  rock/  hiphop/  eletronica/  jazz/  blues/
  classica/  folk/  country/  reggae/  metal/  rb_soul/
  latina/  fado/  relaxamento/  infantil/  gospel/  soundtrack/
```

Cada pasta = um género. Os demos atuais estão em `classica/`, `folk/` e `relaxamento/`.

## Funções

| Função | Papel |
|---|---|
| `listar_generos()` | Pastas + quantidade de faixas |
| `listar_biblioteca()` / `listar_por_genero()` | Catálogo |
| `obter(id)` | Uma faixa pelo id |
| `escolher_para_tocar(titulo, genero)` | Escolhe faixa para o player |
| `garantir_pastas()` | Cria pastas base se faltarem |

## Relação com a BD

**Não é obrigatório criar outra base de dados** para as músicas.

- Lembretes → SQLite (`ric.db`) — precisam de estado/hora
- Músicas → ficheiros na pasta — a pasta é a “fonte da verdade”

## API / tools

- `GET /api/musica` — géneros + lista
- `GET /api/musica/{id}/stream` — áudio
- Tools LLM: `tocar_musica`, `pausar_musica`, `continuar_musica`
- A UI guarda a posição em `localStorage` (`ric_player_state`) para retomar depois

## Como adicionar músicas

1. Cria/usa uma pasta de género em `ric/musica/`
2. Copia o ficheiro de áudio para lá
3. Reinicia ou atualiza a UI — aparece na lista
