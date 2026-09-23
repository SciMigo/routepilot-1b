#!/usr/bin/env python3
"""Build the published reading and lab pages from their Markdown sources.

Usage: python tools/build_pages.py [--check]

    reading/NN-slug.md               -> reading/NN-slug.html
    modules/NN-slug/lab.md           -> reading/lab-NN-slug.html

A reading may start with a header block whose `sources` list names entries in
reading/_sources/manifest.json; they are rendered as a sources footer. Lab pages
tell the learner to clone this repository, because every lab runs the benchmark
package locally. `--check` exits non-zero if any committed page is stale.
Install the pinned build dependencies with `pip install -r requirements-build.txt`.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

try:
    import markdown  # type: ignore
    from markdown.extensions.codehilite import CodeHiliteExtension  # type: ignore
except ImportError:  # pragma: no cover
    sys.exit("pip install -r requirements-build.txt")

ROOT = Path(__file__).resolve().parents[1]
READING = ROOT / "reading"
MODULES = ROOT / "modules"
TEMPLATE = READING / "_template.html"
MANIFEST = READING / "_sources" / "manifest.json"
REPO_URL = "https://github.com/SciMigo/routepilot-1b"
COURSE_URL = "https://scimigo.com/en/learn/routepilot-1b"

HEADER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
HEADING_RE = re.compile(r'<h2 id="([^"]+)">(.*?)</h2>', re.S)
H1_RE = re.compile(r"^# (.+)$", re.M)


def parse_header(text: str) -> tuple[dict, str]:
    """Read `key: value` lines and `key:` followed by `  - item` lists."""
    m = HEADER_RE.match(text)
    if not m:
        return {}, text
    meta: dict = {}
    key = None
    for line in m.group(1).splitlines():
        item = re.match(r"^\s+-\s+(.+)$", line)
        if item and key:
            meta.setdefault(key, []).append(item.group(1).strip().strip("'\""))
            continue
        if ":" in line:
            key, value = (s.strip() for s in line.split(":", 1))
            if value:
                meta[key] = value.strip("'\"")
    return meta, text[m.end():]


def sources_footer(meta: dict, manifest: dict) -> str:
    keys = meta.get("sources") or []
    if not keys:
        return ""
    items = []
    for key in keys:
        if key not in manifest:
            raise KeyError(f"source {key!r} is not in {MANIFEST.relative_to(ROOT)}")
        s = manifest[key]
        # Pages sit in a cross-origin iframe; open external links at the top level.
        items.append(
            f'<li><a href="{html.escape(s["url"], quote=True)}" target="_blank" '
            f'rel="noopener noreferrer">{html.escape(s["title"])}</a> — '
            f'{html.escape(s["publisher"])}, fetched {html.escape(s["fetched"])}</li>'
        )
    return (
        '<section class="attribution"><h2>Sources</h2>'
        "<p>Product claims on this page are paraphrased from the sources below and may "
        "have changed since they were fetched. Named products are trademarks of their "
        "owners; this independent course is not endorsed by them.</p><ul>"
        + "".join(items)
        + "</ul></section>"
    )


def page_start(rendered: str, lab_url: str = "") -> str:
    """A compact outline, plus a lab route on module readings."""
    links = []
    for anchor, label in HEADING_RE.findall(rendered):
        plain = html.unescape(re.sub(r"<[^>]+>", "", label))
        links.append(f'<a href="#{html.escape(anchor, quote=True)}">{html.escape(plain)}</a>')
    outline = ('<details class="reading-outline"><summary>On this page</summary>'
               '<nav aria-label="Sections">' + "".join(links) + "</nav></details>")
    lab = (f'<a class="reading-lab-link" href="{html.escape(lab_url, quote=True)}" '
           'target="_blank" rel="noopener">Open the lab ↗</a>') if lab_url else ""
    return '<div class="reading-start">' + outline + lab + "</div>"


def lab_setup(module_id: str) -> str:
    source = f"{REPO_URL}/blob/main/modules/{module_id}/lab.md"
    return (
        '<div class="admonition" id="lab-setup"><p class="admonition-title">Before you start</p>'
        "<p>Every lab runs the course benchmark on your own machine. It needs Python 3.11 "
        "or newer and nothing else: the package has no third-party dependencies.</p>"
        f'<pre><code>git clone {REPO_URL}.git\ncd routepilot-1b\n'
        "python3 -m unittest discover -s benchmark/tests</code></pre>"
        "<p>Run every command below from the repository root. The same instructions are "
        f'in the repository at <a href="{source}" target="_blank" rel="noopener noreferrer">'
        f"modules/{module_id}/lab.md</a>.</p></div>"
    )


def strip_h1(text: str) -> str:
    """The template prints the title as the page's h1; drop the source's copy."""
    return H1_RE.sub("", text, count=1)


def render(md: markdown.Markdown, text: str) -> str:
    md.reset()
    return md.convert(text)


def pages() -> dict[Path, str]:
    template = TEMPLATE.read_text(encoding="utf-8")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    # codehilite highlights with Pygments at build time, so each page is
    # self-contained and its colours follow the template's light/dark tokens.
    md = markdown.Markdown(extensions=[
        "fenced_code", "tables", "toc", "attr_list", "admonition",
        CodeHiliteExtension(css_class="codehilite", guess_lang=False, noclasses=False),
    ])
    out: dict[Path, str] = {}

    def fill(title: str, body: str, footer: str = "") -> str:
        return (template.replace("{{title}}", html.escape(title))
                .replace("{{body}}", body)
                .replace("{{attribution}}", footer))

    for src in sorted(READING.glob("*.md")):
        if src.name.startswith("_"):
            continue
        meta, text = parse_header(src.read_text(encoding="utf-8"))
        h1 = H1_RE.search(text)
        title = meta.get("title") or (h1.group(1).strip() if h1 else src.stem)
        body = render(md, strip_h1(text))
        lab_url = ""
        if (MODULES / src.stem / "lab.md").is_file():
            lab_url = f"{COURSE_URL}/{src.stem}/lab"
            body += ('<p class="lab-link"><strong>Lab:</strong> '
                     f'<a href="{lab_url}" target="_blank" rel="noopener">Open the lab</a> '
                     "— exercises you run against the benchmark on your own machine.</p>")
        out[src.with_suffix(".html")] = fill(
            title, page_start(body, lab_url) + body, sources_footer(meta, manifest))

    for lab in sorted(MODULES.glob("*/lab.md")):
        module_id = lab.parent.name
        text = lab.read_text(encoding="utf-8")
        h1 = H1_RE.search(text)
        title = h1.group(1).strip() if h1 else f"Lab: {module_id}"
        body = lab_setup(module_id) + render(md, strip_h1(text))
        out[READING / f"lab-{module_id}.html"] = fill(title, page_start(body) + body)
    return out


def build(check: bool = False) -> int:
    failures = 0
    for path, page in pages().items():
        name = path.relative_to(ROOT)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != page:
                print(f"stale: {name}")
                failures += 1
        else:
            path.write_text(page, encoding="utf-8")
            print(f"built {name}")
    return failures


if __name__ == "__main__":
    sys.exit(1 if build(check="--check" in sys.argv) else 0)
