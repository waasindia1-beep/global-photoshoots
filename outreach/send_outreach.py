#!/usr/bin/env python3
"""
Outreach sender for Global Photoshoots.

Reads leads.csv, personalises a per-segment template, and sends it over SMTP
using credentials you supply. It is a DRY RUN by default: nothing is sent until
you pass --send. That is deliberate, because once mail leaves your domain it is
the deliverability that matters and you cannot take it back.

    python outreach/send_outreach.py --limit 5                # preview 5 emails
    python outreach/send_outreach.py --segment agency --preview # show 1 full email
    python outreach/send_outreach.py --limit 20 --send         # actually send 20

Credentials come from the environment or outreach/.env -- never hardcode them:

    SMTP_USER=you@yourdomain.com
    SMTP_PASS=your-google-app-password

Set SMTP_HOST/SMTP_PORT for other providers (defaults target Gmail: smtp.gmail.com:587).

CAN-SPAM notes (required for US recipients, and just good practice elsewhere):
  - a valid physical postal address is appended to every message
  - a one-click List-Unsubscribe header plus a mailto opt-out are both set
  - the From: name is a real person and the subject line never fakes a
    personal relationship ("Re:" tricks, fake "your order is ready")
  - every opt-out is written to suppression.txt and is permanent
"""

import argparse
import csv
import os
import random
import re
import smtplib
import sys
import time
from datetime import datetime, timezone
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEADS_CSV = HERE / "leads.csv"
SUPPRESSION = HERE / "suppression.txt"
LOG_CSV = HERE / "outreach_log.csv"
ENV_FILE = HERE / ".env"

# ---------------------------------------------------------------------------
# Sender identity. Change these to your real details before sending.
# ---------------------------------------------------------------------------
def load_env():
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


# Must run before the SENDER_* / SMTP_* lookups below, otherwise the module-level
# constants bind to the placeholder defaults and never see the values in .env.
load_env()

SENDER_NAME = "Sudhir Kumar Solanki"
SENDER_EMAIL = os.environ.get("SMTP_USER", "sudhir@globalphotoshoots.com")
SENDER_PHONE = "+91 75575 75514"
SENDER_BUSINESS = "Global Photoshoots"

# ⚠️ REPLACE THIS BEFORE SENDING. CAN-SPAM requires a valid postal address in every
# commercial email, and an inaccurate one is a deliverability and legal problem rather
# than a cosmetic one. Keep it identical to the address in ../config.js, your Google
# Business Profile and your Justdial listing - they get cross-checked.
SENDER_ADDRESS = os.environ.get("SENDER_ADDRESS", "REPLACE WITH YOUR REAL ADDRESS, City, State, PIN, India")

SITE_URL = "https://global-photoshoots.vercel.app/"

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))

# Conservative pacing. Bounce a little and you lose the domain for everyone.
MIN_DELAY_SECONDS = 45
MAX_DELAY_SECONDS = 120
DEFAULT_DAILY_CAP = 40


def load_suppression():
    if not SUPPRESSION.exists():
        return set()
    return {
        line.strip().lower()
        for line in SUPPRESSION.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }


def suppress(email, reason="manual"):
    email = email.strip().lower()
    with SUPPRESSION.open("a", encoding="utf-8") as f:
        f.write(f"{email}\t{datetime.now(timezone.utc).isoformat()}\t{reason}\n")


def load_leads(segment=None):
    if not LEADS_CSV.exists():
        sys.exit(f"Missing {LEADS_CSV}")
    rows = []
    with LEADS_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if segment and row.get("segment", "").strip().lower() != segment.lower():
                continue
            rows.append(row)
    return rows


def load_log():
    if not LOG_CSV.exists():
        return {}
    with LOG_CSV.open(newline="", encoding="utf-8") as f:
        return {r["email"].strip().lower(): r for r in csv.DictReader(f)}


def log_send(lead, status, detail=""):
    new = not LOG_CSV.exists()
    with LOG_CSV.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "timestamp_utc", "company", "email", "contact_name",
                "segment", "status", "detail",
            ],
        )
        if new:
            w.writeheader()
        w.writerow({
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "company": lead.get("company", ""),
            "email": lead.get("email", ""),
            "contact_name": lead.get("contact_name", ""),
            "segment": lead.get("segment", ""),
            "status": status,
            "detail": detail,
        })


