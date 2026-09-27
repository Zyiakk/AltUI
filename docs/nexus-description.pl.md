# AltUI – panel szafy i wyglądu

Polska wersja opisu [strony AltUI na Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). Wiążący jest angielski oryginał na stronie Nexusa.

Szafa w grze daje każdemu autorowi moda własną zakładkę. Przy kilku modach z ubraniami ten sam rodzaj rzeczy jest rozrzucony po kilkunastu zakładkach i nie da się niczego wyszukać. AltUI porządkuje każdą rzecz z gry i ze wszystkich zainstalowanych modów w **jedną listę na slot** (góra, spódnice, obuwie, …), z wyszukiwaniem, filtrami, ulubionymi i ukrywaniem – a fryzurę, makijaż, ciało i stroje wciąga do tego samego panelu. Otwiera się wszędzie w poziomie klawiszem **B**; koniec z chodzeniem do szafy i do lustra.

Dostępny też w [Warsztacie Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). Ten sam mod, te same pliki – wybierz jedno źródło, nie oba naraz.

> ⚠ **Zrobione pod wersję gry 0.6.x.** Aktualizacja gry, która zmieni tabele ubrań / makijażu albo menedżera kamery, może zepsuć moda.

## Instalacja

**AltUI.pak** to cały mod; uruchomić go musi drugi plik. Są na to dwa sposoby – wystarczy jeden, oba naraz też działają. Ścieżki są względem instalacji gry, np. *Steam\steamapps\common\TheKillingAntidote\*; nazwa folderu gry występuje w niej dwa razy i tak ma być.

**1. Z Blueprint Loaderem (AltUI niczego w grze nie podmienia)**

1. Pobierz **TKA_BlueprintLoader.pak** z [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) i wrzuć do *TheKillingAntidote\Content\Paks\~mods\* – utwórz folder **~mods**, jeśli go nie ma (nazwa zaczyna się tyldą).
2. **AltUI.pak** z tutejszego archiwum → *TheKillingAntidote\Mods\*
3. Uruchom grę, w poziomie naciśnij B.

AltUI.pak niesie tabelę, którą loader czyta, i loader uruchamia z niej panel. Ten sam loader uruchamia każdy inny mod z taką tabelą – dlatego to jest droga dla kogoś, kto używa kilku takich modów.

**Przy przejściu ze starszej wersji AltUI: jeśli w ~mods nadal leży AltUI_Hook_P.pak, usuń go. Hook przejmuje klasę menedżera kamery, a ten sprzed 1.5.0 nie uruchamia loadera – panel wprawdzie się otworzy, ale widok nie odsunie się na bok, a mody zrobione pod loader nie wystartują.**

**2. Z pakiem hooka (drugi mod niepotrzebny)**

1. **AltUI.pak** → *TheKillingAntidote\Mods\*
2. **AltUI_Hook_P.pak** → *TheKillingAntidote\Content\Paks\~mods\* – ta sama zasada co wyżej.
3. Uruchom grę, w poziomie naciśnij B.

Hook podmienia jeden z blueprintów gry (menedżera kamery gracza) i stamtąd uruchamia panel; działa to tylko z *~mods*. Każdy mod, który podmienia ten sam blueprint, jest z nim w konflikcie – Blueprint Loader jest właśnie takim modem i akurat ta para jest wyjątkiem: przy obu zainstalowanych hook wygrywa klasę i sam uruchamia loadera, więc mody wymagające loadera działają dalej.

**„B nic nie robi”** → nic nie uruchomiło panelu: albo brakuje drugiego pliku, albo leży on w *Mods* zamiast w *Content\Paks\~mods*.

Kadrowanie kamery obok otwartego panelu nie zależy już od hooka – podpina się do menedżera kamery, który poziom ma i tak, również do tego z gry.

