# Chapter 5: The Failure of Natural Language

Picture a Tuesday afternoon at Meridian when a product manager drops one sentence into a shared document and calls the requirement done: "The user must receive a notification if the payment succeeds, unless they have disabled alerts." Sixteen words, no jargon, nothing a reasonable adult could object to. Three engineers pick up related tickets that sprint, and a coding agent gets the same sentence as its starting brief for a fourth surface. All four treat the sentence as sufficient, because it reads as sufficient.

The Checkout engineer is building the web till confirmation and ships it as an SMS, because Checkout's customers are mobile shoppers and SMS is what the team already has wired up. The Billing engineer is building the subscription-renewal receipt and queues it onto an existing background worker with no delivery deadline, so receipts usually arrive within a minute and occasionally arrive two days later, behind a backlog nobody is watching. The Identity engineer owns the preferences screen that "disabled alerts" must be reading, and wires the checkbox to the same flag that already suppresses marketing email, because that is the flag that exists. The agent, prompted for a new internal reconciliation tool, reads "unless they have disabled alerts" as a condition on the whole operation and writes code that rolls back the payment itself when the notification call times out, on the reasoning that an operation with an unmet condition should not be considered to have succeeded.

At the joint demo, the four implementations disagree with each other in every direction that matters. A customer who opted out of marketing mail gets no receipt at all, though they never asked to lose that one. A customer with no SMS number gets nothing from Checkout. A subscription receipt lands during a support call about a renewal the customer swears never happened. And once, in staging, a slow notification provider takes down a completed payment along with it.

Nobody misread the sentence. Every one of the four readings is a defensible parse of exactly what it says. That is the actual defect, and it is not a defect this team can review its way out of by reading the sentence more carefully, because there is nothing wrong with the sentence at the level where careful reading operates.

## 5.1 Why natural language works for people and fails for compilers

Ordinary English is not a broken specification language. It is an extremely good communication protocol, tuned by use for a purpose that has nothing to do with generating code. It is optimized for two people who already share a great deal: a common situation, a common vocabulary shaped by common experience, and — this is the part that matters here — the ability to ask each other what they meant. A sentence like "the user must receive a notification" works between two Meridian engineers in a hallway because one of them can immediately say "which channel?" and get an answer in three seconds. The sentence was never carrying the whole meaning. The conversation was.

Linguists call the part the sentence does not carry implicature, and human listeners fill it in constantly, often without noticing they have done it. Ask a colleague to "notify the user" and they will silently assume the channel the team already uses, the timing the team already expects, and the exceptions the team has already argued about twice. None of that assumption is wrong. It is the entire reason natural language is efficient enough for two people to build a shared plan out of sixteen words instead of four hundred.

A language model reading the same sentence has none of that shared situation, and — this is the operative difference — no way to get it during generation. Chapter 2 described what a model does with an ambiguous instruction: it does not detect the gap and refuse; it resolves the gap by sampling from whatever pattern was statistically dominant in its training data and commits to one reading, silently, as if it were the only reading available. A human reader who is uncertain can pause and ask. A generator produces an artifact. The uncertainty does not surface as a question. It surfaces as a decision nobody remembers making, embedded in sixty lines of working code that passes review because nothing about it looks wrong.

The second difference compounds the first. Two people who each fill an ambiguous instruction from shared context tend to converge, because the shared context is the same context. Two runs of a generator filling the same instruction from a statistical prior are not guaranteed to converge at all, because the sampling is not required to land on the same plausible reading twice. Chapter 1 called this the central fact of working with a nondeterministic compiler. Here is its sharpest consequence: the same requirement sentence, handed to the same agent on two different days, can produce SMS delivery once and email delivery the next time, and both outputs will look like reasonable software. A specification that depends on natural-language inference to fill its gaps is not merely imprecise. It is unstable in a way that has nothing to do with anyone's competence.

None of this is an argument that natural language is a bad tool. It is the best tool ever built for the job it was built for. The argument is narrower and harder to dismiss: the job of instructing a probabilistic generator that cannot ask a follow-up question is not that job, and pretending otherwise is where the notification sentence went wrong for four different people in four different and equally reasonable ways.

