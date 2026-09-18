# Les maths ouvrent des portes — UQAM, 20 secondes

Troisième production de la [collection UQAM](../README.md). Les deux autres films,
les leçons et `tools/tts.py` ne sont pas modifiés par cette révision.

## Message et images

**Une photo UQAM, une idée à la fois.** Seulement les deux photographies de la
page 1 du PDF fourni : le groupe au tableau et le pavillon UQAM de nuit. Les pages
21–23 fondent le parcours majeure → certificat → B.Sc. Sciences. Les intitulés
« Communication », « Finance », « Économique » et « Informatique » sont conservés.
La durée « 2 ans à temps plein » vient du brief et concerne la majeure, pas un
baccalauréat complet garanti en deux ans. Voir [les sources](sources/accueil_septembre_2026.md).

### Narration raccourcie

> À l’UQAM, les maths ouvrent des portes. Une majeure en maths ou statistique.
> Puis un certificat : communication, finance, économique ou informatique.
> Un bac en sciences. Plusieurs horizons.

Le profil reste `MAI-Voice-2`, à `+2%`. Aucun changement automatique de voix ou de
débit n’est utilisé pour faire tenir le texte. « 2 ans » et « à temps plein »
restent à l’écran. Les sous-titres transcrivent la voix, pas tous les textes écran.

### Montage

| Repère du storyboard muet | Photo | Composition |
|---|---|---|
| 0–4 s | Pavillon | Les maths ouvrent des portes. |
| 4–9 s | Groupe au tableau | 2 ans en maths ou statistique / à temps plein → une majeure |
| 9–16 s | Même photo, sans coupure | Puis, un certificat / deux domaines à la fois |
| 16–20 s | Pavillon | Un bac en sciences. / Plusieurs horizons. / math.uqam.ca |

Les deux paires sont `Communication · Finance`, puis `Économique · Informatique`.
Leur changement est un repère visuel, **pas une synchronisation mot à mot certifiée**.
Le fond ne disparaît plus entre les deux séquences étudiantes. Le texte est placé
plus bas, sur une zone assombrie, et non au centre des visages. Le marquage muet
reste au-dessus des photographies. Aucun nouveau logo ou image de banque n’est ajouté.

## Correction importante : qualité des sources

Les JPEG déjà suivis dans Git mesurent seulement **384×216** et **256×144**.
Leur agrandissement avait été attribué à tort à la qualité du PDF. Celui-ci contient
des images intégrées de **1387×640** et **2012×1128**. Les mêmes cadrages peuvent
être récupérés en **903×508** et **1112×625**, sans réduction intermédiaire.

Les nouvelles images sont des crops natifs, pas des photos nativement 1920×1080.
Leur agrandissement résiduel est enregistré dans `asset_quality.json`.

Le pack de photos natives livré avec l’audit se décompresse à la racine du dépôt.
Il ajoute seulement `miscellaneous/bac_sciences_ouvertures_fr/assets/native/`.
Les pixels sont vérifiés contre les empreintes inscrites dans `project.json`.
**Les PNG natifs ne sont pas encore inclus dans la branche de revue**; le script
ci-dessous les reconstruit à partir du PDF original, ou le pack les fournit.
Les anciens JPEG restent des miniatures de contrôle; ils ne permettent plus un rendu narré de revue.

```bash
python -m pip install -r miscellaneous/bac_sciences_ouvertures_fr/requirements-assets.txt
python miscellaneous/bac_sciences_ouvertures_fr/restore_slide_photos.py \
  --pdf "/chemin/Accueil Nouveaux-2026-Septembre.pdf"
```

L’extraction vérifie le PDF, la page, les dimensions et les pixels. Elle ne
retouche pas les personnes, ne génère aucun détail et ne suppose aucune nouvelle
autorisation de diffusion. Un répertoire non vide n’est jamais écrasé.

## Pipeline local au projet

