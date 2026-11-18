# MASTERPROJECT — contrat de production entre sessions et agents IA

**Lire avant de commencer un nouveau sketch ou de générer des workflows.**

## Projet et dossier permanents

Un projet est identifié par son dossier versionné dans `hot/` :

```text
hot/
  cesar/
    MASTERPROJECT.md            # scénario intégral et mémoire de production
    masterframes/               # images de référence persistantes (casting, décor, objets)
    guides/                     # guides FIRST / MIDDLE / LAST À TRANSFÉRER
    workflows/                  # JSON API ComfyUI À TRANSFÉRER
  snl_musk/
    MASTERPROJECT.md
    masterframes/
    guides/
    workflows/
```

**Les deux ressources permanentes pendant la création d'un projet sont `MASTERPROJECT.md` et `masterframes/`.** Elles restent versionnées dans `hot/<projet>/` jusqu'à la fin du projet. Les deux dossiers `guides/` et `workflows/` servent de boîte d'échange : après copie manuelle vers la production, on peut les vider (en sachant que les objets déjà poussés restent dans l'historique Git).

Le Studio répertorie automatiquement les dossiers de `hot/`. Créer simplement `hot/snl_musk/` puis cliquer sur **↻ Rafraîchir** : un nouveau niveau projet apparaît, même s'il n'a encore aucun clip. Il suffit de le sélectionner pour afficher/créer son `MASTERPROJECT.md`. Le bouton **+ Projet** crée aussi le dossier localement.

Les workflows du projet actif sont lus dans :
- **César historique :** `data/workflows/` (inchangé).
- **Autres projets :** `projects/<projet>/workflows/`.

Le **workflow JSON API ComfyUI reste le fichier de génération maître**. `MASTERPROJECT.md` est la **source narrative et de continuité**, dont on *dérive* les clips. Il ne remplace pas les workflows et ne contient pas de paramètres cachés de génération.

## Nouvelle session : « On fait un sketch »

**Ne pas fabriquer immédiatement 100 workflows ou des guides.** Le nouvel agent doit :

1. Chercher `hot/<projet>/MASTERPROJECT.md`, ainsi que les images de `hot/<projet>/masterframes/`. Si le projet existe, **les relire en premier** ; ne pas faire répéter ce qui est déjà décidé.
2. Si c'est un nouveau projet, demander seulement les **informations nécessaires et non encore connues** : sujet et situation comique, qui apparaît, ton, durée souhaitée, lieux, déroulement et chute. Poser des questions courtes en conversation, sans formulaire interminable. L'utilisateur peut ne connaître que le sujet : démarrer avec une trame provisoire et préciser avec lui.
3. Rédiger **l'histoire intégrale**, chronologique, avec actions et répliques attribuées, dans `MASTERPROJECT.md`. Ne pas confondre histoire entière et prompts de clips.
4. Recenser les **personnages récurrents, vêtements, lieux et accessoires**, puis déterminer les **masterframes** nécessaires : portraits cohérents des personnages, famille/relations, vues du décor vide, objets importants, véhicule, etc.
5. Créer ces masterframes comme **images autonomes de référence** : pas de scènes du sketch, pas de FIRST/MIDDLE/LAST, pas de vignette de storyboard, pas de texte incrusté. Les enregistrer **dans `hot/<projet>/masterframes/`**, les nommer et les déclarer dans `MASTERPROJECT.md`.
6. Verrouiller la continuité visuelle (qui est qui, vêtements, lieu, accessoires). Les nouvelles sessions doivent réutiliser les mêmes références **avant** de créer d'autres images.

**Un masterframe n'est pas un guide temporel.** Il ne montre pas nécessairement une action du film : c'est un aide-mémoire visuel qui doit rester utilisable pour recomposer autant de scènes que nécessaire. Exemple pour un sketch Musk : portraits du personnage principal, autres personnages récurrents, cabine/plateau de décor, véhicule ou objet important. Ne pas inventer un nouveau visage à chaque clip.

