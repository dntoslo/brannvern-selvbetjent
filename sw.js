/* Service worker for sikkerhetskontroll-skjemaet.
   Cacher appen slik at den virker uten dekning.
   Cachenavnet bumpes automatisk av lag-grunndata.py. */
const CACHE = "internkontroll-v1";
const FILER = ["./", "./index.html", "./grunndata.js", "./manifest.webmanifest",
               "./ikon-192.png", "./ikon-512.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILER)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(n => Promise.all(n.filter(x => x !== CACHE).map(x => caches.delete(x))))
    .then(() => self.clients.claim()));
});

/* Cache forst, sa virker alt uten nett. Ny utgave hentes i bakgrunnen
   og tas i bruk neste gang appen apnes med dekning. */
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  e.respondWith(caches.match(e.request).then(truffet => {
    const fra_nett = fetch(e.request).then(svar => {
      if (svar && svar.ok) caches.open(CACHE).then(c => c.put(e.request, svar.clone()));
      return svar;
    }).catch(() => truffet);
    return truffet || fra_nett;
  }));
});
