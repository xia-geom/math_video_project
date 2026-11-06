# Migration préparée avant la restructuration du 6 novembre 2026

Décision confirmée : le chapitre 17 présente les nombres complexes. L'intégralité
du chapitre antérieur, de ses exercices et de ses réponses sur le mouvement
circulaire et les modèles sinusoïdaux est conservée dans l'annexe A. Les cinq
parties et les dix-sept chapitres principaux subsistent; huit sections nouvelles
portent le total à 134, dont les huit sections de l'annexe.

Les identifiants sémantiques historiques `17.1` à `17.8` et les étiquettes TeX
`manual:section:17.01` à `17.08` (idem `workbook`) désignent toujours le mouvement
circulaire. Seul leur numéro imprimé devient `A.1` à `A.8`. Les fichiers passent
de `sources/{manual,workbook}/chapters/ch17.tex` à
`sources/{manual,workbook}/appendices/circular_motion.tex`. Les étiquettes de
chapitre historiques restent également attachées à ce contenu.

Les huit sections nouvelles reçoivent les identifiants `complexes.1` à
`complexes.8`, les étiquettes `manual:section:complexes.01` à `complexes.08`
(idem `workbook`) et les numéros imprimés `17.1` à `17.8`. L'identifiant et le
numéro imprimé ne sont donc plus interchangeables. Les deux index indiquent
explicitement le champ `display` pour ces seize sections; pour les autres,
l'absence de ce champ conserve l'affichage historique de l'identifiant.

| Identifiant conservé | Ancien affichage | Nouvel affichage | Sens conservé |
|---|---|---|---|
| 17.1 | 17.1 | A.1 | Vitesse angulaire |
| 17.2 | 17.2 | A.2 | Coordonnées d'un mouvement circulaire |
| 17.3 | 17.3 | A.3 | Construire un modèle à partir de données |
| 17.4 | 17.4 | A.4 | Interpréter un modèle |
| 17.5 | 17.5 | A.5 | Interprétation ondulatoire |
| 17.6 | 17.6 | A.6 | Du mouvement circulaire au modèle temporel |
| 17.7 | 17.7 | A.7 | Construire un modèle périodique à partir d'observations |
| 17.8 | 17.8 | A.8 | Construire et valider un modèle périodique |

Les renvois vidéo existants gardent leurs identifiants historiques; le répertoire
les affiche comme des sections de l'annexe A. Les associations globales de
l'ancien chapitre 17 passent à l'annexe. Aucune capsule n'est attribuée par
inférence au chapitre des complexes. Les archives, éditions publiées, rapports
historiques et examens restent inchangés : leurs numéros suivent leur propre
édition.

Contrôles prévus : égalité manuel–cahier des 134 identifiants; conservation des
126 identifiants historiques; vérification de chaque étiquette, chemin, titre
et numéro affiché; conservation intégrale des sources circulaires déplacées;
tests indépendants de calcul complexe, racines et équations; vérification
autonome sans PyYAML, intégration vidéo explicite, compilation des trois PDF et
inspection visuelle des pages affectées. Le rapport de révision distinguera ces
preuves d'une validation exhaustive ou d'une approbation de publication.
