# Chapter 7: The Three Levels of a Spec

Imagine an engineer on Meridian's Accounts team asks a coding agent to add one behavior: a withdrawal that trips the fraud detector should be suspended for compliance review instead of silently rejected. It is a small change, a few hours of work for a human who already knows the codebase. The engineer, wanting to be thorough, points the agent at `specs/` and lets it read everything, on the theory that more context can only help.

`specs/` at Meridian is, by this point in the company's life, about four hundred pages: the platform architecture, five domains' worth of contracts and data models, a dozen state machines, and every failure matrix anyone has written since the migration off spreadsheets. The agent reads all of it, because nothing told it not to. What comes back is technically functional and structurally wrong in a way that takes a careful review to catch: it adds the suspension behavior, and it also renames a field in the failure matrix it happened to read most recently, on the reasonable-looking theory that the naming was inconsistent with a convention from an unrelated Billing document three hundred pages earlier. Nothing about the diff looks like a mistake. The agent was not confused. It was given four hundred pages and no way to know that three hundred and ninety of them were not its problem.

The failure here is not verbosity, and it is not the agent's judgment. It is that "the specification" was never one document with one shape; it is at least three different kinds of statement, answering three different questions, at three different distances from any given task. Architecture rarely changes and every task needs to respect it. A domain's contracts change occasionally and only tasks touching that domain need them. A specific operation's edge cases change often and only a task touching that exact operation needs them. Handing an agent all three, undifferentiated, at every distance, is not generosity. It is asking a reader to find one relevant paragraph in a phone book with no headings, and blaming the reader when a wrong page gets edited.

Meridian's fix is not a shorter document. It is a structure with levels, so that a task like this one can be told, precisely, which level to read and which to leave alone.

## 7.1 The concentric levels

The three levels nest, and the nesting mirrors Clean Architecture's own concentric circles for a reason: dependencies in a codebase point inward, from infrastructure toward the domain core, and the specifications describing that codebase point inward too, from broad and stable at the outside toward narrow and volatile at the center.

```
   +-----------------------------------------------+
   | Level 0: Domain Boundaries & Architecture      |
   |  +-------------------------------------------+ |
   |  | Level 1: I/O Contracts & Data Model        | |
   |  |  +---------------------------------------+ | |
   |  |  | Level 2: State Rules & Edge Cases      | | |
   |  |  +---------------------------------------+ | |
   |  +-------------------------------------------+ |
   +-----------------------------------------------+
```

Level 0 is the outermost ring and the one that changes least: it says what the system's boundaries are and which direction dependencies are allowed to point, and it is true for every module in the repository at once. Level 1 sits inside it and says what data crosses the boundaries of one particular component, in what shape, with what failures — true for one module, changing when that module's contracts change. Level 2 is the innermost ring and says exactly how one operation in that module behaves under every combination of its inputs — true for one operation, changing whenever the business adds a rule.

The nesting is not decorative. It fixes what a task needs to read as a function of what the task touches, which is the property the opening scenario's agent was missing entirely. A task that adds a new module respects Level 0 and writes new Level 1 and Level 2 documents. A task that adds a field to an existing contract reads Level 0 for the constraints it must not violate and Level 1 for the module it is changing, and has no business anywhere near another module's Level 2. A task that adds one edge case, like the fraud-suspension behavior in the opening scenario, reads Level 0 once, confirms it is not violating a boundary, and then lives entirely inside one operation's Level 2 — which is the whole document this chapter's engineer actually needed, buried inside the four hundred pages the agent was handed instead.

The three levels also change at three different rates, and the rate is a second, independent reason the nesting matters. `SPEC-ARCH-000` might be revised twice a year, when the platform adds a new bounded context or changes a technology constraint that touches every service. A module's Level 1 contract changes when the module gains or loses a field, an error code, or a dependency — a handful of times a quarter for an actively developed domain. A single operation's Level 2 decision table can change every sprint, because edge cases are where product decisions actually land. Collapsing all three into one document forces the slowest-changing material to be re-reviewed every time the fastest-changing material is touched, which is its own tax on a team even before an agent enters the picture: a reviewer approving a one-row change to a decision table should not have to re-read the platform's dependency rule to do it, and in a properly leveled specification, they never have to.

### Reading outward from a task

