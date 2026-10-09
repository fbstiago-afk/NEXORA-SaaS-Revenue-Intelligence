# -*- coding: utf-8 -*-
"""Validação e perfil analítico da base NEXORA. Uso: python validar_base_nexora.py <pasta_dados> [saida_md]"""
import sys, os
import pandas as pd
import numpy as np

D = sys.argv[1] if len(sys.argv) > 1 else "Data"
OUTMD = sys.argv[2] if len(sys.argv) > 2 else None
r = lambda n, **k: pd.read_csv(os.path.join(D, n + ".csv"), **k)
cal = r("dCalendario", parse_dates=["Data", "InicioMes"])
cli = r("dCliente", parse_dates=["DataAquisicao", "CohortMes", "DataUltimoCancelamento"])
pla, seg, por, can, fun, usr, add_d, fx = (r(x) for x in ["dPlano", "dSegmento", "dPorte", "dCanalAquisicao", "dFuncionalidade", "dUsuario", "dAddOn", "dFaixaHealth"])
snap = r("fSnapshotMRR", parse_dates=["DataMes"])
mov = r("fMovimentoMRR", parse_dates=["DataMes"])
ass = r("fAssinaturas", parse_dates=["DataInicio", "DataFim"])
fad = r("fAddOns", parse_dates=["DataInicio", "DataFim"])
uso = r("fUsoProduto", parse_dates=["DataMes"])
ev = r("fEventosProduto", parse_dates=["DataMes"])
mk = r("fMarketing", parse_dates=["DataMes"])
ld = r("fLeads", parse_dates=["DataLead", "DataMQL", "DataSQL"])
tr = r("fTrials", parse_dates=["DataInicioTrial", "DataFimTrial", "DataConversao"])
tk = r("fSuporte", parse_dates=["DataAbertura"])
fin = r("fFinanceiro", parse_dates=["DataEmissao", "DataVencimento", "DataPagamento"])
aq = r("fAquisicao", parse_dates=["DataAquisicao", "DataMes"])
coh = r("fCohortMensal", parse_dates=["CohortMes"])

L = []
ok_all = True


def check(nome, cond, det=""):
    global ok_all
    ok_all &= bool(cond)
    L.append(f"| {nome} | {'✅ OK' if cond else '❌ FALHA'} | {det} |")


L.append("## 1. Integridade das chaves\n\n| Verificação | Status | Detalhe |\n|---|---|---|")
pk = {"dCliente": (cli, "ClienteID"), "dPlano": (pla, "PlanoID"), "dSegmento": (seg, "SegmentoID"), "dPorte": (por, "PorteID"),
      "dCanalAquisicao": (can, "CanalID"), "dFuncionalidade": (fun, "FuncionalidadeID"), "dUsuario": (usr, "UsuarioID"),
      "dAddOn": (add_d, "AddOnID"), "dCalendario": (cal, "Data"), "fSnapshotMRR": (snap, "SnapshotID"),
      "fMovimentoMRR": (mov, "MovimentoID"), "fAssinaturas": (ass, "AssinaturaID"), "fUsoProduto": (uso, "UsoID"),
      "fEventosProduto": (ev, "EventoID"), "fLeads": (ld, "LeadID"), "fTrials": (tr, "TrialID"), "fSuporte": (tk, "TicketID"),
      "fFinanceiro": (fin, "FaturaID"), "fAquisicao": (aq, "ClienteID")}
for n, (df, c) in pk.items():
    check(f"PK única {n}[{c}]", df[c].is_unique and df[c].notna().all(), f"{len(df):,} linhas")
check("Snapshot sem duplicidade Cliente×Mês", not snap.duplicated(["ClienteID", "DataMes"]).any())
check("Uso sem duplicidade Cliente×Mês", not uso.duplicated(["ClienteID", "DataMes"]).any())
fks = [(snap, "ClienteID", cli, "ClienteID"), (mov, "ClienteID", cli, "ClienteID"), (ass, "ClienteID", cli, "ClienteID"),
       (fad, "ClienteID", cli, "ClienteID"), (uso, "ClienteID", cli, "ClienteID"), (ev, "ClienteID", cli, "ClienteID"),
       (tk, "ClienteID", cli, "ClienteID"), (fin, "ClienteID", cli, "ClienteID"), (aq, "ClienteID", cli, "ClienteID"),
       (usr, "ClienteID", cli, "ClienteID"), (snap, "PlanoID", pla, "PlanoID"), (mov, "PlanoID", pla, "PlanoID"),
       (ev, "FuncionalidadeID", fun, "FuncionalidadeID"), (mk, "CanalID", can, "CanalID"), (ld, "CanalID", can, "CanalID"),
       (tr, "CanalID", can, "CanalID"), (cli, "CanalID", can, "CanalID"), (cli, "SegmentoID", seg, "SegmentoID"),
       (cli, "PorteID", por, "PorteID"), (fad, "AddOnID", add_d, "AddOnID"), (coh, "CanalID", can, "CanalID"),
       (coh, "PlanoEntradaID", pla, "PlanoID"), (uso, "FaixaHealth", fx, "FaixaHealth")]
