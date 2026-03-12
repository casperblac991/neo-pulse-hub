// NEO PULSE HUB — Service Worker v1.0
var CACHE = 'nph-v1';
var STATIC = [
  '/',
  '/index.html',
  '/products.html',
  '/product-detail.html',
  '/checkout.html',
  '/thanks.html',
  '/track.html',
  '/about.html',
  '/contact.html',
  '/404.html',
  '/manifest.json'
];

self.addEventListener('install', function(e) {
  e.waitUntil(
    caches.open(CACHE).then(function(cache) {
      return cache.addAll(STATIC);
    }).catch(function() {})
  );
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE; })
            .map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  if (e.request.method !== 'GET') return;
  var url = e.request.url;
  // لا تعترض طلبات API خارجية
  if (url.indexOf('googleapis') > -1 || url.indexOf('googletagmanager') > -1 || url.indexOf('paypal') > -1) return;

  e.respondWith(
    caches.match(e.request).then(function(cached) {
      var fetchPromise = fetch(e.request).then(function(res) {
        if (res && res.status === 200 && res.type === 'basic') {
          var clone = res.clone();
          caches.open(CACHE).then(function(cache) { cache.put(e.request, clone); });
        }
        return res;
      }).catch(function() { return null; });

      return cached || fetchPromise || caches.match('/404.html');
    })
  );
});
