## O AltUI {#about}

AltUI to alternatywa dla szafy i ekranu wyglądu w The Killing Antidote: jeden panel do wszystkiego, a ekrany gry nadal działają. Otwiera się w dowolnym miejscu poziomu klawiszem B – bez chodzenia do szafy czy lustra.

Każdy element z gry i ze wszystkich zainstalowanych modów stoi na jednej liście na slot, z wyszukiwaniem, filtrami, ulubionymi i ukrywaniem. Fryzura, makijaż, ciało, twarz, pozy, broń oraz zapisane stroje i stylizacje są w tym samym panelu, a także ragdolle – kopie Jodi, zombie i ludzie do ustawiania i pozowania – oraz prędkość chodu i biegu Jodi.

Panel otwiera się na karcie, na której został zamknięty. Nieużywane karty można wyłączyć w Opcje › Karty.

Karta Ekwipunek przenosi przedmioty między plecakiem Jodi a hiperskrzynią, a stylizacje stają się towarzyszami i NPC, którzy chodzą i walczą razem z nią.

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
- AltUI_Followers.sav – towarzysze i NPC
- AltUI_Drawers.sav – szuflady z ubraniami
- folder AltUI – zdjęcia stylizacji, twarzy i presetów wyglądu
- folder WeaponIcons – obrazy broni

Ubrania, stroje, makijaż i fryzura są zapisywane w zapisach samej gry i zostają.

Po aktualizacji gry albo z modem, który zastępuje tabele gry, AltUI może trafić na grę, dla której nie został zrobiony. Wtedy pokazuje ostrzeżenie, zanim cokolwiek zrobi: „Kontynuuj mimo to (na własne ryzyko)” zostaje zapamiętane dla tej wersji gry, „Na razie wyłącz AltUI” pyta ponownie w następnym poziomie.

## Sterowanie {#controls}

- B otwiera i zamyka panel (inny klawisz w Opcje › Sterowanie); Esc go zamyka.
- Lewy przycisk wybiera, zakłada lub stosuje; prawy otwiera menu kontekstowe kafelka, wiersza lub karty.
- Kółko myszy przewija; prędkość ustawia się w Opcje › Sterowanie.
- Gdy panel jest otwarty, Jodi nie może chodzić. Przeciąganie po tle obraca kamerę; kliknięcie na Jodi i przeciąganie obraca ją – po zamknięciu panelu wraca do poprzedniej pozycji.
- + i − zmieniają odległość kamery co 5 %, kółko myszy nad Jodi co 4 %.
- Okrągłe przyciski nad + i − otwierają swobodną kamerę (mysz obraca, W A S D i Q E przesuwają, Shift szybciej, kółko ustawia prędkość, Esc wraca), tryb fotograficzny gry (Esc wraca) i tryb ragdolli (zob. „Tryb ragdolli”).
- Najwyższy okrągły przycisk (żarówka) to światło kamery: rozjaśnia to, co widzi kamera – obok panelu, w swobodnej kamerze i w trybie zdjęć. Kliknięcie otwiera małe menu: wł. / wył., kolor światła (paleta) i suwak jasności. Tylko rozjaśnia (bez odblasków, bez snopu we mgle), w czasie gry jest wyłączone i wraca takie, jak je zostawiono, gdy panel się otworzy.
- Cofnij i Ponów (pięć kroków) są na pasku stanu na dole.
- Przytrzymaj 4, aby otworzyć szybkie menu (zob. „Szybkie menu”).
- W menu głównym B otwiera małe menu: trzy sceny menu i scenę ładowania, następną kamerę oraz ukrywanie menu i tekstów gry (Esc je przywraca).

## Ubrania {#clothes}

Po lewej sloty, po prawej elementy wybranego slotu.

