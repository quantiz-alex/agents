"""Validação determinística do projeto gerado — substitui a leitura do skill00 pelo modelo nas etapas de tela/página/app/assistente.

Uso (na raiz do projeto):  python "$LH/templates/scripts/validate_project.py" [screens|pages|app|assistant|all]
Saída: linhas "ERRO ..." / "AVISO ..." e um resumo; exit code 1 se houver erro. Só a saída entra no contexto do agente.
As listas canônicas vêm de $LH/commands/skill00-validator.md (fonte única).
"""
from __future__ import annotations

import importlib
import py_compile
import re
import sys
from pathlib import Path

import yaml

LH = Path(__file__).resolve().parents[2]
ROOT = Path.cwd()
ERROS: list[str] = []
AVISOS: list[str] = []


def canon() -> dict:
    txt = (LH / "commands" / "skill00-validator.md").read_text(encoding="utf-8")
    m = re.search(r"## Listas Canônicas.*?```yaml\n(.*?)```", txt, re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def _load(p: str) -> dict:
    f = ROOT / p
    if not f.exists():
        ERROS.append(f"{p} ausente")
        return {}
    return yaml.safe_load(f.read_text(encoding="utf-8")) or {}


def screens() -> None:
    c = canon()
    sd = _load("docs/screens_definition.yaml")
    pages = sd.get("pages") or {}
    rotas: dict[str, str] = {}
    for slug, p in pages.items():
        rota = p.get("route")
        if rota in rotas:
            ERROS.append(f"rota duplicada {rota}: {slug} e {rotas[rota]}")
        rotas[rota] = slug
        if c.get("screen_types") and p.get("screen_type") not in c["screen_types"]:
            ERROS.append(f"{slug}: screen_type '{p.get('screen_type')}' fora de {c['screen_types']}")
        for ch in p.get("charts") or []:
            if c.get("chart_types") and ch.get("type") not in c["chart_types"]:
                ERROS.append(f"{slug}: gráfico '{ch.get('id')}' com tipo '{ch.get('type')}' fora da lista canônica")
        layout = " ".join(map(str, p.get("layout") or []))
        for ch in p.get("charts") or []:
            if "charts" not in layout and "split" not in layout and "tabs" not in layout:
                AVISOS.append(f"{slug}: layout não reserva faixa para o gráfico '{ch.get('id')}'")
                break
        acoes = (p.get("grid") or {}).get("row_actions") or []
        if "detalhar" in acoes and "simulate" in acoes:
            AVISOS.append(f"{slug}: row_actions com 'detalhar' e 'simulate' — use só 'detalhar' quando o detalhe traz o simulador")
        if not (ROOT / "docs" / "screens" / f"{slug}.yaml").exists() and slug not in ("home", "login"):
            AVISOS.append(f"{slug}: recorte docs/screens/{slug}.yaml ausente (Step 7 lerá o YAML inteiro)")


def pages() -> None:
    sd = _load("docs/screens_definition.yaml")
    for slug, p in (sd.get("pages") or {}).items():
        pkg = p.get("package") or slug.replace("-", "_")
        base = ROOT / "frontend" / "pages" / pkg
        for suf in ("queries", "components", "page", "callbacks"):
            f = base / f"{pkg}_{suf}.py"
            if not f.exists():
                if slug not in ("home", "login"):
                    ERROS.append(f"{slug}: {f.relative_to(ROOT)} ausente")
                continue
            try:
                py_compile.compile(str(f), doraise=True)
            except py_compile.PyCompileError as e:
                ERROS.append(f"{slug}: erro de sintaxe em {f.name}: {e.msg.splitlines()[-1]}")
            txt = f.read_text(encoding="utf-8")
            if suf in ("page", "components") and re.search(r"\.children\s*=\s*\[", txt):
                ERROS.append(f"{slug}: {f.name} altera .children de componente (use extra= no detail_offcanvas)")
            if suf == "callbacks" and re.search(r'Output\([^)]*-detail"\s*,\s*"title"\)', txt):
                ERROS.append(f"{slug}: {f.name} usa Output(<id>-detail,'title') — o Detalhar é modal: Output(f'{{id}}-title','children')")
            if suf in ("queries", "callbacks") and re.search(r"volume[^\n]*\bround\(|np\.round\([^\n]*volume", txt):
                AVISOS.append(f"{slug}: {f.name} arredonda volume por linha — arredondar só na exibição (core.md §3)")


def app() -> None:
    sys.path.insert(0, str(ROOT))
    try:
        importlib.import_module("frontend.app")
    except Exception as e:  # noqa: BLE001
        ERROS.append(f"import frontend.app falhou: {type(e).__name__}: {e}")


def assistant() -> None:
    cat = _load("docs/assistant_catalog.yaml")
    sd = _load("docs/screens_definition.yaml")
    telas = set((sd.get("pages") or {}).keys()) | {"home"}
    vistos = set()
    por_tela: dict[str, int] = {}
    for a in cat.get("analyses") or []:
        aid = a.get("id")
        if aid in vistos:
            ERROS.append(f"catálogo: id duplicado {aid}")
        vistos.add(aid)
        for k in ("questions", "aliases", "sources", "assumptions"):
            if any(not isinstance(v, str) for v in a.get(k) or []):
                ERROS.append(f"catálogo: {aid}.{k} tem valor não-texto (coloque entre aspas)")
        if a.get("entity") and not a.get("pages"):
            ERROS.append(f"catálogo: {aid} tem entity sem pages (apareceria em telas de outro propósito)")
        for p in a.get("pages") or []:
            if p not in telas:
                AVISOS.append(f"catálogo: {aid} cita tela inexistente '{p}'")
            por_tela[p] = por_tela.get(p, 0) + 1
    for t in sorted(telas - {"login"}):
        if por_tela.get(t, 0) == 0 and t != "administracao":
            AVISOS.append(f"assistente: tela '{t}' sem análises próprias")
    if not (ROOT / "frontend" / "services" / "assistant_llm.py").exists():
        ERROS.append("frontend/services/assistant_llm.py ausente (assistente híbrido)")
    llm = ROOT / "frontend" / "services" / "assistant_llm.py"
    if llm.exists() and "<Nome do produto>" in llm.read_text(encoding="utf-8"):
        ERROS.append("assistant_llm.py: APP_NAME/SCREEN_ROUTING não parametrizados")


def main() -> None:
    alvo = sys.argv[1] if len(sys.argv) > 1 else "all"
    etapas = {"screens": screens, "pages": pages, "app": app, "assistant": assistant}
    for nome, fn in etapas.items():
        if alvo in (nome, "all"):
            fn()
    for e in ERROS:
        print("ERRO", e)
    for a in AVISOS:
        print("AVISO", a)
    print(f"RESUMO {alvo}: {len(ERROS)} erro(s), {len(AVISOS)} aviso(s)")
    sys.exit(1 if ERROS else 0)


if __name__ == "__main__":
    main()
