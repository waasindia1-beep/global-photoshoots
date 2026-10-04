"""Build a self-contained, phone-friendly runner for the WhatsApp outreach queue.

Why this exists: the queue was 42 rows in a CSV on a desktop with an empty send
log. Cold outreach only makes money when it is actually sent, and sending 42
messages is only realistic as a 20-minute phone task. This emits one lead per
screen with the message pre-filled in WhatsApp, so the only action is tapping
send. Outcomes are logged on-device and exported as a CSV at the end.

Run it again after logging outcomes to regenerate with whatever is left.

    python outreach/build_whatsapp_runner.py
"""

import csv
import html
import json
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
QUEUE = HERE / "whatsapp_queue.csv"
LOG = HERE / "whatsapp_log.csv"
OUT = HERE / "whatsapp_runner.html"

# Outcomes. "skip" keeps a lead for later without marking it contacted.
OUTCOMES = [
    ("sent", "Sent"),
    ("interested", "Replied - interested"),
    ("not_now", "Replied - not now"),
    ("no_reply", "No reply 48h"),
    ("wrong", "Wrong number"),
    ("skip", "Skip for now"),
]

SITE = "https://global-photoshoots.vercel.app/"


def load_log():
    if not LOG.exists():
        return {}
    with LOG.open(newline="", encoding="utf-8") as f:
        return {
            r["wa_number"]: r
            for r in csv.DictReader(f)
            if r.get("wa_number") and r.get("reply")
        }


def build_items():
    if not QUEUE.exists():
        sys.exit(f"missing {QUEUE} - run build_whatsapp_queue.py first")
    with QUEUE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    done = load_log()
    items = []
    for r in rows:
        if r["wa_number"] in done:
            continue
        number = r["wa_number"]
        message = r["message"]
        items.append({
            "n": number,
            "company": r["company"],
            "segment": r["segment"],
            "category": r["category"],
            "prio": int(r["priority"]),
            "site": r.get("website", ""),
            "email": r.get("email", ""),
            "msg": message,
            # ?text= means WhatsApp opens with the message already typed.
            "wa": f"https://wa.me/{number}?text={urllib.parse.quote(message)}",
        })
    return items


TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>WhatsApp Runner - Global Photoshoots</title>
<style>
  :root{
    --bg:#0f131f; --bg2:#0a0d16; --card:#141b2d; --line:#1f2a44;
    --ink:#fff; --dim:#8b97b0; --accent:#38bdf8; --accent2:#6366f1;
    --ok:#22c55e; --warn:#f59e0b; --bad:#ef4444;
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;padding:0}
  body{
    background:var(--bg);color:var(--ink);
    font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    padding:0 0 env(safe-area-inset-bottom);
  }
  header{
    position:sticky;top:0;z-index:10;background:var(--bg2);
    border-bottom:1px solid var(--line);padding:14px 16px 12px;
  }
  .row{display:flex;align-items:center;gap:10px}
  h1{font-size:15px;margin:0;font-weight:700;letter-spacing:.2px;flex:1}
  .count{font-size:13px;color:var(--dim);font-variant-numeric:tabular-nums}
  .bar{height:5px;background:var(--line);border-radius:99px;margin-top:10px;overflow:hidden}
  .bar>i{display:block;height:100%;background:linear-gradient(90deg,var(--accent),var(--accent2));
    border-radius:99px;transition:width .25s}
  main{padding:16px;max-width:640px;margin:0 auto}
  .card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}
  .meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:4px}
  .badge{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;
    padding:3px 9px;border-radius:99px;border:1px solid}
  .b-brand{color:#c4b5fd;border-color:#4c1d95;background:#2e1065}
  .b-agency{color:#67e8f9;border-color:#155e75;background:#083344}
  .b-marketplace{color:#fcd34d;border-color:#78350f;background:#451a03}
  .prio{margin-left:auto;font-size:11px;color:var(--dim);font-variant-numeric:tabular-nums}
  h2{font-size:22px;margin:6px 0 2px;letter-spacing:-.3px}
  .sub{font-size:13px;color:var(--dim);margin-bottom:14px}
  .msg{background:var(--bg2);border:1px solid var(--line);border-radius:12px;
    padding:14px;font-size:15px;white-space:pre-wrap;line-height:1.55}
  .go{display:block;width:100%;margin-top:14px;padding:17px;border:0;border-radius:14px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));color:#04121f;
    font-size:17px;font-weight:800;cursor:pointer;text-align:center}
  .go:active{transform:scale(.985)}
  .lbl{font-size:11px;font-weight:700;color:var(--dim);text-transform:uppercase;
    letter-spacing:.7px;margin:18px 0 8px}
  .outs{display:grid;grid-template-columns:1fr 1fr;gap:8px}
  .outs button{padding:14px 8px;border-radius:12px;border:1px solid var(--line);
    background:var(--bg2);color:var(--ink);font-size:14px;font-weight:600;cursor:pointer}
  .outs button:active{border-color:var(--accent)}
  .o-sent{color:var(--ok)} .o-interested{color:var(--accent)} .o-not_now{color:var(--warn)}
  .o-no_reply,.o-wrong{color:var(--bad)} .o-skip{color:var(--dim)}
  .nav{display:flex;gap:8px;margin-top:16px}
  .nav button{flex:1;padding:13px;border-radius:12px;border:1px solid var(--line);
    background:transparent;color:var(--dim);font-size:14px;cursor:pointer}
  .totals{margin-top:26px;padding-top:16px;border-top:1px solid var(--line);
    font-size:13px;color:var(--dim)}
  .totals b{color:var(--ink)}
  .foot{display:flex;gap:8px;margin-top:16px}
  .foot button{flex:1;padding:13px;border-radius:12px;border:1px solid var(--line);
    background:var(--card);color:var(--ink);font-size:14px;font-weight:600;cursor:pointer}
  .empty{text-align:center;padding:60px 20px}
  .empty h2{font-size:20px;margin-bottom:8px}
  .empty p{color:var(--dim);font-size:14px}
  a{color:var(--accent)}
</style>
</head>
<body>
<header>
  <div class="row">
    <h1>WhatsApp Runner</h1>
    <span class="count" id="cnt"></span>
  </div>
  <div class="bar"><i id="fill" style="width:0%"></i></div>
</header>
<main id="app"></main>

<script>
const ITEMS = __ITEMS__;
const KEY = "gp-wa-log-v1";

const load = () => { try { return JSON.parse(localStorage.getItem(KEY) || "{}"); } catch { return {}; } };
let log = load();
let idx = 0;

const esc = s => String(s == null ? "" : s)
  .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");

function remaining(){ return ITEMS.filter(it => !(log[it.n] && log[it.n].reply)); }

function render(){
  const app = document.getElementById("app");
  const left = remaining();
  const done = ITEMS.length - left.length;

  document.getElementById("cnt").textContent = done + " / " + ITEMS.length;
  document.getElementById("fill").style.width =
    (ITEMS.length ? (done / ITEMS.length * 100) : 100) + "%";

  if (!left.length){
    app.innerHTML = '<div class="empty"><h2>Queue clear</h2>' +
      '<p>Every lead has an outcome logged. Send yourself the summary below, ' +
      'then work the replies.</p></div>' + totals();
    bindTotals();
    return;
  }
  if (idx >= left.length) idx = left.length - 1;
  const it = left[idx];

  app.innerHTML =
    '<div class="card">' +
      '<div class="meta">' +
        '<span class="badge b-' + esc(it.segment) + '">' + esc(it.segment) + '</span>' +
        '<span class="prio">score ' + esc(it.prio) + '</span>' +
      '</div>' +
      '<h2>' + esc(it.company) + '</h2>' +
      '<div class="sub">' + esc(it.category) + (it.site ? ' &middot; ' + esc(it.site.replace(/^https?:\\/\\//,"")) : '') + '</div>' +
      '<div class="msg">' + esc(it.msg) + '</div>' +
      '<a class="go" href="' + esc(it.wa) + '" target="_blank" rel="noopener">Open in WhatsApp</a>' +
      '<div class="lbl">After you hit send, log it</div>' +
      '<div class="outs">' + OUTCOMES.map(([k, label]) =>
        '<button class="o-' + k + '" data-o="' + k + '">' + label + '</button>').join("") + '</div>' +
      '<div class="nav">' +
        '<button id="prev">Previous</button>' +
        '<button id="next">Skip ahead</button>' +
      '</div>' +
    '</div>' + totals();

  document.getElementById("prev").onclick = () => { idx = Math.max(0, idx - 1); render(); };
  document.getElementById("next").onclick = () => { idx = Math.min(left.length - 1, idx + 1); render(); };
  app.querySelectorAll("[data-o]").forEach(b => b.onclick = () => {
    // "Skip" must not write an outcome, otherwise remaining() would drop the
    // lead from the queue. It just moves to the next one.
    if (b.dataset.o === "skip"){ idx += 1; render(); return; }
    log[currentNumber()] = { reply: b.dataset.o, at: new Date().toISOString() };
    save(); idx = 0; render();
  });
  bindTotals();
}

function currentNumber(){ return remaining()[idx].n; }

function save(){ localStorage.setItem(KEY, JSON.stringify(log)); }

function totals(){
  const c = {};
  Object.values(log).forEach(v => { if (v && v.reply) c[v.reply] = (c[v.reply]||0)+1; });
  const d = Object.entries(c).filter(([k]) => k !== "skip");
  const sent = d.reduce((a,[,v]) => a + v, 0);
  const hot = (c.interested || 0);
  return '<div class="totals"><b>' + sent + '</b> logged &middot; <b>' + hot +
    '</b> interested' + (d.length ? '<br>' + d.map(([k,v]) => esc(k.replace(/_/g," ")) + ": " + v).join(" &middot; ") : '') +
    '</div><div class="foot">' +
    '<button id="dl">Download log CSV</button>' +
    '<button id="rs">Reset log</button></div>';
}

function bindTotals(){
  const dl = document.getElementById("dl");
  if (dl) dl.onclick = () => {
    const head = "date,company,wa_number,segment,reply,logged_at";
    const rows = Object.entries(log).filter(([,v]) => v && v.reply).map(([n,v]) => {
      const it = ITEMS.find(x => x.n === n) || {};
      const d = (v.at || "").slice(0,10);
      return [d, '"' + String(it.company||"").replace(/"/g,'""') + '"', n,
              '"' + String(it.segment||"") + '"', v.reply, v.at];
    });
    const csv = [head].concat(rows).join("\\n");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([csv], {type:"text/csv"}));
    a.download = "whatsapp_log.csv"; a.click();
  };
  const rs = document.getElementById("rs");
  if (rs) rs.onclick = () => { if (confirm("Clear all logged outcomes on this device?")) {
    log = {}; save(); idx = 0; render(); } };
}

const OUTCOMES = __OUTCOMES__;
render();
</script>
</body>
</html>
"""


def main():
    items = build_items()
    if not items:
        print("Queue is empty - everything has a logged outcome.")
    else:
        print(f"{len(items)} leads queued (already-logged leads excluded).")
    body = (TEMPLATE
            .replace("__ITEMS__", json.dumps(items, ensure_ascii=False))
            .replace("__OUTCOMES__", json.dumps(OUTCOMES)))
    OUT.write_text(body, encoding="utf-8")
    print(f"Wrote {OUT}")
    print("Copy it to your phone and open it in a browser, or serve it:")
    print(f"  python -m http.server 8000 --directory {HERE.parent}")
    print("Then open http://<your-pc-ip>:8000/outreach/whatsapp_runner.html on the phone.")


if __name__ == "__main__":
    main()