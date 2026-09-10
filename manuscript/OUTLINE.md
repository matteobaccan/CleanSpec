# Clean Spec — Outline

Word targets are the midpoint of the 3,500–5,500 range unless noted. Source column points at `book.md` line ranges.

## Front matter — `00-front-matter.md` (2,500 words, 3 H1s)
- Preface: why this book, why now, what changed when code became cheap.
- Who This Book Is For: senior developers, tech leads, architects; what you need to know already.
- How to Read This Book: the five parts, running example (Meridian), spec IDs, formulas policy, hypothetical scenarios.

## Part I — Why Specifications Matter Now

### 1. The Commoditization of Code — `01-commoditization-of-code.md` (4,000) — source 7–75
- Scenario: a weekend prototype that cannot be changed three months later.
- 1.1 Four leaps in abstraction (table: era, what got automated, what became the primary artifact).
- 1.2 Source code as intermediate representation; the model as a nondeterministic compiler.
- 1.3 The vibecoding curve: generation cost O(1), verification cost O(N²) (ASCII chart from draft, explained in words).
- 1.4 The only artifact with positive cognitive return.
- 1.5 What this book does not claim (agents still fail; engineers are not obsolete; specs do not remove judgment).
- Key Takeaways.

### 2. What a Language Model Does With Your Words — `02-what-a-language-model-does.md` (4,000) — source 77–117
- Scenario: same prompt, two runs, two different implementations of the same transfer function.
- 2.1 Next-token prediction in plain words (the conditional probability formula, explained).
- 2.2 Collapsing the output space: "handle financial transactions carefully" vs. the formal transfer tuple (before/after).
- 2.3 Where defaults come from: training-set priors (floats for money, swallowed exceptions, no isolation).
- 2.4 Context windows, lost-in-the-middle, context poisoning.
- 2.5 Constraint Density: definition, before/after paragraph with approximate token counts.
- 2.6 Six practical rules to raise density.
- Key Takeaways.

### 3. Contracts, Not Conversations: Hoare Logic for Working Engineers — `03-contracts-not-conversations.md` (4,000) — source 119–136
- Scenario: an agent implements `withdraw` and lets the balance go negative because nobody said it couldn't.
- 3.1 The Hoare triple in plain words.
- 3.2 Preconditions: what the caller promises.
- 3.3 Postconditions: what the operation promises.
- 3.4 Invariants: what is always true (domain invariants vs. loop invariants).
- 3.5 The contract block format (STYLE.md §7) applied to `withdraw` from `SPEC-ACCT-003`.
- 3.6 From contract to test: one assertion per clause (preview of Chapter 10).
- 3.7 Strength of contracts: weakening preconditions, strengthening postconditions (preview of Chapter 8, Liskov).
- 3.8 What a missing contract costs: the agent extrapolates.
- Key Takeaways.

### 4. Spec-Driven Development: Inverting the Flow — `04-spec-driven-development.md` (4,000) — source 138–177
- Scenario: two Meridian teams build the same feature; one prompts, one specs; compare at week six.
- 4.1 From TDD to SDD (table: waterfall, agile, TDD, SDD; who writes what, what is the source of truth).
- 4.2 The SDD pipeline (ASCII diagram from draft).
- 4.3 The Golden Rule of Clean Spec.
- 4.4 Objections and answers: hotfixes, regeneration cost, "the model is wrong, not the spec", exploratory code.
- 4.5 The spec as single source of truth; what lives where in the repository (preview of Chapter 11 tree).
- 4.6 When SDD is the wrong tool (throwaway scripts, spikes, unknown domains).
- Key Takeaways.

## Part II — Anatomy of a Clean Spec

### 5. The Failure of Natural Language — `05-failure-of-natural-language.md` (4,000) — source 181–204
- Scenario: the payment-notification sentence read by three engineers and an agent; four readings.
- 5.1 Why natural language works for people and fails for compilers.
- 5.2 A taxonomy of ambiguity (table: lexical, syntactic, scope, referential, temporal, quantifier; each with an example).
- 5.3 RFC 2119 and RFC 8174 vocabulary (table; uppercase rule; the boilerplate sentence).
- 5.4 Rewriting the sentence as normative statements N-1..N-5 of `SPEC-PAY-042`.
- 5.5 Common misuses: SHOULD as polite MUST; MAY for undecided; "will"; negated SHOULD.
- 5.6 Beyond modal verbs: quantify everything (numbers, units, time bounds, cardinalities).
- Key Takeaways.

