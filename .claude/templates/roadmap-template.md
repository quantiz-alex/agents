# {NOME_DO_PROJETO}

## Descrição
TODO: O que este sistema faz em 2–3 frases.
TODO: Qual problema ele resolve?
TODO: Quem são os usuários? (ex: analistas de pricing, gestores comerciais, compradores)

## Stack Tecnológico
<!-- SEÇÃO FIXA — NÃO ALTERAR. O pipeline não suporta outras tecnologias. -->
- **Frontend**: Dash 2.14+ · Dash Bootstrap Components · Dash AG Grid · Plotly · Pandas/NumPy
- **Backend**: FastAPI · SQLAlchemy · Pydantic v2 · JWT (python-jose + bcrypt)
- **Banco**: SQL Server / Microsoft Fabric (SQLite em dev)

---

## Contexto de Demonstração
<!-- NOVO — o que faz o cliente dizer "quero comprar". Guia o mock data, a Home e o ui-reviewer.
     Tudo aqui é opcional, mas quanto mais preenchido, mais realista a demo. -->
- **Persona da demo**: TODO — quem vai ver a demo e o que essa pessoa precisa decidir (ex: Diretor Comercial que precisa aprovar reajuste trimestral)
- **Cenário narrativo**: TODO — 2–3 frases contando a história que a demo percorre (ex: "Analista simula +3% de markup na família X, vê impacto de R$ 1,2M na margem, envia para aprovação; o diretor aprova pela fila e o dashboard reflete")
- **Números-âncora**: TODO — grandezas que os dados devem respeitar para parecerem reais (ex: receita anual ≈ R$ 48M; 1.200 SKUs; 35 fornecedores; 4 regiões; ticket médio ≈ R$ 380)
- **Período dos dados**: TODO — ex: últimos 24 meses até o mês atual (o mock gera datas relativas a hoje)
- **Locale**: pt-BR · moeda R$ · datas dd/mm/aaaa
- **Credenciais de demo**: uma por role (o login exibe chips clicáveis) — ex: admin@empresa.com · supervisor@empresa.com · analista@empresa.com

---

## Perfis de Acesso
<!-- Roles padrão do pipeline — ajustar nomes/permissões conforme o cliente -->
- **admin**: acesso total — gerenciar usuários, configurações e todos os módulos
- **supervisor**: visualizar tudo, simular cenários, aprovar e rejeitar pendências
- **analista**: criar, editar, simular e enviar para aprovação — não aprova nem exclui

---

## Módulos
<!-- Cada módulo vira uma tela. Campos marcados (obrigatório) são validados no Step 0 do build.
     Tipos de tela aceitos: dashboard | analytics | grid | master_detail | form | report | mixed | simulation | approval_queue
       dashboard      → KPIs + 1–2 gráficos + grid resumo (visão executiva)
       analytics      → filtros globais + muitos gráficos (4–10) com drill-down (visão analítica)
       grid           → tabela + filtros + CRUD em modal
       master_detail  → grid à esquerda/topo + painel/offcanvas de detalhe do item selecionado
       form           → cadastro/parametrização
       report         → filtros + tabela exportável + 1 gráfico
       simulation     → parâmetros (sliders) + resultado calculado + cenários salvos
       approval_queue → fila de pendências com aprovar/rejeitar
       mixed          → combinação livre
     Tipos de gráfico aceitos: bar | line | area | pie | donut | scatter | histogram | heatmap | treemap | combo | funnel | gauge | sparkline | waterfall | elasticity_curve | scenario_comparison
     Layout (DSL, uma linha por faixa horizontal, de cima para baixo):
       kpis:N        → N cards de KPI
       charts:2col   → 2 gráficos lado a lado (ou charts:3col, charts:1col)
       grid          → tabela principal
       split:7/5     → duas colunas com proporção (ex.: gráfico 7 + grid 5)
       tabs:A,B      → abas nomeadas
       params        → painel de parâmetros (simulação)
       detail        → painel de detalhe (master_detail)
     Ícones: https://icons.getbootstrap.com — ex: speedometer2, bar-chart-line, table, people, gear, box-seam, calculator, check2-circle -->

