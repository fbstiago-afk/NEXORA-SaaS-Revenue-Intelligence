# -*- coding: utf-8 -*-
"""Gera a documentação Markdown do projeto NEXORA. Uso: python gerar_docs.py <pasta_NEXORA_local> <pasta_dados>"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
from pbip_model import T, REL, CALC_TABLES
from pbip_measures import MEASURES

OUT, DATA = sys.argv[1], sys.argv[2]
DOC = os.path.join(OUT, "Documentation")
os.makedirs(DOC, exist_ok=True)


def w(name, txt):
    open(os.path.join(DOC, name), "w", encoding="utf-8").write(txt.strip() + "\n")


# --------------------------------------------------------------- inventário de arquivos
rows = []
for f in sorted(os.listdir(DATA)):
    if f.endswith(".csv"):
        p = os.path.join(DATA, f)
        n = sum(1 for _ in open(p, encoding="utf-8")) - 1
        rows.append((f, n, os.path.getsize(p) / 1024 / 1024))
inv = "| Arquivo | Linhas | Tamanho (MB) |\n|---|---:|---:|\n" + "\n".join(f"| {a} | {b:,} | {c:,.2f} |".replace(",", ".") for a, b, c in rows)
tot = sum(r[1] for r in rows)
inv += f"\n| **Total** | **{tot:,}** | **{sum(r[2] for r in rows):,.1f}** |".replace(",", ".")

# --------------------------------------------------------------- README_BASE
w("README_BASE_NEXORA.md", f"""
# README — Base sintética NEXORA SaaS Revenue Intelligence

**Empresa:** NEXORA (fictícia) · SaaS B2B de gestão comercial, produtividade e automação · *Connect. Automate. Grow.*
**Período:** 01/01/2024 a 31/10/2026 · **Seed:** 20261009 (reprodutível) · **Formato:** CSV UTF-8, vírgula, datas `YYYY-MM-DD`, decimal com ponto.

## Como foi gerada
`Scripts/gerar_base_nexora.py` (Python + pandas + numpy) simula a empresa **mês a mês, cliente a cliente** — não são valores aleatórios independentes:

1. **Aquisição**: volume mensal com crescimento 2024 → 2025 → 2026, sazonalidade e mix de canal por ano (mídia paga ganha peso em 2026).
2. **Perfil**: canal → porte → plano → ciclo (mensal/anual) → segmento; cada conta recebe uma **adoção latente** que depende do canal (Indicação ↑, Meta/Google ↓), segmento (Varejo B2B ↓), plano e ano do cohort (2026 ↓).
3. **Uso** (logins, usuários ativos, automações, integrações, funcionalidades) deriva da adoção, que evolui como passeio aleatório (integração empurra para cima).
4. **Health Score** (0–100) = frequência de login (25) + % usuários ativos (20) + funcionalidades (15) + automações (10) + integração (10) + suporte/CSAT (10) + adimplência (10) ± tendência de uso. Faixas: Saudável ≥75, Atenção 55–74, Risco 35–54, Crítico <35.
5. **Churn** é uma *hazard* mensal por plano multiplicada por adoção, uso nos primeiros 30 dias, integração, canal, segmento, CSAT baixo, inadimplência, ano (Starter 2026) e cohort 2026. Contratos anuais só cancelam na renovação.
6. **Expansão/contração**: usuários extras, add-ons, upgrades e downgrades com probabilidades por plano e adoção; choque temporário de contração em abr–jun/2025.
7. **Reativação**: clientes cancelados (exceto “Encerramento”) podem voltar entre 3 e 15 meses depois.
8. **Funil, marketing e CAC**: leads/MQL/SQL/trials são gerados a partir das taxas de conversão de cada canal; o investimento mensal por canal é alocado aos clientes adquiridos (Σ custo alocado = investimento).
9. **Financeiro**: faturas mensais/anuais, implantação e treinamento (não recorrentes), descontos, atraso, inadimplência e estornos.

## Booking ≠ Billing ≠ Revenue ≠ MRR
| Conceito | Onde está | Regra |
|---|---|---|
| **Booking** | `fAssinaturas[ValorContrato]` | Valor do contrato na assinatura (12× MRR no anual, 1× no mensal) |
| **Billing** | `fFinanceiro[ValorLiquido]` | Faturas emitidas (anual faturado antecipadamente; implantação e treinamento à parte) |
| **Revenue** | `fSnapshotMRR[ReceitaRecorrenteReconhecida]` + não recorrente | Receita reconhecida no mês |
| **MRR** | `fSnapshotMRR[MRR]` | Receita recorrente mensal contratada no fim do mês (líquida de desconto) |

## Arquivos, linhas e tamanhos
{inv}

