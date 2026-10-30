# avaliar.py — o experimento 1 (bancada técnica): roda cada condição sobre os áudios do piloto e mede pedido exato, erro sinalizado ("?") e erro silencioso, acerto por item, WER e tempo, com intervalo de 95% por bootstrap.
import csv
import re
import time
from collections import Counter

import numpy as np
from faster_whisper import decode_audio

import nuvem
import regras
import transcrever
from dados import PASTA, ler_banca, ler_gabarito
from gerar_audios import RUIDOS, SAIDA, TAXA, voz_do_pedido

# condição → (modelo do whisper, com a lista da banca como contexto?, quem tira o pedido do texto)
CONDICOES = {
    "completo": ("small", True, "regras"),
    "sem a lista como contexto": ("small", False, "regras"),
    "whisper tiny": ("tiny", True, "regras"),
    "whisper base": ("base", True, "regras"),
    "qwen3:4b no lugar das regras": ("small", True, "qwen"),
    # depois do pré-registro (emenda de 30/10): outro caminho com IA, maior e na nuvem, nos mesmos pedidos e critérios
    "pipeline alternativo: turbo + DeepSeek": ("large-v3-turbo", True, "nuvem"),
}
RESULTADOS = PASTA / "resultados"
DIGITOS = {str(numero): palavra for palavra, numero in regras.NUMEROS.items() if palavra not in ("uma", "duas", "meio", "meia")}


def _palavras(texto):
    """normaliza para o WER: '2 kg' e 'dois quilos' contam igual."""
    trocas = {**DIGITOS, "kg": "quilos", "pra": "para"}
    return [trocas.get(palavra, palavra) for palavra in regras.normalizar(re.sub(r"(\d)h", r"\1 ", texto)).split()]


def wer(referencia, hipotese):
    ref, hip = _palavras(referencia), _palavras(hipotese)
    distancia = list(range(len(hip) + 1))
    for i, palavra_ref in enumerate(ref, 1):
        anterior, distancia[0] = distancia[0], i
        for j, palavra_hip in enumerate(hip, 1):
            anterior, distancia[j] = distancia[j], min(distancia[j] + 1, distancia[j - 1] + 1,
                                                       anterior + (palavra_ref != palavra_hip))
    return distancia[-1] / max(1, len(ref))


def itens_do_pedido(pedido):
    return Counter((item["produto"], float(item["quantidade"]), item["unidade"]) for item in pedido["itens"])


def julgar(certo, saida):
    """um pedido → exato, sinalizado (pede conferência com '?') ou silencioso (errado e sem aviso)."""
    acertos = sum((itens_do_pedido(certo) & itens_do_pedido(saida)).values())
    if not certo["itens"]:
        exato = not saida["itens"]
    else:
        exato = itens_do_pedido(certo) == itens_do_pedido(saida) and saida["buscar_as"] == certo["hora"]
    avisou = saida["buscar_as"] == "?" and bool(saida["itens"]) or any(item["produto"] == "?" for item in saida["itens"])
    errado_com_aviso = not exato and avisou
    return {"exato": exato, "sinalizado": errado_com_aviso, "silencioso": not exato and not errado_com_aviso,
            "acertos": acertos, "itens_certos": len(certo["itens"]), "itens_saida": len(saida["itens"])}


def _transcricoes(pedidos, tamanho, com_contexto):
    """(id, ruído) → (texto, tempo / áudio), e a carga do modelo, carregado uma vez."""
    inicio = time.perf_counter()
    modelo = transcrever.carregar_modelo(tamanho)
    carga = time.perf_counter() - inicio
    saida = {}
    for pedido in pedidos:
        for ruido in RUIDOS:
            audio = str(SAIDA / f"{pedido['id']}-{ruido}.ogg")
            inicio = time.perf_counter()
            texto = transcrever.transcrever(modelo, audio, transcrever.CONTEXTO if com_contexto else None)
            saida[pedido["id"], ruido] = (texto, (time.perf_counter() - inicio) / (len(decode_audio(audio)) / TAXA))
    return saida, carga


def _ler_tsv(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo, delimiter="\t"))


def _escrever_tsv(caminho, linhas):
    caminho.parent.mkdir(exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=list(linhas[0]), delimiter="\t")
        escritor.writeheader()
        escritor.writerows(linhas)


