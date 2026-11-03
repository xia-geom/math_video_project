# Companion and promotional videos

## Product introductions

[Conversation Archive — English](conversation_archive_intro_en/README.md): a separate 70-second, silent, captioned Manim explainer using invented examples. Its storyboard labels current behavior and the storage roadmap separately. Sources, tests, and its render workflow belong to that project; it is not a curriculum lesson or an institutional advertisement.

## UQAM — trois vidéos parallèles

Cette collection contient trois productions distinctes, pas trois versions interchangeables d’un même film.

| Projet | Message | Entrée de production |
|---|---|---|
| [Présentation longue](uqam-baccalaureat-mathematiques-cheminements/README.md) | Le baccalauréat et ses cheminements en détail | `render_v4.py` et son environnement dédié |
| [Promotion générale](bac_math_uqam_fr/README.md) | Pourquoi étudier les mathématiques à l’UQAM | `build_release.py`, classe `BacMathUQAMFR` |
| [Ouvertures interdisciplinaires — 29 s](bac_sciences_ouvertures_fr/README.md) | Une majeure en maths/statistique, un certificat complémentaire, un bac en sciences par cumul | `build.py`, classe `BacSciencesOuverturesFR` |

Le catalogue lisible par machine est [uqam_promotion.json](uqam_promotion.json).
L’organisation du dépôt entier est décrite dans [ARCHITECTURE.md](../ARCHITECTURE.md).
Les copies de livraison se trouvent dans `/Users/xiaxiao/My Drive/UQAM-apercu-programme` :
un dossier par film, puis `versions/<date>/`. Depuis le 5 octobre, les trois
dossiers Drive contiennent uniquement des vidéos, à la demande de l’utilisateur.
`INDEX.md` à la racine indique la version de revue la plus récente. Les anciens
MP4 sont conservés; les sources, crédits, manifestes et historiques sauvegardés
restent dans le projet local, hors de ces dossiers Drive.

## Frontières à préserver

- Chaque projet garde son scénario, son point d’entrée, ses tests et ses livrables. Ne pas importer une scène d’un film dans un autre.
- Les deux premiers dossiers gardent leurs chemins historiques : leurs outils et leurs rapports les référencent déjà. Aucun déplacement ou double exemplaire sous `scenes/promotion_fr/` n’est nécessaire.
- Les deux clips Manim utilisent la configuration vocale commune `tools/tts.py`. Le film long conserve son environnement verrouillé et son propre moteur.
- Les aperçus muets, les rendus narrés et les masters approuvés sont trois états différents. Un test réussi ne signifie ni écoute réalisée ni autorisation de diffusion.
- Les MP4, WAV et caches produits vont dans `dist/`, `media/` ou les artefacts GitHub Actions, pas dans les sources Git. Les fichiers historiques déjà suivis ne sont pas supprimés automatiquement.

Le clip interdisciplinaire n’entre pas dans les 27 leçons du programme principal ni dans les six vidéos d’erreurs fréquentes.
