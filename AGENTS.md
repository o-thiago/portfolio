# Agent Operating Guidelines & Inviolable Rules

This document outlines strict, mandatory rules for any AI agent or automated contributor operating within this repository.

---

## 1. Visual & Content Parity ("The page should be the same")
- **Never delete user-facing content**: Do not remove author attributions, names, project links, contact sections, awards boxes, or navigation links under the guise of "simplification", "refactoring", or "auditing".
- **No unprompted destructive edits**: Never alter or eliminate sections from markdown pages (`content/**/*.md`) or templates (`templates/**/*.html`) unless the user explicitly and specifically requests the removal of that exact element.
- **Do not butcher code to meet arbitrary metrics**: Never strip out working features, shortcodes, or components merely to satisfy line-count reductions, dependency-count goals, or minimalism rules (e.g., ponytail mode). The site's rendered output and functional capabilities must remain intact.

---

## 2. Central `cv-data` as the Single Source of Truth
- **Rely on `cv-data` for all personal/profile data**: All personal information—including full name, handle, email address (`thiagomm@proton.me`), telephone, location, LinkedIn, GitHub, summary bio, experience, education, skills, and certifications—must be sourced exclusively from `cv-data` (`submodules/cv-data/cv.yaml` / `data/cv.yaml`).
- **No hardcoded contact or profile strings**: Never hardcode email addresses, social profile links, author names, or handles into markdown content or template HTML. Always use the data provided by `cv-data` directly or through the components in `templates/components.html`.
- **Maintain and respect components**: Preserve the component abstractions in `templates/components.html` (`name()`, `author_link()`, `github_link()`, `email_link()`, `linkedin_link()`). These components ensure content files pull their links and metadata dynamically from `data/cv.yaml`.

---

## 3. Architecture & Nix Data Pipeline
- **Understand the pipeline**: Personal data is sourced directly from the `cv-data` Nix flake (`inputs.cv-data`). Core CV data changes should be made in `cv-data` (`../cv-data/cv.yaml`) and adhere to its schema.
- **Nix-provided data**: `data/cv.yaml` is dynamically provided on the Nix side (via `buildPhase` during Nix builds, and via `shellHook` / `apps.default` during development). Do not commit `data/` or rely on a `submodules/cv-data` git submodule.
- **Build integrity**: When modifying templates, scripts, or styles, ensure the site builds cleanly via Zola and Nix without regressions.
