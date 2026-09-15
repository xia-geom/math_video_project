# Film court du baccalauréat en mathématiques

La narration de Montréal, de la recherche et de la conclusion est découpée en prises indépendantes dans `promo_beats.py`. Chaque changement de plan attend la fin de sa prise, sans estimation au nombre de mots. `semantic_timeline.json` consigne les plans sur l’horloge réelle du rendu.

Les photographies gardent leur contexte : activité mathématique, accueil Allô!, visite de bibliothèque et pôle de recherche. Les portraits ne sont pas des témoignages enregistrés. Les crédits non affichés doivent accompagner la description de diffusion; l’inventaire par actif distingue explicitement les deux modes. Autorisations de diffusion et d’identité visuelle ne sont jamais déduites des tests.

`build_release.py` conserve le contrôle séparé d’inspection brute et refuse les rendus périmés. Il produit aussi les images de contrôle de l’export encodé et des statistiques SRT. Un passage automatisé ne certifie ni l’écoute, ni la lecture, ni la diffusion institutionnelle. La voix MAI existante et l’absence de musique restent les valeurs de référence.

La valeur effective du débit et de l’appel à l’action est celle résolue par le parent; la même valeur est transmise au processus de rendu et au manifeste. Les anciennes constantes de maintien sont conservées pour compatibilité, mais ne pilotent plus la sortie des plans Montréal/recherche/conclusion.
