#!/usr/bin/env python3
"""Fetch central CV data (YAML/TOML) and generate site content and PDFs."""

import contextlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import tomli_w  # type: ignore[import-not-found]

try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

try:
    import yaml  # type: ignore[import-not-found]
except ImportError:
    yaml = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ("en", "en", "resume", ".md"),
    ("pt", "pt-br", "curriculo", ".pt.md"),
]


def find_match(
    pattern: str, text: str, group: int = 1, flags: int = re.DOTALL | re.MULTILINE
) -> str:
    """Extract a regex group match or empty string if not found."""
    m = re.search(pattern, text, flags=flags)
    return m.group(group) if m else ""


def get_cv_data_root() -> Path | None:
    """Fetch and synchronize cv-data repository."""
    if env_data := os.getenv("CV_DATA_DIR"):
        p = Path(env_data)
        if (p / "cv.yaml").exists() or (p / "cv.toml").exists():
            return p

    cache = ROOT / ".cache/cv-data"
    local_sources = [
        ROOT.parent / "cv-data",
        ROOT / "../cv-data",
        Path.home() / "Programming/cv-data",
        ROOT / "submodules/cv-data",
    ]
    repo_sources = [
        os.getenv("CV_DATA_REPO_URL"),
        str((ROOT.parent / "cv-data").resolve()),
        str((Path.home() / "Programming/cv-data").resolve()),
        "git@github.com-thiago:o-thiago/cv-data.git",
        "https://github.com/o-thiago/cv-data.git",
    ]

    # If already cloned, pull/fetch latest commits from local ../ and remotes
    if cache.exists() and (cache / ".git").exists():
        for local in local_sources:
            if (local / ".git").exists():
                with contextlib.suppress(OSError, subprocess.SubprocessError):
                    subprocess.run(
                        [
                            "git",
                            "-C",
                            str(cache),
                            "pull",
                            "--ff-only",
                            str(local.resolve()),
                            "HEAD",
                        ],
                        capture_output=True,
                        check=False,
                    )
                break
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                ["git", "-C", str(cache), "pull", "--ff-only"],
                capture_output=True,
                check=False,
            )
        if (cache / "cv.yaml").exists() or (cache / "cv.toml").exists():
            return cache

    # Clone from repo sources (prioritizing ../ sibling repo, then remotes)
    cache.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(cache, ignore_errors=True)

    for src in repo_sources:
        if not src:
            continue
        try:
            res = subprocess.run(
                ["git", "clone", "--depth=1", src, str(cache)],
                capture_output=True,
                check=False,
            )
            if res.returncode == 0 and (
                (cache / "cv.yaml").exists() or (cache / "cv.toml").exists()
            ):
                return cache
        except Exception:
            continue

    # Fallback to local working copy if git clone could not be performed
    for p in local_sources:
        if (p / "cv.yaml").exists() or (p / "cv.toml").exists():
            return p

    return None


def get_cv_template_root() -> Path | None:
    """Fetch and synchronize curriculum-vitae repository for Typst templates."""
    if cv_env := os.getenv("CV_DIR"):
        p = Path(cv_env)
        if (p / "resumes").exists():
            return p

    cache = ROOT / ".cache/curriculum-vitae"
    local_sources = [
        ROOT.parent / "curriculum-vitae",
        ROOT / "../curriculum-vitae",
        Path.home() / "Programming/curriculum-vitae",
        ROOT / "submodules/curriculum-vitae",
    ]
    repo_sources = [
        os.getenv("CV_REPO_URL"),
        str((ROOT.parent / "curriculum-vitae").resolve()),
        str((Path.home() / "Programming/curriculum-vitae").resolve()),
        "git@github.com-thiago:o-thiago/resume-template.git",
        "https://github.com/o-thiago/resume-template.git",
    ]

    # If already cloned, pull/fetch latest commits from local ../ and remotes
    if cache.exists() and (cache / ".git").exists():
        for local in local_sources:
            if (local / ".git").exists():
                with contextlib.suppress(OSError, subprocess.SubprocessError):
                    subprocess.run(
                        [
                            "git",
                            "-C",
                            str(cache),
                            "pull",
                            "--ff-only",
                            str(local.resolve()),
                            "HEAD",
                        ],
                        capture_output=True,
                        check=False,
                    )
                break
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                ["git", "-C", str(cache), "pull", "--ff-only"],
                capture_output=True,
                check=False,
            )
        if (cache / "resumes").exists():
            return cache

    # Clone from repo sources (prioritizing ../ sibling repo, then remotes)
    cache.parent.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(cache, ignore_errors=True)

    for src in repo_sources:
        if not src:
            continue
        try:
            res = subprocess.run(
                ["git", "clone", "--depth=1", src, str(cache)],
                capture_output=True,
                check=False,
            )
            if res.returncode == 0 and (cache / "resumes").exists():
                return cache
        except Exception:
            continue

    # Fallback to local directory
    for p in local_sources:
        if (p / "resumes").exists():
            return p

    return None


