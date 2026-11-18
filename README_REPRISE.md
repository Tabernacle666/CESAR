# César Workflow Studio R3 — narration simple, guides obligatoires

- `data/workflows/` : 27 JSON API ComfyUI (6 scènes). Les JSON sont les fichiers maîtres.
- `input/` : 81 PNG portant exactement les noms des guides de chaque workflow. Déposer les PNG dans `ComfyUI/input/`.
- Node 5 : une succession directe d’actions et de répliques, dans l’ordre du clip, sans présentation théorique des personnages.
- Node 6 : negative prompt vide.
- Nodes 87/130/112 : FIRST, MIDDLE et LAST obligatoires.
- Node 104 : passe 2 / upscale désactivée.
- Node 131 : position du guide MIDDLE propre au clip.
- Le fichier `studio_state.json` local n’est PAS remplacé. La révision R3 réinitialise les anciennes validations Ready sans écraser le chemin ComfyUI propre à l’utilisateur.

## Limite des images

Les guides sont des photographies distinctes sélectionnées puis recadrées parmi les captures déjà produites. Ce ne sont pas 81 nouvelles générations image par image. Les différences de cadrage permettent de ne pas fournir deux fichiers absolument identiques, mais certaines transitions de personnage et de décor restent visuellement insuffisantes. Inspection recommandée avant de lancer les 27 clips.
