# rastro da banca · desenho dos experimentos

O pré-registro dos dois experimentos: hipótese, linha de base, o número que derruba, métricas,
ablações, dados e ética, escritos antes de ver o resultado. Exemplo do artefato **desenho dos
experimentos** da disciplina AI4Good ([guia](https://lucassf.pages.dev/ai4good/exp)).

## E1 · a técnica: o pedido sai certo do áudio?

- **molde:** SLURP (Bastianelli et al., [EMNLP 2020](https://doi.org/10.18653/v1/2020.emnlp-main.588)):
  medir a tarefa, não só as palavras.
- **hipótese:** com o áudio de uma feira (10 dB de relação sinal-ruído), no máximo 1 em cada 10
  pedidos sai errado **sem aviso** ("?"), e a transcrição leva menos tempo que o próprio áudio.
- **linha de base, sem IA:** a regra sozinha sobre o texto que a cliente falou (o gabarito): o teto
  das regras, sem o erro da transcrição.
- **derruba se:** errado sem aviso acima de 10% a 10 dB, ou tempo / áudio acima de 1, com 30 pedidos.
- **métricas:** pedido exato; errado com "?" (sinalizado); errado sem aviso (silencioso); F1 dos
  itens; WER, com números e unidades normalizados ("2 kg" = "dois quilos"); tempo / áudio; intervalo
  de 95% por bootstrap sobre os pedidos.
- **ablações:** sem a lista da banca como contexto; whisper `tiny` e `base`; qwen3:4b no lugar das
  regras, com a saída traduzida para os nomes da banca; três níveis de ruído (limpo, 10 dB, 0 dB).

## E2 · quem usa: a feirante erra menos com o app do que hoje?

- **molde:** Patel et al., fala × teclado ([CHI 2009](https://doi.org/10.1145/1518701.1518709)):
  intra-sujeitos, tarefa cronometrada, com quem vai usar.
- **hipótese:** conferindo a tela do app (passo 7), a feirante termina com menos pedidos errados que
  ouvindo e anotando, e corrige no máximo 1 em cada 3 pedidos.
- **linha de base, sem IA:** a prática de hoje: ouvir o áudio e anotar no caderno.
- **derruba se:** pedidos errados no fim, com o app, iguais ou acima dos sem o app; ou mais de 1
  correção a cada 3 pedidos.
- **desenho:** cada feirante faz as duas condições, A (hoje) e B (app), com duas listas de 15
  pedidos equivalentes (L1, L2), em quadrado latino: metade começa por A, metade por B, e ninguém
  ouve o mesmo áudio duas vezes.
- **métricas:** pedido final exato e errado; correções por pedido; vezes que tocou "ouvir"; erros
  silenciosos do app confirmados sem ouvir (viés de automação); tempo por pedido; carga de trabalho
  (NASA-TLX reduzido, oral); entrevista curta. Comportamento vale mais que preferência
  (Dell et al., [CHI 2012](https://doi.org/10.1145/2207676.2208638)).

## dados e participantes

| | E1 | E2 |
|:--|:--|:--|
| quem | 10 falantes da região, clientes de feira, que leem um cartão com os itens e falam do seu jeito | 6 a 8 feirantes da agricultura familiar |
| quantos, e por quê | 10 pedidos cada, 100 no total: o intervalo de 95% de uma taxa de 10% fica em ±6 pontos | o tamanho comum de estudos intra-sujeitos na CHI (Caine, [CHI 2016](https://doi.org/10.1145/2858036.2858498)); o efeito é medido por pessoa |
| coleta | áudio pelo WhatsApp, gravado na feira (ruído real) | numa feira, com os áudios do E1, cronometrado no app |
| gabarito | duas pessoas anotam cada pedido; a concordância (κ) é reportada | o mesmo do E1 |
| ajuste × teste | 3 falantes para ajustar as regras, 7 para o teste; o teste não é olhado antes | — |
| consentimento | TCLE lido em voz alta e aceito em áudio (Res. CNS 510/2016) | o mesmo, e a pessoa pode parar quando quiser |
| comitê de ética | projeto ao CEP da UFRPE pela Plataforma Brasil (Res. 466/2012, 510/2016, Lei 14.874/2024) | o mesmo projeto |
| dados pessoais | os áudios ficam no notebook da pesquisa até o gabarito e são apagados; o gabarito não tem nome (LGPD) | só o número do participante; nada de voz da feirante é gravado |

## o piloto do semestre, sem pessoas de fora

O E1 roda com voz sintética (Piper, 4 vozes) e burburinho de outras falas; o E2, com uma persona
de IA no papel da feirante. Os dois testam o desenho e os scripts. **Nenhum dos dois diz nada
sobre pessoas** (Agnew et al., [CHI 2024](https://doi.org/10.1145/3613904.3642703)).

```bash
python gerar_audios.py <piper> <pasta das vozes> <pasta de rascunho>   # os 90 áudios do piloto
python avaliar.py                                                       # E1 → resultados/e1.md
python simular_feirante.py                                              # E2 → resultados/e2.md (GEMINI_API_KEY)
```

## emendas, depois do piloto (30/10/2026)

O pré-registro acima fica como foi escrito. O que um revisor externo achou nele, e o que muda:

1. **o molde do E2 não é intra-sujeitos:** Patel et al. (CHI 2009) compararam fala e teclado com 45
   agricultores divididos entre as condições. o E2 continua intra-sujeitos, por outro motivo: com
   poucas feirantes, cada uma comparada com ela mesma.
2. **"6 a 8 é o tamanho comum" não está em Caine (CHI 2016):** ele mostra que o tamanho varia com o
   método. com 8, o E2 mostra a direção e o tamanho da diferença por pessoa, não uma taxa.
3. **a margem do E1 é ±7, não ±6:** com 3 falantes no ajuste, o teste tem 70 pedidos.
4. **os áudios ficam até o fim do E2,** que os reusa, e não só até o gabarito.
5. **o limiar não muda.**

## emendas, depois do piloto do E1 e antes do E2 (30/10/2026)

Quando estas entraram, a tabela do E1 já era conhecida (20% de erro sem aviso a 10 dB). As comparações
novas são exploratórias, e um segundo revisor externo leu o desenho antes de rodar.

6. **o E2 trocou de persona:** o Gemini, que ouvia o áudio, saiu por cota. agora o ouvido dela é o
   whisper large-v3-turbo, e ela é o DeepSeek V4.1 Flash, que lê o que o turbo ouviu
   (`OPENROUTER_API_KEY` no lugar de `GEMINI_API_KEY`). os erros do ouvido dela tendem a coincidir
   com os do app; uma rodada com a fala certa no lugar do turbo dá o teto do que o "ouvir" corrige.
7. **4 execuções simuladas, não participantes:** as 4 combinações de ordem e lista. uma semente não
   faz uma pessoa.
8. **a correção que o limiar conta:** pedidos corrigidos (houve alguma mudança); as trocas contam à parte.
9. **duas linhas de base:** o jeito de hoje e o competidor mais forte. no E1, um pipeline alternativo
   maior, na nuvem (turbo + DeepSeek), nos mesmos pedidos e com o mesmo julgamento; ele não representa
   o Anota AI nem o agente da Meta. no E2, esses competidores não rodam no piloto, porque o fluxo deles
   pede pessoas; entra a ablação "sem conferência".
10. **duas falhas de métrica, para o experimento real:** um "?" faz o pedido inteiro contar como
    avisado, mesmo com outro campo errado calado; e repetir o "?" de um produto fora da lista conta
    como exato. o experimento real mede erro e aviso por campo (produto, quantidade, hora). os 20%
    ficam como estão.
11. **o que a auditoria cega da folha achou:** o DOI de Dell et al. acima aponta para outro artigo;
    o certo é [10.1145/2207676.2208589](https://doi.org/10.1145/2207676.2208589). o TCLE abaixo diz
    que a voz fica guardada só até o gabarito; pela emenda 4, ela fica até o fim do E2, e o TCLE do
    experimento real diz isso. a linha de base do E1 passa a sair do `avaliar.py`.

## termo de consentimento (lido em voz alta)

> Esta é uma pesquisa da UFRPE sobre um aplicativo que transforma áudio de pedido em lista. Você
> vai [E1: ler um pedido de feira em voz alta, do seu jeito] [E2: conferir pedidos, com e sem o
> aplicativo]. Leva uns 20 minutos. Não tem risco além do cansaço, e você pode parar quando quiser,
> sem explicar. Sua voz fica guardada só até a gente escrever o que foi dito, e depois é apagada.
> Seu nome não aparece em lugar nenhum. Se tiver dúvida, fale com [pesquisador, telefone] ou com o
> comitê de ética da UFRPE. Você aceita participar? Pode responder "aceito" nesta gravação.
