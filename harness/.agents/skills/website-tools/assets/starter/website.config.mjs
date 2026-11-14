// Einstellungen der website-tools-Prüfer (references/tooling.md des Skills). Die SEO-Werte kommen aus src/site.config.mjs,
// damit Build und Prüfer dieselbe Quelle haben. Hier nur eintragen, was beim Projekt anders ist.
import site from './src/site.config.mjs';

export default {
  quelle: 'src',
  ausgabe: 'dist',
  build: ['node', 'scripts/build.mjs'],
  // Browser-Prüfungen erkennen nur Verzeichnisrouten (…/index.html); Sonderseiten wie /404.html prüft nur seo-pruefen.
  routen: site.seiten.filter(s => s.route.endsWith('/')).map(s => s.route),
  seo: {
    siteUrl: site.siteUrl,
    schraegstrich: 'immer',
    sonderseiten: site.seiten.filter(s => s.art === 'sonder').map(s => s.route),
    pflichtLinks: site.seiten.filter(s => s.art === 'recht').map(s => s.route),
  },
};
