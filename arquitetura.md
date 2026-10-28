# rastro da banca · fluxograma e arquitetura

O caminho de um pedido, do áudio da cliente até a confirmação que volta para ela. Exemplo do
artefato **fluxograma e arquitetura** da disciplina AI4Good
([guia](https://lucassf.pages.dev/ai4good/flx)).

Formas: **pessoa** `([ ])` · **IA** `{{ }}` · **regra** `[ ]`.

```mermaid
flowchart TD
    A(["1 · cliente grava o pedido em áudio no WhatsApp da banca"])
    B(["2 · feirante compartilha o áudio com o app"])
    C{{"3 · transcrever o áudio, com a lista da banca como contexto (whisper)"}}
    D["4 · achar cada produto na lista da banca; fora da lista vira '?'"]
    E["5 · quantidade e unidade: tabela de palavras ('uma dúzia' = 12, 'meio quilo' = 0,5 kg)"]
    F["6 · hora de buscar: tabela de expressões ('lá pelas dez e meia' = 10:30)"]
    G(["7 · feirante ouve o áudio, confere o pedido na tela e corrige o '?'"])
    H["8 · conta: preço da banca × quantidade"]
    I(["9 · feirante compartilha a confirmação de volta no WhatsApp"])
    J(["10 · cliente recebe o pedido, o total e a hora"])
    K["11 · no dia da feira: lista de separação, ordenada pela hora de buscar"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J
    H --> K
```
