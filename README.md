# Portfolio

Personal portfolio and curriculum vitae of Thiago Macedo Mendes.

Static site built with [Zola](https://www.getzola.org/) and [Tailwind CSS](https://tailwindcss.com/), packaged with Nix.

## Features

- Static HTML/CSS without client-side JavaScript.
- Multilingual (English and Portuguese).
- Automatic CV synchronization with LaTeX source files (`curriculum-vitae` submodule) and compiled PDF downloads.
- `llms.txt` and OpenGraph/JSON-LD metadata support.

## Development

Prerequisites: [Nix](https://nixos.org/) (with flakes enabled) or `zola`, `tailwindcss`, and `just`.

```bash
# Enter development shell
nix develop

# Start dev server and Tailwind watcher
just dev
```

The site will be available at `http://127.0.0.1:1111`.

## Build

```bash
# Synchronize CV, compile PDFs, and build static output to public/
just build

# Or build via Nix
nix build
```

## Curriculum Vitae Sync

The resume data and downloadable PDFs are synchronized directly from the LaTeX source in `submodules/curriculum-vitae`:

```bash
just sync-cv
```

This compiles `resume.tex` and `curriculo.tex` to `static/*.pdf` and generates the corresponding markdown pages under `content/resume/` and `content/experience/`.
