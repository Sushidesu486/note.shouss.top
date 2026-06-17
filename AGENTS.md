# Repository Guidelines

## Project Structure & Module Organization

This repository is a MkDocs Material notes site. Source content lives in `docs/`: `docs/index.md` is the home page, and course notes are Markdown files such as `docs/query_execution.md`. Site configuration, navigation, theme settings, Markdown extensions, and plugins are defined in `mkdocs.yml`. Python documentation dependencies are listed in `requirements.txt`. `CNAME` configures the custom domain. The `site/` directory is generated build output; do not edit it directly.

## Build, Test, and Development Commands

Set up a local environment before editing:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Use `mkdocs serve` to preview the site locally at `http://127.0.0.1:8000`. Use `mkdocs build` to generate the static site and catch broken navigation, Markdown, or plugin errors. GitHub Actions also runs `mkdocs build` before deploying Pages from `main`.

## Coding Style & Naming Conventions

Write notes in Markdown, following the existing Chinese prose with English technical terms where useful. Use clear hierarchical headings and keep related examples near the concepts they explain. Name new note files with lowercase `snake_case`, for example `buffer_pool.md`. When using MkDocs admonitions, indent contents by four spaces:

```markdown
!!! tip "Title"
    Body text here.
```

Mermaid diagrams are supported through fenced `mermaid` blocks. Keep examples and code fences readable, and avoid editing generated files under `site/`.

## Testing Guidelines

There is no separate unit test suite for this documentation site. Treat `mkdocs build` as the required validation step before submitting changes. For content that affects rendering, navigation, admonitions, tables, or diagrams, also run `mkdocs serve` and inspect the changed pages in a browser. When adding a new page, update `mkdocs.yml` navigation if it should appear in the site menu.

## Commit & Pull Request Guidelines

Recent commits use concise prefixes such as `docs(...)`, `fix:`, `update:`, and `init:`. Prefer short, imperative messages that identify the affected area, for example `docs(dbs:query execution): add join examples` or `fix: correct admonition indentation`.

Pull requests should include a brief summary, the pages or config files changed, any source links used for course material, and the result of `mkdocs build`. Add screenshots when changing navigation, theme settings, diagrams, or other visible layout behavior.
