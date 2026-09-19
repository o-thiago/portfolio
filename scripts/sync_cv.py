#!/usr/bin/env python3
"""Sync CV data from central YAML and generate site pages, metadata, and PDFs."""

import os
import re
import shutil
import subprocess
from pathlib import Path

import tomli_w  # type: ignore[import-not-found]
import yaml  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ("en", "en", "resume", ".md"),
    ("pt", "pt-br", "curriculo", ".pt.md"),
]

AWARD_ICONS = [
    (("gold", "ouro"), "🥇", "border-l-amber-400", "text-amber-400"),
    (("silver", "prata"), "🥈", "border-l-slate-400", "text-slate-300"),
    (("bronze",), "🥉", "border-l-amber-600", "text-amber-500"),
    (("honorable mention", "menção honrosa"), "🏅", "border-l-sky-400", "text-sky-400"),
    (("merit honor", "honra ao mérito"), "🎖️", "border-l-teal-400", "text-teal-400"),
    (("4th place", "4º lugar", "4° lugar"), "🏆", "border-l-purple-400", "text-purple-400"),
    (("speaker", "palestrante"), "🎙️", "border-l-indigo-400", "text-indigo-400"),
]


def sync_pdf(cv_dir: Path, sub: str, name: str, dst: Path) -> None:
    """Copy precompiled Typst PDF or compile if typst CLI exists."""
    for cand in (cv_dir / f"{name}.pdf", cv_dir / "resumes" / sub / f"{name}.pdf"):
        if cand.exists():
            shutil.copy2(cand, dst)
            return
    typ = cv_dir / "resumes" / sub / f"{name}.typ"
    if typ.exists() and shutil.which("typst"):
        subprocess.run(
            ["typst", "compile", "--root", str(cv_dir), str(typ), str(dst)],
            capture_output=True,
            check=False,
        )


def parse_award(item: str) -> dict:
    """Parse medal type, year, and UI badge styles from award entry."""
    parts = item.split(" - ", 1)
    badge, title = (parts[0], parts[1]) if len(parts) > 1 else ("Distinction", item)
    m = re.search(r"\b(20\d\d)\b", item)
    year = m.group(1) if m else ""
    lower = item.lower()
    for triggers, icon, border, color in AWARD_ICONS:
        if any(t in lower for t in triggers):
            return {
                "badge": badge or "Honors",
                "title": title,
                "icon": icon,
                "border": border,
                "color": color,
                "year": year,
                "is_major": True,
                "raw": item,
            }
    return {
        "badge": badge or "Distinction",
        "title": title,
        "icon": "💻",
        "border": "border-l-emerald-400",
        "color": "text-emerald-400",
        "year": year,
        "is_major": False,
        "raw": item,
    }


def make_humans_txt(d: dict) -> str:
    """Generate humans.txt file content."""
    cfg = (ROOT / "config.toml").read_text(encoding="utf-8")
    m = re.search(r'^tagline\s*=\s*"([^"]*)"', cfg, re.MULTILINE)
    tagline = f"\nRole: {m.group(1)}" if m else ""
    return f"""/* TEAM */
Author: {d["name"]}{tagline}
Site: {d["site_url"]}
Email: {d["email"]}
GitHub: @{d["handle"]}
LinkedIn: @{d["linkedin"].rstrip("/").split("/")[-1]}
Location: {d["location"]}

/* THANKS */
Thanks to the open-source community, the NixOS project, and Zola developers.

/* SITE */
Standards: HTML5, CSS3, JSON-LD Schema.org, llms.txt
Static Site Generator: Zola (Rust SSG)
CSS Framework: Tailwind CSS v4
JavaScript: None (0kB client-side JS)
Infrastructure: Nix / Nix Flakes
Hosted: GitHub Pages
"""


def make_llms_txt(d: dict) -> str:
    """Generate lightweight llms.txt context document."""
    edu = "\n".join(
        f"- **{e['institution']}**: {e['degree']} ({e['date']})" for e in d["education"]
    )
    exp = "\n".join(
        f"- **{e['company']}** ({e['date']}): {e['role']}. {' '.join(e.get('bullets', []))}"
        for e in d["experience"]
    )
    certs = "\n".join(f"- {c}" for c in d["certifications"])
    skills = "\n".join(f"- {s['label']}: {s['value']}" for s in d.get("skills", []))
    return f"""# {d["name"]}

> {d["summary"]}

## Core Information
- Full Name: {d["name"]}
- GitHub: {d["github"]}
- LinkedIn: {d["linkedin"]}
- Email: {d["email"]}
- Location: {d["location"]}
- Website: {d["site_url"]}

## Education
{edu}

## Experience & Research
{exp}

## Honors & Olympiad Medals
{certs}

## Technical Skills
{skills}

## Full Context
For the complete unabridged markdown portfolio context, see: {d["site_url"]}/llms-full.txt
"""


