# Public OLED organic stocks and candidate RGB recipe

This packet resolves a public chemical identity/preparation route for the p-injection and optical-cap stocks and specifies one normal-polarity RGB candidate using named public materials. It is a research proposal for independently reviewed stock and deposition work. **It does not qualify the finished display.** The adopted 2600-nit peak, 600-nit sustained/4-W, P3 coverage and direct 3000-hour LT95 requirements remain unchanged. No whole-panel lifetime is inferred from another endpoint, luminance, substrate, package or molecular substitution.

## Selected candidate and its evidence boundary

Choose a side-by-side, normal-polarity p–i–n candidate with a reflective Ag anode, MoO3 interface buffer, Spiro-TTB/F6-TCNNQ p transport, intrinsic color-specific emissive/blocking regions, Cs-doped electron transport, a semitransparent Ag cathode and an NPB cap. It fits the *polarity and lateral architecture* of the facilities LTPO/frit-lid proposal. Neither the all-TFE experimental package nor a three-terminal vertically stacked RGB pixel is incorporated into this choice.

The first source-supported blue reference is [Deng et al.2021](https://doi.org/10.1002/adom.202001642), including its complete Figure1 stack and MoO3-buffer experiment. Its red variant uses NPB/Ir(MDQ)2acac. The green emissive region comes from the same public Spiro-TTB/F6-TCNNQ p–i–n material family in [Murawski et al.2014](https://doi.org/10.1063/1.4896127). This is an **explicit engineered RGB candidate**: the green source is bottom-emitting, and converting its optical/contact geometry to the common top-emission stack is an unproved interaction that needs paired controls. It is not described as a source-demonstrated complete RGB handset stack. This is a materially compatible hypothesis because it retains the green source's NPB blocking, TCTA/TPBi host pair and emitter, and the shared p-injection chemistry; that hypothesis is rejected if its top-emission witness tests fail.

The public p-dopant and cap replace private NDP-series/CPL only as a new candidate architecture, with an explicit anode buffer and charge/optical requalification. They are not presumed equivalent to Jeon's private materials. MoO3 alone is not substituted for the whole molecular p-dopant: the Deng source found an important current/luminance penalty for that alternative.

## Molecular identity contract

The registry and canonical index were searched by molecular name, acronym, CAS and use at observed revision116. Existing `oled-hole-transport-feed`, `oled-electron-transport-feed`, `oled-emissive-host-feed`, and RGB emitter feed nodes are broad unexpanded functional assortments, not exact molecule identities. No existing exact record was found for the identities below. Exact named stocks can be reused in several functions; NPB host/blocking/cap roles do not require three molecular identities.

| Stock | Exact public identity | CAS | Candidate use |
|---|---|---|---|
| Spiro-TTB | 2,2',7,7'-tetrakis(di-p-tolylamino)-9,9'-spirobifluorene; C81H68N4 | 515834-67-0 | p-transport host |
| F6-TCNNQ / F6-TNAP | 2,2'-(perfluoronaphthalene-2,6-diylidene)dimalononitrile; C16F6N4 | 912482-15-6 | Molecular p-dopant |
| NPB / alpha-NPD | N,N'-bis(naphthalen-1-yl)-N,N'-bis(phenyl)benzidine; C44H32N2 | 123847-85-8 | Intrinsic blocking/red host and optical cap |
| MADN | 2-methyl-9,10-bis(naphthalen-2-yl)anthracene; C35H24 | 804560-00-7 | Blue host |
| TBPe | 2,5,8,11-tetra-tert-butylperylene | 80663-92-9 | Blue fluorescent emitter |
| BAlq | Bis(2-methyl-8-quinolinolato)(4-phenylphenolato)aluminium(III) | 146162-54-1 | Intrinsic hole-blocking region |
| BPhen | 4,7-diphenyl-1,10-phenanthroline; C24H16N2 | 1662-01-7 | Source-matched electron host |
| NBPhen | 2,9-bis(naphthalen-2-yl)-4,7-diphenyl-1,10-phenanthroline; C44H28N2 | 1174006-43-9 | Separately tested higher-Tg electron-host alternative; not AND with BPhen |
| TCTA | Tris(4-(9H-carbazol-9-yl)phenyl)amine | 139092-78-7 | First green host region |
| TPBi | 1,3,5-tris(1-phenyl-1H-benzimidazol-2-yl)benzene | 192198-85-9 | Second green host region |
| Ir(MDQ)2acac | Bis(2-methyldibenzo[f,h]quinoxalinato)(acetylacetonato)iridium(III), exact coordination form of the cited source | 536755-34-7 | Red phosphorescent emitter |
| Ir(ppy)2acac | Bis[2-(2-pyridinyl-N)phenyl-C](acetylacetonato)iridium(III); C27H23IrN2O2 | 337526-85-9 | Green phosphorescent emitter |

Manufacturer primary identity/grade checks include [Spiro-TTB](https://www.sigmaaldrich.com/BE/en/product/aldrich/923192), [F6-TCNNQ](https://tw.lumtec.com.tw/products-view.php?ID=10124), [NPB](https://www.lumtec.com.tw/products-view.php?ID=6577), [MADN](https://www.ossila.com/products/madn), [TBPe](https://www.ossila.com/products/tbpe), [BAlq](https://www.ossila.com/products/balq), [BPhen](https://www.ossila.com/products/bphen), [NBPhen](https://www.ossila.com/products/nbphen), and [Ir(ppy)2acac SDS](https://downloads.ossila.com/msds/irppy2acac.pdf). CAS/structural identity is not stock availability on untouched Earth. Each synthesis is a separate child; purchase is not a making method or external hardware allowance.

## One complete nominal deposition candidate

This is the first engineering witness recipe, with all colors patterned separately where required. Numbers in the table are nominal source-derived values or explicitly identified engineering selections. They are not an already optimized panel recipe; optical field/lid/polarizer verification may reject it and require a separately versioned design.

| From anode toward viewer | Blue region | Red region | Green region | Authority |
|---|---|---|---|---|
| Reflective anode | Ag80nm | Ag80nm | Ag80nm | Deng source; contact on LTPO/planarization still facilities duty |
| Anode buffer | MoO3 1nm | MoO3 1nm | MoO3 1nm | Deng tested buffer; green interface transfer is engineering choice |
| p transport | Spiro-TTB:F6-TCNNQ4wt%,150nm | Same nominal150nm | Same nominal150nm | Blue source second cavity; R/G optical thickness is initial engineering selection, not source optimization |
| Electron block | NPB10nm | NPB10nm | NPB10nm | Public family; green source region retained |
| Emission | MADN:TBPe1.5wt%,20nm | NPB:Ir(MDQ)2acac10wt%,20nm | TCTA:Ir(ppy)2acac8wt%,8nm, then TPBi:same emitter8wt%,12nm | Blue/red Deng; green Murawski. Dopant fractions use total deposited mixture mass basis |
| Hole block | BAlq10nm | BAlq10nm | BAlq10nm | Blue source; R/G combined top recipe is engineering candidate |
| Electron transport | BPhen:Cs3wt%,55nm | Same | Same | Source-matched blue p–i–n. Green source uses BPhen:Cs but thickness/contact conversion requires paired control |
| Cathode | Ag20nm | Ag20nm | Ag20nm | Deng semitransparent cathode; no opaque Al cathode included |
| Cap | NPB40nm | NPB40nm | NPB40nm | Deng cap; full RGB optical/lid/polarizer response remains measurement duty |

Ag, MoO3 and Cs are actual separately prepared deposition source stocks. Cesium carbonate is **not** silently substituted for pure Cs. Reflective Ag/MoO3 differs from the currently proposed Ag/ITO contact charge; the facilities owner must choose/update that interface before physical integration. The initial BPhen branch is selected for source continuity, but its reported Tg≈63°C imposes an actual junction/sealing thermal problem. The NBPhen branch from Deng is a separately versioned alternative with different current/luminance behavior and cannot inherit BPhen performance or green compatibility automatically.

The fabrication apparatus contract keeps source-specific heating/crucibles/liners/shutters, separate co-evaporation rate sensing and independent deposited composition/thickness checks, compatible vacuum and dry nitrogen transfer, installed RGB/common masks, protected mask exchange/cleaning/replenishment, independent spectra/electrical/thermal/life apparatus, handling/protection and verified waste. Source experiment vacuum was≈10^-7mbar; that is a candidate process demand, not a delivered vacuum system or a calibrated instrument. QCM rates alone do not certify dopant mass fraction.

## Stock preparation and quantity contract

First complete own-stock batch covers three public p-injection/cap molecules: **1.000g Spiro-TTB,0.100g F6-TCNNQ,1.000g NPB**, each separately contained and sampled. These are adopted workshop lot sizes, not measured film mass, yield or OEM requirements. They provide a physically concrete first feed lot plus independent assay/witness material. A lot is replenished before accepting additional deposition demand; no fixed purification/source utilization is asserted.

For any attempted panel, incorporated film mass is `sum(area_region × measured_film_density × thickness × deposited_mass_fraction)`. At full active area65.993×142.985mm, a1nm film occupies9.436mm^3×10^-3, and mass is that volume times its independently measured density. Mask/source/chamber residue, reservoir minimum charge, characterization samples, rejected panels and replacement stock are measured separately. Parent stock demand must be frozen after optical/aperture/source-transfer commissioning; stock-node batch output quantity can be fixed before that eventual panel-loss ledger is known.

Choose **separate vacuum gradient sublimation**, not one mixed distillation or a bought branded material. Receive chemically defined crude synthesized powders; identify them before heating. Place each into its dedicated compatible charge/tube/collection path, establish a thermal gradient under monitored vacuum, collect a central fraction, keep head/tail/residue separately, assay, and repeat or reject until the output meets the lot contract. Protected dry transfer seals each batch into a separate identified low-contamination vial. Do not combine compounds before co-evaporation, assume they sublime congruently as a premix, or reuse contaminated tubes without blank acceptance. Murawski's source explicitly further purified organic materials by vacuum gradient sublimation.

The source/collection temperatures are determined per compound from actual TGA/DSC and recovery/decomposition checks; one invented universal oven temperature is not supplied. The apparatus must cover the characterized transport window, stable independent control/temperature references and compatible vacuum recovery. A complete purification profile is released only after identity/assay before and after transport agree and the specified amount is recovered. That commissioning is stock-process acceptance, not a hidden commercial factory.

Initial adopted own-stock limits: Spiro-TTB≥99.0%HPLC and NPB≥99.9%HPLC, consistent with public supplier grade definitions; F6-TCNNQ>98%elemental-analysis basis as the source grade, supplemented by orthogonal structural identity and active-content uncertainty. HPLC area, elemental analysis and absolute active mass are **not interchangeable purity definitions**. Co-evaporation and film-composition accounting carry the measured assay/response-factor uncertainty. Source grade only establishes a known starting contract; final caller contamination/aging compatibility is accepted by separate deposited controls, not guaranteed by a percent label.

## Independent stock and deposition acceptance

1. Identify positional/coordination identity using independent calibrated spectroscopic methods: NMR and mass spectrometry for the proton-bearing molecules;19F-NMR pattern, elemental analysis and mass spectrometry for F6-TCNNQ. Independent references, analysis reagents/vessels/sample handling and method blanks remain physical requirements. Distinguish isomers and degradation products; CAS label alone is insufficient.
2. Apply the stated purity basis with a validated chromatographic/elemental method and report calibration, response factors, recovery, limits and uncertainty. Weigh the separately recovered accepted batch against independent mass artifacts. Keep the retained reference sample and rejected fractions distinct; output cannot certify its own analytical references.
3. Deposit isolated neat and4wt%Spiro-TTB:F6-TCNNQ witness films using independently verified thickness/composition. Compare identity before/after thermal transport. Demonstrate actual p-type charge transfer and conductivity on a known geometry. Murawski measured about1.3×10^-4S/cm for4wt%Spiro-TTB; this is a comparator datum, not a guaranteed batch value or a fresh arbitrary threshold. A conductivity acceptance floor must be derived from the facilities owner's maximum current/HTL voltage-drop allocation before final caller fit is certified.
4. Deposit NPB cap witnesses and measure spectral n/k, absorption, roughness/film stability and the actual Ag/cap interface. The source's NPB40nm is the candidate, not a proof that private CPL70nm can be renamed. The panel owner must bind its required spectrum/angular/cavity tolerances and thermal exposure to the stock/deposition test; that remaining caller allocation prevents final-grade certification now.
5. Challenge the actual Ag/MoO3/p-layer interface and measured thermal history. Keep buffered/unbuffered controls separate; don't apply the paper's80°CALD aging schedule as the laser-frit process. Actual active-area and lead-crossing heat remains a facilities interface.

## What still blocks full display compatibility

**C01:** The selected current public RGB candidate lacks a paired measured/modelled full-area RGB cavity with lid/polarizer, qualified R/G top conversion and source-current/thermal/rail allocation. Blue/red recipes and common material-family evidence justify experiments; they do not prove P3≥95%,600nit/4W or2600nit/8W. These are interaction decisions, not unidentified molecules or unmade synthesis children.

**C02:** Required stock/deposition conductivity, cap optical tolerances and actual contamination budget must be bound to that paired design. They are caller-facing necessary properties; no complete-reviewed stock flag is requested while those allocations remain unresolved. The three molecular identity/preparation/batch contracts can be reviewed at their exact draft scope now.

**C03:** Direct project LT95 remains a whole-panel test of dedicated packages at200nitD65/60Hz/25°C for3000h. Deng'sLT65, Jeon'sLT50/conversions and high-current VLC minutes are not substitutions. A public material kit plus complete measurement protocol cannot be described as a passed lifetime demonstration. No lifetime acceleration factor is adopted.

The graded-ZADN SEL patent is preserved as another real high-life branch, but its red/p-injection tradecodes remain unidentified. The publicly explicit vertically stacked RGB branch changes drive/TFT geometry and has a separate power limitation. Neither is silently mixed into this nominal candidate. All inherited flagship requirements remain in the facilities parent report; further own-stock review and parent interaction work remain active.
