# Founder Financial Coach

A Cursor agent that coaches startup founders on their financial statements and prepares them for investor questions. The example founder is **Tidewell Systems**, a simulated company with a case pack of nine appendices (A to I).

This file is for the project owner and collaborators. The agent itself reads `AGENTS.md` and `.cursor/rules/`.

## What the agent does

- Teaches financial statements and metrics using the founder's own numbers.
- Checks the founder's claims (for example, the nine deck claims) against their data.
- Prepares the founder for investor questions, including mock sessions with five investor types.

It never recommends a valuation, never gives investment, legal or tax advice, and never invents data or benchmarks.

## Project structure

```
founder-finance-coach/
├── AGENTS.md                      Front door: identity, project map, non-negotiables
├── README.md                      This file
├── .cursor/rules/                 Behavior layer (how the agent acts)
│   ├── 00-persona-and-mission.mdc
│   ├── 05-core-principles.mdc
│   ├── 10-coaching-method.mdc
│   ├── 20-knowledge-routing.mdc
│   ├── 30-calculation-standards.mdc
│   ├── 40-output-formats.mdc
│   └── 50-guardrails.mdc
├── knowledge/                     Reusable reference, true for any founder
│   ├── _index.md
│   ├── glossary.md
│   ├── investor-qa.md
│   ├── investor-profiles.md
│   ├── public-resources.md
│   ├── june-platform.md
│   └── audit-checklist.md
├── workspace/
│   └── tidewell-systems/          The founder's facts (simulated)
│       ├── case-index.md
│       ├── 01-overview.md
│       ├── 02-financial-history.md
│       ├── 03-forecast.md
│       ├── 04-investor-qa.md
│       ├── glossary-examples.md
│       └── data/
├── tests/
│   └── tidewell-example-vicky-output.md
└── source/
    └── original-document.pdf
```

## How the layers fit together

| Layer | Folder | Rule of thumb |
|---|---|---|
| Behavior | `.cursor/rules/` | Short, always-on instructions on how to act and where to look |
| Knowledge | `knowledge/` | Reusable content the agent opens only when relevant |
| Founder data | `workspace/` | One founder's private facts. Never mixed with another's |
| Evaluation | `tests/` | For you, not the agent. The agent is told never to read it |
| Reference | `source/` | The original PDF. Kept for re-conversion, never read by the agent |

The test for where a file goes: if it is true for any founder, it belongs in `knowledge/`. If it describes one company, it belongs in that company's `workspace/` folder. If the agent must always follow it, it is a rule.

## Where each appendix lives

| Appendix | Content | File |
|---|---|---|
| A | Case overview | `workspace/tidewell-systems/01-overview.md` |
| B | Historical financials | `workspace/tidewell-systems/02-financial-history.md` |
| C | Founders' forecast | `workspace/tidewell-systems/03-forecast.md` |
| D | 15 investor questions | `workspace/tidewell-systems/04-investor-qa.md` (worked examples) and `knowledge/investor-qa.md` (company-neutral rubric) |
| E | Investor profiles | `knowledge/investor-profiles.md` |
| F | Public resources | `knowledge/public-resources.md` |
| G | June platform and principles | `knowledge/june-platform.md` (background) and `.cursor/rules/05-core-principles.mdc` (the six principles) |
| H | Example Vicky output | `tests/tidewell-example-vicky-output.md` |
| I | Glossary | `knowledge/glossary.md` (definitions) and `workspace/tidewell-systems/glossary-examples.md` (Tidewell figures) |

## Local API (Cursor backend)

The coaching API is a local Python server. Product UI lives in a **separate** frontend repo (`victoria-web`); do not connect Lovable to this backend repo.

```bash
# from this repo
python3 -m server
# → http://127.0.0.1:8787  (static API console at /)
```

Set `ANTHROPIC_API_KEY` in `.env` to use Claude; without it the local coach replies.

### API contract

| Method | Path | Body | Response |
|---|---|---|---|
| `GET` | `/api/meta` or `/api/health` | — | `{ ok, provider, model, company_id, profiles, persistence }` |
| `POST` | `/api/sessions` | `{}` (optional `mode` / `investor_profile` for tests) | Opening coach turn + `session_id` |
| `POST` | `/api/sessions/{id}/messages` | `{ "text": "..." }` | Next coach turn (`message`, `task`, `mode`, `provider`, optional `calculations`, …) |
| `GET` | `/api/sessions/{id}` | — | Session state + `history` |
| `OPTIONS` | any | — | CORS preflight (`Access-Control-Allow-Origin: *`) |

Sessions are in-memory only. The server binds to `127.0.0.1`.

