# -*- coding: utf-8 -*-
"""Medidas DAX do NEXORA. Cada item: name, folder, fmt, dax, (hidden, desc, cat)."""

M = []


def add(name, folder, dax, fmt=None, desc=None, hidden=False, cat=None):
    M.append(dict(name=name, folder=folder, dax=dax, fmt=fmt, desc=desc, hidden=hidden, cat=cat))


MONEY = '"R$" #,0'
MONEY2 = '"R$" #,0.00'
INT = "#,0"
PCT = "0.0%"
F_REV, F_RET, F_GRO, F_PRO, F_FIN, F_CMP, F_HTML, F_FMT = ("01 Revenue", "02 Retention", "03 Growth", "04 Product",
                                                            "05 Financial", "06 Comparisons", "07 SVG & HTML", "08 Formatting")

# ======================================================================= 01 REVENUE
add("Mês Referência", F_REV, "MAX ( dCalendario[InicioMes] )", "mmm/yy", "Último mês do contexto (referência para métricas de estoque).", True)
add("Beginning MRR", F_REV, """
VAR _m0 = MIN ( dCalendario[InicioMes] )
RETURN
    COALESCE (
        CALCULATE ( SUM ( fSnapshotMRR[MRR] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = EDATE ( _m0, -1 ) ),
        0
    )""", MONEY, "MRR no fim do mês anterior ao primeiro mês do contexto.")
add("Ending MRR", F_REV, """
VAR _m = MAX ( dCalendario[InicioMes] )
RETURN
    CALCULATE ( SUM ( fSnapshotMRR[MRR] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _m )""", MONEY,
    "MRR no fim do último mês do contexto (estoque — nunca somado entre meses).")
for nm, tp, sg in [("New MRR", "New", ""), ("Expansion MRR", "Expansion", ""), ("Reactivation MRR", "Reactivation", ""),
                   ("Contraction MRR", "Contraction", "- "), ("Churned MRR", "Churn", "- ")]:
    add(nm, F_REV, f'{sg}CALCULATE ( SUM ( fMovimentoMRR[ValorMRR] ), fMovimentoMRR[TipoMovimento] = "{tp}" )', MONEY,
        f"Fluxo do período ({tp}). " + ("Exibido como valor positivo (perda)." if sg else ""))
add("Migração Líquida MRR", F_REV,
    'CALCULATE ( SUM ( fMovimentoMRR[ValorMRR] ), fMovimentoMRR[TipoMovimento] IN { "Plan Migration In", "Plan Migration Out" } )',
    MONEY, "Entrada − saída de MRR por migração de plano. Soma zero no total; aparece apenas com filtro de plano.")
add("Net New MRR", F_REV, "SUM ( fMovimentoMRR[ValorMRR] )", MONEY, "New + Expansion + Reactivation − Contraction − Churn (+ migração líquida).")
add("MRR Movimentado", F_REV, "SUM ( fMovimentoMRR[ValorMRR] )", MONEY, "Valor assinado do movimento (para gráficos por tipo).")
add("Check Reconciliação MRR", F_REV, "ROUND ( [Beginning MRR] + [Net New MRR] - [Ending MRR], 2 )", MONEY2,
    "Deve ser sempre 0: Beginning + movimentos − Ending.")
add("ARR", F_REV, "[Ending MRR] * 12", MONEY, "Annual Recurring Revenue = Ending MRR × 12.")
add("Clientes Ativos", F_REV, """
VAR _m = MAX ( dCalendario[InicioMes] )
RETURN
    CALCULATE ( DISTINCTCOUNT ( fSnapshotMRR[ClienteID] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _m )""", INT,
    "Clientes com MRR > 0 no último mês do contexto.")
add("ARPA", F_REV, "DIVIDE ( [Ending MRR], [Clientes Ativos] )", MONEY, "Receita média recorrente por conta.")
add("MRR 12M Antes", F_REV, """
VAR _m = MAX ( dCalendario[InicioMes] )
RETURN
    CALCULATE ( SUM ( fSnapshotMRR[MRR] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = EDATE ( _m, -12 ) )""", MONEY)
add("MRR Mês Anterior", F_REV, """
VAR _m = MAX ( dCalendario[InicioMes] )
RETURN
    CALCULATE ( SUM ( fSnapshotMRR[MRR] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = EDATE ( _m, -1 ) )""", MONEY)
add("MRR YoY %", F_REV, "DIVIDE ( [Ending MRR] - [MRR 12M Antes], [MRR 12M Antes] )", PCT)
add("MRR MoM %", F_REV, "DIVIDE ( [Ending MRR] - [MRR Mês Anterior], [MRR Mês Anterior] )", PCT)
add("MRR MoM % Gráfico", F_REV, "IF ( MAX ( dCalendario[InicioMes] ) >= DATE ( 2024, 7, 1 ), [MRR MoM %] )", PCT, "Crescimento mensal exibido a partir de jul/24 (meses iniciais partem de base próxima de zero).")
add("MRR Growth %", F_REV, "DIVIDE ( [Ending MRR] - [Beginning MRR], [Beginning MRR] )", PCT, "Crescimento do MRR no período selecionado.")
add("% MRR do Total", F_REV, """
DIVIDE (
    [Ending MRR],
    CALCULATE ( [Ending MRR], ALLSELECTED ( dPlano ), ALLSELECTED ( dCanalAquisicao ), ALLSELECTED ( dSegmento ), ALLSELECTED ( dPorte ) )
)""", PCT)
add("MRR por Plano", F_REV, "[Ending MRR]", MONEY, "Use com dPlano[Plano] (plano vigente no snapshot).")
add("MRR por Canal", F_REV, "[Ending MRR]", MONEY, "Use com dCanalAquisicao[Canal] (canal de aquisição do cliente).")
add("MRR por Segmento", F_REV, "[Ending MRR]", MONEY, "Use com dSegmento[Segmento].")

# ======================================================================= 02 RETENTION
for nm, tp in [("Clientes Novos", "New"), ("Clientes Cancelados", "Churn"), ("Clientes Reativados", "Reactivation")]:
    add(nm, F_RET, f'CALCULATE ( COUNTROWS ( fMovimentoMRR ), fMovimentoMRR[TipoMovimento] = "{tp}" )', INT)
add("Clientes Base Mensal", F_RET, """
SUMX (
    VALUES ( dCalendario[InicioMes] ),
    VAR _m = dCalendario[InicioMes]
    RETURN
        CALCULATE ( DISTINCTCOUNT ( fSnapshotMRR[ClienteID] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = EDATE ( _m, -1 ) )
)""", INT, "Σ clientes ativos no início de cada mês do contexto (denominador de churn mensal).", True)
add("MRR Base Mensal", F_RET, """
SUMX (
    VALUES ( dCalendario[InicioMes] ),
    VAR _m = dCalendario[InicioMes]
    RETURN
        CALCULATE ( SUM ( fSnapshotMRR[MRR] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = EDATE ( _m, -1 ) )
)""", MONEY, "Σ MRR no início de cada mês do contexto.", True)
add("Logo Churn %", F_RET, "DIVIDE ( [Clientes Cancelados], [Clientes Base Mensal] )", "0.00%",
    "Taxa média MENSAL de cancelamento de logos no período.")
