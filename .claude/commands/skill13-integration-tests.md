# Skill 13 — Cypress E2E Tests

Gere a suite completa de testes E2E com Cypress para o frontend Dash.

## Diferença entre Skill12 e Skill13

- **Skill12**: Testes unitários de backend (Pytest + TestClient, sem servidor rodando)
- **Skill13**: Testes E2E de frontend (Cypress + browser real, app precisa estar rodando)

## Argumento opcional

Nome da página: $ARGUMENTS

- Se vazio → gera setup completo (config, support, fixtures) + testes de todas as páginas
- Se informado (ex.: `cenarios`) → gera/atualiza apenas o spec daquela página

---

## Instruções

1. Leia `docs/screens_definition.yaml` para obter a lista de páginas, rotas e componentes.
2. Leia `docs/design-system.yaml` para confirmar os padrões de ID (`<pagina>-grid`, `<pagina>-btn-filtrar`, etc.).
3. Leia `mock_data/usuarios.csv` para obter um e-mail de usuário válido para os testes.
4. Gere os arquivos abaixo na ordem indicada.

---

## Arquivos a Gerar

### Estrutura de saída

```
tests/frontend/
├── package.json
├── cypress.config.js
└── cypress/
    ├── fixtures/
    │   └── usuario.json
    ├── support/
    │   ├── commands.js
    │   └── e2e.js
    └── e2e/
        ├── login.cy.js
        ├── <pagina1>.cy.js
        ├── <pagina2>.cy.js
        └── ...
```

---

### `tests/frontend/package.json`

```json
{
  "name": "<project-slug>-e2e",
  "version": "1.0.0",
  "description": "Cypress E2E tests",
  "scripts": {
    "cy:open": "cypress open",
    "cy:run": "cypress run",
    "cy:run:headed": "cypress run --headed"
  },
  "devDependencies": {
    "cypress": "^13.0.0"
  }
}
```

---

### `tests/frontend/cypress.config.js`

```javascript
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:1050',
    specPattern: 'cypress/e2e/**/*.cy.js',
    supportFile: 'cypress/support/e2e.js',
    downloadsFolder: 'cypress/downloads',
    screenshotsFolder: 'cypress/screenshots',
    videosFolder: 'cypress/videos',
    viewportWidth: 1440,
    viewportHeight: 900,
    defaultCommandTimeout: 10000,   // Dash renderiza dinamicamente — timeout maior
    pageLoadTimeout: 30000,
    retries: {
      runMode: 2,
      openMode: 0,
    },
    env: {
      dashUrl: 'http://localhost:1050',
    },
  },
})
```

---

### `tests/frontend/cypress/fixtures/usuario.json`

Ler `mock_data/usuarios.csv` e pegar o primeiro usuário ativo (`ativo=1`):

```json
{
  "email": "<email_do_primeiro_usuario_ativo>",
  "senha": "senha123",
  "nome": "<nome_do_usuario>"
}
```

---

### `tests/frontend/cypress/support/commands.js`

```javascript
// Comando de login com cache de sessão via cy.session()
Cypress.Commands.add('login', (email, senha) => {
  cy.session(
    [email, senha],
    () => {
      cy.visit('/login')
      cy.get('#login-email').type(email)
      cy.get('#login-senha').type(senha)
      cy.get('#login-btn').click()
      // Aguarda redirecionamento após login bem-sucedido
      cy.url().should('not.include', '/login')
    },
    {
      validate() {
        // Sessão válida se não estiver na página de login
        cy.url().then(url => {
          if (url.includes('/login')) throw new Error('Sessão expirada')
        })
      },
      cacheAcrossSpecs: true,
    }
  )
})

// Navegar para uma página já autenticado
Cypress.Commands.add('visitAutenticado', (rota) => {
  cy.fixture('usuario').then(({ email, senha }) => {
    cy.login(email, senha)
  })
  cy.visit(rota)
})

// Aguardar AG Grid carregar (Dash renderiza async)
Cypress.Commands.add('aguardarGrid', (gridId) => {
  cy.get(`#${gridId}`, { timeout: 15000 }).should('exist')
  cy.get(`#${gridId} .ag-center-cols-container`, { timeout: 15000 }).should('exist')
})
```

---

### `tests/frontend/cypress/support/e2e.js`

```javascript
import './commands'

