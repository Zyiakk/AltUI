# AltUI – panneau de garde-robe et d'apparence

Version française de la description de la [fiche du Steam Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3802875867). La [version anglaise](description.en.md) fait foi ; la page du Workshop elle-même n'en montre qu'un résumé.

La garde-robe du jeu donne à chaque auteur de mod son propre onglet : avec quelques mods de vêtements, un même type de pièce se retrouve éparpillé sur une douzaine d'onglets, sans aucun moyen de chercher. AltUI range chaque pièce du jeu et de tous les mods installés dans **une liste par emplacement** (hauts, jupes, chaussures, …), avec recherche, filtres, favoris et masquage – et réunit coiffure, maquillage, corps et tenues dans le même panneau. Il s'ouvre n'importe où dans un niveau avec **B** ; plus besoin d'aller à la garde-robe ou au miroir.

Aussi sur [Nexus Mods](https://www.nexusmods.com/thekillingantidote/mods/988) (les deux fichiers dans une seule archive). C'est le même mod – choisissez une source, pas les deux.

> ⚠️ **Attention :** conçu pour la version 0.6.x du jeu. Une mise à jour du jeu qui modifie les tables de vêtements / de maquillage ou le gestionnaire de caméra peut casser le mod. Au démarrage, AltUI vérifie les tables du jeu et, si elles ont changé, avertit avant de toucher à quoi que ce soit.

## ⚠ Installation – à lire d'abord

L'abonnement installe le mod lui-même, **AltUI.pak**. Un fichier de plus doit le démarrer, et le Workshop ne peut pas le placer pour vous, car il va dans un dossier du jeu auquel le Workshop ne touche pas. Sans lui, **B ne fait rien**. Deux façons de faire – choisissez-en une ; les deux ensemble fonctionnent aussi.

**1. Avec le Blueprint Loader (AltUI ne remplace rien du jeu)**

1. Abonnez-vous à cet élément.
2. Récupérez **TKA_BlueprintLoader.pak** sur https://www.nexusmods.com/thekillingantidote/mods/994
3. Copiez-le dans
   `Steam\steamapps\common\TheKillingAntidote\TheKillingAntidote\Content\Paks\~mods\`
   Créez le dossier **~mods** s'il n'existe pas (le nom commence par un tilde). Le nom du dossier du jeu apparaît deux fois dans le chemin – c'est normal.
4. Lancez le jeu, appuyez sur B dans un niveau.

AltUI contient une table que le loader lit, et le loader démarre le panneau à partir d'elle. Le même loader démarre tout autre mod qui fournit une telle table : c'est donc la voie à suivre si vous en utilisez plusieurs.

**Mise à jour depuis un ancien AltUI : s'il reste un AltUI_Hook_P.pak dans ~mods, supprimez-le. Le hook s'approprie la classe du gestionnaire de caméra, et un hook antérieur à 1.5.0 ne démarre pas le loader – le panneau s'ouvrirait sans que la vue se décale, et les mods conçus pour le loader resteraient inactifs.**

**2. Avec le pak hook (un seul fichier, de la release AltUI)**

1. Abonnez-vous à cet élément.
2. Téléchargez **AltUI_Hook_P.pak** : https://github.com/Zyiakk/AltUI/releases/latest/download/AltUI_Hook_P.pak
3. Copiez-le dans le même dossier *~mods* que ci-dessus.
4. Lancez le jeu, appuyez sur B dans un niveau.

Le hook remplace *TKA_PlayerCameraManager* et démarre le panneau depuis là. Tout mod qui remplace le même blueprint entre en conflit avec lui – le Blueprint Loader en fait partie, et cette paire est l'exception : avec les deux installés, le hook prend la classe et démarre lui-même le loader, si bien que les mods qui ont besoin du loader continuent de fonctionner.

**« Je suis abonné mais B ne fait rien »** → rien n'a démarré le panneau : soit le second fichier manque, soit il se trouve dans *Mods* ou dans le dossier du Workshop au lieu de *Content\Paks\~mods*.

## Ce qu'il fait

* **Menu rapide** – maintenez **4** (modifiable) et une roue s'ouvre avec ce que vous utilisez le plus : caméra libre, mode photo, une tenue, un look, un visage ou un préréglage enregistré, une pose favorite, un onglet et des actions d'autres mods. Jusqu'à 32 éléments, choisis et ordonnés dans les Paramètres ; relâchez sur l'un d'eux pour le lancer. Un clic droit sur une tuile, un onglet ou l'entrée d'un mod l'ajoute à la roue ou l'en retire. Aussi : ralenti, arrêt du temps, masquer Jodi et ordres aux compagnons. Chaque élément peut aussi recevoir sa propre touche (Touches personnelles).
* **Vêtements** – chaque pièce du jeu et de vos mods, une liste par emplacement, avec recherche, filtres, favoris et masquage. Curseur de dégâts dans le menu contextuel ; une couleur par emplacement de matériau, bijoux compris, gardée par sauvegarde.
* **Tenues · Looks** – les tenues du jeu avec des noms, et des looks complets (vêtements avec couleurs, coiffure, maquillage, yeux, peau, corps, visage) enregistrés avec une photo prise en jeu. Un look peut apparaître comme compagnon, PNJ ou ragdoll. « Copie nettoyée » laisse de côté ce qui n'est plus installé. Une tenue enregistrée dans AltUI garde les couleurs de chaque canal de couleur.
* **Sac à dos · Coiffure · Apparence** – ce que Jodi porte et transporte ; coiffures et couleurs de cheveux ; peau, maquillage et yeux, chacun teintable. Coiffures favorites en haut.
* **Inventaire** – les objets de Jodi et l'Hyper coffre de stockage l'un sous l'autre : un clic déplace un objet ; clic droit pour utiliser, examiner, jeter ou décharger ; tout passe par les fonctions du jeu. En option : un catalogue « Tous les objets ». Un curseur choisit n'importe quelle quantité d'une pile ; avant que de très nombreux objets ne tombent au sol, un avertissement demande d'abord.
* **Morphologie** – curseurs poitrine / taille, un sélecteur pour les mods de corps convertis, des curseurs d'échelle des os par corps. Pour la poitrine et les fesses : rebond, angle et largeur des hanches.
* **Visage** – l'expression, le regard et la bouche de Jodi en curseurs ; le visage tient pendant les poses et la danse ; visages enregistrés avec une photo, leurs valeurs sous « Voir le contenu ». « Yeux fermés » avec les corps convertis.
* **Armes** – un modèle, un skin et un son de tir par arme, armes de mêlée comprises, côte à côte depuis tous les mods d'armes, avec une image rendue sur chaque tuile ; un clic sur un son le joue. Accessoires par emplacement (viseur, canon, poignée, chargeur) depuis le sac à dos ou le coffre.
* **Poses** – chaque animation d'action du jeu et des mods de poses, triées en debout, assise et allongée. « Répéter les poses » pour les poses qui se terminent d'elles-mêmes.
* **Mods** – les réglages des autres mods qui s'y enregistrent : interrupteurs, curseurs, nombres, choix, couleurs, champs de texte, lignes d'info, touches et boutons. Affiché seulement quand un tel mod est installé.
* **Paramètres** – rangés en catégories choisies dans une liste à gauche : touche du panneau, langue, couleurs (les thèmes peuvent être enregistrés sous un nom), une barre d'onglets avec icônes, texte ou les deux, et la taille des tuiles, réglable à part pour les tenues et les looks. Plusieurs pièces peuvent partager un emplacement (chaussettes hautes sur collants). Les onglets inutiles peuvent être désactivés. Une caméra libre sans collision et à n'importe quelle distance ; « Aucun avis » masque les avis d'AltUI et du jeu.
* **Thème** – couleurs avec leur opacité, une image de fond derrière le panneau (remplir, ajuster, étirer ou en mosaïque, alignée, avec teinte, sépia et inversion, opacité propre) et une image pour les tuiles et les onglets aux coins arrondis ; images d'AltUI – dont des papiers cartonnés blanc cassé – ou les vôtres ; les thèmes enregistrés sous un nom gardent tout cela. Aperçus sur les puces d'image si tu le souhaites.
* **Gestion** – vos propres noms affichés pour les mods, les groupes et les pièces. Comme dans Vêtements, des puces filtrent la liste par mod ou par groupe, et un champ de recherche réduit les puces.
* **Ragdolls** – des copies de Jodi, des zombies et des humains comme figures avec physique : les placer, les poser articulation par articulation, les figer ou les laisser tomber ; les poses par type de figure et des scènes entières par niveau sont enregistrées. Pendant le glisser, un clic droit fige une partie en l'air, comme le pistolet physique ; des sphères aux articulations montrent où saisir une figure. Un mode ragdoll les déplace sans le panneau. Le mercenaire aussi, fusil en main.
* **Compagnons** – les looks deviennent des compagnons qui marchent et combattent avec Jodi, ou des PNJ qui restent sur place : ordres, objets et armes à donner, vêtements qui s'abîment comme ceux des PNJ du jeu. Gardés dans leur propre fichier, jamais dans la sauvegarde du jeu. Chaque figure porte le maquillage de son look et a une voix. « Tous les compagnons : venez ici » depuis le menu rapide.
* **Codex** – le manuel d'AltUI dans les sept langues, l'encyclopédie du jeu et les serrures à code du niveau actuel ; chaque code reste caché jusqu'au clic.
* **Déplacement** – vitesse de marche et de course propre à Jodi (50–200 %), dans Paramètres. Ralenti avec sa propre vitesse. Comment Jodi se tient : six autres animations d'attente du jeu, des mods d'attente ou une pose comme attente.
* Annuler / rétablir (5 étapes), infobulles indiquant de quel mod vient une pièce.

Langues : anglais, allemand, chinois, russe, espagnol, polonais, français (détectée automatiquement, modifiable dans les Paramètres).

## Commandes

* **B** – ouvrir / fermer (modifiable dans les Paramètres). **Échap** ferme.
* **4** – maintenir pour le menu rapide (modifiable dans les Paramètres) ; relâchez sur un élément pour le lancer, ou au centre pour ne rien faire.
* **B dans le menu principal** – un petit menu : les scènes du menu, la scène de chargement, la caméra suivante et masquer le menu du jeu.
* Clic gauche – choisir / porter / appliquer. Clic droit – menu contextuel. Molette – défiler.

## Mods de corps

Les paks qui remplacent le corps écrasent tous le même fichier du jeu, donc un seul peut être actif. Un petit convertisseur transforme un remplaçant en pak de mod ordinaire qui garde le maillage sous son propre chemin ; autant de corps convertis que vous voulez peuvent être installés côte à côte et apparaissent comme puces dans l'onglet Morphologie.

Guide (Windows, Linux) : [BODY_MODS.md](https://github.com/Zyiakk/AltUI/blob/main/BODY_MODS.md) · bodypak.pyz : https://github.com/Zyiakk/AltUI/releases/latest/download/bodypak.pyz

## Mods d'attente

Les mods d'attente remplacent l'animation de Jodi debout, donc un seul peut être actif. **idlepak.pyz** (dans la version publiée ; Python 3.8+, aucun paquet) transforme un tel remplacement en pak de mod à part : l'attente du jeu reste, et le mod devient un choix de plus sous Paramètres › Déplacement › Debout. AltUI doit être installé – le convertisseur construit le nouveau pak en partie à partir d'AltUI.pak.

```
python idlepak.pyz SomeIdleReplacer.pak --name SomeIdle --title "Some idle"
```

Copiez le IdleAltUI_SomeIdle.pak obtenu dans TheKillingAntidote\Mods\ et retirez le remplacement d'origine.

idlepak.pyz: https://github.com/Zyiakk/AltUI/releases/latest/download/idlepak.pyz · Détails: [README](https://github.com/Zyiakk/AltUI#idle-mods)

## Mises à jour du mod et le second fichier

Ce qui démarre le panneau est volontairement séparé du panneau lui-même : tout ce que fait le mod vit dans le pak du Workshop. Quand cet élément se met à jour via Steam, le fichier que vous avez mis dans *~mods* **continue normalement de fonctionner – inutile d'y toucher**.

Le Blueprint Loader lui-même n'a besoin de rien : c'est un mod à part, mis à jour sur sa propre page. Un AltUI_Hook_P.pak antérieur à 1.5.0 ne doit pas rester dans ~mods (voir la remarque sous Installation) : supprimez-le ou remplacez-le par l'actuel.

**Utiliser le hook sans le Blueprint Loader :** depuis 1.8.0, AltUI applique aussi votre look à Jodi dans le menu principal et sur l'écran de chargement. Avec le hook seul, il faut pour cela l'AltUI_Hook_P.pak actuel – remplacez l'ancien pour l'obtenir ; dans les niveaux, l'ancien continue de fonctionner. Avec le Blueprint Loader, AltUI.pak s'en charge lui-même.

Aucune ressource du jeu n'est incluse ; tout ce qui se trouve dans le pak est généré.

## Ce que fait chaque combinaison

* **AltUI.pak seul** – rien ne démarre le panneau – B ne fait rien.
* **AltUI.pak + Blueprint Loader** – le loader lit la table d'AltUI et démarre le panneau. AltUI lui-même ne remplace rien du jeu ; le loader remplace la classe du gestionnaire de caméra du jeu, c'est ainsi qu'il fonctionne.
* **AltUI.pak + AltUI_Hook_P.pak** – le hook remplace le gestionnaire de caméra du jeu et démarre le panneau.
* **AltUI.pak + les deux** – aucun problème, rien n'est perdu. Les deux remplacent la même classe du jeu, donc un seul des deux paks l'emporte – et quel qu'il soit, AltUI démarre : par la table du loader, ou par le hook, qui démarre alors aussi le loader lui-même, si bien que les mods conçus pour lui continuent de tourner.
* **Le hook ou le loader sans AltUI.pak** – rien – il manque le mod lui-même.

## Ce qu'il ne peut pas faire

Deux limites bonnes à savoir :

* **Le maquillage prend une teinte, pas une nouvelle couleur.** La couleur est multipliée sur le dessin déjà présent : un dessin pâle ou neutre la prend presque entièrement, un dessin sombre ne peut qu'être assombri ou décalé. Le blanc signifie « inchangé », pas un maquillage blanc.
* **Un corps converti peut laisser voir des parties de lui-même à travers des vêtements moulants.** Le jeu les aplatit avec des morph targets qui se trouvent sur le maillage du corps, et un corps dont le maillage n'en apporte pas n'a rien pour aplatir. Cela tient au corps, pas à la conversion : le convertisseur garde ce que l'original possède, et là où l'original n'en a pas, rien ne peut en ajouter.

## Source & problèmes

https://github.com/Zyiakk/AltUI – code source (MIT), tous les téléchargements, rapports de bugs.
