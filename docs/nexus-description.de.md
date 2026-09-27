# AltUI – Garderobe- und Aussehen-Panel

Deutsche Fassung der Beschreibung der [AltUI-Seite auf Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). Maßgeblich ist das englische Original auf der Nexus-Seite.

Die Garderobe des Spiels gibt jedem Mod-Autor einen eigenen Reiter. Mit ein paar Kleidungs-Mods ist dieselbe Art von Teil über ein Dutzend Reiter verstreut, und suchen kann man nicht. AltUI sortiert jedes Teil aus dem Spiel und aus allen installierten Mods in **eine Liste pro Slot** (Oberteile, Röcke, Schuhe, …), mit Suche, Filtern, Favoriten und Ausblenden – und holt Frisur, Makeup, Körper und Outfits in dasselbe Panel. Es öffnet sich überall im Level mit **B**; kein Weg mehr zur Garderobe oder zum Spiegel.

Auch im [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867) erhältlich. Derselbe Mod, dieselben Dateien – eine Quelle wählen, nicht beide.

> ⚠ **Gemacht für Spielversion 0.6.x.** Ein Spiel-Update, das die Kleidungs-/Makeup-Tabellen oder den Kamera-Manager ändert, kann den Mod kaputt machen.

## Installation

**AltUI.pak** ist der ganze Mod; eine zweite Datei muss ihn starten. Dafür gibt es zwei Wege – einer genügt, beide zusammen gehen auch. Pfade sind relativ zur Spielinstallation, z. B. *Steam\steamapps\common\TheKillingAntidote\*; der Spielordner-Name kommt darin zweimal vor, das ist richtig so.

**1. Mit dem Blueprint Loader (AltUI ersetzt nichts vom Spiel)**

1. **TKA_BlueprintLoader.pak** von [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) holen und nach *TheKillingAntidote\Content\Paks\~mods\* legen – den Ordner **~mods** anlegen, falls er nicht existiert (der Name beginnt mit einer Tilde).
2. **AltUI.pak** aus dem Archiv hier → *TheKillingAntidote\Mods\*
3. Spiel starten, in einem Level B drücken.

AltUI.pak bringt eine Tabelle mit, die der Loader liest, und der Loader startet daraus das Panel. Derselbe Loader startet jeden anderen Mod, der so eine Tabelle mitbringt – deshalb ist das der Weg, wenn du mehrere davon benutzt.

**Beim Umstieg von einer älteren AltUI-Version: Liegt noch eine AltUI_Hook_P.pak in ~mods, diese löschen. Der Hook beansprucht die Kameraklasse für sich, und einer von vor 1.5.0 startet den Loader nicht – das Panel öffnet dann zwar, die Ansicht rückt aber nicht zur Seite, und Mods, die für den Loader gebaut sind, bleiben tot.**

**2. Mit dem Hook-Pak (kein zweiter Mod nötig)**

1. **AltUI.pak** → *TheKillingAntidote\Mods\*
2. **AltUI_Hook_P.pak** → *TheKillingAntidote\Content\Paks\~mods\* – dieselbe Ordnerregel wie oben.
3. Spiel starten, in einem Level B drücken.

Der Hook ersetzt eines der Blueprints des Spiels (den Player-Kamera-Manager) und startet von dort das Panel; das geht nur aus *~mods*. Jeder Mod, der dasselbe Blueprint ersetzt, kollidiert mit ihm – der Blueprint Loader ist so einer, und genau dieses Paar ist die Ausnahme: sind beide installiert, gewinnt der Hook die Klasse und startet den Loader selbst, sodass Mods, die den Loader brauchen, weiterlaufen.

**„B tut nichts“** → nichts hat das Panel gestartet: entweder fehlt die zweite Datei, oder sie liegt in *Mods* statt in *Content\Paks\~mods*.

Die Kameraführung neben dem offenen Panel hängt nicht mehr am Hook – sie hängt sich an den Kamera-Manager, den das Level ohnehin hat, auch an den des Spiels.

Deinstallation: die kopierten Dateien löschen. Die eigenen Speicherdateien des Mods (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav*, *AltUI_Names.sav*, die Look-Fotos in *Saved\SaveGames\AltUI\* und die Waffen-Kacheln in *Saved\SaveGames\WeaponIcons\*) können ebenfalls gelöscht werden; sonst wird nichts angefasst – Kleidung, Outfits, Makeup und Frisur laufen über die Speicherdateien des Spiels.