A short example fixes the reading direction before the chapter builds out what each level actually contains. Suppose a task adds a new optional `memo` field to a withdrawal request. Reading outward from that task: Level 2 changes, because a new field may interact with existing rules — does a memo affect fraud scoring? Level 1 changes, because the field appears in the operation's input contract and, if it is free text, needs a length bound and a character-set constraint stated the same way `Money` and `EmailAddress` are constrained elsewhere in the document. Level 0 does not change at all, because adding a field to one operation's contract crosses no architectural boundary — and a task that does not touch Level 0 should never need to open `SPEC-ARCH-000` for anything beyond the single confirming glance that nothing about the change violates the dependency rule. The habit of asking, for any task, "which of the three levels does this actually move" is the whole discipline of this chapter compressed into one question.

## 7.2 Level 0: architecture and boundaries

Level 0 is the specification of the system as a system, and it exists once per repository, not once per module. It states the dependency rule and the boundaries the rule creates, and every other specification in the repository operates inside the constraints it sets without restating them.

### SPEC-ARCH-000: Meridian Platform Architecture (Level 0)

#### 1. Dependency Rule

- N-1: Source code dependencies **MUST** point only inward, from infrastructure toward the domain core; a domain entity or use case **MUST NOT** import a database driver, a web framework, or a third-party SDK.
- N-2: A domain layer **MUST** depend only on abstractions it defines itself — ports — and **MUST NOT** depend on any concrete adapter that implements one.

#### 2. Allowed Components per Layer

| Layer | Permitted contents | Forbidden contents |
| :--- | :--- | :--- |
| Domain | Entities, value objects, use cases, port definitions | Database clients, HTTP clients, framework decorators |
| Application | Use case orchestration, port composition | Direct SQL, direct HTTP calls |
| Adapters | Port implementations (Postgres repository, Stripe client, SMTP sender) | Business rules, invariant checks |

#### 3. Technology Constraints

- N-3: Domain and application code **MUST** be typed and **MUST** pass strict static type checking (`mypy --strict` for Python services, `tsc --strict` for TypeScript services) as a required CI gate.
- N-4: Money **MUST NOT** be represented as a floating-point type anywhere in the domain or application layers.

Notice what this document does not contain. It says nothing about withdrawals, notifications, or subscriptions, because none of those are architecture; they are Level 1 and Level 2 concerns living in their own modules. It says nothing about which cloud provider hosts the database, because that is an adapter's business, several layers removed from anything a domain use case is allowed to know about. Level 0 is short on purpose — this excerpt is nearly the whole document — because its job is to be the one thing every task reads regardless of what it touches, and a document everyone must read on every task has to earn its place in every context window it occupies.

## 7.3 Level 1: contracts and data model

Level 1 belongs to one module, and it says precisely what crosses that module's boundary: the shape of its inputs and outputs, and the full catalog of ways an operation can fail. Two disciplines make a Level 1 document worth reading instead of merely worth having.

The first is value objects over primitives. A Level 1 data model never passes a currency amount as a bare `int` or `float`, an email address as a bare `str`, or a country as a two-letter code with no validation attached. Each becomes a named type — `Money`, `EmailAddress`, `ISOCountryCode` — whose constructor is the enforcement mechanism for the invariants a primitive cannot carry. This is Chapter 3's rule about checkable preconditions taken one level up: a `Money` value object that cannot be constructed with a negative amount makes an entire family of bugs impossible before any function body runs, rather than merely caught by a validation branch someone has to remember to write. Chapter 8 develops the substitution reasoning behind this choice in full; here it is enough to say that a primitive-typed contract is a contract with holes in it, because nothing stops a caller from passing a string that happens to compile but is not, in fact, an email address.

The second discipline is the Failure Modes Matrix, and it exists because a contract that states only the success case is half a contract. Every operation a module exposes maps the complete, enumerated set of ways it can fail — not "may throw an exception," but which exception, under which condition, with which caller-visible consequence.

| Error Condition | Category | Domain Code | HTTP Status / RPC Code | Required Action |
| :--- | :--- | :--- | :--- | :--- |
| Source account does not exist | Business Error | `SRC_ACC_NOT_FOUND` | 404 Not Found | Terminate the flow |
| Insufficient balance | Business Error | `INSUFFICIENT_FUNDS` | 422 Unprocessable Entity | Reject the transaction |
| Persistence timeout | Infra Error | `PERSISTENCE_TIMEOUT` | 504 Gateway Timeout | Exponential retry |
| Payload does not conform to schema | Contract Error | `MALFORMED_PAYLOAD` | 400 Bad Request | Reject with detail |

