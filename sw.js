/* Service worker for sikkerhetskontroll-skjemaet.

   To strategier:
   - index.html og grunndata.js hentes fra nett nar det finnes nett, med cache som
     reserve. Da far alle siste utgave av appen og ferske hyttedata sa snart de
     apner appen i dekning, uten a installere pa nytt.
   - Resten hentes fra cache, og oppdateres i bakgrunnen.

   Nettkallet gir opp etter tre sekunder og gar til cache. Det er viktig i fjellet,
   der telefonen kan ha en strek som ikke fungerer.

   CACHE bumpes automatisk av lag-grunndata.py, eller manuelt ved endringer. */
const CACHE = "internkontroll-v3";
const FILER = ["./", "./index.html", "./grunndata.js", "./manifest.webmanifest",
               "./ikon-192.png", "./ikon-512.png"];
const FERSKE = ["index.html", "grunndata.js"];
const TIDSGRENSE = 3000;

self.addEventListener("install", e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(FILER.map(f => new Request(f, {cache:"reload"}))))
      .then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(n => Promise.all(n.filter(x => x !== CACHE).map(x => caches.delete(x))))
    .then(() => self.clients.claim()));
});

function lagre(req, svar){
  if(svar && svar.ok) { const kopi = svar.clone(); caches.open(CACHE).then(c => c.put(req, kopi)); }
  return svar;
}
function fraCache(req){
  return caches.match(req).then(t => t || caches.match("./index.html"));
}

self.addEventListener("fetch", e => {
  if(e.request.method !== "GET") return;
  let url;
  try { url = new URL(e.request.url); } catch(err) { return; }
  if(url.origin !== location.origin) return;

  const ferskt = e.request.mode === "navigate" ||
                 FERSKE.some(f => url.pathname.endsWith("/" + f));

  if(ferskt){
    // nett forst, men gi opp raskt og bruk det som ligger lagret
    e.respondWith(new Promise(ferdig => {
      let avgjort = false;
      const tidsavbrudd = setTimeout(() => {
        if(!avgjort){ avgjort = true; fraCache(e.request).then(ferdig); }
      }, TIDSGRENSE);
      fetch(e.request).then(svar => {
        lagre(e.request, svar);
        clearTimeout(tidsavbrudd);
        if(!avgjort){ avgjort = true; ferdig(svar); }
      }).catch(() => {
        clearTimeout(tidsavbrudd);
        if(!avgjort){ avgjort = true; fraCache(e.request).then(ferdig); }
      });
    }));
    return;
  }

  // cache forst, oppdater i bakgrunnen
  e.respondWith(caches.match(e.request).then(truffet => {
    const nett = fetch(e.request).then(svar => lagre(e.request, svar)).catch(() => truffet);
    return truffet || nett;
  }));
});
