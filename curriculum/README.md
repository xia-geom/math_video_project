# Programme et nouvelles capsules

## Quelle source utiliser ?

- [programme_principal_fr.yaml](programme_principal_fr.yaml) reste le manifeste
  canonique : 27 capsules principales et 6 capsules d’erreurs fréquentes.
- [couverture_programme.md](couverture_programme.md) conserve le bilan de
  couverture et les lacunes du syllabus.
- [extension_syllabus_fr.yaml](extension_syllabus_fr.yaml) enregistre les dix
  nouvelles sources candidates correspondant aux lacunes obligatoires, avec
  objectifs, prérequis, classes publiques et auto-évaluations. Les identifiants
  S01–S10 ne remplacent pas les identifiants P01–P27 des audits.

Les nombres 28–37 des nouveaux dossiers identifient leurs sources ; ils ne
modifient pas l’ordre de livraison existant. Les vidéos de géométrie et de
notation sigma restent à la fin du manifeste canonique actuel. L’intégration
éditoriale des candidats dans ce parcours sera une modification explicite du
manifeste, de son validateur et des index de livraison, après leur revue.

## Candidats ajoutés

| Identifiant | Sujet | État de la source |
|---|---|---|
| S01 | Opérations sur les nombres réels | Écrite |
| S02 | Fonctions rationnelles et asymptotes | Écrite |
| S03 | Modèles probabilistes élémentaires | Écrite |
| S04 | Équations de la droite et du plan | Écrite |
| S05 | Règle de Cramer | Écrite |
| S06 | Élimination de variables | Écrite |
| S07 | Programmation linéaire à deux variables | Écrite |
| S08 | Trigonométrie du triangle | Écrite |
| S09 | Lois des sinus et des cosinus | Écrite |
| S10 | Fonctions trigonométriques inverses | Écrite |
| S11 | Nombres complexes | Facultatif, non implémenté |

Les exemples et narrations sont nouvellement rédigés pour réaliser les thèmes
du plan ; ce ne sont pas des transcriptions du manuel. Un exemple vérifié et
une capsule introductive ne prouvent pas une couverture exhaustive du chapitre.

## Production sans modifier les anciens livrables

Depuis la racine, dans l’environnement Manim existant :

```bash
python scripts/render_syllabus_expansion.py --check-only
python -m pytest tests/test_syllabus_expansion.py -q
python scripts/render_syllabus_expansion.py --ids S01,S02 --mode silent
python scripts/render_syllabus_expansion.py --mode silent
# Synthèse réelle : nécessite les identifiants Azure et le profil partagé.
python scripts/render_syllabus_expansion.py --ids S01 --mode azure
```

Le script utilise les sources du manifeste, le Python courant et la pile
Manim/Azure existante. Il écrit dans un nouveau dossier horodaté sous
`review_artifacts/syllabus/`. Il ne copie rien vers Drive, ne modifie pas
`dist/programme_principal_fr`, ne produit pas de fausse piste audio et ne publie
pas de vidéo. Les aperçus muets sont explicitement nommés `silent_preview`.

Le résultat `STATUS.json` contient le commit, les empreintes des sources et des
services partagés, le mode audio, les résultats de rendu et les contrôles de flux
MP4. Les images extraites sont des échantillons, pas une revue complète des
transitions. Les médias sont temporaires ; le compte rendu durable appartient
à `reports/syllabus_expansion/`.

## Avant de déclarer une capsule prête

Lire [le standard et les leçons de l’audit](../docs/TEACHING_STANDARD.md).
Séparer les statuts : source écrite, exemples testés, rendu réussi, images
inspectées, mouvement complet inspecté, narration écoutée, résolution finale
vérifiée et publication autorisée. Aucun résultat automatisé ne valide seul
l’ensemble de ces étapes. Ne pas lancer les anciens scripts d’application de
correctifs pour préparer une nouvelle capsule.
