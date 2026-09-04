# Pricing Lab — Gestão e Simulação de Preços

<!-- EXEMPLO COMPLETO de roadmap preenchido. Use como referência de "nível de detalhe ideal".
     Serve também como fixture de validação do pipeline (deve passar no Step 0 sem avisos). -->

## Descrição
Plataforma de pricing para uma distribuidora de autopeças com ~1.200 SKUs e 35 fornecedores. Centraliza a tabela de preços vigente, permite simular reajustes de markup por família/canal com projeção de impacto (via elasticidade), e organiza um fluxo de aprovação para publicar novas listas de preço.
Resolve a falta de visibilidade sobre margem por família e o retrabalho de planilhas na negociação de reajustes.
Usuários: analistas de pricing (simulam e propõem), gerentes comerciais (aprovam) e o administrador do sistema.

## Stack Tecnológico
<!-- SEÇÃO FIXA — NÃO ALTERAR. O pipeline não suporta outras tecnologias. -->
- **Frontend**: Dash 2.14+ · Dash Bootstrap Components · Dash AG Grid · Plotly · Pandas/NumPy
- **Backend**: FastAPI · SQLAlchemy · Pydantic v2 · JWT (python-jose + bcrypt)
- **Banco**: SQL Server / Microsoft Fabric (SQLite em dev)

---

## Contexto de Demonstração
- **Persona da demo**: Diretora Comercial que precisa decidir o reajuste do trimestre e quer ver impacto antes de aprovar
- **Cenário narrativo**: A analista abre a Análise de Vendas, identifica que a família "Baterias" perdeu 2 p.p. de margem no último trimestre; vai à Simulação, aplica +4% de markup em Baterias no canal Loja e vê +R$ 310 mil de margem projetada com queda de 1,8% em volume; salva o cenário "Baterias Q4" e envia para aprovação. A diretora abre a Fila, vê o detalhe com o waterfall, aprova com comentário, e o Dashboard passa a refletir o cenário aprovado.
- **Números-âncora**: receita anual ≈ R$ 48M; 1.200 SKUs em 8 famílias; 35 fornecedores; 4 regiões (Sul, Sudeste, Nordeste, Centro-Oeste); ticket médio ≈ R$ 420; margem média ≈ 28%
- **Período dos dados**: últimos 24 meses até o mês atual
- **Locale**: pt-BR · moeda R$ · datas dd/mm/aaaa
- **Credenciais de demo**: admin@pricinglab.com · gerente@pricinglab.com · analista@pricinglab.com

---

## Perfis de Acesso
- **admin**: acesso total — gerencia usuários, cadastros, parâmetros e todos os módulos
- **gerente**: visualiza tudo, simula, aprova e rejeita cenários enviados pelos analistas
- **analista**: analisa vendas, simula cenários, salva e envia para aprovação — não aprova nem publica

---

## Módulos

### Dashboard Executivo
**Prioridade**: high
**Tipo de tela**: dashboard
**Grupo de menu**: Visão Geral
**Ícone Bootstrap**: speedometer2
**Objetivo do usuário**: "Como gerente, quero ver em 10 segundos receita, margem e o impacto do cenário aprovado para decidir onde agir"
**Descrição**: Visão executiva do mês corrente comparada ao mês anterior e ao cenário de preços aprovado mais recente.
**Layout**: kpis:4 | charts:2col | grid
**Participa de workflow**: Workflow Principal (step final: reflete os preços publicados após aprovação)

**Componentes visuais:**
- **KPIs:** Receita do mês (comparação vs mês anterior, currency, melhor=sobe); Margem % (comparação vs mês anterior, percent, melhor=sobe); Volume (comparação vs mês anterior, number, melhor=sobe); Cenários pendentes (simples, number)
- **Gráfico principal:** combo — Receita e volume por mês (últimos 12 meses) — x: mes, barras: volume, linha: receita
- **Gráfico secundário:** bar — Top 10 famílias por margem (R$) — x: margem, y: familia (horizontal)
- **Grid/Tabela:** vendas agregadas por família — familia, receita (currency), margem (currency), margem_pct (percent, cor semântica), volume (number), variacao_receita_pct (percent, cor semântica)
- **Filtros:** periodo (date_range, padrão: mês atual), regiao (select), canal (select)
- **Drill-down:** gráfico secundário → clique na barra filtra o grid por família
- **Ordenação padrão:** receita desc
- **Estado vazio:** "Nenhuma venda no período selecionado. Amplie o intervalo de datas."