### [Módulo 1 — ex.: Dashboard Comercial]
**Prioridade**: high
**Tipo de tela**: dashboard
**Grupo de menu**: Visão Geral
**Ícone Bootstrap**: speedometer2
**Objetivo do usuário**: TODO — "Como <role>, quero <ver/fazer o quê> para <decidir o quê>" (1 frase — vira o subtítulo da tela e orienta a hierarquia visual)
**Descrição**: TODO: O que este módulo exibe e qual decisão ele apoia.
**Layout**: kpis:4 | charts:2col | grid
**Participa de workflow**: TODO (opcional) — ex: "Workflow Principal" (se esta tela faz parte de uma jornada maior)

**Componentes visuais:**
- **KPIs:** TODO: liste as métricas, indicando o tipo — `comparação` (mostra atual × referência + delta) ou `simples` (valor + tendência)
  - ex: Receita do mês (comparação vs mês anterior, currency, melhor=sobe)
  - ex: Pedidos abertos (simples, number)
- **Gráfico principal:** TODO: tipo — o que mostra — eixo x / eixo y / agrupamento (ex: line — evolução de receita por mês — x: mes, y: receita, série: canal)
- **Gráfico secundário (opcional):** TODO: tipo — o que mostra
- **Grid/Tabela:** TODO: entidade exibida, colunas mais importantes e formato (currency/percent/date/badge)
- **Filtros:** TODO: campo (tipo) — ex: data_pedido (date_range), status (select: Ativo/Inativo), cliente_nome (text)
- **Drill-down:** TODO (opcional) — ex: "gráfico principal → clique na barra filtra o grid por fornecedor"
- **Ordenação padrão:** TODO — ex: receita desc
- **Estado vazio:** TODO — texto exibido quando os filtros não retornam dados (ex: "Nenhum pedido no período. Amplie o intervalo de datas.")

**Funcionalidades:**
- [F-001] TODO: Nome da feature — descrição detalhada
  - Ações disponíveis: [visualizar | exportar-excel | drill-down | detalhar]
- [F-002] TODO: Nome — descrição

**Regras de negócio:**
- [RN-001]: TODO

**Acesso por role:**
- admin: full
- TODO_role2: [visualizar, exportar-excel]
- TODO_role3: [visualizar]

---

### [Módulo 2 — ex.: Gestão de Preços]
**Prioridade**: high
**Tipo de tela**: master_detail
**Grupo de menu**: Pricing
**Ícone Bootstrap**: tag
**Objetivo do usuário**: TODO
**Descrição**: TODO
**Layout**: kpis:3 | grid | detail

**Componentes visuais:**
- **KPIs:** TODO — ex: Itens ativos (simples), Preço médio (comparação vs tabela anterior)
- **Grid/Tabela:** TODO: entidade, colunas (ex: produto, preço_atual (currency), preço_sugerido (currency), variação_% (percent, cor semântica), status (badge))
- **Ações por linha:** TODO — ex: [detalhar, editar, desativar]
- **Painel de detalhe:** TODO — o que aparece ao selecionar uma linha (ex: ficha do produto + histórico de preços em sparkline + últimos pedidos)
- **Filtros:** TODO: campo (tipo) — ex: categoria (select), fornecedor (select), data_vigencia (date_range)
- **Formulário de criação/edição (modal):** TODO: campos do form — ex: produto_id (select), preco decimal, data_inicio date
- **Ordenação padrão:** TODO
- **Estado vazio:** TODO

**Funcionalidades:**
- [F-003] TODO: Nome — descrição
  - Ações: [criar, editar, excluir | approve, reject | exportar-excel | importar-csv | detalhar]
- [F-004] TODO: Nome — descrição

