# Map UI refinements — 9 October 2026

These changes supersede the path enumeration and click behavior in the original UI worker handoff. The physical registry remains at revision 52, with no changes to discovery relationships. No agents were restarted.

## Link status dots

Status dots are larger (16px, 15px on small screens). Status text appears only when the dot is hovered or keyboard-focused. The accessible label remains available to screen readers. Physical link status continues to be generated from recorded research/review state.

## Routes covering every contributing item

Each physical item page also has a Used by section immediately above Paths from Smartphone. It lists every immediate parent in the selected physical graph, including parents outside the Smartphone root map, with links and status dots. Unselected candidate inventories are excluded. Empty parent lists are stated explicitly. The section updates through the same automatic build flow.

Paths from Smartphone now shows a collection of valid routes whose union contains every reachable ancestor of the current item, including Smartphone and the item itself. It does not enumerate repeated path combinations.

Start with the shortest route, then choose a route adding the most uncovered items, using dynamic programming on the DAG. Prefer shorter routes for ties. Remove routes made redundant by the remaining collection. This is a coverage heuristic, not a claim of a globally minimum route collection. All item coverage is preserved, and every adjacent pair is an actual selected physical dependency. Route pagination and jump controls remain.

The user's example is tested: ACDF and ABCEF cover every item in the four original paths ABCDF, ABCEF, ACDF and ACEF.

Live check: stone-occurrence-candidate has 4,456,293,876,583,490 original path combinations. Its collapsed tracker has 124 coverage routes containing all 516 contributing items. The local JavaScript check took about 85ms. Exact combination counts remain internal validation data and are no longer displayed in the tracker or map popup.

## Two level definitions

The map selector switches between Shallowest (shortest selected physical path from Smartphone) and Deepest (longest selected physical path from Smartphone). Smartphone is level zero; recipe records do not add levels. The same physical items and dependencies occur in both views. Items outside the root map have no level in either view.

At revision 52, the maximum shallowest level is 15 and the maximum deepest level is 79. Graph breadth coverage and discovery assignments still use shortest physical levels; changing the map view does not change scheduling or graph relationships.

## Grouping and concentric rows

Each level uses the full order of the preceding level. In rounds, each parent receives its first still-unassigned required child at the current level, in the page's declared requirement order. Shared children are assigned once. Repeat for the next remaining child of every parent, then flatten the parent groups in parent order for the following level.

The user's latest screenshot feedback supersedes both exact parent-ray anchoring and fixed angular sectors. Those sectors could squeeze a group into a long one-dot-wide column even with empty space nearby. Groups now share the entire available ring and can shift together sideways into that space.

The layout prefers the fewest rows that fit the entire ring. The user's subsequent instruction allows three or four rows when that full circle is too crowded for fewer; a narrow local parent region alone never triggers them. Four is the maximum. If even four cannot fit, the ring radius increases. Small groups return to fewer rows when capacity allows, and row spacing adapts to retain the minimum dot clearance. Circular group order is preserved; weighted interval packing keeps group centers as close to their parent directions as possible while maintaining separate group regions. Dense neighboring groups therefore spread side by side instead of becoming radial columns.

Dot-center spacing remains 14 layout units, with radius 6.25 at the same zoom: a 12.5-unit diameter and a small 1.5-unit gap. Intergroup padding remains 4, and interlevel padding remains 12. Frontier borders sit at the dot edge so they do not consume that small gap. Selection corner brackets remain independent.

Level one remains a ring around Smartphone, starting at the top. Its minimum layout radius decreased from 112 to 76; the reserved screen-space area still keeps it clear of Smartphone when zoomed out. Very small overview dots shrink with the layout; frontier outlines appear when zoom provides enough room.

Live revision-52 checks cover all 984 reachable items in both views without overlapping dots or group regions. The earlier fixed-sector method reached 12 rows in the shallowest view and 10 in the deepest. The temporary two-row cap reduced extents to about 1,054 and 2,098 layout units. The current full-circle capacity rule permits up to four, giving extents of about 952 and 2,097. Level 3 now uses four rows where its circle is packed. Every group with three or four rows has a recorded whole-ring capacity requirement above two; dot spacing remains at least 14.

Current evidence: proposals/2026-10-09-map-ui/four-row-layout.json. The earlier flexible-layout.json and flexible-layout-preview.png record the temporary two-row cap; that preview is explicitly a coordinate schematic, not browser output. Earlier sector/parent-aligned snapshots remain historical diagnostics.

The discovery and research prompts now require approximate page order: major Part, major Tool, minor Part, minor Tool. Existing order is assumed and improved when a page is next revised; no bulk physical-inventory rewrite was performed.

## Selection and connection layer

Expand map opens dist/map-view.html, a dedicated page using the full available width and a viewport-sized canvas. It retains the same depth, filtering, search, zoom, selection and faint-connection controls. Back to overview returns to the normal map page. The standalone edition includes the same expanded view at #map-view and restores normal page sizing when leaving it. Its accessible item list starts collapsed so the canvas has priority.

Hover shows details and relationships. Clicking a node pins that information and its relationships; a Go to page link opens the item. Click empty space, Close, or Escape to clear. Parent lines are orange; required-child lines are blue.

Selected nodes use purple corner brackets; hovered nodes use teal corners. The frontier state uses its own dark circular outline, which remains visible inside the brackets when a frontier is selected. Nonfrontier selections have no frontier circle. Selection markers render after the dots so nearby items cannot cover them. The legend and popup identify these states independently.

There are 6,145 distinct physical connections in the selected graph. Of those, 6,038 connect the 984 Smartphone-reachable items. The remaining 107 are outside the root map. These counts collapse making-recipe records and duplicate physical pairs; the validator separately audits 6,676 structural links including recipe records.

Show faint connections is optional and off by default. It draws all connections whose endpoints are visible in the current map filter, then overlays the highlighted parent/child relationships. At the overview scale, dense crossings can reduce readability; the switch allows direct comparison.

## Validation and saved code

54 tests pass, including the user's coverage example, exhaustive small-graph depth comparisons, exponential DAG coverage, matching Python/JavaScript algorithms, parent round-robin assignment, flexible group boundaries, sparse-group single-row preference, a crowded long-column regression, the four-row maximum driven only by full-ring capacity, nearby parent centering, larger dots with near-touching spacing, radial gaps, center clearance, independent frontier/selection markings, pinned popup/navigation link, line colors, connection toggle and view switching. Publication checks compare static and standalone graph payloads with the validated registry and retain the complete dependency-link audit.

Implementation: scripts/research_ui.py, scripts/assets/research-ui.js, scripts/assets/research-ui.css, with existing scripts/build_pages.py integration. The regular add/build flow regenerates both editions automatically. Direct file-URL browser inspection remains unavailable under the browser tool policy; controls and layouts were tested programmatically, without claiming an observed browser visual check.
