## Über AltUI {#about}

AltUI ist eine Alternative zu Kleiderschrank und Aussehen von The Killing Antidote: ein einziges Panel für alles, und die Bildschirme des Spiels bleiben nutzbar. Es öffnet sich überall in einem Level mit B – ohne Weg zum Kleiderschrank oder zum Spiegel.

Jedes Teil aus dem Spiel und aus allen installierten Mods steht in einer Liste pro Slot, mit Suche, Filtern, Favoriten und Ausblenden. Frisur, Make-up, Körper, Gesicht, Posen, Waffen sowie gespeicherte Outfits und Looks liegen im selben Panel, ebenso Ragdolls – Kopien von Jodi, Zombies und Menschen zum Aufstellen und Posieren – und Jodis Geh- und Renntempo.

Das Panel öffnet sich auf dem Reiter, auf dem es geschlossen wurde. Reiter, die du nicht brauchst, lassen sich unter Optionen › Reiter abschalten.

Ein Reiter Inventar verschiebt Gegenstände zwischen Jodis Rucksack und der Hyper Item-Box, und aus Looks werden Follower und NPCs, die mit ihr gehen und kämpfen.

## Installation und Updates {#install}

AltUI.pak enthält den ganzen Mod und gehört nach TheKillingAntidote/Mods/. Eine weitere Datei startet ihn:

- der Blueprint Loader (ein eigener kleiner Mod, TKA_BlueprintLoader.pak in TheKillingAntidote/Content/Paks/~mods/) oder
- AltUIs eigener Hook, AltUI_Hook_P.pak im selben Ordner ~mods/.

Eines von beiden genügt; beide zusammen gehen auch. Mit AltUI.pak allein tut B nichts.

Ein Update ersetzt normalerweise nur AltUI.pak. Das Changelog sagt, wann sich auch der Hook ändert; ein alter Hook darf nicht in ~mods/ bleiben.

Zum Entfernen die kopierten Dateien löschen:

- TheKillingAntidote/Mods/AltUI.pak
- TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak – wenn du den Hook benutzt
- TheKillingAntidote/Content/Paks/~mods/TKA_BlueprintLoader.pak – nur, wenn kein anderer Mod ihn braucht

AltUI legt eigene Daten im Spielstand-Ordner des Spiels ab, unter Windows %LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames. Um alles zu entfernen, dort auch diese löschen:

- AltUI.sav – Einstellungen und Auswahl
- AltUI_Looks.sav – gespeicherte Looks
- AltUI_Faces.sav – gespeicherte Gesichter
- AltUI_Names.sav – eigene Namen
- AltUI_Ragdolls.sav – Ragdoll-Szenen und -Posen
- AltUI_Followers.sav – Follower und NPCs
- der Ordner AltUI – Fotos von Looks, Gesichtern und Aussehen-Presets
- der Ordner WeaponIcons – Waffenbilder

Kleidung, Outfits, Make-up und Frisur stehen in den Spielständen des Spiels und bleiben erhalten.

Nach einem Spiel-Update oder mit einer Mod, die Tabellen des Spiels ersetzt, kann AltUI auf ein Spiel treffen, für das es nicht gemacht ist. Dann zeigt es eine Warnung, bevor es irgendetwas tut: „Trotzdem weiter (eigenes Risiko)“ gilt für diese Spielversion, „AltUI vorerst aus“ fragt im nächsten Level wieder.

## Bedienung {#controls}

- B öffnet und schließt das Panel (andere Taste unter Optionen › Steuerung); Esc schließt es.
- Linksklick wählt, zieht an oder wendet an; Rechtsklick öffnet das Kontextmenü einer Kachel, Zeile oder eines Reiters.
- Das Mausrad scrollt; die Geschwindigkeit steht unter Optionen › Steuerung.
- Solange das Panel offen ist, kann Jodi nicht laufen. Ziehen auf dem Hintergrund dreht die Kamera; Klick auf Jodi und Ziehen dreht sie – beim Schließen dreht sie sich zurück.
- + und − ändern den Kameraabstand in 5-%-Schritten, das Mausrad über Jodi in 4-%-Schritten.
- Die drei runden Knöpfe über + und − öffnen eine freie Kamera (Maus dreht, W A S D und Q E bewegen, Shift ist schneller, das Mausrad stellt die Geschwindigkeit, Esc zurück), den Fotomodus des Spiels (Esc zurück) und den Ragdoll-Modus (siehe „Ragdoll-Modus“).
- Rückgängig und Wiederherstellen (fünf Schritte) stehen in der Statusleiste unten.
- 4 gedrückt halten öffnet das Schnellmenü (siehe „Schnellmenü“).
- Im Hauptmenü öffnet B ein kleines Menü: die drei Menü-Szenen und die Lade-Szene, die nächste Kamera, Menü und Texte des Spiels ausblenden (Esc holt sie zurück).

