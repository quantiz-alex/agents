# Skill — Roadmap Template & Validator

Valida o formato do `roadmap.md` e, se não existir, gera um template preenchível baseado nas informações fornecidas.

## Quando Usar

- Antes de iniciar o pipeline (`/lighthouse`)
- Quando o usuário quer criar um novo projeto do zero
- Para verificar se um `roadmap.md` existente está no formato correto

## Argumento opcional

`$ARGUMENTS` — nome do projeto (ex.: `"Sistema de Vendas"`). Se vazio, gera template genérico.

---

## Schema Obrigatório do roadmap.md

O `roadmap.md` DEVE seguir esta estrutura mínima para ser aceito pelo pipeline:

```markdown
# [Nome do Projeto]

## Descrição
[Descrição geral do sistema em 1–3 parágrafos]

## Stack Tecnológico
- **Frontend**: Dash + Plotly + AG Grid
- **Backend**: FastAPI + SQLAlchemy
- **Banco de dados**: SQL Server / Microsoft Fabric
- **Autenticação**: JWT

## Módulos

### [Nome do Módulo]
**Prioridade**: high | medium | low
**Descrição**: [O que este módulo faz]

**Funcionalidades:**
- [Feature 1]: [Descrição]
- [Feature 2]: [Descrição]

**Regras de negócio:**
- [RN-01]: [Regra]

### [Próximo Módulo]
...

## Entidades de Dados

- **[Entidade]**: [Descrição breve e módulo ao qual pertence]
- **[Entidade]**: ...

## Integrações

- **[Nome]**: [Tipo: API | Database | File] — [Descrição]

## Requisitos Não-Funcionais

- **Performance**: [Ex.: Consultas < 2s com 100k registros]
- **Segurança**: [Ex.: JWT com expiração de 8h, HTTPS obrigatório]
- **Escalabilidade**: [Ex.: Suporte a 50 usuários simultâneos]
```

---

## Campos Obrigatórios

| Campo | Localização | Consequência se ausente |
|---|---|---|
| `# [Nome do Projeto]` | Linha 1 do arquivo | `build` falha no Step 0 |
| `## Módulos` | Seção presente | Nenhuma tela gerada |
| `## Entidades de Dados` | Seção presente | Modelo de dados vazio |
| Pelo menos 1 módulo com features | Em `## Módulos` | `requirements.yaml` inválido |
| Pelo menos 1 entidade | Em `## Entidades de Dados` | `data_model.yaml` vazio |

---

## Ações desta Skill

### Modo Validação (arquivo existe)

1. Verificar que `roadmap.md` existe e não está vazio
2. Extrair `project.name` do `# [Título]` da primeira linha
3. Verificar presença das seções obrigatórias
4. Verificar que há pelo menos 1 módulo com features listadas
5. Verificar que há pelo menos 1 entidade definida
6. Gerar `validation_reports/step_roadmap.yaml` com resultado
7. Se válido → exportar `project.name` para uso nos próximos steps

### Modo Geração de Template (arquivo não existe)

Se `roadmap.md` não existir, criar template preenchível:

```markdown
# {NOME_DO_PROJETO}

## Descrição
TODO: Descreva o objetivo principal do sistema.
TODO: Qual problema ele resolve?
TODO: Quem são os usuários principais?

## Stack Tecnológico
- **Frontend**: Dash + Plotly + AG Grid
- **Backend**: FastAPI + SQLAlchemy
- **Banco de dados**: SQL Server / Microsoft Fabric
- **Autenticação**: JWT

## Módulos

### [Módulo 1 — ex.: Cadastros]
**Prioridade**: high
**Descrição**: TODO: Descreva o módulo.

**Funcionalidades:**
- [F-001] TODO: Nome da feature: Descrição detalhada
- [F-002] TODO: Nome da feature: Descrição detalhada

**Regras de negócio:**
- [RN-001]: TODO: Descreva a regra

### [Módulo 2 — ex.: Relatórios]
**Prioridade**: medium
**Descrição**: TODO

**Funcionalidades:**
- [F-003] TODO

## Entidades de Dados

- **TODO_Entidade1**: Descrição e módulo relacionado
- **TODO_Entidade2**: Descrição e módulo relacionado

## Integrações

- **TODO** (remover se não houver): API — Descrição da integração

## Requisitos Não-Funcionais

- **Performance**: Consultas < 3s com volume médio de dados
- **Segurança**: JWT com expiração de 8h, roles de acesso
- **Escalabilidade**: Suporte a 20 usuários simultâneos
```

---

## Extração de `project.name`

Após validação bem-sucedida, salvar em `.build/project.json`:

```json
{
  "name": "Nome do Projeto Lido do Roadmap",
  "name_slug": "nome-do-projeto",
  "name_class": "NomeDoProjeto",
  "version": "0.1.0",
  "extracted_at": "2024-06-03T15:30:00Z"
}
```

Este arquivo é lido por:
- `skill-shell.md` (app.py, sidebar) e `backend-builder` (`backend/main.py`, `README.md`)
- `skill-env.md` para o `.env`
- `skill-auth.md` para configurar o app JWT

**Regras de derivação:**
- `name`: primeira linha do roadmap sem o `# `
- `name_slug`: lowercase, espaços → `-`, sem acentos
- `name_class`: PascalCase, sem espaços

---

## Saída

```yaml
# validation_reports/step_roadmap.yaml
validation:
  step: roadmap
  timestamp: datetime
  status: success | error

project:
  name: string
  slug: string

checks:
  - id: roadmap_exists
    status: pass | fail
  - id: has_title
    status: pass | fail
  - id: has_modules
    status: pass | fail
  - id: has_entities
    status: pass | fail
  - id: min_one_feature
    status: pass | fail

errors:
  - severity: critical
    message: string
    suggestion: string
```

---

## Modo de Uso

```
/skill-roadmap-template
/skill-roadmap-template "Sistema de Gestão Comercial"
```

## Pós-processamento

1. Se válido → salvar `.build/project.json` e avançar
2. Se inválido → exibir erros com sugestões e PARAR
3. Se template gerado → exibir instruções de preenchimento e AGUARDAR usuário completar o roadmap
