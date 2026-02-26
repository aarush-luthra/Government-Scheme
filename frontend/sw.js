/**
 * Service Worker - Government Scheme Assistant PWA
 * Cache-first for static assets, network-first for API calls
 */

const CACHE_NAME = 'govscheme-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/script.js',
    '/saved.html',
    '/admin.html',
    'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap',
    'https://cdn.jsdelivr.net/npm/dompurify@3.2.6/dist/purify.min.js',
];

// Install: cache static shell
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('SW: Some assets failed to cache:', err);
            });
        })
    );
    self.skipWaiting();
});

// Activate: clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            );
        })
    );
    self.clients.claim();
});

// Fetch strategy
self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Skip non-GET requests
    if (event.request.method !== 'GET') return;

    // API calls: network-first with cache fallback
    if (url.pathname.startsWith('/api/') ||
        url.pathname.startsWith('/chat') ||
        url.pathname.startsWith('/auth/') ||
        url.pathname.startsWith('/translate') ||
        url.pathname.startsWith('/health')) {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Cache successful API responses for offline access
                    if (response.ok && url.pathname.startsWith('/api/v1/saved-dashboard')) {
                        const clone = response.clone();
                        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                    }
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    // Static assets: cache-first
    event.respondWith(
        caches.match(event.request).then((cached) => {
            if (cached) return cached;
            return fetch(event.request).then((response) => {
                if (response.ok) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            });
        }).catch(() => {
            // Offline fallback for navigation requests
            if (event.request.mode === 'navigate') {
                return caches.match('/index.html');
            }
        })
    );
});
