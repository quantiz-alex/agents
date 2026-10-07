"""Regressões do ciclo de cenário mock; executável sem Dash ou banco."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("demo_scenario", Path(__file__).resolve().parents[1] / "demo_scenario.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ScenarioTests(unittest.TestCase):
    def event(self, state, kind, **payload):
        return {"id": f"{kind}-{state['revision']}", "kind": kind,
                "expected_revision": state["revision"], **payload}

    def test_cycle_and_isolation(self):
        state = module.new_session({"markup": 10})
        other = module.new_session({"markup": 10})
        edited = module.transition(state, self.event(state, "edit", parameters={"markup": 20}))
        self.assertEqual(edited["applied"]["parameters"]["markup"], 10)
        self.assertEqual(state, other)
        signature = module.fingerprint(edited["draft"]["parameters"], {})
        preview = module.transition(edited, self.event(edited, "preview", fingerprint=signature, results={"revenue": 120}))
        applied = module.transition(preview, self.event(preview, "apply"))
        self.assertEqual(module.scenario_for_view(applied)["parameters"]["markup"], 20)
        changed = module.transition(applied, self.event(applied, "edit", parameters={"markup": 30}))
        discarded = module.transition(changed, self.event(changed, "discard"))
        self.assertEqual(discarded["draft"], applied["applied"])
        reset = module.transition(discarded, self.event(discarded, "reset"))
        self.assertEqual(reset["applied"], state["baseline"])

    def test_stale_and_unsimulated(self):
        state = module.new_session({"markup": 10})
        with self.assertRaises(ValueError):
            module.transition(state, self.event(state, "apply"))
        with self.assertRaises(ValueError):
            module.transition(state, self.event(state, "preview", fingerprint="old", results={}))
        event = self.event(state, "edit", parameters={"markup": 20})
        changed = module.transition(state, event)
        self.assertEqual(module.transition(changed, event), changed)
        with self.assertRaises(ValueError):
            module.transition(changed, self.event(state, "discard"))

    def test_scope_invalidates_preview(self):
        state = module.new_session({"markup": 10}, {"category": "A"})
        signature = module.fingerprint(state["draft"]["parameters"], state["draft"]["scope"])
        preview = module.transition(state, self.event(state, "preview", fingerprint=signature, results={}))
        changed = module.transition(preview, self.event(preview, "edit", parameters={"markup": 10}, scope={"category": "B"}))
        self.assertIsNone(changed["preview"])
        self.assertNotEqual(signature, module.fingerprint(changed["draft"]["parameters"], changed["draft"]["scope"]))

    def test_shared_calculation_across_views(self):
        # Fixture de apresentação: uma alteração deve afetar detalhe e total de forma coerente.
        def engine(params, scope):
            rows = [{"category": "A", "cost": 100, "quantity": 2},
                    {"category": "B", "cost": 50, "quantity": 3}]
            revenues = [row["cost"] * (1 + params["markup"] / 100) * row["quantity"] for row in rows]
            return {"rows": revenues, "revenue": sum(revenues)}

        original = module.new_session({"markup": 10})
        event = self.event(original, "simulate", parameters={"markup": 20}, results={"revenue": -1})
        simulated = module.dispatch(original, event, engine)
        self.assertAlmostEqual(simulated["preview"]["results"]["revenue"], 420)
        self.assertAlmostEqual(engine(module.scenario_for_view(simulated)["parameters"], {})["revenue"], 385)
        self.assertEqual(module.dispatch(simulated, event, engine), simulated)
        detail = engine(module.scenario_for_view(simulated, "draft")["parameters"], {})
        self.assertEqual(detail, simulated["preview"]["results"])
        applied = module.dispatch(simulated, self.event(simulated, "apply"), engine)
        dashboard = engine(module.scenario_for_view(applied)["parameters"], {})
        self.assertEqual(dashboard, detail)
        # Estado serializado em session storage preserva parâmetros ao navegar/atualizar.
        import json
        self.assertEqual(json.loads(json.dumps(applied)), applied)


if __name__ == "__main__":
    unittest.main()
