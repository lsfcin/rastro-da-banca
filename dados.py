# dados.py — lê a lista da banca e o gabarito dos pedidos, as duas tabelas que os experimentos usam.
import csv
from pathlib import Path

PASTA = Path(__file__).parent


def _linhas(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        return list(csv.DictReader((linha for linha in arquivo if not linha.startswith("#")), delimiter="\t"))


def ler_banca():
    """produto → {"nomes": [o produto e os outros nomes], "unidade", "preco"}."""
    banca = {}
    for linha in _linhas(PASTA / "banca.tsv"):
        outros = [nome for nome in linha["outros nomes"].split(",") if nome]
        banca[linha["produto"]] = {"nomes": [linha["produto"], *outros], "unidade": linha["unidade"],
                                   "preco": float(linha["preço"])}
    return banca


def ler_itens(texto):
    """'macaxeira|2|kg; coentro|1|molho' → [{"produto", "quantidade", "unidade"}, …]."""
    itens = []
    for item in filter(None, (parte.strip() for parte in texto.split(";"))):
        produto, quantidade, unidade = item.split("|")
        itens.append({"produto": produto, "quantidade": float(quantidade), "unidade": unidade})
    return itens


def ler_gabarito():
    """os pedidos do piloto, cada um com a fala, o pedido certo e a hora de buscar."""
    pedidos = _linhas(PASTA / "pedidos" / "gabarito.tsv")
    for pedido in pedidos:
        pedido.update({campo: valor or "" for campo, valor in pedido.items()})
        pedido["itens"] = ler_itens(pedido["itens"])
    return pedidos
