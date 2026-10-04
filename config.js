// Global Photoshoots - Central Configuration File
// Edit your contact details and social links here anytime!

const STUDIO_CONFIG = {
  // Brand & Founder
  studioName: "Global Photoshoots",
  founderName: "Sudhir Kumar Solanki",
  
  // Social & Direct Contact Links
  instagramHandle: "@global.photoshoots",
  instagramUrl: "https://www.instagram.com/global.photoshoots/#",
  
  // WhatsApp Contact (Enter your phone number with country code, e.g. "917557575514")
  whatsappNumber: "917557575514", 
  whatsappPrefilledMessage: "Hi Sudhir! I am interested in booking an AI Photoshoot / Video production campaign with Global Photoshoots.",

  // Email & Scheduling
  contactEmail: "sudhir@globalphotoshoots.com",
  calendlyUrl: "https://calendly.com", // Replace with your personal Calendly or Cal.com booking link

  // Physical business address. Shown in the site footer AND required in the
  // footer of every cold email (CAN-SPAM requires a valid postal address).
  // ⚠️ REPLACE THIS. Google Business Profile and Justdial both verify the address
  // and will reject or suspend a listing that does not match your real premises.
  // Put the address you can actually receive mail at, and keep it consistent
  // across the site, GBP, Justdial and IndiaMART.
  // Set 2026-10-04 from the founder's confirmed details.
  businessAddress: "5B/23 Vishnu Garden, New Delhi 110018, India",

  // City shown in local SEO copy and structured data. Must match the address above.
  city: "New Delhi",
  region: "Delhi",

  // Lead capture. Leave blank to fall back to a pre-filled mailto: (works with
  // zero setup). To get leads stored in a sheet/CMS instead, paste an endpoint
  // that accepts a JSON POST, e.g. Formspree or a Google Apps Script web app URL.
  leadWebhook: "",

  // Plausible Analytics: add your site domain to start collecting traffic.
  // Leave blank to disable (no third-party scripts are loaded).
  analyticsDomain: "",

  // Risk reversal shown in the booking form. Free sample frame costs almost
  // nothing to generate and is the single biggest converter for cold leads.
  // Turn this off if you do not want to promise it.
  freeSampleOfferEnabled: true,

  // Supported Currencies & Exchange Rates (relative to USD)
  defaultCurrency: "INR",
  currencies: {
    USD: { symbol: "$", rate: 1, position: "prefix" },
    INR: { symbol: "₹", rate: 85, position: "prefix" },
    EUR: { symbol: "€", rate: 0.92, position: "prefix" },
    GBP: { symbol: "£", rate: 0.78, position: "prefix" }
  }
};

window.STUDIO_CONFIG = STUDIO_CONFIG;
