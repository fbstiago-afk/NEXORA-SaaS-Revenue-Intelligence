---
name: power-bi-visuais-inteligentes-universal
description: Biblioteca universal para projetar e implementar visuais modernos, gráficos de colunas inteligentes, HTML/SVG, Deneb, insights acionáveis e personalização Power BI em PBIP/PBIR/TMDL.
version: 1.0.0
language: pt-BR
scope: universal
---

# SKILL UNIVERSAL — POWER BI | VISUAIS INTELIGENTES, COLUNAS PERSONALIZADAS E INSIGHTS

> **Uso:** anexe este Markdown como contexto ao Claude, Codex ou outro agente ao desenvolver ou modernizar **qualquer** relatório Power BI. **Não é um prompt para criar um projeto inteiro**: é uma biblioteca de decisões de design, implementações, padrões analíticos e critérios de aceite. Adapte nomes, métricas e recursos à base real.

## 0. Regras inegociáveis

1. **Sem evidência, sem insight causal.** Não inventar causas, recomendações, previsões, conversões ou KPIs indisponíveis.
2. **Poucos visuais, muito conteúdo útil.** Preferir 3–5 KPIs e 2–4 gráficos por página, ajustando à densidade real e à resolução.
3. **Cores inteligentes:** semáforo depende da direção de negócio da métrica (queda de custo pode ser positiva; alta de atraso é negativa).
4. **Medidas antes de cosmética.** Garantir modelo, filtros, períodos, denominadores, metas e granularidade antes de formatar.
5. **Visual nativo primeiro**, Deneb para gramáticas sofisticadas, HTML Content para componentes/cards e SVG quando agregar clareza. Não trocar interatividade nativa por imagem decorativa.
6. **Nunca assumir suporte de Preview.** Verificar versão do Desktop, recursos habilitados, tenant, certificação do visual e compatibilidade no Service.
7. **HTML Content não é navegador livre.** Não depender de JavaScript, APIs de DOM, timers, recursos remotos, fontes externas ou CSS não suportado. Testar no visual instalado.
8. **TMDL descreve o modelo semântico; PBIR descreve páginas e visuais.** Não confundir os dois formatos.
9. **Não alterar medidas existentes sem verificar dependências.** Fazer cópia/controle de versão e documentar alterações.
10. **Todas as cores, números e mensagens devem responder aos filtros.** Não fixar dados em HTML, SVG ou Vega-Lite.

## 1. Método de seleção dos visuais

| Pergunta de negócio | Visual recomendado | Recurso de inteligência | Evitar |
|---|---|---|---|
| Quais categorias lideram? | Barras horizontais | Top N + Outros, ranking e variação | Rosca com dezenas de itens |
| Como evoluiu ao longo do tempo? | Linha ou colunas | último ponto, máximo/mínimo, meta e YoY | 3 eixos sem unidade clara |
| Quanto falta para a meta? | Bullet / colunas + linha de meta | gap, % atingimento, cor condicional | velocímetro grande |
| Onde está o problema? | Heatmap / matriz | limiares, ordenação e drillthrough | tabela extensa sem sinalização |
| Qual a composição? | Barras empilhadas / 100% | participação, variação de mix | pizza com muitos segmentos |
| Qual o impacto das causas? | Cascata / Pareto | contribuição acumulada e ranking | conclusões causais sem evidência |
| Quais itens são exceções? | Tabela enxuta com data bars | ícones, mini barras e destaque de risco | tabela com 25 colunas |
| Há relação entre variáveis? | Dispersão + quadrantes | mediana, grupos e tooltips | correlação apresentada como causa |
| Qual o risco futuro? | Linha real + projeção | faixa de incerteza e cenários | previsão sem método/limites |
| O que fazer agora? | Card de exceção/insight | prioridade, impacto, próximo passo | narrativa genérica |

## 2. Design system universal

**Tema sugerido (ajustável à marca):** fundo `#F5F7FA`, superfície `#FFFFFF`, texto `#172B4D`, secundário `#64748B`, primário `#1E3A8A`, acento `#0F9D92`, sucesso `#15803D`, alerta `#D97706`, risco `#B91C1C`, borda `#E2E8F0`.

