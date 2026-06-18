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

## Perfis de Acesso
<!-- Roles padrão do pipeline — ajustar nomes/permissões conforme o cliente -->
- **admin**: acesso total — gerenciar usuários, configurações e todos os módulos
- **supervisor**: visualizar tudo, simular cenários, aprovar e rejeitar pendências
- **analista**: criar, editar, simular e enviar para aprovação — não aprova nem exclui

---

## Módulos

### [Módulo 1 — ex.: Dashboard Comercial]
**Prioridade**: high
**Tipo de tela**: dashboard
<!-- Tipos: dashboard (KPIs+gráficos), grid (tabela+filtros), form (cadastro), report (relatório), mixed -->
**Ícone Bootstrap**: speedometer2
<!-- Ícones: https://icons.getbootstrap.com — ex: speedometer2, graph-up, table, people, gear, box-seam -->
**Descrição**: TODO: O que este módulo exibe e qual decisão ele apoia.

**Componentes visuais:**
- **KPIs:** TODO: liste as métricas (ex: Total pedidos do mês, Receita acumulada, Margem média %)
- **Gráfico principal:** TODO: tipo (bar | line | area | pie | scatter) — o que ele mostra (ex: line — evolução de receita por semana)
- **Gráfico secundário (opcional):** TODO: tipo — o que mostra
- **Grid/Tabela:** TODO: entidade exibida, colunas mais importantes
- **Filtros:** TODO: campo (tipo) — ex: data_pedido (date_range), status (select: Ativo/Inativo), cliente_nome (text)

**Funcionalidades:**
- [F-001] TODO: Nome da feature — descrição detalhada
  - Ações disponíveis: [visualizar | exportar-excel | drill-down]
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
**Tipo de tela**: grid
**Ícone Bootstrap**: tag
**Descrição**: TODO

**Componentes visuais:**
- **Grid/Tabela:** TODO: entidade, colunas (ex: produto, preço_atual, preço_sugerido, variação_%)
- **Filtros:** TODO: campo (tipo) — ex: categoria (select), fornecedor (select), data_vigencia (date_range)
- **Formulário de criação/edição (modal):** TODO: campos do form — ex: produto_id (select), preco decimal, data_inicio date

**Funcionalidades:**
- [F-003] TODO: Nome — descrição
  - Ações: [criar, editar, excluir | aprovar, rejeitar | exportar-excel | importar-csv]
- [F-004] TODO: Nome — descrição

**Regras de negócio:**
- [RN-002]: TODO (ex: preço não pode ser menor que custo + margem mínima de 10%)

**Acesso por role:**
- admin: full
- TODO_role2: [criar, editar, aprovar]
- TODO_role3: [visualizar, exportar-excel]

---

### [Módulo 3 — ex.: Relatórios]
**Prioridade**: medium
**Tipo de tela**: report
**Ícone Bootstrap**: file-earmark-bar-graph
**Descrição**: TODO

**Componentes visuais:**
- **Filtros:** TODO: campo (tipo)
- **Gráfico:** TODO
- **Grid/Tabela exportável:** TODO: colunas do relatório

**Funcionalidades:**
- [F-005] TODO: Nome — descrição
  - Ações: [visualizar, exportar-excel, exportar-pdf]

**Regras de negócio:**
- [RN-003]: TODO

**Acesso por role:**
- admin: full
- TODO_role2: [gerar, exportar]

---

### Administração
**Prioridade**: low
**Tipo de tela**: grid
**Ícone Bootstrap**: people
**Descrição**: Controle de usuários do sistema.

**Componentes visuais:**
- **Grid/Tabela:** lista de usuários — nome, email, role, ativo
- **Filtros:** role (select), ativo (select: Sim/Não)
- **Formulário:** nome (text), email (text), role (select), senha temporária (text)

**Funcionalidades:**
- [F-006] Gestão de usuários: criar, editar e desativar usuários
  - Ações: [criar, editar, desativar]

**Regras de negócio:**
- [RN-004]: Somente admin pode criar ou desativar usuários
- [RN-005]: Email deve ser único no sistema

**Acesso por role:**
- admin: full

---

## Entidades de Dados
<!-- Para cada entidade: descrição + campos principais + relacionamentos -->
<!-- Tipos de campo: varchar(N), nvarchar(N), int, bigint, decimal(P,S), float, date, datetime2, bit, text -->
<!-- Enum: listar os valores possíveis -->

### {Entidade1}
**Descrição**: TODO — o que representa, para qual módulo serve
**Campos principais**: TODO — ex: nome varchar(100), valor decimal(15,2), status enum(Ativo/Inativo/Pendente), data_inicio date
**Relacionamentos**: TODO — ex: pertence a {Entidade2}, tem muitos {Entidade3}
**Módulo**: TODO

### {Entidade2}
**Descrição**: TODO
**Campos principais**: TODO
**Relacionamentos**: TODO
**Módulo**: TODO

### Usuarios
**Descrição**: Usuários do sistema com autenticação JWT
**Campos principais**: nome varchar(100), email varchar(150) único, senha_hash varchar(255), role enum(admin/TODO_role2/TODO_role3), ativo bit
**Relacionamentos**: —
**Módulo**: Administração

---

## Branding
<!-- Identidade visual do cliente — personaliza design system e sidebar -->
- **Cor primária**: #3b82f6
- **Logo**: (caminho relativo ex: assets/logo.png — deixar vazio se não tiver)
- **Nome na sidebar**: (nome curto — padrão: nome do projeto)

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