// Ignorar erros de rede para requisições ao backend ainda não rodando
Cypress.on('uncaught:exception', (err) => {
  if (err.message.includes('ResizeObserver') || err.message.includes('fetch')) {
    return false
  }
})
```

---

### `tests/frontend/cypress/e2e/login.cy.js`

```javascript
describe('Login', () => {
  beforeEach(() => {
    cy.visit('/login')
  })

  it('exibe a página de login', () => {
    cy.get('#login-email').should('exist')
    cy.get('#login-senha').should('exist')
    cy.get('#login-btn').should('exist')
  })

  it('exibe erro com credenciais inválidas', () => {
    cy.get('#login-email').type('usuario@invalido.com')
    cy.get('#login-senha').type('senhaerrada')
    cy.get('#login-btn').click()
    cy.get('#login-alert').should('be.visible')
  })

  it('redireciona para home com credenciais válidas', () => {
    cy.fixture('usuario').then(({ email, senha }) => {
      cy.get('#login-email').type(email)
      cy.get('#login-senha').type(senha)
      cy.get('#login-btn').click()
      cy.url().should('not.include', '/login')
    })
  })
})
```

---

### `tests/frontend/cypress/e2e/<pagina>.cy.js` — um arquivo por página

Para cada página em `screens_definition.yaml`, gerar um spec com este padrão:

```javascript
// tests/frontend/cypress/e2e/<pagina>.cy.js
// Página: <title> — Rota: <rota>

describe('<title>', () => {
  before(() => {
    // Login único antes de todos os testes desta suite
    cy.fixture('usuario').then(({ email, senha }) => {
      cy.login(email, senha)
    })
  })

  beforeEach(() => {
    cy.visit('<rota>')
    // Aguarda o Dash terminar de renderizar
    cy.get('.page-wrapper', { timeout: 15000 }).should('exist')
  })

  // ── Carregamento ─────────────────────────────────────────────────────────
  it('carrega a página sem erro', () => {
    cy.get('.page-wrapper').should('be.visible')
    cy.get('.page-header').should('exist')
  })

  // ── Grid (se a página tiver grid) ────────────────────────────────────────
  it('exibe a grid com dados', () => {
    cy.aguardarGrid('<pagina>-grid')
    cy.get('#<pagina>-grid .ag-row').should('have.length.greaterThan', 0)
  })

  // ── Filtros ───────────────────────────────────────────────────────────────
  it('filtra os dados ao clicar em Filtrar', () => {
    cy.aguardarGrid('<pagina>-grid')
    // Obter número de linhas antes do filtro
    cy.get('#<pagina>-grid .ag-row').its('length').as('totalAntes')
    // Aplicar filtro (ajustar conforme filtros disponíveis na página)
    cy.get('#<pagina>-btn-filtrar').click()
    cy.get('#<pagina>-grid .ag-row').should('exist')
  })

  // ── Exportação ────────────────────────────────────────────────────────────
  it('exporta CSV ao clicar no botão de exportar', () => {
    cy.aguardarGrid('<pagina>-grid')
    cy.get('#<pagina>-btn-export').click()
    cy.readFile('cypress/downloads/<pagina>.csv', { timeout: 5000 }).should('exist')
  })

  // ── KPIs (se a página tiver KPIs) ────────────────────────────────────────
  it('exibe KPIs com valores', () => {
    cy.get('#<pagina>-kpis-row').should('exist')
    cy.get('#<pagina>-kpis-row .card').should('have.length.greaterThan', 0)
  })

  // ── Gráficos (se a página tiver charts) ──────────────────────────────────
  it('renderiza gráficos sem erro', () => {
    cy.get('[id^="<pagina>-chart-"]').should('exist')
    cy.get('.js-plotly-plot').should('be.visible')
  })

  // ── Modal / Formulário (se a página tiver ação de criar/editar) ───────────
  it('abre modal ao clicar em Novo', () => {
    cy.get('#<pagina>-btn-novo').click()
    cy.get('[id$="-modal"]').should('be.visible')
  })
})
```

**Instruções para adaptar cada página:**
- Incluir apenas os blocos `it()` correspondentes aos `components` definidos em `screens_definition.yaml` para aquela página
- Substituir `<pagina>` pelo slug real da página (ex.: `cenarios`, `skus`)
- Substituir `<title>` pelo título real da página
- Substituir `<rota>` pela rota real (ex.: `/cenarios`)
- Se a página não tem modal/novo, omitir aquele bloco `it()`
- Se a página não tem gráficos, omitir aquele bloco `it()`

---

## Regras

- **App precisa estar rodando** em `http://localhost:1050` para os testes executarem
- **Usar `cy.session()`** para reusar o login entre specs e reduzir tempo de execução
- **Nunca usar `cy.wait(N)`** com número fixo de ms — usar `cy.get(..., {timeout: N})` para aguardar elementos
- **IDs das páginas** seguem o padrão `<pagina>-<componente>` definido em `design-system.yaml`
- Contexto máximo: **8.000 tokens** de saída por arquivo

---

## Como executar

```bash
# Instalar Cypress (apenas uma vez)
cd tests/frontend
npm install

# Abrir Cypress interativo (requer app rodando)
npm run cy:open

# Rodar todos os specs headless (CI)
npm run cy:run

# Rodar um spec específico
npx cypress run --spec "cypress/e2e/cenarios.cy.js"
```

---

## Pós-processamento

1. Verificar que `package.json` e `cypress.config.js` foram criados em `tests/frontend/`
2. Verificar que existe um spec `.cy.js` para cada página em `screens_definition.yaml`
3. Verificar que `cypress/fixtures/usuario.json` tem email real de `mock_data/usuarios.csv`
4. Criar checkpoint step12 e avançar
