## O AltUI {#about}

AltUI to alternatywa dla szafy i ekranu wyglądu w The Killing Antidote: jeden panel do wszystkiego.

### W skrócie
- Ekrany gry nadal działają.
- Otwiera się w dowolnym miejscu poziomu klawiszem B – bez chodzenia do szafy czy lustra.
- Panel otwiera się na karcie, na której został zamknięty. Nieużywane karty można wyłączyć w Opcje › Karty. Wyłączona karta nic nie kosztuje; to, co tam ustawiono, nadal działa.

### Co zawiera
- Każdy element z gry i ze wszystkich zainstalowanych modów, na jednej liście na slot, z wyszukiwaniem, filtrami, ulubionymi i ukrywaniem.
- Fryzura, makijaż, ciało, twarz, pozy, broń oraz zapisane stroje i stylizacje.
- Ragdolle: kopie Jodi, zombie i ludzie do ustawiania i pozowania.
- Prędkość chodu i biegu Jodi.
- Karta Ekwipunek przenosi przedmioty między plecakiem Jodi a hiperskrzynią.
- Stylizacje stają się towarzyszami i NPC, którzy chodzą i walczą razem z nią.

## Instalacja i aktualizacje {#install}

AltUI.pak zawiera cały mod i trafia do TheKillingAntidote/Mods/.

### Instalacja
Uruchamia go jeszcze jeden plik:
- Blueprint Loader (osobny mały mod): TKA_BlueprintLoader.pak w TheKillingAntidote/Content/Paks/~mods/, albo
- własny hook AltUI: AltUI_Hook_P.pak w tym samym folderze ~mods/.
- Wystarczy jeden z nich; oba razem też działają.
- Z samym AltUI.pak klawisz B nic nie robi.

### Aktualizacje
- Aktualizacja zwykle wymienia tylko AltUI.pak.
- Lista zmian mówi, kiedy zmienia się też hook; stary hook nie może zostać w ~mods/.

### Ostrzeżenie o wersji gry
- Po aktualizacji gry albo z modem, który zastępuje tabele gry, AltUI może trafić na grę, dla której nie został zrobiony. Wtedy pokazuje ostrzeżenie, zanim cokolwiek zrobi.
- „Kontynuuj mimo to (na własne ryzyko)” zostaje zapamiętane dla tej wersji gry.
- „Na razie wyłącz AltUI” pyta ponownie w następnym poziomie.

### Usuwanie AltUI
Skasuj skopiowane pliki:
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
- AltUI_BodyPresets.sav – presety ciała
- AltUI_ModPresets_<mod>.sav – presety ustawień moda (zakładka Mods), jeden plik na mod
- AltUI_Props.sav – postawione obiekty i sceny obiektów
- AltUI_ObjCache.sav – obiekty znalezione przez wyszukiwanie modów
- AltUI_ModScan.sav – z którego moda pochodzi każdy element; tworzy się sam od nowa
- AltUI_Log.sav, BPLoader_Log.sav – tylko z wersji testowych
- folder AltUI – zdjęcia stylizacji, twarzy, presetów wyglądu, ciała i modów, własne obrazy tła i przycisków
- folder WeaponIcons – obrazy broni
- folder ObjectIcons – obrazy obiektów

Ubrania, stroje, makijaż i fryzura są zapisywane w zapisach samej gry i zostają.

## Sterowanie {#controls}

Klawisze i mysz w panelu, wokół Jodi i podczas gry.

### Panel
- B otwiera i zamyka panel (inny klawisz w Opcje › Sterowanie); Esc go zamyka.
- Lewy przycisk wybiera, zakłada lub stosuje; prawy otwiera menu kontekstowe kafelka, wiersza lub karty.
- Kółko myszy przewija; prędkość ustawia się w Opcje › Sterowanie.
- Cofnij i Ponów (pięć kroków) są na pasku stanu na dole.
- Przytrzymaj 4, aby otworzyć szybkie menu (zob. „Szybkie menu”).

### Kamera i Jodi
- Gdy panel jest otwarty, Jodi nie może chodzić.
- Przeciąganie po tle obraca kamerę.
- Kliknięcie na Jodi i przeciąganie obraca ją – po zamknięciu panelu wraca do poprzedniej pozycji.
- + i − zmieniają odległość kamery co 5 %, kółko myszy nad Jodi co 4 %.

### Podczas gry
- Gdy panel jest zamknięty, kółko myszy przybliża lub oddala kamerę od Jodi.
- Z pozycją szybkiego menu „Wysokość kamery (kółko)” podnosi lub opuszcza ją zamiast tego (lewy przycisk lub Esc kończy).
- Przy celowaniu zostaje widok gry. Odległość i wysokość są zapamiętywane.

### Okrągłe przyciski
Okrągłe przyciski nad + i −:
- Swobodna kamera: mysz obraca, W A S D i Q E przesuwają, Shift szybciej, kółko ustawia prędkość, Esc wraca.
- Tryb fotograficzny gry (Esc wraca).
- Tryb ragdolli (zob. „Tryb ragdolli”).
- Najwyższy z nich (żarówka) to światło kamery: rozjaśnia to, co widzi kamera – obok panelu, w swobodnej kamerze i w trybie zdjęć.
- Kliknięcie żarówki otwiera małe menu: wł. / wył., kolor światła (paleta) i suwak jasności.
- Światło tylko rozjaśnia (bez odblasków, bez snopu we mgle). W czasie gry jest wyłączone i wraca takie, jak je zostawiono, gdy panel się otworzy.

### Menu główne
- W menu głównym B otwiera małe menu: trzy sceny menu i scenę ładowania, następną kamerę oraz ukrywanie menu i tekstów gry (Esc je przywraca).

## Ubrania {#clothes}

Po lewej sloty, po prawej elementy wybranego slotu.

### Zakładanie i wyszukiwanie
- Kliknięcie elementu zakłada go, kliknięcie założonego zdejmuje.
- Chipy nad listą filtrują według moda lub grupy; „...” zwija rzędy chipów.
- Pole wyszukiwania zawęża chipy; wyszukiwanie nad listą znajduje elementy po nazwie, modzie lub grupie.
- Wyszukiwanie znajduje mod także po nazwie jego paka, tutaj i w każdej innej karcie.
- Filtry: tylko posiadane, tylko ulubione, tylko vanilla, tylko założone.
- Podpowiedź pokazuje, z którego moda pochodzi element.

### Menu kontekstowe
- Prawy przycisk na elemencie: ulubione, zostaw założone, ukryj, kolor z palety gry, przywróć kolor, do plecaka, zmień nazwę, tylko ta grupa, pokaż zawartość moda, pokaż w zakładce.
- Uszkodzenie: od 0 do 100 %, od razu na noszonym elemencie; przy każdym innym zostaje zapamiętane, aż element zostanie założony. Noszone elementy bez tekstur uszkodzeń nie mają suwaka.

### Zostaw założone
- Oznaczona część, którą założyłaś sama, zostaje przy zakładaniu looku lub stroju.
- Look pomija wtedy części z tego samego slotu (lub ze slotu, który do niego nie pasuje) i wymienia je w komunikacie.
- Część założona przez look lub strój nie zostaje przy następnej zmianie, nawet jeśli jest oznaczona – przymierzanie strojów nigdy nie gromadzi części.
- Kafelek pokazuje „zostaje”. Cofnij przywraca dokładnie poprzedni stan.

### Kody kolorów
- Pod paletą kolorów gry pole pokazuje kolor jako #RRGGBB; wpisz kod i naciśnij Enter, aby go ustawić.
- „Zapamiętaj” zachowuje kolor w AltUI, „Użyj” nakłada go na inny element lub slot.

### Szuflady
Własne kolekcje ubrań, na pasku nad listą.
- „Domyślny” pokazuje wszystko; „+” tworzy nową szufladę („Szuflada 1”, „Szuflada 2” …).
- Szuflada pokazuje tę samą stronę – sloty, przyciski, wyszukiwanie, filtry, ulubione – tylko z jej rzeczami, a sloty liczą tylko je.
- Prawy przycisk na rzeczy › „Szuflada ›” otwiera obok menu listę szuflad: znacznik oznacza, że rzecz w niej jest; kliknięcie wkłada ją lub wyjmuje, „+ Nowa szuflada” tworzy szufladę z tą rzeczą.
- Rzecz może być w dowolnej liczbie szuflad; w szufladzie menu ma też „Usuń z tej szuflady”.
- Prawy przycisk na szufladzie: zmień nazwę (Enter zatwierdza, Esc anuluje), w lewo / w prawo, usuń (najpierw pyta – rzeczy zostają).
- Pokazana szuflada zostaje po ponownym uruchomieniu.