add("Revenue Churn %", F_RET, "DIVIDE ( [Churned MRR] + [Contraction MRR], [MRR Base Mensal] )", "0.00%",
    "Gross revenue churn médio mensal (churn + contração).")
add("Customer Retention %", F_RET, "IF ( NOT ISBLANK ( [Logo Churn %] ), 1 - [Logo Churn %] )", PCT, "Retenção média mensal de logos.")
NRR_BASE = """
VAR _m = MAX ( dCalendario[InicioMes] )
VAR _b = EDATE ( _m, -12 )
VAR _t0 =
    CALCULATETABLE (
        SELECTCOLUMNS ( fSnapshotMRR, "ClienteID", fSnapshotMRR[ClienteID], "@v0", fSnapshotMRR[MRR] ),
        REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _b
    )
VAR _t1 =
    CALCULATETABLE (
        SELECTCOLUMNS ( fSnapshotMRR, "ClienteID", fSnapshotMRR[ClienteID], "@v1", fSnapshotMRR[MRR] ),
        REMOVEFILTERS ( dCalendario ), REMOVEFILTERS ( dPlano ), dCalendario[Data] = _m
    )
VAR _j = NATURALLEFTOUTERJOIN ( _t0, _t1 )
VAR _mrr0 = SUMX ( _t0, [@v0] )
"""
add("NRR %", F_RET, NRR_BASE + "RETURN IF ( _mrr0 > 0, DIVIDE ( SUMX ( _j, [@v1] ), _mrr0 ) )", PCT,
    "Net Revenue Retention 12 meses: MRR atual da base de 12 meses atrás ÷ MRR daquela base (inclui expansão).")
add("GRR %", F_RET, NRR_BASE + "RETURN IF ( _mrr0 > 0, DIVIDE ( SUMX ( _j, MIN ( [@v0], COALESCE ( [@v1], 0 ) ) ), _mrr0 ) )", PCT,
    "Gross Revenue Retention 12 meses (sem expansão, limitado a 100% por conta).")
add("Customer Retention 12M %", F_RET, NRR_BASE + "RETURN DIVIDE ( COUNTROWS ( FILTER ( _j, NOT ISBLANK ( [@v1] ) ) ), COUNTROWS ( _t0 ) )", PCT,
    "% de logos ativos há 12 meses que continuam ativos.")
add("Clientes Iniciais Cohort", F_RET, "SUM ( fCohortMensal[ClientesIniciais] )", INT)
add("Clientes Ativos Cohort", F_RET, "SUM ( fCohortMensal[ClientesAtivos] )", INT)
add("Cohort Retention %", F_RET, "DIVIDE ( [Clientes Ativos Cohort], [Clientes Iniciais Cohort] )", PCT)
add("Cohort Revenue Retention %", F_RET, "DIVIDE ( SUM ( fCohortMensal[MRRAtivo] ), SUM ( fCohortMensal[MRRInicial] ) )", PCT,
    "MRR restante do cohort ÷ MRR inicial (inclui expansão acumulada).")
add("Cohort Churn Acumulado %", F_RET, "IF ( NOT ISBLANK ( [Cohort Retention %] ), 1 - [Cohort Retention %] )", PCT)
add("Cohort Retenção Heatmap", F_RET, "IF ( MAX ( fCohortMensal[IdadeCohort] ) <= 12, [Cohort Retention %] )", PCT,
    "Retenção do cohort limitada a M0–M12 (alimenta o heatmap Deneb).", True)
HEALTH_M = "VAR _m = MAX ( dCalendario[InicioMes] )\nRETURN\n    CALCULATE ( {agg}, REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _m{flt} )"
add("Clientes Monitorados", F_RET, HEALTH_M.format(agg="COUNTROWS ( fUsoProduto )", flt=""), INT, "Contas ativas com Health Score no último mês.")
add("Clientes em Risco", F_RET, HEALTH_M.format(agg="COUNTROWS ( fUsoProduto )", flt=', fUsoProduto[FaixaHealth] IN { "Risco", "Crítico" }'), INT,
    "Contas nas faixas Risco ou Crítico no último mês do contexto.")
add("% Clientes em Risco", F_RET, "DIVIDE ( [Clientes em Risco], [Clientes Monitorados] )", PCT)
add("MRR em Risco", F_RET, """
VAR _m = MAX ( dCalendario[InicioMes] )
VAR _risco =
    CALCULATETABLE ( VALUES ( fUsoProduto[ClienteID] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _m, fUsoProduto[FaixaHealth] IN { "Risco", "Crítico" } )
RETURN
    CALCULATE ( SUM ( fSnapshotMRR[MRR] ), REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _m, TREATAS ( _risco, fSnapshotMRR[ClienteID] ) )""", MONEY)
add("% da Base (Health)", F_RET, "DIVIDE ( [Clientes Monitorados], CALCULATE ( [Clientes Monitorados], REMOVEFILTERS ( dFaixaHealth ) ) )", PCT)
add("Health Score Médio", F_RET, HEALTH_M.format(agg="AVERAGE ( fUsoProduto[HealthScore] )", flt=""), "0.0")
add("Clientes com Integração", F_RET, HEALTH_M.format(agg="COUNTROWS ( fUsoProduto )", flt=", fUsoProduto[IntegracoesAtivas] > 0"), INT)
add("% Clientes com Integração", F_RET, "DIVIDE ( [Clientes com Integração], [Clientes Monitorados] )", PCT)
add("Taxa de Adoção", F_RET, "DIVIDE ( " + HEALTH_M.format(agg="AVERAGE ( fUsoProduto[FuncionalidadesUsadas] )", flt="").replace("\n", " ") + ", 10 )", PCT,
    "Média de funcionalidades usadas ÷ 10 funcionalidades disponíveis.")

# ======================================================================= 03 GROWTH
add("Investimento Marketing", F_GRO, "SUM ( fMarketing[Investimento] )", MONEY)
add("Visitantes", F_GRO, "SUM ( fMarketing[Visitantes] )", INT)
add("Leads", F_GRO, "COUNTROWS ( fLeads )", INT)
add("MQL", F_GRO, 'CALCULATE ( COUNTROWS ( fLeads ), fLeads[MQL] = "Sim" )', INT)
add("SQL", F_GRO, 'CALCULATE ( COUNTROWS ( fLeads ), fLeads[SQL] = "Sim" )', INT)
add("Trials", F_GRO, "COUNTROWS ( fTrials )", INT)
add("Clientes Convertidos", F_GRO, 'CALCULATE ( COUNTROWS ( fTrials ), fTrials[Convertido] = "Sim" )', INT)
add("Novos Clientes Adquiridos", F_GRO, "COUNTROWS ( fAquisicao )", INT)
add("Lead → Trial %", F_GRO, "DIVIDE ( [Trials], [Leads] )", PCT)
add("Trial → Paid %", F_GRO, "DIVIDE ( [Clientes Convertidos], [Trials] )", PCT)
add("Lead → Cliente %", F_GRO, "DIVIDE ( [Novos Clientes Adquiridos], [Leads] )", "0.00%")
add("CAC", F_GRO, "DIVIDE ( SUM ( fAquisicao[CustoAquisicao] ), [Novos Clientes Adquiridos] )", MONEY,
    "Investimento alocado ÷ novos clientes da mesma janela e população (Σ custo alocado = investimento de marketing).")
