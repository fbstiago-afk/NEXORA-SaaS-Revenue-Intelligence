# NEXORA — SaaS Revenue Intelligence (Power BI PBIP)

## Estrutura
```
NEXORA/
├── Nexora.pbip                  ← abra este arquivo
├── Nexora.Report/               ← relatório PBIR (páginas, visuais, bookmarks, tema, imagens)
├── Nexora.SemanticModel/        ← modelo TMDL (tabelas, relações, 150 medidas)
├── Data/                        ← 23 CSVs da base sintética
├── Assets/                      ← backgrounds 1920×1080, logo negativo
├── Theme/NEXORA_Dark.json       ← tema central
├── Deneb/                       ← specs Vega-Lite reutilizáveis
├── Scripts/                     ← geração da base, assets, PBIP e docs (Python)
├── Documentation/               ← esta documentação
└── Validation/                  ← validação da base e do Power BI
```

## Como abrir
1. Abra `Nexora.pbip` no Power BI Desktop (versão de 2026 com PBIR habilitado — projeto salvo na versão instalada).
2. Se a pasta for movida: *Transformar dados → Editar parâmetros → `PastaDados`* (terminar com `\`) e **Atualizar**.
3. Visuais personalizados: **HTML Content** e **Deneb** (AppSource, certificados). São baixados automaticamente ao abrir com internet; se não, *Obter mais visuais* → pesquisar e adicionar.
4. No modo de edição, use **Ctrl + clique** nos botões (no Serviço/leitura, clique simples).

## Páginas
Início · Executive SaaS · Revenue Intelligence · Customer & Retention · Growth & Unit Economics · 3 páginas de tooltip ocultas.

## Regenerar tudo
```
python Scripts/gerar_base_nexora.py Data
python Scripts/validar_base_nexora.py Data Validation/VALIDACAO_BASE_NEXORA.md
python Scripts/gerar_assets.py <pasta_imagens_marca> Assets
python Scripts/build_pbip.py <saida>/NEXORA Assets "<caminho Windows>\Data\"
```
