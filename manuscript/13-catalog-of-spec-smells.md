# Chapter 13: A Catalog of Spec Smells

Picture a spec review at Meridian where five engineers sit with a draft on the shared screen and every one of them feels, within the first few minutes, that something about the document is wrong. Nobody can say what. The prose reads fine sentence by sentence. The headings are in the right order. One reviewer flags a paragraph as "kind of vague" and cannot say vague how. Another says the state transitions "feel like they're missing something" and cannot point at the missing piece. A third says nothing at all, unable to distinguish the specific unease from ordinary review fatigue. The meeting ends with two cosmetic comments, an approval, and a specification that ships with the exact defect nobody had a name for.

Three weeks later, that defect is a production incident, and the retrospective identifies it in about ninety seconds, because a concrete failure is always easier to name than a vague feeling about a document that has not failed yet. The frustrating part is that every reviewer in that meeting had, in fact, correctly sensed the problem. What they lacked was not judgment. It was vocabulary — a name specific enough to turn "something feels off" into "this is the fourth time this file has changed for an unrelated reason this month," which is a sentence a team can act on in the room, before the deploy, rather than a feeling nobody trusts enough to block a merge over.

Martin Fowler and Kent Beck gave object-oriented code that vocabulary decades ago, under the name code smells: not bugs, but symptoms correlated strongly enough with future bugs and future maintenance pain that naming one earns an engineer the right to stop and ask a question before approving a change. A specification written for a coding agent develops its own recurring pathologies, different in shape from a code smell because the failure mode is different — an ambiguity here does not throw a runtime exception, it gets silently resolved by a generator sampling from a prior, exactly as Chapter 5 described. This chapter catalogs eleven of them. Each entry states the symptom, gives a concrete example, names the consequence, and points to its cure — a specific refactoring Chapter 14 develops in full. The catalog will not make a bad specification pass review by itself. It will make the five engineers in that opening meeting able to say, out loud, exactly which of eleven things they were each independently reacting to.

## 13.1 The Omniprompt

**Symptom.** A single specification file, often thousands of lines long, that states architectural rules, database configuration, UI copy, form validation, and deployment steps together, with no boundary between them.

**Example.** `checkout-core.md` from Chapter 8: two thousand one hundred lines covering registration validation, payment gateway fees, shipping rates, fraud thresholds, and button copy, all under one heading because all of them, at some point, touched checkout.

**Consequence.** An agent reading the whole document for a narrow task inherits Chapter 2's lost-in-the-middle effect at document scale: constraints in the center of an oversized file compete for attention with hundreds of lines that have nothing to do with the task, and the agent's output starts drawing on material nobody intended it to read, the way Chapter 8's agent picked up a fraud threshold while implementing a fee change.

**Cure.** Extract Bounded Context Spec (Chapter 14), the refactoring that walks a monolithic document apart along its actual reasons to change, restoring the Single Responsibility Spec principle from Chapter 8.

The Omniprompt is usually easy to spot from the outside and hard to fix from the inside, because nobody adds two thousand lines in one sitting. It accretes a paragraph at a time, each addition locally reasonable — "this is the file that's already open," "this is close enough to checkout to belong here" — until the document's table of contents is the only remaining evidence that five unrelated concerns ever agreed to share a heading.

## 13.2 The Handwave

**Symptom.** High-gradient, unquantified language standing in for a testable requirement: "handle errors robustly and gracefully," "the interface must be fast, intuitive, and responsive," "make sure the system scales well under load."

**Example.** A performance requirement written as "the checkout page should feel snappy even during a flash sale," with no number anywhere near it.

**Consequence.** An agent facing a Handwave inserts an empty `try/except`, hallucinates a generic error message, or ignores concurrency altogether, because "robust" and "snappy" have no formal referent to synthesize code against — Chapter 5's argument about unquantified adjectives, restated as a symptom with a name.

**Cure.** Introduce Failure Matrix (Chapter 14), replacing discursive language with a deterministic table of named error conditions and, where the Handwave was really a performance claim, a formalized budget in milliseconds or asymptotic complexity.

The tell that distinguishes a Handwave from an honestly open question is whether the author actually knows the answer and simply reached for a comfortable adjective instead of writing it down. Most Handwaves are not gaps in the business's knowledge; they are gaps in the document, and the fix is rarely research — it is asking the person who wrote "robust" what they actually meant, in front of the room, and writing that answer down instead.

## 13.3 Syntactic Micromanagement

**Symptom.** The specification tells the agent how to write the code, line by line, instead of what the code must guarantee: "declare a variable `i = 0`, loop over the array, and place each element into a dictionary keyed by `id`."

