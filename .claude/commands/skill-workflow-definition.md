# Skill — Workflow Definition

Gera a definição de workflows (jornadas de usuário) que conectam telas interdependentes em projetos de pricing e revenue management.

## Quando usar

Invocada automaticamente pelo `frontend-builder` no **Step 6.5** (após gerar `screens_definition.yaml`), ou diretamente:

```
/skill-workflow-definition
```

---

## O que é um Workflow

Um **workflow** é uma jornada de usuário que conecta múltiplas telas em uma sequência lógica de passos, permitindo:

1. **Transferência de contexto** — Dados fluem automaticamente entre telas relacionadas
2. **Navegação inteligente** — Botões de "próximos passos" aparecem contextualmente
3. **Rastreabilidade** — Histórico de navegação e decisões do usuário
4. **Visibilidade** — Breadcrumb mostra progresso no fluxo

### Exemplo de Workflow Real:

```
Arquitetura de Preços → Simulação de Cenário → Salvar Cenário → 
Enviar para Aprovação → Fila de Aprovações → Aprovar/Rejeitar → 
Dashboard (reflete mudanças)
```

---

## Arquivos gerados

```
docs/workflows.yaml    ← definição de todos os workflows do projeto
```

---

## Estrutura de `workflows.yaml`

```yaml
# Workflows — Jornadas de usuário entre telas interdependentes
# Gerado automaticamente pelo frontend-builder Step 6.5

workflows:
  <workflow_id>:
    name: string
    description: string
    user_roles: [string]        # roles que podem executar este workflow
    category: string            # análise | inovação | implementação | controle
    steps:
      - id: string
        screen: string          # route da tela (ex: simulacao-precos)
        description: string
        icon: string            # ícone Bootstrap Icons
        inputs: [string]        # campos recebidos do step anterior
        outputs: [string]       # campos fornecidos para próximo step
        next_actions:
          - label: string
            target: string      # route da próxima tela
            icon: string
            primary: bool
            context_transfer: [string]   # campos a transferir
            condition: string   # expressão opcional (ex: "cenario_salvo")
            roles: [string]     # roles que veem este botão (opcional)

# Mapeamento inverso: tela → workflows que a incluem
screen_workflows:
  <screen_route>:
    - workflow_id: string
      step_id: string
```

---

## Lógica de Geração

### Input

Ler `docs/screens_definition.yaml` e `docs/requirements.yaml`.

### Análise

Antes de definir navegação, mapear dependências de parâmetros conforme `skill-demo-scenario.md`. Gerar `docs/scenario_dependencies.yaml`. Uma conexão entre telas deve transferir chave do cenário, view (draft/applied), revisão e escopo; breadcrumb sozinho não propaga cálculos. Na arquitetura mostrar o impacto principal antes de navegar. Aprovação só quando explicitamente declarada; os exemplos de aprovação abaixo não são obrigatórios para toda simulação.

1. **Identificar fluxos naturais** baseados em:
   - Telas de simulação → conectam com aprovação somente quando declarada; caso contrário aplicar na demo
   - Telas de configuração → conectam com simulação
   - Dashboards → são destino final ou ponto de partida
   - Relatórios → são destino final

2. **Detectar dependências** entre telas:
   - `data_sources` compartilhados
   - `actions` que referenciam outras telas
   - `screen_type: simulation` → precede `approval_queue` apenas se o workflow exigir aprovação
   - `screen_type: approval_queue` → precede dashboards

3. **Agrupar por categoria** (metodologia de Pricing & Revenue Management):
   - **Análise:** Diagnóstico, dashboards de oportunidades
   - **Inovação:** Simulações, testes de cenários
   - **Implementação:** Aprovações, planos de ação, quick wins
   - **Controle:** Dashboards de monitoramento, relatórios

### Output

Gerar `docs/workflows.yaml` com:
- Pelo menos 1 workflow principal (ex: `pricing_simulation_flow`)
- Workflows secundários conforme módulos do projeto
- Mapeamento `screen_workflows` para lookup reverso

---

## Exemplo Completo