- Kliknięcie elementu zakłada go, kliknięcie założonego zdejmuje.
- Chipy nad listą filtrują według moda lub grupy; „...” zwija rzędy chipów. Pole wyszukiwania zawęża chipy, a wyszukiwanie nad listą znajduje elementy po nazwie, modzie lub grupie.
- Filtry: tylko posiadane, tylko ulubione, tylko vanilla, tylko założone.
- Prawy przycisk na elemencie: ulubione, ukryj, kolor z palety gry, przywróć kolor, do plecaka, zmień nazwę, tylko ta grupa, pokaż zawartość moda, pokaż w zakładce.
- Szuflady: własne kolekcje ubrań, na pasku nad listą. „Domyślny” pokazuje wszystko; „+” tworzy nową szufladę („Szuflada 1”, „Szuflada 2” …). Szuflada pokazuje tę samą stronę – sloty, przyciski, wyszukiwanie, filtry, ulubione – tylko z jej rzeczami, a sloty liczą tylko je. Prawy przycisk na rzeczy › „Szuflada ›” otwiera obok menu listę szuflad: znacznik oznacza, że rzecz w niej jest; kliknięcie wkłada ją lub wyjmuje, „+ Nowa szuflada” tworzy szufladę z tą rzeczą. Rzecz może być w dowolnej liczbie szuflad; w szufladzie menu ma też „Usuń z tej szuflady”. Prawy przycisk na szufladzie: zmień nazwę (Enter zatwierdza, Esc anuluje), w lewo / w prawo, usuń (najpierw pyta – rzeczy zostają). Pokazana szuflada zostaje po ponownym uruchomieniu.
- Podpowiedź pokazuje, z którego moda pochodzi element.
- Uszkodzenie (w menu kontekstowym): od 0 do 100 %, od razu na noszonym elemencie; przy każdym innym zostaje zapamiętane, aż element zostanie założony. Noszone elementy bez tekstur uszkodzeń nie mają suwaka.
- Pod paletą kolorów gry pole pokazuje kolor jako #RRGGBB; wpisz kod i naciśnij Enter, aby go ustawić. „Zapamiętaj” zachowuje kolor w AltUI, „Użyj” nakłada go na inny element lub slot.
- Wyszukiwanie znajduje mod także po nazwie jego paka, tutaj i w każdej innej karcie.

## Stroje {#outfits}

Zapisane stroje gry – te same, których używają szafa i lustro.

- Kafelek „+” zapisuje to, co Jodi ma na sobie, jako nowy strój.
- Kliknięcie stroju zakłada go.
- Prawy przycisk: załóż, pokaż zawartość, dodaj do szybkiego menu lub usuń z niego, zmień nazwę, przesuń w lewo / w prawo / na początek / na koniec, usuń.
- Strój bez własnej nazwy jest pokazywany jako „Strój” z jego miejscem na liście.
- Rozmiar kafelków i liczbę elementów na kafelku ustawia się w Opcje › Kafelki.
- Strój zapisany tutaj zachowuje każdy kanał koloru swoich elementów, tak jak pokolorował je AltUI; sama gra pamięta jeden kolor na element. Strój zapisany przy lustrze ma tylko ten jeden.

## Stylizacje {#looks}

Stylizacja to wszystko naraz: ubrania z kolorami, fryzura i kolor włosów, makijaż, oczy, skóra, mutacja, suwaki ciała, mod ciała i twarz.

- Kafelek „+” zapisuje aktualną stylizację ze zdjęciem całej postaci – z przodu albo tak, jak ją teraz widzisz.
- Kliknięcie stylizacji ją stosuje.
- Prawy przycisk: pokaż zawartość, zmień nazwę, aktualizuj (zdjęcie z przodu lub jak widać), przesuń, usuń, dodaj do szybkiego menu lub usuń z niego.
- Prawy przycisk także: „Utwórz jako ragdoll”, „Utwórz jako towarzysza”, „Utwórz jako NPC” (zobacz „Ragdolle” i „Towarzysze”).
- Prawy przycisk „Oczyszczona kopia (bez brakujących części)” – widoczne tylko, gdy wygląd zawiera części moda, którego już nie ma, albo wiersze makijażu / oczu, których nie zna żadna tabela: nowy wygląd tuż za nim bez tych wpisów, z tym samym zdjęciem. Oryginał zostaje bez zmian; ponowne zapisanie nigdy ich samo nie usuwa.

## Plecak {#bag}

To, co Jodi ma na sobie i co niesie.

- Kliknięcie założonego elementu zdejmuje go, kliknięcie niesionego zakłada go.
- Prawy przycisk: załóż lub zdejmij, napraw (potrzebny zestaw do szycia), usuń z plecaka, do szafy.
- „Uporządkuj plecak” usuwa elementy, które nie są założone i są też w szafie.
- „Wszystko do plecaka” zdejmuje każdy założony element i wkłada go do plecaka.
- Menu kontekstowe ma też suwak uszkodzenia (zobacz „Ubrania”).

## Ekwipunek {#inventory}

Przedmioty Jodi i hiperskrzynia, jedna lista pod drugą.

