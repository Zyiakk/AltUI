## À propos d'AltUI {#about}

AltUI est une alternative à la garde-robe et à l'écran d'apparence de The Killing Antidote : un seul panneau pour tout, et les écrans du jeu restent utilisables. Il s'ouvre n'importe où dans un niveau avec B – sans passer par la garde-robe ni le miroir.

Chaque objet du jeu et de tous les mods installés figure dans une liste par emplacement, avec recherche, filtres, favoris et masquage. Coiffure, maquillage, corps, visage, poses, armes ainsi que les tenues et looks enregistrés sont dans le même panneau, tout comme les ragdolls – des copies de Jodi, des zombies et des humains à placer et à poser – et la vitesse de marche et de course de Jodi.

Le panneau s'ouvre sur l'onglet où il a été fermé. Les onglets inutiles peuvent être désactivés dans Paramètres › Onglets.

Un onglet Inventaire déplace les objets entre le sac à dos de Jodi et l'hyper coffre de stockage, et les looks deviennent des compagnons et des PNJ qui marchent et se battent avec elle.

## Installation et mises à jour {#install}

AltUI.pak contient tout le mod et va dans TheKillingAntidote/Mods/. Un autre fichier le démarre :

- le Blueprint Loader (un petit mod séparé, TKA_BlueprintLoader.pak dans TheKillingAntidote/Content/Paks/~mods/), ou
- le hook propre à AltUI, AltUI_Hook_P.pak dans le même dossier ~mods/.

L'un des deux suffit ; les deux ensemble fonctionnent aussi. Avec AltUI.pak seul, B ne fait rien.

Une mise à jour ne remplace normalement que AltUI.pak. Le journal des modifications indique quand le hook change aussi ; un ancien hook ne doit pas rester dans ~mods/.

Pour retirer AltUI, supprimez les fichiers copiés :

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
- le dossier AltUI – photos des looks, des visages et des préréglages d'apparence
- le dossier WeaponIcons – images des armes

Les vêtements, tenues, maquillage et coiffure sont enregistrés dans les sauvegardes du jeu et restent.

Après une mise à jour du jeu, ou avec un mod qui remplace des tables du jeu, AltUI peut tomber sur un jeu pour lequel il n'a pas été conçu. Il affiche alors un avertissement avant de faire quoi que ce soit : « Continuer quand même (à mes risques) » est retenu pour cette version du jeu, « AltUI désactivé pour l'instant » redemande au niveau suivant.

## Commandes {#controls}

- B ouvre et ferme le panneau (autre touche dans Paramètres › Commandes) ; Échap le ferme.
- Le clic gauche sélectionne, porte ou applique ; le clic droit ouvre le menu contextuel d'une tuile, d'une ligne ou d'un onglet.
- La molette fait défiler ; la vitesse se règle dans Paramètres › Commandes.
- Tant que le panneau est ouvert, Jodi ne peut pas marcher. Faire glisser sur le fond tourne la caméra ; cliquer sur Jodi et faire glisser la tourne – elle revient à sa position à la fermeture du panneau.
- + et − changent la distance de la caméra par pas de 5 %, la molette au-dessus de Jodi par pas de 4 %.
- Les trois boutons ronds au-dessus de + et − ouvrent une caméra libre (la souris tourne, W A S D et Q E déplacent, Maj plus vite, la molette règle la vitesse, Échap revient), le mode photo du jeu (Échap revient) et le mode ragdoll (voir « Mode ragdoll »).
- Annuler et Rétablir (cinq étapes) sont dans la barre d'état en bas.
- Maintenez 4 pour le menu rapide (voir « Menu rapide »).
- Dans le menu principal, B ouvre un petit menu : les trois scènes du menu et la scène de chargement, la caméra suivante, et masquer le menu et les textes du jeu (Échap les rétablit).

## Vêtements {#clothes}

À gauche les emplacements, à droite les objets de l'emplacement choisi.

