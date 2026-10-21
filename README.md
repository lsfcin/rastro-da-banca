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
python transcrever.py
```

Na primeira vez o modelo é baixado (cerca de 500 MB). Roda em CPU, sem GPU.

## de onde vem cada coisa

| peça | origem | licença |
|:--|:--|:--|
| faster-whisper | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT |
| `audio.mp3` | `tests/data/jfk.flac` do faster-whisper, convertido | MIT |