add("ARPA Novos Clientes", F_GRO, "DIVIDE ( SUM ( fAquisicao[MRRInicial] ), [Novos Clientes Adquiridos] )", MONEY)
add("Margem Bruta Premissa", F_GRO, "0.80", PCT, "Premissa documentada de margem bruta SaaS (80%).")
add("Vida Útil Estimada", F_GRO, "IF ( NOT ISBLANK ( [Logo Churn %] ), MIN ( DIVIDE ( 1, [Logo Churn %], 60 ), 60 ) )", "0.0",
    "1 ÷ churn mensal de logos, limitada a 60 meses (premissa conservadora).")
add("LTV Estimado", F_GRO, "[ARPA] * [Margem Bruta Premissa] * [Vida Útil Estimada]", MONEY,
    "ESTIMATIVA: ARPA × margem bruta (80%) × vida útil (1/churn, máx. 60 meses).")
add("LTV:CAC", F_GRO, "DIVIDE ( [LTV Estimado], [CAC] )", '0.0"x"')
add("CAC Payback", F_GRO, "DIVIDE ( [CAC], [ARPA Novos Clientes] * [Margem Bruta Premissa] )", '0.0" meses"',
    "Meses de margem bruta do MRR inicial para recuperar o CAC.")
add("Receita por Canal", F_GRO, "[Ending MRR]", MONEY)
add("Eficiência por Canal", F_GRO, "[LTV:CAC]", '0.0"x"')

# ======================================================================= 04 PRODUCT
PROD = "VAR _m = MAX ( dCalendario[InicioMes] )\nRETURN\n    CALCULATE ( {agg}, REMOVEFILTERS ( dCalendario ), dCalendario[Data] = _m{flt} )"
add("Usuários Ativos", F_PRO, PROD.format(agg="SUM ( fUsoProduto[UsuariosAtivos] )", flt=""), INT)
add("DAU", F_PRO, PROD.format(agg="SUM ( fUsoProduto[DAU] )", flt=""), INT, "Usuários ativos diários médios (último mês).")
add("WAU", F_PRO, PROD.format(agg="SUM ( fUsoProduto[WAU] )", flt=""), INT)
add("MAU", F_PRO, PROD.format(agg="SUM ( fUsoProduto[MAU] )", flt=""), INT)
add("DAU/MAU %", F_PRO, "DIVIDE ( [DAU], [MAU] )", PCT, "Stickiness.")
add("Logins", F_PRO, "SUM ( fUsoProduto[Logins] )", INT)
add("Sessões", F_PRO, "SUM ( fUsoProduto[Sessoes] )", INT)
add("Automações", F_PRO, "SUM ( fUsoProduto[Automacoes] )", INT)
add("Integrações Ativas", F_PRO, PROD.format(agg="SUM ( fUsoProduto[IntegracoesAtivas] )", flt=""), INT)
add("Funcionalidades Utilizadas", F_PRO, PROD.format(agg="AVERAGE ( fUsoProduto[FuncionalidadesUsadas] )", flt=""), "0.0")
add("Adoção Média", F_PRO, "DIVIDE ( [Funcionalidades Utilizadas], 10 )", PCT)
add("Health Score", F_PRO, "[Health Score Médio]", "0.0")
add("Clientes com Baixa Adoção", F_PRO, PROD.format(agg="COUNTROWS ( fUsoProduto )", flt=", fUsoProduto[FuncionalidadesUsadas] <= 3"), INT)
add("Clientes Potencial Upgrade", F_PRO, PROD.format(agg="COUNTROWS ( fUsoProduto )", flt=', fUsoProduto[PotencialUpgrade] = "Sim"'), INT,
    "Starter/Growth/Pro com uso perto do limite de usuários, alta adoção e Health ≥ 74.")
add("Eventos de Produto", F_PRO, "SUM ( fEventosProduto[Eventos] )", INT)

# ======================================================================= 05 FINANCIAL
add("Booking", F_FIN, "SUM ( fAssinaturas[ValorContrato] )", MONEY, "Valor contratado (ACV do contrato: 12× MRR anual, 1× mensal).")
add("Billing", F_FIN, "SUM ( fFinanceiro[ValorLiquido] )", MONEY, "Valor faturado (faturas emitidas). Anual é faturado antecipadamente.")
add("Receita Recebida", F_FIN, "SUM ( fFinanceiro[ValorRecebido] )", MONEY)
add("Descontos Concedidos", F_FIN, "SUM ( fFinanceiro[Desconto] )", MONEY)
add("Estornos", F_FIN, "SUM ( fFinanceiro[ValorEstornado] )", MONEY)
add("Inadimplência", F_FIN, 'CALCULATE ( SUM ( fFinanceiro[ValorLiquido] ), fFinanceiro[StatusPagamento] = "Inadimplente" )', MONEY)
add("% Inadimplência", F_FIN, "DIVIDE ( [Inadimplência], [Billing] )", "0.00%")
add("Receita Não Recorrente", F_FIN, 'CALCULATE ( SUM ( fFinanceiro[ValorLiquido] ), fFinanceiro[TipoCobranca] = "Único" )', MONEY)
add("Receita Reconhecida", F_FIN, "SUM ( fSnapshotMRR[ReceitaRecorrenteReconhecida] ) + [Receita Não Recorrente]", MONEY,
    "Revenue: MRR reconhecido mês a mês + serviços não recorrentes (implantação/treinamento).")
add("Tickets", F_FIN, "COUNTROWS ( fSuporte )", INT)
add("CSAT Médio", F_FIN, "AVERAGE ( fSuporte[Satisfacao] )", "0.00")
add("% Tickets no SLA", F_FIN, 'DIVIDE ( CALCULATE ( COUNTROWS ( fSuporte ), fSuporte[DentroSLA] = "Sim" ), [Tickets] )', PCT)

# ======================================================================= 08 FORMATTING (cores)
add("Cor Coluna MRR", F_FMT, """
VAR _sel = CALCULATE ( MAX ( dCalendario[InicioMes] ), ALLSELECTED ( dCalendario ) )
VAR _m = MAX ( dCalendario[InicioMes] )
VAR _g = [MRR MoM %]
RETURN
    SWITCH ( TRUE (), _m = _sel, "#6736F5", _g < 0, "#FF607A", _g >= 0.02, "#00B8F5", "#1678FF" )""", None,
    "Mês atual = violeta; queda = vermelho; crescimento forte = ciano; demais = azul.")
add("Cor Plano", F_FMT, "MAX ( dPlano[CorPlano] )")
add("Cor Movimento", F_FMT, "MAX ( dTipoMovimento[CorMovimento] )")
add("Cor Faixa Health", F_FMT, "MAX ( dFaixaHealth[CorFaixa] )")
add("Cor Destaque Expansion", F_FMT, """
VAR _v = [Expansion MRR]
VAR _max = CALCULATE ( MAXX ( VALUES ( dPlano[Plano] ), [Expansion MRR] ), ALLSELECTED ( dPlano ) )
RETURN
    IF ( _v = _max, "#00D7C0", "#1678FF" )""")
