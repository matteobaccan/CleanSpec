# Chapter 11: Anatomy of a Spec-Driven Agent

Suppose two engineers at Meridian each ask a coding agent to add the same behavior — the fraud-suspension outcome from Chapter 7's withdrawal decision table — and they ask it two different ways. The first opens a chat session, pastes a summary of what's needed, and lets the conversation run: the agent asks a clarifying question, gets an answer, proposes an approach, gets a nudge, and after six exchanges produces a diff. Reading it afterward, the diff touches the withdrawal operation as requested, and it also reformats an adjacent function's docstring, renames a local variable in a file the task never mentioned, and adds a code comment explaining a design decision nobody asked it to explain. None of these extra touches is wrong exactly. All of them are surface area nobody reviewed for, because the conversation that produced them wandered exactly as far as an open conversation wanders.

The second engineer runs the same task through a constrained pipeline: a task description naming one specification and one operation, a fixed sequence of steps the agent must follow in order, and a validation stage that either accepts the result or hands back a specific, structured reason it did not. The agent reads the withdrawal decision table, derives the test for the new `SUSPENDED` outcome per Chapter 10's rules, writes the minimal implementation the test requires, and stops. The diff touches one file. There is no docstring reformatting, no renamed variable, no unrequested comment, not because the second agent is a better agent — it is very likely running the same underlying model as the first — but because nothing in its loop ever gave it permission to look at, let alone edit, anything the task did not name.

The difference between the two runs is not model quality. It is architecture: whether the agent operates as an open-ended conversational partner or as a constrained automaton with a fixed set of moves and one narrow channel for feedback. This chapter is about building the second kind on purpose, because Chapter 4 already argued that a nondeterministic compiler needs a compiler's discipline around it, and an open chat session is the one shape that discipline cannot survive contact with.

## 11.1 The constrained loop

A spec-driven agent moves through four states, always in the same order, and it is not permitted to skip one or invent a fifth.

$$\text{Spec} \longrightarrow \text{State 0 (Init)} \longrightarrow \text{State 1 (Plan)} \longrightarrow \text{State 2 (Execute)} \longrightarrow \text{State 3 (Validate)}$$

**Init** loads exactly the context 11.2 defines for the task at hand — the relevant specification, nothing from an unrelated domain, no chat history from a previous unrelated task. **Plan** produces a short, reviewable statement of what the agent is about to do, derived from the specification's clauses rather than invented, which Chapter 10 already showed in miniature as the derived test suite. **Execute** writes the implementation, and only the implementation; it does not touch a test file, because the tests were fixed during Plan and Execute's job is to satisfy them, not to renegotiate them. **Validate** runs the Three Gates from Chapter 10 and produces one of two outcomes: acceptance, or a specific, structured failure.

The failure path is where this architecture earns its name over an open conversation, and it rests on one formula:

$$\Delta = \text{Expected (from Spec)} - \text{Obtained (from Run)}$$

In words: the delta is the difference between what the specification's clauses said should be true and what the Three Gates actually observed. When Validate fails, the agent does not receive a fresh copy of the entire conversation, the entire specification, and a vague instruction to "try again." It receives the delta alone — the specific clause that failed, the specific assertion that did not hold, the specific type mismatch the checker reported — and returns to Execute with exactly that much new information added to what Init already loaded. This is the mechanical reason the second engineer's diff stayed narrow: nothing about a failed test for the `SUSPENDED` outcome ever told the agent anything about an adjacent docstring, because the docstring was never part of the delta, and the delta is the only thing a failed Validate step is allowed to hand back.

Init deserves one more word before moving on, because it is the state most often skipped by teams that adopt the other three and wonder why results stay inconsistent. Init is not "start the conversation"; it is a discrete step with its own output — a bounded, enumerated context, computed from the task's declared scope per 11.2 — that Plan then consumes as a fixed input. A loop that folds Init into Plan, letting the agent decide for itself what to read as it goes, reintroduces exactly the judgment call Chapter 7 argued an agent should never have to make, because the agent has no way to know that Billing's contracts are irrelevant to an Accounts task until it has already read enough of them to be influenced by what it read.

An open chat session has no delta. It has an accumulating transcript, in which the original task, every intermediate guess, every human nudge, and every unrelated observation the agent made along the way all sit in context with equal claim on the model's attention — which is Chapter 2's lost-in-the-middle effect, self-inflicted by the shape of the interaction itself rather than by the length of any one document. The constrained loop is not a restriction imposed on a capable agent out of caution. It is what makes the delta the only feedback channel, and the delta being the only feedback channel is what keeps a correction bounded to the size of the actual error.

