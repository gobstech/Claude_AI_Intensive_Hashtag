# CLAUDE.md — Central de Crédito e Cobrança, Distribuidora Aurora

Este arquivo é para quem abrir esta pasta sem ter visto a conversa em que ela foi
construída — inclusive uma sessão nova do Claude, sem memória do que veio antes.
Leia isto antes de tocar em qualquer coisa. Se depois de ler ainda sobrar uma
pergunta óbvia, é porque este arquivo está incompleto — não adivinhe, pergunte ao
dono do projeto.

## O que é este projeto

Uma Central de Crédito e Cobrança para uma distribuidora fictícia (exercício do
curso "Intensivão de Claude", mas tratado aqui como se fosse uma ferramenta real de
uso interno). Ela lê a carteira de contas a receber da empresa e responde, com
número e frase, cinco perguntas: quem cobrar hoje, quem é risco de crédito de
verdade, quanto entra de caixa nas próximas semanas, o que escrever pra cada
cliente, e o que contar pra diretoria em quatro minutos.

**A entrega é um único arquivo HTML** (`central.html`) que abre em qualquer
navegador, sem internet, sem instalar nada, sem conta, sem IA. Isso não é um
detalhe técnico — é o requisito mais duro do projeto e explica quase toda decisão
estranha que você vai encontrar no código (por que não tem framework, por que os
dados estão embutidos no HTML, por que o registro de cobrança não persiste
sozinho). Antes de "melhorar" alguma coisa, pergunte se a melhoria quebra essa
regra.

## Como as peças se encaixam

```
Base_bruta.xlsx  --[build_data.py]-->  dados_central.json  --[build_html.py]-->  central.html
                                              ^                                        ^
                                     (só dado bruto, sem                    (é isto que se abre
                                      conta nenhuma feita)                   no navegador — autocontido)
```

- **`Base_bruta.xlsx`** — a planilha que "vem da empresa". Tem 4 abas: `Leia-me`
  (explica a base e diz a data de referência), `Clientes`, `Títulos`, `Cobranças`.
  Nunca é escrita por nada neste projeto — é gravação zero, sempre. A aba `Leia-me`
  explica cada coluna; não repito aqui.
- **`build_data.py`** — lê o Excel, converte valor pra centavos (inteiro) e data
  pra ISO 8601, e escreve `dados_central.json`. Não calcula nada — é cópia
  fiel dos dados brutos. O docstring do arquivo já explica isso; leia-o antes de
  tocar.
- **`build_html.py`** — cola `dados_central.json` dentro de
  `central_template.html` (no lugar do marcador `__DADOS_JSON__`) e escreve
  `central.html`. Também não calcula nada.
- **`dados_central.json`** — gerado por `build_data.py`, consumido por
  `build_html.py`. Também não se edita na mão — é dado de passagem, não fonte.
- **`central_template.html`** — o código-fonte de verdade. Um arquivo só, HTML +
  CSS + JavaScript vanilla (sem build step, sem npm, sem framework), organizado em
  IIFE. **É este arquivo que você edita.** Nunca edite `central.html` na mão — ele
  é gerado, e a próxima vez que alguém rodar `build_html.py` sua edição desaparece.
- **`central.html`** — o artefato final, o que a Aurora realmente abre. Gerado,
  não editado.
- **`abrir_central.bat`** — atalho de um clique (`start central.html`) pra quem
  não quer usar terminal.
- **`Gabarito/Central Aurora.html`** — a solução de referência do exercício do
  curso. Foi consultada uma vez, no começo, só pra calibrar se o formato do índice
  de risco (seis fatores, 0–100) estava na faixa esperada — o código deste projeto
  foi escrito de forma independente, não copiado de lá. Não é fonte de verdade
  para decisões futuras; é só uma segunda opinião que já foi usada e não precisa
  ser consultada de novo.
- **`Apostila - Intensivao de Claude - Aula 3.pdf`** e **`Guia Aula 3
  (Prompts).html`** — material do curso (apostila e os prompts usados nas
  rodadas). Não fazem parte do app e não são lidos por nenhum script; são
  contexto histórico de como este projeto nasceu, não documentação de código.

## Pré-requisito pra quem regenera os dados

Só quem roda `build_data.py` precisa de Python com `pandas` e `openpyxl`
instalados (`pip install pandas openpyxl` se faltar). Quem só abre
`central.html` não precisa de nada disso — nem Python, nem internet. Os
comandos deste arquivo usam `py -3` (o launcher do Windows, que é o que
funcionou na máquina onde isso foi construído); em outro sistema, o
equivalente pode ser `python3` ou só `python`.

## As cinco telas e de onde vem cada número

