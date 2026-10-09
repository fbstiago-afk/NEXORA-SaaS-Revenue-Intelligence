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

## Relacionamentos (47)
| De (N) | Para (1) |
|---|---|
| fSnapshotMRR.DataMes | dCalendario.Data |
| fSnapshotMRR.ClienteID | dCliente.ClienteID |
| fSnapshotMRR.PlanoID | dPlano.PlanoID |
| fMovimentoMRR.DataMes | dCalendario.Data |
| fMovimentoMRR.ClienteID | dCliente.ClienteID |
| fMovimentoMRR.PlanoID | dPlano.PlanoID |
| fMovimentoMRR.TipoMovimento | dTipoMovimento.TipoMovimento |
| fAssinaturas.DataInicio | dCalendario.Data |
| fAssinaturas.ClienteID | dCliente.ClienteID |
| fAssinaturas.PlanoID | dPlano.PlanoID |
| fAddOns.DataInicio | dCalendario.Data |
| fAddOns.ClienteID | dCliente.ClienteID |
| fAddOns.AddOnID | dAddOn.AddOnID |
| fUsoProduto.DataMes | dCalendario.Data |
| fUsoProduto.ClienteID | dCliente.ClienteID |
| fUsoProduto.FaixaHealth | dFaixaHealth.FaixaHealth |
| fEventosProduto.DataMes | dCalendario.Data |
| fEventosProduto.ClienteID | dCliente.ClienteID |
| fEventosProduto.FuncionalidadeID | dFuncionalidade.FuncionalidadeID |
| fMarketing.DataMes | dCalendario.Data |
| fMarketing.CanalID | dCanalAquisicao.CanalID |
| fLeads.DataLead | dCalendario.Data |
| fLeads.CanalID | dCanalAquisicao.CanalID |
| fLeads.SegmentoID | dSegmento.SegmentoID |
| fLeads.PorteID | dPorte.PorteID |
| fTrials.DataInicioTrial | dCalendario.Data |
| fTrials.CanalID | dCanalAquisicao.CanalID |
| fTrials.SegmentoID | dSegmento.SegmentoID |
| fTrials.PorteID | dPorte.PorteID |
| fTrials.PlanoInteresseID | dPlano.PlanoID |
| fSuporte.DataAbertura | dCalendario.Data |
| fSuporte.ClienteID | dCliente.ClienteID |
| fFinanceiro.DataEmissao | dCalendario.Data |
| fFinanceiro.ClienteID | dCliente.ClienteID |
| fAquisicao.DataAquisicao | dCalendario.Data |
| fAquisicao.ClienteID | dCliente.ClienteID |
| fAquisicao.PlanoEntradaID | dPlano.PlanoID |
| fCohortMensal.CanalID | dCanalAquisicao.CanalID |
| fCohortMensal.PlanoEntradaID | dPlano.PlanoID |
| fCohortMensal.SegmentoID | dSegmento.SegmentoID |
| fCohortMensal.PorteID | dPorte.PorteID |
| fCohortMensal.CohortMes | dCohort.CohortMes |
| dCliente.CanalID | dCanalAquisicao.CanalID |
| dCliente.SegmentoID | dSegmento.SegmentoID |
| dCliente.PorteID | dPorte.PorteID |
| dCliente.CohortMes | dCohort.CohortMes |
| dUsuario.ClienteID | dCliente.ClienteID |

## Tabelas
### dCalendario
Calendário diário 01/01/2024–31/10/2026 (tabela de datas).

| Coluna | Tipo | Observação |
|---|---|---|
| Data | date | chave |
| Ano | int |  |
| MesNum | int | oculta |
| MesNome | text |  |
| MesAbrev | text |  |
| AnoMes | int | oculta |
| MesAno | text |  |
| Trimestre | text |  |
| AnoTrimestre | text |  |
| InicioMes | date |  |
| IndiceMes | int | oculta |
| FaseNegocio | text |  |
| DiaSemana | int | oculta |

