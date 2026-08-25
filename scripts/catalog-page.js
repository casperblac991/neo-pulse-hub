/* NEO PULSE HUB — resilient catalog loader with visible loading and recovery states. */
(() => {
  const VERSION = '2026.08.25.catalog-resilient';
  let allProducts = [];
  let currentCategory = 'all';
  let searchTerm = '';
  let sortMode = 'featured';
  let currentLang = localStorage.getItem('nph_lang') || 'ar';

  const $ = (id) => document.getElementById(id);
  const text = (id, value) => { const el = $(id); if (el) el.textContent = value; };
  const copy = () => currentLang === 'en' ? {
    loadingTitle: 'Loading the catalog', loadingBody: 'We are bringing the latest products into the marketplace.',
    errorTitle: 'The catalog could not be loaded', errorBody: 'Please check your connection and try again. Your filters are ready once the catalog returns.', retry: 'Try again',
    empty: 'No matching products yet. Try another term or category.', visible: 'products', sourceNotice: 'Showing verified catalog data with local image fallbacks.'
  } : {
    loadingTitle: 'جارٍ تحميل الكتالوج', loadingBody: 'نحضّر أحدث المنتجات لعرضها في السوق.',
    errorTitle: 'تعذر تحميل الكتالوج', errorBody: 'تحقق من اتصالك ثم حاول مجدداً. ستصبح الفلاتر جاهزة فور عودة الكتالوج.', retry: 'إعادة المحاولة',
    empty: 'لا توجد منتجات مطابقة حالياً. جرّب كلمة أو فئة أخرى.', visible: 'منتج', sourceNotice: 'نعرض بيانات الكتالوج المتحققة مع بدائل صور محلية.'
  };

  const escapeHTML = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
  const localize = (value, lang = currentLang) => {
    if (value && typeof value === 'object' && !Array.isArray(value)) return value[lang] || value.ar || value.en || '';
    return value || '';
  };
  const normalize = (product) => ({
    ...product,
    id: product.id || '',
    name: typeof product.name === 'object' ? product.name : { ar: product.name_ar || product.name || '', en: product.name_en || product.name || '' },
    category_ar: product.category_ar || product.category || '',
    category_en: product.category_en || product.category || '',
    image: product.image || 'images/product-fallback.svg',
    price: Number(product.price) || 0,
    original_price: Number(product.original_price) || 0,
  });
  const supportedData = (payload) => Array.isArray(payload) ? payload : (Array.isArray(payload?.data) ? payload.data : []);
  const visualFor = (product) => window.NeoPulseVisuals?.get(product, currentLang) || { verified: false, src: 'images/product-fallback.svg', alt: localize(product.name), label: currentLang === 'en' ? 'Category visual' : 'صورة توضيحية للفئة' };

  function showStatus(state, detail = '') {
    const grid = $('productsGrid');
    if (!grid) return;
    const lang = copy();
    grid.setAttribute('aria-busy', state === 'loading' ? 'true' : 'false');
    if (state === 'loading') {
      text('toolbarCount', currentLang === 'en' ? 'Loading…' : 'جارٍ التحميل…');
      text('visibleCount', '—');
      grid.innerHTML = '<div class="product-skeleton"></div><div class="product-skeleton"></div><div class="product-skeleton"></div>';
      return;
    }
    if (state === 'error') {
      grid.innerHTML = `<section class="catalog-status" role="alert"><div class="catalog-status-inner"><div class="catalog-status-icon">!</div><h3>${lang.errorTitle}</h3><p>${escapeHTML(detail || lang.errorBody)}</p><button type="button" class="status-retry" id="retryCatalog">↻ ${lang.retry}</button></div></section>`;
      $('retryCatalog')?.addEventListener('click', fetchProducts);
    }
  }

  async function loadFrom(url) {
    const response = await fetch(url, { cache: 'no-store', headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = supportedData(await response.json());
    if (!data.length) throw new Error('empty catalog');
    return data.map(normalize);
  }

  async function fetchProducts() {
    showStatus('loading');
    const sources = [`./products.json?v=${VERSION}`, `/api/products?limit=100`];
    let lastError = null;
    for (const source of sources) {
      try {
        allProducts = await loadFrom(source);
        const requestedCategory = new URLSearchParams(window.location.search).get('category');
        if (requestedCategory && allProducts.some((product) => product.category === requestedCategory)) {
          currentCategory = requestedCategory;
          document.querySelectorAll('.category-btn').forEach((item) => item.classList.toggle('active', item.getAttribute('onclick')?.includes(`'${requestedCategory}'`)));
        }
        text('totalMetric', allProducts.length.toLocaleString());
        renderProducts();
        return;
      } catch (error) { lastError = error; }
    }
    console.error('Catalog loading failed:', lastError);
    text('totalMetric', '—');
    showStatus('error');
  }

  function formatPrice(product, original = false) {
    const currency = localStorage.getItem('nph_currency') || 'USD';
    const symbols = { USD: '$', SAR: 'ر.س', AED: 'د.إ', EUR: '€' };
    const rates = { USD: 1, SAR: 3.75, AED: 3.67, EUR: .92 };
    let value = original ? product.original_price : product.price;
    if (!value) return '';
    if (!original && product.global_prices?.[currency]) value = product.global_prices[currency];
    else value = (Number(value) * (rates[currency] || 1)).toFixed(2);
    return `${symbols[currency]} ${value}`;
  }

  function renderProducts() {
    const grid = $('productsGrid');
    if (!grid) return;
    const lang = copy();
    let filtered = allProducts.filter((product) => {
      const name = localize(product.name).toLowerCase();
      const terms = `${name} ${localize(product.name, 'ar')} ${localize(product.name, 'en')} ${product.category || ''} ${product.category_ar || ''}`.toLowerCase();
      return (currentCategory === 'all' || product.category === currentCategory) && (!searchTerm || terms.includes(searchTerm.toLowerCase()));
    });
    if (sortMode === 'rating') filtered.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    if (sortMode === 'price-low') filtered.sort((a, b) => a.price - b.price);
    if (sortMode === 'price-high') filtered.sort((a, b) => b.price - a.price);
    text('visibleCount', `${filtered.length} ${lang.visible}`);
    text('toolbarCount', `${filtered.length} ${currentLang === 'en' ? 'of' : 'من'} ${allProducts.length}`);
    grid.setAttribute('aria-busy', 'false');
    if (!filtered.length) {
      grid.innerHTML = `<section class="catalog-status"><div class="catalog-status-inner"><div class="catalog-status-icon">⌕</div><h3>${lang.empty}</h3><p>${currentLang === 'en' ? 'Clear one of the active filters to see more products.' : 'أزل أحد عوامل التصفية الحالية لعرض خيارات أكثر.'}</p></div></section>`;
      return;
    }
    const notice = `<div class="catalog-notice" role="status">● ${lang.sourceNotice}</div>`;
    grid.innerHTML = notice + filtered.map((product) => {
      const name = escapeHTML(localize(product.name));
      const category = escapeHTML(currentLang === 'en' ? product.category_en : product.category_ar);
      const badge = escapeHTML(localize(product.badge));
      const specs = Object.entries(localize(product.specifications) || localize(product.specs) || {}).slice(0, 3).map(([key, value]) => `<span>${escapeHTML(key)}: ${escapeHTML(localize(value))}</span>`).join('');
      const original = product.original_price > product.price ? `<span class="original-price">${formatPrice(product, true)}</span>` : '';
      const visual = visualFor(product);
      const affiliate = /^https:\/\//.test(product.affiliate_amazon || '') ? product.affiliate_amazon : `product-detail.html?id=${encodeURIComponent(product.id)}`;
      return `<article class="product-card"><div class="product-image"><img src="${escapeHTML(visual.src)}" alt="${escapeHTML(visual.alt || name)}" loading="lazy">${visual.label ? `<span class="visual-status">${escapeHTML(visual.label)}</span>` : ''}${badge ? `<span class="badge">${badge}</span>` : ''}</div><div class="product-info"><div class="product-category">${category}</div><h3 class="product-name">${name}</h3><div class="product-rating"><span class="stars" aria-hidden="true">★★★★★</span><span>${escapeHTML(product.rating || '—')}/5</span>${product.reviews ? `<span>(${Number(product.reviews).toLocaleString()})</span>` : ''}</div><div class="price-row"><span class="price">${formatPrice(product)}</span>${original}</div>${specs ? `<div class="spec-preview">${specs}</div>` : ''}<div class="card-actions"><a href="product-detail.html?id=${encodeURIComponent(product.id)}" class="details-btn">${currentLang === 'en' ? 'Details' : 'التفاصيل'}</a><a href="${escapeHTML(affiliate)}" target="_blank" rel="noopener noreferrer" class="buy-btn">${currentLang === 'en' ? 'Buy now' : 'اشترِ الآن'}</a></div></div></article>`;
    }).join('');
  }

  window.updateSearch = (value) => { searchTerm = value.trim(); renderProducts(); };
  window.sortCatalog = (mode) => { sortMode = mode; renderProducts(); };
  window.filterCategory = (category, button) => { currentCategory = category; document.querySelectorAll('.category-btn').forEach((item) => item.classList.remove('active')); button?.classList.add('active'); renderProducts(); };
  window.changeCurrency = (currency) => { localStorage.setItem('nph_currency', currency); renderProducts(); };
  window.switchLanguage = (lang) => { currentLang = lang; localStorage.setItem('nph_lang', lang); document.documentElement.lang = lang; document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr'; $('langAr')?.classList.toggle('active', lang === 'ar'); $('langEn')?.classList.toggle('active', lang === 'en'); text('pageTitle', lang === 'en' ? 'Global Tech Marketplace' : 'سوق التقنية العالمي'); text('pageSub', lang === 'en' ? 'Best smart products from trusted marketplaces in one place' : 'أفضل المنتجات الذكية من المتاجر الموثوقة في مكان واحد'); text('heroKicker', lang === 'en' ? 'Global marketplace is live' : 'متجر عالمي يعمل الآن'); renderProducts(); };
  window.onload = () => { const currency = localStorage.getItem('nph_currency') || 'USD'; document.querySelector('.currency-select').value = currency; window.switchLanguage(localStorage.getItem('nph_lang') || 'ar'); fetchProducts(); };
})();
