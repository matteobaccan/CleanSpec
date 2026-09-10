# Clean Spec — Style Guide

Every chapter file must honor this document. When a chapter and this file disagree, this file wins.

## 1. Voice and register

- First person singular ("I", "my experience", "I recommend"). Address the reader as "you".
- Direct and opinionated. State the principle, then argue for it. Do not hedge with "it could be argued".
- American English spelling (behavior, organize, license).
- Sentences average under 25 words. One idea per paragraph. Paragraphs of 2–6 sentences.
- Contractions are fine ("don't", "isn't") but not in normative statements inside spec examples.
- Humor is allowed sparingly and never at the reader's expense.
- Avoid marketing words: "revolutionary", "game-changing", "unlock", "leverage" (as a verb), "seamless".

## 2. Scenarios and anecdotes

- Every chapter opens with a concrete scenario of 200–400 words. It is explicitly hypothetical: "Imagine a team that...", "Picture a Tuesday afternoon...", "Suppose you inherit...".
- Never invent a personal story presented as true ("Last year at a client of mine..."). Where a true anecdote from the author would strengthen the point, insert an HTML comment on its own line: `<!-- AUTHOR: a real example of X would fit here; needs Y and Z. -->`
- The running fictional company is **Meridian**, a mid-size e-commerce and payments platform. Teams: Checkout, Billing, Ledger, Inventory, Identity. Use it for continuity; do not describe it beyond what a scenario needs.

## 3. Named principles and rules

Introduce a principle with a bold name the first time, then refer to it by name:

- **The Golden Rule of Clean Spec** (Chapter 4): never hand-edit generated code; if the code is wrong, the spec is wrong; fix the spec and regenerate.
- **Constraint Density** (Chapter 2): formal constraints divided by total tokens; a Clean Spec maximizes it.
- **The Three Levels** (Chapter 7): Level 0 architecture and boundaries, Level 1 contracts and data model, Level 2 state rules and edge cases.
- **The Three Gates** (Chapter 10): lint, strict type check, contract tests.
- **The 300-Line Rule** (Chapter 9): an atomic spec never exceeds 300 lines of Markdown.

## 4. Formulas

- Formulas may appear in `$...$` (inline) or `$$...$$` (display) LaTeX.
- Every formula is preceded or followed by a plain-English sentence stating what it means. A formula never stands alone as a paragraph.
- Prefer words when the formula adds nothing: "the sum of debits equals the sum of credits" is better than a summation sign in prose; use the formula inside a spec example where precision matters.

## 5. Code, schemas, and diagrams