Building one is mechanical once the habit is in place. Walk every dependency the operation touches — the database, an external gateway, a message queue — and ask what happens when each one is unavailable, slow, or returns something unexpected; that produces the infra-error rows. Walk every business rule the operation enforces and ask what happens when a caller violates each one; that produces the business-error rows. Walk the operation's own input contract and ask what happens when a caller sends something the schema from Chapter 6 rejects; that produces the contract-error rows. A matrix built this way is closed by construction — every row traces back to something enumerable — rather than open-ended and hoping a reviewer thinks of the missing case, which Chapter 10 turns into the direct source of one contract test per row.

The category column earns its keep beyond bookkeeping. A Business Error means the caller did something the domain forbids, and the correct response is almost always to reject cleanly and tell the caller why. An Infra Error means a dependency the operation needs is unavailable right now, and the correct response is almost always to retry, because the request itself was legitimate. A Contract Error means the caller's request was malformed before the operation's own logic ever ran, and the correct response is to reject with enough detail that the caller can fix the request without guessing. Collapsing all three into one undifferentiated "error" bucket, which is what a bare `try/except` in generated code defaults to when nothing tells it otherwise, throws away exactly the distinction a caller needs to decide whether to retry, alert a human, or give up — and it is the single most common way the Handwave smell that Chapter 13 catalogs shows up in a contract nobody thought was vague.

## 7.4 Level 2: state rules and edge cases

Level 2 belongs to one operation, and it is where the most common failure in informal specifications lives: entrusting a sequence of conditions and their interactions to a paragraph of prose. "If the balance covers it and the daily limit isn't exceeded, approve the withdrawal, unless fraud detection flags it, in which case hold it for review" is exactly the shape of sentence Chapter 5 spent a chapter warning about — a chain of conditionals that reads as clear and hides at least one combination nobody thought through, usually the one where two conditions conflict.

A decision table replaces the chain with an exhaustive grid. Here is the one that governs the withdrawal from Chapter 3, now given in full as part of `SPEC-ACCT-003`.

### SPEC-ACCT-003: Withdrawal Authorization

#### 6. Decision Table: Withdrawal Authorization

| Rule | Balance Available ≥ Requested | Daily Limit Respected | Fraud Signal = LOW | Outcome | Side Effect |
| :--- | :---: | :---: | :---: | :--- | :--- |
| R1 | Yes | Yes | Yes | `APPROVED` | Decrement balance; emit `WithdrawalSettled` event |
| R2 | No | Any | Any | `REJECTED` | Return error `INSUFFICIENT_FUNDS` |
| R3 | Yes | No | Any | `REJECTED` | Return error `DAILY_LIMIT_EXCEEDED` |
| R4 | Yes | Yes | No | `SUSPENDED` | Forward to compliance queue; no balance change |

Notice that this table reuses `INSUFFICIENT_FUNDS` and `DAILY_LIMIT_EXCEEDED` verbatim from the errors Chapter 3 named for this same operation — a decision table does not invent a new vocabulary of outcomes, it arranges the vocabulary the contract already declared, which is exactly why the two sections cannot silently drift apart the way two independently maintained prose descriptions can.

A decision table earns its place over prose because it can be checked for two properties a paragraph cannot be checked for at all. **Completeness** asks whether every combination of conditions has a row: three boolean-ish conditions with a small number of outcomes each define a finite grid, and a reviewer — or a linter — can walk it mechanically and ask whether any combination falls through with no matching rule. **Consistency** asks whether any two rows contradict each other for the same combination of conditions: R2 uses "Any" for the last two columns because an insufficient balance overrides every other consideration, and stating that explicitly, as a wildcard, is what prevents a reader from wondering whether a low fraud signal could somehow rescue an overdrawn withdrawal. Both checks are exactly the kind of question 7.3's Failure Matrix and this table share: walk every combination that could occur, and either give it a row or explain, in the table itself, why the row is subsumed by a wildcard in an earlier one.

The order of the rules matters and should always be stated as a rule of its own rather than left to be inferred from row position: here, evaluation proceeds top to bottom and the first matching rule wins, which is why R2's balance check is checked before R4's fraud check even though fraud detection might reasonably run first in an implementation. The specification is not describing execution order; it is describing precedence among outcomes, and conflating the two is a common way a decision table quietly becomes ambiguous again.

