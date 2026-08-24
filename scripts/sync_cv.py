#!/usr/bin/env python3
"""Programmatically fetch curriculum-vitae LaTeX sources and generate site content."""

import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_CANDIDATES = [
    ROOT.parent / "curriculum-vitae",
    Path.home() / "Programming" / "curriculum-vitae",
]
REMOTE_REPO = os.environ.get(
    "CV_REPO_URL", "https://github.com/o-thiago/resume-template.git"
)


def get_cv_root() -> Path:
    for p in LOCAL_CANDIDATES:
        if (p / "resumes").exists():
            return p
    cache = ROOT / ".cache" / "curriculum-vitae"
    if (cache / "resumes").exists():
        subprocess.run(
            ["git", "pull"],
            cwd=cache,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return cache
    token = (os.environ.get("CV_PAT") or os.environ.get("cv_pat") or "").strip()
    repo_url = REMOTE_REPO
    if token and "github.com" in repo_url:
        clean_url = re.sub(r"^https?://(?:[^@]+@)?github\.com/", "", repo_url)
        repo_url = f"https://x-access-token:{token}@github.com/{clean_url}"
    res = subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(cache)],
        check=False,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0 or not (cache / "resumes").exists():
        err_detail = res.stderr.strip() or res.stdout.strip()
        msg = (
            f"Failed to clone CV repository from {REMOTE_REPO}.\n"
            f"Git error output: {err_detail}\n"
            "If the repository is private, ensure the secret 'CV_PAT' is set with read access."
        )
        raise RuntimeError(msg)
    return cache


