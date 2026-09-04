"""
api_client.py — Cliente HTTP do frontend para a API FastAPI do projeto.
Copie para frontend/api_client.py.

Modo de operação controlado por variáveis de ambiente (.env):
  USE_API=false (padrão)  → páginas lêem mock_data/*.csv (demo offline, sem backend)
  USE_API=true            → páginas chamam a API (backend/main.py em API_BASE_URL)

Todas as funções de `_queries.py` devem seguir o padrão:

    if use_api():
        return pd.DataFrame(api_get("/produtos", params={"skip": 0, "limit": 5000}))
    return pd.read_csv(DATA_DIR / "produto.csv")

O token JWT é obtido em login() e mantido em memória do processo (demo). Em produção,
persista no dcc.Store da sessão e passe via `token=`.
"""
from __future__ import annotations

import os
from typing import Any

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
_TIMEOUT = float(os.getenv("API_TIMEOUT", "15"))
_token: str | None = None


def use_api() -> bool:
    """True quando USE_API=true no ambiente — decide entre CSV e API nas queries."""
    return os.getenv("USE_API", "false").strip().lower() in ("1", "true", "yes")


def set_token(token: str | None) -> None:
    global _token
    _token = token


def _headers(token: str | None = None) -> dict[str, str]:
    t = token or _token
    return {"Authorization": f"Bearer {t}"} if t else {}


def login(email: str, senha: str) -> dict[str, Any]:
    """POST /auth/login → guarda o token e retorna {access_token, token_type, expires_in}."""
    r = requests.post(f"{API_BASE_URL}/auth/login", json={"email": email, "senha": senha}, timeout=_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    set_token(data.get("access_token"))
    return data


def api_get(path: str, params: dict[str, Any] | None = None, token: str | None = None) -> Any:
    r = requests.get(f"{API_BASE_URL}{path}", params=params, headers=_headers(token), timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json()


def api_post(path: str, payload: dict[str, Any], token: str | None = None) -> Any:
    r = requests.post(f"{API_BASE_URL}{path}", json=payload, headers=_headers(token), timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else None


def api_put(path: str, payload: dict[str, Any], token: str | None = None) -> Any:
    r = requests.put(f"{API_BASE_URL}{path}", json=payload, headers=_headers(token), timeout=_TIMEOUT)
    r.raise_for_status()
    return r.json() if r.content else None


def api_delete(path: str, token: str | None = None) -> None:
    r = requests.delete(f"{API_BASE_URL}{path}", headers=_headers(token), timeout=_TIMEOUT)
    r.raise_for_status()


def api_health() -> bool:
    """GET /health (fora de /api/v1) — usado pela Home para exibir o chip 'API online/offline'."""
    try:
        base = API_BASE_URL.rsplit("/api/", 1)[0]
        return requests.get(f"{base}/health", timeout=3).ok
    except requests.RequestException:
        return False
