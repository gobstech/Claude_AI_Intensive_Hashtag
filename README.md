# Intensivão de Claude — Meus projetos

Esta pasta reúne os materiais e os projetos que desenvolvi durante o **Intensivão de Claude** (Hashtag Treinamentos, setembro de 2026). Foram quatro aulas práticas, cada uma com um caso de negócio realista, usando **Claude Cowork**, **Skills** e **Claude Code**.

> O que tornou o treinamento valioso é que cada exercício foi tratado como um produto de verdade, não como uma demo.
>
> Minha maior lição: o Claude não é só um chatbot. Ele rende mais como parceiro quando você dá estrutura: contexto, regras, verificação e documentação.
>
> — trecho do meu post no LinkedIn sobre o treinamento

---

## Visão geral

| Aula | Ferramenta | Caso | O que foi construído |
|---|---|---|---|
| 1 | Claude Cowork | Distribuidora Aurora | Planilha de controle e painel de recebimentos a partir de 230 comprovantes bagunçados |
| 2 | Skills | Praxis Consultoria | Duas Skills: propostas comerciais interativas e framework de decisão |
| 3 | Claude Code | Distribuidora Aurora | Central de Crédito e Cobrança: um HTML offline com 5 telas |
| 4 | Claude Code + Skills | Tergon Pisos Industriais | Redesign de site institucional com foco em SEO e conversão, a partir de um anúncio real de freelance |

Cada aula segue a mesma estrutura: **apostila (PDF)**, **guia com os prompts (HTML)**, **material para praticar** e **gabarito** (a solução de referência do curso).

---

## Aula 1 — Cowork: de documentos bagunçados a painel de gestão

**O problema:** 230 comprovantes de pagamento (janeiro a junho de 2026) de 10 clientes, em 8 layouts de banco e 5 formatos de arquivo. O material traz armadilhas de propósito: arquivos duplicados (`_copia`), nomes de cliente grafados de vários jeitos, fotos ilegíveis e pagadores com razão social diferente do cliente.

**Aprendizado:** a IA brilha com dado bagunçado, mas você ainda precisa definir o que é "certo" e conferir os casos de borda.

```
Aula 1/
├── Apostila - Intensivao de Claude - Aula 1.pdf
├── Material pra praticar/
│   ├── Comprovantes/                     # os 230 comprovantes (PDF, JPG, PNG...)
│   ├── Controle_Recebimentos.xlsx        # planilha de controle
│   ├── Aurora - Painel de Recebimentos.html
│   ├── Guia Aula 1 (Prompts).html
│   └── _ferramentas do painel/           # scripts Python, template e bibliotecas do painel
└── Gabarito/                             # planilha e painel de referência
```

---

## Aula 2 — Skills: ensinando o Claude a pensar como uma empresa

A **Praxis Consultoria** (fictícia) é uma consultoria de marketing. A aula monta um Projeto com as instruções e o documento da empresa, e depois cria duas Skills:

- **`propostas-praxis`** — gera propostas comerciais como apresentação HTML de tela cheia, navegável pelas setas do teclado.
- **`praxis-decisao`** — aplica o framework de decisão da empresa: 7 regras eliminatórias, depois a concentração de carteira, os critérios de peso, os precedentes e, por fim, a recomendação.

**Aprendizado:** a qualidade da resposta depende do contexto. Regras de negócio documentadas valem mais que prompt "esperto". Os arquivos `Ravena_Decisao_Diretoria_com_skill.docx` e `..._sem_skill.docx` mostram essa diferença lado a lado.

```
Aula 2/
├── Material pra praticar/
│   ├── Apostila - Intensivao de Claude - Aula 2.pdf
│   ├── Guia Aula 2 (Prompts).html
│   ├── Informações Praxis - Empresa.docx      # contexto da empresa
│   ├── Cliente Amora - Numeros.xlsx           # dados do cliente da proposta
│   ├── proposta-rede-impeto.html              # proposta que originou a Skill
│   └── Ravena_Decisao_Diretoria_*.docx        # comparação com e sem Skill
└── Gabarito/
    ├── SKILL propostas-praxis.md
    ├── SKILL praxis-decisao.md
    ├── Praxis_Amora_Proposta.html
    └── Proposta Praxis_Impeto.html
```

