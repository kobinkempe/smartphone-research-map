# Smartphone Research Map

## Public demo

[Open the live demo](https://kobin-ai-portfolio.kobinkempe.chatgpt.site/smartphone-research-map/) · [Read the case study](https://kobin-ai-portfolio.kobinkempe.chatgpt.site/case-studies/smartphone-research-map/)

An agent-assisted research system and interactive dependency map for tracing what it would take to make a smartphone from underlying parts, tools and resources.

![Interactive research map](docs/screenshots/map.jpg)

## Why this is more than a visualization

The hard part is preserving meaning as many research contributions accumulate. Canonical IDs, explicit making routes, source provenance, review states and a conservative graph gate keep the map tied to inspectable data. The map is generated from the same validated registry as the reading pages.

The revision-138 snapshot contains **1,507 records**, **825 candidate routes**, and **734 selected routes**. It still reports **zero closed manufacturing paths**. Most physical outputs remain discovery hypotheses. Structural validity and a visually connected path do not prove capability, completeness or physical feasibility.

## Run from source

Python 3.10+; core scripts use the standard library. Node.js is needed for JavaScript-driven layout/control tests.

```sh
python -B scripts/build_pages.py
python -m http.server 8000 --bind 127.0.0.1 --directory dist
```

Open http://127.0.0.1:8000/map.html. Start with a named item, inspect its dependencies and uses, and compare relationship/path controls. The generated `dist/smartphone-research.html` is an offline reading edition. Generated sites are excluded from Git; build them from the registry.

## The workflow

1. Discovery agents propose immediate making inventories and reuse existing canonical items.
2. The shared add operation normalizes proposals and checks every selected scenario.
3. Atomic revision updates reject cycles, dangling references and stale assumptions without partial publication.
4. Bounded research and independent review attach explicit maturity states and hash-bound evidence artifacts.
5. The renderer rebuilds maps and reading pages, checking dependency links against the validated graph.
6. A human inspects gaps and evidence and guides the next research or interaction experiment.

Read [the full workflow](docs/WORKFLOW.md), [graph gate contract](graph-gate-readme.md), [shared add API](docs/map-add-api.md), and [snapshot scope](SOURCE_SCOPE.md). The companion [prototype lab](https://github.com/kobinkempe/smartphone-prototype-lab) compares six learning interactions; it is not yet automatically driven by this registry.

## Validate

```sh
python -B -m unittest discover -s scripts -p "test_*.py"
python -B scripts/build_pages.py
```

The copied suite passes **79 tests**, including adversarial graph updates, lifecycle/publication checks and Node-driven map geometry/control checks. The source rebuild audits the selected dependency links. These tests establish software properties, not the truth of research flags or manufacturing claims.

## Portfolio and data scope

The repo includes 44 registered evidence/source artifacts, authoring code and prompts. Raw chat logs, unregistered scratch proposals, deployment identifiers, credentials and previous Git history are excluded. The UI consumes local generated data; it does not call a model. Future research execution depends on the chosen agent environment. [Publication review](PUBLICATION_REVIEW.md).