def _extrair(extrator, texto, banca):
    """quem tira o pedido do texto: as regras, o qwen local ou o modelo na nuvem; os dois últimos traduzidos para os nomes da banca."""
    if extrator == "regras":
        return regras.extrair_pedido(texto, banca)
    if extrator == "qwen":
        return regras.nos_nomes_da_banca(transcrever.extrair_pedido(texto), banca)
    pedido, _ = nuvem.responder("Tire o pedido desta transcrição de um áudio mandado a uma banca de feira. "
                                + nuvem.instrucoes(banca) + "\nTranscrição: " + texto, transcrever.PEDIDO, 0)
    return regras.nos_nomes_da_banca(pedido, banca)


def _intervalo(valores, sorteio):
    medias = [np.mean(sorteio.choice(valores, len(valores))) for _ in range(2000)]
    return np.mean(valores), *np.percentile(medias, [2.5, 97.5])


def _medir(condicao, pedidos, banca):
    """uma condição → uma linha por pedido e ruído."""
    tamanho, com_contexto, extrator = CONDICOES[condicao]
    textos, carga = _transcricoes(pedidos, tamanho, com_contexto)
    linhas = []
    for (id_, ruido), (texto, rtf) in textos.items():
        certo = next(pedido for pedido in pedidos if pedido["id"] == id_)
        linhas.append({"condicao": condicao, "id": id_, "ruido": ruido, "tipo": certo["tipo"],
                       "voz": voz_do_pedido(certo), "ouvido": texto,
                       "wer": wer(certo["fala"], texto) if certo["fala"] else "", "rtf": rtf, "carga": carga,
                       **julgar(certo, _extrair(extrator, texto, banca))})
    return linhas


def _ja_medidas():
    """condição → as linhas que já estão no e1-pedidos.tsv. elas ficam como foram medidas: rodar de novo
    não muda o tempo, nem a resposta do qwen, que roda sem semente."""
    if not (RESULTADOS / "e1-pedidos.tsv").exists():
        return {}
    medidas = {}
    for linha in _ler_tsv(RESULTADOS / "e1-pedidos.tsv"):
        linha.update({campo: linha[campo] == "True" for campo in ("exato", "sinalizado", "silencioso")})
        linha.update({campo: float(linha[campo]) for campo in ("rtf", "carga", "acertos", "itens_certos", "itens_saida")})
        linha["wer"] = float(linha["wer"]) if linha["wer"] else ""
        medidas.setdefault(linha["condicao"], []).append(linha)
    return medidas


def avaliar():
    pedidos, banca, medidas = ler_gabarito(), ler_banca(), _ja_medidas()
    linhas = [linha for condicao in CONDICOES for linha in (medidas.get(condicao) or _medir(condicao, pedidos, banca))]
    _escrever_tsv(RESULTADOS / "e1-pedidos.tsv", linhas)
    _resumir(linhas, np.random.default_rng(7))


def _resumir(linhas, sorteio):
    cabecalho = "| condição | ruído | pedido exato | errado com \"?\" | errado sem aviso | F1 dos itens | WER | tempo / áudio |"
    tabela = [cabecalho, "|" + ":--|" * 2 + "--:|" * 6]
    for condicao in CONDICOES:
        for ruido in RUIDOS:
            grupo = [linha for linha in linhas if linha["condicao"] == condicao and linha["ruido"] == ruido]
            exato = _intervalo([linha["exato"] for linha in grupo], sorteio)
            silencioso = _intervalo([linha["silencioso"] for linha in grupo], sorteio)
            sinalizado = np.mean([linha["sinalizado"] for linha in grupo])
            acertos = sum(linha["acertos"] for linha in grupo)
            f1 = 2 * acertos / (sum(linha["itens_certos"] + linha["itens_saida"] for linha in grupo) or 1)
            wers = [linha["wer"] for linha in grupo if linha["wer"] != ""]
            rtf = np.mean([linha["rtf"] for linha in grupo])
            tabela.append(f"| {condicao} | {ruido} | {exato[0]:.0%} [{exato[1]:.0%}–{exato[2]:.0%}] | {sinalizado:.0%} | "
                          f"{silencioso[0]:.0%} [{silencioso[1]:.0%}–{silencioso[2]:.0%}] | {f1:.2f} | {np.mean(wers):.2f} | {rtf:.2f} |")
    tabela.append("")
    cargas = {CONDICOES[linha["condicao"]][0]: linha["carga"] for linha in linhas}
    tabela.append("carga do modelo, em segundos: " + ", ".join(f"{tamanho} {segundos:.1f}" for tamanho, segundos in cargas.items()))
    (RESULTADOS / "e1.md").write_text("# E1 · piloto da bancada técnica\n\n" + "\n".join(tabela) + "\n", encoding="utf-8")
    print("\n".join(tabela))


if __name__ == "__main__":
    avaliar()
