# Fail – Lücke klären und gezielt erneut prüfen

> - **Typ:** Prozess
> - **Zuständigkeit:** Bei fehlendem oder gescheitertem Nachweis den nächsten begründeten Schritt oder Blocker bestimmen.
> - **Gilt bei:** Wenn `agentic-harness/harness/verification/gate.md` keine ausreichende Abschlussentscheidung treffen kann.
> - **Ladebeziehungen:** Vom Gate geladen; nutze die Soll-Lücken aus `agentic-harness/harness/verification/requirements.md` und die Ist-/Nachweislücken aus `agentic-harness/harness/verification/implementation.md`. Nach einer Korrektur betroffene Prüfungen und dann das Gate erneut durchführen.
> - **Nicht zuständig:** Anforderungen eigenmächtig ändern, fehlende Checks als bestanden werten oder automatisch reparieren.

## Rückweg zum Gate

1. Benenne die konkrete Lücke mit beobachtetem Ergebnis: ungeklärter Auftrag, fehlende Spec oder Freigabe, Abweichung der Umsetzung, defekter Test, fehlender Nachweis oder nicht verfügbare Umgebung. Eine vermutete Ursache bleibt als Hypothese markiert.
2. Ist das Soll unklar, kläre es mit dem Auftraggeber und aktualisiere erst danach die zuständigen Projektdateien oder Specs. Liegt die Lücke in Umsetzung oder Test, korrigiere nur die begründete Ursache. Erscheint derselbe Fehler erneut, überprüfe die Annahme statt dieselbe Aktion blind zu wiederholen.
3. Wiederhole nach der Korrektur die betroffenen Prüfungen und das Gate mit Soll-Abgleich aus `agentic-harness/harness/verification/requirements.md` und Ist-/Nachweisprüfung aus `agentic-harness/harness/verification/implementation.md`. Bei geändertem Soll aktualisiere zuerst die zuständigen Projektdateien oder Specs. Ändere Akzeptanzkriterien nicht bloß, damit ein Test grün wird.
4. Fehlen Entscheidung, Umgebung oder Nachweis weiterhin, stoppe und berichte bestandene, fehlgeschlagene und nicht ausgeführte Prüfungen getrennt. Eine betroffene neue oder geänderte Spec bleibt `Modified`, bis das Gate bestanden ist; bei Refactor oder Dokuänderung ohne Spec-Änderung kein künstlicher Statuswechsel.
