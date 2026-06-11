const CACHE_NAME = 'scrollguru-v1';

self.addEventListener('install', (e) => {
  self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
  // PWA ko active rakhne ke liye basic fetch handler
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request);
    })
  );
});