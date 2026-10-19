"""Garante a raiz do projeto no sys.path (pytest executado de qualquer pasta).

Sem imports de backend aqui: testes de frontend rodam sem FastAPI/SQLAlchemy. Fixtures de backend ficam em tests/backend/conftest.py.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
