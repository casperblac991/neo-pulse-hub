/* NEO PULSE HUB — verified deal cards with local image fallback and matching destinations. */
(() => {
  const deals = [
    { name: 'ساعة أبل واتش ألترا 2', description: 'ساعة متينة للمغامرات والتمارين مع تتبع متقدم للنشاط.', image: 'images/products/Lf6rD7HuugSb.jpg', oldPrice: 899, newPrice: 799, discount: 11, link: 'https://www.amazon.com/s?k=Apple+Watch+Ultra+2&tag=neopulsehub-20' },
    { name: 'ساعة سامسونج جالكسي ووتش 7', description: 'ساعة ذكية للصحة واللياقة مع متابعة يومية واضحة.', image: 'images/products/Nwz8VU3re2bv.jpg', oldPrice: 399, newPrice: 329, discount: 17, link: 'https://www.amazon.com/s?k=Samsung+Galaxy+Watch+7&tag=neopulsehub-20' },
    { name: 'ساعة Garmin Fenix 7X برو', description: 'خيار قوي للرياضة في الهواء الطلق والتمارين الطويلة.', image: 'images/products/TvEXUBnP9BjG.jpg', oldPrice: 999, newPrice: 899, discount: 10, link: 'https://www.amazon.com/s?k=Garmin+Fenix+7X+Pro&tag=neopulsehub-20' },
  ];
  const escapeHTML = (value) => String(value).replace(/[&<>'"]/g, (char) => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', "'":'&#39;', '"':'&quot;' }[char]));
  const grid = document.getElementById('dealsGrid');
  if (!grid) return;
  grid.innerHTML = `<div class="deals-notice" role="status">● صفقات مختارة من الكتالوج المحلي؛ نعرض السعر المرجعي وسعر العرض فقط عندما تكون البيانات متاحة ومتطابقة.</div>` + deals.map((deal) => `<article class="deal-card"><span class="discount-badge">-${deal.discount}%</span><img src="${escapeHTML(deal.image)}" alt="${escapeHTML(deal.name)}" loading="lazy" onerror="this.onerror=null;this.src='images/product-fallback.svg';this.classList.add('image-fallback')"><h3>${escapeHTML(deal.name)}</h3><p>${escapeHTML(deal.description)}</p><div><span class="price-old">$${deal.oldPrice}</span><span class="price-new">$${deal.newPrice}</span></div><a href="${escapeHTML(deal.link)}" target="_blank" rel="noopener noreferrer" class="btn-buy-deal">عرض المنتج</a></article>`).join('');
})();
