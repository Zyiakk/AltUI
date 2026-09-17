# AltUI – Garderobe- und Aussehen-Panel

Deutsche Fassung der Beschreibung des [Steam-Workshop-Eintrags](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). Maßgeblich ist das englische Original auf der Workshop-Seite.

Die Garderobe des Spiels gibt jedem Mod-Autor einen eigenen Reiter. Mit ein paar Kleidungs-Mods ist dieselbe Art von Teil über ein Dutzend Reiter verstreut, und suchen kann man nicht. AltUI sortiert jedes Teil aus dem Spiel und aus allen installierten Mods in **eine Liste pro Slot** (Oberteile, Röcke, Schuhe, …), mit Suche, Filtern, Favoriten und Ausblenden – und holt Frisur, Makeup, Körper und Outfits in dasselbe Panel. Es öffnet sich überall im Level mit **B**; kein Weg mehr zur Garderobe oder zum Spiegel.

> ⚠️ **Warnung:** Gemacht für Spielversion 0.6.x. Ein Spiel-Update, das die Kleidungs-/Makeup-Tabellen oder den Kamera-Manager ändert, kann den Mod kaputt machen. Steam aktualisiert nur die Hälfte des Mods automatisch (das Workshop-Pak); die Hook-Datei in `~mods` verwaltest du selbst – siehe „Mod-Updates und die Hook-Datei“ unten, wann sie ersetzt werden muss.

## ⚠ Installation – zuerst lesen

Das Abonnieren installiert nur die Hälfte des Mods. Das Panel braucht eine zweite Datei, die der Workshop nicht für dich ablegen kann, weil sie eines der Blueprints des Spiels überschreiben muss (den Player-Kamera-Manager). Ohne sie **passiert bei B nichts**.

