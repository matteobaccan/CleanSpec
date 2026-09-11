# Chapter 14: A Catalog of Spec Refactorings

Return to the review that opened Chapter 13, the one where five engineers each sensed a defect nobody could name. Suppose the same five reconvene the following week, on the same draft, now carrying the catalog from that chapter in hand. The meeting runs differently from the first minute. The reviewer who said a paragraph felt "kind of vague" points at it and says "Handwave" instead, and the room already knows what that means and what fixing it looks like. The reviewer who sensed something missing from the state transitions says "Prose State Machine" and sketches the missing `REFUNDING` state on the whiteboard before anyone asks. By the end of the afternoon, the document that took fifteen minutes to approve wrongly the first time takes three hours to fix correctly, and every one of those three hours is spent applying a named, repeatable procedure rather than groping for a fix that might or might not address whatever was actually wrong.

This chapter is those procedures, one per smell cataloged in Chapter 13, in the format Martin Fowler used for code refactorings and this book borrows for specifications: a stated Motivation for why the transformation is worth the effort, a step-by-step Mechanics section precise enough to follow without inventing anything new, and a worked Example showing the document before and after side by side. Two of the nine refactorings below cure two smells each, because Chapter 13 already found that Omniprompt and Zombie Spec share a root cause, as do Handwave and Happy Path Only — a fact this chapter's structure makes visible on the page rather than hides behind nine separate, superficially distinct headings.

## 14.1 Replace Prose with State Table

**Motivation.** Conditional prose describing a sequence of states forces a reader to hold every transition in memory at once to notice a missing one, and Chapter 13 already showed that even a short, competently written paragraph can omit an entire state without any individual sentence reading as incomplete. This is the cure for Prose State Machine.

**Mechanics.** List every state the prose mentions or implies, including states named only by their consequence, as the `REFUNDING` state was implied but never named in Chapter 13's example. For each state, enumerate every event that can occur while the system is in it. For each event, state the guard condition under which the transition fires, the resulting state, and any side effect — a port invocation, typically — the transition triggers. Assemble the result as a table with one row per transition, never one row per state, because a state with three possible events needs three rows to be complete.

**Example.** Before, the prose from Chapter 13: "When an order is created, it is pending. If payment arrives, it becomes paid and is shipped. If payment fails, it is cancelled. The customer can cancel it only if it has not yet shipped, but if it has already been paid, a refund must be issued instead." After, `SPEC-ORD-007`'s state rules in full.

### SPEC-ORD-007: Order Lifecycle

#### 6. State Rules: FSM-ORD-01

| Initial State | Triggering Event | Guard Condition | Final State | Side Effect (Port) |
| :--- | :--- | :--- | :--- | :--- |
| `PENDING` | `PAYMENT_RECEIVED` | Amount equals order total | `PAID` | `WarehousePort.reserveStock()` |
| `PENDING` | `PAYMENT_FAILED` | None | `FAILED` | `NotificationPort.sendAlert()` |
| `PENDING` | `USER_CANCELLED` | None | `CANCELLED` | None |
| `PAID` | `USER_CANCELLED` | Shipment not yet dispatched | `REFUNDING` | `PaymentPort.issueRefund()` |
| `PAID` | `SHIPMENT_DISPATCHED` | Tracking code present | `SHIPPED` | `NotificationPort.sendTracking()` |
| `SHIPPED` | `USER_CANCELLED` | Not permitted | *No change* | Return error `ILLEGAL_ACTION` |
| `REFUNDING` | `REFUND_SETTLED` | Confirmation from payment gateway | `REFUNDED` | `NotificationPort.sendReceipt()` |

Seven rows, one per transition, and the `REFUNDING` state the prose never named now has a row of its own, entered from exactly one place and exiting to exactly one place. Notice too that `SHIPPED` accepting a `USER_CANCELLED` event and refusing it with a named error is itself a row — the prose's "the customer can cancel it only if it has not yet shipped" reads as a simple restriction, and the table version makes the refusal a first-class, testable transition rather than an implicit absence.

A completeness check follows directly from the same table Chapter 7 described for decision tables: walk every state and confirm every event the domain can raise has a row from that state, even if the row's outcome is only a named error. `PENDING` accepts three events in the table above and rejects nothing silently; if a fourth event existed in the business — say, a `PAYMENT_PARTIALLY_RECEIVED` signal from a split-tender purchase — its absence from the table would be visible as a gap in the "Initial State" column rather than hidden inside a paragraph nobody re-read carefully enough to notice the omission. Once the table exists, generating the Mermaid `stateDiagram-v2` Chapter 6 already demonstrated is mechanical: one arrow per row, one state per distinct value in the Initial State and Final State columns, with no editorial judgment left for the diagram to introduce.

## 14.2 Extract Bounded Context Spec