- Chipy filtrują według grup gry (broń, amunicja, akcesoria do broni, narzędzia…). Waga pokazuje, ile Jodi niesie, ile może unieść i jak bardzo jest przeciążona.
- Kliknięcie wkłada jeden przedmiot do skrzyni albo wyjmuje jeden. Prawy przycisk: połowa albo wszystko, użyj, obejrzyj, wyrzuć, szybki wybór 1 lub 2, rozładuj, „Akcesoria…” (otwiera broń w karcie Broń).
- Menu kontekstowe stosu kończy się wierszem „Ilość”: suwak i pole liczbowe, a pod nimi po jednym wpisie na cel z tą liczbą („Włóż 5 do skrzyni”, „Weź 5”). Enter w polu wykonuje pierwszy wpis. W katalogu liczba oznacza sztuki, a pole przyjmuje więcej, niż sięga suwak. Broń palna i pojedyncze przedmioty nie mają ilości.
- „Wyrzuć wszystko” kładzie na ziemi jeden obiekt na paczkę. Od 100 obiektów najpierw pyta okno: „Anuluj”, „Zamiast tego zniszcz” (przedmioty znikają, nic nie spada) albo „Wyrzuć mimo to” – tyle obiektów z fizyką naraz może spowodować awarię gry. Esc anuluje.
- Wszystko idzie przez funkcje samej gry, więc jej zasady zostają – razem z przeciążeniem.
- „...” nad listą zwija ją, ↑↓ daje jej całą wysokość (jeszcze raz: powrót).
- Na mapach, na których gra nigdy nie zapisuje plecaka (na przykład strzelnica), karta to mówi: to, co chcesz zachować, trzymaj w skrzyni.
- „Wszystkie przedmioty” jest domyślnie wyłączony (Opcje › Ogólne): każdy przedmiot gry jako trzecia lista z własnym wyszukiwaniem. Kliknięcie wkłada jedną paczkę do plecaka; prawy przycisk: pięć albo do skrzyni.
  W „Kolekcji” jest też Niewidzialna ręka z gry: dopóki jest w plecaku, przynosi Jodi przedmioty z okolicy, jeden po drugim, tym szybciej, im więcej rąk (jedna co 2,5 s, od sześciu co 0,1 s). Ile ich ma Jodi, widać w „Kolekcji” plecaka.
- „Automatycznie wyposażaj broń” (Opcje › Ogólne, domyślnie włączone): broń ze skrzyni lub z katalogu trafia do ręki Jodi tak jak w grze; wyłączone – Jodi trzyma to, co trzymała.
- Rozmiar kafelków tej karty ustawia się w Opcje › Kafelki.

## Fryzura {#hair}

Wszystkie fryzury z gry i z modów.

- Kliknięcie fryzury ją zakłada.
- Pole wyszukiwania nad kafelkami znajduje fryzury po wyświetlanej nazwie, identyfikatorze, nazwie moda i pliku pak; × je czyści.
- „Kolor włosów...” otwiera paletę gry; „Naturalne kolory włosów” daje 14 gotowych kolorów.
- Prawy przycisk: dodaj do / usuń z ulubionych, przywróć kolor włosów, zmień nazwę, pokaż zawartość moda.
- Ulubione są na górze, nad wszystkimi fryzurami.
- Prawy przycisk na fryzurze z moda: „Zmień nazwę moda…”.

## Pozy {#poses}

Każda animacja akcji, którą znają gra i twoje mody z pozami – lista za aplikacją „rytm” w telefonie.

- Kliknięcie pozy ją odtwarza; ponowne kliknięcie albo „Zakończ pozę” ją zatrzymuje.
- Pozy są posortowane według postawy (stojąca, siedząca, leżąca) i rozdziału; chipy filtrują według moda, wyszukiwanie znajduje tytuły.
- Prawy przycisk: ulubione, ukryj, oznacz jako stojąca / siedząca / leżąca / w ruchu, zmień nazwę, dodaj do szybkiego menu.
- Prawy przycisk „Użyj jako bezczynność”: poza zaczyna się po 1,5 s bezruchu i kończy, gdy Jodi idzie, wyciąga broń lub kuca; „Już nie jako bezczynność” to wyłącza.
- „Zmierz wszystkie” odtwarza raz każdą pozę, która nie ma jeszcze postawy, i ją sortuje.
- Głośnik w rogu kafelka oznacza pozę z dźwiękiem.
- „Zmierz wszystkie” pokazuje nazwę mierzonej pozy.
- „Powtarzaj pozy: wł.” na pasku stanu uruchamia od nowa pozę, która kończy się sama – dopóki Jodi się nie ruszy, klawisz użycia lub „Zatrzymaj pozę” jej nie zakończy albo nie wybierzesz innej pozy. Wiele modów póz i tak powtarza swoje pozy.

## Broń {#weapons}

Po lewej jeden wpis na broń, także broń do walki wręcz. Dla każdej broni model, skórkę i dźwięk strzału wybiera się osobno.