- Fundo preferencialmente claro, azul-marinho + teal, contraste consistente e áreas de respiro.
- Tipografia Segoe UI/Aptos ou fonte disponível, com título de página 22–30 px, título de visual 12–16 px e KPIs 24–36 px, ajustando ao tamanho.
- Cantos de 10–16 px, bordas discretas, sombras suaves (somente quando renderizadas corretamente).
- Títulos dos gráficos centralizados **quando coerente com a hierarquia**; títulos de linhas de tabela à esquerda, cabeçalhos numéricos alinhados com seus dados.
- Primeira coluna de tabelas à esquerda; números à direita; percentuais com precisão coerente; negativos e unidades evidentes.
- Não repetir título, subtítulo, legenda e rótulos quando o mesmo significado já está visível.
- Navegação compacta, botões consistentes, filtros em painel ocultável **com estado e indicação dos filtros aplicados**.
- Preferir tema JSON centralizado; modern visual defaults apenas se disponíveis/estáveis na versão utilizada.

### 2.1 Estados obrigatórios

- Normal, selecionado, hover (se suportado), sem dados, carregando (quando houver mecanismo real), erro e valor negativo.
- Indicador de filtros ativos no topo: período, unidade, canal, segmento, demais dimensões relevantes; abreviar listas longas como `3 regiões`.
- Evitar verde/vermelho como única codificação: usar sinais ▲▼, rótulos, padrões e tooltips acessíveis.

## 3. Biblioteca de gráficos de colunas inteligentes

### COL-01 — Colunas com cor por desempenho

**Uso:** vendas, produção, receita, volume, chamados, entregas. Uma medida determina a cor de cada categoria/período.

```DAX
Cor Coluna vs Meta =
VAR Atual = [Valor Realizado]
VAR Meta = [Valor Meta]
RETURN
    SWITCH (
        TRUE(),
        ISBLANK(Atual) || ISBLANK(Meta), "#94A3B8",
        Atual >= Meta, "#0F9D92",
        Atual >= Meta * 0.9, "#D97706",
        "#B91C1C"
    )
```

**Aplicação:** gráfico nativo de colunas > Cores dos dados > `fx` > Valor do campo, se disponível para o visual/versão; usar medida hexadecimal. **Se menor é melhor**, inverter a regra.

### COL-02 — Colunas Atual × Anterior

- Colunas lado a lado para dois períodos comparáveis (ano anterior, orçamento, mês anterior).
- Destaque visual para Atual; Anterior neutro; mostrar delta em tooltip.
- Para YTD, comparar períodos com mesmo número de dias; sinalizar calendário incompleto.

```DAX
Variação % =
VAR Atual = [Valor Realizado]
VAR Base = [Valor Período Comparável]
RETURN IF(NOT ISBLANK(Base) && Base <> 0, DIVIDE(Atual - Base, Base))
```

### COL-03 — Coluna com meta (bullet/target)

- Preferir combo de coluna + linha quando a meta varia por mês.
- Meta fixa pode ser linha de referência, desde que os filtros não a tornem enganosa.
- Tooltip: realizado, meta, gap absoluto, atingimento %, direção desejável.

```DAX
Atingimento Meta % = DIVIDE([Valor Realizado], [Valor Meta])
Gap Meta = [Valor Realizado] - [Valor Meta]
```

### COL-04 — Colunas com seleção Top N + Outros

- Criar parâmetro de N (5, 10, 15) e agrupar o restante em Outros quando a estrutura do modelo permitir.
- **Cuidado:** Top N + Outros não se resolve corretamente só com `RANKX` no filtro do visual; o grupo Outros exige eixo/tabela auxiliar e medida de agregação específica.
- Ordenação decrescente; para muitos nomes, trocar colunas por barras horizontais.

### COL-05 — Colunas com destaque de outliers

- Usar limites estatísticos justificáveis: mediana, IQR ou média ± desvio, quando apropriado.
- Exibir metodologia no tooltip; não confundir ponto extremo com erro.
- Tratar séries sazonais antes de sinalizar anomalias.