def greeting(lead):
    """First-name-first greeting, degrading gracefully instead of 'Dear sir'."""
    name = (lead.get("contact_name") or "").strip()
    if name:
        return f"Hi {name.split()[0]},"
    team = (lead.get("company") or "").strip()
    return f"Hi {team} team," if team else "Hi there,"


def build_body(lead, step=1):
    """Render the per-step template for a lead.

    step 1 = first touch, 2 = follow-up, 3 = last touch.
    """
    subs = {
        "company": (lead.get("company") or "your brand").strip(),
        "contact_name": (lead.get("contact_name") or "").strip(),
        "hook": clean_hook(lead.get("hook")),
        "need": (lead.get("need") or "").strip(),
        "sender": SENDER_NAME,
        "site": SITE_URL,
        "phone": SENDER_PHONE,
    }
    tpl = (load_template(lead.get("template", "brand"), step) or "").strip()
    if not tpl:
        return ""
    try:
        return tpl.format(**subs)
    except KeyError as exc:
        sys.exit(f"Template references unknown placeholder {{{exc}}} for segment '{lead.get('template')}'")


TEMPLATE_DIR = HERE / "templates"

DETERMINERS = (
    "the ", "this ", "that ", "these ", "those ", "your ", "a ", "an ",
    "its ", "their ", "our ", "his ", "her ",
)


def load_template(segment, step):
    path = TEMPLATE_DIR / f"{segment.strip().lower()}.txt"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    # Split on every step marker; the chunks come out in order starting at step 1.
    chunks = re.split(r"---\s*STEP\s*\d+\s*---", text)
    idx = step - 1
    if idx < 0 or idx >= len(chunks):
        return None
    return chunks[idx]


def clean_hook(raw):
    """Hooks are written as noun phrases naming something real we saw on the prospect's
    own site ('your ceramic dinnerware range'), so they can be dropped after a verb or a
    preposition. Normalise to a form that reads correctly in every template: drop the
    possessive, then restore a definite article if a bare noun phrase would be left."""
    hook = (raw or "").strip().rstrip(".")
    if not hook:
        return ""
    if hook.lower().startswith("your "):
        hook = hook[5:]
    starts_with_determiner = hook.lower().startswith(DETERMINERS)
    # A capitalised first word usually means a proper noun ("D2C", "Amazon"), which
    # should not get an article. Digits and lowercase words are bare noun phrases.
    looks_like_proper_noun = hook[0].isupper()
    if not starts_with_determiner and not looks_like_proper_noun:
        hook = "the " + hook
    return hook


def build_subject(lead, step):
    subs = {
        "company": (lead.get("company") or "").strip(),
        "hook": (lead.get("hook") or "").strip(),
        "segment": (lead.get("segment") or "").strip(),
    }
    tpl = (lead.get("subject_1") or "").strip() if step == 1 else (lead.get("subject_2") or "").strip()
    if not tpl:
        tpl = "Your {company} product photos".replace("{company}", subs["company"])
    try:
        return tpl.format(**subs)
    except KeyError:
        return tpl


