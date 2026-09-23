# -*- coding: utf-8 -*-
"""
Gerador do site da Tergon.

O que este script faz:
  1. Le os dados de contato em dados.json
  2. Junta cabecalho.html + o conteudo de cada pagina em paginas/ + rodape.html
  3. Escreve o resultado (paginas HTML completas, prontas) dentro de ../site-final

Para atualizar o site inteiro (telefone, whatsapp, endereco, rodape, menu):
  1. Edite dados.json, cabecalho.html ou rodape.html
  2. Rode este script de novo (ou de dois cliques em "Atualizar o Site.bat")

Nao precisa editar nada dentro de site-final/ na mao - esse script sobrescreve
os arquivos .html de la toda vez que roda.
"""
import json
import re
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = BASE_DIR.parent / "site-final"
PAGINAS_DIR = BASE_DIR / "paginas"

FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'"
    "%3E%3Crect width='100' height='100' fill='%230b0d0f'/%3E%3Ctext x='50' y='70' "
    "font-size='60' font-family='Arial,sans-serif' font-weight='900' fill='%23f2941f' "
    "text-anchor='middle'%3ET%3C/text%3E%3C/svg%3E"
)

FONTS_URL = (
    "https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@600;700;800;900"
    "&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500;600&display=swap"
)


def carregar_dados():
    with open(BASE_DIR / "dados.json", encoding="utf-8") as f:
        dados = json.load(f)
    dados["whatsapp_url"] = "https://wa.me/{}?text={}".format(
        dados["whatsapp_numero"], urllib.parse.quote(dados["whatsapp_mensagem_padrao"])
    )
    dados["endereco_completo"] = "{} - {} - {}/{}".format(
        dados["endereco_rua"], dados["endereco_bairro"], dados["endereco_cidade"], dados["endereco_uf"]
    )
    return dados


def substituir_tokens(texto, contexto):
    for chave, valor in contexto.items():
        texto = texto.replace("{{" + chave + "}}", str(valor))
    return texto


def montar_contexto_global(dados, prefixo):
    return {
        "PREFIXO": prefixo,
        "NOME_EMPRESA": dados["nome_empresa"],
        "DOMINIO": dados["dominio"],
        "TELEFONE_EXIBICAO": dados["telefone_exibicao"],
        "TELEFONE_TEL": dados["telefone_tel"],
        "WHATSAPP_NUMERO": dados["whatsapp_numero"],
        "WHATSAPP_URL": dados["whatsapp_url"],
        "EMAIL": dados["email"],
        "ENDERECO_CURTO": dados["endereco_curto"],
        "ENDERECO_COMPLETO": dados["endereco_completo"],
        "ENDERECO_RUA": dados["endereco_rua"],
        "ENDERECO_BAIRRO": dados["endereco_bairro"],
        "ENDERECO_CIDADE": dados["endereco_cidade"],
        "ENDERECO_UF": dados["endereco_uf"],
        "ANO_FUNDACAO": dados["ano_fundacao"],
        "ANO_COPYRIGHT": dados["ano_copyright"],
        "HORARIO": dados["horario"],
    }


def extrair_meta(conteudo_bruto):
    """Le o bloco <!--META ... --> no topo do arquivo e devolve (meta_dict, resto_do_conteudo)."""
    m = re.match(r"\s*<!--META(.*?)-->\s*(.*)", conteudo_bruto, re.S)
    if not m:
        raise ValueError("Arquivo de pagina sem bloco <!--META ... --> no topo.")
    bloco, resto = m.group(1), m.group(2)
    meta = {}
    for linha in bloco.strip().splitlines():
        linha = linha.strip()
        if not linha or ":" not in linha:
            continue
        chave, valor = linha.split(":", 1)
        meta[chave.strip().lower()] = valor.strip()
    return meta, resto


