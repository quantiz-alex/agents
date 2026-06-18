# KC Pricing System

## Descrição
Sistema proprietário de formação de preços regulares (Sell In) e simulação de impactos em toda a cadeia de valor, parametrizado pelas regras da Reforma Tributária brasileira (transição 2026–2033). Substitui planilhas Excel/Alteryx/KNIME por um motor auditável que permite decisões de preço ágeis sob incerteza tributária, com base na metodologia do Projeto Harmonização. Usuários-alvo: time de Pricing e área fiscal/comercial da empresa.

## Stack Tecnológico
<!-- SEÇÃO FIXA — NÃO ALTERAR. O pipeline não suporta outras tecnologias. -->
- **Frontend**: Dash 2.14+ · Dash Bootstrap Components · Dash AG Grid · Plotly · Pandas/NumPy
- **Backend**: FastAPI · SQLAlchemy · Pydantic v2 · JWT (python-jose + bcrypt)
- **Banco**: SQL Server / Microsoft Fabric (SQLite em dev)
<!-- nota: documento original especifica PostgreSQL — adaptado para SQL Server (stack do pipeline). Lógica de negócio é agnóstica ao banco; sem impacto no motor tributário. -->

---

## Perfis de Acesso
- **admin**: acesso total — gerenciar usuários, configurações, parâmetros tributários e todos os módulos
- **gestor_pricing**: visualizar tudo, simular cenários, aprovar e rejeitar lista de preços e exportar relatórios
- **analista_pricing**: importar bases, parametrizar regras, executar simulações, exportar resultados e enviar para aprovação — não aprova nem exclui

---

## Módulos

### Importação de Bases
**Prioridade**: high
**Tipo de tela**: form
**Ícone Bootstrap**: cloud-upload
**Descrição**: Ingestão manual de arquivos Excel com as bases de dados operacionais — Nielsen (Retail e Scantrack), Preços ERP, P&L SAP Hana, Cadastros Gerais (Produtos, Clientes) e De-Paras. Ponto de entrada de todos os dados que alimentam o motor de pricing.

**Componentes visuais:**
- **KPIs:** Total de registros importados por base, Data da última carga por fonte, Status de validação (OK / Erros) <!-- inferido: revisar -->
- **Grid/Tabela:** Histórico de importações — fonte, nome do arquivo, data/hora, usuário, total de linhas, status
- **Filtros:** fonte (select: Nielsen Retail / Nielsen Scantrack / Preços ERP / P&L / Cadastros / De-Paras), data_importacao (date_range), status (select: Sucesso / Erro / Processando)
- **Formulário de upload:** fonte (select), arquivo Excel (.xlsx/.xls), observacao (text, opcional)

**Funcionalidades:**
- [F-001] Importação de bases via Excel: upload de arquivos para cada fonte de dados, com validação de estrutura de colunas obrigatórias e feedback imediato de erros <!-- RF01 -->
  - Ações: [importar-csv, visualizar]
- [F-002] Histórico e rastreabilidade de cargas: listagem de todas as importações realizadas com metadados da carga <!-- inferido: revisar -->
  - Ações: [visualizar, exportar-excel]

**Regras de negócio:**
- [RN-001]: Cada arquivo importado deve ter estrutura de colunas validada contra o schema esperado para aquela fonte antes de ser persistido
- [RN-002]: Toda importação gera registro auditável com usuário, timestamp e hash do arquivo — rastreabilidade obrigatória
- [RN-003]: Bases Nielsen (Retail e Scantrack), Preços ERP, P&L SAP Hana, Cadastros e De-Paras são as fontes suportadas no MVP; outras fontes são rejeitadas com mensagem explicativa

**Acesso por role:**
- admin: full
- gestor_pricing: [visualizar]
- analista_pricing: [importar-csv, visualizar, exportar-excel]

---