- U góry modele – model gry i każdy zainstalowany mod modelu.
- Na dole skórki – malowania broni z gry (bez puszki ze sprayem) i każdy zainstalowany mod skórki.
- Jeśli mod modelu ma własne wersje malowań z gry (zrobione dla jego modelu), pojawiają się jako dodatkowe skórki obok tych z gry, dopóki ten model jest wybrany.
- Kafelki modeli pokazują każdy model z wybraną skórką; własne malowanie modelu tylko na tym modelu – na każdym innym broń zostaje taka, jaka jest, i jej kafelek też. Kafelek moda skórki jest przygaszony, gdy skórka nic nie zmienia na wybranym modelu; wiadomo to, gdy broń choć raz była w ręce Jodi z tym modelem. „Zrób zdjęcia ponownie” na pasku stanu robi od nowa zdjęcia wszystkich kafelków broni.
- Dźwięk: własny dźwięk strzału broni („Oryginalny”) i każdy zainstalowany dla niej dźwięk strzału. Kliknięcie wybiera dźwięk i go odtwarza; każda inna broń zachowuje swój. Zamontowany tłumik z własnym dźwiękiem nadal ma pierwszeństwo.
- Chipy powyżej filtrują wszystkie trzy sekcje naraz. Prawy przycisk na kafelku: ulubione, ukryj, tylko ten mod.
- Wybór jest zapamiętywany i nakładany ponownie, gdy broń zostanie podniesiona lub wyjęta ze skrzyni.
- Malowanie nałożone w grze puszką ze sprayem zostaje: staje się wybraną skórką.
- Prawy przycisk na modelu z moda: wymuś na nim skórki, pomiń magazynek, celownik, tłumik lub chwyt, pokaż własny obraz moda.
- Mody broni i dźwięków strzału trzeba najpierw przekonwertować za pomocą weaponpak.pyz; zob. poradnik WEAPON_MODS na stronie moda.
- Akcesoria do broni: jeden wiersz na każdy slot broni (celownik, lufa, chwyt, magazynek), „Brak” na początku. Części pochodzą z plecaka albo ze skrzyni i wtedy trafiają do plecaka. Akcesoria można zakładać tylko na broń, którą Jodi ma przy sobie; broń zachowuje wybrany tu model, skórkę i dźwięk.
- „Pokaż obrazy przedmiotów” na pasku stanu pokazuje na każdym kafelku własny obraz przedmiotu lub moda zamiast renderowanego.
- Prawy przycisk na modelu, skórce lub dźwięku z moda: „Zmień nazwę moda…”.

## Wygląd {#look}

Skóra, każdy rodzaj makijażu, oczy i presety wyglądu z gry.

- Kliknięcie wpisu go nakłada. Prawy przycisk na makijażu: tonowanie paletą gry, przywróć tonowanie.
- Oczy: kolor tęczówki i rzęs w menu kontekstowym.
- Mutacja: zmutowany wygląd Jodi z fabuły w częściach – kolor skóry i poświata jako suwaki (zaznaczone = działa), żyły i oczy jako przełączniki, „Resetuj” wyłącza wszystko. Makijaż pozostaje widoczny na przebarwionej skórze, własny kolor tęczówki barwi zmutowane oko. „Wygląd z fabuły” ustawia wygląd z przerywnika: materiał skóry z fabuły, wszystkie wiersze na maksimum; potem można cofnąć pojedyncze wiersze. Makijaż i blizny nie są z nim widoczne. Gdy fabuła sama zmienia Jodi w mutanta, obowiązuje jej wygląd.
- Presety: kafelek „+” zapisuje aktualny wygląd ze zdjęciem. Prawy przycisk: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń, szybkie menu.

## Kształt ciała {#body}

- Suwaki biustu i talii z gry.
- Chipy przełączają między ciałem z gry a każdym przekonwertowanym modem ciała.
- Przekonwertowane ciała mają dodatkowo suwaki kości: skala, biust, talia, pośladki i biodra, uda, łydki, ręce, dłonie, stopy. Są zapisywane dla każdego ciała; „Zresetuj kształt” je przywraca.
- Piersi oraz pośladki i biodra: kołysanie (0 % = tylko animacja) zmienia fizykę gry i działa z każdym ciałem; biustonosz nadal tłumi jak w grze. Suwak sutków działa tylko, gdy piersi są odsłonięte. Kąt i szerokość bioder są tylko przy przekonwertowanych ciałach; kąt działa tym mocniej, im mniejsze kołysanie (przy 100 % wcale).
- Mody zastępujące ciało trzeba najpierw przekonwertować za pomocą bodypak.pyz; zob. poradnik BODY_MODS na stronie moda.

## Twarz {#face}

Mimika Jodi.

- Suwaki dla min z gry (zrelaksowana, skupiona, uśmiech, ból, przestrach, zmęczona, cierpienie), spojrzenia i kształtów ust.
- „Zamknięte oczy” (w Spojrzenie) zamyka oczy, od otwartych do całkiem zamkniętych; mruganie gry działa dalej jak zwykle. Tylko na przekonwertowanych ciałach, jak suwaki ciała.
- Zaznaczony wpis zachowuje swoją wartość, także w pozach; niezaznaczony ustala animacja gry. „Ustal wszystkie” i „Wszystko grze” przełączają wszystkie naraz.
- Miny są mieszane (razem najwyżej 100 %) albo sumowane.
- Kafelek „+” zapisuje aktualną twarz ze zdjęciem. Prawy przycisk: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń.

