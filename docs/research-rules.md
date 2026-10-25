# Research rules and goals

Draft contract for review • 8 October 2026 • Target v1

Continuation status: the user authorized coordinated discovery and research on 8 October 2026. The first-checkpoint descriptions below preserve the earlier recovery context; they no longer indicate a pending permission step. Target-level numerical acceptance requirements remain open.

Later user revision: any discovery agent may submit additions through the shared automated add operation in scripts/add_discovery.py. It normalizes compact inventories, checks the whole selected graph, saves valid additions atomically and refreshes the map; circular dependencies fail with the exact loop and no registry changes. This supersedes earlier wording that reserved every insertion for the coordinator. Manual edits that bypass the gate remain prohibited. The coordinator performs later spot checks, identity coordination and deeper research assignments. The current memory-first seven-step procedure is in discovery-agent-prompt.md.

## The goal

A group of knowledgeable people arrives on an Earth on which humans have never lived. They have no manufactured equipment, stock materials, buildings, electronics or utilities. They follow this project's instructions to make the physical hardware of one modern handset with flagship-equivalent capabilities. Software development is an explicit black-box allowance: compatible software may be installed after the hardware enters the real world. The finished handset must charge from a standard real-world charger and function on real-world networks. Exact quantitative performance targets remain to be researched and frozen; the phrase "high-end" is not an acceptance specification.

Cell towers, household outlets, standard external chargers and operating networks are external interfaces. They need not be manufactured in this project. The phone's charging connector and circuitry, battery management hardware, radio hardware, antennas, processor, memory and software-loading interface remain in scope. The operating system, firmware, applications, protocol software, development tools and control programs are black boxes; do not research source code, compiler creation or a software bootstrap chain. Still specify compatible hardware, the physical programming connection and the required software functions. Carrier subscription, SIM provisioning or network permissions are explicit external service conditions. These allowances never count as natural endpoints and do not supply physical workshop equipment or power.

For manufacturing equipment, list any required control software in a separate black-box requirements section with its function, host hardware and when it must be available. Do not assume software installed on the finished phone after import can control an earlier manufacturing step. The software itself needs no making page. Its computer, storage, controller, programmer, cables and electrical supply are physical requirements wherever needed. Final software and network compatibility tests may occur after import. Research closure refers to physical paths under these stated allowances, not a wholly self-contained recreation of software and external services.

Public designs or different materials may replace proprietary implementations if they meet the target capability. A simpler demonstration is a separate earlier tier, not a silent downgrade of the final phone. The project optimizes credible total setup and work for one successful phone, including necessary trial pieces and losses; it does not reproduce commercial throughput by default or promise a proven globally shortest route.

## What every making page must contain

Use a simple title and the visible role **Part** or **Tool**. Materials and consumed inputs are Parts; power supplies and facility equipment are Tools. A process is a bounded making method inside a page. Software black boxes are boundary records outside manufacturing research; the hardware and tools that run or install them remain explicit.

The first paragraph states what the output does, which consumer needs it and the research status. A collapsible specification block holds the required capability: size and quantity; purity; dimensional precision and surface condition; mechanical, electrical, thermal or optical performance; compatible interfaces; environment; and acceptance tests. Unknown values say “not yet specified.” Do not invent tolerances or put technical strings in item names.

The page's mandatory core is an inventory of every known physical requirement. Record structural parts, feedstocks, consumables, fabrication tools, fixtures, work surfaces, containers, handling and transport equipment, lubricants, joining materials, water, heat, electrical supply, gases, vacuum, cooling, environmental controls, necessary protection and waste handling, measuring equipment, calibration references, and control hardware/software. Make explicit which are reused, incorporated, consumed or required for verification. An external article can carry detailed process data; it cannot replace this inventory.

Making steps show where those items are used. A Tool page explains how to make that tool; instructions for using it belong in its caller's steps. Split large assemblies into independently understandable subassemblies or operations. Aim for a core explanation of roughly 600–1,000 words, with sources and technical detail expandable. This is a readability target, never a quota that hides requirements. A grouped item must expose its contents and link to further making pages once its dependencies pass the gate.

Every page also lists primary sources, the claims each source supports, provenance from earlier work, unresolved requirements, rejected or pending alternatives, and next research actions. Source URLs alone do not establish a complete recipe or target-level capability. Review dimensions, units, uncertainty, measurement range, calibration and compatibility against the caller's actual demand.

## No manufacturing loops

Before inventing a new dependency, researchers must inspect the current shared registry, proposals and build/inventory ledger, searching by function and aliases as well as name. Reuse a canonical tool or material when its capability, cleanliness, calibration, quantity and availability meet the caller's demand. Existing research does not itself mean an item is physically built or qualified. Each new ID needs a reuse assessment explaining which existing candidates were checked and why they cannot serve. Multiple required copies normally share one design and making page; consumables still need quantities and replenishment. Reuse cannot create a manufacturing cycle or silently substitute an inadequate capability. The coordinator checks duplicate proposals and maintains shared platform records; every caller still lists its own complete required inventory.

