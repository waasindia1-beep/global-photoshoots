#!/usr/bin/env python3
"""Build the WhatsApp calling queue from leads.csv.

WhatsApp is the real channel for this market: 49 of the 70 researched prospects
publish a wa.me number, often as their only contact route. A cold email to a
Delhi brand founder sits unread for a week; the same message on WhatsApp usually
gets a reply the same evening.

IMPORTANT - THIS DOES NOT SEND ANYTHING, AND THAT IS DELIBERATE.
Every automated WhatsApp sender on the internet works by driving an unofficial
WhatsApp Web client against the business number. WhatsApp bans those numbers,
and it bans the *number*, not the software - so the blast would take out the one
channel that earns. This script produces the queue and the message text; you
open WhatsApp and send each one by hand. That is also the only way the message
stays personalised rather than templated, which is the entire point.

Usage:
    python outreach/build_whatsapp_queue.py              # write whatsapp_queue.csv
    python outreach/build_whatsapp_queue.py --next 10    # print the next 10 messages
    python outreach/build_whatsapp_queue.py --stats      # tier breakdown only
"""

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEADS = HERE / "leads.csv"
TEMPLATES = HERE / "templates"
QUEUE = HERE / "whatsapp_queue.csv"
LOG = HERE / "whatsapp_log.csv"
SITE = "https://global-photoshoots.vercel.app/"
SENDER = "Sudhir (Global Photoshoots)"

# Signals that a prospect has spare budget or an open pain right now, read from
# the research. Each one is a reason to expect them to say yes this month.
OVERFLOW_SIGNALS = {
    "lohar studio": 30,        # advertises limited shoot slots + 30-minute quote promise
    "theprinkmedia": 28,       # contact page openly recruiting creative staff
    "teamtsb": 26,             # high-volume Amazon packshot operation
    "7irisstudio": 24,         # runs a studio-rental model, capacity constrained
    "digisetu": 24,            # resells photography inside a comms platform
    "jamnadigi": 26,           # resells photography to its own web/SEO clients
    "eighteendigitalmarketing": 24,
    "socialeyes": 24,    "medianextdoor": 22,
    "buzzbuddymedia": 20,
    "dare network": 22,
    "thedarenetwork": 22,
    "emipixsolutions": 22,
    "tatvastudio": 18,
}

# Brands that recruit models or run collaboration programmes have an open door.
WARM_SIGNALS = {
    "tamzy": 24,               # About page asks models to email for shoot collabs
    "auli lifestyle": 22,      # runs a Glow & Grow collaboration programme
    "hyphen": 22,              # routes collaborations/media to a public inbox
    "earth rhythm": 20,
    "arata": 20,
    "thesunya": 20,            # already ships AI try-on, open to the conversation
}

# Larger or slower-to-reply accounts. Contacted later, not dropped.
SLOW_SIGNALS = {
    "sugarcosmetics": -18,
    "sugar cosmetics": -18,
    "dotandkey": -16,
    "dot and key": -16,
    "deconstruct": -14,
    "vilvah": -14,
    "fix my curls": -10,
    "simply nam": -10,
    "skin story": -8,
    "the skin story": -8,
}

SEGMENT_BASE = {"agency": 20, "brand": 10, "marketplace": 6}


def clean_hook(raw, limit=64):
    """Shorten the hook to something that fits a WhatsApp message.

    WhatsApp copy is read on a phone in a notification preview, so a 70-word
    product description kills the message before it is opened. Cut on a word
    boundary so it still reads as a phrase.
    """
    hook = (raw or "").strip().rstrip(".")
    if hook.lower().startswith("your "):
        hook = hook[5:]
    if not hook:
        return "your range"
    if len(hook) <= limit:
        return hook
    cut = hook[:limit].rsplit(" ", 1)[0].rstrip(",")
    return cut


def normalise_wa(raw):
    """Extract digits and keep the India country code.

    Leads store numbers in every shape a website footer uses: 'wa.me/919540589758',
    '+91 99711 93530', '1800-103-5572'. Only a real mobile can take a WhatsApp
    message, and a toll-free number cannot, so both are filtered out.
    """
    if not raw:
        return None
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None
    # Toll-free / landline style numbers cannot receive WhatsApp messages.
    if digits.startswith("1800") or digits.startswith("1860") or digits.startswith("022"):
        return None
    if len(digits) == 10:
        digits = "91" + digits
    if not (digits.startswith("91") and len(digits) == 12):
        return None
    return digits


