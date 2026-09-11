# Appendices

These four appendices are reference material, not a fifth part of the argument. Each one distills a discipline the main chapters spent a full chapter deriving into a form meant to sit open in a second window while you draft, review, or onboard a colleague — the template to start from, the vocabulary to check against, the checklist to run before a document leaves review, and the shared terms to point a newcomer at instead of re-explaining them from scratch every time.

None of the four appendices replaces reading the chapter it summarizes. A template filled in without understanding why each section exists produces a document that satisfies `check_manuscript.py`-style structural linting and still contains every smell Chapter 13 catalogs; a checklist run mechanically by someone who has not internalized what each question is actually testing for becomes a box-ticking exercise rather than a review. Treat what follows as compressed notation for arguments made in full elsewhere, in the same spirit RFC 2119's own cheat sheet in Appendix B compresses a standard that took the IETF far more than one page to justify.

## Appendix A: Clean Spec Template

Copy the block below as the starting point for any new specification. Replace every bracketed placeholder; delete no section, even when its content is only the word "None." Chapter 9 develops the reasoning behind each part in full, and Chapter 15's assembled `SPEC-CORE-001` is the fullest worked example of every section filled in at once.

```markdown
---
id: SPEC-<DOMAIN>-<NNN>
title: [Human-readable title]
version: 0.1.0
status: draft
owner: [team or guild]
depends_on: []
supersedes: []
---

# SPEC-<DOMAIN>-<NNN>: [Title]

## 1. Scope

[What this document governs, and what it explicitly does not.]

## 2. Normative Constraints

- N-1: [A single obligation, using MUST, MUST NOT, SHOULD, SHOULD NOT, or MAY.]

## 3. Data Model

[Value objects and, where data crosses a boundary, a JSON Schema with
`additionalProperties: false`.]

## 4. Invariants

**Operation:** `[operationName(args) -> ReturnType]`

**Preconditions**
- P-1: [What the caller must guarantee before calling.]

**Postconditions**
- Q-1: [What the operation guarantees on return.]

**Invariants**
- I-1: [What is always true, for every reachable state.]

**Errors**
- `[ERROR_CODE]` when [condition].

## 5. Failure Matrix

| Condition | Category | Domain Code | Required Action |
| :--- | :--- | :--- | :--- |
| [condition] | [Business / Infra / Contract] | `[CODE]` | [action] |

## 6. State Rules

[A decision table or a state-transition table; never conditional prose.]

## 7. Test Requirements

[What the derived suite must cover: one test per Failure Matrix row, one
boundary test per Data Model bound, one property test per invariant.]

## 8. Open Questions

[Decisions not yet made, stated honestly. Write "None at this time" if
there are genuinely none.]

## 9. Changelog

- **0.1.0** — [date]: Initial draft.
```

## Appendix B: RFC 2119 Cheat Sheet

Chapter 5 develops the reasoning; this is the reference to keep open while drafting. The vocabulary fixes exactly one of the six kinds of ambiguity Chapter 5's taxonomy names — obligation strength — and nothing here substitutes for quantifying a magnitude, naming a channel, or resolving a referential gap; those still need the specific number, name, or clause the sentence was missing.

| Keyword | Meaning | Example |
| :--- | :--- | :--- |
| MUST / SHALL | An absolute requirement. | "The account **MUST** exist and be `ACTIVE`." |
| MUST NOT / SHALL NOT | An absolute prohibition. | "Dispatch **MUST NOT** block the payment transaction." |
| SHOULD / RECOMMENDED | A recommendation; valid reasons to deviate may exist, but the implications must be understood and weighed first. | "Retries **SHOULD** use exponential backoff." |
| SHOULD NOT / NOT RECOMMENDED | The inverse recommendation; the same weighing applies before permitting the behavior. | "A single request **SHOULD NOT** exceed 1 MB." |
| MAY / OPTIONAL | A genuinely discretionary feature; no caller may assume its presence or its absence. | "The system **MAY** additionally deliver by SMS." |

The keywords carry this meaning **only** in uppercase. State the boilerplate sentence near the top of every specification that uses them:

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119 and RFC 8174, when, and only when, they appear in all capitals, as shown here.

