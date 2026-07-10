# Production Scene Audit Index

## Summary

- Scenes in scope: 11
- Rendered this run: 11
- Audited: 11
- Render failures: 0
- Findings: 0 blocker, 12 warning, 5 polish

## Scene Results

| Scene | Render | Audit | Findings | Report | Contact Sheet |
|---|---|---|---:|---|---|
| `PythagoreAireFR` | rendered | audited | B:0 W:1 P:0 I:7 | [open](PythagoreAireFR_audit.md) | [open](PythagoreAireFR_audit_frames/contact_sheet.png) |
| `FunctionIntuitive` | rendered | audited | B:0 W:1 P:0 I:8 | [open](FunctionIntuitive_audit.md) | [open](FunctionIntuitive_audit_frames/contact_sheet.png) |
| `RelationsDomaineImage` | rendered | audited | B:0 W:0 P:1 I:7 | [open](RelationsDomaineImage_audit.md) | [open](RelationsDomaineImage_audit_frames/contact_sheet.png) |
| `ModelesLineairesQuadratiques` | rendered | audited | B:0 W:1 P:1 I:7 | [open](ModelesLineairesQuadratiques_audit.md) | [open](ModelesLineairesQuadratiques_audit_frames/contact_sheet.png) |
| `SigmaSommeBoucleFR` | rendered | audited | B:0 W:0 P:0 I:9 | [open](SigmaSommeBoucleFR_audit.md) | [open](SigmaSommeBoucleFR_audit_frames/contact_sheet.png) |
| `VariablesEtPolynomes` | rendered | audited | B:0 W:2 P:0 I:8 | [open](VariablesEtPolynomes_audit.md) | [open](VariablesEtPolynomes_audit_frames/contact_sheet.png) |
| `Logarithme` | rendered | audited | B:0 W:1 P:1 I:8 | [open](Logarithme_audit.md) | [open](Logarithme_audit_frames/contact_sheet.png) |
| `LogarithmeProprietes` | rendered | audited | B:0 W:2 P:0 I:8 | [open](LogarithmeProprietes_audit.md) | [open](LogarithmeProprietes_audit_frames/contact_sheet.png) |
| `CompleteTheSquare` | rendered | audited | B:0 W:2 P:0 I:8 | [open](CompleteTheSquare_audit.md) | [open](CompleteTheSquare_audit_frames/contact_sheet.png) |
| `GraphProperties` | rendered | audited | B:0 W:1 P:1 I:8 | [open](GraphProperties_audit.md) | [open](GraphProperties_audit_frames/contact_sheet.png) |
| `CircleAreaFR` | rendered | audited | B:0 W:1 P:1 I:7 | [open](CircleAreaFR_audit.md) | [open](CircleAreaFR_audit_frames/contact_sheet.png) |

## Recommended Commands

```bash
./.venv/bin/python scripts/audit_all_scenes.py
./.venv/bin/python scripts/audit_all_scenes.py --no-render
./.venv/bin/python scripts/audit_all_scenes.py --scene-class GraphProperties
```

Use full narrated renders with Azure credentials for final audio/SRT QA.
