// Projektdaten: die einzige Quelle für Seiten, head, Sitemap, robots.txt, JSON-LD, Kopf- und Fußzeile.
// Nur echte Angaben vom Kunden. Unbekanntes bleibt leer oder „Platzhalter: …“: die Vorschau baut trotzdem,
// der Produktions-Build nennt und sperrt es. Regeln: references/seo.md und page-plan.md des website-tools-Skills.
const firma = {
  name: 'Platzhalter Firmenname',
  typ: 'LocalBusiness',          // spezifischster schema.org-Typ, z. B. Electrician, Plumber, HousePainter, Bakery
  beschreibung: 'Platzhalter: die Firma in einem Satz (Angebot, Ort, Besonderheit), überall gleich verwendet.',
  telefon: '',                   // international, z. B. '+49 30 1234567'; erscheint sichtbar in Kopf- und Fußzeile
  telefonAnzeige: '',            // wie auf der Visitenkarte, z. B. '030 123 45 67'
  email: '',
  adresse: { strasse: 'Platzhalter Straße 1', plz: '00000', ort: 'Platzhalter Ort', land: 'DE' }, // land: DE, AT, CH …
  oeffnungszeiten: [],           // z. B. { tage: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], von: '08:00', bis: '17:00' }
  einsatzgebiet: [],             // echte Orte und Regionen
  sameAs: [],                    // eigene Profile: Unternehmensprofil, Branchenverzeichnis, Social Media
  logo: '',                      // optional, z. B. '/logo.png' in src/static/
};

export default {
  siteUrl: 'https://www.example.com', // Produktions-URL: https, gewählte Host-Form (mit oder ohne www), ohne Pfad
  sprache: 'de',                 // <html lang>; de-AT oder de-CH nur, wenn die Inhalte wirklich abweichen
  locale: 'de_DE',               // og:locale
  farbe: '#3b5b4f',              // theme-color; Ersatz-Favicon, solange src/static/favicon.png fehlt
  ogBild: '',                    // Vorschaubild geteilter Links, z. B. '/og.jpg' (1200 × 630) in src/static/
  kiCrawler: 'alle',             // robots.txt: 'alle' (A) oder 'nurSuche' (B: KI-Suche ja, Training nein); entscheidet der Kunde
  firma,
  navigation: [
    { text: 'Leistungen', href: '/#leistungen' },
    { text: 'Kontakt', href: '/#kontakt' },
  ],
  // art: 'suche' (Standard; braucht absicht und beleg vor dem Livegang) · 'info' (indexierbar ohne eigene Suchabsicht, z. B. Über uns, Kontakt)
  //      · 'recht' (in jeder Fußzeile) · 'sonder' (noindex, nicht in der Sitemap). Platzhalter sperren den Livegang bei jeder Art.
  // geaendert: Datum der letzten Inhaltsänderung (JJJJ-MM-TT) für lastmod; ohne Datum entfällt lastmod.
  seiten: [
    {
      route: '/', vorlage: 'start', kurz: 'Start',
      title: `Platzhalter: Hauptleistung in Ort – ${firma.name}`,
      description: 'Platzhalter: Angebot, Ort und ein konkreter Vorteil in einem Satz, 50 bis 160 Zeichen.',
      h1: 'Platzhalter: Hauptleistung in Ort',
      absicht: '',               // Hauptabsicht in den Worten der Suchenden, z. B. „Elektriker Musterstadt“
      beleg: '',                 // echter Nachweis vom Kunden für diese Absicht: Referenzen, Fotos, Qualifikation
      inhalt: {
        einleitung: '',
        aktion: 'Anfrage stellen',
        leistungen: [{ titel: 'Platzhalter Leistung 1' }, { titel: 'Platzhalter Leistung 2' }, { titel: 'Platzhalter Leistung 3' }],
        nachweise: [],           // { text, quelle, datum }
        kontakt: '',
      },
    },
    // Leistungsseite mit eigener Suchabsicht (nur mit echtem Nachweis; sonst ein Abschnitt auf der Startseite):
    // {
    //   route: '/leistungen/name/', vorlage: 'leistung', kurz: 'Name',
    //   title: `Leistung in Ort – ${firma.name}`, description: '…', h1: 'Leistung in Ort',
    //   absicht: '…', beleg: '…', geaendert: 'JJJJ-MM-TT',
    //   inhalt: { karte: 'Kartentext auf der Startseite', einleitung: '…', punkte: ['…'], ablauf: ['…'], preis: 'ab … € inkl. MwSt.', nachweise: [], fragen: [{ frage: '…', antwort: '…' }] },
    // },
    {
      route: '/impressum/', art: 'recht', vorlage: 'recht', kurz: 'Impressum',
      title: `Impressum – ${firma.name}`, description: `Impressum von ${firma.name}: Anbieter, Anschrift und Kontakt.`,
      h1: 'Impressum', datei: '', // z. B. 'recht/impressum.html' (DE § 5 DDG; AT § 5 ECG und § 25 MedienG)
    },
    {
      route: '/datenschutz/', art: 'recht', vorlage: 'recht', kurz: 'Datenschutz',
      title: `Datenschutzerklärung – ${firma.name}`, description: `Datenschutzerklärung von ${firma.name}: welche Daten diese Website verarbeitet.`,
      h1: 'Datenschutzerklärung', datei: '',
    },
    { route: '/404.html', art: 'sonder', vorlage: 'fehler', title: `Seite nicht gefunden – ${firma.name}`, h1: 'Seite nicht gefunden' },
  ],
};
