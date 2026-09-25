# Agentic Harness für neue Produktprojekte

Dieser technologieoffene Harness ist für neue, leere Produktprojekte gedacht – vom kleinen CLI- oder Web-Produkt bis zu größeren Vorhaben mit klar begrenztem erstem Meilenstein. Kopiere `AGENTS.md` und `agentic-harness/` in das neue Projekt; dort führt der Harness von Project Init über beauftragte Änderungen bis zur Verifikation.

Tatsächlicher Arbeits- und Entscheidungsfluss                                             
                                                                                                  
 ```text                                                                                                                                                                                      
   AGENTS.md → core.md + project.md                                                                                                                                                           
                 │          └→ bestätigte Ziele, Grenzen, aktive Prüfbefehle                                                                                                                  
                 │                                                                                                                                                                            
                 ├─ Neues Produktprojekt: Init beauftragt oder vor erster                                                                                                                     
                 │  Produktumsetzung noch „Pending Project Init“?                                                                                                                             
                 │    └→ init.md                                                                                                                                                              
                 │         ├→ Ziel, Grenzen und ersten Schritt klären                                                                                                                         
                 │         ├→ project.md + passende Projekt-Docs befüllen                                                                                                                     
                 │         ├→ ggf. echte Checks einrichten und ausführen                                                                                                                      
                 │         └→ zurück zu core.md und zum konkreten Auftrag                                                                                                                     
                 │            (Init allein ist keine Implementierungsfreigabe)                                                                                                                
                 │                                                                                                                                                                            
                 ↓                                                                                                                                                                            
   [R1] ───→ AUFTRAG KLÄREN: Ziel, Umfang, Nicht-Ziele, Freigaben                                                                                                                             
                 │                                                                                                                                                                            
                 ├─ Größeres Vorhaben noch offen?                                                                                                                                             
                 │    └→ Idea klären → zurück zum Auftrag                                                                                                                                     
                 │         („Ready“ ist noch kein Umsetzungsauftrag)                                                                                                                          
                 │                                                                                                                                                                            
                 ├─ Neues/geändertes Nutzerverhalten beauftragt?                                                                                                                              
                 │    └→ betroffene Spec(s) erstellen/ändern:                                                                                                                                 
                 │       prüfbare Akzeptanzkriterien; zunächst „Modified“                                                                                                                     
                 │                                                                                                                                                                            
                 └─ Sonst, z. B. Refactor/Doku/Struktur:                                                                                                                                      
                      Auftrag als Soll; keine künstliche Produktspec                                                                                                                          
                 │                                                                                                                                                                            
                 ↓                                                                                                                                                                            
   [R2] ───→ PASSENDE DOCS LESEN – direkt nach Auslöser in AGENTS.md                                                                                                                          
                 │                                                                                                                                                                            
                 ├→ architecture.md: Bausteine, Grenzen, Schnittstellen                                                                                                                       
                 ├→ code.md:         gewählter Stack, Codekonventionen                                                                                                                        
                 └→ testing.md:      Risiken und Kriterien → geeignete                                                                                                                        
                                     Testebenen/-arten, Testorte und                                                                                                                          
                                     Ausführungsanlässe auswählen                                                                                                                             
                                     (Strategie; führt selbst keine Tests aus)                                                                                                                
                 │                                                                                                                                                                            
                 ↓                                                                                                                                                                            
   [R3] ───→ core.md, Schritt 3: ÄNDERUNG UMSETZEN                                                                                                                                            
                 │                                                                                                                                                                            
                 ├→ tatsächlichen Produkt-Source-Code ändern                                                                                                                                  
                 ├→ passende Produkttests erstellen oder ändern                                                                                                                               
                 ├→ vorgesehene Checks schon während der Arbeit ausführen                                                                                                                     
                 └→ neues Soll / neue Entscheidung nötig?                                                                                                                                     
                      → zurück zu [R1], Projektdatei/Spec erst klären                                                                                                                         
                 │                                                                                                                                                                            
                 ↓                                                                                                                                                                            
           GATE-DURCHLAUF BEGINNT: gate.md                                                                                                                                                    
                 │                                                                                                                                                                            
                 ├→ requirements.md                                                                                                                                                           
                 │    Auftrag + project.md + ggf. Spec/architecture.md                                                                                                                        
                 │    → betroffene AK und Grenzen = SOLL                                                                                                                                      
                 │                                                                                                                                                                            
                 └→ implementation.md                                                                                                                                                         
                      SOLL + tatsächliche Änderung + project.md (Befehle)                                                                                                                     
                      + je nach Eingriff Code-/Architektur-Doc                                                                                                                                
                      + bei Produkt-/Teständerung testing.md                                                                                                                                  
                      │                                                                                                                                                                       
   [R4] ────────────────┤→ erforderliche Checks auf aktuellem Stand ausführen                                                                                                                 
                      └→ beobachtetes IST, Ergebnisse und Nachweisgrenzen                                                                                                                     
                 │                                                                                                                                                                            
                 ↓                                                                                                                                                                            
           gate.md ENTSCHEIDET: Belegen IST und Nachweise das SOLL?                                                                                                                           
                 │                                                                                                                                                                            
                 ├─ JA → Ergebnis berichten;                                                                                                                                                  
                 │        ggf. betroffene Spec „Implemented“                                                                                                                                  
                 │                                                                                                                                                                            
                 └─ NEIN → fail.md: konkrete Lücke und Ursache bestimmen                                                                                                                      
                             │                                                                                                                                                                
                             ├─ Soll unklar / Freigabe oder Spec fehlt                                                                                                                        
                             │    └──────────────────────────────→ [R1]                                                                                                                       
                             │                                                                                                                                                                
                             ├─ Teststrategie oder Nachweisgrenze ungeeignet                                                                                                                  
                             │    └→ testing.md überprüfen ─────→ [R2]                                                                                                                        
                             │                                                                                                                                                                
                             ├─ Prüfbefehl/Umgebung fehlt                                                                                                                                     
                             │    └→ Einrichtung klären; project.md erst                                                                                                                      
                             │       nach tatsächlicher Einrichtung ändern                                                                                                                    
                             │       → Checks ausführen ─────────→ [R4]                                                                                                                       
                             │                                                                                                                                                                
                             ├─ Fehler im Source Code oder Produkttest                                                                                                                        
                             │    └→ Ursache korrigieren ────────→ [R3]                                                                                                                       
                             │                                                                                                                                                                
                             ├─ Prüfung fehlt oder Nachweis ist veraltet                                                                                                                      
                             │    └→ betroffene Prüfung nachholen → [R4]                                                                                                                      
                             │                                                                                                                                                                
                             └─ Entscheidung oder Nachweis weiter unmöglich                                                                                                                   
                                  └→ STOPP: Blocker und offene Checks berichten                                                                                                               
                                                                                                                                                                                              
           Nach jeder möglichen Korrektur:                                                                                                                                                    
           betroffene Prüfungen wiederholen → gate.md erneut vollständig                                                                                                                      
           durchlaufen (requirements.md + implementation.md + Entscheidung).                                                                                                                  
 ```                                                                                                                                                                                          
                                                                                    

 Welche Datei wird wann gelesen?                                                          
                                                                                                 
 ```text                                                                                         
   AUFTRAG                                                                                       
     ↓                                                                                           
   AGENTS.md                         Einstieg: ordnet die Aufgabe zu                             
     ├─ IMMER → harness/core.md       steuert den Arbeits- und Entscheidungsfluss                
     ├─ IMMER → harness/project.md    bestätigte Ziele, Grenzen, aktive Befehle                  
     │                                                                                           
     ├─ BEI Project Init ───────────→ harness/init.md                                            
     ├─ BEI Architektur/Struktur ──→ docs/architecture.md                                        
     ├─ BEI Code/Refactor ──────────→ docs/code.md                                               
     ├─ BEI Testplanung/-arbeit ───→ docs/testing.md                                             
     │                                                                                           
     ├─ BEI offener größerer Idee ──→ ideas/S000-readme.md                                       
     │                                └→ konkrete Idea;                                          
     │                                   Vorlage nur bei Neuanlage                               
     ├─ BEI neuem/geändertem                                                                     
     │  Nutzerverhalten ────────────→ specs/S000-readme.md                                       
     │                                └→ betroffene Spec(s);                                     
     │                                   Vorlage nur bei Neuanlage                               
     │                                                                                           
     ├─ VOR Abschluss ──────────────→ harness/verification/gate.md                               
     └─ BEI Harness-/MD-Pflege ─────→ harness-map.md /                                           
                                      document-contract.md                                       
 ```                                                                                              
