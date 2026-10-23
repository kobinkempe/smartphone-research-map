# Research dependency contract

Scope clarification, 8 October 2026: software implementation and computing bootstrap for creating software are explicit black-box allowances. Software-bootstrap examples below describe the earlier unrestricted problem and are not current research assignments. Record software functions, physical host/loading hardware and availability timing. Apply manufacturing edges and closure to physical requirements. Software and real-world services are not natural endpoints. Current research-rules.md and research-agent-prompt.md govern this scope.

This is a proposed research contract, not a manufacturing feasibility claim or permission to alter the Site. It covers one modern high-end handset, including installed software, that can plug in, charge and work on real-world networks. Manufacture starts with knowledgeable humans, collective labor and naturally occurring resources. No inherited manufactured object, stock material, instrument, facility, executable file, computer, power service or industrial supply chain is available as a manufacturing prerequisite. Existing towers, outlets and standard chargers are outside the construction scope and are explicit external interfaces for final operation/acceptance. They are never natural terminals and never count as raw-material closure.

## 1. Freeze the target before claiming closure

Record a versioned handset target with measurable requirements: compute and memory capability; display; imaging; audio; sensing; enclosure; battery, battery management, protection and charging interface/circuitry; radios, antennas and supported network standards; operating system, applications and firmware; usability and reliability; and all required acceptance tests. Specify the intended real-world charger/network interface and compatibility conditions, including any required external service credentials. Decide whether “high-end” means a particular current handset's specification or a stated equivalent. Mark every undecided requirement `UNKNOWN`, with an owner. Naming the target Phone does not resolve its specification.

Knowledge and labor are permitted starting conditions, but knowledge does not imply possession of exact proprietary designs, process recipes, firmware, signing keys, licensed code or usable executable binaries. Target changes produce a new scenario/version and revised denominator. A weaker teaching device cannot silently satisfy the high-end target.

## 2. Objects and dependency direction

Use stable IDs and terse names; keep specifications, evidence and explanations in the record. The dependency graph has two node types:

| Record | Required content |
| --- | --- |
| Output | ID/version; short name; physical item, material, software artifact or delivered capability; quantified specification; required amount/capacity; provenance; acceptance state; evidence and unresolved questions |
| Process route | ID/version; operation that delivers one or more outputs; complete AND-set of requirements; yields/losses; operating envelope; assumptions; test plan; evidence; unresolved questions |

An output points to its **selected producing process**. That process points to every **required output**. Arrows mean “requires,” so prerequisites occur earlier in execution even though traversal moves toward them. A process's `produces` field is inverse metadata, never another dependency arrow. Part/Tool labels can remain presentation roles; a tool is itself an output that requires a making route.

Requirements include inputs, reusable tools, fixtures, consumables, power, water, gases, vacuum, buildings, environmental control, transport/handling, human-support services where required by the selected scenario, measurement references, computing/control, and acceptance equipment. “Facility,” “test equipment,” “power,” and “software” are unresolved groups until their contents and required capabilities are explicit. A bounded page may group records visually; grouping cannot terminate expansion.

Containment, explanatory links, evidence citations, diagram connections, parent navigation, caller history and backlinks do not enter the dependency relation. The user can return to Phone from a tool without creating a dependency from that tool to Phone.

## 3. Alternatives, capability tiers and shared production

Represent alternatives as OR choices over process routes; each chosen route has an AND-set of requirements. A scenario records a compatible route selection and its conditions. For example, a geological condition must be supported rather than assumed because it makes extraction convenient. Unknown conditions leave the route conditional, not executable.

The candidate catalog is an AND-OR research space, not one executable dependency graph. A live dependency edge belongs to a versioned selected scenario; nonselected routes remain alternative metadata/proposals. Mutually exclusive alternatives must not be merged into a union and then called the build plan. Every published executable scenario must be acyclic. Cyclic alternatives can remain staged as `BLOCKED`, with the bootstrap problem visible; they cannot be published as executable routes.

Define tiers by measurable capability and actual prerequisites, not by labels such as Primitive or Advanced. An output can satisfy a requirement only if its specification meets that requirement, including quantity, accuracy, purity, power, stability, throughput and environment. Immutable versions distinguish changed specifications or routes. A compatibility record explains substitutions; matching names or higher version numbers are insufficient.

Check semantic identity as well as IDs. Renaming the same dependency Generator 1/Generator 2 or Meter A/Meter B does not resolve a physical bootstrap cycle. A legitimate lower tier must be buildable with strictly earlier available capabilities and must meet its caller's requirements. More capable equipment can be built using earlier equipment; do not rewrite the earlier route to depend on the later replacement.

Represent a shared process with several outputs once, as a production hyperedge/job. Requirements are charged once per actual job, while quantities, batch yields, co-product availability and allocation remain explicit. A co-product is available only after that job has the necessary starting inputs; it cannot supply its own first batch. Jointly produced outputs must retain their coupled route selection and yield constraints.

