# Les maths ouvrent des portes — capsule UQAM de 20 secondes

Troisième vidéo de la [collection UQAM](../README.md), parallèle aux films existants de présentation longue et de promotion générale.

## Message

Une base en mathématiques ou en statistique peut s’inscrire dans un parcours ouvert à d’autres disciplines. Le chemin montré est **majeure, puis certificat complémentaire, puis baccalauréat en sciences par cumul**. Deux ans ne sont pas présentés comme la durée totale du bac.

Source : diapositives 21–23 du PDF fourni, avec la nuance concernant la durée explicitée dans [la fiche source](sources/accueil_septembre_2026.md). Les conditions de chaque programme restent à vérifier auprès de la direction.

## Narration française

> Les maths ouvrent des portes. Deux ans en maths ou en statistique, pour une majeure. Puis un certificat : communication, finance, économique ou informatique. Un bac en sciences par cumul, à ton image. À l’UQAM.

Le texte et les sous-titres ont une seule source de vérité : [project.json](project.json).

## Découpage

| Temps de l’aperçu | Image | Fonction |
|---|---|---|
| 0–3 s | « Les maths, et après ? » | Accroche inclusive : garder ses options ouvertes |
| 3–8 s | « 2 ans », maths ou statistique, « Une majeure » | Expliquer le socle sans le confondre avec le diplôme final |
| 8–15 s | Majeure + un certificat au choix; quatre domaines lisibles | Montrer le complément disciplinaire |
| 15–20 s | « Un bac en sciences à ton image », « par cumul », UQAM et `math.uqam.ca` | Nommer l’aboutissement et donner un point de contact |

L’aperçu muet dure 20 secondes. En mode Azure, chaque plan attend sa vraie prise; un léger dépassement jusqu’à 22 secondes est accepté. Une prise trop longue produit une erreur de validation, jamais une coupe audio ou une accélération cachée. Le texte est à raccourcir ou le débit à ajuster explicitement si nécessaire.

## Technique

Manim Community, `VoiceoverScene`, `AzureService` et les fonctions communes de `tools/tts.py`. Profil promotionnel existant `MAI-Voice-2`, débit `+2%`, sans changement de la voix des leçons ou des deux autres films. Pas de musique; pas de photo empruntée ni de logo officiel. Le nom UQAM est composé comme du texte ordinaire.

Le fond blanc, l’encre sombre, l’accent bleu et Roboto prolongent le clip promotionnel existant. L’aperçu seul peut utiliser DejaVu Sans lorsque Roboto manque; le manifeste le signale. Le rendu narré exige Roboto. La zone basse reste réservée aux sous-titres. Le qualificatif « Parcours type à temps plein. Conditions selon les programmes. » reste visible.

## Installer dans un environnement isolé

Depuis la racine du dépôt, après installation de Cairo/Pango et FFmpeg :

```bash
python3 -m venv .venv-ouvertures
.venv-ouvertures/bin/python -m pip install -r miscellaneous/bac_sciences_ouvertures_fr/requirements.txt
```

Ce fichier garde les versions Manim/voiceover déjà utilisées par le clip général; il ne remplace ni le verrou du film long ni le `pyproject.toml` des leçons.

## Construire

Aperçu clairement marqué comme muet, sans compte Azure :

```bash
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode silent --quality ql
```

Rendu narré de contrôle en haute définition :

```bash
# SPEECH_KEY et SPEECH_REGION doivent déjà être présents dans l’environnement.
# Le profil MAI du dépôt utilise SPEECH_REGION=canadacentral.
.venv-ouvertures/bin/python miscellaneous/bac_sciences_ouvertures_fr/build.py --mode azure --quality qh
```

Les anciens noms d’environnement Azure sont pris en charge par la fonction commune. Aucun secret ne doit être écrit dans Git, dans `project.json` ou dans un rapport. Surcharges explicites : `UQAM_OUVERTURES_VOICE` et `UQAM_OUVERTURES_RATE`. La voix résolue, le débit et la police effective sont enregistrés.

Pour utiliser directement le lanceur Manim commun, avec son environnement `.venv` déjà installé :

```bash
UQAM_OUVERTURES_MODE=silent bash scripts/render.sh miscellaneous/bac_sciences_ouvertures_fr/bac_sciences_ouvertures_fr_scene.py BacSciencesOuverturesFR ql
```

Cette dernière commande est un rendu brut : utiliser `build.py` pour les sous-titres issus de la chronologie réelle et les contrôles de livraison.

## Livrables et sécurité contre les écrasements

`build.py` crée un nouveau dossier horodaté dans `dist/bac_sciences_ouvertures_fr/`. Il refuse un dossier de sortie déjà existant et n’a pas de mode de réutilisation d’un ancien rendu.

Il écrit un MP4 propre, un MP4 sous-titré, un SRT, une piste WAV pour Azure, la chronologie réelle, quatre images de contrôle, les informations `ffprobe`, le journal et un manifeste avec empreintes des sources et sorties. Les noms distinguent `silent_preview` et `azure_review`. Il ne publie rien sur Drive, sur une plateforme vidéo ou dans une release.

## Tests et GitHub Actions

```bash
python -m pytest tests/test_uqam_ouvertures.py -q
```

Le workflow dédié `UQAM — ouvertures 20 s` ne reconstruit pas les deux autres films. Une pull request touchant ce projet lance les tests et l’aperçu muet. Pour une PR du dépôt lui-même, une narration est aussi tentée si les secrets Speech sont présents; les PR externes n’y ont pas accès. Le lancement manuel permet de demander explicitement `silent` ou `azure`.

L’absence de secrets est enregistrée comme `blocked`, pas comme une narration réussie. Les artefacts contiennent l’aperçu et le rapport même si la narration manque. `release_ready` reste faux : le contrôle du programme, la relecture visuelle et l’écoute complète ne sont pas déduits des tests techniques.
