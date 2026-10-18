# June Analytics Platform and AI Agents

> **Source:** Appendix G (June Analytics platform and AI agents)
> **Type:** Context on the sponsoring company's product, plus **the principles the agent should share**
> **Note from the authors:** "This is how it works today. You don't need to copy it."
> **Related files:** `knowledge/investor-qa.md`, `knowledge/investor-profiles.md`, `knowledge/public-resources.md`

June Analytics sells **Finance for Founders**, an AI finance team for startups built by CPAs. Founders connect their books, and three AI agents work from that one set of numbers.

## How data flows

1. The founder connects QuickBooks Online or Xero, or uploads statements as CSV.
2. June builds one dataset for the company. Every agent and every screen reads from it, so the numbers always agree.
3. Calculations happen in code. The AI writes the explanation around numbers that were already computed, and its text is checked against them before it is shown.
4. Each agent works only on the active company's data. One company's numbers never appear in another's workspace.

## The three agents

| Agent | Role | What it does |
|---|---|---|
| **Franco**, the Finance Officer | Builds and runs the forecast | Builds the forecast with the founder through a short guided setup, prefilled from their books. Runs what-if questions ("what if we hire two engineers in March?") on a copy, never on the real plan. Writes the monthly outlook. |
| **Rocco**, the Risk Officer | Checks what happened | Reviews each closed month: actual vs forecast, forecast accuracy, customer and vendor changes, trends. Flags risks in the company's financial health. |
| **Victoria**, the VC | Prepares the founder for investors | Builds an investor-prep pack: market research, strengths and weaknesses, likely investor questions, an action list and a draft deck. A separate audit step then challenges her own work. |

## How Vicky builds an investor-prep pack

1. **Intake.** The founder dumps everything in one box (typed or dictated) and uploads what they have: an old deck, a roadmap, customer lists. A checklist beside the box shows what is still missing.
2. **Market research.** Web search for market size (top-down and bottom-up), competitors and comparable raises. Every figure carries its source: a web page, an upload, or the founder's own plan.
3. **Assessment.** Strengths, weaknesses and moat, using actuals, the forecast and the health checks.
4. **Question prep.** Financial and non-financial questions an investor is likely to ask, with the top three highlighted.
5. **Action list.** What to fix before the first meeting.
6. **Deck draft.** Slides from a template the founder picks. Vicky's text is marked as hers until the founder edits it.
7. **Audit.** A separate reviewer works through a checklist and runs its own searches for evidence that contradicts the pack.
8. **Revise.** Vicky fixes what the audit found.

The founder sees a snapshot: top three questions, next actions, market size and competitors, strengths and weaknesses, and how many issues the audit raised. Each card opens the full report with sources.