## Mody {#mods}

Ustawienia innych modów, które rejestrują się w AltUI: po lewej ich wpisy, po prawej przełączniki, suwaki, liczby, wybory, kolory, pola tekstowe, klawisze i przyciski wybranego.

Ta karta pojawia się tylko wtedy, gdy taki mod jest zainstalowany.

## Opcje {#options}

Po lewej kategorie.

- Ogólne: język, ile ekranu zostaje wolne dla Jodi, czy można zdjąć bieliznę, jak wyglądają elementy, których nie masz, przełącznik Kodeksu dla encyklopedii, katalog „Wszystkie przedmioty” i „Automatycznie wyposażaj broń” dla karty Ekwipunek. „Bez powiadomień” ukrywa wszystkie powiadomienia na dole, z AltUI i z samej gry.
- Kafelki: rozmiar kafelków, osobne rozmiary dla kafelków strojów, stylizacji i ragdolli, elementy na kafelku stroju, bez limitu dla długich list, dane w podpowiedziach, rozmiar kafelków karty Ekwipunek.
- Grupy: łączenie grup lub modów o tej samej nazwie, długość nazw grup, wysokość obszaru chipów, wyszukiwanie chipów.
- Kamera: pole widzenia, odległość, wysokość, kamera podąża za wybranym slotem. Dwa przełączniki wolnej kamery (także w trybie ragdolli): bez kolizji – przelatuje przez ściany i Jodi – oraz dowolnie daleko od Jodi.
- Sterowanie: klawisz panelu, prędkość przewijania, wysokość kamery prawym przyciskiem myszy, jak wysoko kółko myszy podnosi ragdolla na jeden ząbek.
- Ruch: własna prędkość chodu i biegu Jodi (od 50 do 200 %); kucanie i skakanie pozostają bez zmian. „Zwolnienie wł.” włącza zwolnienie, „Tempo zwolnienia” (od 5 do 90 %, domyślnie 25 %) ustala, jak wolno płynie czas; pozycja szybkiego menu „Zwolnienie wł / wył” działa tak samo jak przełącznik. „Przywróć domyślne” przywraca prędkość chodu, biegu i zwolnienia. „Stanie” wybiera animację bezczynności Jodi: animacje gry (rozglądanie się, oglądanie paznokci, oglądanie nogi, ostrożnie, ranna, pozowanie) i zainstalowanych modów bezczynności (IdleAltUI_…).
- Szybkie menu: klawisz, przezroczystość, co jest w kole, własne klawisze.
- Motyw: każdy kolor panelu i jego krycie, obraz tła (wypełnienie, wyrównanie, odcień, sepia, odwrócenie, własne krycie) i obraz dla kafelków i kart, schematy kolorów zapisane pod nazwą; reset jest na pasku stanu. Motyw zapisany teraz zachowuje także obrazy i ich ustawienia. Własne obrazy: Background_1 … Background_30 i Button_1 … Button_30 (.png, .jpg lub .jpeg) w folderze podanym na stronie. „Pokaż podglądy” pokazuje same obrazy na ich chipach; prawy klik na podglądzie własnego obrazu: „Utwórz podgląd ponownie”.
- Konflikty slotów: rozdzielenie par slotów gry (na przykład biustonosz i koszula), aby można było nosić oba elementy. Poniżej: „Kilka rzeczy w jednym slocie” – włączony slot zachowuje swoje rzeczy, gdy zakłada się kolejną (na przykład podkolanówki na rajstopy), dla Jodi, towarzyszy i wyglądów.
- Karty: tekst, ikony lub oba na pasku kart; wyłączanie kart. „Spróbuj w jednym wierszu”: podpisy najpierw się zmniejszają, potem skracają, aby pasek mieścił się w jednym wierszu, gdzie to możliwe.

## Zarządzanie {#manage}

Własne nazwy wyświetlane dla modów, grup, ubrań, fryzur, skór, makijażu, póz i presetów wyglądu.

- Nazwy są używane w całym panelu i znajdowane przez wyszukiwanie; oryginalny identyfikator nadal można wyszukać i widać go w podpowiedzi.
- Chipy i wyszukiwanie filtrują listę; „tylko mody” ukrywa wpisy gry; ↺ przywraca nazwę domyślną.
- Za pomocą altui_names.pyz nazwy można wyeksportować do pliku tekstowego i zaimportować z powrotem.
- Mody broni są na liście razem z innymi modami.
- „Użycie” pokazuje, które mody są teraz używane: dla każdego moda używane elementy i miejsca, w których są (Jodi teraz, stroje, stylizacje, presety, ulubione, towarzysze, sceny ragdolli, stanie, broń). Nieużywane mody są niżej na szaro, tak samo mody, których użycia AltUI nie potrafi ustalić (mapy, mody skryptowe). „Pokaż zawartość” otwiera każdy z nich. To, co leży tylko w szafie, nie liczy się jako użycie. Każdy mod to kafelek z nazwą wyświetlaną i plikiem pak; miejsca elementu są zebrane według rodzaju (np. „Stroje 4–6, 8”). Lista jest zbierana przy otwarciu „Użycie”; gdzie indziej liczba po lewej jest z ostatniego razu (przed pierwszym razem brak).

