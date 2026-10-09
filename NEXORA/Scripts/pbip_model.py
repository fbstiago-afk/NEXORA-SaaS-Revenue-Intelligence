# -*- coding: utf-8 -*-
"""Gera o modelo semântico TMDL do NEXORA (tabelas, relacionamentos, medidas)."""
import os, uuid, textwrap

NS = uuid.UUID("6d2f1b2a-0b55-4e1e-9a51-6e65786f7261")


def lt(*k):
    return str(uuid.uuid5(NS, "|".join(map(str, k))))


TYPES = {"int": ("int64", "Int64.Type", "0"), "dbl": ("double", "type number", "#,0.00"),
         "money": ("double", "type number", "R$ #,0.00"), "date": ("dateTime", "type date", "dd/MM/yyyy"),
         "text": ("string", "type text", None), "pct": ("double", "type number", "0.0%")}

# (tabela, csv, descrição, [ (coluna, tipo, flags) ])  flags: h=hidden, k=key, sort=Col
T = [
    ("dCalendario", "dCalendario", "Calendário diário 01/01/2024–31/10/2026 (tabela de datas).", [
        ("Data", "date", "k"), ("Ano", "int", ""), ("MesNum", "int", "h"), ("MesNome", "text", "sort=MesNum"),
        ("MesAbrev", "text", "sort=MesNum"), ("AnoMes", "int", "h"), ("MesAno", "text", "sort=AnoMes"),
        ("Trimestre", "text", ""), ("AnoTrimestre", "text", ""), ("InicioMes", "date", ""), ("IndiceMes", "int", "h"),
        ("FaseNegocio", "text", ""), ("DiaSemana", "int", "h")]),
    ("dCliente", "dCliente", "Empresas clientes (uma linha por ClienteID) com atributos de aquisição, adoção e status atual.", [
        ("ClienteID", "int", "k"), ("NomeEmpresa", "text", ""), ("SegmentoID", "int", "h"), ("PorteID", "int", "h"),
        ("CanalID", "int", "h"), ("Cidade", "text", ""), ("UF", "text", ""), ("Regiao", "text", ""),
        ("DataAquisicao", "date", ""), ("CohortMes", "date", "h"), ("CohortAno", "int", ""), ("PlanoEntradaID", "int", "h"),
        ("PlanoAtualID", "int", "h"), ("TipoCobranca", "text", ""), ("StatusAtual", "text", ""),
        ("DataUltimoCancelamento", "date", ""), ("MotivoUltimoCancelamento", "text", ""), ("FoiReativado", "text", ""),
        ("QtdeCancelamentos", "int", ""), ("PossuiIntegracao", "text", ""), ("ScoreUsoPrimeiros30Dias", "dbl", ""),
        ("AdocaoInicial", "text", ""), ("DescontoComercialPct", "pct", ""), ("UsuariosAtuais", "int", ""),
        ("MRRAtual", "money", ""), ("HealthScoreAtual", "dbl", ""), ("FaixaHealthAtual", "text", ""),
        ("PotencialUpgrade", "text", "")]),
    ("dPlano", "dPlano", "Planos comerciais.", [
        ("PlanoID", "int", "k"), ("Plano", "text", "sort=OrdemPlano"), ("OrdemPlano", "int", "h"),
        ("PrecoBaseMensal", "money", ""), ("UsuariosInclusos", "int", ""), ("PrecoUsuarioExtra", "money", ""),
        ("Posicionamento", "text", ""), ("CorPlano", "text", "h")]),
    ("dSegmento", "dSegmento", "Segmentos de mercado.", [("SegmentoID", "int", "k"), ("Segmento", "text", "")]),
    ("dPorte", "dPorte", "Porte das empresas.", [("PorteID", "int", "k"), ("Porte", "text", "sort=OrdemPorte"),
                                                ("OrdemPorte", "int", "h"), ("FaixaFuncionarios", "text", "")]),
    ("dCanalAquisicao", "dCanalAquisicao", "Canais de aquisição.", [("CanalID", "int", "k"), ("Canal", "text", ""),
                                                                    ("TipoCanal", "text", ""), ("MidiaPaga", "text", "")]),
    ("dFuncionalidade", "dFuncionalidade", "Funcionalidades do produto.", [
        ("FuncionalidadeID", "int", "k"), ("Funcionalidade", "text", ""), ("CategoriaFuncionalidade", "text", "")]),
    ("dUsuario", "dUsuario", "Usuários licenciados das contas clientes.", [
        ("UsuarioID", "int", "k"), ("ClienteID", "int", "h"), ("Perfil", "text", ""), ("DataCriacao", "date", ""),
        ("StatusUsuario", "text", "")]),
    ("dAddOn", "dAddOn", "Catálogo de add-ons.", [("AddOnID", "int", "k"), ("AddOn", "text", ""),
                                                ("TipoCobrancaAddOn", "text", ""), ("PrecoMensal", "money", "")]),
    ("dFaixaHealth", "dFaixaHealth", "Faixas do Health Score (Saudável ≥75, Atenção 55–74, Risco 35–54, Crítico <35).", [
        ("FaixaHealth", "text", "k;sort=OrdemFaixa"), ("OrdemFaixa", "int", "h"), ("LimiteInferior", "int", ""),
        ("CorFaixa", "text", "h")]),
    ("fSnapshotMRR", "fSnapshotMRR", "Grão: cliente × mês (fim do mês) com MRR > 0. Estoque — nunca somar meses.", [
        ("SnapshotID", "int", "h"), ("ClienteID", "int", "h"), ("DataMes", "date", "h"), ("PlanoID", "int", "h"),
        ("TipoCobranca", "text", "h"), ("MRRPlano", "money", "h"), ("MRRUsuariosExtras", "money", "h"),
        ("MRRAddOns", "money", "h"), ("MRR", "money", "h"), ("Usuarios", "int", "h"), ("IdadeCohort", "int", "h"),
        ("ReceitaRecorrenteReconhecida", "money", "h")]),
    ("fMovimentoMRR", "fMovimentoMRR", "Grão: cliente × mês × tipo de movimento. ValorMRR já com sinal (perdas negativas).", [
        ("MovimentoID", "int", "h"), ("ClienteID", "int", "h"), ("DataMes", "date", "h"), ("TipoMovimento", "text", "h"),
        ("Subtipo", "text", ""), ("PlanoID", "int", "h"), ("PlanoAnteriorID", "int", "h"), ("ValorMRR", "money", "h"),
        ("MotivoChurn", "text", ""), ("SinalMovimento", "int", "h")]),
    ("fAssinaturas", "fAssinaturas", "Contratos (booking). Uma linha por período contratual de plano/ciclo.", [
        ("AssinaturaID", "int", "h"), ("ClienteID", "int", "h"), ("PlanoID", "int", "h"), ("TipoCobranca", "text", "h"),
        ("DataInicio", "date", "h"), ("DataFim", "date", "h"), ("StatusAssinatura", "text", ""), ("TipoAbertura", "text", ""),
        ("MRRInicial", "money", "h"), ("PrazoMeses", "int", "h"), ("ValorContrato", "money", "h"),
        ("UsuariosContratados", "int", "h"), ("MotivoEncerramento", "text", "")]),
    ("fAddOns", "fAddOns", "Contratação de add-ons recorrentes.", [
        ("AddOnContratoID", "int", "h"), ("ClienteID", "int", "h"), ("AddOnID", "int", "h"), ("DataInicio", "date", "h"),
        ("DataFim", "date", "h"), ("StatusAddOn", "text", ""), ("Quantidade", "int", "h"), ("PrecoMensalLista", "money", "h")]),
    ("fUsoProduto", "fUsoProduto", "Grão: cliente × mês ativo. Uso, adoção e Health Score.", [
        ("UsoID", "int", "h"), ("ClienteID", "int", "h"), ("DataMes", "date", "h"), ("UsuariosLicenciados", "int", "h"),
        ("UsuariosAtivos", "int", "h"), ("DAU", "dbl", "h"), ("WAU", "dbl", "h"), ("MAU", "int", "h"), ("Logins", "int", "h"),
        ("Sessoes", "int", "h"), ("Automacoes", "int", "h"), ("Oportunidades", "int", "h"), ("Relatorios", "int", "h"),
        ("IntegracoesAtivas", "int", "h"), ("FuncionalidadesUsadas", "int", "h"), ("TicketsMes", "int", "h"),
        ("FaturasEmAtraso", "int", "h"), ("VariacaoUsoPct", "pct", "h"), ("HealthScore", "dbl", "h"),
        ("FaixaHealth", "text", "h"), ("PotencialUpgrade", "text", ""), ("MesesDeVida", "int", "h")]),
    ("fEventosProduto", "fEventosProduto", "Grão: cliente × mês × funcionalidade.", [
        ("EventoID", "int", "h"), ("ClienteID", "int", "h"), ("DataMes", "date", "h"), ("FuncionalidadeID", "int", "h"),
        ("Eventos", "int", "h"), ("UsuariosUnicos", "int", "h")]),
    ("fMarketing", "fMarketing", "Grão: canal × mês. Investimento e tráfego.", [
        ("MarketingID", "int", "h"), ("CanalID", "int", "h"), ("DataMes", "date", "h"), ("Investimento", "money", "h"),
        ("Impressoes", "int", "h"), ("Cliques", "int", "h"), ("Visitantes", "int", "h"), ("Leads", "int", "h"),
        ("NovosClientes", "int", "h")]),
    ("fLeads", "fLeads", "Grão: lead. Estágios Lead → MQL → SQL → Trial → Cliente.", [
        ("LeadID", "int", "h"), ("DataLead", "date", "h"), ("CanalID", "int", "h"), ("SegmentoID", "int", "h"),
        ("PorteID", "int", "h"), ("MQL", "text", "h"), ("SQL", "text", "h"), ("Trial", "text", "h"), ("Convertido", "text", "h")]),
    ("fTrials", "fTrials", "Grão: trial.", [
        ("TrialID", "int", "h"), ("CanalID", "int", "h"), ("SegmentoID", "int", "h"), ("PorteID", "int", "h"),
        ("PlanoInteresseID", "int", "h"), ("DataInicioTrial", "date", "h"), ("DuracaoDias", "int", "h"),
        ("Convertido", "text", "h"), ("DataConversao", "date", "h"), ("LoginsTrial", "int", "h")]),
    ("fSuporte", "fSuporte", "Grão: ticket de suporte.", [
        ("TicketID", "int", "h"), ("ClienteID", "int", "h"), ("DataAbertura", "date", "h"), ("Categoria", "text", ""),
        ("Prioridade", "text", ""), ("SLAHoras", "int", "h"), ("TempoPrimeiraRespostaH", "dbl", "h"),
        ("TempoResolucaoH", "dbl", "h"), ("DentroSLA", "text", ""), ("Satisfacao", "int", "h")]),
    ("fFinanceiro", "fFinanceiro", "Grão: fatura (billing). Não confundir com MRR.", [
        ("FaturaID", "int", "h"), ("ClienteID", "int", "h"), ("DataEmissao", "date", "h"), ("DataVencimento", "date", "h"),
        ("DataPagamento", "date", "h"), ("TipoFatura", "text", ""), ("TipoCobranca", "text", ""), ("ValorBruto", "money", "h"),
        ("Desconto", "money", "h"), ("ValorLiquido", "money", "h"), ("ValorPago", "money", "h"), ("ValorEstornado", "money", "h"),
        ("ValorRecebido", "money", "h"), ("StatusPagamento", "text", ""), ("DiasAtraso", "int", "h")]),
    ("fAquisicao", "fAquisicao", "Grão: primeira aquisição do cliente, com custo de aquisição alocado (Σ = investimento).", [
        ("ClienteID", "int", "h"), ("DataAquisicao", "date", "h"), ("DataMes", "date", "h"), ("CanalID", "int", "h"),
        ("PlanoEntradaID", "int", "h"), ("LeadID", "int", "h"), ("TrialID", "int", "h"), ("CustoAquisicao", "money", "h"),
        ("MRRInicial", "money", "h")]),
    ("fCohortMensal", "fCohortMensal", "Agregado: cohort × idade × canal × plano de entrada × segmento × porte.", [
        ("CohortRowID", "int", "h"), ("CohortMes", "date", "h"), ("IdadeCohort", "int", ""), ("CanalID", "int", "h"),
        ("PlanoEntradaID", "int", "h"), ("SegmentoID", "int", "h"), ("PorteID", "int", "h"), ("ClientesIniciais", "int", "h"),
        ("ClientesAtivos", "int", "h"), ("MRRInicial", "money", "h"), ("MRRAtivo", "money", "h")]),
]

