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
  Para retomar o build existente, navegue até o diretório e execute /lighthouse ou /build.
```

### 3. Criar Estrutura de Diretórios

Criar `../<project_slug>/` com:

```
<project_slug>/
  docs/
  database/
  mock_data/
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
    backend/
    frontend/
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

### 3.5. Copiar Bibliotecas do Dash Starter

Copiar os arquivos do dash-starter template para o novo projeto:

1. Copiar `.claude/templates/components-library.py` para `../<project_slug>/frontend/components/ui_components.py`
2. Copiar `.claude/templates/charts-library.py` para `../<project_slug>/frontend/components/charts.py`
3. Copiar `.claude/templates/dash-starter/assets/theme.css` para `../<project_slug>/assets/theme.css`
4. Criar pasta `../<project_slug>/assets/icons/` (vazia, para ícones Bootstrap Icons)

**Nota:** As cores primárias serão ajustadas pelo frontend-builder no Step 0 ao ler `.build/project.json`.

### 4. Gerar `roadmap.md` a partir do Template

1. Ler o template em `.claude/templates/roadmap-template.md` (fonte única — NÃO duplicar o conteúdo aqui).
2. Substituir `{NOME_DO_PROJETO}` por `project_name`.
3. Escrever em `../<project_slug>/roadmap.md`.

### 5. Registrar em PROJECTS.md

Ler `.claude/PROJECTS.md` (criar com o cabeçalho padrão se não existir). Adicionar linha na tabela de Projetos Ativos (e remover a linha placeholder "_(nenhum projeto ainda...)_" se presente):

```markdown
| {project_name} | {project_slug} | 🟡 Aguardando roadmap | {data_atual} |
```

### 6. Exibir Próximos Passos

```
✅ Projeto '{project_name}' criado!

📁 Localização: ../{project_slug}/
📚 Bibliotecas UI/UX copiadas: ui_components.py, charts.py, theme.css

Próximos passos:
  1. Editar ../{project_slug}/roadmap.md — preencher todos os TODO
  2. cd ../{project_slug}
  3. /lighthouse        ← build delegado por subagents (recomendado)
     /build             ← pipeline sequencial (fallback)
     /build-parallel    ← pipeline paralelo (fallback)

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
