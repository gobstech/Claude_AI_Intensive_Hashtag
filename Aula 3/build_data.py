"""
Extrai os dados brutos de Base_bruta.xlsx e gera dados_central.json.

Este script roda uma vez (no ambiente de quem está montando a Central).
O arquivo central.html gerado a partir do JSON não depende deste script
nem de Python para ser aberto -- ele é 100% autocontido.

Nenhum número da Central é calculado aqui. Este script só copia os dados
da planilha para JSON, convertendo valores monetários para centavos
(inteiro) e datas para o formato ISO 8601. Toda a conta (fila, risco,
frases) é feita em JavaScript, dentro do central.html, em cima desses
dados brutos.
"""
import json
import re
import pandas as pd

ARQUIVO_ORIGEM = "Base_bruta.xlsx"
ARQUIVO_SAIDA = "dados_central.json"

MESES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5,
    "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10,
    "novembro": 11, "dezembro": 12,
}


def extrair_data_referencia(caminho):
    leia = pd.read_excel(caminho, sheet_name="Leia-me", header=None)
    for _, row in leia.iterrows():
        rotulo = str(row[0]) if pd.notna(row[0]) else ""
        if rotulo.strip().upper() == "DATA DE REFERÊNCIA":
            texto = str(row[1]).strip().lower()
            m = re.match(r"(\d{1,2}) de (\w+) de (\d{4})", texto)
            if not m:
                raise ValueError(f"Não entendi a data de referência: {texto!r}")
            dia, mes_nome, ano = m.groups()
            mes = MESES[mes_nome]
            return f"{int(ano):04d}-{mes:02d}-{int(dia):02d}"
    raise ValueError("Não encontrei a linha 'DATA DE REFERÊNCIA' na aba Leia-me.")


def data_iso_ou_none(valor):
    if pd.isna(valor):
        return None
    return pd.Timestamp(valor).strftime("%Y-%m-%d")


def datahora_iso(valor):
    return pd.Timestamp(valor).strftime("%Y-%m-%dT%H:%M:%S")


def centavos(valor_em_reais):
    # os valores da planilha são reais inteiros, sem casa decimal
    return int(round(float(valor_em_reais) * 100))


def main():
    referencia = extrair_data_referencia(ARQUIVO_ORIGEM)

    clientes_df = pd.read_excel(ARQUIVO_ORIGEM, sheet_name="Clientes")
    titulos_df = pd.read_excel(ARQUIVO_ORIGEM, sheet_name="Títulos")
    cobrancas_df = pd.read_excel(ARQUIVO_ORIGEM, sheet_name="Cobranças")

    clientes = []
    for _, r in clientes_df.iterrows():
        clientes.append({
            "codigo": int(r["Código do cliente"]),
            "nome": str(r["Nome do cliente"]),
            "categoria": str(r["Categoria"]),
            "regiao": str(r["Região"]),
            "uf": str(r["UF"]),
            "prazo_contratado": str(r["Prazo de pagamento contratado"]),
            "prazo_dias": int(r["Prazo em dias"]),
            "limite_credito_centavos": centavos(r["Limite de crédito"]),
            "cliente_desde": data_iso_ou_none(r["Cliente desde"]),
            "contato": str(r["Contato"]),
            "telefone": str(r["Telefone"]),
        })

    titulos = []
    for _, r in titulos_df.iterrows():
        titulos.append({
            "numero": str(r["Número do título"]),
            "codigo_cliente": int(r["Código do cliente"]),
            "valor_centavos": centavos(r["Valor do título"]),
            "emissao": data_iso_ou_none(r["Data de emissão"]),
            "vencimento": data_iso_ou_none(r["Data de vencimento"]),
            "pagamento": data_iso_ou_none(r["Data de pagamento"]),
        })

    cobrancas = []
    for _, r in cobrancas_df.iterrows():
        cobrancas.append({
            "codigo": int(r["Código do registro"]),
            "codigo_cliente": int(r["Código do cliente"]),
            "data_hora": datahora_iso(r["Data e hora do contato"]),
            "canal": str(r["Canal"]),
            "tom": str(r["Tom usado"]),
            "valor_cobrado_centavos": centavos(r["Valor cobrado"]),
            "titulos_na_cobranca": int(r["Títulos na cobrança"]),
            "mensagem": str(r["Mensagem enviada"]),
        })

    dados = {
        "referencia": referencia,
        "clientes": clientes,
        "titulos": titulos,
        "cobrancas": cobrancas,
    }

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, separators=(",", ":"))

    print(f"OK: {ARQUIVO_SAIDA} gerado. referencia={referencia} "
          f"clientes={len(clientes)} titulos={len(titulos)} cobrancas={len(cobrancas)}")


if __name__ == "__main__":
    main()