REL = [  # from (many) -> to (one)
    ("fSnapshotMRR.DataMes", "dCalendario.Data"), ("fSnapshotMRR.ClienteID", "dCliente.ClienteID"),
    ("fSnapshotMRR.PlanoID", "dPlano.PlanoID"),
    ("fMovimentoMRR.DataMes", "dCalendario.Data"), ("fMovimentoMRR.ClienteID", "dCliente.ClienteID"),
    ("fMovimentoMRR.PlanoID", "dPlano.PlanoID"), ("fMovimentoMRR.TipoMovimento", "dTipoMovimento.TipoMovimento"),
    ("fAssinaturas.DataInicio", "dCalendario.Data"), ("fAssinaturas.ClienteID", "dCliente.ClienteID"),
    ("fAssinaturas.PlanoID", "dPlano.PlanoID"),
    ("fAddOns.DataInicio", "dCalendario.Data"), ("fAddOns.ClienteID", "dCliente.ClienteID"), ("fAddOns.AddOnID", "dAddOn.AddOnID"),
    ("fUsoProduto.DataMes", "dCalendario.Data"), ("fUsoProduto.ClienteID", "dCliente.ClienteID"),
    ("fUsoProduto.FaixaHealth", "dFaixaHealth.FaixaHealth"),
    ("fEventosProduto.DataMes", "dCalendario.Data"), ("fEventosProduto.ClienteID", "dCliente.ClienteID"),
    ("fEventosProduto.FuncionalidadeID", "dFuncionalidade.FuncionalidadeID"),
    ("fMarketing.DataMes", "dCalendario.Data"), ("fMarketing.CanalID", "dCanalAquisicao.CanalID"),
    ("fLeads.DataLead", "dCalendario.Data"), ("fLeads.CanalID", "dCanalAquisicao.CanalID"),
    ("fLeads.SegmentoID", "dSegmento.SegmentoID"), ("fLeads.PorteID", "dPorte.PorteID"),
    ("fTrials.DataInicioTrial", "dCalendario.Data"), ("fTrials.CanalID", "dCanalAquisicao.CanalID"),
    ("fTrials.SegmentoID", "dSegmento.SegmentoID"), ("fTrials.PorteID", "dPorte.PorteID"),
    ("fTrials.PlanoInteresseID", "dPlano.PlanoID"),
    ("fSuporte.DataAbertura", "dCalendario.Data"), ("fSuporte.ClienteID", "dCliente.ClienteID"),
    ("fFinanceiro.DataEmissao", "dCalendario.Data"), ("fFinanceiro.ClienteID", "dCliente.ClienteID"),
    ("fAquisicao.DataAquisicao", "dCalendario.Data"), ("fAquisicao.ClienteID", "dCliente.ClienteID"),
    ("fAquisicao.PlanoEntradaID", "dPlano.PlanoID"),
    ("fCohortMensal.CanalID", "dCanalAquisicao.CanalID"), ("fCohortMensal.PlanoEntradaID", "dPlano.PlanoID"),
    ("fCohortMensal.SegmentoID", "dSegmento.SegmentoID"), ("fCohortMensal.PorteID", "dPorte.PorteID"),
    ("fCohortMensal.CohortMes", "dCohort.CohortMes"),
    ("dCliente.CanalID", "dCanalAquisicao.CanalID"), ("dCliente.SegmentoID", "dSegmento.SegmentoID"),
    ("dCliente.PorteID", "dPorte.PorteID"), ("dCliente.CohortMes", "dCohort.CohortMes"),
    ("dUsuario.ClienteID", "dCliente.ClienteID"),
]