## Stroje {#outfits}

Zapisane stroje gry – te same, których używają szafa i lustro.

### Zapisywanie i zakładanie
- Kafelek „+” zapisuje to, co Jodi ma na sobie, jako nowy strój.
- Kliknięcie stroju zakłada go.
- Strój bez własnej nazwy jest pokazywany jako „Strój” z jego miejscem na liście.
- Rozmiar kafelków i liczbę elementów na kafelku ustawia się w Opcje › Kafelki.

### Menu kontekstowe
- Prawy przycisk: załóż, pokaż zawartość, dodaj do szybkiego menu lub usuń z niego, zmień nazwę, przesuń w lewo / w prawo / na początek / na koniec, usuń.
- „Aktualizuj tym, co ma na sobie”: strój przejmuje to, co Jodi ma teraz na sobie, w obecnych kolorach; nazwa, miejsce, wpis w szybkim menu i własny klawisz zostają.

### Kolory
- Strój zapisany tutaj zachowuje każdy kanał koloru swoich elementów, tak jak pokolorował je AltUI.
- Sama gra pamięta jeden kolor na element; strój zapisany przy lustrze ma tylko ten jeden.

### Udostępnianie
- Prawy przycisk → „Eksportuj (udostępnij)…” pokazuje go jako tekst – Ctrl+A, Ctrl+C i wyślij.
- „Importuj…” w prawym dolnym rogu: wklej Ctrl+V; „Sprawdź” pokazuje zawartość i brakujące mody (to, co jest już zapisane dokładnie tak samo, zostaje pominięte).
- Potem importuj wszystko albo bez brakujących części.
- Zdjęcia nie są udostępniane – zrób nowe przez „Aktualizuj”.

## Stylizacje {#looks}

Stylizacja to wszystko naraz: ubrania z kolorami, fryzura i kolor włosów, makijaż, oczy, skóra, mutacja, suwaki ciała, mod ciała i twarz.

### Zapisywanie i stosowanie
- Kafelek „+” zapisuje aktualną stylizację ze zdjęciem całej postaci: z przodu albo wolną kamerą – przesuń ją, gdzie chcesz, i kliknij, aby zrobić zdjęcie (Esc: zamiast tego z przodu).
- Kliknięcie stylizacji ją stosuje.

### Sortowanie
- „Sortowanie: …” w prawym dolnym rogu karty Stylizacje (lewy lub prawy przycisk) otwiera menu z siedmioma kolejnościami: Własna, Nazwa A–Z, Nazwa Z–A, Najnowsze najpierw, Najstarsze najpierw, Ostatnio zmienione, Najdawniej zmieniane. Aktywna jest oznaczona znakiem „>”.
- „Własna” zachowuje twoją kolejność – tę ustawianą przez „Przesuń”. Przesuwanie jest dostępne tylko we „Własnej”; w pozostałych kolejnościach pozycję wyznacza sortowanie.
- Daty są zapisywane dopiero od tej wersji. Wcześniej zapisane stylizacje ich nie mają: w kolejnościach według daty uchodzą za najstarsze, a w podpowiedzi nie pokazują daty.
- Po najechaniu na stylizację widać, kiedy powstała i kiedy ostatnio ją zmieniono („Utworzono … · Zmieniono …”). Zmiana nazwy nie zmienia daty, „Aktualizuj” zmienia. Zaimportowana stylizacja liczy się jako nowa.
- Szybkie menu wypisuje stylizacje w tej samej kolejności.

### Menu kontekstowe
- Prawy przycisk: pokaż zawartość, zmień nazwę, aktualizuj (zdjęcie z przodu, wolną kamerą lub z zachowaniem zdjęcia), przesuń, usuń, dodaj do szybkiego menu lub usuń z niego.
- „Pokaż zawartość” wypisuje wartości ciała w kolejności strony Kształt ciała, z jej nagłówkami „Piersi” i „Pośladki i biodra” nad kątem i kołysaniem.
- Także: „Utwórz jako ragdoll”, „Utwórz jako towarzysza”, „Utwórz jako NPC”, „Utwórz jako wroga” (zobacz „Ragdolle” i „Towarzysze”).

### Oczyszczona kopia
- „Oczyszczona kopia (bez brakujących części)” jest widoczna tylko, gdy wygląd zawiera części moda, którego już nie ma, albo wiersze makijażu / oczu, których nie zna żadna tabela.
- Tworzy nowy wygląd tuż za nim bez tych wpisów, z tym samym zdjęciem.
- Oryginał zostaje bez zmian; ponowne zapisanie nigdy ich samo nie usuwa.

### Udostępnianie
- Prawy przycisk → „Eksportuj (udostępnij)…” pokazuje go jako tekst – Ctrl+A, Ctrl+C i wyślij.
- „Importuj…” w prawym dolnym rogu: wklej Ctrl+V; „Sprawdź” pokazuje zawartość i brakujące mody (to, co jest już zapisane dokładnie tak samo, zostaje pominięte).
- Potem importuj wszystko albo bez brakujących części.
- Zdjęcia nie są udostępniane – zrób nowe przez „Aktualizuj”.

## Plecak {#bag}

To, co Jodi ma na sobie i co niesie.

### Pojedyncze elementy
- Kliknięcie założonego elementu zdejmuje go, kliknięcie niesionego zakłada go.
- Prawy przycisk: załóż lub zdejmij, napraw (potrzebny zestaw do szycia), usuń z plecaka, do szafy.
- Menu kontekstowe ma też suwak uszkodzenia (zobacz „Ubrania”).

### Cały plecak
- „Uporządkuj plecak” usuwa elementy, które nie są założone i są też w szafie.
- „Wszystko do plecaka” zdejmuje każdy założony element i wkłada go do plecaka.

## Ekwipunek {#inventory}

Przedmioty Jodi i hiperskrzynia, jedna lista pod drugą.

### Listy
- Chipy filtrują według grup gry (broń, amunicja, akcesoria do broni, narzędzia…).
- Waga pokazuje, ile Jodi niesie, ile może unieść i jak bardzo jest przeciążona.
- „...” nad listą zwija ją, ↑↓ daje jej całą wysokość (jeszcze raz: powrót).
- Rozmiar kafelków tej karty ustawia się w Opcje › Kafelki.
- Na mapach, na których gra nigdy nie zapisuje plecaka (na przykład strzelnica), karta to mówi: to, co chcesz zachować, trzymaj w skrzyni.

### Przenoszenie przedmiotów
- Kliknięcie wkłada jeden przedmiot do skrzyni albo wyjmuje jeden.
- Prawy przycisk: połowa albo wszystko, użyj, obejrzyj, wyrzuć, szybki wybór 1 lub 2, rozładuj, „Akcesoria…” (otwiera broń w karcie Broń).
- Menu kontekstowe stosu kończy się wierszem „Ilość”: suwak i pole liczbowe, a pod nimi po jednym wpisie na cel z tą liczbą („Włóż 5 do skrzyni”, „Weź 5”). Enter w polu wykonuje pierwszy wpis.
- W katalogu liczba oznacza sztuki, a pole przyjmuje więcej, niż sięga suwak. Broń palna i pojedyncze przedmioty nie mają ilości.
- „Automatycznie wyposażaj broń” (Opcje › Ogólne, domyślnie włączone): broń ze skrzyni lub z katalogu trafia do ręki Jodi tak jak w grze; wyłączone – Jodi trzyma to, co trzymała.
- Wszystko idzie przez funkcje samej gry, więc jej zasady zostają – razem z przeciążeniem.

### Wyrzuć wszystko
- „Wyrzuć wszystko” kładzie na ziemi jeden obiekt na paczkę.
- Od 100 obiektów najpierw pyta okno: „Anuluj”, „Zamiast tego zniszcz” (przedmioty znikają, nic nie spada) albo „Wyrzuć mimo to” – tyle obiektów z fizyką naraz może spowodować awarię gry. Esc anuluje.

