"""Regressões do runtime local, sem Dash, rede ou banco."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("pricing_assistant", Path(__file__).resolve().parents[1] / "pricing_assistant.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def catalog(identifier="margem", question="Onde melhorar a margem?", required=None):
    return {"analyses": [{"id": identifier, "title": identifier, "handler": identifier,
                          "questions": [question], "sources": ["produto.preco", "produto.custo"],
                          "assumptions": ["Volume constante"], "required_context": required or [],
                          "actions": [{"id": "simulate", "kind": "simulate", "scenario_key": "arquitetura"}]}]}


class AssistantTests(unittest.TestCase):
    def test_calculated_context_and_no_mutation(self):
        context = {"price": 100, "cost": 70, "revision": 2}
        def margin(ctx):
            value = ctx["price"] - ctx["cost"]
            ctx["cost"] = 0
            return {"message": f"Margem unitária: {value}", "data": {"margin": value}, "action_ids": []}
        result = module.answer("onde melhorar a MARGEM", catalog(), {"margem": margin}, context)
        self.assertEqual(result["data"]["margin"], 30)
        self.assertEqual(context["cost"], 70)
        changed = module.answer("Onde melhorar a margem?", catalog(), {"margem": margin}, {**context, "cost": 80})
        self.assertEqual(changed["data"]["margin"], 20)
        self.assertEqual(result["revision"], 2)

    def test_catalog_changes_with_project_and_unknown_question(self):
        handlers = {"margem": lambda ctx: {"message": "Margem"}, "volume": lambda ctx: {"message": "Volume"}}
        first = module.answer("Qual volume?", catalog(), handlers, {})
        second = module.answer("Qual volume?", catalog("volume", "Qual volume?"), handlers, {})
        self.assertEqual(first["status"], "choose_analysis")
        self.assertEqual(second["status"], "ok")
        self.assertEqual(second["analysis_id"], "volume")

    def test_missing_product_and_roles(self):
        definition = catalog(required=["product_id"])
        handlers = {"margem": lambda ctx: {"message": "ok"}}
        self.assertEqual(module.answer("Onde melhorar a margem?", definition, handlers, {})["status"], "needs_context")
        definition["analyses"][0]["roles"] = ["admin"]
        answer = module.answer("", definition, handlers, {"role": "analista"}, analysis_id="margem")
        self.assertEqual(answer["status"], "choose_analysis")
        self.assertEqual(answer["options"], [])

    def test_ambiguous_question_and_invalid_actions(self):
        definition = catalog()
        second = catalog("outra")["analyses"][0]
        definition["analyses"].append(second)
        handlers = {"margem": lambda ctx: {"message": "ok", "action_ids": ["apply"]},
                    "outra": lambda ctx: {"message": "ok"}}
        self.assertEqual(module.answer("Onde melhorar a margem?", definition, handlers, {})["status"], "choose_analysis")
        self.assertEqual(module.answer("", definition, handlers, {}, "margem")["status"], "unavailable")
        with self.assertRaises(ValueError):
            module.validate_catalog(catalog(), {})

    def test_non_finite_and_history_isolation(self):
        bad = {"margem": lambda ctx: {"message": "ok", "data": {"value": float("nan")}}}
        self.assertEqual(module.answer("", catalog(), bad, {}, "margem")["status"], "unavailable")
        history = []
        response = {"status": "ok", "data": {"value": 30}}
        updated = module.append_history(history, "Margem?", response)
        response["data"]["value"] = 40
        self.assertEqual(history, [])
        self.assertEqual(updated[0]["response"]["data"]["value"], 30)
        self.assertEqual(len(module.append_history(updated, "Outra?", {}, limit=1)), 1)

    def test_proposal_is_draft_and_stale_filters_are_rejected(self):
        context = {"scenario_key": "arquitetura", "revision": 3, "filters": {"category": "A"}}
        handlers = {"margem": lambda ctx: {"message": "Comparar proposta", "action_ids": ["simulate"],
                                           "proposal": {"parameters": {"markup": 20}}}}
        response = module.answer("", catalog(), handlers, context, "margem")
        event = module.proposal_event(response, context, "event-1", "simulate")
        self.assertEqual(event["kind"], "simulate")
        self.assertEqual(event["expected_revision"], 3)
        self.assertEqual(event["scope"], {"category": "A"})
        with self.assertRaises(ValueError):
            module.proposal_event(response, {**context, "filters": {"category": "B"}}, "event-2", "simulate")
        with self.assertRaises(ValueError):
            module.proposal_event(response, {**context, "revision": 4}, "event-3", "simulate")

    def test_disabled(self):
        self.assertEqual(module.available({"enabled": False}, {}), [])
        self.assertEqual(module.answer("Margem?", {"enabled": False}, {}, {})["status"], "disabled")


if __name__ == "__main__":
    unittest.main()
