// Offline cache for the calculator. Bump VERSION whenever index.html changes.
const VERSION = 'chartgap-v7';
const FILES = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(VERSION).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== VERSION).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
// The page itself: network first so a new version shows at once; the saved copy after 4 s or when offline.
// Other files: serve from cache at once, refresh the cache from the network in the background
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  // live prices and the bubble history: network first, the last saved copy when offline
  const data = new URL(req.url).pathname.match(/\/(prices|history)\.json$/);
  if (data) {
    const name = data[1] + '.json';
    e.respondWith(caches.open(VERSION).then(c => fetch(req).then(r => { if (r.ok) c.put(name, r.clone()); return r; })
      .catch(async () => await c.match(name) || new Response('{}', { status: 504 }))));
    return;
  }
  if (req.mode === 'navigate' || new URL(req.url).pathname.endsWith('/index.html')) {
    e.respondWith(caches.open(VERSION).then(c => {
      const net = fetch(req, { cache: 'no-cache' }).then(r => { if (r.ok) c.put('index.html', r.clone()); return r; });
      const late = new Promise(ok => setTimeout(ok, 4000)).then(() => c.match('index.html'));
      return Promise.race([net.catch(() => c.match('index.html')), late.then(h => h || net)])
        .then(r => r || new Response('', { status: 504 }));
    }));
    return;
  }
  e.respondWith(caches.open(VERSION).then(async c => {
    const hit = await c.match(req, { ignoreSearch: true }) || (req.mode === 'navigate' ? await c.match('index.html') : null);
    const net = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; }).catch(() => null);
    return hit || (await net) || new Response('', { status: 504 });
  }));
});
