# Clean Spec Book Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce the complete English manuscript of *Clean Spec: Specification Engineering for the Age of AI* (about 70,000 words, 17 chapters plus front matter, epilogue, and appendices) from the Italian draft in `book.md`, with a lint script that enforces the chapter conventions and a Pandoc build script.

**Architecture:** One Markdown file per chapter under `manuscript/`, written against two contract documents (`manuscript/STYLE.md` and `manuscript/OUTLINE.md`). A Python lint script (`tools/check_manuscript.py`) is the "test suite": every chapter must pass it before commit. A PowerShell build script concatenates the chapters and calls Pandoc when it is installed.

**Tech Stack:** Markdown (Pandoc flavor), Mermaid fenced blocks, JSON Schema 2020-12, Python 3 (lint script and code examples), PowerShell 7 (build script), Pandoc (optional, not installed on this machine), Git.

**Spec:** `docs/superpowers/specs/2026-09-10-clean-spec-book-design.md`

## Global Constraints

Copied from the design spec. Every task implicitly includes these.

- `book.md` stays untouched as the original Italian source draft.
- Language: American English. First-person voice, direct, opinionated, named principles, before/after examples, in the style of Robert C. Martin's *Clean Code*.
- Audience: senior developers, tech leads, software architects who work with coding agents.
- Formulas are allowed but always explained in words; never a formula standing alone.
- Scenarios are explicitly hypothetical ("Imagine a team that..."). No fabricated personal anecdotes attributed to the author. Where a real anecdote would help, leave `<!-- AUTHOR: ... -->` describing what is needed.
- Tools cited only when stable and verifiable: JSON Schema, Mermaid, RFC 2119/8174, Hypothesis, fast-check, mypy, tsc, agent context files such as CLAUDE.md. No product names likely to be obsolete within a year. Do not name specific LLM vendors or models.
- Chapters 1–17: 3,500–5,500 words each. Each opens with a concrete scenario and closes with a `## Key Takeaways` bulleted list.
- Tables, Mermaid diagrams, and ASCII diagrams as in the draft.
- Cross-references by chapter number ("Chapter 7") and by spec ID (for example `SPEC-PAY-042`). Only the spec IDs registered in `STYLE.md` may be used.
- File layout exactly as in the spec: `manuscript/`, `build/`, `README.md`.
- Pandoc is **not installed** on this machine. The build script must degrade gracefully (concatenate, then explain how to install Pandoc).

## Working conventions for every task

- Work in `D:\GitHub\CleanSpec`. Shell is PowerShell 7; a Git Bash `Bash` tool is also available. Use forward slashes in paths.
- Before writing any chapter, read `manuscript/STYLE.md`, the chapter's entry in `manuscript/OUTLINE.md`, and the source lines of `book.md` listed in the task. The draft is in Italian; translate its ideas, not its sentences, and expand each section to the word target.
- The lint script is the test. Run `python tools/check_manuscript.py manuscript/<file>.md` and fix every reported problem before committing.
- Commit after every task. The commit message ends with the line `Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr`.

---

### Task 1: Repository scaffolding, lint script, build script

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `tools/check_manuscript.py`
- Create: `build/metadata.yaml`
- Create: `build/build.ps1`
- Create: `manuscript/.gitkeep`

**Interfaces:**
- Produces: `python tools/check_manuscript.py [files...]` returning exit code 0 when all files pass. Exposes the spec-ID registry `KNOWN_SPEC_IDS` that later tasks must keep in sync with `STYLE.md`.
- Produces: `pwsh build/build.ps1` writing `build/out/clean-spec.md` and, when Pandoc exists, `build/out/clean-spec.{epub,docx,pdf}`.

- [ ] **Step 1: Initialize git and write .gitignore**

Run:

```powershell
git init
```

Create `.gitignore`:

```
build/out/
__pycache__/
*.pyc
.DS_Store
Thumbs.db
```

- [ ] **Step 2: Write the lint script**

Create `tools/check_manuscript.py`:

```python
#!/usr/bin/env python3
"""Lint the Clean Spec manuscript.

Usage:
    python tools/check_manuscript.py                 # check every chapter file
    python tools/check_manuscript.py manuscript/05-failure-of-natural-language.md

Exit code 0 when every checked file passes, 1 otherwise.
"""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscript"

# Word-count limits by two-digit file prefix. Chapters 01-17 use CHAPTER_LIMITS.
LIMITS: dict[str, tuple[int, int]] = {
    "00": (2000, 4500),   # front matter
    "18": (1500, 3000),   # epilogue
    "19": (3000, 7000),   # appendices
}
CHAPTER_LIMITS = (3500, 5500)
CHAPTER_PREFIXES = {f"{i:02d}" for i in range(1, 18)}

# How many H1 headings a file may contain.
H1_ALLOWED: dict[str, int] = {"00": 3, "19": 1}

FORBIDDEN = [r"\bTBD\b", r"\bTODO\b", r"\bFIXME\b", r"lorem ipsum", r"\[insert\b", r"\bXXX\b"]
ITALIAN = re.compile(
    r"\b(della|delle|degli|nella|nelle|specifica|capitolo|esempio|quindi|anche|però|perché)\b",
    re.IGNORECASE,
)
SPEC_ID = re.compile(r"\bSPEC-[A-Z]+-\d{3}\b")
CHAPTER_REF = re.compile(r"\bChapter (\d+)\b")

# Keep in sync with the registry in manuscript/STYLE.md.
KNOWN_SPEC_IDS = {
    "SPEC-ARCH-000",
    "SPEC-PAY-042",
    "SPEC-ACCT-003",
    "SPEC-ORD-007",
    "SPEC-BILL-017",
    "SPEC-CORE-001",
    "SPEC-RATE-009",
    "SPEC-INV-021",
}


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text))


def check_file(path: pathlib.Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")
    text = strip_html_comments(raw)
    prefix = path.name[:2]

    words = count_words(text)
    lo, hi = LIMITS.get(prefix, CHAPTER_LIMITS)
    if not lo <= words <= hi:
        errors.append(f"word count {words} is outside {lo}-{hi}")

    h1_lines = [line for line in text.splitlines() if line.startswith("# ")]
    allowed = H1_ALLOWED.get(prefix, 1)
    if len(h1_lines) != allowed:
        errors.append(f"expected {allowed} H1 heading(s), found {len(h1_lines)}")

    if not text.lstrip().startswith("# "):
        errors.append("file must start with an H1 heading")

    if prefix in CHAPTER_PREFIXES:
        if "## Key Takeaways" not in text:
            errors.append("missing '## Key Takeaways' section")
        elif not text.rstrip().split("## Key Takeaways")[-1].strip().startswith("-"):
            errors.append("'## Key Takeaways' must be followed by a bulleted list")

    for pattern in FORBIDDEN:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            errors.append(f"forbidden placeholder {m.group(0)!r}")

    for m in ITALIAN.finditer(text):
        errors.append(f"possible Italian leftover {m.group(0)!r}")

    if text.count("```") % 2:
        errors.append("unbalanced code fences")

    for m in SPEC_ID.finditer(text):
        if m.group(0) not in KNOWN_SPEC_IDS:
            errors.append(f"unregistered spec id {m.group(0)}; add it to STYLE.md and KNOWN_SPEC_IDS")

    for m in CHAPTER_REF.finditer(text):
        n = int(m.group(1))
        if not 1 <= n <= 17:
            errors.append(f"cross-reference to nonexistent Chapter {n}")

    return words, errors


