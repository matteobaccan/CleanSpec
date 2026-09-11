# Chapter 12: Specs Under Version Control

Imagine it is two in the morning and the on-call engineer for Meridian's Accounts team is staring at a page: withdrawals are occasionally succeeding twice against the same account within the same UTC day, just past the daily-limit boundary. A quick read of the code shows the bug immediately — the limit check compares timestamps with a boundary condition that lets exactly one extra withdrawal through in the sixty-second window around midnight UTC rollover. The fix is a one-line comparison change. The engineer makes it, deploys it, watches the page clear, and goes back to sleep. `SPEC-ACCT-003`, sitting in `specs/modules/accounts/`, is not open in any editor at any point during this sequence. Nothing about it changes.

Three weeks later, a different engineer picks up an unrelated ticket — the fraud-suspension outcome from Chapter 7 — and asks a coding agent to regenerate the withdrawal module against the current specification, because the module needs a new branch for the `SUSPENDED` result and regeneration is the normal way that happens. The agent reads `SPEC-ACCT-003` faithfully, finds no mention of a midnight boundary condition anywhere in it, and produces a correct implementation of the document exactly as written — which silently drops the two-in-the-morning fix, because nothing told the agent it existed. The bug returns to production a month after it was fixed, and the engineer who fixed it the first time has no idea it happened, because nobody thought to connect a regeneration ticket about fraud suspension to a boundary condition in an unrelated corner of the same file.

This is not a story about carelessness on anyone's part. The on-call fix was the right call at two in the morning, exactly as Chapter 4 already conceded. The regeneration was performed correctly, against the only source of truth anyone told the agent to trust. The failure is structural: a specification and its code drifted apart, nothing recorded that they had, and the drift became invisible the moment enough time passed for anyone to forget it by memory alone. Chapter 4 named the condition — spec drift — and promised this chapter would show how to detect it mechanically, because Chapter 4 was right that human attention has a perfect record of failing to.

## 12.1 Spec commits and implementation commits

Under Spec-Driven Development, a repository's commit history changes shape, because the two halves of Chapter 4's pipeline — the specification and the code derived from it — are authored by different parties and belong in different commits, linked rather than merged.

```
commit a1b2c3d4
Author: Software Architect <architect@meridian.example>
Date:   Thu Sep 10 14:00:00 2026

    spec(billing): formalize tiered subscription upgrade invariants

    - Add JSON schema for UpgradeSubscriptionCommand
    - Define state transition from TRIAL to PRO in Mermaid
    - Add failure modes: ERR_CARD_DECLINED, ERR_ALREADY_ACTIVE
    - Reference: SPEC-BILL-017 v1.0.0
```

```
commit e5f6g7h8
Author: Coding Agent <agent-ci@meridian.example>
Date:   Thu Sep 10 14:02:15 2026

    impl(billing): synthesize subscription upgrade use case from spec a1b2c3d4

    - Generated unit and property-based tests (spec coverage: 100%)
    - Implemented SubscriptionService.upgrade()
    - Static analysis: passed (mypy --strict: 0 errors)
```

The two commits are not a formality. The first is authored by a human, changes only files under `specs/`, and is the commit a reviewer actually argues about — whether the invariant is right, whether the failure modes are complete, whether the state transition matches what the business wants. The second is authored by the agent, changes only files under `src/` and `tests/`, cites the first commit's hash directly, and is the commit CI verifies mechanically against the Three Gates. Splitting them this way means a reviewer with an opinion about the business rule reviews exactly the commit that states it, without wading through generated code to find the one paragraph that matters, and a reviewer checking that the code actually implements the rule can diff the second commit against the first commit's clauses one by one.

The pairing is also what makes the on-call fix's failure visible in retrospect, once the rest of this chapter's tooling is in place. A specification commit with no corresponding implementation commit is unusual but not alarming — someone drafted ahead of schedule. An implementation commit with no corresponding specification commit, changing behavior with nothing under `specs/` to justify it, is exactly the shape a hand-written hotfix takes, and it is a shape a script can flag the moment it looks for the pattern.

Notice what the convention does not ask for. It does not ask an architect to write code, and it does not ask an agent to have opinions about business rules — each commit stays inside the authority Chapter 8's Single Responsibility principle already assigned it, applied now to a unit of history instead of a unit of document. A repository that instead interleaves spec edits and implementation edits inside single, mixed commits loses this property immediately: a reviewer opening one such commit cannot tell, without reading every line, whether they are being asked to approve a business decision or a mechanical consequence of one already approved elsewhere, and the two questions deserve different reviewers asking different things. Two commits, cleanly separated and cross-referenced by hash, is a small convention with an outsized effect on how fast a pull request actually gets reviewed, because nobody has to first reverse-engineer which parts of the diff are the decision and which parts are the derivation.

