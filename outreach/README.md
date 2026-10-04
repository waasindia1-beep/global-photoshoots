# Outreach system

Everything needed to fill the pipeline with inbound calls and WhatsApp messages, without
wrecking the sender domain.

## Start here

**Read [`DAY_ONE.md`](DAY_ONE.md) first** — it is the ordered action list with the exact
commands. This file is the reference behind it.

## What is here

| File | What it is |
| --- | --- |
| **`DAY_ONE.md`** | **The sequence. Start here.** |
| `leads.csv` | 70 researched prospects. Emails read off each company's own live contact page; `email_source_url` records where. |
| `build_whatsapp_queue.py` | Builds the prioritised WhatsApp queue. 41 prospects have a mobile number on their site. |
| `whatsapp_queue.csv` | The generated queue, ranked by likelihood of a yes, with the message written out. |
| `whatsapp_log.csv` | Log every WhatsApp conversation. Header only until you send. |
| `call_script.md` | Cold-call script for the 20 with no WhatsApp, plus objection handling. |
| `call_log.csv` | Call outcomes, including the no's. |
| `inbound_listings.md` | Google Business Profile, Justdial, IndiaMART, Instagram — paste-ready copy. **Where the calls actually come from.** |
| `inbound_log.csv` | Everything that arrives without you chasing it. |
| `send_outreach.py` | The email sender. Dry run by default. |
| `templates/brand.txt` | D2C brand email outreach (skincare, fashion, home, food). 3 steps. |
| `templates/agency.txt` | Agencies and studios. White-label overflow, not competition. 3 steps. |
| `templates/marketplace.txt` | Sellers who need compliant main images to win Buy Box. 3 steps. |
| `templates/whatsapp_*.txt` | WhatsApp first-touch copy. Short, 4 lines, no paragraphs. |
| `suppression.txt` | Opt-outs. Written to automatically. **Never delete lines from here.** |
| `outreach_log.csv` | Every email send attempt, with status. Created on first send. |
| `.env.example` | Credential template. Copy to `.env`, fill in, never commit `.env`. |

## Channel priority — do not skip this

**WhatsApp first.** 41 of the 70 prospects publish a mobile number, and for a lot of them
it is the *only* contact method. An email to a small Delhi brand sits unread for a week;
the same message on WhatsApp usually gets an answer that evening. Agencies and studios —
13 of the list — also skew to WhatsApp-first because that is how Indian agencies
actually communicate.

Email is second: it exists because larger brands and some agencies have gatekeepers that
WhatsApp does not. Keep it to 15 a day.

Cold calling is third and only for the 20 leads with no number on their site.

Inbound (Google, Justdial, IndiaMART) is the half that compounds without you working on
it. It is where the calls come from when a stranger searches for the service.

## Before your first send

**1. Set up sending.** Use a Gmail **app password**, not your account password, and send
from a real, warmed address on a domain you control. `sudhir@globalphotoshoots.com` is
only useful if that mailbox actually receives mail.

```
SMTP_USER=sudhir@yourdomain.com
SMTP_PASS=xxxx xxxx xxxx xxxx
SENDER_ADDRESS=your real postal address
```

Gmail: enable 2FA → Google Account → Security → App passwords.
Other providers: set `SMTP_HOST` / `SMTP_PORT` too.

**2. Fill in `config.js`.** `businessAddress`, `city` and `region` are placeholders right
now. Google Business Profile and Justdial verify the address and cross-check it against
each other, and CAN-SPAM requires it on every commercial email. The site refuses to
print a half-finished address to a prospect.

**3. Warm the mailbox.** Send 20–30 real replies to real people over 2 weeks first. A
cold mailbox sending 40 cold emails on day one gets the whole domain flagged.

**4. Check the unsubscribe page.** The script points `unsubscribe_url` at
`https://global-photoshoots.vercel.app/unsubscribe`. That page now exists. Do not break
it — a broken unsubscribe link is the fastest way to get a complaint.

**5. Replace the portfolio placeholders.** Six cards are badged `Placeholder`. Any
prospect who agrees to a sample and then clicks your site sees that badge. See the
root `README.md` for the 30-second swap.

## Running it

```powershell
# WhatsApp: see the top 5 messages, ranked by likelihood of a yes
python outreach/build_whatsapp_queue.py --next 5

# WhatsApp: regenerate the queue after logging conversations
python outreach/build_whatsapp_queue.py

# Email: preview one in full, exactly as it would be received
python outreach/send_outreach.py --preview --segment agency

# Email: preview the queue without sending (this is the default)
python outreach/send_outreach.py --limit 15

# Email: actually send
python outreach/send_outreach.py --limit 15 --send

# Follow-ups, ~4 days later, non-responders only
python outreach/send_outreach.py --step 2 --limit 15 --send
```

The email send log is what makes step 2 work — already-sent addresses are skipped
automatically, so a follow-up only touches non-responders.

## Why nothing here sends WhatsApp automatically

Every automated WhatsApp sender on the internet works by driving an unofficial WhatsApp
Web client against your business number. WhatsApp bans those numbers — and it bans the
**number**, not the software. A single automated blast would take out the one channel
that earns, and it would stay banned.

So the queue gives you the ranked list and the written message, and you send each one by
hand. That is also the only way the message stays personalised, which is the entire
point.

## Safety rails that are already on

- **Dry run unless `--send`** for email. No way to accidentally mail the list.
- **Nothing sends WhatsApp at all**, by design.
- **45–120 s random delay** between emails. Sending 40 in 90 seconds is a bot signature.
- **Daily cap of 40** on email. Override with `--daily-cap`.
- **Hard bounces auto-suppress.** A refused recipient goes into `suppression.txt` and is
  never retried. This is what keeps the bounce rate low.
- **Refuses to send if `SENDER_ADDRESS` is still the placeholder.**
- **Opt-out is one word.** Every email says reply "unsubscribe". Add the address to
  `suppression.txt` immediately when it happens.
- **List-Unsubscribe header** set for one-click unsubscribe in Gmail and Apple Mail.

## Follow-up schedule

| Day | Step | Tone |
| --- | --- | --- |
| 1 | 1 | First touch, free sample offer |
| 5 | 2 | One follow-up, no new pitch |
| 12 | 3 | Last note, explicitly closes the loop |

Three touches is the ceiling. More than that is spam, and it is also how you get blocked
by Gmail for everyone else's mail too.

## The part that actually makes money

Every message offers **one free sample frame** built from the prospect's own product.

Do that sample **before** sending the message, and attach it. When a founder opens an
image that looks like it belongs in their own store, the reply rate is not comparable to
sending the offer cold. This is the single highest-leverage hour available to you.

## What NOT to do

- Do not send from a free Gmail to domain-email brands, and do not mix free and domain
  senders in one campaign — it damages both.
- Do not send to anyone twice after they ask you to stop.
- Do not invent a case study, client name or result. Every claim here is one you can stand
  behind.
- Do not blast. 10 thoughtful WhatsApp messages and 15 calls a day beats 2,000 scraped ones.
- Do not lead with price. Competitors advertise ₹49–₹1,450 per photo. You win on a written
  turnaround guarantee and full commercial rights, not on being cheaper.