### Parametrização Tributária
**Prioridade**: high
**Tipo de tela**: form
**Ícone Bootstrap**: calculator
**Descrição**: Configuração de todas as variáveis do motor tributário — alíquotas e regimes de transição IBS/CBS (2026–2033), PIS/COFINS, ICMS, Imposto Seletivo — que reprecificam automaticamente todos os cálculos downstream. Base da metodologia de cadeia tributária (PTC Médio / PTC High).

**Componentes visuais:**
- **Grid/Tabela:** Tabela de alíquotas por ano de transição (2026–2033) — ano, IBS %, CBS %, ICMS %, PIS %, COFINS %, Imposto Seletivo %
- **Filtros:** ano_transicao (select), regime (select: Legado / Reforma), canal (select) <!-- inferido: revisar -->
- **Formulário de edição:** aliquota_ibs decimal, aliquota_cbs decimal, aliquota_icms decimal, aliquota_pis decimal, aliquota_cofins decimal, aliquota_is decimal, regime enum(Legado/Reforma), ano_vigencia int

**Funcionalidades:**
- [F-003] Configuração de alíquotas e transição tributária: parametrizar cronograma de transição 2026–2033 com IBS, CBS, ICMS, PIS/COFINS e Imposto Seletivo por ano <!-- RF02 -->
  - Ações: [criar, editar, visualizar]
- [F-004] Configuração de créditos e débitos de PIS/COFINS e ICMS: definição dos créditos apropriáveis e débitos incidentes por regime e canal <!-- RF02 -->
  - Ações: [criar, editar, visualizar]
- [F-005] Reprodução da cadeia tributária PTC Médio / PTC High: cálculo de Sell In NF, Sell In NIV, custo de aquisição e markup de acordo com a metodologia Harmonização <!-- RF07 -->
  - Ações: [visualizar]

**Regras de negócio:**
- [RN-004]: Toda alteração de parâmetro tributário deve propagar recálculo no portfólio ativo imediatamente (performance alvo: segundos)
- [RN-005]: Parâmetros tributários devem ser versionados — nunca sobrescrever histórico; cada conjunto de parâmetros referencia um período de vigência
- [RN-006]: Resultados tributários devem reconciliar com a metodologia Harmonização dentro de tolerância contábil definida

**Acesso por role:**
- admin: full
- gestor_pricing: [visualizar]
- analista_pricing: [criar, editar, visualizar]

---

### Parametrização de Pricing
**Prioridade**: high
**Tipo de tela**: form
**Ícone Bootstrap**: gear
**Descrição**: Configuração da metodologia de pricing — Capitães e Main-Offenders por canal/região, Price Index e Relatividades entre canais, Arquitetura de Produtos (hierarquias de famílias e embalagens) e Margem da Cadeia por família/canal. Inputs estruturantes que definem a régua de preços antes da geração do Sell In.

**Componentes visuais:**
- **Grid/Tabela:** Lista de produtos com classificação por canal/região — produto, família, embalagem, canal, classificação (Capitão / Main-Offender / Seguidor) <!-- inferido: revisar -->
- **Filtros:** canal (select), regiao (select), familia (select), classificacao (select: Capitão / Main-Offender / Seguidor)
- **Formulário:** canal (select), regiao (select), produto_id (select), classificacao (select), price_index decimal, relatividade decimal

**Funcionalidades:**
- [F-006] Definição de Capitães e Main-Offenders: classificar produtos por canal e região como âncoras de preço para aplicação de Price Index <!-- RF03 -->
  - Ações: [criar, editar, excluir, visualizar]
- [F-007] Configuração de Price Index e Relatividades: parametrizar os índices e relatividades de preço entre canais de distribuição <!-- RF03 -->
  - Ações: [criar, editar, visualizar]
- [F-008] Configuração de Arquitetura de Produtos: definir hierarquias de famílias, embalagens e agrupamentos que estruturam o portfólio <!-- RF04 -->
  - Ações: [criar, editar, excluir, visualizar]
