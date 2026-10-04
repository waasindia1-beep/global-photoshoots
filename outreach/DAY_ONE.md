# Day One — the exact sequence

Everything below is already built. This is just the order to do it in, and the two
things you must fill in first. Do not skip step 0.

---

## Step 0 — unblock everything (10 minutes)

Two placeholders will silently cost you money if you leave them.

**a) `config.js`**

| Key | Put in |
| --- | --- |
| `businessAddress` | Your real, verifiable postal address |
| `city` | Your city |
| `region` | Your state |

Google, Justdial and IndiaMART all cross-check this address. The site prints a red
`Placeholder` badge on the portfolio and stops showing an address in the footer until
you do — it is designed to be obvious, not to fail quietly.

**b) `outreach/.env`**

```
SMTP_USER=you@yourdomain.com
SMTP_PASS=your-google-app-password
SENDER_ADDRESS=your real postal address
```

The sender refuses to run while `SENDER_ADDRESS` is a placeholder. That is on purpose:
CAN-SPAM requires a real address on commercial email.

---

## Step 1 — the fastest money (2 hours)

**Agencies and studios first. Not brands.** One agency client is worth twenty small
brands, they understand overflow, and they have the pain this week.

Open the runner. One lead per screen, message pre-filled, tap to send:

```
python outreach/build_whatsapp_runner.py
```

Then serve it to your phone (same Wi-Fi):

```
python -m http.server 8777 --directory "C:\Users\sitso\Desktop\global-photoshoots"
```

Open `http://<your-pc-ip>:8777/outreach/whatsapp_runner.html` on the phone. Tap
**Open in WhatsApp**, the message is already typed — press send. Come back and log
the outcome. When you are done, tap **Download log CSV** and drop the file into
`outreach/whatsapp_log.csv`, then rebuild to get the remainder.

All 42 leads are in it, already ranked and personalised.

**Send 10 today, by hand.** One at a time. Do not batch — this is the whole channel and
it is not worth risking it on an unofficial sender, which would ban the number that
earns.

The queue is sorted by who is most likely to say yes.

1. **Lohar Studio** — Delhi NCR, 16 years, 4000+ brands, 10K+ products shot, ₹49/photo,
   promises 24-72h turnaround. Owner is **Sanjay Babu Lohar**, so the message opens
   with his first name. They are not capacity-constrained and do not advertise limited
   slots — they are a high-volume packshop, which is exactly why overflow work fits.
   Your 24-48h beats their 72h. Do not lead with price: they set the floor at ₹49.
2. **TeamTSB** — agency, Amazon listing content alongside packshots.
3. **Digisetu India** — runs "Capture", a product photography studio in Jaipur.
4. **Tamzy** — caps and sunglasses; their About page publicly recruits models by email,
   so there is an existing creative-collab channel to walk in through.

**You send these. Not me.** Automated WhatsApp sends get the business number banned, and
that number is the one that takes the money.

---

## Step 2 — the free sample, built on demand

Every message in the queue **asks** whether they want a free sample frame. It does not
attach one. That is deliberate: asking costs you nothing and screens out the people who
were never going to buy.

So do not stall the queue waiting to build samples. Send first, build when someone says
yes — and then build it in their category, on their product, so it is unmistakably
theirs.

The one exception: having **one** frame ready before you start measurably speeds up your
reply, because you can send it the moment someone says yes instead of going away to
render. Ten minutes on the Bing generator for a single white-background packshot covers
this.

If a prospect sends you their product photos, `generate_openrouter.py --lohar` has a
ready-made marketplace-spec packshot prompt you can copy straight in.

---

## Step 3 — the calls (45 minutes)

20 prospects have no WhatsApp on their site. For those, use `call_script.md`.

**15 calls, between 11am and 2pm IST.** Log every one in `call_log.csv` including the
no's. After 30 calls, if zero have agreed to a sample, your hook is wrong — not your list.

---

## Step 4 — the emails (30 minutes, then stop)

```
python outreach/send_outreach.py --limit 15
```

