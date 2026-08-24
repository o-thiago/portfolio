{
  description = "Thiago Macedo Mendes - Personal Portfolio (No-JS, Static, Tailwind CSS, Zola)";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
  };

  outputs =
    inputs@{ flake-parts, systems, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = import systems;
      perSystem =
        { pkgs, ... }:
        let
          buildInputs = with pkgs; [
            zola
            tailwindcss_4
            (python3.withPackages (ps: [
              ps.tomli-w
              ps.pylatexenc
            ]))
            texliveFull
          ];

          portfolioSite = pkgs.stdenv.mkDerivation {
            pname = "thiago-portfolio";
            version = "1.0.0";
            src = ./.;

            nativeBuildInputs = buildInputs;

            buildPhase = ''
              mkdir -p static
              if [ -f scripts/sync_cv.py ]; then
                python3 scripts/sync_cv.py || true
              fi
              tailwindcss -i styles/input.css -o static/style.css --minify
              zola build -o $out
            '';

            dontInstall = true;
          };
        in
        {
          packages.default = portfolioSite;

          apps.default = {
            type = "app";
            program = toString (
              pkgs.writeShellScript "serve" ''
                echo "Building CSS and launching Zola development server..."
                mkdir -p static
                ${pkgs.tailwindcss_4}/bin/tailwindcss -i styles/input.css -o static/style.css
                ${pkgs.zola}/bin/zola serve --port 1111 --interface 127.0.0.1
              ''
            );
          };

          devShells.default = pkgs.mkShell {
            packages = buildInputs ++ (with pkgs; [ just ]);

            shellHook = ''
              echo ""
              echo "   Thiago Macedo Mendes - Personal Portfolio Dev Shell"
              echo "   Stack: Pure No-JS / Zola (Rust SSG) / Tailwind CSS v4 / Nix"
              echo ""
              echo "Available commands (via just):"
              echo "  just dev       - Watch CSS and run Zola live-reload dev server"
              echo "  just build     - Build production minified site to public/"
              echo "  just serve     - Preview production build"
              echo "  nix build      - Build reproducible static package via Nix"
              echo "  nix run        - Run local preview server directly with Nix"
              echo ""
            '';
          };
        };
    };
}
