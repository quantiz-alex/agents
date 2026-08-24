# Skill — Simulation Pattern

Gera os componentes e callbacks de uma tela de simulação de cenários de pricing.

## Quando usar

Invocada automaticamente pelo `frontend-builder` quando `screen_type: simulation` em `screens_definition.yaml`, ou diretamente:

```
/skill-simulation <nome_pagina>
```

Exemplo: `/skill-simulation simulacao-preco`

---

## O que é uma tela de simulação

Uma tela de simulação permite ao analista:
1. **Definir parâmetros** de um cenário (ex.: margem desejada, desconto máximo, volume estimado)
2. **Executar o cálculo** sem persistir — apenas visualizar o resultado
3. **Comparar cenários** — salvar múltiplos resultados para análise lado a lado
4. **Promover o cenário** — salvar definitivamente e/ou enviar para aprovação

O cálculo **nunca persiste automaticamente** — é sempre uma operação de leitura/projeção.

---

## Fonte da fórmula — `docs/business_logic.yaml`

**A fórmula usada em `calcular_simulacao()` NUNCA é o exemplo genérico abaixo (`margem_desejada`/`desconto_maximo`) — esse exemplo só existe para ilustrar a FORMA do código.** Antes de gerar `_queries.py`:

1. Leia `docs/business_logic.yaml` e localize a regra `logic_type: interactive_formula` vinculada a esta tela/módulo (via `screens_definition.yaml` → `simulation_panel.config.business_logic_rule_id`).
2. Os parâmetros de `calcular_simulacao()` são exatamente `formula.variables[].name` onde `interactive: true` — nem mais, nem menos.
3. O corpo da função implementa literalmente `formula.expression` (e as demais variáveis com `source: entity_field`/`constant` lidas do DataFrame/roadmap).
4. Os campos retornados em `kpis`/`comparativo`/`resumo` são `formula.output_fields[]` — não invente KPIs genéricos como "Receita Atual/Simulada" se a fórmula real produzir outras grandezas (ex.: margem, volume, desconto efetivo).
5. Se `docs/business_logic.yaml` não existir (roadmap legado, gerado antes desta skill) — e SOMENTE nesse caso — use o exemplo abaixo como fallback, e registre um aviso no relatório final sugerindo rodar `/skill-business-logic`.

## Arquivos gerados

```
frontend/pages/<pagina>/
├── <pagina>_queries.py      ← funções de cálculo isoladas (patch incremental)
├── <pagina>_components.py   ← painel de parâmetros + seção de resultado (patch)
├── <pagina>_page.py         ← layout com seção de resultado inicialmente oculta (patch)
└── <pagina>_callbacks.py    ← padrão de simulação + salvar cenário (patch)
```

---

## `_queries.py` — Funções de cálculo

Toda a lógica de cálculo fica em `_queries.py`. O callback chama a função e exibe o resultado.

