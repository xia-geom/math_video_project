# Périmètre éditorial MAT0339

Ces règles concernent uniquement `books/mat0339/`.

- Les sources actives sont dans `sources/manual/` et `sources/workbook/`; les archives dans `originals/` restent inchangées.
- Le manuel conserve initialement cinq parties et dix-sept chapitres. Les 126 identifiants de section stabilisent la correspondance avec le cahier; documenter toute renumérotation avant de l’appliquer.
- Rédiger les passages destinés aux étudiants en français. Justifier les méthodes, préserver les restrictions et montrer les vérifications des exemples.
- Ne pas importer les anciens statuts d’approbation de `mathbook-renew`. Une correction et une proposition de restructuration sont des changements distincts.
- Mettre à jour le registre des modifications et la correspondance manuel–cahier quand une consigne ou une réponse change.
- Vérifier le TEX final après la dernière retouche, compiler et inspecter les pages affectées. Distinguer contrôles automatisés, relecture mathématique et inspection graphique.
- Ne pas annoncer une validation PDF/UA sur la seule présence de balises PDF. Ne pas annoncer une couverture exhaustive du syllabus sans l’avoir vérifiée.
- Ne modifier ni les scènes ni la narration vidéo pour une tâche limitée au livre. Les correspondances vidéo sont des références, non des dépendances de compilation.
- Les PDF datés demandés sont permis sous `releases/`; caches, journaux, MP4, WAV et fichiers de polices ne le sont pas. Les versions de `releases/` sont immuables.
- Après une tâche, exécuter `make verify` et la compilation pertinente, puis enregistrer uniquement les changements de cette tâche. Aucun force-push, aucune fusion ou publication sans autorisation.
- À la fin du périmètre demandé, présenter les résultats et limites puis s’arrêter; ne pas recommencer des audits de complétion sans nouveau changement à vérifier.