def clean(s: str) -> str:
    s = re.sub(r"(?<!\\)%.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\\(?:begin|end)\{[^}]+\}", "", s)
    s = re.sub(r"\\(?:textbf|textit|emph|c)\{([^}]*)\}", r"\1", s)
    s = re.sub(r"\\href\{[^}]*\}\{([^}]*)\}", r"\1", s)
    replacements = [
        (r"\_", "_"),
        (r"\&", "&"),
        (r"\%", "%"),
        (r"\$", "$"),
        ("``", '"'),
        ("''", '"'),
        ('"', '\\"'),
    ]
    for a, b in replacements:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def parse_cv(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    secs = {
        m.group(1): m.group(2)
        for m in re.finditer(
            r"\\section\{([^}]+)\}(.*?)(?=\\section\{|\\end\{document\})",
            text,
            re.DOTALL,
        )
    }

    def entries(sec: str) -> list[dict]:
        res = []
        for chunk in secs.get(sec, "").split(r"\cventry")[1:]:
            p = [clean(x) for x in re.findall(r"\{([^}]*)\}", chunk[:300])]
            if len(p) >= 4:
                items = [
                    clean(it)
                    for it in re.findall(r"\\item\s+([^\n\\]+(?:\\.[^\n\\]*)*)", chunk)
                ]
                res.append(
                    {
                        "company": p[0],
                        "location": p[1],
                        "role": p[2],
                        "date": p[3],
                        "bullets": items,
                    }
                )
        return res

    summary_k = next((k for k in secs if k in ("Summary", "Resumo")), "Summary")
    exp_k = next((k for k in secs if k in ("Experience", "Experiência")), "Experience")
    edu_k = next((k for k in secs if k in ("Education", "Educação")), "Education")
    skills_k = next((k for k in secs if k in ("Skills", "Habilidades")), "Skills")
    cert_k = next(
        (k for k in secs if k in ("Certifications", "Certificações")),
        "Certifications",
    )

    skills_raw = secs.get(skills_k, "")
    tech = re.search(r"\\textbf\{[^}]+\}\s*(.*?)(?=\\item|\Z)", skills_raw, re.DOTALL)
    lang_chunk = skills_raw.split(r"\item")[-1] if r"\item" in skills_raw else ""
    lang = re.search(r"\\textbf\{[^}]+\}\s*(.*?)(?=\\item|\Z)", lang_chunk, re.DOTALL)

    return {
        "summary_title": summary_k,
        "summary": clean(secs.get(summary_k, "")),
        "experience_title": exp_k,
        "experiences": entries(exp_k),
        "education_title": edu_k,
        "educations": entries(edu_k),
        "skills_title": skills_k,
        "skills_tech": clean(tech.group(1)) if tech else "",
        "skills_lang": clean(lang.group(1)) if lang else "",
        "certifications_title": cert_k,
        "certifications": [
            clean(it)
            for it in re.findall(
                r"\\item\s+([^\n\\]+(?:\\.[^\n\\]*)*)", secs.get(cert_k, "")
            )
        ],
    }


def build_pdf(src_dir: Path, tex_file: str, dst_pdf: Path) -> None:
    cmd = ["pdflatex", "-interaction=nonstopmode", tex_file]
    pdf_path = src_dir / tex_file.replace(".tex", ".pdf")
    try:
        run_res = subprocess.run(
            cmd,
            cwd=src_dir,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if run_res.returncode != 0:
            subprocess.run(
                ["nix", "shell", "nixpkgs#texliveFull", "--command", *cmd],
                cwd=src_dir,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except FileNotFoundError:
        subprocess.run(
            ["nix", "shell", "nixpkgs#texliveFull", "--command", *cmd],
            cwd=src_dir,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    if not pdf_path.exists():
        msg = f"Failed to generate PDF for {tex_file} in {src_dir}."
        raise RuntimeError(msg)

    shutil.copy2(pdf_path, dst_pdf)


def format_bullets(bullets: list[str]) -> str:
    return ", ".join(f'"{x}"' for x in bullets)


def make_pages(data: dict, is_pt: bool) -> tuple[str, str]:
    loc = "Porto Velho, Rondônia, Brasil" if is_pt else "Porto Velho, Rondônia, Brazil"
    exp = "\n".join(
        f'[[extra.experience]]\ncompany = "{e["company"]}"\n'
        f'location = "{e["location"]}"\nrole = "{e["role"]}"\n'
        f'date = "{e["date"]}"\nbullets = [{format_bullets(e["bullets"])}]\n'
        for e in data["experiences"]
    )
    edu = "\n".join(
        f'[[extra.education]]\ninstitution = "{e["company"]}"\n'
        f'location = "{e["location"]}"\ndegree = "{e["role"]}"\n'
        f'date = "{e["date"]}"\n'
        for e in data["educations"]
    )
    certs = ",\n  ".join(f'"{c}"' for c in data["certifications"])

    res_title = "Currículo / CV" if is_pt else "Curriculum Vitae / Resume"
    res_desc = (
        "Currículo profissional e acadêmico de Thiago Macedo Mendes."
        if is_pt
        else "Professional and academic CV of Thiago Macedo Mendes."
    )
    tech_label = "Tecnologias" if is_pt else "Technologies"
    lang_label = "Idiomas" if is_pt else "Languages"

    resume = f"""+++
title = "{res_title}"
description = "{res_desc}"
template = "resume.html"

[extra]
name = "Thiago Macedo Mendes"
location = "{loc}"
phone = "+55 (69) 99314-6868"
email = "thiagomm@pm.me"
linkedin = "https://www.linkedin.com/in/thiagomacedomendes"
github = "https://github.com/o-thiago"
summary_title = "{data["summary_title"]}"
summary = "{data["summary"]}"
experience_title = "{data["experience_title"]}"
education_title = "{data["education_title"]}"
skills_title = "{data["skills_title"]}"
skills_tech_label = "{tech_label}"
skills_tech = "{data["skills_tech"]}"
skills_lang_label = "{lang_label}"
skills_lang = "{data["skills_lang"]}"
certifications_title = "{data["certifications_title"]}"
certifications = [
  {certs}
]

{exp}
{edu}+++
"""
    exp_title = (
        "Experiência Profissional & Pesquisa" if is_pt else "Work & Research Experience"
    )
    exp_desc = (
        "Histórico profissional e acadêmico."
        if is_pt
        else "Professional roles and research grants."
    )
    experience = f"""+++
title = "{exp_title}"
description = "{exp_desc}"
template = "experience.html"

[extra]
experience_title = "{data["experience_title"]}"

{exp}+++
"""
    return resume, experience


def main() -> None:
    cv_root = get_cv_root()
    if not cv_root:
        return

    (ROOT / "static").mkdir(exist_ok=True)
    build_pdf(cv_root / "resumes" / "en", "resume.tex", ROOT / "static" / "resume.pdf")
    build_pdf(
        cv_root / "resumes" / "pt-br",
        "curriculo.tex",
        ROOT / "static" / "curriculo.pdf",
    )

    targets = [
        ("en", "resumes/en/resume.tex", ".md"),
        ("pt", "resumes/pt-br/curriculo.tex", ".pt.md"),
    ]
    for lang, tex, ext in targets:
        data = parse_cv(cv_root / tex)
        res_md, exp_md = make_pages(data, lang == "pt")

        res_dir = ROOT / "content/resume"
        res_dir.mkdir(parents=True, exist_ok=True)
        (res_dir / f"_index{ext}").write_text(res_md, encoding="utf-8")

        exp_dir = ROOT / "content/experience"
        exp_dir.mkdir(parents=True, exist_ok=True)
        (exp_dir / f"_index{ext}").write_text(exp_md, encoding="utf-8")


if __name__ == "__main__":
    main()
