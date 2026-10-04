# Global Photoshoots (Next-Gen AI Visual Production Studio)

Website and digital storefront for **Sudhir Kumar Solanki** / **[@global.photoshoots](https://www.instagram.com/global.photoshoots/#)**.

> *"To the uninitiated, AI photography might seem like 'pressing a button.' To the expert, it is a sophisticated symphony of technical precision, lighting mastery, and generative physics."*

---

## ⚠️ Read this first: `index.html` is the source of truth

`build_index.py` **is stale.** It no longer generates the current `index.html` — it is
missing content that only exists in the HTML, including the broken Instagram icons that
were live for months. **Never run `python build_index.py`**: it will overwrite the real
site with an older, poorer version of it and silently undo the fixes below.

Edit `index.html` directly. `build_index.py` has been left in place only so the history is
traceable.

## 📁 Structure

| Path | Purpose |
| --- | --- |
| `index.html` | The site. **This is the file to edit.** |
| `app.js` | All interactivity: currency, calculator, gallery, modals, brief builder. |
| `config.js` | All business config — contact details, currency rates, webhook, analytics, address. |
| `styles.css` | Custom CSS on top of Tailwind. |
| `assets/favicon.svg` | Browser icon (fixes a 404 on every visit). |
| `assets/og-cover.png` | 1200×630 social share card. Regenerate with `python make_og_image.py`. |
| `robots.txt` / `sitemap.xml` | Crawl directives. Bump `<lastmod>` when you ship. |
| `unsubscribe.html` | Opt-out page. **Required by the outreach emails — do not delete.** |
| `outreach/` | Cold outreach system. See `outreach/README.md`. |
| `assets/portfolio/manifest.json` | **Which image sits in each portfolio slot.** Edit this, not the HTML. |
| `sync_portfolio.py` | Applies the manifest to `index.html` + `app.js`. See below. |
| `verify.py` | Sanity check: asserts every DOM id `app.js` depends on exists. |
| `make_og_image.py` | Regenerates the share card PNG. |
| `build_index.py` | ⚠️ Stale. Do not run. |

---

## 🖼 Swapping In Your Real Portfolio Work

The portfolio was pointing at **Unsplash stock photography** while the page claimed to
show "8K AI renders". Stock photos dressed up as campaign work are worse than no image
— any marketing prospect recognises them instantly. It also mislabels the showcase
slider, which captioned the same stock photo "Finished 8K AI Editorial".

`manifest.json` + `sync_portfolio.py` fix that and keep the site honest while you swap:

1. Drop your image into `assets/portfolio/`
2. Put its filename in `assets/portfolio/manifest.json`
3. Run `python sync_portfolio.py`

It rewrites the card image, the matching lightbox entry in `app.js`, and the showcase
slider, then labels each slot according to what it actually holds:

| Slot state | Badge | Showcase label |
| --- | --- | --- |
| Image file absent | `Placeholder` (red) | "Placeholder image - not a render" |
| Your output, `"demo": true` | `Sample render` (amber) | "Sample AI Render" |
| Your output, `"demo": false` | none | "Finished 8K AI Editorial" |

`fallback` in the manifest is what shows while the file is absent, so deleting an image
falls back cleanly instead of leaving a broken image on the page.

```powershell
python sync_portfolio.py --check    # report status, change nothing
```

**Never delete the `fallback` key until your own image is in place** — the script
refuses to write if a slot would end up pointing at a file that does not exist.

---

## 🔧 Configuration (`config.js`)

Everything you might want to change lives in one file.

| Key | What it does |
| --- | --- |
| `whatsappNumber` / `instagramUrl` / `contactEmail` | All contact routes |
| `businessAddress` | Printed in the footer. **CAN-SPAM requires a real postal address on every outreach email** |
| `leadWebhook` | Blank = briefs arrive by email. Paste a Formspree/Apps Script URL to store them in a sheet instead. |
| `analyticsDomain` | Blank = no analytics, no third-party scripts. Add your Plausible domain to switch it on. |
| `freeSampleOfferEnabled` | Shows the "one free sample frame" risk-reversal in the booking form. |

---

## 🌟 Key Features & Conversion Architecture

1. **Direct Instagram Integration**:
   - Deep-linked across the site to `https://www.instagram.com/global.photoshoots/#`.
   - Direct Instagram DM Brief transmitter that compiles the client's creative brief into the clipboard and immediately directs them to the `@global.photoshoots` message window.

2. **Unbeatable ROI & Business Value Battle Cards**:
   - High-contrast visual comparison between **Traditional Physical Shoots** ($5,000–$25,000+, 3–6 weeks turnaround, weather delays, equipment fees) vs. **Global Photoshoots AI Studio** ($199–$899, 24–48 hours delivery, infinite locations, 8K UHD).

3. **Interactive ROI & Cost Savings Calculator**:
   - Interactive sliders for number of commercial photos and cinematic video clips.
   - Dynamic real-time calculation of net client savings (saving $7,000+ per campaign) and turnaround days saved.

4. **Interactive "Concept to Masterpiece" Before/After Slider**:
   - Smooth mouse and touch slider showing the transition from initial lighting/pose wireframe geometry into the finished 8K photorealistic editorial campaign.

5. **Curated Commercial Portfolio Gallery with Lightbox**:
   - Filterable by:
     - Fashion & High-Street Editorial Lookbooks
     - Luxury Watches & Fine Jewelry Macro
     - Cosmetics & Skincare E-Commerce
     - Cinematic AI Video Reels (60 FPS)
     - Hyper-Realistic Skin & Portrait Benchmarks
   - Detail modal showing technical camera simulation specs (Hasselblad X2D 100C, 85mm f/1.4, Broncolor softbox).

6. **Commercial Packages for Brands & Agencies**:
   - **Packshot Sprint ($249)**: 10 commercial photos, 24–48h delivery.
   - **Brand Campaign Pro ($599)**: 25 photos + 2 cinematic 15s video ads.
   - **Enterprise Virtual Studio ($1,299)**: 60+ photos + 5 video ads, custom brand LoRA.

7. **Digital Products Marketplace**:
   - Sellable assets for generative artists, freelancers, and creative directors:
     - *The Fashion & Editorial Prompt Bible* ($29)
     - *Master Studio Lighting LoRA Weights* ($49)
     - *Cinematic Camera Motion Formulas* ($39)
     - *Luxury Cosmetics & Bottle Mockup Kit* ($35)
   - Interactive product preview and checkout modal.

8. **Frictionless Booking & Brief Estimator**:
   - Client name, contact, email, campaign type, deliverable count, timeline and creative brief.
   - **Submits by email as the primary path** (pre-filled `mailto:`, or a direct JSON POST if
     `leadWebhook` is set). WhatsApp and Instagram DM are the secondary options.
   - This used to only open a chat window, which meant every enquiry had to be chased
     manually and nothing was measurable. Email makes the lead land somewhere durable.

9. **Digital Store With An Honest Checkout**:
   - Purchase requests go by email or WhatsApp with the product and price pre-filled.
   - The previous "Checkout with Card / PayPal" button fired a `Demo Checkout` alert. That
     reads as unfinished to anyone clicking *Buy*, so it was replaced.

10. **Enterprise Brand FAQ**:
    - Clarifies multi-angle product consistency (via LoRA and ControlNet), 100% unrestricted commercial copyright ownership, and 8K master resolution.

11. **Social Share Card & Structured Data**:
    - `assets/og-cover.png` is a real 1200×630 PNG, because Facebook, LinkedIn, WhatsApp and
      X all reject SVG for `og:image`. This is what a prospect sees pasted into an inbox.
    - JSON-LD `ProfessionalService` + `OfferCatalog` + `Person` schema, so Google can surface
      the $249–$1,299 price range.

---

## 🚀 How to Run / View

### Option 1: Local HTTP Server (Python) — recommended
```powershell
cd "C:\Users\sitso\Desktop\global-photoshoots"
python -m http.server 3000
```
Then open `http://localhost:3000`.

Opening `index.html` directly with `file://` also works, but the fetch-based lead webhook
and some clipboard behaviour behave differently. Use the server.

### Option 2: Deploy
Static site — drop the folder into [Vercel](https://vercel.com), [Netlify Drop](https://app.netlify.com/drop) or GitHub Pages.
Deploy `index.html` at the root and `assets/`, `robots.txt`, `sitemap.xml`, `unsubscribe.html` alongside it.

### Verify after any edit
```powershell
python verify.py
```
Fails loudly if `app.js` references a DOM id that no longer exists in the HTML — the exact
class of bug that let the Instagram icons break unnoticed.

---

## 🚨 Known Issues Worth Fixing Next

1. **The portfolio still needs your real work.** The stock photos are now honestly
   badged `Placeholder` rather than passed off as renders, but the fix is to replace
   them. See *Swapping In Your Real Portfolio Work* above — it is a 30-second job per
   image.
2. **Tailwind is loaded from the CDN**, which causes a flash of unstyled content and prints a
   production warning. Move to the Tailwind CLI for a proper build.
3. **Lucide brand icons no longer exist**, so `app.js` renders the Instagram glyph as inline
   SVG. Do not reintroduce `<i data-lucide="instagram">`.
4. **No testimonials or client logos.** Genuine ones would help most — do not fabricate them.
5. **Prices in `config.js` and `app.js` are hardcoded** and disagree with the site's copy in
   places. Single source of truth would be safer.
6. **Cards 6 and the showcase "before" side share one Unsplash photo.** The manifest fallbacks
   make this trivial to fix — point them at different files.