## Was es kann

* **Kleidung** – jedes Teil, das Spiel und Mods kennen, nach Slot gruppiert, Unterreiter pro Mod (einklappbar), Suche, Filter „nur Besessene“ / „nur Favoriten“ / „nur Vanilla“, Favoriten, Farbe über die Palette des Spiels, Farb-Reset, in den Rucksack und zurück, Teile ausblenden.
* **Outfits** – die Outfit-Vorlagen des Spiels, mit Namen (Rechtsklick → umbenennen).
* **Looks** – ein kompletter Look (Kleidung mit Farben, Frisur und Haarfarbe, Makeup, Augen, Haut, Körper-Regler, Body-Mod), gespeichert mit einem Ganzkörperfoto aus dem Spiel. Anwenden, aktualisieren, umbenennen, löschen.
* **Rucksack** – was Jodi trägt und dabeihat: anziehen, ausziehen, reparieren, zurück in die Garderobe, aufräumen.
* **Frisur** – alle Frisuren, Haarfarbe, 14 natürliche Haarfarben, Werkseinstellung.
* **Aussehen** – Haut, jeder Makeup-Typ, Augen, Aussehen-Vorlagen mit Symbolen.
* **Körperform** – Regler für Brust / Taille, ein Umschalter für installierte Body-Mods und – bei konvertierten Bodies – Bone-Regler: Skalierung, Busen, Taille extra, Po/Hüfte, Oberschenkel, Waden, Arme, Hände, Füße, je Body gespeichert.
* **Waffen** – je Waffe ein Modell und ein Skin, nebeneinander aus allen Waffen-Mods, mit gerendertem Bild auf jeder Kachel.
* **Posen** – jede Aktionsanimation des Spiels und der Pose-Mods, sortiert nach stehend, sitzend und liegend.
* **Optionen** – Taste für das Panel, Sprache, Scroll-Geschwindigkeit, Kachelgröße, Länge der Gruppennamen und Höhe der Gruppenzeile, freier Bildschirmanteil für Jodi, Kamera-FOV / -Abstand / -Schwenk, Farbschema und Deckkraft, „Unterwäsche darf ausgezogen werden“, „Nicht im Besitz“ gesperrt / ausgegraut / wie im Besitz, Slot-Konflikte des Spiels (BH vs. Shirt …) freigeben, gleichnamige Gruppen / Mods zusammenlegen, Tooltip-Optionen.
* **Verwaltung** – eigene Anzeigenamen für Mods, Gruppen, Teile, Frisuren, Haut und Makeup – überall im Panel und in der Suche; „Umbenennen…“ im Kontextmenü jeder Kachel; als JSON exportier-/importierbar mit `altui_names.pyz`.
* Rückgängig / Wiederholen (5 Schritte), Tooltips zeigen, aus welchem Mod ein Teil stammt.

Sprachen: Englisch, Deutsch, Chinesisch, Russisch, Spanisch, Polnisch (automatisch erkannt, in den Optionen umschaltbar).

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

## Waffen-Mods

Waffen-Mods ersetzen je Waffe dieselben Spieldateien, deshalb schließen sich zwei für dieselbe Waffe gegenseitig aus, und im Spiel lässt sich nicht zwischen ihnen wechseln. **weaponpak.pyz** (im Archiv; Python 3.8+, keine Pakete) macht aus so einem Replacer ein eigenes Mod-Pak; beliebig viele davon können nebeneinander installiert sein, und Modell und Skin werden im Reiter Waffen je Waffe gewählt und gemerkt.

```
python weaponpak.pyz SomeWeaponReplacer.pak --name SomeGun --title "Some gun"
```

*--name* wird Teil des Dateinamens (Buchstaben, Ziffern und _), *--title* ist der Text auf dem Chip, und *--weapon* braucht es nur, wenn der Ordnername der Mod nicht verrät, für welche Waffe sie ist. Ein Pak kann einen Skin, ein Modell oder beides mitbringen. Das erzeugte *WeaponAltUI_SomeGun.pak* nach *TheKillingAntidote\Mods\* kopieren und den ursprünglichen Replacer entfernen – sonst überschreibt er die Waffe weiter, egal was im Panel gewählt ist.

Schritt-für-Schritt-Anleitung mit je einem Beispiel für Windows und Linux (englisch): [WEAPON_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/WEAPON_MODS.md)

## Einstellungen anderer Mods