**Example.** A Level 2 document that specifies a `for` loop and an accumulator variable for a deduplication step, rather than stating that the output must contain no two entries with the same identifier.

**Consequence.** The agent is denied every idiomatic construct, every vectorized library call, and every asymptotically better algorithm a language actually offers, because the specification has descended to the level of code and lost its function as an abstraction — Chapter 3's substitution rule cannot even apply, because there is nothing left for an implementation to be freer than.

**Cure.** Replace Procedure with Postcondition (Chapter 14): state the guaranteed effect, per Chapter 3's postcondition discipline, and leave the mechanism to the generator.

This smell tends to appear in specifications written by engineers who came to the discipline from code review rather than from requirements work, because the habit of thinking in procedures is exactly the habit years of writing implementations builds. The tell is a clause that would need to change if the target language changed — a Python-flavored dictionary comprehension described in prose is not a requirement that happens to be written procedurally, it is an implementation wearing the specification's clothes, and Chapter 3 already gave the test for telling the two apart.

## 13.4 Domain Leakage

**Symptom.** Pure business logic mixed with transport or persistence detail inside the same normative sentence.

**Example.** Chapter 8 already showed the canonical case: an early draft of `SPEC-BILL-017` instructing the use case to "save the result into the Postgres `tax_records` table with an UPSERT query," naming a database and a SQL verb inside a document whose job was to state a tax rule.

**Consequence.** The business rule becomes impossible to reuse from a CLI tool, a batch worker, or a different persistence technology, and it becomes fragile to any infrastructure change even though nothing about the rule itself changed — the reuse failure Chapter 8 already worked through in detail.

**Cure.** Invert Infrastructure Dependency (Chapter 14), the mechanical application of Dependency Inversion Spec that replaces a named database call with a call to a port the domain layer defines.

Domain Leakage is the smell most likely to pass an ordinary review unremarked, because the leaked sentence is usually precise, confident, and entirely correct about the infrastructure it names — a reviewer checking for ambiguity, in Chapter 5's sense, finds none, since "UPSERT into `tax_records`" is about as unambiguous as a sentence gets. The defect is not imprecision; it is misplaced precision, precision about the wrong layer, and it takes the specific question Chapter 8 gave — would this clause survive a persistence migration — to surface it at all.

## 13.5 Happy Path Only

**Symptom.** A specification that narrates only the success flow and never mentions what happens when anything goes wrong — not vaguely, as the Handwave does, but not at all.

**Example.** A checkout specification stating "the customer enters payment details, the order confirms, and a receipt is sent," with no sentence anywhere addressing a declined card, a network timeout, or a partially fulfilled order.

**Consequence.** The failure paths are, statistically, where a production system spends much of its behavior, and an agent with no stated guidance for them invents its own handling on the spot, differently on every regeneration, which is Chapter 4's argument about an unwritten contract restated for an entire operation rather than one clause of it.

**Cure.** Introduce Failure Matrix (Chapter 14) — the same refactoring that cures the Handwave, because both smells leave an agent with no formal failure vocabulary to implement against, whether the vocabulary was vague or simply absent.

## 13.6 Ghost Invariant

**Symptom.** An invariant stated once, clearly, in the specification everyone reads, and enforced by no test anywhere in the suite.

**Example.** Chapter 8's `PaymentGatewayPort`, whose `I-1` requires every adapter to deduplicate a charge within a sixty-second idempotency window, with no conformance test run against Stripe, Adyen, or the CI test double to confirm any of the three actually does.

**Consequence.** The specification and the team both believe the system has a property it does not verifiably have, which Chapter 3 already named worse than having no stated invariant at all, because the false confidence suppresses the very scrutiny that would have caught the gap.

**Cure.** Normalize Modal Verbs (Chapter 14). Many ghost invariants begin as a `MUST` in the abstract port and quietly become a `SHOULD` somewhere in an adapter's own restatement of the rule, and it is the weakened modal that lets an implementer treat the obligation as negotiable. Forcing every restatement back to the same uppercase keyword the invariant actually requires surfaces the question a `SHOULD` lets slide: if this is genuinely non-negotiable, where is the test that fails when it is violated?

Not every Ghost Invariant announces itself through a weakened modal, and it is worth naming the quieter variant too. Some are simply never restated anywhere an implementer would see them while writing an adapter — the invariant lives in the abstract port's document and nowhere else, and an engineer implementing a third adapter six months later never opens that file at all. Normalizing the modal verb only helps once the invariant is at least visible; the prerequisite, which Chapter 11's context budgeting already assumes, is that every adapter task actually loads the port's specification before Execute begins.

