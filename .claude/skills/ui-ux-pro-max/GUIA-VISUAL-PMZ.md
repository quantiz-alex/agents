# Guia Visual UI × UX — PMZ Edition
Padrão de design para todas as telas do sistema. Serve como instrução para agentes de código
(Dash/Python) e para revisão de PRs. **Regra de ouro: consistência acima de criatividade.**
Toda tela nova deve parecer feita pela mesma pessoa, no mesmo dia.

---

## 1. Princípios de UX

1. **O dado é o herói.** Layout, cor e tipografia existem para tornar números legíveis e
   comparáveis — nunca para decorar. Nada de gradiente/sombra/ícone que não ajude a ler.
2. **Uma tela = um objetivo.** Cabeçalho diz o que é e o que fazer; o resto sustenta isso.
3. **Comparação em vez de valor solto.** Sempre que houver "antes × depois" (atual × simulado),
   mostre os dois + o delta em % com cor semântica. O usuário decide em 1 segundo.
4. **Cor com significado, não com marca.** Primária = navegação/ação primária.
   Verde = melhora/positivo. Vermelho = piora/negativo/erro. Âmbar = atenção/revisar.
   Azul/cinza = neutro/informativo. Nunca pinte gráficos inteiros de uma cor só.
5. **Densidade para quem usa o dia todo.** Analistas veem muitas linhas; aprovadores/diretoria
   veem resumo. Tabelas compactas, KPIs generosos.
6. **Sem tela vazia e sem tela sufocada.** Conteúdo ocupa a altura útil; respiro consistente.
7. **Estado sempre visível.** Status (Aprovado/Pendente/Rejeitado, Ativo/Inativo) é sempre
   um badge colorido — nunca só texto.

---

## 2. Tokens de estilo (fonte única da verdade)

Defina isto uma vez (Python/YAML) e **só** use estes valores. Sem cores/tamanhos "soltos".

### Cores
| Papel | Valor | Uso |
|---|---|---|
| Primária (marca) | `{primary}` | nav ativa, botão primário, ícone de título |
| Primária hover | `{primary_hover}` | hover do primário e links |
| Fundo app | `#f8fafc` | fundo geral da área de conteúdo |
| Superfície (card) | `#ffffff` | cards, tabelas, filtros |
| Borda | `#e2e8f0` | contorno de cards e linhas |
| Borda linha tabela | `#eef2f7` | separador de linhas |
| Fundo cabeçalho tabela | `#f8fafc` | thead e faixas de apoio |
| Sidebar | `#ffffff` | fundo do menu lateral (com border-right) |
| Texto forte | `#1e293b` | títulos, valores |
| Texto padrão | `#374151` | corpo |
| Texto secundário | `#64748b` | rótulos, legendas |
| Texto fraco | `#94a3b8` | metadados, placeholders |
| **Semântico — positivo** | texto `#166534` / fundo `#dcfce7` | melhora, Aprovado, Ativo |
| **Semântico — negativo** | texto `#991b1b` / fundo `#fee2e2` | piora, Rejeitado |
| **Semântico — atenção** | texto `#92400e` / fundo `#fef3c7` | Pendente, revisar |
| **Semântico — info** | texto `#1e40af` / fundo `#dbeafe` | Simulado, tags neutras |

### Tipografia
- Fonte de interface: **system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif** (humanista limpa)
- Fonte de números: **monospace** com `font-variant-numeric: tabular-nums` — **toda** coluna
  numérica, KPI, preço, %, data e código usa mono tabular (alinha casas decimais).
- Escala: título de página `1.25rem/fw-semibold`; título de card `0.875rem/fw-semibold`; 
  corpo `0.875rem`; rótulo/eyebrow `0.7rem/fw-bold uppercase letter-spacing`; 
  valor de KPI `1.5rem–2rem/fw-bold`.

### Espaçamento e forma
- Grade base **4px** (Bootstrap spacing 0–5: 0, 0.25rem, 0.5rem, 1rem, 1.5rem, 3rem)
- Padding de card `1rem`. Gap entre cards `0.75rem` (mb-3).
- Raio: card `0.375rem`; input/botão `0.375rem`; badge/pill `20px`; chip `6px`.
- Borda de card: `1px solid #e2e8f0`. KPI leva **borda esquerda de 4px** na cor semântica.