```python
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_base_simulacao(filtros: dict | None = None) -> pd.DataFrame:
    """Carrega a base de dados para a simulação com filtros opcionais."""
    df = pd.read_csv(DATA_DIR / "<entidade>.csv")
    if filtros:
        for campo, valor in filtros.items():
            if valor is not None:
                df = df[df[campo] == valor]
    return df


def calcular_simulacao(
    df: pd.DataFrame,
    # parâmetros específicos do cenário — definir conforme requirements.yaml
    margem_desejada: float | None = None,
    desconto_maximo: float | None = None,
    # ... demais parâmetros
) -> dict[str, Any]:
    """
    Executa o cálculo do cenário. Retorna dict com:
      - kpis: dict {label: valor_formatado}
      - comparativo: list[dict] — linhas para a tabela comparativa
      - resumo: dict com totais
    NÃO persiste nenhum dado.
    """
    df_sim = df.copy()

    # --- Lógica de cálculo do cenário ---
    # Ajuste conforme as regras de negócio do requirements.yaml
    if margem_desejada is not None:
        df_sim["preco_simulado"] = df_sim["custo"] / (1 - margem_desejada / 100)
    if desconto_maximo is not None:
        df_sim["preco_simulado"] = df_sim["preco_simulado"] * (1 - desconto_maximo / 100)

    df_sim["variacao_pct"] = (
        (df_sim["preco_simulado"] - df_sim["preco_atual"]) / df_sim["preco_atual"] * 100
    ).round(2)

    receita_atual   = (df_sim["preco_atual"]   * df_sim.get("volume", 1)).sum()
    receita_simulada = (df_sim["preco_simulado"] * df_sim.get("volume", 1)).sum()

    return {
        "kpis": {
            "Receita Atual":    f"R$ {receita_atual:,.2f}",
            "Receita Simulada": f"R$ {receita_simulada:,.2f}",
            "Variação Total":   f"{((receita_simulada / receita_atual) - 1) * 100:+.1f}%",
            "Itens Afetados":   str(len(df_sim)),
        },
        "comparativo": df_sim[[
            # colunas relevantes para a tabela comparativa
            "id", "produto", "preco_atual", "preco_simulado", "variacao_pct"
        ]].to_dict("records"),
        "resumo": {
            "receita_atual":    receita_atual,
            "receita_simulada": receita_simulada,
            "variacao_pct":     ((receita_simulada / receita_atual) - 1) * 100,
        },
    }


def salvar_cenario(
    nome_cenario: str,
    parametros: dict,
    resultado: dict,
) -> bool:
    """
    Persiste o cenário salvo em mock_data/cenarios_simulacao.csv.
    Retorna True se salvo com sucesso.
    """
    import csv, os
    from datetime import datetime

    arquivo = DATA_DIR / "cenarios_simulacao.csv"
    existe = arquivo.exists()

    with open(arquivo, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "nome", "parametros", "receita_atual",
            "receita_simulada", "variacao_pct", "criado_em", "status"
        ])
        if not existe:
            writer.writeheader()
        writer.writerow({
            "id":               int(datetime.now().timestamp()),
            "nome":             nome_cenario,
            "parametros":       str(parametros),
            "receita_atual":    resultado["resumo"]["receita_atual"],
            "receita_simulada": resultado["resumo"]["receita_simulada"],
            "variacao_pct":     resultado["resumo"]["variacao_pct"],
            "criado_em":        datetime.now().isoformat(),
            "status":           "Rascunho",
        })
    return True


def listar_cenarios_salvos() -> pd.DataFrame:
    """Lista todos os cenários salvos em mock_data/cenarios_simulacao.csv."""
    arquivo = DATA_DIR / "cenarios_simulacao.csv"
    if not arquivo.exists():
        return pd.DataFrame(columns=[
            "id", "nome", "receita_atual", "receita_simulada", "variacao_pct", "criado_em", "status"
        ])
    return pd.read_csv(arquivo)
```

---

## `_components.py` — Painel de parâmetros + resultado

### Painel de parâmetros de entrada

**Regra de escolha do controle:** se a variável (`formula.variables[]` em `business_logic.yaml`) tem `min`/`max` conhecidos, use `param_slider(...)` de `frontend/components/ui_components.py` (recalcula com tooltip mostrando o valor ao vivo) em vez de `dbc.Input` — reserve `dbc.Input(type="number")` apenas para variáveis sem faixa conhecida. O exemplo abaixo (`margem`/`desconto` com `dbc.Input`) é só a FORMA do código — os nomes/rótulos reais vêm de `formula.variables[]`, não deste exemplo.

```python
def build_painel_parametros(...) -> dbc.Card:
    """Card com campos de configuração do cenário."""
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-sliders me-2"),
            html.Span("Parâmetros do Cenário", className="fw-semibold"),
        ], className="bg-white border-bottom"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label("Margem desejada (%)", className="small fw-semibold"),
                    dbc.Input(
                        id="<pagina>-param-margem",
                        type="number", min=0, max=100, step=0.1,
                        placeholder="Ex.: 35.0",
                    ),
                ], md=3),
                dbc.Col([
                    dbc.Label("Desconto máximo (%)", className="small fw-semibold"),
                    dbc.Input(
                        id="<pagina>-param-desconto",
                        type="number", min=0, max=100, step=0.1,
                        placeholder="Ex.: 10.0",
                    ),
                ], md=3),
                # ... demais parâmetros conforme screens_definition.yaml
                dbc.Col([
                    dbc.Label(" ", className="small"),   # alinha o botão
                    dbc.Button(
                        [html.I(className="bi bi-play-circle me-2"), "Simular"],
                        id="<pagina>-btn-simular",
                        color="primary",
                        className="w-100",
                    ),
                ], md=2),
            ], className="g-3 align-items-end"),
        ], className="py-3"),
    ], className="shadow-sm border-0 mb-3")
```

