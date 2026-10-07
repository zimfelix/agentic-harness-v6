# Architektur

**Zuständigkeit:** Beschlossene Bausteine, Fachmodell, Dateistruktur, Datenfluss und Betrieb. Lesen bei Architektur-, Datenmodell-, Schnittstellen-, Betriebs- oder Strukturänderungen.

## Universeller Rahmen

Vor erstem Produktcode Struktur festlegen: Source, Tests, Konfiguration/Inhalte, Scripts, Assets, ggf. Tokens. Ist, Ziel und offene Optionen unterscheiden. Entscheidungen knapp begründen; keine Abstraktionen auf Vorrat. Fachregeln nur bei Bedarf vom Infrastrukturcode trennen (konkrete Pflichten im gewählten Business-Software-Profil).

Betrieb: Auslöser/Zeitplan, Umgebungen, Secrets-Ort (nie Werte), Protokolle, externe Seiteneffekte und Schutzmaßnahmen. Varianten bleiben intern und getrennt vom Produkt; nach Auswahl löschen/archivieren. Archiv im Projektprofil benennen, nicht laden/bauen/testen. Nur ausdrücklich vorgesehene Einstiege ausliefern.

Werte gehören in Konfiguration/Tokens; die Architektur beschreibt Zuständigkeiten, keine duplizierten Implementierungsdetails.

## Projektspezifische Befüllung

Noch offen (Project Init).
