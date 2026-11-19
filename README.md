# 3D Mind Map skill for Claude

A Claude Code skill that builds an interactive 3D mind map: a dark, glowing "graph view" you can
rotate, zoom, search, filter and click. The output is one self-contained HTML page that works as a
Claude artifact or opens straight in a browser.

Give it either:
- a **nodes-and-links JSON file**, such as a website crawl, an audit, a process or an org chart, or
- a plain **indented outline**, such as notes, a plan or a topic.

## What you get

- Colored clusters around labelled hubs, with nodes sized by how connected they are.
- **Color by status or by group.** Click a legend entry to show or hide that status or group.
- **Search** by name, URL or title.
- **Click to focus.** The camera flies to the node, everything unrelated dims, and a side panel
  shows its notes, its link and every connected node.
- Process links can show moving particles: gold for a step, green for a good outcome, red for a
  broken one.
- An optional "More links" toggle for dense, repetitive links.
- Fullscreen, a phone layout, and a fallback message when WebGL is off.

## Install

Copy the `mindmap-3d` folder into your skills directory:

- Claude Code, one project: `<project>/.claude/skills/mindmap-3d`
- Claude Code, all projects: `~/.claude/skills/mindmap-3d`

Then ask Claude for "a 3D mind map of …", "a graph view of my notes", or "show this crawl as an
interactive map".

## Use the script directly

```bash
python scripts/build_mindmap.py --outline examples/outline.md --out map.html
python scripts/build_mindmap.py --data examples/site-map.json --out map.html --title "My Site"
python scripts/build_mindmap.py --data graph.json --out section.html --embed   # map only, for a longer page
```

The script checks the data before building:
- It stops with an error on duplicate ids or links to nodes that don't exist.
- It warns when part of the map isn't connected to the root, or a status isn't defined.

## Data format

See [SKILL.md](SKILL.md) for the full `graph.json` and outline formats, the link kinds and the
readability rules.

## Libraries

These load from jsDelivr at pinned versions: three.js 0.159.0, three-spritetext 1.8.2 and
3d-force-graph 1.73.4. Newer 3d-force-graph releases (1.80+) need a newer three.js and fail with
this setup. See SKILL.md before changing versions.

## License

MIT