## Kleidung {#clothes}

Links die Slots, rechts die Teile des gewählten Slots.

- Klick auf ein Teil zieht es an, Klick auf ein getragenes zieht es aus.
- Die Chips über der Liste filtern nach Mod oder Gruppe; „...“ klappt die Chip-Zeilen ein. Ein Suchfeld engt die Chips ein, die Suche über der Liste findet Teile nach Name, Mod oder Gruppe.
- Filter: nur Besitz, nur Favoriten, nur Vanilla, nur getragen.
- Rechtsklick auf ein Teil: Favorit, Ausblenden, Farbe über die Palette des Spiels, Farbe zurücksetzen, in den Rucksack, umbenennen, nur diese Gruppe, Mod-Inhalt anzeigen, im Reiter anzeigen.
- Der Tooltip zeigt, aus welchem Mod ein Teil stammt.
- Schaden (im Kontextmenü): 0 bis 100 %, an einem getragenen Teil sofort; bei jedem anderen Teil wird er gemerkt, bis es getragen wird. Getragene Teile ohne Schadens-Texturen haben keinen Regler.
- Unter der Farbpalette des Spiels zeigt ein Feld die Farbe als #RRGGBB; einen Code eintippen und mit Enter bestätigen setzt ihn. „Merken“ behält die Farbe in AltUI, „Einsetzen“ legt sie auf ein anderes Teil oder einen anderen Slot.
- Die Suche findet eine Mod auch über den Namen ihres Paks, hier und in jedem anderen Reiter.

## Outfits {#outfits}

Die gespeicherten Outfits des Spiels – dieselben, die Kleiderschrank und Spiegel benutzen.

- Die „+“-Kachel speichert, was Jodi gerade trägt, als neues Outfit.
- Klick auf ein Outfit zieht es an.
- Rechtsklick: Anziehen, Inhalt anzeigen, ins Schnellmenü oder heraus, Umbenennen, nach links / nach rechts / an den Anfang / ans Ende, Löschen.
- Ein Outfit ohne eigenen Namen heißt „Outfit“ mit seinem Platz in der Liste.
- Kachelgröße und wie viele Teile eine Kachel zeigt, stehen unter Optionen › Kacheln.

## Looks {#looks}

Ein Look ist alles auf einmal: Kleidung mit ihren Farben, Frisur und Haarfarbe, Make-up, Augen, Haut, Körperregler, Body-Mod und Gesicht.

- Die „+“-Kachel speichert den aktuellen Look mit einem Ganzkörperfoto – frontal oder wie du sie gerade siehst.
- Klick auf einen Look wendet ihn an.
- Rechtsklick: Inhalt anzeigen, Umbenennen, Aktualisieren (Foto frontal oder wie gesehen), Verschieben, Löschen, ins Schnellmenü oder heraus.
- Rechtsklick außerdem: „Als Ragdoll spawnen“, „Als Follower spawnen“, „Als NPC spawnen“ (siehe „Ragdolls“ und „Follower“).

## Rucksack {#bag}

Was Jodi trägt und was sie dabeihat.

- Klick auf ein getragenes Teil zieht es aus, Klick auf ein mitgeführtes zieht es an.
- Rechtsklick: Anziehen oder Ausziehen, Reparieren (braucht ein Nähset), aus dem Rucksack entfernen, zurück in den Kleiderschrank.
- „Rucksack aufräumen“ entfernt die Teile, die nicht getragen werden und auch im Kleiderschrank sind.
- „Alles in den Rucksack“ zieht jedes getragene Teil aus und legt es in den Rucksack.
- Im Kontextmenü gibt es auch den Schadensregler (siehe „Kleidung“).

## Inventar {#inventory}

