#!/usr/bin/env python3
"""Fetch curriculum-vitae LaTeX sources and generate site content."""

import os
import re
import shutil
import subprocess
from pathlib import Path

import tomli_w

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    (
        False,
        "en",
        "resume.tex",
        "resume.pdf",
        ".md",
        "Curriculum Vitae / Resume",
        "Professional and academic CV of Thiago Macedo Mendes.",
        "Work & Research Experience",
        "Professional roles and research grants.",
    ),
    (
        True,
        "pt-br",
        "curriculo.tex",
        "curriculo.pdf",
        ".pt.md",
        "Currículo / CV",
        "Currículo profissional e acadêmico de Thiago Macedo Mendes.",
        "Experiência Profissional & Pesquisa",
        "Histórico profissional e acadêmico.",
    ),
]


def get_cv_root() -> Path | None:
    candidates = (
        ROOT.parent / "curriculum-vitae",
        Path.home() / "Programming/curriculum-vitae",
    )
    if p := next((p for p in candidates if (p / "resumes").exists()), None):
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
    repo = os.getenv(
        "CV_REPO_URL", "https://github.com/o-thiago/resume-template.git"
    )
    res = subprocess.run(
        ["git", "clone", "--depth=1", repo, str(cache)],
        capture_output=True,
        text=True,
        check=False,
    )
    if (cache / "resumes").exists():
        return cache
    err = res.stderr.strip() or "clone failed"
    print(f"Notice: CV sources unavailable ({err}). Proceeding with existing content.")
    return None


def build_pdf(src: Path, tex: str, dst: Path) -> None:
    cmd = ["pdflatex", "-interaction=nonstopmode", tex]
    try:
        res = subprocess.run(cmd, cwd=src, capture_output=True, check=False)
    except FileNotFoundError:
        res = None
    if not res or res.returncode != 0:
        subprocess.run(
            ["nix", "shell", "nixpkgs#texliveFull", "--command", *cmd],
            cwd=src,
            capture_output=True,
            check=False,
        )
    if not (pdf := (src / tex).with_suffix(".pdf")).exists():
        raise RuntimeError(f"Failed to generate PDF for {tex} in {src}")
    shutil.copy2(pdf, dst)


def clean(s: str) -> str:
    s = re.sub(r"(?<!\\)%.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", s)
    s = re.sub(r"\\(?:textbf|textit|emph|c|href\{[^}]*\})\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\([_&%$])", r"\1", re.sub(r"``|''", '"', s))
    return " ".join(s.split())


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

    sum_k, exp_k, edu_k, sk_k, cert_k = (
        get_sec(en, pt)
        for en, pt in [
            ("Summary", "Resumo"),
            ("Experience", "Experiência"),
            ("Education", "Educação"),
            ("Skills", "Habilidades"),
            ("Certifications", "Certificações"),
        ]
    )
    skills = [
        clean(m)
        for m in re.findall(
            r"\\textbf\{[^}]+\}\s*(.*?)(?=\\item|\Z)",
            secs.get(sk_k, ""),
            re.DOTALL,
        )
    ]

    return {
        "name": "Thiago Macedo Mendes",
        "location": f"Porto Velho, Rondônia, {'Brasil' if is_pt else 'Brazil'}",
        "phone": "+55 (69) 99314-6868",
        "email": "thiagomm@pm.me",
        "linkedin": "https://www.linkedin.com/in/thiagomacedomendes",
        "github": "https://github.com/o-thiago",
        "summary_title": sum_k,
        "summary": clean(secs.get(sum_k, "")),
        "experience_title": exp_k,
        "education_title": edu_k,
        "skills_title": sk_k,
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
    for is_pt, sub, tex, pdf_name, ext, rt, rd, et, ed in TARGETS:
        build_pdf(cv / "resumes" / sub, tex, ROOT / "static" / pdf_name)
        extra = parse_cv(cv / "resumes" / sub / tex, is_pt)
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
