# Display panel

**Part · evidence research draft · closure open.** The panel converts electrical image signals into visible light and must integrate with the chosen touch/cover stack. BFS item 5/5, level 1, selected `discovery-display-panel-v1`, scenario `coordinated-discovery-v1`, order revision 52 and scoped snapshot revision 53. The parent names a rigid-glass active-matrix OLED; this research exposes allocation and encapsulation-choice questions without replacing the facilities lane's inventory.

<details><summary>Required capability</summary>

One incorporated accepted panel plus process/test/reject stock, quantities not yet specified. Active area, pixel count/pitch, refresh rate, brightness, contrast, color gamut/accuracy, viewing angle, uniformity, defective-pixel acceptance, optical reflection, power, electrical timing/levels, thermal budget, lifetime and environmental limits are **not yet specified**. Backplane current-driving capability, compatible OLED materials/electrodes, moisture barrier, interconnect and driver interface must jointly satisfy the eventual flagship-equivalent handset target. A lit coupon is an earlier demonstration tier.

</details>

## Immediate inventory and hierarchy

| Existing selected ID | Role and use |
|---|---|
| `display-substrate` | Part incorporated glass; allocation with backplane's own substrate unknown |
| `transistor-backplane` | Part incorporated patterned pixel-addressing/current-driving structure |
| `display-oled-stack` | Part incorporated emitter/transport/electrode layers; usually deposited onto the backplane assembly rather than separately installed |
| `display-encapsulation` | Part incorporated moisture/oxygen barrier; selected multilayer-film route requires reconciliation with parent method |
| `flexible-interconnect` | Part incorporated electrical interface; backplane also includes this ID, stock allocation unknown |
| `display-production` | Tool reused for handling, deposition, patterning, joining and process support |
| `optical-metrology`, `electrical-instruments` | Tools reused for independent panel acceptance |

All eight selected requirements are preserved. `transistor-backplane` currently consumes `display-substrate`, `display-gate-source-driver-set` and `flexible-interconnect`, plus patterned materials/process tools and tests. This requires an explicit physical-intermediate ledger: the same substrate travels through backplane, OLED and barrier steps. It is not three independent sheets. Parent substrate/FPC entries may be repeated-use/containment references or extra stock; do not delete them before allocation, and retain their manufacturing reachability through the actual consumer.

Known operational requirements include clean dry protected handling surfaces/carriers; qualified incoming substrates, OLED chemicals and electrodes; fine pattern masks/alignment; deposition sources, thickness/process monitors, vacuum/gas/cooling and power; contamination cleaning stock, witness coupons, rejection/waste receivers; seal/barrier materials and curing tools for the selected encapsulation; connected driver and test-contact hardware; optical illumination/radiance and electrical/time references. Existing IDs in `display-production`, `display-oled-stack` and `transistor-backplane` cover much of this as unqualified groups. `display-process-test-coupons`, `backplane-test-structures`, `workshop-surfaces`, `containers`, `cleanroom`, `dryroom`, `regulated-power`, `process-control`, `bootstrap-computer`, `chemical-protection-equipment` and `chemical-effluent-equipment` remain relevant, with quantities and capacity unknown. Thickness-monitor and panel-specific luminance/color acceptance capabilities need explicit identity matching.

## Bounded making outline

Freeze the backplane technology, pixel circuit and electrical/material interfaces. Independently qualify the prepared glass and build its patterned transistor/interconnect stack. Check transistor/current uniformity and driver connections before consuming expensive emitters. Use a coherent OLED layer/electrode system with compatible work functions, deposition conditions and thermal limits. These parameters and accessible design information remain unresearched; generic oxide-TFT feedstock does not establish target current stability or pixel compensation.

Samsung explains that RGB organic materials can be vacuum evaporated through aligned fine metal masks. This supports explicit fine-mask fabrication, alignment and material/deposition obligations; it supplies no complete organic recipe, our pixel pitch, mask tension specification, thickness tolerance or acceptable yield. `mask-making` is a reuse candidate whose optical-reticle writing purpose may differ from producing a free-standing OLED fine metal mask. [Samsung fine metal masks](https://global.samsungdisplay.com/30929) [D1]

Encapsulate immediately in a supported clean/dry process, retaining the chosen layer sequence and compatible edge seal. Join and connect the panel's driver/interconnect structures, inspect physical/electrical interfaces, and protect/transport it to final optical bonding. Coating, deposition and encapsulation act on one intermediate; represent that state/sequence without inventing separately transferable completed films where the process actually deposits them.

## Encapsulation alternatives requiring a decision

**A: rigid glass lid and selected edge seal.** Samsung describes glass covering a rigid OLED and a glass-frit laser seal with supporting joining/curing steps. A proposal using that evidence needs a compatible lid, frit/seal stock, application and preconditioning, alignment/hold fixture, laser sealing and independent leak/lifetime verification. Existing `glass-stock`, `curing-joining`, `alignment-fixture` and `joining-and-curing-tools` are candidates; lid/frit/laser identities require capability matching. This inventory is nonselected. [Samsung rigid encapsulation](https://global.samsungdisplay.com/29626/) [D2]

**B: multilayer inorganic/organic barrier.** Current `display-encapsulation` selects `discovery-display-encapsulation-breadth03-v1`, consuming `display-barrier-film`, `display-barrier-polymer` and deposition/coating/gas/cleanroom/alignment/joining/assay/optical equipment. Samsung explains alternating layers for flexible OLED, including particle/pinhole management. That supports the barrier principle but does not demonstrate our selected rigid glass substrate, thermal/chemical compatibility or lifetime. Keep this as a distinct candidate pending evidence for the specific stack; do not infer that use of TFE on rigid glass is impossible. [Samsung thin-film encapsulation](https://global.samsungdisplay.com/29678?category=78&page=7&type=list) [D3]

No union of A and B is proposed as a single recipe. The selected route stays unchanged until the owner chooses/reviews a coherent method and preserves every necessary physical requirement.

## Acceptance, reuse and unresolved capability

Independently verify electrical addressing, pixel/brightness/color uniformity, defects, power and temperature, and barrier performance over the required environment/time. Current `optical-metrology` is microscope/length/light inspection; it cannot automatically measure calibrated radiance, spectral color or barrier lifetime. `thermal-radiance-reference`, `electrical-reference-instrument`, `clocks` and `time-comparison-reference` and `thermal-test` may contribute, but dedicated detector/spectral/stimulus fixtures and reference transfer remain unresolved. Count destructive/lifetime samples separately from the final panel.

Reuse canonical drivers, tools and facilities only after range, precision, cleanliness, scheduling and earlier availability review. Process/test programs are black boxes; their physical host, controller, loading and power must be available before fabrication. The final phone's later software installation cannot drive the evaporation plant. An LCD or coarse passive OLED is a separate architecture/tier with different materials, illumination or addressing obligations; it does not prove flagship equivalence.

**Next review:** freeze optical/electrical target, settle intermediate/substrate allocation, select encapsulation, separate reticle/FMM capabilities, specify calibrated panel tests and accessible design/process information. No complete inventory, qualified panel or raw-material closure is claimed.

