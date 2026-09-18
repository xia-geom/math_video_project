# Azure Speech and billing audit

Audit time: 2026-09-18 (America/Toronto)
Scope: read-only Azure Resource Manager, Azure Monitor, Cost Management, Consumption, and Billing queries

## Executive findings

- The signed-in tenant is **UQAM** (`…506f`). One subscription is accessible: **Azure for Students** (`…9bd0`). It is the active/default subscription and its state is **Enabled**.
- Azure contains one `Microsoft.CognitiveServices/accounts` resource. It is the Speech Services account **XIAXIAOVOICE** in resource group **uqamzure**.
- **XIAXIAOVOICE is in `canadacentral` and uses S0 (Standard), not F0.**
- September 1–18 actual Azure cost is **CAD 1.185825**. All returned cost is under **Foundry Tools**, and the detailed ledger contains only Speech text-to-speech meters in `uqamzure`; therefore the Cognitive Services/Speech cost is also **CAD 1.185825**.
- August 1–31 actual Azure cost is **CAD 0.163274**, also entirely Speech text-to-speech. September-to-date is **CAD 1.022552 higher** (about **626.3% higher**, or **7.26×** August).
- The subscription's linked billing profile is active, monthly, and has its **spending limit Off**. The accessible credit balance is **USD 0.00** (estimated equivalent **CAD 0.00**), payments on account are **CAD 0.00**, and no subscription budget is configured.
- A 33-video MAI voice batch is unlikely to hit the observed request-rate quota if the existing sequential renderer is used. It will be billable. The 32 currently packaged subtitle files contain about 51,435 spoken characters; at the current Neural HD meter and September exchange rate, that corpus would cost about **CAD 1.57**. Allowing for the missing 33rd subtitle and changed scripts, **roughly CAD 1.6–2.0** is a reasonable planning estimate, not a guaranteed quote.

## Tenant and subscriptions

| Tenant | Tenant ID | Accessible subscription | Subscription ID | Active/default | State |
|---|---:|---|---:|---|---|
| UQAM | `…506f` | Azure for Students | `…9bd0` | Yes | Enabled |

The authenticated user identity was intentionally redacted. No other tenant or subscription was returned by the signed-in account.

## Cognitive Services inventory

| Account | Kind | Resource group | Region | SKU / tier | Provisioning | Endpoint |
|---|---|---|---|---|---|---|
| XIAXIAOVOICE | SpeechServices | uqamzure | **canadacentral** | **S0 / Standard** | Succeeded | `https://canadacentral.api.cognitive.microsoft.com/` |

This is the only Cognitive Services account returned, so it is also the resource requested in Canada Central.

Available account SKUs:

| SKU | Tier |
|---|---|
| F0 | Free |
| S0 | Standard |

The resource is currently S0. Listing available SKUs did not change the active SKU.

## Quota and measured usage

The Cognitive Services account usage endpoint returned an empty list. Azure therefore did not expose a monthly remaining-quota counter for this S0 account through that management endpoint. This must not be interpreted as zero usage or zero remaining capacity.

The account metadata reports these relevant request-rate rules:

- Neural speech synthesis: **200 requests per second**.
- Standard speech synthesis: **200 requests per second**.
- Batch text-to-speech job creation: **100 requests per 10 seconds**.

Azure Monitor measurements:

| Period | Synthesized characters metric | Total calls | Successful calls | Errors | Blocked by rate/quota |
|---|---:|---:|---:|---:|---:|
| 2026-09-01 through 2026-09-18 | 153 | 255 | 253 | 2 | **0** |
| 2026-08-01 through 2026-08-31 | 7,725 | 12 | 12 | 0 | **0** |

The `SynthesizedCharacters` monitor metric reflects the standard neural meter but does not include all Neural HD billing rows. The Consumption ledger is the more complete billing view:

| Period | Meter | Billed quantity | Cost (CAD) |
|---|---|---:|---:|
| September 1–18 | S1 Neural Text To Speech Characters | 153 characters | 0.003181 |
| September 1–18 | Neural HD Text to Speech Characters | 38,784 characters | 1.182644 |
| August 1–31 | S1 Neural Text To Speech Characters | 7,725 characters | 0.163274 |

No blocked call was recorded in either period. For 33 renders, the practical rate-limit risk is low as long as synthesis remains sequential or modestly parallel. The main constraint is billable character volume rather than a monthly F0 character allowance, because the account is S0.

## Cost Management comparison

| Cost period | Total Azure cost | Cognitive Services / Speech cost | Currency |
|---|---:|---:|---|
| 2026-09-01 through 2026-09-18 | 1.185825 | 1.185825 | CAD |
| 2026-08-01 through 2026-08-31 | 0.163274 | 0.163274 | CAD |

Cost Management returned one service category, `Foundry Tools`, for September. Consumption detail reconciled the total exactly to the two Speech text-to-speech meters above. August detail likewise contained only the Speech meter. Azure cost data can arrive after usage, so September-to-date can increase without another render during the reporting delay.

An initial previous-month query ending at `2026-09-01T00:00:00Z` included September 1 charges because Azure treated the endpoint as inclusive. The comparison above uses the August-only ledger through August 31. Subsequent grouped Cost Management retries were throttled with HTTP 429; the Consumption ledger supplied the corrected August total.

## Billing and subscription metadata

- Authorization source: role-based access.
- Subscription offer metadata: `PayAsYouGo_2014-09-01` quota policy; free-tier promotion recorded through **2027-02-15**.
- Billing account: active, individual, direct Microsoft Customer Agreement; read access is available.
- Linked billing subscription: active usage-based Microsoft Azure Plan, monthly billing, auto-renew Off.
- Linked billing profile: active; billing currency CAD; **spending limit Off**.
- Accessible credit balance: **USD 0.00**; estimated balance in billing currency: **CAD 0.00**.
- Payments on account: **CAD 0.00**.
- Subscription budgets returned: none.

Azure exposes another billing profile with an expired USD 200 free-account limit, but the current subscription is linked to the active profile whose spending limit is Off. Names, addresses, email addresses, phone numbers, complete tenant/subscription IDs, billing account IDs, billing profile IDs, and invoice section IDs are omitted from this report.

## Safety and audit limitations

- No API key operation was invoked; specifically, `listKeys` was not called.
- No environment file or Speech secret was read.
- No resource, SKU, deployment, billing setting, quota, or budget was created or modified.
- The audit used management-plane authentication from `az login` only.
- The cost estimate for 33 videos uses the current packaged subtitle text as a proxy. Actual billed characters depend on final narration/SSML, cache reuse, retry behavior, and the selected meter.
