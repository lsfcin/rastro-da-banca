# rastro-da-banca
> Exemplo excelente dos artefatos tec, flx e exp da disciplina AI4Good: o exemplo oficial do faster-whisper, com entrada e saída trocadas para pedidos de feira, o fluxograma do pedido e os pilotos dos dois experimentos.
> goal: none
> spec: none

Repositório didático, público. O guia que o usa é
[`academy/teaching/classes/ai4good/artefatos/3-tecnologia-base.md`](../../academy/teaching/classes/ai4good/artefatos/3-tecnologia-base.md),
e a folha que o descreve é `artefatos/tec/excelente.md`. A história dos commits é o conteúdo: o
primeiro é o exemplo oficial, intacto; o segundo é a alteração mínima; o terceiro e o quarto são o
fluxograma e a arquitetura (`arquitetura.md`, folha `artefatos/flx/excelente.md`); depois vêm o pré-registro
(`experimentos.md`) e os pilotos (folha `artefatos/exp/excelente.md`). Não reescreva a história.

<!-- routing:start -->
## Routing

| Subdirectory | Description |
|--------------|-------------|
| [`resultados/`](resultados/CONTEXT.md) | As tabelas que os pilotos imprimem (e1.md, e2.md), cada pedido de cada condição (e1-pedidos.tsv, e2-pedidos.tsv) e as respostas guardadas do DeepSeek (respostas.tsv), que deixam os dois rodarem de novo sem a API. |

| File | Interface | API | Description |
|------|-----------|-----|-------------|
| [`README.md`](README.md) | — | — | rastro da banca |
| [`arquitetura.md`](arquitetura.md) | — | — | rastro da banca · fluxograma e arquitetura |
| [`avaliar.py`](avaliar.py) | [`avaliar.pyi`](avaliar.pyi) | `wer`, `itens_do_pedido`, `julgar`, `avaliar` | avaliar.py — o experimento 1 (bancada técnica): roda cada condição sobre os áudios do piloto e mede pedido exato, erro sinalizado ("?") e erro silencioso, acerto por item, WER e tempo, com intervalo de 95% por bootstrap. |
| [`dados.py`](dados.py) | [`dados.pyi`](dados.pyi) | `ler_banca`, `ler_itens`, `ler_gabarito` | dados.py — lê a lista da banca e o gabarito dos pedidos, as duas tabelas que os experimentos usam. |
| [`experimentos.md`](experimentos.md) | — | — | rastro da banca · desenho dos experimentos |
| [`gerar_audios.py`](gerar_audios.py) | [`gerar_audios.pyi`](gerar_audios.pyi) | `voz_do_pedido`, `gerar` | gerar_audios.py — os áudios do piloto: cada fala do gabarito em voz sintética (Piper, 4 vozes pt_BR), com o burburinho de outras falas por baixo, em três níveis de ruído; saem em .ogg (opus), como o WhatsApp manda. |
| [`medir_no_celular.py`](medir_no_celular.py) | [`medir_no_celular.pyi`](medir_no_celular.pyi) | `medir` | medir_no_celular.py — a medida que o tec e o flx deixaram em aberto: o whisper rodando no celular, pelo whisper.cpp, sobre os 30 áudios do E1 a 10 dB, com as mesmas regras e o mesmo julgamento do avaliar.py; mede pedido exato, erro sem aviso, tempo / áudio, carga do modelo e memória. |
| [`nuvem.py`](nuvem.py) | [`nuvem.pyi`](nuvem.pyi) | `instrucoes`, `responder` | nuvem.py — um modelo de linguagem na nuvem (DeepSeek V4.1 Flash, pelo OpenRouter) respondendo num formato json fixo: a persona do E2 e o pipeline alternativo do E1. cada resposta fica guardada, e a rodada seguinte não chama a rede. |
| [`regras.py`](regras.py) | [`regras.pyi`](regras.pyi) | `normalizar`, `hora_de_buscar`, `nos_nomes_da_banca`, `extrair_pedido` | regras.py — os passos 4 a 6 do fluxograma, sem IA: acha cada produto na lista da banca (fora dela vira "?"), a quantidade e a unidade por uma tabela de palavras, e a hora de buscar por uma tabela de expressões. |
| [`requirements.txt`](requirements.txt) | — | — | requirements.txt — a única dependência do exemplo, na versão em que ele foi rodado. |
| [`simular_feirante.py`](simular_feirante.py) | [`simular_feirante.pyi`](simular_feirante.pyi) | `condicao_a`, `condicao_b`, `simular` | simular_feirante.py — o piloto simulado do experimento 2: uma persona de IA (DeepSeek V4.1 Flash, pelo OpenRouter) faz o papel da dona Cida nas duas condições, A (ouve e anota, como hoje) e B (confere a tela do app no passo 7 e só ouve se quiser), em 4 execuções simuladas, uma por sequência de ordem e lista. o ouvido dela é o whisper large-v3-turbo; na… |
| [`transcrever.py`](transcrever.py) | [`transcrever.pyi`](transcrever.pyi) | `carregar_modelo`, `extrair_pedido`, `transcrever` | transcrever.py — o exemplo oficial do faster-whisper (README do projeto, seção "Usage", licença MIT), com a entrada e a saída trocadas para a feira: entra o áudio de um pedido mandado à banca, sai o pedido (produto, quantidade, hora de buscar), tirado da transcrição pelas regras de regras.py. o modelo pequeno local (qwen3:4b no Ollama, licença Apache 2.0)… |
<!-- routing:end -->