The convention also gives the repository's history a property it did not have before: `git log --grep "^spec("` returns exactly the sequence of business decisions the system has ever encoded, with no implementation noise in between. A new engineer joining the Billing team can read that filtered history from the beginning and understand what the domain guarantees today and why each guarantee arrived, in an afternoon, which is close to the onboarding story Chapter 4 already told about Billing's promotions work — a short document beats three thousand lines of generated code, and a filtered commit history beats both, because it shows not just the current state but the sequence of decisions that produced it.

## 12.2 Versioning a spec

Every specification's header, per Chapter 9, carries a `version` field, and it follows semantic versioning rules adapted from software to documents. A **MAJOR** version bump means a change that breaks an existing guarantee — a postcondition weakened, an error code removed, a precondition strengthened in the forbidden direction Chapter 3's substitution rule named — and any document with a `depends_on` reference to the old version needs to be re-examined before it can trust the new one. A **MINOR** version bump means a backward-compatible addition — a new optional field, a new Failure Matrix row for a genuinely new condition, a new decision-table rule that does not change any existing row's outcome — safe for a dependent to ignore until it chooses to use the addition. A **PATCH** version bump means a clarification with no semantic change at all: a typo fixed, an example reworded, a cross-reference corrected.

The Changelog section, ninth and last in Chapter 9's template, is where each bump gets one entry, dated and attributed, stating which clauses changed and why:

```markdown
## Changelog

### 1.2.0 — 2026-09-10
- MINOR: Added N-6, capping retry attempts during a declared provider
  outage window, to prevent retry storms (see 12.6).
- Owner: payments-guild

### 1.1.0 — 2026-06-02
- MINOR: Added SMS as an opt-in delivery channel (N-3).
- Owner: payments-guild

### 1.0.0 — 2026-03-14
- Initial active version.
```

A changelog entry earns the same discipline as a normative statement: it names the clause that changed, not just "improved retry logic," because "improved retry logic" tells a reader nothing they can check against the document, while "added N-6" tells them exactly where to look. A specification with a `version` field and no changelog entries to justify its current number is a specification whose version history cannot be trusted, which defeats the entire purpose of stating a version at all.

The MAJOR category deserves a closer look, because it is the one engineers most often under-classify. Removing a Failure Matrix row is obviously a MAJOR change — a caller that was branching on that error code now has dead code — but so is narrowing a numeric bound that was previously wide enough for a caller to rely on the old range, and so is adding a new required field to a schema that previously accepted a payload without it, even though "adding a field" sounds additive. The test is never whether the change reads as an addition or a removal in the diff; it is whether any conforming caller from before the change could break after it, which is precisely Chapter 3's substitution rule, applied to a specification's version number instead of to a single operation's contract. A team that classifies by diff shape instead of by this test will under-version its breaking changes reliably, and every dependent specification's `depends_on` reference becomes untrustworthy the first time that happens.

Downstream of the version number, the question a dependent specification actually needs answered is narrower than "did anything change" — it is "does the change in this new version affect any clause I depend on." A MINOR or PATCH bump to `SPEC-ARCH-000` should never force every downstream Level 1 document to re-review itself, and the version discipline is what makes that possible to state as a rule rather than a judgment call: a dependent only needs to re-examine an upstream specification when its MAJOR version changes, because MINOR and PATCH bumps are defined, by the rule above, to never break a conforming caller. This is the entire reason the extra ceremony of classifying a change correctly pays for itself the first time a platform-wide document changes and forty downstream teams need to know, in one glance at a version number, whether they need to do anything about it.

## 12.3 The status lifecycle and review flow

Chapter 9 named the four values a specification's `status` field moves through — draft, review, active, deprecated — and promised the machinery behind the lifecycle would arrive here. The machinery is a review flow gated on exactly the same fields the header already carries.

A specification enters `draft` the moment a `specs/` file exists with that status, authored by anyone on the `owner` team. It moves to `review` when the author opens a pull request, and the pull request's required reviewers are computed directly from the `owner` field — no separate access-control list to maintain, because Chapter 9's header already named who is accountable. A `review`-status document cannot merge to the branch that CI treats as authoritative until an approving review lands from someone on that team, which is the mechanical enforcement of Chapter 8's Single Responsibility principle: only the team whose reason-to-change this document represents can move it forward.