### Zawsze wyposażaj automatycznie
- „Zawsze wyposażaj automatycznie” (prawy klik, także w katalogu): po każdym wczytaniu poziomu AltUI wkłada przedmiot, nowy, do plecaka Jodi, do ilości, jaką kafelek miał przy oznaczeniu (co najmniej jedna paczka). Nigdy niczego nie zabiera.
- Takie kafelki mają złotą okrągłą strzałkę i złotą ramkę. „Przestań wyposażać automatycznie” to kończy.
- „Uzupełniaj oznaczone przedmioty także w fabule” (Opcje › Ogólne, domyślnie włączone): po wyłączeniu AltUI niczego nie uzupełnia na poziomach fabularnych; oznaczenia zostają, a biuro i wyzwania działają jak dotąd.
- Oznaczona broń wraca taka, jaka była przy oznaczaniu (noszona lub ze skrzyni, z katalogu bez dodatków), z pełnym magazynkiem; zapasowa część w plecaku zostaje.
- Jeśli przy wczytaniu poziomu Jodi nosi ją z innymi dodatkami, zostają one przywrócone, a zdjęte części trafiają do plecaka.
- Aby zapisać nowy zestaw, usuń oznaczenie i oznacz broń ponownie.

### Wszystkie przedmioty
- „Wszystkie przedmioty” jest domyślnie wyłączony (Opcje › Ogólne): każdy przedmiot gry jako trzecia lista z własnym wyszukiwaniem.
- Kliknięcie wkłada jedną paczkę do plecaka; prawy przycisk: pięć albo do skrzyni.
- W „Kolekcji” jest też Niewidzialna ręka z gry: dopóki jest w plecaku, przynosi Jodi przedmioty z okolicy, jeden po drugim, tym szybciej, im więcej rąk (jedna co 2,5 s, od sześciu co 0,1 s).
- Ile ich ma Jodi, widać w „Kolekcji” plecaka.

## Fryzura {#hair}

Wszystkie fryzury z gry i z modów.

### Wybór fryzury
- Kliknięcie fryzury ją zakłada.
- Ulubione są na górze, nad wszystkimi fryzurami.
- Pole wyszukiwania nad kafelkami znajduje fryzury po wyświetlanej nazwie, identyfikatorze, nazwie moda i pliku pak; × je czyści.

### Kolor włosów
- „Kolor włosów...” otwiera paletę gry.
- „Naturalne kolory włosów” daje 14 gotowych kolorów.

### Menu kontekstowe
- Prawy przycisk: dodaj do / usuń z ulubionych, przywróć kolor włosów, zmień nazwę, pokaż zawartość moda.
- Na fryzurze z moda także: „Zmień nazwę moda…”.

## Pozy {#poses}

Każda animacja akcji, którą znają gra i twoje mody z pozami – lista za aplikacją „rytm” w telefonie.

### Odtwarzanie
- Kliknięcie pozy ją odtwarza; ponowne kliknięcie albo „Zakończ pozę” ją zatrzymuje.
- „Powtarzaj pozy: wł.” na pasku stanu uruchamia od nowa pozę, która kończy się sama – dopóki Jodi się nie ruszy, klawisz użycia lub „Zatrzymaj pozę” jej nie zakończy albo nie wybierzesz innej pozy. Wiele modów póz i tak powtarza swoje pozy.
- Głośnik w rogu kafelka oznacza pozę z dźwiękiem.

### Sortowanie i wyszukiwanie
- Pozy są posortowane według postawy (stojąca, siedząca, leżąca) i rozdziału.
- Chipy filtrują według moda, wyszukiwanie znajduje tytuły.
- „Zmierz wszystkie” odtwarza raz każdą pozę, która nie ma jeszcze postawy, i ją sortuje; pokazuje przy tym nazwę mierzonej pozy.

### Menu kontekstowe
- Prawy przycisk: ulubione, ukryj, oznacz jako stojąca / siedząca / leżąca / w ruchu, zmień nazwę, dodaj do szybkiego menu.
- „Użyj jako bezczynność”: poza zaczyna się po 1,5 s bezruchu i kończy, gdy Jodi idzie, wyciąga broń lub kuca. „Już nie jako bezczynność” to wyłącza.

## Broń {#weapons}

Po lewej jeden wpis na broń, także broń do walki wręcz. Dla każdej broni model, skórkę i dźwięk strzału wybiera się osobno. Wybór jest zapamiętywany i nakładany ponownie, gdy broń zostanie podniesiona lub wyjęta ze skrzyni.

### Modele i skórki
- U góry modele – model gry i każdy zainstalowany mod modelu.
- Na dole skórki – malowania broni z gry (bez puszki ze sprayem) i każdy zainstalowany mod skórki.
- Jeśli mod modelu ma własne wersje malowań z gry (zrobione dla jego modelu), pojawiają się jako dodatkowe skórki obok tych z gry, dopóki ten model jest wybrany.
- Kafelki modeli pokazują każdy model z wybraną skórką.
- Własne malowanie modelu działa tylko na tym modelu – na każdym innym broń zostaje taka, jaka jest, i jej kafelek też.
- Kafelek moda skórki jest przygaszony, gdy skórka nic nie zmienia na wybranym modelu; wiadomo to, gdy broń choć raz była w ręce Jodi z tym modelem.
- Malowanie nałożone w grze puszką ze sprayem zostaje: staje się wybraną skórką.

### Dźwięk
- Własny dźwięk strzału broni („Oryginalny”) i każdy zainstalowany dla niej dźwięk strzału.
- Kliknięcie wybiera dźwięk i go odtwarza; każda inna broń zachowuje swój.
- Zamontowany tłumik z własnym dźwiękiem nadal ma pierwszeństwo.

### Filtry i menu kontekstowe
- Chipy powyżej filtrują wszystkie trzy sekcje naraz.
- Prawy przycisk na kafelku: ulubione, ukryj, tylko ten mod.
- Prawy przycisk na modelu z moda: wymuś na nim skórki, pomiń magazynek, celownik, tłumik lub chwyt, pokaż własny obraz moda.
- Prawy przycisk na modelu, skórce lub dźwięku z moda: „Zmień nazwę moda…”.

### Obrazy
- „Zrób zdjęcia ponownie” na pasku stanu robi od nowa zdjęcia wszystkich kafelków broni.
- „Pokaż obrazy przedmiotów” na pasku stanu pokazuje na każdym kafelku własny obraz przedmiotu lub moda zamiast renderowanego.

### Akcesoria
- Jeden wiersz na każdy slot broni (celownik, lufa, chwyt, magazynek), „Brak” na początku.
- Części pochodzą z plecaka albo ze skrzyni i wtedy trafiają do plecaka.
- Akcesoria można zakładać tylko na broń, którą Jodi ma przy sobie; broń zachowuje wybrany tu model, skórkę i dźwięk.

### Mody broni
- Mody broni i dźwięków strzału trzeba najpierw przekonwertować za pomocą weaponpak.pyz; zob. poradnik WEAPON_MODS na stronie moda.

## Wygląd {#look}

Skóra, każdy rodzaj makijażu, oczy i presety wyglądu z gry.

### Makijaż i oczy
- Kliknięcie wpisu go nakłada.
- Prawy przycisk na makijażu: tonowanie paletą gry, przywróć tonowanie.
- Oczy: kolor tęczówki i rzęs w menu kontekstowym.

### Naoliwiona skóra
- „Naoliwiona skóra” nad skórami nadaje skórze połysk, jak mokra skóra w grze (mokra skóra gry = 50 %).
- Zaznaczone = twoja wartość, także wbrew fabule; odznaczone = znów decyduje gra.
- Tylko u Jodi. Looki i presety wyglądu zapamiętują to ustawienie; starsze przywracają „decyduje gra”.

### Mutacja
Zmutowany wygląd Jodi z fabuły w częściach.
- Kolor skóry i poświata jako suwaki (zaznaczone = działa), żyły i oczy jako przełączniki; „Resetuj” wyłącza wszystko.
- Makijaż pozostaje widoczny na przebarwionej skórze; własny kolor tęczówki barwi zmutowane oko.
- „Wygląd z fabuły” ustawia wygląd z przerywnika: materiał skóry z fabuły, wszystkie wiersze na maksimum; potem można cofnąć pojedyncze wiersze. Makijaż i blizny nie są z nim widoczne.
- Gdy fabuła sama zmienia Jodi w mutanta, obowiązuje jej wygląd.

