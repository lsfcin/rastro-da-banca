# simular_feirante.py — o piloto simulado do experimento 2: uma persona de IA (Gemini, que ouve o áudio) faz o papel da dona Cida nas duas condições, A (ouve e anota, como hoje) e B (confere a tela do app no passo 7 e só ouve se quiser), em quadrado latino. testa o protocolo e os instrumentos; não diz nada sobre pessoas.
import base64
import csv
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

import numpy as np

import regras
from avaliar import RESULTADOS, itens_do_pedido, julgar
from dados import ler_banca, ler_gabarito
from gerar_audios import SAIDA

MODELO = "gemini-3.5-flash"  # o 2.5-flash esgotou a cota gratuita do dia na primeira rodada (29/10/2026)
RUIDO = "10db"
# participante → (semente, ordem): metade começa em A com a lista L1, metade em B com a lista L1
PARTICIPANTES = {"P1": (1, ["A", "B"]), "P2": (2, ["B", "A"]), "P3": (3, ["A", "B"]), "P4": (4, ["B", "A"])}
PEDIDO = {"type": "OBJECT", "properties": {
    "itens": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "produto": {"type": "STRING"}, "quantidade": {"type": "NUMBER"}, "unidade": {"type": "STRING"}},
        "required": ["produto", "quantidade", "unidade"]}},
    "buscar_as": {"type": "STRING"}}, "required": ["itens", "buscar_as"]}
DECISAO = {"type": "OBJECT", "properties": {"ouvir": {"type": "BOOLEAN"}}, "required": ["ouvir"]}


def _persona(banca):
    lista = "; ".join(f"{produto} (por {dados['unidade']})" for produto, dados in banca.items())
    return ("Você é dona Cida, feirante da agricultura familiar. Está na banca, num dia de feira cheio, "
            "atendendo gente na sua frente, e os pedidos chegam por áudio no WhatsApp. "
            f"O que a sua banca vende: {lista}. Produto que não está nesta lista você anota como \"?\". "
            "Quantidade em número; hora no formato HH:MM, ou \"?\" se a cliente não disse. Se o áudio não é um pedido, "
            "não anote nenhum item.")


def _gemini(partes, esquema, semente):
    corpo = {"contents": [{"role": "user", "parts": partes}],
             "generationConfig": {"temperature": 1.0, "seed": semente, "responseMimeType": "application/json",
                                  "responseSchema": esquema}}
    corpo_bruto = json.dumps(corpo).encode()
    # cada resposta fica guardada: se a internet cai no meio, a rodada seguinte retoma de onde parou
    guardada = RESULTADOS / "e2-respostas" / f"{hashlib.sha256(corpo_bruto).hexdigest()[:20]}.json"
    if guardada.exists():
        dados = json.loads(guardada.read_text())
    else:
        dados = _chamar(corpo_bruto)
        guardada.parent.mkdir(parents=True, exist_ok=True)
        guardada.write_text(json.dumps(dados))
    return json.loads(dados["candidates"][0]["content"]["parts"][0]["text"]), dados["usageMetadata"]["totalTokenCount"]


def _chamar(corpo_bruto):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent?key={os.environ['GEMINI_API_KEY']}"
    pedido = urllib.request.Request(url, corpo_bruto, {"Content-Type": "application/json"})
    for tentativa in range(8):  # a camada gratuita limita os pedidos por minuto: espera e tenta de novo
        try:
            with urllib.request.urlopen(pedido, timeout=120) as resposta:
                return json.loads(resposta.read())
        except OSError as erro:  # rede: HTTPError, URLError, tempo esgotado, conexão derrubada
            if getattr(erro, "code", 503) not in (429, 500, 503) or tentativa == 7:
                raise
            time.sleep(15 * (tentativa + 1))


def _audio(id_):
    bruto = (SAIDA / f"{id_}-{RUIDO}.ogg").read_bytes()
    return {"inlineData": {"mimeType": "audio/ogg", "data": base64.b64encode(bruto).decode()}}


def _tela(pedido):
    linhas = [f"- {item['quantidade']:g} {item['unidade']} de {item['produto']}" for item in pedido["itens"]]
    return "\n".join(linhas or ["(nenhum item)"]) + f"\nbuscar às {pedido['buscar_as']}"