### COL-06 — Colunas com variação dinâmica por seletor

- Field Parameters para alternar métrica (receita, margem, quantidade, produtividade).
- Parâmetro desconectado para alternar comparação (vs Meta, vs LY, vs Mês anterior), com medida `SWITCH`.
- Atualizar título, unidade, cor e tooltip ao mudar o seletor.

### COL-07 — Colunas empilhadas e mix

- Absoluto: valores por categoria e composição.
- 100% empilhado: participação; **não** usar para comparar volume absoluto.
- Exibir delta de share em pontos percentuais, não confundir com variação relativa.

### COL-08 — Colunas com marcador de exceção

- Destacar apenas os meses abaixo da meta, perdas relevantes ou desvios fora de tolerância.
- Rótulos apenas nos pontos-chave para reduzir ruído.
- Se visual nativo não oferecer marcador adequado, avaliar Deneb ou sobreposição suportada.

### COL-09 — Colunas com ranking e contribuição

- Pareto: barras por valor decrescente + curva acumulada, preferencialmente Deneb ou combo configurado.
- Linha acumulada deve respeitar filtros e ordenação, com limiar 80% **indicativo**, não lei universal.

### COL-10 — Colunas com múltiplos cenários

- Real, orçamento e forecast claramente diferenciados (cores ou traços).
- Forecast nunca misturado ao realizado sem marcação da data de corte.
- Não sobrecarregar o mesmo gráfico com 5 séries se small multiples forem mais legíveis.

## 4. Biblioteca de linhas e séries temporais

**LIN-01 — Linha premium:** cor principal, linha de meta opcional, rótulo no último ponto e tooltip temporal.

**LIN-02 — Máximo e mínimo:** destacar pontos extremos **do intervalo selecionado**, sem confundir máximo da seleção com máximo global.

**LIN-03 — Linha por status:** segmentos com queda/alta podem ter cor dinâmica em Deneb; em nativo, testar suporte e usar séries auxiliares quando necessário.

**LIN-04 — Queda acima de X%:** parâmetro What-if para tolerância, alertar apenas variações comparáveis e com base válida.

**LIN-05 — Real × Forecast:** divisão clara no cutoff; faixa de confiança apenas quando houver método quantitativo para estimá-la.

**LIN-06 — Sazonalidade:** comparação de meses homólogos, média móvel e índice sazonal com amostra suficiente.

**LIN-07 — Small multiples:** linhas separadas por unidade, produto, loja ou máquina; escalas consistentes quando comparar níveis.

**LIN-08 — Linha com anotações:** marcar evento, mudança de processo ou campanha; não afirmar causalidade só por coincidência temporal.

## 5. Cards premium HTML Content + SVG

### 5.1 Estrutura de card

1. Label claro; 2. Valor com unidade; 3. Delta e comparação; 4. Meta/status; 5. Microtendência quando há histórico válido.

**Exemplo DAX ilustrativo (ajustar nomes de medidas):**

```DAX
Card HTML Valor =
VAR Valor = [Valor Realizado]
VAR Delta = [Variação %]
VAR Cor =
    SWITCH(TRUE(), ISBLANK(Delta), "#64748B", Delta >= 0, "#15803D", "#B91C1C")
VAR ValorTexto = IF(ISBLANK(Valor), "—", FORMAT(Valor, "#,##0"))
VAR DeltaTexto = IF(ISBLANK(Delta), "Sem comparação", FORMAT(Delta, "+0.0%;-0.0%;0.0%"))
RETURN
"<div style='font-family:Segoe UI,Arial,sans-serif;background:#FFFFFF;border:1px solid #E2E8F0;border-radius:14px;padding:16px;box-sizing:border-box'>" &
"<div style='color:#64748B;font-size:12px'>INDICADOR</div>" &
"<div style='color:#172B4D;font-size:28px;font-weight:700;margin-top:8px'>" & ValorTexto & "</div>" &
"<div style='color:" & Cor & ";font-size:12px;margin-top:6px'>" & DeltaTexto & " vs período comparável</div>" &
"</div>"
```