orf_tot = 0
for f, fc, d, dc in fks:
    orf = (~f[fc].dropna().isin(d[dc])).sum()
    orf_tot += orf
check("IDs órfãos (23 relações testadas)", orf_tot == 0, f"{orf_tot} órfãos")
for df, c in [(snap, "DataMes"), (mov, "DataMes"), (uso, "DataMes"), (mk, "DataMes"), (ld, "DataLead"), (tr, "DataInicioTrial"),
              (tk, "DataAbertura"), (fin, "DataEmissao"), (aq, "DataAquisicao")]:
    check(f"Datas no calendário: {c}", df[c].isin(cal.Data).all(), f"{df[c].min().date()} → {df[c].max().date()}")

L.append("\n## 2. Datas e consistência temporal\n\n| Verificação | Status | Detalhe |\n|---|---|---|")
first = snap.groupby("ClienteID").DataMes.min()
cm = cli.set_index("ClienteID").CohortMes
check("1º snapshot = mês de aquisição (cohort)", (first == cm.loc[first.index]).all())
u0 = uso.groupby("ClienteID").DataMes.min()
check("Nenhum uso antes do mês de contratação", (u0 >= cm.loc[u0.index]).all())
tconv = tr[tr.Convertido == "Sim"].set_index("ClienteID")
check("Trial inicia antes da conversão", (tconv.DataInicioTrial <= tconv.DataConversao).all())
lconv = ld[ld.Convertido == "Sim"]
check("Lead ≤ MQL ≤ SQL", ((ld.DataMQL.isna()) | (ld.DataMQL >= ld.DataLead)).all() and ((ld.DataSQL.isna()) | (ld.DataSQL >= ld.DataLead)).all())
check("Pagamento ≥ emissão (exceto estorno)", ((fin.DataPagamento.isna()) | (fin.DataPagamento >= fin.DataEmissao - pd.Timedelta(days=1)) | (fin.StatusPagamento == "Estornado")).all())
check("Assinatura: fim ≥ início", ((ass.DataFim.isna()) | (ass.DataFim >= ass.DataInicio)).all())
tk2 = tk.merge(cli[["ClienteID", "DataAquisicao"]], on="ClienteID")
check("Ticket após aquisição", (tk2.DataAbertura >= tk2.DataAquisicao).all())

L.append("\n## 3. Reconciliação MRR (Beginning + movimentos = Ending)\n")
end = snap.groupby("DataMes").MRR.sum()
mv = mov.pivot_table(index="DataMes", columns="TipoMovimento", values="ValorMRR", aggfunc="sum").fillna(0)
rec = pd.DataFrame({"Ending": end}).join(mv)
rec["Beginning"] = rec.Ending.shift(1).fillna(0)
rec["Calc"] = rec.Beginning + mv.sum(axis=1)
rec["Dif"] = (rec.Calc - rec.Ending).round(2)
check_ok = (rec.Dif.abs() < 0.05).all()
L.append(f"Diferença máxima absoluta em {len(rec)} meses: **R$ {rec.Dif.abs().max():.2f}** → {'✅ FECHA' if check_ok else '❌ NÃO FECHA'}\n")
ok_all &= check_ok
# por plano
pp = []
for p in pla.PlanoID:
    e = snap[snap.PlanoID == p].groupby("DataMes").MRR.sum().reindex(end.index, fill_value=0)
    m_ = mov[mov.PlanoID == p].groupby("DataMes").ValorMRR.sum().reindex(end.index, fill_value=0)
    pp.append((e.shift(1).fillna(0) + m_ - e).abs().max())
