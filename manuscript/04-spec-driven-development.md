# Chapter 4: Spec-Driven Development: Inverting the Flow

Imagine Meridian launches a promotions program and hands the same requirement to two teams: a customer applies a promo code, and the discount comes off the total the same way at the web till and at a subscription renewal. Checkout owns the first surface, Billing owns the second. Neither team sets out to run an experiment; each works the way it already works.

Checkout starts on Monday. An engineer opens a coding agent, pastes the ticket, and iterates. By Wednesday there is a working endpoint, a percentage discount, and a demo. Product then asks about fixed-amount codes, stacking, expiry, and refunds on a discounted order. Each answer is another conversation and another green build.

Billing starts on Monday by not writing code. Two engineers spend a day and a half on a document: types for a code and a discount, the invariant that a discounted total never drops below zero, a decision table for stacking, a failure matrix with six named errors, and the open question of what a refund returns. They take the stacking question to product, who changes their mind twice before lunch. On Wednesday they hand the document to an agent, which writes tests first and code second. Billing's feature works by Friday, two days behind.

Week six separates the two stories, on three numbers.

Change lead time. A new rule says that loyalty-campaign codes never stack with seasonal codes. Billing amends one row of the decision table, regenerates, and watches the gates go green in under two hours. Checkout spends a day and a half, most of it discovering where the current stacking behavior is decided.

Regressions. Checkout has shipped four corrective releases, each of which broke something else; the fourth reintroduced the bug the first one fixed. Billing has shipped one regression, caught before merge by a property test derived from the zero-floor invariant.

Onboarding. A new engineer joins the on-call rotation for both surfaces. For Billing they read a 240-line document and can say, on day one, what happens when an expired code is applied to an order that was later refunded. For Checkout they read three thousand lines of generated code and a closed ticket, then hunt for the engineer who ran the original session, who has moved to Inventory.

Nobody on Checkout was careless. The two teams simply disagreed, without ever discussing it, about which artifact they were producing.

## 4.1 From TDD to SDD

**Spec-Driven Development (SDD)** is not an accessory evolution of Test-Driven Development. It is what TDD was reaching for, finished off under conditions TDD never had to face. In human TDD, the engineer writes a failing test to clarify the requirement to themselves, then writes the code that satisfies it. Both halves are authored by the same person, minutes apart, and the clarification happens in that person's head. In SDD the engineer writes a structured specification, the specification determines the tests, and an agent synthesizes the code that must satisfy both.

The shift is easiest to see by laying four methods side by side. The table below names who authors each of the three artifacts under each method, and which artifact a team treats as authoritative when two of them disagree.

| Method | Who writes the requirements | Who writes the tests | Who writes the code | Source of truth |
| :--- | :--- | :--- | :--- | :--- |
| Waterfall | Analyst, up front, in prose | A separate QA group, after the code exists | Developers | The requirements document, until the code overtakes it |
| Agile | Product owner, as user stories | Developers, alongside or after the code | Developers | The running code, plus the team's shared memory |
| TDD | Product owner, as user stories | The developer, before the code | The same developer | The test suite |
| SDD | The engineer, as a specification | Derived from the specification, transcribed by an agent, reviewed by a human | A coding agent | The specification |

Read the last column downward, because that is the column the whole book is about. Waterfall had the right idea about authority and the wrong idea about timing: it wrote the authoritative document once, before anyone had learned anything, and then let the code drift away from it for two years. Agile fixed the timing by abandoning the document, and the price it paid was that "the source of truth is the code" means nobody can state a guarantee without reading an implementation. TDD made an artifact that actually was maintained in step with the code, which is a real advance and the reason TDD worked.

So why not stop at TDD? Because a test suite is a poor source of truth, for two reasons that have nothing to do with discipline. First, tests are examples, and examples under-determine behavior. A hundred assertions about a discount engine tell you what happens at a hundred points and say nothing about the space between them, which is where Chapter 3's quantified invariant lives. Second, a test suite is not reviewable as a statement of intent. You cannot hand four hundred test functions to a product manager and ask whether the stacking rule is right. The thing a human needs to argue with and the thing a machine needs to check are not the same artifact, and TDD only ever produced the second one.