### 6. A Composite Grammar: Markdown, Schemas, Diagrams — `06-composite-grammar.md` (4,200) — source 206–289
- Scenario: the same notification spec written as one page of prose, then as the tripartite form.
- 6.1 Three layers: Markdown for structure and norms, schemas for data, diagrams for dynamics.
- 6.2 Markdown conventions: addressable headings, numbered normative statements, tables.
- 6.3 JSON Schema for contracts: the `TransactionNotificationEvent` schema, keyword by keyword.
- 6.4 Typed alternatives (Pydantic models, TypeScript types) and when to use them.
- 6.5 Mermaid for dynamics: the delivery state machine of `SPEC-PAY-042`; a sequence diagram for the same flow.
- 6.6 The assembled `SPEC-PAY-042` (full example).
- 6.7 What not to put in a spec: screenshots, pseudo-code, prose that duplicates the schema.
- Key Takeaways.

### 7. The Three Levels of a Spec — `07-three-levels-of-a-spec.md` (4,200) — source 291–336
- Scenario: an agent asked to add one feature is handed 400 pages; what should it read?
- 7.1 The concentric levels (ASCII diagram from draft).
- 7.2 Level 0: architecture and boundaries; `SPEC-ARCH-000` excerpt (dependency rule, allowed components, technology constraints).
- 7.3 Level 1: contracts and data model; value objects over primitives; the Failure Modes Matrix (table from draft) and how to build one.
- 7.4 Level 2: state rules and edge cases; the withdrawal decision table `SPEC-ACCT-003` (table from draft); completeness and consistency checks for decision tables.
- 7.5 How levels reference each other; what an agent reads for a given task.
- Key Takeaways.

### 8. SOLID for Specifications — `08-solid-for-specifications.md` (4,200) — source 338–371
- Scenario: one spec file that changes every week for five unrelated reasons.
- 8.1 Single Responsibility Spec: one reason to change; the 300-line rule of thumb.
- 8.2 Open/Closed Spec: extend by adding subscribers, not by editing the core (`SPEC-PAY-042` SMS channel example).
- 8.3 Liskov Substitution for Specs: `PaymentGatewayPort` and the 60-second idempotency window; what an adapter may not do.
- 8.4 Interface Segregation Spec: role-specific views; the 50-endpoint schema problem.
- 8.5 Dependency Inversion Spec: `TaxRecordPersistencePort.save` vs. "UPSERT into tax_records"; `SPEC-BILL-017` as the high-level spec.
- 8.6 Summary table: principle, spec form, smell it prevents (forward references to Chapter 13).
- Key Takeaways.

### 9. Naming, Structure, and Size of a Spec — `09-naming-structure-size.md` (4,000) — new
- Scenario: "which spec is current?" asked in a release meeting; three answers.
- 9.1 Spec identifiers: `SPEC-<DOMAIN>-<NNN>`, immutability, section addressing (`SPEC-PAY-042 §3`).
- 9.2 Files and directories: `specs/modules/<domain>/<id>-<slug>.md`, companion `schema.json`.
- 9.3 The header block (YAML front matter: id, title, version, status, owner, depends_on, supersedes).
- 9.4 The nine mandatory sections in fixed order: Scope, Normative Constraints, Data Model, Invariants, Failure Matrix, State Rules, Test Requirements, Open Questions, Changelog.
- 9.5 The 300-Line Rule: token budget arithmetic, splitting rules, what to do with a spec that will not fit.
- 9.6 Numbering normative statements (N-), preconditions (P-), postconditions (Q-), invariants (I-).
- 9.7 Status lifecycle: draft, review, active, deprecated (detailed in Chapter 12).
- Key Takeaways.

## Part III — Verification, Validation, and Agentic Workflows

### 10. Spec-First, Test-First — `10-spec-first-test-first.md` (4,200) — source 377–414
- Scenario: an agent hardcodes the answer to pass a single example test.
- 10.1 Tests are derived, not invented: decision-table rows, schema bounds, invariants.
- 10.2 Property-based testing as the anti-hallucination guarantee (Hypothesis example from draft; fast-check equivalent).
- 10.3 Contract tests from the failure matrix: one test per row (`SPEC-CORE-001` rows).
- 10.4 The Three Gates (ASCII diagram from draft): lint, strict types, contract tests.
- 10.5 Ordering the agent's work: tests first; what to do when a test cannot be written (a spec gap).
- 10.6 Coverage means spec coverage, not line coverage.
- Key Takeaways.