## Ragdolle {#ragdolls}

Figury z fizyką do ustawiania i pozowania na poziomie: kopie Jodi, zombie i ludzie.

- „+ Utwórz kopię Jodi” stawia kopię przed nią, stojącą i zamrożoną w jej obecnej pozie, ze wszystkim, co ma na sobie. Stylizacja staje się figurą przez „Utwórz jako ragdoll” w jej menu kontekstowym.
- „Zombie i ludzie”: jeden kafelek z obrazem na rodzaj zombie, do tego pielęgniarka i ocalała. Kliknięcie tworzy figurę; linki pod kafelkiem tworzą jej warianty.
- Najemnik też jest rodzajem figury; trzyma karabin w rękach.
- Każda figura ma swój wiersz: aktywna (fizyka, upada i można nią rzucać) lub zamrożona (trzyma pozę), „stawy ›”, zablokuj wszystkie, zwolnij wszystkie, usuń. Na dole po prawej, na pasku stanu: „Usuń wszystkie” (usuwa każdą figurę) i „Kule stawów: wł./wył.”.
- „stawy ›” rozwija 17 stawów figury, każdy z dwoma przełącznikami: zablokowany/wolny i ruchomy/nieruchomy. Zablokowany staw pozostaje sztywny, dopóki figura jest aktywna; ruchomy można ustawiać na zamrożonej figurze.
- Kule stawów pokazują, gdzie można chwycić: szare, czerwone = zablokowany, zielone = ruchomy, niebieskie = przypięty. Zasłonięte prześwitują blado przez ciało; kliknięcie kuli chwyta dokładnie ten staw. Pojawiają się tylko na tej karcie i w trybie ragdoll.
- Pozy (w rozwiniętym wierszu): nazwa i „zapisz pozę” zapamiętują ułożenie części ciała oraz to, które stawy są zablokowane lub ruchome. Pozę można wczytać na każdą figurę tego samego rodzaju, na każdym poziomie – kliknięcie wczytuje, prawy przycisk: wczytaj / usuń. Figura przy tym zamarza i staje na podłodze.
- Sceny: „Zapisz scenę jako” zapamiętuje każdą figurę poziomu z wyglądem, miejscem, pozą i stawami; ta sama nazwa na tym samym poziomie nadpisuje scenę. Widać tylko sceny bieżącego poziomu. Kliknięcie wczytuje scenę i zastępuje obecne figury; prawy przycisk: wczytaj / usuń.

Z myszą na figurze, obok panelu i w trybie ragdolli:

- Przeciąganie lewym przyciskiem zamrożonej figury przesuwa ją po podłodze; kółko myszy podnosi ją lub opuszcza podczas przeciągania.
- Przeciąganie lewym przyciskiem aktywnej figury chwyta część ciała pod myszą; puść, a figura upadnie.
- Prawy przycisk podczas przeciągania przypina część w tym miejscu; reszta figury na niej wisi. Chwyć ją ponownie, a będzie wolna. „puść wszystkie” w wierszu figury zwalnia wszystkie.
- Przeciąganie prawym przyciskiem obraca figurę wokół bioder.
- Shift + lewy przycisk blokuje lub zwalnia kliknięty staw.
- Shift + prawy przycisk na zamrożonej figurze czyni staw ruchomym. Przeciąganie wtedy lewym przyciskiem części ciała poniżej ruchomego stawu porusza tylko tę część; zostaje tam, gdzie ją puścisz – tak pozuje się figurę.
- Przeciąganie prawym przyciskiem części ciała pod ruchomym stawem zamrożonej figury obraca tę kończynę wokół stawu: chwycony punkt podąża za myszą, dłoń i palce obracają się razem z nią. Kółko myszy skręca przy tym kończynę wokół jej własnej osi. Obrót zostaje w pozie i zapisuje się z pozami i scenami; ograniczenia stawów działają dopiero, gdy figura stanie się aktywna.

Bez panelu figury aktywuje lub zamraża szybkie menu: „Ragdoll: aktywuj / zamroź tę na środku” bierze figurę na środku ekranu, „Ragdolle: aktywne / zamrożone” przełącza wszystkie.

## Tryb ragdolli {#ragmode}