def tm_column(tbl, name, typ, flags, calc=False):
    dt, _, fmt = TYPES[typ]
    L = [f"\tcolumn {q(name)}", f"\t\tdataType: {dt}"]
    fl = flags.split(";") if flags else []
    if "k" in fl:
        L.append("\t\tisKey")
    if "h" in fl:
        L.append("\t\tisHidden")
    if fmt:
        L.append(f"\t\tformatString: {fmt}")
    L.append(f"\t\tlineageTag: {lt(tbl, name)}")
    L.append("\t\tsummarizeBy: none")
    if calc:
        L.append("\t\tisNameInferred")
        L.append(f"\t\tsourceColumn: [{name}]")
    else:
        L.append(f"\t\tsourceColumn: {name}")
    for f in fl:
        if f.startswith("sort="):
            L.append(f"\t\tsortByColumn: {f[5:]}")
    L.append("")
    L.append(f"\t\tannotation SummarizationSetBy = Automatic")
    L.append("")
    return "\n".join(L)


def q(n):
    return n if n.replace("_", "").isalnum() and not n[0].isdigit() else "'" + n.replace("'", "''") + "'"


def m_partition(tbl, csv, cols, extra_steps=None):
    sel = ", ".join(f'"{c}"' for c, _, _ in cols)
    typ = ", ".join(f'{{"{c}", {TYPES[t][1]}}}' for c, t, _ in cols)
    steps = [f'Fonte = Csv.Document(File.Contents(PastaDados & "{csv}.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv])',
             'Cabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true])',
             f'Colunas = Table.SelectColumns(Cabecalho, {{{sel}}})',
             f'Tipos = Table.TransformColumnTypes(Colunas, {{{typ}}}, "en-US")']
    last = "Tipos"
    for nm, expr in (extra_steps or []):
        steps.append(f"{nm} = {expr.replace('#PREV', last)}")
        last = nm
    body = ",\n".join("\t\t\t\t\t" + s for s in steps)
    return (f"\tpartition {q(tbl)} = m\n\t\tmode: import\n\t\tsource =\n\t\t\t\tlet\n{body}\n\t\t\t\tin\n\t\t\t\t\t{last}\n")