---

## 3. Estrutura da página (shell)

```
┌──────────┬─────────────────────────────────────────────┐
│ SIDEBAR  │  CABEÇALHO DE PÁGINA (título + ações)        │
│ 240px    │  ── faixa de filtros (card) ──               │
│ branca   │  ── KPIs / conteúdo ──                       │
│ border   │  ── tabelas / gráficos ──                    │
└──────────┴─────────────────────────────────────────────┘
```

- Conteúdo com padding `px-4 py-3` (1.5rem horizontal, 1rem vertical).
- **Sidebar:** logo/marca no topo; itens **agrupados** (opcional) com label de grupo;
  cada item tem **ícone Bootstrap Icons** + label; item ativo em fundo primário com
  opacidade ou pill destacado; footer fixo no rodapé.
- **Ícones:** sempre Bootstrap Icons (`bi bi-*`), 1rem na nav, 0.875rem em botões.

---

## 4. Componentes padrão

### Cabeçalho de página (obrigatório em toda tela)
Ícone da seção (cor primária) + `H4` título + subtítulo cinza de uma linha, com os
botões de ação alinhados à direita (primário + "Exportar" ghost).

### Card de KPI
Rótulo em eyebrow · valor grande (mono) · linha "de {baseline}" · **badge de delta** com seta
▲/▼ e % na cor semântica. Borda esquerda 4px = cor do delta. Nunca mostrar só o valor final.

### Filtros
Sempre dentro de um card branco no topo, rótulo `dbc.Label` acima de cada campo, alinhados à base,
botão **Filtrar** primário à direita com `className="w-100"`. Opcional: linha de resumo ("afeta 1.284 itens").

### Tabela de dados (AG Grid)
- Cabeçalho: fundo `#f8fafc`, texto uppercase small.
- Numérico alinhado à **direita** e em mono tabular; texto à esquerda; status/flag ao centro.
- Separador `1px #eef2f7`. Linha que exige ação (ex.: Pendente) recebe leve fundo âmbar.
- **Sem truncar colunas**: dê largura adequada, use chip para UF/código, ou scroll horizontal.
- Rodapé com paginação (20 itens por página padrão).
- Ações por linha como link discreto (Editar/Desativar), não botão pesado.

### Badges / chips
- **Pill** (raio 20) para status: Aprovado (verde), Pendente (âmbar), Rejeitado (vermelho),
  Ativo/Inativo. **Chip** (raio 6) para categoria/dimensão/perfil (azul, roxo, ciano neutros).
- Fator/variação em %: `+1,50%` verde, `−10,0%` vermelho, `0,00%` cinza. Sempre com sinal.

### Botões
- Primário: fundo primário, texto branco, fw-bold, raio 0.375rem. 
- Ghost: branco, borda `#cbd5e1`, texto slate.
- Destrutivo: texto/borda vermelha sobre branco. Ícone opcional à esquerda.

### Gráficos (Plotly)
- Paleta categórica ordenada: primária, verde, âmbar, vermelho, azul.
- Rótulos de fatia/eixo **fora** da área colorida (em legenda), nunca sobre a cor.
- Barras com cantos arredondados; variação +/- com verde/vermelho a partir de um zero central.
- Template `plotly_white`, fundos transparentes, margens enxutas.

---

## 5. Regras de conteúdo e microcopy

- Português, tom direto. Rótulos curtos e específicos ("Preço Médio", não "Valor").
- Moeda: `R$ 1.969.961` (sem centavos em KPI executivo; com centavos em tabela de preço).
- Percentual sempre com sinal e vírgula decimal (`+3,7%`). Datas `dd/mm/aaaa`.
- Vazio ≠ em branco: mostrar estado vazio explicativo ("Nenhum cenário salvo ainda").

---

## 6. Mapeamento para Dash/Python

- **Tokens:** centralize as cores em um dict Python (`tokens.py`) ou YAML e injete via 
  `className`/`style`. Não repita hex espalhados pelo código.
