# Map relationship controls — 11 October 2026

The overview, expanded map and standalone edition share these controls:

- Relationships: whole map, ancestors and descendants, only descendants, or only ancestors. Per the final 12 October instruction, direction and relationship depth affect connections only; all nodes and the linked item list stay visible under the existing search and item filters. With no current selection, choosing a directional view starts at the map's center object. Optional faint connections also follow the directional setting.
- Relationship levels: 1 through 10, or all levels. Distances count physical dependency edges from the focused object, independently in each direction. Two descendant levels include children and grandchildren, even when shared items appear at another Smartphone level. Ancestor traversal does not include siblings.
- The final visibility correction tapers paths from 2.5 CSS pixels at level 1 to 1.75 at level 2 and 1 at level 3. All deeper paths stay at 1 pixel with the same 25% opacity, preventing continued thinning from looking like continued fading. Faint background connections use the same taper with their destination's displayed level. Paths are grouped by color, width and opacity for efficient canvas drawing. The regression fixture draws levels 3 through 10 in one group at identical width and opacity.
- The final 12 October follow-up sets path opacity to 100% at relationship level 1, 50% at level 2, and 25% at every later level. Dot, text and selection opacity stays at 100%.
- The pinned info box includes “Making tree for this object”. It centers that object at level zero, includes only its transitive requirements, recomputes shallowest and deepest levels, and opens all descendant levels. Shared requirements appear once. “Back to Smartphone map” restores the original view.
- The linked item list uses the same filters and includes Select and Making tree buttons for keyboard navigation. Objects outside the Smartphone map can open their own making trees.

The physical registry is unchanged. Generated pages were rebuilt at revision 125. Implementation lives in scripts/research_ui.py and scripts/assets/research-ui.js/css; generated HTML was produced through scripts/build_pages.py.

Validation: 15 UI/layout/route tests, 21 graph-gate tests, 4 publication tests and 17 research-publication tests passed. Windows transaction tests used workspace-local temporary files. The full publication audit checked 1,498 static pages, 1,498 standalone views, 51,604 local links and 10,445 dependency edges. Browser checks exercised two-level descendants and the info-box making-tree action on Stone hand tools, including its shared raw-material requirement.

Final browser checks also exercised two-level ancestors. The original making-tree screenshot is saved as docs/map-controls-preview.png. On 12 October the user explicitly approved publication to the existing private Site, with the path-opacity changes applied first. Site identity and audience remain declared in .openai/hosting.json and the existing Sites access policy.

Hosted packaging uses out/ because the offline HTML exceeds Sites' 25 MiB per-file limit. That directory contains byte-identical audited static pages and assets, with the standalone download supplied as an exact ZIP copy. The download link changes to the ZIP; dist/ retains the original standalone HTML. The publication audit checks both output sets, the extracted ZIP bytes and the hosting file-size limit before publication.
