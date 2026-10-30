# regras.py — os passos 4 a 6 do fluxograma, sem IA: acha cada produto na lista da banca (fora dela vira "?"), a quantidade e a unidade por uma tabela de palavras, e a hora de buscar por uma tabela de expressões.
import re
import unicodedata

from dados import ler_banca

NUMEROS = {"um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3, "quatro": 4, "cinco": 5, "seis": 6, "sete": 7,
           "oito": 8, "nove": 9, "dez": 10, "onze": 11, "doze": 12, "meio": 0.5, "meia": 0.5}
UNIDADES = {"quilo": "kg", "quilos": "kg", "kg": "kg", "kilo": "kg", "kilos": "kg", "molho": "molho",
            "molhos": "molho", "maco": "molho", "macos": "molho", "duzia": "dúzia", "duzias": "dúzia",
            "pe": "pé", "pes": "pé", "cacho": "cacho", "cachos": "cacho"}
MINUTOS = {"meia": 30, "meio": 30, "quinze": 15}
# "lá pelas dez e meia", "às 9h", "umas onze", "ao meio-dia": a hora só conta depois de uma destas palavras
ANTES_DA_HORA = r"(?:as|pelas|pelo|umas|ao)"
HORA = re.compile(ANTES_DA_HORA + r" (meio dia|\d{1,2}(?:[:h]\d{2})?h?|" + "|".join(NUMEROS) + r")"
                  r"(?: e (meia|meio|quinze))?\b")


def normalizar(texto):
    """minúsculas, sem acento e sem pontuação, com hífen virando espaço: 'Batata-doce!' → 'batata doce'."""
    sem_acento = unicodedata.normalize("NFD", texto.lower()).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9:h ]", " ", sem_acento.replace("-", " ")).split())


def _numero(palavra):
    if re.fullmatch(r"\d+(?:[.,]\d+)?", palavra):
        return float(palavra.replace(",", "."))
    return NUMEROS.get(palavra)


def _quantidade(trecho):
    """a última quantidade com unidade do trecho: 'dois, nao, bota tres quilos' → (3, 'kg'); 'meia duzia' → (0.5, 'dúzia')."""
    palavras = trecho.split()
    achada = None
    for posicao, palavra in enumerate(palavras):
        if palavra in UNIDADES and posicao > 0 and _numero(palavras[posicao - 1]) is not None:
            quantidade = _numero(palavras[posicao - 1])
            resto = palavras[posicao + 1:posicao + 3]
            if resto[:2] in (["e", "meio"], ["e", "meia"]):
                quantidade += 0.5
            achada = (quantidade, UNIDADES[palavra])
    return achada


def _produto(trecho, nomes):
    """o produto da banca citado no trecho, pelo nome mais longo que aparece; None se nenhum."""
    citados = [(len(nome), produto) for nome, produto in nomes if re.search(rf"\b{nome}\b", trecho)]
    return max(citados)[1] if citados else None


def hora_de_buscar(texto):
    """'la pelas dez e meia' → '10:30'; sem hora reconhecida → '?'."""
    achadas = HORA.findall(normalizar(texto))
    if not achadas:
        return "?"
    hora, minutos = achadas[-1]
    if hora == "meio dia":
        return "12:00"
    numerica = re.fullmatch(r"(\d{1,2})(?:[:h](\d{2}))?h?", hora)
    horas = int(numerica.group(1)) if numerica else int(NUMEROS[hora])
    minuto = int(numerica.group(2) or 0) if numerica else 0
    return f"{horas:02d}:{MINUTOS.get(minutos, minuto):02d}"


def nos_nomes_da_banca(pedido, banca=None):
    """traduz um pedido escrito por outro extrator (o qwen) para os nomes e as unidades da banca:
    'molho de coentro' → 'coentro', 'quilos' → 'kg'; produto fora da lista vira '?'."""
    banca = banca or ler_banca()
    nomes = [(normalizar(nome), produto) for produto, dados in banca.items() for nome in dados["nomes"]]
    itens = [{"produto": _produto(normalizar(item["produto"]), nomes) or "?", "quantidade": item["quantidade"],
              "unidade": UNIDADES.get(normalizar(item["unidade"]), item["unidade"])} for item in pedido["itens"]]
    return {"itens": itens, "buscar_as": pedido["buscar_as"] or "?"}


def extrair_pedido(texto, banca=None):
    """o texto transcrito → {"itens": [{"produto", "quantidade", "unidade"}], "buscar_as"}, só com regras."""
    banca = banca or ler_banca()
    nomes = [(normalizar(nome), produto) for produto, dados in banca.items() for nome in dados["nomes"]]
    itens = []
    # cada pedaço entre vírgula, ponto, "e" ou "que" pede no máximo um produto; o "e meio" de
    # "um quilo e meio" é fração, não outro pedaço
    frases = (re.sub(r"\b(quilos?|kg|duzias?) e (meio|meia)\b", r"\1 e_\2", normalizar(frase))
              for frase in re.split(r"[.,;?!]", texto))
    for trecho in (pedaco.replace("e_", "e ") for frase in frases for pedaco in re.split(r" e | que ", frase)):
        quantidade = _quantidade(trecho)
        if quantidade:
            produto = _produto(trecho, nomes) or "?"
            itens.append({"produto": produto, "quantidade": quantidade[0], "unidade": quantidade[1]})
    return {"itens": itens, "buscar_as": hora_de_buscar(texto) if itens else "?"}
