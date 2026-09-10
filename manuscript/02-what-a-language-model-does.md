# Chapter 2: What a Language Model Does With Your Words

Imagine an engineer on Meridian's Ledger team with a small, well-understood job: move money between two internal accounts. They open a coding agent and type one line. "Implement a function to transfer an amount between two accounts." It is a Tuesday, the task is not interesting, and the sentence feels complete.

The first run produces a tidy function. Amounts are `float`. The balance of the source account is reduced, the balance of the destination is increased, and the whole thing sits inside a single database transaction at whatever isolation level the connection happened to default to. It reads well. It passes the two tests the agent wrote for it.

The engineer is interrupted, loses the session, and runs the same prompt again an hour later. The second run produces a different tidy function. This time amounts are integer minor units, and there is a validation branch that rejects negative values. The balances are updated in the opposite order. There is a retry decorator around the database call. That version also reads well, and also passes its own two tests.

Both functions are defensible. One of them stores money in a binary floating-point type, which means that in some currency and some sequence of operations a cent will evaporate. The other retries a write with no idempotency key, which means that under a timeout it may move the money twice. And here is the part that should bother you most: neither version checks that the source account is different from the destination.

Nobody asked for that check. Nobody asked for it because it is obvious, and it is obvious in the way that costs money. A transfer from an account to itself is either a no-op or, depending on how the two updates are sequenced and how the balance is read, a way to create funds out of nothing. The engineer did not decide to allow it. They did not decide anything. They wrote one sentence, and every decision that sentence did not make was made somewhere else.

This chapter is about where those decisions are actually made, and how to take them back.

## 2.1 What the machine is really doing

Chapter 1 called the generator a nondeterministic compiler and left the mechanism alone. Now the mechanism matters, because you cannot write effective input for a system whose behavior you have the wrong model of. Strip away the interface and the tooling and a large language model (LLM) does one thing repeatedly: given a sequence of tokens, it produces a probability distribution over what the next token might be, samples from that distribution, appends the result, and repeats.

Written out, the quantity it computes for each step is this conditional probability:

$$P(T_n \mid T_1, T_2, \dots, T_{n-1})$$

In words: the model picks each next token based on everything before it. There is no separate planning phase, no internal representation of your intent that it consults and then renders into code. There is a running prefix — your specification, the files it has been shown, and whatever it has already written — and a repeated bet about what comes next.

Two consequences follow immediately, and both are practical rather than philosophical.

The first is that generation is sampling, so identical input yields different programs. The distribution at each step assigns nonzero probability to many continuations, and the sampler takes one. The two transfer functions in the opening scenario were not a malfunction. They were two draws from the same distribution, which is exactly what sampling means. Any workflow that depends on the generator producing the same thing twice is built on a false assumption, which is why verification in this discipline is mechanical and repeated rather than observed once.

The second consequence is the useful one. Because every token is conditioned on the entire prefix, your text does not "instruct" the machine in the way a function call instructs a runtime. It reweights. Each constraint you state makes some continuations much more likely and others much less likely, and the effect persists for the rest of the generation. This is why the distinction between saying something and saying it precisely is not stylistic. A vague sentence reweights weakly. A typed, quantified, numbered sentence reweights hard.

I find it helpful to name the thing being reweighted. Call the set of programs the generator could plausibly produce from a given input its **output space**. Every program in that space is consistent with what you wrote. Most of them are wrong in ways you care about. The entire craft of specification engineering, as I practice it, is the craft of making that space small enough that its remaining members are all acceptable, and then checking mechanically that the one you got is a member.

Notice what this framing does to the usual advice about communicating with agents. "Be clear" is not wrong, but it is aimed at the wrong target, because clarity is a property measured against a human reader who will ask you a question when confused. A generator never asks. What you need is not clarity but constraint, and those two come apart constantly: a paragraph can be perfectly clear to a colleague and still leave ten thousand acceptable programs in the output space.

## 2.2 Collapsing the output space

Here is the vague version of the transfer requirement, written the way it usually gets written:

> Handle financial transactions carefully.

As a sentence to a person, it communicates a stance. As input to a generator, it is nearly empty. It fixes a domain and a register and nothing else. The output space it selects contains essentially every program in the training distribution that looks like a transfer: float amounts and integer amounts, validated inputs and unvalidated ones, transactional and non-transactional, idempotent and not. The spread of behaviors in that space is enormous, and "carefully" does not narrow it, because the word has no operational content. There is no test you can write that fails when code is insufficiently careful.

Now the same requirement stated as constraints. First in words, because the words are the specification and the notation is only a compact restatement of it.

