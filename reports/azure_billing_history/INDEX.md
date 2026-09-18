# Azure billing history index

Archive generated: 2026-09-18 (America/Toronto)

This is the redacted human-readable index for the locally retained Azure billing archive. Complete API responses, invoice PDFs, transaction exports, Cost Details manifests, and Cost Details CSVs are stored under `raw/`. That directory is ignored by Git because it contains full billing identifiers and personal billing records.

## Billing scope discovered

- One accessible individual Microsoft Customer Agreement billing account, status Active.
- Two accessible billing profiles. The Azure for Students subscription is linked to the active monthly usage-based profile; the other profile contains two zero-dollar historical invoices and an expired free-account limit.
- One billing subscription: Azure for Students (`…9bd0`), status Active, monthly billing, auto-renew Off.
- One invoice section under each accessible billing profile.
- Billing currency: CAD.
- Full account, profile, invoice-section, subscription, and tenant IDs are retained only in the local raw exports.

## Available invoices

Azure returned eight invoices from the subscription start date, 2026-02-15, through the audit date. The March period has two invoices because both accessible billing profiles produced one.

The **Azure usage cost** column uses the invoice's billed amount. **Credits applied** shows the magnitude of invoice credits that reduced that usage. Amount due is the current amount due reported by Azure.

| Invoice period | Profile | Azure usage cost | Credits applied | Tax | Amount due | Payment status | Principal resources / services | PDF |
|---|---|---:|---:|---:|---:|---|---|---|
| 2026-02-15–2026-02-28 | Historical profile | CAD 0.00 | CAD 0.00 | CAD 0.00 | CAD 0.00 | Paid | No billable usage | [Invoice](raw/invoices/2026-02_legacy-profile_invoice.pdf) |
| 2026-03-01–2026-03-31 | Azure for Students | CAD 0.13 | CAD 0.13 | CAD 0.00 | CAD 0.00 | Paid | XIAXIAOVOICE; Foundry Tools / Azure Speech | [Invoice](raw/invoices/2026-03_invoice.pdf) |
| 2026-03-01–2026-03-31 | Historical profile | CAD 0.00 | CAD 0.00 | CAD 0.00 | CAD 0.00 | Paid | No billable usage | [Invoice](raw/invoices/2026-03_legacy-profile_invoice.pdf) |
| 2026-04-01–2026-04-30 | Azure for Students | CAD 0.19 | CAD 0.19 | CAD 0.00 | CAD 0.00 | Paid | XIAXIAOVOICE; Foundry Tools / Azure Speech | [Invoice](raw/invoices/2026-04_invoice.pdf) |
| 2026-05-01–2026-05-31 | Azure for Students | CAD 28.67 | CAD 28.67 | CAD 0.00 | CAD 0.00 | Paid | math-rag-mcp-test; Container Registry; Storage | [Invoice](raw/invoices/2026-05_invoice.pdf) |
| 2026-06-01–2026-06-30 | Azure for Students | CAD 71.98 | CAD 71.98 | CAD 0.00 | CAD 0.00 | Paid | math-rag-mcp-test; Container Registry; Storage | [Invoice](raw/invoices/2026-06_invoice.pdf) |
| 2026-07-01–2026-07-31 | Azure for Students | CAD 41.60 | CAD 38.32 | CAD 0.49 | CAD 0.00 | Paid | math-rag-mcp-test; XIAXIAOVOICE; Container Registry; Storage | [Invoice](raw/invoices/2026-07_invoice.pdf) |
| 2026-08-01–2026-08-31 | Azure for Students | CAD 0.13 | CAD 0.00 | CAD 0.02 | CAD 0.00 | Paid | XIAXIAOVOICE; Foundry Tools / Azure Speech | [Invoice](raw/invoices/2026-08_invoice.pdf) |

Across the linked Azure for Students invoices, Azure reported CAD 142.70 in billed usage, CAD 139.29 in credits, CAD 0.51 in tax, and CAD 4.22 in completed payments. All invoices currently report Paid and CAD 0.00 due.

## Invoice documents

- Invoice PDFs downloaded: **8 of 8 available**.
- Tax receipts listed by Azure: **0**.
- Credit notes listed by Azure: **0**.
- Void notes listed by Azure: **0**.