def table_tmdl(tbl, csv, desc, cols):
    out = [f"/// {desc}", f"table {q(tbl)}", f"\tlineageTag: {lt(tbl)}"]
    if tbl == "dCalendario":
        out.append("\tdataCategory: Time")
    out.append("")
    for c, t, f in cols:
        out.append(tm_column(tbl, c, t, f))
    out.append(m_partition(tbl, csv, cols))
    out.append("\tannotation PBI_ResultType = Table\n")
    return "\n".join(out)


# ------------------------------------------------------------------ tabelas auxiliares
CALC_TABLES = {
    "dTipoMovimento": ("Tipos de movimento de MRR (ordem, rótulo PT-BR e cor semântica).",
                       [("TipoMovimento", "text", "k"), ("Movimento", "text", "sort=OrdemMovimento"), ("OrdemMovimento", "int", "h"),
                        ("CorMovimento", "text", "h"), ("GrupoMovimento", "text", "")],
                       'DATATABLE ( "TipoMovimento", STRING, "Movimento", STRING, "OrdemMovimento", INTEGER, "CorMovimento", STRING, "GrupoMovimento", STRING, {'
                       ' { "New", "Novo", 1, "#00B8F5", "Ganho" }, { "Expansion", "Expansão", 2, "#00D7C0", "Ganho" },'
                       ' { "Reactivation", "Reativação", 3, "#1678FF", "Ganho" }, { "Contraction", "Contração", 4, "#FFA3B3", "Perda" },'
                       ' { "Churn", "Churn", 5, "#FF607A", "Perda" }, { "Plan Migration In", "Migração (entrada)", 6, "#6E86B3", "Migração" },'
                       ' { "Plan Migration Out", "Migração (saída)", 7, "#6E86B3", "Migração" } } )'),
    "dEtapaWaterfall": ("Etapas da ponte de MRR (tabela desconectada para o Waterfall Deneb).",
                        [("Etapa", "text", "sort=OrdemEtapa"), ("OrdemEtapa", "int", ""), ("TipoEtapa", "text", "")],
                        'DATATABLE ( "Etapa", STRING, "OrdemEtapa", INTEGER, "TipoEtapa", STRING, {'
                        ' { "MRR inicial", 1, "inicio" }, { "Novo", 2, "ganho" }, { "Expansão", 3, "ganho" }, { "Reativação", 4, "ganho" },'
                        ' { "Migração planos", 5, "migr" }, { "Contração", 6, "perda" }, { "Churn", 7, "perda" }, { "MRR final", 8, "fim" } } )'),
    "dEtapaFunil": ("Etapas do funil de aquisição (tabela desconectada).",
                    [("EtapaFunil", "text", "sort=OrdemFunil"), ("OrdemFunil", "int", "")],
                    'DATATABLE ( "EtapaFunil", STRING, "OrdemFunil", INTEGER, { { "Visitantes", 1 }, { "Leads", 2 }, { "MQL", 3 },'
                    ' { "SQL", 4 }, { "Trials", 5 }, { "Clientes pagos", 6 } } )'),
}