There is a third reason, specific to this era. TDD assumed that the person writing the test and the person writing the code shared a mind. When the code is written by a nondeterministic compiler, as Chapter 1 named it, that assumption is gone. The tests no longer clarify the requirement to the author of the code, because the author of the code has no memory of yesterday and no access to the hallway. Everything the implementer needs to know must exist in the document, in a form that survives being read by a stranger. That is a specification, and it is why the inversion in this chapter is not optional.

Notice what SDD does not invert. It does not move work from humans to machines; it moves human work upstream. Under TDD, a team spends its thinking on how to make the code testable. Under SDD, it spends the same thinking on what must be true, and gets the testability as a consequence, because a numbered contract is already a test plan waiting to be transcribed.

## 4.2 The SDD pipeline

The method has a shape, and the shape is worth drawing before arguing about it. One document at the top, two derivations from it, one deterministic judgment, and two exits.

```
       +-------------------------------------------------------+
       |              CLEAN SPEC  (author: human)              |
       |   types, invariants, state machines, contracts,       |
       |   RFC 2119 normative statements                       |
       +-------------------------------------------------------+
                                  |
            +---------------------+---------------------+
            v                                           v
+-----------------------+                   +-----------------------+
|  Property tests and   |                   |  Application code     |
|  contract tests       |                   |  synthesis            |
|  (derived, reviewed)  |                   |  (coding agent)       |
+-----------------------+                   +-----------------------+
            |                                           |
            +---------------------+---------------------+
                                  v
                    +---------------------------+
                    |  Deterministic execution  |
                    |  and validation           |
                    |  (CI: lint, types, tests) |
                    +---------------------------+
                                  |
                  [failure]       |       [success]
                       +----------+----------+
                       v                     v
             Amend the spec, then        Commit and
             re-run the agent            deploy
             (correction loop)
```

The top box is the only one a human authors by hand, and everything about its contents has been argued for in the first three chapters. Types and value objects remove whole families of representation mistakes. Invariants constrain states that nobody has enumerated. Contracts say what a caller may assume and what an operation owes. State machines close the transitions that prose leaves open. RFC 2119 keywords, which Chapter 5 takes apart in detail, distinguish an obligation from a preference so that a reader and an agent reach the same reading. What makes this box expensive is not its length but its Constraint Density, in the sense Chapter 2 defines: how much it rules out per token it costs.

Then the flow splits, and the split is the most important structural feature of the diagram. Both branches descend from the same document, and neither descends from the other. The tests are not written against the code, which is the habit that produces a suite asserting whatever the implementation happened to do. The code is not written against the tests, which is the habit that produces an implementation shaped to pass examples. They are siblings, derived independently from one parent, and that independence is what gives the green build any meaning at all.

The left branch is mechanical transcription. A decision-table row becomes a test case, a schema bound becomes a boundary test, a failure-matrix entry becomes a test that asserts the named error code, and an invariant becomes a property test whose generator explores the space that examples cannot reach. Chapter 10 works through the derivation rule by rule. An agent can do the transcription, and usually should, but a human reviews the result against the specification, because an untranscribed clause is a hole that nothing else in the pipeline will find.

The right branch is the part people think of as the whole method, and it is the least interesting part. The agent reads the specification, plus whatever architectural context Chapter 11 decides it needs, and synthesizes an implementation. It is allowed to be creative about mechanism and not allowed to be creative about behavior. If it needs to make a behavioral decision to proceed, the correct move is to stop and ask, which is a stop condition rather than a failure.

The convergence box is where the two branches meet, and the word that earns its place there is deterministic. Nothing in that box has an opinion. A linter, a strict type checker, and a contract suite either pass or fail, identically on every run, on every machine, for every reviewer. That is the property the rest of the pipeline lacks and depends on: a generator that samples from a distribution is made safe by a judge that does not. Chapter 10 formalizes this box as the Three Gates.

Failure takes the left exit, and the left exit is where the discipline is won or lost. The arrow does not point at the code. It points back at the top box, with a detour: you read the failure, you decide whether the specification said what you meant, and only then do you act. Sometimes the agent misread a clause that is in fact clear, and re-running is the whole fix. More often the failure is a sentence you never wrote, and the repair belongs upstream. What you may not do is reach into the generated code and adjust it until the gate goes green, and the reason is the subject of 4.3.

Success takes the right exit, and it carries a commit pair rather than a commit: the specification change and the regenerated implementation, linked, in the order Chapter 12 prescribes. A deployment whose specification change is missing from history is a deployment nobody can later explain.

## 4.3 The Golden Rule of Clean Spec