add("Cor CAC Canal", F_FMT, """
VAR _c = [CAC]
VAR _ref = CALCULATE ( [CAC], ALLSELECTED ( dCanalAquisicao ) )
RETURN
    SWITCH ( TRUE (), ISBLANK ( _c ), "#6E86B3", _c <= _ref * 0.8, "#00D7C0", _c >= _ref * 1.2, "#FF607A", "#1678FF" )""",
    None, "CAC ≤ 80% da referência = turquesa; ≥ 120% = vermelho.")
add("Cor LTV CAC", F_FMT, """
VAR _r = [LTV:CAC]
RETURN
    SWITCH ( TRUE (), ISBLANK ( _r ), "#6E86B3", _r >= 3, "#00D7C0", _r >= 1.5, "#F5A524", "#FF607A" )""", None,
    "≥ 3x saudável; 1,5–3x atenção; < 1,5x ineficiente.")
for _n, _m in [("Tbl Novo", "[New MRR]"), ("Tbl Expansão", "[Expansion MRR]"), ("Tbl Contração", "[Contraction MRR]"), ("Tbl Churn", "[Churned MRR]"), ("Tbl Net New", "[Net New MRR]")]:
    add(_n, F_FMT, f"DIVIDE ( {_m}, 1000 )", "#,0.0", "Valor em R$ mil para tabelas compactas.")
add("Ordem Plano", F_FMT, "MAX ( dPlano[OrdemPlano] )", "0", hidden=True)


# --------------------------------------------------------------------- helpers de formatação DAX
def fmt_money(v):
    return (f'SWITCH ( TRUE (), ISBLANK ( {v} ), "–", ABS ( {v} ) >= 1e6, "R$ " & FORMAT ( {v} / 1e6, "#,0.00", "pt-BR" ) & " mi", '
            f'ABS ( {v} ) >= 1e3, "R$ " & FORMAT ( {v} / 1e3, "#,0.0", "pt-BR" ) & " mil", "R$ " & FORMAT ( {v}, "#,0", "pt-BR" ) )')


def fmt_val(kind, v):
    if kind == "money":
        return fmt_money(v)
    if kind == "int":
        return f'IF ( ISBLANK ( {v} ), "–", FORMAT ( {v}, "#,0", "pt-BR" ) )'
    if kind == "pct":
        return f'IF ( ISBLANK ( {v} ), "–", FORMAT ( {v}, "0.0%", "pt-BR" ) )'
    if kind == "pct2":
        return f'IF ( ISBLANK ( {v} ), "–", FORMAT ( {v}, "0.00%", "pt-BR" ) )'
    if kind == "x":
        return f'IF ( ISBLANK ( {v} ), "–", FORMAT ( {v}, "0.0", "pt-BR" ) & "x" )'
    if kind == "mes":
        return f'IF ( ISBLANK ( {v} ), "–", FORMAT ( {v}, "0.0", "pt-BR" ) & " <small>meses</small>" )'
    raise ValueError(kind)


# --------------------------------------------------------------------- CSS / componentes
CSS = ("<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden}"
       ".nx,.nx *{box-sizing:border-box;font-family:'Segoe UI',Inter,Arial,sans-serif}"
       ".nx{color:#FFFFFF}"
       "@keyframes nxin{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
       "@keyframes nxglow{0%,100%{box-shadow:0 0 0 0 rgba(0,184,245,.0),inset 0 1px 0 rgba(255,255,255,.08)}50%{box-shadow:0 0 18px 0 rgba(0,184,245,.25),inset 0 1px 0 rgba(255,255,255,.08)}}"
       "@keyframes nxpulse{0%,100%{box-shadow:0 0 0 0 rgba(255,96,122,.45)}50%{box-shadow:0 0 0 7px rgba(255,96,122,0)}}"
       "@keyframes nxgrow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
       "@keyframes nxdash{from{stroke-dashoffset:400}to{stroke-dashoffset:0}}"
       ".card{position:relative;height:100vh;border-radius:18px;padding:16px 18px 12px 18px;overflow:hidden;"
       "background:linear-gradient(135deg,rgba(22,120,255,.22) 0%,rgba(103,54,245,.12) 55%,rgba(5,13,32,.30) 100%);"
       "border:1px solid rgba(0,184,245,.38);animation:nxin .5s ease both,nxglow 5s ease-in-out 1s infinite}"
       ".card:before{content:'';position:absolute;right:-60px;top:-60px;width:180px;height:180px;border-radius:50%;"
       "background:radial-gradient(circle,rgba(0,184,245,.22),rgba(0,184,245,0) 70%)}"
       ".card.v{border-color:rgba(103,54,245,.55)}.card.v:before{background:radial-gradient(circle,rgba(103,54,245,.30),rgba(103,54,245,0) 70%)}"
       ".card.al{border-color:rgba(255,96,122,.65);animation:nxin .5s ease both,nxpulse 2.4s ease-in-out 1s infinite}"
       ".hd{display:flex;align-items:center;gap:12px;position:relative}"
       ".ic{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;"
       "background:linear-gradient(135deg,rgba(0,184,245,.28),rgba(103,54,245,.28));border:1px solid rgba(255,255,255,.10)}"
       ".ic svg{width:22px;height:22px}"
       ".lb{font-size:14px;font-weight:600;color:#DCE6F7;letter-spacing:.01em;white-space:nowrap}"
       ".vl{position:relative;font-size:34px;font-weight:700;line-height:1.05;margin:12px 0 6px 2px;letter-spacing:-.01em;white-space:nowrap}"
       ".vl small{font-size:16px;font-weight:600;color:#A9BBD8}"
       ".dl{position:relative;font-size:13px;font-weight:700;white-space:nowrap}.cmp{position:relative;font-size:11.5px;color:#8FA3C8;margin-top:2px;white-space:nowrap}"
       ".up{color:#00D7C0}.dn{color:#FF607A}.nt{color:#A9BBD8}"
       ".sp{position:absolute;right:14px;bottom:14px;width:46%;height:44%}"
       ".sp polyline{stroke-dasharray:400;animation:nxdash 1.4s ease-out both}"
       ".pl{filter:drop-shadow(0 0 4px #00B8F5)}"
       ".hdr{padding:4px 0 0 2px}.eb{display:flex;align-items:center;gap:10px;font-size:12px;font-weight:700;letter-spacing:.28em;color:#8FA3C8}"
       ".eb span{display:inline-block;width:34px;height:2px;border-radius:2px;background:linear-gradient(90deg,#00B8F5,#6736F5)}"
       ".tt{font-size:46px;font-weight:700;line-height:1.08;letter-spacing:-.01em;margin-top:4px;white-space:nowrap}"
       ".tt b{font-weight:700;background:linear-gradient(90deg,#00B8F5,#1678FF 45%,#6736F5);-webkit-background-clip:text;background-clip:text;color:transparent}"
       ".st{font-size:15px;color:#A9BBD8;margin-top:2px;white-space:nowrap}"
       ".chips{display:flex;gap:8px;align-items:center;flex-wrap:nowrap;overflow:hidden;height:100vh}"
       ".chip{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 12px;border-radius:13px;white-space:nowrap;"
       "background:rgba(12,28,64,.65);border:1px solid rgba(0,184,245,.30);color:#DCE6F7;font-size:11.5px}"
       ".chip b{font-size:10px;letter-spacing:.12em;color:#00B8F5;font-weight:700}.chip.on{border-color:rgba(103,54,245,.8);background:rgba(103,54,245,.22)}"
       ".tip{padding:14px 16px;height:100vh}.tip h4{margin:0 0 2px 0;font-size:11px;letter-spacing:.2em;color:#00B8F5}"
       ".tip h3{margin:0 0 10px 0;font-size:20px;font-weight:700}.tip table{width:100%;border-collapse:collapse}"
       ".tip td{font-size:12.5px;padding:4px 0;border-bottom:1px solid rgba(169,187,216,.12);color:#A9BBD8}.tip td+td{text-align:right;color:#fff;font-weight:600}"
       ".bar{height:6px;border-radius:3px;background:rgba(169,187,216,.15);margin-top:10px;overflow:hidden}"
       ".bar i{display:block;height:6px;border-radius:3px;background:linear-gradient(90deg,#00B8F5,#6736F5);transform-origin:left;animation:nxgrow .8s ease both}"
       "</style>")