def montar_head(meta, contexto, caminho_saida):
    canonical = contexto["DOMINIO"] + "/" + ("" if caminho_saida == "index.html" else caminho_saida)
    og_image = contexto["DOMINIO"] + "/" + meta.get("ogimage", "images/fotos/01-hero-galpao-piso-espelhado.jpg")
    title = meta["title"]
    description = meta["description"]

    schema_local_business = """
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "{nome}",
  "image": "{dominio}/images/fotos/01-hero-galpao-piso-espelhado.jpg",
  "telephone": "{tel}",
  "email": "{email}",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "{rua}",
    "addressLocality": "{cidade}",
    "addressRegion": "{uf}",
    "addressCountry": "BR"
  }},
  "areaServed": ["São Paulo", "Minas Gerais", "Paraná", "Santa Catarina"],
  "openingHoursSpecification": {{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "opens": "08:00",
    "closes": "18:00"
  }},
  "url": "{dominio}/",
  "priceRange": "$$"
}}
</script>""".format(
        nome=contexto["NOME_EMPRESA"], dominio=contexto["DOMINIO"], tel=contexto["TELEFONE_TEL"],
        email=contexto["EMAIL"], rua=contexto["ENDERECO_RUA"], cidade=contexto["ENDERECO_CIDADE"],
        uf=contexto["ENDERECO_UF"],
    )

    return """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="icon" href="{favicon}">

<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{og_image}">
<meta property="og:site_name" content="{nome_empresa}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts_url}">
<link rel="stylesheet" href="{prefixo}css/estilo.css">
{schema}
</head>
<body>
<script>document.documentElement.className += " js";</script>

<div class="progress"><div class="progress__fill"></div></div>
""".format(
        title=title, description=description, canonical=canonical, favicon=FAVICON,
        og_image=og_image, nome_empresa=contexto["NOME_EMPRESA"], fonts_url=FONTS_URL,
        prefixo=contexto["PREFIXO"], schema=schema_local_business,
    )


def gerar():
    dados = carregar_dados()
    cabecalho_tpl = (BASE_DIR / "cabecalho.html").read_text(encoding="utf-8")
    rodape_tpl = (BASE_DIR / "rodape.html").read_text(encoding="utf-8")

    arquivos = sorted(PAGINAS_DIR.rglob("*.content.html"))
    if not arquivos:
        print("Nenhuma pagina encontrada em paginas/.")
        return

    for arquivo in arquivos:
        rel = arquivo.relative_to(PAGINAS_DIR)
        caminho_saida = str(rel).replace("\\", "/").replace(".content.html", ".html")
        profundidade = caminho_saida.count("/")
        prefixo = "../" * profundidade

        contexto = montar_contexto_global(dados, prefixo)

        bruto = arquivo.read_text(encoding="utf-8")
        meta, conteudo = extrair_meta(bruto)

        head = montar_head(meta, contexto, caminho_saida)
        cabecalho = substituir_tokens(cabecalho_tpl, contexto)
        rodape = substituir_tokens(rodape_tpl, contexto)
        conteudo = substituir_tokens(conteudo, contexto)

        pagina = (
            head
            + cabecalho
            + '\n<main id="conteudo">\n'
            + conteudo
            + "\n</main>\n\n"
            + rodape
            + "\n</body>\n</html>\n"
        )

        destino = SITE_DIR / caminho_saida
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(pagina, encoding="utf-8")
        print("gerado:", caminho_saida)

    gerar_sitemap(dados, arquivos)
    print("\nPronto! {} paginas geradas em site-final/.".format(len(arquivos)))


def gerar_sitemap(dados, arquivos):
    urls = []
    for arquivo in arquivos:
        rel = arquivo.relative_to(PAGINAS_DIR)
        caminho = str(rel).replace("\\", "/").replace(".content.html", ".html")
        loc = dados["dominio"] + "/" + ("" if caminho == "index.html" else caminho)
        urls.append("  <url><loc>{}</loc></url>".format(loc))

    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )
    (SITE_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")

    robots = "User-agent: *\nAllow: /\n\nSitemap: {}/sitemap.xml\n".format(dados["dominio"])
    (SITE_DIR / "robots.txt").write_text(robots, encoding="utf-8")


if __name__ == "__main__":
    gerar()