Todo número de comportamento de pagamento de cliente (média de atraso,
desvio-padrão, se piorou, sazonalidade, índice de risco) nasce em **uma função
só**: `analisarCliente(cliente)`, guardada em `ANALISES[codigo]`. Isso é o ponto
mais importante deste arquivo — leia a seção "A regra de ouro" abaixo antes de
adicionar qualquer conta nova sobre cliente.

| Tela | Hash | O que responde | Função principal |
|---|---|---|---|
| Hoje | `#hoje` (padrão) | Quem cobrar primeiro | `calcularLinhasHoje()` / `renderHoje()` |
| Risco por cliente | `#risco` | Quem é risco de crédito de verdade | `analisarCliente()` / `renderRisco()` |
| Previsão de caixa | `#previsao` | Quanto entra nas próximas 4 semanas | `calcularPrevisaoCaixa()` / `renderPrevisao()` |
| Régua de cobrança | `#regua` | O que escrever pra cada cliente | `escolherTom()` + `gerarTextoCobranca()` / `renderRegua()` |
| Relatório da semana | `#relatorio` (5ª aba da navegação) | Resumo de 4 minutos pra diretoria | `gerarRelatorioSemanal()` / `renderRelatorio()` |
| Ficha do cliente | `#ficha-<código>` | Raio-x de um cliente | `renderFicha(codigo)` |

## A regra de ouro: uma conta, um lugar

Durante um bom tempo deste projeto, a tela Hoje calculava a própria média histórica de
atraso de cada cliente, e a tela Risco calculava a dela — as duas com o mesmo
nome de conceito ("média histórica"), mas fórmulas diferentes (Hoje usava todo o
histórico; Risco descontava meses sazonais). Numa auditoria de revisão, isso quase passou
batido porque o arredondamento fazia as duas mostrarem o mesmo número por
coincidência — até que um cliente (Casa de Carnes Bom Corte) tinha sazonalidade
detectada, e as contas discordavam por baixo do capô (14,0 vs. 13,5 dias), prontas
para um dia aparecer diferente na tela sem ninguém entender por quê.

A correção foi: Hoje passou a **ler** `ANALISES[codigo].meanHist` /
`.stdHist` / `.temHistorico`, em vez de calcular a própria versão. Ver
`calcularLinhasHoje()` — o comentário lá em cima explica isso com mais detalhe.

**A regra pra qualquer coisa nova:** se você vai mostrar algo sobre o
comportamento histórico de um cliente (atraso médio, variação, se piorou, se
parou de comprar, participação no faturamento, ocupação de limite), primeiro
olhe se já existe em `ANALISES[codigo]`. Se existir, use. Se não existir e
parecer que devia, é sinal de que falta um campo em `analisarCliente` — acrescente
o campo lá (é só adicionar uma chave no `return` do fim da função) e leia ele
das outras telas, em vez de calcular de novo em cada lugar que precisar. Foi
assim que a Previsão de caixa e a Régua de cobrança nasceram
sem duplicar nada: elas leem `ANALISES` e `linhasHoje`, não recalculam.

Mesma lógica vale para os números da tela Hoje (`totalVencidoCentavos`,
`totalAbertoCentavos` etc.) — foram extraídos pra `calcularResumoHoje()`
exatamente pra o Relatório da semana poder ler sem recalcular. E os totais da
Previsão (`totalNaive`, `totalCentral`, `diferenca`) moraram um tempo como
variável local dentro de `renderPrevisao()` até o Relatório precisar deles — hoje
vivem dentro do objeto que `calcularPrevisaoCaixa()` devolve, exatamente pelo
mesmo motivo.

## A camada visual (rodada de redesign — "Painel de vidro")

O projeto passou por um redesign visual completo depois de fechado
funcionalmente. **Nada de conta ou de conteúdo mudou nessa rodada** — só a
camada de apresentação (CSS, estrutura de HTML, e algumas funções de
renderização que reorganizam texto já calculado). Se você está lendo isto
numa rodada futura, o que segue é o estado atual dessa camada, não um
histórico pra desfazer.

- **Direção escolhida: vidro/glassmorphism escuro** (das três propostas, o
  dono do projeto escolheu a "A — Painel de vidro"). Gradiente de fundo de
  cima a baixo, painéis com `backdrop-filter: blur()` (com fallback em
  `@supports not (backdrop-filter)` pra fundo sólido semi-opaco, já que nem
  todo navegador corporativo tem isso), e brilho (`box-shadow` com cor)
  reservado só pros elementos principais de cada tela — não é decoração
  espalhada em tudo.
- **Duas fontes variáveis (Inter + Space Grotesk) embutidas como base64** dentro
  de `@font-face` no próprio `<style>`, com `unicode-range` cobrindo
  Latin-1 (acentos do português). Isso existe pra manter o requisito de "abre
  sem internet" mesmo tendo tipografia com mais personalidade — nunca troque
  isso por um `<link>` pro Google Fonts, quebra o app pra quem abrir sem rede.
