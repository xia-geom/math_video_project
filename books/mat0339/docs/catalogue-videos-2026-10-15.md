# Répertoire de révision des capsules - 15 octobre 2026

Le répertoire autonome concerne les 43 identités du catalogue unifié et les
sources actives du manuel et du cahier, édition du 10 octobre 2026. Il sert à
retrouver une notion après le cours. Il ne modifie ni le texte pédagogique des
livres, ni leurs 126 sections, ni les éditions archivées.

## Source et précision des correspondances

`curriculum/video-map.json` conserve la carte historique par chapitre et ajoute
`catalogue_references`, indexé par `lesson_id`. Le générateur résout le numéro et
le titre depuis le catalogue commun. Les références du manuel et du cahier sont
indépendantes. Une section ciblée signifie une correspondance de notion, non un
corrigé complet ni une couverture de tous ses exercices.

Les renvois ont été établis en lisant les sources des leçons, leurs exemples
guidés lorsqu'ils existent et les sections des deux documents. Les index de
sections servent à contrôler l'identité, et les étiquettes présentes dans les
sources à contrôler que la cible existe toujours. Ce contrôle structurel ne
remplace pas une relecture sémantique après modification d'une leçon ou d'un livre.

Quelques distinctions importantes :

- La vidéo 15 renvoie au manuel 5.2, 5.3 et 5.4, mais au cahier 5.1, 5.2 et 5.3 :
  le problème explicite sur les trous est dans le cahier 5.1.
- La vidéo 43 renvoie séparément à la section 2.2 des deux documents : facteurs,
  termes et valeurs interdites y sont directement pertinents.
- La vidéo 09 privilégie l'addition et la soustraction graphiques; la section 3.4
  contient aussi d'autres opérations. Le renvoi ne prétend pas toutes les traiter.
- La vidéo 34 inclut des exemples guidés distinguant une valeur principale et
  toutes les solutions; les sections 16.3 et 16.4 correspondent à ces deux usages.
- La vidéo 35 sur l'aire du cercle est seulement rapprochée du chapitre 14. La
  démonstration n'est pas attribuée artificiellement à un exercice précis.
- La vidéo 36 démontre Pythagore : le manuel est rapproché du chapitre 15; le
  cahier 15.1 apporte une application directe aux triangles rectangles. Aucun
  de ces renvois ne présente une seconde copie de la preuve.
- La vidéo 37 sur sigma est un complément transversal sans section dédiée.
- La vidéo 39 renvoie au manuel 1.4, où la règle du produit est explicitement
  conditionnée à des facteurs non négatifs, et au cahier 1.6, qui demande de
  discuter cette égalité. Sa parenthèse complexe dépasse ces sections.
- Pour la vidéo 40, le manuel 3.1 définit l'égalité de fonctions; le cahier 2.2
  demande de comparer une fonction rationnelle et sa formule simplifiée, en
  contrôlant leurs domaines. Il ne reprend pas tous les cas de la vidéo.

## Régénération et limites

`python3 books/mat0339/scripts/video_map.py --write` régénère la carte Markdown
et `curriculum/catalogue-videos.tex`. Sans `--write`, la commande contrôle les
deux sorties. `make verify` inclut ce contrôle et les tests de correspondance.
La source LaTeX est autonome; le PDF de travail est exporté dans
`review_artifacts/teaching_navigation/catalogue/` et n'est pas une nouvelle
publication des livres.

Le document étudiant ne contient ni URL, ni chemin de code, ni code QR. Il
distingue explicitement une section, un chapitre thématique et un complément
transversal. L'existence d'une source vidéo n'atteste ni son rendu actuel, ni
son écoute, ni sa disponibilité publique. Les résultats des compilations et de
l'inspection des pages sont rapportés séparément dans le compte rendu de tâche.
