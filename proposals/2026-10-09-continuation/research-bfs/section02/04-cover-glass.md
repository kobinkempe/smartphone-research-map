# Cover glass

**Part · evidence research draft · closure open.** Cover glass is the handset's front optical/mechanical protection, distinct from the glass supporting the display backplane. BFS item 4/5, level 1, selected `discovery-cover-glass-v1`, scenario `coordinated-discovery-v1`, order revision 52 and scoped snapshot revision 53. The selected hypothesis cuts/finishes sodium aluminosilicate sheet and chemically strengthens it in a potassium-salt bath. Commercial ion exchange supports the principle; it does not supply a proprietary composition or our recipe.

<details><summary>Required capability</summary>

One incorporated cover plus coupon/reject stock, quantities not yet specified. Geometry, thickness, edge shape, flatness, transmission/haze, spectral range, refractive index, surface quality, flaw population, compressive stress profile/layer depth, interior tension, impact/scratch behavior, bonding compatibility and touch optical integration are **not yet specified**. A finished surface must meet the assembled handset's testable protection and optical target. No vendor's values are adopted as our acceptance limits.

</details>

## Immediate inventory

| Existing selected ID | Role and use |
|---|---|
| `aluminosilicate-sheet` | Part incorporated after cutting/finishing; exact sodium-bearing composition and sheet quality unknown |
| `potassium-salt-stock` | Part consumed/allocated to salt bath; current candidate is purified potassium nitrate |
| `glass-strengthening-bath` | Tool reused for compatible vessel, heat and controlled immersion |
| `lens-polishing` | Tool reused for appropriate edge/surface finishing; cutting capability not established |
| `optical-metrology` | Tool reused for optical/damage inspection; generic microscope is not a stress-profile measurement |
| `dimensional-metrology` | Tool reused for independent geometry acceptance |
| `surface-cleaning` | Tool reused for pre/post treatment cleaning, with materials/stock unresolved |
| `tongs`, `supports` | Tools reused for glass handling/immersion at actual salt, temperature, load and exposure duty |

All nine selected dependencies are retained. Operational physical obligations also include a specific sheet cutting/sizing fixture and blade/scoring/abrasive method; edge supports and polishing compound; qualified rinse water/cleaning media; clean drying/covered storage; compatible bath racks and draining/cooling supports; salt assay/condition monitoring; temperature/time observation and independent reference transfer; ventilation, splash/contact protection and segregated salt/rinse waste capture. Existing `precision-machines`, `polishing-compound-stock`, `pure-water`, `containers`, `temperature-instruments`, `clocks` and `time-comparison-reference`, `analytical-instruments`, `chemical-protection-equipment`, `chemical-effluent-equipment` and `workshop-surfaces` are candidates to match, not a verified complete inventory. Both time identities exist, but their timing range and independent reference qualification are unresolved.

`glass-strengthening-bath` currently has refractories, heat treatment, temperature instruments, supports, tongs and ventilation. Its compact inventory does not establish a corrosion-compatible salt-contact vessel, heat uniformity, bath purity or independent acceptance. A refractory suitable for fuel firing need not be suitable for molten nitrate contact. Consumable heating stock and replenishment belong to the actual operation, not merely apparatus construction.

## Bounded making method and source scope

Select a chemically compatible sodium aluminosilicate sheet with measured geometry and flaw condition. Choose one cutting/edge-finishing method and qualify it on samples. Size and finish the cover before the selected strengthening treatment, then clean it without leaving contamination or damage. The cut-first sequence is a proposal requiring a recipe specific to this glass; it is not a universal prohibition on later glass processing.

Corning explains that a heated salt bath exchanges larger potassium ions for sodium ions and creates surface compression. Its FAQ mentions approximately 400°C for its own process. This is **context**, not our setpoint, dwell time, salt formula, compressive-stress target or heating tolerance. Those must be established for our composition and dimensions. [Corning ion-exchange FAQ](https://www.corning.com/gorillaglass/worldwide/en/faqs.html) [G1]

Prepare/verify the salt and bath, account for startup inventory and contamination, and use qualified racks/tongs to immerse the clean cover with reproducible temperature and time history. Drain/withdraw using compatible tools, cool by a supported thermal sequence, clean residual salt, dry and protect the surface. Testing samples consumes actual glass/salt and may require rejected-lot replacement; unused bath or recycled salts cannot supply the first batch without earlier stock. These steps are a bounded design inference pending primary recipe and experimental verification.

Corning's controlled-edge-impact study shows edge contact can introduce strength-limiting flaws, and assesses damage with controlled impact and subsequent bending. It establishes that visible appearance and generic polishing are insufficient acceptance; its sample dimensions and measured stress values are not specifications for this phone. [Controlled edge damage study](https://www.corning.com/microsites/csm/gorillaglass/PI_Sheets/COR_GG_WhtPaper_Controlled_Edge.pdf) [G2]

## Acceptance and reuse

Measure dimensions, surface/edge quality and optical transmission/haze independently. Define the required stress/depth/profile and interior-tension acceptance before selecting metrology. Orihara lists surface stress and layer-depth measurement and advertises cross-section stress-distribution and double-ion-exchange features. These are manufacturer capability claims, not qualification of our glass. Its stated ranges/accuracy refer to standard glass and depend on wavelength, photoelastic constants and refractive-index distribution. [Orihara surface stress meter](https://www.orihara-ss.co.jp/catalog/photoe/FSM/FSM-6000X_E.pdf) [G3]

The full-profile/interior-tension obligation stays explicit where the eventual consumer requires it. Neither a surface photograph nor the catalog alone supplies that accepted capability. Independently establish optical constants, usable wavelength/fringe response, specimen interfaces, stress-reference transfer and uncertainty for the actual glass. Do not adopt standard-glass guide ranges or accuracy as project targets. The required physical host, program loading and power remain prerequisites; measurement software is a black box.

No canonical glass-stress fixture was found in the inspected global index by glass/stress/optical function. `optical-metrology` currently selects `frontier-optical-metrology-v1`, whose requirements are microscope, length reference, jigs, lights and workshop surfaces; that inventory cannot be presumed to measure stress. Request coordinator assignment for a glass-stress measurement capability or an explicit extension with construction, reference transfer, optical constants, coupling media and earlier host/power. Surface stress/layer depth and any required full profile/interior tension must each have explicit scope and uncertainty acceptance; the proposed profile-instrument identity is an unmet capability request. Controlled mechanical acceptance must preserve G2's two operations: dynamic edge-damage introduction followed by separate four-point bending. The proposed fixture needs distinct impact carriage/drive, specimen-angle support, hard contact tip, force/velocity readout and references, then bend-loading/support-span/contact geometry with independently referenced force; both need containment and destructive sample stock. Existing generic pull/protection/wheel fixtures have different duties and cannot silently replace these operations.

Existing tongs/supports are preferred identities but the lower wooden-grip trial is explicitly excluded from this molten-salt duty. No demonstrated heat/chemical capability exists simply because an ID is present. Any electronic readout/control program is a black box requiring its physical host/loading/power before the test.

## Alternatives and remaining work

Thermally strengthened glass and a different aluminosilicate chemistry have different thickness, heat, stress and fracture obligations. Sapphire or polymer protection changes optical, machining and damage behavior and cannot silently replace the phone's capability target. Keep these nonselected candidates separate. The current ion-exchange route remains selected, conditional and open.

**Next review:** freeze glass composition/geometry and protection target; select cutting/cleaning/heat recipe; assign stress and strength metrology identities; qualify salt-contact handling and waste equipment. No endpoint or manufacturing path is closed.

