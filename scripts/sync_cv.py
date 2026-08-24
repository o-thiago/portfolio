#!/usr/bin/env python3
"""Fetch curriculum-vitae LaTeX sources and generate site content."""

import contextlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import tomli_w
from pylatexenc.latex2text import LatexNodes2Text

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ("en", "en", "resume", ".md"),
    ("pt", "pt-br", "curriculo", ".pt.md"),
]


def clean(s: str) -> str:
    return " ".join(LatexNodes2Text().latex_to_text(s).split())


def get_cv_root() -> Path | None:
    if cv_env := os.getenv("CV_DIR"):
        p = Path(cv_env)
        if (p / "resumes").exists():
            return p
    for p in (
        ROOT.parent / "curriculum-vitae",
        Path.home() / "Programming/curriculum-vitae",
    ):
        if (p / "resumes").exists():
            return p
    cache = ROOT / ".cache/curriculum-vitae"
    if (cache / "resumes").exists():
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                ["git", "-C", str(cache), "pull"],
                capture_output=True,
                check=False,
            )
        return cache
    shutil.rmtree(cache, ignore_errors=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        subprocess.run(
            [
                "git",
                "clone",
                "--depth=1",
                os.getenv(
                    "CV_REPO_URL",
                    "https://github.com/o-thiago/resume-template.git",
                ),
                str(cache),
            ],
            capture_output=True,
            check=False,
        )
    return cache if (cache / "resumes").exists() else None


def build_pdf(src: Path, name: str, dst: Path) -> None:
    if not (src / f"{name}.tex").exists():
        return
    with tempfile.TemporaryDirectory() as tmp:
        for f in src.iterdir():
            if f.is_file():
                shutil.copy2(f, tmp)
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", f"{name}.tex"],
                cwd=tmp,
                capture_output=True,
                check=False,
            )
        if (out := Path(tmp) / f"{name}.pdf").exists():
            shutil.copy2(out, dst)


def parse_award(item: str) -> dict:
    icon_map = [
        (("gold", "ouro"), "🥇", "border-l-amber-400", "text-amber-400"),
        (("silver", "prata"), "🥈", "border-l-slate-400", "text-slate-300"),
        (("bronze",), "🥉", "border-l-amber-600", "text-amber-500"),
        (("honorable mention", "menção honrosa"), "🏅", "border-l-sky-400", "text-sky-400"),
        (("merit honor", "honra ao mérito"), "🎖️", "border-l-teal-400", "text-teal-400"),
        (("4th place", "4º lugar", "4° lugar"), "🏆", "border-l-purple-400", "text-purple-400"),
        (("speaker", "palestrante"), "🎙️", "border-l-indigo-400", "text-indigo-400"),
    ]
    parts = item.split(" - ", 1)
    badge, title = (parts[0], parts[1]) if len(parts) > 1 else ("", item)
    year_m = re.search(r"\b(20\d\d)\b", item)
    year = year_m.group(1) if year_m else ""
    for triggers, icon, border, color in icon_map:
        if any(t in item.lower() for t in triggers):
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


