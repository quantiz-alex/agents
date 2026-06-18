"""Queries para a pagina de Administracao — leitura de mock_data CSV."""

from pathlib import Path
from typing import Optional

import pandas as pd

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def carregar_usuarios(
    role: Optional[str] = None,
    ativo: Optional[str] = None,
) -> pd.DataFrame:
    """Carrega usuarios com filtros opcionais."""
    df = pd.read_csv(_MOCK_DIR / "usuarios.csv")
    df = df.drop(columns=["senha_hash"], errors="ignore")

    if role:
        df = df[df["role"] == role]

    if ativo == "Sim":
        df = df[df["ativo"] == 1]
    elif ativo == "Nao":
        df = df[df["ativo"] == 0]

    return df.reset_index(drop=True)


def calcular_kpis_administracao(df: pd.DataFrame) -> dict:
    """Calcula metricas da pagina de administracao."""
    total = len(df)
    ativos = len(df[df["ativo"] == 1]) if not df.empty else 0
    admins = len(df[df["role"] == "admin"]) if not df.empty else 0
    gestores = len(df[df["role"] == "gestor_pricing"]) if not df.empty else 0
    analistas = len(df[df["role"] == "analista_pricing"]) if not df.empty else 0

    return {
        "total": total,
        "ativos": ativos,
        "admins": admins,
        "gestores": gestores,
        "analistas": analistas,
    }
