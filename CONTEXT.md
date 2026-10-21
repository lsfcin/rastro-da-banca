# rastro-da-banca
> Exemplo excelente do artefato tec da disciplina AI4Good: o exemplo oficial do faster-whisper, com entrada e saída trocadas para pedidos de feira.
> goal: none
> spec: none

Repositório didático, público. O guia que o usa é
[`academy/teaching/classes/ai4good/artefatos/3-tecnologia-base.md`](../../academy/teaching/classes/ai4good/artefatos/3-tecnologia-base.md),
e a folha que o descreve é `artefatos/tec/excelente.md`. A história dos commits é o conteúdo: o
primeiro é o exemplo oficial, intacto; o segundo é a alteração mínima. Não reescreva a história.

<!-- routing:start -->
## Routing

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`README.md`](README.md) | — | — | rastro da banca |
| [`requirements.txt`](requirements.txt) | — | — | requirements.txt — a única dependência do exemplo, na versão em que ele foi rodado. |
| [`transcrever.py`](transcrever.py) | [`transcrever.pyi`](transcrever.pyi) | `extrair_pedido` | transcrever.py — o exemplo oficial do faster-whisper (README do projeto, seção "Usage", licença MIT), com a entrada e a saída trocadas para a feira: entra o áudio de um pedido mandado à banca, sai o pedido (produto, quantidade, hora de buscar), tirado da transcrição por um modelo pequeno local (qwen3:4b no Ollama, licença Apache 2.0). |
<!-- routing:end -->
