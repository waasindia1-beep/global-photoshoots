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
  if (window.lucide) {
    window.lucide.createIcons();
  }

  // 2. Set Current Year
  const yearEl = document.getElementById('currentYear');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // 3. Currency Conversion Engine
  let activeCurrency = config.defaultCurrency || 'USD';

  const formatPrice = (usdAmount, currCode = activeCurrency) => {
    const curr = config.currencies[currCode] || config.currencies.USD;
    const converted = Math.round(usdAmount * curr.rate);
    if (currCode === 'INR') {
      return `${curr.symbol}${converted.toLocaleString('en-IN')}`;
    }
    return `${curr.symbol}${converted.toLocaleString()}`;
  };

  const updateAllPrices = () => {
    document.querySelectorAll('[data-usd-price]').forEach(el => {
      const usdVal = parseFloat(el.getAttribute('data-usd-price'));
      if (!isNaN(usdVal)) {
        el.textContent = formatPrice(usdVal, activeCurrency);
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

  // 4. Mobile Navigation Menu Toggle
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

  // 5. Interactive Before/After Split Slider
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

  // 6. Savings Calculator (Multi-Currency reactive)
  const photosRange = document.getElementById('photosRange');
  const videosRange = document.getElementById('videosRange');
  const photosCountDisplay = document.getElementById('photosCountDisplay');
  const videosCountDisplay = document.getElementById('videosCountDisplay');
  const traditionalCostDisplay = document.getElementById('traditionalCostDisplay');
  const aiCostDisplay = document.getElementById('aiCostDisplay');
  const netSavingsDisplay = document.getElementById('netSavingsDisplay');
  const daysSavedDisplay = document.getElementById('daysSavedDisplay');
  const speedButtons = document.querySelectorAll('.speed-toggle');

  let currentSpeed = 'standard';

  window.updateCalculator = () => {
    if (!photosRange || !videosRange) return;
    const photos = parseInt(photosRange.value, 10);
    const videos = parseInt(videosRange.value, 10);

    photosCountDisplay.textContent = `${photos} Photos`;
    videosCountDisplay.textContent = `${videos} ${videos === 1 ? 'Clip' : 'Clips'}`;

    const traditionalUsd = Math.round(4200 + (photos * 160) + (videos * 1400));
    let aiUsd = 120 + (photos * 16) + (videos * 80);
    if (currentSpeed === 'rush') aiUsd += 80;
    aiUsd = Math.round(aiUsd);

    const netSavingsUsd = traditionalUsd - aiUsd;
    const daysSaved = currentSpeed === 'rush' ? 24 : 21;

    if (traditionalCostDisplay) traditionalCostDisplay.textContent = formatPrice(traditionalUsd);
    if (aiCostDisplay) aiCostDisplay.textContent = formatPrice(aiUsd);
    if (netSavingsDisplay) netSavingsDisplay.textContent = `+${formatPrice(netSavingsUsd)}`;
    if (daysSavedDisplay) daysSavedDisplay.textContent = `~${daysSaved} Days Saved`;
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

  // 7. Portfolio Filters
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

  // 8. Portfolio Lightbox
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

  // 9. Digital Product Modal
  const productModal = document.getElementById('productModal');
  const closeModalBtn = document.getElementById('closeModalBtn');
  const modalProductTitle = document.getElementById('modalProductTitle');
  const modalProductPrice = document.getElementById('modalProductPrice');
  const modalSimulatePayBtn = document.getElementById('modalSimulatePayBtn');
  const modalWhatsAppBtn = document.getElementById('modalWhatsAppBtn');
  const digitalProductBtns = document.querySelectorAll('.digital-product-btn');

  let selectedProductName = '';
  let selectedProductUsd = 29;

  digitalProductBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      selectedProductName = btn.getAttribute('data-product') || 'Digital Asset';
      selectedProductUsd = parseFloat(btn.getAttribute('data-usd-price')) || 29;
      if (modalProductTitle && modalProductPrice && productModal) {
        modalProductTitle.textContent = selectedProductName;
        modalProductPrice.textContent = formatPrice(selectedProductUsd);
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

  if (modalSimulatePayBtn) {
    modalSimulatePayBtn.addEventListener('click', () => {
      alert(`Demo Checkout: Directing to payment for "${selectedProductName}" (${formatPrice(selectedProductUsd)}). To complete purchase immediately with instant download access, message Sudhir on Instagram or WhatsApp!`);
      window.open(config.instagramUrl, '_blank');
      productModal.classList.add('hidden');
    });
  }

  if (modalWhatsAppBtn) {
    modalWhatsAppBtn.addEventListener('click', () => {
      const msg = encodeURIComponent(`Hi Sudhir! I want to buy your digital product: "${selectedProductName}" (${formatPrice(selectedProductUsd)}). Please share the download link!`);
      window.open(`https://wa.me/${config.whatsappNumber}?text=${msg}`, '_blank');
      productModal.classList.add('hidden');
    });
  }

  // 10. Inquiry Brief Generator & Dual Dispatch (Instagram + WhatsApp)
  const shootForm = document.getElementById('shootInquiryForm');
  const sendToInstagramBtn = document.getElementById('sendToInstagramBtn');
  const sendToWhatsAppBtn = document.getElementById('sendToWhatsAppBtn');
  const formSuccessToast = document.getElementById('formSuccessToast');

  const generateBriefText = () => {
    const name = document.getElementById('clientName')?.value || 'Client';
    const contact = document.getElementById('clientContact')?.value || 'Not provided';
    const type = document.querySelector('input[name="projectType"]:checked')?.value || 'AI Photoshoot';
    const deliverables = document.getElementById('deliverableCount')?.value || '15-25 Photos';
    const turnaround = document.getElementById('turnaroundPreference')?.value || '48 Hours';
    const details = document.getElementById('projectDetails')?.value || 'Custom AI photoshoot campaign';

    return `Hello Sudhir (@global.photoshoots)! I would like to book an AI Production shoot:
- Client/Brand: ${name}
- Contact: ${contact}
- Production Scope: ${type}
- Deliverables: ${deliverables}
- Turnaround: ${turnaround}
- Vision & Notes: ${details}`;
  };

  const handleInquiryAction = (channel = 'instagram') => {
    const brief = generateBriefText();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(brief).catch(() => {});
    }

    if (formSuccessToast) {
      formSuccessToast.classList.remove('hidden');
      setTimeout(() => {
        formSuccessToast.classList.add('hidden');
      }, 7000);
    }

    setTimeout(() => {
      if (channel === 'whatsapp') {
        const encodedMsg = encodeURIComponent(brief);
        window.open(`https://wa.me/${config.whatsappNumber}?text=${encodedMsg}`, '_blank');
      } else {
        window.open(config.instagramUrl, '_blank');
      }
    }, 400);
  };

  if (sendToInstagramBtn) {
    sendToInstagramBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleInquiryAction('instagram');
    });
  }

  if (sendToWhatsAppBtn) {
    sendToWhatsAppBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleInquiryAction('whatsapp');
    });
  }

  if (shootForm) {
    shootForm.addEventListener('submit', (e) => {
      e.preventDefault();
      handleInquiryAction('instagram');
    });
  }

  // 11. FAQ Accordion
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