There is one more asymmetry worth naming, because it explains why the failure is so easy to miss during review. A human reader who fills a gap from shared context usually fills it correctly, because the shared context is real and current. A reviewer skimming the notification sentence has the same shared context the writer did, so the sentence feels complete to both of them, and it will keep feeling complete right up until a generator, with none of that context, fills the same gap from a different and much larger distribution: every notification system that ever appeared in its training data, weighted by frequency rather than by relevance to Meridian. The sentence was never ambiguous to the people in the room. It was only ever ambiguous to the reader who was never in a room, and that reader is the one who ends up writing the code.

## 5.2 A taxonomy of ambiguity

It helps to have names for the ways a sentence can fail, because "vague" is too blunt a diagnosis to fix anything. The table below names six kinds, and the notification sentence that opened this chapter turns out to contain an example of every one of them at once, which is less an indictment of that sentence than a demonstration of how ordinary this failure is.

| Kind | What is left open | Where it appears in the sentence |
| :--- | :--- | :--- |
| Lexical | A word has more than one accepted meaning | "Notification" — push, email, SMS, and an in-app banner are all correct dictionary readings |
| Syntactic | The grammar admits more than one parse | "Unless they have disabled alerts" can attach to "receive a notification" (suppress delivery) or to the entire conditional (treat the payment itself as unresolved) |
| Scope | How far a qualifier reaches is undefined | Does "disabled alerts" suppress this one receipt, or every notification this transaction could ever trigger, including a refund receipt three weeks later? |
| Referential | A pronoun or phrase has more than one plausible antecedent | "They" — the person who initiated the payment, or the account owner, when a shared corporate card or a guest checkout makes the two different people |
| Temporal | Timing is left unstated | "Must receive" — synchronously with the payment call, within the same request, or at some point before end of day? |
| Quantifier | Words like "a," "any," or "all" leave cardinality open | "Disabled alerts" — any single alert category, or every category the account offers? |

Two things about this table are worth sitting with. First, none of the six ambiguities is a sign of a careless author; a product manager who wrote a sentence free of all six would have written something closer to a legal contract than a ticket, and nobody wants tickets written that way. Second, the six are independent: resolving the lexical ambiguity of "notification" by picking a channel says nothing about the temporal ambiguity of "must receive," and a spec review that catches one and declares victory will still ship the other five.

The taxonomy is a diagnostic tool, not an exercise. When you read a requirement sentence and it feels fine, run it against these six columns before you believe your own comfort with it. Comfort with a sentence and precision of a sentence are unrelated properties, and the notification sentence had plenty of the first and none of the second.

Use the table the way a reviewer uses a checklist rather than the way a student passes an exam. You do not need a name for every ambiguity you remove; you need the habit of checking all six columns before you sign off on a sentence, because a reviewer who only ever notices lexical ambiguity — the kind that is easiest to spot, since it usually involves one obviously overloaded word — will wave through temporal and referential gaps every time, and those are the two that produced the two-day-late receipt and the rollback bug in the opening scenario, not the channel confusion that was easiest to see.

## 5.3 RFC 2119 and RFC 8174 vocabulary

One of the six kinds deserves special attention because it has a standard, off-the-shelf fix. Ordinary English modal verbs — must, should, may, will, can — carry obligation strength so inconsistently that "the system should notify the user" can mean a firm requirement, a soft preference, or a prediction about future behavior, depending on who wrote it and how they were feeling. IETF engineers hit the identical problem writing protocol documents in the 1990s and solved it once, in RFC 2119: a fixed vocabulary of keywords, each with one meaning, used consistently across every specification that adopts the standard.

| Keyword | Meaning |
| :--- | :--- |
| MUST / SHALL | An absolute requirement of the specification |
| MUST NOT / SHALL NOT | An absolute prohibition |
| SHOULD / RECOMMENDED | A recommendation; valid reasons may exist to deviate, but the full implications must be understood and weighed before choosing to |
| SHOULD NOT / NOT RECOMMENDED | The inverse recommendation; the same weighing applies before permitting the behavior |
| MAY / OPTIONAL | A genuinely discretionary feature; no caller may assume its presence, and none may assume its absence |

RFC 8174 closed the one gap RFC 2119 left open: nothing in the original document said what happens when the same word appears in lowercase. Writers noticed, and started hedging with lowercase "must" when they meant something softer than the uppercase keyword, which reintroduced exactly the ambiguity the vocabulary was built to remove. RFC 8174 fixes this with a rule and a sentence every Clean Spec should carry near its top:

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119 and RFC 8174, when, and only when, they appear in all capitals, as shown here.

