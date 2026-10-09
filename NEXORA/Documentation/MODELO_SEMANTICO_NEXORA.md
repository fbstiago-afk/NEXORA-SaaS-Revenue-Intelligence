# MODELO SEMÂNTICO — NEXORA SaaS Revenue Intelligence

* **Formato:** PBIP com modelo em **TMDL** (`Nexora.SemanticModel/definition`), compatibilidade 1606, cultura pt-BR.
* **Fonte:** 23 CSVs em `Data/` via parâmetro Power Query **`PastaDados`** (Transformar dados → Parâmetros, se mover a pasta).
* **Tabelas:** 23 importadas + 3 calculadas (DATATABLE) + `dCohort` (Power Query) + `_Medidas`.
* **Medidas:** 150 em `_Medidas`, organizadas nas pastas 01 Revenue · 02 Retention · 03 Growth · 04 Product · 05 Financial · 07 SVG & HTML · 08 Formatting (as comparações temporais ficam dentro dos cards da pasta 07).

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
### 01 Revenue (25)

| Medida | Formato | Descrição |
|---|---|---|
| Mês Referência *(oculta)* | `mmm/yy` | Último mês do contexto (referência para métricas de estoque). |
| Beginning MRR | `"R$" #,0` | MRR no fim do mês anterior ao primeiro mês do contexto. |
| Ending MRR | `"R$" #,0` | MRR no fim do último mês do contexto (estoque — nunca somado entre meses). |
| New MRR | `"R$" #,0` | Fluxo do período (New).  |
| Expansion MRR | `"R$" #,0` | Fluxo do período (Expansion).  |
| Reactivation MRR | `"R$" #,0` | Fluxo do período (Reactivation).  |
| Contraction MRR | `"R$" #,0` | Fluxo do período (Contraction). Exibido como valor positivo (perda). |
| Churned MRR | `"R$" #,0` | Fluxo do período (Churn). Exibido como valor positivo (perda). |
| Migração Líquida MRR | `"R$" #,0` | Entrada − saída de MRR por migração de plano. Soma zero no total; aparece apenas com filtro de plano. |
| Net New MRR | `"R$" #,0` | New + Expansion + Reactivation − Contraction − Churn (+ migração líquida). |
| MRR Movimentado | `"R$" #,0` | Valor assinado do movimento (para gráficos por tipo). |
| Check Reconciliação MRR | `"R$" #,0.00` | Deve ser sempre 0: Beginning + movimentos − Ending. |
| ARR | `"R$" #,0` | Annual Recurring Revenue = Ending MRR × 12. |
| Clientes Ativos | `#,0` | Clientes com MRR > 0 no último mês do contexto. |
| ARPA | `"R$" #,0` | Receita média recorrente por conta. |
| MRR 12M Antes | `"R$" #,0` |  |
| MRR Mês Anterior | `"R$" #,0` |  |
| MRR YoY % | `0.0%` |  |
| MRR MoM % | `0.0%` |  |
| MRR MoM % Gráfico | `0.0%` | Crescimento mensal exibido a partir de jul/24 (meses iniciais partem de base próxima de zero). |
| MRR Growth % | `0.0%` | Crescimento do MRR no período selecionado. |
| % MRR do Total | `0.0%` |  |
| MRR por Plano | `"R$" #,0` | Use com dPlano[Plano] (plano vigente no snapshot). |
| MRR por Canal | `"R$" #,0` | Use com dCanalAquisicao[Canal] (canal de aquisição do cliente). |
| MRR por Segmento | `"R$" #,0` | Use com dSegmento[Segmento]. |

### 02 Retention (26)