- Un clic sur un objet le fait porter, un clic sur un objet porté le retire.
- Les puces au-dessus de la liste filtrent par mod ou par groupe ; « ... » replie les rangées de puces. Un champ de recherche réduit les puces, la recherche au-dessus de la liste trouve les objets par nom, mod ou groupe.
- Filtres : possédés seulement, favoris seulement, vanilla seulement, portés seulement.
- Clic droit sur un objet : favori, masquer, couleur via la palette du jeu, réinitialiser la couleur, mettre dans le sac à dos, renommer, seulement ce groupe, voir le contenu du mod, afficher dans l'onglet.
- L'info-bulle indique de quel mod vient un objet.
- Dégâts (dans le menu contextuel) : de 0 à 100 %, en direct sur un vêtement porté ; sur tout autre vêtement, ils sont gardés jusqu'à ce qu'il soit porté. Les vêtements portés sans textures de dégâts n'ont pas de curseur.
- Sous la palette de couleurs du jeu, un champ affiche la couleur en #RRGGBB ; tapez un code et appuyez sur Entrée pour l'appliquer. « Mémoriser » garde la couleur dans AltUI, « Utiliser » la pose sur un autre vêtement ou emplacement.
- La recherche trouve aussi un mod par le nom de son pak, ici et dans tous les autres onglets.

## Tenues {#outfits}

Les tenues enregistrées du jeu – les mêmes que celles de la garde-robe et du miroir.

- La tuile « + » enregistre ce que Jodi porte comme nouvelle tenue.
- Un clic sur une tenue la fait porter.
- Clic droit : porter, voir le contenu, ajouter au menu rapide ou l'en retirer, renommer, déplacer à gauche / à droite / au début / à la fin, supprimer.
- Une tenue sans nom propre s'affiche comme « Tenue » suivie de sa place dans la liste.
- La taille des tuiles et le nombre d'objets affichés par tuile se règlent dans Paramètres › Tuiles.

## Looks {#looks}

Un look, c'est tout à la fois : vêtements avec leurs couleurs, coiffure et couleur des cheveux, maquillage, yeux, peau, curseurs du corps, mod de corps et visage.

- La tuile « + » enregistre le look actuel avec une photo en pied – de face ou telle que vous la voyez.
- Un clic sur un look l'applique.
- Clic droit : voir le contenu, renommer, mettre à jour (photo de face ou telle que vue), déplacer, supprimer, ajouter au menu rapide ou l'en retirer.
- Clic droit aussi : « Créer en ragdoll », « Créer en compagnon », « Créer en PNJ » (voir « Ragdolls » et « Compagnons »).

## Sac à dos {#bag}

Ce que Jodi porte et ce qu'elle transporte.

- Un clic sur un objet porté le retire, un clic sur un objet transporté le fait porter.
- Clic droit : porter ou retirer, réparer (il faut un kit de couture), retirer du sac à dos, vers la garde-robe.
- « Ranger le sac à dos » retire les objets qui ne sont pas portés et qui sont aussi dans la garde-robe.
- « Tout dans le sac à dos » retire chaque objet porté et le met dans le sac à dos.
- Le menu contextuel a aussi le curseur de dégâts (voir « Vêtements »).

## Inventaire {#inventory}

Les objets de Jodi et l'hyper coffre de stockage, une liste sous l'autre.