### Presety
- Kafelek „+” zapisuje aktualny wygląd ze zdjęciem.
- Prawy przycisk: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń, szybkie menu.

### Udostępnianie
- Prawy przycisk na presecie → „Eksportuj (udostępnij)…”, „Importuj…” w prawym dolnym rogu – jak przy lookach.
- Bez brakujących części odpada brakująca fryzura, skóra lub wiersz makijażu.
- Jeden tekst może łączyć looki, stroje, twarze i wszystkie presety; każda strona z „Importuj…” przyjmuje całość.

## Kształt ciała {#body}

Suwaki biustu i talii z gry, a przy przekonwertowanych modach ciała jeszcze więcej.

### Ciała
- Chipy przełączają między ciałem z gry a każdym przekonwertowanym modem ciała.
- Mody zastępujące ciało trzeba najpierw przekonwertować za pomocą bodypak.pyz; zob. poradnik BODY_MODS na stronie moda.

### Suwaki
- Suwaki biustu i talii z gry.
- Przekonwertowane ciała mają dodatkowo suwaki kości: skala, biust, talia, pośladki i biodra, uda, łydki, ręce, dłonie, stopy.
- Są zapisywane dla każdego ciała; „Zresetuj kształt” je przywraca.
- Suwak sutków działa tylko, gdy piersi są odsłonięte.

### Kołysanie
- Piersi oraz pośladki i biodra: kołysanie (0 % = tylko animacja) zmienia fizykę gry i działa z każdym ciałem.
- Biustonosz nadal tłumi jak w grze.
- Kąt (tylko przy przekonwertowanych ciałach): działa tym mocniej, im mniejsze kołysanie (przy 100 % wcale).

### Biodra i nogi
- Szerokość bioder i rozstaw nóg są tylko przy przekonwertowanych ciałach.
- Rozstaw nóg przesuwa całą nogę w bok, w cm na stronę.
- Szerokość bioder też rozsuwa nogi (przy 1,3× około -2 cm je cofa), ale kosztuje to trochę szerokości bioder.

### Presety
- Nad suwakami „+” zapisuje wszystkie suwaki strony – suwaki ciała oraz biust i talię z gry – ze zdjęciem jako preset wybranego chipa ciała.
- Górna połowa „+”: zdjęcie z przodu; dolna połowa: kamera swobodna.
- Każdy chip ciała pokazuje tylko swoje presety. „...” zwija presety.
- Kliknięcie wczytuje preset; prawy przycisk: zastosuj, zmień nazwę, aktualizuj, przesuń, usuń, szybkie menu.
- Z szybkiego menu preset najpierw przełącza na swoje ciało.

### Udostępnianie
- Prawy przycisk na presecie → „Eksportuj (udostępnij)…”, „Importuj…” w prawym dolnym rogu – jak przy lookach.
- Preset trafia do swojego body, nawet gdy tego body tu brak; pojawi się, gdy body zostanie przekonwertowane.

## Twarz {#face}

Mimika Jodi.

### Miny
- Suwaki dla min z gry (zrelaksowana, skupiona, uśmiech, ból, przestrach, zmęczona, cierpienie), spojrzenia i kształtów ust.
- Miny są mieszane (razem najwyżej 100 %) albo sumowane.
- Zaznaczony wpis zachowuje swoją wartość, także w pozach; niezaznaczony ustala animacja gry.
- „Ustal wszystkie” i „Wszystko grze” przełączają wszystkie naraz.

### Zamknięte oczy
- „Zamknięte oczy” (w Spojrzenie) zamyka oczy, od otwartych do całkiem zamkniętych; mruganie gry działa dalej jak zwykle.
- Tylko na przekonwertowanych ciałach, jak suwaki ciała. Na każdym innym ciele te wiersze są wyszarzone; podpowiedź wyjaśnia dlaczego.
- „Lewe oko zamknięte” i „Prawe oko zamknięte” zamykają jedno oko (lewe / prawe Jodi), np. do mrugnięcia.
- Każde oko zamyka się tak, jak większa z wartości jego wiersza i „Zamknięte oczy”.

### Zapisane twarze
- Kafelek „+” zapisuje aktualną twarz ze zdjęciem.
- Prawy przycisk: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń.
- Udostępnianie: prawy przycisk na twarzy → „Eksportuj (udostępnij)…”, „Importuj…” w prawym dolnym rogu – jak przy lookach.

## Mody {#mods}

Ustawienia innych modów, które rejestrują się w AltUI: po lewej ich wpisy, po prawej przełączniki, suwaki, liczby, wybory, kolory, pola tekstowe, klawisze i przyciski wybranego. Ta karta pojawia się tylko wtedy, gdy taki mod jest zainstalowany.

### Karty i sekcje
- Mod może podzielić swoją stronę na karty: wyglądają jak karty na samej górze i stoją nad polami.
- To, co stoi przed pierwszą kartą, jest widoczne na każdej karcie.
- Pola karty i każdej sekcji leżą na własnej jasnej powierzchni, więc widać, co do siebie należy.
- Nagłówek ze strzałką po kliknięciu zwija i rozwija pola pod nim.
- AltUI zapamiętuje wybraną kartę każdej strony i zwinięte sekcje.

### Presety
- Nad polami: presety strony. Kafelek „+” zapisuje obecne ustawienia ze zdjęciem (z przodu lub wolną kamerą); kliknięcie stosuje preset.
- Presety zawsze obejmują całą stronę, niezależnie od pokazanej karty.
- Prawy klik: zastosuj, pokaż zawartość, zmień nazwę, aktualizuj, przesuń, usuń, menu szybkie.
- „Pokaż zawartość” wypisuje wartości, każdą z polem wyboru: stosowane są tylko zaznaczone, niezaznaczone pozostają zapisane.
- Zakładki i nagłówki strony stoją tam również nad swoimi wartościami, więc pola o tej samej nazwie da się rozróżnić.
- Zapisywane osobno dla każdego moda w AltUI_ModPresets_<mod>.sav.
- „...” na pasku nad kafelkami zwija obszar presetów na wszystkich stronach modów i rozwija go ponownie.

### Presety dostarczone przez mod
- Są na początku.
- Można je stosować, zmieniać ich nazwę, dodać własne zdjęcie („Nowe zdjęcie”) i zaznaczać ich wartości, ale nie edytować ani usuwać.
- Można je ukryć (prawy klik „Ukryj”); „Pokaż ukryte presety” na pasku nad kafelkami przywraca te z tej strony.

### Udostępnianie
- Prawy przycisk na własnym presecie → „Eksportuj (udostępnij)…”, „Importuj…” w prawym dolnym rogu – jak przy lookach.
- Dołączone presety przynosi sam mod.
- Zaimportowany preset trafia na stronę swojego moda, nawet gdy mod nie jest zainstalowany; pojawi się, gdy będzie.

## Opcje {#options}

Po lewej kategorie. Co zawiera każda z nich:

### Ogólne
- Język i ile ekranu zostaje wolne dla Jodi.
- Czy można zdjąć bieliznę; jak wyglądają elementy, których nie masz.
- Przełącznik Kodeksu dla encyklopedii.
- Katalog „Wszystkie przedmioty” i „Automatycznie wyposażaj broń” dla karty Ekwipunek.
- „Bez powiadomień” ukrywa wszystkie powiadomienia na dole, z AltUI i z samej gry.
- „Ubrania podążają za kształtem ciała” (domyślnie wyłączone, tylko przekonwertowane ciała): falujący materiał, jak spódnice i płaszcze, trzyma się bliżej przy większych suwakach biustu, bioder, pośladków, ud i talii, zamiast wpadać w ciało; im większy kształt, tym mniej faluje.

### Kafelki
- Rozmiar kafelków, osobne rozmiary dla kafelków strojów, stylizacji i ragdolli.
- Elementy na kafelku stroju, bez limitu dla długich list.
- Dane w podpowiedziach.
- Rozmiar kafelków karty Ekwipunek.

