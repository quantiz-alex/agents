# OneSpaWorld — Cruise Control (Recommendation Engine & Revenue Optimization)

## Descrição
Portal de governança (Human-in-the-Loop) para o motor de recomendação de receita "Cruise Control" da OneSpaWorld (OSW): apresenta as recomendações geradas pelo motor estatístico — desconto ótimo, disponibilidade de serviço (exibir/suprimir) e priorização de mix de serviços — para revisão, aprovação, modificação ou rejeição pelo time de receita, aplicando guardrails comerciais obrigatórios (cap de desconto de 30%, pisos de preço, blackout de parceiros) e exibindo os drivers de explicabilidade (SHAP) de cada recomendação.
Resolve a falta de controle e transparência sobre descontos de pré-reserva de serviços de spa a bordo: hoje o desconto é definido sem base em elasticidade nem em impacto no RevPATH, e não há trilha de decisão auditável. O sistema consome dados do ambiente Microsoft Fabric já existente da OSW (bookings, transações onboard) e devolve as decisões aprovadas para a plataforma de pré-reserva marítima WPBS.
Usuários: time de receita/pricing da OSW (revisão, aprovação e configuração de guardrails) e analistas de pricing (consulta a recomendações e relatórios analíticos).

<!-- nota de escopo: nesta geração, as recomendações, a confiança do modelo e os drivers SHAP vêm do MOCK VOLUMÉTRICO gerado pelo pipeline (entidade Recomendacao).
     O motor estatístico/ML mock da versão anterior (backend/ml_engine/ — elasticidade via statsmodels, LightGBM, SHAP, MLflow local, drift KS-test, champion-challenger)
     NÃO é gerado pelo pipeline; pode ser reacoplado ao novo backend após o build, sem mudança de arquitetura (consumido via /api/v1/ml/*).
     A calibração com os 2–3 anos de dados reais de booking do Fabric continua sendo trabalho futuro. -->

## Stack Tecnológico
<!-- SEÇÃO FIXA — NÃO ALTERAR. O pipeline não suporta outras tecnologias. -->
- **Frontend**: Dash 2.14+ · Dash Bootstrap Components · Dash AG Grid · Plotly · Pandas/NumPy
- **Backend**: FastAPI · SQLAlchemy · Pydantic v2 · JWT (python-jose + bcrypt)
- **Banco**: SQL Server / Microsoft Fabric (SQLite em dev)

---

## Contexto de Demonstração
- **Persona da demo**: Revenue Director da OSW, que precisa decidir se o piloto do Cruise Control está gerando uplift de RevPATH suficiente para escalar a governança de descontos para toda a frota.
- **Cenário narrativo**: O gestor de receita abre o Dashboard e vê RevPATH 8,4% acima do baseline na Classe Aurora, mas 37 recomendações pendentes. Na Fila de Governança, abre uma recomendação de 25% de desconto em Massagem no itinerário Caribe Oriental, consulta os drivers SHAP (antecedência e ocupação do navio), reduz para 18% por estar próximo do piso de preço e aprova; rejeita outra que cai em blackout do parceiro. Em seguida, nos Relatórios de Elasticidade, confirma que Massagem é elástica (−1,6) e que o desconto pré-cruzeiro expande a carteira onboard em vez de substituí-la.
- **Números-âncora**: piloto com 12 navios em 4 classes e 4 parceiros (linhas de cruzeiro); 6 itinerários; 8 categorias de serviço; receita anual de spa no piloto ≈ US$ 18M; RevPATH médio ≈ US$ 145 (baseline ≈ US$ 134); ticket médio de tratamento ≈ US$ 210; ≈ 400 recomendações geradas por mês; taxa de aprovação ≈ 72%; desconto médio aprovado ≈ 14%
- **Período dos dados**: últimos 18 meses até o mês atual (12 meses de baseline + 6 meses de piloto; o mock gera datas relativas a hoje)
- **Locale**: pt-BR · moeda US$ · datas dd/mm/aaaa
  <!-- TODO: confirmar com o cliente se a interface deve ser em inglês (time da OSW é US-based) -->
- **Credenciais de demo**: uma por role (o login exibe chips clicáveis) — admin@onespaworld.demo · gestor@onespaworld.demo · analista@onespaworld.demo

---

## Perfis de Acesso
<!-- Roles inferidos do documento (RFP 7.11) — revisar nomes/permissões com o cliente -->
- **admin**: acesso total — gerenciar guardrails, usuários, configurações e todos os módulos
- **gestor_receita** (Revenue/Pricing Manager — time de receita da OSW): visualizar, aprovar, modificar e rejeitar recomendações; visualizar dashboards e relatórios de elasticidade/RevPATH; exportar
- **analista_pricing** (Pricing Analyst): visualizar recomendações, dashboards e relatórios analíticos; exportar — não aprova, não modifica guardrails
<!-- inferido: revisar — o documento não detalha papéis de usuário final da aplicação, apenas o squad de entrega (Consultoria/Tech). -->

---

## Módulos

### Dashboard Executivo (RevPATH & Piloto)
**Prioridade**: high
**Tipo de tela**: dashboard
**Grupo de menu**: Visão Geral
**Ícone Bootstrap**: speedometer2
**Objetivo do usuário**: Como gestor de receita, quero acompanhar o RevPATH do piloto contra o baseline e o volume de recomendações pendentes para decidir onde agir primeiro.
**Descrição**: Visão consolidada de performance do piloto de recomendação: RevPATH atual vs. baseline, uplift de receita, volume e taxa de aprovação das recomendações, e acompanhamento semanal do piloto por classe de navio (RFP 7.5 execução/monitoramento).
**Layout**: kpis:6 | charts:2col | grid
**Participa de workflow**: Workflow Principal (step: monitoramento → identificação de pendências)

**Componentes visuais:**
- **KPIs:**
  - RevPATH Atual (comparação vs RevPATH Baseline, currency, melhor=sobe)
  - Uplift de Receita (simples, percent, melhor=sobe)
  - Recomendações Pendentes (simples, number)
  - Taxa de Aprovação (comparação vs mês anterior, percent, melhor=sobe)
  - Desconto Médio Aprovado (comparação vs mês anterior, percent, melhor=desce)
  - Taxa de Utilização de Desconto (simples, percent)
- **Gráfico principal:** line — evolução do RevPATH por semana — x: semana, y: revpath, séries: atual × baseline (marcador vertical no início do piloto)
- **Gráfico secundário:** bar — RevPATH atual × baseline por classe de navio — x: classe_navio, y: revpath, agrupamento: atual/baseline
- **Grid/Tabela:** Recomendações recentes — navio, classe de navio, itinerário, categoria de serviço, desconto sugerido (percent), confiança do modelo (percent), gerado em (date), status (badge)
- **Filtros:** classe_navio (select), itinerario (select), periodo (date_range), status (select: Pendente Aprovação/Aprovado/Modificado/Rejeitado)
- **Drill-down:** gráfico secundário → clique na barra da classe de navio filtra o grid e o gráfico principal por classe
- **Ordenação padrão:** gerado_em desc
- **Estado vazio:** "Nenhuma recomendação no período. Amplie o intervalo de datas ou remova filtros."

**Funcionalidades:**
- [F-001] Monitorar performance do piloto — visualizar KPIs e evolução do RevPATH atual vs. baseline
  - Ações disponíveis: [visualizar, exportar-excel]
- [F-002] Drill-down por navio/itinerário — detalhar KPIs por classe de navio e itinerário
  - Ações disponíveis: [visualizar, drill-down]

**Regras de negócio:**
- [RN-001]: RevPATH = receita de tratamentos ÷ horas de tratamento disponíveis no período
  - Tipo: campo_derivado
  - Fórmula/condição: "revpath = receita_tratamentos / horas_disponiveis"
  - Variáveis de entrada: "receita_tratamentos (currency), horas_disponiveis (number)"
  - Campos de saída: "revpath (currency)"
- [RN-001b]: Uplift = variação percentual do RevPATH atual sobre o baseline
  - Tipo: campo_derivado
  - Fórmula/condição: "uplift_pct = (revpath_atual - revpath_baseline) / revpath_baseline * 100"
  - Campos de saída: "uplift_pct (percent)"
- [RN-001c]: Taxa de aprovação = (Aprovado + Modificado) ÷ total de recomendações decididas (exclui Pendente Aprovação)
  - Tipo: campo_derivado
- [RN-001d]: KPIs recalculados a partir dos dados de booking ingeridos do Microsoft Fabric — TODO: confirmar frequência de atualização (diária/near real-time)

**Acesso por role:**
- admin: full
- gestor_receita: [visualizar, exportar-excel, drill-down]
- analista_pricing: [visualizar, drill-down]

---

### Fila de Governança de Recomendações
<!-- RFP 7.11 — Human-in-the-Loop Governance UI -->
**Prioridade**: high
**Tipo de tela**: approval_queue
**Grupo de menu**: Governança
**Ícone Bootstrap**: check2-square
**Objetivo do usuário**: Como gestor de receita, quero revisar cada recomendação com seus drivers de explicabilidade e aprovar, ajustar ou rejeitar dentro dos guardrails, para que só decisões seguras cheguem ao WPBS.
**Descrição**: Portal para o time de receita da OSW revisar, aprovar, modificar ou rejeitar as recomendações geradas pelo motor estatístico (desconto ótimo, disponibilidade de serviço, priorização de mix), aplicando os guardrails obrigatórios (cap de 30%, pisos de preço, blackout windows de parceiros) e consultando os drivers de explicabilidade (SHAP) de cada recomendação.
**Layout**: kpis:5 | grid | detail
**Participa de workflow**: Workflow Principal (step: recomendação gerada → revisão → aprovação/modificação/rejeição → aplicação via WPBS)
**Badge na sidebar**: contagem de recomendações com status "Pendente Aprovação"

**Componentes visuais:**
- **KPIs:** Pendentes (simples, number), Aprovadas no mês (simples, number), Modificadas no mês (simples, number), Rejeitadas no mês (simples, number), Tempo Médio de Revisão (simples, text — ex: "6,5 h")
- **Grid/Tabela:** recomendações — navio, classe de navio, itinerário, parceiro, categoria de serviço, tier de cabine (proxy), preço base (currency), desconto sugerido (percent), preço sugerido (currency), disponibilidade sugerida (badge: Exibir/Suprimir), prioridade de mix (number), confiança do modelo (percent), alerta de guardrail (badge: OK/Acima do cap/Abaixo do piso/Blackout), status (badge)
- **Ações por linha:** [detalhar, approve, editar, reject]
- **Painel de detalhe:** resumo da recomendação selecionada — parâmetros (navio, itinerário, categoria, tier), preço base × preço sugerido × piso do guardrail, gráfico bar horizontal com os 5 principais drivers SHAP (feature × impacto, cor semântica positivo/negativo), histórico de decisões e comentários
- **Formulário de modificação (modal):** desconto_final_pct (number, %, 0–30), disponibilidade_final (select: Exibir/Suprimir), comentario_aprovacao (text, obrigatório) — validação ao vivo contra o guardrail da categoria
- **Filtros:** status (select: Pendente Aprovação/Aprovado/Modificado/Rejeitado), classe_navio (select), parceiro (select), categoria_servico (select), gerado_em (date_range)
- **Ordenação padrão:** gerado_em asc (mais antiga primeiro)
- **Estado vazio:** "Nenhuma recomendação pendente. Tudo em dia!"

**Funcionalidades:**
- [F-003] Revisar recomendação — visualizar detalhe da recomendação e seus drivers SHAP
  - Ações disponíveis: [visualizar, detalhar]
- [F-004] Aprovar recomendação — aplica o valor sugerido sem alteração; comentário opcional
  - Ações disponíveis: [approve]
- [F-005] Modificar recomendação — ajustar desconto/disponibilidade dentro dos guardrails; status final "Modificado"
  - Ações disponíveis: [editar, approve]
- [F-006] Rejeitar recomendação — comentário obrigatório
  - Ações disponíveis: [reject]
- [F-006b] Consultar histórico de decisões e exportar
  - Ações disponíveis: [visualizar, exportar-excel]

**Regras de negócio:**
- [RN-002]: Desconto aprovado não pode exceder o cap de 30% nem o desconto máximo do guardrail da categoria
  - Tipo: validação
  - Fórmula/condição: "desconto_final_pct <= min(30, guardrail.desconto_max_pct)"
  - Variáveis de entrada: "desconto_final_pct (number, %), guardrail.desconto_max_pct (number, %, padrão = 30)"
- [RN-003]: Preço final aprovado não pode ficar abaixo do piso de preço configurado para a categoria
  - Tipo: validação
  - Fórmula/condição: "preco_base * (1 - desconto_final_pct / 100) >= guardrail.piso_preco"
  - Variáveis de entrada: "preco_base (currency), desconto_final_pct (number, %), guardrail.piso_preco (currency)"
- [RN-003b]: Preço sugerido e preço final derivados do preço base
  - Tipo: campo_derivado
  - Fórmula/condição: "preco_sugerido = preco_base * (1 - desconto_sugerido_pct / 100); preco_final = preco_base * (1 - desconto_final_pct / 100)"
  - Campos de saída: "preco_sugerido (currency), preco_final (currency)"
- [RN-004]: Recomendações cuja data_servico cai dentro de uma blackout window ativa do parceiro não podem ser aprovadas nem modificadas
  - Tipo: validação
  - Fórmula/condição: "NOT (guardrail.parceiro == recomendacao.parceiro AND guardrail.ativo AND data_servico BETWEEN guardrail.blackout_inicio AND guardrail.blackout_fim)"
- [RN-005]: Rejeição e modificação exigem comentário explicando o motivo
  - Tipo: regra_workflow
- [RN-005b]: Somente gestor_receita e admin podem aprovar, modificar ou rejeitar; toda decisão grava registro imutável em HistoricoDecisao
  - Tipo: regra_workflow
- [RN-006]: TODO — confirmar com o cliente se há regra de segregação de funções (ex.: quem configura o guardrail de uma categoria não pode aprovar recomendações dessa mesma categoria)

**Acesso por role:**
- admin: full
- gestor_receita: [approve, reject, editar, visualizar, detalhar, exportar-excel]
- analista_pricing: [visualizar, detalhar]

---

### Relatórios de Elasticidade & Interplay
<!-- RFP 7.1 (elasticidade), 7.3 (interplay onboard), 7.4 (yield/RevPATH) -->
**Prioridade**: medium
**Tipo de tela**: analytics
**Grupo de menu**: Análises
**Ícone Bootstrap**: graph-up-arrow
**Objetivo do usuário**: Como analista de pricing, quero entender a elasticidade de preço por categoria/navio/tier e se o desconto pré-cruzeiro expande ou canibaliza o gasto onboard, para calibrar a política de descontos.
**Descrição**: Relatórios analíticos de elasticidade de preço por categoria de serviço/navio/itinerário/tier de cabine, estudo de interplay entre receita onboard e desconto pré-cruzeiro para o mesmo hóspede, e estratégia de yield (RevPATH) por categoria.
**Layout**: kpis:4 | charts:2col | charts:2col | grid

**Componentes visuais:**
- **Filtros globais:** categoria_servico (select), classe_navio (select), itinerario (select), tier_cabine_proxy (select: Interior/Oceanview/Varanda/Suíte), janela_antecedencia (select: 0–30/31–90/91+ dias)
- **KPIs:** Elasticidade média (simples, number), R² médio dos modelos (simples, percent), % hóspedes em Expansão de carteira (simples, percent, melhor=sobe), Receita onboard incremental estimada (simples, currency)
- **Gráficos:**
  - bar — Coeficiente de elasticidade por categoria de serviço — x: categoria_servico, y: coeficiente_elasticidade (horizontal, ordenado)
  - heatmap — Elasticidade por categoria × tier de cabine — x: tier_cabine_proxy, y: categoria_servico, valor: coeficiente_elasticidade
  - scatter — Desconto pré-cruzeiro × gasto onboard (mesmo hóspede) — x: desconto_pre_cruzeiro_pct, y: gasto_onboard, cor: classificacao (Substituição/Expansão)
  - elasticity_curve — Curva preço × volume da categoria selecionada — x: variação de preço (%), y: variação de volume (%)
- **Grid/Tabela exportável:** categoria de serviço, classe de navio, tier de cabine, janela de antecedência, coeficiente de elasticidade (number), R² (percent), receita onboard incremental estimada (currency), calculado em (date)
- **Drill-down:** bar de elasticidade → clique na categoria filtra heatmap, scatter, curva e grid por categoria; célula do heatmap → filtra grid por categoria e tier
- **Ordenação padrão:** coeficiente_elasticidade asc (mais elástico primeiro)
- **Estado vazio:** "Nenhum estudo de elasticidade para os filtros selecionados."

**Funcionalidades:**
- [F-007] Visualizar estudo de elasticidade por categoria/navio/itinerário/tier de cabine
  - Ações disponíveis: [visualizar, exportar-excel, drill-down]
- [F-008] Visualizar relatório de interplay onboard × pré-cruzeiro (substituição vs. expansão de carteira)
  - Ações disponíveis: [visualizar, exportar-excel, drill-down]

**Regras de negócio:**
- [RN-007]: Coeficientes de elasticidade são calculados fora da aplicação (pipeline de Data Science/Fabric) e apenas importados/exibidos aqui — TODO: confirmar frequência de atualização e formato de ingestão
- [RN-007b]: Curva de elasticidade derivada do coeficiente
  - Tipo: fórmula_interativa
  - Fórmula/condição: "variacao_volume_pct = coeficiente_elasticidade * variacao_preco_pct"
  - Variáveis de entrada: "variacao_preco_pct (number, %, faixa -30–+10), coeficiente_elasticidade (number)"
  - Campos de saída: "variacao_volume_pct (percent)"
- [RN-008]: TODO — confirmar regras de anonimização de PII para os dados de hóspede usados no estudo de interplay (guest_id sempre hasheado; nenhum dado pessoal exibido)

**Acesso por role:**
- admin: full
- gestor_receita: [visualizar, exportar-excel, drill-down]
- analista_pricing: [visualizar, exportar-excel, drill-down]

---

### Configuração de Guardrails
**Prioridade**: high
**Tipo de tela**: grid
**Grupo de menu**: Configuração
**Ícone Bootstrap**: shield-check
**Objetivo do usuário**: Como admin, quero manter os limites comerciais (cap de desconto, piso de preço, blackout de parceiros) que toda recomendação aprovada deve respeitar.
**Descrição**: Parametrização dos guardrails comerciais obrigatórios aplicados às recomendações — cap máximo de desconto, pisos de preço por categoria de serviço e janelas de blackout por parceiro.
**Layout**: kpis:3 | grid

**Componentes visuais:**
- **KPIs:** Guardrails ativos (simples, number), Blackouts vigentes hoje (simples, number), Recomendações pendentes violando guardrail (simples, number)
- **Grid/Tabela:** guardrails cadastrados — categoria de serviço, desconto máximo (percent), piso de preço (currency), parceiro, início do blackout (date), fim do blackout (date), ativo (badge)
- **Ações por linha:** [editar, excluir]
- **Filtros:** categoria_servico (select), parceiro (select), ativo (select: Sim/Não)
- **Formulário de criação/edição (modal):** categoria_servico (select), desconto_max_pct (number, %, 0–30, padrão 30), piso_preco (decimal), parceiro (select, opcional), blackout_inicio (date, opcional), blackout_fim (date, opcional), ativo (switch)
- **Ordenação padrão:** categoria_servico asc
- **Estado vazio:** "Nenhum guardrail cadastrado. Crie o primeiro para proteger as recomendações."

**Funcionalidades:**
- [F-009] Cadastrar/editar/excluir guardrail por categoria de serviço e/ou parceiro
  - Ações disponíveis: [criar, editar, excluir, exportar-excel]

**Regras de negócio:**
- [RN-009]: desconto_max_pct não pode exceder 30% (limite contratual definido na fase de Definição do engajamento)
  - Tipo: validação
  - Fórmula/condição: "0 <= desconto_max_pct <= 30"
- [RN-009b]: blackout_fim deve ser maior ou igual a blackout_inicio quando ambos preenchidos
  - Tipo: validação
  - Fórmula/condição: "blackout_fim >= blackout_inicio"

**Acesso por role:**
- admin: full
- gestor_receita: [visualizar, exportar-excel]
- analista_pricing: [visualizar]

---

### Administração
**Prioridade**: low
**Tipo de tela**: grid
**Grupo de menu**: Administração
**Ícone Bootstrap**: people
**Objetivo do usuário**: Como admin, quero manter os usuários e seus perfis de acesso.
**Descrição**: Controle de usuários do sistema.
**Layout**: grid

**Componentes visuais:**
- **Grid/Tabela:** lista de usuários — nome, email, role (badge), ativo (badge), último acesso (date)
- **Ações por linha:** [editar, desativar]
- **Filtros:** role (select), ativo (select: Sim/Não)
- **Formulário:** nome (text), email (text), role (select), senha temporária (text)
- **Estado vazio:** "Nenhum usuário encontrado."

**Funcionalidades:**
- [F-010] Gestão de usuários: criar, editar e desativar usuários
  - Ações: [criar, editar, desativar]

**Regras de negócio:**
- [RN-010]: Somente admin pode criar ou desativar usuários
- [RN-011]: Email deve ser único no sistema

**Acesso por role:**
- admin: full

---

## Workflows e Jornadas de Usuário

### Workflow Principal: Governança de Recomendações Cruise Control
**Categoria**: controle
**Descrição**: Jornada desde a geração da recomendação pelo motor estatístico até a revisão humana (aprovação/modificação/rejeição) e o acompanhamento do impacto real da decisão.
**Roles**: [analista_pricing, gestor_receita, admin]

**Steps:**
1. **Dashboard Executivo** → gestor_receita monitora KPIs (RevPATH, uplift, taxa de aprovação) e identifica recomendações pendentes
   - Dados fornecidos: classe_navio, itinerario, periodo
   - Próximo passo: Fila de Governança de Recomendações

2. **Fila de Governança de Recomendações** → gestor_receita revisa o detalhe da recomendação e seus drivers SHAP, e aprova, modifica ou rejeita respeitando os guardrails vigentes
   - Dados recebidos: classe_navio, itinerario, periodo
   - Dados fornecidos: recomendacao_id, categoria_servico, status, desconto_final_pct
   - Próximo passo: Relatórios de Elasticidade & Interplay (condição: após decidir, para checar a elasticidade da categoria)

3. **Relatórios de Elasticidade & Interplay** → gestor_receita/analista_pricing acompanha a elasticidade e o interplay onboard da categoria decidida
   - Dados recebidos: categoria_servico, classe_navio
   - Ações finais: exportar relatório, retornar ao Dashboard Executivo

**Exemplo de fluxo comum:**
```
Dashboard Executivo → Fila de Governança de Recomendações → Aprovar/Modificar/Rejeitar →
Relatórios de Elasticidade & Interplay (acompanhamento) → Dashboard Executivo (reflete mudanças)
```

### Workflow Secundário: Ajuste de Guardrails
**Categoria**: controle
**Descrição**: Quando muitas recomendações pendentes violam guardrails, o admin revisa os limites da categoria/parceiro e o gestor volta à fila para decidir com os limites atualizados.
**Roles**: [admin, gestor_receita]

**Steps:**
1. **Configuração de Guardrails** → admin identifica recomendações violando guardrail e ajusta piso/cap/blackout
   - Dados fornecidos: categoria_servico, parceiro
   - Próximo passo: Fila de Governança de Recomendações
2. **Fila de Governança de Recomendações** → gestor_receita revisa as pendências daquela categoria/parceiro com os novos limites
   - Dados recebidos: categoria_servico, parceiro

**Notas sobre Workflows:**
- Telas de aprovação sempre criam um workflow automático de governança
- Dashboards + relatórios criam workflows de análise
- Dados fluem automaticamente entre telas do mesmo workflow

---

## Entidades de Dados

### Parceiro
**Descrição**: Linha de cruzeiro parceira da OSW onde o spa opera (dona dos navios e das blackout windows).
**Papel**: dimensao
**Campos principais**: nome varchar(100), codigo varchar(10), mercado_principal enum(América do Norte/Europa/Ásia-Pacífico), ativo bit
**Relacionamentos**: tem muitos Navio, tem muitos GuardrailConfig
**Módulo**: Configuração de Guardrails, Fila de Governança de Recomendações
**Volumetria de demo**: 4 registros
**Distribuições**: mercado_principal: enum(América do Norte:50%, Europa:25%, Ásia-Pacífico:25%); ativo: 100% Ativo
**Exemplo de linha**: "Atlantica Cruises" · ATL · América do Norte · 1

### Navio
**Descrição**: Navio do piloto, com classe e capacidade de atendimento do spa (base do RevPATH).
**Papel**: dimensao
**Campos principais**: nome varchar(100), classe_navio enum(Aurora/Meridian/Horizon/Solstice), capacidade_hospedes int, salas_tratamento int, horas_tratamento_dia int, ativo bit
**Relacionamentos**: pertence a Parceiro; tem muitas Recomendacao, tem muitas RevPathMetrica
**Módulo**: Dashboard Executivo, Fila de Governança de Recomendações
**Volumetria de demo**: 12 registros (3 por classe)
**Distribuições**: classe_navio: enum(Aurora:25%, Meridian:25%, Horizon:25%, Solstice:25%); capacidade_hospedes: faixa(2200–6500); salas_tratamento: faixa(14–32); horas_tratamento_dia: faixa(10–12)
**Exemplo de linha**: "Aurora Serenade" · Aurora · 5.400 · 28 · 12 · 1

### CategoriaServico
**Descrição**: Catálogo de categorias de serviço do spa com preço base de referência.
**Papel**: dimensao
**Campos principais**: nome enum(Massagem/Facial/Acupuntura/Medi-Spa/Fitness & Personal/Salão & Beleza/Pacotes Spa/Thermal Suite), preco_base decimal(15,2), duracao_min int, ativo bit
**Relacionamentos**: tem muitas Recomendacao, tem muitos GuardrailConfig, tem muitas ElasticidadePreco
**Módulo**: todos
**Volumetria de demo**: 8 registros
**Distribuições**: preco_base: faixa(89–399); duracao_min: enum(30:20%, 50:40%, 75:25%, 90:15%)
**Exemplo de linha**: "Massagem" · 239,00 · 50 · 1

### Recomendacao
**Descrição**: Recomendação gerada pelo motor estatístico para uma combinação navio/itinerário/categoria de serviço/tier de cabine, com os 3 outputs (desconto, disponibilidade, mix), drivers SHAP e o fluxo de aprovação humana.
**Papel**: fato
**Campos principais**: navio_id int, parceiro_id int, categoria_servico_id int, itinerario enum(Caribe Oriental 7n/Caribe Ocidental 7n/Bahamas 4n/Mediterrâneo 10n/Alasca 7n/Norte da Europa 12n), tier_cabine_proxy enum(Interior/Oceanview/Varanda/Suíte), data_servico date, antecedencia_dias int, preco_base decimal(15,2), desconto_sugerido_pct decimal(5,2), preco_sugerido decimal(15,2), disponibilidade_sugerida enum(Exibir/Suprimir), prioridade_mix int, confianca_modelo decimal(5,4), shap_drivers text (JSON — lista dos 5 principais drivers {feature, impacto}; features: antecedencia_dias, ocupacao_navio, tier_cabine, gasto_onboard_historico, dia_da_viagem, sazonalidade), alerta_guardrail enum(OK/Acima do cap/Abaixo do piso/Blackout), desconto_final_pct decimal(5,2) nullable, disponibilidade_final enum(Exibir/Suprimir) nullable, preco_final decimal(15,2) nullable, gerado_em datetime2 + campos de aprovação OBRIGATÓRIOS para o fluxo:
  - status enum(Pendente Aprovação/Aprovado/Modificado/Rejeitado) default Pendente Aprovação
  - aprovado_por varchar(100) nullable
  - aprovado_em datetime2 nullable
  - comentario_aprovacao text nullable
**Relacionamentos**: pertence a Navio; pertence a Parceiro; pertence a CategoriaServico; pertence a Usuarios (aprovado_por); tem muitos HistoricoDecisao
**Módulo**: Fila de Governança de Recomendações (+ Dashboard Executivo)
**Volumetria de demo**: 2.400 registros (≈ 400/mês nos 6 meses do piloto)
**Distribuições**: gerado_em: sazonal(mensal, pico: dez,jan,jul) + concentrado nos 6 meses mais recentes; status: enum(Pendente Aprovação:15%, Aprovado:52%, Modificado:20%, Rejeitado:13%) — pendentes concentradas nas 2 últimas semanas; desconto_sugerido_pct: normal(15, 6) limitado a 0–35 (≈ 4% acima do cap de 30% para gerar alertas); confianca_modelo: normal(0.78, 0.09); antecedencia_dias: faixa(1–180); disponibilidade_sugerida: enum(Exibir:85%, Suprimir:15%); prioridade_mix: faixa(1–8); tier_cabine_proxy: enum(Interior:30%, Oceanview:25%, Varanda:35%, Suíte:10%); alerta_guardrail: enum(OK:82%, Acima do cap:5%, Abaixo do piso:8%, Blackout:5%); preco_sugerido: derivado(preco_base * (1 - desconto_sugerido_pct / 100))
**Exemplo de linha**: Aurora Serenade · Atlantica Cruises · Massagem · Caribe Oriental 7n · Varanda · 239,00 · 25,00% · 179,25 · Exibir · 2 · 0,8312 · OK · Pendente Aprovação
<!-- garanta ≥ 30 itens "Pendente Aprovação" para a fila e o badge da sidebar terem o que mostrar na demo -->

### HistoricoDecisao
**Descrição**: Log de auditoria imutável de cada decisão (aprovação, modificação, rejeição) sobre uma recomendação — exibido no painel de detalhe da Fila.
**Papel**: apoio
**Campos principais**: recomendacao_id int, acao enum(Aprovado/Modificado/Rejeitado), desconto_anterior_pct decimal(5,2), desconto_novo_pct decimal(5,2) nullable, comentario text nullable, usuario varchar(100), registrado_em datetime2
**Relacionamentos**: pertence a Recomendacao; pertence a Usuarios (usuario)
**Módulo**: Fila de Governança de Recomendações
**Volumetria de demo**: ≈ 2.040 registros (1 por recomendação decidida)
**Distribuições**: acao: espelha o status da Recomendacao; registrado_em: derivado(gerado_em + 1 a 24 horas)

### GuardrailConfig
**Descrição**: Regras comerciais obrigatórias aplicadas às recomendações — cap de desconto, piso de preço e blackout de parceiros.
**Papel**: apoio
**Campos principais**: categoria_servico_id int, desconto_max_pct decimal(5,2) default 30, piso_preco decimal(15,2), parceiro_id int nullable, blackout_inicio date nullable, blackout_fim date nullable, ativo bit default 1
**Relacionamentos**: pertence a CategoriaServico; pertence a Parceiro (opcional)
**Módulo**: Configuração de Guardrails
**Volumetria de demo**: 20 registros (8 por categoria sem parceiro + 12 blackouts por parceiro)
**Distribuições**: desconto_max_pct: enum(30:60%, 25:25%, 20:15%); piso_preco: derivado(preco_base da categoria * 0.72); ativo: enum(Sim:90%, Não:10%); ≥ 2 blackouts vigentes na data de hoje
**Exemplo de linha**: Massagem · 30,00% · 172,00 · Atlantica Cruises · 20/12/2026 · 05/01/2027 · 1

### ElasticidadePreco
**Descrição**: Coeficientes de elasticidade de preço por categoria de serviço, navio, itinerário e janela de antecedência — calculados externamente (fora do pipeline) e importados apenas para exibição.
**Papel**: fato
**Campos principais**: categoria_servico_id int, classe_navio enum(Aurora/Meridian/Horizon/Solstice), itinerario varchar(100), tier_cabine_proxy enum(Interior/Oceanview/Varanda/Suíte), janela_antecedencia enum(0–30/31–90/91+), coeficiente_elasticidade decimal(8,4), r_squared decimal(5,4), receita_onboard_incremental decimal(15,2), calculado_em datetime2
**Relacionamentos**: pertence a CategoriaServico
**Módulo**: Relatórios de Elasticidade & Interplay
**Volumetria de demo**: 384 registros (8 categorias × 4 classes × 4 tiers × 3 janelas)
**Distribuições**: coeficiente_elasticidade: normal(-1.2, 0.4) — Massagem e Facial mais elásticas (≈ -1,6), Medi-Spa e Acupuntura menos (≈ -0,6); r_squared: normal(0.71, 0.08); receita_onboard_incremental: pareto
**Exemplo de linha**: Massagem · Aurora · Caribe Oriental 7n · Varanda · 31–90 · -1,6120 · 0,7740 · 12.430,00 · 01/10/2026

### RevPathMetrica
**Descrição**: Métricas semanais de RevPATH (receita por hora de tratamento disponível) atual e baseline, por navio/itinerário.
**Papel**: fato
**Campos principais**: navio_id int, itinerario varchar(100), semana date, receita_tratamentos decimal(15,2), horas_disponiveis int, revpath_atual decimal(15,2), revpath_baseline decimal(15,2), variacao_pct decimal(8,4), descontos_utilizados int, descontos_ofertados int
**Relacionamentos**: pertence a Navio
**Módulo**: Dashboard Executivo
**Volumetria de demo**: ≈ 940 registros (12 navios × 78 semanas)
**Distribuições**: semana: sazonal(mensal, pico: dez,jan,jul) + tendencia(+8% ao ano no RevPATH atual a partir do início do piloto); revpath_baseline: normal(134, 18); revpath_atual: derivado(receita_tratamentos / horas_disponiveis); variacao_pct: derivado((revpath_atual - revpath_baseline) / revpath_baseline * 100)
**Exemplo de linha**: Aurora Serenade · Caribe Oriental 7n · 05/10/2026 · 49.392,00 · 336 · 147,00 · 135,60 · 8,41

### InterplayOnboard
**Descrição**: Estudo de interplay entre desconto pré-cruzeiro e gasto onboard para o mesmo hóspede (substituição vs. expansão de carteira).
**Papel**: fato
**Campos principais**: guest_id_hash varchar(64), navio_id int, categoria_servico_id int, data_cruzeiro date, desconto_pre_cruzeiro_pct decimal(5,2), gasto_pre_cruzeiro decimal(15,2), gasto_onboard decimal(15,2), classificacao enum(Substituição/Expansão)
**Relacionamentos**: pertence a Navio; pertence a CategoriaServico
**Módulo**: Relatórios de Elasticidade & Interplay
**Volumetria de demo**: 6.000 registros
**Distribuições**: desconto_pre_cruzeiro_pct: normal(14, 7) limitado a 0–30; gasto_onboard: pareto; classificacao: enum(Expansão:64%, Substituição:36%); data_cruzeiro: sazonal(mensal, pico: dez,jan,jul)
<!-- TODO: confirmar política de anonimização de PII — guest_id_hash é SHA-256 sem possibilidade de reversão -->

### Usuarios
**Descrição**: Usuários do sistema com autenticação JWT
**Papel**: apoio
**Campos principais**: nome varchar(100), email varchar(150) único, senha_hash varchar(255), role enum(admin/gestor_receita/analista_pricing), ativo bit, ultimo_acesso datetime2 nullable
**Relacionamentos**: —
**Módulo**: Administração
**Volumetria de demo**: 12 registros (inclui 1 por role com os e-mails de "Credenciais de demo")
**Distribuições**: role: enum(admin:15%, gestor_receita:35%, analista_pricing:50%); ativo: enum(Sim:90%, Não:10%)

---

## Branding
- **Cor primária**: #1045C8 <!-- TODO: confirmar com o cliente (padrão do pipeline) -->
- **Cor secundária**: #0E9AA7 <!-- sugestão: teal "oceano/spa" — confirmar -->
- **Logo**: (vazio — fallback = badge com iniciais "CC")
- **Logo para fundo escuro**: (vazio)
- **Favicon**: (vazio)
- **Nome na sidebar**: OSW Cruise Control
- **Tagline**: "Descontos de spa com governança e inteligência de receita"
- **Fonte**: inter

---

## Integrações
- **Microsoft Fabric (Lakehouse existente da OSW)**: Database — ingestão de dados de booking e transação onboard (camadas Bronze/Silver/Gold) para alimentar recomendações, elasticidade e RevPATH — TODO: confirmar mecanismo de leitura pela aplicação (view SQL exposta, API ou export)
- **WPBS (plataforma de pré-reserva marítima da OSW)**: API REST — aplicação das decisões aprovadas/modificadas (preço/disponibilidade) de volta ao WPBS — TODO: credenciais e contrato de API pendentes de confirmação com o cliente
- **Motor de Recomendação / MLflow**: API REST interna (`/api/v1/ml/*`) — fonte das recomendações, confiança do modelo e drivers SHAP. Nesta geração os dados vêm do mock volumétrico; o `backend/ml_engine/` da versão anterior pode ser reacoplado após o build.

---

## Requisitos Não-Funcionais
- **Performance**: Consultas < 3s com volume médio de dados (≈ 5.000 recomendações/ano por navio no rollout)
- **Segurança**: JWT com expiração de 8h, senhas com bcrypt, HTTPS em produção; anonimização de PII nos dados de hóspede (responsabilidade do Engenheiro de Dados); logs de auditoria imutáveis (HistoricoDecisao) para toda aprovação/modificação/rejeição
- **Escalabilidade**: Suporte a 30 usuários simultâneos no piloto — TODO: confirmar; rollout para 190+ navios está no Escopo Futuro
- **Disponibilidade**: TODO — não especificado no documento de origem (sugestão: horário comercial US Eastern 8h–20h no piloto)

---

## Escopo Futuro (fora do MVP)
<!-- Itens de fases v1 (avançado) e v2 do documento de origem, movidos para referência futura -->
- **Loop de feedback fechado (7.10)**: ingestão automática de resultados reais de booking (conversão, yield por slot, utilização de desconto) para retreinar os modelos continuamente
- **Detecção de drift e retraining automático (7.10)**: gatilhos automáticos via teste de Kolmogorov-Smirnov quando a performance do modelo ou o comportamento de compra do hóspede se desvia de limiares predefinidos
- **Testes A/B Champion-Challenger (7.10)**: infraestrutura para comparar com segurança candidatos de modelo atualizados contra o baseline em produção
- **Rollout completo de frota e parceiros**: implantação multi-moeda e multi-mercado em todos os parceiros de linhas de cruzeiro habilitados, sem redeploy dos sites dos parceiros (190+ navios)
- **Transferência de conhecimento e handoff operacional**: treinamento das equipes internas de engenharia e analytics da OSW, runbooks operacionais
- **Motor estatístico/ML real**: reacoplar `backend/ml_engine/` (versão anterior) e recalibrá-lo com os 2–3 anos de dados reais de booking do Fabric (pipelines Bronze/Silver/Gold), junto com o time de Data Science
- **Simulador de política de desconto**: tela `simulation` (cap/piso por categoria → impacto projetado em RevPATH via elasticidade) — candidata para a próxima iteração
- **Fases de descoberta/consultoria (v0)**: estudo de demanda e elasticidade, especificação de precificação dinâmica, framework de piloto e modelo de ROI (RFP 7.1, 7.2, 7.5, 7.8) — entregáveis de consultoria, não geram módulos de aplicação diretamente
