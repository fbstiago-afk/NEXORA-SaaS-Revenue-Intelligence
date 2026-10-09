# VALIDAÇÃO POWER BI — NEXORA SaaS Revenue Intelligence

Ambiente: Power BI Desktop (Microsoft Store, out/2026, tema base Fluent2-CY26SU09, visual 2.13 / report 3.4 / page 2.3.1), Windows, projeto aberto a partir de `Nexora.pbip`. Testes executados em 09/10/2026 diretamente no Desktop (consultas DAX via conexão local ao modelo e inspeção visual das páginas).

## 1. Status da abertura do PBIP
| Item | Resultado |
|---|---|
| Estrutura criada a partir de um PBIP em branco salvo pelo próprio Desktop (schemas reais da versão instalada) | ✅ |
| Abertura do `Nexora.pbip` sem erros de schema/TMDL | ✅ |
| Atualização dos 23 CSVs via parâmetro `PastaDados` | ✅ (cache salvo no projeto) |
| Projeto salvo novamente pelo Desktop após os testes | ✅ |
| Visuais personalizados HTML Content e Deneb carregados (AppSource) | ✅ |

## 2. Carga e integridade do modelo
| Tabela | Linhas carregadas |
|---|---:|
| fSnapshotMRR | 88.394 |
| fMovimentoMRR | 17.548 |
| dCliente | 6.935 |
| fLeads | 277.269 |
| fEventosProduto | 557.729 |
| fCohortMensal | 90.372 |
| dCohort | 34 |
| dCalendario | 1.035 |

* 47 relacionamentos, todos 1:N e de direção única; nenhum M:N, nenhum bidirecional, nenhuma relação fato–fato.
* Validação da base (chaves, órfãos, datas, financeiro, funil): **APROVADO** — ver `VALIDACAO_BASE_NEXORA.md`.

## 3. Reconciliação de MRR (DAX no modelo)
| Ano | Beginning | + New | + Expansion | + Reactivation | − Contraction | − Churn | = Ending | Check |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024 | 0 | 1.813.279 | 172.050 | 6.215 | 7.515 | 90.701 | 1.893.327 | **0** |
| 2025 | 1.893.327 | 2.765.165 | 812.618 | 37.171 | 69.271 | 369.004 | 5.070.007 | **0** |
| 2026 (jan–out) | 5.070.007 | 2.758.118 | 875.304 | 98.604 | 45.555 | 685.238 | 8.071.240 | **0** |

Máximo |Check| em todas as combinações **Plano × Mês**, **Canal × Ano** e **Segmento × Ano**: **R$ 0,00** (a migração de plano é registrada como par saída/entrada, soma zero no total).

## 4. Medidas testadas (valores no contexto total, último mês = out/26)
| Medida | Valor |
|---|---|
| Ending MRR / ARR | R$ 8,07 mi / R$ 96,85 mi |
| Clientes ativos / ARPA | 5.176 / R$ 1.559 |
| NRR 12m (2025 → 2026) | 113,3% → 107,9% |
| GRR 12m (2026) | 90,5% |
| Logo churn médio mensal 2024 / 2025 / 2026 | 2,55% / 2,00% / 2,75% |
| CAC 2024 / 2025 / 2026 | R$ 9,4 mil / R$ 10,6 mil / R$ 13,5 mil |
| LTV:CAC 2024 / 2025 / 2026 | 3,8x / 5,1x / 3,4x |
| CAC Payback 2026 | 14,9 meses |
| Clientes em risco (Risco + Crítico) | 1.028 |
| Clientes com potencial de upgrade | 968 |
| Σ custo alocado − investimento de marketing | R$ 0,55 (arredondamento) |
| Booking / Billing / Revenue / Recebido | R$ 57,7 mi / R$ 152,8 mi / R$ 129,6 mi / R$ 147,0 mi |

Todas as 150 medidas compilam; os 16 cards HTML, 4 cabeçalhos, chips e 3 tooltips retornam HTML válido (≈4–5,5 mil caracteres cada). Três cards com sparkline (incluindo NRR, a mais pesada) executam juntos em **152 ms** (18 ms de storage engine).

## 5. Visuais e interações testados no Desktop
| Teste | Resultado |
|---|---|
| Home → botão **Iniciar** navega para Executive SaaS | ✅ |
| Menu lateral (botões nativos sobre o background) navega entre páginas | ✅ |
| Botão **Filtros** abre o painel (bookmark) e **Aplicar e fechar** fecha preservando a seleção | ✅ (teste com Ano = 2026: cards passaram a comparar “vs. período anterior equivalente”) |
| **Limpar filtros** (dentro do painel) limpa os segmentadores | ✅ |
| Chips de filtros ativos refletem o período selecionado | ✅ |
| Cards HTML com sparkline SVG, cor semântica e alerta | ✅ |
| Deneb: Waterfall, Cohort Heatmap, Funil, CAC × LTV, MRR por Plano | ✅ renderizados com dados |
| Cor inteligente nas colunas de MRR (mês atual violeta) e no Expansion por Plano (maior em turquesa) | ✅ (corrigido durante o teste: ver §6) |
| Tabelas com colunas centralizadas e barras SVG | ✅ |

## 6. Problemas encontrados e corrigidos durante a validação
1. **Destaque do Expansion por Plano** pintava todas as barras: `ALL(dPlano[Plano])` não removia o filtro da coluna de ordenação `OrdemPlano`. Corrigido para `CALCULATE(..., ALLSELECTED(dPlano))`.
2. **Linha de crescimento MoM** distorcida pelos primeiros meses (base próxima de zero): criada `MRR MoM % Gráfico`, exibida a partir de jul/24.
3. **Botão “Limpar” no cabeçalho** não limpava segmentadores ocultos (limitação de *Clear all slicers* com visuais ocultos): removido; a limpeza fica no painel de filtros.
4. Tabela de movimentação estourava a largura: valores passaram a R$ mil.

## 7. Limitações conhecidas
* HTML Content e Deneb são visuais do AppSource: precisam de internet na primeira abertura e de permissão para visuais certificados no tenant ao publicar.
* Animações CSS (entrada dos cards, brilho, pulse, desenho da sparkline) funcionam no Desktop; no Serviço/exportação PDF aparecem no estado final estático.
* Visuais Deneb e HTML não aplicam filtro cruzado ao clicar (seleção desativada por design); os gráficos nativos aplicam.
* LTV é **estimativa** (premissa de margem 80% e vida útil máx. 60 meses); canais com churn muito baixo atingem o teto.
* Botões de navegação exigem **Ctrl + clique** no modo de edição do Desktop (comportamento padrão).
* Não testado: publicação no Serviço, RLS (não aplicável), layout mobile.