def parse_cv(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    header_m = re.search(r"\\begin\{center\}(.*?)\\end\{center\}", text, re.DOTALL)
    header = header_m.group(1) if header_m else ""
    github = re.search(r"\\href\{(https://[^}]*github\.com/[^}]+)\}", header).group(1)

    secs = dict(
        re.findall(
            r"\\section\{([^}]+)\}(.*?)(?=\\section\{|\\end\{document\})",
            text,
            re.DOTALL,
        )
    )

    def get_sec(*keys: str) -> str:
        return next((k for k in keys if k in secs), keys[0])

    def items(s: str) -> list[str]:
        return [clean(x) for x in re.findall(r"\\item\s+([^\n\\]+(?:\\.[^\n\\]*)*)", s)]

    def entries(sec: str, keys: tuple[str, ...], *, with_bullets: bool = False) -> list[dict]:
        return [
            dict(zip(keys, p, strict=False), **({"bullets": items(c)} if with_bullets else {}))
            for c in secs.get(sec, "").split(r"\cventry")[1:]
            if len(p := [clean(x) for x in re.findall(r"\{([^}]*)\}", c[:300])][:4]) == 4
        ]

    exp_k = get_sec("Experience", "Experiência")
    edu_k = get_sec("Education", "Educação")
    sum_k = get_sec("Summary", "Resumo")
    cert_k = get_sec("Certifications", "Certificações")
    skills_k = get_sec("Skills", "Habilidades")

    raw_certs = items(secs.get(cert_k, ""))
    skill_items = re.findall(
        r"\\item\s+\\textbf\{([^}]+)\}\s*([^\n\\]+(?:\\.[^\n\\]*)*)",
        secs.get(skills_k, ""),
    )
    skills = [{"label": clean(lbl).rstrip(":"), "value": clean(val)} for lbl, val in skill_items]

    return {
        "name": clean(re.search(r"\\textbf\{([^}]+)\}", header).group(1)),
        "handle": github.rstrip("/").split("/")[-1],
        "location": clean(header.split(r"\\ [0.1cm]")[1].split(r"{\textbullet}")[0]),
        "phone": clean(re.search(r"(\+55[^\n\\{]+)", header).group(1)),
        "email": re.search(r"\\href\{mailto:([^}]+)\}", header).group(1),
        "linkedin": re.search(r"\\href\{(https://[^}]*linkedin\.com/[^}]+)\}", header).group(1),
        "github": github,
        "summary_title": sum_k,
        "summary": clean(secs.get(sum_k, "")),
        "experience_title": exp_k,
        "education_title": edu_k,
        "skills_title": skills_k,
        "skills": skills,
        "certifications_title": cert_k,
        "certifications": raw_certs,
        "awards": [parse_award(c) for c in raw_certs],
        "experience": entries(exp_k, ("company", "location", "role", "date"), with_bullets=True),
        "education": entries(edu_k, ("institution", "location", "degree", "date")),
    }


def make_humans_txt(d: dict) -> str:
    cfg = ROOT / "config.toml"
    tagline = ""
    if cfg.exists():
        m = re.search(r'^tagline\s*=\s*"([^"]*)"', cfg.read_text(encoding="utf-8"), re.MULTILINE)
        tagline = m.group(1) if m else ""

    return f"""/* TEAM */
Author: {d['name']}
Role: {tagline}
Site: {d['site_url']}
Email: {d['email']}
GitHub: @{d['handle']}
LinkedIn: @{d['linkedin'].rstrip('/').split('/')[-1]}
Location: {d['location']}

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
    edu = "\n".join(f"- **{e['institution']}**: {e['degree']} ({e['date']})" for e in d["education"])
    exp = "\n".join(
        f"- **{e['company']}** ({e['date']}): {e['role']}. {' '.join(e.get('bullets', []))}"
        for e in d["experience"]
    )
    certs = "\n".join(f"- {c}" for c in d["certifications"])
    skills_text = "\n".join(f"- {s['label']}: {s['value']}" for s in d.get("skills", []))
    return f"""# {d['name']}

> {d['summary']}

## Core Information
- Full Name: {d['name']}
- GitHub: {d['github']}
- LinkedIn: {d['linkedin']}
- Email: {d['email']}
- Location: {d['location']}
- Website: {d['site_url']}

## Education
{edu}

## Experience & Research
{exp}

## Honors & Olympiad Medals
{certs}

## Technical Skills
{skills_text}

## Full Context
For the complete unabridged markdown portfolio context, see: {d['site_url']}/llms-full.txt
"""


def make_llms_full_txt(d: dict) -> str:
    edu = "\n\n".join(
        f"### {e['institution']}\n- **Degree:** {e['degree']}\n- **Period:** {e['date']}\n- **Location:** {e['location']}"
        for e in d["education"]
    )
    exp = "\n\n".join(
        f"### {e['company']}\n- **Role:** {e['role']}\n- **Period:** {e['date']}\n- **Location:** {e['location']}\n"
        + ("- **Responsibilities:**\n" + "\n".join(f"  - {b}" for b in e.get("bullets", [])) if e.get("bullets") else "")
        for e in d["experience"]
    )
    certs = "\n".join(f"- {c}" for c in d["certifications"])
    skills_text = "\n".join(f"- **{s['label']}:** {s['value']}" for s in d.get("skills", []))
    return f"""# {d['name']} - Full Portfolio & Profile Context

- **Author:** {d['name']}
- **GitHub:** {d['github']}
- **LinkedIn:** {d['linkedin']}
- **Email:** {d['email']}
- **Phone:** {d['phone']}
- **Location:** {d['location']}
- **Website:** {d['site_url']}

---

## 1. Summary

{d['summary']}

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

{skills_text}
"""


def main() -> None:
    if not (cv := get_cv_root()):
        return

    (ROOT / "static").mkdir(exist_ok=True)
    (ROOT / "data").mkdir(exist_ok=True)

    data: dict[str, dict] = {}
    for lang, sub, name, ext in TARGETS:
        build_pdf(cv / "resumes" / sub, name, ROOT / "static" / f"{name}.pdf")
        d = parse_cv(cv / "resumes" / sub / f"{name}.tex")
        d["site_url"] = f"https://{d['handle']}.github.io"
        data[lang] = d

        (ROOT / f"data/cv.{lang}.toml").write_text(tomli_w.dumps(d), encoding="utf-8")

        for folder, page in [
            ("resume", {"title": d["name"], "description": d["summary"], "template": "resume.html", "extra": d}),
            ("experience", {"title": d["experience_title"], "description": d["summary"], "template": "experience.html", "extra": {"experience": d["experience"]}}),
            ("awards", {"title": d["certifications_title"], "description": d["summary"], "template": "awards.html", "extra": {"awards": d["awards"], "certifications": d["certifications"]}}),
        ]:
            out = ROOT / f"content/{folder}/_index{ext}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(f"+++\n{tomli_w.dumps(page)}+++\n", encoding="utf-8")

    # Canonical profile and machine-readable endpoints
    canonical = data["en"]
    profile_fields = ["name", "handle", "email", "phone", "location", "github", "linkedin", "site_url"]
    (ROOT / "data/profile.toml").write_text(
        tomli_w.dumps({k: canonical[k] for k in profile_fields}),
        encoding="utf-8",
    )
    (ROOT / "static/humans.txt").write_text(make_humans_txt(canonical), encoding="utf-8")
    (ROOT / "static/llms.txt").write_text(make_llms_txt(canonical), encoding="utf-8")
    (ROOT / "static/llms-full.txt").write_text(make_llms_full_txt(canonical), encoding="utf-8")


if __name__ == "__main__":
    main()
