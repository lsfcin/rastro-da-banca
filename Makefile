# Makefile — o contrato verify-fast que todo projeto em code/ declara: aqui, que os scripts compilam e que as regras acertam o texto do gabarito.
verify-fast:
	python3 -m py_compile transcrever.py regras.py dados.py gerar_audios.py avaliar.py simular_feirante.py
	python3 -c "from dados import ler_gabarito; from avaliar import julgar; from regras import extrair_pedido; erros = [p['id'] for p in ler_gabarito() if not julgar(p, extrair_pedido(p['fala']))['exato']]; assert erros == ['03'], erros"
