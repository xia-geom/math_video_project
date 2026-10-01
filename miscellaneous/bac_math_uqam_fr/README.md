# Film court du baccalauréat en mathématiques

La narration de Montréal, de la recherche et de la conclusion est découpée en prises indépendantes dans `promo_beats.py`. Chaque changement de plan attend la fin de sa prise, sans estimation au nombre de mots. `semantic_timeline.json` consigne les plans sur l’horloge réelle du rendu.

Les photographies gardent leur contexte : identité UQAM, atelier public de mathématiques (2019), séance de rédaction à la Bibliothèque des sciences (2026) et vie étudiante. La même photo d'atelier revient volontairement dans les deux plans de discussion, sans prétendre montrer un cours régulier ou un mentorat précis. La banque de photos de la Salle de presse UQAM est la source visuelle par défaut pour les plans institutionnels et les pavillons; les pages officielles UQAM plus récentes restent possibles lorsqu’elles montrent mieux le lieu ou l’activité recherchée. Voir `../../assets/uqam_promo/PHOTO_POLICY.md`.

Le plan de recherche présente maintenant trois domaines sur des cartes courtes et équilibrées : **CIRGET** (géométrie et topologie), **LaCIM** (combinatoire et informatique mathématique) et **STATQAM** (statistique et science des données). Les listes d’universités et les explications institutionnelles longues ont été retirées de l’écran; les sources officielles restent consignées dans le builder.

Révision du 1er octobre : le sigle CIRGET reste écrit sur la carte et se prononce « Cirgé »; la conclusion dit « plusieurs portes ». Le débit de l'ouverture est aligné sur celui du reste du film (+2 %) et l'export ajoute un fondu audio de 0,15 s contre le bruit d'attaque. Le logo officiel clôt le film sur fond blanc lorsque `UQAM_USE_OFFICIAL_LOGO=1` et `UQAM_LOGO_APPROVED=1` sont sélectionnés explicitement.

Les portraits ne sont pas des témoignages enregistrés. Les crédits non affichés doivent accompagner la description de diffusion; l’inventaire par actif distingue explicitement les deux modes. Autorisations de diffusion et d’identité visuelle ne sont jamais déduites des tests.

Après un nouveau clonage ou lorsqu’un actif a été remplacé, exécuter `python miscellaneous/bac_math_uqam_fr/fetch_uqam_promo_assets.py` avant le rendu. Le rendu Manim lui-même reste hors ligne.

`build_release.py` conserve le contrôle séparé d’inspection brute et refuse les rendus périmés. Il produit aussi les images de contrôle de l’export encodé et des statistiques SRT. Un passage automatisé ne certifie ni l’écoute, ni la lecture, ni la diffusion institutionnelle. La voix MAI existante et l’absence de musique restent les valeurs de référence.

La valeur effective du débit et de l’appel à l’action est celle résolue par le parent; la même valeur est transmise au processus de rendu et au manifeste. Les anciennes constantes de maintien sont conservées pour compatibilité, mais ne pilotent plus la sortie des plans Montréal/recherche/conclusion.
