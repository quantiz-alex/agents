"""Queries para a pagina de Importacao de Bases — leitura de mock_data CSV."""

from pathlib import Path
from typing import Optional

import pandas as pd

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_importacoes(
    fonte: Optional[str] = None,
    data_inicio: Optional[str] = None,
    data_fim: Optional[str] = None,
    status: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega historico de importacoes com filtros opcionais."""
    df = pd.read_csv(_MOCK_DIR / "importacoes_base.csv")

    if fonte:
        # normaliza o nome para comparar com o CSV (ex: "Nielsen Retail" → "NielsenRetail")
        fonte_norm = fonte.replace(" ", "")
        df = df[df["fonte"].str.replace(" ", "") == fonte_norm]

    if data_inicio:
        df = df[df["data_importacao"] >= data_inicio]

    if data_fim:
        df = df[df["data_importacao"] <= data_fim + "T23:59:59"]

    if status:
        df = df[df["status"] == status]

    return df.reset_index(drop=True)


def calcular_kpis_importacao(df: pd.DataFrame) -> dict:
    """Calcula os KPIs da pagina de importacao."""
    total_registros = len(df)
    ultima_carga = (
        df["data_importacao"].max()
        if not df.empty
        else "—"
    )
    sucesso = len(df[df["status"] == "Sucesso"]) if not df.empty else 0
    erros = len(df[df["status"] == "Erro"]) if not df.empty else 0

    return {
        "total_registros": total_registros,
        "ultima_carga": ultima_carga,
        "sucesso": sucesso,
        "erros": erros,
    }
