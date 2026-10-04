#!/usr/bin/env python3
"""Generate the studio portfolio with Google's Gemini image models (Nano Banana).

The portfolio originally pointed at Unsplash stock photography while the page
claimed to show "8K AI renders". These images are genuine AI renders produced by
exactly the kind of tool this studio sells, so they are honest replacements for
the stock placeholders.

Prerequisite: a Google AI Studio key with the Generative Language API enabled.
Set it as an environment variable - never hardcode it, never commit it:

    PowerShell:
        $env:GEMINI_API_KEY = "your-key-here"
        python generate_portfolio.py

    persistent (recommended):
        [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key", "User")

Usage:
    python generate_portfolio.py                 # all 8 images
    python generate_portfolio.py --only 1        # just the first, to test
    python generate_portfolio.py --model gemini-3.1-flash-image   # cheaper/faster
    python generate_portfolio.py --list
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

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "assets" / "portfolio"

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

DEFAULT_MODEL = "gemini-3-pro-image"

# Each entry maps a manifest slot to the prompt that fills it. Slot ids match
# assets/portfolio/manifest.json so the two stay in step.
PORTRAIT_NOTE = (
    "Editorial commercial photography. Shot on a full-frame camera with an 85mm f/1.4 "
    "lens look, natural depth of field, true-to-life colour, 8K detail, crisp micro-texture. "
    "Lighting is physically plausible with visible falloff and shadow direction. "
    "The result must read as a real photograph, not a render. "
    "No text, no watermark, no logo, no visible brand marks, no extra limbs or distorted hands."
)

PROMPTS = {
    "fashion-lookbook": {
        "aspect": "4:5",
        "prompt": (
            "High-fashion editorial photograph. A model wears a flowing pastel silk organza "
            "couture dress with intricate pleats and translucent layered fabric, standing in a "
            "sunlit Parisian Haussmann interior with tall wrought-iron windows and stone floors. "
            "Soft diffused north-facing daylight, gentle wrap shadows, shallow depth of field. "
            "Muted palette of blush, ivory and soft gold. Magazine quality. " + PORTRAIT_NOTE
        ),
    },
    "watch-macro": {
        "aspect": "4:5",
        "prompt": (
            "Extreme macro product photograph of a luxury skeleton mechanical wristwatch. Black "
            "obsidian-textured dial, exposed tourbillon cage and gear train, blued steel screws, "
            "rose-gold case with mirror-polished bevels, fine knurling on the crown. Ray-traced "
            "sapphire crystal reflections, crisp specular highlights along every chamfer, zero "
            "dust and no fingerprints. Deep black background, one large softbox plus a precise "
            "rim accent, dramatic and moody. " + PORTRAIT_NOTE
        ),
    },
    "skincare": {
        "aspect": "4:5",
        "prompt": (
            "Photorealistic cosmetics product photograph. A frosted glass serum bottle with a "
            "brushed aluminium cap sits on a wet dark stone slab, covered in fresh water droplets "
            "with realistic surface tension and a few running trails. A single dewy green leaf "
            "beside it. Soft warm morning sunlight filtering through with a gentle leaf shadow. "
            "Frosted glass translucency, visible liquid texture, natural condensation on the glass. "
            "Minimal beauty editorial style, shallow depth of field. The bottle is completely blank "
            "with no label or lettering. " + PORTRAIT_NOTE
        ),
    },
    "cinematic-reel": {
        "aspect": "4:5",
        "prompt": (
            "Cinematic still frame from a premium automotive commercial film. A sleek matte charcoal "
            "electric sports car in a dark studio, dramatic cyan and magenta rim lighting, volumetric "
            "haze in the air, wet reflective floor with long streaked light reflections. Subtle "
            "motion blur suggesting speed. Anamorphic lens flare, moody and premium. The car carries "
            "no badge, logo or licence plate. " + PORTRAIT_NOTE
        ),
    },
    "techwear": {
        "aspect": "4:5",
        "prompt": (
            "Photorealistic cyberpunk streetwear editorial. A model wears an oversized matte black "
            "technical shell jacket and wide cargo trousers with subtle reflective piping, standing "
            "on a rain-wet narrow city alley at night. Volumetric neon haze in blue and magenta, wet "
            "pavement reflections, drifting atmospheric fog, volumetric light from shop signage. "
            "Cinematic colour grading, realistic technical fabric weave and water resistance sheen. "
            "Garment is completely unbranded. " + PORTRAIT_NOTE
        ),
    },
    "portrait": {
        "aspect": "4:5",
        "prompt": (
            "Extreme photorealistic beauty close-up portrait of a young adult woman. Natural human "
            "skin showing visible micro-pores, fine vellus hair, realistic epidermal subsurface "
            "scattering and subtle natural tonal unevenness. Highly detailed iris with fine radial "
            "fibres and a single crisp natural eye catchlight, individual separated eyelashes, "
            "natural brow hairs. Soft beauty-dish lighting at 5600K, minimal retouching, honest "
            "editorial standard, sharp focus on the near eye. " + PORTRAIT_NOTE
        ),
    },
    "showcase-finished": {
        "aspect": "16:9",
        "prompt": (
            "Ultra-photorealistic high-fashion editorial campaign image, wide cinematic composition. "
            "Two models in avant-garde sculptural couture stand in a vast empty concrete gallery "
            "beneath a single skylight shaft. One wears ivory structured silk, the other deep "
            "charcoal draped jersey. Dramatic contrast between the hard skylight beam and deep "
            "shadow, soft fill light, visible fabric texture, natural skin. Magazine cover quality. "
            + PORTRAIT_NOTE
        ),
    },
    "showcase-schematic": {
        "aspect": "16:9",
        "prompt": (
            "Technical 3D wireframe render of a human figure in contrapposto stance, displayed as a "
            "grey polygonal mesh with visible triangle edges and vertex points. Overlaid with a "
            "precise lighting schematic drawn as thin glowing cyan vector lines: a key light at 45 "
            "degrees, a rim light behind, and thin amber arcs marking the softbox source and catch "
            "light positions. Dark navy technical background, blueprint aesthetic, glowing wireframe "
            "over faint depth-of-field grid floor. Clean and legible. No text or labels of any kind."
        ),
    },
}

# Showcase labels in index.html describe the image honestly; regenerate those too.
LABEL_IDS = {
    "showcase-finished": "showcaseFinishedLabel",
    "showcase-schematic": "showcaseSchematicLabel",
}


def get_key():
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit(
            "GEMINI_API_KEY is not set.\n\n"
            "PowerShell:\n"
            "    $env:GEMINI_API_KEY = \"your-key\"\n"
            "or permanently:\n"
            "    [Environment]::SetEnvironmentVariable(\"GEMINI_API_KEY\", \"your-key\", \"User\")"
        )
    return key


def generate(key, model, prompt, aspect, out_path, retries=2):
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect},
        },
    }
    url = API.format(model=model)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-goog-api-key": key, "Content-Type": "application/json"},
        method="POST",
    )

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", "replace")[:400]
            if exc.code in (429, 500, 503) and attempt < retries:
                wait = 10 * (attempt + 1)
                print(f"      {exc.code}, retrying in {wait}s")
                time.sleep(wait)
                continue
            sys.exit(f"\nAPI error {exc.code} for {out_path.name}:\n{body}")
        except urllib.error.URLError as exc:
            if attempt < retries:
                time.sleep(8)
                continue
            sys.exit(f"\nNetwork error: {exc.reason}")

    b64 = None
    for cand in data.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                b64 = inline["data"]
                break
        if b64:
            break

    if not b64:
        block = data.get("promptFeedback") or data.get("error") or {}
        sys.exit(f"\nNo image returned for {out_path.name}: {json.dumps(block)[:400]}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(b64))
    return out_path.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, help="generate just slot N (1-based, in the order below)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    slots = list(PROMPTS.keys())
    if args.list:
        for i, s in enumerate(slots, 1):
            print(f"{i}. {s}  ({PROMPTS[s]['aspect']})")
        return

    key = get_key()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    targets = slots if args.only is None else [slots[args.only - 1]]
    print(f"Model: {args.model}")
    print(f"Generating {len(targets)} image(s) into {OUT_DIR}\n")

    failures = []
    for slot in targets:
        dest = OUT_DIR / f"{slot}.png"
        spec = PROMPTS[slot]
        print(f"  -> {slot}.png  [{spec['aspect']}]")
        try:
            size = generate(key, args.model, spec["prompt"], spec["aspect"], dest)
            print(f"     ok, {size // 1024} KB")
        except SystemExit:
            raise
        except Exception as exc:
            print(f"     FAILED: {exc}")
            failures.append(slot)

    print()
    if failures:
        print("Failed:", ", ".join(failures))
        sys.exit(1)

    print("All images generated.")
    print("Now wire them in and label them honestly:")
    print("    python sync_portfolio.py")


if __name__ == "__main__":
    main()