**Funcionalidades:**
- [F-001] Visão consolidada do mês com comparação ao mês anterior
  - Ações disponíveis: [visualizar, exportar-excel]
- [F-002] Ranking de famílias por margem com drill-down para o grid
  - Ações disponíveis: [visualizar, drill-down]

**Regras de negócio:**
- [RN-001]: Margem % = (receita − custo_total) / receita × 100, calculada sobre o período filtrado
  - Tipo: campo_derivado
  - Fórmula/condição: margem_pct = (receita - custo_total) / receita * 100
  - Variáveis de entrada: receita (currency, campo), custo_total (currency, campo)
  - Campos de saída: margem_pct (percent)

**Acesso por role:**
- admin: full
- gerente: [visualizar, exportar-excel]
- analista: [visualizar, exportar-excel]

---

### Análise de Vendas
**Prioridade**: high
**Tipo de tela**: analytics
**Grupo de menu**: Visão Geral
**Ícone Bootstrap**: bar-chart-line
**Objetivo do usuário**: "Como analista, quero cruzar receita e margem por família, canal, região e fornecedor para encontrar onde reajustar"
**Descrição**: Painel analítico do histórico de vendas com múltiplas dimensões e drill-down para o detalhe.
**Layout**: kpis:4 | charts:2col | charts:3col | grid

**Componentes visuais:**
- **Filtros globais:** periodo (date_range, padrão: últimos 12 meses), agrupamento (select: mensal/trimestral, padrão mensal), familia (select), regiao (select), top_n (select: 5/10/20, padrão 10)
- **KPIs:** Receita total (comparação vs período anterior, currency, melhor=sobe); Margem total (comparação, currency, melhor=sobe); Markup médio ponderado (comparação, percent, melhor=sobe); Ticket médio (comparação, currency, melhor=sobe)
- **Gráficos:**
  - line — Evolução da receita e da margem % — x: periodo, y: receita, série secundária: margem_pct
  - heatmap — Receita por família × canal — x: canal, y: familia, valor: receita
  - treemap — Participação na receita — hierarquia: familia > fornecedor, valor: receita
  - bar — Top N fornecedores por receita — x: receita, y: fornecedor (horizontal)
  - bar — Receita por região — x: regiao, y: receita
- **Grid/Tabela exportável:** detalhamento — familia, fornecedor, canal, regiao, receita (currency), custo_total (currency), margem_pct (percent, cor semântica), volume (number)
- **Drill-down:** heatmap → clique na célula filtra o grid por família e canal; treemap → clique filtra por fornecedor
- **Estado vazio:** "Sem vendas para os filtros escolhidos."

**Funcionalidades:**
- [F-010] Análise temporal de receita e margem com agrupamento mensal/trimestral
  - Ações: [visualizar, exportar-excel]
- [F-011] Análise multidimensional (família × canal × região × fornecedor) com drill-down
  - Ações: [visualizar, drill-down, exportar-excel]

**Regras de negócio:**
- [RN-010]: Período anterior = mesmo intervalo imediatamente antes do período atual
- [RN-011]: Markup médio ponderado por volume: markup_medio = Σ(markup × quantidade) / Σ(quantidade)
  - Tipo: campo_derivado
  - Fórmula/condição: markup_medio = sum(markup * quantidade) / sum(quantidade)
  - Variáveis de entrada: markup (percent, campo), quantidade (number, campo)
  - Campos de saída: markup_medio (percent)

**Acesso por role:**
- admin: full
- gerente: [visualizar, exportar-excel]
- analista: [visualizar, exportar-excel]

---

### Tabela de Preços
**Prioridade**: high
**Tipo de tela**: master_detail
**Grupo de menu**: Pricing
**Ícone Bootstrap**: tag
**Objetivo do usuário**: "Como analista, quero consultar e ajustar o preço vigente de cada SKU vendo custo, markup e histórico"
**Descrição**: Lista de preços vigente por produto com ficha de detalhe.
**Layout**: kpis:3 | grid | detail