- Code examples: Python 3 with type hints as the primary language; TypeScript as the secondary. Keep examples under 40 lines.
- Schemas: JSON Schema 2020-12 (`"$schema": "https://json-schema.org/draft/2020-12/schema"`). Always include `"additionalProperties": false` on object schemas in spec examples.
- Diagrams: Mermaid in ```` ```mermaid ```` fences for state machines (`stateDiagram-v2`) and sequences (`sequenceDiagram`). ASCII diagrams in plain ```` ``` ```` fences for pipelines and box layouts (reuse the draft's ASCII art where it exists).
- Tables: GitHub-flavored Markdown with a header row and alignment row. Every table has a one-sentence lead-in.
- Tools you may name: JSON Schema, Mermaid, RFC 2119, RFC 8174, Hypothesis, fast-check, mypy, tsc, pytest, Git, CI, CLAUDE.md-style instruction files (say "an agent instruction file such as CLAUDE.md"). Do not name LLM vendors, model names, IDEs, or SaaS products.
- Fences always start at column 0 and are never nested. Never wrap a Markdown spec example in an outer fence; show it as plain Markdown at heading levels H3/H4, with inner fences only for code, schemas, YAML, or diagrams.
- Inside an example spec, use H3 for the spec title (`### SPEC-PAY-042: ...`) and H4 for its sections (`#### 1. Scope`).

## 6. Normative statements in spec examples

- Use RFC 2119 keywords in uppercase: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY. Bold them in Markdown spec examples: **MUST**.
- Number normative statements inside a spec example as `N-1`, `N-2`, ... so they can be cited (`SPEC-PAY-042 N-3`).

## 7. Contract block format

When a chapter shows an operation contract, use this Markdown shape:

```markdown
**Operation:** `withdraw(account_id: AccountId, amount: Money) -> WithdrawalResult`

**Preconditions**
- P-1: `amount.cents > 0`
- P-2: The account identified by `account_id` exists and is `ACTIVE`.

**Postconditions**
- Q-1: On success, the account balance decreases by exactly `amount`.
- Q-2: On any failure, no balance changes.

**Invariants**
- I-1: `balance.cents >= 0` for every account at all times.

**Errors**
- `INSUFFICIENT_FUNDS` when `balance < amount`.
```

## 8. Spec ID registry

Only these IDs may appear in the manuscript. Sections are cited as `SPEC-PAY-042 §3`.

| ID | Title | Domain | Introduced in | Also used in |
| :--- | :--- | :--- | :--- | :--- |
| `SPEC-ARCH-000` | Meridian Platform Architecture (Level 0) | Platform | Chapter 7 | 9, 11 |
| `SPEC-PAY-042` | Transaction Confirmation Notifications | Payments | Chapter 6 | 5, 9, 10, 12, 13 |
| `SPEC-ACCT-003` | Withdrawal Authorization | Accounts | Chapter 7 | 3, 10 |
| `SPEC-ORD-007` | Order Lifecycle (state machine `FSM-ORD-01`) | Checkout | Chapter 14 | 13, 17 |
| `SPEC-BILL-017` | Tiered Subscription Upgrade | Billing | Chapter 12 | 8 |
| `SPEC-CORE-001` | Double-Entry Ledger | Ledger | Chapter 15 | 3, 10 |
| `SPEC-RATE-009` | Shipping Rate Calculator (reverse spec) | Logistics | Chapter 16 | — |
| `SPEC-INV-021` | Stock Reservation with Expiry | Inventory | Chapter 17 | 12 |

Adding an ID requires updating this table and `KNOWN_SPEC_IDS` in `tools/check_manuscript.py`.

## 9. Chapter skeleton

```markdown
# Chapter N: Title

[Opening scenario, 200–400 words, hypothetical.]

## N.1 First section
...
## N.k Last section
...
## Key Takeaways

- Bullet, one sentence, states a rule or a fact.
- 5 to 8 bullets.
```

- Exactly one H1 per chapter file. Sections are H2 and numbered `N.1`, `N.2`, ... Sub-sections are H3, unnumbered.
- The `## Key Takeaways` heading is followed immediately by the bulleted list, using `-` bullets, with no lead-in sentence.
- Refer to the closing chapter as "the Epilogue", never "Chapter 18". Refer to appendices as "Appendix A" through "Appendix D".
- Cross-reference chapters as "Chapter 7" (capitalized, numeral). Never "the next chapter" or "above/below".
- 3,500–5,500 words per chapter. Run `python tools/check_manuscript.py manuscript/<file>` before committing.

## 10. Terminology (use consistently)

| Use | Not |
| :--- | :--- |
| coding agent, agent | AI, the model, the bot, copilot |
| language model | LLM (spell out on first use per chapter, then "language model") |
| specification, spec | requirement doc, prompt (a prompt is an input to a model; a spec is an artifact) |
| Clean Spec (the discipline, capitalized) | clean spec (lowercase only when meaning "a spec that is clean") |
| Spec-Driven Development (SDD) | spec-first development |
| failure matrix | error table |
| decision table | rules table |
| state machine, state table | FSM (may be used in spec IDs like `FSM-ORD-01`) |
| value object | wrapper type |
| port (Clean Architecture sense) | interface (fine in code, avoid in prose about boundaries) |
| generated code, synthesized code | AI code |
| spec drift | divergence |