Odinstalowanie: usuń skopiowane pliki. Własne zapisy moda (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav*, *AltUI_Names.sav*, zdjęcia stylizacji w *Saved\SaveGames\AltUI\* i obrazki broni w *Saved\SaveGames\WeaponIcons\*) też możesz usunąć; poza tym nic nie jest ruszane – ubrania, stroje, makijaż i fryzura idą przez zapisy samej gry.

## Co potrafi

* **Ubrania** – każda rzecz, którą znają gra i mody, pogrupowana po slotach, podzakładki na mod (zwijane), wyszukiwanie, filtry „tylko posiadane” / „tylko ulubione” / „tylko vanilla”, ulubione, kolor z palety gry, reset koloru, do plecaka i z powrotem, ukrywanie rzeczy.
* **Stroje** – gotowe stroje gry, z nazwami (prawy przycisk → zmień nazwę).
* **Stylizacje** – kompletna stylizacja (ubrania z kolorami, fryzura i kolor włosów, makijaż, oczy, skóra, suwaki ciała, mod ciała) zapisana ze zdjęciem całej sylwetki z gry. Zastosuj, zaktualizuj, zmień nazwę, usuń.
* **Plecak** – co Jodi nosi i ma przy sobie: załóż, zdejmij, napraw, z powrotem do szafy, uporządkuj.
* **Fryzura** – wszystkie fryzury, kolor włosów, 14 naturalnych kolorów włosów, ustawienia fabryczne.
* **Wygląd** – skóra, każdy typ makijażu, oczy, gotowe wyglądy z ikonami.
* **Kształt ciała** – suwaki piersi / talii, przełącznik zainstalowanych modów ciała oraz – przy przekonwertowanych ciałach – suwaki kości: skala, biust, talia extra, pośladki/biodra, uda, łydki, ramiona, dłonie, stopy, zapisywane osobno dla każdego ciała.
* **Opcje** – klawisz panelu, język, szybkość przewijania, rozmiar kafelków, długość nazw grup i wysokość wiersza grup, część ekranu zostawiona dla Jodi, pole widzenia / odległość / przesuw kamery, kolorystyka i krycie, „można zdejmować bieliznę”, „nieposiadane” zablokowane / wyszarzone / jak posiadane, zwalnianie konfliktów slotów z gry (biustonosz vs. koszula …), łączenie grup / modów o tej samej nazwie, opcje podpowiedzi.
* **Zarządzanie** – własne nazwy wyświetlane dla modów, grup, rzeczy, fryzur, skór i makijażu – widoczne w całym panelu i uwzględniane w wyszukiwaniu; „Zmień nazwę…” w menu kontekstowym każdego kafelka; eksport / import jako JSON przez `altui_names.pyz`.
* Cofnij / ponów (5 kroków), podpowiedzi pokazują, z którego moda pochodzi dana rzecz.

Języki: angielski, niemiecki, chiński, rosyjski, hiszpański, polski (wykrywany automatycznie, przełączany w opcjach).

## Sterowanie

* **B** – otwiera / zamyka (zmienialne w opcjach). **Esc** zamyka.
* Lewy przycisk – wybierz / załóż / zastosuj. Prawy przycisk – menu kontekstowe. Kółko myszy – przewijanie.
* Dopóki panel jest otwarty, Jodi nie może chodzić; przeciąganie po tle obraca kamerę, +/− przybliża / oddala. Dwa okrągłe przyciski nad nimi otwierają wolną kamerę (mysz obraca, W A S D / Q E ruch, Shift szybciej, kółko = prędkość, do 6 m wokół Jodi, zatrzymuje się na ścianach; Esc powrót) oraz tryb zdjęć gry (Esc powrót).

## Mody ciała

Paki podmieniające ciało nadpisują wszystkie ten sam plik gry, więc aktywny może być tylko jeden. **bodypak.pyz** (w archiwum; Python 3.8+, bez dodatkowych pakietów) robi z takiego paka zwykły mod-pak, który trzyma mesh pod własną ścieżką; dowolnie wiele przekonwertowanych ciał może być zainstalowanych obok siebie i pojawia się jako chipy w zakładce Kształt ciała.