### Seção de resultado (inicialmente oculta)

```python
def build_secao_resultado() -> html.Div:
    """
    Seção de resultado — inicialmente oculta (display: none).
    O callback altera o style para display: block após a simulação.
    """
    return html.Div([
        html.Hr(className="my-3"),
        html.H6([
            html.I(className="bi bi-graph-up-arrow me-2 text-primary"),
            "Resultado da Simulação",
        ], className="fw-bold text-dark mb-3"),

        # KPIs do resultado
        dbc.Row(id="<pagina>-kpis-simulacao", className="mb-3"),

        # Gráfico comparativo
        dbc.Card([
            dbc.CardHeader("Comparativo Atual × Simulado", className="bg-white border-bottom fw-semibold"),
            dbc.CardBody(
                dcc.Loading(
                    dcc.Graph(id="<pagina>-chart-comparativo", config={"displayModeBar": False}),
                    type="circle", color="#1045C8",
                ),
                className="p-2",
            ),
        ], className="shadow-sm border-0 mb-3"),

        # Tabela comparativa
        build_grid_comparativo(),

        # Ações pós-simulação
        dbc.Row([
            dbc.Col([
                dbc.Input(
                    id="<pagina>-nome-cenario",
                    placeholder="Nome do cenário (ex.: Cenário Base Q3)",
                    className="mb-0",
                ),
            ], md=5),
            dbc.Col([
                dbc.Button(
                    [html.I(className="bi bi-floppy me-2"), "Salvar Cenário"],
                    id="<pagina>-btn-salvar-cenario",
                    color="outline-primary",
                    className="me-2",
                ),
                dbc.Button(
                    [html.I(className="bi bi-send me-2"), "Enviar para Aprovação"],
                    id="<pagina>-btn-enviar-aprovacao",
                    color="success",
                ),
            ], md=7, className="d-flex align-items-center"),
        ], className="g-2 align-items-center"),

    ], id="<pagina>-resultado-simulacao", style={"display": "none"})


def build_grid_comparativo() -> dbc.Card:
    """AG Grid com comparativo atual vs. simulado."""
    column_defs = [
        {"field": "produto",        "headerName": "Produto",           "flex": 2},
        {"field": "preco_atual",    "headerName": "Preço Atual (R$)",  "flex": 1,
         "valueFormatter": {"function": "params.value?.toLocaleString('pt-BR', {minimumFractionDigits: 2})"}},
        {"field": "preco_simulado", "headerName": "Preço Simulado (R$)", "flex": 1,
         "valueFormatter": {"function": "params.value?.toLocaleString('pt-BR', {minimumFractionDigits: 2})"},
         "cellStyle": {"fontWeight": "600", "color": "#1045C8"}},
        {"field": "variacao_pct",   "headerName": "Variação (%)",      "flex": 1,
         "cellStyle": {
             "function": "params.value > 0 ? {color: '#16A34A', fontWeight: '600'} : params.value < 0 ? {color: '#DC2626', fontWeight: '600'} : {}"
         }},
    ]
    return dbc.Card([
        dbc.CardHeader("Detalhamento por Item", className="bg-white border-bottom fw-semibold"),
        dbc.CardBody([
            dag.AgGrid(
                id="<pagina>-grid-comparativo",
                columnDefs=column_defs,
                rowData=[],
                defaultColDef={"resizable": True, "sortable": True, "filter": True, "floatingFilter": True, "suppressMenu": True},
                dashGridOptions={"pagination": True, "paginationPageSize": 20, "rowHeight": 44, "headerHeight": 44, "animateRows": True},
                className="ag-theme-alpine",
                style={"height": "400px"},
            ),
        ], className="p-0"),
    ], className="shadow-sm border-0 mb-3")


def build_kpi_resultado(label: str, valor: str, variacao: str | None = None) -> dbc.Col:
    """Card KPI para resultado de simulação com variação opcional."""
    cor = "primary"
    if variacao:
        try:
            v = float(variacao.replace("%", "").replace("+", ""))
            cor = "success" if v > 0 else "danger" if v < 0 else "secondary"
        except ValueError:
            pass
    return dbc.Col(
        dbc.Card([
            dbc.CardBody([
                html.P(label, className="text-muted small mb-1 text-uppercase fw-semibold",
                       style={"fontSize": "0.7rem", "letterSpacing": "0.05em"}),
                html.H4(valor, className="fw-bold mb-0"),
                html.Small(variacao, className=f"text-{cor} fw-semibold") if variacao else None,
            ], className="py-3"),
        ], className=f"shadow-sm border-0 border-start border-4 border-{cor} h-100"),
        md=3,
    )
```