## Quand l'utilisateur demande : « Génère les workflows de tous les clips »

L'agent doit relire le maître **et toutes les masterframes**, puis :

1. Décomposer la narration intégrale en **scènes**, puis en **clips de 5 à 20 secondes** contenant typiquement **1 à 5 répliques** et leurs actions successives.
2. Rédiger chaque prompt comme une narration directe, dans l'ordre **action → réplique → action → réaction**. Aucun préambule, aucun trait psychologique abstrait, aucune métaphore visuelle. Exemple : « La mère tend le chargeur. Nathan avance la main. César lève la main et dit : “TSSST!” La mère s'immobilise. » La personne qui parle doit être la bonne.
3. Produire **trois guides par clip**, obligatoires : FIRST = départ, MIDDLE = changement concret (pas forcément au milieu), LAST = résultat final. Les trois images doivent **différer causalement**, pas trois copies/rezooms d'un même état.
4. Construire chaque guide à partir des **mêmes masterframes** pour préserver visages, vêtements, lieux et objets. La frame MIDDLE sert souvent à introduire un personnage, un objet ou un mouvement. Le LAST doit représenter l'état atteint et aider LTX à ne pas dériver.
5. Copier un **workflow LTX 2.3 API valide** plutôt que d'inventer un nouveau graphe. Durée `8n+1` frames à 24 FPS, MIDDLE à un index intérieur multiple de 8, LAST à N−1, nœud `5` = narration, nœud `6` = chaîne vide, nœuds `87/130/112` activés, nœud `104` false (upscale désactivé pour essais).
6. Déposer **uniquement** les nouveaux workflows sous `hot/<projet>/workflows/Sxx_Cxxx_LTX23_API.json` et leurs guides nommés `<PROJET>_Sxx_Cxxx_Fxxxx.png` sous `hot/<projet>/guides/`. Garder `MASTERPROJECT.md` et les masterframes dans leur emplacement permanent.
7. L'utilisateur transfère **manuellement** les JSON dans le dossier de workflows du projet, et les PNG dans le vrai `ComfyUI/input` **hors Git**. **↻ Rafraîchir** fait apparaître le découpage dans l'arbre une fois les JSON transférés.

**Un agent ne doit jamais considérer qu'un clip existe dans le Studio seulement parce qu'il a placé des JSON dans `hot/.../workflows`** : c'est la zone d'échange. Le tree node lit les workflows transférés dans `data/workflows` pour César ou `projects/<slug>/workflows` pour les autres.

## À chaque correction

- Lire le maître et les références visuelles avant toute édition.
- Ne modifier que les clips explicitement concernés.
- Si l'utilisateur signale une évolution narrative ou un nouveau personnage, la noter dans le maître **avant** de produire des guides.
- Si l'utilisateur corrige uniquement une image, fournir uniquement le nouveau PNG dans `hot/<projet>/guides`, avec le **nom d'image référencé par le workflow**. Mettre le JSON à jour seulement lorsque les paramètres ou la narration changent.
- Ne pas réutiliser plusieurs fois un même état visuel pour « remplir » FIRST/MIDDLE/LAST. Même personne ≠ même position ; même objet ≠ même action. Exemple auto : rue vide → auto en mouvement → auto arrêtée ; chargeur : proposé → geste interrompu → main figée.
- Ne jamais remplacer des personnes/lieux approuvés par des apparences différentes. Vérifier visuellement chaque trio de guides. Un contrôle des fichiers et des hashes **ne suffit pas**.
- Respecter les clips Ready et conserver la possibilité d'un upscale ultérieur (ne pas supprimer les latents utiles sans accord).

Voir [GUIDE_PRODUCTION_IA.md](GUIDE_PRODUCTION_IA.md) pour le détail des nœuds, index temporels, noms et validations.
