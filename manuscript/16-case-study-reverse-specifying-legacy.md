# Chapter 16: Case Study: Reverse-Specifying a Legacy System

Imagine a nine-hundred-line Python function in Meridian's Logistics domain called `calculate_shipping_rate`, written across six years by engineers who have since moved to other teams, other companies, and in one case retirement. It has eleven parameters, four of which are optional dictionaries whose keys are checked with `.get()` calls scattered throughout the body rather than declared anywhere. It contains a branch reading `if customer_type == "legacy_partner_7":` that applies a flat rate nobody can explain, followed by a comment reading only `# do not remove, breaks Q3 numbers` with no date, no ticket reference, and no indication of whether the customer this branch serves still exists. It writes to a module-level cache dictionary partway through its execution, as a side effect nobody documented, which a different, unrelated function elsewhere in the codebase silently depends on being populated by the time it runs.

Three separate engineers, on three separate occasions, have proposed rewriting it in the last two years. All three proposals died in review, for the same reason each time: a clean rewrite based on reading the function and inferring its intent reliably passes the obvious test cases and reliably breaks something nobody thought to check, because the function's actual behavior and its apparent intent diverged years ago and nobody has been maintaining a record of where. The last attempt shipped a version that was, by every code-quality measure, better than the original, and it silently changed the international shipping rate for a small class of orders that only affected one regional partner's monthly invoice, which nobody in engineering noticed until the partner's finance team called.

Meridian's Logistics team is not short on engineering talent, and the function is not resistant to rewriting because it is complicated in any sense a reasonably skilled engineer cannot handle on a good day with enough coffee close at hand. It is resistant because a rewrite assumes the rewriter already knows what the function is supposed to do, and nine hundred lines of six years of undocumented accretion is not a specification anyone can hold in their head at once, no matter how many times or how carefully they read it.

## 16.1 Why blind rewrites fail

A blind rewrite — read the legacy code, form an intention about what it does, and write a fresh implementation of that intention — fails for a structural reason that has nothing to do with the rewriter's skill. Reading code recovers what the code appears to do on the paths a reader's attention happens to follow. It does not recover what the code actually does on every path, including the ones a reader skims past because they look like defensive boilerplate, and it does not recover why a given branch exists, which is exactly the information a `legacy_partner_7` special case needs before anyone can safely decide whether to keep it.

The failure compounds because a rewrite is judged a success the moment it passes the tests anyone thought to write, and the tests anyone thinks to write for a rewrite are almost always tests of the intent the rewriter formed, not tests of the original's actual, exhaustive behavior. This is survivorship bias applied to software: the branches that get preserved in a blind rewrite are the ones a human reader noticed and judged important, and the branches that get silently dropped are, by definition, exactly the ones nobody noticed — which correlates far more strongly with "obscure and undocumented" than with "unimportant." Meridian's third rewrite attempt did not fail because the engineer who wrote it was careless. It failed because "read the code and rewrite it" was never a procedure capable of recovering behavior that existed only as tribal knowledge encoded in a six-year-old comment nobody could still interrogate.

The alternative this chapter develops does not start with a rewrite at all. It starts by treating the legacy function itself as an unreliable witness whose testimony must be extracted, checked, and only then trusted enough to build on — a discipline closer to archaeology than to authorship, and the four-phase procedure in 16.2 is that discipline made mechanical.

There is a second failure mode worth naming alongside survivorship bias, because it is the one that actually killed Meridian's third rewrite attempt. A rewrite under deadline pressure treats every branch it cannot explain as a candidate for simplification, on the reasonable-sounding theory that unexplainable code is probably unnecessary code. That theory is exactly backward for a codebase that has been in production for years: the branches a team can explain are, almost by definition, the ones somebody documented or discussed recently, which correlates with how recently they were added, not with how much revenue or how many customers depend on them. The `legacy_partner_7` branch is unexplainable precisely because it is old enough that everyone who understood it has moved on — which makes it a worse candidate for casual removal than a branch added last sprint, not a better one, and a blind rewrite's instincts point the opposite direction from where the actual risk sits.

## 16.2 The four phases

```
[Undocumented Legacy Codebase]
              |
              v
   +------------------------+
   | Phase 1: Reverse Spec  | ---> An agent analyzes every branch and drafts a raw specification
   +------------------------+
              |
              v
   +------------------------+
   | Phase 2: Human Audit   | ---> An engineer corrects ambiguity and imposes real invariants
   +------------------------+
              |
              v
   +------------------------+
   | Phase 3: Test Synth    | ---> The audited spec generates a characterization safety net
   +------------------------+
              |
              v
   +------------------------+
   | Phase 4: Re-Synthesis  | ---> An agent generates new, Clean-Architecture-conformant code
   +------------------------+
```

