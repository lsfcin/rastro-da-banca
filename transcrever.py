# transcrever.py — o exemplo oficial do faster-whisper, copiado do README do projeto
# (https://github.com/SYSTRAN/faster-whisper, seção "Usage", licença MIT). Duas escolhas, ambas
# previstas no próprio README: a linha do CPU (a maioria das máquinas não tem GPU) e o modelo
# "small" (cerca de 500 MB, roda num notebook comum). O audio.mp3 é o jfk.flac dos testes do projeto.
from faster_whisper import WhisperModel

model_size = "small"

# Run on GPU with FP16
# model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
model = WhisperModel(model_size, device="cpu", compute_type="int8")

segments, info = model.transcribe("audio.mp3", beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
