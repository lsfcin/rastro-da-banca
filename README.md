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

Os dois commits seguintes são do artefato **fluxograma e arquitetura**
([guia](https://lucassf.pages.dev/ai4good/flx)): [`arquitetura.md`](arquitetura.md) desenha o
caminho do pedido, passo a passo, e diz onde roda cada peça e para onde vai cada dado pessoal.

Os commits depois deles são do artefato **desenho dos experimentos**
([guia](https://lucassf.pages.dev/ai4good/exp)): primeiro o pré-registro,
[`experimentos.md`](experimentos.md), com as hipóteses e o número que derruba cada uma; depois as
regras que substituem o qwen (`regras.py`) e os dois pilotos, com as tabelas em [`resultados/`](resultados/).

## como rodar

```bash
pip install -r requirements.txt
python transcrever.py audios/pedido-*.ogg
python avaliar.py                       # piloto do E1; mede só as condições que faltam em resultados/e1-pedidos.tsv
python simular_feirante.py              # piloto do E2; pede OPENROUTER_API_KEY, ou usa as respostas guardadas
```

Na primeira vez o whisper é baixado (cerca de 0,5 GB; com o qwen, 3 GB). Roda em CPU, sem GPU.
Para rodar o commit 1 (o exemplo oficial): `git checkout 89a3ba4 && python transcrever.py`.

## de onde vem cada coisa

| peça | o que faz aqui | origem | licença |
|:--|:--|:--|:--|
| faster-whisper | **técnica central**: transforma o áudio em texto | [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | MIT |
| regras (`regras.py`, `banca.tsv`) | tiram produto, quantidade e hora do texto, sem IA | escritas aqui | MIT |
| qwen3:4b, no Ollama | só na ablação do E1: o que as regras substituíram | [Qwen3](https://huggingface.co/Qwen/Qwen3-4B), [Ollama](https://github.com/ollama/ollama) | Apache 2.0 · MIT |
| `audio.mp3` | o áudio de teste do exemplo oficial | `tests/data/jfk.flac` do faster-whisper, convertido | MIT |
| `audios/pedido-*.ogg` | três pedidos de feira, com ruído de fundo | voz sintética [Piper](https://github.com/rhasspy/piper), `pt_BR-faber-medium` | CC0 |
| `audios/e1/*.ogg` | os 30 pedidos do gabarito, em 3 níveis de ruído (`gerar_audios.py`) | Piper, vozes `pt_BR` faber, cadu, jeff e edresson | CC0 |
| whisper `large-v3-turbo` | o ouvido da persona do E2 e o pipeline alternativo do E1 | [mobiuslabsgmbh/faster-whisper-large-v3-turbo](https://huggingface.co/mobiuslabsgmbh/faster-whisper-large-v3-turbo) | MIT |
| DeepSeek V4.1 Flash (`nuvem.py`) | a persona do E2, que lê o que o turbo ouviu, e o pipeline alternativo do E1 | [OpenRouter](https://openrouter.ai/deepseek/deepseek-v4.1-flash) | termos da API |