Reuse requires availability and capacity, not just a shared ID. Concurrent loads, destructive tests, contamination, wear and repeated consumption can require additional units or batches. Reusable assets need required service life and replacement inputs. Rework, repair and steady-state recycling belong in temporal operation plans with a demonstrated starting inventory and material balance; they must not become fabricated prerequisites for the first instance. Maintenance needed before target acceptance is in scope. Later operation beyond the specified service period is separately scoped.

## 4. Terminal and closure rules

Only explicitly reviewed starting conditions can be terminals: knowledgeable humans/labor and an identified natural resource or natural phenomenon in its naturally available state. Ore in the ground can be a terminal; mined, sorted or transported ore needs a route. River flow can be a terminal; delivered electrical power, stored water, a channel or a turbine cannot. Natural availability needs supported site/resource assumptions and usable quantity, not merely an element's existence on Earth.

External interfaces are a separate declared boundary state, with an explicit out-of-scope owner and compatibility contract. Final tests may use existing chargers and networks under this boundary; manufacture of the handset's own charging system, battery management, radios/antennas and software/firmware remains in scope. Manufacturing facilities cannot borrow the external charging/network boundary to hide imported electricity, computers or instruments. Report handset manufacturing closure under the declared boundary separately from real-network/charging acceptance and from full raw-material closure; an external leaf is never counted as closed to natural resources.

Human hands may perform a specified direct action. That does not make arbitrary precision, cleanliness, heat, force, measurement or throughput available. Any equipment or prepared environment required to achieve the process specification needs expansion.

A node with no recorded requirements is an **incomplete leaf** unless it has passed terminal review. `UNKNOWN`, `NOT_RESEARCHED`, `PROPRIETARY_GAP` and `UNRESOLVED_BOOTSTRAP` are blockers, not resources and not terminals. A placeholder is visible and countable but cannot close a branch.

Structural closure is recursive: a reviewed terminal is closed; a nonterminal output is closed only when it has a selected adequately specified route, its requirement inventory is reviewed, every requirement is closed and compatible, and no relevant unknown remains. This is research closure, not proof that fabrication will succeed. Physical feasibility and acceptance require separate evidence. Closed children do not close a parent whose requirements have not been reviewed for omissions.

Research status, evidence maturity and closure are separate fields. Suggested research states: `unstarted`, `in progress`, `reviewed`, `blocked`. Suggested evidence maturity: `proposed`, `documented`, `demonstrated`, `accepted`. Specify what was demonstrated and at which tier; evidence from a different capability is not transferable without justification. None of these labels substitutes for closure.

## 5. Candidate staging and the atomic gate

Agents submit candidates to one central staging queue. They may write proposals, notes and ordinary navigation links; they never create or change live dependency links. Each proposal carries:

- Proposal ID; author/owner; base graph revision; affected output and route versions; required target IDs; edge roles and capability demands.
- Sources/evidence, uncertainty and assumptions; complete route requirements or an explicit incompleteness flag; alternative conditions; co-product coupling; specification and quantity changes.
- Reason for addition/removal and any affected accepted scenario. No implicit target creation or name-based ID resolution.

One graph custodian owns a transactional gate. Under a lock, or equivalent compare-and-swap with retry, it validates the whole proposed change against the latest revision and publishes it atomically:

1. Resolve all IDs; reject dangling targets, malformed types, duplicate/conflicting versions and missing required fields. Stubs can exist only as explicit incomplete output records.
2. Generate dependencies from each selected route's full requirement set; agents cannot omit a required link to make validation pass. Validate route selection, conditions and shared-job coupling. Reject direct self-dependency and every directed cycle in every affected live scenario, including cycles crossing several proposals. Cycle detection covers the complete transitive graph, not merely the changed page.
3. Check declared tier compatibility, quantities and terminal rules; send semantic/bootstrap and requirement-completeness decisions to human review. Unknowns prevent executable/closed status.
4. Recheck revision and all conflicts, then commit nodes, edges, selections and review/status changes together. If another transaction has committed, rebuild and revalidate; do not commit a stale validation result.
5. Record accepted/rejected/deferred outcome, cycle witness or other reason, reviewer, evidence and revision. Publish no partial link set. Removing a dependency or changing a target/route also invalidates affected closure and requires review.

Automated checks can guarantee referential integrity, exact version handling, transactional consistency and graph acyclicity for the declared scenario. With sufficiently explicit data, they can detect unit/capacity mismatches and some conflicts. They cannot guarantee that agents listed every physical requirement, that renamed tiers differ meaningfully, that a source supports the needed performance, that proprietary knowledge is accessible, or that the process works. Those require technical review and ultimately experimental evidence. A DAG can still be physically impossible.

## 6. Acceptance, calibration and software bootstrap

Separate a built-but-unqualified item from its accepted capability when qualification creates dependencies. For example, an uncalibrated instrument can exist before a calibration operation yields a calibrated instrument; the latter may be required to accept a phone component. It cannot serve as the independent reference that certifies its own claimed accuracy. Calibration records specify reference construction, uncertainty, range, transfer method and required fixtures/environment. Reference dependencies must close to a supported earlier standard or physical realization under the scenario.