1. Diesen Eintrag abonnieren (das installiert **AltUI.pak**).
2. **AltUI_Hook_P.pak** herunterladen: https://github.com/Zyiakk/AltUI/releases/latest/download/AltUI_Hook_P.pak
3. Kopieren nach
   `Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Content\Paks\~mods\`
   Den Ordner **~mods** anlegen, falls er nicht existiert (der Name beginnt mit einer Tilde). Der Spielordner-Name kommt im Pfad zweimal vor – das ist richtig so.
4. Spiel starten, in einem Level B drücken.

**„Ich habe abonniert, aber B tut nichts“** → die Hook-Datei fehlt oder liegt im falschen Ordner. Sie muss in *Content\Paks\~mods* liegen, nicht in *Mods* und nicht im Workshop-Ordner.

Der Hook ersetzt *TKA_PlayerCameraManager* und kollidiert mit jedem anderen Mod, der dasselbe Blueprint ersetzt (keiner bekannt). Deinstallation: abbestellen und die Hook-Datei löschen. Die eigenen Speicherdateien des Mods (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav* und die Look-Fotos in *Saved\SaveGames\AltUI\*) können ebenfalls gelöscht werden; sonst wird nichts angefasst – Kleidung, Outfits, Makeup und Frisur laufen über die Speicherdateien des Spiels.

## Was es kann

* **Kleidung** – jedes Teil, das Spiel und Mods kennen, nach Slot gruppiert, Unterreiter pro Mod, Suche, Filter „nur Besessene“ / „nur Favoriten“, Favoriten, Farbe über die Palette des Spiels, Farb-Reset, in den Rucksack und zurück, Teile ausblenden.
* **Outfits** – die Outfit-Vorlagen des Spiels, mit Namen (Rechtsklick → umbenennen).
* **Looks** – ein kompletter Look (Kleidung mit Farben, Frisur und Haarfarbe, Makeup, Augen, Haut, Körper-Regler, Body-Mod), gespeichert mit einem Ganzkörperfoto aus dem Spiel. Anwenden, aktualisieren, umbenennen, löschen.
* **Rucksack** – was Jodi trägt und dabeihat: anziehen, ausziehen, reparieren, zurück in die Garderobe, aufräumen.
* **Frisur** – alle Frisuren, Haarfarbe, Werkseinstellung.
* **Aussehen** – Haut, jeder Makeup-Typ, Augen, Aussehen-Vorlagen mit Symbolen.
* **Körperform** – Regler für Brust / Taille und ein Umschalter für installierte Body-Mods.
* **Optionen** – Taste für das Panel, Sprache, Scroll-Geschwindigkeit, Kachelgröße, freier Bildschirmanteil für Jodi, Kamera-FOV / -Abstand / -Schwenk, Farbschema und Deckkraft, „Unterwäsche darf ausgezogen werden“.
* Rückgängig / Wiederholen (5 Schritte), Tooltips zeigen, aus welchem Mod ein Teil stammt.

Sprachen: Englisch, Deutsch, Chinesisch, Russisch, Spanisch (automatisch erkannt, in den Optionen umschaltbar).

## Steuerung

* **B** – öffnen / schließen (in den Optionen änderbar). **Esc** schließt.
* Linksklick – auswählen / anziehen / anwenden. Rechtsklick – Kontextmenü. Mausrad – scrollen.
* Solange das Panel offen ist, kann Jodi nicht laufen; Ziehen auf dem Hintergrund dreht die Kamera, +/− ändert den Abstand.

## Body-Mods

Body-Replacer-Paks überschreiben alle dieselbe Spieldatei, deshalb kann nur einer aktiv sein. Ein kleiner Konverter macht aus einem Replacer ein normales Mod-Pak, das das Mesh unter einem eigenen Pfad behält; beliebig viele konvertierte Bodys können nebeneinander installiert sein und erscheinen als Chips im Reiter Körperform.

Konverter (Python 3.8+, keine Pakete): https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

```
python bodypak.pyz SomeBodyReplacer.pak --name Body_Some --title SomeBody
```

Das erzeugte *Body_Some.pak* nach *TheKillingAntidote\Mods\* kopieren und den ursprünglichen Replacer entfernen (oder in *~mods* lassen – er wird dann zum Chip „Standard“).

## Kompatibilität

Gemacht für Spielversion 0.6.x. Funktioniert mit Kleidungs-, Frisur-, Makeup- und Karten-Mods aus Workshop und Nexus – sie erscheinen einfach in den Listen. Ein Spiel-Update, das die Kleidungs-/Makeup-Tabellen oder den Kamera-Manager ändert, kann den Mod kaputt machen.

## Mod-Updates und die Hook-Datei

Die beiden Dateien sind absichtlich lose gekoppelt: Der Hook startet nur das Panel und bewegt die Kamera, solange es offen ist; alles andere steckt im Workshop-Pak. Wenn dieser Eintrag also über Steam aktualisiert wird, **funktioniert deine vorhandene Hook-Datei normalerweise weiter – kein erneuter Download nötig**. Jeder Changelog-Eintrag nennt, ob sich der Hook geändert hat.

Eine neue **AltUI_Hook_P.pak** brauchst du nur, wenn

* der Changelog es sagt – das passiert, wenn sich das Kamera-Verhalten oder die Startlogik selbst ändert, oder
* ein Spiel-Update den Player-Kamera-Manager ersetzt; dann muss der Hook gegen die neue Spielversion neu gebaut werden (und der alte kann die Kamera stören, bis du ihn löschst oder ersetzt).

Falls der Hook einmal veraltet ist: aktuelle Datei über den GitHub-Link oben laden, die in *Content\Paks\~mods* ersetzen, fertig. Wenn der Mod stattdessen ganz weg soll: abbestellen und diese Datei löschen.

Es sind keine Spiel-Assets enthalten; alles im Pak ist generiert.

## Quellcode & Fehlermeldungen

https://github.com/Zyiakk/AltUI – Quellcode (MIT), alle Downloads, Fehlermeldungen.
