# Covers

**Part · evidence research draft · closure open.** This report concerns the selected polymer rear-cover hypothesis, a distinct incorporated part from the metal enclosure and front cover glass. It is BFS item 3/5 at level 1, selected route `discovery-covers-v1` in `coordinated-discovery-v1`, order chosen at revision 52 and scoped snapshot revision 53. The name is plural; the actual number of rear pieces and interfaces is not yet specified.

<details><summary>Required capability</summary>

The cover must fit the chosen enclosure, protect internal modules, allow intended radio operation, and retain its fastening/sealing interfaces under the frozen handset loads. Dimensions, wall thickness, flatness, clip strain, polymer family/grade, additives, finish, chemical resistance, temperature range, impact performance, creep, adhesive compatibility, antenna clearance and service life are **not yet specified**. Required stock includes trial shots, runners, trimming and rejects, with quantities unknown. Flagship-equivalent appearance or durability cannot be inferred from a molded shape.

</details>

## Immediate inventory

| Selected canonical ID | Role and use |
|---|---|
| `polymers` | Part incorporated; generic one-family synthesis record needs a named compatible feed state |
| `molding-equipment` | Tool reused to shape the selected polymer into the rear cover |
| `adhesives` | Part consumed/incorporated if cover interfaces are bonded; placement needs allocation |
| `seals` | Part incorporated if ingress seals belong to the cover; current fiber packing is unqualified |
| `dimensional-metrology` | Tool reused for independent cover/interface acceptance |

All five selected requirements are retained. The current `molding-equipment` route exposes press frame, metering barrel, die, fuel heating jacket, manual drive, temperature/pressure instruments, water, precision machines, joining tools, ventilation, surfaces, containers, protection, ignition/fuel and a polymer test feed. The selected apparatus inventory also retains `polymer-film-extrusion-stretching-line`; its need and capability for this molding apparatus remain unreviewed, so this report does not remove it. This is reusable apparatus construction, not proof it can fill a thin phone cover. The selected consumer still needs allocated prepared feed, thermal conditioning, mold temperature control/coolant, clean transfer/containment, trimming, inspection and waste stock for the actual job.

For a polycarbonate candidate, add a feed-drying and protected-transfer obligation before melting. Check `dryroom`, `heat-treatment`, `containers`, `moisture-verification-instrument` and `analytical-instruments` for fit. A whole dry room is not automatically a pellet dryer, and a gas dew-point instrument does not automatically measure water inside polymer pellets. This is an unresolved function/identity request after capability matching, not an invented accepted dryer. Mold tooling must include gates/runners, venting, ejector/demolding interfaces and a compatible release strategy. Existing `molding-die-set` is the preferred identity; `casting-moulds` is expendable refractory casting tooling and cannot silently serve as a precision polymer mold.

Heating/cooling, temperature/pressure references, ventilation, handling barriers, work surfaces, cleaning consumables and containers/waste capture remain known physical obligations. `cooling-systems`, `surface-cleaning`, `metalworking-protection` and `metalworking-waste-tray` are candidates requiring compatibility review. Pigments, fillers or protective finishes belong in the incorporated inventory only if selected; a transparent or unfilled cover is a separate material decision. Flexible clips molded into the cover are geometry within this item rather than arbitrary new nodes.

## Bounded making method

Choose one polymer family and formulation, then define the cover geometry and fastening method around demonstrated material properties. Polycarbonate is a research candidate, not a claim that Fairphone uses this feed or that the project's polymer precursor route currently makes it. Prepare the compatible feed at the required moisture/contamination state and preserve that state through storage/transfer. Qualify the mold against the drawing, including shrinkage compensation, flow paths, vents and demolding arrangement.

Covestro documents that moisture during processing can cause visible defects and, for hydrolysis-sensitive plastics, hidden molecular degradation. This supports a real conditioning/verification requirement rather than accepting appearance alone. The brochure does not identify our polymer or prove a locally built dryer reaches its demand. [Covestro drying guidance](https://solutions.covestro.com/-/media/covestro/solution-center/whitepapers/injection-molding-of-high-quality-molded-parts-drying.pdf) [C1]

Heat/plasticate the selected charge, fill the prepared mold with verified drive/pressure capability, hold as needed by the actual formulation/geometry, and control cooling before release. Trim runners and flash without damaging clips or sealing faces. Keep trial settings and reject causes in a material ledger; do not assume regrind from the first successful job can supply the first job. Clean the part, inspect it independently and install the specifically allocated seal or bonded feature. These operations are proposed inferences awaiting a grade-specific recipe.

Covestro's equipment guide ties machine choice to material, shot volume, mold dimensions and clamping needs, and identifies mold heating/cooling capacity as a quality factor. It does not establish that the registry's fuel-heated manual press has sufficient pressure, uniform heating or short-shot control. [Covestro molding equipment](https://www.covestro.com/-/media/covestro/solution-center/brands/downloads/imported/1556891051.pdf) [C2]

Covestro also describes a small-quantity drying cabinet and TVI dryness screening for unreinforced Makrolon/Apec. Treat these as simpler conditional alternatives: cabinet heat/airflow, layer depth, humidity and protected transfer still need qualification. TVI needs a temperature-controlled hot plate, glass slides, pressing/handling and test pellets; it indicates sufficient/insufficient drying, not quantitative water content. If the selected grade or acceptance demands quantitative low moisture, a compatible Karl Fischer or carbide method still needs actual apparatus, reagent/sample stock and independent verification. No other polymer inherits TVI suitability. [Covestro drying guidance](https://solutions.covestro.com/-/media/covestro/solution-center/whitepapers/injection-molding-of-high-quality-molded-parts-drying.pdf) [C1]

## Acceptance and coherent alternatives

Check dimensions/fit independently, then verify attachment retention, seal compression if chosen, impact behavior, heat deformation, chemical interaction with adhesives and intended RF behavior. Tests need compatible fixtures and separate samples where destructive. Candidate existing fixtures include `joint-pull-test-fixture`, `thermal-test`, `chemical-compatibility-test-fixture` and `rf-test`; their current ranges and reference transfer may not meet polymer-cover duty. The cover cannot certify its own impact capability.

A detachable clip/screw cover and a bonded cover differ in stock and acceptance obligations. Do not combine both joining inventories as though each is automatically consumed. Machining a compatible polymer sheet could remove mold-flow dependencies for one-off production but introduces sheet manufacture, machining losses and fragile clip/geometry risks. Compression forming is another candidate with its own pressure, shrinkage and heat evidence. No alternative is established as globally shortest or target-equivalent.

Reuse the canonical molding equipment/die, surfaces and instruments if their actual capabilities and build order suffice. New dryer/fixture identities require coordinator review of existing functions. Software is unnecessary for the presently hypothesized manual press; selecting automated control adds earlier host/controller/loading/power with a black-box program available before molding.

**Next review:** select polymer and joining mode, resolve pellet conditioning versus room humidity, qualify press/die capacity, and allocate test and consumable stock. This page establishes neither complete inventory nor raw-material closure.