def calc_table_tmdl(tbl, desc, cols, dax):
    out = [f"/// {desc}", f"table {q(tbl)}", f"\tlineageTag: {lt(tbl)}", ""]
    for c, t, f in cols:
        out.append(tm_column(tbl, c, t, f, calc=True))
    out.append(f"\tpartition {q(tbl)} = calculated\n\t\tmode: import\n\t\tsource = {dax}\n")
    out.append("\tannotation PBI_Id = " + lt(tbl, "id").replace("-", "") + "\n")
    return "\n".join(out)


def dcohort_tmdl():
    cols = [("CohortMes", "date", "k"), ("Cohort", "text", "sort=CohortIdx"), ("CohortIdx", "int", "h"), ("CohortAno", "int", "")]
    out = ["/// Dimensão de cohort (mês de aquisição). Conecta dCliente e fCohortMensal.", "table dCohort",
           f"\tlineageTag: {lt('dCohort')}", ""]
    for c, t, f in cols:
        out.append(tm_column("dCohort", c, t, f))
    steps = ('\tpartition dCohort = m\n\t\tmode: import\n\t\tsource =\n\t\t\t\tlet\n'
             '\t\t\t\t\tFonte = Csv.Document(File.Contents(PastaDados & "dCliente.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),\n'
             '\t\t\t\t\tCabecalho = Table.PromoteHeaders(Fonte, [PromoteAllScalars = true]),\n'
             '\t\t\t\t\tColunas = Table.SelectColumns(Cabecalho, {"CohortMes"}),\n'
             '\t\t\t\t\tTipos = Table.TransformColumnTypes(Colunas, {{"CohortMes", type date}}, "en-US"),\n'
             '\t\t\t\t\tDistintos = Table.Distinct(Tipos),\n'
             '\t\t\t\t\tRotulo = Table.AddColumn(Distintos, "Cohort", each Text.Lower(Date.ToText([CohortMes], "MMM", "pt-BR")) & "/" & Date.ToText([CohortMes], "yy"), type text),\n'
             '\t\t\t\t\tIdx = Table.AddColumn(Rotulo, "CohortIdx", each Date.Year([CohortMes]) * 100 + Date.Month([CohortMes]), Int64.Type),\n'
             '\t\t\t\t\tAno = Table.AddColumn(Idx, "CohortAno", each Date.Year([CohortMes]), Int64.Type),\n'
             '\t\t\t\t\tOrdenado = Table.Sort(Ano, {{"CohortMes", Order.Ascending}})\n'
             '\t\t\t\tin\n\t\t\t\t\tOrdenado\n')
    out.append(steps)
    out.append("\tannotation PBI_ResultType = Table\n")
    return "\n".join(out)