- **Cada uma das 5 telas tem uma "coisa dominante" no topo** (`.hero-numero`):
  Hoje mostra o vencido em aberto, Risco o valor total em risco, Previsão a
  diferença planilha-vs-Central, Régua não tem (é lista+painel, não número),
  e o Relatório reaproveita o mesmo padrão visual com o vencido em aberto +
  risco total + previsão, pra fechar a sensação de que é um sistema só, não
  5 páginas soltas. Se criar uma tela nova, dê a ela uma dessas — não deixe
  o topo só com título.
- **Hoje ganhou uma seção de "achados"** (`escolherAchados()`) que sobe pro
  topo os 2-3 pontos mais importantes que hoje só apareciam em Risco (os dois
  casos especiais com nome, mais o cliente de risco mais alto). Não recalcula
  nada — só lê `ANALISES`/`LISTA_RISCO` e escolhe o que mostrar.
- **Conteúdo longo foi escondido por trás de `<details>`, não apagado.** Os
  seis fatores do índice (Risco e Ficha) e as notas de método de cada tela
  ficam fechados por padrão e abrem no clique. A frase de cada cliente em
  Hoje e o texto de alerta em Risco foram encurtados pra 1-3 linhas, mas todo
  número, link e explicação que existia antes ainda existe — só que o texto
  completo mora dentro do `<details>` (`alerta.texto`) e um resumo mais curto
  (`alerta.resumo`, campo novo em `gerarAlertaPorExtenso`) fica visível direto.
- **Régua de cobrança virou mestre-detalhe.** Antes cada cliente tinha um
  card inteiro (tom, canal, texto, botões) aberto ao mesmo tempo — virava uma
  tela enorme. Agora `renderRegua()` desenha uma lista compacta
  (`#lista-regua-mestre`) e delega o painel de composição de UM cliente por
  vez pra `renderDetalheRegua()`, dentro de `#regua-detalhe`. O cliente
  selecionado mora em `CLIENTE_SELECIONADO_REGUA` (variável global, seta pelo
  clique na lista ou pelo hash `#regua-<codigo>`, usado pelos links "Cobrar →"
  de Hoje). Nenhuma lógica de tom/canal/texto/registro mudou — só onde ela é
  desenhada na tela.
- **Telas operáveis, não só legíveis.** Hoje e Risco têm busca, filtro
  (chips) e ordenação (`ESTADO_HOJE` / `ESTADO_RISCO`, funções
  `linhasFiltradasHoje()` / `listaFiltradaRisco()`) — sempre filtrando uma
  **cópia** da lista original, nunca mutando `linhasHoje` / `LISTA_RISCO`. A
  opção "prioridade (padrão)" de ordenação não ordena de novo — ela só
  devolve a lista na ordem em que `calcularLinhasHoje()` já a construiu, então
  se um dia mudar o critério de prioridade, mude só lá, uma vez.
- **Um botão principal por card, o resto discreto.** Convenção:
  `.botao-principal` (preenchido, é a ação mais provável daquele card —
  "Cobrar →" em Hoje, "Abrir ficha completa →" em Risco, "Marcar como cobrado
  agora" em Régua) e `.botao-secundario` / `.botao-fantasma` (contorno ou só
  texto, pra ação alternativa). Se um card só tem UMA ação, ela é
  `.botao-principal` — não sobra ação "secundária" sozinha com aparência fraca.
- **Dinheiro em texto corrido ganha cor própria.** No Relatório da semana,
  todo valor monetário dentro do texto (não nos números grandes) passa pela
  função `dinheiro(texto)`, que envolve o valor num `<span class="dinheiro">`
  — é a única forma de destaque de cor que existe pra número dentro de frase,
  e existe só ali. Se adicionar texto corrido com valor em outra tela, reuse
  essa função em vez de inventar uma nova classe.

### Segunda rodada — densidade (o "piso de vidro" ficou, o excesso saiu)

Depois da rodada acima, o dono do projeto abriu as 5 telas e achou pesado
demais: fonte grande de mais pro navegador comum, muita coisa antes do
primeiro cliente, cartão da fila com informação empilhada, lista de 12
clientes em Risco virando 12 cartões grandes em vez de uma tabela. Esta
rodada corrigiu isso — de novo, sem tocar em nenhuma conta.

- **A navegação virou coluna lateral**, não mais cabeçalho + abas
  horizontais. `<aside class="barra-lateral">` tem só o nome da empresa, os
  links das 5 telas (`nav.abas`, mesmos `data-aba` de sempre — só o CSS
  mudou de linha horizontal pra coluna) e a data de referência no rodapé,
  sem frase explicando o que a data significa. Em telas estreitas
  (`@media max-width:720px`) ela colapsa de volta pra uma barra horizontal
  no topo.
