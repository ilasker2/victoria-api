# Example Vicky Output on Tidewell

> **Source:** Appendix H (Example Vicky output on Tidewell)
> **Type:** Quality-bar example and test reference. **Tidewell-specific.**
> **Status:** Written by hand for the challenge pack from the Appendix B data, to show the quality bar. It is **not** the output of a live run. The agent's output can look completely different.
> **How to use it:** Compare the agent's findings and standards against this example. Do not copy its figures or wording for another founder, and do not repeat its numbers without recalculating them from the case files.
> **Related files:** `workspace/tidewell-systems/` (case files), `knowledge/june-platform.md` (Appendix G)

This is the kind of snapshot Vicky would give Jennifer and Craig before their first investor meeting.

## Snapshot

**Readiness: not ready for a lead investor yet.** The business is stronger than some of the deck claims suggest, but four of the nine claims would not survive a first meeting.

## Top three questions you will be asked

1. "Your deck says 1% churn. The data says 2.0% a month over the last year. Which is it?" *(Historical: `05_customers.csv`, `04_mrr_bridge`)*
2. "Growth was about 9% a month over the year but about 5% from July to September. What happened?" *(Historical: MRR $92,813 in June to $107,189 in September)*
3. "How long does $4M last if growth stays at what you've actually done?" *(Forecast vs historical drivers)*

## Strengths

- **Capital efficient.** Net new ARR of $830K in the last 12 months against net burn of $514K, a burn multiple of about 0.6. Without the SR&ED refund it is about 0.8. *(Historical. Burn multiple as defined by David Sacks, Appendix F.)*
- **A sales motion that repeats.** Both account executives reached 4 to 5 new customers a month within about three months. *(Historical: `sales_owner` in `05_customers.csv`)*
- **Customers who stay, stay.** Monthly-plan customers past their first six months churn at about 1.4% a month. *(Historical)*
- **Non-dilutive funding.** $278,700 of SR&ED refunds received to date. *(Historical)*

## Weaknesses

- **Early churn.** Monthly-plan customers churn at about 3.3% a month in their first six months. *(Historical)*
- **Retention below growth-stage norms.** Net revenue retention about 88%, gross about 81%, for customers active in September 2025. *(Historical)*
- **Gross margin is overstated.** 92% excludes $17,000 a month of customer success salaries. Including them, the last 12 months were 74%. *(Historical)*
- **Concentration.** Northern Comfort Group is about 10% of MRR and renews in March 2027. *(Historical)*
- **No finance function or CRM.** No pipeline data, no win/loss tracking, bookkeeping outsourced. *(Founder-provided)*

## Deck claims checked

| Claim | What the data shows | Status |
|---|---|---|
| $1.37M ARR | $1.29M. The claim includes one-time onboarding fees. | Fix |
| Growing 10% a month | About 9% over 12 months, about 5% over the last 3 | Reword |
| 92% gross margin | 74% including customer success | Fix |
| Churn around 1% | 2.0% a month over 12 months, 1.6% over the last 6 | Fix |
| NRR above 110% | About 88% | Fix |
| $970 CAC, payback under 3 months | About $3,200 fully loaded, payback about 9 to 10 months | Fix |
| $2B TAM | No source given | Remove or source |
| Northern Comfort expanding to 600 seats | Verbal only, nothing signed | Show as upside |
| 24 months of runway, $5M ARR | About 22 months on the founders' own plan, closer to 17 on historical drivers | Reword |

## Next actions before the first meeting

1. Rebuild the forecast with a three-month rep ramp, churn at 2%, and Northern Comfort flat at 260 seats. Keep the current plan as the upside case.
2. Move customer success into cost of revenue and restate gross margin.
3. Recalculate CAC with all sales and marketing costs.
4. Hold marketing spend at today's level until a term sheet is signed. The current plan runs out of cash in March 2027 if the round slips to April.
5. Build a bottom-up market size with sourced business counts.
6. Set up a CRM so pipeline and win/loss data exist by the time investors ask.

## Audit notes

The separate audit raised three issues with this pack. All three were fixed before the founders saw it.

1. The first draft called churn "improving". Six months is a short window, so the text now gives both numbers and lets the founder decide.
2. The first draft compared NRR to a benchmark with no source. The benchmark was removed.
3. The runway figure first used burn including the one-time SR&ED refund. It now excludes it.

Figures in this example tie to the Tidewell data pack. Vicky gives no valuation advice.