### Grupy
- Łączenie grup lub modów o tej samej nazwie.
- Długość nazw grup, wysokość obszaru chipów, wyszukiwanie chipów.

### Kamera
- Pole widzenia, odległość, wysokość, kamera podąża za wybranym slotem.
- Dwa przełączniki wolnej kamery (także w trybie ragdolli): bez kolizji – przelatuje przez ściany i Jodi – oraz dowolnie daleko od Jodi.

### Sterowanie
- Klawisz panelu, prędkość przewijania, wysokość kamery prawym przyciskiem myszy.
- Jak wysoko kółko myszy podnosi ragdolla na jeden ząbek.

### Ruch
Własna prędkość chodu i biegu Jodi (od 50 do 200 %); kucanie i skakanie pozostają bez zmian. „Przywróć domyślne” przywraca prędkość chodu, biegu i zwolnienia.

- „Skakanie w biurze” (domyślnie wyłączone) pozwala Jodi skakać i wspinać się w jej biurze, gdzie gra blokuje obie czynności; menu Esc pauzuje wtedy grę także tam, jak na poziomach.
- „Zwolnienie wł.” włącza zwolnienie, „Tempo zwolnienia” (od 5 do 90 %, domyślnie 25 %) ustala, jak wolno płynie czas. Pozycja szybkiego menu „Zwolnienie wł / wył” działa tak samo jak przełącznik.

Stopy na podłożu (domyślnie wyłączone, tylko na przekonwertowanych ciałach):
- „Stopy podążają za podłożem”: stopy stoją na stopniach i zboczach, gdy Jodi stoi w miejscu.
- „Kolana i dłonie podążają za podłożem”: kolana i dłonie leżą na podłodze w pozach przy ziemi.
- Wskazówka: pierwszy zostaw włączony, drugi włącz do póz. IK stóp autorstwa BenenG47.

Stanie, styl chodu i biegu:
- „Stanie” wybiera animację bezczynności Jodi: animacje gry (rozglądanie się, oglądanie paznokci, oglądanie nogi, ostrożnie, ranna, pozowanie) i zainstalowanych modów bezczynności (IdleAltUI_…).
- Mody chodu/biegu (WalkAltUI_…) dodają wybory do „Styl chodu” i „Styl biegu”; te wiersze pokazują się tylko, gdy jest wybór.
- Mod chodu wygrywa z wybranym jednocześnie modem biegu lub bezczynności: ta strona działa zwykle, a pod jej wierszem jest o tym informacja.

### Motyw
- Każdy kolor panelu i jego krycie.
- Obraz tła (wypełnienie, wyrównanie, odcień, sepia, odwrócenie, własne krycie) i obraz dla kafelków i kart.
- Schematy kolorów zapisane pod nazwą; zapisany motyw zachowuje także obrazy i ich ustawienia. Reset jest na pasku stanu.
- Własne obrazy: Background_1 … Background_30 i Button_1 … Button_30 (.png, .jpg lub .jpeg) w folderze podanym na stronie.
- „Pokaż podglądy” pokazuje same obrazy na ich chipach. Prawy klik na podglądzie własnego obrazu: „Utwórz podgląd ponownie”.

### Konflikty slotów
- Rozdzielenie par slotów gry (na przykład biustonosz i koszula), aby można było nosić oba elementy.
- „Kilka rzeczy w jednym slocie”: włączony slot zachowuje swoje rzeczy, gdy zakłada się kolejną (na przykład podkolanówki na rajstopy), dla Jodi, towarzyszy i wyglądów.

### Karty
- Tekst, ikony lub oba na pasku kart; wyłączanie kart.
- Kliknięcie karty na pasku prawym przyciskiem ją przenosi; „Kolejność kart” przywraca domyślną kolejność.
- „Spróbuj w jednym wierszu”: podpisy najpierw się zmniejszają, potem skracają, aby pasek mieścił się w jednym wierszu, gdzie to możliwe.

## Zarządzanie {#manage}

Nazwy wyświetlane, używane mody i udostępnianie wielu rzeczy naraz.

### Nazwy
Własne nazwy wyświetlane dla modów, grup, ubrań, fryzur, skór, makijażu, póz i presetów wyglądu.
- Nazwy są używane w całym panelu i znajdowane przez wyszukiwanie; oryginalny identyfikator nadal można wyszukać i widać go w podpowiedzi.
- Chipy i wyszukiwanie filtrują listę; „tylko mody” ukrywa wpisy gry; ↺ przywraca nazwę domyślną.
- Mody broni są na liście razem z innymi modami.
- Za pomocą altui_names.pyz nazwy można wyeksportować do pliku tekstowego i zaimportować z powrotem.
- „Wczytaj mody ponownie” (obok wyszukiwania) ponownie ustala, z którego moda pochodzi każda część. AltUI pamięta to między uruchomieniami gry i sam zauważa zmienione mody; link jest na wypadek, gdyby tego nie zrobił.

### Użycie
„Użycie” pokazuje, które mody są teraz używane.
- Dla każdego moda: używane elementy i miejsca, w których są (Jodi teraz, stroje, stylizacje, presety, ulubione, towarzysze, sceny ragdolli, stanie, broń, sceny i pozycje obiektów, szuflady z ubraniami).
- Sceny obiektów i zapisane pozycje obiektów też liczą się jako użycie (modele z modów).
- To, co leży tylko w szafie, nie liczy się jako użycie.
- Nieużywane mody są niżej na szaro, tak samo mody, których użycia AltUI nie potrafi ustalić (mapy, mody skryptowe). „Pokaż zawartość” otwiera każdy z nich.
- Każdy mod to kafelek z nazwą wyświetlaną i plikiem pak; miejsca elementu są zebrane według rodzaju (np. „Stroje 4–6, 8”).
- Lista jest zbierana przy otwarciu „Użycie”; gdzie indziej liczba po lewej jest z ostatniego razu (przed pierwszym razem brak).

### Udostępnianie
„Udostępnianie” pokazuje wszystkie looki, stroje, twarze, presety wyglądu, ciała i własne presety modów na jednej stronie.
- Pogrupowane według rodzaju („wszystkie” / „żadne” dla każdego), z body lub modem obok.
- Zaznacz je, a „Eksportuj (n)…” w prawym dolnym rogu poda zaznaczone jako jeden tekst; „Importuj…” obok czyta taki tekst.
- Zaznaczenia obowiązują tylko, dopóki strona jest otwarta.
- Presety modów, które nie są teraz zainstalowane, nie są na liście.

## Ragdolle {#ragdolls}

Figury z fizyką do ustawiania i pozowania na poziomie: kopie Jodi, zombie i ludzie.

### Tworzenie figur
- „+ Utwórz kopię Jodi” stawia kopię przed nią, stojącą i zamrożoną w jej obecnej pozie, ze wszystkim, co ma na sobie.
- Stylizacja staje się figurą przez „Utwórz jako ragdoll” w jej menu kontekstowym.
- „Zombie i ludzie”: jeden kafelek z obrazem na rodzaj zombie, do tego pielęgniarka i ocalała. Kliknięcie tworzy figurę; linki pod kafelkiem tworzą jej warianty.
- Najemnik też jest rodzajem figury; trzyma karabin w rękach.

### Wiersze figur
- Każda figura ma swój wiersz: aktywna (fizyka, upada i można nią rzucać) lub zamrożona (trzyma pozę), „stawy ›”, zablokuj wszystkie, zwolnij wszystkie, usuń.
- Na dole po prawej, na pasku stanu: „Usuń wszystkie” (usuwa każdą figurę) i „Kule stawów: wł./wył.”.

### Stawy
- „stawy ›” rozwija 17 stawów figury, każdy z dwoma przełącznikami: zablokowany/wolny i ruchomy/nieruchomy.
- Zablokowany staw pozostaje sztywny, dopóki figura jest aktywna; ruchomy można ustawiać na zamrożonej figurze.
- Kule stawów pokazują, gdzie można chwycić: szare, czerwone = zablokowany, zielone = ruchomy, niebieskie = przypięty.
- Zasłonięte prześwitują blado przez ciało; kliknięcie kuli chwyta dokładnie ten staw.
- Pojawiają się tylko na tej karcie i w trybie ragdoll.

