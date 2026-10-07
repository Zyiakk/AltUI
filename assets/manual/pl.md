## O AltUI {#about}

AltUI zastępuje szafę i ekran wyglądu w The Killing Antidote jednym panelem. Otwiera się w dowolnym miejscu poziomu klawiszem B – bez chodzenia do szafy czy lustra.

Każdy element z gry i ze wszystkich zainstalowanych modów stoi na jednej liście na slot, z wyszukiwaniem, filtrami, ulubionymi i ukrywaniem. Fryzura, makijaż, ciało, twarz, pozy, broń oraz zapisane stroje i stylizacje są w tym samym panelu, a także ragdolle – kopie Jodi, zombie i ludzie do ustawiania i pozowania – oraz prędkość chodu i biegu Jodi.

Panel otwiera się na karcie, na której został zamknięty. Nieużywane karty można wyłączyć w Opcje › Karty.

## Instalacja i aktualizacje {#install}

AltUI.pak zawiera cały mod i trafia do TheKillingAntidote/Mods/. Uruchamia go jeszcze jeden plik:

- Blueprint Loader (osobny mały mod, TKA_BlueprintLoader.pak w TheKillingAntidote/Content/Paks/~mods/), albo
- własny hook AltUI, AltUI_Hook_P.pak w tym samym folderze ~mods/.

Wystarczy jeden z nich; oba razem też działają. Z samym AltUI.pak klawisz B nic nie robi.

Aktualizacja zwykle wymienia tylko AltUI.pak. Lista zmian mówi, kiedy zmienia się też hook; stary hook nie może zostać w ~mods/.

Aby usunąć AltUI, skasuj skopiowane pliki:

- TheKillingAntidote/Mods/AltUI.pak
- TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak – jeśli używasz hooka
- TheKillingAntidote/Content/Paks/~mods/TKA_BlueprintLoader.pak – tylko jeśli żaden inny mod go nie potrzebuje

AltUI trzyma własne dane w folderze zapisów gry, w Windows %LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames. Aby usunąć wszystko, skasuj tam również:

- AltUI.sav – ustawienia i wybory
- AltUI_Looks.sav – zapisane stylizacje
- AltUI_Faces.sav – zapisane twarze
- AltUI_Names.sav – własne nazwy
- AltUI_Ragdolls.sav – sceny i pozy ragdolli
- folder AltUI – zdjęcia stylizacji, twarzy i presetów wyglądu
- folder WeaponIcons – obrazy broni

Ubrania, stroje, makijaż i fryzura są zapisywane w zapisach samej gry i zostają.

## Sterowanie {#controls}

- B otwiera i zamyka panel (inny klawisz w Opcje › Sterowanie); Esc go zamyka.
- Lewy przycisk wybiera, zakłada lub stosuje; prawy otwiera menu kontekstowe kafelka, wiersza lub karty.
- Kółko myszy przewija; prędkość ustawia się w Opcje › Sterowanie.
- Gdy panel jest otwarty, Jodi nie może chodzić. Przeciąganie po tle obraca kamerę; kliknięcie na Jodi i przeciąganie obraca ją – po zamknięciu panelu wraca do poprzedniej pozycji.
- + i − zmieniają odległość kamery co 5 %, kółko myszy nad Jodi co 4 %.
- Trzy okrągłe przyciski nad + i − otwierają swobodną kamerę (mysz obraca, W A S D i Q E przesuwają, Shift szybciej, kółko ustawia prędkość, Esc wraca), tryb fotograficzny gry (Esc wraca) i tryb ragdolli (zob. „Tryb ragdolli”).
- Cofnij i Ponów (pięć kroków) są na pasku stanu na dole.
- Przytrzymaj 4, aby otworzyć szybkie menu (zob. „Szybkie menu”).

## Ubrania {#clothes}

Po lewej sloty, po prawej elementy wybranego slotu.

- Kliknięcie elementu zakłada go, kliknięcie założonego zdejmuje.
- Chipy nad listą filtrują według moda lub grupy; „...” zwija rzędy chipów. Pole wyszukiwania zawęża chipy, a wyszukiwanie nad listą znajduje elementy po nazwie, modzie lub grupie.
- Filtry: tylko posiadane, tylko ulubione, tylko vanilla, tylko założone.
- Prawy przycisk na elemencie: ulubione, ukryj, kolor z palety gry, przywróć kolor, do plecaka, zmień nazwę, tylko ta grupa, pokaż zawartość moda, pokaż w zakładce.
- Podpowiedź pokazuje, z którego moda pochodzi element.

