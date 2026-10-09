# VALIDAÇÃO DA BASE — NEXORA SaaS Revenue Intelligence

Status geral: **APROVADO** · Seed 20261009 · Período 2024-01-01 a 2026-10-31

## 1. Integridade das chaves

| Verificação | Status | Detalhe |
|---|---|---|
| PK única dCliente[ClienteID] | ✅ OK | 6,935 linhas |
| PK única dPlano[PlanoID] | ✅ OK | 4 linhas |
| PK única dSegmento[SegmentoID] | ✅ OK | 10 linhas |
| PK única dPorte[PorteID] | ✅ OK | 4 linhas |
| PK única dCanalAquisicao[CanalID] | ✅ OK | 10 linhas |
| PK única dFuncionalidade[FuncionalidadeID] | ✅ OK | 10 linhas |
| PK única dUsuario[UsuarioID] | ✅ OK | 120,573 linhas |
| PK única dAddOn[AddOnID] | ✅ OK | 7 linhas |
| PK única dCalendario[Data] | ✅ OK | 1,035 linhas |
| PK única fSnapshotMRR[SnapshotID] | ✅ OK | 88,394 linhas |
| PK única fMovimentoMRR[MovimentoID] | ✅ OK | 17,548 linhas |
| PK única fAssinaturas[AssinaturaID] | ✅ OK | 8,332 linhas |
| PK única fUsoProduto[UsoID] | ✅ OK | 88,394 linhas |
| PK única fEventosProduto[EventoID] | ✅ OK | 557,729 linhas |
| PK única fLeads[LeadID] | ✅ OK | 277,269 linhas |
| PK única fTrials[TrialID] | ✅ OK | 31,603 linhas |
| PK única fSuporte[TicketID] | ✅ OK | 26,539 linhas |
| PK única fFinanceiro[FaturaID] | ✅ OK | 63,153 linhas |
| PK única fAquisicao[ClienteID] | ✅ OK | 6,935 linhas |
| Snapshot sem duplicidade Cliente×Mês | ✅ OK |  |
| Uso sem duplicidade Cliente×Mês | ✅ OK |  |
| IDs órfãos (23 relações testadas) | ✅ OK | 0 órfãos |
| Datas no calendário: DataMes | ✅ OK | 2024-01-01 → 2026-10-01 |
| Datas no calendário: DataMes | ✅ OK | 2024-01-01 → 2026-10-01 |
| Datas no calendário: DataMes | ✅ OK | 2024-01-01 → 2026-10-01 |
| Datas no calendário: DataMes | ✅ OK | 2024-01-01 → 2026-10-01 |
| Datas no calendário: DataLead | ✅ OK | 2024-01-01 → 2026-10-14 |
| Datas no calendário: DataInicioTrial | ✅ OK | 2024-01-01 → 2026-10-29 |
| Datas no calendário: DataAbertura | ✅ OK | 2024-01-11 → 2026-10-31 |
| Datas no calendário: DataEmissao | ✅ OK | 2024-01-01 → 2026-10-31 |
| Datas no calendário: DataAquisicao | ✅ OK | 2024-01-01 → 2026-10-31 |

## 2. Datas e consistência temporal

| Verificação | Status | Detalhe |
|---|---|---|
| 1º snapshot = mês de aquisição (cohort) | ✅ OK |  |
| Nenhum uso antes do mês de contratação | ✅ OK |  |
| Trial inicia antes da conversão | ✅ OK |  |
| Lead ≤ MQL ≤ SQL | ✅ OK |  |
| Pagamento ≥ emissão (exceto estorno) | ✅ OK |  |
| Assinatura: fim ≥ início | ✅ OK |  |
| Ticket após aquisição | ✅ OK |  |

## 3. Reconciliação MRR (Beginning + movimentos = Ending)

Diferença máxima absoluta em 34 meses: **R$ 0.00** → ✅ FECHA

Reconciliação por plano (com migração de plano): diferença máx. **R$ 0.00**

Reconciliação por CanalID: diferença máx. **R$ 0.00**  
Reconciliação por SegmentoID: diferença máx. **R$ 0.00**  
Reconciliação por PorteID: diferença máx. **R$ 0.00**  

