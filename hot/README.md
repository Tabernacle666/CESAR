# hot/ — échange temporaire de frames

Ce répertoire est **volontairement suivi par Git**. Il sert à échanger les images-guide **nouvelles ou corrigées** entre agents et poste de production, **pas** à stocker les médias permanents.

1. Déposer ici des **PNG individuels** (pas des planches-contact) en **1920 × 1088**. Nom exact du workflow, ex. `CESAR_S01_C005_F0128.png`.
2. Pousser seulement les frames modifiées ainsi que tout `data/workflows/*.json` réellement modifié.
3. Après `git pull`, la personne réceptionnaire **copie manuellement** ces PNG dans son dossier local `ComfyUI/input` / projet **hors Git**, en écrasant les guides ciblés.
4. Une fois les copies effectuées, enlever les PNG de `hot/` et committer cette suppression si désiré, afin de maintenir un dossier d'échange léger.
5. Le Studio utilise le dossier `input_dir` configuré dans ses paramètres ; **il ne charge pas automatiquement `hot/`**.

Ne pas utiliser `hot/` pour les rendus, latents, audio, modèles, données personnelles ou lots complets ; les fichiers poussés restent présents dans l'historique Git même après leur suppression.

Consignes de création et de vérification : [GUIDE_PRODUCTION_IA.md](../GUIDE_PRODUCTION_IA.md).
