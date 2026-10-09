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