The uppercase rule is not a stylistic quirk. It is what makes the vocabulary load-bearing: a reader or a generator can scan for capital letters and know, without inferring tone or context, exactly which fifteen-word promise a sentence is making. Lowercase "must" is prose again, with all of prose's ambiguity intact. This is also why a Clean Spec's normative statements are bolded in this book's examples, per the convention Chapter 9 fixes for the whole manuscript: the keyword is the part of the sentence doing the legal work, and it should be visually impossible to skim past.

Adopting RFC 2119 resolves exactly one of the six kinds of ambiguity from 5.2. It says nothing about which channel "notification" means, nothing about whose preferences govern the exception, nothing about timing. What it buys is narrower and still essential: once you have decided that something is required, the vocabulary guarantees that "required" survives the trip from your head to the reader's, human or otherwise, without degrading into a suggestion along the way.

## 5.4 Rewriting the sentence

Put the taxonomy and the vocabulary to work on the sentence that started this chapter. The exercise is not stylistic polish; it is the mechanical process of walking each of the six ambiguities to a decision and writing the decision down as a numbered, keyword-bearing statement. What follows is an excerpt from the normative constraints section of `SPEC-PAY-042`, the specification Chapter 6 assembles in full.

### SPEC-PAY-042: Transaction Confirmation Notifications

#### 1. Normative Constraints

- N-1: Upon a transaction reaching `SETTLED` status, the system **MUST** enqueue a notification event within 2 seconds.
- N-2: Notification dispatch **MUST NOT** block or fail the payment transaction that triggered it.
- N-3: The default delivery channel **MUST** be email, sent to the address on the paying customer's account; the system **MAY** additionally deliver by SMS or push notification if that customer has separately opted into that specific channel.
- N-4: If the paying customer's `preferences.notifications.transaction_receipts` field is `false`, the dispatcher **MUST** suppress delivery on every channel for that event and **MUST** record an audit entry with status `SKIPPED`.
- N-5: If a delivery attempt fails for any reason other than a suppressed preference, the system **MUST** retry according to the retry policy in §6; a delivery failure **MUST NOT** cause the settled transaction to be reversed.

Read the five statements against the four questions the original sentence left open, because each one is answered by exactly one clause. The lexical ambiguity of "notification" is gone: N-3 names email as the default and states the exact condition under which another channel is added, closing the quantifier question of "which channels" at the same time. The temporal ambiguity of "must receive" is gone: N-1 puts a two-second bound on enqueueing and N-2 fixes it as asynchronous with respect to the payment call, which also settles the syntactic question of what "unless" was allowed to reach — nothing here can unwind the transaction. The referential and scope ambiguity of "they" and "disabled alerts" is gone: N-4 names the exact preference field, `transaction_receipts`, rather than a general alerts toggle, so Identity's preferences screen has one unambiguous flag to read instead of a shared marketing switch that happens to be nearby. And N-5 answers a question the original sentence never addressed at all: a delivery failure is retried, not treated as a reason to distrust a settled payment.

Five clauses, numbered `N-1` through `N-5` so that a review comment, a test, or a bug report can cite one of them by name — Chapter 9 fixes that convention, along with `P-`, `Q-`, and `I-` from Chapter 3, for the rest of this book. Under a hundred words longer than the sentence it replaces, and every one of the four implementations from the opening scenario becomes impossible to write correctly without contradicting something on the page.

## 5.5 Common misuses

Adopting the vocabulary does not immunize a document against misuse, and four mistakes account for nearly everything I see go wrong in spec reviews.

**SHOULD as a polite MUST.** An engineer means "this is required," feels that MUST sounds harsh toward a colleague who will implement it, and writes SHOULD instead. The softening is generous and it is a lie the vocabulary was built to prevent. A reader, or an agent under time pressure, is entitled to treat SHOULD as something it may skip for a documented reason, and it will. If noncompliance would be a bug you'd block a release over, the word is MUST, and manners belong in the pull request comment, not in the requirement.

**MAY for an undecided question.** A writer does not yet know whether a feature is wanted and reaches for MAY, because it sounds like the tentative word. It is not. MAY means the behavior is a genuine implementation choice that no caller may depend on either way, which is a much stronger and much more specific claim than "we have not decided." An undecided question is not a MAY clause. It is an Open Question, which Chapter 9 makes a mandatory section precisely so that unresolved decisions have a place to be honest about themselves instead of hiding inside a keyword that means something else.