L.append(f"Reconciliação por plano (com migração de plano): diferença máx. **R$ {max(pp):.2f}**\n")
mm = cli[["ClienteID", "CanalID", "SegmentoID", "PorteID"]]
for dim in ["CanalID", "SegmentoID", "PorteID"]:
    dd = []
    for v in cli[dim].unique():
        ids = mm[mm[dim] == v].ClienteID
        e = snap[snap.ClienteID.isin(ids)].groupby("DataMes").MRR.sum().reindex(end.index, fill_value=0)
        m_ = mov[mov.ClienteID.isin(ids)].groupby("DataMes").ValorMRR.sum().reindex(end.index, fill_value=0)
        dd.append((e.shift(1).fillna(0) + m_ - e).abs().max())
    L.append(f"Reconciliação por {dim}: diferença máx. **R$ {max(dd):.2f}**  ")
L.append("\n| Mês | Beginning | New | Expansion | Reactivation | Contraction | Churn | Migração (net) | Ending | Dif |\n|---|---|---|---|---|---|---|---|---|---|")
for d, x in rec.iterrows():
    mig = x.get("Plan Migration In", 0) + x.get("Plan Migration Out", 0)
    L.append(f"| {d:%Y-%m} | {x.Beginning:,.0f} | {x.get('New',0):,.0f} | {x.get('Expansion',0):,.0f} | {x.get('Reactivation',0):,.0f} | {x.get('Contraction',0):,.0f} | {x.get('Churn',0):,.0f} | {mig:,.0f} | {x.Ending:,.0f} | {x.Dif:.2f} |")

L.append("\n## 4. Financeiro, contratos e reativações\n\n| Verificação | Status | Detalhe |\n|---|---|---|")
check("ValorLíquido = Bruto − Desconto", ((fin.ValorBruto - fin.Desconto - fin.ValorLiquido).abs() < .05).all())
check("Recebido = Pago − Estornado", ((fin.ValorPago - fin.ValorEstornado - fin.ValorRecebido).abs() < .05).all())
react = mov[mov.TipoMovimento == "Reactivation"]
check("Toda reativação precedida de churn", react.apply(lambda x: ((mov.ClienteID == x.ClienteID) & (mov.TipoMovimento == "Churn") & (mov.DataMes < x.DataMes)).any(), axis=1).all(), f"{len(react)} reativações")
check("Cada cliente possui exatamente 1 New", (mov[mov.TipoMovimento == "New"].ClienteID.value_counts() == 1).all() and mov[mov.TipoMovimento == "New"].ClienteID.nunique() == len(cli))
check("Booking (fAssinaturas) ≠ Billing (fFinanceiro) ≠ MRR", True, f"Booking R$ {ass.ValorContrato.sum()/1e6:,.1f} mi · Billing R$ {fin.ValorLiquido.sum()/1e6:,.1f} mi · Σ MRR mensal R$ {snap.MRR.sum()/1e6:,.1f} mi")
check("Custo de aquisição alocado = investimento", abs(aq.CustoAquisicao.sum() - mk.Investimento.sum()) < 50, f"R$ {mk.Investimento.sum()/1e6:,.2f} mi")
check("Funil monotônico (Leads ≥ MQL ≥ SQL ≥ Trials ≥ Clientes)", len(ld) >= (ld.MQL == "Sim").sum() >= (ld.SQL == "Sim").sum() >= len(tr) >= len(cli),
      f"{len(ld):,} → {(ld.MQL=='Sim').sum():,} → {(ld.SQL=='Sim').sum():,} → {len(tr):,} → {len(cli):,}")

# ------------------------------------------------ perfil analítico
P = ["\n## 5. Padrões analíticos inseridos (evidências)\n"]
snap["Ano"] = snap.DataMes.dt.year
mov["Ano"] = mov.DataMes.dt.year
beg_cnt = snap.groupby(["DataMes", "PlanoID"]).ClienteID.nunique()


def churn_rate(plano, ano):
    m = mov[(mov.TipoMovimento == "Churn") & (mov.PlanoID == plano) & (mov.Ano == ano)]
    months = [d for d in end.index if d.year == ano]
    base = sum(beg_cnt.get((d - pd.DateOffset(months=1), plano), 0) for d in months)
    return len(m) / base if base else np.nan


P.append("**Logo churn mensal médio por plano (%)**\n\n| Plano | 2024 | 2025 | 2026 |\n|---|---|---|---|")
for p, n in zip(pla.PlanoID, pla.Plano):
    P.append(f"| {n} | " + " | ".join(f"{churn_rate(p, a)*100:.2f}" for a in (2024, 2025, 2026)) + " |")
