---
name: lead-triage
description: "Automates real estate lead triage from a connected Google Sheet. Use this skill whenever the user says 'triage today's leads', 'triage leads', 'check new leads', 'score my leads', or asks to prioritize, follow up on, or process leads from their Google Sheet. Pulls rows where Status = 'New' from the leads sheet via the Google Drive/Sheets connector, scores each lead as High/Medium/Low priority based on budget-fit and lead source, sorts them, and drafts short professional follow-up messages for every High-Priority lead. Do not invent or hallucinate lead data — always pull real rows from the connected sheet first."
---

# Lead Triage (Real Estate)

Automates lead prioritization and follow-up drafting for a real estate agent, using a connected Google Sheet as the single source of truth.

## Step 1 — Pull the data (never invent leads)

Use the Google Drive/Sheets connector to find and read the leads sheet (default name: **"Real Estate Leads"** — if the user has a different sheet name in mind, ask once, then remember it for the rest of the conversation).

- Read **all rows**.
- Filter to only rows where **Status = "New"** (case-insensitive, trim whitespace). Ignore "Contacted", "Closed", or any other status.
- If the sheet can't be found or the connector isn't available, tell the user directly and stop — do not fabricate sample leads to fill the output.
- If zero rows have Status = "New", say so plainly and stop (no need to render an empty table).

## Step 2 — Parse Budget

Budget values in the sheet are strings like `৳85,00,000` or `N/A`.

- Strip the `৳` symbol and all commas, then parse as a number (Bangladeshi lakh-crore grouping, e.g. `85,00,000` → `8500000`).
- If the value is missing, blank, `N/A`, or not parseable as a number → treat budget as **unknown/incomplete**.

**Available inventory range: ৳50,00,000 – ৳3,00,00,000** (i.e. 5,000,000–30,000,000). A budget is "in range" if it falls within this range inclusive.

## Step 3 — Classify Source

Match the Source column against these two buckets using fuzzy/semantic matching (not just exact strings) — the sheet may contain variants:

- **Hot/Referral bucket** (any of): "Referral", "Hot Listing Inquiry", "Hot Lead", "Direct Referral", "Client Referral", or any phrase clearly containing "referral" or "hot".
- **Cold/Ad bucket** (any of): "Cold Call", "Facebook Ad", "Website Form", "Google Ad", "Ad", "Cold Lead", "Walk-in", or anything not matching the Hot/Referral bucket but still a recognizable lead source.

## Step 4 — Score each lead

Apply in this order:

1. **Low Priority** if:
   - Budget is unknown/incomplete (per Step 2), OR
   - Phone number is missing/blank, OR
   - Budget is a valid number but falls **outside** ৳50,00,000–৳3,00,00,000.
2. **High Priority** if budget is in range AND source is in the Hot/Referral bucket.
3. **Medium Priority** if budget is in range AND source is in the Cold/Ad bucket (or any other non-Hot source not covered above).

Every "New" lead must land in exactly one of these three buckets — never leave a lead unscored.

## Step 5 — Sort

Order the final list **High → Medium → Low**. Within the same priority tier, keep the original sheet order (or sort by Date Added, most recent first, if the user prefers — default to sheet order).

## Step 6 — Output format

Always render a markdown table first:

| Name | Priority | Phone | Suggested Action |
|---|---|---|---|
| ... | High/Medium/Low | ... | (see below) |

**Suggested Action** by tier:
- High → "Call today — high-fit lead"
- Medium → "Send property details via SMS/email, follow up in 2–3 days"
- Low → "Add to nurture list — confirm budget/details before calling" (or "Missing phone — email only" if phone is absent)

After the table, add a section header **"Follow-Up Messages for High-Priority Leads"** and, for each High-Priority lead only, write a short 2-line message:
- Professional, warm, call/SMS-ready tone — written like a real agent would actually text, not generic AI copy.
- Reference the specific property they're interested in and a concrete next step (e.g. a viewing time, a callback offer).
- No greetings-only fluff, no corporate boilerplate ("We hope this message finds you well").
- English only, per user preference.
- Do NOT draft messages for Medium or Low priority leads.

### Example follow-up tone (for calibration, not to copy verbatim)

> Hi Rahim, this is [Agent] from [Agency] — saw you're interested in the 3-bed apartment in Bashundhara. I have availability for a viewing this week, would tomorrow afternoon work for you?

## Step 7 — Wrap-up

After the table and messages, briefly note counts (e.g. "3 High, 4 Medium, 2 Low — 1 lead skipped for missing budget") so the agent gets a quick summary at a glance. Do not add extra commentary beyond this.
