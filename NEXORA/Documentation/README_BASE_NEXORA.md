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
| Arquivo | Linhas | Tamanho (MB) |
|---|---:|---:|
| dAddOn.csv | 7 | 0.00 |
| dCalendario.csv | 1.035 | 0.09 |
| dCanalAquisicao.csv | 10 | 0.00 |
| dCliente.csv | 6.935 | 1.07 |
| dFaixaHealth.csv | 4 | 0.00 |
| dFuncionalidade.csv | 10 | 0.00 |
| dPlano.csv | 4 | 0.00 |
| dPorte.csv | 4 | 0.00 |
| dSegmento.csv | 10 | 0.00 |
| dUsuario.csv | 120.573 | 4.26 |
| fAddOns.csv | 3.312 | 0.13 |
| fAquisicao.csv | 6.935 | 0.39 |
| fAssinaturas.csv | 8.332 | 0.56 |
| fCohortMensal.csv | 90.372 | 3.96 |
| fEventosProduto.csv | 557.729 | 16.12 |
| fFinanceiro.csv | 63.153 | 7.03 |
| fLeads.csv | 277.269 | 13.81 |
| fMarketing.csv | 340 | 0.01 |
| fMovimentoMRR.csv | 17.548 | 1.02 |
| fSnapshotMRR.csv | 88.394 | 5.77 |
| fSuporte.csv | 26.539 | 1.47 |
| fTrials.csv | 31.603 | 1.74 |
| fUsoProduto.csv | 88.394 | 7.52 |
| **Total** | **1.388.512** | **65.0** |

## Padrões analíticos inseridos deliberadamente
1. Aumento de churn do **Starter em 2026**. 2. **Indicação** com CAC baixo e melhor retenção. 3. **Google Ads** (e Meta) com CAC crescente em 2026. 4. **Integrações** associadas a maior retenção. 5. **Baixo uso nos primeiros 30 dias** associado a churn. 6. **Pro** concentra Expansion MRR. 7. **Enterprise** com churn baixo e CAC alto. 8. **Varejo B2B** cresce em clientes, mas com CAC maior, desconto maior e churn maior (rentabilidade ruim). 9. **Cohorts de 2026** com retenção abaixo da média. 10. **Pico temporário de Contraction MRR** em abr–jun/2025. 11. Clientes com **potencial claro de upgrade** (`fUsoProduto[PotencialUpgrade]`). 12. Clientes **cancelados e reativados**.

As relações são estatísticas, não determinísticas (há ruído em todas as etapas). Evidências numéricas em `VALIDACAO_BASE_NEXORA.md`.