- **Tabelas:** `dash_ag_grid.AgGrid` — use `columnDefs` com `cellClass` para badges de
  status e cores de variações; `type="numericColumn"` para colunas numéricas com mono tabular;
  `headerClass` com o fundo `#f8fafc`. Prefira largura fixa por coluna a truncar.
- **KPIs:** componente reutilizável `kpi_card(label, atual, simulado, delta)` que já calcula a
  cor do delta — não montar card na mão em cada página.
- **Gráficos:** `plotly.express` ou `go.Figure` com `color_discrete_sequence` = paleta categórica; 
  `template="plotly_white"`; `paper_bgcolor="rgba(0,0,0,0)"`; `margin` enxuta.
- **Sidebar/cabeçalho:** um único layout base (`app_shell(page_title, subtitle, actions, content)`)
  reutilizado por todas as páginas. Isso garante o padrão automaticamente.
- **Ícones:** Bootstrap Icons (`bi bi-*`) via CDN, referenciados por classe.

---

## 7. Biblioteca de Componentes Reutilizáveis

### Estrutura recomendada:
```
frontend/
├── components/
│   ├── tokens.py          # Cores, tipografia, espaçamento, helpers
│   ├── ui_components.py   # app_shell, kpi_card, data_table, buttons
│   ├── charts.py          # Helpers de gráficos Plotly padronizados
│   └── sidebar.py         # Sidebar com navegação
├── pages/
│   └── <page>/
│       ├── <page>_page.py
│       ├── <page>_components.py
│       ├── <page>_queries.py
│       └── <page>_callbacks.py
└── app.py
```

### Componentes essenciais:

**`app_shell(active_key, icon_key, title, subtitle, content, actions=None)`**
- Retorna layout completo com sidebar + header + content
- Garante consistência em todas as páginas
- Sidebar com estado ativo automático

**`kpi_card(label, atual, simulado, delta_pct, better="up")`**
- KPI com comparação atual × simulado
- Delta colorido com seta ▲/▼
- Borda lateral na cor semântica
- `better`: "up" (subir é bom), "down" (subir é ruim), "neutral"

**`data_table(df, id, numeric_cols=None, status_col=None, page_size=20)`**
- AG Grid já estilizada
- Badges automáticos para coluna de status
- Mono tabular para colunas numéricas
- Paginação padrão

**`page_header(icon_key, title, subtitle, actions=None)`**
- Header padrão com ícone + título + ações
- Alinhamento consistente

**`card(title, body, right=None)`**
- Card genérico com header/body
- Opcional: info à direita do título

---

## 8. Checklist antes de publicar uma tela

- [ ] Usa o `app_shell` (sidebar + cabeçalho padrão + ações à direita).
- [ ] Só usa cores/tamanhos/raios dos tokens — nenhum valor "solto".
- [ ] Todo número em mono tabular e alinhado à direita.
- [ ] Todo status/flag é badge colorido, não texto.
- [ ] Comparações mostram atual × simulado + delta com cor semântica.
- [ ] Nenhuma coluna truncada de forma ilegível; tabela ocupa a largura útil.
- [ ] Gráfico com legenda fora das cores e paleta categórica (não tudo de uma cor).
- [ ] Botão primário único por contexto; ações secundárias ghost.
- [ ] Estados de vazio/carregando/erro previstos.
- [ ] Espaçamento consistente; nada sufocado nem oceano de branco.
- [ ] Raiz da página: `html.Div(className="page-wrapper px-4 py-3", style={"background": "#f8fafc", "minHeight": "100vh"})`
- [ ] Nenhum `dbc.Container` como raiz de página.
- [ ] Filtros em card compacto no topo com botão `className="w-100"`.
- [ ] KPIs em Row com `id="<page>-kpis-row"` para atualização via callback.
- [ ] AG Grid com `floatingFilter=True`, `suppressMenu=True`, `rowHeight=44`, paginação 20.
- [ ] Plotly com `template="plotly_white"`, fundos transparentes, altura 300px.
- [ ] IDs no padrão `<page>-<component>`.
- [ ] Tipagem Python em todas as funções.