**Phase 1** is deliberately not human-led. An agent reads the legacy function exhaustively — every branch, every parameter, every side effect — and produces a raw, unaudited draft specification describing what the code does, not what it should do. This phase's entire value is that an agent will faithfully document the `legacy_partner_7` branch and the undocumented cache write precisely because it has no instinct to skip past them as unimportant the way a human skimming for intent does.

**Phase 2** is where a human takes over, and it is the phase 16.1's blind rewrites skipped entirely. An engineer reads the raw reverse spec, not the original code, and for each clause decides: is this a real business rule that must survive, an accident of implementation nobody intended, or a genuine unknown requiring a conversation with someone who might remember? The output is an audited, Clean-Spec-formatted document — 16.4 shows one in full.

**Phase 3** derives a characterization test suite from the audited specification, using Chapter 10's transcription rules exactly as any other specification would. The difference in this phase alone is what the suite is for: not to confirm new behavior is correct, but to pin the exact behavior the audit just decided must survive, so that Phase 4 has something to prove itself against beyond a human's memory of having read the audit once.

**Phase 4** is the only phase that writes new code, and by the time it runs, the constrained loop from Chapter 11 has everything it needs: a specification, a derived test suite, and Chapter 10's Three Gates to check the result against. The rewrite that failed three times at Meridian was always, structurally, an attempt to run Phase 4 with Phases 1 through 3 skipped.

Each phase also has a distinct owner, and the ownership is as important as the sequence. Phase 1 is an agent's job because faithfulness, not judgment, is the requirement, and judgment is exactly what a human reader cannot help injecting the moment they start reading legacy code with an eye toward improving it. Phase 2 is a human's job because it requires organizational authority no agent has — deciding that a partner account is truly closed, or that an EU surcharge is still current policy, means querying a database a human has access to and, in Meridian's case, having a conversation with someone who remembers 2019. Phases 3 and 4 return to an agent, because both are mechanical once Phase 2's decisions exist in writing: deriving tests from a decision table and synthesizing code from a specification are exactly the tasks Chapters 10 and 11 already built a discipline around.

## 16.3 Rules for the reverse spec

Phase 1's raw output is only useful if the agent producing it follows three specific rules, each aimed at a specific way legacy code hides its own behavior from a casual reader.

**Identify hidden side effects.** Every mutation of state outside the function's own local scope — a global variable write, a direct database query, a network call buried inside a loop — gets documented as an abstract port, in Chapter 7's sense, whether or not the legacy code ever named it as one. `calculate_shipping_rate`'s undocumented cache write becomes, in the raw reverse spec, a candidate `RateCachePort.store(key, value)` entry, flagged for Phase 2's auditor to decide whether the cache write is a real architectural dependency the new code must preserve or an implementation accident that happened to work.

**Isolate big-ball-of-mud variables.** Legacy code frequently reuses one loosely typed variable — a dictionary, a tuple, a bare string — to carry several unrelated meanings across its lifetime inside a function. The reverse spec's job is to identify every distinct meaning a single variable carries and propose a separate, immutable, typed value object for each, exactly as Chapter 14's Replace Primitive with Value Object refactoring would, except here the primitive obsession was never a deliberate choice, only an accumulation of expedient edits over years.

**Consolidate implicit rules.** Every nested `if`/`elif`/`else` chain becomes an explicit decision table, per Chapter 7's method, with one row per combination the legacy branches actually distinguish — including combinations the original code handles by falling through to a default nobody labeled, which the decision table format forces to become a visible, named row rather than an invisible absence.

None of these three rules asks the agent performing Phase 1 to judge whether any given piece of behavior is actually correct. That judgment belongs entirely to Phase 2, and the discipline of Phase 1 is only to describe faithfully, including everything an author six years removed from the code would have wanted flagged, without editorializing about which parts deserve to survive into whatever comes next.

A fourth habit, not quite a rule but close to one, is worth adding for any team running this procedure for the first time: mark every inference the agent makes with an explicit confidence flag rather than presenting the raw reverse spec as a finished document. Chapter 5 spent a chapter arguing that silence in a specification gets filled by inference, and a raw reverse spec is, deliberately, mostly inference — every clause it states is a hypothesis about intent drawn from code that never stated its intent directly. Tagging each uncertain clause `[UNCERTAIN]`, as 16.4's example does, is what keeps Phase 2's auditor from mistaking the agent's best guess for an established fact, which is the single most common way this procedure goes wrong when a team skips the tagging step and starts treating Phase 1's output as though it were already Phase 2's.

