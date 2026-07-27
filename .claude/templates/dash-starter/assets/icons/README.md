# Ícones Bootstrap Icons

Esta pasta deve conter ícones SVG do Bootstrap Icons para uso na aplicação.

## Como adicionar ícones

1. Acesse https://icons.getbootstrap.com/
2. Busque o ícone desejado (ex: "speedometer2", "download", "plus")
3. Baixe o SVG
4. Salve nesta pasta com o nome do ícone (ex: `speedometer2.svg`)

## Ícones comuns para aplicações de precificação

- `speedometer2.svg` — Dashboard
- `tag.svg` — Preços/Tags
- `list-check.svg` — Fila de aprovações
- `diagram-3.svg` — Arquitetura
- `table.svg` — Lista/Tabela
- `folder.svg` — Cadastros
- `people.svg` — Gestão de aprovadores
- `gear.svg` — Administração
- `download.svg` — Exportar
- `plus.svg` — Adicionar
- `pencil.svg` — Editar
- `trash.svg` — Excluir
- `check-circle.svg` — Aprovar
- `x-circle.svg` — Rejeitar
- `clock.svg` — Pendente
- `calculator.svg` — Simulação

## Uso no código

```python
from frontend.components.ui_components import icon

# Ícone simples
icon("speedometer2")

# Ícone com tamanho customizado
icon("download", size="1.5rem")
```

Os ícones são renderizados usando CSS mask, então respeitam a cor do contexto (`currentColor`).