### dCliente
Empresas clientes (uma linha por ClienteID) com atributos de aquisição, adoção e status atual.

| Coluna | Tipo | Observação |
|---|---|---|
| ClienteID | int | chave |
| NomeEmpresa | text |  |
| SegmentoID | int | oculta |
| PorteID | int | oculta |
| CanalID | int | oculta |
| Cidade | text |  |
| UF | text |  |
| Regiao | text |  |
| DataAquisicao | date |  |
| CohortMes | date | oculta |
| CohortAno | int |  |
| PlanoEntradaID | int | oculta |
| PlanoAtualID | int | oculta |
| TipoCobranca | text |  |
| StatusAtual | text |  |
| DataUltimoCancelamento | date |  |
| MotivoUltimoCancelamento | text |  |
| FoiReativado | text |  |
| QtdeCancelamentos | int |  |
| PossuiIntegracao | text |  |
| ScoreUsoPrimeiros30Dias | dbl |  |
| AdocaoInicial | text |  |
| DescontoComercialPct | pct |  |
| UsuariosAtuais | int |  |
| MRRAtual | money |  |
| HealthScoreAtual | dbl |  |
| FaixaHealthAtual | text |  |
| PotencialUpgrade | text |  |

### dPlano
Planos comerciais.

| Coluna | Tipo | Observação |
|---|---|---|
| PlanoID | int | chave |
| Plano | text |  |
| OrdemPlano | int | oculta |
| PrecoBaseMensal | money |  |
| UsuariosInclusos | int |  |
| PrecoUsuarioExtra | money |  |
| Posicionamento | text |  |
| CorPlano | text | oculta |

### dSegmento
Segmentos de mercado.

| Coluna | Tipo | Observação |
|---|---|---|
| SegmentoID | int | chave |
| Segmento | text |  |

### dPorte
Porte das empresas.

| Coluna | Tipo | Observação |
|---|---|---|
| PorteID | int | chave |
| Porte | text |  |
| OrdemPorte | int | oculta |
| FaixaFuncionarios | text |  |

### dCanalAquisicao
Canais de aquisição.

| Coluna | Tipo | Observação |
|---|---|---|
| CanalID | int | chave |
| Canal | text |  |
| TipoCanal | text |  |
| MidiaPaga | text |  |

### dFuncionalidade
Funcionalidades do produto.

| Coluna | Tipo | Observação |
|---|---|---|
| FuncionalidadeID | int | chave |
| Funcionalidade | text |  |
| CategoriaFuncionalidade | text |  |

### dUsuario
Usuários licenciados das contas clientes.

| Coluna | Tipo | Observação |
|---|---|---|
| UsuarioID | int | chave |
| ClienteID | int | oculta |
| Perfil | text |  |
| DataCriacao | date |  |
| StatusUsuario | text |  |

### dAddOn
Catálogo de add-ons.

| Coluna | Tipo | Observação |
|---|---|---|
| AddOnID | int | chave |
| AddOn | text |  |
| TipoCobrancaAddOn | text |  |
| PrecoMensal | money |  |

### dFaixaHealth
Faixas do Health Score (Saudável ≥75, Atenção 55–74, Risco 35–54, Crítico <35).

| Coluna | Tipo | Observação |
|---|---|---|
| FaixaHealth | text | chave |
| OrdemFaixa | int | oculta |
| LimiteInferior | int |  |
| CorFaixa | text | oculta |

### fSnapshotMRR
Grão: cliente × mês (fim do mês) com MRR > 0. Estoque — nunca somar meses.

| Coluna | Tipo | Observação |
|---|---|---|
| SnapshotID | int | oculta |
| ClienteID | int | oculta |
| DataMes | date | oculta |
| PlanoID | int | oculta |
| TipoCobranca | text | oculta |
| MRRPlano | money | oculta |
| MRRUsuariosExtras | money | oculta |
| MRRAddOns | money | oculta |
| MRR | money | oculta |
| Usuarios | int | oculta |
| IdadeCohort | int | oculta |
| ReceitaRecorrenteReconhecida | money | oculta |