```
python bodypak.pyz SomeBodyReplacer.pak --name Body_Some --title SomeBody
```

Powstały *Body_Some.pak* skopiuj do *TheKillingAntidote\Mods\* i usuń pierwotny plik podmieniający (albo zostaw go w *~mods* – stanie się wtedy chipem „Standard”).

Instrukcja krok po kroku z przykładem dla Windowsa i dla Linuksa (po angielsku): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Zgodność

Zrobione pod wersję gry 0.6.x. Działa z modami ubrań, fryzur, makijażu i map z Nexusa i z Warsztatu – po prostu pojawiają się na listach.

## Aktualizacje

Nowa wersja to nowe archiwum; AltUI.pak wystarczy skopiować na stary plik. Sam Blueprint Loader niczego nie potrzebuje – jest osobnym modem i aktualizuje się na własnej stronie. Stary AltUI_Hook_P.pak nie może jednak zostać w ~mods. To ten plik przejmuje klasę menedżera kamery, a wersja sprzed 1.5.0 nie uruchamia loadera – wtedy panel się otworzy, ale widok nie odsunie się na bok, a mody zrobione pod loader nie wystartują. Usuń go albo zastąp aktualnym. Z pakiem hooka: zmienia się rzadko, bo tylko uruchamia panel, cała reszta siedzi w AltUI.pak. Każdy wpis w changelogu mówi, czy hook się zmienił; jeśli stoi tam „unchanged”, twój dotychczasowy może zostać. Nowy hook jest potrzebny tylko wtedy, gdy changelog tak mówi albo gdy aktualizacja gry podmieni menedżera kamery gracza.

Żadne zasoby gry nie są dołączone; wszystko w paku jest generowane.

## Co daje każda kombinacja

AltUI.pak to sam mod; potrzebny jest drugi plik, który go uruchomi. Efekt:

* **Sam AltUI.pak** – nic nie uruchamia panelu – B nic nie robi.
* **AltUI.pak + Blueprint Loader** – loader czyta tabelę AltUI i uruchamia panel. Sam AltUI niczego w grze nie podmienia; loader podmienia klasę menedżera kamery – tak właśnie działa.
* **AltUI.pak + AltUI_Hook_P.pak** – hook podmienia menedżera kamery gry i uruchamia panel.
* **AltUI.pak + oba** – działa i nic nie ginie. Oba podmieniają tę samą klasę gry, więc wygrywa tylko jeden z paków – a niezależnie który, AltUI wystartuje: przez tabelę loadera albo przez hook, który dodatkowo uruchamia sam loader, by mody dla niego działały dalej.
* **Hook albo loader bez AltUI.pak** – nic – brakuje samego moda.

## Czego nie potrafi

Trzy ograniczenia, o których warto wiedzieć:

* **Makijaż jest tonowany, nie przebarwiany.** Kolor mnoży się przez istniejący rysunek: jasny lub neutralny przyjmuje go niemal w pełni, ciemny można tylko przyciemnić albo przesunąć. Biel oznacza „bez zmian”, a nie biały makijaż.
* **Kolory widać w grze, nie w menu głównym.** AltUI nakłada je na Jodi, gdy jesteś na poziomie – tam działa. W menu głównym widać ją w fabrycznych kolorach gry.
* **Przekonwertowane ciało może przebijać przez obcisłe ubrania.** Gra spłaszcza takie miejsca morph targetami osadzonymi w siatce ciała; jeśli siatka żadnych nie ma, nie ma czym spłaszczać. To kwestia ciała, nie konwersji: konwerter zachowuje to, co ma oryginał, a jeśli oryginał nie ma żadnych, nikt ich nie doda.

## Kod źródłowy i zgłaszanie błędów

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – kod źródłowy (MIT), wszystkie pliki do pobrania, zgłoszenia błędów.
