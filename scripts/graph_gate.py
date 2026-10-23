"""Conservative, stdlib-only publication gate for declared research graphs."""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import tempfile
import time
import math
from collections import Counter
from contextlib import contextmanager

MATURITIES = {"proposed", "documented", "demonstrated", "accepted"}
REQUIREMENT_ROLES = {"part", "tool", "verification", "utility"}
UNKNOWN_WORDS = {"UNKNOWN", "NOT_RESEARCHED", "PROPRIETARY_GAP", "UNRESOLVED_BOOTSTRAP",
                 "NOT_YET_SPECIFIED", "NOT_SPECIFIED", "TBD", "UNSPECIFIED"}


class GateError(ValueError):
    def __init__(self, code, message, **details):
        super().__init__(message)
        self.code, self.details = code, details

    def as_dict(self):
        return {"ok": False, "code": self.code, "message": str(self), **self.details}


def fail(code, message, **details):
    raise GateError(code, message, **details)


def require(condition, message):
    if not condition:
        fail("schema", message)


def identifier(value, location):
    require(isinstance(value, str) and bool(value.strip()), f"{location} must be a nonempty ID string")
    return value


def boolean_field(record, field, location):
    require(type(record.get(field)) is bool, f"{location}.{field} must be a boolean")


def has_unknown(value):
    if value is None:
        return True
    if isinstance(value, str):
        normalized = '_'.join(value.strip().upper().replace('-', ' ').replace('_', ' ').split())
        return not normalized or normalized in UNKNOWN_WORDS
    if isinstance(value, dict):
        return any(has_unknown(v) for v in value.values())
    if isinstance(value, list):
        return any(has_unknown(v) for v in value)
    if isinstance(value, float):
        return not math.isfinite(value)
    return False


def unresolved(record):
    """Questions are conservative blockers until removed/resolved in a revision."""
    return any(bool(record.get(key)) for key in ("unknowns", "unresolved_questions", "blockers")) or any(
        record.get(key) is True for key in ("has_unknowns", "conditional")
    ) or record.get("research_status") == "blocked" or any(
        has_unknown(record[key]) for key in ("specification", "spec", "quantity", "conditions") if key in record
    )


def indexed(records, label):
    require(isinstance(records, list), f"{label} must be an array")
    result = {}
    for record in records:
        require(isinstance(record, dict), f"{label} entries must be objects")
        rid = identifier(record.get("id"), f"{label}.id")
        if rid in result:
            fail("duplicate_id", f"Duplicate {label} ID: {rid}", id=rid)
        result[rid] = record
    return result


def cycle_witness(graph):
    """Iterative DFS returns the exact closed directed path, including route IDs."""
    color, path, positions = {}, [], {}
    for start in graph:
        if color.get(start):
            continue
        stack = [(start, iter(graph[start]))]
        color[start] = 1
        positions[start] = len(path)
        path.append(start)
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                stack.pop()
                color[node] = 2
                positions.pop(node)
                path.pop()
            elif color.get(child) == 1:
                return path[positions[child]:] + [child]
            elif not color.get(child):
                color[child] = 1
                positions[child] = len(path)
                path.append(child)
                stack.append((child, iter(graph[child])))
    return None


