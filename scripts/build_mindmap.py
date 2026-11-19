r"""
build_mindmap.py - build an interactive 3D mind map page (mindmap-3d skill).
Author:  Jibril Sulaiman (with Claude Code)
Date:    2026-11-19
Lives:   .claude/skills/mindmap-3d/scripts/build_mindmap.py (run locally; output is published as an artifact)
What:    Fills assets/template.html with a graph. The graph comes from either
           --data graph.json   (nodes and links; see SKILL.md for the format), or
           --outline notes.md  (an indented Markdown outline: "# Root", top-level bullets become
                                hubs, nested bullets hang off their parent, optional [status] tag,
                                optional (https://...) link, text after the tag becomes a note).
         Validates the data (unique ids, links point at real nodes, one connected map) and warns
         about anything that would make the map hard to read.
Why:     Reusable builder for a glowing 3D "graph view", first made for a website sweep.
Usage:   python build_mindmap.py --data graph.json --out map.html [--title T] [--subtitle S] [--embed]
         python build_mindmap.py --outline outline.md --out map.html
"""
import argparse, html, json, re, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "template.html"
STATUS_TAG = re.compile(r"\[([a-zA-Z_-]+)\]")
LINK = re.compile(r"\((https?://[^)\s]+)\)")


def from_outline(text):
    """Turn an indented Markdown outline into graph data."""
    nodes, links, stack = [], [], []
    title, root = "Mind Map", None
    for raw in text.splitlines():
        if not raw.strip():
            continue
        if raw.lstrip().startswith("# ") and root is None:
            title = raw.lstrip()[2:].strip()
            root = {"id": "root", "label": title, "kind": "root", "group": title, "status": "hub"}
            nodes.append(root)
            continue
        m = re.match(r"^(\s*)[-*+]\s+(.*)$", raw)
        if not m:
            continue
        if root is None:
            root = {"id": "root", "label": title, "kind": "root", "group": title, "status": "hub"}
            nodes.append(root)
        depth = len(m.group(1).replace("\t", "  ")) // 2
        body = m.group(2).strip()
        url = (LINK.search(body) or [None, None])[1]
        body = LINK.sub("", body).strip()
        status, note = None, ""
        t = STATUS_TAG.search(body)
        if t:
            status = t.group(1).lower()
            note = body[t.end():].strip(" -:")
            body = body[:t.start()].strip()
        node = {"id": f"n{len(nodes)}", "label": body or "(untitled)", "notes": [note] if note else []}
        if url:
            node["url"] = url
        while stack and stack[-1][0] >= depth:
            stack.pop()
        if depth == 0:
            node.update({"kind": "hub", "group": node["label"], "status": "hub" if status in (None, "hub") else status})
            links.append({"source": "root", "target": node["id"], "kind": "spine"})
        else:
            parent = stack[-1][1]
            node.update({"group": parent["group"], "status": status or "ok"})
            links.append({"source": parent["id"], "target": node["id"], "kind": "hub" if parent.get("kind") == "hub" else "link"})
        nodes.append(node)
        stack.append((depth, node))
    return {"title": title, "nodes": nodes, "links": links}


def check(g):
    """Return a list of problems; raise on anything that would break the page."""
    ids = [n.get("id") for n in g.get("nodes", [])]
    if not ids:
        raise SystemExit("No nodes in the data.")
    if any(i in (None, "") for i in ids):
        raise SystemExit("Every node needs an id.")
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"Duplicate node ids: {sorted(dupes)[:10]}")
    idset = set(ids)
    bad = [l for l in g.get("links", []) if l.get("source") not in idset or l.get("target") not in idset]
    if bad:
        raise SystemExit(f"{len(bad)} links point at nodes that don't exist, e.g. {bad[0]}")
    warn = []
    for n in g["nodes"]:
        if not n.get("label"):
            n["label"] = str(n["id"])
    roots = [n for n in g["nodes"] if n.get("kind") == "root"]
    if len(roots) != 1:
        warn.append(f"{len(roots)} root nodes; one root keeps the map centered.")
    # connectivity
    adj = defaultdict(set)
    for l in g.get("links", []):
        if l.get("kind") == "extra":
            continue
        adj[l["source"]].add(l["target"]); adj[l["target"]].add(l["source"])
    start = roots[0]["id"] if roots else ids[0]
    seen, todo = {start}, [start]
    while todo:
        for x in adj[todo.pop()]:
            if x not in seen:
                seen.add(x); todo.append(x)
    loose = idset - seen
    if loose:
        warn.append(f"{len(loose)} nodes are not connected to the root (e.g. {sorted(loose)[:3]}); "
                    "link each cluster's hub to the root with a 'spine' link.")
    statuses = g.get("statuses")
    if statuses:
        unknown = {n.get("status") for n in g["nodes"]} - set(statuses) - {None}
        if unknown:
            warn.append(f"Statuses not defined in 'statuses': {sorted(unknown)}")
    if len(g["nodes"]) > 1500:
        warn.append(f"{len(g['nodes'])} nodes; above ~1,500 the map gets slow on phones.")
    return warn


def build(g, title, subtitle, embed):
    t = TEMPLATE.read_text(encoding="utf-8")
    data = json.dumps(g, ensure_ascii=False).replace("</", "<\\/")
    page = (t.replace("{{GRAPH_DATA}}", data)
             .replace("{{TITLE}}", html.escape(title))
             .replace("{{SUBTITLE}}", html.escape(subtitle)))
    if embed:
        style = page[page.index("<style>"):page.index("</style>") + 8]
        body = page[page.index("<!--MM-START-->"):page.index("<!--MM-END-->")]
        body = re.sub(r'<div class="mm-top">.*?</div>\s*', "", body, count=1, flags=re.S)
        body = body.replace('class="g-wrap"', 'class="g-wrap embed"', 1)
        return style + body
    return page


def main():
    ap = argparse.ArgumentParser(description="Build an interactive 3D mind map page.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--data", help="graph.json with nodes and links")
    src.add_argument("--outline", help="indented Markdown outline")
    ap.add_argument("--out", required=True, help="output .html file")
    ap.add_argument("--title")
    ap.add_argument("--subtitle")
    ap.add_argument("--embed", action="store_true", help="write only the map section, for a longer report")
    a = ap.parse_args()
    if a.data:
        g = json.loads(Path(a.data).read_text(encoding="utf-8"))
    else:
        g = from_outline(Path(a.outline).read_text(encoding="utf-8"))
    for w in check(g):
        print("warning:", w, file=sys.stderr)
    title = a.title or g.get("title") or "Mind Map"
    subtitle = a.subtitle or g.get("subtitle") or "Drag to rotate, scroll to zoom, click a node to see its details."
    out = build(g, title, subtitle, a.embed)
    Path(a.out).write_text(out, encoding="utf-8")
    print(f"wrote {a.out}: {len(g['nodes'])} nodes, {len(g['links'])} links")


if __name__ == "__main__":
    main()
