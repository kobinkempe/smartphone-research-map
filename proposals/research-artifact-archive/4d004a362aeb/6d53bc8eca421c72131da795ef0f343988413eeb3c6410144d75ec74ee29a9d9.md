# Enclosure

**Part · evidence research draft · closure open.** The enclosure locates and protects the phone's completed modules and establishes their mechanical and thermal interfaces. BFS item 2/5, level 1 after `handset`, scenario `coordinated-discovery-v1`, selected `discovery-enclosure-v1`, chosen revision 52 and scoped snapshot revision 53. This reviews the selected machined-aluminum hypothesis; it does not expand the mechanical lane's shared tools.

<details><summary>Required capability</summary>

One incorporated enclosure, plus trial/loss stock not yet specified. External dimensions, wall thickness, cavity datums, connector openings, flatness, surface finish, screw/bond interfaces, alloy/temper, stiffness, impact behavior, corrosion resistance, thermal contact, battery swelling clearance, antenna geometry and ingress performance are **not yet specified**. The handset's flagship-equivalent capability and real-network requirement are inherited. Enclosure RF interaction must be accepted in the assembled antenna geometry; a geometrically fitting metal box is insufficient.

</details>

## Immediate inventory and allocation

The selected seven requirements remain explicit.

| Existing canonical ID | Role and use |
|---|---|
| `aluminum-stock` | Part incorporated after removal of machining allowance; purity/alloy state unknown |
| `precision-machines` | Tool reused for stock sizing, cavities, datums and holes; motion precision and force unknown |
| `jigs-fixtures` | Tool reused for locating/supporting thin sections during each setup |
| `surface-cleaning` | Tool reused to prepare bonding/contact surfaces; actual wash chemistry and drying unknown |
| `seals` | Part incorporated; selected fiber-packing hypothesis is unqualified for phone ingress duty |
| `adhesives` | Part consumed/incorporated at chosen interfaces; cure and adhesion unqualified |
| `dimensional-metrology` | Tool reused for independent geometry acceptance |

At the consumer page, preserve known operation requirements carried by `precision-machines`: milling machine, compatible cutting-tool set and workholding, manual drive, flat reference/surface, independent dimensional references, suitable lubricant/water, ventilation, protection and containers. These are nested machine requirements, not extra enclosure feedstocks. For the actual machining job, tool wear, cutting-zone chip removal, cutting fluid or an explicitly researched dry-cut strategy, chip capture and cleaning stock must be allocated rather than assumed supplied by tool construction. `cutting-tool-set`, `water-supply`, `solvents-lubricant`, `containers`, `metalworking-waste-tray`, `metalworking-protection` and `workshop-surfaces` are reuse candidates; lubricant suitability is unknown. Dedicated duty quantities remain open.

If the chosen radio arrangement requires insulating windows or separated metal sections, incorporate compatible insulating material and joining interfaces. Check `polymers`, `molding-equipment` and the antenna owner before requesting an enclosure-insert identity; `connector-insulator` describes another consumer and is not automatically interchangeable. No insert is added as a mandatory fact before geometry selection. Fasteners joining frame subassemblies or cover seals need allocation to this route versus final assembly. Mechanical-load, joint-integrity, thermal and RF acceptance fixtures remain explicit unresolved capabilities, with `joint-pull-test-fixture`, `thermal-test`, `antenna-tuning` and `rf-test` as candidates.

## Bounded making outline

The following is a design inference pending a frozen drawing and machining trials. Choose a stock composition/temper capable of meeting strength, corrosion, machining and thermal demands. Existing `aluminum-stock` produces unspecified electrolytic/cast metal; it is not evidence for a chosen wrought alloy. A route through `alloy-stock`, forming or heat treatment may become necessary, but these alternatives must be separately evaluated before substituting stock.

Establish workpiece datums on a stable surface and independently inspect the blank. Cut/face it with compatible cutters, hold it against the expected forces, and machine cavities/openings while supporting thin walls. Preserve appropriate machining allowance between rough and finishing stages. Clear chips without scoring sealing surfaces; deburr edges and verify no sharp contact threatens cables or the battery. Clean, dry and protect the finished piece before joining. If inserts are chosen, prepare their material-specific contact geometry, install/bond or co-mold them, and recheck geometry after thermal processing. Install only the seals and adhesive interfaces assigned to this subassembly; final phone seals remain with their actual consumer.

Apple describes a cellular iPad enclosure containing plastic antenna splits, co-molded into machined aluminum and then finished by CNC machining. That is a primary-source precedent for metal/plastic RF integration, not evidence that this phone requires Apple's geometry, alloy, processing parameters or flatness specification. [Apple enclosure account](https://support.apple.com/en-us/101900) [E1]

Sandvik identifies rigid workholding, machine stability, short tooling and chip removal as milling considerations. Its guide concerns commercial tooling and damped assemblies, so it supports the obligation to handle machining forces/chips without qualifying our earlier manual machine or selecting a cutter. [Sandvik milling guide](https://www.sandvik.coromant.com/en-gb/milling-appl-guide) [E2]

## Acceptance, reuse and alternatives

Independently measure datums, interfaces and sealing surfaces against the actual drawing, accounting for gauge uncertainty. Check assembly fit, joint retention and damaging edges. Validate enclosure/antenna performance with completed radio fixtures and relevant mechanical/thermal loads. Anodizing or another coating is optional until corrosion, conductivity and surface demands are frozen; adding it entails its own chemical process, masking and waste requirements. No coating performance is assumed from a decorative appearance.

The existing machines, metrology and surfaces are preferred reuse candidates, but none has a qualified range, precision or build-order guarantee. A forged/cast near-net blank could reduce removed stock while adding forming/casting obligations. A polymer enclosure could simplify RF isolation but changes stiffness, heat transport, joining and polymer-manufacture burdens. These are coherent separate alternatives, not mixed inventories or proven shorter paths. The current metal hypothesis remains selected and open.

Manual drives avoid assuming imported CNC electronics, yet manual machining accuracy for this geometry is unproven. If automated machining is selected, declare its earlier physical controller, host, loading interface, power and black-box motion program. An enclosed loop involving `enclosures`, machines and metrology cannot be cured by renaming this handset enclosure.

**Next review:** freeze drawing/material, qualify stock and manual machine capability, allocate operation consumables and RF interfaces, and compare independent acceptance resources. No natural terminal or successful enclosure manufacture is claimed.
