# Investor Q&A Coaching Rubric (Company-Neutral)

> **Location:** `knowledge/investor-qa.md`
> **Purpose:** Teach the agent how to coach any founder through seed-investor questions, including questions that are not on any list.
> **Scope:** Method only. Contains no company-specific figures. Apply it to a founder's own data from `workspace/`.
> **Companion material:** `workspace/tidewell-systems/04-investor-qa.md` holds 15 worked examples built on one company's numbers. Use them to see the method in action, never as benchmarks for another founder.
> **Investor types:** `knowledge/investor-profiles.md` describes the five investor archetypes. Use it to choose the persona and adjust the scoring in section 7a.

---

## 1. The core idea

An investor question is rarely about the words asked. It is a probe: *Does this founder know their numbers? Do they tell the truth about weak spots? Do they have a plan?* A strong answer passes all three probes in about 30 to 60 seconds of speech.

The agent's job is to coach founders to answer from **evidence, honestly, with a plan**, not to polish spin.

## 2. The four-part strong answer

Every strong answer contains these four parts, in roughly this order:

| Part | What it does | Example phrasing |
|---|---|---|
| **1. The number** | States a specific figure, with the period and units | "Over the last 12 months, X was Y." |
| **2. The method** | Says how it was calculated and what is included or excluded | "That's A divided by B. It excludes C because..." |
| **3. The weak spot** | Names the unflattering part before the investor finds it | "The part we're not happy with is..." |
| **4. The action** | Says what the founder is doing about it, with a date or trigger | "So we're doing X by [date], and if Y happens we'll Z." |

Optional fifth part, when it fits: **the context** (trend, segment, or outlier effect), such as what the number looks like with and without one large customer, or whether the last six months differ from the last twelve.

**Test:** If the answer could be said by a founder who had never opened their financials, it is weak.

## 3. Weak-answer patterns the agent should recognize

| Pattern | What it sounds like | Why it fails |
|---|---|---|
| **Round or unsourced number** | "Around 1%." "Industry reports." | Signals the number was never calculated |
| **Definition mismatch** | Total revenue called ARR; marketing-only spend called CAC | Uses a flattering definition that an investor will redo |
| **Cherry-picked window** | Best month presented as the trend | Investors will ask for the last 6 and 12 months |
| **Hiding behind an outlier** | "Churn was mostly early customers" | Explains away the number without measuring the claim |
| **Confidence instead of evidence** | "We're confident in the product." "We have strong interest." | Answers a feeling, not the question |
| **Forecast presented as fact** | "They're expanding to 600 seats." | Treats an unsigned or projected outcome as settled |
| **Deflection** | "It won't happen." | Avoids the risk instead of showing planning |
| **No plan** | States the problem, stops there | Candor without action reads as helpless |
| **Inconsistent numbers** | Runway, burn and cash don't reconcile across answers | Destroys credibility on everything else |

## 4. How to produce a strong answer for any question (not on a list)

When a founder asks about a question that has no worked example, the agent follows this procedure:

1. **Identify what the investor is probing.** Use the question map in section 5.
2. **List the evidence needed** to answer with a real number. Decide which files in `workspace/` hold it.
3. **Get the evidence.** Open the relevant files, calculate the metric, and state the formula used (see section 6). If the data is missing, go to step 3a.
   - **3a. If the data is missing:** Say so plainly. Do not estimate, benchmark or invent. Help the founder design how to get it (what to track, what to ask customers, what to pull from billing or the CRM). The strong answer then becomes: here is what we know, here is what we don't, here is how we're finding out and when.
4. **Find the weak spot.** Check the number for: outlier effects, a recent trend that differs from the long-run figure, definitions an investor would challenge, and anything that contradicts the founder's deck.
5. **Draft the answer** using the four-part structure. Keep it speakable: short sentences, one or two numbers per sentence, no jargon the founder wouldn't use out loud.
6. **Reconcile.** Check the answer against the founder's other answers and deck claims. Flag any inconsistency before the founder does it live.
7. **Anticipate the follow-up.** Add the one or two most likely drill-down questions and a short prepared answer to each.

**Always show the weak and strong versions side by side when coaching**, so the founder sees the gap and can explain why the strong one is stronger.

## 5. Question map: what investors probe, by theme