Four checks before a draft leaves review: no SHOULD is standing in for a MUST the author was reluctant to write; no MAY is standing in for an undecided question that belongs in Open Questions instead; no "will" is doing the work of a normative keyword; no SHOULD NOT is standing in for an absolute prohibition that needs MUST NOT. A fifth check catches what the vocabulary alone cannot: scan every adjective and adverb near a modal keyword — "quickly," "reasonably," "as needed" — and replace it with a number, a unit, or a named bound, because a precisely worded obligation attached to an unquantified magnitude is still, in practice, an instruction to guess.

## Appendix C: Spec Review Checklist

Run every draft through both halves of this checklist before it leaves `review` status. The eleven smell questions are Chapter 13's summary table in full; the structure questions are Chapter 9's template, restated as things a reviewer actively confirms rather than assumes. Neither half substitutes for the other — a document can pass every structure question with all nine sections present and still carry a Handwave inside its Normative Constraints section, and a document with no smells present can still be missing a mandatory section a reviewer forgot to check for.

**Smell questions**

1. Does this file have more than one reason to change? *(The Omniprompt)* — Name every team or actor who could legitimately request an edit; more than one means the document has already absorbed a second responsibility.
2. Could two competent engineers implement this sentence differently and both be right? *(The Handwave)* — If yes, the sentence is an adjective standing in for a requirement nobody has written yet.
3. Does this clause name a variable, a loop, or an algorithm instead of an outcome? *(Syntactic Micromanagement)* — Ask whether the clause would need to change if the implementation language changed; if so, it is procedure, not a guarantee.
4. Would this clause survive swapping the database or the framework? *(Domain Leakage)* — A clause naming a table, a query verb, or a status code belongs in an adapter document, not here.
5. Does this document say anything about what happens when something goes wrong? *(Happy Path Only)* — A specification with only a success path is missing its Failure Matrix, not merely light on detail.
6. Does every invariant have a test that fails the moment it is violated? *(Ghost Invariant)* — A stated invariant with no enforcing test is worse than no invariant, because it creates false confidence.
7. Can every state and transition be listed without a second read of the paragraph? *(Prose State Machine)* — If a second read reveals a state the first read missed, the lifecycle belongs in a table.
8. Is there a general rule here, or only worked examples? *(Example as Specification)* — A handful of input-output pairs is satisfied as readily by a hardcoded special case as by a correct rule.
9. Is every MAY and SHOULD here actually scoped to the reader in front of it? *(Modal Mush)* — A discretionary field sitting near fifty unrelated ones invites a reader to stretch it by analogy.
10. Could this field hold an invalid value and still pass type-checking? *(Primitive Obsession)* — A bare primitive where a value object belongs pushes an enforceable invariant onto a validation branch someone has to remember to write.
11. Would anyone notice if this document silently disappeared? *(Zombie Spec)* — If the answer is no, the document has already stopped being anyone's source of truth.

**Structure questions**

- Does the header carry `id`, `title`, `version`, `status`, `owner`, `depends_on`, and `supersedes`? A missing field is a question the document cannot answer about itself.
- Are all nine sections present, in order, even where a section reads "None"? An omitted section is indistinguishable from one nobody thought to write.
- Is every normative statement numbered `N-`, and every precondition, postcondition, and invariant numbered `P-`, `Q-`, or `I-`? An unnumbered rule cannot be cited by a test, a review comment, or a commit message.
- Is the document under three hundred lines, or, if not, is the overage an honestly large single responsibility rather than a second domain that crept in? Length past the limit is a symptom to investigate, not an automatic failure.
- Does every Failure Matrix row have a named domain code and a required action, not a generic "error"? A generic error tells a caller nothing it can branch on.
- Does the file live at `specs/modules/<domain>/<id>-<slug>.md`, with any companion schema beside it? A specification with no fixed location invites exactly the "which document is current" confusion Chapter 9 opened with.
- Does every schema set `additionalProperties: false`? A schema that admits arbitrary extra fields is a suggestion, not a contract.
- Is every cross-reference to another specification a citation by identifier and section, never a vague pointer like "see the withdrawal rules"? A vague pointer cannot be checked for accuracy the way a numbered citation can.

## Appendix D: Glossary