Jodis Gegenstände und die Hyper Item-Box, eine Liste unter der anderen.

- Die Chips filtern nach den Gruppen des Spiels (Waffen, Munition, Waffenzubehör, Werkzeug …). Das Gewicht zeigt, was Jodi trägt, was sie tragen kann und wie weit sie überladen ist.
- Ein Klick legt einen Gegenstand in die Box oder nimmt einen heraus. Rechtsklick: die Hälfte oder alle, verwenden, untersuchen, wegwerfen, Schnellwahl 1 oder 2, Munition entnehmen, „Zubehör …“ (öffnet die Waffe im Reiter Waffen).
- Das Kontextmenü eines Stapels endet mit „Anzahl“: Regler und Zahlenfeld, darunter je Ziel ein Eintrag mit dieser Zahl („5 in die Box“, „5 nehmen“). Enter im Feld führt den ersten Eintrag aus. Im Katalog zählt die Zahl Stück, das Feld nimmt mehr, als der Regler erreicht. Waffen und Einzelstücke haben keine Anzahl.
- „Alle wegwerfen“ legt je Packung ein Objekt auf den Boden. Ab 100 Objekten fragt ein Fenster zuerst: „Abbrechen“, „Stattdessen vernichten“ (die Gegenstände sind weg, nichts fällt) oder „Trotzdem ablegen“ – so viele Objekte mit Physik auf einmal können das Spiel abstürzen lassen. Esc bricht ab.
- Alles läuft über die Funktionen des Spiels, die Regeln des Spiels bleiben also – Überladen eingeschlossen.
- „...“ über einer Liste klappt sie ein, ↑↓ gibt ihr die ganze Höhe (noch einmal: zurück).
- Auf Karten, auf denen das Spiel den Rucksack nie speichert (zum Beispiel der Schießstand), sagt der Reiter das: Was du behalten willst, gehört in die Box.
- „Alle Items“ ist standardmäßig aus (Optionen › Allgemein): jeder Gegenstand des Spiels als dritte Liste mit eigener Suche. Ein Klick legt eine Packung in den Rucksack; Rechtsklick: fünf, oder in die Box.
- „Waffen automatisch ausrüsten“ (Optionen › Allgemein, standardmäßig an): Eine Waffe aus der Box oder dem Katalog kommt wie im Spiel in Jodis Hand; aus, behält sie, was sie hält.
- Die Kachelgröße dieses Reiters steht unter Optionen › Kacheln.

## Frisur {#hair}

Alle Frisuren aus dem Spiel und aus Mods.

- Klick auf eine Frisur setzt sie auf.
- „Haarfarbe...“ öffnet die Palette des Spiels; „Natürliche Haarfarben“ zeigt 14 fertige Farben.
- Rechtsklick: Haarfarbe zurücksetzen, umbenennen, Mod-Inhalt anzeigen.
- Rechtsklick auf eine Frisur aus einer Mod: „Mod umbenennen…“.

## Posen {#poses}

Jede Aktionsanimation, die das Spiel und deine Posen-Mods kennen – die Liste hinter der „Rhythmus“-App des Handys.

- Klick auf eine Pose spielt sie ab; erneuter Klick oder „Pose beenden“ stoppt sie.
- Posen sind nach Haltung (stehend, sitzend, liegend) und nach Kapitel sortiert; Chips filtern nach Mod, die Suche findet Titel.
- Rechtsklick: Favorit, Ausblenden, als stehend / sitzend / liegend / in Bewegung einordnen, umbenennen, ins Schnellmenü.
- Rechtsklick „Als Idle verwenden“: Die Pose beginnt nach 1,5 s Stillstand und endet, wenn Jodi losgeht, eine Waffe zieht oder sich duckt; „Nicht mehr als Idle“ schaltet das ab.
- „Alle einmessen“ spielt jede Pose ohne Einordnung einmal ab und ordnet sie ein.
- Ein Lautsprecher in der Ecke einer Kachel zeigt eine Pose mit Ton.

## Waffen {#weapons}

Links ein Eintrag pro Waffe, Nahkampfwaffen eingeschlossen. Für jede Waffe werden Modell, Skin und Schussgeräusch getrennt gewählt.

