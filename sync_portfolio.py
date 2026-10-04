#!/usr/bin/env python3
"""Sync the portfolio manifest into index.html and app.js.

The portfolio originally pointed at Unsplash stock photography while the page
claimed to show "8K AI renders". Stock photos that look like campaign work are
worse than no image at all - a marketing prospect recognises them instantly.

This script makes swapping in real work a thirty-second job instead of a hunt
through 1,700 lines of HTML:

    1. Drop your image into assets/portfolio/
    2. Set its filename in assets/portfolio/manifest.json
    3. Run:  python sync_portfolio.py

What it rewrites:
  - the <img src> of each portfolio card in index.html
  - the matching `img:` entry in the portfolioData object in app.js (the lightbox)
  - the showcase before/after slider images
  - the status badge on each card, so the site never implies the work is a client
    commission when it is not:

        file missing        -> "Placeholder"   (still the old image, clearly flagged)
        file present, demo  -> "Sample render" (your own output, flagged as a sample)
        file present, real  -> no badge at all

Run with --check to report status without writing anything.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "assets" / "portfolio" / "manifest.json"
INDEX_HTML = ROOT / "index.html"
APP_JS = ROOT / "app.js"

PILL_RE = re.compile(r'<div class="absolute top-4 left-4">[\s\S]*?</div>')

BADGE_TMPL = (
    '\n            <div class="absolute top-4 right-4">\n'
    '              <span class="px-3 py-1 rounded-full text-[10px] font-mono font-semibold '
    'border backdrop-blur-md {cls}">{label}</span>\n'
    '            </div>'
)
BADGE_CLASSES = {
    "Placeholder": "bg-rose-500/20 text-rose-200 border-rose-400/40",
    "Sample render": "bg-amber-500/20 text-amber-200 border-amber-400/40",
}
BADGE_RE = re.compile(
    r'\n\s*<div class="absolute top-4 right-4">\s*<span[^>]*>\s*(?:Placeholder|Sample render)\s*</span>\s*</div>',
    re.S,
)

# The showcase slider labels its two halves. While those halves are still stock
# photography the labels have to stop claiming they are renders and schematics.
SHOWCASE_LABELS = {
    "finished": {
        "placeholder": "Placeholder image - not a render",
        "demo": "Sample AI Render",
        "real": "Finished 8K AI Editorial",
    },
    "schematic": {
        "placeholder": "Placeholder image - not a schematic",
        "demo": "Sample Prompt &amp; Lighting Schematic",
        "real": "Raw Prompt &amp; Lighting Schematic",
    },
}
SHOWCASE_LABEL_IDS = {"finished": "showcaseFinishedLabel", "schematic": "showcaseSchematicLabel"}


def die(msg):
    sys.exit(f"ERROR: {msg}")


def load_manifest():
    if not MANIFEST.exists():
        die(f"missing {MANIFEST}")
    # utf-8-sig transparently drops the BOM that Windows editors like Notepad and
    # PowerShell's Set-Content -Encoding UTF8 add to a JSON file.
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        die(f"manifest.json is not valid JSON: {exc}")


def all_refs(manifest):
    refs = [(i["id"], i["file"]) for i in manifest.get("items", [])]
    for key, entry in manifest.get("showcase", {}).items():
        refs.append((f"showcase:{key}", entry["file"]))
    return refs


def badge_html(label):
    return BADGE_TMPL.format(cls=BADGE_CLASSES[label], label=label)


def resolve_src(entry, port_dir):
    """Work out what a slot's <img src> should be.

    Returns (src, state) where state is 'real' | 'demo' | 'placeholder'. The fallback
    matters: without it, deleting an image would leave the page pointing at a file
    that is no longer there, which renders as a broken image rather than a placeholder.
    """
    if (port_dir / entry["file"]).exists():
        state = "demo" if entry.get("demo", True) else "real"
        return f"assets/portfolio/{entry['file']}", state
    return entry.get("fallback"), "placeholder"


def set_img_src(html, tag_pattern, src, label):
    tag = tag_pattern.search(html)
    if not tag:
        print(f"  ! no <img> matching {label} in index.html")
        return html, False
    patched = re.sub(r'(src=")([^"]*)(")', lambda m: m.group(1) + src + m.group(3),
                     tag.group(0), count=1)
    return html[:tag.start()] + patched + html[tag.end():], True


def sync_index(html, manifest, port_dir):
    """Rewrite each portfolio card's <img src> and manage its status badge."""
    showcase = manifest.get("showcase", {})

    for target, key in (("showcaseFinishedImg", "finished"), ("showcaseSchematicImg", "schematic")):
        entry = showcase.get(key)
        if not entry:
            continue
        src, state = resolve_src(entry, port_dir)
        if not src:
            die(f"showcase {key}: {entry['file']} is missing and no \"fallback\" is set, "
                f"which would leave a broken image on the page")

        # Attribute order varies, so locate the whole tag by id first, then patch src.
        tag_pattern = re.compile(rf'<img\b[^>]*\bid="{target}"[^>]*>')
        html, ok = set_img_src(html, tag_pattern, src, target)
        if ok:
            print(f"  = showcase {key} [{state}] -> {src[:70]}")

        # Keep the on-screen claim in step with what the image actually is.
        label = SHOWCASE_LABELS[key][state]
        label_id = SHOWCASE_LABEL_IDS[key]
        span = re.search(rf'<span id="{label_id}">([\s\S]*?)</span>', html)
        if not span:
            print(f"  ! no <span id=\"{label_id}\"> in index.html, label left as is")
        elif span.group(1) != label:
            html = html[:span.start()] + f'<span id="{label_id}">{label}</span>' + html[span.end():]
            print(f"  . showcase label [{state}]: {label}")

    for item in manifest.get("items", []):
        pid = str(item["id"])
        src, state = resolve_src(item, port_dir)
        if not src:
            die(f"portfolio slot {pid}: {item['file']} is missing and no \"fallback\" is set, "
                f"which would leave a broken image on the page")

        head = re.search(rf'<div class="portfolio-item[^"]*"[^>]*data-id="{pid}"', html)
        if not head:
            die(f"no portfolio card found with data-id=\"{pid}\"")

        start = head.start()
        nxt = html.find('class="portfolio-item', head.end())
        end = nxt if nxt != -1 else len(html)
        card = html[start:end]

        card, n = re.subn(r'(<img\s+[^>]*?src=")([^"]*)(")',
                          lambda m: m.group(1) + src + m.group(3), card, count=1)
        if not n:
            die(f"portfolio card data-id=\"{pid}\" has no <img> tag")
        print(f"  = card {pid} [{state}] -> {src[:70]}")

        card = BADGE_RE.sub("", card)
        label = None if state == "real" else ("Placeholder" if state == "placeholder" else "Sample render")
        if label:
            pill = PILL_RE.search(card)
            if not pill:
                print(f"  ! no category pill on card {pid}; badge skipped")
            else:
                card = card[:pill.end()] + badge_html(label) + card[pill.end():]
                print(f"  . card {pid} badged '{label}'")

        html = html[:start] + card + html[end:]

    return html