Roughly forty terms this book treats as load-bearing vocabulary, gathered here so a reader can look one up without hunting back through the chapter that coined it. Where a term was given a formal, numbered form earlier in the book, the glossary entry states the plain-language sense rather than reproducing the notation.

**Agent instruction file.** A hand-written, non-normative document, such as one in the `CLAUDE.md` family, stating how work gets done in a repository — source of truth, workflow, coding constraints — never a business rule itself.

**Boundary test.** A test constructed at the exact edge of a schema's stated bound — the smallest legal value, or one unit past the largest allowed one — confirming a `minimum`, `maximum`, or `pattern` is actually enforced rather than merely documented on paper.

**Bounded context.** A domain boundary, usually matching a team's ownership, inside which one vocabulary and one set of rules apply consistently.

**Changelog.** A specification's ninth mandatory section, recording one dated, attributed entry per version bump, naming the clause that changed rather than describing the change in vague terms.

**Characterization test.** A test that pins a system's actual current behavior rather than its intended behavior, used to build a safety net before reverse-specifying or refactoring legacy code.

**Clean Spec.** The discipline this book teaches: writing specifications precise enough that a nondeterministic generator's output space narrows to correct implementations.

**Commit pair.** A specification commit and its linked, regenerated implementation commit, authored separately and cross-referenced by hash, so a reviewer arguing about a business rule reviews exactly the commit that states it.

**Conformance linter.** A CI tool that checks a specification and its code for drift: schema mismatches, missing error coverage, and broken traceability tags.

**Constrained loop.** The four-state cycle — Init, Plan, Execute, Validate — a spec-driven agent moves through, receiving only the delta between expected and observed behavior on a failed validation rather than an open-ended conversation.

**Constraint Density.** The ratio of formal constraints to total tokens in a specification; a Clean Spec maximizes it.

**Context budgeting.** The discipline of loading only the specification content a task's declared scope requires into an agent's context, and leaving the rest on disk.

**Contract.** An operation's stated preconditions, postconditions, invariants, and errors, in the block format Chapter 3 defines.

**Contract test.** A test transcribed directly from one Failure Matrix row or one clause of a contract, named after the clause it verifies.

**Decision table.** An exhaustive grid of condition combinations and their outcomes, used in place of conditional prose to state dynamic rules.

**Delta.** The specific difference between a specification's expected result and a run's actual result, and the only feedback a constrained agent loop passes back on a failed validation.

**Domain invariant.** A business truth that holds for every reachable state of a system, belonging in a specification; contrast with a loop invariant.

**Failure matrix.** The exhaustive, categorized catalog of an operation's named error conditions and required actions.

**Golden Rule of Clean Spec.** Never hand-edit generated code; if the code is wrong, incomplete, or slow, the defect is in the specification — fix the spec and regenerate.

**Hoare triple.** The notation $\{P\}\ C\ \{Q\}$: if precondition $P$ holds before command $C$ runs, postcondition $Q$ holds after.

**Invariant.** A condition that must hold at every moment an outside observer could look, for every path through the system, for all time.

**Level 0, 1, 2.** The three concentric specification levels: architecture and boundaries, contracts and data model, and state rules and edge cases, respectively.

**Loop invariant.** A truth about a specific mechanism's iteration, belonging in an implementation, not a specification.

**Idempotency window.** A stated duration within which a repeated call carrying the same identifying key must be treated as a single operation rather than executed twice, and which every implementation of a port must honor at least as generously as the port's own contract states it must.

**MAJOR / MINOR / PATCH.** The three levels of a specification's semantic version: MAJOR for a broken guarantee, MINOR for a backward-compatible addition, PATCH for a clarification with no semantic change — classified by whether a conforming caller could break, never by whether the diff merely looks additive.

**Meridian.** The fictional mid-size e-commerce and payments platform this book's scenarios are set at, with teams named Checkout, Billing, Ledger, Inventory, and Identity.

**Nine-section template.** The fixed, always-present, always-ordered section structure — Scope, Normative Constraints, Data Model, Invariants, Failure Matrix, State Rules, Test Requirements, Open Questions, Changelog — every Clean Spec follows.

**Normative statement.** An RFC 2119–governed sentence, numbered `N-`, stating an obligation.

