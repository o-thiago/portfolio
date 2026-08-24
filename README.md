# Thiago Macedo Mendes — Personal Portfolio

> **High-Performance, Zero-JavaScript, SEO & AI-Agent Optimized Personal Portfolio.**
> Built with **Zola** (Rust SSG), **Tailwind CSS v4**, and **Nix Flakes**.

---

## ⚡ Design & Engineering Principles

- **Pure No-JS (0kB JavaScript):** The entire site renders 100% static HTML and CSS. No client-side JavaScript hydration, runtime bundles, or tracking scripts. Instantaneous First Contentful Paint (<50ms).
- **AI-Agent & Crawler Friendly:**
  - Implements the [`/llms.txt`](https://o-thiago.github.io/llms.txt) and [`/llms-full.txt`](https://o-thiago.github.io/llms-full.txt) standard for direct Markdown ingestion by AI assistants (Claude, GPT, Gemini, Perplexity).
  - Complete **Schema.org JSON-LD** structured data (`Person`, `WebSite`, `EducationalOrganization`).
  - OpenGraph, Twitter Cards, Canonical URLs, and dynamic `sitemap.xml`.
- **Reproducible Nix Infrastructure:** Fully specified in `flake.nix` using `flake-parts`. Compiles both Tailwind CSS and Zola inside an isolated Nix sandbox without system dependencies.
- **Printable Resume:** Dedicated `/resume/` page styled to print cleanly to standard A4/Letter PDF matching professional LaTeX CV standards.

---

## 🛠️ Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Generator** | [Zola](https://www.getzola.org/) (Rust) | Lightning fast (<10ms builds), single binary, Tera templates, zero runtime dependencies. |
| **Styling** | [Tailwind CSS v4](https://tailwindcss.com/) | Standalone CLI, zero-config `@import "tailwindcss"`, modern design tokens, minified output. |
| **Environment** | [Nix Flakes](https://nixos.org/) + `flake-parts` | 100% reproducible developer environment and hermetic build derivations. |
| **Standards** | HTML5, CSS3, JSON-LD, `llms.txt` | Universal access across web browsers, text browsers (`lynx`/`w3m`), and AI scrapers. |

---

## 🚀 Getting Started

### Using Nix Flakes (Recommended)

Enter the reproducible development environment:

```bash
# Enter dev shell with Zola, Tailwind CSS v4, and Just
nix develop

# Start live-reload development server and CSS compiler
just dev
```

The site will be running at [http://127.0.0.1:1111](http://127.0.0.1:1111).

### Building Production Site

```bash
# Via Justfile (outputs to public/)
just build

# Or hermetically via Nix build (outputs to ./result)
nix build
```

### Running Directly with Nix

```bash
# Run local preview server directly
nix run
```

---

## 📂 Project Structure

```
.
├── flake.nix              # Flake specification (flake-parts, zola, tailwindcss_4)
├── config.toml            # Zola site configuration & profile metadata
├── Justfile               # Developer task runner (dev, build, serve, check)
├── styles/
│   └── input.css          # Tailwind CSS v4 source stylesheet
├── templates/
│   ├── base.html          # Base layout with JSON-LD, SEO, and navigation
│   ├── index.html         # Homepage (Hero, 3 Facets, Featured Projects, Timeline)
│   ├── about.html         # Complete biography & engineering philosophy
│   ├── projects.html      # Project directory catalog
│   ├── project.html       # Single project deep-dive layout
│   ├── experience.html    # Work & research timeline
│   ├── awards.html        # Academic olympiad medals & certifications
│   ├── resume.html        # Clean, printable LaTeX-style CV layout
│   ├── 404.html           # Custom 404 error page
│   └── robots.txt         # Permissive crawler rules (AI & search engines)
├── content/
│   ├── _index.md          # Homepage content
│   ├── about/_index.md    # About story
│   ├── projects/          # Markdown deep dives for each project
│   ├── experience/        # Experience section
│   ├── awards/            # Awards section
│   └── resume/            # Resume section
└── static/
    ├── llms.txt           # Structured markdown for LLM agents
    ├── llms-full.txt      # Full-context markdown for LLM agents
    ├── humans.txt         # Humans.txt web standard
    ├── favicon.svg        # SVG favicon
    └── avatar.svg         # SVG brand avatar
```

---

## 👤 Author

**Thiago Macedo Mendes**
- **Email:** [thiagomm@pm.me](mailto:thiagomm@pm.me)
- **LinkedIn:** [linkedin.com/in/thiagomacedomendes](https://www.linkedin.com/in/thiagomacedomendes/)
- **GitHub:** [@o-thiago](https://github.com/o-thiago)
- **Location:** Porto Velho, Rondônia, Brazil