### What "faithful" actually means

It is worth pausing on a question Phase 1's rule set raises without quite answering: faithful to what, exactly, when the code itself contains an evident bug? Suppose a fragment somewhere in the nine hundred lines computes a discount using an operator precedence error that clearly was never intended — a missing set of parentheses that makes a conditional multiplier apply to the wrong term. The reverse spec's job is still to document what the code does, precisely as it does it, and to flag the apparent defect as a note rather than silently correcting it in the transcription. The correction, if there is to be one, belongs to Phase 2, made in the open, by a human who can decide whether four years of customers have been quietly billed according to the buggy formula in a way that makes "fixing" it now its own significant decision — a change to production billing behavior that deserves exactly the review Chapter 12 would demand of any other change to a live financial calculation, not a quiet fix smuggled in under the cover of a rewrite.

## 16.4 Worked example

Here is a shortened fragment standing in for `calculate_shipping_rate`'s actual tangle, small enough to walk through end to end.

```python
def calc_rate(weight, dest, cust_type, opts=None):
    opts = opts or {}
    rate = weight * 0.42
    if dest.startswith("EU"):
        rate *= 1.15
    if cust_type == "legacy_partner_7":
        rate = 12.50
    if opts.get("express"):
        rate += 8.0
    _rate_cache[dest] = rate  # used by invoice_reconciler.py
    return round(rate, 2)
```

**Phase 1's raw reverse spec**, produced by an agent reading only this fragment, states what it finds without judgment:

> The function computes a base rate as `weight * 0.42`. If `dest` starts with `"EU"`, the rate is multiplied by `1.15` [UNCERTAIN: no comment states why 1.15; possibly an EU customs surcharge]. If `cust_type` equals the literal string `"legacy_partner_7"`, the rate is overridden entirely to a flat `12.50`, discarding weight and destination [UNCERTAIN: origin and continued relevance unknown]. If `opts` contains a truthy `"express"` key, `8.0` is added. The function writes its result into a module-level dictionary `_rate_cache`, keyed by destination, with a comment indicating `invoice_reconciler.py` depends on this write [SIDE EFFECT: undeclared cross-module dependency].

**Phase 2's audit** resolves each uncertainty. The team confirms with a remaining member of the original team that the `1.15` EU multiplier is a genuine, still-current customs surcharge rule — it survives. Nobody can find a customer named `legacy_partner_7` in Meridian's current partner directory, and a query against the partner database confirms the account was closed four years ago — the audit marks this branch for removal, a decision 16.6 returns to. The cache write is confirmed as a real, if poorly named, dependency `invoice_reconciler.py` still relies on — it survives, formalized as a named port.

The audited result is `SPEC-RATE-009`:

### SPEC-RATE-009: Shipping Rate Calculator

#### 6. State Rules: Rate Decision Table

| Rule | Destination is EU | Express Requested | Outcome |
| :--- | :---: | :---: | :--- |
| R1 | No | No | `rate = weight_kg × 0.42` |
| R2 | Yes | No | `rate = weight_kg × 0.42 × 1.15` (EU customs surcharge) |
| R3 | No | Yes | `rate = weight_kg × 0.42 + 8.00` |
| R4 | Yes | Yes | `rate = weight_kg × 0.42 × 1.15 + 8.00` |

N-1: On every successful calculation, the result **MUST** be published via `RateCachePort.store(destination, rate)` for downstream reconciliation consumers.

**Phase 3's characterization tests** transcribe the table directly, one test per row, exactly as Chapter 10 already established for any decision table — with an additional test confirming `RateCachePort.store` is called, because N-1 makes the previously undocumented side effect a normative requirement the new implementation must keep honoring.

## 16.5 Re-synthesis and the safety net

Phase 4 hands `SPEC-RATE-009` and its characterization suite to the constrained loop from Chapter 11. The agent writes a fresh implementation — typed, with `RateCachePort` as an explicit dependency rather than a module-level global, with `weight_kg` as a value object rather than a bare float — and Chapter 10's Three Gates check it against the characterization suite exactly as they would check any other module.

The safety net's value is specific and worth stating precisely: it proves the new implementation reproduces every behavior the audit decided must survive, and it says nothing about behavior the audit decided to change on purpose. This distinction is what separates re-synthesis from the blind rewrites that failed three times before. A blind rewrite has no way to distinguish "this differs from the original because I deliberately fixed it" from "this differs from the original because I missed something," because it never produced a document stating which behaviors were decisions. Re-synthesis against a characterization suite makes every difference from the original traceable to one of exactly two causes: a row the audit explicitly changed, findable in `SPEC-RATE-009`'s own text, or a genuine regression the test suite catches before it ships.

