# AltUI – panel szafy i wyglądu

Polska wersja opisu [wpisu w Warsztacie Steam](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). Wiążąca jest [wersja angielska](description.en.md); sama strona Warsztatu pokazuje wersję skróconą.

Szafa w grze daje każdemu autorowi moda własną zakładkę. Przy kilku modach z ubraniami ten sam rodzaj rzeczy jest rozrzucony po kilkunastu zakładkach i nie da się niczego wyszukać. AltUI porządkuje każdą rzecz z gry i ze wszystkich zainstalowanych modów w **jedną listę na slot** (góra, spódnice, obuwie, …), z wyszukiwaniem, filtrami, ulubionymi i ukrywaniem – a fryzurę, makijaż, ciało i stroje wciąga do tego samego panelu. Otwiera się wszędzie w poziomie klawiszem **B**; koniec z chodzeniem do szafy i do lustra.

Dostępny też na [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (oba pliki w jednym archiwum). Ten sam mod – wybierz jedno źródło, nie oba naraz.

> ⚠️ **Uwaga:** Zrobione pod wersję gry 0.6.x. Aktualizacja gry, która zmieni tabele ubrań / makijażu albo menedżera kamery, może zepsuć moda.

## ⚠ Instalacja – przeczytaj najpierw

Subskrypcja instaluje samego moda, **AltUI.pak**. Uruchomić go musi drugi plik, a tego Warsztat nie może za ciebie umieścić, bo należy on do folderu gry, którego Warsztat nie rusza. Bez niego **po naciśnięciu B nic się nie dzieje**. Są na to dwa sposoby – wystarczy jeden, oba naraz też działają.

**1. Z Blueprint Loaderem (AltUI niczego w grze nie podmienia)**

1. Zasubskrybuj ten wpis (to instaluje **AltUI.pak**).
2. Pobierz **TKA_BlueprintLoader.pak**: https://www.nexusmods.com/thekillingantidote/mods/994
3. Skopiuj do
   `Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Content\Paks\~mods\`
   Utwórz folder **~mods**, jeśli go nie ma (nazwa zaczyna się tyldą). Nazwa folderu gry występuje w ścieżce dwa razy – tak ma być.
4. Uruchom grę, w poziomie naciśnij B.

AltUI niesie tabelę, którą loader czyta, i uruchamia z niej panel. Ten sam loader uruchamia każdy inny mod z taką tabelą – dlatego to jest droga dla kogoś, kto używa kilku takich modów.

**Przy przejściu ze starszej wersji AltUI: jeśli w ~mods nadal leży AltUI_Hook_P.pak, usuń go. Hook przejmuje klasę menedżera kamery, a ten sprzed 1.5.0 nie uruchamia loadera – panel wprawdzie się otworzy, ale widok nie odsunie się na bok, a mody zrobione pod loader nie wystartują.**

**2. Z pakiem hooka (jeden plik, z wydania AltUI)**

1. Zasubskrybuj ten wpis.
2. Pobierz **AltUI_Hook_P.pak**: https://github.com/Zyiakk/AltUI/releases/latest/download/AltUI_Hook_P.pak
3. Skopiuj do tego samego folderu *~mods* co wyżej.
4. Uruchom grę, w poziomie naciśnij B.

Hook podmienia *TKA_PlayerCameraManager* i stamtąd uruchamia panel. Każdy mod, który podmienia ten sam blueprint, jest z nim w konflikcie – Blueprint Loader jest właśnie takim modem i akurat ta para jest wyjątkiem: przy obu zainstalowanych hook wygrywa klasę i sam uruchamia loadera, więc mody wymagające loadera działają dalej.

**„Zasubskrybowałem, ale B nic nie robi”** → nic nie uruchomiło panelu: albo brakuje drugiego pliku, albo leży on w *Mods* lub w folderze Warsztatu zamiast w *Content\Paks\~mods*.

## Co potrafi

* **Ubrania** – każda rzecz z gry i z twoich modów, jedna lista na slot, z wyszukiwaniem, filtrami, ulubionymi i ukrywaniem.
* **Zestawy · Looki** – gotowe zestawy gry z nazwami oraz pełne looki (ubrania z kolorami, fryzura, makijaż, oczy, skóra, ciało, twarz) ze zdjęciem z gry.
* **Plecak · Fryzury · Wygląd** – co Jodi nosi i ma przy sobie; fryzury i kolory włosów; skóra, makijaż i oczy, każde do podbarwienia.
* **Sylwetka** – suwaki biustu i talii, przełącznik przekonwertowanych modów ciała, suwaki kości dla każdego ciała.
* **Twarz** – mimika, spojrzenie i usta Jodi jako suwaki; twarz trzyma się także w pozach i podczas tańca; zapisane twarze ze zdjęciem, ich wartości w „Pokaż zawartość”.
* **Bronie** – model i skin na broń, obok siebie ze wszystkich modów do broni, z wyrenderowanym obrazkiem na kafelku.
* **Pozy** – każda animacja akcji z gry i z modów, posortowana na stojące, siedzące i leżące.
* **Mods** – ustawienia innych modów, które się tam rejestrują: przełączniki, suwaki, liczby, wybory, kolory, pola tekstowe, wiersze informacyjne, klawisze i przyciski. Widoczna tylko, gdy taki mod jest zainstalowany.
* **Szybkie menu** – przytrzymaj **4** (klawisz można zmienić), a otworzy się koło z tym, czego używasz najczęściej: wolna kamera, tryb zdjęć, zapisany strój, stylizacja, twarz lub preset, ulubiona poza, karta oraz akcje innych modów. Do 32 pozycji, wybieranych i układanych w opcjach; puść klawisz nad pozycją, aby ją wykonać.
* **Opcje** – podzielone na kategorie wybierane z listy po lewej: klawisz panelu, język, kolory (schematy można zapisać pod nazwą), pasek kart z ikonami, tekstem lub jednym i drugim oraz wielkość kafelków, osobno dla zestawów i looków. Niepotrzebne karty można wyłączyć.
* **Zarządzanie** – własne nazwy modów, grup i przedmiotów. Jak w Ubraniach podzakładki filtrują listę według moda lub grupy, a pole wyszukiwania zawęża podzakładki.
* Cofnij / ponów (5 kroków), dymki z nazwą moda, z którego pochodzi dana rzecz.

Języki: angielski, niemiecki, chiński, rosyjski, hiszpański, polski (wykrywane automatycznie, zmienialne w Opcjach).

## Sterowanie

* **B** – otwiera / zamyka (zmienialne w opcjach). **Esc** zamyka.
* **4** – przytrzymaj, aby otworzyć szybkie menu (zmienialne w opcjach); puść nad pozycją, aby ją wykonać, a puszczenie na środku nic nie robi.
* Lewy przycisk – wybierz / załóż / zastosuj. Prawy przycisk – menu kontekstowe. Kółko myszy – przewijanie.

## Mody ciała

Paki podmieniające ciało nadpisują wszystkie ten sam plik gry, więc aktywny może być tylko jeden. Mały konwerter robi z takiego paka zwykły mod-pak, który trzyma mesh pod własną ścieżką; dowolnie wiele przekonwertowanych ciał może być zainstalowanych obok siebie i pojawia się jako chipy w zakładce Kształt ciała.

Konwerter (Python 3.8+, bez dodatkowych pakietów): https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

Instrukcja krok po kroku z przykładem dla Windowsa i dla Linuksa (po angielsku): [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Aktualizacje moda a drugi plik

To, co uruchamia panel, jest celowo oddzielone od samego panelu: wszystko, co mod potrafi, siedzi w paku z Warsztatu. Gdy więc ten wpis zaktualizuje się przez Steam, **plik w *~mods* zwykle działa dalej – nie musisz go ruszać**.

Sam Blueprint Loader niczego nie potrzebuje: jest osobnym modem i aktualizuje się na własnej stronie. AltUI_Hook_P.pak sprzed 1.5.0 nie może zostać w ~mods (zob. uwagę w sekcji Instalacja): usuń go albo zastąp aktualnym.

**Hook bez Blueprint Loadera:** Od wersji 1.8.0 AltUI nakłada twój wygląd na Jodi także w menu głównym i na ekranie ładowania. Z samym hookiem potrzebny jest do tego aktualny AltUI_Hook_P.pak – zastąp nim starszy; na poziomach starszy dalej działa. Z Blueprint Loaderem robi to sam AltUI.pak.

Żadne zasoby gry nie są dołączone; wszystko w paku jest generowane.

## Co daje każda kombinacja

* **Sam AltUI.pak** – nic nie uruchamia panelu – B nic nie robi.
* **AltUI.pak + Blueprint Loader** – loader czyta tabelę AltUI i uruchamia panel. Sam AltUI niczego w grze nie podmienia; loader podmienia klasę menedżera kamery – tak właśnie działa.
* **AltUI.pak + AltUI_Hook_P.pak** – hook podmienia menedżera kamery gry i uruchamia panel.
* **AltUI.pak + oba** – działa i nic nie ginie. Oba podmieniają tę samą klasę gry, więc wygrywa tylko jeden z paków – a niezależnie który, AltUI wystartuje: przez tabelę loadera albo przez hook, który dodatkowo uruchamia sam loader, by mody dla niego działały dalej.
* **Hook albo loader bez AltUI.pak** – nic – brakuje samego moda.

## Czego nie potrafi

Dwa ograniczenia, o których warto wiedzieć:

* **Makijaż jest tonowany, nie przebarwiany.** Kolor mnoży się przez istniejący rysunek: jasny lub neutralny przyjmuje go niemal w pełni, ciemny można tylko przyciemnić albo przesunąć. Biel oznacza „bez zmian”, a nie biały makijaż.
* **Przekonwertowane ciało może przebijać przez obcisłe ubrania.** Gra spłaszcza takie miejsca morph targetami osadzonymi w siatce ciała; jeśli siatka żadnych nie ma, nie ma czym spłaszczać. To kwestia ciała, nie konwersji: konwerter zachowuje to, co ma oryginał, a jeśli oryginał nie ma żadnych, nikt ich nie doda.

## Kod źródłowy i zgłaszanie błędów

https://github.com/Zyiakk/AltUI – kod źródłowy (MIT), wszystkie pliki do pobrania, zgłoszenia błędów.