**Componentes visuais:**
- **KPIs:** SKUs ativos (simples, number); Preço médio (comparação vs lista anterior, currency, melhor=neutro); Markup médio (simples, percent)
- **Grid/Tabela:** produto — codigo, nome, familia, fornecedor, custo (currency), preco_atual (currency), markup_pct (percent), status (badge), vigencia_inicio (date)
- **Ações por linha:** [detalhar, editar, desativar]
- **Painel de detalhe:** ficha do produto (nome, família, fornecedor, custo, preço, markup) + sparkline do preço nos últimos 12 meses + últimas 10 vendas do produto
- **Filtros:** familia (select), fornecedor (select), status (select: Ativo/Inativo), busca (text: código ou nome)
- **Formulário de criação/edição (modal):** nome (text), familia (select), fornecedor_id (select), custo (decimal), preco_atual (decimal), elasticidade (decimal), status (select)
- **Ordenação padrão:** nome asc
- **Estado vazio:** "Nenhum produto encontrado. Ajuste os filtros ou cadastre um novo produto."

**Funcionalidades:**
- [F-020] Consultar e filtrar a tabela de preços vigente
  - Ações: [visualizar, exportar-excel, detalhar]
- [F-021] Manter produtos (criar, editar, desativar)
  - Ações: [criar, editar, desativar]

**Regras de negócio:**
- [RN-020]: Preço não pode ser menor que custo × (1 + markup mínimo de 15%)
  - Tipo: validação
  - Fórmula/condição: preco_atual >= custo * (1 + 0.15)
  - Variáveis de entrada: custo (currency, campo), preco_atual (currency, campo)
  - Campos de saída: —
- [RN-021]: Markup % = (preco_atual / custo − 1) × 100
  - Tipo: campo_derivado
  - Fórmula/condição: markup_pct = (preco_atual / custo - 1) * 100
  - Variáveis de entrada: preco_atual (currency, campo), custo (currency, campo)
  - Campos de saída: markup_pct (percent)

**Acesso por role:**
- admin: full
- gerente: [visualizar, exportar-excel, detalhar]
- analista: [visualizar, criar, editar, exportar-excel, detalhar]

---

### Simulação de Reajuste
**Prioridade**: high
**Tipo de tela**: simulation
**Grupo de menu**: Pricing
**Ícone Bootstrap**: calculator
**Objetivo do usuário**: "Como analista, quero ajustar o markup por família e canal e ver o impacto em receita, volume e margem antes de enviar para aprovação"
**Descrição**: Simulador de reajuste de markup com projeção de volume via elasticidade e ponte de impacto.
**Layout**: params | kpis:4 | split:7/5 | grid
**Participa de workflow**: Workflow Principal (step: simulação → aprovação)
**Recálculo**: ao vivo

**Parâmetros de entrada:**
- ajuste_markup (number, %, faixa -20–40, padrão 0) — variação percentual aplicada ao markup atual
- familia (select, opcional) — restringe o reajuste a uma família
- canal (select, opcional) — restringe a um canal
- desconto_maximo (number, %, faixa 0–30, padrão 10) — teto de desconto permitido após o reajuste

**Resultado calculado:**
- **KPIs:** Receita atual × simulada (comparação, currency, melhor=sobe); Margem atual × simulada (comparação, currency, melhor=sobe); Volume atual × estimado (comparação, number, melhor=sobe); Itens afetados (simples, number)
- **Gráfico principal:** waterfall — Receita atual → efeito preço → efeito volume → Receita simulada
- **Gráfico secundário:** elasticity_curve — sensibilidade preço × volume da família selecionada
- **Tabela comparativa:** produto, familia, preco_atual (currency), preco_simulado (currency), variacao_pct (percent, cor semântica), volume_estimado (number), margem_simulada (currency)
- **Drill-down:** gráfico principal → clique em "efeito preço" ordena a tabela por variacao_pct desc
- **Estado vazio:** "Ajuste os parâmetros para ver o impacto do cenário."

