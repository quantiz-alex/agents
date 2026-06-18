"""Queries para a pagina de Parametrizacao de Pricing — leitura de mock_data CSV."""

from pathlib import Path
from typing import Optional

import pandas as pd

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_produtos(
    canal: Optional[str] = None,
    regiao: Optional[str] = None,
    familia: Optional[str] = None,
    classificacao: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega catalogo de produtos com filtros opcionais."""
    df = pd.read_csv(_MOCK_DIR / "produtos.csv")

    if canal:
        df = df[df["canal"] == canal]
    if regiao:
        df = df[df["regiao"] == regiao]
    if familia:
        df = df[df["familia"] == familia]
    if classificacao:
        df = df[df["classificacao"] == classificacao]

    return df.reset_index(drop=True)


def carregar_margens_cadeia(
    canal: Optional[str] = None,
    familia: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega margens da cadeia com filtros opcionais."""
    df = pd.read_csv(_MOCK_DIR / "margens_cadeia.csv")

    if canal:
        df = df[df["canal"] == canal]
    if familia:
        df = df[df["familia"] == familia]

    return df.reset_index(drop=True)


def calcular_kpis_pricing(df_produtos: pd.DataFrame, df_margens: pd.DataFrame) -> dict:
    """Calcula metricas de resumo de pricing."""
    total_skus = len(df_produtos)
    capitaes = len(df_produtos[df_produtos["classificacao"] == "Capitao"]) if not df_produtos.empty else 0
    familias = df_produtos["familia"].nunique() if not df_produtos.empty else 0
    canais = df_produtos["canal"].nunique() if not df_produtos.empty else 0

    return {
        "total_skus": total_skus,
        "capitaes": capitaes,
        "familias": familias,
        "canais": canais,
    }
