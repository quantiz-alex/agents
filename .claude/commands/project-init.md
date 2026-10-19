# /project-init — Inicializador de Novo Projeto

Cria a estrutura completa de diretórios para um novo projeto e gera o `roadmap.md` a partir do template compartilhado.

## Argumento obrigatório

`$ARGUMENTS` — nome do projeto em linguagem natural (ex.: `Sistema de Gestão Comercial`)

Se vazio → exibir instruções de uso e exemplos, depois **PARAR**.

---

## Ações

### 1. Derivar Metadados

A partir de `$ARGUMENTS`, derivar:
- `project_name`: o argumento como está (ex.: `Sistema de Gestão Comercial`)
- `project_slug`: lowercase, espaços → `-`, remover acentos e caracteres especiais (ex.: `sistema-de-gestao-comercial`)
- `project_class`: PascalCase, sem espaços (ex.: `SistemaDeGestaoComercial`)

### 2. Verificar se Projeto Já Existe

Verificar se o diretório `../<project_slug>/` já existe (relativo ao diretório `.claude`).
Se já existir → exibir aviso e **PARAR**:
```
⚠ Projeto '<project_slug>' já existe em ../<project_slug>/
  Para retomar o build existente, navegue até o diretório e execute /lighthouse.
```

### 3. Criar Estrutura de Diretórios

Criar `../<project_slug>/` com:

```
<project_slug>/
  docs/
  database/
  mock_data/
  scripts/                  ← mock_generator.py, generate_mock.py, ui_smoke.py (copiados nas skills)
  frontend/
    pages/
    components/
  backend/
    models/
    schemas/
    repositories/
    services/
    api/
      routes/
  tests/
    backend/                ← pytest da API (conftest próprio com FastAPI/SQLAlchemy)
    frontend/               ← pytest do Dash (queries/components/callbacks/assistente)
    e2e/
      cypress/
        e2e/
        fixtures/
        support/
    integration/
  validation_reports/
  assets/
    icons/
  .build/
    checkpoints/
```

### 3.5. Registrar o caminho do framework

Criar `../<project_slug>/.build/project.json` (ou acrescentar ao existente) com `"lighthouse_home": "<caminho absoluto desta pasta .claude>"` — os agentes resolvem `$LH` por ele (`rules/core.md` §1), mesmo quando o projeto fica fora da pasta do framework.

Criar a pasta `../<project_slug>/assets/icons/`. **Não copiar bibliotecas aqui**: o frontend-builder copia tudo no Step 0 com `cp` (evita cópia dupla).

### 4. Gerar `roadmap.md` a partir do Template

1. `cp .claude/templates/roadmap-template.md ../<project_slug>/roadmap.md` (Bash — não ler/reescrever o template).
2. Substituir `{NOME_DO_PROJETO}` por `project_name` com `sed -i` (ou Edit pontual).

### 5. Registrar em PROJECTS.md

Ler `.claude/PROJECTS.md` (criar com o cabeçalho padrão se não existir). Adicionar linha na tabela de Projetos Ativos (e remover a linha placeholder "_(nenhum projeto ainda...)_" se presente):

```markdown
| {project_name} | {project_slug} | 🟡 Aguardando roadmap | {data_atual} |
```

### 6. Exibir Próximos Passos

```
✅ Projeto '{project_name}' criado!

📁 Localização: ../{project_slug}/

Próximos passos:
  1. Editar ../{project_slug}/roadmap.md — preencher todos os TODO
  2. cd ../{project_slug}
  3. /lighthouse        ← build delegado por subagents

  Ou pedir um agente específico em linguagem natural:
  "gere a camada de dados", "regenere o frontend", "crie os testes"

💡 O roadmap.md é o único arquivo que você escreve — todo o resto é gerado.
💡 As bibliotecas UI/UX garantem consistência visual automática em todas as páginas.
```

---

## Uso

```
/project-init Sistema de Gestão Comercial
/project-init Plataforma de Precificação
```

## Notas

- O diretório do projeto é criado como **irmão** do diretório `.claude` (um nível acima)
- O template do roadmap vive em `.claude/templates/roadmap-template.md` — edite lá para mudar o padrão de todos os projetos futuros
- A entidade `Usuarios` vem no template pois é necessária para autenticação JWT