**Regras de negócio:**
- [RN-002]: TODO (ex: preço não pode ser menor que custo + margem mínima de 10%)
  <!-- OPCIONAL: se já souber a fórmula/condição exata, detalhe abaixo — reduz ambiguidade.
       Se omitido, o pipeline tenta extrair a fórmula automaticamente do texto acima. -->
  - Tipo: validação | campo_derivado | fórmula_interativa | regra_workflow
  - Fórmula/condição: TODO (ex.: "preco >= custo * (1 + margem_minima)" ou "margem = preco - custo")
  - Variáveis de entrada: TODO (ex.: "margem_minima (number, %, constante = 10)")
  - Campos de saída: TODO (ex.: "margem (currency)")

**Acesso por role:**
- admin: full
- TODO_role2: [criar, editar, approve]
- TODO_role3: [visualizar, exportar-excel]

---

### [Módulo 3 — ex.: Análise de Vendas]
**Prioridade**: medium
**Tipo de tela**: analytics
**Grupo de menu**: Visão Geral
**Ícone Bootstrap**: bar-chart-line
**Objetivo do usuário**: TODO
**Descrição**: TODO
**Layout**: kpis:4 | charts:2col | charts:3col | grid

**Componentes visuais:**
- **Filtros globais:** TODO: campo (tipo) — aplicam-se a todos os gráficos (ex: periodo (date_range), agrupamento (select: mensal/trimestral/anual), top_n (select: 5/10/20))
- **KPIs:** TODO
- **Gráficos:** TODO — um por linha: tipo — título — x / y / série
  - ex: combo — Receita e volume por mês — x: mes, barras: volume, linha: receita
  - ex: heatmap — Receita por família × canal — x: canal, y: familia, valor: receita
  - ex: treemap — Participação por categoria — hierarquia: categoria > produto, valor: receita
  - ex: bar — Top N fornecedores — x: receita, y: fornecedor (horizontal)
- **Grid/Tabela exportável:** TODO: colunas do detalhamento
- **Drill-down:** TODO — ex: "heatmap → clique na célula filtra grid por família e canal"
- **Estado vazio:** TODO

**Funcionalidades:**
- [F-005] TODO: Nome — descrição
  - Ações: [visualizar, exportar-excel, drill-down]

**Regras de negócio:**
- [RN-003]: TODO

**Acesso por role:**
- admin: full
- TODO_role2: [visualizar, exportar-excel]

---

### [Módulo de Simulação — ex.: Simulação de Preços]
<!-- Usar quando o projeto requer simular cenários antes de aprovar e aplicar -->
**Prioridade**: high
**Tipo de tela**: simulation
**Grupo de menu**: Pricing
**Ícone Bootstrap**: calculator
**Objetivo do usuário**: TODO — ex: "Como analista, quero ajustar markup por família e ver o impacto em margem antes de enviar para aprovação"
**Descrição**: TODO: O que o analista simula (ex: impacto de alteração de margem e desconto nos preços e receita projetada).
**Layout**: params | kpis:4 | split:7/5 | grid
**Participa de workflow**: Workflow Principal (step: simulação → aprovação)
**Recálculo**: ao vivo (sliders recalculam automaticamente) | por botão
<!-- "ao vivo" dá o efeito de simulador na demo; use "por botão" se o cálculo for pesado -->

**Parâmetros de entrada:**
<!-- Campos que o analista preenche para configurar o cenário. Faixas conhecidas → slider -->
- TODO_param1 (number, %, faixa 0–50, padrão 10) — ex.: markup desejado
- TODO_param2 (number, %, faixa 0–30, padrão 0) — ex.: desconto máximo
- TODO_param3 (select) — ex.: família de produto

**Cenário compartilhado (quando parâmetros impactam outras telas):**
- Chave da arquitetura: TODO — identificador estável, ex.: arquitetura-precos
- Escopo: TODO — ex.: categoria_id; vazio significa todas as linhas
- Dependências: TODO — parâmetro → RN da fórmula → campos de saída → telas consumidoras
- Comparativo principal: Atual × Simulado na própria tela de edição
- Detalhamento: TODO — tela de destino, mantendo cenário, escopo e revisão
- Aplicação: explícita na demo, somente após simular os parâmetros atuais
- Exige aprovação: não — alterar para sim apenas se fizer parte da apresentação
- Descartar: volta ao cenário aplicado; Restaurar demonstração: volta ao original
- Persistência: sessão do navegador, sem alterar CSVs nem exigir banco/API

