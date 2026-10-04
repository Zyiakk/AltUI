# AltUI – panneau de garde-robe et d'apparence

Version française de la description de la [page AltUI sur Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988). L'original anglais sur la page Nexus fait foi.

La garde-robe du jeu donne à chaque auteur de mod son propre onglet : avec quelques mods de vêtements, un même type de pièce se retrouve éparpillé sur une douzaine d'onglets, sans aucun moyen de chercher. AltUI range chaque pièce du jeu et de tous les mods installés dans **une liste par emplacement** (hauts, jupes, chaussures, …), avec recherche, filtres, favoris et masquage – et réunit coiffure, maquillage, corps et tenues dans le même panneau. Il s'ouvre n'importe où dans un niveau avec **B** ; plus besoin d'aller à la garde-robe ou au miroir.

Aussi disponible sur le [Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). Le même mod, les mêmes fichiers – choisissez une source, pas les deux.

> ⚠ **Conçu pour la version 0.6.x du jeu.** Une mise à jour du jeu qui modifie les tables de vêtements / de maquillage ou le gestionnaire de caméra peut casser le mod.

## Installation

**AltUI.pak** est le mod tout entier ; un second fichier doit le démarrer. Il y a deux façons de faire – une seule suffit, les deux ensemble fonctionnent aussi. Les chemins sont relatifs à l'installation du jeu, p. ex. *Steam\steamapps\common\TheKillingAntidote\* ; le nom du dossier du jeu y apparaît deux fois, c'est normal.

**1. Avec le Blueprint Loader (AltUI ne remplace rien du jeu)**