---

## Aula 3 — Claude Code: Central de Crédito e Cobrança

Um sistema que lê a carteira de contas a receber (754 títulos, 12 clientes) e responde, em cinco telas:

- **Hoje:** quem cobrar primeiro
- **Risco:** índice de 0 a 100, composto por 6 fatores
- **Previsão de caixa:** as próximas 4 semanas
- **Régua de cobrança:** a mensagem para cada cliente
- **Relatório semanal:** o resumo para a diretoria

**Pipeline:**

```
Base_bruta.xlsx --[build_data.py]--> dados_central.json --[build_html.py]--> central.html
```

**Requisitos duros:** a entrega é um único HTML que funciona offline, sem instalar nada e sem IA. A planilha de origem nunca é alterada, e os valores ficam em centavos inteiros.

**Aprendizado:** um bom `CLAUDE.md` é o que permite a qualquer sessão nova continuar o trabalho sem quebrar nada. E vale manter **uma conta num lugar só**: um bug real, em que duas telas calculavam a "média de atraso" de jeitos diferentes, nasceu exatamente disso.

```
Aula 3/
├── CLAUDE.md                 # documentação completa do projeto (leia primeiro)
├── Base_bruta.xlsx           # dados de entrada (nunca é editada)
├── build_data.py             # Excel -> JSON
├── build_html.py             # JSON + template -> HTML final
├── central_template.html     # código-fonte (é este que se edita)
├── dados_central.json        # gerado
├── central.html              # gerado: o app final
├── abrir_central.bat         # abre o app com um clique
├── Apostila e Guia da Aula 3
└── Gabarito/Central Aurora.html
```

**Para regenerar** (requer Python com `pandas` e `openpyxl`):

```
py -3 build_data.py
py -3 build_html.py
```

---

## Aula 4 — Do anúncio de freelance ao site no ar

O ponto de partida é um **anúncio real** (`anuncio.txt`): redesign de um site institucional com foco em SEO e conversão. A empresa do material é a **Tergon Pisos Industriais**.

A pasta mostra a evolução do site em três estágios:

- **`site-antes/`** — o site original, com 5 páginas
- **`site-depois/`** — primeira versão, com SEO técnico, `sitemap.xml` e `robots.txt`
- **`site-final/`** — versão final: home, páginas por aplicação (frigorífico, centro de distribuição, cozinha industrial, indústria farmacêutica), blog, imagens em WebP e botão de WhatsApp

**Aprendizado:** com IA, um projeto completo desse porte cabe em uma noite, desde que você avance um passo claro de cada vez.

```
Aula 4/
├── Apostila - Intensivao de Claude - Aula 4.pdf
├── Guia Aula 4.html
├── Gabarito/Tergon - o site pronto.html
└── Material pra Praticar/
    ├── anuncio.txt                        # o anúncio original
    ├── SKILL.md                           # skill de design frontend ("anti-slop")
    ├── fotos/                             # banco de imagens do cliente
    ├── site-antes/ · site-depois/ · site-final/
    ├── Editar o Site/                     # mini gerador estático
    │   ├── cabecalho.html · rodape.html · dados.json
    │   ├── paginas/                       # conteúdo de cada página
    │   └── gerar-site.py
    ├── Atualizar o Site (clique aqui).bat # regenera o site
    └── Ver o site (clique aqui).bat       # abre o site no navegador
```

---

## Observações

- As empresas dos casos (Aurora, Praxis, Tergon e os clientes) são fictícias, criadas para o treinamento.
- Os arquivos `.bat` são atalhos para Windows.
- Apostilas, guias e gabaritos são material do curso. Os projetos desenvolvidos durante as aulas estão nas pastas de prática de cada aula.