- **A fonte de destaque trocou de Space Grotesk pra Manrope** (mesmo
  mecanismo: variável, embutida em base64 dentro de `@font-face`, sem
  depender de internet) — troca de gosto do dono do projeto, não defeito.
  Se trocar de novo, o padrão é: baixar o woff2 do subset "latin" do Google
  Fonts, converter pra base64, e substituir o bloco `@font-face` + o valor
  de `--fonte-display`. Os números grandes (`.hero-numero .valor`,
  `.diferenca-hero .valor`) também caíram de ~42-44px pra ~28-29px — não é
  mais pensado como "telão", é pensado como sistema de navegador comum;
  quem quiser maior no telão dá zoom.
- **Hoje: hero-numero e achados viraram UM painel só** (`.topo-tela` com
  `vidro brilho`), não mais 4 cartões de vidro lado a lado. Os achados
  perderam a classe `vidro` e o fundo próprio — agora são blocos de texto
  com uma borda fina à esquerda, dentro do mesmo painel do número grande.
  Risco fez o mesmo, só que do lado direito entra um gráfico
  (`construirGraficoRiscoRanking`) em vez de achados.
- **Título + legenda repetidos no topo de cada tela foram cortados.**
  Hoje, Risco, Previsão e Relatório tinham um `<h2 class="titulo-fila">` +
  `<p class="legenda-fila">` repetindo o nome da tela (redundante com o link
  já ativo na barra lateral) antes de chegar no que importa. Em Régua, a
  explicação de como o registro funciona não foi apagada — virou
  `<details class="metodo">` fechado por padrão, igual às outras telas.
- **Cartão da fila (Hoje) agora tem 4 fileiras fixas, sempre nessa ordem**:
  (1) posição + nome + selos + valor; (2) categoria/região + contato +
  telefone (`l.cliente.contato`/`l.cliente.telefone`, os mesmos campos que a
  Ficha já usava); (3) a frase; (4) os botões. A barra de risco e a
  contagem de títulos em linha própria saíram — a posição na fila já entrega
  a mesma informação de prioridade. **O cartão fica mais simples conforme
  desce na fila**: a partir do 4º cliente (`i >= 3` em `renderHoje()`), a
  classe `frase-1` limita a frase a 1 linha (`-webkit-line-clamp`) e os
  botões de ação virão só links (`.botao-fantasma` no lugar de
  `.botao-principal`). Isso é feito só na variável `simplificado` dentro do
  loop — não duplica template.
- **Risco: lista de cartões virou tabela** (`table.tabela-risco`, dentro do
  `.tabela-scroll` de sempre). O detalhe dos seis fatores **saiu da lista**
  — ele já existe, sozinho, na Ficha (`renderFicha`, `details.detalhe-risco
  open`); manter nos dois lugares era o tipo de duplicação que a "regra de
  ouro" deste arquivo pede pra evitar. Os dois casos com nome + os clientes
  sazonais ganharam um painel próprio acima da tabela
  (`escolherCasosRisco()`, achados-style, sem limite de 3 como em Hoje —
  mostra todos os casos que tiverem flag) e o gráfico de ranking
  (`construirGraficoRiscoRanking`) mostra de uma vez quem deve mais (largura
  da barra) e o nível de risco (cor da barra), sem precisar ler a tabela
  inteira.