```yaml
workflows:
  pricing_simulation_flow:
    name: "Fluxo de Simulação e Aprovação de Preços"
    description: "Jornada completa desde configuração de arquitetura até aprovação e monitoramento"
    user_roles: [analista, supervisor, admin]
    category: inovação
    steps:
      - id: config_architecture
        screen: arquitetura-precos
        description: "Configurar regras de margem e arquitetura"
        icon: diagram-3
        inputs: []
        outputs: [arquitetura_id, regras_margem, margem_minima]
        next_actions:
          - label: "Simular Impacto nos Preços"
            target: simulacao-precos
            icon: calculator
            primary: true
            context_transfer: [arquitetura_id, regras_margem, margem_minima]
            roles: [analista, supervisor, admin]
      
      - id: simulate_scenario
        screen: simulacao-precos
        description: "Executar simulação com parâmetros"
        icon: calculator
        inputs: [arquitetura_id, regras_margem, margem_minima]
        outputs: [cenario_id, resultado_simulacao, variacao_receita]
        next_actions:
          - label: "Salvar e Enviar para Aprovação"
            target: fila-aprovacoes
            icon: send
            primary: true
            context_transfer: [cenario_id, resultado_simulacao, variacao_receita]
            condition: "cenario_salvo"
            roles: [analista]
          - label: "Ajustar Arquitetura"
            target: arquitetura-precos
            icon: arrow-left
            primary: false
            context_transfer: [arquitetura_id]
            roles: [analista, supervisor, admin]
      
      - id: approval_queue
        screen: fila-aprovacoes
        description: "Supervisor avalia cenário simulado"
        icon: list-check
        inputs: [cenario_id, resultado_simulacao, variacao_receita]
        outputs: [status_aprovacao, comentario_aprovacao, aprovado_por]
        next_actions:
          - label: "Ver Dashboard Atualizado"
            target: dashboard
            icon: speedometer2
            primary: true
            context_transfer: [cenario_id, status_aprovacao]
            condition: "status_aprovacao == 'Aprovado'"
            roles: [supervisor, admin]
          - label: "Revisar Simulação"
            target: simulacao-precos
            icon: pencil
            primary: false
            context_transfer: [cenario_id, comentario_aprovacao]
            condition: "status_aprovacao == 'Rejeitado'"
            roles: [analista]
      
      - id: dashboard_monitoring
        screen: dashboard
        description: "Monitorar impacto das mudanças aprovadas"
        icon: speedometer2
        inputs: [cenario_id, status_aprovacao]
        outputs: []
        next_actions:
          - label: "Nova Simulação"
            target: simulacao-precos
            icon: plus-circle
            primary: false
            roles: [analista, supervisor, admin]

  revenue_analysis_flow:
    name: "Análise de Revenue Management"
    description: "Diagnóstico → Oportunidades → Implementação → Controle"
    user_roles: [analista, supervisor, admin]
    category: análise
    steps:
      - id: diagnostic
        screen: dashboard-diagnostico
        description: "Análise estatística e identificação de oportunidades"
        icon: graph-up
        inputs: []
        outputs: [key_issues, oportunidades_priorizadas, baseline_metrics]
        next_actions:
          - label: "Criar Plano de Ação"
            target: plano-acoes
            icon: clipboard-check
            primary: true
            context_transfer: [key_issues, oportunidades_priorizadas, baseline_metrics]
            roles: [supervisor, admin]
      
      - id: action_plan
        screen: plano-acoes
        description: "Definir soluções, quick wins e responsáveis"
        icon: clipboard-check
        inputs: [key_issues, oportunidades_priorizadas, baseline_metrics]
        outputs: [plano_id, acoes_priorizadas, quick_wins]
        next_actions:
          - label: "Monitorar Implementação"
            target: dashboard-controle
            icon: speedometer2
            primary: true
            context_transfer: [plano_id, acoes_priorizadas]
            roles: [supervisor, admin]
          - label: "Simular Impacto Financeiro"
            target: simulacao-impacto
            icon: calculator
            primary: false
            context_transfer: [plano_id, baseline_metrics]
            roles: [analista, supervisor]
      
      - id: control_dashboard
        screen: dashboard-controle
        description: "Painel de controle contínuo com KPIs e contingências"
        icon: speedometer2
        inputs: [plano_id, acoes_priorizadas]
        outputs: [metricas_atuais, desvios_identificados]
        next_actions:
          - label: "Ajustar Plano de Ação"
            target: plano-acoes
            icon: pencil
            primary: false
            context_transfer: [plano_id, desvios_identificados]
            condition: "desvios_identificados > 0"
            roles: [supervisor, admin]

screen_workflows:
  arquitetura-precos:
    - workflow_id: pricing_simulation_flow
      step_id: config_architecture
  
  simulacao-precos:
    - workflow_id: pricing_simulation_flow
      step_id: simulate_scenario
  
  fila-aprovacoes:
    - workflow_id: pricing_simulation_flow
      step_id: approval_queue
  
  dashboard:
    - workflow_id: pricing_simulation_flow
      step_id: dashboard_monitoring
  
  dashboard-diagnostico:
    - workflow_id: revenue_analysis_flow
      step_id: diagnostic
  
  plano-acoes:
    - workflow_id: revenue_analysis_flow
      step_id: action_plan
  
  dashboard-controle:
    - workflow_id: revenue_analysis_flow
      step_id: control_dashboard
```

