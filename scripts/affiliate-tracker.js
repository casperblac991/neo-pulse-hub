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
