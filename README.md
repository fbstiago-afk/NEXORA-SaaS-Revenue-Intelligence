# NEXORA — SaaS Revenue Intelligence

<!-- portfolio-link:start -->
[![Ver no portfólio](https://img.shields.io/badge/Ver%20o%20painel%20no%20portf%C3%B3lio-Bocardi%20Data-6C3BAA?style=for-the-badge)](https://bocardidata.base44.app/ProjectDetail?id=nexora-saas-revenue-intelligence)

> 🔗 **Quer ver o visual do Power BI?** Acesse a página do projeto no portfólio: **[https://bocardidata.base44.app/ProjectDetail?id=nexora-saas-revenue-intelligence](https://bocardidata.base44.app/ProjectDetail?id=nexora-saas-revenue-intelligence)**
<!-- portfolio-link:end -->


**Connect. Automate. Grow.**

Projeto de portfólio em **Power BI (PBIP / PBIR / TMDL)** para uma empresa SaaS B2B fictícia: Revenue Analytics + Customer Analytics + Product Analytics + Growth Analytics. O dashboard mostra como a NEXORA **adquire → ativa → monetiza → retém → expande → perde → recupera** clientes.

> Empresa e dados 100% fictícios, gerados por simulação reprodutível (seed 20261009). Período: jan/2024 – out/2026.

## Destaques
- **Base sintética relacional**: 23 tabelas, ~1,39 mi de linhas e 6.935 empresas, com comportamento causal (adoção → uso → Health Score → churn/expansão).
- **Modelo semântico**: 28 tabelas, 47 relacionamentos 1:N de direção única e **150 medidas DAX** em display folders.
- **Ponte de MRR que fecha em R$ 0,00**: Beginning + New + Expansion + Reactivation − Contraction − Churn = Ending, validada por ano, plano × mês, canal e segmento.
- **5 páginas**: Home (botão Iniciar), Executive SaaS, Revenue Intelligence, Customer & Retention e Growth & Unit Economics, além de 3 tooltips.
- **Visual dark premium**: cards em HTML com sparklines SVG animadas, 5 gráficos Deneb/Vega-Lite (Waterfall, Cohort Heatmap, Funil, CAC × LTV, MRR por Plano), cores semânticas, painel de filtros por bookmarks e chips de filtros ativos.

## Números da base (out/2026)
| Indicador | Valor |
|---|---|
| MRR / ARR | R$ 8,07 mi / R$ 96,9 mi |
| Clientes ativos | 5.176 |
| NRR 12m | 113% (2025) → 108% (2026) |
| Logo churn Starter 2026 | ~6,6% a.m. |
| LTV:CAC Google Ads | 3,6x → 2,3x em 2026 |
| Contas em risco / potencial de upgrade | 1.028 / 968 |

## Estrutura
```
NEXORA/
├── Nexora.pbip               ← abrir no Power BI Desktop
├── Nexora.Report/            ← relatório PBIR (páginas, visuais, bookmarks, tema, imagens)
├── Nexora.SemanticModel/     ← modelo TMDL
├── Data/                     ← 23 CSVs (UTF-8, vírgula, YYYY-MM-DD, decimal com ponto)
├── Assets/  Theme/  Deneb/   ← backgrounds, tema JSON, specs Vega-Lite
├── Scripts/                  ← geração da base, validação, assets, PBIP e docs (Python)
├── Documentation/            ← README da base, modelo relacional, modelo semântico, guia visual
└── Validation/               ← validação da base e do Power BI
Brand/                        ← brand book, brief, one pager, referências visuais e prompt master
```

## Como abrir
1. Clone o repositório e abra `NEXORA/Nexora.pbip` no Power BI Desktop (versão 2026 com PBIR).
2. Em *Transformar dados → Editar parâmetros*, ajuste **`PastaDados`** para o caminho local da pasta `NEXORA\Data\` (terminando com `\`) e clique em **Atualizar**.
3. Os visuais **HTML Content** e **Deneb** (AppSource) são baixados ao abrir com internet.
4. No modo de edição, use **Ctrl + clique** nos botões de navegação.

## Regenerar a base
```bash
python NEXORA/Scripts/gerar_base_nexora.py NEXORA/Data
python NEXORA/Scripts/validar_base_nexora.py NEXORA/Data NEXORA/Validation/VALIDACAO_BASE_NEXORA.md
```

## Documentação
- [README da base](NEXORA/Documentation/README_BASE_NEXORA.md)
- [Modelo relacional](NEXORA/Documentation/MODELO_RELACIONAL_NEXORA.md)
- [Modelo semântico e medidas](NEXORA/Documentation/MODELO_SEMANTICO_NEXORA.md)
- [Guia visual](NEXORA/Documentation/GUIA_VISUAL_NEXORA.md)
- [Validação da base](NEXORA/Validation/VALIDACAO_BASE_NEXORA.md) · [Validação do Power BI](NEXORA/Validation/VALIDACAO_POWER_BI_NEXORA.md)
