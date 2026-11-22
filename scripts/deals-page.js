/* NEO PULSE HUB — product picks without unverified price claims. */
(() => {
  'use strict';

  const language = document.documentElement.lang === 'en' ? 'en' : 'ar';
  const copy = {
    ar: {
      title: 'اختيارات تقنية تستحق التصفح',
      intro: 'استكشف هذه المنتجات عبر المتجر. الأسعار والتوفر يحددهما البائع؛ تحقّق من التفاصيل قبل الشراء.',
      notice: 'هذه اختيارات منتجات وليست عروضًا مؤكدة. السعر والتوفر قد يتغيران لدى البائع.',
      visit: 'تحقق من السعر لدى المتجر'
    },
    en: {
      title: 'Technology picks to explore',
      intro: 'Explore these products at the retailer. The seller sets prices and availability; check the details before buying.',
      notice: 'These are product picks, not verified deals. Price and availability may change at the retailer.',
      visit: 'Check price at retailer'
    }
  }[language];

  const products = [
    {
      name: language === 'en' ? 'Apple Watch Ultra 2' : 'ساعة أبل واتش ألترا 2',
      description: language === 'en' ? 'A rugged smartwatch for outdoor activity and training.' : 'ساعة متينة للأنشطة الخارجية والتمارين.',
      image: 'images/products/Lf6rD7HuugSb.jpg',
      link: 'https://www.amazon.com/s?k=Apple+Watch+Ultra+2&tag=neopulsehub09-20'
    },
    {
      name: language === 'en' ? 'Samsung Galaxy Watch 7' : 'ساعة سامسونج جالكسي ووتش 7',
      description: language === 'en' ? 'A smartwatch with health and fitness tracking features.' : 'ساعة ذكية بميزات لمتابعة الصحة واللياقة.',
      image: 'images/products/Nwz8VU3re2bv.jpg',
      link: 'https://www.amazon.com/s?k=Samsung+Galaxy+Watch+7&tag=neopulsehub09-20'
    },
    {
      name: language === 'en' ? 'Garmin Fenix 7X Pro' : 'ساعة Garmin Fenix 7X برو',
      description: language === 'en' ? 'A sports watch designed for outdoor use and long workouts.' : 'ساعة رياضية للأنشطة الخارجية والتمارين الطويلة.',
      image: 'images/products/TvEXUBnP9BjG.jpg',
      link: 'https://www.amazon.com/s?k=Garmin+Fenix+7X+Pro&tag=neopulsehub09-20'
    }
  ];

  const escapeHTML = (value) => String(value).replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[char]));

  const grid = document.getElementById('dealsGrid');
  if (!grid) return;

  if (typeof countdownInterval !== 'undefined') clearInterval(countdownInterval);
  document.querySelector('.countdown-timer')?.remove();
  const heading = document.querySelector('.deals-hero h1');
  const intro = document.querySelector('.deals-hero p');
  if (heading) heading.textContent = copy.title;
  if (intro) intro.textContent = copy.intro;
  document.title = `${copy.title} | NEO PULSE HUB`;

  const notice = `<div class="deals-notice" role="status">${escapeHTML(copy.notice)}</div>`;
  const cards = products.map((product) => {
    const visual = window.NeoPulseVisuals?.get(product, language) || { src: 'images/product-fallback.svg', alt: product.name };
    return `<article class="deal-card"><img src="${escapeHTML(visual.src)}" alt="${escapeHTML(visual.alt)}" loading="lazy">${visual.label ? `<small class="deal-visual-note">${escapeHTML(visual.label)}</small>` : ''}<h3>${escapeHTML(product.name)}</h3><p>${escapeHTML(product.description)}</p><a href="${escapeHTML(product.link)}" target="_blank" rel="noopener noreferrer" class="btn-buy-deal">${escapeHTML(copy.visit)}</a></article>`;
  }).join('');

  grid.innerHTML = notice + cards;
})();
