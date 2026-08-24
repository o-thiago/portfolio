#!/usr/bin/env python3
"""Fetch curriculum-vitae LaTeX sources and generate site content."""

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
        subprocess.run(
            ["git", "-C", str(cache), "pull"],
            capture_output=True,
            check=False,
        )
        return cache
    shutil.rmtree(cache, ignore_errors=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
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
        "certifications": items(secs.get(cert_k, "")),
        "experience": entries(
            exp_k, ("company", "location", "role", "date"), with_bullets=True
        ),
        "education": entries(
            edu_k, ("institution", "location", "degree", "date")
        ),
    }


def main() -> None:
    if not (cv := get_cv_root()):
        return
    (ROOT / "static").mkdir(exist_ok=True)
    for is_pt, sub, name, ext, rt, rd, et, ed in TARGETS:
        build_pdf(cv / "resumes" / sub, name, ROOT / "static" / f"{name}.pdf")
        extra = parse_cv(cv / "resumes" / sub / f"{name}.tex", is_pt)
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
        ]:
            out = ROOT / "content" / folder / f"_index{ext}"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(f"+++\n{tomli_w.dumps(page)}+++\n", encoding="utf-8")


if __name__ == "__main__":
    main()
