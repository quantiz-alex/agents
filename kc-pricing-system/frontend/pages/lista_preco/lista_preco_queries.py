"""Queries para a pagina de Lista de Precos Sell In — leitura de mock_data CSV."""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_lista_preco_itens(
    familia: Optional[str] = None,
    canal: Optional[str] = None,
    status_cap: Optional[str] = None,
    status_aprovacao: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega itens da lista de precos com filtros opcionais, enriquecidos com dados do produto."""
    df_itens = pd.read_csv(_MOCK_DIR / "listas_preco_itens.csv")
    df_produtos = pd.read_csv(_MOCK_DIR / "produtos.csv")[["id", "sku", "descricao", "familia", "canal", "preco_atual"]]
    df_listas = pd.read_csv(_MOCK_DIR / "listas_preco.csv")[["id", "status", "descricao"]]

    df = df_itens.merge(df_produtos, left_on="produto_id", right_on="id", suffixes=("", "_prod"))
    df = df.merge(df_listas, left_on="lista_preco_id", right_on="id", suffixes=("", "_lista"))

    if familia:
        df = df[df["familia"] == familia]
    if canal:
        df = df[df["canal"] == canal]
    if status_cap == "Dentro":
        df = df[df["cap_aplicado"] == 0]
    elif status_cap == "Limitado pelo CAP":
        df = df[df["cap_aplicado"] == 1]
    if status_aprovacao:
        df = df[df["status"] == status_aprovacao]

    return df.reset_index(drop=True)


def calcular_kpis_lista_preco(df: pd.DataFrame) -> dict:
    """Calcula KPIs da pagina de lista de precos."""
    total_skus = len(df)
    pct_cap = (len(df[df["cap_aplicado"] == 0]) / total_skus * 100) if total_skus > 0 else 0.0
    variacao_media = df["variacao_pct"].mean() if total_skus > 0 else 0.0
    impacto_receita = df["sell_in_niv"].sum() if total_skus > 0 else 0.0

    return {
        "total_skus": total_skus,
        "pct_dentro_cap": round(pct_cap, 1),
        "variacao_media": round(float(variacao_media) if not np.isnan(variacao_media) else 0.0, 2),
        "impacto_receita": round(float(impacto_receita), 2),
    }


def carregar_familias_disponiveis() -> list:
    """Retorna lista de familias unicas."""
    df = pd.read_csv(_MOCK_DIR / "produtos.csv")
    return sorted(df["familia"].dropna().unique().tolist())


def carregar_canais_disponiveis() -> list:
    """Retorna lista de canais unicos."""
    df = pd.read_csv(_MOCK_DIR / "produtos.csv")
    return sorted(df["canal"].dropna().unique().tolist())