| Medida | Formato | Descrição |
|---|---|---|
| Clientes Novos | `#,0` |  |
| Clientes Cancelados | `#,0` |  |
| Clientes Reativados | `#,0` |  |
| Clientes Base Mensal *(oculta)* | `#,0` | Σ clientes ativos no início de cada mês do contexto (denominador de churn mensal). |
| MRR Base Mensal *(oculta)* | `"R$" #,0` | Σ MRR no início de cada mês do contexto. |
| Logo Churn % | `0.00%` | Taxa média MENSAL de cancelamento de logos no período. |
| Revenue Churn % | `0.00%` | Gross revenue churn médio mensal (churn + contração). |
| Customer Retention % | `0.0%` | Retenção média mensal de logos. |
| NRR % | `0.0%` | Net Revenue Retention 12 meses: MRR atual da base de 12 meses atrás ÷ MRR daquela base (inclui expansão). |
| GRR % | `0.0%` | Gross Revenue Retention 12 meses (sem expansão, limitado a 100% por conta). |
| Customer Retention 12M % | `0.0%` | % de logos ativos há 12 meses que continuam ativos. |
| Clientes Iniciais Cohort | `#,0` |  |
| Clientes Ativos Cohort | `#,0` |  |
| Cohort Retention % | `0.0%` |  |
| Cohort Revenue Retention % | `0.0%` | MRR restante do cohort ÷ MRR inicial (inclui expansão acumulada). |
| Cohort Churn Acumulado % | `0.0%` |  |
| Cohort Retenção Heatmap *(oculta)* | `0.0%` | Retenção do cohort limitada a M0–M12 (alimenta o heatmap Deneb). |
| Clientes Monitorados | `#,0` | Contas ativas com Health Score no último mês. |
| Clientes em Risco | `#,0` | Contas nas faixas Risco ou Crítico no último mês do contexto. |
| % Clientes em Risco | `0.0%` |  |
| MRR em Risco | `"R$" #,0` |  |
| % da Base (Health) | `0.0%` |  |
| Health Score Médio | `0.0` |  |
| Clientes com Integração | `#,0` |  |
| % Clientes com Integração | `0.0%` |  |
| Taxa de Adoção | `0.0%` | Média de funcionalidades usadas ÷ 10 funcionalidades disponíveis. |

### 03 Growth (20)

| Medida | Formato | Descrição |
|---|---|---|
| Investimento Marketing | `"R$" #,0` |  |
| Visitantes | `#,0` |  |
| Leads | `#,0` |  |
| MQL | `#,0` |  |
| SQL | `#,0` |  |
| Trials | `#,0` |  |
| Clientes Convertidos | `#,0` |  |
| Novos Clientes Adquiridos | `#,0` |  |
| Lead → Trial % | `0.0%` |  |
| Trial → Paid % | `0.0%` |  |
| Lead → Cliente % | `0.00%` |  |
| CAC | `"R$" #,0` | Investimento alocado ÷ novos clientes da mesma janela e população (Σ custo alocado = investimento de marketing). |
| ARPA Novos Clientes | `"R$" #,0` |  |
| Margem Bruta Premissa | `0.0%` | Premissa documentada de margem bruta SaaS (80%). |
| Vida Útil Estimada | `0.0` | 1 ÷ churn mensal de logos, limitada a 60 meses (premissa conservadora). |
| LTV Estimado | `"R$" #,0` | ESTIMATIVA: ARPA × margem bruta (80%) × vida útil (1/churn, máx. 60 meses). |
| LTV:CAC | `0.0"x"` |  |
| CAC Payback | `0.0" meses"` | Meses de margem bruta do MRR inicial para recuperar o CAC. |
| Receita por Canal | `"R$" #,0` |  |
| Eficiência por Canal | `0.0"x"` |  |

### 04 Product (15)

| Medida | Formato | Descrição |
|---|---|---|
| Usuários Ativos | `#,0` |  |
| DAU | `#,0` | Usuários ativos diários médios (último mês). |
| WAU | `#,0` |  |
| MAU | `#,0` |  |
| DAU/MAU % | `0.0%` | Stickiness. |
| Logins | `#,0` |  |
| Sessões | `#,0` |  |
| Automações | `#,0` |  |
| Integrações Ativas | `#,0` |  |
| Funcionalidades Utilizadas | `0.0` |  |
| Adoção Média | `0.0%` |  |
| Health Score | `0.0` |  |
| Clientes com Baixa Adoção | `#,0` |  |
| Clientes Potencial Upgrade | `#,0` | Starter/Growth/Pro com uso perto do limite de usuários, alta adoção e Health ≥ 74. |
| Eventos de Produto | `#,0` |  |

### 05 Financial (12)

| Medida | Formato | Descrição |
|---|---|---|
| Booking | `"R$" #,0` | Valor contratado (ACV do contrato: 12× MRR anual, 1× mensal). |
| Billing | `"R$" #,0` | Valor faturado (faturas emitidas). Anual é faturado antecipadamente. |
| Receita Recebida | `"R$" #,0` |  |
| Descontos Concedidos | `"R$" #,0` |  |
| Estornos | `"R$" #,0` |  |
| Inadimplência | `"R$" #,0` |  |
| % Inadimplência | `0.00%` |  |
| Receita Não Recorrente | `"R$" #,0` |  |
| Receita Reconhecida | `"R$" #,0` | Revenue: MRR reconhecido mês a mês + serviços não recorrentes (implantação/treinamento). |
| Tickets | `#,0` |  |
| CSAT Médio | `0.00` |  |
| % Tickets no SLA | `0.0%` |  |

### 07 SVG & HTML (39)