## 13.7 Prose State Machine

**Symptom.** A sequence of state transitions described as a paragraph of conditional prose rather than a table or diagram.

**Example.** "When an order is created, it is pending. If payment arrives, it becomes paid and is shipped. If payment fails, it is cancelled. The customer can cancel it only if it has not yet shipped, but if it has already been paid, a refund must be issued instead."

**Consequence.** Asynchronous flows described this way produce dead branches and hallucinated exception paths almost without exception, because a reader — human or agent — has to hold every transition in their head simultaneously to notice a missing one, and prose serializes what a state machine is inherently parallel.

**Cure.** Replace Prose with State Table (Chapter 14), turning exactly this paragraph into `SPEC-ORD-007`'s state transition table, `FSM-ORD-01`, which Chapter 14 builds in full from this same example.

Read the paragraph above once more and count the states it actually implies: pending, paid, shipped, cancelled, and — unstated but logically required by the last sentence — a refunding state between a paid cancellation and whatever comes after it. The prose never says that fifth state's name, because prose does not have to declare its states before using them, which is exactly the property that lets a state machine go missing from a specification while every individual sentence in it reads as complete.

## 13.8 Example as Specification

**Symptom.** A requirement stated only as one or a few worked examples, with no general rule anywhere in the document.

**Example.** Chapter 10's opening scenario in full: a discount requirement given as "a hundred-dollar cart with a ten-percent code should total ninety dollars," and nothing else.

**Consequence.** A generator satisfies the example with a hardcoded special case exactly as readily as with a correct general rule, because a single input-output pair does not distinguish between the two — the failure mode Chapter 10 built an entire chapter's argument for property-based testing around.

**Cure.** Extract Invariant from Examples (Chapter 14), the refactoring that takes the worked example and derives the universal property it was always gesturing at — here, that a discount never exceeds the subtotal and a final price is never negative — so the specification states the rule instead of one instance of it.

This smell is deceptive because an example is genuinely useful — Chapter 10 kept the ninety-dollar cart in the suite as a regression test even after the property test took over the load-bearing work. The defect is not the presence of an example; it is the absence of anything beside it. A document with one worked case and a general rule is well specified. A document with only the worked case has mistaken an illustration for the thing it was supposed to illustrate.

## 13.9 Modal Mush

**Symptom.** An interface so large and undifferentiated that a reader cannot tell which of its discretionary, `MAY`-level features apply to the role actually in front of them.

**Example.** Chapter 8's fifty-endpoint platform schema, handed whole to an agent implementing one Billing endpoint, in which optional fields that make sense for Checkout or Identity sit alongside Billing's own and invite an agent to stretch them by analogy into a domain they were never scoped for.

**Consequence.** Modal strength stops meaning anything reliable, because the same `MAY` reads as one thing in the domain it was written for and as an ambiguous invitation in every domain it merely sits near in context — a schema-scale version of the modal-verb misuses Chapter 5 catalogued at the sentence level.

**Cure.** Split Role-Specific View (Chapter 14), segmenting the monolithic interface into scoped views so a reader — or an agent — only ever sees the discretionary surface that actually applies to their role.

Modal Mush is easy to mistake for the Handwave, because both leave a reader uncertain what is actually required, but the mechanism is different enough to matter. A Handwave is imprecise on its own terms — the sentence itself is vague no matter who reads it. Modal Mush is precise in isolation and becomes ambiguous only in context, when a genuinely well-scoped `MAY` sits close enough to fifty unrelated ones that a reader — or a model — can no longer tell which domain's discretion it was actually describing.

## 13.10 Primitive Obsession

**Symptom.** A data model built from bare primitives — an unadorned `float` for money, a raw `string` for an email address, an unchecked two-letter string for a country — where a value object belongs instead.

**Example.** A withdrawal amount typed as a plain `float`, which both permits a value like `-50.0` to pass type-checking and reopens the exact floating-point rounding risk `SPEC-CORE-001` will strictly forbid in Chapter 15.

**Consequence.** Every invariant a value object would have enforced at construction — positivity, currency validity, a well-formed address — instead becomes a runtime check someone has to remember to write and a caller has to remember to trust, which is Chapter 7's Level 1 discipline violated at its most basic level.

**Cure.** Replace Primitive with Value Object (Chapter 14), the direct construction-time fix Chapter 3 already previewed when it argued that a precondition enforced by a constructor is stronger than one enforced by a validation branch.

