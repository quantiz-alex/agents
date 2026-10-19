"""Helpers comuns das páginas (copiar para frontend/pages/_common.py e acrescentar o que o projeto precisar, ex.: shell()).

Contrato de eventos para o shell:
  {"type": "nav-event", "page": SLUG}            → guard_routes (único dono de url/workflow-context)
  {"type": "demo-session-event", "page": SLUG}   → dono único de demo-session
  {"type": "demo-scenario-event", "page": SLUG}  → dono único de demo-scenario/demo-active
  {"type": "assistant-select", "page": SLUG}     → item em foco do Assistente (Detalhar)
  {"type": "assistant-params", "page": SLUG}     → filtros/parâmetros aplicados na tela (Assistente)
"""
from __future__ import annotations

import io
import uuid
from typing import Any

import pandas as pd
from dash import dcc

from frontend.components.ui_components import button

_LABEL_TABLE = {"canal_id": "canal", "regiao_id": "regiao", "segmento_id": "segmento", "categoria_id": "categoria", "ambiente_id": "ambiente"}


def event_stores(slug: str, scenario: bool = False) -> list:
    """Stores de evento da página + Download do export."""
    stores = [dcc.Store(id={"type": "nav-event", "page": slug}, storage_type="memory"),
              dcc.Store(id={"type": "demo-session-event", "page": slug}, storage_type="memory"),
              dcc.Download(id=f"{slug}-download")]
    if scenario:
        stores.append(dcc.Store(id={"type": "demo-scenario-event", "page": slug}, storage_type="memory"))
    return stores


def nav_event(target: str, context: dict | None = None, workflow_id: str | None = None) -> dict:
    """Pedido de navegação para guard_routes (o contexto vale só na tela de destino e é limpo ao sair dela)."""
    return {"id": uuid.uuid4().hex, "target": target, "context": context or {}, "workflow_id": workflow_id}


def assistant_focus(tipo: str, entity_id: Any, label: str, product_id: Any = None, categoria_id: Any = None,
                    snapshot: dict | None = None) -> dict:
    """Payload do store assistant-select: o item aberto no Detalhar vira o foco do Assistente.
    tipo: produto | pedido | lote | cliente | promocao | combinacao | <entidade do projeto>.
    snapshot: retrato da linha quando o número depende de controles não salvos (ex.: simulação)."""
    out: dict = {"entity": {"type": tipo, "id": entity_id, "label": label}}
    if snapshot:
        out["entity"]["snapshot"] = snapshot
    if product_id not in (None, ""):
        out["product_id"] = int(product_id)
    if categoria_id not in (None, ""):
        out["filters"] = {"categoria_id": str(categoria_id)}
    return out


def assistant_params_store(slug: str) -> Any:
    """Store com o estado aplicado na tela (filtros/parâmetros) para o Assistente."""
    return dcc.Store(id={"type": "assistant-params", "page": slug}, data={})


def screen_params(**values: Any) -> dict:
    """Payload do store assistant-params: valores como a tela usa + rótulo legível para ids (canal_id → canal_id_label)."""
    out = {k: v for k, v in values.items() if v not in (None, "", [], "Todos")}
    try:
        from frontend.services.data import names       # lookup id → nome do projeto (opcional)
    except ImportError:
        return out
    for k, tbl in _LABEL_TABLE.items():
        if out.get(k) is not None:
            try:
                out[f"{k}_label"] = names(tbl).get(int(out[k]), str(out[k]))
            except (ValueError, KeyError, FileNotFoundError):
                pass
    return out


def export_button(slug: str, label: str = "Exportar Excel") -> Any:
    return button(label, primary=False, icon_key="file-earmark-excel", id=f"{slug}-btn-exportar")


def hidden(show: bool) -> dict:
    return {} if show else {"display": "none"}


def send_excel(df: pd.DataFrame, filename: str, sheet: str = "Dados") -> dict:
    """Export Excel de uma aba (requer openpyxl em requirements.txt)."""
    return dcc.send_data_frame(df.to_excel, filename, sheet_name=sheet, index=False)


def send_excel_multi(sheets: dict[str, pd.DataFrame], filename: str) -> dict:
    """Export Excel com várias abas (ex.: "Por produto" + "Combinações")."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf) as xw:
        for nome, df in sheets.items():
            df.to_excel(xw, sheet_name=nome[:31], index=False)
    return dcc.send_bytes(buf.getvalue(), filename)


def opt_value(v: Any) -> Any:
    """Normaliza valor de select ('' → None)."""
    return None if v in (None, "", [], "Todos") else v
