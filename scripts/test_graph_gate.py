"""Adversarial structural and transactional checks, using only the stdlib."""
import copy
import json
from pathlib import Path
import tempfile
import threading
import unittest

from graph_gate import GateError, apply_proposal, load_json, validate_registry


def node(nid, natural=False):
    return {"id": nid, "name": nid, "role": "natural" if natural else "tool",
            "terminal": {"kind": "natural", "reviewed": True, "evidence": ["reviewed site survey"]} if natural else False,
            "maturity": "documented", "inventory_complete": True, "spec_reviewed": True}


def req(target, capability=None, compatibility="reviewed"):
    return {"target": target, "role": "tool", "required_capability": capability or {"quantity": 1, "unit": "item"}, "compatibility": compatibility}


def route(output, targets):
    return {"id": "make-" + output, "output": output, "requires": [req(t) for t in targets],
            "inventory_complete": True, "reviewed": True}


def registry(nodes=None, routes=None, selected=None):
    return {"revision": 0, "nodes": nodes if nodes is not None else [node("a"), node("ore", True)],
            "routes": routes if routes is not None else [route("a", ["ore"])],
            "scenarios": [{"id": "main", "roots": ["a"], "selected_routes": selected if selected is not None else {"a": "make-a"}}]}


class GateTests(unittest.TestCase):
    def test_unspecified_prose_cannot_close_reviewed_capability(self):
        for placeholder in ('not yet specified', 'NOT_YET_SPECIFIED', 'not-yet-specified', 'TBD', 'unspecified'):
            with self.subTest(placeholder=placeholder):
                data=registry()
                data['routes'][0]['requires'][0]['required_capability']={'accuracy':placeholder}
                self.assertFalse(validate_registry(data)['scenarios'][0]['target_research_closed'])

    def assert_rejected(self, data, code):
        with self.assertRaises(GateError) as caught:
            validate_registry(data)
        self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_reviewed_chain_closes_with_explicit_denominators(self):
        report = validate_registry(registry())["scenarios"][0]
        self.assertTrue(report["target_research_closed"])
        self.assertTrue(report["executable"])
        self.assertFalse(report["physical_acceptance_proven"])
        self.assertEqual(report["counts"]["closed_outputs_including_terminals"], 2)
        self.assertEqual(report["counts"]["closed_outputs_excluding_terminals"], 1)
        self.assertEqual(report["natural_endpoints"], ["ore"])

    def test_self_loop_exact_witness(self):
        error = self.assert_rejected(registry([node("a")], [route("a", ["a"])], {"a": "make-a"}), "cycle")
        self.assertEqual(error.details["cycle"], ["a", "make-a", "a"])

    def test_three_output_cycle_exact_witness(self):
        data = registry([node(n) for n in "abc"], [route("a", ["b"]), route("b", ["c"]), route("c", ["a"])], {n: "make-" + n for n in "abc"})
        error = self.assert_rejected(data, "cycle")
        self.assertEqual(error.details["cycle"], ["a", "make-a", "b", "make-b", "c", "make-c", "a"])

    def test_every_scenario_is_validated(self):
        data = registry()
        data["routes"].append({**route("a", ["a"]), "id": "cyclic-a"})
        data["scenarios"].append({"id": "alternative", "selected_routes": {"a": "cyclic-a"}})
        self.assertEqual(self.assert_rejected(data, "cycle").details["scenario"], "alternative")

    def test_missing_target_even_on_unselected_candidate(self):
        data = registry()
        data["routes"].append({**route("a", ["absent"]), "id": "candidate"})
        self.assert_rejected(data, "dangling")

    def test_missing_output_and_selection(self):
        for mutation, code in [(lambda d: d["routes"][0].update(output="absent"), "dangling"),
                               (lambda d: d["scenarios"][0]["selected_routes"].update(a="absent"), "dangling_selection")]:
            data = registry()
            mutation(data)
            self.assert_rejected(data, code)

    def test_duplicates_and_malformed_types(self):
        data = registry()
        data["nodes"].append(copy.deepcopy(data["nodes"][0]))
        self.assert_rejected(data, "duplicate_id")
        data = registry()
        data["routes"][0]["id"] = "a"
        self.assert_rejected(data, "duplicate_id")
        data = registry()
        data["revision"] = True
        self.assert_rejected(data, "schema")

    def test_plausible_navigation_and_inverse_produces_ignored(self):
        data = registry()
        data["nodes"][1]["navigation"] = [{"target": "a", "label": "Back to Phone"}]
        data["nodes"][1]["parent"] = "a"
        data["routes"][0]["produces"] = ["a"]
        report = validate_registry(data)["scenarios"][0]
        self.assertEqual(report["structural_links"], [["a", "make-a"], ["make-a", "ore"]])

    def test_nonselected_cyclic_candidate_emits_no_live_links(self):
        data = registry()
        data["routes"].append({**route("a", ["a"]), "id": "cyclic-candidate"})
        report = validate_registry(data)["scenarios"][0]
        self.assertTrue(report["target_research_closed"])
        self.assertFalse(any("cyclic-candidate" in edge for edge in report["structural_links"]))

    def test_false_terminal_and_external_boundary(self):
        for mutation in [lambda n: n["terminal"].update(reviewed=False),
                         lambda n: n["terminal"].update(evidence=[]),
                         lambda n: n["terminal"].update(kind="external"),
                         lambda n: n.update(role="external")]:
            data = registry()
            mutation(data["nodes"][1])
            self.assert_rejected(data, "false_terminal")

    def test_unknowns_and_incomplete_inventory_allow_only_draft(self):
        mutations = [lambda d: d["routes"][0].update(inventory_complete=False),
                     lambda d: d["nodes"][0].update(inventory_complete=False),
                     lambda d: d["routes"][0]["requires"][0].update(compatibility="unknown"),
                     lambda d: d["routes"][0]["requires"][0].update(required_capability=None),
                     lambda d: d["routes"][0]["requires"][0].update(required_capability={"accuracy": "UNKNOWN"}),
                     lambda d: d["nodes"][0].update(spec_reviewed=False),
                     lambda d: d["nodes"][0].update(unknowns=["required purity"]),
                     lambda d: d["nodes"][0].update(specification={"power": "UNKNOWN"})]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                data = registry()
                mutate(data)
                report = validate_registry(data)["scenarios"][0]
                self.assertFalse(report["closure"]["a"])
                self.assertFalse(report["executable"])
                self.assertEqual(len(report["structural_links"]), 2)

    def test_empty_route_and_unexpanded_placeholder_do_not_close(self):
        data = registry()
        data["routes"][0]["requires"] = []
        self.assertFalse(validate_registry(data)["scenarios"][0]["closure"]["a"])
        data["scenarios"][0]["selected_routes"] = {}
        report = validate_registry(data)["scenarios"][0]
        self.assertEqual(report["unexpanded_outputs"], ["a"])

    def test_scenario_uncertainty_and_unclosed_selected_side_branch(self):
        data = registry()
        data["scenarios"][0]["unknowns"] = ["geological assumption"]
        report = validate_registry(data)["scenarios"][0]
        self.assertFalse(report["target_research_closed"])
        self.assertFalse(report["executable"])
        data["scenarios"][0].pop("unknowns")
        data["nodes"].append(node("other"))
        data["routes"].append(route("other", ["ore"]))
        data["routes"][-1]["inventory_complete"] = False
        data["scenarios"][0]["selected_routes"]["other"] = "make-other"
        report = validate_registry(data)["scenarios"][0]
        self.assertTrue(report["target_research_closed"])
        self.assertFalse(report["executable"])

    def test_independent_calibrated_state_and_self_certification(self):
        data = registry([node("a"), node("uncalibrated"), node("reference", True), node("ore", True)],
                        [route("a", ["uncalibrated", "reference"]), route("uncalibrated", ["ore"])],
                        {"a": "make-a", "uncalibrated": "make-uncalibrated"})
        self.assertTrue(validate_registry(data)["scenarios"][0]["closure"]["a"])
        data["routes"][0]["requires"].append(req("a"))
        self.assert_rejected(data, "cycle")

    def test_long_chain_avoids_python_recursion_limit(self):
        length = 1100
        data = registry([node(str(i)) for i in range(length)] + [node("ore", True)],
                        [route(str(i), [str(i + 1) if i + 1 < length else "ore"]) for i in range(length)],
                        {str(i): "make-" + str(i) for i in range(length)})
        data["scenarios"][0]["roots"] = ["0"]
        self.assertTrue(validate_registry(data)["scenarios"][0]["target_research_closed"])


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "registry.json"
        self.path.write_text(json.dumps(registry()), encoding="utf-8")

    def test_failure_leaves_exact_bytes_unchanged(self):
        before = self.path.read_bytes()
        for proposal in [{"base_revision": 0, "upsert_routes": [route("a", ["a"])]},
                         {"base_revision": 0, "upsert_routes": [route("a", ["absent"])]},
                         {"base_revision": 99}, {"base_revision": 0, "dependency_links": [["ore", "a"]]}]:
            with self.assertRaises(GateError):
                apply_proposal(self.path, proposal)
            self.assertEqual(self.path.read_bytes(), before)
            self.assertFalse(Path(str(self.path) + ".lock").exists())

    def test_stale_second_atomic_proposal_and_joint_cycle(self):
        data = registry([node("a"), node("b"), node("ore", True)],
                        [route("a", ["ore"]), route("b", ["ore"])], {"a": "make-a", "b": "make-b"})
        self.path.write_text(json.dumps(data), encoding="utf-8")
        first = {"base_revision": 0, "upsert_routes": [route("a", ["b"])]}
        second = {"base_revision": 0, "upsert_routes": [route("b", ["a"])]}
        # Each proposal individually is acyclic against the same base.
        isolated = copy.deepcopy(data)
        isolated["routes"][1] = second["upsert_routes"][0]
        validate_registry(isolated)
        apply_proposal(self.path, first)
        before = self.path.read_bytes()
        with self.assertRaises(GateError) as caught:
            apply_proposal(self.path, second)
        self.assertEqual(caught.exception.code, "stale_revision")
        second["base_revision"] = 1
        with self.assertRaises(GateError) as caught:
            apply_proposal(self.path, second)
        self.assertEqual(caught.exception.code, "cycle")
        self.assertEqual(self.path.read_bytes(), before)

    def test_concurrent_commit_has_exactly_one_winner(self):
        barrier = threading.Barrier(2)
        results = []
        def commit(label):
            barrier.wait()
            try:
                apply_proposal(self.path, {"base_revision": 0, "upsert_nodes": [{**node("a"), "name": label}]})
                results.append("accepted")
            except GateError as error:
                results.append(error.code)
        threads = [threading.Thread(target=commit, args=(str(i),)) for i in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(5)
            self.assertFalse(thread.is_alive())
        self.assertCountEqual(results, ["accepted", "stale_revision"])
        self.assertEqual(load_json(self.path)["revision"], 1)

    def test_union_proposal_and_full_scenario_replacement(self):
        proposal = {"base_revision": 0, "upsert_nodes": [node("new")],
                    "upsert_routes": [route("new", ["ore"])],
                    "scenarios": [{"id": "new-target", "roots": ["new"], "selected_routes": {"new": "make-new"}}]}
        report = apply_proposal(self.path, proposal)
        self.assertTrue(report["scenarios"][0]["target_research_closed"])
        self.assertEqual(load_json(self.path)["revision_log"][0]["outcome"], "accepted")

    def test_duplicate_json_keys_not_silently_overwritten(self):
        self.path.write_text('{"revision":0,"revision":1}', encoding="utf-8")
        with self.assertRaises(GateError) as caught:
            load_json(self.path)
        self.assertEqual(caught.exception.code, "duplicate_key")


if __name__ == "__main__":
    unittest.main()
