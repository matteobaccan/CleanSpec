# Chapter 17: Case Study: One Feature, End to End

Suppose a product manager at Meridian writes a ticket for the Inventory team: "Reserve stock when a customer adds an item to their cart, so two people can't buy the last unit at once. Release the reservation after fifteen minutes if the customer doesn't check out." Nine words shorter than the notification sentence Chapter 5 spent a chapter taking apart, and carrying exactly the same shape of hidden decisions — a channel word standing in for a channel, this time a duration standing in for a precise timer, and an entire lifecycle implied by two sentences that never once says the word "state."

Every chapter in this book has worked one slice of the discipline that turns a ticket like this into software a team can trust: contracts from Chapter 3, the composite grammar from Chapter 6, decision tables from Chapter 7, the constrained agent loop from Chapter 11, drift-proof version control from Chapter 12, the smell catalog from Chapter 13 and its refactorings from Chapter 14. This chapter runs all of it, in order, against one feature, from the ticket above to a shipped, tested, versioned specification — including the moment, partway through, where the specification turns out to have a gap nobody caught in review, and what happens next is the entire argument of this book compressed into one incident.

## 17.1 From ticket to draft spec

The engineer who picks up the ticket spends twenty minutes turning it into a first draft, because twenty minutes of drafting is what Chapter 4 argued a specification costs relative to the alternative. The result, `SPEC-INV-021` version `0.1.0`, status `draft`, is short enough to reproduce here in full.

```yaml
---
id: SPEC-INV-021
title: Stock Reservation with Expiry
version: 0.1.0
status: draft
owner: inventory-team
depends_on: [SPEC-ARCH-000]
supersedes: []
---
```

> When a customer adds an item to their cart, the system reserves that quantity of stock so other customers can't buy it out from under them. The reservation should be released promptly if the customer doesn't complete checkout within about fifteen minutes. If the customer does check out, the reservation is consumed by the resulting order.

```
Data Model
- item_id: string
- quantity: int
- expires_in: int
```

That is the entire first draft: one paragraph and three untyped fields, written quickly, in good faith, by an engineer who understood the feature perfectly well and simply had not yet run it through the discipline the rest of this book argues for. It is also, not coincidentally, a small museum of Chapter 13's catalog, and 17.2 is the review that notices.

## 17.2 Spec review: three smells, three fixes

A colleague reviewing the draft the next morning, carrying Chapter 13's vocabulary the way this book has argued a reviewer should, names three defects in under five minutes.

**Prose State Machine.** The paragraph describes at least three states — reserved, consumed, and whatever "released" means — and at least three transitions, entirely in prose, with the exact failure mode Chapter 13 already warned about: a fourth state is implied by "released" without ever being named, and nothing distinguishes a reservation a customer abandoned from one that simply timed out. The cure is Replace Prose with State Table.

**Primitive Obsession.** `expires_in: int` accepts any integer with no stated unit — fifteen what? The paragraph says minutes, the field says nothing, and Chapter 5's quantifier and lexical ambiguity are both present in three characters of a field name. `quantity: int` accepts zero and negative values with equal enthusiasm. The cure is Replace Primitive with Value Object.

**Happy Path Only.** The draft says what happens when a reservation succeeds and what happens when it is consumed by checkout. It says nothing about what happens when the requested quantity exceeds what is in stock, when `item_id` does not exist, or when two carts race for the same last unit at nearly the same instant. The cure is Introduce Failure Matrix.

The review takes an afternoon, not because any one fix is hard but because each one raises a question that needs an actual decision rather than a guess: how many seconds, precisely, is "about fifteen minutes"? What error code fires when stock is insufficient, and does it distinguish "never existed" from "currently zero"? The team settles fifteen minutes at exactly nine hundred seconds, chooses `INSUFFICIENT_STOCK` and `ITEM_NOT_FOUND` as two distinct codes rather than one generic failure, and produces `SPEC-INV-021` version `1.0.0`.