- [F-009] Configuração de Margem da Cadeia: parametrizar margens esperadas por família de produto e canal de venda <!-- RF04 -->
  - Ações: [criar, editar, visualizar]

**Regras de negócio:**
- [RN-007]: Cada canal deve ter ao menos um produto classificado como Capitão antes da geração do Sell In <!-- inferido: revisar -->
- [RN-008]: Relatividades entre canais devem respeitar guardrails de consistência da metodologia Harmonização <!-- inferido: revisar -->
- [RN-009]: Alterações na Arquitetura de Produtos geram reprocessamento das margens da cadeia vinculadas

**Acesso por role:**
- admin: full
- gestor_pricing: [visualizar]
- analista_pricing: [criar, editar, excluir, visualizar]

---

### Geração de Lista de Preços Sell In
**Prioridade**: high
**Tipo de tela**: mixed
**Ícone Bootstrap**: tag
**Descrição**: Motor de geração da lista de preços Sell In seguindo a sequência metodológica PTC (Sell Out) → Margem da Cadeia → Sell In, com aplicação de CAPs e guardrails configurados. Exibe a cascata completa de formação de preço por produto e permite download da lista final para aprovação.

**Componentes visuais:**
- **KPIs:** Total de SKUs precificados, % dentro dos CAPs, Variação média de preço vs. base atual, Impacto estimado em Receita NIV <!-- inferido: revisar -->
- **Gráfico principal:** bar — comparativo Preço Atual vs. Preço Gerado por família de produto <!-- inferido: revisar -->
- **Gráfico secundário:** bar — distribuição de variação de preço (%) em faixas (ex: -5% a 0%, 0% a 5%, >5%)
- **Grid/Tabela:** Lista de preços gerada — SKU, produto, família, canal, PTC, Margem Cadeia %, Sell In NF, Sell In NIV, CAP aplicado (S/N), variação vs. base, status_aprovacao
- **Filtros:** familia (select), canal (select), status_cap (select: Dentro / Limitado pelo CAP), variacao_pct (range slider), status_aprovacao (select: Pendente / Aprovada / Rejeitada)

**Funcionalidades:**
- [F-010] Geração da lista de preços Sell In: executar o motor de pricing na sequência PTC → Margem Cadeia → Sell In para o portfólio completo, respeitando CAPs <!-- RF05 -->
  - Ações: [visualizar, exportar-excel, enviar-para-aprovacao]
- [F-011] Visualização da cascata de formação de preço: detalhar passo a passo o cálculo para cada SKU <!-- RF05, RF07 -->
  - Ações: [visualizar, drill-down]
- [F-012] Aprovação de lista de preços: supervisor revisa e aprova ou rejeita a lista enviada pelo analista <!-- inferido: revisar -->
  - Ações: [aprovar, rejeitar]
- [F-013] Auditoria de preço gerado: rastrear quais parâmetros originaram cada preço calculado <!-- inferido: revisar -->
  - Ações: [visualizar]

**Regras de negócio:**
- [RN-010]: A geração do Sell In só pode ser executada se existirem parâmetros tributários válidos, Capitães definidos e Margem da Cadeia configurada
- [RN-011]: Preços que atingem o CAP devem ser sinalizados explicitamente no resultado — nunca silenciosos
- [RN-012]: Todo preço gerado é rastreável até os parâmetros e bases que o originaram (auditabilidade crítica)
- [RN-013]: A sequência de cálculo é obrigatória e não pode ser reordenada: PTC → Margem Cadeia → Sell In
- [RN-014]: Somente supervisor pode aprovar ou rejeitar uma lista de preços

**Acesso por role:**
- admin: full
- gestor_pricing: [visualizar, exportar-excel, aprovar, rejeitar]
- analista_pricing: [visualizar, exportar-excel, enviar-para-aprovacao, drill-down]

---