def make_llms_full_txt(d: dict) -> str:
    """Generate unabridged llms-full.txt context document."""
    edu = "\n\n".join(
        f"### {e['institution']}\n- **Degree:** {e['degree']}\n- **Period:** {e['date']}\n- **Location:** {e['location']}"
        for e in d["education"]
    )
    exp = "\n\n".join(
        f"### {e['company']}\n- **Role:** {e['role']}\n- **Period:** {e['date']}\n- **Location:** {e['location']}\n"
        + (
            "- **Responsibilities:**\n"
            + "\n".join(f"  - {b}" for b in e.get("bullets", []))
            if e.get("bullets")
            else ""
        )
        for e in d["experience"]
    )
    certs = "\n".join(f"- {c}" for c in d["certifications"])
    skills = "\n".join(f"- **{s['label']}:** {s['value']}" for s in d.get("skills", []))
    return f"""# {d["name"]} - Full Portfolio & Profile Context

- **Author:** {d["name"]}
- **GitHub:** {d["github"]}
- **LinkedIn:** {d["linkedin"]}
- **Email:** {d["email"]}
- **Phone:** {d["phone"]}
- **Location:** {d["location"]}
- **Website:** {d["site_url"]}

---

## 1. Summary

{d["summary"]}

---

## 2. Education

{edu}

---

## 3. Work & Research Experience

{exp}

---

## 4. Honors & Distinctions

{certs}

---

## 5. Technical Skills

{skills}
"""


def main() -> None:
    """Synchronize CV documents, PDF files, and static machine endpoints."""
    default_data_dir = (
        ROOT.parent / "cv-data"
        if (ROOT.parent / "cv-data" / "cv.yaml").exists()
        else ROOT / "data"
    )
    cv_data_dir = Path(os.getenv("CV_DATA_DIR", default_data_dir))
    default_cv_dir = (
        ROOT.parent / "curriculum-vitae"
        if (ROOT.parent / "curriculum-vitae").exists()
        else ROOT / "submodules/curriculum-vitae"
    )
    cv_template_dir = Path(os.getenv("CV_DIR", default_cv_dir))

    yaml_file = cv_data_dir / "cv.yaml"
    if not yaml_file.exists():
        raise FileNotFoundError(f"cv.yaml not found at {yaml_file}")

    raw = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))

    (ROOT / "static").mkdir(exist_ok=True)

    data: dict[str, dict] = {}
    for lang, sub, name, ext in TARGETS:
        sync_pdf(cv_template_dir, sub, name, ROOT / "static" / f"{name}.pdf")
        d = dict(raw[lang])
        d["site_url"] = f"https://{d['handle']}.github.io"
        d["awards"] = [parse_award(c) for c in d.get("certifications", [])]
        data[lang] = d

        for folder, page in [
            (
                "resume",
                {
                    "title": d["name"],
                    "description": d["summary"],
                    "template": "resume.html",
                    "extra": d,
                },
            ),
            (
                "experience",
                {
                    "title": d["experience_title"],
                    "description": d["summary"],
                    "template": "experience.html",
                    "extra": {"experience": d["experience"]},
                },
            ),
            (
                "awards",
                {
                    "title": d["certifications_title"],
                    "description": d["summary"],
                    "template": "awards.html",
                    "extra": {
                        "awards": d["awards"],
                        "certifications": d["certifications"],
                    },
                },
            ),
        ]:
            out = ROOT / f"content/{folder}/_index{ext}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(f"+++\n{tomli_w.dumps(page)}+++\n", encoding="utf-8")

    canonical = data["en"]
    (ROOT / "static/humans.txt").write_text(
        make_humans_txt(canonical), encoding="utf-8"
    )
    (ROOT / "static/llms.txt").write_text(make_llms_txt(canonical), encoding="utf-8")
    (ROOT / "static/llms-full.txt").write_text(
        make_llms_full_txt(canonical), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