It is worth working through what the prose version of this table actually hid, because the comparison is the whole argument for the format. The sentence at the start of this section says nothing about what happens when the balance is sufficient, the daily limit is respected, and the fraud signal is not LOW — which is exactly R4, and exactly the case the engineer in the opening scenario was trying to add. A reader skimming the prose fills that gap the way Chapter 5 predicted: by assuming the nearest analogous case applies, which here would wrongly suggest an outright rejection rather than a hold for review. The decision table does not merely describe R4 more clearly than the prose did. It is the only one of the two forms in which R4's absence would have been visible as a gap before anyone shipped code that guessed.

A decision table also degrades gracefully as the business adds conditions, which prose does not. Adding a fourth boolean condition to the withdrawal rule — say, whether the account is jointly held — means adding a column and working out which existing rows need to split into two, a mechanical exercise with a checkable outcome: the table either still covers every combination or it visibly does not. Adding the same condition to a paragraph means rewriting the paragraph and trusting that the rewrite is still exhaustive, which is precisely the trust Chapter 5's taxonomy argued natural language cannot support once a sentence is doing more than one job.

## 7.5 How the levels reference each other

The three levels are not independent documents that happen to share a repository. Level 2 cites the error codes Level 1 declared, as the withdrawal decision table just did. Level 1 operates inside the boundaries Level 0 set, never importing a concrete adapter, never representing money as a float. And nothing at any level restates what an outer level already said — the decision table does not repeat that money is represented as integer cents, because that is `SPEC-ARCH-000`'s business, cited by reference rather than duplicated by habit.

This is what answers the opening scenario's actual question: what should an agent read for a given task? The rule is to read outward from the operation the task touches, not inward from the top of the tree. A task confined to one operation's edge cases — the fraud-suspension behavior the engineer wanted — reads that operation's Level 2 document in full, its module's Level 1 document for the error vocabulary and data shapes it is allowed to use, and `SPEC-ARCH-000` once, briefly, to confirm the change does not cross a boundary it should not. It does not read Billing's contracts, Ledger's state machines, or Checkout's decision tables, because none of them constrain an operation inside Accounts, and an agent that reads them anyway is exposed to exactly the failure mode from the opening scenario: material with no bearing on the task, sitting in context, available to be misapplied.

Chapter 11 turns this reading rule into a concrete context budget — what an agent instruction file should load for a given class of task, and what it should leave on disk unless asked for. The three levels are what make that budget possible to write down at all: without them, "read what's relevant" has no mechanical definition, because relevance was never structural, only a property a human happened to hold in their head while skimming. With them, relevance is a function of which level a task's boundary sits at, and an agent — or a reviewer — can compute it without having read all four hundred pages first.

Rerun the opening scenario with the levels in place and the failure disappears without anyone having to trust the agent to exercise better judgment. The fraud-suspension task declares, in its own ticket, that it touches `specs/modules/accounts/withdrawal.md` — the file holding `SPEC-ACCT-003` — and nothing else. The agent instruction file's routing rule, which Chapter 11 writes out in full, resolves that declaration to exactly three reads: `SPEC-ARCH-000` for the boundary check, the Accounts module's Level 1 document for its error vocabulary, and the withdrawal operation's Level 2 decision table, where the new `SUSPENDED` outcome actually belongs. Billing's contracts never enter context, so there is nothing left for the agent to misapply a naming convention from, and the diff that comes back touches one file: the decision table this chapter just finished building.

## Key Takeaways

- A specification is not one document but three nested levels: Level 0 architecture and boundaries, Level 1 contracts and data model, Level 2 state rules and edge cases, each answering a question at a different distance from any given task.
- Level 0, `SPEC-ARCH-000`, states the dependency rule and the allowed contents of each architectural layer, is true for the whole repository at once, and stays short because every task reads it.
- Level 1 replaces primitive types with value objects so invariants are enforced by construction, and pairs every operation with a Failure Modes Matrix built by walking its dependencies, its business rules, and its input contract systematically rather than by guessing.
- Level 2 replaces conditional prose with a decision table, which can be checked for completeness — every combination has a row — and consistency — no two rows contradict each other — in a way a paragraph cannot be checked at all.
- A decision table cites the error vocabulary its module's Level 1 document already declared rather than inventing new outcome names, and it states its evaluation order explicitly rather than leaving precedence to be inferred from row position.
- The levels reference each other outward — Level 2 cites Level 1's codes, Level 1 respects Level 0's boundaries — and nothing at an inner level restates what an outer level already settled.
- An agent, or a reviewer, should read outward from the operation a task touches: that operation's Level 2, its module's Level 1, and Level 0 once for boundary confirmation — never every level of every module regardless of what the task actually changes.
