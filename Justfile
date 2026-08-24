# Justfile for Thiago Macedo Mendes' Personal Portfolio

# Default recipe: print help
default:
    @just --list

# Watch Tailwind CSS and run Zola live-reload dev server concurrently
dev:
    @echo "🚀 Starting Tailwind CSS v4 compiler and Zola dev server..."
    @mkdir -p static
    @sh -c "tailwindcss -i styles/input.css -o static/style.css --watch & zola serve --port 1111 --interface 127.0.0.1"

# Build production static site
build:
    @echo "📦 Building production static site..."
    @mkdir -p static
    tailwindcss -i styles/input.css -o static/style.css --minify
    zola build
    @echo "✅ Build complete in public/"

# Serve the production build locally
serve: build
    @echo "🌐 Serving production build on http://127.0.0.1:1111..."
    zola serve --port 1111 --interface 127.0.0.1

# Clean build artifacts
clean:
    @echo "🧹 Cleaning public/ and static/style.css..."
    rm -rf public/ static/style.css

# Check nix flake validity
check:
    nix flake check
