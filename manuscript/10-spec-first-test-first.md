# Chapter 10: Spec-First, Test-First

Imagine a Meridian engineer who wants a coding agent to implement a discount calculation and, following an old habit from human TDD, writes one example test before asking for the code: a cart with a hundred-dollar subtotal and a ten-percent promo code should come out to ninety dollars. The agent reads the test, reads a one-line description of the feature, and returns a function. The test passes on the first try, which feels like exactly the outcome test-first development is supposed to produce.

The function, read afterward out of habit rather than suspicion, contains a branch nobody asked for: `if subtotal == 100 and discount_rate == 0.10: return 90`. Below it, a second branch does something that resembles a general discount calculation, never exercised by the one test in the suite, never reviewed by anyone, and — it turns out under a slightly closer look — wrong for stacked discounts in a way that would have shipped straight to production. The agent did not misunderstand the assignment. It satisfied the only specification it was actually given, which was one input-output pair, and a single input-output pair is satisfied exactly as well by a general rule as by a hardcoded special case. Nothing in the transcript distinguishes the two, and a nondeterministic compiler under no obligation to prefer the harder answer has no reason to write it.

This is not a story about a lazy or deceptive agent. It is a story about what one example test actually specifies, which is one point, not a function. Chapter 3 made the same argument about specifications built from examples instead of contracts: examples under-determine behavior, and a hundred of them still say nothing about the space between them. A single example test is the extreme case of that argument, and the fix is not a better test. It is a different relationship between the specification, the tests, and the code — one where the tests are not something a human writes once, by hand, and hopes the agent respects. They are something the specification determines, mechanically, before the agent is asked to write a single line of implementation.

## 10.1 Tests are derived, not invented

A Clean Spec's Test Requirements section, from Chapter 9's nine-section template, exists so that a test suite is a transcription exercise rather than a creative one. Three kinds of specification content translate into three kinds of test, each by a fixed, repeatable rule.

A decision table's row becomes a test case. Chapter 7's withdrawal table had four rules; a suite derived from it has at least four tests, one setting up the exact combination of conditions each row states and asserting the row's outcome and side effect. `R2` — insufficient balance, any daily-limit status, any fraud signal — becomes a test that constructs an account with a balance below the requested amount and asserts that the result is `REJECTED` with error `INSUFFICIENT_FUNDS`, transcribed directly from the row rather than imagined by whoever writes the test.

A schema bound becomes a boundary test. Chapter 6's `TransactionNotificationEvent` schema declared `amount_in_cents` with `minimum: 1`; the derived suite asserts that zero and negative values are rejected and that the smallest legal value, one cent, is accepted, because a bound stated in a schema and never tested by a value that sits exactly on it is a bound stated on faith. Every `minimum`, `maximum`, `pattern`, and `enum` in a Data Model section has at least one boundary case it implies, and the implication is mechanical enough that Chapter 6's example alone implies eight or nine boundary tests without anyone having to think hard about which ones matter.

An invariant becomes a property test, and this is the case the discount scenario needed and never got, which is the subject of the rest of this chapter.

## 10.2 Property-based testing as the anti-hallucination guarantee

Chapter 3 named the problem with example-based tests directly: three assertions do not establish a property that must hold for every reachable state, and a generator that has learned to make tests pass will cheerfully satisfy three examples without implementing the rule those examples were supposed to illustrate — which is precisely what the hardcoded branch in this chapter's opening scenario did.

The fix is to stop writing examples and start writing the property itself, stated as a universal claim over a whole space of inputs, and to let a tool generate the inputs rather than a human hand-picking three that happen to look representative. For the discount rule underlying the opening scenario's cart, the two properties that matter are that a discount never exceeds the subtotal it is applied to, and that a final price is never negative:

$$\forall x \in \text{Cart}, \quad \text{Subtotal}(x) - \text{Discount}(x) \le \text{Subtotal}(x)$$
$$\forall x \in \text{Cart}, \quad \text{FinalPrice}(x) \ge 0$$

In words: for every possible cart, applying its discount can only lower the total, never raise it, and the total after discount never goes below zero — two sentences that, unlike the single ninety-dollar example, are true across the entire space of carts and discounts Meridian's promo engine could ever see. Hypothesis, a property-based testing library for Python, takes a property stated this way and generates hundreds of cart configurations automatically, searching specifically for the counterexample that would falsify it.

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=1, max_value=10_000), min_size=1))
def test_discounted_total_never_exceeds_subtotal_or_drops_below_zero(item_prices):
    cart = build_cart(item_prices)
    result = apply_discount_rule(cart)
    assert result.final_price_cents <= result.subtotal_cents
    assert result.final_price_cents >= 0
