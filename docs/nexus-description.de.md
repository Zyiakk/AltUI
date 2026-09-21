# AltUI – Garderobe- und Aussehen-Panel

Deutsche Fassung der Beschreibung der [AltUI-Seite auf Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). Maßgeblich ist das englische Original auf der Nexus-Seite.

Die Garderobe des Spiels gibt jedem Mod-Autor einen eigenen Reiter. Mit ein paar Kleidungs-Mods ist dieselbe Art von Teil über ein Dutzend Reiter verstreut, und suchen kann man nicht. AltUI sortiert jedes Teil aus dem Spiel und aus allen installierten Mods in **eine Liste pro Slot** (Oberteile, Röcke, Schuhe, …), mit Suche, Filtern, Favoriten und Ausblenden – und holt Frisur, Makeup, Körper und Outfits in dasselbe Panel. Es öffnet sich überall im Level mit **B**; kein Weg mehr zur Garderobe oder zum Spiegel.

Auch im [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867) erhältlich. Derselbe Mod, dieselben Dateien – eine Quelle wählen, nicht beide.

> ⚠ **Gemacht für Spielversion 0.6.x.** Ein Spiel-Update, das die Kleidungs-/Makeup-Tabellen oder den Kamera-Manager ändert, kann den Mod kaputt machen.

## Installation

Das Archiv enthält zwei Pak-Dateien, die in zwei verschiedene Ordner gehören (Pfade relativ zur Spielinstallation, z. B. *Steam\steamapps\common\TheKillingAntidote\*):

1. **AltUI.pak** → *TheKillingAntidote\Mods\*
2. **AltUI_Hook_P.pak** → *TheKillingAntidote\Content\Paks\~mods\* – den Ordner **~mods** anlegen, falls er nicht existiert (der Name beginnt mit einer Tilde). Der Spielordner-Name kommt im Pfad zweimal vor – das ist richtig so.
3. Spiel starten, in einem Level B drücken.

Beide Dateien sind nötig. Der Hook muss eines der Blueprints des Spiels überschreiben (den Player-Kamera-Manager), und das geht nur aus *~mods*; ohne ihn **passiert bei B nichts**. Der Hook kollidiert mit jedem anderen Mod, der *TKA_PlayerCameraManager* ersetzt (keiner bekannt).

**„B tut nichts“** → die Hook-Datei fehlt oder liegt im falschen Ordner. Sie muss in *Content\Paks\~mods* liegen, nicht in *Mods*.

Deinstallation: die zwei Dateien löschen. Die eigenen Speicherdateien des Mods (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav* und die Look-Fotos in *Saved\SaveGames\AltUI\*) können ebenfalls gelöscht werden; sonst wird nichts angefasst – Kleidung, Outfits, Makeup und Frisur laufen über die Speicherdateien des Spiels.

## Was es kann

