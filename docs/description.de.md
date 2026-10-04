# AltUI – Garderobe- und Aussehen-Panel

Deutsche Fassung der Beschreibung des [Steam-Workshop-Eintrags](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). Maßgeblich ist die [englische Fassung](description.en.md); die Workshop-Seite selbst zeigt eine Kurzfassung.

Die Garderobe des Spiels gibt jedem Mod-Autor einen eigenen Reiter. Mit ein paar Kleidungs-Mods ist dieselbe Art von Teil über ein Dutzend Reiter verstreut, und suchen kann man nicht. AltUI sortiert jedes Teil aus dem Spiel und aus allen installierten Mods in **eine Liste pro Slot** (Oberteile, Röcke, Schuhe, …), mit Suche, Filtern, Favoriten und Ausblenden – und holt Frisur, Makeup, Körper und Outfits in dasselbe Panel. Es öffnet sich überall im Level mit **B**; kein Weg mehr zur Garderobe oder zum Spiegel.

Auch auf [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (beide Dateien in einem Archiv). Derselbe Mod – eine Quelle wählen, nicht beide.

> ⚠️ **Warnung:** Gemacht für Spielversion 0.6.x. Ein Spiel-Update, das die Kleidungs-/Makeup-Tabellen oder den Kamera-Manager ändert, kann den Mod kaputt machen.

## ⚠ Installation – zuerst lesen

Das Abonnieren installiert den Mod selbst, **AltUI.pak**. Eine zweite Datei muss ihn starten, und die kann der Workshop nicht für dich ablegen, weil sie in einen Ordner des Spiels gehört, den der Workshop nicht anfasst. Ohne sie **passiert bei B nichts**. Dafür gibt es zwei Wege – einer genügt, beide zusammen gehen auch.

**1. Mit dem Blueprint Loader (AltUI ersetzt nichts vom Spiel)**

1. Diesen Eintrag abonnieren (das installiert **AltUI.pak**).
2. **TKA_BlueprintLoader.pak** holen: https://www.nexusmods.com/thekillingantidote/mods/994
3. Kopieren nach
   `Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Content\Paks\~mods\`
   Den Ordner **~mods** anlegen, falls er nicht existiert (der Name beginnt mit einer Tilde). Der Spielordner-Name kommt im Pfad zweimal vor – das ist richtig so.
4. Spiel starten, in einem Level B drücken.

AltUI bringt eine Tabelle mit, die der Loader liest, und startet daraus das Panel. Derselbe Loader startet jeden anderen Mod, der so eine Tabelle mitbringt – deshalb ist das der Weg, wenn du mehrere davon benutzt.

**Beim Umstieg von einer älteren AltUI-Version: Liegt noch eine AltUI_Hook_P.pak in ~mods, diese löschen. Der Hook beansprucht die Kameraklasse für sich, und einer von vor 1.5.0 startet den Loader nicht – das Panel öffnet dann zwar, die Ansicht rückt aber nicht zur Seite, und Mods, die für den Loader gebaut sind, bleiben tot.**

**2. Mit dem Hook-Pak (eine Datei, aus dem AltUI-Release)**

1. Diesen Eintrag abonnieren.
2. **AltUI_Hook_P.pak** herunterladen: https://github.com/Zyiakk/AltUI/releases/latest/download/AltUI_Hook_P.pak
3. In denselben *~mods*-Ordner wie oben kopieren.
4. Spiel starten, in einem Level B drücken.

Der Hook ersetzt *TKA_PlayerCameraManager* und startet von dort das Panel. Jeder Mod, der dasselbe Blueprint ersetzt, kollidiert mit ihm – der Blueprint Loader ist so einer, und genau dieses Paar ist die Ausnahme: sind beide installiert, gewinnt der Hook die Klasse und startet den Loader selbst, sodass Mods, die den Loader brauchen, weiterlaufen.

**„Ich habe abonniert, aber B tut nichts“** → nichts hat das Panel gestartet: entweder fehlt die zweite Datei, oder sie liegt in *Mods* oder im Workshop-Ordner statt in *Content\Paks\~mods*.

## Was es kann

* **Kleidung** – jedes Teil des Spiels und deiner Mods, eine Liste je Slot, mit Suche, Filtern, Favoriten und Ausblenden.
* **Outfits · Looks** – die Vorlagen des Spiels mit Namen, und komplette Looks (Kleidung samt Farben, Frisur, Makeup, Augen, Haut, Körper, Gesicht) mit Foto aus dem Spiel.
* **Rucksack · Frisuren · Aussehen** – was Jodi trägt und dabeihat; Frisuren und Haarfarben; Haut, Makeup und Augen, jeweils einfärbbar.
* **Körperform** – Brust- und Taillenregler, Umschalter für konvertierte Body-Mods, Knochenregler je Körper.
* **Gesicht** – Jodis Ausdruck, Blick und Mund als Regler; das Gesicht hält auch in Posen und beim Tanzen; gespeicherte Gesichter mit Foto, ihre Werte unter „Inhalt anzeigen“.
* **Waffen** – je Waffe ein Modell und ein Skin, nebeneinander aus allen Waffen-Mods, mit gerendertem Bild auf jeder Kachel.
* **Posen** – jede Aktionsanimation des Spiels und der Pose-Mods, sortiert nach stehend, sitzend und liegend.
* **Mods** – die Einstellungen anderer Mods, die sich dort eintragen: Schalter, Schieberegler, Zahlen, Auswahlen, Farben, Textfelder, Info-Zeilen, Tasten und Buttons. Nur sichtbar, wenn so ein Mod installiert ist.
* **Schnellmenü** – **4** halten (änderbar) öffnet ein Rad mit dem, was du oft brauchst: freie Kamera, Foto-Modus, ein gespeichertes Outfit, ein Look, Gesicht oder Preset, eine Lieblingspose, ein Reiter und Aktionen anderer Mods. Bis zu 32 Einträge, ausgewählt und sortiert in den Optionen; über einem Eintrag loslassen führt ihn aus. Ein Rechtsklick auf eine Kachel, einen Reiter oder den Eintrag eines Mods legt ihn ins Rad oder nimmt ihn heraus.
* **Optionen** – in Kategorien, links aus einer Liste gewählt: Panel-Taste, Sprache, Farben (Schemata lassen sich unter einem Namen speichern), Reiterleiste mit Icons, Text oder beidem, Kachelgrößen, für Outfits und Looks getrennt. Reiter, die du nicht brauchst, lassen sich abschalten.
* **Verwaltung** – eigene Anzeigenamen für Mods, Gruppen und Teile. Wie in Kleidung filtern Chips die Liste nach Mod oder Gruppe, und ein Suchfeld grenzt die Chips ein.
* Rückgängig / Wiederholen (5 Schritte), Tooltips mit dem Mod, aus dem ein Teil stammt.

Sprachen: Englisch, Deutsch, Chinesisch, Russisch, Spanisch, Polnisch, Französisch (automatisch erkannt, in den Optionen umstellbar).

## Steuerung

* **B** – öffnen / schließen (in den Optionen änderbar). **Esc** schließt.
* **4** – halten für das Schnellmenü (in den Optionen änderbar); über einem Eintrag loslassen führt ihn aus, in der Mitte loslassen tut nichts.
* Linksklick – auswählen / anziehen / anwenden. Rechtsklick – Kontextmenü. Mausrad – scrollen.

## Body-Mods

Body-Replacer-Paks überschreiben alle dieselbe Spieldatei, deshalb kann nur einer aktiv sein. Ein kleiner Konverter macht aus einem Replacer ein normales Mod-Pak, das das Mesh unter einem eigenen Pfad behält; beliebig viele konvertierte Bodys können nebeneinander installiert sein und erscheinen als Chips im Reiter Körperform.

Konverter (Python 3.8+, keine Pakete): https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

Schritt-für-Schritt-Anleitung mit je einem Beispiel für Windows und Linux (englisch): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Mod-Updates und die zweite Datei

Was das Panel startet, ist absichtlich vom Panel selbst getrennt: alles, was der Mod kann, steckt im Workshop-Pak. Wenn dieser Eintrag also über Steam aktualisiert wird, **funktioniert die Datei in *~mods* normalerweise weiter – du musst sie nicht anfassen**.

Der Blueprint Loader selbst braucht nichts: Er ist ein eigener Mod und wird auf seiner eigenen Seite aktualisiert. Eine AltUI_Hook_P.pak von vor 1.5.0 darf nicht in ~mods liegen bleiben (siehe den Hinweis unter Installation): löschen oder durch die aktuelle ersetzen.

**Hook ohne Blueprint Loader:** Seit 1.8.0 legt AltUI deinen Look auch im Hauptmenü und in der Lade-Szene auf Jodi. Mit dem Hook allein braucht das die aktuelle AltUI_Hook_P.pak – eine ältere dafür ersetzen; in Levels funktioniert die ältere weiter. Mit dem Blueprint Loader erledigt das AltUI.pak selbst.

Es sind keine Spiel-Assets enthalten; alles im Pak ist generiert.

## Was die Kombinationen bewirken

* **AltUI.pak allein** – nichts startet das Panel – B tut nichts.
* **AltUI.pak + Blueprint Loader** – der Loader liest AltUIs Tabelle und startet das Panel. AltUI selbst ersetzt nichts am Spiel; der Loader ersetzt die Kameraklasse des Spiels, so arbeitet er.
* **AltUI.pak + AltUI_Hook_P.pak** – der Hook ersetzt den Kamera-Manager des Spiels und startet das Panel.
* **AltUI.pak + beides** – geht, und nichts geht verloren. Beide ersetzen dieselbe Spielklasse, nur eine der zwei Paks gewinnt sie – und welche auch immer: AltUI startet, über die Tabelle des Loaders oder über den Hook, der dann zusätzlich den Loader selbst startet, damit Mods für ihn weiterlaufen.
* **Hook oder Loader ohne AltUI.pak** – nichts – die Mod selbst fehlt.

## Was es nicht kann

Zwei Grenzen, die man kennen sollte:

* **Make-up wird getönt, nicht umgefärbt.** Die Farbe wird mit der vorhandenen Zeichnung multipliziert: Blasses oder Neutrales nimmt sie fast voll an, Dunkles lässt sich nur abdunkeln oder verschieben. Weiß heißt „unverändert“, nicht weißes Make-up.
* **Ein umgewandelter Körper kann unter enger Kleidung durchscheinen.** Das Spiel drückt solche Stellen mit Morph-Targets flach, die am Körper-Mesh hängen; bringt ein Mesh keine mit, ist nichts zum Drücken da. Das liegt am Körper, nicht an der Umwandlung: der Konverter behält, was das Original hat – und hat das Original keine, kann sie niemand nachträglich hinzufügen.

## Quellcode & Fehlermeldungen

https://github.com/Zyiakk/AltUI – Quellcode (MIT), alle Downloads, Fehlermeldungen.
