# Audit Checklist

> **Location:** `knowledge/audit-checklist.md`
> **Purpose:** The review step before any answer reaches the founder. Implements core principle 4 ("have your answer checked before showing it") from `.cursor/rules/05-core-principles.mdc`.
> **Related files:** `.cursor/rules/30-calculation-standards.mdc`, `.cursor/rules/50-guardrails.mdc`, `tests/tidewell-example-vicky-output.md` (shows audit catches in practice)

## When to run it

Run it on every answer that contains a calculated figure, a claim check, a benchmark, a forecast comparison, investor coaching, or a drafted investor answer. Skip it for simple definitions and casual questions.

## How to run it

1. **Review the draft as if someone else wrote it.** Do not assume any number is right. Recalculate each one from the source files before ticking it off.
2. **Prefer a separate reviewer.** A fresh chat, a second agent or a review-only mode, given the draft plus the case files, is a stronger check than the same chat reviewing its own work. If you can only self-review, be stricter: recompute, don't re-read.
3. **Work through every section below.** Mark each item Pass, Fix, or N/A.
4. **Fix every "Fix" item before showing the answer.** Then re-check the items you changed.
5. **Report the audit result** to the founder in one line (see the end of this file).

---

## A. Numbers

- [ ] Every figure reproduces from the founder's files. Recalculate; do not trust the draft.
- [ ] The formula, inputs, period and result are shown for each calculated figure.
- [ ] The definition used is stated, and the alternative is shown where an investor might use a different one (for example, gross margin with and without support).
- [ ] Figures taken from an example file (`04-investor-qa.md`, `glossary-examples.md`, `tests/`) were recalculated from source data, not copied.
- [ ] Quarterly (rounded) figures are flagged as rounded, and monthly data was used where available.
- [ ] Figures agree with each other across the answer (cash, burn and runway reconcile; percentages and dollar amounts match).

## B. Sources and labels

- [ ] Every figure is labeled: historical, forecast, founder's claim, or public source.
- [ ] No forecast, projection or unsigned deal is presented as fact.
- [ ] The founders' reasoning is not treated as evidence. It is tested against the historical data.
- [ ] Every public benchmark names its source, and the source was opened and confirmed (see `50-guardrails.mdc`).
- [ ] US data used for a Canadian company is labeled as US data.

## C. Missing data

- [ ] Any data that was not provided is named as missing (check the data files table in `case-index.md`).
- [ ] Nothing was estimated or invented to fill a gap, including competitor data, win/loss reasons, pipeline and market counts.
- [ ] For each gap, the answer says what would fill it.

## D. Accounting traps specific to the case

- [ ] One-time items (SR&ED refunds, financing) are excluded from burn and runway, and the answer says so. The figure with and without is shown when it matters.
- [ ] The bookkeeping policies in `02-financial-history.md` were applied (customer success in operating expenses, SR&ED booked when cash arrives, deferred revenue from annual plans).
- [ ] Growth and retention are shown with and without the largest customer where it is a meaningful share of MRR.
- [ ] Trends are not labeled "improving" or "worsening" from a short window without giving both the short and long figures.
- [ ] Each forecast driver was compared with its historical value, and a downside case is included.

## E. Investor coaching

- [ ] Each drafted answer has the four parts: the number, the method, the weak spot, the action.
- [ ] The answer is short enough to say aloud in about a minute.
- [ ] The answer matches the founder's deck and their other answers. Flag any inconsistency.
- [ ] The score (if given) uses the rubric and the investor-specific priorities in `knowledge/investor-qa.md`.
- [ ] The most likely follow-up question is anticipated.
- [ ] Nothing coaches spin: no hidden weak number, no redefined metric chosen to look better.

## F. Plain language

- [ ] Each term is explained the first time it appears, consistent with `knowledge/glossary.md`.
- [ ] No unexplained jargon or acronyms.
- [ ] The answer leads with the verdict or the answer, then the evidence.
- [ ] It ends with one concrete next step.

## G. Guardrails

- [ ] No valuation, range or target is suggested, and the company's worth is not stated.
- [ ] No investment advice.
- [ ] No advice on whether to accept investor rights or governance terms. They are explained, and a lawyer is flagged.
- [ ] No legal, tax or securities advice. Where a lawyer or accountant is needed, the answer says so.
- [ ] Only the active founder's data is used. No other founder's figures appear.

## H. Search for contradicting evidence

For any claim about the market, competitors or a public benchmark:

- [ ] A search was run for evidence that contradicts the claim, not just evidence that supports it.
- [ ] Contradicting evidence found is reported, with its source.

---

## Recording the result

End the audit with a short log. Show the founder one line. Keep the detail available if they ask.

**Founder-facing line:**
```
Audit: [N] issues found and fixed before this answer. [M] items could not be verified because the data was not provided.
```

**Audit log (internal):**
| # | Section | Issue found | How it was fixed |
|---|---|---|---|
| 1 | | | |

## Examples of issues this checklist is meant to catch

These are the three audit catches shown in `tests/tidewell-example-vicky-output.md`:

1. **A short window described as a trend.** The first draft called churn "improving" from six months of data. The fix gave both the 6- and 12-month figures and let the founder decide. *(Checks D, E)*
2. **An unsourced benchmark.** The first draft compared net revenue retention to a benchmark with no source. The benchmark was removed. *(Check B)*
3. **A one-time item inside a recurring figure.** The runway calculation first used burn that included the SR&ED refund. It now excludes it. *(Check D)*
