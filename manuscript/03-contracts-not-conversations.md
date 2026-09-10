# Chapter 3: Contracts, Not Conversations: Hoare Logic for Working Engineers

Imagine an engineer on Meridian's Accounts team picking up a ticket whose entire body reads "customers should be able to withdraw money". They open a coding agent and type the obvious sentence: "Implement withdraw money from the account." Nothing in that exchange feels careless. The ticket was written by a product manager who knows what a withdrawal is, the engineer knows what a withdrawal is, and so, in a statistical sense, does the generator.

What comes back is sixty lines of competent Python. It accepts an account identifier and an amount, loads the account, subtracts the amount from the balance, saves the row, logs the operation at info level, and returns the new balance in a small result object. It has a docstring. The agent also writes two unit tests: one withdraws twenty from a balance of a hundred and checks that eighty remains, the other checks that the returned object carries the right account identifier. Both pass. The engineer skims the diff, sees nothing objectionable, and opens a pull request.

The integration suite is where it surfaces. One fixture in that suite drives a short sequence of operations against a seeded account and then runs a reconciliation check, comparing the sum of all account balances against the ledger total. The sequence happens to withdraw fifty from an account holding twenty. The withdrawal succeeds. The balance becomes negative thirty. Reconciliation fails, and the failure message is about a ledger mismatch, which sends two people into the ledger code for half a day before anyone looks at the account row.

Here is the part worth sitting with. No test asserted that the balance may not go negative, because nobody had ever written that sentence down anywhere. The generated code is not wrong with respect to its input. It was asked to withdraw money from the account and it withdrew money from the account. The engineer's instinct is to go back to the chat and type "don't let the balance go negative", which will fix this instance, teach the repository nothing, and survive exactly as long as the session does.

What was missing is not a better sentence. It is a contract.

## 3.1 The Hoare triple in plain words

In 1969 Tony Hoare published a notation for saying precisely what a piece of code does, and it remains the most useful formal idea an ordinary working engineer can carry around. It looks like this:

$$\{P\}\; C \;\{Q\}$$

In words: if the condition $P$ holds before the code $C$ runs, then the condition $Q$ holds after it finishes. $P$ is the **precondition**, the state of the world the code is entitled to assume. $C$ is the **command**, the operation itself, which in our setting is the unit of code the agent synthesizes. $Q$ is the **postcondition**, the state of the world the code guarantees on exit. To those three I add a fourth element that Hoare logic treats separately and that specification work cannot do without: the **invariant** $I$, a condition that is true before, during, and after every operation in the system.

That is the whole apparatus. No proof calculus, no weakest-precondition arithmetic, no theorem prover. I am not asking you to verify programs mechanically; I am asking you to use a three-part shape as the unit of thought when you write down what an operation must do. The shape matters because it forces three separate questions that prose lets you blur into one.

The three questions are: what must be true for this call to be legitimate, what do I owe the caller when it returns, and what must never be false regardless of what anyone calls. Most requirement documents I have reviewed answer a fuzzy average of the three and none of them completely. The withdrawal ticket in the opening scenario answered none.

There is a second reason the shape earns its place, and it is specific to working with a nondeterministic compiler. Chapter 2 described the set of programs a generator could plausibly produce from your input as its output space, and argued that specification works by subtraction. A Hoare triple is an unusually efficient subtractor. A stated precondition eliminates every program that validates the wrong things or validates nothing. A stated postcondition eliminates every program whose effect is approximately right, which in a money domain is the same as wrong. A stated invariant eliminates every program that can reach a forbidden state by any path, including paths nobody enumerated. Three short statements rule out more programs than three pages of narrative, which is exactly what high Constraint Density means in practice.

Chapter 2 closed its rewrite of the transfer requirement by admitting that the result was not yet a contract, because it mixed what the caller owes with what the operation guarantees and never named the failures. This chapter is the finished form of that move.

## 3.2 Preconditions: what the caller promises

A precondition is an obligation on the caller. It is not a defensive check and it is not input validation in the ordinary sense; it is a statement of the circumstances under which the operation is defined at all. If the caller violates a precondition, the operation's guarantees simply do not apply, and the contract says nothing about what happens next.