A dependency means that an output or qualified capability must exist before this item can be made or accepted. The selected build scenario is an acyclic graph: output → selected making route → every required output. An assembly's containment, citations, navigation history and reverse “used by” links are different relationships. A return link does not make the earlier phone a manufacturing prerequisite of its tool.

Agents submit structured proposals; they cannot edit live dependency links. A central gate validates IDs, route selection and the complete selected graph. It rejects self-dependencies, missing targets, stale proposals and cycles, including cycles formed across independently submitted changes. Updates are committed atomically. The page renderer draws dependency links exclusively from the validated selection; candidate dependencies remain unlinked draft text.

Alternative recipes are OR choices, while all requirements inside the chosen recipe are AND obligations. Combining incompatible alternatives into one apparent recipe is prohibited. Repeated operation, adjustment, recycling and rework can be legitimate only with a real earlier starting inventory and temporal accounting; they cannot create the first object or reference out of itself. Co-products and shared tool capacity need explicit quantities and scheduling.

Separate a basic tool from an advanced tool only when its capability and actual construction route differ. An earlier source may power or help manufacture its later replacement. Renaming the same power source, controller or meter cannot conceal circular prerequisites. An uncalibrated instrument and a calibrated instrument can be different states, but an independent earlier reference must establish the claimed accuracy.

Automation checks the declared graph. It cannot prove that an inventory is complete, a tier is physically different, a source supports a claim, or a process is feasible. A technical reviewer audits those questions, and experimentally demonstrated performance is a separate status. A cycle-free graph is necessary but insufficient.

## Endpoints and evidence

A natural endpoint requires an identified, naturally available resource or phenomenon, a supported availability/quantity assumption and reviewer approval. Finding, recognizing, collecting, preparing and transporting it must be represented where required. Refined copper, clean water, sorted mineral stock, a workbench, electricity and a finished plug are not natural endpoints. A node with no known making route is an **unexpanded frontier**, not a completed path.

Use two independent labels. Evidence status progresses through **Discovered**, **Inherited notes**, **Research draft**, **Source-checked**, **Reviewed**, and **Experimentally demonstrated**. A recovered note retains its provenance and does not become source-checked merely because it contains a URL. Closure status is **Open**, **Blocked**, **Closed to nature**, or **External interface**. Research closure requires the specification, complete inventory, selected route, compatible prerequisites and endpoint evidence to be reviewed. Physical acceptance remains a separate claim.

Publish counts for the current target and graph revision: discovered inventory; discovered-but-unresearched percentage; inherited/drafted/source-checked/reviewed pages; selected routes; unresolved frontiers; blocked candidate relationships; reviewed natural endpoints; and manufacturing paths closed to nature. State each denominator, and show growth between snapshots. No page-count ratio is a percentage of the unknowable total phone project.

## Research and review sequence

1. Recover saved research, original decisions and sources. Keep superseded UI choices separate from current engineering rules, and record missing transcript coverage.
2. Discover the broad handset and shared workshop inventory. This first map is a hypothesis, not a bill of materials or a verified build order.
3. Research common bootstrap paths: natural-resource acquisition, coarse metal/tool work, heat, surfaces, dimensional references, mechanical power and earlier electrical generation.
4. Trace the copper → wire → coil → speaker chain, with tool manufacture, calibration and smartphone-quality acceptance in parallel. Compare native-metal or non-electrical earlier routes with refining-dependent alternatives.
5. Research glass/strengthening, batteries, display/touch, optics, circuit fabrication, semiconductor tooling, physical control/programming hardware and live-network compatibility. Specify software interfaces without researching software implementation. Give difficult clusters dedicated reviewers and simpler-route investigations.
6. Audit the complete selected scenario, publish accepted dependency updates, and report what genuinely closes and what remains blocked.

The coordinator owns target definitions, canonical IDs, integration, graph changes and publication. Domain researchers own bounded proposals. A separate reviewer checks omitted prerequisites, evidence and capability matching. Bootstrap/metrology/software specialists challenge self-supporting assumptions and search for earlier routes. Choose concurrency and model settings for the agent environment in use; the registry contract does not depend on one provider or model.

## Source coverage and known limits

The repository contains the research contract, example agent prompts, recovered research pages, a discovery registry and automatic graph checks. Most routes remain unreviewed discovery hypotheses. It is not a completed encyclopedia.

The recovered research covers saved files, original HTML, prototype technical catalogs and selected conversation excerpts used during research. Complete original conversation coverage was not established, and raw transcripts are not included in this repository. Superseded navigation ideas may supply technical citations but cannot become current design decisions.

The research record uses Markdown and JSON, with generated HTML views. Keep source citations as links instead of copying large papers, videos or images. Build output is reproducible from the repository and excluded from Git. The build reports its generated size, enforces a 25 GB local project budget and produces a compressed standalone reading edition for hosting services with per-file limits.

See the repository README for the live demo, local build and validation commands. Hosting account quotas are outside the research contract.