Running Phase 4 through Chapter 11's constrained loop rather than an open conversation matters more here than almost anywhere else in this book, because a legacy re-synthesis task is exactly the kind of work an open chat session tends to wander during. An agent with an unstructured mandate to "clean up and modernize this shipping calculation" has every incentive to also rename variables in `invoice_reconciler.py`, reformat unrelated modules it happens to open while tracing the cache dependency, and generally treat the task as license to improve everything it touches along the way. The constrained loop's Init step, scoped to exactly `SPEC-RATE-009` and its characterization suite, forecloses all of that by construction — the same discipline that kept Chapter 11's fraud-suspension diff to one file keeps a legacy re-synthesis from turning into an unreviewable sprawl across a codebase nobody asked to have touched.

The new implementation this phase produces looks unremarkable next to the original, which is exactly the point. `RateCachePort` replaces the module-level `_rate_cache` dictionary as an explicit constructor dependency. `weight_kg` becomes a value object with its own positivity invariant, per Chapter 14's refactoring, rather than an untyped parameter a caller could pass a negative number into. The decision table's four rows become four branches with no more cleverness than the table itself requires. None of this is exciting engineering, and that is the correct outcome for a rewrite whose entire purpose was to stop being exciting — to turn a function three engineers were afraid to touch into one any engineer can read, modify, and trust in an afternoon.

## 16.6 What to do with behavior nobody wants to keep

The `legacy_partner_7` branch is the case this whole procedure was built to handle correctly, and the handling is not silence. Removing behavior from a legacy system is a specification change exactly as much as adding behavior is, and it goes through Chapter 12's ordinary review flow rather than simply vanishing between the raw reverse spec and the audited document: a changelog entry stating that the flat-rate branch for a since-closed partner account was removed, dated, attributed, and versioned as the MAJOR change it actually is, because any caller still passing `cust_type="legacy_partner_7"` — however unlikely — will now receive a different rate than before.

That entry is worth more than it looks like it should cost. A silent deletion during a rewrite is indistinguishable, to anyone reading the diff six months later, from an accidental regression; a changelog entry that says "removed because the partner account closed in 2022, confirmed via partner database query" is a decision a future engineer can trust, argue with, or reverse, on its own stated terms, without having to reconstruct the reasoning from nothing the way Meridian's team had to reconstruct `calculate_shipping_rate`'s intent in the first place. Reverse-specifying a legacy system does not just produce a cleaner implementation. It produces the document that should have existed the whole time, which is the only artifact that stops the next six years from accumulating the identical kind of debt this chapter spent four phases paying down.

Not every audited decision to drop behavior is as clean as a closed partner account. Sometimes the honest conclusion is that nobody can determine, even after querying every database Meridian still has access to, whether a branch is safe to remove — and the correct move there is not to guess in either direction. It belongs in `SPEC-RATE-009`'s Open Questions section, flagged, with the original branch preserved in the new implementation exactly as Phase 1 found it, until someone with the authority to make the call actually makes it. A reverse-specification project that forces every uncertainty to a premature yes-or-no answer has only replaced one kind of undocumented guess with another, dressed up in the format of a clean specification.

## Key Takeaways

- A blind rewrite fails because reading legacy code recovers what a human reader noticed, not what the code exhaustively does, and the branches most likely to be silently dropped are exactly the undocumented, unglamorous ones most likely to matter to someone.
- The four-phase procedure — Reverse Spec, Human Audit, Test Synthesis, Re-Synthesis — separates faithful description from human judgment from safety-net construction from new code, where a blind rewrite collapses all four into one unreliable step.
- An agent, not a human, should draft the raw reverse spec, because it has no instinct to skim past an undocumented branch as unimportant, and it should flag every uncertainty explicitly rather than resolve it by guessing.
- Reverse-spec rules target three specific blind spots: hidden side effects become named ports, big-ball-of-mud variables become typed value objects, and nested conditionals become explicit decision tables.
- A characterization test suite proves the new implementation reproduces exactly the behavior the audit decided must survive, and nothing more — which is what lets every difference from the original trace to a documented decision instead of an unexplained regression.
- Removing behavior nobody wants to keep is still a specification change: it goes through the same versioned review flow as any other change, with the reasoning recorded rather than deleted along with the code.
- The lasting output of reverse-specifying a legacy system is not only cleaner code; it is the specification that should have existed from the beginning, which is what stops the next several years from accumulating the same undocumented debt.