| Mês | Beginning | New | Expansion | Reactivation | Contraction | Churn | Migração (net) | Ending | Dif |
|---|---|---|---|---|---|---|---|---|---|
| 2024-01 | 0 | 94,192 | 0 | 0 | 0 | 0 | 0 | 94,192 | 0.00 |
| 2024-02 | 94,192 | 140,214 | 1,824 | 0 | 0 | -1,284 | 0 | 234,945 | -0.00 |
| 2024-03 | 234,945 | 129,328 | 1,859 | 0 | -66 | -4,107 | 0 | 361,959 | 0.00 |
| 2024-04 | 361,959 | 147,895 | 6,239 | 0 | 0 | -4,681 | 0 | 511,412 | 0.00 |
| 2024-05 | 511,412 | 152,779 | 7,640 | 0 | -322 | -6,097 | 0 | 665,411 | 0.00 |
| 2024-06 | 665,411 | 138,736 | 6,730 | 0 | -39 | -10,352 | 0 | 800,487 | -0.00 |
| 2024-07 | 800,487 | 165,826 | 18,999 | 1,034 | -126 | -8,899 | 0 | 977,321 | 0.00 |
| 2024-08 | 977,321 | 128,718 | 16,652 | 249 | -610 | -10,839 | 0 | 1,111,491 | 0.00 |
| 2024-09 | 1,111,491 | 192,016 | 31,043 | 237 | -4,186 | -10,373 | 0 | 1,320,228 | 0.00 |
| 2024-10 | 1,320,228 | 183,350 | 30,066 | 1,739 | -855 | -14,723 | 0 | 1,519,805 | 0.00 |
| 2024-11 | 1,519,805 | 176,012 | 28,203 | 1,396 | -721 | -11,406 | 0 | 1,713,288 | 0.00 |
| 2024-12 | 1,713,288 | 164,213 | 22,796 | 1,560 | -590 | -7,941 | 0 | 1,893,327 | 0.00 |
| 2025-01 | 1,893,327 | 166,228 | 38,055 | 943 | -499 | -17,297 | 0 | 2,080,757 | 0.00 |
| 2025-02 | 2,080,757 | 213,703 | 41,153 | 1,419 | -4,252 | -21,751 | 0 | 2,311,029 | 0.00 |
| 2025-03 | 2,311,029 | 248,492 | 53,345 | 3,537 | -886 | -27,615 | 0 | 2,587,902 | 0.00 |
| 2025-04 | 2,587,902 | 247,218 | 51,173 | 1,713 | -15,190 | -23,872 | 0 | 2,848,944 | 0.00 |
| 2025-05 | 2,848,944 | 208,155 | 73,170 | 861 | -15,840 | -30,239 | 0 | 3,085,052 | 0.00 |
| 2025-06 | 3,085,052 | 247,673 | 53,237 | 3,461 | -13,667 | -15,249 | 0 | 3,360,506 | 0.00 |
| 2025-07 | 3,360,506 | 181,235 | 76,025 | 2,106 | -2,145 | -42,683 | 0 | 3,575,045 | 0.00 |
| 2025-08 | 3,575,045 | 229,928 | 61,287 | 4,449 | -1,506 | -44,595 | 0 | 3,824,608 | 0.00 |
| 2025-09 | 3,824,608 | 222,930 | 81,611 | 2,636 | -4,746 | -33,900 | 0 | 4,093,138 | 0.00 |
| 2025-10 | 4,093,138 | 259,348 | 109,257 | 7,830 | -3,243 | -34,672 | 0 | 4,431,658 | 0.00 |
| 2025-11 | 4,431,658 | 288,818 | 76,508 | 3,967 | -2,910 | -29,441 | 0 | 4,768,600 | 0.00 |
| 2025-12 | 4,768,600 | 251,436 | 97,797 | 4,249 | -4,387 | -47,689 | 0 | 5,070,007 | 0.00 |
| 2026-01 | 5,070,007 | 227,156 | 79,772 | 3,972 | -3,933 | -54,678 | 0 | 5,322,296 | -0.00 |
| 2026-02 | 5,322,296 | 214,292 | 78,377 | 5,265 | -2,390 | -58,580 | 0 | 5,559,260 | 0.00 |
| 2026-03 | 5,559,260 | 306,111 | 69,573 | 8,403 | -3,062 | -57,570 | 0 | 5,882,715 | 0.00 |
| 2026-04 | 5,882,715 | 266,426 | 96,767 | 8,687 | -7,468 | -76,213 | 0 | 6,170,913 | -0.00 |
| 2026-05 | 6,170,913 | 270,075 | 77,437 | 16,766 | -6,821 | -63,896 | 0 | 6,464,475 | 0.00 |
| 2026-06 | 6,464,475 | 276,420 | 85,459 | 14,229 | -4,041 | -73,608 | 0 | 6,762,935 | 0.00 |
| 2026-07 | 6,762,935 | 288,713 | 78,415 | 11,247 | -2,060 | -76,453 | 0 | 7,062,798 | -0.00 |
| 2026-08 | 7,062,798 | 296,843 | 90,960 | 7,026 | -7,897 | -70,238 | 0 | 7,379,492 | 0.00 |
| 2026-09 | 7,379,492 | 304,193 | 128,035 | 11,742 | -2,400 | -78,507 | 0 | 7,742,555 | 0.00 |
| 2026-10 | 7,742,555 | 307,888 | 90,510 | 11,267 | -5,484 | -75,497 | 0 | 8,071,240 | 0.00 |

