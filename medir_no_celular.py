# medir_no_celular.py — a medida que o tec e o flx deixaram em aberto: o whisper rodando no celular, pelo whisper.cpp, sobre os 30 áudios do E1 a 10 dB, com as mesmas regras e o mesmo julgamento do avaliar.py; mede pedido exato, erro sem aviso, tempo / áudio, carga do modelo e memória.
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

import regras
import transcrever
from avaliar import RESULTADOS, julgar
from dados import ler_gabarito
from gerar_audios import SAIDA

RUIDO = "10db"
PASTA_NO_CELULAR = "/data/local/tmp/rastro"


def _adb(adb, *argumentos):
    return subprocess.run([adb, *argumentos], check=True, capture_output=True, text=True).stdout


def _enviar(adb, whisper_cli, modelo, pedidos):
    _adb(adb, "shell", "mkdir", "-p", PASTA_NO_CELULAR)
    _adb(adb, "push", whisper_cli, f"{PASTA_NO_CELULAR}/whisper-cli")
    _adb(adb, "push", modelo, f"{PASTA_NO_CELULAR}/modelo.bin")
    with tempfile.TemporaryDirectory() as rascunho:
        for pedido in pedidos:
            wav = Path(rascunho) / f"{pedido['id']}.wav"  # o whisper.cpp lê wav 16 kHz mono
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SAIDA / f"{pedido['id']}-{RUIDO}.ogg"),
                            "-ar", "16000", "-ac", "1", str(wav)], check=True)
            _adb(adb, "push", str(wav), f"{PASTA_NO_CELULAR}/{wav.name}")


def _rodar(adb, id_, threads):
    """transcreve um áudio no celular; devolve o texto, os ms de carga e de total, e a memória máxima em MB."""
    comando = (f"cd {PASTA_NO_CELULAR} && /system/bin/time -v ./whisper-cli -m modelo.bin -f {id_}.wav -l pt "
               f"-t {threads} -bs 5 -nt --prompt \"{transcrever.CONTEXTO}\" 2>&1")
    saida = _adb(adb, "shell", comando)
    texto = " ".join(linha.strip() for linha in saida.splitlines()
                     if linha.strip() and not re.match(r"^(whisper_|main:|system_info|ggml_|\s*Command|\s*\w[\w ()/%:]*: )", linha))
    carga = float(re.search(r"load time =\s*([\d.]+) ms", saida).group(1))
    total = float(re.search(r"total time =\s*([\d.]+) ms", saida).group(1))
    memoria = re.search(r"Maximum resident set size \(kbytes\): (\d+)", saida)
    return texto, carga, total, int(memoria.group(1)) / 1024 if memoria else None


def medir(adb, whisper_cli, modelo, threads=4):
    pedidos = ler_gabarito()
    _enviar(adb, whisper_cli, modelo, pedidos)
    aparelho = _adb(adb, "shell", "getprop", "ro.product.model").strip()
    linhas = []
    for pedido in pedidos:
        texto, carga, total, memoria = _rodar(adb, pedido["id"], threads)
        duracao = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                        str(SAIDA / f"{pedido['id']}-{RUIDO}.ogg")], capture_output=True, text=True).stdout)
        linhas.append({"id": pedido["id"], "ouvido": texto, "carga": carga, "rtf": (total - carga) / 1000 / duracao,
                       "memoria": memoria, **julgar(pedido, regras.extrair_pedido(texto))})
    memorias = [linha["memoria"] for linha in linhas if linha["memoria"]]
    tabela = [f"aparelho: {aparelho} · whisper.cpp, modelo {Path(modelo).name}, {threads} threads, ruído {RUIDO}", "",
              "| pedido exato | errado com \"?\" | errado sem aviso | tempo / áudio | carga do modelo | memória máxima |",
              "|--:|--:|--:|--:|--:|--:|",
              f"| {np.mean([l['exato'] for l in linhas]):.0%} | {np.mean([l['sinalizado'] for l in linhas]):.0%} | "
              f"{np.mean([l['silencioso'] for l in linhas]):.0%} | {np.mean([l['rtf'] for l in linhas]):.2f} | "
              f"{np.median([l['carga'] for l in linhas]) / 1000:.1f} s | {f"{max(memorias):.0f} MB" if memorias else "não medida"} |"]
    (RESULTADOS / "e1-celular.md").write_text("# E1 · o whisper no celular\n\n" + "\n".join(tabela) + "\n", encoding="utf-8")
    print("\n".join(tabela))
    for linha in linhas:
        print(linha["id"], linha["exato"], linha["ouvido"][:90])


if __name__ == "__main__":
    medir(*sys.argv[1:4])  # python medir_no_celular.py <adb> <whisper-cli para arm64> <modelo ggml>