### Tabela de cenários salvos

```python
def build_grid_cenarios_salvos() -> dbc.Card:
    """AG Grid com histórico de cenários salvos."""
    return dbc.Card([
        dbc.CardHeader([
            html.Span("Cenários Salvos", className="fw-semibold"),
            dbc.Button(
                [html.I(className="bi bi-arrow-clockwise me-1"), "Atualizar"],
                id="<pagina>-btn-refresh-cenarios",
                size="sm", color="outline-secondary", className="ms-auto",
            ),
        ], className="bg-white border-bottom d-flex align-items-center"),
        dbc.CardBody([
            dag.AgGrid(
                id="<pagina>-grid-cenarios",
                columnDefs=[
                    {"field": "nome",             "headerName": "Cenário",        "flex": 2},
                    {"field": "variacao_pct",      "headerName": "Variação (%)",  "flex": 1},
                    {"field": "criado_em",         "headerName": "Criado em",     "flex": 1},
                    {"field": "status",            "headerName": "Status",        "flex": 1,
                     "cellRenderer": "agAnimateShowChangeCellRenderer"},
                ],
                rowData=[],
                defaultColDef={"resizable": True, "sortable": True, "suppressMenu": True},
                dashGridOptions={"pagination": True, "paginationPageSize": 10, "rowHeight": 44},
                className="ag-theme-alpine",
                style={"height": "300px"},
            ),
        ], className="p-0"),
    ], className="shadow-sm border-0 mt-3")
```

---

## `_page.py` — Layout

O layout de simulação tem três seções empilhadas:
1. Painel de parâmetros (sempre visível)
2. Seção de resultado (oculta até executar)
3. Tabela de cenários salvos (sempre visível, atualiza após salvar)

```python
def layout() -> html.Div:
    return html.Div([
        # Toast global
        dbc.Toast(
            id="<pagina>-toast", header="Notificação", is_open=False,
            dismissable=True, duration=4000, color="success",
            style={"position": "fixed", "top": "1rem", "right": "1rem",
                   "zIndex": 9999, "minWidth": "300px"},
        ),
        # dcc.Store para resultado intermediário (evita recalcular no salvar)
        dcc.Store(id="<pagina>-store-resultado"),

        # Header
        html.Div([
            html.H4("Simulação de Cenários", className="fw-bold mb-0 text-dark"),
            html.Small("Configure parâmetros e execute para visualizar o impacto", className="text-muted"),
        ], className="d-flex flex-column mb-3"),

        # Loading wrapper envolve painel + resultado
        dcc.Loading(
            html.Div([
                build_painel_parametros(),
                build_secao_resultado(),
            ]),
            type="circle", color="#1045C8", fullscreen=False,
        ),

        # Tabela de cenários salvos
        build_grid_cenarios_salvos(),

    ], className="page-wrapper px-4 py-3", style={"background": "#f8fafc", "minHeight": "100vh"})
```

---

## `_callbacks.py` — Callbacks de simulação

