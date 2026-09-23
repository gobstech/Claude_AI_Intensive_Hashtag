"""
Junta central_template.html + dados_central.json em um único arquivo
autocontido: central.html. Esse é o arquivo final que a Aurora abre
no navegador -- não depende deste script, de Python nem de internet.
"""
import json

with open("dados_central.json", "r", encoding="utf-8") as f:
    dados_json = f.read()
    json.loads(dados_json)  # valida que é JSON de fato antes de embutir

with open("central_template.html", "r", encoding="utf-8") as f:
    template = f.read()

if "__DADOS_JSON__" not in template:
    raise SystemExit("Marcador __DADOS_JSON__ não encontrado no template.")

saida = template.replace("__DADOS_JSON__", dados_json)

with open("central.html", "w", encoding="utf-8") as f:
    f.write(saida)

print(f"OK: central.html gerado ({len(saida):,} bytes).")