### fMovimentoMRR
Grão: cliente × mês × tipo de movimento. ValorMRR já com sinal (perdas negativas).

| Coluna | Tipo | Observação |
|---|---|---|
| MovimentoID | int | oculta |
| ClienteID | int | oculta |
| DataMes | date | oculta |
| TipoMovimento | text | oculta |
| Subtipo | text |  |
| PlanoID | int | oculta |
| PlanoAnteriorID | int | oculta |
| ValorMRR | money | oculta |
| MotivoChurn | text |  |
| SinalMovimento | int | oculta |

### fAssinaturas
Contratos (booking). Uma linha por período contratual de plano/ciclo.

| Coluna | Tipo | Observação |
|---|---|---|
| AssinaturaID | int | oculta |
| ClienteID | int | oculta |
| PlanoID | int | oculta |
| TipoCobranca | text | oculta |
| DataInicio | date | oculta |
| DataFim | date | oculta |
| StatusAssinatura | text |  |
| TipoAbertura | text |  |
| MRRInicial | money | oculta |
| PrazoMeses | int | oculta |
| ValorContrato | money | oculta |
| UsuariosContratados | int | oculta |
| MotivoEncerramento | text |  |

### fAddOns
Contratação de add-ons recorrentes.

| Coluna | Tipo | Observação |
|---|---|---|
| AddOnContratoID | int | oculta |
| ClienteID | int | oculta |
| AddOnID | int | oculta |
| DataInicio | date | oculta |
| DataFim | date | oculta |
| StatusAddOn | text |  |
| Quantidade | int | oculta |
| PrecoMensalLista | money | oculta |

### fUsoProduto
Grão: cliente × mês ativo. Uso, adoção e Health Score.

| Coluna | Tipo | Observação |
|---|---|---|
| UsoID | int | oculta |
| ClienteID | int | oculta |
| DataMes | date | oculta |
| UsuariosLicenciados | int | oculta |
| UsuariosAtivos | int | oculta |
| DAU | dbl | oculta |
| WAU | dbl | oculta |
| MAU | int | oculta |
| Logins | int | oculta |
| Sessoes | int | oculta |
| Automacoes | int | oculta |
| Oportunidades | int | oculta |
| Relatorios | int | oculta |
| IntegracoesAtivas | int | oculta |
| FuncionalidadesUsadas | int | oculta |
| TicketsMes | int | oculta |
| FaturasEmAtraso | int | oculta |
| VariacaoUsoPct | pct | oculta |
| HealthScore | dbl | oculta |
| FaixaHealth | text | oculta |
| PotencialUpgrade | text |  |
| MesesDeVida | int | oculta |

### fEventosProduto
Grão: cliente × mês × funcionalidade.

| Coluna | Tipo | Observação |
|---|---|---|
| EventoID | int | oculta |
| ClienteID | int | oculta |
| DataMes | date | oculta |
| FuncionalidadeID | int | oculta |
| Eventos | int | oculta |
| UsuariosUnicos | int | oculta |

### fMarketing
Grão: canal × mês. Investimento e tráfego.

| Coluna | Tipo | Observação |
|---|---|---|
| MarketingID | int | oculta |
| CanalID | int | oculta |
| DataMes | date | oculta |
| Investimento | money | oculta |
| Impressoes | int | oculta |
| Cliques | int | oculta |
| Visitantes | int | oculta |
| Leads | int | oculta |
| NovosClientes | int | oculta |

### fLeads
Grão: lead. Estágios Lead → MQL → SQL → Trial → Cliente.

| Coluna | Tipo | Observação |
|---|---|---|
| LeadID | int | oculta |
| DataLead | date | oculta |
| CanalID | int | oculta |
| SegmentoID | int | oculta |
| PorteID | int | oculta |
| MQL | text | oculta |
| SQL | text | oculta |
| Trial | text | oculta |
| Convertido | text | oculta |