- **Índice de risco na tabela usa uma casa decimal (`toFixed(1)`), não
  zero.** Isso já é jurisprudência deste arquivo (ver "O que parece defeito
  e não é" mais abaixo e a seção "a regra de ouro"): arredondar pra inteiro
  pode empurrar o número mostrado pra cima do limiar de faixa (ex.: índice
  real 14,8 — cor verde/baixo — mostrando "15" ao lado de uma cor que parece
  discordar). Não arredonde mais que isso num pill de índice.
- **Ficha: o gráfico de atraso mês a mês só aparece se o cliente tiver
  desvio-padrão histórico ≥ 3 dias** (`a.temHistorico && a.stdHist >= 3`).
  Abaixo disso a linha é reta o bastante pra não mostrar nada (caso raiz:
  Adega Serra Azul, desvio de 1,4 dias) — nesses casos entra uma frase
  curta no lugar do gráfico, explicando por que ele não está ali. Histórico
  curto demais (`!a.temHistorico`) também pula o gráfico, com frase própria.
  Isso é decisão de exibição, não muda `a.stdHist` nem nenhum outro número.
- **Relatório: centralizado com `max-width:760px; margin:0 auto` num wrapper
  `.relatorio-centro`** que envolve o hero, o botão de copiar e o corpo do
  texto — antes cada um desses três blocos vivia solto direto dentro de
  `<main>`, encostado à esquerda.
- **Todo `<select>` do sistema ganhou fundo escuro nas opções.** Bug real:
  `color-scheme` nunca tinha sido declarado, então o menu nativo do
  `<select>` (Tom/Canal na Régua, os "ordenar por" de Hoje/Risco) abria com
  o esquema de cores claro do sistema operacional — texto claro do app
  sobre fundo branco do menu, quase ilegível. Corrigido com
  `color-scheme:dark` no `html` + `select option{ background-color:... }`
  como reforço pros motores que não respeitam `color-scheme` no popup do
  select. Se algum select novo for adicionado, ele já herda a correção sem
  precisar repetir nada.

## Decisões e o porquê (não redecida sem entender por quê primeiro)

- **A data de "hoje" nunca é `new Date()`.** É sempre `DADOS.referencia`, lida da
  aba `Leia-me` da planilha (`REF` no código, `paraData(DADOS.referencia)`). Toda
  conta de atraso, dias-desde-contato, janela de previsão etc. trava nessa data.
  Se você usar o relógio real da máquina em algum lugar novo, a régua de 48 horas
  (ver abaixo) para de funcionar sem avisar.

- **Valor monetário é sempre inteiro em centavos** (`valor_centavos`,
  `*_Centavos` nas variáveis). Nunca guarde valor arredondado — arredonde só na
  hora de formatar pra tela. Duas funções de formatação, com papéis diferentes:
  - `formatoReal(centavos)` — com centavo. Usa pra qualquer valor **fechado**
    (valor de título, soma de títulos, saldo em aberto real).
  - `formatoRealCurto(centavos)` — arredondado, sem centavo. Usa pra qualquer
    valor que é **estimativa** (Previsão de caixa: cenário central, conservador,
    otimista, diferença) **e** pra números de **indicador/card de resumo no topo
    de tela** (o hero-numero de cada tela, os 3 cards do topo da Ficha, o valor
    em risco de cada linha da tabela de Risco) — esses últimos são valores fechados,
    mas perderam o centavo por espaço mesmo, não por serem estimativa: numa
    auditoria de tela apertada, o texto com centavo ficava com ~2px de
    sobra dentro do card, praticamente colado na borda. Se um card novo desse
    tipo (número grande, card pequeno) for criado, considere `formatoRealCurto`
    ali também, mesmo que o valor seja fechado.

- **Nunca escreve em `Base_bruta.xlsx`.** Nem o registro de cobrança, nem nada.
  Se algum dia surgir vontade de "salvar direto na planilha", pare e pergunte —
  isso quebra a premissa de que a planilha é gravação zero.

- **Registro de cobrança não usa `localStorage`.** Foi uma escolha explícita do
  dono do projeto (perguntada e respondida quando a Régua de cobrança foi
  construída): ele preferiu
  export/import manual de um `.json` a persistência automática silenciosa, porque
  queria controle e portabilidade do histórico, não um estado escondido no
  navegador. `REGISTRO` (variável em `central_template.html`) vive só na memória
  da sessão. Os botões "Exportar registros" / "Importar registros" (tela Régua)
  são o único jeito de levar isso de uma sessão pra outra. Não reintroduza
  `localStorage` sem perguntar de novo — a resposta já foi dada uma vez.

- **A hora do registro de cobrança usa a data da referência, não o relógio
  real** (`agoraNaBase()`). Isso é de propósito: se um registro nascesse com a
  data real do computador (que pode estar semanas depois da data de referência da
  base), ele apareceria "no futuro" em relação a `REF`, e a regra das 48 horas
  (cliente cobrado recentemente desce na fila de Hoje) simplesmente não pegaria —
  o cálculo de dias-desde-contato ficaria negativo ou absurdo. Só a hora do dia
  (não o dia) usa o relógio real, e só pra ordenar registros feitos na mesma
  sessão — nenhuma conta olha pra essa parte.

- **A redação da Régua de cobrança e do Relatório não usa IA nem serviço
  externo.** Todo texto é montado por template (`CONSTRUTORES_TOM`,
  `montarTextoFinal`, `gerarTextoCobranca`, `gerarRelatorioSemanal`) a partir de
  números já calculados. Esse bloco está isolado e comentado de propósito (ver
  "REDAÇÃO DA COBRANÇA (SEM IA)" em `central_template.html`) para o dia em que
  alguém quiser trocar por um modelo de linguagem — nesse dia, é só substituir o
  corpo dessas funções; o resto da tela (seleção de tom, registro, fila) não
  precisa mudar. Não chame nenhum serviço de rede daqui sem que o dono do projeto
  peça explicitamente — é requisito duro (rodar offline).

- **A Central nunca manda mensagem por si.** Ela redige e copia
  (`navigator.clipboard`); quem manda o WhatsApp ou e-mail é a pessoa. Não
  integre com nenhuma API de envio sem perguntar.

- **Sazonalidade é detectada por regra, não hardcoded.** Um mês só conta como
  "padrão de calendário" se aparecer elevado (≥ `LIMIAR_SAZONAL_DIAS` = 5 dias
  acima do resto) em **todos** os anos em que tem dado, exigindo pelo menos 2 anos
  diferentes. Constantes em `analisarCliente`, seção "sazonalidade". Isso existe
  porque cobrar como risco um atraso que só é sazonal (ex.: Congelados Polo Norte
  atrasa todo janeiro/fevereiro, todo ano) é alarme falso.

- **"Mudou de patamar" (deterioração) exige piora grande em dias E grande frente
  ao próprio desvio-padrão do cliente** (`LIMIAR_DELTA_DIAS` = 7 dias **e**
  `LIMIAR_Z_DELTA` = 1.3 desvios-padrão, ambos ao mesmo tempo). Um cliente que já
  atrasava muito e variava muito (ex.: 35 → 42 dias, com desvio de 10+) não deve
  disparar isso — só quem sai do próprio padrão de forma que seria estranha pra
  ele mesmo.

- **"Recente" = últimos 3 meses corridos completos antes da referência**
  (`RECENTE_MESES = 3`, janela `[recentesIni, recentesFim)`), usado em quase toda
  comparação de tendência (deterioração de pagamento, queda de compras, cenário
  da Previsão). O mês da própria data de referência fica de fora por ser parcial.

- **Os dois casos "com nome e sobrenome" (pedidos quando a tela Risco por
  cliente foi criada) são detectados por
  condição, não por nome de cliente fixo.** `apareceMasNaoRisco` (cliente
  crônico mas estável — hoje é a Adega Serra Azul) e `nuncaFalhouPiorando`
  (cliente que nunca falhou mas está piorando — hoje é o Supermercado Vila Nova)
  são flags calculadas a partir de `nHist`, `stdHist`, `deterioracao.piorou` etc.
  **Quando a base for atualizada, os clientes que se encaixam nesses padrões
  podem ser outros.** Não escreva em nenhum lugar novo "o Vila Nova é o caso tal"
  como se fosse permanente — o texto da tela já é gerado dinamicamente a partir
  da flag; só cuidado se algum dia escrever prosa solta (relatório, e-mail) citando
  esses casos por nome.

- **O índice de risco (0–100) é a soma de seis fatores, com pesos fixos**
  (25/25/15/15/10/10 — gravidade do vencido hoje, mudança de padrão,
  imprevisibilidade, queda de compras, peso no faturamento, ocupação de limite).
  Faixas de leitura: `< 15` baixo, `15–35` moderado, `≥ 35` alto
  (`faixaIndice`). Cada fator carrega a própria frase de justificativa — é assim
  que a tela cumpre "índice fechado ninguém confia".

- **Valor em risco = saldo em aberto × índice / 100.** Não é o índice puro, e
  não é só o valor vencido — é o saldo em aberto (vencido + a vencer) inteiro,
  pesado pelo risco. É por isso que a lista de Risco não fica na mesma ordem que
  a lista de Hoje.

- **A Previsão de caixa reaproveita `ANALISES` e o índice de risco de cada
  cliente** — não inventa um risco novo pra decidir a chance de um título entrar.
  A probabilidade de entrada (`probabilidadeEntrada`) cai com os dias já vencidos
  hoje e com o índice de risco (mesmo índice da tela Risco), nunca chega a 0% nem
  100% (piso 5%, teto 96% — isso é de propósito: nunca escrevemos "impossível" ou
  "certeza" sobre pagamento de cliente). Cenário conservador/otimista usa o pior
  e o melhor dia que o cliente **já praticou** — o período recente, se ele estiver
  piorando (mesmo critério de `deterioracao.piorou`), senão os 24 meses inteiros.
  A faixa conservador–otimista só é desenhada **acumulada**, nunca semana a
  semana — semana a semana ela se cruza (dinheiro que atrasa não desaparece, só
  muda de semana), e isso está explicado na própria tela, não só aqui.

## Armadilhas específicas da camada visual

- **`<a>` usado como botão fica sublinhado se você esquecer
  `text-decoration:none`.** A regra genérica `a{ color:var(--primario); }`
  no topo do `<style>` não reseta sublinhado — só a cor. Isso já causou um
  bug real (sublinhado aparecendo em botões que deviam parecer botão, não
  link) até a regra `.botao-principal, .botao-secundario, .botao-fantasma`
  ganhar `text-decoration:none` explícito. Se criar uma classe de botão nova
  a partir de um `<a>`, lembre de repetir isso — não é automático.
- **Números de posição (`.posicao`, "1" "2" "3"...) usam a fonte de destaque
  (`--fonte-display`)**, e dependendo da fonte escolhida o algarismo "1" pode
  ter uma base/serifa que parece um sublinhado em capturas de tela pequenas
  ou comprimidas. Antes de "corrigir" isso, olhe a mesma tela num print maior
  (ou com `--force-device-scale-factor=2`) pra confirmar se é sublinhado real
  (bug) ou só o desenho do algarismo (não é).
- **Item de grid com SVG dentro não encolhe sozinho em tela estreita.**
  `.topo-tela` é `display:grid`; por padrão, um item de grid tem
  `min-width:auto`, que respeita o tamanho mínimo do conteúdo — um `<svg>`
  com `viewBox` largo (o gráfico de Risco, por exemplo) empurra a coluna
  pra ser pelo menos tão larga quanto o próprio gráfico, e a página inteira
  ganha uma barra de rolagem horizontal no mobile, mesmo com
  `grid-template-columns:1fr` no media query. A correção foi
  `.topo-tela > *{ min-width:0; }` + `.topo-tela svg{ max-width:100%; height:auto; }`,
  e `body{ overflow-x:hidden; }` como cinto de segurança. Se um gráfico novo
  for colocado dentro de um grid/flex, lembre do `min-width:0` no item —
  não é automático, e o sintoma (barra de rolagem horizontal) só aparece
  testando largura estreita de verdade (truque do iframe, não
  `--window-size`).
- **Toda tela precisa da mesma "coisa dominante" no topo** (ver seção
  anterior) — se adicionar uma tela nova ou remover a única do Relatório,
  ela vai ficar visualmente diferente das outras 4 e quebrar a sensação de
  sistema único. Isso não é bug de renderização, é fácil de esquecer ao
  copiar a estrutura de uma tela pra outra.

## O que parece defeito e não é

- **Texto "cortado" ao testar largura de celular.** O Chrome/Edge headless (usado
  pra tirar print automatizado) tem um piso de ~496px de largura de janela —
  pedir `--window-size=390,...` não funciona, ele sempre renderiza a 496px e
  qualquer print salvo em 390px vira um recorte, não o app de verdade. **Pra
  testar largura estreita de verdade**, carregue a página dentro de um
  `<iframe style="width:390px;...">` (o iframe tem viewport próprio, imune a esse
  piso) e tire o print da página que contém o iframe. Foi assim que se descobriu
  que a maior parte dos "defeitos" de mobile dessa auditoria eram falso alarme, e que
  os dois reais (tabela larga vazando e a falta de `<meta name="viewport">`) só
  apareceram depois de corrigir o método de teste.

- **Dois números parecidos em telas diferentes, print tirado em momentos
  diferentes.** Como é um arquivo local, o navegador não recarrega sozinho
  quando o `central.html` é regenerado — se uma aba ficar aberta de antes de uma
  edição, ela mostra o estado antigo. Antes de caçar um "número que não bate
  entre telas", confirme que a página foi recarregada (F5) depois da última
  edição, e confirme visualmente que é o **mesmo cliente** nas duas capturas —
  clientes com índice ou posição parecida são fáceis de trocar ao comparar prints
  (ex.: Atacado São Jorge = 36,9 fica logo acima de Supermercado Vila Nova = 51,9
  na lista de Risco).

- **Procurar `NaN` ou `undefined` no código-fonte da página dá falso
  positivo.** A palavra `undefined` aparece várias vezes dentro do próprio
  `<script>` como palavra-chave normal do JavaScript (`c.valor!==undefined`,
  por exemplo) — isso não é um erro renderizado, é só o texto do programa. Já
  aconteceu de uma checagem automatizada contar "12 de 12 fichas com
  `undefined`" e o susto ser à toa. Pra checar de verdade, procure a string no
  **texto que a página mostra** (Ctrl+F na página aberta, ou um dump de DOM já
  processado — nunca "Ver código-fonte" / o `<script>` crú).

- **Duas telas mostrando o mesmo número por coincidência de arredondamento não
  prova que a conta é a mesma por baixo.** Foi exatamente esse disfarce que
  escondeu o bug real descrito em "A regra de ouro" acima. Se for comparar
  duas telas a fundo, compare o valor **sem arredondar** (adicione um
  `console.log` temporário ou leia a variável direto), não só o texto exibido.

## O que não muda sem perguntar antes

Isto é o requisito duro do projeto, revalidado em mais de uma rodada:

1. Roda com um comando só, numa máquina limpa: sem internet, sem instalar
   pacote, sem conta em lugar nenhum, sem IA.
2. `Base_bruta.xlsx` nunca é escrita.
3. Valor monetário é inteiro em centavos internamente; estimativa exibida sem
   centavo, valor fechado exibido com centavo (com a exceção documentada acima
   pros cards-indicador de topo de tela).
4. `REF` (data de "hoje") vem da aba `Leia-me`, nunca de `new Date()`.
5. Registro de cobrança não persiste automaticamente (sem `localStorage`); só
   export/import manual de `.json`.
6. Redação de texto (Régua, Relatório) não chama IA nem serviço externo — é
   template sobre número já calculado, num bloco isolado pra facilitar troca
   futura.
7. A Central nunca envia mensagem — só redige e copia.

Se uma tarefa nova exigir quebrar algum desses pontos, isso é motivo de parar e
perguntar, não de decidir sozinho.

## Passo a passo: trocando pela planilha nova

Nada nisto abaixo precisa de ajuste manual quando a base cresce: as janelas de
tempo ("recente" = 3 meses, faturamento = 12 meses, a janela de 4 semanas da
Previsão) são todas calculadas a partir de `DADOS.referencia`, e a lista de
clientes/títulos vem inteira de `DADOS.clientes`/`DADOS.titulos` — se a
planilha nova tiver mais um mês de título, cliente novo, ou até cliente que
saiu da carteira, o código já lida com isso sozinho. O que pode mudar sozinho,
como consequência, são **os resultados**: quem é "risco alto", quem se encaixa
nos dois casos especiais, a ordem da fila — isso é esperado, não é bug.

1. **Substitua o arquivo.** Coloque a planilha nova no lugar de `Base_bruta.xlsx`
   (mesmo nome, mesma pasta). Ela precisa ter as mesmas 4 abas com os mesmos
   nomes de coluna (`Leia-me`, `Clientes`, `Títulos`, `Cobranças` — os nomes
   exatos de coluna que `build_data.py` espera estão ali mesmo, um
   `r["Nome da Coluna"]` por campo; se um nome de coluna mudou, o script quebra
   com um `KeyError` claro apontando qual).
2. **Regenere o JSON:**
   ```
   py -3 build_data.py
   ```
   Confirme na saída que `referencia` mudou pra data nova, e que `clientes` /
   `titulos` / `cobrancas` bateram com o que você espera da planilha nova (a
   aba `Leia-me` da própria planilha diz quantos títulos e clientes ela tem —
   confira contra isso).
3. **Regenere o HTML:**
   ```
   py -3 build_html.py
   ```
4. **Abra `central.html` recarregando de verdade** (não uma aba antiga).
5. **Confira que continuou fechando**, nesta ordem:
   - **Bateu com a planilha, por um caminho independente.** Não confie no
     próprio HTML pra validar o próprio HTML. Abra um Python novo e recalcule
     por fora, direto do Excel, pelo menos: total de títulos, total vencido,
     total em aberto, quantos clientes têm vencido hoje — e compare com os 4
     cards da tela Hoje. Isso já foi feito numa auditoria de revisão deste
     projeto (a conta em si estava certa; o valor de ter feito por fora foi
     confirmar).
   - **Bateu entre telas.** Pra cada cliente que aparecer na tela Risco e
     também tiver ficha, o índice mostrado na lista e o índice mostrado na
     ficha têm que ser **idênticos** (são o mesmo `ANALISES[codigo].indice` —
     se divergirem, algo foi duplicado por engano). Mesma checagem vale pra
     valor vencido / saldo em aberto entre Hoje, Risco e Ficha.
   - **Sem `NaN` nem `undefined` na tela.** Abra o HTML final e procure essas
     duas strings no texto renderizado (não no `<script>`) — se aparecerem,
     alguma conta não tem dado suficiente e não está tratando o caso de
     histórico curto.
   - **Os dois casos especiais ainda fazem sentido.** Confira quem hoje se
     encaixa em "aparece na lista mas não é risco" e em "nunca falhou, e por
     isso ninguém viu" (as duas etiquetas amarelas na tela Risco) — pode não
     ser mais Adega Serra Azul / Supermercado Vila Nova. Se aparecer alguém
     novo nessas etiquetas, isso é informação real pra levar pro financeiro, não
     bug.
   - **Mobile de verdade.** Se for revisar layout em tela estreita, use o
     truque do iframe descrito acima — não `--window-size` direto.
   - **Não sobrou nenhum arquivo de teste na pasta.** Se você (ou o Claude que
     estiver ajudando) usou capturas de tela ou dumps de HTML pra conferir
     alguma coisa, apague os arquivos temporários antes de terminar — a pasta
     tem que voltar a ter só os arquivos de projeto.

Se alguma dessas conferências falhar, o conserto é sempre no `central_template.html`
(ache a causa raiz antes de remendar a aparência) seguido de `py -3 build_html.py`
de novo — nunca editando `central.html` direto.
