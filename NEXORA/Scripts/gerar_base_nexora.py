# -*- coding: utf-8 -*-
"""
NEXORA — SaaS Revenue Intelligence
Gerador de base sintética relacional (01/01/2024 a 31/10/2026).

Simulação mês a mês, cliente a cliente, com comportamento causal:
adoção latente -> uso -> health score -> churn / expansão / contração / reativação.
Saída: CSVs UTF-8, vírgula, datas YYYY-MM-DD, decimal com ponto.

Uso: python gerar_base_nexora.py <pasta_saida>
"""
import sys, os, math
import numpy as np
import pandas as pd

SEED = 20261009
rng = np.random.default_rng(SEED)
OUT = sys.argv[1] if len(sys.argv) > 1 else "Data"
os.makedirs(OUT, exist_ok=True)

DATA_INI = pd.Timestamp("2024-01-01")
DATA_FIM = pd.Timestamp("2026-10-31")
MESES = pd.date_range(DATA_INI, DATA_FIM, freq="MS")
NM = len(MESES)  # 34
MES_IDX = {m: i for i, m in enumerate(MESES)}

# ---------------------------------------------------------------- DIMENSÕES
PLANOS = pd.DataFrame({
    "PlanoID": [1, 2, 3, 4],
    "Plano": ["Starter", "Growth", "Pro", "Enterprise"],
    "OrdemPlano": [1, 2, 3, 4],
    "PrecoBaseMensal": [249.0, 649.0, 1490.0, 4900.0],
    "UsuariosInclusos": [3, 10, 25, 75],
    "PrecoUsuarioExtra": [39.0, 35.0, 29.0, 25.0],
    "Posicionamento": ["Entrada / micro e pequenas", "Intermediário / times em crescimento",
                       "Avançado / automação e API", "Corporativo / contratos longos"],
    "CorPlano": ["#6E86B3", "#1678FF", "#00B8F5", "#6736F5"],
})
PRECO = dict(zip(PLANOS.PlanoID, PLANOS.PrecoBaseMensal))
INCL = dict(zip(PLANOS.PlanoID, PLANOS.UsuariosInclusos))
PEXTRA = dict(zip(PLANOS.PlanoID, PLANOS.PrecoUsuarioExtra))
NOME_PLANO = dict(zip(PLANOS.PlanoID, PLANOS.Plano))

SEGMENTOS = ["Serviços", "Tecnologia", "Consultoria", "Agência", "Distribuição",
             "Educação", "Contabilidade", "Imobiliário", "Saúde", "Varejo B2B"]
dSeg = pd.DataFrame({"SegmentoID": range(1, 11), "Segmento": SEGMENTOS})
SEG_W = {2024: [13, 13, 11, 11, 10, 9, 10, 8, 9, 6],
         2025: [12, 13, 10, 10, 10, 8, 9, 8, 9, 11],
         2026: [11, 12, 10, 9, 9, 8, 9, 7, 9, 16]}

PORTES = ["Micro", "Pequena", "Média", "Enterprise"]
dPorte = pd.DataFrame({"PorteID": [1, 2, 3, 4], "Porte": PORTES, "OrdemPorte": [1, 2, 3, 4],
                       "FaixaFuncionarios": ["1-9", "10-49", "50-249", "250+"]})

CANAIS = [  # id, nome, tipo, pago
    (1, "Google Ads", "Mídia Paga"), (2, "Meta Ads", "Mídia Paga"), (3, "LinkedIn Ads", "Mídia Paga"),
    (4, "Conteúdo Orgânico", "Inbound"), (5, "Indicação", "Relacionamento"), (6, "Parceiros", "Relacionamento"),
    (7, "Outbound", "Vendas Ativas"), (8, "Eventos", "Vendas Ativas"), (9, "Webinar", "Inbound"),
    (10, "Marketplace", "Inbound")]
dCanal = pd.DataFrame(CANAIS, columns=["CanalID", "Canal", "TipoCanal"])
dCanal["MidiaPaga"] = np.where(dCanal.TipoCanal == "Mídia Paga", "Sim", "Não")
CANAL_W = {2024: [24, 14, 6, 14, 10, 8, 7, 4, 6, 7],
           2025: [25, 13, 7, 13, 11, 8, 7, 4, 6, 6],
           2026: [27, 13, 8, 12, 10, 8, 7, 4, 5, 6]}
# CAC alvo por canal (R$) por ano — Google/Meta perdem eficiência em 2026
CAC_ALVO = {1: (1650, 1950, 2950), 2: (1400, 1650, 2350), 3: (4200, 4350, 4700), 4: (850, 820, 900),
            5: (420, 430, 460), 6: (1250, 1280, 1350), 7: (5200, 5100, 5300), 8: (4600, 4700, 4900),
            9: (1050, 1080, 1150), 10: (880, 900, 980)}
# funil por canal: lead->MQL, MQL->SQL, SQL->Trial, Trial->Paid (2024/25) e trial->paid 2026
FUNIL = {1: (.42, .38, .62, .21, .165), 2: (.36, .33, .60, .16, .135), 3: (.55, .48, .70, .27, .25),
         4: (.48, .40, .66, .25, .24), 5: (.80, .70, .82, .40, .39), 6: (.70, .62, .78, .33, .32),
         7: (.60, .55, .72, .30, .29), 8: (.62, .52, .74, .29, .28), 9: (.50, .42, .66, .23, .22),
         10: (.45, .40, .64, .19, .18)}
CICLO_VENDA = {1: (5, 20), 2: (4, 18), 3: (25, 55), 4: (10, 30), 5: (7, 21), 6: (15, 40),
               7: (40, 95), 8: (20, 60), 9: (10, 35), 10: (3, 14)}
VISIT_TO_LEAD = {1: .031, 2: .024, 3: .042, 4: .028, 5: .30, 6: .20, 7: .10, 8: .12, 9: .09, 10: .035}

FUNCS = [(1, "CRM", "Core"), (2, "Pipeline", "Core"), (3, "Tarefas", "Produtividade"),
         (4, "Metas", "Produtividade"), (5, "Automação", "Automação"), (6, "Dashboard", "Analytics"),
         (7, "Relatórios", "Analytics"), (8, "API", "Plataforma"), (9, "Integrações", "Plataforma"),
         (10, "Gestão de Equipe", "Produtividade")]
dFunc = pd.DataFrame(FUNCS, columns=["FuncionalidadeID", "Funcionalidade", "CategoriaFuncionalidade"])
FUNC_POP = np.array([1.0, .95, .75, .55, .5, .6, .55, .25, .35, .45])
FUNC_MINPLANO = {8: 3}  # API a partir do Pro

ADDONS = [(1, "Usuários Extras", "Recorrente", 0.0), (2, "Automações+", "Recorrente", 149.0),
          (3, "Armazenamento+", "Recorrente", 89.0), (4, "API Avançada", "Recorrente", 390.0),
          (5, "Integrações Premium", "Recorrente", 199.0), (6, "Suporte Premium", "Recorrente", 490.0),
          (7, "Treinamento", "Único", 1800.0)]