add("HTML CSS", F_HTML, '"' + CSS.replace('"', '""') + '"', None, "Folha de estilo compartilhada (design system NEXORA) para todos os componentes HTML.", True)

ICONS = {
    "mrr": "<path d='M4 20V10M10 20V4M16 20v-7M22 20H2'/>",
    "arr": "<path d='M3 12a9 9 0 0 1 15.5-6.2L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.2L3 16M3 21v-5h5'/>",
    "users": "<circle cx='9' cy='8' r='3.5'/><path d='M2.5 20c.8-3.6 3.4-5.5 6.5-5.5s5.7 1.9 6.5 5.5M16 4.8a3.3 3.3 0 0 1 0 6.4M18.5 14.8c1.6.8 2.6 2.5 3 5.2'/>",
    "nrr": "<path d='M12 3a9 9 0 1 0 9 9M21 3v6h-6M21 9l-6 6-3-3-5 5'/>",
    "new": "<circle cx='12' cy='12' r='9'/><path d='M12 8v8M8 12h8'/>",
    "exp": "<path d='M4 20 20 4M9 4h11v11'/>",
    "churn": "<path d='M4 4l16 16M20 9v11H9'/>",
    "net": "<path d='M3 17l6-6 4 4 8-8M15 7h6v6'/>",
    "risk": "<path d='M12 3 2 20h20L12 3zM12 10v4M12 17v.5'/>",
    "cac": "<circle cx='12' cy='12' r='9'/><circle cx='12' cy='12' r='5'/><circle cx='12' cy='12' r='1.5'/>",
    "ltv": "<path d='M6 3h12l4 6-10 12L2 9l4-6zM2 9h20M12 21 8 9l4-6 4 6-4 12'/>",
    "ratio": "<path d='M12 3v18M5 7h14M5 7l-3 7a3.5 3.5 0 0 0 6 0L5 7zM19 7l-3 7a3.5 3.5 0 0 0 6 0l-3-7z'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 3'/>",
    "churnpct": "<path d='M5 19 19 5M7.5 7.5h.01M16.5 16.5h.01'/><circle cx='7' cy='7' r='2.5'/><circle cx='17' cy='17' r='2.5'/>",
}


def icon_svg(k):
    return ("<svg viewBox='0 0 24 24' fill='none' stroke='#FFFFFF' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>"
            + ICONS[k] + "</svg>")


def spark_dax(measure, sid, c2="#6736F5", area="#00B8F5"):
    return f"""VAR _sm = MAX ( dCalendario[InicioMes] )
VAR _st =
    FILTER (
        ADDCOLUMNS (
            CALCULATETABLE ( VALUES ( dCalendario[InicioMes] ), REMOVEFILTERS ( dCalendario ), dCalendario[InicioMes] > EDATE ( _sm, -12 ), dCalendario[InicioMes] <= _sm ),
            "@v", VAR _mm = dCalendario[InicioMes] RETURN CALCULATE ( [{measure}], REMOVEFILTERS ( dCalendario ), dCalendario[InicioMes] = _mm )
        ),
        NOT ISBLANK ( [@v] )
    )
VAR _sn = COUNTROWS ( _st )
VAR _sx0 = MINX ( _st, dCalendario[InicioMes] )
VAR _sx1 = MAXX ( _st, dCalendario[InicioMes] )
VAR _sy0 = MINX ( _st, [@v] )
VAR _sy1 = MAXX ( _st, [@v] )
VAR _spts =
    CONCATENATEX (
        _st,
        FORMAT ( 4 + DIVIDE ( INT ( dCalendario[InicioMes] - _sx0 ), INT ( _sx1 - _sx0 ), 0 ) * 152, "0.0", "en-US" ) & ","
            & FORMAT ( 54 - DIVIDE ( [@v] - _sy0, _sy1 - _sy0, 0.5 ) * 46, "0.0", "en-US" ),
        " ", dCalendario[InicioMes], ASC
    )
VAR _sly = FORMAT ( 54 - DIVIDE ( MAXX ( FILTER ( _st, dCalendario[InicioMes] = _sx1 ), [@v] ) - _sy0, _sy1 - _sy0, 0.5 ) * 46, "0.0", "en-US" )
VAR _spark =
    IF (
        _sn >= 2,
        "<svg class='sp' viewBox='0 0 160 60' preserveAspectRatio='none'><defs><linearGradient id='l{sid}' x1='0' x2='1'><stop offset='0' stop-color='#00B8F5'/><stop offset='1' stop-color='{c2}'/></linearGradient>"
            & "<linearGradient id='a{sid}' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='{area}' stop-opacity='.38'/><stop offset='1' stop-color='{area}' stop-opacity='0'/></linearGradient></defs>"
            & "<polygon points='4,60 " & _spts & " 156,60' fill='url(#a{sid})'/>"
            & "<polyline points='" & _spts & "' fill='none' stroke='url(#l{sid})' stroke-width='2.6' stroke-linejoin='round' stroke-linecap='round' vector-effect='non-scaling-stroke'/>"
            & "<circle class='pl' cx='156' cy='" & _sly & "' r='3.2' fill='#FFFFFF'/></svg>"
    )"""