- Oben die Modelle – das des Spiels und jeder installierte Modell-Mod.
- Unten die Skins – die Lackierungen des Spiels (ohne Sprühdose) und jeder installierte Skin-Mod.
- Sound: das eigene Schussgeräusch der Waffe („Original“) und jedes installierte Schussgeräusch für sie. Ein Klick wählt den Sound und spielt ihn ab; jede andere Waffe behält ihren. Ein montierter Schalldämpfer mit eigenem Sound hat weiter Vorrang.
- Die Chips darüber filtern alle drei Abschnitte zugleich. Rechtsklick auf eine Kachel: Favorit, Ausblenden, nur dieser Mod.
- Die Wahl bleibt erhalten und wird wieder aufgelegt, wenn die Waffe aufgehoben oder aus der Lagerkiste geholt wird.
- Eine Lackierung, die im Spiel mit einer Sprühdose aufgetragen wurde, bleibt: Sie wird zum gewählten Skin.
- Rechtsklick auf ein Mod-Modell: Skins darauf erzwingen, Magazin, Optik, Schalldämpfer oder Griff ausnehmen, eigenes Bild des Mods zeigen.
- Waffen-Mods und Schussgeräusch-Mods müssen erst mit weaponpak.pyz umgewandelt werden; siehe die Anleitung WEAPON_MODS auf der Seite des Mods.
- Waffenzubehör: eine Zeile je Slot, den die Waffe hat (Zielfernrohr, Lauf, Griff, Magazin), „Keins“ zuerst. Teile kommen aus dem Rucksack oder aus der Box und werden dann in den Rucksack genommen. Zubehör kommt nur an Waffen, die Jodi dabeihat; die Waffe behält das hier gewählte Modell, den Skin und den Sound.
- „Item-Bilder zeigen“ in der Statusleiste zeigt auf jeder Kachel das eigene Bild des Items oder der Mod statt des gerenderten.
- Rechtsklick auf ein Modell, einen Skin oder einen Sound aus einer Mod: „Mod umbenennen…“.

## Aussehen {#look}

Haut, jede Make-up-Art, Augen und die Aussehen-Presets des Spiels.

- Klick auf einen Eintrag legt ihn auf. Rechtsklick auf Make-up: mit der Palette des Spiels tönen, Tönung zurücksetzen.
- Augen: Iris- und Wimpernfarbe im Kontextmenü.
- Presets: Die „+“-Kachel speichert das aktuelle Aussehen mit Foto. Rechtsklick: Anwenden, Inhalt anzeigen, Umbenennen, Aktualisieren, Verschieben, Löschen, Schnellmenü.

## Körperform {#body}

- Brust- und Taillenregler des Spiels.
- Chips wechseln zwischen dem Körper des Spiels und jedem umgewandelten Body-Mod.
- Umgewandelte Bodys haben zusätzlich Knochen-Regler: Größe, Brust, Taille, Gesäß und Hüfte, Oberschenkel, Waden, Arme, Hände, Füße. Sie gelten je Body; „Form zurücksetzen“ stellt sie zurück.
- Brust und Po & Hüfte: Wackeln (0 % = nur Animation) stellt die Physik des Spiels ein und wirkt bei jedem Body; ein BH dämpft weiter wie im Spiel. Der Nippel-Regler wirkt nur, solange die Brust frei ist. Winkel und Hüftbreite gibt es nur bei umgewandelten Bodys; der Winkel wirkt umso stärker, je weniger es wackelt (bei 100 % gar nicht).
- Body-Ersatz-Mods müssen erst mit bodypak.pyz umgewandelt werden; siehe die Anleitung BODY_MODS auf der Seite des Mods.

## Gesicht {#face}

Jodis Gesichtsausdruck.

- Regler für die Ausdrücke des Spiels (entspannt, konzentriert, Lächeln, Schmerz, Schreck, müde, leidend), Blick und Mundformen.
- Ein angehaktes Feld behält seinen Wert, auch in Posen; ein nicht angehaktes bestimmt die Animation des Spiels. „Alle festlegen“ und „Alle ans Spiel“ schalten alle auf einmal.
- Ausdrücke werden überblendet (zusammen höchstens 100 %) oder addiert.
- Die „+“-Kachel speichert das aktuelle Gesicht mit Foto. Rechtsklick: Anwenden, Inhalt anzeigen, Umbenennen, Aktualisieren, Verschieben, Löschen.

## Mods {#mods}

