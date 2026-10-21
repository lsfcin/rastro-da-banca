# rastro da banca

Exemplo do artefato **tecnologia base** da disciplina AI4Good
([guia](https://lucassf.pages.dev/ai4good/artefatos/3-tecnologia-base)). Mostra o caminho que o
aluno faz: rodar o exemplo oficial de uma técnica a partir do código-fonte, na própria máquina, e
depois mudar só a entrada e a saída para o problema dele.

## os dois commits

1. **o exemplo oficial**: o trecho "Usage" do README do
   [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (licença MIT), com o áudio de teste
   do próprio projeto. Duas escolhas, previstas no README dele: CPU e o modelo `small`.
2. **a alteração mínima**: entra o áudio de um pedido mandado à banca da feira; sai o pedido
   (produto, quantidade, hora de buscar).

Para ver só o que mudou: o diff do segundo commit.

## como rodar

```bash
pip install -r requirements.txt
ollama pull qwen3:4b                    # o modelo pequeno que tira o pedido do texto
python transcrever.py audios/pedido-*.ogg
```

Na primeira vez os modelos são baixados (cerca de 3 GB, os dois). Roda em CPU, sem GPU.
Para rodar o commit 1 (o exemplo oficial): `git checkout HEAD~1 && python transcrever.py`.

## de onde vem cada coisa

| peça | o que faz aqui | origem | licença |
|:--|:--|:--|:--|
| faster-whisper | **técnica central**: transforma o áudio em texto | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT |
| qwen3:4b, no Ollama | apoio: tira produto, quantidade e hora do texto | [Qwen3](https://huggingface.co/Qwen/Qwen3-4B), [Ollama](https://github.com/ollama/ollama) | Apache 2.0 · MIT |
| `audio.mp3` | o áudio de teste do exemplo oficial | `tests/data/jfk.flac` do faster-whisper, convertido | MIT |
| `audios/pedido-*.ogg` | três pedidos de feira, com ruído de fundo | voz sintética [Piper](https://github.com/rhasspy/piper), `pt_BR-faber-medium` | CC0 |