Przesuwanie i pozowanie figur bez panelu, z kamerą poruszającą się swobodnie po pomieszczeniu. Uruchamia go trzeci okrągły przycisk nad + i − albo szybkie menu.

- Kursor myszy pozostaje widoczny; na figurze wszystko działa jak obok panelu (zob. „Ragdolle”).
- W A S D i Q E przesuwają kamerę, Shift szybciej; Shift + kółko ustawia prędkość.
- Przeciąganie w pustym miejscu obraca kamerę.
- Esc lub B kończy tryb.

## Towarzysze {#followers}

Stylizacje jako postacie w grze: towarzysz idzie z Jodi, walczy i słucha rozkazów; NPC zostaje na miejscu i się broni.

- W zakładce Stylizacje prawy klik na stylizację: „Utwórz jako towarzysza” albo „Utwórz jako NPC”. Postać pojawia się przed Jodi w tej stylizacji.
- Zakładka „Towarzysze” pokazuje wszystkie postacie ze stanem (podąża, czeka, NPC, nieaktywny, poległ) i przyciskami: „Za mną”, „Czekaj tutaj”, „Przywołaj”, → NPC / → Towarzysz, „Aktywny”, ∞ z sercem (nieśmiertelny), ∞ z nabojami (amunicja bez końca) i zębatka (zmień nazwę, zmień stylizację, ożyw, usuń). „...” zwija i rozwija kafelki postaci (ubrania i plecak); zostaje tak dla każdej postaci, także po ponownym uruchomieniu.
- Towarzysze są nad NPC, linia oddziela obie grupy. Przyciski nad wierszami pokazują wszystkich, tylko towarzyszy albo tylko NPC (zostaje po ponownym uruchomieniu).
- Kliknięcie wiersza wybiera postać. Na górze są plecak (po lewej) i skrzynia (po prawej): kliknięcie daje przedmiot wybranej postaci, broń razem z malowaniem i akcesoriami. Kliknięcie kafelka postaci oddaje go do plecaka; prawy klik: wszystko albo do skrzyni. „...” nad listą zwija ją.
- Menu kontekstowe stosu – Jodi lub postaci – ma wiersz ilości jak w karcie Ekwipunek: „Daj 5”, „Weź 5”, do skrzyni.
- Ubrania to prawdziwe rzeczy postaci, jak u NPC w grze: niszczą się, mogą zostać zerwane i widać je w ekwipunku NPC samej gry, gdzie można je też wymieniać. Pod postacią jej rzeczy są kafelkami (uszkodzone mają znacznik): kliknięcie zdejmuje rzecz i wkłada ją do plecaka Jodi; prawy klik: napraw zestawem do szycia z plecaka Jodi albo napraw wszystko. W kolumnie plecaka „Ubrania” pokazuje rzeczy Jodi: kliknięcie daje jedną wybranej postaci, która ją zakłada (uszkodzenia i kolory idą razem z nią).
- Wyłączenie „Aktywny” zabiera postać ze świata razem z tym, co niesie; po włączeniu wraca przed Jodi.
- „Amunicja bez końca”: postać przeładowuje broń palną bez końca i nie potrzebuje amunicji w torbie. Broń z magazynkiem nie rusza jej amunicji; strzelba i granatnik najpierw zużywają to, co ma przy sobie.
- Postać, która nie jest nieśmiertelna, może polec. Zostaje na liście, a „Ożyw” przywraca ją z jej rzeczami. Postacie nigdy nie zmieniają się w zombie.
- „+ Jason” (na dole po prawej w zakładce) dodaje Jasona z fabuły jako towarzysza, z jego Glockiem. Słucha poleceń, idzie z Jodi i jest zapisywany. Walczy tylko własnym Glockiem: Glock, który mu dasz, staje się jego, innej broni nie przyjmuje. Nie ma stylizacji, ubrań ani makijażu; gdy leży, nie da się go uleczyć – „Ożyw” przywraca go.
- „Usuń” pyta o potwierdzenie; przedmioty i broń postaci trafiają do skrzyni, a ubrania do plecaka Jodi.
- „Zmień stylizację” przechodzi do zakładki Stylizacje: kliknij stylizację, którą postać ma nosić.
- Każda postać nosi makijaż swojej stylizacji i ma jeden z głosów NPC z gry. Postać utworzona w AltUI przed 2.2.0 pokazuje makijaż Jodi, dopóki „Zmień stylizację…” nie da jej własnego.

AltUI przechowuje postacie we własnym zapisie (AltUI_Followers.sav); zapis gry nigdy ich nie zawiera. Podążający towarzysze przechodzą z Jodi do każdego poziomu i są po wczytaniu; czekający i NPC zostają w swoim poziomie na swoim miejscu.

Szybkie menu: „Towarzysz: za mną / czekaj tutaj” dotyczy towarzysza w polu widzenia, „Wszyscy towarzysze: za mną / czekać” – wszystkich. „Wszyscy towarzysze: do mnie” sprowadza każdego aktywnego towarzysza na miejsca przed Jodi – także tego, który czeka na innym poziomie.