### Simulação de Impactos
**Prioridade**: high
**Tipo de tela**: mixed
**Ícone Bootstrap**: sliders
**Descrição**: Painel de simulação de cenários de preço — compara impactos em Volume, Receita (NIV) e Margem por elo da cadeia de valor (Indústria → Distribuidor → Varejo) sob os cenários "Mantém Margem" e "Mantém PPC". Permite ajuste interativo de parâmetros e recálculo em tempo real.

**Componentes visuais:**
- **KPIs:** Delta Volume %, Delta Receita NIV (R$), Delta Margem Indústria (R$), Delta Margem Distribuidor (%), Delta Margem Varejo (%) <!-- inferido: revisar -->
- **Gráfico principal:** bar — impacto em Margem por elo da cadeia (Indústria / Distribuidor / Varejo) comparando cenário atual vs. simulado
- **Gráfico secundário:** bar — variação de Volume e Receita NIV por família/canal no cenário simulado
- **Grid/Tabela:** Resultado por SKU — produto, volume_simulado, receita_niv_simulada, margem_industria, margem_distribuidor, margem_varejo, cenario (Mantém Margem / Mantém PPC)
- **Filtros:** cenario (select: Mantém Margem / Mantém PPC), familia (select), canal (select), regiao (select), ano_transicao (select: 2026–2033)

**Funcionalidades:**
- [F-014] Simulação de impactos em Volume, Receita NIV e Margem: executar simulação de novos preços sobre o portfólio e calcular impactos por elo da cadeia <!-- RF06 -->
  - Ações: [visualizar, exportar-excel]
- [F-015] Comparação de cenários Mantém Margem vs. Mantém PPC: executar e exibir lado a lado os dois cenários estratégicos <!-- RF06, RF07 -->
  - Ações: [visualizar, exportar-excel]
- [F-016] Ajuste interativo de parâmetros: modificar alíquotas ou premissas e ver recálculo em tempo real <!-- inferido: revisar -->
  - Ações: [visualizar]

**Regras de negócio:**
- [RN-015]: Recálculo completo de um cenário do portfólio deve concluir em tempo interativo (alvo: segundos, não minutos)
- [RN-016]: O cenário "Mantém PPC" utiliza busca binária para encontrar o Sell In que preserva o preço ao consumidor — lógica do protótipo TaxReformSimulator deve ser reaproveitada
- [RN-017]: Resultados de simulação devem poder ser exportados com todos os parâmetros utilizados anexados (auditabilidade)

**Acesso por role:**
- admin: full
- gestor_pricing: [visualizar, exportar-excel]
- analista_pricing: [visualizar, exportar-excel]

---

### Administração
**Prioridade**: low
**Tipo de tela**: grid
**Ícone Bootstrap**: people
**Descrição**: Controle de usuários do sistema, com gerenciamento de roles e acesso.

**Componentes visuais:**
- **Grid/Tabela:** Lista de usuários — nome, email, role, ativo
- **Filtros:** role (select: admin / supervisor / analista), ativo (select: Sim / Não)
- **Formulário:** nome (text), email (text), role (select), senha temporária (text)

**Funcionalidades:**
- [F-017] Gestão de usuários: criar, editar e desativar usuários com controle de role
  - Ações: [criar, editar, desativar]

**Regras de negócio:**
- [RN-018]: Somente admin pode criar ou desativar usuários
- [RN-019]: Email deve ser único no sistema
- [RN-020]: Dados de P&L e preços são sensíveis — acesso controlado por role, sem exposição de dados comerciais a usuários não autorizados

**Acesso por role:**
- admin: full

---

## Entidades de Dados
<!-- Tipos de campo: varchar(N), nvarchar(N), int, bigint, decimal(P,S), float, date, datetime2, bit, text -->