dAddOn = pd.DataFrame(ADDONS, columns=["AddOnID", "AddOn", "TipoCobrancaAddOn", "PrecoMensal"])
ADDON_PRECO = {r[0]: r[3] for r in ADDONS}
ADDON_AFIN = {2: [.6, 1, 1.4, 1.2], 3: [.5, .8, 1, 1.2], 4: [0, .2, 1.6, 1.4], 5: [.3, .9, 1.4, 1.3],
              6: [.1, .5, 1.0, 1.8]}  # afinidade por plano

FAIXAS = pd.DataFrame({"FaixaHealth": ["Saudável", "Atenção", "Risco", "Crítico"],
                       "OrdemFaixa": [1, 2, 3, 4], "LimiteInferior": [75, 55, 35, 0],
                       "CorFaixa": ["#00D7C0", "#1678FF", "#F5A524", "#FF607A"]})

MOTIVOS = ["Preço", "Baixo uso", "Falta de funcionalidade", "Concorrente", "Encerramento",
           "Suporte", "Complexidade", "ROI baixo", "Inadimplência"]

CIDADES = [("São Paulo", "SP", "Sudeste", 22), ("Campinas", "SP", "Sudeste", 4), ("Rio de Janeiro", "RJ", "Sudeste", 9),
           ("Belo Horizonte", "MG", "Sudeste", 7), ("Vitória", "ES", "Sudeste", 2), ("Curitiba", "PR", "Sul", 6),
           ("Porto Alegre", "RS", "Sul", 5), ("Florianópolis", "SC", "Sul", 4), ("Joinville", "SC", "Sul", 2),
           ("Brasília", "DF", "Centro-Oeste", 5), ("Goiânia", "GO", "Centro-Oeste", 3), ("Campo Grande", "MS", "Centro-Oeste", 1),
           ("Salvador", "BA", "Nordeste", 4), ("Recife", "PE", "Nordeste", 4), ("Fortaleza", "CE", "Nordeste", 3),
           ("Natal", "RN", "Nordeste", 1), ("Manaus", "AM", "Norte", 2), ("Belém", "PA", "Norte", 2)]

# ---------------------------------------------------------------- NOMES DE EMPRESAS
P1 = ["Alfa", "Nova", "Prime", "Vetor", "Lumen", "Atlas", "Orion", "Vértice", "Sinergia", "Horizonte", "Pulsar",
      "Ápice", "Delta", "Fluxo", "Nexo", "Aurora", "Rumo", "Brava", "Zenit", "Elo", "Vita", "Cobalto", "Mosaico",
      "Ponto", "Terra", "Lince", "Farol", "Quantum", "Sigma", "Trilha", "Arco", "Raiz", "Onda", "Cume", "Polo"]
P2 = {"Serviços": ["Serviços", "Facilities", "Soluções"], "Tecnologia": ["Tech", "Sistemas", "Digital", "Labs"],
      "Consultoria": ["Consultoria", "Advisory", "Gestão"], "Agência": ["Agência", "Studio", "Comunicação"],
      "Distribuição": ["Distribuidora", "Logística", "Atacado"], "Educação": ["Educação", "Ensino", "Academy"],
      "Contabilidade": ["Contábil", "Contabilidade", "Fiscal"], "Imobiliário": ["Imóveis", "Imobiliária", "Realty"],
      "Saúde": ["Saúde", "Clínicas", "Med"], "Varejo B2B": ["Comercial", "Suprimentos", "Trade"]}
SUF = ["Ltda", "S.A.", "ME", "EIRELI", "Ltda", "Ltda"]
_nomes = set()


def nome_empresa(seg):
    for _ in range(50):
        n = f"{rng.choice(P1)} {rng.choice(P2[seg])}"
        if rng.random() < .35:
            n = f"{rng.choice(P1)}{rng.choice(['', 'x', 'ia', 'on'])} {rng.choice(P2[seg])}"
        n = f"{n} {rng.choice(SUF)}"
        if n not in _nomes:
            _nomes.add(n)
            return n
    n = f"{n} {len(_nomes)}"
    _nomes.add(n)
    return n


def wpick(items, w):
    w = np.asarray(w, float)
    return items[rng.choice(len(items), p=w / w.sum())]


# ---------------------------------------------------------------- AQUISIÇÃO MENSAL
novos_mes = []
for i, m in enumerate(MESES):
    if m.year == 2024:
        base = 112 + 88 * (i / 11)
    elif m.year == 2025:
        base = 200 + 38 * ((i - 12) / 11)
    else:
        base = 236 + 14 * ((i - 24) / 9)
    saz = {1: .86, 2: .95, 3: 1.08, 4: 1.0, 5: 1.03, 6: .97, 7: .95, 8: 1.07, 9: 1.04, 10: 1.06, 11: 1.0, 12: .84}[m.month]
    novos_mes.append(int(round(base * saz * rng.normal(1, .045))))

# ---------------------------------------------------------------- ESTRUTURAS DE SAÍDA
clientes, snaps, movs, assin, addons_rows, uso, eventos = [], [], [], [], [], [], []
tickets, faturas, aquis, usuarios = [], [], [], []
tk_id = fat_id = ass_id = add_id = usr_id = 0


def ano_idx(y):
    return {2024: 0, 2025: 1, 2026: 2}[y]


class Cli:
    pass


cli_list = []
cid = 0
for i, m in enumerate(MESES):
    y = m.year
    n = novos_mes[i]
    canais_mes = [wpick(list(range(1, 11)), CANAL_W[y]) for _ in range(n)]
    # garante pelo menos 1 cliente por canal/mês (CAC consistente)
    for c in range(1, 11):
        if c not in canais_mes:
            canais_mes[rng.integers(0, n)] = c
    for c in canais_mes:
        cid += 1
        k = Cli()
        k.id = cid
        k.canal = c
        k.seg_w = list(SEG_W[y])
        if c in (1, 2):  # Varejo B2B fortemente via mídia paga
            k.seg_w[9] *= 1.9
        if c in (3, 7):
            k.seg_w[1] *= 1.4; k.seg_w[2] *= 1.3
        k.seg = wpick(list(range(1, 11)), k.seg_w)
        pw = [40, 35, 20, 5]
        if c in (3, 7, 8):
            pw = [8, 27, 40, 25]
        elif c in (2, 10):
            pw = [58, 32, 9, 1]
        elif c == 6:
            pw = [25, 38, 28, 9]
        k.porte = wpick([1, 2, 3, 4], pw)
        planw = {1: [70, 25, 5, 0], 2: [36, 44, 18, 2], 3: [8, 34, 48, 10], 4: [0, 6, 36, 58]}[k.porte][:]
        if y == 2024:
            planw[0] *= 1.35
        elif y == 2025:
            planw[2] *= 1.25
        else:
            planw[2] *= 1.2; planw[3] *= 1.1
        k.plano = wpick([1, 2, 3, 4], planw)
        k.plano_entrada = k.plano
        k.anual = rng.random() < {1: .15, 2: .30, 3: .45, 4: .85}[k.plano]
        k.data_aq = m + pd.Timedelta(days=int(rng.integers(0, m.days_in_month)))
        k.mes_aq = i
        k.cidade = wpick(CIDADES, [x[3] for x in CIDADES])
        # usuários iniciais
        base_u = {1: (1, 4), 2: (4, 12), 3: (10, 32), 4: (35, 130)}[k.plano]
        k.users = int(rng.integers(base_u[0], base_u[1] + 1))
        if k.porte >= 3 and k.plano <= 2:
            k.users += int(rng.integers(0, 4))
        # adoção latente
        a = rng.normal(.56, .17)
        a += {5: .12, 6: .05, 1: -.04, 2: -.08, 10: -.03, 3: .02, 7: .03}.get(c, 0)
        a += {2: .05, 10: .0, 9: -.02, 6: -.03}.get(k.seg, 0)
        if k.seg == 10:
            a -= .07
        if y == 2026:
            a -= .08
            if k.seg in (10, 6):  # segmentos com queda de ativação em 2026
                a -= .05
        a += {1: -.02, 2: 0, 3: .05, 4: .06}[k.plano]
        k.a0 = float(np.clip(a, .03, .98))
        k.a = k.a0
        k.early = float(np.clip(k.a0 + rng.normal(0, .14), 0, 1))  # uso nos primeiros 30 dias
        k.integracao = False
        k.mes_integ = None
        k.addons = {}  # addon_id -> qty
        if k.plano >= 3 and rng.random() < .35:
            k.addons[int(wpick([2, 4, 5, 6], [1, 1.2, 1, .6]))] = 1
        if k.plano == 4 and rng.random() < .55:
            k.addons[6] = 1
        k.desc = .0
        if k.seg == 10 and rng.random() < .55:
            k.desc = .12  # promo agressiva no Varejo B2B -> ARPA menor
        elif rng.random() < .12:
            k.desc = .05
        k.preco_idx = {2024: 1.0, 2025: 1.05, 2026: 1.10}[y]
        k.ativo = False
        k.ja_ativo = False
        k.churn_mes = None
        k.motivo = None
        k.motivos_hist = []
        k.inicio_contrato = i
        k.lowcsat = 0
        k.atraso = 0
        k.mrr_prev = 0.0
        k.plano_prev = k.plano
        k.reativado = False
        k.n_churn = 0
        k.logins_prev = None
        k.hist_health = None
        k.ass_atual = None
        k.cancel_data = None
        k.addon_start = {}
        cli_list.append(k)

