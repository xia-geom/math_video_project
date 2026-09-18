# UQAM — ouvertures interdisciplinaires : audit visuel et mise à jour

**Date :** 17 septembre 2026  
**PR :** #4  
**Implémentation auditée :** `851ddaca496dd548b41364d853bcbefb573fa40d`  
**Workflow dédié :** run `35288038988` — succès  
**Artefact :** `10525595080`

## Conclusion de l’audit

La première composition était techniquement valide mais trop dense pour une capsule d’environ 20 secondes : trop de cartes, d’étiquettes et de texte simultané. La version révisée abandonne cette logique « diapositive animée ».

La règle visuelle est maintenant :

> **une photo UQAM + une idée courte à la fois.**

Toutes les images visibles du film viennent désormais du diaporama fourni. Deux photographies de la page 1 sont utilisées : le groupe devant le tableau de mathématiques et le pavillon Président-Kennedy avec l’inscription UQAM. Les pages 21–23 restent la base des affirmations sur la majeure, le certificat et le B.Sc. Sciences; la page 7 fournit `math.uqam.ca`.

## Ce qui a été retiré

- grille de quatre cartes;
- boîtes « majeure » / « certificat »;
- bandeau administratif permanent;
- accumulation de titres, sous-titres et petites mentions;
- visuels génériques ou externes dans cette capsule.

Chaque plan contient maintenant au plus trois lignes de texte.

## Storyboard vérifié

| Temps | Photo | Message |
|---|---|---|
| 0–4 s | Pavillon UQAM | **Les maths ouvrent des portes.** |
| 4–9 s | Groupe au tableau | **2 ans en maths ou statistique** / à temps plein → une majeure |
| 9–16 s | Groupe au tableau | Puis, un certificat / **Communication · Finance** / **Économique · Informatique** |
| 16–20 s | Pavillon UQAM | **Un bac en sciences.** / **Plusieurs horizons.** / math.uqam.ca |

Le MP4 propre est la référence éditoriale. Le SRT reste disponible séparément. Le MP4 avec sous-titres incrustés est conservé comme variante d’accessibilité/contrôle, mais il répète naturellement une partie du texte écran et n’est pas la version visuelle recommandée.

## Validation technique

- 20 tests : **20 réussis**, aucun échec, aucune erreur, aucun test ignoré.
- Ruff sur le nouveau projet et son test : **réussi**.
- Rendu Manim réel : **1920 × 1080, 60 fps, 19,983333 s**.
- MP4 de référence : une piste vidéo H.264, **aucune piste audio** en mode aperçu muet.
- Contrôles durée, ratio, flux, chronologie SRT, bornes de mise en page et fraîcheur des sources : **réussis**.
- Les deux photos sont contrôlées par SHA-256 avant rendu.
- Les quatre images de contrôle sont maintenant extraites du **master propre**, pas de la variante avec sous-titres incrustés.
- Inspection visuelle des quatre plans : aucune collision de texte observée; les deux photographies restent visibles et l’identité UQAM est immédiatement perceptible.

## Azure

La narration Azure n’a pas été produite dans GitHub. Le workflow indique :

- demande Azure : oui;
- source PR : fiable;
- `SPEECH_KEY` : absent;
- `SPEECH_REGION` : absent;
- état : **blocked**.

Aucune voix de remplacement et aucune fausse piste audio n’ont été utilisées. Le profil prévu reste `MAI-Voice-2` à `+2%`. L’écoute complète reste à faire après un vrai rendu Azure.

## CI global du dépôt

Le workflow `smoke` séparé a encore son échec Ruff global préexistant; la compilation de tout le dépôt réussit et le rendu global est ignoré après l’échec lint. Cette mise à jour ne masque ni ne désactive ce problème.

## État

La mise à jour est sauvegardée sur `feat/uqam-bac-sciences-20s` et proposée dans la PR #4. Elle n’est pas fusionnée dans `main`, aucun master narré n’est approuvé et aucune publication institutionnelle n’est déduite des tests.
