# simular_feirante.py — o piloto simulado do experimento 2: uma persona de IA (DeepSeek V4.1 Flash, pelo OpenRouter) faz o papel da dona Cida nas duas condições, A (ouve e anota, como hoje) e B (confere a tela do app no passo 7 e só ouve se quiser), em 4 execuções simuladas, uma por sequência de ordem e lista. o ouvido dela é o whisper large-v3-turbo; na sensibilidade, a fala certa. testa o protocolo e os instrumentos; não diz nada sobre pessoas.
import csv

import numpy as np

import nuvem
import regras
import transcrever
from avaliar import RESULTADOS, itens_do_pedido, julgar
from dados import ler_banca, ler_gabarito

RUIDO = "10db"
OUVIDO = "pipeline alternativo: turbo + DeepSeek"  # a condição do E1 de onde vem a transcrição do turbo
# execução → (semente, [(condição, lista), (condição, lista)]): as 4 combinações de ordem e lista
EXECUCOES = {"S1": (1, [("A", "L1"), ("B", "L2")]), "S2": (2, [("B", "L1"), ("A", "L2")]),
             "S3": (3, [("A", "L2"), ("B", "L1")]), "S4": (4, [("B", "L2"), ("A", "L1")])}


def _persona(banca):
    return ("Você é dona Cida, feirante da agricultura familiar. Está na banca, num dia de feira cheio, "
            "atendendo gente na sua frente, e os pedidos chegam por áudio no WhatsApp. " + nuvem.instrucoes(banca))


def _ouvido(texto):
    return "O que você ouve no áudio: \"" + (texto.strip() or "(nenhuma fala, só barulho)") + "\""


def _tela(pedido):
    linhas = [f"- {item['quantidade']:g} {item['unidade']} de {item['produto']}" for item in pedido["itens"]]
    return "\n".join(linhas or ["(nenhum item)"]) + f"\nbuscar às {pedido['buscar_as']}"


def condicao_a(persona, ouvido, semente):
    """hoje: ela ouve o áudio e anota o pedido."""
    anotado, tokens = nuvem.responder(persona + " Anote o pedido no caderno.\n" + _ouvido(ouvido), transcrever.PEDIDO, semente)
    return regras.nos_nomes_da_banca(anotado), {"ouviu": True, "corrigiu": False, "trocas": 0, "tokens": tokens}


def condicao_b(persona, ouvido, semente, tela):
    """com o app: ela vê o pedido na tela (passo 7) e decide se ouve o áudio antes de confirmar."""
    texto = (persona + " O app já transcreveu o áudio e montou este pedido:\n" + _tela(tela) +
             "\nVocê pode confirmar assim, ou tocar em \"ouvir\" para escutar o áudio antes. Decida.")
    decisao, tokens = nuvem.responder(texto, nuvem.DECISAO, semente)
    if not decisao["ouvir"]:
        return tela, {"ouviu": False, "corrigiu": False, "trocas": 0, "tokens": tokens}
    corrigido, mais = nuvem.responder(persona + " Este é o pedido que o app montou:\n" + _tela(tela) +
                                      "\nDevolva o pedido certo, corrigindo o que precisar.\n" + _ouvido(ouvido),
                                      transcrever.PEDIDO, semente)
    corrigido = regras.nos_nomes_da_banca(corrigido)
    antes, depois = itens_do_pedido(tela), itens_do_pedido(corrigido)
    trocas = sum(((antes - depois) + (depois - antes)).values()) + (tela["buscar_as"] != corrigido["buscar_as"])
    return corrigido, {"ouviu": True, "corrigiu": trocas > 0, "trocas": trocas, "tokens": tokens + mais}


def _do_e1(condicao):
    """id → o que o whisper daquela condição do E1 ouviu, a 10 dB."""
    with open(RESULTADOS / "e1-pedidos.tsv", encoding="utf-8") as arquivo:
        return {linha["id"]: linha["ouvido"] for linha in csv.DictReader(arquivo, delimiter="\t")
                if linha["condicao"] == condicao and linha["ruido"] == RUIDO}