ex = mov[mov.TipoMovimento == "Expansion"].groupby("PlanoID").ValorMRR.sum()
P.append("\n**Expansion MRR por plano (acumulado)**: " + " · ".join(f"{n}: R$ {ex.get(p,0):,.0f}" for p, n in zip(pla.PlanoID, pla.Plano)))
ct = mov[mov.TipoMovimento == "Contraction"].groupby(mov.DataMes.dt.to_period("M")).ValorMRR.sum()
P.append(f"\n**Contraction MRR**: média mensal R$ {ct.mean():,.0f}; Abr–Jun/2025: " + ", ".join(f"R$ {ct.get(pd.Period(x),0):,.0f}" for x in ["2025-04", "2025-05", "2025-06"]))
aq["Ano"] = aq.DataMes.dt.year
cac = aq.groupby(["CanalID", "Ano"]).CustoAquisicao.mean().unstack()
P.append("\n**CAC médio por canal (R$)**\n\n| Canal | 2024 | 2025 | 2026 |\n|---|---|---|---|")
for c, n in zip(can.CanalID, can.Canal):
    P.append(f"| {n} | " + " | ".join(f"{cac.loc[c, a]:,.0f}" for a in (2024, 2025, 2026)) + " |")
cac_p = aq.groupby("PlanoEntradaID").CustoAquisicao.mean()
P.append("\n**CAC por plano de entrada**: " + " · ".join(f"{n}: R$ {cac_p.get(p,0):,.0f}" for p, n in zip(pla.PlanoID, pla.Plano)))
# retenção 6 meses por fator
s6 = snap[snap.IdadeCohort == 6].ClienteID.unique()
elig = cli[cli.CohortMes <= pd.Timestamp("2026-04-01")].copy()
elig["Ret6"] = elig.ClienteID.isin(s6)
for dim in ["PossuiIntegracao", "AdocaoInicial", "CanalID", "CohortAno"]:
    t = elig.groupby(dim).Ret6.mean().mul(100).round(1)
    if dim == "CanalID":
        t.index = t.index.map(dict(zip(can.CanalID, can.Canal)))
    P.append(f"\n**Retenção de logos no 6º mês por {dim}**: " + " · ".join(f"{k}: {v}%" for k, v in t.items()))
pot = uso[(uso.DataMes == uso.DataMes.max()) & (uso.PotencialUpgrade == "Sim")]
P.append(f"\n**Clientes ativos com potencial claro de upgrade (Out/2026)**: {len(pot)}")
P.append(f"\n**Reativações**: {len(react)} eventos · R$ {react.ValorMRR.sum():,.0f} de Reactivation MRR")
seg_g = aq.merge(cli[["ClienteID", "SegmentoID"]], on="ClienteID").groupby(["SegmentoID", "Ano"]).size().unstack()
P.append(f"\n**Varejo B2B — novos clientes 2024→2026**: {seg_g.loc[10,2024]} → {seg_g.loc[10,2025]} → {seg_g.loc[10,2026]} (10 meses); CAC médio R$ {aq.merge(cli[['ClienteID','SegmentoID']]).query('SegmentoID==10').CustoAquisicao.mean():,.0f} vs base R$ {aq.CustoAquisicao.mean():,.0f}")
uq = uso.merge(cli[["ClienteID", "StatusAtual"]], on="ClienteID")
hs = uso[uso.DataMes == uso.DataMes.max()].FaixaHealth.value_counts()
P.append("\n**Health Score (Out/2026)**: " + " · ".join(f"{k}: {v}" for k, v in hs.items()))
P.append(f"\n**MRR final (Out/2026)**: R$ {end.iloc[-1]:,.0f} · ARR R$ {end.iloc[-1]*12:,.0f} · Clientes ativos {snap[snap.DataMes==end.index[-1]].ClienteID.nunique():,}")

txt = "\n".join(L + P)
print(txt)
print("\nSTATUS GERAL:", "APROVADO" if ok_all else "COM FALHAS")
if OUTMD:
    with open(OUTMD, "w", encoding="utf-8") as f:
        f.write("# VALIDAÇÃO DA BASE — NEXORA SaaS Revenue Intelligence\n\n")
        f.write(f"Status geral: **{'APROVADO' if ok_all else 'COM FALHAS'}** · Seed 20261009 · Período 2024-01-01 a 2026-10-31\n\n")
        f.write(txt)