For `withdraw`, two obligations are genuine preconditions. The amount must be positive, expressed as `amount.cents > 0`, which rules out zero-value and negative withdrawals, the second being a deposit wearing a disguise. And the account must exist and be in the `ACTIVE` state, which rules out withdrawals against closed, frozen, and imaginary accounts. Write those down and a whole family of implementations disappears from the output space: every version that accepts a negative amount and quietly credits the account, every version that creates a row when the identifier is unknown.

Now the question that separates people who have written contracts from people who have read about them. Is "the balance is at least the amount" a precondition?

It is tempting, and it is wrong here. The test is whether the caller can reliably establish the condition before calling. A caller cannot, because the balance is shared mutable state: any balance the caller reads may be stale by the time the call lands, and a concurrent withdrawal can invalidate it in between. A condition the caller cannot verify is not an obligation you may impose on the caller. It is a case the operation must handle, which means it belongs in the failure list with a named error code, not in the preconditions. That is why the contract in 3.5 carries `INSUFFICIENT_FUNDS` as an error rather than a precondition, and it is the single most common mistake I correct in spec reviews.

The daily withdrawal limit behaves the same way and fails the same test. Whether today's withdrawals plus this amount exceed the account's limit depends on state the caller does not own and cannot lock, so it becomes `DAILY_LIMIT_EXCEEDED` in the failure list. Notice what the distinction buys you beyond tidiness: everything in the failure list is a documented, testable, returnable outcome with a code a client can branch on, while everything in the preconditions is a bug in the caller. Putting a runtime condition in the wrong column is how you end up with exceptions in production that no client knows how to handle.

One more rule about preconditions, stated flatly because it saves arguments. Every precondition must be checkable by something. If you cannot name the code, the type, or the test that establishes it, you have written a wish. A precondition enforced by a value object constructor is better than one enforced by a validation branch, because `Money` that cannot hold a negative number of cents makes `P-1` unviolatable rather than merely checked, and Chapter 7 makes that substitution a standing recommendation.

## 3.3 Postconditions: what the operation promises

A postcondition is the part engineers skip, and skipping it is what produced the scenario. It states the guaranteed effect of the operation, in terms strong enough that an implementation satisfying it cannot be doing something else.

The discipline that makes postconditions useful is to state effects exactly and to state them as relations between the state before and the state after. "The balance is reduced" is not a postcondition; it permits a fee, a rounding adjustment, and a partial withdrawal. "On success, the account balance decreases by exactly `amount`" is a postcondition, because it fixes the magnitude and, by saying "exactly", forbids every helpful extra deduction an agent might have seen in its training data. The word carries real weight in a specification and I use it deliberately.

The second postcondition is the one almost nobody writes and everybody assumes: on any failure, no balance changes. That sentence is the entire content of atomicity as a caller experiences it, and leaving it unstated is how you get an implementation that deducts the amount, fails to record the ledger entry, and returns an error to a client that now has less money and no record of why. State it and you have eliminated from the output space every implementation that mutates before it validates, every implementation that catches an exception halfway through and returns a polite error, and every implementation whose database work is not inside one transaction.

Postconditions are also where you say what the operation does *not* change, and this is worth a deliberate habit. A postcondition that mentions only the source account leaves the status of everything else ambiguous, which is an invitation: the generated code may well update a `last_activity` column, emit an event, or touch a cached aggregate, and none of that is forbidden. When the set of things that may change is small and important, enumerate it and close the list. "No other account balance changes" is one clause and it rules out an entire category of surprise.

There is a failure mode on the other side, and it is worth naming because the cure for vagueness is often overdose. A postcondition must describe the effect, not the procedure. "Begin a transaction, select the row for update, subtract, insert a ledger entry, commit" is not a postcondition; it is an implementation, and writing it in a specification throws away the one thing a nondeterministic compiler is genuinely good at. Chapter 13 catalogs that habit as a smell and Chapter 14 gives the refactoring that reverses it. The rule of thumb I apply: if a clause would have to change because someone swapped the persistence technology, it is procedure, not postcondition.

## 3.4 Invariants: what is always true

Preconditions and postconditions are local. They talk about one operation, at two moments. An invariant is global in both dimensions: it is a property of the system that must hold at every moment an outside observer could look, for every path through the code, for all time. Formally:

