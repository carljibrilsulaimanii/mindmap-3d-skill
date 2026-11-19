---
name: mindmap-3d
description: Build an interactive 3D mind map (a glowing, dark "graph view" like Obsidian's) as a single self-contained HTML page or Claude artifact, from either a nodes-and-links JSON file or a plain indented outline. Use whenever the user asks for a 3D mind map, a graph view, a "2nd brain" map, an interactive site map, a process map they can rotate and click, a knowledge map, a network or relationship map, or to "show this as a 3D map / mind map / graph". Also use to turn an audit, crawl, sitemap, org chart, outline, notes or any list of things-and-connections into something people can explore, filter by status or group, search, and click for details. Not for flat 2D diagrams the user wants printed (use Mermaid or a static SVG for those).
metadata:
  version: 1.0.0
  released: 2026-11-19
---

# 3D Mind Map

**Version 1.0.0**, released 19 November 2026.

Builds one HTML page that shows a 3D force-directed map:

- dark background, glowing nodes, colored clusters, labelled hubs
- drag to rotate, scroll to zoom, fullscreen
- **color by status or by group**, with a legend that shows or hides each one
- **search** a node by name, URL or title
- **click to focus**: the camera flies to the node, everything unrelated dims, and a side panel
  shows the node's notes, link and every connected node (each one clickable)
- optional extra links (for example a site's menu links) behind a toggle so the map stays readable
- a fallback message when the browser has WebGL turned off

The page is self-contained: data is embedded, and the three libraries load from jsDelivr, which
Claude artifacts allow.

## When the input is…

| Input | Do |
|---|---|
| Things and the links between them (a crawl, an audit, a CRM export, a dependency list) | Write `graph.json` in the format below, then run `scripts/build_mindmap.py --data graph.json` |
| An outline, notes, or a topic the user describes in words | Write an indented Markdown outline, then run `scripts/build_mindmap.py --outline outline.md` |
| A request with no data yet | Ask what the map is of. Draft the outline from what they say and show it before building |

## Data format (`graph.json`)

```json
{
  "title": "Acme Site Map",
  "subtitle": "Checked Nov 19, 2026. Click a page to see its findings.",
  "statuses": {
    "ok":     ["#3ddc84", "Works"],
    "broken": ["#ff5252", "Broken"],
    "old":    ["#ffb020", "Outdated"],
    "hub":    ["#ffffff", "Group hub"]
  },
  "nodes": [
    {"id": "home", "label": "acme.com", "kind": "root", "group": "Website", "status": "hub"},
    {"id": "hub:Blog", "label": "Blog", "kind": "hub", "group": "Blog", "status": "hub"},
    {"id": "https://acme.com/pricing", "label": "/pricing", "group": "Website", "status": "broken",
     "url": "https://acme.com/pricing", "title": "Pricing", "notes": ["Buy button goes nowhere"]}
  ],
  "links": [
    {"source": "home", "target": "hub:Blog", "kind": "spine"},
    {"source": "home", "target": "https://acme.com/pricing", "kind": "link"}
  ]
}
```

- **Required on a node:** `id`, `label`. Everything else is optional.
- `kind`: `root` (the center; one per map), `hub` (a cluster center, always labelled), or anything
  else for ordinary nodes.
- `group`: the cluster. Each group gets its own color in "Color by group".
- `status`: a key from `statuses`. If you leave `statuses` out, the defaults above plus
  `ext: ["#4da3ff", "External"]` are used. Put the worst status on a node when several apply.
- `notes`: short plain-language lines shown in the side panel; put the most important first.
- **Link `kind`** sets how a link looks and how long it is:
  - `spine` is the root to a hub: long, bright and thicker.
  - `hub` is a hub to its members: short and faint.
  - `flow` is a step in a process: gold, with moving particles.
  - `good` is a step that ends well: green, with particles.
  - `bad` points to something broken: red.
  - `extra` links are hidden until the "More links" toggle is on. Use it for dense, repetitive
    links such as a menu that appears on every page.
  - Anything else is a plain faint link.

**Keep it one connected map.** Give every cluster a hub and link every hub to the root with a
`spine` link. Without this the clusters drift apart and the auto-fit zooms far out.

## Outline format (`--outline`)

```markdown
# Acme Site Map
- Website [hub]
  - Pricing page [broken] Buy button goes nowhere
  - About page [ok]
- Blog [hub]
  - 2024 launch post [old] Mentions a retired product
```

- The `# heading` becomes the root.
- Each top-level bullet becomes a hub.
- Indentation sets the parent.
- An optional `[status]` tag follows the label, and any text after the tag becomes a note.
- A `(https://...)` anywhere on the line becomes the node's link.

## Build

```bash
python scripts/build_mindmap.py --data graph.json --out my-map.html
python scripts/build_mindmap.py --outline outline.md --out my-map.html --title "My Map"
```

Options:
- `--title`, `--subtitle`: override the values in the data file.
- `--embed`: write only the map section, with no page wrapper, for pasting into a longer report.
  Give the container a height.

Then publish the HTML as an artifact, or open it locally.

## Library versions (do not change without testing)

| Library | Version | URL |
|---|---|---|
| three.js | 0.159.0 | `https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js` |
| three-spritetext | 1.8.2 | `https://cdn.jsdelivr.net/npm/three-spritetext@1.8.2/dist/three-spritetext.min.js` |
| 3d-force-graph | 1.73.4 | `https://cdn.jsdelivr.net/npm/3d-force-graph@1.73.4/dist/3d-force-graph.min.js` |

**Why these:** 3d-force-graph 1.80.x needs a newer three.js. With three.js 0.149 loaded globally it
throws `Timer is not a constructor` and draws nothing. three.js 0.159 is the last release with a
single-file `build/three.min.js`, and 3d-force-graph 1.73.4 accepts three >= 0.118. The custom
glow and labels need `THREE` as a global, so three.js must load first.

## Look and readability rules

- Dark background (`#05070a`), additive-blended glow sprites, a solid sphere at the center of each node.
- **Labels:** hubs and the root are always labelled. With "Labels" off, only the focused node is
  labelled, plus its neighbors when there are 25 or fewer; more than that buries the view.
- **Node size:** grows with the number of links, capped so hubs stay the biggest.
- **Focus:** the camera flies to about 230 units from the node; any closer fills the screen with glow.
- **Layout:** charge -34 with `distanceMax(260)`, and spine links at 120. Auto-fit runs once, when
  the layout settles (`onEngineStop`), not on a timer.
- **Legend:** keep it to about eight entries in status mode. Group mode can list more; it scrolls.

## Check before handing it over

1. **Build a local preview** that adds `[hidden]{display:none!important}`, which the artifact
   viewer normally supplies, so the WebGL fallback message stays hidden.
2. **Load the preview in a browser.** Confirm:
   - no console errors
   - the glow and the hub labels render
   - "Color by group" recolors the nodes
   - a legend click hides that status
   - search finds a node and opens the panel
3. **Check at phone width:** the title must not overlap the controls, and the panel sits at the
   bottom.
4. **Publish.** A Claude artifact runs inside a sandboxed frame, so page readers can't see in;
   judge it by screenshot.

## Files

- `assets/template.html`: the page, with `{{TITLE}}`, `{{SUBTITLE}}` and `{{GRAPH_DATA}}` placeholders.
- `scripts/build_mindmap.py`: builds a page from `graph.json` or an outline.
- `examples/site-map.json`, `examples/outline.md`: small working examples.
- `CHANGELOG.md`: what changed in each version.