def card(name, label, measure, kind, icon, comp="flow", good=1, dtype="pct", sid=None, variant="", alert_rule=None):
    """comp: 'stock' (vs 12 meses antes) | 'flow' (vs período anterior equivalente; fallback 12m vs 12m)."""
    sid = sid or name.replace(" ", "")
    if comp == "stock":
        cmp_block = f"""VAR _m = MAX ( dCalendario[InicioMes] )
VAR _cur = [{measure}]
VAR _base = CALCULATE ( [{measure}], REMOVEFILTERS ( dCalendario ), dCalendario[InicioMes] = EDATE ( _m, -12 ) )
VAR _lbl = "vs. 12 meses antes (" & FORMAT ( EDATE ( _m, -12 ), "mmm/yy", "pt-BR" ) & ")"
VAR _v = _cur"""
    else:
        cmp_block = f"""VAR _mx = MAX ( dCalendario[InicioMes] )
VAR _mn = MIN ( dCalendario[InicioMes] )
VAR _nm = DATEDIFF ( _mn, _mx, MONTH ) + 1
VAR _pi = EDATE ( _mn, - _nm )
VAR _temPrev = _pi >= DATE ( 2024, 1, 1 )
VAR _v = [{measure}]
VAR _cur =
    IF ( _temPrev, _v, CALCULATE ( [{measure}], REMOVEFILTERS ( dCalendario ), dCalendario[InicioMes] > EDATE ( _mx, -12 ), dCalendario[InicioMes] <= _mx ) )
VAR _base =
    IF (
        _temPrev,
        CALCULATE ( [{measure}], REMOVEFILTERS ( dCalendario ), dCalendario[InicioMes] >= _pi, dCalendario[InicioMes] < _mn ),
        IF ( EDATE ( _mx, -23 ) >= DATE ( 2024, 1, 1 ), CALCULATE ( [{measure}], REMOVEFILTERS ( dCalendario ), dCalendario[InicioMes] > EDATE ( _mx, -24 ), dCalendario[InicioMes] <= EDATE ( _mx, -12 ) ) )
    )
VAR _lbl = IF ( _temPrev, "vs. período anterior equivalente", "últimos 12m vs. 12m anteriores" )"""
    if dtype == "pp":
        dcalc = 'VAR _d = IF ( NOT ISBLANK ( _base ) && NOT ISBLANK ( _cur ), ( _cur - _base ) * 100 )\nVAR _dtxt = FORMAT ( ABS ( _d ), "0.0", "pt-BR" ) & " p.p."'
    else:
        dcalc = 'VAR _d = IF ( NOT ISBLANK ( _base ) && _base <> 0, DIVIDE ( _cur - _base, ABS ( _base ) ) )\nVAR _dtxt = FORMAT ( ABS ( _d ), "0.0%", "pt-BR" )'
    good_expr = "_d > 0" if good == 1 else "_d < 0"
    alert = alert_rule or "FALSE ()"
    dax = f"""{cmp_block}
{dcalc}
VAR _cls = IF ( ISBLANK ( _d ) || _d = 0, "nt", IF ( {good_expr}, "up", "dn" ) )
VAR _arrow = IF ( ISBLANK ( _d ), "", IF ( _d >= 0, "▲ ", "▼ " ) )
VAR _txt = {fmt_val(kind, "_v")}
{spark_dax(measure, sid)}
VAR _alert = {alert}
RETURN
    [HTML CSS] & "<div class='nx card {variant}" & IF ( _alert, " al", "" ) & "'><div class='hd'><div class='ic'>{icon_svg(icon)}</div><div class='lb'>{label}</div></div>"
        & "<div class='vl'>" & _txt & "</div>"
        & "<div class='dl " & _cls & "'>" & IF ( ISBLANK ( _d ), "<span class='nt'>sem base comparável</span>", _arrow & _dtxt ) & "</div>"
        & "<div class='cmp'>" & IF ( ISBLANK ( _d ), "histórico insuficiente", _lbl ) & "</div>"
        & _spark & "</div>\""""
    add(name, F_HTML, dax, None, f"Card KPI HTML de [{measure}] com variação e sparkline SVG (12 meses).")


# ---- cards por página
card("HTML Card MRR", "MRR Atual (Ending MRR)", "Ending MRR", "money", "mrr", "stock")
card("HTML Card ARR", "ARR", "ARR", "money", "arr", "stock", variant="v")
card("HTML Card Clientes", "Clientes Ativos", "Clientes Ativos", "int", "users", "stock")
card("HTML Card NRR", "NRR (12 meses)", "NRR %", "pct", "nrr", "stock", dtype="pp", variant="v")
card("HTML Card New MRR", "New MRR", "New MRR", "money", "new", "flow")
card("HTML Card Expansion", "Expansion MRR", "Expansion MRR", "money", "exp", "flow", variant="v")
card("HTML Card Churned", "Churned MRR", "Churned MRR", "money", "churn", "flow", good=-1)
card("HTML Card Net New", "Net New MRR", "Net New MRR", "money", "net", "flow", variant="v")
card("HTML Card Clientes R", "Clientes Ativos", "Clientes Ativos", "int", "users", "stock", sid="CliR")
card("HTML Card Logo Churn", "Logo Churn (média mensal)", "Logo Churn %", "pct2", "churnpct", "flow", good=-1, dtype="pp",
     alert_rule="_v >= 0.03")
card("HTML Card NRR R", "NRR (12 meses)", "NRR %", "pct", "nrr", "stock", dtype="pp", sid="NrrR", variant="v")
card("HTML Card Risco", "Clientes em Risco", "Clientes em Risco", "int", "risk", "stock", good=-1,
     alert_rule="DIVIDE ( _v, [Clientes Monitorados] ) >= 0.15")
card("HTML Card CAC", "CAC", "CAC", "money", "cac", "flow", good=-1)
card("HTML Card LTV", "LTV Estimado", "LTV Estimado", "money", "ltv", "flow", variant="v")
card("HTML Card LTV CAC", "LTV:CAC", "LTV:CAC", "x", "ratio", "flow", alert_rule="_v < 3")
card("HTML Card Payback", "CAC Payback", "CAC Payback", "mes", "clock", "flow", good=-1, variant="v")

# ---- cabeçalhos
HDRS = {
    "Executive": ("01 · EXECUTIVE SAAS", "Visão", "Executiva", "Revenue, retenção e crescimento em uma única visão."),
    "Revenue": ("02 · REVENUE INTELLIGENCE", "Receita e", "Expansão", "Como o MRR cresce, expande e se perde — mês a mês."),
    "Customer": ("03 · CUSTOMER & RETENTION", "Clientes e", "Retenção", "Cohorts, churn, saúde da base e contas em risco."),
    "Growth": ("04 · GROWTH & UNIT ECONOMICS", "Growth e", "Unit Economics", "Eficiência de aquisição e qualidade do crescimento."),
}
for k, (eb, w1, w2, st) in HDRS.items():
    add(f"HTML Header {k}", F_HTML, f"""[HTML CSS] & "<div class='nx hdr'><div class='eb'><span></span>{eb}</div><div class='tt'>{w1} <b>{w2}</b></div><div class='st'>{st}</div></div>\"""",
        None, "Cabeçalho HTML da página.")