### ImportacaoBase
**Descrição**: Registro de cada carga de arquivo Excel realizada — histórico de importações com metadados e status para auditoria
**Campos principais**: id bigint PK, fonte enum(NielsenRetail/NielsenScantrack/PrecosERP/PL/Cadastros/DePara), nome_arquivo varchar(255), data_importacao datetime2, usuario_id bigint FK, total_linhas int, status enum(Sucesso/Erro/Processando), hash_arquivo varchar(64), observacao nvarchar(500)
**Relacionamentos**: pertence a Usuarios
**Módulo**: Importação de Bases

### ParametroTributario
**Descrição**: Conjunto de alíquotas e regras do motor tributário por ano de vigência — base de todos os cálculos de cadeia
**Campos principais**: id bigint PK, ano_vigencia int, regime enum(Legado/Reforma), aliquota_ibs decimal(5,4), aliquota_cbs decimal(5,4), aliquota_icms decimal(5,4), aliquota_pis decimal(5,4), aliquota_cofins decimal(5,4), aliquota_is decimal(5,4), credito_pis_cofins decimal(5,4), debito_icms decimal(5,4), ativo bit, criado_em datetime2, usuario_id bigint FK
**Relacionamentos**: pertence a Usuarios; referenciado por CenarioSimulacao
**Módulo**: Parametrização Tributária

### Produto
**Descrição**: Catálogo de produtos (SKUs) com hierarquia de família, embalagem e classificação por canal — base da Arquitetura de Produtos
**Campos principais**: id bigint PK, sku varchar(50) único, descricao nvarchar(200), familia varchar(100), embalagem varchar(100), classificacao enum(Capitão/MainOffender/Seguidor), canal varchar(100), regiao varchar(100), preco_atual decimal(15,4), ativo bit
**Relacionamentos**: tem muitos MargemCadeia; tem muitos ListaPrecoItem
**Módulo**: Parametrização de Pricing

### MargemCadeia
**Descrição**: Margem esperada por família de produto e canal — parâmetro estruturante da metodologia de pricing
**Campos principais**: id bigint PK, familia varchar(100), canal varchar(100), margem_industria decimal(5,4), margem_distribuidor decimal(5,4), margem_varejo decimal(5,4), price_index decimal(10,4), relatividade decimal(10,4), vigencia_inicio date, vigencia_fim date
**Relacionamentos**: referenciado por ListaPrecoItem
**Módulo**: Parametrização de Pricing

### ListaPreco
**Descrição**: Lista de preços Sell In gerada pelo motor de pricing — agrupa os itens de preço de uma execução com status de aprovação
**Campos principais**: id bigint PK, descricao nvarchar(200), data_geracao datetime2, usuario_id bigint FK, parametro_tributario_id bigint FK, status enum(Gerada/PendenteAprovacao/Aprovada/Rejeitada/Arquivada), total_skus int, pct_dentro_cap decimal(5,2), aprovado_por bigint FK, data_aprovacao datetime2
**Relacionamentos**: pertence a Usuarios; pertence a ParametroTributario; tem muitos ListaPrecoItem
**Módulo**: Geração de Lista de Preços Sell In

### ListaPrecoItem
**Descrição**: Linha de preço calculada para um SKU em uma lista — inclui toda a cascata de formação de preço para auditabilidade
**Campos principais**: id bigint PK, lista_preco_id bigint FK, produto_id bigint FK, ptc_sell_out decimal(15,4), margem_cadeia_pct decimal(5,4), sell_in_nf decimal(15,4), sell_in_niv decimal(15,4), custo_aquisicao decimal(15,4), markup decimal(5,4), cap_aplicado bit, variacao_pct decimal(8,4)
**Relacionamentos**: pertence a ListaPreco; pertence a Produto
**Módulo**: Geração de Lista de Preços Sell In