**"Will."** Plain future tense reads like an obligation and is not one; it is a prediction. "The system will notify the user" describes an expected outcome, the way a weather forecast describes rain, and it carries none of RFC 2119's defined force because it is not one of the defined words. I see this most often when a writer is translating from a design conversation into a document and keeps the conversational tense without noticing that the translation dropped the obligation on the floor.

**The negated SHOULD.** SHOULD NOT is not MUST NOT with a softer tone; it permits the behavior when there is a documented reason and a weighed consequence, exactly as SHOULD permits deviation in the other direction. Writers reach for "should not" when they mean an absolute prohibition and get a recommendation instead. If the behavior must never happen, the sentence needs MUST NOT, full stop, and no amount of surrounding emphasis substitutes for the correct keyword.

All four mistakes share one root cause: the writer is still thinking in the register of a conversation with a trusted colleague who will infer the intended strength from context, tone, and the relationship. That register is the one 5.1 described as excellent for its purpose and unusable for this one.

## 5.6 Beyond modal verbs: quantify everything

RFC 2119 fixes the strength of an obligation. It does nothing for the five other kinds of ambiguity in 5.2's table, and the most common way those five survive into a "clean-looking" specification is through a word that sounds precise and is not: an adjective or adverb with no number behind it.

"Quickly" is not a time bound; "within 200 milliseconds at the 95th percentile" is. "A few retries" is not a retry policy; "at most 3 attempts, with exponential backoff starting at 500 milliseconds" is. "A large withdrawal" is not a threshold; "an amount of 10,000.00 USD or more" is. "Recently" is not a window; "within the preceding 24 hours, UTC" is. Each pair says roughly the same thing to a person skimming for meaning and something entirely different to a generator asked to implement it, because only the second half of each pair removes a decision from the output space rather than describing one loosely enough to fit several.

The discipline is to treat every number, unit, time bound, and cardinality in a requirement as mandatory rather than as a detail to add later during implementation. "Later" is exactly when the decision gets made by sampling instead of by you, which is Chapter 2's argument about defaults applied one level down: a specification with unquantified magnitudes has the same failure mode as one with unquantified obligations, just spread across adjectives instead of modal verbs. Every quantity you write down is one more thing a nondeterministic compiler no longer has to guess, and Chapter 2's Constraint Density is precisely the ratio of how many of those you have written down against how many tokens it took.

This is also where the taxonomy in 5.2 earns its keep as more than a classification exercise. Read a draft sentence and ask, for each of the six kinds: is there a number, a name, or a keyword here that closes this particular gap, or is there an adjective standing in for one? "Fast," "large," "recent," and "several" are the words that taxonomy exists to catch, and every one of them, left in a specification, is a silent instruction to guess.

Resolving obligation strength and quantifying every magnitude gets a sentence most of the way to unambiguous, and it is still only prose. `N-1` through `N-5` say what must be true; they say nothing about the exact shape of the notification payload, and nothing about the sequence of states a delivery attempt moves through on its way to `Delivered` or a dead letter queue. Prose is the wrong tool for both of those jobs, for reasons Chapter 6 takes up next: some of what a specification needs to say is not a sentence at all.

## Key Takeaways

- Natural language is optimized for two people who share context and can ask each other follow-up questions; a generator has neither, so it resolves ambiguity by sampling a default instead of asking, silently and possibly differently each time.
- Six independent kinds of ambiguity — lexical, syntactic, scope, referential, temporal, and quantifier — can all live inside one ordinary-sounding sentence at once, and resolving one says nothing about the other five.
- RFC 2119 and RFC 8174 fix exactly one of those kinds: obligation strength. MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY each carry one defined meaning, and only when written in uppercase.
- The four recurring misuses are SHOULD written to soften a real MUST, MAY written to avoid an undecided question that belongs in Open Questions instead, "will" mistaken for an obligation when it is only a prediction, and SHOULD NOT mistaken for an absolute prohibition.
- Quantify every magnitude — numbers, units, time bounds, cardinalities — because an adjective like "quickly" or "a few" reintroduces exactly the ambiguity the modal vocabulary was built to remove, one level down.
- Numbering normative statements as `N-1`, `N-2`, and so on makes each one citable by a review comment, a test, or a bug report, the same way Chapter 3 numbers preconditions, postconditions, and invariants.
- A sentence with no unresolved ambiguity is still only prose, and prose cannot state a payload's exact shape or a process's exact sequence of states as precisely as a schema or a diagram can.