## 11.2 Context budgeting

Chapter 7 argued that an agent should read outward from the boundary of its task rather than inward from the top of a four-hundred-page tree. Context budgeting is that argument turned into a concrete loading rule for Init, stated as what belongs in an agent's context for an ordinary task and what stays on disk unless a task specifically calls for it.

| Goes in | Stays out |
| :--- | :--- |
| `SPEC-ARCH-000`, in full, every task | Another domain's Level 1 or Level 2 documents |
| The Level 1 document for the module the task touches | The full platform schema, per Chapter 8's Interface Segregation Spec |
| The Level 2 document for the operation the task touches | Chat history from a previous, unrelated task |
| The agent instruction file (11.4) | Design notes, meeting transcripts, Slack threads |
| Existing tests for the operation being changed | The full commit history of the repository |
| The specific error or delta from a prior failed Validate | Specifications for planned, unbuilt features |

The right column is not an arbitrary blacklist; every entry on it is something Chapter 8's Interface Segregation Spec already argued against handing an agent whose task does not need it, or something Chapter 2's account of a crowded context already predicted would degrade the quality of every constraint sitting alongside it. A commit history is a narrative about how the code got here, not a statement of what the code must guarantee, and mixing narrative into a context window a generator is about to synthesize code from is exactly the kind of undifferentiated surface Chapter 8 warned would produce distraction rather than help.

The budget is also asymmetric in a way worth stating outright: it is cheap to be wrong by including too little, because a agent that hits a gap can ask, per 11.5, and Init can be re-run with more. It is expensive to be wrong by including too much, because there is no equivalent recovery from context that has already crowded out the clause that mattered — the model has already generated its answer, shaped by everything that was competing for its attention, before anyone gets to notice the mistake. When in doubt about whether something belongs in context, the cheaper failure mode is to leave it out.

## 11.3 Repository layout for context files

The budget in 11.2 is only enforceable if the repository's layout makes "the Level 1 document for the module the task touches" a path an agent instruction file can compute rather than a judgment call a human has to make every time.

```
meridian-ledger/
├── CLAUDE.md                              hand-written: agent instruction file
├── specs/
│   ├── architecture.md                    Level 0: SPEC-ARCH-000
│   └── modules/
│       ├── accounts/
│       │   └── SPEC-ACCT-003-withdrawal-authorization.md
│       ├── billing/
│       │   ├── SPEC-BILL-017-tiered-subscription-upgrade.md
│       │   └── tax-record.schema.json
│       └── payments/
│           ├── SPEC-PAY-042-transaction-confirmation-notifications.md
│           └── transaction-notification-event.schema.json
├── tests/
│   ├── contract/                          generated from specs/, reviewed by a human
│   └── property/                          generated from specs/, reviewed by a human
└── src/
    └── accounts/                          generated: never hand-edited
```

This is Chapter 4's tree and Chapter 9's naming convention, merged: one specification per file, its identifier in the filename, its companion schema beside it, nested one level under its domain. The nesting is what makes context budgeting computable rather than aspirational. A task ticket that names `SPEC-ACCT-003` resolves, mechanically, to `specs/modules/accounts/SPEC-ACCT-003-withdrawal-authorization.md` and nothing else in `specs/modules/`, because the domain folder is the boundary and the filename is the identifier, with no indirection between the two an agent instruction file has to reason about.

Two properties of this layout matter beyond the obvious one of being tidy. First, a Level 1 document and its schema are siblings in the same directory, so loading one for a task strongly suggests loading the other, which keeps Chapter 6's Data Model section and its companion JSON Schema from drifting into separate mental categories the way `checkout-core.md` in Chapter 8 let concerns drift into one undifferentiated file. Second, nothing about the tree requires an index file enumerating what exists, because Chapter 9 already established that the identifier and the path are the index — a routing rule can glob `specs/modules/<domain>/` and find every specification in that domain without a registry file that could itself go stale.

## 11.4 Anatomy of an agent instruction file

`CLAUDE.md`, or any file in its family, is the one document in this tree that is hand-written and is not a specification, a distinction Chapter 4 already drew and this section makes concrete. It does not say what must be true of the system; it says how work gets done in this repository, and a complete one has three parts.

