// Registers the offline service worker. Externalised from index.html so the
// Content-Security-Policy there does not have to allow inline scripts.
if ('serviceWorker' in navigator && location.protocol === 'https:') {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('service_worker.js');
  });
}
