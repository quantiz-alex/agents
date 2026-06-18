# KC Pricing System

Sistema de gestão de preços Sell In com simulação do impacto da reforma tributária brasileira (IBS/CBS/IS) sobre a cadeia de valor — desenvolvido pela Quantiz Pricing Solution.

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Dash 2.14+ / Dash Bootstrap Components / Dash AG Grid / Plotly |
| Backend | FastAPI 0.111+ / Uvicorn |
| ORM | SQLAlchemy 2.0+ |
| Validação | Pydantic v2 / pydantic-settings |
| Autenticação | JWT (python-jose) + bcrypt (passlib) |
| Banco (prod) | SQL Server / Microsoft Fabric via pyodbc |
| Banco (dev) | SQLite (fallback automático via `USE_SQLITE=true`) |
| Processamento | Pandas / NumPy |
| Testes | Pytest + HTTPX / Cypress |
| Linguagem | Python 3.11+ (100%) |

## Estrutura de Pastas

```
kc-pricing-system/
├── backend/
│   ├── api/routes/          # Routers FastAPI (1 por entidade + auth)
│   ├── models/              # Modelos SQLAlchemy
│   ├── repositories/        # Acesso ao banco de dados
│   ├── schemas/             # Schemas Pydantic v2
│   ├── services/            # Regras de negócio
│   ├── auth.py              # JWT + bcrypt
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Engine + Session + Base
│   └── main.py              # App FastAPI + CORS + routers
├── frontend/
│   ├── app.py               # Dash app entry point
│   ├── components/          # Componentes reutilizáveis
│   └── pages/               # Páginas por módulo
├── docs/                    # YAMLs de especificação
├── database/                # SQL schema, views, procedures, seed
├── mock_data/               # CSVs e JSONs de teste
├── tests/                   # Pytest + Cypress
├── .env.example             # Variáveis de ambiente exemplo
└── requirements.txt
```

## Como Rodar

### 1. Configurar variáveis de ambiente

2. Crie um ambiente virtual:
```bash
python -m venv venv
```

3. Ative o ambiente virtual:
```bash
# Windows
venv\Scripts\activate

```bash
cp .env.example .env
# Editar .env conforme o ambiente (USE_SQLITE=true para dev local)
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Iniciar o backend (porta 8000)

```bash
uvicorn backend.main:app --reload
```

A documentação interativa estará disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### 4. Iniciar o frontend (porta 8050)

```bash
python frontend/app.py
```

Acesse: http://localhost:8050

## Páginas Disponíveis

| Rota | Módulo | Descrição |
|---|---|---|
| `/login` | Login | Autenticação de usuários |
| `/importacao` | Importação de Bases | Upload e histórico de arquivos Nielsen / ERP |
| `/tributario` | Parametrização Tributária | Gestão de alíquotas IBS/CBS/IS por regime e ano |
| `/pricing` | Parametrização de Pricing | Cadastro de produtos e margens da cadeia |
| `/lista-preco` | Lista de Preço | Geração e aprovação de listas Sell In |
| `/simulacao` | Simulação de Cenários | Cenários MantemMargem / MantemPPC |
| `/administracao` | Administração | Gestão de usuários e acessos |

## Testes

### Backend (Pytest)

```bash
# Rodar todos os testes
pytest tests/ -v

# Rodar com cobertura
pytest tests/ --cov=backend --cov-report=term-missing

# Rodar apenas testes de API
pytest tests/api/ -v
```

### Frontend (Cypress)

```bash
# Instalar dependências Cypress (na pasta tests/cypress)
npm install

# Rodar testes E2E em modo headless
npx cypress run

# Abrir Cypress Test Runner
npx cypress open
```

## Entidades da API

Base URL: `http://localhost:8000/api/v1`

Todas as rotas (exceto `/auth/login`) requerem header `Authorization: Bearer <token>`.

| Entidade | Rota | Soft Delete |
|---|---|---|
| Auth | `/auth/login`, `/auth/refresh` | — |
| Usuarios | `/usuarios` | sim (campo `ativo`) |
| Produtos | `/produtos` | sim (campo `ativo`) |
| Parametros Tributarios | `/parametros-tributarios` | sim (campo `ativo`) |
| Margens da Cadeia | `/margens-cadeia` | nao (hard delete) |
| Importacoes Base | `/importacoes-base` | nao (hard delete) |
| Listas de Preco | `/listas-preco` | sim (status=Arquivada) |
| Listas Preco Itens | `/listas-preco-itens` | nao (hard delete) |
| Cenarios Simulacao | `/cenarios-simulacao` | nao (hard delete) |
| Cenarios Simulacao Itens | `/cenarios-simulacao-itens` | nao (hard delete) |

## Proximos Passos

- Integrar SQL Server real: alterar `USE_SQLITE=false` no `.env` e configurar `DB_SERVER`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Executar `test-writer` para cobertura completa de testes
- Configurar CI/CD com GitHub Actions
- Habilitar HTTPS e configurar `SECRET_KEY` forte em produção
