# Chapter 1: The Commoditization of Code

Imagine a Meridian squad with a free weekend and a good idea. Three engineers from the Checkout team want a loyalty feature: customers spend money, earn points, and redeem points at the till. On Friday evening they open a coding agent, describe the idea in a paragraph, and start iterating. By Sunday night there is a running service with a data store, an API, a small admin page, and a demo that survives a live walkthrough on Monday morning. Two years earlier that same weekend would have bought a wireframe and an argument about frameworks.

The feature ships and customers like it. Billing asks for points on subscription renewals. Inventory asks for bonus points on clearance items. Identity asks what should happen to points when two accounts merge. Each request becomes another conversation with the agent, another patch, another green deployment.

Three months later the squad has a different relationship with the service. Every change breaks two things. Fixing the account-merge case quietly re-enables expired points. Adding renewals makes refunds award points twice. The squad writes a test after each incident, the tests pass, and the next change breaks something no test covered.

Then somebody in a review asks the question that ends the meeting: what does this service actually guarantee? Three answers are available, and none of them is a guarantee. You can read the code, which tells you what happens today and says nothing about what is allowed. You can ask the agent, which will produce a confident summary of code it is reading for the first time. You can read the tests, which assert whatever the implementation did on the day each one was written. Somebody asks why the redemption hold expires after sixty seconds, and the only honest answer is that a chat log said so, and the chat log is gone.

None of this is a typing failure, and none of it is carelessness. The squad produced a large amount of working code very quickly, and that was never the problem. The weekend was not the mistake either. The mistake was believing that the weekend had produced an engineering artifact, when what it produced was output. This chapter is about why that distinction suddenly matters so much, and why it did not matter nearly as much before.

## 1.1 Four leaps in abstraction

The history of software engineering is the history of raising the level of abstraction. Each major leap took an activity that consumed human attention and turned it into a subprocess that a machine performs reliably. It helps to look at the leaps together, because they share a shape, and the shape tells you what to expect from the one we are living through.

The table below lists four transitions, what each one automated, and which artifact engineers were left writing by hand afterward.

