# rastro da banca · fluxograma e arquitetura

O caminho de um pedido, do áudio da cliente até a confirmação que volta para ela. Exemplo do
artefato **fluxograma e arquitetura** da disciplina AI4Good
([guia](https://lucassf.pages.dev/ai4good/flx)).

Formas: **pessoa** `([ ])` · **IA** `{{ }}` · **regra** `[ ]`. Caixas: onde cada peça roda.

```mermaid
flowchart TD
    subgraph CEL_C["celular da cliente"]
        A(["1 · cliente grava o pedido em áudio no WhatsApp da banca"])
        J(["10 · cliente recebe o pedido, o total e a hora"])
    end

    subgraph CEL_F["celular do feirante: tudo roda aqui, sem internet"]
        B(["2 · feirante compartilha o áudio com o app"])
        C{{"3 · transcrever o áudio, com a lista da banca como contexto (whisper)"}}
        D["4 · achar cada produto na lista da banca; fora da lista vira '?'"]
        E["5 · quantidade e unidade: tabela de palavras ('uma dúzia' = 12, 'meio quilo' = 0,5 kg)"]
        F["6 · hora de buscar: tabela de expressões ('lá pelas dez e meia' = 10:30)"]
        G(["7 · a tela abre no '?' e toca o áudio; o feirante confere, corrige e escreve o primeiro nome de quem pediu"])
        H["8 · conta: preço da banca × quantidade"]
        I(["9 · feirante compartilha a confirmação de volta no WhatsApp"])
        K["11 · no dia da feira: lista de separação, ordenada pela hora de buscar"]
        DB[("pedidos do dia: primeiro nome, produtos, hora")]
    end

    A -- "áudio, pelo WhatsApp" --> B
    B --> C --> D --> E --> F --> G --> H --> I
    I -- "texto, pelo WhatsApp" --> J
    H --> DB --> K
```

## os dados

| dado pessoal | de quem é | onde fica | quem vê | por quanto tempo |
|:--|:--|:--|:--|:--|
| áudio do pedido (a voz) | cliente | cópia no app, no celular do feirante | feirante | até o pedido ser confirmado; o app apaga a cópia |
| texto transcrito | cliente | memória do app | ninguém além do app | some com o áudio |
| primeiro nome e pedido | cliente | pedidos do dia, no celular do feirante | feirante | até o fim da feira; fica só o total vendido, sem nome |
| registro de correções (sem áudio nem nome) | da banca | celular do feirante | feirante, e a pesquisa se ele aceitar | até o fim do experimento |

Nada sai do celular do feirante além da confirmação, pelo WhatsApp que a banca já usa. O app não
guarda telefone: a conversa já está no WhatsApp.
