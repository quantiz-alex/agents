# Skill — Authentication Layer (JWT + Dash Guard)

Gera a camada completa de autenticação do projeto: JWT para o FastAPI e proteção de rotas no Dash.

## Quando Usar

- Após a Etapa 9 (Backend FastAPI) e antes do Etapa 10 (Config + README)
- Para adicionar autenticação a um projeto que ainda não tem
- Para substituir o mock de login por autenticação real

## Argumento opcional

`$ARGUMENTS` — estratégia (`jwt` | `jwt+roles`). Padrão: `jwt`.

---

## Instruções

1. Leia `backend/config.py` para obter `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`.
2. Leia `docs/data_model.yaml` para localizar a entidade de usuários (nome pode variar: `usuarios`, `users`, `colaboradores`).
3. Gere os arquivos listados abaixo.
4. Se os arquivos já existirem, aplique patch incremental.

---

## Arquivos Gerados

### `backend/auth.py`

```python
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.database import get_db

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Senhas ────────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── Tokens JWT ────────────────────────────────────────────────────────────────

def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


# ── Dependência de rota ───────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Injeta o usuário autenticado em qualquer rota protegida.
    Uso: current_user = Depends(get_current_user)
    """
    payload = decode_token(token)
    user_id: int | None = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token sem identificador de usuário")

    # Importar model de usuário dinamicamente para evitar circular imports
    from backend.models.usuarios import Usuario  # ajustar nome se diferente
    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()

    if user is None or not user.ativo:
        raise HTTPException(status_code=401, detail="Usuário não encontrado ou inativo")

    return user
```

---

### `backend/schemas/token.py`

```python
from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int
    email: str | None = None
    nome: str | None = None
```

---

### `backend/api/routes/auth.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.auth import verify_password, create_access_token
from backend.config import get_settings
from backend.database import get_db
from backend.schemas.token import TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Autentica usuário e retorna JWT."""
    from backend.models.usuarios import Usuario  # ajustar nome se diferente

    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo — contate o administrador",
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "nome": getattr(user, "nome", user.email),
        }
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    token: str,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Renova o access token a partir de um token ainda válido."""
    from backend.auth import decode_token

    payload = decode_token(token)
    new_token = create_access_token(
        data={
            "sub": payload["sub"],
            "email": payload.get("email"),
            "nome": payload.get("nome"),
        }
    )
    return TokenResponse(
        access_token=new_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )
```

---

### Instrução para proteger routers existentes

Para cada arquivo em `backend/api/routes/<entidade>.py`, adicionar a dependência:

```python
from backend.auth import get_current_user
from backend.models.usuarios import Usuario  # ajustar se necessário

# Nos endpoints que requerem autenticação:
@router.get("/", response_model=list[<Entidade>Response])
def get_all(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),  # ← adicionar
):
    ...
```

---

### Atualização em `backend/main.py`

Adicionar o router de auth e configurar CORS:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.api.routes import auth, <entidade1>, <entidade2>
from backend.database import create_tables, health_check

settings = get_settings()

app = FastAPI(
    title="{PROJECT_NAME} API",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(<entidade1>.router, prefix="/api/v1")
app.include_router(<entidade2>.router, prefix="/api/v1")


@app.on_event("startup")
async def startup() -> None:
    create_tables()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "db": health_check()}
```

---

### Atualização no Dash — `frontend/pages/login/login_callbacks.py`

Substituir mock por chamada real à API:

```python
import requests
from dash import Input, Output, State, callback, no_update
from backend.config import get_settings

settings = get_settings()
API_URL = f"http://{settings.app_host}:{settings.app_port}/api/v1"


def register_callbacks() -> None:

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
    def fazer_login(
        n_clicks: int,
        n_email: int,
        n_senha: int,
        email: str | None,
        senha: str | None,
    ) -> tuple:
        if not email or not senha:
            return no_update, "Preencha e-mail e senha.", True

        try:
            resp = requests.post(
                f"{API_URL}/auth/login",
                data={"username": email, "password": senha},
                timeout=5,
            )
        except requests.exceptions.ConnectionError:
            return no_update, "Erro de conexão com o servidor.", True

        if resp.status_code == 200:
            data = resp.json()
            user_data = {
                "access_token": data["access_token"],
                "email": email,
            }
            return user_data, "", False

        detail = resp.json().get("detail", "Credenciais inválidas.")
        return no_update, detail, True
```

**Nota de segurança:** O `access_token` é armazenado em `dcc.Store(storage_type="session")` para uso em chamadas subsequentes à API. Em produção, considere HttpOnly cookies via um proxy reverso.

---

## Dependências Adicionais

Adicionar ao `requirements.txt`:

```
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
```

---

## Restrições

- `SECRET_KEY` NUNCA hardcoded — sempre lida de `Settings` (`.env`).
- Imports de models dentro das funções (não no topo) para evitar circular imports.
- Endpoints `/docs` e `/redoc` desabilitados em produção.
- Contexto máximo: **8.000 tokens** de saída.

## Pós-processamento

1. Verificar que todos os arquivos Python são válidos (parse)
2. Verificar que `SECRET_KEY` não aparece como string literal no código
3. Verificar que `get_current_user` está importado em pelo menos um router
4. Criar checkpoint `step_auth.json`

## Modo de Uso

```
/skill-auth
/skill-auth jwt+roles
```