$$\forall s \in S,\; I(s) = \text{true}$$

In words: for every reachable state $s$ of the system, the invariant $I$ evaluates to true. The quantifier is the whole point. A postcondition is a promise about the state after one operation; an invariant is a promise about every state that can ever exist, which means it constrains operations nobody has written yet. That is what makes invariants the highest-leverage sentences in a specification, and it is why I write them first.

The invariant missing from the opening scenario is one clause long: `balance.cents >= 0` for every account at all times. Had it been written down anywhere, three things would have followed mechanically. The agent would have had a stated reason to reject the withdrawal. The test suite would have contained a check derived from it rather than a reconciliation check that failed for the wrong reason. And the reviewer reading the diff would have had something to compare the code against. Instead the rule lived in everyone's head, which is the same as living nowhere.

It helps to separate two things that share the word "invariant", because conflating them makes specifications worse. A **domain invariant** is a truth about the business: balances are never negative, the sum of debits equals the sum of credits, a reserved unit of stock is never also sold. It belongs in the specification, it survives every rewrite of the implementation, and it is the kind of statement that outlives the team. A **loop invariant** is a truth about a mechanism: a property that holds at the top of each iteration of some particular loop, used to reason about why that loop terminates correctly. It belongs in the implementation, at most in a comment, and it is none of a specification's business. When a review turns up loop invariants in a spec, the document has drifted into describing procedure, and Chapter 13 names that drift as syntactic micromanagement.

Domain invariants have a property that makes them unusually cheap to enforce, which is that they are checkable without knowing what operation produced the state. You can assert one after every test in the suite, audit it with a query against production data, and encode it as a database constraint. Chapter 10 turns each of them into a property-based test, because an invariant is precisely a property in the sense that generative testing tools mean, and Chapter 15 works through a ledger whose three invariants carry the whole specification.

A warning about the most common invariant failure, which is not an unstated invariant but an unenforced one. An invariant written in a document and enforced nowhere is worse than no invariant, because it creates the confident belief that the system has a property it does not have. Chapter 13 calls that a Ghost Invariant. Every invariant you write should have at least one mechanical enforcer, and ideally two: a type or a constraint that makes violation impossible, and a test that fails if someone removes it.

## 3.5 The contract block

Here is the shape I use for every operation contract in this book, applied to the withdrawal that went wrong. It is an excerpt from section 4 of `SPEC-ACCT-003`, which the nine-section template of Chapter 9 reserves for invariants and the contracts that rest on them; it is therefore cited as `SPEC-ACCT-003 §4`. The full specification arrives in Chapter 7, where the decision table of `SPEC-ACCT-003 §6` works out which of these failures wins when several apply at once.

### SPEC-ACCT-003: Withdrawal Authorization

#### 4. Invariants

**Operation:** `withdraw(account_id: AccountId, amount: Money) -> WithdrawalResult`

**Preconditions**
- P-1: `amount.cents > 0`
- P-2: The account identified by `account_id` exists and is `ACTIVE`.

**Postconditions**
- Q-1: On success, the account balance decreases by exactly `amount`.
- Q-2: On any failure, no balance changes.

**Invariants**
- I-1: `balance.cents >= 0` for every account at all times.

**Errors**
- `INSUFFICIENT_FUNDS` when `balance < amount`.
- `DAILY_LIMIT_EXCEEDED` when the sum of amounts already withdrawn from `account_id` in the current UTC day plus `amount` exceeds the account's daily limit.

That is the entire contract: six clauses and two error codes, well under a hundred words. Several things about its form are deliberate.

The four headings are fixed and always present, in that order. A contract with no `Errors` section is not a contract with no errors; it is a contract whose author did not think about errors, and the distinction is invisible unless the heading is mandatory. I would rather see `Errors: none` than silence.

Every clause is numbered, with `P-` for preconditions, `Q-` for postconditions, and `I-` for invariants. Chapter 9 fixes that convention for the whole manuscript, and the reason is traceability in both directions. A test can be named after `Q-2`, a review comment can object to `P-2` specifically, a commit message can say which clause it implements, and a failure report can name the clause that broke. Unnumbered rules cannot be cited, and uncitable rules cannot be traced.

