#!/usr/bin/env python3
"""Fetch curriculum-vitae LaTeX sources and generate site content."""

import contextlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import tomli_w
from pylatexenc.latex2text import LatexNodes2Text

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    (
        False,
        "en",
        "resume",
        ".md",
        "Curriculum Vitae / Resume",
        "Professional and academic CV of Thiago Macedo Mendes.",
        "Work & Research Experience",
        "Professional roles and research grants.",
        "Awards, Olympiads & Distinctions",
        "Honors, national olympiad medals, scientific speaking engagements, and technical certifications.",
        "About Thiago Macedo Mendes",
        "Computer Science student at UNIR and software developer.",
    ),
    (
        True,
        "pt-br",
        "curriculo",
        ".pt.md",
        "Currículo / CV",
        "Currículo profissional e acadêmico de Thiago Macedo Mendes.",
        "Experiência Profissional & Pesquisa",
        "Histórico profissional e acadêmico.",
        "Prêmios, Olimpíadas & Distinções",
        "Honras, medalhas em olimpíadas nacionais, palestras científicas e certificações técnicas.",
        "Sobre Thiago Macedo Mendes",
        "Estudante de Ciência da Computação na UNIR e desenvolvedor de software.",
    ),
]


def clean(s: str) -> str:
    return " ".join(LatexNodes2Text().latex_to_text(s).split())


def get_cv_root() -> Path | None:
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
    cmd = ["pdflatex", "-interaction=nonstopmode", f"{name}.tex"]
    if (
        subprocess.run(
            cmd, cwd=src, capture_output=True, check=False
        ).returncode
        != 0
    ):
        subprocess.run(
            ["nix", "shell", "nixpkgs#texliveFull", "--command", *cmd],
            cwd=src,
            capture_output=True,
            check=False,
        )
    shutil.copy2(src / f"{name}.pdf", dst)


