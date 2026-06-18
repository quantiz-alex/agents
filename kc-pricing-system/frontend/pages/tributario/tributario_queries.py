"""Queries para a pagina de Parametrizacao Tributaria — leitura de mock_data CSV."""

from pathlib import Path
from typing import Optional

import pandas as pd

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_parametros_tributarios(
    ano_vigencia: Optional[str] = None,
    regime: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega parametros tributarios com filtros opcionais."""
    df = pd.read_csv(_MOCK_DIR / "parametros_tributarios.csv")

    if ano_vigencia:
        df = df[df["ano_vigencia"] == int(ano_vigencia)]

    if regime:
        df = df[df["regime"] == regime]

    return df.reset_index(drop=True)


def calcular_kpis_tributario(df: pd.DataFrame) -> dict:
    """Calcula metricas de resumo dos parametros tributarios."""
    total = len(df)
    ativos = len(df[df["ativo"] == 1]) if not df.empty else 0
    anos_cobertos = df["ano_vigencia"].nunique() if not df.empty else 0
    return {
        "total": total,
        "ativos": ativos,
        "anos_cobertos": anos_cobertos,
    }