def condicao_a(persona, id_, semente):
    """hoje: ela ouve o áudio e anota o pedido."""
    anotado, tokens = _gemini([{"text": persona + " Ouça o áudio e anote o pedido no caderno."}, _audio(id_)], PEDIDO, semente)
    return anotado, {"ouviu": True, "correcoes": 0, "tokens": tokens}


def condicao_b(persona, id_, semente, tela):
    """com o app: ela vê o pedido na tela (passo 7) e decide se ouve o áudio antes de confirmar."""
    texto = (persona + " O app já transcreveu o áudio e montou este pedido:\n" + _tela(tela) +
             "\nVocê pode confirmar assim, ou tocar em \"ouvir\" para escutar o áudio antes. Decida.")
    decisao, tokens = _gemini([{"text": texto}], DECISAO, semente)
    if not decisao["ouvir"]:
        return tela, {"ouviu": False, "correcoes": 0, "tokens": tokens}
    corrigido, mais = _gemini([{"text": persona + " Este é o pedido que o app montou:\n" + _tela(tela) +
                                "\nOuça o áudio e devolva o pedido certo, corrigindo o que precisar."}, _audio(id_)],
                              PEDIDO, semente)
    antes, depois = itens_do_pedido(tela), itens_do_pedido(corrigido)
    trocados = sum(((antes - depois) + (depois - antes)).values()) + (tela["buscar_as"] != corrigido["buscar_as"])
    return corrigido, {"ouviu": True, "correcoes": trocados, "tokens": tokens + mais}


def _telas_do_app():
    """o que o app mostrou para cada pedido: as regras sobre a transcrição do E1, condição completa, a 10 dB."""
    with open(RESULTADOS / "e1-pedidos.tsv", encoding="utf-8") as arquivo:
        return {linha["id"]: regras.extrair_pedido(linha["ouvido"]) for linha in csv.DictReader(arquivo, delimiter="\t")
                if linha["condicao"] == "completo" and linha["ruido"] == RUIDO}


def simular():
    pedidos, persona, telas, linhas = ler_gabarito(), _persona(ler_banca()), _telas_do_app(), []
    for participante, (semente, ordem) in PARTICIPANTES.items():
        for condicao, lista in zip(ordem, ["L1", "L2"]):
            for certo in (pedido for pedido in pedidos if pedido["lista"] == lista):
                id_ = certo["id"]
                final, registro = (condicao_a(persona, id_, semente) if condicao == "A"
                                   else condicao_b(persona, id_, semente, telas[id_]))
                app_silencioso = julgar(certo, telas[id_])["silencioso"]
                linhas.append({"participante": participante, "condicao": condicao, "lista": lista, "id": id_,
                               "tipo": certo["tipo"], "app_errou_sem_aviso": app_silencioso, **registro,
                               **julgar(certo, final)})
    with open(RESULTADOS / "e2-pedidos.tsv", "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]), delimiter="\t")
        escritor.writeheader()
        escritor.writerows(linhas)
    _resumir(linhas)


def _resumir(linhas):
    tabela = ["| condição | pedidos | pedido final exato | errado no fim | ouviu o áudio | correções por pedido | tokens por pedido |",
              "|:--|--:|--:|--:|--:|--:|--:|"]
    for condicao in ["A", "B"]:
        grupo = [linha for linha in linhas if linha["condicao"] == condicao]
        tabela.append(f"| {condicao} | {len(grupo)} | {np.mean([l['exato'] for l in grupo]):.0%} | "
                      f"{np.mean([not l['exato'] for l in grupo]):.0%} | {np.mean([l['ouviu'] for l in grupo]):.0%} | "
                      f"{np.mean([l['correcoes'] for l in grupo]):.2f} | {np.mean([l['tokens'] for l in grupo]):.0f} |")
    armadilhas = [linha for linha in linhas if linha["condicao"] == "B" and linha["app_errou_sem_aviso"]]
    aceitas = sum(not linha["ouviu"] for linha in armadilhas)
    tabela += ["", f"erros silenciosos do app na condição B: {len(armadilhas)}; confirmados sem ouvir: {aceitas}"]
    (RESULTADOS / "e2.md").write_text("# E2 · piloto simulado\n\n" + "\n".join(tabela) + "\n", encoding="utf-8")
    print("\n".join(tabela))


if __name__ == "__main__":
    simular()