N_CLI = len(cli_list)
by_month = {}
for k in cli_list:
    by_month.setdefault(k.mes_aq, []).append(k)


def mrr_de(k):
    if not k.ativo:
        return 0.0, 0.0, 0.0
    fator = (0.85 if k.anual else 1.0) * (1 - k.desc) * k.preco_idx
    base = PRECO[k.plano] * fator
    extra = max(0, k.users - INCL[k.plano]) * PEXTRA[k.plano] * fator
    ad = sum(ADDON_PRECO[a] * q for a, q in k.addons.items() if a != 7) * fator
    return round(base, 2), round(extra, 2), round(ad, 2)


def novo_contrato(k, i, motivo_abertura):
    global ass_id
    ass_id += 1
    b, e, ad = mrr_de(k)
    mrr = b + e + ad
    prazo = 12 if k.anual else 1
    k.ass_atual = dict(AssinaturaID=ass_id, ClienteID=k.id, PlanoID=k.plano,
                       TipoCobranca="Anual" if k.anual else "Mensal",
                       DataInicio=max(MESES[i], k.data_aq) if i == k.mes_aq else MESES[i],
                       DataFim=None, StatusAssinatura="Ativa", TipoAbertura=motivo_abertura,
                       MRRInicial=round(mrr, 2), PrazoMeses=prazo, ValorContrato=round(mrr * prazo, 2),
                       UsuariosContratados=k.users, MotivoEncerramento=None)


def fecha_contrato(k, i, status, motivo=None):
    if k.ass_atual is None:
        return
    k.ass_atual["DataFim"] = (MESES[i] + pd.offsets.MonthEnd(0)) if status == "Cancelada" else MESES[i] - pd.Timedelta(days=1)
    if k.ass_atual["DataFim"] < k.ass_atual["DataInicio"]:
        k.ass_atual["DataFim"] = k.ass_atual["DataInicio"]
    k.ass_atual["StatusAssinatura"] = status
    k.ass_atual["MotivoEncerramento"] = motivo
    assin.append(k.ass_atual)
    k.ass_atual = None


def emitir_fatura(k, i, valor_liq, bruto, desconto, tipo, ciclo):
    global fat_id
    fat_id += 1
    emiss = MESES[i] if i != k.mes_aq else k.data_aq
    venc = emiss + pd.Timedelta(days=10)
    # comportamento de pagamento
    p_inad = .018 + (.02 if k.plano == 1 else 0) + (.025 if k.seg == 10 else 0) + (.015 if k.a < .35 else 0)
    if MESES[i].year == 2026:
        p_inad += .006
    r = rng.random()
    estorno = 0.0
    if r < p_inad:
        status, pag = "Inadimplente", None
    elif r < p_inad + .085:
        status, pag = "Pago com atraso", venc + pd.Timedelta(days=int(rng.integers(3, 46)))
    elif r < p_inad + .085 + .006:
        status, pag = "Estornado", venc - pd.Timedelta(days=int(rng.integers(0, 6)))
        estorno = valor_liq
    else:
        status, pag = "Pago", venc - pd.Timedelta(days=int(rng.integers(0, 9)))
    if pag is not None and pag > DATA_FIM:
        status, pag = "Em aberto", None
    if status == "Inadimplente" and venc + pd.Timedelta(days=30) > DATA_FIM:
        status = "Em aberto"
    pago = 0.0 if pag is None else round(valor_liq, 2)
    faturas.append(dict(FaturaID=fat_id, ClienteID=k.id, DataEmissao=emiss.normalize(), DataVencimento=venc.normalize(),
                        DataPagamento=None if pag is None else pag.normalize(), TipoFatura=tipo, TipoCobranca=ciclo,
                        ValorBruto=round(bruto, 2), Desconto=round(desconto, 2), ValorLiquido=round(valor_liq, 2),
                        ValorPago=pago, ValorEstornado=round(estorno, 2),
                        ValorRecebido=round(pago - estorno, 2), StatusPagamento=status,
                        DiasAtraso=0 if pag is None or pag <= venc else int((pag - venc).days)))
    return status