add("HTML Filtros Ativos", F_HTML, """
VAR _per =
    IF (
        ISFILTERED ( dCalendario ),
        FORMAT ( MIN ( dCalendario[Data] ), "mmm/yy", "pt-BR" ) & " – " & FORMAT ( MAX ( dCalendario[Data] ), "mmm/yy", "pt-BR" ),
        "jan/24 – out/26"
    )
VAR _chip = ( _rot, _txt ) => ""
VAR _pl = IF ( ISFILTERED ( dPlano[Plano] ), VAR _n = COUNTROWS ( VALUES ( dPlano[Plano] ) ) RETURN IF ( _n <= 2, CONCATENATEX ( VALUES ( dPlano[Plano] ), dPlano[Plano], ", " ), _n & " planos" ) )
VAR _cn = IF ( ISFILTERED ( dCanalAquisicao[Canal] ), VAR _n = COUNTROWS ( VALUES ( dCanalAquisicao[Canal] ) ) RETURN IF ( _n <= 2, CONCATENATEX ( VALUES ( dCanalAquisicao[Canal] ), dCanalAquisicao[Canal], ", " ), _n & " canais" ) )
VAR _sg = IF ( ISFILTERED ( dSegmento[Segmento] ), VAR _n = COUNTROWS ( VALUES ( dSegmento[Segmento] ) ) RETURN IF ( _n <= 2, CONCATENATEX ( VALUES ( dSegmento[Segmento] ), dSegmento[Segmento], ", " ), _n & " segmentos" ) )
VAR _pt = IF ( ISFILTERED ( dPorte[Porte] ), VAR _n = COUNTROWS ( VALUES ( dPorte[Porte] ) ) RETURN IF ( _n <= 2, CONCATENATEX ( VALUES ( dPorte[Porte] ), dPorte[Porte], ", " ), _n & " portes" ) )
VAR _cb = IF ( ISFILTERED ( dCliente[TipoCobranca] ), CONCATENATEX ( VALUES ( dCliente[TipoCobranca] ), dCliente[TipoCobranca], ", " ) )
VAR _co = IF ( ISFILTERED ( dCohort ), VAR _n = COUNTROWS ( VALUES ( dCohort[CohortAno] ) ) RETURN IF ( _n <= 2, CONCATENATEX ( VALUES ( dCohort[CohortAno] ), dCohort[CohortAno], ", " ), _n & " anos" ) )
VAR _algum = NOT ISBLANK ( _pl ) || NOT ISBLANK ( _cn ) || NOT ISBLANK ( _sg ) || NOT ISBLANK ( _pt ) || NOT ISBLANK ( _cb ) || NOT ISBLANK ( _co )
RETURN
    [HTML CSS] & "<div class='nx chips'>"
        & "<span class='chip" & IF ( ISFILTERED ( dCalendario ), " on", "" ) & "'><b>PERÍODO</b>" & _per & "</span>"
        & IF ( NOT ISBLANK ( _pl ), "<span class='chip on'><b>PLANO</b>" & _pl & "</span>" )
        & IF ( NOT ISBLANK ( _cn ), "<span class='chip on'><b>CANAL</b>" & _cn & "</span>" )
        & IF ( NOT ISBLANK ( _sg ), "<span class='chip on'><b>SEGMENTO</b>" & _sg & "</span>" )
        & IF ( NOT ISBLANK ( _pt ), "<span class='chip on'><b>PORTE</b>" & _pt & "</span>" )
        & IF ( NOT ISBLANK ( _cb ), "<span class='chip on'><b>COBRANÇA</b>" & _cb & "</span>" )
        & IF ( NOT ISBLANK ( _co ), "<span class='chip on'><b>COHORT</b>" & _co & "</span>" )
        & IF ( NOT _algum, "<span class='chip'><b>FILTROS</b>Todos os planos, canais e segmentos</span>" )
        & "</div>\"""".replace('VAR _chip = ( _rot, _txt ) => ""\n', ""), None, "Chips com os filtros aplicados.")

# ---- tooltips HTML
add("HTML TT MRR", F_HTML, """
VAR _m = MAX ( dCalendario[InicioMes] )
VAR _mom = [MRR MoM %]
RETURN
    [HTML CSS] & "<div class='nx tip'><h4>MRR · " & UPPER ( FORMAT ( _m, "mmm/yyyy", "pt-BR" ) ) & "</h4><h3>" & """ + fmt_money("[Ending MRR]") + """ & "</h3><table>"
        & "<tr><td>Variação vs. mês anterior</td><td style='color:" & IF ( _mom < 0, "#FF607A", "#00D7C0" ) & "'>" & IF ( ISBLANK ( _mom ), "–", FORMAT ( _mom, "+0.0%;-0.0%", "pt-BR" ) ) & "</td></tr>"
        & "<tr><td>New MRR</td><td>" & """ + fmt_money("[New MRR]") + """ & "</td></tr>"
        & "<tr><td>Expansion MRR</td><td>" & """ + fmt_money("[Expansion MRR]") + """ & "</td></tr>"
        & "<tr><td>Churned + Contraction</td><td style='color:#FF607A'>" & """ + fmt_money("([Churned MRR] + [Contraction MRR])") + """ & "</td></tr>"
        & "<tr><td>Net New MRR</td><td>" & """ + fmt_money("[Net New MRR]") + """ & "</td></tr></table>"
        & "<div class='bar'><i style='width:" & FORMAT ( MIN ( 1, MAX ( 0, DIVIDE ( [New MRR] + [Expansion MRR], [New MRR] + [Expansion MRR] + [Churned MRR] + [Contraction MRR] ) ) ) * 100, "0", "en-US" ) & "%'></i></div></div>\"""",
    None, "Tooltip de MRR (página de dica de ferramenta).")
add("HTML TT Clientes", F_HTML, """
VAR _m = MAX ( dCalendario[InicioMes] )
RETURN
    [HTML CSS] & "<div class='nx tip'><h4>CLIENTES · " & UPPER ( FORMAT ( _m, "mmm/yyyy", "pt-BR" ) ) & "</h4><h3>" & FORMAT ( [Clientes Ativos], "#,0", "pt-BR" ) & " ativos</h3><table>"
        & "<tr><td>Cancelados</td><td style='color:#FF607A'>" & FORMAT ( [Clientes Cancelados] + 0, "#,0", "pt-BR" ) & "</td></tr>"
        & "<tr><td>Reativados</td><td style='color:#00D7C0'>" & FORMAT ( [Clientes Reativados] + 0, "#,0", "pt-BR" ) & "</td></tr>"
        & "<tr><td>Logo churn (mensal)</td><td>" & IF ( ISBLANK ( [Logo Churn %] ), "–", FORMAT ( [Logo Churn %], "0.00%", "pt-BR" ) ) & "</td></tr>"
        & "<tr><td>Health Score médio</td><td>" & IF ( ISBLANK ( [Health Score Médio] ), "–", FORMAT ( [Health Score Médio], "0.0", "pt-BR" ) ) & "</td></tr>"
        & "<tr><td>Clientes em risco</td><td>" & FORMAT ( [Clientes em Risco] + 0, "#,0", "pt-BR" ) & "</td></tr></table></div>\"""",
    None, "Tooltip de clientes.")
add("HTML TT Canal", F_HTML, """
VAR _c = SELECTEDVALUE ( dCanalAquisicao[Canal], "Canais selecionados" )
VAR _r = [LTV:CAC]
RETURN
    [HTML CSS] & "<div class='nx tip'><h4>CANAL DE AQUISIÇÃO</h4><h3>" & _c & "</h3><table>"
        & "<tr><td>Investimento</td><td>" & """ + fmt_money("[Investimento Marketing]") + """ & "</td></tr>"
        & "<tr><td>Leads</td><td>" & FORMAT ( [Leads] + 0, "#,0", "pt-BR" ) & "</td></tr>"
        & "<tr><td>Clientes convertidos</td><td>" & FORMAT ( [Novos Clientes Adquiridos] + 0, "#,0", "pt-BR" ) & "</td></tr>"
        & "<tr><td>CAC</td><td>" & """ + fmt_money("[CAC]") + """ & "</td></tr>"
        & "<tr><td>LTV:CAC</td><td style='color:" & [Cor LTV CAC] & "'>" & IF ( ISBLANK ( _r ), "–", FORMAT ( _r, "0.0", "pt-BR" ) & "x" ) & "</td></tr></table></div>\"""",
    None, "Tooltip de canal.")

