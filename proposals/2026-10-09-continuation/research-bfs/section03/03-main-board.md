# Main board

**Part · evidence research draft · closure open.** The main board is a populated interconnected electronic assembly, not a bare patterned board or an inventory of loose chips. Section03 item3/5, level1, selected `discovery-main-board-v1`, scenario `coordinated-discovery-v1`; exact captured records are in `base-snapshot.json`. Current hierarchy already includes active packaged devices. This research preserves that correction and identifies remaining operation/allocation demands.

<details><summary>Required capability</summary>

One incorporated accepted board plus coupons, component losses and rework/trial stock, amounts unknown. Dimensions, layer count, trace/via geometry, impedance, package types/pitches, netlist, power rails/sequencing, decoupling, signal integrity, grounding/shielding, thermal contacts, moisture condition and joint-reliability requirements are **not yet specified**. Compatible compute, storage, radio and peripheral functions must meet the frozen handset target. Public package guidelines do not provide an accessible flagship chipset design or board schematic.

</details>

## All selected immediate inventory

| Canonical IDs | Role/use |
|---|---|
| `pcb-patterned-substrate` | Part incorporated completed patterned substrate with matched pads/interfaces |
| `board-passives` | Part incorporated actual compatible passive set |
| `processor`, `memory`, `storage`, `power-management` | Parts incorporated accepted packaged active devices |
| `modem-baseband`, `rf-front-end`, `audio-codec`, `usb-controller` | Parts incorporated accepted compatible active assemblies/devices |
| `solder-alloy-stock`, `solder-flux` | Parts consumed/incorporated by selected joining process; physical paste state needs allocation |
| `component-placement-system`, `stencil-printer`, `reflow-oven`, `assembly-fixtures` | Tools reused for paste application, placement, thermal joining and workholding |
| `optical-inspection-instruments`, `electrical-inspection-instruments`, `electrostatic-protection` | Tools reused for acceptance/handling; range and hidden-joint coverage unqualified |

All19 immediate obligations are retained. `stencil-printer` transitively includes `solder-stencil`, squeegee and `solder-paste-stock`. Printer manufacture/commissioning stock is not automatically the paste charge for each populated board. Parent alloy/flux may be precursor stocks for making paste, but must not be counted as simultaneous separate joining methods without allocation. Use one prepared paste formulation/state and keep its manufacture reachable; manual solder/ball placement is a distinct alternative.

Allocate installed apertured stencil matched to the board, release/cleaning stock, package trays/holders, paste storage/handling, stable surfaces, nozzle/tweezer contacts, board support, thermal profiling witness stock/sensors, rejected components and flux/cleaning waste. Existing canonical stencil, paste, containers, surfaces, cleaning, temperature and waste identities should be matched before new designs are requested. Their presence in nested tool routes is not a guarantee of a replenished production job.

Processor/memory/storage and radio devices already belong to this populated-board route. `audio-codec` is also an audio-system requirement; allocation must say whether one mounted codec serves both functions, or distinct stock is intended. Connector/flex, charging/protection, clock/reset, shield and thermal-pad placement remain design-specific interface questions, not confirmed missing chips. Check actual peripheral routes before duplicating them into this board.

## Bounded making outline

Freeze a compatible schematic/netlist and package/board interfaces using actual chip specifications. Accept bare substrate geometry, cleanliness, insulation, continuity and required interconnect performance. Establish package moisture/storage condition and actual solder-land compatibility. Apply one prepared paste with the installed stencil/squeegee against qualified board supports, inspect the deposit, and place packages/passives with supported orientation/alignment. Preserve the part map and sufficient stock for trial/rework; definitions in the registry are not fabricated packages.

Develop and independently measure a thermal joining profile for the chosen board, package and solder system, then inspect/clean according to actual residue compatibility. TI's QFN/SON guidance distinguishes paste quality/storage, clean lands, stencil design, placement, board-specific reflow and inspection. It supports these obligations for that package family; its example geometry/temperatures are not adopted for every processor or this handset. [TI QFN/SON attachment](https://www.ti.com/lit/an/slua271a/slua271a.pdf) [M1]

Check board shape and joining damage before power. Use an independently qualified earlier source, protection and physical contacts to verify rails, shorts/isolation and board-level functions in staged conditions. Return failed boards to a defined rework route with cleaning/removal/replacement stock rather than claiming rework supplies its own first tools.

## Inspection and earlier physical availability

Surface imaging cannot directly reveal every joint beneath a selected BGA. TI's flip-chip BGA guide discusses X-ray, optical and complementary analysis techniques. This supports a package-specific hidden-joint acceptance decision; it does not prove every board needs every inspection modality or that our X-ray apparatus meets the necessary resolution/contrast. [TI flip-chip BGA guide](https://www.ti.com/lit/ug/spru811a/spru811a.pdf) [M2]

`hidden-joint-x-ray-inspection-equipment` already occurs at handset level. Resolve whether its inspection accepts the populated board before incorporation, and preserve the actual fixture/independent artifact/exposure/readout requirements through that consumer. Electrical continuity/function may complement inspection, but cannot silently establish reliability, void criteria or interface performance absent evidence. Full target acceptance thresholds and sampling remain unknown.

Existing placement/reflow/control/test hosts remain unqualified for the chosen pitch/profile/bandwidth. Manufacturing and diagnostic programs are black boxes requiring earlier physical host, memory, programmer, cables and workshop power before assembly/test. Final software may be installed after import; it cannot supply the earlier control plant. The main board cannot certify its own first bench instrument.

## Alternatives, reuse and exact feedback

For one board, manual assisted placement is an earlier candidate already represented; accuracy/capacity must still match packages. Larger-pitch devices or leaded prototypes can commission equipment but are separate tiers with different compute/size/power capability. Integrated SoC functions versus separate devices require different quantity and interface allocation, not a union of both chip sets. No route is proven shortest or flagship-equivalent.

- **Declared-inventory fact:** active chips are already incorporated in the parent; avoid repeating the former flattening error. Paste/stencil are transitive, while production stock and codec/inspection consumer allocation remain unresolved.
- **Method-supported obligation:** selected package/paste joining needs actual land/deposit/profile and suitable inspection; a tool-making apparatus is not its installed stencil or per-board paste charge.
- **Unresolved decision/suitability:** exact chipset, netlist, pitch, shielding, charging/clock/peripheral placement and joint criteria require target/design selection. No universal new chip or X-ray resolution is inferred.

Next: freeze interfaces/packages, allocate paste/job stock and audio/inspection placement, qualify profile/contacts and independent tests. No complete recipe, natural endpoint or accepted populated board is claimed.