Einstellungen anderer Mods, die sich bei AltUI anmelden: links ihre Einträge, rechts Schalter, Regler, Zahlen, Auswahlen, Farben, Textfelder, Tasten und Knöpfe des gewählten.

Der Reiter erscheint nur, wenn ein solcher Mod installiert ist.

## Optionen {#options}

Links die Kategorien.

- Allgemein: Sprache, wie viel vom Bildschirm für Jodi frei bleibt, Unterwäsche darf ausgezogen werden, wie Teile ohne Besitz erscheinen, der Kodex-Schalter für die Enzyklopädie, der Katalog „Alle Items“ und „Waffen automatisch ausrüsten“ für den Reiter Inventar.
- Kacheln: Kachelgröße, eigene Größen für Outfit-, Look- und Ragdoll-Kacheln, Teile pro Outfit-Kachel, keine Grenze bei langen Listen, Tooltip-Angaben, die Kachelgröße des Reiters Inventar.
- Gruppen: Gruppen oder Mods gleichen Namens zusammenfassen, Länge der Gruppennamen, Höhe des Chip-Bereichs, Chip-Suche.
- Kamera: Blickwinkel, Abstand, Höhe, Kamera folgt dem gewählten Slot.
- Steuerung: Panel-Taste, Scrollgeschwindigkeit, Kamerahöhe mit der rechten Maustaste, wie weit das Mausrad ein Ragdoll pro Raste hebt.
- Bewegung: Jodis eigenes Geh- und Renntempo (50 bis 200 %); Ducken und Springen bleiben, wie sie sind. „Zeitlupe an“ schaltet die Zeitlupe, „Tempo der Zeitlupe“ (5 bis 90 %, Standard 25 %) stellt ein, wie langsam sie läuft; der Schnellmenü-Eintrag „Zeitlupe an / aus“ tut dasselbe wie der Schalter. „Auf Standard zurücksetzen“ stellt Geh-, Renn- und Zeitlupentempo zurück. „Stehen“ wählt Jodis Steh-Animation: die des Spiels (Umsehen, Nägel ansehen, Bein ansehen, Vorsichtig, Verletzt, Posieren) und die installierter Idle-Mods (IdleAltUI_…).
- Schnellmenü: Taste, Deckkraft, was im Rad steht.
- Farben: jede Farbe des Panels, Deckkraft, Farbschemata unter einem Namen gespeichert.
- Slot-Konflikte: die Slot-Paare des Spiels lösen (zum Beispiel BH und Hemd), damit beide getragen werden können.
- Reiter: Text, Symbole oder beides in der Reiterleiste; Reiter abschalten.

## Verwaltung {#manage}

Eigene Anzeigenamen für Mods, Gruppen, Kleidung, Frisuren, Haut, Make-up, Posen und Aussehen-Presets.

- Die Namen gelten überall im Panel und werden von der Suche gefunden; der ursprüngliche Bezeichner bleibt suchbar und steht im Tooltip.
- Chips und eine Suche filtern die Liste; „nur Mods“ blendet die Einträge des Spiels aus; ↺ kehrt zum Standardnamen zurück.
- Mit altui_names.pyz lassen sich die Namen in eine Textdatei exportieren und wieder importieren.
- Waffen-Mods stehen bei den anderen Mods.

## Ragdolls {#ragdolls}

Figuren mit Physik zum Aufstellen und Posieren im Level: Kopien von Jodi, Zombies und Menschen.

- „+ Kopie von Jodi spawnen“ stellt eine Kopie vor sie, stehend und eingefroren in ihrer aktuellen Pose, mit allem, was sie trägt. Ein Look wird mit „Als Ragdoll spawnen“ in seinem Kontextmenü zur Figur.
- „Zombies und Menschen“: eine Bildkachel je Zombie-Art, dazu die Krankenschwester und eine Überlebende. Ein Klick spawnt sie; die Links unter einer Kachel spawnen ihre Varianten.
- Jede Figur hat eine Zeile: aktiv (Physik, sie fällt und lässt sich werfen) oder eingefroren (sie hält ihre Pose), „Gelenke ›“, alle sperren, alle lösen, entfernen. „Alle entfernen“ entfernt jede Figur.
- „Gelenke ›“ klappt die 17 Gelenke der Figur auf, jedes gesperrt, frei oder beweglich. Ein gesperrtes Gelenk bleibt steif, solange die Figur aktiv ist.
- Posen (in der aufgeklappten Zeile): ein Name und „Pose speichern“ halten fest, wie die Körperteile stehen. Eine Pose lässt sich auf jede Figur derselben Art laden, in jedem Level – Klick lädt, Rechtsklick: Laden / Löschen. Die Figur friert dabei ein und steht auf dem Boden.
- Szenen: „Szene speichern als“ hält jede Figur des Levels mit Aussehen, Ort, Pose und Gelenken fest; gleicher Name im selben Level überschreibt. Gezeigt werden nur die Szenen des aktuellen Levels. Ein Klick lädt eine Szene und ersetzt die vorhandenen Figuren; Rechtsklick: Laden / Löschen.

