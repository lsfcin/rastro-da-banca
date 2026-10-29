# gerar_audios.py — os áudios do piloto: cada fala do gabarito em voz sintética (Piper, 4 vozes pt_BR), com o burburinho de outras falas por baixo, em três níveis de ruído; saem em .ogg (opus), como o WhatsApp manda.
import subprocess
import sys
from pathlib import Path

import numpy as np

from dados import PASTA, ler_gabarito

VOZES = ["pt_BR-faber-medium", "pt_BR-cadu-medium", "pt_BR-jeff-medium", "pt_BR-edresson-low"]
TAXA = 16000
RUIDOS = {"limpo": None, "10db": 10, "0db": 0}  # relação sinal-ruído, em dB
SAIDA = PASTA / "audios" / "e1"


def voz_do_pedido(pedido):
    return VOZES[int(pedido["id"]) % len(VOZES)]


def _sintetizar(piper, pasta_vozes, voz, texto, wav):
    subprocess.run([piper, "--model", str(Path(pasta_vozes) / f"{voz}.onnx"), "--output_file", str(wav)],
                   input=texto.encode(), check=True, capture_output=True)


def _ler(wav):
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "1", "-ar", str(TAXA), "-"],
                           check=True, capture_output=True).stdout
    return np.frombuffer(bruto, dtype=np.float32)


def _gravar_ogg(sinal, ogg):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(TAXA), "-ac", "1", "-i", "-",
                    "-c:a", "libopus", "-b:a", "24k", str(ogg)], input=sinal.astype(np.float32).tobytes(), check=True)


def _burburinho(outras, tamanho, sorteio):
    """três outras falas somadas, cada uma repetida e deslocada até cobrir o pedido inteiro."""
    soma = np.zeros(tamanho, dtype=np.float32)
    for fala in sorteio.choice(len(outras), 3, replace=False):
        repetida = np.tile(outras[fala], tamanho // len(outras[fala]) + 2)
        inicio = sorteio.integers(len(outras[fala]))
        soma += repetida[inicio:inicio + tamanho]
    return soma


def _misturar(voz, ruido, snr):
    if snr is None:
        return voz
    potencia_voz = np.mean(voz ** 2) if voz.any() else np.mean(ruido ** 2)
    ganho = np.sqrt(potencia_voz / (np.mean(ruido ** 2) * 10 ** (snr / 10)))
    misturado = voz + ganho * ruido
    return misturado / max(1.0, np.abs(misturado).max())


def gerar(piper, pasta_vozes, rascunho):
    SAIDA.mkdir(parents=True, exist_ok=True)
    pedidos = ler_gabarito()
    limpas = {}
    for pedido in (pedido for pedido in pedidos if pedido["fala"]):
        wav = Path(rascunho) / f"{pedido['id']}.wav"
        _sintetizar(piper, pasta_vozes, voz_do_pedido(pedido), pedido["fala"], wav)
        limpas[pedido["id"]] = _ler(wav)
    sorteio = np.random.default_rng(7)
    for pedido in pedidos:
        voz = limpas.get(pedido["id"], np.zeros(6 * TAXA, dtype=np.float32))  # "ruído": só o burburinho
        voz = np.concatenate([np.zeros(TAXA // 2), voz, np.zeros(TAXA // 2)]).astype(np.float32)
        outras = [fala for chave, fala in limpas.items() if chave != pedido["id"]]
        ruido = _burburinho(outras, len(voz), sorteio)
        for nome, snr in RUIDOS.items():
            _gravar_ogg(_misturar(voz, ruido, snr if pedido["fala"] else 0), SAIDA / f"{pedido['id']}-{nome}.ogg")


if __name__ == "__main__":
    gerar(*sys.argv[1:4])  # python gerar_audios.py <piper> <pasta das vozes> <pasta de rascunho>
