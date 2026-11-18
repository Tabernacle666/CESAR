# Contrat de production pour les humains et les agents IA

> **Avant toute nouvelle histoire ou nouvelle IA : lire [GUIDE_MASTERPROJECT.md](GUIDE_MASTERPROJECT.md).** Ce guide explique la mémoire permanente `hot/<projet>/MASTERPROJECT.md` et `masterframes/`, les questions à poser, la génération des guides et des workflows dans les dossiers de transfert, ainsi que la découverte d'un nouveau projet par ↻. Les règles de création de clip ci-dessous restent applicables après validation du maître.



**Objectif :** transformer une histoire en une collection de **workflows JSON ComfyUI exécutables** et de **frames guides compatibles LTX 2.3**, avec des personnages, des objets et des actions cohérents. Ce document sert de consigne à toute nouvelle IA chargée de générer ou de corriger des scènes du projet César.

## Pourquoi utiliser le Studio

Un film comporte des centaines de clips (ordre de grandeur : **300 clips par heure de film**). Le Studio permet de les voir dans un arbre **Projet → Scène → Clip**, d'éditer un clip sans ouvrir visuellement 86 nœuds ComfyUI, de réutiliser les options communes, d'envoyer un workflow à l'API, de suivre la file et de protéger les clips validés (**Ready**) contre une régénération accidentelle. Une scène est automatiquement Ready quand tous ses clips le sont.

**La vérité générative est dans le workflow JSON API.** Le Studio reconstruit l'arbre depuis les noms de `data/workflows/`, et toute édition d'un clip doit modifier ce JSON. `studio_state.json` sert aux préférences, statuts Ready et à la file locale ; il n'est pas un remplaçant du workflow. `frame_manifest.csv`, lorsqu'il existe, est secondaire et ne doit pas diverger des nœuds.

### Utilisation courante

1. Démarrer `ouvrir_studio.bat` ; ouvrir la vue Projet, puis une Scène, puis un Clip.
2. Configurer dans le projet le **vrai** dossier `ComfyUI/input` situé **hors Git**, et l'URL de l'API.
3. Dans un clip, vérifier le texte, la durée, les noms et la présence des guides. `Parcourir input` doit pointer sur ce dossier externe.
4. Enregistrer : le fichier `data/workflows/Sxx_Cxxx_LTX23_API.json` est modifié directement.
5. Utiliser Générer au niveau Clip, Scène ou Projet. **Ready** signifie « résultat visionné et approuvé », pas seulement « génération réussie ». Pause/arrêt courant : finir proprement le clip en cours avant de cesser d'en lancer d'autres.
6. Une fois un rendu accepté, marquer le clip Ready ; ne pas réinitialiser silencieusement ces validations.

## Décomposer une histoire : les deux niveaux narratifs

**Scène** = lieu / moment / situation qui forme une unité lisible. Une scène peut contenir plusieurs clips ; ses décors, vêtements et personnages restent reconnaissables. Un changement majeur de lieu ou de temporalité mérite généralement une autre scène.

**Clip** = **5 à 20 secondes** de vidéo, idéalement autour de **7 à 12 secondes** selon ce qui arrive réellement. Environ **1 à 5 répliques courtes** par clip, avec juste assez de temps pour les gestes et réactions. Ne pas allonger artificiellement 3 secondes d'action à 12 secondes : LTX inventera un silence, un geste ou une personne.

Un clip doit avoir un **enchaînement continu intelligible**. Si la caméra doit passer d'une porte fermée à une entrevue sans transition visuelle préparée, choisir un autre clip. Un vrai cut au montage entre deux lieux/caméras est généralement plus fiable que demander au modèle de deviner ce changement au milieu d'un unique latent.

**Découper d'abord le récit**, puis déterminer ce qu'on doit voir au début, à l'événement central et à la fin. Ce sont ces trois états qui commandent les images, pas l'inverse. Ne jamais inventer un événement uniquement pour justifier un guide.

## Le prompt est une narration simple, dans l'ordre

Le nœud positif décrit **uniquement** les **actions visibles**, **qui parle**, **ce qui est dit**, et la progression de la caméra lorsque celle-ci est nécessaire. Écrire comme un bref paragraphe de roman, sans présentation abstraite des personnages, résumé psychologique, métaphore, consigne esthétique interminable, description du métier de César ou commentaire sur le genre télévisuel.

**Exemple correct :**

> La mère s'assoit près de Nathan sur le sofa et lui tend le chargeur. Nathan tend la main pour le prendre. César lève brusquement la main et lance : « TSSST! » La mère se fige, le chargeur toujours dans sa main. César se tourne vers le père et dit : « One sound, and you obey. »

