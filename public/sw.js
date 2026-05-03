const CACHE_NAME = 'marlish-ai-v3';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  // Model cache is handled via IndexedDB natively by Transformers.js
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      // Don't fail install if one asset fails
      return Promise.allSettled(
        STATIC_ASSETS.map((url) => {
          return cache.add(url).catch((err) => {
            console.warn(`[SW] Failed to cache ${url}:`, err);
          });
        })
      );
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  // We only cache GET requests
  if (request.method !== 'GET') return;

  // Next.js dev server requests or chrome extensions
  if (
    request.url.includes('/_next/webpack-hmr') ||
    request.url.startsWith('chrome-extension://')
  ) {
    return;
  }

  // API Requests -> Network first, then fallback to cache if applicable
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .catch(() => {
          return caches.match(request).then((response) => {
            if (response) return response;
            return new Response(JSON.stringify({ error: 'Offline' }), {
              headers: { 'Content-Type': 'application/json' },
              status: 503,
            });
          });
        })
    );
    return;
  }

  // Static Assets and Pages -> Network first, cache fallback
  event.respondWith(
    fetch(request)
      .then((networkResponse) => {
        // Only cache valid HTTP responses
        if (
          networkResponse &&
          networkResponse.status === 200 &&
          networkResponse.type === 'basic'
        ) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, responseToCache);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // If network fails (offline), fallback to cache
        return caches.match(request);
      })
  );
});
