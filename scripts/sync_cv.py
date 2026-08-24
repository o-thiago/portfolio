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
    (False, "en", "resume", ".md"),
    (True, "pt-br", "curriculo", ".pt.md"),
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
    header_m = re.search(
        r"\\begin\{center\}(.*?)\\end\{center\}", text, re.DOTALL
    )
    header = header_m.group(1) if header_m else ""

    name = clean(re.search(r"\\textbf\{([^}]+)\}", header).group(1))
    email = re.search(r"\\href\{mailto:([^}]+)\}", header).group(1)
    linkedin = re.search(r"\\href\{(https://[^}]*linkedin\.com/[^}]+)\}", header).group(1)
    github = re.search(r"\\href\{(https://[^}]*github\.com/[^}]+)\}", header).group(1)
    handle = github.rstrip("/").split("/")[-1]
    phone = clean(re.search(r"(\+55[^\n\\{]+)", header).group(1))
    loc_part = header.split(r"\\ [0.1cm]")[1].split(r"{\textbullet}")[0]
    location = clean(loc_part)

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
        "name": name,
        "handle": handle,
        "location": location,
        "phone": phone,
        "email": email,
        "linkedin": linkedin,
        "github": github,
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


def sync_config_globals(d: dict) -> None:
    cfg = ROOT / "config.toml"
    if not cfg.exists():
        return
    text = cfg.read_text(encoding="utf-8")

    # Pick up whatever identity values are currently on record in [extra] so
    # every literal mention of them elsewhere in the file (the header
    # comment, page titles, ASCII banners, the GitHub Pages base_url host,
    # etc.) can be swapped for the freshly parsed CV values too, instead of
    # only updating the [extra] block itself.
    extra_m = re.search(r"\[extra\](.*?)(?=\n\[|\Z)", text, re.DOTALL)
    old = dict(
        re.findall(
            r'^(name|handle|email|phone|location|github|linkedin)\s*=\s*"([^"]*)"',
            extra_m.group(1),
            re.MULTILINE,
        )
    ) if extra_m else {}

    for key in ("name", "handle", "email", "phone", "location", "github", "linkedin"):
        old_val, new_val = old.get(key), d[key]
        if old_val and old_val != new_val:
            text = text.replace(old_val, new_val)
            text = text.replace(old_val.upper(), new_val.upper())

    for key, val in [
        ("name", d["name"]),
        ("handle", d["handle"]),
        ("email", d["email"]),
        ("phone", d["phone"]),
        ("location", d["location"]),
        ("github", d["github"]),
        ("linkedin", d["linkedin"]),
        ("title", d["name"]),
    ]:
        text = re.sub(
            rf'^{key}\s*=.*$', f'{key} = "{val}"', text, flags=re.MULTILINE
        )
    cfg.write_text(text, encoding="utf-8")


def make_humans_txt(d: dict) -> str:
    github_handle = d["github"].rstrip("/").split("/")[-1]
    linkedin_handle = d["linkedin"].rstrip("/").split("/")[-1]
    site_url = f"https://{github_handle}.github.io"

    cfg = ROOT / "config.toml"
    tagline = ""
    if cfg.exists():
        m = re.search(r'^tagline\s*=\s*"([^"]*)"', cfg.read_text(encoding="utf-8"), re.MULTILINE)
        tagline = m.group(1) if m else ""

    return f"""/* TEAM */
Author: {d['name']}
Role: {tagline}
Site: {site_url}
Email: {d['email']}
GitHub: @{github_handle}
LinkedIn: @{linkedin_handle}
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
    edu = "\n".join(
        f"- **{e['institution']}**: {e['degree']} ({e['date']})"
        for e in d["education"]
    )
    exp = "\n".join(
        f"- **{e['company']}** ({e['date']}): {e['role']}. {' '.join(e.get('bullets', []))}"
        for e in d["experience"]
    )
    certs = "\n".join(f"- {c}" for c in d["certifications"])
    github_handle = d["github"].rstrip("/").split("/")[-1]
    site_url = f"https://{github_handle}.github.io"
    return f"""# {d['name']}

> {d['summary']}

## Core Information
- Full Name: {d['name']}
- GitHub: {d['github']}
- LinkedIn: {d['linkedin']}
- Email: {d['email']}
- Location: {d['location']}
- Website: {site_url}

## Education
{edu}

## Experience & Research
{exp}

## Honors & Olympiad Medals
{certs}

## Technical Skills
- Technologies: {d['skills_tech']}
- Languages: {d['skills_lang']}

## Full Context
For the complete unabridged markdown portfolio context, see: {site_url}/llms-full.txt
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
    github_handle = d["github"].rstrip("/").split("/")[-1]
    site_url = f"https://{github_handle}.github.io"
    return f"""# {d['name']} - Full Portfolio & Profile Context

- **Author:** {d['name']}
- **GitHub:** {d['github']}
- **LinkedIn:** {d['linkedin']}
- **Email:** {d['email']}
- **Phone:** {d['phone']}
- **Location:** {d['location']}
- **Website:** {site_url}

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
    for is_pt, sub, name, ext in TARGETS:
        build_pdf(cv / "resumes" / sub, name, ROOT / "static" / f"{name}.pdf")
        extra = parse_cv(cv / "resumes" / sub / f"{name}.tex", is_pt)
        if not is_pt:
            en_data = extra
            sync_config_globals(extra)

        for folder, page in [
            (
                "resume",
                {
                    "title": extra["name"],
                    "description": extra["summary"],
                    "template": "resume.html",
                    "extra": extra,
                },
            ),
            (
                "experience",
                {
                    "title": extra["experience_title"],
                    "description": extra["summary"],
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
                    "title": extra["certifications_title"],
                    "description": extra["summary"],
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
            "title": extra["name"],
            "description": extra["summary"],
            "template": "about.html",
            "extra": extra,
        }
        abt_file.parent.mkdir(parents=True, exist_ok=True)
        abt_file.write_text(
            f"+++\n{tomli_w.dumps(abt_front)}+++\n{body}", encoding="utf-8"
        )

    if en_data:
        (ROOT / "static/humans.txt").write_text(
            make_humans_txt(en_data), encoding="utf-8"
        )
        (ROOT / "static/llms.txt").write_text(
            make_llms_txt(en_data), encoding="utf-8"
        )
        (ROOT / "static/llms-full.txt").write_text(
            make_llms_full_txt(en_data), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