### fTrials
Grão: trial.

| Coluna | Tipo | Observação |
|---|---|---|
| TrialID | int | oculta |
| CanalID | int | oculta |
| SegmentoID | int | oculta |
| PorteID | int | oculta |
| PlanoInteresseID | int | oculta |
| DataInicioTrial | date | oculta |
| DuracaoDias | int | oculta |
| Convertido | text | oculta |
| DataConversao | date | oculta |
| LoginsTrial | int | oculta |

### fSuporte
Grão: ticket de suporte.

| Coluna | Tipo | Observação |
|---|---|---|
| TicketID | int | oculta |
| ClienteID | int | oculta |
| DataAbertura | date | oculta |
| Categoria | text |  |
| Prioridade | text |  |
| SLAHoras | int | oculta |
| TempoPrimeiraRespostaH | dbl | oculta |
| TempoResolucaoH | dbl | oculta |
| DentroSLA | text |  |
| Satisfacao | int | oculta |

### fFinanceiro
Grão: fatura (billing). Não confundir com MRR.

| Coluna | Tipo | Observação |
|---|---|---|
| FaturaID | int | oculta |
| ClienteID | int | oculta |
| DataEmissao | date | oculta |
| DataVencimento | date | oculta |
| DataPagamento | date | oculta |
| TipoFatura | text |  |
| TipoCobranca | text |  |
| ValorBruto | money | oculta |
| Desconto | money | oculta |
| ValorLiquido | money | oculta |
| ValorPago | money | oculta |
| ValorEstornado | money | oculta |
| ValorRecebido | money | oculta |
| StatusPagamento | text |  |
| DiasAtraso | int | oculta |

### fAquisicao
Grão: primeira aquisição do cliente, com custo de aquisição alocado (Σ = investimento).

| Coluna | Tipo | Observação |
|---|---|---|
| ClienteID | int | oculta |
| DataAquisicao | date | oculta |
| DataMes | date | oculta |
| CanalID | int | oculta |
| PlanoEntradaID | int | oculta |
| LeadID | int | oculta |
| TrialID | int | oculta |
| CustoAquisicao | money | oculta |
| MRRInicial | money | oculta |

### fCohortMensal
Agregado: cohort × idade × canal × plano de entrada × segmento × porte.

| Coluna | Tipo | Observação |
|---|---|---|
| CohortRowID | int | oculta |
| CohortMes | date | oculta |
| IdadeCohort | int |  |
| CanalID | int | oculta |
| PlanoEntradaID | int | oculta |
| SegmentoID | int | oculta |
| PorteID | int | oculta |
| ClientesIniciais | int | oculta |
| ClientesAtivos | int | oculta |
| MRRInicial | money | oculta |
| MRRAtivo | money | oculta |

### dTipoMovimento (tabela calculada)
Tipos de movimento de MRR (ordem, rótulo PT-BR e cor semântica).

| Coluna | Tipo |
|---|---|
| TipoMovimento | text |
| Movimento | text |
| OrdemMovimento | int |
| CorMovimento | text |
| GrupoMovimento | text |

### dEtapaWaterfall (tabela calculada)
Etapas da ponte de MRR (tabela desconectada para o Waterfall Deneb).

| Coluna | Tipo |
|---|---|
| Etapa | text |
| OrdemEtapa | int |
| TipoEtapa | text |

### dEtapaFunil (tabela calculada)
Etapas do funil de aquisição (tabela desconectada).

| Coluna | Tipo |
|---|---|
| EtapaFunil | text |
| OrdemFunil | int |

### dCohort (Power Query)
Meses de aquisição distintos de dCliente; conecta dCliente e fCohortMensal.

| Coluna | Tipo |
|---|---|
| CohortMes | date |
| Cohort | text |
| CohortIdx | int |
| CohortAno | int |