def load_cv_data(cv_root: Path) -> dict:
    """Load structured CV data from YAML (cv.yaml)."""
    yaml_file = cv_root / "cv.yaml"
    if yaml_file.exists():
        if yaml is not None:
            return yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        raise RuntimeError("PyYAML required to read cv.yaml")

    toml_file = cv_root / "cv.toml"
    if toml_file.exists():
        return tomllib.loads(toml_file.read_text(encoding="utf-8"))

    raise FileNotFoundError(f"cv.yaml not found in {cv_root}")


def build_pdf(cv_root: Path | None, sub: str, name: str, dst: Path) -> None:
    """Compile Typst document or copy compiled PDF to dst."""
    if not cv_root:
        return

    typ_file = cv_root / "resumes" / sub / f"{name}.typ"
    if typ_file.exists() and shutil.which("typst"):
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                [
                    "typst",
                    "compile",
                    "--root",
                    str(cv_root),
                    str(typ_file),
                    str(dst),
                ],
                capture_output=True,
                check=False,
            )
        return

    # Fallbacks if already precompiled
    for candidate in (
        cv_root / "resumes" / sub / f"{name}.pdf",
        cv_root / f"{name}.pdf",
    ):
        if candidate.exists():
            shutil.copy2(candidate, dst)
            return


def parse_award(item: str) -> dict:
    """Parse medal type, year, and UI badge styles from award entry."""
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
    year = find_match(r"\b(20\d\d)\b", item)
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


def make_humans_txt(d: dict) -> str:
    """Generate humans.txt file content."""
    cfg = ROOT / "config.toml"
    tagline = ""
    if cfg.exists():
        tagline = find_match(
            r'^tagline\s*=\s*"([^"]*)"', cfg.read_text(encoding="utf-8")
        )

    return f"""/* TEAM */
Author: {d["name"]}
Role: {tagline}
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
    skills_text = "\n".join(
        f"- {s['label']}: {s['value']}" for s in d.get("skills", [])
    )
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
{skills_text}

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
    skills_text = "\n".join(
        f"- **{s['label']}:** {s['value']}" for s in d.get("skills", [])
    )
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

{skills_text}
"""


def main() -> None:
    """Synchronize CV documents, PDF files, and static machine endpoints."""
    cv_data_dir = get_cv_data_root()
    if not cv_data_dir:
        print("Error: Could not locate central cv-data repository.")
        return

    cv_template_dir = get_cv_template_root()

    (ROOT / "static").mkdir(exist_ok=True)
    (ROOT / "data").mkdir(exist_ok=True)

    raw = load_cv_data(cv_data_dir)

    data: dict[str, dict] = {}
    for lang, sub, name, ext in TARGETS:
        build_pdf(cv_template_dir, sub, name, ROOT / "static" / f"{name}.pdf")
        d = dict(raw[lang])
        d["site_url"] = f"https://{d['handle']}.github.io"
        d["awards"] = [parse_award(c) for c in d.get("certifications", [])]
        data[lang] = d

        (ROOT / f"data/cv.{lang}.toml").write_text(tomli_w.dumps(d), encoding="utf-8")

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

    # Canonical profile and machine-readable endpoints
    canonical = data["en"]
    profile_fields = [
        "name",
        "handle",
        "email",
        "phone",
        "location",
        "github",
        "linkedin",
        "site_url",
    ]
    (ROOT / "data/profile.toml").write_text(
        tomli_w.dumps({k: canonical[k] for k in profile_fields}),
        encoding="utf-8",
    )
    (ROOT / "static/humans.txt").write_text(
        make_humans_txt(canonical), encoding="utf-8"
    )
    (ROOT / "static/llms.txt").write_text(make_llms_txt(canonical), encoding="utf-8")
    (ROOT / "static/llms-full.txt").write_text(
        make_llms_full_txt(canonical), encoding="utf-8"
    )

    # Ensure Tailwind CSS stylesheet is compiled if tailwindcss CLI is available
    if tw := shutil.which("tailwindcss"):
        with contextlib.suppress(OSError, subprocess.SubprocessError):
            subprocess.run(
                [tw, "-i", "styles/input.css", "-o", "static/style.css", "--minify"],
                cwd=ROOT,
                capture_output=True,
                check=False,
            )


if __name__ == "__main__":
    main()