**Resultado calculado:**
<!-- KPIs e tabela que aparecem após simular -->
- **KPIs:** TODO — ex: Receita Atual × Simulada (comparação), Margem Atual × Simulada (comparação), Variação Total (%), Itens Afetados (simples)
- **Gráfico principal:** TODO — ex: waterfall — ponte Receita atual → efeito preço → efeito volume → Receita simulada
- **Gráfico secundário:** TODO — ex: elasticity_curve — sensibilidade preço × volume para o item selecionado
- **Tabela comparativa:** TODO — colunas (ex: produto, preço atual, preço simulado, variação % (cor semântica), margem simulada)
- **Drill-down:** TODO — ex: "clique na barra do waterfall filtra a tabela por família"
- **Estado vazio:** "Ajuste os parâmetros para ver o impacto do cenário."

**Funcionalidades:**
- [F-SIM-001] Simular cenário: ajustar parâmetros → resultado recalcula → analisar
  - Ações: [simulate]
- [F-SIM-002] Salvar cenário: nomear e gravar o resultado para consulta posterior
  - Ações: [criar]
- [F-SIM-003] Enviar para aprovação: promoção do cenário salvo ao fluxo de aprovação
  - Ações: [submit_approval]

**Regras de negócio:**
- [RN-SIM-001]: TODO — ex: preço simulado = custo × (1 + markup_novo) — este é o `logic_type: fórmula_interativa` do módulo; detalhe a fórmula completa aqui (é o texto que a skill de análise de lógica de negócio usa para gerar o cálculo real da tela — quanto mais precisa esta linha, menos chance de a tela sair com um cálculo genérico/placeholder)
  - Tipo: fórmula_interativa
  - Fórmula/condição: TODO
  - Variáveis de entrada: TODO
  - Campos de saída: TODO
- [RN-SIM-002]: TODO — ex: desconto máximo não pode exceder a política comercial vigente (Tipo: validação)
- [RN-SIM-003]: Cálculo nunca persiste automaticamente — analista escolhe explicitamente salvar (Tipo: regra_workflow)

**Acesso por role:**
- admin: full
- supervisor: [simulate, visualizar, exportar-excel]
- analista: [simulate, criar, submit_approval]

---

### [Módulo de Aprovações — ex.: Fila de Aprovações]
<!-- Usar quando o projeto tem fluxo de aprovação (supervisor avalia itens enviados pelo analista) -->
**Prioridade**: high
**Tipo de tela**: approval_queue
**Grupo de menu**: Pricing
**Ícone Bootstrap**: check2-circle
**Objetivo do usuário**: "Como supervisor, quero avaliar rapidamente os cenários pendentes e aprovar/rejeitar com justificativa"
**Descrição**: TODO: Fila de itens pendentes de aprovação para o supervisor avaliar (ex: cenários de precificação enviados pelos analistas).
**Layout**: kpis:4 | grid | detail
**Participa de workflow**: Workflow Principal (step: aprovação → dashboard ou revisão)
**Badge na sidebar**: contagem de itens com status "Pendente Aprovação"

**Componentes visuais:**
- **KPIs:** Pendentes (simples, number), Aprovados no mês (simples), Rejeitados no mês (simples), Tempo médio de aprovação (simples, text)
- **Grid/Tabela:** lista de itens pendentes — nome/descrição, enviado por, enviado em (date), impacto (currency), status (badge), comentário
- **Ações por linha:** [detalhar, approve, reject]
- **Painel de detalhe:** resumo do cenário selecionado — parâmetros, KPIs de impacto, gráfico comparativo, histórico de comentários
- **Filtros:** status (select: Pendente/Aprovado/Rejeitado), enviado por (select), data de envio (date_range)
- **Ordenação padrão:** enviado em asc (mais antigo primeiro)
- **Estado vazio:** "Nenhuma pendência. Tudo em dia!"

