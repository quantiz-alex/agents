"""Queries para a pagina de Simulacao de Impactos — leitura de mock_data CSV."""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_cenarios(
    tipo_cenario: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega cenarios de simulacao com filtro opcional por tipo."""
    df = pd.read_csv(_MOCK_DIR / "cenarios_simulacao.csv")

    tipo_map = {"Mantem Margem": "MantemMargem", "Mantem PPC": "MantemPPC"}
    if tipo_cenario and tipo_cenario in tipo_map:
        df = df[df["tipo_cenario"] == tipo_map[tipo_cenario]]

    return df.reset_index(drop=True)


def carregar_cenarios_itens(
    familia: Optional[str] = None,
    canal: Optional[str] = None,
    regiao: Optional[str] = None,
    tipo_cenario: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega itens de simulacao enriquecidos com dados de produto e cenario."""
    df_itens = pd.read_csv(_MOCK_DIR / "cenarios_simulacao_itens.csv")
    df_produtos = pd.read_csv(_MOCK_DIR / "produtos.csv")[["id", "sku", "descricao", "familia", "canal", "regiao"]]
    df_cenarios = pd.read_csv(_MOCK_DIR / "cenarios_simulacao.csv")[["id", "tipo_cenario", "descricao"]]

    df = df_itens.merge(df_produtos, left_on="produto_id", right_on="id", suffixes=("", "_prod"))
    df = df.merge(df_cenarios, left_on="cenario_id", right_on="id", suffixes=("", "_cenario"))

    tipo_map = {"Mantem Margem": "MantemMargem", "Mantem PPC": "MantemPPC"}
    if tipo_cenario and tipo_cenario in tipo_map:
        df = df[df["tipo_cenario"] == tipo_map[tipo_cenario]]
    if familia:
        df = df[df["familia"] == familia]
    if canal:
        df = df[df["canal"] == canal]
    if regiao:
        df = df[df["regiao"] == regiao]

    return df.reset_index(drop=True)


def calcular_kpis_simulacao(df_cenarios: pd.DataFrame, df_itens: pd.DataFrame) -> dict:
    """Calcula KPIs de simulacao de impactos."""
    if df_cenarios.empty:
        return {
            "delta_volume_pct": 0.0,
            "delta_receita_niv": 0.0,
            "delta_margem_industria": 0.0,
            "delta_margem_distribuidor_pct": 0.0,
            "delta_margem_varejo_pct": 0.0,
        }

    delta_volume = float(df_cenarios["delta_volume_pct"].mean())
    delta_receita = float(df_cenarios["delta_receita_niv"].sum())
    delta_margem_ind = float(df_cenarios["delta_margem_industria"].sum())

    total_receita = float(df_itens["receita_niv_simulada"].sum()) if not df_itens.empty else 1.0
    total_mg_dist = float(df_itens["margem_distribuidor"].sum()) if not df_itens.empty else 0.0
    total_mg_var = float(df_itens["margem_varejo"].sum()) if not df_itens.empty else 0.0

    delta_mg_dist_pct = (total_mg_dist / total_receita * 100) if total_receita > 0 else 0.0
    delta_mg_var_pct = (total_mg_var / total_receita * 100) if total_receita > 0 else 0.0

    return {
        "delta_volume_pct": round(delta_volume, 2),
        "delta_receita_niv": round(delta_receita, 2),
        "delta_margem_industria": round(delta_margem_ind, 2),
        "delta_margem_distribuidor_pct": round(delta_mg_dist_pct, 2),
        "delta_margem_varejo_pct": round(delta_mg_var_pct, 2),
    }
