# nuvem.py — um modelo de linguagem na nuvem (DeepSeek V4.1 Flash, pelo OpenRouter) respondendo num formato json fixo: a persona do E2 e o pipeline alternativo do E1. cada resposta fica guardada, e a rodada seguinte não chama a rede.
import hashlib
import json
import os
import time
import urllib.request

from dados import PASTA

MODELO = "deepseek/deepseek-v4.1-flash"
GUARDADAS = PASTA / "resultados" / "respostas.tsv"
CABECALHO = ("# respostas.tsv — cada resposta do DeepSeek, pelo hash do pedido: deixa o E1 e o E2 rodarem de novo sem a API.\n"
             "hash\tresposta\n")
DECISAO = {"type": "object", "properties": {"ouvir": {"type": "boolean"}}, "required": ["ouvir"]}


def _estrito(esquema):
    """o modo estrito do OpenRouter pede additionalProperties: false em todo objeto."""
    if esquema.get("type") == "object":
        return {**esquema, "additionalProperties": False,
                "properties": {campo: _estrito(valor) for campo, valor in esquema["properties"].items()}}
    if esquema.get("type") == "array":
        return {**esquema, "items": _estrito(esquema["items"])}
    return esquema


def instrucoes(banca):
    """as mesmas regras de anotação para a persona e para o pipeline alternativo: a lista da banca e o formato."""
    lista = "; ".join(f"{produto} (por {dados['unidade']})" for produto, dados in banca.items())
    return (f"O que a banca vende: {lista}. Produto que não está nesta lista é anotado como \"?\". "
            "Quantidade em número; hora no formato HH:MM, ou \"?\" se a cliente não disse. "
            "Se o áudio não é um pedido, nenhum item.")


def responder(texto, esquema, semente):
    """o texto → (a resposta no formato do esquema, tokens gastos)."""
    corpo = {"model": MODELO, "temperature": 1.0, "seed": semente, "messages": [{"role": "user", "content": texto}],
             "response_format": {"type": "json_schema",
                                 "json_schema": {"name": "resposta", "strict": True, "schema": _estrito(esquema)}}}
    corpo_bruto = json.dumps(corpo).encode()
    # se a internet cai no meio, a rodada seguinte retoma de onde parou
    chave = hashlib.sha256(corpo_bruto).hexdigest()[:20]
    guardadas = _guardadas()
    if chave in guardadas:
        dados = json.loads(guardadas[chave])
    else:
        dados = _chamar(corpo_bruto)
        guardadas[chave] = json.dumps(dados)
        with open(GUARDADAS, "a", encoding="utf-8") as arquivo:
            arquivo.write(("" if arquivo.tell() else CABECALHO) + f"{chave}\t{guardadas[chave]}\n")
    return json.loads(dados["choices"][0]["message"]["content"]), dados["usage"]["total_tokens"]


_CACHE = {}


def _guardadas():
    """hash → resposta em json, lidas do arquivo uma vez por rodada."""
    if not _CACHE and GUARDADAS.exists():
        linhas = GUARDADAS.read_text(encoding="utf-8").splitlines()[2:]
        _CACHE.update(linha.split("\t", 1) for linha in linhas)
    return _CACHE


def _chamar(corpo_bruto):
    pedido = urllib.request.Request("https://openrouter.ai/api/v1/chat/completions", corpo_bruto,
                                    {"Content-Type": "application/json",
                                     "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"})
    for tentativa in range(8):  # limite de pedidos por minuto ou provedor fora: espera e tenta de novo
        try:
            with urllib.request.urlopen(pedido, timeout=180) as resposta:
                return json.loads(resposta.read())
        except OSError as erro:  # rede: HTTPError, URLError, tempo esgotado, conexão derrubada
            if getattr(erro, "code", 503) not in (429, 500, 502, 503) or tentativa == 7:
                raise
            time.sleep(15 * (tentativa + 1))