**Funcionalidades:**
- [F-APR-001] Aprovar itens: selecionar → Aprovar → comentário opcional → confirmar
  - Ações: [approve]
- [F-APR-002] Rejeitar itens: selecionar → Rejeitar → comentário obrigatório → confirmar
  - Ações: [reject]
- [F-APR-003] Visualizar histórico: consultar itens já aprovados/rejeitados
  - Ações: [visualizar, exportar-excel]

**Regras de negócio:**
- [RN-APR-001]: Somente supervisor e admin podem aprovar ou rejeitar
- [RN-APR-002]: Rejeição exige comentário explicando o motivo
- [RN-APR-003]: Analista não pode aprovar seus próprios envios
- [RN-APR-004]: TODO — ex: aprovação de cenários com variação > 20% requer justificativa

**Acesso por role:**
- admin: full
- supervisor: [approve, reject, visualizar, exportar-excel]
- analista: [visualizar]

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
- **Grid/Tabela:** lista de usuários — nome, email, role (badge), ativo (badge), último acesso (date)
- **Ações por linha:** [editar, desativar]
- **Filtros:** role (select), ativo (select: Sim/Não)
- **Formulário:** nome (text), email (text), role (select), senha temporária (text)
- **Estado vazio:** "Nenhum usuário encontrado."

**Funcionalidades:**
- [F-006] Gestão de usuários: criar, editar e desativar usuários
  - Ações: [criar, editar, desativar]

**Regras de negócio:**
- [RN-004]: Somente admin pode criar ou desativar usuários
- [RN-005]: Email deve ser único no sistema

**Acesso por role:**
- admin: full

---

## Workflows e Jornadas de Usuário
<!-- Defina os fluxos entre telas interdependentes -->
<!-- O sistema detectará automaticamente padrões, mas você pode especificar fluxos customizados -->
<!-- Categorias: análise | inovação | implementação | controle (metodologia Pricing & Revenue Management) -->

### Workflow Principal: [Nome do Fluxo]
**Categoria**: inovação
**Descrição**: TODO — jornada completa do usuário (ex: desde configuração de arquitetura até aprovação e monitoramento)
**Roles**: [analista, supervisor, admin]

**Steps:**
1. **[Tela Inicial]** → TODO: descrição do que o usuário faz
   - Dados fornecidos: TODO — ex: arquitetura_id, regras_margem
   - Próximo passo: [Nome da próxima tela]

2. **[Tela Intermediária]** → TODO: descrição
   - Dados recebidos: TODO — ex: arquitetura_id, regras_margem
   - Dados fornecidos: TODO — ex: cenario_id, resultado_simulacao
   - Próximo passo: [Nome da próxima tela] (condição: TODO — ex: após salvar cenário)

3. **[Tela Final]** → TODO: descrição
   - Dados recebidos: TODO
   - Ações finais: TODO — ex: visualizar dashboard atualizado, nova simulação

**Exemplo de fluxo comum:**
```
Arquitetura de Preços → Simulação de Cenário → Salvar Cenário →
Enviar para Aprovação → Fila de Aprovações → Aprovar/Rejeitar →
Dashboard (reflete mudanças)
```

### Workflow Secundário (opcional): [Nome]
**Categoria**: análise | controle
**Descrição**: TODO
**Roles**: [supervisor, admin]

**Steps:**
1. TODO
2. TODO

**Notas sobre Workflows:**
- Workflows são gerados automaticamente pelo sistema baseado nos módulos definidos
- Telas de simulação + aprovação sempre criam um workflow automático
- Dashboards + relatórios criam workflows de análise
- Você pode especificar workflows customizados aqui se necessário
- Dados fluem automaticamente entre telas do mesmo workflow

---