def validate_registry(registry):
    require(isinstance(registry, dict), "Registry must be an object")
    require(type(registry.get("revision")) is int and registry["revision"] >= 0, "revision must be a nonnegative integer")
    if "revision_log" in registry:
        require(isinstance(registry["revision_log"], list), "revision_log must be an array")
    nodes = indexed(registry.get("nodes"), "nodes")
    routes = indexed(registry.get("routes"), "routes")
    scenarios = indexed(registry.get("scenarios"), "scenarios")
    require(bool(scenarios), "At least one explicit scenario is required")
    overlap = nodes.keys() & routes.keys()
    if overlap:
        fail("duplicate_id", "Output and route IDs must be globally distinct", ids=sorted(overlap))
    terminals = set()
    for nid, node in nodes.items():
        identifier(node.get("name"), f"node {nid}.name")
        identifier(node.get("role"), f"node {nid}.role")
        require(isinstance(node.get("maturity"), str) and node["maturity"] in MATURITIES, f"node {nid}.maturity is invalid")
        boolean_field(node, "inventory_complete", f"node {nid}")
        require("terminal" in node, f"node {nid}.terminal is required")
        for field in ("spec_reviewed", "specification_reviewed", "has_unknowns", "conditional"):
            if field in node:
                boolean_field(node, field, f"node {nid}")
        terminal = node["terminal"]
        if terminal is not False:
            require(isinstance(terminal, dict), f"node {nid}.terminal must be false or a natural terminal object")
            if terminal.get("kind") != "natural" or node["role"] == "external" or node.get("boundary") == "external":
                fail("false_terminal", f"{nid}: external/manufactured boundary is not a natural terminal", id=nid)
            if terminal.get("reviewed") is not True or not isinstance(terminal.get("evidence"), list) or not terminal["evidence"] or has_unknown(terminal["evidence"]):
                fail("false_terminal", f"{nid}: natural terminal needs reviewed:true and nonempty usable evidence", id=nid)
            terminals.add(nid)
    for rid, route in routes.items():
        output = identifier(route.get("output"), f"route {rid}.output")
        if output not in nodes:
            fail("dangling", f"Route {rid} output {output} does not exist", route=rid, target=output)
        boolean_field(route, "inventory_complete", f"route {rid}")
        boolean_field(route, "reviewed", f"route {rid}")
        require(isinstance(route.get("requires"), list), f"route {rid}.requires must be an array")
        for req in route["requires"]:
            require(isinstance(req, dict), f"route {rid} requirements must be objects")
            target = identifier(req.get("target"), f"route {rid}.requires.target")
            if target not in nodes:
                fail("dangling", f"Route {rid} target {target} does not exist", route=rid, target=target)
            require(isinstance(req.get("role"), str) and req["role"] in REQUIREMENT_ROLES, f"route {rid}: invalid requirement role")
            require("required_capability" in req and (req["required_capability"] is None or isinstance(req["required_capability"], dict)), f"route {rid}: required_capability must be null or an object")
            require(isinstance(req.get("compatibility"), str) and req["compatibility"] in {"unknown", "reviewed"}, f"route {rid}: compatibility must be unknown or reviewed")
    reports = []
    for sid, scenario in scenarios.items():
        selected = scenario.get("selected_routes")
        require(isinstance(selected, dict), f"scenario {sid}.selected_routes must be an object")
        graph = {nid: [] for nid in nodes}
        for output, rid in selected.items():
            identifier(rid, f"scenario {sid} route selection")
            if output not in nodes or rid not in routes:
                fail("dangling_selection", f"Scenario {sid} selects missing output/route", scenario=sid, output=output, route=rid)
            if routes[rid]["output"] != output:
                fail("selection", f"Scenario {sid}: route {rid} does not produce {output}", scenario=sid)
            if output in terminals:
                fail("false_terminal", f"Terminal {output} cannot also select a producing route", scenario=sid, id=output)
            graph[output] = [rid]
            graph[rid] = [req["target"] for req in routes[rid]["requires"]]
        witness = cycle_witness(graph)
        if witness:
            fail("cycle", f"Scenario {sid} has a directed dependency cycle", scenario=sid, cycle=witness)
        # The graph is acyclic; evaluate dependencies before callers without recursion.
        evaluated, reasons = {}, {}
        pending = [(nid, False) for nid in nodes]
        while pending:
            item, expanded = pending.pop()
            if item in evaluated:
                continue
            children = graph[item]
            if not expanded:
                pending.append((item, True))
                pending.extend((child, False) for child in children if child not in evaluated)
                continue
            blockers = []
            if item in routes:
                record = routes[item]
                if not record["inventory_complete"]:
                    blockers.append("requirement inventory incomplete")
                if not record["reviewed"]:
                    blockers.append("route not reviewed")
                if not record["requires"]:
                    blockers.append("nonterminal route has no recorded prerequisites")
                for req in record["requires"]:
                    if req["compatibility"] != "reviewed":
                        blockers.append(f"compatibility unknown: {req['target']}")
                    capability = req["required_capability"]
                    if not capability or has_unknown(capability):
                        blockers.append(f"capability demand unknown: {req['target']}")
                    if unresolved(req):
                        blockers.append(f"requirement conditions unresolved: {req['target']}")
            else:
                record = nodes[item]
                if item not in terminals:
                    if item not in selected:
                        blockers.append("no selected producing route")
                    if not record["inventory_complete"]:
                        blockers.append("output inventory incomplete")
                    if record.get("spec_reviewed", record.get("specification_reviewed", False)) is not True:
                        blockers.append("output specification not reviewed")
                elif unresolved(record["terminal"]):
                    blockers.append("natural terminal has unresolved conditions")
            if unresolved(record):
                blockers.append("relevant unresolved questions or conditions")
            for child in children:
                if not evaluated[child]:
                    blockers.append(f"unclosed dependency: {child}")
            evaluated[item] = not blockers
            reasons[item] = blockers
        natural_endpoints = sorted(nid for nid in terminals if evaluated[nid])
        closed = sorted(nid for nid in nodes if evaluated[nid])
        unexpanded = sorted(nid for nid in nodes if nid not in terminals and nid not in selected)
        selected_ids = set(selected.values())
        counts = {
            "discovered_outputs": len(nodes), "discovered_routes": len(routes),
            "outputs": len(nodes), "selected_routes": len(selected_ids),
            "dependency_edges": sum(len(children) for children in graph.values()),
            "reviewed_route_inventories": sum(routes[r]["inventory_complete"] and routes[r]["reviewed"] for r in selected_ids),
            "reviewed_output_specifications": sum(n.get("spec_reviewed", n.get("specification_reviewed", False)) is True for n in nodes.values()),
            "closed_outputs_including_terminals": len(closed),
            "closed_outputs_excluding_terminals": len(set(closed) - terminals),
            "reviewed_natural_terminals": len(terminals), "closed_natural_endpoints": len(natural_endpoints),
            "unexpanded_nonterminal_outputs": len(unexpanded),
            "blocked_outputs": sum(n.get("research_status") == "blocked" or bool(n.get("blockers")) for n in nodes.values()),
            "accepted_evidence_outputs": sum(n["maturity"] == "accepted" for n in nodes.values()),
            "known_unresolved_questions": sum(len(n.get("unresolved_questions", [])) if isinstance(n.get("unresolved_questions", []), list) else int(bool(n.get("unresolved_questions"))) for n in list(nodes.values()) + [routes[r] for r in selected_ids]),
        }
        roots = scenario.get("roots", list(nodes))
        require(isinstance(roots, list) and all(isinstance(r, str) and r in nodes for r in roots), f"scenario {sid}.roots must be existing output IDs")
        reports.append({"id": sid, "scope": "complete declared scenario inventory", "counts": counts,
                        "maturity_counts": dict(sorted(Counter(n["maturity"] for n in nodes.values()).items())),
                        "closed_outputs": closed, "natural_endpoints": natural_endpoints,
                        "unexpanded_outputs": unexpanded, "closure": {nid: evaluated[nid] for nid in nodes},
                        "blockers": {nid: reasons[nid] for nid in graph if reasons[nid]},
                        "structural_links": [[source, target] for source, children in graph.items() for target in children],
                        "roots": roots, "target_research_closed": bool(roots) and all(evaluated[r] for r in roots) and not unresolved(scenario),
                        "executable": bool(roots) and all(evaluated[r] for r in roots) and all(evaluated[r] for r in selected) and not unresolved(scenario),
                        "physical_acceptance_proven": False})
    return {"ok": True, "revision": registry["revision"], "scenarios": reports,
            "guarantees": ["declared referential integrity", "acyclic selected scenarios", "conservative recursive research closure"],
            "limits": ["review flags are assertions, not verified evidence", "semantic identity and requirement completeness require human review", "no physical feasibility or acceptance guarantee"]}


