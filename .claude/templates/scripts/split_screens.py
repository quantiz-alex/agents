"""Gera docs/screens/<slug>.yaml — recorte autocontido por tela (economia de tokens no Step 7).

Cada recorte traz: a definição da tela (screens_definition.pages[slug]), as regras de business_logic citadas pela tela
(business_rules / source_rule_ids / module) e as entidades do data_model que ela usa (main_entity, data_sources, joins),
mais as constantes de negócio. O frontend-builder lê SÓ o recorte por página, em vez de ~250 KB de YAMLs.

Uso (na raiz do projeto, após o Step 6):  python "$LH/templates/scripts/split_screens.py"
"""
from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path.cwd()


def _load(p: str) -> dict:
    f = ROOT / p
    return (yaml.safe_load(f.read_text(encoding="utf-8")) or {}) if f.exists() else {}


def _entidades_da_tela(p: dict) -> set[str]:
    ents = {p.get("main_entity")} | {d.get("entity") for d in p.get("data_sources") or [] if isinstance(d, dict)}
    for j in (p.get("grid") or {}).get("joins") or []:
        if isinstance(j, dict):
            ents |= {j.get("entity"), j.get("table"), j.get("ref")}
    return {e for e in ents if e}


def main() -> None:
    sd = _load("docs/screens_definition.yaml")
    bl = _load("docs/business_logic.yaml")
    dm = _load("docs/data_model.yaml")
    regras = bl.get("rules") or []
    entidades = dm.get("entities") or {}
    out_dir = ROOT / "docs" / "screens"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    for slug, p in (sd.get("pages") or {}).items():
        rn = set(p.get("business_rules") or [])
        modulo = p.get("module") or slug
        rs = [r for r in regras if r.get("id") in rn or set(r.get("source_rule_ids") or []) & rn or r.get("module") == modulo]
        ents = _entidades_da_tela(p)
        recorte = {
            "slug": slug,
            "screen": p,
            "business_rules": rs,
            "constants": bl.get("constants") or {},
            "entities": {e: entidades[e] for e in sorted(ents) if e in entidades},
            "shell": {k: v for k, v in (sd.get("shell") or {}).items() if k in ("menu_groups", "roles")},
        }
        (out_dir / f"{slug}.yaml").write_text(yaml.safe_dump(recorte, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8")
        n += 1
    tamanhos = sorted((f.stat().st_size for f in out_dir.glob("*.yaml")), reverse=True)
    print(f"docs/screens: {n} recortes · maior {tamanhos[0] // 1024 if tamanhos else 0} KB · total {sum(tamanhos) // 1024} KB")


if __name__ == "__main__":
    main()