def simular():
    pedidos, persona = ler_gabarito(), _persona(ler_banca())
    # o que o app mostrou: as regras sobre a transcrição do E1, condição completa
    telas = {id_: regras.extrair_pedido(texto) for id_, texto in _do_e1("completo").items()}
    ouvidos = {"turbo": _do_e1(OUVIDO), "fala certa": {pedido["id"]: pedido["fala"] for pedido in pedidos}}
    linhas = []
    for ouvido, ouviu in ouvidos.items():
        for execucao, (semente, sequencia) in EXECUCOES.items():
            for condicao, lista in sequencia:
                for certo in (pedido for pedido in pedidos if pedido["lista"] == lista):
                    id_ = certo["id"]
                    final, registro = (condicao_a(persona, ouviu[id_], semente) if condicao == "A"
                                       else condicao_b(persona, ouviu[id_], semente, telas[id_]))
                    linhas.append({"ouvido": ouvido, "execucao": execucao, "condicao": condicao, "lista": lista,
                                   "id": id_, "tipo": certo["tipo"], "app_errou_sem_aviso": julgar(certo, telas[id_])["silencioso"],
                                   **registro, **julgar(certo, final)})
    # ablação: ninguém confere, o pedido final é a tela; uma vez por pedido, sem persona
    linhas += [{"ouvido": "—", "execucao": "—", "condicao": "sem conferência", "lista": certo["lista"], "id": certo["id"],
                "tipo": certo["tipo"], "app_errou_sem_aviso": julgar(certo, telas[certo["id"]])["silencioso"],
                "ouviu": False, "corrigiu": False, "trocas": 0, "tokens": 0, **julgar(certo, telas[certo["id"]])}
               for certo in pedidos]
    with open(RESULTADOS / "e2-pedidos.tsv", "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]), delimiter="\t")
        escritor.writeheader()
        escritor.writerows(linhas)
    _resumir(linhas)


def _resumir(linhas):
    tabela = ["| ouvido da persona | condição | pedidos | pedido final exato | errado no fim | ouviu o áudio | "
              "pedidos corrigidos | trocas por pedido | tokens por pedido |", "|:--|:--|" + "--:|" * 7]
    for ouvido, condicao in [("turbo", "A"), ("turbo", "B"), ("fala certa", "A"), ("fala certa", "B"), ("—", "sem conferência")]:
        grupo = [linha for linha in linhas if linha["ouvido"] == ouvido and linha["condicao"] == condicao]
        tabela.append(f"| {ouvido} | {condicao} | {len(grupo)} | {np.mean([l['exato'] for l in grupo]):.0%} | "
                      f"{np.mean([not l['exato'] for l in grupo]):.0%} | {np.mean([l['ouviu'] for l in grupo]):.0%} | "
                      f"{np.mean([l['corrigiu'] for l in grupo]):.0%} | {np.mean([l['trocas'] for l in grupo]):.2f} | "
                      f"{np.mean([l['tokens'] for l in grupo]):.0f} |")
    tabela.append("")
    for ouvido in ["turbo", "fala certa"]:
        armadilhas = [l for l in linhas if l["ouvido"] == ouvido and l["condicao"] == "B" and l["app_errou_sem_aviso"]]
        tabela.append(f"ouvido {ouvido}: erros sem aviso do app na condição B: {len(armadilhas)}; "
                      f"confirmados sem ouvir: {sum(not l['ouviu'] for l in armadilhas)}; "
                      f"errados no fim: {sum(not l['exato'] for l in armadilhas)}")
    (RESULTADOS / "e2.md").write_text("# E2 · piloto simulado\n\n" + "\n".join(tabela) + "\n", encoding="utf-8")
    print("\n".join(tabela))


if __name__ == "__main__":
    simular()