- Les puces filtrent par les groupes du jeu (armes, munitions, accessoires d'armes, outils…). Le poids montre ce que Jodi porte, ce qu'elle peut porter et de combien elle est en surcharge.
- Un clic met un objet dans le coffre ou en sort un. Clic droit : la moitié ou tout, utiliser, examiner, jeter, raccourci 1 ou 2, décharger, « Accessoires… » (ouvre l'arme dans l'onglet Armes).
- Le menu contextuel d'une pile se termine par « Quantité » : un curseur et un champ numérique, puis une entrée par destination avec ce nombre (« Ranger 5 dans le coffre », « En prendre 5 »). Entrée dans le champ exécute la première entrée. Dans le catalogue, le nombre compte des unités et le champ accepte plus que le curseur. Les armes à feu et les objets uniques n'ont pas de quantité.
- « Tout jeter » pose un objet au sol par paquet. À partir de 100 objets, une fenêtre demande d'abord : « Annuler », « Détruire à la place » (les objets disparaissent, rien ne tombe) ou « Jeter quand même » – autant d'objets physiques à la fois peuvent faire planter le jeu. Échap annule.
- Tout passe par les fonctions du jeu lui-même, ses règles restent donc – surcharge comprise.
- « ... » au-dessus d'une liste la replie, ↑↓ lui donne toute la hauteur (encore une fois : retour).
- Sur les cartes où le jeu ne sauvegarde jamais le sac à dos (le stand de tir, par exemple), l'onglet le signale : gardez ce que vous voulez conserver dans le coffre.
- « Tous les objets » est désactivé par défaut (Paramètres › Général) : chaque objet du jeu en troisième liste, avec sa propre recherche. Un clic met un paquet dans le sac à dos ; clic droit : cinq, ou dans le coffre.
- « Équiper automatiquement les armes » (Paramètres › Général, activé par défaut) : une arme sortie du coffre ou du catalogue va dans la main de Jodi comme dans le jeu ; désactivé, elle garde ce qu'elle tient.
- La taille des tuiles de cet onglet se règle dans Paramètres › Tuiles.

## Coiffure {#hair}

Toutes les coiffures du jeu et des mods.

- Un clic sur une coiffure la met.
- « Couleur des cheveux... » ouvre la palette du jeu ; « Couleurs naturelles » propose 14 couleurs prêtes.
- Clic droit : ajouter aux / retirer des favoris, réinitialiser la couleur des cheveux, renommer, voir le contenu du mod.
- Les favoris sont en haut, au-dessus de toutes les coiffures.
- Clic droit sur une coiffure issue d'un mod : « Renommer le mod… ».

## Poses {#poses}

Chaque animation d'action que connaissent le jeu et vos mods de poses – la liste derrière l'application « rythme » du téléphone.

- Un clic sur une pose la joue ; un nouveau clic ou « Arrêter la pose » l'arrête.
- Les poses sont triées par posture (debout, assise, allongée) et par chapitre ; les puces filtrent par mod, la recherche trouve les titres.
- Clic droit : favori, masquer, classer comme debout / assise / allongée / en mouvement, renommer, ajouter au menu rapide.
- Clic droit « Utiliser au repos » : la pose commence après 1,5 s d'immobilité et s'arrête quand Jodi marche, sort une arme ou s'accroupit ; « Plus au repos » la désactive.
- « Tout mesurer » joue une fois chaque pose qui n'a pas encore de posture et la classe.
- Un haut-parleur dans le coin d'une tuile signale une pose avec son.

## Armes {#weapons}

À gauche, une entrée par arme, armes de mêlée comprises. Pour chaque arme, le modèle, le skin et le son du tir se choisissent séparément.

- En haut les modèles – celui du jeu et chaque mod de modèle installé.
- En bas les skins – les peintures d'armes du jeu (sans bombe de peinture) et chaque mod de skin installé.
- Son : le son de tir propre à l'arme (« Original ») et chaque son de tir installé pour elle. Un clic choisit le son et le joue ; toutes les autres armes gardent le leur. Un silencieux monté avec son propre son reste prioritaire.
- Les puces au-dessus filtrent les trois sections à la fois. Clic droit sur une tuile : favori, masquer, seulement ce mod.
- Le choix est conservé et réappliqué quand l'arme est ramassée ou sortie de la caisse de rangement.
- Une peinture appliquée dans le jeu avec une bombe de peinture est conservée : elle devient le skin choisi.
- Clic droit sur un modèle de mod : forcer les skins dessus, exclure le chargeur, la visée, le silencieux ou la poignée, afficher l'image propre au mod.
- Les mods d'armes et de sons de tir doivent d'abord être convertis avec weaponpak.pyz ; voir le guide WEAPON_MODS sur la page du mod.
- Accessoires d'armes : une ligne par emplacement de l'arme (viseur, canon, poignée, chargeur), « Aucun » en premier. Les pièces viennent du sac à dos, ou du coffre de stockage et passent alors dans le sac à dos. Les accessoires ne vont que sur les armes que Jodi porte sur elle ; l'arme garde le modèle, le skin et le son choisis ici.
- « Afficher les images d'objet » dans la barre d'état met sur chaque tuile l'image propre de l'objet ou du mod au lieu de l'image rendue.
- Clic droit sur un modèle, un skin ou un son issu d'un mod : « Renommer le mod… ».

## Apparence {#look}

Peau, chaque type de maquillage, yeux et préréglages d'apparence du jeu.

- Un clic sur une entrée l'applique. Clic droit sur un maquillage : teinter avec la palette du jeu, réinitialiser la teinte.
- Yeux : couleur de l'iris et des cils dans le menu contextuel.
- Préréglages : la tuile « + » enregistre l'apparence actuelle avec une photo. Clic droit : appliquer, voir le contenu, renommer, mettre à jour, déplacer, supprimer, menu rapide.

## Morphologie {#body}

- Les curseurs de poitrine et de taille du jeu.
- Les puces passent du corps du jeu à chaque mod de corps converti.
- Les corps convertis ont en plus des curseurs d'os : échelle, buste, taille, fessiers et hanches, cuisses, mollets, bras, mains, pieds. Ils sont conservés par corps ; « Réinitialiser la forme » les remet à zéro.
- Poitrine et fessiers et hanches : rebond (0 % = animation seule) règle la physique du jeu et fonctionne avec tous les corps ; un soutien-gorge amortit toujours comme dans le jeu. Le curseur des tétons n'agit que si la poitrine est découverte. Angle et largeur des hanches n'existent que pour les corps convertis ; l'angle agit d'autant plus qu'il y a moins de rebond (pas du tout à 100 %).
- Les mods qui remplacent le corps doivent d'abord être convertis avec bodypak.pyz ; voir le guide BODY_MODS sur la page du mod.

## Visage {#face}

L'expression du visage de Jodi.

- Curseurs pour les expressions du jeu (détendue, concentrée, sourire, douleur, frayeur, fatiguée, souffrance), le regard et les formes de la bouche.
- « Yeux fermés » (sous Regard) ferme les yeux, d'ouverts à complètement fermés ; le clignement des yeux du jeu continue comme d'habitude. Seulement avec les corps convertis, comme les curseurs du corps.
- Une entrée cochée garde sa valeur, même pendant les poses ; une entrée non cochée est laissée à l'animation du jeu. « Tout fixer » et « Tout au jeu » basculent toutes les entrées à la fois.
- Les expressions sont mélangées (ensemble au plus 100 %) ou additionnées.
- La tuile « + » enregistre le visage actuel avec une photo. Clic droit : appliquer, voir le contenu, renommer, mettre à jour, déplacer, supprimer.

## Mods {#mods}

Les réglages d'autres mods qui s'enregistrent auprès d'AltUI : à gauche leurs entrées, à droite les interrupteurs, curseurs, nombres, choix, couleurs, champs de texte, touches et boutons de celui qui est choisi.

Cet onglet n'apparaît que si un tel mod est installé.

## Paramètres {#options}

À gauche, les catégories.

- Général : langue, part de l'écran laissée libre pour Jodi, autoriser à retirer les sous-vêtements, affichage des objets non possédés, l'interrupteur du Codex pour l'encyclopédie, le catalogue « Tous les objets » et « Équiper automatiquement les armes » pour l'onglet Inventaire.
- Tuiles : taille des tuiles, tailles propres pour les tuiles de tenues, de looks et de ragdolls, objets par tuile de tenue, pas de limite pour les longues listes, détails des info-bulles, la taille des tuiles de l'onglet Inventaire.
- Groupes : fusionner les groupes ou les mods de même nom, longueur des noms de groupe, hauteur de la zone des puces, recherche dans les puces.
- Caméra : champ de vision, distance, hauteur, la caméra suit l'emplacement choisi.
- Commandes : touche du panneau, vitesse de défilement, hauteur de la caméra avec le bouton droit, de combien la molette soulève un ragdoll par cran.
- Déplacement : vitesse de marche et de course propre à Jodi (50 à 200 %) ; s'accroupir et sauter restent inchangés. « Ralenti activé » allume le ralenti, « Vitesse du ralenti » (5 à 90 %, 25 % par défaut) règle sa lenteur ; l'entrée du menu rapide « Ralenti oui / non » fait la même chose que l'interrupteur. « Valeurs par défaut » remet les vitesses de marche, de course et du ralenti. « Debout » choisit l'animation au repos de Jodi : celles du jeu (regarde autour, regarde ses ongles, regarde sa jambe, prudente, blessée, pose) et celles des mods de repos installés (IdleAltUI_…).
- Menu rapide : sa touche, son opacité, ce qui figure dans la roue, les touches personnelles.
- Couleurs : chaque couleur du panneau, opacités, schémas de couleurs enregistrés sous un nom.
- Conflits d'emplacements : séparer les paires d'emplacements du jeu (par exemple soutien-gorge et chemise) pour pouvoir porter les deux.
- Onglets : texte, icônes ou les deux dans la barre d'onglets ; désactiver des onglets.

## Gestion {#manage}

Vos propres noms d'affichage pour les mods, groupes, vêtements, coiffures, peaux, maquillages, poses et préréglages d'apparence.

- Les noms sont utilisés partout dans le panneau et trouvés par la recherche ; l'identifiant d'origine reste cherchable et apparaît dans l'info-bulle.
- Des puces et une recherche filtrent la liste ; « seulement les mods » masque les entrées du jeu ; ↺ revient au nom par défaut.
- Avec altui_names.pyz, les noms peuvent être exportés dans un fichier texte puis réimportés.
- Les mods d'armes figurent avec les autres mods.

## Ragdolls {#ragdolls}

Des figures avec physique à placer et à poser dans le niveau : copies de Jodi, zombies et humains.

- « + Créer une copie de Jodi » place une copie devant elle, debout et figée dans sa pose actuelle, avec tout ce qu'elle porte. Un look devient une figure avec « Créer en ragdoll » dans son menu contextuel.
- « Zombies et humains » : une tuile illustrée par type de zombie, plus l'infirmière et une survivante. Un clic la crée ; les liens sous une tuile créent ses variantes.
- Chaque figure a sa ligne : active (physique, elle tombe et peut être lancée) ou figée (elle garde sa pose), « articulations › », tout bloquer, tout libérer, retirer. « Tout retirer » retire toutes les figures.
- « articulations › » déplie les 17 articulations de la figure, chacune bloquée, libre ou mobile. Une articulation bloquée reste rigide tant que la figure est active.
- Poses (dans la ligne dépliée) : un nom et « enregistrer la pose » retiennent la position des parties du corps. Une pose se charge sur toute figure du même type, dans tous les niveaux – un clic charge, clic droit : charger / supprimer. La figure se fige et se tient sur le sol.
- Scènes : « Enregistrer la scène sous » retient chaque figure du niveau avec son apparence, sa place, sa pose et ses articulations ; le même nom dans le même niveau remplace l'ancienne. Seules les scènes du niveau actuel sont affichées. Un clic charge une scène et remplace les figures présentes ; clic droit : charger / supprimer.

Avec la souris sur une figure, à côté du panneau et en mode ragdoll :

- Glisser avec le bouton gauche une figure figée la déplace sur le sol ; la molette la lève ou l'abaisse pendant le glissement.
- Glisser avec le bouton gauche une figure active saisit la partie du corps sous la souris ; relâchez et elle tombe.
- Glisser avec le bouton droit tourne la figure autour de ses hanches.
- Maj + clic gauche bloque ou libère l'articulation cliquée.
- Maj + clic droit sur une figure figée rend l'articulation mobile. Glisser ensuite avec le bouton gauche une partie du corps sous une articulation mobile ne déplace que cette partie ; elle reste là où vous la lâchez – c'est ainsi qu'on pose une figure.

Sans le panneau, le menu rapide active ou fige les figures : « Ragdoll : activer / figer celle visée » prend la figure au centre de l'écran, « Ragdolls : actifs / figés » les bascule toutes.

## Mode ragdoll {#ragmode}

Déplacer et poser les figures sans le panneau, la caméra libre dans la pièce. On le lance avec le troisième bouton rond au-dessus de + et − ou depuis le menu rapide.

- Le pointeur de la souris reste visible ; sur une figure tout fonctionne comme à côté du panneau (voir « Ragdolls »).
- W A S D et Q E déplacent la caméra, Maj plus vite ; Maj + molette règle la vitesse.
- Glisser dans le vide tourne la caméra.
- Échap ou B quitte le mode.

## Compagnons {#followers}

Des looks devenus personnages du jeu : un compagnon accompagne Jodi, se bat et obéit aux ordres ; un PNJ reste où il est et se défend.

- Dans l'onglet Looks, clic droit sur un look : « Créer en compagnon » ou « Créer en PNJ ». La figure apparaît devant Jodi avec ce look.
- L'onglet « Compagnons » liste toutes les figures avec leur état (suit, attend, PNJ, inactif, tombé) et des puces : « Suis-moi », « Attends ici », « Faire venir », → PNJ / → Compagnon, « Actif », « Invulnérable » et « ... » (renommer, changer de look, ranimer, retirer).
- Un clic sur une ligne sélectionne la figure. En haut se trouvent le sac à dos (à gauche) et la caisse (à droite) : un clic donne un objet à la figure sélectionnée, une arme avec sa peinture et ses accessoires. Un clic sur une tuile de la figure le rend au sac à dos ; clic droit : tout, ou dans la caisse. « ... » au-dessus d'une liste la replie.
- Le menu contextuel d'une pile – de Jodi ou de la figure – a la ligne de quantité comme dans l'onglet Inventaire : « En donner 5 », « En prendre 5 », dans le coffre.
- Les vêtements sont de vraies pièces de la figure, comme pour les PNJ du jeu : ils s'abîment, peuvent se déchirer et apparaissent dans l'inventaire PNJ du jeu, où l'on peut aussi les échanger. Sous une figure, ses pièces sont des tuiles (celles abîmées sont marquées) : un clic en enlève une et la met dans le sac à dos de Jodi ; clic droit : réparer avec un kit de couture du sac à dos de Jodi, ou tout réparer. Dans la colonne du sac à dos, « Vêtements » liste les pièces de Jodi : un clic en donne une à la figure sélectionnée, qui l'enfile (dégâts et couleurs suivent).
- « Actif » désactivé retire la figure du monde avec tout ce qu'elle porte ; réactivée, elle revient devant Jodi.
- Une figure qui n'est pas invulnérable peut tomber. Elle reste dans la liste et « Ranimer » la ramène avec ses affaires. Les figures ne deviennent jamais des zombies.
- « Retirer » demande confirmation ; les objets et les armes de la figure vont dans la caisse, ses vêtements dans le sac à dos de Jodi.
- « Changer de look » passe à l'onglet Looks : cliquez sur le look que la figure doit porter.
- Chaque figure porte le maquillage de son look et a une des voix de PNJ du jeu. Une figure créée avec AltUI avant la 2.2.0 montre le maquillage de Jodi jusqu'à ce que « Changer de look… » lui donne le sien.

AltUI garde les figures dans une sauvegarde à part (AltUI_Followers.sav) ; la sauvegarde du jeu ne les contient jamais. Les compagnons qui suivent viennent dans chaque niveau et après un chargement ; ceux qui attendent et les PNJ restent dans leur niveau, à leur place.

Menu rapide : « Compagnon : suis-moi / attends ici » s'adresse au compagnon en vue, « Tous les compagnons : suivre / attendre » à tous.

## Codex {#kodex}

- Encyclopédie : les entrées des archives de l'ordinateur du bureau de Jodi, avec image et texte. Seules celles que le jeu a débloquées sont affichées – ou toutes avec l'interrupteur dans Paramètres › Général.
- Mots de passe : les serrures à code du niveau actuel, la plus proche d'abord, avec leur distance et si elles sont verrouillées. Chaque code reste caché jusqu'à ce que vous cliquiez dessus.
- Manuel d'AltUI : ce texte.

## Menu rapide {#quick}

Maintenez 4 (autre touche dans Paramètres › Menu rapide) et une roue s'ouvre autour de la souris. Relâchez sur une entrée pour l'exécuter ; relâchez au centre pour ne rien faire.

- Entrées : tenues, looks, visages, préréglages d'apparence, poses, onglets, réglages d'autres mods et actions : caméra libre, mode photo, mode ragdoll, une copie de Jodi en ragdoll, basculer tous les ragdolls entre actif et figé, activer / figer celui visé, retirer tous les ragdolls, vitesse personnalisée oui / non.
- Autres actions : « Ralenti oui / non », « Arrêter le temps / reprendre » (tout s'immobilise ; le panneau et les caméras continuent de fonctionner ; aussi la caméra du mode photo du jeu), « Masquer / afficher Jodi » (avec vêtements, cheveux et arme ; au niveau suivant elle est de retour) et les ordres aux compagnons (voir « Compagnons »).
- « Masquer / afficher l'interface du jeu » éteint et rallume le HUD du jeu, comme son mode photo.
- Touches personnelles : dans Paramètres › Menu rapide, clic droit sur un élément sous « Disponibles » puis appuyez sur une touche – l'élément s'exécute alors avec cette touche, panneau fermé, aussi en caméra libre et dans le mode photo du jeu. Un clic sur la touche d'une ligne en choisit une autre, ✕ la supprime. La touche du panneau, celle du menu rapide et une touche déjà prise sont refusées ; une touche que le jeu utilise lui-même déclenche les deux.
- On les ajoute dans Paramètres › Menu rapide, ou par clic droit sur une tuile, un onglet ou l'entrée d'un mod (« Ajouter au menu rapide »).
- L'ordre dans la roue est l'ordre de la liste dans Paramètres › Menu rapide.

## Pour les auteurs de mods {#modding}

- Les mods de vêtements n'ont besoin de rien de particulier : AltUI lit les tables du jeu et range chaque objet dans son emplacement.
- Les mods qui remplacent le corps ou une arme peuvent être convertis avec bodypak.pyz et weaponpak.pyz pour en installer plusieurs côte à côte ; ils peuvent aussi être faits pour AltUI directement dans l'Unreal Editor.
- Les mods d'attente (un pak qui remplace l'animation d'attente de Jodi) se convertissent avec idlepak.pyz : python3 idlepak.pyz <mod>.pak. Le nouveau IdleAltUI_….pak va dans Mods/ et apparaît sous Paramètres › Déplacement › « Debout » ; l'attente du jeu reste. AltUI doit être installé : le convertisseur construit le nouveau pak en partie à partir d'AltUI.pak et le cherche dans les dossiers Steam habituels ; s'il est ailleurs, indiquez le chemin avec --altui <chemin vers AltUI.pak>.
- Les mods peuvent afficher leurs réglages dans l'onglet Mods grâce à deux tables de données et une interface ; MOD_UI.md dans le dépôt du code source explique comment.