Runtime self-measurement and feedback inside an apparatus are not automatically fabrication dependencies on the finished apparatus. Their sensors, controller, power and software are physical prerequisites. An independent acceptance path must establish the apparatus's claimed capability. Distinguish assembly sequencing, runtime feedback and evidence dependencies explicitly.

Software artifacts need actual routes to an installed runnable state: source/design knowledge, host hardware, editing/input and storage, assembler/compiler or a documented manual seed, build tools/libraries, programming/flashing interface, boot path, drivers/firmware, verification and any keys or permissions the chosen design requires. “Download,” “use open source” and “already know the program” do not create a computer or executable. A compiler built by that same compiler needs a justified earlier seed or host. Control electronics for furnaces, precision stages and metrology need earlier fabrication/programming routes; do not assume a modern phone or semiconductor fabrication line exists to build its own first controller.

Essential adversarial checks before accepting a scenario:

| Proposed relationship | Required finding |
| --- | --- |
| Wire production needs a generator; the generator needs that wire | Reject the cycle unless a specified earlier wire/power route closes and meets its demand. |
| A meter's acceptance needs the same calibrated meter | Split unqualified/qualified states and provide an independent calibration route. |
| A machine uses its later improved replacement to make its first instance | Reject; preserve a real earlier-tier construction route. |
| A fabrication tool's controller needs chips fabricated only by that tool | Require an earlier controller route; a name change is insufficient. |
| A tool's software needs its own not-yet-built compiler or computer | Require a supported seed and a host-building/programming path. |
| Co-product/recycled material starts the job that first produces it | Require starter inventory from a closed route and quantity/time accounting. |
| Two concurrent proposals each pass alone but form a cycle together | The second atomic transaction rejects or defers the joint cycle. |
| A return link opens Phone from a fixture | It remains navigation metadata and does not affect closure. |

## 7. Roles, route choice and honest progress

Use bounded responsibilities: target owner freezes requirements; domain researchers propose output/process records and evidence; bootstrap/metrology/software reviewer checks cross-domain capability transitions; integration reviewer audits omitted facilities, utilities and quantities; graph custodian alone operates the gate; an independent closure reviewer challenges terminals and the selected route. Small teams can combine roles, but authors should not be the only reviewers of critical bootstrap claims. These are recommended responsibilities, not a request to spawn additional agents.

Choose routes against the current accepted prerequisite set. Compare the **union of new required capabilities** and their upstream closure, reusable capacity already available, total resource/facility demand, evidence quality, uncertainty and estimated effort. Short local paths can introduce enormous new industries; repeated links to one reusable tool do not represent multiple fabrication jobs. Record estimates as ranges, identify unknown effort, and explain tradeoffs. Do not claim a globally shortest route: an incomplete AND-OR space with coupled yields/capacities and unknown costs cannot support that proof. Heuristic “best among these researched routes under these assumptions” is an honest claim.

Every progress report names target/scenario version, graph revision and scope, and gives counts with explicit denominators:

- Reachable outputs `O`, process routes `P`, dependency edges `E`, reviewed natural terminals `T`; report discovered inventory size without implying completeness.
- Requirement inventories reviewed `R / P`; output specifications reviewed `S / O`; structurally closed outputs `C / O`, with terminals included/excluded stated explicitly.
- Unexpanded nonterminal outputs `U / O`; blocked outputs `B / O`; relevant unresolved questions `Q` (known count, no claim that all unknowns have been found).
- Accepted physical outputs/capabilities `A / O`, stating the evidence threshold; target acceptance tests satisfied `K / J`, where `J` is the frozen test set.

Denominators can grow as research exposes requirements. Publish changes alongside each snapshot; never convert “completed pages / authored pages” into whole-phone or whole-universe completion. A zero-cycle count measures declared graph health, not manufacturing feasibility. Report target research closure and target physical acceptance as distinct yes/no results with outstanding blockers.

## 8. Highest-priority unresolved issues

1. **Target specification:** “modern high-end” is not yet testable. Freeze equivalence, connectivity/standalone expectations, software scope and acceptance conditions before claiming meaningful completion.
2. **Semiconductor and precision capability bootstrap:** expose required design information, materials/purity, tooling, environments, control and independent metrology at the actual target tier. Teaching-scale fabrication is not evidence for high-end capability.
3. **Proprietary and inaccessible information:** flag unavailable chip designs, production know-how, modem firmware, drivers, signing material, standards compatibility/certification, patents/licenses or other restrictions as specific gaps. Real-network operation needs a supported compatibility route, not merely a generic radio. Do not infer that a secret recipe is known because humans begin with general knowledge. Research possible compatible open/reconstructed routes separately.
4. **Calibration and acceptance bootstrap:** instruments, references and standards are first-class requirements. Audit self-certification and acceptance conditions that were silently weakened to close a branch.
5. **Facilities and consumables:** quantity, lifetime, purity and capacity can invalidate an otherwise acyclic chain. Audit every abstract factory/tool/material group and every natural-terminal claim.
6. **Hidden electronics/software imports:** check every automated process, test instrument and software-build step for an inherited host, controller, binary, network download or manufactured storage medium.

These are review priorities and explicit unknowns, not researched conclusions that a particular modern handset route is either feasible or impossible.