Approval flips `status` to `active` and stamps the version the Changelog's newest entry names. From that point, the specification governs shipped behavior, and any implementation commit citing it, per 12.1, is checked against exactly this version. Deprecation happens the same way, in reverse: a successor specification's `supersedes` field names the old identifier, and the old document's `status` flips to `deprecated` in the same pull request that introduces the replacement, never as an afterthought days later — which closes the gap Chapter 9 warned about, where a `deprecated` document left undated for a week is quietly still governing something somewhere.

## 12.4 Drift detection

Three mechanical checks catch a specification and its code the moment they disagree, and none of them requires a human to notice anything by memory.

**Schema Check** validates that every route, message payload, or stored record a service actually produces or accepts matches its specification's Data Model exactly — no field the schema does not declare, no declared field silently missing. This is Chapter 6's `additionalProperties: false` enforced continuously in production traffic or in a contract-testing harness, rather than checked once at code-review time and never again.

**Exhaustive Error Coverage Check** re-runs Chapter 10's spec-coverage computation on every commit rather than once at merge time, and it is the specific check that would have caught this chapter's opening scenario on the regeneration commit: a Failure Matrix row or decision-table rule with no code path that can produce it — or, just as tellingly, a code path that returns an error no Failure Matrix row names — fails the build immediately, before the drifted behavior ships a second time.

**Spec-to-Code Traceability Tagging** is the mechanism Chapter 11's agent instruction file already required and this section formalizes: every generated public function carries a machine-readable tag naming the specification and section it implements.

```python
@implements_spec("SPEC-BILL-017", section="4")
def calculate_prorated_refund(subscription: Subscription) -> Money:
    ...
```

A traceability tag is not documentation for a human skimming the file, though it serves that purpose too. It is the join key a drift detector uses to connect a function to the exact clause it claims to satisfy, which is what makes it possible to ask, mechanically, "does every `active` specification's clause have at least one function claiming it, and does every traceability tag point at a clause that still exists" — the second half of that question being exactly how a script catches a specification that changed out from under code that was never regenerated against the new version.

The second half of that question matters as much as the first, and it is the direction teams forget to check. A function tagged `@implements_spec("SPEC-ACCT-003", section="6")` claiming to implement a decision table that has since been renumbered, or a rule that has since been deleted, is a dangling reference exactly like a broken hyperlink — the code still runs, the tag still looks plausible, and nothing about the tag's presence tells anyone it now points at nothing. A conformance check that only verifies "every clause has a tag" catches an under-implemented specification. A conformance check that also verifies "every tag has a clause" catches an over-implemented one — code that has outlived the rule it was built for, which is its own quiet source of drift the moment a reviewer assumes a tagged function is still doing something the specification asks for.

## 12.5 A conformance linter in CI

The three checks in 12.4 belong in the same pipeline stage, run on every pull request, before a human review is even requested, because a drift check that runs after merge only tells a team what already went wrong.

```yaml
# .github/workflows/spec-conformance.yml
name: Spec Conformance
on: [pull_request]

jobs:
  conformance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Schema Check
        run: meridian-lint schema-check --specs specs/ --src src/
      - name: Exhaustive Error Coverage Check
        run: meridian-lint coverage-check --specs specs/ --tests tests/ --min-coverage 100
      - name: Traceability Check
        run: meridian-lint trace-check --specs specs/ --src src/
      - name: Spec Structure Check
        run: python tools/check_manuscript.py specs/
```

Four steps, each one a deterministic pass or fail with no human judgment involved, mirroring Chapter 10's Three Gates at the level of the repository rather than a single change. `meridian-lint` is a fictional tool standing in for whatever a team builds or adopts; what matters is not its name but its position in the pipeline — before review, blocking merge, and reporting a specific clause or tag on failure rather than a generic red X a reviewer has to investigate from scratch. The fourth step, spec structure, is Chapter 9's own linter, reused here rather than reinvented, because a specification whose section numbering has drifted out of the nine-section template is a specification whose citations — and whose traceability tags — are about to start pointing at the wrong thing.

## 12.6 Handling the hotfix