## Padrões analíticos inseridos deliberadamente
1. Aumento de churn do **Starter em 2026**. 2. **Indicação** com CAC baixo e melhor retenção. 3. **Google Ads** (e Meta) com CAC crescente em 2026. 4. **Integrações** associadas a maior retenção. 5. **Baixo uso nos primeiros 30 dias** associado a churn. 6. **Pro** concentra Expansion MRR. 7. **Enterprise** com churn baixo e CAC alto. 8. **Varejo B2B** cresce em clientes, mas com CAC maior, desconto maior e churn maior (rentabilidade ruim). 9. **Cohorts de 2026** com retenção abaixo da média. 10. **Pico temporário de Contraction MRR** em abr–jun/2025. 11. Clientes com **potencial claro de upgrade** (`fUsoProduto[PotencialUpgrade]`). 12. Clientes **cancelados e reativados**.

As relações são estatísticas, não determinísticas (há ruído em todas as etapas). Evidências numéricas em `VALIDACAO_BASE_NEXORA.md`.
""")

# --------------------------------------------------------------- MODELO RELACIONAL
tabdocs = []
for tbl, csv, desc, cols in T:
    tabdocs.append(f"### {tbl}\n{desc}\n\n| Coluna | Tipo | Observação |\n|---|---|---|\n" + "\n".join(
        f"| {c} | {t} | {'chave' if 'k' in f.split(';') else ('oculta' if 'h' in f.split(';') else '')} |" for c, t, f in cols))
for tbl, (desc, cols, dax) in CALC_TABLES.items():
    tabdocs.append(f"### {tbl} (tabela calculada)\n{desc}\n\n| Coluna | Tipo |\n|---|---|\n" + "\n".join(f"| {c} | {t} |" for c, t, f in cols))
tabdocs.append("### dCohort (Power Query)\nMeses de aquisição distintos de dCliente; conecta dCliente e fCohortMensal.\n\n| Coluna | Tipo |\n|---|---|\n| CohortMes | date |\n| Cohort | text |\n| CohortIdx | int |\n| CohortAno | int |")
rels = "| De (N) | Para (1) |\n|---|---|\n" + "\n".join(f"| {a} | {b} |" for a, b in REL)
w("MODELO_RELACIONAL_NEXORA.md", f"""
# MODELO RELACIONAL — NEXORA

Modelo estrela/floco controlado: dimensões conformadas (`dCalendario`, `dCliente`, `dPlano`, `dCanalAquisicao`, `dSegmento`, `dPorte`, `dCohort`) filtram os fatos em **direção única**, sem relações muitos-para-muitos, sem filtros bidirecionais e sem relações entre fatos.

```
dCanalAquisicao ─┐          ┌─ fSnapshotMRR (cliente×mês)      dCalendario ─► todos os fatos datados
dSegmento ───────┼─► dCliente ┼─ fMovimentoMRR (cliente×mês×tipo)  dPlano ─► fSnapshotMRR, fMovimentoMRR,
dPorte ──────────┤          ├─ fUsoProduto / fEventosProduto              fAssinaturas, fAquisicao,
dCohort ─────────┘          ├─ fAssinaturas / fAddOns / fFinanceiro       fTrials, fCohortMensal
                            ├─ fSuporte / fAquisicao / dUsuario
dCanalAquisicao, dSegmento, dPorte ─► fLeads, fTrials, fCohortMensal (sem passar por dCliente)
dCanalAquisicao ─► fMarketing · dTipoMovimento ─► fMovimentoMRR · dFaixaHealth ─► fUsoProduto
```

**Por que fLeads/fTrials/fMarketing não se ligam a dCliente?** Leads e trials não convertidos não têm cliente; ligá-los a dCliente e também a dCanal criaria caminhos ambíguos. Eles recebem canal, segmento e porte diretamente.

**Plano:** `fSnapshotMRR`/`fMovimentoMRR` usam o plano vigente no mês; mudanças de plano geram o par *Plan Migration Out/In* (soma zero no total), garantindo que a ponte de MRR feche também com filtro de plano.

## Relacionamentos ({len(REL)})
{rels}

## Tabelas
""" + "\n\n".join(tabdocs))

# --------------------------------------------------------------- MODELO SEMÂNTICO
by = {}
for m in MEASURES:
    by.setdefault(m["folder"], []).append(m)
ms = []
for f in sorted(by):
    ms.append(f"### {f} ({len(by[f])})\n\n| Medida | Formato | Descrição |\n|---|---|---|\n" + "\n".join(
        f"| {m['name']}{' *(oculta)*' if m.get('hidden') else ''} | `{m.get('fmt') or ''}` | {(m.get('desc') or '').replace('|', '/')} |" for m in by[f]))
w("MODELO_SEMANTICO_NEXORA.md", f"""
# MODELO SEMÂNTICO — NEXORA SaaS Revenue Intelligence