**Funcionalidades:**
- [F-SIM-001] Simular cenário ao vivo: mover sliders → resultado recalcula
  - Ações: [simulate]
- [F-SIM-002] Salvar cenário nomeado
  - Ações: [criar]
- [F-SIM-003] Enviar cenário salvo para aprovação
  - Ações: [submit_approval]

**Regras de negócio:**
- [RN-SIM-001]: Preço simulado aplica o ajuste de markup sobre o custo; volume estimado reage pela elasticidade do produto
  - Tipo: fórmula_interativa
  - Fórmula/condição: preco_simulado = custo * (1 + (markup_pct/100) * (1 + ajuste_markup/100)); volume_estimado = volume * (1 + elasticidade * (preco_simulado/preco_atual - 1)); receita_simulada = preco_simulado * volume_estimado; margem_simulada = (preco_simulado - custo) * volume_estimado
  - Variáveis de entrada: ajuste_markup (number, %, faixa -20–40, padrão 0, interativo); custo (currency, campo); markup_pct (percent, campo derivado RN-021); volume (number, campo); elasticidade (number, campo); preco_atual (currency, campo)
  - Campos de saída: preco_simulado (currency), volume_estimado (number), receita_simulada (currency), margem_simulada (currency)
- [RN-SIM-002]: Desconto máximo não pode exceder 30%
  - Tipo: validação
  - Fórmula/condição: desconto_maximo <= 30
- [RN-SIM-003]: Cálculo nunca persiste automaticamente — o analista escolhe explicitamente salvar
  - Tipo: regra_workflow

**Acesso por role:**
- admin: full
- gerente: [simulate, visualizar, exportar-excel]
- analista: [simulate, criar, submit_approval, exportar-excel]

---

### Fila de Aprovações
**Prioridade**: high
**Tipo de tela**: approval_queue
**Grupo de menu**: Pricing
**Ícone Bootstrap**: check2-circle
**Objetivo do usuário**: "Como gerente, quero avaliar os cenários pendentes com o impacto na tela e aprovar/rejeitar com justificativa"
**Descrição**: Fila de cenários enviados pelos analistas aguardando decisão.
**Layout**: kpis:4 | grid | detail
**Participa de workflow**: Workflow Principal (step: aprovação → dashboard)
**Badge na sidebar**: contagem de cenários com status "Pendente Aprovação"

**Componentes visuais:**
- **KPIs:** Pendentes (simples, number); Aprovados no mês (simples, number); Rejeitados no mês (simples, number); Tempo médio de aprovação em dias (simples, number)
- **Grid/Tabela:** cenario — nome, criado_por, criado_em (date), variacao_pct (percent, cor semântica), receita_simulada (currency), status (badge)
- **Ações por linha:** [detalhar, approve, reject]
- **Painel de detalhe:** parâmetros do cenário, KPIs de impacto, waterfall, comentários
- **Filtros:** status (select: Pendente Aprovação/Aprovado/Rejeitado, padrão Pendente Aprovação), criado_por (select), periodo (date_range)
- **Ordenação padrão:** criado_em asc
- **Estado vazio:** "Nenhuma pendência. Tudo em dia!"

**Funcionalidades:**
- [F-APR-001] Aprovar cenário com comentário opcional
  - Ações: [approve]
- [F-APR-002] Rejeitar cenário com comentário obrigatório
  - Ações: [reject]
- [F-APR-003] Consultar histórico de decisões
  - Ações: [visualizar, exportar-excel]

**Regras de negócio:**
- [RN-APR-001]: Somente gerente e admin podem aprovar ou rejeitar (Tipo: regra_workflow)
- [RN-APR-002]: Rejeição exige comentário (Tipo: validação)
- [RN-APR-003]: Analista não pode aprovar os próprios envios (Tipo: regra_workflow)
- [RN-APR-004]: Cenários com variação de receita > 15% exigem justificativa na aprovação (Tipo: validação)

**Acesso por role:**
- admin: full
- gerente: [approve, reject, visualizar, exportar-excel, detalhar]
- analista: [visualizar, detalhar]

---