def relationships_tmdl():
    L = []
    for a, b in REL:
        L.append(f"relationship {lt('rel', a, b)}\n\tfromColumn: {a}\n\ttoColumn: {b}\n")
    return "\n".join(L)


# ------------------------------------------------------------------ medidas
from pbip_measures import MEASURES  # noqa: E402


def measures_tmdl():
    out = ["/// Tabela exclusiva de medidas do NEXORA SaaS Revenue Intelligence.", "table _Medidas",
           f"\tlineageTag: {lt('_Medidas')}", ""]
    for m in MEASURES:
        name, folder, fmt, dax = m["name"], m["folder"], m.get("fmt"), m["dax"].strip("\n")
        if m.get("desc"):
            out.append(f"\t/// {m['desc']}")
        lines = textwrap.dedent(dax).strip().split("\n")
        if len(lines) == 1:
            out.append(f"\tmeasure {q(name)} = {lines[0]}")
        else:
            out.append(f"\tmeasure {q(name)} =")
            for ln in lines:
                out.append("\t\t\t" + ln)
        if fmt:
            out.append(f"\t\tformatString: {fmt}")
        if m.get("hidden"):
            out.append("\t\tisHidden")
        out.append(f"\t\tdisplayFolder: {folder}")
        out.append(f"\t\tlineageTag: {lt('m', name)}")
        if m.get("cat"):
            out.append(f"\t\tdataCategory: {m['cat']}")
        out.append("")
    out.append("\tcolumn Medida\n\t\tdataType: string\n\t\tisHidden\n\t\tlineageTag: " + lt("_Medidas", "c") +
               "\n\t\tsummarizeBy: none\n\t\tisNameInferred\n\t\tsourceColumn: [Medida]\n\n\t\tannotation SummarizationSetBy = Automatic\n")
    out.append('\tpartition _Medidas = calculated\n\t\tmode: import\n\t\tsource = ROW ( "Medida", "NEXORA" )\n')
    out.append("\tannotation PBI_Id = " + lt("_Medidas", "id").replace("-", "") + "\n")
    return "\n".join(out)