The clauses are written in code where code is precise and in English where English is precise. `amount.cents > 0` is better than a sentence about positive amounts because it names the representation: cents, an integer, not a float. "The account identified by `account_id` exists and is `ACTIVE`" is better as prose because the condition is about lifecycle state, and the uppercase `ACTIVE` ties it to an enumerated value elsewhere in the specification. Mixing the two registers inside one block is not inconsistency; it is using each where it subtracts more from the output space.

Finally, notice what is absent. There is no mention of tables, transactions, isolation levels, HTTP status codes, or logging. Those belong in other sections of `SPEC-ACCT-003` or in the architecture specification that Chapter 7 introduces. This block says what a withdrawal is, and nothing about how Meridian happens to implement one this year.

## 3.6 From contract to test

A numbered contract is not only input for a generator. It is a test plan that needs transcription rather than invention, and the transcription rule is one test per clause.

The sketch below covers the two postconditions and the invariant from `SPEC-ACCT-003 §4`. It assumes a `pytest` fixture supplying an active account and a helper that reads a balance.

```python
import pytest
from meridian.accounts import Money, WithdrawalError, balance_of, withdraw

def test_q1_success_decreases_balance_by_exactly_amount(active_account):
    before = balance_of(active_account)
    withdraw(active_account, Money(cents=2_500))
    assert balance_of(active_account) == before - Money(cents=2_500)

def test_q2_failure_changes_no_balance(active_account):
    before = balance_of(active_account)
    with pytest.raises(WithdrawalError) as raised:
        withdraw(active_account, before + Money(cents=1))
    assert raised.value.code == "INSUFFICIENT_FUNDS"
    assert balance_of(active_account) == before

def test_i1_balance_never_goes_negative(active_account):
    with pytest.raises(WithdrawalError):
        withdraw(active_account, balance_of(active_account) + Money(cents=1))
    assert balance_of(active_account).cents >= 0
```

Three properties of those tests matter more than their content. Each test name carries the clause identifier, so a red build names the broken promise rather than the broken function. Each test asserts one clause, so a failure localizes. And none of them was invented: every assertion is a transcription of a sentence somebody reviewed and agreed to, which means the suite cannot drift away from the specification without the drift being visible as a clause with no test.

The preconditions get tests of their own, in a different register: they assert that a violated precondition is rejected rather than absorbed. Zero and negative amounts for `P-1`, a closed account for `P-2`. The failure list gets one test per code, which is the pattern Chapter 10 builds out into a contract test per row of a failure matrix.

What example-based tests like these cannot do is cover the quantifier in `I-1`. Three examples do not establish a property that must hold for every reachable state, and a generator that has learned to make tests pass will cheerfully satisfy three examples. The answer is property-based testing, where the tool generates amounts and sequences and the assertion is the invariant itself; Chapter 10 develops it as the anti-hallucination guarantee, and Chapter 15 applies it to a ledger. For now, note the ordering that makes the whole method work: the contract is written first, the tests are derived from the contract, and the implementation is synthesized last, against both.

## 3.7 How strong may an implementation be?

Contracts raise a question that matters the moment more than one implementation exists behind the same operation: how much freedom does an implementer have to differ from the contract and still be correct?

The answer is asymmetric, and the asymmetry is the useful part. **An implementation may accept more than its contract requires and guarantee more than its contract promises, but never less of either.** That is the substitution rule, and everything else in this section is a gloss on it.

Accepting more means weakening the precondition. If the contract requires an `ACTIVE` account and an implementation also handles `FROZEN` accounts correctly, no caller that obeyed the contract can tell, because every call the contract permitted still works. Guaranteeing more means strengthening the postcondition. If the contract promises that the balance decreases by exactly the amount and an implementation also emits an audit record, no caller that relied on the contract is harmed, because everything promised still holds and more besides.

The reverse directions both break callers, which is why the table below is the whole rule in two rows.

| Clause | Allowed direction | Forbidden direction |
| :--- | :--- | :--- |
| Preconditions | Weaken: accept everything the contract allows, and possibly more | Strengthen: demand something the contract did not require |
| Postconditions | Strengthen: guarantee everything the contract promises, and possibly more | Weaken: deliver less than the contract promised |