Notice what the review does not do, because it is as instructive as what it does. Nobody proposes rewriting the paragraph to be more careful prose, and nobody proposes adding more examples to make the intent clearer. Both would be treating the symptom Chapter 5 already diagnosed — natural language straining under a job it was never built for — with more natural language, which is the one move this book has spent sixteen chapters arguing never actually closes a gap, only relocates it somewhere slightly harder to spot. Every fix the reviewer proposes instead moves content into a different grammar: the lifecycle into a table, the fields into typed constructors, the missing cases into a matrix. The paragraph survives in the final document only as the Scope section's opening sentence, demoted from specification to orientation.

### SPEC-INV-021: Stock Reservation with Expiry

#### 1. Scope

This module governs the reservation of inventory stock for the duration of a shopping cart session, from the moment an item is added to a cart until the reservation is consumed by an order, explicitly released, or expires.

#### 2. Normative Constraints

- N-1: Adding an item to a cart **MUST** create a reservation only if sufficient stock is available; otherwise the operation **MUST** fail with `INSUFFICIENT_STOCK`.
- N-2: A reservation **MUST** expire exactly 900 seconds after creation unless consumed or released before that deadline.

#### 3. Data Model

**Value Object: `Quantity`** — a positive integer, `> 0`.
**Value Object: `ReservationDuration`** — an integer count of seconds, fixed at `900` for this specification's initial version.
**Entity: `Reservation`** — `reservation_id: UUID`, `item_id: ItemId`, `quantity: Quantity`, `created_at: datetime (UTC)`, `status: enum [RESERVED, CONSUMED, RELEASED, EXPIRED]`.

#### 4. Invariants

- I-1: For every item, the sum of `quantity` across all `RESERVED` reservations **MUST NOT** exceed that item's available stock.

#### 5. Failure Matrix

| Condition | Domain Code | Required Action |
| :--- | :--- | :--- |
| Requested quantity exceeds available stock | `INSUFFICIENT_STOCK` | Reject; no reservation created |
| `item_id` does not exist | `ITEM_NOT_FOUND` | Reject; no reservation created |
| Two reservation requests race for the same final unit | `INSUFFICIENT_STOCK` for the losing request | Requests serialized at the storage layer; one succeeds, one fails cleanly |

#### 6. State Rules: FSM-INV-01

| Initial State | Event | Guard | Final State | Side Effect |
| :--- | :--- | :--- | :--- | :--- |
| `RESERVED` | `CHECKOUT_COMPLETED` | None | `CONSUMED` | `InventoryPort.decrementStock()` |
| `RESERVED` | `USER_REMOVED_FROM_CART` | None | `RELEASED` | `InventoryPort.releaseHold()` |
| `RESERVED` | `TIMER_EXPIRED` | 900 seconds elapsed since `created_at` | `EXPIRED` | `InventoryPort.releaseHold()` |

#### 7. Test Requirements

One contract test per Failure Matrix row; one property test for I-1, generating concurrent reservation attempts against a fixed stock level and asserting the sum of `RESERVED` quantities never exceeds it; one boundary test confirming a reservation at exactly 900 seconds has not yet expired and one at 901 seconds has.

#### 8. Open Questions

None at this time.

#### 9. Changelog

- **1.0.0** — 2026-08-03: Initial active version.

Three named smells, three targeted refactorings, one afternoon, and a document the team is confident enough in to hand to an agent — which is where 17.3 picks up, and where the confidence turns out to be premature in one specific, instructive way.

## 17.3 The agent's plan and first test suite

Following Chapter 11's constrained loop, Init loads `SPEC-ARCH-000`, `SPEC-INV-021` in full, and the agent instruction file; nothing from Checkout, Billing, or any other domain enters context. Plan produces a short, reviewable statement before any code exists:

> Deriving from `SPEC-INV-021`: three contract tests from §5, one property test from I-1, two boundary tests from §7. No implementation will be written until this suite is reviewed.

The property test, once written, looks like this:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=20))
def test_i1_reserved_quantity_never_exceeds_stock(reservation_requests, item_with_stock_of_10):
    for qty in reservation_requests:
        try:
            reserve(item_with_stock_of_10, Quantity(qty))
        except InsufficientStockError:
            pass
    assert total_reserved(item_with_stock_of_10) <= 10