def write_model(root, pasta_dados):
    d = os.path.join(root, "definition")
    os.makedirs(os.path.join(d, "tables"), exist_ok=True)
    names = ["_Medidas"]
    for tbl, csv, desc, cols in T:
        open(os.path.join(d, "tables", f"{tbl}.tmdl"), "w", encoding="utf-8").write(table_tmdl(tbl, csv, desc, cols))
        names.append(tbl)
    for tbl, (desc, cols, dax) in CALC_TABLES.items():
        open(os.path.join(d, "tables", f"{tbl}.tmdl"), "w", encoding="utf-8").write(calc_table_tmdl(tbl, desc, cols, dax))
        names.append(tbl)
    open(os.path.join(d, "tables", "dCohort.tmdl"), "w", encoding="utf-8").write(dcohort_tmdl())
    names.append("dCohort")
    open(os.path.join(d, "tables", "_Medidas.tmdl"), "w", encoding="utf-8").write(measures_tmdl())
    open(os.path.join(d, "relationships.tmdl"), "w", encoding="utf-8").write(relationships_tmdl())
    open(os.path.join(d, "expressions.tmdl"), "w", encoding="utf-8").write(
        "/// Pasta com os CSVs da base NEXORA. Altere aqui se mover o projeto (termine com \\).\n"
        f'expression PastaDados = "{pasta_dados}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]\n'
        f"\tlineageTag: {lt('PastaDados')}\n\n\tannotation PBI_ResultType = Text\n")
    model = ["model Model", "\tculture: pt-BR", "\tdefaultPowerBIDataSourceVersion: powerBI_V3", "\tdiscourageImplicitMeasures",
             "\tsourceQueryCulture: pt-BR", "\tvalueFilterBehavior: independent", "\tdataAccessOptions", "\t\tlegacyRedirects",
             "\t\treturnErrorValuesAsNull", "", "annotation __PBI_TimeIntelligenceEnabled = 0", "",
             'annotation PBI_ProTooling = ["DevMode"]', ""]
    for n in names:
        model.append(f"ref table {q(n)}")
    model += ["", "ref cultureInfo pt-BR", ""]
    open(os.path.join(d, "model.tmdl"), "w", encoding="utf-8").write("\n".join(model))
    return names