```text
project.json                     texte, rythme préféré, marges et empreintes
restore_slide_photos.py           extraction facultative du PDF original
project.py                       validation du contenu, des images et du SRT
narration.py                      AzureService + tools/tts.py → clips figés
                                 → cache par requête → mesure FFprobe
                                 → audio/audio.json et fichiers MP3 exacts
timing.py                        allocation globale des 20 secondes en images
                                 → rejet avant rendu si le budget est impossible
bac_sciences_ouvertures_fr_scene.py
                                 lecture des clips vérifiés + animation Manim
build.py                         orchestration, validation, preuves et variantes
```

Les durées 4/5/7/4 sont des préférences, **pas quatre minima indépendants**.
Le plan global redistribue les pauses disponibles, jamais la parole. Chaque
séquence réserve 0,4 s avant l’audio pour rendre le texte visible. La fin conserve
au moins une seconde après la voix. Les minima de lecture restent explicites.
Si l’ensemble ne tient pas, le rendu est refusé avant les calculs graphiques.
Les fichiers audio et le détail par séquence sont conservés pour diagnostic.

Le cache est dans `media/voiceovers/uqam_ouvertures_frozen/`, hors sources Git.
Sa clé dépend du texte SSML, de la voix, de la configuration et du helper TTS.
Une deuxième qualité de rendu réutilise les mêmes octets; le renderer n’appelle
pas Azure. Il n’y a ni recherche automatique d’une prise plus courte, ni
`atempo`, ni découpage de la fin de la phrase, ni faux audio dans un aperçu muet.

## Construire

L’environnement Manim/Azure existant et ses versions sont conservés.

```bash
python -m pip install -r miscellaneous/bac_sciences_ouvertures_fr/requirements.txt

# Aperçu. Sans pack natif : marquage explicite des images de contrôle.
python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode silent --quality qh

# Vérifier la voix avant de lancer un rendu : aucune image native nécessaire ici.
# SPEECH_KEY/SPEECH_REGION restent dans l’environnement; la région du profil
# MAI est celle définie dans tools/tts.py (canadacentral).
python miscellaneous/bac_sciences_ouvertures_fr/build.py \
  --mode azure --quality qh --audio-only --output dist/uqam-audio-review

# Réutiliser exactement la prise mesurée; pack natif requis pour cette étape.
python miscellaneous/bac_sciences_ouvertures_fr/build.py \
  --mode azure --quality qh \
  --audio-package dist/uqam-audio-review/audio/audio.json
```

`--source-pdf` permet aussi la récupération initiale des photos dans le builder.
Les chemins de sortie existants sont refusés. Le cache peut être placé ailleurs
par `UQAM_OUVERTURES_AUDIO_CACHE`; les images par `UQAM_OUVERTURES_SOURCE_ASSETS`.
Pour protéger un répertoire de travail comportant d’autres modifications, utiliser
un **worktree Git séparé**, sans `reset --hard`, `clean`, ni écrasement de fichiers.

## Preuves et limites

`status.json` reflète aussi les échecs. `timing_plan.json` détaille les durées
mesurées, les marges, les débuts/fins d’audio et le budget. Le SRT utilise les
intervalles d’audio, et non la totalité des pauses visuelles. Le MP4 propre reste
la référence de montage; la variante incrustée est également inspectable.
Les images de contrôle couvrent les transitions, les deux paires de domaines et
la fin, dans **les deux versions**.

GitHub Actions teste et rend un aperçu muet sur PR. Azure est réservé à une demande
manuelle et requiert les photos natives; les erreurs de synthèse/budget ne laissent
plus un état trompeur `ready`. Un workflow vert ne signifie pas narration réalisée.

Un aperçu muet, un rendu narré, une écoute complète et une autorisation de diffusion
restent des étapes distinctes. `release_ready` reste faux. Aucune fusion dans main,
aucune publication et aucune modification des deux autres films ne sont automatiques.