Use this to classify unfamiliar questions. Each row lists the probe, the evidence a strong answer needs, and the red flags.

### Traction and revenue

| Likely questions | Investor is probing | Evidence needed | Red flags |
|---|---|---|---|
| What is your ARR / MRR? | Do you separate recurring from one-time revenue? | Subscription revenue by month, one-time fees | Total revenue × 12 called ARR |
| How fast are you growing? | Trend, durability, dependence on one deal | MRR by month, growth with and without largest customers | Best month as the trend |
| What is your churn? | Product stickiness | Customers and MRR lost, by month, by tenure, by plan type | One blended number, no segmentation |
| What is your net revenue retention? | Whether the base grows by itself | Starting-cohort MRR now vs. then | Quoted without a method, or above what the data shows |
| How concentrated is your revenue? | Dependence on a few customers | Top customers as a share of MRR | Hiding the largest customer |
| How do customers find you? | Whether acquisition is repeatable | Customers and spend by channel | "Word of mouth" with no numbers |

### Unit economics

| Likely questions | Investor is probing | Evidence needed | Red flags |
|---|---|---|---|
| What is your gross margin? | How much revenue can fund growth | Cost of revenue lines, support cost treatment | Excluding costs most investors include |
| What does a customer cost to win, and how fast do you earn it back? | Whether more spend creates profitable growth | Fully loaded sales and marketing spend, new customers, new-customer MRR, margin | Marketing-only CAC |
| What is a customer worth over time? (LTV) | Long-term value vs. acquisition cost | Churn, margin, revenue per customer | LTV built on a churn rate lower than the data |
| What is your burn multiple / efficiency? | How much cash buys how much new recurring revenue | Net burn, net new recurring revenue | Ignoring one-time cash events |
| How does pricing work, and what could you charge? | Pricing power and discipline | Price history, discounts, legacy pricing | Assuming a price rise costs no customers |

### The forecast

| Likely questions | Investor is probing | Evidence needed | Red flags |
|---|---|---|---|
| What are your key assumptions, and why? | Whether assumptions come from data | Assumption-by-assumption comparison with history | Reasoning that is a quote or a feeling |
| What if churn, ramp or growth miss? | Whether the founder has a downside case | A second scenario with the assumptions that matter changed | Only a base case |
| How fast do new salespeople ramp? | Whether the hiring plan can produce | History of past hires: time to productivity | Ramp faster than any real hire achieved |
| How reliable are your large expected deals? | Pipeline honesty | Signed vs. verbal vs. hoped | Unsigned deals in the base plan |

### Cash and the raise

| Likely questions | Investor is probing | Evidence needed | Red flags |
|---|---|---|---|
| Why this amount, and how long does it last? | Understanding of burn, planning for the next round | Cash, burn history, plan burn, a realistic-growth case | One runway figure, no sensitivity |
| What if the round takes longer? | Negotiating position, spending discipline | Cash today, current burn, spending triggers | Spending ahead of money received |
| What are the funds for? | Strategy behind the budget | Use of funds tied to milestones | A split of percentages with no milestones |
| What valuation do you want? | Realistic expectations | Metrics, round size, existing SAFEs or notes and how they convert | A number with no reasoning |
| Who else is in the round, and what happens to existing investors? | Cap table understanding | Cap table, SAFE and note terms | Not knowing the dilution |

### Market and strategy

| Likely questions | Investor is probing | Evidence needed | Red flags |
|---|---|---|---|
| How big is the market? (TAM) | Rigor, not the number | Bottom-up: count of target customers × seats or usage × price | A top-down number from "industry reports" |
| Why will you win against competitors? | Whether founders know why customers buy | Win/loss reasons, switching customers, customer quotes | "Our product is better" |
| What is your moat or advantage over time? | Defensibility | Specific, evidence-backed advantages | Generic claims (AI, speed, culture) |
| Why now? | Timing logic | A specific shift in market, technology or behavior | No answer |

### Team and risk

| Likely questions | Investor is probing | Evidence needed | Red flags |
|---|---|---|---|
| Why are you the team to build this? | Founder-market fit | Specific experience and customer proximity | Credentials without relevance |
| Who are you hiring first, and why? | Awareness of gaps | A hiring plan tied to the biggest risks | Hiring to a budget, not a gap |
| What is the biggest risk, and what will you do about it? | Self-awareness | A named risk with a trigger and a response | "Execution" or no risk named |
| What will this round get you to? | A path to the next round | Specific milestones, timing, a downside case | A funding target with no milestones |

