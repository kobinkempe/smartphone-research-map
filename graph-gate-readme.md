# Declared dependency publication gate

The gate is Python standard-library code. It checks the whole declared graph in every scenario before publishing any registry revision. The research contract remains `research-staging/graph-contract.md` in the project workspace.

Run from the `smartphone-research` directory:

```powershell
python scripts/graph_gate.py validate path/to/registry.json
python scripts/graph_gate.py apply path/to/registry.json path/to/proposal.json
python -m unittest discover -s scripts -p test_graph_gate.py -v
```

Both CLI commands emit JSON. Exit code 0 means the declared registry passed structural validation; it does **not** mean the target is executable, closed or physically accepted. Inspect each scenario's `target_research_closed`, `executable`, `closure`, `blockers` and counts. Failure returns exit code 1 and an error code. Cycle errors include the scenario and exact directed closed path, with both output and route IDs.

## Registry shape

```json
{
  "revision": 0,
  "nodes": [
    {"id":"wire", "name":"Wire", "role":"part", "terminal":false,
     "maturity":"proposed", "inventory_complete":false, "spec_reviewed":false},
    {"id":"native-copper", "name":"Native copper", "role":"natural",
     "terminal":{"kind":"natural", "reviewed":true, "evidence":["site survey reference"]},
     "maturity":"documented", "inventory_complete":true}
  ],
  "routes": [
    {"id":"make-wire", "output":"wire", "inventory_complete":false, "reviewed":false,
     "requires":[{"target":"native-copper", "role":"part",
                   "required_capability":null, "compatibility":"unknown"}]}
  ],
  "scenarios": [
    {"id":"research-draft", "roots":["wire"], "selected_routes":{"wire":"make-wire"}}
  ]
}
```

Output/route IDs must be nonempty strings and globally distinct. Scenario IDs are unique within the scenario list. Duplicate JSON object keys are rejected when reading files, so duplicate route-selection keys cannot silently overwrite each other. Evidence maturity is one of `proposed`, `documented`, `demonstrated`, `accepted`; maturity does not imply closure. `specification_reviewed` is accepted as an alias for `spec_reviewed`.

For each scenario the only dependency arrows are output → selected route and selected route → every required target. All selected edges are generated from the full `requires` array. `navigation`, `parent`, backlinks, explanatory/evidence links and inverse `produces` metadata have no effect on this relation. A nonselected cyclic route is allowed as a candidate; it creates no `structural_links`. Its output and prerequisite IDs must still resolve. A cycle is rejected whenever that route is selected. Every scenario is checked, including draft scenarios.

Only a terminal object with `kind:"natural"`, `reviewed:true` and nonempty evidence can close without a producing route. A terminal may represent an identified natural starting condition or reviewed knowledgeable human/labor starting condition. An `external` role or `boundary:"external"` can never be a natural terminal. Terminal classification and actual evidence support require human review: the program cannot infer that an author falsely called delivered power a natural phenomenon. A terminal cannot also select a producing route.

Nonterminal closure requires a selected route, `inventory_complete:true` on the output and route, `reviewed:true` on the route, reviewed output specification, at least one recorded prerequisite, and recursively closed children. Each requirement needs `compatibility:"reviewed"` and a nonempty `required_capability` object with no null, blank, nonfinite, or `UNKNOWN`/`NOT_RESEARCHED`/`PROPRIETARY_GAP`/`UNRESOLVED_BOOTSTRAP` values. A null demand is unspecified, so closure stays false. Unknown inventory/compatibility/demands permit structurally valid draft links, but never make a branch executable or closed.

Nonempty `unknowns`, `unresolved_questions` or `blockers`, `has_unknowns:true`, `conditional:true`, `research_status:"blocked"`, or unknown values in `specification`, `spec`, `quantity` and `conditions` block the relevant record. Scenario uncertainty blocks target closure/executable status. A route with zero recorded prerequisites is an incomplete nonterminal leaf even if its author set review flags. Optional `roots` determines target closure; without roots every declared output is a target. Counts always cover the entire declared output inventory and selected routes, with candidate route inventory reported separately. `accepted_evidence_outputs` counts the asserted maturity label and is not proof of physical acceptance.

## Atomic proposals

```json
{
  "base_revision": 0,
  "upsert_nodes": [],
  "upsert_routes": [],
  "scenarios": [
    {"id":"research-draft", "roots":["wire"], "selected_routes":{}}
  ]
}
```

Upserts replace complete records by exact ID; they do not merge individual fields or guess IDs from names. Optional `scenarios` replaces the whole scenario list. There is no deletion API. Optional `proposal_id`, `author` and `reason` are accepted for the revision log. Raw dependency-link proposal fields are rejected; only the custodian applies candidates and the gate derives links from selections.

`apply` obtains an exclusive sibling `.lock` file, reads the current registry inside that lock, checks `base_revision`, validates the existing registry and the entire proposed union, writes and flushes a temporary sibling file, then atomically replaces the registry. Revision increments once and an accepted revision-log entry is recorded. Failed or stale proposals publish no partial links and leave registry bytes unchanged. Rejected outcomes and reasons are emitted as JSON rather than written into the registry. With two proposals based on one revision, only the first can commit; the second must be rebased and the joint graph revalidated. All writers must use this gate for the transaction guarantee. A crashed process can leave its lock; inspect the recorded PID and remove that lock only after establishing no writer owns it. Locks time out after ten seconds rather than being automatically stolen.

## Guarantees and review limits

The automated guarantee is referential integrity, explicit ID handling, acyclicity of every selected declared scenario, conservative closure computation, and atomic revision publication among cooperating writers. Twenty-one adversarial tests cover self-dependency, multi-output cycles, all scenarios, dangling candidates/selections, duplicate IDs/JSON keys, navigation, nonselected alternatives, false terminals, unknown or unspecified capability, independent calibrated state, scenario uncertainty, incomplete selected branches, deep traversal, stale/joint-cycle proposals, simultaneous commits, union validation and unchanged bytes on failure.

The renderer obtains manufacturing links exclusively from that validated graph. The publication audit checks actual destinations as well as relationship annotations in the static and standalone editions. The export command validates the captured registry and captured static dependency links, then includes file hashes in its audit manifest. The live hosting integration still needs its source-upload connection before an actual private site can be published.

The program trusts declared review flags. It cannot prove requirement completeness, semantic identity across renamed tiers, resource availability, quantity or unit compatibility, co-product coupling, timing/capacity, access to proprietary designs/software/keys, source adequacy, or physical feasibility. Shared production jobs and temporal plans need a richer reviewed representation before they can claim closure. Changing a dependency or specification must be accompanied by an actual review; setting a review boolean in a candidate is not that review. `physical_acceptance_proven` deliberately remains false. A DAG is a structural research result, not a manufacturing demonstration.