Return to the opening scenario with the reverse-drift procedure Chapter 4 promised and this chapter now delivers in full. The on-call engineer's one-line fix was correct to make at two in the morning; nothing in this chapter argues otherwise. What Chapter 4's Golden Rule actually requires is that the fix does not end the story.

The procedure has four steps, and they run in the days immediately following the incident, not months later when someone happens to notice the drift. First, **record the divergence** the moment the hotfix ships: a ticket, linked from the deploy that shipped it, stating plainly that production code and `SPEC-ACCT-003` now disagree, with an owner and a deadline measured in days. Second, **read the hand-written fix as evidence**, not as a nuisance to clean up — the boundary-condition comparison the engineer changed at two in the morning is, read carefully, a missing clause: `SPEC-ACCT-003` never stated how the daily-limit window behaves across a UTC day boundary, and the fix is the specification the engineer would have written if there had been time. Third, **add the clause**, formally, through the review flow 12.3 describes: a new `N-` statement fixing the exact boundary behavior, a version bump, a changelog entry. Fourth, **regenerate the module** against the amended specification, so that Chapter 10's derived test suite now contains a test for this exact boundary case, and the fix survives every future regeneration because it is now something the specification states rather than something a human remembers happened once.

The two rules Chapter 4 promised would keep this from becoming a loophole are exactly the ones 12.4's tooling now enforces without anyone having to remember to check. The divergence is recorded where the conformance linter can see it — an implementation commit with no specification commit behind it, exactly the pattern 12.1 described as flaggable — so a hotfix whose repair ticket is still open next week fails CI on a subsequent, unrelated change, rather than aging quietly forever. And the deadline is short, because a divergence the linter can see and nobody has closed is not a hotfix anymore. It is spec drift with a paper trail, which is better than spec drift without one, but it is still the condition this entire chapter exists to prevent.

Notice, finally, what the procedure did not require: nobody asked the on-call engineer to write `SPEC-ACCT-003`'s new clause at two in the morning, and nobody asked them to justify the one-line fix to a review board before deploying it. The urgency and the discipline operate on different clocks, which is the entire reconciliation this chapter offers between Chapter 4's Golden Rule and the reality of an incident. The urgent clock says fix the page now, by whatever means work, because revenue and trust are both bleeding while the withdrawal bug is live. The disciplined clock says the specification learns what happened within days, through the same review flow every other change goes through, because a fix that only the urgent clock ever sees is a fix the rest of the organization — the next engineer, the next agent, the next regeneration — will never know existed until it needs it and finds it gone.

That two-clock reconciliation is worth carrying forward as the chapter's actual thesis, more than any one of its individual mechanisms. Version control for a specification is not a heavier process bolted onto version control for code; it is the same discipline — small changes, reviewed, attributed, traceable to what they replaced — applied to the one artifact this book has spent eleven chapters arguing is the one that matters most. A team that versions its code carefully and lets its specifications drift unversioned in the background has, without quite deciding to, kept rigorous history for the artifact with negative cognitive return and no history at all for the one with positive return, which is Chapter 1's argument turned into an indictment of exactly the wrong set of habits.

## Key Takeaways

- A specification change and its regenerated implementation belong in two linked commits, authored by different parties, so a reviewer arguing about the business rule reviews exactly the commit that states it.
- A specification's `version` field follows semantic versioning: MAJOR for a broken guarantee, MINOR for a backward-compatible addition, PATCH for a clarification with no semantic change — and every bump gets one Changelog entry naming the clause that moved.
- The status lifecycle from Chapter 9 is enforced by a review flow gated on the header's own fields: `owner` computes required reviewers, approval flips `draft` to `active`, and a successor's `supersedes` field flips the old document to `deprecated` in the same pull request.
- Drift detection runs three mechanical checks continuously: a Schema Check against the Data Model, an Exhaustive Error Coverage Check re-running spec coverage on every commit, and Spec-to-Code Traceability Tagging joining every function to the clause it claims to implement.
- A conformance linter belongs in CI, before human review, blocking merge on any of the three drift checks or on Chapter 9's own structural rules, and it reports a specific clause or tag rather than a generic failure.
- A production hotfix is not itself a violation of the Golden Rule; leaving it unrepaired is. The reverse-drift procedure records the divergence immediately, reads the hand-written fix as evidence of a missing clause, adds that clause through the normal review flow, and regenerates so the fix survives every future regeneration instead of being quietly overwritten by the next one.
- A drift check that only runs after merge only tells a team what has already gone wrong; the entire value of this chapter's tooling is catching the disagreement before it ships a second time.
