"""
Componentes de Workflow e Navegação Contextual
Biblioteca de componentes para workflows e transferência de contexto entre telas.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from pathlib import Path
import yaml
from typing import Any


# ============================================================================
# HELPERS — Leitura de workflows.yaml
# ============================================================================

def load_workflows() -> dict:
    """Carrega workflows.yaml do projeto."""
    workflows_path = Path(__file__).parent.parent.parent / "docs" / "workflows.yaml"
    if not workflows_path.exists():
        return {"workflows": {}, "screen_workflows": {}}
    return yaml.safe_load(workflows_path.read_text(encoding="utf-8"))


def get_workflow_by_id(workflow_id: str) -> dict | None:
    """Retorna workflow específico por ID."""
    workflows = load_workflows()
    return workflows.get("workflows", {}).get(workflow_id)


def get_workflows_for_screen(screen_route: str) -> list[dict]:
    """Retorna lista de workflows que incluem a tela especificada."""
    workflows_data = load_workflows()
    screen_workflows = workflows_data.get("screen_workflows", {}).get(screen_route, [])
    
    result = []
    for sw in screen_workflows:
        workflow = get_workflow_by_id(sw["workflow_id"])
        if workflow:
            result.append({
                "workflow": workflow,
                "step_id": sw["step_id"],
            })
    return result


def get_current_step(workflow: dict, step_id: str) -> dict | None:
    """Retorna step específico de um workflow."""
    for step in workflow.get("steps", []):
        if step["id"] == step_id:
            return step
    return None


def eval_condition(condition: str, context: dict) -> bool:
    """
    Avalia condição simples baseada no contexto.
    Suporta apenas comparações básicas para segurança.
    """
    if not condition:
        return True
    
    # Condições simples suportadas
    if condition == "cenario_salvo":
        return context.get("cenario_id") is not None
    
    if "==" in condition:
        field, value = condition.split("==")
        field = field.strip()
        value = value.strip().strip("'\"")
        return str(context.get(field)) == value
    
    if ">" in condition:
        field, value = condition.split(">")
        field = field.strip()
        value = int(value.strip())
        return int(context.get(field, 0)) > value
    
    return True


# ============================================================================
# WORKFLOW BREADCRUMB — Navegação visual do progresso
# ============================================================================

def workflow_breadcrumb(
    workflow_id: str,
    current_step_id: str,
    context: dict | None = None,
) -> html.Div:
    """
    Breadcrumb que mostra progresso no workflow e permite navegação contextual.
    
    Args:
        workflow_id: ID do workflow ativo
        current_step_id: ID do step atual
        context: Dados de contexto para avaliar condições
    
    Exemplo visual:
        [✓ Arquitetura] → [● Simulação] → [○ Aprovação] → [○ Dashboard]
    """
    workflow = get_workflow_by_id(workflow_id)
    if not workflow:
        return html.Div()
    
    context = context or {}
    steps = workflow.get("steps", [])
    current_index = next(
        (i for i, s in enumerate(steps) if s["id"] == current_step_id),
        0
    )
    
    breadcrumb_items = []
    
    for i, step in enumerate(steps):
        is_current = step["id"] == current_step_id
        is_completed = i < current_index
        is_accessible = i <= current_index  # pode voltar para steps anteriores
        
        # Ícones de status
        if is_completed:
            status_icon = "check-circle-fill"
            status_text = "✓"
            color = "success"
        elif is_current:
            status_icon = "circle-fill"
            status_text = "●"
            color = "primary"
        else:
            status_icon = "circle"
            status_text = "○"
            color = "muted"
        
        # Botão do step
        breadcrumb_items.append(
            dbc.Button(
                [
                    html.I(className=f"bi bi-{step.get('icon', 'circle')} me-2"),
                    html.Span(status_text, className="me-1"),
                    step["description"],
                ],
                id={"type": "workflow-breadcrumb", "step": step["id"]},
                color=color,
                outline=not is_current,
                size="sm",
                disabled=not is_accessible,
                className="me-2 mb-2",
                href=f"/{step['screen']}" if is_accessible else None,
            )
        )
        
        # Seta entre steps
        if i < len(steps) - 1:
            breadcrumb_items.append(
                html.Span("→", className="mx-2 text-muted align-self-center")
            )
    
    return html.Div([
        html.Div([
            html.I(className="bi bi-signpost-2 me-2 text-primary"),
            html.Strong(workflow["name"], className="text-dark"),
            html.Small(f" — {workflow['category']}", className="text-muted ms-2"),
        ], className="mb-2"),
        html.Div(
            breadcrumb_items,
            className="d-flex flex-wrap align-items-center",
        ),
    ], className="workflow-breadcrumb bg-light p-3 rounded mb-3 border")


# ============================================================================
# WORKFLOW CONTEXT ACTIONS — Botões de próximos passos
# ============================================================================

def workflow_context_actions(
    workflow_id: str,
    current_step_id: str,
    context: dict | None = None,
    user_role: str | None = None,
) -> list[dbc.Button]:
    """
    Retorna lista de botões de ação contextual baseados no workflow.
    
    Args:
        workflow_id: ID do workflow ativo
        current_step_id: ID do step atual
        context: Dados de contexto para avaliar condições
        user_role: Role do usuário atual para filtrar ações
    
    Returns:
        Lista de botões dbc.Button para próximos passos
    """
    workflow = get_workflow_by_id(workflow_id)
    if not workflow:
        return []
    
    context = context or {}
    current_step = get_current_step(workflow, current_step_id)
    if not current_step:
        return []
    
    next_actions = current_step.get("next_actions", [])
    buttons = []
    
    for action in next_actions:
        # Verificar role (se especificado)
        if action.get("roles") and user_role not in action["roles"]:
            continue
        
        # Verificar condição (se especificada)
        if action.get("condition") and not eval_condition(action["condition"], context):
            continue
        
        # Criar botão
        buttons.append(
            dbc.Button(
                [
                    html.I(className=f"bi bi-{action.get('icon', 'arrow-right')} me-2"),
                    action["label"],
                ],
                id={"type": "workflow-action", "target": action["target"]},
                color="primary" if action.get("primary") else "outline-primary",
                size="sm",
                className="me-2",
                href=f"/{action['target']}",
            )
        )
    
    return buttons


# ============================================================================
# WORKFLOW STATUS CARD — Card de status do workflow
# ============================================================================

def workflow_status_card(
    workflow_id: str,
    current_step_id: str,
    context: dict | None = None,
) -> dbc.Card:
    """
    Card mostrando status atual do workflow com progresso visual.
    
    Args:
        workflow_id: ID do workflow ativo
        current_step_id: ID do step atual
        context: Dados de contexto
    
    Returns:
        Card com informações do workflow
    """
    workflow = get_workflow_by_id(workflow_id)
    if not workflow:
        return html.Div()
    
    steps = workflow.get("steps", [])
    current_index = next(
        (i for i, s in enumerate(steps) if s["id"] == current_step_id),
        0
    )
    
    progress_pct = ((current_index + 1) / len(steps)) * 100
    
    return dbc.Card([
        dbc.CardHeader([
            html.I(className="bi bi-diagram-3 me-2"),
            html.Span("Workflow Ativo", className="fw-semibold"),
        ], className="bg-white border-bottom"),
        dbc.CardBody([
            html.H6(workflow["name"], className="mb-2"),
            html.P(workflow["description"], className="text-muted small mb-3"),
            
            # Barra de progresso
            html.Div([
                html.Small(f"Progresso: {current_index + 1}/{len(steps)}", 
                          className="text-muted mb-1 d-block"),
                dbc.Progress(
                    value=progress_pct,
                    color="primary",
                    className="mb-2",
                    style={"height": "8px"},
                ),
            ]),
            
            # Step atual
            html.Div([
                html.Small("Step atual:", className="text-muted d-block mb-1"),
                html.Div([
                    html.I(className=f"bi bi-{steps[current_index].get('icon', 'circle')} me-2 text-primary"),
                    html.Strong(steps[current_index]["description"]),
                ], className="d-flex align-items-center"),
            ]),
        ], className="py-3"),
    ], className="shadow-sm border-0 mb-3")


# ============================================================================
# WORKFLOW NAVIGATION HELPER — Para uso em callbacks
# ============================================================================

def get_context_transfer_data(
    workflow_id: str,
    from_step_id: str,
    to_step_id: str,
    current_context: dict,
) -> dict:
    """
    Retorna dados a serem transferidos entre steps do workflow.
    
    Args:
        workflow_id: ID do workflow
        from_step_id: Step de origem
        to_step_id: Step de destino
        current_context: Contexto atual com dados disponíveis
    
    Returns:
        Dict com dados filtrados para transferência
    """
    workflow = get_workflow_by_id(workflow_id)
    if not workflow:
        return {}
    
    from_step = get_current_step(workflow, from_step_id)
    to_step = get_current_step(workflow, to_step_id)
    
    if not from_step or not to_step:
        return {}
    
    # Encontrar ação que conecta os steps
    next_action = next(
        (a for a in from_step.get("next_actions", []) if a["target"] == to_step["screen"]),
        None
    )
    
    if not next_action:
        return {}
    
    # Transferir apenas campos especificados em context_transfer
    transfer_fields = next_action.get("context_transfer", [])
    transferred_data = {}
    
    for field in transfer_fields:
        if field in current_context:
            transferred_data[field] = current_context[field]
    
    return transferred_data


# ============================================================================
# WORKFLOW SELECTOR — Dropdown para escolher workflow ativo
# ============================================================================

def workflow_selector(current_screen: str, user_role: str | None = None) -> dbc.Select:
    """
    Dropdown para selecionar workflow ativo na tela atual.
    Mostra apenas workflows que incluem a tela atual.
    
    Args:
        current_screen: Route da tela atual
        user_role: Role do usuário para filtrar workflows
    
    Returns:
        dbc.Select com workflows disponíveis
    """
    screen_workflows = get_workflows_for_screen(current_screen)
    
    if not screen_workflows:
        return html.Div()
    
    # Filtrar por role se especificado
    if user_role:
        screen_workflows = [
            sw for sw in screen_workflows
            if user_role in sw["workflow"].get("user_roles", [])
        ]
    
    if not screen_workflows:
        return html.Div()
    
    options = [
        {"label": sw["workflow"]["name"], "value": sw["workflow"].get("id", i)}
        for i, sw in enumerate(screen_workflows)
    ]
    
    return dbc.Select(
        id="workflow-selector",
        options=options,
        value=options[0]["value"] if options else None,
        size="sm",
        className="mb-3",
    )


# ============================================================================
# EXEMPLO DE USO EM PÁGINA
# ============================================================================

"""
Exemplo de uso em uma página:

