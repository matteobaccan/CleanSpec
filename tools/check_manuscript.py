#!/usr/bin/env python3
"""Lint the Clean Spec manuscript.

Usage:
    python tools/check_manuscript.py                 # check every chapter file
    python tools/check_manuscript.py manuscript/05-failure-of-natural-language.md

Exit code 0 when every checked file passes, 1 otherwise.

Fenced code blocks are excluded from the heading, placeholder, language, and
cross-reference checks (word count, fence balance, and spec ID checks still
see the full text, fences included).
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


def strip_fenced_code(text: str) -> str:
    return re.sub(r"^```.*?^```[ \t]*$", "", text, flags=re.S | re.M)


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", text))


def check_file(path: pathlib.Path) -> tuple[int, list[str]]:
    errors: list[str] = []
    raw = path.read_text(encoding="utf-8")
    text = strip_html_comments(raw)
    prose = strip_fenced_code(text)
    prefix = path.name[:2]

    words = count_words(text)
    lo, hi = LIMITS.get(prefix, CHAPTER_LIMITS)
    if not lo <= words <= hi:
        errors.append(f"word count {words} is outside {lo}-{hi}")

    h1_lines = [line for line in prose.splitlines() if line.startswith("# ")]
    allowed = H1_ALLOWED.get(prefix, 1)
    if len(h1_lines) != allowed:
        errors.append(f"expected {allowed} H1 heading(s), found {len(h1_lines)}")

    if not text.lstrip().startswith("# "):
        errors.append("file must start with an H1 heading")

    if prefix in CHAPTER_PREFIXES:
        if "## Key Takeaways" not in prose:
            errors.append("missing '## Key Takeaways' section")
        elif not prose.rstrip().split("## Key Takeaways")[-1].strip().startswith("-"):
            errors.append("'## Key Takeaways' must be followed by a bulleted list")

    for pattern in FORBIDDEN:
        for m in re.finditer(pattern, prose, flags=re.IGNORECASE):
            errors.append(f"forbidden placeholder {m.group(0)!r}")

    for m in ITALIAN.finditer(prose):
        errors.append(f"possible Italian leftover {m.group(0)!r}")

    if text.count("```") % 2:
        errors.append("unbalanced code fences")

    for m in SPEC_ID.finditer(text):
        if m.group(0) not in KNOWN_SPEC_IDS:
            errors.append(f"unregistered spec id {m.group(0)}; add it to STYLE.md and KNOWN_SPEC_IDS")

    for m in CHAPTER_REF.finditer(prose):
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
