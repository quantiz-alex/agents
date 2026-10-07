# Cenários mock conectados entre telas

Aplicar a módulos de arquitetura/configuração cujos parâmetros alimentam simulações e outras telas. Este contrato prevalece sobre exemplos antigos de estado isolado por página. Não exige banco, API ou gravação em CSV.

## Contrato declarativo

Gerar `docs/scenario_dependencies.yaml` a partir do roadmap e business_logic, antes de gerar páginas:

```yaml
version: 1
mode: mock
scenarios:
  arquitetura:
    source_page: arquitetura
    parameters:
      - name: markup
        default: 10
        rule_ids: [RN-001]
        # Nome/valor são apenas exemplos; usar parâmetros reais do roadmap.
    scope_fields: [categoria_id]
    consumers:
      - page: arquitetura
        outputs: [preco_simulado, receita_simulada]
        default_view: draft
      - page: dashboard
        outputs: [receita]
        default_view: applied
    requires_approval: false
```

Cada parâmetro deve apontar para uma regra real, campos calculados e telas consumidoras. Compartilhar entidade não basta para inferir dependência. Se faltar fórmula, registrar lacuna e bloquear Aplicar para esse cálculo; não inventar impacto percentual. Gerar `frontend/services/scenario_engine.py` com funções puras das regras reais. Todas as telas usam esse motor antes de agregar KPIs, gráficos e grids. Recalcular por item antes de somar; preservar unidades, arredondamento e escopo. Fora do escopo, preservar valores aplicados. Esta primeira versão suporta um cenário ativo por arquitetura e um escopo explícito; múltiplas arquiteturas usam stores separados por chave.

## Estado e interação

Copiar `templates/demo_scenario.py` para `frontend/components/demo_scenario.py`. O estado tem baseline original, applied, draft, preview com fingerprint, revision e applied_revision. O baseline deriva dos parâmetros iniciais, não de números de KPI inventados.

- Editar: atualizar rascunho e invalidar resultado anterior; valores aplicados permanecem.
- Simular: calcular e mostrar Atual × Simulado na própria tela de arquitetura. Preferir evento `simulate` atômico com parâmetros, escopo, fingerprint e resultados calculados pelo motor.
- Ver impacto detalhado: navegar com chave da arquitetura, scenario_view=draft, escopo e revision. Reusar cenário no store; nunca duplicar parâmetros na URL ou manter cópia independente em outra tela.
- Aplicar na demo: aceitar apenas preview válido para parâmetros/escopo atuais. Atualizar applied e todas as telas consumidoras. Se houver aprovação declarada, enviar snapshot para aprovação e aplicar apenas quando aprovado; não criar aprovação automaticamente.
- Descartar: restaurar draft a partir de applied, sem desfazer alterações já aplicadas.
- Restaurar demonstração: confirmação e reset para baseline, incluindo cenários salvos e decisões mock da sessão. Nunca modificar dados-fonte compartilhados. Logout deve limpar o estado da persona anterior.

Exibir nomes de produto: Atual, Simulado, Aplicado na demonstração. Detalhamento do rascunho deve indicar Simulação. Telas comuns usam applied; navegação explícita de aprofundamento usa draft. Voltar preserva o rascunho. Refresh preserva sessão; restaurar demo redefine tudo. Se o contexto pedir revisão antiga, avisar e usar revisão atual explicitamente ou impedir abertura; nunca misturar resultados.

## Integração Dash sem IDs ausentes

No shell, criar `dcc.Store(id="demo-scenario", storage_type="session")` e `dcc.Store(id="demo-active", storage_type="memory")`. Para múltiplas arquiteturas, guardar dict por chave. Um único callback é dono de demo-scenario e demo-active, incluindo inicialização/reset/logout. Inicializar por usuário; usar baseline declarada e `new_session`.

Eventos de páginas usam `dcc.Store(id={"type": "demo-scenario-event", "page": PAGE})` e o shell escuta `Input({"type": "demo-scenario-event", "page": ALL}, "data")`. Ausência de páginas produz lista vazia. O dono recebe estado como State, valida evento/id/revisão e chama `dispatch(state, event, calculate)` com o motor real. Erros não mudam cenário; emitir feedback global. Não registrar callbacks dentro do layout.

O callback de página que captura parâmetros é disparado por controles locais e usa cenário global somente como State. Emitir evento com uuid e expected_revision. Não emitir evento ao apenas montar a página. Exibir resultados com callback local disparado pelo botão Simular, usando o mesmo motor; o shell recalcula/valida o payload antes de guardar. Desabilitar Aplicar até o resultado atual estar confirmado no store. Evitar envios concorrentes: controles bloqueados enquanto um evento aguarda confirmação; tratar revisão desatualizada com recálculo, não sobrescrita silenciosa. Um writer sozinho não é garantia contra respostas fora de ordem.

`demo-active` recebe {applied_revision, scenario_key} apenas em aplicar/reset/inicialização; em edit/preview retornar no_update. O roteador usa Input(demo-active.data) e State(demo-scenario.data), e passa `scenario_state` e `workflow_context` ao layout. Assim aplicar atualiza a tela atual e consumidores futuros, mas editar não remonta formulário e não perde foco. Todos os layouts aceitam `layout(workflow_context=None, scenario_state=None)`. Ao abrir detalhe, o contexto define view; queries resolvem `scenario_for_view` e chamam motor compartilhado. Nunca colocar Input global de cenário em callback com Output de página desmontada.

Navegação é responsabilidade do dono de url/workflow-context no shell. Transferir apenas chave/view/revision/escopo. Não apagar contexto em callbacks das páginas. Se consumidor atual precisar atualizar sem remount, usar IDs de dicionário e Outputs ALL com retorno alinhado aos componentes presentes; não usar Outputs string ausentes.

## Critérios de aceite da demo

1. Alterar um parâmetro conhecido muda os outputs declarados de acordo com a fórmula.
2. Comparativo da arquitetura e detalhe mostram os mesmos totais e escopo.
3. Navegar e voltar preserva parâmetros; refresh preserva sessão.
4. Antes de aplicar, dashboard comum mantém applied. Depois, reflete os novos números.
5. Editar novamente invalida preview; resultado antigo não pode ser aplicado.
6. Descartar restaura applied; reset restaura baseline e decisões da sessão.
7. Duas sessões/personas não compartilham alterações; CSVs originais ficam intactos.
8. Console sem IDs ausentes/Outputs duplicados na jornada completa.

Executar `templates/scripts/check_demo_scenario.py` para regressão do estado. Esse teste não substitui smoke no navegador e paridade das fórmulas específicas geradas.
