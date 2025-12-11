/**
 * Service Worker for Leadership Artifacts PWA
 *
 * Provides offline functionality and caching for the application.
 * Implements a cache-first strategy for static assets and network-first for dynamic content.
 *
 * Cache Strategy:
 * - Static assets (HTML, manifest) are cached immediately on install
 * - Dynamic content is cached on first access
 * - Old caches are cleaned up on activation
 *
 * @version 1.0.0
 */

// Cache names - increment version to force cache refresh
const CACHE_NAME = 'leadership-artifacts-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';

/**
 * Assets to cache immediately on service worker install
 * These are essential for offline functionality
 */
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json'
];

/**
 * Install Event Handler
 *
 * Triggered when service worker is first installed.
 * Caches essential static assets and forces immediate activation.
 *
 * @param {ExtendableEvent} event - Service worker install event
 */
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => self.skipWaiting()) // Activate immediately without waiting
  );
});

/**
 * Activate Event Handler
 *
 * Triggered when service worker takes control.
 * Cleans up old caches from previous versions and claims all clients.
 *
 * @param {ExtendableEvent} event - Service worker activate event
 */
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating...');
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        // Delete old caches that don't match current version
        return Promise.all(
          cacheNames
            .filter(name => name !== STATIC_CACHE && name !== DYNAMIC_CACHE)
            .map(name => {
              console.log('[Service Worker] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => self.clients.claim()) // Take control of all pages immediately
  );
});

/**
 * Fetch Event Handler
 *
 * Intercepts all network requests and implements caching strategy.
 * Strategy: Cache-first with network fallback
 *
 * Flow:
 * 1. Check if request is in cache
 * 2. If cached, return immediately (fast!)
 * 3. If not cached, fetch from network
 * 4. Cache the response for future use
 * 5. Return the response
 *
 * @param {FetchEvent} event - Service worker fetch event
 */
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests (external resources)
  // Only cache same-origin resources
  if (url.origin !== location.origin) {
    return;
  }

  event.respondWith(
    caches.match(request)
      .then(cachedResponse => {
        // Cache hit - return immediately
        if (cachedResponse) {
          console.log('[Service Worker] Serving from cache:', request.url);
          return cachedResponse;
        }

        // Cache miss - fetch from network
        return fetch(request)
          .then(response => {
            // Only cache successful responses (200 OK)
            // Skip opaque responses from CORS requests
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone the response because it can only be consumed once
            const responseToCache = response.clone();

            // Add to cache for future requests
            caches.open(DYNAMIC_CACHE)
              .then(cache => {
                console.log('[Service Worker] Caching dynamic:', request.url);
                cache.put(request, responseToCache);
              });

            return response;
          })
          .catch(error => {
            // Network request failed (offline or error)
            console.error('[Service Worker] Fetch failed:', error);

            // Return offline message
            // TODO: Could return a custom offline.html page here
            return new Response('Offline - content not available', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
});

/**
 * Message Event Handler
 *
 * Handles messages from the main application for manual control.
 *
 * Supported message types:
 * - SKIP_WAITING: Force service worker to activate immediately
 * - CLEAR_CACHE: Delete all caches (useful for debugging)
 *
 * @param {ExtendableMessageEvent} event - Service worker message event
 */
self.addEventListener('message', event => {
  // Force activation without waiting for all tabs to close
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  // Clear all caches (for debugging or manual refresh)
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(name => caches.delete(name))
        );
      })
    );
  }
});

// Service worker successfully loaded and ready
console.log('[Service Worker] Loaded and ready');