```

A human reviews the suite, confirms it covers every row §5 and §7 name, and approves it. Execute writes the implementation against the reviewed suite, and Validate runs the Three Gates clean on the first attempt — lint, strict types, and every derived test passing, including the property test above, which Hypothesis has by this point run against several hundred generated combinations of concurrent reservation requests with no counterexample found. By every measure this book has built up to this point, `SPEC-INV-021` v1.0.0 is a success.

Read the spec-coverage number the pipeline reports alongside that success, and it says exactly what Chapter 10 promised it would: one hundred percent, every Failure Matrix row and every invariant clause exercised by at least one derived test. It is worth sitting with why that number, true and mechanically verified, still did not prevent the failure 17.4 describes. Spec coverage measures whether every clause a specification actually states has a test protecting it. It cannot measure whether the specification stated every clause the domain actually needed, because that question is not about the tests at all — it is about the document, and no coverage metric computed from a document can see past that document's own boundary. This is the one honest limit Chapter 10 flagged and this chapter now makes concrete: a hundred percent spec-coverage report is a strong claim about internal consistency, and it is not, and was never meant to be, a claim that the specification itself is complete.

## 17.4 The first failure: expiry during payment

The gap surfaces two weeks later, in staging, on a scenario nobody's test suite generated because nothing in the specification described it as a scenario at all. A test engineer, running a manual exploratory pass rather than an automated one, adds an item to a cart, waits until the fifteen-minute timer has almost elapsed, and begins checkout at the fourteen-minute-fifty-eight-second mark — deliberately, to see what happens at the edge Chapter 5 would call a temporal boundary. Payment processing, which involves a round trip to an external gateway, takes four seconds. At the nine-hundred-and-first second, `TIMER_EXPIRED` fires against a reservation that `CHECKOUT_COMPLETED` is about to consume, and `FSM-INV-01`, read literally, permits both transitions from the same `RESERVED` state with no stated precedence between them. In the actual run, the timer wins the race: the reservation moves to `EXPIRED`, the stock is released, and — because nothing was holding it — immediately claimed by a different, unrelated test transaction running in the same environment. The payment that was already in flight then succeeds, on stock that a moment earlier had been sold to somebody else.

This is not a bug in the implementation. The generated code faithfully implements `FSM-INV-01` exactly as written, and Chapter 10's Three Gates all passed because nothing in the specification stated a rule for this exact race to violate. It is a specification gap in Chapter 13's precise sense: `SPEC-INV-021` never modeled that checkout itself takes measurable time, and it never said what should happen to a reservation's timer during the window checkout occupies. Per Chapter 11's stop conditions, this is exactly the situation in which the correct move is not to patch the generated code — the Golden Rule from Chapter 4 forbids it outright — but to treat the discovery as evidence the specification needs a new clause, and to route the fix upstream.

It is worth being precise about which smell this actually is, because it does not map cleanly onto any single row in Chapter 13's catalog, and naming that mismatch is itself useful. It is not quite Happy Path Only, since §5 does enumerate real failure conditions. It is not quite Prose State Machine, since `FSM-INV-01` is already a proper table. The closest name for it is an incomplete decision table in Chapter 7's specific sense: two events, `TIMER_EXPIRED` and `CHECKOUT_COMPLETED`, both legitimately reachable from the same state, `RESERVED`, with no stated precedence and no guard distinguishing the case where both become eligible at nearly the same instant. Chapter 7 argued that a decision table's completeness can be checked mechanically by walking every combination of conditions; what this incident exposes is that the table's condition set itself was incomplete, because nothing in it captured "checkout is currently in progress" as a condition at all. A complete table over an incomplete set of conditions still has gaps, and no amount of row-by-row auditing catches a missing column.

The team also has to answer a harder question before writing any new clause: was this the only such race, or did the review that produced v1.0.0 simply not think to look for others? A second look at `FSM-INV-01` turns up one more candidate — `USER_REMOVED_FROM_CART` and `TIMER_EXPIRED` could, in principle, race the same way if a browser tab sends a delayed removal request after the timer has already fired — but the team judges that case harmless, since both transitions lead to a released reservation regardless of which wins, and releasing stock twice is idempotent in a way consuming it once while also expiring it is not. That judgment goes into the specification too, as a one-line note in §6, rather than being made silently and left for the next reader to wonder whether anyone had considered it.

## 17.5 Amending the spec

The team's fix is a new state, inserted between `RESERVED` and `CONSUMED`, that gives checkout a place to occupy the timeline explicitly rather than treating it as instantaneous.

```yaml
---
id: SPEC-INV-021
title: Stock Reservation with Expiry
version: 1.1.0
status: active
owner: inventory-team
depends_on: [SPEC-ARCH-000]
supersedes: []
---
```

The Data Model's `status` enum grows a fifth value, `PAYMENT_PENDING`, and §2 gains a clause stating the rule the race exposed:

- N-3: While a reservation is in `PAYMENT_PENDING`, `TIMER_EXPIRED` **MUST NOT** fire against it; the expiry timer **MUST** be paused on entry to `PAYMENT_PENDING` and **MUST** resume only if the reservation returns to `RESERVED`.

`FSM-INV-01` gains three rows and loses none, because nothing about the original three transitions was wrong — they were incomplete.

| Initial State | Event | Guard | Final State | Side Effect |
| :--- | :--- | :--- | :--- | :--- |
| `RESERVED` | `CHECKOUT_INITIATED` | None | `PAYMENT_PENDING` | `InventoryPort.pauseExpiry()` |
| `PAYMENT_PENDING` | `PAYMENT_SUCCEEDED` | None | `CONSUMED` | `InventoryPort.decrementStock()` |
| `PAYMENT_PENDING` | `PAYMENT_FAILED` | None | `RESERVED` | `InventoryPort.resumeExpiry()` |

The version bump is MINOR by Chapter 12's rule, not MAJOR: no existing caller's guarantee weakens, because nothing in v1.0.0 ever promised what happens during checkout — the gap simply had no defined behavior, and N-3 supplies one without breaking anything a conforming caller relied on. The Changelog gains an honest entry:

```markdown
### 1.1.0 — 2026-08-19
- MINOR: Added PAYMENT_PENDING state and N-3, pausing the expiry timer
  during checkout to close a race between TIMER_EXPIRED and
  CHECKOUT_COMPLETED discovered in staging.
