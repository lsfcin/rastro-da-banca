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

| File | Interface | Description |
|------|-----------|-------------|
| [`README.md`](README.md) | — | rastro da banca |
| [`requirements.txt`](requirements.txt) | — | requirements.txt — a única dependência do exemplo, na versão em que ele foi rodado. |
| [`transcrever.py`](transcrever.py) | [`transcrever.pyi`](transcrever.pyi) | transcrever.py — o exemplo oficial do faster-whisper, copiado do README do projeto (https://github.com/SYSTRAN/faster-whisper, seção "Usage", licença MIT). Duas escolhas, ambas previstas no próprio README: a linha do CPU (a maioria das máquinas não tem GPU) e o modelo "small" (cerca de 500 MB, roda num notebook comum). O audio.mp3 é o jfk.flac dos testes do… |
<!-- routing:end -->
