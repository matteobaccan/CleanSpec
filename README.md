# Clean Spec: Specification Engineering for the Age of AI

A book about writing specifications that coding agents can compile into correct software.

## Layout

- `book.md` — original Italian draft (source material, never edited).
- `manuscript/` — the English manuscript, one file per chapter, plus `STYLE.md` and `OUTLINE.md`.
- `tools/check_manuscript.py` — lint script that enforces the chapter conventions.
- `build/build.ps1` — concatenates the chapters and renders EPUB/DOCX/PDF with Pandoc.
- `assets/cover/` — the cover art: `cover.svg` (source, edit this one), `cover.png` (rendered, used as the EPUB cover image), `cover.jpg` (alternate format).
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

Requires [Pandoc](https://pandoc.org). PDF output also needs a LaTeX engine (MiKTeX or TeX Live). Mermaid diagrams are kept as fenced code blocks; use a Pandoc Mermaid filter to render them as images. The EPUB build embeds `assets/cover/cover.png` automatically when the file exists.

## Cover

Edit `assets/cover/cover.svg`, then re-render the raster copy used by the build:

```powershell
magick -background none -density 150 assets/cover/cover.svg assets/cover/cover.png
```