Read them in `--preview` first. Then `--send`. **15 a day, maximum, for the first week**,
and only from an address you have warmed with real replies.

The WhatsApp messages will beat the emails. Email is the slower channel here, and it
exists because agencies and bigger brands have gatekeepers that WhatsApp does not.

Follow-ups: `--step 2` around day 5, `--step 3` around day 12. **Three touches maximum.**

---

## Step 5 — inbound, starting today, compounding

This is the half that runs without you working. `inbound_listings.md` has the exact copy.

1. **Google Business Profile — today.** Free tier. This is where calls come from when a
   stranger searches `product photography [your city]`.
2. **Verify it.** Unverified profiles do not rank and do not get calls.
3. **9 real photos.** Do not skip this, and do not use the placeholders.
4. **Justdial — same week.** Free to claim, and it is a large share of Indian service search.
5. **IndiaMART — same week.** This one sends enquiries to your inbox rather than to a
   search page. Respond within the hour; that is the ranking factor.
6. **Instagram — 20 minutes.** Set the WhatsApp contact button. Add four highlights:
   Work, How it works, Pricing, Rights.

Use the tagged links from section 7 of `inbound_listings.md` so you can tell which
listing earns.

---

## Step 6 — the thing that is still blocking conversions

The portfolio images are stock photos, badged `Placeholder`. Any prospect who messages
you, agrees to a sample, then clicks your site sees that badge. **That is where you lose
deals you already won.**

```
1. Drop your images into assets/portfolio/
2. Set the filenames in assets/portfolio/manifest.json
3. python sync_portfolio.py
```

Thirty seconds per image. Until this is done, every other step above works at maybe
half strength.

I could not do this part, and I want to be exact about why rather than vague. Two
generators were available and both are dead:

- The Google Gemini image API accepts the key you gave me, but the free tier is
  hard-capped: it returns `429, limit: 0` for every image model. That resets on Google's
  schedule and cannot be topped up.
- Kilo's built-in generator reports "no image generation provider available". Its
  stored `openrouter` entry is not a key at all — it is a blog URL.

**The free way out, in the browser you already have open:** Bing Image Creator at
`bing.com/images/create/ai-image-generator` generates on a free Microsoft account, and
it can do aspect ratio and mode. Paste a prompt, set 4:5 for the portfolio slots and 1:1
for the Lohar packshot. No API key, no billing.

```
python generate_openrouter.py --list     # shows slot -> filename for all 8
```

That prints the eight targets with their aspect ratios. `generate_portfolio.py` holds
the full prompts if you want to copy them out.

Ten minutes there replaces the two hours this step was costing, and it is the only
step standing between you and the rest of this page working at full strength.

---

## The weekly rhythm

| | |
| --- | --- |
| Daily | 10 WhatsApp messages, 15 calls, 15 emails, log all three |
| Daily | Answer the phone. +91 75575 75514 is your call line — miss it and they will not call twice. |
| Weekly | 1 Google Business Profile post |
| Weekly | Review `whatsapp_log.csv` + `call_log.csv` + `inbound_log.csv` |
| Weekly | Ask every completed customer for a Google review — cheapest conversion lever you have |
| Monthly | Sort your brief inbox by `Reference:` to see which channel earns |

---

## What to expect

Out of 10 WhatsApp messages to agencies who publicly advertise limited capacity, expect
2-4 replies and maybe 1 sample agreement. That is normal, not failure — the reason to
work the queue in priority order is that the reply rate is uneven by design.

The first paying client will most likely come from Step 5 (someone searching), not from
Step 1 (cold outreach). Cold messages open the relationship; the listings create the
steady flow. Keep doing both.

---

## If you only have an hour

1. `config.js` — real address, city and state (10 min). Until this is done the site
   shows a red `Placeholder` badge and Google will not verify the listing.
2. `python outreach/build_whatsapp_runner.py`, serve it, and message the top 10 (30 min).
   This is the part that earns — do it even if nothing else gets done.
3. One free sample frame for **Lohar Studio** on the Bing generator (20 min), so the
   first "yes" costs you nothing to honour.

If you have zero minutes, do step 2 alone.