| Transition | What got automated | What became the primary artifact |
| :--- | :--- | :--- |
| Machine code to assembly | Manual translation into numeric opcodes, and hand-computed addresses | The symbolic assembly listing |
| Assembly to compiled procedural languages (Fortran, C) | Register allocation, call-stack layout, instruction selection | The procedural source file |
| Procedural to managed object-oriented languages (Java, C#, Python) | Memory lifecycle, bounds and type checking, dispatch tables | Class and interface definitions |
| Traditional programming to spec-driven agentic engineering | Translating intent into syntax: writing the statements themselves | The specification: contracts, invariants, failure modes |

Read the third column downward and you see the real story. Every leap moved the artifact that engineers author up one level, and every leap turned the previous artifact into something you can still read but no longer write. I can read the assembly a compiler emits. I have read it to chase a performance problem, and I expect to read it again. I have not authored a line of it in twenty years, and nobody on my teams checks it into version control.

Each of these transitions also arrived with the same objection, and the objection was never silly. Assembly programmers pointed out, correctly, that early compilers produced worse code than a careful human. Procedural programmers pointed out, correctly, that garbage collection introduced pauses they could not control. In both cases the critics were right about the immediate quality and wrong about the trajectory. The automated layer improved, the cost of not using it grew, and the argument ended not because anyone won it but because the generation that cared had moved on to harder problems.

There is a second pattern worth naming. Each leap did not reduce the total difficulty of building software; it relocated the difficulty. When register allocation stopped being your problem, data structure design became your problem, because you were now writing programs large enough for data structures to matter. Automation at one level exposes the next level's mistakes, and those mistakes are always more expensive, because they are mistakes about intent rather than mistakes about mechanism.

The fourth row is where we are now, and it differs from the first three in one important respect. The earlier leaps automated mechanical translation, where the correct output was determined by the input. This one automates the step where meaning is decided: turning a human idea into precise behavior. That is not a mechanical step, which is why the rest of this book exists.

The difference shows up in what "correct" means for the automated layer. A compiler is correct when its output preserves the semantics of the input, and the input has semantics, defined by a language standard that a committee spent years arguing over. When you hand a generator a paragraph of English, there is no semantics to preserve, because English sentences about software do not have one. What you are really asking for is a behavior consistent with your sentences, and a paragraph of English is consistent with an enormous number of different behaviors. That gap is where every problem in this book lives, and closing it is the whole job.

## 1.2 Source code as intermediate representation

If an inference engine turns a description of required behavior into running code, then conventional source code has changed category. Python, TypeScript, Go, and Rust files are no longer the original artifact. They are an **intermediate representation**: a lower-level form, produced from something else, that happens to be the form your runtime consumes.

I want to be precise about what "intermediate" does and does not mean here, because the word invites a misreading. It does not mean unimportant, and it does not mean disposable. The intermediate representation is the thing you deploy, profile, and get paged about at three in the morning. Compiler output is also the thing that actually runs, and we take it extremely seriously. "Intermediate" means only that it is derived: it is downstream of a more authoritative document, and when it disagrees with that document, it is the code that is wrong.

The engine producing it is a large language model (LLM), and from here on I will call it a language model. For the purposes of this chapter, what matters is the role it plays rather than how it works, and the role is best named directly: it is a **nondeterministic compiler**. It consumes a description in natural language and emits code, which is what a compiler does. Everything else about it violates what we expect from compilers. Run it twice on the same input and you get two different programs, both plausible, sometimes differing in behavior you care about. It has no language standard, no reference semantics, and no errata list. Where a conventional compiler rejects what it cannot interpret, this one interprets everything, because producing output is the only thing it knows how to do.

The missing errata list is worth dwelling on, because it breaks a habit you rely on more than you notice. When a conventional toolchain miscompiles something, the bug has an identity: a number, a report, a version where it appears and a version where it is fixed, and a workaround you can write down and hand to the next person. A generator that makes a poor choice offers none of that. There is no defect to file, because nothing was violated; the output was one valid sample from a distribution that also contains better ones. You cannot fix it upstream, and you cannot rely on it not recurring. All you can do is change the input or check the output, which is a strong hint about where the engineering work has gone.

That last property is the one that reshapes the work. A conventional compiler treats silence in your source as a syntax error: omit the return type, and it either infers it by documented rules or refuses to proceed. A nondeterministic compiler treats silence as permission to choose. Omit what happens when the amount is zero, and you will get a choice, made from the statistical habits of an enormous amount of public code, and that code stores money in floating-point numbers and swallows exceptions. Your specification's gaps are not questions waiting to be asked. They are delegated decisions, and you will not be told which ones you delegated.

Consider what determinism was actually buying us. Compiler correctness is verified once, by the compiler's authors, for all programs. You do not test whether your compiler allocated registers correctly for your function; you test your function's logic and trust the translation. That trust is an enormous, invisible subsidy on every project, and a nondeterministic compiler withdraws it. Verification of the translation moves to you, and it moves per program, per feature, per run.

There are only two coherent responses to that withdrawal, and this book is about both. The first is to make the input carry enough constraints that the space of acceptable outputs is small, which is the property Chapter 2 defines and names. The second is to verify every output mechanically against the same document that produced it, which is what Chapter 10 builds. What you cannot do is treat the generated code as the authority and patch it by hand when it misbehaves. That move feels like engineering and is the single most expensive habit in this whole field; Chapter 4 gives it a name and a rule.

One more consequence deserves saying plainly. If code is an intermediate representation, then reading generated code remains a core skill and stops being the place where your judgment is most valuable. I read compiler output to diagnose, not to decide. You will read generated code the same way: to confirm that a contract holds, to find out why a gate failed, to understand a performance profile. The decisions live upstream, in the document the generator read.

## 1.3 The vibecoding curve

Vibecoding is the name that stuck for the informal practice: conversational prompts, untracked iteration, and verification by looking at the screen and deciding it seems to work. I use the word without contempt, because I do it too, and because it is genuinely the fastest path to a certain kind of answer. What I object to is not the practice but the belief that the curve it sits on keeps its shape.

The curve has two regimes. Below roughly a thousand lines, or inside a single domain with no real invariants, perceived productivity climbs steeply and the climb is not an illusion. You are getting real working software for a marginal fraction of what it used to cost. Past the toy threshold, which I would put somewhere past five thousand lines or the moment two application domains start interacting, the trend inverts. The absence of stated boundaries produces entropy, and the entropy compounds, because each fix is made by an agent that has no statement of global truth to check itself against. This is the regime where fixing one bug introduces two invisible regressions, and where the squad in the opening scenario spent its third month.

The draft chart below is the one I keep redrawing on whiteboards. The rising line is the informal approach, the flat line is the disciplined one, and the interesting part is where they cross.

```
Cost
  ^
  |                                   / Informal approach (vibecoding)
  |                                  /  Verification cost: O(N^2)
  |                                 /
  |                                /
  |                               /
  |                              /
  |-----------------------------/------------------------
  |                            /      Clean Spec approach (SDD)
  |                           /       Constant verification cost: O(1)
  |                          /
  +-------------------------------------------------------> System complexity (N)
```

Now the two claims in words, because notation that nobody unpacks is decoration. The cost of generating code is roughly constant per feature, written $O(1)$: the fiftieth feature costs about what the first one cost, because the generator's effort does not grow with the size of your system. That flatness is exactly why the early regime feels so good, and it is also the trap, because generation is the cheap half.

The second claim is about the other half. Without a written specification, the cost of verifying a change grows with the square of the number of implicit invariants in the system, written $O(N^2)$, where $N$ counts the rules that everyone assumes and nobody has recorded. The reason is combinatorial rather than mysterious. With $N$ unstated assumptions there are $N(N-1)/2$ pairs of them, which grows like $N^2$, and every pair is a place where satisfying one assumption can violate the other. Points expire after ninety days; merged accounts inherit balances. Each rule is obvious alone. Together they decide whether a merge resurrects expired points, and nobody has ever written down which answer is correct.

That is why verification cost, not generation cost, sets the pace of a mature system. Checking a change against an unwritten rule means reconstructing the rule first, from code and memory and whoever is still on the team, and then doing it again for the next pair. The work is invisible in planning, lands as incident response, and scales badly with exactly the thing that makes a system valuable, which is the number of rules it enforces.

A written specification flattens the curve because each stated invariant becomes independently checkable. Write down "expired points are never restored by an account merge" and it stops being one half of an unexamined pair. It becomes a sentence a reviewer can object to, a test that runs on every commit, and a constraint the agent reads before it generates. You still pay to state the rules, and that cost grows with the size of the domain. What you stop paying is the multiplicative cost of rediscovering the interactions, which is the term that was eating your quarter.

Trace the opening scenario along the curve and the months stop looking like bad luck. The weekend sat far to the left, where the squad had one domain, no interactions, and perhaps three implicit rules, so there was nothing to rediscover and the informal approach was the correct choice. Renewals, clearance bonuses, and account merges did not add three features; they added three domains touching a balance, and the count of implicit rules went up along with the count of pairs between them. By the third month the squad was spending most of its effort in the quadratic term, which is why the work felt heavier while the features got smaller. Nobody chose that; they simply crossed the line without a reason to look up.

I should be honest about the notation. These are shapes, not measurements, and I have never seen anyone instrument a codebase and recover a clean quadratic. The useful content is the relationship: one curve is flat in the variable that grows, the other is not, so any fixed comparison between them expires. Which brings us to the crossing point, which is the most practical thing in the chart. To the left of it, informal work really is cheaper, and a team that specifies a weekend prototype is wasting its weekend. To the right of it, the gap widens every month, and a team that keeps prompting is not saving time but borrowing it.

## 1.4 The only artifact with positive cognitive return

If synthesizing code is a commodity, engineering value moves upstream into four activities: clarifying what is required, modeling the domain and its invariants, enumerating what can go wrong, and fixing the contracts at interface boundaries. None of those produce code. All of them produce a document, and that document is now the expensive thing in the pipeline.

Those four deserve a second look, because they are not a list of phases and they are not equally familiar. Clarifying requirements is the one everybody claims to do and almost nobody finishes, since a requirement is only clear when a reasonable reader cannot produce two behaviors from it. Modeling invariants means writing the sentences that must be true before, during, and after every operation, which is the skill Chapter 3 borrows from Hoare logic. Enumerating failures means listing what goes wrong and what the system owes the caller in each case, before you have written the path where nothing goes wrong. Fixing contracts at boundaries means deciding what each side of an interface may assume, which is the part that survives longest and gets written down least.

I call the property that document has **positive cognitive return**. An artifact has positive cognitive return when the thinking you invest in it keeps paying after the occasion that prompted it, and keeps paying to readers who were not in the room. The test is simple: a year from now, does this artifact still answer questions, or does it only record answers that have since been overwritten? Most of what a software team produces fails that test, and it is worth walking the inventory.

Code depreciates, and it depreciated before any of this. It rots against its dependencies, it gets rewritten when the platform moves, and it answers "what happens" while staying silent on "what is allowed". Now it also costs almost nothing to reproduce, which finishes the argument: an artifact you can regenerate in an afternoon is not where your accumulated thinking should live.

Tests are the interesting case, because teams treat them as the durable record and they usually are not. A test written after the fact asserts what the code did on the day somebody observed it, which makes it a photograph of an implementation rather than a statement of intent. Such tests pass while the system is wrong and fail when the system is correctly changed. A test derived from a written rule is a different animal entirely, which is why Chapter 10 insists that tests are derived, not invented.

Conversations and tickets score worst of all. A chat log containing the reasoning behind a sixty-second window has a useful life measured in days: it is unsearchable, unreviewable, unversioned, and frequently deleted by a retention policy nobody chose. A ticket describes intent in the vocabulary of a hallway conversation and closes, and closing it is precisely the moment its content stops being maintained.

A specification written to a strict standard is the one artifact in that inventory whose value compounds. It outlives any particular generator, because it constrains behavior rather than phrasing, and it can be handed to a different agent next year without rewriting a word. It produces tests, because a stated invariant and a failure table are test definitions that only need transcribing. It answers the review question that ended the meeting in the opening scenario, in one place, in language a person can argue with. And it is the artifact a new engineer should read first, because it is the only one that distinguishes a decision from an accident.

There is a harder benefit that I value more than any of those. Writing a specification forces the disagreement to happen before the code exists. The question of whether a merged account inherits expired points has exactly one cheap moment in its life, and that moment is while two people are looking at a sentence neither of them has agreed to yet. Everywhere after that, the same question costs an incident. Keeping a specification readable while it accumulates that kind of detail is a structural problem, and Chapter 7 solves it with three levels.

<!-- AUTHOR: a real case where a written invariant paid for itself years later, ideally one where the original authors had all left the team, would close this section better than the loyalty-points example; needs the domain, the invariant, and what the later change would have broken. -->

## 1.5 What this book does not claim

Arguments like the one I have just made attract enthusiasm that I do not want. Three limits are worth stating flatly, before the rest of the book commits itself to the method.

First, agents produce wrong code from good specifications. This happens constantly, and it is not a transitional problem that better generators will eliminate. A nondeterministic compiler will misread a clause, satisfy eleven constraints and drop the twelfth, or generate something that passes every example you thought to give and fails the case you did not. A specification narrows the output space; it does not collapse it to one program. That is the entire reason Part III exists, and why every change in this discipline passes mechanical gates before a human reads it. If you take the method and skip the gates, you have swapped an unreviewed prompt for an unverified document and gained nothing.

Second, a specification does not replace engineering judgment. Deciding that expired points must never be restored by an account merge is not clerical work; it is a domain decision with revenue and support consequences, and no document template will make it for you. Judgment does not disappear under this discipline, and it does not diminish. It moves upstream, from choosing how to implement behavior to deciding what behavior must be guaranteed, which was always the part that deserved senior attention and rarely received a full share of it. If anything, this method is more demanding of judgment, because it removes the option of deferring the hard question until the code forces it.

Third, the discipline has a real cost, and below a certain size it does not pay. Writing contracts, enumerating failures, and closing state machines takes hours that could have produced running code. For a thirty-line script, a one-off data migration, or a spike whose purpose is to find out whether an approach is viable at all, that trade is bad and you should not make it. Go back to the crossing point in the chart: its existence is an argument for specifying, and equally an argument for not specifying to the left of it. Chapter 4 is explicit about where the line falls and about the honest exceptions.

I will add a fourth limit that is less about modesty and more about scope. Nothing in this book is prompt engineering. I name no generator, and I have deliberately avoided techniques that depend on one, because a specification has to outlive the thing that reads it. If a practice stops working when a generator is updated, it was never an engineering practice.

What remains after those subtractions is still, I think, the most important shift in the economics of our craft that I have seen. The cheap part of building software is now writing it. The expensive part is knowing precisely what it must do, and recording that knowledge in a form that a person can review and a machine can consume. We have a century of accumulated craft for the part that became cheap, and almost none for the part that became the bottleneck. The vocabulary for the second part, which is the vocabulary of smells and refactorings that Chapter 13 and Chapter 14 catalog, is what this book is trying to supply.

## Key Takeaways

- Every leap in abstraction automated a mechanical step and moved the artifact engineers author up one level; spec-driven agentic engineering moves it to the specification.
- Conventional source code is now an intermediate representation: still deployed, still read, but derived from a more authoritative document.
- A language model acting as a generator is a nondeterministic compiler, with no reference semantics and no way to reject an ambiguous input.
- Silence in a specification is not a question waiting to be asked; it is a decision delegated to the statistical habits of public code.
- Generation cost is roughly constant per feature, while verification cost without a written specification grows with the square of the number of implicit invariants, because every pair of unstated assumptions can interact.
- A specification has positive cognitive return: it outlives any generator, produces tests, and records decisions rather than their consequences.
- Agents still produce wrong code from good specifications, so the method is worthless without mechanical gates.
- The discipline costs real hours and only pays beyond toy size, so specify to the right of the crossing point and prototype freely to the left of it.