> A cor acima assume **maior = melhor**. Para custo, perdas, inadimplência, atraso etc., calcular status específico. HTML é uma **string DAX renderizada por visual compatível**, não uma definição de visual TMDL.

### 5.2 SVG sparklines

- Gerar `svg` inline com `viewBox`, `polyline`/`path` e pontos discretos.
- Coordenadas devem ser calculadas a partir de uma série de datas ordenada, com escalonamento min–max e proteção para série constante e BLANK.
- **Nunca** usar pontos fixos simulando dados reais. Se não houver histórico, omitir sparkline.
- Respeitar limite de tamanho de texto/medida e capacidade do visual HTML instalado.

### 5.3 Cards de insight

- Cabeçalho: `Atenção`, `Oportunidade` ou `Dentro da meta`.
- Evidência numérica + período + referência.
- Impacto monetário somente se houver medida confiável.
- Próximo passo **como hipótese ou ação de investigação** quando a causa não estiver comprovada.

### 5.4 Relógio, cronômetro e SLA

- Só em contexto operacional (filas, vencimentos, despacho, produção).
- `NOW()` em DAX **não é atualização contínua por segundo**; depende de atualização/consulta do modelo.
- Não prometer relógio em tempo real via JavaScript no HTML Content. Para atualização frequente, estudar arquitetura DirectQuery/Automatic Page Refresh e restrições de licença/capacidade.

## 6. Tabelas e matrizes de alto padrão

- Coluna descritiva à esquerda, cabeçalhos consistentes, numéricos alinhados à direita.
- Data bars dentro de célula para atingimento, participação, gap e estoque.
- Mini gráficos em célula: usar sparkline nativo quando suportado, ou SVG em coluna/medida com categoria de dados adequada, testando compatibilidade.
- Ícones condicionais por status, evitando excesso de emojis.
- Colunas recomendadas: nome, realizado, meta, delta, tendência, status. Evitar repetir todos os KPIs da página.
- Totais e subtotais devem ter lógica explícita: média de percentuais pode estar errada; preferir razão de agregados.
- Drillthrough para detalhe; tooltip com histórico e decomposição.

## 7. Outros visuais modernos reutilizáveis

| Padrão | Melhor uso | Detalhe inteligente |
|---|---|---|
| Bullet chart | Atingimento | faixas e meta por entidade |
| Waterfall | Explicação de variação | contribuição por fator; sem causalidade indevida |
| Heatmap | Padrão por período/local | intensidade e tooltip |
| Pareto | Concentração | % acumulado e limiar |
| Scatter | Segmentação | quadrantes dinâmicos por mediana/meta |
| Gantt | Etapas e prazos | atrasos e dependências reais |
| Timeline de eventos | Paradas e status | duração e criticidade |
| Funnel | Etapas sequenciais | conversão e perdas entre etapas |
| Decomposition Tree | Investigação | explorar dimensões, sem tratar correlação como prova |
| Key Influencers | Exploração | validação estatística e vieses |
| Small multiples | Comparações repetidas | escalas e ordenação consistentes |
| Mapa | Cobertura territorial | granularidade, privacidade e geocodificação |
| Deneb Vega-Lite | visuais customizados | interações e compatibilidade testadas |
| Tooltip page | Contexto sob demanda | histórico, meta, detalhe |
| Field Parameters | Alternar medidas/dimensões | títulos e formatação dinâmicos |
| What-if | Cenários | não alterar fatos históricos |
| Bookmarks + buttons | Filtros ocultos e navegação | persistência de estado e acessibilidade |

## 8. Insights automáticos: método obrigatório

### 8.1 Três camadas

- **Descritivo:** o que mudou? `Produção caiu 8,2% vs mês anterior`.
- **Diagnóstico:** quais componentes explicam matematicamente a mudança? `A unidade B respondeu por 63% da queda agregada` (se a decomposição permitir).
- **Prescritivo:** qual verificação/ação priorizar? `Investigar indisponibilidade na unidade B`; não declarar causa não medida.

### 8.2 Score de prioridade

