/**
 * NEO PULSE HUB — Affiliate Link Tracker
 * Records affiliate clicks & estimated revenue attribution in localStorage.
 * Zero external services, zero PII, works offline. ~1KB.
 * Usage (on any page): <script src="scripts/affiliate-tracker.js" defer></script>
 */
(function () {
  'use strict';
  var STORAGE_KEY = 'nph_affiliate_log_v1';
  var NETWORKS = [
    { id: 'amazon', match: 'amazon.com', tagParam: 'tag', tag: 'neopulsehub09-20' },
    { id: 'aliexpress', match: 'aliexpress.com' },
    { id: 'ebay', match: 'ebay.com' },
    { id: 'walmart', match: 'walmart.com' },
    { id: 'banggood', match: 'banggood.com' }
  ];

  function detectNetwork(url) {
    var lower = String(url || '').toLowerCase();
    for (var i = 0; i < NETWORKS.length; i++) {
      if (lower.indexOf(NETWORKS[i].match) !== -1) return NETWORKS[i].id;
    }
    return 'other';
  }

  function readLog() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{"clicks":[],"daily":{}}'); }
    catch (e) { return { clicks: [], daily: {} }; }
  }

  function writeLog(log) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(log)); }
    catch (e) { /* storage full — ignore */ }
  }

  document.addEventListener('click', function (ev) {
    var a = ev.target && ev.target.closest ? ev.target.closest('a[href]') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var network = detectNetwork(href);
    if (network === 'other') return;

    var log = readLog();
    var today = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    var page = location.pathname.split('/').pop() || 'index';

    log.clicks.push({
      network: network,
      page: page,
      date: today,
      ts: Date.now()
    });
    // Keep only last 500 clicks to stay within localStorage limits
    if (log.clicks.length > 500) log.clicks = log.clicks.slice(-500);

    log.daily[today] = (log.daily[today] || 0) + 1;

    // Aggregate counts per network for quick admin view
    log.byNetwork = log.byNetwork || {};
    log.byNetwork[network] = (log.byNetwork[network] || 0) + 1;

    writeLog(log);
  }, true); // capture phase so it fires before any navigation

  // Expose a tiny admin helper: window.NPH_AFFILIATE_STATS()
  window.NPH_AFFILIATE_STATS = function () {
    var log = readLog();
    return {
      totalClicks: log.clicks.length,
      clicksByNetwork: log.byNetwork || {},
      clicksByDay: log.daily || {},
      lastClicks: log.clicks.slice(-10)
    };
  };
})();

/**
 * Compatibility shim: some pages (index.html) read `product.affiliate_ali`
 * while products.json stores the link as `affiliate_aliexpress`, so the
 * AliExpress compare button never rendered. This runs via defer before any
 * product fetch, and normalizes fetched product JSON so both names exist.
 * Remove this block once all pages read affiliate_aliexpress directly.
 */
(function () {
  'use strict';
  if (typeof window.fetch !== 'function') return;
  var nativeFetch = window.fetch.bind(window);

  window.fetch = function (input, init) {
    return nativeFetch(input, init).then(function (response) {
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      if (url.indexOf('products.json') === -1 && url.indexOf('/api/products') === -1) {
        return response;
      }
      var originalJson = response.json.bind(response);
      var parsed = null;
      response.json = function () {
        if (!parsed) {
          parsed = originalJson().then(function (data) {
            if (Array.isArray(data)) {
              for (var i = 0; i < data.length; i++) {
                var p = data[i];
                if (p && typeof p === 'object' && p.affiliate_aliexpress && !p.affiliate_ali) {
                  p.affiliate_ali = p.affiliate_aliexpress;
                }
              }
            }
            return data;
          });
        }
        return parsed;
      };
      return response;
    });
  };
})();

