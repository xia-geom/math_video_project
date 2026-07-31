# Production Scene Audit Index

## Summary

- Scenes in scope: 20
- Rendered this run: 0
- Audited: 20
- Render failures: 0
- Findings: 0 blocker, 24 warning, 6 polish

## Scene Results

| Scene | Render | Audit | Findings | Report | Contact Sheet |
|---|---|---|---:|---|---|
| `PythagoreAireFR` | existing | audited | B:0 W:1 P:0 I:6 | [open](PythagoreAireFR_audit.md) | [open](PythagoreAireFR_audit_frames/contact_sheet.png) |
| `FonctionsDomaineImageFR` | existing | audited | B:0 W:1 P:1 I:6 | [open](FonctionsDomaineImageFR_audit.md) | [open](FonctionsDomaineImageFR_audit_frames/contact_sheet.png) |
| `ModelesLineairesQuadratiques` | existing | audited | B:0 W:1 P:1 I:6 | [open](ModelesLineairesQuadratiques_audit.md) | [open](ModelesLineairesQuadratiques_audit_frames/contact_sheet.png) |
| `SigmaSommeBoucleFR` | existing | audited | B:0 W:2 P:0 I:6 | [open](SigmaSommeBoucleFR_audit.md) | [open](SigmaSommeBoucleFR_audit_frames/contact_sheet.png) |
| `VariablesEtPolynomes` | existing | audited | B:0 W:2 P:0 I:7 | [open](VariablesEtPolynomes_audit.md) | [open](VariablesEtPolynomes_audit_frames/contact_sheet.png) |
| `Logarithme` | existing | audited | B:0 W:1 P:1 I:7 | [open](Logarithme_audit.md) | [open](Logarithme_audit_frames/contact_sheet.png) |
| `SineCurveUnitCircle` | existing | audited | B:0 W:1 P:0 I:6 | [open](SineCurveUnitCircle_audit.md) | [open](SineCurveUnitCircle_audit_frames/contact_sheet.png) |
| `CompleteTheSquare` | existing | audited | B:0 W:0 P:0 I:7 | [open](CompleteTheSquare_audit.md) | [open](CompleteTheSquare_audit_frames/contact_sheet.png) |
| `GraphProperties` | existing | audited | B:0 W:2 P:1 I:6 | [open](GraphProperties_audit.md) | [open](GraphProperties_audit_frames/contact_sheet.png) |
| `CircleAreaFR` | existing | audited | B:0 W:2 P:1 I:6 | [open](CircleAreaFR_audit.md) | [open](CircleAreaFR_audit_frames/contact_sheet.png) |
| `RacineProduitHypothesesFR` | existing | audited | B:0 W:0 P:0 I:7 | [open](RacineProduitHypothesesFR_audit.md) | [open](RacineProduitHypothesesFR_audit_frames/contact_sheet.png) |
| `PrincipeFondamentalDenombrementFR` | existing | audited | B:0 W:1 P:0 I:6 | [open](PrincipeFondamentalDenombrementFR_audit.md) | [open](PrincipeFondamentalDenombrementFR_audit_frames/contact_sheet.png) |
| `PermutationArrangementCombinaisonFR` | existing | audited | B:0 W:1 P:0 I:6 | [open](PermutationArrangementCombinaisonFR_audit.md) | [open](PermutationArrangementCombinaisonFR_audit_frames/contact_sheet.png) |
| `RepetitionsDenombrementFR` | existing | audited | B:0 W:1 P:0 I:6 | [open](RepetitionsDenombrementFR_audit.md) | [open](RepetitionsDenombrementFR_audit_frames/contact_sheet.png) |
| `VecteursDeplacementComposantesFR` | existing | audited | B:0 W:0 P:0 I:6 | [open](VecteursDeplacementComposantesFR_audit.md) | [open](VecteursDeplacementComposantesFR_audit_frames/contact_sheet.png) |
| `OperationsVecteursFR` | existing | audited | B:0 W:2 P:0 I:6 | [open](OperationsVecteursFR_audit.md) | [open](OperationsVecteursFR_audit_frames/contact_sheet.png) |
| `VecteursR2R3FR` | existing | audited | B:0 W:1 P:0 I:6 | [open](VecteursR2R3FR_audit.md) | [open](VecteursR2R3FR_audit_frames/contact_sheet.png) |
| `MatricesLireEtAppliquerFR` | existing | audited | B:0 W:1 P:0 I:6 | [open](MatricesLireEtAppliquerFR_audit.md) | [open](MatricesLireEtAppliquerFR_audit_frames/contact_sheet.png) |
| `OperationsMatricesFR` | existing | audited | B:0 W:3 P:0 I:6 | [open](OperationsMatricesFR_audit.md) | [open](OperationsMatricesFR_audit_frames/contact_sheet.png) |
| `DeterminantEtMatriceInverseFR` | existing | audited | B:0 W:1 P:1 I:6 | [open](DeterminantEtMatriceInverseFR_audit.md) | [open](DeterminantEtMatriceInverseFR_audit_frames/contact_sheet.png) |

## Recommended Commands

```bash
./.venv/bin/python scripts/audit_all_scenes.py
./.venv/bin/python scripts/audit_all_scenes.py --no-render
./.venv/bin/python scripts/audit_all_scenes.py --scene-class GraphProperties
```

Use full narrated renders with Azure credentials for final audio/SRT QA.