# ---- SVG em tabelas (dataCategory ImageUrl)
add("SVG Barra CAC", F_HTML, """
VAR _v = [CAC]
VAR _max = MAXX ( ALLSELECTED ( dCanalAquisicao[Canal] ), [CAC] )
VAR _w = FORMAT ( MAX ( 0, MIN ( 1, DIVIDE ( _v, _max ) ) ) * 100, "0.0", "en-US" )
VAR _col = SWITCH ( [Cor CAC Canal], "#00D7C0", "rgb(0,215,192)", "#FF607A", "rgb(255,96,122)", "rgb(22,120,255)" )
VAR _lb = "R$ " & FORMAT ( _v, "#,0", "pt-BR" )
RETURN
    IF ( NOT ISBLANK ( _v ), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='190' height='22' viewBox='0 0 190 22'><rect x='0' y='7' width='100' height='8' rx='4' fill='rgb(30,48,90)'/><rect x='0' y='7' width='" & _w & "' height='8' rx='4' fill='" & _col & "'/><text x='108' y='15.5' font-family='Segoe UI,Arial' font-size='12' font-weight='600' fill='rgb(255,255,255)'>" & _lb & "</text></svg>" )""",
    None, "Barra SVG de CAC (escala relativa ao maior CAC selecionado).", cat="ImageUrl")
add("SVG Barra LTV CAC", F_HTML, """
VAR _v = [LTV:CAC]
VAR _w = FORMAT ( MAX ( 0, MIN ( 1, DIVIDE ( _v, 10 ) ) ) * 100, "0.0", "en-US" )
VAR _col = SWITCH ( [Cor LTV CAC], "#00D7C0", "rgb(0,215,192)", "#F5A524", "rgb(245,165,36)", "rgb(255,96,122)" )
VAR _lb = FORMAT ( _v, "0.0", "pt-BR" ) & "x"
RETURN
    IF ( NOT ISBLANK ( _v ), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='170' height='22' viewBox='0 0 170 22'><rect x='0' y='7' width='100' height='8' rx='4' fill='rgb(30,48,90)'/><rect x='0' y='7' width='" & _w & "' height='8' rx='4' fill='" & _col & "'/><rect x='29' y='3' width='2' height='16' fill='rgb(169,187,216)'/><text x='108' y='15.5' font-family='Segoe UI,Arial' font-size='12' font-weight='700' fill='" & _col & "'>" & _lb & "</text></svg>" )""",
    None, "Barra SVG de LTV:CAC (escala 0–10x; marcador em 3x).", cat="ImageUrl")
add("SVG Status Health", F_HTML, """
VAR _h = [Health Score Médio]
VAR _col = SWITCH ( TRUE (), ISBLANK ( _h ), "rgb(110,134,179)", _h >= 75, "rgb(0,215,192)", _h >= 55, "rgb(22,120,255)", _h >= 35, "rgb(245,165,36)", "rgb(255,96,122)" )
RETURN
    IF ( NOT ISBLANK ( _h ), "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='90' height='22' viewBox='0 0 90 22'><circle cx='9' cy='11' r='5' fill='" & _col & "'/><text x='20' y='15.5' font-family='Segoe UI,Arial' font-size='12' font-weight='600' fill='rgb(255,255,255)'>" & FORMAT ( _h, "0", "pt-BR" ) & "</text></svg>" )""",
    None, "Indicador SVG de status do Health Score.", cat="ImageUrl")

# ---- Deneb (campos auxiliares)
add("Valor Etapa Waterfall", F_HTML, """
VAR _e = SELECTEDVALUE ( dEtapaWaterfall[Etapa] )
RETURN
    COALESCE (
        SWITCH (
            _e,
            "MRR inicial", [Beginning MRR],
            "Novo", [New MRR],
            "Expansão", [Expansion MRR],
            "Reativação", [Reactivation MRR],
            "Migração planos", [Migração Líquida MRR],
            "Contração", - [Contraction MRR],
            "Churn", - [Churned MRR],
            "MRR final", [Ending MRR]
        ),
        0
    )""", MONEY, "Valor de cada etapa da ponte de MRR (perdas negativas).")
add("Rótulo Etapa Waterfall", F_HTML, """
VAR _v = [Valor Etapa Waterfall]
VAR _t = SELECTEDVALUE ( dEtapaWaterfall[TipoEtapa] )
VAR _s = IF ( _t IN { "inicio", "fim" }, "", IF ( _v < 0, "−", "+" ) )
VAR _a = ABS ( _v )
RETURN
    _s & """ + fmt_money("_a"), None, "Rótulo formatado da etapa.")
add("Valor Etapa Funil", F_HTML, """
SWITCH (
    SELECTEDVALUE ( dEtapaFunil[EtapaFunil] ),
    "Visitantes", [Visitantes],
    "Leads", [Leads],
    "MQL", [MQL],
    "SQL", [SQL],
    "Trials", [Trials],
    "Clientes pagos", [Clientes Convertidos]
)""", INT)
add("Rótulo Etapa Funil", F_HTML, """
VAR _v = [Valor Etapa Funil]
RETURN
    SWITCH ( TRUE (), ISBLANK ( _v ), "–", _v >= 1e6, FORMAT ( _v / 1e6, "#,0.0", "pt-BR" ) & " mi", _v >= 1e4, FORMAT ( _v / 1e3, "#,0", "pt-BR" ) & " mil", FORMAT ( _v, "#,0", "pt-BR" ) )""")
add("Rótulo MRR Plano", F_HTML, "VAR _v = [Ending MRR] RETURN " + fmt_money("_v") + ' & "  ·  " & FORMAT ( [% MRR do Total], "0%", "pt-BR" )')
add("Rótulo LTV CAC", F_HTML, 'IF ( NOT ISBLANK ( [LTV:CAC] ), FORMAT ( [LTV:CAC], "0.0", "pt-BR" ) & "x" )')
add("Rótulo CAC", F_HTML, "VAR _v = [CAC] RETURN " + fmt_money("_v"))
add("Rótulo LTV", F_HTML, "VAR _v = [LTV Estimado] RETURN " + fmt_money("_v"))
add("Rótulo Cohort", F_HTML, 'IF ( NOT ISBLANK ( [Cohort Retenção Heatmap] ), FORMAT ( [Cohort Retenção Heatmap], "0%", "pt-BR" ) )')

add("Conversão Etapa Funil", F_HTML, """
VAR _o = SELECTEDVALUE ( dEtapaFunil[OrdemFunil] )
VAR _prev = SWITCH ( _o, 2, [Visitantes], 3, [Leads], 4, [MQL], 5, [SQL], 6, [Trials] )
RETURN
    IF ( _o > 1, DIVIDE ( [Valor Etapa Funil], _prev ) )""", PCT, "Conversão em relação à etapa anterior do funil.")
add("Rótulo Conversão Funil", F_HTML, 'IF ( NOT ISBLANK ( [Conversão Etapa Funil] ), "↓ " & FORMAT ( [Conversão Etapa Funil], "0.0%", "pt-BR" ) & " da etapa anterior" )')
MEASURES = M