### 11. Anatomy of a Spec-Driven Agent — `11-anatomy-of-a-spec-driven-agent.md` (4,200) — source 416–466
- Scenario: the same task run in an open chat and in a constrained loop.
- 11.1 The constrained loop: Init, Plan, Execute, Validate; the Delta as the only feedback.
- 11.2 Context budgeting: what goes in, what stays out (table).
- 11.3 Repository layout for context files (tree from draft).
- 11.4 Anatomy of an agent instruction file (full English example of the draft's CLAUDE.md-style file).
- 11.5 Stop conditions: when the agent must halt and ask (semantic gaps).
- 11.6 Splitting roles: spec reviewer, test synthesizer, implementer.
- Key Takeaways.

### 12. Specs Under Version Control — `12-specs-under-version-control.md` (4,000) — source 468–514
- Scenario: a 2 a.m. hotfix that the spec never learns about.
- 12.1 Spec commits and implementation commits (the two commit messages from the draft, `SPEC-BILL-017`).
- 12.2 Versioning a spec: semantic versioning rules for specs; the Changelog section.
- 12.3 The status lifecycle and review flow.
- 12.4 Drift detection: schema check, exhaustive error coverage, traceability tags (`@implements_spec`).
- 12.5 A conformance linter in CI: what it checks, sample configuration.
- 12.6 Handling the hotfix: the reverse-drift procedure.
- Key Takeaways.

## Part IV — Spec Smells and Refactorings

### 13. A Catalog of Spec Smells — `13-catalog-of-spec-smells.md` (5,000) — source 518–562
- Scenario: a spec review where every reviewer feels something is wrong and nobody can name it.
- Intro: why a vocabulary of smells matters.
- One H2 per smell, each with Symptom, Example, Consequence, Cure (naming the Chapter 14 refactoring):
  13.1 The Omniprompt; 13.2 The Handwave; 13.3 Syntactic Micromanagement; 13.4 Domain Leakage; 13.5 Happy Path Only; 13.6 Ghost Invariant; 13.7 Prose State Machine; 13.8 Example as Specification; 13.9 Modal Mush; 13.10 Primitive Obsession; 13.11 Zombie Spec.
- Summary table: smell, detection question, refactoring.
- Key Takeaways.

### 14. A Catalog of Spec Refactorings — `14-catalog-of-spec-refactorings.md` (5,000) — source 564–599
- Scenario: a review turns a smelly spec into a clean one in one afternoon.
- One H2 per refactoring, Fowler format (Motivation, Mechanics, Example before/after):
  14.1 Replace Prose with State Table (`SPEC-ORD-007`, `FSM-ORD-01`); 14.2 Extract Bounded Context Spec; 14.3 Introduce Failure Matrix; 14.4 Replace Primitive with Value Object; 14.5 Extract Invariant from Examples; 14.6 Normalize Modal Verbs; 14.7 Replace Procedure with Postcondition; 14.8 Invert Infrastructure Dependency; 14.9 Split Role-Specific View.
- Key Takeaways.

## Part V — Case Studies and Practice

### 15. Case Study: A Double-Entry Ledger — `15-case-study-double-entry-ledger.md` (4,500) — source 603–663
- Scenario: Meridian's Ledger team must replace a float-based balance table.
- 15.1 The problem and the constraints.
- 15.2 The full `SPEC-CORE-001`, in the Chapter 9 template, section by section with commentary.
- 15.3 What the agent generates first: the test suite (property tests for the three invariants; one test per failure-matrix row).
- 15.4 What the agent generates second: the domain types (`Money`, `LedgerEntry`, `Transaction`) in Python.
- 15.5 A walkthrough of one failure: an unbalanced transaction.
- 15.6 Lessons.
- Key Takeaways.

### 16. Case Study: Reverse-Specifying a Legacy System — `16-case-study-reverse-specifying-legacy.md` (4,200) — source 665–702
- Scenario: a 900-line shipping-rate function nobody dares touch.
- 16.1 Why blind rewrites fail.
- 16.2 The four phases (ASCII diagram from draft): Reverse Spec, Human Audit, Test Synthesis, Re-synthesis.
- 16.3 Rules for the reverse spec: hidden side effects, big-ball-of-mud variables, implicit rules.
- 16.4 Worked example: a legacy Python fragment; the raw reverse spec the agent produces; the audited `SPEC-RATE-009` with a decision table; the characterization tests.
- 16.5 Re-synthesis and the safety net.
- 16.6 What to do with behavior nobody wants to keep.
- Key Takeaways.

### 17. Case Study: One Feature, End to End — `17-case-study-one-feature.md` (5,000) — new
- Scenario: the ticket "reserve stock during checkout, release after 15 minutes".
- 17.1 From ticket to draft spec (`SPEC-INV-021` v0.1).
- 17.2 Spec review: three smells found and fixed (v1.0).
- 17.3 The agent's plan and first test suite (hypothetical transcript excerpts).
- 17.4 The first failure: expiry during payment; a spec gap.
- 17.5 Amending the spec (v1.1), regenerating, the commit pair.
- 17.6 Retrospective: what the spec caught that a prompt would not.
- Key Takeaways.

## Epilogue — `18-epilogue.md` (2,000) — source 704–707
- The Specification Is the Software: architects of constraints; what changes for careers, teams, education; a closing charge.

## Appendices — `19-appendices.md` (4,500, 1 H1 with H2 per appendix)
- A. Clean Spec Template (the nine sections, ready to copy).
- B. RFC 2119 Cheat Sheet.
- C. Spec Review Checklist (one question per smell, plus structure checks).
- D. Glossary (about 40 terms).
