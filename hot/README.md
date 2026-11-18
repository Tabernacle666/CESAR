# hot/ — espace d'échange ET mémoire permanente des projets

Un dossier par projet : `hot/cesar/`, `hot/snl_musk/`, etc. Studio le voit à **↻ Rafraîchir** et peut lui créer un MASTERPROJECT si nécessaire.

**Permanents jusqu'à la fin du projet**
- `hot/<projet>/MASTERPROJECT.md` : narration intégrale, personnages, lieux, objets, décisions verrouillées, découpage.
- `hot/<projet>/masterframes/` : photos de référence indépendantes des actions du film, réutilisables entre clips et sessions.

**Boîtes d'échange temporaires**
- `hot/<projet>/workflows/` : nouveaux JSON ComfyUI à copier manuellement dans `data/workflows/` (César) ou `projects/<projet>/workflows/` (autres projets).
- `hot/<projet>/guides/` : guides `<PROJET>_Sxx_Cxxx_Fxxxx.png` à copier manuellement dans le vrai `ComfyUI/input` **hors Git**.

Le Studio ne transfère pas automatiquement les images ; il lit les workflows transférés, non les JSON en attente sous `hot/`. Les dossiers et fichiers contenus dans `hot/` sont volontairement versionnés (y compris les PNG temporaires : ils restent dans l'historique Git après suppression).

Pour un nouvel agent IA : **lire [GUIDE_MASTERPROJECT.md](../GUIDE_MASTERPROJECT.md)** puis [GUIDE_PRODUCTION_IA.md](../GUIDE_PRODUCTION_IA.md).