A transfer is a triple of a source account, a destination account, and an amount. The source must not be the same account as the destination. The amount must be a positive integer in minor units. When a transfer succeeds, the source balance decreases by exactly the amount and the destination balance increases by exactly the amount, and no other balance changes. The transfer executes under serializable isolation, so no interleaved transfer can observe or modify either balance mid-operation. Every transfer carries an idempotency key, a UUID supplied by the caller; a repeated key returns the original result and moves no money a second time.

The same content in notation, for the parts where notation is tighter than prose:

$$T = \langle S, D, A \rangle \quad \text{with } S \neq D,\; A \in \mathbb{N}^{+},\; \Delta_{\text{balance}}(S) = -A,\; \Delta_{\text{balance}}(D) = +A$$

Read that as: a transfer consists of a source, a destination, and an amount; the source and destination differ; the amount is a positive whole number; and the operation changes the source balance by minus the amount and the destination balance by plus the amount, exactly. The symbols earn their place here because the relationship between the two balance changes is precisely what English sentences blur. "Debits the source and credits the destination" does not say the two magnitudes are equal; the formula does.

What did those five sentences and one line of notation actually do to the output space? They eliminated float amounts, because the type is stated. They eliminated the self-transfer that neither run in the scenario caught, because inequality is stated. They eliminated fee deductions, rounding adjustments, and partial transfers, because the balance deltas are stated as exact and equal. They eliminated the lost-update interleaving, because the isolation level is named rather than left to a connection default. They eliminated double-spending under retry, because idempotency is specified with a concrete key type instead of being implied by the word "safely".

Each of those eliminations removes a family of programs that the vague version permitted. That is what specification does mechanically: not persuasion, but subtraction. And note that the dense version is barely longer than a careful paragraph of prose. Precision is cheap in tokens; it is expensive only in thought, which is the point Chapter 1 made about where engineering value moved.

One thing that version is not yet: a contract. It states what must hold without separating what the caller owes from what the operation guarantees, and without naming the failures. That separation is the subject of Chapter 3, and the formal sentences above are a preview of it rather than the finished form.

## 2.3 Where the defaults come from

If your specification does not decide something, the generator still has to emit tokens, and it emits the ones with the highest probability given everything else it has seen. That probability was shaped by an enormous amount of public code. So the practical question is not "what will the agent do when I am silent", which is unanswerable, but "what does the average of all published code do", which is depressingly answerable.

The table below lists the silences I see most often in payment and ledger work, the choice that public code makes by sheer volume, and what it costs in a domain where money is involved.

| Silence in the specification | The statistically popular choice | What it costs in a money domain |
| :--- | :--- | :--- |
| The type of a monetary amount | A binary floating-point number | Fractions of a cent appear and disappear; sums stop reconciling |
| What happens on an unexpected error | Catch broadly, log, continue | A failed transfer looks successful to the caller |
| Transaction boundaries and isolation | Whatever the connection defaults to | Concurrent transfers overwrite each other's balance reads |
| Behavior on retry | Retry the call, no key | A timeout becomes a double payment |
| Validation of inputs | Trust the caller | Negative and zero amounts reach the ledger |
| Identifiers | Sequential integers | Identifiers become guessable and leak volume data |
| Rounding | The language's default rounding mode | Pennies accumulate in the wrong direction, consistently |

None of these choices is stupid in general. Floating point is correct for physics and graphics, broad exception handling is reasonable in a batch script, and sequential identifiers are fine for a local cache. They are popular because most published code is not a ledger. The generator is not choosing badly; it is choosing typically, and your domain is atypical.

This is why "the agent made a mistake" is usually the wrong diagnosis, and an expensive one, because it sends you to fix the output instead of the input. In the opening scenario the agent made no mistake. It was asked for a transfer and it produced a transfer, twice, each time filling the unstated parts with the most common pattern available. The float was not an error; it was a default. The missing self-transfer check was not an oversight; it was an unasked question.

There is a corollary worth stating, because it changes how you review. The most dangerous part of a generated file is the part nobody specified, and that part is invisible in a diff. A reviewer reads what is there and judges whether it looks right. What they cannot see is the set of decisions that were never anybody's decision. The only defense I know is to enumerate the decisions in advance, in the document, which is what the failure matrices of Chapter 5 and the gates of Chapter 10 operationalize.

## 2.4 Longer is not better

The natural reaction to everything so far is to write more. That reaction is half right, and the wrong half is expensive, because a language model's effectiveness does not grow linearly with the length of its input.

