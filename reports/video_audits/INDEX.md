# Production Scene Audit Index

## Summary

- Scenes in scope: 11
- Rendered this run: 0
- Audited: 11
- Render failures: 0
- Findings: 0 blocker, 12 warning, 6 polish

## Scene Results

| Scene | Render | Audit | Findings | Report | Contact Sheet |
|---|---|---|---:|---|---|
| `PythagoreAireFR` | existing | audited | B:0 W:1 P:0 I:6 | [open](PythagoreAireFR_audit.md) | [open](PythagoreAireFR_audit_frames/contact_sheet.png) |
| `FonctionsDomaineImageFR` | existing | audited | B:0 W:1 P:1 I:7 | [open](FonctionsDomaineImageFR_audit.md) | [open](FonctionsDomaineImageFR_audit_frames/contact_sheet.png) |
| `ModelesLineairesQuadratiques` | existing | audited | B:0 W:2 P:1 I:6 | [open](ModelesLineairesQuadratiques_audit.md) | [open](ModelesLineairesQuadratiques_audit_frames/contact_sheet.png) |
| `SigmaSommeBoucleFR` | existing | audited | B:0 W:0 P:0 I:8 | [open](SigmaSommeBoucleFR_audit.md) | [open](SigmaSommeBoucleFR_audit_frames/contact_sheet.png) |
| `VariablesEtPolynomes` | existing | audited | B:0 W:2 P:0 I:7 | [open](VariablesEtPolynomes_audit.md) | [open](VariablesEtPolynomes_audit_frames/contact_sheet.png) |
| `Logarithme` | existing | audited | B:0 W:1 P:1 I:8 | [open](Logarithme_audit.md) | [open](Logarithme_audit_frames/contact_sheet.png) |
| `SineCurveUnitCircle` | existing | audited | B:0 W:2 P:1 I:7 | [open](SineCurveUnitCircle_audit.md) | [open](SineCurveUnitCircle_audit_frames/contact_sheet.png) |
| `CompleteTheSquare` | existing | audited | B:0 W:0 P:0 I:7 | [open](CompleteTheSquare_audit.md) | [open](CompleteTheSquare_audit_frames/contact_sheet.png) |
| `GraphProperties` | existing | audited | B:0 W:1 P:1 I:6 | [open](GraphProperties_audit.md) | [open](GraphProperties_audit_frames/contact_sheet.png) |
| `CircleAreaFR` | existing | audited | B:0 W:2 P:1 I:6 | [open](CircleAreaFR_audit.md) | [open](CircleAreaFR_audit_frames/contact_sheet.png) |
| `RacineProduitHypothesesFR` | existing | audited | B:0 W:0 P:0 I:7 | [open](RacineProduitHypothesesFR_audit.md) | [open](RacineProduitHypothesesFR_audit_frames/contact_sheet.png) |

## Recommended Commands

```bash
./.venv/bin/python scripts/audit_all_scenes.py
./.venv/bin/python scripts/audit_all_scenes.py --no-render
./.venv/bin/python scripts/audit_all_scenes.py --scene-class GraphProperties
```

Use full narrated renders with Azure credentials for final audio/SRT QA.
