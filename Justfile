# Justfile for my own Personal Portfolio

# Default recipe: print help
default:
    @just --list

# Watch Tailwind CSS and run Zola live-reload dev server concurrently
dev: sync-cv
    @mkdir -p static
    @sh -c "tailwindcss -i styles/input.css -o static/style.css --watch & zola serve --port 1111 --interface 127.0.0.1"

# Synchronize CV data from central cv-data: compile Typst PDFs and generate content
sync-cv:
    @if [ ! -f data/cv.yaml ] && [ -f ../cv-data/cv.yaml ]; then \
        mkdir -p data && cp -f ../cv-data/cv.yaml data/cv.yaml; \
    fi
    @if command -v python3 >/dev/null 2>&1; then \
        python3 scripts/sync_cv.py; \
    else \
        nix shell --impure --expr 'with import <nixpkgs> {}; [ (python3.withPackages (ps: [ ps.tomli-w ps.pyyaml ])) tailwindcss_4 ]' --command python3 scripts/sync_cv.py; \
    fi

# Build production static site (includes fresh CV sync)
build: sync-cv
    @mkdir -p static
    tailwindcss -i styles/input.css -o static/style.css --minify
    zola build

# Serve the production build locally
serve: build
    zola serve --port 1111 --interface 127.0.0.1

# Clean build artifacts
clean:
    rm -rf public/ static/style.css

# Check nix flake validity
check:
    nix flake check