The test for this smell is almost mechanical, which is what makes it one of the fastest to catch in a review: for every field in a Data Model section, ask whether an obviously invalid value of the declared primitive type would still pass the type checker. A `float` accepts a negative balance. A bare `string` accepts `"not-an-email"`. A two-character `string` accepts `"ZZ"`, which is syntactically a country code and not a real one. Every yes to that question is a value object that has not been written yet.

## 13.11 Zombie Spec

**Symptom.** A specification that still exists in the repository, still carries a `status` of `active`, and no longer describes what the code actually does — and, crucially, that nobody on the team trusts enough to read before making a change.

**Example.** `SPEC-ACCT-003` at the moment just before Chapter 12's on-call engineer's fix: nothing wrong with the document on its face, and already quietly out of step with production behavior around a boundary condition the document had never addressed.

**Consequence.** An agent asked to regenerate against a Zombie Spec reproduces the stale document faithfully, silently reintroducing behavior a human already fixed by hand — exactly Chapter 12's opening incident, replayed a month later on an unrelated ticket.

**Cure.** Extract Bounded Context Spec (Chapter 14) resurrects a zombie by carving a small, currently accurate document out of whatever the team can still verify against production, rather than trying to rehabilitate the whole stale file at once; Chapter 12's reverse-drift procedure is what keeps a freshly resurrected document from decaying the same way twice.

A Zombie Spec is the one smell in this catalog that a spec review, on its own, is structurally unable to catch, because the document being reviewed is not the one that is wrong — the disagreement lives between the document and a production system nobody is comparing it against in the room. Detecting a Zombie Spec is Chapter 12's job, not this chapter's: the drift-detection tooling that checks a specification against running behavior is the only mechanism with visibility into both sides of the gap at once.

## Summary

| Smell | Detection question | Refactoring |
| :--- | :--- | :--- |
| The Omniprompt | Does this file have more than one reason to change? | Extract Bounded Context Spec |
| The Handwave | Could two competent engineers implement this sentence differently and both be right? | Introduce Failure Matrix |
| Syntactic Micromanagement | Does this clause name a variable, a loop, or an algorithm instead of an outcome? | Replace Procedure with Postcondition |
| Domain Leakage | Would this clause survive swapping the database or the framework? | Invert Infrastructure Dependency |
| Happy Path Only | Does this document say anything about what happens when something goes wrong? | Introduce Failure Matrix |
| Ghost Invariant | Does every invariant have a test that fails the moment it is violated? | Normalize Modal Verbs |
| Prose State Machine | Can every state and transition be listed without a second read of the paragraph? | Replace Prose with State Table |
| Example as Specification | Is there a general rule here, or only worked examples? | Extract Invariant from Examples |
| Modal Mush | Is every `MAY` and `SHOULD` here actually scoped to the reader in front of it? | Split Role-Specific View |
| Primitive Obsession | Could this field hold an invalid value and still pass type-checking? | Replace Primitive with Value Object |
| Zombie Spec | Would anyone notice if this document silently disappeared? | Extract Bounded Context Spec |

Eleven questions, each short enough to ask out loud in the middle of a review without derailing it, which is the entire test a smell has to pass to earn its place in this catalog: if naming it does not fit in the time it takes to raise a hand, it is not doing the job a smell is supposed to do.

## Key Takeaways

- A spec smell is not a bug; it is a symptom correlated strongly enough with future failure that naming it earns the right to ask a question before a document ships, the same relationship Fowler and Beck established for code smells decades earlier.
- The Omniprompt and Zombie Spec both cure through Extract Bounded Context Spec, because both are, at root, a document that grew past the boundary of what one team can honestly stay accountable for.
- The Handwave and Happy Path Only both cure through Introduce Failure Matrix, because vague failure language and absent failure language leave an agent with the identical lack of formal vocabulary to implement against.
- Syntactic Micromanagement and Primitive Obsession are opposite failures of abstraction — one over-specifies mechanism, the other under-specifies data — and each has its own dedicated Chapter 14 refactoring rather than a shared one.
- A Ghost Invariant is more dangerous than an absent one, because it produces false confidence; the cure starts by normalizing every restatement of the rule to the same modal strength the original invariant actually demands.
- Modal Mush is Interface Segregation's failure mode at the level of RFC 2119 vocabulary: a discretionary `MAY` stops meaning anything reliable once it sits in an undifferentiated interface a reader cannot scope to their own role.
- Every smell in this catalog reduces to the same underlying question this book has asked since Chapter 5: does this document leave a decision to be resolved by inference, and if so, whose job was it actually to make that decision explicit?
