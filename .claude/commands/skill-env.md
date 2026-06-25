# Skill — Environment & Database Configuration

Leia `.build/project.json` e `docs/data_model.yaml` para gerar os arquivos de configuração de ambiente, conexão com banco de dados e gerenciamento de segredos do projeto.

## Quando Usar

- Após a Etapa 2 (Data Model) e antes da Etapa 9 (Backend FastAPI)
- Quando precisar adicionar uma nova variável de ambiente ao projeto
- Para configurar conexão com banco de dados real (substituindo mock)

## Argumento opcional

`$ARGUMENTS` — banco alvo (`sqlserver` | `sqlite` | `postgres`). Padrão: `sqlserver`.

---

## Instruções

1. Leia `.build/project.json` para obter `name` e `name_slug`.
2. Leia `docs/data_model.yaml` para listar as entidades (necessário para `Base.metadata`).
3. Gere os 4 arquivos abaixo.
4. Se os arquivos já existirem, aplique patch incremental.

---

## Arquivos Gerados

### `.env.example`

```dotenv
# ============================================================
# {PROJECT_NAME} — Variáveis de Ambiente
# Copie este arquivo para .env e preencha os valores reais.
# NUNCA versione o arquivo .env — ele está no .gitignore.
# ============================================================

# --- Banco de dados ---
# SQL Server / Microsoft Fabric
DATABASE_DRIVER=ODBC+Driver+18+for+SQL+Server
DATABASE_SERVER=localhost
DATABASE_PORT=1433
DATABASE_NAME={project_slug}_db
DATABASE_USER=sa
DATABASE_PASSWORD=SuaSenhaAqui

# SQLite (desenvolvimento local sem SQL Server)
# DATABASE_URL=sqlite:///./dev.db

# --- Segurança JWT ---
SECRET_KEY=troque-esta-chave-por-uma-string-aleatoria-de-64-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480   # 8 horas

# --- Aplicação ---
APP_ENV=development       # development | staging | production
APP_DEBUG=true
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_URL=http://localhost:1050

# --- CORS ---
ALLOWED_ORIGINS=http://localhost:1050,http://127.0.0.1:1050

# --- Frontend Dash ---
DASH_HOST=0.0.0.0
DASH_PORT=1050
DASH_DEBUG=true
```

---

### `backend/config.py`

```python
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Banco de dados
    database_driver: str = "ODBC+Driver+18+for+SQL+Server"
    database_server: str = "localhost"
    database_port: int = 1433
    database_name: str = "app_db"
    database_user: str = "sa"
    database_password: str = ""
    database_url: str = ""          # se definido, sobrescreve os campos acima

    # Segurança
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    # Aplicação
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    frontend_url: str = "http://localhost:1050"

    # CORS
    allowed_origins: str = "http://localhost:1050"

    @property
    def sqlserver_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"mssql+pyodbc://{self.database_user}:{self.database_password}"
            f"@{self.database_server}:{self.database_port}/{self.database_name}"
            f"?driver={self.database_driver.replace('+', ' ')}"
        )

    @property
    def sqlite_url(self) -> str:
        return "sqlite:///./dev.db"

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

---

### `backend/database.py`

```python
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from backend.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


def _get_engine():
    if settings.app_env == "development" and not settings.database_url:
        # Fallback para SQLite em desenvolvimento sem SQL Server configurado
        engine = create_engine(
            settings.sqlite_url,
            connect_args={"check_same_thread": False},
            echo=settings.app_debug,
        )
    else:
        engine = create_engine(
            settings.sqlserver_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.app_debug,
        )
    return engine


engine = _get_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """Dependency do FastAPI — injeta sessão de banco de dados."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Cria todas as tabelas definidas nos models SQLAlchemy."""
    Base.metadata.create_all(bind=engine)


def health_check() -> bool:
    """Verifica conexão com o banco de dados."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
```

---

### `.gitignore` (append — não sobrescrever)

Verificar se as linhas abaixo existem; adicionar apenas as ausentes:

```
# Ambiente
.env
.env.local
.env.*.local

# Banco de dados SQLite (desenvolvimento)
*.db
*.db-shm
*.db-wal

# Build artifacts
.build/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
htmlcov/

# Mock data (opcional — remover se quiser versionar)
# mock_data/

# Reports
validation_reports/
tests/reports/
```

---

## Dependências Adicionais

Adicionar ao `requirements.txt` se não existirem:

```
pydantic-settings>=2.0.0
python-dotenv>=1.0.0
pyodbc>=5.0.0
sqlalchemy>=2.0.0
```

---

## Restrições

- O arquivo `.env` NUNCA deve ser gerado — apenas `.env.example`.
- `SECRET_KEY` no `.env.example` deve ter comentário explícito para troca.
- Em ambiente `development`, usar SQLite como fallback automático.
- Contexto máximo: **6.000 tokens** de saída.

## Pós-processamento

1. Verificar que `backend/config.py` é Python válido (parse)
2. Verificar que `backend/database.py` é Python válido (parse)
3. Verificar que `.gitignore` contém `.env`
4. Criar checkpoint `step_env.json`

## Modo de Uso

```
/skill-env
/skill-env sqlite
/skill-env sqlserver
```