def build_message(lead, step, unsubscribe_url):
    msg = EmailMessage()
    msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"] = lead["email"]
    msg["Subject"] = build_subject(lead, step)
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="globalphotoshoots.com")
    msg["Reply-To"] = SENDER_EMAIL
    msg["List-Unsubscribe"] = f"<mailto:{SENDER_EMAIL}?subject=unsubscribe>, <{unsubscribe_url}>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg["X-Entity-Ref-ID"] = (lead.get("company") or "").strip()[:32]

    body = build_body(lead, step)
    footer = (
        f"\n\n---\n"
        f"{SENDER_NAME} · {SENDER_BUSINESS}\n"
        f"{SENDER_ADDRESS}\n"
        f"WhatsApp: {SENDER_PHONE} · {SITE_URL}\n"
        f"\nNot want further emails? Reply 'unsubscribe' or click {unsubscribe_url} "
        f"and you will never hear from me again."
    )
    msg.set_content(body + footer)
    return msg, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true", help="actually send (default is a dry run)")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--segment", help="filter: brand / agency / marketplace")
    ap.add_argument("--step", type=int, default=1, choices=[1, 2, 3])
    ap.add_argument("--preview", action="store_true", help="print full rendered emails and exit")
    ap.add_argument("--daily-cap", type=int, default=DEFAULT_DAILY_CAP)
    ap.add_argument("--unsubscribe-url", default=f"{SITE_URL}unsubscribe")
    ap.add_argument("--resend", action="store_true", help="ignore the send log and include already-sent leads")
    ap.add_argument("--include-unverified", action="store_true",
                    help="also queue leads whose status is 'verify email'")
    args = ap.parse_args()

    load_env()
    leads = load_leads(args.segment)
    prior = {} if args.resend else load_log()
    suppressed = load_suppression()

    queue = []
    skipped = {"sent": 0, "suppressed": 0, "no_email": 0, "do_not_contact": 0}
    for lead in leads:
        raw = (lead.get("email") or "").strip()
        email = raw.lower()
        local, _, domain = email.partition("@")
        looks_valid = bool(local) and bool(domain) and "." in domain and " " not in email
        if not looks_valid:
            skipped["no_email"] += 1
            continue
        if email in suppressed:
            skipped["suppressed"] += 1
            continue
        if email in prior:
            skipped["sent"] += 1
            continue
        status = (lead.get("status") or "").strip().lower()
        if status == "do not contact":
            skipped["do_not_contact"] += 1
            continue
        if status.startswith("verify") and not args.include_unverified:
            skipped["do_not_contact"] += 1
            continue
        queue.append(lead)

    print(f"Loaded {len(leads)} lead(s). "
          f"Skipped: {skipped['sent']} already sent, {skipped['suppressed']} suppressed, "
          f"{skipped['no_email']} without a usable email, {skipped['do_not_contact']} flagged/held.")
    print(f"Queued {len(queue)}.")

    if not queue:
        return

    if args.preview:
        lead = queue[0]
        msg, body = build_message(lead, args.step, args.unsubscribe_url)
        print("\n" + "=" * 70)
        print("FROM:", msg["From"])
        print("TO  :", msg["To"])
        print("SUBJ:", msg["Subject"])
        print("=" * 70)
        print(body)
        return

    if not args.send:
        print("\nDRY RUN - nothing sent. Pass --send to actually deliver.\n")
        for lead in queue[: args.limit]:
            msg, _ = build_message(lead, args.step, args.unsubscribe_url)
            print(f"  -> {lead['email']:<40} {msg['Subject']}")
        print(f"\nShowing {min(args.limit, len(queue))} of {len(queue)}. Add --preview to see one in full.")
        return

    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        sys.exit("Set SMTP_USER and SMTP_PASS (env vars or outreach/.env) before using --send.")
    if SENDER_ADDRESS.strip().upper().startswith("REPLACE"):
        sys.exit(
            "SENDER_ADDRESS is still the placeholder. CAN-SPAM requires a real postal\n"
            "address on commercial email. Set it in outreach/.env or at the top of this file."
        )

    sent_today = sum(
        1 for r in prior.values()
        if r.get("status") == "sent"
        and r.get("timestamp_utc", "").startswith(datetime.now(timezone.utc).date().isoformat())
    )
    budget = min(args.limit, max(0, args.daily_cap - sent_today))
    if budget <= 0:
        sys.exit(f"Daily cap reached ({sent_today}/{args.daily_cap}). Stopping.")
    print(f"Sending up to {budget} message(s), {sent_today} already sent today.")

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.starttls()
        server.login(smtp_user, smtp_pass)
    except Exception as exc:
        sys.exit(f"Could not connect/send: {exc}")

    print("Connection OK.\n")

    for i, lead in enumerate(queue[:budget], 1):
        email = lead["email"].strip()
        try:
            msg, _ = build_message(lead, args.step, args.unsubscribe_url)
            server.send_message(msg)
            log_send(lead, "sent", f"step {args.step}")
            print(f"  [{i}/{budget}] sent -> {email}")
        except smtplib.SMTPRecipientsRefused as exc:
            # A refused recipient is a hard no-send signal. Suppress immediately so we
            # never retry an invalid address and wreck our sender reputation.
            log_send(lead, "bounced", str(exc)[:120])
            suppress(email, "recipient refused")
            print(f"  [{i}/{budget}] BOUNCE  {email} (suppressed)")
        except Exception as exc:
            log_send(lead, "error", str(exc)[:120])
            print(f"  [{i}/{budget}] ERROR   {email}: {exc}")
            break

        if i < budget:
            time.sleep(random.uniform(MIN_DELAY_SECONDS, MAX_DELAY_SECONDS))

    try:
        server.quit()
    except Exception:
        pass

    print("\nDone. Check outreach_log.csv for the full history.")


if __name__ == "__main__":
    main()