def load_json(path):
    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                fail("duplicate_key", f"Duplicate JSON object key: {key}")
            obj[key] = value
        return obj

    def invalid_constant(value):
        fail("schema", f"Nonfinite JSON constant is invalid: {value}")

    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            return json.load(handle, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail("read", f"Cannot read JSON {path}: {exc}")


@contextmanager
def exclusive_lock(path, timeout=10):
    lock_path = Path(str(path) + ".lock")
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                fail("locked", f"Registry is locked: {lock_path}; inspect owner before removing a stale lock")
            time.sleep(0.05)
    try:
        os.write(fd, str(os.getpid()).encode("ascii"))
        os.fsync(fd)
        yield
    finally:
        os.close(fd)
        lock_path.unlink()


def apply_proposal(registry_path, proposal, lock_timeout=10):
    registry_path = Path(registry_path).resolve()
    require(isinstance(proposal, dict), "Proposal must be an object")
    require(type(proposal.get("base_revision")) is int, "base_revision must be an integer")
    require(not (set(proposal) - {"base_revision", "upsert_nodes", "upsert_routes", "scenarios", "proposal_id", "author", "reason"}), "Unsupported proposal field; dependency links must be generated from selected routes")
    changes = {"nodes": indexed(proposal.get("upsert_nodes", []), "upsert_nodes"),
               "routes": indexed(proposal.get("upsert_routes", []), "upsert_routes")}
    if "scenarios" in proposal:
        indexed(proposal["scenarios"], "scenarios")
    with exclusive_lock(registry_path, lock_timeout):
        current = load_json(registry_path)
        require(isinstance(current, dict), "Registry must be an object")
        require(type(current.get("revision")) is int, "Registry revision must be an integer")
        if current["revision"] != proposal["base_revision"]:
            fail("stale_revision", "Proposal base revision does not match current registry", base_revision=proposal["base_revision"], current_revision=current["revision"])
        # Validate existing state as well as the entire union; an upsert cannot hide duplicate IDs.
        validate_registry(current)
        updated = copy.deepcopy(current)
        for collection, replacements in changes.items():
            existing = {record["id"]: record for record in updated[collection]}
            existing.update(copy.deepcopy(replacements))
            updated[collection] = list(existing.values())
        if "scenarios" in proposal:
            updated["scenarios"] = copy.deepcopy(proposal["scenarios"])
        updated["revision"] += 1
        report = validate_registry(updated)
        updated.setdefault("revision_log", []).append({"revision": updated["revision"], "base_revision": current["revision"],
                                                       "outcome": "accepted", "proposal_id": proposal.get("proposal_id"),
                                                       "author": proposal.get("author"), "reason": proposal.get("reason")})
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=registry_path.parent,
                                             prefix=registry_path.name + ".", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(updated, handle, indent=2, ensure_ascii=False, allow_nan=False)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, registry_path)
            temporary = None
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("registry")
    apply = commands.add_parser("apply")
    apply.add_argument("registry")
    apply.add_argument("proposal")
    args = parser.parse_args(argv)
    try:
        report = validate_registry(load_json(args.registry)) if args.command == "validate" else apply_proposal(args.registry, load_json(args.proposal))
    except GateError as exc:
        print(json.dumps(exc.as_dict(), ensure_ascii=False))
        return 1
    except (OSError, TypeError, ValueError) as exc:
        print(json.dumps({"ok": False, "code": "io_or_schema", "message": str(exc)}))
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