### CenarioSimulacao
**Descrição**: Cenário de simulação de impactos — agrega os resultados de Volume, Receita NIV e Margem por elo da cadeia
**Campos principais**: id bigint PK, descricao nvarchar(200), tipo_cenario enum(MantemMargem/MantemPPC), lista_preco_id bigint FK, parametro_tributario_id bigint FK, data_simulacao datetime2, usuario_id bigint FK, delta_volume_pct decimal(8,4), delta_receita_niv decimal(15,2), delta_margem_industria decimal(15,2)
**Relacionamentos**: pertence a ListaPreco; pertence a ParametroTributario; pertence a Usuarios; tem muitos CenarioSimulacaoItem
**Módulo**: Simulação de Impactos

### CenarioSimulacaoItem
**Descrição**: Resultado de simulação por SKU — Volume, Receita NIV e Margem por elo da cadeia para cada produto do cenário
**Campos principais**: id bigint PK, cenario_id bigint FK, produto_id bigint FK, volume_simulado decimal(15,2), receita_niv_simulada decimal(15,4), margem_industria decimal(15,4), margem_distribuidor decimal(15,4), margem_varejo decimal(15,4)
**Relacionamentos**: pertence a CenarioSimulacao; pertence a Produto
**Módulo**: Simulação de Impactos

### Usuarios
**Descrição**: Usuários do sistema com autenticação JWT
**Campos principais**: nome varchar(100), email varchar(150) único, senha_hash varchar(255), role enum(admin/supervisor/analista), ativo bit
**Relacionamentos**: —
**Módulo**: Administração

---

## Branding
- **Cor primária**: TODO: #3b82f6
- **Logo**: TODO: (caminho relativo ex: assets/logo_kc.png)
- **Nome na sidebar**: KC Pricing

---

## Integrações
<!-- MVP usa carga manual via Excel para todas as fontes — integrações automáticas são escopo v1 -->
- **Nielsen Retail / Nielsen Scantrack**: Arquivo Excel (upload manual) — base de preços de mercado e scantrack para cálculo de PTC e Price Index
- **Preços ERP**: Arquivo Excel (upload manual) — lista de preços atuais praticados pela empresa
- **P&L SAP Hana**: Arquivo Excel (upload manual) — dados de custos e margem por produto para cálculo de Margem da Cadeia
- **Cadastros Gerais / De-Paras**: Arquivo Excel (upload manual) — hierarquias de produtos, clientes e mapeamentos de canais/regiões

---

## Requisitos Não-Funcionais
- **Auditabilidade**: Todo preço gerado deve ser rastreável até os parâmetros tributários, de pricing e bases de dados que o originaram — requisito crítico para área fiscal e comercial
- **Precisão e Reconciliação**: Resultados devem conferir com a metodologia Harmonização dentro de tolerância contábil definida; reconciliação obrigatória nos testes de aceitação
- **Performance**: Recálculo completo de um cenário do portfólio em tempo interativo (alvo: segundos, não minutos)
- **Segurança**: JWT com expiração de 8h, senhas com bcrypt, HTTPS em produção; dados de P&L e preços são sensíveis — sem exposição a roles não autorizados
- **Usabilidade**: Parametrização sem necessidade de código, operável pelo time de Pricing sem suporte técnico

---

## Escopo Futuro (fora do MVP)

### v1 — Sprint 2: Automação, Promoção e Analytics

**Ingestão e Tratamento de Dados (datalake)**
- Construção de datalake com integração plena e automatizada com ERP/SAP/Nielsen — elimina carga manual de Excel
- Orquestração de pipelines, governança de dados e observabilidade

**Módulo Promoção**
- Mecânica de recomendação de PTC Low: cobertura, profundidade e TP
- Cálculo de ROI de promoções (Retorno vs TP)

**Suite de Análises de Preços**
- NRR Tracking: Realizado vs Referência/Target
- Evolutivo de PTC e Sell In ao longo do tempo
- Aderência Sell Out: comparativo do que foi praticado vs. recomendado
- Evolutivo de Market Share por canal/região
- Evolutivo TA/TP e Pricing Index Tracking

**Melhorias Não-Funcionais**
- SLA de disponibilidade definido e monitorado
- RBAC avançado (versionamento de cenários e aprovação formal)
