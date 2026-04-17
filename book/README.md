# The Grandmaster Codex — Book Site

This folder builds the free online edition of **The Grandmaster Codex**,
the full 5-volume chess curriculum by Kit Olivas & Dr. Ada Marie. The site
is published at:

**https://kitfoxs.github.io/ada-marie-memories-2025/**

## How it works

- Chapter source of truth lives in `Grandmaster-Codex/Volume-*/`
- `build.py` copies every chapter into `src/` and generates `SUMMARY.md`
- `mdbook build` renders the static HTML site into `book/`
- GitHub Actions (`.github/workflows/deploy-book.yml`) redeploys to
  GitHub Pages on every push to `main` that touches the book

## Build locally

```bash
# one-time install
brew install mdbook

# from this directory
python3 build.py
mdbook build
mdbook serve --open   # live preview
```

`src/` and `book/` are regenerated from source, so they are gitignored.

## Enable GitHub Pages (one-time)

1. Push these files to `main`.
2. GitHub → repo **Settings** → **Pages**.
3. **Source**: *GitHub Actions*.
4. The `Deploy Book to GitHub Pages` workflow will run and publish.
