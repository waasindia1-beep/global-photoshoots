// Global Photoshoots - Enhanced Studio Application Script
document.addEventListener('DOMContentLoaded', () => {
  const config = window.STUDIO_CONFIG || {
    instagramHandle: '@global.photoshoots',
    instagramUrl: 'https://www.instagram.com/global.photoshoots/#',
    whatsappNumber: '917557575514',
    whatsappPrefilledMessage: 'Hi Sudhir! I want to book an AI Photoshoot / Video with Global Photoshoots.',
    contactEmail: 'sudhir@globalphotoshoots.com',
    calendlyUrl: 'https://calendly.com',
    defaultCurrency: 'USD',
    currencies: {
      USD: { symbol: '$', rate: 1 },
      INR: { symbol: '₹', rate: 85 },
      EUR: { symbol: '€', rate: 0.92 },
      GBP: { symbol: '£', rate: 0.78 }
    }
  };

  // 1. Initialize Lucide Icons
  // Lucide dropped brand icons (Instagram) from its icon set, so <i data-lucide="instagram">
  // renders as nothing and spams the console. Run createIcons() first, then swap the
  // leftover Instagram placeholders for inline SVG. Order matters: createIcons() would
  // otherwise re-scan the injected SVGs and clobber them.
  const inlineIcon = (selector, viewBox, shapes) => {
    document.querySelectorAll(selector).forEach(el => {
      const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      svg.setAttribute('viewBox', viewBox);
      svg.setAttribute('fill', 'none');
      svg.setAttribute('stroke', 'currentColor');
      svg.setAttribute('stroke-width', '2');
      svg.setAttribute('stroke-linecap', 'round');
      svg.setAttribute('stroke-linejoin', 'round');
      svg.setAttribute('aria-hidden', 'true');
      el.className.split(/\s+/).forEach(c => {
        if (c) svg.classList.add(c);
      });
      svg.innerHTML = shapes;
      // replaceWith drops the original element, and with it the data-lucide
      // attribute, so createIcons() never sees the icon it cannot resolve.
      el.replaceWith(svg);
    });
  };

  // Lucide dropped brand icons (Instagram) from its icon set, so <i data-lucide="instagram">
  // renders as nothing and spams the console. Swap those placeholders for inline SVG
  // BEFORE createIcons() runs.
  inlineIcon(
    '[data-lucide="instagram"]',
    '0 0 24 24',
    '<rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect>' +
      '<path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path>' +
      '<line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line>'
  );

  if (window.lucide) {
    window.lucide.createIcons();
  }

// 2. Analytics (opt-in). No third-party script is loaded unless a Plausible
  //   domain is set in config.js, so the site stays fully private by default.
  if (config.analyticsDomain) {
    const s = document.createElement('script');
    s.defer = true;
    s.dataset.domain = config.analyticsDomain;
    s.src = 'https://plausible.io/js/script.js';
    document.head.appendChild(s);
  }

  // 3. Lead-source attribution.
  //   Every outbound link he distributes gets a ?src= tag (gbp, justdial, whatsapp-outreach,
  //   instagram, referral). When someone lands and later enquires, that tag travels with the
  //   brief, so he can see which channel actually produces money instead of guessing.
  const qs = new URLSearchParams(window.location.search);
  const leadSource = qs.get('src') || qs.get('utm_source') || document.referrer || 'direct';
  window.LEAD_SOURCE = leadSource;
  try {
    sessionStorage.setItem('gp_lead_source', leadSource);
  } catch (err) {
    // Private browsing can block sessionStorage; the in-memory value still works.
  }

  // Surface it on the booking form so a prospect can see their enquiry is being attributed
  // and, more importantly, so a human reading the inbox knows where it came from.
  const sourceNote = document.getElementById('leadSourceNote');
  if (sourceNote) {
    sourceNote.textContent = `Reference: ${leadSource}`;
    sourceNote.classList.remove('hidden');
  }


  // 4. Set Current Year
  const yearEl = document.getElementById('currentYear');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // 5. Footer business address (drives trust and CAN-SPAM compliance)
  const addressEl = document.getElementById('businessAddressLine');
  const configPlaceholder = (v) => !v || /^REPLACE/i.test(v.trim());
  if (addressEl && config.businessAddress && !configPlaceholder(config.businessAddress)) {
    addressEl.textContent = config.businessAddress;
  }
  if (configPlaceholder(config.businessAddress)) {
    // Never print a half-finished address to a prospect. Failing visibly here is
    // better than shipping "REPLACE WITH YOUR REAL ADDRESS" onto a live page.
    console.warn(
      '[Global Photoshoots] config.businessAddress is still the placeholder. '
      + 'Set a real postal address in config.js - Google Business Profile and Justdial '
      + 'verify it, and CAN-SPAM requires it on outreach email.'
    );
  }

  // 6. City/state for local SEO. Injected into the page so the location is in the
  // rendered HTML, not just in a meta tag, which is what local ranking reads.
  if (config.city && !configPlaceholder(config.city)) {
    document.querySelectorAll('[data-city]').forEach(el => {
      el.textContent = el.textContent.replace(/\{\{city\}\}/g, config.city);
    });
  }

  // 7. Push the real address into the JSON-LD, so the structured data stops
  // advertising the REPLACE placeholder once config.js is filled in.
  document.querySelectorAll('script[type="application/ld+json"]').forEach(node => {
    if (configPlaceholder(config.businessAddress)) return;
    try {
      const data = JSON.parse(node.textContent);
      let touched = false;
      const walk = (obj) => {
        if (Array.isArray(obj)) { obj.forEach(walk); return; }
        if (!obj || typeof obj !== 'object') return;
        if (obj['@type'] === 'PostalAddress' && String(obj.streetAddress || '').startsWith('REPLACE')) {
          // businessAddress is written for humans, with commas. schema.org wants
          // the street alone in streetAddress, with city and region in their own
          // fields, so cut everything from the city onwards.
          const full = String(config.businessAddress).trim();
          const city = (config.city || '').trim();
          let street = full;
          if (city) {
            const at = full.toLowerCase().indexOf(city.toLowerCase());
            if (at > 0) street = full.slice(0, at).replace(/[\s,·-]+$/, '');
          }
          // Drop a trailing "India" that survived the split.
          street = street.replace(/[,·\s]+India$/i, '').trim();
          obj.streetAddress = street || full;
          obj.addressLocality = config.city || '';
          obj.addressRegion = config.region || '';
          touched = true;
        }
        Object.values(obj).forEach(walk);
      };
      walk(data);
      if (touched) node.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
      console.warn('Could not update the JSON-LD address:', err);
    }
  });

  // 7. Currency Conversion Engine
  let activeCurrency = config.defaultCurrency || 'USD';

  const formatPrice = (usdAmount, currCode = activeCurrency) => {
    const curr = config.currencies[currCode] || config.currencies.USD;
    const converted = Math.round(usdAmount * curr.rate);
    if (currCode === 'INR') {
      return `${curr.symbol}${converted.toLocaleString('en-IN')}`;
    }
    return `${curr.symbol}${converted.toLocaleString()}`;
  };

  // The Indian price list is INR-native; older markup still carries USD-base figures in
  // [data-usd-price]. Both are supported, and INR amounts are routed through the USD base
  // so every number on the page is produced by the one formatPrice() implementation.
  const inrToUsd = (inrAmount) => inrAmount / ((config.currencies.INR && config.currencies.INR.rate) || 85);
  const formatFromInr = (inrAmount, currCode = activeCurrency) => formatPrice(inrToUsd(inrAmount), currCode);

  const updateAllPrices = () => {
    document.querySelectorAll('[data-usd-price]').forEach(el => {
      const usdVal = parseFloat(el.getAttribute('data-usd-price'));
      if (!isNaN(usdVal)) {
        el.textContent = formatPrice(usdVal, activeCurrency);
      }
    });
    document.querySelectorAll('[data-inr-price]').forEach(el => {
      const inrVal = parseFloat(el.getAttribute('data-inr-price'));
      if (!isNaN(inrVal)) {
        el.textContent = formatFromInr(inrVal, activeCurrency);
      }
    });
    if (typeof window.updateCalculator === 'function') {
      window.updateCalculator();
    }
  };

  const currencySelector = document.getElementById('currencySelector');
  if (currencySelector) {
    currencySelector.value = activeCurrency;
    currencySelector.addEventListener('change', (e) => {
      activeCurrency = e.target.value;
      updateAllPrices();
    });
  }

  // 8. Mobile Navigation Menu Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
    });
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
      });
    });
  }

  // 9. Interactive Before/After Split Slider
  const sliderContainer = document.getElementById('beforeAfterSlider');
  const sliderBeforeContainer = document.getElementById('sliderBeforeContainer');
  const sliderHandle = document.getElementById('sliderHandle');

  if (sliderContainer && sliderBeforeContainer && sliderHandle) {
    let isDragging = false;
    const setPos = (clientX) => {
      const rect = sliderContainer.getBoundingClientRect();
      let percentage = ((clientX - rect.left) / rect.width) * 100;
      percentage = Math.max(2, Math.min(98, percentage));
      sliderBeforeContainer.style.width = percentage + '%';
      sliderHandle.style.left = percentage + '%';
    };

    sliderHandle.addEventListener('mousedown', () => { isDragging = true; });
    window.addEventListener('mouseup', () => { isDragging = false; });
    window.addEventListener('mousemove', (e) => {
      if (isDragging) setPos(e.clientX);
    });

    sliderHandle.addEventListener('touchstart', () => { isDragging = true; }, { passive: true });
    window.addEventListener('touchend', () => { isDragging = false; });
    window.addEventListener('touchmove', (e) => {
      if (isDragging && e.touches[0]) setPos(e.touches[0].clientX);
    }, { passive: true });

    sliderContainer.addEventListener('click', (e) => {
      setPos(e.clientX);
    });
  }

  // 10. Production Cost Calculator (INR-native price list, multi-currency reactive)
  //  Quoted from the same pack prices the Pricing section publishes, so the calculator
  //  cannot drift away from what a client is actually invoiced.
  const PACK_TIERS = [
    { name: 'Trial',   images: 1,  clips: 0, price: 499 },
    { name: 'Starter', images: 10, clips: 0, price: 2499 },
    { name: 'Growth',  images: 30, clips: 1, price: 6999 },
    { name: 'Scale',   images: 75, clips: 3, price: 17999 }
  ];
  const OVERFLOW_PER_IMAGE = 120;   // Studio Overflow, from INR 120/image
  const OVERFLOW_MIN_IMAGES = 100;  // ...on a 100-image minimum order
  const EXTRA_CLIP_INR = 1999;      // Add-on: extra video clip
  const RUSH_MULTIPLIER = 1.3;      // Add-on: 24h rush, +30%

  // Physical-studio benchmark. Deliberately the TOP of the verified Indian band (Delhi NCR
  // studios quote INR 167-500 per image and INR 1,500-3,000 per clip) so the comparison is
  // biased against us. No invented base fee, no inflated studio-day rate, no 90% claim.
  const STUDIO_INR_PER_IMAGE = 400;
  const STUDIO_INR_PER_CLIP = 3000;
  const STUDIO_BOOKING_DAYS = 6;    // 5-7 day booking cycle, midpoint
  const STUDIO_PRODUCTION_DAYS = 3; // brief, shoot, selects, retouch
  const DELIVERY_DAYS = { standard: 2, rush: 1 }; // 24-48h standard, 24h on rush

  // Smallest published pack that covers the requested image count, plus any clips beyond
  // what that pack includes, plus the rush fee if rush was selected.
  const quoteAiInr = (photos, clips, speed) => {
    const tier = PACK_TIERS.find(t => photos <= t.images);
    const overflowImages = Math.max(OVERFLOW_MIN_IMAGES, photos);
    const base = tier ? tier.price : overflowImages * OVERFLOW_PER_IMAGE;
    const extraClips = Math.max(0, clips - (tier ? tier.clips : 0));
    const subtotal = base + extraClips * EXTRA_CLIP_INR;
    const total = Math.round(speed === 'rush' ? subtotal * RUSH_MULTIPLIER : subtotal);

    const parts = [tier ? tier.name + ' pack' : 'Studio Overflow, ' + overflowImages + ' images'];
    if (extraClips > 0) {
      parts.push(extraClips + ' extra clip' + (extraClips === 1 ? '' : 's')
        + ' at ' + formatFromInr(EXTRA_CLIP_INR));
    }
    if (speed === 'rush') parts.push('24h rush +30%');
    return { total, breakdown: parts.join(' + ') };
  };

  const photosRange = document.getElementById('photosRange');
  const videosRange = document.getElementById('videosRange');
  const photosCountDisplay = document.getElementById('photosCountDisplay');
  const videosCountDisplay = document.getElementById('videosCountDisplay');
  const traditionalCostDisplay = document.getElementById('traditionalCostDisplay');
  const aiCostDisplay = document.getElementById('aiCostDisplay');
  const netSavingsDisplay = document.getElementById('netSavingsDisplay');
  const netSavingsLabel = document.getElementById('netSavingsLabel');
  const daysSavedDisplay = document.getElementById('daysSavedDisplay');
  const calcRateNote = document.getElementById('calcRateNote');
  const speedButtons = document.querySelectorAll('.speed-toggle');

  let currentSpeed = 'standard';

  window.updateCalculator = () => {
    if (!photosRange || !videosRange) return;
    const photos = parseInt(photosRange.value, 10);
    const videos = parseInt(videosRange.value, 10);

    photosCountDisplay.textContent = `${photos} Photos`;
    videosCountDisplay.textContent = `${videos} ${videos === 1 ? 'Clip' : 'Clips'}`;

    const { total: aiInr, breakdown } = quoteAiInr(photos, videos, currentSpeed);
    const studioInr = (photos * STUDIO_INR_PER_IMAGE) + (videos * STUDIO_INR_PER_CLIP);
    const netInr = studioInr - aiInr;
    const deliveryDays = DELIVERY_DAYS[currentSpeed] || DELIVERY_DAYS.standard;
    const daysSaved = Math.max(0, (STUDIO_BOOKING_DAYS + STUDIO_PRODUCTION_DAYS) - deliveryDays);

    if (traditionalCostDisplay) traditionalCostDisplay.textContent = formatFromInr(studioInr);
    if (aiCostDisplay) aiCostDisplay.textContent = formatFromInr(aiInr);

    // Honest in both directions: on a 5-image job a studio really can come out cheaper,
    // so the label and colour flip instead of showing a saving that does not exist.
    const isSaving = netInr >= 0;
    if (netSavingsDisplay) {
      netSavingsDisplay.textContent = isSaving
        ? `+${formatFromInr(netInr)}`
        : `-${formatFromInr(Math.abs(netInr))}`;
      netSavingsDisplay.classList.toggle('text-emerald-400', isSaving);
      netSavingsDisplay.classList.toggle('text-amber-400', !isSaving);
    }
    if (netSavingsLabel) {
      netSavingsLabel.textContent = isSaving ? 'Your Net Savings:' : 'Studio Is Cheaper By:';
    }
    if (daysSavedDisplay) daysSavedDisplay.textContent = `~${daysSaved} Days Saved`;
    if (calcRateNote) {
      calcRateNote.textContent = `${breakdown}. Delivered in ${deliveryDays} `
        + `${deliveryDays === 1 ? 'day' : 'days'}, product accuracy guaranteed, files yours `
        + 'to use commercially with no per-listing fees.';
    }
  };

  if (photosRange && videosRange) {
    photosRange.addEventListener('input', window.updateCalculator);
    videosRange.addEventListener('input', window.updateCalculator);

    speedButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        speedButtons.forEach(b => {
          b.classList.remove('active', 'bg-cyan-500/15', 'border-cyan-500/50', 'text-cyan-300');
          b.classList.add('bg-white/5', 'border-white/10', 'text-slate-400');
        });
        btn.classList.add('active', 'bg-cyan-500/15', 'border-cyan-500/50', 'text-cyan-300');
        btn.classList.remove('bg-white/5', 'border-white/10', 'text-slate-400');
        currentSpeed = btn.dataset.speed;
        window.updateCalculator();
      });
    });

    window.updateCalculator();
  }

  // 11. Portfolio Filters
  const filterBtns = document.querySelectorAll('.filter-btn');
  const portfolioItems = document.querySelectorAll('.portfolio-item');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => {
        b.classList.remove('active', 'bg-cyan-500', 'text-black', 'shadow-md', 'shadow-cyan-500/30');
        b.classList.add('bg-white/5', 'text-slate-300', 'border-white/5');
      });
      btn.classList.add('active', 'bg-cyan-500', 'text-black', 'shadow-md', 'shadow-cyan-500/30');
      btn.classList.remove('bg-white/5', 'text-slate-300', 'border-white/5');

      const filter = btn.getAttribute('data-filter');
      portfolioItems.forEach(item => {
        const itemCategory = item.getAttribute('data-category');
        item.style.display = (filter === 'all' || itemCategory === filter) ? 'block' : 'none';
      });
    });
  });

  // 12. Portfolio Lightbox
  const portfolioData = {
    '1': {
      title: 'Neo-Couture Parisienne Spring Lookbook',
      category: 'Fashion & Editorial',
      img: 'https://images.unsplash.com/photo-1509631179647-0177331693ae?q=80&w=1600&auto=format&fit=crop',
      desc: 'Executed with custom virtual models trained for luxury fashion brands. Combines soft Parisian diffused daylight, intricate organza silk folds, and an 85mm optical telephoto compression.'
    },
    '2': {
      title: 'Obsidian Tourbillon Macro Campaign',
      category: 'Luxury Watches & Jewelry',
      img: 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1600&auto=format&fit=crop',
      desc: 'Ray-traced crystal reflections and micro mechanical gears. Achieves crisp bevel highlights and hyper-fine diamond knurling without fingerprint smudges or reflection artifacts.'
    },
    '3': {
      title: 'Botanical Dew Drops Skincare Series',
      category: 'Cosmetics & Beauty',
      img: 'https://images.unsplash.com/photo-1556228720-195a672e8a03?q=80&w=1600&auto=format&fit=crop',
      desc: 'E-commerce hero visuals with frosted glass translucency, real physical water surface tension, and organic morning sunlight cast through monstera foliage.'
    },
    '4': {
      title: 'Electric Velocity: Brand Commercial Reel',
      category: 'Cinematic AI Video',
      img: 'https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?q=80&w=1600&auto=format&fit=crop',
      desc: '60 FPS seamless cinematic camera movement generated using combined diffusion and motion vector models. Perfect for Instagram Reels, TikTok brand launches, and digital billboards.'
    },
    '5': {
      title: 'Neo-Tokyo Techwear Capsule Lookbook',
      category: 'Urban Fashion & Streetwear',
      img: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=1600&auto=format&fit=crop',
      desc: 'Atmospheric cyberpunk night aesthetics with wet pavement reflections, volumetric blue-magenta neon haze, and realistic Gore-Tex matte fabric textures.'
    },
    '6': {
      title: 'Skin Micro-Pores & Iris Depth Benchmark',
      category: 'Hyper-Realistic Portraits',
      img: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?q=80&w=1600&auto=format&fit=crop',
      desc: 'Benchmark testing realistic human skin texture, epidermal scattering, individual eyelash strands, and natural eye catchlights without artificial plastic look.'
    }
  };

  const lightboxModal = document.getElementById('lightboxModal');
  const closeLightboxBtn = document.getElementById('closeLightboxBtn');
  const lightboxImg = document.getElementById('lightboxImg');
  const lightboxTitle = document.getElementById('lightboxTitle');
  const lightboxCategory = document.getElementById('lightboxCategory');
  const lightboxDescription = document.getElementById('lightboxDescription');

  portfolioItems.forEach(item => {
    item.addEventListener('click', () => {
      const id = item.getAttribute('data-id');
      const data = portfolioData[id];
      if (data && lightboxModal) {
        lightboxImg.src = data.img;
        lightboxTitle.textContent = data.title;
        lightboxCategory.textContent = data.category;
        lightboxDescription.textContent = data.desc;
        lightboxModal.classList.remove('hidden');
      }
    });
  });

  if (closeLightboxBtn && lightboxModal) {
    closeLightboxBtn.addEventListener('click', () => {
      lightboxModal.classList.add('hidden');
    });
    lightboxModal.addEventListener('click', (e) => {
      if (e.target === lightboxModal) lightboxModal.classList.add('hidden');
    });
  }

  // 13. Digital Product Modal
  const productModal = document.getElementById('productModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalProductTitle = document.getElementById('modalProductTitle');
  const modalProductPrice = document.getElementById('modalProductPrice');
  const modalEmailBtn = document.getElementById('modalEmailBtn');
  const modalWhatsAppBtn = document.getElementById('modalWhatsAppBtn');
  const digitalProductBtns = document.querySelectorAll('.digital-product-btn');

  let selectedProductName = '';
  let selectedProductInr = null;

  // Price comes from data-product-price (INR) or the separately rendered price span in the
  // same card, so updateAllPrices() can never overwrite the button's label text, and there
  // is no stale hardcoded USD figure to fall back to.
  const readProductInr = (btn) => {
    const own = parseFloat(btn.getAttribute('data-product-price'));
    if (!isNaN(own)) return own;
    const rendered = parseFloat(btn.parentElement?.querySelector('[data-inr-price]')
      ?.getAttribute('data-inr-price'));
    return isNaN(rendered) ? null : rendered;
  };

  const selectedProductPriceText = () =>
    selectedProductInr === null ? 'price on request' : formatFromInr(selectedProductInr);

  digitalProductBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      selectedProductName = btn.getAttribute('data-product') || 'Digital Asset';
      selectedProductInr = readProductInr(btn);
      if (modalProductTitle && modalProductPrice && productModal) {
        modalProductTitle.textContent = selectedProductName;
        modalProductPrice.textContent = selectedProductPriceText();
        productModal.classList.remove('hidden');
      }
    });
  });

  if (closeModalBtn && productModal) {
    closeModalBtn.addEventListener('click', () => {
      productModal.classList.add('hidden');
    });
    productModal.addEventListener('click', (e) => {
      if (e.target === productModal) productModal.classList.add('hidden');
    });
  }

  // This used to fire a fake "Demo Checkout" alert and open Instagram. A prospect
  // who clicks Buy and sees "Demo" does not buy, so requests go by email instead.
  if (modalEmailBtn) {
    modalEmailBtn.addEventListener('click', () => {
      const subject = encodeURIComponent(`Digital product request — ${selectedProductName}`);
      const body = encodeURIComponent(
        `Hi Sudhir,\n\n` +
        `I would like to purchase: ${selectedProductName} (${selectedProductPriceText()}).\n\n` +
        `Please send the payment link and I'll pay by UPI / card / PayPal.\n\n` +
        `My email address is the one this was sent from.`
      );
      window.location.href = `mailto:${config.contactEmail}?subject=${subject}&body=${body}`;
      productModal.classList.add('hidden');
    });
  }

  if (modalWhatsAppBtn) {
    modalWhatsAppBtn.addEventListener('click', () => {
      const msg = encodeURIComponent(`Hi Sudhir! I want to buy your digital product: "${selectedProductName}" (${selectedProductPriceText()}). Please share the download link!`);
      window.open(`https://wa.me/${config.whatsappNumber}?text=${msg}`, '_blank');
      productModal.classList.add('hidden');
    });
  }

  // 14. Inquiry Brief Generator & Dispatch (Email + WhatsApp + Instagram)
  const shootForm = document.getElementById('shootInquiryForm');
  const sendToEmailBtn = document.getElementById('sendToEmailBtn');
  const sendToWhatsAppBtn = document.getElementById('sendToWhatsAppBtn');
  const sendToInstagramBtn = document.getElementById('sendToInstagramBtn');
  const formSuccessToast = document.getElementById('formSuccessToast');
  const formSuccessToastText = formSuccessToast?.querySelector('span');
  const freeSampleOffer = document.getElementById('freeSampleOffer');

  if (config.freeSampleOfferEnabled && freeSampleOffer) {
    freeSampleOffer.classList.remove('hidden');
    freeSampleOffer.classList.add('flex');
  }

  const fieldVal = (id, fallback) => {
    const v = document.getElementById(id)?.value?.trim();
    return v || fallback;
  };

  const currentLeadSource = () => {
    if (window.LEAD_SOURCE) return window.LEAD_SOURCE;
    try {
      return sessionStorage.getItem('gp_lead_source') || 'direct';
    } catch (err) {
      return 'direct';
    }
  };

  const generateBriefText = () => {
    const name = fieldVal('clientName', 'Client');
    const contact = fieldVal('clientContact', 'Not provided');
    const email = fieldVal('clientEmail', 'Not provided');
    const type = document.querySelector('input[name="projectType"]:checked')?.value || 'AI Photoshoot Campaign';
    const deliverables = fieldVal('deliverableCount', '25 Photos + 2 AI Video Clips');
    const turnaround = fieldVal('turnaroundPreference', '24-48 Hours (Standard Production)');
    const details = fieldVal('projectDetails', 'Custom AI photoshoot campaign');

    return [
      'Hello Sudhir,',
      '',
      'I would like to book an AI production shoot. My brief:',
      '',
      `Client/Brand: ${name}`,
      `Contact (WhatsApp/IG): ${contact}`,
      `Email: ${email}`,
      `Production Scope: ${type}`,
      `Deliverables: ${deliverables}`,
      `Turnaround: ${turnaround}`,
      `How I found you: ${currentLeadSource()}`,
      '',
      'Vision & Notes:',
      details,
      '',
      'Please confirm availability and pricing. Thank you.',
    ].join('\n');
  };

  let toastTimer = null;
  const showToast = (msg) => {
    if (!formSuccessToast) return;
    if (formSuccessToastText) formSuccessToastText.innerHTML = msg;
    formSuccessToast.classList.remove('hidden');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => formSuccessToast.classList.add('hidden'), 8000);
  };

  const copyToClipboard = (text) => {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).catch(() => {});
    }
  };

  // If leadWebhook is configured, POST the lead so it lands in a sheet/CMS.
  // Otherwise fall back to a pre-filled mailto: so nothing is ever lost.
  const postLead = async (payload, brief) => {
    if (!config.leadWebhook) return false;
    try {
      const res = await fetch(config.leadWebhook, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...payload, brief, submittedAt: new Date().toISOString() }),
      });
      return res.ok;
    } catch (err) {
      console.warn('Lead webhook failed, falling back to mailto:', err);
      return false;
    }
  };

  const handleEmailSubmit = async (e) => {
    if (e) e.preventDefault();
    if (!shootForm || !shootForm.reportValidity()) return;

    const brief = generateBriefText();
    const payload = {
      name: fieldVal('clientName', ''),
      contact: fieldVal('clientContact', ''),
      email: fieldVal('clientEmail', ''),
      projectType: document.querySelector('input[name="projectType"]:checked')?.value || '',
      deliverables: fieldVal('deliverableCount', ''),
      turnaround: fieldVal('turnaroundPreference', ''),
      details: fieldVal('projectDetails', ''),
      leadSource: currentLeadSource(),
      page: window.location.href,
      referrer: document.referrer || '',
    };

    const stored = await postLead(payload, brief);
    copyToClipboard(brief);

    if (!stored) {
      const subject = encodeURIComponent(`New shoot brief — ${payload.name}`);
      const href = `mailto:${config.contactEmail}?subject=${subject}&body=${encodeURIComponent(brief)}`;
      window.location.href = href;
    }

    showToast(
      stored
        ? '<strong>Brief received!</strong> Sudhir will reply to your email shortly.'
        : '<strong>Brief ready in your email app.</strong> Hit send and Sudhir will reply shortly.'
    );
  };

  if (shootForm) {
    shootForm.addEventListener('submit', handleEmailSubmit);
  }

  if (sendToEmailBtn) {
    sendToEmailBtn.addEventListener('click', handleEmailSubmit);
  }

  const handleChannelAction = (channel) => {
    const brief = generateBriefText();
    copyToClipboard(brief);
    showToast('<strong>Brief copied to your clipboard.</strong> Paste it into the chat window that just opened.');
    setTimeout(() => {
      if (channel === 'whatsapp') {
        window.open(`https://wa.me/${config.whatsappNumber}?text=${encodeURIComponent(brief)}`, '_blank');
      } else {
        window.open(config.instagramUrl, '_blank');
      }
    }, 500);
  };

  if (sendToWhatsAppBtn) {
    sendToWhatsAppBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleChannelAction('whatsapp');
    });
  }

  if (sendToInstagramBtn) {
    sendToInstagramBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleChannelAction('instagram');
    });
  }

  // 15. FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    item.addEventListener('click', () => {
      const answer = item.querySelector('.faq-answer');
      const icon = item.querySelector('i');
      if (answer) answer.classList.toggle('hidden');
      if (icon) icon.classList.toggle('rotate-180');
    });
  });
});