## 6. Standard metric definitions

The agent states which definition it uses every time. Where an investor would reasonably use a different one, show both.

| Metric | Standard definition |
|---|---|
| **MRR** | Monthly subscription revenue at month end. Excludes one-time fees. |
| **ARR** | MRR × 12. |
| **Compounded monthly growth** | (Ending MRR ÷ Starting MRR)^(1 ÷ number of months) − 1 |
| **Logo churn (monthly)** | Customers lost in the month ÷ customers at the start of the month. Report the average over 6 and 12 months. |
| **Gross revenue retention (GRR)** | MRR today from customers who existed N months ago, counting only decreases (churn and contraction), ÷ their MRR N months ago. Cannot exceed 100%. |
| **Net revenue retention (NRR)** | MRR today from customers who existed N months ago, including expansion, ÷ their MRR N months ago. N is usually 12. |
| **Gross margin** | (Revenue − cost of revenue) ÷ revenue. State which costs are in cost of revenue. Also show the version that includes customer support. |
| **Fully loaded CAC** | All sales and marketing cost (salaries, commissions, programs) for the period ÷ new customers in the same period. |
| **CAC payback (months)** | CAC ÷ (new-customer MRR × gross margin). |
| **Net burn** | Cash spent minus cash received from operations, excluding financing. |
| **Runway (months)** | Cash ÷ net burn. Show both current burn and planned burn. |
| **Burn multiple** | Net burn ÷ net new ARR (net new MRR × 12), for the same period. |

If the founder's books treat any of these differently (for example, where support costs sit, or when tax credits are recorded), say so and show the adjusted number.

## 7. Scoring an answer

When the founder practices, score the answer on six criteria. Use 0 (missing), 1 (partial) or 2 (clear).

| Criterion | 2 means |
|---|---|
| **Specific number** | A figure, period and units are given |
| **Method** | The calculation and inclusions or exclusions are stated |
| **Accuracy** | The number matches the founder's own data |
| **Candor** | The weak spot is named without being asked |
| **Action** | A plan with a date or trigger is stated |
| **Consistency and delivery** | Matches other answers and the deck; short enough to say out loud |

Interpretation: 11 to 12 is investor-ready, 8 to 10 needs targeted fixes, below 8 means rebuild the answer using section 4.

**Accuracy is a hard check.** If a number cannot be reproduced from the founder's data, score it 0 and show the calculation that does work.

### 7a. Adjusting the score for the investor type

When the founder is practicing with a specific investor from `knowledge/investor-profiles.md`, keep the six criteria but treat the investor's priority criteria as mandatory: if either scores below 2, the overall verdict cannot be better than "needs targeted fixes," whatever the total. Suggested defaults:

| Investor | Priority criteria | What this investor tests |
|---|---|---|
| Lead seed fund | Accuracy, Method | Follows a number two or three levels down: "Which months? Which customers?" |
| Angel operator | Candor, Consistency and delivery | Asks for a story, then the number behind it. Stops the meeting if the founder bluffs |
| Strategic investor | Specific number, Action | Wants figures on channel fit and a clear view of what the founder needs from them |
| Government-backed fund | Method, Action | Asks who prepares the statements, how SR&ED is recorded and what the plan is for the finance function |
| Skeptical partner | Accuracy, Candor | Looks for the one claim that falls apart under a single follow-up question |

These are suggested defaults. Adjust them if your course or challenge brief says otherwise.

## 8. Mock investor mode

When a founder asks to prepare for investor meetings, run this loop:

1. **Pick the investor and set the scene.** Let the founder choose an investor type from `knowledge/investor-profiles.md`, or pick one at random. Say which investor you are playing and ask one question at a time, in that investor's style.
2. **Order the questions** by investor type. The seed fund goes deep on metrics and the angel goes deep on customers. Otherwise use the usual sequence: traction, unit economics, forecast, cash and raise, then strategy and team. Prioritize the questions where the founder's deck is most exposed.
3. **Ask one question.** Wait for the founder's answer.
4. **Score it** using sections 7 and 7a, and show the result briefly.
5. **Give feedback in this order:** what worked, the single most important fix, then a rewritten strong answer built from the founder's own data.
6. **Add one follow-up** an investor would likely ask next, and let the founder try it.
7. **Move on** to the next question, or stop when the founder asks.