### Checklist de produto (v4 — "quero comprar")
- [ ] Tela abre com dados; grids/gráficos nunca vazios com o mock padrão.
- [ ] KPI de comparação só onde há baseline; senão `kpi_simple` (com sparkline quando há série).
- [ ] Grid: FK → nome legível, moeda/percentual/data formatados, status como pill, ordenação padrão.
- [ ] Todo drill-down do roadmap funciona (clique → grid filtrado → chip ✕ para limpar → gráfico destaca a seleção).
- [ ] Simulação com `recalc_mode: live` reage aos sliders sem botão e abre já calculada.
- [ ] Detalhar em modal central com ficha + relacionados (e botão do assistente) quando há `detalhar`/`detail_panel`.
- [ ] `empty_state` com texto do roadmap; `loading` em tudo que callback atualiza; `toast` em toda ação; `confirm_modal` em decisões/destrutivas.
- [ ] Botões restritos somem para roles sem permissão; sidebar mostra só telas acessíveis.
- [ ] Shell: Home (âncoras, atalhos, pendências), sidebar com grupos + usuário + Sair + badges, login split com chips de demo.
- [ ] Breadcrumb `Grupo › Tela`, subtítulo = objetivo do usuário, chip "dados até dd/mm/aaaa".

---

## 9. Anti-Padrões (NUNCA FAZER)

❌ **Valor solto sem comparação** — sempre mostrar baseline + delta  
❌ **Hex/style inline** — usar tokens e className  
❌ **Status como texto** — usar badge colorido  
❌ **Gráfico monocromático** — usar paleta categórica  
❌ **Coluna truncada** — dar largura adequada ou scroll  
❌ **dbc.Container como raiz** — usar html.Div com page-wrapper  
❌ **Números sem mono tabular** — sempre usar font mono para números  
❌ **Filtro sem botão** — sempre ter botão "Filtrar" explícito  
❌ **Grid sem paginação** — sempre paginar com 20 itens  
❌ **Callback sem loading** — envolver em dcc.Loading se > 300ms  

---

## 10. Exemplos de Código

### KPI Card com Comparação
```python
from components.ui_components import kpi_card, kpi_row

kpis = [
    kpi_card("Faturamento atual × simulado", "R$ 1.899.674", "R$ 1.969.961", +3.7, "up"),
    kpi_card("Custo atual × simulado", "R$ 1.181.668", "R$ 1.335.509", +13.0, "down"),
    kpi_card("Margem atual × simulada", "R$ 718.005", "R$ 634.452", -11.6, "up"),
]

layout = kpi_row(kpis)  # Row: todos os KPIs numa linha (larguras iguais a partir de lg)
```

### Data Table com Badges
```python
from components.ui_components import data_table

df = pd.DataFrame([...])
table = data_table(
    df, 
    id="precos-grid",
    numeric_cols=["Custo", "Markup", "Preço"],
    status_col="Status",
    page_size=20
)
```

### App Shell Completo
```python
from components.ui_components import app_shell, button

def layout():
    return app_shell(
        active_key="dashboard",
        icon_key="speedometer2",
        title="Dashboard de Precificação",
        subtitle="Visão executiva comparando o cenário atual com o simulado ativo.",
        actions=[button("Exportar", primary=False, icon_key="download")],
        content=[kpi_row(kpis), card("Dados", table)]
    )
```

### Gráfico Padronizado
```python
from components.charts import bar_ranking, donut

# Ranking horizontal
fig1 = bar_ranking(
    ["Bosch", "Freedom", "Fulgor", "Zetta", "Moura"],
    [612, 548, 447, 218, 92]
)

# Donut com legenda externa
fig2 = donut(
    ["Pesadas/Caminhão", "Carro Médio/SUV", "Carro Popular"],
    [83.1, 7.6, 7.3]
)
```

---

**Lembre-se:** O padrão vem da **estrutura compartilhada**, não da disciplina. 
Se algo não existe como componente, crie-o na biblioteca e reutilize — não estilize 
inline caso a caso.