* **Formato:** PBIP com modelo em **TMDL** (`Nexora.SemanticModel/definition`), compatibilidade 1606, cultura pt-BR.
* **Fonte:** 23 CSVs em `Data/` via parâmetro Power Query **`PastaDados`** (Transformar dados → Parâmetros, se mover a pasta).
* **Tabelas:** {len(T)} importadas + 3 calculadas (DATATABLE) + `dCohort` (Power Query) + `_Medidas`.
* **Medidas:** {len(MEASURES)} em `_Medidas`, organizadas nas pastas 01 Revenue · 02 Retention · 03 Growth · 04 Product · 05 Financial · 07 SVG & HTML · 08 Formatting (as comparações temporais ficam dentro dos cards da pasta 07).

## Granularidade dos fatos
| Fato | Grão | Tipo |
|---|---|---|
| fSnapshotMRR | cliente × mês (MRR > 0) | estoque — **nunca somar meses** |
| fMovimentoMRR | cliente × mês × tipo | fluxo (valor já com sinal) |
| fUsoProduto | cliente × mês ativo | estoque de uso / Health |
| fEventosProduto | cliente × mês × funcionalidade | fluxo |
| fAssinaturas | período contratual | booking |
| fFinanceiro | fatura | billing / caixa |
| fMarketing | canal × mês | investimento |
| fLeads / fTrials | lead / trial | funil |
| fAquisicao | primeira aquisição do cliente | CAC alocado |
| fCohortMensal | cohort × idade × canal × plano × segmento × porte | agregado de retenção |

## Regras de cálculo principais
* **Estoque (MRR, ARR, clientes ativos, Health, risco):** avaliados no **último mês do contexto** (`MAX(dCalendario[InicioMes])`).
* **Fluxos (New, Expansion, Contraction, Churn, Reactivation):** soma dos movimentos do período.
* **Reconciliação:** `Beginning MRR + Net New MRR − Ending MRR = 0` (medida `Check Reconciliação MRR`), validada em todos os anos.
* **Logo Churn % / Revenue Churn %:** taxas **médias mensais** (cancelamentos ÷ Σ base no início de cada mês).
* **NRR / GRR (12 meses):** MRR atual da base ativa 12 meses antes ÷ MRR daquela base; GRR limita cada conta ao MRR original.
* **CAC:** custo de aquisição alocado ÷ novos clientes da mesma janela e população (Σ alocado = investimento de marketing).
* **LTV (estimado):** ARPA × margem bruta **80% (premissa)** × vida útil = 1/churn mensal, **limitada a 60 meses**. É estimativa, não valor contábil.
* **CAC Payback:** CAC ÷ (ARPA de novos clientes × 80%).
* **Cards:** estoques comparam com 12 meses antes; fluxos comparam com o período anterior de mesmo tamanho (sem histórico, mostram últimos 12m vs. 12m anteriores).

## Medidas
""" + "\n\n".join(ms))

# --------------------------------------------------------------- GUIA VISUAL
w("GUIA_VISUAL_NEXORA.md", """
# GUIA VISUAL — NEXORA Dark Premium

## Paleta (tema `Theme/NEXORA_Dark.json`)
| Token | Hex | Uso |
|---|---|---|
| Fundo profundo | #050D20 | canvas / outspace |
| Navy principal | #08152F | tooltips, tabelas |
| Painel | #0C1C40 | cabeçalhos de tabela, slicers |
| Azul elétrico | #00B8F5 | destaque principal, MRR, linhas |
| Azul secundário | #1678FF | neutro / referência |
| Violeta | #6736F5 | mês atual, saldo final, gradientes |
| Turquesa | #00D7C0 | resultado positivo / saudável |
| Vermelho | #FF607A | perda / risco / ineficiência |
| Âmbar | #F5A524 | atenção |
| Texto secundário | #A9BBD8 | rótulos, eixos |

## Tipografia
Segoe UI / Segoe UI Semibold nos visuais nativos (fonte disponível em qualquer Windows); HTML usa `'Segoe UI', Inter, Arial`. Títulos de página 46 px, cards 34 px, títulos de visuais 13 pt **centralizados** (diretriz do Brand Book).

## Grid (1920 × 1080)
* Menu lateral 0–248 px (desenhado no background, botões nativos transparentes por cima).
* Conteúdo x = 280 → 1890. Cabeçalho y 20–124; chips de filtros y 118; KPIs y 150–310 (4 cards de 386 px, gap 22).
* Área analítica y 334–1050: principal 1062 px à esquerda + coluna 524 px à direita (2 painéis de 346 px) — ou principal + secundário empilhados.
* Painéis “glass” (cantos 18 px, borda ciano 30%, brilho cyan→violeta no topo) são parte do background; os gráficos são transparentes.