Everything in the pipeline rests on one prohibition, and because it is the prohibition that teams break first, it gets a name. This is **The Golden Rule of Clean Spec**:

> Never hand-edit generated code. If the code is wrong, incomplete, or slow, the defect is in the specification. Fix the spec, then run the agent again.

I state it as an absolute because the hedged version does not survive contact with a sprint. A rule with a standing exception becomes a rule with a habit, and this particular habit is the one that returns a repository to the condition Chapter 1 described, where the only account of what the system guarantees is the system itself.

Start with why the edit is so tempting. The gate is red, the fix is four lines, and the specification change is a paragraph that needs a review. Editing the code is faster by a factor of ten and it works. It works today, and the cost arrives later, which is the structure of every bad engineering habit ever recorded.

The cost is that the repository now has two sources of truth that disagree, and no mechanism for noticing. The specification describes a behavior the code does not have. The code has a behavior no document mentions. Nothing is broken, no test fails, and the divergence is invisible until the next regeneration silently deletes your four lines, or the next engineer reads the document and believes it. That condition has a name in this book, spec drift, and Chapter 12 is about detecting it mechanically, because human attention has a perfect record of failing to.

The compiler analogy from Chapter 1 does the rest of the argument. You have spent years not patching compiler output. When a program misbehaves you do not open the emitted assembly and correct an instruction, even though you could, and even though it would work for that one build. You change the source and recompile, because the source is the artifact and the output is a consequence. The Golden Rule says nothing more exotic than that, applied to an output that happens to be readable enough to tempt you.

Three words in the rule deserve separate attention. **Wrong** is the easy case: the code does something the specification forbids, or fails to do something it requires. Usually the clause was ambiguous, and the repair is to make it unambiguous.

**Incomplete** is more common and more dangerous, because the gate often passes. The code handles four of the five cases and nothing told it about the fifth. A missing case in generated code is almost always a missing row in a decision table or a missing entry in a failure matrix, and the repair is to add it, which also adds the test that will catch it forever.

**Slow** is the word engineers expect to be an exception, and it is not one. If an endpoint must answer within 200 milliseconds at the ninety-fifth percentile, that is a requirement, and a requirement that is not written down has been delegated, exactly like every other silence. The repair for slow generated code is to state the budget, state the constraints that make it achievable — no query inside the loop, at most one round trip to the payment port — and let the agent work inside them. Performance constraints belong in the document for the same reason correctness constraints do: if they are not stated, the next regeneration resamples them.

The rule also changes what a code review is for, and I consider this a benefit rather than a loss. You are no longer reviewing generated code to improve it, because improving it by hand is forbidden. You are reading it to answer one question: does this implementation reveal something my specification failed to say? Every review comment becomes a candidate specification change. That reframing makes reviews faster and much better, because a comment that ends up in the document protects every future generation, while a comment that ends up in the diff protects one.

There is exactly one situation in which a human writes into generated code with my blessing, and it is a bounded emergency with a mandatory repair afterward.

## 4.4 Objections and answers

I have made this argument to a lot of skeptical senior engineers, and the objections arrive in a reliable order. All four are reasonable, and three of them have answers that make the method stronger rather than weaker.

### What about production hotfixes?

This is the strongest objection and the one I concede most of. It is two in the morning, checkout is returning errors on every discounted order, and the fix is a one-line null check. You are not going to amend a decision table, get a spec review, regenerate a module, and wait for a full gate run while revenue stops. Neither am I. Ship the one-line fix.

What the Golden Rule actually forbids is not the hotfix. It is leaving the hotfix as the end of the story. The patch creates a known, deliberate divergence, and a deliberate divergence needs an owner, a ticket, and a deadline. The repair runs backward through the pipeline: the hand-written fix is read as evidence of a missing clause, the clause is added to the specification, a test is derived from it, and the module is regenerated so that the temporary patch is reproduced by the generator rather than preserved by hand. That is the reverse-drift procedure of Chapter 12, and it is the only sanctioned path from hand-edited code back to a clean repository.

Two rules keep this from becoming a loophole. The divergence is recorded where tooling can see it, not only in a person's memory, so that the conformance linter of Chapter 12 can fail the build if it is still open next week. And the deadline is short — days, not quarters. A hotfix that has outlived its repair ticket is no longer a hotfix; it is the beginning of a second source of truth.

### Regeneration is expensive