def main(argv: list[str]) -> int:
    if argv:
        paths = [pathlib.Path(a) for a in argv]
    else:
        paths = sorted(p for p in MANUSCRIPT.glob("*.md") if p.name[:2].isdigit())
    failed = False
    total = 0
    for path in paths:
        words, errors = check_file(path)
        total += words
        status = "OK " if not errors else "FAIL"
        print(f"{status} {path.name}: {words} words")
        for e in errors:
            print(f"     - {e}")
        failed = failed or bool(errors)
    print(f"TOTAL {total} words in {len(paths)} file(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 3: Verify the lint script fails on a placeholder chapter**

Create a throwaway file `manuscript/01-commoditization-of-code.md` containing just:

```markdown
# Chapter 1: The Commoditization of Code

TBD
```

Run:

```powershell
python tools/check_manuscript.py manuscript/01-commoditization-of-code.md
```

Expected: `FAIL 01-commoditization-of-code.md: 8 words` with errors for word count, missing Key Takeaways, and forbidden placeholder. Exit code 1. Then delete the throwaway file:

```powershell
Remove-Item manuscript/01-commoditization-of-code.md
```

- [ ] **Step 4: Write Pandoc metadata**

Create `build/metadata.yaml`:

```yaml
---
title: "Clean Spec"
subtitle: "Specification Engineering for the Age of AI"
author: "Matteo Baccan"
lang: en-US
date: "2026"
rights: "© 2026 Matteo Baccan. All rights reserved."
toc: true
toc-depth: 2
numbersections: false
documentclass: book
geometry: margin=1in
mainfont: ""
---
```

- [ ] **Step 5: Write the build script**

Create `build/build.ps1`:

```powershell
#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Concatenates manuscript/*.md into build/out/clean-spec.md and, when Pandoc is
  available, renders EPUB, DOCX and PDF.

.USAGE
  pwsh build/build.ps1            # concatenate + render all formats Pandoc can
  pwsh build/build.ps1 -Formats epub,docx
#>
param(
    [string[]]$Formats = @('epub', 'docx', 'pdf')
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$manuscript = Join-Path $root 'manuscript'
$out = Join-Path $PSScriptRoot 'out'
New-Item -ItemType Directory -Force $out | Out-Null

# Part titles are inserted before the first chapter of each part.
$parts = @{
    '01' = 'Part I: Why Specifications Matter Now'
    '05' = 'Part II: Anatomy of a Clean Spec'
    '10' = 'Part III: Verification, Validation, and Agentic Workflows'
    '13' = 'Part IV: Spec Smells and Refactorings'
    '15' = 'Part V: Case Studies and Practice'
}

$files = Get-ChildItem $manuscript -Filter '*.md' |
    Where-Object { $_.Name -match '^\d{2}-' } |
    Sort-Object Name

$combined = Join-Path $out 'clean-spec.md'
$sb = [System.Text.StringBuilder]::new()
foreach ($f in $files) {
    $prefix = $f.Name.Substring(0, 2)
    if ($parts.ContainsKey($prefix)) {
        [void]$sb.AppendLine("# $($parts[$prefix]) {.unnumbered .part}")
        [void]$sb.AppendLine()
    }
    [void]$sb.Append((Get-Content $f.FullName -Raw))
    [void]$sb.AppendLine()
    [void]$sb.AppendLine()
}
[System.IO.File]::WriteAllText($combined, $sb.ToString(), [System.Text.UTF8Encoding]::new($false))
Write-Host "Wrote $combined ($($files.Count) files)"

$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) {
    Write-Warning 'Pandoc is not installed. Only the concatenated Markdown was produced.'
    Write-Host 'Install it with: winget install --id JohnMacFarlane.Pandoc   (PDF also needs a LaTeX engine, e.g. winget install MiKTeX.MiKTeX)'
    exit 0
}

$meta = Join-Path $PSScriptRoot 'metadata.yaml'
foreach ($fmt in $Formats) {
    $target = Join-Path $out "clean-spec.$fmt"
    $args = @($combined, '--metadata-file', $meta, '--from', 'markdown+smart', '--toc', '--top-level-division=chapter', '-o', $target)
    if ($fmt -eq 'pdf') {
        $engine = @('xelatex', 'lualatex', 'pdflatex') | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
        if (-not $engine) {
            Write-Warning 'No LaTeX engine found; skipping PDF. Install MiKTeX or TeX Live to enable it.'
            continue
        }
        $args += @('--pdf-engine', $engine)
    }
    Write-Host "pandoc -> $target"
    & pandoc @args
}
Write-Host 'Note: Mermaid blocks are emitted as fenced code. Render them with a Pandoc Mermaid filter if you need images.'
```

- [ ] **Step 6: Run the build script on an empty manuscript**

Run:

```powershell
New-Item -ItemType File -Force manuscript/.gitkeep | Out-Null
pwsh build/build.ps1
```

Expected: `Wrote ...build/out/clean-spec.md (0 files)` followed by the Pandoc warning and install hint. Exit code 0.

- [ ] **Step 7: Write README.md**

Create `README.md`:

```markdown
# Clean Spec: Specification Engineering for the Age of AI

A book about writing specifications that coding agents can compile into correct software.

## Layout

- `book.md` — original Italian draft (source material, never edited).
- `manuscript/` — the English manuscript, one file per chapter, plus `STYLE.md` and `OUTLINE.md`.
- `tools/check_manuscript.py` — lint script that enforces the chapter conventions.
- `build/build.ps1` — concatenates the chapters and renders EPUB/DOCX/PDF with Pandoc.
- `docs/superpowers/` — design spec and implementation plan.

## Checking the manuscript

```powershell
python tools/check_manuscript.py            # all chapters
python tools/check_manuscript.py manuscript/07-three-levels-of-a-spec.md
```

## Building

```powershell
pwsh build/build.ps1                        # all formats Pandoc can produce
pwsh build/build.ps1 -Formats epub,docx
```

Requires [Pandoc](https://pandoc.org). PDF output also needs a LaTeX engine (MiKTeX or TeX Live). Mermaid diagrams are kept as fenced code blocks; use a Pandoc Mermaid filter to render them as images.
```

- [ ] **Step 8: Commit**

```powershell
git add .gitignore README.md tools/check_manuscript.py build/metadata.yaml build/build.ps1 manuscript/.gitkeep book.md docs/
git commit -m "chore: scaffold manuscript repo with lint and build scripts

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 2: STYLE.md, the style contract

**Files:**
- Create: `manuscript/STYLE.md`

**Interfaces:**
- Produces: the spec-ID registry, the running-example domain, the contract block format, and the chapter skeleton that every chapter task must follow.

- [ ] **Step 1: Write STYLE.md**

Create `manuscript/STYLE.md` with exactly this content:

````markdown
# Clean Spec — Style Guide

Every chapter file must honor this document. When a chapter and this file disagree, this file wins.

## 1. Voice and register

- First person singular ("I", "my experience", "I recommend"). Address the reader as "you".
- Direct and opinionated. State the principle, then argue for it. Do not hedge with "it could be argued".
- American English spelling (behavior, organize, license).
- Sentences average under 25 words. One idea per paragraph. Paragraphs of 2–6 sentences.
- Contractions are fine ("don't", "isn't") but not in normative statements inside spec examples.
- Humor is allowed sparingly and never at the reader's expense.
- Avoid marketing words: "revolutionary", "game-changing", "unlock", "leverage" (as a verb), "seamless".

## 2. Scenarios and anecdotes

- Every chapter opens with a concrete scenario of 200–400 words. It is explicitly hypothetical: "Imagine a team that...", "Picture a Tuesday afternoon...", "Suppose you inherit...".
- Never invent a personal story presented as true ("Last year at a client of mine..."). Where a true anecdote from the author would strengthen the point, insert an HTML comment on its own line: `<!-- AUTHOR: a real example of X would fit here; needs Y and Z. -->`
- The running fictional company is **Meridian**, a mid-size e-commerce and payments platform. Teams: Checkout, Billing, Ledger, Inventory, Identity. Use it for continuity; do not describe it beyond what a scenario needs.

## 3. Named principles and rules

Introduce a principle with a bold name the first time, then refer to it by name:

- **The Golden Rule of Clean Spec** (Chapter 4): never hand-edit generated code; if the code is wrong, the spec is wrong; fix the spec and regenerate.
- **Constraint Density** (Chapter 2): formal constraints divided by total tokens; a Clean Spec maximizes it.
- **The Three Levels** (Chapter 7): Level 0 architecture and boundaries, Level 1 contracts and data model, Level 2 state rules and edge cases.
- **The Three Gates** (Chapter 10): lint, strict type check, contract tests.
- **The 300-Line Rule** (Chapter 9): an atomic spec never exceeds 300 lines of Markdown.

## 4. Formulas

- Formulas may appear in `$...$` (inline) or `$$...$$` (display) LaTeX.
- Every formula is preceded or followed by a plain-English sentence stating what it means. A formula never stands alone as a paragraph.
- Prefer words when the formula adds nothing: "the sum of debits equals the sum of credits" is better than a summation sign in prose; use the formula inside a spec example where precision matters.

## 5. Code, schemas, and diagrams

- Code examples: Python 3 with type hints as the primary language; TypeScript as the secondary. Keep examples under 40 lines.
- Schemas: JSON Schema 2020-12 (`"$schema": "https://json-schema.org/draft/2020-12/schema"`). Always include `"additionalProperties": false` on object schemas in spec examples.
- Diagrams: Mermaid in ```` ```mermaid ```` fences for state machines (`stateDiagram-v2`) and sequences (`sequenceDiagram`). ASCII diagrams in plain ```` ``` ```` fences for pipelines and box layouts (reuse the draft's ASCII art where it exists).
- Tables: GitHub-flavored Markdown with a header row and alignment row. Every table has a one-sentence lead-in.
- Tools you may name: JSON Schema, Mermaid, RFC 2119, RFC 8174, Hypothesis, fast-check, mypy, tsc, pytest, Git, CI, CLAUDE.md-style instruction files (say "an agent instruction file such as CLAUDE.md"). Do not name LLM vendors, model names, IDEs, or SaaS products.

## 6. Normative statements in spec examples

- Use RFC 2119 keywords in uppercase: MUST, MUST NOT, SHOULD, SHOULD NOT, MAY. Bold them in Markdown spec examples: **MUST**.
- Number normative statements inside a spec example as `N-1`, `N-2`, ... so they can be cited (`SPEC-PAY-042 N-3`).

## 7. Contract block format

When a chapter shows an operation contract, use this Markdown shape:

```markdown
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
```

## 8. Spec ID registry

Only these IDs may appear in the manuscript. Sections are cited as `SPEC-PAY-042 §3`.

| ID | Title | Domain | Introduced in | Also used in |
| :--- | :--- | :--- | :--- | :--- |
| `SPEC-ARCH-000` | Meridian Platform Architecture (Level 0) | Platform | Chapter 7 | 9, 11 |
| `SPEC-PAY-042` | Transaction Confirmation Notifications | Payments | Chapter 6 | 5, 9, 10, 12, 13 |
| `SPEC-ACCT-003` | Withdrawal Authorization | Accounts | Chapter 7 | 3, 10 |
| `SPEC-ORD-007` | Order Lifecycle (state machine `FSM-ORD-01`) | Checkout | Chapter 14 | 13, 17 |
| `SPEC-BILL-017` | Tiered Subscription Upgrade | Billing | Chapter 12 | 8 |
| `SPEC-CORE-001` | Double-Entry Ledger | Ledger | Chapter 15 | 3, 10 |
| `SPEC-RATE-009` | Shipping Rate Calculator (reverse spec) | Logistics | Chapter 16 | — |
| `SPEC-INV-021` | Stock Reservation with Expiry | Inventory | Chapter 17 | 12 |

Adding an ID requires updating this table and `KNOWN_SPEC_IDS` in `tools/check_manuscript.py`.

## 9. Chapter skeleton

```markdown
# Chapter N: Title

[Opening scenario, 200–400 words, hypothetical.]

## N.1 First section
...
## N.k Last section
...
## Key Takeaways

- Bullet, one sentence, states a rule or a fact.
- 5 to 8 bullets.
```

- Exactly one H1 per chapter file. Sections are H2 and numbered `N.1`, `N.2`, ... Sub-sections are H3, unnumbered.
- Cross-reference chapters as "Chapter 7" (capitalized, numeral). Never "the next chapter" or "above/below".
- 3,500–5,500 words per chapter. Run `python tools/check_manuscript.py manuscript/<file>` before committing.

## 10. Terminology (use consistently)

| Use | Not |
| :--- | :--- |
| coding agent, agent | AI, the model, the bot, copilot |
| language model | LLM (spell out on first use per chapter, then "language model") |
| specification, spec | requirement doc, prompt (a prompt is an input to a model; a spec is an artifact) |
| Clean Spec (the discipline, capitalized) | clean spec (lowercase only when meaning "a spec that is clean") |
| Spec-Driven Development (SDD) | spec-first development |
| failure matrix | error table |
| decision table | rules table |
| state machine, state table | FSM (may be used in spec IDs like `FSM-ORD-01`) |
| value object | wrapper type |
| port (Clean Architecture sense) | interface (fine in code, avoid in prose about boundaries) |
| generated code, synthesized code | AI code |
| spec drift | divergence |
````

- [ ] **Step 2: Verify the registry matches the lint script**

Run:

```powershell
python -c "import re,sys; s=open('manuscript/STYLE.md',encoding='utf-8').read(); ids=set(re.findall(r'SPEC-[A-Z]+-\d{3}', s)); sys.path.insert(0,'tools'); import check_manuscript as c; missing=ids^c.KNOWN_SPEC_IDS; print('MISMATCH', missing) if missing else print('registry OK')"
```

Expected: `registry OK`

- [ ] **Step 3: Commit**

```powershell
git add manuscript/STYLE.md
git commit -m "docs: add manuscript style guide

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 3: OUTLINE.md, the structural contract

**Files:**
- Create: `manuscript/OUTLINE.md`

**Interfaces:**
- Produces: the section list and word target per chapter. Chapter tasks below repeat their own entry, so the file is the single place where the whole book is visible.

- [ ] **Step 1: Write OUTLINE.md**

Create `manuscript/OUTLINE.md` with exactly this content:

```markdown
# Clean Spec — Outline

Word targets are the midpoint of the 3,500–5,500 range unless noted. Source column points at `book.md` line ranges.

## Front matter — `00-front-matter.md` (2,500 words, 3 H1s)
- Preface: why this book, why now, what changed when code became cheap.
- Who This Book Is For: senior developers, tech leads, architects; what you need to know already.
- How to Read This Book: the five parts, running example (Meridian), spec IDs, formulas policy, hypothetical scenarios.

## Part I — Why Specifications Matter Now

### 1. The Commoditization of Code — `01-commoditization-of-code.md` (4,000) — source 7–75
- Scenario: a weekend prototype that cannot be changed three months later.
- 1.1 Four leaps in abstraction (table: era, what got automated, what became the primary artifact).
- 1.2 Source code as intermediate representation; the model as a nondeterministic compiler.
- 1.3 The vibecoding curve: generation cost O(1), verification cost O(N²) (ASCII chart from draft, explained in words).
- 1.4 The only artifact with positive cognitive return.
- 1.5 What this book does not claim (agents still fail; engineers are not obsolete; specs do not remove judgment).
- Key Takeaways.

### 2. What a Language Model Does With Your Words — `02-what-a-language-model-does.md` (4,000) — source 77–117
- Scenario: same prompt, two runs, two different implementations of the same transfer function.
- 2.1 Next-token prediction in plain words (the conditional probability formula, explained).
- 2.2 Collapsing the output space: "handle financial transactions carefully" vs. the formal transfer tuple (before/after).
- 2.3 Where defaults come from: training-set priors (floats for money, swallowed exceptions, no isolation).
- 2.4 Context windows, lost-in-the-middle, context poisoning.
- 2.5 Constraint Density: definition, before/after paragraph with approximate token counts.
- 2.6 Six practical rules to raise density.
- Key Takeaways.

### 3. Contracts, Not Conversations: Hoare Logic for Working Engineers — `03-contracts-not-conversations.md` (4,000) — source 119–136
- Scenario: an agent implements `withdraw` and lets the balance go negative because nobody said it couldn't.
- 3.1 The Hoare triple in plain words.
- 3.2 Preconditions: what the caller promises.
- 3.3 Postconditions: what the operation promises.
- 3.4 Invariants: what is always true (domain invariants vs. loop invariants).
- 3.5 The contract block format (STYLE.md §7) applied to `withdraw` from `SPEC-ACCT-003`.
- 3.6 From contract to test: one assertion per clause (preview of Chapter 10).
- 3.7 Strength of contracts: weakening preconditions, strengthening postconditions (preview of Chapter 8, Liskov).
- 3.8 What a missing contract costs: the agent extrapolates.
- Key Takeaways.

### 4. Spec-Driven Development: Inverting the Flow — `04-spec-driven-development.md` (4,000) — source 138–177
- Scenario: two Meridian teams build the same feature; one prompts, one specs; compare at week six.
- 4.1 From TDD to SDD (table: waterfall, agile, TDD, SDD; who writes what, what is the source of truth).
- 4.2 The SDD pipeline (ASCII diagram from draft).
- 4.3 The Golden Rule of Clean Spec.
- 4.4 Objections and answers: hotfixes, regeneration cost, "the model is wrong, not the spec", exploratory code.
- 4.5 The spec as single source of truth; what lives where in the repository (preview of Chapter 11 tree).
- 4.6 When SDD is the wrong tool (throwaway scripts, spikes, unknown domains).
- Key Takeaways.

## Part II — Anatomy of a Clean Spec

### 5. The Failure of Natural Language — `05-failure-of-natural-language.md` (4,000) — source 181–204
- Scenario: the payment-notification sentence read by three engineers and an agent; four readings.
- 5.1 Why natural language works for people and fails for compilers.
- 5.2 A taxonomy of ambiguity (table: lexical, syntactic, scope, referential, temporal, quantifier; each with an example).
- 5.3 RFC 2119 and RFC 8174 vocabulary (table; uppercase rule; the boilerplate sentence).
- 5.4 Rewriting the sentence as normative statements N-1..N-5 of `SPEC-PAY-042`.
- 5.5 Common misuses: SHOULD as polite MUST; MAY for undecided; "will"; negated SHOULD.
- 5.6 Beyond modal verbs: quantify everything (numbers, units, time bounds, cardinalities).
- Key Takeaways.

### 6. A Composite Grammar: Markdown, Schemas, Diagrams — `06-composite-grammar.md` (4,200) — source 206–289
- Scenario: the same notification spec written as one page of prose, then as the tripartite form.
- 6.1 Three layers: Markdown for structure and norms, schemas for data, diagrams for dynamics.
- 6.2 Markdown conventions: addressable headings, numbered normative statements, tables.
- 6.3 JSON Schema for contracts: the `TransactionNotificationEvent` schema, keyword by keyword.
- 6.4 Typed alternatives (Pydantic models, TypeScript types) and when to use them.
- 6.5 Mermaid for dynamics: the delivery state machine of `SPEC-PAY-042`; a sequence diagram for the same flow.
- 6.6 The assembled `SPEC-PAY-042` (full example).
- 6.7 What not to put in a spec: screenshots, pseudo-code, prose that duplicates the schema.
- Key Takeaways.

### 7. The Three Levels of a Spec — `07-three-levels-of-a-spec.md` (4,200) — source 291–336
- Scenario: an agent asked to add one feature is handed 400 pages; what should it read?
- 7.1 The concentric levels (ASCII diagram from draft).
- 7.2 Level 0: architecture and boundaries; `SPEC-ARCH-000` excerpt (dependency rule, allowed components, technology constraints).
- 7.3 Level 1: contracts and data model; value objects over primitives; the Failure Modes Matrix (table from draft) and how to build one.
- 7.4 Level 2: state rules and edge cases; the withdrawal decision table `SPEC-ACCT-003` (table from draft); completeness and consistency checks for decision tables.
- 7.5 How levels reference each other; what an agent reads for a given task.
- Key Takeaways.

### 8. SOLID for Specifications — `08-solid-for-specifications.md` (4,200) — source 338–371
- Scenario: one spec file that changes every week for five unrelated reasons.
- 8.1 Single Responsibility Spec: one reason to change; the 300-line rule of thumb.
- 8.2 Open/Closed Spec: extend by adding subscribers, not by editing the core (`SPEC-PAY-042` SMS channel example).
- 8.3 Liskov Substitution for Specs: `PaymentGatewayPort` and the 60-second idempotency window; what an adapter may not do.
- 8.4 Interface Segregation Spec: role-specific views; the 50-endpoint schema problem.
- 8.5 Dependency Inversion Spec: `TaxRecordPersistencePort.save` vs. "UPSERT into tax_records"; `SPEC-BILL-017` as the high-level spec.
- 8.6 Summary table: principle, spec form, smell it prevents (forward references to Chapter 13).
- Key Takeaways.

### 9. Naming, Structure, and Size of a Spec — `09-naming-structure-size.md` (4,000) — new
- Scenario: "which spec is current?" asked in a release meeting; three answers.
- 9.1 Spec identifiers: `SPEC-<DOMAIN>-<NNN>`, immutability, section addressing (`SPEC-PAY-042 §3`).
- 9.2 Files and directories: `specs/modules/<domain>/<id>-<slug>.md`, companion `schema.json`.
- 9.3 The header block (YAML front matter: id, title, version, status, owner, depends_on, supersedes).
- 9.4 The nine mandatory sections in fixed order: Scope, Normative Constraints, Data Model, Invariants, Failure Matrix, State Rules, Test Requirements, Open Questions, Changelog.
- 9.5 The 300-Line Rule: token budget arithmetic, splitting rules, what to do with a spec that will not fit.
- 9.6 Numbering normative statements (N-), preconditions (P-), postconditions (Q-), invariants (I-).
- 9.7 Status lifecycle: draft, review, active, deprecated (detailed in Chapter 12).
- Key Takeaways.

## Part III — Verification, Validation, and Agentic Workflows

### 10. Spec-First, Test-First — `10-spec-first-test-first.md` (4,200) — source 377–414
- Scenario: an agent hardcodes the answer to pass a single example test.
- 10.1 Tests are derived, not invented: decision-table rows, schema bounds, invariants.
- 10.2 Property-based testing as the anti-hallucination guarantee (Hypothesis example from draft; fast-check equivalent).
- 10.3 Contract tests from the failure matrix: one test per row (`SPEC-CORE-001` rows).
- 10.4 The Three Gates (ASCII diagram from draft): lint, strict types, contract tests.
- 10.5 Ordering the agent's work: tests first; what to do when a test cannot be written (a spec gap).
- 10.6 Coverage means spec coverage, not line coverage.
- Key Takeaways.

### 11. Anatomy of a Spec-Driven Agent — `11-anatomy-of-a-spec-driven-agent.md` (4,200) — source 416–466
- Scenario: the same task run in an open chat and in a constrained loop.
- 11.1 The constrained loop: Init, Plan, Execute, Validate; the Delta as the only feedback.
- 11.2 Context budgeting: what goes in, what stays out (table).
- 11.3 Repository layout for context files (tree from draft).
- 11.4 Anatomy of an agent instruction file (full English example of the draft's CLAUDE.md-style file).
- 11.5 Stop conditions: when the agent must halt and ask (semantic gaps).
- 11.6 Splitting roles: spec reviewer, test synthesizer, implementer.
- Key Takeaways.

### 12. Specs Under Version Control — `12-specs-under-version-control.md` (4,000) — source 468–514
- Scenario: a 2 a.m. hotfix that the spec never learns about.
- 12.1 Spec commits and implementation commits (the two commit messages from the draft, `SPEC-BILL-017`).
- 12.2 Versioning a spec: semantic versioning rules for specs; the Changelog section.
- 12.3 The status lifecycle and review flow.
- 12.4 Drift detection: schema check, exhaustive error coverage, traceability tags (`@implements_spec`).
- 12.5 A conformance linter in CI: what it checks, sample configuration.
- 12.6 Handling the hotfix: the reverse-drift procedure.
- Key Takeaways.

## Part IV — Spec Smells and Refactorings

### 13. A Catalog of Spec Smells — `13-catalog-of-spec-smells.md` (5,000) — source 518–562
- Scenario: a spec review where every reviewer feels something is wrong and nobody can name it.
- Intro: why a vocabulary of smells matters.
- One H2 per smell, each with Symptom, Example, Consequence, Cure (naming the Chapter 14 refactoring):
  13.1 The Omniprompt; 13.2 The Handwave; 13.3 Syntactic Micromanagement; 13.4 Domain Leakage; 13.5 Happy Path Only; 13.6 Ghost Invariant; 13.7 Prose State Machine; 13.8 Example as Specification; 13.9 Modal Mush; 13.10 Primitive Obsession; 13.11 Zombie Spec.
- Summary table: smell, detection question, refactoring.
- Key Takeaways.

### 14. A Catalog of Spec Refactorings — `14-catalog-of-spec-refactorings.md` (5,000) — source 564–599
- Scenario: a review turns a smelly spec into a clean one in one afternoon.
- One H2 per refactoring, Fowler format (Motivation, Mechanics, Example before/after):
  14.1 Replace Prose with State Table (`SPEC-ORD-007`, `FSM-ORD-01`); 14.2 Extract Bounded Context Spec; 14.3 Introduce Failure Matrix; 14.4 Replace Primitive with Value Object; 14.5 Extract Invariant from Examples; 14.6 Normalize Modal Verbs; 14.7 Replace Procedure with Postcondition; 14.8 Invert Infrastructure Dependency; 14.9 Split Role-Specific View.
- Key Takeaways.

## Part V — Case Studies and Practice

### 15. Case Study: A Double-Entry Ledger — `15-case-study-double-entry-ledger.md` (4,500) — source 603–663
- Scenario: Meridian's Ledger team must replace a float-based balance table.
- 15.1 The problem and the constraints.
- 15.2 The full `SPEC-CORE-001`, in the Chapter 9 template, section by section with commentary.
- 15.3 What the agent generates first: the test suite (property tests for the three invariants; one test per failure-matrix row).
- 15.4 What the agent generates second: the domain types (`Money`, `LedgerEntry`, `Transaction`) in Python.
- 15.5 A walkthrough of one failure: an unbalanced transaction.
- 15.6 Lessons.
- Key Takeaways.

### 16. Case Study: Reverse-Specifying a Legacy System — `16-case-study-reverse-specifying-legacy.md` (4,200) — source 665–702
- Scenario: a 900-line shipping-rate function nobody dares touch.
- 16.1 Why blind rewrites fail.
- 16.2 The four phases (ASCII diagram from draft): Reverse Spec, Human Audit, Test Synthesis, Re-synthesis.
- 16.3 Rules for the reverse spec: hidden side effects, big-ball-of-mud variables, implicit rules.
- 16.4 Worked example: a legacy Python fragment; the raw reverse spec the agent produces; the audited `SPEC-RATE-009` with a decision table; the characterization tests.
- 16.5 Re-synthesis and the safety net.
- 16.6 What to do with behavior nobody wants to keep.
- Key Takeaways.

### 17. Case Study: One Feature, End to End — `17-case-study-one-feature.md` (5,000) — new
- Scenario: the ticket "reserve stock during checkout, release after 15 minutes".
- 17.1 From ticket to draft spec (`SPEC-INV-021` v0.1).
- 17.2 Spec review: three smells found and fixed (v1.0).
- 17.3 The agent's plan and first test suite (hypothetical transcript excerpts).
- 17.4 The first failure: expiry during payment; a spec gap.
- 17.5 Amending the spec (v1.1), regenerating, the commit pair.
- 17.6 Retrospective: what the spec caught that a prompt would not.
- Key Takeaways.

## Epilogue — `18-epilogue.md` (2,000) — source 704–707
- The Specification Is the Software: architects of constraints; what changes for careers, teams, education; a closing charge.

## Appendices — `19-appendices.md` (4,500, 1 H1 with H2 per appendix)
- A. Clean Spec Template (the nine sections, ready to copy).
- B. RFC 2119 Cheat Sheet.
- C. Spec Review Checklist (one question per smell, plus structure checks).
- D. Glossary (about 40 terms).
```

- [ ] **Step 2: Commit**

```powershell
git add manuscript/OUTLINE.md
git commit -m "docs: add per-chapter outline

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 4: Front matter

**Files:**
- Create: `manuscript/00-front-matter.md`

**Interfaces:**
- Consumes: `manuscript/STYLE.md`, `manuscript/OUTLINE.md`.
- Produces: the book's framing that later chapters may assume (Meridian, spec IDs, formula policy).

- [ ] **Step 1: Read STYLE.md and the Front matter entry in OUTLINE.md**

- [ ] **Step 2: Write the file**

Three H1 sections, in this order: `# Preface`, `# Who This Book Is For`, `# How to Read This Book`. Target 2,500 words total.

Preface (about 1,100 words): open with the observation that writing code stopped being the expensive part; what the author noticed changed in how teams fail; the thesis in one sentence ("the specification is the software; the code is a build artifact"); why *Clean Code* is the model for this book (principles with names, before/after, smells and refactorings) and what is different (the reader of the spec is a probabilistic compiler); a short acknowledgement paragraph left as `<!-- AUTHOR: acknowledgements -->`.

Who This Book Is For (about 600 words): senior developers, tech leads, architects; what they need already (types, tests, Git, one coding agent in daily use); who should skip it (beginners, people who never work with agents); what the book is not (a prompt-engineering guide, a vendor manual).

How to Read This Book (about 800 words): the five parts in one paragraph each; the Meridian running example; spec IDs and how to cite them; the formula policy (every formula explained); the hypothetical-scenario convention; the Key Takeaways lists; the appendices as tools to copy.

- [ ] **Step 3: Lint**

Run: `python tools/check_manuscript.py manuscript/00-front-matter.md`
Expected: `OK 00-front-matter.md: <2000-4500> words`

- [ ] **Step 4: Commit**

```powershell
git add manuscript/00-front-matter.md
git commit -m "book: add front matter

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 5: Chapter 1, The Commoditization of Code

**Files:**
- Create: `manuscript/01-commoditization-of-code.md`
- Source: `book.md` lines 7–75

**Interfaces:**
- Produces: the terms "nondeterministic compiler", "intermediate representation", "positive cognitive return" used by later chapters.

- [ ] **Step 1: Read STYLE.md, the Chapter 1 entry in OUTLINE.md, and `book.md` lines 7–75**

- [ ] **Step 2: Write the chapter**

`# Chapter 1: The Commoditization of Code`, 4,000 words, sections 1.1–1.5 as outlined, then `## Key Takeaways`.

Required elements:
- Opening scenario: a Meridian squad ships a prototype in a weekend with an agent; three months later every change breaks two things; nobody can say what the system guarantees.
- 1.1 table with four rows (machine code to assembly; assembly to compiled procedural; procedural to managed object-oriented; traditional programming to spec-driven agentic engineering) and columns "Transition", "What got automated", "What became the primary artifact".
- 1.3 reproduces the draft's ASCII cost chart inside a plain code fence, then explains in words: generation cost is roughly constant per feature, verification cost without a formal spec grows with the square of the number of implicit invariants because every pair of unstated assumptions can interact.
- 1.5 explicitly states three limits: agents still produce wrong code from good specs, a spec does not replace engineering judgment, and the discipline has a cost that only pays off beyond toy size.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/01-commoditization-of-code.md`
Expected: `OK` line, no error bullets.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/01-commoditization-of-code.md
git commit -m "book: chapter 1, the commoditization of code

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 6: Chapter 2, What a Language Model Does With Your Words

**Files:**
- Create: `manuscript/02-what-a-language-model-does.md`
- Source: `book.md` lines 77–117

**Interfaces:**
- Produces: **Constraint Density** (named principle), the "output space" metaphor, the six practical rules referenced by Chapters 5, 9, 13.

- [ ] **Step 1: Read STYLE.md, the Chapter 2 entry in OUTLINE.md, and `book.md` lines 77–117**

- [ ] **Step 2: Write the chapter**

`# Chapter 2: What a Language Model Does With Your Words`, 4,000 words, sections 2.1–2.6, `## Key Takeaways`.

Required elements:
- Scenario: the same one-line prompt for a money transfer run twice produces one implementation using floats and one using integers; neither checks that source and destination differ.
- 2.1 includes the conditional probability formula `$P(T_n \mid T_1, \dots, T_{n-1})$` followed by a sentence explaining it as "the model picks each next token based on everything before it".
- 2.2 before/after: the vague sentence, then the formal transfer definition (source, destination, amount as a tuple; source not equal to destination; amount a positive integer; balances change by exactly minus and plus amount) written first in words then as the formula from the draft, plus serializable isolation and UUID idempotency key.
- 2.5 defines Constraint Density as formal constraints divided by total tokens, shows one 120-word "polite" paragraph and its 40-word dense rewrite with approximate token counts and a count of constraints in each.
- 2.6 six rules: delete pleasantries and preambles; one fact per line; tables over paragraphs; name every type; number every rule; put the most important constraints first and last.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/02-what-a-language-model-does.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/02-what-a-language-model-does.md
git commit -m "book: chapter 2, what a language model does with your words

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 7: Chapter 3, Contracts, Not Conversations

**Files:**
- Create: `manuscript/03-contracts-not-conversations.md`
- Source: `book.md` lines 119–136

**Interfaces:**
- Consumes: contract block format from STYLE.md §7.
- Produces: the P-/Q-/I- numbering convention; the `withdraw` contract of `SPEC-ACCT-003` reused in Chapters 7 and 10.

- [ ] **Step 1: Read STYLE.md (§7 especially), the Chapter 3 entry in OUTLINE.md, and `book.md` lines 119–136**

- [ ] **Step 2: Write the chapter**

`# Chapter 3: Contracts, Not Conversations: Hoare Logic for Working Engineers`, 4,000 words, sections 3.1–3.8, `## Key Takeaways`.

Required elements:
- Scenario: an agent implements `withdraw`; the balance goes negative in the first integration test; the prompt said "withdraw money from the account" and nothing else.
- 3.1 shows `$\{P\}\; C \;\{Q\}$` and explains: if P holds before C runs, Q holds after.
- 3.4 shows `$\forall s \in S,\; I(s) = \text{true}$` and explains: for every reachable state the invariant holds; distinguishes domain invariants from loop invariants in one paragraph.
- 3.5 the full contract block for `withdraw(account_id: AccountId, amount: Money) -> WithdrawalResult` exactly in the STYLE.md §7 shape, cited as `SPEC-ACCT-003 §4`.
- 3.6 a Python test sketch: one `pytest` function per postcondition clause, under 30 lines.
- 3.7 explains that an implementation may accept more (weaker precondition) and promise more (stronger postcondition), never the reverse, with a two-row table.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/03-contracts-not-conversations.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/03-contracts-not-conversations.md
git commit -m "book: chapter 3, contracts not conversations

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 8: Chapter 4, Spec-Driven Development

**Files:**
- Create: `manuscript/04-spec-driven-development.md`
- Source: `book.md` lines 138–177

**Interfaces:**
- Produces: **The Golden Rule of Clean Spec** (named exactly so), the SDD pipeline diagram, the repository layout preview.

- [ ] **Step 1: Read STYLE.md, the Chapter 4 entry in OUTLINE.md, and `book.md` lines 138–177**

- [ ] **Step 2: Write the chapter**

`# Chapter 4: Spec-Driven Development: Inverting the Flow`, 4,000 words, sections 4.1–4.6, `## Key Takeaways`.

Required elements:
- Scenario: two Meridian teams, Checkout and Billing, build "apply promo code at checkout"; compare at week six on change lead time, regressions, and onboarding of a new engineer.
- 4.1 table with rows waterfall, agile, TDD, SDD and columns "Who writes the requirements", "Who writes the tests", "Who writes the code", "Source of truth".
- 4.2 reproduces the draft's pipeline ASCII diagram (translated labels) in a plain code fence and walks through each box.
- 4.3 states the Golden Rule in a blockquote: "Never hand-edit generated code. If the code is wrong, incomplete, or slow, the defect is in the specification. Fix the spec, then run the agent again."
- 4.4 answers four objections in H3 sub-sections: "What about production hotfixes?" (answer forward-references the reverse-drift procedure of Chapter 12), "Regeneration is expensive", "Sometimes the model is wrong and the spec is fine" (answer: then the spec lacked the constraint that would have caught it, add a test requirement), "What about exploratory code?".
- 4.5 shows a short repository tree with `specs/`, `tests/`, `src/` and states which are hand-written and which are generated.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/04-spec-driven-development.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/04-spec-driven-development.md
git commit -m "book: chapter 4, spec-driven development

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 9: Chapter 5, The Failure of Natural Language

**Files:**
- Create: `manuscript/05-failure-of-natural-language.md`
- Source: `book.md` lines 181–204

**Interfaces:**
- Produces: the ambiguity taxonomy table; normative statements N-1..N-5 of `SPEC-PAY-042` that Chapter 6 assembles into the full spec.

- [ ] **Step 1: Read STYLE.md, the Chapter 5 entry in OUTLINE.md, and `book.md` lines 181–204**

- [ ] **Step 2: Write the chapter**

`# Chapter 5: The Failure of Natural Language`, 4,000 words, sections 5.1–5.6, `## Key Takeaways`.

Required elements:
- Scenario: the sentence "The user must receive a notification if the payment succeeds, unless they have disabled alerts" is read by three engineers and one agent; list four different readings.
- 5.1 expands the draft's four open questions (channel, sync vs async, rollback on notification failure, scope of "disabled alerts") and adds two more (what "succeeds" means: authorized vs settled; what "user" means: payer vs merchant).
- 5.2 table with six ambiguity types (lexical, syntactic, scope, referential, temporal, quantifier), each with a one-line example from a software requirement.
- 5.3 table of MUST/SHALL, MUST NOT/SHALL NOT, SHOULD/RECOMMENDED, SHOULD NOT, MAY/OPTIONAL with meaning and "use when"; the RFC 8174 clarification that only uppercase keywords are normative; the boilerplate sentence to include in every spec.
- 5.4 rewrites the sentence as five numbered normative statements, matching the draft's three (queue on SETTLED; MUST NOT block the payment; opt-out yields SKIPPED audit log) plus two on retry limit and channel selection:

```markdown
- N-1: When a transaction reaches status `SETTLED`, the system **MUST** enqueue one `TransactionNotificationEvent`.
- N-2: Enqueuing or dispatching a notification **MUST NOT** block, delay, or fail the settled transaction.
- N-3: If `preferences.notifications.transaction_receipts` is `false`, the dispatcher **MUST** skip delivery and **MUST** write an audit record with status `SKIPPED`.
- N-4: The dispatcher **MUST** retry a transient provider failure (HTTP 5xx or timeout) at most 3 times, then **MUST** move the event to the dead-letter queue.
- N-5: The delivery channel **MUST** be the one in `preferences.notifications.channel`; if unset, the system **MUST** use email.
```

- 5.5 four misuses, each with a wrong sentence and its fix.
- 5.6 a before/after list of five vague phrases ("fast", "recent", "large", "soon", "some") and their quantified replacements.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/05-failure-of-natural-language.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/05-failure-of-natural-language.md
git commit -m "book: chapter 5, the failure of natural language

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 10: Chapter 6, A Composite Grammar

**Files:**
- Create: `manuscript/06-composite-grammar.md`
- Source: `book.md` lines 206–289

**Interfaces:**
- Consumes: N-1..N-5 from Chapter 5 (repeat them verbatim inside the assembled spec).
- Produces: the full `SPEC-PAY-042` example (schema, state diagram) reused in Chapters 8, 10, 12, 13.

- [ ] **Step 1: Read STYLE.md, the Chapter 6 entry in OUTLINE.md, `book.md` lines 206–289, and section 5.4 of `manuscript/05-failure-of-natural-language.md`**

- [ ] **Step 2: Write the chapter**

`# Chapter 6: A Composite Grammar: Markdown, Schemas, Diagrams`, 4,200 words, sections 6.1–6.7, `## Key Takeaways`.

Required elements:
- 6.3 the JSON Schema from the draft upgraded to 2020-12, with `channel` added as an enum of `email`, `sms`, `push`, `webhook`, and each keyword explained in a following list (`format: uuid`, `minimum: 1`, `pattern: ^[A-Z]{3}$`, `required`, `additionalProperties: false`).
- 6.4 the same payload as a Pydantic model and as a TypeScript type, each under 20 lines, with a paragraph on when a type-language beats JSON Schema (when the agent generates in that language anyway) and when it does not (cross-language contracts).
- 6.5 the draft's `stateDiagram-v2` in a ```` ```mermaid ```` fence with English labels, plus a `sequenceDiagram` with participants Payments, Queue, Dispatcher, Provider, AuditLog.
- 6.6 the assembled spec as one Markdown block with headings `### SPEC-PAY-042: Transaction Confirmation Notifications`, `#### 1. Normative Constraints` (N-1..N-5), `#### 2. Payload Model`, `#### 3. Delivery State Machine`, `#### 4. Failure Matrix` (four rows: provider 5xx, provider 4xx, malformed payload, preference service unavailable).
- 6.7 three things to leave out and why.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/06-composite-grammar.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/06-composite-grammar.md
git commit -m "book: chapter 6, a composite grammar

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 11: Chapter 7, The Three Levels of a Spec

**Files:**
- Create: `manuscript/07-three-levels-of-a-spec.md`
- Source: `book.md` lines 291–336

**Interfaces:**
- Produces: **The Three Levels** (named principle), the Failure Modes Matrix format, the decision-table format, `SPEC-ARCH-000` and `SPEC-ACCT-003` excerpts.

- [ ] **Step 1: Read STYLE.md, the Chapter 7 entry in OUTLINE.md, `book.md` lines 291–336, and section 3.5 of Chapter 3 (the `withdraw` contract)**

- [ ] **Step 2: Write the chapter**

`# Chapter 7: The Three Levels of a Spec`, 4,200 words, sections 7.1–7.5, `## Key Takeaways`.

Required elements:
- 7.1 the draft's nested-box ASCII diagram in a plain code fence.
- 7.2 a `SPEC-ARCH-000` excerpt of about 25 lines: the dependency rule (dependencies point inward; the domain imports no database, web, or framework code), allowed component kinds (ports, entities, use cases, adapters), technology constraints (language, strict type checking, no floats for money).
- 7.3 the draft's Failure Modes Matrix translated (columns: Error condition, Category, Domain code, HTTP/RPC status, Required action; rows: source account missing, insufficient funds, persistence timeout, malformed payload), followed by a five-step procedure to build one (list inputs; list each external dependency; for each, list ways it fails; classify business/contract/infrastructure; assign code and action).
- 7.4 the draft's withdrawal decision table translated and labelled `SPEC-ACCT-003 §6`, R1–R4 with columns Rule, Balance ≥ requested, Daily limit respected, Fraud score LOW, Outcome, Side effect; then two checks: completeness (every combination of conditions maps to exactly one rule, show the 2³ = 8 combinations collapse into R1–R4 with "any" wildcards) and consistency (no two rules match the same input with different outcomes).
- 7.5 a table: task type (new use case, new adapter, bug in state logic) versus which level files the agent must read.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/07-three-levels-of-a-spec.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/07-three-levels-of-a-spec.md
git commit -m "book: chapter 7, the three levels of a spec

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 12: Chapter 8, SOLID for Specifications

**Files:**
- Create: `manuscript/08-solid-for-specifications.md`
- Source: `book.md` lines 338–371

**Interfaces:**
- Produces: the five spec principles named Single Responsibility Spec, Open/Closed Spec, Liskov Substitution for Specs, Interface Segregation Spec, Dependency Inversion Spec; the summary table that Chapter 13 references.

- [ ] **Step 1: Read STYLE.md, the Chapter 8 entry in OUTLINE.md, and `book.md` lines 338–371**

- [ ] **Step 2: Write the chapter**

`# Chapter 8: SOLID for Specifications`, 4,200 words, sections 8.1–8.6, `## Key Takeaways`.

Required elements:
- Each of 8.1–8.5 has H3 sub-sections "The principle", "A violation", "The fix", "Rule of thumb".
- 8.1 violation: one file mixing user-profile validation and payment-gateway fee calculation; fix: two specs and a shared value-object spec; rule of thumb: the 300-line limit (forward reference to Chapter 9).
- 8.2 violation: adding SMS receipts by editing `SPEC-PAY-042 §1`; fix: a new subscriber spec that consumes `TransactionNotificationEvent`.
- 8.3 `PaymentGatewayPort` abstract contract with idempotency tolerance of duplicate calls within 60 seconds; violation: an adapter requiring an extra mandatory `merchant_ref` parameter; explain in terms of Chapter 3 (an adapter may not strengthen preconditions or weaken postconditions).
- 8.4 the 50-endpoint monolithic API schema handed to an agent; fix: a role-specific view containing only the two endpoints the task touches; mention the lost-in-the-middle effect from Chapter 2.
- 8.5 the draft's violation ("save the result to PostgreSQL table tax_records with an UPSERT") and correction (`TaxRecordPersistencePort.save(TaxRecord)`); place the example inside `SPEC-BILL-017`.
- 8.6 table: Principle, What it means for a spec, Smell it prevents (Omniprompt, Domain Leakage, and so on, forward-referencing Chapter 13).

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/08-solid-for-specifications.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/08-solid-for-specifications.md
git commit -m "book: chapter 8, SOLID for specifications

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 13: Chapter 9, Naming, Structure, and Size of a Spec

**Files:**
- Create: `manuscript/09-naming-structure-size.md`
- Source: none (new chapter); reuse conventions from STYLE.md §6–§8

**Interfaces:**
- Produces: the nine mandatory sections in fixed order and the header block. Appendix A (Task 23) and `SPEC-CORE-001` in Chapter 15 must use exactly these section names: Scope, Normative Constraints, Data Model, Invariants, Failure Matrix, State Rules, Test Requirements, Open Questions, Changelog.

- [ ] **Step 1: Read STYLE.md and the Chapter 9 entry in OUTLINE.md**

- [ ] **Step 2: Write the chapter**

`# Chapter 9: Naming, Structure, and Size of a Spec`, 4,000 words, sections 9.1–9.7, `## Key Takeaways`.

Required elements:
- 9.1 the ID grammar `SPEC-<DOMAIN>-<NNN>`: domain is 3–6 uppercase letters, number is zero-padded and never reused; IDs are immutable even when the title changes; section citations `SPEC-PAY-042 §3`.
- 9.2 the path pattern `specs/modules/<domain>/SPEC-<DOMAIN>-<NNN>-<slug>.md` and companion `SPEC-<DOMAIN>-<NNN>.schema.json`.
- 9.3 the YAML header:

```yaml
---
id: SPEC-PAY-042
title: Transaction Confirmation Notifications
version: 1.2.0
status: active        # draft | review | active | deprecated
owner: payments-team
depends_on: [SPEC-ARCH-000]
supersedes: null
---
```

- 9.4 one H3 per mandatory section with two or three sentences on what belongs there and what does not; an explicit rule that empty sections stay in the file with the single word "None." so the absence is a decision, not an omission.
- 9.5 arithmetic: about 300 lines is roughly 2,500–4,000 tokens; an agent's working context must also hold Level 0, the instruction file, and the code it edits; three splitting rules (by bounded context, by level, by actor); what to do when it will not fit (it is two specs).
- 9.6 numbering N-, P-, Q-, I- and the rule that numbers are never renumbered after status `active` (deprecate with strikethrough instead).
- 9.7 the four statuses with allowed transitions, detailed in Chapter 12.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/09-naming-structure-size.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/09-naming-structure-size.md
git commit -m "book: chapter 9, naming structure and size of a spec

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 14: Chapter 10, Spec-First, Test-First

**Files:**
- Create: `manuscript/10-spec-first-test-first.md`
- Source: `book.md` lines 377–414

**Interfaces:**
- Consumes: `SPEC-ACCT-003` decision table (Chapter 7), `SPEC-CORE-001` invariants (draft lines 636–650).
- Produces: **The Three Gates** (named principle).

- [ ] **Step 1: Read STYLE.md, the Chapter 10 entry in OUTLINE.md, `book.md` lines 377–414 and 636–663**

- [ ] **Step 2: Write the chapter**

`# Chapter 10: Spec-First, Test-First`, 4,200 words, sections 10.1–10.6, `## Key Takeaways`.

Required elements:
- Scenario: a test `test_discount_10_percent` passes because the agent returned the literal expected number.
- 10.1 a three-row table: spec element (decision table row, schema bound, invariant) to test kind (example test, boundary test, property test) with an example from `SPEC-ACCT-003` rules R1–R4.
- 10.2 the two cart properties from the draft as formulas each followed by a sentence; the draft's Hypothesis test (cleaned up, under 20 lines) and a fast-check equivalent in TypeScript under 20 lines.
- 10.3 one pytest function per row of the `SPEC-CORE-001` failure matrix, sketched as four short functions raising `UnbalancedTransactionError`, `CurrencyMismatchError`, `InsufficientEntriesError`, `CircularEntryError`.
- 10.4 the draft's three-gate ASCII diagram in a plain code fence; name the gates lint, strict type check (`mypy --strict`, `tsc --noEmit --strict`), contract tests.
- 10.5 the rule that when the agent cannot write a test for a statement, the statement is not testable and the spec must change; give one example (a SHOULD without a metric).
- 10.6 defines spec coverage as the share of numbered statements (N-, P-, Q-, I-, failure rows, decision rows) that have at least one test referencing them by ID.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/10-spec-first-test-first.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/10-spec-first-test-first.md
git commit -m "book: chapter 10, spec-first test-first

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 15: Chapter 11, Anatomy of a Spec-Driven Agent

**Files:**
- Create: `manuscript/11-anatomy-of-a-spec-driven-agent.md`
- Source: `book.md` lines 416–466

**Interfaces:**
- Produces: the constrained loop (Init, Plan, Execute, Validate), the Delta, the repository tree, the instruction-file example reused in Chapter 17.

- [ ] **Step 1: Read STYLE.md, the Chapter 11 entry in OUTLINE.md, and `book.md` lines 416–466**

- [ ] **Step 2: Write the chapter**

`# Chapter 11: Anatomy of a Spec-Driven Agent`, 4,200 words, sections 11.1–11.6, `## Key Takeaways`.

Required elements:
- 11.1 the loop as a Mermaid `stateDiagram-v2` (states Init, Plan, Execute, Validate, Done; Validate to Execute on failure with the Delta; Validate to Done on success) and the sentence explaining `Delta = expected (from spec) − observed (from run)`; the rule that on failure the agent receives only the Delta, not the whole context again.
- 11.2 a table with columns "Always in context", "In context for this task", "Never in context" listing instruction file, Level 0 spec, the one module spec, the failing test output, unrelated specs, chat history, and so on.
- 11.3 the draft's repository tree translated, in a plain code fence.
- 11.4 the full instruction file in English, in a Markdown code fence, with sections SOURCE OF TRUTH, WORKFLOW (four steps), CODING CONSTRAINTS, STOP CONDITIONS; keep it under 40 lines.
- 11.5 three stop conditions: a statement the agent cannot test, two statements that conflict, a needed behavior no statement covers; the required output is a question that proposes a spec change, never an assumption.
- 11.6 three roles with what each reads and produces.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/11-anatomy-of-a-spec-driven-agent.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/11-anatomy-of-a-spec-driven-agent.md
git commit -m "book: chapter 11, anatomy of a spec-driven agent

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 16: Chapter 12, Specs Under Version Control

**Files:**
- Create: `manuscript/12-specs-under-version-control.md`
- Source: `book.md` lines 468–514

**Interfaces:**
- Produces: the spec/impl commit pair format and the reverse-drift procedure reused in Chapter 17.

- [ ] **Step 1: Read STYLE.md, the Chapter 12 entry in OUTLINE.md, and `book.md` lines 468–514**

- [ ] **Step 2: Write the chapter**

`# Chapter 12: Specs Under Version Control: Lifecycle, Drift, Traceability`, 4,000 words, sections 12.1–12.6, `## Key Takeaways`.

Required elements:
- 12.1 the two commit messages from the draft in English, using `SPEC-BILL-017` (`spec(billing): formalize tiered subscription upgrade invariants` and `impl(billing): synthesize subscription upgrade use case from spec <hash>`), with the convention that an `impl` commit names the spec commit it implements.
- 12.2 semantic versioning for specs: patch for wording, minor for added statements that keep old behavior valid, major for changed or removed statements; the Changelog section format (version, date, statements touched).
- 12.3 statuses draft, review, active, deprecated with a Mermaid `stateDiagram-v2`.
- 12.4 the three drift checks from the draft (schema check, exhaustive error coverage, traceability tags) and the `@implements_spec("SPEC-BILL-017", section="1.2")` decorator example with a short Python definition of the decorator (under 15 lines).
- 12.5 a sample CI configuration snippet (YAML, generic runner) with jobs lint-spec, schema-check, error-coverage, traceability.
- 12.6 the reverse-drift procedure as a numbered list: tag the hotfix commit; open a spec change with the observed behavior; decide keep or revert; regenerate; close within one sprint.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/12-specs-under-version-control.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/12-specs-under-version-control.md
git commit -m "book: chapter 12, specs under version control

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 17: Chapter 13, A Catalog of Spec Smells

**Files:**
- Create: `manuscript/13-catalog-of-spec-smells.md`
- Source: `book.md` lines 518–562

**Interfaces:**
- Produces: eleven smell names that Chapter 14 and Appendix C reference exactly: The Omniprompt, The Handwave, Syntactic Micromanagement, Domain Leakage, Happy Path Only, Ghost Invariant, Prose State Machine, Example as Specification, Modal Mush, Primitive Obsession, Zombie Spec.

- [ ] **Step 1: Read STYLE.md, the Chapter 13 entry in OUTLINE.md, `book.md` lines 518–562, and the Chapter 14 refactoring names in OUTLINE.md**

- [ ] **Step 2: Write the chapter**

`# Chapter 13: A Catalog of Spec Smells`, 5,000 words, an intro section `## 13.0 Why Name a Smell`, then `## 13.1` to `## 13.11`, then `## 13.12 Summary`, then `## Key Takeaways`.

Each smell section has H3s **Symptom**, **Example**, **Consequence**, **Cure**. Cure names the Chapter 14 refactoring:

| Smell | Cure |
| :--- | :--- |
| The Omniprompt | Extract Bounded Context Spec |
| The Handwave | Introduce Failure Matrix; Normalize Modal Verbs |
| Syntactic Micromanagement | Replace Procedure with Postcondition |
| Domain Leakage | Invert Infrastructure Dependency |
| Happy Path Only | Introduce Failure Matrix |
| Ghost Invariant | Extract Invariant from Examples |
| Prose State Machine | Replace Prose with State Table |
| Example as Specification | Extract Invariant from Examples |
| Modal Mush | Normalize Modal Verbs |
| Primitive Obsession | Replace Primitive with Value Object |
| Zombie Spec | (no refactoring; Chapter 12 lifecycle: deprecate or reconcile) |

Examples: reuse the draft's quotes for the first four ("Handle errors robustly and elegantly", the `let i = 0` loop instruction, the `UPDATE customers SET discount` sentence). For the new seven, write one short quoted example each set at Meridian. 13.12 is a table: Smell, Detection question, Refactoring.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/13-catalog-of-spec-smells.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/13-catalog-of-spec-smells.md
git commit -m "book: chapter 13, a catalog of spec smells

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 18: Chapter 14, A Catalog of Spec Refactorings

**Files:**
- Create: `manuscript/14-catalog-of-spec-refactorings.md`
- Source: `book.md` lines 564–599

**Interfaces:**
- Consumes: smell names from Chapter 13 (each refactoring names the smells it cures).
- Produces: nine refactoring names, and the `FSM-ORD-01` state table of `SPEC-ORD-007` reused in Chapter 17.

- [ ] **Step 1: Read STYLE.md, the Chapter 14 entry in OUTLINE.md, `book.md` lines 564–599, and the smell list in `manuscript/13-catalog-of-spec-smells.md`**

- [ ] **Step 2: Write the chapter**

`# Chapter 14: A Catalog of Spec Refactorings`, 5,000 words, `## 14.0 How to Read a Refactoring`, then `## 14.1` to `## 14.9`, then `## Key Takeaways`.

Each refactoring has H3s **Motivation** (names the smells it cures), **Mechanics** (numbered steps), **Example** (Before and After as two Markdown blocks).

- 14.1 Replace Prose with State Table: the draft's order prose and the `FSM-ORD-01` table translated (columns From, Event, Guard, To, Side effects (ports); rows PENDING/PAYMENT_RECEIVED, PENDING/PAYMENT_FAILED, PENDING/USER_CANCELLED, PAID/USER_CANCELLED, PAID/SHIPMENT_DISPATCHED, SHIPPED/USER_CANCELLED, REFUNDING/REFUND_SETTLED), labelled `SPEC-ORD-007 §6`.
- 14.2 Extract Bounded Context Spec: the draft's three mechanics steps expanded to six; before: a 900-line spec header list; after: three spec headers with `depends_on`.
- 14.3 Introduce Failure Matrix: before "handle errors robustly"; after a four-row matrix.
- 14.4 Replace Primitive with Value Object: before `amount: number, currency: string`; after `Money` with invariants.
- 14.5 Extract Invariant from Examples: before three examples of discounts; after the invariant "final price ≥ 0 and ≤ subtotal".
- 14.6 Normalize Modal Verbs: before a paragraph with "should", "needs to", "will", "can"; after RFC 2119 statements.
- 14.7 Replace Procedure with Postcondition: before the `let i = 0` loop; after a Q- clause about the resulting map.
- 14.8 Invert Infrastructure Dependency: before the UPDATE statement; after a port call plus an adapter spec reference.
- 14.9 Split Role-Specific View: before "see the full API schema"; after a two-endpoint view file.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/14-catalog-of-spec-refactorings.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/14-catalog-of-spec-refactorings.md
git commit -m "book: chapter 14, a catalog of spec refactorings

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 19: Chapter 15, Case Study: A Double-Entry Ledger

**Files:**
- Create: `manuscript/15-case-study-double-entry-ledger.md`
- Source: `book.md` lines 603–663

**Interfaces:**
- Consumes: the nine mandatory sections and header block from Chapter 9; the test kinds from Chapter 10.
- Produces: the full `SPEC-CORE-001`.

- [ ] **Step 1: Read STYLE.md, the Chapter 15 entry in OUTLINE.md, `book.md` lines 603–663, and section 9.3–9.4 of `manuscript/09-naming-structure-size.md`**

- [ ] **Step 2: Write the chapter**

`# Chapter 15: Case Study: A Double-Entry Ledger`, 4,500 words, sections 15.1–15.6, `## Key Takeaways`.

Required elements:
- 15.2 the complete spec in one Markdown code fence, with the YAML header (id `SPEC-CORE-001`, version 1.0.0, status active, depends_on `[SPEC-ARCH-000]`) and all nine sections in Chapter 9 order. Content from the draft: pure domain layer, no floats (MUST NOT), `Money` (`amount_cents` positive integer, `currency` ISO 4217), `LedgerEntry`, `Transaction` (at least two entries; status DRAFT/POSTED/REJECTED); invariants I-1 balance (sum of debits equals sum of credits, formula plus sentence), I-2 currency uniformity, I-3 non-zero amounts; the four-row failure matrix; the three test requirements (random unbalanced transactions, idempotent posting, global balance conservation); Open Questions "None."; Changelog with one entry. After the fence, commentary paragraphs per section explaining the choices.
- 15.3 the test suite outline: three Hypothesis property tests (sketched, under 25 lines each) and four failure-matrix tests as names only.
- 15.4 Python dataclasses `Money`, `LedgerEntry`, `Transaction` with a `post()` method enforcing the invariants, under 45 lines total, with `@implements_spec("SPEC-CORE-001", section="4")`.
- 15.5 a walkthrough: an unbalanced transaction, the exception raised, the status set to REJECTED, no balance changed.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/15-case-study-double-entry-ledger.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/15-case-study-double-entry-ledger.md
git commit -m "book: chapter 15, case study double-entry ledger

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 20: Chapter 16, Case Study: Reverse-Specifying a Legacy System

**Files:**
- Create: `manuscript/16-case-study-reverse-specifying-legacy.md`
- Source: `book.md` lines 665–702

**Interfaces:**
- Produces: `SPEC-RATE-009` and the four-phase method.

- [ ] **Step 1: Read STYLE.md, the Chapter 16 entry in OUTLINE.md, and `book.md` lines 665–702**

- [ ] **Step 2: Write the chapter**

`# Chapter 16: Case Study: Reverse-Specifying a Legacy System`, 4,200 words, sections 16.1–16.6, `## Key Takeaways`.

Required elements:
- 16.2 the draft's four-phase ASCII diagram translated, in a plain code fence, with a paragraph per phase.
- 16.3 the draft's three rules expanded, each with a one-line legacy symptom and the spec construct it becomes (port, value object, decision table).
- 16.4 a legacy Python fragment of about 30 lines computing a shipping rate with nested ifs, a global `SURCHARGE` mutated inside the function, a `weight` variable reused for volumetric weight, and a direct database call; then the agent's raw reverse spec (about 15 lines, deliberately containing one Handwave and one Ghost Invariant); then the audited `SPEC-RATE-009 §6` decision table with rules for weight band, destination zone, express flag, and the outcome rate; then two characterization tests pinning current behavior.
- 16.6 the rule that behavior nobody wants is recorded in the spec as deprecated with a target version, never silently dropped.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/16-case-study-reverse-specifying-legacy.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/16-case-study-reverse-specifying-legacy.md
git commit -m "book: chapter 16, case study reverse-specifying a legacy system

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 21: Chapter 17, Case Study: One Feature, End to End

**Files:**
- Create: `manuscript/17-case-study-one-feature.md`
- Source: none (new chapter); reuses Chapters 9, 11, 12, 14

**Interfaces:**
- Consumes: the header block and nine sections (Chapter 9), the instruction file and stop conditions (Chapter 11), the commit pair and versioning rules (Chapter 12), `FSM-ORD-01` (Chapter 14).
- Produces: `SPEC-INV-021`.

- [ ] **Step 1: Read STYLE.md, the Chapter 17 entry in OUTLINE.md, and sections 9.3–9.4, 11.4–11.5, 12.1–12.2, 14.1 of the corresponding chapter files**

- [ ] **Step 2: Write the chapter**

`# Chapter 17: Case Study: One Feature, End to End`, 5,000 words, sections 17.1–17.6, `## Key Takeaways`.

Required elements:
- Scenario: the ticket text, verbatim, in a blockquote: "Reserve stock when the customer starts checkout so two people can't buy the last unit. Release it after 15 minutes if they don't pay."
- 17.1 `SPEC-INV-021` v0.1 as a Markdown block: header (status draft), Scope, and five normative statements written quickly and imperfectly.
- 17.2 a review that finds Modal Mush (a "should" that means MUST), Happy Path Only (no failure matrix), Prose State Machine (the reservation lifecycle in prose); each fixed by the named refactoring; v1.0 shown with a state table (states REQUESTED, HELD, CONSUMED, RELEASED, EXPIRED; events CHECKOUT_STARTED, PAYMENT_CONFIRMED, PAYMENT_ABANDONED, TIMER_ELAPSED), a failure matrix (out of stock, unknown SKU, duplicate reservation key, inventory service timeout), and test requirements.
- 17.3 hypothetical agent transcript excerpts in blockquotes labelled "Agent:" and "Engineer:", showing the plan and the list of generated tests named by statement ID.
- 17.4 the failing test: `TIMER_ELAPSED` arrives while the order is in payment; the table has no row for HELD + TIMER_ELAPSED when a payment is in flight; the agent halts with the stop-condition question from Chapter 11.
- 17.5 v1.1 adds a guard "no payment in flight" and a new row; the Changelog entry; the spec commit and the impl commit shown as in Chapter 12.
- 17.6 a table of the three defects the spec caught versus what a prompt-only flow would have produced.

- [ ] **Step 3: Lint and fix**

Run: `python tools/check_manuscript.py manuscript/17-case-study-one-feature.md`
Expected: `OK`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/17-case-study-one-feature.md
git commit -m "book: chapter 17, case study one feature end to end

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 22: Epilogue

**Files:**
- Create: `manuscript/18-epilogue.md`
- Source: `book.md` lines 704–707

- [ ] **Step 1: Read STYLE.md, the Epilogue entry in OUTLINE.md, and `book.md` lines 704–707**

- [ ] **Step 2: Write the file**

`# Epilogue: The Specification Is the Software`, 2,000 words, no numbered sections, no Key Takeaways. Themes: engineers as architects of constraints, not syntax laborers; what changes for careers (the skill that compounds is writing what must be true), for teams (review specs, not diffs), for education; the honest limits (specs are hard, agents fail, the discipline costs); a closing charge in the second person of about 150 words.

- [ ] **Step 3: Lint**

Run: `python tools/check_manuscript.py manuscript/18-epilogue.md`
Expected: `OK 18-epilogue.md: <1500-3000> words`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/18-epilogue.md
git commit -m "book: epilogue

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 23: Appendices

**Files:**
- Create: `manuscript/19-appendices.md`

**Interfaces:**
- Consumes: the nine sections and header (Chapter 9), the RFC 2119 table (Chapter 5), the eleven smells (Chapter 13), terminology (STYLE.md §10 and all chapters).

- [ ] **Step 1: Read STYLE.md, the Appendices entry in OUTLINE.md, and sections 9.3–9.4, 5.3, 13.12 of the corresponding chapter files**

- [ ] **Step 2: Write the file**

`# Appendices` as the single H1, then `## Appendix A: Clean Spec Template`, `## Appendix B: RFC 2119 Cheat Sheet`, `## Appendix C: Spec Review Checklist`, `## Appendix D: Glossary`. About 4,500 words.

- A: one Markdown code fence containing the YAML header with placeholder values in angle brackets (`<SPEC-DOMAIN-NNN>`) and all nine sections with a one-line instruction under each, plus the RFC 2119 boilerplate sentence.
- B: the keyword table from Chapter 5 plus ten one-line do/don't pairs.
- C: a checklist with `- [ ]` items grouped by Structure (header present, nine sections, under 300 lines, IDs registered), Content (one question per smell from Chapter 13, phrased as a yes/no question), Testability (every N-/P-/Q-/I- has a test requirement), Lifecycle (status, version, changelog entry).
- D: about 40 terms, alphabetical, one or two sentences each, including: agent instruction file, bounded context, constraint density, contract test, decision table, Delta, drift, failure matrix, Hoare triple, invariant, Level 0/1/2, port, postcondition, precondition, property-based test, reverse spec, spec coverage, spec ID, SDD, Three Gates, value object, vibecoding, Zombie Spec.

- [ ] **Step 3: Lint**

Run: `python tools/check_manuscript.py manuscript/19-appendices.md`
Expected: `OK 19-appendices.md: <3000-7000> words`.

- [ ] **Step 4: Commit**

```powershell
git add manuscript/19-appendices.md
git commit -m "book: appendices

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

### Task 24: Consistency pass and build

**Files:**
- Modify: any `manuscript/*.md` that fails a check below
- Modify: `README.md` (add total word count and build status)

- [ ] **Step 1: Run the full lint**

Run: `python tools/check_manuscript.py`
Expected: every line `OK`, `TOTAL` between 65,000 and 80,000 words. Fix any failure in the chapter file.

- [ ] **Step 2: Check cross-references resolve to the intended chapter**

Run:

```powershell
Select-String -Path manuscript/*.md -Pattern 'Chapter (\d+)' -AllMatches | ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Group-Object | Sort-Object { [int]$_.Name } | Format-Table Name, Count
```

Then for each chapter number, spot-check two references by opening the referencing sentence and confirming the target chapter's H1 matches the claim (for example a reference to "the Golden Rule in Chapter 4" must land on `04-spec-driven-development.md`). Fix mismatches.

- [ ] **Step 3: Check named principles and smells are spelled consistently**

Run:

```powershell
foreach ($t in 'Golden Rule of Clean Spec','Constraint Density','Three Levels','Three Gates','300-Line Rule','The Omniprompt','The Handwave','Syntactic Micromanagement','Domain Leakage','Happy Path Only','Ghost Invariant','Prose State Machine','Example as Specification','Modal Mush','Primitive Obsession','Zombie Spec') { $n = (Select-String -Path manuscript/*.md -Pattern ([regex]::Escape($t)) -AllMatches | ForEach-Object { $_.Matches.Count } | Measure-Object -Sum).Sum; "$n`t$t" }
```

Expected: every term appears at least twice (defined once, referenced at least once). Search for near-misses (`Golden rule`, `three gates`, `Omni-prompt`) and normalize.

- [ ] **Step 4: Check the nine mandatory section names match across Chapter 9, Chapter 15, Chapter 17, and Appendix A**

Run:

```powershell
Select-String -Path manuscript/09-*.md,manuscript/15-*.md,manuscript/17-*.md,manuscript/19-*.md -Pattern '^#+ *\d*\.? *(Scope|Normative Constraints|Data Model|Invariants|Failure Matrix|State Rules|Test Requirements|Open Questions|Changelog)\b' | Select-Object Filename, Line
```

Expected: each of the nine names appears in each of the four files. Fix any variant spelling.

- [ ] **Step 5: Check terminology bans from STYLE.md §10**

Run:

```powershell
Select-String -Path manuscript/0*.md,manuscript/1*.md -Pattern '\b(the bot|copilot|AI code|error table|rules table|spec-first development)\b' -CaseSensitive:$false
```

Expected: no matches. Fix any that appear outside a deliberate "do not say" context.

- [ ] **Step 6: Build**

Run: `pwsh build/build.ps1`
Expected: `Wrote ...build/out/clean-spec.md (20 files)` and, since Pandoc is absent, the warning with install instructions. Open `build/out/clean-spec.md` and confirm the five Part headings appear before chapters 1, 5, 10, 13, 15.

- [ ] **Step 7: Update README.md**

Add under the title a line "Manuscript status: complete draft, N words (run `python tools/check_manuscript.py` for the current count)." with N from Step 1, and a line noting that Pandoc was not available on the authoring machine so rendered outputs are not committed.

- [ ] **Step 8: Commit**

```powershell
git add -A
git commit -m "book: consistency pass and build script run

Claude-Session: https://claude.ai/code/session_01LfJ5T8ubdHdvg1iHSwbDpr"
```

---

## Self-review notes

- Spec coverage: front matter (Task 4), Parts I–V chapters 1–17 (Tasks 5–21), epilogue (Task 22), appendices A–D (Task 23), STYLE.md (Task 2), OUTLINE.md (Task 3), `build/metadata.yaml` and `build/build.ps1` (Task 1), README (Tasks 1 and 24), final consistency pass and build (Task 24), `book.md` untouched (no task edits it; Task 1 only adds it to git).
- Chapter conventions (word range, scenario, Key Takeaways, tables/diagrams, cross-references by chapter number and spec ID) are enforced by the lint script and repeated in each chapter task.
- Spec IDs: the eight IDs in STYLE.md §8 match `KNOWN_SPEC_IDS` in Task 1 and are the only IDs used in Tasks 5–23. `FSM-ORD-01` is a state-machine label inside `SPEC-ORD-007`, not a spec ID, so the lint regex does not match it.
- Section names: the nine mandatory sections are spelled identically in Tasks 13, 19, 21, 23 and checked in Task 24 Step 4.
- Smell and refactoring names: Task 17's table and Task 18's list use the same strings; Task 23 Appendix C reuses the Task 17 names.