1. Récupérez **TKA_BlueprintLoader.pak** sur [Blueprint Loader](https://www.nexusmods.com/thekillingantidote/mods/994) et placez-le dans *TheKillingAntidote\Content\Paks\~mods\* – créez le dossier **~mods** s'il n'existe pas (le nom commence par un tilde).
2. **AltUI.pak** de l'archive ici → *TheKillingAntidote\Mods\*
3. Lancez le jeu, appuyez sur B dans un niveau.

AltUI.pak apporte une table que le loader lit, et le loader démarre le panneau à partir d'elle. Le même loader démarre tout autre mod qui apporte une telle table – c'est donc la voie à suivre si vous en utilisez plusieurs.

**Mise à jour depuis une ancienne version d'AltUI : s'il reste un AltUI_Hook_P.pak dans ~mods, supprimez-le. Le hook s'approprie la classe de la caméra, et un hook antérieur à 1.5.0 ne démarre pas le loader – le panneau s'ouvre alors, mais la vue ne se décale pas, et les mods conçus pour le loader restent inactifs.**

**2. Avec le pak hook (aucun second mod nécessaire)**

1. **AltUI.pak** → *TheKillingAntidote\Mods\*
2. **AltUI_Hook_P.pak** → *TheKillingAntidote\Content\Paks\~mods\* – même règle de dossier que ci-dessus.
3. Lancez le jeu, appuyez sur B dans un niveau.

Le hook remplace l'un des blueprints du jeu (le gestionnaire de caméra du joueur) et démarre le panneau depuis là ; cela ne fonctionne que depuis *~mods*. Tout mod qui remplace le même blueprint entre en conflit avec lui – le Blueprint Loader en fait partie, et cette paire est justement l'exception : si les deux sont installés, le hook prend la classe et démarre lui-même le loader, si bien que les mods qui ont besoin du loader continuent de fonctionner.

**« B ne fait rien »** → rien n'a démarré le panneau : soit le second fichier manque, soit il se trouve dans *Mods* au lieu de *Content\Paks\~mods*.

Le placement de la caméra à côté du panneau ouvert ne dépend plus du hook – il s'accroche au gestionnaire de caméra que le niveau possède de toute façon, y compris celui du jeu.

Désinstallation : supprimez les fichiers copiés. Les fichiers de sauvegarde propres au mod (*Saved\SaveGames\AltUI.sav*, *AltUI_Looks.sav*, *AltUI_Faces.sav*, *AltUI_Names.sav*, les photos de looks et de visages dans *Saved\SaveGames\AltUI\* et les tuiles d'armes dans *Saved\SaveGames\WeaponIcons\*) peuvent aussi être supprimés ; rien d'autre n'est touché – vêtements, tenues, maquillage et coiffure passent par les fichiers de sauvegarde du jeu.

## Ce qu'il fait

* **Vêtements** – chaque pièce connue du jeu et des mods, regroupée par emplacement, des sous-onglets par mod (repliables), recherche, filtres « possédés seulement » / « favoris seulement » / « vanilla seulement », favoris, couleur via la palette du jeu, réinitialisation de la couleur, vers le sac à dos et retour, masquage de pièces.
* **Tenues** – les tenues enregistrées du jeu, avec des noms (clic droit → renommer).
* **Looks** – un look complet (vêtements avec couleurs, coiffure et couleur de cheveux, maquillage, yeux, peau, curseurs du corps, mod de corps, visage), enregistré avec une photo en pied prise en jeu, de face ou tel que vous la voyez. Appliquer, mettre à jour, renommer, supprimer.
* **Sac à dos** – ce que Jodi porte et transporte : porter, enlever, réparer, remettre dans la garde-robe, ranger.
* **Coiffure** – toutes les coiffures, couleur des cheveux, 14 couleurs naturelles, réglage d'origine.
* **Apparence** – peau, chaque type de maquillage, yeux, apparences enregistrées avec icônes (enregistrer, mettre à jour, renommer, supprimer).
* **Morphologie** – curseurs de poitrine / taille, un sélecteur pour les mods de corps installés et – pour les corps convertis – des curseurs d'os : échelle, buste, taille extra, fessiers/hanches, cuisses, mollets, bras, mains, pieds, enregistrés par corps.
* **Visage** – l'expression de Jodi : les expressions du jeu, la direction du regard et les formes de bouche en curseurs ; une entrée cochée garde sa valeur, même en pose et pendant la danse, une entrée non cochée est laissée au jeu. Visages enregistrés avec photo. « Voir le contenu » liste leurs valeurs.
* **Armes** – un modèle et un skin par arme, côte à côte depuis tous les mods d'armes, avec une image rendue sur chaque tuile.
* **Poses** – chaque animation d'action du jeu et des mods de poses, triées en debout, assise et allongée.
* **Mods** – les réglages d'autres mods qui s'y enregistrent (visible seulement quand un tel mod est installé).
* **Menu rapide** – maintenir **4** (modifiable) ouvre une roue avec ce dont vous vous servez souvent : caméra libre, mode photo, une tenue, un look, un visage ou un préréglage enregistré, une pose favorite, un onglet et des actions d'autres mods. Jusqu'à 32 éléments, choisis et ordonnés dans les Paramètres ; relâcher sur un élément le lance. Un clic droit sur une tuile, un onglet ou l'entrée d'un mod l'ajoute à la roue ou l'en retire.
* **Paramètres** – en catégories avec une liste à gauche ; les onglets inutiles peuvent être désactivés ; touche du panneau, langue, vitesse de défilement, taille des tuiles, longueur des noms de groupe et hauteur de la ligne de groupes, part de l'écran laissée à Jodi, FOV / distance / déplacement de la caméra, thème de couleurs et opacité, « les sous-vêtements peuvent être retirés », « non possédés » verrouillés / grisés / comme possédés, lever les conflits d'emplacements du jeu (soutien-gorge contre chemise …), fusionner les groupes / mods de même nom, options des infobulles ; barre d'onglets avec icônes, texte ou les deux, l'icône à gauche ou à droite du texte ; thèmes de couleurs enregistrés sous un nom ; tailles propres pour les tuiles de tenues et de looks et nombre de pièces qu'affiche une tuile de tenue ; opacité du menu rapide.
* **Gestion** – vos propres noms affichés pour les mods, groupes, pièces, coiffures, peaux et maquillages – partout dans le panneau et dans la recherche ; « Renommer… » dans le menu contextuel de chaque tuile ; exportables / importables en JSON avec `altui_names.pyz` ; comme dans Vêtements, des puces filtrent la liste par mod ou par groupe et un champ de recherche réduit les puces ; les poses et les apparences enregistrées se renomment aussi.
* Annuler / rétablir (5 étapes), les infobulles indiquent de quel mod vient une pièce.

Langues : anglais, allemand, chinois, russe, espagnol, polonais, français (détectée automatiquement, modifiable dans les Paramètres).

## Commandes

* **B** – ouvrir / fermer (modifiable dans les Paramètres). **Échap** ferme.
* **4** – maintenir pour le menu rapide (modifiable dans les Paramètres) ; relâcher sur un élément le lance, relâcher au centre ne fait rien.
* Clic gauche – choisir / porter / appliquer. Clic droit – menu contextuel. Molette – défiler.
* Tant que le panneau est ouvert, Jodi ne peut pas marcher ; faire glisser sur le fond fait tourner la caméra, +/− rapproche / éloigne la caméra. Les deux boutons ronds au-dessus ouvrent une caméra libre (la souris oriente, W A S D / Q E déplacent, Maj plus vite, molette = vitesse, jusqu'à 6 m autour de Jodi, s'arrête aux murs ; Échap pour revenir) et le mode photo du jeu (Échap pour revenir).

## Mods de corps

Les paks qui remplacent le corps écrasent tous le même fichier du jeu, donc un seul peut être actif. **bodypak.pyz** (dans l'archive ; Python 3.8+, aucun paquet) transforme un remplaçant en pak de mod ordinaire qui garde le maillage sous son propre chemin ; autant de corps convertis que vous voulez peuvent être installés côte à côte et apparaissent comme puces dans l'onglet Morphologie.

```
python bodypak.pyz SomeBodyReplacer.pak --name BodyAltUI_Some --title SomeBody
```

Copiez le *BodyAltUI_Some.pak* obtenu dans *TheKillingAntidote\Mods\* et retirez le remplaçant d'origine (ou laissez-le dans *~mods* – il devient alors la puce « Standard »).

Guide pas à pas avec un exemple pour Windows et pour Linux (en anglais) : [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md)

## Mods d'armes

Les mods d'armes remplacent, pour chaque arme, les mêmes fichiers du jeu : deux mods pour la même arme s'excluent donc, et on ne peut pas passer de l'un à l'autre en jeu. **weaponpak.pyz** (dans l'archive ; Python 3.8+, aucun paquet) transforme un tel remplaçant en pak de mod à part ; autant que vous voulez peuvent être installés côte à côte, et modèle et skin se choisissent par arme dans l'onglet Armes et sont mémorisés.

```
python weaponpak.pyz SomeWeaponReplacer.pak --name SomeGun --title "Some gun"
```

*--name* fait partie du nom du fichier (lettres, chiffres et _), *--title* est le texte de la puce, et *--weapon* n'est nécessaire que si le nom du dossier du mod ne dit pas pour quelle arme il est. Un pak peut apporter un skin, un modèle ou les deux. Copiez le *WeaponAltUI_SomeGun.pak* obtenu dans *TheKillingAntidote\Mods\* et retirez le remplaçant d'origine – sinon il continue d'écraser l'arme, quel que soit le choix dans le panneau.

Guide pas à pas avec un exemple pour Windows et pour Linux (en anglais) : [WEAPON_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/WEAPON_MODS.md)

## Réglages d'autres mods

Les mods que l'on utilise en jeu – une lampe par exemple – peuvent placer leurs réglages dans AltUI au lieu d'occuper leurs propres touches. Un onglet **Mods** les liste alors, avec interrupteurs, curseurs, nombres, choix, couleurs, champs de texte, lignes d'info, touches et boutons dans le style d'AltUI. L'onglet n'apparaît que si un tel mod est installé. Leurs boutons et interrupteurs peuvent aussi aller dans le menu rapide, et un mod peut apporter ses propres actions avec une image.

Pour les auteurs de mods (en anglais) : [MOD_UI.md](https://github.com/Zyiakk/AltUI/blob/main/MOD_UI.md) décrit les deux tables de données et l'interface dont un mod a besoin ; un mod d'exemple prêt à installer et à reproduire se trouve dans [examples/AltUIMod_Example](https://github.com/Zyiakk/AltUI/tree/main/examples/AltUIMod_Example).

## Compatibilité

Conçu pour la version 0.6.x du jeu. Fonctionne avec les mods de vêtements, de coiffures, de maquillage et de cartes de Nexus et du Workshop – ils apparaissent simplement dans les listes.

## Mises à jour

Une nouvelle version est une nouvelle archive ; copiez simplement AltUI.pak par-dessus l'ancien fichier. Le Blueprint Loader lui-même n'a besoin de rien – c'est un mod à part, mis à jour sur sa propre page. Un ancien AltUI_Hook_P.pak ne doit cependant pas rester dans ~mods. C'est le fichier qui s'approprie la classe de la caméra, et un hook antérieur à 1.5.0 ne démarre pas le loader – le panneau s'ouvre alors sans que la vue se décale, et tout mod conçu pour le loader reste inactif. Supprimez-le donc ou remplacez-le par l'actuel. Avec le pak hook : il change rarement, car il ne fait que démarrer le panneau, tout le reste est dans AltUI.pak. Chaque entrée du changelog indique si le hook a changé ; s'il y est écrit « unchanged », le vôtre peut rester. Un nouveau hook n'est nécessaire que si le changelog le dit ou si une mise à jour du jeu remplace le gestionnaire de caméra du joueur.

**Le hook sans le Blueprint Loader :** depuis 1.8.0, AltUI applique aussi votre look à Jodi dans le menu principal et sur l'écran de chargement. Avec le hook seul, il faut pour cela l'AltUI_Hook_P.pak actuel – remplacez l'ancien ; dans les niveaux, l'ancien continue de fonctionner. Avec le Blueprint Loader, AltUI.pak s'en charge lui-même.

Aucune ressource du jeu n'est incluse ; tout ce qui se trouve dans le pak est généré.

## Ce que font les combinaisons

AltUI.pak est le mod ; un second fichier doit le démarrer. Ce que cela donne :

* **AltUI.pak seul** – rien ne démarre le panneau – B ne fait rien.
* **AltUI.pak + Blueprint Loader** – le loader lit la table d'AltUI et démarre le panneau. AltUI lui-même ne remplace rien du jeu ; le loader remplace la classe de caméra du jeu, c'est ainsi qu'il fonctionne.
* **AltUI.pak + AltUI_Hook_P.pak** – le hook remplace le gestionnaire de caméra du jeu et démarre le panneau.
* **AltUI.pak + les deux** – cela fonctionne, et rien n'est perdu. Les deux remplacent la même classe du jeu, un seul des deux paks l'emporte – et quel qu'il soit : AltUI démarre, par la table du loader ou par le hook, qui démarre alors en plus le loader lui-même, pour que les mods conçus pour lui continuent de tourner.
* **Le hook ou le loader sans AltUI.pak** – rien – il manque le mod lui-même.

## Ce qu'il ne peut pas faire

Deux limites bonnes à connaître :

* **Le maquillage prend une teinte, pas une nouvelle couleur.** La couleur est multipliée sur le dessin existant : un dessin pâle ou neutre la prend presque entièrement, un dessin sombre ne peut qu'être assombri ou décalé. Le blanc signifie « inchangé », pas un maquillage blanc.
* **Un corps converti peut transparaître sous des vêtements moulants.** Le jeu aplatit ces zones avec des morph targets portés par le maillage du corps ; si un maillage n'en apporte pas, il n'y a rien pour aplatir. Cela tient au corps, pas à la conversion : le convertisseur garde ce que l'original possède – et si l'original n'en a pas, personne ne peut en ajouter après coup.

## Code source & bugs

[github.com/Zyiakk/AltUI](https://github.com/Zyiakk/AltUI) – code source (MIT), tous les téléchargements, rapports de bugs.