## Stroje {#outfits}

Zapisane stroje gry – te same, których używają szafa i lustro.

- Kafelek „+” zapisuje to, co Jodi ma na sobie, jako nowy strój.
- Kliknięcie stroju zakłada go.
- Prawy przycisk: załóż, pokaż zawartość, dodaj do szybkiego menu lub usuń z niego, zmień nazwę, przesuń w lewo / w prawo / na początek / na koniec, usuń.
- Strój bez własnej nazwy jest pokazywany jako „Strój” z jego miejscem na liście.
- Rozmiar kafelków i liczbę elementów na kafelku ustawia się w Opcje › Kafelki.

## Stylizacje {#looks}

Stylizacja to wszystko naraz: ubrania z kolorami, fryzura i kolor włosów, makijaż, oczy, skóra, suwaki ciała, mod ciała i twarz.

- Kafelek „+” zapisuje aktualną stylizację ze zdjęciem całej postaci – z przodu albo tak, jak ją teraz widzisz.
- Kliknięcie stylizacji ją stosuje.
- Prawy przycisk: pokaż zawartość, zmień nazwę, aktualizuj (zdjęcie z przodu lub jak widać), przesuń, usuń, dodaj do szybkiego menu lub usuń z niego.

## Plecak {#bag}

To, co Jodi ma na sobie i co niesie.

- Kliknięcie założonego elementu zdejmuje go, kliknięcie niesionego zakłada go.
- Prawy przycisk: załóż lub zdejmij, napraw (potrzebny zestaw do szycia), usuń z plecaka, do szafy.
- „Uporządkuj plecak” usuwa elementy, które nie są założone i są też w szafie.
- „Wszystko do plecaka” zdejmuje każdy założony element i wkłada go do plecaka.

## Fryzura {#hair}

Wszystkie fryzury z gry i z modów.

- Kliknięcie fryzury ją zakłada.
- „Kolor włosów...” otwiera paletę gry; „Naturalne kolory włosów” daje 14 gotowych kolorów.
- Prawy przycisk: przywróć kolor włosów, zmień nazwę, pokaż zawartość moda.

## Pozy {#poses}

Każda animacja akcji, którą znają gra i twoje mody z pozami – lista za aplikacją „rytm” w telefonie.

- Kliknięcie pozy ją odtwarza; ponowne kliknięcie albo „Zakończ pozę” ją zatrzymuje.
- Pozy są posortowane według postawy (stojąca, siedząca, leżąca) i rozdziału; chipy filtrują według moda, wyszukiwanie znajduje tytuły.
- Prawy przycisk: ulubione, ukryj, oznacz jako stojąca / siedząca / leżąca / w ruchu, zmień nazwę, dodaj do szybkiego menu.
- „Zmierz wszystkie” odtwarza raz każdą pozę, która nie ma jeszcze postawy, i ją sortuje.

## Broń {#weapons}

Po lewej jeden wpis na broń, także broń do walki wręcz. Dla każdej broni model, skórkę i dźwięk strzału wybiera się osobno.

- U góry modele – model gry i każdy zainstalowany mod modelu.
- Na dole skórki – malowania broni z gry (bez puszki ze sprayem) i każdy zainstalowany mod skórki.
- Dźwięk: własny dźwięk strzału broni („Oryginalny”) i każdy zainstalowany dla niej dźwięk strzału. Kliknięcie wybiera dźwięk i go odtwarza; każda inna broń zachowuje swój. Zamontowany tłumik z własnym dźwiękiem nadal ma pierwszeństwo.
- Chipy powyżej filtrują wszystkie trzy sekcje naraz. Prawy przycisk na kafelku: ulubione, ukryj, tylko ten mod.
- Wybór jest zapamiętywany i nakładany ponownie, gdy broń zostanie podniesiona lub wyjęta ze skrzyni.
- Malowanie nałożone w grze puszką ze sprayem zostaje: staje się wybraną skórką.
- Prawy przycisk na modelu z moda: wymuś na nim skórki, pomiń magazynek, celownik, tłumik lub chwyt, pokaż własny obraz moda.
- Mody broni i dźwięków strzału trzeba najpierw przekonwertować za pomocą weaponpak.pyz; zob. poradnik WEAPON_MODS na stronie moda.

## Wygląd {#look}

Skóra, każdy rodzaj makijażu, oczy i presety wyglądu z gry.

- Kliknięcie wpisu go nakłada. Prawy przycisk na makijażu: tonowanie paletą gry, przywróć tonowanie.
- Oczy: kolor tęczówki i rzęs w menu kontekstowym.
- Presety: kafelek „+” zapisuje aktualny wygląd ze zdjęciem. Prawy przycisk: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń, szybkie menu.

