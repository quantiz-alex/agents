# Regras centrais do Lighthouse (fonte única)

Todo agente lê este arquivo primeiro. Os demais arquivos **referenciam** estas regras em vez de repeti-las. Se algum arquivo contradisser este, vale este.

## 1. Caminhos e cópias (economia de tokens)

- **`$LH`** é a pasta `.claude` do framework. Resolva assim, uma vez por execução:
  1. variável de ambiente `LIGHTHOUSE_HOME`;
  2. senão, `.build/project.json → lighthouse_home`, gravado pelo `/project-init`;
  3. senão, `../.claude`.

  Nas instruções, `../.claude/...` significa `$LH/...`.
- **Copiar template = Bash `cp`.** Nunca use Read + Write para copiar: um template de 40 KB lido e reescrito custa cerca de 20K tokens.
  - Primeira vez: `cp "$LH/templates/X" destino`.
  - Atualização: `cp -u`, ou aplicar um patch pontual com Edit preservando customizações do projeto.
- **Não leia código de template para "entender" a biblioteca.** Use o índice de funções em `$LH/templates/LIBRARY_INDEX.md`. Abra o `.py` só para conferir a assinatura de uma função específica (Grep pelo nome).
- **Leia por recorte, não por arquivo inteiro.** Os YAMLs do projeto passam de 100 KB.
  - Use `docs/handoff.md`, que é o resumo do data-engineer.
  - Use `docs/screens/<slug>.yaml`, o recorte por tela.
  - Para o resto, faça Grep pela chave e Read com `offset`/`limit`.

## 2. Stack fixo
100% Python.
- **Frontend:** Dash 2.14+, Dash Bootstrap Components, Dash AG Grid, Plotly, Pandas e NumPy.
- **Backend:** FastAPI, SQLAlchemy, Pydantic v2 e python-jose/bcrypt.
- **Assistente:** SDK `anthropic`, opcional em tempo de execução.
- **Excel:** `openpyxl`.
- **Fora do stack:** React, Streamlit, Node, CSS fora de `assets/theme.css` e matplotlib na UI.

## 3. Decisões padronizadas (resolvem contradições antigas)

| Tema | Regra |
|---|---|
| Roteamento | `use_pages=False`. `render_page_content` explícito. **Nunca** `register_page` |
| Navegação e URL | Só `guard_routes` escreve `url.pathname` e `workflow-context`. O contexto de um atalho (ex.: `{sku}`) é **limpo ao navegar para outra tela** |
| Rota pós-login | `/home` |
| Sidebar | Branca, 240 px, grupos, usuário + Sair, badges |
| Raiz da página | `app_shell(...)` / `app_shell_with_workflow(...)`. Nada de `html.Div`/`dbc.Container` manual nem hex em página |
| Credenciais demo | `<role>@<empresa>.com` / senha `demo` (roles: admin, supervisor, analista) |
| Estado do demo | Cenário, aprovações e cadastros vivem na **sessão** (`dcc.Store`). Nunca escrever CSV |
| Mock | Sempre pelo motor volumétrico (`scripts/mock_generator.py`). Nada de linhas digitadas à mão |
| Detalhar | **Modal central** `detail_offcanvas(id, title, width, extra=)`. Título por `Output(f"{id}-title","children")`. Conteúdo fixo só por `extra=` (nunca `oc.children = [...]`) |
| Ações de linha | Uma ação "Detalhar" quando o detalhe já contém simulador. Não duplicar com "Simular" |
| Volume | **Nunca** arredondar volume por linha (combinação/item). Arredondar só na exibição de totais. Frações por combinação somam o total do produto |
| Exportação | `send_excel` com `openpyxl` em `requirements.txt` |
| Textos YAML | Listas de texto **sempre entre aspas** (`"× 0,75"` sem aspas vira número) |
| Saída por arquivo | No máximo cerca de 8.000 tokens por escrita. Divida arquivos grandes |

## 4. Assistente de Pricing (todo projeto tem)
- **Gerado na Fase 2 pelo frontend-builder**, conforme `$LH/commands/skill-pricing-assistant.md`.
- **Modo híbrido:**
  - Com `ANTHROPIC_API_KEY`, o Claude usa as análises do catálogo como ferramentas sem parâmetros. O contexto é injetado pelo servidor.
  - Sem a chave, ou se a API falhar, entra o motor local: busca aproximada mais trava de escopo.
- **Análises:**
  - Cada tela tem 2 a 5 análises próprias.
  - Toda análise chama as **mesmas funções `*_queries.py` da tela**, com o estado dela (stores `assistant-select` = item em foco e `assistant-params` = filtros/parâmetros).
- **Ações:**
  - Só "Abrir" e "Simular proposta" (rascunho).
  - Nunca aplica nem aprova.

## 5. Cenário demo compartilhado
Os parâmetros de configuração (arquitetura, índices) que afetam outras telas passam por um motor puro compartilhado mais os stores de sessão, conforme `$LH/commands/skill-demo-scenario.md`. Todo consumidor recalcula por linha antes de agregar e não copia números entre páginas.

## 6. Protocolo de execução
- **Estado:** detecte o que já existe no disco e gere só o que falta. Ao atualizar, aplique patch e preserve as customizações.
- **Checkpoint:** após cada passo, registre em `.build/checkpoints/` e uma linha `✓ [passo] → [arquivos]`.
- **Validação barata primeiro:** `py_compile`, import e Grep de IDs, via Bash. Só a saída entra no contexto.
- **Loops de correção:** no máximo 3 tentativas por problema. Depois, reporte com o erro resumido.
- **Relatório final:** sempre `STATUS: success | partial | failed | blocked`, mais arquivos gerados e avisos.
