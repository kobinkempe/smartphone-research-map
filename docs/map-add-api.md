# Automated shared map additions

Any discovery agent can add a compact inventory through the shared add operation. A coordinator approval step is not required for ordinary discovery additions. The operation normalizes records, checks the entire selected graph, rejects cycles and missing references, and saves accepted changes atomically. The map view and Tool-name bank refresh automatically.

From smartphone-research, run `python -B scripts/add_discovery.py proposals/your-draft.json`. Python callers can import `add_to_map` from scripts/add_discovery.py and pass the same dictionary.

## Compact draft

Supply new_items for newly identified outputs, and expansions for immediate making inventories. Each new item has id, name and role (part/tool), plus a short function and reuse assessment when known. Each expansion has output, method and requires. Requirement rows may use existing IDs or unambiguous names/aliases; target, use and reason are preferable to a bare name. Methods considered and the choice reason can be kept in the draft audit. New records and requirements remain unreviewed discovery hypotheses.

Example: a draft can introduce a lens spacer blank and expand its selected shaping method using an existing metal stock, machine and measuring tool. All those targets must resolve. The operation fills required schema fields and unknown capability demands automatically. It does not approve suitability or natural-resource closure.

## Success and failure

Success returns ok:true, status:accepted and the new graph revision. The browser files and tool bank update before normal completion. If an addition is saved but page refresh fails, the result explicitly says the addition is accepted and the view failed; repair the view without resubmitting the same addition.

A rejected circular dependency returns ok:false, status:rejected, code:cycle and the exact closed path containing output and route IDs. No partial node, edge, route or revision is saved. The CLI records the attempted compact inventory and result under data/add-attempts/. The worker tries a quick alternative from memory, then escalates unresolved loops and moves on.

Independent agents can submit at the same time. A file lock and revision check serialize commits. For new additions with no explicit base_revision, a concurrent change triggers a fresh normalization and full-graph check. Two individually safe additions that together create a loop cannot both commit.

Existing selected recipes are protected against silent overwrite. Intentional replacement requires the current base_revision and expected_route on that expansion. Replacements and explicit stale requests fail when their assumptions are no longer current. Name aliases cannot bypass this guard.

For large batches, --defer-view saves additions while postponing the expensive page generation; finish with `python -B scripts/build_pages.py`. Ordinary additions use the default automatic refresh. The rendered view is built while holding the registry lock so its links and copied JSON match one revision.

The structural check proves referential integrity and absence of declared selected cycles. It does not prove complete inventories, physical feasibility, suitable capability, verified resources or final handset performance. The coordinator's research and spot checks follow discovery.
