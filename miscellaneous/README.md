# UQAM — trois vidéos parallèles

Ce dossier contient trois productions distinctes, pas trois versions interchangeables d’un même film.

| Projet | Message | Entrée de production |
|---|---|---|
| [Présentation longue](uqam-baccalaureat-mathematiques-cheminements/README.md) | Le baccalauréat et ses cheminements en détail | `render_v4.py` et son environnement dédié |
| [Promotion générale](bac_math_uqam_fr/README.md) | Pourquoi étudier les mathématiques à l’UQAM | `build_release.py`, classe `BacMathUQAMFR` |
| [Ouvertures interdisciplinaires — 20 s](bac_sciences_ouvertures_fr/README.md) | Une majeure en maths/statistique, un certificat complémentaire, un bac en sciences par cumul | `build.py`, classe `BacSciencesOuverturesFR` |

Le catalogue lisible par machine est [uqam_promotion.json](uqam_promotion.json).
L’organisation du dépôt entier est décrite dans [ARCHITECTURE.md](../ARCHITECTURE.md).

## Frontières à préserver

- Chaque projet garde son scénario, son point d’entrée, ses tests et ses livrables. Ne pas importer une scène d’un film dans un autre.
- Les deux premiers dossiers gardent leurs chemins historiques : leurs outils et leurs rapports les référencent déjà. Aucun déplacement ou double exemplaire sous `scenes/promotion_fr/` n’est nécessaire.
- Les deux clips Manim utilisent la configuration vocale commune `tools/tts.py`. Le film long conserve son environnement verrouillé et son propre moteur.
- Les aperçus muets, les rendus narrés et les masters approuvés sont trois états différents. Un test réussi ne signifie ni écoute réalisée ni autorisation de diffusion.
- Les MP4, WAV et caches produits vont dans `dist/`, `media/` ou les artefacts GitHub Actions, pas dans les sources Git. Les fichiers historiques déjà suivis ne sont pas supprimés automatiquement.

Le nouveau clip n’entre pas dans les 27 leçons du programme principal ni dans les six vidéos d’erreurs fréquentes.
