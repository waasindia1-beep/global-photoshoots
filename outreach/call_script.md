# Cold Call Script — Global Photoshoots

For the **20 prospects with no WhatsApp number on their site**. Everyone else in
`whatsapp_queue.csv` gets messaged, not called.

Call between **11:00 and 2:00 IST**. That is when a founder or a 3-person brand is
actually reachable. Before 10 and after 4 you are hitting a shopkeeper who cannot
make a decision.

---

## Before you dial

- Open their site on your second screen. You should be able to see their product
  range while you talk. Everything below depends on having looked.
- Have `whatsapp_queue.csv` open in a text editor so you can paste.
- Log every call in `call_log.csv`, including the ones that go nowhere. The no's are
  what tell you which segment is worth more time.

---

## 1. The 20-second opener

Never open with "my name is X and I run a studio." Open with something you saw.

> "Hi, is this the person who looks after [brand]? My name's Sudhir, I'm calling about
> the product photos on [brand].com — I actually had a look at your [specific product]
> listings before I called."

Then stop talking. The opener exists to get a second question ("yeah, what about them?"),
not to deliver your pitch.

**If they say they're not the right person**, ask for the name and number directly.
Do not pretend to be a customer or a customer service agent — that is how you get
blocked, and word travels fast in these circles.

---

## 2. The hook — one sentence, specific to them

Pick whichever fits the lead on your screen:

| Lead type | Say this |
| --- | --- |
| Multi-category catalogue | "You've got [N] product families on one site. That's a lot of imagery to keep current." |
| Marketplace seller | "Your [Amazon/Flipkart] listings are live — are the images being shot locally or are you using whatever photos came with the product?" |
| Apparel / streetwear | "The [product name] line — fit on model is what sells that, and it's hard to shoot." |
| Beauty / skincare | "Your [serum/lip] range sells on texture. Flat packshots don't show texture, which is why texture shots convert." |
| Jewellery / watches | "At [price] per piece, the macro detail is doing all the work. That needs proper lighting, not a phone." |
| Agency / studio | "You already resell [service]. I'm not competing — I'm overflow capacity at 24-48h, white-label." |

---

## 3. The offer — say this exactly

> "Here's what I'd suggest. Point me at your top three products, and I'll build **one
> free sample image** — one, at no cost. You send me a couple of photos of the product,
> I make the shot. If you don't like it, you delete it, and nobody ever has to talk to
> me again."

This is the whole pitch. It is short because a sample image is worth more than any
argument, and it is low-risk for them because they are not spending anything.

**Do not lead with price.** Verified competitor rates run from ₹49 to ₹1,450 per photo,
so you lose a price conversation. You win on turnaround: everyone else in this market
advertises "quick" and nobody puts a number on it. Yours is 24-48 hours, in writing.

---

## 4. Qualifying questions

You need three answers before you spend time on a custom sample:

1. **"Who makes the final call on images — you, or an agency?"**
   If an agency, you have a warm intro to sell and they need your pricing sheet, not a sample.
2. **"When's the last time you needed images fast, and how long did it take?"**
   If they answer with frustration, you have a sale. If they say "it's fine", you have a polite exit.
3. **"What are you spending per month on photography right now?"**
   Do not ask this as the first question. Ask it after they've shown interest.

---

## 5. Objection handling

**"We're happy with our current photographer."**
> "That's fair, and I'd not want you to break a working relationship. My offer is specific though — if they're ever at 5 days and you need it in 48 hours, that's the gap I fill. Can I send the sample anyway so you've got a fallback?"

**"Send us your rate card."**
> "Happy to. Before I do — is this for a specific launch, or are you reviewing options?"

**"How do we know the quality?"**
> "That's exactly what the free sample answers. You don't have to take my word for it, you look at the image."

**"Is this AI or real photography?"**
> "It's a hybrid — I'm a production studio that uses AI generation for the parts that don't need a physical set. You get full commercial copyright on every file, which is the thing that actually bites clients." *(Only say this if it's true of your process. Never overstate.)*

**"Not interested."**
> "No problem at all. I'll stop there. If images ever become a bottleneck, I'm on WhatsApp at that number."

Then hang up and log it. Do not push a fourth time.

---

## 6. What to ask for before you close

- The WhatsApp number for the person who decides (many sites hide it in the footer)
- Three product names or SKUs, emailed over
- Whether they use Shopify, Amazon, Flipkart, Myntra — this tells you which specs to shoot to

You leave every call with a WhatsApp number or a polite no. There is no third outcome.

---

## 7. The call log

`call_log.csv` columns:

```
date,company,segment,person_spoke_to,phone,outcome,quote_given,follow_up_date,notes
```

Outcomes: `no answer` · `wrong person` · `not interested` · `send rates` ·
`agreed to sample` · `callback requested`

Review after every 10 calls. If `agreed to sample` is zero after 30 calls, your hook is
wrong, not your list.

---

## Call volume

**15 calls a day.** More than that and the quality of the hook drops, because you start
reading the script at people instead of looking at their site. A cold call that is
personalised beats a hundred that are not.