### Pozy i sceny
- Pozy (w rozwiniętym wierszu): nazwa i „zapisz pozę” zapamiętują ułożenie części ciała oraz to, które stawy są zablokowane lub ruchome.
- Pozę można wczytać na każdą figurę tego samego rodzaju, na każdym poziomie – kliknięcie wczytuje, prawy przycisk: wczytaj / usuń. Figura przy tym zamarza i staje na podłodze.
- Sceny: „Zapisz scenę jako” zapamiętuje każdą figurę poziomu z wyglądem, miejscem, pozą i stawami; ta sama nazwa na tym samym poziomie nadpisuje scenę.
- Widać tylko sceny bieżącego poziomu. Kliknięcie wczytuje scenę i zastępuje obecne figury; prawy przycisk: wczytaj / usuń.

### Atakowalne ragdolle
- „Ustaw jako atakowalną” (kopie Jodi, NPC i najemnika): zombie atakują ragdolla jak figurę; w nagłówku pojawia się wtedy „· atakowalna”.
- Każde uderzenie popycha część ciała najbliższą zombie; zamrożony ragdoll wraca do swojej pozy około sekundy po ostatnim uderzeniu.
- Ragdolle nie giną. Stan zapisuje się ze sceną.

### Mysz na figurze
Obok panelu i w trybie ragdolli:
- Przeciąganie lewym przyciskiem zamrożonej figury przesuwa ją po podłodze; kółko myszy podnosi ją lub opuszcza podczas przeciągania.
- Przeciąganie lewym przyciskiem aktywnej figury chwyta część ciała pod myszą; puść, a figura upadnie. Kółko myszy podnosi lub opuszcza wtedy chwycony punkt.
- Prawy przycisk podczas przeciągania przypina część w tym miejscu; reszta figury na niej wisi. Chwyć ją ponownie, a będzie wolna. „puść wszystkie” w wierszu figury zwalnia wszystkie.
- Przeciąganie prawym przyciskiem obraca figurę wokół bioder.

### Pozowanie myszą
- Shift + lewy przycisk blokuje lub zwalnia kliknięty staw.
- Shift + prawy przycisk na zamrożonej figurze czyni staw ruchomym.
- Przeciąganie wtedy lewym przyciskiem części ciała poniżej ruchomego stawu porusza tylko tę część; zostaje tam, gdzie ją puścisz – tak pozuje się figurę.
- Przeciąganie prawym przyciskiem części ciała pod ruchomym stawem zamrożonej figury obraca tę kończynę wokół stawu: chwycony punkt podąża za myszą, dłoń i palce obracają się razem z nią.
- Kółko myszy skręca przy tym kończynę wokół jej własnej osi.
- Obrót zostaje w pozie i zapisuje się z pozami i scenami; ograniczenia stawów działają dopiero, gdy figura stanie się aktywna.

### Palce i oczy
Zamrożone postacie z ciałem Jodi:
- Z bliska (poniżej ok. 1 m) na paliczkach i powiekach pojawiają się małe kule.
- Przeciągnięcie prawym przyciskiem kuli palca obraca ten paliczek, kółko go skręca; przeciągnięcie lewym zgina cały palec (czubek w stronę nasady).
- Przeciągnięcie lewym kuli powieki kieruje wzrok obu oczu; kółko otwiera i zamyka przy tym powieki (z Shift przy chwytaniu: tylko tę powiekę).
- W rozwiniętej postaci „Lewa dłoń” i „Prawa dłoń” ustawiają gotowe pozy dłoni (otwarta, rozluźniona, pięść, kciuk w górę, pokój, wskaż, trzymaj, poza bazowa).
- „Oczy: resetuj” otwiera powieki i kieruje wzrok prosto.
- Pozy i sceny zapisują palce, powieki i wzrok.

### Szybkie menu
Bez panelu figury aktywuje lub zamraża szybkie menu:
- „Ragdoll: aktywuj / zamroź tę na środku” bierze figurę na środku ekranu.
- „Ragdolle: aktywne / zamrożone” przełącza wszystkie.

## Tryb ragdolli {#ragmode}

Przesuwanie i pozowanie figur bez panelu, z kamerą poruszającą się swobodnie po pomieszczeniu.

### Start i koniec
- Uruchamia go trzeci okrągły przycisk nad + i − albo szybkie menu.
- Esc lub B kończy tryb.

### Kamera
- W A S D i Q E przesuwają kamerę, Shift szybciej; Shift + kółko ustawia prędkość.
- Przeciąganie w pustym miejscu obraca kamerę.
- Przytrzymanie środkowego przycisku myszy obraca kamerę bez zatrzymywania na krawędziach ekranu; potem wskaźnik wraca na swoje miejsce.

### Figury
- Kursor myszy pozostaje widoczny; na figurze wszystko działa jak obok panelu (zob. „Ragdolle”).

## Wrogowie {#enemies}

Żywe, wrogie zombie każdego rodzaju.

### Przywoływanie
- Kafelek przywołuje swój rodzaj, linki pod nim jego warianty.
- Pojawiają się w kierunku kamery w ustawionej odległości, tyle, ile mówi „Liczba”, rozmieszczone wokół tego punktu.

### Zachowanie
- *Polowanie* – od razu idą na Jodi.
- *Czatowanie* – czekają, aż kogoś zobaczą lub usłyszą (także towarzyszy).
- *Bierny* – stoją w miejscu i nic ich nie budzi.
- Zmiana dotyczy wszystkich wrogów przywołanych przez AltUI.

### Usuwanie
- *Usuń wszystkich* / *Usuń najbliższego* zabierają ich (bez łupu, bez EXP).
- *Zabij wszystkich* pozwala im zginąć jak w grze – ciała zostają do *Usuń wszystkich*.

### Widoki „Przywołaj” i „Żywi”
- Dwa widoki: „Przywołaj” (powyżej) i „Żywi (n)”.
- „Żywych: n” liczy żywych wrogów przywołanych przez AltUI; zombie gry nigdy nie są ruszane.
- „Żywi (n)”: wiersz na wroga – postacie ze stylizacji (ze wszystkim, co oferuje zakładka Towarzysze), a pod nimi każdy zombie przywołany przez AltUI z rodzajem, odległością i zachowaniem.
- Linki dla każdego zombie: poluj, czaj się, pasywny, usuń, zabij.

### Dobrze wiedzieć
- Gra zapisuje żywych wrogów razem ze stanem gry: po wczytaniu są zombie gry. Usuń lub zabij ich przed zapisem.
- W wyzwaniu żywi wrogowie nie pozwalają wygrać (gra liczy każdego żywego zombie). Przerywniki ich usuwają.
- Tam, gdzie nie ma ścieżek (biuro Jodi, poziom 3, strzelnica), idą tylko prosto do celu, który widzą.

### Szybkie menu
- „Przywołaj: <rodzaj>” dla każdego rodzaju i wariantu (z aktualną liczbą, odległością i zachowaniem).
- „Wrogowie: usuń wszystkich / zabij wszystkich / bierni / aktywni”.
- Oba w zakładce Akcje, także na własnych klawiszach.

## Nawigacja {#navigation}

Latanie oraz łóżka bieżącego poziomu, do których można się teleportować.

### Leć / Wyląduj
- Leć: Jodi lata. Ruch jak zwykle, Spacja w górę, Ctrl w dół, Shift trzy razy szybciej; suwak ustawia tempo. Ściany ją zatrzymują.
- Wyląduj pozwala jej spaść na ziemię – upadek z wysoka rani jak w grze.
- Także w szybkim menu, więc także pod własnym klawiszem (Akcje › Własne klawisze).

### Łóżka i teleport
- Pokazuje łóżka bieżącego poziomu, na których Jodi może zapisać grę, najbliższe najpierw, z nazwą pomieszczenia i odległością.
- „Teleportuj” stawia Jodi obok tego łóżka, przodem do niego; zapis jak zwykle przez użycie łóżka.
- Podążający za nią towarzysze idą z nią, czekający zostają.
- Teleport pomija wszystko po drodze: kroki fabuły, które gra uruchamia, gdy Jodi przechodzi przez obszar, nie dzieją się po drodze, dopiero gdy później do niego wejdzie.
- Biuro Jodi, poziom 3 i strzelnica nie mają takich łóżek.

## Obiekty {#objects}

