#!/usr/bin/env python3
"""Build mdBook source from the Grandmaster-Codex pipeline output.

Uses Grandmaster-Codex/build/epub/ which already has diagrams rendered
as image references by the pipeline (no FEN text, no ASCII boards).
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
SRC = HERE / "src"
CODEX = REPO / "Grandmaster-Codex"
PROCESSED = CODEX / "build" / "epub"
DIAGRAM_PNG_DIR = CODEX / "diagrams" / "png"

VOLUMES = [
    ("Volume 1 — Foundations", "Volume-1-Foundations", "volume-1"),
    ("Volume 2 — Club Player", "Volume-2-Club-Player", "volume-2"),
    ("Volume 3 — Tournament Fighter", "Volume-3-Tournament-Fighter", "volume-3"),
    ("Volume 4 — Expert", "Volume-4-Expert", "volume-4"),
    ("Volume 5 — Grandmaster", "Volume-5-Grandmaster", "volume-5"),
]

IMG_REF_RE = re.compile(r'!\[([^\]]*)\]\(diagrams/(png|svg)/([^)]+)\)')
FEN_LINE_RE = re.compile(r'^\s*\*{0,2}FEN\b[^:\n]*:?\*{0,2}\s*`?[^`\n]+`?.*$', re.MULTILINE)


def rewrite_image_paths(text: str) -> str:
    """Make image refs work from book/src/volume-N/chapter.md."""
    return IMG_REF_RE.sub(
        r'<p align="center"><img src="../diagrams/\2/\3" alt="\1" width="360" /></p>',
        text,
    )


def strip_fen_lines(text: str) -> str:
    """Remove any FEN: lines the pipeline didn't catch."""
    return FEN_LINE_RE.sub('', text)


def title_from_filename(name: str) -> str:
    stem = Path(name).stem
    m = re.match(r"^(\d+)([A-Za-z]?)[-_](.+)$", stem)
    if m:
        num, suffix, rest = m.groups()
        rest = rest.replace("_", " ").replace("-", " ").strip().title()
        return f"Chapter {int(num)}{suffix.upper()}: {rest}" if rest else stem
    stem2 = re.sub(r"^[Cc]h(?:apter)?[-_]?\d+[-_]?", "", stem)
    stem2 = stem2.replace("_", " ").replace("-", " ")
    stem2 = re.sub(r"\s+", " ", stem2).strip()
    return stem2.title() if stem2 else Path(name).stem


def title_from_content(path: Path, fallback: str) -> str:
    generic_re = re.compile(
        r"^(the grandmaster codex|grandmaster codex|codex|volume [ivx\d]+.*)$",
        re.IGNORECASE,
    )
    section_re = re.compile(
        r"^(what you'?ll learn|key takeaways|welcome back|introduction|preface|foreword|overview)$",
        re.IGNORECASE,
    )
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped.startswith("# "):
                    text = stripped.lstrip("# ").strip()
                    if generic_re.match(text):
                        continue
                    return text
                if stripped.startswith("## "):
                    text = stripped.lstrip("# ").strip()
                    if text and not generic_re.match(text) and not section_re.match(text):
                        return text
    except OSError:
        pass
    return fallback


def main() -> None:
    if not PROCESSED.is_dir():
        raise SystemExit(
            f"Processed markdown not found at {PROCESSED}. "
            "Run Grandmaster-Codex/pipeline/build_all.sh first."
        )

    if SRC.exists():
        shutil.rmtree(SRC)
    SRC.mkdir(parents=True)

    # Copy the PNG diagrams that the processed markdown references
    diagrams_out = SRC / "diagrams" / "png"
    if DIAGRAM_PNG_DIR.exists():
        shutil.copytree(DIAGRAM_PNG_DIR, diagrams_out)
        print(f"copied {sum(1 for _ in diagrams_out.glob('*.png'))} PNG diagrams")

    summary = ["# Summary", "", "[Introduction](./introduction.md)", ""]

    for display, folder, slug in VOLUMES:
        vol_src = PROCESSED / folder
        if not vol_src.is_dir():
            print(f"skip missing volume: {folder}")
            continue
        vol_dir = SRC / slug
        vol_dir.mkdir(parents=True, exist_ok=True)

        chapters = sorted(p for p in vol_src.iterdir() if p.suffix == ".md")
        summary.append(f"# {display}")
        summary.append("")

        for ch in chapters:
            dest = vol_dir / ch.name
            text = ch.read_text(encoding="utf-8")
            text = rewrite_image_paths(text)
            text = strip_fen_lines(text)
            dest.write_text(text, encoding="utf-8")
            fallback_title = title_from_filename(ch.name)
            if re.match(r"^\d", ch.stem):
                title = fallback_title
            else:
                title = title_from_content(ch, fallback_title)
            summary.append(f"- [{title}](./{slug}/{ch.name})")
        summary.append("")

    summary.append("# Reference")
    summary.append("")
    ref_files = [
        ("BIBLIOGRAPHY.md", "Bibliography"),
        ("RESEARCH_CITATIONS.md", "Research Citations"),
        ("GAME_SOURCES_INDEX.md", "Game Sources Index"),
        ("ACADEMIC_STANDARDS_REPORT.md", "Academic Standards"),
    ]
    ref_dir = SRC / "reference"
    ref_dir.mkdir(exist_ok=True)
    for fname, title in ref_files:
        src_path = CODEX / fname
        if src_path.exists():
            shutil.copy2(src_path, ref_dir / fname)
            summary.append(f"- [{title}](./reference/{fname})")
    summary.append("")

    (SRC / "SUMMARY.md").write_text("\n".join(summary), encoding="utf-8")

    intro = """# The Grandmaster Codex

*A Complete Chess Curriculum from Beginner to Grandmaster*

**By Kit Olivas & Dr. Ada Marie**

Welcome to the free online edition of **The Grandmaster Codex** — a
five-volume chess curriculum designed to carry a player from their very
first move all the way to grandmaster-level thinking.

This is the **complete, unabridged book**. Every chapter, every annotated
game, every exercise — free to read, free to share, free to study.

## How to Use This Book

- **Use the sidebar** to jump to any volume or chapter.
- **Press `s`** (or tap the magnifying glass) to search across the entire
  curriculum.
- **Press `t`** to toggle between light and dark themes.
- **Click the printer icon** to get a clean print-ready copy.

## Five Volumes, One Journey

1. **Foundations** — rules, fundamentals, and your first fifty games.
2. **Club Player** — tactics, calculation, and the first real openings.
3. **Tournament Fighter** — advanced strategy, preparation, and rating climb.
4. **Expert** — professional-level decision making and engine-informed play.
5. **Grandmaster** — elite calculation, championship preparation, and legacy.

## Supporting the Book

If this curriculum helps you, please consider grabbing a copy on
[Amazon Kindle](https://www.amazon.com/) — every purchase helps fund future
free editions and translations.

---

*Stockfish-verified · Neurodivergent-inclusive · Built with love.* 💙♟️
"""
    (SRC / "introduction.md").write_text(intro, encoding="utf-8")

    print(f"built SRC at {SRC}")


if __name__ == "__main__":
    main()