```markdown
# Agent Instructions — meridian-ledger

## 1. Source of Truth

- The `specs/` directory is the authoritative source of truth for system behavior.
- Do not invent behavior that is not specified. If you encounter a semantic
  gap, STOP and request a specification update before writing any code.
- Never hand-edit a file under `src/`. If generated code is wrong, incomplete,
  or slow, the defect is in the specification — fix the specification and
  regenerate.

## 2. Workflow

1. Read `specs/architecture.md` (Level 0) once per task.
2. Read the Level 1 document for the module named in the task, and the
   Level 2 section for the specific operation.
3. Derive the test suite: one test per Failure Matrix row, one boundary
   test per Data Model bound, one property test per Invariants clause.
   Stop and present the suite for review before writing any implementation.
4. Write the minimal implementation required to satisfy the reviewed suite.
5. Run the Three Gates: lint, strict type check, contract tests.
6. If any gate fails, report the delta — the specific clause and the
   specific failure — and wait. Do not guess a broader fix.

## 3. Coding Constraints

- No untyped or dynamically typed values in domain or application code
  (no `any`, no bare `dict`/`object` where a value object is defined).
- Pure domain functions are separated from I/O side effects, per
  `SPEC-ARCH-000`'s dependency rule.
- Every generated public function carries a traceability comment naming
  the specification and section it implements.
```

Each numbered section answers a question 11.1 through 11.3 already raised in the abstract. Source of Truth states the Golden Rule from Chapter 4 as an operating instruction rather than an argument, and adds the stop condition 11.5 develops in full. Workflow is the constrained loop from 11.1, written as a checklist an agent can follow literally, with step 3 enforcing Chapter 10's rule that tests are reviewed before an implementation exists. Coding Constraints translates `SPEC-ARCH-000`'s Level 0 rules from Chapter 7 into instructions about the generated artifact itself, plus one addition — the traceability comment — that Chapter 12 turns into the mechanism a drift-detection linter reads.

What the file does not contain is just as deliberate as what it does. It states no business rule, no error code, no field name, because every one of those belongs in a specification the agent reads separately, and an instruction file that duplicates them is a second source of truth for exactly the reason Chapter 6 warned against duplicating a schema in prose. `CLAUDE.md` is short — the excerpt above is nearly the whole document for a repository this size — because its job, like `SPEC-ARCH-000`'s, is to be read on every single task, and a document everyone reads every time has to earn that cost by staying small.

## 11.5 Stop conditions

Chapter 10 ended with a specific failure mode: a clause a test cannot be derived for is a specification gap, not a testing problem to improvise around. This section generalizes that into the full set of conditions under which a spec-driven agent's correct behavior is to halt and ask rather than proceed on its best guess.

A **semantic gap** — a task requires a decision the specification does not make — is the clearest case and the one the instruction file in 11.4 names directly. If the withdrawal specification says nothing about what happens when a fraud-suspended account is closed before compliance reviews it, an agent that proceeds anyway is doing exactly what Chapter 2 described a generator doing with every silence: filling it from a statistical prior instead of from anything Meridian actually decided. The correct behavior is to stop, state the gap in the terms Chapter 9's Open Questions section expects, and wait for a human to close it in the specification before any code addresses it.

A **contradiction between two specifications** — Level 1 for one module states something that conflicts with Level 0's boundary rule, or two Level 2 decision tables disagree about a shared error code — is a second case, and it is the one an agent is least equipped to resolve on its own, because resolving it requires organizational authority over which document is wrong, not technical judgment about which reading is more plausible. Chapter 12's drift detection catches many of these mechanically before an agent ever encounters them; when one slips through, the instruction file's stop condition is the last line of defense.

An **undecidable test derivation**, Chapter 10's case restated, is a third: a clause with no way to construct a test that would fail if the clause were violated is not yet a testable clause, regardless of how clearly it reads as prose.

And a **gate failure with no localized delta** — a contract test fails in a way that implicates more of the system than the single operation the task was scoped to, suggesting the bug is not in the change but in an assumption the specification made about a dependency — is the fourth, and it is the case most tempting to push through with a quick patch, which is exactly the temptation Chapter 4's Golden Rule exists to name and resist. In every one of the four cases, the discipline is identical: the agent's job is to produce the most precise possible statement of what it does not know, not the most plausible guess at what to do about it, because the first is cheap to act on and the second is how a specification quietly stops being the source of truth.