## 4. Financeiro, contratos e reativações

| Verificação | Status | Detalhe |
|---|---|---|
| ValorLíquido = Bruto − Desconto | ✅ OK |  |
| Recebido = Pago − Estornado | ✅ OK |  |
| Toda reativação precedida de churn | ✅ OK | 279 reativações |
| Cada cliente possui exatamente 1 New | ✅ OK |  |
| Booking (fAssinaturas) ≠ Billing (fFinanceiro) ≠ MRR | ✅ OK | Booking R$ 57.7 mi · Billing R$ 152.8 mi · Σ MRR mensal R$ 119.7 mi |
| Custo de aquisição alocado = investimento | ✅ OK | R$ 78.25 mi |
| Funil monotônico (Leads ≥ MQL ≥ SQL ≥ Trials ≥ Clientes) | ✅ OK | 277,269 → 120,621 → 48,414 → 31,603 → 6,935 |

## 5. Padrões analíticos inseridos (evidências)

**Logo churn mensal médio por plano (%)**

| Plano | 2024 | 2025 | 2026 |
|---|---|---|---|
| Starter | 4.64 | 3.66 | 6.62 |
| Growth | 2.15 | 1.89 | 2.18 |
| Pro | 0.56 | 0.76 | 0.91 |
| Enterprise | 0.00 | 0.28 | 0.16 |

**Expansion MRR por plano (acumulado)**: Starter: R$ 40,319 · Growth: R$ 308,549 · Pro: R$ 861,557 · Enterprise: R$ 649,548

**Contraction MRR**: média mensal R$ -3,946; Abr–Jun/2025: R$ -15,190, R$ -15,840, R$ -13,667

**CAC médio por canal (R$)**

| Canal | 2024 | 2025 | 2026 |
|---|---|---|---|
| Google Ads | 7,027 | 8,223 | 13,583 |
| Meta Ads | 4,549 | 5,997 | 8,537 |
| LinkedIn Ads | 29,502 | 29,511 | 34,135 |
| Conteúdo Orgânico | 3,605 | 3,931 | 3,959 |
| Indicação | 1,915 | 1,888 | 2,141 |
| Parceiros | 6,315 | 5,703 | 6,770 |
| Outbound | 34,161 | 36,768 | 39,524 |
| Eventos | 30,948 | 32,765 | 36,927 |
| Webinar | 4,636 | 4,054 | 5,550 |
| Marketplace | 2,542 | 2,992 | 3,946 |

**CAC por plano de entrada**: Starter: R$ 3,375 · Growth: R$ 7,147 · Pro: R$ 16,254 · Enterprise: R$ 53,015

**Retenção de logos no 6º mês por PossuiIntegracao**: Não: 69.6% · Sim: 94.7%

**Retenção de logos no 6º mês por AdocaoInicial**: Alta: 91.6% · Baixa: 64.0% · Média: 88.0%

**Retenção de logos no 6º mês por CanalID**: Google Ads: 80.4% · Meta Ads: 73.0% · LinkedIn Ads: 91.7% · Conteúdo Orgânico: 86.5% · Indicação: 90.7% · Parceiros: 88.8% · Outbound: 92.7% · Eventos: 90.9% · Webinar: 83.6% · Marketplace: 80.6%

**Retenção de logos no 6º mês por CohortAno**: 2024: 86.3% · 2025: 85.9% · 2026: 75.9%

**Clientes ativos com potencial claro de upgrade (Out/2026)**: 968

**Reativações**: 279 eventos · R$ 141,990 de Reactivation MRR

**Varejo B2B — novos clientes 2024→2026**: 145 → 395 → 456 (10 meses); CAC médio R$ 13,315 vs base R$ 11,283

**Health Score (Out/2026)**: Saudável: 2432 · Atenção: 1716 · Risco: 945 · Crítico: 83

**MRR final (Out/2026)**: R$ 8,071,240 · ARR R$ 96,854,878 · Clientes ativos 5,176