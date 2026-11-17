## À propos d'AltUI {#about}

AltUI est une alternative à la garde-robe et à l'écran d'apparence de The Killing Antidote : un seul panneau pour tout.

### En bref
- Les écrans du jeu restent utilisables.
- Il s'ouvre n'importe où dans un niveau avec B – sans passer par la garde-robe ni le miroir.
- Le panneau s'ouvre sur l'onglet où il a été fermé. Les onglets inutiles peuvent être désactivés dans Paramètres › Onglets. Un onglet désactivé ne coûte rien ; ce que vous y avez réglé continue de fonctionner.

### Contenu
- Chaque objet du jeu et de tous les mods installés, dans une liste par emplacement, avec recherche, filtres, favoris et masquage.
- Coiffure, maquillage, corps, visage, poses, armes ainsi que les tenues et looks enregistrés.
- Les ragdolls : des copies de Jodi, des zombies et des humains à placer et à poser.
- La vitesse de marche et de course de Jodi.
- Un onglet Inventaire déplace les objets entre le sac à dos de Jodi et l'hyper coffre de stockage.
- Les looks deviennent des compagnons et des PNJ qui marchent et se battent avec elle.

## Installation et mises à jour {#install}

AltUI.pak contient tout le mod et va dans TheKillingAntidote/Mods/.

### Installation
Un autre fichier le démarre :
- le Blueprint Loader (un petit mod séparé) : TKA_BlueprintLoader.pak dans TheKillingAntidote/Content/Paks/~mods/, ou
- le hook propre à AltUI : AltUI_Hook_P.pak dans le même dossier ~mods/.
- L'un des deux suffit ; les deux ensemble fonctionnent aussi.
- Avec AltUI.pak seul, B ne fait rien.

### Mises à jour
- Une mise à jour ne remplace normalement que AltUI.pak.
- Le journal des modifications indique quand le hook change aussi ; un ancien hook ne doit pas rester dans ~mods/.

### Avertissement de version du jeu
- Après une mise à jour du jeu, ou avec un mod qui remplace des tables du jeu, AltUI peut tomber sur un jeu pour lequel il n'a pas été conçu. Il affiche alors un avertissement avant de faire quoi que ce soit.
- « Continuer quand même (à mes risques) » est retenu pour cette version du jeu.
- « AltUI désactivé pour l'instant » redemande au niveau suivant.

### Retirer AltUI
Supprimez les fichiers copiés :
- TheKillingAntidote/Mods/AltUI.pak
- TheKillingAntidote/Content/Paks/~mods/AltUI_Hook_P.pak – si vous utilisez le hook
- TheKillingAntidote/Content/Paks/~mods/TKA_BlueprintLoader.pak – seulement si aucun autre mod n'en a besoin

AltUI garde ses propres données dans le dossier de sauvegarde du jeu, sous Windows %LOCALAPPDATA%\TheKillingAntidote\Saved\SaveGames. Pour tout retirer, supprimez-y aussi :
- AltUI.sav – paramètres et choix
- AltUI_Looks.sav – looks enregistrés
- AltUI_Faces.sav – visages enregistrés
- AltUI_Names.sav – vos propres noms
- AltUI_Ragdolls.sav – scènes et poses des ragdolls
- AltUI_Followers.sav – compagnons et PNJ
- AltUI_Drawers.sav – tiroirs de vêtements
- AltUI_BodyPresets.sav – préréglages de corps
- AltUI_ModPresets_<mod>.sav – préréglages des réglages d'un mod (onglet Mods), un fichier par mod
- AltUI_Props.sav – objets placés et scènes d'objets
- AltUI_ObjCache.sav – les objets trouvés par la recherche de mods
- AltUI_ModScan.sav – de quel mod vient chaque pièce ; se recrée tout seul
- AltUI_Log.sav, BPLoader_Log.sav – seulement des versions de test
- le dossier AltUI – photos des looks, des visages, des préréglages d'apparence, de corps et de mods, vos propres images de fond et de boutons
- le dossier WeaponIcons – images des armes
- le dossier ObjectIcons – images des objets

Les vêtements, tenues, maquillage et coiffure sont enregistrés dans les sauvegardes du jeu et restent.

## Commandes {#controls}

Touches et souris dans le panneau, autour de Jodi et en jouant.

### Panneau
- B ouvre et ferme le panneau (autre touche dans Paramètres › Commandes) ; Échap le ferme.
- Le clic gauche sélectionne, porte ou applique ; le clic droit ouvre le menu contextuel d'une tuile, d'une ligne ou d'un onglet.
- La molette fait défiler ; la vitesse se règle dans Paramètres › Commandes.
- Annuler et Rétablir (cinq étapes) sont dans la barre d'état en bas.
- Maintenez 4 pour le menu rapide (voir « Menu rapide »).

### Caméra et Jodi
- Tant que le panneau est ouvert, Jodi ne peut pas marcher.
- Faire glisser sur le fond tourne la caméra.
- Cliquer sur Jodi et faire glisser la tourne – elle revient à sa position à la fermeture du panneau.
- + et − changent la distance de la caméra par pas de 5 %, la molette au-dessus de Jodi par pas de 4 %.

### En jouant
- Panneau fermé, la molette rapproche ou éloigne la caméra de Jodi.
- Avec l'entrée du menu rapide « Hauteur de la caméra (molette) », elle la monte ou la descend à la place (clic gauche ou Échap y met fin).
- En visant, la vue du jeu reste. La distance et la hauteur sont conservées.