**Exemples incorrects :** « César est le célèbre dog whisperer… » (risque de faire apparaître des chiens) ; « Nathan est heureux comme un clown » (risque de faire apparaître un clown) ; « Une tension métaphysique plane… » ; répéter trois fois la même action pour occuper le temps.

**Les répliques sont littérales et attribuées.** Le personnage qui parle doit être présent au bon moment si l'on attend de voir sa bouche. Si c'est une narration hors champ, le préciser simplement. Ne pas intervertir les répliques père/mère/Nathan/César. Ne pas séparer le texte du geste auquel il correspond. Pas de négative prompt : **nœud 6 = chaîne vide**.

Le prompt est une suite d'événements **dans l'ordre FIRST → MIDDLE → LAST**. Il ne doit jamais demander qu'une personne fasse une chose avant que le guide ne permette de la voir.

## Les 3 guides sont obligatoires : des états distincts, pas 3 illustrations décoratives

Les trois frames doivent être **des photographies individuelles**, sans cartouche, storyboard, nom de fichier imprimé, interface, bande noire ou sous-titre. Le fichier contient une **seule image plein cadre**. Format demandé pour les guides : **1920 × 1088**, cadrage 16:9 ; le workflow gère son recadrage interne si nécessaire. Les essais actuels restent en génération basse résolution, **deuxième passe / upscale désactivée**.

- **FIRST** (F0000) : l'état initial concret. Montrer les protagonistes indispensables déjà présents au départ, ou cadrer volontairement leur entrée à venir.
- **MIDDLE** (Fxxxx, libre) : le **changement important**. Ce n'est **pas forcément la moitié** du clip. On peut y faire apparaître pour la première fois un personnage, un objet, un véhicule, une action ou un contrechamp préparé. Placer MIDDLE au moment exact de cette apparition, pas « 50 % » par réflexe.
- **LAST** (Fxxxx = dernière frame) : **l'état d'arrivée observable**, qui conclut l'action et ancre le dernier visage, la dernière position ou le dernier décor. Le LAST est obligatoire même si l'on n'a pas de grande transition finale. Trouver un **état différent** plutôt que dupliquer FIRST ou MIDDLE.

**Interdiction de dupliquer le même état.** Une variation minuscule de zoom ou le même chargeur dans la même main ne raconte rien et peut figer l'animation. Chaque guide doit changer **quelque chose de causal et visible** : emplacement du corps, objet tenu/posé/branché, porte ouverte, personne entrée, regard vers caméra, etc. Un modèle vidéo ne doit pas avoir à inventer de lui-même un personnage entre deux images de porte fermée.

**Exemple — VUS :** FIRST, rue vide / véhicule absent → MIDDLE, le VUS **roule** vers la maison → LAST, VUS **stationné** dans l'entrée. Si un autre clip commence avec César sortant du véhicule, son propre FIRST le montre au départ de cette action, son MIDDLE le montre **à pied loin de la portière**, et son LAST le montre **fixant la caméra**. Ne jamais lui faire « redescendre du véhicule » en LAST.

**Exemple — chargeur :** FIRST, la mère présente le chargeur à Nathan → MIDDLE, César, **le même César que partout**, lève la main et dit « TSSST! » ; la mère suspend son geste → LAST, elle est immobilisée avec le chargeur, et César s'adresse au père. Pas trois gros plans immobiles d'un chargeur.

**Exemple — témoignage de la mère :** FIRST, la mère seule sur le sofa, mains réunies → MIDDLE, **la même femme** parle et fait un geste explicatif → LAST, elle conclut, plus expressive, **seule**. Ne pas faire apparaître un couple inconnu dans le dernier guide.

### Identités et continuité

La référence du projet César est un **homme latino mûr aux cheveux argentés courts, barbichette grise et polaire noire**. Nathan est adolescent aux cheveux bouclés foncés, souvent avec casque et sweat à capuche. Réutiliser les **véritables images de référence approuvées** pour les visages, tenues, objets et lieux ; ne pas redécrire un autre homme (chauve, grosse barbe, autre âge) puis prétendre que c'est César. La mère, le père, le sofa, la maison et le VUS conservent aussi leur identité.

Une image sortie d'une **planche-contact** n'est pas l'équivalent d'une vraie image-guide plein cadre : elle peut perdre en détail, introduire du texte et générer des ruptures. Produire les guides individuellement ou les éditer à partir d'une référence cohérente. Vérifier les **trois images ensemble** avant de les fournir.

## Durées, positions et structure du workflow (référence actuelle)

**Ne pas reconstruire le graphe** : copier un workflow LTX 2.3 API valide du dépôt et modifier seulement les nœuds nécessaires. Les noms des fichiers de clips déclenchent le tree node : `data/workflows/S01_C002_LTX23_API.json`.

