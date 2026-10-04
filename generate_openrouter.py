"""Generate portfolio art and free outreach sample frames via OpenRouter.

The Google Gemini endpoint in generate_portfolio.py is the primary path, but its
free tier enforces a hard daily request cap that resets on Google's schedule and
cannot be topped up. OpenRouter is the fallback: set OPENROUTER_API_KEY and this
script fills the same slots.

Key is read from, in order: the environment, then a .env beside this file. It is
never written into any tracked file - .gitignore covers .env.

Usage:
    python generate_openrouter.py --list
    python generate_openrouter.py --lohar
    python generate_openrouter.py --only 3
    python generate_openrouter.py --all
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PORTFOLIO = ROOT / "assets" / "portfolio"
SAMPLES = ROOT / "outreach" / "samples"

API = "https://openrouter.ai/api/v1/chat/completions"

# Gemini flash image is the best cost/latency trade for proof-of-concept frames.
# Swap for google/gemini-3-pro-image-preview when you want the higher fidelity pass.
DEFAULT_MODEL = "google/gemini-2.5-flash-image-preview"

# Free sample frames for outreach. Each one is deliberately built to be the single
# most persuasive image for that target's category - the thing they sell.
LOHAR_PROMPT = (
    "Commercial e-commerce packshot photograph on a seamless pure white background "
    "(RGB 255,255,255), copy stand, large softbox plus a white fill card. Subject: an "
    "unbranded frosted-glass cosmetic serum bottle with a matte white screw cap, "
    "standing upright, dead centre, filling roughly 85 percent of the frame. "
    "Completely blank product with no text, no logo, no label copy. Crisp specular "
    "highlight down the left edge of the glass, one soft natural contact shadow "
    "beneath the bottle, gradient-free white sweep. Colour-accurate, neutral white "
    "balance, no colour cast. Razor-sharp from cap to base, high micro-contrast, "
    "commercial retouching: dust-free, scratch-free. Medium-format look, 100mm macro, "
    "f/11. Must read as a real studio photograph, not a render."
)


def load_key():
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY"):
                _, _, val = line.partition("=")
                val = val.strip().strip("'\"")
                if val:
                    return val
    return ""


def load_prompts():
    """Reuse the Gemini script's prompts so both backends stay identical."""
    sys.path.insert(0, str(ROOT))
    from generate_portfolio import PROMPTS  # noqa: E402

    return PROMPTS


def request_image(key, model, prompt, retries=2):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image", "text"],
    }).encode("utf-8")

    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://global-photoshoots.vercel.app/",
            "X-Title": "Global Photoshoots",
        },
        method="POST",
    )

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            images = payload["choices"][0]["message"].get("images") or []
            if not images:
                raise RuntimeError("model returned no image")
            url = images[0]["image_url"]["url"]
            if url.startswith("data:"):
                return base64.b64decode(url.split(",", 1)[1])
            with urllib.request.urlopen(url, timeout=300) as r:
                return r.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:400]
            if exc.code in (429, 500, 502, 503, 529) and attempt < retries:
                wait = 10 * (attempt + 1)
                print(f"  HTTP {exc.code}, retrying in {wait}s", flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc


def save(blob, out_path):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(blob)
    return len(blob)


def manifest_files():
    """Map prompt name -> output path.

    manifest.json keys portfolio entries by numeric id but names the file by
    prompt slug ("fashion-lookbook.png"), so index on the filename stem instead.
    """
    mf = PORTFOLIO / "manifest.json"
    if not mf.exists():
        return {}
    data = json.loads(mf.read_text(encoding="utf-8"))
    slots = {}
    for item in data.get("items", []):
        stem = Path(item["file"]).stem
        slots[stem] = PORTFOLIO / item["file"]
    for entry in data.get("showcase", {}).values():
        stem = Path(entry["file"]).stem
        slots[stem] = PORTFOLIO / entry["file"]
    return slots


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lohar", action="store_true", help="free sample frame for Lohar Studio")
    ap.add_argument("--only", help="manifest slot id to fill")
    ap.add_argument("--all", action="store_true", help="fill every manifest slot")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--list", action="store_true", help="list slots and exit")
    args = ap.parse_args()

    prompts = load_prompts()
    files = manifest_files()

    if args.list:
        for name, meta in prompts.items():
            print(f"{name:22} {meta['aspect']:6} -> {files.get(name, 'MISSING')}")
        print(f"{'lohar-studio':22} {'1:1':6} -> outreach/samples/lohar-studio-packshot.png")
        return

    key = load_key()
    if not key:
        sys.exit(
            "No OPENROUTER_API_KEY.\n"
            "  setx OPENROUTER_API_KEY sk-or-v1-...   (then reopen the terminal)\n"
            "  or put OPENROUTER_API_KEY=sk-or-v1-... in a .env file beside this script"
        )

    jobs = []
    if args.lohar:
        jobs.append(("lohar-studio-packshot", LOHAR_PROMPT, SAMPLIES / "lohar-studio-packshot.png"))
    if args.only:
        if args.only not in prompts:
            sys.exit(f"unknown slot {args.only}; try --list")
        jobs.append((args.only, prompts[args.only]["prompt"], files[args.only]))
    if args.all or (not args.lohar and not args.only):
        for name, meta in prompts.items():
            if name in files:
                jobs.append((name, meta["prompt"], files[name]))

    if not jobs:
        sys.exit("nothing to do; pass --lohar, --only N, --all or --list")

    print(f"model: {args.model}\n")
    failures = 0
    for name, prompt, out_path in jobs:
        print(f"[{name}] -> {out_path.relative_to(ROOT)}", flush=True)
        try:
            blob = request_image(key, args.model, prompt)
            size = save(blob, out_path)
            print(f"  OK {size/1024:.0f} KB\n", flush=True)
        except Exception as exc:  # noqa: BLE001 - report and keep going
            failures += 1
            print(f"  FAILED: {exc}\n", flush=True)

    print(f"done: {len(jobs) - failures}/{len(jobs)} succeeded")
    if failures:
        print("run sync_portfolio.py after the files land so index.html picks them up.")


if __name__ == "__main__":
    main()