```python
from dash import Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc, html
from frontend.pages.<pagina>.<pagina>_queries import (
    carregar_base_simulacao,
    calcular_simulacao,
    salvar_cenario,
    listar_cenarios_salvos,
)
from frontend.pages.<pagina>.<pagina>_components import build_kpi_resultado


def register_callbacks() -> None:

    @callback(
        Output("<pagina>-store-resultado", "data"),
        Output("<pagina>-kpis-simulacao", "children"),
        Output("<pagina>-grid-comparativo", "rowData"),
        Output("<pagina>-chart-comparativo", "figure"),
        Output("<pagina>-resultado-simulacao", "style"),
        Output("<pagina>-btn-simular", "disabled"),
        Output("<pagina>-toast", "is_open"),
        Output("<pagina>-toast", "children"),
        Output("<pagina>-toast", "color"),
        Input("<pagina>-btn-simular", "n_clicks"),
        State("<pagina>-param-margem", "value"),
        State("<pagina>-param-desconto", "value"),
        # ... demais parâmetros
        prevent_initial_call=True,
    )
    def executar_simulacao(n_clicks: int, margem, desconto, ...) -> tuple:
        if not n_clicks:
            return no_update, no_update, [], {}, {"display": "none"}, False, False, "", "success"

        if margem is None:
            return (
                no_update, no_update, [], {}, {"display": "none"}, False,
                True, "Informe a margem desejada.", "warning"
            )

        df = carregar_base_simulacao()
        resultado = calcular_simulacao(df, margem_desejada=margem, desconto_maximo=desconto)

        kpi_cards = [
            build_kpi_resultado(label, valor)
            for label, valor in resultado["kpis"].items()
        ]

        # Gráfico comparativo
        import plotly.graph_objects as go
        fig = go.Figure(data=[
            go.Bar(name="Atual",    x=[r["produto"] for r in resultado["comparativo"]],
                                    y=[r["preco_atual"] for r in resultado["comparativo"]],
                   marker_color="#94a3b8"),
            go.Bar(name="Simulado", x=[r["produto"] for r in resultado["comparativo"]],
                                    y=[r["preco_simulado"] for r in resultado["comparativo"]],
                   marker_color="#1045C8"),
        ])
        fig.update_layout(
            barmode="group", template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=30, b=20), height=300,
            font=dict(family="system-ui, sans-serif", size=12, color="#374151"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        return (
            resultado,                      # store
            kpi_cards,                      # KPIs
            resultado["comparativo"],       # grid
            fig,                            # gráfico
            {"display": "block"},           # mostra seção
            False,                          # re-habilita botão
            True, "Simulação concluída.", "success"
        )

    @callback(
        Output("<pagina>-grid-cenarios", "rowData"),
        Output("<pagina>-toast", "is_open", allow_duplicate=True),
        Output("<pagina>-toast", "children", allow_duplicate=True),
        Output("<pagina>-toast", "color", allow_duplicate=True),
        Input("<pagina>-btn-salvar-cenario", "n_clicks"),
        State("<pagina>-nome-cenario", "value"),
        State("<pagina>-store-resultado", "data"),
        State("<pagina>-param-margem", "value"),
        State("<pagina>-param-desconto", "value"),
        prevent_initial_call=True,
    )
    def salvar_cenario_callback(
        n_clicks: int, nome: str, resultado: dict, margem, desconto
    ) -> tuple:
        if not n_clicks or not resultado:
            return no_update, False, "", "success"

        nome_final = nome or f"Cenário {margem}% margem"
        parametros = {"margem_desejada": margem, "desconto_maximo": desconto}
        salvar_cenario(nome_final, parametros, resultado)

        df_cenarios = listar_cenarios_salvos()
        return (
            df_cenarios.to_dict("records"),
            True, f'Cenário "{nome_final}" salvo com sucesso.', "success"
        )

    @callback(
        Output("<pagina>-grid-cenarios", "rowData", allow_duplicate=True),
        Input("<pagina>-btn-refresh-cenarios", "n_clicks"),
        prevent_initial_call=False,
    )
    def carregar_cenarios(n_clicks: int) -> list:
        df = listar_cenarios_salvos()
        return df.to_dict("records")
```

---

## Integração com fluxo de aprovação

Após salvar, o botão "Enviar para Aprovação" usa o **Padrão 3** da skill08:
- `<pagina>-btn-enviar-aprovacao` → callback de envio de aprovação
- O `id` do cenário salvo vem de `<pagina>-grid-cenarios` `selectedRows`
- Status do cenário muda de `Rascunho` para `Pendente Aprovação`

---

## Restrições

- `calcular_simulacao()` NUNCA persiste dados — apenas calcula e retorna.
- O resultado intermediário fica em `dcc.Store` — não recalcular no salvar.
- A seção de resultado começa com `style={"display": "none"}` e é revelada pelo callback.
- Tipagem Python obrigatória em todas as funções.
- Contexto máximo: **8.000 tokens** de saída por arquivo.
