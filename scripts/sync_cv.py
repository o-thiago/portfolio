#!/usr/bin/env python3
"""Programmatically fetch curriculum-vitae LaTeX sources and generate site content."""

import os
import re
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_CANDIDATES = [
    ROOT.parent / "curriculum-vitae",
    Path.home() / "Programming" / "curriculum-vitae",
]
REMOTE_REPO = os.environ.get("CV_REPO_URL", "https://github.com/o-thiago/resume-template.git")

def get_cv_root() -> Path:
    for p in LOCAL_CANDIDATES:
        if (p / "resumes").exists():
            return p
    cache = ROOT / ".cache" / "curriculum-vitae"
    if (cache / "resumes").exists():
        subprocess.run(["git", "pull"], cwd=cache, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return cache
    token = os.environ.get("CV_PAT") or os.environ.get("GH_PAT")
    repo_url = REMOTE_REPO
    if token and "github.com" in repo_url and "@" not in repo_url:
        repo_url = repo_url.replace("https://", f"https://x-access-token:{token}@")
    res = subprocess.run(["git", "clone", "--depth", "1", repo_url, str(cache)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0 or not (cache / "resumes").exists():
        raise RuntimeError(
            f"Failed to clone private CV repository from {REMOTE_REPO}.\n"
            "If running in CI, add a GitHub secret named 'CV_PAT' with read access to the repo."
        )
    return cache

def clean(s: str) -> str:
    s = re.sub(r'(?<!\\)%.*$', '', s, flags=re.M)
    s = re.sub(r'\\(?:begin|end)\{[^}]+\}', '', s)
    s = re.sub(r'\\(?:textbf|textit|emph|c)\{([^}]*)\}', r'\1', s)
    s = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', s)
    for a, b in [(r'\_', '_'), (r'\&', '&'), (r'\%', '%'), (r'\$', '$'), ("``", '"'), ("''", '"'), ('"', '\\"')]:
        s = s.replace(a, b)
    return re.sub(r'\s+', ' ', s).strip()

def parse_cv(path: Path) -> dict:
    text = path.read_text(encoding='utf-8')
    secs = {m.group(1): m.group(2) for m in re.finditer(r'\\section\{([^}]+)\}(.*?)(?=\\section\{|\\end\{document\})', text, re.S)}

    def entries(sec):
        res = []
        for chunk in secs.get(sec, '').split(r'\cventry')[1:]:
            p = [clean(x) for x in re.findall(r'\{([^}]*)\}', chunk[:300])]
            if len(p) >= 4:
                items = [clean(it) for it in re.findall(r'\\item\s+([^\n\\]+(?:\\.[^\n\\]*)*)', chunk)]
                res.append({'company': p[0], 'location': p[1], 'role': p[2], 'date': p[3], 'bullets': items})
        return res

    summary_k = next((k for k in secs if k in ('Summary', 'Resumo')), 'Summary')
    exp_k = next((k for k in secs if k in ('Experience', 'Experiência')), 'Experience')
    edu_k = next((k for k in secs if k in ('Education', 'Educação')), 'Education')
    skills_k = next((k for k in secs if k in ('Skills', 'Habilidades')), 'Skills')
    cert_k = next((k for k in secs if k in ('Certifications', 'Certificações')), 'Certifications')

    skills_raw = secs.get(skills_k, '')
    tech = re.search(r'\\textbf\{[^}]+\}\s*(.*?)(?=\\item|\Z)', skills_raw, re.S)
    lang = re.search(r'\\textbf\{[^}]+\}\s*(.*?)(?=\\item|\Z)', skills_raw.split(r'\item')[-1], re.S) if r'\item' in skills_raw else None

    return {
        'summary_title': summary_k, 'summary': clean(secs.get(summary_k, '')),
        'experience_title': exp_k, 'experiences': entries(exp_k),
        'education_title': edu_k, 'educations': entries(edu_k),
        'skills_title': skills_k,
        'skills_tech': clean(tech.group(1)) if tech else '',
        'skills_lang': clean(lang.group(1)) if lang else '',
        'certifications_title': cert_k,
        'certifications': [clean(it) for it in re.findall(r'\\item\s+([^\n\\]+(?:\\.[^\n\\]*)*)', secs.get(cert_k, ''))]
    }

def build_pdf(src_dir: Path, tex_file: str, dst_pdf: Path):
    cmd = ["pdflatex", "-interaction=nonstopmode", tex_file]
    if subprocess.run(cmd, cwd=src_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
        subprocess.run(["nix", "shell", "nixpkgs#texliveFull", "--command", *cmd], cwd=src_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    shutil.copy2(src_dir / tex_file.replace(".tex", ".pdf"), dst_pdf)

def make_pages(data: dict, is_pt: bool):
    loc = "Porto Velho, Rondônia, Brasil" if is_pt else "Porto Velho, Rondônia, Brazil"
    b_fmt = lambda b: ", ".join(f'"{x}"' for x in b)
    exp = "\n".join(f'[[extra.experience]]\ncompany = "{e["company"]}"\nlocation = "{e["location"]}"\nrole = "{e["role"]}"\ndate = "{e["date"]}"\nbullets = [{b_fmt(e["bullets"])}]\n' for e in data["experiences"])
    edu = "\n".join(f'[[extra.education]]\ninstitution = "{e["company"]}"\nlocation = "{e["location"]}"\ndegree = "{e["role"]}"\ndate = "{e["date"]}"\n' for e in data["educations"])
    certs = ",\n  ".join(f'"{c}"' for c in data["certifications"])

    resume = f"""+++
title = "{"Currículo / CV" if is_pt else "Curriculum Vitae / Resume"}"
description = "{"Currículo profissional e acadêmico de Thiago Macedo Mendes." if is_pt else "Professional and academic CV of Thiago Macedo Mendes."}"
template = "resume.html"

[extra]
name = "Thiago Macedo Mendes"
location = "{loc}"
phone = "+55 (69) 99314-6868"
email = "thiagomm@pm.me"
linkedin = "https://www.linkedin.com/in/thiagomacedomendes"
github = "https://github.com/o-thiago"
summary_title = "{data['summary_title']}"
summary = "{data['summary']}"
experience_title = "{data['experience_title']}"
education_title = "{data['education_title']}"
skills_title = "{data['skills_title']}"
skills_tech_label = "{"Tecnologias" if is_pt else "Technologies"}"
skills_tech = "{data['skills_tech']}"
skills_lang_label = "{"Idiomas" if is_pt else "Languages"}"
skills_lang = "{data['skills_lang']}"
certifications_title = "{data['certifications_title']}"
certifications = [
  {certs}
]

{exp}
{edu}+++
"""
    experience = f"""+++
title = "{"Experiência Profissional & Pesquisa" if is_pt else "Work & Research Experience"}"
description = "{"Histórico profissional e acadêmico." if is_pt else "Professional roles and research grants."}"
template = "experience.html"

[extra]
experience_title = "{data['experience_title']}"

{exp}+++
"""
    return resume, experience

def main():
    cv_root = get_cv_root()
    if not cv_root:
        return

    (ROOT / "static").mkdir(exist_ok=True)
    build_pdf(cv_root / "resumes" / "en", "resume.tex", ROOT / "static" / "resume.pdf")
    build_pdf(cv_root / "resumes" / "pt-br", "curriculo.tex", ROOT / "static" / "curriculo.pdf")

    for lang, tex, ext in [("en", "resumes/en/resume.tex", ".md"), ("pt", "resumes/pt-br/curriculo.tex", ".pt.md")]:
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