## Kształt ciała {#body}

- Suwaki biustu i talii z gry.
- Chipy przełączają między ciałem z gry a każdym przekonwertowanym modem ciała.
- Przekonwertowane ciała mają dodatkowo suwaki kości: skala, biust, talia, pośladki i biodra, uda, łydki, ręce, dłonie, stopy. Są zapisywane dla każdego ciała; „Zresetuj kształt” je przywraca.
- Mody zastępujące ciało trzeba najpierw przekonwertować za pomocą bodypak.pyz; zob. poradnik BODY_MODS na stronie moda.

## Twarz {#face}

Mimika Jodi.

- Suwaki dla min z gry (zrelaksowana, skupiona, uśmiech, ból, przestrach, zmęczona, cierpienie), spojrzenia i kształtów ust.
- Zaznaczony wpis zachowuje swoją wartość, także w pozach; niezaznaczony ustala animacja gry. „Ustal wszystkie” i „Wszystko grze” przełączają wszystkie naraz.
- Miny są mieszane (razem najwyżej 100 %) albo sumowane.
- Kafelek „+” zapisuje aktualną twarz ze zdjęciem. Prawy przycisk: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń.

## Mody {#mods}

Ustawienia innych modów, które rejestrują się w AltUI: po lewej ich wpisy, po prawej przełączniki, suwaki, liczby, wybory, kolory, pola tekstowe, klawisze i przyciski wybranego.

Ta karta pojawia się tylko wtedy, gdy taki mod jest zainstalowany.

## Opcje {#options}

Po lewej kategorie.

- Ogólne: język, ile ekranu zostaje wolne dla Jodi, czy można zdjąć bieliznę, jak wyglądają elementy, których nie masz, przełącznik Kodeksu dla encyklopedii.
- Kafelki: rozmiar kafelków, osobne rozmiary dla kafelków strojów, stylizacji i ragdolli, elementy na kafelku stroju, bez limitu dla długich list, dane w podpowiedziach.
- Grupy: łączenie grup lub modów o tej samej nazwie, długość nazw grup, wysokość obszaru chipów, wyszukiwanie chipów.
- Kamera: pole widzenia, odległość, wysokość, kamera podąża za wybranym slotem.
- Sterowanie: klawisz panelu, prędkość przewijania, wysokość kamery prawym przyciskiem myszy.
- Ruch: własna prędkość chodu i biegu Jodi (od 50 do 200 %, „Przywróć 100 %”); kucanie i skakanie pozostają bez zmian.
- Szybkie menu: klawisz, przezroczystość, co jest w kole.
- Kolory: każdy kolor panelu, przezroczystość, schematy kolorów zapisane pod nazwą.
- Konflikty slotów: rozdzielenie par slotów gry (na przykład biustonosz i koszula), aby można było nosić oba elementy.
- Karty: tekst, ikony lub oba na pasku kart; wyłączanie kart.

## Zarządzanie {#manage}

Własne nazwy wyświetlane dla modów, grup, ubrań, fryzur, skór, makijażu, póz i presetów wyglądu.

- Nazwy są używane w całym panelu i znajdowane przez wyszukiwanie; oryginalny identyfikator nadal można wyszukać i widać go w podpowiedzi.
- Chipy i wyszukiwanie filtrują listę; „tylko mody” ukrywa wpisy gry; ↺ przywraca nazwę domyślną.
- Za pomocą altui_names.pyz nazwy można wyeksportować do pliku tekstowego i zaimportować z powrotem.

## Ragdolle {#ragdolls}

Figury z fizyką do ustawiania i pozowania na poziomie: kopie Jodi, zombie i ludzie.

