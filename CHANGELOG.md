# Changelog

## 1.0.0 — 19 November 2026

First release. The skill was built from the interactive 3D site map made for a website sweep.

- Full-screen dark 3D force-directed map with glow sprites, labelled hubs and nodes sized by
  number of links.
- Color by status or by group, with a show/hide legend, search, click-to-focus side panel,
  "More links" toggle, fullscreen and phone layout.
- `scripts/build_mindmap.py`:
  - Builds from `graph.json` or from an indented Markdown outline.
  - Checks ids, links, connection to the root and status names.
  - `--embed` writes the map section only, for use inside a longer page.
- Pinned to three.js 0.159.0, three-spritetext 1.8.2 and 3d-force-graph 1.73.4. 3d-force-graph
  1.80.x fails with a global three.js 0.149 ("Timer is not a constructor").
- Examples: `examples/site-map.json`, `examples/outline.md`.