**Motivation.** A document that has accreted responsibilities past what one team can stay accountable for either saturates an agent's attention across concerns nobody asked about — the Omniprompt — or eventually becomes too costly to touch, drifts from the code it once described, and stops being read at all — the Zombie Spec. Both share the same defect: a document's boundary no longer matches the boundary of what actually changes together.

**Mechanics.** Identify the actual bounded contexts mixed inside the document by asking, for each section, which team or actor would legitimately request a change to it — Chapter 8's Single Responsibility test applied section by section rather than to the file as a whole. Group sections by that answer. For each group, create a new specification file, with its own identifier, owner, and version, under its own domain directory. Replace every place the original document referred to another group's concern with a reference by identifier — a `depends_on` entry, or a named port or event the other document now owns — rather than inline detail. For a Zombie Spec specifically, extract only the subset the team can currently verify against production; leave the rest deprecated rather than attempting to rehabilitate material nobody can confirm is still true.

**Example.** Before, `checkout-core.md`, two thousand one hundred lines mixing registration validation, payment gateway fees, fraud thresholds, shipping rates, and UI copy under one heading, owned by no single team. After, five documents: `specs/modules/identity/registration-validation.md`, owned by Identity; `specs/modules/payments/fee-schedule.md`, owned by Payments; `specs/modules/fraud/scoring-thresholds.md`, owned by the fraud team; `specs/modules/logistics/shipping-rates.md`, owned by Logistics; and a slimmed `specs/modules/checkout/checkout-orchestration.md`, owned by Checkout, whose only remaining content is the sequence in which the other four modules are called and what the till does with each result, each other module referenced by identifier rather than restated.

Applied to a Zombie Spec instead of an Omniprompt, the same mechanics run against a different kind of uncertainty. There is no confident five-way split to make, because the team extracting the document does not yet know how much of it is still true. The discipline is to verify each candidate section against current production behavior — a query against live data, a manual test against the running system — before it earns a place in the resurrected document, and to leave everything unverified in a clearly marked, deprecated remainder rather than silently carrying it forward. A resurrected specification that is honestly thirty lines and entirely true is worth more than the original two thousand that nobody could vouch for, and Chapter 16's reverse-specification procedure is this same extraction technique run against an entire undocumented legacy system rather than one stale file.

## 14.3 Introduce Failure Matrix

**Motivation.** A specification that describes error handling in vague adjectives leaves a generator nothing formal to implement against, and one that omits failure handling entirely leaves the identical gap with an even more misleading appearance of completeness, since the happy path reads as though it were the whole story. Both the Handwave and Happy Path Only cure the same way, because both are, structurally, a Failure Matrix that was never written.

**Mechanics.** Walk every dependency the operation touches and ask what happens when it is unavailable, slow, or returns something unexpected — this produces the infrastructure-error rows. Walk every business rule the operation enforces and ask what happens when a caller violates it — this produces the business-error rows. Walk the operation's own input contract and ask what happens when a caller sends something the schema rejects — this produces the contract-error rows. For each row, name a domain-specific error code, its category, and the required system action, following the four-column format Chapter 7 introduced. Delete the vague sentence, or the silent gap, the matrix now replaces.

**Example.** Before: "Handle errors during checkout robustly and gracefully." After:

| Error Condition | Category | Domain Code | Required Action |
| :--- | :--- | :--- | :--- |
| Card issuer declines the charge | Business Error | `CARD_DECLINED` | Reject order; prompt for another payment method |
| Payment gateway does not respond within 3 seconds | Infra Error | `GATEWAY_TIMEOUT` | Retry once; if still failing, fail the order and notify the customer |
| Warehouse confirms only partial stock availability | Business Error | `PARTIAL_FULFILLMENT` | Reject order; offer a partial-quantity order for confirmation |
| Cart payload omits a required shipping field | Contract Error | `MALFORMED_CART` | Reject with the missing field named in the response |

Four rows replace one adjective, and each row is now a candidate for exactly one contract test, per Chapter 10's rule.

The same mechanics apply unchanged when the starting point is Happy Path Only rather than the Handwave — the difference is only where the walk begins. With a vague sentence to refactor, the analyst starts from the adjective and asks what it was gesturing at. With no sentence at all, the analyst starts cold from the operation's dependencies, business rules, and input contract, which is why Happy Path Only, though it looks like the less severe smell on the page, often takes longer to refactor: there is no existing text to react to, only the operation itself to interrogate from scratch.

## 14.4 Replace Primitive with Value Object

**Motivation.** A field typed as a bare primitive admits every value the primitive's type allows, including every value the domain forbids, and pushes the enforcement of that boundary onto a validation branch someone has to remember to write and a caller has to remember to trust. This is the cure for Primitive Obsession.