## Entidades de Dados
<!-- Para cada entidade: descrição + campos principais + relacionamentos + VOLUMETRIA DE DEMO
     Tipos de campo: varchar(N), nvarchar(N), int, bigint, decimal(P,S), float, date, datetime2, bit, text
     Enum: listar os valores possíveis
     Papel: dimensao (cadastro, poucas linhas, muda pouco) | fato (transações/eventos, muitas linhas, tem data) | apoio (config, log)
     Distribuições aceitas (uma por campo, opcional — o gerador de mock usa isso para parecer real):
       enum(A:60%, B:30%, C:10%)         → valores com pesos
       faixa(min–max)                    → uniforme
       normal(media, desvio)             → gaussiana
       pareto                            → 20% dos itens concentram 80% do valor
       sazonal(mensal, pico: nov,dez)    → séries temporais com sazonalidade (fatos com data)
       tendencia(+X% ao ano)             → crescimento/queda ao longo do período
       derivado(<expressão>)             → calculado de outros campos DA MESMA LINHA (ex: derivado(quantidade * preco_unitario))
       lista(BR:cidades | BR:estados | BR:nomes | BR:empresas | BR:produtos_<dominio>) → catálogos brasileiros embutidos -->

### {Entidade1}
**Descrição**: TODO — o que representa, para qual módulo serve
**Papel**: dimensao
**Campos principais**: TODO — ex: nome varchar(100), categoria enum(Premium/Standard/Econômico), valor decimal(15,2), status enum(Ativo/Inativo), data_inicio date
**Relacionamentos**: TODO — ex: pertence a {Entidade2}, tem muitos {Entidade3}
**Módulo**: TODO
**Volumetria de demo**: TODO — ex: 120 registros
**Distribuições**: TODO — ex: categoria: enum(Premium:20%, Standard:50%, Econômico:30%); status: enum(Ativo:92%, Inativo:8%); valor: pareto
**Exemplo de linha**: TODO — ex: "Bateria 60Ah Heavy Duty" · Standard · 389,90 · Ativo · 2025-03-01

### {Entidade2}
**Descrição**: TODO
**Papel**: fato
**Campos principais**: TODO — ex: data date, quantidade int, preco_unitario decimal(15,2), receita decimal(15,2), canal enum(Loja/E-commerce/Atacado)
**Relacionamentos**: TODO — ex: pertence a {Entidade1}, pertence a Cliente
**Módulo**: TODO
**Volumetria de demo**: TODO — ex: 5.000 registros
**Distribuições**: TODO — ex: data: sazonal(mensal, pico: nov,dez) + tendencia(+8% ao ano); quantidade: normal(12, 5); canal: enum(Loja:55%, E-commerce:30%, Atacado:15%); receita: derivado(quantidade * preco_unitario)
**Exemplo de linha**: TODO

### {EntidadeComAprovacao}
<!-- Copiar este bloco para qualquer entidade que passa pelo fluxo de aprovação -->
<!-- Remover este bloco se a entidade NÃO tem fluxo de aprovação -->
**Descrição**: TODO
**Papel**: fato
**Campos principais**: TODO + os campos de aprovação abaixo são OBRIGATÓRIOS para o fluxo:
  - status enum(Rascunho/Pendente Aprovação/Aprovado/Rejeitado) default Rascunho
  - aprovado_por varchar(100) nullable
  - aprovado_em datetime2 nullable
  - comentario_aprovacao text nullable
**Relacionamentos**: TODO
**Módulo**: TODO (+ Módulo de Aprovações)
**Volumetria de demo**: TODO — ex: 40 registros
**Distribuições**: status: enum(Rascunho:20%, Pendente Aprovação:30%, Aprovado:40%, Rejeitado:10%)
<!-- garanta ≥5 itens "Pendente Aprovação" para a fila ter o que mostrar na demo -->

### {EntidadeComSimulacao}
<!-- Copiar este bloco para entidades cujos valores são simulados antes de aplicar -->
<!-- Remover se não houver módulo de simulação -->
**Descrição**: TODO — entidade base para a simulação (ex: precificacao, tabela_preco)
**Papel**: dimensao
**Campos principais**: TODO + os campos abaixo são necessários para cálculo:
  - custo decimal(15,2) — base de cálculo
  - preco_atual decimal(15,2) — preço vigente
  - volume int nullable — quantidade para projeção de receita
  - elasticidade decimal(6,3) nullable — sensibilidade preço × volume (ex: -1.2)