Mods, die man im Spiel bedient – etwa eine Lampe – können ihre Einstellungen in AltUI unterbringen, statt eigene Tasten zu belegen. Ein Reiter **Mods** listet sie dann auf, mit Schaltern, Schiebereglern, Zahlen, Auswahlen, Farben, Textfeldern und Buttons im Stil von AltUI. Der Reiter erscheint nur, wenn so ein Mod installiert ist.

Für Mod-Autoren (englisch): [MOD_UI.md](https://github.com/Zyiakk/AltUI/blob/main/MOD_UI.md) beschreibt die zwei Datentabellen und das Interface, die ein Mod braucht; ein fertiger Beispiel-Mod zum Installieren und Nachbauen liegt in [examples/AltUIMod_Example](https://github.com/Zyiakk/AltUI/tree/main/examples/AltUIMod_Example).

## Kompatibilität

Gemacht für Spielversion 0.6.x. Funktioniert mit Kleidungs-, Frisur-, Makeup- und Karten-Mods von Nexus und aus dem Workshop – sie erscheinen einfach in den Listen.

## Updates

Eine neue Version ist ein neues Archiv; AltUI.pak einfach über die alte Datei kopieren. Der Blueprint Loader selbst braucht nichts – er ist ein eigener Mod und wird auf seiner eigenen Seite aktualisiert. Eine alte AltUI_Hook_P.pak darf aber nicht in ~mods liegen bleiben. Sie ist die Datei, die die Kameraklasse beansprucht, und eine von vor 1.5.0 startet den Loader nicht – dann öffnet das Panel, ohne dass die Ansicht zur Seite rückt, und jeder Mod, der für den Loader gebaut ist, bleibt tot. Also löschen oder durch die aktuelle ersetzen. Mit dem Hook-Pak: es ändert sich selten, denn es startet nur das Panel, alles andere steckt in AltUI.pak. Jeder Changelog-Eintrag nennt, ob sich der Hook geändert hat; steht dort „unchanged“, kann deine vorhandene bleiben. Ein neuer Hook ist nur nötig, wenn der Changelog es sagt oder wenn ein Spiel-Update den Player-Kamera-Manager ersetzt.

Es sind keine Spiel-Assets enthalten; alles im Pak ist generiert.

## Was die Kombinationen bewirken

AltUI.pak ist die Mod; eine zweite Datei muss sie starten. Was dabei herauskommt:

* **AltUI.pak allein** – nichts startet das Panel – B tut nichts.
* **AltUI.pak + Blueprint Loader** – der Loader liest AltUIs Tabelle und startet das Panel. AltUI selbst ersetzt nichts am Spiel; der Loader ersetzt die Kameraklasse des Spiels, so arbeitet er.
* **AltUI.pak + AltUI_Hook_P.pak** – der Hook ersetzt den Kamera-Manager des Spiels und startet das Panel.
* **AltUI.pak + beides** – geht, und nichts geht verloren. Beide ersetzen dieselbe Spielklasse, nur eine der zwei Paks gewinnt sie – und welche auch immer: AltUI startet, über die Tabelle des Loaders oder über den Hook, der dann zusätzlich den Loader selbst startet, damit Mods für ihn weiterlaufen.
* **Hook oder Loader ohne AltUI.pak** – nichts – die Mod selbst fehlt.

## Was es nicht kann

Drei Grenzen, die man kennen sollte:

* **Make-up wird getönt, nicht umgefärbt.** Die Farbe wird mit der vorhandenen Zeichnung multipliziert: Blasses oder Neutrales nimmt sie fast voll an, Dunkles lässt sich nur abdunkeln oder verschieben. Weiß heißt „unverändert“, nicht weißes Make-up.
* **Die Farben zeigen sich im Spiel, nicht im Hauptmenü.** AltUI legt sie auf Jodi, solange du in einem Level bist – dort läuft es. Im Hauptmenü steht sie in den Werksfarben des Spiels, was immer du gewählt hast.
* **Ein umgewandelter Körper kann unter enger Kleidung durchscheinen.** Das Spiel drückt solche Stellen mit Morph-Targets flach, die am Körper-Mesh hängen; bringt ein Mesh keine mit, ist nichts zum Drücken da. Das liegt am Körper, nicht an der Umwandlung: der Konverter behält, was das Original hat – und hat das Original keine, kann sie niemand nachträglich hinzufügen.

## Quellcode & Fehlermeldungen

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – Quellcode (MIT), alle Downloads, Fehlermeldungen.