Teststruktur: 
```text
   Auftrag + project.md + ggf. Spec (Akzeptanzkriterien)                                         
                       │                                                                         
                       ├→ architecture.md + code.md                                              
                       │          ↓                                                              
                       └────→ testing.md                                                         
                              Welche Prüfungen passen zum Risiko?                                
                              Wo, wie und wann werden sie ausgeführt?                            
                                         │                                                       
                                         ↓                                                       
   core.md, Schritt 3: UMSETZUNG                                                                 
     ├→ Source Code ändern                                                                       
     ├→ passende Tests erstellen/ändern                                                          
     └→ vorgesehene Checks ggf. schon während der Arbeit ausführen                               
                                         │                                                       
                                         ↓                                                       
   gate.md: EINE Abschlussprüfung beginnt                                                        
     ├→ requirements.md → SOLL: Auftrag, Grenzen, betroffene AK                                  
     └→ implementation.md → IST: tatsächliche Änderung prüfen;                                   
          │                  testing.md heranziehen, erforderliche Checks                        
          │                  auf aktuellem Stand ausführen, Belege erfassen                      
          └─────────────────────────┬───────────────────────────────                             
                                    ↓                                                            
                      gate.md entscheidet: Soll ausreichend belegt?                              
                        ├→ JA: Ergebnis berichten; ggf. Spec „Implemented“                       
                        └→ NEIN: fail.md → Ursache klären/korrigieren                            
                                         → betroffene Checks wiederholen                         
                                         → gate.md erneut durchlaufen                            
 ```
