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

  // Supported Currencies & Exchange Rates (relative to USD)
  defaultCurrency: "USD",
  currencies: {
    USD: { symbol: "$", rate: 1, position: "prefix" },
    INR: { symbol: "₹", rate: 85, position: "prefix" },
    EUR: { symbol: "€", rate: 0.92, position: "prefix" },
    GBP: { symbol: "£", rate: 0.78, position: "prefix" }
  }
};

window.STUDIO_CONFIG = STUDIO_CONFIG;