def parse_award(item: str) -> dict:
    icon_map = [
        (("gold", "ouro"), "🥇", "border-l-amber-400", "text-amber-400"),
        (("silver", "prata"), "🥈", "border-l-slate-400", "text-slate-300"),
        (("bronze",), "🥉", "border-l-amber-600", "text-amber-500"),
        (
            ("honorable mention", "menção honrosa"),
            "🏅",
            "border-l-sky-400",
            "text-sky-400",
        ),
        (
            ("merit honor", "honra ao mérito"),
            "🎖️",
            "border-l-teal-400",
            "text-teal-400",
        ),
        (
            ("4th place", "4º lugar", "4° lugar"),
            "🏆",
            "border-l-purple-400",
            "text-purple-400",
        ),
        (
            ("speaker", "palestrante"),
            "🎙️",
            "border-l-indigo-400",
            "text-indigo-400",
        ),
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


def parse_cv(path: Path, is_pt: bool) -> dict:
    text = path.read_text(encoding="utf-8")
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
        return [
            clean(x)
            for x in re.findall(r"\\item\s+([^\n\\]+(?:\\.[^\n\\]*)*)", s)
        ]

    def entries(
        sec: str, keys: tuple[str, ...], *, with_bullets: bool = False
    ) -> list[dict]:
        return [
            dict(
                zip(keys, p, strict=False),
                **({"bullets": items(c)} if with_bullets else {}),
            )
            for c in secs.get(sec, "").split(r"\cventry")[1:]
            if len(
                p := [clean(x) for x in re.findall(r"\{([^}]*)\}", c[:300])][:4]
            )
            == 4
        ]

    exp_k, edu_k = (
        get_sec(en, pt)
        for en, pt in (
            ("Experience", "Experiência"),
            ("Education", "Educação"),
        )
    )
    skills = [
        clean(m)
        for m in re.findall(
            r"\\textbf\{[^}]+\}\s*(.*?)(?=\\item|\Z)",
            secs.get(get_sec("Skills", "Habilidades"), ""),
            re.DOTALL,
        )
    ]
    sum_k, cert_k = get_sec("Summary", "Resumo"), get_sec(
        "Certifications", "Certificações"
    )
    raw_certs = items(secs.get(cert_k, ""))

    return {
        "name": "Thiago Macedo Mendes",
        "location": (
            "Porto Velho, Rondônia, " + ("Brasil" if is_pt else "Brazil")
        ),
        "phone": "+55 (69) 99314-6868",
        "email": "thiagomm@pm.me",
        "linkedin": "https://www.linkedin.com/in/thiagomacedomendes",
        "github": "https://github.com/o-thiago",
        "summary_title": sum_k,
        "summary": clean(secs.get(sum_k, "")),
        "experience_title": exp_k,
        "education_title": edu_k,
        "skills_title": get_sec("Skills", "Habilidades"),
        "skills_tech_label": "Tecnologias" if is_pt else "Technologies",
        "skills_tech": skills[0] if skills else "",
        "skills_lang_label": "Idiomas" if is_pt else "Languages",
        "skills_lang": skills[1] if len(skills) > 1 else "",
        "certifications_title": cert_k,
        "certifications": raw_certs,
        "awards": [parse_award(c) for c in raw_certs],
        "experience": entries(
            exp_k, ("company", "location", "role", "date"), with_bullets=True
        ),
        "education": entries(
            edu_k, ("institution", "location", "degree", "date")
        ),
    }


def make_llms_txt(d: dict) -> str:
    edu = "\n".join(
        f"- **{e['institution']}**: {e['degree']} ({e['date']})"
        for e in d["education"]
    )
    exp = "\n".join(
        f"- **{e['company']}** ({e['date']}): {e['role']}. {' '.join(e.get('bullets', []))}"
        for e in d["experience"]
    )
    certs = "\n".join(f"- {c}" for c in d["certifications"])
    return f"""# {d['name']}

> {d['summary']}

## Core Information
- Full Name: {d['name']}
- GitHub: {d['github']}
- LinkedIn: {d['linkedin']}
- Email: {d['email']}
- Location: {d['location']}
- Website: https://o-thiago.github.io

## Education
{edu}

## Experience & Research
{exp}

## Featured Projects
- **toof-os** (https://github.com/o-thiago/ToofOS): Declarative NixOS configuration built for the DACC Station on Raspberry Pi 4.
- **gpm-cards** (https://github.com/o-thiago/gpm-cards): Web platform for member profiles and card generation for GPMecatrônica.
- **sqlx-conditional-queries-layering** (https://github.com/o-thiago/sqlx-conditional-queries-layering): Declarative macro library in Rust for composing SQLx queries.
- **Innovation Radar**: Web platform for tracking innovation initiatives and research IP at IFRO.

## Honors & Olympiad Medals
{certs}

## Technical Skills
- Technologies: {d['skills_tech']}
- Languages: {d['skills_lang']}

## Full Context
For the complete unabridged markdown portfolio context, see: https://o-thiago.github.io/llms-full.txt
"""


def make_llms_full_txt(d: dict) -> str:
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
    return f"""# {d['name']} - Full Portfolio & Profile Context

- **Author:** {d['name']}
- **GitHub:** {d['github']}
- **LinkedIn:** {d['linkedin']}
- **Email:** {d['email']}
- **Phone:** {d['phone']}
- **Location:** {d['location']}
- **Website:** https://o-thiago.github.io

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

- **Technologies:** {d['skills_tech']}
- **Languages:** {d['skills_lang']}
"""


def main() -> None:
    if not (cv := get_cv_root()):
        return
    (ROOT / "static").mkdir(exist_ok=True)
    en_data = None
    for (
        is_pt,
        sub,
        name,
        ext,
        rt,
        rd,
        et,
        ed,
        at,
        ad,
        abt_t,
        abt_d,
    ) in TARGETS:
        build_pdf(cv / "resumes" / sub, name, ROOT / "static" / f"{name}.pdf")
        extra = parse_cv(cv / "resumes" / sub / f"{name}.tex", is_pt)
        if not is_pt:
            en_data = extra

        for folder, page in [
            (
                "resume",
                {
                    "title": rt,
                    "description": rd,
                    "template": "resume.html",
                    "extra": extra,
                },
            ),
            (
                "experience",
                {
                    "title": et,
                    "description": ed,
                    "template": "experience.html",
                    "extra": {
                        "experience_title": extra["experience_title"],
                        "experience": extra["experience"],
                    },
                },
            ),
            (
                "awards",
                {
                    "title": at,
                    "description": ad,
                    "template": "awards.html",
                    "extra": {
                        "awards": extra["awards"],
                        "certifications": extra["certifications"],
                    },
                },
            ),
        ]:
            out = ROOT / "content" / folder / f"_index{ext}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(f"+++\n{tomli_w.dumps(page)}+++\n", encoding="utf-8")

        # Inject dynamic extra frontmatter into about/_index{ext} while preserving content body
        abt_file = ROOT / "content/about" / f"_index{ext}"
        body = ""
        if abt_file.exists():
            parts = abt_file.read_text(encoding="utf-8").split("+++\n")
            if len(parts) >= 3:
                body = "+++\n".join(parts[2:])
        abt_front = {
            "title": abt_t,
            "description": abt_d,
            "template": "about.html",
            "extra": extra,
        }
        abt_file.parent.mkdir(parents=True, exist_ok=True)
        abt_file.write_text(
            f"+++\n{tomli_w.dumps(abt_front)}+++\n{body}", encoding="utf-8"
        )

    if en_data:
        (ROOT / "static/llms.txt").write_text(
            make_llms_txt(en_data), encoding="utf-8"
        )
        (ROOT / "static/llms-full.txt").write_text(
            make_llms_full_txt(en_data), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