**Mechanics.** For each primitive field in a Data Model section, identify the invariant the domain actually requires of it — positivity, a currency code drawn from a closed set, a well-formed address. Define a named value object whose constructor enforces that invariant and rejects any value that violates it. Replace every occurrence of the primitive type, in the schema and in the corresponding code, with the value object. Delete any validation branch the value object's constructor now makes redundant.

**Example.** Before: `amount: float`, silently permitting `-50.0` and every representable rounding error a floating-point type carries. After:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    cents: int
    currency: str

    def __post_init__(self) -> None:
        if self.cents < 0:
            raise ValueError("Money cannot be negative")
        if len(self.currency) != 3 or not self.currency.isupper():
            raise ValueError("currency must be a 3-letter uppercase code")
```

A negative balance is no longer a value that reaches a validation branch and is rejected at runtime. It is a value `Money` cannot be constructed to hold, which is Chapter 3's precondition-by-construction argument made concrete for exactly the field type Chapter 15's ledger will build its entire domain layer around.

The refactoring is worth applying even to fields that look harmless in isolation, because the cost of skipping one compounds across a codebase rather than staying contained to the field where the shortcut was taken. A bare `str` for an email address means every function that receives one has to decide, independently, whether to trust it or re-validate it, and a codebase with forty call sites making that decision forty separate times is a codebase with, at minimum, thirty-nine chances to get the validation subtly wrong or skip it entirely. A single `EmailAddress` value object collapses all forty decisions into one, made once, at the only place a malformed value could ever have entered the system.

## 14.5 Extract Invariant from Examples

**Motivation.** A requirement stated only as worked examples is satisfied exactly as well by a hardcoded special case as by a correct general rule, because a finite set of input-output pairs does not distinguish between the two. This is the cure for Example as Specification.

**Mechanics.** Collect every worked example the specification offers for the requirement. Identify the property every one of them satisfies — not the specific numbers, but the relationship between input and output that would still hold for an example nobody wrote down. State that property as a numbered invariant clause, quantified over the whole space of legitimate inputs rather than over the handful enumerated. Keep the original examples in the test suite as named regression cases, now sitting alongside the property test the invariant implies, rather than deleting them.

**Example.** Before: "For example, a hundred-dollar cart with a ten-percent discount code should total ninety dollars." After:

- I-1: For every cart, `FinalPrice(cart) ≤ Subtotal(cart)`.
- I-2: For every cart, `FinalPrice(cart) ≥ 0`.

The ninety-dollar example survives, in the test suite, as `test_ten_percent_discount_on_hundred_dollar_cart`, a single named case among the hundreds Chapter 10's property test now generates and checks against `I-1` and `I-2` directly.

## 14.6 Normalize Modal Verbs

**Motivation.** An invariant correctly stated once, at its point of origin, loses its force the moment a restatement elsewhere weakens its modal verb — a port's `MUST` becoming an adapter document's `SHOULD` is enough to let an implementer read the obligation as negotiable, producing a Ghost Invariant nobody notices is unenforced until it is violated.

**Mechanics.** Locate every restatement of the invariant across the specification tree — in adapter documents, in onboarding guides, in code comments that quote it. Compare each restatement's modal verb against the original clause's. Replace any restatement that weakens the modal with the original's exact keyword. For each corrected restatement, confirm a conformance test exists that would fail if the invariant were violated at that specific site; if none exists, write one before considering the refactoring complete.

**Example.** Before, in an adapter-specific document: "The Stripe adapter should honor the sixty-second idempotency window." After: "The Stripe adapter **MUST** honor the sixty-second idempotency window defined in `I-1` of `PaymentGatewayPort`," paired with a conformance test that calls the adapter's `charge` method twice with the same idempotency key and asserts exactly one charge resulted, run against Adyen and the CI test double as well, so all three adapters answer to the identical, unweakened obligation.

## 14.7 Replace Procedure with Postcondition

**Motivation.** A specification that states how to write code rather than what the code must guarantee denies a generator every idiomatic construct, every vectorized library, and every asymptotically better algorithm a language offers, and it has lost its function as an abstraction the moment it descends to this level of detail. This is the cure for Syntactic Micromanagement.

**Mechanics.** Identify every clause naming a variable, a loop construct, or a named algorithm rather than an outcome. For each, ask what guaranteed effect the procedure produces — the actual property a caller can observe and depend on. State that effect as a postcondition, in the register Chapter 3 established: precise where code is precise, prose where prose is precise, and never a step-by-step description of execution. Delete the procedural clause entirely; nothing about the postcondition should reference the deleted mechanism.

**Example.** Before: "Declare a variable `seen = {}`. Loop over the input array. For each element, check whether its `id` is already a key in `seen`; if not, add it to the output list and to `seen`." After: "Q-1: The output **MUST** contain no two entries sharing the same `id`, and **MUST** preserve the relative order of the first occurrence of each `id` in the input." The postcondition permits a hash set, a sorted-merge pass, or a single vectorized library call — whichever the generator's language makes fastest and most idiomatic — because none of those implementation choices affects whether `Q-1` itself holds.

## 14.8 Invert Infrastructure Dependency

**Motivation.** A business rule stated in terms of a specific database, table, or protocol cannot be reused outside that infrastructure and becomes fragile to any change in it, even when the business rule itself never changed. This is the cure for Domain Leakage.

**Mechanics.** Identify every noun or verb in a domain-layer clause that names a specific technology — a database product, a table name, a SQL verb, an HTTP status code. Define a port: an abstract operation the domain layer can call without knowing what implements it. Rewrite the clause to delegate to that port by name. Move the infrastructure-specific detail — which table, which query, which status code — into a separate, low-level specification for the concrete adapter, which depends on the port from the other side.

**Example.** Before, from an early draft of `SPEC-BILL-017`: "The use case computes the customer's tax liability for the upgrade and saves the result into the Postgres `tax_records` table with an UPSERT query." After: "The use case computes the tax record for the upgrade and delegates it to `TaxRecordPersistencePort.save(TaxRecord)`," with the Postgres UPSERT detail relocated to a separate adapter specification neither `SPEC-BILL-017` nor any other high-level document needs to reference again.

The port's own definition is worth writing down explicitly rather than leaving implicit in the rewritten sentence, because "delegates it to a port" only closes the leak if the port's contract is itself precise:

**Operation:** `TaxRecordPersistencePort.save(record: TaxRecord) -> None`

**Postconditions**
- Q-1: After a successful call, a subsequent read for the same `record.subscription_id` returns a `TaxRecord` equal to the one saved.

Nothing in that contract mentions a table, a query verb, or a database product, and that silence is the entire point: any adapter — Postgres today, a different store after a migration nobody has proposed yet — can satisfy `Q-1` without `SPEC-BILL-017` ever needing to change.

## 14.9 Split Role-Specific View

**Motivation.** An interface large enough to serve every consumer at once forces a reader — human or agent — to locate the narrow slice relevant to their own role inside a much larger undifferentiated surface, and material from an unrelated role sitting nearby in context gets referenced by analogy, producing Modal Mush: a discretionary field whose scope was clear in isolation and ambiguous once it is surrounded by fifty others.

**Mechanics.** Partition the monolithic interface by the bounded context or role that actually consumes each part — the same partitioning Chapter 8's Interface Segregation Spec already argues for. Generate a scoped view for each partition from the same underlying source, never by hand-forking a duplicate, so the views cannot drift from the definition they were extracted from. Update the agent instruction file's routing rule, per Chapter 11's context budget, to load only the view matching a task's declared domain.

**Example.** Before: one fifty-endpoint OpenAPI document, handed in full to every agent regardless of which domain's endpoint the task touches. After: `specs/modules/billing/billing.view.json`, `specs/modules/checkout/checkout.view.json`, and eight further domain-scoped views, each generated from the same underlying schema registry, each containing only the endpoints, fields, and discretionary options that belong to its own domain — so an agent implementing one Billing endpoint sees Billing's dozen fields and none of the other thirty-eight, and a `MAY`-level field two domains over is never close enough in context to be mistaken for license to touch.

## Key Takeaways

- Every refactoring in this catalog follows the same three-part shape — Motivation, Mechanics, Example — because a repeatable procedure is exactly what turns a named smell from a diagnosis into a fix a team can execute the same way twice.
- Replace Prose with State Table turns a paragraph's implicit states, like the `REFUNDING` state Chapter 13 found hiding in one sentence, into rows nobody can leave out without the gap being visible.
- Extract Bounded Context Spec cures both the Omniprompt and the Zombie Spec, because oversized and abandoned documents share one root cause: a boundary that no longer matches what actually changes together.
- Introduce Failure Matrix cures both the Handwave and Happy Path Only, because vague failure language and absent failure language leave a generator the same missing formal vocabulary.
- Replace Primitive with Value Object moves an invariant from a validation branch someone has to remember to write into a constructor that makes the violation impossible to construct in the first place.
- Extract Invariant from Examples keeps the worked example as a regression test while adding the universal property that closes the gap a hardcoded special case could otherwise hide inside.
- Normalize Modal Verbs and Invert Infrastructure Dependency both repair a clause that was correct where it originated and corrupted only in a later restatement or a later addition of infrastructure detail — the fix is always to trace the corruption back to its source and correct it there.
- Split Role-Specific View scales Interface Segregation to a whole platform's schema, generating scoped views from one source so an agent — or a reviewer — only ever sees the surface its actual task requires.
