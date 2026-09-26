const CACHE_PREFIX = 'pokebindr-pwa-';
const CACHE_NAME = `${CACHE_PREFIX}v15`;
const CORE_PATHS = [
  './',
  'index.html',
  'flutter_bootstrap.js',
  'flutter.js',
  'main.dart.js',
  'manifest.json',
  'favicon.png',
  'icons/Icon-192.png',
  'icons/Icon-512.png',
  'icons/Icon-maskable-192.png',
  'icons/Icon-maskable-512.png',
  'drift_worker.dart.js',
  'sqlite3.wasm',
  'assets/AssetManifest.bin.json',
  'assets/FontManifest.json',
  'assets/fonts/MaterialIcons-Regular.otf',
  'assets/packages/cupertino_icons/assets/CupertinoIcons.ttf',
  'assets/assets/fonts/Phosphor-Bold.ttf',
  'assets/assets/fonts/Phosphor-Fill.ttf',
  'assets/assets/google_fonts/Archivo-Regular.ttf',
  'assets/assets/google_fonts/Archivo-Medium.ttf',
  'assets/assets/google_fonts/Archivo-SemiBold.ttf',
  'assets/assets/google_fonts/Archivo-Bold.ttf',
  'assets/assets/google_fonts/IBMPlexMono-Regular.ttf',
  'assets/assets/google_fonts/IBMPlexMono-Medium.ttf',
  'assets/assets/google_fonts/IBMPlexMono-SemiBold.ttf',
  'assets/assets/icons/logo_mark.png',
  'assets/assets/catalog/catalog_seed.db.gz',
];

const scopedUrl = (path) => new URL(path, self.registration.scope).toString();

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => cache.addAll(CORE_PATHS.map(scopedUrl)))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(
          keys
            .filter((key) => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME)
            .map((key) => caches.delete(key)),
        ),
      )
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  event.respondWith(
    fetch(request)
      .then((response) => {
        if (response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      })
      .catch(async () => {
        const cached = await caches.match(request);
        if (cached) return cached;
        if (request.mode === 'navigate') {
          return caches.match(scopedUrl('./'));
        }
        throw new Error(`No cached response for ${request.url}`);
      }),
  );
});
