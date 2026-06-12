# {NOME_DO_PROJETO}

## Descrição
TODO: Descreva o objetivo principal do sistema (1–3 parágrafos).
TODO: Qual problema ele resolve?
TODO: Quem são os usuários principais?

## Stack Tecnológico
<!-- SEÇÃO FIXA — NÃO ALTERAR. Todo projeto é 100% Python; o pipeline não suporta outras tecnologias. -->
- **Framework Frontend**: Dash 2.14+
- **UI Components**: Dash Bootstrap Components
- **Tabelas**: Dash AG Grid
- **Gráficos**: Plotly
- **Processamento de Dados**: Pandas, NumPy
- **Backend**: FastAPI + SQLAlchemy + Pydantic
- **Banco de dados**: SQL Server / Microsoft Fabric
- **Autenticação**: JWT

## Módulos

### [Módulo 1 — ex.: Cadastros]
**Prioridade**: high
**Descrição**: TODO: Descreva o que este módulo faz.

**Funcionalidades:**
- [F-001] TODO: Nome da feature: Descrição detalhada da funcionalidade
- [F-002] TODO: Nome da feature: Descrição detalhada

**Regras de negócio:**
- [RN-001]: TODO: Descreva a regra de negócio

### [Módulo 2 — ex.: Relatórios]
**Prioridade**: medium
**Descrição**: TODO: Descreva o módulo.

**Funcionalidades:**
- [F-003] TODO: Nome da feature: Descrição

**Regras de negócio:**
- [RN-002]: TODO: Descreva a regra

### Administração
**Prioridade**: low
**Descrição**: Controle de usuários e configurações do sistema.

**Funcionalidades:**
- [F-004] Gestão de usuários: Criar, editar, desativar usuários do sistema
- [F-005] Controle de acesso: Definir roles e permissões por módulo

**Regras de negócio:**
- [RN-003]: Apenas administradores podem criar novos usuários

## Entidades de Dados

- **TODO_Entidade1**: Descrição e módulo relacionado
- **TODO_Entidade2**: Descrição e módulo relacionado
- **Usuarios**: Usuários do sistema com email, senha (hash), nome e role (Módulo: Administração)

## Integrações

- **TODO** (remover se não houver): Tipo (API | Database | File) — Descrição da integração externa

## Requisitos Não-Funcionais

- **Performance**: Consultas < 3s com volume médio de dados
- **Segurança**: JWT com expiração de 8h, senhas com bcrypt, HTTPS em produção
- **Escalabilidade**: Suporte a 20 usuários simultâneos
- **Disponibilidade**: Disponível em horário comercial (8h–18h)
