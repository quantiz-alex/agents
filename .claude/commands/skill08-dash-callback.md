# Skill 08 — Dash Callback Generation Skill

Leia `docs/screens_definition.yaml` e gere os callbacks de uma página Dash.

## Argumento obrigatório

Nome da página a gerar: $ARGUMENTS

Exemplo de uso: `/skill08-dash-callback aprovacao`

## Instruções

1. Leia `docs/screens_definition.yaml` — extraia APENAS a página solicitada.
2. Leia `docs/data_model.yaml` para saber os campos disponíveis.
3. Gere APENAS `frontend/pages/<pagina>/<pagina>_callbacks.py`.
4. Se o arquivo já existir, aplique patch incremental.

## Estrutura do Arquivo Gerado

```python
from dash import Input, Output, State, callback, no_update
import pandas as pd
from frontend.pages.<pagina>.<pagina>_queries import (
    get_<entidade>_data,
)

def register_callbacks() -> None:
    """Registra todos os callbacks da página <pagina>."""

    @callback(
        Output("<pagina>-grid", "rowData"),
        Output("<pagina>-grid", "columnDefs"),
        Input("<pagina>-btn-filtrar", "n_clicks"),
        State("<pagina>-filtro-campo", "value"),
        prevent_initial_call=False,
    )
    def update_grid(n_clicks: int, filtro_valor: str) -> tuple:
        df = get_<entidade>_data(filtro=filtro_valor)
        row_data = df.to_dict("records")
        col_defs = [{"field": c, "headerName": c.title()} for c in df.columns]
        return row_data, col_defs

    # outros callbacks conforme actions da screens_definition
```

## Regras

- Todos os callbacks em uma função `register_callbacks()`.
- `register_callbacks()` é chamada em `app.py`.
- IDs devem ser consistentes com `_page.py`.
- Dados lidos via funções de `_queries.py` (que usa mock_data/).
- Usar `prevent_initial_call=False` para carregar dados na abertura da página.
- Tipagem Python obrigatória em todos os parâmetros e retornos.
- NÃO conectar ao banco.
- NÃO repetir lógica de dados dentro do callback — delegar para `_queries.py`.

## Restrições

- Gerar APENAS o arquivo `_callbacks.py` desta skill.
- Contexto máximo: **8.000 tokens** de saída (anteriormente 2.000).
- Se exceder 8.000 tokens, dividir em chunks com continuação automática.

## Pós-processamento

1. Verificar que arquivo Python é válido (parse)
2. Verificar que `register_callbacks()` existe
3. Verificar que IDs são consistentes com `_page.py`