### Administração
**Prioridade**: low
**Tipo de tela**: grid
**Grupo de menu**: Administração
**Ícone Bootstrap**: people
**Objetivo do usuário**: "Como admin, quero manter os usuários e seus perfis de acesso"
**Descrição**: Controle de usuários do sistema.
**Layout**: grid

**Componentes visuais:**
- **Grid/Tabela:** usuarios — nome, email, role (badge), ativo (badge), ultimo_acesso (date)
- **Ações por linha:** [editar, desativar]
- **Filtros:** role (select), ativo (select: Sim/Não)
- **Formulário:** nome (text), email (text), role (select), senha temporária (text)
- **Estado vazio:** "Nenhum usuário encontrado."

**Funcionalidades:**
- [F-ADM-001] Gestão de usuários: criar, editar e desativar
  - Ações: [criar, editar, desativar]

**Regras de negócio:**
- [RN-ADM-001]: Somente admin pode criar ou desativar usuários (Tipo: regra_workflow)
- [RN-ADM-002]: Email deve ser único (Tipo: validação)

**Acesso por role:**
- admin: full

---

## Workflows e Jornadas de Usuário

### Workflow Principal: Reajuste de Preços
**Categoria**: inovação
**Descrição**: Da análise do histórico à publicação de um novo cenário de preços aprovado.
**Roles**: [analista, gerente, admin]

**Steps:**
1. **Análise de Vendas** → analista identifica família/canal com margem em queda
   - Dados fornecidos: familia, canal, periodo
   - Próximo passo: Simulação de Reajuste
2. **Simulação de Reajuste** → analista ajusta markup, salva e envia o cenário
   - Dados recebidos: familia, canal
   - Dados fornecidos: cenario_id
   - Próximo passo: Fila de Aprovações (condição: após enviar para aprovação)
3. **Fila de Aprovações** → gerente aprova ou rejeita
   - Dados recebidos: cenario_id
   - Próximo passo: Dashboard Executivo (condição: status = Aprovado)
4. **Dashboard Executivo** → reflete o cenário aprovado
   - Dados recebidos: cenario_id
   - Ações finais: visualizar impacto, iniciar nova simulação

---

## Entidades de Dados

### Fornecedor
**Descrição**: Fornecedores de autopeças
**Papel**: dimensao
**Campos principais**: nome varchar(120), cnpj varchar(18), regiao enum(Sul/Sudeste/Nordeste/Centro-Oeste), ativo bit
**Relacionamentos**: tem muitos Produto
**Módulo**: Tabela de Preços
**Volumetria de demo**: 35 registros
**Distribuições**: nome: lista(BR:empresas); regiao: enum(Sudeste:45%, Sul:25%, Nordeste:20%, Centro-Oeste:10%); ativo: enum(1:94%, 0:6%)
**Exemplo de linha**: "Autopeças Horizonte Ltda" · 12.345.678/0001-90 · Sudeste · 1

### Produto
**Descrição**: SKUs comercializados com preço vigente e parâmetros de simulação
**Papel**: dimensao
**Campos principais**: codigo varchar(20) único, nome varchar(150), familia enum(Baterias/Filtros/Freios/Suspensão/Iluminação/Lubrificantes/Elétrica/Acessórios), fornecedor_id int FK, custo decimal(15,2), preco_atual decimal(15,2), volume int, elasticidade decimal(6,3), status enum(Ativo/Inativo), vigencia_inicio date
**Relacionamentos**: pertence a Fornecedor, tem muitos Venda
**Módulo**: Tabela de Preços + Simulação de Reajuste
**Volumetria de demo**: 1.200 registros
**Distribuições**: nome: lista(BR:produtos_autopecas); familia: enum(Baterias:18%, Filtros:16%, Freios:15%, Suspensão:12%, Iluminação:11%, Lubrificantes:10%, Elétrica:10%, Acessórios:8%); custo: pareto; preco_atual: derivado(custo * 1.38); volume: pareto; elasticidade: normal(-1.2, 0.4); status: enum(Ativo:93%, Inativo:7%)
**Exemplo de linha**: "BAT-0601" · "Bateria 60Ah Heavy Duty" · Baterias · 12 · 289,90 · 399,90 · 340 · -1,35 · Ativo · 2025-03-01