```

Run this against the hardcoded branch from the opening scenario and it fails almost immediately, because Hypothesis will construct a cart the special case never anticipated — say, a subtotal of forty-seven dollars — and the hardcoded path either falls through to undefined behavior or exposes exactly the stacking bug a single example test had no way to see. That failure is the entire value of the technique: a property-based test cannot be satisfied by memorizing the answer to one question, because it does not ask one question. It asks the same question of every input a search strategy can construct, which is what makes it, in this book's terms, the anti-hallucination guarantee — the one test format a generator cannot pass by pattern-matching its way to a plausible-looking special case.

TypeScript teams get the identical guarantee from fast-check, generating the same kind of adversarial input against the same property:

```typescript
import fc from "fast-check";

fc.assert(
  fc.property(fc.array(fc.integer({ min: 1, max: 10_000 }), { minLength: 1 }), (itemPrices) => {
    const result = applyDiscountRule(buildCart(itemPrices));
    return result.finalPriceCents <= result.subtotalCents && result.finalPriceCents >= 0;
  })
);
```

Chapter 3 already identified where the properties themselves come from: they are the domain invariants stated in a specification's `I-` clauses, and Chapter 15 works through a ledger whose entire correctness rests on three of them. Property-based testing is not a separate testing philosophy competing with example-based tests for a team's attention. It is the mechanical consequence of taking an invariant clause seriously enough to test the thing it actually claims, rather than three instances of it.

Example-based tests do not disappear from a Clean Spec's suite; they narrow to the job they are actually good at, which is documenting one specific, named scenario a human wants pinned down for readability — the ninety-dollar cart from the opening scenario is a perfectly reasonable regression test for the ten-percent case once the general property is also in the suite protecting every case the example does not mention. What changes is which one a reviewer trusts to catch a wrong implementation. An example-based test earns exactly as much trust as the number of examples it enumerates, and Chapter 3 already argued that number is always too small for a domain with real structure. A property-based test earns trust proportional to how well the property captures the invariant, which is a question about the specification's own honesty rather than about how many cases someone remembered to write down. A team that ships both, with the property doing the load-bearing work and the examples doing the documentation, has the discipline this section is arguing for. A team that ships only examples has, whether it knows it or not, delegated its actual correctness guarantee to however many test cases a human had patience to type.

It is worth being precise about what a property test does not do, because the technique invites overclaiming. Hypothesis and fast-check search a space; they do not exhaustively enumerate it, and a property test that passes a thousand generated cases has not proven the property holds for every conceivable input, only that no counterexample turned up in the cases the search strategy tried. For the strong, quantifier-shaped guarantee Chapter 3's `I-1` demands — true for every reachable state, not merely every state a random search happened to construct — a property test is the strongest tool this book recommends for ordinary engineering work, and it is meaningfully weaker than a formal proof. That is an acceptable trade for the domains this book addresses, and Chapter 15's ledger will lean on it hard, but it is a trade, not a guarantee, and a specification that needs an actual proof of an invariant — a cryptographic protocol, a consensus algorithm — has left the territory this technique alone can cover.

## 10.3 Contract tests from the failure matrix

A Failure Modes Matrix, from Chapter 7's Level 1 discipline, is a checklist as much as a specification, and the discipline is one test per row, no exceptions and no rows silently merged into a general "error handling" test that asserts something vague.

`SPEC-CORE-001`, Meridian's double-entry ledger specification that Chapter 15 develops in full, declares four rows in its Failure Modes Matrix:

| Condition | Domain Exception | System Action |
| :--- | :--- | :--- |
| Sum of debits ≠ sum of credits | `UnbalancedTransactionError` | Transaction marked `REJECTED`; no balance altered |
| Entries carry mixed currencies | `CurrencyMismatchError` | Immediate rejection; audit log entry |
| Fewer than two entries | `InsufficientEntriesError` | Transaction rejected |
| Source account equals destination account on the same transaction | `CircularEntryError` | Transaction rejected |

Four rows, four tests, each constructing the exact condition the row names and asserting the exact exception and the exact system action — no balance altered, an audit entry written, whichever the row states. A suite with three tests for this matrix has an untested failure mode, and the gap is not hypothetical: it is precisely the kind of gap Chapter 4 described an agent filling in by extrapolation the moment a caller finally triggers it in production, on a path nothing in CI ever exercised.

The discipline scales the same way Chapter 3's clause-per-test rule did for preconditions and postconditions, because a failure matrix row is, structurally, the same kind of statement — a condition paired with a guaranteed outcome — just phrased for the failure side of an operation instead of the success side. Naming each test after its row's domain exception, the way Chapter 3 named tests after `Q-1` and `Q-2`, means a red build on `test_unbalanced_transaction_error` points a reader at one row of one matrix in one specification, without anyone having to read a stack trace to find out what broke.

```python
import pytest
from meridian.ledger import Transaction, LedgerEntry, Money, post