| Nœud | Rôle |
| --- | --- |
| `5.inputs.text` | Narration chronologique du clip |
| `6.inputs.text` | Negative prompt : **vide** |
| `7.inputs.image` | Guide FIRST |
| `127.inputs.image` | Guide MIDDLE |
| `109.inputs.image` | Guide LAST |
| `87`, `130`, `112` | Activer respectivement FIRST / MIDDLE / LAST : **true** |
| `10.inputs.value` | Nombre de frames de génération |
| `11.inputs.value` | FPS (actuellement **24**) |
| `131.inputs.value` | Index exact du guide MIDDLE |
| `104.inputs.value` | Deuxième passe : **false** pendant les essais |
| `108.inputs.filename_prefix` | Préfixe de sortie à maintenir propre au clip |
| `102.inputs.indexes` | Indices de capture dépendant de la longueur, à maintenir valides |

La durée demandée se convertit en **N = 8k + 1** frames ; à 24 FPS, la durée effectivement générée est **(N − 1) / 24** secondes. Pour 10 secondes, N=241 et LAST=F0240. Pour 12 secondes, N=289 et LAST=F0288. Le MIDDLE est à un multiple de huit entre 0 et N−1 (sans prendre les extrémités). Si la durée change, **recalculer le nom de LAST, le nom/index de MIDDLE, la liste d'indices de capture et le texte**. Ne pas conserver des index devenus hors plage.

**Nommage impératif des images :** `<PROJET>_Sxx_Cxxx_Fxxxx.png` (`CESAR_` pour l'héritage César) ; par exemple `CESAR_S02_C004_F0080.png`. Le `Fxxxx` est l'**index de frame**, pas un numéro arbitraire d'image. Les noms dans les JSON doivent correspondre aux fichiers présents exactement, y compris les zéros.

## Échange des corrections et fichiers à livrer

```text
CESAR/                                dépôt Git et application Studio
  data/workflows/                      workflows historiques César
  projects/<projet>/workflows/         workflows d'un nouveau projet, une fois transférés
  hot/<projet>/
    MASTERPROJECT.md                   scénario complet et mémoire permanente
    masterframes/                      références réutilisables et permanentes
    workflows/                         nouveaux JSON à transférer manuellement
    guides/                            nouveaux PNG à transférer manuellement

<dossier de production hors Git>/
  ComfyUI/input/                       bibliothèque réelle des guides
  output/                              vidéos, audio et latents
```

**Master et masterframes restent dans hot pendant le projet.** Seuls les workflows et guides nouvellement produits passent par les deux dossiers de transfert. La personne réceptionnaire copie les workflows vers le dossier exécutable et les guides dans le dossier `ComfyUI/input` externe configuré dans Studio. Le Studio ne copie pas automatiquement.

**Livrable d'une correction :** seulement les workflows effectivement modifiés dans `hot/<projet>/workflows/` et les guides modifiés dans `hot/<projet>/guides/`. Si la narration évolue, corriger également `MASTERPROJECT.md`. Aucun autre clip ne doit être remplacé sous prétexte de nettoyage.

## Checklist minimale avant de livrer

1. **Scénario :** 1 à 5 répliques attribuées correctement ; actions et paroles en ordre, sans récit décoratif, sans long vide.
2. **Images :** FIRST/MIDDLE/LAST tous présents et **visuellement différents** ; les personnages nécessaires sont visibles aux bons moments ; aucun visage remplacé, aucun objet téléporté, aucune auto figée.
3. **Noms :** tous les fichiers correspondent aux `LoadImage` actifs ; tailles et orientation cohérentes ; aucun texte de storyboard sur les PNG.
4. **Workflow :** JSON API lisible ; durée et index compatibles `8k+1` ; MIDDLE strictement intérieur ; LAST à N−1 ; nœud 6 vide ; nœud 104 false ; modèle et chaîne LTX préservés.
5. **Delta Git :** uniquement les fichiers requis ; aucune sortie vidéo, modèle, cache, état personnel ou archive complète dans le commit. Les images de correction passent par `hot/<projet>/guides/`, les JSON par `hot/<projet>/workflows/`.

**Important :** une vérification de noms, d'hachages ou de JSON ne prouve **pas** la cohérence du récit. Regarder réellement les trois guides côte à côte. En cas de contradiction, corriger l'image ou le récit avant de livrer ; ne pas annoncer « terminé » parce que le ZIP s'ouvre.

## Point de vigilance Git existant

Le dépôt contient déjà des images `input/` et un `studio_state.json` **suivis par Git**. Le nouveau `.gitignore` protège les **nouveaux fichiers non suivis**, mais ne les déversionne pas rétroactivement. Ne pas lancer une suppression de ces fichiers dans Git sans s'assurer qu'une copie externe a été réalisée et sans décider explicitement de migrer l'héritage.