| Medida | Formato | Descrição |
|---|---|---|
| HTML CSS *(oculta)* | `` | Folha de estilo compartilhada (design system NEXORA) para todos os componentes HTML. |
| HTML Card MRR | `` | Card KPI HTML de [Ending MRR] com variação e sparkline SVG (12 meses). |
| HTML Card ARR | `` | Card KPI HTML de [ARR] com variação e sparkline SVG (12 meses). |
| HTML Card Clientes | `` | Card KPI HTML de [Clientes Ativos] com variação e sparkline SVG (12 meses). |
| HTML Card NRR | `` | Card KPI HTML de [NRR %] com variação e sparkline SVG (12 meses). |
| HTML Card New MRR | `` | Card KPI HTML de [New MRR] com variação e sparkline SVG (12 meses). |
| HTML Card Expansion | `` | Card KPI HTML de [Expansion MRR] com variação e sparkline SVG (12 meses). |
| HTML Card Churned | `` | Card KPI HTML de [Churned MRR] com variação e sparkline SVG (12 meses). |
| HTML Card Net New | `` | Card KPI HTML de [Net New MRR] com variação e sparkline SVG (12 meses). |
| HTML Card Clientes R | `` | Card KPI HTML de [Clientes Ativos] com variação e sparkline SVG (12 meses). |
| HTML Card Logo Churn | `` | Card KPI HTML de [Logo Churn %] com variação e sparkline SVG (12 meses). |
| HTML Card NRR R | `` | Card KPI HTML de [NRR %] com variação e sparkline SVG (12 meses). |
| HTML Card Risco | `` | Card KPI HTML de [Clientes em Risco] com variação e sparkline SVG (12 meses). |
| HTML Card CAC | `` | Card KPI HTML de [CAC] com variação e sparkline SVG (12 meses). |
| HTML Card LTV | `` | Card KPI HTML de [LTV Estimado] com variação e sparkline SVG (12 meses). |
| HTML Card LTV CAC | `` | Card KPI HTML de [LTV:CAC] com variação e sparkline SVG (12 meses). |
| HTML Card Payback | `` | Card KPI HTML de [CAC Payback] com variação e sparkline SVG (12 meses). |
| HTML Header Executive | `` | Cabeçalho HTML da página. |
| HTML Header Revenue | `` | Cabeçalho HTML da página. |
| HTML Header Customer | `` | Cabeçalho HTML da página. |
| HTML Header Growth | `` | Cabeçalho HTML da página. |
| HTML Filtros Ativos | `` | Chips com os filtros aplicados. |
| HTML TT MRR | `` | Tooltip de MRR (página de dica de ferramenta). |
| HTML TT Clientes | `` | Tooltip de clientes. |
| HTML TT Canal | `` | Tooltip de canal. |
| SVG Barra CAC | `` | Barra SVG de CAC (escala relativa ao maior CAC selecionado). |
| SVG Barra LTV CAC | `` | Barra SVG de LTV:CAC (escala 0–10x; marcador em 3x). |
| SVG Status Health | `` | Indicador SVG de status do Health Score. |
| Valor Etapa Waterfall | `"R$" #,0` | Valor de cada etapa da ponte de MRR (perdas negativas). |
| Rótulo Etapa Waterfall | `` | Rótulo formatado da etapa. |
| Valor Etapa Funil | `#,0` |  |
| Rótulo Etapa Funil | `` |  |
| Rótulo MRR Plano | `` |  |
| Rótulo LTV CAC | `` |  |
| Rótulo CAC | `` |  |
| Rótulo LTV | `` |  |
| Rótulo Cohort | `` |  |
| Conversão Etapa Funil | `0.0%` | Conversão em relação à etapa anterior do funil. |
| Rótulo Conversão Funil | `` |  |

### 08 Formatting (13)

| Medida | Formato | Descrição |
|---|---|---|
| Cor Coluna MRR | `` | Mês atual = violeta; queda = vermelho; crescimento forte = ciano; demais = azul. |
| Cor Plano | `` |  |
| Cor Movimento | `` |  |
| Cor Faixa Health | `` |  |
| Cor Destaque Expansion | `` |  |
| Cor CAC Canal | `` | CAC ≤ 80% da referência = turquesa; ≥ 120% = vermelho. |
| Cor LTV CAC | `` | ≥ 3x saudável; 1,5–3x atenção; < 1,5x ineficiente. |
| Tbl Novo | `#,0.0` | Valor em R$ mil para tabelas compactas. |
| Tbl Expansão | `#,0.0` | Valor em R$ mil para tabelas compactas. |
| Tbl Contração | `#,0.0` | Valor em R$ mil para tabelas compactas. |
| Tbl Churn | `#,0.0` | Valor em R$ mil para tabelas compactas. |
| Tbl Net New | `#,0.0` | Valor em R$ mil para tabelas compactas. |
| Ordem Plano *(oculta)* | `0` |  |