**Open Questions.** A specification's eighth mandatory section, recording a decision the team has not yet made, so a genuine unknown has a place to live where a reviewer or an agent can see it rather than being silently guessed at.

**Port.** An abstract interface a domain layer defines and depends on, implemented by one or more concrete adapters it never names directly.

**Regeneration.** Synthesizing a module's implementation afresh from its current specification, the normal response to a specification change, rather than hand-editing the previous generated output.

**Reverse-drift procedure.** The four-step repair Chapter 12 prescribes for a production hotfix: record the divergence, read the hand-written fix as evidence of a missing clause, add the clause through normal review, and regenerate so the fix survives every future regeneration instead of being silently overwritten by the next one.

**Role split.** Dividing spec review, test synthesis, and implementation across separate agent contexts with separate authority, so an implementer can never quietly narrow the tests it must satisfy to whatever it was about to generate anyway.

**Stop condition.** One of the situations — a semantic gap, a contradiction between specifications, an untestable clause, an unlocalized gate failure — in which a spec-driven agent's correct behavior is to halt and report precisely what it does not know, rather than guess a plausible answer and proceed as though the gap had never existed.

**Postcondition.** What an operation guarantees on return, stated as an exact relation between the state before and after.

**Precondition.** An obligation on the caller; a condition the operation is entitled to assume and is not responsible for checking.

**Property-based testing.** Testing a universally quantified property against a search-generated space of inputs, rather than a hand-picked set of examples.

**Reverse spec.** A specification drafted by reading existing, undocumented code and describing its actual behavior, as the first phase of reverse-specifying a legacy system.

**RFC 2119 / RFC 8174.** The IETF standards defining the uppercase modal vocabulary — MUST, SHOULD, MAY, and their negations — this book's normative statements use.

**Schema.** A JSON Schema, written to the 2020-12 specification with `additionalProperties: false`, stating a data contract's shape exhaustively.

**Semantic gap.** A task that requires a decision the specification never makes anywhere, and the most common of the four stop conditions an agent actually encounters in ordinary day-to-day work.

**SOLID for Specifications.** The five principles of Chapter 8 — Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion — restated for specification documents rather than classes.

**Spec coverage.** The fraction of a specification's numbered clauses with at least one derived test exercising it; contrast with line coverage.

**Spec drift.** The condition where a specification and its implementation have diverged and nothing has recorded that they have.

**Spec ID.** An identifier of the form `SPEC-<DOMAIN>-<NNN>`, permanent, never reassigned, and never reused after deprecation.

**Spec-Driven Development (SDD).** The method in which a human-authored specification determines both a derived test suite and a synthesized implementation, as independent siblings, rather than one being derived from the other.

**Spec smell.** A recurring, named pattern in a specification correlated with future failure, cataloged in Chapter 13.

**Spec refactoring.** A named, repeatable procedure — Motivation, Mechanics, Example — for curing one spec smell, cataloged in Chapter 14.

**State machine.** A finite set of states and the guarded transitions between them, expressed as a table or a diagram rather than conditional prose.

**Status lifecycle.** The four values a specification's `status` field moves through in order: draft, review, active, deprecated.

**Substitution rule.** An implementation may accept more than its contract requires and guarantee more than its contract promises, but never less of either.

**The Three Gates.** The deterministic validation sequence: syntactic lint, strict type check, contract tests.

**The 300-Line Rule.** An atomic specification never exceeds three hundred lines of Markdown.

**Traceability tag.** A machine-readable annotation, such as `@implements_spec`, joining a function to the specification clause it implements.

**Value object.** A named, immutable type whose constructor enforces an invariant, used in place of a bare primitive.

**Vibecoding curve.** The relationship Chapter 1 describes between generation cost, which stays roughly constant, and verification cost, which grows with the complexity of what was generated.

**Working memory.** The portion of an agent's context window actually available to influence generation quality on the task at hand, which shrinks — in effective terms, not merely in token count — as irrelevant material crowds in alongside it, the mechanism behind the lost-in-the-middle effect Chapter 2 describes.

**Zombie Spec.** A specification that still exists and still carries an `active` status while no longer describing what the code actually does, and that nobody on the team trusts enough to read before making a change — detectable only by comparing the document against running behavior, never by reviewing the document alone.