- Owner: inventory-team
```

And the commit pair Chapter 12 prescribes follows immediately:

```
commit 7c1d9e2
Author: Inventory Guild <inventory-guild@meridian.example>

    spec(inventory): add PAYMENT_PENDING state to close expiry race

    - Add N-3: expiry timer MUST pause during checkout
    - Add PAYMENT_PENDING to Reservation.status and FSM-INV-01
    - Reference: staging incident found via manual exploratory test
```

```
commit 9f4a0b6
Author: Coding Agent <agent-ci@meridian.example>

    impl(inventory): regenerate reservation lifecycle from spec 7c1d9e2

    - Added pauseExpiry/resumeExpiry to InventoryPort
    - Regenerated FSM transition handling (7 rows, up from 3)
    - New property test: expiry never fires during PAYMENT_PENDING
    - Static analysis: passed; spec coverage: 100%
```

The regenerated suite includes a new test, transcribed directly from N-3, that constructs a reservation, transitions it to `PAYMENT_PENDING`, advances a mocked clock past the nine-hundred-second mark, and asserts the reservation is still exactly where it was left — the test that would have caught this failure in Chapter 11's constrained loop, months earlier, had N-3 existed from the start.

## 17.6 Retrospective: what the spec caught that a prompt would not

Run the counterfactual Chapter 4 already argued for in the abstract, concretely, against this exact feature. An engineer who had simply prompted an agent with the ticket's two sentences — reserve stock, release after fifteen minutes — would have received a working implementation on the first try, exactly as the discount-calculation agent in Chapter 10 did, and exactly as unprotected against the same race, because nothing about an unstructured prompt would have produced a state machine explicit enough to reveal that checkout occupies time the original model never accounted for. The race would very likely have shipped to production rather than staging, discovered not by an exploratory test but by a customer complaint about a double-sold item during a high-traffic afternoon, diagnosed under incident pressure rather than during a calm regression run, and patched — per every instinct Chapter 4 warned against — directly in the generated code, at two in the morning, by someone who would never have circled back to write down what they'd learned.

What the specification actually caught was not the race itself — a test engineer's manual exploration caught that, and no amount of specification discipline replaces the value of someone deliberately prodding a system's edges. What the specification caught was everything downstream of the discovery: a precise, citable location for the fix (`N-3`, `FSM-INV-01`), a mechanical way to verify the fix actually closed the gap (a derived test, not a hand-verified patch), a version history explaining why `PAYMENT_PENDING` exists for the next engineer who wonders, and a regenerated implementation that reproduces the fix from source rather than carrying it as an unrepeatable manual edit. The gap was inevitable — Chapter 1 conceded from the first page that specifications narrow an output space, they do not eliminate every possible failure a system can have. What Spec-Driven Development changed was not whether this feature could fail. It was how expensive the failure was to find, to fix, to explain, and to trust was actually fixed — the four questions this entire book has spent seventeen chapters arguing a specification answers and a prompt does not.

Compare the two timelines one more time, end to end, because the comparison is the chapter's actual conclusion rather than a rhetorical flourish. The prompt-only timeline: a working feature ships in days, a customer reports a double-sold item weeks later, an engineer reproduces it under pressure, patches the running service directly, and the fix lives nowhere but that one deployment until someone eventually forgets it exists and reverts it during an unrelated cleanup. The specification-driven timeline: a working feature ships in a few more days than the prompt would have taken, a test engineer's deliberate exploration in staging finds the same gap before a single customer ever sees it, the fix is a nine-line addition to a document three people review in an afternoon, and the resulting `N-3` protects every future regeneration of this module for as long as the specification exists. Both timelines encounter the identical gap. Only one of them pays for it once.

None of this required a smarter agent, a longer specification, or a reviewer who happened to anticipate a payment-timing race in advance — nobody on Meridian's Inventory team saw it coming either, and the honest record of that fact is exactly what the Changelog entry preserves rather than hides. What it required was a structure in which the gap, once found, had somewhere specific to go: a clause to add, a test to derive from it, a version to bump, and a commit pair to carry the reasoning forward. A prompt has no such structure to receive a lesson into. A specification does, and that difference, multiplied across every feature a team the size of Meridian's ships in a year, is the entire economic argument this book has been making since Chapter 1's cost curve.

## Key Takeaways

- A two-sentence ticket carries the same hidden decisions Chapter 5 found in a sixteen-word requirement sentence, and a twenty-minute draft specification is where those decisions first become visible enough to review.
- A first draft written in good faith still reliably contains the smells Chapter 13 catalogs; the value of the vocabulary is turning "something feels incomplete" into three named, independently fixable defects in one afternoon.
- Passing every one of Chapter 10's Three Gates on the first attempt is not proof a specification is complete — it is proof the specification's own stated clauses are internally satisfied, which says nothing about a scenario the specification never modeled in the first place.
- A specification gap discovered after code ships is not a reason to patch the code; it is evidence for exactly one new clause, added through the review flow, that removes the ambiguity for every future regeneration rather than for the one instance a human happened to catch.
- A version bump for a gap-closing clause is usually MINOR, not MAJOR, because nothing about the original document promised behavior for the scenario it never addressed — the fix adds a guarantee rather than breaking one.
- The commit pair — a spec commit citing the discovery, an implementation commit citing the spec commit's hash — turns a production incident into a permanent, traceable part of the system's history rather than an unrepeatable hallway story.
- What a specification protects against is not the existence of gaps, which no discipline eliminates entirely, but the cost of finding them, fixing them, and trusting the fix — the exact four-part cost a prompt-only approach pays in full, every time, with no discount for having paid it once before.