from frontend.components.workflow_components import (
    workflow_breadcrumb,
    workflow_context_actions,
    workflow_status_card,
)

def layout():
    # Obter workflow context do dcc.Store
    workflow_context = {
        "current_workflow": "pricing_simulation_flow",
        "current_step": "simulate_scenario",
        "context_data": {
            "arquitetura_id": 123,
            "regras_margem": {...},
        },
    }
    
    user_role = "analista"
    
    return html.Div([
        # Breadcrumb de progresso
        workflow_breadcrumb(
            workflow_context["current_workflow"],
            workflow_context["current_step"],
            workflow_context["context_data"],
        ),
        
        # Conteúdo da página
        html.H4("Simulação de Cenários"),
        
        # ... componentes da página ...
        
        # Botões de próximos passos (contextuais)
        html.Div([
            html.H6("Próximos Passos", className="mb-2"),
            html.Div(
                workflow_context_actions(
                    workflow_context["current_workflow"],
                    workflow_context["current_step"],
                    workflow_context["context_data"],
                    user_role,
                ),
                className="d-flex flex-wrap",
            ),
        ], className="mt-4"),
        
        # Sidebar com status do workflow (opcional)
        workflow_status_card(
            workflow_context["current_workflow"],
            workflow_context["current_step"],
            workflow_context["context_data"],
        ),
    ])
"""