def sync_app_js(js, manifest, port_dir):
    """Point each portfolioData entry at whatever its slot currently resolves to."""
    for item in manifest.get("items", []):
        src, _ = resolve_src(item, port_dir)
        if not src:
            continue
        key = re.escape(str(item["id"]))
        pattern = re.compile(rf"('{key}'\s*:\s*\{{[\s\S]*?\bimg\s*:\s*')([^']*)(')")
        match = pattern.search(js)
        if not match:
            die(f"no portfolioData entry with key '{item['id']}' in app.js")
        js = js[:match.start()] + match.group(1) + src + match.group(3) + js[match.end():]
        print(f"  = app.js portfolioData[{item['id']}] -> {src[:70]}")
    return js


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report status without writing")
    args = ap.parse_args()

    manifest = load_manifest()
    port_dir = MANIFEST.parent

    items = manifest.get("items", [])
    missing = [f for _, f in all_refs(manifest) if not (port_dir / f).exists()]

    print(f"Manifest: {len(items)} portfolio slot(s), {len(missing)} image file(s) missing.")
    if missing:
        print("  missing: " + ", ".join(missing))
        print("  those slots keep their current image and are badged 'Placeholder'.")
    print()

    html = INDEX_HTML.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")

    new_html = sync_index(html, manifest, port_dir)
    new_js = sync_app_js(js, manifest, port_dir)

    unsplash = (
        len(re.findall(r"images\.unsplash\.com", new_html))
        + len(re.findall(r"images\.unsplash\.com", new_js))
    )
    real = [i for i in items
            if (port_dir / i["file"]).exists() and not i.get("demo", True)]

    if args.check:
        in_sync = (new_html == html and new_js == js)
        print()
        print(f"unsplash references remaining: {unsplash}")
        print("--check:", "in sync with the manifest." if in_sync else "OUT OF sync - run without --check.")
        return 0 if in_sync else 1

    if new_html != html:
        INDEX_HTML.write_text(new_html, encoding="utf-8")
        print("\nupdated index.html")
    if new_js != js:
        APP_JS.write_text(new_js, encoding="utf-8")
        print("updated app.js")

    demo = [i for i in items
            if i.get("demo", True) and (port_dir / i["file"]).exists()]
    print()
    print(f"unsplash references remaining: {unsplash}")
    print(f"Slots badged 'Sample render': {len(demo)} of {len(items)}.")
    print(f"Slots badged 'Placeholder':   {len(items) - len(demo) - len(real)}")
    print(f"Slots live (no badge):        {len(real)}")
    print("Set \"demo\": false once a slot shows your own finished work and the badge disappears.")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