/** Keep homepage claims aligned with observable catalog data. */
(function () {
  'use strict';
  var path = window.location.pathname;
  var isHome = path === '/' || /\/index\.html$/.test(path);
  var isContact = /\/contact\.html$/.test(path);
  if (!isHome && !isContact) return;

  function patchTranslations(patches) {
    try {
      if (typeof T === 'undefined') return;
      Object.keys(patches).forEach(function (language) {
        if (T[language]) Object.assign(T[language], patches[language]);
      });
    } catch (e) { /* Leave the page usable if a translation table is unavailable. */ }
  }

  if (isHome) {
    patchTranslations({
      ar: {
        hero_badge: 'منتجات تقنية ذكية مختارة',
        hero_desc: 'تصفّح منتجات التقنية الذكية عبر روابط المتاجر. تحقّق من السعر والتوفر لدى البائع قبل الشراء.',
        growth_title: 'كتالوج المنتجات',
        growth_products: 'منتجات في الكتالوج',
        products_sub: 'استكشف المنتجات عبر صفحات المتاجر، وتحقق من السعر والتوفر قبل الشراء.',
        f1t: 'تفاصيل الشراء لدى البائع',
        f1d: 'تحقق من معلومات الضمان وسياسة الإرجاع لدى البائع قبل الشراء.',
        f2t: 'تصفح الخيارات',
        f2d: 'استكشف مجموعة من المنتجات التقنية عبر روابط المتاجر.',
        f4t: 'الشحن حسب البائع',
        f4d: 'تختلف خيارات الشحن والتكلفة ومدة التسليم حسب المنتج وموقعك والبائع.',
        f6t: 'معلومات المنتج',
        f6d: 'تحقق من السعر والتوفر ومواصفات المنتج مباشرة لدى البائع.',
        footer_desc: 'استكشف منتجات التقنية الذكية عبر روابط المتاجر، وتحقق من التفاصيل لدى البائع قبل الشراء.'
      },
      en: {
        hero_badge: 'Selected smart technology products',
        hero_desc: 'Browse smart-tech products through retailer links. Check current price and availability with the seller before buying.',
        growth_title: 'Product catalog',
        growth_products: 'products in the catalog',
        products_sub: 'Explore products through retailer pages and check price and availability before buying.',
        f1t: 'Seller purchase details',
        f1d: 'Check warranty information and the seller’s return policy before buying.',
        f2t: 'Browse options',
        f2d: 'Explore a selection of technology products through retailer links.',
        f4t: 'Shipping depends on the seller',
        f4d: 'Shipping options, cost and delivery time vary by product, location and seller.',
        f6t: 'Product information',
        f6d: 'Check price, availability and product specifications directly with the seller.',
        footer_desc: 'Explore smart-tech products through retailer links and check details with the seller before buying.'
      }
    });

    if (typeof updateTranslations === 'function') updateTranslations();
    var status = document.getElementById('growthCycleAt');
    if (status) status.textContent = document.documentElement.lang === 'en' ? 'Checking catalog…' : 'جارٍ فحص الكتالوج…';
    var dataSource = document.getElementById('liveDataSource');
    if (dataSource) dataSource.textContent = 'JSON';
    var unsupportedStats = document.querySelector('.hero-stats');
    if (unsupportedStats) unsupportedStats.hidden = true;

    document.querySelectorAll('script[type="application/ld+json"]').forEach(function (schema) {
      try {
        var data = JSON.parse(schema.textContent || 'null');
        if (data && data['@type'] === 'ItemList') {
          schema.remove();
        } else if (data && data['@type'] === 'WebSite' && data.potentialAction) {
          delete data.potentialAction;
          schema.textContent = JSON.stringify(data);
        }
      } catch (e) { /* Keep unrelated structured data unchanged. */ }
    });

    document.querySelectorAll('a[href="privacy.html#affiliate"]').forEach(function (link) {
      link.setAttribute('href', '/affiliate-disclosure.html');
    });
  }

  if (isContact) {
    patchTranslations({
      ar: {
        btn_send: 'فتح مسودة البريد الإلكتروني',
        toast_ok: 'إذا فُتح تطبيق البريد، أرسل الرسالة منه لإكمال الإرسال.',
        toast_err: 'أدخل اسمًا وبريدًا صحيحًا ورسالة قبل المتابعة.'
      },
      en: {
        btn_send: 'Open email draft',
        toast_ok: 'If your email app opens, send the draft there to complete delivery.',
        toast_err: 'Enter your name, a valid email address and a message to continue.'
      }
    });

    window.sendMessage = function () {
      var name = document.getElementById('inp_name').value.trim();
      var email = document.getElementById('inp_email').value.trim();
      var subjectInput = document.getElementById('inp_subject').value.trim();
      var message = document.getElementById('inp_message').value.trim();
      var language = document.documentElement.lang === 'en' ? 'en' : 'ar';
      var messages = {
        ar: {
          invalid: 'أدخل اسمًا وبريدًا صحيحًا ورسالة قبل المتابعة.',
          tooLong: 'اختصر الرسالة إلى 4000 حرف أو أقل لفتحها في تطبيق البريد.',
          opened: 'إذا فُتح تطبيق البريد، أرسل الرسالة منه لإكمال الإرسال.',
          subject: 'رسالة من موقع NEO PULSE HUB'
        },
        en: {
          invalid: 'Enter your name, a valid email address and a message to continue.',
          tooLong: 'Shorten the message to 4000 characters or fewer to open it in your email app.',
          opened: 'If your email app opens, send the draft there to complete delivery.',
          subject: 'Message from NEO PULSE HUB'
        }
      };
      if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !message) {
        if (typeof window.showToast === 'function') window.showToast('⚠️', messages[language].invalid);
        return;
      }
      if (message.length > 4000) {
        if (typeof window.showToast === 'function') window.showToast('⚠️', messages[language].tooLong);
        return;
      }
      var subject = subjectInput || messages[language].subject;
      var body = language === 'en'
        ? 'Name: ' + name + '\nEmail: ' + email + '\n\n' + message
        : 'الاسم: ' + name + '\nالبريد الإلكتروني: ' + email + '\n\n' + message;
      var mailto = 'mailto:Saidchaik@gmail.com?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      if (typeof window.showToast === 'function') window.showToast('📧', messages[language].opened);
      window.location.href = mailto;
    };
  }
})();
