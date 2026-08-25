/* NEO PULSE HUB — show a product photo only when the catalog ships a verified local asset. */
(() => {
  const categories = {
    smartwatch: { icon: '⌚', ar: 'ساعات ذكية', en: 'Smart watches' },
    earbuds: { icon: '🎧', ar: 'سماعات لاسلكية', en: 'Wireless audio' },
    headphones: { icon: '🎧', ar: 'سماعات رأس', en: 'Headphones' },
    'smart-home': { icon: '⌂', ar: 'منزل ذكي', en: 'Smart home' },
    health: { icon: '♥', ar: 'صحة ذكية', en: 'Smart health' },
    productivity: { icon: '▣', ar: 'إنتاجية', en: 'Productivity' },
    gaming: { icon: '◉', ar: 'ألعاب', en: 'Gaming' },
    cameras: { icon: '◉', ar: 'كاميرات', en: 'Cameras' },
    'smart-glasses': { icon: '◒', ar: 'نظارات ذكية', en: 'Smart glasses' },
    accessories: { icon: '◇', ar: 'ملحقات', en: 'Accessories' },
    kitchen: { icon: '◍', ar: 'مطبخ ذكي', en: 'Smart kitchen' },
    sports: { icon: '◈', ar: 'رياضة', en: 'Sports' },
    car: { icon: '▱', ar: 'سيارة ذكية', en: 'Smart car' },
    kids: { icon: '★', ar: 'تقنية للأطفال', en: 'Kids tech' },
  };

  const escape = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  const localizedName = (product, lang) => typeof product?.name === 'object' ? (product.name[lang] || product.name.ar || product.name.en || '') : (product?.name_ar || product?.name || '');
  const isVerifiedLocal = (product) => /^images\/products\/[\w.-]+\.(?:png|jpe?g|webp)$/i.test(String(product?.image || ''));
  const category = (product, lang = 'ar') => categories[product?.category] || { icon: '✦', ar: product?.category_ar || 'تقنية مختارة', en: product?.category_en || 'Curated tech' };

  function categoryVisual(product, lang = 'ar') {
    const meta = category(product, lang);
    const label = lang === 'en' ? meta.en : meta.ar;
    const note = lang === 'en' ? 'Category visual' : 'صورة توضيحية للفئة';
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800" role="img" aria-label="${escape(label)}"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#12385a"/><stop offset="1" stop-color="#0b1024"/></linearGradient><radialGradient id="r"><stop stop-color="#40d9ff" stop-opacity=".36"/><stop offset="1" stop-color="#40d9ff" stop-opacity="0"/></radialGradient></defs><rect width="800" height="800" fill="url(#g)"/><circle cx="610" cy="160" r="270" fill="url(#r)"/><rect x="72" y="72" width="656" height="656" rx="48" fill="none" stroke="#60a5fa" stroke-opacity=".38" stroke-width="3"/><text x="400" y="360" text-anchor="middle" font-family="Arial, sans-serif" font-size="176" fill="#dff8ff">${meta.icon}</text><text x="400" y="510" text-anchor="middle" font-family="Arial, sans-serif" font-size="42" fill="#dbeafe">${escape(label)}</text><text x="400" y="575" text-anchor="middle" font-family="Arial, sans-serif" font-size="28" fill="#7dd3fc">${escape(note)}</text></svg>`;
    return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`;
  }

  function get(product, lang = document.documentElement.lang || 'ar') {
    const verified = isVerifiedLocal(product);
    return {
      verified,
      src: verified ? product.image : categoryVisual(product, lang),
      alt: verified ? localizedName(product, lang) : `${localizedName(product, lang)} — ${lang === 'en' ? 'category visual' : 'صورة توضيحية للفئة'}`,
      label: verified ? '' : (lang === 'en' ? 'Category visual — product photo pending verification' : 'صورة الفئة — صورة المنتج قيد التحقق'),
    };
  }

  window.NeoPulseVisuals = { get, isVerifiedLocal, localizedName };
})();
