"""Callbacks da pagina de Login do KC Pricing System."""

from pathlib import Path
from typing import Any, Optional

import pandas as pd
from dash import Input, Output, State, callback, no_update

_MOCK_DIR = Path(__file__).parent.parent.parent.parent / "mock_data"


def _carregar_usuarios() -> pd.DataFrame:
    """Carrega usuarios do mock_data."""
    df = pd.read_csv(_MOCK_DIR / "usuarios.csv")
    df["email"] = df["email"].str.lower().str.strip()
    return df


def register_callbacks() -> None:
    """Registra callbacks da pagina de login.

    REGRA CRITICA: Output('url','pathname') NAO existe aqui.
    O redirecionamento pos-login e tratado pelo guard_routes em app.py,
    que reage a mudancas em current-user.data via Input.
    """

    @callback(
        Output("current-user", "data"),
        Output("login-alert", "children"),
        Output("login-alert", "is_open"),
        Input("login-btn", "n_clicks"),
        Input("login-email", "n_submit"),
        Input("login-senha", "n_submit"),
        State("login-email", "value"),
        State("login-senha", "value"),
        prevent_initial_call=True,
    )
    def autenticar(
        n_clicks: Optional[int],
        n_submit_email: Optional[int],
        n_submit_senha: Optional[int],
        email: Optional[str],
        senha: Optional[str],
    ) -> tuple[Any, str, bool]:
        if not email or not senha:
            return no_update, "Preencha email e senha.", True

        email_norm = email.lower().strip()

        try:
            df = _carregar_usuarios()
            usuario = df[df["email"] == email_norm]
        except Exception:
            return no_update, "Erro ao verificar credenciais. Contate o suporte.", True

        if usuario.empty:
            return no_update, "Email nao encontrado. Verifique e tente novamente.", True

        row = usuario.iloc[0]
        if int(row.get("ativo", 1)) == 0:
            return no_update, "Usuario inativo. Contate o administrador.", True

        # Em modo mock, qualquer senha e aceita
        user_data: dict = {
            "id": int(row["id"]),
            "nome": str(row["nome"]),
            "email": str(row["email"]),
            "role": str(row["role"]),
        }

        return user_data, "", False