def test_unbalanced_transaction_error(draft_transaction_factory):
    txn = draft_transaction_factory(debits=Money(cents=500), credits=Money(cents=400))
    with pytest.raises(UnbalancedTransactionError):
        post(txn)
    assert txn.status == "REJECTED"

def test_currency_mismatch_error(draft_transaction_factory):
    txn = draft_transaction_factory(currencies=["USD", "EUR"])
    with pytest.raises(CurrencyMismatchError):
        post(txn)

def test_insufficient_entries_error(draft_transaction_factory):
    txn = draft_transaction_factory(entry_count=1)
    with pytest.raises(InsufficientEntriesError):
        post(txn)

def test_circular_entry_error(draft_transaction_factory):
    txn = draft_transaction_factory(source_account="ACC-1", dest_account="ACC-1")
    with pytest.raises(CircularEntryError):
        post(txn)
```

Each test constructs exactly the condition its row names and nothing more, which is what keeps the suite legible as a mirror of the matrix rather than a general-purpose stress test somebody has to reverse-engineer the intent of. A reviewer checking this suite against `SPEC-CORE-001`'s Failure Matrix does not read the test bodies closely; they check that four rows exist and four tests exist, with names that pair off one to one, and the review is finished in the time it takes to count.

## 10.4 The Three Gates

Before any generated code reaches a running environment, it passes through three deterministic checks, in a fixed order, and the order matters because each gate is cheaper to run and faster to fail than the one after it.

```
[Generated Code]
       |
       v
+-----------------------+
| 1. Syntactic Lint     | ---> Failure: immediate rejection, auto-fix where possible
+-----------------------+
       | Pass
       v
+-----------------------+
| 2. Strict Type Check  | ---> Failure: type mismatch against the Data Model
+-----------------------+
       | Pass
       v
+-----------------------+
| 3. Contract Tests     | ---> Failure: an invariant or a failure-matrix row was violated
+-----------------------+
       | Pass
       v