## Componentes HTML (HTML Content — medidas na pasta 07)
Cabeçalho de página · KPI card com sparkline SVG animada · indicador ▲▼ com cor semântica · chips de filtros ativos · estado de alerta (pulse vermelho) · tooltips HTML · barras SVG em tabelas (`dataCategory = ImageUrl`). CSS central na medida oculta **HTML CSS** (animações `nxin`, `nxglow`, `nxpulse`, `nxdash`, `nxgrow`; sem JavaScript).

## Deneb (Vega-Lite — specs em `Deneb/`)
| Visual | Página | Por que Deneb |
|---|---|---|
| MRR Waterfall | Revenue | conectores, cores por tipo e etapa de migração condicional |
| Cohort Heatmap | Customer | matriz cohort × idade com escala de 4 cores |
| Funil de Aquisição | Growth | larguras em escala log + conversão entre etapas |
| CAC vs. LTV por Canal | Growth | barra LTV + barra CAC sobrepostas + rótulo LTV:CAC colorido |
| MRR por Plano | Executive | rótulo duplo valor · participação |

## Cores inteligentes (pasta 08)
`Cor Coluna MRR` (mês atual violeta, queda vermelho, crescimento ciano) · `Cor Destaque Expansion` · `Cor CAC Canal` (≤80% ref. turquesa, ≥120% vermelho) · `Cor LTV CAC` (≥3x turquesa, 1,5–3x âmbar, <1,5x vermelho) · `Cor Faixa Health` · `Cor Movimento`. A semântica respeita a direção do indicador (CAC, churn e risco: subir é ruim).

## Navegação e filtros
Home com botão **Iniciar** → Executive. Menu lateral com botões de navegação nativos. Botão **Filtros** abre o painel lateral oculto (bookmarks *Filtros abertos/fechados* por página, `applyOnlyToTargetVisuals`, sem capturar dados). 8 segmentadores sincronizados entre páginas (Ano, Mês, Plano, Canal, Segmento, Porte, Tipo de cobrança, Cohort) + **Limpar filtros** nativo. Chips HTML mostram o que está aplicado.

## Tooltips
Páginas de dica `TT MRR`, `TT Clientes` e `TT Canal` (360 × 240, HTML) ligadas aos gráficos de evolução, perdidos/recuperados e à tabela de canais.
""")

# --------------------------------------------------------------- README POWER BI
w("README_NEXORA_POWER_BI.md", f"""
# NEXORA — SaaS Revenue Intelligence (Power BI PBIP)

## Estrutura
```
NEXORA/
├── Nexora.pbip                  ← abra este arquivo
├── Nexora.Report/               ← relatório PBIR (páginas, visuais, bookmarks, tema, imagens)
├── Nexora.SemanticModel/        ← modelo TMDL (tabelas, relações, {len(MEASURES)} medidas)
├── Data/                        ← 23 CSVs da base sintética
├── Assets/                      ← backgrounds 1920×1080, logo negativo
├── Theme/NEXORA_Dark.json       ← tema central
├── Deneb/                       ← specs Vega-Lite reutilizáveis
├── Scripts/                     ← geração da base, assets, PBIP e docs (Python)
├── Documentation/               ← esta documentação
└── Validation/                  ← validação da base e do Power BI
```

## Como abrir
1. Abra `Nexora.pbip` no Power BI Desktop (versão de 2026 com PBIR habilitado — projeto salvo na versão instalada).
2. Se a pasta for movida: *Transformar dados → Editar parâmetros → `PastaDados`* (terminar com `\\`) e **Atualizar**.
3. Visuais personalizados: **HTML Content** e **Deneb** (AppSource, certificados). São baixados automaticamente ao abrir com internet; se não, *Obter mais visuais* → pesquisar e adicionar.
4. No modo de edição, use **Ctrl + clique** nos botões (no Serviço/leitura, clique simples).

## Páginas
Início · Executive SaaS · Revenue Intelligence · Customer & Retention · Growth & Unit Economics · 3 páginas de tooltip ocultas.

## Regenerar tudo
```
python Scripts/gerar_base_nexora.py Data
python Scripts/validar_base_nexora.py Data Validation/VALIDACAO_BASE_NEXORA.md
python Scripts/gerar_assets.py <pasta_imagens_marca> Assets
python Scripts/build_pbip.py <saida>/NEXORA Assets "<caminho Windows>\\Data\\"
```
""")
print("docs ok")
