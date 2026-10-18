# Knowledge Index

> **Location:** `knowledge/_index.md`
> **Purpose:** A map of every file in `knowledge/` and when to use it. The routing rule (`.cursor/rules/20-knowledge-routing.mdc`) points here.
> **Scope:** Reusable material that is true for any founder. Company-specific facts live in `workspace/`, not here.

## How to use this index

1. Find the row that matches the question.
2. Open only that file (and any file in its "Pairs with" column).
3. Apply what you read to the active founder's facts from `workspace/`. Never reuse another company's figures.
4. If no file covers the topic, say so, and look for a public source (see `public-resources.md`) rather than answering from memory.

## Files

| File | What it contains | Use it when | Pairs with |
|---|---|---|---|
| `glossary.md` | Plain-English definitions of 37 finance and fundraising terms (ARR, CAC, burn multiple, NRR, SAFE, dilution, valuation cap, runway, and more). No company figures. | A term appears that the founder may not know, or you need to explain a concept simply for the first time | `workspace/[founder]/glossary-examples.md` for the founder's own figure for each term |
| `investor-qa.md` | The coaching rubric for investor questions: the four-part strong answer, weak-answer patterns, a procedure for questions not on any list, a map of what investors probe by theme, standard metric definitions, the scoring rubric, the mock investor loop, and guardrails. | Preparing a founder for investors, answering any investor question, scoring a practice answer, or running a mock session | `investor-profiles.md`, the founder's case files, `workspace/[founder]/04-investor-qa.md` for worked examples |
| `investor-profiles.md` | Five investor archetypes (lead seed fund, angel operator, strategic investor, government-backed fund, skeptical partner): what each evaluates, their style, what makes them say no, and typical questions. | Choosing or playing an investor in a mock session, or explaining what a particular type of investor cares about | `investor-qa.md` |
| `public-resources.md` | A list of 23 public sources with live URLs: example pitch decks, seed fundraising guides, metric definitions, SAFE and term resources, Canadian funding programs. The server may fetch pages at runtime; cite title + URL; do not invent page content if fetch fails. | Citing a benchmark or investor expectation, seed fundraising / terms coaching, pointing a founder to an example deck or guide, or answering questions about SAFEs, SR&ED or Canadian funding | `investor-qa.md` (guardrail on sourcing) |
| `audit-checklist.md` | The review checklist run before an answer is sent: numbers, source labels, missing data, accounting traps, investor coaching, plain language, guardrails, and a search for contradicting evidence. Includes a founder-facing audit line and an internal log. | Before sending any answer that contains figures, claim checks, benchmarks or investor coaching | `.cursor/rules/05-core-principles.mdc`, the founder's case files |
| `june-platform.md` | A description of the sponsoring platform: how data flows, the three agents (Franco, Rocco, Vicky), and Vicky's 8-step investor-prep pack. | Asked what the platform does, or structuring a full investor-prep session | `investor-qa.md`, `investor-profiles.md` |

## Quick routing by question

| If the question is about... | Open |
|---|---|
| What a term means | `glossary.md` |
| How to answer an investor question | `investor-qa.md` |
| Practicing or a mock investor | `investor-profiles.md` and `investor-qa.md` |
| What a type of investor cares about | `investor-profiles.md` |
| A benchmark, an example deck, SAFEs, SR&ED, Canadian programs | `public-resources.md` |
| How the platform or an investor-prep pack works | `june-platform.md` |
| Reviewing an answer before sending it | `audit-checklist.md` |
| The founder's own numbers or claims | Not here. Go to `workspace/[founder]/case-index.md` |

## What is not in this folder

| Material | Where it lives |
|---|---|
| The founder's company facts, financials, forecast, worked investor answers | `workspace/[founder]/` (for Tidewell: `workspace/tidewell-systems/`, start with `case-index.md`) |
| Quality-bar examples for testing the agent | `tests/` |
| The original source PDF | `source/` (reference only, never read it when coaching) |

## Maintaining this index

When you add, rename or remove a file in `knowledge/`, update the table above in the same change. Each row needs a one-line description, a clear "use it when," and its related files, so the agent can route without opening every file.
