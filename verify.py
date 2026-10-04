with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

required_ids = [
    'currencySelector', 'mobileMenuBtn', 'mobileMenu', 'beforeAfterSlider',
    'sliderBeforeContainer', 'sliderHandle', 'photosRange', 'videosRange',
    'photosCountDisplay', 'videosCountDisplay', 'traditionalCostDisplay',
    'aiCostDisplay', 'netSavingsDisplay', 'daysSavedDisplay', 'lightboxModal',
    'closeLightboxBtn', 'lightboxImg', 'lightboxTitle', 'lightboxCategory',
    'lightboxDescription', 'productModal', 'closeModalBtn', 'modalProductTitle',
    'modalProductPrice', 'modalEmailBtn', 'modalWhatsAppBtn',
    'shootInquiryForm', 'sendToInstagramBtn', 'sendToWhatsAppBtn',
    'formSuccessToast', 'currentYear'
]

missing = [i for i in required_ids if f'id="{i}"' not in content]
print(f'Total HTML length: {len(content)} chars')
print(f'Missing IDs count: {len(missing)}')
if missing:
    print('Missing IDs:', missing)
else:
    print('ALL required DOM IDs are present!')

# Check data attributes
usd_prices = content.count('data-usd-price')
print(f'data-usd-price occurrences: {usd_prices}')
filter_btns = content.count('filter-btn')
print(f'filter-btn occurrences: {filter_btns}')
portfolio_items = content.count('portfolio-item')
print(f'portfolio-item occurrences: {portfolio_items}')
faq_items = content.count('faq-item')
print(f'faq-item occurrences: {faq_items}')
digital_btns = content.count('digital-product-btn')
print(f'digital-product-btn occurrences: {digital_btns}')