- „+ Utwórz kopię Jodi” stawia kopię przed nią, stojącą i zamrożoną w jej obecnej pozie, ze wszystkim, co ma na sobie. Stylizacja staje się figurą przez „Utwórz jako ragdoll” w jej menu kontekstowym.
- „Zombie i ludzie”: jeden kafelek z obrazem na rodzaj zombie, do tego pielęgniarka i ocalała. Kliknięcie tworzy figurę; linki pod kafelkiem tworzą jej warianty.
- Każda figura ma swój wiersz: aktywna (fizyka, upada i można nią rzucać) lub zamrożona (trzyma pozę), „stawy ›”, zablokuj wszystkie, zwolnij wszystkie, usuń. „Usuń wszystkie” usuwa każdą figurę.
- „stawy ›” rozwija 17 stawów figury, każdy zablokowany, wolny lub ruchomy. Zablokowany staw pozostaje sztywny, dopóki figura jest aktywna.
- Pozy (w rozwiniętym wierszu): nazwa i „zapisz pozę” zapamiętują ułożenie części ciała. Pozę można wczytać na każdą figurę tego samego rodzaju, na każdym poziomie – kliknięcie wczytuje, prawy przycisk: wczytaj / usuń. Figura przy tym zamarza i staje na podłodze.
- Sceny: „Zapisz scenę jako” zapamiętuje każdą figurę poziomu z wyglądem, miejscem, pozą i stawami; ta sama nazwa na tym samym poziomie nadpisuje scenę. Widać tylko sceny bieżącego poziomu. Kliknięcie wczytuje scenę i zastępuje obecne figury; prawy przycisk: wczytaj / usuń.

Z myszą na figurze, obok panelu i w trybie ragdolli:

- Przeciąganie lewym przyciskiem zamrożonej figury przesuwa ją po podłodze; kółko myszy podnosi ją lub opuszcza podczas przeciągania.
- Przeciąganie lewym przyciskiem aktywnej figury chwyta część ciała pod myszą; puść, a figura upadnie.
- Przeciąganie prawym przyciskiem obraca figurę wokół bioder.
- Shift + lewy przycisk blokuje lub zwalnia kliknięty staw.
- Shift + prawy przycisk na zamrożonej figurze czyni staw ruchomym. Przeciąganie wtedy lewym przyciskiem części ciała poniżej ruchomego stawu porusza tylko tę część; zostaje tam, gdzie ją puścisz – tak pozuje się figurę.

Bez panelu figury aktywuje lub zamraża szybkie menu: „Ragdoll: aktywuj / zamroź tę na środku” bierze figurę na środku ekranu, „Ragdolle: aktywne / zamrożone” przełącza wszystkie.

## Tryb ragdolli {#ragmode}

Przesuwanie i pozowanie figur bez panelu, z kamerą poruszającą się swobodnie po pomieszczeniu. Uruchamia go trzeci okrągły przycisk nad + i − albo szybkie menu.

- Kursor myszy pozostaje widoczny; na figurze wszystko działa jak obok panelu (zob. „Ragdolle”).
- W A S D i Q E przesuwają kamerę, Shift szybciej; Shift + kółko ustawia prędkość.
- Przeciąganie w pustym miejscu obraca kamerę.
- Esc lub B kończy tryb.

## Kodeks {#kodex}

- Encyklopedia: wpisy z archiwum na komputerze w biurze Jodi, z obrazem i tekstem. Pokazywane są tylko te odblokowane w grze – albo wszystkie po włączeniu przełącznika w Opcje › Ogólne.
- Hasła: zamki szyfrowe bieżącego poziomu, najbliższy pierwszy, z odległością i informacją, czy są zamknięte. Każdy kod pozostaje ukryty, dopóki go nie klikniesz.
- Podręcznik AltUI: ten tekst.

## Szybkie menu {#quick}

Przytrzymaj 4 (inny klawisz w Opcje › Szybkie menu), a wokół myszy otworzy się koło. Puść nad wpisem, aby go wykonać; puść na środku, aby nic nie robić.

- Wpisy: stroje, stylizacje, twarze, presety wyglądu, pozy, karty, ustawienia innych modów i akcje: swobodna kamera, tryb fotograficzny, tryb ragdolli, kopia Jodi jako ragdoll, przełączanie wszystkich ragdolli między aktywnymi a zamrożonymi, aktywuj / zamroź tę na środku, usuń wszystkie ragdolle, własna prędkość wł. / wył.
- Dodaje się je w Opcje › Szybkie menu albo prawym przyciskiem na kafelku, karcie lub wpisie moda („Dodaj do szybkiego menu”).
- Kolejność w kole to kolejność listy w Opcje › Szybkie menu.

## Dla autorów modów {#modding}

- Mody z ubraniami nie potrzebują niczego szczególnego: AltUI czyta tabele gry i przypisuje każdy element do jego slotu.
- Mody zastępujące ciało lub broń można przekonwertować za pomocą bodypak.pyz i weaponpak.pyz, aby kilka mogło być zainstalowanych obok siebie; można je też zbudować dla AltUI bezpośrednio w Unreal Editorze.
- Mody mogą pokazywać swoje ustawienia w karcie Mody przez dwie tabele danych i interfejs; jak to zrobić, opisuje MOD_UI.md w repozytorium kodu źródłowego.
