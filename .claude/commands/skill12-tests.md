# Skill 12 — Unit Tests (Backend Pytest)

Gere testes unitários de backend com Pytest para uma entidade da API FastAPI.

## Argumento obrigatório

Nome da entidade: $ARGUMENTS

Exemplos:
- `/skill12-tests cenarios_precificacao`
- `/skill12-tests skus`

---

## Instruções

1. Leia `backend/api/routes/<entidade>.py` para ver os endpoints e prefixo de rota.
2. Leia `backend/schemas/<entidade>.py` para ver os campos obrigatórios.
3. Leia `docs/data_model.yaml` para confirmar campos nullable e tipos.
4. Gere `tests/backend/test_<entidade>.py`.
5. Fixtures de API vão em `tests/backend/conftest.py` (gere se não existir). O `tests/conftest.py` raiz é só `sys.path` (template `$LH/templates/tests/conftest.py`) para os testes de frontend rodarem sem backend.

---

## `tests/backend/conftest.py` (gerar apenas se não existir)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.main import app
from backend.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
```

---

## `tests/backend/test_<entidade>.py`

```python
import pytest
from fastapi.testclient import TestClient

# Prefixo real das rotas — sempre /api/v1/<entidade>s
BASE = "/api/v1/<entidade>s"


@pytest.fixture
def payload_valido() -> dict:
    """
    Preencher com os campos obrigatórios da entidade conforme data_model.yaml.
    Campos nullable=true podem ser omitidos.
    Campos com FK devem referenciar IDs que existam ou usar fixture auxiliar.
    """
    return {
        # ex.: "nome": "Teste", "ativo": True, "tipo": "valor_enum_valido"
    }


class Test<Entidade>CRUD:
    """Testes unitários CRUD da entidade <Entidade>."""

    def test_listar_retorna_200_e_lista(self, client: TestClient) -> None:
        response = client.get(f"{BASE}/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_criar_com_payload_valido_retorna_201(
        self, client: TestClient, payload_valido: dict
    ) -> None:
        response = client.post(f"{BASE}/", json=payload_valido)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data and data["id"] > 0

    def test_criar_com_payload_vazio_retorna_422(self, client: TestClient) -> None:
        response = client.post(f"{BASE}/", json={})
        assert response.status_code == 422

    def test_buscar_por_id_existente(
        self, client: TestClient, payload_valido: dict
    ) -> None:
        criado = client.post(f"{BASE}/", json=payload_valido).json()
        response = client.get(f"{BASE}/{criado['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == criado["id"]

    def test_buscar_por_id_inexistente_retorna_404(self, client: TestClient) -> None:
        response = client.get(f"{BASE}/999999")
        assert response.status_code == 404

    def test_atualizar_existente_retorna_200(
        self, client: TestClient, payload_valido: dict
    ) -> None:
        criado = client.post(f"{BASE}/", json=payload_valido).json()
        response = client.put(f"{BASE}/{criado['id']}", json=payload_valido)
        assert response.status_code == 200
        assert response.json()["id"] == criado["id"]

    def test_deletar_existente_retorna_204(
        self, client: TestClient, payload_valido: dict
    ) -> None:
        criado = client.post(f"{BASE}/", json=payload_valido).json()
        response = client.delete(f"{BASE}/{criado['id']}")
        assert response.status_code == 204

    def test_deletar_inexistente_retorna_404(self, client: TestClient) -> None:
        response = client.delete(f"{BASE}/999999")
        assert response.status_code == 404
```

---

## Regras

- **Banco de teste começa VAZIO** — nunca assumir que id=1 existe. Criar via POST antes de consultar.
- **Prefixo `/api/v1/` obrigatório** — as rotas não ficam na raiz.
- **Payload válido real** — preencher `payload_valido` com valores reais que passem na validação Pydantic da entidade.
- Se a entidade tiver campos FK obrigatórios, criar as entidades dependentes em fixtures auxiliares antes de criar a entidade principal.
- Não testar regras de negócio internas (services) — apenas comportamento HTTP observável.
- Contexto máximo: **8.000 tokens** de saída.

## Pós-processamento

1. Verificar que `tests/backend/test_<entidade>.py` é Python sintaticamente válido
2. Verificar que `BASE` usa o prefixo correto `/api/v1/`
3. Verificar que `payload_valido` não retorna dicionário vazio `{}`
4. Criar checkpoint parcial por entidade e avançar

## Para testes E2E com Cypress

Consulte `/skill13-integration-tests` — ele gera a suite Cypress completa para o frontend.
