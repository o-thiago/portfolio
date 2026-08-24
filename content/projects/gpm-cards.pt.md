+++
title = "GPMecatrônica Cards & Plataforma Web"
description = "Aplicação web full-stack e sistema gerador de cartões para os membros do Grupo de Pesquisa em Mecatrônica do IFRO."
date = 2025-04-10
weight = 3

[extra]
category = "Web / Full-Stack"
github = "https://github.com/o-thiago/gpm-cards"
stack = ["Next.js 14", "TypeScript", "PostgreSQL", "Tailwind CSS", "Nix / process-compose", "Docker"]
+++

## Visão Geral

Desenvolvido para o **GPMecatrônica** (Grupo de Pesquisa em Mecatrônica do IFRO), este sistema atua como vitrine institucional, credencial dinâmica e gerador de cards de membros para eventos científicos e perfis acadêmicos.

---

## Decisões Técnicas de Engenharia

- **Full-Stack com Next.js:** Construído com App Router e **TypeScript**, utilizando server actions e tipagem estrita de banco de dados.
- **Ambiente Declarativo com Nix:** Configuração de orquestração multi-serviços via `flake.nix` e `process-compose-flake`, provisionando instâncias locais do PostgreSQL e padronizando o ambiente de desenvolvimento de toda a equipe de pesquisa com um único comando.
- **Builds Herméticos de Contêiner:** Geração de imagens Docker em camadas utilizando Nix (`dockerTools.buildLayeredImage`), garantindo imagens de produção compactas e reprodutíveis.
