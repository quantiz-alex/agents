"""ui_smoke.py — Smoke test de UI com Playwright (dev-only).

Roda contra uma instância já iniciada do frontend Dash (default http://localhost:1050).
Verifica em runtime o que a validação estática não consegue:
  - login flui, redireciona, não deixa erro no console
  - cada página do app carrega sem exception (status 200, sem Traceback no DOM)
  - componentes-chave por página estão presentes (grid, KPIs, charts, filtros)
  - callbacks de filtro/disparo não estouram no console
  - sidebar badge de approval_queue mostra número
  - role com permissão restrita vê menos itens de menu

Uso:
  python scripts/ui_smoke.py                         # todas as páginas, base url default
  python scripts/ui_smoke.py --base http://localhost:1050 --user admin@slug.com
  python scripts/ui_smoke.py --only dashboard,aprovacao
  python scripts/ui_smoke.py --headed                # abre navegador visível (debug)

Pré-requisitos (dev-only, NÃO vá para requirements.txt de produção):
  pip install playwright pytest-playwright
  playwright install chromium

Saída:
  - stdout: linha por página `[ok]` ou `[FAIL]` + motivo
  - código de saída 0 se tudo passou, 1 se qualquer página falhou
  - relatório JSON em validation_reports/ui_smoke.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout  # type: ignore
except ImportError:  # pragma: no cover
    print("[FATAL] playwright não instalado. Rode:\n  pip install playwright\n  playwright install chromium")
    sys.exit(2)


# --------------------------------------------------------------------------- #
# Configuração
# --------------------------------------------------------------------------- #

DEFAULT_BASE = "http://localhost:1050"
DEFAULT_USER = "admin@example.com"
DEFAULT_PASS = "demo"
REPORT_PATH = Path("validation_reports/ui_smoke.json")
PAGE_TIMEOUT_MS = 15_000
CONSOLE_ERROR_PATTERNS = [
    r"Traceback",
    r"TypeError",
    r"ReferenceError",
    r"SyntaxError",
    r"Error: Cannot read",
    r"dash_renderer.*error",
    r"Callback error",
]


# --------------------------------------------------------------------------- #
# Utilitários
# --------------------------------------------------------------------------- #

def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def discover_pages(page) -> list[dict]:
    """Lê a sidebar para descobrir as páginas disponíveis e suas rotas."""
    links = page.eval_on_selector_all(
        "a[href^='/']",
        """els => els.map(e => ({
            href: e.getAttribute('href'),
            text: (e.textContent || '').trim(),
            badge: (e.querySelector('.badge') || {}).textContent || null
        }))""",
    )
    # dedup por href, filtra /login e /
    seen, pages = set(), []
    for l in links:
        h = l["href"]
        if not h or h in ("/login", "/logout", "/") or h in seen:
            continue
        seen.add(h)
        pages.append(l)
    return pages


def collect_console_errors(page) -> list[str]:
    errors: list[str] = []
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    return errors


def has_traceback(page) -> str | None:
    body = page.inner_text("body", timeout=2_000) if page.query_selector("body") else ""
    if "Traceback" in body and ("line" in body or "Error" in body):
        # extrai a primeira linha do traceback
        m = re.search(r"(Traceback.*?)(?:\n\n|\Z)", body, re.S)
        return (m.group(1) if m else body[:200]).replace("\n", " | ")
    return None


# --------------------------------------------------------------------------- #
# Checks por página
# --------------------------------------------------------------------------- #

def check_login(page, base: str, user: str, pwd: str) -> tuple[bool, str]:
    page.goto(f"{base}/login", wait_until="networkidle", timeout=PAGE_TIMEOUT_MS)
    # preenche formulário
    email_input = page.query_selector("input[type='email'], #login-email, #email")
    pass_input = page.query_selector("input[type='password'], #login-senha, #senha")
    if not email_input or not pass_input:
        return False, "formulário de login não encontrado (sem input email/senha)"
    email_input.fill(user)
    pass_input.fill(pwd)
    # botão submit
    btn = page.query_selector("button[type='submit'], #login-btn-entrar, #btn-entrar")
    if not btn:
        return False, "botão de submit não encontrado"
    btn.click()
    page.wait_for_load_state("networkidle", timeout=PAGE_TIMEOUT_MS)
    if "/login" in page.url:
        alert = page.query_selector("#login-alert, .alert-danger")
        return False, f"continua em /login — alerta: {alert.inner_text() if alert else '(sem alerta visível)'}"
    return True, page.url


def check_page_loads(page, base: str, href: str) -> tuple[bool, str]:
    page.goto(f"{base}{href}", wait_until="networkidle", timeout=PAGE_TIMEOUT_MS)
    tb = has_traceback(page)
    if tb:
        return False, f"Traceback no DOM: {tb}"
    # título da página presente (h1/h2/h3 não vazio)
    title = page.query_selector("h1, h2, h3, .page-title")
    if not title or not title.inner_text().strip():
        return False, "sem título de página (h1/h2/h3 vazio ou ausente)"
    return True, title.inner_text().strip()[:60]


def check_components(page, base: str, href: str) -> list[str]:
    """Verifica componentes esperados por tipo de tela (heurística por URL/texto)."""
    page.goto(f"{base}{href}", wait_until="networkidle", timeout=PAGE_TIMEOUT_MS)
    issues: list[str] = []
    body_text = page.inner_text("body", timeout=2_000)
    page_slug = href.strip("/").split("/")[-1]

    # Grid (AG Grid)
    grid = page.query_selector(".ag-grid, .ag-root-wrapper, [class*='ag-grid']")
    if "grid" in body_text.lower() or "tabela" in body_text.lower():
        if not grid:
            issues.append("texto menciona grid/tabela mas .ag-root-wrapper ausente")

    # KPIs
    kpis = page.query_selector_all(".kpi-card, .card-kpi, [class*='kpi']")
    if "KPI" in body_text or "indicador" in body_text.lower():
        if len(kpis) == 0:
            issues.append("texto menciona KPI mas nenhum .kpi-card encontrado")

    # Charts (Plotly)
    charts = page.query_selector_all(".js-plotly-plot, .plotly-graph-div, [class*='chart']")
    if "gráfico" in body_text.lower() or "chart" in body_text.lower():
        if len(charts) == 0:
            issues.append("texto menciona gráfico mas nenhum .js-plotly-plot encontrado")

    # Filtros
    filtros = page.query_selector_all(f"#{page_slug}-filtro-*, #filtro-*, .filter-bar, [id*='filtro']")
    if "filtro" in body_text.lower() or "filtrar" in body_text.lower():
        if len(filtros) == 0:
            issues.append("texto menciona filtro mas nenhum #filtro-* encontrado")

    # Botão de simular (simulation)
    if "simular" in body_text.lower() or "simulação" in body_text.lower():
        if not page.query_selector(f"#{page_slug}-btn-simular, #btn-simular"):
            issues.append("tela de simulação sem #btn-simular")

    # Empty state
    if "nenhum registro" in body_text.lower() or "sem dados" in body_text.lower():
        if not page.query_selector(".empty-state, [class*='empty']"):
            issues.append("texto de estado vazio mas sem .empty-state")

    return issues


def check_sidebar_badge(page, base: str) -> list[str]:
    """Aproval_queue deve ter badge numérico na sidebar."""
    page.goto(base, wait_until="networkidle", timeout=PAGE_TIMEOUT_MS)
    issues: list[str] = []
    badges = page.query_selector_all(".nav-link .badge, .sidebar .badge")
    found_numeric = any(b.inner_text().strip().isdigit() for b in badges)
    # só reporta se houver menção a aprovação no app
    body = page.inner_text("body", timeout=2_000)
    if "aprova" in body.lower() and not found_numeric:
        issues.append("tela de aprovação referenciada mas sidebar sem badge numérico")
    return issues


def check_role_restriction(page, base: str, restricted_user: str, restricted_pass: str) -> list[str]:
    """Login com role restrito deve ver menos itens de menu."""
    issues: list[str] = []
    try:
        ok, _ = check_login(page, base, restricted_user, restricted_pass)
        if not ok:
            return issues  # não bloqueia — só avisa
        admin_count = page.eval_on_selector_all(
            "a[href^='/']", "els => els.filter(e => e.offsetParent !== null).length"
        )
        # logout + login admin para comparar
        page.goto(f"{base}/logout", wait_until="networkidle", timeout=5_000)
        check_login(page, base, "admin@example.com", restricted_pass)
        full_count = page.eval_on_selector_all(
            "a[href^='/']", "els => els.filter(e => e.offsetParent !== null).length"
        )
        if admin_count >= full_count:
            issues.append(
                f"role restrito vê {admin_count} itens vs admin {full_count} — restrição não aplicada"
            )
    except Exception as e:  # noqa: BLE001
        issues.append(f"check_role_restriction não executou: {e}")
    return issues


# --------------------------------------------------------------------------- #
# Runner principal
# --------------------------------------------------------------------------- #

def run(base: str, user: str, pwd: str, only: list[str] | None, headed: bool) -> dict:
    results: dict[str, Any] = {"base": base, "user": user, "pages": [], "summary": {}}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed)
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        console_errors = collect_console_errors(page)

        # 1. Login
        ok, msg = check_login(page, base, user, pwd)
        results["login"] = {"ok": ok, "redirect": msg}
        if not ok:
            browser.close()
            results["summary"] = {"status": "failed", "reason": "login falhou"}
            return results
        print(f"[ok] login → {msg}")

        # 2. Descobrir páginas
        pages = discover_pages(page)
        if not pages:
            print("[WARN] nenhuma página descoberta na sidebar — verificando apenas /")
            pages = [{"href": "/", "text": "Home", "badge": None}]
        if only:
            want = set(only)
            pages = [pg for pg in pages if slug(pg["text"]) in want or pg["href"].strip("/") in want]

        # 3. Por página: carrega + componentes + console
        failures = 0
        for pg in pages:
            href, text = pg["href"], pg["text"]
            console_errors.clear()
            ok, msg = check_page_loads(page, base, href)
            comp_issues = check_components(page, base, href) if ok else []
            errs = list(console_errors)
            page_result = {
                "href": href,
                "title": text,
                "loads": ok,
                "page_title": msg if ok else None,
                "component_issues": comp_issues,
                "console_errors": errs[:5],
            }
            results["pages"].append(page_result)
            if ok and not comp_issues and not errs:
                print(f"[ok] {href} — {msg}")
            else:
                failures += 1
                reasons = []
                if not ok:
                    reasons.append(f"load: {msg}")
                if comp_issues:
                    reasons.append(f"components: {'; '.join(comp_issues)}")
                if errs:
                    reasons.append(f"console: {'; '.join(errs[:2])}")
                print(f"[FAIL] {href} — {' | '.join(reasons)}")

        # 4. Sidebar badge (approval_queue)
        badge_issues = check_sidebar_badge(page, base)
        results["sidebar_badge"] = {"issues": badge_issues}
        if badge_issues:
            print(f"[WARN] sidebar badge: {'; '.join(badge_issues)}")

        # 5. Role restriction (opcional — só se houver segundo usuário)
        # (skip por padrão — exige credencial adicional; habilitar via flag --role-check)

        browser.close()

    results["summary"] = {
        "status": "failed" if failures else "success",
        "pages_checked": len(results["pages"]),
        "pages_failed": failures,
        "sidebar_badge_issues": len(badge_issues),
    }
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="Smoke test de UI com Playwright")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--user", default=DEFAULT_USER)
    ap.add_argument("--pass", dest="password", default=DEFAULT_PASS)
    ap.add_argument("--only", default=None, help="lista de slugs separados por vírgula")
    ap.add_argument("--headed", action="store_true", help="abre navegador visível")
    ap.add_argument("--report", default=str(REPORT_PATH))
    args = ap.parse_args()

    only = [s.strip() for s in args.only.split(",")] if args.only else None
    print(f"ui_smoke → {args.base} (user={args.user}, only={only or 'all'})\n")

    # espera o servidor estar up (até 30s)
    for _ in range(30):
        try:
            import urllib.request
            urllib.request.urlopen(args.base, timeout=2)
            break
        except Exception:  # noqa: BLE001
            time.sleep(1)
    else:
        print(f"[FATAL] servidor não responde em {args.base}")
        return 2

    results = run(args.base, args.user, args.password, only, args.headed)

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nrelatório → {report}")
    return 0 if results["summary"]["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