[Artifact Accepted]
```

**The Three Gates**, as this book names the sequence, are deliberately ordered from cheapest to most expensive and from least to most meaningful. A linter catches malformed syntax and style violations in milliseconds, and there is no reason to run a type checker, let alone a test suite, against code that does not parse. A strict type checker — `mypy --strict`, `tsc --strict` — catches a mismatch against the Data Model from Chapter 9's §3 before a single test runs, which is exactly the substitution Chapter 3 already recommended: a value object that cannot be constructed with a negative amount makes a whole family of precondition violations a type error instead of a runtime failure, and a type error is caught by gate two rather than gate three. Contract tests, gate three, are the most expensive to run and the only gate that can catch a behavioral violation — a value that type-checks perfectly and still returns the wrong answer, which is exactly what the opening scenario's hardcoded branch would have sailed through gates one and two, undetected, and only gate three, running the property test from 10.2, would have caught.

Nothing in the pipeline has an opinion, which is the property Chapter 4 already named as the reason the convergence box means anything at all: a linter, a type checker, and a contract suite either pass or fail, identically, on every machine, for every reviewer, every time. That determinism is what lets Chapter 4's correction loop work — amend the spec, regenerate, and the same three gates either agree the new artifact is acceptable or point, specifically, at which one rejected it and why.

## 10.5 Ordering the agent's work

The opening scenario's failure had a second cause beyond the weak test: the human wrote the test, by hand, before the specification existed in a form the agent could derive anything from, which put the test and the specification in the wrong order relative to each other. Chapter 4's pipeline already fixed the order for tests and code — siblings, both derived from one document, neither derived from the other — and this section states what that means for an agent's actual sequence of work.

The agent's first deliverable, given a specification, is not the implementation. It is the derived test suite: contract tests transcribed from the Failure Matrix per 10.3, boundary tests transcribed from the Data Model, and property tests transcribed from the Invariants section per 10.2. A human reviews that suite against the specification before any implementation exists, checking coverage the way 10.6 defines it, which catches a missing test requirement while it is still cheap to add — a comment on a test file, not a diff against working code nobody wants to touch. Only once the suite is reviewed and accepted does the agent write the implementation, against a suite it did not choose the shape of and cannot quietly narrow to fit whatever it was about to generate anyway.

The ordering also gives the agent a principled way to stop instead of guessing, which is the other half of the discipline. If deriving a test from the specification turns out to be impossible — the Invariants section states a rule with no way to construct a counterexample generator for it, or a Failure Matrix row names a condition the Data Model provides no way to trigger — that impossibility is not a testing problem to work around. It is a specification gap, surfaced at the one moment it is cheapest to fix: before any code exists that would have to be regenerated once the gap closes. Chapter 9's Open Questions section is where that gap gets recorded, and Chapter 11 turns "I could not derive a test for this clause" into one of the formal stop conditions an agent instruction file requires an agent to honor rather than paper over with an assumption.

## 10.6 Coverage means spec coverage

Line coverage answers a question nobody in this chapter's opening scenario needed answered: what fraction of the code's own text executed during the test run. The hardcoded branch that returned ninety dollars for exactly one input achieved effectively complete line coverage the moment its one test ran, because the branch that mattered — the general case, silently wrong for stacked discounts — was never the one under discussion. Line coverage measures whether the tests touched the code. It says nothing about whether the code satisfies the specification, which is the only question a Clean Spec discipline actually cares about.

**Spec coverage** is the metric this book uses instead, and it is defined structurally rather than statistically: the fraction of a specification's numbered clauses — every `N-`, every `P-`, `Q-`, and `I-`, every Failure Matrix row, every decision-table row — that has at least one derived test exercising it. A hundred percent line-covered implementation with one Failure Matrix row untested is a specification with a hole in it and a code coverage dashboard insisting everything is fine. A hundred percent spec-covered implementation is a much stronger claim, because it is a claim about the document a human actually reviewed and agreed to, traced clause by clause to a test that would fail if that clause stopped being true.

Computing spec coverage is mechanical for the same reason deriving the tests was: walk every numbered clause in the nine-section template, and check whether a test's name or its explicit annotation cites it. A specification linter — the same family of tool Chapter 12 develops for drift detection — can compute this ratio automatically and fail a build the moment a new clause lands with no corresponding test, which turns "did we test the whole spec" from a question a reviewer has to reconstruct by reading two documents side by side into a number CI reports on every pull request. The opening scenario's gap would have shown up here immediately: one clause, "the discount rule applies correctly to every cart," zero tests citing it, a spec-coverage report reading anything less than a hundred percent, and a build that never should have merged in the first place.

The two metrics are not opposed, and a team should keep both dashboards rather than replace one with the other. Line coverage still catches genuinely dead code — a branch nothing in the specification ever describes reaching, which is its own kind of bug, usually a leftover from a requirement that changed without the implementation catching up. What spec coverage adds is the half of the picture line coverage structurally cannot see: not whether the tests touched the code, but whether the code was ever asked to prove it satisfies the one document a human agreed to before any of it was written. A team that reports only line coverage can reach a hundred percent while shipping the opening scenario's hardcoded branch unnoticed. A team that reports spec coverage alongside it cannot, because the clause the hardcoded branch was supposed to satisfy would sit there, untested, on every single report until someone wrote the property test that actually closes it.

## Key Takeaways

- A single example test specifies one point, not a function, and a generator under no obligation to prefer the harder answer will satisfy that one point with a hardcoded special case exactly as readily as with a correct general rule.
- Tests are derived mechanically from three parts of a specification: a decision-table row becomes a test case, a schema bound becomes a boundary test, and an invariant becomes a property test.
- Property-based testing is the anti-hallucination guarantee because a property stated as a universal claim, searched by a tool like Hypothesis or fast-check, cannot be satisfied by memorizing the answer to one input the way an example-based test can.
- A Failure Modes Matrix gets one contract test per row, named after the row's domain exception, so a red build points at one row of one specification rather than a stack trace someone has to interpret.
- **The Three Gates** — syntactic lint, strict type check, contract tests — run in order from cheapest to most meaningful, and only the third can catch a behavioral violation that type-checks perfectly and still returns the wrong answer.
- An agent's first deliverable from a specification is the derived test suite, reviewed by a human before any implementation exists, so a missing test requirement is caught while it is still a comment rather than a diff against working code.
- A clause a test cannot be derived for is not a testing problem to improvise around; it is a specification gap that belongs in the Open Questions section and, per Chapter 11, is grounds for the agent to stop and ask.
- Spec coverage — the fraction of a specification's numbered clauses with a derived test — is the metric that matters; line coverage measures whether tests touched the code, not whether the code satisfies the document a human actually reviewed.