### Cliente
**Descrição**: Clientes B2B (oficinas, lojas e frotas)
**Papel**: dimensao
**Campos principais**: nome varchar(120), tipo enum(Oficina/Loja/Frota), cidade varchar(80), uf varchar(2), regiao enum(Sul/Sudeste/Nordeste/Centro-Oeste), ativo bit
**Relacionamentos**: tem muitos Venda
**Módulo**: Análise de Vendas
**Volumetria de demo**: 400 registros
**Distribuições**: nome: lista(BR:empresas); tipo: enum(Oficina:55%, Loja:30%, Frota:15%); cidade/uf: lista(BR:cidades); regiao: enum(Sudeste:45%, Sul:25%, Nordeste:20%, Centro-Oeste:10%)

### Venda
**Descrição**: Fato de vendas (uma linha por item vendido)
**Papel**: fato
**Campos principais**: data date, produto_id int FK, cliente_id int FK, canal enum(Loja/E-commerce/Atacado), quantidade int, preco_unitario decimal(15,2), custo_unitario decimal(15,2), receita decimal(15,2), custo_total decimal(15,2), markup decimal(8,4)
**Relacionamentos**: pertence a Produto, pertence a Cliente
**Módulo**: Dashboard Executivo + Análise de Vendas
**Volumetria de demo**: 6.000 registros
**Distribuições**: data: sazonal(mensal, pico: nov,dez) + tendencia(+8% ao ano); canal: enum(Loja:55%, E-commerce:30%, Atacado:15%); quantidade: normal(6, 3); preco_unitario: derivado(produto.preco_atual * normal(1, 0.04)); custo_unitario: derivado(produto.custo); receita: derivado(quantidade * preco_unitario); custo_total: derivado(quantidade * custo_unitario); markup: derivado((preco_unitario / custo_unitario - 1) * 100)
**Exemplo de linha**: 2025-11-14 · 87 · 231 · Loja · 4 · 402,50 · 289,90 · 1.610,00 · 1.159,60 · 38,84

### CenarioSimulacao
**Descrição**: Cenários de reajuste salvos pelos analistas
**Papel**: fato
**Campos principais**: nome varchar(200), parametros text, receita_atual decimal(15,2), receita_simulada decimal(15,2), margem_atual decimal(15,2), margem_simulada decimal(15,2), variacao_pct decimal(8,4), status enum(Rascunho/Pendente Aprovação/Aprovado/Rejeitado) default Rascunho, criado_por varchar(100), criado_em datetime2, aprovado_por varchar(100) nullable, aprovado_em datetime2 nullable, comentario_aprovacao text nullable
**Relacionamentos**: pertence a Usuarios (criado_por)
**Módulo**: Simulação de Reajuste + Fila de Aprovações
**Volumetria de demo**: 30 registros
**Distribuições**: status: enum(Rascunho:20%, Pendente Aprovação:30%, Aprovado:40%, Rejeitado:10%); variacao_pct: normal(2.5, 4); criado_em: faixa(últimos 6 meses)

### Usuarios
**Descrição**: Usuários do sistema com autenticação JWT
**Papel**: apoio
**Campos principais**: nome varchar(100), email varchar(150) único, senha_hash varchar(255), role enum(admin/gerente/analista), ativo bit, ultimo_acesso datetime2 nullable
**Relacionamentos**: —
**Módulo**: Administração
**Volumetria de demo**: 12 registros (inclui admin@pricinglab.com, gerente@pricinglab.com, analista@pricinglab.com)

---

## Branding
- **Cor primária**: #0F766E
- **Cor secundária**: #F59E0B
- **Logo**: 
- **Logo para fundo escuro**: 
- **Favicon**: 
- **Nome na sidebar**: Pricing Lab
- **Tagline**: Decisões de preço com confiança
- **Fonte**: system

---

## Requisitos Não-Funcionais
- **Performance**: Consultas < 3s com 6.000 vendas; simulação ao vivo < 500ms
- **Segurança**: JWT com expiração de 8h, senhas com bcrypt, HTTPS em produção
- **Escalabilidade**: Suporte a 30 usuários simultâneos
- **Disponibilidade**: horário comercial 8h–20h
