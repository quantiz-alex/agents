"""Gera $LH/templates/LIBRARY_INDEX.md — índice compacto das funções públicas dos templates.

Os agentes leem o ÍNDICE (≈10 KB) em vez do código-fonte das bibliotecas (≈150 KB). Rode após alterar qualquer template:
    python .claude/templates/scripts/build_library_index.py
"""
from __future__ import annotations

import ast
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1]
FILES = [
    ("components-library.py", "frontend/components/ui_components.py"),
    ("charts-library.py", "frontend/components/charts.py"),
    ("workflow_components.py", "frontend/components/workflow_components.py"),
    ("page_common.py", "frontend/pages/_common.py"),
    ("api_client.py", "frontend/api_client.py"),
    ("demo_scenario.py", "frontend/components/demo_scenario.py"),
    ("pricing_assistant.py", "frontend/services/pricing_assistant.py"),
    ("assistant_llm.py", "frontend/services/assistant_llm.py"),
    ("assistant_detail.py", "frontend/services/assistant_detail.py"),
    ("assistant_pages.py", "frontend/services/assistant_pages.py"),
    ("assistant_callbacks.py", "frontend/assistant_callbacks.py"),
    ("pricing_assistant_components.py", "frontend/components/pricing_assistant_components.py"),
]


def _sig(fn: ast.FunctionDef) -> str:
    a = fn.args
    parts = []
    pos = a.posonlyargs + a.args
    defaults = [None] * (len(pos) - len(a.defaults)) + list(a.defaults)
    for arg, d in zip(pos, defaults):
        parts.append(arg.arg + ("=…" if d is not None else ""))
    if a.vararg:
        parts.append("*" + a.vararg.arg)
    for arg, d in zip(a.kwonlyargs, a.kw_defaults):
        parts.append(arg.arg + ("=…" if d is not None else ""))
    if a.kwarg:
        parts.append("**" + a.kwarg.arg)
    return f"{fn.name}({', '.join(parts)})"


def main() -> None:
    out = ["# Índice das bibliotecas do Lighthouse (gerado — não editar à mão)", "",
           "Use este índice para escolher componentes/funções. Copie o template com `cp`; abra o `.py` só para conferir uma assinatura (Grep pelo nome).", ""]
    for src, dest in FILES:
        p = TEMPLATES / src
        if not p.exists():
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"))
        mod_doc = (ast.get_docstring(tree) or "").strip().splitlines()
        out.append(f"## `{src}` → `{dest}`")
        if mod_doc:
            out.append(f"_{mod_doc[0]}_")
        out.append("")
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                doc = (ast.get_docstring(node) or "").strip().splitlines()
                out.append(f"- `{_sig(node)}` — {doc[0] if doc else ''}".rstrip(" —"))
        out.append("")
    (TEMPLATES / "LIBRARY_INDEX.md").write_text("\n".join(out), encoding="utf-8")
    print(f"LIBRARY_INDEX.md: {sum(1 for line in out if line.startswith('- '))} funções")


if __name__ == "__main__":
    main()