Both the billing-profile and broader billing-account inventories were checked. Every returned document had kind `Invoice`; Azure exposed no tax receipt or credit note to download.

## Transaction exports

One raw JSON transaction export is stored for every invoice under `raw/transactions/`:

| Invoice period / profile | Transactions returned |
|---|---:|
| 2026-02 historical | 0 |
| 2026-03 Azure for Students | 2 |
| 2026-03 historical | 0 |
| 2026-04 Azure for Students | 2 |
| 2026-05 Azure for Students | 8 |
| 2026-06 Azure for Students | 8 |
| 2026-07 Azure for Students | 11 |
| 2026-08 Azure for Students | 2 |

The raw transaction records preserve product, service, invoice, quantity, price, credit, tax, and transaction-amount fields returned by Azure. No payment-card details were requested or exported.

## Monthly Cost Details reports

Cost Details uses subscription-scope ActualCost reports. Monthly CSVs are stored under `raw/cost_details/`.

| Usage period | Cost Details total | Principal resources / services | CSV |
|---|---:|---|---|
| 2026-02-15–2026-02-28 | CAD 0.000000 | No cost data | [CSV](raw/cost_details/2026-02_cost_details.csv) |
| 2026-03-01–2026-03-31 | CAD 0.149167 | XIAXIAOVOICE; Foundry Tools | [CSV](raw/cost_details/2026-03_cost_details.csv) |
| 2026-04-01–2026-04-30 | CAD 0.196257 | XIAXIAOVOICE; Foundry Tools | [CSV](raw/cost_details/2026-04_cost_details.csv) |
| 2026-05-01–2026-05-31 | CAD 28.738910 | math-rag-mcp-test; Container Registry; Storage | [CSV](raw/cost_details/2026-05_cost_details.csv) |
| 2026-06-01–2026-06-30 | CAD 72.067611 | math-rag-mcp-test; Container Registry; Storage | [CSV](raw/cost_details/2026-06_cost_details.csv) |
| 2026-07-01–2026-07-31 | CAD 41.673822 | math-rag-mcp-test; XIAXIAOVOICE; Container Registry; Storage | [CSV](raw/cost_details/2026-07_cost_details.csv) |
| 2026-08-01–2026-08-31 | CAD 0.163274 | XIAXIAOVOICE; Foundry Tools | [CSV](raw/cost_details/2026-08_cost_details.csv) |
| 2026-09-01–2026-09-18 | CAD 1.185825 | XIAXIAOVOICE; Foundry Tools | [CSV](raw/cost_details/2026-09_cost_details.csv) |

Cost Details totals retain Azure's unrounded usage precision. Invoice billed amounts can differ slightly because invoices use their own billing cutoffs and displayed rounding.

## When the Azure for Students credit reached zero

The invoice evidence establishes that the credit was still available through June and was exhausted during July:

- March through June usage was fully offset by credits.
- July billed usage was CAD 41.60, but only CAD 38.32 of credit remained. The remaining CAD 3.28 became taxable and was paid.
- August received no credit and was charged normally.

Using the July Cost Details report, cumulative July ActualCost first exceeded the remaining CAD 38.32 on **2026-07-17**. This is the best-supported usage date for the credit reaching zero. The July invoice formally recorded the exhaustion when it was issued in early August. Azure's current accessible credit balance is also zero.

## Local archive inventory

- `raw/discovery/`: billing accounts, profiles, invoice sections, billing subscription, and both invoice inventories.
- `raw/invoices/`: eight PDFs plus temporary download-response records.
- `raw/transactions/`: one complete API export for each of the eight invoices.
- `raw/cost_details/`: eight monthly CSVs plus request, polling, and manifest records.

The raw directory intentionally preserves Azure's original identifiers and API fields. It must remain local and must not be committed, shared, or uploaded without a separate redaction review.

## Safety record

- Read-only list, get, download, report-generation, and polling operations only.
- No API keys, service secrets, payment-card details, or environment secrets were requested.
- No billing profile, subscription, resource, SKU, payment method, budget, quota, or deployment was modified.
- Human-readable identifiers and personal contact data are redacted in this index.