Mit der Maus auf einer Figur, neben dem Panel und im Ragdoll-Modus:

- Links-Ziehen an einer eingefrorenen Figur verschiebt sie über den Boden; das Mausrad hebt oder senkt sie beim Ziehen.
- Links-Ziehen an einer aktiven Figur greift das Körperteil unter der Maus; loslassen, und sie fällt.
- Rechts-Ziehen dreht die Figur um ihre Hüfte.
- Shift + Linksklick sperrt oder löst das angeklickte Gelenk.
- Shift + Rechtsklick auf eine eingefrorene Figur macht das Gelenk beweglich. Links-Ziehen an einem Körperteil unter einem beweglichen Gelenk bewegt dann nur diesen Teil; er bleibt, wo du loslässt – so wird eine Figur posiert.

Ohne Panel aktiviert oder friert das Schnellmenü Figuren ein: „Ragdoll: anvisierte aktivieren / einfrieren“ nimmt die Figur in der Bildmitte, „Ragdolls: aktiv / eingefroren“ schaltet alle um.

## Ragdoll-Modus {#ragmode}

Figuren ohne Panel bewegen und posieren, die Kamera frei im Raum. Start mit dem dritten runden Knopf über + und − oder aus dem Schnellmenü.

- Der Mauszeiger bleibt sichtbar; auf einer Figur geht alles wie neben dem Panel (siehe „Ragdolls“).
- W A S D und Q E bewegen die Kamera, Shift ist schneller; Shift + Mausrad stellt die Geschwindigkeit.
- Ziehen im Leeren dreht die Kamera.
- Esc oder B beendet den Modus.

## Follower {#followers}

Looks als Personen im Spiel: Ein Follower geht mit Jodi, kämpft und nimmt Befehle an; ein NPC bleibt, wo er ist, und verteidigt sich.

- Im Looks-Reiter Rechtsklick auf einen Look: „Als Follower spawnen“ oder „Als NPC spawnen“. Die Figur erscheint vor Jodi und trägt diesen Look.
- Der Reiter „Follower“ listet alle Figuren mit Status (folgt, wartet, NPC, inaktiv, gefallen) und Chips: „Folge mir“, „Warte hier“, „Herholen“, → NPC / → Follower, „Aktiv“, „Unverwundbar“ und „...“ (umbenennen, Look ändern, wiederbeleben, entfernen).
- Ein Klick auf eine Zeile wählt die Figur aus. Oben stehen Rucksack (links) und Hyper Item-Box (rechts): Ein Klick gibt ein Item an die ausgewählte Figur, eine Schusswaffe samt Lackierung und Zubehör. Ein Klick auf eine Kachel der Figur gibt das Item zurück in den Rucksack; Rechtsklick: alles, oder in die Box. „...“ über einer Liste klappt sie ein.
- Das Kontextmenü eines Stapels – bei Jodi oder der Figur – hat die Anzahl-Zeile wie im Reiter Inventar: „5 geben“, „5 nehmen“, in die Box.
- Die Kleidung besteht aus echten Stücken der Figur wie bei den NPCs des Spiels: Sie bekommt Schaden, kann abreißen und steht im Inventar-Dialog des Spiels, wo man sie auch tauschen kann. Unter einer Figur stehen ihre Stücke als Kacheln (beschädigte mit Markierung): Ein Klick zieht eines aus und legt es in Jodis Rucksack; Rechtsklick: mit einem Nähset aus Jodis Rucksack reparieren oder alle reparieren. In der Rucksack-Spalte listet „Kleidung“ Jodis Stücke: Ein Klick gibt eines an die ausgewählte Figur, die es anzieht (Schaden und Farben gehen mit).
- „Aktiv“ aus nimmt eine Figur mit allem, was sie trägt, aus der Welt; wieder an, kommt sie vor Jodi zurück.
- Eine Figur, die nicht unverwundbar ist, kann fallen. Sie bleibt in der Liste, „Wiederbeleben“ holt sie mit ihren Sachen zurück. Figuren werden nie zu Zombies.
- „Entfernen“ fragt nach; Items und Schusswaffen der Figur kommen in die Box, ihre Kleidung in Jodis Rucksack.
- „Look ändern“ wechselt in den Looks-Reiter: den Look anklicken, den die Figur tragen soll.