Often this objection means wall-clock time, and sometimes it means money. Both are worth taking seriously, and both are usually mis-measured.

The first answer is that you should not be regenerating the whole system. If a change to one module forces you to regenerate six, the problem is not the method; it is that your specifications do not have boundaries, and Chapter 8 is entirely about giving them boundaries. A well-factored specification set regenerates one module, runs that module's gates, and leaves the rest of the repository untouched. The 300-line rule of thumb that Chapter 9 defends exists partly for this reason.

The second answer is about what you compare the cost against. Regeneration is expensive relative to a four-line hand edit and cheap relative to the bug that the hand edit causes in eleven weeks. Checkout's six weeks in the opening scenario were not slow because generation was slow. They were slow because every change required rediscovering an unwritten rule, which is the quadratic term from Chapter 1, and no amount of faster generation touches it.

The third answer is that regeneration cost is partly a property of your document, which means you can engineer it. A specification with high Constraint Density, in the sense of Chapter 2, succeeds on the first attempt more often, because it leaves fewer decisions to sampling. Teams that experience regeneration as expensive are usually regenerating three or four times per change, and the cause is almost always a vague document rather than a slow generator. Raising density lowers the number of attempts, and the number of attempts is the term that dominates.

### Sometimes the model is wrong and the spec is fine

This objection is true as stated and misleading in what it implies. Agents do produce wrong code from good documents; Chapter 1 listed that as one of the three things this book does not claim away. A specification narrows the output space, it does not collapse it to a single program, and a careless reading of a perfectly clear clause happens every day.

Then the question is what you do about it, and "hand-edit the output" is still the wrong answer. Consider what happened concretely. A wrong implementation passed through a gate whose entire purpose is to stop wrong implementations. That is the interesting failure, and it is not the agent's.

So the diagnosis changes from "the spec was wrong" to something more precise and more useful: the specification lacked the test requirement that would have caught this. The behavioral clause may well be correct and complete. What is missing is the instruction that turns that clause into a check — the boundary case, the property, the failure-matrix row that should have produced a red build. Chapter 9 gives test requirements a mandatory section of their own, and Chapter 10 shows how to write them, precisely because a clause that nothing verifies is a clause you will have to defend by hand forever.

So the repair is the same shape as every other repair, and the specification still changes. You add a test requirement, regenerate, and now the agent's next careless reading of that clause fails in CI instead of in production. You have converted a one-time catch by an alert human into a permanent mechanical one. An agent that is wrong in a way your gates detect is not a problem with the method; it is the method working.

### What about exploratory code?

Here I have no argument to make, because the objection is correct. When the purpose of writing code is to find out something you do not know, a specification cannot come first, since the specification would have to state the thing you are trying to learn. Writing one would be a ritual.

The honest answer is that exploratory work is outside the pipeline, and saying so protects the method rather than weakening it. A spike is a question with a deadline, and its deliverable is an answer, not an artifact. What matters is the boundary: a spike is not merged, or it is merged behind a flag with a deletion date, and the knowledge it produced leaves the repository as clauses in a document rather than as code nobody dares remove. The rule I use is blunt. Write the throwaway code, learn the thing, then write the specification from what you learned and regenerate the implementation. Keeping the spike is how a prototype becomes a production system by accident, which is the opening scenario of Chapter 1.

## 4.5 What lives where

If the specification is the source of truth, the repository has to say so in its layout, because a principle that is not visible in the directory structure will be forgotten by the third new hire. The tree below is the minimal shape; Chapter 11 expands it into the full layout an agent navigates.

```
meridian-checkout/
├── CLAUDE.md                     hand-written: agent instruction file
├── specs/
│   ├── architecture.md           hand-written: boundaries, dependency rule
│   └── modules/
│       └── promotions/
│           ├── promo-code.md     hand-written: the normative document
│           └── promo-code.schema.json   hand-written: the data contract
├── tests/
│   ├── contract/                 generated from specs/, reviewed by a human
│   └── property/                 generated from specs/, reviewed by a human
└── src/
    └── promotions/               generated: never hand-edited
```

Three categories, and the boundaries between them are the point. `specs/` and the agent instruction file are hand-written, and they are the only things in the repository that are. Everything under `tests/` is generated from `specs/` and then read by a person, which is a middle category I insist on: machines transcribe tests well and omit clauses silently, so a human checks coverage of the document rather than coverage of the lines. Everything under `src/` is generated and nobody touches it, which is what the Golden Rule means when you express it as a file permission rather than as a sentence in a book.

