# Cours de mathématiques — catalogue unifié

La source unique est [programme_principal_fr.yaml](programme_principal_fr.yaml).
Les 37 leçons principales suivent le syllabus ; les six vidéos d'erreurs
fréquentes continuent la séquence globale de 38 à 43 dans leur collection propre.
Les films promotionnels et l'identité visuelle sont exclus de cette numérotation.

[Numérotation et liens vers les 43 sources](NUMBERING.md) ·
[Correspondance avec les anciens codes et chemins](LEGACY_NUMBERING.md) ·
[Index exploitable par les outils](playlist.csv).

Les dix ajouts sont placés dans leurs chapitres, pas ajoutés artificiellement à
la fin. L'élimination précède Cramer, puis la programmation linéaire. Les deux
preuves de géométrie et la notation sigma restent à la fin du parcours principal.
La preuve de Pythagore est une leçon liée à la trigonométrie, non un prérequis
vidéo à voir plus tard ; la connaissance scolaire du théorème est explicitée.

`extension_syllabus_fr.yaml` ne contient plus de seconde copie des chemins,
objectifs ou prérequis : ce fichier sélectionne seulement les dix productions
nouvelles dans le catalogue commun. Les nombres complexes restent facultatifs,
non implémentés et sans numéro de vidéo réservé.

## Utilisation

```bash
python tools/course_catalog.py check
python tools/course_catalog.py --write-indexes
python scripts/render_curriculum.py --list
# Le numéro est global, même avec --track errors.
python scripts/render_curriculum.py --track programme --order 15 --quality ql --render --disable-voiceover
python scripts/render_curriculum.py --track errors --order 39 --quality ql --render --disable-voiceover
# Les anciens alias S restent acceptés pour sélectionner le lot de nouvelles productions.
python scripts/render_syllabus_expansion.py --check-only
python scripts/render_syllabus_expansion.py --ids S01,S02 --mode silent
```

La classe publique de chaque scène est préservée. `scripts/render.sh` résout les
anciens chemins exacts grâce à la correspondance et utilise le même nom de
livraison que le rendu par curriculum. Les dossiers de sources, les noms des
sources, les sorties, les index et les sélections ont le même numéro global.
Les rapports historiques ne changent pas de sens : leurs codes P/E/S demeurent
historiques, avec une correspondance explicite vers le présent catalogue.

## Vérification et état des vidéos

Une source intégrée et numérotée n'est pas une vidéo publiée. Les tests de
catalogue, de mathématiques, de rendu, d'images, de mouvement et d'audio sont
distincts. Les dix nouvelles leçons conservent leur statut de production ; aucune
approbation audiovisuelle n'est déduite du changement de numéro.

Les anciens MP4 locaux, archives de rendu et copies Drive ne sont ni déplacés ni
effacés par la migration Git. Les prochains rendus emploient les nouveaux noms ;
`numbering_migration.json` conserve les anciens noms pour une migration locale
explicite. Ne pas réutiliser un MP4 simplement parce que son ancien numéro
correspond à un nouveau numéro.

Lire [le standard d'enseignement](../docs/TEACHING_STANDARD.md) avant de créer ou
modifier une leçon. Les résultats datés se trouvent dans
[le rapport d'audit global](../reports/course_audit/2026-09-20/AUDIT.md).