Three distinct effects work against length. The first is the hard limit: the context window. Everything the generator can condition on — your specification, the source files it was given, its own prior output, the tool results — must fit in a finite budget of tokens. Exceed it and something is dropped or summarized, and you do not choose what. A specification that is too long to fit alongside the code it governs is not a thorough specification; it is a specification that will be partially read.

The second effect appears well before the limit. As the input grows, attention to material in the middle of it degrades measurably, an effect usually called **lost in the middle**. Constraints at the very beginning and the very end of a long input carry more weight than identical constraints buried at forty percent of its length. I treat this as a layout constraint on my documents, not as a curiosity. If a rule is critical, it belongs somewhere the geometry favors, and it may belong in two places. Chapter 8 turns the same observation into a structural principle about giving each agent only the slice of specification its task requires.

The third effect is the one that does real damage, and it is **context poisoning**. Once irrelevant, outdated, or contradictory material is in the context, it conditions every subsequent token. A superseded requirement that nobody deleted does not sit quietly; it competes with the current one. A pasted snippet of a rejected design competes with the accepted design. An obsolete example of a response shape will be reproduced faithfully, because examples are the strongest signal a generator receives, stronger than the prose around them telling it not to. I have watched a single stale code block in an appendix drive three rounds of wrong generation while everyone argued about the prompt.

Context poisoning explains something that confuses teams new to this discipline: adding material to a specification can make the output worse, not merely no better. The mechanism is dilution plus competition. Every token you add reduces the relative weight of every constraint already there, and if the added tokens conflict with those constraints, the generator resolves the conflict by sampling, invisibly. Chapter 11 treats the context as a budget to be managed deliberately, and Chapter 13 catalogs the document-level smells that poison it.

There is a conclusion here that took me a while to accept. Deleting a paragraph from a specification can be an improvement with no compensating addition. Length is a cost, relevance is the good, and the ratio between them is the thing worth measuring.

## 2.5 Constraint Density

That ratio deserves a name, because it is the property I optimize for when I edit a specification. **Constraint Density** is the number of formal constraints a document states divided by the number of tokens it spends stating them:

$$D_c = \frac{\text{formal constraints (types, invariants, preconditions, postconditions)}}{\text{total tokens}}$$

In words: Constraint Density measures how many checkable facts you get per token of context you spend. A Clean Spec maximizes it. The numerator counts only statements that eliminate programs from the output space — a named type, a quantified bound, a stated invariant, an enumerated error, a pre- or postcondition. Encouragement, context, rationale, and politeness contribute to the denominator and nothing to the numerator.

A worked comparison makes the arithmetic concrete. Here is a requirement written in the register most of us were trained to use in ticket descriptions:

> We would really appreciate it if you could take a careful look at the money transfer part of the ledger, which has caused us some trouble in the past and is quite important to the business. Please make sure everything is handled correctly and safely, because this is financial code and our customers depend on it working properly. It would be good if the implementation followed best practices and was written in a clean, maintainable style, with sensible error handling and perhaps some logging so that the operations team can see what is going on. Do try to be careful about amounts and balances, and about what happens when two transfers arrive at roughly the same moment.

That is about 120 words, which is roughly 155 tokens. Count the formal constraints in it and you get zero. Not a low number — zero. There is no type, no bound, no invariant, no named isolation level, no error condition. "Carefully", "safely", "properly", and "best practices" are all unfalsifiable: no test can fail because of them. The paragraph communicates anxiety, and anxiety is not a constraint.

Now the same requirement, rewritten as constraints:

- `Transfer = (source: AccountId, destination: AccountId, amount: Money)`
- `amount.cents` **MUST** be a positive integer.
- `source` **MUST NOT** equal `destination`.
- Source balance `-amount`, destination `+amount`, exactly; no other balance changes.
- Isolation: SERIALIZABLE.
- Repeated `idempotency_key` (UUID): return first result, move no money.
- On failure: no balance changes.

That is about 40 words, roughly 60 tokens, and it states nine formal constraints: the type, the positive-integer bound, the inequality, the two exact deltas, the no-other-change rule, the isolation level, idempotency, and atomicity on failure. The table below compares the two versions on the three numbers that matter.

| Version | Approximate words | Approximate tokens | Formal constraints | Constraint Density |
| :--- | ---: | ---: | ---: | ---: |
| Polite paragraph | 120 | 155 | 0 | 0.00 |
| Dense rewrite | 40 | 60 | 9 | 0.15 |

The dense version is a third of the length and states nine things the long one did not. It is also, and this surprises people, easier to review: a colleague can disagree with line three specifically, which is not a move you can make against "handled correctly and safely". Reviewability and Constraint Density rise together, because both depend on each statement being separately true or false.