**Relacionamentos**: TODO
**Módulo**: Módulo de Simulação
**Volumetria de demo**: TODO — ex: 300 registros
**Distribuições**: custo: pareto; preco_atual: derivado(custo * 1.35); volume: pareto; elasticidade: normal(-1.2, 0.4)

### CenarioSimulacao
<!-- Manter se o projeto tem módulo de simulação; remover caso contrário -->
**Descrição**: Registra os cenários de simulação salvos pelo analista para consulta e envio para aprovação
**Papel**: fato
**Campos principais**: nome varchar(200), parametros text (JSON), receita_atual decimal(15,2), receita_simulada decimal(15,2), variacao_pct decimal(8,4), status enum(Rascunho/Pendente Aprovação/Aprovado/Rejeitado) default Rascunho, criado_por varchar(100), aprovado_por varchar(100) nullable, aprovado_em datetime2 nullable, comentario_aprovacao text nullable
**Relacionamentos**: pertence a Usuarios (criado_por)
**Módulo**: Módulo de Simulação + Módulo de Aprovações
**Volumetria de demo**: 30 registros
**Distribuições**: status: enum(Rascunho:20%, Pendente Aprovação:30%, Aprovado:40%, Rejeitado:10%); variacao_pct: normal(2.5, 4)

### Usuarios
**Descrição**: Usuários do sistema com autenticação JWT
**Papel**: apoio
**Campos principais**: nome varchar(100), email varchar(150) único, senha_hash varchar(255), role enum(admin/TODO_role2/TODO_role3), ativo bit, ultimo_acesso datetime2 nullable
**Relacionamentos**: —
**Módulo**: Administração
**Volumetria de demo**: 12 registros (inclui 1 por role com os e-mails de "Credenciais de demo")

---

## Branding
<!-- Identidade visual do cliente — personaliza design system, login, sidebar e favicon -->
- **Cor primária**: auto — hexadecimal oficial, se informado, prevalece sobre a cor estimada do logo
- **Cor secundária**: (opcional — usada em gráficos e destaques; padrão: derivada da primária)
- **Logo**: assets/logo.png — grande e centralizado no painel do login; sem arquivo, mostrar nome da empresa
- **Logo para fundo escuro** (opcional): (ex: assets/logo-white.png — usado no painel do login)
- **Favicon**: (opcional — ex: assets/favicon.ico)
- **Nome na sidebar**: (nome curto — padrão: nome do projeto)
- **Tagline**: TODO — frase curta exibida no login (ex: "Decisões de preço com confiança")
- **Fonte**: system (padrão) | inter

## Assistente de Pricing (automático)
<!-- Não é necessário preencher perguntas/respostas: o pipeline descobre análises a partir
     das funcionalidades, dados e fórmulas reais do roadmap. Sem API de IA em runtime. -->
- **Habilitado**: sim — padrão; usar não para excluir o assistente deste projeto
- **Análises**: auto — conforme regras, campos e objetivos dos módulos
- **Contexto**: tela, filtros, produto selecionado e cenário da sessão
- **Ações**: abrir detalhe e simular proposta; aplicação sempre explícita pelo usuário
- **Limitações**: não estimar volume/ótimo de preço sem regra de demanda; informar hipóteses

---

## Integrações
<!-- Liste apenas se houver integração com sistema externo — remover se não houver -->
- **TODO** (remover se não houver): Tipo (API REST | Database | Arquivo CSV/Excel) — Descrição breve da integração

---

## Requisitos Não-Funcionais
- **Performance**: Consultas < 3s com volume médio de dados
- **Segurança**: JWT com expiração de 8h, senhas com bcrypt, HTTPS em produção
- **Escalabilidade**: Suporte a TODO usuários simultâneos
- **Disponibilidade**: TODO (ex: disponível em horário comercial 8h–18h)