Criar **somente com regras de negócio acordadas**. Exemplo conceitual: `prioridade = severidade normalizada × exposição financeira × urgência × criticidade`. Normalizar escalas e evitar multiplicação de grandezas sem significado.

### 8.3 Padrão de narrativa

`[STATUS] [MÉTRICA] [VALOR E UNIDADE] [COMPARAÇÃO E PERÍODO]. [FATOR QUANTIFICADO, SE EXISTIR]. [AÇÃO OU INVESTIGAÇÃO].`

- Sem dados suficientes: `Não há histórico comparável para este filtro`.
- Denominador zero: `Variação percentual não aplicável`.
- Sem meta: `Meta não cadastrada para o período`.
- Não repetir parágrafos narrativos longos; preferir alertas concisos e acionáveis.

## 9. DAX analítico reutilizável

### 9.1 Extremos no contexto selecionado

```DAX
Cor Extremo =
VAR ValorAtual = [Valor Realizado]
VAR Maior =
    MAXX(ALLSELECTED('dCalendario'[AnoMes]), CALCULATE([Valor Realizado]))
VAR Menor =
    MINX(ALLSELECTED('dCalendario'[AnoMes]), CALCULATE([Valor Realizado]))
RETURN
    SWITCH(TRUE(), ISBLANK(ValorAtual), "#94A3B8",
        ValorAtual = Maior, "#0F9D92",
        ValorAtual = Menor, "#B91C1C",
        "#94A3B8")
```

> Empates serão destacados. `AnoMes` precisa identificar unicamente mês/ano e estar corretamente ordenado. O significado de máximo/mínimo depende da métrica.

### 9.2 Tendência de janela móvel

```DAX
Média Móvel 3M =
VAR Fim = MAX('dCalendario'[Data])
VAR Periodo = DATESINPERIOD('dCalendario'[Data], Fim, -3, MONTH)
RETURN
    AVERAGEX(
        SUMMARIZE(Periodo, 'dCalendario'[AnoMes]),
        CALCULATE([Valor Realizado])
    )
```

> Ajustar para meses completos, calendário contínuo, granularidade e comportamento desejado para meses sem movimento; validar em contexto mensal antes de usar em produção.

### 9.3 Status semântico

```DAX
Status Meta =
VAR Real = [Valor Realizado]
VAR Meta = [Valor Meta]
VAR Direcao = SELECTEDVALUE('dIndicador'[Direcao], "MaiorMelhor")
RETURN
SWITCH(TRUE(),
    ISBLANK(Real) || ISBLANK(Meta), "Sem dados",
    Direcao = "MenorMelhor" && Real <= Meta, "Dentro da meta",
    Direcao = "MaiorMelhor" && Real >= Meta, "Dentro da meta",
    "Fora da meta"
)
```

> Não utilizar `FORMAT()` para transformar medidas numéricas que precisam continuar numéricas; criar medidas de apresentação separadas ou format strings dinâmicas quando disponíveis.

## 10. Deneb, HTML Content, SVG e visuais nativos: decisão técnica

**Nativo:** preferido para acessibilidade, seleção cruzada, exportação e manutenção.

**Deneb:** para linha multicolorida por segmento, Pareto avançado, bullet sofisticado, faixas, anotações e composição Vega-Lite. Validar bindings de campos, `__selected__`/interações conforme documentação da versão, temas e performance. Não prometer suporte a todo tipo de interação.

**HTML Content:** cards, cabeçalhos, status, painéis de filtro, pequenos SVGs. Validar sanitização, limitações de CSS e restrições do visual escolhido. Não usar JS como requisito.

**SVG:** adequado a indicadores pequenos, barras, símbolos, mini tendências; usar escaping de texto dinâmico e evitar SVG gigantes por linha.

**Visuais customizados:** verificar fonte, certificação, políticas organizacionais, exportação e Service antes de adotá-los.

## 11. Arquitetura PBIP, PBIR, TMDL e tema

