# Clean Spec — Book Design

Date: 2026-09-10
Status: approved in conversation

## Goal

Produce a complete English-language manuscript titled **Clean Spec: Specification Engineering for the Age of AI**, expanding the Italian draft in `book.md` (about 700 lines, 5 parts, 13 chapters) into a full book of roughly 70,000 words in the style of Robert C. Martin's *Clean Code*.

`book.md` stays untouched as the original source draft.

## Audience and register

- Senior developers, tech leads, and software architects who work with coding agents.
- First-person voice, direct, opinionated, with named principles and before/after examples.
- American English.
- Formulas are allowed but always explained in words; never a formula standing alone.
- Illustrative scenarios are explicitly hypothetical ("Imagine a team that..."). No fabricated personal anecdotes attributed to the author. Where a real anecdote from the author would strengthen a point, leave an HTML comment `<!-- AUTHOR: ... -->` describing what is needed.
- Tools cited only when stable and verifiable: JSON Schema, Mermaid, RFC 2119/8174, Hypothesis, fast-check, mypy, tsc, agent context files such as CLAUDE.md. No product names likely to be obsolete within a year.

## Structure

Front matter: title page, Preface, Who This Book Is For, How to Read This Book.

Part I — Why Specifications Matter Now
1. The Commoditization of Code (draft ch. 1)
2. What a Language Model Does With Your Words (draft 2.1–2.2)
3. Contracts, Not Conversations: Hoare Logic for Working Engineers (draft 2.3, expanded)
4. Spec-Driven Development: Inverting the Flow (draft ch. 3, includes the Golden Rule)

Part II — Anatomy of a Clean Spec
5. The Failure of Natural Language (draft 4.1–4.2, RFC 2119)
6. A Composite Grammar: Markdown, Schemas, Diagrams (draft 4.3)
7. The Three Levels of a Spec (draft ch. 5)
8. SOLID for Specifications (draft ch. 6)
9. Naming, Structure, and Size of a Spec (new: spec IDs, mandatory sections, length limits)

Part III — Verification, Validation, and Agentic Workflows
10. Spec-First, Test-First (draft ch. 7)
11. Anatomy of a Spec-Driven Agent (draft ch. 8)
12. Specs Under Version Control: Lifecycle, Drift, Traceability (draft ch. 9)

Part IV — Spec Smells and Refactorings
13. A Catalog of Spec Smells (draft ch. 10, expanded from 4 to about 10 smells)
14. A Catalog of Spec Refactorings (draft ch. 11, expanded from 2 to about 8, Fowler format: motivation, mechanics, example)

Part V — Case Studies and Practice
15. Case Study: A Double-Entry Ledger (draft ch. 12)
16. Case Study: Reverse-Specifying a Legacy System (draft 13.1–13.2)
17. Case Study: One Feature, End to End (new: realistic feature from spec to commit, showing the agent/spec dialogue)

Epilogue — The Specification Is the Software (draft 13.3)

Appendices: A. Clean Spec template; B. RFC 2119 cheat sheet; C. Spec review checklist; D. Glossary.

## Chapter conventions

- 3,500–5,500 words per chapter.
- Opens with a concrete scenario; closes with a "Key Takeaways" list.
- Tables, Mermaid diagrams, and ASCII diagrams as in the draft.
- Cross-references by chapter number and by spec ID (e.g. SPEC-PAY-042).

## File layout

```
manuscript/
  STYLE.md                 shared style guide for all chapters
  OUTLINE.md               per-chapter outline with section list and target word count
  00-front-matter.md
  01-commoditization-of-code.md
  ...
  17-case-study-one-feature.md
  18-epilogue.md
  19-appendices.md
build/
  metadata.yaml            Pandoc metadata (title, author, language, etc.)
  build.ps1                concatenates manuscript/*.md, runs Pandoc for PDF, EPUB, DOCX
README.md
book.md                    original Italian draft, unchanged
```

## Process

1. Write STYLE.md and OUTLINE.md first; they are the contract every chapter must honor.
2. Write chapters in order.
3. Final consistency pass: terminology, cross-references, spec IDs, key-takeaway format.
4. Build with Pandoc if available; otherwise leave the script ready and report it.