Keep the investor tone realistic but fair. The goal is confidence through preparation, not intimidation.

After the session, offer a one-page summary: the founder's weakest numbers, the answers still to rework, and the evidence they still need to gather.

## 9. Worked mini-examples for questions not on the standard list

Illustrative only. Brackets mark where the founder's real data goes. The agent fills these from `workspace/`, never from this file.

**Q: What is your burn multiple?**
- **Weak:** "We're efficient." / "Our burn is reasonable."
- **Strong:** "Over the last [period], we burned [$A] net and added [$B] of net new MRR, so [A÷B annualized]. That excludes [one-time cash event]. It's [above/below] where we'd like it because [reason]. We're [action] by [date]."
- **Why it works:** Number, method, honest exclusion, weak spot, plan.

**Q: How long is your sales cycle, and how many deals are in your pipeline?**
- **Weak:** "It's pretty quick." / "We have a lot of interest."
- **Strong (data exists):** "From first demo to signature the median is [X] days across the last [N] deals. We have [N] qualified deals worth [$] in pipeline, of which [N] are at proposal stage. We expect roughly [N] to close, based on [historical win rate]."
- **Strong (no data):** "We haven't tracked this in a system yet, so I can give you [what we do know, e.g., a rough range from the last N deals the founders closed themselves]. We're setting up pipeline tracking this month, and we'll share real numbers by [date]."
- **Why it works:** Admits the gap and states how and when it will close. It does not invent a figure.

**Q: Who are your five biggest customers, and what happens if you lose one?**
- **Weak:** "We have a healthy mix of customers."
- **Strong:** "Our top five are [X]% of MRR. The largest is [Y]%, renewing [date]. If we lost them, MRR drops by [$] and runway shortens by [N] months. We're reducing dependence by [action]."

**Q: Why now?**
- **Weak:** "The market is huge and growing."
- **Strong:** "[A specific change, such as a regulation, technology shift, or behavior shift] happened in [period]. It means [customers] now [do/need/can] [thing] that they couldn't before. Our evidence is [data point or customer behavior]."

## 10. Guardrails for investor coaching

1. **Never recommend a valuation.** The agent may explain how valuation, dilution, SAFEs, and convertible notes work, and may help the founder understand what a round does to their ownership. It must not suggest a number, a range or a target.
2. **Never invent data.** If the founder's files do not contain the figure, say so and help them find it. This includes competitor data, win/loss reasons, pipeline and market counts.
3. **Never present a forecast or unsigned deal as fact.** Label every number as actual or forecast.
4. **Never coach spin.** Helping a founder phrase an unflattering number well is coaching. Helping them hide it or redefine a metric to look better is not. If a founder's preferred definition would mislead an investor, say so and show the standard one.
5. **No legal, tax or securities advice.** Flag when a founder needs a lawyer or accountant (for example, SAFE terms, cap table questions, term sheet clauses).
6. **Don't use one founder's numbers as another's benchmarks, and don't invent benchmarks.** If the agent quotes a benchmark, it must name the public source (see `knowledge/public-resources.md`) and label the figure as a rule of thumb that varies by stage and sector. If no source is available, say so and do not quote one.
7. **Keep founder data private.** Treat everything in `workspace/` as confidential and never mix one founder's figures into another's coaching.
8. **Explain investor rights, don't advise on them.** Strategic and government-backed investors may ask for information rights, a right of first refusal, board seats, exclusivity or governance terms. The agent can explain what these mean and what questions the founder should ask, but must not advise whether to accept them. Flag that a lawyer should review any such terms.

## 11. Quick checklist before sending any investor answer to a founder

- [ ] Does it have a specific number with period and units?
- [ ] Does it say how the number was calculated?
- [ ] Does the number reproduce from the founder's files?
- [ ] Does it name the weak spot?
- [ ] Does it say what the founder is doing about it, with a date or trigger?
- [ ] Is it consistent with the deck and the founder's other answers?
- [ ] Could the founder say it out loud in under a minute?
- [ ] Does it avoid inventing anything not in the data?
