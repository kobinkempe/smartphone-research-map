# Touch panel

**Part · evidence research draft · closure open.** This level1 assembly translates finger contacts into electrical position signals for the handset. It is section03 item1/5, following the first five completed root reports. Order was chosen from revision90; exact current records are in `base-snapshot.json`. Scenario `coordinated-discovery-v1`, selected `discovery-touch-panel-v1`. No discovery ownership or live route changes are made here.

<details><summary>Required capability</summary>

One accepted incorporated touch assembly plus trial/coupon/loss stock, quantities unknown. Active area, simultaneous contacts, spatial error, latency, scan rate, cover/bond thickness, electrode resistance/transmission, controller noise/range, host interface, power, temperature and wet/glove/charger-noise behavior are **not yet specified**. Compatible flagship-equivalent use is inherited. Freeze the physical stack and controller interface before adopting any sensor layout. Capacitive measurement, position decoding and tuning are black-box software functions, not software-making dependencies.

</details>

## All selected immediate requirements

| Canonical ID | Role/use |
|---|---|
| `touch-electrodes` | Part incorporated patterned transparent sensing conductors |
| `touch-controller` | Part incorporated compatible drive/sense/processing hardware |
| `optical-bonding-layers` | Part incorporated adhesive/bond interface, with dispense/trim losses |
| `display-substrate` | Part incorporated supporting optical sheet; allocation with electrode processing unknown |
| `flexible-interconnect` | Part incorporated sensor/controller/host connection |
| `touch-production` | Tool reused for patterning, layer handling and lamination |
| `electrical-instruments`, `optical-metrology` | Tools reused for independent acceptance; actual property coverage unqualified |

All eight selected obligations are preserved. `touch-production` already exposes holder/lamination stage, deposition, lithography, etching, masks, presses/dispensers, vacuum, test coupons, impedance measurement, power/control/cable, cleanroom, cleaning and chemical protection/effluent. They are transitive declared requirements, not missing factories. Their construction stock does not automatically supply production's electrode feed, masks, clean wipes/rinse, adhesive charge, liners and rejected assemblies. Allocate clean work surfaces, protected carriers/storage, handling, test contacts and waste capture to the actual operation.

`touch-electrodes` consumes transparent conductor and patterning tools but does not name its supporting substrate. The parent also lists a completed electrode item and `display-substrate`. Resolve whether electrodes mean a layer patterned onto this sheet, a transferable film, or a completed sensor sheet. Preserve crossing insulation/bridges if the chosen X/Y layout needs them; do not invent a mandatory extra dielectric for every architecture. Existing `backplane-dielectric-stock`, substrate/conductor and flex identities are reuse candidates requiring chemistry/optical/process matching, not interchangeable by name.

## Bounded making method

Choose one capacitive arrangement and a compatible controller. Establish layer ownership across cover glass, sensor substrate and display: a separate laminated sensor and an integrated sensor-on-cover/display have different inventories. Prepare the actual sheet, clean it, deposit/pattern the chosen conductors with coherent routing and isolation, and verify resistance/continuity and optical defects. Transfer or laminate only layers that physically exist in the chosen method. Connect the sensor and controller through the qualified flex/contact interfaces; retain hardware protection and supply decoupling within the actual controller board/module consumer.

Microchip AN2934 describes self/mutual capacitance, cover effects, shielding and surface layouts with routing/crossovers. It supports the need to match geometry, dielectric stack and acquisition electronics. Its button/slider/surface examples are not evidence of a flagship phone's multi-touch accuracy or a transferable production pitch. [Microchip sensor design guide](https://www.microchip.com/content/dam/mchp/documents/TXFG/ApplicationNotes/ApplicationNotes/Capacitive-Touch-Sensor-Design-Guide-DS00002934-B.pdf) [T1]

Select one bond chemistry. Place clean layers against the appropriate carrier/lamination controls, establish the bond line, remove trapped defects by a supported process, and preserve cleanliness during curing or pressure bonding. 3M documents an ITO-compatible free-film adhesive for glass-to-sensor bonding that requires no UV cure. This is a concrete alternative to a liquid curing adhesive, not the project's selected chemistry or a natural supply. Do not combine its no-cure method with mandatory UV steps from another adhesive. [3M adhesive example](https://www.3m.com/3M/en_US/p/d/b5005356007/) [T2]

## Acceptance, reuse and alternatives

Check finished stack geometry, bond voids/haze/transmission, conductor integrity, insulation, controller timing/noise and touch response over the actual mounted display/enclosure/power condition. `touch-electrode-simulator` supports controller characterization as an unqualified existing frontier; it does not alone simulate real fingers, cover mechanics, moisture or complete handset interference. Physical stimulus/position fixtures, reference contacts, environmental samples and host readout need range/uncertainty and quantity allocation. Do not accept the controller solely using its own decoded coordinates.

Current `touch-controller` construction includes physical chip packaging, simulator/references, programmer/loading contacts/cable, earlier workshop host, power and environment. These obligations already exist transitively. Programs needed for production/test must be available earlier on those physical hosts; final handset software may be installed after import. A schematic/interface definition is not available controller stock.

A coarser self-capacitance control can test earlier acquisition but cannot silently satisfy unfrozen multi-touch phone demands. Separate sensor glass versus sensor-on-cover, alternative transparent conductors and liquid versus film bonding remain coherent candidate routes requiring distinct compatibility evidence. Reuse existing layer/tool identities when their states and capabilities match; no new identity is requested in this report.

## Exact discovery feedback

- **Declared-inventory fact:** parent/electrode records leave the supporting workpiece state and consumption allocation unclear; fix a state ledger before moving edges.
- **Method-supported obligation:** a chosen crossing X/Y layout needs its actual routing/isolation; the lamination operation needs real installed carriers, bond stock and test contacts. Existing tool construction does not allocate job quantities.
- **Unresolved decision/suitability:** shielding, glove/wet performance, integrated stack, controller range and physical position test thresholds remain target-dependent. These are not confirmed universally absent parts.

Next: freeze stack/layout/controller demand, assign operational stock and independent full-panel acceptance, and review earlier capability availability. No complete inventory, endpoint or accepted physical touch panel is claimed.