Two honest caveats. Constraint Density is a ratio to reason with, not a metric to report in a dashboard; the moment a team starts measuring it, somebody will game it by splitting one constraint into three. And maximizing it does not mean deleting all explanation. A short rationale next to a surprising constraint earns its tokens, because it stops a future reader — or a future agent asked to refactor — from helpfully removing the constraint. What I am against is the preamble that explains nothing and the courtesy that constrains nothing.

## 2.6 Six rules that raise density

These are the edits I make mechanically, in this order, when I tighten a specification. They are numbered so that later chapters can cite them.

**Rule 1: Delete pleasantries and preambles.** Remove "please", "we would like", "it would be good if", and every sentence that describes the business importance of the work. A generator does not work harder on text that says the task matters. Remove background narrative too, unless a specific constraint depends on it. This edit typically removes a quarter of a document and zero constraints.

**Rule 2: One fact per line.** Break compound sentences into single statements, each independently true or false. "Validate the amount and make sure balances stay consistent" is one sentence holding two vague obligations; split it and each half becomes something you can state precisely or discover you cannot state at all. This rule is also the cheapest way to find gaps: a fact you cannot put on its own line is usually a fact you have not decided.

**Rule 3: Tables over paragraphs.** Any content with repeating structure — error conditions, field definitions, state transitions, rate tiers — belongs in a table. Tables are denser per token, they make omissions visible as empty cells, and they resist the drift that creeps into parallel prose. A missing row in a failure matrix is obvious in a way that a missing clause in the fourth sentence of a paragraph never is.

**Rule 4: Name every type.** Replace every bare scalar with a named type carrying its unit and its constraint: `Money` rather than "amount", `AccountId` rather than "the account", `DurationSeconds` rather than "the timeout". A type is the most powerful constraint available, because it applies at every use site without being restated, and because it is checkable by a tool rather than by a reviewer's attention. This is the single edit that most reliably removes float money.

**Rule 5: Number every rule.** Give each normative statement an identifier, so that a review comment, a test name, and a commit message can all point at the same sentence. Unnumbered rules cannot be cited, and uncitable rules cannot be traced to the tests that enforce them. Chapter 10 depends on this rule completely, because its gates are built by transcribing numbered statements into checks.

**Rule 6: Put the most important constraints first and last.** Because of the lost-in-the-middle effect, position carries weight. Open with the invariants that must never be violated and close with the constraints you most expect an agent to forget, and accept the small redundancy of stating something twice when it is genuinely critical. Put narrative, examples, and rationale in the middle, where attention is weakest and the cost of drift is lowest.

Applied together, these six rules typically cut a specification's length by a third to a half while increasing the number of constraints it states. That combination is the whole point: you are not writing less, you are spending fewer tokens on things that do not eliminate programs. Chapter 5 explains why natural language fails at this job in the first place, and Chapter 6 gives you the mixed grammar — Markdown, schemas, diagrams, tables — that makes high density practical to write and pleasant to read.

The engineer in the opening scenario did not need a longer prompt. They needed eight lines. Two runs of eight lines would still have produced two different programs, because sampling is sampling, and Chapter 1 already promised you that a specification narrows the output space without collapsing it to a point. But both programs would have used integer minor units, both would have rejected the self-transfer, and both would have been checkable against the same document. That is the difference between a nondeterministic compiler you have constrained and one you have merely addressed politely.

## Key Takeaways

- A language model computes a probability distribution over the next token conditioned on everything before it, so identical input produces different programs and your text reweights that distribution rather than instructing it.
- The set of programs a generator could plausibly produce from your input is its output space, and specification engineering is the craft of making that space small enough that every remaining member is acceptable.
- Vague words such as "carefully" and "safely" eliminate nothing from the output space, because no test can fail on account of them.
- Whatever your specification leaves unstated is filled with the statistically popular choice in public code, which means float money, swallowed exceptions, default isolation, and retries without idempotency keys.
- Effectiveness does not grow with length: the context window is finite, attention degrades for material in the middle of a long input, and irrelevant or contradictory material poisons every token that follows.
- **Constraint Density** is formal constraints divided by total tokens, and a Clean Spec maximizes it; a 40-word rewrite stating nine constraints beats a 120-word paragraph stating none.
- The six rules that raise density are to delete pleasantries, state one fact per line, prefer tables to paragraphs, name every type, number every rule, and place the most important constraints first and last.
- Deleting text can improve a specification on its own, because length is a cost and only checkable constraints are the good.
