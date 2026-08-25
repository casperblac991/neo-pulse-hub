/* NEO PULSE HUB — personalized gift recommendations with transparent AI/API fallback. */
(() => {
  const $ = (id) => document.getElementById(id);
  const escapeHTML = (value) => String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
  const apiEndpoint = '/api/ai/recommend';
  const budgetLabels = { any: 'أي ميزانية', 50: 'أقل من 50 دولار', 100: '50 إلى 100 دولار', 200: '100 إلى 200 دولار', 500: '200 إلى 500 دولار', '500+': 'أكثر من 500 دولار' };
  const intentMap = {
    smartwatch: ['ساعة','رياضة','لياقة','صحة','جري','نوم','fitness','watch','sport'],
    earbuds: ['سماعة','موسيقى','صوت','بودكاست','headphone','earbud','audio'],
    gaming: ['ألعاب','لعب','gaming','game','بلايستيشن'],
    cameras: ['كاميرا','تصوير','فيديو','صورة','camera','photo'],
    'smart-home': ['منزل','بيت','إضاءة','مطبخ','home','alexa'],
    productivity: ['عمل','مكتب','دراسة','إنتاجية','تعلم','office','work','study'],
  };

  const setStatus = (type, message) => {
    const status = $('giftStatus');
    status.className = `form-status visible ${type}`;
    status.textContent = message;
  };
  const clearStatus = () => { const status = $('giftStatus'); status.className = 'form-status'; status.textContent = ''; };
  const normalize = (p) => ({ ...p, name: typeof p.name === 'object' ? p.name : { ar: p.name_ar || p.name || '', en: p.name_en || p.name || '' }, image: p.image || 'images/product-fallback.svg', price: Number(p.price) || 0 });
  const name = (p) => p.name?.ar || p.name?.en || p.name_ar || p.name_en || 'منتج ذكي';
  const description = (p) => p.description?.ar || p.description?.en || p.category_ar || 'خيار تقني من الكتالوج';
  const image = (p) => p.image || 'images/product-fallback.svg';
  const categoryTerms = (product) => `${product.category || ''} ${product.category_ar || ''} ${product.category_en || ''} ${name(product)} ${description(product)}`.toLowerCase();

  function maxBudget(value) { return value === 'any' ? Infinity : value === '500+' ? Infinity : Number(value) || Infinity; }
  function localRecommendations(products, interests, budget) {
    const tokens = interests.toLowerCase().split(/[،,\s]+/).map((item) => item.trim()).filter((item) => item.length > 1);
    const budgetLimit = maxBudget(budget);
    return products.map((product) => {
      const terms = categoryTerms(product);
      let score = Number(product.rating || 0) * 5;
      if (product.price <= budgetLimit) score += 24; else score -= Math.min(30, Math.ceil((product.price - budgetLimit) / 20));
      tokens.forEach((token) => { if (terms.includes(token)) score += 18; });
      Object.entries(intentMap).forEach(([category, hints]) => { if (product.category === category && hints.some((hint) => tokens.some((token) => token.includes(hint) || hint.includes(token)))) score += 15; });
      return { product, score };
    }).sort((a, b) => b.score - a.score).slice(0, 3).map((item) => item.product);
  }

  async function fetchCatalog() {
    const response = await fetch('./products.json?gift=20260825', { cache: 'no-store', headers: { Accept: 'application/json' } });
    if (!response.ok) throw new Error('catalog unavailable');
    const data = await response.json();
    if (!Array.isArray(data) || !data.length) throw new Error('empty catalog');
    return data.map(normalize);
  }
  async function askAI(query, recipient, interests, budget) {
    const response = await fetch(apiEndpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ query, recipient, interests, budget: maxBudget(budget) === Infinity ? null : maxBudget(budget) }) });
    if (!response.ok) throw new Error('AI service unavailable');
    const payload = await response.json();
    if (!payload.success || !Array.isArray(payload.data) || !payload.data.length) throw new Error('AI returned no recommendations');
    return { products: payload.data.map(normalize), reason: payload.reason || '', mode: payload.recommendation_mode || 'ai' };
  }
  function render(products, reason, mode, recipient, budget) {
    const results = $('giftResults'); const grid = $('resultsGrid');
    const label = mode === 'ai' ? 'توصية مخصصة بالذكاء الاصطناعي' : 'اقتراح ذكي من الكتالوج';
    const note = `<div class="recommendation-note"><strong>${label}</strong> · ${escapeHTML(reason || `اختيرت الخيارات بعد مواءمة الاهتمامات مع ${budgetLabels[budget] || 'الميزانية المحددة'}.`)}<br><small>ملف الهدية: ${escapeHTML(recipient)} · ${escapeHTML(budgetLabels[budget] || '')}</small></div>`;
    grid.innerHTML = note + products.map((product) => {
      const link = /^https:\/\//.test(product.affiliate_amazon || '') ? product.affiliate_amazon : `product-detail.html?id=${encodeURIComponent(product.id || '')}`;
      return `<article class="product-card"><img src="${escapeHTML(image(product))}" alt="${escapeHTML(name(product))}" loading="lazy" onerror="this.onerror=null;this.src='images/product-fallback.svg';this.classList.add('image-fallback')"><h3>${escapeHTML(name(product))}</h3><p>${escapeHTML(description(product))}</p><div class="price">$${Number(product.price || 0).toLocaleString()}</div><a href="${escapeHTML(link)}" target="_blank" rel="noopener noreferrer" class="btn-amazon">عرض المنتج</a></article>`;
    }).join('');
    results.style.display = 'block'; results.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  async function handleRecommendation() {
    const recipient = $('recipient').value.trim(); const interests = $('interests').value.trim(); const budget = $('budget').value;
    if (recipient.length < 2 || interests.length < 2) { setStatus('error', 'أدخل لمن الهدية واهتمامين على الأقل لنتمكن من تخصيص الاقتراحات.'); return; }
    const button = $('findGiftsBtn'); button.disabled = true; button.textContent = 'جارٍ تحليل التفضيلات…';
    setStatus('loading', 'نحلل الاهتمامات والميزانية ونطابقها مع المنتجات المتاحة الآن.');
    const query = `هدية إلى ${recipient}. الاهتمامات: ${interests}. الميزانية: ${budgetLabels[budget] || 'غير محددة'}.`;
    try {
      const ai = await askAI(query, recipient, interests, budget); render(ai.products, ai.reason, ai.mode, recipient, budget); setStatus('success', ai.mode === 'ai' ? 'تم إنشاء توصيات مخصصة بناءً على ملف الهدية.' : 'تم ترتيب التوصيات محلياً حسب التفضيلات والميزانية.');
    } catch (aiError) {
      try {
        const products = localRecommendations(await fetchCatalog(), interests, budget); if (!products.length) throw new Error('no candidates');
        render(products, 'خدمة الذكاء الاصطناعي غير متاحة الآن؛ استخدمنا مطابقة الاهتمامات والميزانية داخل الكتالوج بدلاً منها.', 'fallback', recipient, budget); setStatus('success', 'عرضنا أفضل الخيارات المتاحة الآن وفق اهتماماتك وميزانيتك.');
      } catch (catalogError) { setStatus('error', 'تعذر إنشاء التوصيات حالياً. أعد المحاولة بعد قليل أو انتقل إلى صفحة المنتجات.'); }
    } finally { button.disabled = false; button.textContent = 'حلّل التفضيلات واقترح هدايا'; }
  }
  const oldButton = $('findGiftsBtn'); const button = oldButton.cloneNode(true); oldButton.replaceWith(button); button.addEventListener('click', handleRecommendation); clearStatus();
})();