AltUI speichert die Figuren in einem eigenen Spielstand (AltUI_Followers.sav), der Spielstand des Spiels enthält sie nie. Folgende Follower kommen in jedes Level mit und sind nach dem Laden da; wartende Follower und NPCs bleiben in ihrem Level an ihrem Platz.

Schnellmenü: „Follower: Folge mir / Warte hier“ gilt für den Follower im Blick, „Alle Follower: folgen / warten“ für alle.

## Kodex {#kodex}

- Enzyklopädie: die Einträge des Archivs auf Jodis Bürocomputer, mit Bild und Text. Gezeigt werden nur die, die das Spiel freigeschaltet hat – oder alle mit dem Schalter unter Optionen › Allgemein.
- Passwörter: die Code-Schlösser des aktuellen Levels, das nächste zuerst, mit Entfernung und ob sie gesperrt sind. Jeder Code bleibt verdeckt, bis du ihn anklickst.
- AltUI-Handbuch: dieser Text.

## Schnellmenü {#quick}

4 gedrückt halten (andere Taste unter Optionen › Schnellmenü), und um die Maus öffnet sich ein Rad. Über einem Eintrag loslassen führt ihn aus; in der Mitte loslassen tut nichts.

- Einträge: Outfits, Looks, Gesichter, Aussehen-Presets, Posen, Reiter, Einstellungen anderer Mods und Aktionen: freie Kamera, Fotomodus, Ragdoll-Modus, Kopie von Jodi als Ragdoll, alle Ragdolls zwischen aktiv und eingefroren umschalten, anvisierte aktivieren / einfrieren, alle Ragdolls entfernen, eigenes Tempo an / aus.
- Weitere Aktionen: „Zeitlupe an / aus“, „Zeit anhalten / weiter“ (alles steht still; Panel und Kameras arbeiten weiter), „Jodi aus- / einblenden“ (mit Kleidung, Haaren und Waffe; im nächsten Level ist sie wieder da) und die Befehle an Follower (siehe „Follower“).
- Hinzufügen unter Optionen › Schnellmenü oder per Rechtsklick auf eine Kachel, einen Reiter oder den Eintrag eines Mods („Ins Schnellmenü“).
- Die Reihenfolge im Rad ist die Reihenfolge der Liste unter Optionen › Schnellmenü.

## Für Mod-Autoren {#modding}

- Kleidungs-Mods brauchen nichts Besonderes: AltUI liest die Tabellen des Spiels und ordnet jedes Teil seinem Slot zu.
- Body- und Waffen-Ersatz-Mods lassen sich mit bodypak.pyz und weaponpak.pyz umwandeln, damit mehrere nebeneinander installiert sein können; sie lassen sich auch direkt im Unreal Editor für AltUI bauen.
- Idle-Mods (ein Pak, das Jodis Idle-Animation ersetzt) lassen sich mit idlepak.pyz umwandeln: python3 idlepak.pyz <mod>.pak. Das neue IdleAltUI_….pak gehört nach Mods/ und erscheint unter Optionen › Bewegung › „Stehen“; das Idle des Spiels bleibt. AltUI muss installiert sein: Der Konverter baut das neue Pak zum Teil aus AltUI.pak und sucht es in den üblichen Steam-Ordnern; liegt es woanders, gibt man den Pfad mit --altui <Pfad zu AltUI.pak> an.
- Mods können ihre Einstellungen über zwei Datentabellen und eine Schnittstelle im Reiter Mods zeigen; MOD_UI.md im Quell-Repository beschreibt, wie.
