+++
title = "Plataforma de Cartões GPMecatrônica"
description = "Aplicação web desenvolvida em Next.js e PostgreSQL para cadastro de membros e geração de credenciais no GPMecatrônica (IFRO)."
date = 2025-04-10
weight = 2

[extra]
category = "Web / Full-Stack"
github = "https://github.com/o-thiago/gpm-cards"
stack = ["Next.js", "TypeScript", "PostgreSQL", "Tailwind CSS", "Nix", "Docker"]
+++

## O que é o projeto?

Aplicação web desenvolvida para o grupo de pesquisa **GPMecatrônica** do IFRO (Campus Porto Velho Calama). O sistema serve para cadastrar membros do laboratório, exibir seus perfis e gerar cartões digitais de identificação para eventos e apresentações científicas.

---

## Detalhes Técnicos

- **Frontend e Backend:** Construído com **Next.js** (App Router) e **TypeScript**, integrando schemas tipados e Tailwind CSS para a interface.
- **Serviços Locais com Nix:** Utilização do `process-compose` via Nix Flakes para inicializar instâncias locais do banco de dados PostgreSQL durante o desenvolvimento, permitindo que outros membros executem o projeto com um único comando, sem instalação manual do banco.
- **Docker:** Criação de imagens Docker multi-stage para manter os deploys leves e consistentes.

```nix
/* Configuração do serviço local do PostgreSQL via process-compose */
services.postgres."gpm-cards-db" = {
  enable = true;
  initialDatabases = [ { name = "gpm-cards"; } ];
  initialScript.after = ''
    CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
  '';
};
```

---

## Repositório

- **GitHub:** {{ github_link(repo="gpm-cards") }}
- **Autor:** {{ author_link() }}