## Kodeks {#kodex}

- Encyklopedia: wpisy z archiwum na komputerze w biurze Jodi, z obrazem i tekstem. Pokazywane są tylko te odblokowane w grze – albo wszystkie po włączeniu przełącznika w Opcje › Ogólne.
- Hasła: zamki szyfrowe bieżącego poziomu, najbliższy pierwszy, z odległością i informacją, czy są zamknięte. Każdy kod pozostaje ukryty, dopóki go nie klikniesz.
- Podręcznik AltUI: ten tekst.

## TV {#tv}

- Widoczna tylko wtedy, gdy na bieżącym poziomie jest telewizor (biuro Jodi), albo zawsze – z przełącznikiem w Opcje › Ogólne. Przy kilku telewizorach sterowany jest ten najbliżej Jodi.
- Włącz / Wyłącz działają jak klawisz E przy telewizorze. Listę filmów telewizor odczytuje przy pierwszym włączeniu – do tego czasu karta prosi, aby włączyć go raz.
- Kliknięcie filmu odtwarza go. Film już rozpoczęty jest kontynuowany od miejsca, w którym został przerwany, tak jak na samym telewizorze.
- Własne filmy: włóż pliki .mp4 do folderu gry TheKillingAntidote/Videos/TV/. Pojawią się po ponownym wczytaniu poziomu.

## Szybkie menu {#quick}

Przytrzymaj 4 (inny klawisz w Opcje › Szybkie menu), a wokół myszy otworzy się koło. Puść nad wpisem, aby go wykonać; puść na środku, aby nic nie robić.

- Wpisy: stroje, stylizacje, twarze, presety wyglądu, pozy, karty, ustawienia innych modów i akcje: swobodna kamera, tryb fotograficzny, tryb ragdolli, kopia Jodi jako ragdoll, przełączanie wszystkich ragdolli między aktywnymi a zamrożonymi, aktywuj / zamroź tę na środku, usuń wszystkie ragdolle, własna prędkość wł. / wył.
- Dalsze akcje: „Zwolnienie wł / wył”, „Zatrzymaj czas / dalej” (wszystko staje; panel i kamery działają dalej; także kamera trybu fotograficznego gry), „Ukryj / pokaż Jodi” (z ubraniem, włosami i bronią; w następnym poziomie znów jest widoczna) oraz rozkazy dla towarzyszy (zobacz „Towarzysze”).
- „Ukryj / pokaż interfejs gry” wyłącza i włącza HUD gry, tak jak jej tryb fotograficzny.
- „+1 Niewidzialna ręka” wkłada jedną Niewidzialną rękę do plecaka (zob. Ekwipunek › Wszystkie przedmioty).
- Własne klawisze: w Opcje › Szybkie menu kliknij prawym przyciskiem pozycję w „Dostępne” i naciśnij klawisz – pozycja działa wtedy pod tym klawiszem, przy zamkniętym panelu, także w swobodnej kamerze i w trybie fotograficznym gry. Kliknięcie klawisza w wierszu przypisuje inny, ✕ go usuwa. Klawisz panelu, klawisz szybkiego menu i klawisz już przypisany są odrzucane; klawisz używany przez grę uruchamia oba działania.
- Dodaje się je w Opcje › Szybkie menu albo prawym przyciskiem na kafelku, karcie lub wpisie moda („Dodaj do szybkiego menu”).
- Kolejność w kole to kolejność listy w Opcje › Szybkie menu.

## Dla autorów modów {#modding}

- Mody z ubraniami nie potrzebują niczego szczególnego: AltUI czyta tabele gry i przypisuje każdy element do jego slotu.
- Mody zastępujące ciało lub broń można przekonwertować za pomocą bodypak.pyz i weaponpak.pyz, aby kilka mogło być zainstalowanych obok siebie; można je też zbudować dla AltUI bezpośrednio w Unreal Editorze.
- Mody bezczynności (pak zastępujący animację bezczynności Jodi) można przekonwertować za pomocą idlepak.pyz: python3 idlepak.pyz <mod>.pak. Nowy IdleAltUI_….pak trafia do Mods/ i pojawia się w Opcje › Ruch › „Stanie”; własna animacja gry zostaje. AltUI musi być zainstalowany: konwerter buduje nowy pak częściowo z AltUI.pak i szuka go w zwykłych folderach Steam; jeśli leży gdzie indziej, podaj ścieżkę przez --altui <ścieżka do AltUI.pak>.
- Mody mogą pokazywać swoje ustawienia w karcie Mody przez dwie tabele danych i interfejs; jak to zrobić, opisuje MOD_UI.md w repozytorium kodu źródłowego.
