# Índice das bibliotecas do Lighthouse (gerado — não editar à mão)

Use este índice para escolher componentes/funções. Copie o template com `cp`; abra o `.py` só para conferir uma assinatura (Grep pelo nome).

## `components-library.py` → `frontend/components/ui_components.py`
_components-library.py — Biblioteca de componentes reutilizáveis padrão PMZ (v4)._

- `derive_palette(primary, secondary=…)` — Deriva a paleta do projeto a partir da cor primária (e secundária opcional).
- `set_primary_color(primary, secondary=…)` — Aplica a cor primária do projeto aos tokens em runtime (opcional — o Step 0 já substitui no arquivo).
- `format_currency(value, decimals=…)` — Moeda brasileira: R$ 1.234.567 (decimals=0) ou R$ 1.234,56 (decimals=2).
- `format_percent(value, decimals=…, with_sign=…)` — Percentual com vírgula decimal e sinal opcional: +3,7%.
- `format_number(value, decimals=…)` — Número com separador de milhares pt-BR.
- `format_compact(value, prefix=…)` — Formato compacto para KPIs executivos: R$ 1,2M · R$ 48,3K · R$ 950.
- `format_date(value)` — dd/mm/aaaa a partir de ISO string, date ou datetime.
- `icon(icon_name, size=…, className=…)` — Ícone Bootstrap Icons.
- `button(label, primary=…, icon_key=…, danger=…, size=…, **kwargs)` — Botão padrão: primário cheio, ghost (outline) para secundários, vermelho outline para destrutivos.
- `status_badge(value, kind=…)` — Pill de status com cor semântica (kind inferido de STATUS_KIND se omitido).
- `status_badge_style(kind)` — kind: 'pos' | 'neg' | 'warn' | 'info' | 'neutral' -> style de pill (compat v3).
- `stat_pill(text, kind=…, icon_key=…)` — Chip informativo pequeno (ex.: 'dados até 31/08/2026', '1.284 itens afetados').
- `section_title(text, right=…, icon_key=…)` — Título de seção dentro da página (H5) com conteúdo opcional à direita.
- `user_badge(name, role, email=…, compact=…)` — Bloco do usuário logado: avatar com iniciais + nome + badge de role (usado na sidebar/Home).
- `breadcrumb(items)` — Breadcrumb 'Grupo › Tela'. Cada item é str (texto) ou (texto, href).
- `page_header(icon_key, title, subtitle, actions=…, breadcrumb_items=…, meta=…)` — Cabeçalho padrão: [breadcrumb] · ícone + H4 + subtítulo (objetivo do usuário) · ações à direita.
- `app_shell(active_key, icon_key, title, subtitle, content, actions=…, breadcrumb_items=…, meta=…)` — Shell completo da área de conteúdo (a sidebar é renderizada por app.py).
- `app_shell_with_workflow(active_key, icon_key, title, subtitle, content, actions=…, workflow_context=…, breadcrumb_items=…, meta=…)` — app_shell + breadcrumb de jornada e próximos passos quando a tela participa de um workflow.
- `kpi_card(label, atual, simulado, delta_pct, better=…, compare_label=…, icon_key=…)` — KPI de COMPARAÇÃO: valor de referência (simulado/atual) em destaque, baseline ('de {atual}')
- `kpi_simple(label, value, delta_pct=…, better=…, trend=…, icon_key=…, hint=…, color=…)` — KPI SIMPLES: um valor em destaque, opcionalmente com delta % e/ou sparkline de tendência.
- `kpi_row(cards, row_id=…)` — Row responsiva de KPIs: 1 col no mobile, 2 em tablets, todos numa linha (largura igual) a partir de lg.
- `card(title, body, right=…, icon_key=…, body_class=…, card_id=…)` — Card com header (título + conteúdo opcional à direita) e body.
- `home_shortcut_card(icon_key, title, description, href, badge=…)` — Card-atalho da Home: ícone, título, descrição e badge opcional (ex.: '5 pendências').
- `empty_state(title=…, hint=…, icon_key=…, action=…, compact=…)` — Estado vazio explicativo — SEMPRE usar no lugar de grid/gráfico vazio.
- `loading(children, id=…, overlay=…)` — dcc.Loading padronizado (spinner na cor primária, overlay leve). Envolva grids/gráficos atualizados por callback.
- `toast(id, header=…)` — Toast fixo no canto superior direito. Controle com notify() → (is_open, children, icon).
- `notify(message, kind=…)` — Retorna a tupla para os 3 Outputs padrão do toast: (is_open, children, icon).
- `confirm_modal(id, title=…, body=…, confirm_label=…, danger=…, with_comment=…, comment_label=…, comment_required=…)` — Modal de confirmação. IDs gerados: {id} (modal), {id}-confirm, {id}-cancel, {id}-comment (se with_comment).
- `assistant_ask_button(source)` — Abre o Assistente sobre o item deste Detalhar (o item já é o foco do assistente). Callback global em assistant_callbacks.
- `detail_offcanvas(id, title=…, width=…, extra=…)` — Modal central de detalhe (master_detail / approval_queue / clique em linha).
- `detail_field(label, value, mono=…)` — Par rótulo/valor para uso dentro do detail_offcanvas.
- `filter_card(filters, button_id=…, show_button=…, right=…, card_id=…)` — Card de filtros compacto no topo da página.
- `filter_select(id, label, options, value=…, all_label=…, md=…)` — Filtro select padrão em dbc.Col com label. options: lista de str ou {label, value}.
- `filter_date_range(id, label, start=…, end=…, md=…)` — Filtro de período (dcc.DatePickerRange) padronizado.
- `filter_text(id, label, placeholder=…, md=…)` — Filtro texto com debounce (não dispara a cada tecla).
- `chip(label, value, chip_id, removable=…)` — Chip de filtro ativo (ex.: 'Família: Baterias ✕'). chip_id pattern-matching: {"type": "<page>-chip", "field": ...}.
- `chips_row(id, chips=…)` — Container de chips de filtros ativos (drill-down). Preenchido por callback via children.
- `param_slider(id, label, unit=…, min=…, max=…, step=…, default=…, md=…, hint=…)` — Slider de parâmetro para painéis de simulação. Tooltip mostra o valor ao vivo.
- `data_table(df, id, column_types=…, numeric_cols=…, status_col=…, page_size=…, headers=…, row_actions=…, default_sort=…, hide_cols=…, height=…, empty_message=…, selectable=…, pending_values=…)` — AG Grid padrão PMZ — formatos pt-BR, badges reais, ações por linha, linha pendente destacada.
- `quick_filter_input(grid_id, placeholder=…)` — Campo de busca rápida para um data_table. ID: {grid_id}-quick.
- `login_brand_logo(assets_dir, display_name, logo=…)` — Logo grande do login, detectado em cada montagem; fallback com nome da empresa.
- `with_empty_state(component, empty, is_empty)` — Mantém `component` (grid/gráfico) SEMPRE no layout e alterna com `empty_state`.
- `format_value(value, fmt, compact=…, suffix=…)` — Formata um número conforme o `format` do roadmap: currency | percent | number | text.
- `kpi_from_spec(spec, value, baseline=…, trend=…, hint=…, compare_label=…, icon_key=…)` — kind: comparação → kpi_card (exige baseline real); simples → kpi_simple. Nunca kpi_card(x, x, 0).
- `chart_block(graph_id, figure, is_empty, empty_title, empty_hint=…, height=…)` — Gráfico + empty_state alternáveis por callback (IDs {graph_id}-empty / {graph_id}-wrap).
- `chart_outputs(graph_id, allow_duplicate=…)`
- `chart_values(figure, is_empty)`
- `grid_block(grid, grid_id, is_empty, empty_title, empty_hint=…)` — Grid + empty_state alternáveis por callback (IDs {grid_id}-empty / {grid_id}-wrap).
- `grid_outputs(grid_id, allow_duplicate=…)`
- `grid_values(df)`