* **Kleidung** – jedes Teil, das Spiel und Mods kennen, nach Slot gruppiert, Unterreiter pro Mod (einklappbar), Suche, Filter „nur Besessene“ / „nur Favoriten“ / „nur Vanilla“, Favoriten, Farbe über die Palette des Spiels, Farb-Reset, in den Rucksack und zurück, Teile ausblenden.
* **Outfits** – die Outfit-Vorlagen des Spiels, mit Namen (Rechtsklick → umbenennen).
* **Looks** – ein kompletter Look (Kleidung mit Farben, Frisur und Haarfarbe, Makeup, Augen, Haut, Körper-Regler, Body-Mod), gespeichert mit einem Ganzkörperfoto aus dem Spiel. Anwenden, aktualisieren, umbenennen, löschen.
* **Rucksack** – was Jodi trägt und dabeihat: anziehen, ausziehen, reparieren, zurück in die Garderobe, aufräumen.
* **Frisur** – alle Frisuren, Haarfarbe, 14 natürliche Haarfarben, Werkseinstellung.
* **Aussehen** – Haut, jeder Makeup-Typ, Augen, Aussehen-Vorlagen mit Symbolen.
* **Körperform** – Regler für Brust / Taille, ein Umschalter für installierte Body-Mods und – bei konvertierten Bodies – Bone-Regler: Skalierung, Busen, Taille extra, Po/Hüfte, Oberschenkel, Waden, Arme, Hände, Füße, je Body gespeichert.
* **Optionen** – Taste für das Panel, Sprache, Scroll-Geschwindigkeit, Kachelgröße, Länge der Gruppennamen und Höhe der Gruppenzeile, freier Bildschirmanteil für Jodi, Kamera-FOV / -Abstand / -Schwenk, Farbschema und Deckkraft, „Unterwäsche darf ausgezogen werden“, „Nicht im Besitz“ gesperrt / ausgegraut / wie im Besitz, Slot-Konflikte des Spiels (BH vs. Shirt …) freigeben, gleichnamige Gruppen / Mods zusammenlegen, Tooltip-Optionen.
* **Verwaltung** – eigene Anzeigenamen für Mods, Gruppen, Teile, Frisuren, Haut und Makeup – überall im Panel und in der Suche; „Umbenennen…“ im Kontextmenü jeder Kachel; als JSON exportier-/importierbar mit `altui_names.pyz`.
* Rückgängig / Wiederholen (5 Schritte), Tooltips zeigen, aus welchem Mod ein Teil stammt.

Sprachen: Englisch, Deutsch, Chinesisch, Russisch, Spanisch (automatisch erkannt, in den Optionen umschaltbar).

## Steuerung

* **B** – öffnen / schließen (in den Optionen änderbar). **Esc** schließt.
* Linksklick – auswählen / anziehen / anwenden. Rechtsklick – Kontextmenü. Mausrad – scrollen.
* Solange das Panel offen ist, kann Jodi nicht laufen; Ziehen auf dem Hintergrund dreht die Kamera, +/− holt die Kamera näher / weiter weg. Die zwei Rundknöpfe darüber öffnen eine freie Kamera (Maus dreht, W A S D / Q E bewegen, Shift schneller, Rad = Tempo, bis 6 m um Jodi, stoppt an Wänden; Esc zurück) und den Foto-Modus des Spiels (Esc zurück).

## Body-Mods

Body-Replacer-Paks überschreiben alle dieselbe Spieldatei, deshalb kann nur einer aktiv sein. **bodypak.pyz** (im Archiv; Python 3.8+, keine Pakete) macht aus einem Replacer ein normales Mod-Pak, das das Mesh unter einem eigenen Pfad behält; beliebig viele konvertierte Bodys können nebeneinander installiert sein und erscheinen als Chips im Reiter Körperform.

```
python bodypak.pyz SomeBodyReplacer.pak --name Body_Some --title SomeBody
```

Das erzeugte *Body_Some.pak* nach *TheKillingAntidote\Mods\* kopieren und den ursprünglichen Replacer entfernen (oder in *~mods* lassen – er wird dann zum Chip „Standard“).

Schritt-für-Schritt-Anleitung mit je einem Beispiel für Windows und Linux (englisch): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Kompatibilität

Gemacht für Spielversion 0.6.x. Funktioniert mit Kleidungs-, Frisur-, Makeup- und Karten-Mods von Nexus und aus dem Workshop – sie erscheinen einfach in den Listen.

## Updates

Eine neue Version ist ein neues Archiv mit beiden Dateien; einfach über die alten kopieren. Die Hook-Datei ändert sich selten – sie startet nur das Panel und bewegt die Kamera, alles andere steckt in AltUI.pak. Jeder Changelog-Eintrag nennt, ob sich der Hook geändert hat; steht dort „unchanged“, kann deine vorhandene bleiben. Ein neuer Hook ist nur nötig, wenn der Changelog es sagt oder wenn ein Spiel-Update den Player-Kamera-Manager ersetzt.

Es sind keine Spiel-Assets enthalten; alles im Pak ist generiert.

## Quellcode & Fehlermeldungen

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – Quellcode (MIT), alle Downloads, Fehlermeldungen.