```text
Projeto.pbip
├── Projeto.SemanticModel/
│   └── definition/
│       ├── model.tmdl
│       ├── tables/
│       ├── relationships.tmdl
│       └── ...
└── Projeto.Report/
    └── definition/
        ├── report.json
        ├── pages/
        │   └── .../visuals/.../visual.json
        └── ...
```

> Estrutura **ilustrativa**, sujeita à versão do PBIP/PBIR. Inspecionar os arquivos reais; nunca inventar IDs, nomes internos, schemas ou propriedades JSON.

- **TMDL:** tabelas, colunas, medidas, relacionamentos, formatos e metadados do modelo semântico.
- **PBIR:** definição de páginas, posições, visuais, filtros, bookmarks e configurações do relatório.
- **Theme JSON:** tokens e formatação padrão onde suportados; validar esquema de tema da versão.
- **DAX:** métricas e medidas de cor/título/status/HTML; criar display folders (`01 KPIs`, `02 Comparações`, `03 Metas`, `04 Formatação`, `05 HTML`, `06 Insights`).
- **Power Query:** transformar e tipar dados; preservar folding quando relevante.
- **Fonte e segurança:** não expor credenciais, dados pessoais ou segredos no PBIP.

### 11.1 Exemplo mínimo de medida TMDL (ilustrativo)

```tmdl
table 'Medidas'
    measure 'Valor Realizado' = SUM(fFato[Valor])
        formatString: #,0.00
        displayFolder: 01 KPIs
```

> O exemplo pressupõe `fFato[Valor]` existente e sintaxe compatível com o projeto; não criar tabela de medidas isolada sem conferir o esquema e a serialização atuais.

### 11.2 Tema JSON mínimo de referência

```json
{
  "name": "Universal Executive Light",
  "dataColors": ["#1E3A8A", "#0F9D92", "#64748B", "#D97706", "#B91C1C"],
  "background": "#F5F7FA",
  "foreground": "#172B4D",
  "tableAccent": "#0F9D92"
}
```

> Validar a importação no Power BI Desktop e expandir `visualStyles` apenas com propriedades confirmadas.

## 12. Navegação e experiência

- Página inicial opcional com marca, contexto e botão **Iniciar**; fundo pode ser imagem, mas **botão funcional deve ser visual nativo** para navegação real.
- Botões compactos por seção; indicar página atual.
- Painel de filtros oculto via bookmarks ou experiência nativa equivalente; não bloquear interação do canvas.
- Faixa superior dinâmica com filtros ativos; não mostrar filtros que não estão efetivamente aplicados.
- Tooltips informativos com base, comparação, meta e data de atualização.
- Drillthrough com botão de voltar; testar preservação dos filtros.
- Layout 16:9 como padrão, com versão mobile intencional quando exigida.

## 13. Performance, segurança e compatibilidade

1. Modelo estrela com relações adequadas, dimensões conformadas e calendário correto.
2. Evitar `FILTER(ALL(fFato))` em medidas frequentes quando houver alternativa eficiente.
3. Medir tempos com Performance Analyzer e, se disponível, DAX Studio.
4. Controlar cardinalidade de eixos, pontos e SVGs; limitar linhas de tabelas por paginação/filtragem.
5. Evitar dezenas de visuais HTML por página e medidas que concatenem milhares de linhas.
6. Testar Desktop **e** Service, filtros, cross-highlighting, bookmarks, mobile, exportação, RLS e refresh.
7. Não supor que visual HTML terá scripts, eventos ou interatividade customizada.
8. Para dados sensíveis, respeitar RLS/OLS, classificações e políticas de exportação.
9. Documentar recursos Preview como opcionais com fallback estável.

## 14. Matriz de adaptação por setor

| Setor | Colunas inteligentes | Linha/insight | Complemento |
|---|---|---|---|
| Comercial | vendas vs meta por canal | variação e clientes perdidos | ranking + Pareto |
| Financeiro/DRE | receita, custos e lucro | margem e budget adaptativo | waterfall de desvios |
| Indústria | produção vs plano | OEE, perdas e paradas | heatmap + Pareto |
| Logística | entregas vs SLA | OTIF e pedidos vencidos | control tower + aging |
| SaaS | MRR por segmento | churn, NRR e cohort | funil + retenção |
| Varejo | vendas por loja/produto | margem e sazonalidade | mix + ruptura |
| Saúde | atendimentos vs capacidade | espera e SLA | filas + segurança |
| Educação | matrículas vs meta | evasão e inadimplência | cohort + aging |
| RH | vagas e contratações | tempo de preenchimento | funil + segmentação |