## `charts-library.py` → `frontend/components/charts.py`
_charts-library.py — Helpers de gráfico no padrão PMZ (Plotly)._

- `bar_ranking(labels, values, value_fmt=…, title=…, height=…)` — Barras horizontais para ranking (ex.: Top fornecedores).
- `bar_vertical(labels, values, title=…, height=…)` — Barras verticais para comparação entre categorias.
- `variation_bars(labels, pcts, title=…, height=…)` — Barras +/- a partir do zero: verde positivo, vermelho negativo.
- `donut(labels, values, title=…, height=…, hole=…)` — Rosca (donut) com legenda externa; sem rótulo sobre as fatias.
- `pie(labels, values, title=…, height=…)` — Pizza simples com legenda externa.
- `line_chart(x, y, title=…, x_label=…, y_label=…, height=…)` — Gráfico de linha para tendências no tempo.
- `multi_line_chart(x, series, title=…, x_label=…, y_label=…, height=…)` — Gráfico de múltiplas linhas para comparação de séries.
- `area_chart(x, y, title=…, x_label=…, y_label=…, height=…)` — Gráfico de área para tendências com volume.
- `scatter_chart(x, y, title=…, x_label=…, y_label=…, height=…)` — Gráfico de dispersão para relação entre duas variáveis.
- `histogram(values, title=…, x_label=…, y_label=…, height=…, nbins=…)` — Histograma para distribuição de valores.
- `waterfall_chart(labels, values, measure=…, value_fmt=…, title=…, height=…)` — Gráfico de ponte (waterfall) — mostra a composição de uma variação em etapas
- `elasticity_curve(preco_range, volume_estimado, preco_atual=…, preco_simulado=…, title=…, x_label=…, y_label=…, height=…)` — Curva de sensibilidade preço x volume/receita (elasticidade de demanda)
- `scenario_comparison_chart(cenarios, metric_field, label_field=…, value_fmt=…, title=…, height=…)` — Barras agrupadas comparando N cenários salvos lado a lado (ui.chart_hint ==
- `heatmap(x_labels, y_labels, values, title=…, value_fmt=…, height=…, colorscale=…)` — Matriz de calor para 2 dimensões × 1 métrica (ex.: receita por família × canal).
- `treemap(labels, parents, values, title=…, height=…, value_prefix=…)` — Treemap para participação hierárquica (ex.: família > fornecedor por receita).
- `combo_bar_line(x, bars, line, bar_name=…, line_name=…, title=…, height=…, bar_fmt=…, line_fmt=…, line_prefix=…)` — Barras (eixo esquerdo) + linha (eixo direito) — ex.: volume × receita por mês.
- `stacked_bars(x, series, title=…, height=…, horizontal=…, percent=…)` — Barras empilhadas por série (ex.: receita por mês × canal). percent=True normaliza para 100%.
- `grouped_bars(x, series, title=…, height=…, value_fmt=…)` — Barras agrupadas — comparação atual × simulado (ou período × período) por categoria.
- `funnel(stages, values, title=…, height=…)` — Funil de etapas (ex.: cenários criados → enviados → aprovados → publicados).
- `gauge(value, target=…, min_value=…, max_value=…, title=…, suffix=…, height=…, better=…)` — Indicador tipo velocímetro — realizado × meta (ex.: margem % vs meta).
- `sparkline(values, color=…, height=…, fill=…)` — Mini-gráfico de tendência sem eixos (para kpi_simple e painel de detalhe).
- `with_selection(fig, selected_label)` — Destaca o item clicado (drill-down) em gráficos de barra: esmaece os demais.
- `diverging_bars(labels, values, value_fmt=…, title=…, height=…)` — Barras horizontais divergentes a partir do zero com cor semântica (verde > 0, vermelho < 0)
- `scatter_by_series(series, title=…, x_label=…, y_label=…, height=…, x_suffix=…, y_prefix=…, colors=…)` — Dispersão com uma cor por série (ex.: Expansão × Substituição). series = {nome: (x, y)}.
- `set_primary_color(color, secondary=…)` — Define a cor primária (e secundária opcional) do projeto para usar nos gráficos.
- `get_empty_state_message(chart_type=…)` — Retorna um dbc.Alert para estado vazio de gráfico.
- `bar_colored(labels, values, colors, horizontal=…, value_fmt=…, title=…, height=…, customdata=…, hover_suffix=…)` — Barras com cor por item (ex.: índice de preço por faixa RN-002). Ordem de entrada preservada.
- `bubble_by_series(series, title=…, x_label=…, y_label=…, height=…, colors=…, hover=…, size_max=…)` — Dispersão com tamanho e cor por série. series = {nome: {"x","y","size","text","customdata","symbol"?}}.
- `add_reference_lines(fig, x=…, y=…, label=…)`
- `empty_figure(height=…)` — Figura neutra usada enquanto o empty_state cobre a área (o ID do gráfico continua no layout).

## `workflow_components.py` → `frontend/components/workflow_components.py`
_Componentes de Workflow e Navegação Contextual_

- `load_workflows()` — Carrega workflows.yaml do projeto.
- `get_workflow_by_id(workflow_id)` — Retorna workflow específico por ID.
- `get_workflows_for_screen(screen_route)` — Retorna lista de workflows que incluem a tela especificada.
- `get_current_step(workflow, step_id)` — Retorna step específico de um workflow.
- `eval_condition(condition, context)` — Avalia condição simples baseada no contexto.
- `workflow_breadcrumb(workflow_id, current_step_id, context=…)` — Breadcrumb que mostra progresso no workflow e permite navegação contextual.
- `workflow_context_actions(workflow_id, current_step_id, context=…, user_role=…)` — Retorna lista de botões de ação contextual baseados no workflow.
- `workflow_status_card(workflow_id, current_step_id, context=…)` — Card mostrando status atual do workflow com progresso visual.
- `get_context_transfer_data(workflow_id, from_step_id, to_step_id, current_context)` — Retorna dados a serem transferidos entre steps do workflow.
- `workflow_selector(current_screen, user_role=…)` — Dropdown para selecionar workflow ativo na tela atual.

## `page_common.py` → `frontend/pages/_common.py`
_Helpers comuns das páginas (copiar para frontend/pages/_common.py e acrescentar o que o projeto precisar, ex.: shell())._

- `event_stores(slug, scenario=…)` — Stores de evento da página + Download do export.
- `nav_event(target, context=…, workflow_id=…)` — Pedido de navegação para guard_routes (o contexto vale só na tela de destino e é limpo ao sair dela).
- `assistant_focus(tipo, entity_id, label, product_id=…, categoria_id=…, snapshot=…)` — Payload do store assistant-select: o item aberto no Detalhar vira o foco do Assistente.
- `assistant_params_store(slug)` — Store com o estado aplicado na tela (filtros/parâmetros) para o Assistente.
- `screen_params(**values)` — Payload do store assistant-params: valores como a tela usa + rótulo legível para ids (canal_id → canal_id_label).
- `export_button(slug, label=…)`
- `hidden(show)`
- `send_excel(df, filename, sheet=…)` — Export Excel de uma aba (requer openpyxl em requirements.txt).
- `send_excel_multi(sheets, filename)` — Export Excel com várias abas (ex.: "Por produto" + "Combinações").
- `opt_value(v)` — Normaliza valor de select ('' → None).

## `api_client.py` → `frontend/api_client.py`
_api_client.py — Cliente HTTP do frontend para a API FastAPI do projeto._

- `use_api()` — True quando USE_API=true no ambiente — decide entre CSV e API nas queries.
- `set_token(token)`
- `login(email, senha)` — POST /auth/login → guarda o token e retorna {access_token, token_type, expires_in}.
- `api_get(path, params=…, token=…)`
- `api_post(path, payload, token=…)`
- `api_put(path, payload, token=…)`
- `api_delete(path, token=…)`
- `api_health()` — GET /health (fora de /api/v1) — usado pela Home para exibir o chip 'API online/offline'.

## `demo_scenario.py` → `frontend/components/demo_scenario.py`
_Estado de cenário mock por sessão. Copiar para frontend/components/demo_scenario.py._

- `fingerprint(params, scope)`
- `new_session(parameters, scope=…)`
- `transition(state, event)` — Eventos serializados por um único callback do shell.
- `scenario_for_view(state, view=…)` — Comparativo de simulação usa draft; telas comuns usam applied.
- `dispatch(state, event, calculate)` — Entrada do shell: recalcula preview com motor real, ignorando resultados do cliente.

## `pricing_assistant.py` → `frontend/services/pricing_assistant.py`
_Assistente orientado a catálogo — motor local (sem rede)._

- `normalize(text)`
- `context_fingerprint(context)` — Revisão/visão do cenário só contam em telas de cenário; fora delas não invalidam ações.
- `validate_catalog(catalog, handlers)`
- `entity_type(context)`
- `available(catalog, context)` — Análises da tela atual (`pages`). As de item em foco (`entity`) exigem também o foco desse tipo — e só valem nas telas listadas,
- `options_for(analyses)`
- `match(question, analyses)` — (análise escolhida | None, candidatos ordenados). Escolhe só com score alto e sem empate próximo.
- `scope_vocabulary(catalog, extra_terms=…)`
- `in_scope(question, vocab, has_history=…)` — Trava barata (sem API): fora do escopo só quando a pergunta não tem NENHUM termo do domínio.
- `out_of_scope_response(catalog, context)`
- `missing_message(missing, page)`
- `run_analysis(catalog, handlers, analysis, context)` — Executa UMA análise do catálogo com o contexto do servidor e devolve a resposta padronizada.
- `answer(question, catalog, handlers, context, analysis_id=…)` — Motor local: id explícito (sugestão clicada) ou pergunta casada por similaridade com perguntas/aliases/título.
- `proposal_event(response, context, event_id, action_id)` — Intenção de rascunho para o dispatcher; jamais aplica o cenário.
- `append_history(history, question, response, meta=…, limit=…)` — Histórico para dcc.Store(session). Cada turno guarda tela/produto/motor; só o último mantém a proposta completa.

## `assistant_llm.py` → `frontend/services/assistant_llm.py`
_Motor do Assistente de Pricing com Claude (opcional)._

- `enabled()`
- `tool_definitions(analyses)` — Uma ferramenta por análise disponível na tela, sem parâmetros (o contexto vem do servidor).
- `answer(question, catalog, handlers, context, history=…, page_label=…, product_label=…, client=…)` — Responde com Claude + ferramentas do catálogo. Levanta LLMUnavailable em qualquer falha da API.

## `assistant_detail.py` → `frontend/services/assistant_detail.py`
_Ferramentas de DETALHE do Assistente — analisam o item aberto no "Detalhar" de qualquer tela._

- `detalhe_produto(ctx)` — EXEMPLO (tela-tabela por produto). Mesmas consultas da Tabela Vigente: base (cenário aplicado + aprovados) → recalcular → por_produto/variacoes.
- `detalhe_combinacao(ctx)` — A simulação da Configuração usa parâmetros ainda não salvos (controles da tela). Por isso a tela grava no foco o retrato

## `assistant_pages.py` → `frontend/services/assistant_pages.py`
_Análises do Assistente POR TELA — cada handler chama as mesmas funções `*_queries.py` da tela, com o estado atual dela._

- `dash_resumo(ctx)` — KPIs do Dashboard: dashboard_queries.calcular_kpis(período e filtros da tela).
- `dash_categorias(ctx)` — Gráfico receita × margem por categoria: dashboard_queries.agregar_categoria.
- `dash_top_clientes(ctx)` — Top clientes do Dashboard: dashboard_queries.agregar_top_clientes.
- `dash_mix_canal(ctx)` — Mix por canal do Dashboard: dashboard_queries.agregar_mix_canal (receita).
- `reforma_produto(ctx)` — KPIs do Simulador Tributário: simular(produto, ano e sliders da tela).
- `reforma_transicao(ctx)` — Linha do tempo 2026–2033 do Simulador: maior salto anual de PPC e de alíquota efetiva.
- `faixas_desconto(ctx)` — KPIs da Política de Descontos: kpis(simular(faixas em edição na tela, vigentes)).
- `politica_segmento(ctx)` — Gráfico de impacto por segmento: impacto_segmento(simular(...)).
- `politica_distribuicao(ctx)` — Gráfico de distribuição por faixa (Volume, Mix, Fidelidade): distribuicao(simular(...)["sim"], tipo).

## `assistant_callbacks.py` → `frontend/assistant_callbacks.py`
_Callbacks globais do Assistente de Pricing — registrados UMA vez pelo app.py._

- `catalog()`
- `page_label(page)`
- `focus_label(context)` — Rótulo do item aberto no Detalhar (ex.: "Pedido PED-0001 · Mercado X").
- `product_label(context)`
- `build_context(pathname, user, scenario, session, selects, select_ids, params=…, params_ids=…)` — Contexto do assistente: tela, usuário, item em foco (assistant-select) e estado da tela (assistant-params: filtros/parâmetros).
- `scope_vocab()` — Termos do domínio: glossário + catálogo + nomes reais de categorias, produtos, SKUs, canais, regiões e segmentos.
- `responder(pergunta, analysis_id, context, history)` — Sugestão/opção clicada → análise direta. Texto livre: trava de escopo (sem custo) → Claude (se ativo), com queda para o motor local.
- `register_assistant_callbacks()`

## `pricing_assistant_components.py` → `frontend/components/pricing_assistant_components.py`
_Painel global do Assistente de Pricing (montado uma vez no shell; oculto no login)._

- `assistant_panel(ai_enabled=…)` — Montar uma vez no shell; callbacks registrados uma vez em frontend/assistant_callbacks.py.
- `focus_chip(label)` — Item aberto no Detalhar que o assistente está considerando.
- `suggestion_buttons(items)`
- `render_messages(history, current_fp)` — Turnos antigos recolhidos (pergunta + tela); o último aberto com tabela/ações. Ações só ativas se o contexto não mudou.