Read the forbidden column as a list of outage reports. An implementation that strengthens a precondition rejects calls the contract said were legitimate, so correct callers start failing against a component that was swapped in underneath them. An implementation that weakens a postcondition returns success having done less than promised, which is the worse of the two, because nothing fails at the boundary and the damage appears later somewhere else.

Invariants admit no weakening at all. An implementation may add invariants of its own, since a stricter system state is still a valid one. It may never relax `I-1`, because another component's correctness may rest on it, and "balances are never negative" is exactly the kind of sentence that ends up baked into a reconciliation job three teams away.

This is Liskov's substitution principle, stated over contracts instead of over types, and it is the reason a specification can be satisfied by more than one implementation without becoming a lie. Chapter 8 takes the rule, cites it as the substitution rule of Chapter 3, and applies it to the thing that actually breaks in practice: a port with several adapters, each of which quietly has its own idea of what the contract said.

## 3.8 What a missing contract costs

Return to the opening scenario and ask what the generator actually did with "withdraw money from the account". It did not fail to find a precondition, a postcondition, and an invariant. It supplied all three, by extrapolation, and then implemented them faithfully.

That is the mechanism worth internalizing. An operation cannot be synthesized without some implicit contract, because code has to decide what it checks, what it changes, and what it refuses. If your document does not state those decisions, they are made by sampling from the statistical habits of an enormous amount of public code, and Chapter 2's table of popular defaults tells you what you get. The implicit contract behind the sixty lines in the scenario was roughly this: the precondition is that the account row exists, the postcondition is that the balance is lower than it was, and the invariant set is empty. Every one of those is defensible as a sample. Together they are a bug with a reconciliation failure attached.

I call the result structural instability, because "bug" understates it in a specific way. A bug is a deviation from intent that you can identify, fix, and regression-test. An extrapolated contract is not a deviation from anything: there is no statement it contradicts, nothing to file, and nothing to regression-test against, so the same gap will be filled differently on the next generation and differently again by the next agent. The code is not unstable because it is bad. It is unstable because its contract is resampled every time someone regenerates.

This also explains why the conversational fix fails. Typing "don't let the balance go negative" into a session supplies the missing invariant to exactly one generation. It does not put the clause where the next agent will read it, where a reviewer can object to it, or where a test can be derived from it. Chapter 1 made the general form of that argument about artifacts with positive cognitive return; the specific form here is that a sentence in a chat log is a contract with a lifetime of one request.

The cost is asymmetric in your favor, which is the encouraging part of this chapter. The contract in 3.5 took six clauses and under a hundred words. Finding the negative balance in the scenario took two engineers half a day in the wrong subsystem, and that was the cheap outcome, the one where an integration suite caught it before a customer did. Writing a contract is among the highest-return uses of fifteen minutes available to a working engineer, and unlike most things that claim that, the arithmetic is easy to check.

So the discipline is small and mechanical. Before you describe an operation to an agent, answer three questions in writing: what must be true for this call to be legitimate, what do I guarantee when it returns, and what must never be false no matter what anyone calls. Number the answers. Name the errors. Then let the generator write the code, and let the clauses write the tests. Chapter 4 puts that loop in its proper order and gives it a rule strong enough to argue with.

## Key Takeaways

- A Hoare triple says that if the precondition holds before the operation runs, the postcondition holds after, and it is the unit of thought for specifying any operation.
- A precondition is an obligation on the caller, so any condition the caller cannot reliably establish belongs in the failure list with a named error code instead.
- A postcondition must state the effect exactly, including what does not change and what is guaranteed on failure, and must never describe the procedure.
- A domain invariant holds for every reachable state and therefore constrains operations nobody has written yet, which makes invariants the highest-leverage clauses in a specification; loop invariants belong in the implementation.
- An invariant with no mechanical enforcer is worse than none at all, and since examples cannot cover its quantifier, the enforcer is a property-based test plus, where possible, a type that makes violation impossible.
- Number every clause as `P-`, `Q-`, or `I-` and transcribe one test per clause with the identifier in its name, so that tests, review comments, and failure reports all point at the same sentence.
- An implementation may accept more than its contract requires and guarantee more than its contract promises, but never less of either.
- An operation with no written contract still has one: the agent extrapolates it from public code, which is resampled on every generation and contradicts nothing you can point to.