def score(lead):
    key = lead["company"].strip().lower()
    s = SEGMENT_BASE.get(lead["segment"].strip().lower(), 0)
    for table, weight in ((OVERFLOW_SIGNALS, None), (WARM_SIGNALS, None), (SLOW_SIGNALS, None)):
        for k, v in table.items():
            if k in key:
                s += v
                break
    # Gmail-only contact addresses are a reliable proxy for a 1-5 person shop that
    # actually replies, rather than a marketing inbox nobody opens.
    if lead["email"].strip().lower().endswith("@gmail.com"):
        s += 8
    return s


def salutation(lead):
    """Greet a named person where we actually verified their name, else the team.

    Only ever uses a name that was read off the company's own site, so this
    stays factual. Names arrive as "Sanjay Babu Lohar", "Mr. Sanjay Babu Lohar"
    or "Sanjay" - take the first token that is not a title.
    """
    titles = {"mr", "mrs", "ms", "miss", "dr", "shri", "smt", "prof"}
    raw = (lead.get("contact_name") or "").replace(",", " ").split()
    for tok in raw:
        if tok.lower().strip(".") not in titles:
            return f"Hi {tok} - Sudhir from Global Photoshoots."
    return f"Hi {lead['company'].strip()} team - Sudhir from Global Photoshoots."


def render(lead):
    tpl = TEMPLATES / f"whatsapp_{lead['template'].strip().lower()}.txt"
    if not tpl.exists():
        return None
    text = tpl.read_text(encoding="utf-8").strip()
    return text.format(
        company=lead["company"].strip(),
        hook=clean_hook(lead.get("hook")),
        site=SITE,
        salutation=salutation(lead),
    )


def load_log():
    if not LOG.exists():
        return {}
    with LOG.open(newline="", encoding="utf-8") as f:
        return {r["wa_number"]: r for r in csv.DictReader(f)}


def build():
    if not LEADS.exists():
        sys.exit(f"missing {LEADS}")
    with LEADS.open(newline="", encoding="utf-8") as f:
        leads = list(csv.DictReader(f))

    prior = load_log()
    rows, skipped = [], {"no_wa": 0, "sent": 0, "not_mobile": 0, "no_message": 0}

    for lead in leads:
        wa = normalise_wa(lead.get("whatsapp"))
        if not (lead.get("whatsapp") or "").strip():
            skipped["no_wa"] += 1
            continue
        if not wa:
            skipped["not_mobile"] += 1
            continue
        if wa in prior:
            skipped["sent"] += 1
            continue
        msg = render(lead)
        if not msg:
            skipped["no_message"] += 1
            continue
        rows.append({
            "priority": score(lead),
            "company": lead["company"].strip(),
            "segment": lead["segment"].strip(),
            "category": lead["category"].strip(),
            "wa_number": wa,
            "wa_link": f"https://wa.me/{wa}",
            "website": lead["website"].strip(),
            "email": lead["email"].strip(),
            "hook": clean_hook(lead.get("hook")),
            "chars": len(msg),
            # Keep the paragraph breaks: on WhatsApp a four-line message reads far
            # better than the same words run together into one block.
            "message": "\n".join(l.strip() for l in msg.strip().splitlines() if l.strip()),
        })

    rows.sort(key=lambda r: (-r["priority"], r["company"].lower()))
    return rows, skipped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", type=int, default=0, help="print the N highest-priority messages")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    rows, skipped = build()

    if args.stats or not args.next:
        print(f"WhatsApp queue: {len(rows)} ready")
        print(f"  skipped: {skipped['sent']} already sent, {skipped['no_wa']} no WhatsApp on site, "
              f"{skipped['not_mobile']} number is not a mobile")
        print()
        print("Priority order (agents first - overflow work is the fastest money):")
        for i, r in enumerate(rows[: args.next or 15], 1):
            print(f"  {i:>2}. [{r['priority']:>3}] {r['company']:<28} {r['segment']:<12} {r['wa_link']}")

    if args.next:
        print("\n" + "=" * 72)
        for r in rows[: args.next]:
            print(f"\n--- {r['company']}  ({r['wa_link']})  [{r['chars']} chars]")
            print(r["message"])
        print("=" * 72)
        over = [r for r in rows if r["chars"] > 400]
        if over:
            print(f"\n{len(over)} message(s) exceed 400 chars - trim before sending.")
        else:
            longest = max(r["chars"] for r in rows)
            print(f"\nAll messages within 400 chars (longest {longest}).")

    if args.next or args.stats:
        return

    with QUEUE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {QUEUE} ({len(rows)} rows)")
    print("Send these by hand, one at a time. Log every outcome in whatsapp_log.csv.")


if __name__ == "__main__":
    main()
