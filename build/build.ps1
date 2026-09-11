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
$cover = Join-Path $root 'assets/cover/cover.png'
foreach ($fmt in $Formats) {
    $target = Join-Path $out "clean-spec.$fmt"
    $args = @($combined, '--metadata-file', $meta, '--from', 'markdown+smart', '--toc', '--top-level-division=chapter', '-o', $target)
    if ((Test-Path $cover) -and $fmt -eq 'epub') {
        # cover-image is an EPUB-only metadata key in Pandoc's default templates;
        # the plain LaTeX template used for PDF ignores it without a custom template.
        $args += @('--metadata', "cover-image=$cover")
    }
    if ($fmt -eq 'pdf') {
        $engine = @('xelatex', 'lualatex', 'pdflatex') | Where-Object { Get-Command $_ -ErrorAction SilentlyContinue } | Select-Object -First 1
        if (-not $engine) {
            Write-Warning 'No LaTeX engine found; skipping PDF. Install MiKTeX or TeX Live to enable it.'
            continue
        }
        $args += @('--pdf-engine', $engine)
        if (Test-Path $cover) {
            # Pandoc's plain LaTeX template has no titlepage-image hook, so the
            # cover is injected as a full-bleed page before the body via raw LaTeX:
            # one snippet for the preamble (package), one for right after \begin{document}.
            $coverPath = ($cover -replace '\\', '/')
            $coverHeaderTex = Join-Path $out 'cover-header.tex'
            $coverBodyTex = Join-Path $out 'cover-body.tex'
            # Disable Pandoc's automatic plain-text title page: the cover image
            # already carries the title, subtitle, and author.
            "\usepackage{graphicx}`n\let\maketitle\relax" | Set-Content -Encoding UTF8 $coverHeaderTex
            @"
\begin{titlepage}
\thispagestyle{empty}
\newgeometry{margin=0pt}
\noindent\includegraphics[width=\paperwidth,height=\paperheight]{$coverPath}
\restoregeometry
\end{titlepage}
"@ | Set-Content -Encoding UTF8 $coverBodyTex
            $args += @('--include-in-header', $coverHeaderTex, '--include-before-body', $coverBodyTex)
        }
    }
    Write-Host "pandoc -> $target"
    & pandoc @args
}
Write-Host 'Note: Mermaid blocks are emitted as fenced code. Render them with a Pandoc Mermaid filter if you need images.'