## Empfohlen: in ein leeres Projekt kopieren

Kopiere **`AGENTS.md` und den gesamten Ordner `agentic-harness/`** aus diesem Repository unverändert ins Root des neuen Projekts. Nur zusammen stimmen die aktuellen Ladepfade.

```sh
HARNESS=/pfad/zum/agentic-harness-repo
PROJEKT=/pfad/zum/neuen-leeren-projekt
mkdir -p "$PROJEKT"
cp "$HARNESS/AGENTS.md" "$PROJEKT/"
cp -R "$HARNESS/agentic-harness" "$PROJEKT/"
```

Öffne danach das Zielprojekt mit deinem Coding-Agenten und beauftrage Project Init, z. B. „Kläre den ersten Nutzerablauf und initialisiere dieses neue Produktprojekt.“ Der Agent befüllt `agentic-harness/harness/project.md` und die betroffenen Projekt-Docs. Eine **Produkt-`README.md`** wird im Zielprojekt neu erstellt oder, falls vorhanden, mit bestätigten Produktinformationen ergänzt. Beobachtungen über mögliche **universelle** Harness-Verbesserungen können dort in `agentic-harness/harness-learnings.md` gesammelt werden; sie werden nicht automatisch in dieses Quell-Repository übernommen.

**Nicht mitkopieren:** Diese README ist nur die Anleitung zum Harness. `main.py` ist hier leer; `.venv/` ist eine lokale virtuelle Python-Umgebung (virtual environment). Auch `.idea/`, `assets/` und `.git/` sind kein benötigter Teil des Harnesses. Richte Umgebung und Produktcode für das Zielprojekt nach dessen Entscheidungen ein.

## Ganzes Repository als Ausgangspunkt

Du kannst das Repository auch klonen oder als Vorlage kopieren, musst dann aber die Harness-README durch eine Produkt-README ersetzen und nicht benötigte Dateien wie `main.py` und `assets/` entfernen. Das ist derzeit **kein automatischer Installer**; für ein neues Produkt ist das gezielte Kopieren der beiden oben genannten Bestandteile der einfachere Weg.
