# César Workflow Studio

Éditeur local de production vidéo pour **LTX 2.3 / ComfyUI**. Le **workflow JSON API est le fichier maître** : Studio le lit, l'affiche, le modifie et l'envoie à ComfyUI. Il ne remplace pas les workflows par une autre représentation.

## Démarrage

1. Sous Windows, lancer `ouvrir_studio.bat` (Python 3 requis ; `studio.py` utilise la bibliothèque standard).
2. L'interface s'ouvre sur `http://127.0.0.1:8765/`.
3. Dans les paramètres du projet, choisir le vrai dossier `ComfyUI/input` **hors du dépôt Git** et l'URL locale de ComfyUI (par défaut `http://127.0.0.1:8188`).
4. Sélectionner un clip dans l'arbre, lire/modifier son prompt, les guides FIRST/MIDDLE/LAST et sa durée, puis enregistrer : **c'est le JSON du clip qui change**.
5. Générer un clip, une scène ou le projet. Les clips marqués **Ready** sont ignorés par défaut.

L'arbre est reconstruit à partir de `data/workflows/Sxx_Cxxx_LTX23_API.json` : projet → scène → clip. À la création de ce guide, le dépôt possède 6 scènes, 27 workflows et 81 images dans `input/` (héritage initial, voir la remarque Git plus bas).

## Pour faire produire de nouveaux clips par une IA

Lire **[GUIDE_PRODUCTION_IA.md](GUIDE_PRODUCTION_IA.md)** avant de modifier un workflow ou fabriquer une image. Il décrit le découpage d'une histoire, la narration chronologique, les trois états visuels, les noms exacts, les paramètres LTX et les pièges observés en production.

## Échange d'images

- `hot/` : **dossier Git versionné**, utilisé seulement pour déposer et échanger les **nouvelles frames ou frames corrigées**.
- La personne qui réceptionne les images les copie **manuellement** avec leur nom exact dans son projet local / `ComfyUI/input`, **hors Git**.
- `hot/README.md` précise le protocole. `hot/` n'est pas la bibliothèque permanente des guides.
- Les workflows modifiés vont dans `data/workflows/`, jamais seulement dans une base ou dans un manifeste.

## Git et données locales

Le dépôt ne disposait pas de `.gitignore` au départ : il suit déjà `input/` (81 PNG) et `studio_state.json`. Le `.gitignore` protège **les nouveaux fichiers non suivis** dans ces emplacements, mais ne déversionne **pas** ceux déjà suivis. Les anciennes images et l'état existant ont été préservés pour éviter une suppression au prochain `git pull`. Une migration hors Git des anciens fichiers suivis nécessitera une opération distincte, après sauvegarde de leur copie locale.

Le moteur ComfyUI et ses modèles ne sont pas inclus. L'upscale / deuxième passe est **désactivé pour les essais actuels**, sans empêcher une phase de finition ultérieure.