## 11.6 Splitting roles

Nothing about the constrained loop requires one agent to perform all four states end to end, and for tasks above a certain size, splitting the work across roles with different context and different authority produces better outcomes than one agent doing everything in sequence.

A **spec reviewer** role reads a specification before any implementation work begins and checks it against the structural rules this book has spent two parts establishing: does it have all nine sections from Chapter 9, does every Failure Matrix row have a corresponding Level 2 rule, does every `N-` clause use RFC 2119 vocabulary correctly per Chapter 5, is the document under the 300-line limit or honestly split if not. This role never writes code and never writes tests; its entire output is a list of structural defects in the specification itself, caught before Chapter 10's derivation step has anything unreliable to derive from.

A **test synthesizer** role receives a specification that has passed review and performs exactly Chapter 10's transcription: one test per Failure Matrix row, one boundary test per schema bound, one property test per invariant. It has read access to the specification and the existing test directory, and no access to `src/` at all, which removes any temptation — architectural, not moral — to shape a test around what an implementation already does rather than around what the specification requires.

An **implementer** role receives the specification and the reviewed, accepted test suite, and only then writes code, exactly as 11.1's Execute state describes. It has no authority to modify the test suite it was handed; a test that turns out to be wrong is a finding the implementer reports upward, through the delta, not a file it edits on its own initiative.

The three roles can be three separate agent invocations, three separate context windows, or three passes within one longer-running process — the mechanism matters less than the separation of authority, which is the same argument Chapter 8's Interface Segregation Spec already made about schemas, applied here to the roles themselves. An implementer that cannot edit tests cannot quietly narrow them to fit whatever it was about to generate, which is the opening scenario's hardcoded discount branch prevented not by a smarter model but by a role that was never given the permission to make the problem disappear that way.

This is also where the constrained loop and Chapter 4's pipeline finally meet as the same diagram viewed at two different resolutions. Chapter 4 drew tests and code as two siblings descending independently from one specification; this chapter has now named who — or what — sits at the base of each branch. The test synthesizer is the left branch. The implementer is the right branch. The spec reviewer is the gate neither branch is allowed to start from until it passes. None of the three needs to trust the others' judgment, because none of the three is exercising judgment about anything outside its own narrow authority — the reviewer judges structure, the synthesizer judges coverage against Chapter 10's derivation rules, and the implementer judges nothing at all beyond how to satisfy a suite it did not write. Removing judgment from every place a specification could otherwise settle the question is, restated one more time, the entire argument of this book.

A team adopting this for the first time does not need all three roles from day one. A single agent running Plan, Execute, and Validate in sequence, with a human standing in for the spec reviewer during the Plan step, captures most of the benefit at a fraction of the setup cost, and splitting into fully separate roles is worth the overhead once a specification's Failure Matrix and decision tables are large enough that a single pass genuinely struggles to hold spec review, test derivation, and implementation in mind at once without one bleeding into another. The separation is a scaling response to complexity, not a prerequisite for starting.

## Key Takeaways

- A spec-driven agent moves through a fixed loop — Init, Plan, Execute, Validate — and receives only the delta between what the specification expected and what the run produced, never the whole transcript, which is what keeps a correction bounded instead of open-ended.
- Context budgeting turns Chapter 7's "read outward from the task" into a concrete rule: Level 0 always, the relevant Level 1 and Level 2 documents, the agent instruction file, and the current delta — nothing from an unrelated domain, no chat history, no commit narrative.
- A repository layout with one specification per file, its identifier in the filename, and its schema beside it makes context budgeting computable rather than a judgment call repeated on every task.
- An agent instruction file states how work gets done — source of truth, workflow, coding constraints — and states no business rule itself, because duplicating a specification's content in the instruction file creates a second source of truth for it.
- Stop conditions cover four cases: a semantic gap the specification never resolved, a contradiction between two specifications, a clause with no derivable test, and a gate failure whose delta implicates more than the task's own scope.
- In every stop condition, the agent's job is to state precisely what it does not know, not to guess plausibly at what to do about it.
- Splitting spec reviewer, test synthesizer, and implementer into separate roles with separate authority — especially denying the implementer any power to edit the tests it must satisfy — closes off the exact failure mode of an agent quietly narrowing its tests to match whatever it was about to write anyway.