Two conventions make the boundary enforceable instead of aspirational. Generated files carry a header naming the specification and section they implement, which Chapter 12 develops into the traceability tags a conformance linter reads. And `src/` is regenerable from `specs/` at any commit: if you cannot delete a module and get it back, something is in there that was never written down, and finding out on an ordinary Tuesday is much better than finding out during an incident.

The agent instruction file deserves a word, since it is hand-written but is not a specification. An agent instruction file such as CLAUDE.md carries the standing rules of the repository — the gates that must pass, the directories that may be written, the stop conditions that require asking a human. It describes how work is done here; the documents under `specs/` describe what must be true. Chapter 11 writes one out in full.

What is absent from the tree matters as much as what is in it. There is no directory of prompts, because a prompt is an input to a generator and a specification is an artifact, and the day you start versioning prompts you have two documents competing to be authoritative. There are no design notes that restate the specification in friendlier language, for the same reason. One document per module, addressable by section, is the whole discipline.

## 4.6 When SDD is the wrong tool

A method that claims to fit everything fits nothing, so here is where I do not use this one.

Throwaway scripts. A forty-line data fix that runs once, in a terminal, under supervision, and is then deleted has no future readers and no regeneration. Specifying it is pure overhead. The test is whether the code will exist next month: if the answer is no, prompt it and move on.

Spikes. As 4.4 conceded, a question cannot be specified before it is answered. Keep the boundary sharp and the deletion date real.

Unknown domains. This is the case that is most often misdiagnosed, so it deserves care. Sometimes you cannot write the invariant because you do not yet know what the business rule is, and no amount of discipline conjures the knowledge. But the distinction matters enormously: not knowing the rule is a reason to go find out, not a reason to let a generator pick one. What you do in an unknown domain is write the specification with an Open Questions section and let it be honestly incomplete, which Chapter 9 makes a mandatory section precisely so that ignorance has a place to live where a reviewer can see it. A document that says "we do not know what a refund does to a stacked discount" is worth far more than silence, because it tells the agent to stop rather than to guess.

Below the crossing point. Chapter 1's chart had a crossing point, and its existence is an argument in both directions. One module, one domain, three implicit rules, two weeks of life: stay to the left and prompt freely. Two domains touching the same number, a rule somebody will ask about in a year, an on-call rotation: you are to the right, and you were to the right before it felt like it.

The remaining case is the one I want to leave you with, because it is where the discipline pays most and gets applied least: code that already exists. A system with no specification and nine years of behavior is not outside this method. It is the hardest and most valuable application of it, because the specification has to be recovered from the implementation before anything can be regenerated against it. Chapter 16 reverse-specifies a nine-hundred-line function that nobody dares touch, and the procedure there is the same pipeline run backward once.

Part I ends here. The argument is complete: code has become a derived artifact, a language model is a nondeterministic compiler that treats your silences as permissions, contracts are the unit that removes the silences, and the pipeline in 4.2 with the rule in 4.3 is how a team works once it believes all three. What Part I has not done is tell you what a specification actually looks like — which words, which structure, which sections, which size. Chapter 5 starts there, with the reason plain English was never going to be enough.

## Key Takeaways

- Spec-Driven Development completes TDD rather than replacing it: the specification is authored by a human, the tests are derived from it, and the code is synthesized against both.
- A test suite is a poor source of truth because examples under-determine behavior and four hundred test functions cannot be reviewed as a statement of intent.
- Tests and code are siblings derived independently from the same document, and that independence is what makes a green build mean something.
- **The Golden Rule of Clean Spec**: never hand-edit generated code; if the code is wrong, incomplete, or slow — and performance is a specification concern, so an unstated latency budget is a delegated decision like any other — fix the specification and run the agent again.
- A production hotfix may be hand-written, but it creates a recorded divergence with an owner and a short deadline, repaired by the reverse-drift procedure of Chapter 12.
- When an agent misreads a clause that was genuinely clear, the specification lacked the test requirement that would have caught it, so the repair is still upstream.
- `specs/` is hand-written, `tests/` is generated and reviewed by a human, `src/` is generated and never edited, and a module you cannot delete and regenerate contains something nobody wrote down.
- Skip the discipline for throwaway scripts, spikes, and anything left of the crossing point, but record an unknown domain as an Open Question rather than letting a generator choose for you.