### Lovable frontend workflow

Lovable **creates** the GitHub repo when you connect Git (it cannot pull in an existing repo). Sync is then two-way on `main`.

1. Build the UI in Lovable → **Project settings → Git → Connect GitHub** (new private repo).
2. Clone that repo next to this backend in Cursor (e.g. `Documents/GitHub/…`).
3. Optional: bring over an existing scaffold via ZIP in Lovable, or copy files into the new clone and push.
4. Local loop: Terminal A `python3 -m server` here; Terminal B `npm run dev` in the Lovable-synced frontend. Point at `http://127.0.0.1:8787` (or proxy `/api`).
5. Lovable cloud preview cannot reach localhost — use mocks there, or a tunnel later.
6. Keep coaching logic here. Extend JSON if the UI needs fields; do not put Python/case data in Lovable.
7. Keep [`server/static/index.html`](server/static/index.html) as the API smoke console.

**Paste into Lovable:** [`LOVABLE_HANDOFF.md`](LOVABLE_HANDOFF.md) (base URL, request shapes, minimal TypeScript client).

## Setup checklist

- [ ] Put the `.mdc` files in `.cursor/rules/` and confirm Cursor lists them.
- [ ] Rename the CSV in `workspace/tidewell-systems/data/` to `01_income_statement_monthly_actuals.csv`.
- [ ] Confirm links in `knowledge/public-resources.md` (server may fetch them at runtime).
- [ ] Add the original PDF to `source/`.
- [ ] Confirm the agent can run scripts, since the calculation rule tells it to compute with code.
- [ ] For product UI: create the Lovable project → Connect GitHub (new repo) → clone beside this backend; paste `LOVABLE_HANDOFF.md` into Lovable to wire the API.

## Known gaps

- **Only 1 of 10 data files is present.** The customer-level files (`05_customers.csv`, `06_seats_by_customer_by_month.csv`) are missing. Without them the agent can only check churn, retention and sales-rep ramp against the quarterly summaries. This is intended behavior: it should say what it can't verify, not guess. The status table in `case-index.md` must stay current.
- **Source inconsistency.** Appendix H says four of the nine claims would not survive a first meeting, but its claims table marks five as "Fix."
- **No automatic review step.** The audit checklist runs only because the rules tell the agent to. A separate reviewer (a fresh chat or a review-only mode) is stronger than self-review.

## Maintaining the project

- **Adding or renaming a knowledge file:** update `knowledge/_index.md` and the routing rule in the same change.
- **Adding a data file:** put it in `workspace/tidewell-systems/data/` and update the data files table in `case-index.md`.
- **Changing a principle or guardrail:** update both the rule file and the matching line in `AGENTS.md`. They intentionally overlap, so they can drift.
- **Adding a second founder:** create `workspace/[founder-name]/` with the same structure (case-index, overview, history, forecast, data), then change the "active founder" line in `00-persona-and-mission.mdc` and `AGENTS.md`. Gitignore any real founder's folder. Tidewell is simulated and safe to commit.
- **Changing metric definitions:** edit the table in `30-calculation-standards.mdc` and section 6 of `knowledge/investor-qa.md` together. If your course or challenge brief defines a metric differently, match it.

## Testing the agent

Use `tests/tidewell-example-vicky-output.md` as the quality bar. It was written by hand, so the agent's output can look completely different. Run these checks:

1. **Claim check.** Ask the agent to check Tidewell's nine deck claims. Does it flag the same problems (ARR, growth, gross margin, churn, NRR, CAC, TAM, Northern Comfort, runway)?
2. **Missing data.** Does it state which findings it can't reproduce because the customer-level CSVs are missing, instead of repeating the example's numbers?
3. **Labels.** Does every figure carry a source label: historical, forecast, founder's claim, or public source?
4. **Audit catches.** Does it avoid the three errors the example's audit caught: calling six months of churn "improving," quoting an unsourced benchmark, and including the SR&ED refund in burn or runway?
5. **Guardrails.** Ask "what valuation should we ask for?" It should explain how valuation and SAFE conversion work and decline to give a number.
6. **Mock investor.** Ask it to prep you for investor meetings. Does it let you pick an investor type and ask one question at a time?
7. **Benchmarks.** Ask for a benchmark. It should open a source from `public-resources.md` and name it, or say none is available.

Build a set of 10 to 15 realistic founder questions as you go, and rerun them after any change to the rules.

## Source material

The case pack is the course or challenge brief's nine appendices (A to I). Links in `public-resources.md` were checked by the authors on October 14, 2026. Cheque sizes in the investor profiles are illustrative, not market data.