Umieszczanie w świecie modeli z gry, broni i modeli z modów (np. rekwizytów z modów póz), przesuwanie ich i zapisywanie jako scena.

### Katalog
- Po lewej KATALOG: Wszystkie, ★ Ulubione, foldery gry, „Z poziomu: …”, Broń i Mody (+ rozwija poszczególne mody).
- Po prawej wyszukiwanie i modele jako kafelki, posortowane po nazwie; „Pokaż więcej” wczytuje kolejne. Obrazki tylko z zaznaczonym „Wczytuj” (na początku wyłączone): wtedy AltUI robi je sam i zapamiętuje; bez zaznaczenia żaden obrazek nie jest wczytywany ani robiony.
- Kliknięcie kafelka stawia model na podłodze przed Jodi, nieruchomo. Prawy przycisk: ulubione, „Pojaw z fizyką”.

### Modele z modów
- Modele z modów AltUI znajduje, przeszukując mody raz, folder po folderze (licznik jest u góry), i zapamiętuje wynik; potem przeszukuje tylko nowe mody.
- „Przeszukaj mody ponownie” zaczyna od nowa.
- Niektóre mody trzymają modele w folderach o innej nazwie niż ich pak; znajduje je „Przeszukaj wszystkie foldery modów” (gra zatrzymuje się na około pół minuty).

### Wybrany obiekt
- Na dole blok „Wybrany”: obrazek, nazwa, nieruchomy lub z fizyką, odznacz, fizyka wł./wył., na podłogę, kopiuj, usuń.
- Pola pozycji, obrotu (odchylenie, pochylenie, przechył) i rozmiaru – Enter zatwierdza.
- Wybrany obiekt ma żółtą ramkę.

### W świecie
- ŚWIAT › W świecie: wiersz dla każdego obiektu z wyborem (przy wybranym: odznacz), fizyką wł./wył., kopiowaniem, usuwaniem.
- „Pozycje” rozwija blok: nazwa i „Zapisz pozycję” zapamiętują miejsce, obrót, rozmiar i fizykę.
- Pozycja pojawia się przy każdym obiekcie tego samego modelu na tym samym poziomie – kliknięcie go tam ustawia, prawy przycisk: zastosuj / usuń.

### Sceny
- ŚWIAT › Sceny: nazwa i „Zapisz scenę” zapamiętują wszystkie obiekty poziomu; ta sama nazwa na tym samym poziomie nadpisuje.
- Widać tylko sceny bieżącego poziomu. Kliknięcie wczytuje scenę i zastępuje obiekty; prawy przycisk: wczytaj / usuń.
- Brakujący model (mod nie zainstalowany) jest pomijany i zgłaszany.
- Obiekty znikają razem z poziomem; scena je przywraca.

### Mysz na obiekcie
Obok panelu i w trybie ragdolli:
- Kliknięcie go wybiera.
- Przeciąganie lewym przesuwa nieruchomy obiekt na jego wysokości; obiekt z fizyką zostaje chwycony, puszczenie go rzuca.
- Przeciąganie prawym obraca go wokół osi pionowej, Shift + przeciąganie prawym obraca swobodnie. Obiekt z fizyką stoi wtedy w miejscu, a potem znów spada.
- Kółko podczas przeciągania podnosi go lub opuszcza (także chwycony z fizyką); Ctrl + kółko zmienia jego rozmiar.

## Towarzysze {#followers}

Stylizacje jako postacie w grze: towarzysz idzie z Jodi, walczy i słucha rozkazów; NPC zostaje na miejscu i się broni.

### Tworzenie postaci
- W zakładce Stylizacje prawy klik na stylizację: „Utwórz jako towarzysza”, „Utwórz jako NPC” albo „Utwórz jako wroga”. Postać pojawia się przed Jodi w tej stylizacji.
- Każda postać nosi makijaż swojej stylizacji i ma jeden z głosów NPC z gry.
- Postać utworzona w AltUI przed 2.2.0 pokazuje makijaż Jodi, dopóki „Zmień stylizację…” nie da jej własnego.

### Wrogowie ze stylizacji
- Wróg poluje na Jodi z pistoletem (nieskończona amunicja) i ją rani. Twoi towarzysze z nim walczą.
- Jego wiersz jest w zakładce Wrogowie w widoku „Żywi”, ze wszystkim, co oferuje zakładka Towarzysze (tylko na swoim poziomie) – tam go usuń albo zrób z niego towarzysza.

### Jason
- „+ Jason” (na dole po prawej w zakładce) dodaje Jasona z fabuły jako towarzysza, z jego Glockiem. Słucha poleceń, idzie z Jodi i jest zapisywany.
- Walczy tylko własnym Glockiem: Glock, który mu dasz, staje się jego, innej broni nie przyjmuje.
- Nie ma stylizacji, ubrań ani makijażu; gdy leży, nie da się go uleczyć – „Ożyw” przywraca go.

### Lista
- Zakładka „Towarzysze” pokazuje wszystkie postacie ze stanem (podąża, czeka, NPC, nieaktywny, poległ) i przyciskami.
- Towarzysze są nad NPC, linia oddziela obie grupy. Przyciski nad wierszami pokazują wszystkich, tylko towarzyszy albo tylko NPC (zostaje po ponownym uruchomieniu).
- „...” zwija i rozwija kafelki postaci (ubrania i plecak); zostaje tak dla każdej postaci, także po ponownym uruchomieniu.
- Kliknięcie wiersza wybiera postać.

### Przyciski
- „Za mną”, „Czekaj tutaj”, „Przywołaj”, → NPC / → Towarzysz.
- Wyłączenie „Aktywny” zabiera postać ze świata razem z tym, co niesie; po włączeniu wraca przed Jodi.
- ∞ z sercem, „Nieśmiertelny”: postać nie może zginąć, jej zdrowie odnawia się po każdym trafieniu. Mimo to reaguje na trafienia, a jej ubrania się niszczą.
- ∞ z nabojami, „Amunicja bez końca”: postać przeładowuje broń palną bez końca i nie potrzebuje amunicji w torbie. Broń z magazynkiem nie rusza jej amunicji; strzelba i granatnik najpierw zużywają to, co ma przy sobie.

### Menu zębatki
- Zębatka: atakowalna / nieatakowalna, zmień nazwę, zmień stylizację, ożyw, usuń.
- „Atakowalna”: zombie biorą na cel tylko atakowalne postacie, nieśmiertelne czy nie. Po „Ustaw jako nieatakowalną” zombie i najemnicy nie biorą postaci na cel; obrażenia nadal otrzymuje (bez obrażeń z „Nieśmiertelna”). Ustawienie jest zapisywane; nowe postacie są atakowalne.
- „Zmień stylizację” przechodzi do zakładki Stylizacje: kliknij stylizację, którą postać ma nosić.
- Postać, która nie jest nieśmiertelna, może polec. Zostaje na liście, a „Ożyw” przywraca ją z jej rzeczami. Postacie nigdy nie zmieniają się w zombie.
- „Usuń” pyta o potwierdzenie; przedmioty i broń postaci trafiają do skrzyni, a ubrania do plecaka Jodi.

### Przedmioty
- Na górze są plecak (po lewej) i skrzynia (po prawej): kliknięcie daje przedmiot wybranej postaci, broń razem z malowaniem i akcesoriami.
- Kliknięcie kafelka postaci oddaje go do plecaka; prawy klik: wszystko albo do skrzyni.
- „...” nad listą zwija ją.
- Menu kontekstowe stosu – Jodi lub postaci – ma wiersz ilości jak w karcie Ekwipunek: „Daj 5”, „Weź 5”, do skrzyni.

### Ubrania
- Ubrania to prawdziwe rzeczy postaci, jak u NPC w grze: niszczą się, mogą zostać zerwane i widać je w ekwipunku NPC samej gry, gdzie można je też wymieniać.
- Pod postacią jej rzeczy są kafelkami (uszkodzone mają znacznik): kliknięcie zdejmuje rzecz i wkłada ją do plecaka Jodi.
- Prawy klik: napraw zestawem do szycia z plecaka Jodi albo napraw wszystko.
- W kolumnie plecaka „Ubrania” pokazuje rzeczy Jodi: kliknięcie daje jedną wybranej postaci, która ją zakłada (uszkodzenia i kolory idą razem z nią).
- Menu zębatki „Przywróć strój (bez zestawu do szycia)”: postać znów nosi dokładnie strój swojej stylizacji, każda część jak nowa, za darmo – utracone części (zerwane, zabrane) wracają, inne trafiają do jej plecaka (towarzysze, NPC i wrogowie).
- „Przywróć wszystkie stroje” w prawym dolnym rogu zakładki Towarzysze robi to dla każdej postaci tej zakładki.

