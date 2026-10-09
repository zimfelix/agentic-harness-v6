// Öffnet die Geräte-Vorschau (../assets/device-preview.html, vom Vorschau-Server serve.mjs unter /_geraete/ ausgeliefert)
// in einem neuen Brave-Fenster: die Website gleichzeitig als Handy, Tablet, MacBook und Monitor.
// Läuft die Vorschau nicht, wird sie gebaut und im Hintergrund gestartet. Aufruf aus dem Projektordner.
import { execFileSync, spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { sleep } from './browser.mjs';
import { konfig } from './konfig.mjs';

const port = Number(process.env.PORT || konfig.port);
const url = `http://127.0.0.1:${port}/_geraete/`;

// 'ok' = Vorschau mit Geräte-Vorschau, 'alt' = Vorschau ohne (vor dieser Funktion gestartet), 'aus' = keine Vorschau
const check = async () => {
  try {
    const res = await fetch(`http://127.0.0.1:${port}/_geraete/stand`, { signal:AbortSignal.timeout(1000) });
    if (!res.headers.get('content-type')?.includes('json')) return 'alt';
    const info = await res.json();
    if (info.aktuell === false) return 'fehler';
    return res.ok && info.aktuell === true ? 'ok' : 'alt';
  } catch { return 'aus'; }
};

let state = await check();
if (state === 'alt') {
  console.error(`Auf Port ${port} läuft eine ältere Vorschau ohne Geräte-Vorschau. Bitte beenden und neu starten.`);
  process.exit(1);
}
if (state === 'fehler') {
  console.error('Vorschau meldet einen Buildfehler; kein aktueller Stand. Buildquelle prüfen.');
  process.exit(1);
}
if (state === 'aus') {
  spawn(process.execPath, [fileURLToPath(new URL('./serve.mjs', import.meta.url))], { detached:true, stdio:'ignore' }).unref();
  for (let i = 0; i < 40 && !['ok', 'fehler'].includes(state); i++) { await sleep(250); state = await check(); }
  if (state !== 'ok') { console.error('Die Vorschau ließ sich nicht aktuell starten (ggf. Buildfehler).'); process.exit(1); }
  console.log(`Vorschau gestartet: http://127.0.0.1:${port}/ (läuft im Hintergrund weiter)`);
}

// Immer ein neues Fenster: Brave kann ohne offenes Fenster laufen, dann erschiene sonst nichts.
const appleScript = ['tell application "Brave Browser"', 'make new window', `set URL of active tab of front window to "${url}"`, 'activate', 'return count of windows', 'end tell'];
try {
  const windows = Number(execFileSync('osascript', appleScript.flatMap(line => ['-e', line]), { encoding:'utf8' }).trim());
  console.log(windows > 0 ? `Geräte-Vorschau in Brave geöffnet: ${url}` : `Brave zeigt kein Fenster. Adresse: ${url}`);
} catch {
  console.log(`Brave ließ sich nicht automatisch öffnen. Adresse: ${url}`);
}
