# transcrever.py — o exemplo oficial do faster-whisper (README do projeto, seção "Usage", licença
# MIT), com a entrada e a saída trocadas para a feira: entra o áudio de um pedido mandado à banca,
# sai o pedido (produto, quantidade, hora de buscar), tirado da transcrição por um modelo pequeno
# local (qwen3:4b no Ollama, licença Apache 2.0).
import json
import sys
import urllib.request

from faster_whisper import WhisperModel

model_size = "small"

# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

# entrada: uma frase como a cliente diria primeiro ensina ao modelo as palavras da banca
CONTEXTO = ("Pedido por áudio para a banca de dona Cida, na feira: me separa um molho de coentro, macaxeira, "
            "jerimum, feijão verde, uma dúzia de ovos caipira e um cacho de banana prata, que eu busco às nove.")

# saída: o modelo pequeno devolve o pedido neste formato, e só nele
PEDIDO = {
    "type": "object",
    "properties": {
        "itens": {"type": "array", "items": {"type": "object", "properties": {
            "produto": {"type": "string"}, "quantidade": {"type": "number"}, "unidade": {"type": "string"}},
            "required": ["produto", "quantidade", "unidade"]}},
        "buscar_as": {"type": "string"},
    },
    "required": ["itens", "buscar_as"],
}


def extrair_pedido(texto):
    corpo = {"model": "qwen3:4b", "stream": False, "think": False, "format": PEDIDO,
             "prompt": "Liste cada produto pedido, com a quantidade em número e a unidade, e a hora de "
                       "buscar (HH:MM), neste pedido de feira: " + texto}
    pedido = urllib.request.Request("http://localhost:11434/api/generate", json.dumps(corpo).encode())
    with urllib.request.urlopen(pedido) as resposta:
        return json.loads(json.loads(resposta.read())["response"])


for audio in sys.argv[1:]:
    segments, info = model.transcribe(audio, beam_size=5, language="pt", initial_prompt=CONTEXTO)
    texto = " ".join(segment.text.strip() for segment in segments)
    pedido = extrair_pedido(texto)
    print(f"\n{audio}\n  ouvido: {texto}")
    for item in pedido["itens"]:
        print(f"  - {item['quantidade']:g} {item['unidade']} de {item['produto']}")
    print(f"  buscar às {pedido['buscar_as']}")