def registrar_tickets(k, i):
    global tk_id
    lam = (.10 + .05 * math.sqrt(k.users)) * (1.35 - .7 * k.a) * (1.25 if k.plano == 4 else 1)
    if i - k.inicio_contrato <= 1:
        lam *= 1.6  # onboarding
    nt = rng.poisson(lam)
    lows = 0
    for _ in range(nt):
        tk_id += 1
        cw = [3.0 + 2.5 * (1 - k.a), 1.6 if k.integracao else .5, 1.2, .5 + 1.5 * (k.atraso > 0),
              1.5 + 1.2 * (1 - k.a), 1.0 + 1.5 * (1 - k.a)]
        cat = wpick(["Dúvida", "Integração", "Bug", "Cobrança", "Configuração", "Treinamento"], cw)
        prio = wpick(["Baixa", "Média", "Alta", "Crítica"], [35, 40, 19, 6] if cat != "Bug" else [10, 35, 38, 17])
        sla = {"Baixa": 48, "Média": 24, "Alta": 8, "Crítica": 4}[prio]
        if k.plano == 4 or 6 in k.addons:
            sla = max(2, sla // 2)
        resp = max(.1, rng.gamma(2, sla * .18))
        if MESES[i].year == 2025 and MESES[i].month in (4, 5, 6):
            resp *= 1.25
        res = resp + rng.gamma(2.2, sla * .45 * (1.6 if cat in ("Bug", "Integração") else 1))
        dentro = res <= sla * 1.6
        csat_mu = 4.35 - (0 if dentro else 1.1) - (.35 if cat == "Bug" else 0) - (.25 if k.a < .35 else 0)
        csat = int(np.clip(round(rng.normal(csat_mu, .75)), 1, 5))
        if csat <= 2:
            lows += 1
        dt = MESES[i] + pd.Timedelta(days=int(rng.integers(0, MESES[i].days_in_month)))
        if i == k.mes_aq and dt < k.data_aq:
            dt = k.data_aq
        if dt > DATA_FIM:
            dt = DATA_FIM
        tickets.append(dict(TicketID=tk_id, ClienteID=k.id, DataAbertura=dt.normalize(), Categoria=cat, Prioridade=prio,
                            SLAHoras=sla, TempoPrimeiraRespostaH=round(resp, 1), TempoResolucaoH=round(res, 1),
                            DentroSLA="Sim" if dentro else "Não", Satisfacao=csat))
    return nt, lows


def pick_motivo(k, i, involuntario):
    if involuntario:
        return "Inadimplência"
    w = {"Preço": 1.0 + (1.6 if k.plano == 1 else 0) + (.6 if k.seg == 10 else 0),
         "Baixo uso": .6 + 3.0 * (1 - k.a) ** 2 + (1.2 if k.early < .35 else 0),
         "Falta de funcionalidade": .7 + (.6 if k.plano >= 3 else 0),
         "Concorrente": .9 + (.5 if k.plano == 4 else 0) + (.4 if MESES[i].year == 2026 else 0),
         "Encerramento": .55 + (.4 if k.porte == 1 else 0),
         "Suporte": .3 + 1.2 * k.lowcsat,
         "Complexidade": .4 + 1.0 * (1 - k.a) + (.4 if k.plano == 1 else 0),
         "ROI baixo": .6 + 1.8 * (1 - k.a)}
    return wpick(list(w.keys()), list(w.values()))


# ---------------------------------------------------------------- LOOP MENSAL
churned_pool = []
for i, m in enumerate(MESES):
    y = m.year
    # novos clientes
    for k in by_month.get(i, []):
        k.ativo = True
        k.ja_ativo = True
        k.inicio_contrato = i
        novo_contrato(k, i, "Nova")
        for a in list(k.addons):
            k.addon_start[a] = i
    # reativações
    for k in list(churned_pool):
        if k.motivo == "Encerramento":
            churned_pool.remove(k); continue
        dt = i - k.churn_mes
        if 3 <= dt <= 15:
            p = .022 * (1.5 if k.motivo in ("Preço", "Concorrente") else 1) * (1.3 if k.a0 > .5 else .8)
            if y == 2026:
                p *= 1.1
            if rng.random() < p:
                k.ativo = True
                k.reativado = True
                k.plano = k.plano if rng.random() < .65 else max(1, k.plano - 1)
                k.users = max(1, int(round(k.users * rng.uniform(.6, 1.0))))
                k.addons = {}
                k.a = float(np.clip(k.a0 + rng.normal(.05, .1), .1, .95))
                k.inicio_contrato = i
                k.preco_idx = {2024: 1.0, 2025: 1.05, 2026: 1.10}[y]
                novo_contrato(k, i, "Reativação")
                churned_pool.remove(k)
        elif dt > 15:
            churned_pool.remove(k)

    for k in cli_list:
        if not k.ativo or k.mes_aq > i:
            continue
        ten = i - k.inicio_contrato
        novo_no_mes = (i == k.mes_aq) or (ten == 0 and k.reativado)
        # dinâmica de adoção
        if not novo_no_mes:
            drift = .012 if k.integracao else -.004
            if ten <= 3 and k.early < .35:
                drift -= .025
            k.a = float(np.clip(k.a + drift + rng.normal(0, .045), .02, .99))
        # integração
        if not k.integracao and ten <= 8:
            pi = (.03 + .16 * k.a) * {1: .5, 2: 1, 3: 1.4, 4: 1.6}[k.plano]
            if rng.random() < pi:
                k.integracao = True
                k.mes_integ = i
        nt, lows = registrar_tickets(k, i)
        k.lowcsat = .6 * k.lowcsat + lows
        # faturamento
        b, e, ad = mrr_de(k)
        mrr_now = b + e + ad
        fator = (0.85 if k.anual else 1.0) * (1 - k.desc) * k.preco_idx
        bruto_m = mrr_now / max(fator, 1e-9) * k.preco_idx
        if k.anual:
            if ten % 12 == 0:
                st = emitir_fatura(k, i, mrr_now * 12, bruto_m * 12, bruto_m * 12 - mrr_now * 12, "Assinatura anual", "Anual")
            else:
                st = "Pago"
        else:
            st = emitir_fatura(k, i, mrr_now, bruto_m, bruto_m - mrr_now, "Assinatura mensal", "Mensal")
        if novo_no_mes and k.plano >= 3 and not k.reativado:
            fee = 2500.0 if k.plano == 3 else 9800.0
            emitir_fatura(k, i, fee, fee, 0, "Implantação (não recorrente)", "Único")
        if st == "Inadimplente":
            k.atraso += 1
        else:
            k.atraso = max(0, k.atraso - 1)

        # ---------- churn
        churn = False
        involunt = False
        if not novo_no_mes:
            h = {1: .033, 2: .027, 3: .0165, 4: .0068}[k.plano]
            h *= (1.65 - 1.25 * k.a)
            if ten <= 6 and k.early < .35:
                h *= 2.1
            if k.integracao:
                h *= .55
            h *= {5: .58, 6: .82, 1: 1.08, 2: 1.32, 3: .9, 7: .88, 8: .9, 9: 1.0, 10: 1.15, 4: .95}[k.canal]
            h *= {10: 1.45, 6: 1.1, 2: .9, 7: .85}.get(k.seg, 1.0)
            if y == 2026 and k.plano == 1:
                h *= 1.75
            if k.mes_aq >= 24:
                h *= 1.3
            if ten <= 3:
                h *= 1.25
            h *= (1 + .35 * min(k.lowcsat, 3))
            if k.anual:
                h = 1 - (1 - h) ** 12 if (ten > 0 and ten % 12 == 0) else 0.0
                h *= .8
            if rng.random() < h:
                churn = True
            if k.atraso >= 2 and rng.random() < .45:
                churn = True; involunt = True
        if churn:
            k.motivo = pick_motivo(k, i, involunt)
            k.ativo = False
            k.churn_mes = i
            k.n_churn += 1
            k.cancel_data = m + pd.Timedelta(days=int(rng.integers(0, m.days_in_month)))
            fecha_contrato(k, i, "Cancelada", k.motivo)
            for a, s in list(k.addon_start.items()):
                addons_rows.append((k.id, a, s, i, k.addons.get(a, 1) if a != 1 else 0))
            k.addon_start = {}
            churned_pool.append(k)
        else:
            # ---------- expansão / contração
            mult_exp = (.35 + 1.25 * k.a)
            if y == 2025:
                mult_exp *= 1.3
            plano_antes = k.plano
            pode_contrair = (not k.anual) or (ten > 0 and ten % 12 == 0) or (y == 2025 and m.month in (4, 5, 6))
            if not novo_no_mes:
                if rng.random() < {1: .014, 2: .032, 3: .085, 4: .03}[k.plano] * mult_exp:
                    k.users += int(rng.integers(*{1: (1, 3), 2: (1, 5), 3: (2, 10), 4: (3, 12)}[k.plano]))
                if rng.random() < {1: .006, 2: .016, 3: .045, 4: .028}[k.plano] * mult_exp:
                    cand = [a for a in ADDON_AFIN if a not in k.addons and ADDON_AFIN[a][k.plano - 1] > 0]
                    if cand:
                        ao = int(wpick(cand, [ADDON_AFIN[a][k.plano - 1] for a in cand]))
                        k.addons[ao] = 1
                        k.addon_start[ao] = i
                # treinamento (único)
                if rng.random() < .004 * (1.5 if k.a < .4 else 1):
                    emitir_fatura(k, i, 1800, 1800, 0, "Treinamento (não recorrente)", "Único")
                # upgrade
                pu = {1: .011, 2: .0095, 3: .0035, 4: 0}[k.plano] * (.3 + 1.6 * k.a)
                if k.users >= INCL[k.plano]:
                    pu *= 1.6
                if y == 2025:
                    pu *= 1.35
                if k.plano < 4 and rng.random() < pu:
                    k.plano += 1
                    k.preco_idx = {2024: 1.0, 2025: 1.05, 2026: 1.10}[y]
                if pode_contrair:
                    choque = 7.5 if (y == 2025 and m.month in (4, 5, 6)) else 1.0
                    pc = .011 * (1.7 - 1.3 * k.a) * choque
                    if k.users > 1 and rng.random() < pc:
                        k.users = max(1, k.users - int(rng.integers(1, max(2, k.users // 4 + 1))))
                    if k.addons and rng.random() < .007 * (1.7 - 1.3 * k.a) * choque:
                        ao = int(rng.choice(list(k.addons)))
                        k.addons.pop(ao)
                        if ao in k.addon_start:
                            addons_rows.append((k.id, ao, k.addon_start.pop(ao), i, 1))
                    if k.plano > 1 and rng.random() < .0035 * (1.7 - 1.3 * k.a) * (2.4 if choque > 1 else 1):
                        k.plano -= 1
            if k.plano != plano_antes:
                fecha_contrato(k, i, "Upgrade" if k.plano > plano_antes else "Downgrade")
                k.inicio_contrato = i if not k.anual else k.inicio_contrato
                novo_contrato(k, i, "Upgrade" if k.plano > plano_antes else "Downgrade")

        # ---------- MRR fim do mês e movimento
        b, e, ad = mrr_de(k)
        mrr_cur = round(b + e + ad, 2)
        prev = round(k.mrr_prev, 2)
        p0, p1 = k.plano_prev, k.plano
        dmes = MESES[i]

        def mov(tipo, valor, plano, sub, motivo=None):
            movs.append(dict(ClienteID=k.id, DataMes=dmes, TipoMovimento=tipo, Subtipo=sub, PlanoID=plano,
                             PlanoAnteriorID=p0 if prev > 0 else None, ValorMRR=round(valor, 2), MotivoChurn=motivo))
        if prev == 0 and mrr_cur > 0:
            if k.reativado and not (i == k.mes_aq):
                mov("Reactivation", mrr_cur, p1, "Reativação")
            else:
                mov("New", mrr_cur, p1, "Novo cliente")
        elif prev > 0 and mrr_cur == 0:
            mov("Churn", -prev, p0, "Involuntário" if k.motivo == "Inadimplência" else "Voluntário", k.motivo)
        elif prev > 0:
            if p0 != p1:
                mov("Plan Migration Out", -prev, p0, "Migração de plano")
                mov("Plan Migration In", prev, p1, "Migração de plano")
            d = round(mrr_cur - prev, 2)
            if d > 0:
                mov("Expansion", d, p1, "Upgrade de plano" if p1 > p0 else "Usuários / add-ons")
            elif d < 0:
                mov("Contraction", d, p1, "Downgrade de plano" if p1 < p0 else "Redução de usuários / add-ons")
        if mrr_cur > 0:
            snaps.append(dict(ClienteID=k.id, DataMes=dmes, PlanoID=p1, TipoCobranca="Anual" if k.anual else "Mensal",
                              MRRPlano=b, MRRUsuariosExtras=e, MRRAddOns=ad, MRR=mrr_cur, Usuarios=k.users,
                              IdadeCohort=i - k.mes_aq))
            # ---------- uso do produto
            frac = 1.0
            if novo_no_mes and i == k.mes_aq:
                frac = max(.15, (MESES[i] + pd.offsets.MonthEnd(0) - k.data_aq).days / MESES[i].days_in_month)
            at = k.a if not (novo_no_mes and i == k.mes_aq) else k.early
            ativos = int(np.clip(round(k.users * np.clip(.22 + .72 * at + rng.normal(0, .07), .05, 1)), 1, k.users))
            logins = int(round(ativos * 19 * (.45 + at) * frac * rng.normal(1, .08)))
            logins = max(1, logins)
            sess = int(round(logins * rng.uniform(1.15, 1.45)))
            dau = round(ativos * np.clip(.25 + .5 * at + rng.normal(0, .04), .05, .95), 1)
            wau = round(min(ativos, ativos * np.clip(.62 + .33 * at, .3, 1)), 1)
            nfeat_max = 10 if k.plano >= 3 else 9
            nfeat = int(np.clip(round(1.5 + 8.2 * at + rng.normal(0, .8)), 1, nfeat_max))
            auto = int(rng.poisson(max(.1, k.users * at * {1: 4, 2: 12, 3: 26, 4: 30}[k.plano] * frac)))
            opps = int(rng.poisson(max(.1, ativos * 6 * (.5 + at) * frac)))
            rels = int(rng.poisson(max(.1, ativos * 2.2 * at * frac)))
            integ = 0
            if k.integracao:
                integ = int(np.clip(1 + rng.poisson(.6 + 2.4 * at * (k.plano / 3)), 1, 8))
            var = None if k.logins_prev in (None, 0) else (logins - k.logins_prev) / k.logins_prev
            k.logins_prev = logins
            # health score
            s_login = np.clip(logins / max(ativos, 1) / 28, 0, 1) * 25
            s_users = np.clip(ativos / k.users, 0, 1) * 20
            s_feat = nfeat / 10 * 15
            s_auto = np.clip(auto / max(k.users * 15, 1), 0, 1) * 10
            s_int = (10 if integ > 0 else 0)
            s_tk = 10 * (1 - np.clip(.45 * k.lowcsat + .1 * nt, 0, 1))
            s_fin = 10 if k.atraso == 0 else (4 if k.atraso == 1 else 0)
            s_trend = 0 if var is None else float(np.clip(var * 25, -8, 5))
            hs = float(np.clip(s_login + s_users + s_feat + s_auto + s_int + s_tk + s_fin + s_trend, 0, 100))
            faixa = "Saudável" if hs >= 75 else "Atenção" if hs >= 55 else "Risco" if hs >= 35 else "Crítico"
            pot = "Não"
            if k.plano <= 3 and hs >= 74 and k.users >= INCL[k.plano] * .9 and (nfeat >= 7 or auto > k.users * 20):
                pot = "Sim"
            uso.append(dict(ClienteID=k.id, DataMes=dmes, UsuariosLicenciados=k.users, UsuariosAtivos=ativos,
                            DAU=dau, WAU=wau, MAU=ativos, Logins=logins, Sessoes=sess, Automacoes=auto,
                            Oportunidades=opps, Relatorios=rels, IntegracoesAtivas=integ,
                            FuncionalidadesUsadas=nfeat, TicketsMes=nt, FaturasEmAtraso=k.atraso,
                            VariacaoUsoPct=None if var is None else round(var, 4),
                            HealthScore=round(hs, 1), FaixaHealth=faixa, PotencialUpgrade=pot,
                            MesesDeVida=i - k.inicio_contrato))
            # eventos por funcionalidade
            pop = FUNC_POP.copy()
            if k.plano < 3:
                pop[7] = 0
            if k.integracao:
                pop[8] = 1.2
            else:
                pop[8] = 0
            feats = rng.choice(10, size=min(nfeat, int((pop > 0).sum())), replace=False, p=pop / pop.sum())
            for f in feats:
                ev = int(max(1, logins * FUNC_POP[f] * rng.uniform(.6, 2.2)))
                uu = int(np.clip(round(ativos * FUNC_POP[f] * rng.uniform(.4, 1.0)), 1, ativos))
                eventos.append((k.id, dmes, int(f) + 1, ev, uu))
        k.mrr_prev = mrr_cur
        k.plano_prev = k.plano
        k.hist_health = (uso[-1]["HealthScore"], uso[-1]["FaixaHealth"], uso[-1]["PotencialUpgrade"]) if mrr_cur > 0 else k.hist_health

# fecha contratos e add-ons abertos
for k in cli_list:
    if k.ass_atual is not None:
        assin.append(k.ass_atual)
    for a, s in k.addon_start.items():
        addons_rows.append((k.id, a, s, None, 1))

# ---------------------------------------------------------------- DATAFRAMES
fSnap = pd.DataFrame(snaps)
fSnap.insert(0, "SnapshotID", range(1, len(fSnap) + 1))
fMov = pd.DataFrame(movs)
fMov.insert(0, "MovimentoID", range(1, len(fMov) + 1))
fMov["SinalMovimento"] = np.sign(fMov.ValorMRR).astype(int)
fUso = pd.DataFrame(uso)
fUso.insert(0, "UsoID", range(1, len(fUso) + 1))
fEv = pd.DataFrame(eventos, columns=["ClienteID", "DataMes", "FuncionalidadeID", "Eventos", "UsuariosUnicos"])
fEv.insert(0, "EventoID", range(1, len(fEv) + 1))
fAss = pd.DataFrame(assin).sort_values(["ClienteID", "DataInicio"])
fTk = pd.DataFrame(tickets)
fFin = pd.DataFrame(faturas)

# add-ons: reconstruir também "usuários extras" a partir do snapshot
ad = pd.DataFrame(addons_rows, columns=["ClienteID", "AddOnID", "MesIni", "MesFim", "Quantidade"])
ad = ad[ad.AddOnID != 1]
ad["DataInicio"] = ad.MesIni.map(lambda x: MESES[int(x)])
ad["DataFim"] = ad.MesFim.map(lambda x: None if pd.isna(x) else MESES[int(x)] - pd.Timedelta(days=1))
ad["DataFim"] = [None if (f is None or pd.isna(f)) else max(f, s) for f, s in zip(ad.DataFim, ad.DataInicio)]
ad["StatusAddOn"] = np.where(ad.MesFim.isna(), "Ativo", "Cancelado")
ad["PrecoMensalLista"] = ad.AddOnID.map(ADDON_PRECO)
fAdd = ad[["ClienteID", "AddOnID", "DataInicio", "DataFim", "StatusAddOn", "Quantidade", "PrecoMensalLista"]].copy()
fAdd.insert(0, "AddOnContratoID", range(1, len(fAdd) + 1))

# ---------------------------------------------------------------- CLIENTES
last_snap = fSnap.sort_values("DataMes").groupby("ClienteID").tail(1).set_index("ClienteID")
rows = []
for k in cli_list:
    hs = k.hist_health or (None, None, "Não")
    ativo_fim = k.ativo
    rows.append(dict(
        ClienteID=k.id, NomeEmpresa=nome_empresa(SEGMENTOS[k.seg - 1]), SegmentoID=k.seg, PorteID=k.porte,
        CanalID=k.canal, Cidade=k.cidade[0], UF=k.cidade[1], Regiao=k.cidade[2],
        DataAquisicao=k.data_aq.normalize(), CohortMes=MESES[k.mes_aq], CohortAno=MESES[k.mes_aq].year,
        PlanoEntradaID=k.plano_entrada, PlanoAtualID=k.plano, TipoCobranca="Anual" if k.anual else "Mensal",
        StatusAtual=("Ativo" if not k.reativado else "Reativado") if ativo_fim else "Cancelado",
        DataUltimoCancelamento=None if k.cancel_data is None else k.cancel_data.normalize(),
        MotivoUltimoCancelamento=k.motivo if k.cancel_data is not None else None,
        FoiReativado="Sim" if k.reativado else "Não", QtdeCancelamentos=k.n_churn,
        PossuiIntegracao="Sim" if k.integracao else "Não",
        ScoreUsoPrimeiros30Dias=round(k.early * 100, 1),
        AdocaoInicial="Baixa" if k.early < .35 else ("Média" if k.early < .65 else "Alta"),
        DescontoComercialPct=k.desc,
        UsuariosAtuais=int(last_snap.Usuarios.get(k.id, 0)) if ativo_fim else 0,
        MRRAtual=float(last_snap.MRR.get(k.id, 0)) if ativo_fim and last_snap.DataMes.get(k.id) == MESES[-1] else 0.0,
        HealthScoreAtual=hs[0] if ativo_fim else None, FaixaHealthAtual=hs[1] if ativo_fim else None,
        PotencialUpgrade=hs[2] if ativo_fim else "Não"))
dCli = pd.DataFrame(rows)

# ---------------------------------------------------------------- USUÁRIOS
max_users = fSnap.groupby("ClienteID").Usuarios.max()
urows = []
uid = 0
for k in cli_list:
    nu = int(max_users.get(k.id, k.users))
    for j in range(nu):
        uid += 1
        perfil = "Administrador" if j == 0 else wpick(["Gestor", "Vendedor", "SDR", "Operações", "Financeiro"], [15, 45, 15, 15, 10])
        dc = k.data_aq + pd.Timedelta(days=int(rng.integers(0, 15))) if j < 3 else k.data_aq + pd.Timedelta(days=int(rng.integers(0, max(1, (DATA_FIM - k.data_aq).days))))
        dc = min(dc, DATA_FIM)
        urows.append(dict(UsuarioID=uid, ClienteID=k.id, Perfil=perfil, DataCriacao=dc.normalize(),
                          StatusUsuario="Ativo" if (k.ativo and j < k.users) else "Inativo"))
dUsr = pd.DataFrame(urows)

# ---------------------------------------------------------------- AQUISIÇÃO, MARKETING, LEADS, TRIALS
cli_df = pd.DataFrame([dict(ClienteID=k.id, CanalID=k.canal, MesIdx=k.mes_aq, PlanoID=k.plano_entrada,
                            SegmentoID=k.seg, PorteID=k.porte, DataAq=k.data_aq) for k in cli_list])
w_plano = {1: .55, 2: 1.0, 3: 1.85, 4: 5.2}
cli_df["Peso"] = cli_df.PlanoID.map(w_plano) * np.where(cli_df.SegmentoID == 10, 1.25, 1.0)
mk_rows, aq_cost = [], {}
for (c, mi), g in cli_df.groupby(["CanalID", "MesIdx"]):
    y = MESES[mi].year
    cac = CAC_ALVO[c][ano_idx(y)] * 3.4  # escala: payback realista de SaaS B2B (10–20 meses)
    if y == 2026 and c in (1, 2):
        cac *= 1 + .06 * (MESES[mi].month - 1) / 9  # piora progressiva
    mix = g.Peso.mean()
    invest = round(cac * len(g) * mix * rng.normal(1, .06), 2)
    share = g.Peso / g.Peso.sum()
    for cid_, s in zip(g.ClienteID, share):
        aq_cost[cid_] = round(invest * s, 2)
    mk_rows.append(dict(CanalID=c, DataMes=MESES[mi], Investimento=invest, NovosClientes=len(g)))
fMk = pd.DataFrame(mk_rows)

lead_rows, trial_rows = [], []
lid = tid = 0
first_mov = fMov[fMov.TipoMovimento == "New"].set_index("ClienteID").ValorMRR
for (c, mi), g in cli_df.groupby(["CanalID", "MesIdx"]):
    y = MESES[mi].year
    f = FUNIL[c]
    tp = f[4] if y == 2026 else f[3]
    if y == 2026 and c in (1, 2):
        tp *= .93
    C = len(g)
    n_trial = max(C, int(round(C / tp * rng.normal(1, .05))))
    n_sql = max(n_trial, int(round(n_trial / f[2])))
    n_mql = max(n_sql, int(round(n_sql / f[1])))
    n_lead = max(n_mql, int(round(n_mql / f[0])))
    # leads convertidos
    for _, r in g.iterrows():
        lid += 1; tid += 1
        enterprise_like = r.PlanoID == 4
        tlen = 30 if enterprise_like else 14
        t_ini = r.DataAq - pd.Timedelta(days=int(rng.integers(tlen - 6, tlen + 1)))
        ciclo = CICLO_VENDA[c]
        l_dt = t_ini - pd.Timedelta(days=int(rng.integers(ciclo[0], ciclo[1] + 1)))
        mql = l_dt + (t_ini - l_dt) * rng.uniform(.1, .4)
        sql = l_dt + (t_ini - l_dt) * rng.uniform(.5, .9)
        lead_rows.append(dict(LeadID=lid, DataLead=l_dt.normalize(), CanalID=c, SegmentoID=r.SegmentoID, PorteID=r.PorteID,
                              MQL="Sim", DataMQL=mql.normalize(), SQL="Sim", DataSQL=sql.normalize(), Trial="Sim",
                              Convertido="Sim", ClienteID=r.ClienteID))
        trial_rows.append(dict(TrialID=tid, LeadID=lid, CanalID=c, SegmentoID=r.SegmentoID, PorteID=r.PorteID,
                               PlanoInteresseID=r.PlanoID, DataInicioTrial=t_ini.normalize(),
                               DataFimTrial=(t_ini + pd.Timedelta(days=tlen)).normalize(), DuracaoDias=tlen,
                               Convertido="Sim", DataConversao=r.DataAq.normalize(), ClienteID=r.ClienteID,
                               LoginsTrial=int(rng.poisson(8 + 30 * dCli.ScoreUsoPrimeiros30Dias.iat[r.ClienteID - 1] / 100))))
    # leads não convertidos — distribuídos no mês
    nconv = n_lead - C
    stages = np.zeros(nconv, int)  # 0 lead,1 mql,2 sql,3 trial
    idx = rng.permutation(nconv)
    stages[idx[:n_mql - C]] = 1
    stages[idx[:n_sql - C]] = 2
    stages[idx[:n_trial - C]] = 3
    m0 = MESES[mi]
    for s in stages:
        lid += 1
        l_dt = m0 - pd.Timedelta(days=int(rng.integers(0, 40)))
        if l_dt < DATA_INI - pd.Timedelta(days=60):
            l_dt = DATA_INI
        seg = int(wpick(list(range(1, 11)), SEG_W[y]))
        por = int(wpick([1, 2, 3, 4], [45, 33, 17, 5]))
        mql = l_dt + pd.Timedelta(days=int(rng.integers(1, 10))) if s >= 1 else None
        sql = l_dt + pd.Timedelta(days=int(rng.integers(10, 25))) if s >= 2 else None
        lead_rows.append(dict(LeadID=lid, DataLead=l_dt.normalize(), CanalID=c, SegmentoID=seg, PorteID=por,
                              MQL="Sim" if s >= 1 else "Não", DataMQL=mql, SQL="Sim" if s >= 2 else "Não", DataSQL=sql,
                              Trial="Sim" if s >= 3 else "Não", Convertido="Não", ClienteID=None))
        if s >= 3:
            tid += 1
            t_ini = min(sql + pd.Timedelta(days=int(rng.integers(1, 6))), DATA_FIM - pd.Timedelta(days=1))
            trial_rows.append(dict(TrialID=tid, LeadID=lid, CanalID=c, SegmentoID=seg, PorteID=por,
                                   PlanoInteresseID=int(wpick([1, 2, 3, 4], [45, 33, 18, 4])),
                                   DataInicioTrial=t_ini.normalize(), DataFimTrial=(t_ini + pd.Timedelta(days=14)).normalize(),
                                   DuracaoDias=14, Convertido="Não", DataConversao=None, ClienteID=None,
                                   LoginsTrial=int(rng.poisson(5))))
fLeads = pd.DataFrame(lead_rows)
fTrials = pd.DataFrame(trial_rows)
# leads anteriores a 2024 (ciclo de vendas) ficam na janela do calendário
fLeads.loc[fLeads.DataLead < DATA_INI, "DataLead"] = DATA_INI
for col in ("DataMQL", "DataSQL"):
    fLeads[col] = pd.to_datetime(fLeads[col])
    fLeads.loc[fLeads[col] < fLeads.DataLead, col] = fLeads.DataLead
fTrials.loc[fTrials.DataInicioTrial < DATA_INI, "DataInicioTrial"] = DATA_INI

# visitantes / cliques derivados de leads
lead_mes = fLeads.assign(DataMes=fLeads.DataLead.dt.to_period("M").dt.to_timestamp()).groupby(["CanalID", "DataMes"]).size()
fMk["Leads"] = [int(lead_mes.get((c, d), 0)) for c, d in zip(fMk.CanalID, fMk.DataMes)]
fMk["Visitantes"] = [int(round(l / VISIT_TO_LEAD[c] * rng.normal(1, .05))) for c, l in zip(fMk.CanalID, fMk.Leads)]
fMk["Cliques"] = np.where(fMk.CanalID.isin([1, 2, 3]), (fMk.Visitantes * rng.uniform(.9, 1.0, len(fMk))).round(), 0).astype(int)
fMk["Impressoes"] = np.where(fMk.CanalID.isin([1, 2, 3]), (fMk.Cliques / rng.uniform(.012, .03, len(fMk))).round(), 0).astype(int)
fMk = fMk[["CanalID", "DataMes", "Investimento", "Impressoes", "Cliques", "Visitantes", "Leads", "NovosClientes"]]
fMk.insert(0, "MarketingID", range(1, len(fMk) + 1))

fAq = cli_df[["ClienteID", "CanalID", "PlanoID", "DataAq"]].rename(columns={"DataAq": "DataAquisicao"})
fAq["DataMes"] = fAq.DataAquisicao.dt.to_period("M").dt.to_timestamp()
fAq["DataAquisicao"] = fAq.DataAquisicao.dt.normalize()
fAq["CustoAquisicao"] = fAq.ClienteID.map(aq_cost)
fAq["MRRInicial"] = fAq.ClienteID.map(first_mov)
conv_lead = fLeads[fLeads.Convertido == "Sim"].set_index("ClienteID").LeadID
conv_trial = fTrials[fTrials.Convertido == "Sim"].set_index("ClienteID").TrialID
fAq["LeadID"] = fAq.ClienteID.map(conv_lead).astype(int)
fAq["TrialID"] = fAq.ClienteID.map(conv_trial).astype(int)
fAq = fAq.rename(columns={"PlanoID": "PlanoEntradaID"})[["ClienteID", "DataAquisicao", "DataMes", "CanalID", "PlanoEntradaID",
                                                          "LeadID", "TrialID", "CustoAquisicao", "MRRInicial"]]

# ---------------------------------------------------------------- COHORT MENSAL (agregado)
s2 = fSnap.merge(dCli[["ClienteID", "CohortMes", "CanalID", "PlanoEntradaID", "SegmentoID", "PorteID"]], on="ClienteID")
grp = ["CohortMes", "CanalID", "PlanoEntradaID", "SegmentoID", "PorteID"]
base = s2[s2.IdadeCohort == 0].groupby(grp).agg(ClientesIniciais=("ClienteID", "nunique"), MRRInicial=("MRR", "sum")).reset_index()
ativos = s2.groupby(grp + ["IdadeCohort"]).agg(ClientesAtivos=("ClienteID", "nunique"), MRRAtivo=("MRR", "sum")).reset_index()
fCoh = ativos.merge(base, on=grp, how="left")
fCoh = fCoh[["CohortMes", "IdadeCohort", "CanalID", "PlanoEntradaID", "SegmentoID", "PorteID", "ClientesIniciais",
             "ClientesAtivos", "MRRInicial", "MRRAtivo"]].sort_values(["CohortMes", "IdadeCohort"])
# grade completa (combinações sem ativos na idade -> 0 ativos) apenas para idades observáveis
full = []
for _, r in base.iterrows():
    max_age = NM - 1 - MES_IDX[r.CohortMes]
    full.append(pd.DataFrame({"CohortMes": r.CohortMes, "CanalID": r.CanalID, "PlanoEntradaID": r.PlanoEntradaID,
                              "SegmentoID": r.SegmentoID, "PorteID": r.PorteID, "IdadeCohort": range(0, max_age + 1)}))
full = pd.concat(full)
fCoh = full.merge(fCoh.drop(columns=["ClientesIniciais", "MRRInicial"]), on=grp + ["IdadeCohort"], how="left").merge(base, on=grp, how="left")
fCoh[["ClientesAtivos", "MRRAtivo"]] = fCoh[["ClientesAtivos", "MRRAtivo"]].fillna(0)
fCoh["ClientesAtivos"] = fCoh.ClientesAtivos.astype(int)
fCoh = fCoh[["CohortMes", "IdadeCohort", "CanalID", "PlanoEntradaID", "SegmentoID", "PorteID", "ClientesIniciais",
             "ClientesAtivos", "MRRInicial", "MRRAtivo"]].sort_values(["CohortMes", "IdadeCohort", "CanalID"])
fCoh.insert(0, "CohortRowID", range(1, len(fCoh) + 1))

# ---------------------------------------------------------------- RECEITA RECONHECIDA no snapshot
# Revenue = MRR reconhecido no mês + serviços não recorrentes reconhecidos na emissão
fSnap["ReceitaRecorrenteReconhecida"] = fSnap.MRR

# ---------------------------------------------------------------- CALENDÁRIO
cal = pd.DataFrame({"Data": pd.date_range(DATA_INI, DATA_FIM, freq="D")})
MESN = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESL = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
cal["Ano"] = cal.Data.dt.year
cal["MesNum"] = cal.Data.dt.month
cal["MesNome"] = cal.MesNum.map(lambda x: MESL[x - 1])
cal["MesAbrev"] = cal.MesNum.map(lambda x: MESN[x - 1])
cal["AnoMes"] = cal.Ano * 100 + cal.MesNum
cal["MesAno"] = cal.MesAbrev + "/" + (cal.Ano % 100).astype(str).str.zfill(2)
cal["Trimestre"] = "T" + cal.Data.dt.quarter.astype(str)
cal["AnoTrimestre"] = cal.Ano.astype(str) + " " + cal.Trimestre
cal["InicioMes"] = cal.Data.dt.to_period("M").dt.to_timestamp()
cal["IndiceMes"] = (cal.Ano - 2024) * 12 + cal.MesNum
cal["FaseNegocio"] = cal.Ano.map({2024: "2024 · Aquisição", 2025: "2025 · Expansão", 2026: "2026 · Eficiência"})
cal["DiaSemana"] = cal.Data.dt.dayofweek + 1

# ---------------------------------------------------------------- GRAVAÇÃO
def save(df, name):
    df = df.copy()
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            df[c] = df[c].dt.strftime("%Y-%m-%d")
        elif df[c].dtype == object:
            df[c] = df[c].map(lambda v: v.strftime("%Y-%m-%d") if isinstance(v, pd.Timestamp) else v)
    df.to_csv(os.path.join(OUT, f"{name}.csv"), index=False, encoding="utf-8", float_format="%.2f" if name != "fUsoProduto" else None)
    print(f"{name:20s} {len(df):>9,d} linhas")


for c in ("PlanoAnteriorID",):
    fMov[c] = fMov[c].astype("Int64")
for c in ("ClienteID",):
    fLeads[c] = fLeads[c].astype("Int64"); fTrials[c] = fTrials[c].astype("Int64")

save(cal, "dCalendario"); save(dCli, "dCliente"); save(PLANOS, "dPlano"); save(dSeg, "dSegmento")
save(dPorte, "dPorte"); save(dCanal, "dCanalAquisicao"); save(dFunc, "dFuncionalidade"); save(dUsr, "dUsuario")
save(dAddOn, "dAddOn"); save(FAIXAS, "dFaixaHealth")
save(fSnap, "fSnapshotMRR"); save(fMov, "fMovimentoMRR"); save(fAss.reset_index(drop=True), "fAssinaturas")
save(fAdd, "fAddOns"); save(fUso, "fUsoProduto"); save(fEv, "fEventosProduto"); save(fMk, "fMarketing")
save(fLeads, "fLeads"); save(fTrials, "fTrials"); save(fTk, "fSuporte"); save(fFin, "fFinanceiro")
save(fAq, "fAquisicao"); save(fCoh, "fCohortMensal")
print("Clientes:", N_CLI)
