const CACHE_NAME = 'backloggy-e583f65';
const PRECACHE_URLS = ["404.html","assets/AssetManifest.bin","assets/AssetManifest.bin.json","assets/FontManifest.json","assets/NOTICES","assets/assets/branding/backloggy_icon.png","assets/assets/dev/api_keys.example.json","assets/assets/help/igdb.md","assets/assets/help/omdb.md","assets/assets/help/overview.md","assets/assets/help/rawg.md","assets/assets/help/steamgriddb.md","assets/assets/help/tmdb.md","assets/assets/help/tvdb.md","assets/fonts/MaterialIcons-Regular.otf","assets/google_fonts/IBMPlexMono-Medium.ttf","assets/google_fonts/IBMPlexMono-Regular.ttf","assets/google_fonts/SpaceGrotesk-Bold.ttf","assets/google_fonts/SpaceGrotesk-Medium.ttf","assets/google_fonts/SpaceGrotesk-Regular.ttf","assets/google_fonts/SpaceGrotesk-SemiBold.ttf","assets/packages/cupertino_icons/assets/CupertinoIcons.ttf","assets/packages/material_ui/shaders/ink_sparkle.frag","assets/packages/phosphor_flutter/lib/fonts/Phosphor-Bold.ttf","assets/packages/phosphor_flutter/lib/fonts/Phosphor-Duotone.ttf","assets/packages/phosphor_flutter/lib/fonts/Phosphor-Fill.ttf","assets/packages/phosphor_flutter/lib/fonts/Phosphor-Light.ttf","assets/packages/phosphor_flutter/lib/fonts/Phosphor-Thin.ttf","assets/packages/phosphor_flutter/lib/fonts/Phosphor.ttf","assets/shaders/ink_sparkle.frag","assets/shaders/stretch_effect.frag","canvaskit/canvaskit.js","canvaskit/canvaskit.wasm","canvaskit/chromium/canvaskit.js","canvaskit/chromium/canvaskit.wasm","drift_worker.dart.js","favicon.png","flutter.js","flutter_bootstrap.js","icons/Icon-192.png","icons/Icon-512.png","icons/Icon-maskable-192.png","icons/Icon-maskable-512.png","index.html","main.dart.js","manifest.json","sqlite3.wasm","sw_register.js","version.json"];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys
          .filter((key) => key.startsWith('backloggy-') && key !== CACHE_NAME)
          .map((key) => caches.delete(key)),
      ))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put('index.html', copy));
          return response;
        })
        .catch(() => caches.match('index.html')),
    );
    return;
  }

  event.respondWith(
    caches.match(request).then((cached) => {
      const refreshed = fetch(request)
        .then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
          }
          return response;
        })
        .catch(() => cached);
      return cached || refreshed;
    }),
  );
});