### Boutons ronds
Les boutons ronds au-dessus de + et − :
- Une caméra libre : la souris tourne, W A S D et Q E déplacent, Maj plus vite, la molette règle la vitesse, Échap revient.
- Le mode photo du jeu (Échap revient).
- Le mode ragdoll (voir « Mode ragdoll »).
- Celui du haut (l'ampoule) est la lumière de caméra : elle éclaire ce que voit la caméra – à côté du panneau, dans la caméra libre et en mode photo.
- Un clic sur l'ampoule ouvre un petit menu : allumer / éteindre, la couleur de la lumière (palette) et un curseur de luminosité.
- La lumière ne fait qu'éclaircir (pas de reflets, pas de faisceau dans le brouillard). Elle s'éteint pendant le jeu et revient comme vous l'avez laissée quand le panneau s'ouvre.

### Menu principal
- Dans le menu principal, B ouvre un petit menu : les trois scènes du menu et la scène de chargement, la caméra suivante, et masquer le menu et les textes du jeu (Échap les rétablit).

## Vêtements {#clothes}

À gauche les emplacements, à droite les objets de l'emplacement choisi.

### Porter et trouver
- Un clic sur un objet le fait porter, un clic sur un objet porté le retire.
- Les puces au-dessus de la liste filtrent par mod ou par groupe ; « ... » replie les rangées de puces.
- Un champ de recherche réduit les puces ; la recherche au-dessus de la liste trouve les objets par nom, mod ou groupe.
- La recherche trouve aussi un mod par le nom de son pak, ici et dans tous les autres onglets.
- Filtres : possédés seulement, favoris seulement, vanilla seulement, portés seulement.
- L'info-bulle indique de quel mod vient un objet.

### Menu contextuel
- Clic droit sur un objet : favori, garder, masquer, couleur via la palette du jeu, réinitialiser la couleur, mettre dans le sac à dos, renommer, seulement ce groupe, voir le contenu du mod, afficher dans l'onglet.
- Dégâts : de 0 à 100 %, en direct sur un vêtement porté ; sur tout autre vêtement, ils sont gardés jusqu'à ce qu'il soit porté. Les vêtements portés sans textures de dégâts n'ont pas de curseur.

### Garder
- Une pièce marquée que vous avez mise vous-même reste en place quand vous mettez un look ou une tenue.
- Le look laisse alors de côté les pièces du même emplacement (ou d'un emplacement incompatible) et les nomme dans l'avis.
- Une pièce mise par un look ou une tenue ne reste pas au changement suivant, même marquée – essayer des tenues n'accumule donc jamais de pièces.
- La tuile affiche « gardé ». Annuler rétablit exactement l'état précédent.

### Codes couleur
- Sous la palette de couleurs du jeu, un champ affiche la couleur en #RRGGBB ; tapez un code et appuyez sur Entrée pour l'appliquer.
- « Mémoriser » garde la couleur dans AltUI, « Utiliser » la pose sur un autre vêtement ou emplacement.

### Tiroirs
Vos propres collections de vêtements, dans une barre au-dessus de la liste.
- « Par défaut » montre tout ; « + » crée un nouveau tiroir (« Tiroir 1 », « Tiroir 2 » …).
- Un tiroir montre la même page – emplacements, puces, recherche, filtres, favoris – avec seulement ses pièces, et les emplacements ne comptent que celles-ci.
- Clic droit sur une pièce › « Tiroir › » ouvre à côté du menu la liste des tiroirs : une coche indique que la pièce y est, un clic l'y met ou l'en retire, « + Nouveau tiroir » en crée un avec la pièce dedans.
- Une pièce peut être dans autant de tiroirs que vous voulez ; dans un tiroir, le menu a en plus « Retirer de ce tiroir ».
- Clic droit sur un tiroir : renommer (Entrée valide, Échap annule), déplacer à gauche / à droite, supprimer (demande d'abord – les pièces restent).
- Le tiroir affiché est conservé après un redémarrage.

## Tenues {#outfits}

Les tenues enregistrées du jeu – les mêmes que celles de la garde-robe et du miroir.

### Enregistrer et porter
- La tuile « + » enregistre ce que Jodi porte comme nouvelle tenue.
- Un clic sur une tenue la fait porter.
- Une tenue sans nom propre s'affiche comme « Tenue » suivie de sa place dans la liste.
- La taille des tuiles et le nombre d'objets affichés par tuile se règlent dans Paramètres › Tuiles.

### Menu contextuel
- Clic droit : porter, voir le contenu, ajouter au menu rapide ou l'en retirer, renommer, déplacer à gauche / à droite / au début / à la fin, supprimer.
- « Mettre à jour avec ce qu'elle porte » : la tenue reprend ce que Jodi porte, dans ses couleurs actuelles ; le nom, la place, l'entrée du menu rapide et la touche propre restent.

### Couleurs
- Une tenue enregistrée ici garde chaque canal de couleur de ses pièces, tel qu'AltUI les a colorées.
- Le jeu lui-même ne garde qu'une couleur par pièce ; une tenue enregistrée au miroir n'a que celle-là.

### Partager
- Clic droit → « Exporter (partager)… » l'affiche en texte – Ctrl+A, Ctrl+C et envoyez-le.
- « Importer… » en bas à droite : collez avec Ctrl+V ; « Vérifier » montre le contenu et les mods manquants (ce qui est déjà enregistré exactement ainsi est laissé de côté).
- Puis importez tout ou sans les pièces manquantes.
- Les photos ne sont pas partagées – prenez-en une nouvelle avec « Mettre à jour ».

## Looks {#looks}

Un look, c'est tout à la fois : vêtements avec leurs couleurs, coiffure et couleur des cheveux, maquillage, yeux, peau, mutation, curseurs du corps, mod de corps et visage.

### Enregistrer et appliquer
- La tuile « + » enregistre le look actuel avec une photo en pied : de face, ou avec la caméra libre – placez-la où vous voulez et cliquez pour prendre la photo (Échap : photo de face à la place).
- Un clic sur un look l'applique.

### Tri
- « Tri : … » en bas à droite de l'onglet Looks (clic gauche ou droit) ouvre un menu de sept ordres : Personnalisé, Nom A–Z, Nom Z–A, Plus récents d'abord, Plus anciens d'abord, Modifiés récemment, Inchangés depuis le plus longtemps. L'ordre actif est marqué par « > ».
- « Personnalisé » garde votre propre ordre, celui réglé avec « Déplacer ». Déplacer n'est proposé qu'en Personnalisé ; dans les autres ordres, la position suit le tri.
- Les dates ne sont enregistrées que depuis cette version. Les looks enregistrés avant n'en ont pas : ils comptent comme les plus anciens dans les ordres par date et n'affichent pas de date dans l'infobulle.
- En survolant un look, on voit quand il a été créé et modifié pour la dernière fois (« Créé le … · Modifié le … »). Renommer ne change pas la date, « Mettre à jour » oui. Un look importé compte comme nouveau.
- Le menu rapide liste les looks dans le même ordre.

### Menu contextuel
- Clic droit : voir le contenu, renommer, mettre à jour (photo de face, en caméra libre ou en gardant la photo), déplacer, supprimer, ajouter au menu rapide ou l'en retirer.
- « Voir le contenu » liste les valeurs du corps dans l'ordre de la page Morphologie, avec ses titres « Poitrine » et « Fessiers et hanches » au-dessus de l'angle et du rebond.
- Aussi : « Créer en ragdoll », « Créer en compagnon », « Créer en PNJ », « Créer en ennemi » (voir « Ragdolls » et « Compagnons »).

### Copie nettoyée
- « Copie nettoyée (sans les parties manquantes) » n'est affiché que si le look contient des pièces d'un mod qui n'est plus installé, ou des lignes de maquillage / d'yeux qu'aucune table ne connaît.
- Elle crée un nouveau look juste après, sans ces entrées, avec la même photo.
- L'original reste tel quel ; réenregistrer un look ne les retire jamais de lui-même.

### Partager
- Clic droit → « Exporter (partager)… » l'affiche en texte – Ctrl+A, Ctrl+C et envoyez-le.
- « Importer… » en bas à droite : collez avec Ctrl+V ; « Vérifier » montre le contenu et les mods manquants (ce qui est déjà enregistré exactement ainsi est laissé de côté).
- Puis importez tout ou sans les pièces manquantes.
- Les photos ne sont pas partagées – prenez-en une nouvelle avec « Mettre à jour ».

## Sac à dos {#bag}

Ce que Jodi porte et ce qu'elle transporte.

### Objets un par un
- Un clic sur un objet porté le retire, un clic sur un objet transporté le fait porter.
- Clic droit : porter ou retirer, réparer (il faut un kit de couture), retirer du sac à dos, vers la garde-robe.
- Le menu contextuel a aussi le curseur de dégâts (voir « Vêtements »).

### Tout le sac à dos
- « Ranger le sac à dos » retire les objets qui ne sont pas portés et qui sont aussi dans la garde-robe.
- « Tout dans le sac à dos » retire chaque objet porté et le met dans le sac à dos.

## Inventaire {#inventory}

Les objets de Jodi et l'hyper coffre de stockage, une liste sous l'autre.

### Listes
- Les puces filtrent par les groupes du jeu (armes, munitions, accessoires d'armes, outils…).
- Le poids montre ce que Jodi porte, ce qu'elle peut porter et de combien elle est en surcharge.
- « ... » au-dessus d'une liste la replie, ↑↓ lui donne toute la hauteur (encore une fois : retour).
- La taille des tuiles de cet onglet se règle dans Paramètres › Tuiles.
- Sur les cartes où le jeu ne sauvegarde jamais le sac à dos (le stand de tir, par exemple), l'onglet le signale : gardez ce que vous voulez conserver dans le coffre.

### Déplacer des objets
- Un clic met un objet dans le coffre ou en sort un.
- Clic droit : la moitié ou tout, utiliser, examiner, jeter, raccourci 1 ou 2, décharger, « Accessoires… » (ouvre l'arme dans l'onglet Armes).
- Le menu contextuel d'une pile se termine par « Quantité » : un curseur et un champ numérique, puis une entrée par destination avec ce nombre (« Ranger 5 dans le coffre », « En prendre 5 »). Entrée dans le champ exécute la première entrée.
- Dans le catalogue, le nombre compte des unités et le champ accepte plus que le curseur. Les armes à feu et les objets uniques n'ont pas de quantité.
- « Équiper automatiquement les armes » (Paramètres › Général, activé par défaut) : une arme sortie du coffre ou du catalogue va dans la main de Jodi comme dans le jeu ; désactivé, elle garde ce qu'elle tient.
- Tout passe par les fonctions du jeu lui-même, ses règles restent donc – surcharge comprise.

### Tout jeter
- « Tout jeter » pose un objet au sol par paquet.
- À partir de 100 objets, une fenêtre demande d'abord : « Annuler », « Détruire à la place » (les objets disparaissent, rien ne tombe) ou « Jeter quand même » – autant d'objets physiques à la fois peuvent faire planter le jeu. Échap annule.

### Toujours équiper automatiquement
- « Toujours équiper automatiquement » (clic droit, aussi sur le catalogue) : après chaque chargement de niveau, AltUI remet l'objet, neuf, dans le sac de Jodi, jusqu'à la quantité de la tuile au moment du marquage (au moins un paquet). Rien n'est jamais retiré.
- Ces tuiles montrent une flèche circulaire dorée et un cadre doré. « Ne plus équiper automatiquement » l'arrête.
- « Réapprovisionner aussi les objets marqués en mode histoire » (Paramètres › Général, activé par défaut) : désactivé, AltUI ne réapprovisionne rien dans les niveaux de l'histoire ; les marques restent, le bureau et les défis ne changent pas.
- Une arme marquée revient telle qu'elle était au marquage (celle portée ou celle de la boîte, celle du catalogue sans accessoires), avec un chargeur plein ; une pièce de rechange dans le sac à dos reste.
- Si Jodi la porte avec d'autres accessoires au chargement d'un niveau, ils sont rétablis et les pièces retirées vont dans le sac à dos.
- Pour une nouvelle configuration, retirez la marque puis marquez-la à nouveau.

### Tous les objets
- « Tous les objets » est désactivé par défaut (Paramètres › Général) : chaque objet du jeu en troisième liste, avec sa propre recherche.
- Un clic met un paquet dans le sac à dos ; clic droit : cinq, ou dans le coffre.
- « Collection » contient aussi la Main invisible du jeu : tant qu'elle est dans le sac à dos, elle apporte à Jodi les objets proches, l'un après l'autre, plus vite avec plusieurs mains (une toutes les 2,5 s, dès six toutes les 0,1 s).
- « Collection » dans le sac à dos montre combien Jodi en a.

## Coiffure {#hair}

Toutes les coiffures du jeu et des mods.

### Choisir
- Un clic sur une coiffure la met.
- Les favoris sont en haut, au-dessus de toutes les coiffures.
- Le champ de recherche au-dessus des vignettes trouve les coiffures par nom affiché, identifiant, nom du mod et fichier pak ; × le vide.

### Couleur des cheveux
- « Couleur des cheveux... » ouvre la palette du jeu.
- « Couleurs naturelles » propose 14 couleurs prêtes.

### Menu contextuel
- Clic droit : ajouter aux / retirer des favoris, réinitialiser la couleur des cheveux, renommer, voir le contenu du mod.
- Sur une coiffure issue d'un mod, aussi : « Renommer le mod… ».

## Poses {#poses}

Chaque animation d'action que connaissent le jeu et vos mods de poses – la liste derrière l'application « rythme » du téléphone.

### Jouer
- Un clic sur une pose la joue ; un nouveau clic ou « Arrêter la pose » l'arrête.
- « Répéter les poses : oui » dans la barre d'état relance une pose qui se termine d'elle-même, jusqu'à ce que Jodi bouge, que la touche d'utilisation ou « Arrêter la pose » la termine ou qu'une autre pose soit choisie. Beaucoup de mods de poses répètent leurs poses de toute façon.
- Un haut-parleur dans le coin d'une tuile signale une pose avec son.

### Trier et trouver
- Les poses sont triées par posture (debout, assise, allongée) et par chapitre.
- Les puces filtrent par mod, la recherche trouve les titres.
- « Tout mesurer » joue une fois chaque pose qui n'a pas encore de posture et la classe ; il affiche le nom de la pose en cours de mesure.

### Menu contextuel
- Clic droit : favori, masquer, classer comme debout / assise / allongée / en mouvement, renommer, ajouter au menu rapide.
- « Utiliser au repos » : la pose commence après 1,5 s d'immobilité et s'arrête quand Jodi marche, sort une arme ou s'accroupit. « Plus au repos » la désactive.

## Armes {#weapons}

À gauche, une entrée par arme, armes de mêlée comprises. Pour chaque arme, le modèle, le skin et le son du tir se choisissent séparément. Le choix est conservé et réappliqué quand l'arme est ramassée ou sortie de la caisse de rangement.

### Modèles et skins
- En haut : les modèles – celui du jeu et chaque mod de modèle installé.
- En bas : les skins – les peintures d'armes du jeu (sans bombe de peinture) et chaque mod de skin installé.
- Si un mod de modèle apporte ses propres versions des peintures du jeu (faites pour son modèle), elles apparaissent comme skins supplémentaires à côté de celles du jeu tant que ce modèle est choisi.
- Les tuiles de modèle montrent chaque modèle avec le skin choisi.
- La peinture propre d'un modèle ne fonctionne que sur ce modèle – sur tout autre, l'arme reste telle quelle, et sa tuile aussi.
- La tuile d'un mod de skin est atténuée quand le skin n'a aucun effet sur le modèle choisi ; on le sait dès que l'arme a été dans la main de Jodi avec ce modèle.
- Une peinture appliquée dans le jeu avec une bombe de peinture est conservée : elle devient le skin choisi.

### Son
- Le son de tir propre à l'arme (« Original ») et chaque son de tir installé pour elle.
- Un clic choisit le son et le joue ; toutes les autres armes gardent le leur.
- Un silencieux monté avec son propre son reste prioritaire.

### Filtres et menu contextuel
- Les puces au-dessus filtrent les trois sections à la fois.
- Clic droit sur une tuile : favori, masquer, seulement ce mod.
- Clic droit sur un modèle de mod : forcer les skins dessus, exclure le chargeur, la visée, le silencieux ou la poignée, afficher l'image propre au mod.
- Clic droit sur un modèle, un skin ou un son issu d'un mod : « Renommer le mod… ».

### Images
- « Reprendre les images » dans la barre d'état reprend toutes les tuiles de l'arme.
- « Afficher les images d'objet » dans la barre d'état met sur chaque tuile l'image propre de l'objet ou du mod au lieu de l'image rendue.

### Accessoires
- Une ligne par emplacement de l'arme (viseur, canon, poignée, chargeur), « Aucun » en premier.
- Les pièces viennent du sac à dos, ou du coffre de stockage et passent alors dans le sac à dos.
- Les accessoires ne vont que sur les armes que Jodi porte sur elle ; l'arme garde le modèle, le skin et le son choisis ici.

### Mods d'armes
- Les mods d'armes et de sons de tir doivent d'abord être convertis avec weaponpak.pyz ; voir le guide WEAPON_MODS sur la page du mod.

## Apparence {#look}

Peau, chaque type de maquillage, yeux et préréglages d'apparence du jeu.

### Maquillage et yeux
- Un clic sur une entrée l'applique.
- Clic droit sur un maquillage : teinter avec la palette du jeu, réinitialiser la teinte.
- Yeux : couleur de l'iris et des cils dans le menu contextuel.

### Peau huilée
- « Peau huilée » au-dessus des peaux rend la peau brillante, comme la peau mouillée du jeu (la peau mouillée du jeu = 50 %).
- Case cochée = votre valeur, même face à l'histoire ; décochée = le jeu décide à nouveau.
- Seulement sur Jodi. Les looks et les presets d'apparence gardent ce réglage ; les plus anciens reviennent à « le jeu décide ».

### Mutation
L'apparence mutée de Jodi dans l'histoire, par parties.
- Couleur de peau et lueur en curseurs (case cochée = actif), veines et yeux en interrupteurs ; « Réinitialiser » désactive tout.
- Le maquillage reste visible sur la peau décolorée ; votre couleur d'iris teinte l'œil muté.
- « Look de l'histoire » reproduit l'apparence de la cinématique : matériau de peau de l'histoire, toutes les lignes au maximum ; chaque ligne peut ensuite être réduite. Maquillage et cicatrices n'y sont pas visibles.
- Pendant que l'histoire fait muter Jodi elle-même, c'est son apparence qui s'applique.

### Préréglages
- La tuile « + » enregistre l'apparence actuelle avec une photo.
- Clic droit : appliquer, voir le contenu, renommer, mettre à jour, déplacer, supprimer, menu rapide.

### Partager
- Clic droit sur un preset → « Exporter (partager)… », « Importer… » en bas à droite – comme pour les looks.
- Sans les pièces manquantes, une coiffure, une peau ou une ligne de maquillage manquante est retirée.
- Un texte peut mêler looks, tenues, visages et tous les presets ; chaque page avec « Importer… » prend tout.

## Morphologie {#body}

Les curseurs de poitrine et de taille du jeu, et davantage sur les mods de corps convertis.

### Corps
- Les puces passent du corps du jeu à chaque mod de corps converti.
- Les mods qui remplacent le corps doivent d'abord être convertis avec bodypak.pyz ; voir le guide BODY_MODS sur la page du mod.

### Curseurs
- Les curseurs de poitrine et de taille du jeu.
- Les corps convertis ont en plus des curseurs d'os : échelle, buste, taille, fessiers et hanches, cuisses, mollets, bras, mains, pieds.
- Ils sont conservés par corps ; « Réinitialiser la forme » les remet à zéro.
- Le curseur des tétons n'agit que si la poitrine est découverte.

### Rebond
- Poitrine et fessiers et hanches : rebond (0 % = animation seule) règle la physique du jeu et fonctionne avec tous les corps.
- Un soutien-gorge amortit toujours comme dans le jeu.
- Angle (seulement sur les corps convertis) : l'angle agit d'autant plus qu'il y a moins de rebond (pas du tout à 100 %).

### Hanches et jambes
- La largeur des hanches et l'écart des jambes n'existent que pour les corps convertis.
- L'écart des jambes déplace toute la jambe sur le côté, en cm par côté.
- La largeur des hanches écarte aussi les jambes (à 1,3×, environ -2 cm les ramènent), mais cela réduit un peu la largeur des hanches.

### Préréglages
- Au-dessus des curseurs, « + » enregistre tous les curseurs de la page – ceux du corps ainsi que la poitrine et la taille du jeu – avec une photo comme préréglage de la puce de corps choisie.
- Moitié haute du « + » : photo de face ; moitié basse : caméra libre.
- Chaque puce de corps n'affiche que ses propres préréglages. « ... » replie les préréglages.
- Un clic en charge un ; clic droit : appliquer, renommer, mettre à jour, déplacer, supprimer, menu rapide.
- Depuis le menu rapide, un préréglage passe d'abord à son corps.

### Partager
- Clic droit sur un preset → « Exporter (partager)… », « Importer… » en bas à droite – comme pour les looks.
- Un preset va à son body, même si ce body manque ici ; il apparaît dès que le body est converti.

## Visage {#face}

L'expression du visage de Jodi.

### Expressions
- Curseurs pour les expressions du jeu (détendue, concentrée, sourire, douleur, frayeur, fatiguée, souffrance), le regard et les formes de la bouche.
- Les expressions sont mélangées (ensemble au plus 100 %) ou additionnées.
- Une entrée cochée garde sa valeur, même pendant les poses ; une entrée non cochée est laissée à l'animation du jeu.
- « Tout fixer » et « Tout au jeu » basculent toutes les entrées à la fois.

### Yeux fermés
- « Yeux fermés » (sous Regard) ferme les yeux, d'ouverts à complètement fermés ; le clignement des yeux du jeu continue comme d'habitude.
- Seulement avec les corps convertis, comme les curseurs du corps. Sur tout autre corps, ces lignes sont grisées ; l'infobulle explique pourquoi.
- « Œil gauche fermé » et « Œil droit fermé » ferment un seul œil (gauche / droit de Jodi), par exemple pour un clin d'œil.
- Chaque œil se ferme autant que la plus grande valeur entre sa ligne et « Yeux fermés ».

### Visages enregistrés
- La tuile « + » enregistre le visage actuel avec une photo.
- Clic droit : appliquer, voir le contenu, renommer, mettre à jour, déplacer, supprimer.
- Partager : clic droit sur un visage → « Exporter (partager)… », « Importer… » en bas à droite – comme pour les looks.

## Mods {#mods}

Les réglages d'autres mods qui s'enregistrent auprès d'AltUI : à gauche leurs entrées, à droite les interrupteurs, curseurs, nombres, choix, couleurs, champs de texte, touches et boutons de celui qui est choisi. Cet onglet n'apparaît que si un tel mod est installé.

### Onglets et sections
- Un mod peut répartir sa page en onglets : ils ressemblent aux onglets du haut et se placent au-dessus des réglages.
- Ce qui précède le premier onglet reste visible sur chaque onglet.
- Les réglages d'un onglet et de chaque section reposent sur une surface claire à part, on voit ainsi ce qui va ensemble.
- Un titre avec une flèche replie ou déplie d'un clic les réglages en dessous.
- AltUI retient l'onglet choisi de chaque page et les sections repliées.

### Préréglages
- Au-dessus des réglages : les préréglages de la page. La tuile « + » enregistre les réglages actuels avec une photo (de face ou en caméra libre) ; un clic applique un préréglage.
- Les préréglages contiennent toujours la page entière, quel que soit l'onglet affiché.
- Clic droit : appliquer, afficher le contenu, renommer, mettre à jour, déplacer, supprimer, menu rapide.
- « Afficher le contenu » liste les valeurs, chacune avec une case : seules les valeurs cochées sont appliquées, les autres restent enregistrées.
- Les onglets et les titres de la page y figurent aussi au-dessus de leurs valeurs : des champs du même nom restent ainsi distincts.
- Enregistrés par mod dans AltUI_ModPresets_<mod>.sav.
- « ... » dans la barre au-dessus des tuiles replie la zone des préréglages de toutes les pages de mods et la rouvre.

### Préréglages fournis par un mod
- Ils viennent en premier.
- On peut les appliquer, les renommer, leur donner sa propre photo (« Nouvelle photo ») et cocher ou décocher leurs valeurs – pas les modifier ni les supprimer.
- Ils peuvent être masqués (clic droit « Masquer ») ; « Afficher les préréglages masqués » dans la barre au-dessus des tuiles fait revenir ceux de cette page.

### Partager
- Clic droit sur un preset personnel → « Exporter (partager)… », « Importer… » en bas à droite – comme pour les looks.
- Les préréglages fournis viennent avec le mod lui-même.
- Un preset importé va à la page de son mod, même si le mod manque ; il apparaît dès qu'il est installé.

## Paramètres {#options}

À gauche, les catégories. Ce que contient chacune :

### Général
- Langue et part de l'écran laissée libre pour Jodi.
- Autoriser à retirer les sous-vêtements ; affichage des objets non possédés.
- L'interrupteur du Codex pour l'encyclopédie.
- Le catalogue « Tous les objets » et « Équiper automatiquement les armes » pour l'onglet Inventaire.
- « Aucun avis » masque tous les avis en bas, ceux d'AltUI et ceux du jeu lui-même.
- « Les vêtements suivent la forme du corps » (désactivé par défaut, corps convertis uniquement) : le tissu qui ondule, comme les jupes et les manteaux, reste plus près des curseurs de poitrine, hanches, fessiers, cuisses et taille agrandis au lieu de rentrer dans le corps ; plus la forme est grande, moins il ondule.

### Tuiles
- Taille des tuiles, tailles propres pour les tuiles de tenues, de looks et de ragdolls.
- Objets par tuile de tenue, pas de limite pour les longues listes.
- Détails des info-bulles.
- La taille des tuiles de l'onglet Inventaire.

### Groupes
- Fusionner les groupes ou les mods de même nom.
- Longueur des noms de groupe, hauteur de la zone des puces, recherche dans les puces.

### Caméra
- Champ de vision, distance, hauteur, la caméra suit l'emplacement choisi.
- Deux interrupteurs pour la caméra libre (aussi en mode ragdolls) : sans collision – elle traverse les murs et Jodi – et à n'importe quelle distance de Jodi.

### Commandes
- Touche du panneau, vitesse de défilement, hauteur de la caméra avec le bouton droit.
- De combien la molette soulève un ragdoll par cran.

### Déplacement
Vitesse de marche et de course propre à Jodi (50 à 200 %) ; s'accroupir et sauter restent inchangés. « Valeurs par défaut » remet les vitesses de marche, de course et du ralenti.

- « Sauter au bureau » (désactivé par défaut) permet à Jodi de sauter et de grimper dans son bureau, où le jeu bloque les deux ; le menu Échap met alors aussi le jeu en pause à cet endroit, comme dans les niveaux.
- « Ralenti activé » allume le ralenti, « Vitesse du ralenti » (5 à 90 %, 25 % par défaut) règle sa lenteur. L'entrée du menu rapide « Ralenti oui / non » fait la même chose que l'interrupteur.

Pieds au sol (désactivés par défaut, uniquement sur les corps convertis) :
- « Les pieds suivent le sol » : les pieds se posent sur les marches et les pentes tant que Jodi reste immobile.
- « Genoux et mains suivent le sol » : les genoux et les mains se posent au sol dans les poses au sol.
- Astuce : laisser le premier activé, activer le second pour les poses. IK des pieds par BenenG47.

Debout, styles de marche et de course :
- « Debout » choisit l'animation au repos de Jodi : celles du jeu (regarde autour, regarde ses ongles, regarde sa jambe, prudente, blessée, pose) et celles des mods de repos installés (IdleAltUI_…).
- Les mods de marche / course (WalkAltUI_…) ajoutent des choix à « Style de marche » et « Style de course » ; ces lignes n'apparaissent que s'il y a un choix.
- Un mod de marche l'emporte sur un mod de course ou d'attente choisi en même temps : ce côté reste normal et le dit sous sa ligne.

### Thème
- Chaque couleur du panneau et son opacité.
- Une image de fond (remplissage, alignement, teinte, sépia, inversion, opacité propre) et une image pour les tuiles et les onglets.
- Schémas de couleurs enregistrés sous un nom ; un thème enregistré garde aussi les images et leurs réglages. La réinitialisation est dans la barre d'état.
- Images personnelles : Background_1 … Background_30 et Button_1 … Button_30 (.png, .jpg ou .jpeg) dans le dossier indiqué sur la page.
- « Afficher les aperçus » montre les images elles-mêmes sur leurs puces. Clic droit sur l'aperçu d'une image personnelle : « Recréer l'aperçu ».

### Conflits d'emplacements
- Séparer les paires d'emplacements du jeu (par exemple soutien-gorge et chemise) pour pouvoir porter les deux.
- « Plusieurs pièces dans un emplacement » : un emplacement activé garde ses pièces quand on en enfile une autre (par exemple des chaussettes hautes sur des collants), pour Jodi, les compagnons et les looks.

### Onglets
- Texte, icônes ou les deux dans la barre d'onglets ; désactiver des onglets.
- Un clic droit sur un onglet de la barre le déplace ; « Ordre des onglets » rétablit l'ordre par défaut.
- « Tenter de tenir sur une ligne » : les libellés rétrécissent puis raccourcissent, pour que la barre tienne sur une ligne quand c'est possible.

## Gestion {#manage}

Noms d'affichage, mods utilisés et partage de nombreux éléments à la fois.

### Noms
Vos propres noms d'affichage pour les mods, groupes, vêtements, coiffures, peaux, maquillages, poses et préréglages d'apparence.
- Les noms sont utilisés partout dans le panneau et trouvés par la recherche ; l'identifiant d'origine reste cherchable et apparaît dans l'info-bulle.
- Des puces et une recherche filtrent la liste ; « seulement les mods » masque les entrées du jeu ; ↺ revient au nom par défaut.
- Les mods d'armes figurent avec les autres mods.
- Avec altui_names.pyz, les noms peuvent être exportés dans un fichier texte puis réimportés.
- « Relire les mods » (à côté de la recherche) relit de quel mod vient chaque pièce. AltUI le garde d’un lancement à l’autre et remarque seul les mods modifiés ; le lien sert au cas où il ne le ferait pas.

### Utilisation
« Utilisation » montre quels mods sont utilisés en ce moment.
- Pour chaque mod : les pièces utilisées et où elles se trouvent (Jodi maintenant, tenues, looks, préréglages, favoris, compagnons, scènes de ragdolls, position debout, armes, scènes et positions d'objets, tiroirs de vêtements).
- Les scènes d'objets et les positions d'objets enregistrées comptent aussi comme utilisation (modèles de mods).
- Ce qui se trouve seulement dans la garde-robe ne compte pas comme utilisé.
- Les mods inutilisés sont listés en gris en dessous, ainsi que les mods dont AltUI ne peut pas détecter l'utilisation (cartes, mods de script). « Voir le contenu » ouvre chacun d'eux.
- Chaque mod est une tuile avec son nom affiché et son fichier pak ; les emplacements d'une pièce sont résumés par type (p. ex. « Tenues 4–6, 8 »).
- La liste est établie à l'ouverture de « Utilisation » ; ailleurs, le nombre à gauche est celui de la dernière fois (aucun avant la première).

### Partager
« Partager » met tous les looks, tenues, visages, préréglages d'apparence, du corps et vos préréglages de mods sur une page.
- Groupés par type (« tous » / « aucun » par type), avec le body ou le mod à côté.
- Cochez-les, puis « Exporter (n)… » en bas à droite les donne en un seul texte ; « Importer… » à côté lit un tel texte.
- Les coches ne valent que tant que la page est ouverte.
- Les préréglages de mods non installés en ce moment ne sont pas listés.

## Ragdolls {#ragdolls}

Des figures avec physique à placer et à poser dans le niveau : copies de Jodi, zombies et humains.

### Créer
- « + Créer une copie de Jodi » place une copie devant elle, debout et figée dans sa pose actuelle, avec tout ce qu'elle porte.
- Un look devient une figure avec « Créer en ragdoll » dans son menu contextuel.
- « Zombies et humains » : une tuile illustrée par type de zombie, plus l'infirmière et une survivante. Un clic la crée ; les liens sous une tuile créent ses variantes.
- Le mercenaire est aussi un type de figure ; il garde son fusil en main.

### Lignes des figures
- Chaque figure a sa ligne : active (physique, elle tombe et peut être lancée) ou figée (elle garde sa pose), « articulations › », tout bloquer, tout libérer, retirer.
- En bas à droite, dans la barre d'état : « Tout retirer » (retire toutes les figures) et « Sphères des articulations : oui/non ».

### Articulations
- « articulations › » déplie les 17 articulations de la figure, chacune avec deux interrupteurs : bloquée/libre et mobile/fixe.
- Une articulation bloquée reste rigide tant que la figure est active ; une articulation mobile peut être posée sur la figure figée.
- Les sphères des articulations montrent où saisir : gris, rouge = bloquée, vert = mobile, bleu = fixée.
- Les sphères cachées transparaissent, pâles, à travers le corps ; un clic sur une sphère saisit exactement cette articulation.
- Elles n'apparaissent que dans cet onglet et en mode ragdoll.

### Poses et scènes
- Poses (dans la ligne dépliée) : un nom et « enregistrer la pose » retiennent la position des parties du corps et les articulations bloquées ou mobiles.
- Une pose se charge sur toute figure du même type, dans tous les niveaux – un clic charge, clic droit : charger / supprimer. La figure se fige et se tient sur le sol.
- Scènes : « Enregistrer la scène sous » retient chaque figure du niveau avec son apparence, sa place, sa pose et ses articulations ; le même nom dans le même niveau remplace l'ancienne.
- Seules les scènes du niveau actuel sont affichées. Un clic charge une scène et remplace les figures présentes ; clic droit : charger / supprimer.

### Attaquable
- « Rendre attaquable » (copies de Jodi, de PNJ et du mercenaire) : les zombies attaquent le ragdoll comme une figure ; son en-tête affiche alors « · attaquable ».
- Chaque coup pousse la partie du corps la plus proche du zombie ; un ragdoll figé reprend sa pose environ une seconde après le dernier coup.
- Les ragdolls ne meurent pas. L'état est enregistré avec la scène.

### Souris sur une figure
À côté du panneau et en mode ragdoll :
- Glisser avec le bouton gauche une figure figée la déplace sur le sol ; la molette la lève ou l'abaisse pendant le glissement.
- Glisser avec le bouton gauche une figure active saisit la partie du corps sous la souris ; relâchez et elle tombe. La molette monte ou descend alors le point saisi.
- Un clic droit pendant le glissement fixe la partie là où elle est ; le reste de la figure y pend. Saisissez-la de nouveau et elle est libre. « tout relâcher » dans la ligne de la figure les libère toutes.
- Glisser avec le bouton droit tourne la figure autour de ses hanches.

### Poser avec la souris
- Maj + clic gauche bloque ou libère l'articulation cliquée.
- Maj + clic droit sur une figure figée rend l'articulation mobile.
- Glisser ensuite avec le bouton gauche une partie du corps sous une articulation mobile ne déplace que cette partie ; elle reste là où vous la lâchez – c'est ainsi qu'on pose une figure.
- Glisser avec le bouton droit sur une partie du corps sous une articulation mobile d'une figure figée tourne ce membre autour de l'articulation : le point saisi suit la souris, la main et les doigts tournent avec.
- La molette tord pendant ce temps le membre autour de son propre axe.
- La rotation reste dans la pose et est enregistrée avec les poses et les scènes ; les limites des articulations ne s'appliquent que lorsque la figure devient active.

### Doigts et yeux
Figures figées avec le corps de Jodi :
- De près (à moins d'environ 1 m), de petites sphères apparaissent sur les phalanges et les paupières.
- Glisser avec le bouton droit sur une sphère de doigt tourne la phalange, la molette la vrille ; glisser avec le bouton gauche plie tout le doigt (tirer le bout vers la base).
- Glisser avec le bouton gauche sur une sphère de paupière oriente le regard des deux yeux ; la molette ouvre et ferme alors les paupières (avec Maj en saisissant : cette paupière seulement).
- Dans une figure dépliée, « Main gauche » et « Main droite » appliquent des poses de main (ouverte, détendue, poing, pouce levé, paix, montrer, tenir, pose de base).
- « Yeux : réinitialiser » ouvre les paupières et regarde droit devant.
- Les poses et les scènes enregistrent doigts, paupières et regard.

### Menu rapide
Sans le panneau, le menu rapide active ou fige les figures :
- « Ragdoll : activer / figer celle visée » prend la figure au centre de l'écran.
- « Ragdolls : actifs / figés » les bascule toutes.

## Mode ragdoll {#ragmode}

Déplacer et poser les figures sans le panneau, la caméra libre dans la pièce.

### Lancer et quitter
- On le lance avec le troisième bouton rond au-dessus de + et − ou depuis le menu rapide.
- Échap ou B quitte le mode.

### Caméra
- W A S D et Q E déplacent la caméra, Maj plus vite ; Maj + molette règle la vitesse.
- Glisser dans le vide tourne la caméra.
- Maintenir le bouton du milieu tourne la caméra sans être arrêté par les bords de l'écran ; le pointeur revient ensuite à sa place.

### Figures
- Le pointeur de la souris reste visible ; sur une figure tout fonctionne comme à côté du panneau (voir « Ragdolls »).

## Ennemis {#enemies}

Des zombies vivants et hostiles de toutes sortes.

### Faire apparaître
- Une tuile fait apparaître son type, les liens en dessous ses variantes.
- Ils apparaissent dans la direction de la caméra à la distance réglée, autant que « Nombre » l'indique, répartis autour de ce point.

### Comportement
- *Traquer* – ils foncent aussitôt sur Jodi.
- *Guetter* – ils attendent de voir ou d'entendre quelqu'un (les compagnons aussi).
- *Passif* – ils restent immobiles et rien ne les réveille.
- Un changement s'applique à tous les ennemis créés par AltUI.

### Retirer
- *Tout retirer* / *Retirer le plus proche* les font disparaître (pas de butin, pas d'EXP).
- *Tout tuer* les fait mourir comme dans le jeu – les corps restent jusqu'à *Tout retirer*.

### Vues « Faire apparaître » et « Vivants »
- Deux vues : « Faire apparaître » (ci-dessus) et « Vivants (n) ».
- « En vie : n » compte les ennemis vivants créés par AltUI ; les zombies du jeu ne sont jamais touchés.
- « Vivants (n) » : une ligne par ennemi – les figures créées depuis un look (avec tout ce que propose l'onglet Compagnons) et, en dessous, chaque zombie créé par AltUI avec son type, sa distance et son comportement.
- Liens par zombie : traquer, guetter, passif, retirer, tuer.

### Bon à savoir
- Le jeu enregistre les ennemis vivants avec la sauvegarde : après le chargement, ce sont des zombies du jeu. Retirez-les ou tuez-les avant de sauvegarder.
- Dans un défi, des ennemis vivants empêchent la victoire (le jeu compte chaque zombie vivant). Les cinématiques les retirent.
- Là où il n'y a pas de chemins (le bureau de Jodi, le niveau 3, le stand de tir), ils ne marchent que tout droit vers une cible qu'ils voient.

### Menu rapide
- « Faire apparaître : <type> » par type et variante (avec le nombre, la distance et le comportement actuels).
- « Ennemis : tout retirer / tout tuer / passifs / actifs ».
- Les deux dans l'onglet Actions, aussi sur des touches propres.

## Navigation {#navigation}

Le vol, et les lits du niveau actuel vers lesquels se téléporter.

### Voler / Atterrir
- Voler : Jodi vole. Se déplacer comme d'habitude, Espace monte, Ctrl descend, Maj va trois fois plus vite ; le curseur règle la vitesse. Les murs l'arrêtent.
- Atterrir la laisse tomber au sol – une longue chute blesse comme dans le jeu.
- Aussi dans le menu rapide, donc aussi sur une touche à soi (Actions › Touches personnelles).

### Lits et téléportation
- Liste les lits du niveau actuel où Jodi peut sauvegarder, le plus proche d'abord, avec le nom de la pièce et la distance.
- « Téléporter » place Jodi à côté de ce lit, tournée vers lui ; on sauvegarde comme d'habitude en utilisant le lit.
- Les suiveurs qui la suivent viennent aussi, ceux qui attendent restent.
- Une téléportation saute tout ce qui se trouve sur le chemin : les étapes de l'histoire que le jeu déclenche quand Jodi traverse une zone n'ont pas lieu en route, seulement quand elle y entre plus tard.
- Le bureau de Jodi, le niveau 3 et le stand de tir n'ont pas de tels lits.

## Objets {#objects}

Placer dans le monde des modèles du jeu, des armes et des modèles de mods (p. ex. les accessoires des mods de poses), les déplacer et les enregistrer en scène.

### Catalogue
- À gauche, CATALOGUE : Tous, ★ Favoris, les dossiers du jeu, « Du niveau : … », Armes et Mods (+ déplie les mods).
- À droite une recherche et les modèles en tuiles, triés par nom ; « Afficher plus » en charge d'autres. Images seulement avec « Charger » coché (décoché au départ) : AltUI les prend alors lui-même et les garde ; décoché, aucune image n'est chargée ni prise.
- Un clic sur une tuile pose le modèle au sol devant Jodi, fixe. Clic droit : favori, « Faire apparaître avec physique ».

### Modèles de mods
- AltUI trouve les modèles des mods en parcourant les mods une fois, dossier par dossier (le compteur est affiché en haut), et garde le résultat ; ensuite seuls les nouveaux mods sont parcourus.
- « Rechercher à nouveau dans les mods » recommence.
- Certains mods rangent des modèles dans des dossiers qui ne portent pas le nom de leur pak ; « Rechercher dans tous les dossiers de mods » les trouve (le jeu s'arrête environ une demi-minute).

### Objet sélectionné
- En bas le bloc « Sélectionné » : image, nom, fixe ou avec physique, désélectionner, physique on/off, au sol, copier, retirer.
- Champs pour la position, la rotation (lacet, tangage, roulis) et la taille – Entrée applique.
- L'objet sélectionné a un cadre jaune.

### Dans le monde
- MONDE › Dans le monde : une ligne par objet avec sélectionner (sur l'objet sélectionné : désélectionner), physique on/off, copier, retirer.
- « Positions » ouvre un bloc : un nom et « Enregistrer la position » gardent l'endroit, la rotation, la taille et la physique.
- La position apparaît pour chaque objet du même modèle dans le même niveau – un clic l'y place, clic droit : appliquer / supprimer.

### Scènes
- MONDE › Scènes : un nom et « Enregistrer la scène » gardent tous les objets du niveau ; le même nom dans le même niveau remplace.
- Seules les scènes du niveau actuel sont affichées. Un clic charge une scène et remplace les objets présents ; clic droit : charger / supprimer.
- Un modèle manquant (mod non installé) est ignoré et signalé.
- Les objets disparaissent avec le niveau ; une scène les ramène.

### Souris sur un objet
À côté du panneau et en mode ragdoll :
- Un clic le sélectionne.
- Glisser à gauche déplace un objet fixe à sa hauteur ; un objet avec physique est saisi, le relâcher le lance.
- Glisser à droite le tourne autour de son axe vertical, Maj + glisser à droite le tourne librement. Un objet avec physique reste immobile pendant ce temps puis retombe.
- La molette en glissant le monte ou le descend (aussi saisi avec physique) ; Ctrl + molette change sa taille.

## Compagnons {#followers}

Des looks devenus personnages du jeu : un compagnon accompagne Jodi, se bat et obéit aux ordres ; un PNJ reste où il est et se défend.

### Créer
- Dans l'onglet Looks, clic droit sur un look : « Créer en compagnon », « Créer en PNJ » ou « Créer en ennemi ». La figure apparaît devant Jodi avec ce look.
- Chaque figure porte le maquillage de son look et a une des voix de PNJ du jeu.
- Une figure créée avec AltUI avant la 2.2.0 montre le maquillage de Jodi jusqu'à ce que « Changer de look… » lui donne le sien.

### Ennemis issus de looks
- Un ennemi traque Jodi avec un pistolet (munitions infinies) et la blesse. Vos compagnons le combattent.
- Sa ligne est dans l'onglet Ennemis sous « Vivants », avec tout ce que propose l'onglet Compagnons (seulement dans son niveau) – à supprimer là-bas ou à transformer en compagnon.

### Jason
- « + Jason » (en bas à droite de l'onglet) ajoute Jason de l'histoire comme compagnon, avec son Glock. Il obéit aux ordres, suit et est sauvegardé.
- Il ne se bat qu'avec son propre Glock : un Glock qu'on lui donne devient le sien, il refuse les autres armes.
- Il n'a ni look, ni vêtements, ni maquillage ; à terre, il ne peut pas être soigné – « Ranimer » le ramène.

### La liste
- L'onglet « Compagnons » liste toutes les figures avec leur état (suit, attend, PNJ, inactif, tombé) et des puces.
- Les compagnons sont listés au-dessus des PNJ, une ligne sépare les deux groupes. Les puces au-dessus des lignes montrent tout, seulement les compagnons ou seulement les PNJ (conservé après un redémarrage).
- « ... » replie et déplie les tuiles de la figure (vêtements et sac) ; cela reste par figure, même après un redémarrage.
- Un clic sur une ligne sélectionne la figure.

### Puces
- « Suis-moi », « Attends ici », « Faire venir », → PNJ / → Compagnon.
- « Actif » désactivé retire la figure du monde avec tout ce qu'elle porte ; réactivée, elle revient devant Jodi.
- ∞ avec un cœur, « Invulnérable » : la figure ne peut pas mourir, sa santé se remplit après chaque coup. Elle montre quand même les réactions aux coups et ses vêtements s'abîment.
- ∞ avec des cartouches, « Munitions infinies » : la figure recharge ses armes à feu sans fin, sans avoir besoin de munitions dans son sac. Les armes à chargeur ne touchent pas à ses munitions ; le fusil à pompe et le lance-grenades utilisent d'abord ce qu'elle porte.

### Menu engrenage
- L'engrenage : attaquable / inattaquable, renommer, changer de look, ranimer, retirer.
- « Attaquable » : les zombies ne ciblent que les figures attaquables, invulnérables ou non. Après « Rendre inattaquable », les zombies et les mercenaires ne la prennent plus pour cible ; elle subit toujours des dégâts (indemne avec « Invulnérable »). Le réglage est enregistré ; les nouvelles figures sont attaquables.
- « Changer de look » passe à l'onglet Looks : cliquez sur le look que la figure doit porter.
- Une figure qui n'est pas invulnérable peut tomber. Elle reste dans la liste et « Ranimer » la ramène avec ses affaires. Les figures ne deviennent jamais des zombies.
- « Retirer » demande confirmation ; les objets et les armes de la figure vont dans la caisse, ses vêtements dans le sac à dos de Jodi.

### Objets
- En haut se trouvent le sac à dos (à gauche) et la caisse (à droite) : un clic donne un objet à la figure sélectionnée, une arme avec sa peinture et ses accessoires.
- Un clic sur une tuile de la figure le rend au sac à dos ; clic droit : tout, ou dans la caisse.
- « ... » au-dessus d'une liste la replie.
- Le menu contextuel d'une pile – de Jodi ou de la figure – a la ligne de quantité comme dans l'onglet Inventaire : « En donner 5 », « En prendre 5 », dans le coffre.

### Vêtements
- Les vêtements sont de vraies pièces de la figure, comme pour les PNJ du jeu : ils s'abîment, peuvent se déchirer et apparaissent dans l'inventaire PNJ du jeu, où l'on peut aussi les échanger.
- Sous une figure, ses pièces sont des tuiles (celles abîmées sont marquées) : un clic en enlève une et la met dans le sac à dos de Jodi.
- Clic droit : réparer avec un kit de couture du sac à dos de Jodi, ou tout réparer.
- Dans la colonne du sac à dos, « Vêtements » liste les pièces de Jodi : un clic en donne une à la figure sélectionnée, qui l'enfile (dégâts et couleurs suivent).
- Menu engrenage « Restaurer la tenue (sans kit de couture) » : la figure porte à nouveau exactement la tenue de son look, chaque pièce comme neuve, gratuitement – les pièces perdues (arrachées, retirées) reviennent, les autres vont dans son sac (compagnons, PNJ et ennemis).
- « Restaurer toutes les tenues » en bas à droite de l'onglet Compagnons le fait pour chaque figure de cet onglet.

### Sauvegarde et niveaux
- AltUI garde les figures dans une sauvegarde à part (AltUI_Followers.sav) ; la sauvegarde du jeu ne les contient jamais.
- Les compagnons qui suivent viennent dans chaque niveau et après un chargement.
- Ceux qui attendent et les PNJ restent dans leur niveau, à leur place.

### Menu rapide
- « Compagnon : suis-moi / attends ici » s'adresse au compagnon en vue, « Tous les compagnons : suivre / attendre » à tous.
- « Tous les compagnons : venez ici » amène chaque compagnon actif aux places devant Jodi – aussi celui qui attend dans un autre niveau.

### Figure en pose
- Le groupe du menu rapide « Figure : poses favorites » contient chacune de tes poses favorites sous la forme « Figure : <pose> ».
- L'entrée met la figure compagnon ou PNJ en vue dans cette pose (pas Jason).
- Elle ne marche ni ne combat alors, garde la pose même après des coups et ne se détourne pas.
- Si elle est attaquable, les zombies l'attaquent, et une figure qui n'est pas invulnérable peut mourir – de quoi monter des scènes.
- « Figure : arrêter la pose » la fait se relever ; ensuite elle suit ou attend comme avant. Un changement de niveau met fin à la pose.

## Codex {#kodex}

Trois pages :

- Encyclopédie : les entrées des archives de l'ordinateur du bureau de Jodi, avec image et texte. Seules celles que le jeu a débloquées sont affichées – ou toutes avec l'interrupteur dans Paramètres › Général.
- Mots de passe : les serrures à code du niveau actuel, la plus proche d'abord, avec leur distance et si elles sont verrouillées. Chaque code reste caché jusqu'à ce que vous cliquiez dessus.
- Manuel d'AltUI : ce texte.

## Télé {#tv}

La télé du niveau actuel, depuis le panneau.

### Quand elle apparaît
- Visible seulement quand le niveau actuel a une télé (le bureau de Jodi), ou toujours avec l'interrupteur dans Paramètres › Général.
- S'il y a plusieurs télés, c'est la plus proche de Jodi qui est commandée.

### Lecture
- Allumer / Éteindre agissent comme la touche E devant la télé.
- La télé lit sa liste de vidéos la première fois qu'elle est allumée – jusque-là, l'onglet vous demande de l'allumer une fois.
- « Lire » à côté d'une vidéo la lance ; celle en cours est mise en évidence.
- Une vidéo déjà commencée reprend là où elle s'était arrêtée, comme sur la télé elle-même.

### Vos propres vidéos
- Placez des fichiers .mp4 dans le dossier du jeu TheKillingAntidote/Videos/TV/.
- Elles apparaissent après le rechargement du niveau.

## Menu rapide {#quick}

Maintenez 4 (autre touche dans Actions) et une roue s'ouvre autour de la souris. Relâchez sur une entrée pour l'exécuter ; relâchez au centre pour ne rien faire.

### Entrées
- Tenues, looks, visages, préréglages d'apparence, poses, onglets et réglages d'autres mods.
- Actions : caméra libre, mode photo, mode ragdoll, une copie de Jodi en ragdoll, basculer tous les ragdolls entre actif et figé, activer / figer celui visé, retirer tous les ragdolls, vitesse personnalisée oui / non.
- « Ralenti oui / non ».
- « Arrêter le temps / reprendre » : tout s'immobilise ; le panneau et les caméras continuent de fonctionner, aussi la caméra du mode photo du jeu.
- « Masquer / afficher Jodi » (avec vêtements, cheveux et arme ; au niveau suivant elle est de retour).
- « Masquer / afficher l'interface du jeu » éteint et rallume le HUD du jeu, comme son mode photo.
- « +1 Main invisible » met une Main invisible dans le sac à dos (voir Inventaire › Tous les objets).
- Les ordres aux compagnons (voir « Compagnons »).

### Hauteur de la caméra
- « Hauteur de la caméra (molette) » : deux flèches apparaissent au centre de l'écran, et la molette monte ou descend la caméra au lieu de la rapprocher ou de l'éloigner.
- Un clic gauche ou Échap y met fin. La hauteur est conservée.

### L'onglet Actions
- On ajoute les entrées dans Actions, ou par clic droit sur une tuile, un onglet ou l'entrée d'un mod (« Ajouter au menu rapide »).
- À gauche : « Dans la roue » (touche, opacité, ordre avec ↑ ↓ ✕), « Touches personnelles », puis « Tous » et chaque groupe qui a des entrées – tenues, looks, visages, préréglages, poses, onglets, entrées de mods – et une ligne par mod avec des actions.
- À droite : les entrées de ce groupe avec une case (dans la roue ou non) et une recherche au-dessus. Chaque groupe garde sa position de défilement.
- L'ordre dans la roue est l'ordre de la liste dans Actions › Dans la roue.

### Touches personnelles
- Dans Actions, clic droit sur un élément sous « Disponibles » puis appuyez sur une touche – l'élément s'exécute alors avec cette touche, panneau fermé, aussi en caméra libre et dans le mode photo du jeu.
- Un clic sur la touche d'une ligne en choisit une autre, ✕ la supprime.
- La touche du panneau, celle du menu rapide et une touche déjà prise sont refusées ; une touche que le jeu utilise lui-même déclenche les deux.

## Pour les auteurs de mods {#modding}

Comment d'autres mods fonctionnent avec AltUI.

### Mods de vêtements, de corps et d'armes
- Les mods de vêtements n'ont besoin de rien de particulier : AltUI lit les tables du jeu et range chaque objet dans son emplacement.
- Les mods qui remplacent le corps ou une arme peuvent être convertis avec bodypak.pyz et weaponpak.pyz pour en installer plusieurs côte à côte.
- Ils peuvent aussi être faits pour AltUI directement dans l'Unreal Editor.

### Mods d'attente
- Un pak qui remplace l'animation d'attente de Jodi se convertit avec idlepak.pyz : python3 idlepak.pyz <mod>.pak.
- Le nouveau IdleAltUI_….pak va dans Mods/ et apparaît sous Paramètres › Déplacement › « Debout » ; l'attente du jeu reste.
- AltUI doit être installé : le convertisseur construit le nouveau pak en partie à partir d'AltUI.pak et le cherche dans les dossiers Steam habituels. S'il est ailleurs, indiquez le chemin avec --altui <chemin vers AltUI.pak>.

### Mods de marche et de course
- Un pak qui remplace l'animation de marche ou de course de Jodi se convertit avec walkpak.pyz : python3 walkpak.pyz <mod>.pak.
- Le nouveau WalkAltUI_….pak va dans Mods/ et apparaît dans Paramètres › Déplacement › « Style de marche » (et « Style de course » s'il apporte une course) ; la marche propre au jeu reste.
- walkpak refuse une animation sans les courbes de mouvement du jeu (MoveData_Speed, Rotation Speed) et indique laquelle manque.
- Comme idlepak, il a besoin d'AltUI.pak (--altui <chemin> s'il n'est pas dans les dossiers Steam habituels).

### Réglages dans l'onglet Mods
- Les mods peuvent afficher leurs réglages dans l'onglet Mods grâce à deux tables de données et une interface ; MOD_UI.md dans le dépôt du code source explique comment.