---

## Regras de Geração

### Workflows Obrigatórios

1. **Se existir tela de simulação + approval_queue:**
   - Criar workflow `pricing_simulation_flow` conectando ambas

2. **Se existir dashboard + relatórios:**
   - Criar workflow `reporting_flow` conectando análise → relatório

3. **Se existir tela de configuração + simulação:**
   - Conectar configuração → simulação no workflow principal

### Context Transfer Automático

- **Simulação → Aprovação:** `[cenario_id, resultado_simulacao, variacao_*]`
- **Aprovação → Dashboard:** `[cenario_id, status_aprovacao]`
- **Configuração → Simulação:** `[*_id, regras_*, parametros_*]`
- **Diagnóstico → Plano:** `[key_issues, oportunidades_*, baseline_*]`

### Condições Padrão

- `"cenario_salvo"` — após salvar cenário em simulação
- `"status_aprovacao == 'Aprovado'"` — após aprovação
- `"status_aprovacao == 'Rejeitado'"` — após rejeição
- `"desvios_identificados > 0"` — quando há alertas no dashboard

---

## Integração com Frontend-Builder

O `frontend-builder` invoca esta skill no **Step 6.5** (após `screens_definition.yaml`):

1. Ler `docs/screens_definition.yaml` e `docs/requirements.yaml`
2. Identificar padrões de fluxo (simulação, aprovação, dashboards)
3. Gerar `docs/workflows.yaml` com workflows detectados
4. Atualizar `screens_definition.yaml` com campo `workflow` em cada página
5. Checkpoint: `✓ Step 6.5 → workflows.yaml`

---

## Validação

Após gerar `workflows.yaml`, validar:

- [ ] Todos os `screen` referenciados existem em `screens_definition.yaml`
- [ ] Todos os `user_roles` existem em `requirements.yaml`
- [ ] `context_transfer` lista apenas campos de `outputs` do step anterior
- [ ] Cada workflow tem pelo menos 2 steps
- [ ] Nenhum step órfão (sem `next_actions`)
- [ ] Categorias válidas: análise | inovação | implementação | controle

---

## Restrições

- Workflows são **descritivos**, não executáveis — servem para gerar UI contextual
- Não gerar lógica de validação de condições — apenas documentar
- Máximo de 5 workflows por projeto (evitar complexidade excessiva)
- Cada tela pode participar de múltiplos workflows
- Tipagem: todos os campos são strings ou listas de strings
- Contexto máximo: **8.000 tokens** de saída

---

## Exemplo de Uso pelo Frontend-Builder

```python
# No Step 6.5 do frontend-builder

from pathlib import Path
import yaml

def generate_workflows():
    screens = yaml.safe_load(Path("docs/screens_definition.yaml").read_text())
    requirements = yaml.safe_load(Path("docs/requirements.yaml").read_text())
    
    workflows = detect_workflows(screens, requirements)
    
    Path("docs/workflows.yaml").write_text(
        yaml.dump(workflows, allow_unicode=True, sort_keys=False)
    )
    
    # Atualizar screens_definition.yaml com referências de workflow
    for screen_route, screen_data in screens["pages"].items():
        if screen_route in workflows["screen_workflows"]:
            screen_data["workflow"] = workflows["screen_workflows"][screen_route]
    
    Path("docs/screens_definition.yaml").write_text(
        yaml.dump(screens, allow_unicode=True, sort_keys=False)
    )
```