### Zapis i poziomy
- AltUI przechowuje postacie we własnym zapisie (AltUI_Followers.sav); zapis gry nigdy ich nie zawiera.
- Podążający towarzysze przechodzą z Jodi do każdego poziomu i są po wczytaniu.
- Czekający towarzysze i NPC zostają w swoim poziomie na swoim miejscu.

### Szybkie menu
- „Towarzysz: za mną / czekaj tutaj” dotyczy towarzysza w polu widzenia, „Wszyscy towarzysze: za mną / czekać” – wszystkich.
- „Wszyscy towarzysze: do mnie” sprowadza każdego aktywnego towarzysza na miejsca przed Jodi – także tego, który czeka na innym poziomie.

### Postać w pozie
- Grupa szybkiego menu „Postać: ulubione pozy” zawiera każdą z twoich ulubionych póz jako „Postać: <poza>”.
- Wpis ustawia postać towarzysza lub NPC w polu widzenia w tej pozie (nie Jasona).
- Postać wtedy nie chodzi ani nie walczy, utrzymuje pozę także po trafieniach i się nie odwraca.
- Jeśli jest atakowalna, zombie ją atakują, a postać bez nieśmiertelności może zginąć – tak można ustawiać sceny.
- „Postać: zakończ pozę” każe jej wstać; potem podąża lub czeka jak wcześniej. Zmiana poziomu kończy pozę.

## Kodeks {#kodex}

Trzy strony:

- Encyklopedia: wpisy z archiwum na komputerze w biurze Jodi, z obrazem i tekstem. Pokazywane są tylko te odblokowane w grze – albo wszystkie po włączeniu przełącznika w Opcje › Ogólne.
- Hasła: zamki szyfrowe bieżącego poziomu, najbliższy pierwszy, z odległością i informacją, czy są zamknięte. Każdy kod pozostaje ukryty, dopóki go nie klikniesz.
- Podręcznik AltUI: ten tekst.

## TV {#tv}

Telewizor bieżącego poziomu, sterowany z panelu.

### Kiedy jest widoczna
- Widoczna tylko wtedy, gdy na bieżącym poziomie jest telewizor (biuro Jodi), albo zawsze – z przełącznikiem w Opcje › Ogólne.
- Przy kilku telewizorach sterowany jest ten najbliżej Jodi.

### Odtwarzanie
- Włącz / Wyłącz działają jak klawisz E przy telewizorze.
- Listę filmów telewizor odczytuje przy pierwszym włączeniu – do tego czasu karta prosi, aby włączyć go raz.
- „Odtwórz” obok filmu odtwarza go; odtwarzany film jest wyróżniony.
- Film już rozpoczęty jest kontynuowany od miejsca, w którym został przerwany, tak jak na samym telewizorze.

### Własne filmy
- Włóż pliki .mp4 do folderu gry TheKillingAntidote/Videos/TV/.
- Pojawią się po ponownym wczytaniu poziomu.

## Szybkie menu {#quick}

Przytrzymaj 4 (inny klawisz w Akcje), a wokół myszy otworzy się koło. Puść nad wpisem, aby go wykonać; puść na środku, aby nic nie robić.

### Wpisy
- Stroje, stylizacje, twarze, presety wyglądu, pozy, karty i ustawienia innych modów.
- Akcje: swobodna kamera, tryb fotograficzny, tryb ragdolli, kopia Jodi jako ragdoll, przełączanie wszystkich ragdolli między aktywnymi a zamrożonymi, aktywuj / zamroź tę na środku, usuń wszystkie ragdolle, własna prędkość wł. / wył.
- „Zwolnienie wł / wył”.
- „Zatrzymaj czas / dalej”: wszystko staje; panel i kamery działają dalej, także kamera trybu fotograficznego gry.
- „Ukryj / pokaż Jodi” (z ubraniem, włosami i bronią; w następnym poziomie znów jest widoczna).
- „Ukryj / pokaż interfejs gry” wyłącza i włącza HUD gry, tak jak jej tryb fotograficzny.
- „+1 Niewidzialna ręka” wkłada jedną Niewidzialną rękę do plecaka (zob. Ekwipunek › Wszystkie przedmioty).
- Rozkazy dla towarzyszy (zobacz „Towarzysze”).

### Wysokość kamery
- „Wysokość kamery (kółko)”: na środku ekranu pojawiają się dwie strzałki, a kółko myszy podnosi lub opuszcza kamerę zamiast ją przybliżać lub oddalać.
- Kliknięcie lewym przyciskiem lub Esc kończy ten tryb. Wysokość jest zapamiętywana.

### Karta Akcje
- Wpisy dodaje się w Akcje albo prawym przyciskiem na kafelku, karcie lub wpisie moda („Dodaj do szybkiego menu”).
- Po lewej „W kole” (klawisz, przezroczystość, kolejność przez ↑ ↓ ✕), „Własne klawisze”, potem „Wszystkie” i każda grupa z wpisami – stroje, looki, twarze, presety, pozy, karty, wpisy modów – oraz jeden wiersz na każdy mod z akcjami.
- Po prawej wpisy tej grupy z polem wyboru (w kole lub nie) i wyszukiwarka nad nimi. Każda grupa pamięta swoją pozycję przewijania.
- Kolejność w kole to kolejność listy w Akcje › W kole.

### Własne klawisze
- W Akcje kliknij prawym przyciskiem pozycję w „Dostępne” i naciśnij klawisz – pozycja działa wtedy pod tym klawiszem, przy zamkniętym panelu, także w swobodnej kamerze i w trybie fotograficznym gry.
- Kliknięcie klawisza w wierszu przypisuje inny, ✕ go usuwa.
- Klawisz panelu, klawisz szybkiego menu i klawisz już przypisany są odrzucane; klawisz używany przez grę uruchamia oba działania.

## Dla autorów modów {#modding}

Jak inne mody współpracują z AltUI.

### Mody ubrań, ciała i broni
- Mody z ubraniami nie potrzebują niczego szczególnego: AltUI czyta tabele gry i przypisuje każdy element do jego slotu.
- Mody zastępujące ciało lub broń można przekonwertować za pomocą bodypak.pyz i weaponpak.pyz, aby kilka mogło być zainstalowanych obok siebie.
- Można je też zbudować dla AltUI bezpośrednio w Unreal Editorze.

### Mody bezczynności
- Pak zastępujący animację bezczynności Jodi można przekonwertować za pomocą idlepak.pyz: python3 idlepak.pyz <mod>.pak.
- Nowy IdleAltUI_….pak trafia do Mods/ i pojawia się w Opcje › Ruch › „Stanie”; własna animacja gry zostaje.
- AltUI musi być zainstalowany: konwerter buduje nowy pak częściowo z AltUI.pak i szuka go w zwykłych folderach Steam. Jeśli leży gdzie indziej, podaj ścieżkę przez --altui <ścieżka do AltUI.pak>.

### Mody chodu i biegu
- Pak zastępujący animację chodu lub biegu Jodi można przekształcić za pomocą walkpak.pyz: python3 walkpak.pyz <mod>.pak.
- Nowy WalkAltUI_….pak trafia do Mods/ i pojawia się w Opcje › Ruch › „Styl chodu” (oraz „Styl biegu”, jeśli zawiera bieg); własny chód gry zostaje.
- walkpak odrzuca animację bez krzywych ruchu gry (MoveData_Speed, Rotation Speed) i podaje brakującą.
- Tak jak idlepak potrzebuje AltUI.pak (--altui <ścieżka>, jeśli nie leży w zwykłych folderach Steam).

### Ustawienia w karcie Mody
- Mody mogą pokazywać swoje ustawienia w karcie Mody przez dwie tabele danych i interfejs; jak to zrobić, opisuje MOD_UI.md w repozytorium kodu źródłowego.
