# -*- coding: utf-8 -*-
"""
Calcula os indicadores usados na aba "Insights" do painel (mesma lógica usada
na primeira versão do painel, para a Aurora). Rode isso depois de atualizar a
aba "Recebimentos" da planilha e ANTES de editar o texto da aba Insights no
template.html — os números aqui devem ser usados para atualizar as frases
hardcoded do template (ele não tem substituição automática de texto, só de
dados dos gráficos).

Uso:
    python3 calc_indicadores.py "/caminho/para/Controle_Recebimentos.xlsx"
"""
import sys
from collections import defaultdict
import openpyxl


def brl(x):
    s = f"{x:,.2f}"
    s = s.replace(',', '§').replace('.', ',').replace('§', '.')
    return f"R$ {s}"


def main(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb['Recebimentos']
    cadastro_ws = wb['Cadastro de Clientes']

    cli_map = {}
    for row in cadastro_ws.iter_rows(min_row=5, values_only=True):
        if not row or not row[0]:
            continue
        cli_map[row[0]] = (row[1], row[2])

    header_row = None
    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if row and row[0] == 'Data':
            header_row = i
            break
    if header_row is None:
        raise SystemExit('Não encontrei a linha de cabeçalho (Data | Cliente | ...) na aba Recebimentos.')

    rows = []
    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        if not row or row[0] is None:
            continue
        data, cliente, valor = row[0], row[1], row[2]
        regiao, categoria = cli_map.get(cliente, (None, None))
        rows.append({
            'data': data, 'cliente': cliente, 'valor': float(valor),
            'regiao': regiao or 'Não identificado',
            'categoria': categoria or 'Não identificado',
        })

    total = sum(r['valor'] for r in rows)
    count = len(rows)
    avg = total / count if count else 0

    by_period = defaultdict(float)
    for r in rows:
        key = (r['data'].year, r['data'].month)
        by_period[key] += r['valor']
    period_list = sorted(by_period.items())
    best_period = max(period_list, key=lambda x: x[1])

    by_client = defaultdict(float)
    for r in rows:
        by_client[r['cliente']] += r['valor']
    client_sorted = sorted(by_client.items(), key=lambda x: -x[1])

    by_region = defaultdict(float)
    for r in rows:
        by_region[r['regiao']] += r['valor']
    region_sorted = sorted(by_region.items(), key=lambda x: -x[1])
    region_real = [(k, v) for k, v in region_sorted if k != 'Não identificado']

    by_cat = defaultdict(float)
    for r in rows:
        by_cat[r['categoria']] += r['valor']
    cat_sorted = sorted(by_cat.items(), key=lambda x: -x[1])
    cat_real = [(k, v) for k, v in cat_sorted if k != 'Não identificado']

    top1_pct = client_sorted[0][1] / total * 100 if total else 0
    top3_pct = sum(v for _, v in client_sorted[:3]) / total * 100 if total else 0
    top5_pct = sum(v for _, v in client_sorted[:5]) / total * 100 if total else 0

    unmatched_total = by_region.get('Não identificado', 0.0)
    unmatched_pct = unmatched_total / total * 100 if total else 0
    unmatched_clients = sorted(set(r['cliente'] for r in rows if r['regiao'] == 'Não identificado'))
    unmatched_count = sum(1 for r in rows if r['regiao'] == 'Não identificado')

    print(f"Período coberto: {period_list[0][0]} a {period_list[-1][0]} ({len(period_list)} meses)")
    print(f"TOTAL: {brl(total)}  |  Nº recebimentos: {count}  |  Ticket médio: {brl(avg)}")
    print()
    print("Recebido por mês (ano, mês) -> valor, variação % vs mês anterior:")
    prev = None
    for (y, m), v in period_list:
        var = '' if prev is None else f"  ({(v - prev) / prev * 100:+.1f}% vs mês anterior)" if prev else ''
        print(f"  {y}-{m:02d}: {brl(v)}{var}")
        prev = v
    print(f"  Melhor mês: {best_period[0][0]}-{best_period[0][1]:02d} = {brl(best_period[1])}")
    print()
    print("Regiões (maior -> menor), excluindo 'Não identificado':")
    region_total = sum(v for _, v in region_real)
    for k, v in region_sorted:
        pct = v / region_total * 100 if k != 'Não identificado' and region_total else None
        print(f"  {k}: {brl(v)}" + (f"  ({pct:.1f}% do caixa regionalizado)" if pct is not None else "  (fora do cadastro)"))
    print()
    print("Categorias (maior -> menor), excluindo 'Não identificado':")
    for k, v in cat_sorted:
        pct = v / total * 100 if total else 0
        print(f"  {k}: {brl(v)}  ({pct:.1f}% do total)")
    print()
    print(f"Concentração de clientes: top1={top1_pct:.1f}%  top3={top3_pct:.1f}%  top5={top5_pct:.1f}%")
    print("Ranking de clientes (todos):")
    for name, v in client_sorted:
        print(f"  {name}: {brl(v)}  ({v/total*100:.1f}%)" if total else f"  {name}: {brl(v)}")
    print()
    print(f"Pagadores fora do cadastro: {unmatched_count} recebimento(s), {brl(unmatched_total)} ({unmatched_pct:.2f}% do total)")
    if unmatched_clients:
        print("  Clientes:", ', '.join(unmatched_clients))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Uso: python3 calc_indicadores.py "/caminho/para/Controle_Recebimentos.xlsx"')
    main(sys.argv[1])