**Regra:** KPI só entra se as colunas e definições existirem. Ex.: conversão exige denominador; CAC exige custos de aquisição e novos clientes; OTIF exige prazo e entrega; OEE exige disponibilidade, performance e qualidade com definições verificadas.

## 15. Workflow para Claude/Codex aplicar esta skill

**Etapa A — Inventário**
- Ler arquivos do projeto e dicionário de dados.
- Identificar tabelas, medidas, relacionamentos, páginas, tema, visuais, formatos e limitações de versão.
- Registrar o que existe e o que não é possível calcular.

**Etapa B — Diagnóstico**
- Mapear perguntas executivas por página e identificar gráficos sem contexto.
- Classificar visuais por impacto, custo de implementação e compatibilidade.
- Selecionar somente os padrões que melhoram a tomada de decisão.

**Etapa C — Implementação**
- Criar/ajustar medidas base, comparativas, metas, cores, títulos e tooltips.
- Aplicar tema central e formatação condicional.
- Introduzir HTML/SVG/Deneb apenas onde justificável.
- Preservar filtros, relacionamentos, RLS e navegação.

**Etapa D — Validação**
- Comparar totais antes/depois; conferir visuais com seleções múltiplas, BLANK e períodos incompletos.
- Verificar layout em Desktop/Service, resoluções, exportação e desempenho.
- Registrar limitações e fallback para Preview/custom visuals.

**Etapa E — Entrega**
- Listar arquivos modificados, novas medidas, visuais alterados e validações executadas.
- Declarar explicitamente o que não pôde ser testado; não afirmar sucesso sem execução real.

## 16. Checklist de aceite

- [ ] Nenhum número fictício em visual de produção.
- [ ] Todas as comparações usam períodos equivalentes.
- [ ] Cor respeita direção da métrica.
- [ ] Colunas mostram meta, ranking ou contexto quando relevante.
- [ ] Títulos, unidades e formatos são consistentes.
- [ ] HTML/SVG renderiza sem JS e sem dependência externa.
- [ ] Tabelas têm alinhamento, data bars e totais corretos.
- [ ] Insights distinguem fato, hipótese e recomendação.
- [ ] Filtros ocultos funcionam e filtros ativos são visíveis.
- [ ] PBIR e TMDL não foram confundidos.
- [ ] Preview tem fallback e compatibilidade foi testada.
- [ ] Sem sobrecarga visual; cada componente tem função analítica.
- [ ] Performance e legibilidade validadas.

## 17. Instrução curta para colar em qualquer prompt

> **Aplique integralmente a skill `SKILL_POWER_BI_VISUAIS_INTELIGENTES_UNIVERSAL.md` como biblioteca de padrões, não como lista obrigatória de visuais. Inspecione primeiro os dados e o PBIP existente; selecione gráficos de colunas inteligentes, linhas com destaque, metas, Top N + Outros, HTML/SVG, Deneb, tabelas enriquecidas, filtros ocultos, tooltips e insights somente onde houver justificativa analítica. Priorize tema centralizado, poucos visuais bem distribuídos, cores semânticas e métricas verificáveis. Implemente medidas no modelo TMDL e layout em PBIR, respeitando os schemas reais. Teste Desktop/Service e documente o que foi ou não validado.**

## 18. Material de referência contextual

Esta biblioteca consolida os padrões discutidos anteriormente: cards executivos HTML, sparklines SVG, status SLA, gráficos de colunas condicionais, linhas inteligentes, máximos/mínimos, Top N + Outros, Pareto, budget adaptativo, control tower, Modern Visual Defaults, TMDL/PBIR, tooltips e narrativas de exceção. **Não assume que vídeos e posts externos tenham sido integralmente transcritos ou verificados.**
